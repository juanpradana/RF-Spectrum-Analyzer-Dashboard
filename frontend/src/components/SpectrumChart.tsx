'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { getChannels } from '@/lib/api'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface SpectrumChartProps {
  analysisId: number
  bandNumber: number
}

export default function SpectrumChart({ analysisId, bandNumber }: SpectrumChartProps) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [analysisId, bandNumber])

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await getChannels(analysisId, bandNumber)
      setData(response.channels)
    } catch (error) {
      console.error('Error loading channels:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Memuat grafik...</p>
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-center text-gray-500">Tidak ada data untuk ditampilkan</p>
      </div>
    )
  }

  const frequencies = data.map((ch: any) => ch.frequency)
  const avgStrengths = data.map((ch: any) => ch.avg_field_strength)
  const maxStrengths = data.map((ch: any) => ch.max_field_strength)

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Grafik Spektrum
      </h2>
      <Plot
        data={[
          {
            x: frequencies,
            y: avgStrengths,
            type: 'scatter',
            mode: 'lines',
            name: 'Average Field Strength',
            line: { color: '#3182ce', width: 2 },
          },
          {
            x: frequencies,
            y: maxStrengths,
            type: 'scatter',
            mode: 'lines',
            name: 'Maximum Field Strength',
            line: { color: '#e53e3e', width: 1, dash: 'dot' },
            opacity: 0.6,
          },
        ]}
        layout={{
          autosize: true,
          xaxis: {
            title: 'Frekuensi (MHz)',
            gridcolor: '#e2e8f0',
          },
          yaxis: {
            title: 'Kuat Medan (dBµV/m)',
            gridcolor: '#e2e8f0',
          },
          plot_bgcolor: '#ffffff',
          paper_bgcolor: '#ffffff',
          showlegend: true,
          legend: {
            x: 0,
            y: 1,
            bgcolor: 'rgba(255,255,255,0.8)',
          },
          margin: { l: 60, r: 30, t: 30, b: 60 },
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
        }}
        style={{ width: '100%', height: '450px' }}
      />
    </div>
  )
}
