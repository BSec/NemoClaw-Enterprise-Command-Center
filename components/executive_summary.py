"""Executive Summary component for CISO Dashboard.

Provides high-level KPIs and at-a-glance security status for executives.
"""

import streamlit as st
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@dataclass
class ExecutiveKPIs:
    """Key performance indicators for executive view."""
    overall_security_score: float  # 0-100
    risk_trend: str  # "improving", "stable", "worsening"
    critical_incidents_24h: int
    compliance_score: float  # 0-100
    active_threats: int
    pending_reviews: int
    system_uptime: float  # percentage
    agents_deployed: int
    agents_compliant: int
    data_requests_approved: int
    data_requests_denied: int

@dataclass
class SecurityTrend:
    """Security trend data point."""
    timestamp: datetime
    security_score: float
    incident_count: int
    compliance_score: float

def render_executive_summary(
    openshell_service,
    instance_id: str
):
    """Render executive summary KPIs and overview."""
    
    # Fetch KPIs
    kpis = _fetch_executive_kpis(openshell_service)
    trends = _fetch_security_trends(openshell_service)
    
    # Status indicator
    status_color = "🟢" if kpis.overall_security_score >= 80 else "🟡" if kpis.overall_security_score >= 60 else "🔴"
    status_text = "HEALTHY" if kpis.overall_security_score >= 80 else "ATTENTION" if kpis.overall_security_score >= 60 else "CRITICAL"
    
    st.subheader(f"{status_color} Security Status: {status_text}")
    
    # Top KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Security Score",
            f"{kpis.overall_security_score:.0f}/100",
            delta=f"{kpis.risk_trend.title()}",
            delta_color="normal" if kpis.risk_trend == "improving" else "off" if kpis.risk_trend == "stable" else "inverse"
        )
    
    with col2:
        delta_color = "inverse" if kpis.critical_incidents_24h > 0 else "normal"
        st.metric(
            "Critical Incidents (24h)",
            kpis.critical_incidents_24h,
            delta_color=delta_color
        )
    
    with col3:
        st.metric(
            "Compliance",
            f"{kpis.compliance_score:.0f}%",
            delta_color="normal" if kpis.compliance_score >= 90 else "inverse"
        )
    
    with col4:
        delta_color = "inverse" if kpis.active_threats > 0 else "normal"
        st.metric(
            "Active Threats",
            kpis.active_threats,
            delta_color=delta_color
        )
    
    with col5:
        st.metric(
            "Uptime",
            f"{kpis.system_uptime:.1f}%",
            delta_color="normal" if kpis.system_uptime >= 99 else "inverse"
        )
    
    st.divider()
    
    # Second row - operational metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        compliance_rate = (kpis.agents_compliant / kpis.agents_deployed * 100) if kpis.agents_deployed > 0 else 0
        st.metric(
            "Agent Compliance",
            f"{kpis.agents_compliant}/{kpis.agents_deployed}",
            f"{compliance_rate:.0f}%"
        )
    
    with col2:
        st.metric(
            "Pending Reviews",
            kpis.pending_reviews,
            delta_color="inverse" if kpis.pending_reviews > 10 else "normal"
        )
    
    with col3:
        approval_rate = (kpis.data_requests_approved / (kpis.data_requests_approved + kpis.data_requests_denied) * 100) if (kpis.data_requests_approved + kpis.data_requests_denied) > 0 else 0
        st.metric(
            "Data Access Approval Rate",
            f"{approval_rate:.0f}%",
            f"{kpis.data_requests_approved} approved, {kpis.data_requests_denied} denied"
        )
    
    with col4:
        # Calculate average time to resolve
        avg_resolution = "2.4h"  # Mock
        st.metric(
            "Avg Incident Resolution",
            avg_resolution,
            "-15% from last week"
        )
    
    st.divider()
    
    # Trend charts
    _render_executive_trends(trends)
    
    # Quick insights
    st.divider()
    _render_quick_insights(kpis, trends)

