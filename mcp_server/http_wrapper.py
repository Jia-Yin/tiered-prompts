#!/usr/bin/env python3
"""
HTTP Wrapper for MCP Server

This provides HTTP endpoints to access MCP tools and resources
for the web interface backend.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import components directly instead of using the FastMCP wrapper
import sys
import os

# Add project paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
ai_prompt_dir = os.path.join(project_root, 'ai_prompt_system')

if ai_prompt_dir not in sys.path:
    sys.path.append(ai_prompt_dir)

# Change to ai_prompt_system directory for database access
os.chdir(ai_prompt_dir)

# Import rule engine components directly
try:
    from src.rule_engine.engine import RuleEngine
    from src.rule_engine.resolver import RuleResolver
    from src.rule_engine.validation import ValidationEngine
    from src.rule_engine.cache import CacheManager
    from src.database.connection import DatabaseManager
    from src.database.crud import primitive_crud, semantic_crud, task_crud, category_crud
    RULE_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import rule engine components: {e}")
    RULE_ENGINE_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rule engine components globally
rule_engine = None
db_manager = None
cache_manager = None
validation_engine = None

# Initialize CRUD instances globally
primitive_crud_instance = None
semantic_crud_instance = None
task_crud_instance = None
category_crud_instance = None

if RULE_ENGINE_AVAILABLE:
    try:
        # Initialize database manager with absolute path
        db_path = os.path.join(project_root, "ai_prompt_system", "database", "prompt_system.db")
        db_manager = DatabaseManager(db_path)
        
        # Initialize cache manager
        cache_manager = CacheManager(max_size=1000, ttl=3600)
        
        # Initialize validation engine
        validation_engine = ValidationEngine(db=db_manager)
        
        # Initialize rule engine
        rule_engine = RuleEngine(db=db_manager, cache_size=1000, cache_ttl=3600)
        
        # Initialize CRUD instances
        from src.database.crud import PrimitiveRuleCRUD, SemanticRuleCRUD, TaskRuleCRUD, CategoryCRUD, RelationCRUD
        primitive_crud_instance = PrimitiveRuleCRUD()
        semantic_crud_instance = SemanticRuleCRUD()
        task_crud_instance = TaskRuleCRUD()
        category_crud_instance = CategoryCRUD()
        relation_crud_instance = RelationCRUD()
        
        logger.info("✅ Rule engine components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize rule engine: {e}")
        RULE_ENGINE_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="MCP Server HTTP Wrapper",
    description="HTTP wrapper for AI Prompt Engineering System MCP Server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# FUNCTION IMPLEMENTATIONS
# ============================================================================

def create_primitive_rule(name: str, content: str, description: str = None, category: str = None) -> Dict[str, Any]:
    """Create a primitive rule"""
    if not RULE_ENGINE_AVAILABLE or not primitive_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        rule_id = primitive_crud_instance.create_primitive_rule(
            name=name,
            content=content,
            description=description,
            category=category
        )
        return {"success": True, "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error creating primitive rule: {e}")
        return {"success": False, "error": str(e)}

def create_semantic_rule(name: str, content_template: str, description: str = None, category: str = None) -> Dict[str, Any]:
    """Create a semantic rule"""
    if not RULE_ENGINE_AVAILABLE or not semantic_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        rule_id = semantic_crud_instance.create_semantic_rule(
            name=name,
            content_template=content_template,
            description=description,
            category=category
        )
        return {"success": True, "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error creating semantic rule: {e}")
        return {"success": False, "error": str(e)}

def create_task_rule(name: str, prompt_template: str, description: str = None, 
                    language: str = None, framework: str = None, domain: str = None, 
                    category: str = None) -> Dict[str, Any]:
    """Create a task rule"""
    if not RULE_ENGINE_AVAILABLE or not task_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        rule_id = task_crud_instance.create_task_rule(
            name=name,
            prompt_template=prompt_template,
            description=description,
            language=language,
            framework=framework,
            domain=domain,
            category=category
        )
        return {"success": True, "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error creating task rule: {e}")
        return {"success": False, "error": str(e)}

def update_primitive_rule(rule_id: int, **kwargs) -> Dict[str, Any]:
    """Update a primitive rule"""
    if not RULE_ENGINE_AVAILABLE or not primitive_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = primitive_crud_instance.update(rule_id, **kwargs)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error updating primitive rule: {e}")
        return {"success": False, "error": str(e)}

def update_semantic_rule(rule_id: int, **kwargs) -> Dict[str, Any]:
    """Update a semantic rule"""
    if not RULE_ENGINE_AVAILABLE or not semantic_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = semantic_crud_instance.update(rule_id, **kwargs)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error updating semantic rule: {e}")
        return {"success": False, "error": str(e)}

def update_task_rule(rule_id: int, **kwargs) -> Dict[str, Any]:
    """Update a task rule"""
    if not RULE_ENGINE_AVAILABLE or not task_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = task_crud_instance.update(rule_id, **kwargs)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error updating task rule: {e}")
        return {"success": False, "error": str(e)}

def delete_primitive_rule(rule_id: int) -> Dict[str, Any]:
    """Delete a primitive rule"""
    if not RULE_ENGINE_AVAILABLE or not primitive_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = primitive_crud_instance.delete(rule_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting primitive rule: {e}")
        return {"success": False, "error": str(e)}

def delete_semantic_rule(rule_id: int) -> Dict[str, Any]:
    """Delete a semantic rule"""
    if not RULE_ENGINE_AVAILABLE or not semantic_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = semantic_crud_instance.delete(rule_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting semantic rule: {e}")
        return {"success": False, "error": str(e)}

def delete_task_rule(rule_id: int) -> Dict[str, Any]:
    """Delete a task rule"""
    if not RULE_ENGINE_AVAILABLE or not task_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = task_crud_instance.delete(rule_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting task rule: {e}")
        return {"success": False, "error": str(e)}

# Prompt generation function
def generate_prompt(rule_name: str, context: dict = None, target_model: str = "claude") -> Dict[str, Any]:
    """Generate a prompt using the rule engine"""
    if not RULE_ENGINE_AVAILABLE or not rule_engine:
        return {
            "prompt": "Rule engine not available - using mock response",
            "metadata": {
                "rule_name": rule_name,
                "target_model": target_model,
                "context_variables": list(context.keys()) if context else [],
                "generation_time": 0.001,
                "rules_used": ["mock"],
                "error": "Rule engine not available"
            }
        }
    
    try:
        import time
        start_time = time.time()
        
        # Find the rule by name across all types
        rule_data = None
        rule_type = None
        
        # Search in all rule types
        for rt, crud_instance in [("task", task_crud_instance), ("semantic", semantic_crud_instance), ("primitive", primitive_crud_instance)]:
            if crud_instance:
                try:
                    # Get all rules of this type and search by name
                    rules = crud_instance.get_all()
                    for rule in rules:
                        if rule.get('name') == rule_name:
                            rule_data = rule
                            rule_type = rt
                            break
                    if rule_data:
                        break
                except Exception as e:
                    logger.error(f"Error searching {rt} rules: {e}")
                    continue
        
        if not rule_data:
            return {
                "prompt": f"Error: Rule '{rule_name}' not found",
                "metadata": {
                    "rule_name": rule_name,
                    "target_model": target_model,
                    "context_variables": list(context.keys()) if context else [],
                    "generation_time": time.time() - start_time,
                    "rules_used": [],
                    "error": f"Rule '{rule_name}' not found"
                }
            }
        
        # Get the rule content based on type
        if rule_type == "primitive":
            template = rule_data.get('content', '')
        elif rule_type == "semantic":
            template = rule_data.get('content_template', '')
        elif rule_type == "task":
            template = rule_data.get('prompt_template', '')
        else:
            template = str(rule_data.get('content', ''))
        
        # Generate the prompt using the rule engine
        if context is None:
            context = {}
            
        try:
            # Use the rule engine to generate the prompt
            prompt_result = rule_engine.generate_prompt(rule_name, context, target_model)
            generation_time = time.time() - start_time
            
            return {
                "prompt": prompt_result.get('prompt', template),
                "metadata": {
                    "rule_name": rule_name,
                    "target_model": target_model,
                    "context_variables": list(context.keys()),
                    "generation_time": round(generation_time, 4),
                    "rules_used": prompt_result.get('rules_used', [rule_name]),
                    "rule_type": rule_type,
                    "rule_id": rule_data.get('id')
                }
            }
        except Exception as e:
            # Fallback to simple template substitution if rule engine fails
            logger.warning(f"Rule engine failed for {rule_name}, using fallback: {e}")
            
            # Simple template substitution
            prompt = template
            variables_used = []
            
            if context:
                for key, value in context.items():
                    placeholder_patterns = [
                        f"{{{{{key}}}}}",  # {{key}} format
                        f"{{key}}",       # {key} format
                        f"${key}",        # $key format
                        f"<{key}>",       # <key> format
                    ]
                    
                    for pattern in placeholder_patterns:
                        if pattern in prompt:
                            prompt = prompt.replace(pattern, str(value))
                            if key not in variables_used:
                                variables_used.append(key)
            
            generation_time = time.time() - start_time
            
            return {
                "prompt": prompt,
                "metadata": {
                    "rule_name": rule_name,
                    "target_model": target_model,
                    "context_variables": variables_used,
                    "generation_time": round(generation_time, 4),
                    "rules_used": [rule_name],
                    "rule_type": rule_type,
                    "rule_id": rule_data.get('id'),
                    "method": "template_substitution"
                }
            }
            
    except Exception as e:
        logger.error(f"Error generating prompt for {rule_name}: {e}")
        return {
            "prompt": f"Error generating prompt: {str(e)}",
            "metadata": {
                "rule_name": rule_name,
                "target_model": target_model,
                "context_variables": list(context.keys()) if context else [],
                "generation_time": 0,
                "rules_used": [],
                "error": str(e)
            }
        }

def analyze_rules(**kwargs):
    """Placeholder for analyze_rules"""
    return {"analysis": "Analysis placeholder"}

def validate_rules(**kwargs):
    """Placeholder for validate_rules"""
    return {"valid": True, "issues": []}

def optimize_rules(**kwargs):
    """Placeholder for optimize_rules"""
    return {"suggestions": []}

def get_performance_stats():
    """Placeholder for performance stats"""
    return {"system_stats": {"total_rules": 0}}

def get_rule_relationships(rule_id: str):
    """Placeholder for rule relationships"""
    return {"relationships": []}

def list_categories():
    """List all categories"""
    if not RULE_ENGINE_AVAILABLE or not category_crud_instance:
        return {"categories": []}
    
    try:
        categories = category_crud_instance.get_all()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        return {"categories": []}

def create_category(name: str, description: str = None, color: str = "#6B7280", icon: str = None):
    """Create a category"""
    if not RULE_ENGINE_AVAILABLE or not category_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        category_id = category_crud_instance.create_category(
            name=name,
            description=description,
            color=color,
            icon=icon
        )
        return {"success": True, "category_id": category_id}
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# TOOL ENDPOINTS
# ============================================================================

@app.post("/tools/generate_prompt")
async def http_generate_prompt(request: Dict[str, Any]):
    """Generate a prompt via HTTP"""
    try:
        result = generate_prompt(
            rule_name=request.get("rule_name", ""),
            context=request.get("context", {}),
            target_model=request.get("target_model", "claude")
        )
        return result
    except Exception as e:
        logger.error(f"Error in generate_prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/analyze_rules")
async def http_analyze_rules(request: Dict[str, Any]):
    """Analyze rules via HTTP"""
    try:
        result = analyze_rules(
            rule_type=request.get("rule_type", "all"),
            include_dependencies=request.get("include_dependencies", True),
            rule_id=request.get("rule_id")
        )
        return result
    except Exception as e:
        logger.error(f"Error in analyze_rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/validate_rules")
async def http_validate_rules(request: Dict[str, Any]):
    """Validate rules via HTTP"""
    try:
        result = validate_rules(
            rule_type=request.get("rule_type", "all"),
            rule_id=request.get("rule_id"),
            detailed=request.get("detailed", False)
        )
        return result
    except Exception as e:
        logger.error(f"Error in validate_rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/search_rules")
async def http_search_rules(request: Dict[str, Any]):
    """Search rules via HTTP"""
    try:
        query = request.get("query", "")
        search_type = request.get("search_type", "content")
        rule_type = request.get("rule_type", "all")
        limit = request.get("limit", 10)
        
        if not RULE_ENGINE_AVAILABLE or not db_manager:
            # Mock response for development
            return {
                "query": query,
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
            }
        
        # Implement real search functionality
        import time
        start_time = time.time()
        results = []
        
        # Search in different rule types based on rule_type parameter
        tables_to_search = []
        if rule_type == "all":
            tables_to_search = ["primitive_rules", "semantic_rules", "task_rules"]
        elif rule_type == "primitive":
            tables_to_search = ["primitive_rules"]
        elif rule_type == "semantic":
            tables_to_search = ["semantic_rules"]
        elif rule_type == "task":
            tables_to_search = ["task_rules"]
        
        for table in tables_to_search:
            # Determine rule type from table name
            if "primitive" in table:
                current_rule_type = "primitive"
            elif "semantic" in table:
                current_rule_type = "semantic"
            else:
                current_rule_type = "task"
            
            # Define content column based on table
            content_column = "content"
            if table == "semantic_rules":
                content_column = "content_template"
            elif table == "task_rules":
                content_column = "prompt_template"
            
            # Search based on search_type
            if search_type == "content":
                sql = f"SELECT id, name, {content_column} as content, description FROM {table} WHERE {content_column} LIKE ? OR description LIKE ? LIMIT ?"
                params = (f"%{query}%", f"%{query}%", limit)
            elif search_type == "name":
                sql = f"SELECT id, name, {content_column} as content, description FROM {table} WHERE name LIKE ? LIMIT ?"
                params = (f"%{query}%", limit)
            else:  # metadata search
                sql = f"SELECT id, name, {content_column} as content, description FROM {table} WHERE name LIKE ? OR {content_column} LIKE ? OR description LIKE ? LIMIT ?"
                params = (f"%{query}%", f"%{query}%", f"%{query}%", limit)
            
            # Execute search query
            try:
                rows = db_manager.execute_query(sql, params)
                for row in rows:
                    # Calculate simple relevance score (could be improved)
                    relevance = 1.0
                    if query.lower() in (row.get('name', '') or '').lower():
                        relevance = 0.95
                    elif query.lower() in (row.get('content', '') or '').lower():
                        relevance = 0.8
                    elif query.lower() in (row.get('description', '') or '').lower():
                        relevance = 0.6
                    
                    results.append({
                        "rule_id": row['id'],
                        "name": row['name'],
                        "type": current_rule_type,
                        "content": row['content'] or '',
                        "relevance": relevance
                    })
            except Exception as e:
                logger.error(f"Error searching {table}: {e}")
                continue
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        results = results[:limit]
        
        search_time = time.time() - start_time
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "search_time": search_time
        }
        
    except Exception as e:
        logger.error(f"Error in search_rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/optimize_rules")
async def http_optimize_rules(request: Dict[str, Any]):
    """Optimize rules via HTTP"""
    try:
        result = optimize_rules(
            optimization_type=request.get("optimization_type", "performance"),
            rule_type=request.get("rule_type", "all")
        )
        return result
    except Exception as e:
        logger.error(f"Error in optimize_rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_primitive_rule")
async def http_create_primitive_rule(request: Dict[str, Any]):
    """Create primitive rule via HTTP"""
    try:
        result = create_primitive_rule(
            name=request.get("name", ""),
            content=request.get("content", ""),
            description=request.get("description"),
            category=request.get("category")
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_primitive_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_semantic_rule")
async def http_create_semantic_rule(request: Dict[str, Any]):
    """Create semantic rule via HTTP"""
    try:
        result = create_semantic_rule(
            name=request.get("name", ""),
            content_template=request.get("content_template", ""),
            description=request.get("description"),
            category=request.get("category")
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_semantic_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_task_rule")
async def http_create_task_rule(request: Dict[str, Any]):
    """Create task rule via HTTP"""
    try:
        result = create_task_rule(
            name=request.get("name", ""),
            prompt_template=request.get("prompt_template", ""),
            description=request.get("description"),
            language=request.get("language"),
            framework=request.get("framework"),
            domain=request.get("domain"),
            category=request.get("category")
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_task_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_primitive_rule")
async def http_update_primitive_rule(request: Dict[str, Any]):
    """Update primitive rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        # Remove rule_id from request data
        update_data = {k: v for k, v in request.items() if k != "rule_id"}
        result = update_primitive_rule(rule_id, **update_data)
        return result
    except Exception as e:
        logger.error(f"Error in update_primitive_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_semantic_rule")
