# Research: Leitura do conteúdo não publicado na gestão

As decisões técnicas desta feature, em `D-001` a `D-008`, e o inventário que as fundamenta. As
decisões de produto são as `P-` da [spec](spec.md); cada `D-` diz de qual depende.

---

## Inventário de 01/11/2026

Medido sobre a `main` em `32097602`, por leitura de `interface/urls.py` e de cada view. A tabela
completa, rota a rota, com a classificação que o guardião lê, é o
[contrato do inventário](contracts/inventario-das-rotas.md). O que ele estabelece:

- **Nenhum seletor nem serviço da camada de aplicação conhece "leitura do rascunho".**
  `listar_processos` e `obter_edital` (`processos/application/selectors.py`) filtram só o escopo.
  `LEITURA_DO_RASCUNHO` existe só em `interface/views.py` e só `anexo_do_rascunho` a usa.
- **Quase toda rota que exibe o não publicado confere só identidade e escopo**: `lista`, `detalhe`,
  `compor`/`compor_etapa` (em leitura quando `pode_compor` é falso), `previa`, `previa_documento`,
  `praticar_ato` (GET), `processo_detalhe`, `processo_ato` (GET), `supervisao`, `retificacao_detalhe`,
  `retificacao_ato` (GET), `retificar` (a lista das em curso) e sete fragmentos que leem o rascunho
  (`fragmento_etapa`, `fragmento_documento`, `fragmento_perfil`, `fragmento_marco`,
  `fragmento_marco_recomposto`, `fragmento_criterio`, `fragmento_previa_da_classificacao`, por
  `_edital_do_fragmento`).
- **Conferem capacidade**: `anexo_do_rascunho` (três capacidades, 404), `reaproveitar`
  (`edital:elaborar`, 404), `fragmento_perfil_duplicado` (`pode_compor`, 403), `retificacao_editar`
  (`retificacao:elaborar`, 403), `auditoria` (`auditoria:consultar`, 403), `visao_geral`
  (`visao:consultar`, recusa explicada).
- **A faixa** (`interface/trabalho.py`) já filtra por capacidade, e é a única leitura em lote que o
  faz.
- **Papéis fora de `PAPEIS`** (`seguranca/acessos.py`): `integrante` (sem permissão),
  `administrador-de-acessos` (`acesso:gerir`, `acesso:consultar`) e `administrador-institucional`
  (escopo institucional). Os dois primeiros produzem um `Actor` com o escopo da unidade e por isso
  atravessam todas as rotas que só conferem escopo.
- **A comissão** chega pela lista (vínculos lidos em lote), por Minhas Etapas e pela Mesa. A Mesa e
  as etapas tratam Edital publicado; `alocacoes` lista os Editais do Processo (`editais_alocaveis`),
  e só mostra etapa de Edital publicado.
- **A Agenda, a trilha da unidade e o relatório do Edital** não exibem nada não publicado. A Visão
  Geral lista número, título e situação de Edital não publicado, sob `visao:consultar`.

---

## D-001 — Capacidade própria `rascunho:ler`

- **Decision**: uma permissão nova, `rascunho:ler`, escrita por extenso no `PAPEIS` de
  `interface/identidade.py`, nos papéis `elaborador`, `homologador`, `publicador` e `gestor`.
  Nenhum papel de acesso nem institucional a recebe. Depende da **P-1**.
- **Rationale**:
  - É a doutrina do catálogo, repetida em cada comentário dele: "capacidade própria, e não efeito
    de outra" (`inscricao:consultar`, `visao:consultar`, `aviso:enviar`, `matricula:exportar`). A
    leitura do não publicado responde a uma pergunta que nenhuma das existentes responde.
  - Destacá-la para outro papel custa uma linha, sem tocar nas portas.
  - O nome segue o padrão `objeto:verbo`. "Rascunho" cobre o Edital antes da Publicação e a
    Retificação antes da dela — o vocabulário que a `020` e a `103` já usam.
