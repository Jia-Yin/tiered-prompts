"""
API Routes for Web Interface
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from app.models.requests import (
    GeneratePromptRequest,
    AnalyzeRulesRequest, 
    ValidateRulesRequest,
    SearchRulesRequest,
    OptimizeRulesRequest,
    CreateRuleRequest
)
from app.models.responses import (
    PromptResponse,
    AnalysisResponse,
    ValidationResponse,
    SearchResponse,
    OptimizationResponse,
    RuleResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get MCP client
def get_mcp_client(request: Request):
    return request.app.state.mcp_client

# Dependency to get WebSocket manager
def get_websocket_manager(request: Request):
    return request.app.state.websocket_manager

# ============================================================================
# MCP TOOL ENDPOINTS
# ============================================================================

@router.post("/mcp/generate-prompt", response_model=PromptResponse)
async def generate_prompt(
    request: GeneratePromptRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Generate a prompt using MCP server"""
    try:
        result = await mcp_client.call_mcp_tool("generate_prompt", {
            "rule_name": request.rule_name,
            "context": request.context or {},
            "target_model": request.target_model
        })
        
        response = PromptResponse(**result)
        
        # Broadcast operation to WebSocket clients
        await ws_manager.broadcast_mcp_operation("generate_prompt", result)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/analyze-rules", response_model=AnalysisResponse)
async def analyze_rules(
    request: AnalyzeRulesRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Analyze rules using MCP server"""
    try:
        result = await mcp_client.call_mcp_tool("analyze_rules", {
            "rule_type": request.rule_type,
            "include_dependencies": request.include_dependencies,
            "rule_id": request.rule_id
        })
        
        response = AnalysisResponse(**result)
        
        # Broadcast operation to WebSocket clients
        await ws_manager.broadcast_mcp_operation("analyze_rules", result)
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/validate-rules", response_model=ValidationResponse)
async def validate_rules(
    request: ValidateRulesRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Validate rules using MCP server"""
    try:
        result = await mcp_client.call_mcp_tool("validate_rules", {
            "rule_type": request.rule_type,
            "rule_id": request.rule_id,
            "detailed": request.detailed
        })
        
        response = ValidationResponse(**result)
        
        # Broadcast operation to WebSocket clients
        await ws_manager.broadcast_mcp_operation("validate_rules", result)
        
        return response
        
    except Exception as e:
        logger.error(f"Error validating rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/search-rules", response_model=SearchResponse)
async def search_rules(
    request: SearchRulesRequest,
    mcp_client=Depends(get_mcp_client)
):
    """Search rules using MCP server"""
    try:
        result = await mcp_client.call_mcp_tool("search_rules", {
            "query": request.query,
            "search_type": request.search_type,
            "rule_type": request.rule_type,
            "limit": request.limit
        })
        
        return SearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Error searching rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/optimize-rules", response_model=OptimizationResponse)
async def optimize_rules(
    request: OptimizeRulesRequest,
    mcp_client=Depends(get_mcp_client)
):
    """Optimize rules using MCP server"""
    try:
        result = await mcp_client.call_mcp_tool("optimize_rules", {
            "optimization_type": request.optimization_type,
            "rule_type": request.rule_type
        })
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error optimizing rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MCP RESOURCE ENDPOINTS
# ============================================================================

@router.get("/mcp/resources/rules/{rule_type}")
async def get_rule_hierarchy(
    rule_type: str,
    mcp_client=Depends(get_mcp_client)
):
    """Get rule hierarchy from MCP server"""
    try:
        result = await mcp_client.get_mcp_resource(f"rules://{rule_type}")
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Error getting rule hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp/resources/stats/performance")
async def get_performance_stats(
    mcp_client=Depends(get_mcp_client)
):
    """Get performance statistics from MCP server"""
    try:
        result = await mcp_client.get_mcp_resource("stats://performance")
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp/resources/relationships/{rule_id}")
async def get_rule_relationships(
    rule_id: str,
    mcp_client=Depends(get_mcp_client)
):
    """Get rule relationships from MCP server"""
    try:
        result = await mcp_client.get_mcp_resource(f"relationships://{rule_id}")
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Error getting rule relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RULE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    request: CreateRuleRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Create a new rule"""
    try:
        # Determine which MCP tool to use based on rule type
        tool_map = {
            "primitive": "create_primitive_rule",
            "semantic": "create_semantic_rule", 
            "task": "create_task_rule"
        }
        
        tool_name = tool_map.get(request.rule_type)
        if not tool_name:
            raise ValueError(f"Invalid rule type: {request.rule_type}")
        
        # Prepare arguments based on rule type
        args = {
            "name": request.name,
            "description": request.description,
            "category": request.category
        }
        
        if request.rule_type == "primitive":
            args["content"] = request.content
        elif request.rule_type == "semantic":
            args["content_template"] = request.content
        elif request.rule_type == "task":
            args["prompt_template"] = request.content
            args["language"] = request.language
            args["framework"] = request.framework
            args["domain"] = request.domain
        
        result = await mcp_client.call_mcp_tool(tool_name, args)
        
        if result.get("success"):
            # Broadcast rule creation to WebSocket clients
            await ws_manager.broadcast_rule_update(
                request.rule_type, 
                result.get("rule_id"), 
                "create",
                request.dict()
            )
            
            return RuleResponse(
                success=True,
                rule_id=result.get("rule_id"),
                message="Rule created successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create rule"))
        
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
async def list_rules(
    rule_type: Optional[str] = None,
    limit: Optional[int] = 50,
    mcp_client=Depends(get_mcp_client)
):
    """List all rules or rules of a specific type"""
    try:
        if rule_type:
            result = await mcp_client.get_mcp_resource(f"rules://{rule_type}")
        else:
            # Get all rule types
            primitive_rules = await mcp_client.get_mcp_resource("rules://primitive")
            semantic_rules = await mcp_client.get_mcp_resource("rules://semantic")
            task_rules = await mcp_client.get_mcp_resource("rules://task")
            
            result = {
                "primitive": primitive_rules,
                "semantic": semantic_rules,
                "task": task_rules
            }
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_system_status(
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Get overall system status"""
    try:
        mcp_connected = mcp_client.is_connected()
        websocket_connections = ws_manager.get_connection_count()
        
        status = {
            "mcp_server": "connected" if mcp_connected else "disconnected",
            "websocket_connections": websocket_connections,
            "api_status": "healthy"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))