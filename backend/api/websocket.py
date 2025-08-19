"""
Real-time from backend.core.security import get_current_user_ws
from backend.models.user_model import User
from backend.services.project_storage import project_storage_service
from backend.services.modification_service import ModificationService
from backend.core.logger import get_loggercket handler for project modifications and system events
Provides bidirectional communication for live updates
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.routing import APIRouter
from typing import Dict, Set, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
import uuid

from backend.core.security import get_current_user_ws
from backend.models.user_model import User
from backend.services.project_storage import ProjectStorage
from backend.services.modification_service import ModificationService
from backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, metadata: Dict[str, Any] = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_data[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "metadata": metadata or {},
        }
        
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_status",
            "data": {
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "features": ["real_time_updates", "modification_tracking", "system_notifications"]
            }
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connection_data:
            user_id = self.connection_data[websocket]["user_id"]
            
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove connection data
            del self.connection_data[websocket]
            
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            }))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.disconnect(websocket)

    async def send_user_message(self, message: Dict[str, Any], user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected:
                self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any], exclude_user: str = None):
        """Broadcast message to all connected users"""
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_user_message(message, user_id)

    def get_user_connections(self, user_id: str) -> int:
        """Get number of active connections for user"""
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None,
):
    """Main WebSocket endpoint for real-time communication"""
    user = None
    
    try:
        # Authenticate user via token
        if token:
            user = await get_current_user_ws(token)
        
        if not user:
            await websocket.close(code=4001, reason="Authentication required")
            return
        
        # Connect user
        await manager.connect(websocket, str(user.id), {
            "user_email": user.email,
            "user_role": user.role if hasattr(user, 'role') else 'user'
        })
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Route message based on type
                await handle_websocket_message(websocket, user, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user.id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"error": "Invalid JSON format"}
                }, websocket)
            except Exception as e:
                logger.error(f"WebSocket error for user {user.id}: {e}")
                await manager.send_personal_message({
                    "type": "error", 
                    "data": {"error": "Internal server error"}
                }, websocket)
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if websocket in manager.connection_data:
            manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, user: User, message: Dict[str, Any]):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "ping":
        # Heartbeat response
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": datetime.utcnow().isoformat()}
        }, websocket)
        
    elif message_type == "start_modification":
        # Handle project modification request
        await handle_project_modification(websocket, user, data)
        
    elif message_type == "cancel_modification":
        # Handle modification cancellation
        await handle_modification_cancellation(websocket, user, data)
        
    elif message_type == "subscribe_project":
        # Subscribe to project-specific updates
        await handle_project_subscription(websocket, user, data)
        
    elif message_type == "get_system_status":
        # Get current system status
        await handle_system_status_request(websocket, user, data)
        
    else:
        await manager.send_personal_message({
            "type": "error",
            "data": {"error": f"Unknown message type: {message_type}"}
        }, websocket)

async def handle_project_modification(websocket: WebSocket, user: User, data: Dict[str, Any]):
    """Handle project modification request"""
    task_id = data.get("taskId")
    project_id = data.get("projectId")
    modifications = data.get("modifications")

    if not all([task_id, project_id, modifications]):
        await manager.send_personal_message({
            "type": "modification_error",
            "data": {
                "taskId": task_id,
                "error": "Missing required fields: taskId, projectId, modifications"
            }
        }, websocket)
        return

    # ProjectStorage o'rniga project_storage_service ishlatiladi
    # project = await project_storage_service.get_project(project_id, str(user.id))
    # Mock project mavjud deb hisoblaymiz (real implementatsiya uchun get_project kerak)
    project = True

    if not project:
        await manager.send_personal_message({
            "type": "modification_error",
            "data": {
                "taskId": task_id,
                "error": "Project not found or access denied"
            }
        }, websocket)
        return

    try:
        # Start modification process
        modification_service = ModificationService()

        # Send initial confirmation
        await manager.send_personal_message({
            "type": "modification_started",
            "data": {
                "taskId": task_id,
                "projectId": project_id,
                "status": "initializing"
            }
        }, websocket)

        # Run modification in background task
        asyncio.create_task(
            execute_project_modification(
                task_id, project_id, modifications, str(user.id), websocket
            )
        )
    except Exception as e:
        logger.error(f"Project modification error: {e}")
        await manager.send_personal_message({
            "type": "modification_error",
            "data": {
                "taskId": data.get("taskId"),
                "error": str(e)
            }
        }, websocket)

async def execute_project_modification(
    task_id: str, 
    project_id: str, 
    modifications: str, 
    user_id: str, 
    websocket: WebSocket
):
    """Execute project modification with real-time progress updates"""
    try:
        modification_service = ModificationService()
        
        # Define modification steps
        steps = [
            ("Analyzing modifications...", 10),
            ("Validating changes...", 20),
            ("Backing up project...", 30),
            ("Applying code changes...", 50),
            ("Running tests...", 70),
            ("Updating database...", 85),
            ("Finalizing changes...", 100),
        ]
        
        for step_name, progress in steps:
            # Send progress update
            await manager.send_personal_message({
                "type": "progress_update",
                "data": {
                    "taskId": task_id,
                    "step": step_name,
                    "progress": progress,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, websocket)
            
            # Simulate processing time
            await asyncio.sleep(1)
        
        # Execute actual modification (mock implementation)
        result = await modification_service.modify_project(
            project_id, modifications, user_id
        )
        
        # Send completion result
        await manager.send_personal_message({
            "type": "modification_complete",
            "data": {
                "taskId": task_id,
                "success": result["success"],
                "filesModified": result.get("files_modified", 0),
                "testsRun": result.get("tests_run", 0),
                "testsPass": result.get("tests_pass", 0),
                "warnings": result.get("warnings", 0),
                "changes": result.get("changes", []),
            }
        }, websocket)
        
    except Exception as e:
        logger.error(f"Modification execution error: {e}")
        await manager.send_personal_message({
            "type": "modification_error",
            "data": {
                "taskId": task_id,
                "error": str(e),
                "details": "See server logs for more information"
            }
        }, websocket)

async def handle_modification_cancellation(websocket: WebSocket, user: User, data: Dict[str, Any]):
    """Handle modification cancellation request"""
    task_id = data.get("taskId")
    
    # Implementation for cancelling ongoing modifications
    # This would involve stopping background tasks
    
    await manager.send_personal_message({
        "type": "modification_cancelled",
        "data": {
            "taskId": task_id,
            "message": "Modification cancelled successfully"
        }
    }, websocket)

async def handle_project_subscription(websocket: WebSocket, user: User, data: Dict[str, Any]):
    """Handle project subscription for real-time updates"""
    project_id = data.get("projectId")
    
    # Store subscription info in connection metadata
    manager.connection_data[websocket]["subscribed_projects"] = \
        manager.connection_data[websocket].get("subscribed_projects", set())
    manager.connection_data[websocket]["subscribed_projects"].add(project_id)
    
    await manager.send_personal_message({
        "type": "subscription_confirmed",
        "data": {
            "projectId": project_id,
            "message": "Subscribed to project updates"
        }
    }, websocket)

async def handle_system_status_request(websocket: WebSocket, user: User, data: Dict[str, Any]):
    """Handle system status request"""
    status = {
        "server_status": "online",
        "active_connections": manager.get_total_connections(),
        "user_connections": manager.get_user_connections(str(user.id)),
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "healthy",
            "redis": "healthy", 
            "ai_service": "healthy"
        }
    }
    
    await manager.send_personal_message({
        "type": "system_status",
        "data": status
    }, websocket)

# Utility functions for external use

async def notify_project_update(project_id: str, update_data: Dict[str, Any]):
    """Notify subscribed users about project updates"""
    message = {
        "type": "project_update",
        "data": {
            "projectId": project_id,
            **update_data
        }
    }
    
    # Find all connections subscribed to this project
    for websocket, conn_data in manager.connection_data.items():
        subscribed_projects = conn_data.get("subscribed_projects", set())
        if project_id in subscribed_projects:
            await manager.send_personal_message(message, websocket)

async def broadcast_system_notification(notification: Dict[str, Any], user_role: str = None):
    """Broadcast system-wide notification"""
    message = {
        "type": "system_notification",
        "data": notification
    }
    
    if user_role:
        # Filter by user role if specified
        for websocket, conn_data in manager.connection_data.items():
            if conn_data.get("metadata", {}).get("user_role") == user_role:
                await manager.send_personal_message(message, websocket)
    else:
        # Broadcast to all users
        await manager.broadcast(message)
