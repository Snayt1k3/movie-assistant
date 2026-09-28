from fastapi import FastAPI

app = FastAPI(title="Сеанс API")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
