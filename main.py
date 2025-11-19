from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

viewers = set()
last_frame = None


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

@app.websocket("/ws")
async def websocket_viewer(websocket: WebSocket):
    global last_frame

    await websocket.accept()
    viewers.add(websocket)
    print("Viewer connected")

    # send last frame instantly (faster first frame)
    if last_frame:
        await websocket.send_text(last_frame)

    try:
        while True:
            await websocket.receive_text()  # viewer sends nothing
    except WebSocketDisconnect:
        viewers.remove(websocket)
        print("Viewer disconnected")


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
