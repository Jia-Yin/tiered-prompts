"""
API Routes for Web Interface
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import httpx

from app.models.requests import (
    GeneratePromptRequest,
    AnalyzeRulesRequest, 
    ValidateRulesRequest,
    SearchRulesRequest,
    OptimizeRulesRequest,
    CreateRuleRequest,
    UpdateRuleRequest
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

@router.get("/rules/{rule_id}")
async def get_rule(
    rule_id: int,
    mcp_client=Depends(get_mcp_client)
):
    """Get a specific rule by ID"""
    try:
        # Use the direct MCP endpoint for getting a single rule
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/tools/get_rule/{rule_id}", timeout=30.0)
            response.raise_for_status()
            return response.json()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Rule not found")
        else:
            logger.error(f"HTTP error getting rule {rule_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    request: UpdateRuleRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Update an existing rule"""
    try:
        # First, get the current rule to determine its type
        current_rule = None
        rule_type = None
        
        rule_types = ["primitive", "semantic", "task"]
        for rt in rule_types:
            try:
                result = await mcp_client.get_mcp_resource(f"rules://{rt}")
                if isinstance(result, str):
                    import json
                    parsed_result = json.loads(result)
                    if "rules" in parsed_result:
                        for rule in parsed_result["rules"]:
                            if rule.get("id") == rule_id:
                                current_rule = rule
                                rule_type = rt
                                break
                elif isinstance(result, dict) and "rules" in result:
                    for rule in result["rules"]:
                        if rule.get("id") == rule_id:
                            current_rule = rule
                            rule_type = rt
                            break
                if current_rule:
                    break
            except Exception:
                continue
        
        if not current_rule or not rule_type:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Determine which MCP tool to use based on rule type
        tool_map = {
            "primitive": "update_primitive_rule",
            "semantic": "update_semantic_rule",
            "task": "update_task_rule"
        }
        
        tool_name = tool_map.get(rule_type)
        if not tool_name:
            raise ValueError(f"Invalid rule type: {rule_type}")
        
        # Prepare arguments for update
        args = {"rule_id": rule_id}
        
        # Add non-None fields from request
        if request.name is not None:
            args["name"] = request.name
        if request.description is not None:
            args["description"] = request.description
        if request.category is not None:
            args["category"] = request.category
        if request.content is not None:
            if rule_type == "primitive":
                args["content"] = request.content
            elif rule_type == "semantic":
                args["content_template"] = request.content
            elif rule_type == "task":
                args["prompt_template"] = request.content
        
        # Task-specific fields
        if rule_type == "task":
            if request.language is not None:
                args["language"] = request.language
            if request.framework is not None:
                args["framework"] = request.framework
            if request.domain is not None:
                args["domain"] = request.domain
        
        result = await mcp_client.call_mcp_tool(tool_name, args)
        
        if result.get("success"):
            # Broadcast rule update to WebSocket clients
            await ws_manager.broadcast_rule_update(
                rule_type,
                rule_id,
                "update",
                request.dict(exclude_none=True)
            )
            
            return RuleResponse(
                success=True,
                rule_id=rule_id,
                message="Rule updated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update rule"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}", response_model=RuleResponse)
