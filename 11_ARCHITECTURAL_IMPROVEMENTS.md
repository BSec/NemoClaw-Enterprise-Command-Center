# NemoClaw Gateway Dashboard - Architectural Improvements

## Phase: Ideation (v0.1.0)

---

## Executive Summary

Based on review of current architecture, the following improvements are recommended to enhance **stability**, **functionality**, and **usefulness** before development begins.

---

## 1. Stability Improvements

### 1.1 Error Handling & Resilience

**Current Gap**: No explicit error handling strategy for OpenShell CLI failures, GPU monitoring unavailability, or network issues.

**Recommendations**:

```python
# Add to services/base_service.py
from typing import Optional, TypeVar, Callable
from functools import wraps
import time
import logging

T = TypeVar('T')

class ServiceError(Exception):
    """Base service error"""
    pass

class RetryableError(ServiceError):
    """Error that can be retried"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern for external calls"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise ServiceError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            raise e

def retry_with_backoff(max_retries=3, base_delay=1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    logging.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

**Implementation Priority**: High (Sprint 1)

---

### 1.2 Health Check & Monitoring System

**Current Gap**: No built-in health checks for dashboard components or dependencies.

**Recommendation**: Add health check framework

```python
# services/health_check.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import subprocess

@dataclass
class HealthStatus:
    component: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    message: str
    last_check: datetime
    response_time_ms: float

class HealthCheckService:
    """Centralized health monitoring"""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check"""
        self.checks[name] = check_func
    
    def check_all(self) -> Dict[str, HealthStatus]:
        """Run all health checks"""
        results = {}
        for name, check_func in self.checks.items():
            start = datetime.now()
            try:
                status, message = check_func()
            except Exception as e:
                status, message = 'unhealthy', str(e)
            
            elapsed = (datetime.now() - start).total_seconds() * 1000
            results[name] = HealthStatus(
                component=name,
                status=status,
                message=message,
                last_check=datetime.now(),
                response_time_ms=elapsed
            )
        return results
    
    def check_openshell(self) -> tuple:
        """Check OpenShell CLI availability"""
        try:
            result = subprocess.run(
                ['openshell', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'healthy', 'OpenShell CLI responding'
            return 'degraded', f'OpenShell error: {result.stderr}'
        except Exception as e:
            return 'unhealthy', str(e)
    
    def check_gpu(self) -> tuple:
        """Check GPU monitoring availability"""
        try:
            from pynvml import nvmlInit, nvmlShutdown
            nvmlInit()
            nvmlShutdown()
            return 'healthy', 'GPU monitoring available'
        except:
            return 'degraded', 'GPU monitoring unavailable (CPU-only mode)'
    
    def check_disk_space(self) -> tuple:
        """Check available disk space"""
        import shutil
        stat = shutil.disk_usage('/')
        free_gb = stat.free / (1024**3)
        if free_gb < 1:
            return 'unhealthy', f'Critical: only {free_gb:.1f}GB free'
        elif free_gb < 5:
            return 'degraded', f'Low disk: {free_gb:.1f}GB free'
        return 'healthy', f'{free_gb:.1f}GB available'
```

**UI Integration**: Add health status indicator to dashboard header

---

### 1.3 Graceful Degradation

**Current Gap**: If GPU monitoring fails, entire dashboard may fail.

**Recommendation**: Implement feature flags with graceful degradation

```python
# utils/feature_flags.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class FeatureStatus:
    enabled: bool
    available: bool
    fallback_message: Optional[str] = None

class FeatureManager:
    """Manage feature availability"""
    
    def __init__(self):
        self.features = {}
        self.health_service = None
    
    def register(self, name: str, check_func, required=True):
        """Register a feature with health check"""
        self.features[name] = {
            'check': check_func,
            'required': required,
            'status': None
        }
    
    def check_feature(self, name: str) -> FeatureStatus:
        """Check if feature is available"""
        feature = self.features.get(name)
        if not feature:
            return FeatureStatus(False, False, "Unknown feature")
        
        try:
            available, message = feature['check']()
            return FeatureStatus(True, available, None if available else message)
        except Exception as e:
            if feature['required']:
                return FeatureStatus(True, False, f"Feature error: {e}")
            return FeatureStatus(False, False, f"Optional feature unavailable: {e}")
    
    def get_available_features(self) -> list:
        """Get list of available features"""
        available = []
        for name in self.features:
            status = self.check_feature(name)
            if status.available:
                available.append(name)
        return available

# Usage in components
def render_gpu_dashboard(feature_manager: FeatureManager):
    status = feature_manager.check_feature('gpu_monitoring')
    
    if not status.enabled:
        return  # Don't show GPU section at all
    
    if not status.available:
        st.info(f"⚠️ GPU Monitoring: {status.fallback_message}")
        st.markdown("CPU-only mode active. GPU metrics unavailable.")
        return
    
    # Render full GPU dashboard
    ...
```

---

### 1.4 Data Persistence Layer

**Current Gap**: Session state lost on page refresh, no local data caching.

**Recommendation**: Abstract data layer with multiple backends

```python
# services/data_store.py
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import sqlite3
from pathlib import Path

class DataStore(ABC):
    """Abstract data store interface"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        pass
    
    @abstractmethod
    def delete(self, key: str):
        pass

