import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def default_handler(request: Request):
    cur = request.app.db["cursor"]
    message_limit = 50

    cur.execute("SELECT * FROM questions ORDER BY created_at DESC LIMIT ?", (message_limit,))
    last_questions = cur.fetchall()

    cur.execute("SELECT count(*) FROM questions")
    messages_served = cur.fetchone()
    
    payload = {
        "active_users": len(request.app.message_queues),
        "messages_served": messages_served[0],
        "last_questions": last_questions,
        "message_limit": message_limit,
        "uptime": datetime.datetime.now() - request.app.startup_time,
    }

    return request.app.templates.TemplateResponse(
        request=request, name="statistics.html", context=payload
    )

