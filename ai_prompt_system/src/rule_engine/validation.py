"""
ValidationEngine: Ensures rule consistency and detects circular dependencies.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ValidationEngine:
    def __init__(self, db):
        self.db = db
        self.errors = []
        self.warnings = []

    def check_consistency(self) -> Dict[str, any]:
        """
        Perform comprehensive consistency checks on all rules and relationships.

        Returns:
            Dict with validation results
        """
        self.errors = []
        self.warnings = []

        # Check rule consistency
        self._check_rule_integrity()
        self._check_relationship_integrity()
        self._check_template_validity()

        # Check for circular dependencies
        cycles = self.detect_circular_dependencies()
        if cycles:
            self.errors.extend([f"Circular dependency detected: {' -> '.join(map(str, cycle))}" for cycle in cycles])

        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'circular_dependencies': cycles
        }

    def detect_circular_dependencies(self) -> List[List[int]]:
        """
        Detect circular dependencies in rule relationships using DFS.

        Returns:
            List of cycles, each cycle is a list of rule IDs
        """
        cycles = []

        # Build dependency graph
        graph = self._build_dependency_graph()

        # Track visited nodes and recursion stack
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor)

            rec_stack.remove(node)
            path.pop()

        # Check each node
        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _build_dependency_graph(self) -> Dict[int, List[int]]:
        """
        Build a dependency graph from rule relationships.

        Returns:
            Dictionary mapping rule IDs to their dependencies
        """
        graph = defaultdict(list)

        try:
            # Get semantic -> primitive relationships
            semantic_relations = self.db.execute_query(
                "SELECT semantic_rule_id, primitive_rule_id FROM semantic_primitive_relations"
            )

            for relation in semantic_relations:
                # Semantic rule depends on primitive rule
                semantic_id = f"semantic_{relation['semantic_rule_id']}"
                primitive_id = f"primitive_{relation['primitive_rule_id']}"
                graph[semantic_id].append(primitive_id)

            # Get task -> semantic relationships
            task_relations = self.db.execute_query(
                "SELECT task_rule_id, semantic_rule_id FROM task_semantic_relations"
            )

            for relation in task_relations:
                # Task rule depends on semantic rule
                task_id = f"task_{relation['task_rule_id']}"
                semantic_id = f"semantic_{relation['semantic_rule_id']}"
                graph[task_id].append(semantic_id)

        except Exception as e:
            logger.error(f"Error building dependency graph: {e}")
            self.errors.append(f"Failed to build dependency graph: {e}")

        return dict(graph)

    def _check_rule_integrity(self):
        """Check integrity of individual rules."""
        try:
            # Check primitive rules
            primitives = self.db.execute_query("SELECT * FROM primitive_rules")
            for rule in primitives:
                if not rule['name'] or not rule['content']:
                    self.errors.append(f"Primitive rule {rule['id']} has missing name or content")

                if rule['category'] not in ['instruction', 'format', 'constraint', 'pattern']:
                    self.errors.append(f"Primitive rule {rule['id']} has invalid category: {rule['category']}")

            # Check semantic rules
            semantics = self.db.execute_query("SELECT * FROM semantic_rules")
            for rule in semantics:
                if not rule['name'] or not rule['content_template']:
                    self.errors.append(f"Semantic rule {rule['id']} has missing name or content_template")

            # Check task rules
            tasks = self.db.execute_query("SELECT * FROM task_rules")
            for rule in tasks:
                if not rule['name'] or not rule['prompt_template']:
                    self.errors.append(f"Task rule {rule['id']} has missing name or prompt_template")

        except Exception as e:
            logger.error(f"Error checking rule integrity: {e}")
            self.errors.append(f"Failed to check rule integrity: {e}")

    def _check_relationship_integrity(self):
        """Check integrity of relationships between rules."""
        try:
            # Check semantic-primitive relationships
            sp_relations = self.db.execute_query("""
                SELECT spr.*, sr.name as semantic_name, pr.name as primitive_name
                FROM semantic_primitive_relations spr
                LEFT JOIN semantic_rules sr ON spr.semantic_rule_id = sr.id
                LEFT JOIN primitive_rules pr ON spr.primitive_rule_id = pr.id
            """)

            for rel in sp_relations:
                if not rel['semantic_name']:
                    self.errors.append(f"Semantic-primitive relation {rel['id']} references non-existent semantic rule {rel['semantic_rule_id']}")
                if not rel['primitive_name']:
                    self.errors.append(f"Semantic-primitive relation {rel['id']} references non-existent primitive rule {rel['primitive_rule_id']}")

            # Check task-semantic relationships
            ts_relations = self.db.execute_query("""
                SELECT tsr.*, tr.name as task_name, sr.name as semantic_name
                FROM task_semantic_relations tsr
                LEFT JOIN task_rules tr ON tsr.task_rule_id = tr.id
                LEFT JOIN semantic_rules sr ON tsr.semantic_rule_id = sr.id
            """)

            for rel in ts_relations:
                if not rel['task_name']:
                    self.errors.append(f"Task-semantic relation {rel['id']} references non-existent task rule {rel['task_rule_id']}")
                if not rel['semantic_name']:
                    self.errors.append(f"Task-semantic relation {rel['id']} references non-existent semantic rule {rel['semantic_rule_id']}")

        except Exception as e:
            logger.error(f"Error checking relationship integrity: {e}")
            self.errors.append(f"Failed to check relationship integrity: {e}")

    def _check_template_validity(self):
        """Check validity of template syntax in rules."""
        try:
            from jinja2 import Template, TemplateSyntaxError

            # Check semantic rule templates
            semantics = self.db.execute_query("SELECT id, name, content_template FROM semantic_rules")
            for rule in semantics:
                try:
                    Template(rule['content_template'])
                except TemplateSyntaxError as e:
                    self.errors.append(f"Semantic rule '{rule['name']}' has invalid template syntax: {e}")

            # Check task rule templates
            tasks = self.db.execute_query("SELECT id, name, prompt_template FROM task_rules")
            for rule in tasks:
                try:
                    Template(rule['prompt_template'])
                except TemplateSyntaxError as e:
                    self.errors.append(f"Task rule '{rule['name']}' has invalid template syntax: {e}")

        except Exception as e:
            logger.error(f"Error checking template validity: {e}")
            self.errors.append(f"Failed to check template validity: {e}")

    def check_rule_conflicts(self) -> List[Dict]:
        """
        Check for conflicting rules that might cause issues.

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        try:
            # Check for duplicate rule names within same type
            for table in ['primitive_rules', 'semantic_rules', 'task_rules']:
                duplicates = self.db.execute_query(f"""
                    SELECT name, COUNT(*) as count
                    FROM {table}
                    GROUP BY name
                    HAVING COUNT(*) > 1
                """)

                for dup in duplicates:
                    conflicts.append({
                        'type': 'duplicate_name',
                        'table': table,
                        'name': dup['name'],
                        'count': dup['count']
                    })

            # Check for conflicting categories/domains
            # This could be expanded based on specific business rules

        except Exception as e:
            logger.error(f"Error checking rule conflicts: {e}")
            conflicts.append({
                'type': 'error',
                'message': f"Failed to check rule conflicts: {e}"
            })

        return conflicts
