"""Funções auxiliares compartilhadas entre as telas do painel."""


def usuario_logado(session) -> bool:
    """Verifica se existe um usuário autenticado na sessão Flask."""
    return bool(session.get("usuario"))
