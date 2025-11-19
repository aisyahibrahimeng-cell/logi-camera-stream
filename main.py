from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

# Store viewer clients
viewers = set()

@app.get("/")
async def home():
    return {"status": "WebSocket server is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    viewers.add(websocket)
    print("Viewer connected")

    try:
        while True:
            await asyncio.sleep(1)
    except:
        viewers.remove(websocket)

@app.websocket("/upload")
async def upload_endpoint(websocket: WebSocket):
    """Raspberry Pi will connect here and send frames to viewers"""
    await websocket.accept()
    print("Pi connected")

    try:
        while True:
            frame = await websocket.receive_text()  # Base64 frame
            # Forward to all viewers
            for v in viewers.copy():
                try:
                    await v.send_text(frame)
                except:
                    viewers.remove(v)
    except:
        print("Pi disconnected")
