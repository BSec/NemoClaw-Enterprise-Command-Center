# NemoClaw Gateway Dashboard - Persona Requirements & User Journeys

## Phase: Ideation (v0.1.0)

---

## 1. Alex - AI Engineer

### Detailed Profile
**Name**: Alex Chen  
**Role**: Senior Machine Learning Engineer  
**Experience**: 5+ years in AI/ML, 2 years with LLM systems  
**Technical Level**: Expert  
**Daily Tasks**:
- Developing and debugging AI agents
- Optimizing agent performance and resource usage
- Testing different inference providers
- Collaborating with SecOps on security policies

### Goals & Motivations
1. **Performance Optimization**: Ensure agents run efficiently with minimal resource waste
2. **Rapid Debugging**: Quickly identify and fix agent behavior issues
3. **Inference Flexibility**: Easily switch between providers based on cost/latency needs
4. **Productivity**: Spend less time on CLI commands, more time on agent development

### Pain Points
| Pain Point | Current Impact | Desired Outcome |
|------------|----------------|-----------------|
| No GPU visibility | Can't optimize resource allocation | Real-time GPU metrics dashboard |
| Scattered logs | 10+ minutes to find relevant logs | Unified log viewer with search |
| CLI-only policy changes | Risk of typos, slow iteration | Visual policy editor |
| No inference comparison | Manual testing per provider | Side-by-side provider comparison |
| Workspace navigation | Terminal file browsing only | Visual file browser with editing |

### User Journeys

#### Journey 1: Debugging a Malfunctioning Agent
**Scenario**: Agent is throwing errors, need to investigate

**Steps**:
1. Opens dashboard → Engineer view (default)
2. Sees sandbox list with error indicator on "Agent-7"
3. Clicks on "Agent-7" to open detail view
4. Views recent logs with ERROR level filter
5. Identifies issue: Out of memory during inference
6. Checks GPU metrics → 95% memory utilization
7. Switches to lighter inference profile via dropdown
8. Restarts sandbox
9. Monitors GPU metrics to confirm fix

**Time Saved**: 15 minutes vs 45 minutes with CLI

#### Journey 2: Optimizing Inference Provider
**Scenario**: Need to evaluate NVIDIA NIM vs local Ollama for cost/latency

**Steps**:
1. Navigates to "Inference Router" section
2. Views current provider cards with latency indicators
3. Clicks "Test" on NIM card
4. Runs benchmark test (built-in UI)
5. Switches to Ollama card, runs same test
6. Compares results in side-by-side view
7. Switches production routing to Ollama
8. Monitors performance impact over next hour

**Time Saved**: 5 minutes vs 30 minutes manual testing

#### Journey 3: Creating New Sandbox
**Scenario**: Need isolated environment for testing new agent version

**Steps**:
1. Clicks "New Sandbox" button
2. Selects base template from dropdown
3. Configures workspace directory via file picker
4. Selects inference provider
5. Reviews policy summary
6. Clicks "Create"
7. Watches real-time creation progress
8. Sandbox appears in list, starts automatically

**Time Saved**: 2 minutes vs 10 minutes CLI commands

### Required Features
- [ ] Sandbox list with status indicators
- [ ] Real-time GPU telemetry (utilization, memory, temperature)
- [ ] Unified log viewer with filtering and search
- [ ] Inference provider management UI
- [ ] Workspace file browser with basic editing
- [ ] Sandbox creation wizard
- [ ] Resource usage alerts (configurable thresholds)
- [ ] Performance comparison tools

### Success Metrics
- Can create new sandbox in <2 minutes
- Can find relevant logs in <30 seconds
- Can switch inference provider in <1 minute
- GPU metrics update within 5 seconds of change

---

## 2. Sarah - Security Operations Analyst

### Detailed Profile
**Name**: Sarah Martinez  
**Role**: Security Operations Analyst  
**Experience**: 4 years in SOC, 1 year with AI security  
**Technical Level**: Intermediate (security-focused)  
**Daily Tasks**:
- Monitoring agent network activity
- Investigating suspicious behavior
- Approving/denying network requests
- Documenting security incidents
- Coordinating with Engineering on policy violations

