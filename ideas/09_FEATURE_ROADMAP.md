# NemoClaw Gateway Dashboard - Feature Roadmap

## Phase: Ideation (v0.1.0)

---

## 1. Roadmap Overview

### Phases

| Phase | Focus | Timeline | Status |
|-------|-------|----------|--------|
| **Phase 0** | Ideation & Documentation | March 2026 | **In Progress** |
| **Phase 1** | Foundation & Engineer View | Q2 2026 | Planned |
| **Phase 2** | SecOps View & Security | Q3 2026 | Planned |
| **Phase 3** | CISO View & Compliance | Q4 2026 | Planned |
| **Phase 4** | Enterprise Scale & Multi-User | Q1 2027 | Future |

---

## 2. Deployment Progression: Personal → Enterprise

The roadmap supports a **natural evolution** from individual use to enterprise scale.

### Phase Alignment by Deployment Mode

```
PERSONAL MODE (Default)          ENTERPRISE MODE (Phase 4+)
─────────────────────────         ─────────────────────────
Phase 0: Ideation                 Phase 0: Ideation
Phase 1: Engineer View    ──────▶  Phase 1: Engineer View
Phase 2: SecOps View      ──────▶  Phase 2: SecOps View  
Phase 3: CISO View        ──────▶  Phase 3: CISO View
                          ──────▶  Phase 4: Multi-User & Governance
                          ──────▶  Phase 5: Enterprise Scale
```

### Progressive Feature Enablement

| Phase | Personal Features | Enterprise Additions |
|-------|------------------|---------------------|
| **Phase 1** | Sandbox management, GPU monitoring, logs | - |
| **Phase 2** | Request queue, reputation scoring | Workflow approvals, audit trails |
| **Phase 3** | Compliance dashboard, reports | Multi-tenant reports, org policies |
| **Phase 4** | - | Authentication, RBAC/ABAC, SSO |
| **Phase 5** | - | High availability, clustering, SIEM |

### Migration Path

1. **Start Personal**: Deploy on local machine for immediate value
2. **Grow Usage**: Add users via shared workstation or simple auth
3. **Need Governance**: Export config, deploy Enterprise with auth
4. **Scale Up**: Add HA, clustering, integrations as needed

### Code Reuse Strategy

- **80% shared code** between Personal and Enterprise
- Same Python codebase, different configuration
- Feature flags enable/disable capabilities
- No rewrite required for migration

---

## 3. Phase 0: Ideation & Documentation (Current)

**Goal**: Define complete conceptual framework before development

### Deliverables
- [x] **IDEAS.md** - Master documentation with all URLs and concepts
- [x] **CONCEPTUAL_DESIGN.md** - Architecture and design principles
- [x] **PERSONA_REQUIREMENTS.md** - Detailed user personas and journeys
- [x] **UI_UX_DESIGN.md** - Visual design system and wireframes
- [x] **API_CONTRACTS.md** - Data models and API specifications
- [ ] **FEATURE_ROADMAP.md** - This document

### Key Decisions
- [ ] Confirm local-only deployment model
- [ ] Approve persona-based UI approach
- [ ] Validate technology stack choices
- [ ] Define MVP scope vs. future enhancements

### Success Criteria
- All stakeholder questions answered in documentation
- Clear development path for Phase 1
- Risk assessment completed

---

## 3. Phase 1: Foundation & Engineer View (MVP)

**Goal**: Core dashboard with sandbox management for engineers

**Timeline**: Q2 2026 (8-10 weeks)

### Week 1-2: Project Setup

**Sprint 1: Infrastructure**
- [ ] Set up Python project structure
- [ ] Create virtual environment and requirements.txt
- [ ] Configure Streamlit with custom theme
- [ ] Set up Pydantic models for type safety
- [ ] Configure linting (ruff) and formatting (black)
- [ ] Create folder structure (pages, components, services, models)
- [ ] Set up testing framework (pytest)
- [ ] Create CI/CD pipeline (GitHub Actions)

**Deliverables**:
- Working development environment
- Streamlit app running locally
- Test suite passing
- CI pipeline passing

### Week 3-4: Core Layout & Navigation

