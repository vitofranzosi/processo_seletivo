# Entrega 4 — Protótipos navegáveis

## O que são
O protótipo é Django de verdade, servido por um `runserver` próprio do estudo. Ele lê o banco dos
cenários de treinamento pelas mesmas funções do detalhe do Edital, como `andamento.do_edital`,
`acoes.do_edital`, `atos_retificacao.em_curso` e `Alcance.de`, e mostra o resultado com o layout
proposto, sobre a moldura, os tokens e as folhas da gestão.

**Nada disto está no código de produção.** As configurações, as rotas, as vistas, os templates e a
folha moram em [`prototipo/`](prototipo/), e o servidor os acrescenta em tempo de execução:
- `configuracao_do_prototipo.py` estende `config.settings.development`;
- `rotas_do_prototipo.py` monta `/gestao/prototipo-centro/` à frente das rotas do sistema.

| Arquivo | Papel |
|---|---|
| `prototipo/centro.py` | A composição: macrofases, agregação pura, roteiro, "agora nesta lista", conceitos |
| `prototipo/vistas_do_prototipo.py` | Índice, Centro de Controle do Edital, Processo agregado e a fixture "concluída" |
| `prototipo/templates/prototipo/*.html` | As quatro telas |
| `prototipo/static/prototipo/centro.css` | A folha, só com os tokens de `shared/tokens.css` |
| `prototipo/servidor.py` | O runserver do estudo |
| `prototipo/capturar.py`, `roteiro-*.json` | As capturas por Playwright, por identidade e largura, que acusam rolagem horizontal e violação de CSP |
| `prototipo/validar.py` | As tarefas medidas na tela atual e na proposta |

## Como rodar

O banco é próprio. Os cenários **não** são os da homologação: são os mesmos geradores (134), rodada 1,
num PostgreSQL local. Nada na homologação foi tocado.

```bash
export LC_ALL=pt_BR.UTF-8
createdb ps_cc_centro
```

```bash
cd backend && export DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_cc_centro DB_USER=$USER DB_RUNTIME_USER=$USER
```

```bash
uv run python manage.py migrate && uv run python manage.py semear_unidades
```

O gerador recusa unidade sem autoridade já usada. Num banco novo, crie uma autoridade fictícia e
passe-a por extenso:

```bash
uv run python manage.py shell -c "from datetime import date; from django.utils import timezone; from processo_seletivo.unidades.models import AutoridadeHabilitada as A, Unidade as U; print(A.objects.create(unidade=U.objects.get(), cargo='Diretor-Geral (fictício)', nome='Autoridade Fictícia', inicio_vigencia=date(2026,1,1), cadastrada_por='estudo', cadastrada_em=timezone.now()).pk)"
```

```bash
CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco ps_cc_centro --autoridade <pk impresso acima>
```

