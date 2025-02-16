from models import Comment, Novel, NovelShorts, User
import pytest


@pytest.fixture
def test_comment(db_session, test_shorts, test_user_in_db):
    comment = Comment(
        novel_shorts_no=test_shorts.no,
        user_no=test_user_in_db.no,
        content="테스트 댓글입니다",
        like=0,
    )
    db_session.add(comment)
    db_session.commit()
    return comment


@pytest.fixture
def test_user_in_db(db_session):
    user = User(
        id="testuser",
        password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGR9z6B5Lmy",  # Test1234!
        name="테스트유저",
        gender="M",
        age=20,
    )
    db_session.add(user)
    db_session.commit()
    return user


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
        subtitle="테스트 부제목",
        content="테스트 내용",
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


@pytest.fixture
def auth_headers(client):
    # 로그인하여 토큰 얻기
    login_data = {"id": "testuser", "password": "Test1234!"}
    response = client.post("/user/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_comments(client, test_comment):
    response = client.get(f"/shorts/{test_comment.novel_shorts_no}/comments")
    assert response.status_code == 200
    assert response.json()["success"] is True
    comments = response.json()["comments"]
    assert len(comments) == 1
    assert comments[0]["content"] == "테스트 댓글입니다"
    assert comments[0]["user_name"] == "테스트유저"


def test_create_comment(client, test_shorts, auth_headers):
    comment_data = {
        "novel_shorts_no": test_shorts.no,
        "content": "새로운 댓글입니다",
    }
    response = client.post("/shorts/comment", json=comment_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "댓글이 작성되었습니다"


def test_update_comment(client, test_comment, auth_headers):
    update_data = {"content": "수정된 댓글입니다"}
    response = client.put(
        f"/shorts/comment/{test_comment.no}",
        json=update_data,
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "댓글이 수정되었습니다"


def test_delete_comment(client, test_comment, auth_headers):
    response = client.delete(
        f"/shorts/comment/{test_comment.no}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "댓글이 삭제되었습니다"


def test_like_comment(client, test_comment, auth_headers):
    # 좋아요 테스트
    response = client.post(
        f"/shorts/comment/{test_comment.no}/like",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "댓글에 좋아요를 눌렀습니다"

    # 중복 좋아요 테스트
    response = client.post(
        f"/shorts/comment/{test_comment.no}/like",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 좋아요를 눌렀습니다"


def test_unlike_comment(client, test_comment, auth_headers):
    # 먼저 좋아요를 누름
    client.post(f"/shorts/comment/{test_comment.no}/like", headers=auth_headers)

    # 좋아요 취소 테스트
    response = client.delete(
        f"/shorts/comment/{test_comment.no}/like",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "댓글 좋아요를 취소했습니다"

    # 이미 취소된 좋아요 다시 취소 테스트
    response = client.delete(
        f"/shorts/comment/{test_comment.no}/like",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "좋아요 기록이 없습니다"
