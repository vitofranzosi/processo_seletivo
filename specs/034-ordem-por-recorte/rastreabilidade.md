# Rastreabilidade — `034` · Ordem por recorte em marco computado

Uma linha por `FR-`, uma por `SC-`, **e uma por teste alterado, com o motivo**. A última é a que
separa fechar o `ACH-47` de afrouxar a ordem: um teste pode manter o número de asserções e trocar o
que afirma, e a suíte fica verde do mesmo jeito.

---

## Requisitos funcionais

| Requisito | Onde foi implementado | Onde está prendido |
|---|---|---|
| **FR-490** — uma ordem por recorte | `classificacao/application/emissao.py` — o filtro do vigente e o `create` passaram a receber o recorte; `calculo.py` filtra o universo | `test_ordem_por_recorte.py::test_a_ordem_do_recorte_reservado_nasce_com_a_lista_daquele_recorte`, `::test_cada_recorte_tem_uma_raiz_e_as_tres_convivem`; percurso, cenário 1 |
| **FR-491** — derivação única | `editais/domain/recortes.py` (**novo**), consumido por `ocupacao/application/selectors.py` e pela classificação | `test_recortes_do_marco.py::test_a_classificacao_e_a_ocupacao_derivam_a_mesma_lista` |
| **FR-491a** — a divergência do sorteio é registrada, não corrigida | nada em código: registro em [inventario-dos-recortes.md](inventario-dos-recortes.md) | a ausência de mudança em `sorteios/` é o próprio cumprimento; `git diff --stat` não toca o módulo |
| **FR-492** — universo do recorte, e o autodeclarado fica nas duas listas | `calculo.py`, o `filter(modality_id=...)` que só o recorte reservado aplica | `test_universo_do_recorte.py`, seis casos |
| **FR-492a** — ordem vazia emitível, nunca automática | `emissao.py` (nenhuma guarda de universo vazio) e `ordenacao.html` (a frase "Ninguém concorreu por este recorte") | `test_ordem_por_recorte.py::test_recorte_sem_autodeclarado_admite_ordem_vazia_emitida`, `::test_a_ordem_vazia_nunca_e_automatica`; `test_navegacao_entre_recortes.py::test_o_recorte_sem_autodeclarado_diz_que_ninguem_concorreu`; **percurso, cenário 5.1 — Edital 35/2026** |
| **FR-493** — a ampla não muda | `calculo.py`: o filtro só existe quando há recorte; o padrão é o de antes | `test_ordem_sem_reserva_nao_muda.py`, quatro casos; percurso, contraprova do cenário 1 |
| **FR-494** — emitir num recorte não constitui ato sobre os outros | o `lista_id` no filtro do vigente e as duas `UniqueConstraint` da `021` | `test_ordem_por_recorte.py::test_emitir_no_recorte_reservado_nao_toca_a_ordem_da_ampla`, `::test_suceder_num_recorte_nao_obsoleta_os_outros`, `::test_a_mesma_chave_de_idempotencia_nao_serve_a_dois_recortes` |
| **FR-494a** — Modalidade acrescentada depois não obsoleta a ampla | consequência da cadeia por recorte; nenhuma linha própria | `test_ordem_por_recorte.py::test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla`; **percurso, cenário 5.2 na metade que a interface alcança** — ver abaixo |
| **FR-495** — confirmação do recorte | `assinatura_da_proposta` passou a incluir `"recorte"` | `test_ordem_por_recorte.py::test_confirmar_num_recorte_e_emitir_no_outro_e_recusado`, `::test_dois_recortes_vazios_do_mesmo_marco_nao_compartilham_confirmacao` |
| **FR-496** — abrir a tela não constitui ato | `calcular_ordem` continua fora do comando transacional | `test_ordem_por_recorte.py::test_ler_os_tres_recortes_repetidamente_nao_constitui_ato`, `::test_a_leitura_do_recorte_sem_ordem_nao_cria_ato_vazio` |
| **FR-497** — as telas nomeiam o recorte e oferecem os outros | `interface/views.py::_recortes_navegaveis` e `::_navegacao_do_recorte`; `ordenacao.html` e `corte.html` | `test_navegacao_entre_recortes.py`, seis casos — entre eles `::test_as_duas_telas_nomeiam_o_recorte_em_que_se_esta` |
| **FR-498** — recorte sem ordem diz o que falta e onde se faz | `ordenacao.html` (três ausências distintas) e `classificacao/application/corte.py` (a recusa reescrita) + `corte.html` (o caminho) | `test_navegacao_entre_recortes.py::test_o_recorte_sem_ordem_diz_o_que_falta_e_onde_se_faz`, `::test_o_corte_do_recorte_sem_ordem_leva_a_classificacao_dele` |
| **FR-499** — recorte inexistente é objeto inexistente | `recortes.py::normalizar_recorte` e `views.py::_recorte_pedido` | `test_recortes_do_marco.py::test_recorte_que_nao_e_modalidade_do_perfil_e_objeto_inexistente`; `test_navegacao_entre_recortes.py::test_recorte_que_nao_e_modalidade_do_perfil_responde_404` |
| **FR-500** — o predicado da `032` é espelho da fonte **enquanto existir** | `marcos.py::emite_ordem_no_recorte` passou a `return True` (`T033`) | o teste de igualdade viveu entre `T033` e `T036`, e saiu com o predicado; o registro está em `test_forma_da_ordem.py`, ao fim |
| **FR-501** — o aviso é aposentado | `editais/domain/validation.py`: `_reserva_sem_via_de_apuracao` e a chamada dela foram removidas | os cinco casos de `test_executabilidade.py` que afirmavam o aviso; varredura: zero ocorrências do código em `processo_seletivo/` |
| **FR-501a** — o predicado que deixa de variar é removido | `marcos.py` (função removida), `ocupacao/application/selectors.py` (campo `apuravel` removido) | a medição que autorizou está em `test_forma_da_ordem.py`; `grep` por `apuravel` em `processo_seletivo/` devolve só o comentário que explica a ausência |
| **FR-502** — a apuração volta a ser oferecida, sem instante em que deixe de sê-lo | `ocupacao.html`: a frase e as duas ramificações saíram **antes** de o campo ser removido | `test_ocupacao.py::test_recorte_reservado_em_marco_computado_agora_oferece_apuracao`, `::test_a_frase_do_fora_do_sistema_saiu_da_tela`; percurso, cenário 2 |
| **FR-503** — a ampla continua sendo o recorte sem lista | `recortes.py`, a exclusão da Modalidade declarada como ampla | `test_recortes_do_marco.py::test_a_modalidade_declarada_como_ampla_nao_produz_recorte`, `::test_pedir_a_modalidade_declarada_como_ampla_devolve_a_ampla`; `test_universo_do_recorte.py::test_a_modalidade_declarada_como_ampla_nao_e_recorte_e_cai_na_ampla` |
| **FR-504** — nada do acervo é reescrito, e a tela diz o que a ordem única é | nenhuma reescrita; `ordenacao.html` explica a ordem única do marco | `test_navegacao_entre_recortes.py::test_o_recorte_sem_ordem_explica_a_ordem_unica_que_o_marco_tem`, `::test_a_tela_nao_oferece_corrigir_a_ordem_unica`; percurso, cenário 4 |
| **FR-505** — nenhuma capacidade, papel, regra de autorização ou migration nova | — | **três conferidas por leitura do diff, abaixo**; a quarta é o `make check` |
| **FR-506** — o documento nomeia o recorte | `divulgacao/infrastructure/documento.py::_identificacao` | `test_documento.py`, três casos; percurso: o PDF do resultado divulgado imprime `LISTA DE CONCORRÊNCIA · Ampla concorrência` |

