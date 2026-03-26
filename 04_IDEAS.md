# NemoClaw Gateway Dashboard - Project Ideas & Documentation

## Project Overview

**NemoClaw Gateway Dashboard** is a production-grade, centralized control plane and **Safe-by-Default** Zero Trust gateway for managing **NVIDIA NemoClaw** and **OpenShell** environments. This dashboard runs **locally** where the NemoClaw setup is installed, providing real-time monitoring and management of AI agents and sandboxes.

---

## Core Concept

The dashboard serves as a **single pane of glass** for:
- Managing NemoClaw/OpenShell installations running locally
- Monitoring sandbox activity and agent behavior
- Enforcing network policies and security guardrails
- Providing forensic traceability of AI agent decisions
- Enabling multi-persona views (Engineer, SecOps, CISO)

---

## Reference Documentation URLs

### Official NVIDIA Documentation

1. **NemoClaw Build Page**
   - URL: https://build.nvidia.com/nemoclaw
   - Description: Official NVIDIA build page for NemoClaw with deployment options

2. **NemoClaw Documentation**
   - URL: https://docs.nvidia.com/nemoclaw/latest/index.html
   - Description: Complete developer guide for NemoClaw including:
     - Quickstart guide
     - Network policy management
     - Sandbox monitoring
     - Inference provider switching
     - Architecture reference

3. **OpenShell Documentation**
   - URL: https://docs.nvidia.com/openshell/latest/index.html
   - Description: Developer guide for OpenShell runtime covering:
     - Gateway and sandbox management
     - Inference routing configuration
     - Policy management
     - Community sandboxes

4. **OpenShell on DGX Station**
   - URL: https://build.nvidia.com/station/openshell
   - Description: Deployment guide for DGX Station hardware

5. **NemoClaw GitHub Repository**
   - URL: https://github.com/NVIDIA/NemoClaw
   - Description: Open source reference stack for running OpenClaw assistants

---

## NemoClaw Solution Understanding

### What is NemoClaw?

NemoClaw is an **open source reference stack** that simplifies running OpenClaw always-on assistants with a single command. It installs the NVIDIA OpenShell runtime to add:
- Policy-based privacy controls
- Security guardrails
- Access control (shapes access, not capabilities)
- Private inference capabilities

### Key Capabilities

1. **Network Policy Management**
   - Approve or deny network requests from agents
   - Customize network policies per sandbox
   - Real-time request monitoring

2. **Sandbox Management**
   - Create and manage isolated agent environments
   - Workspace file management
   - Backup and restore capabilities

3. **Inference Routing**
   - Switch between inference providers
   - Local inference support (Ollama, LM Studio)
   - NVIDIA NIM integration

4. **Agent Monitoring**
   - Monitor sandbox activity
   - Track agent behavior and network requests
   - GPU utilization tracking

---

## Deployment Modes: Personal vs Enterprise

The NemoClaw Gateway Dashboard supports **two operational models** that share the same core architecture but differ in scale, governance, and access controls.

### Personal Mode (Single-User)

**Target Use Case**: Individual developers, researchers, or small teams managing their own NemoClaw environment.

**Characteristics**:
- **Single administrator** with full control
- **Local deployment** on user's machine
- **Simplified interface** with minimal overhead
- **No authentication layer** (relies on OS-level security)
- **Direct control** over all sandboxes and policies
- **Quick setup** - install and run immediately

**Features**:
- Centralized sandbox management
- Real-time monitoring and logs
- GPU telemetry dashboard
- Network policy configuration
- Workspace file browser
- One-click sandbox operations

**Deployment**: `streamlit run app.py` → Dashboard available at `localhost:8501`

---

### Enterprise Mode (Multi-User)

**Target Use Case**: Organizations with multiple teams, governance requirements, and compliance needs.

**Characteristics**:
- **Multi-user** with role-based access (RBAC/ABAC)
- **Centralized deployment** (server or cloud)
- **Granular permissions** per user/team
- **Authentication required** (SSO/LDAP/OAuth)
- **Workflow approvals** for critical operations
- **Comprehensive audit logging**
- **Policy enforcement** at organizational level

