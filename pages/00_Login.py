"""Login Page for NemoClaw Gateway.

Phase 4: Enterprise authentication and SSO.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.auth_service import auth_manager, UserRole, AuthProvider

st.set_page_config(
    page_title="Login - NemoClaw Gateway",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar on login page
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Centered login container
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("🔐 NemoClaw Gateway")
    st.caption("Enterprise AI Agent Orchestration Platform")
    
    st.divider()
    
    # Already authenticated?
    if st.session_state.get('authenticated'):
        st.success(f"✅ Already logged in as {st.session_state['user'].name}")
        if st.button("Continue to Dashboard", use_container_width=True):
            st.switch_page("app.py")
        st.stop()
    
    # Login method tabs
    tab1, tab2 = st.tabs(["🔑 Email/Password", "🏢 Single Sign-On"])
    
    with tab1:
        email = st.text_input("Email", placeholder="user@company.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember = st.checkbox("Remember me", value=True)
        with col2:
            st.caption("[Forgot password?]")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if email and password:
                user = auth_manager.authenticate(email, password)
                if user:
                    st.session_state['user'] = user
                    st.session_state['authenticated'] = True
                    st.success(f"Welcome back, {user.name}! 👋")
                    st.balloons()
                    st.switch_page("app.py")
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.warning("Please enter both email and password")
    
    with tab2:
        st.info("Connect with your organization's identity provider")
        
        provider = st.selectbox(
            "Select Provider",
            options=["Azure Active Directory", "Okta", "Google Workspace", "OneLogin", "Ping Identity"],
            key="sso_provider"
        )
        
        if st.button(f"Sign in with {provider}", type="primary", use_container_width=True):
            with st.spinner(f"Redirecting to {provider}..."):
                # In production: redirect to OAuth2/SAML flow
                import time
                time.sleep(1)
            
            # Mock successful SSO login
            user = auth_manager._users.get("user-002")  # CISO user
            auth_manager._current_user = user
            st.session_state['user'] = user
            st.session_state['authenticated'] = True
            st.success(f"Welcome, {user.name}! 👋")
            st.switch_page("app.py")
    
    st.divider()
    
    # Demo quick login
    with st.expander("🧪 Demo Mode - Quick Login", expanded=False):
        st.caption("Select a role to test the dashboard:")
        
        demo_users = [
            ("👤 System Administrator", "user-001", "Full system access"),
            ("🛡️ CISO", "user-002", "Security & compliance"),
            ("🔒 SecOps Analyst", "user-003", "Security operations"),
            ("⚙️ AI Engineer", "user-004", "Sandbox management"),
            ("📖 Auditor", "user-005", "Read-only access")
        ]
        
        for name, user_id, description in demo_users:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{name}** - {description}")
            with col2:
                if st.button("Login", key=f"demo_{user_id}"):
                    user = auth_manager._users.get(user_id)
                    auth_manager._current_user = user
                    st.session_state['user'] = user
                    st.session_state['authenticated'] = True
                    st.switch_page("app.py")
    
    st.divider()
    st.caption("© 2024 NemoClaw Gateway - v2.1.0")
    st.caption("Secure by Design • Zero Trust Architecture")
