# Research: a advertência no "Encerrar Processo"

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-11-06

As decisões D-001 a D-007 estão na spec. Aqui ficam as escolhas de desenho (R-1 a R-8) que a spec não
fixa, cada uma com o que se escolheu, por quê e o que se descartou. Tudo foi conferido no código da
`main` em `5cf5f179`.

## R-1 — A composição mora em `interface/encerramento.py`, ao lado da do Edital

- **Decisão**: uma função nova, `encerramento.do_processo(processo, ator, *, agora)`, que devolve a
  advertência do Processo. Ela reaproveita, por Edital, as duas peças que `da_confirmacao` já usa:
  `pendencias_do_edital.situacoes(..., ato="encerrar", com_advertencias=True)` com `_item`, e
  `_providencias_da_099`.
- **Por quê**: a FR-4351 pede a mesma regra e a mesma frase. Com a composição no mesmo módulo, uma frase
  mudada na `113` muda nas duas telas, e o teste de paridade (R-7) compara as duas funções.
- **Descartado**: chamar `da_confirmacao` de cada Edital. Ela devolve vazio para Edital fora de
  PUBLICADO (`encerramento.py`, primeira linha da função), e todos os Editais aqui são finais. Tirar
  essa guarda mudaria a tela do Edital encerrado, que hoje não tem confirmação de encerrar.
- **Descartado**: pôr a composição em `processos/application`. Ela redige frases e caminhos por ator,
  que é trabalho da interface. A regra continua em `pendencias_do_edital`, sem mudança.

## R-2 — Os tipos entram por lista explícita, com um guardião exaustivo

- **Decisão**: `TIPOS_NO_PROCESSO` lista os tipos da `113` que entram (os cinco de recurso), e
  `TIPOS_FORA_DO_PROCESSO` lista os que ficam fora (os três de período, os dois de Retificação e o
  `RASCUNHOS_NAO_ENVIAVEIS`, que só o cancelar produz). As providências da `099` entram pelo `DA_099` que
  já existe. Um teste unitário exige que cada constante de tipo de `pendencias_do_edital` esteja em
  exatamente uma das listas, ou no `DA_099`.
- **Por quê**: com só a lista de fora, um tipo novo da `113` apareceria no Processo sem ninguém ter
  decidido. Com só a lista de dentro, ele sumiria sem aviso. O guardião obriga quem criar o tipo a
  decidir.
- **Descartado**: filtrar pela espécie (`IMPEDIMENTO` ou `ADVERTENCIA`). A espécie diz o que impede o
  Edital, e não o que importa para o Processo (D-003).

## R-3 — Só os Editais finais publicados, na ordem da recusa

- **Decisão**: `processo.editais.filter(status__in=EDITAL_FINAL)`, mais a existência de `Publicacao`
  (`Exists`, numa consulta só), ordenados por ano, número e id, como `pending_editais`. O Edital
  cancelado antes de publicar não tem conteúdo vigente, e `effective_version` falharia nele.
- **Por quê**: FR-4350 e FR-4358.

## R-4 — Uma leitura consistente para todos os Editais, fechada antes do comando

- **Decisão**: a view abre `relatorio_do_edital.leitura_consistente()` em volta de `do_processo`, e
  **fecha antes de chamar `close_process`**.
- **Por quê**: a FR-4361 pede um só instante, e `fatos_do_edital` supõe a transação aberta. O comando
  abre a dele (`command_context`), com travas. Dentro do bloco de leitura, ele viraria um savepoint de
  uma transação `REPEATABLE READ`: as travas e a conferência dos Editais finais leriam o retrato do
  início da leitura, e não o estado de agora. O projeto não usa `ATOMIC_REQUESTS`, de modo que o bloco
  de leitura é de fato a transação de fora.
- **Descartado**: ler sem a transação, como a confirmação do Edital faz hoje. Para um Edital só isso é
  tolerável; com vários, dois Editais poderiam ser lidos em instantes diferentes.

## R-5 — O resumo da lista: um hash das frases, num campo oculto, sem assinatura

- **Decisão**: `resumo = sha256` sobre a serialização canônica (JSON ordenado) de
  `[(id do Edital, [mensagens do Edital, ordenadas])]`, em hexadecimal. As frases de cada Edital entram ordenadas porque a regra da `113` percorre os recortes de resultado sem `order_by`: a ordem dos prazos de recurso entre marcos é a do banco, e mudaria o resumo sem nada ter mudado (achado da revisão independente). Ele vai num
  `<input type="hidden" name="resumo_das_providencias">`. No POST, a view relê a advertência e compara o
  resumo enviado com o recalculado. Qualquer diferença, ou a ausência do campo, leva à reapresentação
  (FR-4365).
- **Por quê as frases, e não os fatos**: a frase já carrega tudo o que o gestor viu (contagem, data,
  marco, a quem pedir), e é exatamente o que precisa ser igual. Os URLs ficam fora porque dependem do
  ator e não mudam o que está em aberto. A lista vazia também tem resumo: o gestor que viu "nenhuma
  providência" e envia depois de nascer uma convocação é reapresentado.