**Additional Enterprise Features**:
- User authentication and session management
- Role-based access control (Engineer, SecOps, Admin, Viewer)
- Activity tracking and audit trails
- Approval workflows for sandbox creation/policy changes
- Organizational policy templates
- Compliance reporting and dashboards
- Multi-tenant support (teams/projects)
- Integration with SIEM/SOC tools
- Automated backup and disaster recovery

**Deployment Options**:
- On-premises server deployment
- Docker/Kubernetes orchestration
- Cloud deployment (AWS/Azure/GCP)
- High-availability configuration

---

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                     PERSONAL MODE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │   User      │                                                │
│  │ (Developer) │                                                │
│  └──────┬──────┘                                                │
│         │                                                        │
│         │ HTTP                                                   │
│         ▼                                                        │
│  ┌──────────────────┐                                           │
│  │  Streamlit App   │  ← Runs on localhost                       │
│  │  (Single User)   │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           │ Local CLI                                            │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │  NemoClaw CLI    │                                           │
│  │  (Local)         │                                           │
│  └──────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE MODE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Engineer │  │  SecOps  │  │   CISO   │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │            │            │                               │
│       └────────────┼────────────┘                               │
│                    │                                             │
│                    │ HTTPS + Auth                                │
│                    ▼                                             │
│         ┌────────────────────┐                                  │
│         │   Load Balancer    │                                  │
│         └────────┬───────────┘                                  │
│                  │                                               │
│         ┌────────┴────────┐                                    │
│         │  Streamlit App  │  ← Multiple instances              │
│         │   (Multi-User)  │     with auth middleware            │
│         └────────┬────────┘                                    │
│                  │                                              │
│         ┌────────┴────────┐                                     │
│         │   PostgreSQL    │  ← User data, audit logs             │
│         │    (Auth DB)    │                                    │
│         └────────┬────────┘                                    │
│                  │                                              │
│                  │ API calls                                    │
│                  ▼                                              │
│         ┌──────────────────┐                                   │
│         │  NemoClaw Gateway  │  ← Centralized control plane      │
│         │   (Enterprise)   │                                    │
│         └──────────────────┘                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Mode Transition

The architecture supports **seamless transition** from Personal to Enterprise:

| Aspect | Personal | Enterprise |
|--------|----------|------------|
| **Authentication** | None (OS-level) | SSO/LDAP/OAuth |
| **User Management** | Single user | RBAC/ABAC |
| **Audit Logging** | Local files | Centralized DB |
| **Policy Enforcement** | Local policies | Organization-wide |
| **Deployment** | Localhost | Server/Cloud |
| **Scaling** | Single instance | Multi-instance |
| **Backup** | Manual | Automated |
| **Support** | Community | Enterprise support |

**Migration Path**:
1. Start with Personal mode for development/testing
2. Export configuration and policies
3. Deploy Enterprise mode with authentication
4. Import settings and enable multi-user features
5. Configure RBAC roles and permissions

---

## Multi-Instance Architecture

The NemoClaw Gateway Dashboard can administer **multiple NemoClaw installations** from a single dashboard instance, supporting both personal and enterprise scenarios.

### Use Cases

**Personal Use Case**:
- Developer with NemoClaw on local workstation + remote GPU server
- Researcher with separate environments for different projects
- Testing different OpenShell versions side-by-side

**Enterprise Use Case**:
- Central IT managing NemoClaw across multiple departments
- Multi-region deployment (US, EU, APAC)
- Separate environments for dev/staging/production

---

### Personal Mode: Multi-Instance

