"""Multi-tenant Instance Management for Enterprise Scale.

Phase 4: Enterprise Scale & Multi-User
Supports multiple organizations, teams, and isolated environments.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class TenantTier(Enum):
    """Tenant subscription tiers."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ResourceQuota:
    """Resource limits for tenants."""
    
    TIERS = {
        TenantTier.STARTER: {
            "max_instances": 3,
            "max_sandboxes_per_instance": 5,
            "max_users": 10,
            "max_storage_gb": 100,
            "max_gpu_hours_per_day": 24,
            "supports_multi_region": False,
            "supports_advanced_security": False
        },
        TenantTier.PROFESSIONAL: {
            "max_instances": 10,
            "max_sandboxes_per_instance": 20,
            "max_users": 50,
            "max_storage_gb": 500,
            "max_gpu_hours_per_day": 100,
            "supports_multi_region": True,
            "supports_advanced_security": True
        },
        TenantTier.ENTERPRISE: {
            "max_instances": 100,
            "max_sandboxes_per_instance": 100,
            "max_users": 500,
            "max_storage_gb": 5000,
            "max_gpu_hours_per_day": 1000,
            "supports_multi_region": True,
            "supports_advanced_security": True
        }
    }

@dataclass
class Tenant:
    """Organization/tenant entity."""
    id: str
    name: str
    domain: str
    tier: TenantTier
    created_at: datetime
    admin_email: str
    settings: Dict
    features: List[str]
    instances: List[str] = field(default_factory=list)
    users: List[str] = field(default_factory=list)
    
    def get_quota(self) -> Dict:
        """Get resource quota for tenant tier."""
        return ResourceQuota.TIERS.get(self.tier, ResourceQuota.TIERS[TenantTier.STARTER])
    
    def can_add_instance(self) -> bool:
        """Check if tenant can add more instances."""
        quota = self.get_quota()
        return len(self.instances) < quota["max_instances"]
    
    def can_add_user(self) -> bool:
        """Check if tenant can add more users."""
        quota = self.get_quota()
        return len(self.users) < quota["max_users"]

@dataclass
class Team:
    """Team within a tenant."""
    id: str
    tenant_id: str
    name: str
    description: str
    members: List[str]
    instance_access: List[str]  # Instances this team can access
    created_at: datetime

class TenantManager:
    """Manage multi-tenant environments."""
    
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._teams: Dict[str, Team] = {}
        self._init_demo_tenants()
    
    def _init_demo_tenants(self):
        """Initialize demo tenants."""
        now = datetime.now()
        
        # Demo tenant 1 - Enterprise
        self._tenants["tenant-001"] = Tenant(
            id="tenant-001",
            name="Acme Corporation",
            domain="acme.com",
            tier=TenantTier.ENTERPRISE,
            created_at=now - timedelta(days=365),
            admin_email="admin@acme.com",
            settings={
                "sso_enabled": True,
                "mfa_required": True,
                "audit_retention_days": 2555,  # 7 years
                "data_residency": "US"
            },
            features=["advanced_security", "multi_region", "custom_policies", "dedicated_support"],
            instances=["instance-001", "instance-002", "instance-003"],
            users=["user-001", "user-002", "user-003", "user-004", "user-005"]
        )
        
        # Demo tenant 2 - Professional
        self._tenants["tenant-002"] = Tenant(
            id="tenant-002",
            name="TechStart Inc",
            domain="techstart.io",
            tier=TenantTier.PROFESSIONAL,
            created_at=now - timedelta(days=180),
            admin_email="admin@techstart.io",
            settings={
                "sso_enabled": True,
                "mfa_required": False,
                "audit_retention_days": 365,
                "data_residency": "EU"
            },
            features=["multi_region", "standard_support"],
            instances=["instance-004", "instance-005"],
            users=["user-006", "user-007", "user-008"]
        )
        
        # Demo teams
        self._teams["team-001"] = Team(
            id="team-001",
            tenant_id="tenant-001",
            name="AI Research",
            description="Core AI research and development team",
            members=["user-001", "user-004"],
            instance_access=["instance-001", "instance-002"],
            created_at=now - timedelta(days=300)
        )
        
        self._teams["team-002"] = Team(
            id="team-002",
            tenant_id="tenant-001",
            name="Security Operations",
            description="SOC and security engineering team",
            members=["user-002", "user-003"],
            instance_access=["instance-001", "instance-002", "instance-003"],
            created_at=now - timedelta(days=250)
        )
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)
    
    def get_tenants(self) -> List[Tenant]:
        """Get all tenants."""
        return list(self._tenants.values())
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        for tenant in self._tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    def create_tenant(
        self,
        name: str,
        domain: str,
        tier: TenantTier,
        admin_email: str
    ) -> Tenant:
        """Create new tenant."""
        tenant = Tenant(
            id=f"tenant-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            domain=domain,
            tier=tier,
            created_at=datetime.now(),
            admin_email=admin_email,
            settings={},
            features=list(ResourceQuota.TIERS[tier].keys()),
            instances=[],
            users=[]
        )
        self._tenants[tenant.id] = tenant
        return tenant
    
    def update_tenant_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade/downgrade tenant tier."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.tier = new_tier
        # Update available features
        quota = ResourceQuota.TIERS[new_tier]
        tenant.features = [
            k for k in quota.keys()
            if isinstance(quota[k], bool) and quota[k]
        ]
        return True
    
    def get_teams_for_tenant(self, tenant_id: str) -> List[Team]:
        """Get all teams for a tenant."""
        return [t for t in self._teams.values() if t.tenant_id == tenant_id]
    
    def create_team(
        self,
        tenant_id: str,
        name: str,
        description: str,
        instance_access: List[str]
    ) -> Team:
        """Create new team."""
        team = Team(
            id=f"team-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            tenant_id=tenant_id,
            name=name,
            description=description,
            members=[],
            instance_access=instance_access,
            created_at=datetime.now()
        )
        self._teams[team.id] = team
        return team
    
    def add_user_to_team(self, team_id: str, user_id: str) -> bool:
        """Add user to team."""
        team = self._teams.get(team_id)
        if not team:
            return False
        if user_id not in team.members:
            team.members.append(user_id)
        return True
    
    def get_usage_report(self, tenant_id: str) -> Dict:
        """Get resource usage report for tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {}
        
        quota = tenant.get_quota()
        
        return {
            "instances": {
                "used": len(tenant.instances),
                "limit": quota["max_instances"],
                "percentage": (len(tenant.instances) / quota["max_instances"] * 100)
            },
            "users": {
                "used": len(tenant.users),
                "limit": quota["max_users"],
                "percentage": (len(tenant.users) / quota["max_users"] * 100)
            },
            "storage_gb": {
                "used": 45,  # Mock
                "limit": quota["max_storage_gb"],
                "percentage": (45 / quota["max_storage_gb"] * 100)
            }
        }

# Import for demo
from datetime import timedelta
