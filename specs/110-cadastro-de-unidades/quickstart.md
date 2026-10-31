# Quickstart: validar o cadastro de unidades (110)

Roteiros para conferir a feature depois de implementada. Os contratos estão em
[contracts/](contracts/), o modelo em [data-model.md](data-model.md).

## Pré-requisitos

- PostgreSQL local com o par `TEST_DB_ENGINE=postgresql` e `DB_USER` (ver *As armadilhas caras* no
  `CLAUDE.md`), e um `DB_NAME` próprio desta worktree;
- `uv sync --extra dev --extra navegador` e `uv run playwright install chromium`, para a jornada;
- a `main` com a `108` e a `109`, integradas em 31/10/2026.

## Roteiro A — a suíte

```bash
cd backend && make lint check test-pg
```

Esperado: tudo passa; os testes da semente substituem os da sincronização; o teste da agenda que
movia o Edital agora o cria na outra unidade.

Isolados, os desta feature:

```bash
cd backend && PYTEST_ADDOPTS="tests/unidades tests/seguranca/test_papel_do_registro.py tests/homologacao tests/authorization/test_administrar_unidades.py tests/interface/test_isolamento_entre_unidades.py tests/integration/test_escopo_imutavel.py tests/interface/test_telas_de_unidades.py" make test-pg PYTEST_WORKERS=0
```

## Roteiro B — a jornada no navegador (SC-1041)

```bash
cd backend && PYTEST_ADDOPTS="tests/navegador/test_jornada_de_unidades.py" make test-navegador
```

Esperado: com a janela aberta, a pessoa com os dois papéis institucionais cadastra `serra`, confere a prévia,
concede o Administrador de acessos dela; a segunda pessoa concede o Gestor; a terceira cria um
Processo em `serra`. Nenhum arquivo do repositório muda (`git status` limpo ao fim).

## Roteiro C — a semente não desfaz a tela

Num banco de desenvolvimento preparado:

```bash
cd backend && make preparar
```

1. pelo shell, simular o ato da tela com um ator institucional: alterar o nome do Cefor e cadastrar
   `serra` (o teste `test_a_semente_nao_desfaz_a_tela` faz isso; aqui é para ver com os olhos);
2. `make preparar` de novo, e `docker compose restart app` no ambiente containerizado;
3. esperado: `Unidades: registro com 2 unidades; a semente não se aplica.`, a subida termina, e
   `semear_unidades --exportar` mostra o nome novo e `serra`.

## Roteiro D — o escopo não muda

```bash
cd backend && uv run python manage.py shell -c "from processo_seletivo.processos.models import Edital; Edital.objects.update(institution_scope='outra')"
```

Esperado, com algum Edital no banco: erro do banco, `the institution scope of an edital is
immutable`, e nenhum Edital muda.

## Roteiro E — a homologação continua

```bash
cd backend && uv run python manage.py seed_demo
```

Abrir `/gestao/` com `INTERFACE_SELETOR_IDENTIDADE=true`: o seletor é o de sempre, os oito papéis
funcionam, e nenhum deles vê "Unidades" na barra. `/gestao/administracao-de-unidades` responde 403,
com a recusa explicada da `033`: nenhum papel do seletor tem a permissão.

## Roteiro F — duas unidades num banco novo de homologação (D-017)

Para validar P-1 e P-3 no portal, num banco **vazio**: `semear_unidades --arquivo <arquivo com cefor
e serra>`, depois `seed_demo`. Esperado: `Unidades: 2 semeadas.`, e o portal com a moldura "Ifes".
Num banco que já tem unidade, o comando diz que a semente não se aplica e não grava nada.

## Roteiro G — validação funcional com pessoas, antes do SSO (D-017, D-018, SC-1048)

**Critério de aceite humano, e não teste automatizado.** Quem conduz é o operador; quem valida é uma
pessoa da equipe que não escreveu a feature. O ambiente é o de homologação funcional da D-018 —
**nunca** a VM de homologação do guia, que roda as settings de produção, recusa o provedor e
continua em 503 até o SSO.

1. No `backend/.env` do ambiente — que o `compose.yaml` entrega ao contêiner por `env_file`; uma
   variável exportada no *shell* não chega lá —, um `DJANGO_SECRET_KEY` gerado para ele e estas
   duas linhas:

   ```text
   INTERFACE_SELETOR_IDENTIDADE=false
   GESTAO_PROVEDOR_INSTITUCIONAL=tests.homologacao.provedor.ProvedorDeHomologacao
   ```

   e subir num banco novo:

   ```bash
   docker compose up --build
   ```

2. Cadastrar pela implantação as pessoas da validação, cada uma com o papel que o roteiro pede e o
   motivo da sessão:

   ```bash
   docker compose exec app python manage.py conceder_administracao_institucional --papel administrador-de-unidades --provedor homologacao --identificador validadora --nome "Validadora" --motivo "Validação funcional da 110"
   ```

   e, para conceder acesso à unidade nova durante o roteiro, o mesmo com o papel padrão, a outra
   identidade sintética ou à mesma (`--adicional` a partir da segunda pessoa com o mesmo papel).
   **Antes do incremento C** a opção `--papel` não existe: o ambiente serve à validação das telas
   da `107` com o papel padrão, e o roteiro das unidades espera C.
3. A pessoa abre `/gestao/`, escolhe a entrada institucional, escolhe a si mesma na página do
   provedor — que lista só as pessoas cadastradas com `--provedor homologacao` —, e segue o roteiro sem ajuda: cadastrar `serra` conferindo a prévia; editar o nome e o
   canal; desativar, lendo as consequências; reativar; abrir a ficha e ler o histórico.
4. Gerar um documento de `serra` (um Edital publicado pelo helper dos testes) e comparar o cabeçalho
   com a prévia.

Esperado: tudo feito sem ajuda (SC-1048). O que a pessoa estranhou, o que não entendeu e onde
hesitou vai ao `verificacao.md`, na seção da validação funcional — separada dos resultados da suíte
—, com a data e quem validou. Fora de `localhost`, só depois da P-6, com o perímetro da D-018.
