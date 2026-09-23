from pathlib import Path
import sqlite3

CAMINHO_BANCO = Path(__file__).parent / "Acidentes"

conexao = sqlite3.connect(CAMINHO_BANCO)
cursor = conexao.cursor()

print(cursor.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table'"
).fetchall())