Para servir, use a entrada `centro-de-controle` do `.claude/launch.json` (porta 8150), ou:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_cc_centro DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python ../doc/estudo-centro-de-controle-2026-11-09/prototipo/servidor.py 8150
```

Abra <http://localhost:8150/gestao/prototipo-centro/>. A gestão pede identificação: escolha uma
identidade no seletor de demonstração.

O índice liga, para cada cenário, o **Centro de Controle proposto**, a **tela atual do Edital**, o
**Processo proposto** e a **tela atual do Processo**. Troque de identidade para ver o mesmo Edital com
outras permissões:
- `treino.presidencia`;
- `treino.avaliacao1`;
- "Nome na auditoria" `treino.gestao` com o papel Gestor;
- `treino.publicacao` com o papel Publicador.

As capturas se refazem com o servidor no ar:

```bash
cd backend && uv run python ../doc/estudo-centro-de-controle-2026-11-09/prototipo/capturar.py ../doc/estudo-centro-de-controle-2026-11-09/prototipo/roteiro-proposta.json
```

## Os cinco cenários pedidos

| # | Situação pedida | Fonte | Atual | Proposta |
|---|---|---|---|---|
| 1 | Sorteio em preparação, antes do congelamento | **C06, real** | `atual-c06-edital.png` | `proposta-c06.png`, `proposta-c06-dobra.png`, `proposta-c06-fase-avaliacao.png`, `proposta-c06-entenda-aberto.png` |
| 2 | Pontuação com operações parcialmente concluídas | **C04, real**: Etapas feitas, ordem a emitir. O C08 e o C12 mostram a ordem em 1 de 2 listas | `atual-c04-edital.png` | `proposta-c04.png` |
| 3 | Resultado ou recurso em andamento | **C08, real**: preliminar publicado, prazo recursal até 14/11 | `atual-c08-edital.png` | `proposta-c08.png`, `proposta-c08-fase-resultado.png`, `proposta-c08-publicador.png` |
| 4 | Convocação e conferência, com ações e esperas | **C12, real**; também o C11 (entrega com pendência) | `atual-c12-edital.png`, `atual-c12-matriz-aberta.png`, `atual-c12-processo.png` | `proposta-c12.png`, `proposta-c12-dobra.png`, `proposta-c12-fase-vagas.png`, `proposta-c12-processo.png`, `proposta-c11.png` |
| 5 | Seleção concluída, sem providências | **Fixture**, dita na tela: nenhum cenário termina concluído | — | `proposta-c05-concluida-fixture.png` |

**Real e ilustrativo não se misturam.** A fixture do cenário 5 é montada inteira no protótipo
(`_fixture_concluida`), com Edital `FIX05/2026`, e a página abre com a faixa "Ilustração (fixture)".
Nenhuma página de cenário real recebe dado fictício.

## O que cada protótipo demonstra

| Pedido | Onde ver |
|---|---|
| Visão inicial | `proposta-c06-dobra.png`, `proposta-c12-dobra.png` (primeira dobra a 1440 × 900) |
| Detalhe da fase atual | Painel à direita. Roteiro Relação → Semente → Sorteio no C06; Corte → Análise documental → Apuração em `proposta-c12-fase-vagas.png` |
| Detalhe por lista | "Onde cada lista está"; no C12, a ampla convoca enquanto a PPP espera a ordem |
| Providências disponíveis | "Suas ações disponíveis" (C06, C12); "Sua próxima ação" quando é uma só (C08) |
| Bloqueios e explicações | Semente *Depois*, "nenhuma relação deste marco está congelada" (C06); "Quem resolve" nos impedidos |
| Ações em espera | "Esperando um prazo, uma resposta ou uma correção" (C08, C12), com data e marca "recomendação" |
| Fases concluídas | Cartões ✓; "ver o ato" nas células feitas (C12) |
| Próximas fases | Cartões "Ainda não", com a razão no detalhe da fase |
| Navegação às operações | Link de cada providência e célula; "Telas do marco"; Administração |
| Microtextos pedagógicos | "Entenda: …" em cada providência e no detalhe da fase (`proposta-c06-entenda-aberto.png`) |
| Permissões diferentes | `proposta-c06-gestor.png`, `proposta-c06-avaliacao1.png` (sem detalhe por lista, como na 127), `proposta-c08-publicador.png` ("Você publica resultados") |
| Várias listas e providências | Todos os cenários têm duas listas; o C12 tem 4 providências em 4 fases |
| Celular (390 px) | `proposta-c06-celular.png`, `proposta-c12-celular.png`, contra `atual-c06-celular.png` e `atual-c12-celular.png`: a trilha vira lista vertical, e as tabelas rolam na própria moldura |
| Processo agregado | `proposta-c12-processo.png`, contra `atual-c12-processo.png` |

## Verificações feitas no navegador
- **23 capturas por Playwright** (Chromium sem janela), a 1440 e a 390 px, com cinco identidades:
  - **nenhuma rolagem horizontal** da página;
  - **nenhuma violação de CSP** no console: o protótipo segue a regra da 091/092, sem `style=` nem
    `<script>`.
- **Teclado.** A ordem do Tab percorre os oito cartões da jornada, "Como ler a jornada" e as
  providências na ordem visual. O foco tem contorno visível (`:focus-visible`).
  Ver [validacao-automatizada.txt](validacao-automatizada.txt).
- **Erros encontrados e corrigidos durante a validação** (registrados porque são o tipo de defeito que
  a implementação vai encontrar):
  1. O detalhe por lista aparecia para quem não `ve_a_matriz`: avaliação e Publicador. Corrigido para
     a regra da 127.
  2. A primeira versão empurrava "O que fazer agora" para **abaixo da dobra**: a próxima ação do C06
     ficava a 1009 px, contra a primeira dobra na tela atual. Compactar o topo resolveu: ver a avaliação.
  3. "Agora nesta lista" mostrava a Etapa paralela no lugar do sorteio. Passou a listar um ato por fase.
