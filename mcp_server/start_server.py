#!/usr/bin/env python3
"""
Startup script for MCP Server with HTTP wrapper

This script starts the MCP server with HTTP endpoints
for the web interface to consume.
"""

import asyncio
import logging
import signal
import sys
import os
from contextlib import asynccontextmanager

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan_manager():
    """Manage the lifecycle of the MCP server"""
    logger.info("🚀 Starting AI Prompt Engineering System MCP Server...")
    
    try:
        # Import and start HTTP wrapper
        from http_wrapper import main as start_http_wrapper
        
        # Start the HTTP wrapper in a separate task
        http_task = asyncio.create_task(
            asyncio.to_thread(start_http_wrapper)
        )
        
        logger.info("✅ MCP Server with HTTP wrapper started successfully")
        logger.info("📡 HTTP endpoints available at http://localhost:8001")
        logger.info("🔗 Web interface can now connect to real data")
        
        yield http_task
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP server: {e}")
        raise
    finally:
        logger.info("🛑 Shutting down MCP server...")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

async def main():
    """Main function to run the MCP server"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        async with lifespan_manager() as http_task:
            # Keep the server running
            await http_task
            
    except KeyboardInterrupt:
        logger.info("👋 MCP server stopped by user")
    except Exception as e:
        logger.error(f"💥 MCP server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Change to the ai_prompt_system directory for proper database access
    ai_prompt_dir = os.path.join(os.path.dirname(script_dir), 'ai_prompt_system')
    if os.path.exists(ai_prompt_dir):
        os.chdir(ai_prompt_dir)
        logger.info(f"📁 Changed working directory to: {ai_prompt_dir}")
    
    # Run the server
    exit_code = asyncio.run(main())
    sys.exit(exit_code)