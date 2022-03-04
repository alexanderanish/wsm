from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
import uvicorn
import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from fastapi_users import FastAPIUsers
from fastapi_users.db import MongoDBUserDatabase
from fastapi.staticfiles import StaticFiles
from apps.auth.auth import jwt_authentication
from apps.auth.models import User, UserCreate, UserUpdate, UserDB
from apps.todo.routers import router as todo_router
from apps.user.routers import router as user_router
from apps.stock.routers import router as stock_router, stock_page_router, post_router, comment_router
from apps.external.routers import router as external_router
from apps.auth.routers import get_users_router, router as auth_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv('.env')

app = FastAPI()


SECRET_KEY = "b750fab2229674e86d5fddeb9e61af884a3c612560f3d4ae6fd03206d0885309"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.on_event("startup")
async def startup_db_client():
    # app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    # app.mongodb = app.mongodb_client[settings.DB_NAME]

    app.mongodb_client = AsyncIOMotorClient(
        settings.DB_URL, uuidRepresentation="standard"
    )
    app.db = app.mongodb_client[settings.DB_NAME]

    user_db = MongoDBUserDatabase(UserDB, app.db["users"])

    app.fastapi_users = FastAPIUsers(
        user_db,
        [jwt_authentication],
        User,
        UserCreate,
        UserUpdate,
        UserDB,
    )

    app.include_router(get_users_router(app))
    app.include_router(auth_router, tags=["auth"], prefix="/auth")
    # app.include_router(stock_router, tags=["stock"], prefix="/stock")
    app.include_router(external_router, tags=["external"], prefix="/external")
    app.include_router(stock_page_router(app), tags=["stock-page"], prefix="/stock-page")
    app.include_router(post_router(app), tags=["post"], prefix="/posts")
    app.include_router(comment_router(app), tags=["comment"], prefix="/comment")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


notifier = Notifier()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    print ('>>>>>>>>>.Connection Initiated>>>>>>>>.')
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Total Active Connections are : {len(notifier.connections)}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


@app.get("/push/{message}")
async def push_to_connected_websockets(message: str):
    print ('$$$$Recievddddd', message)
    await notifier.push(f"! Push notification: {message} !")

@app.get('/send-email/backgroundtasks')
def send_email_backgroundtasks(background_tasks: BackgroundTasks):
    send_email_background(background_tasks, 'WSM Project',   
    'azarmhmd21@gmail.com', "title: 'Hello World', 'name':       'John Doe'")
    return 'Success'


@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)

    
# app.include_router(todo_router, tags=["tasks"], prefix="/task")
# app.include_router(user_router, tags=["auth"], prefix="/auth")


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
