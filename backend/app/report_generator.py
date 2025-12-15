from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import plotly.graph_objects as go
import os
from typing import Dict, List

class ReportGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12
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
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_analysis_summary(self, results: Dict):
        heading = Paragraph("Ringkasan Analisis", self.styles['CustomHeading'])
        self.story.append(heading)
        
        band_info = results.get('band_info', {})
        band_text = f"Band {results.get('band_number', 'N/A')}: {band_info.get('start_freq', 'N/A')} - {band_info.get('stop_freq', 'N/A')} MHz"
        
        data = [
            ['Band:', band_text],
            ['Total Channel:', str(results.get('total_channels', 0))],
            ['Threshold:', f"{results.get('threshold_used', 50)} dBµV/m"],
            ['Noise Floor:', f"{results.get('noise_floor', 0)} dBµV/m"],
            ['Channel Terisi:', str(results.get('occupied_channels', 0))],
            ['Tingkat Okupansi:', f"{results.get('occupancy_percentage', 0)}%"]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#fef5e7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_top_signals_table(self, results: Dict):
        heading = Paragraph("20 Sinyal Terkuat", self.styles['CustomHeading'])
        self.story.append(heading)
        
        top_signals = results.get('top_signals', [])[:20]
        
        data = [['No.', 'Frekuensi (MHz)', 'Rata-rata (dBµV/m)', 'Maksimum (dBµV/m)', 'Stasiun']]
        
        for i, signal in enumerate(top_signals, 1):
            station = signal.get('station')
            station_name = station.get('name', '-') if station else '-'
            
            data.append([
                str(i),
                f"{signal.get('frequency', 0):.3f}",
                f"{signal.get('avg_field_strength', 0):.1f}",
                f"{signal.get('max_field_strength', 0):.1f}",
                station_name
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
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
        
        if len(occupied_list) > 20:
            heading = Paragraph(f"Channel Terisi (Menampilkan 20 dari {len(occupied_list)})", self.styles['CustomHeading'])
            self.story.append(heading)
            occupied_list = occupied_list[:20]
        elif len(occupied_list) > 0:
            heading = Paragraph("Daftar Channel Terisi", self.styles['CustomHeading'])
            self.story.append(heading)
        else:
            return
        
        data = [['No.', 'Frekuensi (MHz)', 'Kuat Sinyal (dBµV/m)', 'Stasiun']]
        
        for i, channel in enumerate(occupied_list, 1):
            station = channel.get('station')
            station_name = station.get('name', 'Tidak Teridentifikasi') if station else 'Tidak Teridentifikasi'
            
            data.append([
                str(i),
                f"{channel.get('frequency', 0):.3f}",
                f"{channel.get('avg_field_strength', 0):.1f}",
                station_name
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1.8*inch, 2*inch, 2.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
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
        
        recommendations = []
        
        if occupancy > 70:
            recommendations.append("Tingkat okupansi tinggi (>70%). Perlu dilakukan monitoring lebih lanjut untuk memastikan tidak ada penggunaan frekuensi ilegal.")
        elif occupancy > 50:
            recommendations.append("Tingkat okupansi sedang (50-70%). Monitoring rutin tetap diperlukan.")
        else:
            recommendations.append("Tingkat okupansi rendah (<50%). Spektrum frekuensi masih tersedia untuk alokasi baru.")
        
        if len(anomalies) > 0:
            recommendations.append(f"Terdeteksi {len(anomalies)} anomali sinyal. Perlu investigasi lebih lanjut untuk memastikan kepatuhan regulasi.")
        
        recommendations.append("Lakukan verifikasi stasiun yang tidak teridentifikasi dengan database perizinan terbaru.")
        recommendations.append("Pertimbangkan untuk melakukan pengukuran ulang pada waktu berbeda untuk validasi data.")
        
        for rec in recommendations:
            para = Paragraph(f"• {rec}", self.styles['Normal'])
            self.story.append(para)
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.3*inch))
    
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
