# NemoClaw Gateway Dashboard - Conceptual Design Document

## Phase: Ideation (v0.1.0)

---

## 1. Problem Statement

### Current State
NemoClaw and OpenShell provide powerful capabilities for running AI agents securely, but managing these tools currently requires:
- Command-line interface knowledge
- Manual monitoring of multiple log files
- Text-based network request approvals
- No centralized visibility into agent behavior

### Desired State
A unified, visual dashboard that:
- Runs locally alongside NemoClaw installation
- Provides real-time visibility into all agent activities
- Enables quick policy management without CLI commands
- Offers persona-specific views for different stakeholders
- Maintains zero-trust security principles

---

## 2. Design Principles

### 2.1 Local-First Architecture
- **No cloud dependency** - Dashboard runs entirely on local machine
- **Data sovereignty** - All telemetry and logs remain local
- **Zero external calls** - Core functionality works offline
- **Localhost binding** - Dashboard accessible only from local machine

### 2.2 Safe-by-Default UI
- **Fail-closed indicators** - Clear visual warnings when safety systems are down
- **Explicit approvals** - No implicit permissions, all actions require confirmation
- **Audit trail** - Every UI action logged with user attribution
- **Read-only defaults** - Views default to read-only, edits require elevation

### 2.3 Persona-Driven Design
- **Context switching** - UI adapts based on user's role
- **Relevant information** - Each persona sees only what they need
- **Action-appropriate** - Available actions match persona's responsibilities
- **Progressive disclosure** - Advanced features hidden behind role gates

---

## 3. Dual-Mode Architecture

The NemoClaw Gateway Dashboard is architected to support **two distinct operational modes** while maintaining a unified codebase and user experience.

### 3.1 Personal Mode (Individual/Small Team)

**Philosophy**: Maximum simplicity with minimal overhead

**Key Characteristics**:
- **Zero configuration**: Install and run immediately
- **Single-user ownership**: One administrator controls everything
- **Local-first**: All data stays on user's machine
- **OS-level security**: Relies on system permissions
- **No authentication friction**: Direct access to all features

**Architecture Decisions**:
- SQLite for local data storage (optional)
- File-based configuration (YAML/JSON)
- Direct subprocess calls to OpenShell CLI
- Local file system for logs and telemetry
- Streamlit's built-in server (localhost only)

**Use Cases**:
- Individual AI researchers
- Developers testing agents locally
- Small teams (< 5 people) with shared workstation
- Proof-of-concept deployments

### 3.2 Enterprise Mode (Organization/Scale)

**Philosophy**: Governance, oversight, and compliance at scale

**Key Characteristics**:
- **Multi-tenancy**: Support for multiple teams/departments
- **Strong authentication**: SSO, LDAP, OAuth2 integration
- **Granular access control**: RBAC/ABAC with fine-grained permissions
- **Centralized governance**: Organization-wide policies
- **Comprehensive audit trail**: All actions logged and traceable

**Architecture Decisions**:
- PostgreSQL for user data and audit logs
- Redis for session management and caching
- Authentication middleware (OAuth2/OIDC)
- API gateway for centralized control
- Distributed deployment support (K8s/Docker)
- SIEM integration capabilities

**Use Cases**:
- Enterprise AI teams with compliance requirements
- Organizations with multiple projects
- Regulated industries (finance, healthcare, government)
- Production deployments requiring SLA guarantees

### 3.3 Unified Core, Modular Extensions

Both modes share **80% of the codebase**:

```
┌─────────────────────────────────────────────────────────┐
│                    CORE LAYER (Shared)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Sandbox    │  │     GPU      │  │     Logs     │  │
│  │  Management  │  │  Monitoring  │  │   & Traces   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Policy     │  │   Network    │  │  Workspace   │  │
│  │   Engine     │  │   Requests   │  │    Browser   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   PERSONAL   │  │  ENTERPRISE  │  │   SHARED     │
│    LAYER     │  │    LAYER     │  │   LAYER      │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ • No auth    │  │ • RBAC/ABAC  │  │ • Streamlit  │
│ • Local DB   │  │ • Auth DB    │  │ • Plotly     │
│ • File logs  │  │ • Audit DB   │  │ • Pydantic   │
│ • Direct CLI │  │ • API layer  │  │ • OpenShell  │
└──────────────┘  │ • Workflow   │  └──────────────┘
                  │   engine     │
                  │ • SIEM conn  │
                  └──────────────┘
```

### 3.4 Mode Detection and Activation

