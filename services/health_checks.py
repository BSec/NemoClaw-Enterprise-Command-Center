"""Built-in health checks for NemoClaw Gateway.

Pre-configured health checks for system components.
"""

import os
import json
import hashlib
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
import streamlit as st

from services.health_monitor import (
    SecureHealthMonitor, HealthCheckResult, CheckType,
    HealthStatus, SeverityLevel, health_monitor
)
from services.instance_manager import InstanceManager
from services.gpu_monitor import GpuMonitor
from utils.config import load_config

def check_service_availability() -> HealthCheckResult:
    """Check core service availability."""
    start_time = datetime.utcnow()
    
    try:
        # Check if we can load config
        config = load_config()
        
        # Check Streamlit session state
        session_active = hasattr(st, 'session_state')
        
        # Check instance manager
        instance_manager = InstanceManager()
        instances = instance_manager.list_instances()
        
        status = HealthStatus.HEALTHY
        message = "All core services available"
        severity = SeverityLevel.INFO
        
        if not instances:
            status = HealthStatus.DEGRADED
            message = "No instances configured"
            severity = SeverityLevel.LOW
        
        return HealthCheckResult(
            check_id="service_availability",
            check_type=CheckType.SERVICE_AVAILABILITY,
            status=status,
            timestamp=start_time,
            duration_ms=0,
            message=message,
            details={
                "config_loaded": True,
                "session_active": session_active,
                "instances_configured": len(instances),
                "instance_names": [i.name for i in instances]
            },
            severity=severity,
            remediation_suggested="Configure at least one NemoClaw instance" if not instances else None
        )
    except Exception as e:
        return HealthCheckResult(
            check_id="service_availability",
            check_type=CheckType.SERVICE_AVAILABILITY,
            status=HealthStatus.CRITICAL,
            timestamp=start_time,
            duration_ms=0,
            message=f"Core service failure: {str(e)}",
            details={"error": str(e)},
            severity=SeverityLevel.CRITICAL,
            remediation_suggested="Check configuration files and restart application"
        )

