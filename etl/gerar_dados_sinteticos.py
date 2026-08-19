"""Gerador de dados sintéticos.

Simula o que a "raspagem" diária do portal interno fictício ConectaCarga
traria: um lote de pedidos de coleta por site, turno e horário, cada um
marcado como coletado ou não (falta de bipagem). Nenhum dado aqui vem de
sistema real - tudo é fabricado com `random` a partir do cadastro fictício
de sites em `etl/sites_cadastro.py`.

Uso via linha de comando:
    python -m etl.gerar_dados_sinteticos --data 2026-08-19
"""

import argparse
import random
from datetime import date, datetime

from etl.sites_cadastro import SITES_FICTICIOS

TURNOS = ("T1", "T2", "T3")

# Janela de horário aproximada de cada turno, só para gerar um valor de
# hora plausível no pedido sintético.
JANELA_TURNO = {
    "T1": (6, 14),
    "T2": (14, 22),
    "T3": (22, 30),  # 30 = 06h do dia seguinte, tratado com módulo 24 abaixo
}


def _hora_aleatoria(turno: str, rng: random.Random) -> str:
    inicio, fim = JANELA_TURNO[turno]
    minuto_total = rng.randint(inicio * 60, fim * 60 - 1)
    hora = (minuto_total // 60) % 24
    minuto = minuto_total % 60
    return f"{hora:02d}:{minuto:02d}"


def gerar_pedidos_do_dia(data_referencia: date, semente: int | None = None) -> list[dict]:
    """Fabrica a lista de pedidos de coleta fictícios para uma data.

    Cada site gera um volume aleatório de pedidos por turno, com uma taxa
    de falta de bipagem também aleatória (entre 5% e 22%), pra simular
    variação operacional real entre sites e dias.
    """
    rng = random.Random(semente if semente is not None else f"{data_referencia.isoformat()}")
    pedidos: list[dict] = []
    sequencial = 1

    for site in SITES_FICTICIOS:
        for turno in TURNOS:
            volume_turno = rng.randint(25, 90)
            taxa_falta_bipagem = rng.uniform(0.05, 0.22)

            for _ in range(volume_turno):
                nao_coletado = rng.random() < taxa_falta_bipagem
                pedido = {
                    "data": data_referencia.isoformat(),
                    "site_id": site["site_id"],
                    "turno": turno,
                    "hora": _hora_aleatoria(turno, rng),
                    "status": "NAO_COLETADO" if nao_coletado else "COLETADO",
                    "pedido_codigo": f"CC-{data_referencia.strftime('%Y%m%d')}-{sequencial:05d}",
                }
                pedidos.append(pedido)
                sequencial += 1

    return pedidos


def _parse_data(texto: str) -> date:
    return datetime.strptime(texto, "%Y-%m-%d").date()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera pedidos de coleta sintéticos simulando a raspagem diária do ConectaCarga."
    )
    parser.add_argument(
        "--data",
        type=_parse_data,
        default=date.today(),
        help="Data de referência no formato AAAA-MM-DD (padrão: hoje).",
    )
    args = parser.parse_args()

    pedidos = gerar_pedidos_do_dia(args.data)
    print(f"Gerados {len(pedidos)} pedidos de coleta sintéticos para {args.data.isoformat()}.")


if __name__ == "__main__":
    main()
