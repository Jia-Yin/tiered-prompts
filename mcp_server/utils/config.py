#!/usr/bin/env python3
"""
Configuration Management for MCP Server

This module provides centralized configuration management for the MCP server,
supporting different deployment environments and runtime configurations.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import logging

# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "ai_prompt_system/database/prompt_system.db"
    connection_timeout: int = 30
    max_connections: int = 10
    backup_enabled: bool = True
    backup_interval_hours: int = 24

@dataclass
class CacheConfig:
    """Cache configuration"""
    max_size: int = 1000
    ttl_seconds: int = 3600
    cleanup_interval: int = 300
    enabled: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "mcp_server.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    console_enabled: bool = True

@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration"""
    enable_metrics: bool = True
    metrics_retention_hours: int = 24
    slow_query_threshold_ms: int = 100
    max_concurrent_requests: int = 50
    request_timeout_seconds: int = 30

@dataclass
class MCPConfig:
    """MCP server configuration"""
    name: str = "AI Prompt Engineering System"
    version: str = "1.0.0"
    description: str = "MCP server for AI prompt engineering with hierarchical rules"
    dependencies: List[str] = field(default_factory=lambda: ["sqlite3", "jinja2", "pydantic"])

    # Server settings
    enable_mock_mode: bool = False
    validate_schemas: bool = True
    enable_completions: bool = True

    # Transport settings
    transport_type: str = "stdio"  # stdio, sse, websocket
    host: str = "localhost"
    port: int = 8000

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_authentication: bool = False
    enable_authorization: bool = False
    api_key_required: bool = False
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60

