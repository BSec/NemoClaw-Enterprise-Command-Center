# NemoClaw Enterprise Command Center - Data Flow Diagrams (DFD)

**Version**: 2.1.0  
**Classification**: Internal Use  
**Last Updated**: March 27, 2026

---

## 🎯 Overview

This document contains comprehensive Data Flow Diagrams (DFD) at three levels:
- **Level 0**: Context Diagram - System boundary and external interactions
- **Level 1**: System Decomposition - Major processes and data stores
- **Level 2**: Detailed Processes - Sub-process breakdown with security controls

**Security Legend:**
- 🔒 = Encryption at rest
- 🔐 = Encryption in transit (TLS 1.3)
- ✅ = Authentication required
- 🛡️ = Authorization check
- 📝 = Audit logging
- ⚠️ = Sensitive data

---

## Level 0: Context Diagram

### System Context

```mermaid
flowchart TB
    subgraph "External Entities"
        E1[👤 Engineer]
        E2[🛡️ SecOps Analyst]
        E3[📊 CISO Executive]
        E4[🏢 Admin]
    end

    subgraph "External Systems"
        S1[🔧 NemoClaw/OpenShell<br/>Instances]
        S2[🔐 Identity Provider<br/>OAuth2/SAML]
        S3[📧 Email/SMS Gateway]
        S4[📊 SIEM/Monitoring<br/>Splunk/Datadog]
        S5[☁️ Cloud Provider<br/>AWS/Azure/GCP]
    end

    subgraph "NemoClaw Gateway System"
        direction TB
        NS[🌐 NemoClaw Gateway<br/>Enterprise Dashboard]
    end

    E1 -->|"🔐 HTTPS/API<br/>Manage Sandboxes"| NS
    E2 -->|"🔐 HTTPS/API<br/>Security Operations"| NS
    E3 -->|"🔐 HTTPS/API<br/>View Reports"| NS
    E4 -->|"🔐 HTTPS/API<br/>System Admin"| NS

    NS -->|"🔐 SSH/API<br/>Control Sandboxes"| S1
    NS -->|"🔐 OAuth2/SAML<br/>Authenticate Users"| S2
    NS -->|"🔐 SMTP/API<br/>Send Notifications"| S3
    NS -->|"🔐 Syslog/CEF<br/>Export Audit Logs"| S4
    NS -->|"🔐 API<br/>Provision Resources"| S5

    style NS fill:#4ecdc4,stroke:#333,stroke-width:3px
    style E1 fill:#ff6b6b,stroke:#333
    style E2 fill:#4ecdc4,stroke:#333
    style E3 fill:#ffeaa7,stroke:#333
    style E4 fill:#a29bfe,stroke:#333
```

### Level 0 Data Flows

| Flow | From | To | Data | Security |
|------|------|-----|------|----------|
| F1 | Engineer | Gateway | Sandbox commands, config | 🔐 TLS 1.3, ✅ Auth, 🛡️ RBAC |
| F2 | SecOps | Gateway | Security actions, approvals | 🔐 TLS 1.3, ✅ Auth, 🛡️ RBAC, 📝 Audit |
| F3 | CISO | Gateway | Report queries | 🔐 TLS 1.3, ✅ Auth, 🛡️ RBAC |
| F4 | Admin | Gateway | System configuration | 🔐 TLS 1.3, ✅ Auth, 🛡️ Admin only, 📝 Audit |
| F5 | Gateway | NemoClaw | Instance control | 🔐 SSH/API keys, ✅ Service auth |
| F6 | Gateway | IdP | Auth tokens | 🔐 OAuth2/SAML, ✅ MFA |
| F7 | Gateway | Email Gateway | Alerts, notifications | 🔐 SMTP TLS, ⚠️ Email addresses |
| F8 | Gateway | SIEM | Audit logs, events | 🔐 Syslog TLS/CEF, ⚠️ Sanitized data |
| F9 | Gateway | Cloud Provider | Resource provisioning | 🔐 API tokens, ✅ IAM roles |

---

## Level 1: System Decomposition

### Major Processes

