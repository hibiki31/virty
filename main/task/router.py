from asyncio.log import logger
from fastapi import APIRouter, Depends, HTTPException
from starlette.websockets import WebSocket
from starlette.requests import Request
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from sqlalchemy.orm import Session
from sqlalchemy import desc, true
from mixin.database import get_db
from auth.router import get_current_user, CurrentUser

from .models import *
from .schemas import *

import time
import hashlib


class WebSocketApp(WebSocketEndpoint):
    encoding = 'bytes'

    async def on_connect(self, websocket):
        await websocket.accept()

    async def on_receive(self, websocket, data):
        await websocket.send_bytes(b"Message: " + data)

    async def on_disconnect(self, websocket, close_code):
        pass


app = APIRouter()


# WebSockets用のエンドポイント
# @app.websocket("/ws")
# async def websocket_endpoint(ws: WebSocket):
#     await ws.accept()
#     # クライアントを識別するためのIDを取得
#     key = ws.headers.get('sec-websocket-key')
#     ws_clients[key] = ws
#     logger.info(key)
#     try:
#         while True:
#             # クライアントからメッセージを受信
#             data = await ws.receive_text()
#             # 接続中のクライアントそれぞれにメッセージを送信（ブロードキャスト）
#             logger.info("aaaa")
#             for client in ws_clients.values():
#                 await client.send_text(f"ID: {key} | Message: {data}")
#     except:
#         await ws.close()
#         # 接続が切れた場合、当該クライアントを削除する
#         del ws_clients[key]

# async def close_ws():
#     for client in ws_clients.values():
#         await client.close()


@app.get("/api/tasks", tags=["task"])
def get_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        update_mode: bool = False,
        update_hash: str = None,
    ):
    # if update_mode:
    #     while true:
    #         task: TaskModel = db.query(TaskModel).filter(TaskModel.status!="finish").all()
    #         task_count = len(task)
    #         task_hash = str(hashlib.md5(str([i.uuid for i in task]).encode()).hexdigest())
    #         if task_hash != update_hash:
    #             return {"task_hash": task_hash, "task_count": task_count}
    #         time.sleep(1)
        
    # else:
    task = db.query(TaskModel).order_by(desc(TaskModel.post_time)).all()
    
    return task


@app.get("/api/tasks/{uuid}", tags=["task"], response_model=TaskSelect)
def get_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid: str = None,
        polling: bool = False
    ):
    while True:
        try:
            task: TaskModel = db.query(TaskModel).filter(TaskModel.uuid==uuid).one()
        except:
            raise HTTPException(status_code=404, detail="task not fund")
        if task.status == "finish":
            break
        if polling:
            time.sleep(0.5)
            db.commit() # こいつないと、他が加えたDBの変更入らない
            continue
        break
    
    return task


@app.delete("/api/tasks", tags=["task"], response_model=List[TaskSelect])
def delete_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    # current_user.verify_scope(["admin"])
    model = db.query(TaskModel).all()
    db.query(TaskModel).delete()
    db.commit()

    return model