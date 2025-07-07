// Core types for the AI Prompt Engineering System

export interface Rule {
  id: number;
  name: string;
  type: 'primitive' | 'semantic' | 'task';
  content: string;
  description?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
  
  // Task rule specific fields
  language?: string;
  framework?: string;
  domain?: string;
  
  // Relationship information
  dependencies?: RuleRelation[];
  dependents?: RuleRelation[];
}

export interface RuleRelation {
  rule_id: number;
  name: string;
  type: string;
  weight?: number;
  order_index?: number;
  is_required?: boolean;
}

export interface PromptMetadata {
  rule_name: string;
  target_model: string;
  context_variables: string[];
  generation_time: number;
  rules_used: string[];
}

export interface PromptResult {
  prompt: string;
  metadata: PromptMetadata;
}

export interface ValidationIssue {
  rule_id: string;
  message: string;
  severity?: 'error' | 'warning' | 'info';
}

export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
  warnings: ValidationIssue[];
  suggestions: ValidationIssue[];
}

export interface SearchResult {
  rule_id: number;
  name: string;
  type: string;
  content: string;
  relevance: number;
}

export interface AnalysisResult {
  rule_type: string;
  total_rules: number;
  dependencies: Array<{
    rule_id: number;
    depends_on: number[];
    type: string;
  }>;
  relationships: Array<{
    from: string;
    to: string;
    type: string;
  }>;
  performance_metrics: {
    average_resolution_time: number;
    cache_hit_rate: number;
    total_resolutions: number;
  };
}

export interface OptimizationSuggestion {
  rule_id: string;
  suggestion: string;
  impact: 'Low' | 'Medium' | 'High';
  effort: 'Low' | 'Medium' | 'High';
}

export interface OptimizationResult {
  optimization_type: string;
  suggestions: OptimizationSuggestion[];
  potential_improvements: Array<{
    metric: string;
    current: number;
    potential: number;
    improvement: string;
  }>;
  priority_score: number;
}

export interface SystemStatus {
  mcp_server: 'connected' | 'disconnected';
  websocket_connections: number;
  api_status: 'healthy' | 'degraded' | 'unhealthy';
}

export interface PerformanceStats {
  system_stats: {
    total_rules: number;
    total_prompts_generated: number;
    average_generation_time: number;
    cache_hit_rate: number;
    uptime_hours: number;
  };
  rule_stats: {
    primitive_rules: number;
    semantic_rules: number;
    task_rules: number;
  };
  performance_metrics?: {
    queries_per_second: number;
    memory_usage_mb: number;
    disk_usage_mb: number;
  };
}

export interface WebSocketMessage {
  type: 'connection_established' | 'rule_update' | 'mcp_operation' | 'system_status';
  data?: any;
  rule_type?: string;
  rule_id?: number;
  action?: 'create' | 'update' | 'delete';
  operation?: string;
  result?: any;
  status?: SystemStatus;
  message?: string;
  timestamp: string;
}

export interface CreateRuleRequest {
  rule_type: 'primitive' | 'semantic' | 'task';
  name: string;
  content: string;
  description?: string;
  category?: string;
  
  // Task rule specific fields
  language?: string;
  framework?: string;
  domain?: string;
}

export interface UpdateRuleRequest extends Partial<CreateRuleRequest> {
  id: number;
}

export interface GeneratePromptRequest {
  rule_name: string;
  context?: Record<string, any>;
  target_model?: 'claude' | 'gpt' | 'gemini';
}

export interface SearchRulesRequest {
  query: string;
  search_type?: 'content' | 'name' | 'metadata';
  rule_type?: 'primitive' | 'semantic' | 'task' | 'all';
  limit?: number;
}

// UI State types
export interface UIState {
  loading: boolean;
  error: string | null;
  selectedRules: number[];
  viewMode: 'list' | 'grid' | 'hierarchy';
  filterCategory: string | null;
  filterType: 'all' | 'primitive' | 'semantic' | 'task';
}

export interface EditorState {
  content: string;
  isDirty: boolean;
  isValid: boolean;
  validationErrors: string[];
  cursorPosition: number;
}

export interface PlaygroundState {
  selectedRule: Rule | null;
  context: Record<string, any>;
  targetModel: 'claude' | 'gpt' | 'gemini';
  generatedPrompt: PromptResult | null;
  isGenerating: boolean;
}