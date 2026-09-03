# Implementation Plan: Consolidação do Resultado da Etapa

**Branch**: `claude/spec-013-consolidacao-resultado-a0665b` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-consolidacao-resultado-etapa/spec.md`

## Summary

A 012 entregou avaliações confiáveis e parou no ponto exato em que o gate dela diz "nada disso
produziu resultado". A 013 começa ali: transforma a Avaliação concluída e elegível de uma inscrição
numa consequência da Etapa — pontuação, `HABILITADA` ou `ELIMINADA`, com origem verificável — e faz
essa consequência valer para a Etapa seguinte. Não classifica, não combina Etapas, não publica e não
trata recurso.

**Esta é a menor feature desde a 005**, e é pequena por decisão, não por escopo tímido. Três
verificações no código explicam por quê:

1. **A quantidade normativa já existe.** A 012 subiu a versão canônica 5 para que a Etapa declarasse
   quantas avaliações cada inscrição recebe e qual a pontuação máxima, com o significado da ausência
   num leitor só. A 013 lê e não cria incremento nenhum (FR-041).
2. **O conjunto de entrada já é um contrato.** `avaliacoes_elegiveis` foi escrita com o docstring
   "o contrato que a 013 herda", e `avaliacoes_inelegiveis` já responde, com ato, autor e motivo, o
   que ficou de fora. Não há seleção de avaliações a projetar.
3. **O lote já é mecanismo.** Invólucro transacional com bloqueio, reautorização e reserva; desfecho
   preservado no `result_payload` que a 012 criou por precisar dele; recusas agrupadas por motivo;
   um evento de auditoria por item. Quatro peças, nenhuma nova.

O trabalho tem três naturezas, e elas não têm o mesmo peso:

- **Uma tabela, num app novo** — `ResultadoEtapa`, append-only pelas três camadas que o projeto já
  opera. É o agregado que a 014 vai herdar (T-001, T-002).
- **Três funções de domínio puro** — a regra da V1, a compatibilidade normativa e a escolha das
  Etapas anteriores. Nenhuma toca banco, e é isso que faz a tabela-verdade caber num teste unitário
  (T-003 a T-005). Os **conjuntos** que a progressão consulta ficam num seletor, e não nelas: a
  primeira redação chamava de pura uma função que prescrevia `exists` e `values_list`.
- **Uma superfície alterada maior do que parece** — a progressão alcança seis pontos da 012, não
  três: a distribuição, a rota individual de autorização, a Mesa, a inscrição de trabalho com seus
  documentos, a navegação de próxima pendente e a contagem de Minhas Etapas. É a parte arriscada, e a
  que tem contrato próprio e testes de não regressão e anti-IDOR.

**A decisão que mais determina o desenho** é a que a revisão da spec produziu: a **exigência de
habilitação** na Etapa imediatamente anterior só vigora depois do primeiro Resultado dela. Sem esse
gate, a combinação de D-001 com D-003 esvaziaria permanentemente a Etapa seguinte de todo Edital de
segunda leitura — a 013 quebraria, para os Editais que declinou de servir, um fluxo que a 012 faz
funcionar hoje. O gate custa uma consulta de existência, e alcança **apenas** essa exigência: a
exclusão por eliminação anterior não tem gate nenhum, e vale para todas as Etapas posteriores.

**A que mais economiza**: a spec proíbe explicitamente inventar a média. Consolidar N avaliações
exigiria um terceiro campo normativo na Etapa, e o FR-008 da 012 já fechou aquela porta — "o único
incremento canônico, e ele acontece uma vez". A V1 consolida leitura única, impede o resto com frase
nomeada, e a regra de combinação fica para quando houver Edital real que a exija.

**A que mais surpreende**: o guard de D-002 protege **só a reabertura**. Reabrir muda a pontuação e
tornaria o Resultado uma afirmação sobre um número que não existe mais; é recusado por inteiro.
Impedir não muda pontuação nenhuma — e por isso se aplica integralmente, inativando inclusive a
Atribuição da Avaliação fonte. Uma redação anterior a preservava, e abria um buraco que o próprio
código denuncia: a cadeia de autorização não consulta Impedimento, ela depende de ele ter inativado
a Atribuição, de modo que preservá-la deixaria a pessoa recém-declarada impedida com acesso mantido
à inscrição e aos documentos dela. O Resultado, que já está materializado e não depende de Atribuição
ativa, permanece — e passa a **exibir a contestação superveniente**, que é a única forma pela qual a
V1, sem anulação, registra que algo saiu errado.

**A que a revisão do plano corrigiu por último**: a progressão tem duas regras, não uma. Eliminação
exclui de **todas** as Etapas posteriores, sem gate; a exigência de habilitação vale sobre a
imediatamente anterior e só depois do primeiro Resultado dela. Fundi-las deixava um buraco concreto —
eliminada na Etapa 1, com a Etapa 2 ainda não consolidada, a inscrição reaparecia na Etapa 3.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** Nenhuma superfície de
API nova: a feature inteira é servida pelo canal HTML institucional, com os fragmentos htmx já
embarcados. Nenhuma alteração no `openapi.yaml` da 001.

**Storage**: PostgreSQL. **Uma** migration, no app novo `resultados`: um modelo, uma unicidade
`(inscricao, etapa_id)`, um `OneToOne` sobre a Avaliação fonte, três checks de completude, um índice
`(edital, etapa_id)` e **duas** triggers — a de coerência, que impede o Resultado de nascer apontando
para Avaliação de outra inscrição, e a append-only, que impede que ele mude depois. Sem a primeira, a
segunda apenas congelaria o erro (T-011). **Nenhuma migration em `editais`, `publicacoes`,
`auditoria`, `avaliacoes` ou `comissoes`** — a 013 não acrescenta coluna a nenhum modelo existente.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. Três exigências específicas: a unicidade sob
concorrência e a trigger só são exercidas com `TEST_DB_ENGINE=postgresql`; o teste de imutabilidade
`test_imutabilidade_do_historico.py:225` falha se o modelo recusar mutação sem estar em
`TABELAS_APPEND_ONLY`; e a ausência de verificação por linha nas listagens precisa de teste de
`performance` próprio, como a 011 e a 012 têm.

**Target Platform**: servidor Linux; navegador institucional, incluindo celular — o resumo ampliado
e a lista de Resultados precisam caber em 375 px sem tabela horizontal.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: o resumo da Etapa continua sendo **uma** agregação, com as dimensões novas
como `Count` condicional; a resolução da progressão custa duas consultas por listagem — as eliminadas
em Etapas anteriores e as habilitadas na imediatamente anterior — e nunca uma por linha. A rota
individual ganha uma consulta, onde ela não é gargalo e onde o próprio docstring da 012 registra que
listagem não passa. O lote resolve elegíveis, Resultados existentes e
habilitados **antes** do laço.

**Constraints**: `comando_de_comissao` bloqueia o `ProcessoSeletivo` inteiro, e um lote de mil
inscrições o segura pela duração da transação. Não é novidade — a distribuição da 012 tem a mesma
forma —, mas é o motivo de o lote ser paginado por seleção de tela e não crescer indefinidamente.

**Scale/Scope**: um Edital com mil inscritos e quatro Etapas — mil é o teto de SC-002, e é o número
usado em spec, contrato, quickstart e no teste de volume do lote. Um modelo novo, três funções de
domínio, um classificador de prontidão, um seletor de conjuntos, duas rotas novas, seis superfícies
alteradas, zero campos normativos novos.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; identificador público não autoriza; invariantes em constraint | `ResultadoEtapa` é conceito distinto de `Avaliacao`, com ciclo de vida próprio, e por isso app próprio (T-001) — a Constituição nomeia Avaliação e Resultado separadamente. `etapa_id` referencia a identidade publicada, não a linha de elaboração, pela razão que a 011 e a 012 já fixaram. As duas invariantes centrais vão para o banco: unicidade do par e `OneToOne` da fonte. Trocar o UUID de uma inscrição eliminada na URL responde 404 uniforme. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | O Resultado **não copia** nota mínima, máxima nem caráter: guarda a `VersaoConsolidada`, e a regra histórica é reproduzida dela — a mesma decisão que a 012 tomou e pelo mesmo motivo (T-004). A compatibilidade compara norma, não identidade de versão, o que impede tanto misturar regras diferentes quanto bloquear por Retificação irrelevante. Nada nesta feature escreve em conteúdo publicado. Instantes vêm do `now` da transação, como nos demais comandos. **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | A autorização é a herdada — `comando_de_comissao` sobre `pode_gerir_comissao` —, reavaliada depois do bloqueio, sem capacidade nova (T-009). Eliminação passa a ser motivo de 404 na Mesa, com a mesma resposta uniforme que a 012 dá para inscrição não atribuída. A trilha registra ator, ato, agregado, correlação e chave, e **não copia pontuação nem parecer**; o desfecho do lote carrega protocolo, nunca nome ou nota. Respostas com Resultado são não armazenáveis. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | A regra é função pura no domínio, e a tela não decide nada — FR-016 proíbe até que a presidência digite a nota. Estados: `HABILITADA` e `ELIMINADA` são persistidos porque são o ato; `PENDENTE` e `CONSOLIDADO` são derivados porque são fatos, e persistí-los criaria estado a manter (D-006). Os quatro riscos de concorrência da Constituição estão mapeados a mecanismo existente em T-010, e cada um tem resultado observável na spec. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | O [quickstart.md](./quickstart.md) demonstra os requisitos observáveis pelo canal do ator e **declara** que os demais — invariantes de banco, de comando e de não regressão — são responsabilidade de `tasks.md`, com fechamento em `traceability.md`. Nada de motor de regras: uma tabela, três funções puras. A simplicidade não custou histórico: o Resultado é append-only nas três camadas. **Passa, com a cobertura declarada e não presumida** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | O percurso inteiro é navegável em `interface`: a presidência abre a Etapa, lê a prontidão, consolida um lote, consulta a proveniência, é recusada ao tentar reabrir a fonte e encontra apenas os habilitados na Etapa seguinte. A recusa faz parte da entrega. E o gate de D-003 tem demonstração própria — o Edital de segunda leitura que continua funcionando —, porque não regredir é parte do valor. **Passa** |

Duas exceções vão para `Complexity Tracking`: o app novo e a versão materializada no Resultado.

**Reavaliação após a Fase 1.** Os seis gates continuam aprovados, e a Fase 1 mudou uma coisa: a
primeira leitura do princípio III dava a autorização por resolvida com "a mesma base da reabertura".
O contrato mostrou que falta uma segunda pergunta — quem **lê** um Resultado. A resposta ficou em
T-009: presidência e o papel `auditoria:consultar` que já existe, pela mesma porta das conclusões
preservadas, sem que ler conceda consolidar. Sem isso, US4 teria nascido sem ator definido para
metade do seu enunciado.

**Reavaliação depois da revisão do plano, e o que ela derrubou.** Três gates haviam sido aprovados
sobre premissa errada, e o registro fica porque os erros são de tipos diferentes:

- **III** — dava-se por resolvido com "o impedimento é sempre registrável". Era, e mesmo assim o
  desenho abria um buraco: preservar a Atribuição que fundamenta Resultado mantinha o acesso da
  pessoa impedida, porque a cadeia de autorização não pergunta por impedimento — ela depende de ele
  ter inativado a Atribuição. Corrigido em T-007: o impedimento se aplica por inteiro, e o Resultado
  passa a declarar a contestação. **Passa** de novo, agora por construção e não por otimismo.
- **I** — dava-se a integridade por garantida porque as linhas são imutáveis. Imutabilidade impede
  que o correto se torne errado; não impede que o errado nasça, e num append-only ela o torna
  incorrigível. Corrigido em T-011: sai o campo `versao`, entra a trigger de coerência. **Passa.**
- **IV/V** — a progressão estava descrita como uma regra só, e como três arquivos alterados. São
  duas regras — eliminação transitiva sem gate, habilitação com gate — e seis superfícies. A
  subestimação não era de esforço, era de risco: `proxima_pendente` entregaria inscrição eliminada
  sem que ninguém a pedisse. **Passa**, com a superfície enumerada no contrato e nas fatias.

## Project Structure

### Documentation (this feature)

```text
specs/013-consolidacao-resultado-etapa/
├── spec.md              # a especificação, com sete decisões fechadas
├── plan.md              # este arquivo
├── research.md          # Fase 0 — T-001 a T-010
├── data-model.md        # Fase 1 — a tabela e o que não é tabela
├── quickstart.md        # Fase 1 — o percurso, e a cobertura declarada
├── contracts/
│   └── resultado.md     # rotas, corpos, desfecho, recusas e o que muda na 012
├── checklists/
│   └── requirements.md  # qualidade da spec, três iterações
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── resultados/                      # NOVO
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                    # ResultadoEtapa
│   ├── migrations/0001_initial.py   # modelo, constraints, índice, trigger
│   ├── domain/                      # puro: sem consulta, sem modelo
│   │   ├── regra.py                 # consequência a partir da norma (T-003)
│   │   ├── compatibilidade.py       # norma histórica × vigente (T-004)
│   │   └── progressao.py            # Etapa anterior e Etapas anteriores (T-005)
│   └── application/
│       ├── prontidao.py             # classificação derivada de cada participante (T-008)
│       ├── consolidacao.py          # o lote, sob comando_de_comissao (T-006)
│       └── selectors.py             # conjuntos de eliminadas e habilitadas; Resultados da Etapa
├── avaliacoes/
│   ├── domain/
│   │   └── autorizacao.py           # ALTERADO: terceira pergunta, só na rota individual (T-005)
│   ├── application/
│   │   ├── avaliacao.py             # ALTERADO: guard em reabrir (T-007)
│   │   ├── impedimento.py           # ALTERADO: declara Resultados contestados (T-007)
│   │   ├── distribuicao.py          # ALTERADO: excluída é erro do pedido (T-005)
│   │   ├── mesa.py                  # ALTERADO: inscrição e documento herdam a decisão
│   │   └── selectors.py             # ALTERADO: resumo, listagem, mesa, proxima_pendente,
│   │                                #   carga_nas_etapas (T-005, T-008)
├── seguranca/papeis.py              # ALTERADO: a tabela entra em TABELAS_APPEND_ONLY
└── interface/
    ├── urls.py                      # ALTERADO: duas rotas novas
    ├── views.py                     # ALTERADO: consolidar, resultados, resumo ampliado
    └── templates/interface/
        ├── distribuicao.html        # ALTERADO: prontidão e ação de consolidar
        ├── impedimentos.html        # ALTERADO: duas listas na confirmação
        └── resultados.html          # NOVO

