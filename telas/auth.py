"""Tela de login/logout.

Autenticação simples baseada em sessão, com senha verificada por hash
(nunca texto puro). Usuários e hashes vêm de `config.USUARIOS`.
"""

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

import config

bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        senha = request.form.get("senha") or ""

        cadastro = config.USUARIOS.get(usuario)
        if cadastro and check_password_hash(cadastro["senha_hash"], senha):
            session["usuario"] = usuario
            session["nome_exibicao"] = cadastro["nome_exibicao"]
            return redirect(url_for("visao_geral.index"))

        erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro, sistema_origem=config.SISTEMA_ORIGEM)


@bp_auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
