import pytest
from app import crud, schemas


# 1. Successful book creation (100 tests)
@pytest.mark.parametrize(
    "idx, title, author, isbn, category, copies",
    [
        (i, f"Book Title {i}", f"Author {i}", f"978-0-100{i:04d}", f"Category_{i % 10}", (i % 10) + 1)
        for i in range(100)
    ],
    ids=[f"book_create_success_{i:03d}" for i in range(100)],
)
def test_create_book_success(client, idx, title, author, isbn, category, copies):
    payload = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "category": category,
        "available_copies": copies,
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == title
    assert data["author"] == author
    assert data["isbn"] == isbn
    assert data["category"] == category
    assert data["available_copies"] == copies
    assert "id" in data


# 2. Boundary and category variations (80 tests)
@pytest.mark.parametrize(
    "idx, title_len, author_len, copies",
    [
        (i, (i % 20) + 2, (i % 15) + 2, i % 50)
        for i in range(80)
    ],
    ids=[f"book_create_boundary_{i:03d}" for i in range(80)],
)
def test_create_book_boundary_and_categories(client, idx, title_len, author_len, copies):
    payload = {
        "title": "T" * title_len,
        "author": "A" * author_len,
        "isbn": f"ISBN-BND-{idx:04d}",
        "category": "General",
        "available_copies": copies,
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    assert response.json()["available_copies"] == copies


# 3. Duplicate ISBN rejection (40 tests)
@pytest.mark.parametrize(
    "idx",
    range(40),
    ids=[f"book_duplicate_isbn_{i:03d}" for i in range(40)],
)
def test_create_book_duplicate_isbn(client, idx):
    isbn = f"978-DUP-{idx:04d}"
    payload1 = {
        "title": f"Original Book {idx}",
        "author": "Author One",
        "isbn": isbn,
        "category": "Fiction",
        "available_copies": 3,
    }
    res1 = client.post("/books/", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "title": f"Duplicate Book {idx}",
        "author": "Author Two",
        "isbn": isbn,
        "category": "SciFi",
        "available_copies": 1,
    }
    res2 = client.post("/books/", json=payload2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


# 4. Invalid payloads / missing fields (30 tests)
@pytest.mark.parametrize(
    "idx, payload",
    [
        (i, {"title": "", "author": "Valid", "isbn": f"INV-{i}", "category": "Cat"}) if i < 10
        else (i, {"title": f"Book {i}", "author": "", "isbn": f"INV-{i}", "category": "Cat"}) if i < 20
        else (i, {"title": f"Book {i}", "author": "Valid", "isbn": f"INV-{i}", "category": "Cat", "available_copies": -1})
        for i in range(30)
    ],
    ids=[f"book_invalid_payload_{i:03d}" for i in range(30)],
)
def test_create_book_invalid_payload(client, idx, payload):
    response = client.post("/books/", json=payload)
    assert response.status_code == 422


# 5. View all books & pagination (50 tests)
@pytest.mark.parametrize(
    "idx, skip, limit",
    [
        (i, i % 5, (i % 10) + 1)
        for i in range(50)
    ],
    ids=[f"book_list_pagination_{i:03d}" for i in range(50)],
)
def test_view_all_books_pagination(client, idx, skip, limit):
    # Pre-populate 3 books
    for b in range(3):
        client.post("/books/", json={
            "title": f"List Book {idx}_{b}",
            "author": "Author",
            "isbn": f"LIST-{idx:03d}-{b}",
            "category": "Tech",
            "available_copies": 2,
        })
    response = client.get(f"/books/?skip={skip}&limit={limit}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 6. Search book by ID - found (50 tests)
@pytest.mark.parametrize(
    "idx",
    range(50),
    ids=[f"book_search_found_{i:03d}" for i in range(50)],
)
def test_search_book_by_id_found(client, idx):
    res = client.post("/books/", json={
        "title": f"Search Target {idx}",
        "author": f"Author {idx}",
        "isbn": f"SRCH-{idx:04d}",
        "category": "History",
        "available_copies": 5,
    })
    book_id = res.json()["id"]
    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == f"Search Target {idx}"


# 7. Search book by ID - not found (40 tests)
@pytest.mark.parametrize(
    "idx, missing_id",
    [
        (i, 90000 + i)
        for i in range(40)
    ],
    ids=[f"book_search_not_found_{i:03d}" for i in range(40)],
)
def test_search_book_by_id_not_found(client, idx, missing_id):
    res = client.get(f"/books/{missing_id}")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# 8. Update book details - success (60 tests)
@pytest.mark.parametrize(
    "idx, new_title, new_copies",
    [
        (i, f"Updated Title {i}", (i % 15) + 1)
        for i in range(60)
    ],
    ids=[f"book_update_success_{i:03d}" for i in range(60)],
)
def test_update_book_success(client, idx, new_title, new_copies):
    res = client.post("/books/", json={
        "title": f"Initial Title {idx}",
        "author": "Initial Author",
        "isbn": f"UPD-{idx:04d}",
        "category": "Drama",
        "available_copies": 2,
    })
    book_id = res.json()["id"]

    update_res = client.put(f"/books/{book_id}", json={
        "title": new_title,
        "available_copies": new_copies,
    })
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["title"] == new_title
    assert data["available_copies"] == new_copies
    assert data["author"] == "Initial Author"


# 9. Update book details - errors (40 tests)
@pytest.mark.parametrize(
    "idx",
    range(40),
    ids=[f"book_update_error_{i:03d}" for i in range(40)],
)
def test_update_book_errors(client, idx):
    if idx < 20:
        # Nonexistent book ID
        res = client.put(f"/books/{80000 + idx}", json={"title": "New"})
        assert res.status_code == 404
    else:
        # Duplicate ISBN update
        r1 = client.post("/books/", json={"title": "A", "author": "A", "isbn": f"U-DUP1-{idx}", "category": "C", "available_copies": 1})
        r2 = client.post("/books/", json={"title": "B", "author": "B", "isbn": f"U-DUP2-{idx}", "category": "C", "available_copies": 1})
        b2_id = r2.json()["id"]
        res = client.put(f"/books/{b2_id}", json={"isbn": f"U-DUP1-{idx}"})
        assert res.status_code == 400


# 10. Delete book - success, not found, active borrow blocked (60 tests)
@pytest.mark.parametrize(
    "idx",
    range(60),
    ids=[f"book_delete_{i:03d}" for i in range(60)],
)
def test_delete_book(client, db_session, idx):
    if idx < 30:
        # Successful deletion
        res = client.post("/books/", json={
            "title": f"Delete Book {idx}",
            "author": "Author",
            "isbn": f"DEL-{idx:04d}",
            "category": "Category",
            "available_copies": 1,
        })
        book_id = res.json()["id"]
        del_res = client.delete(f"/books/{book_id}")
        assert del_res.status_code == 200
        # Verify book no longer exists
        assert client.get(f"/books/{book_id}").status_code == 404
    elif idx < 45:
        # Delete non-existent book
        del_res = client.delete(f"/books/{70000 + idx}")
        assert del_res.status_code == 404
    else:
        # Prevent deletion when book has active borrowing record
        b_res = client.post("/books/", json={
            "title": f"Active Borrow Book {idx}",
            "author": "Author",
            "isbn": f"ACT-DEL-{idx:04d}",
            "category": "Category",
            "available_copies": 2,
        })
        book_id = b_res.json()["id"]
        m_res = client.post("/members/", json={
            "name": f"Borrower {idx}",
            "email": f"borrower{idx}@lib.org",
            "phone": "555-0199",
        })
        member_id = m_res.json()["id"]
        # Create active borrowing directly
        crud.create_borrowing(db_session, book_id=book_id, member_id=member_id, borrow_date="2026-01-01", due_date="2026-01-15")

        del_res = client.delete(f"/books/{book_id}")
        assert del_res.status_code == 400
        assert "Cannot delete book with active borrowing records" in del_res.json()["detail"]
