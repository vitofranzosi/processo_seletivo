---

description: "Implementation plan — 046 · Contrato de executabilidade do Processo publicado"
---

# Implementation Plan: Contrato de executabilidade do Processo publicado

**Branch**: `claude/spec-046-processo-executabilidade-31fa38` · **Date**: 2026-09-26 · **Spec**: [spec.md](spec.md)

## Summary

A publicação passa a recusar o que o próprio sistema já sabe que não executará: a Etapa cujo
Resultado o fluxo exige e que a consolidação nunca produzirá, e o Perfil em que nenhum marco corta. O
Edital publicado deixa de ser julgado pela validação de quem ainda vai publicar. E a fonte de
demonstração do sorteio sai do vocabulário de produção.

**Três funções novas na validação, uma guarda em `_pendencias`, um vocabulário que passa a depender
do ambiente.** Nenhuma entidade, nenhuma migration, nenhuma capacidade, nenhuma espécie `UX-`. A regra
da consolidação não é copiada: é consultada.

**O custo não está no código de produção: está nas fixtures** (`R-7`). Medido em 26/09 com um
protótipo que registrava sem bloquear: **1457 casos (19% da suíte), em 191 arquivos**, teriam a
submissão recusada — e a causa é de fixture em cada família. A fixture central da `011` publica, por
padrão, uma Etapa eliminatória sem nota mínima; quatro fixtures de marco e o `seed_demo` publicam
Perfil sem corte.

## Technical Context

Python 3.13 · Django 5.2.17 · PostgreSQL. Superfícies: a **validação do conteúdo** do Edital (Revisão
do assistente, submissão, publicação, confirmação da Retificação), a **tela do Edital**, o
`como-preencher` da etapa *Etapas*, o **seletor de fonte** do método de sorteio e a **configuração**
de produção.

| Pergunta | Resposta, medida |
|---|---|
| Entidade nova? | **não** |
| Migration? | **não** — o `make preparar` continua em `N de 34` |
| Achado de validação novo? | **três códigos**: `stage_result_unreachable` (impeditivo), `stage_without_result` (aviso/advertência), `profile_without_cut_rule` (impeditivo) — [contrato](contracts/o-gate-da-publicacao.md) |
| Achado que deixa de sair? | `milestone_without_cut_rule` no Perfil sem corte algum (`FR-753`) |
| Dependência nova entre apps? | `editais/domain/validation.py` → `resultados/domain/regra.py`, importação local de função pura (`R-1`) |
| Configuração nova? | `SORTEIO_FONTE_DE_DEMONSTRACAO` (`R-6`) |
| Consulta nova? | **não**; a tela do Edital publicado passa a fazer **uma a menos** — deixa de montar o snapshot (`R-5`) |
| Casos que cercam o comportamento antigo | **1457** atravessam fixtures (quatro mudanças de fixture e um ajudante novo resolvem); **3** afirmavam o `RC-32` e mudam de premissa; os da `FR-461` com marco único, a recontar (`R-7`) |

**Nenhum `NEEDS CLARIFICATION`.** As decisões de domínio foram tomadas pelo usuário em 26/09 (`D-001`,
`D-002`); as de desenho estão em [research.md](research.md), cada uma com a alternativa descartada.

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **II · Publicação é ato imutável** | nenhum conteúdo publicado muda; os impeditivos novos existem só no ato de publicação, e a Retificação recebe advertência ou nada | `FR-751`, `FR-754`, `SC-281` |
| **II · Uma fonte autoritativa** | a regra da consolidação é consultada, não copiada; o vocabulário de fontes continua sendo o único ponto que decide a fonte | `FR-747`, `FR-757`, `R-1`, `R-6` |
| **II · O valor publicado é intocável** | o acervo não é revalidado nem convertido; o `RC-32` para de julgá-lo | `FR-755` |
| **III · Negar por padrão** | nenhuma capacidade nova; produção nega a fonte de demonstração e recusa o boot que a reinclua | `FR-757`, `FR-758` |
| **IV · Regras explícitas** | nenhum padrão inventado: a publicação recusa a Etapa sem regra de combinação em vez de escolher uma; a mensagem diz o que falta e onde | `FR-746`, `FR-749`, `FR-752` |
| **V · Simplicidade** | três funções vizinhas das que já existem; nenhum framework de validação, nenhuma flag no conteúdo | `R-1`, `R-4` |
| **VI · Completude de jornada** | os percursos de [quickstart.md](quickstart.md) pela tela, com identidades segregadas | `SC-275` a `SC-280` |
| **Nada é excluído** | nenhuma migration, nenhuma linha apagada | [data-model.md](data-model.md) |

