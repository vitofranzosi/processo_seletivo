# Verificação: A experiência da convocação, incremento 1 (121)

**Tarefas**: [tasks.md](tasks.md) · **Rastreabilidade**: [rastreabilidade.md](rastreabilidade.md)

Registro das conferências antes do código (T001), da linha de base (T002), do que a implementação
encontrou no caminho e da suíte final (T057). Caminhos relativos a `backend/`.

## T000 — o portão

O plano e as tarefas estão na `main` desde o PR #399 (`1bba1c92`). A worktree partiu de
`5c3501d3`, e a linha de base abaixo, sobre esse commit, tem `tests/test_citacoes_de_requisito.py`
verde.

## T001 — as conferências antes do código

**(a) As listas literais das varreduras de vocabulário.**

- `tests/test_vocabulario_da_convocacao.py`, `DA_019`: as telas da gestão e do portal da `019`, os
  módulos de aplicação e de domínio da convocação, e os parciais da `118`
  (`_obrigacoes_da_convocacao.html`, `_cartao_do_documento_da_convocacao.html`,
  `_requerimento_nas_obrigacoes.html`). Os `.html` da lista passam também pela conferência de
  acentuação do texto visível.
- `tests/test_vocabulario_dos_documentos_da_convocacao.py`, `DA_115`: as telas dos documentos, os
  parciais da `118`, `portal/obrigacoes.py` e `portal/situacao.py`.
- `tests/portal/test_vocabulario_das_telas_publicas.py` **não é lista literal**: lê as respostas da
  vitrine, da seleção e das telas de acesso, com o dicionário importado da `063`.

Entraram nas duas listas o parcial novo da chamada e os quatro modelos da mensagem; na `DA_019`,
também `convocacao/domain/mensagem.py` e `convocacao/domain/prazo_apresentado.py`. A varredura das
telas públicas ganhou o caso das telas de acesso a caminho da convocação (FR-3892).

**(b) O guardião da contagem de migrations.** `tests/migrations/test_migrations.py` tem dois: o da
`017` (`divulgacao`, `processos`, `publicacoes`, `:749`) e o da `022` (`APPS_QUE_A_022_NAO_TOCA`,
`:984`). **`convocacao` não está em nenhum dos dois**, e por isso a `0006` não pede linha nova em
guardião. O plano e a T040 supunham o contrário; não há o que atualizar.

**(c) Os testes de JavaScript.** `tests/test_javascript.py` roda `node --test javascript/*.test.js`
e exige só que o glob tenha encontrado algum teste, nas duas formas do resumo (TAP no *pipe*, `ℹ` no
terminal). O *shim* `tests/javascript/dom.js` cobre as APIs dos scripts da gestão; os dois testes
novos (`envio.test.js`, `arquivo.test.js`) usam objetos simples, no molde de
`correcao-da-convocacao.test.js`, porque nenhum dos dois scripts usa o que o *shim* simula.

**(d) A última migration da convocação** era `0005_documentos_da_convocacao`. A desta feature é a
`0006_modelo_da_mensagem`, só `AddField` com `default=""`.

**(e) A fonte do modelo com o carregador com cache.** Com as settings de teste e um motor montado
com `debug=False` — o que dá ao Django o `cached.Loader` das settings de produção —,
`get_template("portal/convocacao.html").template` é um `django.template.base.Template` com
`.source` preenchido, e duas chamadas devolvem **o mesmo objeto**. A R-009 se sustenta: o resumo sai
da fonte que renderizou.

**(f) Os testes que prendiam o texto da mensagem.** Nenhum teste importava `CORPO`, `COM_PRAZO`,
`SEM_PRAZO` nem `ASSUNTO` de `comunicar.py`. Prendiam o texto pelo envio:

- `tests/unit/convocacao/test_mensagem.py`: o assunto, *"acesse a sua área"* e o prazo em `HH:MM`
  (`:151`, `:170`) — revistos, citando a FR-3875 e a FR-3884;
