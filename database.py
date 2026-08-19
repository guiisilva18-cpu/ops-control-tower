"""Camada de acesso ao banco SQLite.

Este projeto usa SQLite por padrão para permitir clonar e rodar sem
depender de infraestrutura externa. O padrão de carga (DELETE + INSERT por
dia) é o mesmo usado no sistema real que inspirou este portfólio: cada
execução do ETL primeiro apaga os registros do dia-alvo e depois insere os
novos, o que torna a carga idempotente (rodar duas vezes para o mesmo dia
não duplica dados).

Para evoluir este projeto para Postgres, bastaria trocar o driver
(`sqlite3` -> `psycopg`) mantendo a mesma lógica de DELETE+INSERT por dia -
o SQL abaixo já usa apenas sintaxe compatível com ambos.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

import config

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sites (
    site_id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    custo_unitario_coleta REAL NOT NULL,
    efetivo_t1 INTEGER NOT NULL DEFAULT 0,
    efetivo_t2 INTEGER NOT NULL DEFAULT 0,
    efetivo_t3 INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pedidos_coleta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    site_id TEXT NOT NULL,
    turno TEXT NOT NULL,
    hora TEXT NOT NULL,
    status TEXT NOT NULL,
    pedido_codigo TEXT NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites (site_id)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_coleta_data ON pedidos_coleta (data);
CREATE INDEX IF NOT EXISTS idx_pedidos_coleta_site ON pedidos_coleta (site_id, data);
"""


def caminho_banco() -> Path:
    caminho = Path(config.DB_PATH)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return caminho


@contextmanager
def conexao():
    """Abre uma conexão SQLite com row_factory em dict e FKs habilitadas."""
    con = sqlite3.connect(caminho_banco())
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def inicializar_banco() -> None:
    """Cria as tabelas do zero, caso ainda não existam."""
    with conexao() as con:
        con.executescript(SCHEMA_SQL)
