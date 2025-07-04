"""
Rule Engine module - Core rule resolution and prompt generation system.

This module provides the core functionality for:
- Rule dependency resolution
- Template rendering with Jinja2
- Rule validation and circular dependency detection
- Performance optimization with caching
- Rule export/import/backup functionality
"""

from .engine import RuleEngine
from .resolver import RuleResolver
from .template import TemplateEngine
from .validation import ValidationEngine
from .cache import CacheManager, MemoryEfficientCache
from .export import RuleExporter

__all__ = [
    'RuleEngine',
    'RuleResolver',
    'TemplateEngine',
    'ValidationEngine',
    'CacheManager',
    'MemoryEfficientCache',
    'RuleExporter'
]

__version__ = '1.0.0'
