"""
WebSocket Manager Service
Handles WebSocket connections for real-time updates
"""

import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manager for WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to AI Prompt Engineering System",
            "timestamp": self._get_timestamp()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting WebSocket message: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
    
    async def broadcast_rule_update(self, rule_type: str, rule_id: int, action: str, rule_data: Dict[str, Any] = None):
        """Broadcast rule update to all clients"""
        message = {
            "type": "rule_update",
            "rule_type": rule_type,
            "rule_id": rule_id,
            "action": action,  # create, update, delete
            "data": rule_data,
            "timestamp": self._get_timestamp()
        }
        await self.broadcast_message(message)
    
    async def broadcast_mcp_operation(self, operation: str, result: Dict[str, Any]):
        """Broadcast MCP operation result to all clients"""
        message = {
            "type": "mcp_operation",
            "operation": operation,
            "result": result,
            "timestamp": self._get_timestamp()
        }
        await self.broadcast_message(message)
    
    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status update to all clients"""
        message = {
            "type": "system_status",
            "status": status,
            "timestamp": self._get_timestamp()
        }
        await self.broadcast_message(message)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)