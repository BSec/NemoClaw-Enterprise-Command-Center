# NemoClaw Gateway Dashboard - Data Models & API Contracts

## Phase: Ideation (v0.1.0)

---

## 1. Data Models

### 1.1 Core Entities

#### Sandbox
```typescript
interface Sandbox {
  // Identity
  id: string;                    // Unique identifier (e.g., "sandbox-7a3b9c")
  name: string;                  // Human-readable name (e.g., "Agent-7")
  description?: string;         // Optional description
  
  // Status
  status: SandboxStatus;         // 'running' | 'stopped' | 'error' | 'pending' | 'quarantined'
  statusMessage?: string;       // Detailed status (e.g., error message)
  
  // Configuration
  agent: AgentConfig;           // Agent configuration
  workspace: WorkspaceConfig;   // Workspace settings
  inference: InferenceConfig;   // Inference provider settings
  policies: PolicyRef[];        // Applied policies
  
  // Resources
  resources: ResourceUsage;     // Current resource consumption
  limits: ResourceLimits;       // Resource constraints
  
  // Metadata
  createdAt: DateTime;
  updatedAt: DateTime;
  createdBy: string;            // User who created sandbox
  lastActivityAt?: DateTime;    // Last observed activity
  uptime?: Duration;            // Total running time
  
  // Security
  reputation: AgentReputation;  // Current reputation score
  quarantineReason?: string;    // If status is 'quarantined'
}

type SandboxStatus = 
  | 'running'      // Active and processing
  | 'stopped'      // Gracefully stopped
  | 'error'        // Error state, needs attention
  | 'pending'      // Starting up
  | 'quarantined'; // Security hold

interface AgentConfig {
  type: string;                 // Agent type (e.g., "openai", "anthropic")
  version: string;              // Agent version
  model: string;                // Model identifier
  systemPrompt?: string;        // System prompt/template
  capabilities: string[];       // Enabled capabilities
  environment: Record<string, string>; // Environment variables
}

interface WorkspaceConfig {
  path: string;                 // Filesystem path
  size: number;                 // Current size in bytes
  maxSize: number;              // Maximum allowed size
  files: number;                // Number of files
  backupEnabled: boolean;
  lastBackupAt?: DateTime;
}

interface InferenceConfig {
  provider: InferenceProvider;
  model: string;
  temperature: number;
  maxTokens: number;
  endpoint?: string;            // Custom endpoint if not default
  apiKeyRef: string;            // Reference to stored API key (masked)
}

type InferenceProvider = 
  | 'nvidia-nim'
  | 'ollama'
  | 'lm-studio'
  | 'openai'
  | 'anthropic'
  | 'custom';

interface ResourceUsage {
  cpu: CpuMetrics;
  memory: MemoryMetrics;
  gpu: GpuMetrics[];           // Multiple GPUs supported
  network: NetworkMetrics;
  disk: DiskMetrics;
}

interface GpuMetrics {
  index: number;                // GPU device index
  name: string;                 // GPU model name
  utilization: number;          // 0-100 percentage
  memoryUsed: number;          // MB
  memoryTotal: number;         // MB
  temperature: number;         // Celsius
  powerDraw: number;           // Watts
  powerLimit: number;          // Watts
  fanSpeed?: number;          // 0-100 percentage
  clockSpeed: {
    graphics: number;          // MHz
    memory: number;            // MHz
  };
  processes: GpuProcess[];      // Processes using this GPU
}

interface GpuProcess {
  pid: number;
  name: string;
  memoryUsed: number;          // MB
}
```

