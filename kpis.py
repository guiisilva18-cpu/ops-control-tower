"""Lógica de cálculo dos indicadores exibidos no painel.

Consulta o banco (SQLite por padrão) e transforma os pedidos de coleta
brutos em KPIs operacionais: volume total, percentual de falta de
bipagem, custo estimado do dia e ranking por site.
"""

from __future__ import annotations

from datetime import date

import database


def datas_disponiveis() -> list[str]:
    """Lista as datas (mais recente primeiro) que já têm carga no banco."""
    with database.conexao() as con:
        linhas = con.execute(
            "SELECT DISTINCT data FROM pedidos_coleta ORDER BY data DESC"
        ).fetchall()
    return [linha["data"] for linha in linhas]


def data_mais_recente() -> str | None:
    disponiveis = datas_disponiveis()
    return disponiveis[0] if disponiveis else None


def montar_kpis_gerais(data_referencia: str) -> dict:
    """Monta os cards de KPI da tela Visão Geral para uma data."""
    with database.conexao() as con:
        totais = con.execute(
            """
            SELECT
                COUNT(*) AS volume_total,
                SUM(CASE WHEN status = 'NAO_COLETADO' THEN 1 ELSE 0 END) AS total_falta_bipagem
            FROM pedidos_coleta
            WHERE data = ?
            """,
            (data_referencia,),
        ).fetchone()

        custo_total = con.execute(
            """
            SELECT COALESCE(SUM(s.custo_unitario_coleta), 0) AS custo
            FROM pedidos_coleta p
            JOIN sites s ON s.site_id = p.site_id
            WHERE p.data = ? AND p.status = 'COLETADO'
            """,
            (data_referencia,),
        ).fetchone()

        efetivo_total = con.execute(
            """
            SELECT COALESCE(SUM(efetivo_t1 + efetivo_t2 + efetivo_t3), 0) AS efetivo
            FROM sites
            """
        ).fetchone()

    volume_total = totais["volume_total"] or 0
    total_falta_bipagem = totais["total_falta_bipagem"] or 0
    percentual_falta_bipagem = (total_falta_bipagem / volume_total * 100) if volume_total else 0.0

    return {
        "data_referencia": data_referencia,
        "volume_total": volume_total,
        "total_falta_bipagem": total_falta_bipagem,
        "percentual_falta_bipagem": round(percentual_falta_bipagem, 1),
        "custo_do_dia": round(custo_total["custo"], 2),
        "efetivo_total": efetivo_total["efetivo"],
    }


def montar_ranking_sites(data_referencia: str) -> list[dict]:
    """Monta a tabela de ranking por site (tela Detalhe por Site)."""
    with database.conexao() as con:
        linhas = con.execute(
            """
            SELECT
                s.site_id,
                s.nome,
                s.cidade,
                s.uf,
                (s.efetivo_t1 + s.efetivo_t2 + s.efetivo_t3) AS efetivo_total,
                COUNT(p.id) AS volume_total,
                SUM(CASE WHEN p.status = 'COLETADO' THEN 1 ELSE 0 END) AS volume_coletado,
                SUM(CASE WHEN p.status = 'NAO_COLETADO' THEN 1 ELSE 0 END) AS volume_falta_bipagem,
                COALESCE(SUM(CASE WHEN p.status = 'COLETADO' THEN s.custo_unitario_coleta ELSE 0 END), 0) AS custo_estimado
            FROM sites s
            LEFT JOIN pedidos_coleta p ON p.site_id = s.site_id AND p.data = ?
            GROUP BY s.site_id
            ORDER BY volume_total DESC
            """,
            (data_referencia,),
        ).fetchall()

    ranking = []
    for linha in linhas:
        volume_total = linha["volume_total"] or 0
        volume_falta = linha["volume_falta_bipagem"] or 0
        percentual_falta = (volume_falta / volume_total * 100) if volume_total else 0.0
        ranking.append(
            {
                "site_id": linha["site_id"],
                "nome": linha["nome"],
                "cidade": linha["cidade"],
                "uf": linha["uf"],
                "efetivo_total": linha["efetivo_total"],
                "volume_total": volume_total,
                "volume_coletado": linha["volume_coletado"] or 0,
                "percentual_falta_bipagem": round(percentual_falta, 1),
                "custo_estimado": round(linha["custo_estimado"], 2),
            }
        )
    return ranking


def data_valida_ou_mais_recente(data_solicitada: str | None) -> str:
    """Resolve a data a ser exibida: usa a solicitada se existir carga,
    senão cai para a mais recente disponível, senão usa a data de hoje."""
    disponiveis = set(datas_disponiveis())
    if data_solicitada and data_solicitada in disponiveis:
        return data_solicitada
    recente = data_mais_recente()
    return recente or date.today().isoformat()
