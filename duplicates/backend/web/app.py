import asyncio
import logging.config
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncIterator

from fastapi import FastAPI
from prometheus_client import start_http_server
from starlette.middleware.cors import CORSMiddleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from web.api.v1.router import router as v1_router
from web.api.tech.router import router as tech_router
from web.config.settings import settings
from web.logger import LOGGING_CONFIG, logger
from web.metrics import http_prometheus_middleware
from web.storage.rabbit import setup_queue_and_exchange
from web.storage.db import init_db


def setup_middleware(app: FastAPI) -> None:

    app.middleware('http')(
        partial(http_prometheus_middleware, exclude_routes=None),
    )
    app.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])

    # CORS Middleware should be last
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,  # type: ignore
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )


def setup_routers(app: FastAPI) -> None:
    app.include_router(v1_router, prefix='/api/v1') # затестить
    app.include_router(tech_router, prefix='/api/tech')


def setup_logger() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    if settings.LOG_LEVEL == 'DEBUG':
        logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Starting pod...')

    logger.info('Launch metrics server...')
    start_http_server(settings.METRICS_APP_PORT)

    logger.info('Setup exchange and queue...')
    await setup_queue_and_exchange()

    logger.info('Setup database...')
    await init_db()

    logger.info('Start successfully')
    yield

    logger.info('Drop successfully')


def create_app() -> FastAPI:
    setup_logger()

    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    setup_middleware(app)
    setup_routers(app)
    return app
