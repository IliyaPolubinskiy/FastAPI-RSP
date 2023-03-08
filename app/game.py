from fastapi import WebSocket


class Game:


    def __init__(self, manager):
        self.manager = manager
        self.readies = []
        self.games = {}


    async def add_readies(self, websocket: WebSocket):
        if websocket not in self.readies:
            self.readies.append(websocket)
        amount_of_ready = 0
        for ws in self.readies:
            if ws.get("path") == websocket.get("path"):
                amount_of_ready += 1
                await self.send_status_to_opponent(websocket, status = True)
        if amount_of_ready == 2:
            for ws in self.readies:
                if ws.get("path") == websocket.get("path"):
                    await self.send_status_to_opponent(websocket, status = True)
                    await ws.send_json({"command": "start"})


    async def remove_readies(self, websocket):
        self.readies.remove(websocket)
        await self.send_status_to_opponent(websocket, status = False)


    async def send_status_to_opponent(self, websocket: WebSocket, status: bool):
        path = websocket.get("path")
        opponent = None
        for ws in self.manager.active_connections:
            if ws != websocket and ws.get("path") == path:
                opponent = ws
        if opponent is not None:
            await opponent.send_json({"command": "update_opponent_status",
                                      "opponent_status": status})


    async def on_game_over(self, path: str, gamer: int, result: str, websocket: WebSocket):
        if not self.games.get(path):
            self.games[path] = {}
        self.games[path][gamer] = result
        if len(self.games[path]) == 2:
            await self.get_winner(self.games[path], path)
        

    async def get_winner(self, result: dict, path: str):
        values=[]
        keys=[]
        for k, v in result.items():
            values.append(v)
            keys.append(k)

        if values[0] == values[1]:
            await self.send_result(path, keys[1], keys[0], {"winner": "no one", "item": values[0]})
        elif values[0] == "rock" and values[1] == "paper":
            await self.send_result(path, keys[1], keys[0], {"winner": {keys[1]: values[1]}, "loser": {keys[0]: values[0]}})
        elif values[0] == "rock" and values[1] == "clippers":
            await self.send_result(path, keys[0], keys[1], {"winner": {keys[0]: values[0]}, "loser": {keys[1]: values[1]}})
        elif values[0] == "paper" and values[1] == "rock":
            await self.send_result(path, keys[0], keys[1], {"winner": {keys[0]: values[0]}, "loser": {keys[1]: values[1]}})
        elif values[0] == "paper" and values[1] == "clippers":
            await self.send_result(path, keys[1], keys[0], {"winner": {keys[1]: values[1]}, "loser": {keys[0]: values[0]}})
        elif values[0] == "clippers" and values[1] == "rock":
            await self.send_result(path, keys[1], keys[0], {"winner": {keys[1]: values[1]}, "loser": {keys[0]: values[0]}})
        elif values[0] == "clippers" and values[1] == "paper":
            await self.send_result(path, keys[0], keys[1], {"winner": {keys[0]: values[0]}, "loser": {keys[1]: values[1]}})

    
    async def send_result(self, path, winner, loser, result):
        for ws in self.manager.active_connections:
            if path == ws.get("path"):
                client = ws.get("client")[1]
                if result.get("winner") != "no one": 
                    if client == winner:
                        await ws.send_json({"result": {
                                            "win": True,
                                            "winner_item": result.get("winner").get(winner),
                                            "loser_item": result.get("loser").get(loser),
                                            "result": result
                                            }})
                    elif client == loser:
                        await ws.send_json({"result": {
                                            "win": False,
                                            "winner_item": result.get("winner").get(winner),
                                            "loser_item": result.get("loser").get(loser),
                                            "result": result
                                            }})
                elif result.get("winner") == "no one":
                    await ws.send_json({"result": {
                                        "win": "no one",
                                        "item": result.get("item"),
                                        }})
                self.games[path] = None
                await self.remove_readies(ws)
