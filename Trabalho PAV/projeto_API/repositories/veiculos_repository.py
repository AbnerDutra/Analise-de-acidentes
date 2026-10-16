from sqlalchemy import select
from sqlalchemy.orm import Session

from ..entities import Veiculo
from ..schemas import VeiculoInput


class VeiculoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_todos(self) -> list[Veiculo]:
        statement = select(Veiculo).order_by(Veiculo.idveiculo)
        return list(self.db.scalars(statement).all())

    def buscar(self, idveiculo: int) -> Veiculo | None:
        return self.db.get(Veiculo, idveiculo)

    def salvar(self, dados: VeiculoInput) -> Veiculo:
        veiculo = Veiculo(
            idacidente=dados.idacidente,
            nome_veiculo=dados.nome_veiculo,
        )
        self.db.add(veiculo)
        self.db.commit()
        self.db.refresh(veiculo)
        return veiculo

    def atualizar(
        self,
        idveiculo: int,
        dados: VeiculoInput,
    ) -> Veiculo | None:
        veiculo = self.db.get(Veiculo, idveiculo)
        if veiculo is None:
            return None

        veiculo.idacidente = dados.idacidente
        veiculo.nome_veiculo = dados.nome_veiculo
        self.db.commit()
        self.db.refresh(veiculo)
        return veiculo

    def deletar(self, idveiculo: int) -> bool:
        veiculo = self.db.get(Veiculo, idveiculo)
        if veiculo is None:
            return False

        self.db.delete(veiculo)
        self.db.commit()
        return True