class SQLiteStore(DataStore):
    """SQLite-based persistent store"""
    
    def __init__(self, db_path: str = "~/.nemoclaw/dashboard.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at TIMESTAMP
                )
            """)
    
    def get(self, key: str) -> Optional[Any]:
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT value FROM store WHERE key = ? AND (expires_at IS NULL OR expires_at > datetime('now'))",
                (key,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        import datetime
        expires = None
        if ttl:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO store (key, value, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), expires)
            )

class MemoryStore(DataStore):
    """In-memory store for session data"""
    
    def __init__(self):
        self._store = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self._store[key] = value
    
    def delete(self, key: str):
        self._store.pop(key, None)

class HybridStore(DataStore):
    """Hybrid: Memory for speed, SQLite for persistence"""
    
    def __init__(self):
        self.memory = MemoryStore()
        self.persistent = SQLiteStore()
    
    def get(self, key: str) -> Optional[Any]:
        # Try memory first
        value = self.memory.get(key)
        if value is not None:
            return value
        
        # Fall back to persistent
        value = self.persistent.get(key)
        if value is not None:
            # Populate memory cache
            self.memory.set(key, value)
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, persistent: bool = False):
        self.memory.set(key, value, ttl)
        if persistent:
            self.persistent.set(key, value, ttl)
    
    def delete(self, key: str):
        self.memory.delete(key)
        self.persistent.delete(key)
```

---

## 2. Functionality Enhancements

### 2.1 Plugin/Extension System

**Current Gap**: No way to extend dashboard functionality without modifying core code.

**Recommendation**: Simple plugin architecture

```python
# plugins/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import streamlit as st

class DashboardPlugin(ABC):
    """Base class for dashboard plugins"""
    
    name: str = "Unnamed Plugin"
    version: str = "1.0.0"
    author: str = "Unknown"
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        pass
    
    @abstractmethod
    def get_widgets(self) -> List[Dict]:
        """Return list of widgets provided by plugin"""
        pass
    
    @abstractmethod
    def render_widget(self, widget_id: str):
        """Render specific widget"""
        pass

class PluginManager:
    """Manage dashboard plugins"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, DashboardPlugin] = {}
    
    def load_plugins(self):
        """Load all plugins from plugin directory"""
        if not self.plugin_dir.exists():
            return
        
        for plugin_file in self.plugin_dir.glob("*_plugin.py"):
            try:
                self._load_plugin(plugin_file)
            except Exception as e:
                logging.error(f"Failed to load plugin {plugin_file}: {e}")
    
    def _load_plugin(self, plugin_file: Path):
        """Load single plugin"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin class
        for attr in dir(module):
            obj = getattr(module, attr)
            if (isinstance(obj, type) and 
                issubclass(obj, DashboardPlugin) and 
                obj != DashboardPlugin):
                plugin = obj()
                self.plugins[plugin.name] = plugin
                logging.info(f"Loaded plugin: {plugin.name} v{plugin.version}")

# Example plugin
# plugins/example_plugin.py
class ExamplePlugin(DashboardPlugin):
    name = "Example Plugin"
    version = "1.0.0"
    author = "NemoClaw Team"
    
    def initialize(self, config):
        self.api_key = config.get('api_key')
    
    def get_widgets(self):
        return [
            {
                'id': 'example_widget',
                'name': 'Example Widget',
                'description': 'A demonstration widget',
                'category': 'custom'
            }
        ]
    
    def render_widget(self, widget_id):
        if widget_id == 'example_widget':
            st.write("Hello from plugin!")
```

---

### 2.2 Automation & Workflow Engine

**Current Gap**: Manual operations only, no automation capabilities.

**Recommendation**: Add workflow automation system

```python
# services/workflow_engine.py
from dataclasses import dataclass
from typing import List, Dict, Callable, Any
from datetime import datetime, timedelta
import json
from enum import Enum

class TriggerType(Enum):
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"

class ActionType(Enum):
    START_SANDBOX = "start_sandbox"
    STOP_SANDBOX = "stop_sandbox"
    SEND_NOTIFICATION = "send_notification"
    EXECUTE_COMMAND = "execute_command"
    UPDATE_POLICY = "update_policy"

@dataclass
class WorkflowTrigger:
    type: TriggerType
    config: Dict[str, Any]  # schedule: cron, event: condition

@dataclass
class WorkflowAction:
    type: ActionType
    config: Dict[str, Any]
    conditions: List[Dict]  # Pre-conditions
    on_error: str  # 'continue', 'stop', 'retry'

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    enabled: bool
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    created_at: datetime
    last_run: Optional[datetime]
    run_count: int

class WorkflowEngine:
    """Execute automated workflows"""
    
    def __init__(self, data_store: DataStore):
        self.store = data_store
        self.workflows: Dict[str, Workflow] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """Register action type handlers"""
        self.action_handlers[ActionType.START_SANDBOX] = self._handle_start_sandbox
        self.action_handlers[ActionType.STOP_SANDBOX] = self._handle_stop_sandbox
        self.action_handlers[ActionType.SEND_NOTIFICATION] = self._handle_notification
    
    def create_workflow(self, workflow: Workflow) -> str:
        """Create and store workflow"""
        self.workflows[workflow.id] = workflow
        self.store.set(f"workflow:{workflow.id}", {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'enabled': workflow.enabled,
            'trigger': {
                'type': workflow.trigger.type.value,
                'config': workflow.trigger.config
            },
            'actions': [
                {
                    'type': a.type.value,
                    'config': a.config,
                    'conditions': a.conditions,
                    'on_error': a.on_error
                }
                for a in workflow.actions
            ]
        }, persistent=True)
        return workflow.id
    
    def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        if not workflow.enabled:
            return {'success': False, 'error': 'Workflow disabled'}
        
        results = []
        for action in workflow.actions:
            try:
                # Check pre-conditions
                if not self._check_conditions(action.conditions, context):
                    results.append({'action': action.type.value, 'skipped': True})
                    continue
                
                # Execute action
                handler = self.action_handlers.get(action.type)
                if handler:
                    result = handler(action.config, context)
                    results.append({'action': action.type.value, 'success': True, 'result': result})
                else:
                    results.append({'action': action.type.value, 'error': 'No handler'})
                    
            except Exception as e:
                results.append({'action': action.type.value, 'error': str(e)})
                if action.on_error == 'stop':
                    break
        
        # Update workflow stats
        workflow.last_run = datetime.now()
        workflow.run_count += 1
        
        return {'success': True, 'results': results}
    
    def _check_conditions(self, conditions: List[Dict], context: Dict) -> bool:
        """Evaluate action pre-conditions"""
        for condition in conditions:
            # Example: {'field': 'gpu.utilization', 'operator': 'gt', 'value': 80}
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            # Resolve field from context
            actual_value = self._resolve_field(field, context)
            
            if operator == 'gt' and not (actual_value > value):
                return False
            elif operator == 'lt' and not (actual_value < value):
                return False
            elif operator == 'eq' and not (actual_value == value):
                return False
        return True
    
    def _handle_start_sandbox(self, config, context):
        """Start sandbox action"""
        sandbox_id = config.get('sandbox_id')
        # Call OpenShell service
        pass
    
    def _handle_notification(self, config, context):
        """Send notification action"""
        message = config.get('message')
        channels = config.get('channels', ['ui'])
        # Send to configured channels
        pass
```

**Use Cases**:
- Auto-start sandboxes at 9 AM
- Stop idle sandboxes after 30 minutes
- Alert when GPU utilization > 90%
- Daily backup of critical workspaces

---

### 2.3 Configuration Management

**Current Gap**: No versioning or validation for configuration files.

**Recommendation**: Schema-based config with validation

```python
# utils/config_manager.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, validator, Field

class SandboxConfigSchema(BaseModel):
    """Schema for sandbox configuration"""
    name: str = Field(..., min_length=1, max_length=64)
    agent_type: str = Field(..., pattern="^(openai|anthropic|ollama|custom)$")
    workspace_path: Path
    gpu_enabled: bool = True
    max_memory_gb: float = Field(default=8.0, ge=1.0, le=128.0)
    auto_start: bool = False
    
    @validator('workspace_path')
    def validate_path(cls, v):
        if not v.exists():
            raise ValueError(f"Path does not exist: {v}")
        return v

class DashboardConfigSchema(BaseModel):
    """Schema for dashboard configuration"""
    version: str = "1.0.0"
    mode: str = Field(default="personal", pattern="^(personal|enterprise)$")
    refresh_interval: int = Field(default=5, ge=1, le=300)
    
    # Personal mode settings
    local_db_path: Path = Path("~/.nemoclaw/dashboard.db")
    
    # Enterprise mode settings
    auth_provider: Optional[str] = None
    session_timeout: int = Field(default=3600, ge=300)
    
    # Feature toggles
    features: Dict[str, bool] = field(default_factory=dict)
    
    @validator('features', pre=True, always=True)
    def set_defaults(cls, v):
        defaults = {
            'gpu_monitoring': True,
            'log_aggregation': True,
            'policy_management': True,
            'attack_graph': False,  # Phase 2+
            'compliance_dashboard': False  # Phase 3+
        }
        defaults.update(v or {})
        return defaults

class ConfigManager:
    """Manage dashboard configuration with validation"""
    
    def __init__(self, config_path: str = "~/.nemoclaw/config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[DashboardConfigSchema] = None
    
    def load(self) -> DashboardConfigSchema:
        """Load and validate configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            self._config = DashboardConfigSchema(**data)
        else:
            self._config = DashboardConfigSchema()
            self.save()
        return self._config
    
    def save(self):
        """Save configuration to file"""
        if self._config:
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config.dict(), f, default_flow_style=False)
    
    def update(self, updates: Dict):
        """Update configuration with validation"""
        if self._config:
            current = self._config.dict()
            current.update(updates)
            self._config = DashboardConfigSchema(**current)
            self.save()
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        if self._config:
            return getattr(self._config, key, default)
        return default
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        if self._config and self._config.features:
            return self._config.features.get(feature, False)
        return False
