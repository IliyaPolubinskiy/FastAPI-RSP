from sqlalchemy import Integer, Column, String, ForeignKey, UUID, DateTime, Enum
import enum
from sqlalchemy.orm import relationship
import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Statuses(enum.Enum):
    created = "Created"
    played = "Played"
    canceled = "Canceled"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    status = Column(Enum(Statuses), default=Statuses.created)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    player_id = Column(Integer, ForeignKey("users.id"), default=None, index=True)


    creator = relationship("User", foreign_keys=[creator_id])
    player = relationship("User", foreign_keys=[player_id])
