"""Audit Export and Reporting for NemoClaw Gateway.

Phase 4: Enterprise audit trail export and compliance reporting.
"""

import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import csv
from io import StringIO

class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    SYSLOG = "syslog"
    CEF = "cef"  # Common Event Format
    LEEF = "leef"  # Log Event Extended Format

class ReportType(Enum):
    """Types of compliance reports."""
    SECURITY_AUDIT = "security_audit"
    COMPLIANCE_SUMMARY = "compliance_summary"
    USER_ACTIVITY = "user_activity"
    INCIDENT_RESPONSE = "incident_response"
    ACCESS_REVIEW = "access_review"
    DATA_ACCESS = "data_access"

@dataclass
class ExportJob:
    """Export job tracking."""
    id: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str  # pending, running, completed, failed
    format: ExportFormat
    record_count: int
    file_size: Optional[int]
    download_url: Optional[str]
    filters: Dict

@dataclass
class ScheduledReport:
    """Scheduled recurring report."""
    id: str
    name: str
    report_type: ReportType
    frequency: str  # daily, weekly, monthly, quarterly
    recipients: List[str]
    last_run: Optional[datetime]
    next_run: datetime
    is_active: bool
    format: ExportFormat

class AuditExporter:
    """Audit export and reporting manager."""
    
    def __init__(self):
        self._export_jobs: Dict[str, ExportJob] = {}
        self._scheduled_reports: Dict[str, ScheduledReport] = {}
        self._init_demo_reports()
    
    def _init_demo_reports(self):
        """Initialize demo scheduled reports."""
        now = datetime.now()
        
        self._scheduled_reports["sched-001"] = ScheduledReport(
            id="sched-001",
            name="Weekly Security Summary",
            report_type=ReportType.SECURITY_AUDIT,
            frequency="weekly",
            recipients=["ciso@company.com", "secops@company.com"],
            last_run=now - timedelta(days=7),
            next_run=now + timedelta(days=0),  # Due today
            is_active=True,
            format=ExportFormat.PDF
        )
        
        self._scheduled_reports["sched-002"] = ScheduledReport(
            id="sched-002",
            name="Monthly Compliance Report",
            report_type=ReportType.COMPLIANCE_SUMMARY,
            frequency="monthly",
            recipients=["compliance@company.com", "audit@company.com"],
            last_run=now - timedelta(days=30),
            next_run=now + timedelta(days=3),
            is_active=True,
            format=ExportFormat.PDF
        )
        
        self._scheduled_reports["sched-003"] = ScheduledReport(
            id="sched-003",
            name="Quarterly Access Review",
            report_type=ReportType.ACCESS_REVIEW,
            frequency="quarterly",
            recipients=["admin@company.com", "ciso@company.com"],
            last_run=now - timedelta(days=90),
            next_run=now + timedelta(days=60),
            is_active=True,
            format=ExportFormat.CSV
        )
    
    def create_export_job(
        self,
        format: ExportFormat,
        start_date: datetime,
        end_date: datetime,
        filters: Dict
    ) -> ExportJob:
        """Create new export job."""
        job = ExportJob(
            id=f"export-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            status="pending",
            format=format,
            record_count=0,
            file_size=None,
            download_url=None,
            filters=filters
        )
        self._export_jobs[job.id] = job
        return job
    
    def get_export_jobs(self) -> List[ExportJob]:
        """Get all export jobs."""
        return sorted(
            self._export_jobs.values(),
            key=lambda j: j.created_at,
            reverse=True
        )
    
    def get_scheduled_reports(self) -> List[ScheduledReport]:
        """Get all scheduled reports."""
        return list(self._scheduled_reports.values())
    
    def export_to_format(
        self,
        events: List[Dict],
        format: ExportFormat
    ) -> str:
        """Export events to specified format."""
        if format == ExportFormat.JSON:
            return json.dumps(events, indent=2, default=str)
        
        elif format == ExportFormat.CSV:
            if not events:
                return ""
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=events[0].keys())
            writer.writeheader()
            writer.writerows(events)
            return output.getvalue()
        
        elif format == ExportFormat.SYSLOG:
            lines = []
            for event in events:
                timestamp = event.get('timestamp', datetime.now())
                lines.append(
                    f"<{timestamp}> NEMOCLAW {event.get('severity', 'INFO')} "
                    f"{event.get('event_type', 'UNKNOWN')}: {json.dumps(event)}"
                )
            return "\n".join(lines)
        
        elif format == ExportFormat.CEF:
            lines = []
            for event in events:
                lines.append(
                    f"CEF:0|NemoClaw|Gateway|2.1.0|{event.get('event_type', 'unknown')}|"
                    f"{event.get('description', 'Event')}|{event.get('severity', 'low')}|"
                    f"msg={json.dumps(event)}"
                )
            return "\n".join(lines)
        
        else:
            return json.dumps(events, default=str)

