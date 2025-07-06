# Claude Desktop Integration Guide

## Prerequisites

1. Claude Desktop application installed
2. AI Prompt Engineering System MCP Server set up
3. `uv` package manager installed and configured in mcp_server folder
4. Dependencies installed via `uv sync` in the mcp_server directory

## Configuration

### 1. Locate Claude Desktop Config

The Claude Desktop configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### 2. Add MCP Server Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-prompt-engineering": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp_server.py"
      ],
      "cwd": "/home/jyw/Program/tiered-prompts/mcp_server",
      "env": {
        "MCP_SERVER_ENVIRONMENT": "production",
        "MCP_SERVER_LOG_LEVEL": "INFO",
        "MCP_SERVER_CACHE_SIZE": "1000",
        "PROJECT_ROOT": "/home/jyw/Program/tiered-prompts"
      }
    }
  }
}
```

**Important Notes**:
- Update the paths in `cwd` to match your installation directory
- The `cwd` should point to the `mcp_server` directory where `pyproject.toml` is located
- Using `uv run` ensures proper dependency management and virtual environment activation
- The `PROJECT_ROOT` environment variable tells the server where to find the database
- The server will automatically change to the project root directory for database access

### 3. Test the Integration

1. **Run the integration test:**
   ```bash
   cd /home/jyw/Program/tiered-prompts/mcp_server
   python test_integration.py
   ```
   This will verify uv setup, dependencies, and server startup.

2. **Test server manually:**
   ```bash
   cd /home/jyw/Program/tiered-prompts/mcp_server
   PROJECT_ROOT=/home/jyw/Program/tiered-prompts uv run python fastmcp_server.py
   ```
   You should see logs indicating successful startup and rule engine initialization:
   ```
   INFO:__main__:Starting AI Prompt Engineering System FastMCP Server...
   INFO:__main__:Available tools: generate_prompt, analyze_rules, validate_rules, search_rules, optimize_rules
   INFO:__main__:Initializing rule engine services...
   INFO:__main__:Rule engine services initialized successfully
   ```

3. **Restart Claude Desktop**
4. **Look for the MCP server in the available tools**
5. **Try using the prompt generation tool:**
   - Tool: `generate_prompt`
   - Rule name: `react_component_review`
   - Context: `{"component": "UserProfile"}`
   - Target model: `claude`

## Available Tools

### Core Tools
- **generate_prompt**: Generate prompts from rule hierarchy
- **analyze_rules**: Analyze rule dependencies and relationships
- **validate_rules**: Validate rule consistency
- **search_rules**: Search rules by content or metadata
- **optimize_rules**: Get optimization suggestions

### Resources
- **rules://primitive**: Get primitive rule hierarchy (P1-P24)
- **rules://semantic**: Get semantic rule hierarchy (S1-S12)
- **rules://task**: Get task rule hierarchy (T1-T8)
- **stats://performance**: Get system performance statistics
- **relationships://{rule_id}**: Get relationships for specific rule

### Prompts
- **create_rule_prompt**: Assistance for creating new rules
- **debug_rule_prompt**: Help with debugging rule issues

## Troubleshooting

### Server Not Starting
1. **Check uv installation:** `uv --version`
2. **Verify dependencies:** `cd mcp_server && uv sync`
3. **Test dependencies:** `cd mcp_server && PROJECT_ROOT=/home/jyw/Program/tiered-prompts uv run python -c "import mcp; import pydantic; print('OK')"`
4. **Test server manually:** `cd mcp_server && PROJECT_ROOT=/home/jyw/Program/tiered-prompts uv run python fastmcp_server.py`
5. **Check configuration paths:** Ensure `cwd` points to the mcp_server directory
6. **Verify PROJECT_ROOT:** Ensure the environment variable points to the correct project directory
7. **Check database access:** Verify the database file exists at `$PROJECT_ROOT/ai_prompt_system/database/prompt_system.db`

### Tools Not Available
1. Check Claude Desktop logs for connection errors
2. Verify the server path in configuration is correct
3. Ensure the server process has proper permissions

### Performance Issues
1. Check system health: `python mcp_server/utils/health_check.py`
2. Monitor server logs: `tail -f mcp_server.log`
3. Adjust cache settings in configuration if needed

## Best Practices

1. **Rule Management**: Use descriptive rule names and clear hierarchies
2. **Context Variables**: Provide meaningful context for better prompts
3. **Performance**: Monitor response times and adjust cache settings
4. **Debugging**: Use validation tools to check rule consistency

## Example Workflows

### 1. **查詢規則階層**
**獲取所有 primitive rules:**
```
Resource: rules://primitive
```
**或在對話中詢問:** "請獲取所有的 primitive rules，我想了解基礎規則有哪些。"

**獲取所有 semantic rules:**
```
Resource: rules://semantic
```
**或在對話中詢問:** "請列出所有的 semantic rules 及其結構。"

**獲取所有 task rules:**
```
Resource: rules://task
```
**或在對話中詢問:** "請顯示所有的 task rules，我想了解任務級別的規則。"

### 2. **搜尋特定規則**
```
Tool: search_rules
Args: {
  "query": "虛擬環境",
  "search_type": "content",
  "rule_type": "all",
  "limit": 10
}
```
**或在對話中詢問:** "請搜尋所有與虛擬環境相關的規則。"

### 3. **分析規則關係**
```
Tool: analyze_rules
Args: {
  "rule_type": "semantic",
  "include_dependencies": true
}
```
**或在對話中詢問:** "請分析所有 semantic rules 的依賴關係。"

### 4. **生成 Code Review 提示**
```
Tool: generate_prompt
Args: {
  "rule_name": "react_component_review",
  "context": {
    "component_name": "UserProfile",
    "framework": "React",
    "complexity": "medium"
  },
  "target_model": "claude"
}
```

### 5. **規則分析**
```
Tool: analyze_rules
Args: {
  "rule_type": "semantic",
  "include_dependencies": true
}
```

### 6. **規則搜尋**
```
Tool: search_rules
Args: {
  "query": "code quality",
  "search_type": "content",
  "limit": 10
}
```

## 🗣️ **在 Claude 中查詢規則的方法**

### **方式 1: 使用資源獲取規則階層**

**查詢所有 primitive rules:**
```
請幫我獲取所有的 primitive rules，我想了解目前系統中有哪些基礎規則。
```
*Claude 會使用 `rules://primitive` 資源*

**查詢所有 semantic rules:**
```
請獲取所有的 semantic rules，包括它們的層次結構。
```
*Claude 會使用 `rules://semantic` 資源*

**查詢所有 task rules:**
```
請列出所有的 task rules，我想知道目前有哪些任務級別的實現規則。
```
*Claude 會使用 `rules://task` 資源*

### **方式 2: 使用搜尋工具查找特定規則**

**搜尋特定類型的規則:**
```
請搜尋所有包含 "虛擬環境" 的規則，我想找到相關的最佳實踐。
```
*Claude 會使用 `search_rules` 工具*

**搜尋特定領域的規則:**
```
請搜尋所有與 "MCP" 相關的規則，包括實現和配置相關的。
```

### **方式 3: 使用分析工具了解規則結構**

**分析規則依賴關係:**
```
請分析所有 semantic rules 的依賴關係，我想了解它們是如何組織的。
```
*Claude 會使用 `analyze_rules` 工具*

### **方式 4: 組合查詢**

**完整的規則概覽:**
```
請幫我：
1. 獲取所有 primitive rules 的列表
2. 獲取所有 semantic rules 的列表
3. 獲取所有 task rules 的列表
4. 分析這些規則的整體結構

我想了解整個規則系統的組織架構。
```