```
┌─────────────────────────────────────────────────────────┐
│              Personal Dashboard (Local)                 │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Instance        │  │ Instance                  │  │
│  │ Selector        │  │ Details Panel             │  │
│  │ • localhost     │  │ • Status: 🟢 Online        │  │
│  │ • gpu-server    │  │ • Sandboxes: 3 running     │  │
│  │ • lab-workstation│  │ • GPU: 2x A100            │  │
│  └─────────────────┘  └─────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │          Sandboxes from Selected Instance          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐              │ │
│  │  │Agent-1  │ │Agent-2  │ │Agent-3  │              │ │
│  │  │🟢 Running│ │⚫ Stopped│ │🟢 Running│              │ │
│  │  └─────────┘ └─────────┘ └─────────┘              │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           │ SSH/HTTP           │ SSH                │ Local
           ▼                    ▼                    ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  NemoClaw    │      │  NemoClaw    │      │  NemoClaw    │
│  (GPU Server)│      │  (Lab PC)    │      │  (Localhost) │
└──────────────┘      └──────────────┘      └──────────────┘
```

**Configuration** (Personal):
```yaml
# ~/.nemoclaw/instances.yaml
instances:
  - id: local
    name: "Local Workstation"
    type: local
    connection:
      path: /usr/local/bin/openshell
    default: true
    
  - id: gpu-server
    name: "GPU Server"
    type: remote
    connection:
      host: gpu-server.company.com
      port: 22
      user: nemoclaw
      key_path: ~/.ssh/gpu-server.pem
      openshell_path: /opt/openshell/bin/openshell
    
  - id: lab-pc
    name: "Lab Workstation"
    type: remote
    connection:
      host: 192.168.1.50
      port: 22
      user: researcher
      openshell_path: ~/openshell/bin/openshell
```

---

### Enterprise Mode: Multi-Instance

```
┌─────────────────────────────────────────────────────────┐
│           Enterprise Dashboard (Centralized)            │
│                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ Instance     │  │ Instance Overview             │  │
│  │ Registry     │  │ • Total: 12 instances         │  │
│  │              │  │ • Online: 10 🟢               │  │
│  │ 🌐 us-prod   │  │ • Warning: 1 🟡              │  │
│  │ 🌐 eu-prod   │  │ • Offline: 1 🔴               │  │
│  │ 🌐 apac-dev  │  │                               │  │
│  │ 🏢 dept-ai   │  │ • Total Sandboxes: 45         │  │
│  │ 🏢 dept-ml   │  │ • Active GPUs: 23/30         │  │
│  │ ...          │  │ • Pending Requests: 12        │  │
│  └──────────────┘  └──────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │            Cross-Instance Operations               │ │
│  │  • Deploy policy to all instances                  │ │
│  │  • Aggregate compliance report                     │ │
│  │  • Global search across all sandboxes            │ │
│  │  • Fleet-wide GPU utilization                    │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  NemoClaw    │ │  NemoClaw    │ │  NemoClaw    │ │  NemoClaw    │
│  (US Prod)   │ │  (EU Prod)   │ │  (APAC Dev)  │ │  (Dept AI)   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Configuration** (Enterprise):
```yaml
# /etc/nemoclaw/instances.yaml
instances:
  - id: us-production
    name: "US Production"
    environment: production
    region: us-east-1
    team: platform-engineering
    connection:
      type: api
      endpoint: https://us-prod.nemoclaw.internal/api
      auth: vault
      vault_path: secret/nemoclaw/us-prod
    monitoring:
      health_check_interval: 30
      alerts: [slack-platform]
    
  - id: eu-production
    name: "EU Production"
    environment: production
    region: eu-west-1
    team: platform-engineering
    connection:
      type: api
      endpoint: https://eu-prod.nemoclaw.internal/api
      auth: vault
      vault_path: secret/nemoclaw/eu-prod
    compliance:
      gdpr: true
      data_residency: eu
    
  - id: apac-development
    name: "APAC Development"
    environment: development
    region: ap-southeast-1
    team: ai-research
    connection:
      type: api
      endpoint: https://apac-dev.nemoclaw.internal/api
      auth: vault