The dashboard **automatically detects** which mode to run in:

```python
# Pseudo-configuration
def get_deployment_mode():
    if os.getenv('ENTERPRISE_MODE') == 'true':
        return DeploymentMode.ENTERPRISE
    elif os.path.exists('/etc/nemoclaw/enterprise.yaml'):
        return DeploymentMode.ENTERPRISE
    else:
        return DeploymentMode.PERSONAL  # Default

# Mode-specific features
if mode == DeploymentMode.ENTERPRISE:
    enable_authentication()
    enable_audit_logging()
    enable_workflow_engine()
else:
    # Personal mode - keep it simple
    pass
```

### 3.5 Graduated Feature Matrix

| Feature | Personal | Enterprise |
|---------|----------|------------|
| **Sandbox Management** | ✅ Full access | ✅ Role-based |
| **GPU Monitoring** | ✅ Full access | ✅ Role-based |
| **Log Viewer** | ✅ Local only | ✅ With audit trails |
| **Policy Management** | ✅ Local policies | ✅ Org-wide policies |
| **Network Requests** | ✅ Approve/Deny | ✅ With approval workflows |
| **User Authentication** | ❌ None | ✅ Required |
| **RBAC/ABAC** | ❌ None | ✅ Full support |
| **Audit Logging** | ✅ Local files | ✅ Centralized DB |
| **Workflow Approvals** | ❌ None | ✅ Multi-stage |
| **Multi-tenancy** | ❌ None | ✅ Teams/Projects |
| **SIEM Integration** | ❌ None | ✅ Splunk/Elastic |
| **High Availability** | ❌ None | ✅ K8s/Docker |

### 3.5 Multi-Instance Support

Both Personal and Enterprise modes support **managing multiple NemoClaw installations** from a single dashboard:

| Aspect | Personal Multi-Instance | Enterprise Multi-Instance |
|--------|------------------------|---------------------------|
| **Use Case** | Local + remote GPU server | Multi-region, multi-team |
| **Connection** | Local subprocess, SSH | API (REST), Agent |
| **Authentication** | SSH keys, OS-level | OAuth2, mTLS, Vault |
| **Scale** | 2-5 instances | 10-100+ instances |
| **Operations** | Per-instance | Cross-instance (fleet-wide) |

**Instance Types**:
- **Local**: Direct subprocess on same machine
- **SSH**: Remote server via SSH tunnel
- **API**: Enterprise REST API endpoint
- **Agent**: Air-gapped with local agent proxy

**Unified View**: Users see a single dashboard that aggregates sandboxes, metrics, and alerts from all configured instances, with the ability to drill down into specific instances.

**Personal → Enterprise Migration Path**:

1. **Export Phase** (Personal mode)
   - Export all sandbox configurations
   - Export policy definitions
   - Export workspace files

2. **Deploy Phase** (Enterprise infrastructure)
   - Set up authentication provider
   - Deploy dashboard with enterprise config
   - Configure PostgreSQL database
   - Set up Redis for sessions

3. **Import Phase**
   - Import sandbox configurations
   - Import policies as org templates
   - Map local users to enterprise identities

4. **Enable Phase**
   - Configure RBAC roles
   - Set up approval workflows
   - Enable audit logging
   - Connect SIEM tools

**Code Reuse**: The same Python codebase runs both modes - only configuration and optional middleware differ.

---

## 4. User Personas

### 3.1 Alex - AI Engineer
**Profile**: ML Engineer developing and debugging AI agents

**Goals**:
- Monitor agent performance and resource usage
- Debug agent behavior through logs and traces
- Manage sandbox configurations
- Optimize inference routing

**Pain Points**:
- No visibility into GPU utilization
- Difficult to correlate agent actions with resource consumption
- Scattered log files across multiple sandboxes
- No easy way to test inference providers

**Needs**:
- Real-time GPU metrics dashboard
- Sandbox status overview with quick actions
- Unified log viewer with filtering
- Inference provider switching UI
- Workspace file browser

### 3.2 Sarah - Security Operations Analyst
**Profile**: SecOps analyst monitoring for threats and policy violations

**Goals**:
- Monitor network requests for suspicious activity
- Investigate agent behavior anomalies
- Respond to policy violations in real-time
- Maintain forensic records of incidents

**Pain Points**:
- Network requests require manual CLI approval
- No visualization of agent relationships
- Difficult to trace agent decision paths
- Alert fatigue from scattered monitoring tools

