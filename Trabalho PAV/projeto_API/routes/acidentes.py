from collections.abc import Generator

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..entities import Acidente
from ..controllers import AcidenteController
from ..schemas import AcidenteInput, AcidenteRead


router = APIRouter(prefix="/acidentes", tags=["Acidentes"])


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


@router.get("", response_model=list[AcidenteRead])
def listar_acidentes(db: Session = Depends(get_db)) -> list[Acidente]:
    return AcidenteController(db).listar()


@router.post(
    "",
    response_model=AcidenteRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_acidente(
    dados: AcidenteInput,
    db: Session = Depends(get_db),
) -> Acidente:
    return AcidenteController(db).cadastrar(dados)


@router.get("/{idacidente}", response_model=AcidenteRead)
def buscar_acidente(
    idacidente: int,
    db: Session = Depends(get_db),
) -> Acidente:
    return AcidenteController(db).buscar(idacidente)


@router.put("/{idacidente}", response_model=AcidenteRead)
def atualizar_acidente(
    idacidente: int,
    dados: AcidenteInput,
    db: Session = Depends(get_db),
) -> Acidente:
    return AcidenteController(db).atualizar(idacidente, dados)


@router.delete("/{idacidente}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_acidente(idacidente: int, db: Session = Depends(get_db)):
    return AcidenteController(db).deletar(idacidente)


@router.delete("")
def excluir_todos_acidentes(db: Session = Depends(get_db)) -> dict[str, int]:
    return AcidenteController(db).deletar_todos()
