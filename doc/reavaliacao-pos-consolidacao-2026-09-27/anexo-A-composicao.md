# Reavaliação A — esforço humano de composição e publicação de Edital

**Data:** 2026-09-26 · **Código lido:** `origin/main` `79aeb847` (worktree `auditoria-consolidacao-seletivo-8dba99`, HEAD `f77e8aa9` = main + doc)
**048 lida por diff:** #197 (`origin/claude/retificacao-cobertura-auditoria-b7eabb`, ponta `f96ec280`).
**Atenção — a `main` avançou durante a sessão:** o #197 foi mesclado em `0113b782` (26/09, 23:44). A
árvore mesclada é **idêntica** à ponta lida (`git diff f96ec280 0113b782` vazio), então tudo o que se
diz da `048` vale para a `main` atual. Linhas citadas: as de composição (`views.py` até a 2607, `forms.py`,
`validation.py`, templates `compor_*`/`_perfil`/`_marco`/…) são iguais nas duas; em
`interface/retificacao.py` e em `views.py` depois da 2607, o número entre colchetes é o da `0113b782`.
**Método:** somente leitura — código, templates, specs, `git show/diff`, `pdftotext` nos três PDFs.
Nenhum servidor, nenhuma suíte, nenhuma edição no repositório. **Nada aqui foi cronometrado nem clicado**:
as contagens são de controles no template e de operações que o código oferece, e as estimativas dos
cenários são por custo unitário, com a conta à vista.

Caminhos abreviados: `views` = `backend/processo_seletivo/interface/views.py`; `forms` =
`backend/processo_seletivo/interface/forms.py`; `tpl/` = `backend/processo_seletivo/interface/templates/interface/`.

---

## 0. Linha de base (21/09) — o que se compara

Do `doc/estudo-esforco-de-cadastro-2026-09-21.md` §4, §6.2, §8:

- 78/2026 (medido): ~116 campos, 23 "Acrescentar", 25 objetos, Revisão 3 IMPEDE / 11 AVISO.
- 140/2025 (medido): ~730 campos, ~95 "Acrescentar", 118 objetos, ~430 campos redigitados; **etapa Perfis ~530 interações**; Revisão 1 IMPEDE / 54 AVISO.
- 28/2026 (estimado): ~320 campos, ~75 "Acrescentar", ~120 redigitados.
- Custos unitários: Perfil sem Modalidade = 1 clique + 9 campos; Perfil com 4 Modalidades = 6 cliques + ~30 campos (≈ 33–34 interações); Evento = 1 + 3–5; Documento = 1 + 2–3; marco = 1 + 8 a 12.
- §8: "a curva é **estritamente linear** — não há mecanismo algum que a dobre".

**O que entrou depois da linha de base e mexe na composição** (conferido no código, não na spec):

