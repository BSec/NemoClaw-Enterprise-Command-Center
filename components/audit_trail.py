"""Audit Trail component for CISO Dashboard.

Comprehensive activity logging and forensic capabilities.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import plotly.graph_objects as go

class AuditEventType(Enum):
    """Types of audit events."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    POLICY_CHANGE = "policy_change"
    SANDBOX_CREATE = "sandbox_create"
    SANDBOX_DELETE = "sandbox_delete"
    REQUEST_APPROVE = "request_approve"
    REQUEST_DENY = "request_deny"
    CONFIG_CHANGE = "config_change"
    PERMISSION_CHANGE = "permission_change"
    ALERT_ACK = "alert_acknowledge"
    VIOLATION_RESOLVE = "violation_resolve"
    DATA_ACCESS = "data_access"

class AuditSeverity(Enum):
    """Audit event severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AuditEvent:
    """Individual audit event."""
    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user: str
    action: str
    resource: str
    details: Dict[str, any]
    ip_address: str
    session_id: str
    success: bool

@dataclass
class AuditSummary:
    """Audit summary statistics."""
    total_events_24h: int
    critical_events: int
    failed_actions: int
    unique_users: int
    top_event_types: List[tuple[str, int]]

EVENT_TYPE_ICONS = {
    AuditEventType.USER_LOGIN: "🔑",
    AuditEventType.USER_LOGOUT: "🚪",
    AuditEventType.POLICY_CHANGE: "⚖️",
    AuditEventType.SANDBOX_CREATE: "🆕",
    AuditEventType.SANDBOX_DELETE: "🗑️",
    AuditEventType.REQUEST_APPROVE: "✅",
    AuditEventType.REQUEST_DENY: "❌",
    AuditEventType.CONFIG_CHANGE: "⚙️",
    AuditEventType.PERMISSION_CHANGE: "🔐",
    AuditEventType.ALERT_ACK: "📋",
    AuditEventType.VIOLATION_RESOLVE: "✓",
    AuditEventType.DATA_ACCESS: "📄"
}

SEVERITY_STYLES = {
    AuditSeverity.CRITICAL: ("🔴", "#ff4444"),
    AuditSeverity.HIGH: ("🟠", "#ff8800"),
    AuditSeverity.MEDIUM: ("🟡", "#ffbb33"),
    AuditSeverity.LOW: ("🟢", "#00C851"),
    AuditSeverity.INFO: ("⚪", "#grey")
}

def render_audit_trail(
    openshell_service,
    instance_id: str
):
    """Render audit trail viewer."""
    
    # Fetch audit data
    summary = _fetch_audit_summary(openshell_service)
    events = _fetch_audit_events(openshell_service)
    
    # Header metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Events (24h)", summary.total_events_24h)
    with col2:
        color = "inverse" if summary.critical_events > 0 else "normal"
        st.metric("Critical", summary.critical_events, delta_color=color)
    with col3:
        color = "inverse" if summary.failed_actions > 0 else "normal"
        st.metric("Failed Actions", summary.failed_actions, delta_color=color)
    with col4:
        st.metric("Active Users", summary.unique_users)
    
    st.divider()
    
    # Event timeline
    _render_event_timeline(events)
    
    # Event type distribution
    st.divider()
    st.subheader("Event Distribution")
    _render_event_distribution(events)
    
    # Filters
    st.divider()
    st.subheader("🔍 Search & Filter")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        event_types = st.multiselect(
            "Event Types",
            options=[e.value for e in AuditEventType],
            default=[],
            key="audit_event_types"
        )
    with col2:
        severity_filter = st.multiselect(
            "Severity",
            options=[s.value for s in AuditSeverity],
            default=[AuditSeverity.CRITICAL.value, AuditSeverity.HIGH.value],
            key="audit_severity"
        )
    with col3:
        user_filter = st.text_input("User", placeholder="Filter by user...", key="audit_user")
    with col4:
        time_range = st.selectbox(
            "Time Range",
            options=["Last Hour", "Last 4 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
            index=2,
            key="audit_time_range"
        )
    
    # Search
    search_term = st.text_input("🔍 Search events...", placeholder="Enter search term...", key="audit_search")
    
    # Filter events
    filtered = events
    if event_types:
        filtered = [e for e in filtered if e.event_type.value in event_types]
    if severity_filter:
        filtered = [e for e in filtered if e.severity.value in severity_filter]
    if user_filter:
        filtered = [e for e in filtered if user_filter.lower() in e.user.lower()]
    if search_term:
        filtered = [e for e in filtered if 
                   search_term.lower() in e.action.lower() or 
                   search_term.lower() in e.resource.lower() or
                   search_term.lower() in str(e.details).lower()]
    
    # Event list
    st.divider()
    st.subheader(f"Audit Events ({len(filtered)} found)")
    
    if filtered:
        # Show most recent first
        for event in sorted(filtered, key=lambda e: e.timestamp, reverse=True):
            _render_audit_event(event)
    else:
        st.info("No events match the selected filters")
    
    # Export options
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Audit Log", use_container_width=True):
            st.info("Export functionality coming in Phase 4")
    with col2:
        if st.button("📊 Generate Compliance Report", use_container_width=True):
            st.info("Compliance report generation coming in Phase 4")

def _render_event_timeline(events: List[AuditEvent]):
    """Render event timeline chart."""
    
    # Group by hour for last 24 hours
    now = datetime.now()
    hourly_counts = {}
    
    for i in range(24):
        hour = now - timedelta(hours=i)
        hour_key = hour.strftime("%H:00")
        hourly_counts[hour_key] = 0
    
    for event in events:
        if event.timestamp > now - timedelta(hours=24):
            hour_key = event.timestamp.strftime("%H:00")
            if hour_key in hourly_counts:
                hourly_counts[hour_key] += 1
    
    # Sort by time
    sorted_hours = sorted(hourly_counts.keys())
    counts = [hourly_counts[h] for h in sorted_hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sorted_hours,
        y=counts,
        mode='lines+markers',
        line=dict(color='#76B900', width=2),
        fill='tozeroy',
        fillcolor='rgba(118, 185, 0, 0.2)',
        name='Events'
    ))
    
    fig.update_layout(
        title="Event Timeline (Last 24 Hours)",
        xaxis_title="Hour",
        yaxis_title="Event Count",
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_event_distribution(events: List[AuditEvent]):
    """Render event type distribution."""
    
    # Count by type
    type_counts = {}
    for event in events:
        type_name = event.event_type.value.replace('_', ' ').title()
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    if not type_counts:
        return
    
    # Sort by count
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    fig = go.Figure(data=[go.Bar(
        x=[t[0] for t in sorted_types],
        y=[t[1] for t in sorted_types],
        marker_color='#76B900'
    )])
    
    fig.update_layout(
        title="Top Event Types",
        xaxis_title="Event Type",
        yaxis_title="Count",
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3'),
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_audit_event(event: AuditEvent):
    """Render individual audit event."""
    
    icon = EVENT_TYPE_ICONS.get(event.event_type, "📝")
    severity_icon, color = SEVERITY_STYLES[event.severity]
    
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.write(f"**{icon}**")
            st.caption(severity_icon + " " + event.severity.value.upper())
        
        with col2:
            st.write(f"**{event.action}**")
            st.caption(f"User: {event.user} | Resource: {event.resource}")
            st.caption(f"Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col3:
            if not event.success:
                st.error("❌ FAILED")
            st.caption(f"IP: {event.ip_address}")
            st.caption(f"Session: {event.session_id[:12]}...")
        
        with st.expander("📋 Event Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Event Information**")
                st.write(f"**ID:** `{event.id}`")
                st.write(f"**Type:** {event.event_type.value.replace('_', ' ').title()}")
                st.write(f"**Severity:** {event.severity.value.upper()}")
                st.write(f"**Success:** {'Yes' if event.success else 'No'}")
            
            with col2:
                st.markdown("**Request Context**")
                st.write(f"**User:** {event.user}")
                st.write(f"**IP Address:** {event.ip_address}")
                st.write(f"**Session:** {event.session_id}")
            
            st.markdown("**Details**")
            st.json(event.details)
        
        st.divider()

def _fetch_audit_summary(openshell_service) -> AuditSummary:
    """Fetch audit summary statistics."""
    
    return AuditSummary(
        total_events_24h=1247,
        critical_events=3,
        failed_actions=12,
        unique_users=28,
        top_event_types=[
            ("user_login", 342),
            ("data_access", 156),
            ("request_approve", 89),
            ("sandbox_create", 45),
            ("config_change", 23)
        ]
    )

def _fetch_audit_events(openshell_service) -> List[AuditEvent]:
    """Fetch audit events."""
    
    now = datetime.now()
    
    return [
        AuditEvent(
            id="AUDIT-001",
            timestamp=now - timedelta(minutes=5),
            event_type=AuditEventType.POLICY_CHANGE,
            severity=AuditSeverity.HIGH,
            user="admin@company.com",
            action="Modified network policy",
            resource="network-policy-prod",
            details={
                "old_config": {"allowed_domains": ["api.internal.com"]},
                "new_config": {"allowed_domains": ["api.internal.com", "external-api.com"]},
                "change_reason": "Added partner API integration"
            },
            ip_address="10.0.1.45",
            session_id="sess_abc123xyz789",
            success=True
        ),
        AuditEvent(
            id="AUDIT-002",
            timestamp=now - timedelta(minutes=15),
            event_type=AuditEventType.REQUEST_DENY,
            severity=AuditSeverity.MEDIUM,
            user="system",
            action="Denied outbound request",
            resource="sandbox-003",
            details={
                "request_url": "https://suspicious-site.com/upload",
                "reason": "Domain not in whitelist",
                "sandbox": "Agent-Gamma"
            },
            ip_address="internal",
            session_id="system",
            success=True
        ),
        AuditEvent(
            id="AUDIT-003",
            timestamp=now - timedelta(hours=1),
            event_type=AuditEventType.USER_LOGIN,
            severity=AuditSeverity.INFO,
            user="secops@company.com",
            action="User login successful",
            resource="dashboard",
            details={
                "auth_method": "SSO",
                "mfa_verified": True
            },
            ip_address="192.168.1.100",
            session_id="sess_def456uvw012",
            success=True
        ),
        AuditEvent(
            id="AUDIT-004",
            timestamp=now - timedelta(hours=2),
            event_type=AuditEventType.SANDBOX_CREATE,
            severity=AuditSeverity.INFO,
            user="engineer@company.com",
            action="Created new sandbox",
            resource="Agent-Epsilon",
            details={
                "agent_type": "openai",
                "model": "gpt-4",
                "workspace": "/workspaces/agent-epsilon"
            },
            ip_address="10.0.2.15",
            session_id="sess_ghi789rst345",
            success=True
        ),
        AuditEvent(
            id="AUDIT-005",
            timestamp=now - timedelta(hours=3),
            event_type=AuditEventType.CONFIG_CHANGE,
            severity=AuditSeverity.HIGH,
            user="admin@company.com",
            action="Updated security settings",
            resource="security-config",
            details={
                "changes": ["increased_max_request_size", "tightened_rate_limits"],
                "reason": "Security hardening"
            },
            ip_address="10.0.1.45",
            session_id="sess_abc123xyz789",
            success=True
        ),
        AuditEvent(
            id="AUDIT-006",
            timestamp=now - timedelta(hours=4),
            event_type=AuditEventType.PERMISSION_CHANGE,
            severity=AuditSeverity.CRITICAL,
            user="admin@company.com",
            action="Granted elevated permissions",
            resource="user:new-engineer@company.com",
            details={
                "granted_roles": ["sandbox_admin", "policy_editor"],
                "requested_by": "manager@company.com",
                "approval_ticket": "SEC-1234"
            },
            ip_address="10.0.1.45",
            session_id="sess_abc123xyz789",
            success=True
        ),
        AuditEvent(
            id="AUDIT-007",
            timestamp=now - timedelta(hours=5),
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            user="Agent-Delta",
            action="Accessed sensitive data",
            resource="customer_database",
            details={
                "records_accessed": 15,
                "query_pattern": "SELECT * FROM customers WHERE...",
                "justification": "Customer support request"
            },
            ip_address="internal",
            session_id="sandbox-sess-004",
            success=True
        ),
        AuditEvent(
            id="AUDIT-008",
            timestamp=now - timedelta(hours=6),
            event_type=AuditEventType.ALERT_ACK,
            severity=AuditSeverity.MEDIUM,
            user="secops@company.com",
            action="Acknowledged security alert",
            resource="alert-002",
            details={
                "alert_type": "Data Exfiltration",
                "acknowledged_at": (now - timedelta(hours=6)).isoformat()
            },
            ip_address="192.168.1.100",
            session_id="sess_def456uvw012",
            success=True
        ),
        AuditEvent(
            id="AUDIT-009",
            timestamp=now - timedelta(minutes=30),
            event_type=AuditEventType.USER_LOGIN,
            severity=AuditSeverity.HIGH,
            user="unknown@external.com",
            action="Failed login attempt",
            resource="dashboard",
            details={
                "auth_method": "password",
                "failure_reason": "Invalid credentials",
                "attempt_count": 5
            },
            ip_address="203.0.113.50",
            session_id="failed_sess_001",
            success=False
        ),
        AuditEvent(
            id="AUDIT-010",
            timestamp=now - timedelta(hours=8),
            event_type=AuditEventType.VIOLATION_RESOLVE,
            severity=AuditSeverity.MEDIUM,
            user="compliance@company.com",
            action="Resolved policy violation",
            resource="viol-003",
            details={
                "violation_type": "Rate Limit",
                "resolution": "User educated, policy acknowledged",
                "follow_up_required": False
            },
            ip_address="10.0.3.20",
            session_id="sess_jkl012mno456",
            success=True
        )
    ]
