"""Ponto de entrada da aplicação.

Uso local:
    python app.py

Em produção (Render ou similar), o `render.yaml` aponta para um servidor
WSGI de produção (gunicorn) usando o objeto `app` exportado aqui.
"""

import database
from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    database.inicializar_banco()
    app.run(host="0.0.0.0", port=8765, debug=True)
