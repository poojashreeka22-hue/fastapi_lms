import pytest
from app import crud, schemas


# =====================================================================
# THE 2 TESTS IN THIS FILE THAT FAIL INITIALLY DUE TO THE BORROWING BUG
# =====================================================================

def test_book_availability_after_borrow_single_copy(client):
    """Business rule: When the last available copy of a book is borrowed, availability must become 0 and is_available False."""
    b_res = client.post("/books/", json={
        "title": "Unique Manuscript",
        "author": "Scholar",
        "isbn": "ISBN-AVAIL-FAIL-001",
        "category": "Rare",
        "available_copies": 1,
    })
    book_id = b_res.json()["id"]

    m_res = client.post("/members/", json={
        "name": "Eve",
        "email": "eve_avail@library.org",
        "phone": "555-0987",
    })
    member_id = m_res.json()["id"]

    borrow_res = client.post("/borrow/", json={"book_id": book_id, "member_id": member_id})
    assert borrow_res.status_code == 201

    avail_res = client.get(f"/books/{book_id}/availability")
    assert avail_res.status_code == 200
    data = avail_res.json()
    assert data["available_copies"] == 0, (
        f"Expected available copies to be 0 after borrowing the only copy, but got {data['available_copies']}"
    )
    assert data["is_available"] is False, (
        "Expected is_available to be False when 0 copies remain"
    )


def test_book_availability_after_borrow_multi_copy(client):
    """Business rule: Availability endpoint must reflect reduced copies after a book is borrowed."""
    b_res = client.post("/books/", json={
        "title": "Multi Copy Avail Book",
        "author": "Author",
        "isbn": "ISBN-AVAIL-FAIL-002",
        "category": "Fiction",
        "available_copies": 5,
    })
    book_id = b_res.json()["id"]

    m_res = client.post("/members/", json={
        "name": "Grace",
        "email": "grace_avail@library.org",
        "phone": "555-1122",
    })
    member_id = m_res.json()["id"]

    borrow_res = client.post("/borrow/", json={"book_id": book_id, "member_id": member_id})
    assert borrow_res.status_code == 201

    avail_res = client.get(f"/books/{book_id}/availability")
    assert avail_res.status_code == 200
    data = avail_res.json()
    assert data["available_copies"] == 4, (
        f"Expected available copies to be 4 after borrowing 1 of 5 copies, but got {data['available_copies']}"
    )


# =====================================================================
# THE REMAINING 148 TESTS IN THIS FILE (ALL PASS)
# =====================================================================

# 1. Books with available copies report is_available=True (60 tests)
@pytest.mark.parametrize(
    "idx, copies",
    [
        (i, (i % 15) + 1)
        for i in range(60)
    ],
    ids=[f"avail_positive_{i:03d}" for i in range(60)],
)
def test_availability_with_copies(client, idx, copies):
    res = client.post("/books/", json={
        "title": f"Available Book {idx}",
        "author": "Author",
        "isbn": f"AVL-POS-{idx:04d}",
        "category": "Fiction",
        "available_copies": copies,
    })
    book_id = res.json()["id"]

    avail = client.get(f"/books/{book_id}/availability")
    assert avail.status_code == 200
    data = avail.json()
    assert data["available_copies"] == copies
    assert data["is_available"] is True


# 2. Books with 0 copies report is_available=False (40 tests)
@pytest.mark.parametrize(
    "idx",
    range(40),
    ids=[f"avail_zero_{i:03d}" for i in range(40)],
)
def test_availability_zero_copies(client, idx):
    res = client.post("/books/", json={
        "title": f"Zero Book {idx}",
        "author": "Author",
        "isbn": f"AVL-ZERO-{idx:04d}",
        "category": "Reference",
        "available_copies": 0,
    })
    book_id = res.json()["id"]

    avail = client.get(f"/books/{book_id}/availability")
    assert avail.status_code == 200
    data = avail.json()
    assert data["available_copies"] == 0
    assert data["is_available"] is False


# 3. Check availability of nonexistent book returns 404 (30 tests)
@pytest.mark.parametrize(
    "idx, missing_id",
    [
        (i, 92000 + i)
        for i in range(30)
    ],
    ids=[f"avail_not_found_{i:03d}" for i in range(30)],
)
def test_availability_not_found(client, idx, missing_id):
    res = client.get(f"/books/{missing_id}/availability")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# 4. Book availability after return operation (18 tests)
@pytest.mark.parametrize(
    "idx",
    range(18),
    ids=[f"avail_after_return_{i:03d}" for i in range(18)],
)
def test_availability_after_return(client, db_session, idx):
    book = crud.create_book(db_session, schemas.BookCreate(
        title=f"Return Avail Book {idx}", author="Author", isbn=f"AVL-RET-{idx:04d}",
        category="Tech", available_copies=1
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name=f"Reader {idx}", email=f"reader_{idx:04d}@test.com", phone="12345"
    ))
    borrow = crud.create_borrowing(
        db_session, book_id=book.id, member_id=member.id,
        borrow_date="2026-01-01", due_date="2026-01-15"
    )

    client.post("/return/", json={"borrow_id": borrow.id})

    avail = client.get(f"/books/{book.id}/availability")
    assert avail.status_code == 200
    assert avail.json()["available_copies"] == 2
    assert avail.json()["is_available"] is True
