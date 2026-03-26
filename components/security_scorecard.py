"""Security Scorecard component for CISO Dashboard.

Provides comprehensive security posture metrics and risk assessment.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class SecurityDomain(Enum):
    """Security assessment domains."""
    IDENTITY = "Identity & Access"
    DATA = "Data Protection"
    NETWORK = "Network Security"
    ENDPOINT = "Endpoint Security"
    APPLICATION = "Application Security"
    INFRASTRUCTURE = "Infrastructure"
    MONITORING = "Monitoring & Logging"
    GOVERNANCE = "Governance & Compliance"

class RiskLevel(Enum):
    """Risk assessment levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

@dataclass
class SecurityMetric:
    """Individual security metric."""
    name: str
    domain: SecurityDomain
    score: float  # 0-100
    weight: float  # Importance weight
    benchmark: float  # Industry benchmark
    trend: str  # "up", "down", "stable"
    last_assessed: datetime

@dataclass
class RiskItem:
    """Identified risk item."""
    id: str
    title: str
    description: str
    domain: SecurityDomain
    level: RiskLevel
    probability: float  # 0-100
    impact: float  # 0-100
    risk_score: float  # Calculated: probability * impact / 100
    remediation_cost: str  # Low, Medium, High
    owner: str
    due_date: datetime
    status: str  # Open, In Progress, Mitigated

@dataclass
class SecurityPosture:
    """Overall security posture."""
    overall_score: float
    maturity_level: str
    total_controls: int
    implemented_controls: int
    critical_gaps: int
    high_risks: int
    last_assessment: datetime

DOMAIN_COLORS = {
    SecurityDomain.IDENTITY: "#ff6b6b",
    SecurityDomain.DATA: "#4ecdc4",
    SecurityDomain.NETWORK: "#45b7d1",
    SecurityDomain.ENDPOINT: "#96ceb4",
    SecurityDomain.APPLICATION: "#ffeaa7",
    SecurityDomain.INFRASTRUCTURE: "#dfe6e9",
    SecurityDomain.MONITORING: "#fd79a8",
    SecurityDomain.GOVERNANCE: "#a29bfe"
}

RISK_STYLES = {
    RiskLevel.CRITICAL: ("🔴", "#ff4444"),
    RiskLevel.HIGH: ("🟠", "#ff8800"),
    RiskLevel.MEDIUM: ("🟡", "#ffbb33"),
    RiskLevel.LOW: ("🟢", "#00C851"),
    RiskLevel.MINIMAL: ("⚪", "#grey")
}

def render_security_scorecard(
    openshell_service,
    instance_id: str
):
    """Render security scorecard dashboard."""
    
    # Fetch data
    posture = _fetch_security_posture(openshell_service)
    metrics = _fetch_security_metrics(openshell_service)
    risks = _fetch_risk_items(openshell_service)
    
    # Header metrics
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        score_color = "normal" if posture.overall_score >= 80 else "inverse"
        st.metric("Security Score", f"{posture.overall_score:.0f}/100", delta_color=score_color)
    with col2:
        st.metric("Maturity", posture.maturity_level)
    with col3:
        impl_pct = (posture.implemented_controls / posture.total_controls * 100) if posture.total_controls > 0 else 0
        st.metric("Controls", f"{posture.implemented_controls}/{posture.total_controls}", f"{impl_pct:.0f}%")
    with col4:
        color = "inverse" if posture.critical_gaps > 0 else "normal"
        st.metric("Critical Gaps", posture.critical_gaps, delta_color=color)
    with col5:
        color = "inverse" if posture.high_risks > 0 else "normal"
        st.metric("High Risks", posture.high_risks, delta_color=color)
    
    st.divider()
    
    # Domain scores radar chart
    _render_domain_radar(metrics)
    
    # Domain breakdown
    st.divider()
    st.subheader("Domain Breakdown")
    _render_domain_breakdown(metrics)
    
    # Risk register
    st.divider()
    st.subheader("🎯 Risk Register")
    _render_risk_register(risks)
    
    # Risk matrix
    st.divider()
    st.subheader("Risk Matrix")
    _render_risk_matrix(risks)

