"""Compliance Overview component for CISO Dashboard.

Tracks regulatory compliance status for SOC2, GDPR, HIPAA, and other frameworks.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ComplianceStatus(Enum):
    """Compliance control status."""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOC2 = "SOC 2 Type II"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    ISO27001 = "ISO 27001"
    NIST = "NIST CSF"
    PCI_DSS = "PCI DSS"

@dataclass
class ComplianceControl:
    """Individual compliance control."""
    id: str
    name: str
    description: str
    framework: ComplianceFramework
    status: ComplianceStatus
    last_checked: datetime
    evidence_count: int
    critical: bool
    owner: str
    next_audit: datetime

@dataclass
class ComplianceSummary:
    """Summary for a compliance framework."""
    framework: ComplianceFramework
    overall_score: float  # 0-100
    controls_total: int
    controls_compliant: int
    controls_partial: int
    controls_non_compliant: int
    last_assessment: datetime
    next_assessment: datetime
    auditor: str

# Status styling
STATUS_STYLES = {
    ComplianceStatus.COMPLIANT: ("✅", "#00C851", "Compliant"),
    ComplianceStatus.PARTIAL: ("⚠️", "#ffbb33", "Partial"),
    ComplianceStatus.NON_COMPLIANT: ("❌", "#ff4444", "Non-Compliant"),
    ComplianceStatus.NOT_APPLICABLE: ("⚪", "#grey", "N/A")
}

FRAMEWORK_ICONS = {
    ComplianceFramework.SOC2: "🔒",
    ComplianceFramework.GDPR: "🛡️",
    ComplianceFramework.HIPAA: "🏥",
    ComplianceFramework.ISO27001: "📋",
    ComplianceFramework.NIST: "🌐",
    ComplianceFramework.PCI_DSS: "💳"
}

def render_compliance_dashboard(
    openshell_service,
    instance_id: str
):
    """Render compliance dashboard."""
    
    # Fetch compliance data
    summaries = _fetch_compliance_summaries(openshell_service)
    controls = _fetch_compliance_controls(openshell_service)
    
    # Overall compliance score
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    total_score = sum(s.overall_score for s in summaries) / len(summaries) if summaries else 0
    total_controls = sum(s.controls_total for s in summaries)
    total_compliant = sum(s.controls_compliant for s in summaries)
    non_compliant = sum(s.controls_non_compliant for s in summaries)
    
    with col1:
        color = "normal" if total_score >= 90 else "inverse"
        st.metric("Overall Compliance", f"{total_score:.0f}%", delta_color=color)
    with col2:
        st.metric("Total Controls", total_controls)
    with col3:
        st.metric("Compliant", total_compliant, f"{total_compliant/total_controls*100:.0f}%" if total_controls > 0 else "0%")
    with col4:
        color = "inverse" if non_compliant > 0 else "normal"
        st.metric("Non-Compliant", non_compliant, delta_color=color)
    
    st.divider()
    
    # Framework cards
    st.subheader("Framework Status")
    
    cols = st.columns(min(len(summaries), 3))
    for idx, summary in enumerate(summaries):
        with cols[idx % 3]:
            _render_framework_card(summary)
    
    st.divider()
    
    # Compliance matrix
    st.subheader("Control Compliance Matrix")
    _render_compliance_matrix(controls)
    
    # Control details
    st.divider()
    st.subheader("Control Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        framework_filter = st.multiselect(
            "Framework",
            options=[f.value for f in ComplianceFramework],
            default=[f.value for f in ComplianceFramework],
            key="compliance_framework_filter"
        )
    with col2:
        status_filter = st.multiselect(
            "Status",
            options=[s.value for s in ComplianceStatus],
            default=[ComplianceStatus.NON_COMPLIANT.value, ComplianceStatus.PARTIAL.value],
            key="compliance_status_filter"
        )
    with col3:
        critical_only = st.checkbox("Critical Controls Only", key="compliance_critical_only")
    
    # Filter controls
    filtered = controls
    if framework_filter:
        filtered = [c for c in filtered if c.framework.value in framework_filter]
    if status_filter:
        filtered = [c for c in filtered if c.status.value in status_filter]
    if critical_only:
        filtered = [c for c in filtered if c.critical]
    
    # Display controls
    if filtered:
        for control in filtered:
            _render_control_card(control)
    else:
        st.success("✅ All controls meet selected criteria")
    
    # Audit schedule
    st.divider()
    st.subheader("📅 Upcoming Audits")
    _render_audit_schedule(summaries)

def _render_framework_card(summary: ComplianceSummary):
    """Render a framework summary card."""
    
    icon = FRAMEWORK_ICONS.get(summary.framework, "📋")
    
    with st.container():
        st.markdown(f"**{icon} {summary.framework.value}**")
        
        # Score gauge
        score_color = "#00C851" if summary.overall_score >= 90 else "#ffbb33" if summary.overall_score >= 70 else "#ff4444"
        st.progress(summary.overall_score / 100, text=f"{summary.overall_score:.0f}%")
        
        # Control counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"✅ {summary.controls_compliant}")
        with col2:
            st.caption(f"⚠️ {summary.controls_partial}")
        with col3:
            if summary.controls_non_compliant > 0:
                st.error(f"❌ {summary.controls_non_compliant}")
            else:
                st.caption(f"❌ {summary.controls_non_compliant}")
        
        # Assessment dates
        st.caption(f"Last: {summary.last_assessment.strftime('%Y-%m-%d')} | Next: {summary.next_assessment.strftime('%Y-%m-%d')}")
        st.caption(f"Auditor: {summary.auditor}")

def _render_compliance_matrix(controls: List[ComplianceControl]):
    """Render compliance matrix heatmap."""
    
    if not controls:
        return
    
    # Group by framework
    frameworks = list(set(c.framework for c in controls))
    statuses = [ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIAL, ComplianceStatus.NON_COMPLIANT]
    
    # Build matrix
    matrix = []
    for framework in frameworks:
        framework_controls = [c for c in controls if c.framework == framework]
        row = []
        for status in statuses:
            count = len([c for c in framework_controls if c.status == status])
            row.append(count)
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[s.value.title() for s in statuses],
        y=[f.value for f in frameworks],
        colorscale=[[0, '#00C851'], [0.5, '#ffbb33'], [1, '#ff4444']],
        text=[[str(val) for val in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 14},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Control Status by Framework",
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_control_card(control: ComplianceControl):
    """Render individual control card."""
    
    icon, color, label = STATUS_STYLES[control.status]
    
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.write(f"**{icon}**")
            if control.critical:
                st.error("🔴 CRITICAL")
        
        with col2:
            st.write(f"**{control.id}: {control.name}**")
            st.caption(control.description[:100] + "..." if len(control.description) > 100 else control.description)
            st.caption(f"Framework: {control.framework.value} | Owner: {control.owner}")
        
        with col3:
            st.write(f"**{label}**")
            st.caption(f"Evidence: {control.evidence_count} items")
            st.caption(f"Next audit: {control.next_audit.strftime('%Y-%m-%d')}")
        
        # Action buttons
        if control.status != ComplianceStatus.COMPLIANT:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📁 View Evidence", key=f"evidence_{control.id}", use_container_width=True):
                    st.info(f"Evidence for {control.id} - coming in Phase 4")
            with col2:
                if st.button("✏️ Update Status", key=f"update_{control.id}", use_container_width=True):
                    st.info(f"Status update for {control.id} - coming in Phase 4")
        
        st.divider()

def _render_audit_schedule(summaries: List[ComplianceSummary]):
    """Render upcoming audit schedule."""
    
    now = datetime.now()
    
    # Sort by next assessment date
    sorted_summaries = sorted(summaries, key=lambda s: s.next_assessment)
    
    for summary in sorted_summaries:
        days_until = (summary.next_assessment - now).days
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        
        with col1:
            icon = FRAMEWORK_ICONS.get(summary.framework, "📋")
            st.write(f"**{icon} {summary.framework.value}**")
        
        with col2:
            if days_until < 0:
                st.error(f"⚠️ Overdue by {abs(days_until)} days")
            elif days_until <= 7:
                st.warning(f"⏰ Due in {days_until} days")
            elif days_until <= 30:
                st.info(f"📅 Due in {days_until} days")
            else:
                st.caption(f"📅 Due in {days_until} days")
        
        with col3:
            st.write(f"{summary.overall_score:.0f}%")
        
        with col4:
            st.caption(f"Auditor: {summary.auditor}")
            if st.button("📋 View Details", key=f"audit_{summary.framework.value}", use_container_width=True):
                st.info(f"Audit details for {summary.framework.value} - coming in Phase 4")

def _fetch_compliance_summaries(openshell_service) -> List[ComplianceSummary]:
    """Fetch compliance framework summaries."""
    
    now = datetime.now()
    
    return [
        ComplianceSummary(
            framework=ComplianceFramework.SOC2,
            overall_score=96.5,
            controls_total=64,
            controls_compliant=62,
            controls_partial=2,
            controls_non_compliant=0,
            last_assessment=now - timedelta(days=45),
            next_assessment=now + timedelta(days=45),
            auditor="Deloitte"
        ),
        ComplianceSummary(
            framework=ComplianceFramework.GDPR,
            overall_score=92.0,
            controls_total=48,
            controls_compliant=44,
            controls_partial=3,
            controls_non_compliant=1,
            last_assessment=now - timedelta(days=30),
            next_assessment=now + timedelta(days=60),
            auditor="Internal"
        ),
        ComplianceSummary(
            framework=ComplianceFramework.ISO27001,
            overall_score=88.5,
            controls_total=114,
            controls_compliant=101,
            controls_partial=10,
            controls_non_compliant=3,
            last_assessment=now - timedelta(days=60),
            next_assessment=now + timedelta(days=30),
            auditor="BSI Group"
        ),
        ComplianceSummary(
            framework=ComplianceFramework.NIST,
            overall_score=94.2,
            controls_total=108,
            controls_compliant=102,
            controls_partial=5,
            controls_non_compliant=1,
            last_assessment=now - timedelta(days=90),
            next_assessment=now + timedelta(days=90),
            auditor="Internal"
        )
    ]

def _fetch_compliance_controls(openshell_service) -> List[ComplianceControl]:
    """Fetch compliance controls."""
    
    now = datetime.now()
    
    return [
        ComplianceControl(
            id="SOC2-CC1.1",
            name="Logical Access Security",
            description="Logical access to systems and data is restricted to authorized users",
            framework=ComplianceFramework.SOC2,
            status=ComplianceStatus.COMPLIANT,
            last_checked=now - timedelta(days=7),
            evidence_count=12,
            critical=True,
            owner="Security Team",
            next_audit=now + timedelta(days=30)
        ),
        ComplianceControl(
            id="SOC2-CC6.1",
            name="System Monitoring",
            description="System monitoring is implemented to detect security events",
            framework=ComplianceFramework.SOC2,
            status=ComplianceStatus.COMPLIANT,
            last_checked=now - timedelta(days=5),
            evidence_count=8,
            critical=True,
            owner="Ops Team",
            next_audit=now + timedelta(days=25)
        ),
        ComplianceControl(
            id="GDPR-Art32",
            name="Data Encryption",
            description="Personal data is encrypted at rest and in transit",
            framework=ComplianceFramework.GDPR,
            status=ComplianceStatus.PARTIAL,
            last_checked=now - timedelta(days=10),
            evidence_count=5,
            critical=True,
            owner="Data Protection Officer",
            next_audit=now + timedelta(days=15)
        ),
        ComplianceControl(
            id="GDPR-Art25",
            name="Privacy by Design",
            description="Privacy considerations integrated into system design",
            framework=ComplianceFramework.GDPR,
            status=ComplianceStatus.NON_COMPLIANT,
            last_checked=now - timedelta(days=14),
            evidence_count=2,
            critical=True,
            owner="Product Team",
            next_audit=now + timedelta(days=10)
        ),
        ComplianceControl(
            id="ISO27001-A12.4",
            name="Logging and Monitoring",
            description="Event logs recording user activities and system events",
            framework=ComplianceFramework.ISO27001,
            status=ComplianceStatus.COMPLIANT,
            last_checked=now - timedelta(days=3),
            evidence_count=15,
            critical=False,
            owner="Security Team",
            next_audit=now + timedelta(days=40)
        )
    ]
