import json
import uuid
import asyncio
import threading
import datetime

from pydantic import BaseModel
from queue import Queue

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

router = APIRouter()

class AskModel(BaseModel):
    question: str

def llm_wrapper(x_key, question, app):
    response = app.query_engine.query(question)
    app.message_queues[x_key].put_nowait({ "question": question, "answer": response })

@router.get("/")
async def default_handler(request: Request):
    return {}

# Route that in threaded way performs a search on the vector database / LLM.
@router.post("/ask")
async def ask_handler(payload: AskModel, request: Request):
    if "X-Key" not in request.headers:
        raise HTTPException(status_code=400, detail="X-Key header not found")

    x_key = request.headers["X-Key"]
    
    # Creates a new Queue for this X-Key.
    if x_key not in request.app.message_queues:
        request.app.message_queues[x_key] = Queue(maxsize = request.app.max_queue_capacity)

    # Start communication with LLM in a separate thread.
    thread = threading.Thread(target=llm_wrapper, args=(x_key, payload.question, request.app))
    thread.start()

    # Notify client that the task has been created and LLM has been pinged.
    return JSONResponse(content={
        "message": "Task started", 
        "question": payload.question
    }, status_code=201)

# Route for streaming SSE responses.
@router.get("/stream")
async def stream_handler(request: Request):
    x_key = str(uuid.uuid4())
    async def event_stream(x_key: str, request: Request):
        yield f"event: key\ndata: {x_key}\n\n"
        while True:
            if x_key in request.app.message_queues:
                message_queue = request.app.message_queues[x_key]
                while not message_queue.empty():
                    queue_item = message_queue.get()
                    payload = json.dumps({
                        "question": str(queue_item["question"]),
                        "answer": str(queue_item["answer"])
                    })

                    # Store the conversation to a local database.
                    request.app.db["connection"].execute("INSERT INTO questions(x_key,created_at,question,answer) VALUES(?,?,?,?)", (
                        x_key, datetime.datetime.now(), str(queue_item["question"]), str(queue_item["answer"]),                       
                    ))
                    request.app.db["connection"].commit()
                    
                    yield f"event: message\ndata: {payload}\n\n"
            await asyncio.sleep(0.2)

    return StreamingResponse(event_stream(x_key, request), media_type="text/event-stream")