### Goals & Motivations
1. **Threat Detection**: Quickly identify anomalous agent behavior
2. **Incident Response**: Respond to security events within SLA
3. **Forensic Analysis**: Reconstruct agent decision paths during incidents
4. **Policy Enforcement**: Ensure network policies are properly applied

### Pain Points
| Pain Point | Current Impact | Desired Outcome |
|------------|----------------|-----------------|
| Manual request approval | CLI commands for each request | One-click approve/deny in UI |
| No agent relationship view | Can't see lateral movement risk | Visual attack graph |
| Alert fatigue | Multiple monitoring tools | Single-pane alert view |
| No decision context | Can't understand why agent acted | Forensic timeline replay |
| Delayed escalation | Manual escalation processes | HITL queue with auto-escalation |

### User Journeys

#### Journey 1: Responding to Suspicious Network Request
**Scenario**: Agent attempting to access external API not in allowlist

**Steps**:
1. Dashboard alert appears (SecOps view)
2. Navigates to "Request Queue"
3. Sees high-priority request with risk score 75/100
4. Views request details: Agent, URL, headers, context
5. Checks agent's recent activity in timeline
6. Identifies pattern: Agent making unexpected API calls
7. Denies request
8. Adds policy rule to block this pattern
9. Creates incident ticket with auto-populated details
10. Sets agent reputation to "under review"

**Time Saved**: 3 minutes vs 15 minutes manual investigation

#### Journey 2: Investigating Agent Anomaly
**Scenario**: Agent reputation score dropped significantly

**Steps**:
1. Receives alert: Agent-3 reputation dropped from 85 to 45
2. Opens "Agent Reputation" dashboard
3. Views signal breakdown for Agent-3
4. Identifies negative signals:
   - 5 blocked network requests
   - Unusual file access patterns
   - High token consumption
5. Opens forensic timeline
6. Replays agent decisions from last hour
7. Discovers agent was attempting data exfiltration
8. Quarantines sandbox immediately
9. Generates incident report with full timeline

**Time Saved**: 10 minutes vs 1 hour manual log analysis

#### Journey 3: HITL Adjudication
**Scenario**: Agent requests high-risk action requiring human approval

**Steps**:
1. HITL alert appears in queue
2. Opens adjudication view
3. Reviews full context:
   - Agent goal and current task
   - Proposed action with risk assessment
   - Similar historical decisions
4. Sees 5-minute SLA timer
5. Clicks "Request More Info" → adds question
6. Agent provides additional context
7. Evaluates new information
8. Clicks "Approve with Constraints"
9. Adds time limit and logging requirements
10. Action executes with applied constraints

**Time Saved**: Immediate vs back-and-forth via tickets

### Required Features
- [ ] Real-time request approval queue
- [ ] Risk scoring visualization per request
- [ ] Agent reputation dashboard with trends
- [ ] Attack graph visualization (Neo4j-powered)
- [ ] Forensic timeline with replay capability
- [ ] HITL adjudication interface
- [ ] Incident creation and documentation
- [ ] Policy violation alerts
- [ ] Automated threat detection indicators
- [ ] Quarantine controls for compromised agents

### Success Metrics
- Mean time to approve/deny request: <30 seconds
- Mean time to detect policy violation: <1 minute
- Can investigate agent anomaly in <5 minutes
- False positive rate for alerts: <5%

---

## 3. Michael - CISO

### Detailed Profile
**Name**: Michael Thompson  
**Role**: Chief Information Security Officer  
**Experience**: 15+ years in security, 3 years with AI governance  
**Technical Level**: High-level strategic (not hands-on)  
**Daily Tasks**:
- Reporting to board on AI security posture
- Ensuring regulatory compliance
- Setting security policies and governance
- Managing security budget and ROI
- Coordinating with legal on AI regulations

### Goals & Motivations
1. **Regulatory Compliance**: Demonstrate adherence to AI regulations (EU AI Act, NIST AI RMF)
2. **Risk Visibility**: Understand organizational AI risk posture
3. **Board Reporting**: Provide executive-level security metrics
4. **Governance**: Establish and enforce AI usage policies

