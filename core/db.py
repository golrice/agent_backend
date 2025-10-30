from sqlmodel import Session, create_engine, select

from core.config import settings
import mod.user.services.crud as user_crud
from mod.user.models.dto import UserCreate
from mod.user.models.dao import User


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def init_db(session: Session) -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_crud.create_user(session=session, user_create=user_in)
