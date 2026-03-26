"""Authentication and User Management for NemoClaw Gateway.

Phase 4: Enterprise Scale & Multi-User
Provides authentication, user roles, and access control.
"""

import streamlit as st
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets

class UserRole(Enum):
    """User roles with different permissions."""
    ADMIN = "admin"           # Full access
    CISO = "ciso"             # Security/compliance view
    SECOPS = "secops"         # Security operations
    ENGINEER = "engineer"     # Sandbox management
    VIEWER = "viewer"         # Read-only access

class AuthProvider(Enum):
    """Authentication providers."""
    LOCAL = "local"           # Built-in authentication
    OAUTH2 = "oauth2"         # OAuth2 / SSO
    SAML = "saml"             # SAML 2.0
    LDAP = "ldap"             # LDAP/Active Directory

@dataclass
class User:
    """User entity."""
    id: str
    email: str
    name: str
    role: UserRole
    auth_provider: AuthProvider
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    mfa_enabled: bool
    preferences: Dict

@dataclass
class Session:
    """User session."""
    id: str
    user_id: str
    started_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_valid: bool

class Permission:
    """Permission definitions."""
    VIEW_SANDBOXES = "view_sandboxes"
    CREATE_SANDBOX = "create_sandbox"
    DELETE_SANDBOX = "delete_sandbox"
    START_STOP_SANDBOX = "start_stop_sandbox"
    VIEW_LOGS = "view_logs"
    VIEW_GPU_METRICS = "view_gpu_metrics"
    VIEW_REQUEST_QUEUE = "view_request_queue"
    APPROVE_REQUESTS = "approve_requests"
    VIEW_SECURITY_ALERTS = "view_security_alerts"
    ACKNOWLEDGE_ALERTS = "acknowledge_alerts"
    VIEW_COMPLIANCE = "view_compliance"
    MANAGE_POLICIES = "manage_policies"
    VIEW_AUDIT_TRAIL = "view_audit_trail"
    MANAGE_USERS = "manage_users"
    MANAGE_INSTANCES = "manage_instances"
    SYSTEM_ADMIN = "system_admin"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.SYSTEM_ADMIN,
        Permission.MANAGE_USERS,
        Permission.MANAGE_INSTANCES,
        Permission.MANAGE_POLICIES,
        Permission.VIEW_AUDIT_TRAIL,
        Permission.VIEW_COMPLIANCE,
        Permission.ACKNOWLEDGE_ALERTS,
        Permission.VIEW_SECURITY_ALERTS,
        Permission.APPROVE_REQUESTS,
        Permission.VIEW_REQUEST_QUEUE,
        Permission.VIEW_GPU_METRICS,
        Permission.VIEW_LOGS,
        Permission.START_STOP_SANDBOX,
        Permission.DELETE_SANDBOX,
        Permission.CREATE_SANDBOX,
        Permission.VIEW_SANDBOXES
    ],
    UserRole.CISO: [
        Permission.VIEW_AUDIT_TRAIL,
        Permission.VIEW_COMPLIANCE,
        Permission.VIEW_SECURITY_ALERTS,
        Permission.VIEW_REQUEST_QUEUE,
        Permission.VIEW_GPU_METRICS,
        Permission.VIEW_LOGS,
        Permission.VIEW_SANDBOXES
    ],
    UserRole.SECOPS: [
        Permission.ACKNOWLEDGE_ALERTS,
        Permission.VIEW_SECURITY_ALERTS,
        Permission.APPROVE_REQUESTS,
        Permission.VIEW_REQUEST_QUEUE,
        Permission.VIEW_LOGS,
        Permission.VIEW_SANDBOXES,
        Permission.START_STOP_SANDBOX
    ],
    UserRole.ENGINEER: [
        Permission.CREATE_SANDBOX,
        Permission.DELETE_SANDBOX,
        Permission.START_STOP_SANDBOX,
        Permission.VIEW_LOGS,
        Permission.VIEW_GPU_METRICS,
        Permission.VIEW_SANDBOXES
    ],
    UserRole.VIEWER: [
        Permission.VIEW_SANDBOXES,
        Permission.VIEW_LOGS,
        Permission.VIEW_GPU_METRICS
    ]
}

