# Percursos — o cenário F da proposta, com as identidades separadas

**Tudo pela interface.** Shell e banco preparam o ambiente e diagnosticam; **não atravessam passo
que deveria estar disponível à pessoa**. Não havendo caminho, registre a lacuna e siga — protocolo da
`034`.

**A condição que dá sentido a esta feature é a segregação.** Quem acumula papéis não encontra o
`N-01` nem o `N-04` — foi o que a convergência mediu. Cada percurso abaixo diz **qual identidade**,
e o seletor de identidade da gestão declara **um papel por vez**. Trocar de papel no meio de um
passo invalida o passo.

## Ambiente

- Banco próprio da worktree (`DB_NAME`), `migrate`, a preparação dos papéis **duas vezes** — a saída
  deve dizer `34 de 34` — e `seed_demo`. O seed cria **dois** Editais: o primeiro com o prazo de
  inscrição aberto, o segundo com resultado divulgado e janela recursal de cinco dias.
- `INTERFACE_SELETOR_IDENTIDADE=true` para a gestão; `PORTAL_IDENTIDADE_DEMO=true` para o candidato.
  O código de acesso do portal sai no terminal do servidor (ou em `preview_logs`).
- Abra sempre por `http://localhost:<porta>` — `127.0.0.1` devolve `DisallowedHost`.
- As identidades: **Gestor** (papel Gestor), **Publicador** (papel Publicador), **Julgador**
  (papel Julgador de recursos), **Auditor**, e `paulo.presidente` para a presidência.

---

## 1 — A ausência respeita o alcance (`SC-269`, `FR-730`, `FR-731`)

1. Como **Gestor**, abra o Processo da demonstração e anote a região *Atenção*.
2. Como **Publicador**, abra o mesmo Processo.

**Esperado**: se não houver sinal da divulgação, a frase **relativa** (`UX-084`) — nunca *"Nenhuma
condição de atenção neste Processo"*. Hoje é a global.

3. Como **Julgador**, abra o mesmo Processo sem recurso pendente.

**Esperado**: a mesma frase relativa.

4. **Contraprova do vazamento**: sem mudar nada que o Publicador alcance, resolva como Gestor uma
   condição que só ele vê (ou crie uma). Releia como Publicador.

**Esperado**: **o mesmo texto, letra por letra.** Se mudou, a frase está lendo o que ela não alcança.

5. Declare numa identidade só os papéis Gestor, Julgador e Publicador, num Processo sem condição.

**Esperado**: a frase global. Quem lê tudo pode ouvir que não há nada.

---

## 2 — O recurso aparece desde que chega (`SC-270`, `FR-732` a `FR-734`)

1. No portal, como candidata do segundo Edital, interponha recurso contra o resultado divulgado.
2. Como **Julgador**, abra o Processo **antes de qualquer ato**.

**Esperado**: sinal do recurso naquele Edital, dizendo que aguarda **admissibilidade**, com medida
*"N de M recursos"* e caminho para os recursos do Edital. Hoje: nada.

3. Na lista de Processos e no cartão do Edital, confira a ação de recursos.

**Esperado**: a contagem é de **pendentes**, e o rótulo diz isso.

4. Admita o recurso. Volte ao Processo.

**Esperado**: o **mesmo** sinal, agora dizendo *julgamento*. Não dois sinais.

5. Julgue-o. Volte ao Processo e à lista.

**Esperado**: sem sinal, e a contagem de pendentes caiu.

6. **Contraprova da partição**: com um segundo recurso cuja comissão esteja inteira impedida (a
   presidência consolidou o resultado atacado, e é o único membro), confira que o sinal dele é o
   `UX-005` já na admissibilidade — e não o `UX-064`.

---

## 3 — O Cronograma deixa de produzir alarme (`SC-271`, `FR-735` a `FR-739`)

1. Como **Gestor**, abra o Processo.

**Esperado**: **nenhum** sinal de Cronograma. Hoje o seed produz `UX-002` (os Eventos do segundo
Edital já passaram, e estão `PLANEJADO`) e `UX-001` (as Etapas *Análise de títulos* e *Análise
documental* não têm Evento).

2. Leia os próximos marcos do pulso.

**Esperado**: nenhum *"declarado planejado"*; o marco em curso diz *em andamento* (`UX-088`).

3. Abra a página do segundo Edital, publicado.

**Esperado**: em *Validação do conteúdo*, um **Aviso** — não *Impede* — para cada Etapa sem Evento,
nomeando a Etapa (`UX-086`).

4. Crie um Edital a partir do anterior e vá à Revisão antes de submeter.

**Esperado**: o mesmo aviso, e a submissão continua possível.

5. **Pela API do rascunho**, tente gravar um Evento com `status` `EM_ANDAMENTO`.

**Esperado**: recusa, com a razão. `CANCELADO` continua aceito, e um Evento cancelado com datas em
curso não aparece como *em andamento* em superfície nenhuma.

---

## 4 — O sinal que fica diz o que conta e a quem pedir (`SC-272`, `SC-273`, `FR-740` a `FR-743`)

1. Refaça a medição de 20/09: como **Gestor**, conte os sinais e, para cada um, se tem caminho ou diz
   a quem pedir.

**Esperado**: **zero** sinais mudos. Eram 9 de 15.

2. Num Edital com `UX-046`, como **Gestor** (sem a permissão de retificar).

**Esperado**: sem caminho, e com a frase *"A Retificação depende da permissão de retificar. Peça a
alguém com a permissão de retificar que a proponha."* Como **Elaborador**: o caminho, e **não** a
frase.

3. Repita com **Auditor**, **Julgador** e **Publicador**: para cada sinal que cada um vê e cujo ato
   não pratica, a frase está no sinal ou na tela a que ele leva.
4. Encerre um Edital com `UX-046`.

**Esperado**: o sinal sai da Atenção — ninguém pode retificar um Edital encerrado.

5. Numa Etapa com uma inscrição eliminada na Etapa anterior, como **presidência**, compare o
   `UX-003` do painel com a tela de distribuição e clique no número *"sem avaliador suficiente"*.

**Esperado**: o denominador do painel é o número de participantes da tela; o número clicado e a
lista que ele abre têm o **mesmo** tamanho, inclusive quem não tem avaliador nenhum.

6. Leia toda medida exibida.

**Esperado**: cada uma diz a unidade — *inscrições*, *recursos*, *recortes*.

---

## 5 — O que não pode quebrar

- **Processo e Supervisão dizem a mesma coisa** do mesmo Edital, inclusive a frase de ausência
  (`038`, `FR-557`).
- **Ator sem espécie nenhuma** continua sem a região da Atenção.
- **O catálogo** tem oito espécies, e o requisito que o fecha (`FR-744`) nomeia as oito.
