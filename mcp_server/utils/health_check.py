#!/usr/bin/env python3
"""
Health Check Script for MCP Server

This script performs comprehensive health checks on the MCP server
and its dependencies to ensure everything is working correctly.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import sys
import os
import json
from pathlib import Path
import sqlite3
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_python_environment():
    """Check Python environment and basic requirements"""
    print("🔍 Checking Python Environment...")

    checks = {
        "Python version": sys.version,
        "Python executable": sys.executable,
        "Virtual environment": "ACTIVE" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "NOT ACTIVE"
    }

    for name, value in checks.items():
        print(f"  ✅ {name}: {value}")

    # Check required packages
    required_packages = ['mcp', 'pydantic', 'jinja2']
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: Available")
        except ImportError:
            print(f"  ❌ {package}: Missing")
            return False

    return True

def check_rule_engine():
    """Check rule engine components"""
    print("\n🔍 Checking Rule Engine Components...")

    try:
        from ai_prompt_system.src.rule_engine.engine import RuleEngine
        from ai_prompt_system.src.rule_engine.resolver import RuleResolver
        from ai_prompt_system.src.rule_engine.validation import ValidationEngine
        from ai_prompt_system.src.rule_engine.cache import CacheManager
        from ai_prompt_system.src.database.connection import DatabaseManager
        print("  ✅ All rule engine components imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Rule engine import failed: {e}")
        return False

def check_database():
    """Check database connectivity and structure"""
    print("\n🔍 Checking Database...")

    try:
        # Check database file exists
        db_path = project_root / "ai_prompt_system" / "database" / "prompt_system.db"
        if not db_path.exists():
            print(f"  ❌ Database file not found: {db_path}")
            return False

        print(f"  ✅ Database file exists: {db_path}")

        # Check database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['primitive_rules', 'semantic_rules', 'task_rules',
                          'semantic_primitive_relations', 'task_semantic_relations']

        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ Table {table}: {count} records")
            else:
                print(f"  ❌ Table {table}: Missing")
                conn.close()
                return False

        conn.close()
        return True

    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False

def check_mcp_server():
    """Check MCP server components"""
    print("\n🔍 Checking MCP Server...")

    try:
        # Test basic import
        from mcp_server.fastmcp_server import mcp
        print("  ✅ FastMCP server imported successfully")
        print(f"  ✅ Server name: {mcp.name}")
        print(f"  ✅ Server dependencies: {mcp.dependencies}")

        # Test utility imports
        try:
            from mcp_server.utils.monitoring import mcp_monitor
            from mcp_server.utils.config import get_config
            print("  ✅ Monitoring and config utilities available")
        except ImportError:
            print("  ⚠️  Monitoring/config utilities not available (running in basic mode)")

        return True

    except Exception as e:
        print(f"  ❌ MCP server check failed: {e}")
        return False

def check_configuration():
    """Check configuration files and settings"""
    print("\n🔍 Checking Configuration...")

    try:
        config_file = project_root / "mcp_server" / "config.yaml"
        if config_file.exists():
            print(f"  ✅ Configuration file exists: {config_file}")

            # Try to load config
            from mcp_server.utils.config import get_config
            config = get_config()
            print(f"  ✅ Environment: {config.environment}")
            print(f"  ✅ Debug mode: {config.debug}")
            print(f"  ✅ Cache enabled: {config.cache.enabled}")
            print(f"  ✅ Logging level: {config.logging.level}")
        else:
            print(f"  ⚠️  Configuration file not found, using defaults")

        return True

    except Exception as e:
        print(f"  ❌ Configuration check failed: {e}")
        return False

def check_monitoring():
    """Check monitoring and metrics collection"""
    print("\n🔍 Checking Monitoring System...")

    try:
        from mcp_server.utils.monitoring import mcp_monitor

        # Test basic monitoring functionality
        start_time = time.time()
        mcp_monitor.log_request("test", "health_check", {"test": True})
        response_time = time.time() - start_time
        mcp_monitor.log_response("test", "health_check", True, response_time)
        mcp_monitor.record_operation("test", "health_check", response_time, True)

        # Get metrics summary
        metrics = mcp_monitor.get_metrics_summary()
        print(f"  ✅ Monitoring active, total requests: {metrics['request_metrics']['total_requests']}")

        # Get health status
        health = mcp_monitor.get_health_status()
        print(f"  ✅ System health status: {health['status']}")

        return True

    except Exception as e:
        print(f"  ❌ Monitoring check failed: {e}")
        return False

def check_tools_and_resources():
    """Check MCP tools and resources"""
    print("\n🔍 Checking MCP Tools and Resources...")

    try:
        from mcp_server.fastmcp_server import (
            generate_prompt, analyze_rules, validate_rules,
            search_rules, optimize_rules,
            get_rule_hierarchy, get_performance_stats, get_rule_relationships
        )

        print("  ✅ All MCP tools imported successfully")
        print("  ✅ All MCP resources imported successfully")

        # Test basic tool functionality (mock mode)
        try:
            result = generate_prompt("test_rule", {"test": "context"}, "claude")
            print("  ✅ generate_prompt tool works")
        except Exception as e:
            print(f"  ⚠️  generate_prompt tool error: {e}")

        return True

    except Exception as e:
        print(f"  ❌ Tools and resources check failed: {e}")
        return False

def generate_health_report():
    """Generate comprehensive health report"""
    print("\n📊 Generating Health Report...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_status": "healthy"
    }

    checks = [
        ("python_environment", check_python_environment),
        ("rule_engine", check_rule_engine),
        ("database", check_database),
        ("mcp_server", check_mcp_server),
        ("configuration", check_configuration),
        ("monitoring", check_monitoring),
        ("tools_and_resources", check_tools_and_resources)
    ]

    for check_name, check_func in checks:
        try:
            result = check_func()
            report["checks"][check_name] = {
                "status": "pass" if result else "fail",
                "timestamp": datetime.now().isoformat()
            }
            if not result:
                report["overall_status"] = "degraded"
        except Exception as e:
            report["checks"][check_name] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            report["overall_status"] = "critical"

    return report

def main():
    """Main health check function"""
    print("🏥 AI Prompt Engineering System - Health Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Project root: {project_root}")

    # Generate comprehensive health report
    report = generate_health_report()

    # Print summary
    print("\n📋 Health Check Summary")
    print("-" * 30)

    total_checks = len(report["checks"])
    passed_checks = sum(1 for check in report["checks"].values() if check["status"] == "pass")
    failed_checks = sum(1 for check in report["checks"].values() if check["status"] == "fail")
    error_checks = sum(1 for check in report["checks"].values() if check["status"] == "error")

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks} ✅")
    print(f"Failed: {failed_checks} ❌")
    print(f"Errors: {error_checks} 🔥")
    print(f"Overall status: {report['overall_status']} {'✅' if report['overall_status'] == 'healthy' else '⚠️' if report['overall_status'] == 'degraded' else '❌'}")

    # Save detailed report
    report_file = project_root / "mcp_server" / "health_report.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")

    # Return appropriate exit code
    if report["overall_status"] == "healthy":
        print("\n🎉 All systems operational!")
        return 0
    elif report["overall_status"] == "degraded":
        print("\n⚠️  Some issues detected, but system is functional")
        return 1
    else:
        print("\n❌ Critical issues detected!")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
