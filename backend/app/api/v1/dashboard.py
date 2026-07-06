# dashboard.py
# Purpose: Dashboard analytics API endpoint router.
# Responsibilities:
#   - Route REST fetch requests for dashboard statistics
#   - Expose WebSocket handshake endpoint, parsing query authorization tokens
# DO NOT: Run database transaction logic directly inside controllers.
# DO NOT: Catch raw connection disconnect exceptions silently.

import logging
import uuid
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user_id
from app.core.security import decode_access_token
from app.websockets.dashboard_ws import connection_manager
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard")


@router.get("")
async def get_dashboard(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Fetch aggregated static analytics metrics for the dashboard."""
    logger.info(f"REST request: Dashboard metrics for user {user_id}")
    return await DashboardService(db).get_dashboard_metrics(user_id)


@router.websocket("/ws")
async def dashboard_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint establishing a real-time analytics connection.
    Authenticates using token query parameters.
    """
    logger.info("WebSocket: Connection request received.")

    # 1. Parse and validate JWT token
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        logger.warning("WebSocket: Authentication failed. Closing socket.")
        await websocket.close(code=4008) # Policy Violation code
        return

    user_id_str = payload["sub"]

    # 2. Register connection
    await connection_manager.connect(user_id_str, websocket)

    try:
        user_id = uuid.UUID(user_id_str)
        # 3. Push initial compiled dashboard statistics
        metrics = await DashboardService(db).get_dashboard_metrics(user_id)
        await connection_manager.send_dashboard_update(user_id_str, metrics)

        # 4. Stay alive loop, waiting for incoming messages or ping/pongs
        while True:
            # We discard client payloads but keep socket open
            data = await websocket.receive_text()
            logger.debug(f"WebSocket: Received ping from user {user_id_str}: {data}")
            # Optional: Echo back heartbeat
            await websocket.send_json({"event": "pong"})

    except WebSocketDisconnect:
        connection_manager.disconnect(user_id_str)
    except Exception as e:
        logger.error(f"WebSocket: Connection error for user {user_id_str}: {e}")
        connection_manager.disconnect(user_id_str)