#### NetworkRequest
```typescript
interface NetworkRequest {
  // Identity
  id: string;                   // Unique request ID
  
  // Source
  sandboxId: string;           // Originating sandbox
  agentId: string;           // Originating agent
  processId: number;         // Process ID
  
  // Request Details
  timestamp: DateTime;       // When request was made
  method: HttpMethod;         // GET, POST, PUT, DELETE, etc.
  url: string;                // Full URL
  hostname: string;           // Extracted hostname
  port: number;               // Destination port
  path: string;               // URL path
  headers: Record<string, string>; // Request headers
  body?: string;             // Request body (truncated if large)
  bodySize: number;            // Body size in bytes
  
  // Risk Assessment
  riskScore: number;          // 0-100 calculated risk
  riskFactors: RiskFactor[];  // Why this risk score
  category: RequestCategory;  // Classification
  
  // Policy & Status
  status: RequestStatus;      // Current status
  decisionBy?: string;        // Who made the decision
  decisionAt?: DateTime;     // When decision was made
  decisionReason?: string;  // Rationale for decision
  policyId?: string;          // Which policy was applied
  
  // Context
  context: RequestContext;  // Surrounding activity
  similarRequests: number;    // Count of similar requests
  historicalApproval: 'always' | 'sometimes' | 'never' | 'new';
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS' | 'CONNECT';

type RequestStatus = 
  | 'pending'      // Awaiting approval
  | 'approved'     // Allowed through
  | 'denied'       // Blocked
  | 'auto-approved' // Allowed by policy
  | 'auto-denied'  // Blocked by policy
  | 'expired';     // Timed out waiting

type RequestCategory =
  | 'api'          // API endpoint
  | 'database'     // Database connection
  | 'file-transfer' // File upload/download
  | 'web'          // General web
  | 'internal'     // Internal network
  | 'suspicious'   // Flagged by analysis
  | 'blocked';     // Known bad destination

interface RiskFactor {
  type: string;               // Factor type
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;        // Human-readable explanation
  score: number;               // Points added to risk (0-100)
}

interface RequestContext {
  agentTask: string;          // What was the agent doing
  conversationId?: string;    // Related conversation
  previousRequests: string[]; // Recent requests from same agent
  fileAccesses: string[];     // Recent file operations
  toolCalls: string[];        // Recent tool invocations
}
```

#### AgentReputation
```typescript
interface AgentReputation {
  // Identity
  agentId: string;
  sandboxId: string;
  
  // Score
  currentScore: number;       // 0-100
  previousScore: number;      // Last period score
  trend: ReputationTrend;     // Direction of change
  
  // Time Boundaries
  calculatedAt: DateTime;
  periodStart: DateTime;      // Calculation window start
  periodEnd: DateTime;        // Calculation window end
  
  // Signals
  positiveSignals: ReputationSignal[];
  negativeSignals: ReputationSignal[];
  
  // History
  history: ReputationPoint[]; // Score over time
  
  // Actions
  lastAction?: ReputationAction; // Last automatic action taken
  quarantineThreshold: number; // Score that triggers quarantine
}

type ReputationTrend = 'improving' | 'stable' | 'declining' | 'critical';

interface ReputationSignal {
  type: string;               // Signal identifier
  category: 'behavior' | 'security' | 'performance' | 'compliance';
  weight: number;             // Impact on score (+/-)
  description: string;        // Human explanation
  occurrences: number;          // How many times observed
  firstSeen: DateTime;
  lastSeen: DateTime;
  evidence: SignalEvidence[];  // Supporting data
}

interface SignalEvidence {
  type: string;               // Evidence type
  timestamp: DateTime;
  data: unknown;               // Evidence data (context-specific)
}

interface ReputationPoint {
  timestamp: DateTime;
  score: number;
  reason?: string;            // Why score changed
}

interface ReputationAction {
  type: 'none' | 'warning' | 'restricted' | 'quarantined';
  triggeredAt: DateTime;
  triggeredBy: string;        // Policy or manual
  reason: string;
  resolvedAt?: DateTime;
  resolvedBy?: string;
}

// Signal Types (Examples)
type PositiveSignalType =
  | 'task_completion'           // Completed assigned task
  | 'low_error_rate'           // Few errors
  | 'efficient_token_usage'    // Good token-to-output ratio
  | 'approved_request_pattern' // Consistent good requests
  | 'policy_compliance'        // Following all policies
  | 'quick_response';          // Fast response times

type NegativeSignalType =
  | 'high_error_rate'          // Many errors
  | 'blocked_requests'         // Requests denied
  | 'unusual_file_access'      // Accessing unexpected files
  | 'excessive_token_usage'    // Inefficient usage
  | 'suspicious_timing'        // Activity at odd hours
  | 'repetitive_failures'      // Same action failing repeatedly
  | 'data_exfiltration_attempt' // Suspicious data movement
  | 'policy_violation'         // Breaking policies
  | 'recursive_calls'          // Self-referential loops
  | 'toxic_output';            // Generating harmful content
```

