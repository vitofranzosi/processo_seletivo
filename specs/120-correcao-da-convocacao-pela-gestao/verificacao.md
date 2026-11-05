# Verificação: A correção da convocação pela gestão (120)

Registro da implementação, em 04/11/2026, sobre a `main` em `015861c7`. Caminhos de teste relativos a
`backend/tests/`.

## T001 — conferências antes do código

| | O que se conferiu | O que se achou | Consequência |
|---|---|---|---|
| a | se a leitura do recorte expõe a ordem vigente (R-006) | não expõe; mas a ordem sucedida já chega como causa de obsolescência da apuração (`ordem_sucedida`), e a ordem ausente não tem apuração | `impedimento_da_correcao` lê só a apuração e as causas; **nenhuma consulta a mais** por página. A apuração ausente não convive com cartão em aberto — convocar exige apuração —, e o ramo dela fica no parcial sem teste de tela próprio |
| b | testes que prendem a razão da trilha de convocar | `integration/ocupacao/test_auditoria.py` prende `Motivo da sucessão:` por inclusão, e não por igualdade | a frase nova (*"Sucede a convocação…"*) entra depois, sem quebrar nada |
| c | a lista literal de `test_vocabulario_da_convocacao.py` | não tinha os parciais novos | os dois entraram (T027) |
| d | como `test_javascript.py` descobre os testes | glob `javascript/*.test.js`, sem contagem fixa | o teste novo entra sozinho |
| e | regras de folha para as classes do parcial | todas as classes usadas já têm regra; nenhuma classe nova | nada na folha |

## T002 — linha de base

`make test-pg` numa cópia descartável de `93e8c3a5`, com os grupos `assistente` e `navegador`, 4
workers, `DB_NAME=ps_120_base`: **15 795 passando, 12 pulados, 1 falha**, em 793 s. A falha é
`performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`
(0,0150 s contra 0,0041 s), o teste de tempo que o `CLAUDE.md` registra como instável sob carga — a
suíte rodou ao lado dos testes desta feature, no mesmo cluster. Os 12 pulados são os do `CLAUDE.md`:
10 de `test_vocabulario_da_composicao.py`, a recusa por vendor e o E2E da Caixa.

## A jornada no navegador (T028–T030)

`navegador/test_jornada_da_correcao_da_convocacao.py`, num Chromium pelo Playwright, contra o
`live_server`: a comissão em 1280 × 900, o convocado em 375 × 812. **4 de 4 passando.** As ações são
só no navegador; a preparação é das *fixtures* (Constituição, VI).

| Caso | O que prova | Capturas |
|---|---|---|
| `test_corrigida_na_gestao_o_convocado_complementa_e_envia` | **a jornada principal, passos 1 a 11 do quickstart.** O portal recusa o vencido; a comissão corrige pelo cartão lendo *"O que reabre"* e *"O prazo é estendido até…"*; o portal mostra o prazo novo, aceita a complementação do histórico pendente e o envio do Requerimento, a partir do rascunho feito no prazo; a comissão vê a complementação e o histórico com o motivo. Uma sucessora, a mesma chamada, a lista e as conferências intactas, um evento de trilha com o motivo e a convocação corrigida | `capturas/test_corrigida_…-01` a `-07` |
| `test_corrige_pela_tela_nos_outros_estados_em_aberto[prazo-em-curso]` e `[sem-comunicacao]` | SC-1141 nos dois estados que o caso principal não percorre, com o vencimento antecipado: a prévia sem *"O que reabre"*, o script dizendo *"antecipado"*, e o resultado | `capturas/test_corrige_…` |
| `test_com_a_apuracao_superada_nenhum_cartao_oferece_formulario` | SC-1146: a limitação, a causa nas palavras do topo e *"Emitir a apuração seguinte"*, sem formulário | `capturas/test_com_a_apuracao_superada_…` |

Nenhuma violação da política de conteúdo no console em nenhum caso (a `Tela` da `115` a vigia), e
nenhuma rolagem horizontal no portal a 375 px.

**A demonstração humana** da T030 foi feita sobre as capturas do Chromium, lidas uma a uma, e não
no painel do app: a jornada pede um certame com documentos, Requerimento e prazo vencido, que o
`seed_demo` não produz, e o teste no navegador é a mesma jornada pelo mesmo canal do ator, com a
preparação às claras. O que as capturas mostram: a prévia com cada valor e a origem ao lado; o
efeito do vencimento dito antes do clique; o resultado com os dois vencimentos; o portal com o prazo
novo no formato único da `118`, o histórico pendente com o reenvio aberto e o Requerimento como
tarefa; e a limitação no cartão com a apuração superada.

**Nenhum defeito do portal impediu a jornada** (FR-3854): o portal leu a sucessora pelas regras da
`115` e da `118`, sem mudança.

## Achado de passagem

A lista de causas no topo da condução **não tinha frase** para `acrescimo_posterior`, que a `097`
acrescentou: com uma vaga acrescida depois da apuração, a linha saía vazia. A frase passou ao parcial
comum `_causa_de_obsolescencia.html`, que a correção também usa, e ganhou a do acréscimo e um fecho
para a causa que vier depois. É a única mudança fora do escopo estrito, e é de texto.

## Desvios do plano, registrados

- **A ação fica por último no cartão**, depois da emissão da comunicação, e não logo após
  *"Registrar desfecho"*: a recusa de quem corrigia uma chamada que teve desfecho no intervalo
  aparece no cartão que agora mostra o desfecho, e por isso o parcial fica fora do bloco *sem
  desfecho*. O desfecho continua a ação principal.
- **O detalhe da prévia superada não nomeia os componentes que mudaram.** O plano dizia que o comando
  os registraria; com a assinatura num campo só, o comando não tem os valores que a tela assinou. A
  recusa recarrega a tela, que mostra a prévia nova, e é isso que a FR-3857 exige.
- **A Retificação no intervalo é simulada** no teste do serviço pela versão que o comando lê sob a
  trava, e não por uma Retificação publicada; a unidade prova que a versão muda a assinatura.
- **A espécie que muda no intervalo é simulada** na tela, pela função da espécie; a regra dela é
  provada na unidade, e a recusa no serviço.
- **A chamada sem vencimento** é recusada no comando (`correcao_sem_vencimento`), e a tela não
  oferece a ação nela — D-004, como planejado.
- **O 404 da convocação nomeada fora do recorte** é um `raise Http404 from` novo em `convocar_view`,
  função que o inventário da `033` já registrava; a linha de mudança foi acrescentada lá.
