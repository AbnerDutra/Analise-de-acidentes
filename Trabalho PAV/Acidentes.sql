-- Criação da tabela 'local'
CREATE TABLE local (
    idlocal INTEGER PRIMARY KEY,
    nome_local TEXT NOT NULL
);
 
-- Criação da tabela 'horario'
CREATE TABLE horario (
    idhorario INTEGER PRIMARY KEY,
    hora REAL NOT NULL
);
 
-- Criação da tabela 'clima'
CREATE TABLE clima (
    idclima INTEGER PRIMARY KEY, 
    nome_clima TEXT NOT NULL
);
 
-- Criação da tabela 'veiculo'
CREATE TABLE veiculo (
    idveiculo INTEGER PRIMARY KEY,
    nome_veiculo TEXT NOT NULL
);
 
-- Criação da tabela 'gravidade'
CREATE TABLE gravidade (
    idgravidade INTEGER PRIMARY KEY,
    tipo_gravidade TEXT NOT NULL
);
 
-- Criação da tabela central 'acidente' para relacionar as tabelas
CREATE TABLE acidente (
    idacidente INTEGER PRIMARY KEY,
    idlocal INTEGER NOT NULL,
    idhorario INTEGER NOT NULL,
    idclima INTEGER NOT NULL,
    idveiculo INTEGER NOT NULL,
    idgravidade INTEGER NOT NULL,
    FOREIGN KEY (idlocal) REFERENCES local (idlocal),
    FOREIGN KEY (idhorario) REFERENCES horario (idhorario),
    FOREIGN KEY (idclima) REFERENCES clima (idclima),
    FOREIGN KEY (idveiculo) REFERENCES veiculo (idveiculo),
    FOREIGN KEY (idgravidade) REFERENCES gravidade (idgravidade)
);