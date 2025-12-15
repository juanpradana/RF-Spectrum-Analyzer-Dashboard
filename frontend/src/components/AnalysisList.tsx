'use client'

import Link from 'next/link'
import { FileText, MapPin, Calendar } from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface Analysis {
  id: number
  task_id: string
  filename: string
  upload_time: string
  location: {
    lat: number
    lon: number
  }
  station_name: string
  bands_count: number
}

interface AnalysisListProps {
  analyses: Analysis[]
}

export default function AnalysisList({ analyses }: AnalysisListProps) {
  if (analyses.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">Belum ada analisis</p>
        <p className="text-sm text-gray-400 mt-1">
          Upload file CSV untuk memulai analisis
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {analyses.map((analysis) => (
        <Link
          key={analysis.id}
          href={`/analysis/${analysis.id}`}
          className="block bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-colors border border-gray-200"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <FileText className="h-4 w-4 text-blue-600" />
                <h3 className="font-semibold text-gray-900">
                  Task {analysis.task_id}
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-2">{analysis.filename}</p>
              <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <MapPin className="h-3 w-3" />
                  <span>{analysis.station_name || 'Unknown'}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(analysis.upload_time)}</span>
                </div>
                <div>
                  <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    {analysis.bands_count} bands
                  </span>
                </div>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
