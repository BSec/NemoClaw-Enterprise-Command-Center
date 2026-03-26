"""Settings page for dashboard configuration."""

import streamlit as st
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import load_config, save_config, DashboardConfig, ThemeConfig
from services.instance_manager import InstanceManager, create_default_config

st.set_page_config(
    page_title="Settings - NemoClaw Gateway",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Settings")

# Initialize config
config = load_config()

# Create tabs for different settings categories
tab1, tab2, tab3 = st.tabs(["🎨 Appearance", "🔧 Instance Management", "📊 System"])

with tab1:
    st.header("Appearance Settings")
    
    # Theme settings
    st.subheader("Theme")
    
    primary_color = st.color_picker(
        "Primary Color",
        value=config.theme.primary_color,
        key="primary_color"
    )
    
    refresh_interval = st.slider(
        "Auto-refresh Interval (seconds)",
        min_value=1,
        max_value=60,
        value=config.refresh_interval,
        key="refresh_interval"
    )
    
    if st.button("💾 Save Appearance Settings"):
        config.theme.primary_color = primary_color
        config.refresh_interval = refresh_interval
        save_config(config)
        st.success("Settings saved!")
        st.rerun()

with tab2:
    st.header("Instance Management")
    
    instance_manager = InstanceManager()
    instances = instance_manager.list_instances()
    
    st.subheader("Configured Instances")
    
    if not instances:
        st.warning("No instances configured.")
        
        if st.button("➕ Create Default Local Instance"):
            create_default_config()
            st.success("Created default configuration!")
            st.rerun()
    else:
        for instance in instances:
            with st.expander(f"{instance.name} ({instance.type.value})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** {instance.id}")
                    st.write(f"**Type:** {instance.type.value}")
                    st.write(f"**Environment:** {instance.environment}")
                    st.write(f"**Status:** {instance.status.value}")
                    st.write(f"**Connection:**")
                    st.json(instance.connection_config)
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{instance.id}"):
                        instance_manager.remove_instance(instance.id)
                        st.success(f"Removed {instance.name}")
                        st.rerun()
                    
                    if st.button("🔄 Check Health", key=f"health_{instance.id}"):
                        status = instance_manager.check_health(instance.id)
                        st.info(f"Status: {status.value}")
                        st.rerun()
        
        # Add new instance section
        st.divider()
        st.subheader("Add New Instance")
        
        with st.expander("➕ Add Instance"):
            new_id = st.text_input("Instance ID", value="new-instance", key="new_id")
            new_name = st.text_input("Instance Name", value="New Instance", key="new_name")
            new_type = st.selectbox(
                "Instance Type",
                options=["local", "ssh", "api"],
                key="new_type"
            )
            new_env = st.text_input("Environment", value="default", key="new_env")
            
            if new_type == "local":
                new_path = st.text_input("OpenShell Path", value="openshell", key="new_path")
                connection_config = {"path": new_path}
            elif new_type == "ssh":
                st.info("SSH configuration - implementation pending")
                connection_config = {}
            else:  # api
                st.info("API configuration - implementation pending")
                connection_config = {}
            
            if st.button("Add Instance"):
                from services.instance_manager import NemoClawInstance, InstanceType, InstanceStatus
                new_instance = NemoClawInstance(
                    id=new_id,
                    name=new_name,
                    type=InstanceType(new_type),
                    environment=new_env,
                    connection_config=connection_config,
                    status=InstanceStatus.UNKNOWN
                )
                instance_manager.add_instance(new_instance)
                st.success(f"Added instance: {new_name}")
                st.rerun()

with tab3:
    st.header("System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dashboard Info")
        st.write(f"**Version:** {config.version}")
        st.write(f"**Mode:** {config.mode}")
        st.write(f"**Config Path:** ~/.nemoclaw/config.yaml")
        st.write(f"**Instances Path:** ~/.nemoclaw/instances.yaml")
    
    with col2:
        st.subheader("Python Environment")
        import platform
        import sys
        st.write(f"**Python Version:** {sys.version.split()[0]}")
        st.write(f"**Platform:** {platform.platform()}")
        st.write(f"**Working Directory:** {Path.cwd()}")
    
    # Export/Import section
    st.divider()
    st.subheader("Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Configuration"):
            import json
            import yaml
            
            export_data = {
                'config': {
                    'version': config.version,
                    'mode': config.mode,
                    'refresh_interval': config.refresh_interval,
                    'theme': {
                        'primary_color': config.theme.primary_color
                    }
                },
                'instances': [
                    {
                        'id': i.id,
                        'name': i.name,
                        'type': i.type.value,
                        'environment': i.environment,
                        'connection': i.connection_config
                    }
                    for i in instances
                ]
            }
            
            export_json = json.dumps(export_data, indent=2)
            st.download_button(
                "Download Config JSON",
                data=export_json,
                file_name="nemoclaw-config.json",
                mime="application/json"
            )

# Back button
st.divider()
if st.button("← Back to Main"):
    st.switch_page("app.py")
