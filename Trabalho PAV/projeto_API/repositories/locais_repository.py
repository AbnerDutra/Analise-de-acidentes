from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..entities import Acidente, Local
from ..schemas import LocalInput


class LocalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_ou_salvar(self, dados: LocalInput) -> Local:
        local = self.db.scalars(
            select(Local).filter_by(
                estado=dados.estado,
                cidade=dados.cidade,
                bairro=dados.bairro,
                rua=dados.rua,
            )
        ).first()
        if local is not None:
            return local

        local = Local(
            estado=dados.estado,
            cidade=dados.cidade,
            bairro=dados.bairro,
            rua=dados.rua,
        )
        self.db.add(local)
        self.db.flush()
        return local

    def buscar_todos(self) -> list[Local]:
        statement = select(Local).order_by(Local.idlocal)
        return list(self.db.scalars(statement).all())

    def buscar(self, idlocal: int) -> Local | None:
        return self.db.get(Local, idlocal)

    def salvar(self, dados: LocalInput) -> Local:
        local = Local(
            estado=dados.estado,
            cidade=dados.cidade,
            bairro=dados.bairro,
            rua=dados.rua,
        )
        self.db.add(local)
        self.db.commit()
        self.db.refresh(local)
        return local

    def atualizar(self, idlocal: int, dados: LocalInput) -> Local | None:
        local = self.db.get(Local, idlocal)
        if local is None:
            return None

        local.estado = dados.estado
        local.cidade = dados.cidade
        local.bairro = dados.bairro
        local.rua = dados.rua
        self.db.commit()
        self.db.refresh(local)
        return local

    def possui_acidentes(self, idlocal: int) -> bool:
        statement = (
            select(func.count())
            .select_from(Acidente)
            .where(Acidente.idlocal == idlocal)
        )
        return self.db.scalar(statement) > 0

    def deletar(self, idlocal: int) -> bool:
        local = self.db.get(Local, idlocal)
        if local is None:
            return False

        self.db.delete(local)
        self.db.commit()
        return True
