"""Policy Management component for CISO Dashboard.

Configure and manage security policies, rules, and enforcement settings.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class PolicyType(Enum):
    """Types of security policies."""
    NETWORK = "Network Policy"
    DATA = "Data Protection"
    ACCESS = "Access Control"
    AUDIT = "Audit & Logging"
    RATE_LIMIT = "Rate Limiting"
    CONTENT = "Content Filtering"
    ENCRYPTION = "Encryption"

class PolicyStatus(Enum):
    """Policy status."""
    ACTIVE = "active"
    DRAFT = "draft"
    DISABLED = "disabled"
    PENDING = "pending_review"

class EnforcementMode(Enum):
    """Policy enforcement mode."""
    ENFORCE = "enforce"      # Block violations
    AUDIT = "audit"          # Log only
    WARN = "warn"            # Allow with warning

@dataclass
class PolicyRule:
    """Individual policy rule."""
    id: str
    name: str
    description: str
    policy_type: PolicyType
    status: PolicyStatus
    enforcement: EnforcementMode
    priority: int
    conditions: Dict[str, any]
    actions: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int
    enabled: bool

@dataclass
class PolicyStats:
    """Policy statistics."""
    total_policies: int
    active_policies: int
    violations_24h: int
    avg_enforcement_rate: float
    top_triggered: List[tuple[str, int]]

def render_policy_management(
    openshell_service,
    instance_id: str
):
    """Render policy management interface."""
    
    # Fetch policies
    stats = _fetch_policy_stats(openshell_service)
    policies = _fetch_policies(openshell_service)
    
    # Header stats
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Policies", stats.total_policies)
    with col2:
        st.metric("Active", stats.active_policies)
    with col3:
        color = "inverse" if stats.violations_24h > 10 else "normal"
        st.metric("Violations (24h)", stats.violations_24h, delta_color=color)
    with col4:
        st.metric("Enforcement Rate", f"{stats.avg_enforcement_rate:.0f}%")
    
    st.divider()
    
    # Policy categories
    st.subheader("Policy Categories")
    _render_policy_categories(policies)
    
    st.divider()
    
    # Policy list
    st.subheader("Policy Rules")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect(
            "Policy Type",
            options=[t.value for t in PolicyType],
            default=[],
            key="policy_type_filter"
        )
    with col2:
        status_filter = st.multiselect(
            "Status",
            options=[s.value for s in PolicyStatus],
            default=[PolicyStatus.ACTIVE.value],
            key="policy_status_filter"
        )
    with col3:
        enforcement_filter = st.multiselect(
            "Enforcement",
            options=[e.value for e in EnforcementMode],
            default=[],
            key="policy_enforcement_filter"
        )
    
    # Filter policies
    filtered = policies
    if type_filter:
        filtered = [p for p in filtered if p.policy_type.value in type_filter]
    if status_filter:
        filtered = [p for p in filtered if p.status.value in status_filter]
    if enforcement_filter:
        filtered = [p for p in filtered if p.enforcement.value in enforcement_filter]
    
    # Add new policy button
    st.divider()
    if st.button("➕ Create New Policy", type="primary"):
        _render_policy_wizard()
    
    # Display policies
    st.divider()
    for policy in filtered:
        _render_policy_card(policy)
    
    if not filtered:
        st.info("No policies match the selected filters")

def _render_policy_categories(policies: List[PolicyRule]):
    """Render policy category summary."""
    
    # Count by type
    type_counts = {}
    type_active = {}
    for policy in policies:
        pt = policy.policy_type
        type_counts[pt] = type_counts.get(pt, 0) + 1
        if policy.status == PolicyStatus.ACTIVE:
            type_active[pt] = type_active.get(pt, 0) + 1
    
    cols = st.columns(min(len(type_counts), 4))
    
    for idx, (policy_type, total) in enumerate(type_counts.items()):
        with cols[idx % 4]:
            with st.container():
                active = type_active.get(policy_type, 0)
                st.markdown(f"**{policy_type.value}**")
                st.write(f"{active}/{total} Active")
                st.progress(active / total if total > 0 else 0)

def _render_policy_card(policy: PolicyRule):
    """Render individual policy card."""
    
    status_colors = {
        PolicyStatus.ACTIVE: "🟢",
        PolicyStatus.DRAFT: "🟡",
        PolicyStatus.DISABLED: "⚪",
        PolicyStatus.PENDING: "🟠"
    }
    
    enforcement_icons = {
        EnforcementMode.ENFORCE: "🚫",
        EnforcementMode.AUDIT: "👁️",
        EnforcementMode.WARN: "⚠️"
    }
    
    status_icon = status_colors.get(policy.status, "⚪")
    enforce_icon = enforcement_icons.get(policy.enforcement, "⚙️")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 2])
        
        with col1:
            st.write(f"**{status_icon}**")
            if policy.enabled:
                st.caption("🟢 Enabled")
            else:
                st.caption("⚪ Disabled")
        
        with col2:
            st.write(f"**{policy.name}**")
            st.caption(f"{policy.policy_type.value} | v{policy.version}")
            st.caption(policy.description[:80] + "..." if len(policy.description) > 80 else policy.description)
        
        with col3:
            st.write(f"**{enforce_icon} {policy.enforcement.value.upper()}**")
            st.caption(f"Priority: {policy.priority}")
            st.caption(f"Updated: {policy.updated_at.strftime('%Y-%m-%d')}")
        
        with st.expander("📋 Policy Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Policy Information**")
                st.write(f"**ID:** `{policy.id}`")
                st.write(f"**Type:** {policy.policy_type.value}")
                st.write(f"**Status:** {policy.status.value.replace('_', ' ').title()}")
                st.write(f"**Enforcement:** {policy.enforcement.value.title()}")
                st.write(f"**Priority:** {policy.priority}")
                st.write(f"**Version:** {policy.version}")
            
            with col2:
                st.markdown("**Metadata**")
                st.write(f"**Created By:** {policy.created_by}")
                st.write(f"**Created:** {policy.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Updated:** {policy.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            st.markdown("**Conditions**")
            st.json(policy.conditions)
            
            st.markdown("**Actions**")
            for action in policy.actions:
                st.write(f"- {action}")
            
            # Action buttons
            st.divider()
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                if policy.enabled:
                    if st.button("⏸️ Disable", key=f"disable_{policy.id}", use_container_width=True):
                        st.info(f"Disabling {policy.name} - coming in Phase 4")
                else:
                    if st.button("▶️ Enable", key=f"enable_{policy.id}", use_container_width=True):
                        st.info(f"Enabling {policy.name} - coming in Phase 4")
            
            with btn_col2:
                if st.button("✏️ Edit", key=f"edit_{policy.id}", use_container_width=True):
                    st.info(f"Editing {policy.name} - coming in Phase 4")
            
            with btn_col3:
                if st.button("🗑️ Delete", key=f"delete_{policy.id}", use_container_width=True):
                    st.warning(f"Deleting {policy.name} - coming in Phase 4")
        
        st.divider()

def _render_policy_wizard():
    """Render policy creation wizard."""
    
    with st.expander("➕ Create New Policy", expanded=True):
        st.subheader("Policy Configuration")
        
        # Basic info
        policy_name = st.text_input("Policy Name", placeholder="e.g., Block External Uploads")
        policy_type = st.selectbox(
            "Policy Type",
            options=[t for t in PolicyType],
            format_func=lambda x: x.value
        )
        
        policy_description = st.text_area("Description", placeholder="Describe what this policy enforces...")
        
        # Enforcement settings
        col1, col2, col3 = st.columns(3)
        with col1:
            enforcement = st.selectbox(
                "Enforcement Mode",
                options=[e for e in EnforcementMode],
                format_func=lambda x: x.value.title()
            )
        with col2:
            priority = st.slider("Priority", min_value=1, max_value=100, value=50)
        with col3:
            status = st.selectbox(
                "Initial Status",
                options=[PolicyStatus.DRAFT, PolicyStatus.ACTIVE],
                format_func=lambda x: x.value.replace('_', ' ').title()
            )
        
        # Conditions builder
        st.divider()
        st.subheader("Conditions")
        st.caption("Define when this policy applies")
        
        condition_type = st.selectbox(
            "Condition Type",
            options=["Domain Match", "Data Size", "Request Type", "User Role", "Time of Day"]
        )
        
        if condition_type == "Domain Match":
            domain_pattern = st.text_input("Domain Pattern", placeholder="*.example.com")
            match_type = st.selectbox("Match Type", ["Block", "Allow", "Monitor"])
        elif condition_type == "Data Size":
            max_size = st.number_input("Max Size (MB)", min_value=1, max_value=10000, value=100)
        elif condition_type == "Request Type":
            request_types = st.multiselect(
                "Request Types",
                options=["GET", "POST", "PUT", "DELETE", "PATCH"]
            )
        
        # Actions
        st.divider()
        st.subheader("Actions")
        actions = st.multiselect(
            "Select Actions",
            options=["Block Request", "Log Event", "Send Alert", "Rate Limit", "Quarantine", "Notify Admin"],
            default=["Block Request", "Log Event"]
        )
        
        # Create button
        if st.button("🚀 Create Policy", type="primary", use_container_width=True):
            if policy_name:
                st.success(f"Policy '{policy_name}' created successfully!")
                st.info("Policy will be active after review - coming in Phase 4")
            else:
                st.error("Please provide a policy name")

def _fetch_policy_stats(openshell_service) -> PolicyStats:
    """Fetch policy statistics."""
    
    return PolicyStats(
        total_policies=24,
        active_policies=18,
        violations_24h=47,
        avg_enforcement_rate=94.5,
        top_triggered=[
            ("Block External Domains", 156),
            ("Rate Limit API", 89),
            ("Data Exfiltration", 34),
            ("Suspicious Patterns", 23)
        ]
    )

def _fetch_policies(openshell_service) -> List[PolicyRule]:
    """Fetch security policies."""
    
    now = datetime.now()
    
    return [
        PolicyRule(
            id="POL-001",
            name="Block External Domain Access",
            description="Prevents sandboxes from accessing unauthorized external domains",
            policy_type=PolicyType.NETWORK,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.ENFORCE,
            priority=90,
            conditions={
                "domain_whitelist": ["api.internal.com", "logs.internal.com"],
                "action": "block_if_not_in_list"
            },
            actions=["Block Request", "Log Event", "Send Alert"],
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=2),
            created_by="admin@company.com",
            version=3,
            enabled=True
        ),
        PolicyRule(
            id="POL-002",
            name="Data Exfiltration Prevention",
            description="Detects and blocks attempts to exfiltrate sensitive data",
            policy_type=PolicyType.DATA,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.ENFORCE,
            priority=100,
            conditions={
                "patterns": ["credit_card", "ssn", "api_key"],
                "max_size": "10MB",
                "destinations": ["external"]
            },
            actions=["Block Request", "Quarantine", "Notify Admin"],
            created_at=now - timedelta(days=45),
            updated_at=now - timedelta(days=5),
            created_by="security@company.com",
            version=5,
            enabled=True
        ),
        PolicyRule(
            id="POL-003",
            name="Rate Limiting",
            description="Limits request rate to prevent abuse",
            policy_type=PolicyType.RATE_LIMIT,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.ENFORCE,
            priority=70,
            conditions={
                "requests_per_minute": 100,
                "burst_allowance": 20
            },
            actions=["Rate Limit", "Log Event"],
            created_at=now - timedelta(days=60),
            updated_at=now - timedelta(days=10),
            created_by="ops@company.com",
            version=2,
            enabled=True
        ),
        PolicyRule(
            id="POL-004",
            name="Prompt Injection Detection",
            description="Monitors for potential prompt injection attacks",
            policy_type=PolicyType.CONTENT,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.ENFORCE,
            priority=95,
            conditions={
                "patterns": ["ignore previous", "override instructions", "system prompt leak"],
                "confidence_threshold": 0.8
            },
            actions=["Block Request", "Send Alert", "Log Event"],
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=1),
            created_by="security@company.com",
            version=1,
            enabled=True
        ),
        PolicyRule(
            id="POL-005",
            name="Encryption at Rest",
            description="Enforces encryption for all stored data",
            policy_type=PolicyType.ENCRYPTION,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.AUDIT,
            priority=80,
            conditions={
                "encryption_required": True,
                "allowed_algorithms": ["AES-256", "ChaCha20"]
            },
            actions=["Log Event", "Send Alert"],
            created_at=now - timedelta(days=90),
            updated_at=now - timedelta(days=15),
            created_by="compliance@company.com",
            version=4,
            enabled=True
        ),
        PolicyRule(
            id="POL-006",
            name="Admin Access Monitoring",
            description="Enhanced logging for administrative access",
            policy_type=PolicyType.AUDIT,
            status=PolicyStatus.DRAFT,
            enforcement=EnforcementMode.AUDIT,
            priority=60,
            conditions={
                "roles": ["admin", "superuser"],
                "log_level": "verbose"
            },
            actions=["Log Event"],
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=5),
            created_by="admin@company.com",
            version=1,
            enabled=False
        ),
        PolicyRule(
            id="POL-007",
            name="API Key Rotation Policy",
            description="Enforces regular API key rotation",
            policy_type=PolicyType.ACCESS,
            status=PolicyStatus.PENDING,
            enforcement=EnforcementMode.WARN,
            priority=75,
            conditions={
                "max_key_age_days": 90,
                "warning_at_days": 75
            },
            actions=["Send Alert", "Log Event"],
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=3),
            created_by="security@company.com",
            version=2,
            enabled=False
        ),
        PolicyRule(
            id="POL-008",
            name="Sandbox Resource Limits",
            description="Enforces CPU and memory limits on sandboxes",
            policy_type=PolicyType.ACCESS,
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementMode.ENFORCE,
            priority=50,
            conditions={
                "max_memory_gb": 8,
                "max_cpu_cores": 4,
                "max_runtime_hours": 24
            },
            actions=["Rate Limit", "Block Request"],
            created_at=now - timedelta(days=120),
            updated_at=now - timedelta(days=20),
            created_by="ops@company.com",
            version=6,
            enabled=True
        )
    ]
