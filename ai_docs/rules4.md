# Rules Extracted from Phase 4 Development Session

## File Management and Project Structure Rules

### R4.1: Module Resolution Strategy
**Category**: Development Process  
**Type**: Constraint  
**Rule**: When facing React module resolution errors with TypeScript path aliases (@/), prefer switching to relative imports over complex path configuration.  
**Context**: React compilation failed with `@/components/Layout/Layout` imports  
**Solution Applied**: Changed to `./components/Layout/Layout` relative imports  
**Rationale**: Simpler, more reliable, and works across different build environments  

### R4.2: Git Ignore Best Practices
**Category**: Project Setup  
**Type**: Standard  
**Rule**: Always create separate .gitignore files for frontend and backend in multi-component projects  
**Implementation**:
- Frontend: Include `node_modules/`, `dist/`, `.env.*`, coverage reports
- Backend: Include `*.db`, `__pycache__/`, `.env`, `uv.lock`, virtual environments  
**Benefit**: Prevents accidental commits of generated files and secrets  

### R4.3: Database Path Configuration
**Category**: Configuration  
**Type**: Constraint  
**Rule**: Always use absolute paths for database connections to prevent unwanted folder creation  
**Anti-pattern**: `os.path.join("database", "prompt_system.db")` creates `/database` in project root  
**Correct Pattern**: `os.path.join(project_root, "ai_prompt_system", "database", "prompt_system.db")`  
**Impact**: Prevents cluttering project structure with unintended directories  

## Architecture and Integration Rules

### R4.4: Real Data Integration Strategy
**Category**: System Architecture  
**Type**: Process  
**Rule**: When replacing mock data with real data, implement and test the full data flow path systematically  
**Process**:
1. Verify database connectivity and schema compatibility
2. Update backend HTTP clients to call real services  
3. Fix response parsing (e.g., `.text` vs `.text()`)
4. Test search functionality with actual data
5. Validate frontend rendering with real data structures  
**Critical**: Each layer must be verified independently before testing end-to-end  

### R4.5: React Key Uniqueness for Multi-Type Collections
**Category**: React Development  
**Type**: Best Practice  
**Rule**: When rendering collections with potentially overlapping IDs across different types, use composite keys  
**Pattern**: `key={`${item.type}-${item.id}`}` instead of `key={item.id}`  
**Context**: Different rule types (primitive, semantic, task) can have same numeric IDs  
**Benefit**: Prevents React rendering warnings and ensures proper component lifecycle  

### R4.6: Database Schema Mapping for Search
**Category**: Database Operations  
**Type**: Implementation  
**Rule**: When searching across heterogeneous tables, implement dynamic column mapping  
**Implementation**:
```sql
-- Map content columns by table type
primitive_rules.content
semantic_rules.content_template  
task_rules.prompt_template
```
**Rationale**: Different rule types store content in differently named columns  
**Search Pattern**: Use table-specific column names but alias to common name for uniform results  

## Error Handling and Debugging Rules

### R4.7: Service Dependency Chain Debugging
**Category**: Troubleshooting  
**Type**: Process  
**Rule**: When debugging multi-service communication, verify each layer independently  
**Debug Chain**:
1. Frontend → Backend API (check network requests)
2. Backend → MCP HTTP Wrapper (verify HTTP client calls)  
3. MCP Wrapper → Database (test direct database queries)
4. Database → Results (validate data format and content)  
**Tool**: Use browser dev tools, server logs, and direct database queries  

### R4.8: WebSocket Connection Error Interpretation
**Category**: System Monitoring  
**Type**: Knowledge  
**Rule**: WebSocket connection errors during development are often normal and expected  
**Context**: "Download the React DevTools" and connection errors are typically harmless  
**Action**: Focus on actual functionality rather than connection warnings during active development  
**Exception**: Investigate if WebSocket functionality is specifically required  

## Documentation and Communication Rules

### R4.9: Progressive Documentation Updates
**Category**: Documentation  
**Type**: Process  
**Rule**: Update documentation immediately when scope or capabilities change during development  
**Trigger Events**:
- Feature implementation completion
- Scope reduction (e.g., CRUD → READ-only)
- Architecture changes
- Limitation discoveries  
**Format**: Include both "What was implemented" and "What was NOT implemented" sections  

