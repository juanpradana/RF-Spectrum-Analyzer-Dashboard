from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import plotly.graph_objects as go
import os
from typing import Dict, List

class ReportGenerator:
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
        self.page_width = A4[0] - 3*cm  # Available width
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=20,
            alignment=TA_CENTER,
            leading=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=10,
            spaceBefore=15,
            leading=14
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
    
    def generate_report(self, metadata: Dict, analysis_results: Dict, chart_paths: List[str] = None):
        self._add_header(metadata)
        self._add_metadata_section(metadata)
        self._add_analysis_summary(analysis_results)
        self._add_top_signals_table(analysis_results)
        
        if chart_paths:
            self._add_charts(chart_paths)
        
        self._add_occupied_channels_table(analysis_results)
        self._add_anomalies_section(analysis_results)
        self._add_recommendations(analysis_results)
        self._add_footer()
        
        self.doc.build(self.story)
    
    def _add_header(self, metadata: Dict):
        title = Paragraph(
            "LAPORAN ANALISIS SPEKTRUM FREKUENSI RADIO",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        
        subtitle = Paragraph(
            "Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung",
            self.styles['Normal']
        )
        subtitle.alignment = TA_CENTER
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_metadata_section(self, metadata: Dict):
        heading = Paragraph("Informasi Pengukuran", self.styles['CustomHeading'])
        self.story.append(heading)
        
        data = [
            ['Task ID:', metadata.get('Task ID', 'N/A')],
            ['Lokasi:', metadata.get('Station Name', 'N/A')],
            ['Koordinat:', f"{metadata.get('Location (lat)', 'N/A')}, {metadata.get('Location (lon)', 'N/A')}"],
            ['Waktu Mulai:', str(metadata.get('Start Time', 'N/A'))],
            ['Waktu Selesai:', str(metadata.get('Stop Time', 'N/A'))],
            ['Durasi:', metadata.get('Duration', 'N/A')],
            ['Operator:', metadata.get('Operator ID', 'N/A')]
        ]
        
        col1_width = 3*cm
        col2_width = self.page_width - col1_width
        table = Table(data, colWidths=[col1_width, col2_width])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_analysis_summary(self, results: Dict):
        heading = Paragraph("Ringkasan Analisis", self.styles['CustomHeading'])
        self.story.append(heading)
        
        band_info = results.get('band_info', {})
        band_text = f"Band {results.get('band_number', 'N/A')}: {band_info.get('start_freq', 'N/A')} - {band_info.get('stop_freq', 'N/A')} MHz"
        
        # Count licensed vs unlicensed
        occupied_list = results.get('occupied_list', [])
        licensed_count = len([s for s in occupied_list if s.get('station')])
        unlicensed_count = len(occupied_list) - licensed_count
        
        data = [
            ['Band:', band_text],
            ['Total Channel:', str(results.get('total_channels', 0))],
            ['Threshold:', f"{results.get('threshold_used', 50)} dBµV/m"],
            ['Noise Floor:', f"{results.get('noise_floor', 0)} dBµV/m"],
            ['Channel Terisi:', f"{results.get('occupied_channels', 0)} ({licensed_count} berizin, {unlicensed_count} tidak berizin)"],
            ['Tingkat Okupansi:', f"{results.get('occupancy_percentage', 0)}%"]
        ]
        
        col1_width = 3*cm
        col2_width = self.page_width - col1_width
        table = Table(data, colWidths=[col1_width, col2_width])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#fef5e7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_top_signals_table(self, results: Dict):
        heading = Paragraph("Sinyal Terkuat (Top 20)", self.styles['CustomHeading'])
        self.story.append(heading)
        
        top_signals = results.get('top_signals', [])[:20]
        
        # Calculate column widths proportionally
        col_widths = [0.8*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, self.page_width - 9.3*cm]
        
        data = [['No.', 'Frekuensi', 'Avg (dB)', 'Max (dB)', 'Status', 'Stasiun']]
        
        for i, signal in enumerate(top_signals, 1):
            station = signal.get('station')
            station_name = station.get('name', '-') if station else '-'
            status = 'Berizin' if station else 'Tidak Berizin'
            
            # Truncate long station names
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
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_charts(self, chart_paths: List[str]):
        heading = Paragraph("Visualisasi Data", self.styles['CustomHeading'])
        self.story.append(heading)
        
        for chart_path in chart_paths:
            if os.path.exists(chart_path):
                try:
                    img = Image(chart_path, width=6*inch, height=3.5*inch)
                    self.story.append(img)
                    self.story.append(Spacer(1, 0.2*inch))
                except:
                    pass
    
    def _add_occupied_channels_table(self, results: Dict):
        occupied_list = results.get('occupied_list', [])
        
        if len(occupied_list) == 0:
            return
        
        # Add page break before this section if there are many signals
        if len(occupied_list) > 10:
            self.story.append(PageBreak())
        
        total_count = len(occupied_list)
        display_list = occupied_list[:30]  # Show max 30 in PDF
        
        if total_count > 30:
            heading = Paragraph(f"Daftar Channel Terisi (30 dari {total_count})", self.styles['CustomHeading'])
        else:
            heading = Paragraph(f"Daftar Channel Terisi ({total_count})", self.styles['CustomHeading'])
        self.story.append(heading)
        
        # Calculate column widths
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
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_anomalies_section(self, results: Dict):
        anomalies = results.get('anomalies', [])
        
        if not anomalies:
            return
        
        heading = Paragraph("Anomali Terdeteksi", self.styles['CustomHeading'])
        self.story.append(heading)
        
        for anomaly in anomalies:
            text = f"• {anomaly.get('description', 'N/A')} pada frekuensi {anomaly.get('frequency', 0):.3f} MHz"
            para = Paragraph(text, self.styles['Normal'])
            self.story.append(para)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_recommendations(self, results: Dict):
        heading = Paragraph("Rekomendasi", self.styles['CustomHeading'])
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
        
        for rec in recommendations:
            para = Paragraph(f"• {rec}", self.styles['SmallText'])
            self.story.append(para)
            self.story.append(Spacer(1, 0.05*inch))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def _add_footer(self):
        self.story.append(Spacer(1, 0.5*inch))
        
        footer_text = f"Laporan dibuat secara otomatis pada {datetime.now().strftime('%d %B %Y, %H:%M:%S')}"
        footer = Paragraph(footer_text, self.styles['Normal'])
        footer.alignment = TA_CENTER
        self.story.append(footer)
        
        org_text = "Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung"
        org = Paragraph(org_text, self.styles['Normal'])
        org.alignment = TA_CENTER
        self.story.append(org)

def create_chart_image(channels_df, band_info: Dict, output_path: str):
    band_channels = channels_df[
        (channels_df['frequency'] >= band_info['start_freq']) &
        (channels_df['frequency'] <= band_info['stop_freq'])
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=band_channels['frequency'],
        y=band_channels['avg_field_strength'],
        mode='lines',
        name='Average Field Strength',
        line=dict(color='#3182ce', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=band_channels['frequency'],
        y=band_channels['max_field_strength'],
        mode='lines',
        name='Maximum Field Strength',
        line=dict(color='#e53e3e', width=1, dash='dot'),
        opacity=0.6
    ))
    
    fig.update_layout(
        title=f"Spektrum Band {band_info.get('start_freq', 0)}-{band_info.get('stop_freq', 0)} MHz",
        xaxis_title="Frekuensi (MHz)",
        yaxis_title="Kuat Medan (dBµV/m)",
        template="plotly_white",
        width=800,
        height=450,
        showlegend=True
    )
    
    fig.write_image(output_path)
    return output_path
