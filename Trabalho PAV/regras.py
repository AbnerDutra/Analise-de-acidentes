import re
from datetime import date, time

from sqlalchemy import (
    create_engine, event, text, func, Column, Integer, String, Date,
    ForeignKey, Identity, CheckConstraint, Index,
)
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship, Session

engine = create_engine('postgresql://postgres:123456@localhost:5432/postgres')
Base = declarative_base()


# =====================================================
# FUNÇÃO AUXILIAR NO BANCO: converte "15 de junho de 2026" em DATE
# =====================================================
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
# MODELOS
# =====================================================
class Local(Base):
    __tablename__ = 'local'

    idlocal = Column(Integer, Identity(), primary_key=True)
    estado = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    bairro = Column(String)
    rua = Column(String)

    acidentes = relationship('Acidente', back_populates='local')


class Acidente(Base):
    __tablename__ = 'acidente'

    idacidente = Column(Integer, Identity(), primary_key=True)
    idlocal = Column(Integer, ForeignKey('local.idlocal'), nullable=False)      # RN02
    data_acidente = Column(Date, nullable=False)
    hora_acidente = Column(TIME(precision=0), nullable=False)                    # RN03
    nome_clima = Column(String, nullable=False)                                  # RN08
    tipo_gravidade = Column(String, nullable=False)                              # RN04
    qtd_vitimas = Column(Integer, nullable=False, default=0)                     # RN01

    local = relationship('Local', back_populates='acidentes')
    veiculos = relationship('Veiculo', back_populates='acidente')

    __table_args__ = (
        CheckConstraint('qtd_vitimas >= 0', name='ck_vitimas_nao_negativa'),                       # RN01
        CheckConstraint('EXTRACT(SECOND FROM hora_acidente) = 0', name='ck_hora_hhmm'),
        CheckConstraint("nome_clima !~ '[0-9]' AND length(trim(nome_clima)) > 0",
                        name='ck_clima_sem_numero'),                                               # RN05
        CheckConstraint("tipo_gravidade !~ '[0-9]' AND length(trim(tipo_gravidade)) > 0",
                        name='ck_gravidade_sem_numero'),                                           # RN04, RN05
        Index('idx_acidente_idlocal', 'idlocal'),
    )


class Veiculo(Base):
    __tablename__ = 'veiculo'

    idveiculo = Column(Integer, Identity(), primary_key=True)
    idacidente = Column(Integer, ForeignKey('acidente.idacidente'), nullable=False)
    nome_veiculo = Column(String, nullable=False)

    acidente = relationship('Acidente', back_populates='veiculos')

    __table_args__ = (
        Index('idx_veiculo_idacidente', 'idacidente'),
    )


# =====================================================
# LEITURA E VALIDAÇÃO DOS DADOS
# =====================================================
MESES = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
}


def ler_texto_sem_numeros(rotulo, obrigatorio=True):
    """Aceita só letras, espaços e hífen. Sem números (RN05)."""
    while True:
        texto = input(f'{rotulo}: ').strip()
        if not texto:
            if obrigatorio:
                print(f'  Erro: {rotulo.lower()} é obrigatório.')
                continue
            return None
        if not all(c.isalpha() or c in ' -' for c in texto):
            print(f'  Erro: {rotulo.lower()} não pode conter números ou símbolos.')
            continue
        return texto


def ler_texto_livre(rotulo, obrigatorio=True):
    while True:
        texto = input(f'{rotulo}: ').strip()
        if texto:
            return texto
        if not obrigatorio:
            return None
        print(f'  Erro: {rotulo.lower()} é obrigatório.')


def ler_data():
    while True:
        texto = input('Data do acidente (Ex: 15 de junho de 2026): ').strip().lower()
        m = re.fullmatch(r'(\d{1,2}) de ([a-zç]+) de (\d{4})', texto)
        if not m:
            print('  Erro: use o formato do exemplo: (15 de junho de 2026).')
            continue
        dia, nome_mes, ano = m.groups()
        mes = MESES.get(nome_mes)
        if mes is None:
            print(f'  Erro: mês "{nome_mes}" inválido.')
            continue
        try:
            return date(int(ano), mes, int(dia))
        except ValueError:
            print('  Erro: essa data não existe.')


def ler_hora():
    """Só aceita HH:MM; letras são rejeitadas (RN03, RN06)."""
    while True:
        texto = input('Horário do acidente (HH:MM): ').strip()
        if not texto:
            print('  Erro: o horário é obrigatório.')
            continue
        if not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', texto):
            print('  Erro: use o formato HH:MM, apenas com números (00:00 a 23:59).')
            continue
        h, m = texto.split(':')
        return time(int(h), int(m))


