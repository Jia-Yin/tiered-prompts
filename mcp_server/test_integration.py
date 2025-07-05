#!/usr/bin/env python3
"""
Test script for MCP server integration.
This script verifies that the MCP server can start properly with uv.
"""

import os
import sys
import subprocess
import time
import signal

def test_uv_setup():
    """Test that uv is properly configured"""
    print("🔍 Testing uv setup...")

    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv version: {result.stdout.strip()}")
        else:
            print("❌ uv not found or not working")
            return False
    except FileNotFoundError:
        print("❌ uv command not found")
        return False

    return True

def test_dependencies():
    """Test that dependencies are installed"""
    print("🔍 Testing dependencies...")

    try:
        result = subprocess.run(['uv', 'run', 'python', '-c', 'import mcp; import pydantic; print("Dependencies OK")'],
                              capture_output=True, text=True, cwd='/home/jyw/Program/tiered-prompts/mcp_server')
        if result.returncode == 0:
            print("✅ All dependencies available")
            return True
        else:
            print(f"❌ Dependency error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def test_server_startup():
    """Test that the MCP server can start"""
    print("🔍 Testing MCP server startup...")

    try:
        # Start server in background
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'fastmcp_server.py'],
            cwd='/home/jyw/Program/tiered-prompts/mcp_server',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a bit for startup
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server started successfully")

            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def test_path_resolution():
    """Test that paths are correctly resolved"""
    print("🔍 Testing path resolution...")

    try:
        result = subprocess.run([
            'uv', 'run', 'python', '-c',
            '''
import os
project_root = os.environ.get("PROJECT_ROOT", "/home/jyw/Program/tiered-prompts")
db_path = os.path.join(project_root, "ai_prompt_system/database/prompt_system.db")
print(f"PROJECT_ROOT: {project_root}")
print(f"DB exists: {os.path.exists(db_path)}")
            '''
        ],
        capture_output=True, text=True,
        cwd='/home/jyw/Program/tiered-prompts/mcp_server',
        env={**os.environ, "PROJECT_ROOT": "/home/jyw/Program/tiered-prompts"}
        )

        if result.returncode == 0:
            print("✅ Path resolution working")
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Path resolution error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing paths: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting MCP Server Integration Tests")
    print("=" * 50)

    tests = [
        test_uv_setup,
        test_dependencies,
        test_path_resolution,
        test_server_startup,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! MCP server is ready for Claude Desktop integration.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
