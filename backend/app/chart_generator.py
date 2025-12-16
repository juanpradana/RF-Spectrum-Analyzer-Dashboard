import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import os

class ChartGenerator:
    """Generate various charts for spectrum analysis reports"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_spectrum_chart(self, channels_df: pd.DataFrame, band_info: Dict, 
                             threshold: float, output_path: str) -> str:
        """Create main spectrum chart with threshold line"""
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
            line=dict(color='#3182ce', width=2),
            fill='tozeroy',
            fillcolor='rgba(49, 130, 206, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=band_channels['frequency'],
            y=band_channels['max_field_strength'],
            mode='lines',
            name='Maximum Field Strength',
            line=dict(color='#e53e3e', width=1.5, dash='dot'),
            opacity=0.7
        ))
        
        fig.add_hline(
            y=threshold, 
            line_dash="dash", 
            line_color="orange",
            annotation_text=f"Threshold: {threshold} dBµV/m",
            annotation_position="right"
        )
        
        fig.update_layout(
            title=dict(
                text=f"<b>Spektrum Frekuensi Band {band_info.get('start_freq', 0)}-{band_info.get('stop_freq', 0)} MHz</b>",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="<b>Frekuensi (MHz)</b>",
            yaxis_title="<b>Kuat Medan (dBµV/m)</b>",
            template="plotly_white",
            width=900,
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        fig.write_image(output_path)
        return output_path
    
    def create_occupancy_pie_chart(self, results: Dict, output_path: str) -> str:
        """Create pie chart showing occupancy breakdown"""
        occupied_list = results.get('occupied_list', [])
        total_channels = results.get('total_channels', 0)
        
        licensed_count = len([s for s in occupied_list if s.get('station')])
        unlicensed_count = len(occupied_list) - licensed_count
        free_channels = total_channels - len(occupied_list)
        
        labels = ['Channel Kosong', 'Berizin', 'Tidak Berizin']
        values = [free_channels, licensed_count, unlicensed_count]
        colors = ['#48bb78', '#3182ce', '#e53e3e']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textinfo='label+percent+value',
            textfont_size=12,
            pull=[0.05, 0, 0.1]
        )])
        
        fig.update_layout(
            title=dict(
                text=f"<b>Distribusi Okupansi Channel</b><br><sub>Total: {total_channels} channels</sub>",
                x=0.5,
                xanchor='center'
            ),
            width=600,
            height=500,
            showlegend=True,
            template="plotly_white"
        )
        
        fig.write_image(output_path)
        return output_path
    
    def create_signal_strength_histogram(self, channels_df: pd.DataFrame, 
                                        band_info: Dict, threshold: float,
                                        output_path: str) -> str:
        """Create histogram of signal strength distribution"""
        band_channels = channels_df[
            (channels_df['frequency'] >= band_info['start_freq']) &
            (channels_df['frequency'] <= band_info['stop_freq'])
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=band_channels['avg_field_strength'],
            nbinsx=50,
            name='Distribution',
            marker=dict(
                color='#3182ce',
                line=dict(color='white', width=1)
            ),
            opacity=0.75
        ))
        
        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Threshold: {threshold} dB",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title=dict(
                text="<b>Distribusi Kuat Medan Sinyal</b>",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="<b>Kuat Medan (dBµV/m)</b>",
            yaxis_title="<b>Jumlah Channel</b>",
            template="plotly_white",
            width=900,
            height=450,
            showlegend=False,
            bargap=0.1
        )
        
        fig.write_image(output_path)
        return output_path
    
    def create_statistics_panel(self, results: Dict, channels_df: pd.DataFrame,
                               band_info: Dict, output_path: str) -> str:
        """Create a panel with key statistics"""
        band_channels = channels_df[
            (channels_df['frequency'] >= band_info['start_freq']) &
            (channels_df['frequency'] <= band_info['stop_freq'])
        ]
        
        occupied_list = results.get('occupied_list', [])
        licensed_count = len([s for s in occupied_list if s.get('station')])
        unlicensed_count = len(occupied_list) - licensed_count
        
        # Get threshold info
        threshold = results.get('threshold_used', 0)
        
        stats_data = [
            ('Total Channels', results.get('total_channels', 0), ''),
            ('Channels Terisi', len(occupied_list), ''),
            ('Okupansi', results.get('occupancy_percentage', 0), '%'),
            ('Threshold', threshold, ' dB'),
            ('Noise Floor', results.get('noise_floor', 0), ' dB'),
            ('Berizin', licensed_count, ''),
            ('Tidak Berizin', unlicensed_count, ''),
            ('Avg Signal', band_channels['avg_field_strength'].mean(), ' dB'),
            ('Max Signal', band_channels['max_field_strength'].max(), ' dB'),
            ('Std Dev', band_channels['avg_field_strength'].std(), ' dB')
        ]
        
        fig = make_subplots(
            rows=5, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}]] * 5,
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        colors = ['#3182ce', '#38a169', '#d69e2e', '#48bb78', '#e53e3e', 
                 '#805ad5', '#dd6b20', '#319795', '#c53030', '#2c5282']
        
        for idx, (label, value, suffix) in enumerate(stats_data):
            row = idx // 2 + 1
            col = idx % 2 + 1
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=value,
                title={
                    "text": f"<b>{label}</b>",
                    "font": {"size": 13}
                },
                number={
                    "suffix": suffix,
                    "font": {"size": 28, "color": colors[idx]},
                    "valueformat": ".1f" if suffix else ".0f"
                }
            ), row=row, col=col)
        
        fig.update_layout(
            title=dict(
                text="<b>Statistik Analisis Spektrum</b>",
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            height=700,
            width=800,
            template="plotly_white",
            margin=dict(t=80, b=20, l=20, r=20)
        )
        
        fig.write_image(output_path)
        return output_path
    
    def create_frequency_occupancy_heatmap(self, channels_df: pd.DataFrame,
                                          band_info: Dict, threshold: float,
                                          output_path: str) -> str:
        """Create heatmap showing frequency occupancy over time/samples"""
        band_channels = channels_df[
            (channels_df['frequency'] >= band_info['start_freq']) &
            (channels_df['frequency'] <= band_info['stop_freq'])
        ].copy()
        
        band_channels['occupied'] = (band_channels['avg_field_strength'] > threshold).astype(int)
        
        freq_bins = 50
        freq_range = np.linspace(band_info['start_freq'], band_info['stop_freq'], freq_bins)
        
        occupancy_matrix = []
        for i in range(len(freq_range) - 1):
            mask = (band_channels['frequency'] >= freq_range[i]) & \
                   (band_channels['frequency'] < freq_range[i + 1])
            occupancy = band_channels[mask]['occupied'].mean() * 100 if mask.any() else 0
            occupancy_matrix.append(occupancy)
        
        occupancy_matrix = np.array(occupancy_matrix).reshape(-1, 1)
        occupancy_matrix = np.tile(occupancy_matrix, (1, 10))
        
        fig = go.Figure(data=go.Heatmap(
            z=occupancy_matrix.T,
            x=freq_range[:-1],
            y=list(range(10)),
            colorscale='RdYlGn_r',
            colorbar=dict(title="Okupansi %"),
            hovertemplate='Freq: %{x:.2f} MHz<br>Okupansi: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Peta Okupansi Frekuensi</b>",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="<b>Frekuensi (MHz)</b>",
            yaxis_title="<b>Sampling</b>",
            width=900,
            height=400,
            template="plotly_white"
        )
        
        fig.write_image(output_path)
        return output_path
    
    def create_top_signals_bar_chart(self, results: Dict, output_path: str) -> str:
        """Create horizontal bar chart of top signals"""
        top_signals = results.get('top_signals', [])[:15]
        
        if not top_signals:
            return None
        
        frequencies = [f"{s['frequency']:.3f}" for s in top_signals]
        avg_strengths = [s['avg_field_strength'] for s in top_signals]
        max_strengths = [s['max_field_strength'] for s in top_signals]
        colors_list = ['#3182ce' if s.get('station') else '#e53e3e' for s in top_signals]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=frequencies,
            x=avg_strengths,
            orientation='h',
            name='Avg Strength',
            marker=dict(color=colors_list),
            text=[f"{v:.1f}" for v in avg_strengths],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>15 Sinyal Terkuat</b><br><sub>Biru: Berizin | Merah: Tidak Berizin</sub>",
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="<b>Kuat Medan (dBµV/m)</b>",
            yaxis_title="<b>Frekuensi (MHz)</b>",
            width=800,
            height=600,
            template="plotly_white",
            showlegend=False,
            yaxis=dict(autorange="reversed")
        )
        
        fig.write_image(output_path)
        return output_path
