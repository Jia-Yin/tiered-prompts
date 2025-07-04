"""
Comprehensive test suite for AI Prompt Engineering System Phase 1.
"""

import unittest
import tempfile
import os
from pathlib import Path
import json

# Import system modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import get_system_status, setup_database
from src.database import (
    db_manager,
    validate_database,
    primitive_crud,
    semantic_crud,
    task_crud,
    relation_crud,
    version_crud,
    tag_crud,
)


class TestDatabaseSetup(unittest.TestCase):
    """Test database initialization and setup."""

    def setUp(self):
        """Set up test environment."""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()

        # Override database path
        db_manager.db_path = Path(self.temp_db.name)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary database
        os.unlink(self.temp_db.name)

    def test_database_initialization(self):
        """Test database initialization."""
        result = setup_database(with_sample_data=False)

        self.assertTrue(result['database_initialized'])
        self.assertTrue(result['validation_passed'])
        self.assertEqual(len(result['errors']), 0)

    def test_database_with_sample_data(self):
        """Test database initialization with sample data."""
        result = setup_database(with_sample_data=True)

        self.assertTrue(result['database_initialized'])
        self.assertTrue(result['sample_data_created'])
        self.assertTrue(result['validation_passed'])

        # Check that sample data exists
        primitives = primitive_crud.get_all()
        semantics = semantic_crud.get_all()
        tasks = task_crud.get_all()

        self.assertGreater(len(primitives), 0)
        self.assertGreater(len(semantics), 0)
        self.assertGreater(len(tasks), 0)

    def test_system_status(self):
        """Test system status reporting."""
        setup_database()
        status = get_system_status()

        self.assertIn('database_stats', status)
        self.assertIn('migration_status', status)
        self.assertIn('validation_passed', status)
        self.assertIn('version', status)


class TestPrimitiveRuleCRUD(unittest.TestCase):
    """Test primitive rule CRUD operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_create_primitive_rule(self):
        """Test creating primitive rules."""
        rule_id = primitive_crud.create_primitive_rule(
            name="test_rule",
            content="Test content",
            description="Test description",
            category="instruction"
        )

        self.assertIsInstance(rule_id, int)
        self.assertGreater(rule_id, 0)

        # Retrieve and verify
        rule = primitive_crud.get_by_id(rule_id)
        self.assertIsNotNone(rule)
        self.assertEqual(rule['name'], "test_rule")
        self.assertEqual(rule['content'], "Test content")
        self.assertEqual(rule['category'], "instruction")

    def test_invalid_category(self):
        """Test creating rule with invalid category."""
        with self.assertRaises(ValueError):
            primitive_crud.create_primitive_rule(
                name="invalid_rule",
                content="Test content",
                category="invalid_category"
            )

    def test_get_by_name(self):
        """Test retrieving rule by name."""
        primitive_crud.create_primitive_rule(
            name="unique_rule",
            content="Test content"
        )

        rule = primitive_crud.get_by_name("unique_rule")
        self.assertIsNotNone(rule)
        self.assertEqual(rule['name'], "unique_rule")

        # Test non-existent rule
        rule = primitive_crud.get_by_name("non_existent")
        self.assertIsNone(rule)

    def test_update_rule(self):
        """Test updating primitive rules."""
        rule_id = primitive_crud.create_primitive_rule(
            name="update_test",
            content="Original content"
        )

        # Update rule
        success = primitive_crud.update(rule_id, content="Updated content", description="New description")
        self.assertTrue(success)

        # Verify update
        rule = primitive_crud.get_by_id(rule_id)
        self.assertEqual(rule['content'], "Updated content")
        self.assertEqual(rule['description'], "New description")

    def test_delete_rule(self):
        """Test deleting primitive rules."""
        rule_id = primitive_crud.create_primitive_rule(
            name="delete_test",
            content="Test content"
        )

        # Verify rule exists
        rule = primitive_crud.get_by_id(rule_id)
        self.assertIsNotNone(rule)

        # Delete rule
        success = primitive_crud.delete(rule_id)
        self.assertTrue(success)

        # Verify rule is deleted
        rule = primitive_crud.get_by_id(rule_id)
        self.assertIsNone(rule)

    def test_search_rules(self):
        """Test searching primitive rules."""
        primitive_crud.create_primitive_rule(
            name="search_test_1",
            content="Python programming",
            description="Python related rule"
        )
        primitive_crud.create_primitive_rule(
            name="search_test_2",
            content="JavaScript coding",
            description="JS related rule"
        )

        # Search by content
        results = primitive_crud.search("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "search_test_1")

        # Search by description
        results = primitive_crud.search("JS")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "search_test_2")


class TestSemanticRuleCRUD(unittest.TestCase):
    """Test semantic rule CRUD operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_create_semantic_rule(self):
        """Test creating semantic rules."""
        rule_id = semantic_crud.create_semantic_rule(
            name="test_semantic",
            content_template="Review {{code}} for {{criteria}}",
            description="Code review template",
            category="code_review"
        )

        self.assertIsInstance(rule_id, int)

        rule = semantic_crud.get_by_id(rule_id)
        self.assertIsNotNone(rule)
        self.assertEqual(rule['name'], "test_semantic")
        self.assertIn("{{code}}", rule['content_template'])

    def test_template_variables(self):
        """Test semantic rule template variables."""
        rule_id = semantic_crud.create_semantic_rule(
            name="variable_test",
            content_template="Analyze {{input}} with parameters {{params}} and output {{format}}"
        )

        rule = semantic_crud.get_by_id(rule_id)
        template = rule['content_template']

        # Check that variables are preserved
        self.assertIn("{{input}}", template)
        self.assertIn("{{params}}", template)
        self.assertIn("{{format}}", template)