| Entrega | O que muda no esforço | Onde |
|---|---|---|
| `043` duplicar Perfil | cópia com Modalidades, quadro, fatos e **marcos** (se a origem já os tiver), pedindo Código e Localidade | `views:2015-2144`; `editais/domain/duplicacao.py:30-80`; `tpl/_duplicar_perfil.html:15-35` |
| `044` recorte transversal | um documento por **código** de Modalidade vale para todos os Perfis que o têm | `forms:1495-1530`; `tpl/_documento.html:61-80` |
| `030` método comum do sorteio | 9 campos declarados uma vez no Edital, herdados pelos marcos | `tpl/compor_classificacao.html:59-155`; `views:1370-1384` |
| `030` marco novo pré-preenchido | código, denominação e arredondamento derivados | `views:2300-2323` |
| `046` executabilidade | **novos IMPEDE por Perfil**: sem marco, e sem regra de corte em nenhum marco | `editais/domain/validation.py:1741-1785`, `1954-1988` |
| #163 (25/09, grupo B) | dobra de avisos repetidos — **só** das famílias por Evento/Etapa | `interface/templatetags/interface_extras.py:335-376` |
| `045`, `047` | nada na composição (condução e página pública) | — |
| `048` (#197, mesclada em `0113b782` durante esta sessão) | a Retificação passa a **acrescentar** Modalidade, critério, janela, corte e reversão — um a um | §4 abaixo |

---

## 1. O assistente, etapa a etapa — o que se preenche e o que multiplica

Unidade: **interação** = clique em botão, campo preenchido, escolha de rádio/`select` — a mesma do
estudo de 21/09 e da rastreabilidade da `043`. Contagem feita sobre os controles do template; "típico"
é o que um Edital da amostra de fato preenche, e não o total de controles.

As nove etapas e a ordem: `views:898-921` (`identificacao`, `perfis`, `cronograma`, `etapas`,
`classificacao`, `inscricao`, `anexos`, `conteudo`, `revisao`). A ordem é **deliberada** e explicada no
comentário (a Classificação vem depois das Etapas porque o marco as enumera — `views:907-911`).

### 1.0 Criação do Processo e do Edital — O(1)

`tpl/processo_criar.html:35-85`: 5 obrigatórios (Identificação institucional, Título do Processo,
Número, Ano, Título do Edital) + Descrição opcional. Edital extra no mesmo Processo:
`tpl/edital_criar.html:30-56`, 3 + 1. Etapa Identificação: título (pré-preenchido) + descrição,
`tpl/compor_identificacao.html:50,64`. **Não depende do tamanho do Edital.** O atrito é conceitual (duas
strings do Processo que o Edital não nomeia, estudo §7.1), não de escala.

### 1.1 Perfis de Vaga — O(P) com inclinação baixa, **se** duplicado

Cartão do Perfil (`tpl/_perfil.html`):

| Bloco | Controles | Linhas |
|---|---|---|
| Identidade | Código\*, Denominação\*, Localidade | `_perfil.html:21-36` |
| Vaga | Descrição, Carga horária, Remuneração | `:43-60` |
| Textos longos | Atribuições (textarea), Requisitos (textarea, um por linha) | `:65-81` |
| Quantidade | Vagas imediatas; Cadastro Reserva (rádio de 3) + Limite condicional | `:90-127` |
| Modalidades | por Modalidade: Código\*, Denominação\*, Percentual, Fundamento, Versão — **5 campos + 1 clique** | `tpl/_modalidade.html:11-50`; botão `_perfil.html:141-144` |
| Declarações da Modalidade | "Qual delas é a ampla" (`select`), Reversão (`select`) — só existem com ≥1 Modalidade | `_perfil.html:173-229` |
| Convocação | Forma de comunicar (`select`) | `:241-252` |
| Quadro de vagas | linha geral + **uma linha por lista reservada**, só a quantidade | `tpl/_secao_do_quadro.html:27-29`; `tpl/_linha_do_quadro.html:35-58` |
| Fatos | por fato: Código\*, Rótulo\*, Tipo\* + 1 clique | `tpl/_fato.html:12-25`; botão `_perfil.html:294-296` |
| Duplicar | Código do novo\*, Localidade do novo, "Criar a cópia" (+ abrir o `details`) = **4** | `tpl/_duplicar_perfil.html:15-35`; incluído em `_perfil.html:298` |

Custo unitário: **Perfil sem Modalidade ≈ 10–12** interações; **com M Modalidades ≈ 12 + 6M + M
(quadro) + 2**; o 140/2025 (M = 4, AC só com código e nome) mediu **34** (`specs/043-duplicar-perfil/rastreabilidade.md:111-117`).
**Cópia: 4** + ajustes onde o Perfil diverge; média medida **4,4** por cópia no 140/2025 (mesmo arquivo,
`:120`). A cópia entra **logo abaixo** da origem (`hx-swap="afterend"`, `_duplicar_perfil.html:35`),
e não no fim da lista — o B10 do estudo deixou de valer para a cópia, e continua valendo para
"Acrescentar Perfil" (`tpl/compor_perfis.html:96-98`, `beforeend`).

**O que multiplica:** P (Perfis) — sempre, pelo Código e Localidade; M (Modalidades por Perfil) e F
(fatos por Perfil) — só quando o Perfil é composto do zero em vez de duplicado. A cópia **não guarda
vínculo** com a origem (`specs/043-duplicar-perfil/spec.md` D-005) e é independente a partir daí.

**O que a cópia não leva:** Documentos Exigidos restritos à origem (anunciado no cartão —
`views:2156-2171`, `_perfil.html:7`); conteúdo sem tela (`CAMPOS_SEM_TELA`,
`editais/domain/reaproveitamento.py:24`; `duplicacao.py:78-79`); e **marcos que a origem ainda não
tem** — ver §5.2, o achado mais importante deste relatório.

### 1.2 Cronograma — O(E), do Edital, sem lote

Por Evento (`tpl/_evento.html:18-66`): Tipo\*, Descrição\*, Onde, Início\*, Término — **1 clique + 3
obrigatórios + até 2**, ≈ 4–6 interações. Reordenar é ↑/↓ um passo por clique
(`tpl/_acoes_da_linha.html`, `static/interface/ordenacao.js`). O local do Evento anterior aparece como
*placeholder* e não preenche (`views:1391-1394`). **Nada aqui cresce com P**: o Evento é do Edital.
Mas também nada foi barateado desde 21/09 — não há colar tabela, nem Tipo sugerido, nem Evento
duplicado; Tipo **e** Descrição continuam ambos obrigatórios (M9 do estudo). No reuso, cada Evento
volta com a data da oferta anterior e mantém a etapa pendente até ser corrigido
(`tpl/compor_cronograma.html:17-22`): **O(E) edições de data**.

### 1.3 Etapas de Avaliação — O(S), do Edital

Por Etapa (`tpl/_etapa.html:12-182`): Nome\*, Evento (`select`), Forma (rádio) → Nota mínima e
Pontuação máxima **ou** dois rótulos\*, Peso, Avaliações por inscrição, Eliminatória, Classificatória —
≈ 7–9 interações. **Não cresce com P** (estudo §6.3, e continua assim). O aviso "Etapa sem vínculo
com o Cronograma" é dobrado na Revisão (`interface_extras.py:340`).

### 1.4 Classificação — O(P × (marco + C)) no fluxo linear; O(1) só no fluxo invertido

- **Método comum do sorteio**: 9 controles, uma vez (`tpl/compor_classificacao.html:59-155`). O marco
  que não declara o próprio herda o comum; os 10 campos do método do marco viajam ocultos
  (`tpl/_marco.html:439-448`). **Para sorteio, o método saiu de O(P) para O(1).**
- **Marco** — um fieldset por Perfil, cada um com o seu "Acrescentar marco"
  (`tpl/compor_classificacao.html:160-170`). O marco novo nasce com Código, Denominação e
  arredondamento derivados (`views:2300-2323`). Restam, por marco: Como a ordem é produzida\*
  (`_marco.html:49-61`, IMPEDE se vazio — `validation.py:1694-1738`), Etapas que entram (`select
  multiple`, `:86-114`), Recurso (rádio + prazo + unidade, `:200-244`), Combinação (2 `select`, só com ≥2
  Etapas, `:461-481`), e a **Regra de corte** — 4 `select` sem padrão + Alvo/Suplentes
  (`:504-570`). Desde a `046`, Perfil em que nenhum marco corta é **IMPEDE** (`validation.py:1954-1988`),
  e Perfil sem marco também (`:1741-1785`). **Custo por marco: ≈ 1 + 9 a 13**, contra "1 + 8 a 12" em
  21/09 — o corte, que era opcional, virou obrigatório por Perfil.
- **Critério de desempate**: 1 clique + Ordem\*, Critério\*, Alvo\*, Quando falta\* = **5**
  (`tpl/_criterio.html:10-49`). O `select` do alvo lista **todos os fatos de todos os Perfis**,
  rotulados `LP01 · Data de nascimento` (`views:2277-2282`): **P × F opções** em cada critério, das
  quais só F são válidas — a publicação recusa o critério que aponta fato de outro Perfil
  (`tiebreaker_fact_missing`, IMPEDE, `validation.py:673-675, 763-772`). A tela oferece 45 escolhas
  que ela mesma vai recusar, num Edital de 16 Perfis com 3 fatos.

**O que multiplica:** P × (1 + ~11 + 5C). O duplicar leva marco e critérios — remapeando o critério
para o fato **da cópia** (`duplicacao.py:49-53`) —, mas só se a origem **já tiver marco** quando for
duplicada (`views:2092-2097`). Ver §5.2.

### 1.5 Inscrição — O(D) com o recorte transversal; O(P × D) no recorte exato

- Período de inscrições: um `select` do Evento (`tpl/compor_inscricao.html:17-26`) — datas não se
  redigitam.
- Por documento (`tpl/_documento.html`): Chave\*, Nome\*, Instrução, Perfil (`select`), Modalidade
  (`select`), Modelo (`select`), Obrigatório (já marcado, `:105-106`) — ≈ **1 + 2 a 4**.
- **O recorte transversal** (`044`): o `select` da Modalidade tem o grupo "Em todos os Perfis" — uma
  opção por código, com o alcance escrito ("16 de 16") — e o grupo "Modalidade de um Perfil" com **P ×
  M** opções (`_documento.html:65-80`; `forms:1471-1530`). No 140/2025 são 64 opções exatas e 3
  transversais (AC declarada ampla não aparece, `forms:1513-1516,1529`).
- Requerimento de Matrícula: 2 campos, O(1) (`compor_inscricao.html:83-100`).

**O que multiplica:** D (documentos). Só volta a multiplicar por P quando o documento é **de um Perfil**
— ex.: o item f) do 140/2025, "de acordo com a função pleiteada" — ou quando a condição é **sobre o
candidato** (sexo e idade, servidor, indígena, quilombola), que continua sem forma: vira facultativo
com instrução (decisão D2 em `doc/decisao-recorte-documental.md`).

