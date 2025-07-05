# Claude Desktop Integration Guide

## Prerequisites

1. Claude Desktop application installed
2. AI Prompt Engineering System MCP Server set up
3. Virtual environment activated

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
      "command": "python",
      "args": [
        "/home/jyw/Program/tiered-prompts/mcp_server/fastmcp_server.py"
      ],
      "env": {
        "MCP_SERVER_ENVIRONMENT": "production",
        "MCP_SERVER_LOG_LEVEL": "INFO",
        "MCP_SERVER_CACHE_SIZE": "1000"
      }
    }
  }
}
```

**Important**: Update the path in `args` to match your installation directory.

### 3. Test the Integration

1. Restart Claude Desktop
2. Look for the MCP server in the available tools
3. Try using the prompt generation tool:
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
- **rules://primitive**: Get primitive rule hierarchy
- **rules://semantic**: Get semantic rule hierarchy  
- **rules://task**: Get task rule hierarchy
- **stats://performance**: Get system performance statistics
- **relationships://{rule_id}**: Get relationships for specific rule

### Prompts
- **create_rule_prompt**: Assistance for creating new rules
- **debug_rule_prompt**: Help with debugging rule issues

## Troubleshooting

### Server Not Starting
1. Check that Python virtual environment is properly set up
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Test server manually: `python mcp_server/fastmcp_server.py`

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

### 1. Code Review Prompt Generation
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

### 2. Rule Analysis
```
Tool: analyze_rules  
Args: {
  "rule_type": "semantic",
  "include_dependencies": true
}
```

### 3. Rule Search
```
Tool: search_rules
Args: {
  "query": "code quality",
  "search_type": "content",
  "limit": 10
}
```

For more information, see the project documentation and health check reports.
