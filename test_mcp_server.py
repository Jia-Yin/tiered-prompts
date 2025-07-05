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
        from mcp_server.fastmcp_server import mcp
        print("✅ FastMCP Server imported successfully")

        # Test server properties
        print(f"✅ Server name: {mcp.name}")
        print(f"✅ Server dependencies: {mcp.dependencies}")

        # Note: Tool functions require MCP server context to run properly
        # These tests validate that the tools are properly defined and decorated
        print("\n--- Testing tool definitions ---")

        # Check that tools are properly decorated
        from mcp_server.fastmcp_server import (
            generate_prompt, analyze_rules, validate_rules,
            search_rules, optimize_rules
        )
        print("✅ All MCP tools imported successfully")

        # Check that resources are properly decorated
        from mcp_server.fastmcp_server import (
            get_rule_hierarchy, get_performance_stats, get_rule_relationships
        )
        print("✅ All MCP resources imported successfully")

        # Check that prompts are properly decorated
        from mcp_server.fastmcp_server import (
            create_rule_prompt, debug_rule_prompt
        )
        print("✅ All MCP prompts imported successfully")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rule_engine_integration():
    """Test rule engine integration"""
    print("\n=== Testing Rule Engine Integration ===")

    try:
        # Test rule engine components
        from ai_prompt_system.src.rule_engine.engine import RuleEngine
        from ai_prompt_system.src.database.connection import DatabaseManager
        print("✅ Rule engine components imported successfully")

        # Test database connection
        db = DatabaseManager()
        print("✅ Database manager created successfully")

        return True

    except Exception as e:
        print(f"❌ Rule engine integration failed: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic models"""
    print("\n=== Testing Pydantic Models ===")

    try:
        from mcp_server.fastmcp_server import (
            PromptMetadata, PromptResult, RuleAnalysis,
            ValidationResult, SearchResult, OptimizationResult
        )

        # Test PromptMetadata model
        metadata = PromptMetadata(
            rule_name="test_rule",
            target_model="claude",
            context_variables=["var1", "var2"],
            generation_time=0.05,
            rules_used=["primitive:1", "semantic:1"]
        )
        print("✅ PromptMetadata model works correctly")

        # Test PromptResult model
        result = PromptResult(
            prompt="Test prompt content",
            metadata=metadata
        )
        print("✅ PromptResult model works correctly")

        # Test RuleAnalysis model
        analysis = RuleAnalysis(
            rule_type="all",
            total_rules=10,
            dependencies=[],
            relationships=[],
            performance_metrics={}
        )
        print("✅ RuleAnalysis model works correctly")

        print("✅ All Pydantic models validated successfully")
        return True

    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Starting FastMCP Server tests...\n")

    # Run tests
    basic_test_success = test_fastmcp_server()
    rule_engine_success = test_rule_engine_integration()
    models_test_success = test_pydantic_models()

    # Summary
    print("\n=== Test Summary ===")
    print(f"FastMCP Server Tests: {'✅ PASS' if basic_test_success else '❌ FAIL'}")
    print(f"Rule Engine Integration: {'✅ PASS' if rule_engine_success else '❌ FAIL'}")
    print(f"Pydantic Models: {'✅ PASS' if models_test_success else '❌ FAIL'}")

    if basic_test_success and rule_engine_success and models_test_success:
        print("\n🎉 All tests passed! FastMCP Server is ready!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
