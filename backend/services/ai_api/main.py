import logging

from fastapi import FastAPI

from shared.logging import configure_logging
from shared.logging.fastapi import RequestContextMiddleware

from routes import router

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(RequestContextMiddleware)
app.include_router(router)


@app.get("/")
def read_root():
    return {"Service": "AI API"}


@app.get("/health")
def health():
    return {"status": "ok"}
