# NemoClaw Enterprise Command Center v2.1.0

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/streamlit-1.28+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/security-hardened-green.svg" alt="Security">
  <img src="https://img.shields.io/badge/phases-5%20complete-brightgreen.svg" alt="Phases">
</p>

<p align="center">
  <b>Enterprise AI Agent Orchestration Platform</b><br>
  Secure, scalable, and compliant dashboard for managing AI sandboxes with zero-trust architecture
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Documentation](#documentation)

---

## 🎯 Overview

NemoClaw Gateway Dashboard provides a unified interface for managing AI agent sandboxes with enterprise-grade security and compliance features. Built on Streamlit, it offers real-time monitoring, security operations, executive reporting, and self-assessment capabilities for organizations deploying AI at scale.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Sandbox Management** | Create, start, stop, and monitor AI sandboxes |
| **GPU Telemetry** | Real-time GPU utilization and health monitoring |
| **Security Operations** | Request approval, threat detection, policy enforcement |
| **Compliance Tracking** | SOC2, GDPR, HIPAA, ISO27001 monitoring |
| **Health Monitoring** | Self-assessment with anomaly detection |
| **Multi-Tenancy** | Enterprise-scale tenant isolation |

---

## ✨ Features

### Phase 1: Foundation & Engineer View ✅

- **Sandbox Management**
  - Creation wizard with validation
  - Start/stop/restart controls
  - Workspace file browser with upload/download
  - Real-time log streaming

- **Resource Monitoring**
  - GPU metrics with Plotly gauges
  - CPU, memory, disk, network mini-charts
  - Real-time updates

### Phase 2: SecOps View & Security ✅

- **Request Queue**
  - Network request approval system
  - 4-tick risk scoring (0-100)
  - Bulk approval/deny actions

- **Agent Reputation**
  - Behavior scoring dashboard
  - Historical trend analysis
  - Risk factor breakdown

- **Security Alerts**
  - Real-time threat detection
  - Severity-based alerting
  - Alert acknowledgment workflow

- **Policy Violations**
  - Policy breach tracking
  - Compliance violation detection
  - Action logging

### Phase 3: CISO View & Compliance ✅

- **Executive Dashboard**
  - KPI summaries
  - 30-day trend analysis
  - Automated insights

- **Security Scorecard**
  - Domain-based radar charts
  - Risk matrix visualization
  - Risk register management

- **Compliance Overview**
  - Multi-framework tracking (SOC2, GDPR, ISO27001, NIST)
  - Control compliance matrix
  - Audit schedule management

- **Audit Trail**
  - Forensic logging
  - Event timeline visualization
  - SIEM integration

- **Policy Management**
  - Rule configuration
  - Enforcement modes (Enforce/Audit/Warn)
  - Version control

### Phase 4: Enterprise Scale & Multi-User ✅

- **Authentication & Authorization**
  - 5 role-based access levels
  - OAuth2/SAML SSO integration
  - MFA support

- **User Management**
  - Add/edit/deactivate users
  - Role assignment
  - Permission auditing

- **Multi-Tenancy**
  - 3-tier pricing (Starter/Professional/Enterprise)
  - Resource quotas
  - Team isolation

- **Audit Export**
  - Multiple formats (JSON, CSV, PDF, Syslog, CEF, LEEF)
  - Scheduled reporting
  - Compliance report generation

### Self-Assessment & Health Monitoring ✅ (New)

- **SecureHealthMonitor**
  - Continuous operational integrity checks
  - Tamper-resistant validation (HMAC-SHA256)
  - Anomaly detection with evidence preservation

- **Health Checks**
  - Service availability
  - Configuration integrity
  - Access control validation
  - Dependency health
  - Data flow verification
  - Performance monitoring
  - Security posture assessment

- **Remediation Engine**
  - Risk-rated suggestions
  - Safe-by-default actions
  - Approval workflow for high-risk changes

### Phase 5: Enterprise Documentation Suite ✅ (New)

- **Data Flow Diagrams**
  - Level 0, 1, 2 DFDs with security boundaries
  - Trust zone visualization
  - Sensitive data flow mapping

- **Database Schema**
  - Complete DDL/DML documentation
  - ERD diagrams for 20 tables
  - Security constraints and indexes

- **Architecture Documentation**
  - High-level and deep-dive architecture
  - Security architecture (7 defense layers)
  - Compliance mapping (SOC2, GDPR, ISO27001, NIST)

- **API Specifications**
  - 30+ REST API endpoints
  - Request/response schemas
  - Security requirements

- **Operational Runbooks**
  - Incident response procedures (P1, P2, P3)
  - Deployment and rollback workflows
  - Troubleshooting guides

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Engineer   │  │   SecOps     │  │    CISO      │      │
│  │    View      │  │    View      │  │    View      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                          │
│  ┌────────────────────────────────────────────────────────┐│
│  │              Streamlit Dashboard                        ││
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        ││
│  │  │  Sandbox  │ │  Security │ │ Compliance │        ││
│  │  │  Mgmt     │ │  Ops      │ │  Reporting │        ││
│  │  └────────────┘ └────────────┘ └────────────┘        ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Instance │ │ OpenShell│ │   GPU    │ │  Health  │     │
│  │ Manager  │ │ Service  │ │ Monitor  │ │ Monitor  │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│  │   Auth   │ │  Tenant  │ │   Audit  │                  │
│  │ Service  │ │ Manager  │ │  Logger  │                  │
│  └──────────┘ └──────────┘ └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ NemoClaw │ │ OpenShell│ │  GPU     │ │  Audit   │       │
│  │Instances │ │   CLI    │ │ Cluster  │ │   DB     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Streamlit, Plotly, Pandas |
| **Backend** | Python 3.11, asyncio |
| **Security** | PBKDF2, HMAC-SHA256, TLS 1.3 |
| **Monitoring** | NVML (GPU), SecureHealthMonitor |
| **Integration** | OAuth2, SAML, SIEM APIs |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip 21+

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/nemoclaw-gateway.git
cd nemoclaw-gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
streamlit run app.py
```

---

## 📖 Usage

### Dashboard Views

| View | Path | Description |
|------|------|-------------|
| **Login** | `pages/00_Login.py` | Authentication page |
| **Main** | `app.py` | Instance selection, quick actions |
| **Engineer** | `pages/01_Engineer_View.py` | Sandbox management, GPU metrics |
| **SecOps** | `pages/02_SecOps_View.py` | Security operations, request queue |
| **CISO** | `pages/03_CISO_View.py` | Executive dashboard, compliance |
| **Health Monitor** | `pages/05_Health_Monitor.py` | System health monitoring |
| **Settings** | `pages/04_Settings.py` | Instance management |

### Health Monitoring API

```python
from services.health_monitor import health_monitor
from services.health_checks import register_all_checks

# Register all checks
register_all_checks(health_monitor)

# Run assessment
report = health_monitor.run_assessment()

# Detect anomalies
anomalies = health_monitor.detect_anomalies(report)

# Export report
json_report = health_monitor.export_report_json(report)
text_report = health_monitor.export_report_human(report)
```

---

## 🔒 Security

### Authentication Methods

- **Local Authentication**: Email/password with PBKDF2
- **OAuth2/SSO**: Okta, Azure AD, Google Workspace
- **SAML 2.0**: Enterprise SSO
- **Multi-Factor Authentication**: TOTP/SMS

### Security Features

- ✅ Tamper-resistant health monitoring (HMAC-SHA256)
- ✅ Cryptographic integrity validation
- ✅ Rate limiting and abuse prevention
- ✅ Input validation and sanitization
- ✅ Audit logging with data sanitization
- ✅ Session security and MFA
- ✅ TLS 1.3 enforcement

See [SECURITY.md](SECURITY.md) for detailed security documentation.

---

## � Documentation

Complete enterprise documentation suite (10 documents, 175+ pages):

| Document | Description | Location |
|----------|-------------|----------|
| **README** | Project overview and quick start | [README.md](README.md) |
| **Security Guide** | Security hardening and compliance | [SECURITY.md](SECURITY.md) |
| **Progress** | Project status and roadmap | [PROGRESS.md](PROGRESS.md) |
| **Changelog** | Version history and changes | [CHANGELOG.md](CHANGELOG.md) |
| **Data Flow Diagrams** | DFD Level 0, 1, 2 with security | [docs/DATA_FLOW_DIAGRAMS.md](docs/DATA_FLOW_DIAGRAMS.md) |
| **Database Schema** | DDL/DML and ERD diagrams | [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) |
| **Architecture** | System architecture overview | [docs/ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md) |
| **Components** | Component specifications | [docs/COMPONENT_DOCUMENTATION.md](docs/COMPONENT_DOCUMENTATION.md) |
| **API Specs** | REST API documentation | [docs/API_SPECIFICATIONS.md](docs/API_SPECIFICATIONS.md) |
| **Runbooks** | Operational procedures | [docs/OPERATIONAL_RUNBOOKS.md](docs/OPERATIONAL_RUNBOOKS.md) |
| **Doc Index** | Documentation master index | [docs/INDEX.md](docs/INDEX.md) |

---

## �️ Development

### Project Structure

```
nemoclaw-gateway/
├── app.py                      # Main application
├── pages/                      # Dashboard views
│   ├── 00_Login.py             # Authentication
│   ├── 01_Engineer_View.py     # Engineer dashboard
│   ├── 02_SecOps_View.py       # Security operations
│   ├── 03_CISO_View.py         # Executive view
│   ├── 04_Settings.py          # Instance settings
│   └── 05_Health_Monitor.py    # Health monitoring
├── components/                 # UI components
│   ├── sandbox_form.py
│   ├── file_browser.py
│   ├── log_streamer.py
│   ├── resource_charts.py
│   ├── request_queue.py
│   ├── agent_reputation.py
│   ├── security_alerts.py
│   ├── executive_summary.py
│   ├── security_scorecard.py
│   ├── compliance_overview.py
│   ├── audit_trail.py
│   ├── policy_management.py
│   ├── user_management.py
│   ├── audit_export.py
│   └── health_dashboard.py     # NEW
├── services/                   # Business logic
│   ├── instance_manager.py
│   ├── openshell.py
│   ├── gpu_monitor.py
│   ├── auth_service.py
│   ├── tenant_manager.py
│   ├── health_monitor.py       # NEW
│   └── health_checks.py        # NEW
├── utils/                      # Utilities
│   ├── config.py
│   ├── styling.py
│   ├── error_handling.py
│   └── security_hardening.py
└── tests/                      # Test suite
```

### Running Tests

```bash
pytest tests/ --cov=nemoclaw
```

---

## 📜 Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.1.0** | 2024-03-27 | All 5 phases + Health Monitoring + Documentation Suite |
| **2.0.0** | 2024-03-27 | Phase 4: Enterprise & Multi-User |
| **1.3.0** | 2024-03-27 | Phase 3: CISO View & Compliance |
| **1.2.0** | 2024-03-27 | Phase 2: SecOps View |
| **1.1.0** | 2024-03-27 | Phase 1: Foundation |
| **0.2.0** | 2024-03-26 | Initial Python migration |

---

*Last Updated: March 27, 2026*

## 👤 Author

**Bhasker Patel**  
🔗 LinkedIn: [https://www.linkedin.com/in/bhaskerkpatel/](https://www.linkedin.com/in/bhaskerkpatel/)