### 1.6 Anexos — O(A)

Por anexo: rótulo + arquivo + "Acrescentar anexo" = 3 (`tpl/compor_anexos.html:157-177`), mais o
trabalho **fora do sistema** de recortar o PDF-fonte. Fora de `ETAPAS_GRAVAVEIS`, cada operação é um
comando (`views:914-917`).

### 1.7 Conteúdo — O(1), 7 seções textuais fixas

`tpl/compor_conteudo.html`; catálogo em `editais/domain/secoes.py:49-161` (12 seções, 7 `TEXTUAL`,
5 `GERADA`). Nascem com texto institucional; o custo é **revisar**, não digitar. Não cresce com P — mas
também não acomoda seção nova (E5 do estudo).

### 1.8 Revisão — O(achados), e os achados por Perfil **não se dobram**

`_pendencias` roda a validação de publicação inteira (`views:826-887`). Só três famílias se dobram numa
linha: Evento no passado, Evento em ano divergente, Etapa sem Evento
(`interface_extras.py:335-341`). As famílias **por Perfil** continuam uma linha por Perfil, ou por
Perfil × Modalidade:

| Código | Severidade | Unidade | Linhas |
|---|---|---|---|
| `general_competition_modality_undeclared` | AVISO | Perfil | `validation.py:1124-1160` |
| `vacancy_reserved_list_without_row` | AVISO | Perfil | `:2818-2857` |
| `vacancy_row_percentage_divergence` | AVISO | Perfil × Modalidade | `:2935-2969` |
| `milestone_without_cut_rule` | AVISO | marco | `:1991-2044` |
| `order_production_nao_declarada` | **IMPEDE** | marco | `:1694-1738` |
| `profile_without_milestone` (032) | **IMPEDE** | Perfil | `:1741-1785` |
| `profile_without_cut_rule` (046) | **IMPEDE** | Perfil | `:1954-1988` |

A auditoria de consolidação registra o mesmo como RC-10, "colapso por Perfil (32 dos 45)", não
implementado (`doc/auditoria-de-consolidacao-2026-09-26.md:274`).

### 1.9 Submeter, homologar, publicar — O(1)

Três atos (`interface/atos.py:48-117`): Submeter (confirmação), Homologar (Fundamento\*, `:63-73`),
Publicar (Signatário\*, `:103-117`), com troca de identidade entre eles — a segregação exige ao menos
duas pessoas (`interface/acoes.py:190`). ≈ 8–10 interações **independentes do tamanho**. O que cresce é
o que o homologador tem de **ler**: o PDF continua repetindo o Perfil inteiro (34 tabelas em 27 páginas no
140/2025; `specs/043-duplicar-perfil/spec.md` §2 e G-003: "não reduz o documento publicado").

---

## 2. Mapa de loops — "para cada X, o operador repete Y"

Notação: **P** Perfis · **M** Modalidades por Perfil · **F** fatos por Perfil · **K** marcos por Perfil
(quase sempre 1) · **C** critérios por marco · **E** Eventos · **S** Etapas · **D** documentos · **A**
anexos. "Escala" é a das interações humanas; o custo de máquina não entra.

