from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from ..entities import Veiculo
from ..schemas import VeiculoInput
from ..services.veiculo_service import (
    AcidenteVeiculoNaoEncontrado,
    DadosVeiculoInvalidos,
    RegistroVeiculoNaoEncontrado,
    VeiculoService,
)


class VeiculoController:
    def __init__(self, db: Session) -> None:
        self.service = VeiculoService(db)

    def listar(self) -> list[Veiculo]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: VeiculoInput) -> Veiculo:
        try:
            return self.service.salvar(dados)
        except DadosVeiculoInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro
        except AcidenteVeiculoNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def buscar(self, idveiculo: int) -> Veiculo:
        try:
            return self.service.buscar(idveiculo)
        except RegistroVeiculoNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def atualizar(self, idveiculo: int, dados: VeiculoInput) -> Veiculo:
        try:
            return self.service.atualizar(idveiculo, dados)
        except DadosVeiculoInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro
        except (
            RegistroVeiculoNaoEncontrado,
            AcidenteVeiculoNaoEncontrado,
        ) as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def deletar(self, idveiculo: int) -> Response:
        try:
            self.service.deletar(idveiculo)
        except RegistroVeiculoNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro
        return Response(status_code=status.HTTP_204_NO_CONTENT)