async def delete_rule(
    rule_id: int,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Delete a rule"""
    try:
        # First, get the current rule to determine its type
        current_rule = None
        rule_type = None
        
        rule_types = ["primitive", "semantic", "task"]
        for rt in rule_types:
            try:
                result = await mcp_client.get_mcp_resource(f"rules://{rt}")
                if isinstance(result, str):
                    import json
                    parsed_result = json.loads(result)
                    if "rules" in parsed_result:
                        for rule in parsed_result["rules"]:
                            if rule.get("id") == rule_id:
                                current_rule = rule
                                rule_type = rt
                                break
                elif isinstance(result, dict) and "rules" in result:
                    for rule in result["rules"]:
                        if rule.get("id") == rule_id:
                            current_rule = rule
                            rule_type = rt
                            break
                if current_rule:
                    break
            except Exception:
                continue
        
        if not current_rule or not rule_type:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Determine which MCP tool to use based on rule type
        tool_map = {
            "primitive": "delete_primitive_rule",
            "semantic": "delete_semantic_rule",
            "task": "delete_task_rule"
        }
        
        tool_name = tool_map.get(rule_type)
        if not tool_name:
            raise ValueError(f"Invalid rule type: {rule_type}")
        
        # Call the delete tool
        result = await mcp_client.call_mcp_tool(tool_name, {"rule_id": rule_id})
        
        if result.get("success"):
            # Broadcast rule deletion to WebSocket clients
            await ws_manager.broadcast_rule_update(
                rule_type,
                rule_id,
                "delete",
                {"rule_id": rule_id}
            )
            
            return RuleResponse(
                success=True,
                rule_id=rule_id,
                message="Rule deleted successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete rule"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RELATIONSHIP MANAGEMENT ENDPOINTS
# ============================================================================

class CreateRelationRequest(BaseModel):
    """Request model for creating relationships"""
    task_rule_id: Optional[int] = None
    semantic_rule_id: Optional[int] = None
    primitive_rule_id: Optional[int] = None
    weight: float = 1.0
    order_index: int = 0
    is_required: bool = True
    context_override: Optional[Dict[str, Any]] = None

class DeleteRelationRequest(BaseModel):
    """Request model for deleting relationships"""
    task_rule_id: Optional[int] = None
    semantic_rule_id: Optional[int] = None
    primitive_rule_id: Optional[int] = None

@router.post("/relationships/task-semantic")
async def create_task_semantic_relation(
    request: CreateRelationRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Create a relationship between task and semantic rule"""
    try:
        if not request.task_rule_id or not request.semantic_rule_id:
            raise HTTPException(status_code=400, detail="Both task_rule_id and semantic_rule_id are required")
        
        result = await mcp_client.call_mcp_tool("create_task_semantic_relation", {
            "task_rule_id": request.task_rule_id,
            "semantic_rule_id": request.semantic_rule_id,
            "weight": request.weight,
            "order_index": request.order_index,
            "is_required": request.is_required,
            "context_override": request.context_override
        })
        
        if result.get("success"):
            # TODO: Broadcast relationship creation to WebSocket clients when available
            # await ws_manager.broadcast_operation("relationship_created", {
            #     "type": "task_semantic",
            #     "task_rule_id": request.task_rule_id,
            #     "semantic_rule_id": request.semantic_rule_id,
            #     "relation_id": result.get("relation_id")
            # })
            
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create relationship"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task-semantic relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationships/semantic-primitive")
async def create_semantic_primitive_relation(
    request: CreateRelationRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Create a relationship between semantic and primitive rule"""
    try:
        if not request.semantic_rule_id or not request.primitive_rule_id:
            raise HTTPException(status_code=400, detail="Both semantic_rule_id and primitive_rule_id are required")
        
        result = await mcp_client.call_mcp_tool("create_semantic_primitive_relation", {
            "semantic_rule_id": request.semantic_rule_id,
            "primitive_rule_id": request.primitive_rule_id,
            "weight": request.weight,
            "order_index": request.order_index,
            "is_required": request.is_required
        })
        
        if result.get("success"):
            # TODO: Broadcast relationship creation to WebSocket clients when available
            # await ws_manager.broadcast_operation("relationship_created", {
            #     "type": "semantic_primitive", 
            #     "semantic_rule_id": request.semantic_rule_id,
            #     "primitive_rule_id": request.primitive_rule_id,
            #     "relation_id": result.get("relation_id")
            # })
            
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create relationship"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating semantic-primitive relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/task-semantic")
async def get_task_semantic_relations(
    task_rule_id: Optional[int] = None,
    mcp_client=Depends(get_mcp_client)
):
    """Get task-semantic relationships"""
    try:
        # Use direct HTTP call to MCP server
        async with httpx.AsyncClient() as client:
            url = "http://localhost:8001/tools/get_task_semantic_relations"
            if task_rule_id:
                url += f"?task_rule_id={task_rule_id}"
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        
    except Exception as e:
        logger.error(f"Error getting task-semantic relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/semantic-primitive")
async def get_semantic_primitive_relations(
    semantic_rule_id: Optional[int] = None,
    mcp_client=Depends(get_mcp_client)
):
    """Get semantic-primitive relationships"""
    try:
        # Use direct HTTP call to MCP server
        async with httpx.AsyncClient() as client:
            url = "http://localhost:8001/tools/get_semantic_primitive_relations"
            if semantic_rule_id:
                url += f"?semantic_rule_id={semantic_rule_id}"
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        
    except Exception as e:
        logger.error(f"Error getting semantic-primitive relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/relationships/task-semantic")
async def delete_task_semantic_relation(
    request: DeleteRelationRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Delete a task-semantic relationship"""
    try:
        if not request.task_rule_id or not request.semantic_rule_id:
            raise HTTPException(status_code=400, detail="Both task_rule_id and semantic_rule_id are required")
        
        # Use direct HTTP call to MCP server  
        async with httpx.AsyncClient() as client:
            response = await client.request(
                "DELETE",
                "http://localhost:8001/tools/delete_task_semantic_relation",
                json={
                    "task_rule_id": request.task_rule_id,
                    "semantic_rule_id": request.semantic_rule_id
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        if result.get("success"):
            # TODO: Broadcast relationship deletion to WebSocket clients when available
            # await ws_manager.broadcast_operation("relationship_deleted", {
            #     "type": "task_semantic",
            #     "task_rule_id": request.task_rule_id,
            #     "semantic_rule_id": request.semantic_rule_id
            # })
            
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete relationship"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task-semantic relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/relationships/semantic-primitive")
async def delete_semantic_primitive_relation(
    request: DeleteRelationRequest,
    mcp_client=Depends(get_mcp_client),
    ws_manager=Depends(get_websocket_manager)
):
    """Delete a semantic-primitive relationship"""
    try:
        if not request.semantic_rule_id or not request.primitive_rule_id:
            raise HTTPException(status_code=400, detail="Both semantic_rule_id and primitive_rule_id are required")
        
        # Use direct HTTP call to MCP server
        async with httpx.AsyncClient() as client:
            response = await client.request(
                "DELETE",
                "http://localhost:8001/tools/delete_semantic_primitive_relation",
                json={
                    "semantic_rule_id": request.semantic_rule_id,
                    "primitive_rule_id": request.primitive_rule_id
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        if result.get("success"):
            # TODO: Broadcast relationship deletion to WebSocket clients when available
            # await ws_manager.broadcast_operation("relationship_deleted", {
            #     "type": "semantic_primitive",
            #     "semantic_rule_id": request.semantic_rule_id,
            #     "primitive_rule_id": request.primitive_rule_id
            # })
            
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete relationship"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting semantic-primitive relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/dependencies/{rule_type}/{rule_id}")
async def get_rule_dependencies(
    rule_type: str,
    rule_id: int,
    mcp_client=Depends(get_mcp_client)
):
    """Get dependencies for a specific rule"""
    try:
        # Use direct HTTP call to MCP server
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8001/tools/get_rule_dependencies/{rule_type}/{rule_id}",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        
    except Exception as e:
        logger.error(f"Error getting rule dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/hierarchy")
async def get_rule_hierarchy(
    mcp_client=Depends(get_mcp_client)
):
    """Get complete rule hierarchy with relationships"""
    try:
        # Use direct HTTP call to MCP server
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8001/tools/get_rule_hierarchy",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        
    except Exception as e:
        logger.error(f"Error getting rule hierarchy: {e}")
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