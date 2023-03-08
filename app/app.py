from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Union
from . import auth
import ast
from .db import models, schemas, crud
from .db.database import engine, SessionLocal
from .connection_manager import ConnectionManager
from .game import Game


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static"), name="static")


manager = ConnectionManager()
game = Game(manager)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/me/")
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/")
async def some_func(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": "hello"})


@app.get("/{room}")
async def some_func(request: Request, room: int):
    return templates.TemplateResponse("websocket.html", {"request": request, "room": room})



@app.post("/token", response_model=auth.Token)
async def login_for_access_token(db: Session = Depends(get_db) , form_data: auth.OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=auth.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def commands(websocket, data):
    command = data.get("command")

    if command == "ready":
        await game.add_readies(websocket)
    elif command == "not ready":
        await game.remove_readies(websocket)


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: int):
    if manager.get_connections_amount(websocket.get("path")) < 2:
        await manager.connect(websocket)
        await manager.send_connections_amount(websocket.get("path"))
        try:
            while True:
                data = await websocket.receive_text()
                data = ast.literal_eval(data)
                if data.get("command"):
                    await commands(websocket, data)
                elif data.get("result"):
                    path = websocket.get("path")
                    gamer = websocket.get("client")[1]
                    result = data.get('result')
                    await game.on_game_over(path, gamer, result, websocket)
        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            await manager.send_connections_amount(websocket.get("path"))