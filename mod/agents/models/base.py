from sqlmodel import SQLModel


class GenerateBase(SQLModel):
    is_user: bool
    msg: str
