"""Request Queue component for managing OpenShell network requests.

Provides UI for viewing, filtering, and approving/denying requests.
"""

import streamlit as st
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import time

class RequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"

class RequestRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NetworkRequest:
    id: str
    sandbox_id: str
    sandbox_name: str
    timestamp: datetime
    method: str  # GET, POST, etc.
    url: str
    status: RequestStatus
    risk_score: int  # 0-100
    risk_level: RequestRisk
    reason: str  # Why it's flagged (e.g., "external domain", "sensitive data")
    estimated_data_size: Optional[int] = None
    request_body_preview: Optional[str] = None

# Risk level styling
RISK_COLORS = {
    RequestRisk.LOW: ("🟢", "#00C851"),
    RequestRisk.MEDIUM: ("🟡", "#ffbb33"),
    RequestRisk.HIGH: ("🔴", "#ff4444"),
    RequestRisk.CRITICAL: ("🔴", "#ff4444")
}

STATUS_COLORS = {
    RequestStatus.PENDING: ("⏳", "#ffbb33"),
    RequestStatus.APPROVED: ("✅", "#00C851"),
    RequestStatus.DENIED: ("❌", "#ff4444"),
    RequestStatus.EXPIRED: ("⚪", "#grey")
}

def render_request_queue(
    openshell_service,
    instance_id: str,
    filter_status: Optional[List[str]] = None,
    auto_refresh: bool = True,
    refresh_interval: float = 3.0
):
    """Render the main request queue component."""
    
    # Initialize request data
    requests = _fetch_requests(openshell_service, filter_status)
    
    # Summary metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    pending_count = sum(1 for r in requests if r.status == RequestStatus.PENDING)
    critical_count = sum(1 for r in requests if r.risk_level == RequestRisk.CRITICAL and r.status == RequestStatus.PENDING)
    high_count = sum(1 for r in requests if r.risk_level == RequestRisk.HIGH and r.status == RequestStatus.PENDING)
    approved_today = sum(1 for r in requests if r.status == RequestStatus.APPROVED)
    
    with col1:
        st.metric("Pending", pending_count, delta=f"{critical_count} critical" if critical_count > 0 else None, delta_color="inverse")
    with col2:
        st.metric("High Risk", high_count, delta_color="inverse")
    with col3:
        st.metric("Approved Today", approved_today)
    with col4:
        avg_risk = sum(r.risk_score for r in requests if r.status == RequestStatus.PENDING) / pending_count if pending_count > 0 else 0
        st.metric("Avg Risk Score", f"{avg_risk:.0f}/100")
    
    st.divider()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
    
    # Request list
    if not requests:
        st.info("✅ No requests in queue. All caught up!")
        return
    
    # Group by status
    pending_requests = [r for r in requests if r.status == RequestStatus.PENDING]
    other_requests = [r for r in requests if r.status != RequestStatus.PENDING]
    
    # Show pending requests first
    if pending_requests:
        st.subheader(f"⏳ Pending Requests ({len(pending_requests)})")
        
        for request in pending_requests:
            _render_request_card(request, openshell_service, is_pending=True)
    
    # Show resolved requests (collapsible)
    if other_requests:
        with st.expander(f"📜 Resolved Requests ({len(other_requests)})", expanded=False):
            for request in other_requests:
                _render_request_card(request, openshell_service, is_pending=False)

def _render_request_card(
    request: NetworkRequest,
    openshell_service,
    is_pending: bool = True
):
    """Render a single request card."""
    
    risk_icon, risk_color = RISK_COLORS[request.risk_level]
    status_icon, _ = STATUS_COLORS[request.status]
    
    with st.container():
        # Header row
        col1, col2, col3, col4 = st.columns([2, 3, 1, 2])
        
        with col1:
            st.write(f"**{request.sandbox_name}**")
            st.caption(f"ID: {request.id[:8]}...")
        
        with col2:
            st.write(f"`{request.method}` {request.url[:60]}...")
            st.caption(f"Risk: {risk_icon} {request.risk_level.value.upper()} ({request.risk_score}/100)")
        
        with col3:
            st.write(f"{status_icon} {request.status.value.upper()}")
            st.caption(request.timestamp.strftime("%H:%M:%S"))
        
        with col4:
            if is_pending:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✅ Approve", key=f"approve_{request.id}", use_container_width=True):
                        _approve_request(openshell_service, request.id)
                        st.success("Approved!")
                        st.rerun()
                with btn_col2:
                    if st.button("❌ Deny", key=f"deny_{request.id}", use_container_width=True):
                        _deny_request(openshell_service, request.id)
                        st.warning("Denied!")
                        st.rerun()
        
        # Details expander
        with st.expander("📋 Request Details", expanded=False):
            _render_request_details(request)
        
        st.divider()

