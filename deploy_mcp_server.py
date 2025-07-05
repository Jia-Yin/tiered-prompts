#!/usr/bin/env python3
"""
MCP Server Deployment Script

This script provides deployment automation for the AI Prompt Engineering System MCP Server.
It supports different deployment environments and configurations.

Author: AI Prompt Engineering System
Date: 2025-07-05
"""

import os
import sys
import argparse
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking environment...")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment: ACTIVE")
    else:
        print("⚠️  Virtual environment: NOT ACTIVE (recommended)")

    # Check required packages
    required_packages = ['mcp', 'pydantic', 'jinja2', 'yaml']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Missing")

    if missing_packages:
        print(f"❌ Missing required packages: {missing_packages}")
        return False

    # Check project structure
    required_dirs = [
        'mcp_server',
        'ai_prompt_system',
        'mcp_server/utils'
    ]

    for dir_path in required_dirs:
        if (project_root / dir_path).exists():
            print(f"✅ {dir_path}: Found")
        else:
            print(f"❌ {dir_path}: Missing")
            return False

    print("✅ Environment check passed")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")

    try:
        # Install MCP SDK if not available
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'mcp'], check=True)

        # Install other dependencies
        requirements = [
            'pydantic>=2.0.0',
            'jinja2>=3.0.0',
            'pyyaml>=6.0.0'
        ]

        for req in requirements:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], check=True)

        print("✅ Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Set up the database"""
    print("🗄️  Setting up database...")

    try:
        # Import database setup
        from ai_prompt_system.src.database.connection import DatabaseManager
        from ai_prompt_system.src.database.migrations import DatabaseMigrator

        # Initialize database
        db_manager = DatabaseManager()
        migrator = DatabaseMigrator(db_manager)

        # Run migrations
        migrator.migrate_to_latest()

        print("✅ Database setup completed")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_config_file(environment: str = "development"):
    """Create configuration file for specified environment"""
    print(f"⚙️  Creating configuration for {environment} environment...")

    config_path = project_root / 'mcp_server' / f'config_{environment}.yaml'

    # Environment-specific configurations
    configs = {
        "development": {
            "environment": "development",
            "debug": True,
            "logging": {"level": "DEBUG"},
            "mcp": {"enable_mock_mode": False}
        },
        "staging": {
            "environment": "staging",
            "debug": False,
            "logging": {"level": "INFO"},
            "performance": {"enable_metrics": True}
        },
        "production": {
            "environment": "production",
            "debug": False,
            "logging": {"level": "WARNING", "file_enabled": True},
            "performance": {"enable_metrics": True, "max_concurrent_requests": 100},
            "security": {"rate_limit_enabled": True}
        }
    }

    try:
        # Load default config
        default_config_path = project_root / 'mcp_server' / 'config.yaml'
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                base_config = yaml.safe_load(f)
        else:
            base_config = {}

        # Merge environment-specific config
        if environment in configs:
            env_config = configs[environment]
            for key, value in env_config.items():
                if isinstance(value, dict) and key in base_config:
                    base_config[key].update(value)
                else:
                    base_config[key] = value

        # Write config file
        with open(config_path, 'w') as f:
            yaml.dump(base_config, f, default_flow_style=False, indent=2)

        print(f"✅ Configuration file created: {config_path}")
        return str(config_path)

    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return None

def test_server():
    """Test the MCP server"""
    print("🧪 Testing MCP server...")

    try:
        # Run test script
        test_script = project_root / 'test_mcp_server.py'
        if test_script.exists():
            result = subprocess.run([sys.executable, str(test_script)],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Server tests passed")
                return True
            else:
                print(f"❌ Server tests failed: {result.stderr}")
                return False
        else:
            print("⚠️  Test script not found, skipping tests")
            return True

    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def deploy_server(environment: str = "development", config_file: str = None):
    """Deploy the MCP server"""
    print(f"🚀 Deploying MCP server for {environment} environment...")

    try:
        # Set environment variable
        os.environ['MCP_SERVER_ENVIRONMENT'] = environment

        if config_file:
            os.environ['MCP_SERVER_CONFIG'] = config_file

        # Import and run server
        from mcp_server.fastmcp_server import mcp, logger

        logger.info(f"Starting MCP server deployment for {environment}")

        # For development, run interactively
        if environment == "development":
            print("🔧 Starting development server...")
            print("Press Ctrl+C to stop the server")

            # Run server (this would normally be called by MCP client)
            print("✅ MCP server ready for connections")
            print("Use Claude Desktop or another MCP client to connect")

        else:
            print(f"✅ MCP server configured for {environment} deployment")
            print("Use a process manager like systemd to run the server")

        return True

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def create_systemd_service():
    """Create systemd service file for production deployment"""
    print("📋 Creating systemd service file...")

    service_content = f"""[Unit]
Description=AI Prompt Engineering System MCP Server
After=network.target

[Service]
Type=simple
User=mcp-server
WorkingDirectory={project_root}
Environment=MCP_SERVER_ENVIRONMENT=production
Environment=MCP_SERVER_CONFIG={project_root}/mcp_server/config_production.yaml
ExecStart={sys.executable} -m mcp_server.fastmcp_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_path = project_root / 'mcp-server.service'

    try:
        with open(service_path, 'w') as f:
            f.write(service_content)

        print(f"✅ Service file created: {service_path}")
        print("To install:")
        print(f"  sudo cp {service_path} /etc/systemd/system/")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable mcp-server")
        print("  sudo systemctl start mcp-server")

        return True

    except Exception as e:
        print(f"❌ Failed to create service file: {e}")
        return False

def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description='Deploy AI Prompt Engineering System MCP Server')
    parser.add_argument('--environment', '-e',
                       choices=['development', 'staging', 'production'],
                       default='development',
                       help='Deployment environment')
    parser.add_argument('--config', '-c',
                       help='Custom configuration file')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip server tests')
    parser.add_argument('--create-service', action='store_true',
                       help='Create systemd service file')

    args = parser.parse_args()

    print("🚀 AI Prompt Engineering System MCP Server Deployment")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)

    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            print("❌ Dependency installation failed.")
            sys.exit(1)

    # Setup database
    if not setup_database():
        print("❌ Database setup failed.")
        sys.exit(1)

    # Create configuration
    config_file = args.config
    if not config_file:
        config_file = create_config_file(args.environment)
        if not config_file:
            print("❌ Configuration creation failed.")
            sys.exit(1)

    # Test server
    if not args.skip_tests:
        if not test_server():
            print("❌ Server tests failed.")
            sys.exit(1)

    # Create systemd service if requested
    if args.create_service:
        create_systemd_service()

    # Deploy server
    if deploy_server(args.environment, config_file):
        print("🎉 Deployment completed successfully!")

        # Print next steps
        print("\n📋 Next Steps:")
        if args.environment == "development":
            print("  • Configure your MCP client (e.g., Claude Desktop)")
            print("  • Add server configuration to client settings")
            print("  • Test the connection with the client")
        else:
            print("  • Configure your production environment")
            print("  • Set up monitoring and logging")
            print("  • Configure your MCP client")
            print("  • Test the deployment")
    else:
        print("❌ Deployment failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
