"""
Request models for API endpoints
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class GeneratePromptRequest(BaseModel):
    """Request for generating a prompt"""
    rule_name: str = Field(..., description="Name of the task rule to generate prompt for")
    context: Optional[Dict[str, Any]] = Field(None, description="Context variables for template rendering")
    target_model: str = Field("claude", description="Target AI model (claude, gpt, gemini)")

class AnalyzeRulesRequest(BaseModel):
    """Request for analyzing rules"""
    rule_type: str = Field("all", description="Type of rules to analyze (primitive, semantic, task, all)")
    include_dependencies: bool = Field(True, description="Whether to include dependency analysis")
    rule_id: Optional[int] = Field(None, description="Specific rule ID to analyze")

class ValidateRulesRequest(BaseModel):
    """Request for validating rules"""
    rule_type: str = Field("all", description="Type of rules to validate (primitive, semantic, task, all)")
    rule_id: Optional[int] = Field(None, description="Specific rule ID to validate")
    detailed: bool = Field(False, description="Whether to provide detailed validation results")

class SearchRulesRequest(BaseModel):
    """Request for searching rules"""
    query: str = Field(..., description="Search query string")
    search_type: str = Field("content", description="Type of search (content, name, metadata)")
    rule_type: str = Field("all", description="Type of rules to search (primitive, semantic, task, all)")
    limit: int = Field(10, description="Maximum number of results to return")

class OptimizeRulesRequest(BaseModel):
    """Request for optimizing rules"""
    optimization_type: str = Field("performance", description="Type of optimization (performance, structure, content)")
    rule_type: str = Field("all", description="Type of rules to optimize (primitive, semantic, task, all)")

class CreateRuleRequest(BaseModel):
    """Request for creating a new rule"""
    rule_type: str = Field(..., description="Type of rule (primitive, semantic, task)")
    name: str = Field(..., description="Unique name for the rule")
    content: str = Field(..., description="Rule content/template")
    description: Optional[str] = Field(None, description="Description of what the rule does")
    category: Optional[str] = Field(None, description="Rule category")
    
    # Task rule specific fields
    language: Optional[str] = Field(None, description="Programming language or context")
    framework: Optional[str] = Field(None, description="Framework or technology")
    domain: Optional[str] = Field(None, description="Domain area (web_dev, data_science, etc.)")

class UpdateRuleRequest(BaseModel):
    """Request for updating an existing rule"""
    name: Optional[str] = Field(None, description="Updated name for the rule")
    content: Optional[str] = Field(None, description="Updated rule content/template")
    description: Optional[str] = Field(None, description="Updated description")
    category: Optional[str] = Field(None, description="Updated category")
    
    # Task rule specific fields
    language: Optional[str] = Field(None, description="Updated programming language")
    framework: Optional[str] = Field(None, description="Updated framework")
    domain: Optional[str] = Field(None, description="Updated domain")

class CreateRelationshipRequest(BaseModel):
    """Request for creating a rule relationship"""
    parent_rule_type: str = Field(..., description="Type of parent rule (task, semantic)")
    parent_rule_name: str = Field(..., description="Name of parent rule")
    child_rule_type: str = Field(..., description="Type of child rule (semantic, primitive)")
    child_rule_name: str = Field(..., description="Name of child rule")
    weight: float = Field(1.0, description="Relationship weight (0.0-1.0)")
    order_index: int = Field(0, description="Order in which child rule should appear")
    is_required: bool = Field(True, description="Whether the child rule is required")