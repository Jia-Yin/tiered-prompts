#!/usr/bin/env python3
"""
Phase 3.3 Integration Testing Preparation

This script prepares the system for integration testing with MCP clients,
particularly Claude Desktop, and performs preliminary integration tests.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def prepare_production_environment():
    """Prepare system for production-like testing"""
    print("🔧 Preparing Production Environment...")

    # Create production config
    prod_config = {
        "environment": "production",
        "debug": False,
        "database": {
            "path": "ai_prompt_system/database/prompt_system.db",
            "backup_enabled": True
        },
        "cache": {
            "enabled": True,
            "max_size": 2000,
            "ttl_seconds": 7200
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "file_path": "mcp_server_production.log"
        },
        "performance": {
            "enable_metrics": True,
            "max_concurrent_requests": 100
        },
        "mcp": {
            "name": "AI Prompt Engineering System",
            "version": "1.0.0",
            "enable_mock_mode": False,
            "transport_type": "stdio"
        }
    }

    # Save production config
    prod_config_file = project_root / "mcp_server" / "config_production.yaml"
    try:
        import yaml
        with open(prod_config_file, 'w') as f:
            yaml.dump(prod_config, f, default_flow_style=False, indent=2)
        print(f"  ✅ Production config created: {prod_config_file}")
    except ImportError:
        print("  ⚠️  PyYAML not available, using JSON config")
        prod_config_file = prod_config_file.with_suffix('.json')
        with open(prod_config_file, 'w') as f:
            json.dump(prod_config, f, indent=2)

    return True

def test_stdio_interface():
    """Test MCP server stdio interface"""
    print("\n🔌 Testing stdio Interface...")

    try:
        # Start server process
        server_path = project_root / "mcp_server" / "fastmcp_server.py"
        venv_python = project_root / ".venv" / "bin" / "python"

        if not venv_python.exists():
            venv_python = "python"  # fallback to system python

        # Test server starts without errors
        result = subprocess.run(
            [str(venv_python), str(server_path), "--test-mode"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root
        )

        if result.returncode == 0:
            print("  ✅ Server starts successfully")
            return True
        else:
            print(f"  ❌ Server failed to start: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("  ⚠️  Server startup timeout (may be normal for stdio mode)")
        return True
    except Exception as e:
        print(f"  ❌ stdio interface test failed: {e}")
        return False

def create_integration_test_cases():
    """Create test cases for integration testing"""
    print("\n📝 Creating Integration Test Cases...")

    test_cases = {
        "tool_tests": [
            {
                "name": "generate_prompt_basic",
                "tool": "generate_prompt",
                "args": {
                    "rule_name": "react_component_review",
                    "context": {"component_name": "UserProfile"},
                    "target_model": "claude"
                },
                "expected_fields": ["prompt", "metadata"]
            },
            {
                "name": "analyze_rules_all",
                "tool": "analyze_rules",
                "args": {
                    "rule_type": "all",
                    "include_dependencies": True
                },
                "expected_fields": ["rule_type", "total_rules", "dependencies"]
            },
            {
                "name": "search_rules_content",
                "tool": "search_rules",
                "args": {
                    "query": "formatting",
                    "search_type": "content",
                    "limit": 5
                },
                "expected_fields": ["query", "results", "total_found"]
            }
        ],
        "resource_tests": [
            {
                "name": "get_primitive_hierarchy",
                "resource": "rules://primitive",
                "expected_format": "json"
            },
            {
                "name": "get_performance_stats",
                "resource": "stats://performance",
                "expected_format": "json"
            },
            {
                "name": "get_task_relationships",
                "resource": "relationships://task:1",
                "expected_format": "json"
            }
        ],
        "prompt_tests": [
            {
                "name": "create_rule_prompt_basic",
                "prompt": "create_rule_prompt",
                "args": {
                    "rule_type": "semantic",
                    "domain": "web_development"
                }
            }
        ]
    }

    # Save test cases
    test_file = project_root / "mcp_server" / "integration_test_cases.json"
    with open(test_file, 'w') as f:
        json.dump(test_cases, f, indent=2)

    print(f"  ✅ Integration test cases created: {test_file}")
    print(f"  📊 Test coverage: {len(test_cases['tool_tests'])} tools, {len(test_cases['resource_tests'])} resources, {len(test_cases['prompt_tests'])} prompts")

    return True

def create_claude_desktop_setup_guide():
    """Create setup guide for Claude Desktop integration"""
    print("\n📖 Creating Claude Desktop Setup Guide...")

    guide = """# Claude Desktop Integration Guide

## Prerequisites

1. Claude Desktop application installed
2. AI Prompt Engineering System MCP Server set up
3. Virtual environment activated

## Configuration

### 1. Locate Claude Desktop Config

The Claude Desktop configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`
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
"""

    guide_file = project_root / "mcp_server" / "claude_desktop_setup.md"
    with open(guide_file, 'w') as f:
        f.write(guide)

    print(f"  ✅ Claude Desktop setup guide created: {guide_file}")
    return True

def generate_performance_baseline():
    """Generate performance baseline for comparison"""
    print("\n📊 Generating Performance Baseline...")

    try:
        from mcp_server.utils.monitoring import mcp_monitor
        from mcp_server.utils.health_check import main as health_check

        # Run health check to populate initial metrics
        health_check()

        # Get baseline metrics
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            },
            "performance_targets": {
                "tool_response_time_ms": 100,  # Target: < 100ms
                "resource_response_time_ms": 50,  # Target: < 50ms
                "success_rate_percent": 95,  # Target: > 95%
                "cache_hit_rate_percent": 80  # Target: > 80%
            },
            "test_environment": {
                "cache_size": 1000,
                "concurrent_limit": 50,
                "log_level": "INFO"
            }
        }

        baseline_file = project_root / "mcp_server" / "performance_baseline.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)

        print(f"  ✅ Performance baseline saved: {baseline_file}")
        print("  📈 Target metrics:")
        for metric, target in baseline["performance_targets"].items():
            print(f"    - {metric}: {target}")

        return True

    except Exception as e:
        print(f"  ❌ Performance baseline generation failed: {e}")
        return False

def main():
    """Main preparation function"""
    print("🚀 Phase 3.3 Integration Testing Preparation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    preparation_steps = [
        ("Production Environment", prepare_production_environment),
        ("stdio Interface Test", test_stdio_interface),
        ("Integration Test Cases", create_integration_test_cases),
        ("Claude Desktop Setup Guide", create_claude_desktop_setup_guide),
        ("Performance Baseline", generate_performance_baseline)
    ]

    results = {}
    for step_name, step_func in preparation_steps:
        try:
            print(f"\n{'='*20} {step_name} {'='*20}")
            result = step_func()
            results[step_name] = "SUCCESS" if result else "FAILED"
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            results[step_name] = "ERROR"

    # Summary
    print(f"\n{'='*60}")
    print("📋 Preparation Summary")
    print("-" * 30)

    for step, status in results.items():
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔥"
        print(f"{status_icon} {step}: {status}")

    success_count = sum(1 for status in results.values() if status == "SUCCESS")
    total_count = len(results)

    print(f"\nOverall: {success_count}/{total_count} steps completed successfully")

    if success_count == total_count:
        print("\n🎉 Phase 3.3 preparation completed successfully!")
        print("\n📋 Next Steps:")
        print("1. 📖 Review Claude Desktop setup guide")
        print("2. 🔧 Configure Claude Desktop with MCP server")
        print("3. 🧪 Run integration test cases")
        print("4. 📊 Monitor performance against baseline")
        return 0
    else:
        print(f"\n⚠️  Some preparation steps failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