### Pain Points
| Pain Point | Current Impact | Desired Outcome |
|------------|----------------|-----------------|
| No consolidated view | Data scattered across tools | Single compliance dashboard |
| Manual report creation | 2 days per board report | One-click executive reports |
| Unclear policy coverage | Don't know what's protected | Policy coverage matrix |
| No risk trends | Reactive security posture | Predictive risk analysis |
| Shadow AI unknown | Undocumented AI usage | Shadow AI discovery |

### User Journeys

#### Journey 1: Preparing Board Report
**Scenario**: Quarterly board meeting, need AI security status

**Steps**:
1. Opens dashboard → CISO view
2. Navigates to "Executive Summary"
3. Reviews auto-generated quarterly report:
   - Compliance posture (92% NIST AI RMF)
   - Risk trend (down 15% from last quarter)
   - Incident summary (3 minor, 0 major)
   - Cost of security vs risk reduction
4. Drills into specific frameworks:
   - NIST AI RMF: 45/49 controls compliant
   - ISO 42001: 38/42 controls compliant
5. Exports report to PowerPoint format
6. Reviews slide deck (auto-formatted)
7. Schedules automated monthly reports

**Time Saved**: 30 minutes vs 2 days manual compilation

#### Journey 2: Assessing New AI Project Risk
**Scenario**: Business unit requesting approval for new AI agent

**Steps**:
1. Opens "Risk Assessment" tool
2. Enters project details:
   - Agent type, data sensitivity, exposure level
3. System generates risk score: 67/100 (Medium-High)
4. Views recommended controls:
   - Sandboxing requirements
   - Network policy templates
   - Monitoring recommendations
5. Checks policy coverage for this use case
6. Identifies gaps: No egress filtering defined
7. Creates policy requirement for project
8. Approves with conditions
9. Dashboard auto-configures monitoring for project

**Time Saved**: 1 hour vs 3 days manual assessment

#### Journey 3: Responding to Audit Request
**Scenario**: External auditor requesting AI security evidence

**Steps**:
1. Navigates to "Compliance Center"
2. Selects audit scope: ISO 42001 Section 4-7
3. System gathers evidence:
   - Policy configurations
   - Access logs
   - Incident reports
   - Training records
4. Reviews evidence package
5. Exports to PDF with evidence mapping
6. Provides auditor with read-only dashboard access
7. Monitors auditor questions in real-time
8. Responds to clarification requests

**Time Saved**: 4 hours vs 2 weeks evidence gathering

#### Journey 4: Monitoring Shadow AI
**Scenario**: Suspect unauthorized AI usage in organization

**Steps**:
1. Opens "Shadow AI Discovery" panel
2. Views discovered AI endpoints:
   - Known managed agents (green)
   - Discovered unmanaged endpoints (amber)
   - High-risk endpoints (red)
3. Identifies 3 new OpenAI API calls from unknown source
4. Drills down to source IP and user
5. Initiates "Bring into Management" workflow
6. Creates policy for discovered endpoint
7. Adds to monitoring dashboard

**Time Saved**: Immediate visibility vs weeks to discover

### Required Features
- [ ] Compliance posture dashboard (NIST AI RMF, ISO 42001)
- [ ] Risk trend analysis with forecasting
- [ ] Executive summary report generator
- [ ] Policy coverage matrix
- [ ] Audit evidence collection and export
- [ ] Shadow AI discovery dashboard
- [ ] Cost-to-security ratio metrics
- [ ] Framework mapping and gap analysis
- [ ] Board-ready visualizations
- [ ] Automated report scheduling

### Success Metrics
- Board report generation: <30 minutes
- Audit response time: <1 day
- Compliance visibility: 100% of AI projects
- Shadow AI discovery: <24 hours from deployment

---

## 4. Cross-Persona Features

### Features Used by Multiple Personas

