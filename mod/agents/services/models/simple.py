from langchain_openai.chat_models.base import ChatOpenAI
import uuid
import json
import asyncio
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain.tools import tool
from typing import Iterable, cast
from langgraph.checkpoint.postgres import PostgresSaver


from mod.agents.services.models.base import Message
from core.config import settings


def get_api_key() -> str:
    api_key = settings.AI_API_KEY
    if api_key == None:
        raise ValueError("no api key")
    return api_key


# 系统提示
SYSTEM_PROMPT = """
你是一个富有智慧的助手，擅长使用费曼学习法。
"""


class Context(BaseModel):
    pass


# 模型配置
model = ChatOpenAI(
    model=settings.AI_MODEL,
    api_key=get_api_key,
    base_url=settings.AI_BASE_URL,
    timeout=800,
    max_retries=3,
)


# 工具
@tool
def get_weather(location: str) -> str:
    """
    用于请求某个地点的天气

    Args:
        location: 需要询问的地点名称

    Return:
        str: 这是对该地点的天气描述
    """
    return "warm"


# 响应格式
class ResponseFormat(BaseModel):
    punny_response: str


# 长期记忆与代理
with PostgresSaver.from_conn_string(settings.DATABASE_URI) as checkpointer:
    checkpointer.setup()
    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        context_schema=Context,
        tools=[get_weather],
        # response_format=ResponseFormat,
        checkpointer=checkpointer,
    )



async def generate_stream_agent_response(context: Iterable[Message], session_id: uuid.UUID):
    msgs = [{
        "role": item.role.value, "content": item.content
    } for item in context]

    try:
        for token, _metadata in agent.stream({"messages": msgs}, stream_mode="messages", config={"configurable": {"thread_id": session_id}}): # type: ignore
            for block in token.content_blocks: # type: ignore
                if block["type"] == "text":
                    content = block["text"]

                    json_data = {"content": content}

                    yield f"data: {json.dumps(json_data)}\n\n"
                    await asyncio.sleep(0.1)
    finally:
        yield "data: [END]\n\n"
