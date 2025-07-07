"""
MCP Client Service
Handles communication with the MCP server
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, Optional, List
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClientService:
    """Service for communicating with MCP server"""
    
    def __init__(self):
        self.mcp_process: Optional[subprocess.Popen] = None
        self.connected = False
        self.mcp_server_path = Path(__file__).parent.parent.parent.parent.parent / "mcp_server"
        
    async def connect(self):
        """Connect to MCP server"""
        try:
            # Test if MCP HTTP wrapper is running
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8001/health", timeout=5.0)
                response.raise_for_status()
                
            self.connected = True
            logger.info("Connected to MCP server HTTP wrapper on port 8001")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
            finally:
                self.mcp_process = None
        
        self.connected = False
        logger.info("Disconnected from MCP server")
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self.connected
    
    async def _start_mcp_server(self):
        """Start MCP server process"""
        if self.mcp_process and self.mcp_process.poll() is None:
            logger.info("MCP server already running")
            return
        
        try:
            # Start MCP server in background
            server_script = self.mcp_server_path / "fastmcp_server.py"
            
            if not server_script.exists():
                raise FileNotFoundError(f"MCP server script not found: {server_script}")
            
            # Start server process
            self.mcp_process = subprocess.Popen(
                ["python", str(server_script)],
                cwd=str(self.mcp_server_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            if self.mcp_process.poll() is not None:
                stdout, stderr = self.mcp_process.communicate()
                raise RuntimeError(f"MCP server failed to start. Error: {stderr}")
            
            logger.info("MCP server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # Use HTTP to communicate with MCP server
            # The MCP server should expose HTTP endpoints for tools
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8001/tools/{tool_name}",
                    json=arguments,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"HTTP error calling MCP tool {tool_name}: {e}")
            # Fall back to mock response for development
            logger.warning(f"Falling back to mock response for {tool_name}")
            return await self._mock_mcp_call(tool_name, arguments)
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            # Fall back to mock response
            return await self._mock_mcp_call(tool_name, arguments)
    
    async def get_mcp_resource(self, resource_uri: str) -> str:
        """Get an MCP resource"""
        if not self.is_connected():
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # Use HTTP to communicate with MCP server for resources
            # Convert resource URI to proper path format
            if resource_uri.startswith("rules://"):
                rule_type = resource_uri.replace("rules://", "")
                url = f"http://localhost:8001/resources/rules/{rule_type}"
            elif resource_uri.startswith("stats://"):
                stat_type = resource_uri.replace("stats://", "")
                url = f"http://localhost:8001/resources/stats/{stat_type}"
            elif resource_uri.startswith("relationships://"):
                rule_id = resource_uri.replace("relationships://", "")
                url = f"http://localhost:8001/resources/relationships/{rule_id}"
            else:
                url = f"http://localhost:8001/resources/{resource_uri}"
                
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return json.dumps(data.get("data", {}), indent=2)
                
        except httpx.RequestError as e:
            logger.error(f"HTTP error getting MCP resource {resource_uri}: {e}")
            # Fall back to mock response for development
            logger.warning(f"Falling back to mock response for {resource_uri}")
            return await self._mock_resource_call(resource_uri)
        except Exception as e:
            logger.error(f"Error getting MCP resource {resource_uri}: {e}")
            # Fall back to mock response
            return await self._mock_resource_call(resource_uri)
    
    async def _mock_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock MCP tool calls for development"""
        mock_responses = {
            "generate_prompt": {
                "prompt": f"# Generated Prompt\\n\\nThis is a mock prompt for testing.\\nTool: {tool_name}\\nArguments: {arguments}",
                "metadata": {
                    "rule_name": arguments.get("rule_name", "test_rule"),
                    "target_model": arguments.get("target_model", "claude"),
                    "context_variables": list(arguments.get("context", {}).keys()),
                    "generation_time": 0.05,
                    "rules_used": ["primitive:1", "semantic:1", "task:1"]
                }
            },
            "analyze_rules": {
                "rule_type": arguments.get("rule_type", "all"),
                "total_rules": 25,
                "dependencies": [
                    {"rule_id": 1, "depends_on": [2, 3], "type": "primitive"},
                    {"rule_id": 2, "depends_on": [], "type": "semantic"}
                ],
                "relationships": [
                    {"from": "primitive:1", "to": "semantic:1", "type": "enhances"},
                    {"from": "semantic:1", "to": "task:1", "type": "implements"}
                ],
                "performance_metrics": {
                    "average_resolution_time": 0.05,
                    "cache_hit_rate": 0.85,
                    "total_resolutions": 1247
                }
            },
            "validate_rules": {
                "valid": True,
                "issues": [],
                "warnings": [
                    {"rule_id": "semantic:3", "message": "Template variable 'user_name' not defined in context"}
                ],
                "suggestions": [
                    {"rule_id": "task:1", "message": "Consider adding fallback for missing context variables"}
                ]
            },
            "search_rules": {
                "query": arguments.get("query", ""),
                "results": [
                    {
                        "rule_id": 1,
                        "name": "clear_formatting",
                        "type": "primitive",
                        "content": "Use clear headings and bullet points",
                        "relevance": 0.95
                    },
                    {
                        "rule_id": 5,
                        "name": "user_friendly_tone",
                        "type": "semantic",
                        "content": "Maintain professional but friendly tone",
                        "relevance": 0.78
                    }
                ],
                "total_found": 2,
                "search_time": 0.003
            },
            "optimize_rules": {
                "optimization_type": arguments.get("optimization_type", "performance"),
                "suggestions": [
                    {
                        "rule_id": "task:3",
                        "suggestion": "Combine similar formatting rules to reduce redundancy",
                        "impact": "Medium",
                        "effort": "Low"
                    }
                ],
                "potential_improvements": [
                    {
                        "metric": "generation_time",
                        "current": 0.15,
                        "potential": 0.08,
                        "improvement": "47%"
                    }
                ],
                "priority_score": 7.8
            },
            "create_primitive_rule": {
                "success": True,
                "rule_id": 999,
                "message": "Rule created successfully (mock)"
            },
            "create_semantic_rule": {
                "success": True,
                "rule_id": 999,
                "message": "Rule created successfully (mock)"
            },
            "create_task_rule": {
                "success": True,
                "rule_id": 999,
                "message": "Rule created successfully (mock)"
            },
            "update_primitive_rule": {
                "success": True,
                "message": "Rule updated successfully (mock)"
            },
            "update_semantic_rule": {
                "success": True,
                "message": "Rule updated successfully (mock)"
            },
            "update_task_rule": {
                "success": True,
                "message": "Rule updated successfully (mock)"
            },
            "delete_primitive_rule": {
                "success": True,
                "message": "Rule deleted successfully (mock)"
            },
            "delete_semantic_rule": {
                "success": True,
                "message": "Rule deleted successfully (mock)"
            },
            "delete_task_rule": {
                "success": True,
                "message": "Rule deleted successfully (mock)"
            }
        }
        
        return mock_responses.get(tool_name, {"error": f"Unknown tool: {tool_name}"})
    
    async def _mock_resource_call(self, resource_uri: str) -> str:
        """Mock MCP resource calls for development"""
        mock_resources = {
            "rules://primitive": json.dumps({
                "rule_type": "primitive",
                "rules": [
                    {"id": 1, "name": "clear_formatting", "content": "Use clear headings and bullet points"},
                    {"id": 2, "name": "concise_language", "content": "Use simple, direct language"}
                ],
                "total_rules": 2
            }, indent=2),
            "rules://semantic": json.dumps({
                "rule_type": "semantic",
                "rules": [
                    {"id": 1, "name": "professional_tone", "content": "Maintain {{tone}} throughout {{context}}"},
                    {"id": 2, "name": "code_review_style", "content": "Focus on {{criteria}} when reviewing {{code}}"}
                ],
                "total_rules": 2
            }, indent=2),
            "rules://task": json.dumps({
                "rule_type": "task",
                "rules": [
                    {"id": 1, "name": "react_component_review", "content": "Review React component {{component}} for {{criteria}}"},
                    {"id": 2, "name": "documentation_writer", "content": "Write documentation for {{feature}} using {{style}}"}
                ],
                "total_rules": 2
            }, indent=2),
            "stats://performance": json.dumps({
                "system_stats": {
                    "total_rules": 47,
                    "total_prompts_generated": 1523,
                    "average_generation_time": 0.12,
                    "cache_hit_rate": 0.87,
                    "uptime_hours": 168.5
                },
                "rule_stats": {
                    "primitive_rules": 15,
                    "semantic_rules": 18,
                    "task_rules": 14
                }
            }, indent=2)
        }
        
        return mock_resources.get(resource_uri, json.dumps({"error": f"Unknown resource: {resource_uri}"}, indent=2))