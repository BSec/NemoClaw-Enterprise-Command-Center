"""Styling and UI utilities for NemoClaw Gateway Dashboard."""

import streamlit as st
from typing import Optional

def apply_theme(theme_config):
    """Apply custom CSS theme to Streamlit."""
    custom_css = f"""
    <style>
    /* Primary color */
    .stButton>button {{
        background-color: {theme_config.primary_color};
        color: white;
    }}
    
    /* Header styling */
    .main-header {{
        padding: 1rem;
        background-color: {theme_config.secondary_background};
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }}
    
    /* Status indicators */
    .status-online {{
        color: #00C851;
    }}
    .status-offline {{
        color: #ff4444;
    }}
    .status-warning {{
        color: #ffbb33;
    }}
    
    /* Card styling */
    .dashboard-card {{
        background-color: {theme_config.secondary_background};
        border-radius: 0.5rem;
        padding: 1rem;
        border-left: 4px solid {theme_config.primary_color};
    }}
    
    /* Metric cards */
    .metric-container {{
        background-color: {theme_config.secondary_background};
        border-radius: 0.5rem;
        padding: 1rem;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_header(instance_manager):
    """Render the dashboard header with system status."""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("### 🛡️ NemoClaw Gateway")
        
        with col2:
            # Quick health indicator
            instances = instance_manager.list_instances()
            if instances:
                online = sum(1 for i in instances if i.status.value == "online")
                total = len(instances)
                st.markdown(f"**Instances:** {online}/{total} 🟢")
            else:
                st.markdown("**Instances:** None ⚪")
        
        with col3:
            st.caption("v0.2.0 | Phase 1")

def render_status_badge(status: str) -> str:
    """Render a status badge with appropriate color."""
    status_icons = {
        "online": "🟢",
        "running": "🟢",
        "offline": "🔴",
        "stopped": "⚫",
        "error": "🔴",
        "degraded": "🟡",
        "warning": "🟡",
        "pending": "🟡",
        "unknown": "⚪",
    }
    return status_icons.get(status.lower(), "⚪")

def render_sandbox_card(sandbox: dict, on_start=None, on_stop=None, on_logs=None):
    """Render a sandbox status card."""
    status = sandbox.get('status', 'unknown')
    status_icon = render_status_badge(status)
    
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.subheader(f"{status_icon} {sandbox.get('name', 'Unnamed')}")
            st.caption(f"ID: {sandbox.get('id', 'unknown')}")
            agent_type = sandbox.get('agent_type', 'unknown')
            st.caption(f"Agent: {agent_type}")
        
        with col2:
            st.metric("Status", status.upper())
            created_at = sandbox.get('created_at')
            if created_at:
                st.caption(f"Created: {created_at}")
        
        with col3:
            # Action buttons
            if status == "running":
                if st.button("⏹️ Stop", key=f"stop_{sandbox.get('id')}", use_container_width=True):
                    if on_stop:
                        on_stop(sandbox.get('id'))
            elif status == "stopped":
                if st.button("▶️ Start", key=f"start_{sandbox.get('id')}", use_container_width=True):
                    if on_start:
                        on_start(sandbox.get('id'))
            
            if st.button("📄 Logs", key=f"logs_{sandbox.get('id')}", use_container_width=True):
                if on_logs:
                    on_logs(sandbox.get('id'))
        
        st.divider()

def format_bytes(bytes_val: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"
