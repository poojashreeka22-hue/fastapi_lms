import pytest
from client import library_cli
from app import crud, schemas


class ClientSessionAdapter:
    """Routes CLI HTTP calls directly into the FastAPI test client."""
    def __init__(self, test_client):
        self.test_client = test_client

    def post(self, url, json=None, **kwargs):
        path = url.replace("http://127.0.0.1:8000", "")
        return self.test_client.post(path, json=json, **kwargs)

    def get(self, url, **kwargs):
        path = url.replace("http://127.0.0.1:8000", "")
        return self.test_client.get(path, **kwargs)

    def put(self, url, json=None, **kwargs):
        path = url.replace("http://127.0.0.1:8000", "")
        return self.test_client.put(path, json=json, **kwargs)

    def delete(self, url, **kwargs):
        path = url.replace("http://127.0.0.1:8000", "")
        return self.test_client.delete(path, **kwargs)


@pytest.fixture
def cli_session(client):
    return ClientSessionAdapter(client)


# =====================================================================
# THE 1 TEST IN THIS FILE THAT FAILS INITIALLY DUE TO THE BORROWING BUG
# =====================================================================

def test_cli_borrow_book_decrements_available_copies(cli_session):
    """CLI operation: Borrowing a book via CLI must decrease available copies by one."""
    book = library_cli.add_book(
        title="CLI Book Copy Test",
        author="Author",
        isbn="ISBN-CLI-FAIL-001",
        category="Tech",
        available_copies=4,
        session=cli_session,
    )
    member = library_cli.register_member(
        name="CLI User",
        email="cli_fail@test.com",
        phone="555-4321",
        session=cli_session,
    )

    library_cli.borrow_book(book["id"], member["id"], session=cli_session)

    # Inquire about the book after borrowing
    updated_book = library_cli.search_book_by_id(book["id"], session=cli_session)
    # Under the bug, available_copies is 5 instead of 3!
    assert updated_book["available_copies"] == 3, (
        f"Expected available_copies to decrease from 4 to 3, but got {updated_book['available_copies']}"
    )


# =====================================================================
# THE REMAINING 99 TESTS IN THIS FILE (ALL PASS)
# =====================================================================

# 1. CLI Add Book (15 tests)
@pytest.mark.parametrize(
    "idx",
    range(15),
    ids=[f"cli_add_book_{i:03d}" for i in range(15)],
)
def test_cli_add_book(cli_session, idx):
    book = library_cli.add_book(
        title=f"CLI Book {idx}",
        author="CLI Author",
        isbn=f"CLI-BK-{idx:04d}",
        category="Tech",
        available_copies=2,
        session=cli_session,
    )
    assert book["title"] == f"CLI Book {idx}"
    assert book["available_copies"] == 2


# 2. CLI View All Books (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_view_all_books_{i:03d}" for i in range(10)],
)
def test_cli_view_all_books(cli_session, idx):
    library_cli.add_book(
        title=f"Viewable Book {idx}",
        author="Author",
        isbn=f"CLI-VIEW-{idx:04d}",
        category="Fiction",
        available_copies=1,
        session=cli_session,
    )
    books = library_cli.view_all_books(session=cli_session)
    assert isinstance(books, list)
    assert len(books) >= 1


# 3. CLI Search Book by ID (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_search_book_{i:03d}" for i in range(10)],
)
def test_cli_search_book_by_id(cli_session, idx):
    added = library_cli.add_book(
        title=f"Findable {idx}",
        author="Author",
        isbn=f"CLI-FND-{idx:04d}",
        category="Reference",
        available_copies=3,
        session=cli_session,
    )
    found = library_cli.search_book_by_id(added["id"], session=cli_session)
    assert found["id"] == added["id"]
    assert found["title"] == f"Findable {idx}"


# 4. CLI Update Book (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_update_book_{i:03d}" for i in range(10)],
)
def test_cli_update_book(cli_session, idx):
    added = library_cli.add_book(
        title=f"Old Title {idx}",
        author="Old Author",
        isbn=f"CLI-UPD-{idx:04d}",
        category="General",
        available_copies=1,
        session=cli_session,
    )
    updated = library_cli.update_book(
        added["id"],
        title=f"New Title {idx}",
        available_copies=5,
        session=cli_session,
    )
    assert updated["title"] == f"New Title {idx}"
    assert updated["available_copies"] == 5


