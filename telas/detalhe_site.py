"""Tela Detalhe por Site: tabela de ranking (volume, falta de bipagem, custo, efetivo)."""

from flask import Blueprint, render_template, request, session

import kpis

bp_detalhe_site = Blueprint("detalhe_site", __name__)


@bp_detalhe_site.route("/detalhe-site")
def index():
    data_solicitada = request.args.get("data")
    data_referencia = kpis.data_valida_ou_mais_recente(data_solicitada)

    ranking = kpis.montar_ranking_sites(data_referencia)

    return render_template(
        "detalhe_site.html",
        ranking=ranking,
        datas_disponiveis=kpis.datas_disponiveis(),
        data_referencia=data_referencia,
        nome_exibicao=session.get("nome_exibicao", ""),
    )
