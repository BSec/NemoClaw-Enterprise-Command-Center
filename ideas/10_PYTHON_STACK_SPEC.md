# NemoClaw Gateway Dashboard - Python Stack Specification

## Phase: Ideation (v0.1.0)

---

## 1. Technology Stack Overview

### Primary Stack: Streamlit

**Why Streamlit?**
- Pure Python - no frontend framework needed
- Native data visualization support
- Built-in real-time updates via session state
- Perfect for dashboard applications
- Simple to develop, deploy, and maintain
- Wide ecosystem of components

**Alternative Considered**: FastAPI + frontend, Gradio, Dash

**Decision**: Streamlit selected for rapid development and dashboard-optimized features

---

## 2. Core Dependencies

### requirements.txt

```txt
# Web Framework
streamlit>=1.30.0
streamlit-elements>=0.1.0
streamlit-extras>=0.3.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0

# Visualization
plotly>=5.18.0
altair>=5.2.0
matplotlib>=3.8.0

# System Integration
psutil>=5.9.0
pynvml>=11.5.0
watchdog>=3.0.0

# OpenShell Integration
pyyaml>=6.0.0
requests>=2.31.0

# Utilities
pydantic>=2.5.0
python-dateutil>=2.8.0
humanize>=4.9.0
tabulate>=0.9.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.7.0
```

---

## 3. Architecture Components

### 3.1 Main Application Structure

```
nemoclaw-gateway-dashboard/
├── app.py                          # Entry point
├── pages/                          # Streamlit pages (auto-discovered)
│   ├── 01_Engineer_View.py
│   ├── 02_SecOps_View.py
│   ├── 03_CISO_View.py
│   └── 04_Settings.py
├── components/                     # Reusable UI components
│   ├── __init__.py
│   ├── sandbox_cards.py
│   ├── gpu_metrics.py
│   ├── log_viewer.py
│   ├── request_queue.py
│   └── reputation.py
├── services/                       # Business logic
│   ├── __init__.py
│   ├── openshell.py
│   ├── nemoclaw.py
│   ├── gpu_monitor.py
│   ├── file_watcher.py
│   └── telemetry.py
├── models/                         # Data models
│   ├── __init__.py
│   ├── sandbox.py
│   ├── policy.py
│   ├── request.py
│   └── reputation.py
├── utils/                          # Utilities
│   ├── __init__.py
│   ├── config.py
│   ├── styling.py
│   └── helpers.py
├── config/                         # Configuration
│   ├── default.yaml
│   └── themes/
├── tests/                          # Test suite
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── requirements.txt
└── README.md
```

### 3.2 Entry Point (app.py)

```python
"""NemoClaw Gateway Dashboard - Main Application"""

import streamlit as st
from utils.config import load_config
from utils.styling import apply_theme

# Page configuration
st.set_page_config(
    page_title="NemoClaw Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = load_config()

# Apply custom theme
apply_theme(config.theme)

# Main layout
st.title("🛡️ NemoClaw Gateway Dashboard")
st.markdown("*Safe-by-Default AI Control Plane*")

# Persona selector in sidebar
with st.sidebar:
    st.header("Select Persona")
    
    persona = st.radio(
        "View as:",
        options=["Engineer", "SecOps", "CISO"],
        index=0,
        help="Switch between different dashboard views based on your role"
    )
    
    # Store in session state
    st.session_state.persona = persona
    
    st.divider()
    
    # System status
    st.subheader("System Status")
    st.success("🟢 Connected to OpenShell")
    
    # Active sandboxes count
    from services.openshell import OpenShellService
    service = OpenShellService()
    sandboxes = service.list_sandboxes()
    active_count = sum(1 for s in sandboxes if s.status == "running")
    
    st.metric("Active Sandboxes", active_count, len(sandboxes))

# Redirect to appropriate page based on persona
if persona == "Engineer":
    st.info("👨‍💻 **Engineer View**: Manage sandboxes, monitor resources, debug agents")
    st.page_link("pages/01_Engineer_View.py", label="Go to Engineer View", icon="🔧")
    
elif persona == "SecOps":
    st.info("🛡️ **SecOps View**: Monitor security, approve requests, investigate threats")
    st.page_link("pages/02_SecOps_View.py", label="Go to SecOps View", icon="🔒")
    
elif persona == "CISO":
    st.info("📊 **CISO View**: Compliance dashboard, executive reports, risk analysis")
    st.page_link("pages/03_CISO_View.py", label="Go to CISO View", icon="📈")
```

