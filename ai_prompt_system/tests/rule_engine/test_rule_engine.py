"""
Comprehensive unit tests for Rule Engine components.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add the ai_prompt_system directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rule_engine.engine import RuleEngine
from src.rule_engine.resolver import RuleResolver
from src.rule_engine.template import TemplateEngine
from src.rule_engine.validation import ValidationEngine
from src.rule_engine.cache import CacheManager, MemoryEfficientCache
from src.rule_engine.export import RuleExporter


class TestTemplateEngine:
    """Test TemplateEngine functionality."""

    def test_basic_template_rendering(self):
        """Test basic template rendering with Jinja2."""
        engine = TemplateEngine()
        template = "Hello, {{ name }}!"
        context = {"name": "World"}
        result = engine.render_template(template, context)
        assert result == "Hello, World!"

    def test_template_with_custom_filters(self):
        """Test custom Jinja2 filters."""
        engine = TemplateEngine()

        # Test json_pretty filter
        template = "{{ data | json_pretty }}"
        context = {"data": {"key": "value"}}
        result = engine.render_template(template, context)
        assert '"key": "value"' in result

        # Test truncate_words filter
        template = "{{ text | truncate_words(3) }}"
        context = {"text": "This is a long text that should be truncated"}
        result = engine.render_template(template, context)
        assert result == "This is a..."

    def test_template_validation(self):
        """Test template validation functionality."""
        engine = TemplateEngine()

        # Valid template
        valid_result = engine.validate_template("Hello {{ name }}!")
        assert valid_result['valid'] is True
        assert len(valid_result['errors']) == 0

        # Invalid template
        invalid_result = engine.validate_template("Hello {{ name")
        assert invalid_result['valid'] is False
        assert len(invalid_result['errors']) > 0

    def test_model_specific_formatting(self):
        """Test model-specific formatting."""
        engine = TemplateEngine()
        content = "Test content"

        # Test Claude formatting
        claude_result = engine.render_with_model_format(content, "claude")
        assert "<thinking>" in claude_result

        # Test GPT formatting
        gpt_result = engine.render_with_model_format(content, "gpt")
        assert "System:" in gpt_result

        # Test Gemini formatting
        gemini_result = engine.render_with_model_format(content, "gemini")
        assert "Instructions:" in gemini_result


class TestCacheManager:
    """Test CacheManager functionality."""

    def test_basic_cache_operations(self):
        """Test basic cache get/set operations."""
        cache = CacheManager(max_size=10, ttl=3600)

        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test non-existent key
        assert cache.get("nonexistent") is None

        # Test cache stats
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hit_count'] == 1
        assert stats['miss_count'] == 1

    def test_cache_eviction(self):
        """Test LRU cache eviction."""
        cache = CacheManager(max_size=2, ttl=3600)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Add third item (should evict key1)
        cache.set("key3", "value3")

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_key_generation(self):
        """Test cache key generation."""
        cache = CacheManager()

        # Test consistent key generation
        key1 = cache.get_cache_key("task", 1, {"param": "value"})
        key2 = cache.get_cache_key("task", 1, {"param": "value"})
        assert key1 == key2

        # Test different keys for different contexts
        key3 = cache.get_cache_key("task", 1, {"param": "different"})
        assert key1 != key3

    def test_memory_efficient_cache(self):
        """Test memory-efficient cache implementation."""
        cache = MemoryEfficientCache(max_memory_mb=1)

        # Test basic operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test memory management (this is approximate)
        large_value = "x" * 1000000  # 1MB string
        cache.set("large_key", large_value)

        # Should still work within memory limits
        assert cache.get("large_key") == large_value


class TestValidationEngine:
    """Test ValidationEngine functionality."""

    def setup_method(self):
        """Set up test database mock."""
        self.db_mock = Mock()
        self.validator = ValidationEngine(self.db_mock)

    def test_template_validation(self):
        """Test template syntax validation."""
        # Mock database responses
        self.db_mock.execute_query.side_effect = [
            # Semantic rules
            [{'id': 1, 'name': 'test_semantic', 'content_template': 'Hello {{ name }}!'}],
            # Task rules
            [{'id': 1, 'name': 'test_task', 'prompt_template': 'Task: {{ task }}'}]
        ]

        # This should not raise any errors
        self.validator._check_template_validity()

        # Check that no errors were added
        assert len(self.validator.errors) == 0

    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        # Mock a simple dependency graph
        self.db_mock.execute_query.side_effect = [
            # Semantic-primitive relations (empty for this test)
            [],
            # Task-semantic relations (empty for this test)
            []
        ]

        cycles = self.validator.detect_circular_dependencies()
        assert isinstance(cycles, list)


class TestRuleResolver:
    """Test RuleResolver functionality."""

    def setup_method(self):
        """Set up test database mock."""
        self.db_mock = Mock()
        self.cache_mock = Mock()
        self.resolver = RuleResolver(self.db_mock, self.cache_mock)

    def test_task_rule_resolution(self):
        """Test task rule resolution."""
        # Mock database responses
        self.db_mock.execute_query.side_effect = [
            # Task rule
            [{'id': 1, 'name': 'test_task', 'prompt_template': 'Task: {{ task }}'}],
            # Semantic rules for task
            [{'id': 1, 'name': 'test_semantic', 'content_template': 'Semantic: {{ content }}'}],
            # Primitive rules for semantic
            [{'id': 1, 'name': 'test_primitive', 'content': 'Primitive content'}]
        ]

        # Mock cache miss
        self.cache_mock.get.return_value = None

        result = self.resolver.resolve_task_rule(1, {"task": "test"})

        assert result['task_rule']['name'] == 'test_task'
        assert len(result['semantic_rules']) == 1
        assert result['context'] == {"task": "test"}

    def test_dependency_resolution(self):
        """Test rule dependency resolution."""
        # Mock database responses for dependencies
        self.db_mock.execute_query.side_effect = [
            # Semantic rules for task
            [{'id': 1, 'name': 'semantic1', 'weight': 1.0}],
            # Primitive rules for semantic
            [{'id': 1, 'name': 'primitive1', 'weight': 1.0}]
        ]

        dependencies = self.resolver.get_rule_dependencies('task', 1)

        assert isinstance(dependencies, list)
        # Should have both semantic and primitive dependencies
        assert len(dependencies) >= 1


class TestRuleExporter:
    """Test RuleExporter functionality."""

    def setup_method(self):
        """Set up test database mock."""
        self.db_mock = Mock()
        self.exporter = RuleExporter(self.db_mock)

    def test_json_export(self):
        """Test JSON export functionality."""
        # Mock database responses
        self.db_mock.execute_query.side_effect = [
            # Primitive rules
            [{'id': 1, 'name': 'test_primitive', 'content': 'Test content'}],
            # Semantic rules
            [{'id': 1, 'name': 'test_semantic', 'content_template': 'Test template'}],
            # Task rules
            [{'id': 1, 'name': 'test_task', 'prompt_template': 'Test prompt'}],
            # Semantic-primitive relations
            [{'id': 1, 'semantic_rule_id': 1, 'primitive_rule_id': 1}],
            # Task-semantic relations
            [{'id': 1, 'task_rule_id': 1, 'semantic_rule_id': 1}]
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.exporter.export_rules(tmp_path, ['primitive', 'semantic', 'task'], 'json')

            assert result['success'] is True
            assert result['format'] == 'json'
            assert Path(tmp_path).exists()

            # Verify file content
            with open(tmp_path, 'r') as f:
                data = json.load(f)
                assert 'rules' in data
                assert 'primitive' in data['rules']
                assert 'semantic' in data['rules']
                assert 'task' in data['rules']

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_backup_creation(self):
        """Test database backup creation."""
        # Mock database connection
        conn_mock = Mock()
        conn_mock.iterdump.return_value = ["CREATE TABLE test;", "INSERT INTO test VALUES (1);"]

        # Mock context manager
        self.db_mock.get_connection.return_value.__enter__.return_value = conn_mock
        self.db_mock.get_connection.return_value.__exit__.return_value = None

        # Mock stats query
        self.db_mock.execute_query.return_value = [{'count': 1}]

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.exporter.backup_database(tmp_path)

            assert result['success'] is True
            assert Path(tmp_path).exists()
            assert result['backup_size'] > 0

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestRuleEngine:
    """Test main RuleEngine functionality."""

    def setup_method(self):
        """Set up test database mock."""
        self.db_mock = Mock()
        self.engine = RuleEngine(self.db_mock)

    def test_rule_engine_initialization(self):
        """Test rule engine initialization."""
        assert self.engine.db == self.db_mock
        assert self.engine.cache_manager is not None
        assert self.engine.resolver is not None
        assert self.engine.template_engine is not None
        assert self.engine.validation_engine is not None
        assert self.engine.exporter is not None

    def test_system_validation(self):
        """Test system validation."""
        # Mock validation responses
        self.db_mock.execute_query.side_effect = [
            # Primitive rules
            [{'id': 1, 'name': 'test', 'content': 'test', 'category': 'instruction'}],
            # Semantic rules
            [{'id': 1, 'name': 'test', 'content_template': 'test'}],
            # Task rules
            [{'id': 1, 'name': 'test', 'prompt_template': 'test'}],
            # Semantic-primitive relations
            [{'id': 1, 'semantic_rule_id': 1, 'primitive_rule_id': 1, 'semantic_name': 'test', 'primitive_name': 'test'}],
            # Task-semantic relations
            [{'id': 1, 'task_rule_id': 1, 'semantic_rule_id': 1, 'task_name': 'test', 'semantic_name': 'test'}],
            # Circular dependency check - semantic_primitive_relations
            [],
            # Circular dependency check - task_semantic_relations
            [],
            # Conflicts check - primitive_rules
            [],
            # Conflicts check - semantic_rules
            [],
            # Conflicts check - task_rules
            [],
            # System stats
            [{'count': 1}], [{'count': 1}], [{'count': 1}], [{'count': 1}], [{'count': 1}]
        ]

        result = self.engine.validate_system()

        assert 'validation' in result
        assert 'conflicts' in result
        assert 'cache' in result
        assert 'system' in result
        assert 'performance' in result

    def test_prompt_generation_flow(self):
        """Test end-to-end prompt generation."""
        # Mock task rule lookup
        self.db_mock.execute_query.side_effect = [
            # Task rule by name
            [{'id': 1, 'name': 'test_task', 'prompt_template': 'Task: {{ semantic_content }}'}],
            # Task rule by ID
            [{'id': 1, 'name': 'test_task', 'prompt_template': 'Task: {{ semantic_content }}'}],
            # Semantic rules for task
            [{'id': 1, 'name': 'test_semantic', 'content_template': 'Semantic: {{ primitive_content }}'}],
            # Primitive rules for semantic
            [{'id': 1, 'name': 'test_primitive', 'content': 'Primitive content'}]
        ]

        # Mock cache miss
        self.engine.cache_manager.get = Mock(return_value=None)
        self.engine.cache_manager.set = Mock()

        result = self.engine.generate_prompt('test_task', {'var': 'value'})

        assert 'prompt' in result
        assert 'raw_prompt' in result
        assert 'task_rule' in result
        assert 'context' in result
        assert result['target_model'] == 'claude'
        assert result['context']['var'] == 'value'


# Integration tests
class TestRuleEngineIntegration:
    """Integration tests for rule engine components."""

    def test_full_pipeline_with_real_templates(self):
        """Test the full pipeline with realistic templates."""
        # Mock database with realistic data
        db_mock = Mock()

        # Mock realistic rule data
        task_rule = {
            'id': 1,
            'name': 'code_review_task',
            'prompt_template': '''
# Code Review Task

{{ semantic_content }}

## Additional Context
- Language: {{ language }}
- Framework: {{ framework }}
'''
        }

        semantic_rule = {
            'id': 1,
            'name': 'code_review_semantic',
            'content_template': '''
## Code Review Guidelines

{{ primitive_content }}

Focus on: {{ focus_areas | join(', ') }}
'''
        }

        primitive_rule = {
            'id': 1,
            'name': 'code_quality_primitive',
            'content': 'Check for code quality, performance, and security issues.'
        }

        # Set up mock responses
        db_mock.execute_query.side_effect = [
            [task_rule],  # Task rule by name
            [task_rule],  # Task rule by ID
            [semantic_rule],  # Semantic rules for task
            [primitive_rule]  # Primitive rules for semantic
        ]

        # Create engine and generate prompt
        engine = RuleEngine(db_mock)

        context = {
            'language': 'Python',
            'framework': 'Django',
            'focus_areas': ['security', 'performance', 'maintainability']
        }

        result = engine.generate_prompt('code_review_task', context)

        # Verify the generated prompt contains expected content
        assert 'Code Review Task' in result['prompt']
        assert 'Python' in result['prompt']
        assert 'Django' in result['prompt']
        assert 'security' in result['prompt']
        assert 'code quality' in result['prompt']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