class TestTaskRuleCRUD(unittest.TestCase):
    """Test task rule CRUD operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_create_task_rule(self):
        """Test creating task rules."""
        rule_id = task_crud.create_task_rule(
            name="test_task",
            prompt_template="You are an expert in {{domain}}. {{semantic_rules}} {{primitive_rules}}",
            language="python",
            framework="django",
            domain="web_dev"
        )

        self.assertIsInstance(rule_id, int)

        rule = task_crud.get_by_id(rule_id)
        self.assertIsNotNone(rule)
        self.assertEqual(rule['language'], "python")
        self.assertEqual(rule['framework'], "django")
        self.assertEqual(rule['domain'], "web_dev")

    def test_get_by_domain(self):
        """Test retrieving tasks by domain."""
        task_crud.create_task_rule(
            name="web_task",
            prompt_template="Web development task",
            domain="web_dev"
        )
        task_crud.create_task_rule(
            name="data_task",
            prompt_template="Data science task",
            domain="data_science"
        )

        web_tasks = task_crud.get_by_domain("web_dev")
        self.assertEqual(len(web_tasks), 1)
        self.assertEqual(web_tasks[0]['name'], "web_task")

        data_tasks = task_crud.get_by_domain("data_science")
        self.assertEqual(len(data_tasks), 1)
        self.assertEqual(data_tasks[0]['name'], "data_task")


class TestRelationships(unittest.TestCase):
    """Test rule relationship operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

        # Create test rules
        self.primitive_id = primitive_crud.create_primitive_rule(
            name="test_primitive",
            content="Test primitive content"
        )
        self.semantic_id = semantic_crud.create_semantic_rule(
            name="test_semantic",
            content_template="Test semantic {{variable}}"
        )
        self.task_id = task_crud.create_task_rule(
            name="test_task",
            prompt_template="Test task {{semantic_rules}}"
        )

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_semantic_primitive_relation(self):
        """Test semantic-primitive relationships."""
        relation_id = relation_crud.create_semantic_primitive_relation(
            semantic_rule_id=self.semantic_id,
            primitive_rule_id=self.primitive_id,
            weight=0.8,
            order_index=1,
            is_required=True
        )

        self.assertIsInstance(relation_id, int)

        # Get related primitives
        primitives = relation_crud.get_primitive_rules_for_semantic(self.semantic_id)
        self.assertEqual(len(primitives), 1)
        self.assertEqual(primitives[0]['id'], self.primitive_id)
        self.assertEqual(primitives[0]['weight'], 0.8)
        self.assertEqual(primitives[0]['order_index'], 1)

    def test_task_semantic_relation(self):
        """Test task-semantic relationships."""
        context_override = json.dumps({"custom_param": "value"})

        relation_id = relation_crud.create_task_semantic_relation(
            task_rule_id=self.task_id,
            semantic_rule_id=self.semantic_id,
            weight=0.9,
            context_override=context_override
        )

        self.assertIsInstance(relation_id, int)

        # Get related semantics
        semantics = relation_crud.get_semantic_rules_for_task(self.task_id)
        self.assertEqual(len(semantics), 1)
        self.assertEqual(semantics[0]['id'], self.semantic_id)
        self.assertEqual(semantics[0]['weight'], 0.9)
        self.assertEqual(semantics[0]['context_override'], context_override)

    def test_invalid_weight(self):
        """Test invalid weight values."""
        with self.assertRaises(ValueError):
            relation_crud.create_semantic_primitive_relation(
                semantic_rule_id=self.semantic_id,
                primitive_rule_id=self.primitive_id,
                weight=15.0  # Invalid: > 10
            )

    def test_delete_relations(self):
        """Test deleting relationships."""
        # Create relation
        relation_crud.create_semantic_primitive_relation(
            semantic_rule_id=self.semantic_id,
            primitive_rule_id=self.primitive_id
        )

        # Verify relation exists
        primitives = relation_crud.get_primitive_rules_for_semantic(self.semantic_id)
        self.assertEqual(len(primitives), 1)

        # Delete relation
        success = relation_crud.delete_semantic_primitive_relation(
            self.semantic_id, self.primitive_id
        )
        self.assertTrue(success)

        # Verify relation is deleted
        primitives = relation_crud.get_primitive_rules_for_semantic(self.semantic_id)
        self.assertEqual(len(primitives), 0)


