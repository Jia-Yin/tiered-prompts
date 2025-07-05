"""
AI Prompt Engineering System - MCP Server Package

This package provides MCP (Model Context Protocol) server implementation
that exposes the rule engine functionality to AI clients.

Main Components:
- server.py: Main MCP server implementation
- tools/: Individual tool implementations
- resources/: Resource providers
- prompts/: Prompt templates
- utils/: Utility functions
"""

from .server import MCPServer

__version__ = "0.1.0"
__author__ = "AI Prompt Engineering System"
__description__ = "MCP Server for AI Prompt Engineering System"

# Export main server class
__all__ = ["MCPServer"]
