from exceptions.handlers import register_exception_handlers
from fastapi import APIRouter, FastAPI
from routes import auth, users

app = FastAPI(title="Seans API")
register_exception_handlers(app)

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router)
api_v1.include_router(users.router)
app.include_router(api_v1)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
