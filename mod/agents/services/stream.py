import asyncio

async def generate_ai_stream(q: str):
    for i in range(len(q)):
        yield f"data: {q[i]}\n\n"
        await asyncio.sleep(0.3)

    yield f"data: [END]\n\n"
