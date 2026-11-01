import pytest
from datetime import date
from app import crud, schemas, services


# 1. Returning a book increases available copies by one (100 tests)
@pytest.mark.parametrize(
    "idx, initial_copies",
    [
        (i, (i % 10) + 1)
        for i in range(100)
    ],
    ids=[f"return_inc_copies_{i:03d}" for i in range(100)],
)
def test_return_book_increases_copies(client, db_session, idx, initial_copies):
    book = crud.create_book(db_session, schemas.BookCreate(
        title=f"Returnable Book {idx}", author="Author", isbn=f"RET-INC-{idx:04d}",
        category="Science", available_copies=initial_copies
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name=f"Returner {idx}", email=f"ret_{idx:04d}@test.com", phone="12345"
    ))
    borrow = crud.create_borrowing(
        db_session, book_id=book.id, member_id=member.id,
        borrow_date="2026-01-01", due_date="2026-01-15"
    )

    res = client.post("/return/", json={"borrow_id": borrow.id})
    assert res.status_code == 200

    db_session.refresh(book)
    assert book.available_copies == initial_copies + 1


# 2. A book cannot be returned twice (70 tests)
@pytest.mark.parametrize(
    "idx",
    range(70),
    ids=[f"return_double_prevention_{i:03d}" for i in range(70)],
)
def test_cannot_return_twice(client, db_session, idx):
    book = crud.create_book(db_session, schemas.BookCreate(
        title=f"Double Return Book {idx}", author="Author", isbn=f"DBL-RET-{idx:04d}",
        category="Tech", available_copies=2
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name=f"Member {idx}", email=f"dbl_{idx:04d}@test.com", phone="12345"
    ))
    borrow = crud.create_borrowing(
        db_session, book_id=book.id, member_id=member.id,
        borrow_date="2026-01-01", due_date="2026-01-15"
    )

    # First return succeeds
    res1 = client.post("/return/", json={"borrow_id": borrow.id})
    assert res1.status_code == 200

    # Second return must be rejected
    res2 = client.post("/return/", json={"borrow_id": borrow.id})
    assert res2.status_code == 400
    assert "cannot be returned twice" in res2.json()["detail"].lower()


# 3. Return updates status to 'returned' and sets return date (50 tests)
@pytest.mark.parametrize(
    "idx",
    range(50),
    ids=[f"return_status_date_{i:03d}" for i in range(50)],
)
def test_return_updates_status_and_date(client, db_session, idx):
    book = crud.create_book(db_session, schemas.BookCreate(
        title=f"Status Book {idx}", author="Author", isbn=f"RET-STAT-{idx:04d}",
        category="History", available_copies=1
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name=f"Member {idx}", email=f"stat_{idx:04d}@test.com", phone="12345"
    ))
    borrow = crud.create_borrowing(
        db_session, book_id=book.id, member_id=member.id,
        borrow_date="2026-01-01", due_date="2026-01-15"
    )

    res = client.post("/return/", json={"borrow_id": borrow.id})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "returned"
    assert data["return_date"] == date.today().isoformat()


# 4. Return nonexistent borrow record returns 404 (50 tests)
@pytest.mark.parametrize(
    "idx, invalid_borrow_id",
    [
        (i, 94000 + i)
        for i in range(50)
    ],
    ids=[f"return_not_found_{i:03d}" for i in range(50)],
)
def test_return_nonexistent_borrow_id(client, idx, invalid_borrow_id):
    res = client.post("/return/", json={"borrow_id": invalid_borrow_id})
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# 5. Return input validation (30 tests)
@pytest.mark.parametrize(
    "idx, payload",
    [
        (i, {"borrow_id": "not-an-int"}) if i < 15
        else (i, {})  # Missing borrow_id
        for i in range(30)
    ],
    ids=[f"return_input_val_{i:03d}" for i in range(30)],
)
def test_return_input_validation(client, idx, payload):
    res = client.post("/return/", json=payload)
    assert res.status_code == 422
