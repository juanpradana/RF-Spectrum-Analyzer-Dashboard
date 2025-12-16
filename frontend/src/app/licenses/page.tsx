'use client'

import { useState, useEffect } from 'react'
import { Upload, Database, Trash2, Filter, Download, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

export default function LicensesPage() {
  const [uploading, setUploading] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const [licenses, setLicenses] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [replaceExisting, setReplaceExisting] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [filters, setFilters] = useState({
    province: '',
    service: '',
    freq_min: '',
    freq_max: ''
  })

  useEffect(() => {
    loadStats()
    loadLicenses()
  }, [])

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/licenses/stats`)
      setStats(response.data)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const loadLicenses = async () => {
    setLoading(true)
    try {
      const params: any = { limit: 50 }
      if (filters.province) params.province = filters.province
      if (filters.service) params.service = filters.service
      if (filters.freq_min) params.freq_min = parseFloat(filters.freq_min)
      if (filters.freq_max) params.freq_max = parseFloat(filters.freq_max)

      const response = await axios.get(`${API_URL}/api/licenses`, { params })
      setLicenses(response.data.data)
    } catch (error) {
      console.error('Error loading licenses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setUploadMessage('Error: Hanya file Excel (.xlsx, .xls) yang diperbolehkan')
      return
    }

    setUploading(true)
    setUploadMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('replace_existing', replaceExisting.toString())

      const response = await axios.post(`${API_URL}/api/licenses/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setUploadMessage(`✓ ${response.data.message} - ${response.data.added_count} stasiun ditambahkan`)
      loadStats()
      loadLicenses()
    } catch (error: any) {
      setUploadMessage(`✗ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDeleteAll = async () => {
    if (!confirm('Yakin ingin menghapus semua data perizinan?')) return

    try {
      const response = await axios.delete(`${API_URL}/api/licenses`)
      setUploadMessage(`✓ ${response.data.message}`)
      loadStats()
      loadLicenses()
    } catch (error: any) {
      setUploadMessage(`✗ Error: ${error.response?.data?.detail || error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Database Perizinan Spektrum
                </h1>
                <p className="text-sm text-gray-600">Kelola data izin stasiun radio</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Upload Data</h2>
              <Upload className="h-5 w-5 text-blue-600" />
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="flex items-center space-x-2 cursor-pointer mb-3">
                  <input
                    type="checkbox"
                    checked={replaceExisting}
                    onChange={(e) => setReplaceExisting(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Replace existing data</span>
                </label>

                <label className="block w-full">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer">
                    <Database className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      {uploading ? 'Uploading...' : 'Click to upload Excel file'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">.xlsx, .xls</p>
                  </div>
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
              </div>

              {uploadMessage && (
                <div className={`p-3 rounded text-sm ${
                  uploadMessage.startsWith('✓') 
                    ? 'bg-green-50 text-green-700' 
                    : 'bg-red-50 text-red-700'
                }`}>
                  {uploadMessage}
                </div>
              )}

              <button
                onClick={handleDeleteAll}
                disabled={!stats || stats.total_stations === 0}
                className="w-full flex items-center justify-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                <span>Hapus Semua Data</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistik</h2>
            
            {stats ? (
              <div className="space-y-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Total Stasiun</p>
                  <p className="text-3xl font-bold text-blue-600">{stats.total_stations.toLocaleString()}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">By Service</h3>
                    <div className="space-y-1">
                      {stats.by_service.slice(0, 5).map((s: any, i: number) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span className="text-gray-600">{s.service || 'Unknown'}</span>
                          <span className="font-medium">{s.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Top Provinces</h3>
                    <div className="space-y-1">
                      {stats.top_provinces.slice(0, 5).map((p: any, i: number) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span className="text-gray-600">{p.province}</span>
                          <span className="font-medium">{p.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No data available</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Data Perizinan</h2>
            <Filter className="h-5 w-5 text-gray-600" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <input
              type="text"
              placeholder="Province"
              value={filters.province}
              onChange={(e) => setFilters({...filters, province: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Service"
              value={filters.service}
              onChange={(e) => setFilters({...filters, service: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="Freq Min (MHz)"
              value={filters.freq_min}
              onChange={(e) => setFilters({...filters, freq_min: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="Freq Max (MHz)"
              value={filters.freq_max}
              onChange={(e) => setFilters({...filters, freq_max: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={loadLicenses}
            className="mb-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Apply Filters
          </button>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Callsign</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Station Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Freq (MHz)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Emission</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                      Loading...
                    </td>
                  </tr>
                ) : licenses.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                      No data available. Upload an Excel file to get started.
                    </td>
                  </tr>
                ) : (
                  licenses.map((license) => (
                    <tr key={license.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{license.callsign || '-'}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{license.stn_name || '-'}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{license.clnt_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{license.service}</td>
                      <td className="px-4 py-3 text-sm text-gray-900 font-mono">{license.freq?.toFixed(3)}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{license.city}, {license.province}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {license.eq_mfr || license.eq_mdl ? (
                          <div className="text-xs">
                            {license.eq_mfr && <div>{license.eq_mfr}</div>}
                            {license.eq_mdl && <div className="text-gray-400">{license.eq_mdl}</div>}
                          </div>
                        ) : '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-purple-600 font-mono">
                        {license.emis_class_1 || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          license.status_simf === 'ACTIVE' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {license.status_simf || 'Unknown'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