### A `FR-505`, conferida por leitura do diff

As três proibições que nenhum comando prova, varridas sobre `git diff backend/`:

| Proibição | Como foi conferida | Resultado |
|---|---|---|
| nenhuma **capacidade nova** | varredura das linhas acrescentadas por `can(`, `require_permission`, `permission`, `:consultar`, `:gerir`, `:publicar`, `:elaborar` | **zero** ocorrências |
| nenhum **papel novo** | varredura por `Funcao.`, `PAPEIS`, `role` | **zero** — as três linhas que casam com "papel" são a palavra em prosa (`role="status"`, *"o papel dos dois recortes"*, *"a não-regressão do papel"*) |
| nenhuma **regra de autorização nova** | varredura por `require_authorization_base`, `pode_gerir_comissao`, `BASES_` | **zero** ocorrências |

A quarta — **nenhuma migration** — é a `SC-175`, e quem a prova é `manage.py makemigrations --check
--dry-run`, cujo resultado está ao fim deste arquivo.

---

## Critérios de sucesso

| Critério | Como foi verificado | Resultado |
|---|---|---|
| **SC-169** — o Edital 7/1/2 vai da classificação à convocação pelos três recortes | percurso pela interface administrativa, cenários 1 e 2 do `quickstart`, sem shell e sem banco | **cumprido, com uma ressalva registrada abaixo** |
| **SC-170** — zero ações oferecidas que sempre falham | percurso: os três botões "Apurar a ocupação deste recorte" foram clicados, e os três concluíram | **cumprido** |
| **SC-171** — Edital sem reserva produz ordem idêntica | `test_ordem_sem_reserva_nao_muda.py`, por comparação de ordem e proveniência (e não de contagem) | **cumprido** |
| **SC-172** — 100% dos recortes coincidem entre classificação e ocupação | `test_recortes_do_marco.py`, igualdade das duas listas | **cumprido** |
| **SC-173** — o acervo atravessa sem mudar conteúdo, resumo nem documento | retrato exportado antes da primeira edição (`T002`) e de novo ao fim (`T043`) | **cumprido — os dois retratos são idênticos**, campo a campo: 7 publicações, 7 documentos, 7 versões consolidadas, `schemaVersion` 16, 15 degraus de elevação |
| **SC-174** — nenhum aviso da família dispara sobre recorte que ganhou via | [varredura-da-amostra.md](varredura-da-amostra.md) | **cumprido** |
| **SC-175** — nenhuma migration | `make check` | **cumprido** |

