'use client'

import { useState, useEffect } from 'react'
import { Upload, FileText, Activity, Database } from 'lucide-react'
import Link from 'next/link'
import FileUpload from '@/components/FileUpload'
import AnalysisList from '@/components/AnalysisList'
import { getAnalyses } from '@/lib/api'

export default function Home() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  const loadAnalyses = async () => {
    try {
      const data = await getAnalyses()
      setAnalyses(data)
    } catch (error) {
      console.error('Error loading analyses:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalyses()
  }, [])

  const handleUploadSuccess = () => {
    loadAnalyses()
  }

  const handleDeleteAnalysis = (id: number) => {
    setAnalyses(analyses.filter((a: any) => a.id !== id))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  RF Spectrum Analyzer
                </h1>
                <p className="text-sm text-gray-600">
                  Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung
                </p>
              </div>
            </div>
            <Link
              href="/licenses"
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Database className="h-4 w-4" />
              <span>Database Perizinan</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Upload className="h-5 w-5 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Upload File CSV
                </h2>
              </div>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>

            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                Format File CSV
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Separator: ^ (caret)</li>
                <li>• Bagian: Metadata, Bands, Channels</li>
                <li>• Max size: 10MB</li>
              </ul>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <FileText className="h-5 w-5 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Riwayat Analisis
                </h2>
              </div>
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-gray-600">Memuat data...</p>
                </div>
              ) : (
                <AnalysisList analyses={analyses} onDelete={handleDeleteAnalysis} />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
