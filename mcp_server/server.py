"""
AI Prompt Engineering System - MCP Server

This module implements an MCP (Model Context Protocol) server that exposes
the rule engine functionality to AI clients. The server provides tools for
prompt generation, rule analysis, validation, and optimization.

Based on Phase 2 rule engine and following Phase 3 implementation plan.

Note: This is a simplified implementation that works without the full MCP SDK
for now. We'll enhance it with proper MCP SDK integration later.
"""

import asyncio
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import our existing rule engine components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ai_prompt_system.src.rule_engine.engine import RuleEngine
    from ai_prompt_system.src.rule_engine.resolver import RuleResolver
    from ai_prompt_system.src.rule_engine.validation import ValidationEngine
    from ai_prompt_system.src.rule_engine.cache import CacheManager
    from ai_prompt_system.src.database.connection import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import rule engine components: {e}")
    print("This is a placeholder implementation for MCP server development.")
    RuleEngine = None
    RuleResolver = None
    ValidationEngine = None
    CacheManager = None
    DatabaseManager = None

"""
AI Prompt Engineering System - MCP Server

This module implements an MCP (Model Context Protocol) server that exposes
the rule engine functionality to AI clients. The server provides tools for
prompt generation, rule analysis, validation, and optimization.

Based on Phase 2 rule engine and following Phase 3 implementation plan.

Note: This is a simplified implementation that works without the full MCP SDK
for now. We'll enhance it with proper MCP SDK integration later.
"""

import asyncio
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import our existing rule engine components
import sys
import os

# Add the project root to the path to find ai_prompt_system
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from ai_prompt_system.src.rule_engine.engine import RuleEngine
    from ai_prompt_system.src.rule_engine.resolver import RuleResolver
    from ai_prompt_system.src.rule_engine.validation import ValidationEngine
    from ai_prompt_system.src.rule_engine.cache import CacheManager
    from ai_prompt_system.src.database.connection import DatabaseManager
    RULE_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import rule engine components: {e}")
    print("This is a placeholder implementation for MCP server development.")
    RULE_ENGINE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerContext:
    """MCP server context containing initialized services"""
    rule_engine: Any = None
    db_manager: Any = None
    cache_manager: Any = None