#### Policy
```typescript
interface Policy {
  // Identity
  id: string;
  name: string;
  description: string;
  version: string;
  
  // Metadata
  type: PolicyType;
  category: PolicyCategory;
  priority: number;           // 1-100, higher = evaluated first
  
  // Status
  status: PolicyStatus;
  enabled: boolean;
  createdAt: DateTime;
  updatedAt: DateTime;
  createdBy: string;
  
  // Rules
  rules: PolicyRule[];
  
  // Scope
  appliesTo: PolicyScope;     // What this policy affects
  
  // Actions
  defaultAction: PolicyAction;
  actions: PolicyAction[];    // Available actions
  
  // Stats
  stats: PolicyStats;
}

type PolicyType = 
  | 'network'        // Network access rules
  | 'behavior'       // Agent behavior constraints
  | 'resource'       // Resource usage limits
  | 'security'       // Security-specific rules
  | 'compliance';    // Regulatory compliance

type PolicyCategory =
  | 'egress'         // Outbound traffic
  | 'ingress'        // Inbound traffic
  | 'file_access'    // File system access
  | 'tool_usage'     // External tool usage
  | 'data_handling'  // Data processing rules
  | 'authentication' // Auth requirements
  | 'encryption';    // Encryption requirements

type PolicyStatus =
  | 'active'         // Currently enforced
  | 'draft'          // Not yet active
  | 'deprecated'     // Scheduled for removal
  | 'violated';      // Currently being violated

interface PolicyRule {
  id: string;
  name: string;
  condition: PolicyCondition;   // When this rule applies
  action: PolicyAction;          // What to do
  priority: number;            // Within policy
  enabled: boolean;
}

interface PolicyCondition {
  type: 'match' | 'regex' | 'range' | 'list' | 'composite';
  field: string;               // Field to evaluate
  operator: ConditionOperator;
  value: unknown;              // Value to compare
  caseSensitive?: boolean;
}

type ConditionOperator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'starts_with'
  | 'ends_with'
  | 'regex_match'
  | 'in_list'
  | 'not_in_list'
  | 'greater_than'
  | 'less_than'
  | 'between'
  | 'exists'
  | 'not_exists';

interface PolicyAction {
  type: PolicyActionType;
  parameters?: Record<string, unknown>;
  message?: string;            // User-facing message
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

type PolicyActionType =
  | 'allow'              // Permit the action
  | 'deny'               // Block the action
  | 'log'                // Log and allow
  | 'alert'              // Alert and allow
  | 'quarantine'         // Isolate agent
  | 'rate_limit'         // Apply rate limiting
  | 'require_approval'   // Send to HITL queue
  | 'mask_data'          // Apply data masking
  | 'encrypt'            // Require encryption
  | 'audit';             // Enhanced logging

interface PolicyScope {
  sandboxes?: string[];         // Specific sandbox IDs (undefined = all)
  agents?: string[];           // Specific agent types
  users?: string[];            // Specific users
  exclude?: {
    sandboxes?: string[];
    agents?: string[];
    users?: string[];
  };
}

interface PolicyStats {
  timesApplied: number;
  timesAllowed: number;
  timesDenied: number;
  timesAlerted: number;
  lastAppliedAt?: DateTime;
}
```