| Operação | Unidade de repetição | Escala atual | Há lote/reuso? | Impacto em edital grande |
|---|---|---|---|---|
| Criar Processo + Edital, Identificação | Edital | O(1), ~7 | — | nenhum |
| Primeiro Perfil completo | Edital | O(1 + M + F), ~12 + 7M + 4F | só "Partir de um Edital anterior" (023), que exige origem **publicada** | 34 no 140/2025; pago uma vez por família sem origem |
| Perfis irmãos | **Perfil** | O(P) × **4** | **duplicar** (043) | 15 × 4 = 60 no 140/2025; 65 × 4 ≈ 260 no multicampi de 66 |
| Divergência entre Perfis irmãos (requisitos, denominação, vagas) | Perfil divergente × campo | O(P_div) | não — "aplicar a todos" é TF-1, não feito | 6 no 140/2025 (4 blocos de requisito em 16 códigos) |
| Modalidades + regra normativa + ampla + reversão + quadro | Perfil × Modalidade | O(P × M) **sem** duplicar; O(M) com duplicar | duplicar copia tudo | 64 Modalidades → 4 digitadas |
| Fatos do desempate | Perfil × fato | O(P × F) sem duplicar; O(F) com | duplicar copia | no 140/2025, 3 fatos × 16 = 48 fatos publicados, 3 digitados |
| Marco classificatório | Perfil × marco | **O(P × K)** no fluxo linear | duplicar copia **só se a origem já tiver marco** (§5.2) | 16 × ~12 = ~190 no 140/2025, ou ~12 |
| Critério de desempate | marco × critério | **O(P × K × C)** no fluxo linear | idem | 16 × 3 × 5 = 240, ou 15 |
| Escolher o fato do critério | critério, numa lista de P × F | tamanho da lista O(P × F) | não | 48 opções `LP01 · …` a cada escolha (`views:2277-2282`) |
| Método do sorteio | Edital | O(1), 9 | método comum (030) | nenhum |
| Evento do cronograma | Evento | O(E), ~5 cada | não (nem colar, nem duplicar) | 13–18 Eventos ≈ 65–90 — **hoje o maior bloco de um Edital médio** |
| Datas do cronograma no reuso | Evento | O(E), 1–2 cada | não | idem |
| Etapa de Avaliação | Etapa | O(S), ~8 | do Edital (sem repetir por Perfil) | nenhum |
| Documento geral | documento | O(D), ~4 | escopo "Todos os Perfis" | nenhum |
| Documento por Modalidade | documento | **O(D)** com o transversal (044); O(P × D) no exato | recorte por código | 112 → 7 linhas no 140/2025 (por construção, não recomposto no navegador — `specs/044-…/rastreabilidade.md:62`) |
| Documento por Perfil | Perfil × documento | O(P × D_perfil) | não; e a cópia **não** o leva (FR-645) | quem duplica depois de declará-lo refaz na Inscrição |
| Documento sob condição do candidato | documento | O(D), mas sem forma | não existe | facultativo com instrução (D2 da decisão de 25/09) |
| Anexo | anexo | O(A), 3 + extração fora do sistema | não | 7–11 no 140/2025 |
| Seções textuais | seção | O(1), 7 fixas | texto institucional pré-preenchido; no reuso, **o da oferta anterior** | revisar prosa, não digitar |
| Ler a Revisão | achado | O(P) e O(P × M) nas famílias por Perfil | dobra **só** Evento/Etapa (#163) | dezenas de linhas com 16 Perfis; IMPEDE misturado (RC-10) |
| Resolver IMPEDE por Perfil (sem marco, sem corte, ordem não declarada) | Perfil ou marco | O(P) | não | 16 IMPEDE iguais se o marco não veio na cópia |
| Submeter · homologar · publicar | Edital | O(1), ~8–10 | — | nenhum na ação; O(P) na **leitura** do PDF |
| Retificar dado comum a N Perfis | Perfil (ou Modalidade de cada Perfil) | **O(N)** | não | ver §4 |
| Restaurar rascunho local perdido | Perfil × coleção aninhada | perde Modalidades, quadro, fatos e marcos de **todo** Perfil acrescentado | — | a perda cresce com P × M (RC-08; `static/interface/rascunho.js:81`, o padrão `^([a-z]+)-(\d+)-(\w+)$` não reconhece `modalidade-3-0-code`) |

**Resposta direta à pergunta central.** Dobrar o Edital **não dobra** o trabalho de Perfis — desde a
`043`, o incremento de um Perfil irmão é ~4 interações, contra ~33. Dobra, integralmente: Eventos,
documentos gerais e anexos (O(E + D + A), sem nenhum mecanismo de lote) — mas estes crescem com o
**certame**, e não com o número de polos. E continua dobrando com P, **no fluxo que a tela sugere**, a
Classificação (marco + critérios por Perfil), a Revisão (achados por Perfil) e qualquer Retificação
de conteúdo comum.

---

## 3. Cenários reais — o que custa hoje, contra 21/09

Estrutura extraída com `pdftotext -layout` + grep (nenhum nome, CPF, e-mail ou telefone copiado). As
contas usam os custos unitários do §1; os números de 21/09 vêm do estudo (§4). **Nada foi percorrido
no navegador nesta revisão**: são estimativas, com faixa, e a conta está escrita para ser refeita.
"Linear" = seguir o assistente na ordem das etapas; "invertido" = compor o marco do primeiro Perfil
**antes** de duplicá-lo (§5.2).

### 3.1 Pequeno — 78/2026 (Libras A1, vagas remanescentes)

**Estrutura:** 2 Turmas (21 e 40 vagas, horários diferentes), nenhuma Modalidade; 11 Eventos (Anexo I);
sorteio eletrônico → análise documental dos sorteados até o número de vagas, com até 30 suplentes por
código de vaga (item 6.10); recurso do resultado preliminar (2 dias); 7 documentos para todos (a–g), um
deles (f, serviço militar) condicionado a sexo e idade; Anexo II (requerimento de matrícula).
Nenhum critério de desempate além do sorteio.

| Etapa | Conta de hoje | Hoje | 21/09 |
|---|---|---:|---:|
| Criação + Identificação | 6 + 1 | 7 | ~7 |
| Perfis | Turma 1: 1 + ~7 campos; Turma 2: duplicar 4 + vagas + horário 2; gravar 1 | ~15 | 2 + 18 = 20 |
| Cronograma | 11 × (1 + 3) + ~6 términos/locais | ~50 | 11 + ~37 = 48 |
| Etapas | 1 Etapa decisória: 1 + 6 | ~7 | 6 |
| Classificação | método comum 9 + 2 marcos × (1 + ordem + corte 5 + recurso 2 ≈ 9) | ~27 (invertido ~18) | 9 + 2 × 8 + 2 ≈ 27 |
| Inscrição | período 1 + 7 × (1 + 3) | ~29 | 7 + ~16 = 23 |
| Conteúdo | 7 seções, ~5 editadas | ~5 | 7 |
| Anexos | 1 × 3 | 3 | 0 (pulado) |
| Revisão (voltas) + atos | ~5 + ~9 | ~14 | 3 IMPEDE/11 AVISO + atos |
| **Total** | | **~150–170** | **~140 + atos ≈ 150** |

**Leitura:** no Edital pequeno **nada mudou em ordem de grandeza**. O custo é dominado por Cronograma,
Documentos e Classificação (~105 de ~155), e nenhuma das entregas de 043/044 os toca. A `046` põe
~4–5 interações a mais em cada marco (a regra de corte, que era opcional, virou condição do Perfil —
`validation.py:1954-1988`), e o pré-preenchimento do marco (`views:2300-2323`) devolve ~2. Saldo ≈ 0.

### 3.2 Médio — 28/2026 (Pós-graduação Informática na Educação, EaD)

**Estrutura:** 7 polos, **idênticos**: 40 vagas = AC 28 + PPI 10 + PcD 2 (Quadro 2), 25% PPI e 5% PcD
declarados **uma vez** (item 4.2), reversão para a ampla "em cada polo" (4.3); 18 Eventos (Anexo I);
sorteio (ampla primeiro, depois as reservas — 8.7) → análise documental → procedimento complementar de
verificação da autodeclaração (entrevista PP, documentos dos indígenas) com recurso próprio; 12
documentos: 7 para todos (a–g), 1 PPI (h), 2 **indígenas** (i — condição sobre o candidato, dentro de
PPI), 2 PcD (j); 5 anexos-modelo (II a VI).

| Etapa | Conta de hoje | Hoje | 21/09 (estimado) |
|---|---|---:|---:|
| Criação + Identificação | | 7 | ~7 |
| Perfis | polo 1: 1 + 6 campos + 3 Modalidades (3 + 6 + 6) + ampla + reversão + convocação + quadro 3 + gravar ≈ 30; 6 cópias × 4 = 24 | **~55** | 7 × ~31 ≈ **~215** |
| Cronograma | 18 × ~4,5 | ~80 | ~80 |
| Etapas | 3 × ~8 | ~24 | ~24 |
| Classificação | comum 9 + 7 marcos × ~9 (linear) · ou 9 + 9 (invertido) | ~72 · **~18** | ~9 + 7 × ~10 ≈ 80 |
| Inscrição | 1 + 12 × ~4 (PPI e PcD por código: 3 linhas; indígenas: facultativo com instrução) | ~49 | ~49 com recorte infiel; **~170** fiel (7 + 5 × 7 = 42 linhas) |
| Conteúdo · Revisão · atos | ~8 + ~6 + ~9 | ~23 | ~23 |
| Anexos | 5 × 3 | 15 | 0 |
| **Total sem anexos** | | **~250–310** | **~390–480** (a faixa alta é o recorte fiel) |

**Leitura:** a etapa Perfis cai **~75%** (~215 → ~55) e o Cronograma passa a ser o maior bloco do Edital
(~80, intocado). O ganho total é de **−20% a −45%** conforme o recorte documental e o fluxo da
Classificação. **Por reuso** (o caminho real do 28/2026, sobre o 149/2024 de 5 polos): 18 Eventos × 1–2
datas (~27), 2 polos novos por duplicar (8), Código/Localidade dos 5 herdados se mudaram (0–10), vagas
por polo se mudaram (0–21), a ocorrência e o método do sorteio herdados, que a D-G3 manda substituir
(2–9), a Identificação (2–3; a Descrição não se copia, FR-007 da `023`) e a revisão de 7 seções de
prosa herdada: **~50–110 interações e a leitura de toda a prosa anterior**. O estudo não registrou este
número com método (§14); ele continua não medido.

### 3.3 Grande — 140/2025 (cadastro de reserva, Tutor Presencial UAB)

**Estrutura:** 16 códigos (LP01–LP11 e TADS11–TADS15); **4 blocos de requisito** para os 16 (LP01–LP03,
LP04, LP05–LP11, TADS — Anexo III), duas denominações de função; 4 Modalidades (AC, PPIQ, PcD, PTT) com
percentuais que valem "para cada curso/área/polo" (item 4.3); **cadastro de reserva, sem quantidade**;
13 Eventos (Anexo II); Prova de Títulos (classificatória e eliminatória, barema no Anexo IV, sem forma
no sistema — RC-64) e verificação da autodeclaração PP (entrevista), cada uma com recurso; desempate em
3 critérios (idade, experiência em meses, curso FIC — item 6.3.2) → **3 fatos por Perfil**; ~16 linhas de
documento: 8 para todos (um deles, f, "de acordo com a função pleiteada"), PcD 2, PPIQ 3 (dois só para
indígena), PTT 1, servidor 1 (condição sobre o candidato), quilombola 1 (submodalidade); 11 anexos, dos
quais 7 são modelos (V–XI).

| Etapa | Conta de hoje | Linear | Invertido | 21/09 (medido) |
|---|---|---:|---:|---:|
| Criação + Identificação | | 7 | 7 | ~7 |
| Perfis | **101 medido** (`043`, sem fatos) + 3 fatos × 4 no LP01 antes de duplicar | ~113 | ~113 | **~530** |
| Cronograma | 13 × ~4,5 | ~60 | ~60 | |
| Etapas | 2 × ~8 | ~16 | ~16 | |
| Classificação | por marco: 1 + ordem + Etapa + corte 5 + recurso 2 + 3 critérios × 5 ≈ 25 | 16 × 25 = **~400** | **~25** (+ ~5 de navegação) | |
| Inscrição | 1 + 16 × ~4 (7 por código) | ~65 | ~65 | ~65 infiel; 112 linhas × ~4 ≈ **~450** fiel |
| Conteúdo · Revisão · atos | ~10 + ~15 + ~9 | ~34 | ~34 | |
| **Total sem anexos** | | **~690** | **~320** | **~825** (730 campos + 95 cliques, **com reuso** do 14/2026 e documentos infiéis) |
| Anexos | 8 × 3 + extração do PDF-fonte | +24 | +24 | 0 |

**Leitura:** a etapa Perfis caiu de ~530 para ~113 (**−79%**), e é o único número medido do lado de
hoje. **O total só cai à metade se o operador inverter a ordem do assistente.** No fluxo linear, a
Classificação reconstrói quase todo o custo que a `043` tirou dos Perfis: ~400 interações, com 48
escolhas de fato numa lista de 48 opções `LP01 · …` (`views:2277-2282`). A Revisão continua
emitindo por Perfil: no cadastro de reserva, o quadro de uma linha zerada produz até P × M avisos de
divergência de percentual (`validation.py:2935-2969`; o estudo contou 32 deles, E8), e nenhum se dobra.

### 3.4 O que ainda cresce com o tamanho, e por quê

| Cresce com | Onde | Por quê |
|---|---|---|
| P, inclinação ~4 | Perfis | Código e Localidade são pedidos a cada cópia (D-003 da `043`); não há "gerar N Perfis desta lista de polos" |
| P_div × campos | Perfis | divergência entre irmãos é editada Perfil a Perfil; os 4 blocos de requisito do 140/2025 custam 3 edições, e os 11 Perfis que partilham um bloco não o partilham no sistema |
| P × K × (12 + 5C) | Classificação, no fluxo linear | o marco é do Perfil (`views:907-911`, `compor_classificacao.html:25-30`), e a cópia só o leva se ele já existir |
| P × F | cada `select` de critério | a lista de fatos é do Edital inteiro (`views:2277-2282`) |
| P × M | cada `select` de Modalidade do documento | o grupo "Modalidade de um Perfil" lista todos os pares (`_documento.html:75-79`) |
| P, P × M | Revisão | 7 famílias por Perfil/marco, nenhuma dobrada (§1.8) |
| E | Cronograma | sem lote, sem colar, Tipo e Descrição obrigatórios |
| D, A | Inscrição, Anexos | por construção (o Edital declara D documentos); condição sobre o candidato sem forma |
| P | PDF e leitura do homologador | o documento publicado repete o Perfil inteiro (`043` G-003) |
| N (Perfis afetados) | Retificação | §4 |

Projeção do multicampi (66 Perfis, 4 Modalidades, estudo §8): Perfis ≈ 34 + 65 × 4 + divergências
≈ **~300** (contra ~2.200 em 21/09). Classificação linear ≈ 66 × 25 ≈ **~1.650**; invertida ≈ 25 a 75
(uma origem por função). **Neste tamanho, a Classificação no fluxo linear passa a custar cinco vezes a
etapa de Perfis** — é o maior loop humano que restou.

---

## 4. Retificar um dado comum a N Perfis

A tela de Retificação edita o conteúdo vigente e traduz a diferença em Alterações, uma por caminho
(`interface/retificacao.py:1-17`). Cada Perfil, cada Modalidade de cada Perfil e cada marco é um grupo
próprio de campos; um índice de âncoras mitiga a rolagem (`tpl/retificar.html:73-91`). **Não há, em
lugar nenhum da Retificação, "aplicar a todos" ou edição em lote** (varredura em `retificacao.py`,
`retificar.html` e `_retificacao_*.html`; as únicas ocorrências de "todos os Perfis" são o recorte
transversal do documento, `retificacao.py:380, 709` [411, 867]).

### 4.1 Na `main` em `79aeb847` (antes da 048)

| O que se corrige | Onde mora | Custo para N Perfis | Observação |
|---|---|---|---|
| Atribuições, carga horária, remuneração, descrição, requisitos | `CAMPOS_PERFIL`, `retificacao.py:63-96` | **N edições** (colar N vezes) | N Alterações no ato e N linhas no "O que mudou" |
| Percentual, fundamento ou versão da cota | `CAMPOS_REGRA`, por Modalidade de cada Perfil, `:163-178` | **N**, e +N se as linhas do quadro acompanharem (`CAMPOS_DA_LINHA`, `:159-162`) | não acompanhar deixa N avisos de divergência (`validation.py:2935-2969`) |
| Denominação de uma Modalidade | `CAMPOS_MODALIDADE`, `:154` | **N, obrigatoriamente todas** se um documento transversal usar o código | 1 a N−1 edições → IMPEDE (`044` FR-706, SC-266: "renomear em 1 dos 16 produz exatamente 1 IMPEDE… nos 16 produz zero") |
| Critério de desempate | `CAMPOS_CRITERIO`, só a **ordem** (`:335` [366]); o critério é removível | trocar o critério nos N marcos: **N remoções**, e na `main` não há como acrescentar o substituto | é o beco que a `048` fecha |
| Janela recursal, arredondamento, corte, método próprio | `CAMPOS_DA_JANELA` `:241`, `CAMPOS_DO_ARREDONDAMENTO` `:231`, `CAMPOS_DO_CORTE` `:286` [292], `CAMPOS_DO_METODO` `:263` [269] | **N** (um por marco) | |
| Método comum do sorteio | `CAMPOS_DO_METODO_COMUM`, `:139-153` | **1** | o único conteúdo comum que a Retificação corrige de uma vez |
| Recorte de um documento por código | `CAMPOS_DOCUMENTO` `modalityCode`, `:368-385` [399-416] | **1** | mas N documentos exatos publicados **não viram 1** por Retificação (`044`, D-009) |
| Evento, Etapa, seção | `CAMPOS_EVENTO` `:100`, `CAMPOS_ETAPA` `:342` [373], `CAMPOS_SECAO` `:356` [387] | 1 por item | não dependem de P |

Os atos da Retificação (justificativa, submissão, homologação, publicação) são O(1). O que é O(N) é
**achar e editar** o mesmo campo em N grupos, e depois **conferir** N linhas no resumo antes → depois.

### 4.2 O que a `048` acrescenta (#197, mesclada em `0113b782`)

Lido em `git diff origin/main...origin/claude/retificacao-cobertura-auditoria-b7eabb`. A `048` fecha
becos reais (`RC-37`, `RC-38`), e todos os acréscimos são **por entidade**:

| Acréscimo | Campos | Unidade | Linhas (branch da 048) |
|---|---|---|---|
| Modalidade num Perfil publicado | Perfil (`select`), Código, Denominação, Descrição, Fundamento, Versão, Percentual, "É a ampla", Vagas da cota — **~10 por Perfil** | Perfil | `NOVA_MODALIDADE` em `interface/retificacao.py:610-621`; botão único em `retificar.html:171-176` |
| Critério de desempate | Marco (`select`), tipo, alvo, quando falta, ordem — **~6** | marco | `NOVO_CRITERIO`, `retificacao.py:633-640`; `retificar.html:207-211` |
| Janela recursal que nasce | prazo em dias — ~2 | marco | `CAMPOS_DO_NASCIMENTO_DA_JANELA`, `:249` |
| Regra de corte que nasce | 6 campos | marco | `CAMPOS_DO_NASCIMENTO_DO_CORTE`, `:341-361` |
| Reversão que nasce | 1 escolha | Perfil | FR-791 |

E a spec **proíbe** o mecanismo que tornaria isso O(1): *"A feature MUST NOT criar mecanismo de
acréscimo além dos dois que existem"* (FR-802). Consequências concretas:

- **O caso-tipo da `048` é produzido pela `043`.** Um Perfil publicado sem a ampla (RC-37) raramente está
  sozinho: se ele foi a origem das cópias, os 16 nasceram sem ela. Corrigir custa 16 × ~10 ≈ **~160
  interações** numa Retificação — mais que a etapa Perfis inteira do mesmo Edital hoje (~113).
- **Trocar um critério de desempate nos 16 marcos**: 16 remoções + 16 × ~6 acréscimos ≈ **~110**.
- **O documento da Modalidade nova só entra na Retificação seguinte** (edge case da spec 048, §Edge
  Cases): são **dois atos** com aprovação cada, e o recorte por código só serve se o código estiver nos
  Perfis que a têm.
- A `048` não mexe em nada do que já era O(N) (§4.1).

---

## 5. Complexidade transferida — onde a redução de campos criou trabalho de outro tipo

### 5.1 Duplicar produz N cópias independentes, que depois precisam ser mantidas iguais

A cópia não guarda vínculo (`043` D-005) e não registra origem (D-006). Nada no sistema confere que os
16 Perfis continuem iguais no que o Edital declara uma vez — a única conferência transversal é
código ⇒ denominação, e só quando um documento usa o código (`044` FR-706/707). A própria `043`
registrou o risco (G-001: *"uma Modalidade errada no Perfil de origem é copiada quinze vezes… e se
corrige Perfil a Perfil"*), e a auditoria o reclassificou: *"a 043 **barateou** produzir as cópias, e com
isso **aumentou** o risco de divergência"* (`doc/auditoria-de-consolidacao-2026-09-26.md:532`). O
esforço saiu da **digitação** e foi para a **manutenção**: composição O(1) + cópia O(P) com passo 4;
correção O(P) com passo cheio, na composição e na Retificação (§4).

### 5.2 O duplicar só economiza a Classificação se o operador inverter a ordem do assistente

É o achado de maior efeito nesta reavaliação, e não está escrito em lugar nenhum:

1. O duplicar leva os marcos da origem **gravada**, ou os que estão em trânsito numa cópia ainda não
   gravada (`views:2092-2097`; `043` R-003).
2. O marco se declara na etapa **Classificação**, a quinta (`views:898-911`), que só mostra Perfis
   **gravados** (`compor_classificacao.html:160`; `forms.perfis_do_edital`, `forms:807`), e cujo marco
   enumera Etapas (etapa 4) e governa uma Etapa pelo corte.
3. Logo, no fluxo que o assistente sugere — compor o LP01 e duplicá-lo na etapa 2 — **as quinze cópias
   nascem sem marco**, e a Classificação volta a pedir 16 × (marco + 3 critérios). Para herdar, é preciso:
   compor o LP01 → gravar → Cronograma → Etapas → Classificação do LP01 → **voltar** a Perfis → duplicar.
4. A tela não diz isso. O "Como preencher" promete *"um Perfil com tudo o que este tem — Modalidades,
   quadro, fatos e marcos de classificação"* (`compor_perfis.html:85-88`); o anúncio da cópia só fala
   dos marcos **quando há** marcos (`_perfil.html:7`) — sem marco, silêncio.
5. A medição de 101 interações **não compôs marcos** (`specs/043-duplicar-perfil/rastreabilidade.md`,
   "Não medido aqui: a economia na etapa Classificação"; `research.md` R-011 a exclui de propósito).

Custo da diferença no 140/2025: ~400 contra ~25 interações; no multicampi, ~1.650 contra ~75.
E a `046` agravou o ponto sem querer: sem marco e sem corte por Perfil agora são IMPEDE
(`validation.py:1741-1785, 1954-1988`), de modo que o fluxo linear termina numa Revisão com um IMPEDE
por Perfil até cada marco ser composto à mão.

### 5.3 A Revisão ficou maior por Perfil, e a dobra não chegou até ela

A `032`/`046` levaram para a publicação três exigências por Perfil ou marco (sem marco, sem corte,
ordem não declarada), corretas normativamente. Cada uma emite uma linha por Perfil. A dobra do #163
cobre só Evento e Etapa (`interface_extras.py:335-341`); as sete famílias por Perfil do §1.8 não se
dobram, e nada ordena por severidade (RC-10). O trabalho saiu do formulário e foi para a **leitura e
triagem** de uma lista que cresce com P.

### 5.4 O recorte transversal exige entender "código da Modalidade" como identidade do Edital

O ganho (112 → 7 linhas) depende de um conceito que a tela não nomeia em lugar nenhum da etapa Perfis:
o **código** da Modalidade passa a ser a chave que liga documento e Perfis, é **estrutural e não se
retifica** (`doc/decisao-recorte-documental.md`, "O que já está fixado"), e a denominação dele passa a
ter regra de coerência na publicação (FR-706). Trocas associadas:

- o `select` da Modalidade do documento tem **dois grupos** — "Em todos os Perfis" e "Modalidade de um
  Perfil", este com P × M opções (`_documento.html:65-80`) —, e a combinação "Todos os Perfis" + exata
  continua IMPEDE (#161, FR-708);
- a Modalidade declarada como ampla **não aparece** no transversal (`forms:1513-1516, 1529`): quem
  declarou "AC" como Modalidade vê três opções, e não quatro (a grafia-armadilha da memória do projeto);
- a gravação da etapa **Perfis** pode ser recusada por causa de um **documento** (`044` D-010): remover
  ou renomear o código num Perfil acopla duas etapas;
- renomear a denominação vira operação de N edições obrigatórias (§4.1).

### 5.5 O método comum criou a noção de "marco que diverge"

Declarar uma vez (`compor_classificacao.html:59-155`) trouxe um segundo lugar com os mesmos 9 campos
(o do marco, `_marco.html:271-422`), a frase "Este marco **diverge** do método comum" (`:282-286`), dez
campos ocultos por marco (`:439-448`) e dois grupos na Retificação (`CAMPOS_DO_METODO_COMUM` e
`CAMPOS_DO_METODO`). O custo é conceitual e pequeno — mas é o padrão: cada "declarar uma vez" feito
**sem** mover o objeto para o Edital deixa dois lugares e uma regra de precedência.

### 5.6 O reuso troca digitação por revisão sem marcar o que falta revisar

"Partir de um Edital anterior" copia tudo o que tem forma e as seções de prosa
(`editais/application/reaproveitamento.py`; `reaproveitamento.py:24` só retém o que não tem tela). O
aviso é permanente e em bloco (`compor_base.html:70-83`), e diz "datas, vagas e prazos" mais a
contagem de seções com texto (`views:3686` [3776]). Não há estado "a revisar" por campo ou etapa
(RC-43). O esforço vira **O(E + P + 7 seções)** de conferência, sem sinal de progresso — e a primeira
oferta de cada família continua sendo composta do zero, porque a origem precisa estar publicada
(`reaproveitamento.py:60`, `ORIGENS_ELEGIVEIS`).

### 5.7 O formulário único da etapa cresce com P, e a salvaguarda local não o acompanha

A etapa Perfis envia todos os Perfis num POST e a gravação substitui a etapa inteira (`replace_draft`;
comentário em `editais/application/reaproveitamento.py:68-73`). Com 16 Perfis × 4 Modalidades, a página
tem da ordem de mil controles. O rascunho local, que é a salvaguarda contra falha de envio, reconhece
só campos `prefixo-N-campo` (`static/interface/rascunho.js:81`) e recria os cartões por fragmento vazio
(`:120-133`): Modalidades, quadro, fatos e marcos em trânsito de **todo** Perfil acrescentado se perdem
na restauração (RC-08; `043` G-006). Quanto maior o Edital, maior o que se perde — e a `043` aumentou a
quantidade de conteúdo não gravado que uma sessão acumula antes do primeiro "Salvar".

### 5.8 As listas de escolha crescem com P e oferecem o que a publicação recusa

Com a composição barata, o custo que sobra por Perfil passa a ser **escolher certo em listas longas**. O
alvo do critério lista P × F fatos, e só os F do próprio Perfil são válidos (`views:2277-2282`;
`validation.py:763-772`). A Modalidade do documento lista P × M pares exatos ao lado das opções
transversais (`_documento.html:75-79`). O Perfil do documento lista P opções (`:44-50`). Nenhuma dessas
listas se restringe pelo contexto do cartão, e o erro só aparece na Revisão.

---

## 6. Achados principais

1. **A etapa Perfis deixou de ser o gargalo.** Com a `043`, o Perfil irmão custa ~4 interações, contra
   ~33 (medido: 101 contra ~530 no 140/2025). A curva continua linear, com a inclinação oito vezes menor.
   É a única redução de ordem de grandeza desde 21/09.
2. **O gargalo mudou de lugar, para a Classificação, e só some se o operador inverter o assistente.** O
   duplicar leva marcos e critérios apenas se a origem já os tiver gravado. Mas o marco se declara na
   etapa 5, depois de Cronograma e Etapas, e a tela não avisa (§5.2). No fluxo linear, o 140/2025 custa ~400
   interações de Classificação, e o multicampi ~1.650. A medição da `043` excluiu essa etapa.
3. **A `046` subiu o piso por Perfil.** A regra de corte virou condição de publicação do Perfil: são 4
   `select` sem padrão em cada marco, e dois IMPEDE novos por Perfil. É uma decisão normativa certa, mas
   ela transformou um aviso opcional em trabalho obrigatório O(P) e em linhas O(P) na Revisão.
4. **No Edital pequeno nada mudou.** O 78/2026 custa hoje o que custava (~150), porque é Cronograma +
   Documentos + Classificação, e nenhuma entrega mexeu em Evento. **No médio**, a queda é de 20% a 45%
   (~250–310 contra ~390–480). O Cronograma (~80, O(E), sem lote) virou o maior bloco.
5. **A Revisão continua proporcional a P.** São sete famílias de achado por Perfil ou marco, e nenhuma se
   dobra (RC-10). O #163 dobrou só Evento e Etapa.
6. **O comum aos Perfis continua morando N vezes, e agora é mais fácil de produzir errado.** Duplicar gera
   cópias independentes, e nada confere a igualdade além de código ⇒ denominação. Retificar atribuições,
   percentual, fundamento, denominação ou critério custa N edições. A denominação ligada a um documento
   transversal custa N **obrigatórias**. O método comum do sorteio é o único conteúdo comum que se retifica
   uma vez.
7. **A `048` fecha becos reais, mas um a um, e proíbe o lote (FR-802).** A Modalidade esquecida na origem
   e copiada para 16 Perfis custa ~160 interações para retificar, mais que a etapa Perfis inteira desse
   Edital hoje. O documento da Modalidade nova exige uma segunda Retificação.
8. **O recorte transversal cortou 112 → 7 linhas por construção, ainda não medido no navegador.** O preço
   é conceitual: o código da Modalidade como identidade do Edital, estrutural e não retificável. Vêm junto
   um `select` com P × M opções exatas, a ampla declarada excluída e a etapa Perfis podendo ser recusada por
   causa de um documento.

## 7. O que esta reavaliação não fez

- Não percorreu a interface: nenhum número de "hoje" foi medido, exceto os 101 da `043` (medidos por
  ela). As faixas são de custo unitário, com a conta escrita.
- Não mediu tempo, nem erro de operador.
- Não percorreu o reuso 149/2024 → 28/2026 (continua não medido desde 21/09, §14 do estudo).
- Não leu o código da `048` além dos campos e templates novos; o comportamento veio da spec e do diff.
