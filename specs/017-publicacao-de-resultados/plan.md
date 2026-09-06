# Implementation Plan: Publicação de Resultados

**Branch**: `claude/spec-017-publicacao-resultados-605ce0` | **Date**: 2026-09-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-publicacao-de-resultados/spec.md`

## Summary

A 015 entregou o ato de ordenação: imutável, sucedível, reproduzível e invisível para quem não
administra o certame. A 017 acrescenta o segundo ato — a divulgação — e com ele a página pública, o
documento oficial e a primeira informação de resultado que chega ao candidato.

**Esta é uma feature pequena, e é pequena por três verificações no código, não por otimismo.**

1. **A forma do ato já existe, inteira.** `AtoDeOrdenacao` resolveu append-only, sucessão sem coluna
   de vigência e unicidade da raiz e do sucessor (`classificacao/models.py:44-61`). A publicação é a
   mesma forma sobre outro objeto: duas constraints, `save`/`delete` que recusam, e a tabela na
   política de privilégios. Não há desenho a inventar — há um padrão a repetir (T-002).
2. **A obsolescência já é aferível.** `estado_do_marco` devolve `vigente`, `obsoleto`,
   `recomputavel` e as `divergencias` (`classificacao/application/selectors.py:52-116`), e trata o
   marco removido por Retificação sem exceção especial. As três formas de impedimento da FR-004 são
   leitura desse retorno, não regra nova (T-004).
3. **O documento já tem as duas metades.** `Composicao` acumula e `render_documento` pagina
   (`publicacoes/infrastructure/pdf.py:1899`), e a costura já sustenta **dois** documentos — o
   Edital e o comprovante de inscrição (`inscricoes/infrastructure/comprovante_pdf.py:67`). O
   terceiro entra pelo mesmo lugar, com `_tabela` para a lista. Nada de biblioteca nova (T-007).

E uma quarta, que chegou depois da spec e mudou o tamanho do S4: a correção de E2E15-004/005/008
ensinou o renderizador a resolver `stageId` e `factId` para nome publicado e fixou a política do
alvo irresolvível — dizer a lacuna, nunca imprimir identificador. O vocabulário institucional que a
FR-012 exige **já está escrito**, e no arquivo certo.

**A decisão que mais determina o desenho** é o que a publicação persiste. Ela não guarda ponteiro
para o ato e compõe na leitura: guarda o **conteúdo divulgado**, em bytes canônicos com resumo
(T-003). Não é por causa dos rótulos — `VersaoConsolidada` é append-only e os rótulos já são
estáveis. É por causa da **projeção**: quem entra na lista, o que de cada linha atravessa a
fronteira, como o empate é dito. Essas são decisões desta feature, e uma correção futura numa delas
reescreveria em silêncio tudo o que já foi divulgado. Congelar a projeção é o que faz a I-005
verdadeira e o que dá à SC-004 um hash para conferir.

**A decisão que mais economiza** é a consequência dela: a página pública lê **um registro** e nada
mais. Não toca `Inscricao`, `PosicaoNaOrdem` nem `VersaoConsolidada` — a superfície pública do
sistema deixa de ter caminho de leitura para as tabelas que guardam dado pessoal, em vez de ter um
caminho que se confia estar filtrado (T-013).

**A que mais exigiu cuidado** é a tensão entre a FR-017 e a FR-058: quem não recebeu posição não é
nomeado publicamente, mas é informado na própria Área. Resolver isso lendo `PosicaoNaOrdem` criaria
a segunda fonte de verdade que a FR-056 proíbe. O snapshot publicado passa a ter duas faces — a
lista pública e o índice individual —, ambas congeladas no mesmo ato, e a página pública renderiza
só a primeira (T-010).

**O que não aparece no diagrama e custa** é a política de privilégios: tabela append-only nova
significa entrada em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:26-48`), triggers nomeadas em
`TRIGGERS_POR_APP` e o app novo em `APPS` (`tests/migrations/test_migrations.py:17-38`). Três
registros fora do app, e o teste estrutural não enxerga o que não foi registrado (T-011).

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova, e nenhuma rota de API
nova.** Os três canais desta feature já existem: `interface` (HTML administrativo) para publicar e
consultar o histórico, `portal` (HTML público, sem autenticação) para a página do resultado e para a
Área do Candidato, e o mesmo `HttpResponse` com `ETag` que `PublishedDocumentView` já usa para
entregar bytes de documento (`publicacoes/api/views.py:120-133`). O `openapi.yaml` da 001 **não**
muda: nada aqui é contrato de API.

