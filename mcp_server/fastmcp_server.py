#!/usr/bin/env python3
"""
AI Prompt Engineering System - FastMCP Server

This module implements the official MCP server using FastMCP framework.
It exposes the rule engine functionality through standardized MCP protocol.

Based on Phase 2 rule engine and following Phase 3 implementation plan.
Integrates with official MCP Python SDK.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Official MCP SDK imports
from mcp.server import FastMCP
from mcp.types import (
    Completion,
    CompletionArgument,
    CompletionContext,
    PromptReference,
    ResourceTemplateReference,
)
from pydantic import BaseModel, Field

# Import our existing rule engine components
import sys
import os
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
    print("Running in mock mode for development.")
    RULE_ENGINE_AVAILABLE = False

# Import monitoring and configuration utilities
try:
    from mcp_server.utils.monitoring import mcp_monitor, monitor_mcp_operation
    from mcp_server.utils.config import get_config
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import monitoring/config utilities: {e}")
    UTILS_AVAILABLE = False

# Configure logging
if UTILS_AVAILABLE:
    config = get_config()
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format
    )
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class PromptMetadata(BaseModel):
    """Metadata for generated prompts"""
    rule_name: str
    target_model: str
    context_variables: List[str]
    generation_time: float
    rules_used: List[str]

class PromptResult(BaseModel):
    """Complete prompt generation result"""
    prompt: str
    metadata: PromptMetadata

class RuleAnalysis(BaseModel):
    """Rule analysis result"""
    rule_type: str
    total_rules: int
    dependencies: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    performance_metrics: Dict[str, Union[int, float]]

class ValidationResult(BaseModel):
    """Rule validation result"""
    valid: bool
    issues: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    suggestions: List[Dict[str, str]]

class SearchResult(BaseModel):
    """Rule search result"""
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    search_time: float

class OptimizationResult(BaseModel):
    """Rule optimization result"""
    optimization_type: str
    suggestions: List[Dict[str, str]]
    potential_improvements: List[Dict[str, Any]]
    priority_score: float

# ============================================================================
# APP CONTEXT FOR DEPENDENCY INJECTION
# ============================================================================

@dataclass
class AppContext:
    """Application context for dependency injection"""
    rule_engine: Any = None
    db_manager: Any = None
    cache_manager: Any = None
    validation_engine: Any = None
    rule_resolver: Any = None
    config: Any = None
    monitor: Any = None

# ============================================================================
# FASTMCP SERVER IMPLEMENTATION
# ============================================================================

# Get configuration
server_config = get_config() if UTILS_AVAILABLE else None

# Create FastMCP server instance
mcp = FastMCP(
    server_config.mcp.name if server_config else "AI Prompt Engineering System",
    dependencies=server_config.mcp.dependencies if server_config else ["sqlite3", "jinja2", "pydantic"]
)

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with dependency injection"""
    context = AppContext()

    # Initialize configuration and monitoring
    if UTILS_AVAILABLE:
        context.config = get_config()
        context.monitor = mcp_monitor
        logger.info(f"Starting {context.config.mcp.name} v{context.config.mcp.version}")
        logger.info(f"Environment: {context.config.environment}")
        logger.info(f"Debug mode: {context.config.debug}")
    else:
        logger.info("Starting AI Prompt Engineering System (no config/monitoring)")

    if RULE_ENGINE_AVAILABLE:
        try:
            # Initialize rule engine components in correct order
            logger.info("Initializing rule engine services...")

            # 1. Initialize database manager
            context.db_manager = DatabaseManager()

            # 2. Initialize cache manager
            cache_config = context.config.cache if context.config else None
            context.cache_manager = CacheManager(
                max_size=cache_config.max_size if cache_config else 1000,
                ttl=cache_config.ttl_seconds if cache_config else 3600
            )

            # 3. Initialize validation engine (needs db)
            context.validation_engine = ValidationEngine(db=context.db_manager)

            # 4. Initialize rule resolver (needs db and cache)
            context.rule_resolver = RuleResolver(db=context.db_manager, cache_manager=context.cache_manager)

            # 5. Initialize main rule engine (needs db, cache_size, cache_ttl)
            context.rule_engine = RuleEngine(
                db=context.db_manager,
                cache_size=cache_config.max_size if cache_config else 1000,
                cache_ttl=cache_config.ttl_seconds if cache_config else 3600
            )

            logger.info("Rule engine services initialized successfully")

            # Log available tools and resources
            logger.info("Available tools: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules")
            logger.info("Available resources: rules://{type}, stats://performance, relationships://{id}")
            logger.info("Available prompts: create_rule_prompt, debug_rule_prompt")

        except Exception as e:
            logger.error(f"Failed to initialize rule engine: {e}")
            logger.warning("Falling back to mock mode")
            context.rule_engine = None
    else:
        logger.warning("Rule engine not available - using mock mode")
        context.rule_engine = None

    try:
        yield context
    finally:
        # Cleanup on shutdown
        if UTILS_AVAILABLE and context.monitor:
            logger.info("Generating final metrics summary...")
            metrics = context.monitor.get_metrics_summary()
            logger.info(f"Total requests processed: {metrics['request_metrics']['total_requests']}")
            logger.info(f"Success rate: {metrics['request_metrics']['success_rate']:.1f}%")
            logger.info(f"Average response time: {metrics['performance_metrics']['average_response_time']:.3f}s")

        logger.info("Application lifecycle cleanup completed")