# 5. CLI Delete Book (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_delete_book_{i:03d}" for i in range(10)],
)
def test_cli_delete_book(cli_session, idx):
    added = library_cli.add_book(
        title=f"Delete Target {idx}",
        author="Author",
        isbn=f"CLI-DEL-{idx:04d}",
        category="Temp",
        available_copies=1,
        session=cli_session,
    )
    res = library_cli.delete_book(added["id"], session=cli_session)
    assert "deleted successfully" in res["message"]


# 6. CLI Register Member (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_register_member_{i:03d}" for i in range(10)],
)
def test_cli_register_member(cli_session, idx):
    member = library_cli.register_member(
        name=f"CLI Member {idx}",
        email=f"climem_{idx:04d}@domain.test",
        phone="555-7890",
        session=cli_session,
    )
    assert member["name"] == f"CLI Member {idx}"
    assert member["email"] == f"climem_{idx:04d}@domain.test"


# 7. CLI View All Members (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_view_all_members_{i:03d}" for i in range(10)],
)
def test_cli_view_all_members(cli_session, idx):
    library_cli.register_member(
        name=f"Member List {idx}",
        email=f"memlist_{idx:04d}@domain.test",
        phone="555-1111",
        session=cli_session,
    )
    members = library_cli.view_all_members(session=cli_session)
    assert isinstance(members, list)
    assert len(members) >= 1


# 8. CLI Borrow Book Success (10 tests)
@pytest.mark.parametrize(
    "idx",
    range(10),
    ids=[f"cli_borrow_success_{i:03d}" for i in range(10)],
)
def test_cli_borrow_book_success(cli_session, idx):
    b = library_cli.add_book(
        title=f"Borrow Book {idx}",
        author="Author",
        isbn=f"CLI-BRW-{idx:04d}",
        category="Reading",
        available_copies=5,
        session=cli_session,
    )
    m = library_cli.register_member(
        name=f"Borrower {idx}",
        email=f"borrower_{idx:04d}@domain.test",
        phone="555-2222",
        session=cli_session,
    )
    borrow = library_cli.borrow_book(b["id"], m["id"], session=cli_session)
    assert borrow["status"] == "borrowed"
    assert "id" in borrow


# 9. CLI Return Book (8 tests)
@pytest.mark.parametrize(
    "idx",
    range(8),
    ids=[f"cli_return_book_{i:03d}" for i in range(8)],
)
def test_cli_return_book(cli_session, db_session, idx):
    book = crud.create_book(db_session, schemas.BookCreate(
        title=f"CLI Return {idx}", author="Author", isbn=f"CLI-RET-{idx:04d}",
        category="General", available_copies=2
    ))
    member = crud.create_member(db_session, schemas.MemberCreate(
        name=f"Returner {idx}", email=f"cliret_{idx:04d}@test.org", phone="555-3333"
    ))
    borrow = crud.create_borrowing(
        db_session, book_id=book.id, member_id=member.id,
        borrow_date="2026-01-01", due_date="2026-01-15"
    )
    res = library_cli.return_book(borrow.id, session=cli_session)
    assert res["status"] == "returned"
    assert res["return_date"] is not None


# 10. CLI Check Book Availability (6 tests)
@pytest.mark.parametrize(
    "idx",
    range(6),
    ids=[f"cli_check_avail_{i:03d}" for i in range(6)],
)
def test_cli_check_book_availability(cli_session, idx):
    book = library_cli.add_book(
        title=f"Check Avail {idx}",
        author="Author",
        isbn=f"CLI-AVL-{idx:04d}",
        category="Tech",
        available_copies=3,
        session=cli_session,
    )
    avail = library_cli.check_book_availability(book["id"], session=cli_session)
    assert avail["is_available"] is True
    assert avail["available_copies"] == 3
