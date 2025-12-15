from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from Application.backend.socket_manager import manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class WorkflowMessage(BaseModel):
    """Represents a workflow event message to be broadcast to clients."""

    event_type: str
    message: str
    cart_id: int | None = None


@router.post("/workflow-event")
async def workflow_event(data: WorkflowMessage):
    """
    Broadcast a workflow event to all connected WebSocket clients.

    Args:
        data: WorkflowMessage containing event_type, message, and cart_id.

    Returns:
        dict with status confirmation.
    """
    await manager.broadcast(data.model_dump_json())
    return {"status": "Event broadcasted"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to connect and receive real-time notifications.

    Keeps the connection open and handles disconnects gracefully.

    Args:
        websocket: The WebSocket connection object.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open by receiving data
            # (even though we don't process client messages, this keeps the connection alive)
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Handle client disconnect by removing from active connections
        manager.disconnect(websocket)