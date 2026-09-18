# Rastreabilidade — 032 · Executabilidade antes de publicar

Uma linha por `FR-` e por `SC-`: **onde foi feito** e **onde é verificado**. É o Princípio V, e
requisito sem linha aqui é requisito que ninguém sabe se entrou.

Caminhos relativos a `backend/`.

---

## A contagem da suíte

| Momento | Passando | Pulados | Falhando |
|---|---|---|---|
| Partida, antes de qualquer mudança (T002) | 6880 | 12 | 0 |
| Depois de US1 | 6905 | 11 | 0 |
| Depois de US2 | 6933 | 11 | 0 |
| Final (T040) | **6947** | **11** | **0** |
| Depois de integrar a `main` com a `031` | **7158** | **12** | **0** |
| Depois das duas correções da revisão | **7165** | **12** | **0** |

`make lint check test-pg` limpo: `ruff check`, `ruff format --check`, `manage.py check`,
`makemigrations --check` (**nenhuma migration**, que é o que a `data-model.md` promete) e a suíte.

**A `main` andou no meio da feature**, e a 031 entrou com 211 testes novos. Nenhum deles é alcançado
pela `FR-457`: as fixtures que ela trouxe já declaram marco. O pulado que volta é da 031, e não
desta feature.

**Um pulado a menos, e é melhoria.** `tests/test_vocabulario_da_composicao.py` pula o caso em que a
tela não usa o termo. As frases novas passaram a usar **geração** em duas telas que não a usavam, e
lá ela agora é definida no primeiro uso — dois casos que eram pulados passaram a rodar.

---