class MCPServer:
    """
    Simplified MCP Server implementation

    This provides the core MCP server functionality without requiring
    the full FastMCP framework. It implements the essential tools and
    resources needed for the AI Prompt Engineering System.
    """

    def __init__(self):
        self.context = ServerContext()
        self._initialize_services()

    def _initialize_services(self):
        """Initialize rule engine services if available"""
        if RULE_ENGINE_AVAILABLE:
            try:
                # Initialize database manager
                self.context.db_manager = DatabaseManager()

                # Initialize cache manager
                self.context.cache_manager = CacheManager()

                # Initialize rule engine with dependency injection
                self.context.rule_engine = RuleEngine(
                    db_manager=self.context.db_manager,
                    cache_manager=self.context.cache_manager
                )

                # Test database connection
                self.context.db_manager.test_connection()
                logger.info("Rule engine services initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize rule engine services: {e}")
                RULE_ENGINE_AVAILABLE = False
        else:
            logger.warning("Rule engine services not available - using mock implementation")

    # ============================================================================
    # MCP TOOLS - Actions that LLMs can perform
    # ============================================================================

    def generate_prompt(
        self,
        rule_name: str,
        context: Optional[Dict[str, Any]] = None,
        target_model: str = "claude"
    ) -> Dict[str, Any]:
        """
        Generate a complete prompt from rule hierarchy.

        Args:
            rule_name: Name of the task rule to generate prompt for
            context: Optional context variables for template rendering
            target_model: Target AI model (claude, gpt, gemini)

        Returns:
            Generated prompt with metadata
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                return {
                    "success": False,
                    "error": "Rule engine not available",
                    "mock_response": {
                        "prompt": f"Mock prompt for {rule_name} targeting {target_model}",
                        "metadata": {
                            "rule_name": rule_name,
                            "target_model": target_model,
                            "context_variables": list(context.keys()) if context else [],
                            "generation_time": 0.01,
                            "rules_used": ["mock_rule"]
                        }
                    }
                }

            # Generate the prompt using rule engine
            result = self.context.rule_engine.generate_prompt(
                rule_name=rule_name,
                context=context or {},
                model=target_model
            )

            return {
                "success": True,
                "prompt": result["prompt"],
                "metadata": {
                    "rule_name": rule_name,
                    "target_model": target_model,
                    "context_variables": list(context.keys()) if context else [],
                    "generation_time": result.get("generation_time", 0),
                    "rules_used": result.get("rules_used", [])
                }
            }

        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return {
                "success": False,
                "error": str(e),
                "rule_name": rule_name
            }

    def analyze_rules(
        self,
        rule_type: str = "all",
        include_dependencies: bool = True,
        rule_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze rules and their dependencies.

        Args:
            rule_type: Type of rules to analyze (primitive, semantic, task, all)
            include_dependencies: Whether to include dependency analysis
            rule_id: Specific rule ID to analyze (optional)

        Returns:
            Analysis results with dependencies and relationships
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                return {
                    "success": False,
                    "error": "Rule engine not available",
                    "mock_response": {
                        "analysis": {
                            "rule_count": 10,
                            "dependencies": ["mock_dependency"],
                            "relationships": {"parent": [], "children": []},
                            "analysis_time": 0.01
                        }
                    }
                }

            # Get analysis from rule engine
            analysis = self.context.rule_engine.analyze_rules(
                rule_type=rule_type,
                include_dependencies=include_dependencies,
                rule_id=rule_id
            )

            return {
                "success": True,
                "analysis": analysis,
                "metadata": {
                    "rule_type": rule_type,
                    "include_dependencies": include_dependencies,
                    "rule_id": rule_id,
                    "analysis_time": analysis.get("analysis_time", 0)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing rules: {e}")
            return {
                "success": False,
                "error": str(e),
                "rule_type": rule_type
            }

    def validate_rules(
        self,
        rule_type: str = "all",
        rule_id: Optional[int] = None,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Validate rule consistency and integrity.

        Args:
            rule_type: Type of rules to validate (primitive, semantic, task, all)
            rule_id: Specific rule ID to validate (optional)
            detailed: Whether to provide detailed validation results

        Returns:
            Validation results with any issues found
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                return {
                    "success": False,
                    "error": "Rule engine not available",
                    "mock_response": {
                        "validation": {
                            "valid": True,
                            "issues": [],
                            "warnings": ["Mock validation warning"],
                            "validation_time": 0.01
                        }
                    }
                }

            # Validate rules using rule engine
            validation_results = self.context.rule_engine.validate_rules(
                rule_type=rule_type,
                rule_id=rule_id,
                detailed=detailed
            )

            return {
                "success": True,
                "validation": validation_results,
                "metadata": {
                    "rule_type": rule_type,
                    "rule_id": rule_id,
                    "detailed": detailed,
                    "validation_time": validation_results.get("validation_time", 0)
                }
            }

        except Exception as e:
            logger.error(f"Error validating rules: {e}")
            return {
                "success": False,
                "error": str(e),
                "rule_type": rule_type
            }

    def search_rules(
        self,
        query: str,
        search_type: str = "content",
        rule_type: str = "all",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search rules by content, name, or metadata.

        Args:
            query: Search query string
            search_type: Type of search (content, name, metadata)
            rule_type: Type of rules to search (primitive, semantic, task, all)
            limit: Maximum number of results to return

        Returns:
            Search results with matching rules
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                return {
                    "success": False,
                    "error": "Rule engine not available",
                    "mock_response": {
                        "results": [
                            {
                                "id": 1,
                                "name": f"mock_rule_matching_{query}",
                                "type": "primitive",
                                "content": f"Mock rule content containing {query}",
                                "score": 0.95
                            }
                        ],
                        "metadata": {
                            "query": query,
                            "search_type": search_type,
                            "rule_type": rule_type,
                            "limit": limit,
                            "result_count": 1
                        }
                    }
                }

            # Search rules using rule engine
            search_results = self.context.rule_engine.search_rules(
                query=query,
                search_type=search_type,
                rule_type=rule_type,
                limit=limit
            )

            return {
                "success": True,
                "results": search_results,
                "metadata": {
                    "query": query,
                    "search_type": search_type,
                    "rule_type": rule_type,
                    "limit": limit,
                    "result_count": len(search_results.get("results", []))
                }
            }

        except Exception as e:
            logger.error(f"Error searching rules: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def optimize_rules(
        self,
        optimization_type: str = "performance",
        rule_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Analyze and suggest rule optimizations.

        Args:
            optimization_type: Type of optimization (performance, structure, content)
            rule_type: Type of rules to optimize (primitive, semantic, task, all)

        Returns:
            Optimization suggestions and recommendations
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                return {
                    "success": False,
                    "error": "Rule engine not available",
                    "mock_response": {
                        "optimization": {
                            "suggestions": [
                                {
                                    "type": "performance",
                                    "description": "Mock optimization suggestion",
                                    "impact": "medium",
                                    "effort": "low"
                                }
                            ],
                            "metadata": {
                                "optimization_type": optimization_type,
                                "rule_type": rule_type,
                                "suggestions_count": 1
                            }
                        }
                    }
                }

            # Get optimization suggestions from rule engine
            optimization_results = self.context.rule_engine.optimize_rules(
                optimization_type=optimization_type,
                rule_type=rule_type
            )

            return {
                "success": True,
                "optimization": optimization_results,
                "metadata": {
                    "optimization_type": optimization_type,
                    "rule_type": rule_type,
                    "suggestions_count": len(optimization_results.get("suggestions", []))
                }
            }

        except Exception as e:
            logger.error(f"Error optimizing rules: {e}")
            return {
                "success": False,
                "error": str(e),
                "optimization_type": optimization_type
            }

    # ============================================================================
    # MCP RESOURCES - Data sources that LLMs can access
    # ============================================================================

    def get_rule_hierarchy(self, rule_type: str) -> str:
        """
        Get rule hierarchy for a specific type.

        Args:
            rule_type: Type of rules (primitive, semantic, task)

        Returns:
            JSON representation of rule hierarchy
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                mock_hierarchy = {
                    "rule_type": rule_type,
                    "rules": [
                        {
                            "id": 1,
                            "name": f"mock_{rule_type}_rule",
                            "content": f"Mock {rule_type} rule content",
                            "dependencies": []
                        }
                    ],
                    "relationships": [],
                    "metadata": {
                        "total_rules": 1,
                        "last_updated": "2025-01-05"
                    }
                }
                return json.dumps(mock_hierarchy, indent=2, ensure_ascii=False)

            # Get hierarchy from rule engine
            hierarchy = self.context.rule_engine.get_rule_hierarchy(rule_type)

            return json.dumps(hierarchy, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error getting rule hierarchy: {e}")
            return json.dumps({"error": str(e), "rule_type": rule_type})

    def get_performance_stats(self) -> str:
        """
        Get system performance statistics.

        Returns:
            JSON representation of performance metrics
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                mock_stats = {
                    "performance": {
                        "average_response_time": 0.05,
                        "cache_hit_rate": 0.85,
                        "total_requests": 100,
                        "memory_usage": "15MB",
                        "uptime": "2 hours"
                    },
                    "rules": {
                        "total_rules": 15,
                        "active_rules": 12,
                        "most_used_rules": ["mock_rule_1", "mock_rule_2"]
                    },
                    "timestamp": "2025-01-05T10:00:00Z"
                }
                return json.dumps(mock_stats, indent=2)

            # Get performance stats from rule engine
            stats = self.context.rule_engine.get_performance_stats()

            return json.dumps(stats, indent=2)

        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return json.dumps({"error": str(e)})

    def get_rule_relationships(self, rule_id: str) -> str:
        """
        Get relationships for a specific rule.

        Args:
            rule_id: ID of the rule (format: type:id, e.g., "task:1")

        Returns:
            JSON representation of rule relationships
        """
        try:
            if not RULE_ENGINE_AVAILABLE or not self.context.rule_engine:
                mock_relationships = {
                    "rule_id": rule_id,
                    "relationships": {
                        "parents": [
                            {"id": "semantic:1", "name": "mock_semantic_rule", "weight": 1.0}
                        ],
                        "children": [
                            {"id": "primitive:1", "name": "mock_primitive_rule", "weight": 0.8}
                        ]
                    },
                    "dependency_depth": 2,
                    "total_dependencies": 2
                }
                return json.dumps(mock_relationships, indent=2, ensure_ascii=False)

            # Parse rule_id format (type:id)
            if ":" in rule_id:
                rule_type, rule_id_num = rule_id.split(":", 1)
                rule_id_num = int(rule_id_num)
            else:
                return json.dumps({"error": "Invalid rule_id format. Use 'type:id' (e.g., 'task:1')"})

            # Get relationships from rule engine
            relationships = self.context.rule_engine.get_rule_relationships(rule_id_num, rule_type)

            return json.dumps(relationships, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error getting rule relationships: {e}")
            return json.dumps({"error": str(e), "rule_id": rule_id})

    # ============================================================================
    # CLI INTERFACE FOR TESTING
    # ============================================================================

    def run_cli(self):
        """Run CLI interface for testing MCP server functionality"""
        print("=== AI Prompt Engineering System MCP Server ===")
        print("Available commands:")
        print("1. generate_prompt <rule_name> [context] [model]")
        print("2. analyze_rules [rule_type] [include_deps] [rule_id]")
        print("3. validate_rules [rule_type] [rule_id] [detailed]")
        print("4. search_rules <query> [search_type] [rule_type] [limit]")
        print("5. optimize_rules [optimization_type] [rule_type]")
        print("6. get_hierarchy <rule_type>")
        print("7. get_stats")
        print("8. get_relationships <rule_id>")
        print("9. help")
        print("10. exit")
        print()

        while True:
            try:
                command = input("> ").strip().split()
                if not command:
                    continue

                cmd = command[0].lower()

                if cmd == "exit":
                    break
                elif cmd == "help":
                    print("Available commands: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules, get_hierarchy, get_stats, get_relationships, help, exit")
                elif cmd == "generate_prompt":
                    if len(command) < 2:
                        print("Usage: generate_prompt <rule_name> [context] [model]")
                        continue

                    rule_name = command[1]
                    context = json.loads(command[2]) if len(command) > 2 else {}
                    model = command[3] if len(command) > 3 else "claude"

                    result = self.generate_prompt(rule_name, context, model)
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                elif cmd == "analyze_rules":
                    rule_type = command[1] if len(command) > 1 else "all"
                    include_deps = command[2].lower() == "true" if len(command) > 2 else True
                    rule_id = int(command[3]) if len(command) > 3 else None

                    result = self.analyze_rules(rule_type, include_deps, rule_id)
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                elif cmd == "validate_rules":
                    rule_type = command[1] if len(command) > 1 else "all"
                    rule_id = int(command[2]) if len(command) > 2 else None
                    detailed = command[3].lower() == "true" if len(command) > 3 else False

                    result = self.validate_rules(rule_type, rule_id, detailed)
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                elif cmd == "search_rules":
                    if len(command) < 2:
                        print("Usage: search_rules <query> [search_type] [rule_type] [limit]")
                        continue

                    query = command[1]
                    search_type = command[2] if len(command) > 2 else "content"
                    rule_type = command[3] if len(command) > 3 else "all"
                    limit = int(command[4]) if len(command) > 4 else 10

                    result = self.search_rules(query, search_type, rule_type, limit)
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                elif cmd == "optimize_rules":
                    optimization_type = command[1] if len(command) > 1 else "performance"
                    rule_type = command[2] if len(command) > 2 else "all"

                    result = self.optimize_rules(optimization_type, rule_type)
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                elif cmd == "get_hierarchy":
                    if len(command) < 2:
                        print("Usage: get_hierarchy <rule_type>")
                        continue

                    rule_type = command[1]
                    result = self.get_rule_hierarchy(rule_type)
                    print(result)

                elif cmd == "get_stats":
                    result = self.get_performance_stats()
                    print(result)

                elif cmd == "get_relationships":
                    if len(command) < 2:
                        print("Usage: get_relationships <rule_id>")
                        continue

                    rule_id = command[1]
                    result = self.get_rule_relationships(rule_id)
                    print(result)

                else:
                    print(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="AI Prompt Engineering System MCP Server")
    parser.add_argument("--mode", choices=["cli", "server"], default="cli",
                       help="Run mode: cli for interactive testing, server for MCP protocol")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for server mode (default: 8000)")

    args = parser.parse_args()

    logger.info("Starting AI Prompt Engineering System MCP Server...")
    logger.info("Available tools: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules")
    logger.info("Available resources: rules://{type}, stats://performance, relationships://{id}")

    # Initialize server
    server = MCPServer()

    if args.mode == "cli":
        try:
            server.run_cli()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
    else:
        # TODO: Implement proper MCP server protocol
        logger.info("MCP server protocol not yet implemented - use CLI mode for now")
        server.run_cli()

if __name__ == "__main__":
    main()