**Needs**:
- Network request approval queue with context
- Agent reputation scoring visualization
- Attack path visualization
- Forensic timeline browser
- HITL adjudication interface
- Real-time threat alerts

### 3.3 Michael - CISO
**Profile**: Chief Information Security Officer responsible for AI governance

**Goals**:
- Ensure AI deployment compliance
- Understand organizational risk posture
- Report on AI security metrics to board
- Establish governance policies

**Pain Points**:
- No consolidated view of AI risk
- Difficult to prove compliance with AI regulations
- Limited visibility into shadow AI usage
- No executive-friendly reporting

**Needs**:
- Compliance posture dashboard (NIST AI RMF, ISO 42001)
- Risk trend analysis with historical data
- Executive summary reports
- Policy coverage overview
- Cost-to-security metrics

---

## 4. Conceptual Architecture

### 4.1 High-Level Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     BROWSER LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Engineer  │  │   SecOps    │  │    CISO     │          │
│  │    View     │  │    View     │  │    View     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     DASHBOARD LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Next.js Application                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │   │
│  │  │   UI     │ │   State  │ │   Auth   │ │ Routing │ │   │
│  │  │Components│ │ Management│ │  Layer  │ │         │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OpenShell    │  │   File System │  │   Process    │      │
│  │ CLI Wrapper  │  │   Watcher     │  │   Monitor    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     NEMOCLAW LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Sandboxes│  │ Policies │  │Workspaces│  │  Agents  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Component Breakdown

#### Dashboard Layer (Next.js)
- **UI Components**: shadcn/ui-based component library
- **State Management**: React hooks + Context for local state
- **Persona System**: Role-based view switching
- **Real-time Updates**: Server-Sent Events for live data

#### Integration Layer (Node.js)
- **OpenShell Service**: Wrapper around openshell CLI commands
- **File Watcher**: Monitors workspace and config file changes
- **Process Monitor**: Tracks agent processes and GPU metrics
- **Local API**: RESTful endpoints for dashboard consumption

#### NemoClaw Layer (System)
- **Sandboxes**: Isolated agent environments
- **Policies**: Network and behavior rules
- **Workspaces**: Agent file storage
- **Agents**: Running AI agent instances

---

## 5. Key Concepts

### 5.1 Persona Context
The dashboard maintains a "current persona" context that determines:
- Which navigation items are visible
- What actions are available
- Which dashboard widgets are displayed
- Default views and filters

**Context Switching**:
- Persona selector in header
- Deep linking preserves persona context
- Session persistence of last used persona
- URL-based persona routing (/engineer, /secops, /ciso)

### 5.2 Real-Time Data Flow
- **Polling Strategy**: 5-second refresh for sandbox status
- **Event Stream**: Server-Sent Events for network requests
- **File Watching**: fs.watch for configuration changes
- **WebSocket Alternative**: For future multi-user support

### 5.3 Security Model
- **Localhost Only**: Dashboard binds to 127.0.0.1
- **OS Authentication**: Leverages system user permissions
- **Action Logging**: All changes logged with user attribution
- **No Secrets in UI**: API keys, tokens never displayed in full

---

## 6. Feature Concepts

### 6.1 Engineer View Features

#### Sandbox Manager
- **Concept**: Card-based view of all sandboxes
- **Features**:
  - Status badges (Running, Stopped, Error)
  - Quick actions (Start, Stop, Restart)
  - Resource usage indicators
  - Last activity timestamp
  - Configuration summary

#### GPU Telemetry Dashboard
- **Concept**: Real-time GPU monitoring widgets
- **Features**:
  - Utilization percentage with sparkline
  - Memory usage (used/total)
  - Temperature gauge
  - Power consumption
  - Historical trends (1h, 24h, 7d)

#### Inference Router
- **Concept**: Visual provider selection and testing
- **Features**:
  - Provider cards (NVIDIA NIM, Ollama, LM Studio, OpenAI)
  - Latency indicators per provider
  - Quick test interface
  - Routing rule configuration

#### Unified Log Viewer
- **Concept**: Centralized log browser with powerful filtering
- **Features**:
  - Multi-sandbox log aggregation
  - Severity filtering (DEBUG, INFO, WARN, ERROR)
  - Full-text search
  - Timestamp range selection
  - Export functionality

### 6.2 SecOps View Features

#### Network Request Queue
- **Concept**: Approval workflow for outbound requests
- **Features**:
  - Request list with source agent, destination, method
  - Risk score indicator per request
  - One-click approve/deny
  - Batch selection for bulk actions
  - Request detail modal with context