### O cenário 5, percorrido — e a metade que a interface não alcança

**5.1 — o recorte em que ninguém concorreu: percorrido.** O Edital 35/2026 foi composto por
reaproveitamento do 34/2026, com o mesmo quadro 7/1/2, publicado **sem receber inscrição alguma**. A
tela do recorte de PcD diz *"Ninguém concorreu por este recorte… a ordem vazia é um fato normativo,
e emiti-la declara que ninguém concorreu ali. Emitir continua sendo ato seu — nada foi constituído
automaticamente"*, e a seção da ordem diz *"Nenhuma inscrição se autodeclarou nesta Modalidade de
Concorrência"* em vez de parecer pendência. A ordem vazia foi então **emitida pela interface**: a
confirmação declarou zero participantes com posição, e o ato nasceu. `FR-492a` cumprida por percurso.

**5.2 — a Modalidade que chega depois: inexequível pela interface, e a metade que resta foi
percorrida.** A tela de Retificação **não acrescenta Modalidade de Concorrência** — ela acrescenta
Perfil, linha do quadro, Evento e Anexo, e cada Modalidade existente só oferece "Remover do Edital".
O registro da medição está em
[achado-percurso-ampla-sem-inscricao.md](achado-percurso-ampla-sem-inscricao.md).

O que foi percorrido é a regra que a `FR-494a` protege, pela Retificação que a interface permite:
com **as três ordens já emitidas**, o Quadro de Vagas do Edital 34/2026 foi retificado — a linha de
PPI de 2 para 3, e o total do Perfil de 10 para 11 — e a Retificação foi publicada. O resultado:

| O que se olhou | O que aconteceu |
|---|---|
| ordem da ampla | **continua vigente**, emitida 22:29, sem aviso de obsolescência |
| ordem de PPI | **continua vigente**, emitida 22:30, sem aviso sobre ela |
| ordem de PcD | **continua vigente**, sem aviso |
| corte de PPI | **ficou obsoleto** — *"a linha do quadro de vagas de onde este corte tirou o alvo mudou"* |
| corte de PcD e da ampla | **intactos** |