**Sprint 2: Shell & Navigation**
- [ ] Implement persona switching with session state
- [ ] Create sidebar navigation with page links
- [ ] Set up Streamlit pages (Engineer, SecOps, CISO)
- [ ] Implement responsive layout with containers
- [ ] Create custom theme with NVIDIA colors
- [ ] Add header with system status indicators
- [ ] Keyboard navigation support

**Deliverables**:
- Functional dashboard shell
- All personas can switch contexts
- Mobile-responsive layout
- Accessibility audit passing

### Week 5-6: OpenShell Integration Layer

**Sprint 3: Backend Integration**
- [ ] OpenShell CLI wrapper service (Python subprocess)
- [ ] Sandbox listing API endpoint
- [ ] Sandbox status monitoring
- [ ] File system watcher using watchdog library
- [ ] Log streaming via subprocess pipes
- [ ] GPU metrics collection using pynvml
- [ ] Error handling and retry logic

**Deliverables**:
- API endpoints for all core operations
- Real-time data streaming working
- Error handling robust

### Week 7-8: Engineer View - Sandbox Management

**Sprint 4: Sandbox Dashboard**
- [ ] Sandbox list view with status cards (Streamlit containers)
- [ ] Sandbox detail expanders with metrics
- [ ] Sandbox creation form with validation
- [ ] Start/stop/restart buttons with callbacks
- [ ] Resource usage mini-charts (Plotly)
- [ ] Workspace file browser with st.file_uploader
- [ ] Basic log viewer with st.text_area

**Deliverables**:
- Engineer can list all sandboxes
- Engineer can create new sandbox
- Engineer can control sandbox lifecycle
- Engineer can browse workspace files

### Week 9-10: Engineer View - Monitoring & Logs

**Sprint 5: Telemetry & Debugging**
- [ ] GPU telemetry dashboard with Plotly gauges
- [ ] Real-time utilization charts with st.line_chart
- [ ] Memory usage tracking with metrics
- [ ] Unified log viewer with filtering
- [ ] Log search with text input
- [ ] Log severity filtering with multiselect
- [ ] Export logs to CSV/JSON

**Deliverables**:
- Real-time GPU metrics visible
- Logs searchable and filterable
- Engineer can debug issues effectively

### Phase 1 Success Criteria

| Metric | Target |
|--------|--------|
| Sandbox creation time | <2 minutes |
| Log search time | <30 seconds |
| Dashboard load time | <2 seconds |
| GPU metric latency | <5 seconds |
| CLI command reduction | 80% |

---

## 4. Phase 2: SecOps View & Security Features

**Goal**: Security operations capabilities and threat management

**Timeline**: Q3 2026 (8-10 weeks)

### Week 1-2: Network Request Management

**Sprint 6: Request Queue**
- [ ] Network request list view
- [ ] Request detail drawer
- [ ] Risk score display
- [ ] One-click approve/deny
- [ ] Bulk actions (multi-select)
- [ ] Request filtering and search
- [ ] Auto-refresh queue
- [ ] Request history view

**Deliverables**:
- SecOps can view pending requests
- SecOps can approve/deny with one click
- Historical request log accessible

### Week 3-4: Agent Reputation System

**Sprint 7: Reputation Scoring**
- [ ] Reputation calculation engine
- [ ] Agent reputation dashboard
- [ ] Score cards with trends
- [ ] Signal breakdown visualization
- [ ] Historical score charts
- [ ] Quarantine controls
- [ ] Auto-action configuration

**Deliverables**:
- All agents have reputation scores
- Scores update in real-time
- Quarantine actions available

### Week 5-6: Policy Management

**Sprint 8: Policy UI**
- [ ] Policy list view
- [ ] Policy detail view
- [ ] Visual policy builder
- [ ] Rule condition editor
- [ ] Policy test/simulation
- [ ] Policy version history
- [ ] Policy conflict detection

**Deliverables**:
- SecOps can view all policies
- SecOps can create new policies
- Policy changes testable before deployment

### Week 7-8: HITL (Human-in-the-Loop)

