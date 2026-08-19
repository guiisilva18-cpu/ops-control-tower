"""Fábrica da aplicação Flask.

Registra as blueprints de cada tela e aplica a exigência de login antes de
qualquer rota, seguindo o mesmo padrão arquitetural do sistema real que
inspirou este portfólio (app_factory + blueprints por tela).
"""

from flask import Flask, redirect, request, session, url_for

import config
from telas import bp_auth, bp_detalhe_site, bp_visao_geral
from utils import usuario_logado


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = config.SECRET_KEY

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_visao_geral)
    app.register_blueprint(bp_detalhe_site)

    @app.before_request
    def exigir_login():
        rotas_publicas = ("auth.login", "static")
        if request.endpoint in rotas_publicas:
            return None
        if not usuario_logado(session):
            return redirect(url_for("auth.login"))
        return None

    @app.context_processor
    def injetar_globais():
        return {"sistema_origem": config.SISTEMA_ORIGEM}

    return app