```

---

## 3. Usefulness Improvements

### 3.1 Command Palette / Quick Actions

**Current Gap**: Users must navigate through menus for common actions.

**Recommendation**: Add command palette (Ctrl+K / Cmd+K)

```python
# components/command_palette.py
import streamlit as st
from typing import List, Dict, Callable
from dataclasses import dataclass
import re

@dataclass
class Command:
    id: str
    title: str
    shortcut: str
    category: str
    icon: str
    action: Callable
    condition: Callable = None  # When to show command

class CommandPalette:
    """Quick action command palette"""
    
    def __init__(self):
        self.commands: List[Command] = []
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default commands"""
        self.register(Command(
            id="new_sandbox",
            title="Create New Sandbox",
            shortcut="Ctrl+N",
            category="Sandbox",
            icon="➕",
            action=lambda: st.session_state.update({'show_create_dialog': True})
        ))
        
        self.register(Command(
            id="stop_all_sandboxes",
            title="Stop All Sandboxes",
            shortcut="Ctrl+Shift+S",
            category="Sandbox",
            icon="⏹️",
            action=self._stop_all_sandboxes,
            condition=lambda: len(st.session_state.get('running_sandboxes', [])) > 0
        ))
        
        self.register(Command(
            id="view_logs",
            title="View System Logs",
            shortcut="Ctrl+L",
            category="Monitoring",
            icon="📜",
            action=lambda: st.session_state.update({'current_view': 'logs'})
        ))
        
        self.register(Command(
            id="approve_all_low_risk",
            title="Approve All Low Risk Requests",
            shortcut="Ctrl+Shift+A",
            category="Security",
            icon="✅",
            action=self._approve_low_risk,
            condition=lambda: st.session_state.get('has_pending_requests', False)
        ))
        
        self.register(Command(
            id="export_logs",
            title="Export Logs to CSV",
            shortcut="Ctrl+E",
            category="Data",
            icon="📊",
            action=self._export_logs
        ))
        
        self.register(Command(
            id="toggle_theme",
            title="Toggle Dark/Light Theme",
            shortcut="Ctrl+T",
            category="UI",
            icon="🌓",
            action=self._toggle_theme
        ))
    
    def register(self, command: Command):
        """Register a new command"""
        self.commands.append(command)
    
    def search(self, query: str) -> List[Command]:
        """Search commands by query"""
        query = query.lower()
        results = []
        
        for cmd in self.commands:
            # Check if command should be shown
            if cmd.condition and not cmd.condition():
                continue
            
            # Match against title, id, or category
            if (query in cmd.title.lower() or 
                query in cmd.id.lower() or 
                query in cmd.category.lower()):
                results.append(cmd)
        
        return results
    
    def render(self):
        """Render command palette UI"""
        # Modal dialog
        with st.modal("Command Palette"):
            query = st.text_input(
                "Search commands...",
                placeholder="Type to search (e.g., 'new sandbox', 'logs')",
                key="command_search"
            )
            
            if query:
                results = self.search(query)
                
                for cmd in results:
                    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
                    
                    with col1:
                        st.write(cmd.icon)
                    
                    with col2:
                        st.write(f"**{cmd.title}**")
                        st.caption(f"{cmd.category}")
                    
                    with col3:
                        st.code(cmd.shortcut, language=None)
                    
                    if st.button("Run", key=f"cmd_{cmd.id}"):
                        cmd.action()
                        st.rerun()
            else:
                # Show recent/favorite commands
                st.caption("Recent Commands")
                for cmd in self.commands[:5]:  # Show first 5 as examples
                    if cmd.condition is None or cmd.condition():
                        st.write(f"{cmd.icon} **{cmd.title}** `{cmd.shortcut}`")

    def _stop_all_sandboxes(self):
        """Stop all running sandboxes"""
        # Implementation
        pass
    
    def _approve_low_risk(self):
        """Approve all low risk requests"""
        # Implementation
        pass
    
    def _export_logs(self):
        """Export logs"""
        # Implementation
        pass
    
    def _toggle_theme(self):
        """Toggle theme"""
        current = st.session_state.get('theme', 'dark')
        st.session_state['theme'] = 'light' if current == 'dark' else 'dark'
```

---

### 3.2 Smart Search & Discovery

**Current Gap**: Limited search capabilities across logs, sandboxes, policies.

**Recommendation**: Unified search with indexing

```python
# services/search_engine.py
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class SearchResult:
    id: str
    type: str  # 'sandbox', 'log', 'policy', 'request'
    title: str
    snippet: str
    timestamp: datetime
    relevance: float
    metadata: Dict[str, Any]

class SearchEngine:
    """Unified search across all dashboard data"""
    
    def __init__(self):
        self.indexers = {}
        self.search_history = []
    
    def register_indexer(self, type_name: str, indexer_func):
        """Register a data type indexer"""
        self.indexers[type_name] = indexer_func
    
    def search(self, query: str, filters: Dict = None, limit: int = 50) -> List[SearchResult]:
        """Execute search across all indexed data"""
        results = []
        
        # Parse query for special syntax
        # e.g., "sandbox:running gpu:high", "error level:critical"
        parsed_query, query_filters = self._parse_query(query)
        
        # Merge filters
        if filters:
            query_filters.update(filters)
        
        # Search each indexer
        for type_name, indexer in self.indexers.items():
            if query_filters.get('type') and query_filters['type'] != type_name:
                continue
            
            try:
                type_results = indexer(parsed_query, query_filters, limit)
                results.extend(type_results)
            except Exception as e:
                logging.error(f"Search error in {type_name}: {e}")
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance, reverse=True)
        
        # Log search for analytics
        self.search_history.append({
            'query': query,
            'filters': filters,
            'results_count': len(results),
            'timestamp': datetime.now()
        })
        
        return results[:limit]
    
    def _parse_query(self, query: str) -> tuple:
        """Parse query for filters and search terms"""
        filters = {}
        
        # Extract type: filters
        type_match = re.search(r'type:(\w+)', query)
        if type_match:
            filters['type'] = type_match.group(1)
            query = query.replace(type_match.group(0), '')
        
        # Extract date: filters
        date_match = re.search(r'date:(\d{4}-\d{2}-\d{2})', query)
        if date_match:
            filters['date'] = date_match.group(1)
            query = query.replace(date_match.group(0), '')
        
        # Extract status: filters
        status_match = re.search(r'status:(\w+)', query)
        if status_match:
            filters['status'] = status_match.group(1)
            query = query.replace(status_match.group(0), '')
        
        return query.strip(), filters
    
    def get_search_suggestions(self, partial: str) -> List[str]:
        """Get search suggestions based on partial input"""
        suggestions = []
        
        # Common search patterns
        patterns = [
            "sandbox:",
            "log level:error",
            "request status:pending",
            "policy:",
            "gpu utilization:high",
            "date:today",
            "agent:",
        ]
        
        for pattern in patterns:
            if pattern.startswith(partial.lower()):
                suggestions.append(pattern)
        
        return suggestions[:10]

# Usage in components
def render_search_bar(search_engine: SearchEngine):
    """Render unified search bar"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "🔍 Search across sandboxes, logs, policies...",
            placeholder="Try: 'sandbox:running error' or 'gpu:high'",
            key="global_search"
        )
    
    with col2:
        st.selectbox(
            "Filter",
            ["All", "Sandboxes", "Logs", "Policies", "Requests"],
            key="search_filter"
        )
    
    if query:
        results = search_engine.search(
            query,
            filters={'type': st.session_state.get('search_filter', 'All').lower()}
        )
        
        st.write(f"Found {len(results)} results")
        
        for result in results:
            with st.container():
                col1, col2 = st.columns([0.8, 0.2])
                
                with col1:
                    st.write(f"**{result.title}**")
                    st.caption(f"{result.snippet}")
                
                with col2:
                    st.badge(result.type)
                    st.caption(f"Score: {result.relevance:.2f}")
