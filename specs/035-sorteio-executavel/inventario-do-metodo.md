# Inventário da superfície do método — 035 · Sorteio executável

**Phase 1, tarefas `T003`, `T004` e `T011`.** Medido em 18/09/2026 nesta worktree, contra a `main`
`9b72d75`. Cada linha foi classificada pelo `if` que decide, e não pela leitura da definição da
função — foi essa leitura por definição que produziu três medições erradas na `033`.

---

## T003 · Todo ponto que **valida** campo do método

A conferência do método é **uma** função, e os dois métodos — o próprio do marco e o comum do
Edital — atravessam ela. É o que torna a sexta guarda suficiente sozinha.

| Ponto | Arquivo | O que decide |
|---|---|---|
| `_validar_metodo_de_sorteio` | `editais/domain/perfis.py:401` | a função única. Confere presença dos sete campos, o par `rule`/`text` das duas regras, e chama os cinco validadores de forma |
| `_validar_algoritmo_publicado` | `editais/domain/perfis.py:553` | `algorithm` ∈ `chave.ALGORITMOS` |
| `_validar_fonte_publicada` | `editais/domain/perfis.py:508` | `source` ∈ `fontes.FONTES` |
| `_validar_instante_da_ocorrencia` | `editais/domain/perfis.py:526` | `occurrenceAt` é RFC 3339 **com fuso** |
| `_validar_regra_publicada` | `editais/domain/perfis.py:585` | `normalization.rule` ∈ `normalizacao.REGRAS` |
| `_validar_substituicao_publicada` | `editais/domain/perfis.py:571` | `substitutionRule.rule` ∈ `substituicao.REGRAS` |
| `_validar_etapa_de_habilitacao` | `editais/domain/perfis.py:490` | `qualifyingStageId` ∈ as Etapas do marco |
| **`occurrence`** | — | **nada.** Aparece uma única vez em `perfis.py`, na tabela `CAMPOS_DO_METODO`, como rótulo |

**Confirma o `R-2` do `research.md`, e o número é o mesmo:** cinco campos de forma conferida, e a
ocorrência sem nenhuma.

### Por onde a função é alcançada — e é aqui que a `FR-514` mora

| Caminho | Chamador | Ato |
|---|---|---|
| Gravar o rascunho | `editais/application/draft.py:198` → `validate_profiles` | elaboração |
| Gravar o rascunho, método comum | `editais/application/draft.py:207` → `validate_common_draw_method` | elaboração |
| Aferir publicabilidade | `editais/domain/validation.py:1407` → `_coerencia_do_metodo_de_sorteio` | **publicação _e_ Retificação** |

**A terceira linha é o risco que a `FR-514` nomeia.** `_coerencia_do_metodo_de_sorteio` não recebia
`ato`, e `retificacoes.py:531` afere o conteúdo que a Retificação produziria com
`blocking_findings(validate_for_publication(content, ato=ATO_DE_RETIFICACAO))`. Uma sexta guarda
escrita **sem** recorte por ato tornaria irretificável todo Edital do acervo cuja ocorrência não
satisfizesse a forma — inclusive por uma Retificação que só corrige uma data.

**O precedente do recorte está no mesmo arquivo**, escrito pela `032`:
`_metodo_do_sorteio_publicavel` abre com `if ato != ATO_DE_PUBLICACAO: return []`, e a razão que
ele registra é literalmente esta — *"um Edital que declarou o sorteio antes desta feature não pode
ficar irretificável por não ter dito o que a capacidade não pedia"*.

---

## T003 · Todo ponto que **lê** a derivação em prosa (`derivation`)

| Onde | Quantos | O que faz com ela |
|---|---|---|
| `interface/forms.py:298,435` | 2 | carrega do formulário e devolve para a tela |
| `interface/retificacao.py:143,267` | 2 | declara o campo retificável |
| `interface/templates/.../_marco.html:290-292,378` | 2 | caixa de texto, e o campo oculto que a preserva |
| `interface/templates/.../compor_classificacao.html:86-88` | 1 | caixa de texto |
| `interface/templates/.../sorteio.html:85` | 1 | **exibe**, com o rótulo *Derivação* |
| `editais/domain/perfis.py:391` | 1 | rótulo, na tabela `CAMPOS_DO_METODO` |
| `editais/domain/mutabilidade.py:219,375` | 2 | declara retificável, na raiz e no marco |
| `processos/.../seed_demo.py:419,440` | 2 | dado de exemplo, e o comentário que explica a distinção |

**`sorteios/domain/`: zero. `sorteios/application/`: zero.** Nenhum caminho de execução a lê.

---

## T003 · Todo ponto que **trata** a falha da derivação da ocorrência

| Ponto | Arquivo | O `if` que decide |
|---|---|---|
| A recusa é levantada | `sorteios/domain/substituicao.py:38` | `if achado is None:` → `DomainError("substitution_rule_not_applicable", …)` |
| A cadeia esgota | `sorteios/domain/substituicao.py:96` | o `for` percorre e não acha → `DomainError("substitution_chain_exhausted", …)` |
| **As duas caem juntas** | `sorteios/application/previa.py:96` | `except DomainError as esgotada:` — **sem distinguir o código** |
| A tela | `interface/templates/.../sorteio.html:171` | o `{% else %}` do bloco da ocorrência, com a frase da indisponibilidade |