```

---

### Instance Connection Types

| Type | Use Case | Connection Method | Security |
|------|----------|-------------------|----------|
| **Local** | Single machine | Direct subprocess | OS permissions |
| **SSH** | Remote servers | Paramiko/SSH tunnel | SSH keys |
| **API** | Enterprise | HTTPS REST API | OAuth2/mTLS |
| **Agent** | Air-gapped | Local agent → API | Mutual TLS |

---

### Instance Manager Service

```python
# services/instance_manager.py
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
import subprocess
import paramiko

class InstanceType(Enum):
    LOCAL = "local"
    SSH = "ssh"
    API = "api"
    AGENT = "agent"

class InstanceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class NemoClawInstance:
    id: str
    name: str
    type: InstanceType
    environment: str  # dev, staging, production
    connection_config: Dict
    status: InstanceStatus = InstanceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    metadata: Dict = None

class InstanceManager:
    """Manage multiple NemoClaw instances"""
    
    def __init__(self, config_path: str = "~/.nemoclaw/instances.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.instances: Dict[str, NemoClawInstance] = {}
        self.connectors: Dict[InstanceType, callable] = {
            InstanceType.LOCAL: LocalConnector(),
            InstanceType.SSH: SSHConnector(),
            InstanceType.API: APIConnector(),
        }
        self._load_instances()
    
    def _load_instances(self):
        """Load instances from configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            for instance_data in config.get('instances', []):
                instance = NemoClawInstance(
                    id=instance_data['id'],
                    name=instance_data['name'],
                    type=InstanceType(instance_data['type']),
                    environment=instance_data.get('environment', 'default'),
                    connection_config=instance_data['connection'],
                    metadata=instance_data.get('metadata', {})
                )
                self.instances[instance.id] = instance
    
    def get_instance(self, instance_id: str) -> Optional[NemoClawInstance]:
        """Get instance by ID"""
        return self.instances.get(instance_id)
    
    def list_instances(self, environment: Optional[str] = None) -> List[NemoClawInstance]:
        """List all instances, optionally filtered by environment"""
        instances = list(self.instances.values())
        if environment:
            instances = [i for i in instances if i.environment == environment]
        return instances
    
    def check_health(self, instance_id: str) -> InstanceStatus:
        """Check instance health"""
        instance = self.get_instance(instance_id)
        if not instance:
            return InstanceStatus.UNKNOWN
        
        connector = self.connectors.get(instance.type)
        if not connector:
            return InstanceStatus.UNKNOWN
        
        try:
            status = connector.check_health(instance.connection_config)
            instance.status = status
            instance.last_seen = datetime.now()
            return status
        except Exception as e:
            instance.status = InstanceStatus.OFFLINE
            return InstanceStatus.OFFLINE
    
    def execute_on_instance(self, instance_id: str, command: str, *args) -> Dict:
        """Execute command on specific instance"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        connector = self.connectors.get(instance.type)
        if not connector:
            raise ValueError(f"No connector for type {instance.type}")
        
        return connector.execute(instance.connection_config, command, *args)
    
    def aggregate_from_all(self, command: str, *args) -> Dict[str, Dict]:
        """Execute command on all instances and aggregate results"""
        results = {}
        for instance_id, instance in self.instances.items():
            try:
                results[instance_id] = self.execute_on_instance(instance_id, command, *args)
            except Exception as e:
                results[instance_id] = {'error': str(e)}
        return results

# Connector implementations
class LocalConnector:
    """Direct local connection"""
    
    def check_health(self, config: Dict) -> InstanceStatus:
        try:
            result = subprocess.run(
                [config['path'], '--version'],
                capture_output=True,
                timeout=5
            )
            return InstanceStatus.ONLINE if result.returncode == 0 else InstanceStatus.DEGRADED
        except:
            return InstanceStatus.OFFLINE
    
    def execute(self, config: Dict, command: str, *args) -> Dict:
        cmd = [config['path'], command] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

class SSHConnector:
    """SSH connection to remote instance"""
    
    def check_health(self, config: Dict) -> InstanceStatus:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=config['host'],
                port=config.get('port', 22),
                username=config['user'],
                key_filename=config.get('key_path')
            )
            
            # Check openshell availability
            stdin, stdout, stderr = client.exec_command(
                f"{config['openshell_path']} --version"
            )
            exit_code = stdout.channel.recv_exit_status()
            client.close()
            
            return InstanceStatus.ONLINE if exit_code == 0 else InstanceStatus.DEGRADED
        except:
            return InstanceStatus.OFFLINE
    
    def execute(self, config: Dict, command: str, *args) -> Dict:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=config['host'],
            port=config.get('port', 22),
            username=config['user'],
            key_filename=config.get('key_path')
        )
        
        cmd = f"{config['openshell_path']} {command} {' '.join(args)}"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        result = {
            'stdout': stdout.read().decode(),
            'stderr': stderr.read().decode(),
            'returncode': stdout.channel.recv_exit_status()
        }
        client.close()
        return result

