"""Fixtures compartilhadas dos testes.

Cada teste roda contra um banco SQLite temporário e isolado (nunca contra
o banco de desenvolvimento em data/), garantido via monkeypatch da
variável de ambiente OPS_TOWER_DB_PATH antes de importar os módulos que
leem `config.DB_PATH`.
"""

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture()
def banco_temporario(tmp_path, monkeypatch):
    caminho_db = tmp_path / "teste_ops_control_tower.db"
    monkeypatch.setenv("OPS_TOWER_DB_PATH", str(caminho_db))

    import config
    import database

    importlib.reload(config)
    importlib.reload(database)

    database.inicializar_banco()
    return database