```mermaid
flowchart TB
    subgraph "External Entities"
        E1[👤 Users<br/>Engineer/SecOps/CISO/Admin]
        E2[🔧 NemoClaw Instances]
        E3[🔐 Identity Provider]
        E4[📧 Notification Service]
        E5[📊 SIEM/Monitoring]
    end

    subgraph "NemoClaw Gateway"
        direction TB

        subgraph "Presentation Layer"
            P1[🖥️ Web Interface<br/>Streamlit UI]
        end

        subgraph "Application Layer"
            P2[⚙️ Sandbox Management<br/>Process 1.0]
            P3[🛡️ Security Operations<br/>Process 2.0]
            P4[📊 Compliance & Reporting<br/>Process 3.0]
            P5[👥 User & Access Management<br/>Process 4.0]
            P6[🏥 Health Monitoring<br/>Process 5.0]
        end

        subgraph "Data Stores"
            D1[(🔒 Configuration DB<br/>PostgreSQL)]
            D2[(🔒 Audit Log Store<br/>Immutable)]
            D3[(⚠️ Secrets Vault<br/>HashiCorp/AWS KMS)]
            D4[(🔒 Metrics Store<br/>Time Series)]
        end

        subgraph "Security Layer"
            S1[🔐 Auth Service]
            S2[🛡️ RBAC Engine]
            S3[📝 Audit Logger]
            S4[🔍 Input Validator]
        end
    end

    E1 -->|"1. Login Request<br/>🔐 HTTPS"| P1
    P1 -->|"2. Auth Check"| S1
    S1 -->|"3. Token Validation"| E3
    S1 -->|"4. Auth Response<br/>✅ Token"| P1

    P1 -->|"5. User Request<br/>✅ + 🛡️"| P2
    P1 -->|"6. User Request<br/>✅ + 🛡️"| P3
    P1 -->|"7. User Request<br/>✅ + 🛡️"| P4
    P1 -->|"8. User Request<br/>✅ + 🛡️"| P5
    P1 -->|"9. System Query"| P6

    P2 <-->|"10. CRUD Ops<br/>📝 Audit"| D1
    P3 <-->|"11. Read/Write<br/>📝 Audit"| D1
    P4 <-->|"12. Reporting"| D1
    P5 <-->|"13. User Mgmt"| D1
    P6 <-->|"14. Metrics"| D4

    P2 <-->|"15. Get/Set Secrets"| D3
    P3 <-->|"16. Log Events<br/>⚠️ Sanitized"| D2

    P2 <-->|"17. Control Commands<br/>🔐 SSH"| E2
    P3 <-->|"18. Security Status"| E2
    P5 <-->|"19. Send Alerts<br/>🔐 SMTP"| E4
    P3 -->|"20. Export Logs<br/>🔐 Syslog"| E5
    P6 -->|"21. Health Status"| E5

    S4 -->|"Validate Input"| P2
    S4 -->|"Validate Input"| P3
    S4 -->|"Validate Input"| P5

    style P1 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style D3 fill:#ff6b6b,stroke:#333,stroke-width:2px
    style D2 fill:#ffeaa7,stroke:#333,stroke-width:2px
```

### Level 1 Process Descriptions

| Process ID | Name | Description | Security Controls |
|------------|------|-------------|-------------------|
| **P1.0** | Web Interface | Streamlit-based UI layer | 🔐 HTTPS, S4 Input Validation |
| **P2.0** | Sandbox Management | Create, start, stop, monitor sandboxes | ✅ Auth, 🛡️ RBAC, 📝 Audit, 🔐 SSH to instances |
| **P3.0** | Security Operations | Request queue, alerts, policy enforcement | ✅ Auth, 🛡️ RBAC, 📝 Audit, 🔐 API tokens |
| **P4.0** | Compliance & Reporting | Audit trails, compliance tracking | ✅ Auth, 🛡️ RBAC, ⚠️ Data classification |
| **P5.0** | Health Monitoring | Self-assessment, anomaly detection | 🔍 Internal only, 📝 Audit, 🔐 Signed reports |
| **P6.0** | User & Access Management | Authentication, authorization, SSO | ✅ Auth, 🛡️ Admin only, 🔐 MFA, 📝 Audit |

