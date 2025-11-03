import uuid
from pydantic import BaseModel, Field
from sqlmodel import SQLModel
from mod.agents.models.base import GenerateBase


class GenerateAsk(GenerateBase):
    pass

class GenerateBlock(SQLModel):
    msg: str

class StreamID(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