def render_audit_export(openshell_service, instance_id: str):
    """Render audit export interface."""
    
    exporter = AuditExporter()
    
    st.header("📤 Audit Export & Reporting")
    st.caption("Export audit logs and generate compliance reports")
    
    # Quick stats
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Records (24h)", "1,247")
    with col2:
        st.metric("Storage Used", "45.2 MB")
    with col3:
        st.metric("Retention", "7 years")
    with col4:
        st.metric("Scheduled Reports", "3 active")
    
    st.divider()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📥 Quick Export", "📅 Scheduled Reports", "📊 Compliance Reports"])
    
    with tab1:
        _render_quick_export(exporter)
    
    with tab2:
        _render_scheduled_reports(exporter)
    
    with tab3:
        _render_compliance_reports(exporter)

def _render_quick_export(exporter: AuditExporter):
    """Render quick export interface."""
    
    st.subheader("Quick Export")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=7),
            key="export_start"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="export_end"
        )
    
    # Filters
    st.divider()
    st.caption("Filters (optional)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            options=["critical", "high", "medium", "low", "info"],
            default=[],
            key="export_severity"
        )
    with col2:
        event_types = st.multiselect(
            "Event Types",
            options=["user_login", "policy_change", "sandbox_create", "request_approve", "data_access"],
            default=[],
            key="export_types"
        )
    with col3:
        users = st.multiselect(
            "Users",
            options=["admin@company.com", "ciso@company.com", "secops@company.com", "engineer@company.com"],
            default=[],
            key="export_users"
        )
    
    # Format selection
    st.divider()
    format_col1, format_col2 = st.columns([2, 1])
    
    with format_col1:
        export_format = st.selectbox(
            "Export Format",
            options=[f for f in ExportFormat],
            format_func=lambda x: {
                ExportFormat.JSON: "📄 JSON (Machine readable)",
                ExportFormat.CSV: "📊 CSV (Spreadsheet)",
                ExportFormat.PDF: "📑 PDF (Human readable)",
                ExportFormat.SYSLOG: "📝 Syslog (SIEM integration)",
                ExportFormat.CEF: "🔒 CEF (ArcSight/LogRhythm)",
                ExportFormat.LEEF: "🔒 LEEF (QRadar)"
            }.get(x, x.value),
            key="export_format"
        )
    
    with format_col2:
        if st.button("🚀 Generate Export", type="primary", use_container_width=True):
            with st.spinner("Generating export..."):
                import time
                time.sleep(2)
            
            # Create download button with mock data
            filters = {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "severity": severity_filter,
                "types": event_types,
                "users": users
            }
            
            job = exporter.create_export_job(export_format, start_date, end_date, filters)
            
            # Generate mock export data
            mock_events = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "user_login",
                    "severity": "info",
                    "user": "admin@company.com",
                    "description": "User login successful"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "policy_change",
                    "severity": "high",
                    "user": "admin@company.com",
                    "description": "Modified network policy"
                }
            ]
            
            export_data = exporter.export_to_format(mock_events, export_format)
            
            file_extensions = {
                ExportFormat.JSON: "json",
                ExportFormat.CSV: "csv",
                ExportFormat.PDF: "pdf",
                ExportFormat.SYSLOG: "log",
                ExportFormat.CEF: "cef",
                ExportFormat.LEEF: "leef"
            }
            
            st.download_button(
                label=f"⬇️ Download {export_format.value.upper()}",
                data=export_data,
                file_name=f"nemoclaw_audit_{start_date}_{end_date}.{file_extensions[export_format]}",
                mime="application/octet-stream",
                use_container_width=True
            )
            
            st.success(f"✅ Export ready! Job ID: {job.id}")
    
    # Recent exports
    st.divider()
    st.subheader("Recent Exports")
    
    jobs = exporter.get_export_jobs()
    if jobs:
        for job in jobs[:5]:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{job.id}**")
                    st.caption(f"{job.format.value.upper()} | {job.created_at.strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    status_colors = {
                        "pending": "🟡",
                        "running": "🔵",
                        "completed": "🟢",
                        "failed": "🔴"
                    }
                    st.write(f"{status_colors.get(job.status, '⚪')} {job.status.title()}")
                with col3:
                    if job.status == "completed":
                        st.button("⬇️ Download", key=f"dl_{job.id}", use_container_width=True)
                st.divider()
    else:
        st.info("No recent exports")

