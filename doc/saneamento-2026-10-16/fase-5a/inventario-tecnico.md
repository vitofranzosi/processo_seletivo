# Inventário técnico — observação local e requisitos

Inspeção não destrutiva de 16/10/2026. Valores de segredos não foram consultados ou exibidos.

## Versões e disponibilidade

| Recurso | Requisito/fonte | Observado localmente | Limite |
|---|---|---|---|
| Python | `backend/pyproject.toml`: >=3.13,<3.14; Dockerfile Python 3.13 slim | `backend/.venv/Scripts/python.exe --version`: 3.13.15 | Não prova imagem reprodutível |
| Django | pyproject: >=5.2,<5.3 | Metadado instalado: 5.2.17 | Sem carregar settings ou banco |
| psycopg | pyproject: >=3.2,<3.4 | 3.3.4 | Sem conexão PostgreSQL |
| pytest | pyproject: >=8.4,<9, pytest-django e cobertura no extra dev | 8.4.2 | Nenhum teste executado nesta fase |
| PostgreSQL servidor | Compose/CI: 18 | Não conectado ou verificado | Serviço local ou imagem disponível não presumidos |
| psql/pg_dump | Ferramentas cliente encontradas em instalação PostgreSQL 17 | Ambos 17.7 | Não é versão de servidor; preparar cliente da versão alvo para dump/restore |
| Docker CLI | Encontrado via Rancher Desktop | 29.6.2-rd, build ede120b | Não é prova de daemon, VM, recursos ou privilégios |
| Docker Compose | Plugin disponível | v5.3.1 | Nenhum projeto consultado/iniciado |
| uv | Gerência de dependências | 0.12.13 | Dockerfile copia uv 0.9, divergência de ferramenta a fixar no manifesto |
| Arquivos de evidência | PowerShell, hashes, JSON e scripts de carga; XLSX por openpyxl | Fontes presentes | Ferramentas de navegador não foram instaladas ou executadas |

Comandos executados: `docker --version`, `docker compose version`, `psql --version`,
`pg_dump --version`, `uv --version`, Python `--version` e `importlib.metadata.version` dos três
pacotes. Sem `docker info/ps/inspect`, `psql` conectado ou dump. Não listar ambientes ou valores secretos.

## Banco, settings e variáveis

[base.py](../../../backend/config/settings/base.py): PostgreSQL por padrão; nome padrão
`processo_seletivo`, host localhost, porta 5432. Esses são **defaults de código**, não configuração
real descoberta. `DB_ROLE` seleciona migration/runtime; `DB_RUNTIME_USER` ou `DB_MIGRATION_USER`
prevalece sobre `DB_USER`; senhas respectivas prevalecem sobre `DB_PASSWORD`.

[test.py](../../../backend/config/settings/test.py): sem `TEST_DB_ENGINE=postgresql`, usa SQLite
em memória. Apenas essa variável não basta se as credenciais restantes não forem corretas; role
runtime não cria banco de teste. Django pode criar nome prefixado `test_`, aplicar migrations e
limpar tabelas. Nenhum teste persistente está autorizado por esta inspeção.

[development.py](../../../backend/config/settings/development.py) liga fonte de sorteio de
demonstração e avisos por módulo. Portanto propor `AVISOS_AOS_CANDIDATOS=false` só no ambiente não
garante desligamento no development. O controle de não entrega precisa ser backend/rede locais.
O seletor de identidade exige `INTERFACE_SELETOR_IDENTIDADE=true` para jornada da gestão; isso
deixa declarar identidades e só é aceitável no ambiente local controlado.

Famílias de configuração a preencher independentemente: `DJANGO_SETTINGS_MODULE`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`; `POSTGRES_*`, `DB_ROLE`, `DB_NAME`, `DB_HOST`, `DB_PORT`,
`DB_RUNTIME_*`, `DB_MIGRATION_*`; `DJANGO_EMAIL_BACKEND`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`;
`ARQUIVOS_CANDIDATOS_RAIZ`; `SORTEIO_FONTE_DE_DEMONSTRACAO`; `ASSISTENTE_PILOTO`,
`ASSISTENTE_SERVICO`, `ASSISTENTE_NA_PAGINA_DO_EDITAL` e demais caminhos do assistente.
Nenhum valor carregado foi inspecionado. Não usar dump irrestrito de `env`, settings ou Compose config.

