from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware, AppExceptionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.debug)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AppExceptionMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
