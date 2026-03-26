"""Health Monitor Page - System Self-Assessment.

Dedicated page for comprehensive health monitoring and diagnostics.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.health_monitor import health_monitor
from services.health_checks import register_all_checks
from components.health_dashboard import render_health_dashboard
from services.auth_service import require_auth

st.set_page_config(
    page_title="Health Monitor - NemoClaw Gateway",
    page_icon="🏥",
    layout="wide"
)

# Check authentication
user = require_auth()

st.title("🏥 System Health Monitor")
st.markdown("*Continuous self-assessment and operational integrity monitoring*")

st.divider()

# Info banner
st.info("""
**🔒 Security Notice:** This health monitoring system operates with least-privilege access, 
does not expose sensitive data, and includes tamper-resistant integrity validation. 
All assessments are cryptographically signed and audit-logged.
""")

# Auto-refresh option
auto_refresh = st.toggle("🔄 Auto-refresh (30s)", value=False, key="health_auto_refresh")

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Render main health dashboard
render_health_dashboard(user_permissions=user.role if user else None)

# Back button
st.divider()
if st.button("← Back to Main"):
    st.switch_page("app.py")