**Storage**: PostgreSQL. **Uma migration**, no app novo `divulgacao`: duas tabelas — a publicação e
seu documento —, duas constraints de cadeia — raiz única por marco e sucessor único — e duas
triggers append-only, absolutas, sem a condicionalidade que `Retificacao` exige. Nenhuma migration
em `classificacao`, `resultados`, `editais` ou `publicacoes`: a FR-068 é exatamente isso dito como
requisito, e a feature inteira **lê** os agregados existentes.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. Quatro exigências específicas: as duas constraints de
cadeia sob concorrência e as duas triggers só são exercidas com `TEST_DB_ENGINE=postgresql`; os nomes
das triggers entram em `TRIGGERS_POR_APP` e o app em `APPS`
(`tests/migrations/test_migrations.py:17-38`); as tabelas entram em `TABELAS_APPEND_ONLY`
(`seguranca/papeis.py:26-48`); e a varredura de vocabulário da 013
(`tests/test_vocabulario_do_resultado.py`) hoje só lê `interface/templates` — os templates do
`portal` desta feature afirmam classificação legitimamente, e a varredura **não** deve ser estendida
a eles.

**Target Platform**: servidor Linux; navegador institucional e celular. A página pública é a
superfície mais exposta que o produto ganhou desde a vitrine, e a FR-049 dá 375 px sem rolagem
horizontal com listas que podem passar de mil linhas.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: a página pública responde com **uma** consulta ao registro da publicação e
nenhuma junção — o conteúdo já está composto e canonizado (T-003). O alvo é derivada zero: o custo
da página não varia entre 10 e 1.000 posições, e é isso que o teste mede, no molde de
`tests/performance/test_public_queries.py`. A composição do conteúdo, essa sim proporcional ao
universo, acontece **uma vez**, dentro do comando de publicar.

**Constraints**: publicar exige reproduzir o estado classificatório para aferir publicabilidade
(D-001), e essa reprodução tem o custo de `calcular_ordem` — o mesmo que a tela do marco da 015 já
paga ao abrir. A prévia e a confirmação pagam-no duas vezes, e é deliberado: é o que fecha a janela
entre ler e confirmar.

**Scale/Scope**: um Edital com mil inscritos e até três marcos por Perfil. **Um app novo, duas
tabelas, uma migration, uma capacidade nova no mapa de papéis, três rotas administrativas, duas
rotas públicas e um acréscimo ao acompanhamento.** Nenhuma coleção normativa nova, nenhuma elevação
de versão canônica, nenhum campo publicado novo — a diferença de porte para a 015, que precisou de
uma elevação 6→7, está inteira aqui.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; invariantes em constraint; histórico não excluído | `Publicacao` (do Edital) e `PublicacaoResultado` são atos distintos sobre objetos distintos, e por isso moram em apps distintos (D-009, T-001). As duas invariantes de cadeia vão ao banco, não ao código: raiz única por marco e sucessor único (T-002). Nada é excluído — `delete` recusa, a trigger recusa e o papel de runtime não tem privilégio. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível; documento deriva do conteúdo | A publicação não é fonte de resultado: ela cita o ato e congela a **projeção** dele (T-003). O documento deriva dos mesmos bytes que a página, e o resumo publicado é o que permite conferi-los (FR-060, FR-061). Retificação posterior não alcança publicação concluída porque não há o que alcançar: o conteúdo está gravado, não recomposto (FR-043). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; identificador público não autoriza; LGPD avaliada; auditoria de ato sensível | Capacidade própria e explícita (`resultado:publicar`), verificada no backend antes da transação (T-006). A superfície pública **não tem caminho de leitura** para `Inscricao` nem `PosicaoNaOrdem` (T-013) — a minimização é estrutural, e não uma serialização que se confia estar filtrada. O protocolo passa a ser público e a FR-024 o impede de virar credencial. A trilha é a existente, com ator, entidade, instante e versão (FR-064). **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; publicar é operação de domínio; transação; concorrência | Publicar é comando de domínio com transação, autorização, reserva de idempotência e revalidação — nunca alteração de booleano. O agregado **não tem máquina de estados** porque não tem ciclo de vida, e a FR-044 declara isso em vez de omitir. A verificação classifica informação, aviso e impedimento (FR-005), no espírito do que a constituição exige da publicação do Edital. Concorrência coberta em três frentes: idempotência, assinatura da prévia e constraint de raiz (T-005). **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Citação resolvível; teste como prova; simplicidade justificada | As nove decisões estão na spec, no formato que `test_citacoes_de_requisito.py` resolve. A simplicidade é ativa: sem rascunho persistente (D-008), sem abstração de publicável (D-002), sem despublicação (FR-038), sem notificação (FR-070). O que se acrescenta de estrutura — app novo, duas tabelas — é o mínimo que a imutabilidade exige. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | A jornada fecha nos três canais dos três atores: a autoridade publica pela interface administrativa, qualquer pessoa consulta pelo portal sem autenticar, e o candidato encontra o resultado dentro da própria Inscrição. O único slice sem comportamento observável é o S0, e a spec declara o que ele desbloqueia. **Passa** |

