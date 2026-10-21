from fastapi import Response, status
from sqlalchemy.orm import Session

from ..entities import Local
from ..schemas import LocalInput
from ..services.local_service import LocalService


class LocalController:
    def __init__(self, db: Session) -> None:
        self.service = LocalService(db)

    def listar(self) -> list[Local]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: LocalInput) -> Local:
        return self.service.salvar(dados)

    def buscar(self, idlocal: int) -> Local:
        return self.service.buscar(idlocal)

    def atualizar(self, idlocal: int, dados: LocalInput) -> Local:
        return self.service.atualizar(idlocal, dados)

    def deletar(self, idlocal: int) -> Response:
        self.service.deletar(idlocal)
        return Response(status_code=status.HTTP_204_NO_CONTENT)