---

## 4. Service Layer Design

### 4.1 OpenShell Service

```python
"""OpenShell CLI integration service"""

import subprocess
import json
from typing import Iterator, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Sandbox:
    id: str
    name: str
    status: str
    agent_type: str
    workspace_path: str
    created_at: datetime
    updated_at: datetime


class OpenShellService:
    """Service for interacting with OpenShell CLI"""
    
    def __init__(self, cli_path: str = "openshell"):
        self.cli_path = cli_path
        self._cache = {}
        
    def _run_command(self, *args, capture_json: bool = True) -> dict | str:
        """Execute openshell CLI command"""
        cmd = [self.cli_path] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            if capture_json:
                return json.loads(result.stdout)
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenShell command failed: {e.stderr}")
            raise OpenShellError(f"Command failed: {e.stderr}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise OpenShellError("Invalid JSON response from CLI")
    
    def list_sandboxes(self) -> list[Sandbox]:
        """List all sandboxes"""
        response = self._run_command("list", "sandboxes", "--json")
        
        sandboxes = []
        for item in response.get("sandboxes", []):
            sandboxes.append(Sandbox(
                id=item["id"],
                name=item["name"],
                status=item["status"],
                agent_type=item.get("agent_type", "unknown"),
                workspace_path=item.get("workspace_path", ""),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"])
            ))
        
        return sandboxes
    
    def get_sandbox_status(self, sandbox_id: str) -> dict:
        """Get detailed sandbox status"""
        return self._run_command("sandbox", "status", sandbox_id, "--json")
    
    def start_sandbox(self, sandbox_id: str) -> bool:
        """Start a sandbox"""
        try:
            self._run_command("sandbox", "start", sandbox_id)
            return True
        except OpenShellError:
            return False
    
    def stop_sandbox(self, sandbox_id: str) -> bool:
        """Stop a sandbox"""
        try:
            self._run_command("sandbox", "stop", sandbox_id)
            return True
        except OpenShellError:
            return False
    
    def stream_logs(self, sandbox_id: str) -> Iterator[str]:
        """Stream logs from sandbox in real-time"""
        cmd = [self.cli_path, "logs", sandbox_id, "--follow"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line.strip()
        finally:
            process.terminate()
    
    def get_network_requests(self, status: str = "pending") -> list[dict]:
        """Get network requests"""
        return self._run_command(
            "request", "list", 
            "--status", status,
            "--json"
        )
    
    def approve_request(self, request_id: str) -> bool:
        """Approve a network request"""
        try:
            self._run_command("request", "approve", request_id)
            return True
        except OpenShellError:
            return False
    
    def deny_request(self, request_id: str) -> bool:
        """Deny a network request"""
        try:
            self._run_command("request", "deny", request_id)
            return True
        except OpenShellError:
            return False


class OpenShellError(Exception):
    """OpenShell CLI error"""
    pass
```

### 4.2 GPU Monitor Service

