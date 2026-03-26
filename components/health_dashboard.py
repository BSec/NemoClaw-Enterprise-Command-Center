"""Health Monitoring Dashboard Component.

Visual component for displaying health monitoring results.
"""

import streamlit as st
from typing import List, Dict, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from services.health_monitor import (
    HealthReport, HealthCheckResult, HealthStatus, SeverityLevel,
    AnomalyEvent, health_monitor
)
from services.health_checks import register_all_checks

def render_health_dashboard(
    user_permissions: Optional[List[str]] = None
):
    """
    Render health monitoring dashboard.
    
    Args:
        user_permissions: List of user's permissions for access control
    """
    st.header("🏥 System Health Monitor")
    st.caption("Self-assessment and operational integrity monitoring")
    
    # Run assessment
    try:
        report = health_monitor.run_assessment(user_permissions=user_permissions)
        anomalies = health_monitor.detect_anomalies(report)
    except Exception as e:
        st.error(f"❌ Health assessment failed: {e}")
        return
    
    # Overall status indicator
    status_config = {
        HealthStatus.HEALTHY: ("🟢", "#00C851", "All systems healthy"),
        HealthStatus.DEGRADED: ("🟡", "#ffbb33", "Some systems degraded"),
        HealthStatus.CRITICAL: ("🔴", "#ff4444", "Critical issues detected"),
        HealthStatus.UNKNOWN: ("⚪", "#grey", "Status unknown")
    }
    
    icon, color, message = status_config.get(report.overall_status, status_config[HealthStatus.UNKNOWN])
    
    # Top status banner
    st.divider()
    status_col1, status_col2, status_col3 = st.columns([1, 2, 1])
    
    with status_col1:
        st.markdown(f"<h1 style='text-align: center;'>{icon}</h1>", unsafe_allow_html=True)
    
    with status_col2:
        st.subheader(f"Status: {report.overall_status.value.upper()}")
        st.caption(message)
        st.caption(f"Report ID: {report.report_id}")
    
    with status_col3:
        st.caption(f"Generated: {report.generated_at.strftime('%H:%M:%S UTC')}")
        st.caption(f"Checks: {report.summary.get('total', 0)}")
    
    st.divider()
    
    # Summary metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        healthy = report.summary.get('healthy', 0)
        total = report.summary.get('total', 1)
        st.metric("Healthy", healthy, f"{healthy/total*100:.0f}%")
    
    with metric_col2:
        degraded = report.summary.get('degraded', 0)
        color = "inverse" if degraded > 0 else "normal"
        st.metric("Degraded", degraded, delta_color=color)
    
    with metric_col3:
        critical = report.summary.get('critical', 0)
        color = "inverse" if critical > 0 else "normal"
        st.metric("Critical", critical, delta_color=color)
    
    with metric_col4:
        unknown = report.summary.get('unknown', 0)
        st.metric("Unknown", unknown)
    
    st.divider()
    
    # Visual status breakdown
    _render_status_breakdown(report)
    
    # Anomalies section
    if anomalies:
        st.divider()
        st.error(f"🚨 {len(anomalies)} Anomaly(s) Detected")
        _render_anomalies(anomalies)
    
    # Detailed check results
    st.divider()
    st.subheader("Check Results")
    _render_check_details(report.checks)
    
    # Remediation suggestions
    st.divider()
    st.subheader("💡 Remediation Suggestions")
    suggestions = health_monitor.get_remediation_suggestions(report, max_risk_level="medium")
    
    if suggestions:
        for suggestion in suggestions:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.write(f"**{suggestion['check_id']}**")
                    st.caption(suggestion['issue'][:50])
                
                with col2:
                    st.write(suggestion['suggested_action'])
                
                with col3:
                    risk_color = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🔴'
                    }.get(suggestion['risk_level'], '⚪')
                    st.write(f"{risk_color} {suggestion['risk_level'].title()}")
                    if suggestion['requires_approval']:
                        st.caption("⚠️ Requires approval")
                
                st.divider()
    else:
        st.success("✅ No remediation required")
    
    # Export options
    st.divider()
    st.subheader("📤 Export Report")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📄 Copy JSON", use_container_width=True):
            json_report = health_monitor.export_report_json(report)
            st.code(json_report, language="json")
            st.success("JSON exported to clipboard!")
    
    with export_col2:
        if st.button("📝 Copy Text Summary", use_container_width=True):
            text_report = health_monitor.export_report_human(report)
            st.text(text_report)
            st.success("Text summary exported to clipboard!")
    
    # Re-run button
    st.divider()
    if st.button("🔄 Re-run Assessment", use_container_width=True):
        st.rerun()

