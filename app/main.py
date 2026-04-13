from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.engine import close_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_engine()


app = FastAPI(title="Auth API", description="Authentication API for managing users and sessions", lifespan=lifespan)
