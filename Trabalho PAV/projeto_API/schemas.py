from datetime import date, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    ValidationInfo,
    field_validator,
)


class VeiculoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idveiculo: int
    idacidente: int
    nome_veiculo: str


class VeiculoInput(BaseModel):
    idacidente: StrictInt = Field(gt=0)
    nome_veiculo: str = Field(min_length=1)

    @field_validator("nome_veiculo")
    @classmethod
    def validar_nome_veiculo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O tipo do veículo é obrigatório.")
        return value


class LocalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idlocal: int
    estado: str
    cidade: str
    bairro: str | None
    rua: str | None


class LocalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idlocal: int
    estado: str
    cidade: str
    bairro: str | None
    rua: str | None


class LocalInput(BaseModel):
    estado: str = Field(min_length=1)
    cidade: str = Field(min_length=1)
    bairro: str = Field(min_length=1)
    rua: str = Field(min_length=1)

    @field_validator("estado", "cidade", "bairro", "rua")
    @classmethod
    def validar_endereco(
        cls,
        value: str,
        info: ValidationInfo,
    ) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"O campo {info.field_name} não pode ficar vazio.")
        return value


class AcidenteInput(BaseModel):
    local: LocalInput
    data_acidente: date
    hora_acidente: time
    qtd_vitimas: StrictInt = Field(ge=0)
    qtd_veiculos: StrictInt = Field(gt=0)
    tipos_veiculos: list[str] = Field(min_length=1)
    nome_clima: str = Field(min_length=1)
    tipo_gravidade: str = Field(min_length=1)

    @field_validator("hora_acidente")
    @classmethod
    def validar_hora_sem_segundos(cls, value: time) -> time:
        if value.second or value.microsecond:
            raise ValueError("A hora deve estar no formato HH:MM, sem segundos.")
        return value

    @field_validator("nome_clima", "tipo_gravidade")
    @classmethod
    def validar_texto_obrigatorio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O campo não pode ficar vazio.")
        return value

    @field_validator("tipos_veiculos")
    @classmethod
    def validar_tipos_veiculos(cls, values: list[str]) -> list[str]:
        tipos = [value.strip() for value in values]
        if any(not tipo for tipo in tipos):
            raise ValueError("Informe os tipos de veículos sem itens vazios.")
        return tipos


class AcidenteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idacidente: int
    idlocal: int
    data_acidente: date
    hora_acidente: time
    qtd_vitimas: int
    qtd_veiculos: int
    nome_clima: str
    tipo_gravidade: str
    local: LocalRead
    veiculos: list[VeiculoRead]


class AnaliseRegiaoRead(BaseModel):
    estado: str
    cidade: str
    total_acidentes: int


class AnaliseHorarioRead(BaseModel):
    posicao: int
    hora_inicio: str
    hora_fim: str
    total_acidentes: int


class AnaliseResumoRead(BaseModel):
    total_acidentes: int
    total_vitimas: int


class AnaliseCategoriaRead(BaseModel):
    categoria: str
    quantidade: int


class AnalisePeriodoRead(BaseModel):
    periodo: str
    quantidade: int


class AnaliseVeiculoRead(BaseModel):
    nome_veiculo: str
    quantidade: int


class AnaliseLocalRead(BaseModel):
    idlocal: int
    estado: str
    cidade: str
    bairro: str | None
    rua: str | None
    total_ocorrencias: int