def _render_status_breakdown(report: HealthReport):
    """Render visual status breakdown."""
    
    # Pie chart of status distribution
    labels = []
    values = []
    colors = []
    
    status_colors = {
        HealthStatus.HEALTHY: "#00C851",
        HealthStatus.DEGRADED: "#ffbb33",
        HealthStatus.CRITICAL: "#ff4444",
        HealthStatus.UNKNOWN: "#grey"
    }
    
    for status in HealthStatus:
        count = report.summary.get(status.value, 0)
        if count > 0:
            labels.append(status.value.title())
            values.append(count)
            colors.append(status_colors.get(status, "#grey"))
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Health Status Distribution",
        showlegend=False,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_anomalies(anomalies: List[AnomalyEvent]):
    """Render detected anomalies."""
    
    severity_icons = {
        SeverityLevel.CRITICAL: "🔴",
        SeverityLevel.HIGH: "🟠",
        SeverityLevel.MEDIUM: "🟡",
        SeverityLevel.LOW: "🟢",
        SeverityLevel.INFO: "🔵"
    }
    
    for anomaly in anomalies:
        icon = severity_icons.get(anomaly.severity, "⚪")
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"<h2 style='text-align: center;'>{icon}</h2>", unsafe_allow_html=True)
            
            with col2:
                st.write(f"**{anomaly.anomaly_type.replace('_', ' ').title()}**")
                st.write(anomaly.description)
                st.caption(f"Component: {anomaly.affected_component}")
                st.caption(f"Detected: {anomaly.timestamp.strftime('%H:%M:%S UTC')}")
                
                with st.expander("Details & Evidence"):
                    st.json(anomaly.evidence)
                
                st.info(f"💡 **Recommended Action:** {anomaly.recommended_action}")
            
            st.divider()

def _render_check_details(checks: List[HealthCheckResult]):
    """Render detailed check results."""
    
    status_icons = {
        HealthStatus.HEALTHY: ("✅", "#00C851"),
        HealthStatus.DEGRADED: ("⚠️", "#ffbb33"),
        HealthStatus.CRITICAL: ("❌", "#ff4444"),
        HealthStatus.UNKNOWN: ("❓", "#grey")
    }
    
    severity_icons = {
        SeverityLevel.CRITICAL: "🔴",
        SeverityLevel.HIGH: "🟠",
        SeverityLevel.MEDIUM: "🟡",
        SeverityLevel.LOW: "🟢",
        SeverityLevel.INFO: "🔵"
    }
    
    for check in checks:
        icon, color = status_icons.get(check.status, ("❓", "#grey"))
        severity_icon = severity_icons.get(check.severity, "⚪")
        
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"<h3 style='text-align: center;'>{icon}</h3>", unsafe_allow_html=True)
            
            with col2:
                st.write(f"**{check.check_id}** ({check.check_type.value.replace('_', ' ').title()})")
                st.write(check.message)
                st.caption(f"Duration: {check.duration_ms:.2f}ms | Time: {check.timestamp.strftime('%H:%M:%S')}")
                
                if check.details:
                    with st.expander("Details"):
                        st.json(check.details)
            
            with col3:
                st.write(f"{severity_icon} {check.severity.value.upper()}")
                if check.remediation_suggested:
                    st.caption("Action suggested")
            
            st.divider()

def render_mini_health_indicator():
    """Render a compact health status indicator for sidebar/header."""
    try:
        # Quick check without full assessment
        from services.health_checks import check_service_availability
        result = check_service_availability()
        
        status_colors = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.CRITICAL: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }
        
        icon = status_colors.get(result.status, "⚪")
        
        st.sidebar.markdown(f"---")
        st.sidebar.caption(f"{icon} System: {result.status.value.title()}")
        
        if st.sidebar.button("🔍 Health Details", use_container_width=True):
            st.session_state['show_health_dashboard'] = True
            st.rerun()
        
    except Exception:
        st.sidebar.caption("⚪ System: Unknown")
