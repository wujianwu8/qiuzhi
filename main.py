from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

from agent import chat, clear_history


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="QAgent", lifespan=lifespan)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")

    reply = chat(req.session_id, req.message)
    return ChatResponse(session_id=req.session_id, reply=reply)


@app.delete("/chat/{session_id}")
def clear_session(session_id: str):
    clear_history(session_id)
    return {"message": f"会话 {session_id} 的记忆已清除"}
