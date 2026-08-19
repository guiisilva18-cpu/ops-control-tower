"""Normalização e carga dos pedidos de coleta no banco.

Segue o mesmo padrão idempotente do sistema real que inspirou este
portfólio: para cada carga, primeiro apaga (DELETE) os registros já
existentes para a data-alvo e depois insere (INSERT) o lote novo. Isso
garante que rodar o pipeline duas vezes para o mesmo dia não duplica
dados - a segunda execução apenas substitui a primeira.
"""

from __future__ import annotations

from datetime import date

import database
from etl.sites_cadastro import SITES_FICTICIOS

STATUS_VALIDOS = {"COLETADO", "NAO_COLETADO"}
CAMPOS_OBRIGATORIOS = ("data", "site_id", "turno", "hora", "status", "pedido_codigo")


class PedidoInvalidoError(ValueError):
    """Levantado quando um registro de pedido não passa na normalização."""


def normalizar_pedidos(pedidos_brutos: list[dict]) -> list[dict]:
    """Valida e normaliza uma lista de pedidos antes da carga.

    - Garante que todos os campos obrigatórios estão presentes.
    - Garante que `status` é um dos valores válidos.
    - Remove espaços em branco supérfluos de campos texto.
    - Descarta duplicatas exatas de `pedido_codigo` (mantém a primeira
      ocorrência), já que o "portal raspado" pode eventualmente repetir
      um pedido na mesma janela de coleta.
    """
    normalizados: list[dict] = []
    codigos_vistos: set[str] = set()

    for bruto in pedidos_brutos:
        faltando = [campo for campo in CAMPOS_OBRIGATORIOS if not bruto.get(campo)]
        if faltando:
            raise PedidoInvalidoError(f"Pedido sem campos obrigatórios: {faltando} -> {bruto}")

        status = str(bruto["status"]).strip().upper()
        if status not in STATUS_VALIDOS:
            raise PedidoInvalidoError(f"Status inválido: {status!r}")

        pedido_codigo = str(bruto["pedido_codigo"]).strip()
        if pedido_codigo in codigos_vistos:
            continue
        codigos_vistos.add(pedido_codigo)

        normalizados.append(
            {
                "data": str(bruto["data"]).strip(),
                "site_id": str(bruto["site_id"]).strip().upper(),
                "turno": str(bruto["turno"]).strip().upper(),
                "hora": str(bruto["hora"]).strip(),
                "status": status,
                "pedido_codigo": pedido_codigo,
            }
        )

    return normalizados


def garantir_sites_cadastrados(con) -> None:
    """Insere o cadastro fictício de sites caso a tabela esteja vazia.

    Usa INSERT OR REPLACE para que reexecuções também apliquem eventuais
    ajustes no cadastro fictício (efetivo, custo unitário etc.).
    """
    con.executemany(
        """
        INSERT OR REPLACE INTO sites
            (site_id, nome, cidade, uf, custo_unitario_coleta, efetivo_t1, efetivo_t2, efetivo_t3)
        VALUES (:site_id, :nome, :cidade, :uf, :custo_unitario_coleta, :efetivo_t1, :efetivo_t2, :efetivo_t3)
        """,
        SITES_FICTICIOS,
    )


def carregar_pedidos_do_dia(pedidos_brutos: list[dict], data_referencia: date) -> int:
    """Normaliza e carrega os pedidos de um dia, de forma idempotente.

    Retorna a quantidade de registros inseridos.
    """
    pedidos = normalizar_pedidos(pedidos_brutos)
    data_str = data_referencia.isoformat()

    with database.conexao() as con:
        garantir_sites_cadastrados(con)

        # Padrão DELETE + INSERT por dia: idempotente para reexecuções.
        con.execute("DELETE FROM pedidos_coleta WHERE data = ?", (data_str,))

        con.executemany(
            """
            INSERT INTO pedidos_coleta (data, site_id, turno, hora, status, pedido_codigo)
            VALUES (:data, :site_id, :turno, :hora, :status, :pedido_codigo)
            """,
            pedidos,
        )

    return len(pedidos)
