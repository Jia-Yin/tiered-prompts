#!/usr/bin/env python3
"""
Simple integration test for Phase 2 Rule Engine implementation.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_template_engine():
    """Test basic template engine functionality."""
    print("Testing TemplateEngine...")

    try:
        from src.rule_engine.template import TemplateEngine

        engine = TemplateEngine()

        # Test basic rendering
        result = engine.render_template("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!", f"Expected 'Hello World!', got '{result}'"

        # Test template validation
        validation = engine.validate_template("Hello {{ name }}!")
        assert validation['valid'] == True, "Template should be valid"

        # Test model formatting
        formatted = engine.render_with_model_format("Test content", "claude")
        assert "<thinking>" in formatted, "Claude formatting should include <thinking>"

        print("✓ TemplateEngine tests passed")
        return True

    except Exception as e:
        print(f"✗ TemplateEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_manager():
    """Test cache manager functionality."""
    print("Testing CacheManager...")

    try:
        from src.rule_engine.cache import CacheManager

        cache = CacheManager(max_size=10, ttl=3600)

        # Test basic operations
        cache.set("key1", "value1")
        result = cache.get("key1")
        assert result == "value1", f"Expected 'value1', got '{result}'"

        # Test cache key generation
        key = cache.get_cache_key("task", 1, {"param": "value"})
        assert isinstance(key, str), "Cache key should be a string"

        # Test stats
        stats = cache.get_stats()
        assert "hit_count" in stats, "Stats should include hit_count"

        print("✓ CacheManager tests passed")
        return True

    except Exception as e:
        print(f"✗ CacheManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_engine():
    """Test validation engine functionality."""
    print("Testing ValidationEngine...")

    try:
        from src.rule_engine.validation import ValidationEngine
        from unittest.mock import Mock

        # Create mock database
        db_mock = Mock()
        db_mock.execute_query.return_value = []

        validator = ValidationEngine(db_mock)

        # Test circular dependency detection
        cycles = validator.detect_circular_dependencies()
        assert isinstance(cycles, list), "Cycles should be a list"

        # Test consistency check
        result = validator.check_consistency()
        assert "valid" in result, "Result should include 'valid' field"
        assert "errors" in result, "Result should include 'errors' field"

        print("✓ ValidationEngine tests passed")
        return True

    except Exception as e:
        print(f"✗ ValidationEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_resolver():
    """Test rule resolver functionality."""
    print("Testing RuleResolver...")

    try:
        from src.rule_engine.resolver import RuleResolver
        from src.rule_engine.cache import CacheManager
        from unittest.mock import Mock

        # Create mocks
        db_mock = Mock()
        cache_mock = CacheManager()

        resolver = RuleResolver(db_mock, cache_mock)

        # Test initialization
        assert resolver.db == db_mock, "Database should be set"
        assert resolver.cache_manager == cache_mock, "Cache manager should be set"

        print("✓ RuleResolver tests passed")
        return True

    except Exception as e:
        print(f"✗ RuleResolver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_engine():
    """Test main rule engine functionality."""
    print("Testing RuleEngine...")

    try:
        from src.rule_engine.engine import RuleEngine
        from unittest.mock import Mock

        # Create mock database
        db_mock = Mock()

        engine = RuleEngine(db_mock)

        # Test initialization
        assert engine.db == db_mock, "Database should be set"
        assert engine.cache_manager is not None, "Cache manager should be initialized"
        assert engine.resolver is not None, "Resolver should be initialized"
        assert engine.template_engine is not None, "Template engine should be initialized"
        assert engine.validation_engine is not None, "Validation engine should be initialized"

        print("✓ RuleEngine tests passed")
        return True

    except Exception as e:
        print(f"✗ RuleEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Phase 2: Core Rule Engine - Integration Tests")
    print("=" * 50)

    tests = [
        test_template_engine,
        test_cache_manager,
        test_validation_engine,
        test_rule_resolver,
        test_rule_engine
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Phase 2 implementation is working.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
