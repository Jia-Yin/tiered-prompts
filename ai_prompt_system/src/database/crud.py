"""
CRUD operations for all database tables in the AI Prompt Engineering System.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import logging

from .connection import db_manager, validate_json_field

logger = logging.getLogger(__name__)


class BaseRuleCRUD:
    """Base class for rule CRUD operations."""

    def __init__(self, table_name: str, content_field: str):
        self.table_name = table_name
        self.content_field = content_field

    def create(self, **kwargs) -> int:
        """Create a new rule."""
        fields = []
        values = []
        placeholders = []

        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)
                placeholders.append('?')

        query = f"""
            INSERT INTO {self.table_name} ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        return db_manager.execute_insert(query, tuple(values))

    def get_by_id(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """Get rule by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        results = db_manager.execute_query(query, (rule_id,))
        return results[0] if results else None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get rule by name."""
        query = f"SELECT * FROM {self.table_name} WHERE name = ?"
        results = db_manager.execute_query(query, (name,))
        return results[0] if results else None

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all rules with optional pagination."""
        query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        return db_manager.execute_query(query)

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get rules by category."""
        query = f"SELECT * FROM {self.table_name} WHERE category = ? ORDER BY created_at DESC"
        return db_manager.execute_query(query, (category,))

    def update(self, rule_id: int, **kwargs) -> bool:
        """Update rule by ID."""
        if not kwargs:
            return False

        set_clauses = []
        values = []

        for key, value in kwargs.items():
            if key != 'id':  # Don't allow ID updates
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        values.append(rule_id)
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = ?"

        affected_rows = db_manager.execute_update(query, tuple(values))
        return affected_rows > 0

    def delete(self, rule_id: int) -> bool:
        """Delete rule by ID."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        affected_rows = db_manager.execute_update(query, (rule_id,))
        return affected_rows > 0

    def search(self, search_term: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search rules by term in specified fields."""
        if not fields:
            fields = ['name', 'description', self.content_field]

        conditions = []
        params = []

        for field in fields:
            conditions.append(f"{field} LIKE ?")
            params.append(f"%{search_term}%")

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {' OR '.join(conditions)}
            ORDER BY created_at DESC
        """

        return db_manager.execute_query(query, tuple(params))


class PrimitiveRuleCRUD(BaseRuleCRUD):
    """CRUD operations for primitive rules."""

    def __init__(self):
        super().__init__('primitive_rules', 'content')

    def create_primitive_rule(
        self,
        name: str,
        content: str,
        description: str = None,
        category: str = None
    ) -> int:
        """Create a new primitive rule with validation."""
        if category and category not in ['instruction', 'format', 'constraint', 'pattern']:
            raise ValueError(f"Invalid category: {category}")

        return self.create(
            name=name,
            content=content,
            description=description,
            category=category
        )


class SemanticRuleCRUD(BaseRuleCRUD):
    """CRUD operations for semantic rules."""

    def __init__(self):
        super().__init__('semantic_rules', 'content_template')

    def create_semantic_rule(
        self,
        name: str,
        content_template: str,
        description: str = None,
        category: str = None
    ) -> int:
        """Create a new semantic rule with validation."""
        valid_categories = ['code_review', 'explanation', 'debugging', 'optimization', 'generation']
        if category and category not in valid_categories:
            raise ValueError(f"Invalid category: {category}")

        return self.create(
            name=name,
            content_template=content_template,
            description=description,
            category=category
        )


class TaskRuleCRUD(BaseRuleCRUD):
    """CRUD operations for task rules."""

    def __init__(self):
        super().__init__('task_rules', 'prompt_template')

    def create_task_rule(
        self,
        name: str,
        prompt_template: str,
        description: str = None,
        language: str = None,
        framework: str = None,
        domain: str = None
    ) -> int:
        """Create a new task rule with validation."""
        valid_domains = ['web_dev', 'data_science', 'electrical_eng', 'mobile_dev', 'devops', 'general']
        if domain and domain not in valid_domains:
            raise ValueError(f"Invalid domain: {domain}")

        return self.create(
            name=name,
            prompt_template=prompt_template,
            description=description,
            language=language,
            framework=framework,
            domain=domain
        )

    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get task rules by domain."""
        query = "SELECT * FROM task_rules WHERE domain = ? ORDER BY created_at DESC"
        return db_manager.execute_query(query, (domain,))

    def get_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get task rules by programming language."""
        query = "SELECT * FROM task_rules WHERE language = ? ORDER BY created_at DESC"
        return db_manager.execute_query(query, (language,))

    def get_by_framework(self, framework: str) -> List[Dict[str, Any]]:
        """Get task rules by framework."""
        query = "SELECT * FROM task_rules WHERE framework = ? ORDER BY created_at DESC"
        return db_manager.execute_query(query, (framework,))


class RelationCRUD:
    """CRUD operations for rule relationships."""

    def create_semantic_primitive_relation(
        self,
        semantic_rule_id: int,
        primitive_rule_id: int,
        weight: float = 1.0,
        order_index: int = 0,
        is_required: bool = True
    ) -> int:
        """Create semantic-primitive relationship."""
        if not (0 <= weight <= 10):
            raise ValueError("Weight must be between 0 and 10")

        if order_index < 0:
            raise ValueError("Order index must be non-negative")

        query = """
            INSERT INTO semantic_primitive_relations
            (semantic_rule_id, primitive_rule_id, weight, order_index, is_required)
            VALUES (?, ?, ?, ?, ?)
        """

        return db_manager.execute_insert(
            query,
            (semantic_rule_id, primitive_rule_id, weight, order_index, is_required)
        )

    def create_task_semantic_relation(
        self,
        task_rule_id: int,
        semantic_rule_id: int,
        weight: float = 1.0,
        order_index: int = 0,
        is_required: bool = True,
        context_override: str = None
    ) -> int:
        """Create task-semantic relationship."""
        if not (0 <= weight <= 10):
            raise ValueError("Weight must be between 0 and 10")

        if order_index < 0:
            raise ValueError("Order index must be non-negative")

        if context_override and not validate_json_field(context_override):
            raise ValueError("Context override must be valid JSON")

        query = """
            INSERT INTO task_semantic_relations
            (task_rule_id, semantic_rule_id, weight, order_index, is_required, context_override)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        return db_manager.execute_insert(
            query,
            (task_rule_id, semantic_rule_id, weight, order_index, is_required, context_override)
        )

    def get_primitive_rules_for_semantic(self, semantic_rule_id: int) -> List[Dict[str, Any]]:
        """Get primitive rules related to a semantic rule."""
        query = """
            SELECT pr.*, spr.weight, spr.order_index, spr.is_required
            FROM primitive_rules pr
            JOIN semantic_primitive_relations spr ON pr.id = spr.primitive_rule_id
            WHERE spr.semantic_rule_id = ?
            ORDER BY spr.order_index, pr.name
        """

        return db_manager.execute_query(query, (semantic_rule_id,))

    def get_semantic_rules_for_task(self, task_rule_id: int) -> List[Dict[str, Any]]:
        """Get semantic rules related to a task rule."""
        query = """
            SELECT sr.*, tsr.weight, tsr.order_index, tsr.is_required, tsr.context_override
            FROM semantic_rules sr
            JOIN task_semantic_relations tsr ON sr.id = tsr.semantic_rule_id
            WHERE tsr.task_rule_id = ?
            ORDER BY tsr.order_index, sr.name
        """

        return db_manager.execute_query(query, (task_rule_id,))

    def delete_semantic_primitive_relation(self, semantic_rule_id: int, primitive_rule_id: int) -> bool:
        """Delete semantic-primitive relationship."""
        query = """
            DELETE FROM semantic_primitive_relations
            WHERE semantic_rule_id = ? AND primitive_rule_id = ?
        """

        affected_rows = db_manager.execute_update(query, (semantic_rule_id, primitive_rule_id))
        return affected_rows > 0

    def delete_task_semantic_relation(self, task_rule_id: int, semantic_rule_id: int) -> bool:
        """Delete task-semantic relationship."""
        query = """
            DELETE FROM task_semantic_relations
            WHERE task_rule_id = ? AND semantic_rule_id = ?
        """

        affected_rows = db_manager.execute_update(query, (task_rule_id, semantic_rule_id))
        return affected_rows > 0


class VersionCRUD:
    """CRUD operations for rule versions."""

    def create_version(
        self,
        rule_type: str,
        rule_id: int,
        content_snapshot: str,
        change_description: str = None
    ) -> int:
        """Create a new version entry."""
        if rule_type not in ['primitive', 'semantic', 'task']:
            raise ValueError(f"Invalid rule type: {rule_type}")

        # Get next version number
        query = """
            SELECT COALESCE(MAX(version_number), 0) + 1 as next_version
            FROM rule_versions
            WHERE rule_type = ? AND rule_id = ?
        """

        result = db_manager.execute_query(query, (rule_type, rule_id))
        version_number = result[0]['next_version'] if result else 1

        # Insert version
        insert_query = """
            INSERT INTO rule_versions (rule_type, rule_id, version_number, content_snapshot, change_description)
            VALUES (?, ?, ?, ?, ?)
        """

        return db_manager.execute_insert(
            insert_query,
            (rule_type, rule_id, version_number, content_snapshot, change_description)
        )

    def get_versions_for_rule(self, rule_type: str, rule_id: int) -> List[Dict[str, Any]]:
        """Get all versions for a specific rule."""
        query = """
            SELECT * FROM rule_versions
            WHERE rule_type = ? AND rule_id = ?
            ORDER BY version_number DESC
        """

        return db_manager.execute_query(query, (rule_type, rule_id))

    def get_version(self, version_id: int) -> Optional[Dict[str, Any]]:
        """Get specific version by ID."""
        query = "SELECT * FROM rule_versions WHERE id = ?"
        results = db_manager.execute_query(query, (version_id,))
        return results[0] if results else None


class TagCRUD:
    """CRUD operations for rule tags."""

    def add_tag(self, rule_type: str, rule_id: int, tag: str) -> int:
        """Add tag to a rule."""
        if rule_type not in ['primitive', 'semantic', 'task']:
            raise ValueError(f"Invalid rule type: {rule_type}")

        # First, ensure the tag exists in the tags table
        tag_query = "INSERT OR IGNORE INTO tags (name) VALUES (?)"
        db_manager.execute_insert(tag_query, (tag,))

        # Get the tag ID
        tag_id_query = "SELECT id FROM tags WHERE name = ?"
        tag_result = db_manager.execute_query(tag_id_query, (tag,))
        if not tag_result:
            raise ValueError(f"Failed to get tag ID for: {tag}")
        tag_id = tag_result[0]['id']

        # Insert into rule_tags with tag_id
        query = """
            INSERT OR IGNORE INTO rule_tags (rule_type, rule_id, tag_id)
            VALUES (?, ?, ?)
        """

        return db_manager.execute_insert(query, (rule_type, rule_id, tag_id))

    def remove_tag(self, rule_type: str, rule_id: int, tag: str) -> bool:
        """Remove tag from a rule."""
        # Get the tag ID first
        tag_id_query = "SELECT id FROM tags WHERE name = ?"
        tag_result = db_manager.execute_query(tag_id_query, (tag,))
        if not tag_result:
            return False  # Tag doesn't exist
        tag_id = tag_result[0]['id']

        query = """
            DELETE FROM rule_tags
            WHERE rule_type = ? AND rule_id = ? AND tag_id = ?
        """

        affected_rows = db_manager.execute_update(query, (rule_type, rule_id, tag_id))
        return affected_rows > 0

    def get_tags_for_rule(self, rule_type: str, rule_id: int) -> List[str]:
        """Get all tags for a specific rule."""
        query = """
            SELECT t.name as tag FROM rule_tags rt
            JOIN tags t ON rt.tag_id = t.id
            WHERE rt.rule_type = ? AND rt.rule_id = ?
            ORDER BY t.name
        """

        results = db_manager.execute_query(query, (rule_type, rule_id))
        return [row['tag'] for row in results]

    def get_rules_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all rules with a specific tag."""
        query = """
            SELECT rt.rule_type, rt.rule_id, t.name as tag FROM rule_tags rt
            JOIN tags t ON rt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY rt.rule_type, rt.rule_id
        """

        return db_manager.execute_query(query, (tag,))

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        query = "SELECT name FROM tags ORDER BY name"
        results = db_manager.execute_query(query)
        return [row['name'] for row in results]


# Initialize CRUD instances
primitive_crud = PrimitiveRuleCRUD()
semantic_crud = SemanticRuleCRUD()
task_crud = TaskRuleCRUD()
relation_crud = RelationCRUD()
version_crud = VersionCRUD()
tag_crud = TagCRUD()
