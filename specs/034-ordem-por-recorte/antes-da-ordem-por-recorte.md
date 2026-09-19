# O "antes" da `034` — gravado em 18/09/2026, antes da primeira edição de código

**Por que este arquivo existe.** A conferência da entrega é **caso a caso**, e não por contagem: um
teste pode manter o número de asserções e trocar o que afirma. E a prova de imutabilidade do acervo
(`FR-504`, `SC-173`) precisa de um "antes" que **só existe agora** — depois da primeira edição não
há mais o que exportar, e a prova deixa de ser refazível.

Base: `main` `d30f6d8`. Ambiente: PostgreSQL local, banco `ps_034_recorte`, worktree própria.

---

## 1. A contagem da suíte

```
cd backend && make lint check test-pg
```

| | Antes |
|---|---|
| `ruff check` | `All checks passed!` |
| `ruff format --check` | `1110 files already formatted` |
| `manage.py check` | `no issues (0 silenced)` |
| `makemigrations --check --dry-run` | `No changes detected` |
| `pytest` (PostgreSQL) | **7213 passando, 12 pulados** — 705,40 s |

---

## 2. Os oito casos que a `034` altera, e o que cada um afirma **hoje**

Nomeados em [research.md](research.md) `R-5`. A citação é do código de hoje, e é contra ela que a
`T045` confere.

### `tests/unit/editais/test_executabilidade.py` — cinco dos dez casos do aviso

| # | Caso | O que afirma hoje |
|---|---|---|
| 1 | `test_reserva_em_marco_que_nao_sorteia_produz_aviso_e_nao_impedimento` | `len(achado) == 1`; `severity == WARNING`; `path == "/profiles/id=…/vacancyTable"` |
| 2 | `test_o_aviso_da_reserva_nomeia_a_causa_e_nao_o_sintoma` | seis asserções sobre a mensagem: `"DOC-INFO"`, `"Pessoas com deficiência"`, `"Negros"`, `"CLASS-TUT"`, `"lista única"`, `"só a ordem sorteada é emitida por recorte"`, e `"não tem ordem emitida" not in` |
| 3 | `test_o_aviso_da_reserva_nao_e_emitido_na_retificacao` | `achados(…, ato=ATO_DE_RETIFICACAO) == []` |
| 4 | `test_o_aviso_alcanca_o_segundo_marco_quando_o_primeiro_sorteia` | `len(achado) == 1`; `"COMPUTA" in message`; `"SORT-X" not in message` |
| 5 | `test_dois_marcos_em_lista_unica_saem_num_achado_so_que_nomeia_os_dois` | `len(achado) == 1`; `"os marcos CLASS-TUT e COMPUTA-2" in message`; `path == …/vacancyTable` |

**Os cinco que NÃO mudam**, e que a conferência tem de encontrar intactos:
`test_perfil_cujo_marco_sorteia_nao_recebe_achado`,
`test_a_modalidade_declarada_como_ampla_nao_e_lida_como_reserva`,
`test_linha_reservada_zerada_nao_produz_aviso`,
`test_perfil_sem_marco_algum_nao_acumula_o_aviso_da_reserva`,
`test_todos_os_marcos_sorteando_continua_sem_achado`.

> O segundo deles passa a valer **vacuamente** depois da `034` — com o aviso aposentado,
> `achados(...) == []` é verdade qualquer que seja a derivação. Ele fica, e **não** serve de guarda
> da derivação única: quem guarda essa é a `SC-172`, que compara as duas listas.

### `tests/interface/test_ocupacao.py` — dois dos três casos do `apuravel`

| # | Caso | O que afirma hoje |
|---|---|---|
| 6 | `test_recorte_reservado_em_marco_computado_nao_oferece_apuracao` | `"Pretos, pardos e indígenas" in pagina`; `pagina.count("Apurar a ocupação deste recorte") == 1` |
| 7 | `test_no_lugar_da_apuracao_a_tela_nomeia_a_causa_e_nao_o_sintoma` | `"lista única" in pagina`; `"fora do sistema" in pagina` |

**O terceiro NÃO muda** — `test_o_recorte_da_ampla_continua_apuravel`, com
`"Ampla concorrência (linha geral do quadro)" in pagina` e `"A ocupar" in pagina`. É a
não-regressão.