### Level 1 Data Stores

| Store ID | Name | Type | Security |
|----------|------|------|----------|
| **D1** | Configuration DB | PostgreSQL | 🔒 Encryption at rest, 🔐 TLS connections, Row-level security |
| **D2** | Audit Log Store | Append-only, signed | 🔒 Immutable, 📝 Signed with HMAC, ⚠️ Sanitized |
| **D3** | Secrets Vault | HashiCorp Vault/AWS KMS | 🔒 Encrypted, 🔐 mTLS, Access logging, Rotation |
| **D4** | Metrics Store | Time-series (Influx/Prometheus) | 🔒 Encrypted, Retention policies, Aggregation |

---

## Level 2: Detailed Process Decomposition

### Process 2.0: Sandbox Management (Detailed)

```mermaid
flowchart LR
    subgraph "Process 2.0: Sandbox Management"
        direction TB

        P2.1[2.1 Authenticate<br/>& Authorize]
        P2.2[2.2 Validate<br/>Request]
        P2.3[2.3 Retrieve<br/>Instance Config]
        P2.4[2.4 Execute<br/>Sandbox Op]
        P2.5[2.5 Monitor<br/>& Log]
        P2.6[2.6 Update<br/>Status]

        P2.1 --> P2.2 --> P2.3 --> P2.4 --> P2.5 --> P2.6
    end

    subgraph "Data Stores"
        D1[(Users & Roles)]
        D2[(Instance Config)]
        D3[(Sandbox State)]
        D4[(Audit Logs)]
    end

    subgraph "External"
        E1[User Request]
        E2[NemoClaw Instance]
    end

    E1 -->|"🔐 Request<br/>{user_id, action, params}"| P2.1
    P2.1 <-->|"✅ Validate Token<br/>🛡️ Check Permissions"| D1
    P2.2 -->|"📝 Log Attempt"| D4
    P2.3 <-->|"🔒 Get Instance<br/>API Keys"| D2
    P2.4 <-->|"🔐 SSH/API<br/>Execute Command"| E2
    P2.5 -->|"📝 Log Result<br/>⚠️ No secrets"| D4
    P2.6 -->|"Update State"| D3

    style P2.4 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style D4 fill:#ffeaa7,stroke:#333,stroke-width:2px
```

#### Process 2.0 Data Flows

| Flow | From | To | Data Elements | Security |
|------|------|-----|---------------|----------|
| 2.1 | User | 2.1 | `user_id`, `action`, `sandbox_id`, `params` | 🔐 HTTPS, S4 validation |
| 2.2 | 2.1 | D1 | `token`, `required_permission` | 🔒 Query |
| 2.3 | D1 | 2.1 | `user_valid`, `permissions[]` | 🔒 Response |
| 2.4 | 2.2 | D4 | `timestamp`, `user_id`, `action`, `ip` | 📝 Audit log |
| 2.5 | 2.3 | D2 | `instance_id` | 🔒 Query |
| 2.6 | D2 | 2.3 | `instance_config`, `api_key_ref` | 🔒 Response, ⚠️ Key reference only |
| 2.7 | 2.3 | D3 | `api_key` | 🔐 Vault lookup, ⚠️ In-memory only |
| 2.8 | 2.4 | E2 | `command`, `credentials` | 🔐 SSH with key |
| 2.9 | E2 | 2.4 | `result`, `status`, `logs` | 🔐 SSH return |
| 2.10 | 2.5 | D4 | `timestamp`, `result_status`, `duration` | 📝 Audit log, ⚠️ Sanitized |
| 2.11 | 2.6 | D3 | `sandbox_id`, `new_status` | 🔒 State update |

---

### Process 3.0: Security Operations (Detailed)

