from collections.abc import Generator

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..controllers import LocalController
from ..entities import Local
from ..schemas import LocalInput, LocalResponse


router = APIRouter(prefix="/locais", tags=["Locais"])


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


@router.get("", response_model=list[LocalResponse])
def listar_locais(db: Session = Depends(get_db)) -> list[Local]:
    return LocalController(db).listar()


@router.post(
    "",
    response_model=LocalResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_local(
    dados: LocalInput,
    db: Session = Depends(get_db),
) -> Local:
    return LocalController(db).cadastrar(dados)


@router.get("/{idlocal}", response_model=LocalResponse)
def buscar_local(idlocal: int, db: Session = Depends(get_db)) -> Local:
    return LocalController(db).buscar(idlocal)


@router.put("/{idlocal}", response_model=LocalResponse)
def atualizar_local(
    idlocal: int,
    dados: LocalInput,
    db: Session = Depends(get_db),
) -> Local:
    return LocalController(db).atualizar(idlocal, dados)


@router.delete("/{idlocal}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_local(idlocal: int, db: Session = Depends(get_db)):
    return LocalController(db).deletar(idlocal)