class APIConnector:
    """API connection to enterprise instance"""
    
    def check_health(self, config: Dict) -> InstanceStatus:
        import requests
        try:
            response = requests.get(
                f"{config['endpoint']}/health",
                timeout=10,
                verify=config.get('verify_ssl', True)
            )
            if response.status_code == 200:
                return InstanceStatus.ONLINE
            return InstanceStatus.DEGRADED
        except:
            return InstanceStatus.OFFLINE
    
    def execute(self, config: Dict, command: str, *args) -> Dict:
        import requests
        headers = self._get_auth_headers(config)
        
        response = requests.post(
            f"{config['endpoint']}/v1/execute",
            json={'command': command, 'args': args},
            headers=headers,
            timeout=30
        )
        return response.json()
    
    def _get_auth_headers(self, config: Dict) -> Dict:
        # OAuth2 or API key authentication
        auth_type = config.get('auth', 'none')
        if auth_type == 'oauth2':
            # Get token from cache or refresh
            return {'Authorization': f'Bearer {self._get_token(config)}'}
        elif auth_type == 'api_key':
            return {'X-API-Key': config['api_key']}
        return {}
```

---

### UI Integration

**Instance Selector** (Sidebar):
```python
# components/instance_selector.py
import streamlit as st

def render_instance_selector(instance_manager: InstanceManager):
    """Render instance selector in sidebar"""
    instances = instance_manager.list_instances()
    
    if len(instances) == 1:
        # Single instance - just show name
        st.sidebar.write(f"📍 {instances[0].name}")
        return instances[0].id
    
    # Multiple instances - show dropdown
    instance_options = {f"{i.name} ({i.status.value})": i.id for i in instances}
    
    selected_label = st.sidebar.selectbox(
        "📍 Select Instance",
        options=list(instance_options.keys()),
        index=0
    )
    
    selected_id = instance_options[selected_label]
    
    # Show instance details
    instance = instance_manager.get_instance(selected_id)
    with st.sidebar.expander("Instance Details"):
        st.write(f"**Environment:** {instance.environment}")
        st.write(f"**Type:** {instance.type.value}")
        st.write(f"**Last Seen:** {instance.last_seen or 'Never'}")
    
    return selected_id

# Usage in pages
selected_instance = render_instance_selector(instance_manager)
service = OpenShellService(instance_id=selected_instance)
```

**Multi-Instance Dashboard**:
```python
# pages/05_Multi_Instance_Overview.py
import streamlit as st

