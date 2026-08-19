"""Tela Visão Geral: cards de KPI + gráfico de volume por site."""

from flask import Blueprint, render_template, request, session

import kpis
from grafico_svg import montar_grafico_barras

bp_visao_geral = Blueprint("visao_geral", __name__)


@bp_visao_geral.route("/")
def index():
    data_solicitada = request.args.get("data")
    data_referencia = kpis.data_valida_ou_mais_recente(data_solicitada)

    cards = kpis.montar_kpis_gerais(data_referencia)
    ranking = kpis.montar_ranking_sites(data_referencia)

    grafico = montar_grafico_barras(
        rotulos=[linha["site_id"] for linha in ranking],
        valores=[linha["volume_coletado"] for linha in ranking],
        titulo_eixo_y="Volume coletado por site",
    )

    return render_template(
        "visao_geral.html",
        cards=cards,
        grafico=grafico,
        datas_disponiveis=kpis.datas_disponiveis(),
        data_referencia=data_referencia,
        nome_exibicao=session.get("nome_exibicao", ""),
    )
