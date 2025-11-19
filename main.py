from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Allow cross-origin requests so your HTML can run anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket viewers
viewers = set()
last_frame = None

# HTML for quick test (optional)
HTML = """
<!doctype html>
<html>
<head>
<title>Live Camera</title>
</head>
<body>
<h1>Logitech Camera Live</h1>
<img id="stream" width="640">
<script>
let ws = new WebSocket("wss://" + location.host + "/ws");
let img = document.getElementById("stream");

ws.onmessage = function(event){
    img.src = "data:image/jpeg;base64," + event.data;
};
</script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(HTML)

# ---------------- WebSocket for viewers ----------------
@app.websocket("/ws")
async def websocket_viewer(websocket: WebSocket):
    global last_frame
    await websocket.accept()
    viewers.add(websocket)

    # Send last frame immediately for fast first frame
    if last_frame:
        await websocket.send_text(last_frame)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        viewers.remove(websocket)

# ---------------- WebSocket for Pi upload ----------------
@app.websocket("/upload")
async def websocket_upload(websocket: WebSocket):
    global last_frame
    await websocket.accept()
    print("Pi connected")
    try:
        while True:
            frame = await websocket.receive_text()
            last_frame = frame

            # broadcast to all viewers
            dead = []
            for v in viewers:
                try:
                    await v.send_text(frame)
                except:
                    dead.append(v)

            for v in dead:
                viewers.remove(v)
    except WebSocketDisconnect:
        print("Pi disconnected")

# ---------------- HTTP endpoint for commands ----------------
@app.post("/control")
async def send_command(command: dict):
    cmd = command.get("cmd")
    if cmd:
        print(f"Command received: {cmd}")
        # TODO: forward this to ROS2 or Pi if needed
        # Example: store last command, or forward to Pi via WebSocket
        return {"status": "ok", "cmd": cmd}
    return {"status": "error", "reason": "no command provided"}