```

---

### 3.3 Dashboard Customization

**Current Gap**: Fixed dashboard layout, users can't customize.

**Recommendation**: Widget-based customizable dashboard

```python
# components/customizable_dashboard.py
import streamlit as st
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class WidgetConfig:
    id: str
    type: str
    title: str
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any]
    refresh_interval: int = 5

class DashboardLayout:
    """Customizable dashboard layout manager"""
    
    def __init__(self, user_id: str, data_store: DataStore):
        self.user_id = user_id
        self.store = data_store
        self.widgets: List[WidgetConfig] = []
        self._load_layout()
    
    def _load_layout(self):
        """Load user's saved layout"""
        layout_data = self.store.get(f"layout:{self.user_id}")
        if layout_data:
            self.widgets = [WidgetConfig(**w) for w in layout_data]
        else:
            # Default layout
            self.widgets = self._get_default_layout()
    
    def _get_default_layout(self) -> List[WidgetConfig]:
        """Get default widget layout"""
        return [
            WidgetConfig(
                id="sandbox_summary",
                type="sandbox_summary",
                title="Sandbox Summary",
                position={'x': 0, 'y': 0, 'width': 6, 'height': 2},
                config={}
            ),
            WidgetConfig(
                id="gpu_metrics",
                type="gpu_metrics",
                title="GPU Metrics",
                position={'x': 6, 'y': 0, 'width': 6, 'height': 2},
                config={'show_all_gpus': True}
            ),
            WidgetConfig(
                id="recent_logs",
                type="log_viewer",
                title="Recent Logs",
                position={'x': 0, 'y': 2, 'width': 12, 'height': 3},
                config={'lines': 100, 'level': 'INFO'}
            ),
        ]
    
    def save_layout(self):
        """Save current layout"""
        layout_data = [asdict(w) for w in self.widgets]
        self.store.set(f"layout:{self.user_id}", layout_data, persistent=True)
    
    def add_widget(self, widget: WidgetConfig):
        """Add new widget to layout"""
        self.widgets.append(widget)
        self.save_layout()
    
    def remove_widget(self, widget_id: str):
        """Remove widget from layout"""
        self.widgets = [w for w in self.widgets if w.id != widget_id]
        self.save_layout()
    
    def update_widget_position(self, widget_id: str, position: Dict):
        """Update widget position"""
        for widget in self.widgets:
            if widget.id == widget_id:
                widget.position = position
                break
        self.save_layout()
    
    def render(self):
        """Render dashboard with all widgets"""
        # Check if in edit mode
        edit_mode = st.session_state.get('dashboard_edit_mode', False)
        
        if edit_mode:
            self._render_edit_mode()
        else:
            self._render_view_mode()
    
    def _render_view_mode(self):
        """Render dashboard in view mode"""
        # Group widgets by row
        rows = {}
        for widget in self.widgets:
            y = widget.position['y']
            if y not in rows:
                rows[y] = []
            rows[y].append(widget)
        
        # Render each row
        for y in sorted(rows.keys()):
            widgets = rows[y]
            cols = st.columns(12)  # 12-column grid
            
            for widget in widgets:
                width = widget.position['width']
                col_idx = widget.position['x']
                
                with cols[col_idx:col_idx + width]:
                    self._render_widget(widget)
    
    def _render_widget(self, widget: WidgetConfig):
        """Render individual widget"""
        with st.container():
            st.subheader(widget.title)
            
            # Widget-specific rendering
            if widget.type == "sandbox_summary":
                self._render_sandbox_summary(widget.config)
            elif widget.type == "gpu_metrics":
                self._render_gpu_metrics(widget.config)
            elif widget.type == "log_viewer":
                self._render_log_viewer(widget.config)
            # ... more widget types
    
    def _render_edit_mode(self):
        """Render dashboard in edit mode"""
        st.info("🛠️ Edit Mode: Drag widgets to reposition, click × to remove")
        
        for widget in self.widgets:
            col1, col2 = st.columns([0.9, 0.1])
            
            with col1:
                st.write(f"**{widget.title}** ({widget.type})")
                st.caption(f"Position: {widget.position}")
            
            with col2:
                if st.button("×", key=f"remove_{widget.id}"):
                    self.remove_widget(widget.id)
                    st.rerun()
        
        # Add new widget
        st.divider()
        st.write("**Add Widget**")
        
        widget_types = [
            "sandbox_summary",
            "gpu_metrics",
            "log_viewer",
            "request_queue",
            "reputation_chart",
            "system_health"
        ]
        
        new_type = st.selectbox("Widget Type", widget_types)
        new_title = st.text_input("Title", value=f"New {new_type.replace('_', ' ').title()}")
        
        if st.button("Add Widget"):
            new_widget = WidgetConfig(
                id=f"widget_{len(self.widgets)}",
                type=new_type,
                title=new_title,
                position={'x': 0, 'y': len(self.widgets), 'width': 6, 'height': 2},
                config={}
            )
            self.add_widget(new_widget)
            st.rerun()