class TestVersioning(unittest.TestCase):
    """Test rule versioning functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_automatic_versioning(self):
        """Test automatic version creation on updates."""
        # Create rule
        rule_id = primitive_crud.create_primitive_rule(
            name="version_test",
            content="Original content"
        )

        # Update rule content (should trigger versioning)
        primitive_crud.update(rule_id, content="Updated content")

        # Check versions
        versions = version_crud.get_versions_for_rule('primitive', rule_id)
        self.assertGreater(len(versions), 0)

        # Check that old content is preserved in version
        version = versions[0]
        self.assertEqual(version['content_snapshot'], "Original content")

    def test_manual_versioning(self):
        """Test manual version creation."""
        rule_id = primitive_crud.create_primitive_rule(
            name="manual_version_test",
            content="Test content"
        )

        version_id = version_crud.create_version(
            rule_type='primitive',
            rule_id=rule_id,
            content_snapshot="Manual snapshot",
            change_description="Manual version for testing"
        )

        self.assertIsInstance(version_id, int)

        version = version_crud.get_version(version_id)
        self.assertIsNotNone(version)
        self.assertEqual(version['content_snapshot'], "Manual snapshot")
        self.assertEqual(version['change_description'], "Manual version for testing")


class TestTags(unittest.TestCase):
    """Test rule tagging functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database()

        self.rule_id = primitive_crud.create_primitive_rule(
            name="tag_test",
            content="Test content"
        )

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_add_tags(self):
        """Test adding tags to rules."""
        tag_crud.add_tag('primitive', self.rule_id, 'test')
        tag_crud.add_tag('primitive', self.rule_id, 'quality')

        tags = tag_crud.get_tags_for_rule('primitive', self.rule_id)
        self.assertIn('test', tags)
        self.assertIn('quality', tags)
        self.assertEqual(len(tags), 2)

    def test_remove_tags(self):
        """Test removing tags from rules."""
        tag_crud.add_tag('primitive', self.rule_id, 'removeme')
        tag_crud.add_tag('primitive', self.rule_id, 'keepme')

        # Remove one tag
        success = tag_crud.remove_tag('primitive', self.rule_id, 'removeme')
        self.assertTrue(success)

        tags = tag_crud.get_tags_for_rule('primitive', self.rule_id)
        self.assertNotIn('removeme', tags)
        self.assertIn('keepme', tags)

    def test_get_rules_by_tag(self):
        """Test finding rules by tag."""
        # Create another rule with same tag
        rule_id2 = primitive_crud.create_primitive_rule(
            name="tag_test_2",
            content="Test content 2"
        )

        tag_crud.add_tag('primitive', self.rule_id, 'common')
        tag_crud.add_tag('primitive', rule_id2, 'common')

        rules = tag_crud.get_rules_by_tag('common')
        self.assertEqual(len(rules), 2)


class TestValidation(unittest.TestCase):
    """Test database validation functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        db_manager.db_path = Path(self.temp_db.name)
        setup_database(with_sample_data=True)

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_db.name)

    def test_database_validation(self):
        """Test comprehensive database validation."""
        results = validate_database()

        self.assertIsInstance(results, dict)
        self.assertIn('valid', results)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        self.assertIn('checks', results)

        # With sample data, validation should pass
        self.assertTrue(results['valid'])
        self.assertEqual(len(results['errors']), 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
