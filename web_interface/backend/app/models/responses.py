"""
Response models for API endpoints
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class PromptMetadata(BaseModel):
    """Metadata for generated prompts"""
    rule_name: str
    target_model: str
    context_variables: List[str]
    generation_time: float
    rules_used: List[str]

class PromptResponse(BaseModel):
    """Response for prompt generation"""
    prompt: str = Field(..., description="Generated prompt content")
    metadata: PromptMetadata = Field(..., description="Prompt generation metadata")

class AnalysisResponse(BaseModel):
    """Response for rule analysis"""
    rule_type: str = Field(..., description="Type of rules analyzed")
    total_rules: int = Field(..., description="Total number of rules")
    dependencies: List[Dict[str, Any]] = Field(..., description="Rule dependencies")
    relationships: List[Dict[str, Any]] = Field(..., description="Rule relationships")
    performance_metrics: Dict[str, Union[int, float]] = Field(..., description="Performance metrics")

class ValidationIssue(BaseModel):
    """Validation issue details"""
    rule_id: str
    message: str
    severity: Optional[str] = None

class ValidationResponse(BaseModel):
    """Response for rule validation"""
    valid: bool = Field(..., description="Whether validation passed")
    issues: List[ValidationIssue] = Field(..., description="Validation issues found")
    warnings: List[ValidationIssue] = Field(..., description="Validation warnings")
    suggestions: List[ValidationIssue] = Field(..., description="Optimization suggestions")

class SearchResult(BaseModel):
    """Single search result"""
    rule_id: int
    name: str
    type: str
    content: str
    relevance: float

class SearchResponse(BaseModel):
    """Response for rule search"""
    query: str = Field(..., description="Search query used")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    search_time: float = Field(..., description="Time taken for search in seconds")

class OptimizationSuggestion(BaseModel):
    """Optimization suggestion details"""
    rule_id: str
    suggestion: str
    impact: str
    effort: str

class PotentialImprovement(BaseModel):
    """Potential improvement details"""
    metric: str
    current: float
    potential: float
    improvement: str

class OptimizationResponse(BaseModel):
    """Response for rule optimization"""
    optimization_type: str = Field(..., description="Type of optimization performed")
    suggestions: List[OptimizationSuggestion] = Field(..., description="Optimization suggestions")
    potential_improvements: List[PotentialImprovement] = Field(..., description="Potential improvements")
    priority_score: float = Field(..., description="Priority score for optimization")

class RuleResponse(BaseModel):
    """Response for rule operations"""
    success: bool = Field(..., description="Whether operation was successful")
    rule_id: Optional[int] = Field(None, description="ID of affected rule")
    message: str = Field(..., description="Operation result message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

class SystemStatus(BaseModel):
    """System status information"""
    mcp_server: str = Field(..., description="MCP server connection status")
    websocket_connections: int = Field(..., description="Number of active WebSocket connections")
    api_status: str = Field(..., description="API server status")
    
class ErrorResponse(BaseModel):
    """Error response format"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")

class ListRulesResponse(BaseModel):
    """Response for listing rules"""
    rules: List[Dict[str, Any]] = Field(..., description="List of rules")
    total_count: int = Field(..., description="Total number of rules")
    rule_type: Optional[str] = Field(None, description="Type of rules listed")

class RuleDetails(BaseModel):
    """Detailed rule information"""
    id: int
    name: str
    type: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Task rule specific fields
    language: Optional[str] = None
    framework: Optional[str] = None
    domain: Optional[str] = None
    
    # Relationship information
    dependencies: Optional[List[Dict[str, Any]]] = None
    dependents: Optional[List[Dict[str, Any]]] = None

class GetRuleResponse(BaseModel):
    """Response for getting a specific rule"""
    rule: RuleDetails = Field(..., description="Rule details")

class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: str = Field(..., description="Message timestamp")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall health status")
    mcp_server: str = Field(..., description="MCP server status")
    active_websockets: int = Field(..., description="Number of active WebSocket connections")
    uptime: Optional[float] = Field(None, description="Server uptime in seconds")