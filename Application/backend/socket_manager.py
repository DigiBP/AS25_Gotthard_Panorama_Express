from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections for broadcasting messages."""

    def __init__(self):
        """Initialize the connection manager with an empty list of active connections."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept a WebSocket connection and add it to the active connections list.

        Args:
            websocket: The WebSocket connection to accept and store.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from the active connections list.

        Args:
            websocket: The WebSocket connection to remove.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        """
        Send a message to all active WebSocket connections.

        If sending to a connection fails, the connection is disconnected.

        Args:
            message: The message string to broadcast to all connections.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                # If sending fails, mark connection for disconnection
                disconnected.append(connection)
                print(f"Error sending message to connection: {e}")

        # Disconnect failed connections
        for connection in disconnected:
            self.disconnect(connection)


# Global instance for use in FastAPI endpoints
manager = ConnectionManager()