- **Alternatives considered**:
  - **o conjunto das capacidades de ato** (generalizar `LEITURA_DO_RASCUNHO` com `edital:publicar`,
    `edital:cancelar` e as de Retificação): funciona hoje, mas faz da leitura efeito colateral de
    outra permissão, e um papel futuro que recebesse `edital:cancelar` herdaria a leitura sem
    ninguém decidir;
  - **ler pela situação do Edital** em vez da existência de Publicação: erra no Edital cancelado
    sem publicação (EC-1).

## D-002 — Uma regra, na aplicação, em três níveis

- **Decision**: um módulo `publicacoes/application/leitura_do_nao_publicado.py` com:
  - `Alcance` — enumeração `NENHUM`, `EXISTENCIA`, `CONTEUDO`;
  - `alcance_do_edital(ator, edital, *, vinculos=None, publicado=None)`;
  - `alcance_da_retificacao(ator, retificacao)`;
  - `editais_visiveis(ator, editais, *, vinculos)` — o filtro em lote da lista, sem consulta nova.
  Edital publicado devolve `CONTEUDO` a todo ator do escopo. A pergunta "tem Publicação?" lê
  `edital.publicacoes`, pré-carregada em lote onde houver lista.
- **Rationale**: a FR-3506 pede uma regra só, consultável fora das views. Ela mora em
  `publicacoes` porque é lá que "publicado" se define; a interface só pergunta. Três níveis porque
  a spec distingue existência de conteúdo (FR-3504, FR-3503).
- **Alternatives considered**: a regra na interface, ao lado de `pode_compor` — seria a quinta
  derivação local, que é o que a FR-3506 proíbe.

## D-003 — Duas portas na interface, e a ordem delas

- **Decision**: dois auxiliares em `interface/views.py`, chamados logo depois de `obter_edital`:
  - `_edital_para_ler(request, edital_id, *, exige)` — `exige` é `EXISTENCIA` ou `CONTEUDO`;
  - `_retificacao_para_ler(...)` — o mesmo, sobre `_retificacao_do_ator`.
  A ordem é: identidade → escopo (o filtro da consulta) → `NENHUM` responde `Http404` →
  `EXISTENCIA` diante de `exige=CONTEUDO` responde pela recusa explicada → só então o estado (409)
  e a leitura.
- **Rationale**: a FR-3515 e o EC-4 — a conferência de estado não pode vir antes, ou o 409 conta a
  situação. Duas portas nomeadas entram na lista `PORTAS` de `test_gramatica_das_portas.py`, que
  afirma escopo na consulta e ponto único de autorização.
- **Alternatives considered**: um decorador de view — esconderia a ordem e não cobriria os
  fragmentos que recebem o Edital por `?edital=`.

## D-004 — Recusas: 404 para quem não tem a existência; recusa explicada para quem só tem a existência

- **Decision**:
  - `NENHUM` → `raise Http404`, a mesma resposta do inexistente e de outra unidade. O `if` que o
    guarda menciona a regra, e o inventário da `033` ganha as linhas, na classe "recusa de
    autorização — existência de ato não publicado", ao lado de `anexo_do_rascunho`.
  - `EXISTENCIA` diante de conteúdo → `require_authorization_base(False,
    bases=[base_de_permissao("ler o Edital antes da publicação")])` — 403 com "Peça a alguém com
    a permissão de ler o Edital antes da publicação".