**Sprint 9: Adjudication System**
- [ ] HITL queue interface
- [ ] Case detail view
- [ ] Context preview panel
- [ ] Approve/Deny/Override actions
- [ ] Comment system
- [ ] SLA timer display
- [ ] Escalation workflow
- [ ] Decision history

**Deliverables**:
- High-risk actions route to HITL queue
- Human can review full context
- Decisions tracked and auditable

### Week 9-10: Threat Detection Basics

**Sprint 10: Security Monitoring**
- [ ] Alert dashboard
- [ ] Policy violation notifications
- [ ] Unusual behavior detection
- [ ] Alert severity classification
- [ ] Alert acknowledgment workflow
- [ ] Alert correlation
- [ ] Security event timeline

**Deliverables**:
- Security alerts visible in real-time
- Alert context provided
- Alert workflow functional

### Phase 2 Success Criteria

| Metric | Target |
|--------|--------|
| Request approval time | <30 seconds |
| Time to detect anomaly | <1 minute |
| HITL response time | <5 minutes |
| False positive rate | <5% |
| Policy deployment time | <2 minutes |

---

## 5. Phase 3: CISO View & Compliance

**Goal**: Executive reporting and compliance management

**Timeline**: Q4 2026 (6-8 weeks)

### Week 1-2: Compliance Framework

**Sprint 11: Compliance Dashboard**
- [ ] NIST AI RMF framework mapping
- [ ] ISO 42001 framework mapping
- [ ] Compliance score calculation
- [ ] Category breakdown views
- [ ] Control status tracking
- [ ] Evidence management UI
- [ ] Gap analysis report

**Deliverables**:
- Compliance frameworks loaded
- Current compliance status visible
- Gap analysis available

### Week 3-4: Reporting Engine

**Sprint 12: Executive Reports**
- [ ] Executive summary view
- [ ] Risk trend charts
- [ ] Key metrics dashboard
- [ ] Report generator
- [ ] PDF export
- [ ] PowerPoint export
- [ ] Scheduled report automation
- [ ] Report template library

**Deliverables**:
- Board-ready reports generated
- Multiple export formats supported
- Reports schedulable

### Week 5-6: Audit Support

**Sprint 13: Audit Features**
- [ ] Audit trail viewer
- [ ] Evidence collection workflow
- [ ] Auditor read-only access
- [ ] Evidence package export
- [ ] Compliance timeline
- [ ] Findings management
- [ ] Remediation tracking

**Deliverables**:
- Full audit trail accessible
- Evidence easily collected
- Auditor access supported

### Week 7-8: Shadow AI Discovery

**Sprint 14: Shadow AI**
- [ ] Network scanning for AI endpoints
- [ ] Shadow AI dashboard
- [ ] Endpoint classification
- [ ] Risk assessment for discovered endpoints
- [ ] "Bring into Management" workflow
- [ ] Unmanaged usage reports

**Deliverables**:
- Shadow AI instances discoverable
- Risk assessment automated
- Migration workflow functional

### Phase 3 Success Criteria

| Metric | Target |
|--------|--------|
| Board report generation | <30 minutes |
| Audit response time | <1 day |
| Compliance visibility | 100% of AI projects |
| Shadow AI discovery | <24 hours |

---

## 6. Phase 4: Enterprise Scale & Multi-User (Future)

**Goal**: Transform from single-user tool to enterprise-grade multi-user platform

**Focus Areas**:
1. **Multi-User Architecture**: RBAC/ABAC, authentication, session management
2. **Enterprise Governance**: Workflow approvals, audit trails, compliance enforcement
3. **Scalability**: High availability, clustering, load balancing
4. **AI-Powered Features**: Advanced automation and intelligence

**Timeline**: Q1 2027+ (TBD)

### Potential Features

#### AI-Powered Capabilities
- [ ] **Anomaly Detection ML**: Train models on agent behavior
- [ ] **Natural Language Log Query**: "Show me errors from yesterday"
- [ ] **Auto-Policy Recommendations**: Suggest policies based on patterns
- [ ] **Predictive Risk Scoring**: Forecast potential issues
- [ ] **Smart Alerting**: Reduce noise with ML classification

