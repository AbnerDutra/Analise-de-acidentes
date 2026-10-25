from datetime import date, time

from sqlalchemy.orm import Session

from ..entities import Acidente
from ..repositories import AcidenteRepository
from ..schemas import AcidenteInput
from .exceptions import InvalidDataError, ResourceNotFoundError


class DadosAcidenteInvalidos(InvalidDataError):
    pass


class RegistroAcidenteNaoEncontrado(ResourceNotFoundError):
    pass


class AcidenteService:
    GRAVIDADES_PERMITIDAS = frozenset({"leve", "moderada", "grave", "fatal"})
    CLIMAS_PERMITIDOS = frozenset(
        {"ensolarado", "chuvoso", "neblina", "nublado"}
    )

    def __init__(self, db: Session) -> None:
        self.repository = AcidenteRepository(db)

    @classmethod
    def _validar_e_normalizar(cls, dados: AcidenteInput) -> None:
        if dados.data_acidente > date.today():
            raise DadosAcidenteInvalidos(
                "A data do acidente não pode estar no futuro."
            )

        if dados.qtd_vitimas < 0:
            raise DadosAcidenteInvalidos(
                "A quantidade de vítimas deve ser maior ou igual a zero."
            )

        if dados.qtd_veiculos <= 0:
            raise DadosAcidenteInvalidos(
                "Informe pelo menos um veículo envolvido no acidente."
            )

        dados.tipos_veiculos = [
            tipo.strip() for tipo in dados.tipos_veiculos
        ]
        if any(not tipo for tipo in dados.tipos_veiculos):
            raise DadosAcidenteInvalidos(
                "Informe os tipos de veículos sem itens vazios."
            )
        if len(dados.tipos_veiculos) != dados.qtd_veiculos:
            raise DadosAcidenteInvalidos(
                "A quantidade de tipos de veículos deve corresponder "
                "à quantidade de veículos envolvidos."
            )

        gravidade = dados.tipo_gravidade.strip().casefold()
        if gravidade not in cls.GRAVIDADES_PERMITIDAS:
            permitidas = ", ".join(sorted(cls.GRAVIDADES_PERMITIDAS))
            raise DadosAcidenteInvalidos(
                f"Gravidade inválida. Opções permitidas: {permitidas}."
            )

        clima = dados.nome_clima.strip().casefold()
        if clima not in cls.CLIMAS_PERMITIDOS:
            permitidos = ", ".join(sorted(cls.CLIMAS_PERMITIDOS))
            raise DadosAcidenteInvalidos(
                f"Condição climática inválida. Opções permitidas: {permitidos}."
            )

        if (
            not isinstance(dados.hora_acidente, time)
            or dados.hora_acidente.tzinfo is not None
            or dados.hora_acidente.second != 0
            or dados.hora_acidente.microsecond != 0
        ):
            raise DadosAcidenteInvalidos(
                "O horário deve ser válido e estar no formato HH:MM."
            )

        dados.tipo_gravidade = gravidade
        dados.nome_clima = clima

    def buscar_todos(self) -> list[Acidente]:
        return self.repository.buscar_todos()

    def buscar(self, idacidente: int) -> Acidente:
        acidente = self.repository.buscar(idacidente)
        if acidente is None:
            raise RegistroAcidenteNaoEncontrado(
                f"Acidente {idacidente} não encontrado."
            )
        return acidente

    def salvar(self, dados: AcidenteInput) -> Acidente:
        self._validar_e_normalizar(dados)
        return self.repository.salvar(dados)

    def atualizar(self, idacidente: int, dados: AcidenteInput) -> Acidente:
        self._validar_e_normalizar(dados)
        acidente = self.repository.atualizar(idacidente, dados)
        if acidente is None:
            raise RegistroAcidenteNaoEncontrado(
                f"Acidente {idacidente} não encontrado."
            )
        return acidente

    def deletar(self, idacidente: int) -> None:
        if not self.repository.deletar(idacidente):
            raise RegistroAcidenteNaoEncontrado(
                f"Acidente {idacidente} não encontrado."
            )

    def deletar_todos(self) -> dict[str, int]:
        return self.repository.deletar_todos()