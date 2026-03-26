"""GPU monitoring service using NVML/pynvml."""

from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class GpuMetrics:
    index: int
    name: str
    utilization: float  # 0-100
    memory_used: float  # MB
    memory_total: float  # MB
    temperature: float  # Celsius
    power_draw: Optional[float] = None  # Watts
    power_limit: Optional[float] = None  # Watts

class GpuMonitor:
    """GPU monitoring using NVIDIA NVML."""
    
    def __init__(self, instance_manager, instance_id: str):
        self.instance_manager = instance_manager
        self.instance_id = instance_id
        self.nvml = None
        self._initialized = False
        self._try_init()
    
    def _try_init(self):
        """Try to initialize NVML."""
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
        """Check if GPU monitoring is available."""
        return self._initialized
    
    def get_gpu_count(self) -> int:
        """Get number of GPUs."""
        if not self._initialized:
            return 0
        try:
            return self.nvml.nvmlDeviceGetCount()
        except:
            return 0
    
    def get_metrics(self) -> List[GpuMetrics]:
        """Get metrics for all GPUs."""
        if not self._initialized:
            return []
        
        metrics = []
        try:
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
                    
                    # Power (may not be available on all GPUs)
                    power_draw = None
                    power_limit = None
                    try:
                        power_draw = self.nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                        power_limit = self.nvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
                    except:
                        pass
                    
                    metrics.append(GpuMetrics(
                        index=i,
                        name=name,
                        utilization=util.gpu,
                        memory_used=mem.used / 1024 / 1024,  # Convert to MB
                        memory_total=mem.total / 1024 / 1024,
                        temperature=temp,
                        power_draw=power_draw,
                        power_limit=power_limit
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to get metrics for GPU {i}: {e}")
        except Exception as e:
            logger.error(f"Failed to get GPU metrics: {e}")
        
        return metrics
    
    def __del__(self):
        """Cleanup NVML."""
        if self._initialized and self.nvml:
            try:
                self.nvml.nvmlShutdown()
            except:
                pass
