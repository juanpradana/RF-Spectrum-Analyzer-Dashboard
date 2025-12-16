'use client'

import { useEffect, useRef } from 'react'

interface StationMarker {
  lat: number
  lon: number
  name: string
  frequency?: number
  callsign?: string
  isLicensed?: boolean
}

interface SelectedStation {
  lat: number
  lon: number
  name: string
  frequency: number
  callsign?: string
}

interface MapViewProps {
  lat: number
  lon: number
  name: string
  stations?: StationMarker[]
  selectedStation?: SelectedStation | null
}

export default function MapView({ lat, lon, name, stations = [], selectedStation }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<Map<string, any>>(new Map())

  useEffect(() => {
    if (typeof window === 'undefined') return

    const initMap = async () => {
      const L = (await import('leaflet')).default
      await import('leaflet/dist/leaflet.css')

      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
      }

      if (mapRef.current) {
        const map = L.map(mapRef.current).setView([lat, lon], 13)

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
        }).addTo(map)

        const measurementIcon = L.icon({
          iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
          iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
          shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41],
        })

        L.marker([lat, lon], { icon: measurementIcon })
          .addTo(map)
          .bindPopup(`<b>📍 Lokasi Pengukuran</b><br/>${name}`)
          .openPopup()

        if (stations && stations.length > 0) {
          const stationIcon = L.divIcon({
            className: 'custom-station-marker',
            html: `<div style="
              background-color: #10b981;
              width: 12px;
              height: 12px;
              border-radius: 50%;
              border: 2px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6],
            popupAnchor: [0, -6],
          })

          stations.forEach((station) => {
            if (station.lat && station.lon) {
              const marker = L.marker([station.lat, station.lon], { icon: stationIcon })
                .addTo(map)
                .bindPopup(`
                  <b>📻 ${station.name}</b><br/>
                  ${station.callsign ? `Callsign: ${station.callsign}<br/>` : ''}
                  ${station.frequency ? `Freq: ${station.frequency.toFixed(3)} MHz` : ''}
                `)
              const key = `${station.lat}-${station.lon}`
              markersRef.current.set(key, marker)
            }
          })

          const allPoints: [number, number][] = [[lat, lon]]
          stations.forEach((s) => {
            if (s.lat && s.lon) {
              allPoints.push([s.lat, s.lon])
            }
          })
          
          if (allPoints.length > 1) {
            const bounds = L.latLngBounds(allPoints)
            map.fitBounds(bounds, { padding: [30, 30] })
          }
        }

        mapInstanceRef.current = map
      }
    }

    initMap()

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [lat, lon, name, stations])

  useEffect(() => {
    if (selectedStation && mapInstanceRef.current) {
      const map = mapInstanceRef.current
      map.setView([selectedStation.lat, selectedStation.lon], 15, { animate: true })
      
      const key = `${selectedStation.lat}-${selectedStation.lon}`
      const marker = markersRef.current.get(key)
      if (marker) {
        marker.openPopup()
      }
    }
  }, [selectedStation])

  return <div ref={mapRef} className="w-full h-full" />
}
