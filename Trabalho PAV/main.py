from sqlalchemy import (
    create_engine, event, text, Column, Integer, String, Date,
    ForeignKey, Identity, CheckConstraint, Index,
)
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine('postgresql://postgres:123456@localhost:5432/postgres')
Base = declarative_base()


# FUNÇÃO AUXILIAR: converte "15 de junho de 2026" em DATE
# Criada automaticamente antes das tabelas
FUNCAO_DATA_PT = """
CREATE OR REPLACE FUNCTION data_pt_para_date(texto TEXT) RETURNS DATE AS $$
DECLARE
    meses  TEXT[] := ARRAY['janeiro','fevereiro','março','abril','maio','junho',
                           'julho','agosto','setembro','outubro','novembro','dezembro'];
    partes TEXT[];
    mes    INTEGER;
BEGIN
    partes := regexp_match(lower(trim(texto)), '^(\\d{1,2}) de ([a-zç]+) de (\\d{4})$');
    IF partes IS NULL THEN
        RAISE EXCEPTION 'Formato inválido: %. Use "15 de junho de 2026"', texto;
    END IF;

    mes := array_position(meses, partes[2]);
    IF mes IS NULL THEN
        RAISE EXCEPTION 'Mês inválido: %', partes[2];
    END IF;

    RETURN make_date(partes[3]::INT, mes, partes[1]::INT);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
"""


@event.listens_for(Base.metadata, 'before_create')
def criar_funcao_data(target, connection, **kw):
    connection.execute(text(FUNCAO_DATA_PT))


# =====================================================
# 1 LOCAL: onde o acidente aconteceu
# =====================================================
class Local(Base):
    __tablename__ = 'local'

    idlocal = Column(Integer, Identity(), primary_key=True)
    estado = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    bairro = Column(String)
    rua = Column(String)

    acidentes = relationship('Acidente', back_populates='local')


# =====================================================
# 2 ACIDENTE: tabela central (data, hora, clima e gravidade)
# =====================================================
class Acidente(Base):
    __tablename__ = 'acidente'

    idacidente = Column(Integer, Identity(), primary_key=True)
    idlocal = Column(Integer, ForeignKey('local.idlocal'), nullable=False)
    data_acidente = Column(Date, nullable=False)
    hora_acidente = Column(TIME(precision=0), nullable=False)  # só HH:MM
    nome_clima = Column(String, nullable=False)
    tipo_gravidade = Column(String, nullable=False)

    local = relationship('Local', back_populates='acidentes')
    veiculos = relationship('Veiculo', back_populates='acidente')

    __table_args__ = (
        CheckConstraint(
            'EXTRACT(SECOND FROM hora_acidente) = 0',
            name='ck_hora_hhmm',
        ),
        Index('idx_acidente_idlocal', 'idlocal'),
    )


# =====================================================
# 3 VEICULO: veículos envolvidos em cada acidente
# =====================================================
class Veiculo(Base):
    __tablename__ = 'veiculo'

    idveiculo = Column(Integer, Identity(), primary_key=True)
    idacidente = Column(Integer, ForeignKey('acidente.idacidente'), nullable=False)
    nome_veiculo = Column(String, nullable=False)

    acidente = relationship('Acidente', back_populates='veiculos')

    __table_args__ = (
        Index('idx_veiculo_idacidente', 'idacidente'),
    )


# CRIAÇÃO DAS TABELAS
Base.metadata.create_all(engine)

Base.metadata.create_all(engine)

from sqlalchemy import inspect

Base.metadata.create_all(engine)

inspetor = inspect(engine)

print("Tabelas existentes no PostgreSQL:")
print(inspetor.get_table_names())