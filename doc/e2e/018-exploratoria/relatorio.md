# Auditoria exploratória E2E — Recursos e Superação de Resultados (018)

## 1. Resumo executivo

O ciclo administrativo **fecha para três das quatro espécies de decisão**. Foi possível, só pelo navegador, publicar um resultado preliminar, ver o candidato consultá-lo, interpor recurso, admitir, julgar nas quatro espécies, produzir a superação append-only do `ResultadoEtapa`, reabilitar quem tinha sido eliminado numa Etapa anterior, fazê-lo progredir retroativamente, tornar a classificação obsoleta, emitir o ato sucessor e republicar — com a publicação anterior preservada e a Área do Candidato acompanhando cada passo.

As três decisões que ficaram pendentes antes da spec foram implementadas e verificadas:

- **A — definitividade** deixou de ser escolha livre. É porta de fato verificável: recurso pendente, reingresso pendente, reavaliação pendente, providência pendente e janela aberta. Testada e recusando.
- **B — resultado de Etapa ao candidato** foi entregue. Helena, eliminada na Etapa 1 e fora de qualquer marco, agora vê "Analise de requisitos — Eliminada — a avaliação concluiu Indeferida" na própria inscrição.
- **C — superação append-only** foi entregue. O Resultado corrigido nasce como linha nova citando a anterior, com motivo; a linha original permanece intacta no banco.

**O achado que impede o fechamento é um só, e é grave.** A espécie `REAVALIACAO_DETERMINADA` — "deferir determinando reavaliação" — **não tem como ser cumprida pela interface**. A decisão determina que a Etapa reavalie; a única forma de produzir a nova avaliação é reabrir a conclusão; e a reabertura é recusada, por regra da 013, exatamente porque aquela avaliação fundamenta um Resultado consolidado. A recusa orienta a usar o julgamento de recurso — que é o que acabou de acontecer, e cuja espécie escolhida, por desenho, não cria sucessor. Como a reavaliação pendente é um dos fatos que barram a definitiva, o marco fica **permanentemente impedido de chegar a resultado definitivo**.

Os outros quatro cenários passaram: indeferimento sem efeito, correção direta com R1→R2, reabilitação com progressão retroativa, e a porta da definitividade recusando em duas situações distintas.

> **Segunda passada (§9).** Os quatro cenários que faltavam foram exercidos depois. Três passaram —
> impedimento do julgador, *non reformatio in pejus* e a quarta espécie de decisão. O quarto revelou
> um segundo P1: **a janela recursal declarada no Edital nunca chega ao conteúdo publicado**
> (E2E18-005), o que também retrata o achado E2E18-002 da primeira passada.
>
> **Corrigido depois desta auditoria.** O E2E18-005 foi fechado pelo PR #51 (commit `ae97f5d`), e
> com ele o cenário da janela — antes não observável — passou a ser verificável e foi verificado
> (§9). Resta aberto o **E2E18-001**, que é decisão de desenho. O corpo dos achados preserva o que
> foi observado; o estado de cada um vem ao fim da respectiva seção.

---

## 2. Ambiente e base

| item | valor |
|---|---|
| commit | `368d9cd` (merge do PR #50 — SPEC 018) |
| banco | PostgreSQL local `ps018_audit`, criado vazio e migrado |
| servidor | `runserver` :8188, seletor de identidade ligado |
| ferramentas | Playwright (Chromium), mailpit, `psql` para as provas de banco |
| screenshots | **52** (41 na primeira passada, 11 na segunda) |
| candidatos | 6 |
| recursos | 6 (quatro na primeira passada, dois na segunda) |
| publicações | 2 (P1 preliminar, P2 preliminar sucessora) |
| atos de ordenação | 2 (C1, C2) |

**Atores:** `elena.elaboradora`, `wagner.homologador`, `paula.publicadora`, `gustavo.gestor`, `paulo.presidente`, `alice.avaliadora`, `otavio.avaliador`, **`julia.julgadora`** (papel `julgador`, exclusivo de `recurso:julgar`) e seis candidatos. Sem superusuário.

**Preparação fora do produto:** banco vazio, seletor de identidade, mailpit, dois PDFs fictícios. Nada do domínio.

**Cenário:** Edital 03/2026 — Auxiliar de Biblioteca. Duas Etapas (decisória e pontuada, nota mínima 60), marco `FINAL` **declarando que admite recurso em 5 dias**, um critério de desempate por fato declarado.

---

## 3. Escopo executado

| Fase | Executada | Resultado | Evidência |
|---|---|---|---|
| Edital com janela de recurso declarada no marco | sim | ok | `01`, `02` |
| 6 inscrições, comissão, distribuição | sim | ok | `03`, `04` |
| Avaliação decisória e pontuada, consolidação | sim | ok | `05`–`07` |
| Classificação C1 e **publicação preliminar P1** | sim | ok | `08`, `09` |
| Candidato consulta resultado (classificado e eliminado) | sim | ok | `10` |
| **Cenário 5a — definitiva com recurso pendente** | sim | **recusada** | `13` |
| Interposição (4 recursos, com protocolo) | sim | ok | `11`, `12` |
| Admissibilidade | sim | ok | `16` |
| **Cenário 1 — indeferido** | sim | **nada mudou** | `17` |
| **Cenário 2 — correção fixada (R1→R2)** | sim | **82 → 90** | `18`, `21` |
| **Cenário 3 — reavaliação determinada** | sim | **sem caminho de cumprimento** | `19`, `27`, `30` |
| **Cenário 4 — reabilitação e progressão retroativa** | sim | **ok, e bloqueia publicação** | `20`, `22`, `24`, `28` |
| Classificação obsoleta por superação | sim | ok | `23` |
| Ato sucessor C2 e republicação P2 | sim | ok | `31`, `33` |
| **Cenário 5b — definitiva com reavaliação pendente** | sim | **recusada** | `32` |
| P1 preservada após sucessão | sim | ok | `34` |
| Área do Candidato nas 4 situações | sim | ok | `36` |
| Superação append-only no banco | sim | **provada** | — |
| *Non reformatio in pejus* (2ª passada) | sim | **recusada, sem gravar nada** | `38`, `39` |
| Impedimento do julgador, FR-039 (2ª passada) | sim | **recusado** | `37` |
| `PROVIDENCIA_A_JUSANTE` (2ª passada) | sim | julgada, sem sucessor | `40`, `41` |
| Janela recursal aberta (2ª passada) | **provada após a correção** | barra a definitiva | `43`–`47` |

---

## 4. Jornada observada

P1 preliminar publicada com **1º Ana 95 · 2º Bruno 88 · 3º Carla 82 · 4º Diego 75**, Elisa eliminada por nota e Helena fora do universo (eliminada na Etapa 1).

Quatro recursos interpostos pela Área do Candidato, cada um com protocolo próprio (`REC-2026-…`). Admitidos com motivo. Julgados:

| candidato | espécie | efeito observado |
|---|---|---|
| Bruno | Indeferir | nenhum sucessor; resultado segue 88 |
| Carla | Deferir fixando a correção | sucessor 90 citando o anterior e a decisão |
| Diego | Deferir determinando reavaliação | nenhum sucessor — e **nenhum caminho para produzi-lo** |
| Helena | Deferir fixando a correção (Etapa decisória) | Eliminada → Habilitada; volta à Etapa 2 |

A classificação ficou obsoleta com o motivo certo — *"Os Resultados oficiais do universo mudaram: resultado superado por recurso"* — e a publicação foi **bloqueada mesmo como preliminar** enquanto Helena não tivesse Resultado na Etapa seguinte: *"Há inscrição reabilitada por recurso cujo resultado ainda não foi consolidado numa Etapa que este marco enumera."*

Cumprida a reabilitação, C2 foi emitido: **1º Ana 95 · 2º Carla 90 · 3º Bruno 88 · 4º Diego 75 · 5º Helena 70**. A definitiva foi recusada pela reavaliação pendente do Diego; a preliminar sucessora foi publicada, e P1 permaneceu consultável dizendo que foi sucedida.

---

## 5. Invariantes verificados

| Invariante | Resultado | Evidência |
|---|---|---|
| superação é append-only: linha nova citando a anterior | ✅ | banco: `aee50c8f` (82) ← `cfed1106` (90) e `4ae275dd` (Eliminada) ← `d0ae0268` (Habilitada), originais intactos |
| indeferimento não produz efeito | ✅ | Bruno segue 88, "SUCESSOR: Nenhum" (`17`) |
| correção fixada produz exatamente um sucessor, com motivo | ✅ | *"Resultado corrigido em cumprimento da decisão … no recurso REC-2026-MPP5E486"* |
| reabilitação faz progredir retroativamente | ✅ | Helena reaparece na Mesa da Etapa 2 como "Não iniciada" (`28`) |
| reingresso pendente bloqueia **até o preliminar** | ✅ | CTA ausente e recusa nominal (`24`) |
| definitiva exige fato: recurso pendente barra | ✅ | recusa com próximo passo (`13`) |
| definitiva exige fato: reavaliação pendente barra | ✅ | recusa com próximo passo (`32`) |
| julgador impedido não julga (FR-039) | ✅ | tela sem ações e `POST` → 403 (`37`) |
| recurso não agrava quem recorre (FR-070) | ✅ | recusa total, sem decisão nem sucessor (`39`) |
| definitiva sem prazo declarado exige declaração escrita | ✅ | recusada sem, aceita com (`45`, `46`) |
| **janela recursal chega ao conteúdo publicado** | ✅ **após o PR #51** | `appealWindow` com o prazo no snapshot; antes dele, **E2E18-005** |
| janela aberta barra a definitiva | ✅ | *"O prazo recursal deste marco ainda está aberto: ele se encerra em 12/09/2026 às 23h59"* (`47`) |
| classificação fica obsoleta por superação | ✅ | motivo nomeia o recurso (`23`) |
| publicação anterior preservada | ✅ | P1 mantém `3º Carla 82,00` e avisa que foi sucedida (`34`) |
| candidato vê o próprio recurso e o efeito | ✅ | "Seus recursos" + motivo da correção na inscrição (`36`) |
| julgar é papel próprio, não derivado | ✅ | presidência, gestão, elaboração e auditoria recusadas; só `julgador` entra (`14`, `15`) |
| **reavaliação determinada é cumprível** | ❌ | **E2E18-001** |

---

## 6. Achados

### E2E18-001 — A reavaliação determinada não tem como ser cumprida, e trava a definitiva para sempre

**Severidade:** P1 · **Tipo:** domínio / funcional · **Features:** 012–013–018 · **Ator:** Presidência, Julgador

**Observado.** Julgado o recurso do Diego como *"Deferir determinando reavaliação"*, a decisão foi registrada e a tela da Etapa passou a exibir corretamente *"reavaliação determinada por recurso, ainda não cumprida — Otavio Oliveira"*. Para produzir a nova avaliação, a presidência foi a **Conclusões preservadas** e pediu a reabertura, que é o caminho que a própria tela indica. A reabertura foi **recusada**:

> Esta avaliação fundamenta o Resultado da Etapa Avaliacao de titulos para a inscrição INS-2026-8HCQF32J (Resultado …) e não pode ser reaberta. Corrigir um Resultado consolidado é ato de outra natureza: o julgamento de recurso o supera por um Resultado novo, sem alterar este.

A orientação da recusa é circular: o julgamento de recurso **já aconteceu**, e a espécie escolhida é justamente a que, por desenho, não cria sucessor. A peça do recurso não oferece nenhuma ação de cumprimento ("AÇÕES: Sair"). Não há rota, botão ou tela em `interface/` que cumpra uma reavaliação.

**Esperado.** Que a decisão que determina reavaliar abra o caminho para reavaliar — reabrindo a avaliação protegida, criando uma nova atribuição, ou qualquer via explícita.

**Impacto.** Duplo, e o segundo é o grave:

1. A decisão é **inexequível**: o candidato lê "Recurso deferido — a etapa será reavaliada" e nada acontece, nunca.
2. Como reavaliação pendente é um dos fatos que barram a definitiva, o marco fica **permanentemente impedido** de chegar a resultado definitivo. A recusa da definitiva instrui *"Conclua a reavaliação, consolide o resultado e emita o ato sucessor"* — três passos, e o primeiro é impossível.

**Reprodução.** Julgar qualquer recurso como `REAVALIACAO_DETERMINADA` sobre Etapa já consolidada; tentar reabrir em Conclusões preservadas; tentar publicar definitiva.

**Evidência.** `19-julgamento-reavaliacao.png`, `27-reabertura-para-reavaliacao.png`, `30-recurso-reavaliacao-sem-caminho.png`, `32-definitiva-bloqueada-por-reavaliacao.png`.

**Causa confirmada no código.** A guarda em `avaliacoes/application/avaliacao.py` recusa a reabertura sempre que existir `ResultadoEtapa` ligado à avaliação, **sem exceção para reavaliação determinada** — e o comentário mostra que a 018 editou exatamente essa mensagem (FR-111) sem abrir a via. Do outro lado, `julgar.py` documenta para a espécie: *"nenhum sucessor; a decisão declara o efeito e cita o Resultado protegido"*. E `recursos/application/selectors.py::reavaliacoes_pendentes` define cumprimento como *"a existência de um sucessor do Resultado protegido"*. As três peças são coerentes entre si e não se encontram: quem deve criar o sucessor não tem por onde.

- **Estado (07/09/2026):** **aberto**. É o único ponto em que o ciclo da 018 não fecha, e depende
  de decisão de governança — não entrou no hardening do E2E18-005.

**Recomendação.** É decisão de desenho, não conserto óbvio. As saídas visíveis: (a) a decisão da espécie autorizar a reabertura daquela avaliação específica, nominalmente; (b) a decisão criar a atribuição de reavaliação, sem reabrir a conclusão antiga; (c) retirar a espécie do produto enquanto não houver via. O que não pode permanecer é a espécie ofertada no seletor sem caminho de cumprimento.

---

### E2E18-002 — ~~Recurso contra Resultado de Etapa nasce "sem prazo computável"~~ → RETRATADO

**Retratação (segunda passada).** O achado **não procede como foi escrito**. A causa de todos os
recursos aparecerem com "Sem prazo computável" não é o objeto atacado ser Resultado de Etapa: é que
**nenhum dos Editais chegou a publicar a janela recursal**, por causa do defeito descrito em
E2E18-005. Com a janela ausente do conteúdo publicado, nenhum recurso teria prazo computável,
qualquer que fosse o objeto. A hipótese que registrei na primeira passada foi construída sobre um
sintoma cuja causa eu ainda não conhecia. O número é preservado para as citações anteriores.

### E2E18-003 — A peça mostra identificadores técnicos onde quem julga lê significado

**Severidade:** P3 · **Tipo:** conteúdo / legibilidade · **Features:** 018 · **Ator:** Julgador

**Observado.** Na peça: `INTERPOSTO POR — cand:745c4cc1c91249428f9a5ad26f4f41ce`, `IDENTIDADE DO OBJETO — aa0aacff-…`, `VERSÃO CONSOLIDADA CITADA — 10a8a002-…`. O nome do candidato aparece logo abaixo, então não há ambiguidade — mas o campo "interposto por" é o único que responde "quem", e responde com um opaco.

**Impacto.** Menor que o equivalente da 015 porque o contexto é administrativo e os dados corretos estão na mesma tela. Ainda assim é a peça que instrui a decisão.

**Evidência.** `15-peca-do-recurso.png`.

---

### E2E18-004 — Comentário desatualizado sobre a janela na porta da definitividade

**Severidade:** P3 · **Tipo:** consistência · **Ator:** — (código)

**Observado.** O docstring de `_impedimento_da_definitiva` diz *"O quarto fato — janela aberta — é do degrau 8, e entra quando ele existir"*, e a função chama `_janela_aberta` seis linhas abaixo. O comentário descreve um estado anterior do código.

**Impacto.** Nenhum em runtime; custo de leitura para quem for mexer na porta.

---

## 7. Severidade

| Sev. | Qtde | Achados |
|---|---|---|
| P0 | 0 | — |
| P1 | 2 | 001 **aberto** · 005 — **corrigido** no PR #51 (`ae97f5d`) |
| P2 | 0 | — |
| P3 | 2 | 003, 004 |
| — | 1 | 002 (retratado na segunda passada) |

Aberto de fato, hoje: **um P1** (E2E18-001) e dois P3.

---

## 8. Regressões e decisões fechadas desde a auditoria da 017

| Item | Estado | Como verifiquei |
|---|---|---|
| **E2E17-001** — Edital publicado sem período de inscrições | ✅ **corrigido** | compus o Edital na **ordem natural** do assistente, sem contorno, e as inscrições abriram; `eventos_persistidos()` passou a emitir `status` e `isRegistrationPeriod`, com teste de round-trip que também cobre `status` |
| **E2E17-003** — UUID e data em inglês | ✅ **corrigido** | `LANGUAGE_CODE = "pt-br"` presente; a coluna MODALIDADE da ordenação mostra "Ampla concorrencia" |
| **E2E17-004** — eliminado cedo sem notícia | ✅ **corrigido (decisão B)** | Helena vê "Resultado das etapas — Analise de requisitos — Eliminada" |
| **E2E17-005** — definitiva por escolha livre | ✅ **corrigido (decisão A)** | porta de fato, com cinco impedimentos distintos; duas recusas observadas |
| **Decisão C** — superação do `ResultadoEtapa` | ✅ **implementada** | append-only, linha nova citando a anterior, constraint de unicidade movida para a raiz |
| Segregação de funções | ✅ sem regressão | julgar é papel próprio; presidência e gestão recusadas |
| Sucessão de publicação | ✅ sem regressão | P1 intacta e sinalizada |

Nenhuma regressão.

---

## 9. Segunda passada — os quatro cenários que faltavam

Executada logo após a primeira, no mesmo ambiente, com dois recursos novos (Ana e Elisa) e um
Edital mínimo criado só para isolar a janela.

| Cenário | Resultado | Evidência |
|---|---|---|
| **Impedimento do julgador (FR-039)** | ✅ **provado** | `37` |
| **Non reformatio in pejus (FR-070)** | ✅ **provado** | `38`, `39` |
| **`PROVIDENCIA_A_JUSANTE`** | ✅ julgada, sem sucessor, como especificado | `40`, `41` |
| **Janela recursal como quarto fato** | ✅ **provada** depois de corrigido o E2E18-005 | `43`–`47` |

**Impedimento.** `alice.avaliadora`, que produziu a nota atacada, recebeu o papel `julgador` e abriu
o recurso da Ana: *"Você não pode julgar este recurso. Aguardando apreciação por quem não esteja
impedido."* Sem ações na tela; `POST` direto em `/admitir` → **403**.

**Non reformatio.** Julgando o recurso da Ana como correção fixada com pontuação **80** (contra 95
vigentes): *"A correção proposta pioraria a situação de quem recorreu, e o recurso não pode
agravá-la. Nenhum resultado sucessor foi criado."* Conferido no banco: **nenhuma decisão gravada** e
nenhum sucessor novo — a atomicidade documentada em `julgar.py` (*"não fica decisão sem efeito, nem
efeito sem decisão"*) se manteve sob recusa. Vale registrar a distinção fina do domínio: `pejus.py`
trata como piora apenas perder a habilitação ou cair de pontuação — **queda de posição não é
piora**, porque corrigir o erro de A desloca B sem agravar A.

**Providência a jusante.** Registrada, sem sucessor, e passa a constar como pendência do marco. Não
chegou a barrar a definitiva porque a reavaliação do E2E18-001 barra antes — a ordem dos
impedimentos (recurso → reavaliação → providência → janela) foi observada na prática.

**Janela.** Na auditoria não foi possível observar o quarto fato: como nenhum Edital conseguia
publicar a janela (E2E18-005), a aferição caía sempre no ramo *"não declara prazo computável"*.
Esse ramo foi testado e funciona bem, com a saída prevista: um campo **Declaração de encerramento
do prazo recursal** aparece só na definitiva, a publicação é recusada sem ele e aceita com ele.

**Depois da correção**, o cenário foi refeito num Edital composto na ordem natural, e o quarto fato
recusou como especificado: *"O prazo recursal deste marco ainda está aberto: ele se encerra em
12/09/2026 às 23h59. Aguarde o encerramento, ou publique como resultado preliminar."* E o campo de
declaração escrita **desaparece** quando há prazo computável — a saída excepcional deixa de ser
oferecida quando a norma responde sozinha. Confirma-se que o quarto fato da porta da
definitividade estava implementado e correto o tempo todo: era o dado que nunca chegava até ele
(`47`).

---

## 10. Achado da segunda passada

### E2E18-005 — A janela recursal declarada no marco é apagada por qualquer gravação posterior

**Severidade:** P1 · **Tipo:** domínio / funcional · **Features:** 006–015–018 · **Ator:** Elaborador

**Observado.** No passo *Classificação*, declarei "Admite recurso, no prazo abaixo" com 5 dias. O
rascunho gravou corretamente: `janela_recursal = {"unit": "DIAS_CORRIDOS", "admits": true,
"durationDays": 5}`. Ao gravar **qualquer passo seguinte** — cronograma, inscrição, conteúdo —, o
valor volta a `{}`, e o Edital é publicado com `appealWindow: null`. Reproduzido em três Editais
independentes; nos três, `janela_recursal = {}` ao final.

**Esperado.** A declaração sobrevive até a publicação, como sobrevive a marca do período de
inscrições depois do E2E17-001.

**Impacto.** Nenhum marco chega ao conteúdo publicado com prazo recursal computável. Em
consequência: todo recurso nasce "Sem prazo computável" e a tempestividade recai inteiramente sobre
a admissibilidade humana; e a publicação definitiva **sempre** exige a declaração escrita de
encerramento, que foi desenhada para o caso excepcional do Edital que nada declarou. O documento
publicado agrava o quadro: a seção *9. DOS RECURSOS* diz *"Caberá recurso … nos casos e prazos que
este Edital declara para cada marco"* — remetendo a uma declaração que foi apagada em silêncio.

**Reprodução.** Compor marco com "Admite recurso, 5 dias" → gravar o passo *Inscrição* (ou
qualquer outro) → conferir `janela_recursal` no rascunho, ou `appealWindow` no snapshot publicado.

**Evidência.** `43`–`46`; `janela_recursal = {}` nos Editais 03, 04 e 99; `appealWindow = null` nos
snapshots.

**Causa confirmada no código.** `interface/forms.py::_marco_persistido()` serializa
`id, code, name, stages, operation, normalization, rounding, tiebreakers` — e **não**
`appealWindow`. Como `views._gravar_etapa()` reconstrói `profiles` a partir de
`perfis_persistidos()` em todos os passos, e `draft.py:287` faz
`janela_recursal=marco_payload.get("appealWindow") or {}`, a declaração é zerada na gravação
seguinte, sem recusa e sem aviso.

**É a mesma família do E2E17-001**, no serializador irmão que o hardening não alcançou: lá era
`eventos_persistidos()` omitindo `status` e `isRegistrationPeriod`; aqui é `_marco_persistido()`
omitindo `appealWindow`. O teste de round-trip existente cobre o cronograma e o conteúdo normativo
do Perfil, mas não desce ao marco.

**Recomendação.** Emitir `appealWindow` em `_marco_persistido()` e estender o teste de round-trip
ao marco — de preferência afirmando a igualdade do rascunho inteiro, e não campo a campo, para
fechar a classe em vez do caso.

- **Resolução (07/09/2026):** corrigido em `ae97f5d` (PR #51), e a correção encontrou **duas
  pontas** onde a auditoria via uma. Além de `_marco_persistido()`, o contrato de entrada da API —
  `editais/api/serializers.py::ClassificationMilestoneSerializer` — também não declarava
  `appealWindow`, de modo que nem por aquele canal a janela podia ser expressa. O teste de
  round-trip desceu ao marco no idioma que já usava para o Cronograma, comparando a coleção
  inteira, e foi conferido por mutação: revertendo apenas `_marco_persistido()`, ele falha.
  Verificado também no navegador — Edital composto na ordem natural publica
  `appealWindow = {"unit": "DIAS_CORRIDOS", "admits": true, "durationDays": 5}` — e o cenário da
  janela, antes bloqueado, foi então exercido com sucesso (§9).

---

## 11. Não exercido em nenhuma das passadas

- ~~**Janela recursal efetivamente aberta** barrando a definitiva~~ — **exercida e provada** depois
  da correção do E2E18-005 (§9).
- **Cumprimento de `PROVIDENCIA_A_JUSANTE`** por ato citante publicado.
- Recurso contra a **publicação** (todos os quatro atacaram Resultado de Etapa).

---

## 12. Evidências

`screenshots/` — 52 imagens na ordem da jornada, de `00-processo-criado.png` a
`47-janela-aberta-bloqueia-a-definitiva.png`. As de `37` em diante são da segunda passada.
