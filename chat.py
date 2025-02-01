import json
import uuid
import asyncio
import threading
import datetime

from pydantic import BaseModel
from queue import Queue

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

class AskModel(BaseModel):
    user_prompt: str
    system_prompt: str

def llm_wrapper(x_key, user_prompt, system_prompt, app):
    question = f"{user_prompt} {system_prompt}"
    response = app.query_engine.query(question)
    app.message_queues[x_key].put_nowait({ "user_prompt": user_prompt, "system_prompt": system_prompt, "answer": response })

@router.get("/", response_class=HTMLResponse)
async def default_handler(request: Request):
    return request.app.templates.TemplateResponse(
        request=request, name="chat.html", context={}
    )

# Route that in threaded way performs a search on the vector database / LLM.
@router.post("/ask")
async def ask_handler(payload: AskModel, request: Request):
    if "X-Key" not in request.headers:
        raise HTTPException(status_code=400, detail="X-Key header not found")

    x_key = request.headers["X-Key"]
    
    # Creates a new Queue for this X-Key.
    if x_key not in request.app.message_queues:
        request.app.message_queues[x_key] = Queue(maxsize = request.app.MAX_QUEUE_CAPACITY)

    # Start communication with LLM in a separate thread.
    thread = threading.Thread(target=llm_wrapper, args=(x_key, payload.user_prompt, payload.system_prompt, request.app))
    thread.start()

    # Notify client that the task has been created and LLM has been pinged.
    return JSONResponse(content={
        "message": "Task started", 
        "user_prompt": payload.user_prompt,
        "system_prompt": payload.system_prompt,
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
                        "user_prompt": str(queue_item["user_prompt"]),
                        "system_prompt": str(queue_item["system_prompt"]),
                        "answer": str(queue_item["answer"])
                    })

                    # Store the conversation to a local database.
                    request.app.db["connection"].execute("INSERT INTO questions(x_key,created_at,user_prompt,system_prompt,answer) VALUES(?,?,?,?,?)", (
                        x_key, datetime.datetime.now(), str(queue_item["user_prompt"]), str(queue_item["system_prompt"]), str(queue_item["answer"]),
                    ))
                    request.app.db["connection"].commit()
                    
                    yield f"event: message\ndata: {payload}\n\n"
            await asyncio.sleep(0.2)

    return StreamingResponse(event_stream(x_key, request), media_type="text/event-stream")
