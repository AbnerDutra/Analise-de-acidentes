from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from .config.database import create_session_factory
from .routes.analises import router as analises_router
from .routes.acidentes import router as acidentes_router
from .routes.locais import router as locais_router
from .routes.veiculos import router as veiculos_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.session_factory = create_session_factory()
    yield


app = FastAPI(
    title="API de Acidentes",
    description="API para consulta e gerenciamento de acidentes de trânsito.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(acidentes_router)
app.include_router(locais_router)
app.include_router(veiculos_router)
app.include_router(analises_router)