#### ComplianceFramework
```typescript
interface ComplianceFramework {
  id: string;
  name: string;                 // e.g., "NIST AI RMF"
  version: string;              // e.g., "1.0"
  description: string;
  
  categories: ComplianceCategory[];
  overallScore: number;         // 0-100
  status: ComplianceStatus;
  
  lastAssessed: DateTime;
  nextAssessment: DateTime;
  assessedBy: string;
}

interface ComplianceCategory {
  id: string;
  name: string;                 // e.g., "Govern", "Map", "Measure", "Manage"
  description: string;
  
  controls: ComplianceControl[];
  score: number;                // Category score 0-100
  weight: number;               // Impact on overall score
}

interface ComplianceControl {
  id: string;                   // e.g., "GOV-1.1"
  name: string;
  description: string;
  
  status: ControlStatus;
  implementation: ImplementationStatus;
  
  // Evidence
  evidence: Evidence[];
  evidenceRequired: boolean;
  
  // Automation
  automated: boolean;           // Can be auto-assessed?
  automatedCheck?: string;     // How to auto-check
  
  // Metadata
  priority: 'critical' | 'high' | 'medium' | 'low';
  applicable: boolean;          // Is this control applicable to us?
  
  // Relationships
  relatedControls: string[];   // IDs of related controls
  policies: string[];          // IDs of enforcing policies
}

type ComplianceStatus = 'compliant' | 'non_compliant' | 'partial' | 'not_applicable';
type ImplementationStatus = 'implemented' | 'partially_implemented' | 'planned' | 'not_implemented';
type ControlStatus = 'pass' | 'fail' | 'warning' | 'not_assessed';

interface Evidence {
  id: string;
  type: 'document' | 'screenshot' | 'log' | 'policy' | 'configuration' | 'audit';
  title: string;
  description: string;
  fileRef?: string;             // Path to file
  url?: string;                 // External URL
  collectedAt: DateTime;
  collectedBy: string;
  expiresAt?: DateTime;         // Evidence expiration
  valid: boolean;               // Is evidence still valid?
}
```

#### LogEntry
```typescript
interface LogEntry {
  id: string;
  timestamp: DateTime;
  
  // Source
  source: LogSource;
  sandboxId?: string;
  agentId?: string;
  
  // Content
  level: LogLevel;
  message: string;
  details?: Record<string, unknown>;
  
  // Context
  correlationId?: string;       // Groups related logs
  traceId?: string;            // Distributed tracing
  
  // Metadata
  tags: string[];
  category: LogCategory;
}

type LogSource = 
  | 'sandbox'
  | 'agent'
  | 'gateway'
  | 'policy'
  | 'network'
  | 'system'
  | 'audit'
  | 'security';

type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';

type LogCategory =
  | 'startup'
  | 'shutdown'
  | 'request'
  | 'response'
  | 'error'
  | 'security'
  | 'policy'
  | 'resource'
  | 'user_action';
```

#### HITLCase
```typescript
interface HITLCase {
  id: string;
  
  // Status
  status: HITLStatus;
  priority: HITLPriority;
  
  // Source
  sandboxId: string;
  agentId: string;
  triggeredBy: string;          // What triggered the HITL
  
  // Content
  title: string;
  description: string;
  riskScore: number;
  
  // Context
  context: HITLContext;
  similarCases: number;         // Count of similar past cases
  historicalDecision?: 'approved' | 'denied' | 'mixed';
  
  // SLA
  createdAt: DateTime;
  slaDuration: number;          // SLA in minutes
  slaDeadline: DateTime;
  
  // Decision
  decision?: HITLDecision;
  
  // Audit
  audit: HITLAudit;
}

type HITLStatus = 
  | 'pending'        // Waiting for human
  | 'under_review'   // Someone is looking at it
  | 'awaiting_info'  // More info requested
  | 'approved'       // Approved
  | 'denied'         // Denied
  | 'overridden'     // Approved with modifications
  | 'escalated'      // Escalated to higher authority
  | 'expired';       // SLA expired

type HITLPriority = 'low' | 'medium' | 'high' | 'critical';

interface HITLContext {
  agentGoal: string;            // What the agent was trying to do
  currentTask: string;          // Current task description
  proposedAction: string;       // Action requiring approval
  supportingData: unknown;       // Additional context
  conversationHistory?: string[]; // Recent conversation
  fileContext?: string[];       // Relevant files
}

interface HITLDecision {
  type: 'approve' | 'deny' | 'override';
  decisionBy: string;
  decisionAt: DateTime;
  reason: string;
  constraints?: string[];       // If override, what constraints
  expiration?: DateTime;        // Decision expiration if temporary
}

interface HITLAudit {
  views: HITLView[];            // Who viewed the case
  comments: HITLComment[];      // Comments on the case
}

interface HITLView {
  userId: string;
  viewedAt: DateTime;
  duration: number;              // Seconds spent viewing
}

interface HITLComment {
  id: string;
  userId: string;
  timestamp: DateTime;
  message: string;
}
```