def _render_domain_radar(metrics: List[SecurityMetric]):
    """Render domain scores radar chart."""
    
    # Group by domain and calculate average
    domain_scores = {}
    for metric in metrics:
        if metric.domain not in domain_scores:
            domain_scores[metric.domain] = []
        domain_scores[metric.domain].append(metric.score)
    
    categories = list(domain_scores.keys())
    values = [sum(domain_scores[d]) / len(domain_scores[d]) for d in categories]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=[d.value for d in categories] + [categories[0].value],
        fill='toself',
        fillcolor='rgba(118, 185, 0, 0.3)',
        line=dict(color='#76B900', width=2),
        name='Current Score'
    ))
    
    # Add benchmark
    benchmarks = [metric.benchmark for metric in metrics[:len(categories)]]
    fig.add_trace(go.Scatterpolar(
        r=benchmarks + [benchmarks[0]],
        theta=[d.value for d in categories] + [categories[0].value],
        fill='toself',
        fillcolor='rgba(255, 68, 68, 0.1)',
        line=dict(color='#ff4444', width=1, dash='dash'),
        name='Industry Benchmark'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_domain_breakdown(metrics: List[SecurityMetric]):
    """Render domain score breakdown."""
    
    # Group by domain
    domain_data = {}
    for metric in metrics:
        if metric.domain not in domain_data:
            domain_data[metric.domain] = []
        domain_data[metric.domain].append(metric)
    
    cols = st.columns(min(len(domain_data), 4))
    
    for idx, (domain, domain_metrics) in enumerate(domain_data.items()):
        with cols[idx % 4]:
            avg_score = sum(m.score for m in domain_metrics) / len(domain_metrics)
            color = DOMAIN_COLORS.get(domain, "#76B900")
            
            with st.container():
                st.markdown(f"**{domain.value}**")
                
                # Mini gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=avg_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': color},
                        'bgcolor': "rgba(255,255,255,0.1)",
                        'steps': [
                            {'range': [0, 60], 'color': 'rgba(255, 68, 68, 0.2)'},
                            {'range': [60, 80], 'color': 'rgba(255, 187, 51, 0.2)'},
                            {'range': [80, 100], 'color': 'rgba(0, 200, 81, 0.2)'}
                        ]
                    }
                ))
                fig.update_layout(height=150, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Show metrics in this domain
                for m in domain_metrics:
                    trend_icon = "📈" if m.trend == "up" else "📉" if m.trend == "down" else "➡️"
                    st.caption(f"{trend_icon} {m.name}: {m.score:.0f}")

def _render_risk_register(risks: List[RiskItem]):
    """Render risk register table."""
    
    if not risks:
        st.success("✅ No risks registered. System secure.")
        return
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        level_filter = st.multiselect(
            "Risk Level",
            options=[l.value for l in RiskLevel],
            default=[RiskLevel.CRITICAL.value, RiskLevel.HIGH.value],
            key="risk_level_filter"
        )
    with col2:
        domain_filter = st.multiselect(
            "Domain",
            options=[d.value for d in SecurityDomain],
            default=[d.value for d in SecurityDomain],
            key="risk_domain_filter"
        )
    with col3:
        status_filter = st.multiselect(
            "Status",
            options=["Open", "In Progress", "Mitigated"],
            default=["Open", "In Progress"],
            key="risk_status_filter"
        )
    
    # Filter risks
    filtered = risks
    if level_filter:
        filtered = [r for r in filtered if r.level.value in level_filter]
    if domain_filter:
        filtered = [r for r in filtered if r.domain.value in domain_filter]
    if status_filter:
        filtered = [r for r in filtered if r.status in status_filter]
    
    # Sort by risk score (highest first)
    filtered = sorted(filtered, key=lambda r: r.risk_score, reverse=True)
    
    # Display risks
    if filtered:
        for risk in filtered:
            _render_risk_card(risk)
    else:
        st.success("✅ No risks match selected filters")

def _render_risk_card(risk: RiskItem):
    """Render individual risk card."""
    
    icon, color = RISK_STYLES[risk.level]
    
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.write(f"**{icon}**")
            st.caption(risk.level.value.upper())
        
        with col2:
            st.write(f"**{risk.id}: {risk.title}**")
            st.write(risk.description[:100] + "..." if len(risk.description) > 100 else risk.description)
            st.caption(f"Domain: {risk.domain.value} | Owner: {risk.owner}")
        
        with col3:
            st.write(f"**Score: {risk.risk_score:.0f}**")
            st.progress(risk.risk_score / 100, text=f"{risk.probability:.0f}% × {risk.impact:.0f} impact")
            st.caption(f"Due: {risk.due_date.strftime('%Y-%m-%d')} | Cost: {risk.remediation_cost}")
        
        with st.expander("📋 Risk Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Risk Assessment**")
                st.write(f"**Probability:** {risk.probability:.0f}%")
                st.write(f"**Impact:** {risk.impact:.0f}%")
                st.write(f"**Score:** {risk.risk_score:.0f}/100")
                st.write(f"**Status:** {risk.status}")
            with col2:
                st.markdown("**Remediation**")
                st.write(f"**Cost:** {risk.remediation_cost}")
                st.write(f"**Due Date:** {risk.due_date.strftime('%Y-%m-%d')}")
                st.write(f"**Owner:** {risk.owner}")
        
        st.divider()

def _render_risk_matrix(risks: List[RiskItem]):
    """Render probability-impact risk matrix."""
    
    # Create 5x5 matrix
    matrix = [[0 for _ in range(5)] for _ in range(5)]
    
    for risk in risks:
        if risk.status != "Mitigated":
            prob_idx = min(int(risk.probability / 20), 4)
            impact_idx = min(int(risk.impact / 20), 4)
            matrix[4 - prob_idx][impact_idx] += 1
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
        y=['Very High', 'High', 'Medium', 'Low', 'Very Low'],
        colorscale=[
            [0, '#00C851'],
            [0.25, '#ffbb33'],
            [0.5, '#ff8800'],
            [0.75, '#ff4444'],
            [1, '#ff4444']
        ],
        text=[[str(val) if val > 0 else '' for val in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 16},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Risk Matrix (Probability vs Impact)",
        xaxis_title="Impact",
        yaxis_title="Probability",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _fetch_security_posture(openshell_service) -> SecurityPosture:
    """Fetch overall security posture."""
    return SecurityPosture(
        overall_score=87.5,
        maturity_level="Level 4 - Managed",
        total_controls=156,
        implemented_controls=142,
        critical_gaps=2,
        high_risks=5,
        last_assessment=datetime.now() - timedelta(days=7)
    )

def _fetch_security_metrics(openshell_service) -> List[SecurityMetric]:
    """Fetch security metrics by domain."""
    now = datetime.now()
    
    return [
        SecurityMetric("MFA Coverage", SecurityDomain.IDENTITY, 95.0, 0.15, 85.0, "up", now),
        SecurityMetric("Access Reviews", SecurityDomain.IDENTITY, 88.0, 0.10, 80.0, "stable", now),
        SecurityMetric("Encryption at Rest", SecurityDomain.DATA, 100.0, 0.15, 95.0, "stable", now),
        SecurityMetric("DLP Coverage", SecurityDomain.DATA, 75.0, 0.15, 70.0, "up", now),
        SecurityMetric("Firewall Rules", SecurityDomain.NETWORK, 92.0, 0.10, 88.0, "stable", now),
        SecurityMetric("Network Segmentation", SecurityDomain.NETWORK, 85.0, 0.10, 80.0, "up", now),
        SecurityMetric("EDR Coverage", SecurityDomain.ENDPOINT, 98.0, 0.10, 90.0, "stable", now),
        SecurityMetric("Patch Management", SecurityDomain.ENDPOINT, 82.0, 0.10, 85.0, "down", now),
        SecurityMetric("Secure Coding", SecurityDomain.APPLICATION, 78.0, 0.05, 75.0, "up", now),
        SecurityMetric("Code Reviews", SecurityDomain.APPLICATION, 85.0, 0.05, 80.0, "stable", now),
        SecurityMetric("SIEM Coverage", SecurityDomain.MONITORING, 90.0, 0.05, 85.0, "stable", now),
        SecurityMetric("Log Retention", SecurityDomain.MONITORING, 95.0, 0.05, 90.0, "stable", now)
    ]

def _fetch_risk_items(openshell_service) -> List[RiskItem]:
    """Fetch risk register items."""
    now = datetime.now()
    
    return [
        RiskItem(
            id="RISK-001",
            title="Insufficient Data Classification",
            description="Lack of automated data classification may result in sensitive data exposure",
            domain=SecurityDomain.DATA,
            level=RiskLevel.HIGH,
            probability=70.0,
            impact=75.0,
            risk_score=52.5,
            remediation_cost="Medium",
            owner="Data Protection Team",
            due_date=now + timedelta(days=30),
            status="Open"
        ),
        RiskItem(
            id="RISK-002",
            title="Legacy System Vulnerabilities",
            description="Critical legacy systems lack security patches and modern security controls",
            domain=SecurityDomain.INFRASTRUCTURE,
            level=RiskLevel.CRITICAL,
            probability=60.0,
            impact=90.0,
            risk_score=54.0,
            remediation_cost="High",
            owner="Infrastructure Team",
            due_date=now + timedelta(days=14),
            status="In Progress"
        ),
        RiskItem(
            id="RISK-003",
            title="Third-Party Access Risk",
            description="Vendor access lacks sufficient monitoring and controls",
            domain=SecurityDomain.IDENTITY,
            level=RiskLevel.MEDIUM,
            probability=50.0,
            impact=60.0,
            risk_score=30.0,
            remediation_cost="Low",
            owner="Vendor Management",
            due_date=now + timedelta(days=60),
            status="Open"
        ),
        RiskItem(
            id="RISK-004",
            title="Incomplete Log Monitoring",
            description="Some critical systems not sending logs to SIEM",
            domain=SecurityDomain.MONITORING,
            level=RiskLevel.HIGH,
            probability=65.0,
            impact=70.0,
            risk_score=45.5,
            remediation_cost="Medium",
            owner="Security Operations",
            due_date=now + timedelta(days=21),
            status="In Progress"
        )
    ]
