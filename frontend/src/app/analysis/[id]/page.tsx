'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, MapPin, Clock, Radio, Maximize2, X, CheckCircle, XCircle } from 'lucide-react'
import Link from 'next/link'
import { getAnalysis, analyzeSpectrum, generateReport, downloadReport, getAutoThreshold } from '@/lib/api'
import SpectrumChart from '@/components/SpectrumChart'
import AnalysisResults from '@/components/AnalysisResults'
import MapView from '@/components/MapView'
import { formatDate, formatFrequency } from '@/lib/utils'

function FullscreenSignalsTable({ signals }: { signals: any[] }) {
  return (
    <table className="min-w-full divide-y divide-gray-200 text-sm">
      <thead className="bg-gray-50 sticky top-0">
        <tr>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No.</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Frekuensi (MHz)</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg (dBµV/m)</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max (dBµV/m)</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">Stasiun / Client</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Callsign</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">Perangkat</th>
          <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Emisi</th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {signals.map((signal: any, idx: number) => (
          <tr key={idx} className={`hover:bg-gray-50 ${signal.station ? 'bg-green-50/30' : 'bg-amber-50/30'}`}>
            <td className="px-3 py-2 whitespace-nowrap text-gray-900">{idx + 1}</td>
            <td className="px-3 py-2 whitespace-nowrap font-mono text-gray-900">{formatFrequency(signal.frequency)}</td>
            <td className="px-3 py-2 whitespace-nowrap text-gray-900">{signal.avg_field_strength?.toFixed(1)}</td>
            <td className="px-3 py-2 whitespace-nowrap text-gray-900">{signal.max_field_strength?.toFixed(1)}</td>
            <td className="px-3 py-2 whitespace-nowrap">
              {signal.station ? (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3" />
                  Berizin
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                  <XCircle className="h-3 w-3" />
                  Tidak Berizin
                </span>
              )}
            </td>
            <td className="px-3 py-2 text-gray-600">
              {signal.station ? (
                <div>
                  <div className="font-medium">{signal.station.name}</div>
                  {signal.station.clnt_name && signal.station.clnt_name !== signal.station.name && (
                    <div className="text-xs text-gray-400">{signal.station.clnt_name}</div>
                  )}
                </div>
              ) : '-'}
            </td>
            <td className="px-3 py-2 whitespace-nowrap text-gray-600">{signal.station?.callsign || '-'}</td>
            <td className="px-3 py-2 text-gray-600">
              {signal.station ? (
                <div className="text-xs">
                  {signal.station.eq_mfr && <div>{signal.station.eq_mfr}</div>}
                  {signal.station.eq_mdl && <div className="text-gray-400">{signal.station.eq_mdl}</div>}
                </div>
              ) : '-'}
            </td>
            <td className="px-3 py-2 whitespace-nowrap text-purple-600 text-xs">
              {signal.station?.emis_class_1 || '-'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function AnalysisPage() {
  const params = useParams()
  const router = useRouter()
  const id = parseInt(params.id as string)

  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [selectedBand, setSelectedBand] = useState(1)
  const [threshold, setThreshold] = useState(50)
  const [useAutoThreshold, setUseAutoThreshold] = useState(false)
  const [marginDb, setMarginDb] = useState(10)
  const [autoThresholdInfo, setAutoThresholdInfo] = useState<any>(null)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [fullscreenMode, setFullscreenMode] = useState<'map' | 'chart' | 'table' | null>(null)
  const [selectedStation, setSelectedStation] = useState<{ lat: number; lon: number; name: string; frequency: number; callsign?: string } | null>(null)

  useEffect(() => {
    loadAnalysis()
  }, [id])

  const loadAnalysis = async () => {
    try {
      const data = await getAnalysis(id)
      setAnalysis(data)
      if (data.occupancy_results) {
        setResults(data.occupancy_results)
      }
    } catch (error) {
      console.error('Error loading analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAutoThreshold = async () => {
    try {
      const data = await getAutoThreshold(id, selectedBand, marginDb)
      setAutoThresholdInfo(data)
      if (useAutoThreshold) {
        setThreshold(data.auto_threshold)
      }
    } catch (error) {
      console.error('Error loading auto threshold:', error)
    }
  }

  useEffect(() => {
    if (analysis) {
      loadAutoThreshold()
    }
  }, [selectedBand, marginDb])

  useEffect(() => {
    if (useAutoThreshold && autoThresholdInfo) {
      setThreshold(autoThresholdInfo.auto_threshold)
    }
  }, [useAutoThreshold, autoThresholdInfo])

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const data = await analyzeSpectrum(id, selectedBand, threshold, useAutoThreshold, marginDb)
      setResults(data)
    } catch (error) {
      console.error('Error analyzing:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    try {
      const data = await generateReport(id, selectedBand, threshold)
      const url = downloadReport(data.filename)
      window.open(url, '_blank')
    } catch (error) {
      console.error('Error generating report:', error)
    } finally {
      setGeneratingReport(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Memuat data...</p>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Analisis tidak ditemukan</p>
          <Link href="/" className="text-blue-600 hover:underline mt-2 inline-block">
            Kembali ke beranda
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Task {analysis.task_id}
                </h1>
                <p className="text-sm text-gray-600">{analysis.filename}</p>
              </div>
            </div>
            <button
              onClick={handleGenerateReport}
              disabled={!results || generatingReport}
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>{generatingReport ? 'Membuat...' : 'Download PDF'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Informasi Pengukuran
              </h2>
              <div className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <MapPin className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-700">Lokasi</p>
                    <p className="text-gray-600">{analysis.metadata['Station Name']}</p>
                    <p className="text-xs text-gray-500">
                      {analysis.location.lat}, {analysis.location.lon}
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Clock className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-700">Waktu</p>
                    <p className="text-gray-600">
                      {formatDate(analysis.metadata['Start Time'])}
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Radio className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-700">Operator</p>
                    <p className="text-gray-600">{analysis.metadata['Operator ID']}</p>
                  </div>
                </div>
              </div>
            </div>

            {!fullscreenMode && (
            <div className="bg-white rounded-lg shadow-lg p-4 md:p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Peta Lokasi
                </h2>
                <button
                  onClick={() => setFullscreenMode('map')}
                  className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Fullscreen"
                >
                  <Maximize2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-72 md:h-96 lg:h-[400px] rounded-lg overflow-hidden">
                <MapView
                  lat={analysis.location.lat}
                  lon={analysis.location.lon}
                  name={analysis.metadata['Station Name']}
                  stations={results?.occupied_list
                    ?.filter((s: any) => s.station?.latitude && s.station?.longitude)
                    ?.map((s: any) => ({
                      lat: s.station.latitude,
                      lon: s.station.longitude,
                      name: s.station.name,
                      frequency: s.frequency,
                      callsign: s.station.callsign,
                      isLicensed: true
                    })) || []
                  }
                  selectedStation={selectedStation}
                />
              </div>
              {selectedStation && (
                <p className="mt-2 text-xs text-blue-600 font-medium">
                  📍 Menampilkan: {selectedStation.name} ({selectedStation.frequency.toFixed(3)} MHz)
                </p>
              )}
              {!selectedStation && results?.occupied_list?.filter((s: any) => s.station?.latitude)?.length > 0 && (
                <p className="mt-2 text-xs text-gray-500">
                  🟢 Titik hijau = Lokasi stasiun berizin yang terdeteksi
                </p>
              )}
            </div>
            )}

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Pengaturan Analisis
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pilih Band
                  </label>
                  <select
                    value={selectedBand}
                    onChange={(e) => setSelectedBand(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {analysis.bands.map((band: any) => (
                      <option key={band.band_number} value={band.band_number}>
                        Band {band.band_number}: {band.start_freq}-{band.stop_freq} MHz
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Threshold (dBµV/m): {threshold}
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={useAutoThreshold}
                        onChange={(e) => setUseAutoThreshold(e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-600">Auto</span>
                    </label>
                  </div>
                  <input
                    type="range"
                    min="30"
                    max="70"
                    value={threshold}
                    onChange={(e) => setThreshold(parseInt(e.target.value))}
                    disabled={useAutoThreshold}
                    className="w-full disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>30</span>
                    <span>70</span>
                  </div>
                  {autoThresholdInfo && (
                    <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-700">
                      <p><strong>Noise Floor:</strong> {autoThresholdInfo.noise_floor} dBµV/m</p>
                      <p><strong>Threshold Otomatis:</strong> {autoThresholdInfo.auto_threshold} dBµV/m</p>
                    </div>
                  )}
                </div>
                {useAutoThreshold && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Margin di atas Noise Floor (dB): {marginDb}
                    </label>
                    <input
                      type="range"
                      min="5"
                      max="20"
                      step="1"
                      value={marginDb}
                      onChange={(e) => setMarginDb(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>5</span>
                      <span>20</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      Threshold = Noise Floor + {marginDb} dB
                    </p>
                  </div>
                )}
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {analyzing ? 'Menganalisis...' : 'Analisis Spektrum'}
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {results && (
              <>
                <AnalysisResults 
                  results={results} 
                  onFullscreen={() => setFullscreenMode('table')}
                />
                <SpectrumChart 
                  analysisId={id} 
                  bandNumber={selectedBand}
                  matchedChannels={results.occupied_list}
                  threshold={results.threshold_used}
                  onFullscreen={() => setFullscreenMode('chart')}
                  onPointClick={(station) => setSelectedStation(station)}
                />
              </>
            )}
            {!results && (
              <div className="bg-white rounded-lg shadow-lg p-8 md:p-12 text-center">
                <Radio className="h-12 w-12 md:h-16 md:w-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-sm md:text-base">
                  Pilih band dan klik "Analisis Spektrum" untuk memulai
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Fullscreen Modal */}
      {fullscreenMode && (
        <div className="fixed inset-0 bg-white flex flex-col" style={{ zIndex: 9999 }}>
          <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50 flex-shrink-0">
            <h2 className="text-base md:text-lg font-semibold text-gray-900">
              {fullscreenMode === 'map' && 'Peta Lokasi'}
              {fullscreenMode === 'chart' && 'Grafik Spektrum'}
              {fullscreenMode === 'table' && `Seluruh Sinyal Kuat (${results?.occupied_list?.length || 0})`}
            </h2>
            <button
              onClick={() => setFullscreenMode(null)}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-hidden">
            {fullscreenMode === 'map' && (
              <div className="w-full h-full">
                <MapView
                  lat={analysis.location.lat}
                  lon={analysis.location.lon}
                  name={analysis.metadata['Station Name']}
                  stations={results?.occupied_list
                    ?.filter((s: any) => s.station?.latitude && s.station?.longitude)
                    ?.map((s: any) => ({
                      lat: s.station.latitude,
                      lon: s.station.longitude,
                      name: s.station.name,
                      frequency: s.frequency,
                      callsign: s.station.callsign,
                      isLicensed: true
                    })) || []
                  }
                  selectedStation={selectedStation}
                />
              </div>
            )}
            {fullscreenMode === 'chart' && results && (
              <div className="h-full p-4 overflow-auto">
                <SpectrumChart 
                  analysisId={id} 
                  bandNumber={selectedBand}
                  matchedChannels={results.occupied_list}
                  threshold={results.threshold_used}
                  fullscreen
                  onPointClick={(station) => {
                    setSelectedStation(station)
                    setFullscreenMode('map')
                  }}
                />
              </div>
            )}
            {fullscreenMode === 'table' && results && (
              <div className="h-full overflow-auto">
                <FullscreenSignalsTable signals={results.occupied_list || []} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
