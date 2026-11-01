from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Book Schemas ---
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    available_copies: int = Field(default=1, ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(default=None, min_length=1, max_length=50)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    available_copies: Optional[int] = Field(default=None, ge=0)


class BookResponse(BookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookAvailabilityResponse(BaseModel):
    book_id: int
    title: str
    available_copies: int
    is_available: bool


# --- Member Schemas ---
class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=50)


class MemberCreate(MemberBase):
    pass


class MemberResponse(MemberBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Borrowing Schemas ---
class BorrowCreate(BaseModel):
    book_id: int
    member_id: int


class ReturnRequest(BaseModel):
    borrow_id: int


class BorrowResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrow_date: str
    due_date: str
    return_date: Optional[str] = None
    status: str
    model_config = ConfigDict(from_attributes=True)