```

---

### 3.4 Notification System

**Current Gap**: No notification system for alerts, approvals, or status changes.

**Recommendation**: Multi-channel notification system

```python
# services/notification_service.py
from dataclasses import dataclass
from typing import List, Dict, Callable
from datetime import datetime
from enum import Enum

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    UI = "ui"           # In-dashboard
    EMAIL = "email"     # Email notification
    SLACK = "slack"     # Slack webhook
    DESKTOP = "desktop" # OS notification

@dataclass
class Notification:
    id: str
    title: str
    message: str
    priority: NotificationPriority
    channel: NotificationChannel
    timestamp: datetime
    read: bool = False
    action_url: str = None
    metadata: Dict = None

class NotificationService:
    """Multi-channel notification system"""
    
    def __init__(self, data_store: DataStore):
        self.store = data_store
        self.handlers: Dict[NotificationChannel, Callable] = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """Register channel handlers"""
        self.handlers[NotificationChannel.UI] = self._send_ui_notification
        self.handlers[NotificationChannel.EMAIL] = self._send_email
        self.handlers[NotificationChannel.SLACK] = self._send_slack
        self.handlers[NotificationChannel.DESKTOP] = self._send_desktop
    
    def send(self, notification: Notification):
        """Send notification through specified channel"""
        # Store notification
        self._store_notification(notification)
        
        # Send through channel
        handler = self.handlers.get(notification.channel)
        if handler:
            try:
                handler(notification)
            except Exception as e:
                logging.error(f"Failed to send notification: {e}")
    
    def _store_notification(self, notification: Notification):
        """Store notification for history"""
        notifications = self.store.get("notifications") or []
        notifications.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority.value,
            'channel': notification.channel.value,
            'timestamp': notification.timestamp.isoformat(),
            'read': notification.read,
            'action_url': notification.action_url,
            'metadata': notification.metadata
        })
        
        # Keep only last 1000 notifications
        notifications = notifications[-1000:]
        self.store.set("notifications", notifications, persistent=True)
    
    def get_unread(self, limit: int = 50) -> List[Notification]:
        """Get unread notifications"""
        notifications = self.store.get("notifications") or []
        unread = [n for n in notifications if not n.get('read')]
        return unread[:limit]
    
    def mark_read(self, notification_id: str):
        """Mark notification as read"""
        notifications = self.store.get("notifications") or []
        for n in notifications:
            if n['id'] == notification_id:
                n['read'] = True
                break
        self.store.set("notifications", notifications, persistent=True)
    
    def _send_ui_notification(self, notification: Notification):
        """Send in-dashboard notification"""
        # Streamlit session state notification
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        st.session_state.notifications.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority.value,
            'timestamp': notification.timestamp
        })
    
    def _send_email(self, notification: Notification):
        """Send email notification"""
        # Requires email configuration
        pass
    
    def _send_slack(self, notification: Notification):
        """Send Slack notification"""
        # Requires Slack webhook URL
        pass
    
    def _send_desktop(self, notification: Notification):
        """Send OS desktop notification"""
        try:
            import plyer
            plyer.notification.notify(
                title=notification.title,
                message=notification.message,
                timeout=10
            )
        except ImportError:
            pass

