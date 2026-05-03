from fastapi import FastAPI

from app.api.wallet import router as wallet_router
from app.db import Base, engine

app = FastAPI(title="Wallet API", version="1.0.0")

app.include_router(wallet_router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
