# Implementation Plan: Edital Institucional

**Branch**: `007-edital-institucional` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-edital-institucional/spec.md`

## Summary

Aproximar o documento de um Edital institucional real e eliminar os atritos restantes da autoria,
**sem construir mecanismo novo**. O trabalho se divide em três naturezas, e a divisão é o que
governa o encadeamento:

1. **Apresentação pura** — o compositor deixa de imprimir estado interno e passa a escrever decimais
   em português. Não toca snapshot, não toca hash, é a primeira entrega e é demonstrável sozinha.
2. **Forma canônica** — três seções no catálogo declarado, três campos no Perfil e a identificação
   institucional do Processo na raiz. É o **único** incremento de `SCHEMA_VERSION` da feature, e as
   três mudanças viajam juntas por FR-018.
3. **Exposição** — becos, passagem de bastão e atritos. Tudo em `interface/`, tudo lendo informação
   que o sistema já tem e descarta.

Nenhum command novo. Nenhum modelo novo. Nenhuma coleção-raiz nova no snapshot. Um único registro
declarativo nasce — o catálogo de autoridades signatárias —, no mesmo padrão do catálogo de seções
que a `006` estabeleceu.

**A descoberta que mais simplifica o plano**: os achados 07 e 08 da auditoria têm **uma única
causa**. Existem hoje dois registros de ação — `ACOES_POR_SITUACAO`
(`interface/views.py:61-67`, usado pela listagem, e que já conhece a permissão
`retificacao:elaborar`) e `atos.disponiveis` (usado pelo detalhe) — e o `detalhe.html` ainda
renderiza `Retificar` num `<li>` fixo fora dos dois (`:74`), enquanto o `{% empty %}` observa apenas
`atos` (`:86-94`). Unificar o cálculo resolve os dois achados de uma vez, e resolve o terceiro
(FR-026) de graça, porque a permissão passa a ser consultada no caminho unificado.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. **Nenhuma dependência nova** —
inclusive para formatação decimal e localização, resolvidas com a biblioteca padrão.

**Storage**: PostgreSQL. Uma migration de três colunas em `PerfilVaga`. Sem mecanismo de
compatibilidade (precondição de implantação, FR-019).

**Testing**: pytest com `tests/{unit,contract,interface,integration,migrations,javascript}`.

**Target Platform**: servidor Linux; interface administrativa server-rendered com HTMX.

**Project Type**: aplicação web Django em camadas por app — `domain/`, `application/`, `models/`,
`api/`, `infrastructure/` — mais o app `interface/`.

**Performance Goals**: nenhuma meta nova.

**Constraints**: a forma canônica não muda por motivo de legibilidade (FR-001); a gramática de
`publicacoes/domain/changes.py` não muda (P-005); nenhuma entidade persistida nasce para autoridades
(FR-039); nenhum estado de visita é persistido (FR-040).

**Scale/Scope**: cinco entregas; 48 requisitos; três colunas novas; três seções novas; um catálogo
declarado novo; nenhuma reescrita.

## Constitution Check

*GATE: avaliado contra a Constituição 1.1.1, antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Portão | Situação |
|---|---|---|
| I — Linguagem ubíqua | Termos novos existem no domínio e no código com o mesmo nome | `Autoridade Signatária` já é termo da Constituição e não é renomeado. Os campos novos do Perfil entram como `duties`, `workload` e `compensation`, e as três seções novas usam chaves do mesmo estilo do catálogo vigente. Nenhum conceito novo é criado. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável | A identificação institucional do Processo passa a viajar no snapshot **derivada** do Processo no momento da publicação, como `title` e `number` do Edital já viajam. **E passa a ser protegida**: os cinco campos de identidade da raiz deixam de ser endereçáveis por Retificação (FR-004, D-003.1), de modo que nenhum ato posterior faz o documento nomear outro Processo. Editais anteriores tornam-se irretificáveis por versão, o que é a integridade funcionando e está coberto pela precondição de implantação. **Passa** |
| III — Segurança, dados pessoais e auditoria | Autorização explícita; LGPD avaliada; auditoria não regride | FR-026 usa a checagem de permissão existente e **não** cria camada nova. A avaliação de LGPD está na spec (FR-044 a FR-048): o catálogo guarda nome, cargo no exercício de atribuição pública e o identificador institucional que `Publicacao.signatory_id` já exige — nunca digitado, exibido nem impresso —, e nada além. FR-042 amplia o que a auditoria diz sobre **conteúdo**, não sobre pessoas. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; interface não é fronteira de segurança | FR-025 declara explicitamente que a desabilitação é previsão de interface e não substitui a recusa do domínio — a mesma postura que `praticar_ato` já adota com `recusa_certa`. **Passa** |
| V — Qualidade e simplicidade | Solução mais simples que preserve os requisitos | Nenhum padrão novo: sem repositório, sem DTO novo, sem serviço novo, sem entidade nova, sem workflow engine. O catálogo de autoridades reusa o padrão do catálogo de seções em vez de inventar um. **Passa** |
| VI — Completude de jornada | Cada entrega termina em cenário demonstrável pelo canal do ator | As cinco entregas terminam no navegador; `SC-010` reafirma a jornada de ponta a ponta com dois atores. **Passa** |

**Restrições e Invariantes do Domínio.** Duas merecem registro:

- *"O PDF DEVE derivar dos dados estruturados... A cadeia dados estruturados → versão homologada →
  PDF publicado DEVE ser demonstrável."* FR-004 **fortalece** esta invariante: hoje o snapshot
  publicado não consegue nomear o Processo a que pertence, e o documento só o identifica por UUID.
  Com o campo, o snapshot passa a bastar para compor o documento.
- *"Interfaces DEVEM priorizar clareza, consistência, prevenção de erro, feedback, acessibilidade,
  teclado, legibilidade."* É a invariante que FR-024, FR-032, FR-033, FR-038 e FR-040 pagam, e a
  auditoria da `006` foi o levantamento que a mediu.

**Reavaliação pós-Fase 1**: sem violações novas. Nenhuma entrada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/007-edital-institucional/
├── plan.md              # Este arquivo
├── spec.md
├── research.md          # Fase 0 — decisões e alternativas recusadas
├── data-model.md        # Fase 1 — colunas, catálogos e a forma canônica v3
├── quickstart.md        # Fase 1 — como demonstrar e validar
├── checklists/
└── contracts/
    └── institucional.md # Fase 1 — forma canônica v3 e regras de apresentação
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── domain/
│   │   └── secoes.py                 # +3 entradas no CATALOGO (FR-007, FR-008)
│   ├── models/
│   │   └── perfis.py                 # +duties, +workload, +compensation (FR-012)
│   ├── migrations/
│   │   └── 0005_perfil_institucional.py   # NOVO — três colunas
│   └── api/serializers.py            # payload do rascunho ganha os três campos
├── processos/
│   └── application/commands.py       # separa os dois create no tratamento do erro (FR-022)
├── publicacoes/
│   ├── domain/
│   │   └── autoridades.py            # NOVO — catálogo declarado (FR-039)
│   ├── application/
│   │   └── publish_edital.py         # raiz ganha processoCode/processoTitle; profiles ganha 3
│   └── infrastructure/
│       ├── pdf.py                    # sem estado interno; decimal pt-BR; integridade sem UUID
│       └── humano.py                 # NOVO — decimal e rótulo para leitura (FR-002, FR-003)
├── interface/
│   ├── acoes.py                      # NOVO — conjunto único de ações do Edital (FR-023/24/26)
│   ├── views.py                      # detalhe unificado; processo_detalhe; progresso em 3 estados
│   ├── forms.py                      # três campos do Perfil; obrigatoriedade declarada
│   ├── templates/interface/          # detalhe, confirmar, processo_detalhe, _perfil, linhas
│   └── static/interface/             # ordenacao.js: desabilitar nas pontas, numerar posição
└── shared/canonical.py               # SCHEMA_VERSION 2 -> 3

backend/tests/
├── unit/                             # formatação humana; catálogo de autoridades; progresso
├── contract/                         # forma canônica v3 completa; guarda de versão
└── interface/                        # ações unificadas; permissão de retificar; acessibilidade
```