O projeto não lê `.env` automaticamente em `manage.py`. [Makefile](../../../backend/Makefile)
inclui `.env` e exporta valores, salvo `EM_CONTAINER`; Compose usa `env_file`. Uma execução nativa
fora do Make depende do ambiente exportado; não se pode presumir que copia de exemplo o configure.

## Containers e inicialização existentes

[compose.yaml](../../../compose.yaml): `db` postgres:18, app e correio Mailpit `latest`; volumes
de banco/documentos, porta app 8000 e Mailpit 8025 sem restrição explícita a loopback. Monta backend
do workspace para desenvolvimento. Não foi identificado nele isolamento equivalente ao plano F4.

[Dockerfile](../../../Dockerfile): Python 3.13, uv 0.9, extra dev pelo lock; não instala extra assistente
por padrão. Build faz apt/dependências, exige aquisição de artefatos/rede. Entry point
[entrypoint.sh](../../../scripts/docker/entrypoint.sh) provisiona, migra, provisiona novamente,
sincroniza unidades e só então executa comando. Logo `compose run app ...` sem sobrescrever
entrypoint também pode gravar esquema. Não usar como simples consulta antes da autorização.

`make preparar`: mesma ordem de provisionamento/migrations e unidades; `make test-pg`: pytest com
usuário PostgreSQL elevado para criar teste; `seed`: chama `seed_demo`. Nenhum desses alvos é
inspeção pura. A segunda provisão é necessária às proteções das tabelas novas, não redundância.

## Dados sintéticos, testes e coleta

[seed_demo.py](../../../backend/processo_seletivo/processos/management/commands/seed_demo.py)
usa comandos normativos e atores distintos, cria demonstração navegável com atos e trilha. Possui
opções `--codigo`, `--numero`, `--titulo`, `--ano`, `--janela-recursal`; demais opções devem ser
conferidas na fonte antes do manifesto final. Emprega relógio sintético e autoridades/escopo Cefor;
é carga persistente, não fixture sem escrita. Número/IDs têm formato específico: não usar texto
arbitrário ou repetir carga para “limpar”. Idempotência integral não foi comprovada nesta inspeção.

Fixtures em `backend/tests/fixtures/`: seleção/publicação, autoridades, candidato, sorteio,
resultado, recursos, requerimento, matrículas e legado. Permitem planejar cenários positivos e
negativos; helpers não são comandos de produção nem baseline completa pronta. Não copiar fixture
para um shell apontado a banco existente. Ver [baseline planejada](baseline-planejada.md).

[CI](../../../.github/workflows/backend.yml) usa PostgreSQL 18, `uv sync --extra dev --extra assistente
--locked`, Ruff check/format e pytest. O lock existe; não houve resolução/download aqui. Grupos
opcionais não autorizam inferência: assistente pode ficar desabilitado nos cenários propostos.

Coleta: JSON/capturas sanitizadas, hash SHA-256 de arquivos, trilha, respostas HTTP e XLSX sintético.
Scripts `backend/scripts/carga_publica.py`/`carga_do_assistente.py` não estão autorizados: geram carga
ou podem atingir serviço. `filme-de-lancamento/producao/capture.py` importa Playwright, mas não foi
demonstrada ferramenta E2E completa instalada/configurada para homologação. Captura manual é opção
a pactuar; não executar scripts de filmagem contra URLs preexistentes.

## Serviços externos

Correio real, OpenRouter/Ollama, fonte externa de sorteio e carga externa de CEP devem permanecer
sem acesso na execução proposta. Fonte de demonstração do sorteio já existe. Mailpit local pode
capturar OTP sintético, se autorizado e isolado; console também evita entrega, mas expõe código
no log e exige controle de acesso. CSV/CEP sintético de fixture pode atender casos selecionados;
não baixar base real para preparar homologação por conveniência.
