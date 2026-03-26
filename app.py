"""NemoClaw Gateway Dashboard - Main Application

Phase 4: Enterprise Scale & Multi-User (Complete)
A Streamlit-based dashboard for managing NemoClaw/OpenShell environments.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config import load_config
from utils.styling import apply_theme, render_header
from services.instance_manager import InstanceManager
from services.auth_service import auth_manager, require_auth, render_user_menu

# Page configuration
st.set_page_config(
    page_title="NemoClaw Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize configuration
config = load_config()

# Apply custom theme
apply_theme(config.theme)

# Check authentication
user = require_auth()

# Render user menu
render_user_menu()

# Render mini health indicator
from components.health_dashboard import render_mini_health_indicator
render_mini_health_indicator()
@st.cache_resource
def get_instance_manager():
    return InstanceManager()

instance_manager = get_instance_manager()

# Render header with system status
render_header(instance_manager)

# Main content
st.title("🛡️ NemoClaw Gateway Dashboard")
st.markdown("*Safe-by-Default AI Control Plane*")

# Quick stats row
st.divider()
col1, col2, col3, col4 = st.columns(4)

with col1:
    instances = instance_manager.list_instances()
    online_count = sum(1 for i in instances if i.status.value == "online")
    st.metric("Instances", len(instances), f"{online_count} online")

with col2:
    # Total sandboxes across all instances
    total_sandboxes = 0
    for instance in instances:
        if instance.status.value == "online":
            try:
                result = instance_manager.execute_on_instance(instance.id, "list", "sandboxes")
                if isinstance(result, dict) and "sandboxes" in result:
                    total_sandboxes += len(result["sandboxes"])
            except:
                pass
    st.metric("Sandboxes", total_sandboxes)

with col3:
    # Pending requests (placeholder)
    st.metric("Pending Requests", 0, delta="0 new")

with col4:
    # System health (placeholder)
    st.metric("System Health", "🟢 Good")

st.divider()

# Instance selector
st.subheader("📍 Select Instance")
instances = instance_manager.list_instances()

if not instances:
    st.warning("No instances configured. Please add an instance to get started.")
    
    with st.expander("➕ Add Local Instance"):
        st.markdown("""
        ### Quick Setup
        
        Add your local NemoClaw installation:
        
        ```yaml
        # ~/.nemoclaw/instances.yaml
        instances:
          - id: local
            name: "Local Workstation"
            type: local
            environment: default
            connection:
              path: /usr/local/bin/openshell
            default: true
        ```
        """)
        
        if st.button("Create Default Config"):
            from services.instance_manager import create_default_config
            create_default_config()
            st.success("Created default configuration. Please refresh the page.")
            st.rerun()

else:
    instance_options = {f"{i.name} ({i.status.value})": i.id for i in instances}
    
    selected_label = st.selectbox(
        "Select NemoClaw Instance",
        options=list(instance_options.keys()),
        index=0,
        help="Choose which NemoClaw installation to manage"
    )
    
    selected_instance_id = instance_options[selected_label]
    selected_instance = instance_manager.get_instance(selected_instance_id)
    
    # Store in session state
    st.session_state.selected_instance = selected_instance_id
    
    # Show instance details
    with st.expander("Instance Details"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Name:** {selected_instance.name}")
            st.write(f"**Type:** {selected_instance.type.value}")
        with col2:
            st.write(f"**Environment:** {selected_instance.environment}")
            st.write(f"**Status:** {selected_instance.status.value}")
        with col3:
            if selected_instance.last_seen:
                st.write(f"**Last Seen:** {selected_instance.last_seen.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.write("**Last Seen:** Never")
    
    # Navigation to views
    st.divider()
    st.subheader("🔧 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🖥️ Engineer View", use_container_width=True):
            st.switch_page("pages/01_Engineer_View.py")
    
    with col2:
        if st.button("🛡️ SecOps View", use_container_width=True):
            st.switch_page("pages/02_SecOps_View.py")
    
    with col3:
        if st.button("📊 CISO View", use_container_width=True):
            st.switch_page("pages/03_CISO_View.py")
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/04_Settings.py")
    
    col5, col6 = st.columns(2)
    with col5:
        if st.button("🏥 Health Monitor", use_container_width=True):
            st.switch_page("pages/05_Health_Monitor.py")
    
    # Instance health check
    if selected_instance.status.value != "online":
        st.warning(f"⚠️ Instance '{selected_instance.name}' is not online. Check the connection settings.")
        
        if st.button("🔄 Check Health"):
            with st.spinner("Checking instance health..."):
                status = instance_manager.check_health(selected_instance_id)
                if status.value == "online":
                    st.success("Instance is now online!")
                else:
                    st.error(f"Instance is {status.value}. Please verify the connection.")
                st.rerun()

# Footer
st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    st.caption("NemoClaw Gateway Dashboard v2.1.0 | All Phases Complete")
with col2:
    if user:
        st.caption(f"👤 Logged in as: {user.name} ({user.role.value})")