# Set lifespan for the server
mcp = FastMCP(
    server_config.mcp.name if server_config else "AI Prompt Engineering System",
    dependencies=server_config.mcp.dependencies if server_config else ["sqlite3", "jinja2", "pydantic"],
    lifespan=app_lifespan
)

# ============================================================================
# MONITORED TOOLS - Tools with performance monitoring
# ============================================================================

def monitored_tool(func):
    """Decorator to add monitoring to MCP tools"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if UTILS_AVAILABLE:
            # Log request
            mcp_monitor.log_request("tool", func.__name__, kwargs)

            import time
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time

                # Log successful response
                mcp_monitor.log_response("tool", func.__name__, True, response_time)
                mcp_monitor.record_operation("tool", func.__name__, response_time, True)

                return result

            except Exception as e:
                response_time = time.time() - start_time
                error_message = str(e)

                # Log failed response
                mcp_monitor.log_response("tool", func.__name__, False, response_time, error_message)
                mcp_monitor.record_operation("tool", func.__name__, response_time, False, error_message)

                raise
        else:
            return func(*args, **kwargs)

    return wrapper

# ============================================================================
# MCP TOOLS - Actions that LLMs can perform
# ============================================================================

@mcp.tool()
@monitored_tool
def generate_prompt(
    rule_name: str,
    context: Dict[str, Any] = None,
    target_model: str = "claude"
) -> PromptResult:
    """
    Generate a complete prompt from rule hierarchy.

    Args:
        rule_name: Name of the task rule to generate prompt for
        context: Optional context variables for template rendering
        target_model: Target AI model (claude, gpt, gemini)

    Returns:
        Complete prompt with metadata
    """
    try:
        # Get application context
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response for development
            return PromptResult(
                prompt=f"# Generated Prompt for {rule_name}\n\n"
                      f"Target Model: {target_model}\n"
                      f"Context Variables: {list(context.keys()) if context else []}\n\n"
                      f"This is a mock prompt generated for rule '{rule_name}'. "
                      f"The actual prompt would be generated using the rule engine "
                      f"with context variables and hierarchy resolution.",
                metadata=PromptMetadata(
                    rule_name=rule_name,
                    target_model=target_model,
                    context_variables=list(context.keys()) if context else [],
                    generation_time=0.001,
                    rules_used=[f"primitive:1", f"semantic:1", f"task:1"]
                )
            )

        # Use real rule engine
        result = app_context.rule_engine.generate_prompt(
            rule_name=rule_name,
            context=context or {},
            model=target_model
        )

        return PromptResult(
            prompt=result["prompt"],
            metadata=PromptMetadata(
                rule_name=rule_name,
                target_model=target_model,
                context_variables=list(context.keys()) if context else [],
                generation_time=result.get("generation_time", 0),
                rules_used=result.get("rules_used", [])
            )
        )

    except Exception as e:
        logger.error(f"Error generating prompt: {e}")
        raise ValueError(f"Failed to generate prompt: {str(e)}")

@mcp.tool()
@monitored_tool
def analyze_rules(
    rule_type: str = "all",
    include_dependencies: bool = True,
    rule_id: Optional[int] = None
) -> RuleAnalysis:
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
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            return RuleAnalysis(
                rule_type=rule_type,
                total_rules=25,
                dependencies=[
                    {"rule_id": 1, "depends_on": [2, 3], "type": "primitive"},
                    {"rule_id": 2, "depends_on": [], "type": "semantic"}
                ],
                relationships=[
                    {"from": "primitive:1", "to": "semantic:1", "type": "enhances"},
                    {"from": "semantic:1", "to": "task:1", "type": "implements"}
                ],
                performance_metrics={
                    "average_resolution_time": 0.05,
                    "cache_hit_rate": 0.85,
                    "total_resolutions": 1247
                }
            )

        # Use real rule engine
        analysis = app_context.rule_engine.analyze_rules(
            rule_type=rule_type,
            include_dependencies=include_dependencies,
            rule_id=rule_id
        )

        return RuleAnalysis(
            rule_type=rule_type,
            total_rules=analysis["total_rules"],
            dependencies=analysis["dependencies"],
            relationships=analysis["relationships"],
            performance_metrics=analysis["performance_metrics"]
        )

    except Exception as e:
        logger.error(f"Error analyzing rules: {e}")
        raise ValueError(f"Failed to analyze rules: {str(e)}")

@mcp.tool()
@monitored_tool
def validate_rules(
    rule_type: str = "all",
    rule_id: Optional[int] = None,
    detailed: bool = False
) -> ValidationResult:
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
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.validation_engine:
            # Mock response
            return ValidationResult(
                valid=True,
                issues=[],
                warnings=[
                    {"rule_id": "semantic:3", "message": "Template variable 'user_name' not defined in context"}
                ],
                suggestions=[
                    {"rule_id": "task:1", "message": "Consider adding fallback for missing context variables"}
                ]
            )

        # Use real validation engine
        validation = app_context.validation_engine.validate_rules(
            rule_type=rule_type,
            rule_id=rule_id,
            detailed=detailed
        )

        return ValidationResult(
            valid=validation["valid"],
            issues=validation["issues"],
            warnings=validation["warnings"],
            suggestions=validation["suggestions"]
        )

    except Exception as e:
        logger.error(f"Error validating rules: {e}")
        raise ValueError(f"Failed to validate rules: {str(e)}")

@mcp.tool()
@monitored_tool
def search_rules(
    query: str,
    search_type: str = "content",
    rule_type: str = "all",
    limit: int = 10
) -> SearchResult:
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
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            return SearchResult(
                query=query,
                results=[
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
                total_found=2,
                search_time=0.003
            )

        # Use real rule engine
        search = app_context.rule_engine.search_rules(
            query=query,
            search_type=search_type,
            rule_type=rule_type,
            limit=limit
        )

        return SearchResult(
            query=query,
            results=search["results"],
            total_found=search["total_found"],
            search_time=search["search_time"]
        )

    except Exception as e:
        logger.error(f"Error searching rules: {e}")
        raise ValueError(f"Failed to search rules: {str(e)}")

@mcp.tool()
@monitored_tool
def optimize_rules(
    optimization_type: str = "performance",
    rule_type: str = "all"
) -> OptimizationResult:
    """
    Analyze and suggest rule optimizations.

    Args:
        optimization_type: Type of optimization (performance, structure, content)
        rule_type: Type of rules to optimize (primitive, semantic, task, all)

    Returns:
        Optimization suggestions and recommendations
    """
    try:
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            return OptimizationResult(
                optimization_type=optimization_type,
                suggestions=[
                    {
                        "rule_id": "task:3",
                        "suggestion": "Combine similar formatting rules to reduce redundancy",
                        "impact": "Medium",
                        "effort": "Low"
                    },
                    {
                        "rule_id": "semantic:2",
                        "suggestion": "Add caching for frequently used templates",
                        "impact": "High",
                        "effort": "Medium"
                    }
                ],
                potential_improvements=[
                    {
                        "metric": "generation_time",
                        "current": 0.15,
                        "potential": 0.08,
                        "improvement": "47%"
                    }
                ],
                priority_score=7.8
            )

        # Use real rule engine
        optimization = app_context.rule_engine.optimize_rules(
            optimization_type=optimization_type,
            rule_type=rule_type
        )

        return OptimizationResult(
            optimization_type=optimization_type,
            suggestions=optimization["suggestions"],
            potential_improvements=optimization["potential_improvements"],
            priority_score=optimization["priority_score"]
        )

    except Exception as e:
        logger.error(f"Error optimizing rules: {e}")
        raise ValueError(f"Failed to optimize rules: {str(e)}")

# ============================================================================
# MONITORED RESOURCES - Resources with performance monitoring
# ============================================================================

def monitored_resource(func):
    """Decorator to add monitoring to MCP resources"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if UTILS_AVAILABLE:
            # Log request
            mcp_monitor.log_request("resource", func.__name__, kwargs)

            import time
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time

                # Log successful response
                mcp_monitor.log_response("resource", func.__name__, True, response_time)
                mcp_monitor.record_operation("resource", func.__name__, response_time, True)

                return result

            except Exception as e:
                response_time = time.time() - start_time
                error_message = str(e)

                # Log failed response
                mcp_monitor.log_response("resource", func.__name__, False, response_time, error_message)
                mcp_monitor.record_operation("resource", func.__name__, response_time, False, error_message)

                raise
        else:
            return func(*args, **kwargs)

    return wrapper

