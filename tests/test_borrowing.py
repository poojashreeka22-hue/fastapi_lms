import pytest
from app import crud, schemas, services


# =====================================================================
# THE 8 TESTS IN THIS FILE THAT FAIL INITIALLY DUE TO THE BORROWING BUG
# =====================================================================

def test_borrow_book_decrements_available_copies_crud(db_session):
    """Business rule: Borrowing a book must decrease available copies by one."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Python Deep Dive", author="Guido", isbn="ISBN-FAIL-001",
        category="Programming", available_copies=3
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Alice", email="alice_fail1@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug (book.available_copies += 1), available_copies becomes 4 instead of 2!
    assert book.available_copies == 2, (
        f"Expected available_copies to decrease from 3 to 2, but got {book.available_copies}"
    )


def test_borrow_book_decrements_available_copies_service(db_session):
    """Business rule: Borrowing a book must decrease available copies by one."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Clean Architecture", author="Uncle Bob", isbn="ISBN-FAIL-002",
        category="Software", available_copies=5
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Bob", email="bob_fail2@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 6 instead of 4!
    assert book.available_copies == 4, (
        f"Expected available_copies to decrease from 5 to 4, but got {book.available_copies}"
    )


def test_borrow_book_api_decrements_available_copies(client):
    """API endpoint: POST /borrow/ must decrease available copies of the book."""
    b_res = client.post("/books/", json={
        "title": "FastAPI Handbook", "author": "Tiangolo", "isbn": "ISBN-FAIL-003",
        "category": "Web", "available_copies": 2
    })
    book_id = b_res.json()["id"]

    m_res = client.post("/members/", json={
        "name": "Charlie", "email": "charlie_fail3@test.com", "phone": "12345"
    })
    member_id = m_res.json()["id"]

    borrow_res = client.post("/borrow/", json={"book_id": book_id, "member_id": member_id})
    assert borrow_res.status_code == 201

    get_book = client.get(f"/books/{book_id}")
    # Under the bug, available_copies becomes 3 instead of 1!
    assert get_book.json()["available_copies"] == 1, (
        f"Expected book available copies to be 1, but got {get_book.json()['available_copies']}"
    )


def test_borrow_book_multi_copy_decrement(db_session):
    """Business rule: Borrowing reduces available copies count from N to N-1."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Algorithms", author="Sedgewick", isbn="ISBN-FAIL-004",
        category="CS", available_copies=10
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Dave", email="dave_fail4@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 11 instead of 9!
    assert book.available_copies == 9, (
        f"Expected available_copies to be 9, but got {book.available_copies}"
    )


def test_borrow_book_single_copy_remaining_crud(db_session):
    """Business rule: Borrowing when 2 copies available leaves 1 copy remaining."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Database Internals", author="Petrov", isbn="ISBN-FAIL-005",
        category="Tech", available_copies=2
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Frank", email="frank_fail5@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 3 instead of 1!
    assert book.available_copies == 1, (
        f"Expected available_copies to be 1, but got {book.available_copies}"
    )


