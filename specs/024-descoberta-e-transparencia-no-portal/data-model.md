# Modelo de dados — 024 Descoberta e Transparência no Portal Público

**Spec:** [spec.md](spec.md) · **Pesquisa:** [research.md](research.md)

> **Nenhuma tabela nova, nenhuma coluna nova, nenhuma migration.** É a `D-001`, e este documento
> existe para mostrar **de onde** cada informação da tela vem — não para propor persistência.

---

## 1. O que já está persistido, e é tudo o que a feature lê

| Origem | O que guarda | Quem a feature lê |
|---|---|---|
| `VersaoConsolidada` | o conteúdo normativo vigente do Edital, em `content`; `valid_from` é o início da vigência | as duas telas |
| `Publicacao` | cada ato publicado: `published_at`, `effective_at`, `publication_order`, e o documento gerado | a página da seleção |
| `Retificacao` | `justification`, o vínculo com a `Publicacao` que a publicou, `status` | a página da seleção |
| `AlteracaoNormativa` | `target_path`, `operation`, `order` — o que cada Retificação alterou | a página da seleção, traduzida (T-002) |
| `Edital` | `institution_scope`, `status` | as duas telas |

`ProvenienciaConteudo` **não é lida**: ela endereça caminho por publicação, e a página não expõe
caminho (`D-005`).

---

## 2. Os modelos de leitura

Estruturas montadas por requisição, entregues ao template, descartadas. Nada aqui é gravado.

### 2.1 `Selecao` — o que a vitrine e o detalhe já montam

Existe hoje, e permanece. Campos: `edital_id`, `periodo`, `processo_codigo`, `processo_titulo`,
`unidade`, `numero`, `ano`, `titulo`, `descricao`, `publicacao_id`, `anexos`.

**Acréscimos desta feature:**

| Campo | Origem | Requisito |
|---|---|---|
| `vigente_desde` | `VersaoConsolidada.valid_from` | `FR-131`, `T-006` |
| `cronograma` | `content["schedule"]`, via a função reusada da T-003 | `FR-125` |
| `atos` | Publicações e Retificações do Edital (T-001) | `FR-129` |

### 2.2 `Perfil` — a vaga

Existe hoje: `codigo`, `nome`, `descricao`, `localidade`, `vagas`, `reserva`, `requisitos`,
`modalidades`, `documentos_anunciados`, e o estado do convite.

**Acréscimos:**

| Campo | Origem no conteúdo publicado | Requisito |
|---|---|---|
| `atribuicoes` | `duties` | `FR-134` |
| `carga_horaria` | `workload` | `FR-134` |
| `remuneracao` | `compensation` | `FR-134` |
| `oferta` | derivado de `immediateVacancies` + `reserveType` | `FR-136` |

Os três primeiros são sempre presentes no conteúdo publicado, com `""` quando não declarados — é o
que a validação do snapshot garante. **`""` significa não declarado, e a linha some** (`FR-135`,
`D-009`).

`oferta` é a leitura principal da quantidade. Uma regra, três formas:

```text
vagas > 0                        → "N vagas imediatas" (+ menção à reserva, se houver)
vagas == 0 e reserva declarada   → "Cadastro reserva" (+ "sem vagas imediatas", secundário)
vagas == 0 e sem reserva         → "sem vagas imediatas"
```

### 2.3 `Evento` — o marco do cronograma

Já montado pela função que a T-003 move de lugar. Campos: `nome`, `inicio`, `fim`, `situacao`
(`concluido`, `em_curso`, `futuro`), `local`.

**Invariante:** `situacao` descreve o Evento (`FR-126`). Nenhum campo aqui sabe quem está lendo — é
o que separa esta estrutura da que a área do candidato usa para falar da inscrição da pessoa.

### 2.4 `Ato` — o histórico normativo *(novo)*

Uma linha por ato publicado, em ordem cronológica.