def ler_vitimas():
    """Inteiro maior ou igual a zero (RN01)."""
    while True:
        texto = input('Quantidade de vítimas: ').strip()
        if not re.fullmatch(r'-?\d+', texto):
            print('  Erro: informe apenas um número inteiro.')
            continue
        valor = int(texto)
        if valor < 0:
            print('  Erro: a quantidade de vítimas não pode ser negativa.')
            continue
        return valor


def ler_veiculos():
    """Exige pelo menos um veículo (RN07)."""
    veiculos = []
    while True:
        if not veiculos:
            nome = input('Veículo envolvido: ').strip()
            if not nome:
                print('  Erro: informe pelo menos um veículo.')
                continue
        else:
            nome = input('Outro veículo (Enter para finalizar): ').strip()
            if not nome:
                return veiculos
        veiculos.append(nome)


# =====================================================
# FUNCIONALIDADES
# =====================================================
def cadastrar_acidente(session):
    print('\n--- Cadastro de acidente ---')
    print('Local da ocorrência')
    estado = ler_texto_sem_numeros('  Estado')
    cidade = ler_texto_sem_numeros('  Cidade')
    bairro = ler_texto_livre('  Bairro (opcional)', obrigatorio=False)
    rua = ler_texto_livre('  Rua (opcional)', obrigatorio=False)

    data_acidente = ler_data()
    hora_acidente = ler_hora()
    nome_clima = ler_texto_sem_numeros('Clima no horário da ocorrência')
    tipo_gravidade = ler_texto_sem_numeros('Gravidade da ocorrência')
    qtd_vitimas = ler_vitimas()
    veiculos = ler_veiculos()

    try:
        local = session.query(Local).filter_by(
            estado=estado, cidade=cidade, bairro=bairro, rua=rua
        ).first()
        if local is None:
            local = Local(estado=estado, cidade=cidade, bairro=bairro, rua=rua)

        acidente = Acidente(
            local=local,
            data_acidente=data_acidente,
            hora_acidente=hora_acidente,
            nome_clima=nome_clima,
            tipo_gravidade=tipo_gravidade,
            qtd_vitimas=qtd_vitimas,
            veiculos=[Veiculo(nome_veiculo=v) for v in veiculos],
        )
        session.add(acidente)
        session.commit()
        print('\nAcidente cadastrado com sucesso.')
    except SQLAlchemyError as erro:
        session.rollback()
        print(f'\nErro ao gravar no banco: {erro}')


def exibir_quantidade_por_regiao(session):
    """RN09: quantidade de acidentes em uma região (cidade)."""
    cidade = input('\nCidade (Enter para listar todas): ').strip()
    qtd = func.count(Acidente.idacidente)

    consulta = (
        session.query(Local.estado, Local.cidade, qtd)
        .join(Acidente, Acidente.idlocal == Local.idlocal)
        .group_by(Local.estado, Local.cidade)
        .order_by(qtd.desc())
    )
    if cidade:
        consulta = consulta.filter(func.lower(Local.cidade) == cidade.lower())

    linhas = consulta.all()
    if not linhas:
        print('Nenhum acidente encontrado para essa região.')
        return
    print('\n--- Acidentes por região ---')
    for estado, nome_cidade, total in linhas:
        print(f'{nome_cidade}/{estado}: {total} acidente(s)')


def exibir_horarios_com_mais_acidentes(session):
    """RN10: ranking dos horários (por hora cheia) com mais acidentes."""
    hora = func.extract('hour', Acidente.hora_acidente)
    qtd = func.count(Acidente.idacidente)

    linhas = (
        session.query(hora, qtd)
        .group_by(hora)
        .order_by(qtd.desc(), hora)
        .all()
    )
    if not linhas:
        print('\nNenhum acidente cadastrado.')
        return
    print('\n--- Horários com mais acidentes ---')
    for posicao, (h, total) in enumerate(linhas, start=1):
        print(f'{posicao}º  {int(h):02d}:00 às {int(h):02d}:59  ->  {total} acidente(s)')


def menu():
    with Session(engine) as session:
        while True:
            print('\n===== ANÁLISE DE ACIDENTES DE TRÂNSITO =====')
            print('1 - Cadastrar acidente')
            print('2 - Quantidade de acidentes por região')
            print('3 - Horários com mais acidentes')
            print('0 - Sair')
            opcao = input('Escolha: ').strip()

            if opcao == '1':
                cadastrar_acidente(session)
            elif opcao == '2':
                exibir_quantidade_por_regiao(session)
            elif opcao == '3':
                exibir_horarios_com_mais_acidentes(session)
            elif opcao == '0':
                break
            else:
                print('Opção inválida.')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    menu()