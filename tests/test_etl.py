"""Testes da normalização e carga (garantindo idempotência DELETE+INSERT)."""

from datetime import date

import pytest

from etl.carregar_dados import (
    PedidoInvalidoError,
    carregar_pedidos_do_dia,
    normalizar_pedidos,
)
from etl.gerar_dados_sinteticos import gerar_pedidos_do_dia


def test_normalizar_pedidos_valida_status():
    pedidos = [
        {
            "data": "2026-08-19",
            "site_id": "ponto-centro",
            "turno": "t1",
            "hora": "08:00",
            "status": "coletado",
            "pedido_codigo": "CC-1",
        }
    ]
    normalizados = normalizar_pedidos(pedidos)
    assert normalizados[0]["status"] == "COLETADO"
    assert normalizados[0]["site_id"] == "PONTO-CENTRO"


def test_normalizar_pedidos_rejeita_status_invalido():
    pedidos = [
        {
            "data": "2026-08-19",
            "site_id": "PONTO-CENTRO",
            "turno": "T1",
            "hora": "08:00",
            "status": "PENDENTE",
            "pedido_codigo": "CC-1",
        }
    ]
    with pytest.raises(PedidoInvalidoError):
        normalizar_pedidos(pedidos)


def test_normalizar_pedidos_remove_duplicata_de_codigo():
    pedidos = [
        {
            "data": "2026-08-19", "site_id": "PONTO-CENTRO", "turno": "T1",
            "hora": "08:00", "status": "COLETADO", "pedido_codigo": "CC-1",
        },
        {
            "data": "2026-08-19", "site_id": "PONTO-CENTRO", "turno": "T1",
            "hora": "08:05", "status": "NAO_COLETADO", "pedido_codigo": "CC-1",
        },
    ]
    normalizados = normalizar_pedidos(pedidos)
    assert len(normalizados) == 1


def test_normalizar_pedidos_rejeita_campo_faltando():
    pedidos = [{"data": "2026-08-19", "site_id": "PONTO-CENTRO", "turno": "T1", "hora": "08:00", "status": "COLETADO"}]
    with pytest.raises(PedidoInvalidoError):
        normalizar_pedidos(pedidos)


def test_gerador_produz_pedidos_para_todos_os_sites():
    data_referencia = date(2026, 8, 19)
    pedidos = gerar_pedidos_do_dia(data_referencia)
    assert len(pedidos) > 0
    sites_gerados = {p["site_id"] for p in pedidos}
    assert "PONTO-CENTRO" in sites_gerados
    assert all(p["status"] in ("COLETADO", "NAO_COLETADO") for p in pedidos)


def test_carga_e_idempotente_para_o_mesmo_dia(banco_temporario):
    data_referencia = date(2026, 8, 19)
    pedidos = gerar_pedidos_do_dia(data_referencia)

    total_primeira_carga = carregar_pedidos_do_dia(pedidos, data_referencia)
    total_segunda_carga = carregar_pedidos_do_dia(pedidos, data_referencia)

    assert total_primeira_carga == total_segunda_carga

    with banco_temporario.conexao() as con:
        linha = con.execute(
            "SELECT COUNT(*) AS total FROM pedidos_coleta WHERE data = ?",
            (data_referencia.isoformat(),),
        ).fetchone()

    # Mesmo rodando a carga duas vezes para o mesmo dia, o total no banco
    # deve ser igual ao total normalizado de uma única carga - sem duplicar.
    assert linha["total"] == total_primeira_carga


def test_carga_de_dias_diferentes_nao_se_apaga(banco_temporario):
    dia_1 = date(2026, 8, 18)
    dia_2 = date(2026, 8, 19)

    carregar_pedidos_do_dia(gerar_pedidos_do_dia(dia_1), dia_1)
    carregar_pedidos_do_dia(gerar_pedidos_do_dia(dia_2), dia_2)

    with banco_temporario.conexao() as con:
        total = con.execute("SELECT COUNT(*) AS total FROM pedidos_coleta").fetchone()["total"]
        total_dia_1 = con.execute(
            "SELECT COUNT(*) AS total FROM pedidos_coleta WHERE data = ?", (dia_1.isoformat(),)
        ).fetchone()["total"]

    assert total_dia_1 > 0
    assert total > total_dia_1  # os dois dias coexistem no banco