#### Advanced Security
- [ ] **Attack Graph Visualization**: Neo4j-powered graph view
- [ ] **Forensic Timeline Replay**: Step-through agent decisions
- [ ] **Multi-Model Guardrail Consensus**: 3-model voting
- [ ] **Behavioral Biometrics**: Agent behavior fingerprinting

#### Enterprise Multi-User & Governance
- [ ] **Authentication System**: SSO, LDAP, OAuth2 integration
- [ ] **RBAC Implementation**: Role-based access control (Admin, Engineer, SecOps, Viewer)
- [ ] **ABAC Support**: Attribute-based access control for fine-grained permissions
- [ ] **Session Management**: Redis-backed sessions with timeout control
- [ ] **Audit Database**: PostgreSQL for centralized audit logging
- [ ] **Workflow Engine**: Multi-stage approval workflows for critical operations
- [ ] **User Management**: User provisioning, deprovisioning, role assignment
- [ ] **Team/Project Isolation**: Multi-tenancy with resource boundaries
- [ ] **Policy Templates**: Organization-wide policy distribution and enforcement
- [ ] **Usage Analytics**: User activity tracking and reporting

#### Multi-Instance & Fleet Management
- [ ] **Instance Registry**: Centralized management of multiple NemoClaw installations
- [ ] **Multi-Instance Dashboard**: View sandboxes across all instances
- [ ] **Instance Health Monitoring**: Per-instance health checks and alerts
- [ ] **Cross-Instance Search**: Global search across all instances
- [ ] **Fleet-wide Operations**: Deploy policies to multiple instances
- [ ] **Instance Connector Types**: Local, SSH, API, Agent-based connections
- [ ] **Instance Migration**: Move sandboxes between instances
- [ ] **Aggregated Reporting**: Cross-instance compliance and usage reports

#### Enterprise Scale Infrastructure
- [ ] **LDAP/SSO Integration**: Enterprise authentication
- [ ] **High Availability**: Multi-instance dashboard with load balancing
- [ ] **Audit Log Retention**: Long-term log storage with archiving
- [ ] **Backup & Recovery**: Automated backup strategies
- [ ] **Horizontal Scaling**: Kubernetes/Docker orchestration support

#### Integration Ecosystem
- [ ] **SIEM Connectors**: Splunk, Elastic, Datadog
- [ ] **Ticketing Integration**: Jira, ServiceNow
- [ ] **Slack/Teams Notifications**: Real-time alerts
- [ ] **Webhook Support**: Custom integrations

---

## 7. Feature Prioritization Matrix

### MoSCoW Prioritization

#### Must Have (MVP - Phase 1)

| Feature | Persona | Effort | Value | Priority |
|---------|---------|--------|-------|----------|
| Sandbox List & Status | Engineer | M | H | P0 |
| Sandbox Start/Stop/Restart | Engineer | M | H | P0 |
| GPU Telemetry Display | Engineer | M | H | P0 |
| Log Viewer with Filtering | Engineer | M | H | P0 |
| Workspace File Browser | Engineer | L | M | P0 |
| Persona Switching | All | M | H | P0 |
| Real-time Updates | All | M | H | P0 |

#### Should Have (Phase 2)

| Feature | Persona | Effort | Value | Priority |
|---------|---------|--------|-------|----------|
| Network Request Queue | SecOps | M | H | P1 |
| One-Click Approve/Deny | SecOps | M | H | P1 |
| Agent Reputation Scoring | SecOps | H | H | P1 |
| Basic Policy Management | SecOps | M | M | P1 |
| HITL Adjudication | SecOps | H | M | P1 |
| Security Alerts | SecOps | M | H | P1 |

#### Could Have (Phase 3)

| Feature | Persona | Effort | Value | Priority |
|---------|---------|--------|-------|----------|
| Compliance Dashboard | CISO | M | H | P2 |
| Executive Reports | CISO | M | H | P2 |
| Audit Evidence Collection | CISO | L | M | P2 |
| Shadow AI Discovery | CISO | H | M | P2 |

#### Won't Have (Yet) / Future