## Requisitos funcionais

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-457** Perfil sem marco impede a publicação | `editais/domain/validation.py::_perfil_sem_marco` | `tests/unit/editais/test_executabilidade.py::test_perfil_sem_marco_impede_a_publicacao` · `tests/interface/test_hardening_pos_auditoria.py::test_a_submissao_e_recusada_com_a_mesma_frase_da_revisao` |
| **FR-458** todo achado nomeia entidade, falta e etapa | as quatro mensagens, e o `path` de cada uma | `test_executabilidade.py::test_a_recusa_do_perfil_sem_marco_nomeia_o_perfil_a_falta_e_a_etapa` · `test_hardening_pos_auditoria.py::test_cada_achado_da_familia_leva_a_etapa_em_que_a_correcao_e_feita` |
| **FR-459** impeditivo só no ato de publicação | `if ato != ATO_DE_PUBLICACAO: return []`, primeira linha das quatro | `tests/interface/test_round_trip_do_rascunho.py::test_gravar_rascunho_inexecutavel_continua_sendo_aceito` · os quatro casos `..._na_retificacao` de `test_executabilidade.py` |
| **FR-460** a Retificação do acervo continua aceita | o mesmo recorte por ato | `tests/integration/editais/test_acervo_inexecutavel_continua_retificavel.py` (3 casos) |
| **FR-461** aviso do marco sem regra de corte | `validation.py::_marco_sem_regra_de_corte` | `test_executabilidade.py::test_marco_sem_regra_de_corte_e_aviso_e_nao_impedimento` · `::test_o_aviso_do_corte_nomeia_a_cadeia_inteira_ate_a_convocacao` · `::test_a_regra_que_declara_nao_governar_etapa_nao_recebe_aviso` |
| **FR-462** a consequência dita na composição | `interface/templates/interface/_marco.html` (`ajuda-corte-…`) e `_como_preencher_o_marco.html` | `tests/interface/test_metodo_do_marco.py::test_o_cartao_do_marco_declara_que_sem_corte_nao_ha_convocacao` · `::test_a_explicacao_longa_do_corte_fica_no_como_preencher_e_nao_no_cartao` |
| **FR-463** a faixa seguinte não é oferecida sem corte | `ocupacao/application/selectors.py` (`faixaDisponivel`) e `ocupacao.html` | `tests/interface/test_ocupacao.py::test_sem_regra_de_corte_a_faixa_seguinte_nao_e_oferecida` · `::test_no_lugar_da_faixa_a_tela_diz_por_que_a_acao_nao_existe_ali` · `::test_com_regra_de_corte_a_faixa_continua_sendo_oferecida` |
| **FR-464** o documento diz como a ordem nasce | `publicacoes/infrastructure/pdf.py::_marcos` (par `Ordem`, `FORMA_DA_ORDEM`) | `tests/unit/publicacoes/test_pdf_classificacao.py::test_o_marco_declara_como_a_ordem_dele_e_produzida` · `::test_o_marco_do_acervo_sem_forma_declarada_sai_exatamente_como_hoje` |
| **FR-465** os sete dados do método no documento | `pdf.py::_metodo_do_marco` + `CAMPOS_DO_METODO` | `test_pdf_classificacao.py::test_o_documento_imprime_os_sete_dados_do_metodo` (7 casos) · `::test_os_rotulos_do_metodo_saem_do_vocabulario_do_dominio` |
| **FR-466** próprio, comum, e a divergência nomeada | `pdf.py::_origem_do_metodo` + `::_publica_a_mesma_norma` | `test_pdf_classificacao.py::test_o_documento_diz_qual_metodo_governa_o_marco` (3 casos) · `::test_o_metodo_do_marco_igual_ao_comum_nao_e_anunciado_como_divergente` · `::test_a_divergencia_real_continua_sendo_nomeada` · `::test_a_etapa_de_habilitacao_declarada_nao_cria_divergencia_sozinha` |
| **FR-467** sorteio sem método não publica | `validation.py::_metodo_do_sorteio_publicavel` | `test_executabilidade.py::test_marco_que_sorteia_sem_metodo_impede_a_publicacao` · `::test_o_metodo_comum_do_edital_satisfaz_o_marco_que_o_referencia` · `::test_metodo_pela_metade_continua_sendo_o_achado_antigo_e_nao_este` |
| **FR-468** marco de sorteio não imprime combinação | `pdf.py::_marcos`, condicionado por `orderProduction` | `test_pdf_classificacao.py::test_o_marco_que_sorteia_nao_imprime_combinacao_de_pontuacoes` · `tests/integration/publicacoes/test_sorteio_no_documento.py::test_o_documento_do_sorteio_nao_afirma_combinacao_de_pontuacoes` |
| **FR-469** o documento do acervo não muda | **nada** — é conferência | `tests/integration/publicacoes/test_elevacao_de_versao.py::test_a_032_nao_acrescenta_degrau_de_elevacao` · `::test_o_acervo_atravessa_a_032_sem_mudar_conteudo_nem_resumo` · cenário 4 do quickstart (abaixo) |
| **FR-470** aviso da reserva sem via de apuração | `validation.py::_reserva_sem_via_de_apuracao` + `marcos.emite_ordem_no_recorte` | `test_executabilidade.py::test_reserva_em_marco_que_nao_sorteia_produz_aviso_e_nao_impedimento` · `::test_perfil_cujo_marco_sorteia_nao_recebe_achado` · `::test_a_modalidade_declarada_como_ampla_nao_e_lida_como_reserva` · `::test_o_aviso_alcanca_o_segundo_marco_quando_o_primeiro_sorteia` · `::test_todos_os_marcos_sorteando_continua_sem_achado` |
| **FR-471** a mensagem nomeia a causa, não o sintoma | a mensagem de `reserved_row_without_ordering` | `test_executabilidade.py::test_o_aviso_da_reserva_nomeia_a_causa_e_nao_o_sintoma` · `tests/interface/test_ocupacao.py::test_no_lugar_da_apuracao_a_tela_nomeia_a_causa_e_nao_o_sintoma` |
| **FR-472** a apuração não é oferecida no recorte não emitido | `selectors.py` (`apuravel`) e `ocupacao.html` | `test_ocupacao.py::test_recorte_reservado_em_marco_computado_nao_oferece_apuracao` · `::test_o_recorte_da_ampla_continua_apuravel` |

**`FR-469` não tem linha de implementação, e é deliberado.** Documento publicado não se regenera —
ele é composto no ato da publicação e guardado. O risco que a `FR-469` cobre não é o renderizador:
é um **degrau de elevação acrescentado por engano**, que reescreveria o conteúdo de toda versão
consolidada do acervo de uma vez. O censo literal dos degraus é o guarda.

---

## Critérios de sucesso