**É a `FR-494a` e a `FR-494` de uma vez.** A Retificação do quadro não obsoleta ordem nenhuma — o
que ela alcança é a cauda, que é o que a `FR-494a` antecipa por escrito ("o que pode ficar obsoleto
é a apuração da ocupação, porque o Quadro de Vagas mudou de números") —, e a obsolescência **não
atravessou** para os outros dois recortes, embora a Retificação seja do mesmo Perfil e do mesmo
marco.

**O que não foi demonstrado, e fica dito:** que o recorte **novo** nasce sem ordem. Ele depende de
criar uma Modalidade por Retificação, e a interface não o faz. A regra está prendida por
`test_ordem_por_recorte.py::test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla`.

**5.3 — o Edital que emitiu antes desta feature: percorrido**, no passo 4 do cenário 1. A tela do
recorte sem ordem própria explica a ordem única do marco, oferece consultá-la e não oferece
correção nenhuma.

### A ressalva do `SC-169`, dita inteira

Os três recortes foram percorridos **ordem → corte → ocupação → convocação**, cada um com o seu
número do quadro (7 / 1 / 2), e a tela da convocação foi alcançada e **praticou ato** nos três.

**A convocação praticada foi a de regularização, e não a de vaga inicial.** A razão não é da `034`:
a fila de vaga inicial sai de `elegiveis_em_ordem`, que filtra por quem **habilitou na Etapa que o
corte governa** — e o marco montado no percurso declara `cutGovernedStage = NONE`, que é o corte
terminal que a `FR-224` admite e que o Edital 69/2026 da amostra pratica. Sem Etapa governada,
`habilitadas_na_etapa` devolve conjunto vazio, e ninguém é chamável para vaga inicial — **na ampla
igualmente**, e não só nos recortes reservados.

Não foi possível corrigir o cenário por Retificação: a tela de Retificação não expõe os campos da
regra de corte, e recompor o Edital do zero repetiria o percurso inteiro. Fica registrado como
limitação do **cenário montado**, e não da feature: o que a `034` entrega — a ordem, o corte e a
apuração por recorte, e a tela da convocação alcançável por recorte com os números daquele recorte —
foi percorrido nos três.

---

## Os testes alterados, um a um, com o motivo

**São doze casos, em quatro arquivos, mais uma correção de prosa num quinto.** O `research.md` `R-5`
previa **oito em três arquivos**, e a diferença está explicada logo abaixo da tabela.

| # | Caso | O que mudou | Motivo |
|---|---|---|---|
| 1 | `test_executabilidade.py::test_reserva_em_marco_que_nao_sorteia_produz_aviso_e_nao_impedimento` → `..._nao_produz_mais_aviso` | afirmava `len(achado) == 1` e a severidade; passa a afirmar `== []` | `FR-501`: a via de apuração passou a existir, e o aviso perdeu o objeto |
| 2 | `...::test_o_aviso_da_reserva_nomeia_a_causa_e_nao_o_sintoma` → `test_nenhum_achado_da_familia_sobra_sobre_o_quadro_com_reserva` | seis asserções sobre a mensagem do aviso deram lugar a uma sobre o `path` do quadro | a mensagem não existe mais; o que tem valor prender é que a aposentadoria **não** levou junto as regras vizinhas do mesmo `vacancyTable` |
| 3 | `...::test_o_aviso_da_reserva_nao_e_emitido_na_retificacao` → `test_a_aposentadoria_alcanca_tambem_a_retificacao` | a asserção é a mesma; o nome e a razão mudaram | antes o silêncio na Retificação era **exceção** (`FR-459`); agora é a regra geral. O caso fica porque a distinção entre os dois atos continua real para as outras regras do quadro |
| 4 | `...::test_o_aviso_alcanca_o_segundo_marco_quando_o_primeiro_sorteia` → `test_o_segundo_marco_computado_tambem_deixou_de_receber_o_aviso` | afirmava `"COMPUTA" in message`; passa a afirmar ausência | o conteúdo fica porque a **forma** do defeito sobrevive à regra: uma regra futura que leia `marcos_do_perfil[0]` erra do mesmo jeito, e é este conteúdo que a pega |
| 5 | `...::test_dois_marcos_em_lista_unica_saem_num_achado_so_que_nomeia_os_dois` → `test_dois_marcos_computados_no_mesmo_perfil_nao_produzem_aviso_algum` | prendia a **agregação** (um achado por Perfil); passa a afirmar ausência | a agregação deixou de ter o que agregar; o conteúdo prova que a aposentadoria não parou no Perfil de um marco só |
| 6 | `test_ocupacao.py::test_recorte_reservado_em_marco_computado_nao_oferece_apuracao` → `..._agora_oferece_apuracao` | `count(...) == 1` → `== 2` | `FR-502`: a ação voltou a ser oferecida onde passou a executar. **É troca de sentido, e não de número** — por isso está nomeada aqui |
| 7 | `...::test_no_lugar_da_apuracao_a_tela_nomeia_a_causa_e_nao_o_sintoma` → `test_a_frase_do_fora_do_sistema_saiu_da_tela` | `"fora do sistema" in pagina` → `not in`, e mais duas ausências | a frase deixou de ser verdade. Frase verdadeira que virou falsa é pior do que frase ausente |
| 8 | `test_hardening_pos_auditoria.py::test_os_dois_avisos_da_familia_nao_impedem_a_publicacao` → `test_o_aviso_que_resta_na_familia_nao_impede_a_publicacao` | a asserção de severidade do aviso virou asserção de ausência; os dois impedimentos ficam | eram dois avisos, é um |
| 9 | `...::test_a_familia_inteira_dispara_no_mesmo_edital` | nenhuma linha do caso mudou — mudou `A_FAMILIA`, que ele compara por igualdade | **foi ele que acusou a aposentadoria**, em vez de deixá-la passar como silêncio |
| 10 | `...::test_cada_achado_da_familia_leva_a_etapa_em_que_a_correcao_e_feita` | idem — percorre `A_FAMILIA` | sem a remoção da entrada, ele quebraria com `KeyError` |
| 11 | `...::test_a_revisao_apresenta_os_quatro_e_nao_o_primeiro` → `..._os_tres_...` | nome e docstring | **este caso não falhou**, e o silêncio é o ponto: `COM-COTA` continuava no corpo por causa de **outro** achado do mesmo Perfil, e a asserção passou a valer por acidente |
| 12 | `test_limites_da_classificacao.py::test_a_classificacao_nao_cria_corte_vaga_nem_rota_para_candidato` | `"corte" not in emissao` → `not re.search(r"\bcorte", emissao)` | a busca era por **substring**, e `recorte` a contém. Estreitar uma varredura merece desconfiança, e por isso veio acompanhada de `test_a_varredura_do_corte_distingue_corte_de_recorte`, que prova que o termo proibido continua sendo acusado |
| — | `test_reversao.py` — docstring do módulo e de `apuracao_da_cota` | prosa | a frase *"o caminho do ator não a alcança em certame computado"* deixou de ser verdade. **O helper não foi apagado**: ele é chamado por seis casos, e a razão de ele existir mudou — isolar o movimento do percurso que o precede |

### Por que doze, e não oito

O `research.md` `R-5` contou **um** caso em `test_hardening_pos_auditoria.py` (a linha 1055). A
medição feita aqui, rodando a suíte contra a implementação, mostra **quatro**: o código
`reserved_row_without_ordering` não está solto no arquivo — ele é uma entrada do dicionário
`A_FAMILIA`, que **quatro** casos leem. A contagem por linha não enxerga um dicionário compartilhado.

O décimo segundo é de outra natureza: a varredura de fronteira da `015` foi alcançada pela palavra
**recorte**, que é vocabulário do domínio desta feature. Não era previsível pela contagem de `R-5`,
que media o achado da `032` e não a colisão léxica.

*Fica registrado, e não corrigido para trás*, pelo mesmo critério que o `research.md` usou com a
própria contagem errada: quem for conferir a entrega procurando oito e achando doze precisa saber
por quê.

---

## Testes novos

| Arquivo | Casos | O que prende |
|---|---|---|
| `tests/unit/classificacao/test_recortes_do_marco.py` | 11 | a derivação única, a exclusão da ampla declarada, o 404 e a igualdade da `SC-172` |
| `tests/unit/classificacao/test_universo_do_recorte.py` | 9 | o `D-001` nas duas direções, e a ordem própria de cada recorte |
| `tests/integration/classificacao/test_ordem_por_recorte.py` | 18 | não-atravessamento, confirmação cruzada, universo emitido, leitura pura, recusa do sorteio, ordem vazia, os dois casos de borda |
| `tests/integration/classificacao/test_ordem_sem_reserva_nao_muda.py` | 4 | a não-regressão da `FR-493` |
| `tests/interface/test_navegacao_entre_recortes.py` | 16 | a navegação lida da página, o 404, a ordem única histórica, o recorte vazio |
| `tests/unit/divulgacao/test_documento.py` (acrescentado) | +3 | a `FR-506` no papel |
| `tests/performance/test_ordenacao.py` (acrescentado) | +2 | o orçamento de consulta por recorte |
| `tests/contract/test_limites_da_classificacao.py` (acrescentado) | +1 | que a varredura estreitada ainda enxerga o termo proibido |
| `tests/fixtures/recortes.py` (**novo**, não é caso) | — | o cenário 7/1/2 e os ajudantes de emissão por recorte |

---

## Dois achados do percurso, registrados e não corrigidos

**Nenhum dos dois é da `034`, e nenhum vira escopo por decisão de quem implementa.**

1. **O Perfil que declara Modalidades e não aponta a ampla não recebe inscrição de não-cotista.** No
   portal, o campo `Modalidade` da inscrição é obrigatório e só oferece as Modalidades declaradas:
   quem não é PcD nem PPI **não consegue se inscrever**, e a recusa é do navegador. A Revisão
   adverte, mas sobre o quadro — *"todas contam como lista reservada"* —, e não sobre a consequência
   no portal. Registro completo em [achado-percurso-ampla-sem-inscricao.md](achado-percurso-ampla-sem-inscricao.md).
2. **A tela de Retificação não expõe os campos da regra de corte** — `cutTargetKind`,
   `cutGovernedStage`, `cutSurplusCount` e `cutContinuation`. Só `cutTieOutcome` aparece. Corrigir a
   Etapa governada de um marco publicado, portanto, não tem caminho pela interface. Foi o que impediu
   o percurso de exercitar a convocação para vaga inicial.

---

## O que a revisão de código pegou, e o que cada coisa custou

**Quatro achados, e o primeiro era da própria promessa da feature.**

### O botão que voltou a sempre falhar — e a lição sobre a `FR-501a`

A `032` guardava a ação de apurar com o campo `apuravel`, derivado do predicado
`emite_ordem_no_recorte`. A `FR-501a` mandou remover o predicado **porque ele deixou de variar**, e
a remoção estava certa. **O que estava errado foi não pôr nada no lugar**: a condição que a tela
passou a usar — quem pode emitir, e recorte com linha no quadro — não pergunta o que a apuração
exige, que é **ordem vigente naquele recorte**.

O resultado foi a `SC-170` violada pela feature que existe para cumpri-la: num certame com as ordens
reservadas ainda não emitidas, a tela oferecia os três botões e dois recusavam com
`ordem_nao_vigente` (409). Medido por reprodução antes de corrigir: **3 botões oferecidos, 1 com
ordem**.

**O teste que devia ter pego contava botões e nunca clicava.** Ele afirmava
`count("Apurar a ocupação deste recorte") == 2` sobre um cenário em que só a ampla tinha ordem — a
asserção era verdadeira, o produto estava errado, e a suíte ficava verde. É exatamente o defeito
contra o qual a `T045` adverte, cometido dentro da feature que a escreveu.

**A correção** é `temOrdem` no selector, e ele **não é `apuravel` renomeado**: `apuravel` perguntava
se o **marco** emite ordem naquele recorte — propriedade normativa, que deixou de variar —, e
`temOrdem` pergunta se **existe ordem vigente ali agora** — estado do certame, que varia o tempo
todo. Onde não há, a tela mostra a razão e o caminho para emiti-la, que é a `FR-498` aplicada à
outra tela.

**Os três casos que a prendem** estão em `test_ocupacao.py`, e um deles **pratica o POST**:
`…com_ordem_emitida_oferece_apuracao_e_ela_conclui`,
`…sem_ordem_nao_oferece_apuracao_e_diz_onde_emiti_la` e
`…a_acao_oferecida_no_recorte_sem_ordem_seria_recusada` — este último provando que a razão dita na
tela é a razão real, e não uma tela que cala.

### Três defeitos de texto e de caminho, todos na mesma família

| Achado | O que acontecia | Correção |
|---|---|---|
| **"Cancelar e voltar" perdia o recorte** | numa conferência de PPI, o botão e a trilha voltavam à ampla. A tela que abria era **legítima** — uma ordem verdadeira, de um recorte verdadeiro —, e é isso que tornava o desvio silencioso | `views.py::_navegacao_do_recorte` passou a preparar `url_do_recorte`, e os dois links a usam. Nenhum template monta `?lista=` na mão |
| **"é o primeiro ato deste marco"** | ao confirmar a primeira ordem de uma cota num marco que já tem a da ampla, `ato_vigente` vem vazio **porque é vazio naquele recorte** — e a frase afirmava, numa confirmação de ato imutável, que o marco não tinha ato nenhum | "deste recorte", em `ordenacao_confirmar.html` |
| **"primeiro ato do marco" no histórico** | a mesma frase na tela que fica, sobre uma lista que a view já filtra por recorte | "deste recorte", e o título da seção passou a nomear o recorte |

**Os três são da mesma espécie do defeito que a `FR-502` descreve**: nada quebra, nada erra, e o que
sobra é uma pessoa decidindo sobre outra coisa. Prendidos por três casos em
`test_navegacao_entre_recortes.py`.

---

## Um defeito que o percurso pegou e teste nenhum pegava

A tela do corte recebeu, na primeira versão da `US2`, só `recortes` — e não `recorte_atual`. O
cabeçalho saiu com *"Recorte:"* seguido de **nada**: o mecanismo de template trata variável ausente
como vazia, e por isso não houve erro, exceção nem teste vermelho. O caso que existia conferia a
lista de caminhos oferecidos, e ela estava correta.

A correção foi derivar as duas chaves juntas (`views.py::_navegacao_do_recorte`), e o caso novo
`test_as_duas_telas_nomeiam_o_recorte_em_que_se_esta` confere as **duas metades** da `FR-497` nas
duas telas. É a mesma espécie de defeito que a `FR-502` descreve, entrando por outra porta.

---

## `T048` — a verificação final

```bash
cd backend && make lint check test-pg
```

| Passo | Resultado |
|---|---|
| `ruff check` | `All checks passed!` |
| `ruff format --check` | `1117 files already formatted` |
| `manage.py check` | `no issues (0 silenced)` |
| `manage.py makemigrations --check --dry-run` | **`No changes detected`** — é a prova da `SC-175`, e **só dela** |
| `pytest` contra PostgreSQL | **7284 passando, 11 pulados, 0 falhas** — 676,55 s |

Linha de base, medida em `T002` antes da primeira edição: **7213 passando, 12 pulados**.

### A conta da diferença, medida e não estimada

A suíte coletava **7225** itens na base e coleta **7295** agora: **+70**. A decomposição foi obtida
comparando as duas listas de identificadores coletados — a da `main` `d30f6d8`, lida de uma worktree
auxiliar descartada em seguida, e a de agora:

| Origem dos itens novos | Quantos |
|---|---|
| os cinco arquivos de teste novos | **58** |
| `test_documento.py` — a `FR-506` no papel | 3 |
| `test_ordenacao.py` (performance) — o orçamento por recorte | 2 |
| `test_limites_da_classificacao.py` — a prova de que a varredura estreitada ainda enxerga | 1 |
| `test_sem_dado_pessoal_da_amostra.py` | **6** |
| **Total** | **70** |

**Os seis últimos não são casos escritos por esta feature**, e a linha merece explicação: aquele
teste é parametrizado **por arquivo**, e varre `backend/tests/**/*.py`. Os seis arquivos `.py` novos
— os cinco de teste e `tests/fixtures/recortes.py` — entraram na varredura por conta própria, e os
seis passam. É a garantia de que nenhum dado da amostra real vazou para o que esta feature escreveu.

**Nove identificadores desapareceram, e os nove têm substituto nomeado** — cinco em
`test_executabilidade.py`, dois em `test_ocupacao.py` e dois em `test_hardening_pos_auditoria.py`.
São as renomeações da tabela acima. **Nenhum teste sumiu sem substituto**, e a comparação por
identificador é o que prova isso: contagem não provaria.

### O pulado que virou executado

A suíte ia de **12 pulados** para **11**, e o que mudou foi o caso
`test_vocabulario_da_composicao.py::test_o_termo_usado_pela_tela_se_define_no_primeiro_uso[ordenacao.html-recorte]`.

Ele se pulava sozinho — *"`ordenacao.html` não usa «recorte» em texto visível"* —, e passou a rodar
porque a `FR-497` fez a tela usar a palavra. A `US2` teve de lhe dar a definição `<dfn>Recorte</dfn>`
**e** pôr a navegação depois dela, que é o que o teste cobra.

**Um pulado a menos é um teste a mais de fato exercitado**, e não um teste desativado. A distinção é
a que a conferência caso a caso existe para fazer.
