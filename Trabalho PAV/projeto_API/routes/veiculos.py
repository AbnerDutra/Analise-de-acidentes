from collections.abc import Generator

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..controllers import VeiculoController
from ..entities import Veiculo
from ..schemas import VeiculoInput, VeiculoRead


router = APIRouter(prefix="/veiculos", tags=["Veículos"])


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    with session_factory() as session:
        yield session


@router.get("", response_model=list[VeiculoRead])
def listar_veiculos(db: Session = Depends(get_db)) -> list[Veiculo]:
    return VeiculoController(db).listar()


@router.post(
    "",
    response_model=VeiculoRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_veiculo(
    dados: VeiculoInput,
    db: Session = Depends(get_db),
) -> Veiculo:
    return VeiculoController(db).cadastrar(dados)


@router.get("/{idveiculo}", response_model=VeiculoRead)
def buscar_veiculo(
    idveiculo: int,
    db: Session = Depends(get_db),
) -> Veiculo:
    return VeiculoController(db).buscar(idveiculo)


@router.put("/{idveiculo}", response_model=VeiculoRead)
def atualizar_veiculo(
    idveiculo: int,
    dados: VeiculoInput,
    db: Session = Depends(get_db),
) -> Veiculo:
    return VeiculoController(db).atualizar(idveiculo, dados)


@router.delete("/{idveiculo}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_veiculo(
    idveiculo: int,
    db: Session = Depends(get_db),
):
    return VeiculoController(db).deletar(idveiculo)
