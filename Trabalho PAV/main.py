from conexao import conexao


def escolher_opcao(pergunta, opcoes):
	while True:
		resposta = input(pergunta).strip().lower()
		if resposta in opcoes:
			return resposta
		print(f"Digite uma das opções: {', '.join(opcoes)}")


def obter_id(tabela, coluna, valor):
	"""Retorna o id existente ou cria o valor na tabela auxiliar."""
	registro = conexao.execute(
		f"SELECT rowid FROM {tabela} WHERE {coluna} = ?", (valor,)
	).fetchone()
	if registro:
		return registro[0]

	conexao.execute(f"INSERT INTO {tabela} ({coluna}) VALUES (?)", (valor,))
	return conexao.execute("SELECT last_insert_rowid()").fetchone()[0]


def inserir_acidente():
	local = input("Local do acidente: ").strip()
	horario = input("Horário do acidente: ").strip()
	clima = escolher_opcao("Clima (chuvoso ou ensolarado): ", ["chuvoso", "ensolarado"])
	veiculo = input("Veículo envolvido: ").strip()
	gravidade = escolher_opcao("Gravidade (grave ou leve): ", ["grave", "leve"])

	if not all([local, horario, veiculo]):
		print("Local, horário e veículo são obrigatórios.")
		return

	idlocal = obter_id("local", "nome_local", local)
	idhorario = obter_id("horario", "hora", horario)
	idclima = obter_id("clima", "nome_clima", clima)
	idveiculo = obter_id("veiculo", "nome_veiculo", veiculo)
	idgravidade = obter_id("gravidade", "tipo_gravidade", gravidade)

	conexao.execute(
		"""INSERT INTO acidente
		(idlocal, idhorario, idclima, idveiculo, idgravidade)
		VALUES (?, ?, ?, ?, ?)""",
		(idlocal, idhorario, idclima, idveiculo, idgravidade),
	)
	conexao.commit()
	print("Acidente salvo com sucesso.")


def buscar_por_local():
	local = input("Digite o local para buscar: ").strip()
	registros = conexao.execute(
		"""SELECT a.idacidente, l.nome_local, h.hora, c.nome_clima,
		v.nome_veiculo, g.tipo_gravidade
		FROM acidente AS a
		JOIN local AS l ON l.idlocal = a.idlocal
		JOIN horario AS h ON h.idhorario = a.idhorario
		JOIN clima AS c ON c.idclima = a.idclima
		JOIN veiculo AS v ON v.idveiculo = a.idveiculo
		JOIN gravidade AS g ON g.idgravidade = a.idgravidade
		WHERE l.nome_local LIKE ?
		ORDER BY a.idacidente""",
		(f"%{local}%",),
	).fetchall()

	if not registros:
		print("Nenhum acidente encontrado nesse local.")
		return

	for idacidente, nome_local, hora, nome_clima, nome_veiculo, gravidade in registros:
		print(
			f"\nID: {idacidente} | Local: {nome_local} | Horário: {hora} "
			f"| Clima: {nome_clima} | Veículo: {nome_veiculo} "
			f"| Gravidade: {gravidade}"
		)


try:
	while True:
		opcao = escolher_opcao(
			"\n1 - Cadastrar acidente\n2 - Buscar por local\n3 - Sair\nEscolha: ",
			["1", "2", "3"],
		)
		if opcao == "1":
			inserir_acidente()
		elif opcao == "2":
			buscar_por_local()
		else:
			break
finally:
	conexao.close()