async def http_update_semantic_rule(request: Dict[str, Any]):
    """Update semantic rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        # Remove rule_id from request data
        update_data = {k: v for k, v in request.items() if k != "rule_id"}
        result = update_semantic_rule(rule_id, **update_data)
        return result
    except Exception as e:
        logger.error(f"Error in update_semantic_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_task_rule")
async def http_update_task_rule(request: Dict[str, Any]):
    """Update task rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        # Remove rule_id from request data
        update_data = {k: v for k, v in request.items() if k != "rule_id"}
        result = update_task_rule(rule_id, **update_data)
        return result
    except Exception as e:
        logger.error(f"Error in update_task_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_primitive_rule")
async def http_delete_primitive_rule(request: Dict[str, Any]):
    """Delete primitive rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        result = delete_primitive_rule(rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_primitive_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_semantic_rule")
async def http_delete_semantic_rule(request: Dict[str, Any]):
    """Delete semantic rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        result = delete_semantic_rule(rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_semantic_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/delete_task_rule")
async def http_delete_task_rule(request: Dict[str, Any]):
    """Delete task rule via HTTP"""
    try:
        rule_id = request.get("rule_id")
        if not rule_id:
            raise HTTPException(status_code=400, detail="rule_id is required")
        
        result = delete_task_rule(rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_task_rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a direct get rule by ID endpoint
@app.get("/tools/get_rule/{rule_id}")
async def http_get_rule_by_id(rule_id: int):
    """Get a specific rule by ID via HTTP"""
    try:
        if not RULE_ENGINE_AVAILABLE:
            return {"error": "Rule engine not available"}
        
        # Try to find the rule across all types
        rule_types = [
            ("primitive", primitive_crud_instance),
            ("semantic", semantic_crud_instance), 
            ("task", task_crud_instance)
        ]
        
        for rule_type, crud_instance in rule_types:
            if crud_instance:
                try:
                    rule = crud_instance.get_by_id(rule_id)
                    if rule:
                        return {"rule": {**rule, "type": rule_type}}
                except Exception as e:
                    logger.error(f"Error getting {rule_type} rule {rule_id}: {e}")
                    continue
        
        raise HTTPException(status_code=404, detail="Rule not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RESOURCE ENDPOINTS
# ============================================================================

@app.get("/resources/rules/{rule_type}")
async def http_get_rule_hierarchy(rule_type: str):
    """Get rule hierarchy via HTTP"""
    try:
        if not RULE_ENGINE_AVAILABLE or not db_manager:
            # Mock response
            mock_data = {
                "rule_type": rule_type,
                "rules": [
                    {
                        "id": 1,
                        "name": f"mock_{rule_type}_rule_1",
                        "content": f"Mock {rule_type} rule content",
                        "dependencies": []
                    }
                ],
                "total_rules": 1
            }
            return {"data": mock_data}
        
        # Get real data from database
        if rule_type == "primitive":
            rules = primitive_crud_instance.get_all()
        elif rule_type == "semantic":
            rules = semantic_crud_instance.get_all()
        elif rule_type == "task":
            rules = task_crud_instance.get_all()
        else:
            raise HTTPException(status_code=400, detail=f"Invalid rule type: {rule_type}")
        
        result = {
            "rule_type": rule_type,
            "rules": rules,
            "total_rules": len(rules)
        }
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Error in get_rule_hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources/stats/performance")
async def http_get_performance_stats():
    """Get performance stats via HTTP"""
    try:
        result = get_performance_stats()
        return {"data": result}
    except Exception as e:
        logger.error(f"Error in get_performance_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources/relationships/{rule_id}")
async def http_get_rule_relationships(rule_id: str):
    """Get rule relationships via HTTP"""
    try:
        result = get_rule_relationships(rule_id)
        return {"data": result}
    except Exception as e:
        logger.error(f"Error in get_rule_relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RELATIONSHIP MANAGEMENT FUNCTIONS
# ============================================================================

def create_task_semantic_relation(task_rule_id: int, semantic_rule_id: int, weight: float = 1.0, 
                                  order_index: int = 0, is_required: bool = True, 
                                  context_override: dict = None) -> Dict[str, Any]:
    """Create relationship between task and semantic rule"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        relation_id = relation_crud_instance.create_task_semantic_relation(
            task_rule_id=task_rule_id,
            semantic_rule_id=semantic_rule_id,
            weight=weight,
            order_index=order_index,
            is_required=is_required,
            context_override=context_override
        )
        return {"success": True, "relation_id": relation_id}
    except Exception as e:
        logger.error(f"Error creating task-semantic relation: {e}")
        return {"success": False, "error": str(e)}

def create_semantic_primitive_relation(semantic_rule_id: int, primitive_rule_id: int, 
                                       weight: float = 1.0, order_index: int = 0, 
                                       is_required: bool = True) -> Dict[str, Any]:
    """Create relationship between semantic and primitive rule"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        relation_id = relation_crud_instance.create_semantic_primitive_relation(
            semantic_rule_id=semantic_rule_id,
            primitive_rule_id=primitive_rule_id,
            weight=weight,
            order_index=order_index,
            is_required=is_required
        )
        return {"success": True, "relation_id": relation_id}
    except Exception as e:
        logger.error(f"Error creating semantic-primitive relation: {e}")
        return {"success": False, "error": str(e)}

def get_task_semantic_relations(task_rule_id: int = None) -> Dict[str, Any]:
    """Get task-semantic relationships"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"relations": []}
    
    try:
        relations = relation_crud_instance.get_task_semantic_relations(task_rule_id)
        return {"relations": relations}
    except Exception as e:
        logger.error(f"Error getting task-semantic relations: {e}")
        return {"relations": [], "error": str(e)}

def get_semantic_primitive_relations(semantic_rule_id: int = None) -> Dict[str, Any]:
    """Get semantic-primitive relationships"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"relations": []}
    
    try:
        relations = relation_crud_instance.get_semantic_primitive_relations(semantic_rule_id)
        return {"relations": relations}
    except Exception as e:
        logger.error(f"Error getting semantic-primitive relations: {e}")
        return {"relations": [], "error": str(e)}

def delete_task_semantic_relation(task_rule_id: int, semantic_rule_id: int) -> Dict[str, Any]:
    """Delete task-semantic relationship"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = relation_crud_instance.delete_task_semantic_relation(task_rule_id, semantic_rule_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting task-semantic relation: {e}")
        return {"success": False, "error": str(e)}

def delete_semantic_primitive_relation(semantic_rule_id: int, primitive_rule_id: int) -> Dict[str, Any]:
    """Delete semantic-primitive relationship"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"success": False, "error": "Rule engine not available"}
    
    try:
        success = relation_crud_instance.delete_semantic_primitive_relation(semantic_rule_id, primitive_rule_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting semantic-primitive relation: {e}")
        return {"success": False, "error": str(e)}

def get_rule_dependencies(rule_type: str, rule_id: int) -> Dict[str, Any]:
    """Get dependencies for a rule"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"dependencies": {"children": [], "parents": []}}
    
    try:
        dependencies = relation_crud_instance.get_rule_dependencies(rule_type, rule_id)
        return {"dependencies": dependencies}
    except Exception as e:
        logger.error(f"Error getting rule dependencies: {e}")
        return {"dependencies": {"children": [], "parents": []}, "error": str(e)}

def get_rule_hierarchy() -> Dict[str, Any]:
    """Get complete rule hierarchy with relationships"""
    if not RULE_ENGINE_AVAILABLE or not relation_crud_instance:
        return {"hierarchy": {}}
    
    try:
        hierarchy = relation_crud_instance.get_rule_hierarchy()
        return {"hierarchy": hierarchy}
    except Exception as e:
        logger.error(f"Error getting rule hierarchy: {e}")
        return {"hierarchy": {}, "error": str(e)}

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/categories")
async def http_list_categories():
    """List all categories via HTTP"""
    try:
        result = list_categories()
        return result
    except Exception as e:
        logger.error(f"Error in list_categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories")
async def http_create_category(request: Dict[str, Any]):
    """Create category via HTTP"""
    try:
        result = create_category(
            name=request.get("name", ""),
            description=request.get("description"),
            color=request.get("color", "#6B7280"),
            icon=request.get("icon")
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RELATIONSHIP MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/tools/create_task_semantic_relation")
async def http_create_task_semantic_relation(request: Dict[str, Any]):
    """Create task-semantic relationship via HTTP"""
    try:
        result = create_task_semantic_relation(
            task_rule_id=request.get("task_rule_id"),
            semantic_rule_id=request.get("semantic_rule_id"),
            weight=request.get("weight", 1.0),
            order_index=request.get("order_index", 0),
            is_required=request.get("is_required", True),
            context_override=request.get("context_override")
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_task_semantic_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/create_semantic_primitive_relation")
async def http_create_semantic_primitive_relation(request: Dict[str, Any]):
    """Create semantic-primitive relationship via HTTP"""
    try:
        result = create_semantic_primitive_relation(
            semantic_rule_id=request.get("semantic_rule_id"),
            primitive_rule_id=request.get("primitive_rule_id"),
            weight=request.get("weight", 1.0),
            order_index=request.get("order_index", 0),
            is_required=request.get("is_required", True)
        )
        return result
    except Exception as e:
        logger.error(f"Error in create_semantic_primitive_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_task_semantic_relations")
async def http_get_task_semantic_relations(task_rule_id: int = None):
    """Get task-semantic relationships via HTTP"""
    try:
        result = get_task_semantic_relations(task_rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_task_semantic_relations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_semantic_primitive_relations")
async def http_get_semantic_primitive_relations(semantic_rule_id: int = None):
    """Get semantic-primitive relationships via HTTP"""
    try:
        result = get_semantic_primitive_relations(semantic_rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_semantic_primitive_relations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tools/delete_task_semantic_relation")
async def http_delete_task_semantic_relation(request: Dict[str, Any]):
    """Delete task-semantic relationship via HTTP"""
    try:
        result = delete_task_semantic_relation(
            task_rule_id=request.get("task_rule_id"),
            semantic_rule_id=request.get("semantic_rule_id")
        )
        return result
    except Exception as e:
        logger.error(f"Error in delete_task_semantic_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tools/delete_semantic_primitive_relation")
async def http_delete_semantic_primitive_relation(request: Dict[str, Any]):
    """Delete semantic-primitive relationship via HTTP"""
    try:
        result = delete_semantic_primitive_relation(
            semantic_rule_id=request.get("semantic_rule_id"),
            primitive_rule_id=request.get("primitive_rule_id")
        )
        return result
    except Exception as e:
        logger.error(f"Error in delete_semantic_primitive_relation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_rule_dependencies/{rule_type}/{rule_id}")
async def http_get_rule_dependencies(rule_type: str, rule_id: int):
    """Get rule dependencies via HTTP"""
    try:
        result = get_rule_dependencies(rule_type, rule_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_rule_dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/get_rule_hierarchy")
async def http_get_rule_hierarchy():
    """Get complete rule hierarchy via HTTP"""
    try:
        result = get_rule_hierarchy()
        return result
    except Exception as e:
        logger.error(f"Error in get_rule_hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCP Server HTTP Wrapper",
        "version": "1.0.0"
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the HTTP wrapper server"""
    logger.info("Starting MCP Server HTTP Wrapper...")
    logger.info("Available endpoints:")
    logger.info("  POST /tools/{tool_name}")
    logger.info("  GET /resources/{resource_path}")
    logger.info("  GET /health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

if __name__ == "__main__":
    main()