```python
"""GPU telemetry monitoring using NVML"""

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class GpuMetrics:
    index: int
    name: str
    utilization: float  # 0-100
    memory_used: int    # MB
    memory_total: int   # MB
    temperature: float  # Celsius
    power_draw: float   # Watts
    power_limit: float  # Watts


class GpuMonitor:
    """GPU monitoring using NVIDIA NVML"""
    
    def __init__(self):
        self.nvml = None
        self._initialized = False
        self._try_init()
    
    def _try_init(self):
        """Try to initialize NVML"""
        try:
            from pynvml import nvmlInit, nvmlShutdown
            nvmlInit()
            self.nvml = __import__('pynvml')
            self._initialized = True
            logger.info("NVML initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize NVML: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if GPU monitoring is available"""
        return self._initialized
    
    def get_gpu_count(self) -> int:
        """Get number of GPUs"""
        if not self._initialized:
            return 0
        return self.nvml.nvmlDeviceGetCount()
    
    def get_metrics(self) -> list[GpuMetrics]:
        """Get metrics for all GPUs"""
        if not self._initialized:
            return []
        
        metrics = []
        for i in range(self.get_gpu_count()):
            try:
                handle = self.nvml.nvmlDeviceGetHandleByIndex(i)
                
                # GPU name
                name = self.nvml.nvmlDeviceGetName(handle)
                
                # Utilization
                util = self.nvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Memory
                mem = self.nvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Temperature
                temp = self.nvml.nvmlDeviceGetTemperature(
                    handle, 
                    self.nvml.NVML_TEMPERATURE_GPU
                )
                
                # Power
                power_draw = self.nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                power_limit = self.nvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
                
                metrics.append(GpuMetrics(
                    index=i,
                    name=name,
                    utilization=util.gpu,
                    memory_used=mem.used // 1024 // 1024,  # Convert to MB
                    memory_total=mem.total // 1024 // 1024,
                    temperature=temp,
                    power_draw=power_draw,
                    power_limit=power_limit
                ))
                
            except Exception as e:
                logger.error(f"Failed to get metrics for GPU {i}: {e}")
        
        return metrics
    
    def __del__(self):
        """Cleanup NVML"""
        if self._initialized and self.nvml:
            try:
                self.nvml.nvmlShutdown()
            except:
                pass
```

### 4.3 File Watcher Service

```python
"""File system watching for real-time updates"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if isinstance(event, FileModifiedEvent):
            logger.info(f"File modified: {event.src_path}")
            self.callback(event.src_path)


class FileWatcher:
    """Watch files for changes"""
    
    def __init__(self, watch_paths: list[str], callback):
        self.watch_paths = [Path(p) for p in watch_paths]
        self.callback = callback
        self.observer = Observer()
        self._running = False
    
    def start(self):
        """Start watching"""
        handler = ConfigFileHandler(self.callback)
        
        for path in self.watch_paths:
            if path.exists():
                self.observer.schedule(handler, str(path), recursive=True)
                logger.info(f"Watching: {path}")
        
        self.observer.start()
        self._running = True
        logger.info("File watcher started")
    
    def stop(self):
        """Stop watching"""
        if self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            logger.info("File watcher stopped")
```

---

## 5. Component Design

### 5.1 Sandbox Cards Component

```python
"""Sandbox status card components"""

import streamlit as st
from models.sandbox import Sandbox
from services.openshell import OpenShellService
from services.gpu_monitor import GpuMonitor
import humanize
from datetime import datetime


def render_sandbox_card(sandbox: Sandbox, service: OpenShellService) -> None:
    """Render a single sandbox card"""
    
    # Status colors
    status_colors = {
        "running": "🟢",
        "stopped": "⚫",
        "error": "🔴",
        "pending": "🟡",
        "quarantined": "🟠"
    }
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"{status_colors.get(sandbox.status, '⚪')} {sandbox.name}")
            st.caption(f"ID: {sandbox.id}")
            st.caption(f"Agent: {sandbox.agent_type}")
        
        with col2:
            st.metric("Status", sandbox.status.upper())
            st.caption(f"Created: {humanize.naturaltime(datetime.now() - sandbox.created_at)}")
        
        with col3:
            # Quick actions
            if sandbox.status == "running":
                if st.button("⏹️ Stop", key=f"stop_{sandbox.id}"):
                    service.stop_sandbox(sandbox.id)
                    st.rerun()
            elif sandbox.status == "stopped":
                if st.button("▶️ Start", key=f"start_{sandbox.id}"):
                    service.start_sandbox(sandbox.id)
                    st.rerun()
            
            if st.button("📄 Logs", key=f"logs_{sandbox.id}"):
                st.session_state.selected_sandbox = sandbox.id
                st.session_state.view = "logs"
        
        st.divider()


def render_sandbox_grid(sandboxes: list[Sandbox], service: OpenShellService) -> None:
    """Render grid of sandbox cards"""
    
    if not sandboxes:
        st.info("No sandboxes found. Create one to get started.")
        return
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    with col1:
        status_filter = st.multiselect(
            "Filter by status",
            options=["running", "stopped", "error", "pending"],
            default=["running", "stopped", "error"]
        )
    
    with col2:
        st.metric("Total", len(sandboxes))
    
    # Filter sandboxes
    filtered = [s for s in sandboxes if s.status in status_filter]
    
    # Render cards
    for sandbox in filtered:
        render_sandbox_card(sandbox, service)
```

