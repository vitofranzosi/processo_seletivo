# Implementation Plan: Ordenação e Classificação

**Branch**: `claude/spec-015-ordenacao-classificacao-4e0ab0` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-ordenacao-e-classificacao/spec.md`

## Summary

A 013 entregou Resultados de Etapa oficiais, imutáveis e auditáveis, e parou antes de dizer quem
ficou em primeiro. A 015 começa ali: produz a ordem entre participantes segundo uma regra publicada,
em marcos classificatórios identificáveis, e constitui essa ordem por **ato** — calculado de forma
determinística, emitido por quem tem autoridade, imutável depois de emitido e reproduzível a partir
do que ficou registrado.

**Esta é a maior feature desde a 012, e o peso não está onde parece.** O cálculo é uma função pura
sobre dados que já existem. O que custa é que **a regra que o governa ainda não é conteúdo
publicado** — e a 013 excluiu isso no §5 com todas as letras: "novo campo normativo para regra de
combinação; isso inclui esquema, elaboração, documento e catálogo de Retificação". A conta vem
inteira para cá, e o levantamento mediu: **19 pontos de toque** para acrescentar uma coleção aninhada
ao Perfil (T-012), antes de existir regra para o cálculo ler.

Três verificações no código explicam o desenho:

1. **A metade normativa da combinação já existe.** A Etapa publicada traz `weight`, `order` e
   `classificatory` desde sempre (`editais/api/serializers.py:99-104`). A clarificação fixou que
   `weight` continua sendo a fonte autoritativa e que o marco apenas **enumera** as Etapas e declara
   a **operação** — o que reduz a coleção nova ao que de fato falta, em vez de duplicar o peso
   (FR-008 a FR-012).
2. **O ato administrativo é mecanismo pronto.** `comando_de_comissao` entrega transação, bloqueio do
   Processo, reavaliação da autorização **depois** do bloqueio e reserva da chave, nessa ordem e por
   razões documentadas (`comissoes/application/__init__.py:45-63`). A 015 usa os quatro e não escreve
   nenhum (T-001). Não há permissão nova: `resultado:consolidar` nem é permissão — é `operation` de
   idempotência, e a armadilha está registrada.
3. **A modalidade já é legível.** `ModalidadeConcorrencia` existe, viaja no snapshot e é escolhida na
   inscrição (`inscricoes/models.py:34`). FR-005 apenas a registra na posição, declarada e não
   verificada — a 015 não inicia verificação de elegibilidade.

O trabalho tem três naturezas, e a primeira domina:

- **Uma coleção normativa nova, com elevação de versão canônica** — `classificationMilestones`
  aninhada no Perfil, com a elevação 6→7 que, pela primeira vez, precisa descer abaixo de `/stages`
  (T-007, T-008). É aqui que mora o risco.
- **Duas tabelas num app novo e três funções puras** — o ato, suas posições, o cálculo, o desempate e
  a comparação de obsolescência (T-010, T-011).
- **Uma superfície de interface pequena** — a tela do marco, com cálculo na abertura, emissão por
  POST e consulta do ato, no molde de `distribuicao.html` (T-006).

**A decisão que mais determina o desenho** é a da clarificação sobre emissão concorrente: recusar, e
não suceder. Isso transforma "no máximo um ato vigente" em constraint de banco, e não em verificação
de aplicação (T-002) — a idempotência não cobre o caso, porque chaves diferentes são pedidos
diferentes.

**A que mais economiza** é a que ficou de fora: o sorteio. O Edital 57/2026 não é executável por esta
feature, e a razão é dependência, não escopo — a 013 só produz Resultado a partir de Avaliação, e
D-1 acrescenta apenas a Ocorrência. Não há Resultado de sorteio para ordenar. Fingir que havia
custaria um mecanismo de importação inteiro dentro desta spec.

**A que mais preocupa** é de sequenciamento, e é do usuário: D-2 acrescenta outra coleção normativa e
sobe a mesma versão. Em levas separadas são duas elevações, dois degraus e dois caminhos de leitura —
e os critérios de desempate por idade e por experiência ficam sem valor para ler até a segunda cair.
O plano assume a leva conjunta e a declara nas fatias.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** O canal é o HTML
institucional de `interface`, com os fragmentos htmx já embarcados. Há alteração no `openapi.yaml` da
001 — o schema do Perfil publicado ganha a coleção nova, e o teste de contrato exige que todo campo
publicado seja obrigatório (`tests/contract/test_forma_publicada.py:109-116`).

**Storage**: PostgreSQL. **Três migrations**, pela leva decidida (ver §Fases): uma em `editais` — o
marco e seus critérios, os **fatos declarados** de D-2 e o teto `maxInscricoesPorCandidato` de D-3,
todos como linhas de elaboração no molde de `ModalidadeConcorrencia`; uma em `inscricoes` — os
valores **congelados na submissão** e o que a trava do par identidade–Edital exige; e uma no app novo
`classificacao` — o ato, as posições, a unicidade da raiz e do sucessor, e duas triggers (coerência
no `INSERT` e append-only no `UPDATE`/`DELETE`, esta **sem exceção alguma**). Nenhuma migration em
`resultados`, `avaliacoes` ou `auditoria`: D-1 corre em paralelo, como extensão da 013, e não toca
conteúdo publicado.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. Quatro exigências específicas: a unicidade da raiz e a do
sucessor sob concorrência e as triggers só são exercidas com `TEST_DB_ENGINE=postgresql`; o nome de cada
trigger precisa entrar em `TRIGGERS_POR_APP` (`tests/migrations/test_migrations.py:21-38`), sem o que
o teste estrutural não a enxerga; as tabelas novas entram em `TABELAS_APPEND_ONLY`
(`seguranca/papeis.py:26-41`); e a coleção aninhada nova só é pega por um guarda —
`tests/integration/publicacoes/test_enderecamento.py:249-250`.

**Target Platform**: servidor Linux; navegador institucional, incluindo celular — a ordem e a
divergência precisam caber em 375 px sem tabela horizontal.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: SC-002 dá **3 segundos a 1.000 participantes** na abertura da tela do marco, e
o alvo exige **duas provas**, não uma. Orçamento de consultas sozinho não prova nada sobre tempo —
uma consulta pode ser lenta, e ordenar e renderizar mil linhas pode estourar o teto sem mudar a
contagem. A casa já faz as duas: `tests/performance/test_public_queries.py:145-169` mede o percurso
com `time.monotonic()` contra um `BUDGET_SECONDS` deliberadamente **abaixo** do limite da SC, para
que a folga absorva a variação da máquina, e o teste vizinho compara custos entre cenários. Esta
feature repete o par: medição de ponta a ponta com 1.000 participantes (SC-002) e derivada de
consultas igual a zero entre dois tamanhos (SC-003). O cálculo resolve participantes, Resultados das Etapas enumeradas e conteúdos de versão
**antes** do laço, com `conteudos_das_versoes` para desduplicar por versão — a alternativa errada não
muda a contagem de consultas e por isso nenhum orçamento a denunciaria (T-004).

**Constraints**: `comando_de_comissao` bloqueia o `ProcessoSeletivo` inteiro pela duração da
transação, como em toda a família. A elevação canônica é a restrição dura: enquanto o degrau 7 não
souber descer até `profiles`, todo conteúdo v6 publicado fica irretificável.

**Scale/Scope**: um Edital com mil inscritos, quatro Etapas e até três marcos por Perfil. Com a leva
decidida: **duas** coleções normativas novas — marco e fatos declarados — mais um campo publicado,
numa elevação canônica única; **seis** tabelas novas — marco, critério, fato declarado, valor congelado, ato e posição; três funções de domínio; duas rotas novas; uma
tela nova; e o caminho do conteúdo publicado percorrido **uma** vez para as três mudanças, em vez de
três vezes.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; invariantes em constraint | Marco, Ato de Ordenação e Posição são conceitos distintos, com ciclos de vida próprios — daí o app novo (T-010). Marco e critério recebem identidade estável e são endereçados por `id=`, no padrão da 004; a ordem dos critérios é normativa e por isso a posição no array significa, o que é declarado e não presumido. As duas invariantes centrais vão ao banco: unicidade parcial do ato vigente por marco (T-002) e coerência das posições contra os Resultados citados (T-003). **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | `weight` continua sendo a única fonte do peso — o marco enumera e declara operação, não duplica número (FR-009). O ato grava a versão normativa que o governou, e a proveniência é suficiente para reproduzir a ordem sem consultar o estado vigente (FR-041). A elevação 6→7 declara significado verdadeiro para a ausência: Edital sem marco não classifica (T-008). Retificação alcança marco e critérios e não reescreve publicação anterior. **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | Autorização herdada — `comissao:gerir` ∪ presidência —, reavaliada depois do bloqueio, sem capacidade nova (D-007, T-001). Consultar abre para `auditoria:consultar`; emitir não. Recusa é 404 uniforme. A resposta que carrega posição e fatos de desempate é `marcar_como_privada`. A trilha registra ator, base, ato, correlação e motivo, e **não tem por onde** pontuação caber — a assinatura de `auditar` a exclui por projeto. Fato de candidato usado em desempate é dado pessoal: FR-048 restringe a quem administra e audita. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | O cálculo é função pura sobre conteúdo publicado, e a tela não decide nada — não há campo de posição, nota ou desempate no POST de emissão. **Nada é persistido como estado mutável:** vigente, obsoleto e não recomputável são todos derivados, e a sucessão é linha nova apontando a anterior. Não é elegância — a política de papéis revoga `UPDATE` das tabelas append-only (`seguranca/papeis.py:129`), e um booleano `vigente` seria impossível de virar em produção. Concorrência: bloqueio do Processo mais unicidade da raiz e do sucessor. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Citação resolvível; teste como prova; simplicidade | As decisões herdadas D-1 a D-4 foram declaradas na `research.md` porque a feature as cita, e `test_citacoes_de_requisito.py` exige que citação seja resolvível dentro da feature — o teste estava vermelho e voltou ao verde antes deste plano. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável; jornada de ponta a ponta pelo canal do ator | A jornada é inteira pela interface administrativa: declarar o marco no Edital, publicar, abrir a tela, conferir a ordem calculada, emitir, consultar a proveniência e ver a obsolescência (FR-046). A divergência entre computado e vigente é exigência de interface, não de domínio — é o que impede a capacidade de existir sem ser alcançável. **Passa** |

## Project Structure

### Documentation (this feature)

```text
specs/015-ordenacao-e-classificacao/
├── spec.md              # a especificação, com nove decisões e cinco clarificações
├── plan.md              # este arquivo
├── research.md          # Fase 0 — decisões herdadas D-1 a D-4 e T-001 a T-012
├── data-model.md        # Fase 1 — as duas tabelas, e o que não é tabela
├── quickstart.md        # Fase 1 — o percurso, e a cobertura declarada
├── contracts/
│   ├── marco.md         # a coleção normativa nova: forma, validação e Retificação
│   └── ordenacao.md     # rotas, corpos, desfecho e recusas
├── checklists/
│   └── requirements.md  # qualidade da spec, clarificação, revisão do plano e análise cruzada
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── classificacao/                        # NOVO
│   ├── models.py                         # AtoDeOrdenacao, PosicaoNaOrdem
│   ├── migrations/0001_initial.py        # unicidade parcial do vigente + duas triggers
│   ├── domain/
│   │   ├── combinacao.py                 # pontuação combinada a partir da operação publicada
│   │   ├── desempate.py                  # critérios ordenados, valor ausente, empate residual
│   │   └── universo.py                   # o recorte declarado e a comparação de obsolescência
│   └── application/
│       ├── calculo.py                    # leitura única, laço sem consulta
│       ├── emissao.py                    # o ato, sob comando_de_comissao
│       └── selectors.py                  # ato vigente, posições paginadas, divergência
├── editais/
│   ├── models/perfis.py                  # ALTERADO: MarcoClassificatorio, CriterioDesempate
│   ├── domain/validation.py              # ALTERADO: verificação aninhada do marco (T-009)
│   ├── domain/perfis.py                  # ALTERADO: validação de elaboração
│   ├── api/serializers.py                # ALTERADO: coleção no ProfileSerializer
│   └── application/draft.py              # ALTERADO: preservar id; identidades aninhadas alheias
├── publicacoes/
│   ├── application/publish_edital.py     # ALTERADO: emitir a coleção no laço do Perfil
│   ├── domain/colecoes.py                # ALTERADO: COLECOES_COM_CHAVE
│   ├── domain/elevacao.py                # ALTERADO: degrau 7, e elevar() desce até profiles
│   └── infrastructure/pdf.py             # ALTERADO: render dentro de _perfis
├── shared/canonical.py                   # ALTERADO: SCHEMA_VERSION 6→7 e a história
├── portal/                               # ALTERADO (D-2): o canal do candidato
│   ├── views.py                          #   campos dos fatos declarados na inscrição
│   └── templates/portal/inscricao.html   #   e a recusa do teto, com o motivo
├── inscricoes/                           # ALTERADO (D-2, D-3): fatos congelados na submissão
│   ├── models.py                         #   valores por inscrição, contra a versao_aceita
│   └── application/                       #   trava do par identidade–Edital; teto de D-3
├── seguranca/papeis.py                   # ALTERADO: as duas tabelas em TABELAS_APPEND_ONLY
└── interface/
    ├── urls.py                           # ALTERADO: duas rotas novas
    ├── views.py                          # ALTERADO: marco, emitir, fragmento do critério
    ├── forms.py                          # ALTERADO: ler/renderizar/persistir o marco
    ├── retificacao.py                    # ALTERADO: CAMPOS_MARCO e laço aninhado
    └── templates/interface/
        ├── _marco.html                   # NOVO
        ├── _fato.html                     # NOVO (D-2, na composição do Edital)
        └── ordenacao.html                # NOVO

backend/tests/
├── unit/classificacao/                   # combinação, desempate, universo — sem banco
├── unit/editais/                         # forma do snapshot com a coleção nova
├── integration/                          # unicidade da raiz e do sucessor, triggers, elevação
├── authorization/                        # 404 uniforme; consultar é de dois, emitir é de um
├── performance/                          # o custo não cresce com a população
└── acceptance/test_ordenacao.py
```

**Structure Decision**: a estrutura existente do backend Django, com um app novo em
`backend/processo_seletivo/classificacao/`. O canal administrativo continua sendo o HTML de
`interface`. **`portal` recebe os campos dos fatos declarados**, porque a leva trouxe a US2 e quem
preenche fato é o candidato — o que continua fora do `portal` é a **ordem**, que é administrativa
nesta feature e só chega ao candidato pela 017.

## Fases de implementação sugeridas

**A leva está decidida:** D-2 (fatos declarados) e D-3 (teto de inscrições) entram **nesta** feature,
junto com o marco, numa elevação canônica única 6→7. D-1 corre **em paralelo**, como extensão da 013,
porque é esquema e regra de domínio sem reflexo no snapshot — e por isso não disputa a elevação.

A consequência honesta: a 015 absorve trabalho que seria de outra spec. A coleta dos fatos é
território da 009 e o teto é regra de submissão; os dois entram aqui porque atravessam o mesmo
caminho de conteúdo publicado, e percorrê-lo três vezes custaria três elevações, três degraus em
`elevacao.py` e três caminhos de leitura das versões anteriores.

| Slice | Entrega | Artefatos |
|---|---|---|
| **S0** | O Edital declara marco, desempate, fatos exigidos e teto; publica e retifica — numa elevação só | `perfis.py`, `draft.py`, `validation.py`, `publish_edital.py`, `canonical.py`, `elevacao.py`, `colecoes.py`, `forms.py`, `retificacao.py`, `pdf.py`, `_marco.html`, `_fato.html` |
| **S1** | A inscrição coleta e **congela** os fatos na submissão, e o teto passa a valer | `inscricoes/`, submissão com trava do par identidade–Edital, `portal/` |
| **S2** | A ordem é calculada e exibida, e nada é gravado | `combinacao.py`, `desempate.py`, `calculo.py`, `ordenacao.html` |
| **S3** | A ordem é emitida, imutável, com proveniência e trilha | app `classificacao`, migration com as duas triggers, `emissao.py` |
| **S4** | A obsolescência aparece, e a sucessão exige recálculo confirmado | `universo.py`, `selectors.py`, divergência na tela |

**O que S3 não trata, e por quê:** o par "obsoleto e não recomputável" foi reformulado depois que a
revisão do plano mostrou que o cenário original era inalcançável. Remover a Etapa enumerada sem
ajustar o marco é **recusado na publicação** por FR-017 e FR-043, de modo que critério pendurado não
existe. O caso real é a **remoção do marco**: aí não há regra vigente com que comparar, e o ato
segue reproduzível pela versão histórica (FR-042).

S0 é a fatia mais longa e a mais arriscada, e não pode ser encurtada: sem regra publicada, S2 não tem
o que ler. **A elevação de versão é o item de maior risco da feature inteira** — é a primeira vez que
um degrau precisa descer abaixo de `/stages`, e agora ela carrega duas coleções e um campo de uma
vez; enquanto não funcionar, todo conteúdo v6 publicado fica irretificável.

S1 é o que torna o desempate executável: sem fato congelado, os critérios por idade e por tempo de
experiência não têm valor para ler. Ela vem antes do cálculo de propósito — o congelamento acontece
na **submissão**, contra a `versao_aceita`, e não há como retroagi-lo para quem já se inscreveu.

S4 vem por último porque só há divergência a mostrar depois de existir ato emitido, e antecipá-la
produziria código com um único caminho testável — o de nunca haver ato.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples, e por que foi rejeitada |
|---|---|---|
| App novo `classificacao` para duas tabelas | Ordenar não é resultado de Etapa: o ato tem universo, autoridade e sucessão próprios, e a 016 crescerá em torno dele. Migration aplicada não se reescreve, e mover tabela depois é caro. | *Tabelas dentro de `resultados`*: custa zero apps e hospeda em "resultados" um agregado que não é resultado. Repete exatamente o erro que a 013 evitou ao não morar em `avaliacoes`. |
| Elevação canônica que desce abaixo de `/stages` | Sem ela, todo Edital publicado em v6 fica irretificável, e a feature quebraria conteúdo em uso para entregar capacidade nova. | *Aceitar a irretificabilidade*, como a 007 e a 009 fizeram: era aceitável quando não havia conteúdo publicado em uso; hoje não é. |
| Posição como tabela, e não JSON dentro do ato | SC-016 exige contar posições e considerados sem posição contra o universo; FR-045 exige consultar o desempate entre vizinhas. Ambas viram agregação em memória sobre mil linhas se a posição for JSON. | *JSON no ato*: uma tabela a menos e uma migration mais simples, ao custo de toda consulta da feature. |
| Unicidade da raiz e do sucessor, em vez de um campo `vigente` | FR-031 exige recusa da segunda emissão, e a idempotência não cobre — chaves diferentes são pedidos diferentes. Com a sucessão em linha nova, unicidade sobre `ato_anterior` impede bifurcar a cadeia e unicidade parcial da raiz impede dois primeiros atos. | *Booleano `vigente` com unicidade parcial*: era o desenho anterior, e é **impossível** — a política revoga `UPDATE` do runtime nas tabelas append-only, e a exceção em trigger não devolve privilégio. |
| Absorver D-2 e D-3 nesta feature | As três mudanças atravessam o mesmo caminho de conteúdo publicado e a mesma elevação canônica. Separadas, são três elevações, três degraus e três caminhos de leitura — e a 015 seria entregue com o desempate por fato inexecutável para os Editais em vista. | *Uma spec normativa antes, e a 015 depois*: cada spec do tamanho planejado, ao custo de duas elevações, sendo a segunda a que precisa descer até `profiles`. Considerada e recusada pelo usuário em 04/09/2026. |
| Ordem publicada como campo do critério, com unicidade | A ordem dos critérios **é** a norma, e a Retificação precisa de um alvo endereçável para reordenar: substituir a lista inteira perderia identidades e quebraria o endereçamento por `id=`. Com `uq_criterio_marco_ordem`, o empate de ordem que se temia não é representável. | *Posição no array como única fonte da ordem*: foi a primeira redação, e não dizia como reordenar por Retificação — o catálogo endereça por identidade, nunca por índice. |