- `tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py`: separa o prazo por *"Prazo
  para atender:"* — o rótulo continua, e o teste passa sem mudança;
- `tests/unidades/test_identificacao_multiunidade.py`: a assinatura *"— Seleções"* e *"fale com
  ‹canal›."* — continuam no rodapé; o caso passa a dar ao envio a escolha e o identificador da
  inscrição que ele agora precisa;
- *"Documento recebido. A comissão vai conferir."*: `interface/test_portal_documentos_da_convocacao.py:106`,
  `navegador/test_jornada_dos_documentos_da_convocacao.py:254` e
  `navegador/test_jornada_da_correcao_da_convocacao.py:162` — passam a ler a confirmação da FR-3870.

O que a conferência **não** achou, e a suíte achou depois: três arquivos simulavam a falha do SMTP
trocando `comunicar.send_mail`, que deixou de existir (`integration/convocacao/test_titulares_em_lote.py`,
`test_nao_atendimento_em_lote.py`, `interface/test_convocacao_em_fluxo.py`). Passaram a simular em
`comunicar.EmailMultiAlternatives.send`, o mesmo ponto do envio.

## T002 — a linha de base

`make lint check test-pg`, com `DB_NAME=ps_121`, os grupos `assistente` e `navegador`, 4 workers,
sobre `5c3501d3`, em 2026-11-05:

- `lint` e `check` verdes;
- **16 516 passando, 12 pulados, nenhuma falha**, em 852 s.

Os 12 pulados: os 10 pares *termo × template* de `test_vocabulario_da_composicao.py`, o E2E da Caixa
(`test_sorteio_com_a_fonte_de_producao.py`) e a recusa por vendor (`test_database_permissions.py`).

## O que a implementação encontrou

- **A varredura da CSP lê todo modelo `.html`, e não só o portal.**
  `tests/interface/test_politica_de_conteudo.py` percorre `*/templates/**/*.html` e recusa `style=`
  e `<style>` em qualquer um. O plano supunha que os modelos da mensagem, em
  `convocacao/templates/`, escapariam dela, e o contrato pedia *"CSS só em `style` inline"*. O HTML
  da mensagem saiu **sem CSS nenhum**: o destaque do prazo e os quadros usam os atributos de
  apresentação do próprio HTML (`bgcolor`, `border`, `cellpadding`), que os clientes de e-mail
  respeitam bem. A regra que o contrato protege — nada de `<style>`, de folha ou fonte externa, de
  `src=` — continua, mais estrita. A SC-1164 (humana) dirá como sai em cada cliente.
- **O assunto mora no modelo.** O resumo da D-009 é das duas fontes; um assunto escrito em
  `comunicar.py` sairia sem versão identificável. A primeira linha de `inicial.txt` e de
  `correcao.txt` é o assunto, e o envio a separa do corpo.
- **O navegador trata a âncora depois do script.** A volta da recusa é `#item-‹id›`, e o cartão é
  focável (`tabindex="-1"`, da `118`): o Chromium focava o cartão depois de `recusa.js` focar a
  recusa. O script — um dos três, sem script novo — passou a refocar a recusa no `load`. Sem
  script, a âncora leva ao cartão, e a recusa está nele.
- **O Requerimento a preencher ganhou lugar no bloco *O que falta*.** A ação da FR-3863 leva a ele
  quando é a única tarefa, e a lista de tarefas com âncora, onde ele morava, saiu com a FR-3736
  revista. O link *"Preencher o Requerimento de Matrícula"* foi para *O que falta*, depois dos
  documentos, com a âncora `requerimento-a-preencher` (FR-3738 da `118`).
- **O título da página sem convocação continua *"Convocação"*** (caso-limite *aguardando ou não
  convocado*), e o cartão do prazo só leva o rótulo *"Prazo desta convocação"* quando tem data: com o
  prazo não iniciado ou sem vencimento, ele diz **só** a frase do caso (FR-3861).