backend/tests/
├── unit/resultados/                 # regra, compatibilidade, progressão — sem banco
├── integration/                     # unicidade, imutabilidade, idempotência, guards
├── authorization/                   # 404 uniforme para eliminada e para não presidência
├── performance/                     # nenhuma listagem verifica por linha
└── acceptance/test_resultado_da_etapa.py
```

**Structure Decision**: a estrutura existente do backend Django, com um app novo em
`backend/processo_seletivo/resultados/`. O canal continua sendo o HTML de `interface`; não há
diretório de frontend, e nada é acrescentado a `portal` — o Resultado é administrativo, e o candidato
não o vê nesta feature.

## Fases de implementação sugeridas

As fatias da §6 da spec, com o que cada uma entrega observável:

| Slice | Entrega | Artefatos |
|---|---|---|
| **S0** | O resumo existente explica participação, prontidão e impedimentos | `selectors.py`, `progressao.py`, `distribuicao.html` |
| **S1** | Uma inscrição pronta produz Resultado imutável, coerente e reproduzível | app `resultados`, migration com as duas triggers, `regra.py`, `compatibilidade.py` |
| **S2** | A presidência confirma lote idempotente com desfecho e auditoria por item | `consolidacao.py`, rota e template |
| **S3** | A progressão fecha as seis superfícies, e os guards entram | `resultados.html`, `autorizacao.py`, `distribuicao.py`, `mesa.py`, `avaliacao.py`, `impedimento.py` |

Os guards ficam em S3 de propósito: eles só têm o que proteger depois de S2, e antecipá-los
produziria código com um único caminho testável — o de nunca haver Resultado. S3 é a fatia mais
arriscada da feature, porque é a única que altera comportamento já entregue, e é ela que carrega os
testes de não regressão e anti-IDOR das seis superfícies.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples, e por que foi rejeitada |
|---|---|---|
| App novo `resultados` para um único modelo | O princípio I pede conceitos distintos com ciclos de vida distintos, e a 014 crescerá em torno deste agregado — classificação, publicação, recurso. Mover tabela depois é caro onde migration aplicada não se reescreve. | *Modelo dentro de `avaliacoes`*: elimina até o import local e custa zero apps, mas hospeda em "avaliações" um agregado que não é avaliação. Troca uma linha de import hoje por uma migration de renomeação amanhã. |
| Import de `resultados` dentro do corpo de duas funções de `avaliacoes` | As dependências são genuinamente mútuas — consolidar lê o conjunto elegível, reabrir pergunta por Resultado — e o import local é idioma da casa, não gambiarra: `reabrir` já importa `comando_de_comissao` assim. | *Sinal ou registro de observadores*: mecanismo desproporcional para duas funções, e esconderia num despachante a regra que a spec quer explícita. |
| Trigger `BEFORE INSERT` conferindo o Resultado contra a Avaliação fonte | O Resultado é append-only, e uma combinação errada gravada uma vez é incorrigível pela aplicação. `CHECK` não atravessa tabelas em PostgreSQL, e a Constituição pede constraint para invariante persistente quando aplicável. | *Confiar na função de consolidação, único ponto de inserção*: verdade hoje, e a feature seguinte também escreve nessa tabela. *Materializar menos e derivar tudo*: `inscricao` e `etapa_id` sustentam a unicidade, que precisa ser constraint. |
| Terceira condição em `pode_avaliar_inscricao`, cujo docstring diz "duas, e não três" | O argumento do docstring é custo em listagem, e ele mesmo registra que listagem nunca usa essa função. Uma consulta a mais na rota de item é o preço certo. | *Resolver tudo por conjunto, inclusive na rota individual*: obrigaria a rota de item a montar o conjunto da Etapa inteira para responder sobre uma inscrição. |