| Critério | Onde é verificado |
|---|---|
| **SC-157** nenhum dos Editais da auditoria chega à submissão sem que a Revisão nomeie | `test_hardening_pos_auditoria.py::test_a_familia_inteira_dispara_no_mesmo_edital` · `::test_a_revisao_apresenta_os_quatro_e_nao_o_primeiro` · cenários 1 e 3 do quickstart |
| **SC-158** o documento basta para conferir o sorteio | `tests/integration/publicacoes/test_sorteio_no_documento.py` (6 casos) · cenário 2 do quickstart |
| **SC-159** 100% dos achados citam a etapa da correção | `test_hardening_pos_auditoria.py::test_cada_achado_da_familia_leva_a_etapa_em_que_a_correcao_e_feita` |
| **SC-160** gravar rascunho incompleto continua possível | `test_round_trip_do_rascunho.py::test_gravar_rascunho_inexecutavel_continua_sendo_aceito` · contraprova do cenário 1 |
| **SC-161** o acervo não muda de conteúdo nem de resumo | `test_elevacao_de_versao.py` (2 casos) · cenário 4 do quickstart |
| **SC-162** a consequência do corte é lida na etapa em que se decide | `test_metodo_do_marco.py` (2 casos) · cenário 3 do quickstart |
| **SC-163** nenhuma tela oferece ação que sempre falha | `test_ocupacao.py` (5 casos) |

---

## O quickstart, percorrido (T038, T039)

Pela interface administrativa, em `http://localhost:8032` sobre o banco desta worktree, em
18/09/2026. Os três primeiros sem shell e sem banco, que é o que o Princípio VI cobra.

| Cenário | O que se observou |
|---|---|
| **1** · o Edital que não classifica ninguém | A Revisão respondeu **IMPEDE**, nomeando `DOC-INFO`, a falta e a etapa, com *Ir para Classificação*. A submissão foi recusada com a **mesma frase**, e a tela nem ofereceu confirmar. **Contraprova**: com o Perfil ainda sem marco, "Rascunho salvo — Perfis de Vaga." |
| **2** · o sorteio que o documento não contava | Edital 04/2026 publicado pelo caminho real. O documento imprime `Ordem: por sorteio`, o bloco `Sorteio` com os sete campos e `Método: comum a este Edital`. **`Combinação` e `Normalização` desapareceram** — eram elas que afirmavam "soma ponderada" sob uma ordem que não vem de nota. **A recusa**: o mesmo marco sem método algum produziu IMPEDE nomeando o marco. |
| **3** · a cota e o corte que ninguém avisou | O cartão do marco com o corte em branco declara *"não há faixa, de modo que este marco classifica e não convoca"*. Na Revisão, os **dois avisos** e **nenhum impedimento**. **Contraprova do 69/2026**: declarada a regra que não governa Etapa alguma, o aviso do corte **desapareceu**. **Contraprova da grafia-armadilha**: a Modalidade "AC", apontada como a da ampla, **não entrou** no aviso da reserva. |
| **4** · o acervo não se mexeu | `/tmp/032-acervo-antes.json` e `/tmp/032-acervo-depois.json` **idênticos**: `schemaVersion` 16, 7 publicações, 7 versões consolidadas e 7 documentos, cada um com o mesmo `content_hash`, o mesmo resumo do conteúdo canônico e os mesmos bytes de documento. |

---

## A varredura contra a amostra real (T041)

Os quatro Editais da auditoria não são a amostra: são os que ela **montou**. A amostra real está em
[doc/avaliacao-de-capacidade-editais-2026-09-12.md](../../doc/avaliacao-de-capacidade-editais-2026-09-12.md),
com doze Editais. A varredura abaixo é manual, Edital a Edital, e existe porque **checklist,
`analyze` e o teste de citações ficam verdes com regras que se contradizem**.

