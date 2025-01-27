import json

from database import get_db
from fastapi.testclient import TestClient
from main import app
import pytest


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user():
    return {
        "id": "testuser",
        "password": "Test1234!",  # 8자리 이상, 영문+숫자 포함
        "name": "테스트",
        "gender": "M",
        "age": 25,
    }


def test_signup(client, test_user):
    # 회원가입 테스트
    print("\nTest user data:", json.dumps(test_user, ensure_ascii=False))  # 실제 JSON 데이터 확인
    response = client.post("/user/signup", json=test_user, headers={"Content-Type": "application/json"})
    print("Response status:", response.status_code)
    print("Response body:", response.json())

    assert response.status_code == 200
    assert response.json() == {"message": "회원가입이 완료되었습니다"}

    # 중복 회원가입 테스트
    response = client.post("/user/signup", json=test_user)
    assert response.status_code == 409
    assert response.json()["detail"] == "이미 존재하는 아이디입니다"


def test_login(client, test_user):
    # 회원가입
    client.post("/user/signup", json=test_user)

    # 올바른 로그인 테스트
    login_data = {"id": test_user["id"], "password": test_user["password"]}
    response = client.post("/user/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.cookies.get("access_token") is not None

    # 잘못된 비밀번호 테스트
    wrong_login = {"id": test_user["id"], "password": "wrongpassword"}
    response = client.post("/user/login", json=wrong_login)
    assert response.status_code == 401
    assert response.json()["detail"] == "아이디 또는 비밀번호가 일치하지 않습니다"


def test_logout(client, test_user):
    # 로그아웃 테스트 (로그인하지 않은 상태)
    response = client.post("/user/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "이미 로그아웃된 상태입니다"

    # 로그인 후 로그아웃 테스트
    client.post("/user/signup", json=test_user)
    login_response = client.post("/user/login", json={"id": test_user["id"], "password": test_user["password"]})

    cookies = login_response.cookies
    response = client.post("/user/logout", cookies=cookies)
    assert response.status_code == 200
    assert response.json() == {"message": "로그아웃되었습니다"}
