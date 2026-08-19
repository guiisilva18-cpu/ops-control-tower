"""Orquestra o pipeline diário: gera dados sintéticos e carrega no banco.

É este script que o job agendado do GitHub Actions roda todo dia (ver
`.github/workflows/pipeline_diario.yml`), no mesmo espírito do job real que
inspirou este portfólio: raspar o portal -> normalizar -> carregar no banco,
de forma idempotente por dia.

Uso:
    python scripts/executar_pipeline.py                  # roda para hoje
    python scripts/executar_pipeline.py --data 2026-08-19 # roda para uma data específica
    python scripts/executar_pipeline.py --dias-historico 7 # popula os últimos N dias
"""

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import database  # noqa: E402
from etl.carregar_dados import carregar_pedidos_do_dia  # noqa: E402
from etl.gerar_dados_sinteticos import gerar_pedidos_do_dia  # noqa: E402


def rodar_para_data(data_referencia: date) -> int:
    pedidos_brutos = gerar_pedidos_do_dia(data_referencia)
    total_carregado = carregar_pedidos_do_dia(pedidos_brutos, data_referencia)
    print(f"[{data_referencia.isoformat()}] {total_carregado} pedidos de coleta carregados.")
    return total_carregado


def _parse_data(texto: str) -> date:
    return datetime.strptime(texto, "%Y-%m-%d").date()


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o pipeline diário (gerar + carregar) do painel.")
    parser.add_argument("--data", type=_parse_data, default=None, help="Data alvo (AAAA-MM-DD). Padrão: hoje.")
    parser.add_argument(
        "--dias-historico",
        type=int,
        default=None,
        help="Se informado, popula os últimos N dias (incluindo hoje) em vez de uma única data.",
    )
    args = parser.parse_args()

    database.inicializar_banco()

    if args.dias_historico:
        hoje = date.today()
        for offset in range(args.dias_historico - 1, -1, -1):
            rodar_para_data(hoje - timedelta(days=offset))
    else:
        rodar_para_data(args.data or date.today())


if __name__ == "__main__":
    main()