**Uma tensão, justificada** em *Complexity Tracking*: a dependência nova de `editais` para `resultados`.

## Phase 0 — o que a medição decidiu

Completa em [research.md](research.md). O que a spec não sabia:

1. **A regra é consultada por importação local** (`R-1`), e a nota de `avaliacoes/domain/formas.py`
   que diz que `editais` não conhece o domínio da conclusão continua verdadeira: a validação não lê
   forma nem sentido, só pergunta.
2. **Dois códigos para a Etapa, e a #117 fica como está** (`R-3`): um código em duas severidades
   quebraria o invariante de `test_invariantes_da_declaracao_unica.py` e faria a advertência da
   Retificação sumir. Com dois, a `FR-751` vale sem tocar a subtração.
3. **`_pendencias` é o ponto único do `RC-32`** (`R-5`), e a guarda entra antes de montar o snapshot.
4. **O vocabulário de fontes vira função** (`R-6`), porque o dicionário montado no import não
   responderia a `override_settings`.
5. **A suíte quebra em bloco, e por fixture** (`R-7`): 1457 casos, quatro causas, todas resolvidas antes da regra.
6. **A `045` prende o contrário da `FR-755`** numa tarefa ainda não executada (`R-8`). O usuário
   decidiu em 26/09: a `045` entra antes. Com ela mesclada, a leitura mostrou que era requisito (`FR-739`
   de lá), e não cláusula de teste; o usuário decidiu *"fatos ficam, gate sai"* (`D-003`, `R-5`).

## Ordem de entrega

```
Fase 0 — o chão
   a. conferir que a 045 está na main e rebasear (R-8)
   b. publicar_como_acervo em tests/fixtures/ (sem regra nova ainda: ele só precisa existir)
   ▼
US3 — o Edital publicado não se julga como se fosse publicar   ← views.py (_pendencias); 3 casos + a contraprova na T021 da 045; varredura da FR-756
   ▼   (primeiro porque é o menor e não depende de fixture)
US4 — a fonte de demonstração                                   ← settings + fontes/__init__.py + 2 leitores; independente
   ▼
US2 — o Perfil que não convoca ninguém
   │   a. as quatro fixtures de marco e o seed_demo ganham corte que não governa Etapa — ANTES da regra
   │   b. _perfil_sem_corte + supressão do aviso por marco
   │   c. os casos da FR-461 ganham o segundo marco (Cenário D)
   ▼
US1 — a Etapa que o fluxo exige e que não se consolida
       a. etapas(minima="0.0000") por padrão; avaliacoes=2 e os quatro arquivos da consolidação para o acervo — ANTES da regra
       b. _etapa_sem_resultado, com a tabela-verdade (SC-275)
       c. como-preencher (FR-750)
       d. a advertência na confirmação da Retificação (FR-751)
   ▼
Fecho — SC-276 (os executáveis continuam publicáveis), rastreabilidade.md, percursos do quickstart, make lint check test-pg
```

**A ordem das histórias não é a das prioridades, e é de propósito.** A `US1` é a de maior valor e a de
maior churn de fixture; a `US3` e a `US4` são pequenas e independentes, e entrar com elas primeiro
deixa a suíte verde e o diff legível antes do bloco. **Em cada história que muda fixture, a fixture
muda antes da regra** (passos *a*): com a regra primeiro, a suíte cai em bloco, com causa enganosa, e
a correção vira caça — foi o que a primeira rodada do protótipo mostrou (872 erros a 34%).

## Riscos, medidos

