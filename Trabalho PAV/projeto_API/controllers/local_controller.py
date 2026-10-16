from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from ..entities import Local
from ..schemas import LocalInput
from ..services.local_service import (
    DadosLocalInvalidos,
    LocalAssociadoAAcidentes,
    LocalService,
    RegistroLocalNaoEncontrado,
)


class LocalController:
    def __init__(self, db: Session) -> None:
        self.service = LocalService(db)

    def listar(self) -> list[Local]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: LocalInput) -> Local:
        try:
            return self.service.salvar(dados)
        except DadosLocalInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro

    def buscar(self, idlocal: int) -> Local:
        try:
            return self.service.buscar(idlocal)
        except RegistroLocalNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def atualizar(self, idlocal: int, dados: LocalInput) -> Local:
        try:
            return self.service.atualizar(idlocal, dados)
        except DadosLocalInvalidos as erro:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(erro),
            ) from erro
        except RegistroLocalNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro

    def deletar(self, idlocal: int) -> Response:
        try:
            self.service.deletar(idlocal)
        except RegistroLocalNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro
        except LocalAssociadoAAcidentes as erro:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(erro),
            ) from erro
        return Response(status_code=status.HTTP_204_NO_CONTENT)