def render_multi_instance_overview(instance_manager: InstanceManager):
    """Render overview of all instances"""
    st.title("🌐 Multi-Instance Overview")
    
    instances = instance_manager.list_instances()
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Instances", len(instances))
    with col2:
        online = sum(1 for i in instances if i.status == InstanceStatus.ONLINE)
        st.metric("Online", online)
    with col3:
        offline = sum(1 for i in instances if i.status == InstanceStatus.OFFLINE)
        st.metric("Offline", offline, delta_color="inverse")
    with col4:
        # Total sandboxes across all instances
        total_sandboxes = sum(
            len(instance_manager.execute_on_instance(i.id, 'list', 'sandboxes').get('sandboxes', []))
            for i in instances if i.status == InstanceStatus.ONLINE
        )
        st.metric("Total Sandboxes", total_sandboxes)
    
    # Instance table
    st.subheader("Instance Status")
    instance_data = []
    for instance in instances:
        instance_data.append({
            'Name': instance.name,
            'Environment': instance.environment,
            'Status': instance.status.value,
            'Type': instance.type.value,
            'Last Seen': instance.last_seen.strftime('%Y-%m-%d %H:%M') if instance.last_seen else 'Never'
        })
    
    st.dataframe(instance_data, use_container_width=True)
    
    # Global operations
    st.subheader("Global Operations")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh All Health Status"):
            for instance in instances:
                instance_manager.check_health(instance.id)
            st.rerun()
    with col2:
        if st.button("📊 Aggregate Compliance Report"):
            # Generate cross-instance compliance report
            pass
