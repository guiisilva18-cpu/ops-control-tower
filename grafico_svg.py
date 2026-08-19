"""Gráfico de barras em SVG puro, sem dependências externas.

Gerado inteiramente no servidor (sem JavaScript, sem CDN) para que o
painel funcione totalmente offline. Recebe uma lista de rótulos e valores
e devolve uma string SVG pronta para ser inserida no template (com
`| safe` no Jinja).
"""

from __future__ import annotations

LARGURA = 640
ALTURA = 260
MARGEM_INFERIOR = 60
MARGEM_SUPERIOR = 20
MARGEM_LATERAL = 20
COR_BARRA = "#3b82f6"
COR_BARRA_ALERTA = "#ef4444"


def montar_grafico_barras(
    rotulos: list[str],
    valores: list[float],
    titulo_eixo_y: str = "",
    limite_alerta: float | None = None,
) -> str:
    """Monta um gráfico de barras verticais simples em SVG.

    Se `limite_alerta` for informado, barras com valor acima dele são
    pintadas na cor de alerta (usado, por exemplo, para destacar sites com
    percentual de falta de bipagem acima do limite aceitável).
    """
    if not rotulos or not valores or len(rotulos) != len(valores):
        return "<svg></svg>"

    area_util_altura = ALTURA - MARGEM_SUPERIOR - MARGEM_INFERIOR
    area_util_largura = LARGURA - 2 * MARGEM_LATERAL
    valor_maximo = max(valores) or 1
    largura_barra = area_util_largura / len(valores)

    partes = [
        f'<svg viewBox="0 0 {LARGURA} {ALTURA}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{titulo_eixo_y}" class="grafico-svg">'
    ]

    # Linha de base do eixo X.
    y_base = ALTURA - MARGEM_INFERIOR
    partes.append(
        f'<line x1="{MARGEM_LATERAL}" y1="{y_base}" x2="{LARGURA - MARGEM_LATERAL}" '
        f'y2="{y_base}" stroke="currentColor" stroke-opacity="0.25" />'
    )

    for indice, (rotulo, valor) in enumerate(zip(rotulos, valores)):
        altura_barra = (valor / valor_maximo) * area_util_altura if valor_maximo else 0
        x = MARGEM_LATERAL + indice * largura_barra + largura_barra * 0.15
        largura_real = largura_barra * 0.7
        y = y_base - altura_barra

        cor = COR_BARRA
        if limite_alerta is not None and valor > limite_alerta:
            cor = COR_BARRA_ALERTA

        partes.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{largura_real:.1f}" height="{altura_barra:.1f}" '
            f'fill="{cor}" rx="3"><title>{rotulo}: {valor}</title></rect>'
        )
        partes.append(
            f'<text x="{x + largura_real / 2:.1f}" y="{y - 6:.1f}" font-size="11" '
            f'text-anchor="middle" fill="currentColor">{valor:g}</text>'
        )
        partes.append(
            f'<text x="{x + largura_real / 2:.1f}" y="{y_base + 16}" font-size="10" '
            f'text-anchor="middle" fill="currentColor" opacity="0.75">{rotulo}</text>'
        )

    partes.append("</svg>")
    return "".join(partes)
