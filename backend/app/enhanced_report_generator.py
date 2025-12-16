from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import pandas as pd
import os
from typing import Dict, List
from .chart_generator import ChartGenerator
from .map_generator import MapGenerator

class EnhancedReportGenerator:
    """Enhanced PDF report generator with rich visualizations and maps"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        self.page_width = A4[0] - 3*cm
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()
        
        reports_dir = os.path.dirname(output_path)
        self.chart_gen = ChartGenerator(reports_dir)
        self.map_gen = MapGenerator(reports_dir)
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=20,
            alignment=TA_CENTER,
            leading=22,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=18,
            leading=16,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=8,
            spaceBefore=12,
            leading=14,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            wordWrap='CJK'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10,
            spaceBefore=10
        ))
    
    def generate_report(self, metadata: Dict, analysis_results: Dict, 
                       channels_df: pd.DataFrame):
        """Generate comprehensive PDF report with enhanced visualizations"""
        
        self._add_cover_page(metadata, analysis_results)
        self.story.append(PageBreak())
        
        self._add_executive_summary(metadata, analysis_results)
        self.story.append(PageBreak())
        
        self._add_measurement_info(metadata)
        
        self._add_location_map(metadata, analysis_results)
        self.story.append(PageBreak())
        
        self._add_analysis_overview(analysis_results)
        
        self._add_spectrum_visualizations(analysis_results, channels_df)
        self.story.append(PageBreak())
        
        self._add_statistics_section(analysis_results, channels_df)
        self.story.append(PageBreak())
        
        self._add_detailed_findings(analysis_results)
        
        self._add_recommendations(analysis_results)
        
        self._add_footer()
        
        self.doc.build(self.story)
    
    def _add_cover_page(self, metadata: Dict, results: Dict):
        """Add professional cover page"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph(
            "<b>LAPORAN ANALISIS<br/>SPEKTRUM FREKUENSI RADIO</b>",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        band_info = results.get('band_info', {})
        band_text = f"Band {results.get('band_number', 'N/A')}: {band_info.get('start_freq', 'N/A')} - {band_info.get('stop_freq', 'N/A')} MHz"
        
        subtitle = Paragraph(
            f"<b>{band_text}</b>",
            ParagraphStyle(
                'subtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c5282')
            )
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.3*inch))
        
        location = Paragraph(
            f"<i>Lokasi: {metadata.get('Station Name', 'N/A')}</i>",
            ParagraphStyle(
                'location',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER
            )
        )
        self.story.append(location)
        self.story.append(Spacer(1, 1*inch))
        
        data = [
            ['Task ID:', metadata.get('Task ID', 'N/A')],
            ['Tanggal:', datetime.now().strftime('%d %B %Y')],
            ['Okupansi:', f"{results.get('occupancy_percentage', 0):.1f}%"],
            ['Channel Terisi:', f"{results.get('occupied_channels', 0)} / {results.get('total_channels', 0)}"]
        ]
        
        table = Table(data, colWidths=[4*cm, 8*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.story.append(table)
        
        self.story.append(Spacer(1, 1.5*inch))
        
        org = Paragraph(
            "<b>Balai Monitor Spektrum Frekuensi Radio<br/>Kelas II Lampung</b>",
            ParagraphStyle(
                'org',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                leading=16
            )
        )
        self.story.append(org)
    
    def _add_executive_summary(self, metadata: Dict, results: Dict):
        """Add executive summary with key findings"""
        heading = Paragraph("<b>RINGKASAN EKSEKUTIF</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        occupied_list = results.get('occupied_list', [])
        licensed_count = len([s for s in occupied_list if s.get('station')])
        unlicensed_count = len(occupied_list) - licensed_count
        occupancy = results.get('occupancy_percentage', 0)
        
        summary_text = f"""
        Analisis spektrum frekuensi radio telah dilakukan pada lokasi <b>{metadata.get('Station Name', 'N/A')}</b> 
        dengan koordinat {metadata.get('Location (lat)', 'N/A')}, {metadata.get('Location (lon)', 'N/A')}. 
        Pengukuran dilakukan pada band frekuensi {results.get('band_info', {}).get('start_freq', 'N/A')} - 
        {results.get('band_info', {}).get('stop_freq', 'N/A')} MHz.
        <br/><br/>
        <b>Temuan Utama:</b><br/>
        • Tingkat okupansi spektrum: <b>{occupancy:.1f}%</b><br/>
        • Total channel terdeteksi: <b>{results.get('total_channels', 0)}</b><br/>
        • Channel terisi: <b>{results.get('occupied_channels', 0)}</b> 
        ({licensed_count} berizin, {unlicensed_count} tidak berizin)<br/>
        • Noise floor: <b>{results.get('noise_floor', 0):.1f} dBµV/m</b><br/>
        • Threshold yang digunakan: <b>{results.get('threshold_used', 50):.1f} dBµV/m</b>
        """
        
        para = Paragraph(summary_text, self.styles['SmallText'])
        self.story.append(para)
        self.story.append(Spacer(1, 0.3*inch))
        
        if occupancy > 70:
            status = "TINGGI"
            color = colors.HexColor('#e53e3e')
            recommendation = "Memerlukan perhatian khusus dan monitoring intensif"
        elif occupancy > 50:
            status = "SEDANG"
            color = colors.HexColor('#d69e2e')
            recommendation = "Monitoring rutin diperlukan"
        else:
            status = "RENDAH"
            color = colors.HexColor('#38a169')
            recommendation = "Spektrum masih tersedia untuk alokasi baru"
        
        status_data = [[f"Status Okupansi: {status}", recommendation]]
        status_table = Table(status_data, colWidths=[5*cm, self.page_width - 5*cm])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), color),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f7fafc')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 2, colors.grey)
        ]))
        self.story.append(status_table)
    
    def _add_measurement_info(self, metadata: Dict):
        """Add detailed measurement information"""
        heading = Paragraph("<b>INFORMASI PENGUKURAN</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        data = [
            ['Task ID:', metadata.get('Task ID', 'N/A')],
            ['Lokasi Pengukuran:', metadata.get('Station Name', 'N/A')],
            ['Koordinat:', f"Lat: {metadata.get('Location (lat)', 'N/A')}, Lon: {metadata.get('Location (lon)', 'N/A')}"],
            ['Waktu Mulai:', str(metadata.get('Start Time', 'N/A'))],
            ['Waktu Selesai:', str(metadata.get('Stop Time', 'N/A'))],
            ['Durasi Pengukuran:', metadata.get('Duration', 'N/A')],
            ['Operator:', metadata.get('Operator ID', 'N/A')],
            ['Tanggal Laporan:', datetime.now().strftime('%d %B %Y, %H:%M:%S')]
        ]
        
        table = Table(data, colWidths=[4*cm, self.page_width - 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_location_map(self, metadata: Dict, results: Dict):
        """Add location map with station markers"""
        heading = Paragraph("<b>PETA LOKASI PENGUKURAN</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        task_id = metadata.get('Task ID', 'unknown')
        map_path = os.path.join(
            os.path.dirname(self.output_path),
            f"map_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        try:
            occupied_list = results.get('occupied_list', [])
            self.map_gen.create_station_map(metadata, occupied_list, map_path)
            
            if os.path.exists(map_path):
                img = Image(map_path, width=6.5*inch, height=4.3*inch)
                self.story.append(img)
                
                caption = Paragraph(
                    "<i>Gambar: Peta lokasi pengukuran (merah) dan stasiun berizin terdekat (biru)</i>",
                    self.styles['SmallText']
                )
                caption.alignment = TA_CENTER
                self.story.append(Spacer(1, 0.1*inch))
                self.story.append(caption)
        except Exception as e:
            note = Paragraph(
                f"<i>Catatan: Peta tidak dapat dibuat ({str(e)})</i>",
                self.styles['SmallText']
            )
            self.story.append(note)
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_analysis_overview(self, results: Dict):
        """Add analysis overview with key metrics"""
        heading = Paragraph("<b>RINGKASAN ANALISIS</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        band_info = results.get('band_info', {})
        band_text = f"Band {results.get('band_number', 'N/A')}: {band_info.get('start_freq', 'N/A')} - {band_info.get('stop_freq', 'N/A')} MHz"
        
        occupied_list = results.get('occupied_list', [])
        licensed_count = len([s for s in occupied_list if s.get('station')])
        unlicensed_count = len(occupied_list) - licensed_count
        
        data = [
            ['Band Frekuensi:', band_text],
            ['Total Channel:', str(results.get('total_channels', 0))],
            ['Threshold:', f"{results.get('threshold_used', 50):.1f} dBµV/m"],
            ['Noise Floor:', f"{results.get('noise_floor', 0):.1f} dBµV/m"],
            ['Channel Terisi:', f"{results.get('occupied_channels', 0)}"],
            ['  - Berizin:', f"{licensed_count}"],
            ['  - Tidak Berizin:', f"{unlicensed_count}"],
            ['Tingkat Okupansi:', f"{results.get('occupancy_percentage', 0):.1f}%"]
        ]
        
        table = Table(data, colWidths=[4*cm, self.page_width - 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#fef5e7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_spectrum_visualizations(self, results: Dict, channels_df: pd.DataFrame):
        """Add comprehensive spectrum visualizations"""
        heading = Paragraph("<b>VISUALISASI DATA SPEKTRUM</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        task_id = results.get('band_info', {}).get('start_freq', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_path = os.path.dirname(self.output_path)
        
        band_info = results.get('band_info', {})
        threshold = results.get('threshold_used', 50)
        
        charts = []
        
        try:
            spectrum_path = os.path.join(base_path, f"spectrum_{task_id}_{timestamp}.png")
            self.chart_gen.create_spectrum_chart(channels_df, band_info, threshold, spectrum_path)
            charts.append(('Grafik Spektrum Frekuensi', spectrum_path))
        except Exception as e:
            print(f"Error creating spectrum chart: {e}")
        
        try:
            pie_path = os.path.join(base_path, f"occupancy_pie_{task_id}_{timestamp}.png")
            self.chart_gen.create_occupancy_pie_chart(results, pie_path)
            charts.append(('Distribusi Okupansi Channel', pie_path))
        except Exception as e:
            print(f"Error creating pie chart: {e}")
        
        try:
            hist_path = os.path.join(base_path, f"histogram_{task_id}_{timestamp}.png")
            self.chart_gen.create_signal_strength_histogram(channels_df, band_info, threshold, hist_path)
            charts.append(('Distribusi Kuat Medan Sinyal', hist_path))
        except Exception as e:
            print(f"Error creating histogram: {e}")
        
        try:
            heatmap_path = os.path.join(base_path, f"heatmap_{task_id}_{timestamp}.png")
            self.chart_gen.create_frequency_occupancy_heatmap(channels_df, band_info, threshold, heatmap_path)
            charts.append(('Peta Okupansi Frekuensi', heatmap_path))
        except Exception as e:
            print(f"Error creating heatmap: {e}")
        
        try:
            bar_path = os.path.join(base_path, f"top_signals_{task_id}_{timestamp}.png")
            self.chart_gen.create_top_signals_bar_chart(results, bar_path)
            charts.append(('15 Sinyal Terkuat', bar_path))
        except Exception as e:
            print(f"Error creating bar chart: {e}")
        
        for idx, (title, chart_path) in enumerate(charts):
            if os.path.exists(chart_path):
                if idx > 0 and idx % 2 == 0:
                    self.story.append(PageBreak())
                
                subheading = Paragraph(f"<b>{title}</b>", self.styles['SectionHeading'])
                self.story.append(subheading)
                
                img = Image(chart_path, width=6.5*inch, height=3.8*inch)
                self.story.append(img)
                self.story.append(Spacer(1, 0.2*inch))
    
    def _add_statistics_section(self, results: Dict, channels_df: pd.DataFrame):
        """Add detailed statistics section"""
        heading = Paragraph("<b>STATISTIK DETAIL</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        task_id = results.get('band_info', {}).get('start_freq', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stats_path = os.path.join(
            os.path.dirname(self.output_path),
            f"statistics_{task_id}_{timestamp}.png"
        )
        
        try:
            band_info = results.get('band_info', {})
            self.chart_gen.create_statistics_panel(results, channels_df, band_info, stats_path)
            
            if os.path.exists(stats_path):
                img = Image(stats_path, width=6*inch, height=5.2*inch)
                self.story.append(img)
        except Exception as e:
            print(f"Error creating statistics panel: {e}")
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_detailed_findings(self, results: Dict):
        """Add detailed findings with tables"""
        heading = Paragraph("<b>TEMUAN DETAIL</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        self._add_top_signals_table(results)
        
        self._add_occupied_channels_table(results)
        
        self._add_anomalies_section(results)
    
    def _add_top_signals_table(self, results: Dict):
        """Add top signals table"""
        subheading = Paragraph("<b>Sinyal Terkuat (Top 20)</b>", self.styles['SectionHeading'])
        self.story.append(subheading)
        
        top_signals = results.get('top_signals', [])[:20]
        
        col_widths = [0.8*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, self.page_width - 9.3*cm]
        
        data = [['No.', 'Frekuensi', 'Avg (dB)', 'Max (dB)', 'Status', 'Stasiun']]
        
        for i, signal in enumerate(top_signals, 1):
            station = signal.get('station')
            station_name = station.get('name', '-') if station else '-'
            status = 'Berizin' if station else 'Tidak Berizin'
            
            if len(station_name) > 25:
                station_name = station_name[:22] + '...'
            
            data.append([
                str(i),
                f"{signal.get('frequency', 0):.3f}",
                f"{signal.get('avg_field_strength', 0):.1f}",
                f"{signal.get('max_field_strength', 0):.1f}",
                status,
                station_name
            ])
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (4, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_occupied_channels_table(self, results: Dict):
        """Add occupied channels table"""
        occupied_list = results.get('occupied_list', [])
        
        if len(occupied_list) == 0:
            return
        
        if len(occupied_list) > 15:
            self.story.append(PageBreak())
        
        total_count = len(occupied_list)
        display_list = occupied_list[:30]
        
        if total_count > 30:
            subheading = Paragraph(f"<b>Daftar Channel Terisi (30 dari {total_count})</b>", self.styles['SectionHeading'])
        else:
            subheading = Paragraph(f"<b>Daftar Channel Terisi ({total_count})</b>", self.styles['SectionHeading'])
        self.story.append(subheading)
        
        col_widths = [0.8*cm, 2.2*cm, 1.8*cm, 1.8*cm, 2*cm, self.page_width - 8.6*cm]
        
        data = [['No.', 'Frekuensi', 'Avg (dB)', 'Max (dB)', 'Status', 'Stasiun / Client']]
        
        for i, channel in enumerate(display_list, 1):
            station = channel.get('station')
            if station:
                station_name = station.get('name', '-')
                if len(station_name) > 30:
                    station_name = station_name[:27] + '...'
                status = 'Berizin'
            else:
                station_name = '-'
                status = 'Tidak Berizin'
            
            data.append([
                str(i),
                f"{channel.get('frequency', 0):.3f}",
                f"{channel.get('avg_field_strength', 0):.1f}",
                f"{channel.get('max_field_strength', 0):.1f}",
                status,
                station_name
            ])
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (4, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        
        self.story.append(table)
        
        if total_count > 30:
            note = Paragraph(
                f"<i>Catatan: Menampilkan 30 dari {total_count} channel terisi. Lihat data lengkap di aplikasi.</i>",
                self.styles['SmallText']
            )
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(note)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_anomalies_section(self, results: Dict):
        """Add anomalies section"""
        anomalies = results.get('anomalies', [])
        
        if not anomalies:
            return
        
        subheading = Paragraph("<b>Anomali Terdeteksi</b>", self.styles['SectionHeading'])
        self.story.append(subheading)
        
        for anomaly in anomalies:
            text = f"• {anomaly.get('description', 'N/A')} pada frekuensi {anomaly.get('frequency', 0):.3f} MHz"
            para = Paragraph(text, self.styles['Normal'])
            self.story.append(para)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_recommendations(self, results: Dict):
        """Add recommendations section"""
        self.story.append(PageBreak())
        
        heading = Paragraph("<b>REKOMENDASI</b>", self.styles['CustomHeading'])
        self.story.append(heading)
        
        occupancy = results.get('occupancy_percentage', 0)
        anomalies = results.get('anomalies', [])
        occupied_list = results.get('occupied_list', [])
        unlicensed_count = len([s for s in occupied_list if not s.get('station')])
        
        recommendations = []
        
        if occupancy > 70:
            recommendations.append("Tingkat okupansi tinggi (>70%). Perlu dilakukan monitoring lebih lanjut untuk memastikan tidak ada penggunaan frekuensi ilegal.")
        elif occupancy > 50:
            recommendations.append("Tingkat okupansi sedang (50-70%). Monitoring rutin tetap diperlukan.")
        else:
            recommendations.append("Tingkat okupansi rendah (<50%). Spektrum frekuensi masih tersedia untuk alokasi baru.")
        
        if unlicensed_count > 0:
            recommendations.append(f"Terdeteksi {unlicensed_count} sinyal tidak berizin. Perlu investigasi untuk identifikasi sumber sinyal.")
        
        if len(anomalies) > 0:
            recommendations.append(f"Terdeteksi {len(anomalies)} anomali sinyal. Perlu investigasi lebih lanjut untuk memastikan kepatuhan regulasi.")
        
        recommendations.append("Lakukan verifikasi stasiun yang tidak teridentifikasi dengan database perizinan terbaru.")
        recommendations.append("Pertimbangkan untuk melakukan pengukuran ulang pada waktu berbeda untuk validasi data.")
        recommendations.append("Koordinasi dengan operator untuk memastikan penggunaan frekuensi sesuai izin.")
        
        for rec in recommendations:
            para = Paragraph(f"• {rec}", self.styles['SmallText'])
            self.story.append(para)
            self.story.append(Spacer(1, 0.05*inch))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_footer(self):
        """Add footer"""
        self.story.append(Spacer(1, 0.5*inch))
        
        footer_text = f"Laporan dibuat secara otomatis pada {datetime.now().strftime('%d %B %Y, %H:%M:%S')}"
        footer = Paragraph(footer_text, self.styles['SmallText'])
        footer.alignment = TA_CENTER
        self.story.append(footer)
        
        org_text = "<b>Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung</b>"
        org = Paragraph(org_text, self.styles['Normal'])
        org.alignment = TA_CENTER
        self.story.append(org)
