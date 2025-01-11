from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
async def default_handler(request: Request):
    return JSONResponse(content={
        "message": "AI Assistant",
    }, status_code=200)

# TODO: Add check for SQLite and Index.
@router.get("/healthcheck")
async def default_handler(request: Request):
    return JSONResponse(content={
        "message": "AI Assistant",
    }, status_code=200)
