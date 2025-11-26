import asyncio
import websockets

class WS:
  def __init__(self, host="localhost", port=8765):
    self.host = host
    self.port = port
    self.clients = set()  # store connected clients

  async def message(self, websocket, path):
    self.clients.add(websocket)
    try:
      async for message in websocket:
        print(f"Received from client: {message}")
        await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
      print("Client disconnected")
    finally:
      self.clients.remove(websocket)

  async def send(self, payload):
    # Send to all connected clients
    if self.clients:
      await asyncio.wait([client.send(payload) for client in self.clients])

  async def serve(self):
    print(f"WebSocket server running at ws://{self.host}:{self.port}")
    async with websockets.serve(self.message, self.host, self.port):
      await asyncio.Future()  # run forever