- **Rationale**:
  - A doutrina dos anexos da `020`, da supervisão da `022` e de `minha_etapa`: o que não se pode
    enumerar responde como o inexistente. O inventário da `033` registrou essas sete como
    deliberadas em 18/09.
  - Para quem já sabe que o Edital existe (presidência, auditor), o 404 seria mentira e o
    "não permitido" mudo é o defeito que a `033` corrigiu; a recusa explicada é a gramática dela.
  - O detector `test_nenhuma_porta_responde_inexistente_para_recusa_de_autorizacao` lê os sinais
    `.can(` e `pode_*` no `if`. A guarda do 404 pergunta `alcance is Alcance.NENHUM`, que não é
    sinal, e a regra está classificada no inventário: é o mesmo estado em que `anexo_do_rascunho`
    vive hoje. **A T009 confere isso antes de escrever a porta**, e se o detector reprovar, a
    porta entra na lista com a justificativa — não se afrouxa o detector.
- **Alternatives considered**: 403 explicado para todos — diria ao integrante que o Edital existe,
  que é exatamente o vazamento da P-2 da `111`.

## D-005 — A trilha de auditoria fica como está

- **Decision**: `editais/<id>/auditoria` continua sob `auditoria:consultar`, e o auditor tem a
  existência do Edital não publicado para chegar até ela (FR-3504). A trilha continua mostrando as
  Retificações não publicadas (FR-3505).
- **Rationale**: auditar ato em preparação é o ofício do auditor, e a trilha é pergunta própria
  (Princípio III, "Logs e auditoria" — a trilha não expõe o conteúdo do rascunho, expõe eventos).
  Mudá-la é decisão separada; a P-4 a deixa aberta.

## D-006 — A lista filtra em lote

- **Decision**: em `lista`, o filtro `editais_visiveis` corre sobre os Editais já lidos, com as
  Publicações em `prefetch_related` e os vínculos que a view já lê (`comissoes_da_pessoa`). A
  chamada a `em_curso_por_edital` recebe só os Editais cujo alcance de Retificação é `CONTEUDO`, e
  nenhum quando o ator não tem `rascunho:ler` — o que **economiza** uma consulta para esse ator.
  `contar_por_situacao` passa a receber os Processos com os Editais já filtrados.
- **Rationale**: a FR-3526 e a SC-1065; a lista é a página mais aberta da gestão e já teve
  orçamento de consulta medido (`104`).

## D-007 — A barra não muda

- **Decision**: "Processos Seletivos" continua para toda identidade; nenhuma entrada nova.
- **Rationale**: a lista filtrada já não mostra o não publicado, e diz a quem não tem papel o que
  falta. Uma entrada própria para a Comunicação é UX da `111` e não substitui a porta — a URL do
  detalhe continuaria aberta por acesso direto.

## D-008 — A matriz e o guardião

- **Decision**:
  - `tests/authorization/test_leitura_do_nao_publicado.py`: matriz parametrizada rota × ator
    (FR-3524), com os cenários "Edital em elaboração", "homologado", "cancelado sem publicação",
    "publicado com Retificação em revisão" e "publicado com Retificação cancelada", e as doze
    identidades da FR-3524. Cada célula afirma 200, 403 explicado ou 404, e para 200 afirma que o
    HTML não contém o título do Edital não publicado quando o nível é menor.
  - `tests/test_rotas_do_nao_publicado.py`: lê `interface/urls.py` pelos `URLPattern` resolvidos,
    seleciona os que têm `edital_id`, `retificacao_id` ou `processo_id`, e reprova o que não está
    na tabela do [contrato](contracts/inventario-das-rotas.md); um caso testa o próprio detector,
    como `test_a_varredura_reconhece_uma_negativa_nao_registrada`.
  - `tests/authorization/test_papel_da_leitura_do_rascunho.py`: a grafia e o conjunto fechado de
    papéis com `rascunho:ler` (FR-3502, FR-3523), no padrão de `test_papel_do_aviso.py`.
- **Rationale**: a SC-1064 — o defeito desta spec existe porque nada reprovava rota nova que só
  conferisse escopo. Fragmentos com `?edital=` não têm o identificador na rota; o contrato os lista
  à parte e o guardião confere que todo chamador de `_edital_do_fragmento` está na lista.