| Risco | Onde | Como se fecha |
|---|---|---|
| a suíte cair em bloco com causa enganosa | `R-7` — 1457 casos, quatro causas, todas de fixture | a fixture muda antes da regra, em cada história; a recontagem compara com o registro do protótipo |
| `minima="0.0000"` mudar o que a Mesa exercita | `comissao.etapas`, 96 arquivos | zero não elimina e não obriga parecer (`012`, `FR-033`); se algum caso afirmar a ausência de nota mínima na tela, ele declara `minima=None` e publica como acervo |
| o corte que não governa Etapa mudar participação | as quatro fixtures de marco | `faixa.etapa_governada` devolve `None` e nenhum corte é emitido por elas; o `FR-214` preserva o conjunto. Se um caso emitir corte sobre essas fixtures, a recontagem o acusa |
| o ajudante de acervo esconder regressão | `publicar_como_acervo` | neutraliza **só** as duas funções desta feature, e só durante a publicação; o nome e o docstring dizem o que simula; a varredura do `FR-756` não o alcança porque ele não chama a validação |
| a advertência da Retificação sumir | `advertencias_do_ato` (#117) | dois códigos (`R-3`); um caso confere a advertência **na confirmação**, e não só na função |
| divergência com a `045` | `validation.py`, `views.py`, a `FR-739` de lá | a `045` entra antes (decisão de 26/09); na página do Edital publicado ficam só os fatos de uma lista fechada, e o da Etapa sem Evento é o único (`D-003`, `R-5`) |
| `SC-191` da `037` parecer violada | `test_cronograma_publico.py` | o lado da gestão passa a ler a conferência no domínio e a fase derivada; a tela publicada não acusa, e portanto não diverge (`R-7`) |
| a barreira de produção não ser exercida | `test_configuracao_producao.py` | um caso novo carrega o módulo de produção com a variável ligada e espera `ImproperlyConfigured` nomeando-a |
| Edital de produção com a fonte de demonstração | base de produção | consulta de [data-model.md](data-model.md) antes da implantação — fora do alcance da suíte |

## Phase 1 — desenho

| Artefato | O que decide |
|---|---|
| [data-model.md](data-model.md) | que nada persiste; o que muda de sentido; a configuração nova; a consulta que responde pelo acervo de produção |
| [contracts/o-gate-da-publicacao.md](contracts/o-gate-da-publicacao.md) | os três códigos, severidades, atos, caminhos e o esqueleto das frases; o que deixa de aparecer; a lista fechada de quem consulta a validação; o vocabulário por ambiente |
| [quickstart.md](quickstart.md) | cinco percursos: Etapa, Perfil, Edital publicado, fonte de demonstração, regressão |

**Constitution Check, depois do desenho**: sem mudança.

## Project Structure

### Documentação (esta feature)

```text
specs/046-contrato-de-executabilidade/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── o-gate-da-publicacao.md
├── checklists/
│   └── requirements.md
├── rastreabilidade.md    # na implementação
└── tasks.md              # /speckit-tasks
```

### Código tocado

```text
backend/
├── config/settings/
│   ├── base.py · development.py · test.py      # SORTEIO_FONTE_DE_DEMONSTRACAO
│   └── production.py                           # a barreira de boot
└── processo_seletivo/
    ├── editais/domain/
    │   ├── validation.py                       # _etapa_sem_resultado, _perfil_sem_corte, supressão do aviso por marco
    │   └── perfis.py                           # lê o vocabulário pela função
    ├── sorteios/infrastructure/fontes/__init__.py   # fontes_publicadas()
    └── interface/
        ├── views.py                            # _pendencias: só antes da publicação
        ├── forms.py                            # o seletor lê o vocabulário pela função
        └── templates/interface/compor_etapas.html   # como-preencher (FR-750)

backend/tests/                                  # ver R-7
```

## Complexity Tracking

| Tensão | Por que é necessária | Alternativa mais simples descartada |
|---|---|---|
| `editais/domain/validation.py` passa a importar `resultados/domain/regra.py` (local, função pura) | a `FR-747` exige uma fonte só para a regra de consolidação; a publicação precisa perguntar a ela | copiar os três predicados para `editais` — é a duplicação que a feature existe para evitar, e divergiria na primeira mudança da regra |