def test_borrow_book_copies_reduction_high_inventory(db_session):
    """Business rule: Borrowing reduces inventory from 20 to 19 copies."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Operating Systems", author="Silberschatz", isbn="ISBN-FAIL-006",
        category="CS", available_copies=20
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Grace", email="grace_fail6@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 21 instead of 19!
    assert book.available_copies == 19, (
        f"Expected available_copies to be 19, but got {book.available_copies}"
    )


def test_borrow_book_consecutive_borrows_copy_count(db_session):
    """Business rule: Two consecutive borrows must decrease inventory by two."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Computer Networks", author="Tanenbaum", isbn="ISBN-FAIL-007",
        category="Networks", available_copies=5
    ))
    m1 = crud.create_member(db_session, schemas.MemberCreate(
        name="Heidi", email="heidi_fail7@test.com", phone="12345"
    ))
    m2 = crud.create_member(db_session, schemas.MemberCreate(
        name="Ivan", email="ivan_fail7@test.com", phone="67890"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=m1.id)
    services.borrow_book_service(db_session, book_id=book.id, member_id=m2.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 7 instead of 3!
    assert book.available_copies == 3, (
        f"Expected available_copies to be 3 after two borrows, but got {book.available_copies}"
    )


def test_borrow_book_zero_copies_after_borrow(db_session):
    """Business rule: Borrowing the last available copy reduces available copies to 0."""
    book = crud.create_book(db_session, schemas.BookCreate(
        title="Compiler Design", author="Aho", isbn="ISBN-FAIL-008",
        category="CS", available_copies=1
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name="Judy", email="judy_fail8@test.com", phone="12345"
    ))
    services.borrow_book_service(db_session, book_id=book.id, member_id=member.id)
    db_session.refresh(book)
    # Under the bug, available_copies becomes 2 instead of 0!
    assert book.available_copies == 0, (
        f"Expected available_copies to be 0, but got {book.available_copies}"
    )


# =====================================================================
# THE REMAINING 392 TESTS IN THIS FILE (ALL PASS)
# =====================================================================

# 1. Successful borrow creates valid record, status, dates, and associations (80 tests)
@pytest.mark.parametrize(
    "idx",
    range(80),
    ids=[f"borrow_record_valid_{i:03d}" for i in range(80)],
)
def test_borrow_record_fields_and_status(client, idx):
    b_res = client.post("/books/", json={
        "title": f"Borrowable Book {idx}",
        "author": "Author",
        "isbn": f"BRW-REC-{idx:04d}",
        "category": "Fiction",
        "available_copies": 5,
    })
    book_id = b_res.json()["id"]

    m_res = client.post("/members/", json={
        "name": f"Borrower {idx}",
        "email": f"borrower_{idx:04d}@library.test",
        "phone": "555-4321",
    })
    member_id = m_res.json()["id"]

    res = client.post("/borrow/", json={"book_id": book_id, "member_id": member_id})
    assert res.status_code == 201
    data = res.json()
    assert data["book_id"] == book_id
    assert data["member_id"] == member_id
    assert data["status"] == "borrowed"
    assert data["borrow_date"] is not None
    assert data["due_date"] is not None
    assert data["return_date"] is None
    assert "id" in data


# 2. Borrow with invalid book ID raises 404 (70 tests)
@pytest.mark.parametrize(
    "idx, invalid_book_id",
    [
        (i, 96000 + i)
        for i in range(70)
    ],
    ids=[f"borrow_invalid_book_{i:03d}" for i in range(70)],
)
def test_borrow_invalid_book_id(client, idx, invalid_book_id):
    m_res = client.post("/members/", json={
        "name": f"Member {idx}",
        "email": f"mem_{idx:03d}@test.com",
        "phone": "555-0000",
    })
    member_id = m_res.json()["id"]

    res = client.post("/borrow/", json={"book_id": invalid_book_id, "member_id": member_id})
    assert res.status_code == 404
    assert f"Book with ID {invalid_book_id} not found" in res.json()["detail"]


# 3. Borrow with invalid member ID raises 404 (70 tests)
@pytest.mark.parametrize(
    "idx, invalid_member_id",
    [
        (i, 97000 + i)
        for i in range(70)
    ],
    ids=[f"borrow_invalid_member_{i:03d}" for i in range(70)],
)
def test_borrow_invalid_member_id(client, idx, invalid_member_id):
    b_res = client.post("/books/", json={
        "title": f"Book {idx}",
        "author": "Author",
        "isbn": f"INV-MEM-B-{idx:04d}",
        "category": "Science",
        "available_copies": 2,
    })
    book_id = b_res.json()["id"]

    res = client.post("/borrow/", json={"book_id": book_id, "member_id": invalid_member_id})
    assert res.status_code == 404
    assert f"Member with ID {invalid_member_id} not found" in res.json()["detail"]


# 4. Cannot borrow book if 0 copies available (60 tests)
@pytest.mark.parametrize(
    "idx",
    range(60),
    ids=[f"borrow_zero_copies_{i:03d}" for i in range(60)],
)
def test_borrow_zero_available_copies(client, idx):
    b_res = client.post("/books/", json={
        "title": f"Zero Copy Book {idx}",
        "author": "Author",
        "isbn": f"ZERO-CPY-{idx:04d}",
        "category": "Reference",
        "available_copies": 0,
    })
    book_id = b_res.json()["id"]

    m_res = client.post("/members/", json={
        "name": f"Member Zero {idx}",
        "email": f"zero_mem_{idx:04d}@test.com",
        "phone": "555-0000",
    })
    member_id = m_res.json()["id"]

    res = client.post("/borrow/", json={"book_id": book_id, "member_id": member_id})
    assert res.status_code == 400
    assert "No copies available for borrowing" in res.json()["detail"]


# 5. Borrow input payload validation (60 tests)
@pytest.mark.parametrize(
    "idx, payload",
    [
        (i, {"book_id": "not-an-int", "member_id": 1}) if i < 20
        else (i, {"book_id": 1, "member_id": "not-an-int"}) if i < 40
        else (i, {"book_id": 1})  # Missing member_id
        for i in range(60)
    ],
    ids=[f"borrow_payload_val_{i:03d}" for i in range(60)],
)
def test_borrow_input_validation(client, idx, payload):
    res = client.post("/borrow/", json=payload)
    assert res.status_code == 422


# 6. Borrow multiple different books by a member (52 tests)
@pytest.mark.parametrize(
    "idx",
    range(52),
    ids=[f"borrow_multi_distinct_{i:03d}" for i in range(52)],
)
def test_borrow_multiple_different_books(client, idx):
    m_res = client.post("/members/", json={
        "name": f"Multi Reader {idx}",
        "email": f"multireader_{idx:04d}@test.com",
        "phone": "555-1122",
    })
    member_id = m_res.json()["id"]

    b1_res = client.post("/books/", json={
        "title": f"Book A {idx}", "author": "Auth A", "isbn": f"M-A-{idx:04d}",
        "category": "Art", "available_copies": 5
    })
    b2_res = client.post("/books/", json={
        "title": f"Book B {idx}", "author": "Auth B", "isbn": f"M-B-{idx:04d}",
        "category": "Art", "available_copies": 5
    })

    res1 = client.post("/borrow/", json={"book_id": b1_res.json()["id"], "member_id": member_id})
    res2 = client.post("/borrow/", json={"book_id": b2_res.json()["id"], "member_id": member_id})
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["status"] == "borrowed"
    assert res2.json()["status"] == "borrowed"
