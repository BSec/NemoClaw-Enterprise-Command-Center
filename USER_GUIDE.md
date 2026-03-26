# NemoClaw Enterprise Command Center - User Guide

**Version**: 2.1.0  
**Last Updated**: March 27, 2026  
**Author**: Bhaskar Puppala - [LinkedIn](https://www.linkedin.com/in/bhaskerkpatel/)  

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Operating Models](#operating-models)
3. [Single-User / Personal Mode](#single-user--personal-mode)
4. [Enterprise Mode](#enterprise-mode)
5. [Core Capabilities](#core-capabilities)
6. [Quick Start Guide](#quick-start-guide)
7. [Dashboard Views](#dashboard-views)
8. [Security Features](#security-features)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

**NemoClaw Enterprise Command Center** is a unified web-based interface for managing Nvidia NemoClaw OpenShell environments. It provides comprehensive control over AI agent sandboxes with enterprise-grade security, compliance, and monitoring capabilities.

### Supported Environments
- **Nvidia NemoClaw**: Enterprise AI platform for building and deploying conversational AI
- **OpenShell CLI**: Command-line interface for NemoClaw management
- **GPU Clusters**: NVIDIA GPU-based compute resources

---

## Operating Models

### (1) Single-User / Personal Mode

**Best For**: Individual developers, researchers, small teams

**Characteristics**:
- ✅ Single user with full admin access
- ✅ Local or remote instance management
- ✅ No authentication required (or optional simple auth)
- ✅ Direct file system access
- ✅ Simplified UI without role-based restrictions

**Use Cases**:
- Personal AI development projects
- Research and experimentation
- Prototyping and POCs
- Learning and training

**Setup**:
```bash
# Run without authentication
streamlit run app.py

# Or with simple password
export AUTH_MODE=simple
export SIMPLE_PASSWORD=your_password
streamlit run app.py
```

**Features in Personal Mode**:
- Full access to all sandbox operations
- Direct GPU monitoring
- Simplified security model
- No audit logging overhead
- Single-tenant (user = tenant)

---

### (2) Enterprise Mode

**Best For**: Organizations, production deployments, multi-team environments

**Characteristics**:
- ✅ Role-Based Access Control (RBAC) with 5 roles
- ✅ Multi-tenant architecture
- ✅ Full authentication (OAuth2/SAML/Local)
- ✅ Comprehensive audit logging
- ✅ Security operations center (SecOps)
- ✅ Compliance tracking (SOC2, GDPR, ISO27001)
- ✅ Health monitoring and self-assessment
- ✅ Policy enforcement and violation tracking

**Use Cases**:
- Production AI deployment
- Enterprise AI development
- Multi-team collaboration
- Regulated industries (finance, healthcare)
- Mission-critical applications

**Setup**:
```bash
# Configure enterprise settings
export AUTH_MODE=enterprise
export OAUTH_PROVIDER=okta
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...

# Run
streamlit run app.py
```

**Roles in Enterprise Mode**:

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | System administrator | Full access to all features |
| **CISO** | Chief Information Security Officer | Security/compliance view, policies, audit |
| **SecOps** | Security Operations | Alerts, requests, threat response |
| **Engineer** | AI/ML Engineer | Sandbox management, GPU monitoring |
| **Viewer** | Read-only user | View sandboxes, logs, metrics |

---

## Core Capabilities

### 1. Sandbox Management

**Features**:
- Create sandboxes with custom configurations
- Start, stop, restart lifecycle management
- Real-time resource monitoring (CPU, memory, GPU)
- Workspace file browser (upload/download)
- Live log streaming

**Personal Mode**: Full access, no restrictions  
**Enterprise Mode**: Role-based permissions, audit logging

### 2. GPU Telemetry

**Features**:
- Real-time GPU utilization charts
- Temperature monitoring with alerts
- Memory usage tracking
- Multi-GPU support
- Historical performance data

**Use**: Monitor training jobs, prevent overheating, optimize resource allocation

### 3. Security Operations (SecOps)

**Enterprise Mode Only**

**Features**:
- Network request approval queue
- Agent reputation scoring
- Security alert dashboard
- Policy violation tracking
- Threat detection and response

### 4. Compliance & Governance (CISO)

**Enterprise Mode Only**

**Features**:
- Executive summary with KPIs
- Security scorecard with radar charts
- Compliance framework tracking (SOC2, GDPR, ISO27001, NIST)
- Audit trail with forensic capabilities
- Policy management with enforcement modes

### 5. Health Monitoring

**Both Modes**

**Features**:
- Self-assessment with 7 check types
- Anomaly detection
- Tamper-resistant integrity validation
- Remediation suggestions
- Export capabilities (JSON, text, SIEM)

---

## Quick Start Guide

### Prerequisites

```bash
# Python 3.11+
python --version

# pip
pip --version
```

### Installation

**Step 1: Clone Repository**
```bash
git clone https://github.com/BSec/NemoClaw-Enterprise-Command-Center.git
cd NemoClaw-Enterprise-Command-Center
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure**

*For Personal Mode*:
```bash
cp .env.example .env
# Edit .env - set AUTH_MODE=personal
```

*For Enterprise Mode*:
```bash
cp .env.example .env
# Edit .env - configure:
# - AUTH_MODE=enterprise
# - Database settings
# - OAuth/SAML settings
# - Redis for caching
```

**Step 5: Run**
```bash
streamlit run app.py
```

**Access**: http://localhost:8501

---

## Dashboard Views

### Login Page (`pages/00_Login.py`)

**Purpose**: Authentication and role selection

**Personal Mode**: Optional simple password or none  
**Enterprise Mode**: Full authentication with MFA

### Main Dashboard (`app.py`)

**Purpose**: Instance selection and quick actions

**Features**:
- Select NemoClaw/OpenShell instances
- Quick action buttons
- System health status
- Navigation to all views

### Engineer View (`pages/01_Engineer_View.py`)

**Purpose**: Sandbox management for engineers

**Tabs**:
1. **Sandbox Management** - Create, control, monitor
2. **GPU Telemetry** - Real-time GPU metrics
3. **Log Streaming** - Live log viewing
4. **Resources** - System resource monitoring

**Permissions Required**: `view_sandboxes`, `create_sandbox`, `delete_sandbox`

### SecOps View (`pages/02_SecOps_View.py`)

**Purpose**: Security operations center

**Tabs**:
1. **Request Queue** - Network request approvals
2. **Agent Reputation** - Behavior scoring
3. **Security Alerts** - Threat detection
4. **Policy Violations** - Compliance tracking

**Permissions Required**: `view_security_alerts`, `acknowledge_alerts`

### CISO View (`pages/03_CISO_View.py`)

**Purpose**: Executive dashboard for security leadership

**Tabs**:
1. **Executive Summary** - High-level KPIs
2. **Security Scorecard** - Domain analysis
3. **Compliance Overview** - Framework tracking
4. **Audit Trail** - Forensic events
5. **Policy Management** - Security policies

**Permissions Required**: `view_compliance`, `view_audit_trail`

### Health Monitor (`pages/05_Health_Monitor.py`)

**Purpose**: System health and self-assessment

**Features**:
- Overall status indicator
- Individual check results
- Anomaly detection
- Remediation suggestions
- Export reports

**Permissions Required**: Any authenticated user

### Settings (`pages/04_Settings.py`)

**Purpose**: Instance configuration

**Features**:
- Add/edit NemoClaw instances
- Test connectivity
- Configure API endpoints

**Permissions Required**: `system_admin`

---

## Security Features

### Authentication

**Personal Mode**:
- Optional password protection
- Session-based access
- No external dependencies

**Enterprise Mode**:
- OAuth2 (Okta, Azure AD, Google)
- SAML 2.0 SSO
- Local authentication with PBKDF2 hashing
- Multi-Factor Authentication (MFA)
- Session timeout and management

### Authorization

**Enterprise Mode Only**:
- RBAC with 5 roles
- 15 granular permissions
- Resource-level access control
- Permission inheritance

### Audit & Logging

**Enterprise Mode**:
- Immutable audit logs
- Cryptographic signatures (HMAC-SHA256)
- Event timeline
- SIEM integration ready
- Export formats: JSON, CSV, PDF, Syslog, CEF, LEEF

**Personal Mode**:
- Optional basic logging
- No cryptographic signatures
- Simplified audit trail

### Data Protection

**Both Modes**:
- TLS 1.3 for data in transit
- Input validation and sanitization
- Output encoding (XSS prevention)

**Enterprise Mode**:
- Encryption at rest (database)
- Secrets management (HashiCorp Vault)
- Row-level database security

---

## Troubleshooting

### Issue: Cannot connect to NemoClaw instance

**Solution**:
1. Check instance status in Settings
2. Verify network connectivity
3. Confirm API credentials
4. Check firewall rules

### Issue: GPU metrics not showing

**Solution**:
1. Ensure NVIDIA drivers installed
2. Install pynvml: `pip install pynvml`
3. Check GPU accessibility
4. Restart the application

### Issue: Authentication failed (Enterprise)

**Solution**:
1. Verify OAuth/SAML configuration
2. Check redirect URLs
3. Confirm user exists in database
4. Check role assignment

### Issue: Health check failing

**Solution**:
1. Check logs for specific error
2. Verify dependencies installed
3. Check database connectivity
4. Review configuration files

---

## FAQ

### Q: Can I switch from Personal to Enterprise mode?

**A**: Yes, but requires database migration and configuration update. See migration guide in [OPERATIONAL_RUNBOOKS.md](docs/OPERATIONAL_RUNBOOKS.md).

### Q: How many sandboxes can I create?

**A**: 
- **Personal Mode**: Unlimited (resource dependent)
- **Enterprise Mode**: Based on tenant tier (Starter: 3, Pro: 10, Enterprise: 100)

### Q: Is my data secure?

**A**: 
- **Personal Mode**: Local security, no external transmission
- **Enterprise Mode**: Full encryption, audit logging, compliance certified

### Q: Can I integrate with my existing SIEM?

**A**: Yes, Enterprise mode supports export to Splunk, QRadar, ArcSight, and generic syslog.

### Q: What browsers are supported?

**A**: Chrome, Firefox, Safari, Edge (latest versions). IE11 not supported.

### Q: How do I backup my configuration?

**A**: 
- **Personal Mode**: Copy `.env` and instance configs
- **Enterprise Mode**: Use built-in backup/restore in Settings

### Q: Can multiple users work on the same sandbox?

**A**: 
- **Personal Mode**: No, single user only
- **Enterprise Mode**: Yes, with proper role assignments and audit tracking

### Q: What happens when my session expires?

**A**: You'll be redirected to login. Enterprise mode supports automatic refresh tokens.

### Q: How do I report a bug or request a feature?

**A**: Create an issue at: https://github.com/BSec/NemoClaw-Enterprise-Command-Center/issues

---

## Support

**Documentation**: https://github.com/BSec/NemoClaw-Enterprise-Command-Center/tree/main/docs  
**Issues**: https://github.com/BSec/NemoClaw-Enterprise-Command-Center/issues  
**Author**: Bhaskar Puppala - [LinkedIn](https://www.linkedin.com/in/bhaskerkpatel/)

---

**Version**: 2.1.0  
**License**: MIT  
**© 2026 NemoClaw Enterprise Command Center**

---

*End of User Guide*
