import pytest
from app import models, schemas


# 1. Book Model direct DB operations (25 tests)
@pytest.mark.parametrize(
    "idx",
    range(25),
    ids=[f"db_book_model_{i:03d}" for i in range(25)],
)
def test_book_model_attributes(db_session, idx):
    book = models.Book(
        title=f"Direct DB Book {idx}",
        author=f"Author {idx}",
        isbn=f"DB-BK-{idx:04d}",
        category="Direct",
        available_copies=(idx % 5) + 1,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    assert book.id is not None
    assert book.title == f"Direct DB Book {idx}"
    assert book.isbn == f"DB-BK-{idx:04d}"


# 2. Member Model direct DB operations (25 tests)
@pytest.mark.parametrize(
    "idx",
    range(25),
    ids=[f"db_member_model_{i:03d}" for i in range(25)],
)
def test_member_model_attributes(db_session, idx):
    member = models.Member(
        name=f"Direct Member {idx}",
        email=f"direct_mem_{idx:04d}@db.test",
        phone=f"555-88{idx:02d}",
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    assert member.id is not None
    assert member.email == f"direct_mem_{idx:04d}@db.test"


# 3. Borrowing Model direct DB operations & relationships (25 tests)
@pytest.mark.parametrize(
    "idx",
    range(25),
    ids=[f"db_borrow_model_{i:03d}" for i in range(25)],
)
def test_borrowing_model_attributes(db_session, idx):
    book = models.Book(
        title=f"Rel Book {idx}",
        author="Author",
        isbn=f"REL-B-{idx:04d}",
        category="Rel",
        available_copies=2,
    )
    member = models.Member(
        name=f"Rel Member {idx}",
        email=f"rel_mem_{idx:04d}@db.test",
        phone="555-0011",
    )
    db_session.add(book)
    db_session.add(member)
    db_session.commit()

    borrow = models.Borrowing(
        book_id=book.id,
        member_id=member.id,
        borrow_date="2026-02-01",
        due_date="2026-02-15",
        status="borrowed",
    )
    db_session.add(borrow)
    db_session.commit()
    db_session.refresh(borrow)

    assert borrow.id is not None
    assert borrow.book.title == f"Rel Book {idx}"
    assert borrow.member.name == f"Rel Member {idx}"


# 4. Schema Validations & Serialization (25 tests)
@pytest.mark.parametrize(
    "idx",
    range(25),
    ids=[f"schema_validation_{i:03d}" for i in range(25)],
)
def test_schema_validations_and_serialization(idx):
    # Test BookCreate
    book_in = schemas.BookCreate(
        title=f"Schema Book {idx}",
        author="Author",
        isbn=f"SCH-{idx:04d}",
        category="Testing",
        available_copies=idx,
    )
    assert book_in.available_copies == idx

    # Test MemberCreate
    mem_in = schemas.MemberCreate(
        name=f"Schema User {idx}",
        email=f"user_{idx}@test.org",
        phone="555-9999",
    )
    assert mem_in.name == f"Schema User {idx}"

    # Test BorrowCreate
    brw_in = schemas.BorrowCreate(book_id=idx + 1, member_id=idx + 2)
    assert brw_in.book_id == idx + 1
    assert brw_in.member_id == idx + 2

    # Test ReturnRequest
    ret_in = schemas.ReturnRequest(borrow_id=idx + 10)
    assert ret_in.borrow_id == idx + 10
