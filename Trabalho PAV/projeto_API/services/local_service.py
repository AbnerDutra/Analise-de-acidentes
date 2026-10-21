from sqlalchemy.orm import Session

from ..entities import Local
from ..repositories import LocalRepository
from ..schemas import LocalInput
from .exceptions import (
    InvalidDataError,
    ResourceConflictError,
    ResourceNotFoundError,
)


class DadosLocalInvalidos(InvalidDataError):
    pass


class RegistroLocalNaoEncontrado(ResourceNotFoundError):
    pass


class LocalAssociadoAAcidentes(ResourceConflictError):
    pass


class LocalService:
    def __init__(self, db: Session) -> None:
        self.repository = LocalRepository(db)

    @staticmethod
    def _validar(dados: LocalInput) -> None:
        campos_obrigatorios = {
            "estado": dados.estado,
            "cidade": dados.cidade,
            "bairro": dados.bairro,
            "rua": dados.rua,
        }
        for campo, valor in campos_obrigatorios.items():
            if not valor or not valor.strip():
                raise DadosLocalInvalidos(
                    f"O campo {campo} é obrigatório e não pode conter apenas espaços."
                )

            setattr(dados, campo, valor.strip())

    def buscar_todos(self) -> list[Local]:
        return self.repository.buscar_todos()

    def buscar(self, idlocal: int) -> Local:
        local = self.repository.buscar(idlocal)
        if local is None:
            raise RegistroLocalNaoEncontrado(
                f"Local {idlocal} não encontrado."
            )
        return local

    def salvar(self, dados: LocalInput) -> Local:
        self._validar(dados)
        return self.repository.salvar(dados)

    def atualizar(self, idlocal: int, dados: LocalInput) -> Local:
        self._validar(dados)
        local = self.repository.atualizar(idlocal, dados)
        if local is None:
            raise RegistroLocalNaoEncontrado(
                f"Local {idlocal} não encontrado."
            )
        return local

    def deletar(self, idlocal: int) -> None:
        local = self.repository.buscar(idlocal)
        if local is None:
            raise RegistroLocalNaoEncontrado(
                f"Local {idlocal} não encontrado."
            )

        if self.repository.possui_acidentes(idlocal):
            raise LocalAssociadoAAcidentes(
                f"Local {idlocal} não pode ser excluído porque possui acidentes associados."
            )

        self.repository.deletar(idlocal)