**E os três vizinhos, de 472 a 500, são da família do corte (`FR-463`) e NÃO mudam**:
`test_sem_regra_de_corte_a_faixa_seguinte_nao_e_oferecida`,
`test_no_lugar_da_faixa_a_tela_diz_por_que_a_acao_nao_existe_ali`,
`test_com_regra_de_corte_a_faixa_continua_sendo_oferecida`. Estão nomeados porque a semelhança
convida ao erro.

### `tests/interface/test_hardening_pos_auditoria.py` — um caso

| # | Caso | O que afirma hoje |
|---|---|---|
| 8 | `test_os_dois_avisos_da_familia_nao_impedem_a_publicacao` | quatro asserções de severidade, entre elas `achados["reserved_row_without_ordering"] == Severity.WARNING`. O dicionário `A_FAMILIA` mapeia `"reserved_row_without_ordering": ("perfis", "COM-COTA")`, e o caso vizinho `test_…` que o lê também percorre `A_FAMILIA` |

### E a prosa que muda sem ser caso

`tests/integration/ocupacao/test_reversao.py` — o docstring do módulo e o de `apuracao_da_cota`
afirmam, hoje:

> *"`emitir_ordem` fixa `lista_id=None` por decisão declarada (PR #85) … Logo **reversão de cota só
> é apurável em certame de sorteio**."*
>
> *"O caminho do ator não a alcança em certame computado, porque não existe ordem com `lista_id`."*

**O helper não é apagado**: ele é chamado por seis casos de reversão, e trocá-lo mudaria o que eles
exercitam. O que muda é a frase, que deixou de ser verdade.

---

## 3. O retrato do acervo

Exportado de `ps_034_recorte` depois de `make seed`, por leitura pura — nada foi escrito.

| | Antes |
|---|---|
| `schemaVersion` canônica | **16** |
| Publicações | **7** |
| Documentos publicados | **7** |
| Versões consolidadas | **7** |

**Censo dos degraus de elevação** — é o guarda contra o degrau acrescentado por engano, que
reescreveria de uma vez o conteúdo de toda versão consolidada do acervo:

| Família | Degraus |
|---|---|
| `DEGRAUS` | 2 |
| `DEGRAUS_DA_RAIZ` | 3 |
| `DEGRAUS_DE_DOCUMENTO` | 1 |
| `DEGRAUS_DE_EVENTO` | 1 |
| `DEGRAUS_DE_MARCO` | 3 |
| `DEGRAUS_DE_PERFIL` | 5 |
| **Total** | **15** |

Os resumos por publicação — `content_hash`, o SHA-256 do canônico, o `document_hash` e o SHA-256 dos
bytes de cada documento, e o `content_hash` de cada versão consolidada — estão em
[retrato-do-acervo-antes.json](retrato-do-acervo-antes.json), ao lado deste arquivo. É esse arquivo
que a `T043` compara, e não esta tabela: a tabela conta, e o JSON identifica.

---

## 4. A conferência da entrega — `T045`

Feita em 18/09/2026, **depois de todos os percursos** — e o percurso achou defeito, mudou o estado, e
por isso esta seção só pôde ser escrita no fim.

**Caso a caso, contra a lista do item 2 — e nunca pela contagem.**