```

---

## Dashboard Architecture (Local Deployment)

### Deployment Model

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                        │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────┐
│         NemoClaw Gateway Dashboard (Python/Streamlit)          │
│                   Runs on localhost                    │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   Dashboard UI  │  │  Local API Integration      │  │
│  │  (Streamlit)    │  │  - OpenShell CLI wrapper    │  │
│  │                 │  │  - File watcher (watchdog)  │  │
│  │                 │  │  - GPU metrics (pynvml)     │  │
│  │                 │  │  - Process monitor (psutil) │  │
│  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Local system calls
                           ▼
┌─────────────────────────────────────────────────────────┐
│              NemoClaw/OpenShell Installation           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Sandboxes  │  │   Policies   │  │  Workspaces  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Local Integration Points

1. **OpenShell CLI Integration**
   - Execute openshell commands via Python subprocess
   - Parse JSON output for dashboard display
   - Real-time log streaming with subprocess pipes

2. **File System Monitoring**
   - Watch workspace directories
   - Monitor policy configuration files
   - Track sandbox state files

3. **Process Monitoring**
   - Monitor running agent processes
   - GPU utilization via nvidia-smi
   - Network activity monitoring

---

## Multi-Persona Dashboard Views

### 1. Engineer View
**Focus**: Performance, debugging, resource management

**Features**:
- Sandbox list with status indicators
- Real-time GPU telemetry (utilization, memory, temperature)
- Inference routing configuration
- Workspace file browser
- Agent logs and traces
- Performance metrics (latency, throughput)

### 2. SecOps View
**Focus**: Security monitoring, threat detection, forensics

**Features**:
- Network request approval queue
- Agent reputation scoring dashboard
- Real-time threat alerts
- AI Attack Graph visualization (Neo4j-powered)
- Forensic log browser with search
- Policy violation reports
- HITL (Human-in-the-Loop) adjudication queue

### 3. CISO View
**Focus**: Compliance, risk management, governance

**Features**:
- Compliance posture dashboard (NIST AI RMF, ISO 42001)
- Risk trend analysis
- Audit trail reports
- Cost-to-security ratio metrics
- Policy coverage overview
- Executive summary reports

---

## Core Features to Implement

### Phase 1: Foundation
- [ ] Dashboard layout with persona switching
- [ ] OpenShell CLI integration layer
- [ ] Sandbox management interface
- [ ] Real-time monitoring dashboard

### Phase 2: Security & Governance
- [ ] Network policy management UI
- [ ] Agent reputation scoring system
- [ ] HITL adjudication queue
- [ ] Forensic log viewer

### Phase 3: Advanced Features
- [ ] AI Attack Graph visualization
- [ ] Compliance reporting
- [ ] Multi-cluster federation support
- [ ] Automated threat response

---

## Technical Stack (Python-Based)

### Web Framework
- **Primary**: Streamlit - Python-based web app framework
  - Perfect for data dashboards and real-time monitoring
  - Built-in widgets for tables, charts, and forms
  - Automatic reloading during development
  - Wide component ecosystem

### Alternative Options Evaluated

#### Option A: Streamlit (Recommended)
**Pros**:
- Pure Python - no frontend code needed
- Excellent for dashboards and data apps
- Built-in real-time updates
- Simple to develop and maintain
- Great charting support (Altair, Plotly)

**Cons**:
- Less customizable UI
- Page-based navigation (not SPA)
- Limited styling options

**Best For**: Rapid development, data-heavy dashboards

#### Option B: FastAPI + Simple Frontend
**Pros**:
- Full control over API and UI
- Can use lightweight frontend (HTMX, Alpine.js)
- High performance async support
- Better for complex interactions

**Cons**:
- Requires frontend knowledge
- More code to maintain
- Slower development

**Best For**: Complex APIs, custom UI requirements

#### Option C: Gradio
**Pros**:
- ML-focused, great for AI demos
- Simple interface building
- Built-in sharing capabilities

**Cons**:
- Less dashboard-focused
- Limited layout control

**Best For**: Quick demos, not production dashboards

### Selected Stack: Streamlit

**Core Components**:
- **Framework**: Streamlit 1.30+
- **Language**: Python 3.10+
- **Styling**: Streamlit theming + custom CSS
- **Charts**: Plotly, Altair, Matplotlib
- **Data**: Pandas for data manipulation
- **Real-time**: Streamlit session state + st.rerun()

### Backend Integration (Python)
- **OpenShell Integration**: Python subprocess for CLI calls
- **File Watching**: watchdog library
- **Process Monitoring**: psutil library
- **GPU Metrics**: pynvml (NVML Python bindings)
- **Real-time Updates**: Streamlit polling + caching
- **Configuration**: YAML/JSON files, Python dataclasses

### Data Storage (Local)
- **Configuration**: JSON/YAML files in ~/.nemoclaw/
- **Logs**: Local log file parsing
- **Metrics**: In-memory with optional SQLite persistence
- **Dashboard State**: LocalStorage / IndexedDB

---

## File Structure (Python)

```
nemoclaw-gateway-dashboard/
├── app.py                          # Main Streamlit entry point
├── pages/
│   ├── 01_Engineer_View.py         # Engineer persona page
│   ├── 02_SecOps_View.py           # SecOps persona page
│   ├── 03_CISO_View.py             # CISO persona page
│   └── 04_Settings.py              # Configuration page
├── components/
│   ├── __init__.py
│   ├── sandbox_cards.py            # Sandbox status components
│   ├── gpu_metrics.py              # GPU telemetry widgets
│   ├── log_viewer.py               # Log display components
│   ├── request_queue.py            # Network request UI
│   └── reputation.py               # Agent reputation display
├── services/
│   ├── __init__.py
│   ├── openshell.py                # OpenShell CLI integration
│   ├── nemoclaw.py                 # NemoClaw config parser
│   ├── gpu_monitor.py              # GPU metrics collection
│   ├── file_watcher.py             # File system monitoring
│   └── telemetry.py                # System telemetry
├── models/
│   ├── __init__.py
│   ├── sandbox.py                  # Sandbox data models
│   ├── policy.py                   # Policy data models
│   ├── request.py                  # Network request models
│   └── reputation.py               # Reputation models
├── utils/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── styling.py                  # Custom CSS/themes
│   └── helpers.py                  # Utility functions
├── config/
│   ├── default.yaml                # Default configuration
│   └── themes/
│       ├── dark.yaml               # Dark theme
│       └── light.yaml              # Light theme
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
└── README.md                       # Project documentation
```

---

## Local API Integration Design (Python)

### OpenShell Service

```python
class OpenShellService:
    """Service for interacting with OpenShell CLI"""
    
    def list_sandboxes(self) -> list[Sandbox]:
        """List all sandboxes"""
        pass
    
    def get_sandbox_status(self, sandbox_id: str) -> SandboxStatus:
        """Get status of specific sandbox"""
        pass
    
    def create_sandbox(self, config: SandboxConfig) -> Sandbox:
        """Create new sandbox"""
        pass
    
    def stop_sandbox(self, sandbox_id: str) -> None:
        """Stop a running sandbox"""
        pass
    
    def get_network_policies(self) -> list[NetworkPolicy]:
        """Get all network policies"""
        pass
    
    def update_policy(self, policy: NetworkPolicy) -> None:
        """Update a policy"""
        pass
    
    def approve_request(self, request_id: str) -> None:
        """Approve a network request"""
        pass
    
    def deny_request(self, request_id: str) -> None:
        """Deny a network request"""
        pass
    
    def stream_logs(self, sandbox_id: str) -> Iterator[LogEntry]:
        """Stream logs from sandbox"""
        pass
    
    def get_gpu_metrics(self) -> GpuMetrics:
        """Get GPU telemetry"""
        pass
    
    def get_network_requests(self) -> list[NetworkRequest]:
        """Get pending network requests"""
        pass
    
    def list_workspace_files(self, sandbox_id: str) -> list[FileEntry]:
        """List files in workspace"""
        pass
    
    def read_file(self, path: str) -> str:
        """Read file contents"""
        pass
