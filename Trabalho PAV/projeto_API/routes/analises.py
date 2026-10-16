from collections.abc import Generator

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ..controllers import AnaliseController
from ..schemas import (
    AnaliseCategoriaRead,
    AnaliseHorarioRead,
    AnaliseLocalRead,
    AnalisePeriodoRead,
    AnaliseRegiaoRead,
    AnaliseResumoRead,
    AnaliseVeiculoRead,
)


router = APIRouter(prefix="/analises", tags=["Análises"])


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


@router.get("/resumo", response_model=AnaliseResumoRead)
def resumo(db: Session = Depends(get_db)) -> AnaliseResumoRead:
    return AnaliseController(db).resumo()


@router.get(
    "/acidentes-por-regiao",
    response_model=list[AnaliseRegiaoRead],
)
def quantidade_por_regiao(
    cidade: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AnaliseRegiaoRead]:
    return AnaliseController(db).quantidade_por_regiao(cidade)


@router.get(
    "/horarios-com-mais-acidentes",
    response_model=list[AnaliseHorarioRead],
)
def horarios_com_mais_acidentes(
    db: Session = Depends(get_db),
) -> list[AnaliseHorarioRead]:
    return AnaliseController(db).horarios_com_mais_acidentes()


@router.get(
    "/acidentes-por-clima",
    response_model=list[AnaliseCategoriaRead],
)
def quantidade_por_clima(
    db: Session = Depends(get_db),
) -> list[AnaliseCategoriaRead]:
    return AnaliseController(db).quantidade_por_clima()


@router.get(
    "/acidentes-por-gravidade",
    response_model=list[AnaliseCategoriaRead],
)
def quantidade_por_gravidade(
    db: Session = Depends(get_db),
) -> list[AnaliseCategoriaRead]:
    return AnaliseController(db).quantidade_por_gravidade()


@router.get(
    "/acidentes-por-periodo",
    response_model=list[AnalisePeriodoRead],
)
def quantidade_por_periodo(
    db: Session = Depends(get_db),
) -> list[AnalisePeriodoRead]:
    return AnaliseController(db).quantidade_por_periodo()


@router.get(
    "/veiculos-mais-envolvidos",
    response_model=list[AnaliseVeiculoRead],
)
def tipos_veiculos_mais_envolvidos(
    db: Session = Depends(get_db),
) -> list[AnaliseVeiculoRead]:
    return AnaliseController(db).tipos_veiculos_mais_envolvidos()


@router.get(
    "/locais-com-mais-ocorrencias",
    response_model=list[AnaliseLocalRead],
)
def locais_com_mais_ocorrencias(
    db: Session = Depends(get_db),
) -> list[AnaliseLocalRead]:
    return AnaliseController(db).locais_com_mais_ocorrencias()
