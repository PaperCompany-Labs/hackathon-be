from datetime import datetime

from models import User, UserActiveLog
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from user.user_schema import NewUserForm, UserActiveCreate, UserActiveResponse


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, id: str, provider: str = None):
    if provider:
        return db.query(User).filter(User.id == id, User.provider == provider).first()
    else:
        return db.query(User).filter(User.id == id).first()


def create_user(new_user: NewUserForm, db: Session):
    user = User(
        id=new_user.id,
        password=pwd_context.hash(new_user.password),
        name=new_user.name,
        gender=new_user.gender,
        age=new_user.age,
    )
    db.add(user)
    db.commit()


def create_active_log(db: Session, user_no: int, active_data: UserActiveCreate) -> UserActiveResponse:
    try:
        log = UserActiveLog(
            user_no=user_no,
            novel_no=active_data.novel_no,
            comment_no=active_data.comment_no,
            active_type=active_data.active_type,
            acted_date=active_data.acted_date,
            created_date=datetime.now(),
        )

        db.add(log)
        db.commit()

        return UserActiveResponse(success=True, message="활동 로그가 저장되었습니다")
    except Exception as e:
        print(f"Error in create_active_log: {str(e)}")
        db.rollback()
        return UserActiveResponse(success=False, message="활동 로그 저장 중 오류가 발생했습니다")