```mermaid
flowchart TB
    subgraph "Process 3.0: Security Operations"
        direction TB

        subgraph "3.1 Request Processing"
            P3.1[3.1.1 Receive<br/>Request]
            P3.2[3.1.2 Risk<br/>Assessment]
            P3.3[3.1.3 Policy<br/>Check]
            P3.4[3.1.4 Decision<br/>Engine]
        end

        subgraph "3.2 Alert Management"
            P3.5[3.2.1 Detect<br/>Anomaly]
            P3.6[3.2.2 Classify<br/>Severity]
            P3.7[3.2.3 Notify<br/>Stakeholders]
            P3.8[3.2.4 Track<br/>Resolution]
        end

        subgraph "3.3 Policy Enforcement"
            P3.9[3.3.1 Evaluate<br/>Rules]
            P3.10[3.3.2 Enforce<br/>Action]
            P3.11[3.3.3 Log<br/>Violation]
        end
    end

    subgraph "Data Stores"
        D1[(Network Requests)]
        D2[(Security Policies)]
        D3[(Alert Queue)]
        D4[(Audit Trail)]
    end

    subgraph "External"
        E1[Agent Request]
        E2[Notification Service]
        E3[SIEM]
    end

    E1 -->|"⚠️ Network Request<br/>{source, target, type}"| P3.1
    P3.1 --> P3.2 --> P3.3 --> P3.4

    P3.2 <-->|"Get Risk Score"| D1
    P3.3 <-->|"Load Policies"| D2
    P3.4 -->|"⚠️ High Risk?"| P3.9
    P3.4 -->|"Store Request"| D1

    P3.9 --> P3.10 --> P3.11
    P3.11 -->|"📝 Log"| D4
    P3.5 <-->|"Monitor"| D1
    P3.5 --> P3.6 --> P3.7 --> P3.8
    P3.6 -->|"Create Alert"| D3
    P3.7 -->|"🔐 Send"| E2
    P3.8 -->|"Export<br/>🔐 Syslog"| E3

    style P3.2 fill:#ff6b6b,stroke:#333,stroke-width:2px
    style P3.9 fill:#ff6b6b,stroke:#333,stroke-width:2px
    style D4 fill:#ffeaa7,stroke:#333,stroke-width:2px
```

---

### Process 4.0: User & Access Management (Detailed)

```mermaid
flowchart LR
    subgraph "Process 4.0: Access Management"
        direction TB

        subgraph "4.1 Authentication"
            P4.1[4.1.1 Receive<br/>Credentials]
            P4.2[4.1.2 Validate<br/>Password]
            P4.3[4.1.3 Check<br/>MFA]
            P4.4[4.1.4 Issue<br/>Token]
        end

        subgraph "4.2 Authorization"
            P4.5[4.2.1 Parse<br/>Request]
            P4.6[4.2.2 Load<br/>Permissions]
            P4.7[4.2.3 Check<br/>Access]
        end

        subgraph "4.3 Session Management"
            P4.8[4.3.1 Create<br/>Session]
            P4.9[4.3.2 Validate<br/>Session]
            P4.10[4.3.3 Revoke<br/>Session]
        end
    end

    subgraph "Data Stores"
        D1[(User DB<br/>🔒)]
        D2[(Session Store)]
        D3[(RBAC Cache)]
        D4[(Audit Logs)]
    end

    subgraph "External"
        E1[Login Request]
        E2[Protected Resource]
        E3[IdP/OAuth]
    end

    E1 -->|"🔐 {email, password}"| P4.1
    P4.1 --> P4.2 --> P4.3 --> P4.4

    P4.2 <-->|"🔒 Get Hash & Salt"| D1
    P4.3 <-->|"Verify TOTP/SMS"| E3
    P4.4 -->|"🔐 Issue JWT<br/>📝 Log"| D2
    P4.4 -->|"📝 Auth Success"| D4

    E2 -->|"Request + Token"| P4.5
    P4.5 --> P4.6 --> P4.7
    P4.6 <-->|"Load Roles/Perms"| D3
    P4.7 -->|"🛡️ Allow/Deny<br/>📝 Log"| D4
    P4.7 -->|"✅ Authorized"| E2

    P4.8 --> D2
    P4.9 <-->|"Check Validity"| D2
    P4.10 -->|"Invalidate"| D2

    style P4.2 fill:#a29bfe,stroke:#333,stroke-width:2px
    style P4.3 fill:#a29bfe,stroke:#333,stroke-width:2px
    style P4.7 fill:#a29bfe,stroke:#333,stroke-width:2px
```

