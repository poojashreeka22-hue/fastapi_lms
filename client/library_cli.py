import sys
from typing import Optional, Dict, Any, List
import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _get_session(session: Optional[requests.Session] = None) -> Any:
    return session if session is not None else requests


def add_book(
    title: str,
    author: str,
    isbn: str,
    category: str,
    available_copies: int = 1,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    payload = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "category": category,
        "available_copies": int(available_copies),
    }
    client = _get_session(session)
    response = client.post(f"{base_url}/books/", json=payload)
    if response.status_code == 201:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to add book: {error_msg}")


def view_all_books(
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    client = _get_session(session)
    response = client.get(f"{base_url}/books/")
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to fetch books: {error_msg}")


def search_book_by_id(
    book_id: int,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    client = _get_session(session)
    response = client.get(f"{base_url}/books/{book_id}")
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Book with ID {book_id} not found: {error_msg}")


def update_book(
    book_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    isbn: Optional[str] = None,
    category: Optional[str] = None,
    available_copies: Optional[int] = None,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if author is not None:
        payload["author"] = author
    if isbn is not None:
        payload["isbn"] = isbn
    if category is not None:
        payload["category"] = category
    if available_copies is not None:
        payload["available_copies"] = int(available_copies)

    client = _get_session(session)
    response = client.put(f"{base_url}/books/{book_id}", json=payload)
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to update book: {error_msg}")


def delete_book(
    book_id: int,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    client = _get_session(session)
    response = client.delete(f"{base_url}/books/{book_id}")
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to delete book: {error_msg}")


def register_member(
    name: str,
    email: str,
    phone: str,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    payload = {"name": name, "email": email, "phone": phone}
    client = _get_session(session)
    response = client.post(f"{base_url}/members/", json=payload)
    if response.status_code == 201:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to register member: {error_msg}")


def view_all_members(
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    client = _get_session(session)
    response = client.get(f"{base_url}/members/")
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to fetch members: {error_msg}")


def borrow_book(
    book_id: int,
    member_id: int,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    payload = {"book_id": int(book_id), "member_id": int(member_id)}
    client = _get_session(session)
    response = client.post(f"{base_url}/borrow/", json=payload)
    if response.status_code == 201:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to borrow book: {error_msg}")


def return_book(
    borrow_id: int,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    payload = {"borrow_id": int(borrow_id)}
    client = _get_session(session)
    response = client.post(f"{base_url}/return/", json=payload)
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to return book: {error_msg}")


def check_book_availability(
    book_id: int,
    base_url: str = DEFAULT_BASE_URL,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    client = _get_session(session)
    response = client.get(f"{base_url}/books/{book_id}/availability")
    if response.status_code == 200:
        return response.json()
    error_msg = response.json().get("detail", response.text)
    raise RuntimeError(f"Failed to check book availability: {error_msg}")


def interactive_menu(base_url: str = DEFAULT_BASE_URL):
    print("=" * 50)
    print("      LIBRARY MANAGEMENT SYSTEM CLI")
    print("=" * 50)

    while True:
        print("\nPlease select an option:")
        print("1. Add a book")
        print("2. View all books")
        print("3. Search for a book by ID")
        print("4. Update book details")
        print("5. Delete a book")
        print("6. Register a library member")
        print("7. View all members")
        print("8. Borrow a book")
        print("9. Return a borrowed book")
        print("10. Check book availability")
        print("11. Exit")

        choice = input("\nEnter choice (1-11): ").strip()

        try:
            if choice == "1":
                title = input("Enter Title: ").strip()
                author = input("Enter Author: ").strip()
                isbn = input("Enter ISBN: ").strip()
                category = input("Enter Category: ").strip()
                copies = int(input("Enter Available Copies: ").strip() or "1")
                book = add_book(title, author, isbn, category, copies, base_url)
                print(f"[SUCCESS] Book added: {book}")

            elif choice == "2":
                books = view_all_books(base_url)
                print(f"\n--- Books in Library ({len(books)}) ---")
                for b in books:
                    print(
                        f"ID: {b['id']} | Title: {b['title']} | Author: {b['author']} "
                        f"| ISBN: {b['isbn']} | Copies: {b['available_copies']}"
                    )

            elif choice == "3":
                bid = int(input("Enter Book ID: ").strip())
                book = search_book_by_id(bid, base_url)
                print(f"[FOUND] {book}")

            elif choice == "4":
                bid = int(input("Enter Book ID to update: ").strip())
                print("Leave blank to keep existing value.")
                title = input("New Title: ").strip() or None
                author = input("New Author: ").strip() or None
                isbn = input("New ISBN: ").strip() or None
                category = input("New Category: ").strip() or None
                copies_str = input("New Available Copies: ").strip()
                copies = int(copies_str) if copies_str else None
                updated = update_book(
                    bid, title, author, isbn, category, copies, base_url
                )
                print(f"[UPDATED] {updated}")

            elif choice == "5":
                bid = int(input("Enter Book ID to delete: ").strip())
                res = delete_book(bid, base_url)
                print(f"[DELETED] {res}")

            elif choice == "6":
                name = input("Enter Member Name: ").strip()
                email = input("Enter Member Email: ").strip()
                phone = input("Enter Member Phone: ").strip()
                member = register_member(name, email, phone, base_url)
                print(f"[SUCCESS] Member registered: {member}")

            elif choice == "7":
                members = view_all_members(base_url)
                print(f"\n--- Library Members ({len(members)}) ---")
                for m in members:
                    print(
                        f"ID: {m['id']} | Name: {m['name']} | Email: {m['email']} | Phone: {m['phone']}"
                    )

            elif choice == "8":
                bid = int(input("Enter Book ID to borrow: ").strip())
                mid = int(input("Enter Member ID: ").strip())
                borrow = borrow_book(bid, mid, base_url)
                print(f"[BORROWED] Record: {borrow}")

            elif choice == "9":
                brid = int(input("Enter Borrow ID to return: ").strip())
                ret = return_book(brid, base_url)
                print(f"[RETURNED] Record: {ret}")

            elif choice == "10":
                bid = int(input("Enter Book ID to check availability: ").strip())
                avail = check_book_availability(bid, base_url)
                status_str = "Available" if avail["is_available"] else "Unavailable"
                print(
                    f"[AVAILABILITY] Title: '{avail['title']}' | Status: {status_str} | Copies: {avail['available_copies']}"
                )

            elif choice == "11":
                print("Goodbye!")
                sys.exit(0)

            else:
                print("[ERROR] Invalid choice. Please enter a number between 1 and 11.")

        except Exception as e:
            print(f"[ERROR] {e}")


def main():
    interactive_menu()


if __name__ == "__main__":
    main()
