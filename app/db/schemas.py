from typing import Union, List
from pydantic import BaseModel

class RoomBase(BaseModel):
    id: int


class Room(RoomBase):
    creator_id: int
    player_id: int
    uuid: str
    
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    first_name: str
    last_name: str
    rooms: list[Room] = []

    class Config:
        orm_mode = True    
