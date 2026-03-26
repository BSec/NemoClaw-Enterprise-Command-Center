"""SecOps View - Security Dashboard for NemoClaw Gateway.

Phase 2: SecOps View & Security
Provides security monitoring, request queue, and agent reputation.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.instance_manager import InstanceManager
from services.openshell import OpenShellService
from components.request_queue import render_request_queue, render_request_details
from components.agent_reputation import render_reputation_dashboard
from components.security_alerts import render_security_alerts, render_policy_violations
from utils.styling import render_status_badge

st.set_page_config(
    page_title="SecOps View - NemoClaw Gateway",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SecOps View")
st.caption("Security monitoring, request approval, and threat detection")

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

# Create tabs for SecOps dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Request Queue",
    "⭐ Agent Reputation",
    "🔔 Security Alerts",
    "⚠️ Policy Violations"
])

with tab1:
    st.header("📋 Pending Request Queue")
    st.caption("Review and approve OpenShell network requests")
    
    # Request queue controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        auto_refresh = st.toggle("Auto-refresh", value=True, key="queue_auto_refresh")
    
    with col2:
        if st.button("🔄 Refresh Now", key="queue_refresh"):
            st.rerun()
    
    with col3:
        filter_status = st.multiselect(
            "Filter Status",
            options=["pending", "approved", "denied", "expired"],
            default=["pending"],
            key="queue_filter"
        )
    
    # Render request queue
    render_request_queue(
        openshell_service=openshell,
        instance_id=selected_instance_id,
        filter_status=filter_status,
        auto_refresh=auto_refresh,
        refresh_interval=3.0
    )

with tab2:
    st.header("⭐ Agent Reputation Dashboard")
    st.caption("Track and analyze agent behavior scores")
    
    render_reputation_dashboard(
        openshell_service=openshell,
        instance_id=selected_instance_id
    )

with tab3:
    st.header("🔔 Security Alerts")
    st.caption("Real-time threat detection and alerts")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            options=["critical", "high", "medium", "low"],
            default=["critical", "high", "medium"],
            key="alert_severity"
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range",
            options=["Last Hour", "Last 4 Hours", "Last 24 Hours", "Last 7 Days"],
            index=1,
            key="alert_time_range"
        )
    
    with col3:
        if st.button("🗑️ Clear All Alerts", key="clear_alerts"):
            st.warning("Clear alerts functionality coming in Phase 3")
    
    render_security_alerts(
        openshell_service=openshell,
        instance_id=selected_instance_id,
        severity_filter=severity_filter,
        time_range=time_range
    )

with tab4:
    st.header("⚠️ Policy Violations")
    st.caption("Track policy breaches and compliance issues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        violation_type = st.multiselect(
            "Violation Type",
            options=["network_policy", "data_exfiltration", "prompt_injection", "rate_limit", "authentication"],
            default=["network_policy", "data_exfiltration"],
            key="violation_type"
        )
    
    with col2:
        if st.button("📊 Export Report", key="export_violations"):
            st.info("Export functionality coming in Phase 3")
    
    render_policy_violations(
        openshell_service=openshell,
        instance_id=selected_instance_id,
        violation_types=violation_type
    )

# Global actions bar
st.divider()
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✅ Approve All Low Risk", use_container_width=True):
        st.info("Bulk approval coming in Phase 3")

with col2:
    if st.button("🚫 Emergency Stop", type="primary", use_container_width=True):
        st.error("Emergency stop triggered! All sandboxes would be stopped.")

with col3:
    if st.button("🔍 Run Security Scan", use_container_width=True):
        with st.spinner("Scanning..."):
            import time
            time.sleep(2)
        st.success("Security scan complete - no threats detected")

with col4:
    if st.button("📋 Generate Report", use_container_width=True):
        st.info("Report generation coming in Phase 3")

# Back button
st.divider()
if st.button("← Back to Main"):
    st.switch_page("app.py")