| Campo | Origem | Observação |
|---|---|---|
| `natureza` | `abertura` ou `retificacao` | derivada da existência de `Retificacao` ligada à `Publicacao` |
| `publicado_em` | `Publicacao.published_at` | `FR-129` |
| `vigente_desde` | `Publicacao.effective_at` | vigência pode ser posterior à publicação |
| `documento_id` | `Publicacao.id` | endereça o documento daquele ato (`FR-132`) |
| `justificativa` | `Retificacao.justification` | só na retificação |
| `alteracoes` | lista de `AlteracaoLegivel` | só na retificação (`FR-130`) |

**Só Retificação publicada entra.** As em elaboração, em revisão, homologadas e canceladas não são
atos publicados — anunciá-las diria ao público que o Edital mudou antes de ele ter mudado.

### 2.5 `AlteracaoLegivel` — o que mudou, em português *(novo)*

| Campo | Conteúdo | Exemplo |
|---|---|---|
| `onde` | a entidade alterada, pelo rótulo que ela tem no conteúdo-base | `Perfil "Professor de Informática"` |
| `campo` | o campo alterado, nomeado no domínio | `Vagas imediatas` |
| `operacao` | acrescentado, alterado ou removido | `alterado` |

**Não carrega valor anterior nem novo** (T-002). Quem quer o texto do ato abre o documento da
Retificação, que está na mesma linha do histórico.

Caminho não reconhecido pelo tradutor **não produz linha** (`D-009`).

### 2.6 `Consulta` — a busca da vitrine *(novo)*

| Campo | Valores | Ausente |
|---|---|---|
| `busca` | texto dobrado (T-005) | sem busca |
| `unidade` | escopo institucional publicado | todas |
| `situacao` | `aberta`, `futura`, `encerrada`, `sem-prazo` | todas |
| `perfil` | denominação de Perfil publicada | todos |
| `ordem` | `prazo` \| `recentes` | `prazo` |

**Não é entidade persistida** (`D-002`): vive no endereço, é reconstruída a cada requisição, e valor
não reconhecido é lido como ausência (T-004).

Deriva dela o que a tela precisa dizer: `total_encontrado` — **um número só, global** (`FR-141`) —,
`filtrando` (há algo a limpar) e `querystring` (o que viaja nos links, T-007).

E `filtrando` decide a forma da lista, não só o botão de limpar: sem consulta a vitrine agrupa pelas
quatro situações (`FR-146`); com consulta é uma lista única ordenada, e a marca de situação de cada
cartão é o que mantém as quatro distinguíveis (`FR-146a`, `FR-145`).

---

## 3. Transições de estado

**Nenhuma.** A feature não tem entidade com ciclo de vida: ela lê estado que outras features
produziram.

A única classificação que ela calcula é a situação do período de inscrições, e ela já é função pura
do conteúdo publicado e do instante — quatro saídas, nenhuma persistida:

```text
sem Evento designado ────────────► sem prazo declarado
                         agora < início ────► futura
início ≤ agora ≤ fim ──────────────────────► aberta
                         agora > fim ──────► encerrada
```

---

## 4. Regras de validação

Não há entrada de dados nesta feature: nenhum formulário grava, nenhum campo é validado para
persistência. O que existe é **saneamento de consulta**, e ele tem uma regra só:

> Parâmetro não reconhecido, ou valor fora do conjunto declarado, é tratado como ausência do filtro
> — nunca como erro, nunca repassado adiante.

Vale também para o que atravessa para o link de volta (T-007): só os cinco parâmetros da §2.6
sobrevivem à travessia.

---

## 5. Consultas ao banco

| Tela | Consultas | Cresce com |
|---|---|---|
| Vitrine | as duas que já existem: identificar a versão vigente por Edital, e materializar as vencedoras | número de seleções publicadas |
| Seleção | a que já existe, mais uma para os atos publicados do Edital (T-001) | número de atos daquele Edital |

Busca, filtro e ordenação **não acrescentam consulta**: operam sobre o que a vitrine já carregou
(`D-003`).

O histórico usa `select_related` para o documento e `prefetch_related` para as alterações, como o
selector existente já faz — sem isso, cada Retificação viraria uma consulta própria.