| Edital | Marco | Corte | Sorteio | Reserva | O que dispararia |
|---|---|---|---|---|---|
| **58/2026** 3 cursos FIC | um marco, 3 códigos | alvo derivado + 30 | sim, método declarado | sem cota | **nada** |
| **59/2026** Libras A1 | um marco, 2 turmas | alvo derivado + 30 | sim | sem cota | **nada** |
| **69/2026** Multimeios | um marco | declara **não governar Etapa alguma** | sim | sem cota | **nada** — e é a contraprova de `FR-461` |
| **77/2026** FIC Acessibilização | um marco | alvo derivado + 30 | sim | sem cota | **nada** |
| **78/2026** Libras A1 remanescentes | um marco, 2 turmas | alvo derivado + 30 | sim | sem cota | **nada** |
| **158/2024** FIC Educação Especial | um marco | alvo derivado, excedente 0 | sim | sem cota, **sem quadro** | **nada** da família nova; o quadro ausente é da `027` |
| **57/2026** unificado, 2 cursos | três listas, três atos raiz | alvo derivado + 20 | **não** — computado | **sim** | **`reserved_row_without_ordering`** (aviso) |
| **28/2026** Informática na Educação | 7 polos × 3 modalidades | alvo derivado + 15 | **não** | **sim** | **`reserved_row_without_ordering`** (aviso) |
| **173/2025** Designer Educacional | computado, CR puro | **n/a** — sem Etapa após a ordem | **não** | **sim** | **`reserved_row_without_ordering`** (aviso), e `milestone_without_cut_rule` **se** não declarar a regra |
| **14/2026** Orientador de TFC | um marco por código | alvo fixo, 10 | **não** | sem cota | **nada** |
| **76/2026** Secretaria Escolar | bloqueado pela `P-8` antes disto | — | — | — | **nada** que a `P-8` já não impeça |
| 46/2026 | fora do alvo por decisão | | | | — |

**O que a varredura confirma, e é o ponto dela:**

1. **Nenhum impedimento novo alcança a amostra real.** Os dois achados impeditivos — `FR-457` e
   `FR-467` — não disparam em Edital nenhum dos doze. Isso é o esperado: todos declaram marco, e
   todos os que sorteiam publicam o método.
2. **Os três avisos de reserva são exatamente os três que a `spec.md` nomeia** — 57/2026, 28/2026 e
   173/2025 —, e são a razão registrada de o `FR-470` ser aviso e não impedimento. A varredura
   confirma a medição que sustentou a decisão, em vez de a repetir de memória.
3. **O 69/2026 sai limpo**, e era o risco nomeado na tabela de riscos do plano: *"o aviso do corte
   vira ruído — sinal de que aconteceu: dispara no 69/2026"*. Não dispara, porque a regra dele
   **existe** e declara não governar Etapa alguma.
4. **O 173/2025 é o único com uma dúvida aberta**, e ela é de leitura do Edital, não da regra: o
   documento declara "ordem por lista — decisão declarada" e não há Etapa após a ordem. Se o
   conteúdo publicado dele tiver `cutRule` nula, ele recebe também o aviso de `FR-461` — o que
   estaria **certo**, porque um CR puro sem regra de corte de fato não convoca por faixa. Registrado
   como leitura a conferir contra o PDF, e não como defeito.

---

## O que a implementação mudou nos artefatos (T037)

Quatro divergências entre contrato e código. Nas quatro o **código está certo** e o artefato foi
corrigido; as razões estão escritas no ponto de uso de cada contrato.

| O que mudou | Onde | Por quê |
|---|---|---|
| `CAMPOS_DO_METODO` passou a trinca `(campo, o_que_é, rótulo)` | `contracts/marco-no-documento.md` · `editais/domain/perfis.py` | O contrato se contradizia: mostrava rótulos curtos e dizia que eles saíam da constante, cujas entradas são frases de sessenta caracteres. A trinca torna a frase literalmente verdadeira sem desmontar o bloco de pares |
| A ocorrência e o instante saem em **dois** pares | `contracts/marco-no-documento.md` | O exemplo os fundia; a `FR-465` os lista separados, e separados nenhum dos sete rótulos fica sem uso |
| A divergência do método é nomeada **quando existe** | `contracts/marco-no-documento.md` | A `FR-466` diz "método próprio **divergente** do comum". Próprio idêntico ao comum não diverge, e dizer que diverge afirmaria uma diferença que ninguém publicou |
| O Perfil é nomeado pelo `code`, e não pelo `name` | `contracts/achados-de-executabilidade.md` | Os três achados do quadro que já existem escrevem o código, e os quatro aparecem juntos na Revisão: `DOC-INFO` numa linha com `Professor de Informática` na seguinte pareceriam dois Perfis |

**E uma decisão de desenho que nenhum contrato previa:** a razão que a tela de Ocupação escreve
**para na apuração**, enquanto o aviso da Revisão diz "a ocupação e a convocação". A fronteira com a
`019` é guardada por varredura — a `016` conta vaga e não sabe quem foi chamado —, e atravessá-la
faria a tela afirmar um fato que ela não tem.

