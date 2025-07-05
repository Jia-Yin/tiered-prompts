#!/usr/bin/env python3
"""
Test script to verify virtual environment setup and MCP SDK availability.
"""

import sys
import subprocess
from pathlib import Path

def test_environment():
    """Test the virtual environment setup"""
    print("🧪 Testing Virtual Environment Setup")
    print("=" * 50)

    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment: ACTIVE")
    else:
        print("❌ Virtual environment: NOT ACTIVE")

    print("\n📦 Testing Package Imports")
    print("-" * 30)

    # Test MCP SDK import
    try:
        import mcp
        # Try to get version, fallback to "available" if no version attribute
        version = getattr(mcp, '__version__', 'available')
        print(f"✅ MCP SDK: {version}")
    except ImportError as e:
        print(f"❌ MCP SDK: {e}")
        return False
    except AttributeError:
        print("✅ MCP SDK: available (no version info)")

    # Test Pydantic import
    try:
        import pydantic
        print(f"✅ Pydantic: {pydantic.__version__}")
    except ImportError as e:
        print(f"❌ Pydantic: {e}")
        return False

    # Test rule engine imports
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from ai_prompt_system.src.rule_engine.engine import RuleEngine
        print("✅ Rule Engine: Available")
    except ImportError as e:
        print(f"⚠️  Rule Engine: {e} (will use mock mode)")

    print("\n🚀 Testing FastMCP Server Import")
    print("-" * 35)

    # Test FastMCP server import
    try:
        from mcp_server.fastmcp_server import mcp
        print("✅ FastMCP Server: Can be imported")
        print(f"✅ Server name: {mcp.name}")
        return True
    except ImportError as e:
        print(f"❌ FastMCP Server: {e}")
        return False

def main():
    """Main test function"""
    success = test_environment()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Environment setup: SUCCESS")
        print("\nNext steps:")
        print("1. source .venv/bin/activate")
        print("2. python mcp_server/fastmcp_server.py")
    else:
        print("❌ Environment setup: FAILED")
        print("\nPlease check the error messages above.")

    return success

if __name__ == "__main__":
    main()