| # | Caso do "antes" | O que aconteceu | Confere? |
|---|---|---|---|
| 1 | `…reserva_em_marco_que_nao_sorteia_produz_aviso_e_nao_impedimento` | virou `…nao_produz_mais_aviso`: as três asserções (`len == 1`, severidade, `path`) deram lugar a `== []` | **sim** — a troca é de sentido, e é a que a `FR-501` manda |
| 2 | `…o_aviso_da_reserva_nomeia_a_causa_e_nao_o_sintoma` | virou `test_nenhum_achado_da_familia_sobra_sobre_o_quadro_com_reserva`: as seis asserções sobre a mensagem saíram, e entrou uma sobre o `path` do quadro | **sim** — a mensagem não existe; o que restou a prender é que as regras vizinhas do mesmo `vacancyTable` **não** saíram junto |
| 3 | `…o_aviso_da_reserva_nao_e_emitido_na_retificacao` | virou `test_a_aposentadoria_alcanca_tambem_a_retificacao`: **a asserção é literalmente a mesma** | **sim** — e a mudança é só de razão: era exceção, virou regra geral |
| 4 | `…o_aviso_alcanca_o_segundo_marco_quando_o_primeiro_sorteia` | virou `test_o_segundo_marco_computado_tambem_deixou_de_receber_o_aviso`: `"COMPUTA" in message` e `"SORT-X" not in message` deram lugar a `== []` | **sim** — o conteúdo do cenário ficou intacto, e é ele que pega a regra futura que leia só o primeiro marco |
| 5 | `…dois_marcos_em_lista_unica_saem_num_achado_so_que_nomeia_os_dois` | virou `test_dois_marcos_computados_no_mesmo_perfil_nao_produzem_aviso_algum`: a asserção da agregação saiu | **sim** — não há o que agregar |
| 6 | `…recorte_reservado_em_marco_computado_nao_oferece_apuracao` | virou `…agora_oferece_apuracao`: `count(...) == 1` → `== 2` | **sim, e é o caso que mais pedia leitura**: o número mudou de 1 para 2, e o que mudou de verdade foi o sentido |
| 7 | `…no_lugar_da_apuracao_a_tela_nomeia_a_causa_e_nao_o_sintoma` | virou `test_a_frase_do_fora_do_sistema_saiu_da_tela`: dois `in` viraram três `not in` | **sim** |
| 8 | `…os_dois_avisos_da_familia_nao_impedem_a_publicacao` | virou `test_o_aviso_que_resta_na_familia_nao_impede_a_publicacao`: a asserção de severidade do aviso virou asserção de ausência; **os dois impedimentos ficaram intactos** | **sim** — e a permanência dos dois impedimentos é o que impede a aposentadoria de virar afrouxamento |

**Os cinco que deviam permanecer permaneceram**, literalmente:
`…perfil_cujo_marco_sorteia_nao_recebe_achado`,
`…a_modalidade_declarada_como_ampla_nao_e_lida_como_reserva`,
`…linha_reservada_zerada_nao_produz_aviso`,
`…perfil_sem_marco_algum_nao_acumula_o_aviso_da_reserva`,
`…todos_os_marcos_sorteando_continua_sem_achado`. Nenhuma linha deles foi tocada.

**Os três vizinhos da família do corte também**, em `test_ocupacao.py`
(`…sem_regra_de_corte_a_faixa_seguinte_nao_e_oferecida`,
`…no_lugar_da_faixa_a_tela_diz_por_que_a_acao_nao_existe_ali`,
`…com_regra_de_corte_a_faixa_continua_sendo_oferecida`), e o
`…o_recorte_da_ampla_continua_apuravel`, que é a não-regressão.

### Quatro casos que o "antes" não previa, e a conferência encontrou

| Caso | O que mudou | Por quê |
|---|---|---|
| `test_hardening…::test_a_familia_inteira_dispara_no_mesmo_edital` | nenhuma linha própria — mudou `A_FAMILIA`, que ele compara por igualdade | **foi ele que acusou a aposentadoria**, e é o comportamento desejado da varredura |
| `test_hardening…::test_cada_achado_da_familia_leva_a_etapa_em_que_a_correcao_e_feita` | idem | sem a remoção da entrada, quebraria com `KeyError` |
| `test_hardening…::test_a_revisao_apresenta_os_quatro_e_nao_o_primeiro` | nome e docstring | **não falhou** — `COM-COTA` seguia no corpo por outro achado. A asserção passou a valer por acidente, e o nome mentia |
| `test_limites_da_classificacao.py::test_a_classificacao_nao_cria_corte_vaga_nem_rota_para_candidato` | a busca por substring virou busca com fronteira de palavra | `recorte` contém `corte`. Veio acompanhada de um caso que prova que o termo proibido continua sendo acusado |

**Total conferido: 12 casos alterados**, e não os oito que o `research.md` previa. A causa dos quatro
a mais está na [rastreabilidade](rastreabilidade.md), seção *Por que doze, e não oito*.

### A contagem, e o que ela não prova

| | Antes | Depois |
|---|---|---|
| passando | 7213 | **7284** |
| pulados | 12 | **11** |
| coletados | 7225 | **7295** |

**A contagem não prova nada sozinha, e é por isso que ela vem depois da tabela.** O que prova é a
comparação por identificador: nove identificadores sumiram, e os nove têm substituto nomeado acima.
