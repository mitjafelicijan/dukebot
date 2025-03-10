from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
async def default_handler(request: Request):
    return JSONResponse(content={
        "message": "Texas Knights Duke Bot",
    }, status_code=200)