# Predefined notification templates
class NotificationTemplates:
    """Common notification templates"""
    
    @staticmethod
    def sandbox_started(sandbox_name: str) -> Notification:
        return Notification(
            id=f"sandbox_start_{datetime.now().timestamp()}",
            title="Sandbox Started",
            message=f"Sandbox '{sandbox_name}' is now running",
            priority=NotificationPriority.LOW,
            channel=NotificationChannel.UI,
            timestamp=datetime.now(),
            action_url=f"/sandboxes/{sandbox_name}"
        )
    
    @staticmethod
    def high_risk_request(request_id: str, risk_score: int) -> Notification:
        return Notification(
            id=f"risk_request_{request_id}",
            title="High Risk Request Detected",
            message=f"Request {request_id} has risk score {risk_score}/100 and requires review",
            priority=NotificationPriority.HIGH,
            channel=NotificationChannel.UI,
            timestamp=datetime.now(),
            action_url=f"/requests/{request_id}"
        )
    
    @staticmethod
    def gpu_overheating(gpu_name: str, temp: float) -> Notification:
        return Notification(
            id=f"gpu_temp_{datetime.now().timestamp()}",
            title="GPU Temperature Alert",
            message=f"{gpu_name} temperature is {temp}°C (threshold: 85°C)",
            priority=NotificationPriority.CRITICAL,
            channel=NotificationChannel.UI,
            timestamp=datetime.now()
        )