def _render_request_details(request: NetworkRequest):
    """Render detailed request information."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Request Information**")
        st.write(f"**ID:** `{request.id}`")
        st.write(f"**Sandbox:** {request.sandbox_name} ({request.sandbox_id})")
        st.write(f"**Timestamp:** {request.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Method:** {request.method}")
        st.write(f"**URL:** `{request.url}`")
        
        if request.estimated_data_size:
            st.write(f"**Data Size:** {_format_bytes(request.estimated_data_size)}")
    
    with col2:
        st.markdown("**Risk Analysis**")
        st.write(f"**Risk Score:** {request.risk_score}/100")
        st.write(f"**Risk Level:** {request.risk_level.value.upper()}")
        st.write(f"**Flag Reason:** {request.reason}")
        
        # Risk score visualization
        st.progress(request.risk_score / 100, text=f"Risk: {request.risk_score}%")
        
        if request.risk_score > 80:
            st.error("⚠️ CRITICAL: This request has been flagged for manual review due to high risk indicators.")
        elif request.risk_score > 50:
            st.warning("⚡ MEDIUM: This request requires approval before proceeding.")
        else:
            st.info("ℹ️ LOW: Standard verification recommended.")
    
    if request.request_body_preview:
        st.divider()
        st.markdown("**Request Body Preview**")
        st.code(request.request_body_preview[:500], language="json")

def render_request_details(
    request_id: str,
    openshell_service
):
    """Render detailed view of a specific request."""
    
    st.subheader(f"Request Details: {request_id}")
    
    # Fetch request details
    request = _fetch_request_by_id(openshell_service, request_id)
    
    if not request:
        st.error("Request not found")
        return
    
    _render_request_details(request)
    
    # Action buttons
    st.divider()
    if request.status == RequestStatus.PENDING:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve Request", type="primary", use_container_width=True):
                _approve_request(openshell_service, request.id)
                st.success("Request approved!")
        with col2:
            if st.button("❌ Deny Request", type="secondary", use_container_width=True):
                _deny_request(openshell_service, request.id)
                st.warning("Request denied!")
    else:
        st.info(f"This request has already been {request.status.value}.")

def _fetch_requests(
    openshell_service,
    filter_status: Optional[List[str]] = None
) -> List[NetworkRequest]:
    """Fetch requests from OpenShell service."""
    
    # Placeholder implementation - would integrate with actual OpenShell API
    # For now, return mock data for demonstration
    
    mock_requests = [
        NetworkRequest(
            id="req-001",
            sandbox_id="sandbox-1",
            sandbox_name="Agent-Alpha",
            timestamp=datetime.now(),
            method="GET",
            url="https://api.example.com/data",
            status=RequestStatus.PENDING,
            risk_score=25,
            risk_level=RequestRisk.LOW,
            reason="External API call",
            estimated_data_size=1024,
            request_body_preview=None
        ),
        NetworkRequest(
            id="req-002",
            sandbox_id="sandbox-2",
            sandbox_name="Agent-Beta",
            timestamp=datetime.now(),
            method="POST",
            url="https://suspicious-site.com/upload",
            status=RequestStatus.PENDING,
            risk_score=85,
            risk_level=RequestRisk.CRITICAL,
            reason="Suspicious domain + data upload",
            estimated_data_size=10485760,
            request_body_preview='{"data": "sensitive_info"}'
        ),
        NetworkRequest(
            id="req-003",
            sandbox_id="sandbox-1",
            sandbox_name="Agent-Alpha",
            timestamp=datetime.now(),
            method="GET",
            url="https://safe-site.com/api",
            status=RequestStatus.APPROVED,
            risk_score=15,
            risk_level=RequestRisk.LOW,
            reason="Safe domain",
            estimated_data_size=512,
            request_body_preview=None
        )
    ]
    
    # Apply status filter
    if filter_status:
        status_filter = [RequestStatus(s) for s in filter_status]
        mock_requests = [r for r in mock_requests if r.status in status_filter]
    
    return mock_requests

def _fetch_request_by_id(openshell_service, request_id: str) -> Optional[NetworkRequest]:
    """Fetch single request by ID."""
    requests = _fetch_requests(openshell_service)
    return next((r for r in requests if r.id == request_id), None)

def _approve_request(openshell_service, request_id: str) -> bool:
    """Approve a pending request."""
    # Placeholder - would call OpenShell API
    return True

def _deny_request(openshell_service, request_id: str) -> bool:
    """Deny a pending request."""
    # Placeholder - would call OpenShell API
    return True

def _format_bytes(size: int) -> str:
    """Format byte size to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
