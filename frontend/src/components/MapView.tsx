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
  const pendingSelectedStation = useRef<SelectedStation | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const initMap = async () => {
      const L = (await import('leaflet')).default
      await import('leaflet/dist/leaflet.css')

      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove()
          mapInstanceRef.current = null
        } catch (e) {
          console.warn('Error removing map instance:', e)
        }
      }

      if (mapRef.current) {
        markersRef.current.clear()
        
        await new Promise(resolve => setTimeout(resolve, 100))
        
        if (!mapRef.current) return
        
        const map = L.map(mapRef.current, {
          preferCanvas: true,
          fadeAnimation: false,
          zoomAnimation: false
        }).setView([lat, lon], 13)
        
        setTimeout(() => {
          if (map && mapRef.current) {
            map.invalidateSize()
          }
        }, 200)

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
        
        // Check if there's a pending selected station or initial selectedStation prop to show
        const stationToShow = pendingSelectedStation.current || selectedStation
        if (stationToShow) {
          showSelectedStationOnMap(L, map, stationToShow)
          pendingSelectedStation.current = null
        }
      }
    }

    initMap()

    return () => {
      if (mapInstanceRef.current) {
        try {
          markersRef.current.clear()
          mapInstanceRef.current.off()
          mapInstanceRef.current.remove()
          mapInstanceRef.current = null
        } catch (e) {
          console.warn('Error during map cleanup:', e)
        }
      }
    }
  }, [lat, lon, name, stations])

  const showSelectedStationOnMap = async (L: any, map: any, station: SelectedStation) => {
    
    // Remove previous selected marker if exists
    if ((map as any)._selectedMarker) {
      map.removeLayer((map as any)._selectedMarker)
    }
    
    // Create highlighted marker for selected station
    const selectedIcon = L.divIcon({
      className: 'selected-station-marker',
      html: `<div style="
        background-color: #ef4444;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 0 10px rgba(239,68,68,0.8), 0 2px 6px rgba(0,0,0,0.4);
        animation: pulse 1s infinite;
      "></div>
      <style>
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.2); }
        }
      </style>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
      popupAnchor: [0, -10],
    })
    
    const marker = L.marker([station.lat, station.lon], { icon: selectedIcon })
      .addTo(map)
      .bindPopup(`
        <b>📻 ${station.name}</b><br/>
        ${station.callsign ? `Callsign: ${station.callsign}<br/>` : ''}
        Freq: ${station.frequency.toFixed(3)} MHz
      `)
    
    // Store reference to remove later
    ;(map as any)._selectedMarker = marker
    
    // Pan to location and open popup
    map.setView([station.lat, station.lon], 15, { animate: true })
    setTimeout(() => {
      marker.openPopup()
    }, 400)
  }

  useEffect(() => {
    const handleSelectedStation = async () => {
      if (selectedStation) {
        if (mapInstanceRef.current) {
          const L = (await import('leaflet')).default
          showSelectedStationOnMap(L, mapInstanceRef.current, selectedStation)
        } else {
          pendingSelectedStation.current = selectedStation
        }
      }
    }
    
    handleSelectedStation()
  }, [selectedStation])

  return <div ref={mapRef} className="w-full h-full" />
}
