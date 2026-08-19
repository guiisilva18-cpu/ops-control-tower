"""Pacote com uma blueprint Flask por tela do painel.

Segue o mesmo padrão do sistema real que inspirou este portfólio: cada
tela vive no seu próprio módulo com sua própria blueprint, registrada no
`app_factory.py`.
"""

from telas.auth import bp_auth
from telas.detalhe_site import bp_detalhe_site
from telas.visao_geral import bp_visao_geral

__all__ = ["bp_auth", "bp_visao_geral", "bp_detalhe_site"]
