"""Resource usage mini-charts for sandbox monitoring.

Provides compact visualization of CPU, memory, disk, and network usage.
Uses Plotly for interactive charts.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

@dataclass
class ResourceMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_used: float  # MB
    memory_total: float  # MB
    disk_used: float  # GB
    disk_total: float  # GB
    network_rx: float  # KB/s
    network_tx: float  # KB/s

class ResourceHistory:
    """Keep history of resource metrics for charting."""
    
    def __init__(self, max_points: int = 60):
        self.max_points = max_points
        self.history: List[ResourceMetrics] = []
    
    def add(self, metrics: ResourceMetrics):
        """Add new metrics point."""
        self.history.append(metrics)
        # Keep only last N points
        if len(self.history) > self.max_points:
            self.history = self.history[-self.max_points:]
    
    def get_data(self) -> Dict[str, List]:
        """Get chart data as dictionary of lists."""
        return {
            'timestamps': [m.timestamp for m in self.history],
            'cpu': [m.cpu_percent for m in self.history],
            'memory': [(m.memory_used / m.memory_total * 100) if m.memory_total > 0 else 0 for m in self.history],
            'memory_used': [m.memory_used for m in self.history],
            'disk': [(m.disk_used / m.disk_total * 100) if m.disk_total > 0 else 0 for m in self.history],
            'network_rx': [m.network_rx for m in self.history],
            'network_tx': [m.network_tx for m in self.history],
        }

def get_system_metrics() -> ResourceMetrics:
    """Get current system resource metrics."""
    import psutil
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Memory
    memory = psutil.virtual_memory()
    memory_used = (memory.total - memory.available) / 1024 / 1024  # MB
    memory_total = memory.total / 1024 / 1024  # MB
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_used = disk.used / 1024 / 1024 / 1024  # GB
    disk_total = disk.total / 1024 / 1024 / 1024  # GB
    
    # Network (since last call)
    net_io = psutil.net_io_counters()
    network_rx = net_io.bytes_recv / 1024  # KB (cumulative, would need delta calculation for real rate)
    network_tx = net_io.bytes_sent / 1024  # KB
    
    return ResourceMetrics(
        timestamp=datetime.now(),
        cpu_percent=cpu_percent,
        memory_used=memory_used,
        memory_total=memory_total,
        disk_used=disk_used,
        disk_total=disk_total,
        network_rx=network_rx,
        network_tx=network_tx
    )

def render_resource_mini_charts(
    sandbox_id: Optional[str] = None,
    auto_refresh: bool = True,
    refresh_interval: float = 5.0
):
    """Render compact resource usage charts."""
    
    # Initialize history
    history_key = f"resource_history_{sandbox_id or 'system'}"
    if history_key not in st.session_state:
        st.session_state[history_key] = ResourceHistory(max_points=60)
    
    history = st.session_state[history_key]
    
    # Get current metrics
    metrics = get_system_metrics()
    history.add(metrics)
    
    # Header
    st.subheader("📊 Resource Usage")
    
    # Auto-refresh
    if auto_refresh:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏸️ Pause", key=f"pause_res_{sandbox_id}"):
                st.session_state[f"pause_res_{sandbox_id}"] = True
                st.rerun()
        time.sleep(refresh_interval)
        st.rerun()
    
    # Current metrics summary
    data = history.get_data()
    
    # Create 2x2 subplot grid
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CPU Usage %', 'Memory Usage %', 'Disk Usage %', 'Network I/O (KB)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # CPU Chart
    if data['cpu']:
        fig.add_trace(
            go.Scatter(
                x=data['timestamps'],
                y=data['cpu'],
                mode='lines',
                name='CPU %',
                line=dict(color='#76B900', width=2),
                fill='tozeroy',
                fillcolor='rgba(118, 185, 0, 0.2)'
            ),
            row=1, col=1
        )
    
    # Memory Chart
    if data['memory']:
        fig.add_trace(
            go.Scatter(
                x=data['timestamps'],
                y=data['memory'],
                mode='lines',
                name='Memory %',
                line=dict(color='#00C851', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 200, 81, 0.2)'
            ),
            row=1, col=2
        )
    
    # Disk Chart
    if data['disk']:
        fig.add_trace(
            go.Scatter(
                x=data['timestamps'],
                y=data['disk'],
                mode='lines',
                name='Disk %',
                line=dict(color='#ffbb33', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 187, 51, 0.2)'
            ),
            row=2, col=1
        )
    
    # Network Chart (dual line)
    if data['network_rx']:
        fig.add_trace(
            go.Scatter(
                x=data['timestamps'],
                y=data['network_rx'],
                mode='lines',
                name='RX',
                line=dict(color='#33b5e5', width=2)
            ),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(
                x=data['timestamps'],
                y=data['network_tx'],
                mode='lines',
                name='TX',
                line=dict(color='#ff4444', width=2)
            ),
            row=2, col=2
        )
    
    # Layout settings
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=60, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    # Set y-axis ranges
    fig.update_yaxes(range=[0, 100], row=1, col=1)
    fig.update_yaxes(range=[0, 100], row=1, col=2)
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_cpu = data['cpu'][-1] if data['cpu'] else 0
        delta_color = "inverse" if current_cpu > 80 else "normal"
        st.metric("CPU", f"{current_cpu:.1f}%", delta_color=delta_color)
    
    with col2:
        current_mem = data['memory'][-1] if data['memory'] else 0
        mem_used = data['memory_used'][-1] if data['memory_used'] else 0
        delta_color = "inverse" if current_mem > 80 else "normal"
        st.metric("Memory", f"{mem_used:.0f} MB", f"{current_mem:.1f}%", delta_color=delta_color)
    
    with col3:
        current_disk = data['disk'][-1] if data['disk'] else 0
        delta_color = "inverse" if current_disk > 90 else "normal"
        st.metric("Disk", f"{current_disk:.1f}%", delta_color=delta_color)
    
    with col4:
        rx = data['network_rx'][-1] / 1024 if data['network_rx'] else 0  # Convert to MB
        st.metric("Network RX", f"{rx:.1f} MB", "Cumulative")

def render_compact_resource_card():
    """Render a compact resource summary card (for sidebar or small spaces)."""
    import psutil
    
    # Get metrics
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Create mini gauges
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CPU mini gauge
        cpu_color = "#76B900" if cpu < 50 else "#ffbb33" if cpu < 80 else "#ff4444"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cpu,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': cpu_color},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(118, 185, 0, 0.2)'},
                    {'range': [50, 80], 'color': 'rgba(255, 187, 51, 0.2)'},
                    {'range': [80, 100], 'color': 'rgba(255, 68, 68, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # Memory mini gauge
        mem_pct = memory.percent
        mem_color = "#76B900" if mem_pct < 60 else "#ffbb33" if mem_pct < 85 else "#ff4444"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=mem_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Memory", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': mem_color},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(118, 185, 0, 0.2)'},
                    {'range': [60, 85], 'color': 'rgba(255, 187, 51, 0.2)'},
                    {'range': [85, 100], 'color': 'rgba(255, 68, 68, 0.2)'}
                ]
            }
        ))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        # Disk mini gauge
        disk_pct = disk.percent
        disk_color = "#76B900" if disk_pct < 70 else "#ffbb33" if disk_pct < 90 else "#ff4444"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=disk_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Disk", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': disk_color},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 70], 'color': 'rgba(118, 185, 0, 0.2)'},
                    {'range': [70, 90], 'color': 'rgba(255, 187, 51, 0.2)'},
                    {'range': [90, 100], 'color': 'rgba(255, 68, 68, 0.2)'}
                ]
            }
        ))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