**Confirma o `R-4`.** A frase específica e correta existe — ela é o `detail` do
`substitution_rule_not_applicable` — e o `except` a descarta: o `motivo` só sai na lista das
ocorrências **registradas como indisponíveis**, e quando a referência declarada nunca foi
derivável essa lista é vazia. A frase certa é jogada fora a uma linha de onde seria exibida.

---

## T004 · PORTÃO DE MEDIÇÃO — quantos Editais do acervo têm ocorrência fora da forma

**Resposta: zero.** Levantado em duas frentes, porque nenhuma delas sozinha responde.

### Frente 1 — todo conteúdo publicado nos bancos desta máquina

Varredura por `jsonb_path_query` sobre `publicacoes_versaoconsolidada`, em **17** bancos: o do
checkout principal e os de todas as worktrees e demonstrações. Foram lidos o método comum
(`$.drawMethod.occurrence`) e todo método próprio de marco
(`$.profiles[*].classificationMilestones[*].drawMethod.occurrence`).

| Banco | Ocorrências publicadas |
|---|---|
| `processo_seletivo` | `5965`, `5955` |
| `processo_seletivo_033`, `ps_034_recorte` | `5926` |
| `ps_auditoria_e2e`, `ps_demo_025` a `ps_demo_028`, `ps_demo_029d`, `ps_ux_p1` | `5926` |
| `ps_demo_024` | `5926`, `5927` |
| `ps_demo_029` | `5956`, `5957` |
| `ps030_rebase`, `ps_034_percurso`, `ps_aval_0912`, `ps_demo_016`, `ps_demo_019` | nenhuma publicação |

**Todas terminam em número. Nenhuma fora da forma.**

### Frente 2 — toda declaração de `occurrence` no repositório

**16 declarações**, das quais **13** terminam em número e **3** não. As três estão no mesmo
arquivo — `tests/unit/publicacoes/test_pdf_classificacao.py`, linhas 417, 432 e 591 —, todas na
forma `'concurso 6100 da Loteria Federal'`. **Confirma o `R-6`, número por número.**

Elas são fixtures de teste, e **não** acervo: nenhuma delas é conteúdo publicado por alguém. São a
evidência do defeito — alguém do próprio projeto escreveu a referência como uma pessoa escreve —, e
a `T024` as corrige sem tocar a regra.

### A decisão que o número autoriza

**Zero Editais do acervo seriam impedidos**, e por isso a guarda vai para junto das outras cinco,
em `editais/domain/perfis.py`, como a `T004` previu para este desfecho.

**O recorte por ato continua obrigatório, e o zero não o dispensa.** A `FR-514` proíbe que a guarda
torne o acervo irretificável, e o alcance da guarda não é uma função do censo de hoje: qualquer
instalação — ou qualquer conteúdo publicado antes desta feature, aqui ou em produção — passaria por
`_coerencia_do_metodo_de_sorteio` no ato de Retificação. O censo diz que **nada quebra hoje**; o
requisito diz que **nada pode prender amanhã**. São coisas diferentes, e a segunda é a que governa
onde a conferência é conferida.

---

## T011 · A derivação em prosa, conferida depois da entrega

**O campo continua texto livre**, nas duas telas de composição e na Retificação. A varredura de
leitores foi refeita depois da implementação e **continua devolvendo zero** caminhos de execução —
nenhuma ocorrência em `sorteios/domain/` e nenhuma em `sorteios/application/`.

A `FR-510` é o requisito mais fácil de perder de vista porque manda **não fazer** o que a auditoria
parecia pedir. Trocá-lo por um código removeria do Edital a frase que diz a norma em português, que
é a função dele; quem deriva de fato é a regra de substituição, que já é vocabulário fechado.

**O que mudou nele, e por quê:** só o **rótulo** na tela de Retificação, que dizia *"Como a
ocorrência foi escolhida"* enquanto a composição e o documento dizem *"Como a ocorrência decorre da
data programada"*. É a `T013`, é o Princípio I, e não é mudança de espécie do campo.

---

## Um achado de passagem, registrado e **não** corrigido

As duas telas de composição montam os `<option>` da **regra de normalização** e da **regra de
substituição** à mão, em HTML literal, com rótulos em prosa — `Os dígitos do material, na ordem em
que aparecem` — enquanto `opcoes_do_metodo` lê os mesmos dois vocabulários de quem os executa.
São **duas origens para o mesmo vocabulário**, que é exatamente o que a `FR-507` proíbe para o
algoritmo e a fonte. Acrescentar uma terceira regra de normalização hoje a faria aparecer na
Retificação e **não** na composição, sem que nada avisasse.

**Não foi corrigido aqui**, e a razão é a `FR-507`: ela nomeia **o algoritmo e a fonte**, e o
recorte da feature é esse. Corrigir os outros dois obriga a decidir o que fazer com os rótulos em
prosa — que são melhores do que o identificador cru que `opcoes_do_metodo` devolve, e que a
Retificação exibe hoje. Isso é desenho de vocabulário de tela, é decisão de quem governa o backlog,
e vira spec própria.
