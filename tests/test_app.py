"""Testes de rota do painel Flask (login e telas autenticadas)."""

from datetime import date

from etl.carregar_dados import carregar_pedidos_do_dia
from etl.gerar_dados_sinteticos import gerar_pedidos_do_dia


def _popular_um_dia(data_referencia: date):
    pedidos = gerar_pedidos_do_dia(data_referencia)
    carregar_pedidos_do_dia(pedidos, data_referencia)


def _criar_cliente_app():
    from app_factory import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_login_get_retorna_200(banco_temporario):
    cliente = _criar_cliente_app()
    resposta = cliente.get("/login")
    assert resposta.status_code == 200
    assert "Torre de Controle".encode() in resposta.data or "Entrar".encode() in resposta.data


def test_rota_protegida_redireciona_sem_login(banco_temporario):
    cliente = _criar_cliente_app()
    resposta = cliente.get("/", follow_redirects=False)
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_login_com_credenciais_validas_e_acesso_as_telas(banco_temporario):
    _popular_um_dia(date(2026, 8, 19))
    cliente = _criar_cliente_app()

    resposta_login = cliente.post(
        "/login",
        data={"usuario": "gestor.demo", "senha": "OpsTower2026Demo"},
        follow_redirects=True,
    )
    assert resposta_login.status_code == 200

    resposta_visao_geral = cliente.get("/")
    assert resposta_visao_geral.status_code == 200
    assert "Volume total coletado".encode() in resposta_visao_geral.data

    resposta_detalhe = cliente.get("/detalhe-site")
    assert resposta_detalhe.status_code == 200
    assert "Detalhe por Site".encode() in resposta_detalhe.data


def test_login_com_senha_invalida_nao_autentica(banco_temporario):
    cliente = _criar_cliente_app()
    resposta = cliente.post(
        "/login",
        data={"usuario": "gestor.demo", "senha": "senha-errada"},
    )
    assert resposta.status_code == 200
    assert "inválidos".encode() in resposta.data
