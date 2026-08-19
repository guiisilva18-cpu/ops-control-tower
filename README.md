# Torre de Controle de Operações

Painel de indicadores logísticos com pipeline diário de dados: um script simula a raspagem de um portal interno fictício de transportadora (**ConectaCarga**), carrega os pedidos de coleta num banco de forma idempotente e um dashboard Flask exibe os KPIs operacionais do dia.

> **Aviso importante:** este é um projeto de **portfólio**, com **dados 100% sintéticos e fictícios**. Nenhum nome de empresa, site, custo, usuário ou URL aqui corresponde a algo real. O projeto é inspirado na arquitetura de um sistema real que construí no trabalho (blueprints Flask por tela, `app_factory`, carga idempotente DELETE+INSERT por dia), mas todo o conteúdo - nomes, valores e credenciais - foi recriado do zero especificamente para esta demonstração pública.

## O que este projeto demonstra

- **Pipeline ETL com carga idempotente**: cada execução apaga (`DELETE`) os registros do dia-alvo antes de inserir (`INSERT`) o novo lote, então rodar o pipeline duas vezes para o mesmo dia nunca duplica dados.
- **Agendamento automático**: GitHub Actions com cron diário rodando geração + carga, no mesmo padrão do job real (raspar -> normalizar -> carregar).
- **Dashboard Flask com arquitetura modular**: uma blueprint por tela, registradas numa fábrica de aplicação (`app_factory.py`), com autenticação por sessão e senha em hash (nunca texto puro).
- **Visualização sem dependências externas**: o gráfico de barras é gerado como SVG puro no servidor - o painel funciona 100% offline, sem CDN de JavaScript.
- **Testes automatizados**: cobrindo a normalização/carga de dados (incluindo a idempotência) e as rotas HTTP do painel.

## Telas

| Tela | Rota | O que mostra |
|---|---|---|
| Login | `/login` | Autenticação simples por usuário/senha (hash) |
| Visão Geral | `/` | Cards de KPI (volume total, % falta de bipagem, custo estimado do dia, efetivo total) + gráfico de volume por site |
| Detalhe por Site | `/detalhe-site` | Tabela com ranking de sites por volume, falta de bipagem, efetivo e custo estimado |

Ambas as telas de dados têm um seletor de data no topo, que troca entre os dias já carregados no banco.

## Arquitetura

```
ops-control-tower/
├── app.py                     # ponto de entrada (roda o servidor local)
├── app_factory.py             # fábrica Flask: registra blueprints e exige login
├── config.py                  # configurações e usuários (só hash de senha)
├── database.py                # conexão SQLite e schema
├── kpis.py                    # consultas e cálculo dos indicadores
├── grafico_svg.py             # gráfico de barras em SVG puro (sem JS/CDN)
├── utils.py                   # helpers compartilhados
├── etl/
│   ├── sites_cadastro.py      # cadastro fictício de sites/pontos de coleta
│   ├── gerar_dados_sinteticos.py  # simula a "raspagem" diária do ConectaCarga
│   └── carregar_dados.py      # normalização + carga idempotente (DELETE+INSERT)
├── telas/                     # uma blueprint Flask por tela
│   ├── auth.py
│   ├── visao_geral.py
│   └── detalhe_site.py
├── templates/ e static/       # HTML (Jinja) e CSS/SVG
├── scripts/executar_pipeline.py   # orquestra gerar + carregar (usado pelo cron)
├── tests/                     # pytest (ETL + rotas Flask)
├── .github/workflows/pipeline_diario.yml  # cron diário (GitHub Actions)
└── render.yaml                # blueprint de deploy no Render (documentado, não publicado)
```

Este é o mesmo padrão arquitetural do sistema real que inspirou o projeto: cada tela do painel é uma blueprint Flask isolada, registrada numa fábrica de aplicação central, e a carga de dados segue sempre o padrão "apaga o dia, insere de novo" para ser segura contra reexecuções.

## Como rodar localmente

Pré-requisitos: Python 3.11 ou superior.

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/guiisilva18-cpu/ops-control-tower.git
cd ops-control-tower

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows (PowerShell/cmd)

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Gerar e carregar dados sintéticos (últimos 7 dias, por exemplo)
python scripts/executar_pipeline.py --dias-historico 7

# 5. Rodar o painel
python app.py
```

Acesse `http://localhost:8765`. Credenciais de demonstração:

- **Usuário:** `gestor.demo`
- **Senha:** `OpsTower2026Demo`

O banco já vem versionado no repositório com alguns dias de dados sintéticos (`data/ops_control_tower.db`), então dá pra rodar o passo 5 direto sem o passo 4, se só quiser ver o painel funcionando.

### Rodando o pipeline para uma data específica

```bash
python scripts/executar_pipeline.py --data 2026-08-19
```

Rodar o mesmo comando de novo para a mesma data não duplica os pedidos - o pipeline sempre substitui a carga do dia (`DELETE` + `INSERT`).

### Testes

```bash
pytest
```

## Banco de dados

Por padrão o projeto usa **SQLite** (`data/ops_control_tower.db`), justamente para permitir clonar e rodar sem precisar subir nenhuma infraestrutura externa. O SQL usado (`DELETE` + `INSERT` simples, sem funções específicas de dialeto) é compatível com Postgres - para evoluir o projeto bastaria trocar o driver em `database.py` (`sqlite3` por `psycopg`) mantendo a mesma lógica de carga. A variável de ambiente `OPS_TOWER_DB_PATH` permite apontar para outro caminho de arquivo, se necessário.

## Agendamento automático

O workflow `.github/workflows/pipeline_diario.yml` roda todo dia às 07:00 UTC (e também pode ser disparado manualmente pela aba **Actions** do GitHub), executando o mesmo `scripts/executar_pipeline.py` usado localmente e commitando o banco SQLite atualizado de volta no repositório - simulando o job diário do sistema real, que raspa o portal interno e carrega os dados em produção.

## Deploy

O arquivo `render.yaml` documenta como este painel poderia ser publicado no [Render](https://render.com) (serviço web Python + disco persistente para o SQLite). Ele **não está publicado de fato** neste momento - é um blueprint de referência.

## Sobre os dados fictícios

- **Sistema "raspado":** ConectaCarga (nome fictício, sem relação com nenhum sistema real).
- **Sites/pontos de coleta:** nomes genéricos inventados (`PONTO-CENTRO`, `HUB-VALE` etc.), em cidades fictícias.
- **Custos e efetivo:** valores fabricados aleatoriamente, sem relação com nenhuma operação real.
- **Usuários e senhas:** usuário de demonstração com senha em hash (`werkzeug.security.generate_password_hash`) - a senha em texto puro só aparece neste README, nunca no código.

## Licença

Este projeto está sob a licença MIT (veja [`LICENSE`](LICENSE)).
