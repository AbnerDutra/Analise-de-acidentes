from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from ..entities import Acidente
from ..schemas import AcidenteInput
from ..services.acidente_service import (
    AcidenteService,
    DadosAcidenteInvalidos,
    RegistroAcidenteNaoEncontrado,
)


class AcidenteController:
    def __init__(self, db: Session) -> None:
        self.service = AcidenteService(db)

    def listar(self) -> list[Acidente]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: AcidenteInput) -> Acidente:
        try:
            return self.service.salvar(dados)
        except DadosAcidenteInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro

    def buscar(self, idacidente: int) -> Acidente:
        try:
            return self.service.buscar(idacidente)
        except RegistroAcidenteNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def atualizar(self, idacidente: int, dados: AcidenteInput) -> Acidente:
        try:
            return self.service.atualizar(idacidente, dados)
        except DadosAcidenteInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro
        except RegistroAcidenteNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def deletar(self, idacidente: int) -> Response:
        try:
            self.service.deletar(idacidente)
        except RegistroAcidenteNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def deletar_todos(self) -> dict[str, int]:
        return self.service.deletar_todos()