'use client'

import { useState } from 'react'
import { Activity, AlertTriangle, Radio, TrendingUp, CheckCircle, XCircle, ChevronDown, ChevronUp, Maximize2 } from 'lucide-react'
import { getOccupancyColor, getOccupancyBgColor, formatFrequency, formatFieldStrength } from '@/lib/utils'

interface AnalysisResultsProps {
  results: any
  onFullscreen?: () => void
  fullscreen?: boolean
}

export default function AnalysisResults({ results, onFullscreen, fullscreen = false }: AnalysisResultsProps) {
  const [showAllSignals, setShowAllSignals] = useState(fullscreen)
  const occupancyColor = getOccupancyColor(results.occupancy_percentage)
  const occupancyBgColor = getOccupancyBgColor(results.occupancy_percentage)

  const licensedCount = results.occupied_list?.filter((s: any) => s.station)?.length || 0
  const unlicensedCount = (results.occupied_list?.length || 0) - licensedCount

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="h-5 w-5 text-blue-600" />
            <h3 className="text-sm font-medium text-gray-600">Total Channel</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {results.total_channels}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Radio className="h-5 w-5 text-green-600" />
            <h3 className="text-sm font-medium text-gray-600">Channel Terisi</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {results.occupied_channels}
          </p>
          <div className="mt-1 text-xs text-gray-500">
            <span className="text-green-600">{licensedCount} berizin</span>
            {' / '}
            <span className="text-amber-600">{unlicensedCount} tidak berizin</span>
          </div>
        </div>

        <div className={`bg-white rounded-lg shadow p-4 ${occupancyBgColor}`}>
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className={`h-5 w-5 ${occupancyColor}`} />
            <h3 className="text-sm font-medium text-gray-600">Okupansi</h3>
          </div>
          <p className={`text-2xl font-bold ${occupancyColor}`}>
            {results.occupancy_percentage}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="h-5 w-5 text-gray-600" />
            <h3 className="text-sm font-medium text-gray-600">Noise Floor</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {results.noise_floor} dB
          </p>
        </div>
      </div>

      {results.anomalies && results.anomalies.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900 mb-2">
                Anomali Terdeteksi ({results.anomalies.length})
              </h3>
              <ul className="space-y-1 text-sm text-yellow-800">
                {results.anomalies.map((anomaly: any, idx: number) => (
                  <li key={idx}>
                    • {anomaly.description} ({formatFrequency(anomaly.frequency)})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className={`bg-white rounded-lg shadow-lg p-4 md:p-6 ${fullscreen ? 'shadow-none' : ''}`}>
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h2 className="text-base md:text-lg font-semibold text-gray-900">
            Seluruh Sinyal Kuat ({results.occupied_list?.length || 0})
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAllSignals(!showAllSignals)}
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showAllSignals ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  <span className="hidden sm:inline">Sembunyikan</span>
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  <span className="hidden sm:inline">Tampilkan Semua</span>
                </>
              )}
            </button>
            {!fullscreen && onFullscreen && (
              <button
                onClick={onFullscreen}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Fullscreen"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
        <div className="overflow-x-auto -mx-4 md:mx-0">
          <div className="inline-block min-w-full align-middle">
            <table className="min-w-full divide-y divide-gray-200 text-xs md:text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    No.
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Frekuensi
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Avg (dB)
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Max (dB)
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Status
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                    Stasiun / Client
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    Callsign
                  </th>
                  <th className="px-2 md:px-4 py-2 md:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                    Perangkat
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(showAllSignals ? results.occupied_list : results.occupied_list?.slice(0, 10))?.map((signal: any, idx: number) => (
                  <tr key={idx} className={`hover:bg-gray-50 ${signal.station ? 'bg-green-50/30' : 'bg-amber-50/30'}`}>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap text-gray-900">
                      {idx + 1}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap font-mono text-gray-900">
                      {formatFrequency(signal.frequency)}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap text-gray-900">
                      {signal.avg_field_strength?.toFixed(1)}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap text-gray-900">
                      {signal.max_field_strength?.toFixed(1)}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap">
                      {signal.station ? (
                        <span className="inline-flex items-center gap-1 px-1.5 md:px-2 py-0.5 md:py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3" />
                          <span className="hidden sm:inline">Berizin</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-1.5 md:px-2 py-0.5 md:py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                          <XCircle className="h-3 w-3" />
                          <span className="hidden sm:inline">Tidak</span>
                        </span>
                      )}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-gray-600">
                      {signal.station ? (
                        <div className="max-w-[200px]">
                          <div className="font-medium truncate">{signal.station.name}</div>
                          {signal.station.clnt_name && signal.station.clnt_name !== signal.station.name && (
                            <div className="text-xs text-gray-400 truncate">{signal.station.clnt_name}</div>
                          )}
                        </div>
                      ) : '-'}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 whitespace-nowrap text-gray-600">
                      {signal.station?.callsign || '-'}
                    </td>
                    <td className="px-2 md:px-4 py-2 md:py-3 text-gray-600">
                      {signal.station ? (
                        <div className="text-xs max-w-[150px]">
                          {signal.station.eq_mfr && <div className="truncate">{signal.station.eq_mfr}</div>}
                          {signal.station.eq_mdl && <div className="text-gray-400 truncate">{signal.station.eq_mdl}</div>}
                          {signal.station.emis_class_1 && (
                            <div className="text-purple-600">{signal.station.emis_class_1}</div>
                          )}
                        </div>
                      ) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {!showAllSignals && results.occupied_list?.length > 10 && (
          <p className="mt-2 text-xs md:text-sm text-gray-500 text-center">
            Menampilkan 10 dari {results.occupied_list.length} sinyal.
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          20 Sinyal Terkuat
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  No.
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Frekuensi
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rata-rata
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Maksimum
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stasiun
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.top_signals.slice(0, 20).map((signal: any, idx: number) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {idx + 1}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatFrequency(signal.frequency)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatFieldStrength(signal.avg_field_strength)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatFieldStrength(signal.max_field_strength)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    {signal.station ? signal.station.name : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
