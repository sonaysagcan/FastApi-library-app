from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from connections import Base
from pydantic import BaseModel
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True, unique=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String)
    books = relationship("Book", back_populates="owner")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, Sequence("book_id_seq"), primary_key=True, index=True, unique=True)
    title = Column(String, index=True)
    author = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="books")
    due_date = Column(DateTime, default=func.now())

class UpdateUserData(BaseModel):
    username: str
    email: str
    full_name: str

class AddBookData(BaseModel):
    title: str
    author: str
