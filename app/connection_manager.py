from .app import WebSocket 



class ConnectionManager:
    

    def __init__(self):
        self.active_connections: list[WebSocket] = []


    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)


    async def disconnect(self, websocket: WebSocket):
        if websocket in self.readies:
            await self.remove_readies(websocket)
        self.active_connections.remove(websocket)


    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


    async def broadcast(self, path: str, message: str):
        for ws in self.active_connections:
            if path == ws.get("path"):
                await ws.send_json({"message": message})


    async def send_connections_amount(self, path):
        amount = 0
        for ws in self.active_connections:
            if path == ws.get("path"):
                amount += 1
        for ws in self.active_connections:
            if path == ws.get("path"):
                await ws.send_json({"connections": amount})


    def get_connections_amount(self, path):
        amount = 0
        for ws in self.active_connections:
            if path == ws.get("path"):
                amount += 1
        return amount