## Project Structure

### Documentation (this feature)

```text
specs/017-publicacao-de-resultados/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — as decisões técnicas T-001 a T-013
├── data-model.md        # Fase 1 — as duas tabelas e a forma do conteúdo congelado
├── quickstart.md        # Fase 1 — o roteiro que demonstra o gate da spec
├── contracts/
│   ├── publicacao.md    # O comando de publicar: rotas administrativas e recusas
│   ├── conteudo.md      # A forma do conteúdo congelado e a sua canonização
│   └── publico.md       # As rotas públicas, a Área do Candidato e o documento
└── tasks.md             # Fase 2 — $speckit-tasks, não criado aqui
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── divulgacao/                          # app novo
│   ├── models.py                        # PublicacaoResultado, DocumentoDoResultado
│   ├── migrations/0001_initial.py       # tabelas, constraints e triggers append-only
│   ├── domain/
│   │   ├── conteudo.py                  # a projeção publicável do ato (T-003, T-010)
│   │   └── publicabilidade.py           # as três formas de impedimento (T-004)
│   ├── application/
│   │   ├── publicar.py                  # o comando: autoriza, revalida, reserva, grava
│   │   └── selectors.py                 # vigente por marco, histórico, publicação do candidato
│   └── infrastructure/
│       └── documento.py                 # Composicao + render_documento (T-007)
├── interface/                           # canal administrativo (existente)
│   ├── urls.py                          # 3 rotas: prévia, publicar, histórico
│   ├── views.py                         # as views correspondentes
│   └── templates/interface/             # prévia com confirmação, lista do histórico
├── portal/                              # canal público e do candidato (existente)
│   ├── urls.py                          # 2 rotas: página do resultado e documento
│   ├── views.py                         # + o resumo no acompanhamento
│   └── templates/portal/                # resultado.html, + bloco no acompanhamento.html
└── seguranca/papeis.py                  # + 2 tabelas em TABELAS_APPEND_ONLY

backend/tests/
├── acceptance/                          # o gate da spec, ponta a ponta
├── authorization/                       # os negativos da FR-025 e da FR-054
├── contract/                            # a canonização do conteúdo e o resumo
├── integration/divulgacao/              # comando, recusas, sucessão, concorrência
├── interface/ e portal/                 # as telas, incluindo 375 px
├── performance/                         # derivada zero da página pública
├── unit/divulgacao/                     # projeção, publicabilidade, documento
└── migrations/test_migrations.py        # + "divulgacao" em APPS e TRIGGERS_POR_APP
```

**Structure Decision**: app novo `divulgacao`, no precedente do que a 015 fez com `classificacao`.
A justificativa está em T-001, e o que a sustenta é a direção da dependência: `divulgacao` lê
`classificacao` e `publicacoes`, e nenhum dos dois passa a conhecê-la.

## Fases de implementação sugeridas

As fases seguem os slices da spec, e cada uma termina em comportamento observável pelo navegador —
exceto a primeira, que a spec declara como desbloqueio.

| Fase | Entrega | Termina quando |
|---|---|---|
| **F0** | App, tabelas, constraints, triggers, privilégios | O teste estrutural de migrations enxerga as duas triggers e o papel de runtime não consegue `UPDATE` |
| **F1** | Projeção, publicabilidade, comando, prévia e confirmação | A autoridade publica pela interface e as três recusas da FR-004 aparecem nomeadas na tela |
| **F2** | Página pública e descobribilidade pelo Edital | Alguém sem conta abre o resultado pela vitrine, em 375 px |
| **F3** | Área do Candidato | Ana vê "2º lugar" dentro da própria Inscrição, e não via nada antes de P1 |
| **F4** | Documento oficial | O PDF sai com autoridade, resumo e os mesmos rótulos da página |
| **F5** | Histórico, sucessão observável e concorrência | P1 diz que foi sucedida, o histórico lista as duas, e o duplo submit produz uma |

**A F1 é a maior**, e dentro dela a projeção (T-003, T-010) é o que decide se as demais são simples.
**A F5 não é hardening**: a sucessão é a metade da spec que responde "isto ainda vale?", e adiá-la
para o fim é o que permite exercê-la sobre publicações que já existem, em vez de sobre fixtures.

## Complexity Tracking

> Sem violações a justificar. As duas escolhas que acrescentam estrutura estão argumentadas em
> T-001 (app novo em vez de acréscimo a `publicacoes`) e T-003 (conteúdo congelado em vez de
> composição na leitura), e ambas reduzem, e não aumentam, o que precisa ser confiado ao código.
