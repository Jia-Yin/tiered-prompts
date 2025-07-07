import axios from 'axios';
import {
  Rule,
  PromptResult,
  ValidationResult,
  SearchResult,
  AnalysisResult,
  OptimizationResult,
  SystemStatus,
  PerformanceStats,
  CreateRuleRequest,
  UpdateRuleRequest,
  GeneratePromptRequest,
  SearchRulesRequest
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// MCP TOOL API CALLS
// ============================================================================

export const generatePrompt = async (request: GeneratePromptRequest): Promise<PromptResult> => {
  const response = await api.post('/mcp/generate-prompt', request);
  return response.data;
};

export const analyzeRules = async (params: {
  rule_type?: string;
  include_dependencies?: boolean;
  rule_id?: number;
}): Promise<AnalysisResult> => {
  const response = await api.post('/mcp/analyze-rules', params);
  return response.data;
};

export const validateRules = async (params: {
  rule_type?: string;
  rule_id?: number;
  detailed?: boolean;
}): Promise<ValidationResult> => {
  const response = await api.post('/mcp/validate-rules', params);
  return response.data;
};

export const searchRules = async (request: SearchRulesRequest): Promise<{
  query: string;
  results: SearchResult[];
  total_found: number;
  search_time: number;
}> => {
  const response = await api.post('/mcp/search-rules', request);
  return response.data;
};

export const optimizeRules = async (params: {
  optimization_type?: string;
  rule_type?: string;
}): Promise<OptimizationResult> => {
  const response = await api.post('/mcp/optimize-rules', params);
  return response.data;
};

// ============================================================================
// MCP RESOURCE API CALLS
// ============================================================================

export const getRuleHierarchy = async (ruleType: string): Promise<any> => {
  const response = await api.get(`/mcp/resources/rules/${ruleType}`);
  return JSON.parse(response.data.data);
};

export const getPerformanceStats = async (): Promise<PerformanceStats> => {
  const response = await api.get('/mcp/resources/stats/performance');
  return JSON.parse(response.data.data);
};

export const getRuleRelationships = async (ruleId: string): Promise<any> => {
  const response = await api.get(`/mcp/resources/relationships/${ruleId}`);
  return JSON.parse(response.data.data);
};

// ============================================================================
// RULE MANAGEMENT API CALLS
// ============================================================================

export const listRules = async (params?: {
  rule_type?: string;
  limit?: number;
}): Promise<Rule[]> => {
  const response = await api.get('/rules', { params });
  
  // Handle different response formats
  if (response.data.data) {
    const data = response.data.data;
    
    // Case 1: Specific rule type requested - returns {rule_type, rules, total_rules}
    if (params?.rule_type && data.rules && Array.isArray(data.rules)) {
      return data.rules.map((rule: any) => ({
        ...rule,
        type: params.rule_type, // Ensure type is set correctly
        id: rule.id // Keep original numeric ID
      }));
    }
    
    // Case 2: All rule types - returns {primitive: {...}, semantic: {...}, task: {...}}
    if (data.primitive || data.semantic || data.task) {
      const allRules: Rule[] = [];
      Object.entries(data).forEach(([type, typeData]: [string, any]) => {
        if (typeData) {
          // Handle string response (needs parsing)
          if (typeof typeData === 'string') {
            try {
              const parsedRules = JSON.parse(typeData);
              if (parsedRules.rules && Array.isArray(parsedRules.rules)) {
                allRules.push(...parsedRules.rules.map((rule: any) => ({ 
                  ...rule, 
                  type,
                  id: rule.id // Keep original numeric ID
                })));
              }
            } catch (e) {
              console.error(`Failed to parse ${type} rules:`, e);
            }
          }
          // Handle object response
          else if (typeof typeData === 'object' && typeData.rules && Array.isArray(typeData.rules)) {
            allRules.push(...typeData.rules.map((rule: any) => ({ 
              ...rule, 
              type,
              id: rule.id // Keep original numeric ID
            })));
          }
        }
      });
      return allRules;
    }
    
    // Case 3: Direct array
    if (Array.isArray(data)) {
      return data;
    }
  }
  
  return [];
};

export const createRule = async (request: CreateRuleRequest): Promise<{
  success: boolean;
  rule_id?: number;
  message: string;
}> => {
  const response = await api.post('/rules', request);
  return response.data;
};

export const updateRule = async (id: number, request: Partial<UpdateRuleRequest>): Promise<{
  success: boolean;
  message: string;
}> => {
  const response = await api.put(`/rules/${id}`, request);
  return response.data;
};

export const deleteRule = async (id: number): Promise<{
  success: boolean;
  message: string;
}> => {
  const response = await api.delete(`/rules/${id}`);
  return response.data;
};

export const getRule = async (id: number): Promise<Rule> => {
  const response = await api.get(`/rules/${id}`);
  return response.data.rule;
};

// ============================================================================
// SYSTEM STATUS API CALLS
// ============================================================================

export const getSystemStatus = async (): Promise<SystemStatus> => {
  const response = await api.get('/status');
  return response.data;
};

export const getHealthCheck = async (): Promise<{
  status: string;
  mcp_server: string;
  active_websockets: number;
}> => {
  const response = await api.get('/health');
  return response.data;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const downloadRules = async (format: 'json' | 'yaml' = 'json'): Promise<Blob> => {
  const response = await api.get(`/export/rules?format=${format}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const uploadRules = async (file: File): Promise<{
  success: boolean;
  imported_count: number;
  message: string;
}> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/import/rules', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Error handler utility
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default api;