```

---

### 3.5 Multi-Instance Management

**Current Gap**: Dashboard designed for single NemoClaw installation only.

**Recommendation**: Add multi-instance support for both Personal and Enterprise modes

```python
# services/instance_manager.py
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
from pathlib import Path
import yaml

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

# UI Integration
def render_instance_selector(instance_manager: InstanceManager):
    """Render instance selector in sidebar"""
    instances = instance_manager.list_instances()
    
    if len(instances) == 1:
        st.sidebar.write(f"📍 {instances[0].name}")
        return instances[0].id
    
    instance_options = {f"{i.name} ({i.status.value})": i.id for i in instances}
    selected_label = st.sidebar.selectbox("📍 Select Instance", options=list(instance_options.keys()))
    return instance_options[selected_label]
```

**Use Cases**:
- Personal: Local + remote GPU server
- Enterprise: Multi-region fleet management
- Cross-instance policy deployment
- Global search across all sandboxes
- Aggregated compliance reporting

**Implementation**: Phase 4 (Enterprise Scale)

---

## 4. Summary of Recommendations

### Stability (Must Have)

| Improvement | Impact | Effort | Phase |
|-------------|--------|--------|-------|
| Circuit Breaker Pattern | High | Medium | Sprint 2 |
| Health Check System | High | Low | Sprint 1 |
| Graceful Degradation | High | Medium | Sprint 2 |
| Hybrid Data Store | Medium | Medium | Sprint 3 |
| Retry Logic | High | Low | Sprint 1 |

### Functionality (Should Have)

| Improvement | Impact | Effort | Phase |
|-------------|--------|--------|-------|
| Plugin System | High | High | Phase 2 |
| Workflow Engine | High | High | Phase 2 |
| Schema Validation | Medium | Low | Sprint 1 |
| Backup/Restore | High | Medium | Sprint 3 |
| Import/Export | Medium | Low | Sprint 2 |

### Usefulness (Could Have)

| Improvement | Impact | Effort | Phase |
|-------------|--------|--------|-------|
| Command Palette | High | Medium | Sprint 2 |
| Smart Search | High | Medium | Phase 2 |
| Customizable Dashboard | Medium | High | Phase 2 |
| Notification System | High | Medium | Sprint 3 |
| Keyboard Shortcuts | Medium | Low | Sprint 2 |

### Priority Implementation Order

1. **Sprint 1**: Health checks, schema validation, retry logic
2. **Sprint 2**: Circuit breaker, command palette, graceful degradation
3. **Sprint 3**: Data store, notification system, backup/restore
4. **Phase 2**: Plugin system, workflow engine, smart search

---

*Document Version: 0.1.0*
*Last Updated: March 26, 2026*
