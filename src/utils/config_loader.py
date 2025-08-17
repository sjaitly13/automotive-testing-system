"""
Configuration loader utility for the infotainment testing system.
Handles loading, validation, and access to system configuration.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class ConfigLoader:
    """Loads and manages configuration from YAML files."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Config file not found: {self.config_path}")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config: {e}")
            self._create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration if file doesn't exist."""
        self.logger.info("Creating default configuration")
        self.config = {
            'platform': {
                'mode': 'hybrid',
                'qnx': {
                    'real_time_constraint': 0.016,
                    'priority_levels': 5,
                    'deterministic_timing': True,
                    'max_response_time': 0.100
                },
                'android': {
                    'app_launch_delay': 0.500,
                    'multitasking_enabled': True,
                    'memory_limit_mb': 2048,
                    'garbage_collection_interval': 5.0
                }
            },
            'performance': {
                'response_time': {
                    'excellent': 0.050,
                    'good': 0.100,
                    'acceptable': 0.200,
                    'poor': 0.500
                },
                'cpu_usage': {
                    'max_percentage': 80.0,
                    'warning_threshold': 60.0
                },
                'memory_usage': {
                    'max_percentage': 85.0,
                    'warning_threshold': 70.0
                },
                'frame_rate': {
                    'min_fps': 30.0,
                    'target_fps': 60.0
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration."""
        return self.config.get('platform', {})
    
    def get_performance_thresholds(self) -> Dict[str, Any]:
        """Get performance threshold configuration."""
        return self.config.get('performance', {})
    
    def get_test_scenarios(self) -> Dict[str, Any]:
        """Get test scenario configuration."""
        return self.config.get('test_scenarios', {})
    
    def get_automation_config(self) -> Dict[str, Any]:
        """Get automation configuration."""
        return self.config.get('automation', {})
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
    
    def validate(self) -> bool:
        """Validate configuration structure and values."""
        required_keys = ['platform', 'performance', 'test_scenarios']
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required config key: {key}")
                return False
        
        # Validate platform mode
        platform_mode = self.get('platform.mode')
        valid_modes = ['qnx', 'android', 'hybrid']
        if platform_mode not in valid_modes:
            self.logger.error(f"Invalid platform mode: {platform_mode}")
            return False
        
        # Validate performance thresholds
        thresholds = self.get_performance_thresholds()
        if not thresholds.get('response_time'):
            self.logger.error("Missing response time thresholds")
            return False
        
        self.logger.info("Configuration validation passed")
        return True

# Global configuration instance
config = ConfigLoader()

def get_config() -> ConfigLoader:
    """Get global configuration instance."""
    return config 