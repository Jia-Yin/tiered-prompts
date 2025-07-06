"""
RuleResolver: Navigates rule hierarchy and resolves dependencies.
"""

import logging
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class RuleResolver:
    def __init__(self, db, cache_manager=None):
        self.db = db
        self.cache_manager = cache_manager
        self._resolution_cache = {}

    def resolve_task_rule(self, task_rule_id: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve a task rule and all its dependencies.

        Args:
            task_rule_id: ID of the task rule to resolve
            context: Additional context for template rendering

        Returns:
            Dictionary containing resolved rule hierarchy
        """
        if context is None:
            context = {}

        # Check cache first
        cache_key = f"task_{task_rule_id}_{hash(str(sorted(context.items())))}"
        if self.cache_manager:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result

        try:
            # Get task rule
            task_rule = self._get_task_rule(task_rule_id)
            if not task_rule:
                raise ValueError(f"Task rule {task_rule_id} not found")

            # Get semantic rules for this task
            semantic_rules = self._get_semantic_rules_for_task(task_rule_id)

            # Resolve each semantic rule
            resolved_semantics = []
            for semantic_rule in semantic_rules:
                resolved_semantic = self.resolve_semantic_rule(semantic_rule['id'], context)
                resolved_semantics.append(resolved_semantic)

            # Build final result
            result = {
                'task_rule': task_rule,
                'semantic_rules': resolved_semantics,
                'context': context,
                'resolved_at': self._get_timestamp()
            }

            # Cache the result
            if self.cache_manager:
                self.cache_manager.set(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error resolving task rule {task_rule_id}: {e}")
            raise

    def resolve_semantic_rule(self, semantic_rule_id: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve a semantic rule and its primitive dependencies.

        Args:
            semantic_rule_id: ID of the semantic rule to resolve
            context: Additional context for template rendering

        Returns:
            Dictionary containing resolved semantic rule
        """
        if context is None:
            context = {}

        # Check cache first
        cache_key = f"semantic_{semantic_rule_id}_{hash(str(sorted(context.items())))}"
        if self.cache_manager:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result

        try:
            # Get semantic rule
            semantic_rule = self._get_semantic_rule(semantic_rule_id)
            if not semantic_rule:
                raise ValueError(f"Semantic rule {semantic_rule_id} not found")

            # Get primitive rules for this semantic rule
            primitive_rules = self._get_primitive_rules_for_semantic(semantic_rule_id)

            # Build result
            result = {
                'semantic_rule': semantic_rule,
                'primitive_rules': primitive_rules,
                'context': context,
                'resolved_at': self._get_timestamp()
            }

            # Cache the result
            if self.cache_manager:
                self.cache_manager.set(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Error resolving semantic rule {semantic_rule_id}: {e}")
            raise

    def resolve_rule_hierarchy(self, rule_type: str, rule_id: int, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve complete rule hierarchy starting from any rule type.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive')
            rule_id: ID of the rule to resolve
            context: Additional context for template rendering

        Returns:
            Dictionary containing complete resolved hierarchy
        """
        if rule_type == 'task':
            return self.resolve_task_rule(rule_id, context)
        elif rule_type == 'semantic':
            return self.resolve_semantic_rule(rule_id, context)
        elif rule_type == 'primitive':
            return self._get_primitive_rule(rule_id)
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")

    def get_rule_dependencies(self, rule_type: str, rule_id: int) -> List[Dict[str, Any]]:
        """
        Get all dependencies for a given rule.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive')
            rule_id: ID of the rule

        Returns:
            List of dependency dictionaries
        """
        dependencies = []

        try:
            if rule_type == 'task':
                # Task depends on semantic rules
                semantic_rules = self._get_semantic_rules_for_task(rule_id)
                for semantic in semantic_rules:
                    dependencies.append({
                        'type': 'semantic',
                        'id': semantic['id'],
                        'name': semantic['name'],
                        'weight': semantic.get('weight', 1.0)
                    })

                    # Also get primitive dependencies of semantic rules
                    primitives = self._get_primitive_rules_for_semantic(semantic['id'])
                    for primitive in primitives:
                        dependencies.append({
                            'type': 'primitive',
                            'id': primitive['id'],
                            'name': primitive['name'],
                            'weight': primitive.get('weight', 1.0),
                            'via_semantic': semantic['id']
                        })

            elif rule_type == 'semantic':
                # Semantic depends on primitive rules
                primitive_rules = self._get_primitive_rules_for_semantic(rule_id)
                for primitive in primitive_rules:
                    dependencies.append({
                        'type': 'primitive',
                        'id': primitive['id'],
                        'name': primitive['name'],
                        'weight': primitive.get('weight', 1.0)
                    })

            # Primitive rules have no dependencies

        except Exception as e:
            logger.error(f"Error getting dependencies for {rule_type} rule {rule_id}: {e}")
            raise

        return dependencies

    def get_rules_by_type(self, rule_type: str) -> List[Dict[str, Any]]:
        """
        Get all rules of a specific type.

        Args:
            rule_type: Type of rule ('task', 'semantic', 'primitive', 'all')

        Returns:
            List of rule dictionaries
        """
        if rule_type == 'all':
            task_rules = self.db.execute_query("SELECT id, name, 'task' as type FROM task_rules")
            semantic_rules = self.db.execute_query("SELECT id, name, 'semantic' as type FROM semantic_rules")
            primitive_rules = self.db.execute_query("SELECT id, name, 'primitive' as type FROM primitive_rules")
            return task_rules + semantic_rules + primitive_rules

        table_name = f"{rule_type}_rules"
        if rule_type not in ['task', 'semantic', 'primitive']:
            raise ValueError(f"Invalid rule type: {rule_type}")

        query = f"SELECT id, name, '{rule_type}' as type FROM {table_name}"
        try:
            results = self.db.execute_query(query)
            return results
        except Exception as e:
            logger.error(f"Error getting {rule_type} rules: {e}")
            raise

    def _get_task_rule(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get task rule by ID."""
        try:
            results = self.db.execute_query(
                "SELECT * FROM task_rules WHERE id = ?", (task_id,)
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting task rule {task_id}: {e}")
            return None

    def _get_semantic_rule(self, semantic_id: int) -> Optional[Dict[str, Any]]:
        """Get semantic rule by ID."""
        try:
            results = self.db.execute_query(
                "SELECT * FROM semantic_rules WHERE id = ?", (semantic_id,)
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting semantic rule {semantic_id}: {e}")
            return None

    def _get_primitive_rule(self, primitive_id: int) -> Optional[Dict[str, Any]]:
        """Get primitive rule by ID."""
        try:
            results = self.db.execute_query(
                "SELECT * FROM primitive_rules WHERE id = ?", (primitive_id,)
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting primitive rule {primitive_id}: {e}")
            return None

    def _get_semantic_rules_for_task(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all semantic rules associated with a task rule."""
        try:
            results = self.db.execute_query("""
                SELECT sr.*, tsr.weight, tsr.order_index, tsr.is_required, tsr.context_override
                FROM semantic_rules sr
                JOIN task_semantic_relations tsr ON sr.id = tsr.semantic_rule_id
                WHERE tsr.task_rule_id = ?
                ORDER BY tsr.order_index, sr.name
            """, (task_id,))
            return results
        except Exception as e:
            logger.error(f"Error getting semantic rules for task {task_id}: {e}")
            return []

    def _get_primitive_rules_for_semantic(self, semantic_id: int) -> List[Dict[str, Any]]:
        """Get all primitive rules associated with a semantic rule."""
        try:
            results = self.db.execute_query("""
                SELECT pr.*, spr.weight, spr.order_index, spr.is_required
                FROM primitive_rules pr
                JOIN semantic_primitive_relations spr ON pr.id = spr.primitive_rule_id
                WHERE spr.semantic_rule_id = ?
                ORDER BY spr.order_index, pr.name
            """, (semantic_id,))
            return results
        except Exception as e:
            logger.error(f"Error getting primitive rules for semantic {semantic_id}: {e}")
            return []

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def clear_cache(self):
        """Clear the resolution cache."""
        self._resolution_cache.clear()
        if self.cache_manager:
            self.cache_manager.clear()
