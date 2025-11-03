import enum
import asyncio
from pydantic import BaseModel, Field, model_validator, PrivateAttr, ConfigDict
from typing_extensions import Self
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
from typing import Iterable, List, Optional, Dict, cast, Any
from core.config import settings
import json

from mod.agents.services.stream import generate_ai_stream

class Role(enum.Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class AgentClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: str
    base_url: str
    api_key: Optional[str] = None

    client: Optional[OpenAI] = None

    _lock: asyncio.Lock = PrivateAttr()

    def model_post_init(self, __context: Any):
        self.api_key = settings.AI_API_KEY
        self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
        self._lock = asyncio.Lock()

    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    @model_validator(mode="after")
    def _ensure_valid_api_key(self) -> Self:
        if self.api_key == None:
            raise ValueError("fail to get API_KEY")

        return self

    async def generate_stream_response(self, context: Iterable[Message]):
        assert self.client, "client is not initialized"

        print(f"context: {list(context)}")

        msgs = cast(Iterable[ChatCompletionMessageParam], [{
            "role": item.role.value, "content": item.content
        } for item in context])

        try:
            for block in self.client.chat.completions.create(model=self.model, messages=msgs, stream=True):
                res = block.model_dump()
                content = res["choices"][0]["delta"]["content"]

                json_data = {"content": content}

                yield f"data: {json.dumps(json_data)}\n\n"
                await asyncio.sleep(0.1)
        finally:
            yield "data: [END]\n\n"

agent_client = AgentClient(model=settings.AI_MODEL, base_url=settings.AI_BASE_URL)
