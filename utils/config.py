"""Configuration management for NemoClaw Gateway Dashboard."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import yaml

@dataclass
class ThemeConfig:
    primary_color: str = "#76B900"
    background_color: str = "#0D1117"
    secondary_background: str = "#161B22"
    text_color: str = "#E6EDF3"
    font: str = "sans serif"

@dataclass
class DashboardConfig:
    version: str = "0.2.0"
    mode: str = "personal"  # personal or enterprise
    refresh_interval: int = 5
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    local_db_path: Path = field(default_factory=lambda: Path("~/.nemoclaw/dashboard.db"))
    instances_config_path: Path = field(default_factory=lambda: Path("~/.nemoclaw/instances.yaml"))
    features: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        # Expand paths
        self.local_db_path = self.local_db_path.expanduser()
        self.instances_config_path = self.instances_config_path.expanduser()
        
        # Set default features
        default_features = {
            'gpu_monitoring': True,
            'log_aggregation': True,
            'policy_management': True,
            'multi_instance': True,
        }
        default_features.update(self.features)
        self.features = default_features

def load_config(config_path: str = "~/.nemoclaw/config.yaml") -> DashboardConfig:
    """Load dashboard configuration from YAML file."""
    config_file = Path(config_path).expanduser()
    
    # Create default config if not exists
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config = DashboardConfig()
        save_config(config, config_path)
        return config
    
    # Load existing config
    try:
        with open(config_file) as f:
            data = yaml.safe_load(f) or {}
        
        # Parse theme config
        theme_data = data.get('theme', {})
        theme = ThemeConfig(**theme_data)
        
        # Create config object
        config = DashboardConfig(
            version=data.get('version', '0.2.0'),
            mode=data.get('mode', 'personal'),
            refresh_interval=data.get('refresh_interval', 5),
            theme=theme,
            features=data.get('features', {})
        )
        
        return config
    except Exception as e:
        print(f"Error loading config: {e}. Using defaults.")
        return DashboardConfig()

def save_config(config: DashboardConfig, config_path: str = "~/.nemoclaw/config.yaml"):
    """Save dashboard configuration to YAML file."""
    config_file = Path(config_path).expanduser()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'version': config.version,
        'mode': config.mode,
        'refresh_interval': config.refresh_interval,
        'theme': {
            'primary_color': config.theme.primary_color,
            'background_color': config.theme.background_color,
            'secondary_background': config.theme.secondary_background,
            'text_color': config.theme.text_color,
            'font': config.theme.font,
        },
        'features': config.features,
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
