"""Agent Reputation Scoring System for SecOps Dashboard.

Tracks and displays agent behavior scores, risk history, and reputation trends.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ReputationLevel(Enum):
    """Reputation score levels."""
    TRUSTED = "trusted"      # 90-100
    GOOD = "good"            # 70-89
    NEUTRAL = "neutral"      # 50-69
    SUSPICIOUS = "suspicious" # 30-49
    HIGH_RISK = "high_risk"   # 0-29

@dataclass
class AgentReputation:
    sandbox_id: str
    sandbox_name: str
    current_score: float  # 0-100
    previous_score: float
    level: ReputationLevel
    requests_approved: int
    requests_denied: int
    policy_violations: int
    last_updated: datetime
    
    # Historical data for charts
    score_history: List[tuple[datetime, float]]  # (timestamp, score)
    
    # Risk factors
    risk_factors: Dict[str, float]  # {factor: weight}

# Level styling
LEVEL_COLORS = {
    ReputationLevel.TRUSTED: ("🟢", "#00C851", "Trusted"),
    ReputationLevel.GOOD: ("🟢", "#76B900", "Good Standing"),
    ReputationLevel.NEUTRAL: ("🟡", "#ffbb33", "Neutral"),
    ReputationLevel.SUSPICIOUS: ("🟠", "#ff8800", "Suspicious"),
    ReputationLevel.HIGH_RISK: ("🔴", "#ff4444", "High Risk")
}

def _get_level(score: float) -> ReputationLevel:
    """Determine reputation level from score."""
    if score >= 90:
        return ReputationLevel.TRUSTED
    elif score >= 70:
        return ReputationLevel.GOOD
    elif score >= 50:
        return ReputationLevel.NEUTRAL
    elif score >= 30:
        return ReputationLevel.SUSPICIOUS
    else:
        return ReputationLevel.HIGH_RISK

def render_reputation_dashboard(
    openshell_service,
    instance_id: str
):
    """Render the agent reputation dashboard."""
    
    # Fetch reputation data
    agents = _fetch_agent_reputations(openshell_service)
    
    if not agents:
        st.info("No agents with reputation data available.")
        return
    
    # Summary metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    avg_score = sum(a.current_score for a in agents) / len(agents)
    trusted_count = sum(1 for a in agents if a.level == ReputationLevel.TRUSTED)
    high_risk_count = sum(1 for a in agents if a.level in [ReputationLevel.SUSPICIOUS, ReputationLevel.HIGH_RISK])
    total_violations = sum(a.policy_violations for a in agents)
    
    with col1:
        color = "normal" if avg_score >= 70 else "inverse"
        st.metric("Avg Reputation", f"{avg_score:.1f}/100", delta_color=color)
    
    with col2:
        st.metric("Trusted Agents", trusted_count)
    
    with col3:
        delta_color = "inverse" if high_risk_count > 0 else "normal"
        st.metric("High Risk", high_risk_count, delta_color=delta_color)
    
    with col4:
        delta_color = "inverse" if total_violations > 0 else "normal"
        st.metric("Total Violations", total_violations, delta_color=delta_color)
    
    st.divider()
    
    # Agent reputation list
    st.subheader("Agent Reputation Status")
    
    # Sort by score (lowest first to highlight problematic agents)
    agents_sorted = sorted(agents, key=lambda a: a.current_score)
    
    for agent in agents_sorted:
        _render_agent_reputation_card(agent)
    
    # Historical trends
    st.divider()
    st.subheader("📈 Reputation Trends")
    
    _render_reputation_trends(agents)

def _render_agent_reputation_card(agent: AgentReputation):
    """Render a single agent reputation card."""
    
    icon, color, description = LEVEL_COLORS[agent.level]
    
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        
        with col1:
            st.write(f"**{icon} {agent.sandbox_name}**")
            st.caption(f"ID: {agent.sandbox_id[:12]}...")
        
        with col2:
            # Score display with color-coded progress
            st.progress(agent.current_score / 100, text=f"{agent.current_score:.0f}/100")
            delta = agent.current_score - agent.previous_score
            if delta > 0:
                st.caption(f"📈 +{delta:.1f} from last check")
            elif delta < 0:
                st.caption(f"📉 {delta:.1f} from last check")
            else:
                st.caption("➡️ No change")
        
        with col3:
            st.write(f"**{agent.level.value.upper()}**")
            st.caption(description)
        
        with col4:
            # Stats
            st.write(f"✅ {agent.requests_approved} approved")
            st.write(f"❌ {agent.requests_denied} denied")
            st.write(f"⚠️ {agent.policy_violations} violations")
        
        # Risk factors
        with st.expander("🔍 Risk Analysis", expanded=False):
            _render_risk_factors(agent.risk_factors, agent.score_history)
        
        st.divider()

def _render_risk_factors(
    risk_factors: Dict[str, float],
    score_history: List[tuple[datetime, float]]
):
    """Render risk factor breakdown and score history."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Risk Factors**")
        
        # Display risk factors as horizontal bars
        for factor, weight in sorted(risk_factors.items(), key=lambda x: x[1], reverse=True):
            color = "red" if weight > 50 else "orange" if weight > 25 else "yellow"
            st.write(f"{factor.replace('_', ' ').title()}: {weight:.0f}%")
            st.progress(weight / 100)
    
    with col2:
        st.markdown("**Score History (24h)**")
        
        if score_history:
            # Create mini trend chart
            times = [t[0] for t in score_history]
            scores = [t[1] for t in score_history]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=scores,
                mode='lines+markers',
                line=dict(color='#76B900', width=2),
                marker=dict(size=4),
                name='Reputation Score'
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(range=[0, 100]),
                showlegend=False,
                font=dict(size=10)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No history available")