def _render_executive_trends(trends: List[SecurityTrend]):
    """Render executive trend charts."""
    
    st.subheader("📈 30-Day Security Trends")
    
    if not trends:
        st.info("No trend data available")
        return
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Security Score Trend',
            'Daily Incident Count',
            'Compliance Score',
            'Risk vs Time'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    times = [t.timestamp for t in trends]
    
    # Security Score
    scores = [t.security_score for t in trends]
    fig.add_trace(
        go.Scatter(
            x=times,
            y=scores,
            mode='lines',
            line=dict(color='#76B900', width=2),
            fill='tozeroy',
            fillcolor='rgba(118, 185, 0, 0.2)',
            name='Security Score'
        ),
        row=1, col=1
    )
    
    # Incidents
    incidents = [t.incident_count for t in trends]
    fig.add_trace(
        go.Bar(
            x=times,
            y=incidents,
            marker_color='#ff4444',
            name='Incidents'
        ),
        row=1, col=2
    )
    
    # Compliance
    compliance = [t.compliance_score for t in trends]
    fig.add_trace(
        go.Scatter(
            x=times,
            y=compliance,
            mode='lines',
            line=dict(color='#00C851', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 200, 81, 0.2)',
            name='Compliance'
        ),
        row=2, col=1
    )
    
    # Combined risk view (security vs compliance)
    fig.add_trace(
        go.Scatter(
            x=times,
            y=scores,
            mode='lines',
            line=dict(color='#76B900', width=2),
            name='Security'
        ),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=times,
            y=compliance,
            mode='lines',
            line=dict(color='#33b5e5', width=2),
            name='Compliance'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    # Update y-axes ranges
    fig.update_yaxes(range=[0, 100], row=1, col=1)
    fig.update_yaxes(range=[0, max(incidents) * 1.2 if incidents else 10], row=1, col=2)
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    fig.update_yaxes(range=[0, 100], row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

def _render_quick_insights(kpis: ExecutiveKPIs, trends: List[SecurityTrend]):
    """Render quick insights and recommendations."""
    
    st.subheader("💡 Executive Insights")
    
    insights = []
    
    # Generate insights based on KPIs
    if kpis.critical_incidents_24h > 0:
        insights.append({
            "type": "warning",
            "icon": "🚨",
            "title": "Critical Incidents Require Attention",
            "message": f"{kpis.critical_incidents_24h} critical incidents in the last 24 hours. Immediate review recommended."
        })
    
    if kpis.compliance_score < 90:
        insights.append({
            "type": "caution",
            "icon": "⚠️",
            "title": "Compliance Score Below Target",
            "message": f"Current compliance score ({kpis.compliance_score:.0f}%) is below the 90% target. Review pending items."
        })
    
    if kpis.pending_reviews > 20:
        insights.append({
            "type": "info",
            "icon": "📋",
            "title": "High Volume of Pending Reviews",
            "message": f"{kpis.pending_reviews} items awaiting review. Consider additional resources."
        })
    
    if kpis.overall_security_score >= 90:
        insights.append({
            "type": "success",
            "icon": "✅",
            "title": "Strong Security Posture",
            "message": f"Security score of {kpis.overall_security_score:.0f}/100 indicates robust security controls."
        })
    
    if kpis.system_uptime < 99:
        insights.append({
            "type": "warning",
            "icon": "⚡",
            "title": "System Availability Below Target",
            "message": f"Uptime at {kpis.system_uptime:.1f}%, below 99% SLA target."
        })
    
    # Display insights
    if insights:
        cols = st.columns(min(len(insights), 3))
        for idx, insight in enumerate(insights[:3]):
            with cols[idx]:
                with st.container():
                    st.markdown(f"**{insight['icon']} {insight['title']}**")
                    st.caption(insight['message'])
                    
                    if insight['type'] == 'warning':
                        st.error("Action Required")
                    elif insight['type'] == 'caution':
                        st.warning("Review Recommended")
                    elif insight['type'] == 'success':
                        st.success("On Track")
                    else:
                        st.info("FYI")
    else:
        st.success("✅ All systems operating within normal parameters")
    
    # Export option
    st.divider()
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📊 Generate Executive Report", use_container_width=True):
            st.info("Executive report generation coming in Phase 4")
    with col2:
        if st.button("📧 Email Summary to Stakeholders", use_container_width=True):
            st.info("Email integration coming in Phase 4")

def _fetch_executive_kpis(openshell_service) -> ExecutiveKPIs:
    """Fetch executive KPIs."""
    
    # Mock data for demonstration
    return ExecutiveKPIs(
        overall_security_score=87.5,
        risk_trend="improving",
        critical_incidents_24h=1,
        compliance_score=94.0,
        active_threats=3,
        pending_reviews=15,
        system_uptime=99.7,
        agents_deployed=12,
        agents_compliant=11,
        data_requests_approved=145,
        data_requests_denied=8
    )

def _fetch_security_trends(openshell_service) -> List[SecurityTrend]:
    """Fetch security trend data for last 30 days."""
    
    trends = []
    now = datetime.now()
    
    # Generate 30 days of mock trend data
    import random
    base_score = 85
    
    for i in range(30):
        day = now - timedelta(days=29-i)
        # Add some realistic variation
        score_variation = random.gauss(0, 3)
        incident_chance = random.random()
        
        trends.append(SecurityTrend(
            timestamp=day,
            security_score=max(60, min(100, base_score + score_variation)),
            incident_count=1 if incident_chance > 0.8 else 0,
            compliance_score=max(85, min(100, 92 + random.gauss(0, 2)))
        ))
    
    return trends
