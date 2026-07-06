# dashboard_ws.py
# Purpose: WebSocket connection manager for real-time dashboard updates.
# Responsibilities:
#   - Accept, track, and manage active WebSocket connections mapped by user UUIDs
#   - Broadcast JSON-serialized data updates to specific client sockets
# DO NOT: Execute background agent processes or DB queries inside connection manager loops.
# DO NOT: Run authentication validation checks without proper security helpers.

import logging
from fastapi import WebSocket

from app.core.constants import WS_EVENT_DASHBOARD_UPDATE

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections mapped by user IDs."""

    def __init__(self):
        # Maps user_id_str → WebSocket connection
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected: user_id={user_id}")

    def disconnect(self, user_id: str) -> None:
        """Remove a disconnected WebSocket."""
        self.active_connections.pop(user_id, None)
        logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def send_dashboard_update(self, user_id: str, data: dict) -> None:
        """Send a dashboard update payload to a specific user."""
        websocket = self.active_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json({
                    "event": WS_EVENT_DASHBOARD_UPDATE,
                    "data": data,
                })
                logger.debug(f"Successfully broadcasted update to user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to send WebSocket data to user {user_id}: {e}")
                self.disconnect(user_id)


# ─── Connection Manager Singleton ─────────────────────────────────────────────
connection_manager = ConnectionManager()
