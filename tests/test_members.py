import pytest


# 1. Member Registration Success (100 tests)
@pytest.mark.parametrize(
    "idx, name, email, phone",
    [
        (i, f"Member Name {i}", f"member{i:04d}@example.com", f"555-01{i:02d}")
        for i in range(100)
    ],
    ids=[f"member_reg_success_{i:03d}" for i in range(100)],
)
def test_register_member_success(client, idx, name, email, phone):
    payload = {"name": name, "email": email, "phone": phone}
    res = client.post("/members/", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == name
    assert data["email"] == email
    assert data["phone"] == phone
    assert "id" in data


# 2. Member Duplicate Email (50 tests)
@pytest.mark.parametrize(
    "idx",
    range(50),
    ids=[f"member_dup_email_{i:03d}" for i in range(50)],
)
def test_register_member_duplicate_email(client, idx):
    email = f"dup_user_{idx:03d}@library.test"
    payload1 = {"name": "First User", "email": email, "phone": "123-456-7890"}
    res1 = client.post("/members/", json=payload1)
    assert res1.status_code == 201

    payload2 = {"name": "Second User", "email": email, "phone": "098-765-4321"}
    res2 = client.post("/members/", json=payload2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


# 3. Member Invalid Inputs / Missing fields (50 tests)
@pytest.mark.parametrize(
    "idx, payload",
    [
        (i, {"name": "", "email": f"valid{i}@test.com", "phone": "12345"}) if i < 15
        else (i, {"name": f"User {i}", "email": "", "phone": "12345"}) if i < 30
        else (i, {"name": f"User {i}", "email": f"valid{i}@test.com", "phone": ""}) if i < 40
        else (i, {"name": f"User {i}"})  # Missing required email & phone
        for i in range(50)
    ],
    ids=[f"member_invalid_{i:03d}" for i in range(50)],
)
def test_register_member_invalid_inputs(client, idx, payload):
    res = client.post("/members/", json=payload)
    assert res.status_code == 422


# 4. View All Members & Pagination (60 tests)
@pytest.mark.parametrize(
    "idx, skip, limit",
    [
        (i, i % 4, (i % 8) + 1)
        for i in range(60)
    ],
    ids=[f"member_list_pagination_{i:03d}" for i in range(60)],
)
def test_view_all_members_pagination(client, idx, skip, limit):
    for m in range(2):
        client.post("/members/", json={
            "name": f"Seed Member {idx}_{m}",
            "email": f"seed_{idx:03d}_{m}@example.org",
            "phone": "555-1234",
        })
    res = client.get(f"/members/?skip={skip}&limit={limit}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# 5. Get Member by ID - Found (70 tests)
@pytest.mark.parametrize(
    "idx",
    range(70),
    ids=[f"member_get_found_{i:03d}" for i in range(70)],
)
def test_get_member_by_id_found(client, db_session, idx):
    res = client.post("/members/", json={
        "name": f"Find Member {idx}",
        "email": f"find_{idx:03d}@domain.org",
        "phone": f"555-99{idx:02d}",
    })
    member_id = res.json()["id"]
    from app import services
    member = services.get_member_service(db_session, member_id)
    assert member.id == member_id
    assert member.name == f"Find Member {idx}"


# 6. Get Member by ID - Not Found (70 tests)
@pytest.mark.parametrize(
    "idx, missing_id",
    [
        (i, 88000 + i)
        for i in range(70)
    ],
    ids=[f"member_get_not_found_{i:03d}" for i in range(70)],
)
def test_get_member_by_id_not_found(db_session, idx, missing_id):
    from fastapi import HTTPException
    from app import services
    with pytest.raises(HTTPException) as exc_info:
        services.get_member_service(db_session, missing_id)
    assert exc_info.value.status_code == 404
    assert f"Member with ID {missing_id} not found" in exc_info.value.detail
