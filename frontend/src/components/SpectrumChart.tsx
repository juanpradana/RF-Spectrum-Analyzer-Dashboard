'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { getChannels } from '@/lib/api'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface MatchedChannel {
  frequency: number
  avg_field_strength: number
  station: {
    name: string
    callsign?: string
  } | null
}

interface SpectrumChartProps {
  analysisId: number
  bandNumber: number
  matchedChannels?: MatchedChannel[]
  threshold?: number
}

export default function SpectrumChart({ 
  analysisId, 
  bandNumber, 
  matchedChannels = [],
  threshold 
}: SpectrumChartProps) {
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

  const matchedFreqs = matchedChannels
    .filter((ch) => ch.station)
    .map((ch) => ch.frequency)
  const matchedStrengths = matchedChannels
    .filter((ch) => ch.station)
    .map((ch) => ch.avg_field_strength)
  const matchedLabels = matchedChannels
    .filter((ch) => ch.station)
    .map((ch) => `${ch.station?.name || 'Unknown'}<br>${ch.frequency.toFixed(3)} MHz`)

  const unmatchedFreqs = matchedChannels
    .filter((ch) => !ch.station)
    .map((ch) => ch.frequency)
  const unmatchedStrengths = matchedChannels
    .filter((ch) => !ch.station)
    .map((ch) => ch.avg_field_strength)

  const plotData: any[] = [
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
  ]

  if (matchedFreqs.length > 0) {
    plotData.push({
      x: matchedFreqs,
      y: matchedStrengths,
      type: 'scatter',
      mode: 'markers',
      name: 'Terisi (Berizin)',
      marker: { 
        color: '#10b981', 
        size: 10, 
        symbol: 'circle',
        line: { color: 'white', width: 1 }
      },
      text: matchedLabels,
      hovertemplate: '%{text}<br>%{y:.1f} dBµV/m<extra></extra>',
    })
  }

  if (unmatchedFreqs.length > 0) {
    plotData.push({
      x: unmatchedFreqs,
      y: unmatchedStrengths,
      type: 'scatter',
      mode: 'markers',
      name: 'Terisi (Tidak Berizin)',
      marker: { 
        color: '#f59e0b', 
        size: 10, 
        symbol: 'diamond',
        line: { color: 'white', width: 1 }
      },
      hovertemplate: '%{x:.3f} MHz<br>%{y:.1f} dBµV/m<extra></extra>',
    })
  }

  const shapes: any[] = []
  if (threshold) {
    shapes.push({
      type: 'line',
      x0: Math.min(...frequencies),
      x1: Math.max(...frequencies),
      y0: threshold,
      y1: threshold,
      line: { color: '#9333ea', width: 2, dash: 'dash' },
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Grafik Spektrum
      </h2>
      {threshold && (
        <div className="mb-2 flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            Berizin
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-amber-500" style={{ clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }}></span>
            Tidak Berizin
          </span>
          <span className="flex items-center gap-1">
            <span className="w-6 border-t-2 border-dashed border-purple-600"></span>
            Threshold: {threshold} dBµV/m
          </span>
        </div>
      )}
      <Plot
        data={plotData}
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
          shapes: shapes,
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
