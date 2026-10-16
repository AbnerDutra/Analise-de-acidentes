from unicodedata import combining, normalize

from sqlalchemy import case, func, select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import Session

from ..entities import Acidente, Local, Veiculo
from ..schemas import (
    AnaliseCategoriaRead,
    AnaliseHorarioRead,
    AnaliseLocalRead,
    AnalisePeriodoRead,
    AnaliseRegiaoRead,
    AnaliseResumoRead,
    AnaliseVeiculoRead,
)


class AnaliseAcidenteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def resumo(self) -> AnaliseResumoRead:
        statement = select(
            func.count(Acidente.idacidente),
            func.coalesce(func.sum(Acidente.qtd_vitimas), 0),
        )
        total_acidentes, total_vitimas = self.db.execute(statement).one()
        return AnaliseResumoRead(
            total_acidentes=int(total_acidentes),
            total_vitimas=int(total_vitimas),
        )

    def quantidade_por_regiao(
        self,
        cidade: str | None = None,
    ) -> list[AnaliseRegiaoRead]:
        total = func.count(Acidente.idacidente)
        statement = (
            select(Local.estado, Local.cidade, total)
            .join(Acidente, Acidente.idlocal == Local.idlocal)
            .group_by(Local.estado, Local.cidade)
            .order_by(total.desc(), Local.estado, Local.cidade)
        )

        cidade_normalizada = cidade.strip() if cidade is not None else ""
        if cidade_normalizada:
            statement = statement.where(
                func.lower(Local.cidade) == cidade_normalizada.lower()
            )

        return [
            AnaliseRegiaoRead(
                estado=estado,
                cidade=nome_cidade,
                total_acidentes=int(total_acidentes),
            )
            for estado, nome_cidade, total_acidentes in self.db.execute(statement)
        ]

    def horarios_com_mais_acidentes(self) -> list[AnaliseHorarioRead]:
        hora = func.extract("hour", Acidente.hora_acidente)
        total = func.count(Acidente.idacidente)
        statement = (
            select(hora, total)
            .group_by(hora)
            .order_by(total.desc(), hora)
        )

        return [
            AnaliseHorarioRead(
                posicao=posicao,
                hora_inicio=f"{int(hora_acidente):02d}:00",
                hora_fim=f"{int(hora_acidente):02d}:59",
                total_acidentes=int(total_acidentes),
            )
            for posicao, (hora_acidente, total_acidentes) in enumerate(
                self.db.execute(statement),
                start=1,
            )
        ]

    def quantidade_por_clima(self) -> list[AnaliseCategoriaRead]:
        return self._quantidade_por_categoria(Acidente.nome_clima)

    def quantidade_por_gravidade(self) -> list[AnaliseCategoriaRead]:
        return self._quantidade_por_categoria(Acidente.tipo_gravidade)

    def _quantidade_por_categoria(
        self,
        coluna: ColumnElement[str],
    ) -> list[AnaliseCategoriaRead]:
        total = func.count(Acidente.idacidente)
        statement = (
            select(coluna, total)
            .group_by(coluna)
            .order_by(total.desc(), coluna)
        )
        return [
            AnaliseCategoriaRead(categoria=categoria, quantidade=int(quantidade))
            for categoria, quantidade in self.db.execute(statement)
        ]

    def quantidade_por_periodo(self) -> list[AnalisePeriodoRead]:
        hora = func.extract("hour", Acidente.hora_acidente)
        periodo = case(
            (hora.between(6, 17), "dia"),
            else_="noite",
        )
        total = func.count(Acidente.idacidente)
        statement = select(periodo, total).group_by(periodo)
        quantidades = {
            nome: int(quantidade)
            for nome, quantidade in self.db.execute(statement)
        }
        return [
            AnalisePeriodoRead(periodo=nome, quantidade=quantidades.get(nome, 0))
            for nome in ("dia", "noite")
        ]

    @staticmethod
    def _normalizar_tipo_veiculo(nome: str) -> str | None:
        sem_acentos = normalize("NFKD", nome.casefold())
        normalizado = "".join(
            caractere
            for caractere in sem_acentos
            if not combining(caractere)
        )
        if "moto" in normalizado:
            return "moto"
        if "carro" in normalizado or "automovel" in normalizado:
            return "carro"
        return None

    def tipos_veiculos_mais_envolvidos(self) -> list[AnaliseVeiculoRead]:
        statement = select(Veiculo.nome_veiculo)
        contagens = {"carro": 0, "moto": 0}
        for (nome_veiculo,) in self.db.execute(statement):
            tipo = self._normalizar_tipo_veiculo(nome_veiculo)
            if tipo is not None:
                contagens[tipo] += 1

        return [
            AnaliseVeiculoRead(tipo=tipo, quantidade=quantidade)
            for tipo, quantidade in sorted(
                contagens.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]

    def locais_com_mais_ocorrencias(self) -> list[AnaliseLocalRead]:
        total = func.count(Acidente.idacidente)
        statement = (
            select(
                Local.idlocal,
                Local.estado,
                Local.cidade,
                Local.bairro,
                Local.rua,
                total,
            )
            .join(Acidente, Acidente.idlocal == Local.idlocal)
            .group_by(
                Local.idlocal,
                Local.estado,
                Local.cidade,
                Local.bairro,
                Local.rua,
            )
            .order_by(total.desc(), Local.idlocal)
        )
        ocorrencias = list(self.db.execute(statement))
        if not ocorrencias:
            return []

        maior_total = int(ocorrencias[0][5])
        return [
            AnaliseLocalRead(
                idlocal=idlocal,
                estado=estado,
                cidade=cidade,
                bairro=bairro,
                rua=rua,
                total_ocorrencias=int(total_ocorrencias),
            )
            for idlocal, estado, cidade, bairro, rua, total_ocorrencias in ocorrencias
            if int(total_ocorrencias) == maior_total
        ]