---

### Process 5.0: Health Monitoring (Detailed)

```mermaid
flowchart TB
    subgraph "Process 5.0: Health Monitoring"
        direction TB

        subgraph "5.1 Health Checks"
            P5.1[5.1.1 Schedule<br/>Checks]
            P5.2[5.1.2 Execute<br/>Check]
            P5.3[5.1.3 Collect<br/>Metrics]
        end

        subgraph "5.2 Anomaly Detection"
            P5.4[5.2.1 Analyze<br/>Baseline]
            P5.5[5.2.2 Detect<br/>Anomaly]
            P5.6[5.2.3 Classify<br/>Severity]
        end

        subgraph "5.3 Report Generation"
            P5.7[5.3.1 Aggregate<br/>Results]
            P5.8[5.3.2 Sign<br/>Report]
            P5.9[5.3.3 Export<br/>Format]
        end
    end

    subgraph "Data Stores"
        D1[(Health History)]
        D2[(Anomaly Events)]
        D3[(Signed Reports)]
    end

    subgraph "External"
        E1[System Components]
        E2[Monitoring Dashboard]
        E3[SIEM]
    end

    P5.1 -->|"Trigger"| P5.2 -->|"Query"| E1
    P5.2 -->|"Results"| P5.3 -->|"Store"| D1

    P5.3 -->|"Metrics"| P5.4 -->|"Compare"| D1
    P5.4 -->|"Deviation"| P5.5 -->|"⚠️ Anomaly"| P5.6
    P5.6 -->|"Create Event"| D2

    P5.7 <-->|"Load History"| D1
    P5.7 -->|"Report"| P5.8 -->|"🔐 HMAC Sign"| P5.9
    P5.9 -->|"🔒 Store"| D3
    P5.9 -->|"Display"| E2
    P5.9 -->|"🔐 Export<br/>JSON/Syslog"| E3

    style P5.8 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style D3 fill:#ffeaa7,stroke:#333,stroke-width:2px
```

---

## Security Control Mapping

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Gateway as NemoClaw Gateway
    participant Auth as Auth Service
    participant IdP as Identity Provider
    participant DB as User DB
    participant Session as Session Store
    participant Audit as Audit Logger

    User->>Gateway: 1. Login Request<br/>{email, password}
    Gateway->>Auth: 2. Validate Format
    Auth->>DB: 3. Get User Record<br/>🔒 Query
    DB-->>Auth: 4. {hash, salt, mfa_enabled}
    Auth->>Auth: 5. Hash Password<br/>PBKDF2
    Auth->>DB: 6. Compare Hashes
    
    alt MFA Required
        Auth->>User: 7a. Request MFA Code
        User->>Auth: 8a. {totp_code}
        Auth->>Auth: 9a. Verify TOTP
    end
    
    Auth->>Session: 10. Create Session<br/>🔐 Token
    Auth->>Audit: 11. Log Success<br/>📝 {user_id, ip, time}
    Auth-->>Gateway: 12. {token, expiry}
    Gateway-->>User: 13. Set Cookie<br/>🔐 HttpOnly, Secure
```

### Authorization Check

```mermaid
sequenceDiagram
    actor User
    participant Gateway as API Gateway
    participant RBAC as RBAC Engine
    participant Cache as Permission Cache
    participant Resource as Protected Resource
    participant Audit as Audit Logger

    User->>Gateway: 1. Request<br/>{token, action, resource}
    Gateway->>RBAC: 2. Validate Token
    RBAC->>RBAC: 3. Check Expiry
    RBAC->>Cache: 4. Load Permissions
    Cache-->>RBAC: 5. {roles[], permissions[]}
    RBAC->>RBAC: 6. Check Access<br/>🛡️ ACL Check
    
    alt Access Granted
        RBAC->>Resource: 7a. Forward Request
        Resource-->>RBAC: 8a. Response
        RBAC->>Audit: 9a. Log Access<br/>📝 Success
        RBAC-->>Gateway: 10a. Response
    else Access Denied
        RBAC->>Audit: 7b. Log Denial<br/>📝 Denied
        RBAC-->>Gateway: 8b. 403 Forbidden
    end
    
    Gateway-->>User: 11. Response
