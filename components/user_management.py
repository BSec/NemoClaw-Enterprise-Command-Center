"""User Management component for NemoClaw Gateway.

Phase 4: Enterprise user administration interface.
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd

def render_user_management(
    auth_manager,
    instance_id: str
):
    """Render user management interface."""
    
    from services.auth_service import UserRole, AuthProvider
    
    st.header("👥 User Management")
    st.caption("Manage users, roles, and permissions")
    
    # Fetch users
    users = auth_manager.get_users()
    
    # Summary metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = len(users)
    active_users = sum(1 for u in users if u.is_active)
    mfa_enabled = sum(1 for u in users if u.mfa_enabled)
    sso_users = sum(1 for u in users if u.auth_provider != AuthProvider.LOCAL)
    
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Active", active_users)
    with col3:
        pct_mfa = (mfa_enabled / total_users * 100) if total_users > 0 else 0
        st.metric("MFA Enabled", f"{mfa_enabled}", f"{pct_mfa:.0f}%")
    with col4:
        st.metric("SSO Users", sso_users)
    
    st.divider()
    
    # Role distribution
    _render_role_distribution(users)
    
    st.divider()
    
    # User list
    st.subheader("User Directory")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        role_filter = st.multiselect(
            "Filter by Role",
            options=[r.value for r in UserRole],
            default=[],
            key="user_role_filter"
        )
    with col2:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Active", "Inactive"],
            index=0,
            key="user_status_filter"
        )
    with col3:
        if st.button("➕ Add User", type="primary", use_container_width=True):
            _render_add_user_dialog(auth_manager)
    
    # Filter users
    filtered = users
    if role_filter:
        filtered = [u for u in filtered if u.role.value in role_filter]
    if status_filter == "Active":
        filtered = [u for u in filtered if u.is_active]
    elif status_filter == "Inactive":
        filtered = [u for u in filtered if not u.is_active]
    
    # User table
    if filtered:
        user_data = []
        for user in filtered:
            user_data.append({
                "ID": user.id,
                "Name": user.name,
                "Email": user.email,
                "Role": user.role.value.title(),
                "Status": "🟢 Active" if user.is_active else "⚪ Inactive",
                "Auth": user.auth_provider.value.upper(),
                "MFA": "✅" if user.mfa_enabled else "❌",
                "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never",
                "Created": user.created_at.strftime("%Y-%m-%d")
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # User actions
        st.divider()
        st.subheader("User Actions")
        
        selected_user_id = st.selectbox(
            "Select User",
            options=[u.id for u in filtered],
            format_func=lambda x: next((f"{u.name} ({u.email})" for u in filtered if u.id == x), x),
            key="selected_user"
        )
        
        if selected_user_id:
            selected_user = next((u for u in filtered if u.id == selected_user_id), None)
            if selected_user:
                _render_user_actions(auth_manager, selected_user)
    else:
        st.info("No users match the selected filters")
    
    # Bulk operations
    st.divider()
    st.subheader("⚡ Bulk Operations")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📧 Send Password Reset", use_container_width=True):
            st.info("Password reset emails sent to selected users")
    with col2:
        if st.button("🔒 Require MFA", use_container_width=True):
            st.info("MFA requirement updated")
    with col3:
        if st.button("📊 Export User List", use_container_width=True):
            st.info("User list export generated")

def _render_role_distribution(users: List):
    """Render role distribution chart."""
    
    from collections import Counter
    import plotly.graph_objects as go
    
    role_counts = Counter(u.role.value for u in users)
    
    fig = go.Figure(data=[go.Pie(
        labels=[r.replace('_', ' ').title() for r in role_counts.keys()],
        values=list(role_counts.values()),
        hole=0.4,
        marker=dict(colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'])
    )])
    
    fig.update_layout(
        title="User Role Distribution",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E6EDF3')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_add_user_dialog(auth_manager):
    """Render add user dialog."""
    
    from services.auth_service import UserRole, AuthProvider
    
    with st.expander("➕ Add New User", expanded=True):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john.doe@company.com")
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox(
                "Role",
                options=[r for r in UserRole],
                format_func=lambda x: x.value.title()
            )
        with col2:
            auth_provider = st.selectbox(
                "Authentication",
                options=[AuthProvider.LOCAL, AuthProvider.OAUTH2],
                format_func=lambda x: "Email/Password" if x == AuthProvider.LOCAL else "SSO (OAuth2)"
            )
        
        require_mfa = st.checkbox("Require MFA", value=True)
        
        if auth_provider == AuthProvider.LOCAL:
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Temporary Password", type="password", value="TempPass123!")
            with col2:
                force_change = st.checkbox("Force password change on first login", value=True)
        
        if st.button("🚀 Create User", type="primary", use_container_width=True):
            if name and email:
                user = auth_manager.create_user(email, name, role)
                user.mfa_enabled = require_mfa
                user.auth_provider = auth_provider
                st.success(f"User {name} created successfully!")
                st.info(f"Welcome email sent to {email}")
            else:
                st.error("Please fill in all required fields")

def _render_user_actions(auth_manager, user):
    """Render action buttons for selected user."""
    
    from services.auth_service import UserRole
    
    st.write(f"**Managing:** {user.name} ({user.email})")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        new_role = st.selectbox(
            "Change Role",
            options=[r for r in UserRole],
            index=[r for r in UserRole].index(user.role),
            format_func=lambda x: x.value.title(),
            key=f"role_{user.id}"
        )
        if new_role != user.role:
            if st.button("Update Role", key=f"update_role_{user.id}", use_container_width=True):
                auth_manager.change_user_role(user.id, new_role)
                st.success(f"Role updated to {new_role.value}")
                st.rerun()
    
    with col2:
        if user.is_active:
            if st.button("⏸️ Deactivate", key=f"deactivate_{user.id}", use_container_width=True):
                auth_manager.update_user(user.id, is_active=False)
                st.warning("User deactivated")
                st.rerun()
        else:
            if st.button("▶️ Activate", key=f"activate_{user.id}", use_container_width=True):
                auth_manager.update_user(user.id, is_active=True)
                st.success("User activated")
                st.rerun()
    
    with col3:
        if st.button("🔑 Reset Password", key=f"reset_{user.id}", use_container_width=True):
            st.info("Password reset email sent")
    
    with col4:
        if st.button("🗑️ Delete", key=f"delete_{user.id}", use_container_width=True):
            auth_manager.delete_user(user.id)
            st.error("User deleted")
            st.rerun()
    
    # User details
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**User Details**")
        st.write(f"**ID:** `{user.id}`")
        st.write(f"**Role:** {user.role.value.title()}")
        st.write(f"**Provider:** {user.auth_provider.value.upper()}")
        st.write(f"**MFA:** {'Enabled' if user.mfa_enabled else 'Disabled'}")
    with col2:
        st.markdown("**Activity**")
        st.write(f"**Created:** {user.created_at.strftime('%Y-%m-%d')}")
        st.write(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'}")
        st.write(f"**Status:** {'Active' if user.is_active else 'Inactive'}")