---

## 2. API Contracts

### 2.1 Sandbox API

#### List Sandboxes
```
GET /api/sandboxes
```

**Query Parameters**:
- `status` (optional): Filter by status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset

**Response**:
```json
{
  "sandboxes": [
    {
      "id": "sandbox-7a3b9c",
      "name": "Agent-7",
      "status": "running",
      "statusMessage": null,
      "resources": {
        "gpu": [
          {
            "index": 0,
            "utilization": 65,
            "memoryUsed": 7200,
            "temperature": 72
          }
        ]
      },
      "reputation": {
        "currentScore": 85,
        "trend": "stable"
      },
      "createdAt": "2026-03-24T10:30:00Z",
      "lastActivityAt": "2026-03-26T14:22:00Z"
    }
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

#### Get Sandbox Details
```
GET /api/sandboxes/:id
```

**Response**: Full `Sandbox` object with all details

#### Create Sandbox
```
POST /api/sandboxes
```

**Request Body**:
```json
{
  "name": "Agent-8",
  "description": "Customer support agent",
  "agent": {
    "type": "openai",
    "version": "1.0",
    "model": "gpt-4",
    "capabilities": ["web_search", "file_access"]
  },
  "inference": {
    "provider": "nvidia-nim",
    "temperature": 0.7,
    "maxTokens": 2048
  },
  "workspace": {
    "maxSize": 1073741824
  }
}
```

**Response**: Created `Sandbox` object

#### Control Sandbox
```
POST /api/sandboxes/:id/control
```

**Request Body**:
```json
{
  "action": "start" | "stop" | "restart" | "pause" | "quarantine"
}
```

#### Get Sandbox Logs
```
GET /api/sandboxes/:id/logs
```

**Query Parameters**:
- `level` (optional): Filter by log level
- `since` (optional): ISO timestamp start
- `until` (optional): ISO timestamp end
- `limit` (optional): Number of lines (default: 100)
- `follow` (optional): Stream logs (SSE)

**Response**:
```json
{
  "entries": [
    {
      "id": "log-abc123",
      "timestamp": "2026-03-26T14:22:15Z",
      "level": "info",
      "message": "Processing request #1294",
      "source": "agent",
      "tags": ["request", "processing"]
    }
  ],
  "hasMore": true
}
```

### 2.2 Network Request API

#### List Requests
```
GET /api/network-requests
```

**Query Parameters**:
- `status` (optional): Filter by status
- `sandboxId` (optional): Filter by sandbox
- `riskMin` (optional): Minimum risk score
- `since` (optional): Time filter
- `limit`, `offset`: Pagination

**Response**:
```json
{
  "requests": [
    {
      "id": "req-xyz789",
      "timestamp": "2026-03-26T14:22:15Z",
      "sandboxId": "sandbox-7a3b9c",
      "agentId": "agent-7",
      "method": "GET",
      "url": "https://api.github.com/repos/NVIDIA/NemoClaw",
      "hostname": "api.github.com",
      "riskScore": 35,
      "riskFactors": [
        {
          "type": "known_domain",
          "severity": "low",
          "description": "Domain is in allowlist",
          "score": -10
        }
      ],
      "status": "pending",
      "category": "api",
      "context": {
        "agentTask": "Researching NemoClaw repository",
        "previousRequests": ["req-xyz788", "req-xyz787"]
      }
    }
  ],
  "stats": {
    "pending": 12,
    "approvedToday": 45,
    "deniedToday": 3
  }
}
```

#### Approve/Deny Request
```
POST /api/network-requests/:id/decision
```

**Request Body**:
```json
{
  "decision": "approve" | "deny",
  "reason": "Domain is trusted",
  "applyToSimilar": false  // Whether to remember this decision
}
```

#### Bulk Decision
```
POST /api/network-requests/bulk-decision
```

**Request Body**:
```json
{
  "requestIds": ["req-xyz789", "req-xyz790"],
  "decision": "approve",
  "reason": "Batch approval for trusted domains"
}
```

### 2.3 Agent Reputation API

#### Get Reputation Scores
```
GET /api/reputation
```

**Query Parameters**:
- `sandboxId` (optional): Filter by sandbox
- `minScore` (optional): Minimum score filter
- `trend` (optional): Filter by trend

**Response**:
```json
{
  "reputations": [
    {
      "agentId": "agent-7",
      "sandboxId": "sandbox-7a3b9c",
      "currentScore": 85,
      "previousScore": 82,
      "trend": "improving",
      "calculatedAt": "2026-03-26T14:00:00Z",
      "positiveSignals": [
        {
          "type": "task_completion",
          "category": "behavior",
          "weight": 20,
          "description": "Successfully completed 12 tasks",
          "occurrences": 12
        }
      ],
      "negativeSignals": [],
      "quarantineThreshold": 40
    }
  ],
  "average": 72,
  "distribution": {
    "excellent": 5,   // 80-100
    "good": 4,        // 60-79
    "fair": 2,        // 40-59
    "poor": 1         // 0-39
  }
}
```

#### Get Reputation History
```
GET /api/reputation/:agentId/history
```

**Query Parameters**:
- `period` (optional): '1h', '24h', '7d', '30d' (default: '7d')

**Response**:
```json
{
  "agentId": "agent-7",
  "history": [
    {
      "timestamp": "2026-03-26T14:00:00Z",
      "score": 85,
      "reason": "Task completion bonus"
    },
    {
      "timestamp": "2026-03-26T13:00:00Z",
      "score": 82,
      "reason": null
    }
  ],
  "trend": "improving",
  "volatility": 0.05  // Score variance
}
```

### 2.4 Policy API

#### List Policies
```
GET /api/policies
```

**Query Parameters**:
- `type` (optional): Filter by policy type
- `status` (optional): Filter by status
- `enabled` (optional): Filter by enabled state

#### Get Policy
```
GET /api/policies/:id
```

#### Create/Update Policy
```
POST /api/policies
PUT /api/policies/:id
```

**Request Body** (Create/Update):
```json
{
  "name": "Block Internal Database Access",
  "description": "Prevents agents from accessing internal databases directly",
  "type": "network",
  "category": "egress",
  "priority": 90,
  "enabled": true,
  "rules": [
    {
      "name": "Block DB Port",
      "condition": {
        "type": "match",
        "field": "port",
        "operator": "equals",
        "value": 5432
      },
      "action": {
        "type": "deny",
        "message": "Direct database access is not permitted",
        "logLevel": "warn"
      }
    }
  ],
  "appliesTo": {
    "sandboxes": ["*"],  // All sandboxes
    "exclude": {
      "sandboxes": ["sandbox-trusted-001"]  // Except trusted
    }
  },
  "defaultAction": {
    "type": "allow",
    "logLevel": "debug"
  }
}
```

### 2.5 Compliance API

#### Get Frameworks
```
GET /api/compliance/frameworks
```

**Response**:
```json
{
  "frameworks": [
    {
      "id": "nist-ai-rmf",
      "name": "NIST AI Risk Management Framework",
      "version": "1.0",
      "overallScore": 92,
      "status": "compliant",
      "lastAssessed": "2026-03-26T10:00:00Z",
      "categories": [
        {
          "id": "govern",
          "name": "Govern",
          "score": 100,
          "controls": [
            {
              "id": "GOV-1.1",
              "name": "AI Risk Management Policies",
              "status": "pass",
              "implementation": "implemented",
              "evidence": [
                {
                  "id": "ev-001",
                  "type": "policy",
                  "title": "AI Risk Management Policy v2.0",
                  "valid": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

#### Upload Evidence
```
POST /api/compliance/evidence
```

**Request** (multipart/form-data):
- `controlId`: Which control this evidence supports
- `type`: Evidence type
- `file`: File upload or
- `url`: External reference

### 2.6 HITL API

#### List Cases
```
GET /api/hitl/cases
```

**Query Parameters**:
- `status` (optional): Filter by case status
- `priority` (optional): Filter by priority
- `assignedTo` (optional): Filter by assignee

#### Get Case Details
```
GET /api/hitl/cases/:id
```

#### Make Decision
```
POST /api/hitl/cases/:id/decision
```

**Request Body**:
```json
{
  "decision": "approve" | "deny" | "override",
  "reason": "Approved with time constraint",
  "constraints": ["expires_in=1h", "require_audit_log=true"],
  "expiration": "2026-03-26T15:22:00Z"
}
```

#### Add Comment
```
POST /api/hitl/cases/:id/comments
```

**Request Body**:
```json
{
  "message": "Requesting additional context from the agent"
}
```

### 2.7 Telemetry API

#### Get GPU Metrics
```
GET /api/telemetry/gpu
```

**Query Parameters**:
- `sandboxId` (optional): Filter by sandbox
- `since` (optional): Historical data start
- `interval` (optional): Aggregation interval ('1m', '5m', '1h')

**Response**:
```json
{
  "gpus": [
    {
      "index": 0,
      "name": "NVIDIA H100",
      "current": {
        "utilization": 65,
        "memoryUsed": 7200,
        "memoryTotal": 81920,
        "temperature": 72,
        "powerDraw": 320
      },
      "history": [
        {
          "timestamp": "2026-03-26T14:20:00Z",
          "utilization": 62,
          "memoryUsed": 7100
        }
      ],
      "processes": [
        {
          "pid": 12345,
          "name": "agent-7",
          "memoryUsed": 6800,
          "sandboxId": "sandbox-7a3b9c"
        }
      ]
    }
  ],
  "aggregate": {
    "totalUtilization": 65,
    "totalMemoryUsed": 7200,
    "activeSandboxes": 3
  }
}
```

#### Get System Metrics
```
GET /api/telemetry/system
```

### 2.8 Real-time Events API

#### Event Stream (Server-Sent Events)
```
GET /api/events/stream
```

**Event Types**:
```
event: network_request
data: {"id": "req-xyz790", "status": "pending", "riskScore": 45}

event: sandbox_status
data: {"sandboxId": "sandbox-7a3b9c", "status": "running", "timestamp": "..."}

event: reputation_change
data: {"agentId": "agent-7", "oldScore": 82, "newScore": 85}

event: hitl_new_case
data: {"caseId": "hitl-123", "priority": "high", "agentId": "agent-3"}

event: gpu_metrics
data: {"gpuIndex": 0, "utilization": 68, "temperature": 73}
```

---

## 3. Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "SANDBOX_NOT_FOUND",
    "message": "Sandbox with ID 'sandbox-abc' not found",
    "details": {
      "sandboxId": "sandbox-abc",
      "suggestion": "Check the sandbox ID or list all sandboxes with GET /api/sandboxes"
    },
    "timestamp": "2026-03-26T14:22:15Z",
    "requestId": "req-uuid-123"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SANDBOX_NOT_FOUND` | 404 | Sandbox does not exist |
| `SANDBOX_ALREADY_RUNNING` | 409 | Sandbox is already running |
| `POLICY_VIOLATION` | 403 | Action blocked by policy |
| `INVALID_CONFIGURATION` | 400 | Invalid sandbox configuration |
| `RESOURCE_EXHAUSTED` | 429 | Rate limit or resource limit hit |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `SERVICE_UNAVAILABLE` | 503 | OpenShell not available |

---

## 4. Authentication & Security

### Local Authentication
- No separate auth layer (runs on localhost)
- OS user permissions apply
- All actions logged with OS username

### API Security
- CORS restricted to localhost origins
- Rate limiting on mutation endpoints
- Request size limits (10MB)
- Input validation on all endpoints

### Audit Logging
All API calls logged with:
- Timestamp
- OS user
- Endpoint
- Request/Response (sanitized)
- IP (always 127.0.0.1 for local)

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
