from sqlalchemy.orm import Session

from ..entities import Acidente, Veiculo
from ..repositories import VeiculoRepository
from ..schemas import VeiculoInput
from .exceptions import (
    InvalidDataError,
    ResourceConflictError,
    ResourceNotFoundError,
)


class DadosVeiculoInvalidos(InvalidDataError):
    pass


class RegistroVeiculoNaoEncontrado(ResourceNotFoundError):
    pass


class AcidenteVeiculoNaoEncontrado(ResourceNotFoundError):
    pass


class UltimoVeiculoDoAcidente(ResourceConflictError):
    pass


class VeiculoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = VeiculoRepository(db)

    @staticmethod
    def _validar_tipo(dados: VeiculoInput) -> None:
        if not dados.nome_veiculo or not dados.nome_veiculo.strip():
            raise DadosVeiculoInvalidos("O tipo do veículo é obrigatório.")
        dados.nome_veiculo = dados.nome_veiculo.strip()

    def _validar_acidente(self, idacidente: int) -> None:
        if self.db.get(Acidente, idacidente) is None:
            raise AcidenteVeiculoNaoEncontrado(
                f"Acidente {idacidente} não encontrado."
            )

    def buscar_todos(self) -> list[Veiculo]:
        return self.repository.buscar_todos()

    def buscar(self, idveiculo: int) -> Veiculo:
        veiculo = self.repository.buscar(idveiculo)
        if veiculo is None:
            raise RegistroVeiculoNaoEncontrado(
                f"Veículo {idveiculo} não encontrado."
            )
        return veiculo

    def salvar(self, dados: VeiculoInput) -> Veiculo:
        self._validar_tipo(dados)
        self._validar_acidente(dados.idacidente)
        return self.repository.salvar(dados)

    def atualizar(self, idveiculo: int, dados: VeiculoInput) -> Veiculo:
        self._validar_tipo(dados)
        if self.repository.buscar(idveiculo) is None:
            raise RegistroVeiculoNaoEncontrado(
                f"Veículo {idveiculo} não encontrado."
            )
        self._validar_acidente(dados.idacidente)
        veiculo = self.repository.atualizar(idveiculo, dados)
        if veiculo is None:
            raise RegistroVeiculoNaoEncontrado(
                f"Veículo {idveiculo} não encontrado."
            )
        return veiculo

    def deletar(self, idveiculo: int) -> None:
        veiculo = self.repository.buscar(idveiculo)
        if veiculo is None:
            raise RegistroVeiculoNaoEncontrado(
                f"Veículo {idveiculo} não encontrado."
            )
        if len(veiculo.acidente.veiculos) <= 1:
            raise UltimoVeiculoDoAcidente(
                "Não é possível excluir o único veículo do acidente."
            )
        if not self.repository.deletar(idveiculo):
            raise RegistroVeiculoNaoEncontrado(
                f"Veículo {idveiculo} não encontrado."
            )