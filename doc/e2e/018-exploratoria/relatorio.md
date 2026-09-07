# Auditoria exploratória E2E — Recursos e Superação de Resultados (018)

## 1. Resumo executivo

O ciclo administrativo **fecha para três das quatro espécies de decisão**. Foi possível, só pelo navegador, publicar um resultado preliminar, ver o candidato consultá-lo, interpor recurso, admitir, julgar nas quatro espécies, produzir a superação append-only do `ResultadoEtapa`, reabilitar quem tinha sido eliminado numa Etapa anterior, fazê-lo progredir retroativamente, tornar a classificação obsoleta, emitir o ato sucessor e republicar — com a publicação anterior preservada e a Área do Candidato acompanhando cada passo.

As três decisões que ficaram pendentes antes da spec foram implementadas e verificadas:

- **A — definitividade** deixou de ser escolha livre. É porta de fato verificável: recurso pendente, reingresso pendente, reavaliação pendente, providência pendente e janela aberta. Testada e recusando.
- **B — resultado de Etapa ao candidato** foi entregue. Helena, eliminada na Etapa 1 e fora de qualquer marco, agora vê "Analise de requisitos — Eliminada — a avaliação concluiu Indeferida" na própria inscrição.
- **C — superação append-only** foi entregue. O Resultado corrigido nasce como linha nova citando a anterior, com motivo; a linha original permanece intacta no banco.

**O achado que impede o fechamento é um só, e é grave.** A espécie `REAVALIACAO_DETERMINADA` — "deferir determinando reavaliação" — **não tem como ser cumprida pela interface**. A decisão determina que a Etapa reavalie; a única forma de produzir a nova avaliação é reabrir a conclusão; e a reabertura é recusada, por regra da 013, exatamente porque aquela avaliação fundamenta um Resultado consolidado. A recusa orienta a usar o julgamento de recurso — que é o que acabou de acontecer, e cuja espécie escolhida, por desenho, não cria sucessor. Como a reavaliação pendente é um dos fatos que barram a definitiva, o marco fica **permanentemente impedido de chegar a resultado definitivo**.

Os outros quatro cenários passaram: indeferimento sem efeito, correção direta com R1→R2, reabilitação com progressão retroativa, e a porta da definitividade recusando em duas situações distintas.

---

## 2. Ambiente e base

| item | valor |
|---|---|
| commit | `368d9cd` (merge do PR #50 — SPEC 018) |
| banco | PostgreSQL local `ps018_audit`, criado vazio e migrado |
| servidor | `runserver` :8188, seletor de identidade ligado |
| ferramentas | Playwright (Chromium), mailpit, `psql` para as provas de banco |
| screenshots | **41** |
| candidatos | 6 |
| recursos | 4 (um por espécie de desfecho) |
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
| *Non reformatio in pejus* | **não** | não exercida | — |
| Impedimento do julgador (FR-039) | **não** | não exercido | — |

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

**Recomendação.** É decisão de desenho, não conserto óbvio. As saídas visíveis: (a) a decisão da espécie autorizar a reabertura daquela avaliação específica, nominalmente; (b) a decisão criar a atribuição de reavaliação, sem reabrir a conclusão antiga; (c) retirar a espécie do produto enquanto não houver via. O que não pode permanecer é a espécie ofertada no seletor sem caminho de cumprimento.

---

### E2E18-002 — Recurso contra Resultado de Etapa nasce "sem prazo computável"

**Severidade:** P2 · **Tipo:** domínio / governança · **Features:** 018 · **Ator:** Julgador

**Observado.** O marco declarou que admite recurso em 5 dias. Os quatro recursos — três contra Resultado de Etapa e um contra Resultado de Etapa decisória — aparecem na lista e na peça com **TEMPESTIVIDADE: Sem prazo computável**. A janela só é computável quando ancorada na publicação do marco.

**Esperado.** Não necessariamente um prazo: a ausência é coerente com o desenho declarado em `janela.py` (silêncio devolve a tempestividade ao juízo humano). O que surpreende é que o Edital **declarou** prazo e ele não alcança o objeto que o candidato de fato ataca.

**Impacto.** Na prática, o prazo publicado no Edital governa apenas o recurso contra a classificação; recursos contra Etapa ficam sem prazo algum, e a tempestividade recai inteira sobre a admissibilidade motivada. Isso é defensável, mas é uma decisão normativa que o produto toma em silêncio — e um Edital que promete "5 dias contados da divulgação" não distingue os dois casos.

**Evidência.** `14-lista-de-recursos.png`, `15-peca-do-recurso.png`.

**Recomendação.** Decisão de governança: ou a declaração do marco alcança os Resultados das Etapas que ele enumera, ou a tela diz por que aquele objeto não tem prazo. Registrar, não consertar às cegas.

---

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
| P1 | 1 | 001 |
| P2 | 1 | 002 |
| P3 | 2 | 003, 004 |

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

## 9. Não exercido nesta auditoria

- **Non reformatio in pejus** (FR-070): o código a implementa em `CORRECAO_FIXADA`; não testei uma correção que piorasse a situação do recorrente.
- **Impedimento do julgador** (FR-039): não testei julgar com quem avaliou a peça.
- **Janela aberta bloqueando a definitiva**: a porta recusou antes, por recurso e por reavaliação pendentes; o quarto fato não chegou a ser alcançado.
- **`PROVIDENCIA_A_JUSANTE`**: espécie não julgada.

---

## 10. Evidências

`screenshots/` — 41 imagens na ordem da jornada, de `00-processo-criado.png` a `36-candidato-*-apos-recurso.png`.
