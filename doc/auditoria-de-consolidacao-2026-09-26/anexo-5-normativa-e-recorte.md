# Lote 5 — Granularidade normativa (AX), fontes sem confronto (E-4) e recorte

**Auditoria de consolidação · 25–26/09/2026 · contra `bb774d9` (= origin/main de 25/09)**
Somente leitura. Código lido diretamente; relatórios usados só como ponto de partida. Nenhum teste
rodado. Caminhos relativos a `backend/processo_seletivo/` salvo indicação.

**Fato de base que condiciona quase todo o lote.** Desde 15/09 o único commit em
`editais/models` e `editais/migrations` é o da `030` (`d9d47ed`, 18/09, que só acrescentou campos
ao Perfil). Os modelos de Perfil, Modalidade, Regra Normativa, Fato, Marco, Critério, Etapa e
Documento Exigido são **os mesmos** que a auditoria de 15/09 mediu. O que mudou depois de 19/09 e
toca este lote foi: `01d9163` (IMPEDE do recorte "Todos os Perfis" + Modalidade de um só),
`a2b1e1f` (instrução na Mesa e marca de facultativo), `0479f4e` (043, duplicar Perfil), a decisão
de 25/09 sobre o recorte documental (`doc/decisao-recorte-documental.md`) e a spec 044 — mesclada
na main só como spec/plan/tasks; a **implementação** está em `origin/claude/044-recorte-transversal-documental`
(PR #173, aberto, fora da main), e é tratada como IMPLEMENTADO, MAS NÃO VALIDADO onde toca um achado.

**Rótulo "integridade × custo de autoria"** — pedido para AX-1, AX-5, AX-6, AX-7, AX-14 e AX-16 —
aparece no campo "Impacto atual" de cada bloco.

---

### AX-1 — Sentido do desempate divergente entre Perfis, e o tipo do critério não se retifica
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-1 (15/09)
- Problema original: o 6.3.2 do Edital declara a ordem de desempate uma vez; o sistema a guarda como
  `Perfil → Marco → Critério` (1 → 3n). Na prévia, 2 de 9 blocos imprimiram "menor valor" onde o
  Edital manda "maior". Nada confronta os Perfis, e o `type` (onde mora o sentido) é não
  retificável.
- Recomendação original: famílias (a) regra de classificação no Edital; (b) marco herdado com
  sobrescrita; (c) conferência de publicação que exiba divergências entre Perfis sem decidir por
  elas; (d) declarar uma vez e materializar por Perfil (só alívio de digitação).
- Rastro posterior: varredura 19/09 ("🔴 aberto, pequeno"); convergência 20/09 §4 ("ABERTO,
  confirmado por código"); estudo 21/09 §13/E1–E2 (reuso dentro do Edital; "na amostra nenhum
  Perfil diverge dos irmãos"); 043 (25/09) implementa a família (d) por duplicação.
- Specs relacionadas: 015 (FR-015, FR-058), 026 (contrato de mutabilidade), 043.
- Implementação encontrada: só a família (d), via 043 — duplicar Perfil copia marcos e critérios de
  desempate com identidades novas (`editais/domain/duplicacao.py`; spec 043 FR-639/FR-641). Nenhuma
  conferência entre Perfis; nenhuma mudança na mutabilidade.
- Evidência no código atual:
  - `interface/retificacao.py:335` — `CAMPOS_CRITERIO = [("order", "Ordem de aplicação", INTEIRO)]`: a tela só retifica a ordem.
  - `editais/domain/mutabilidade.py:402-407` — `("tiebreakers","type")` é `nao_retificavel`, com razão normativa escrita; idem `parameters/stageId`, `parameters/factId` e `whenMissing` (`:408-421`).
  - `interface/retificacao.py:925-936` — o grupo do critério nasce com `removivel` padrão (`True`, `:586`): **remover** um critério é possível pela tela; **acrescentar** não — os únicos `ADD` emitidos são Perfil (`:1629`), linha do quadro (`:1676`), Anexo (`:1700`) e Evento (`:1769`); `SECOES_QUE_ACRESCENTAM = {perfis, cronograma, anexos}` (`:1054`). O caminho "remover e acrescentar outro" que a própria razão do contrato supõe fica **pela metade na interface** (a outra metade só pela API).
  - `editais/domain/validation.py` — nenhuma função compara critérios/fatos/percentuais entre Perfis (lista de funções `:300-2605`; o único confronto entre Perfis é o de `:2226`, que é de documento, ver AX-14).
  - `classificacao/domain/desempate.py:29-32` — `MAIOR_VALOR_DE_FATO` × `MENOR_VALOR_DE_FATO`: o sentido é o tipo.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente. A família (a)/(b) (mover a regra para o Edital) colide com a
  linha de decisão de 25/09 (conteúdo continua por Perfil — 043 §2, 044 §3) e a amostra não mostrou
  Perfil divergente. O que continua fazendo sentido é barato: (c) um AVISO na Revisão quando marcos
  de Perfis do mesmo Edital têm critérios de desempate diferentes (tipo, sentido, fato por código),
  sem impedir — divergência legítima continua publicável. E fechar a metade que falta do caminho de
  correção (acrescentar critério por Retificação, ou registrar por escrito que nasce só pela API).
- Lacuna residual: (i) nenhuma conferência entre Perfis; (ii) erro de sentido publicado não tem
  conserto completo pela interface.
- Grupo do resíduo: **B**
- Impacto atual: **integridade do que se publica** — o critério errado é publicado fielmente e
  executado (inverte a ordem de empatados), e não se corrige pela tela. A 043 reduz a probabilidade
  (a cópia é exata; o erro passa a nascer uma vez e se propagar, em vez de nascer por digitação em
  cada bloco), mas não a detecção.
- Próxima ação sugerida: criar spec curta (aviso de divergência entre Perfis + acréscimo de critério
  na Retificação) ou decidir e registrar que acrescentar critério é só API.
- Relações: mesmo mecanismo de AX-11 e AX-7 (E-1); raiz E-4 (fontes sem confronto) e estudo §13/E2.
  Sintoma de "o comum do certame mora no Perfil".
- Confiança: alta — leitura direta de contrato, tela e validação.

### AX-2 — Requisito de formação e documento que o comprova: dois textos livres sem vínculo
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-2 (15/09)
- Problema original: `PerfilVaga.requirements` e `DocumentoExigido.instructions` são campos livres
  independentes; na prévia o documento do LP04 comprovava requisito que o LP04 não tem, e o texto do
  TADS saiu embaralhado.
- Recomendação original: (a) requisito com identidade, documento aponta para ele; (b) `instructions`
  não repete o requisito e o PDF faz a remissão; (c) conferir divergência na publicação.
- Rastro posterior: varredura 19/09 ("🟠 provável, não confirmado a fundo"); convergência 20/09
  (herdado); estudo 21/09 (requisitos redigitados por Perfil, §6.2).
- Specs relacionadas: 006, 009, 043 (FR-639 copia requisitos; FR-645 **não** copia documentos).
- Implementação encontrada: nenhuma. 043 torna os requisitos entre Perfis iguais por cópia, mas
  documentos recortados por Perfil ficam fora da cópia — a relação requisito ↔ documento continua
  sem vínculo.
- Evidência no código atual: `editais/models/perfis.py:20` (`requirements = JSONField`) e
  `editais/models/documentos.py:29` (`instructions = TextField`), sem FK entre si; `DocumentoExigido`
  liga só a Anexo (`attachmentId`). Nenhum confronto em `validation.py`.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente. A conferência automática (c) é inviável — comparar duas prosas
  exige semântica. A família (b), remissão em vez de repetição, é boa prática de redação e cabe em
  orientação de cadastro; a (a) só se justifica se o requisito ganhar execução (hoje é texto).
- Lacuna residual: duas fontes livres do mesmo requisito podem se contradizer no documento publicado.
- Grupo do resíduo: **C**
- Impacto atual: integridade do texto publicado, mas causada por redação do autor; o sistema não
  tem como saber que as duas prosas falam da mesma coisa.
- Próxima ação sugerida: nenhuma de engenharia; eventual orientação na ajuda da etapa Documentos
  ("comprove o requisito do Perfil; não o reescreva").
- Relações: E-4 (fontes sem confronto); P-13 de `achados-editais-externos.md`.
- Confiança: média — mecanismo confirmado por código; a frequência depende de redação.

### AX-3 — Catálogo de Seções fechado: oito seções normativas do 140/2025 sem lugar próprio
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-3 (15/09)
- Problema original: `CATALOGO` fixo; Vagas, Prova de Títulos, Verificação da autodeclaração,
  Convocação, Mobilidade, Curso de formação, Vinculação UAB e Prazo de validade não têm onde morar.
- Recomendação original: (a) seções textuais livres; (b) catálogo maior; (c) separar "norma que o
  sistema executa" de "norma que só publica"; (d) aceitar que publica um extrato.
- Rastro posterior: varredura 19/09 (aberto); estudo 21/09 §9-bis e §13/E5 — **refina o achado**:
  as oito seções não somem, viram "parágrafo em caixa alta dentro de outra seção" (a norma é
  publicada como prosa; perde-se a hierarquia). §15 lista "o conjunto de seções do documento" entre
  as **três decisões do usuário antes de qualquer spec**.
- Specs relacionadas: 006 (FR-034), 007, 020.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/domain/secoes.py:1-11` (catálogo "declarado, e não
  gerenciável") e as 12 entradas `:50-160` (7 textuais, 5 geradas); último commit no arquivo é da
  020 (`1020f9d`).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente. A afirmação original de que a norma "não aparece em nenhuma
  forma" está superada pelo estudo: ela cabe em prosa nas seções textuais. O que resta é
  estrutura/fidelidade documental (títulos de primeiro nível que viram parágrafo) e a norma que
  deveria ser executável (convocação 10.5) — esta é AX-15/E7, não AX-3.
- Lacuna residual: hierarquia do documento publicado não reproduz a do Edital real.
- Grupo do resíduo: **B**
- Impacto atual: fidelidade/legibilidade do documento; não altera execução.
- Próxima ação sugerida: decisão do usuário (estudo §15, decisão 3) antes de spec.
- Relações: estudo §13/E5 (mesmo achado, outro lote); AX-12 depende dele (remissões a anexos vivem
  nas seções textuais).
- Confiança: alta.

### AX-4 — Ficha de Avaliação varia por curso, não existe como objeto; a Etapa é do Edital inteiro
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-4 (15/09)
- Problema original: duas fichas (Letras × TADS) colapsadas numa Etapa do Edital; barema (itens,
  limites, notas) inexistente; declarar duas Etapas não resolve, porque toda Etapa vale para todos.
- Recomendação original: (a) barema como objeto na Etapa; (b) Curso como dimensão; (c) Etapa com
  alcance por Perfil; (d) declarar que o sistema não conhece a regra de pontuação.
- Rastro posterior: varredura 19/09 (aberto); **039 (branch não mesclada)** — a 1ª redação
  (`ecb63e4`, 19/09) tinha a US2 "a Etapa que não vale para todos"; a reescrita (`cecba68`, 20/09) a
  tirou "por medição", registrando-a como "a candidata seguinte, e o defeito é mais grave para o
  candidato do que para o elaborador"; estudo 21/09 §13/E11 ("ficha de avaliação sem forma",
  observada no 140/2025 e no 14/2026).
- Specs relacionadas: 012 (pontuação máxima), 039 (rascunho), nenhuma na main.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/etapas.py:11-20` — docstring: "Pertence ao **Edital** e
  vale para todos os seus Perfis. A Constituição admite que Perfis possuam Etapas distintas, e
  admitir não é exigir … preço que se paga quando houver um Edital real que precise disso".
  `avaliacoes/models.py:36,77,180,234` — só `Atribuicao`, `Avaliacao`, `ConclusaoAvaliacao`,
  `Impedimento`; zero ocorrência de barema no backend.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, em duas partes de peso diferente. (i) **Barema como objeto**: sem ele a
  nota da banca não é conferível contra norma publicada e o recurso perde objeto — observado em dois
  Editais da amostra (E11). (ii) **Etapa com alcance por Perfil**: a Constituição
  (`.specify/memory/constitution.md:203-205`) diz que "Perfis PODEM possuir Etapas distintas" e que
  critérios, pontuação e acumulação "DEVEM existir no domínio/backend"; o modelo não permite. Na
  amostra, porém, as duas fichas do 140/2025 têm o mesmo teto e o mesmo tipo de Etapa — o caso
  bloqueante (curso com redação × curso sem) é hipotético, do rascunho da 039.
- Lacuna residual: barema inexistente; Etapa sem alcance.
- Grupo do resíduo: **B** (com a ressalva de leitura constitucional nas Incertezas)
- Impacto atual: execução opera (banca pontua fora do sistema contra o teto de 100), mas a regra de
  pontuação não é publicada nem conferida.
- Próxima ação sugerida: criar spec quando o usuário priorizar; a 039 já registrou o alcance da
  Etapa como candidata.
- Relações: estudo §13/E11 (mesmo achado); AX-10 (título pontuável como "documento facultativo");
  AX-5 (o alcance natural da Etapa seria o curso).
- Confiança: alta.

### AX-5 — Curso, Área e Campus ofertante não existem; sobrevivem só no prefixo do código
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-5 (15/09)
- Problema original: o ANEXO III é matriz `CURSO | ÁREA | PERFIL | FUNÇÃO | POLO | CÓDIGO`; o
  sistema tem `code`, `name`, `locality`. O candidato não descobre pelo documento para qual curso
  concorre; `LP`/`TADS` não é evidência normativa.
- Recomendação original: (a) Curso como objeto do Edital; (b) dimensão genérica de agrupamento
  declarada pelo Edital; (c) aceitar.
- Rastro posterior: varredura 19/09 (aberto); convergência 20/09 §5 cenário D e §17 ("não abstrair
  polo antes de ter o Edital real de múltiplos polos"); 040 (21/09) `G-004` — "não há dimensão de
  campus ou polo abaixo do escopo", filtro não oferecido; estudo 21/09 — o operador contorna pondo o
  curso no nome ("Classificação final — Tutor Presencial / Supervisor de Estágio — Letras",
  `doc/diario-estudo-esforco-2026-09-21.md:534`).
- Specs relacionadas: 040 (G-004), 041 (§ fora de escopo: "Polo como dimensão").
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/perfis.py:9-95` — `PerfilVaga` sem Curso/Área/Campus;
  identidade `uq_perfil_edital_code` (`:95`). Modelos inalterados desde a 030.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente. Como dimensão de **execução** não: a população de apuração da
  cota ("por curso/área/polo") coincide com o código, que o sistema já tem. Como dimensão de
  **agrupamento de leitura** (b) sim, e ela seria a âncora natural do alcance da Etapa (AX-4) — mas
  só vale o custo se AX-4 for priorizado; sozinha, o nome do Perfil cobre o caso.
- Lacuna residual: documento de Edital multicurso não se agrupa por curso; nada valida o prefixo.
- Grupo do resíduo: **C** (sobe para B se AX-4 entrar)
- Impacto atual: **custo de autoria e de leitura**, não integridade — nada publicado contradiz o que
  se executa.
- Próxima ação sugerida: nenhuma isolada; considerar junto com AX-4.
- Relações: P-5 de `achados-editais-externos.md`; AX-6; ACH-60 (trabalho sem Perfil/polo — outro
  lote); E-6/040 G-004.
- Confiança: alta.

### AX-6 — O código não é o polo: é o par (perfil de formação × polo)
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-6 (15/09)
- Problema original: LP01 e LP04 são o mesmo município com perfis diferentes; corrige a premissa de
  `achado-atribuicoes-repetidas-por-polo.md`. Tabela 1 fica com linhas iguais distinguíveis só pelo
  código.
- Recomendação original: as do AX-5, com dois eixos declarados e o código derivado do par.
- Rastro posterior: convergência 20/09 (§5 cenário D 🔴, §17: "polo como eixo — precisa de Edital
  real de múltiplos polos antes"); 040 `G-004`; 041 fora de escopo.
- Specs relacionadas: 040, 041.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/perfis.py:95` (`uq_perfil_edital_code`); `locality`
  texto livre. `publicacoes/infrastructure/pdf.py:1940-1960` — `_rotulo_do_perfil` compõe
  `código — nome`, o que distingue as linhas pelo código (fix `c0403a9`), mas não mostra o perfil de
  formação.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: não como achado próprio. É diagnóstico que condiciona a forma de qualquer
  solução de AX-5 (se um dia vier, dois eixos, não um). O defeito observável (Tabela 1 ambígua) é
  pequeno e o código já desambigua.
- Lacuna residual: nenhuma além da de AX-5.
- Grupo do resíduo: **C**
- Impacto atual: custo de leitura; nenhuma integridade em jogo.
- Próxima ação sugerida: nenhuma; manter como premissa registrada para AX-5.
- Relações: AX-5; P-5; ACH-60 (outro lote) na face operacional (comissão por polo).
- Confiança: alta.

### AX-7 (+ experimento E-1) — Modalidade e regra de cota amplificadas por Perfil; 3% × 30% sem conferência
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-7 e §Experimento E-1 (15/09)
- Problema original: `ModalidadeConcorrencia → PerfilVaga`, `RegraNormativa 1:1 Modalidade`,
  documento condicionado → Modalidade de um Perfil. 4 → 4n, 3 → 4n, 5 → 5n. E-1 publicou 3% e 30%
  para a mesma lei, em tabelas vizinhas, sem nenhuma conferência.
- Recomendação original: (a) redefinir Perfil; (b) Modalidade e regra como objetos do Edital, com o
  quadro continuando por Perfil; (c) aceitar 4n. O próprio achado registrou o conflito parcial com
  "Cotas DEVEM ser definidas por Perfil" e disse que a solução exige decisão do usuário.
- Rastro posterior: varredura 19/09 — a conferência que existe (`_divergencia_do_percentual`, da
  025) é **dentro** da linha, não entre Perfis; convergência 20/09 §4 e §17 (E-4 aberto; D-G5 —
  acrescentar Modalidade por Retificação, sem spec); **039 (20/09, não mesclada)** propôs exatamente
  a família (b): "O Edital declara suas Modalidades uma vez … cada Perfil declara quais oferece"
  (`git show claude/spec-039-alcance:specs/039-catalogo-de-modalidades/spec.md`, D-001);
  **decisão de 25/09** (`doc/decisao-recorte-documental.md`, "O que já está fixado"): *"A Modalidade
  continua sendo do Perfil. Mover a propriedade dela para o Edital está fora de questão"*; D1: a
  coerência transversal cobre "só a denominação, nunca percentual ou fundamento", porque "a cota é do
  Perfil, e o percentual pode variar legitimamente"; 044 §3 "Não move a Modalidade para o Edital";
  043 §2 idem; 043 implementada duplica Modalidades com regra normativa.
- Specs relacionadas: 025, 027, 039 (rascunho), 043, 044.
- Implementação encontrada: 043 (duplicar Perfil copia as 4 Modalidades e as regras — alívio de
  digitação); 044 para o recorte transversal do documento (a parte 5 → 5n) — **implementada só na
  branch/PR #173, fora da main**, e com IMPEDE de coerência que cobre só a denominação. Nenhuma
  conferência de percentual/fundamento entre Perfis, nem na main nem na branch.
- Evidência no código atual: `editais/models/perfis.py:110-119` (`ModalidadeConcorrencia.perfil`,
  `uq_modalidade_perfil_code`) e `:376-378` (`RegraNormativa` 1:1); `editais/domain/validation.py:2563`
  (`_divergencia_do_percentual`, linha a linha) e `:1188` (`_faixa_do_percentual`, faixa do valor) —
  nenhuma compara Perfis; `editais/domain/mutabilidade.py:150-160` — `callRules`, `calculation`,
  `rounding`, `distribution` da regra seguem **opacos**.
- Estado atual: **CONTRADITO POR DECISÃO POSTERIOR** — a recomendação estrutural (b), que a 039
  tentou, foi recusada pela decisão de 25/09 (`doc/decisao-recorte-documental.md`) e pelas specs
  043 §2 e 044 §3; a amplificação 4n passa a ser o desenho assumido, com a duplicação como remédio de
  custo.
- Ainda faz sentido?: parcialmente. Mover a Modalidade não (decidido). Mas a divergência medida em
  E-1 continua publicável sem sinal, e a própria decisão admite que percentual "pode variar
  legitimamente" — o que pede **aviso**, não recusa. Um AVISO na Revisão quando Modalidades de mesmo
  código em Perfis diferentes divergirem em percentual ou fundamento é coerente com a decisão
  (não decide pela pessoa) e barato.
- Lacuna residual: nenhuma conferência entre Perfis de percentual/fundamento; correção de fundamento
  continua custando n Alterações.
- Grupo do resíduo: **B**
- Impacto atual: **integridade do que se publica** no caso E-1 (o ato afirma duas coisas sobre a
  mesma lei) e **custo de autoria/retificação** no resto; a 043 reduz o segundo e, por cópia exata,
  a chance do primeiro.
- Próxima ação sugerida: corrigir (aviso de divergência entre Perfis de mesmo código), se o usuário
  aceitar; a 044 (branch, PR #173) já introduz o IMPEDE de coerência da **denominação** por código
  (`_denominacoes_do_codigo`) — o aviso de percentual/fundamento caberia ao lado, como AVISO.
- Relações: E-4 (fontes sem confronto); AX-1/AX-11 (mesmo mecanismo); AX-14 (caso extremo);
  D-G5 (acrescentar Modalidade a Edital publicado — ver bloco da 039); PR #172 é sintoma na gestão.
- Confiança: alta quanto ao código; média quanto ao alcance da decisão (ver Incertezas).

### AX-8 — Número do Edital com duas fontes; a capa pode citar outro ato
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-8 (15/09)
- Problema original: capa usa `title` quando ele começa por "EDITAL", descartando `number`/`year`;
  rodapé usa `number`/`year`. Na prévia: capa "EDITAL 140/2025", rodapé "Edital 149/2026". O número
  estruturado é irretificável; o título livre é retificável e não conferido.
- Recomendação original: (a) capa sempre compõe de `number`/`year`; (b) validação que recuse título
  com número diferente do declarado; (c) título sem prefixo "Edital"; (d) conferir na leitura.
- Rastro posterior: varredura 19/09 ("🟠 provável"); convergência 20/09 (herdado); nada depois.
- Specs relacionadas: 007, 023.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `publicacoes/infrastructure/pdf.py:879-889` — `anuncio = titulo if
  titulo.upper().startswith("EDITAL") else …` (o comentário justifica: evitar anunciar o ato duas
  vezes); rodapé em `:2189` e `:2303` com `number`/`year`; `editais/domain/validation.py:1366-1370`
  só exige `title` não vazio; `editais/domain/mutabilidade.py:177-195` mantém a assimetria (número
  irretificável, título retificável); `editais/application/identificacao.py:21-60` não confere o
  título contra o número.
- Estado atual: **NÃO IMPLEMENTADO** (confirmado por código; a varredura de 19/09 o deixava como
  "provável")
- Ainda faz sentido?: sim, na forma (b) como AVISO/IMPEDE — é uma regex sobre `title` comparada com
  `number/year`, de custo mínimo e sem tocar modelo. (a) também é barata, mas muda a capa de todos os
  Editais cujo título já começa por "Edital".
- Lacuna residual: o ato publicado pode se identificar com dois números.
- Grupo do resíduo: **B** (integridade barata de fechar; corrigível por Retificação do título, o que
  impede classificá-la como A)
- Impacto atual: integridade do documento publicado (identificação do ato), com gatilho humano
  (colar título do Edital de origem).
- Próxima ação sugerida: corrigir (conferência de publicação título × número/ano).
- Relações: E-4; relação com 023 (reuso induz a colagem).
- Confiança: alta.

### AX-9 — Teto de inscrições por candidato executado, retificável, e não publicado em canal nenhum
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-9 (15/09)
- Problema original: `max_inscricoes_por_candidato` entra no snapshot, é retificável e recusa
  submissão com 409, mas nem PDF nem portal nem consulta pública o dizem.
- Recomendação original: (a) PDF e portal declaram o teto; (b) varredura de contrato que exija, para
  todo campo retificável, um canal de exibição; (c) aceitar.
- Rastro posterior: varredura 19/09 ("zero ocorrências em `divulgacao/` e `portal/`"); 023 spec
  (`specs/023-…/spec.md:171`) já registrava que o campo **não é copiado** porque "nenhuma etapa do
  assistente oferece"; 029 spec (`:906`) cita como precedente de "campo de raiz não renderizado".
- Specs relacionadas: 015 (FR-063 a FR-066), 023, 026, 029.
- Implementação encontrada: nenhuma.
- Evidência no código atual: todas as ocorrências de `maxInscricoesPorCandidato` fora de testes:
  `processos/models.py:63`, `publicacoes/application/publish_edital.py:318`,
  `inscricoes/application/submissao.py:307` (executa), `editais/domain/mutabilidade.py:195`,
  `interface/retificacao.py:119` (retifica), `seed_demo.py:875`. **Nenhuma** em `pdf.py`, templates do
  portal ou `interface/forms.py`/composição. Achado de passagem (ver NOVOS): o teto **não é
  declarável na composição** — só por Retificação depois de publicado, ou pela semente.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, e o recorte certo hoje é maior que o de 15/09: FR-063 ("o Edital MUST
  poder publicar um teto") está entregue só no motor. Pela tela, o teto só nasce por Retificação — e
  aí é executado sem aparecer no documento. A saída (b) do achado (varredura "retificável ⇒ tem
  canal") continua a melhor proteção de classe.
- Lacuna residual: norma executável sem publicação; e sem campo na composição.
- Grupo do resíduo: **B** (o Edital real escreve "1 inscrição por candidato" em prosa na seção de
  inscrição; o sistema simplesmente não executa — risco de execução-sem-norma só aparece se alguém
  retificar o campo)
- Impacto atual: integridade do ato quando o teto existe (recusa sem norma publicada); lacuna de
  capacidade quando não existe.
- Próxima ação sugerida: corrigir (renderizar o teto na seção de inscrição e no portal) e decidir se
  ganha campo na etapa Inscrição.
- Relações: `achado-objeto-normativo-sem-forma.md` (mesmo padrão, lado oposto); 026 (contrato).
- Confiança: alta.

### AX-10 — "Documentos exigidos" funde naturezas; títulos pontuáveis entram como facultativos
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-10 (15/09)
- Problema original: `DocumentoExigido` tem `required` e dois recortes (Perfil, Modalidade); não há
  natureza (obrigatório geral / comprobatório / condicionado / pontuável / formulário). Condição
  sobre a pessoa (sexo, idade) sem dimensão. O PDF imprimiu o barema como cinco "(facultativo)".
- Recomendação original: (a) natureza declarada e PDF agrupando; (b) pontuável passa ao barema
  (AX-4); (c) manter como orientação.
- Rastro posterior: estudo 21/09 §5.9 e §13/E6 (nove obrigatórios publicados como facultativos no
  140/2025); achado do portal 25/09 (`doc/achado-documento-condicional-no-portal.md`); conferência
  25/09; **decisão 25/09** D2 — condição sobre o candidato fica como "opção 1" (informativa, à mão)
  "como estado assumido", spec própria depois; duas correções diretas; D5 — 044 faz só o recorte
  transversal e a lista gravada.
- Specs relacionadas: 009, 020, 044 (spec).
- Implementação encontrada: `a2b1e1f` (25/09) — a instrução chega à Mesa
  (`avaliacoes/application/mesa.py`, `interface/templates/interface/mesa_inscricao.html`) e a
  Revisão do portal mantém a marca "(facultativo)" (`portal/templates/portal/revisao.html`), testes
  `tests/portal/test_revisao_marca_o_facultativo.py` e `tests/interface/test_mesa_modelo_exigido.py`.
  044 fará "obrigatório para todo PcD" caber numa linha — **implementada só na branch/PR #173, fora
  da main** (IMPLEMENTADO, MAS NÃO VALIDADO; ver bloco da 044).
- Evidência no código atual: `editais/models/documentos.py:21-64` inalterado (`required`, `perfil`,
  `modalidade`; nenhum campo de natureza nem de condição); `pdf.py:2021` (`_documentos_exigidos`)
  continua agrupando só por alcance.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente. A parte "condicionado à modalidade publicado como facultativo" é
  exatamente o que a 044 fecha — e está decidida. A condição sobre a pessoa foi **adiada por decisão**
  (D2). O que sobra da recomendação original é a natureza "título pontuável", que pertence ao barema
  (AX-4) e não a documentos.
- Lacuna residual: até a 044, documento obrigatório de modalidade continua saindo facultativo ou em
  5n linhas; título pontuável sem forma.
- Grupo do resíduo: **B** (resolvido pela 044 no que é modalidade; o resto depende de AX-4)
- Impacto atual: candidato lê obrigatório como facultativo (integridade do comunicado ao candidato),
  mitigado pela marca e pela instrução na Mesa.
- Próxima ação sugerida: validar e mesclar a 044 (PR #173 — decisão do usuário); nada novo além dela.
- Relações: AX-14 (mesmo recorte), AX-4, estudo §13/E6, decisão D2.
- Confiança: alta.

### AX-11 — Fatos declarados são do certame e moram no Perfil
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-11 (15/09)
- Problema original: `FatoDeclarado → PerfilVaga` (`3 → 3n`); o tipo não se retifica; 16 "Data de
  nascimento" com 16 identidades.
- Recomendação original: as mesmas do AX-1 (fato e regra no mesmo nível).
- Rastro posterior: decisão 25/09 D2 cita a mesma limitação ("são por Perfil, e a condição costuma
  valer para o Edital todo"); 043 copia os fatos e remapeia o `factId` dos critérios (FR-641).
- Specs relacionadas: 015 (FR-058), 043.
- Implementação encontrada: só a duplicação (043).
- Evidência no código atual: `editais/models/perfis.py:192-221` (`FatoDeclarado.perfil`,
  `uq_fato_perfil_code`); `interface/retificacao.py:325-329` — `CAMPOS_FATO` só `label`, e o
  comentário registra que a ausência do tipo "é a regra".
- Estado atual: **PARCIALMENTE RESOLVIDO** (custo de autoria reduzido pela 043; granularidade
  mantida por decisão)
- Ainda faz sentido?: pouco. Não houve divergência medida; com a duplicação, a cópia é exata. Se o
  aviso de divergência do AX-1 for feito, deve cobrir o fato (tipo por código) de passagem.
- Lacuna residual: tipo errado num Perfil continua irretificável; nada compara fatos entre Perfis.
- Grupo do resíduo: **C**
- Impacto atual: custo de autoria (já reduzido); risco de integridade baixo.
- Próxima ação sugerida: nenhuma isolada; incluir no aviso do AX-1.
- Relações: AX-1, AX-7; decisão 25/09 D2 (fatos como veículo de condição — descartado por ora).
- Confiança: alta.

### AX-12 — Anexos publicados como lista; nenhuma integridade referencial entre texto e anexo
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-12 (15/09)
- Problema original: nada verifica se "ANEXO IV" citado numa seção textual tem anexo, nem buracos ou
  repetições de numeração.
- Recomendação original: (a) conferência que case `ANEXO \w+` das seções com os rótulos; (b) número
  como campo; (c) manter.
- Rastro posterior: estudo 21/09 §14 — **materializado**: "o documento publicado cita `ANEXO I` a
  `ANEXO XI` sem publicar nenhum" (o operador não pôde enviar os PDFs, e a publicação passou).
- Specs relacionadas: 020 (D-002, D-006, FR-005, FR-022, FR-023).
- Implementação encontrada: nenhuma além do que já existia.
- Evidência no código atual: `editais/domain/validation.py:2104-2161` — `_coerencia_dos_anexos`
  confere rótulo vazio (IMPEDE), rótulo repetido (AVISO) e `attachmentId` pendurado (IMPEDE);
  **nenhuma** leitura do conteúdo das seções textuais.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, e mais do que em 15/09 — a remissão morta deixou de ser hipótese (estudo
  §14). A forma (a) como AVISO ("a seção X cita ANEXO IV, e nenhum anexo tem esse rótulo") é barata
  e não decide redação.
- Lacuna residual: remissão a anexo inexistente publica sem sinal.
- Grupo do resíduo: **B**
- Impacto atual: integridade referencial do documento publicado.
- Próxima ação sugerida: corrigir (aviso na Revisão).
- Relações: `achado-anexo-sem-destinatario.md` (face oposta); AX-3 (as remissões vivem na prosa).
- Confiança: alta quanto à ausência; média quanto à frequência.

### AX-13 — Cabeçalho de alcance dizia só o nome do Perfil
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-13 (15/09)
- Problema original: nove cabeçalhos idênticos "Dos candidatos ao perfil Tutor Presencial".
- Recomendação original: já corrigido no próprio dia (`c0403a9`).
- Rastro posterior: varredura 19/09 deixou como "percurso".
- Specs relacionadas: 009/020 (documentos por alcance).
- Implementação encontrada: `_rotulo_do_perfil` compõe `código — nome`.
- Evidência no código atual: `publicacoes/infrastructure/pdf.py:1940-1960` e uso em `:1963-1968`
  (`_nomes_do_alcance`) e `:1984` (`Dos candidatos ao perfil {rótulo}`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma.
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: achado de 15/09 (atribuições repetidas por polo).
- Confiança: alta.

### AX-14 / AX-17 (+ experimento E-2) — O documento publicado diz "toda a modalidade"; a execução aplica a um Perfil
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-14, §AX-17, §Experimento E-2
  (15/09). AX-17 é a correção de rumo do AX-14 (causa no renderizador, não na tela).
- Problema original: documento com `modalityId` da PcD do LP01 e `profileId` nulo é aceito; o PDF
  imprime "Dos candidatos concorrentes na modalidade Pessoa com Deficiência" (sem Perfil); a
  inscrição aplica pela **identidade** e só o LP01 recebe a exigência (1 de 3; 1 de 16 no real). O
  caminho fiel custa 5n registros e 5n chaves inventadas.
- Recomendação original: (a) Modalidade do Edital; (b) aplicabilidade por código; (c) recusar
  `modalityId` sem `profileId` com mais de um Perfil; (d) conferência de publicação que compare
  alcance declarado com alcance executável. AX-17: (a) o cabeçalho nomeia o Perfil da modalidade;
  (b) recusar na elaboração; (c) as duas.
- Rastro posterior: varredura 19/09 ("a validação confere existência, não alcance"; "se confirmar, é
  mais grave que a E-4"); estudo 21/09 §5.9/§13/E6 (112 linhas para 7 documentos); **achado do
  portal 25/09** (`doc/achado-documento-condicional-no-portal.md`) — reproduziu pela tela no
  903/2026: PDF exige o laudo de todo PcD, portal só o pede no C1; conferência do envio 25/09
  (analista indeferiu por documento que o sistema nunca pediu); **`01d9163` (#161, 25/09)** fecha a
  contradição por IMPEDE; decisão 25/09 D1/D3; **044** (recorte transversal por código + lista gravada
  no envio) especificada na main e **implementada só na branch** `origin/claude/044-…` (PR #173,
  aberto).
- Specs relacionadas: 009, 025 (R-006 recusou casar por nome), 044.
- Implementação encontrada: a família (d)/(c) — conferência de publicação que recusa o recorte cujo
  alcance publicado (por **nome**) é mais largo que o executado (por **identidade**).
- Evidência no código atual:
  - `editais/domain/validation.py:2213-2216` chama, para documento sem Perfil,
    `_recorte_que_o_documento_publicado_alarga` (`:2226-2275`): IMPEDE
    `document_requirement_modality_scope_ambiguous` quando o rótulo da Modalidade se repete em outro
    Perfil, com a saída escrita na mensagem. Vale em publicação **e** Retificação
    (`validate_for_publication` sem dependência de `ato`; chamada em
    `publicacoes/application/retificacoes.py:531`). Testes:
    `tests/unit/editais/test_validacao_inscricao.py::test_todos_os_perfis_com_a_modalidade_de_um_so_e_impeditivo_quando_o_nome_se_repete`,
    `::test_o_mesmo_recorte_com_o_perfil_declarado_passa`, `::test_modalidade_que_so_um_perfil_tem_nao_e_acusada`.
  - `editais/domain/documentos.py:97-110` — `aplicaveis` continua comparando identidade (inalterado,
    correto pelo desenho).
  - `publicacoes/infrastructure/pdf.py:1973-1990` — `_titulo_do_grupo` continua compondo "Dos
    candidatos concorrentes na modalidade X" sem Perfil quando `profileId` é nulo (AX-17 família (a)
    **não** feita) — mas o caso em que isso mente agora não publica.
  - `interface/templates/interface/compor_inscricao.html:46-47` — a ajuda ainda diz "ou só para uma
    modalidade" (a frase que o AX-17 apontou como indutora); a gravação da etapa aceita a combinação,
    e o sinal vem na Revisão.
  - O Documento Exigido tem `profileId`/`modalityId` retificáveis pela tela
    (`interface/retificacao.py:368-379`), então Edital do acervo com a contradição tem saída no mesmo
    ato de Retificação.
- Estado atual: **RESOLVIDO** quanto à contradição documento × execução (pela família (d), não pela
  (a) do AX-17); a amplificação 5 → 5n está **absorvida pela 044** — IMPLEMENTADO, MAS NÃO VALIDADO, **fora
  da main** (PR #173); na main o custo 5n continua.
- Ainda faz sentido?: a parte de integridade, não — está fechada e testada. A parte de custo, sim, e
  já tem decisão, spec e implementação pendente de merge (044/PR #173). A ajuda da etapa Documentos
  só fica verdadeira quando a 044 entrar na main.
- Lacuna residual: (i) custo 5n até a 044; (ii) o IMPEDE depende de igualdade de **rótulo** — duas
  Modalidades de mesmo sentido com nomes diferentes ("PcD" × "Pessoa com Deficiência") escapam, e o
  PDF continua sugerindo alcance amplo (a 044 D1 resolve por código + coerência de denominação);
  (iii) Editais publicados antes de 25/09 com o recorte contraditório continuam dizendo o que
  disseram (imutáveis) — se existirem.
- Grupo do resíduo: **B** (custo, via 044) — o grave (A) foi fechado.
- Impacto atual: era **integridade do que se publica** (o mais grave do lote: ato normativo e regra
  aplicada divergiam, e a fração de prejudicados crescia com n). Hoje é **custo de autoria**.
- Próxima ação sugerida: validar e mesclar a 044 (PR #173, decisão do usuário); validar se há Edital
  publicado antes de 25/09 com o recorte contraditório (ver Incertezas).
- Relações: AX-7 (caso extremo), AX-10, E-4 ("três leituras da mesma Modalidade": portal por
  identidade, PDF por nome, #161 por nome/código — `doc/decisao-recorte-documental.md`); PR #172
  (mesma ambiguidade, na consulta do Gestor).
- Confiança: alta — código, testes e reprodução pela tela em 25/09.

### AX-15 — Submodalidades de PPIQ não existem
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-15 e E-2 (15/09)
- Problema original: o 140/2025 convoca Pretos/Pardos, Indígenas e Quilombolas em posições distintas
  (10.5), com reversão entre elas (10.5.1), documentos distintos e heteroidentificação só de
  pretos/pardos; o sistema tem Modalidade plana.
- Recomendação original: (a) submodalidade abaixo da Modalidade; (b) irmãs com cota no grupo;
  (c) aceitar que Editais com subdivisão não são representáveis.
- Rastro posterior: estudo 21/09 §13/E7 (mesmo achado, com a tabela de 50 posições); decisão 25/09
  e 044 §1/§3 — **fora por decisão do usuário** ("Não é submodalidade"; três documentos do 140/2025
  seguem facultativos; "limite E7 … registra sem resolvê-lo").
- Specs relacionadas: 016 (reversão), 019 (convocação), 044 (exclui).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/perfis.py:110-119` — Modalidade plana (código, nome,
  percentual via regra); `callRules` opaco e não retificável (`editais/domain/mutabilidade.py:150-160`).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim como evolução — é o único ponto do lote em que uma regra de **execução**
  (ordem de convocação, reversão entre subgrupos, heteroidentificação) não é representável. Mas é
  grande, e a amostra só tem um Edital com a forma.
- Lacuna residual: convocação por submodalidade, reversão hierárquica e documentos por subgrupo.
- Grupo do resíduo: **B**
- Impacto atual: Edital com subdivisão de reserva é publicado como extrato; a convocação real ocorre
  fora do sistema.
- Próxima ação sugerida: nenhuma agora (decisão registrada na 044); reabrir quando houver segundo
  Edital com a forma.
- Relações: estudo E7; H-3 (heteroidentificação por código); `achados-editais-externos.md:280`
  (reversão hierárquica).
- Confiança: alta.

### AX-16 — Restaurar o rascunho local perde as coleções aninhadas e regrava a perda
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §AX-16 e §Experimento E-3 (15/09)
- Problema original: `restaurar()` recria cada Perfil com o fragmento de Perfil vazio; `preencher()`
  só casa nomes de três segmentos; campos de Modalidade (quatro segmentos) caem em `simples` e são
  descartados; o HTML inserido não passa por `htmx.process()` (botões inertes); o autosave regrava o
  estado incompleto por cima.
- Recomendação original: (a) recriar coleções aninhadas e chamar `htmx.process()`; (b) não regravar
  antes de confirmar restauração completa; (c) guardar HTML; (d) remover a salvaguarda.
- Rastro posterior: varredura 19/09 ("❓ percurso — a rede da 032 é round-trip de servidor; o AX-16 é
  a restauração no navegador"); convergência 20/09 (herdado); estudo 21/09 §16 **elogia** a
  salvaguarda ("Há preenchimento não enviado… Restaurar"), mas o diário não registra ter restaurado
  Perfil com Modalidades (`doc/diario-estudo-esforco-2026-09-21.md:61-63`, `:539-542`).
- Specs relacionadas: 002 **FR-020** ("preservar o conteúdo em preenchimento … permitindo retomar sem
  redigitação"), 003, 043 (FR-650 — marcos da cópia sobrevivem à recusa **do servidor**).
- Implementação encontrada: nenhuma. Último commit em `rascunho.js` é `4e9f0a0` (08/09), anterior à
  auditoria.
- Evidência no código atual: `interface/static/interface/rascunho.js:81` (`ler()` só reconhece
  `^([a-z]+)-(\d+)-(\w+)$`; `modalidade-3-1-code` vai para `simples`), `:104-118` (`preencher` com o
  mesmo padrão), `:120-133` (`restaurar`: `replaceChildren()`, `fetch(fragmento)`,
  `insertAdjacentHTML`, e `form.elements[nome]` que é `undefined` para os campos aninhados), `:225`
  (`MutationObserver` → `agendar` → regrava); nenhum `htmx.process` no arquivo. Os campos de
  Modalidade seguem com quatro segmentos (`interface/templates/interface/_modalidade.html:8-45`) e a
  etapa Perfis liga a salvaguarda (`compor_perfis.html:5-6`). `tests/javascript/rascunho.test.js` só
  cobre validade, recibo e rádio — nada de coleção aninhada.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim. O código é o de 15/09 e o requisito escrito (FR-020 da 002) é
  descumprido para a etapa mais cara do assistente. E a 043 agravou a superfície: o Perfil duplicado
  e ainda não gravado carrega os marcos num oculto `perfil-N-marcosEmTransito`
  (`interface/templates/interface/_perfil.html:4`) que o fragmento vazio não tem — restaurar uma
  cópia perde os marcos dela em silêncio (inferência por leitura; não reproduzido).
- Lacuna residual: perda silenciosa de Modalidades, Regras, fatos, linhas do quadro e (agora) marcos
  da cópia; tela inoperante após restaurar; perda regravada.
- Grupo do resíduo: **A** (contradiz FR-020 da 002; perda silenciosa)
- Impacto atual: **custo de autoria** (anterior à publicação), não integridade do publicado — mas
  induz redigitação, que é onde as cópias divergem (AX-1/AX-7).
- Próxima ação sugerida: validar pela tela (um Perfil com uma Modalidade, sair sem gravar,
  restaurar) e corrigir — ou, na falta de prioridade, restringir a salvaguarda às etapas sem
  coleção aninhada (família (d) parcial), para ela parar de prometer o que não entrega.
- Relações: memória "replace_draft apaga o que não for reenviado" (mesma família, lado do servidor —
  fechado por `PRESERVADO_DA_ETAPA` e `test_round_trip_do_rascunho.py`); E2E-006 (02/09, outro
  defeito da mesma salvaguarda, corrigido).
- Confiança: alta pelo código (inalterado desde a reprodução de 15/09); a extensão à 043 é média.

### E-3 (experimento) — Custo de autoria: 1.300+ campos e nenhum "copiar/duplicar"
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §Experimento E-3, "Custo de autoria,
  medido" (15/09)
- Problema original: "não existe botão de copiar, duplicar ou replicar"; o segundo Perfil nasce em
  branco; ~640 campos só para 16 Perfis com 4 Modalidades.
- Recomendação original: nenhuma explícita (medição); consumida pelo estudo 21/09 §13/E1.
- Rastro posterior: estudo 21/09 (~530 interações na etapa Perfis, ~430 sem informação nova; frente
  2 da §15); **043 implementada** (`0479f4e`, 25/09).
- Specs relacionadas: 043.
- Implementação encontrada: "Duplicar este Perfil" na etapa Perfis — copia tudo do Perfil (inclusive
  Modalidades, regra, quadro, fatos, marcos e critérios), com identidades novas; **não** copia
  Documentos Exigidos (FR-645) e não oferece "aplicar a todos" (fora por decisão, §Clarifications).
- Evidência no código atual: `editais/domain/duplicacao.py` (183 linhas), `interface/views.py`
  (+265), `interface/templates/interface/_duplicar_perfil.html`; testes
  `tests/unit/editais/test_duplicacao.py`, `tests/interface/test_duplicar_perfil.py`,
  `tests/authorization/test_duplicar_perfil.py`.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: o que falta já tem dono: documentos (044 — implementada na branch/PR #173, fora
  da main) e propagação em massa (spec futura registrada na 043 §5).
- Lacuna residual: 5n documentos; editar depois continua sendo editar n.
- Grupo do resíduo: **B**
- Impacto atual: custo de autoria (reduzido de ~33 para ~6 interações por Perfil, estimativa da 043).
- Próxima ação sugerida: nenhuma além da 044.
- Relações: AX-1, AX-7, AX-11 (família (d) desses achados).
- Confiança: alta.

### 039 (branch não mesclada `claude/spec-039-alcance`) — Catálogo de Modalidades do Edital / alcance declarável
- Origem: `git log main..claude/spec-039-alcance` — dois commits só de spec: `ecb63e4` (19/09,
  "alcance declarável — a Modalidade que atravessa Perfis, e a Etapa que não vale para todos") e
  `cecba68` (20/09, reescrita "o catálogo de Modalidades do Edital — a lei declarada uma vez").
  Base: `b97cc0d` (merge da auditoria de convergência). Sem plan, sem tasks, sem PR (busca `gh pr
  list --search 039`: nenhum).
- Problema original: 1ª redação — (US1) "família de concorrência" sobre as Modalidades dos Perfis,
  para o documento valer para a família; (US2) Etapa com alcance por Perfil. 2ª redação — a
  Modalidade declarada **uma vez no Edital** com seu fundamento; o Perfil "adere e reparte"
  (FR-568…FR-580, SC-201…SC-205, UX-067/068); absorvia a `D-G5` (acrescentar Modalidade por
  Retificação) e recusava a "grafia dupla da ampla concorrência" (FR-572/D-004). A Etapa com alcance
  **saiu** "por medição", registrada como "a candidata seguinte".
- Recomendação original: a própria spec se colocou como **terceiro** investimento ("Nota de
  sequenciamento": 1º fechar a 038/N-03, 2º derivar o campo declarado derivado, 3º esta).
- Rastro posterior: 040 (21/09) e 041 registram a 039 "ainda não mesclada" e reservam a faixa acima
  dela (`specs/040-…/spec.md:26-31`, `specs/041-…/spec.md:371-373`); estudo 21/09 §13/E2 deixa em
  aberto "quais destes podem migrar" e registra que "na amostra, nenhum Perfil diverge dos irmãos";
  **decisão de 25/09** (`doc/decisao-recorte-documental.md`, "O que já está fixado"): *"A Modalidade
  continua sendo do Perfil. Mover a propriedade dela para o Edital está fora de questão."*; D5: "a
  primeira spec faz **só** o recorte transversal"; 043 §2 ("Não é mover conteúdo para o nível do
  Edital … a Constituição fixa que *Cotas DEVEM ser definidas por Perfil*; esta feature não a
  tensiona"); 044 §3 ("Não move a Modalidade para o Edital").
- Por que não entrou: **não há registro explícito de abandono** — nem commit, nem doc, nem memória
  (`grep` por "039"/"catálogo de Modalidades" em `doc/`, `specs/` e no diretório de memória não acha
  decisão). O que existe é **supersessão implícita**: (i) a própria spec pedia para vir depois de
  duas outras frentes; (ii) o usuário priorizou 040–042 (21/09) e depois o estudo de esforço, 043 e
  044; (iii) a decisão de 25/09 escolheu a opção **A** (código com coerência de denominação) contra
  a **B** (categoria no Edital) e declarou fora de questão mover a Modalidade — que é o núcleo da
  2ª redação da 039.
- Specs relacionadas: 040, 041, 043, 044; D-G5 (18/09).
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/models/perfis.py:110-119` (Modalidade no Perfil);
  `interface/retificacao.py:1054` (`SECOES_QUE_ACRESCENTAM` sem Modalidade);
  `interface/templates/interface/retificar.html:159` ("Modalidades de Concorrência ainda não são
  definidas por aqui").
- Estado atual: **CONTRADITO POR DECISÃO POSTERIOR** — `doc/decisao-recorte-documental.md` (25/09,
  aceita pelo usuário) + 043 §2 + 044 §3.
- Ainda faz sentido?: o catálogo, não (decidido). Duas peças dela continuam órfãs e **não dependem**
  do catálogo: (1) a **D-G5** — acrescentar Modalidade a Perfil de Edital publicado cabe como
  `ADD /profiles/id=…/competitionModalities/-` com a Modalidade continuando no Perfil; a 039 a
  tinha absorvido, e com a 039 fora ela volta a não ter spec (é item de outro lote — ver
  convergência 20/09 §17); (2) o **alcance da Etapa** (AX-4), que a 039 registrou como "candidata
  seguinte" e ninguém retomou.
- Lacuna residual: D-G5 sem spec; alcance da Etapa sem dono; branch com faixa FR-568…580 reservada e
  nunca definida (inofensivo: a 040 já pulou a faixa).
- Grupo do resíduo: **B** (as duas peças órfãs)
- Impacto atual: nenhum no produto; risco de governança — a branch parece trabalho em curso e não é.
- Próxima ação sugerida: o usuário registrar que a 039 está encerrada (ou apagar a branch local) e
  dizer onde ficam D-G5 e o alcance da Etapa.
- Relações: AX-7, AX-14, AX-4, D-G5, "três nomes para duas coisas" (FR-572 da 039).
- Confiança: alta quanto ao conteúdo; média quanto ao motivo (inferido — sem registro explícito).

### 044 — Recorte transversal do documento exigido: spec na main, implementação só na branch
- Origem: `specs/044-recorte-transversal-documental/` (spec/plan/tasks mesclados em `bb774d9`, 25/09).
  **Correção de premissa recebida durante a auditoria:** a implementação existe em
  `origin/claude/044-recorte-transversal-documental` — `bccfda0`, `fe9780b`, `6e2aa5a`, `85ebd61`,
  `4ae22d1`, `dffb9db`, `46ac737`, `56649d4` (último commit de trabalho 25/09 23:28; merge de
  `origin/main` em `683dc58`, 23:29) —, **fora da main**. `gh pr list --head
  claude/044-recorte-transversal-documental` mostra o **PR #173 aberto** ("feat(044): … —
  implementação", criado 26/09 03:21 UTC, base `main`), com o check `compose` verde e o `test`
  **pendente** no momento da consulta. `git diff --stat main...origin/claude/044-…`: 57 arquivos,
  +3399/−188. Na **main de hoje** nada disso existe (`grep` por `modalityCode`/`lista_exigida` no
  backend: zero; `inscricoes/migrations` termina em `0004`).
- Problema original / recomendação: cumprir D1–D5 da decisão de 25/09 — recorte por **código** da
  Modalidade em todos os Perfis (FR-700…FR-705), IMPEDE de coerência de denominação por código
  (FR-706/707), proibido para a ampla declarada (FR-704), agrupamento por código no PDF (FR-712), e
  **lista exigida gravada no envio** lida pela Mesa, consulta e portal (FR-714…FR-720).
- Implementação encontrada (na branch, lida com `git show`/`git diff`, sem checkout):
  - modelo: `editais/migrations/0022_documento_modalidade_codigo.py` — coluna
    `DocumentoExigido.modalidade_codigo` e `ck_documento_recorte_exclusivo` (código exclusivo com
    Perfil/Modalidade exata);
  - aplicabilidade única: `editais/domain/documentos.py:206-290` (`recorte_de`, `aplicabilidade`,
    `aplicaveis`, `_se_aplica`) e recusas de gravação `:69-151`;
  - publicação: `editais/domain/validation.py:2234-2275` (`_recorte_por_codigo`: conflito de recorte,
    código inexistente, código da ampla declarada — FR-704/FR-724) e `:2278-2321`
    (`_denominacoes_do_codigo`, `modality_code_name_divergent`: **só a denominação**, "percentual e
    fundamento são da cota, e a cota é por Perfil"); a mensagem da #161 ganha a saída "use a
    modalidade … em todos os Perfis" (`:2324-2360`);
  - PDF: `publicacoes/infrastructure/pdf.py` — `_titulo_do_grupo` ganha o grupo por código, "agora
    verdadeiro, porque o portal aplica pelo mesmo critério";
  - tela: `interface/templates/interface/_documento.html` — seletor com `optgroup` "Em todos os
    Perfis" × "Modalidade de um Perfil"; Retificação: `("documentRequirements","modalityCode")`
    retificável (`editais/domain/mutabilidade.py:499` na branch);
  - lista gravada: `inscricoes/migrations/0005_item_da_lista_exigida.py`,
    `inscricoes/application/lista_exigida.py`, leitura pela Mesa (`avaliacoes/application/mesa.py`),
    consulta e portal; tabela append-only nova (`seguranca/papeis.py`).
  - testes novos: `tests/unit/inscricoes/test_aplicabilidade.py`,
    `tests/unit/editais/test_validacao_inscricao.py`, `tests/integration/inscricoes/test_recorte_transversal.py`,
    `test_lista_exigida*.py`, `tests/integration/publicacoes/test_retificar_recorte_transversal.py`,
    `tests/unit/publicacoes/test_pdf_documentos_exigidos.py`, entre outros. O commit `56649d4` diz
    "7747 passando, 11 pulados contra PostgreSQL" — **medição local do autor, não reproduzida aqui**.
- O que fecharia, por achado (quando entrar na main):
  - **AX-14** — a parte de custo (5 → 5n, chaves inventadas); a de integridade já fechou na main por
    `01d9163`. E o IMPEDE de coerência por código cobre o furo do rótulo ("PcD" × "Pessoa com
    Deficiência") **para quem usa o recorte transversal**.
  - **AX-10** — o "obrigatório de modalidade publicado como facultativo" (4 dos 9 do 140/2025, pela
    conta da própria 044 §1); **não** fecha condição sobre a pessoa nem submodalidade.
  - **AX-7** — só a face documental (5 → 5); a Modalidade e a regra continuam 4n **por decisão**. E
    introduz o **primeiro confronto entre Perfis** do sistema (denominação por código, FR-706) —
    pequeno passo na direção da E-4. **Não** confronta percentual/fundamento (FR-707, por decisão).
  - **AX-17** — torna verdadeiro o cabeçalho sem Perfil no grupo por código. A ajuda da etapa
    ("ou só para uma modalidade", `compor_inscricao.html:46`) **não foi alterada na branch**, mas
    passa a descrever uma opção que existe.
  - **"Três nomes para duas coisas"** — só o flanco documental (FR-704 recusa o recorte transversal
    na ampla declarada); o sorteio continua como está.
  - **Não fecha**: AX-15 (submodalidade — excluída em §3), AX-1/AX-11 (fora), condição sobre o
    candidato (D2).
- Estado atual: **IMPLEMENTADO, MAS NÃO VALIDADO** — **fora da main** (branch + PR #173 aberto, CI
  `test` pendente). Na main de hoje a lacuna que a 044 fecha continua aberta.
- Ainda faz sentido?: sim; é a frente decidida pelo usuário para esta família de achados.
- Lacuna residual: na main, toda a 044; na branch, validação independente (CI verde e conferência pela
  tela do 140/2025 com os sete documentos).
- Grupo do resíduo: **B**
- Próxima ação sugerida: validar (CI do #173 e percurso pela tela); merge é do usuário.
- Relações: AX-7, AX-10, AX-14/17, E-4; PR #172 e `doc/achado-filtro-de-concorrencia-sem-perfil.md`
  (a 044 registrou o defeito do seletor como fora de escopo); memória
  `valor-de-fato-corrigir-depois-da-044.md` (a correção do `ValorDeFato` espera esta migration `0005`).
- Confiança: alta quanto ao que está na branch; baixa quanto a funcionar (não executado).

### E-4 (raiz) — Fontes normativas que ninguém confronta: ACH-41, ACH-13, ACH-18, AX-7 e "três nomes para duas coisas"
- Origem: `doc/auditoria-exploratoria-ux-2026-09-16.md` §11 (E-4) e §13.5 (16/09); ampliada pela
  varredura 19/09 ("a classe tem membros": ACH-41, AX-2, AX-8, AX-7) e pela convergência 20/09 §4,
  §5 (cenário C) e §17 ("E-4 em estado puro").
- Problema original: o sistema é rigoroso **dentro** de cada fonte e cego **entre** elas.
- Recomendação original (13.5): "Validação do conteúdo" com verificações cruzadas — janela recursal
  × Evento de recurso; término de inscrições × designação; numeração exibida = a do documento.
- Rastro posterior: reavaliação 18/09 ("🔴 intocados"); convergência 20/09 ("ABERTO"; `N-05`/`N-06`
  como casos novos, do lote da convergência); 25/09 — **primeiro confronto cruzado entregue**
  (`01d9163`, documento × execução) e o segundo implementado **fora da main** (044 FR-706,
  `_denominacoes_do_codigo`, denominação entre Perfis — branch/PR #173, não validado).
- Specs relacionadas: 025, 027, 034, 044.
- Evidência no código atual, por membro:
  - **ACH-41** (janela do marco × Evento de recurso): `editais/domain/validation.py:1497-1533` só
    confere que a janela é computável; o Evento de Cronograma tem `type` em **texto livre**
    (`editais/models/cronograma.py:26`, e o comentário de `:33-37` diz que nada o valida), então não
    há como identificar estruturalmente "o Evento de recurso" para confrontar. **NÃO IMPLEMENTADO**.
  - **ACH-13** (período de inscrições designado na etapa 6, editado no Evento na Retificação): o
    roteamento da pendência leva à etapa certa desde a 009 (`interface/views.py:664-668`), mas a
    mensagem continua dizendo "marcado" (`editais/domain/validation.py:1886-1893`) e a Retificação
    edita o fato no Evento (`interface/retificacao.py:109-111`). Não é confronto entre fontes: é um
    dado com duas superfícies. **NÃO IMPLEMENTADO**, **C**.
  - **ACH-18/ACH-33** (numeração de seção tela × documento): a composição mostra `secao.order` do
    catálogo (`interface/templates/interface/compor_conteudo.html:19`); o PDF renumera sem preâmbulo e
    sem seções vazias (`publicacoes/infrastructure/pdf.py:2095-2130`). O resumo **público** da
    Retificação nomeia a seção pelo título (`publicacoes/domain/alteracoes.py:33`), então o ato
    publicado não herda a divergência. **NÃO IMPLEMENTADO**, **C**.
  - **AX-7 / AX-2 / AX-8**: ver blocos próprios (nenhum confronto novo).
  - **"Três nomes para duas coisas"** (Modalidade AC declarada × linha geral do quadro × recorte nulo
    do sorteio): **parcialmente fechado antes de 20/09** — `generalCompetitionModalityId` liga a AC
    declarada à linha geral (014/027); AVISO quando não declarada (`validation.py:1117-1153`, 027
    FR-325); IMPEDE quando a declarada tem linha (`:1100-1114`); classificação e ocupação usam um
    recorte só, com a declarada como apelido do nulo (`editais/domain/recortes.py:1-80`, 034
    FR-491). **Continua aberto no sorteio**, por decisão ratificada: `sorteios/application/previa.py:43-51`
    ainda lista **todas** as Modalidades como recortes, incluindo a AC declarada (o bloco vazio que a
    convergência viu), e a 034 `FR-491a`/`D-004` (18/09) mandou registrar e **não** corrigir ("é
    desenho, e é spec própria"). A 039 (FR-572) recusaria a grafia dupla; não entrou.
- Estado atual: **PARCIALMENTE RESOLVIDO** (dois confrontos novos em 25/09 — um na main, um só na
  branch da 044 —; os três membros de 16/09 intocados; o sorteio mantido por decisão)
- Ainda faz sentido?: sim, mas **não como "uma validação que ataca a classe"**. Cada confronto exige
  primeiro que as duas fontes sejam identificáveis estruturalmente (ACH-41 não é, porque o tipo do
  Evento é texto livre). O caminho real tem sido caso a caso, e os casos que valem o custo são os que
  mudam direito: ACH-41 (prazo de recurso) e AX-7 (percentual). ACH-13 e ACH-18 são microcópia e
  numeração.
- Lacuna residual: ACH-41 (dois prazos de recurso publicados sem sinal); AX-7 (percentuais
  divergentes entre Perfis); sorteio com recorte da AC declarada.
- Grupo do resíduo: **A** para ACH-41 (dois prazos contraditórios do mesmo direito no mesmo Edital,
  e o candidato que seguir o Cronograma perde o prazo real); **B** para AX-7 e o sorteio; **C** para
  ACH-13 e ACH-18.
- Impacto atual: integridade do que se publica nos membros A/B.
- Próxima ação sugerida: ACH-41 — AVISO quando a janela do marco e algum Evento de Cronograma
  vinculado a recurso divergirem, o que pede antes designar o Evento de recurso (como já se designa
  o de inscrição); sorteio — decidir se a spec própria da `FR-491a` entra.
- Relações: ACH-41/13/18 (lote de 16/09 — aqui só a checagem pontual); N-05/N-06 (lote da
  convergência); `memory/ampla-concorrencia-tem-duas-grafias.md`.
- Confiança: alta para a checagem de código; média para a priorização.

### Achado avulso — A cópia levava, como ampla concorrência, a Modalidade do Edital anterior
- Origem: `doc/achado-ampla-declarada-nao-remapeada.md` (15/09)
- Problema original: `generalCompetitionModalityId` atravessava o reaproveitamento (023) sem troca;
  o guarda de varredura estava cego porque nenhuma fixture declarava o campo.
- Recomendação original: corrigido no ato; registrada como classe aberta a ideia de uma varredura
  que compare os campos do conteúdo publicado com os que a fixture de origem declara ("a fixture é
  parte do guarda").
- Rastro posterior: **a classe se repetiu em 25/09** — `doc/achado-etapa-governada-nao-remapeada.md`
  (`cutRule.governedStage`, corrigido em `643e865`), com a mesma causa (nenhuma fixture declarava
  regra de corte) e a mesma frase: "A classe continua aberta".
- Specs relacionadas: 014, 023, 027, 043 (reusa `remapear`).
- Implementação encontrada: o defeito pontual está corrigido; a varredura de classe não existe.
- Evidência no código atual: `editais/domain/reaproveitamento.py:143-144` (remapeia a ampla) e
  `:173-181` (remapeia `governedStage`); testes em `tests/unit/editais/test_reaproveitamento.py` e
  `tests/integration/editais/test_reaproveitamento.py`.
- Estado atual: **PARCIALMENTE RESOLVIDO** (defeito resolvido; mecanismo de classe não)
- Ainda faz sentido?: sim — foram **dois** casos em dez dias, e a 043 passou a usar o mesmo
  `remapear` dentro do Edital, dobrando a superfície. A varredura "campo do contrato canônico ⇒
  presente na fixture rica de reaproveitamento" é pequena e já tem precedente (o guardião da 026).
- Lacuna residual: próximo campo de referência que nascer depois da 023 atravessa de novo.
- Grupo do resíduo: **B**
- Impacto atual: não publica errado (a validação costuma pegar a referência pendurada), mas gera
  pendência impeditiva que o operador não causou.
- Próxima ação sugerida: criar teste guardião (decisão do usuário, registrado como "registro, não
  prioridade" nos dois achados).
- Relações: memória "replace_draft apaga o que não for reenviado" (família "o que não se lembra de
  carregar some"); 043 FR-639 ("campo acrescentado ao Perfil no futuro e esquecido aqui DEVE reprovar
  a conferência" — a 043 aplicou o guardião à duplicação, não ao reaproveitamento).
- Confiança: alta.

### Achado avulso — Objeto normativo sem forma, sem semântica e sem leitor
- Origem: `doc/achado-objeto-normativo-sem-forma.md` (13/09)
- Problema original: `classificationInformation` e `callInformation` do Perfil são `JSONField`
  livre, entram no snapshot, nenhum canal os exibe e nenhum cálculo os lê; classificados como não
  retificáveis.
- Recomendação original: decidir entre (1) declarar forma e destino, ou (2) deixar de emiti-los.
- Rastro posterior: 023 os exclui da cópia (`CAMPOS_SEM_TELA`); 043 FR-643 também.
- Specs relacionadas: 026, 023, 043.
- Implementação encontrada: nenhuma decisão.
- Evidência no código atual: `editais/models/perfis.py:36-37`;
  `publicacoes/application/publish_edital.py:252` (emitido); `editais/domain/mutabilidade.py:153-156`
  (opacos) e `:247-260` (não retificáveis, com a razão); `editais/domain/reaproveitamento.py:24`;
  leitores fora da autoria: nenhum.
- Estado atual: **NÃO IMPLEMENTADO** (a decisão continua aberta)
- Ainda faz sentido?: pouco. Nenhuma tela os escreve; só a API e o `seed_demo`. O estado é honesto
  e protegido por teste. A opção (2) é a mais barata e limpa, mas mexe na versão canônica.
- Lacuna residual: dois campos publicados sem significado.
- Grupo do resíduo: **C**
- Impacto atual: nenhum para o candidato.
- Próxima ação sugerida: nenhuma, ou decisão do usuário quando houver degrau canônico por outro
  motivo.
- Relações: AX-9 (mesmo padrão, lado oposto); `callRules` opaco (AX-7/AX-15).
- Confiança: alta.

### Achado avulso — Só o método do sorteio nasce pela tela; corte, janela recursal e reversão só pela API
- Origem: `doc/achado-objeto-que-nasce-so-pelo-metodo.md` (14/09)
- Problema original: `PODE_PASSAR_A_EXISTIR` admite que `cutRule`, `appealWindow` e
  `vacancyReversion` nasçam por Retificação, mas a tela só oferece os campos quando o objeto já
  existe.
- Recomendação original: para cada um, oferecer os campos em branco com rótulo do vazio **ou**
  registrar por escrito que nasce só pela API.
- Rastro posterior: nenhum.
- Specs relacionadas: 026 (FR-313), 014, 016.
- Implementação encontrada: nenhuma.
- Evidência no código atual: `editais/domain/mutabilidade.py:515-545` (quatro podem nascer);
  `interface/retificacao.py:851-860` — `CAMPOS_DO_CORTE` e `CAMPOS_DA_JANELA` só "se o objeto
  existe"; `:764` — `CAMPOS_DA_REVERSAO` idem; o método é "sempre" (`:861-868`).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim para a **janela recursal** (Edital publicado sem prazo de recurso declarado
  não tem como ganhá-lo pela tela — é direito com prazo); menos para corte e reversão, que mudam
  resultado e merecem decisão caso a caso.
- Lacuna residual: três objetos com decisão "pode nascer" sem caminho na interface.
- Grupo do resíduo: **B** (janela recursal); **C** (corte, reversão)
- Impacto atual: correção de Edital publicado depende de API para esses três.
- Próxima ação sugerida: decisão do usuário por objeto, como o achado pede.
- Relações: AX-1 (acrescentar critério também só pela API); D-G5 (Modalidade).
- Confiança: alta.

### Achado avulso — A igualdade da soma não lia a ampla declarada
- Origem: `doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md` (12/09)
- Problema original: `_coerencia_do_quadro_de_vagas` não descontava a Modalidade declarada como
  ampla; no formato normal a igualdade da soma nunca rodava (quadro 79 × 80 publicava calado).
- Recomendação original: quatro caminhos, sem escolher (ligar o campo na completude; exigir a
  declaração; completude frouxa; deixar).
- Rastro posterior: **027** tomou o caminho 1 (FR-317, T-002) e acrescentou o aviso de ampla não
  declarada (FR-325).
- Specs relacionadas: 025 (FR-161, FR-176, R-006), 014 (FR-231), 027.
- Implementação encontrada: sim.
- Evidência no código atual: `editais/domain/validation.py:2401-2418` — "A completude desconta a
  Modalidade declarada como ampla (027, FR-317, T-002)", `reservadas = set(modalidades) -
  ({str(ampla)} …)`; `:1117-1153` (AVISO quando não declarada). Testes:
  `tests/interface/test_compor_quadro.py::test_a_igualdade_roda_no_edital_com_ampla_declarada`
  (`:755`) e o registro antigo `::test_a_igualdade_nao_roda_onde_uma_modalidade_fica_sem_linha`
  (`:231`, que agora descreve o caso sem declaração).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma (quem não declara a ampla recebe aviso).
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma.
- Relações: "três nomes para duas coisas" (E-4).
- Confiança: alta.

### Achado avulso — O Anexo publicado não diz a quem serve
- Origem: `doc/achado-anexo-sem-destinatario.md` (08/09)
- Problema original: a página pública lista anexos sem dizer se são modelo de documento exigido, à
  disposição, ou esquecidos; a elaboração já distingue ("modelo de …"). Declarado "não é defeito".
- Recomendação original: três decisões para uma spec (dizer o que o anexo-modelo é; o que dizer do
  que não é modelo; aviso na Revisão).
- Rastro posterior: 024 unificou a lista de documentos da seleção.
- Specs relacionadas: 020 (FR-039), 024 (FR-129…FR-132).
- Implementação encontrada: parcial e anterior — no fluxo da inscrição o anexo aparece junto do
  documento de que é modelo; a lista pública continua só com rótulos.
- Evidência no código atual: `portal/templates/portal/_documentos_do_edital.html:50-60` (lista de
  rótulos); `portal/templates/portal/_documentos.html:43` ("Baixar o modelo: …" no documento);
  `interface/revisao.py:237-247` (Revisão: "modelo de: …" / "não é modelo de nenhum requisito",
  informativo, não aviso).
- Estado atual: **NÃO IMPLEMENTADO** (e nunca foi pedido como defeito)
- Ainda faz sentido?: pouco. A inscrição, onde a pergunta importa, já liga o modelo ao documento.
- Lacuna residual: a lista pública não diz a finalidade.
- Grupo do resíduo: **C**
- Impacto atual: leitura.
- Próxima ação sugerida: nenhuma.
- Relações: AX-12 (face oposta — remissão sem anexo).
- Confiança: alta.

### Decisão — Contrato de mutabilidade normativa
- Origem: `doc/decisao-mutabilidade-normativa.md` (13/09, executada pela 026 em 13–14/09)
- Problema original: campos normativos publicados sem decisão de retificabilidade.
- Recomendação original: invariante "nenhum campo entra sem natureza declarada" + guardião.
- Rastro posterior: a 043 e a 044 citam o contrato como condição de desenho (044 FR-721).
- Implementação encontrada: sim.
- Evidência no código atual: `editais/domain/mutabilidade.py` — hoje 84 `retificavel()`, 25
  `nao_retificavel(`, 25 `estrutural()`, 5 `derivado(` (eram 72/23/24/4 em 14/09: o contrato cresceu
  com os campos novos, como deveria); guardião `tests/contract/test_mutabilidade.py:303`
  (`test_todo_campo_publicado_tem_natureza_declarada`) e `:339`
  (`test_campo_novo_sem_decisao_derruba_a_suite_nomeando_o_campo`).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não como pendência. Dois resíduos pertencem a outros blocos: a natureza
  "retificável" não garante canal de exibição (AX-9, família (b)), nem caminho de **acréscimo** na
  tela (AX-1 e o achado do "objeto que nasce só pelo método").
- Lacuna residual: nenhuma própria.
- Grupo do resíduo: —
- Próxima ação sugerida: nenhuma.
- Relações: AX-1, AX-9, objeto que nasce só pelo método.
- Confiança: alta.

### PR #172 (aberto) — O filtro de concorrência diz de qual Perfil é cada Modalidade
- Origem: `gh pr view 172` (26/09, `claude/filtro-de-concorrencia-com-perfil`); registra
  `doc/achado-filtro-de-concorrencia-sem-perfil.md` (novo no PR).
- O que fecha: defeito de rótulo na consulta "Inscrições recebidas" do Gestor — com dois Perfis,
  "Ampla concorrência" aparecia duas vezes com o mesmo texto; o PR prefixa o nome do Perfil
  (`interface/templates/interface/inscricoes.html`, só template) com dois testes em
  `tests/integration/interface/test_inscricoes_em_escala.py`. Origem declarada: conferência do envio
  §3 e a 044 (*Riscos e lacunas*).
- Relação com este lote: **não fecha AX nenhum**. É sintoma, na gestão, de AX-7 (a Modalidade é do
  Perfil e se repete por nome) — a mesma ambiguidade que AX-17 viu no PDF e que o seletor da
  composição já resolve com "LP01 — … · PcD". Deixa registrado, fora do escopo, que o seletor não
  se restringe ao Perfil escolhido.
- Estado atual: **IMPLEMENTADO, MAS NÃO VALIDADO** (PR aberto; o próprio corpo diz que a combinação
  com a #168 "só o CI viu")
- Grupo do resíduo: **C** (o que sobra — seletor que ignora o Perfil ativo)
- Próxima ação sugerida: merge é do usuário; nada deste lote o bloqueia.
- Confiança: alta.

### H-1, H-2, H-3 — Hipóteses não confirmadas de 15/09
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §Hipóteses (15/09)
- Problema original: H-1 "Tutor Presencial / Supervisor de Estágio" pode ser duas funções num
  código; H-2 mobilidade entre perfis precisaria de adjacência entre polos; H-3 heteroidentificação
  "até 3 por código" é regra do certame executada por código.
- Rastro posterior: o estudo de 21/09 cadastrou os 16 Perfis do 140/2025 e tratou a função composta
  como nome ("Classificação final — Tutor Presencial / Supervisor de Estágio — Letras",
  `doc/diario-estudo-esforco-2026-09-21.md:534`), sem medir duas atribuições; "Mobilidade entre
  Perfis" aparece entre as oito seções sem lugar (estudo §9-bis) — só como prosa; nada executa
  heteroidentificação.
- Implementação encontrada: nenhuma, e nenhuma foi pedida.
- Estado atual: **DUPLICADO / ABSORVIDO** — H-1 e H-2 em AX-5/AX-6 (dimensões da matriz) e AX-3
  (seção de mobilidade); H-3 em AX-15 (heteroidentificação por submodalidade).
- Ainda faz sentido?: não como itens próprios.
- Grupo do resíduo: —
- Confiança: média — continuam hipóteses; só o autor do 140/2025 responde H-1.

### Divergências de conteúdo que NÃO demonstram problema de arquitetura (sete itens de 15/09)
- Origem: `doc/auditoria-granularidade-normativa-2026-09-15.md` §"Divergências de conteúdo…"
- Estado: continuam não sendo achados, com uma exceção de reclassificação: o item 7 ("Realização:
  19/11/2026, às 00h") foi reclassificado pelo estudo de 21/09 §9-bis como defeito do gerador ("Hora
  inventada impressa como norma", 11 de 13 eventos no 140/2025) — **do lote do estudo**, não
  reverificado aqui. O item 2 (texto do TADS embaralhado) está absorvido em AX-2.
- Estado atual: **SUPERADO / OBSOLETO** (como lista; o item 7 é **DUPLICADO / ABSORVIDO** pelo
  estudo §9-bis)
- Grupo do resíduo: —
- Confiança: alta.

---

## 1. Tabela-resumo

| ID | Título | Estado | Grupo | Próxima ação |
|---|---|---|---|---|
| AX-1 | Sentido do desempate divergente; `type` irretificável; acréscimo de critério só pela API | PARCIALMENTE RESOLVIDO (043 duplica) | B | spec curta: aviso de divergência entre Perfis + acrescentar critério na Retificação (ou registrar "só API") |
| AX-2 | Requisito × documento comprobatório: duas prosas sem vínculo | NÃO IMPLEMENTADO | C | nenhuma (orientação de redação) |
| AX-3 | Catálogo de Seções fechado (8 seções viram parágrafo) | NÃO IMPLEMENTADO | B | decisão do usuário (estudo §15, decisão 3) |
| AX-4 | Barema inexistente; Etapa sem alcance por Perfil/curso | NÃO IMPLEMENTADO | B | spec quando priorizado (039 a registrou como "candidata seguinte") |
| AX-5 | Curso/Área/Campus inexistentes | NÃO IMPLEMENTADO | C | nenhuma isolada (junto com AX-4) |
| AX-6 | Código é o par perfil × polo | NÃO IMPLEMENTADO | C | nenhuma (premissa para AX-5) |
| AX-7 (+E-1) | Modalidade/regra 4n; 3% × 30% sem conferência | CONTRADITO POR DECISÃO POSTERIOR (`decisao-recorte-documental.md`, 043 §2, 044 §3) | B | corrigir: AVISO de percentual/fundamento divergente por código |
| AX-8 | Número do Edital com duas fontes na capa | NÃO IMPLEMENTADO | B | corrigir: conferência título × número/ano |
| AX-9 | Teto de inscrições executado e não publicado (nem declarável na composição) | NÃO IMPLEMENTADO | B | corrigir: renderizar; decidir campo na etapa Inscrição |
| AX-10 | "Documentos exigidos" funde naturezas | PARCIALMENTE RESOLVIDO (`a2b1e1f`; 044 fora da main) | B | validar/mesclar 044 |
| AX-11 | Fatos declarados por Perfil | PARCIALMENTE RESOLVIDO (043) | C | nenhuma (entrar no aviso do AX-1) |
| AX-12 | Remissão a anexo sem conferência (materializada no estudo) | NÃO IMPLEMENTADO | B | corrigir: AVISO de remissão `ANEXO X` sem rótulo |
| AX-13 | Cabeçalho de alcance só com nome | RESOLVIDO (`c0403a9`) | — | nenhuma |
| AX-14 / AX-17 (+E-2) | Documento publicado "toda a modalidade" × execução por Perfil | RESOLVIDO (`01d9163`, IMPEDE); custo 5n absorvido pela 044 | B | validar/mesclar 044; checar acervo pré-25/09 |
| AX-15 | Submodalidades de PPIQ | NÃO IMPLEMENTADO (fora da 044 por decisão) | B | nenhuma agora |
| AX-16 | Restaurar rascunho local perde coleções aninhadas | NÃO IMPLEMENTADO | **A** | validar pela tela e corrigir (ou restringir a salvaguarda) |
| E-3 | Custo de autoria sem duplicar | PARCIALMENTE RESOLVIDO (043) | B | nenhuma além da 044 |
| 039 | Catálogo de Modalidades / alcance declarável (branch local) | CONTRADITO POR DECISÃO POSTERIOR | B (peças órfãs: D-G5, alcance da Etapa) | usuário registrar encerramento e destino das peças |
| 044 | Recorte transversal + lista gravada | IMPLEMENTADO, MAS NÃO VALIDADO (**fora da main**, PR #173) | B | validar (CI + tela); merge do usuário |
| ACH-41 (E-4) | Janela recursal do marco × Evento de recurso | NÃO IMPLEMENTADO | **A** | criar spec: designar Evento de recurso + AVISO |
| ACH-13 (E-4) | Período de inscrições: "marcado" × designado na etapa 6 | NÃO IMPLEMENTADO | C | microcópia |
| ACH-18/33 (E-4) | Numeração de seção tela × PDF | NÃO IMPLEMENTADO | C | nenhuma urgente (ato público usa título) |
| "Três nomes para duas coisas" (E-4) | AC declarada × linha geral × recorte nulo | PARCIALMENTE RESOLVIDO (014/027/034; sorteio mantido por `FR-491a`/D-004) | B | decidir a spec própria do sorteio |
| E-4 (raiz, agregado) | Fontes sem confronto | PARCIALMENTE RESOLVIDO | A/B/C por membro | caso a caso (ver membros) |
| Avulso — ampla não remapeada | Referência que atravessa o reuso | PARCIALMENTE RESOLVIDO (repetiu-se em 25/09: `governedStage`) | B | teste guardião "campo do contrato ⇒ fixture rica" |
| Avulso — objeto sem forma | `classificationInformation`/`callInformation` | NÃO IMPLEMENTADO (decisão aberta) | C | nenhuma |
| Avulso — objeto que nasce só pelo método | corte, janela, reversão sem caminho na tela | NÃO IMPLEMENTADO | B (janela) / C | decisão do usuário por objeto |
| Avulso — igualdade da soma | desconto da ampla declarada | RESOLVIDO (027 FR-317) | — | nenhuma |
| Avulso — anexo sem destinatário | lista pública sem finalidade | NÃO IMPLEMENTADO | C | nenhuma |
| Decisão — mutabilidade | contrato + guardião | RESOLVIDO (026) | — | nenhuma |
| PR #172 | Filtro de concorrência com Perfil | IMPLEMENTADO, MAS NÃO VALIDADO (PR aberto) | C | merge do usuário |
| H-1…H-3 | Hipóteses de 15/09 | DUPLICADO / ABSORVIDO (AX-3, AX-5/6, AX-15) | — | nenhuma |
| Divergências sem achado | 7 itens de 15/09 | SUPERADO / OBSOLETO (item 7 absorvido pelo estudo §9-bis) | — | nenhuma |

## 2. Contagens por estado

Contadas as 32 linhas da tabela **sem** a linha agregada da raiz E-4 (que é PARCIALMENTE RESOLVIDO e
se decompõe nos quatro membros).

| Estado | Nº | Quais |
|---|---:|---|
| RESOLVIDO | 4 | AX-13, AX-14/17, igualdade da soma, decisão de mutabilidade |
| RESOLVIDO POR OUTRO CAMINHO | 0 | — (o AX-14/17 fechou pela família (d) que ele próprio listava) |
| PARCIALMENTE RESOLVIDO | 6 | AX-1, AX-10, AX-11, E-3, "três nomes", ampla não remapeada |
| NÃO IMPLEMENTADO | 16 | AX-2, AX-3, AX-4, AX-5, AX-6, AX-8, AX-9, AX-12, AX-15, AX-16, ACH-41, ACH-13, ACH-18, objeto sem forma, objeto que nasce só pelo método, anexo sem destinatário |
| IMPLEMENTADO, MAS NÃO VALIDADO | 2 | 044 (fora da main, PR #173), PR #172 |
| SUPERADO / OBSOLETO | 1 | divergências sem achado |
| DUPLICADO / ABSORVIDO | 1 | H-1…H-3 |
| CONTRADITO POR DECISÃO POSTERIOR | 2 | AX-7 (estrutural), 039 |

Resíduos por grupo: **A** = 2 (AX-16, ACH-41) · **B** = 16 · **C** = 9 · sem resíduo = 5.

Leitura dos 17 AX de 15/09 contra a varredura de 19/09 ("0 fechados"): hoje **3 fechados**
(AX-13, AX-14, AX-17), **3 parciais** (AX-1, AX-10, AX-11), **1 contradito por decisão** (AX-7) e
**10 abertos** (AX-2, 3, 4, 5, 6, 8, 9, 12, 15, 16) — o único que fazia ato publicado e execução
divergirem (AX-14) fechou em 25/09, na main.

## 3. Achados NOVOS encontrados de passagem

1. **O teto de inscrições por candidato não é declarável na composição.** FR-063 da 015 diz "o
   Edital MUST poder publicar um teto"; fora de testes, o campo só é escrito por
   `interface/retificacao.py:119` (Retificação, depois de publicado) e por `seed_demo.py:875`. Nenhuma
   ocorrência em `interface/forms.py` nem nas etapas do assistente. A 023 já sabia ("nenhuma etapa do
   assistente oferece"), mas nada o registra como lacuna. Combinado com AX-9: o único caminho da tela
   é justamente o que produz execução sem norma publicada.
2. **A 043 ampliou a superfície do AX-16.** O Perfil duplicado e não gravado leva os marcos num oculto
   `perfil-N-marcosEmTransito` (`interface/templates/interface/_perfil.html:4`) que o fragmento vazio
   não tem; restaurar o rascunho local deve perdê-los em silêncio. A FR-650 da 043 garante a
   sobrevivência só à recusa **do servidor**. Por leitura, não reproduzido.
3. **A Retificação remove critério de desempate mas não acrescenta.** O grupo do critério é removível
   por padrão (`interface/retificacao.py:586`, `:925-936`); os `ADD` são só Perfil, linha do quadro,
   Anexo e Evento. A razão normativa de `("tiebreakers","type")` ("remove-se e acrescenta-se") tem
   metade do caminho na tela — removendo sem acrescentar, a tela permite **reduzir** a regra de
   desempate de um Perfil, e não corrigi-la.
4. **A 039 deixou duas peças sem dono.** Com o catálogo superado, a D-G5 (acrescentar Modalidade por
   Retificação), que ela absorvia, e o alcance da Etapa, que ela adiou para a "candidata seguinte",
   não têm spec nem registro de destino. A branch local continua parecendo trabalho em curso.
5. **Existe PR para a 044.** `gh` mostra o **#173** aberto (26/09 03:21 UTC) sobre
   `claude/044-recorte-transversal-documental`, com `test` pendente — a premissa "sem PR aberto"
   recebida durante a auditoria já não vale.

## 4. Incertezas que exigem validação humana

1. **Alcance da decisão de 25/09 sobre a Modalidade.** `doc/decisao-recorte-documental.md` diz que a
   Constituição ("Cotas DEVEM ser definidas por Perfil", `constitution.md:197`) põe "fora de questão"
   mover a Modalidade para o Edital. A 039 lia o mesmo princípio de outro modo (o Perfil continua
   definindo a cota ao "aderir e repartir"). Já houve correção do usuário a uma leitura parecida
   (memória `constituicao-preserva-valor-nao-campo.md`). Confirmar que o encerramento da 039 é
   decisão de produto, e não só inferência do texto constitucional — é isso que faz AX-7 e 039 caírem
   em "contradito por decisão".
2. **AX-4 pode ser A.** A Constituição (`constitution.md:203-205`) diz que "Perfis PODEM possuir
   Etapas distintas" e que critérios, pontuação e acumulação "DEVEM existir no domínio/backend". Lido
   como obrigação, a ausência de barema e de alcance da Etapa contradiz requisito escrito.
3. **Acervo com o recorte contraditório.** Editais publicados **antes** de `01d9163` (25/09) com
   "Todos os Perfis" + Modalidade de um só continuam afirmando no ato o que a execução não faz. Não
   há como saber pelo código se existe algum fora do ambiente de estudo.
4. **AX-16 não foi reproduzido hoje.** O código é o mesmo de 15/09, mas o estudo de 21/09 elogia a
   salvaguarda sem registrar ter restaurado Perfil com Modalidades. Um percurso de cinco minutos
   decide.
5. **Divergência de percentual entre Perfis é legítima na prática?** A decisão de 25/09 diz que pode
   ser; a amostra (estudo §13/E2) não mostrou nenhum caso. Define se o AVISO do AX-7 vale o custo.
6. **044 / PR #173 não foi executada aqui.** Leitura de diff apenas; a suíte "7747 passando" é a
   medição do autor (`56649d4`), e o CI `test` estava pendente.
7. **ACH-41 como A** assume que o candidato lê as duas datas na mesma tela (medido pela interface em
   16/09, não reverificado). O item é primariamente do lote de 16/09; aqui só a checagem de código.