- **Por quê sem assinatura (HMAC)**: o resumo não autoriza nada. Quem o forjasse para casar com a lista
  atual só pularia uma renovação que confirmar duas vezes já pula. Não há segredo a proteger, e a
  FR-4366 garante que a renovação não é barreira.
- **Descartado**: guardar o resumo na sessão. É estado no servidor, e o formulário aberto em duas abas
  se confundiria.

## R-6 — A reapresentação responde 409, sem chamar o comando

- **Decisão**: a reapresentação devolve a confirmação com o status **409**, a lista atual, o resumo
  novo, `renovada=True` (a frase da UX-279) e o motivo preenchido. O comando não é chamado, e por isso
  a chave de idempotência não é reservada. O formulário reapresentado leva a mesma chave.
- **Por quê 409**: é o código que o projeto já usa quando o estado mudou entre a leitura e o ato
  (`expected_revision`). É invisível para quem lê a tela, e permite ao teste distinguir a
  reapresentação do encerramento aceito (302). O formulário é comum, e não htmx, de modo que o 4xx é
  renderizado normalmente.
- **A ordem no POST**: primeiro a renovação, depois o motivo. Com a lista mudada e o motivo vazio, a
  tela volta com a renovação e o motivo continua vazio; o erro do motivo vem no envio seguinte, se for
  o caso. Assim o gestor nunca é levado ao comando sem ter visto a lista atual.
- **O motivo vazio** é conferido depois da renovação e antes do comando, e a tela volta (422) com a
  lista lida no próprio pedido, sem relê-la.
- **Na recusa do comando**, só no encerrar: a view relê o Processo, `pendentes`, o `impedimento` e, se
  a tela ainda oferece o Confirmar, a advertência e o resumo (FR-4360). No ativar e no cancelar, nada
  muda: a view recalcula só os pendentes, como antes, e o motivo não volta ao formulário (FR-4364).

## R-7 — Os testes

- **Unitário** (`tests/unit/interface/test_advertencia_do_processo.py`): o guardião exaustivo de R-2 e o
  resumo (mesma lista dá o mesmo resumo; uma frase diferente dá outro; lista vazia tem resumo).
- **Interface** (`tests/interface/test_advertencia_do_encerramento_do_processo.py`, transacional):
  - os cenários das histórias 1 a 5, sobre `tests/fixtures/relatorio.montar_cenario`: o final
    `pendente` é Edital encerrado com convocação no prazo, `sem-pendencia` é encerrado sem nada, e
    `cancelado` é o cancelado publicado;
  - a paridade (SC-1321): para cada Edital final, as frases do grupo são as de `_providencias_da_099`
    mais as de `_item` sobre as situações de `TIPOS_NO_PROCESSO`, e as providências que
    `fatos_do_edital` lista nos tipos do `DA_099` estão todas lá;
  - a renovação: lista mudada → 409, nenhum `AtoAdministrativo`, Processo Ativo; reenvio com o resumo
    novo → 302 e Processo Encerrado; sem resumo → 409;
  - o que não muda: "Cancelar Processo" sem bloco, e o desenho do botão (o teste de
    `test_paineis_e_telas_de_apoio.py` continua valendo);
  - a varredura de dado pessoal (SC-1323), com nome, CPF, e-mail e protocolo do cenário.
- **Desempenho** (`tests/performance/test_confirmacao_do_encerramento_do_processo.py`): o número de
  consultas da advertência com 1 e com 10 de escala de inscrições é o mesmo, e cresce por Edital, e não
  por inscrição. O orçamento é medido na implementação e fixado no teste, como o da `113`. Uma conferência
  à parte prende o detalhe e a lista de Processos sem consulta nova (SC-1324).
- **Os existentes**: o helper `ato()` de `tests/interface/test_processo.py` faz o GET da confirmação,
  lê a chave de idempotência do contexto e envia o POST sem o resumo. No encerrar, o resumo ausente leva
  à reapresentação (FR-4365), e o teste que espera 302 receberia 409. **É o único ajuste previsto**: o
  helper passa a ler também o resumo do contexto do GET e a enviá-lo. Fica nomeado no `verificacao.md`.
  Os outros POSTs ao ato do Processo não são afetados: o de `test_csrf.py` é recusado pelo CSRF antes da
  view, e os de `test_paineis_e_telas_de_apoio.py` e `test_limpeza_dos_achados_da_etapa_4.py` só fazem
  GET.

## R-8 — A tela

- **Decisão**: `processo_confirmar.html` ganha o bloco depois do aviso de recusa certa e antes das
  consequências, só com classes que já têm regra na folha (`aviso`, e `impedimentos` para a lista), o
  `role="status"` do bloco da `113` e um `<h3>` por Edital. A mensagem da UX-279 usa o padrão da
  mensagem de erro de hoje (`tabindex="-1" autofocus`), com a classe `aviso`. O `<textarea>` passa a
  receber o motivo de volta. A linha do botão não muda, porque um guardião a lê literalmente.
- **Por quê**: a CSP recusa estilo inline, e classe nova exige regra na folha. Reaproveitar as classes
  evita mexer na folha comum.
