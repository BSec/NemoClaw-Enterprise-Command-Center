"""CISO View - Executive Dashboard for NemoClaw Gateway.

Phase 3: CISO View & Compliance
Provides executive-level security posture, compliance tracking, and governance.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.instance_manager import InstanceManager
from services.openshell import OpenShellService
from components.compliance_overview import render_compliance_dashboard
from components.security_scorecard import render_security_scorecard
from components.audit_trail import render_audit_trail
from components.policy_management import render_policy_management
from components.executive_summary import render_executive_summary

st.set_page_config(
    page_title="CISO View - NemoClaw Gateway",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CISO View")
st.caption("Executive dashboard for security posture, compliance, and governance")

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

# Executive summary at top
render_executive_summary(
    openshell_service=openshell,
    instance_id=selected_instance_id
)

st.divider()

# Create tabs for CISO dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "🔒 Security Scorecard",
    "📋 Compliance Overview",
    "📝 Audit Trail",
    "⚖️ Policy Management"
])

with tab1:
    st.header("🔒 Security Posture Scorecard")
    st.caption("Overall security metrics and risk assessment")
    
    render_security_scorecard(
        openshell_service=openshell,
        instance_id=selected_instance_id
    )

with tab2:
    st.header("📋 Compliance Status")
    st.caption("Regulatory compliance tracking (SOC2, GDPR, HIPAA, etc.)")
    
    render_compliance_dashboard(
        openshell_service=openshell,
        instance_id=selected_instance_id
    )

with tab3:
    st.header("📝 Audit Trail")
    st.caption("Comprehensive activity logging and forensics")
    
    render_audit_trail(
        openshell_service=openshell,
        instance_id=selected_instance_id
    )

with tab4:
    st.header("⚖️ Policy Management")
    st.caption("Configure and manage security policies")
    
    render_policy_management(
        openshell_service=openshell,
        instance_id=selected_instance_id
    )

# Back button
st.divider()
if st.button("← Back to Main"):
    st.switch_page("app.py")
