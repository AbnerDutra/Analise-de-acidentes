from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..entities import Acidente, Local, Veiculo
from ..schemas import AcidenteInput
from .locais_repository import LocalRepository


class AcidenteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.locais = LocalRepository(db)

    def buscar_todos(self) -> list[Acidente]:
        statement = (
            select(Acidente)
            .options(
                joinedload(Acidente.local),
                selectinload(Acidente.veiculos),
            )
            .order_by(Acidente.idacidente)
        )
        return list(self.db.scalars(statement).all())

    def buscar(self, idacidente: int) -> Acidente | None:
        statement = (
            select(Acidente)
            .options(
                joinedload(Acidente.local),
                selectinload(Acidente.veiculos),
            )
            .where(Acidente.idacidente == idacidente)
        )
        return self.db.scalars(statement).first()

    def salvar(self, dados: AcidenteInput) -> Acidente:
        acidente = Acidente(
            local=self.locais.buscar_ou_salvar(dados.local),
            data_acidente=dados.data_acidente,
            hora_acidente=dados.hora_acidente,
            qtd_vitimas=dados.qtd_vitimas,
            nome_clima=dados.nome_clima,
            tipo_gravidade=dados.tipo_gravidade,
            veiculos=[
                Veiculo(nome_veiculo=nome) for nome in dados.veiculos
            ],
        )
        self.db.add(acidente)
        self.db.commit()
        self.db.refresh(acidente)
        return acidente

    def atualizar(
        self,
        idacidente: int,
        dados: AcidenteInput,
    ) -> Acidente | None:
        acidente = self.db.scalars(
            select(Acidente)
            .options(selectinload(Acidente.veiculos))
            .where(Acidente.idacidente == idacidente)
        ).first()
        if acidente is None:
            return None

        acidente.local = self.locais.buscar_ou_salvar(dados.local)
        acidente.data_acidente = dados.data_acidente
        acidente.hora_acidente = dados.hora_acidente
        acidente.qtd_vitimas = dados.qtd_vitimas
        acidente.nome_clima = dados.nome_clima
        acidente.tipo_gravidade = dados.tipo_gravidade
        acidente.veiculos = [
            Veiculo(nome_veiculo=nome) for nome in dados.veiculos
        ]
        self.db.commit()
        self.db.refresh(acidente)
        return acidente

    def deletar(self, idacidente: int) -> bool:
        acidente = self.db.scalars(
            select(Acidente)
            .options(selectinload(Acidente.veiculos))
            .where(Acidente.idacidente == idacidente)
        ).first()
        if acidente is None:
            return False

        for veiculo in acidente.veiculos:
            self.db.delete(veiculo)
        self.db.delete(acidente)
        self.db.commit()
        return True

    def deletar_todos(self) -> dict[str, int]:
        veiculos_excluidos = self.db.execute(delete(Veiculo)).rowcount or 0
        acidentes_excluidos = self.db.execute(delete(Acidente)).rowcount or 0
        locais_excluidos = self.db.execute(delete(Local)).rowcount or 0
        self.db.commit()
        return {
            "acidentes": acidentes_excluidos,
            "veiculos": veiculos_excluidos,
            "locais": locais_excluidos,
        }