- **A frase da prévia da correção** (FR-3890) diz também o caso da D-008: sem nenhuma mensagem
  enviada com sucesso na cadeia, a mensagem sai como a primeira. Sem isso, a comissão esperaria o
  quadro da correção que não viria.
- ***"Você envia tudo pela sua área do candidato."*** saiu só na variante documento e Requerimento:
  nas outras, a frase da FR-3884 já diz por onde se envia, e em *"nenhum"* não há o que enviar.

## A revisão de código

A revisão do PR achou seis pontos, todos corrigidos e cobertos por teste:

- **A confirmação com a chamada fechada entre o envio e a volta** dizia *"Você não tem mais
  documentos para enviar agora"* acima de *"ficaram sem envio"*. Fechada a chamada, ela diz só o
  que foi recebido.
- **A volta do envio não guardava a inscrição**: a convocação de outra inscrição da mesma pessoa
  consumia a confirmação ou a recusa. Os dois registros levam a inscrição, e só a convocação dela
  os consome.
- **Uma falha na escolha ou na montagem da mensagem subia depois da reserva da chave**, sem
  registro, e cada nova tentativa diria *"estado indeterminado"*. Ela vira `FALHA` gravada, com o
  modelo quando ele chegou a carregar.
- **O prazo ainda era formatado à mão** no acompanhamento, na lista, nos dados do ato e no núcleo
  do vencido. Passou pela função única (FR-3873), por dois filtros de template
  (`portal/templatetags/prazo_da_convocacao.py`) e por `apresentar` em `frase_do_prazo_decorrido`.
- **A cadeia era lida em todo envio**, também sem convocação anterior: duas consultas por pessoa na
  convocação em lote. A primeira chamada não a lê.
- **Uma condição repetida** no cartão do Requerimento saiu.

## Registrado, sem desenvolver

Além dos dois achados do plano (a convocação sem `@resposta_privada`, e `_dias_ate`):

- A `ComunicacaoEmitida` não tem instante na `FALHA` (a constraint o proíbe). A reconstrução de uma
  tentativa que falhou usa o instante da própria reconstrução; como a lista e a cadeia só mudam
  antes do envio, o resultado é o mesmo, mas a auditoria não sabe **quando** a tentativa falhou
  além da trilha.

## T057 — a suíte final

Mesmas condições da linha de base (`DB_NAME=ps_121`, `assistente` e `navegador`, 4 workers).

**Primeira rodada**, em 2026-11-05, sobre `85e86a7b` com a documentação: `lint` e `check` verdes;
**16 729 passando, 12 pulados, 2 falhas**, em 801 s.

- `tests/interface/test_acessibilidade.py::test_nenhuma_classe_citada_deixa_de_existir_na_folha`:
  a classe `andamento-da-convocacao` estava no template sem regra em `portal.css`. **Defeito desta
  feature**, corrigido com a regra.
- `tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`
  (0,0117 s contra 0,0037 s): o teste de tempo que o `AGENTS.md` registra como oscilante com 4
  workers. A feature não toca a ocupação; isolado, passou **3 de 3**.

**Os pulados, por lista:** os mesmos 12 da linha de base, arquivo a arquivo e motivo a motivo — os
10 pares de `test_vocabulario_da_composicao.py`, o E2E da Caixa e a recusa por vendor. Nenhum teste
novo pula. A diferença de total (+213) é a dos testes novos e parametrizados desta feature.

**Segunda rodada**, sobre `87bd0a93`, depois da correção: `lint` e `check` verdes; **16 730
passando, 12 pulados, 1 falha**, em 855 s. Os pulados são os mesmos 12, por lista. A falha é de novo
`test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`, e pelo procedimento do `AGENTS.md`
(*Um teste de tempo oscila sob carga*) ela foi medida isolada: **8 de 8** passando, com
`PYTEST_WORKERS=0`. O diff desta feature não toca nenhum arquivo de `ocupacao`, `classificacao` ou
`resultados`, que são o que o teste mede. Não é regressão; a decisão de mexer no teto é do usuário.
