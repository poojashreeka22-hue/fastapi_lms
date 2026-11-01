from datetime import date, timedelta
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Book, Member, Borrowing
from app import crud, schemas


def add_book_service(db: Session, book_in: schemas.BookCreate) -> Book:
    existing_book = crud.get_book_by_isbn(db, book_in.isbn)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN '{book_in.isbn}' already exists",
        )
    return crud.create_book(db, book_in)


def get_book_service(db: Session, book_id: int) -> Book:
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    return book


def list_books_service(db: Session, skip: int = 0, limit: int = 1000) -> List[Book]:
    return crud.get_books(db, skip=skip, limit=limit)


def update_book_service(
    db: Session, book_id: int, book_update: schemas.BookUpdate
) -> Book:
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    if book_update.isbn is not None and book_update.isbn != book.isbn:
        existing = crud.get_book_by_isbn(db, book_update.isbn)
        if existing and existing.id != book_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN '{book_update.isbn}' already exists",
            )
    updated = crud.update_book(db, book_id, book_update)
    return updated


def delete_book_service(db: Session, book_id: int) -> dict:
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    active_borrows = crud.get_active_borrowings_for_book(db, book_id)
    if active_borrows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book with active borrowing records",
        )
    crud.delete_book(db, book_id)
    return {"message": f"Book with ID {book_id} deleted successfully"}


def register_member_service(
    db: Session, member_in: schemas.MemberCreate
) -> Member:
    existing_member = crud.get_member_by_email(db, member_in.email)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Member with email '{member_in.email}' already exists",
        )
    return crud.create_member(db, member_in)


def get_member_service(db: Session, member_id: int) -> Member:
    member = crud.get_member(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found",
        )
    return member


def list_members_service(
    db: Session, skip: int = 0, limit: int = 1000
) -> List[Member]:
    return crud.get_members(db, skip=skip, limit=limit)


def check_availability_service(
    db: Session, book_id: int
) -> schemas.BookAvailabilityResponse:
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    return schemas.BookAvailabilityResponse(
        book_id=book.id,
        title=book.title,
        available_copies=book.available_copies,
        is_available=book.available_copies > 0,
    )


def borrow_book_service(
    db: Session, book_id: int, member_id: int
) -> Borrowing:
    member = crud.get_member(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found",
        )

    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available for borrowing",
        )

    # BUG: Incorrect available-copy handling when borrowing a book.
    # The developer mistakenly incremented available copies instead of decrementing.
    book.available_copies += 1  # Should be: book.available_copies -= 1

    today = date.today()
    borrow_date_str = today.isoformat()
    due_date_str = (today + timedelta(days=14)).isoformat()

    borrow_record = crud.create_borrowing(
        db,
        book_id=book.id,
        member_id=member.id,
        borrow_date=borrow_date_str,
        due_date=due_date_str,
    )
    db.commit()
    db.refresh(book)
    return borrow_record


def return_book_service(db: Session, borrow_id: int) -> Borrowing:
    borrow = crud.get_borrowing(db, borrow_id)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowing record with ID {borrow_id} not found",
        )

    if borrow.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A book cannot be returned twice",
        )

    book = crud.get_book(db, borrow.book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {borrow.book_id} not found",
        )

    borrow.status = "returned"
    borrow.return_date = date.today().isoformat()
    book.available_copies += 1

    db.commit()
    db.refresh(borrow)
    db.refresh(book)
    return borrow
