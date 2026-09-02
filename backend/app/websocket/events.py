from app.websocket.connection_manager import manager


async def broadcast_event(event: str, data: dict):
    await manager.broadcast(
        {
            "event": event,
            "data": data,
        }
    )