### 5.2 GPU Metrics Component

```python
"""GPU telemetry dashboard components"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from services.gpu_monitor import GpuMonitor
import pandas as pd
import time


def render_gpu_dashboard(gpu_monitor: GpuMonitor) -> None:
    """Render GPU metrics dashboard"""
    
    st.header("🎮 GPU Telemetry")
    
    if not gpu_monitor.is_available():
        st.warning("GPU monitoring not available. NVIDIA drivers or pynvml not installed.")
        return
    
    # Auto-refresh checkbox
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Get metrics
    metrics = gpu_monitor.get_metrics()
    
    if not metrics:
        st.info("No GPUs detected")
        return
    
    # GPU selector
    selected_gpus = st.multiselect(
        "Select GPUs to display",
        options=[f"GPU {m.index}: {m.name}" for m in metrics],
        default=[f"GPU {m.index}: {m.name}" for m in metrics]
    )
    
    # Filter metrics
    selected_indices = [int(s.split(":")[0].replace("GPU ", "")) for s in selected_gpus]
    filtered_metrics = [m for m in metrics if m.index in selected_indices]
    
    # Render metrics for each GPU
    for gpu in filtered_metrics:
        with st.container():
            st.subheader(f"GPU {gpu.index}: {gpu.name}")
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                fig_util = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gpu.utilization,
                    title={"text": "Utilization %"},
                    gauge={"axis": {"range": [0, 100]},
                           "bar": {"color": "#76B900"},
                           "steps": [
                               {"range": [0, 50], "color": "lightgray"},
                               {"range": [50, 80], "color": "yellow"},
                               {"range": [80, 100], "color": "red"}
                           ]}
                ))
                fig_util.update_layout(height=250)
                st.plotly_chart(fig_util, use_container_width=True)
            
            with col2:
                memory_percent = (gpu.memory_used / gpu.memory_total) * 100
                st.metric(
                    "Memory",
                    f"{gpu.memory_used:.0f} MB",
                    f"{memory_percent:.1f}%"
                )
            
            with col3:
                st.metric("Temperature", f"{gpu.temperature}°C")
            
            with col4:
                power_percent = (gpu.power_draw / gpu.power_limit) * 100
                st.metric(
                    "Power",
                    f"{gpu.power_draw:.1f}W",
                    f"{power_percent:.1f}%"
                )
            
            st.divider()
```

### 5.3 Request Queue Component

```python
"""Network request queue components"""

import streamlit as st
import pandas as pd
from services.openshell import OpenShellService
import humanize
from datetime import datetime


def render_request_queue(service: OpenShellService) -> None:
    """Render network request approval queue"""
    
    st.header("🌐 Network Request Queue")
    
    # Get pending requests
    requests = service.get_network_requests(status="pending")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pending", len(requests))
    with col2:
        st.metric("Approved Today", 45)
    with col3:
        st.metric("Denied Today", 3)
    
    st.divider()
    
    if not requests:
        st.success("No pending requests! 🎉")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(requests)
    
    # Risk score coloring
    def color_risk(val):
        if val >= 80:
            return "background-color: #ffcccc"
        elif val >= 50:
            return "background-color: #ffffcc"
        return "background-color: #ccffcc"
    
    # Display table
    st.dataframe(
        df.style.applymap(color_risk, subset=["risk_score"]),
        use_container_width=True,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "timestamp": st.column_config.DatetimeColumn("Time"),
            "agent_id": st.column_config.TextColumn("Agent"),
            "url": st.column_config.LinkColumn("URL"),
            "risk_score": st.column_config.NumberColumn("Risk", format="%d"),
        },
        hide_index=True
    )
    
    # Action buttons
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Approve All Low Risk", type="primary"):
            for req in requests:
                if req["risk_score"] < 50:
                    service.approve_request(req["id"])
            st.success("Approved low-risk requests")
            st.rerun()
    
    with col2:
        if st.button("❌ Deny All High Risk"):
            for req in requests:
                if req["risk_score"] >= 80:
                    service.deny_request(req["id"])
            st.success("Denied high-risk requests")
            st.rerun()
```

