from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()
clients = []

HTML = """
<!doctype html>
<html>
<head>
<title>Camera Live</title>
</head>
<body>
<h1>Live Camera</h1>
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
async def index():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(data)
    except:
        clients.remove(websocket)