```

---

## UI/UX Design Principles

### Visual Language
- **Color Palette**: NVIDIA Green (#76B900) as primary accent
- **Dark Mode**: Default for reduced eye strain during monitoring
- **Data Density**: High information density with clear hierarchy
- **Real-time Indicators**: Subtle animations for live data

### Layout
- **Sidebar Navigation**: Collapsible, persona-aware menu
- **Header**: Current persona indicator, system status, user menu
- **Main Content**: Context-aware dashboard widgets
- **Footer**: Version info, connection status

### Key UI Components

1. **Status Badges**
   - Running: Green pulse
   - Stopped: Gray
   - Warning: Amber
   - Error: Red
   - Pending Approval: Blinking amber

2. **Metric Cards**
   - GPU Utilization: Progress bar + sparkline
   - Memory Usage: Gauge chart
   - Request Rate: Line chart
   - Agent Reputation: Score badge with trend

3. **Network Request Queue**
   - List view with approve/deny actions
   - Request details modal
   - Batch selection for bulk actions

---

## Security Considerations

### Local Deployment Security
- Dashboard binds to localhost only (127.0.0.1)
- No external network exposure by default
- Authentication via local system user
- All OpenShell operations require appropriate OS permissions

### Data Privacy
- No data leaves the local machine
- Logs and telemetry stay local
- Optional anonymization for sharing reports

---

## Development Roadmap

### Sprint 1: Foundation
- Project setup (Python, Streamlit, dependencies)
- Dashboard layout with pages
- Persona switching logic
- Basic OpenShell CLI integration

### Sprint 2: Engineer View
- Sandbox list with status
- GPU telemetry dashboard
- Workspace file browser
- Inference routing UI

### Sprint 3: SecOps View
- Network request queue
- Policy management interface
- Basic reputation scoring
- Log viewer with filtering

### Sprint 4: Advanced Features
- Attack graph visualization
- HITL adjudication workflow
- Forensic playback concept
- Compliance reporting

---

## Resources

### NVIDIA Documentation
- NemoClaw: https://docs.nvidia.com/nemoclaw/latest/index.html
- OpenShell: https://docs.nvidia.com/openshell/latest/index.html
- GitHub: https://github.com/NVIDIA/NemoClaw

### Build Pages
- NemoClaw: https://build.nvidia.com/nemoclaw
- OpenShell Station: https://build.nvidia.com/station/openshell
- OpenShell Spark: https://build.nvidia.com/spark/openshell

### Community
- Discord: https://discord.gg/XFpfPv9Uvx

---

## Notes

- This dashboard runs **locally** alongside NemoClaw installation
- Real-time data comes from local OpenShell CLI and system monitoring
- No cloud connectivity required for core functionality
- Designed for single-user or small team local deployment
- All data stays on the local machine

---

*Last Updated: March 26, 2026*
*Version: 0.1.0 - Ideation Phase*