def check_configuration_integrity() -> HealthCheckResult:
    """Verify configuration integrity."""
    start_time = datetime.utcnow()
    
    try:
        config = load_config()
        issues = []
        
        # Check required files exist
        required_files = [
            "config.yaml",
            "components/__init__.py",
            "services/__init__.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            issues.append(f"Missing files: {', '.join(missing_files)}")
        
        # Check config structure
        if not hasattr(config, 'theme'):
            issues.append("Invalid config structure")
        
        # Calculate config file hash for integrity
        config_hash = ""
        try:
            with open("config.yaml", "rb") as f:
                config_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            pass
        
        status = HealthStatus.HEALTHY if not issues else HealthStatus.DEGRADED
        severity = SeverityLevel.INFO if not issues else SeverityLevel.MEDIUM
        
        return HealthCheckResult(
            check_id="configuration_integrity",
            check_type=CheckType.CONFIGURATION_INTEGRITY,
            status=status,
            timestamp=start_time,
            duration_ms=0,
            message="Configuration valid" if not issues else f"Configuration issues: {', '.join(issues)}",
            details={
                "config_hash": config_hash,
                "missing_files": missing_files,
                "issues": issues
            },
            severity=severity,
            remediation_suggested="Restore missing configuration files" if missing_files else None
        )
    except Exception as e:
        return HealthCheckResult(
            check_id="configuration_integrity",
            check_type=CheckType.CONFIGURATION_INTEGRITY,
            status=HealthStatus.CRITICAL,
            timestamp=start_time,
            duration_ms=0,
            message=f"Configuration check failed: {str(e)}",
            details={"error": str(e)},
            severity=SeverityLevel.CRITICAL,
            remediation_suggested="Verify config.yaml exists and is valid YAML"
        )

def check_access_control() -> HealthCheckResult:
    """Check access control enforcement."""
    start_time = datetime.utcnow()
    
    try:
        from services.auth_service import auth_manager, UserRole
        
        # Check authentication system
        users = auth_manager.get_users()
        admin_users = [u for u in users if u.role == UserRole.ADMIN]
        mfa_enabled_count = sum(1 for u in users if u.mfa_enabled)
        
        issues = []
        if not admin_users:
            issues.append("No admin users configured")
        
        mfa_percentage = (mfa_enabled_count / len(users) * 100) if users else 0
        
        status = HealthStatus.HEALTHY
        if issues:
            status = HealthStatus.DEGRADED
        
        return HealthCheckResult(
            check_id="access_control",
            check_type=CheckType.ACCESS_CONTROL,
            status=status,
            timestamp=start_time,
            duration_ms=0,
            message=f"Access control active - {len(users)} users, {mfa_percentage:.0f}% MFA",
            details={
                "total_users": len(users),
                "admin_users": len(admin_users),
                "mfa_enabled": mfa_enabled_count,
                "mfa_percentage": mfa_percentage,
                "issues": issues
            },
            severity=SeverityLevel.LOW if issues else SeverityLevel.INFO,
            remediation_suggested="Configure at least one admin user" if not admin_users else None
        )
    except Exception as e:
        return HealthCheckResult(
            check_id="access_control",
            check_type=CheckType.ACCESS_CONTROL,
            status=HealthStatus.UNKNOWN,
            timestamp=start_time,
            duration_ms=0,
            message=f"Access control check failed: {str(e)}",
            details={"error": str(e)},
            severity=SeverityLevel.MEDIUM,
            remediation_suggested="Verify authentication service is functioning"
        )

def check_dependency_health() -> HealthCheckResult:
    """Check critical dependencies."""
    start_time = datetime.utcnow()
    
    dependencies = {
        "streamlit": False,
        "plotly": False,
        "pandas": False,
        "numpy": False,
        "pynvml": False
    }
    
    try:
        import streamlit
        dependencies["streamlit"] = True
    except:
        pass
    
    try:
        import plotly
        dependencies["plotly"] = True
    except:
        pass
    
    try:
        import pandas
        dependencies["pandas"] = True
    except:
        pass
    
    try:
        import numpy
        dependencies["numpy"] = True
    except:
        pass
    
    try:
        import pynvml
        dependencies["pynvml"] = True
    except:
        pass
    
    failed = [k for k, v in dependencies.items() if not v]
    
    if failed:
        status = HealthStatus.CRITICAL
        message = f"Missing critical dependencies: {', '.join(failed)}"
        severity = SeverityLevel.CRITICAL
    else:
        status = HealthStatus.HEALTHY
        message = "All critical dependencies available"
        severity = SeverityLevel.INFO
    
    return HealthCheckResult(
        check_id="dependency_health",
        check_type=CheckType.DEPENDENCY_HEALTH,
        status=status,
        timestamp=start_time,
        duration_ms=0,
        message=message,
        details={
            "dependencies": dependencies,
            "failed": failed
        },
        severity=severity,
        remediation_suggested=f"Install missing packages: pip install {' '.join(failed)}" if failed else None
    )

def check_data_flow() -> HealthCheckResult:
    """Check data flow correctness."""
    start_time = datetime.utcnow()
    
    try:
        # Test data serialization
        test_data = {"test": "value", "number": 42, "nested": {"key": "val"}}
        serialized = json.dumps(test_data)
        deserialized = json.loads(serialized)
        
        if deserialized == test_data:
            return HealthCheckResult(
                check_id="data_flow",
                check_type=CheckType.DATA_FLOW,
                status=HealthStatus.HEALTHY,
                timestamp=start_time,
                duration_ms=0,
                message="Data serialization/deserialization working correctly",
                details={"serialization_test": "passed"},
                severity=SeverityLevel.INFO
            )
        else:
            return HealthCheckResult(
                check_id="data_flow",
                check_type=CheckType.DATA_FLOW,
                status=HealthStatus.DEGRADED,
                timestamp=start_time,
                duration_ms=0,
                message="Data serialization mismatch detected",
                details={},
                severity=SeverityLevel.HIGH,
                remediation_suggested="Check JSON encoding settings"
            )
    except Exception as e:
        return HealthCheckResult(
            check_id="data_flow",
            check_type=CheckType.DATA_FLOW,
            status=HealthStatus.CRITICAL,
            timestamp=start_time,
            duration_ms=0,
            message=f"Data flow check failed: {str(e)}",
            details={"error": str(e)},
            severity=SeverityLevel.CRITICAL,
            remediation_suggested="Verify Python JSON library is functional"
        )

def check_performance() -> HealthCheckResult:
    """Check system performance."""
    start_time = datetime.utcnow()
    
    try:
        import time
        
        # Simple timing test
        begin = time.time()
        _ = [i ** 2 for i in range(10000)]
        elapsed = (time.time() - begin) * 1000
        
        # Check session state size
        session_size = len(str(st.session_state)) if hasattr(st, 'session_state') else 0
        
        status = HealthStatus.HEALTHY
        message = f"Performance nominal - operation took {elapsed:.2f}ms"
        
        if elapsed > 100:  # > 100ms for simple operation
            status = HealthStatus.DEGRADED
            message = f"Performance degraded - operation took {elapsed:.2f}ms"
        
        return HealthCheckResult(
            check_id="performance",
            check_type=CheckType.PERFORMANCE,
            status=status,
            timestamp=start_time,
            duration_ms=elapsed,
            message=message,
            details={
                "operation_time_ms": elapsed,
                "session_state_size": session_size
            },
            severity=SeverityLevel.LOW if status == HealthStatus.DEGRADED else SeverityLevel.INFO,
            remediation_suggested="Clear session state or restart application" if session_size > 10000 else None
        )
    except Exception as e:
        return HealthCheckResult(
            check_id="performance",
            check_type=CheckType.PERFORMANCE,
            status=HealthStatus.UNKNOWN,
            timestamp=start_time,
            duration_ms=0,
            message=f"Performance check failed: {str(e)}",
            details={"error": str(e)},
            severity=SeverityLevel.MEDIUM
        )

def check_security_posture() -> HealthCheckResult:
    """Check overall security posture."""
    start_time = datetime.utcnow()
    
    checks = {
        "secure_random": False,
        "hash_available": False,
        "no_debug_mode": True
    }
    
    try:
        import secrets
        _ = secrets.token_hex(16)
        checks["secure_random"] = True
    except:
        pass
    
    try:
        hashlib.sha256(b"test")
        checks["hash_available"] = True
    except:
        pass
    
    # Check for debug flags
    debug_enabled = os.environ.get('DEBUG', '').lower() in ('true', '1', 'yes')
    checks["no_debug_mode"] = not debug_enabled
    
    failed = [k for k, v in checks.items() if not v]
    
    if failed:
        status = HealthStatus.DEGRADED
        message = f"Security posture concerns: {', '.join(failed)}"
        severity = SeverityLevel.MEDIUM
    else:
        status = HealthStatus.HEALTHY
        message = "Security posture nominal"
        severity = SeverityLevel.INFO
    
    return HealthCheckResult(
        check_id="security_posture",
        check_type=CheckType.SECURITY_POSTURE,
        status=status,
        timestamp=start_time,
        duration_ms=0,
        message=message,
        details=checks,
        severity=severity,
        remediation_suggested="Disable debug mode in production" if debug_enabled else None
    )

def register_all_checks(monitor: SecureHealthMonitor):
    """Register all built-in health checks."""
    checks = [
        ("service_availability", CheckType.SERVICE_AVAILABILITY, check_service_availability, True),
        ("configuration_integrity", CheckType.CONFIGURATION_INTEGRITY, check_configuration_integrity, True),
        ("access_control", CheckType.ACCESS_CONTROL, check_access_control, False),
        ("dependency_health", CheckType.DEPENDENCY_HEALTH, check_dependency_health, True),
        ("data_flow", CheckType.DATA_FLOW, check_data_flow, False),
        ("performance", CheckType.PERFORMANCE, check_performance, False),
        ("security_posture", CheckType.SECURITY_POSTURE, check_security_posture, False),
    ]
    
    for check_id, check_type, func, critical in checks:
        monitor.register_check(
            check_id=check_id,
            check_type=check_type,
            check_func=func,
            critical=critical
        )

# Register all checks on the global monitor
register_all_checks(health_monitor)
