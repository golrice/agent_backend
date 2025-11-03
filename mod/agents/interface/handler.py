from typing import Annotated, Any, Dict
import uuid

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import StreamingResponse

from api.deps import SessionDep
from mod.agents.models.dto import GenerateAsk, GenerateBlock, StreamID
from mod.agents.services.models.base import Message, Role, agent_client
from mod.agents.services.models.simple import generate_stream_agent_response
from mod.agents.services.stream import generate_ai_stream


router = APIRouter(prefix="/agents", tags=["agents"])

data: Dict[uuid.UUID, GenerateAsk] = {}

@router.post("/generate/{session_id}", response_model=GenerateBlock)
def generate_content(session: SessionDep, session_id: uuid.UUID, ask: GenerateAsk) -> GenerateBlock:
    return GenerateBlock(msg=ask.msg)

@router.post("/generate/stream_on/{session_id}", response_model=StreamID)
def stream_on(session: SessionDep, session_id: uuid.UUID, ask: GenerateAsk) -> StreamID:
    stream_id = StreamID()

    data[stream_id.id] = ask

    return stream_id

@router.get("/generate/stream/{session_id}/{stream_id}", response_model=None)
async def generate_stream_content(session: SessionDep, session_id: uuid.UUID, stream_id: uuid.UUID) -> StreamingResponse:
    async with agent_client.lock:
        ask = data[stream_id]
        msg = Message(role=Role.user, content=ask.msg)

        # return StreamingResponse(agent_client.generate_stream_response([msg]), media_type="text/event-stream")
        return StreamingResponse(generate_stream_agent_response([msg], session_id), media_type="text/event-stream")