# ============================================================================
# MCP RESOURCES - Data sources that LLMs can access
# ============================================================================

@mcp.resource("rules://{rule_type}")
@monitored_resource
def get_rule_hierarchy(rule_type: str) -> str:
    """
    Get rule hierarchy for a specific type.

    Args:
        rule_type: Type of rules (primitive, semantic, task)

    Returns:
        JSON representation of rule hierarchy
    """
    try:
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            hierarchy = {
                "rule_type": rule_type,
                "rules": [
                    {
                        "id": 1,
                        "name": f"{rule_type}_rule_1",
                        "content": f"Sample {rule_type} rule content",
                        "dependencies": []
                    },
                    {
                        "id": 2,
                        "name": f"{rule_type}_rule_2",
                        "content": f"Another {rule_type} rule",
                        "dependencies": [1]
                    }
                ],
                "relationships": [
                    {"from": 1, "to": 2, "type": "enhances"}
                ],
                "metadata": {
                    "total_rules": 2,
                    "last_updated": "2025-07-05"
                }
            }
            return json.dumps(hierarchy, indent=2)

        # Use real rule engine
        hierarchy = app_context.rule_engine.get_rule_hierarchy(rule_type)
        return json.dumps(hierarchy, indent=2)

    except Exception as e:
        logger.error(f"Error getting rule hierarchy: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.resource("stats://performance")
@monitored_resource
def get_performance_stats() -> str:
    """
    Get system performance statistics.

    Returns:
        JSON representation of performance metrics
    """
    try:
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            stats = {
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
                },
                "performance_metrics": {
                    "queries_per_second": 25.3,
                    "memory_usage_mb": 156.8,
                    "disk_usage_mb": 45.2
                },
                "last_updated": "2025-07-05T10:30:00Z"
            }
            return json.dumps(stats, indent=2)

        # Use real rule engine
        stats = app_context.rule_engine.get_performance_stats()
        return json.dumps(stats, indent=2)

    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.resource("relationships://{rule_id}")