#### Agent Reputation Dashboard
- **Concept**: Scoring system for agent trustworthiness
- **Features**:
  - Score cards for each agent (0-100)
  - Trend indicators (improving/declining)
  - Signal breakdown (positive/negative factors)
  - Auto-action configuration (quarantine threshold)

#### Attack Graph Visualization
- **Concept**: Neo4j-powered relationship mapping
- **Features**:
  - Interactive graph of users, agents, models, tools, data stores
  - Attack path highlighting
  - Risk weight visualization on edges
  - Drill-down into node details
  - Historical graph snapshots

#### Forensic Timeline
- **Concept**: Time-based replay of agent decisions
- **Features**:
  - Timeline scrubber for time selection
  - Agent thought process reconstruction
  - Decision tree visualization
  - Context snapshot at any point in time
  - Export incident reports

#### HITL Adjudication Queue
- **Concept**: Human approval for high-risk actions
- **Features**:
  - Frozen action list awaiting approval
  - Full context preview
  - Approve/Deny/Override options
  - SLA timer for response urgency
  - Escalation rules

### 6.3 CISO View Features

#### Compliance Posture Dashboard
- **Concept**: NIST AI RMF and ISO 42001 compliance tracking
- **Features**:
  - Framework selection toggle
  - Control mapping visualization
  - Compliance percentage by category
  - Gap identification
  - Evidence collection status

#### Risk Trend Analysis
- **Concept**: Historical risk metrics visualization
- **Features**:
  - Risk score trends over time
  - Incident frequency charts
  - Mean time to detection (MTTD)
  - Mean time to response (MTTR)
  - Predictive risk forecasting

#### Executive Summary
- **Concept**: Board-ready reporting interface
- **Features**:
  - One-page summary view
  - Key metrics at a glance
  - Period comparison (MoM, QoQ, YoY)
  - Export to PDF/PowerPoint
  - Scheduled report generation

#### Policy Coverage Matrix
- **Concept**: Visual policy enforcement overview
- **Features**:
  - Policy catalog with coverage indicators
  - Sandbox coverage percentage
  - Policy conflict detection
  - Recommendation engine for gaps

---

## 7. Data Models (Conceptual)

### 7.1 Core Entities

#### Sandbox
```typescript
interface Sandbox {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error' | 'pending';
  agent: AgentConfig;
  workspace: WorkspaceConfig;
  policies: PolicyRef[];
  resources: ResourceUsage;
  createdAt: Date;
  updatedAt: Date;
}
```

#### NetworkRequest
```typescript
interface NetworkRequest {
  id: string;
  sandboxId: string;
  agentId: string;
  method: string;
  url: string;
  headers: Record<string, string>;
  timestamp: Date;
  status: 'pending' | 'approved' | 'denied';
  riskScore: number;
  context: RequestContext;
}
```

#### AgentReputation
```typescript
interface AgentReputation {
  agentId: string;
  sandboxId: string;
  score: number; // 0-100
  trend: 'improving' | 'stable' | 'declining';
  signals: ReputationSignal[];
  lastUpdated: Date;
}
```

#### ComplianceControl
```typescript
interface ComplianceControl {
  id: string;
  framework: 'nist-airmf' | 'iso-42001';
  category: string;
  controlId: string;
  description: string;
  status: 'compliant' | 'non-compliant' | 'partial';
  evidence: Evidence[];
  lastAssessed: Date;
}
```

---

## 8. UI/UX Concepts

### 8.1 Layout Concepts

#### Sidebar Navigation
- **Collapsible**: Collapses to icons-only on small screens
- **Persona-aware**: Different items per persona
- **Status indicators**: Connection status, alert counts
- **Quick actions**: Common tasks accessible from any view

#### Dashboard Grid
- **Widget-based**: Modular widgets users can arrange
- **Responsive**: Adapts to screen size
- **Draggable**: (Future) Customizable layout
- **Contextual**: Widgets change based on selected sandbox

### 8.2 Visual Design Concepts

