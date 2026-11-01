from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)
    available_copies = Column(Integer, nullable=False, default=1)

    borrowings = relationship("Borrowing", back_populates="book", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=False)

    borrowings = relationship("Borrowing", back_populates="member", cascade="all, delete-orphan")


class Borrowing(Base):
    __tablename__ = "borrowings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    borrow_date = Column(String(50), nullable=False)
    due_date = Column(String(50), nullable=False)
    return_date = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="borrowed")

    book = relationship("Book", back_populates="borrowings")
    member = relationship("Member", back_populates="borrowings")
