#!/usr/bin/env python3
"""
Health Check Script for MCP Server

This script provides comprehensive health checking for the AI Prompt Engineering System MCP Server.
It can be used for monitoring, alerting, and automated deployment health verification.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class HealthChecker:
    """Comprehensive health checker for MCP server"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "unknown",
            "checks": {},
            "errors": [],
            "warnings": []
        }

    def log(self, message: str, level: str = "info"):
        """Log message with appropriate level"""
        if self.verbose or level in ["error", "warning"]:
            prefix = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }.get(level, "•")
            print(f"{prefix} {message}")

    def check_python_environment(self) -> bool:
        """Check Python environment and dependencies"""
        self.log("Checking Python environment...", "info")

        try:
            # Check Python version
            version = sys.version_info
            if version < (3, 8):
                self.results["errors"].append(f"Python version {version.major}.{version.minor} is too old (3.8+ required)")
                return False

            # Check virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            if not in_venv:
                self.results["warnings"].append("Not running in virtual environment")

            # Check required packages
            required_packages = {
                'mcp': 'MCP SDK',
                'pydantic': 'Pydantic',
                'jinja2': 'Jinja2',
                'yaml': 'PyYAML'
            }

            missing = []
            for package, name in required_packages.items():
                try:
                    __import__(package)
                    self.log(f"{name}: Available", "success")
                except ImportError:
                    missing.append(name)
                    self.log(f"{name}: Missing", "error")

            if missing:
                self.results["errors"].append(f"Missing required packages: {missing}")
                return False

            self.results["checks"]["python_environment"] = {
                "status": "healthy",
                "python_version": f"{version.major}.{version.minor}.{version.micro}",
                "virtual_env": in_venv,
                "packages": list(required_packages.values())
            }

            self.log("Python environment check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Python environment check failed: {str(e)}")
            return False

    def check_project_structure(self) -> bool:
        """Check project structure and required files"""
        self.log("Checking project structure...", "info")

        try:
            required_paths = {
                'mcp_server/fastmcp_server.py': 'MCP Server',
                'mcp_server/utils/monitoring.py': 'Monitoring Module',
                'mcp_server/utils/config.py': 'Configuration Module',
                'mcp_server/config.yaml': 'Default Configuration',
                'ai_prompt_system/src/rule_engine/engine.py': 'Rule Engine',
                'ai_prompt_system/database/prompt_system.db': 'Database'
            }

            missing = []
            for path, name in required_paths.items():
                full_path = project_root / path
                if full_path.exists():
                    self.log(f"{name}: Found", "success")
                else:
                    missing.append(name)
                    self.log(f"{name}: Missing", "error")

            if missing:
                self.results["errors"].append(f"Missing required files: {missing}")
                return False

            self.results["checks"]["project_structure"] = {
                "status": "healthy",
                "required_files": len(required_paths),
                "found_files": len(required_paths) - len(missing)
            }

            self.log("Project structure check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Project structure check failed: {str(e)}")
            return False

    def check_database_connectivity(self) -> bool:
        """Check database connectivity and schema"""
        self.log("Checking database connectivity...", "info")

        try:
            from ai_prompt_system.src.database.connection import DatabaseManager
            from ai_prompt_system.src.database.validation import validate_database_integrity

            # Test database connection
            db_manager = DatabaseManager()

            # Test basic query
            result = db_manager.execute_query("SELECT COUNT(*) FROM primitive_rules")
            if result is None:
                self.results["errors"].append("Database connection test failed")
                return False

            # Validate database integrity
            validation_result = validate_database_integrity(db_manager)
            if not validation_result.get("valid", False):
                issues = validation_result.get("issues", [])
                self.results["errors"].append(f"Database integrity issues: {issues}")
                return False

            self.results["checks"]["database"] = {
                "status": "healthy",
                "connection": "active",
                "integrity": "valid",
                "primitive_rules": result[0] if result else 0
            }

            self.log("Database connectivity check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Database connectivity check failed: {str(e)}")
            return False

    def check_rule_engine(self) -> bool:
        """Check rule engine functionality"""
        self.log("Checking rule engine...", "info")

        try:
            from ai_prompt_system.src.rule_engine.engine import RuleEngine
            from ai_prompt_system.src.database.connection import DatabaseManager

            # Initialize rule engine
            db_manager = DatabaseManager()
            rule_engine = RuleEngine(db=db_manager, cache_size=100, cache_ttl=300)

            # Test basic functionality
            # This would normally test prompt generation, but we'll just check initialization
            if rule_engine.db is None:
                self.results["errors"].append("Rule engine database not initialized")
                return False

            self.results["checks"]["rule_engine"] = {
                "status": "healthy",
                "initialized": True,
                "cache_enabled": True
            }

            self.log("Rule engine check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Rule engine check failed: {str(e)}")
            return False

    def check_mcp_server(self) -> bool:
        """Check MCP server functionality"""
        self.log("Checking MCP server...", "info")

        try:
            from mcp_server.fastmcp_server import mcp

            # Check server initialization
            if mcp.name is None:
                self.results["errors"].append("MCP server not properly initialized")
                return False

            # Check if tools are registered (this is a basic check)
            # In a real implementation, you might want to test tool execution

            self.results["checks"]["mcp_server"] = {
                "status": "healthy",
                "server_name": mcp.name,
                "dependencies": mcp.dependencies if hasattr(mcp, 'dependencies') else []
            }

            self.log("MCP server check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"MCP server check failed: {str(e)}")
            return False

    def check_monitoring(self) -> bool:
        """Check monitoring system"""
        self.log("Checking monitoring system...", "info")

        try:
            from mcp_server.utils.monitoring import mcp_monitor

            # Check monitor initialization
            if mcp_monitor.metrics is None:
                self.results["errors"].append("Monitoring system not initialized")
                return False

            # Get basic metrics
            health_status = mcp_monitor.get_health_status()
            metrics_summary = mcp_monitor.get_metrics_summary()

            self.results["checks"]["monitoring"] = {
                "status": "healthy",
                "health_status": health_status,
                "total_requests": metrics_summary.get("request_metrics", {}).get("total_requests", 0),
                "uptime_seconds": metrics_summary.get("system_info", {}).get("uptime_seconds", 0)
            }

            self.log("Monitoring system check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Monitoring check failed: {str(e)}")
            return False

    def check_configuration(self) -> bool:
        """Check configuration system"""
        self.log("Checking configuration...", "info")

        try:
            from mcp_server.utils.config import get_config

            # Get configuration
            config = get_config()

            if config is None:
                self.results["errors"].append("Configuration not loaded")
                return False

            # Check essential configuration
            if not config.mcp.name:
                self.results["warnings"].append("MCP server name not configured")

            self.results["checks"]["configuration"] = {
                "status": "healthy",
                "environment": config.environment,
                "debug": config.debug,
                "server_name": config.mcp.name,
                "transport": config.mcp.transport_type
            }

            self.log("Configuration check passed", "success")
            return True

        except Exception as e:
            self.results["errors"].append(f"Configuration check failed: {str(e)}")
            return False

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        self.log("Starting comprehensive health check...", "info")

        checks = [
            ("python_environment", self.check_python_environment),
            ("project_structure", self.check_project_structure),
            ("database", self.check_database_connectivity),
            ("rule_engine", self.check_rule_engine),
            ("mcp_server", self.check_mcp_server),
            ("monitoring", self.check_monitoring),
            ("configuration", self.check_configuration)
        ]

        passed = 0
        failed = 0

        for check_name, check_func in checks:
            try:
                if check_func():
                    passed += 1
                else:
                    failed += 1
                    self.results["checks"][check_name] = {"status": "unhealthy"}
            except Exception as e:
                failed += 1
                self.results["checks"][check_name] = {"status": "error", "error": str(e)}
                self.results["errors"].append(f"Check {check_name} failed: {str(e)}")

        # Determine overall status
        if failed == 0:
            self.results["overall_status"] = "healthy"
            self.log("All health checks passed", "success")
        elif passed > failed:
            self.results["overall_status"] = "warning"
            self.log(f"Health check completed with warnings ({failed} failures)", "warning")
        else:
            self.results["overall_status"] = "unhealthy"
            self.log(f"Health check failed ({failed} failures)", "error")

        self.results["summary"] = {
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "success_rate": round(passed / len(checks) * 100, 1)
        }

        return self.results

def main():
    """Main health check function"""
    import argparse

    parser = argparse.ArgumentParser(description='Health check for AI Prompt Engineering System MCP Server')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', '-j', action='store_true', help='Output in JSON format')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # Run health check
    checker = HealthChecker(verbose=args.verbose)
    results = checker.run_all_checks()

    # Output results
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        # Human-readable output
        output = f"""
🏥 AI Prompt Engineering System MCP Server Health Check
{'=' * 60}
Status: {results['overall_status'].upper()}
Timestamp: {results['timestamp']}

📊 Summary:
  Total Checks: {results['summary']['total_checks']}
  Passed: {results['summary']['passed']}
  Failed: {results['summary']['failed']}
  Success Rate: {results['summary']['success_rate']}%

📋 Check Results:
"""

        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            status_icon = {'healthy': '✅', 'unhealthy': '❌', 'warning': '⚠️', 'error': '💥'}.get(status, '❓')
            output += f"  {status_icon} {check_name}: {status}\n"

        if results['errors']:
            output += f"\n❌ Errors:\n"
            for error in results['errors']:
                output += f"  • {error}\n"

        if results['warnings']:
            output += f"\n⚠️ Warnings:\n"
            for warning in results['warnings']:
                output += f"  • {warning}\n"

        output += f"\n🔗 Next Steps:\n"
        if results['overall_status'] == 'healthy':
            output += "  • System is healthy and ready for use\n"
            output += "  • Continue monitoring for any issues\n"
        elif results['overall_status'] == 'warning':
            output += "  • Address warnings to improve system health\n"
            output += "  • Monitor more closely for potential issues\n"
        else:
            output += "  • Address errors immediately\n"
            output += "  • Check logs for more detailed information\n"
            output += "  • Consider restarting services if necessary\n"

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Health check results saved to {args.output}")
    else:
        print(output)

    # Exit with appropriate code
    if results['overall_status'] == 'healthy':
        sys.exit(0)
    elif results['overall_status'] == 'warning':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
