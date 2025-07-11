"""
Main Rule Engine: Orchestrates all rule engine components.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .resolver import RuleResolver
from .template import TemplateEngine
from .validation import ValidationEngine
from .cache import CacheManager
from .export import RuleExporter

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Main rule engine that orchestrates all components.
    """

    def __init__(self, db, cache_size: int = 1000, cache_ttl: int = 3600):
        """
        Initialize the rule engine.

        Args:
            db: Database connection manager
            cache_size: Maximum cache size
            cache_ttl: Cache time-to-live in seconds
        """
        self.db = db
        self.cache_manager = CacheManager(max_size=cache_size, ttl=cache_ttl)
        self.resolver = RuleResolver(db, self.cache_manager)
        self.template_engine = TemplateEngine()
        self.validation_engine = ValidationEngine(db)
        self.exporter = RuleExporter(db)

        # Performance tracking
        self.performance_stats = {
            'total_resolutions': 0,
            'total_render_time': 0,
            'average_render_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    def generate_prompt(self, task_rule_name: str, context: Dict[str, Any] = None,
                       target_model: str = "claude") -> Dict[str, Any]:
        """
        Generate a complete prompt from a task rule.

        Args:
            task_rule_name: Name of the task rule
            context: Context variables for template rendering
            target_model: Target AI model for formatting

        Returns:
            Dictionary with generated prompt and metadata
        """
        start_time = datetime.now()

        try:
            # Get task rule by name
            task_rule = self._get_task_rule_by_name(task_rule_name)
            if not task_rule:
                raise ValueError(f"Task rule '{task_rule_name}' not found")

            # Resolve rule hierarchy
            resolved_hierarchy = self.resolver.resolve_task_rule(task_rule['id'], context)

            # Render final prompt
            rendered_prompt = self.template_engine.render_rule_hierarchy(resolved_hierarchy, context)

            # Format for target model
            formatted_prompt = self.template_engine.render_with_model_format(rendered_prompt, target_model)

            # Calculate performance metrics
            end_time = datetime.now()
            render_time = (end_time - start_time).total_seconds()

            self.performance_stats['total_resolutions'] += 1
            self.performance_stats['total_render_time'] += render_time
            self.performance_stats['average_render_time'] = (
                self.performance_stats['total_render_time'] / self.performance_stats['total_resolutions']
            )

            return {
                'prompt': formatted_prompt,
                'raw_prompt': rendered_prompt,
                'task_rule': task_rule,
                'target_model': target_model,
                'context': context,
                'hierarchy': resolved_hierarchy,
                'performance': {
                    'render_time': render_time,
                    'cached': False  # TODO: Track cache usage
                },
                'generated_at': start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating prompt for task '{task_rule_name}': {e}")
            raise

    def validate_system(self) -> Dict[str, Any]:
        """
        Validate the entire rule system.

        Returns:
            Validation results
        """
        try:
            # Run comprehensive validation
            validation_results = self.validation_engine.check_consistency()

            # Check for conflicts
            conflicts = self.validation_engine.check_rule_conflicts()

            # Get cache statistics
            cache_stats = self.cache_manager.get_stats()

            # Get system statistics
            system_stats = self._get_system_stats()

            return {
                'validation': validation_results,
                'conflicts': conflicts,
                'cache': cache_stats,
                'system': system_stats,
                'performance': self.performance_stats,
                'validated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"System validation failed: {e}")
            raise

    def optimize_system(self) -> Dict[str, Any]:
        """
        Optimize the rule system performance.

        Returns:
            Optimization results
        """
        try:
            # Clean up expired cache entries
            expired_cleaned = self.cache_manager.cleanup_expired()

            # TODO: Implement more optimization strategies
            # - Analyze rule usage patterns
            # - Suggest rule consolidations
            # - Optimize relationship weights

            return {
                'cache_cleaned': expired_cleaned,
                'optimized_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"System optimization failed: {e}")
            raise

    def get_rule_dependencies(self, rule_type: str, rule_name: str) -> List[Dict[str, Any]]:
        """
        Get all dependencies for a rule.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive')
            rule_name: Name of the rule

        Returns:
            List of dependencies
        """
        try:
            # Get rule by name
            rule = self._get_rule_by_name(rule_type, rule_name)
            if not rule:
                raise ValueError(f"{rule_type.title()} rule '{rule_name}' not found")

            # Get dependencies
            dependencies = self.resolver.get_rule_dependencies(rule_type, rule['id'])

            return dependencies

        except Exception as e:
            logger.error(f"Error getting dependencies for {rule_type} rule '{rule_name}': {e}")
            raise

    def analyze_rule_usage(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze rule usage patterns.

        Args:
            days: Number of days to analyze

        Returns:
            Usage analysis results
        """
        # TODO: Implement usage tracking
        # This would require adding usage logging to the database
        return {
            'analysis_period': f"{days} days",
            'message': "Usage tracking not yet implemented",
            'analyzed_at': datetime.now().isoformat()
        }

    def export_rules(self, filepath: str, rule_types: List[str] = None,
                    format: str = 'json') -> Dict[str, Any]:
        """
        Export rules to file.

        Args:
            filepath: Output file path
            rule_types: Types of rules to export
            format: Export format

        Returns:
            Export results
        """
        return self.exporter.export_rules(filepath, rule_types, format)

    def import_rules(self, filepath: str, merge_strategy: str = 'skip_existing') -> Dict[str, Any]:
        """
        Import rules from file.

        Args:
            filepath: Input file path
            merge_strategy: How to handle existing rules

        Returns:
            Import results
        """
        return self.exporter.import_rules(filepath, merge_strategy)

    def backup_system(self, backup_path: str) -> Dict[str, Any]:
        """
        Create a complete system backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Backup results
        """
        return self.exporter.backup_database(backup_path)

    def restore_system(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore system from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Restore results
        """
        # Clear cache after restore
        self.cache_manager.clear()

        return self.exporter.restore_database(backup_path)

    def _get_task_rule_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get task rule by name."""
        try:
            results = self.db.execute_query(
                "SELECT * FROM task_rules WHERE name = ?", (name,)
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting task rule '{name}': {e}")
            return None

    def _get_rule_by_name(self, rule_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get rule by type and name."""
        try:
            table_name = f"{rule_type}_rules"
            results = self.db.execute_query(
                f"SELECT * FROM {table_name} WHERE name = ?", (name,)
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting {rule_type} rule '{name}': {e}")
            return None

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            stats = {}

            # Count rules
            for rule_type in ['primitive', 'semantic', 'task']:
                count = self.db.execute_query(f"SELECT COUNT(*) as count FROM {rule_type}_rules")[0]['count']
                stats[f"{rule_type}_rules"] = count

            # Count relationships
            stats['semantic_primitive_relations'] = self.db.execute_query(
                "SELECT COUNT(*) as count FROM semantic_primitive_relations"
            )[0]['count']

            stats['task_semantic_relations'] = self.db.execute_query(
                "SELECT COUNT(*) as count FROM task_semantic_relations"
            )[0]['count']

            return stats

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
