import folium
from folium import plugins
import io
from PIL import Image
from typing import Dict, List, Optional
import os

class MapGenerator:
    """Generate maps for spectrum analysis reports"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_station_map(self, metadata: Dict, occupied_list: List[Dict], 
                          output_path: str, zoom_start: int = 13) -> str:
        """
        Create a map showing the measurement station location and nearby licensed stations
        
        Args:
            metadata: Measurement metadata containing station location
            occupied_list: List of occupied channels with station info
            output_path: Path to save the map image
            zoom_start: Initial zoom level for the map
        """
        lat = metadata.get('Location (lat)')
        lon = metadata.get('Location (lon)')
        station_name = metadata.get('Station Name', 'Unknown Location')
        
        if lat is None or lon is None:
            lat, lon = -5.4292, 105.2619
            station_name = "Default Location (Lampung)"
        
        m = folium.Map(
            location=[lat, lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<b>Lokasi Pengukuran</b><br>{station_name}<br>Lat: {lat}<br>Lon: {lon}",
                max_width=250
            ),
            tooltip=station_name,
            icon=folium.Icon(color='red', icon='signal', prefix='fa')
        ).add_to(m)
        
        folium.Circle(
            location=[lat, lon],
            radius=5000,
            popup='Area Pengukuran (5km)',
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.1,
            weight=2,
            dashArray='5, 5'
        ).add_to(m)
        
        licensed_stations = []
        for channel in occupied_list:
            station = channel.get('station')
            if station:
                station_lat = station.get('latitude')
                station_lon = station.get('longitude')
                if station_lat and station_lon:
                    licensed_stations.append({
                        'name': station.get('name', 'Unknown'),
                        'lat': station_lat,
                        'lon': station_lon,
                        'frequency': channel.get('frequency', 0),
                        'service': station.get('service', 'N/A'),
                        'callsign': station.get('callsign', 'N/A')
                    })
        
        for idx, station in enumerate(licensed_stations[:50]):
            folium.Marker(
                location=[station['lat'], station['lon']],
                popup=folium.Popup(
                    f"<b>{station['name']}</b><br>"
                    f"Callsign: {station['callsign']}<br>"
                    f"Service: {station['service']}<br>"
                    f"Freq: {station['frequency']:.3f} MHz",
                    max_width=250
                ),
                tooltip=station['name'],
                icon=folium.Icon(color='blue', icon='broadcast-tower', prefix='fa')
            ).add_to(m)
        
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 220px; height: auto; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; border-radius: 5px; padding: 10px">
        <p style="margin: 0; font-weight: bold;">Legenda:</p>
        <p style="margin: 5px 0;"><i class="fa fa-signal" style="color:red"></i> Lokasi Pengukuran</p>
        <p style="margin: 5px 0;"><i class="fa fa-broadcast-tower" style="color:blue"></i> Stasiun Berizin</p>
        <p style="margin: 5px 0; font-size: 11px; color: #666;">
        Menampilkan max 50 stasiun terdekat
        </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        plugins.Fullscreen(
            position='topleft',
            title='Fullscreen',
            title_cancel='Exit Fullscreen',
            force_separate_button=True
        ).add_to(m)
        
        plugins.MiniMap(toggle_display=True).add_to(m)
        
        html_path = output_path.replace('.png', '.html')
        m.save(html_path)
        
        try:
            self._convert_html_to_image(html_path, output_path)
        except Exception as e:
            print(f"Warning: Could not convert map to image: {e}")
            print("HTML map saved instead")
        
        return output_path
    
    def _convert_html_to_image(self, html_path: str, output_path: str, 
                               width: int = 1200, height: int = 800):
        """Convert HTML map to PNG image using selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            import time
            import shutil
            import subprocess
            
            chrome_binary = shutil.which('google-chrome') or shutil.which('chromium-browser') or '/usr/bin/google-chrome'
            chromedriver_path = '/usr/local/bin/chromedriver' if os.path.exists('/usr/local/bin/chromedriver') else (shutil.which('chromedriver') or '/usr/bin/chromedriver')
            
            print(f"Using Chrome binary: {chrome_binary}")
            print(f"Using ChromeDriver: {chromedriver_path}")
            
            result = subprocess.run([chrome_binary, '--version'], capture_output=True, text=True)
            print(f"Chrome version: {result.stdout.strip()}")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--metrics-recording-only')
            chrome_options.add_argument('--mute-audio')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument(f'--user-data-dir={self.output_dir}/chrome-temp')
            chrome_options.add_argument(f'--window-size={width},{height}')
            chrome_options.binary_location = chrome_binary
            
            service_env = os.environ.copy()
            service_env['SNAP_NAME'] = 'chromium'
            service_env['SNAP_INSTANCE_NAME'] = 'chromium'
            service_env['HOME'] = self.output_dir
            
            import tempfile
            log_path = os.path.join(tempfile.gettempdir(), 'chromedriver.log')
            
            service = Service(
                executable_path=chromedriver_path,
                service_args=['--verbose', f'--log-path={log_path}'],
                env=service_env
            )
            
            print(f"ChromeDriver log: {log_path}")
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(f'file:///{os.path.abspath(html_path)}')
            time.sleep(2)
            
            driver.save_screenshot(output_path)
            driver.quit()
            
        except ImportError:
            print("Selenium not available, using alternative method")
            self._create_static_map_image(output_path, width, height)
        except Exception as e:
            print(f"Error converting map: {e}")
            import traceback
            traceback.print_exc()
            self._create_static_map_image(output_path, width, height)
    
    def _create_static_map_image(self, output_path: str, width: int = 1200, height: int = 800):
        """Create a placeholder image when map conversion fails"""
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        text = "Peta Lokasi Pengukuran"
        subtext = "Lihat file HTML untuk peta interaktif"
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2 - 30
        
        draw.text((x, y), text, fill='#333333', font=font)
        
        bbox2 = draw.textbbox((0, 0), subtext, font=small_font)
        text_width2 = bbox2[2] - bbox2[0]
        x2 = (width - text_width2) / 2
        y2 = y + text_height + 20
        
        draw.text((x2, y2), subtext, fill='#666666', font=small_font)
        
        img.save(output_path)
    
    def create_coverage_heatmap(self, metadata: Dict, occupied_list: List[Dict],
                               output_path: str) -> str:
        """Create a heatmap showing signal coverage intensity"""
        lat = metadata.get('Location (lat)')
        lon = metadata.get('Location (lon)')
        
        if lat is None or lon is None:
            lat, lon = -5.4292, 105.2619
        
        m = folium.Map(
            location=[lat, lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        heat_data = []
        for channel in occupied_list[:100]:
            station = channel.get('station')
            if station:
                station_lat = station.get('latitude')
                station_lon = station.get('longitude')
                if station_lat and station_lon:
                    intensity = channel.get('avg_field_strength', 50) / 100.0
                    heat_data.append([station_lat, station_lon, intensity])
        
        if not heat_data:
            heat_data = [[lat, lon, 0.5]]
        
        plugins.HeatMap(
            heat_data,
            min_opacity=0.3,
            max_zoom=18,
            radius=25,
            blur=35,
            gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(m)
        
        folium.Marker(
            location=[lat, lon],
            popup='Lokasi Pengukuran',
            icon=folium.Icon(color='red', icon='signal', prefix='fa')
        ).add_to(m)
        
        html_path = output_path.replace('.png', '_heatmap.html')
        m.save(html_path)
        
        try:
            self._convert_html_to_image(html_path, output_path)
        except:
            self._create_static_map_image(output_path)
        
        return output_path
