from fastapi import Response
from sqlalchemy.orm import Session

from ..entities import Acidente
from ..schemas import AcidenteInput
from ..services.acidente_service import AcidenteService


class AcidenteController:
    def __init__(self, db: Session) -> None:
        self.service = AcidenteService(db)

    def listar(self) -> list[Acidente]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: AcidenteInput) -> Acidente:
        return self.service.salvar(dados)

    def buscar(self, idacidente: int) -> Acidente:
        return self.service.buscar(idacidente)

    def atualizar(self, idacidente: int, dados: AcidenteInput) -> Acidente:
        return self.service.atualizar(idacidente, dados)

    def deletar(self, idacidente: int) -> Response:
        self.service.deletar(idacidente)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def deletar_todos(self) -> dict[str, int]:
        return self.service.deletar_todos()