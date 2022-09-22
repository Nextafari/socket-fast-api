import ijson
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from manager import ConnectionManager

app = FastAPI()
socket_manager = ConnectionManager()


@app.get("/scanner-poses")
def get_scanner_poses():
    """Robot pose for possible localization"""
    poses = {
        "pose_front": {
            "x": 0.3440000116825104,
            "y": -0.3190000057220459,
            "theta": 1.5707900524139404,
        },
        "pose_rear": {
            "x": -0.3440000116825104,
            "y": 0.3190000057220459,
            "theta": -1.5707900524139404,
        },
    }
    return JSONResponse(conetent := (data := jsonable_encoder(poses)))


@app.get("/robot-dimensions")
def get_dimensions():
    """Robot dimension"""
    dim = {"length": 0.816, "width": 0.766}
    return JSONResponse(content := (data := jsonable_encoder(dim)))


@app.websocket("/ws/stream-location")
async def stream_location(websocket: WebSocket):
    """
    Retrieve data in parts using ijson and keeping the file open,
    to avoid having to use load up all data in memory
    """
    await socket_manager.connect(websocket)
    try:
        while True:
            with open("challenge.json", "rb") as f:
                data = list(ijson.items(f, "data.item", use_float=True))
                for i in data:
                    await socket_manager.send_message(i, websocket)
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)
        print("Socket error, disconnecting ==>>>> \n ==>>>>")
