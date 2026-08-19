"""Configurações centrais do painel.

Todas as credenciais aqui são fictícias e servem apenas para demonstração
deste portfólio. As senhas nunca ficam em texto puro no código-fonte -
apenas o hash (gerado com `werkzeug.security.generate_password_hash`) é
versionado. As senhas de demonstração estão documentadas no README.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Caminho do banco SQLite usado por padrão (clone-and-run, sem infra externa).
# Pode ser sobrescrito por variável de ambiente para apontar pra Postgres via
# um driver compatível, se o usuário quiser evoluir o projeto.
DB_PATH = os.environ.get("OPS_TOWER_DB_PATH", str(BASE_DIR / "data" / "ops_control_tower.db"))

# Chave de sessão do Flask. Em produção deve vir de variável de ambiente.
SECRET_KEY = os.environ.get("OPS_TOWER_SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")

# Nome fictício do sistema interno da transportadora que o ETL simula
# "raspar" todo dia (ver etl/gerar_dados_sinteticos.py). Não corresponde a
# nenhum sistema real.
SISTEMA_ORIGEM = "ConectaCarga"

# Usuários de demonstração do painel. A senha em texto puro NUNCA é
# armazenada aqui - apenas o hash. As credenciais de demonstração (usuário e
# senha em texto puro) estão documentadas no README para quem for testar
# localmente.
#
# Hashes gerados com:
#   from werkzeug.security import generate_password_hash
#   generate_password_hash("senha-aqui")
USUARIOS = {
    "gestor.demo": {
        "senha_hash": "scrypt:32768:8:1$5O9InSQCbwutY3vc$96b8a1e52e0258b955772fefd5b843aef1562beb66514c5b3b8d0dbf4b4e4e8"
                       "e5aa91abd7fac847b6862fb7ba01466fc5e05a36edf070fcc4dbbd43f7cc47e8c",
        "nome_exibicao": "Gestor(a) de Operações (demo)",
    },
}
