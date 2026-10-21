from fastapi import Response, status
from sqlalchemy.orm import Session

from ..entities import Veiculo
from ..schemas import VeiculoInput
from ..services.veiculo_service import VeiculoService


class VeiculoController:
    def __init__(self, db: Session) -> None:
        self.service = VeiculoService(db)

    def listar(self) -> list[Veiculo]:
        return self.service.buscar_todos()

    def cadastrar(self, dados: VeiculoInput) -> Veiculo:
        return self.service.salvar(dados)

    def buscar(self, idveiculo: int) -> Veiculo:
        return self.service.buscar(idveiculo)

    def atualizar(self, idveiculo: int, dados: VeiculoInput) -> Veiculo:
        return self.service.atualizar(idveiculo, dados)

    def deletar(self, idveiculo: int) -> Response:
        self.service.deletar(idveiculo)
        return Response(status_code=status.HTTP_204_NO_CONTENT)