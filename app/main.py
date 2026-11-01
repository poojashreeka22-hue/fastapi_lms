from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import schemas, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables automatically on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Library Management System API",
    description="A beginner-friendly REST API for managing books, members, and borrowings.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Library Management System API!",
        "documentation": "/docs",
        "endpoints": {
            "books": "/books/",
            "members": "/members/",
            "borrow": "/borrow/",
            "return": "/return/",
        },
    }


# --- 1. Add a book ---
@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return services.add_book_service(db, book)


# --- 2. View all books ---
@app.get(
    "/books/",
    response_model=List[schemas.BookResponse],
    tags=["Books"],
)
def view_all_books(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return services.list_books_service(db, skip=skip, limit=limit)


# --- 3. Search for a book by ID ---
@app.get(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    tags=["Books"],
)
def search_book_by_id(book_id: int, db: Session = Depends(get_db)):
    return services.get_book_service(db, book_id)


# --- 4. Update book details ---
@app.put(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    tags=["Books"],
)
def update_book(
    book_id: int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)
):
    return services.update_book_service(db, book_id, book_update)


# --- 5. Delete a book ---
@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_200_OK,
    tags=["Books"],
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return services.delete_book_service(db, book_id)


# --- 6. Register a library member ---
@app.post(
    "/members/",
    response_model=schemas.MemberResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Members"],
)
def register_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return services.register_member_service(db, member)


# --- 7. View all members ---
@app.get(
    "/members/",
    response_model=List[schemas.MemberResponse],
    tags=["Members"],
)
def view_all_members(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return services.list_members_service(db, skip=skip, limit=limit)


# --- 8. Borrow a book ---
@app.post(
    "/borrow/",
    response_model=schemas.BorrowResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Borrowing"],
)
def borrow_book(borrow_in: schemas.BorrowCreate, db: Session = Depends(get_db)):
    return services.borrow_book_service(db, borrow_in.book_id, borrow_in.member_id)


# --- 9. Return a borrowed book ---
@app.post(
    "/return/",
    response_model=schemas.BorrowResponse,
    status_code=status.HTTP_200_OK,
    tags=["Borrowing"],
)
def return_book(return_in: schemas.ReturnRequest, db: Session = Depends(get_db)):
    return services.return_book_service(db, return_in.borrow_id)


# --- 10. Check book availability ---
@app.get(
    "/books/{book_id}/availability",
    response_model=schemas.BookAvailabilityResponse,
    tags=["Books"],
)
def check_book_availability(book_id: int, db: Session = Depends(get_db)):
    return services.check_availability_service(db, book_id)
