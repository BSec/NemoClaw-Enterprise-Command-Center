"""Security Alerts and Policy Violations components for SecOps Dashboard.

Provides real-time threat detection alerts and policy violation tracking.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AlertType(Enum):
    """Types of security alerts."""
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_VIOLATION = "rate_limit"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    POLICY_VIOLATION = "policy_violation"
    ANOMALY_DETECTED = "anomaly"

class ViolationType(Enum):
    """Types of policy violations."""
    NETWORK_POLICY = "network_policy"
    DATA_EXFILTRATION = "data_exfiltration"
    PROMPT_INJECTION = "prompt_injection"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    RESOURCE_LIMIT = "resource_limit"

@dataclass
class SecurityAlert:
    id: str
    timestamp: datetime
    severity: AlertSeverity
    alert_type: AlertType
    sandbox_id: str
    sandbox_name: str
    title: str
    description: str
    details: Dict[str, any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class PolicyViolation:
    id: str
    timestamp: datetime
    violation_type: ViolationType
    sandbox_id: str
    sandbox_name: str
    policy_name: str
    description: str
    severity: AlertSeverity
    action_taken: str
    details: Dict[str, any]

# Severity styling
SEVERITY_STYLES = {
    AlertSeverity.CRITICAL: ("🔴", "#ff4444", "Critical"),
    AlertSeverity.HIGH: ("🟠", "#ff8800", "High"),
    AlertSeverity.MEDIUM: ("🟡", "#ffbb33", "Medium"),
    AlertSeverity.LOW: ("🔵", "#33b5e5", "Low")
}

ALERT_TYPE_ICONS = {
    AlertType.PROMPT_INJECTION: "💉",
    AlertType.DATA_EXFILTRATION: "📤",
    AlertType.UNAUTHORIZED_ACCESS: "🚫",
    AlertType.RATE_LIMIT_VIOLATION: "⏱️",
    AlertType.SUSPICIOUS_PATTERN: "🔍",
    AlertType.POLICY_VIOLATION: "⚠️",
    AlertType.ANOMALY_DETECTED: "👁️"
}

VIOLATION_TYPE_NAMES = {
    ViolationType.NETWORK_POLICY: "Network Policy",
    ViolationType.DATA_EXFILTRATION: "Data Exfiltration",
    ViolationType.PROMPT_INJECTION: "Prompt Injection",
    ViolationType.RATE_LIMIT: "Rate Limit",
    ViolationType.AUTHENTICATION: "Authentication",
    ViolationType.RESOURCE_LIMIT: "Resource Limit"
}

def render_security_alerts(
    openshell_service,
    instance_id: str,
    severity_filter: Optional[List[str]] = None,
    time_range: str = "Last 4 Hours"
):
    """Render security alerts component."""
    
    # Fetch alerts
    alerts = _fetch_security_alerts(openshell_service, time_range)
    
    # Apply severity filter
    if severity_filter:
        severity_filter = [s.lower() for s in severity_filter]
        alerts = [a for a in alerts if a.severity.value in severity_filter]
    
    # Summary metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    critical_count = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL and not a.acknowledged)
    unacknowledged = sum(1 for a in alerts if not a.acknowledged)
    total_alerts = len(alerts)
    resolved_count = sum(1 for a in alerts if a.resolved)
    
    with col1:
        delta_color = "inverse" if critical_count > 0 else "normal"
        st.metric("Critical", critical_count, delta_color=delta_color)
    with col2:
        st.metric("Unacknowledged", unacknowledged)
    with col3:
        st.metric("Total Alerts", total_alerts)
    with col4:
        st.metric("Resolved", resolved_count)
    
    st.divider()
    
    # Alert timeline chart
    if alerts:
        _render_alert_timeline(alerts)
    
    # Alert list
    st.divider()
    st.subheader("Alert Feed")
    
    if not alerts:
        st.success("✅ No alerts in selected time range. System secure.")
        return
    
    # Group by severity
    unack_critical = [a for a in alerts if a.severity == AlertSeverity.CRITICAL and not a.acknowledged]
    unack_high = [a for a in alerts if a.severity == AlertSeverity.HIGH and not a.acknowledged]
    other = [a for a in alerts if a not in unack_critical and a not in unack_high]
    
    # Show unacknowledged critical first
    if unack_critical:
        st.error(f"🚨 {len(unack_critical)} CRITICAL UNACKNOWLEDGED ALERTS")
        for alert in unack_critical:
            _render_alert_card(alert, openshell_service, is_critical=True)
    
    if unack_high:
        st.warning(f"⚠️ {len(unack_high)} High Priority Unacknowledged Alerts")
        for alert in unack_high:
            _render_alert_card(alert, openshell_service, is_critical=False)
    
    # Show other alerts (collapsed)
    if other:
        with st.expander(f"📋 Other Alerts ({len(other)})", expanded=False):
            for alert in other:
                _render_alert_card(alert, openshell_service, is_critical=False)

def _render_alert_card(
    alert: SecurityAlert,
    openshell_service,
    is_critical: bool = False
):
    """Render a single alert card."""
    
    icon, color, label = SEVERITY_STYLES[alert.severity]
    type_icon = ALERT_TYPE_ICONS.get(alert.alert_type, "⚠️")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.write(f"**{icon}**")
            st.caption(label)
        
        with col2:
            st.write(f"**{type_icon} {alert.title}**")
            st.write(alert.description)
            st.caption(f"Agent: {alert.sandbox_name} | {alert.timestamp.strftime('%H:%M:%S')}")
        
        with col3:
            if not alert.acknowledged:
                if st.button("✓ Acknowledge", key=f"ack_{alert.id}", use_container_width=True):
                    _acknowledge_alert(openshell_service, alert.id)
                    st.rerun()
            
            if not alert.resolved:
                if st.button("✓ Resolve", key=f"resolve_{alert.id}", use_container_width=True):
                    _resolve_alert(openshell_service, alert.id)
                    st.rerun()
        
        # Alert details
        with st.expander("📋 Details", expanded=is_critical):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Alert Information**")
                st.write(f"**ID:** `{alert.id}`")
                st.write(f"**Type:** {alert.alert_type.value.replace('_', ' ').title()}")
                st.write(f"**Severity:** {alert.severity.value.upper()}")
                st.write(f"**Sandbox:** {alert.sandbox_name}")
            
            with col2:
                st.markdown("**Detection Details**")
                for key, value in alert.details.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        st.divider()

def _render_alert_timeline(alerts: List[SecurityAlert]):
    """Render alert timeline visualization."""
    
    # Count alerts by time bucket (hourly)
    time_buckets = {}
    for alert in alerts:
        hour = alert.timestamp.replace(minute=0, second=0, microsecond=0)
        if hour not in time_buckets:
            time_buckets[hour] = {sev: 0 for sev in AlertSeverity}
        time_buckets[hour][alert.severity] += 1
    
    # Sort by time
    sorted_times = sorted(time_buckets.keys())
    
    # Create stacked bar chart
    fig = go.Figure()
    
    severities = [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM, AlertSeverity.LOW]
    colors = ['#ff4444', '#ff8800', '#ffbb33', '#33b5e5']
    
    for sev, color in zip(severities, colors):
        counts = [time_buckets[t][sev] for t in sorted_times]
        fig.add_trace(go.Bar(
            name=sev.value.title(),
            x=[t.strftime('%H:%M') for t in sorted_times],
            y=counts,
            marker_color=color
        ))
    
    fig.update_layout(
        barmode='stack',
        title="Alert Timeline",
        xaxis_title="Time",
        yaxis_title="Alert Count",
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_policy_violations(
    openshell_service,
    instance_id: str,
    violation_types: Optional[List[str]] = None
):
    """Render policy violations component."""
    
    # Fetch violations
    violations = _fetch_policy_violations(openshell_service)
    
    # Apply type filter
    if violation_types:
        violation_types = [v.lower() for v in violation_types]
        violations = [v for v in violations if v.violation_type.value in violation_types]
    
    # Summary
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    total = len(violations)
    critical = sum(1 for v in violations if v.severity == AlertSeverity.CRITICAL)
    today = sum(1 for v in violations if v.timestamp.date() == datetime.now().date())
    
    with col1:
        st.metric("Total Violations", total)
    with col2:
        delta_color = "inverse" if critical > 0 else "normal"
        st.metric("Critical", critical, delta_color=delta_color)
    with col3:
        st.metric("Today", today)
    
    st.divider()
    
    # Violation breakdown by type
    _render_violation_breakdown(violations)
    
    # Violation list
    st.divider()
    st.subheader("Violation Log")
    
    if not violations:
        st.success("✅ No policy violations detected. All agents compliant.")
        return
    
    # Group by severity
    critical_violations = [v for v in violations if v.severity == AlertSeverity.CRITICAL]
    high_violations = [v for v in violations if v.severity == AlertSeverity.HIGH]
    other = [v for v in violations if v not in critical_violations and v not in high_violations]
    
    if critical_violations:
        st.error(f"🚨 {len(critical_violations)} Critical Policy Violations")
        for v in critical_violations:
            _render_violation_card(v)
    
    if high_violations:
        st.warning(f"⚠️ {len(high_violations)} High Severity Violations")
        for v in high_violations:
            _render_violation_card(v)
    
    if other:
        with st.expander(f"📋 Other Violations ({len(other)})", expanded=False):
            for v in other:
                _render_violation_card(v)

def _render_violation_card(violation: PolicyViolation):
    """Render a single violation card."""
    
    icon, color, label = SEVERITY_STYLES[violation.severity]
    
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.write(f"**{icon}**")
            st.caption(violation.violation_type.value.replace('_', ' ').title())
        
        with col2:
            st.write(f"**{violation.policy_name}**")
            st.write(violation.description)
            st.caption(f"Agent: {violation.sandbox_name} | {violation.timestamp.strftime('%H:%M:%S')}")
        
        with col3:
            st.write(f"**Action:** {violation.action_taken}")
            st.caption(label)
        
        with st.expander("📋 Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** `{violation.id}`")
                st.write(f"**Type:** {violation.violation_type.value.replace('_', ' ').title()}")
                st.write(f"**Policy:** {violation.policy_name}")
            with col2:
                st.write(f"**Agent:** {violation.sandbox_name}")
                st.write(f"**Severity:** {violation.severity.value.upper()}")
                st.write(f"**Action:** {violation.action_taken}")
        
        st.divider()

def _render_violation_breakdown(violations: List[PolicyViolation]):
    """Render violation type breakdown chart."""
    
    # Count by type
    type_counts = {}
    for v in violations:
        name = VIOLATION_TYPE_NAMES.get(v.violation_type, v.violation_type.value)
        type_counts[name] = type_counts.get(name, 0) + 1
    
    if not type_counts:
        return
    
    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=0.4,
        marker=dict(colors=['#ff4444', '#ff8800', '#ffbb33', '#33b5e5', '#00C851', '#76B900'])
    )])
    
    fig.update_layout(
        title="Violations by Type",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _fetch_security_alerts(openshell_service, time_range: str) -> List[SecurityAlert]:
    """Fetch security alerts from OpenShell service."""
    
    # Parse time range
    now = datetime.now()
    if time_range == "Last Hour":
        cutoff = now - timedelta(hours=1)
    elif time_range == "Last 4 Hours":
        cutoff = now - timedelta(hours=4)
    elif time_range == "Last 24 Hours":
        cutoff = now - timedelta(days=1)
    else:  # Last 7 Days
        cutoff = now - timedelta(days=7)
    
    # Mock data
    mock_alerts = [
        SecurityAlert(
            id="alert-001",
            timestamp=now - timedelta(minutes=15),
            severity=AlertSeverity.CRITICAL,
            alert_type=AlertType.PROMPT_INJECTION,
            sandbox_id="sandbox-003",
            sandbox_name="Agent-Gamma",
            title="Prompt Injection Detected",
            description="Potential prompt injection attack pattern detected in user input",
            details={
                "pattern": "ignore previous instructions",
                "confidence": 0.95,
                "input_length": 512,
                "blocked": True
            },
            acknowledged=False,
            resolved=False
        ),
        SecurityAlert(
            id="alert-002",
            timestamp=now - timedelta(hours=1),
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.DATA_EXFILTRATION,
            sandbox_id="sandbox-004",
            sandbox_name="Agent-Delta",
            title="Large Data Transfer Attempt",
            description="Attempted to transfer 500MB of data to external domain",
            details={
                "data_size": "500MB",
                "destination": "external-site.com",
                "type": "upload",
                "blocked": True
            },
            acknowledged=True,
            resolved=False
        ),
        SecurityAlert(
            id="alert-003",
            timestamp=now - timedelta(hours=2),
            severity=AlertSeverity.MEDIUM,
            alert_type=AlertType.RATE_LIMIT_VIOLATION,
            sandbox_id="sandbox-002",
            sandbox_name="Agent-Beta",
            title="Rate Limit Exceeded",
            description="API rate limit exceeded: 150 requests/minute",
            details={
                "limit": 100,
                "actual": 150,
                "duration": "1 minute"
            },
            acknowledged=True,
            resolved=True
        )
    ]
    
    return [a for a in mock_alerts if a.timestamp > cutoff]

def _fetch_policy_violations(openshell_service) -> List[PolicyViolation]:
    """Fetch policy violations from OpenShell service."""
    
    now = datetime.now()
    
    mock_violations = [
        PolicyViolation(
            id="viol-001",
            timestamp=now - timedelta(minutes=30),
            violation_type=ViolationType.NETWORK_POLICY,
            sandbox_id="sandbox-003",
            sandbox_name="Agent-Gamma",
            policy_name="External Domain Restriction",
            description="Attempted to access unauthorized domain: malicious-site.com",
            severity=AlertSeverity.CRITICAL,
            action_taken="Request Blocked",
            details={"domain": "malicious-site.com", "ip": "192.0.2.100"}
        ),
        PolicyViolation(
            id="viol-002",
            timestamp=now - timedelta(hours=2),
            violation_type=ViolationType.DATA_EXFILTRATION,
            sandbox_id="sandbox-004",
            sandbox_name="Agent-Delta",
            policy_name="Data Loss Prevention",
            description="Attempted to send sensitive data pattern via POST request",
            severity=AlertSeverity.CRITICAL,
            action_taken="Request Blocked + Alert",
            details={"pattern": "credit_card", "size": "10KB"}
        ),
        PolicyViolation(
            id="viol-003",
            timestamp=now - timedelta(hours=4),
            violation_type=ViolationType.RATE_LIMIT,
            sandbox_id="sandbox-002",
            sandbox_name="Agent-Beta",
            policy_name="API Rate Limit",
            description="Exceeded maximum requests per minute",
            severity=AlertSeverity.MEDIUM,
            action_taken="Throttled",
            details={"limit": 100, "actual": 145}
        )
    ]
    
    return mock_violations

def _acknowledge_alert(openshell_service, alert_id: str) -> bool:
    """Acknowledge an alert."""
    return True

def _resolve_alert(openshell_service, alert_id: str) -> bool:
    """Resolve an alert."""
    return True