**Structure Decision**: mantida a estrutura existente. **Três módulos novos e uma migration**, todos
justificados por separação de responsabilidade e não por generalização:

- `publicacoes/infrastructure/humano.py` — porque FR-001 exige um lugar **declarado** onde a
  formatação humana vive. Espalhá-la pelo compositor tornaria a fronteira canônica uma convenção em
  vez de uma regra verificável, e é exatamente a fronteira que a revisão da spec mostrou ser fácil de
  atravessar por descuido.
- `interface/acoes.py` — porque FR-023 exige que o conjunto seja calculado **uma vez**. Hoje ele
  está em três lugares (`ACOES_POR_SITUACAO`, `atos.disponiveis`, e um `<li>` no template), e é essa
  dispersão que produz o cartão que oferece uma ação e diz que não há ação.
- `publicacoes/domain/autoridades.py` — porque FR-039 exige uma origem declarada para a escolha da
  autoridade. Reusa o padrão do catálogo de seções em vez de inventar entidade.

Mais `editais/migrations/0005_perfil_institucional.py`. Nenhum app novo. Nenhum diretório novo.
`colecoes.py` **ganha um conjunto declarado**, não um arquivo.

## Abordagem por entrega

A ordem é a da spec. A entrega 2 é a única que incrementa a versão canônica.

