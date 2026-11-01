from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Book, Member, Borrowing
from app.schemas import BookCreate, BookUpdate, MemberCreate


# --- Book CRUD ---
def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.query(Book).filter(Book.id == book_id).first()


def get_book_by_isbn(db: Session, isbn: str) -> Optional[Book]:
    return db.query(Book).filter(Book.isbn == isbn).first()


def get_books(db: Session, skip: int = 0, limit: int = 1000) -> List[Book]:
    return db.query(Book).offset(skip).limit(limit).all()


def create_book(db: Session, book: BookCreate) -> Book:
    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        category=book.category,
        available_copies=book.available_copies,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book_update: BookUpdate) -> Optional[Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True


# --- Member CRUD ---
def get_member(db: Session, member_id: int) -> Optional[Member]:
    return db.query(Member).filter(Member.id == member_id).first()


def get_member_by_email(db: Session, email: str) -> Optional[Member]:
    return db.query(Member).filter(Member.email == email).first()


def get_members(db: Session, skip: int = 0, limit: int = 1000) -> List[Member]:
    return db.query(Member).offset(skip).limit(limit).all()


def create_member(db: Session, member: MemberCreate) -> Member:
    db_member = Member(
        name=member.name,
        email=member.email,
        phone=member.phone,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# --- Borrowing CRUD ---
def get_borrowing(db: Session, borrow_id: int) -> Optional[Borrowing]:
    return db.query(Borrowing).filter(Borrowing.id == borrow_id).first()


def get_active_borrowings_for_book(db: Session, book_id: int) -> List[Borrowing]:
    return (
        db.query(Borrowing)
        .filter(Borrowing.book_id == book_id, Borrowing.status == "borrowed")
        .all()
    )


def create_borrowing(
    db: Session, book_id: int, member_id: int, borrow_date: str, due_date: str
) -> Borrowing:
    db_borrow = Borrowing(
        book_id=book_id,
        member_id=member_id,
        borrow_date=borrow_date,
        due_date=due_date,
        status="borrowed",
    )
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow
