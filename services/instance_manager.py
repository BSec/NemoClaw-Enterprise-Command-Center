"""Instance Manager for multi-NemoClaw support.

Manages multiple NemoClaw installations from a single dashboard.
Supports Local, SSH, API, and Agent connection types.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
from datetime import datetime
import yaml
import subprocess

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
    environment: str  # dev, staging, production, default
    connection_config: Dict[str, Any]
    status: InstanceStatus = InstanceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class InstanceManager:
    """Manage multiple NemoClaw instances."""
    
    def __init__(self, config_path: str = "~/.nemoclaw/instances.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.instances: Dict[str, NemoClawInstance] = {}
        self._load_instances()
    
    def _load_instances(self):
        """Load instances from configuration file."""
        if not self.config_path.exists():
            # No instances configured yet
            return
        
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f) or {}
            
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
        except Exception as e:
            print(f"Error loading instances: {e}")
    
    def _save_instances(self):
        """Save instances to configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'instances': [
                {
                    'id': i.id,
                    'name': i.name,
                    'type': i.type.value,
                    'environment': i.environment,
                    'connection': i.connection_config,
                    'metadata': i.metadata
                }
                for i in self.instances.values()
            ]
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def add_instance(self, instance: NemoClawInstance):
        """Add a new instance."""
        self.instances[instance.id] = instance
        self._save_instances()
    
    def remove_instance(self, instance_id: str):
        """Remove an instance."""
        if instance_id in self.instances:
            del self.instances[instance_id]
            self._save_instances()
    
    def get_instance(self, instance_id: str) -> Optional[NemoClawInstance]:
        """Get instance by ID."""
        return self.instances.get(instance_id)
    
    def list_instances(self, environment: Optional[str] = None) -> List[NemoClawInstance]:
        """List all instances, optionally filtered by environment."""
        instances = list(self.instances.values())
        if environment:
            instances = [i for i in instances if i.environment == environment]
        return instances
    
    def check_health(self, instance_id: str) -> InstanceStatus:
        """Check instance health."""
        instance = self.get_instance(instance_id)
        if not instance:
            return InstanceStatus.UNKNOWN
        
        try:
            if instance.type == InstanceType.LOCAL:
                return self._check_local_health(instance)
            elif instance.type == InstanceType.SSH:
                return self._check_ssh_health(instance)
            elif instance.type == InstanceType.API:
                return self._check_api_health(instance)
            else:
                return InstanceStatus.UNKNOWN
        except Exception as e:
            instance.status = InstanceStatus.OFFLINE
            return InstanceStatus.OFFLINE
    
    def _check_local_health(self, instance: NemoClawInstance) -> InstanceStatus:
        """Check health of local instance."""
        path = instance.connection_config.get('path', 'openshell')
        
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                instance.status = InstanceStatus.ONLINE
                instance.last_seen = datetime.now()
                return InstanceStatus.ONLINE
            else:
                instance.status = InstanceStatus.DEGRADED
                return InstanceStatus.DEGRADED
        except Exception:
            instance.status = InstanceStatus.OFFLINE
            return InstanceStatus.OFFLINE
    
    def _check_ssh_health(self, instance: NemoClawInstance) -> InstanceStatus:
        """Check health of SSH-connected instance."""
        # Placeholder - requires paramiko for actual implementation
        instance.status = InstanceStatus.UNKNOWN
        return InstanceStatus.UNKNOWN
    
    def _check_api_health(self, instance: NemoClawInstance) -> InstanceStatus:
        """Check health of API-connected instance."""
        # Placeholder - requires requests for actual implementation
        instance.status = InstanceStatus.UNKNOWN
        return InstanceStatus.UNKNOWN
    
    def execute_on_instance(self, instance_id: str, command: str, *args) -> Any:
        """Execute command on specific instance."""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        if instance.type == InstanceType.LOCAL:
            return self._execute_local(instance, command, *args)
        elif instance.type == InstanceType.SSH:
            return self._execute_ssh(instance, command, *args)
        elif instance.type == InstanceType.API:
            return self._execute_api(instance, command, *args)
        else:
            raise ValueError(f"Unsupported instance type: {instance.type}")
    
    def _execute_local(self, instance: NemoClawInstance, command: str, *args) -> Dict:
        """Execute command on local instance."""
        path = instance.connection_config.get('path', 'openshell')
        cmd = [path, command] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Command timed out', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _execute_ssh(self, instance: NemoClawInstance, command: str, *args) -> Dict:
        """Execute command via SSH."""
        # Placeholder implementation
        return {'error': 'SSH not yet implemented', 'success': False}
    
    def _execute_api(self, instance: NemoClawInstance, command: str, *args) -> Dict:
        """Execute command via API."""
        # Placeholder implementation
        return {'error': 'API not yet implemented', 'success': False}

def create_default_config():
    """Create default instance configuration."""
    config_path = Path("~/.nemoclaw/instances.yaml").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = {
        'instances': [
            {
                'id': 'local',
                'name': 'Local Workstation',
                'type': 'local',
                'environment': 'default',
                'connection': {
                    'path': 'openshell'
                },
                'default': True
            }
        ]
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    return config_path