### Entrega 1 — O documento se lê como um Edital, parte apresentacional (FR-002, FR-003)

Nasce `humano.py` com duas funções: `decimal(valor)` e a supressão do que não deve ser impresso.
`decimal` recebe a string canônica de quatro casas e devolve a forma pt-BR — `"20.0000"` → `"20"`,
`"12.5000"` → `"12,5"` —, descartando zeros à direita e trocando o ponto por vírgula. O compositor
passa a chamá-la nos três pontos que hoje escrevem o decimal cru
(`pdf.py:157`, `:235`, `:237`).

`Situação: {status}` sai de `_cronograma` (`pdf.py:203-204`). Não é substituído por um mapa: **o
estado do Evento simplesmente não é conteúdo de Edital**. O precedente do mapa existe para
`reserveType`, que descreve a vaga; o estado do Evento descreve a gestão do certame.

A fixture de bytes é regenerada por `backend/scripts/gerar_fixture_documento.py`, que a `006` já
deixou pronto para isto.

### Entrega 2 — A forma canônica v3 (FR-004, FR-007, FR-012, FR-014, FR-017)

**Entra inteira num único PR**, pelo mesmo motivo que a `006` declarou para a versão 2: subir a
versão com uma parte e acrescentar a outra depois produziria snapshots de versão 3 com e sem as
propriedades, e a versão canônica deixaria de identificar uma forma.

O catálogo de seções ganha três entradas textuais com redação institucional inicial, nas posições
que FR-008 fixa. O `order` das seções existentes é renumerado — o catálogo é declarado, não
persistido, e a identidade de cada seção é `uuid5(edital, key)`, que **não depende da ordem**. Por
isso renumerar não move identidade nem quebra endereçamento.

`PerfilVaga` ganha três colunas. `duties` é `TextField` porque atribuições são vários parágrafos e o
documento os preserva; `workload` e `compensation` são `CharField(255)` porque são frases. As três
entram no snapshot como string sempre presente.

A raiz do snapshot ganha `processoCode` e `processoTitle`, lidos de `edital.processo` — que já vem
por `select_related("processo")` em `_locked_edital` (`publish_edital.py:158-163`), de modo que não
há consulta a mais. `_integridade` passa a escrever o Edital por número/ano e o Processo por código
e título, mantendo a afirmação de derivação, a versão do schema e o SHA-256, e deixando de escrever
os dois UUIDs.

**E a identidade da raiz passa a ser protegida na mesma entrega.** `colecoes.py` ganha um segundo
conjunto declarado — os cinco campos de identidade —, e `_recusar_controle_interno`
(`changes.py:167-173`) passa a consultá-lo junto de `LISTAS_DE_CONTROLE`. É um conjunto e uma
condição, na via de extensão que a `006` já usou; não é gramática nova. Sem isto, uma Retificação
faria o documento publicado nomear outro Processo, e seria esta feature que abriria a porta
(D-003.1).

### Entrega 3 — O fluxo administrativo sem becos (FR-021 a FR-027)

Nasce `interface/acoes.py` com **uma** função que responde, para um Edital e um ator, o conjunto
completo de ações: rótulo, rota, se está disponível e, quando não está, o motivo. Ela funde os três
lugares de hoje e incorpora a previsão de recusa que `praticar_ato` já calcula
(`views.py:849-861`) — `atos.impedimento` e `_pendencias`, ambos já disponíveis no `detalhe`.

