'use client'

import { Activity, AlertTriangle, Radio, TrendingUp } from 'lucide-react'
import { getOccupancyColor, getOccupancyBgColor, formatFrequency, formatFieldStrength } from '@/lib/utils'

interface AnalysisResultsProps {
  results: any
}

export default function AnalysisResults({ results }: AnalysisResultsProps) {
  const occupancyColor = getOccupancyColor(results.occupancy_percentage)
  const occupancyBgColor = getOccupancyBgColor(results.occupancy_percentage)

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