@monitored_resource
def get_rule_relationships(rule_id: str) -> str:
    """
    Get relationships for a specific rule.

    Args:
        rule_id: ID of the rule (format: type:id, e.g., "task:1")

    Returns:
        JSON representation of rule relationships
    """
    try:
        app_context = mcp.get_context().request_context.lifespan_context

        if not app_context or not app_context.rule_engine:
            # Mock response
            rule_type, rule_num = rule_id.split(':')
            relationships = {
                "rule_id": rule_id,
                "rule_name": f"{rule_type}_rule_{rule_num}",
                "depends_on": [
                    {"rule_id": "primitive:1", "name": "clear_formatting", "type": "formatting"},
                    {"rule_id": "semantic:2", "name": "professional_tone", "type": "style"}
                ],
                "used_by": [
                    {"rule_id": "task:3", "name": "code_review", "type": "application"},
                    {"rule_id": "task:4", "name": "documentation", "type": "application"}
                ],
                "related_rules": [
                    {"rule_id": "task:2", "name": "similar_task", "similarity": 0.85}
                ],
                "metadata": {
                    "total_dependencies": 2,
                    "total_dependents": 2,
                    "last_used": "2025-07-05T09:45:00Z"
                }
            }
            return json.dumps(relationships, indent=2)

        # Use real rule engine
        relationships = app_context.rule_engine.get_rule_relationships(rule_id)
        return json.dumps(relationships, indent=2)

    except Exception as e:
        logger.error(f"Error getting rule relationships: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.resource("stats://monitoring")
@monitored_resource
def get_monitoring_stats() -> str:
    """
    Get comprehensive monitoring statistics.

    Returns:
        JSON representation of monitoring metrics
    """
    try:
        if UTILS_AVAILABLE:
            # Get real monitoring data
            metrics = mcp_monitor.get_metrics_summary()
            health = mcp_monitor.get_health_status()

            combined_stats = {
                "health_status": health,
                "metrics": metrics,
                "timestamp": "2025-07-05T10:00:00Z"
            }

            return json.dumps(combined_stats, indent=2)
        else:
            # Mock response
            mock_stats = {
                "health_status": {
                    "status": "healthy",
                    "success_rate": 98.5,
                    "average_response_time": 0.12,
                    "total_requests": 1523,
                    "uptime_seconds": 86400
                },
                "metrics": {
                    "request_metrics": {
                        "total_requests": 1523,
                        "successful_requests": 1500,
                        "failed_requests": 23,
                        "success_rate": 98.5
                    },
                    "performance_metrics": {
                        "average_response_time": 0.12,
                        "max_response_time": 0.85,
                        "min_response_time": 0.01
                    },
                    "tool_metrics": {
                        "generate_prompt": {"total_calls": 845, "avg_response_time": 0.15},
                        "analyze_rules": {"total_calls": 234, "avg_response_time": 0.08},
                        "validate_rules": {"total_calls": 156, "avg_response_time": 0.12}
                    }
                },
                "timestamp": "2025-07-05T10:00:00Z"
            }

            return json.dumps(mock_stats, indent=2)

    except Exception as e:
        logger.error(f"Error getting monitoring stats: {e}")
        return json.dumps({"error": str(e)}, indent=2)

# ============================================================================
# MCP PROMPTS - Reusable prompt templates
# ============================================================================

@mcp.prompt(title="Rule Creation Assistant")
def create_rule_prompt(
    rule_type: str,
    domain: str = "general"
) -> str:
    """
    Assist in creating new rules.

    Args:
        rule_type: Type of rule to create (primitive, semantic, task)
        domain: Domain for the rule (general, coding, documentation)

    Returns:
        Prompt template for rule creation
    """
    return f"""# Rule Creation Assistant

You are helping to create a new {rule_type} rule for the {domain} domain.

## Rule Type: {rule_type}

### Guidelines for {rule_type} rules:
- **Primitive rules**: Basic formatting and structure guidelines
- **Semantic rules**: Meaning and content quality guidelines
- **Task rules**: Complete workflow templates

### Domain: {domain}

Please provide:
1. **Rule Name**: A clear, descriptive name
2. **Rule Content**: The actual rule or template
3. **Dependencies**: Any rules this depends on
4. **Context Variables**: Variables that can be customized
5. **Usage Examples**: How this rule should be applied

### Example Structure:
```
Name: {rule_type}_rule_example
Content: [Your rule content here]
Dependencies: [List any prerequisite rules]
Variables: [List customizable variables]
```

What {rule_type} rule would you like to create for the {domain} domain?
"""

@mcp.prompt(title="Rule Debugging Assistant")
def debug_rule_prompt(
    error_description: str,
    rule_context: str
) -> str:
    """
    Assist in debugging rule issues.

    Args:
        error_description: Description of the error or issue
        rule_context: Context about the rule causing problems

    Returns:
        Debugging assistance prompt
    """
    return f"""# Rule Debugging Assistant

I'll help you debug the rule issue you're experiencing.

## Error Description:
{error_description}

## Rule Context:
{rule_context}

## Debugging Steps:

1. **Rule Validation**: Check if the rule syntax is correct
2. **Dependency Analysis**: Verify all dependencies are available
3. **Context Variables**: Ensure all required variables are provided
4. **Template Rendering**: Check for template syntax errors
5. **Performance Issues**: Look for inefficient patterns

## Common Issues and Solutions:

### Template Errors:
- Missing variables: `{{ variable_name }}`
- Incorrect syntax: Use Jinja2 syntax
- Undefined filters: Check available filters

### Dependency Problems:
- Missing rules: Verify rule IDs exist
- Circular dependencies: Check for loops
- Order issues: Ensure proper resolution order

### Performance Issues:
- Complex templates: Simplify where possible
- Large contexts: Optimize variable usage
- Cache misses: Review caching strategy

## Next Steps:
1. Run rule validation
2. Check dependency tree
3. Test with minimal context
4. Review error logs

How can I help you resolve this specific issue?
"""

# ============================================================================
# MCP COMPLETIONS - Argument completion support
# ============================================================================

@mcp.completion()
async def handle_completion(
    ref: PromptReference | ResourceTemplateReference,
    argument: CompletionArgument,
    context: CompletionContext | None,
) -> Completion | None:
    """
    Provide completions for prompts and resources.

    Args:
        ref: Reference to prompt or resource template
        argument: Argument being completed
        context: Context for completion

    Returns:
        Completion suggestions
    """
    try:
        # Complete rule types
        if argument.name == "rule_type":
            rule_types = ["primitive", "semantic", "task", "all"]
            matches = [rt for rt in rule_types if rt.startswith(argument.value)]
            return Completion(values=matches, hasMore=False)

        # Complete target models
        if argument.name == "target_model":
            models = ["claude", "gpt", "gemini", "llama"]
            matches = [m for m in models if m.startswith(argument.value)]
            return Completion(values=matches, hasMore=False)

        # Complete optimization types
        if argument.name == "optimization_type":
            opt_types = ["performance", "structure", "content"]
            matches = [ot for ot in opt_types if ot.startswith(argument.value)]
            return Completion(values=matches, hasMore=False)

        # Complete search types
        if argument.name == "search_type":
            search_types = ["content", "name", "metadata"]
            matches = [st for st in search_types if st.startswith(argument.value)]
            return Completion(values=matches, hasMore=False)

        # Complete domains for rule creation
        if argument.name == "domain":
            domains = ["general", "coding", "documentation", "analysis", "creative"]
            matches = [d for d in domains if d.startswith(argument.value)]
            return Completion(values=matches, hasMore=False)

        return None

    except Exception as e:
        logger.error(f"Error in completion: {e}")
        return None

# ============================================================================
# SERVER EXECUTION
# ============================================================================

def main():
    """Main entry point for the FastMCP server"""
    logger.info("Starting AI Prompt Engineering System FastMCP Server...")
    logger.info("Available tools: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules")
    logger.info("Available resources: rules://{type}, stats://performance, relationships://{id}")
    logger.info("Available prompts: create_rule_prompt, debug_rule_prompt")

    # Run the server
    mcp.run()

if __name__ == "__main__":
    main()