`detalhe.html` passa a iterar esse conjunto único; `Retificar` deixa de ser um `<li>` fixo e vira uma
entrada como as outras, sujeita à permissão `retificacao:elaborar` que `ACOES_POR_SITUACAO` já
declara. O `{% empty %}` passa a observar o mesmo conjunto, e a contradição do achado 08 deixa de
ter como ocorrer.

A view `retificar` ganha a checagem de permissão **fora** do ramo POST, apresentando a tela em
leitura para quem não pode elaborar.

`processo_detalhe` promove elaborar o Edital a ação primária e rebaixa o impedimento de cancelar.

`create_process_with_first_edital` separa os dois `create` em blocos `try` distintos
(`processos/application/commands.py:29-46`), devolvendo `edital_identifier_conflict` para o conflito
do Edital — código que já existe trinta linhas abaixo, em `create_edital` (`:92-95`). Nenhum erro
novo é inventado.

### Entrega 4 — Passagem de bastão (FR-028 a FR-031)

Uma função de leitura em `interface/acoes.py`: dado o estado do Edital, devolve a situação em
português e o papel responsável pelo próximo ato, derivados de `ACOES_POR_SITUACAO`, que já mapeia
situação → ações → permissão. Nada é persistido, nada é atribuído a pessoa.

A coerência com a segregação de funções (FR-031) **não sai de graça, e este é o ponto delicado da
entrega**. Derivar apenas de `ACOES_POR_SITUACAO` diria "você publica" a quem elaborou e homologou
sozinho — exatamente a pessoa que o domínio recusará. A função consulta também
`impede_por_segregacao`, que já é calculada no `detalhe` e no `confirmar`
(`views.py`, `impede_por_segregacao(participantes, ator)`), e nesse caso nomeia o **papel** sem
apontar o leitor. O cenário 3 da `US5` é o teste que separa "derivar do mapa de permissões" de
"derivar do que o domínio aceitaria".

### Entrega 5 — Os atritos de operação (FR-032 a FR-043)

A maior em número de itens e a menor em risco. Três agrupamentos:

**Obrigatoriedade e recusa (FR-032, FR-033).** A obrigatoriedade passa a ser declarada junto do
campo, não escrita na etiqueta à mão, e o resumo de erros ganha âncora e vínculo programático.

**Ordem e leitura de linha (FR-035, FR-036, FR-037).** `ordenacao.js` já move linhas e renumera
`order`; ganha desabilitar nas pontas e escrever a posição na legenda. O seletor de Evento passa a
compor a opção com a data — o dado já está no fragmento, que é escopado ao Edital exatamente para
ter os Eventos daquele Cronograma (`interface/urls.py:40-46`).

**Estado, confirmação e nomes (FR-038, FR-039, FR-040, FR-041, FR-042).** O progresso do assistente
passa de dois estados para três; `conteudo` deixa de ser `True` fixo (`views.py:325-328`) e passa a
distinguir **gravada** de **nunca gravada** — sinal que já existe e não custa estado novo, porque
`SecaoEdital` só tem linha depois da primeira edição. O catálogo de autoridades nasce em
`publicacoes/domain/autoridades.py`. `Ato registrado:` deixa de passar a chave pelo filtro `situacao`
(`detalhe.html:15`), que mapeia **situações** e por isso devolve `submeter` cru; passa a ler o
`rotulo` que `atos.ATOS` já declara. E a auditoria da gravação do rascunho passa a registrar qual
etapa foi salva.

### Encadeamento

Só há uma dependência real entre entregas: **a 1 e a 2 tocam o mesmo arquivo** (`pdf.py`) e ambas
alteram os bytes do documento, de modo que **cada uma regenera a fixture** — duas regenerações, e
FR-006 foi corrigido para dizê-lo. Não é desperdício: é o preço de FR-018, que faz a parte
apresentacional chegar sem esperar o incremento canônico. Fundi-las numa entrega só economizaria uma
regeneração e custaria a demonstração antecipada; deixar a fixture desatualizada entre as duas
deixaria a `main` vermelha.

As entregas 3, 4 e 5 são independentes entre si e independentes das duas primeiras. A 4 usa a
função que a 3 cria, e por isso vem depois dela.

## Complexity Tracking

Nenhuma violação constitucional a justificar. Nenhum padrão arquitetural novo introduzido.