| Feature | Persona | Effort | Value | Priority |
|---------|---------|--------|-------|----------|
| Attack Graph Visualization | SecOps | H | M | P3 |
| Forensic Timeline Replay | SecOps | H | M | P3 |
| AI-Powered Anomaly Detection | All | H | M | P3 |
| Multi-Instance Support | All | H | L | P3 |
| LDAP/SSO Integration | All | M | L | P3 |
| Natural Language Query | All | H | L | P3 |

---

## 8. Technical Debt & Risk Management

### Technical Debt Tracking

| Area | Description | Priority | Resolution |
|------|-------------|----------|------------|
| Testing | Integration tests for OpenShell wrapper | High | Sprint 3 |
| Documentation | API documentation auto-generation | Medium | Phase 2 |
| Performance | Log pagination for large files | Medium | Phase 2 |
| Security | Input sanitization audit | High | Sprint 1 |
| Scalability | SQLite → PostgreSQL migration path | Low | Phase 4 |

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenShell API changes | Medium | High | Abstraction layer, version pinning |
| GPU metrics unavailable | Low | Medium | Graceful degradation, mock data |
| Performance with many sandboxes | Medium | Medium | Pagination, virtualization, caching |
| Security vulnerabilities | Low | Critical | Regular audits, dependency updates |
| User adoption resistance | Medium | Medium | UX testing, feedback loops, training |

---

## 9. Success Metrics by Phase

### Phase 1 (Engineer MVP)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Sandbox creation time | 10 min (CLI) | 2 min | User testing |
| Log search time | 5 min | 30 sec | User testing |
| Dashboard adoption | 0% | 80% of engineers | Analytics |
| CLI command reduction | 0% | 80% | Usage analytics |
| User satisfaction | N/A | 4.0/5.0 | Survey |

### Phase 2 (SecOps)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Request approval time | 5 min | 30 sec | System logs |
| Time to detect anomaly | 30 min | 1 min | Incident logs |
| Mean time to respond | 15 min | 5 min | Incident logs |
| False positive rate | N/A | <5% | Alert analysis |
| Security incidents caught | N/A | 100% | Incident reports |

### Phase 3 (CISO)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Board report prep time | 2 days | 30 min | Time tracking |
| Audit response time | 2 weeks | 1 day | Time tracking |
| Compliance visibility | 0% | 100% | Inventory |
| Policy coverage | Unknown | 100% known | Audit |
| Executive satisfaction | N/A | 4.5/5.0 | Survey |

---

## 10. Release Planning

### Versioning Strategy

- **0.x.x**: Pre-release / Alpha (Phase 0-1)
- **1.0.0**: MVP Release (End of Phase 1)
- **1.x.x**: Feature releases (Phase 2)
- **2.0.0**: Major release with SecOps (End of Phase 2)
- **2.x.x**: Feature releases (Phase 3)
- **3.0.0**: Enterprise release (End of Phase 3)

### Release Checklist

#### Pre-Release
- [ ] All P0 features complete
- [ ] Test coverage >80%
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Accessibility audit passed

#### Release
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Git tag created
- [ ] Release notes published
- [ ] Installation packages built
- [ ] Documentation deployed

#### Post-Release
- [ ] Monitoring dashboards active
- [ ] Feedback channels open
- [ ] Support documentation ready
- [ ] Training materials available

---

## 11. Open Questions & Decisions Needed

### Architecture Decisions

1. **Database**: SQLite for local-only vs optional PostgreSQL?
2. **Real-time**: SSE vs WebSocket for updates?
3. **Authentication**: OS-level only vs optional auth layer?
4. **Deployment**: Single binary vs containerized?

### Feature Decisions

1. **Multi-user**: Support multiple concurrent users?
2. **Remote access**: Allow remote dashboard access (VPN/tunnel)?
3. **Mobile app**: Native mobile companion worth building?
4. **Plugins**: Plugin architecture for extensibility?

### Integration Decisions

1. **OpenShell version**: Support multiple OpenShell versions?
2. **Cloud providers**: Native cloud deployment options?
3. **SIEM integration**: Which platforms to prioritize?
4. **Backup/restore**: Built-in or external tools?

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