---

## 6. Page Designs

### 6.1 Engineer View Page

```python
"""pages/01_Engineer_View.py - Engineer persona dashboard"""

import streamlit as st
from services.openshell import OpenShellService
from services.gpu_monitor import GpuMonitor
from components.sandbox_cards import render_sandbox_grid
from components.gpu_metrics import render_gpu_dashboard
from components.log_viewer import render_log_viewer

st.set_page_config(
    page_title="Engineer View - NemoClaw Gateway",
    page_icon="🔧",
    layout="wide"
)

st.title("👨‍💻 Engineer View")
st.caption("Manage sandboxes, monitor resources, debug agents")

# Initialize services
service = OpenShellService()
gpu_monitor = GpuMonitor()

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["🖥️ Sandboxes", "🎮 GPU Metrics", "📜 Logs"])

with tab1:
    st.header("Sandbox Management")
    
    # New sandbox button
    if st.button("➕ Create New Sandbox", type="primary"):
        st.session_state.show_create_dialog = True
    
    # List sandboxes
    sandboxes = service.list_sandboxes()
    render_sandbox_grid(sandboxes, service)

with tab2:
    render_gpu_dashboard(gpu_monitor)

with tab3:
    render_log_viewer(service)
```

### 6.2 SecOps View Page

```python
"""pages/02_SecOps_View.py - SecOps persona dashboard"""

import streamlit as st
from services.openshell import OpenShellService
from components.request_queue import render_request_queue
from components.reputation import render_reputation_dashboard

st.set_page_config(
    page_title="SecOps View - NemoClaw Gateway",
    page_icon="🔒",
    layout="wide"
)

st.title("🛡️ SecOps View")
st.caption("Monitor security, approve requests, investigate threats")

service = OpenShellService()

tab1, tab2 = st.tabs(["🌐 Request Queue", "📊 Agent Reputation"])

with tab1:
    render_request_queue(service)

with tab2:
    render_reputation_dashboard()
```

---

## 7. Configuration

### 7.1 Streamlit Config (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#76B900"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E6EDF3"
font = "sans serif"

[server]
headless = true
address = "127.0.0.1"
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[logger]
level = "info"
```

### 7.2 Default Config (config/default.yaml)

```yaml
app:
  name: "NemoClaw Gateway Dashboard"
  version: "0.1.0"
  refresh_interval: 5  # seconds
  
openshell:
  cli_path: "openshell"
  timeout: 30
  
gpu:
  enabled: true
  sample_interval: 2  # seconds
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
security:
  bind_address: "127.0.0.1"
  require_localhost: true
  log_all_actions: true
```

---

## 8. Development Workflow

### 8.1 Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Or with custom config
streamlit run app.py --server.port 8080 --theme.base dark
```

### 8.2 Testing

```python
# tests/test_openshell.py
import pytest
from unittest.mock import patch, MagicMock
from services.openshell import OpenShellService

def test_list_sandboxes():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = '{"sandboxes": []}'
        mock_run.return_value.returncode = 0
        
        service = OpenShellService()
        sandboxes = service.list_sandboxes()
        
        assert len(sandboxes) == 0

def test_start_sandbox():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        service = OpenShellService()
        result = service.start_sandbox("sandbox-123")
        
        assert result is True
```

### 8.3 Code Quality

```bash
# Format code
black app.py components/ services/ models/ utils/

# Lint
ruff check app.py components/ services/ models/ utils/

# Type check
mypy services/

# Run tests
pytest tests/ -v
```

---

## 9. Deployment

### 9.1 Local Deployment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

### 9.2 Production Considerations

- **Process Management**: Use systemd or supervisor
- **Logging**: Configure log rotation
- **Security**: Firewall rules (localhost only)
- **Backup**: Regular config backup

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