def _render_reputation_trends(agents: List[AgentReputation]):
    """Render overall reputation trends chart."""
    
    # Create subplot for each agent
    n_agents = min(len(agents), 4)  # Show max 4 agents
    
    if n_agents == 0:
        return
    
    fig = make_subplots(
        rows=(n_agents + 1) // 2,
        cols=2,
        subplot_titles=[a.sandbox_name for a in agents[:n_agents]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    for idx, agent in enumerate(agents[:n_agents]):
        row = idx // 2 + 1
        col = idx % 2 + 1
        
        if agent.score_history:
            times = [t[0] for t in agent.score_history]
            scores = [t[1] for t in agent.score_history]
            
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=scores,
                    mode='lines',
                    line=dict(color=LEVEL_COLORS[agent.level][1], width=2),
                    fill='tozeroy',
                    fillcolor=f"rgba{tuple(int(LEVEL_COLORS[agent.level][1].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        height=300 * ((n_agents + 1) // 2),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    # Update all y-axes
    for i in range(1, n_agents + 1):
        fig.update_yaxes(range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.divider()
    st.subheader("📊 Reputation Summary Table")
    
    data = []
    for agent in agents:
        icon, _, desc = LEVEL_COLORS[agent.level]
        data.append({
            "Agent": agent.sandbox_name,
            "Score": f"{agent.current_score:.0f}",
            "Level": f"{icon} {agent.level.value.title()}",
            "Approved": agent.requests_approved,
            "Denied": agent.requests_denied,
            "Violations": agent.policy_violations,
            "Last Updated": agent.last_updated.strftime("%H:%M:%S")
        })
    
    st.dataframe(data, use_container_width=True, hide_index=True)

def _fetch_agent_reputations(openshell_service) -> List[AgentReputation]:
    """Fetch agent reputation data from OpenShell service."""
    
    # Placeholder implementation with mock data
    now = datetime.now()
    
    # Generate score history
    def generate_history(base_score: float, num_points: int = 24) -> List[tuple[datetime, float]]:
        history = []
        for i in range(num_points):
            time = now - timedelta(hours=num_points - i)
            # Add some random variation
            import random
            variation = random.gauss(0, 5)
            score = max(0, min(100, base_score + variation))
            history.append((time, score))
        return history
    
    mock_agents = [
        AgentReputation(
            sandbox_id="sandbox-001",
            sandbox_name="Agent-Alpha",
            current_score=92.5,
            previous_score=91.0,
            level=ReputationLevel.TRUSTED,
            requests_approved=145,
            requests_denied=2,
            policy_violations=0,
            last_updated=now,
            score_history=generate_history(92.5),
            risk_factors={
                "request_frequency": 10,
                "external_domains": 15,
                "data_volume": 5,
                "error_rate": 5
            }
        ),
        AgentReputation(
            sandbox_id="sandbox-002",
            sandbox_name="Agent-Beta",
            current_score=78.3,
            previous_score=75.0,
            level=ReputationLevel.GOOD,
            requests_approved=89,
            requests_denied=12,
            policy_violations=3,
            last_updated=now,
            score_history=generate_history(78.3),
            risk_factors={
                "request_frequency": 25,
                "external_domains": 30,
                "data_volume": 20,
                "error_rate": 10
            }
        ),
        AgentReputation(
            sandbox_id="sandbox-003",
            sandbox_name="Agent-Gamma",
            current_score=45.2,
            previous_score=52.0,
            level=ReputationLevel.SUSPICIOUS,
            requests_approved=34,
            requests_denied=45,
            policy_violations=12,
            last_updated=now,
            score_history=generate_history(45.2),
            risk_factors={
                "request_frequency": 60,
                "external_domains": 75,
                "data_volume": 55,
                "error_rate": 40
            }
        ),
        AgentReputation(
            sandbox_id="sandbox-004",
            sandbox_name="Agent-Delta",
            current_score=22.1,
            previous_score=25.0,
            level=ReputationLevel.HIGH_RISK,
            requests_approved=5,
            requests_denied=67,
            policy_violations=28,
            last_updated=now,
            score_history=generate_history(22.1),
            risk_factors={
                "request_frequency": 80,
                "external_domains": 90,
                "data_volume": 85,
                "error_rate": 70
            }
        )
    ]
    
    return mock_agents
