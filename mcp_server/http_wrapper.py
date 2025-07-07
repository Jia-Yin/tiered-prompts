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
    from src.database.crud import primitive_crud, semantic_crud, task_crud
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
        return result.dict()
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
        return result.dict()
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
        return result.dict()
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
        return result.dict()
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
            rules = primitive_crud.get_all()
        elif rule_type == "semantic":
            rules = semantic_crud.get_all()
        elif rule_type == "task":
            rules = task_crud.get_all()
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