#### Color System
- **Primary**: NVIDIA Green (#76B900) for brand alignment
- **Status Colors**:
  - Success: Green
  - Warning: Amber
  - Error: Red
  - Info: Blue
  - Neutral: Gray
- **Dark Mode**: Default to reduce eye strain

#### Typography
- **Font**: Inter or system sans-serif
- **Hierarchy**: Clear H1-H6 distinction
- **Monospace**: JetBrains Mono for logs and code

#### Iconography
- **Library**: Lucide React icons
- **Consistency**: Semantic icon usage
- **Accessibility**: Labels for all icons

### 8.3 Interaction Concepts

#### Real-time Indicators
- **Pulsing dots**: For live/running status
- **Sparklines**: Mini charts in table cells
- **Tooltips**: Hover for additional context
- **Skeletons**: Loading state placeholders

#### Data Tables
- **Sorting**: Column header sorting
- **Filtering**: Column filters and global search
- **Pagination**: Configurable rows per page
- **Selection**: Checkbox row selection
- **Actions**: Row-level action buttons

#### Forms
- **Validation**: Inline validation with clear errors
- **Auto-save**: For long forms
- **Confirmation**: Destructive actions require confirmation
- **Progress**: Multi-step form progress indicators

---

## 9. Integration Points

### 9.1 OpenShell CLI Integration

**Command Mapping**:
```
openshell list sandboxes     → GET /api/sandboxes
openshell sandbox start <id> → POST /api/sandboxes/:id/start
openshell logs <id>          → GET /api/sandboxes/:id/logs
openshell policy list        → GET /api/policies
openshell request list       → GET /api/requests
```

**Output Parsing**:
- JSON mode for structured data
- Streaming for real-time logs
- Exit code handling for errors

### 9.2 File System Integration

**Watch Directories**:
- `~/.openshell/sandboxes/` - Sandbox configurations
- `~/.openshell/policies/` - Policy definitions
- `~/.openshell/logs/` - Log files
- `~/.openshell/workspaces/` - Workspace files

**File Operations**:
- Read configuration files
- Stream log files
- Monitor file changes
- Backup/restore operations

### 9.3 System Integration

**GPU Metrics**:
- `nvidia-smi` for GPU telemetry
- NVML library (future) for programmatic access
- DCGM for advanced metrics (enterprise)

**Process Monitoring**:
- Process list for agent processes
- Resource usage per process
- Health check endpoints

---

## 10. Security & Privacy Concepts

### 10.1 Local Security Model

**Network Binding**:
- Dashboard binds to `127.0.0.1:3000` only
- No external network exposure
- (Future) Option to bind to specific interface

**Authentication**:
- OS-level user authentication
- No separate login credentials
- Leverage file system permissions

**Authorization**:
- Persona selection is preference, not privilege
- All users can see all views
- (Future) Role-based access control

### 10.2 Data Privacy

**Local Data Only**:
- No telemetry sent externally
- No cloud dependencies
- Optional offline mode

**Sensitive Data Handling**:
- API keys masked in UI
- Secrets not logged
- Session timeout for inactivity

---

## 11. Future Considerations

### 11.1 Potential Enhancements

#### Multi-User Support
- User authentication system
- Role-based access control
- Audit logging per user
- Session management

#### Remote Access
- Secure tunnel for remote access
- VPN integration
- Mobile app companion

#### AI-Powered Features
- Anomaly detection in agent behavior
- Automated policy recommendations
- Natural language log querying
- Predictive risk scoring

#### Integration Ecosystem
- SIEM integration (Splunk, Elastic)
- Ticketing system integration (Jira, ServiceNow)
- Slack/Teams notifications
- Webhook support

### 11.2 Scalability Considerations

#### Multi-Cluster Support
- Connect to multiple NemoClaw installations
- Cluster comparison views
- Cross-cluster policy management

#### Enterprise Features
- LDAP/SSO integration
- Audit log retention policies
- High availability mode
- Disaster recovery

---

## 12. Success Metrics

### 12.1 User Experience
- Time to complete common tasks (target: <30 seconds)
- Persona switching efficiency
- Dashboard load time (target: <2 seconds)
- Error rate (target: <1%)

### 12.2 Security Effectiveness
- Mean time to detect policy violations
- Mean time to approve/deny requests
- False positive rate for alerts
- User satisfaction with security controls

### 12.3 Operational Efficiency
- Reduction in CLI command usage
- Time saved in log analysis
- Faster incident response
- Improved compliance audit efficiency

---

## 13. Open Questions

1. Should the dashboard support multiple NemoClaw installations?
2. How should we handle authentication for multi-user scenarios?
3. What is the appropriate refresh interval for real-time data?
4. Should we support custom policy rule authoring in the UI?
5. How do we handle large log files (GBs) efficiently?
6. What level of mobile support is needed?
7. Should we integrate with external monitoring tools?
8. How do we handle offline scenarios?

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
