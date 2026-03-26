"""Engineer View - Sandbox Management and GPU Monitoring

Phase 1: Foundation & Engineer View (MVP)
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.instance_manager import InstanceManager
from services.openshell import OpenShellService, OpenShellError
from services.gpu_monitor import GpuMonitor
from utils.styling import render_sandbox_card, render_status_badge, format_bytes
from components.sandbox_form import render_sandbox_creation_wizard, render_quick_sandbox_form
from components.file_browser import render_workspace_browser_card
from components.log_streamer import render_log_streamer, render_log_viewer_simple
from components.resource_charts import render_resource_mini_charts, render_compact_resource_card
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Engineer View - NemoClaw Gateway",
    page_icon="🔧",
    layout="wide"
)

st.title("👨‍💻 Engineer View")
st.caption("Manage sandboxes, monitor resources, debug agents")

# Initialize services
@st.cache_resource
def get_services():
    instance_manager = InstanceManager()
    return instance_manager

instance_manager = get_services()

# Get selected instance
selected_instance_id = st.session_state.get('selected_instance')
if not selected_instance_id:
    st.warning("⚠️ No instance selected. Please select an instance from the main page.")
    if st.button("← Back to Main"):
        st.switch_page("app.py")
    st.stop()

selected_instance = instance_manager.get_instance(selected_instance_id)
if not selected_instance:
    st.error("Selected instance not found.")
    st.stop()

# Initialize OpenShell service
openshell = OpenShellService(instance_manager, selected_instance_id)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🖥️ Sandboxes", "🎮 GPU Metrics", "📜 Logs", "📊 Resources"])

with tab1:
    st.header("Sandbox Management")
    
    # Sandbox creation section
    with st.expander("➕ Create New Sandbox", expanded=False):
        # Use quick form or full wizard
        form_mode = st.radio(
            "Form Mode",
            options=["Quick Create", "Advanced Wizard"],
            horizontal=True,
            key="form_mode"
        )
        
        if form_mode == "Quick Create":
            render_quick_sandbox_form(openshell, on_create=lambda name: st.rerun())
        else:
            render_sandbox_creation_wizard(openshell, on_create=lambda name: st.rerun())
    
    # Refresh button
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    # Load sandboxes
    with st.spinner("Loading sandboxes..."):
        sandboxes = openshell.list_sandboxes()
    
    if not sandboxes:
        st.info("No sandboxes found. Create one to get started.")
    else:
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            status_filter = st.multiselect(
                "Filter by status",
                options=["running", "stopped", "error", "pending"],
                default=["running", "stopped", "error"],
                key="sandbox_filter"
            )
        with col2:
            st.metric("Total", len(sandboxes))
        
        # Filter sandboxes
        filtered = [s for s in sandboxes if s.status in status_filter]
        
        # Render sandbox cards
        for sandbox in filtered:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    status_icon = render_status_badge(sandbox.status)
                    st.subheader(f"{status_icon} {sandbox.name}")
                    st.caption(f"ID: `{sandbox.id}`")
                    st.caption(f"Agent: {sandbox.agent_type}")
                    if sandbox.workspace_path:
                        st.caption(f"Workspace: `{sandbox.workspace_path}`")
                
                with col2:
                    st.metric("Status", sandbox.status.upper())
                    if sandbox.created_at:
                        st.caption(f"Created: {sandbox.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                with col3:
                    # Action buttons
                    if sandbox.status == "running":
                        if st.button("⏹️ Stop", key=f"stop_{sandbox.id}", use_container_width=True):
                            with st.spinner("Stopping sandbox..."):
                                if openshell.stop_sandbox(sandbox.id):
                                    st.success("Sandbox stopped!")
                                    st.rerun()
                                else:
                                    st.error("Failed to stop sandbox")
                    elif sandbox.status == "stopped":
                        if st.button("▶️ Start", key=f"start_{sandbox.id}", use_container_width=True):
                            with st.spinner("Starting sandbox..."):
                                if openshell.start_sandbox(sandbox.id):
                                    st.success("Sandbox started!")
                                    st.rerun()
                                else:
                                    st.error("Failed to start sandbox")
                    
                    # Restart button (shown for all states)
                    if st.button("🔄 Restart", key=f"restart_{sandbox.id}", use_container_width=True):
                        with st.spinner("Restarting sandbox..."):
                            # Stop first if running
                            if sandbox.status == "running":
                                openshell.stop_sandbox(sandbox.id)
                            # Then start
                            if openshell.start_sandbox(sandbox.id):
                                st.success("Sandbox restarted!")
                                st.rerun()
                            else:
                                st.error("Failed to restart sandbox")
                    
                    # View details button
                    if st.button("📄 Details", key=f"details_{sandbox.id}", use_container_width=True):
                        st.session_state.selected_sandbox = sandbox.id
                
                # Workspace file browser
                if sandbox.workspace_path:
                    render_workspace_browser_card(sandbox.id, sandbox.workspace_path)
                
                st.divider()

with tab2:
    st.header("🎮 GPU Telemetry")
    
    # Initialize GPU monitor
    gpu_monitor = GpuMonitor(instance_manager, selected_instance_id)
    
    if not gpu_monitor.is_available():
        st.warning("⚠️ GPU monitoring not available. NVIDIA drivers may not be installed.")
    else:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True, key="gpu_auto_refresh")
        
        if auto_refresh:
            import time
            time.sleep(5)
            st.rerun()
        
        # Get GPU metrics
        with st.spinner("Loading GPU metrics..."):
            metrics = gpu_monitor.get_metrics()
        
        if not metrics:
            st.info("No GPUs detected on this instance.")
        else:
            # GPU summary
            col1, col2, col3 = st.columns(3)
            with col1:
                total_gpus = len(metrics)
                st.metric("GPUs", total_gpus)
            with col2:
                avg_util = sum(m.utilization for m in metrics) / len(metrics) if metrics else 0
                st.metric("Avg Utilization", f"{avg_util:.1f}%")
            with col3:
                high_temp = any(m.temperature > 80 for m in metrics)
                st.metric("Temperature Alert", "🔴 Yes" if high_temp else "🟢 No")
            
            st.divider()
            
            # Per-GPU metrics
            for gpu in metrics:
                with st.container():
                    st.subheader(f"GPU {gpu.index}: {gpu.name}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Utilization gauge
                    with col1:
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=gpu.utilization,
                            title={"text": "Utilization %"},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "#76B900" if gpu.utilization < 80 else "#ff4444"},
                                "steps": [
                                    {"range": [0, 50], "color": "lightgray"},
                                    {"range": [50, 80], "color": "yellow"},
                                    {"range": [80, 100], "color": "red"}
                                ]
                            }
                        ))
                        fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
                        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{gpu.index}")
                    
                    with col2:
                        memory_pct = (gpu.memory_used / gpu.memory_total) * 100 if gpu.memory_total > 0 else 0
                        st.metric("Memory", f"{gpu.memory_used:.0f} MB")
                        st.progress(memory_pct / 100, text=f"{memory_pct:.1f}%")
                    
                    with col3:
                        temp_color = "normal" if gpu.temperature < 80 else "inverse"
                        st.metric("Temperature", f"{gpu.temperature:.0f}°C", delta_color=temp_color)
                    
                    with col4:
                        if gpu.power_draw and gpu.power_limit:
                            power_pct = (gpu.power_draw / gpu.power_limit) * 100
                            st.metric("Power", f"{gpu.power_draw:.1f}W")
                            st.progress(power_pct / 100, text=f"{power_pct:.1f}%")
                        else:
                            st.metric("Power", "N/A")
                    
                    st.divider()

with tab3:
    st.header("📜 System Logs")
    
    # Sandbox selector for logs
    if sandboxes:
        sandbox_options = {s.name: s.id for s in sandboxes}
        selected_sandbox_name = st.selectbox(
            "Select Sandbox",
            options=list(sandbox_options.keys()),
            key="log_sandbox_select"
        )
        selected_sandbox_id = sandbox_options[selected_sandbox_name]
        
        # Log mode selector
        log_mode = st.radio(
            "View Mode",
            options=["Real-time Stream", "Static View"],
            horizontal=True,
            key="log_mode"
        )
        
        if log_mode == "Real-time Stream":
            # Use the streaming component
            render_log_streamer(
                openshell,
                selected_sandbox_id,
                auto_refresh=True,
                refresh_interval=1.0,
                max_lines=500
            )
        else:
            # Static view with simple log viewer
            render_log_viewer_simple(openshell, selected_sandbox_id, lines=100)
    else:
        st.info("No sandboxes available to view logs.")

with tab4:
    st.header("📊 System Resources")
    
    # Render resource mini-charts
    render_resource_mini_charts(
        sandbox_id=selected_instance_id,
        auto_refresh=True,
        refresh_interval=5.0
    )
    
    # Compact resource cards
    st.divider()
    st.subheader("Current System Status")
    render_compact_resource_card()

# Back button
st.divider()
if st.button("← Back to Main"):
    st.switch_page("app.py")
