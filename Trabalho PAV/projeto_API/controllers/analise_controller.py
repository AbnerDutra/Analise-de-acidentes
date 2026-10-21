from sqlalchemy.orm import Session

from ..schemas import (
    AnaliseCategoriaRead,
    AnaliseHorarioRead,
    AnaliseLocalRead,
    AnalisePeriodoRead,
    AnaliseRegiaoRead,
    AnaliseResumoRead,
    AnaliseVeiculoRead,
)
from ..services.analise_acidente_service import AnaliseAcidenteService


class AnaliseController:
    def __init__(self, db: Session) -> None:
        self.service = AnaliseAcidenteService(db)

    def resumo(self) -> AnaliseResumoRead:
        return self.service.resumo()

    def quantidade_por_regiao(
        self,
        cidade: str | None = None,
    ) -> list[AnaliseRegiaoRead]:
        return self.service.quantidade_por_regiao(cidade)

    def horarios_com_mais_acidentes(self) -> list[AnaliseHorarioRead]:
        return self.service.horarios_com_mais_acidentes()

    def quantidade_por_clima(self) -> list[AnaliseCategoriaRead]:
        return self.service.quantidade_por_clima()

    def quantidade_por_gravidade(self) -> list[AnaliseCategoriaRead]:
        return self.service.quantidade_por_gravidade()

    def quantidade_por_periodo(self) -> list[AnalisePeriodoRead]:
        return self.service.quantidade_por_periodo()

    def tipos_veiculos_mais_envolvidos(self) -> list[AnaliseVeiculoRead]:
        return self.service.tipos_veiculos_mais_envolvidos()

    def locais_com_mais_ocorrencias(self) -> list[AnaliseLocalRead]:
        return self.service.locais_com_mais_ocorrencias()
