"""OpenShell service wrapper for CLI integration."""

import subprocess
import json
from typing import List, Dict, Optional, Any
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OpenShellError(Exception):
    """OpenShell CLI error."""
    pass

class OpenShellService:
    """Service for interacting with OpenShell CLI."""
    
    def __init__(self, instance_manager, instance_id: str):
        self.instance_manager = instance_manager
        self.instance_id = instance_id
    
    def _execute(self, command: str, *args, capture_json: bool = True) -> Any:
        """Execute openshell command on the managed instance."""
        try:
            result = self.instance_manager.execute_on_instance(
                self.instance_id, command, *args
            )
            
            if not result.get('success'):
                error = result.get('stderr') or result.get('error', 'Unknown error')
                raise OpenShellError(f"Command failed: {error}")
            
            if capture_json:
                try:
                    return json.loads(result['stdout'])
                except json.JSONDecodeError:
                    return result['stdout']
            return result['stdout']
            
        except Exception as e:
            logger.error(f"OpenShell command failed: {e}")
            raise OpenShellError(str(e))
    
    def list_sandboxes(self) -> List[Sandbox]:
        """List all sandboxes."""
        try:
            response = self._execute("list", "sandboxes", "--json")
            
            if isinstance(response, dict) and "sandboxes" in response:
                sandboxes = []
                for item in response["sandboxes"]:
                    sandboxes.append(Sandbox(
                        id=item.get("id", "unknown"),
                        name=item.get("name", "Unnamed"),
                        status=item.get("status", "unknown"),
                        agent_type=item.get("agent_type", "unknown"),
                        workspace_path=item.get("workspace_path", ""),
                        created_at=self._parse_datetime(item.get("created_at")),
                        updated_at=self._parse_datetime(item.get("updated_at"))
                    ))
                return sandboxes
            return []
        except Exception as e:
            logger.error(f"Failed to list sandboxes: {e}")
            return []
    
    def get_sandbox_status(self, sandbox_id: str) -> Dict:
        """Get detailed sandbox status."""
        try:
            return self._execute("sandbox", "status", sandbox_id, "--json")
        except OpenShellError as e:
            return {"error": str(e), "id": sandbox_id}
    
    def start_sandbox(self, sandbox_id: str) -> bool:
        """Start a sandbox."""
        try:
            self._execute("sandbox", "start", sandbox_id)
            return True
        except OpenShellError:
            return False
    
    def stop_sandbox(self, sandbox_id: str) -> bool:
        """Stop a sandbox."""
        try:
            self._execute("sandbox", "stop", sandbox_id)
            return True
        except OpenShellError:
            return False
    
    def get_sandbox_logs(self, sandbox_id: str, lines: int = 100) -> str:
        """Get sandbox logs."""
        try:
            return self._execute("logs", sandbox_id, "--lines", str(lines), capture_json=False)
        except OpenShellError as e:
            return f"Error retrieving logs: {e}"
    
    def stream_logs(self, sandbox_id: str):
        """Stream logs from sandbox (generator)."""
        # Note: Real implementation would use subprocess with streaming
        # This is a placeholder
        yield "Log streaming not yet implemented"
    
    def get_gpu_metrics(self) -> Dict:
        """Get GPU telemetry via nvidia-smi."""
        try:
            result = self.instance_manager.execute_on_instance(
                self.instance_id,
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader"
            )
            
            if not result.get('success'):
                return {"error": "Failed to get GPU metrics"}
            
            # Parse CSV output
            lines = result['stdout'].strip().split('\n')
            gpus = []
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    gpus.append({
                        'index': parts[0],
                        'name': parts[1],
                        'utilization': parts[2].replace('%', ''),
                        'memory_used': parts[3],
                        'memory_total': parts[4],
                        'temperature': parts[5]
                    })
            
            return {"gpus": gpus}
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None
