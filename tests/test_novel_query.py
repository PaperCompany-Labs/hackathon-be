from datetime import datetime

from models import Novel, NovelShorts, SourceType
from novel.novel_query import get_post
from novel.novel_schema import PostResponse
from sqlalchemy.orm import Session


def test_get_post_success(db_session: Session):
    # 테스트 데이터 준비
    novel = Novel(
        title="테스트 소설",
        author="테스트 작가",
        description="테스트 설명",
        genres=[1],
        cover_image="test.jpg",
        chapters=10,
        views=100,
        recommends=50,
        created_date=datetime.now(),
        last_uploaded_date=datetime.now(),
        source_type=SourceType.MUNPIA.value,
        source_url="http://test.com",
        source_platform_type=1,
    )

    novel_shorts = NovelShorts(
        novel_no=1, likes=10, saves=5, comments=3, content="테스트 내용", image="test.jpg", music="test.mp3"
    )

    db_session.add(novel)
    db_session.add(novel_shorts)
    db_session.commit()

    # 함수 실행
    result = get_post(post_no=1, db=db_session)

    # 디버깅을 위한 print 문
    print("\n")  # 가독성을 위한 빈 줄
    print("=== 테스트 결과 출력 ===")
    print(f"전체 결과: {result}")
    print(f"타입: {type(result)}")
    print(f"속성 목록: {result.__dict__ if hasattr(result, '__dict__') else 'N/A'}")
    print("=====================")
    print(result)

    # 결과 검증
    assert isinstance(result, PostResponse)
    assert result.no == 1
    assert result.title == "테스트 소설"
    assert result.likes == 10
    assert result.content == "테스트 내용"


def test_get_post_not_found(db_session: Session):
    # 존재하지 않는 게시물 조회
    result = get_post(post_no=999, db=db_session)

    assert isinstance(result, dict)
    assert "error" in result
    assert result["msg"] == "존재하지 않는 번호입니다."


def test_get_post_db_error(db_session: Session):
    # DB 세션을 닫아서 에러 발생시키기
    db_session.close()

    result = get_post(post_no=1, db=db_session)

    print("\n=== DB 에러 테스트 결과 ===")
    print(f"결과: {result}")
    print("==========================")

    assert isinstance(result, dict)
    assert "error" in result
    assert result["msg"] == "존재하지 않는 번호입니다."
