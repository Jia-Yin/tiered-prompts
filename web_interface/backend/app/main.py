#!/usr/bin/env python3
"""
AI Prompt Engineering System - Web Interface Backend
FastAPI server that bridges web interface with MCP server
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.api.routes import router
from app.services.mcp_client import MCPClientService
from app.services.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Prompt Engineering Web Interface...")
    
    # Initialize services
    app.state.mcp_client = MCPClientService()
    app.state.websocket_manager = WebSocketManager()
    
    try:
        # Connect to MCP server
        await app.state.mcp_client.connect()
        logger.info("Connected to MCP server")
    except Exception as e:
        logger.warning(f"Could not connect to MCP server: {e}")
        logger.warning("Running in standalone mode")
    
    yield
    
    # Cleanup
    try:
        await app.state.mcp_client.disconnect()
        logger.info("Disconnected from MCP server")
    except Exception as e:
        logger.error(f"Error disconnecting from MCP server: {e}")
    
    logger.info("Web interface shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI Prompt Engineering System - Web Interface",
    description="Web interface for managing hierarchical rules and MCP operations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time updates"""
    await app.state.websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # Echo message back (for testing)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        app.state.websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mcp_status = "connected" if app.state.mcp_client.is_connected() else "disconnected"
    return {
        "status": "healthy",
        "mcp_server": mcp_status,
        "active_websockets": len(app.state.websocket_manager.active_connections)
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Prompt Engineering System - Web Interface API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )