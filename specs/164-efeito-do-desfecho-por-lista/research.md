# Research: O efeito do desfecho da Etapa por lista

As decisões de produto estão na spec (`D-001` a `D-011`). Aqui ficam as técnicas, `T-NNN`, cada uma
com o que foi escolhido, por quê e o que foi descartado. Os caminhos são relativos a
`backend/processo_seletivo/`, sobre a branch da `163` (`claude/163-alcance-da-etapa`).

## T-001 — Duas colunas de texto na Etapa, com o vazio dizendo "não declarado"

**Decisão.** `EtapaAvaliacao` ganha duas colunas:

- `efeito_desfavoravel`, com `""`, `RETIRA_DA_RESERVA` ou `ELIMINA`;
- `efeito_da_ausencia`, com `""` (*"o mesmo efeito"*), `RETIRA_DA_RESERVA` ou `ELIMINA`.

As duas são `CharField` com `choices` e `CheckConstraint`. A migration é `editais/0030`, aditiva, e
toda linha existente fica `""`.

**Por quê.** São escolhas fechadas, que só se leem junto da Etapa, e a gravação do rascunho recria
as Etapas a cada `replace_draft`. O `""` do rascunho é o *"não declarado"* que a FR-7001 manda ler
como **retira** na Etapa restrita e eliminatória. Por isso a coluna não precisa de padrão de
domínio: o padrão é aplicado na leitura do rascunho e na publicação, onde a Etapa é conhecida
inteira.

**Descartados.**

- `BooleanField` "retira da reserva": não diria *"não declarado"*, e a ausência pede três estados.
- Uma coluna só com quatro valores combinados: ilegível na Retificação, que mostra campo a campo.

## T-002 — `unfavorableOutcomeEffect` e `absenceEffect` no conteúdo publicado, degrau 23

**Decisão.** Cada item de `stages` ganha dois campos:

- `unfavorableOutcomeEffect`: `null`, `"RESERVE_REMOVAL"` ou `"ELIMINATION"`;
- `absenceEffect`: `null` (o mesmo efeito), `"RESERVE_REMOVAL"` ou `"ELIMINATION"`.

`SCHEMA_VERSION` vai a 23, e `DEGRAUS[23] = {"unfavorableOutcomeEffect": None, "absenceEffect":
None}`.

A publicação grava o efeito **explícito** só na Etapa restrita e eliminatória: o declarado, ou
`RESERVE_REMOVAL` quando o rascunho não declarou. Em toda outra Etapa grava `null`.

**A leitura.** `unfavorableOutcomeEffect` nulo numa Etapa restrita e eliminatória é conteúdo de antes
do degrau 23, e é lido como `ELIMINATION` (D-002). Como a publicação nova nunca grava nulo nessa
Etapa, o nulo nela só vem do acervo.

**Por quê.** Conversão sem invenção, no molde dos degraus 17, 21 e 22. O resumo canônico do acervo
não muda (SC-2330): o degrau acrescenta `null` às Etapas, e o resumo é calculado sobre o conteúdo
como foi publicado.

## T-003 — Um módulo puro, `resultados/domain/efeito.py`

**Decisão.** Funções puras sobre a Etapa do conteúdo publicado:

- `efeito_desfavoravel(etapa)` → `RETIRA_DA_RESERVA`, `ELIMINA` ou `None`. Devolve `None` na Etapa que
  não declara: a que alcança todas, ou a não eliminatória. Na restrita e eliminatória, o nulo vira
  `ELIMINA`.
- `efeito_da_ausencia(etapa)` → o explícito, ou o do desfavorável.
- `consequencia_do_efeito(efeito)` → `RETIRADA_DA_RESERVA` ou `ELIMINADA`.
- `GRAVIDADE = {HABILITADA: 0, RETIRADA_DA_RESERVA: 1, ELIMINADA: 2}`, `mais_grave(a, b)`.
- `desfavoravel(consequencia)` → `RETIRADA_DA_RESERVA` ou `ELIMINADA`.
- `frase_do_efeito(conteudo, etapa)` → a frase do documento e da Revisão, ou `""`.

**Por quê.** A consolidação, a Ocorrência, o recurso, a Retificação e as telas fazem a mesma
pergunta. Uma resposta só impede que divirjam. `regra.py` continua sendo a tabela-verdade da
consequência e passa a pedir o efeito aqui.

## T-004 — A terceira consequência, `RETIRADA_DA_RESERVA`

**Decisão.** `ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA = "RETIRADA_DA_RESERVA"`, com 19
caracteres, que cabem no `max_length=20` de `PosicaoNaOrdem.consequencia`. Duas migrations trocam
as constraints:

- `resultados/0007`: `ck_resultado_consequencia` passa a três valores;
- `recursos/0004`: `ck_decisao_consequencia` passa a quatro, com o vazio.

**Por quê.** É a D-003. As constraints existem porque o registro é append-only (comentário em
`resultados/models.py`). Ampliá-las é a mudança mínima, e o `M` da preparação do banco não muda,
porque nenhuma tabela nova é protegida.

## T-005 — A regra da consequência lê o efeito

**Decisão.** Três pontos passam a ler o efeito:

- `regra._consequencia_decisoria` e o ramo eliminatório da forma pontuada trocam `ELIMINADA` por
  `consequencia_do_efeito(efeito_desfavoravel(etapa) or ELIMINA)`.
- O motivo da retirada cita o rótulo publicado e a reserva. A reserva é dita pela Modalidade da
  inscrição, e por isso a frase completa é montada por quem conhece a inscrição: a consolidação e a
  Ocorrência acrescentam *"deixa de concorrer pela reserva «nome» e continua na ampla
  concorrência"*.
- `ocorrencia.registrar` usa `consequencia_do_efeito(efeito_da_ausencia(etapa))` na Etapa restrita, e
  `ELIMINADA` nas demais. O motivo diz que o fundamento é a ausência.

**Por quê.** FR-7007 e FR-7009. O recurso (`recursos/domain/consequencia.derivar`) já chama a mesma
`regra.consequencia` pela versão citada, e herda o efeito sem código novo. É a FR-059 da `018`: a
consequência é derivada, e nunca digitada.

## T-006 — A progressão: a retirada satisfaz a exigência de habilitação

**Decisão.** Em `resultados/application/prontidao.py`, a Regra 2 passa a ler
`consequencia__in=(HABILITADA, RETIRADA_DA_RESERVA)` nas três funções: `restringir_a_participantes`,
`participa_da_etapa` e `participacao_detalhada`. A Regra 1 continua lendo só `ELIMINADA`.

**Por quê.** FR-7011 e D-004. A mudança cabe no `Exists` que já existe, e não custa consulta nova.

## T-007 — A faixa do corte conta a retirada só pela ampla

**Decisão.** `_dentro_da_faixa` ganha as Etapas anteriores e passa a ser:

```text
~Exists(faixa do Perfil)
| Exists(PROGREDIU na faixa da ampla)
| (Exists(PROGREDIU na faixa da Modalidade) & ~Exists(RETIRADA vigente nas anteriores))
```

Quando nenhuma Etapa anterior é restrita, o terceiro `Exists` não é montado, e a consulta é a de
hoje.

**Por quê.** FR-7013. Fica na mesma subconsulta correlacionada, sem consulta a mais, e por isso os
orçamentos da `011`, da `012` e da `015` continuam valendo.

## T-008 — A ordem: a lista reservada exclui ou deixa sem posição

**Decisão.** São três mudanças:

- Em `classificacao/application/calculo.py`, quando o recorte é reservado, o universo exclui a
  inscrição com `RETIRADA_DA_RESERVA` vigente em Etapa de `order` **menor** que a última enumerada.
  É um `~Exists` a mais, só no recorte reservado. O mesmo vale em `listas_sem_concorrente`, que
  pergunta por Modalidade.
- Em `universo_classificavel.preparar`, com `recorte` não nulo, a retirada numa Etapa enumerada conta
  como a eliminação conta: sem posição, com a consequência e o motivo dela. Com `recorte` nulo, a
  ampla, ela é ignorada.
- `reproducao.py` repete a mesma regra, como hoje repete a da eliminação.

**Por quê.** FR-7012 e D-005. A exclusão da anterior e o sem posição da enumerada são exatamente o
par que a eliminação já tem: o `restringir_a_participantes` do universo e o
`_eliminacao_mais_recente`.

**Descartado.** Ler a retirada no `restringir_a_participantes` do universo, que é comum aos
recortes: a ampla perderia a inscrição.

## T-009 — Ocupação, fila, situação da vaga e acréscimo: a subtração na reserva

**Decisão.** `ocupacao/application/selectors.habilitadas_pelo_corte` ganha a subtração. Quando
`corte.lista_id` não é nulo, ela tira do conjunto as inscrições com `RETIRADA_DA_RESERVA` vigente em
Etapa até o horizonte:

- `order` menor que a da Etapa governada, quando o corte governa uma;
- `order` até a última enumerada, quando o corte declara não governar Etapa.

**Por quê.** FR-7014. A apuração (`emissao.py`), a destinação (`destinacao.py`, da `155`), o
acréscimo e a fila (`convocacao/application/selectors.py`) chamam todos `habilitadas_pelo_corte`.
Tirar a inscrição do *habilitadas*, e não da *sequência*, é o mesmo tratamento que a inscrição
eliminada na Etapa governada recebe hoje: ela continua no lugar da faixa, não ocupa e não é
chamada. A faixa não se reabre (FR-7015).

**Descartados.**

- Tirar a inscrição de `progrediram_em_ordem`. Isso mudaria quem é titular inicial e anteciparia o
  seguinte, ou seja, reabriria a faixa.
- Filtrar em cada um dos quatro consumidores: seriam quatro cópias da mesma regra.

## T-010 — O sorteio: a relação de habilitados da reserva

**Decisão.** `sorteios/application/habilitacao.habilitadas_na_etapa` ganha `lista_id`. Na lista
reservada, ela subtrai a inscrição com `RETIRADA_DA_RESERVA` vigente em Etapa de `order` menor que a
Etapa de habilitação. A relação (`relacao._habilitadas`) e a prévia (`previa.py`) passam a lista.
Sem Etapa de habilitação, nada muda, porque a eliminação de hoje também não chega à relação.

**Por quê.** Na Etapa de habilitação, a progressão manda a inscrição retirada como `HABILITADA`. A
relação a poria no sorteio da reserva. É o caso do marco terminal da FR-7014, e por isso a spec
ganhou a **FR-7030**.

## T-011 — O recurso: gravidade na vedação de piora

**Decisão.** São duas mudanças:

- `recursos/domain/pejus.piora` passa a comparar por `GRAVIDADE`: piora quando a consequência nova é
  mais grave que a protegida; com a mesma consequência, decide a pontuação, como hoje. A consolidação
  em cumprimento de reavaliação (`consolidacao.py:188`) usa a mesma função e herda a regra (FR-073 da
  `018`).
- O ramo da Ocorrência (`julgar._conclusao`, protegido sem forma) continua produzindo `HABILITADA`:
  *"a ocorrência não subsiste"*.

**Por quê.** FR-7028 e FR-7029. A reavaliação contra ausência produz Resultado por avaliação, e a
regra aplica o efeito do desfavorável, sem código novo.

**Refinamento da spec.** Na `018`, a decisão não escolhe a consequência: ela fixa a conclusão, e a
regra deriva a consequência (FR-059 da `018`). O cenário da US4 em que *"a decisão fixa retirada"*
contra a eliminação por ausência não existe nesse mecanismo. Ele foi trocado pelo que existe: a
correção contra Ocorrência habilita, e a retirada só vem pela reavaliação. A FR-7019 foi reescrita
no mesmo sentido.

## T-012 — A Retificação: o impedimento histórico

**Decisão.** `publicacoes/application/retificacoes.py` ganha `_recusar_efeito_mudado_apos_desfavoravel`,
no molde da recusa de estreitar o alcance da `163`. A função:

- compara, Etapa a Etapa, o efeito **efetivo** (`efeito_desfavoravel` e `efeito_da_ausencia`, já
  resolvidos) entre a base e o conteúdo novo;
- havendo diferença, conta `ResultadoEtapa.objects` (e não `vigentes`) daquela Etapa com
  consequência `RETIRADA_DA_RESERVA` ou `ELIMINADA`;
- havendo ao menos um, recusa com `DomainError("stage_effect_changed_after_unfavorable", ..., 422)`.

Roda na gravação e de novo na publicação, sob o bloqueio do Edital.