@dataclass
class MCPServerConfig:
    """Complete MCP server configuration"""
    environment: str = "development"
    debug: bool = False

    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Centralized configuration management"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = MCPServerConfig()
        self.logger = logging.getLogger(f"{__name__}.ConfigManager")

        # Load configuration
        self._load_config()
        self._apply_environment_overrides()
        self._resolve_paths()
        self._validate_config()

    def _resolve_paths(self):
        """Resolve paths relative to project root if specified."""
        project_root_str = os.getenv("PROJECT_ROOT")
        if project_root_str:
            project_root = Path(project_root_str)

            # Resolve Database Path
            db_path = Path(self.config.database.path)
            if not db_path.is_absolute():
                self.config.database.path = str(project_root / db_path)
                self.logger.info(f"Resolved database path to: {self.config.database.path}")

            # Resolve Log File Path
            log_path = Path(self.config.logging.file_path)
            if not log_path.is_absolute():
                # Assume log path is relative to the mcp_server directory inside project_root
                self.config.logging.file_path = str(project_root / 'mcp_server' / log_path)
                self.logger.info(f"Resolved log file path to: {self.config.logging.file_path}")

    def _load_config(self):
        """Load configuration from file or environment"""
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)

                self._merge_config(config_data)
                self.logger.info(f"Configuration loaded from {self.config_file}")

            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_file}: {e}")
                self.logger.info("Using default configuration")
        else:
            self.logger.info("Using default configuration")

    def _merge_config(self, config_data: Dict[str, Any]):
        """Merge configuration data with defaults"""
        def merge_dict(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        # Convert config to dict, merge, and convert back
        current_dict = self._config_to_dict(self.config)
        merge_dict(current_dict, config_data)
        self.config = self._dict_to_config(current_dict)

    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        env_mapping = {
            'MCP_SERVER_ENVIRONMENT': ('environment',),
            'MCP_SERVER_DEBUG': ('debug',),
            'MCP_SERVER_DB_PATH': ('database', 'path'),
            'MCP_SERVER_CACHE_SIZE': ('cache', 'max_size'),
            'MCP_SERVER_LOG_LEVEL': ('logging', 'level'),
            'MCP_SERVER_MOCK_MODE': ('mcp', 'enable_mock_mode'),
            'MCP_SERVER_PORT': ('mcp', 'port'),
            'MCP_SERVER_HOST': ('mcp', 'host'),
        }

        for env_var, config_path in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]

                # Type conversion
                if config_path[-1] in ['debug', 'enable_mock_mode', 'enable_metrics']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif config_path[-1] in ['max_size', 'port', 'ttl_seconds']:
                    value = int(value)

                # Set value
                current = self.config
                for key in config_path[:-1]:
                    current = getattr(current, key)
                setattr(current, config_path[-1], value)

                self.logger.info(f"Environment override: {env_var} = {value}")

    def _validate_config(self):
        """Validate configuration"""
        errors = []

        # Validate database path
        db_path = Path(self.config.database.path)
        if not db_path.parent.exists():
            errors.append(f"Database directory does not exist: {db_path.parent}")

        # Validate cache settings
        if self.config.cache.max_size <= 0:
            errors.append("Cache max_size must be positive")

        # Validate logging settings
        if self.config.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append(f"Invalid logging level: {self.config.logging.level}")

        # Validate performance settings
        if self.config.performance.max_concurrent_requests <= 0:
            errors.append("max_concurrent_requests must be positive")

        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")

        self.logger.info("Configuration validation passed")

    def _config_to_dict(self, config: MCPServerConfig) -> Dict[str, Any]:
        """Convert config dataclass to dictionary"""
        def convert_value(value):
            if hasattr(value, '__dict__'):
                return {k: convert_value(v) for k, v in value.__dict__.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            else:
                return value

        return convert_value(config)

    def _dict_to_config(self, data: Dict[str, Any]) -> MCPServerConfig:
        """Convert dictionary to config dataclass"""
        # This is a simplified implementation
        # In production, you might want to use a more robust conversion
        config = MCPServerConfig()

        if 'environment' in data:
            config.environment = data['environment']
        if 'debug' in data:
            config.debug = data['debug']

        # Update sub-configs
        if 'database' in data:
            for key, value in data['database'].items():
                if hasattr(config.database, key):
                    setattr(config.database, key, value)

        if 'cache' in data:
            for key, value in data['cache'].items():
                if hasattr(config.cache, key):
                    setattr(config.cache, key, value)

        if 'logging' in data:
            for key, value in data['logging'].items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)

        if 'performance' in data:
            for key, value in data['performance'].items():
                if hasattr(config.performance, key):
                    setattr(config.performance, key, value)

        if 'mcp' in data:
            for key, value in data['mcp'].items():
                if hasattr(config.mcp, key):
                    setattr(config.mcp, key, value)

        if 'security' in data:
            for key, value in data['security'].items():
                if hasattr(config.security, key):
                    setattr(config.security, key, value)

        return config

    def get_config(self) -> MCPServerConfig:
        """Get current configuration"""
        return self.config

    def save_config(self, output_file: str):
        """Save current configuration to file"""
        config_dict = self._config_to_dict(self.config)

        try:
            with open(output_file, 'w') as f:
                if output_file.endswith('.yaml') or output_file.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)

            self.logger.info(f"Configuration saved to {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise

    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "environment": self.config.environment,
            "debug": self.config.debug,
            "mcp_server": {
                "name": self.config.mcp.name,
                "version": self.config.mcp.version,
                "transport": self.config.mcp.transport_type,
                "mock_mode": self.config.mcp.enable_mock_mode
            },
            "database": {
                "path": self.config.database.path,
                "backup_enabled": self.config.database.backup_enabled
            },
            "cache": {
                "enabled": self.config.cache.enabled,
                "max_size": self.config.cache.max_size
            },
            "logging": {
                "level": self.config.logging.level,
                "file_enabled": self.config.logging.file_enabled
            },
            "performance": {
                "metrics_enabled": self.config.performance.enable_metrics,
                "max_concurrent": self.config.performance.max_concurrent_requests
            }
        }

# ============================================================================
# GLOBAL CONFIGURATION INSTANCE
# ============================================================================

# Initialize global configuration manager
config_manager = ConfigManager()

def get_config() -> MCPServerConfig:
    """Get global configuration"""
    return config_manager.get_config()

def reload_config(config_file: Optional[str] = None):
    """Reload configuration"""
    global config_manager
    config_manager = ConfigManager(config_file)
    return config_manager.get_config()
