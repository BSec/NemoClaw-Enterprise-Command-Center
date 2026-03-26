"""Error handling and retry utilities for the NemoClaw Gateway Dashboard.

Provides:
- Circuit breaker pattern for external calls
- Retry decorators with exponential backoff
- Error boundary components
- Logging and monitoring
"""

import logging
import time
from typing import Callable, Any, TypeVar, Optional, List
from functools import wraps
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
T = TypeVar('T')

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    exceptions: tuple = (Exception,)
    on_retry: Optional[Callable[[Exception, int], None]] = None
    on_final_failure: Optional[Callable[[Exception], None]] = None

class CircuitBreaker:
    """Circuit breaker pattern implementation.
    
    Prevents cascading failures when external services are unavailable.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self._state == CircuitState.CLOSED:
            return True
        
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed > self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit {self.name} transitioning to HALF_OPEN")
                    return True
            return False
        
        return True  # HALF_OPEN allows single test
    
    def record_success(self):
        """Record successful execution."""
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info(f"Circuit {self.name} closed after successful recovery")
        
        self._failure_count = 0
        self._last_failure_time = None
    
    def record_failure(self):
        """Record failed execution."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        if self._state == CircuitState.HALF_OPEN:
            # Recovery test failed
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name} opened after failed recovery test")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit {self.name} opened after {self._failure_count} failures")
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if not self.can_execute():
            raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator interface."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                name=name
            )
        return self._breakers[name]
    
    def get_status(self) -> dict:
        """Get status of all circuit breakers."""
        return {
            name: {
                "state": cb.state.value,
                "failure_count": cb._failure_count,
                "last_failure": cb._last_failure_time.isoformat() if cb._last_failure_time else None
            }
            for name, cb in self._breakers.items()
        }

# Global registry
circuit_breakers = CircuitBreakerRegistry()

def retry_with_backoff(config: Optional[RetryConfig] = None):
    """Decorator for retry logic with exponential backoff.
    
    Args:
        config: Retry configuration. Uses defaults if not provided.
    """
    cfg = config or RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except cfg.exceptions as e:
                    last_exception = e
                    
                    if attempt < cfg.max_retries:
                        # Calculate delay with exponential backoff
                        delay = min(
                            cfg.base_delay * (cfg.exponential_base ** attempt),
                            cfg.max_delay
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{cfg.max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        if cfg.on_retry:
                            cfg.on_retry(e, attempt + 1)
                        
                        time.sleep(delay)
                    else:
                        logger.error(f"All {cfg.max_retries + 1} attempts failed for {func.__name__}")
                        if cfg.on_final_failure:
                            cfg.on_final_failure(e)
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator

def safe_execute(
    func: Callable[..., T],
    default: Optional[T] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    log_errors: bool = True
) -> Optional[T]:
    """Execute function safely with error handling.
    
    Returns default value instead of raising exceptions.
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        if on_error:
            on_error(e)
        return default

def error_boundary(
    error_message: str = "An error occurred",
    show_details: bool = True
):
    """Decorator for wrapping Streamlit components with error boundaries.
    
    Catches exceptions and displays user-friendly error messages.
    """
    import streamlit as st
    
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                
                with st.container():
                    st.error(f"⚠️ {error_message}")
                    
                    if show_details:
                        with st.expander("Error Details"):
                            st.code(str(e))
                            import traceback
                            st.code(traceback.format_exc())
                
                return None
        
        return wrapper
    return decorator

class HealthCheck:
    """Health check system for monitoring component status."""
    
    def __init__(self):
        self.checks: dict[str, Callable[[], tuple[bool, str]]] = {}
    
    def register(self, name: str, check_func: Callable[[], tuple[bool, str]]):
        """Register a health check."""
        self.checks[name] = check_func
    
    def run_all(self) -> dict[str, dict]:
        """Run all health checks and return results."""
        results = {}
        
        for name, check in self.checks.items():
            try:
                healthy, message = check()
                results[name] = {
                    "healthy": healthy,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "message": f"Health check failed: {e}",
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        results = self.run_all()
        return all(r["healthy"] for r in results.values())

# Convenience retry configurations
RETRY_CONFIG_NETWORK = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    exceptions=(ConnectionError, TimeoutError, OSError)
)

RETRY_CONFIG_CLI = RetryConfig(
    max_retries=2,
    base_delay=0.5,
    exceptions=(subprocess.SubprocessError, OSError)
)

# Example usage patterns for documentation
EXAMPLE_USAGE = """
Usage Examples:

1. Circuit Breaker on function:
    @circuit_breakers.get_or_create("openshell")
    def call_openshell():
        return subprocess.run(["openshell", "list"])

2. Retry with backoff:
    @retry_with_backoff(RETRY_CONFIG_NETWORK)
    def fetch_remote_data():
        return requests.get("https://api.example.com/data")

3. Safe execution with default:
    result = safe_execute(
        lambda: openshell.list_sandboxes(),
        default=[],
        on_error=lambda e: st.error(f"Failed to load sandboxes: {e}")
    )

4. Error boundary for UI components:
    @error_boundary("Failed to render sandbox list")
    def render_sandbox_list():
        for sandbox in sandboxes:
            render_sandbox_card(sandbox)

5. Health checks:
    health = HealthCheck()
    health.register("openshell", check_openshell_available)
    health.register("gpu", check_gpu_available)
    status = health.run_all()
"""

import subprocess  # For CLI retry config
