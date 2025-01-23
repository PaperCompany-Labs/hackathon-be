from models import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from user.user_schema import NewUserForm


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
        user_name=new_user.name,
        id=new_user.id,
        password=pwd_context.hash(new_user.password),
        name=new_user.name,
        gender=new_user.gender,
        age=new_user.age,
    )
    db.add(user)
    db.commit()