### R4.10: Limitation Transparency
**Category**: Project Communication  
**Type**: Standard  
**Rule**: Always explicitly document limitations and missing features in phase completion documentation  
**Implementation**:
- Create "Limitations and Scope" sections
- Use clear ❌/✅ indicators for feature status
- Explain why features were not implemented (scope, time, dependencies)
- Provide clear path forward for future phases  

## Performance and Optimization Rules

### R4.11: Search Performance Optimization
**Category**: Database Operations  
**Type**: Best Practice  
**Rule**: Implement relevance scoring for search results to improve user experience  
**Scoring Logic**:
- Name matches: 0.95 relevance
- Content matches: 0.8 relevance  
- Description matches: 0.6 relevance
**Additional**: Sort by relevance and limit results for better performance  

### R4.12: HTTP Response Handling
**Category**: Integration  
**Type**: Implementation  
**Rule**: Distinguish between HTTP response properties and methods in client code  
**Common Error**: `response.text()` vs `response.text`  
**Fix Pattern**: Check API documentation for correct property access  
**Context**: FastAPI clients may expose response content as properties, not methods  

## Development Workflow Rules

### R4.13: Feature Implementation Scope Management  
**Category**: Project Management  
**Type**: Strategy  
**Rule**: When implementing complex features, clearly define and stick to phase boundaries  
**Phase 4 Example**: Implement READ operations completely before attempting CREATE/UPDATE/DELETE  
**Benefit**: Delivers working functionality incrementally and provides stable foundation  
**Risk Mitigation**: Prevents scope creep and incomplete feature delivery  

### R4.14: Multi-Service Startup Dependencies
**Category**: Development Operations  
**Type**: Process  
**Rule**: When running multi-service architecture, start services in dependency order  
**Order for This Project**:
1. Database (SQLite - always available)
2. MCP HTTP Wrapper (port 8001) 
3. Backend API (port 8000)
4. Frontend (port 3000)  
**Verification**: Test each service health endpoint before starting dependent services  

### R4.15: TypeScript Type Safety in Data Transformation
**Category**: Frontend Development  
**Type**: Best Practice  
**Rule**: Maintain type safety when transforming API responses to frontend types  
**Pattern**:
```typescript
const results: Rule[] = response.results.map(result => ({
  id: result.rule_id, // Transform API field names
  name: result.name,
  type: result.type as 'primitive' | 'semantic' | 'task', // Type assertion
  content: result.content,
}));
```
**Benefit**: Catches type mismatches early and provides better IDE support  

## Testing and Validation Rules

### R4.16: End-to-End Data Flow Validation
**Category**: Quality Assurance  
**Type**: Process  
**Rule**: For data integration features, test with specific real data examples  
**Example**: Search for "vue" should return "Vue SFC Ordering" rule  
**Validation Points**:
- Data exists in database
- Search query reaches database correctly
- Results are returned with proper formatting
- Frontend displays results correctly  

### R4.17: Architecture Component Testing
**Category**: System Testing  
**Type**: Strategy  
**Rule**: Test each architectural component independently before integration testing  
**Components**:
- Database queries (direct SQL)
- MCP wrapper endpoints (HTTP calls)
- Backend API endpoints (API testing)
- Frontend components (unit/integration tests)  
**Integration**: Only test full stack after each component works independently  

## Code Quality Rules

### R4.18: Import Path Consistency
**Category**: Code Organization  
**Type**: Standard  
**Rule**: Maintain consistent import path strategy throughout the project  
**Decision**: Use relative imports for internal components  
**Pattern**: `import Layout from './components/Layout/Layout'`  
**Avoid**: Mixing relative imports with path aliases in the same project  

### R4.19: Error Boundary Implementation
**Category**: React Development  
**Type**: Best Practice  
**Rule**: Implement proper error handling for async operations in React components  
**Pattern**:
```typescript
try {
  const result = await apiCall();
  setData(result);
} catch (error) {
  console.error('Operation failed:', error);
  setData([]);
} finally {
  setLoading(false);
}
```
**Benefit**: Prevents application crashes and provides user feedback  

### R4.20: Component Placeholder Strategy
**Category**: Development Process  
**Type**: Implementation  
**Rule**: Create meaningful placeholder components for referenced but unimplemented features  
**Implementation**:
```tsx
const RuleEditor: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Rule Editor</h1>
      <p className="text-gray-600">Coming in Phase 5</p>
    </div>
  );
};
```
**Benefit**: Prevents build errors while communicating feature status to users