```

---

## Trust Boundaries

### Trust Zones

```mermaid
flowchart TB
    subgraph "🔴 Untrusted Zone"
        U1[Public Internet]
        U2[External Users]
    end

    subgraph "🟡 DMZ"
        D1[WAF]
        D2[Load Balancer]
        D3[Reverse Proxy]
    end

    subgraph "🟢 Trusted Zone"
        T1[Application Servers]
        T2[Auth Service]
        T3[Business Logic]
    end

    subgraph "🔒 Secure Zone"
        S1[(Database)]
        S2[(Secrets Vault)]
        S3[(Audit Store)]
    end

    U2 -->|"🔐 HTTPS"| D1
    D1 --> D2 --> D3
    D3 -->|"🔐 mTLS"| T1
    T1 --> T2 --> T3
    T3 <-->|"🔐 Internal TLS"| S1
    T3 <-->|"🔐 Vault mTLS"| S2
    T3 -->|"📝 Append-only"| S3

    style U1 fill:#ff6b6b,stroke:#333,stroke-width:2px
    style D1 fill:#ffeaa7,stroke:#333,stroke-width:2px
    style T1 fill:#a8e6cf,stroke:#333,stroke-width:2px
    style S2 fill:#ff6b6b,stroke:#333,stroke-width:3px
```

### Data Classification

| Classification | Examples | Storage | Transmission |
|----------------|----------|---------|--------------|
| **Public** | Documentation, marketing | Unencrypted | HTTPS |
| **Internal** | Configs, non-sensitive logs | 🔒 Encrypted | 🔐 HTTPS |
| **Confidential** | User data, sandbox configs | 🔒 Encrypted + Access Control | 🔐 HTTPS + mTLS |
| **Restricted** | Passwords, API keys, tokens | 🔒 Vault + Encryption | 🔐 Never in transit (references only) |
| **Audit** | Security events, compliance | 🔒 Immutable + Signed | 🔐 Syslog TLS |

---

## Data Flow Security Matrix

| Flow | Source | Destination | Classification | Encryption | Auth | Audit |
|------|--------|-------------|----------------|------------|------|-------|
| User Login | Browser | Gateway | Restricted | 🔐 TLS 1.3 | ✅ MFA | 📝 Yes |
| API Calls | Browser | Gateway | Confidential | 🔐 TLS 1.3 | ✅ Token | 📝 Yes |
| Instance Control | Gateway | NemoClaw | Confidential | 🔐 SSH/API | ✅ Key | 📝 Yes |
| Database Queries | Gateway | PostgreSQL | Confidential | 🔐 TLS | ✅ Service | 📝 Query logs |
| Secret Retrieval | Gateway | Vault | Restricted | 🔐 mTLS | ✅ Token | 📝 Access logs |
| Audit Export | Gateway | SIEM | Audit | 🔐 Syslog TLS | ✅ Cert | 📝 N/A |
| Notifications | Gateway | Email | Confidential | 🔐 SMTP TLS | ✅ API Key | 📝 Sent logs |

---

## Diagram Update Process

### Version Control

All DFD diagrams are version controlled with the following metadata:

```yaml
# dfd-version.yaml
document: NemoClaw_Gateway_DFD
version: 2.1.0
last_updated: 2024-03-27T00:00:00Z
author: Architecture Team
reviewers:
  - security_lead
  - principal_engineer
changes:
  - id: DFD-2024-001
    date: 2024-03-27
    description: Added Process 5.0 Health Monitoring
    author: dev_team
    approved_by: security_lead
```

### Review Checklist

- [ ] All external entities identified
- [ ] All processes have security controls marked
- [ ] Data classifications applied
- [ ] Trust boundaries clearly defined
- [ ] No sensitive data in diagram labels
- [ ] All flows have encryption noted
- [ ] Audit points identified
- [ ] Version metadata updated

---

**Classification**: Internal Use  
**Owner**: Security Architecture Team  
**Review Cycle**: Quarterly  
**Next Review**: June 27, 2026