class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._current_user: Optional[User] = None
        self._init_default_users()
    
    def _init_default_users(self):
        """Initialize default users for demonstration."""
        now = datetime.now()
        
        default_users = [
            User(
                id="user-001",
                email="admin@company.com",
                name="System Administrator",
                role=UserRole.ADMIN,
                auth_provider=AuthProvider.LOCAL,
                created_at=now,
                last_login=now - timedelta(hours=1),
                is_active=True,
                mfa_enabled=True,
                preferences={"theme": "dark", "notifications": True}
            ),
            User(
                id="user-002",
                email="ciso@company.com",
                name="Chief Information Security Officer",
                role=UserRole.CISO,
                auth_provider=AuthProvider.OAUTH2,
                created_at=now - timedelta(days=30),
                last_login=now - timedelta(hours=2),
                is_active=True,
                mfa_enabled=True,
                preferences={"theme": "dark", "dashboard": "executive"}
            ),
            User(
                id="user-003",
                email="secops@company.com",
                name="Security Operations Analyst",
                role=UserRole.SECOPS,
                auth_provider=AuthProvider.LOCAL,
                created_at=now - timedelta(days=15),
                last_login=now - timedelta(minutes=30),
                is_active=True,
                mfa_enabled=False,
                preferences={"theme": "light", "auto_refresh": True}
            ),
            User(
                id="user-004",
                email="engineer@company.com",
                name="AI Engineer",
                role=UserRole.ENGINEER,
                auth_provider=AuthProvider.OAUTH2,
                created_at=now - timedelta(days=7),
                last_login=now - timedelta(hours=4),
                is_active=True,
                mfa_enabled=True,
                preferences={"theme": "dark", "default_view": "sandbox"}
            ),
            User(
                id="user-005",
                email="viewer@company.com",
                name="Auditor",
                role=UserRole.VIEWER,
                auth_provider=AuthProvider.LOCAL,
                created_at=now - timedelta(days=1),
                last_login=None,
                is_active=True,
                mfa_enabled=False,
                preferences={"theme": "light"}
            )
        ]
        
        for user in default_users:
            self._users[user.id] = user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        # In production, verify against hashed passwords
        for user in self._users.values():
            if user.email == email and user.is_active:
                # Mock password check - in production use proper hashing
                user.last_login = datetime.now()
                self._current_user = user
                return user
        return None
    
    def authenticate_oauth(self, token: str, provider: AuthProvider) -> Optional[User]:
        """Authenticate with OAuth2/SAML token."""
        # Mock OAuth authentication
        # In production, validate token with identity provider
        return self._current_user
    
    def logout(self):
        """Logout current user."""
        self._current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Get currently authenticated user."""
        return self._current_user
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        return permission in user_permissions or Permission.SYSTEM_ADMIN in user_permissions
    
    def require_auth(self, permission: Optional[str] = None):
        """Decorator/requirement for authentication."""
        if not self._current_user:
            return False
        if permission and not self.has_permission(self._current_user, permission):
            return False
        return True
    
    def get_users(self) -> List[User]:
        """Get all users."""
        return list(self._users.values())
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def create_user(self, email: str, name: str, role: UserRole) -> User:
        """Create new user."""
        user = User(
            id=f"user-{secrets.token_hex(4)}",
            email=email,
            name=name,
            role=role,
            auth_provider=AuthProvider.LOCAL,
            created_at=datetime.now(),
            last_login=None,
            is_active=True,
            mfa_enabled=False,
            preferences={}
        )
        self._users[user.id] = user
        return user
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user properties."""
        user = self._users.get(user_id)
        if not user:
            return False
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Deactivate/delete user."""
        user = self._users.get(user_id)
        if user:
            user.is_active = False
            return True
        return False
    
    def change_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Change user role."""
        user = self._users.get(user_id)
        if user:
            user.role = new_role
            return True
        return False

# Global auth manager instance
auth_manager = AuthManager()

def render_login_page():
    """Render login page."""
    st.set_page_config(
        page_title="Login - NemoClaw Gateway",
        page_icon="🔐",
        layout="centered"
    )
    
    st.title("🔐 NemoClaw Gateway")
    st.subheader("Secure Login")
    
    # Login method tabs
    tab1, tab2 = st.tabs(["Email/Password", "Single Sign-On (SSO)"])
    
    with tab1:
        email = st.text_input("Email", placeholder="user@company.com")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user = auth_manager.authenticate(email, password)
            if user:
                st.session_state['user'] = user
                st.session_state['authenticated'] = True
                st.success(f"Welcome, {user.name}!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.info("SSO Authentication")
        provider = st.selectbox(
            "Identity Provider",
            options=["Okta", "Azure AD", "Google Workspace", "OneLogin"]
        )
        
        if st.button("Login with SSO", use_container_width=True):
            st.info(f"Redirecting to {provider}...")
            # In production, redirect to OAuth/SAML flow
    
    # Demo mode
    st.divider()
    st.caption("Demo Mode - Quick Login")
    
    demo_users = auth_manager.get_users()
    for user in demo_users:
        if st.button(f"Login as {user.name} ({user.role.value})", key=f"demo_{user.id}", use_container_width=True):
            auth_manager._current_user = user
            st.session_state['user'] = user
            st.session_state['authenticated'] = True
            st.rerun()

def require_auth(permission: Optional[str] = None):
    """Check authentication and authorization."""
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.error("🔒 Please log in to access this page")
        if st.button("Go to Login"):
            st.switch_page("pages/00_Login.py")
        st.stop()
    
    user = st.session_state.get('user')
    if permission and not auth_manager.has_permission(user, permission):
        st.error("⛔ You don't have permission to access this feature")
        st.stop()
    
    return user

def render_user_menu():
    """Render user menu in sidebar."""
    user = auth_manager.get_current_user()
    if user:
        with st.sidebar:
            st.divider()
            st.write(f"**{user.name}**")
            st.caption(f"Role: {user.role.value.title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout()
                st.session_state['authenticated'] = False
                st.session_state.pop('user', None)
                st.rerun()
