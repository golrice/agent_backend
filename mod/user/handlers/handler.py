import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from core.config import settings
from core.security import get_password_hash, verify_password

from utils import generate_new_account_email, send_email
from mod.user.models.dto import UserPublic, UserCreate, UsersPublic, UserUpdateMe, UserRegister, UserUpdate
from mod.user.models.dao import User
import mod.user.services.crud as user_crud
from mod.login.models.dto import Message, UpdatePassword


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = user_crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = user_crud.create_user(session=session, user_create=user_create)
    return user
