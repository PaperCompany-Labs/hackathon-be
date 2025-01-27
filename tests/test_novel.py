from models import Novel, NovelShorts
import pytest


@pytest.fixture
def test_novel(db_session):
    novel = Novel(
        source_platform_type=1,
        source_id=1,
        source_url="http://test.com",
        title="테스트 소설",
        author="테스트 작가",
        description="테스트 설명",
        genres=[1, 2],
        cover_image="test.jpg",
        chapters=10,
        views=100,
        recommends=50,
    )
    db_session.add(novel)
    db_session.commit()
    return novel


@pytest.fixture
def test_shorts(db_session, test_novel):
    shorts = NovelShorts(
        novel_no=test_novel.no,
        form_type=1,
        content="테스트 내용",
        image="test.jpg",
        music="test.mp3",
        likes=0,
        saves=0,
        comments=0,
    )
    db_session.add(shorts)
    db_session.commit()
    return shorts


def test_read_posts(client, test_shorts):
    response = client.get("/shorts")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "테스트 소설"


def test_read_post(client, test_shorts):
    response = client.get(f"/shorts/{test_shorts.no}")
    assert response.status_code == 200
    assert response.json()["title"] == "테스트 소설"
    assert response.json()["content"] == "테스트 내용"


def test_like_shorts_unauthorized(client, test_shorts):
    response = client.post(f"/shorts/{test_shorts.no}/like")
    assert response.status_code == 401
    assert response.json()["detail"] == "로그인이 필요한 서비스입니다"


def test_like_shorts(client, test_shorts, test_user):
    # 로그인
    client.post("/user/signup", json=test_user)
    login_response = client.post("/user/login", json={"id": test_user["id"], "password": test_user["password"]})
    cookies = login_response.cookies

    # 좋아요 테스트
    response = client.post(f"/shorts/{test_shorts.no}/like", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["likes"] == 1

    # 좋아요 취소 테스트
    response = client.delete(f"/shorts/{test_shorts.no}/like", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["likes"] == 0


def test_save_shorts(client, test_shorts, test_user):
    # 로그인
    client.post("/user/signup", json=test_user)
    login_response = client.post("/user/login", json={"id": test_user["id"], "password": test_user["password"]})
    cookies = login_response.cookies

    # 저장 테스트
    response = client.post(f"/shorts/{test_shorts.no}/save", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["saves"] == 1

    # 중복 저장 테스트
    response = client.post(f"/shorts/{test_shorts.no}/save", cookies=cookies)
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 저장된 게시물입니다"

    # 저장 취소 테스트
    response = client.delete(f"/shorts/{test_shorts.no}/save", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["saves"] == 0

    # 이미 취소된 저장 다시 취소 테스트
    response = client.delete(f"/shorts/{test_shorts.no}/save", cookies=cookies)
    assert response.status_code == 400
    assert response.json()["detail"] == "저장되지 않은 게시물입니다"
