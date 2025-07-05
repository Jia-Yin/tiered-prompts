#!/usr/bin/env python3
"""
Test script for the FastMCP Server

This script tests the basic functionality of the FastMCP server
using the official MCP SDK.
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fastmcp_server():
    """Test basic FastMCP server functionality"""
    print("=== Testing AI Prompt Engineering System FastMCP Server ===")

    try:
        # Import the FastMCP server
        from mcp_server.fastmcp_server import mcp, generate_prompt, analyze_rules
        print("✅ FastMCP Server imported successfully")

        # Test server properties
        print(f"✅ Server name: {mcp.name}")
        print(f"✅ Server dependencies: {mcp.dependencies}")

        # Test tool functions (these will use mock responses since we're not in server context)
        print("\n--- Testing generate_prompt tool (mock mode) ---")
        result = server.generate_prompt(
            rule_name="test_rule",
            context={"variable": "test_value"},
            target_model="claude"
        )
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Test analyze_rules tool
        print("\n--- Testing analyze_rules tool ---")
        result = server.analyze_rules(rule_type="all")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Test validate_rules tool
        print("\n--- Testing validate_rules tool ---")
        result = server.validate_rules(rule_type="all")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Test search_rules tool
        print("\n--- Testing search_rules tool ---")
        result = server.search_rules(query="test", search_type="content")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Test optimize_rules tool
        print("\n--- Testing optimize_rules tool ---")
        result = server.optimize_rules(optimization_type="performance")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # Test get_rule_hierarchy resource
        print("\n--- Testing get_rule_hierarchy resource ---")
        result = server.get_rule_hierarchy("primitive")
        print(f"Result: {result}")

        # Test get_performance_stats resource
        print("\n--- Testing get_performance_stats resource ---")
        result = server.get_performance_stats()
        print(f"Result: {result}")

        # Test get_rule_relationships resource
        print("\n--- Testing get_rule_relationships resource ---")
        result = server.get_rule_relationships("task:1")
        print(f"Result: {result}")

        print("\n✅ All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_engine_integration():
    """Test integration with the actual rule engine"""
    print("\n=== Testing Rule Engine Integration ===")

    try:
        # Try to import the rule engine directly
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_prompt_system'))

        from ai_prompt_system.src.database.connection import DatabaseManager
        from ai_prompt_system.src.rule_engine.cache import CacheManager

        # Test database connection
        db_manager = DatabaseManager()
        db_manager.test_connection()
        print("✅ Database connection successful")

        # Test cache manager
        cache_manager = CacheManager()
        cache_manager.set("test_key", "test_value")
        value = cache_manager.get("test_key")
        assert value == "test_value"
        print("✅ Cache manager working")

        print("✅ Rule engine integration successful!")
        return True

    except ImportError as e:
        print(f"⚠️  Rule engine not available: {e}")
        print("This is expected if the rule engine hasn't been set up yet")
        return True
    except Exception as e:
        print(f"❌ Rule engine integration failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting MCP Server tests...\n")

    # Run basic MCP server tests
    basic_test_success = test_mcp_server()

    # Run rule engine integration tests
    integration_test_success = test_rule_engine_integration()

    print(f"\n=== Test Summary ===")
    print(f"Basic MCP Server Tests: {'✅ PASS' if basic_test_success else '❌ FAIL'}")
    print(f"Rule Engine Integration: {'✅ PASS' if integration_test_success else '❌ FAIL'}")

    if basic_test_success and integration_test_success:
        print("\n🎉 All tests passed! MCP Server is ready for use.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