**Por quê.** FR-7020 e D-008. `objects` é deliberado: o impedimento é histórico, e é a única leitura
de efeito que **não** usa `vigentes`. A varredura `test_vigencia_do_resultado.py` ganha a exceção
nomeada.

**Serialização (FR-7022).** A consolidação e a Ocorrência já bloqueiam o Processo
(`comando_de_comissao`). A publicação da Retificação passa a reler o efeito sob o mesmo bloqueio.

## T-013 — A validação de publicação

**Decisão.** Em `editais/domain/validation.py`, o achado `BLOCKING_ERROR` `efeito_sem_reserva`
(FR-7002) dispara quando a Etapa declara `RESERVE_REMOVAL` num dos dois efeitos e alcança todas, ou
quando não é eliminatória. `validate_stage` recusa, na gravação, o valor fora das escolhas.

## T-014 — Documento, Revisão, página pública e Retificação

**Decisão.** `frase_do_efeito` (T-003) devolve `""` para a Etapa sem declaração. Para a Etapa que
declara, devolve uma frase só quando os dois efeitos coincidem:

- *"O candidato com resultado desfavorável ou que não comparecer deixa de concorrer pela reserva de
  vagas e continua concorrendo pela ampla concorrência."*
- *"O candidato com resultado desfavorável ou que não comparecer é eliminado do processo seletivo."*

Quando diferem, uma frase para cada caso.

As três redações a usam como a frase do alcance da `163`: a redação 1, como par *"Efeito"*; a 2 e a
3, como frase depois da do alcance.

`CAMPOS_ETAPA` (`interface/retificacao.py`) ganha os dois campos. A composição ganha o grupo, que o
`alcance.js` da `163`, estendido, mostra só na Etapa restrita e eliminatória (CSP: arquivo
estático).

## T-015 — O que o candidato e a gestão leem

**Portal.**

- `resultados/application/selectors` passa `"retirada"` ao lado de `"habilitada"`.
- Em `portal/situacao.situacao_da_inscricao`, as eliminações deixam de contar a retirada.
- Uma linha `Linha` da retirada entra no *porquê* dos degraus de classificação, com o texto da
  UX-742.
- O cartão da lista reservada lê a consequência gravada em `SituacaoDivulgada` e diz *"Deixou de
  concorrer por esta lista"*.

**Gestão.**

- O relatório do Edital conta `RETIRADA_DA_RESERVA:avaliacao` e `:ocorrencia` à parte.
- `resultados.html` ganha o filtro e o rótulo.
- A confirmação da consolidação conta retiradas e eliminações antes de confirmar (UX-743).
- `conferencia_da_ordem` mostra o rótulo da consequência.

## T-016 — O guardião da FR-7018

**Decisão.** Um teste novo, `tests/test_leitores_da_consequencia.py`, varre `backend/processo_seletivo`
atrás de toda leitura da consequência, literal ou pelo enum, e exige que o arquivo esteja num
inventário com a classificação dele. As classificações são:

- **trata as três**;
- **não alcança Etapa restrita**, com o motivo: Etapa governada, Etapa de habilitação ao sorteio ou
  Etapa de análise das inscrições;
- **só habilitada importa**.

Leitor novo, fora do inventário, reprova.

**Por quê.** SC-2335. É o defeito silencioso que a D-003 aponta: um leitor esquecido elimina sem
ninguém ver.

## T-017 — O que não muda, e por quê

- **Regularização da convocação** (`convocacao/application/fluxo.py`, `desfechar.py`): opera sobre a
  Etapa governada, que nunca é restrita.
- **Publicação das inscrições** (`divulgacao/application/inscricoes.py`): a Etapa de análise nunca é
  restrita (regra da `163`).
- **`destinacao.py:263`** (eliminados na Etapa governada) e **`reabilitados_por_deferimento`** (Etapa
  governada).
- **`reabilitadas_por_recurso`**: a retirada que vira habilitada aparece como reabilitação. A guarda
  de publicação da `018` só bloqueia quem não tem Resultado numa Etapa enumerada, e a inscrição
  retirada seguiu as Etapas, de modo que não muda nada.
- **Prévia da classificação e do sorteio**: não simulam retirada (FR-7026).
- **Avisos complementares** (`066`): fora do escopo.