---

## O custo que a `FR-457` cobrou da suíte

Vale registrar, porque foi o maior trabalho da feature e porque a próxima regra desta família vai
cobrar o mesmo.

A `FR-457` quebrou **1892 testes** ao ser ligada. A causa foi **uma só**: quatro fixtures de
rascunho (`edital`, `selecao`, `snapshot`, `supervisao`), o `seed_demo` e o percurso do assistente
publicavam Perfis **sem marco algum** — o mesmo defeito que a auditoria encontrou em Edital real.
Uma demonstração que reproduz o defeito ensina o defeito.

| Passo | Quebrados |
|---|---|
| Regra ligada, fixtures intactas | 1892 |
| `complete_draft` ganha marco | 858 |
| `selecao`, `snapshot`, identidades derivadas de `uuid5` | 72 |
| `supervisao`, `seed_demo`, percurso do assistente, três asserções de conteúdo | 3 |
| Vocabulário: `geração` definida onde passou a ser usada | 0 |

**A armadilha que custou duas rodadas**: identificador literal para o marco colide.
`identificador(450, seed)` esbarrou em outra coleção deslocada pelo `seed`, e copiar o Perfil-modelo
três vezes copiava a identidade do marco junto. A identidade passou a sair de
`tests/fixtures/edital.py::identidade_do_marco`, derivada do Perfil por `uuid5` — o mesmo recurso
que a `027` usa para a linha geral do quadro.

---

## O que a revisão encontrou, e o que ele muda

Dois defeitos, os dois reproduzidos antes de corrigir, e os dois na mesma família: **uma afirmação
que o artefato não sustenta**.

### O documento anunciava uma divergência que não existia

`_origem_do_metodo` comparava os dois métodos por igualdade bruta de dicionário. Mas o método do
**marco** carrega `qualifyingStageId` — a Etapa que habilita a participar do sorteio, que é do
marco porque depende de quais Etapas ele enumera — e o método **comum** nunca a carrega:
`metodo_comum_do_formulario` a remove de propósito. O formulário a grava como `None` quando ninguém
a declara, e a comparação achava diferença entre dois métodos campo a campo idênticos. O documento
publicado — normativo e imutável — dizia *"diverge do comum deste Edital"* sobre um marco que
publica exatamente o método comum.

**A ironia é o ponto**: essa comparação foi acrescentada nesta feature justamente para o documento
não afirmar uma divergência inexistente, e era ela que a afirmava, no caminho mais comum.

A correção **não** foi normalizar nulos. A comparação passou a ser **pelo valor impresso dos sete
campos** (`_publica_a_mesma_norma`), o que amarra a afirmação ao artefato: o documento não diz que
diverge aquilo que ele mesmo mostra igual. Isso também resolve o caso que a normalização de nulos
deixaria em aberto — um marco que **declara** uma Etapa de habilitação está especificando o que o
comum não tem como dizer, e não o contrariando.

### A validação parava no primeiro marco

`_reserva_sem_via_de_apuracao` lia `marcos_do_perfil[0]` e nada mais. Num Perfil cujo primeiro marco
sorteia e cujo segundo computa, **nenhum aviso era emitido** — e é no segundo que a tela de Ocupação
mostra os recortes reservados sem ordem a apurar.

É a mesma divergência que `emite_ordem_no_recorte` existe para fechar, entrando por outra porta:
não por haver dois predicados, mas por um deles ser perguntado sobre **menos marcos** que o outro.
A tela de Ocupação é por marco; a validação precisava ser também. Agora percorre todos e emite **um
achado por Perfil** nomeando os marcos que produzem lista única — um por marco encheria a Revisão de
linhas que só diferem no código.

### E o que ele diz sobre os testes que eu tinha escrito

Os casos de divergência montavam os dois dicionários **à mão, com a mesma forma**, e por isso a
igualdade bruta os satisfazia. Os testes novos pedem os métodos a `interface/forms.py`, a partir do
mesmo formulário, e um deles prende a premissa por escrito
(`test_a_tela_produz_um_proprio_que_difere_do_comum_por_uma_chave_nula`): o dia em que o formulário
mudar dá **falha**, e não silêncio.
