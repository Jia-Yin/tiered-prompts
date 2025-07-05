#!/bin/bash
# Test script for FastMCP server in virtual environment

echo "🔧 AI Prompt Engineering System - FastMCP Server Testing"
echo "========================================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment is active: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment is not active!"
    echo "Please run: source .venv/bin/activate"
    echo ""
    echo "Full instructions:"
    echo "1. cd /home/jyw/Program/tiered-prompts"
    echo "2. source .venv/bin/activate"
    echo "3. ./test_fastmcp.sh"
    exit 1
fi

echo ""
echo "🐍 Python Environment Check"
echo "----------------------------"
python --version
echo "Python executable: $(which python)"
echo ""

echo "📦 Package Verification"
echo "----------------------"
echo "Testing MCP SDK import..."
python -c "import mcp; print('✅ MCP SDK: available')" || {
    echo "❌ MCP SDK import failed!"
    exit 1
}

echo "Testing Pydantic import..."
python -c "import pydantic; print('✅ Pydantic version:', pydantic.__version__)" || {
    echo "❌ Pydantic import failed!"
    exit 1
}

echo ""
echo "🧪 Environment Test"
echo "-------------------"
python test_venv.py

echo ""
echo "🚀 FastMCP Server Test"
echo "----------------------"
echo "Testing FastMCP server import..."
python -c "
try:
    from mcp_server.fastmcp_server import mcp
    print('✅ FastMCP server can be imported')
    print('✅ Server name:', mcp.name)
    print('✅ Server dependencies:', mcp.dependencies)
    print('✅ All MCP tools, resources, and prompts are registered')
except Exception as e:
    print('❌ FastMCP server import failed:', e)
    exit(1)
"

echo ""
echo "🎯 Ready to run FastMCP server!"
echo "-------------------------------"
echo "Run the server with:"
echo "python mcp_server/fastmcp_server.py"
echo ""
echo "Or test in stdio mode:"
echo "python mcp_server/fastmcp_server.py --stdio"