def _render_scheduled_reports(exporter: AuditExporter):
    """Render scheduled reports interface."""
    
    st.subheader("Scheduled Reports")
    
    # Add new report
    with st.expander("➕ Create Scheduled Report", expanded=False):
        report_name = st.text_input("Report Name", placeholder="Weekly Security Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            report_type = st.selectbox(
                "Report Type",
                options=[r for r in ReportType],
                format_func=lambda x: x.value.replace('_', ' ').title()
            )
        with col2:
            frequency = st.selectbox(
                "Frequency",
                options=["daily", "weekly", "monthly", "quarterly"]
            )
        
        recipients = st.text_area(
            "Recipients (one per line)",
            placeholder="ciso@company.com\nsecops@company.com"
        )
        
        if st.button("📅 Schedule Report", type="primary", use_container_width=True):
            if report_name and recipients:
                st.success(f"Report '{report_name}' scheduled!")
            else:
                st.error("Please fill in all fields")
    
    # Existing scheduled reports
    st.divider()
    reports = exporter.get_scheduled_reports()
    
    for report in reports:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{report.name}**")
                st.caption(f"{report.report_type.value.replace('_', ' ').title()} | {report.frequency.title()}")
            
            with col2:
                if report.is_active:
                    st.write("🟢 Active")
                else:
                    st.write("⚪ Paused")
                st.caption(f"Next: {report.next_run.strftime('%Y-%m-%d')}")
            
            with col3:
                st.write(f"{len(report.recipients)} recipients")
                st.caption(f"Last: {report.last_run.strftime('%Y-%m-%d') if report.last_run else 'Never'}")
            
            with col4:
                if report.is_active:
                    if st.button("⏸️ Pause", key=f"pause_{report.id}", use_container_width=True):
                        st.info("Report paused")
                else:
                    if st.button("▶️ Resume", key=f"resume_{report.id}", use_container_width=True):
                        st.info("Report resumed")
            
            st.divider()

def _render_compliance_reports(exporter: AuditExporter):
    """Render compliance reports interface."""
    
    st.subheader("Compliance Reports")
    
    report_templates = {
        "SOC 2 Type II": "Comprehensive SOC 2 audit report with all trust service criteria",
        "GDPR Data Processing": "Data processing activities and compliance status",
        "ISO 27001": "Information security management system audit",
        "NIST CSF": "Cybersecurity framework assessment",
        "User Access Review": "Quarterly access rights certification"
    }
    
    for name, description in report_templates.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{name}**")
                st.caption(description)
            
            with col2:
                if st.button("📊 Generate", key=f"gen_{name}", use_container_width=True):
                    with st.spinner(f"Generating {name}..."):
                        import time
                        time.sleep(2)
                    st.success(f"{name} generated!")
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f"Mock {name} report content",
                        file_name=f"{name.lower().replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            st.divider()