| Feature | Engineer | SecOps | CISO | Description |
|---------|----------|--------|------|-------------|
| Sandbox Status | Primary | Secondary | View | View sandbox health |
| Network Requests | View | Primary | View | Monitor outbound traffic |
| Logs | Primary | Primary | View | Unified logging |
| Policies | Edit | Edit | Approve | Security rules |
| GPU Metrics | Primary | View | View | Resource utilization |
| Agent Reputation | View | Primary | View | Trust scoring |
| Alerts | View | Primary | View | Notification center |
| Reports | View | Generate | Primary | Analytics and summaries |

### Collaboration Workflows

#### Workflow 1: Security Incident Response
1. **SecOps detects** anomaly via alert
2. **SecOps investigates** using forensic tools
3. **SecOps escalates** to Engineer if configuration issue
4. **Engineer investigates** technical root cause
5. **Engineer fixes** and updates SecOps
6. **SecOps documents** incident
7. **CISO reviews** during weekly security review

#### Workflow 2: New Agent Deployment
1. **Engineer requests** new sandbox
2. **SecOps reviews** policy implications
3. **SecOps approves** with specific guardrails
4. **Engineer deploys** agent
5. **SecOps monitors** initial behavior
6. **CISO reviews** deployment metrics weekly

#### Workflow 3: Policy Change
1. **SecOps identifies** policy gap
2. **SecOps drafts** policy change
3. **Engineer reviews** for operational impact
4. **CISO approves** policy change
5. **SecOps implements** via dashboard
6. **Engineer verifies** agent functionality

---

## 5. Feature Prioritization Matrix

### By Persona Impact

| Feature | Engineer Impact | SecOps Impact | CISO Impact | Priority |
|---------|----------------|---------------|-------------|----------|
| Sandbox Management | High | Medium | Low | P0 |
| Network Request Queue | Low | High | Medium | P0 |
| GPU Telemetry | High | Low | Low | P0 |
| Unified Logs | High | High | Low | P0 |
| Agent Reputation | Low | High | Medium | P1 |
| Attack Graph | Low | High | Medium | P1 |
| Compliance Dashboard | Low | Low | High | P1 |
| HITL Adjudication | Low | High | Low | P1 |
| Forensic Timeline | Medium | High | Medium | P2 |
| Executive Reports | Low | Low | High | P2 |
| Shadow AI Discovery | Low | Medium | High | P2 |
| Policy Editor | High | High | Low | P2 |

### By Implementation Complexity

| Feature | Complexity | Value | Priority |
|---------|------------|-------|----------|
| Sandbox List | Low | High | P0 |
| Log Viewer | Medium | High | P0 |
| GPU Metrics | Medium | High | P0 |
| Request Queue | Medium | High | P0 |
| Agent Reputation | High | High | P1 |
| Attack Graph | High | High | P1 |
| Compliance Dashboard | Medium | High | P1 |
| HITL Queue | Medium | Medium | P1 |
| Forensic Timeline | High | Medium | P2 |
| Executive Reports | Low | Medium | P2 |
| Shadow AI Discovery | High | Medium | P2 |

---

## 6. User Interface Preferences

### By Persona

#### Engineer Preferences
- **Density**: High information density preferred
- **Layout**: Grid-based dashboard with many widgets
- **Colors**: Functional, data-driven color schemes
- **Interactivity**: High - lots of clickable elements
- **Navigation**: Keyboard shortcuts, quick actions
- **Data**: Raw metrics, detailed logs, performance charts

#### SecOps Preferences
- **Density**: Medium - balance of overview and detail
- **Layout**: Queue-based, alert-focused layouts
- **Colors**: Status-driven (red/amber/green indicators)
- **Interactivity**: Medium - focused on investigation tools
- **Navigation**: Alert-driven navigation
- **Data**: Risk scores, threat indicators, forensic data

#### CISO Preferences
- **Density**: Low - clean, summary views
- **Layout**: Report-style, high-level overview
- **Colors**: Professional, board-ready aesthetics
- **Interactivity**: Low - mostly view and export
- **Navigation**: Section-based, report-oriented
- **Data**: Aggregated metrics, trend lines, compliance scores

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
