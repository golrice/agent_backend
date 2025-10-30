from mod.user.models.dto import UserPublic
from sqlmodel import Field
import uuid

# Database model, database table inferred from class name
class User(UserPublic, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
