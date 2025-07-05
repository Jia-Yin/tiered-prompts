#!/usr/bin/env python3
"""Simple test to verify basic functionality"""

print("Testing basic imports...")
import json
import logging
print("✅ Basic imports successful")

print("\nTesting MCP server import...")
try:
    import sys
    import os

    # Add the project root to the path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    from mcp_server.server import MCPServer
    print("✅ MCP Server imported successfully")

    # Create server instance
    server = MCPServer()
    print("✅ MCP Server instance created")

    # Test one simple method
    result = server.get_performance_stats()
    print("✅ Basic method call successful")
    print(f"Sample result: {result[:100]}...")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed!")
