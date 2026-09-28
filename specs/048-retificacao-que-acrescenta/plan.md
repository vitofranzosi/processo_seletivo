---

description: "Implementation plan — 048 · A Retificação acrescenta o que o contrato já permite"
---

# Implementation Plan: A Retificação acrescenta o que o contrato já permite

**Branch**: `claude/retificacao-cobertura-auditoria-b7eabb` · **Date**: 2026-09-26 · **Spec**: [spec.md](spec.md)

## Summary

A tela de Retificação passa a oferecer o que o domínio e o contrato de mutabilidade já admitiam e
nenhuma interface alcançava:
- acrescentar **Modalidade** a um Perfil publicado, com a declaração da ampla ou a linha do quadro da
  cota no mesmo ato;
- acrescentar **critério de desempate** a um marco;
- fazer **nascer** a janela recursal, a regra de corte e a reversão onde o Edital não as declarava.

Duas guardas acompanham o acréscimo:
- a janela que nasce concede;
- o corte não nasce sobre Etapa já avaliada.

**Os dois mecanismos de acréscimo que já existem, e nenhum novo.** O nascimento de objeto é o do
método do sorteio. O acréscimo de item é o do Perfil, do Evento, do Anexo e da linha do quadro. O que se
escreve é:
- duas listas de campos e um registro de nascimento;
- dois fragmentos;
- duas funções extraídas da validação da composição;
- uma função de guarda de domínio, para a janela, e uma de aplicação, para o corte.

Nenhuma entidade, nenhuma migration, nenhuma capacidade, nenhuma espécie `UX-`.

**O risco não está no código: está em onde a guarda da janela mora** (`R-1`). Pô-la no motor de
alterações faria a reprodução de atos já publicados passar a julgar a história. Ela mora no ato de
Retificação.

**Enxugado depois do `/speckit-analyze`**, pelo parecer de 26/09: a guarda genérica de objeto inteiro
saiu (achado A-6 da spec), e o protótipo de medição também (`R-9`). A `D-001` foi decidida: qualquer
Modalidade.

## Technical Context

Python 3.13 · Django 5.2.17 · PostgreSQL · htmx. Superfícies:
- a **tela de Retificação** e os fragmentos dela;
- a **aplicação da Retificação**: elaboração, advertências e publicação;
- a **validação da composição** de Perfil e marco;
- o **documento** da Retificação.

| Pergunta | Resposta, medida |
|---|---|
| Entidade nova? | **não** |
| Migration? | **não** — o `make preparar` continua em `N de 34` |
| Mudança no contrato de mutabilidade? | **não** — `CONTRATO` e `PODE_PASSAR_A_EXISTIR` já decidem tudo; a tela ganha o registro de nascimento conferido contra eles (`R-2`) |
| Achado de validação novo? | **não** — as recusas da Modalidade e do critério vêm da composição, extraída (`R-4`); as do objeto que nasce, da publicação que já existe |
| Recusa nova de domínio? | **duas**, no ato de Retificação: janela que nasce sem admitir; corte sobre Etapa com Resultado — [contrato](contracts/a-retificacao-que-acrescenta.md) §2 |
| Dependência nova entre apps? | `publicacoes/application/retificacoes.py` → `resultados/application/selectors.ha_resultado_em`, importação local (`R-3`) |
| URL nova? | **duas**: `fragmento-retificacao-modalidade`, `fragmento-retificacao-criterio` |
| Casos que cercam o comportamento antigo | **quatro** conhecidos, e duas linhas no inventário de negativas da `033` (`R-9`) |

**Nenhum `NEEDS CLARIFICATION`.** As quatro decisões de domínio foram tomadas pelo usuário em 26/09
(`D-001` a `D-004`). As decisões de desenho estão
em [research.md](research.md), cada uma com a alternativa descartada.

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **II · Publicação é ato imutável** | a Retificação produz versão nova e não toca a anterior; as guardas novas **não** entram na reprodução de atos publicados | `FR-795`, `FR-796`, `R-1` |
| **II · Regras atuais não substituem as históricas** | inscrição, lista exigida, ordens, sorteios e cortes de outros recortes ficam como estão; o que muda é consequência das regras de obsolescência que já existem, e é provado por teste | `FR-781`, `R-8`, `SC-289` |
| **II · Uma fonte autoritativa** | o contrato de mutabilidade continua a única decisão do que se retifica e do que nasce; a validação da Modalidade e do critério é a da composição, extraída e não copiada | `FR-803`, `R-2`, `R-4` |
| **III · Negar por padrão** | nenhuma capacidade nova: acrescentar é retificar, e quem grava é o POST de *Retificar*, que já exige a permissão de elaborar Retificação. Os fragmentos novos seguem o da linha do quadro: exigem sessão e Edital alcançável, devolvem 404 fora disso, e não gravam nada | contrato §3; `R-9` |
| **IV · Regras explícitas** | nenhum valor por omissão: a janela nasce concedendo porque é a única declaração admitida (`D-003`), e não por pré-seleção; vazio é vazio, e diz o que significa | `FR-785`, `FR-799`, `R-2`, `R-10` |
| **V · Simplicidade** | dois mecanismos existentes; nenhuma retificação aditiva genérica, nenhum metamodelo | `FR-802`, `R-5`, `R-6` |
| **VI · Completude de jornada** | o critério da spec **é** o Princípio VI: o que o domínio sustentava e nenhuma interface alcançava passa a ser alcançável pela tela; os percursos do [quickstart](quickstart.md) não usam API | `SC-288`, `SC-290`, `SC-291` |
| **Nada é excluído** | nenhuma migration, nenhuma linha apagada | [data-model.md](data-model.md) |

**Uma tensão, justificada** em *Complexity Tracking*: a dependência de `publicacoes` para `resultados`.

## Phase 0 — o que a medição decidiu

Completa em [research.md](research.md). O que a spec não sabia:

1. **As guardas moram no ato, e não no motor** (`R-1`). `apply_changes` também reproduz atos
   publicados em `consolidate`, e uma guarda ali julgaria a história. A comparação antes/depois fecha,
   de quebra, o contorno por `REMOVE` + `ADD`.
2. **A janela nasce sem pergunta** (`R-2`). O booleano da tela nasce em *"Não"*, e oferecê-lo para
   objeto ausente faria **toda** Retificação criar janela *"não admite"*. A `D-003` torna a pergunta
   desnecessária: a tela pede o prazo e completa o resto.
3. **O corte nasce com os seis campos**, e a guarda de carga ganha a conferência que declara isso
   (`R-2`, `FR-803`).
4. **A validação da composição não corre na Retificação** (`validation.py:893-898`), e aplicá-la ao
   conteúdo inteiro julgaria o acervo. Ela passa a correr **só sobre o que o ato acrescenta** (`R-4`).
5. **A ampla não tem linha própria** (`general_competition_modality_with_row`), e a spec foi corrigida
   nisso: `FR-779` e o cenário 7 da US1.
6. **A Modalidade do mesmo ato não é opção das referências**, que leem o vigente. A declaração da
   ampla e as vagas vêm embutidas no fragmento dela (`R-5`).
7. **Metade das garantias da `D-G5` já vale, e nada as prova** (`R-8`). O teste que devia provar não
   retifica, e é reescrito.

## Ordem de entrega

```
Fase 0 — o chão
   a. ambiente e testes de Retificação verdes antes de editar
   b. extrair validar_modalidade e validar_criterio de perfis.py, sem mudar comportamento (R-4)
   ▼
US5 — a reversão nasce                                   ← CAMPOS_DA_REVERSAO sempre; test_retificar_reversao.py muda de premissa
   ▼   (primeiro porque é uma condição a menos, e prova o caminho do nascimento pela tela)
Guarda da janela — R-1                                  ← função antes/depois em changes.py; chamada nos três pontos da aplicação
   ▼   (antes da janela e do corte: são elas que tornam o nascimento seguro pela API também)
US3 — a janela nasce concedendo                          ← lista de nascimento + complemento fixo; registro de nascimento na guarda de carga
   ▼
US2 — o corte nasce, com guarda                          ← lista de nascimento dos seis; R-3 na elaboração e na publicação; o link da tela do corte chega ao campo
   ▼
US4 — o critério                                         ← fragmento, R-4 na aplicação; test_derivacao ganha o fragmento
   ▼
US1 — a Modalidade                                       ← fragmento, as três alterações, R-4; a frase sai; test_ordem_por_recorte.py:356 retifica de fato
   ▼
Fecho — SC-294 (a Retificação só de texto), PDF da Retificação (FR-798), rastreabilidade.md,
        percursos do quickstart pelo navegador, make lint check test-pg
```

**A ordem das histórias não é a das prioridades, e é de propósito.** A US1 tem o maior valor e o maior
desenho: fragmento, três alterações encadeadas e a validação extraída. As menores vêm antes e
estabelecem as peças que ela usa:
- a reversão prova o nascimento pela tela;
- as guardas fecham a porta da API;
- o critério estreia o fragmento de item com identidade estável e a validação extraída.

**As guardas vêm antes do que elas protegem.** Com a janela e o corte oferecidos antes da guarda, uma
tarefa intermediária deixaria nascer pela API a janela que não concede.

## Riscos, medidos

| Risco | Onde | Como se fecha |
|---|---|---|
| a guarda da janela recusar ato já publicado | `consolidate` reproduz atos com `apply_changes` | a guarda não está em `apply_changes` (`R-1`); um teste reproduz uma Retificação antiga que fez nascer janela *"não admite"* e confere que a consolidação continua |
| a suíte cair em bloco | guardas `R-1`, `R-3` e `R-4` | elas só alcançam o que o ato faz nascer ou acrescenta; os quatro testes conhecidos estão no `R-9`; testes focados em cada tarefa, suíte completa no fecho |
| a troca por objeto inteiro pela API continuar aberta | `apply_change` | **aceito**: é o achado A-6 da spec, fora do escopo por decisão de 26/09 |
| toda Retificação criar objeto que ninguém pediu | o booleano da janela; qualquer `select` que nasça com valor | a janela nasce sem booleano; todo campo de nascimento nasce vazio; `SC-294` é teste, e não só percurso |
| a validação extraída mudar a composição | `validate_profile`, `validate_classification_milestones` | a extração vem antes, sozinha, e a suíte de composição continua verde sem mudança de asserção (Fase 0b) |
| o acervo deixar de ser retificável | a validação da composição sobre o conteúdo inteiro | ela corre só sobre o que o ato acrescenta (`R-4`) |
| a Modalidade nova mudar a ordem de outro recorte | `recorte_da_regra`, `projecao.elegiveis` | não muda por construção; `SC-289` prova retificando de fato |
| ciclo de importação | `resultados/models.py` → `publicacoes` | importação local de `ha_resultado_em`, como o repositório já faz (`R-3`) |
| leitura fora da vigência | `tests/test_vigencia_do_resultado.py` | usa o seletor que já existe, e não `ResultadoEtapa.objects` |
| o *"O que mudou"* público calar os nascimentos | `publicacoes/domain/alteracoes.py` | **não se fecha aqui**: é o `RC-111`, registrado como achado A-4 da spec |

## Phase 1 — desenho

| Artefato | O que decide |
|---|---|
| [data-model.md](data-model.md) | que nada persiste; as formas do que a Retificação passa a escrever; onde mora cada guarda |
| [contracts/a-retificacao-que-acrescenta.md](contracts/a-retificacao-que-acrescenta.md) | o que a tela oferece; os dois fragmentos; a conferência; as recusas e o esqueleto das frases; o que não muda |
| [quickstart.md](quickstart.md) | sete percursos: Modalidade ampla, cota com vagas, corte, janela, critério, reversão, regressão |

**Constitution Check, depois do desenho**: sem mudança.

## Project Structure

### Documentação (esta feature)

```text
specs/048-retificacao-que-acrescenta/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── a-retificacao-que-acrescenta.md
├── checklists/
│   └── requirements.md
├── rastreabilidade.md    # na implementação
└── tasks.md              # /speckit-tasks
```

### Código tocado

```text
backend/processo_seletivo/
├── publicacoes/
│   ├── domain/changes.py                        # a guarda antes/depois (R-1)
│   └── application/retificacoes.py              # chama R-1, R-3 e R-4 na elaboração, nas advertências e na publicação
├── editais/domain/perfis.py                     # validar_modalidade, validar_criterio, extraídas (R-4)
└── interface/
    ├── retificacao.py                           # listas e registro de nascimento; NOVA_MODALIDADE, NOVO_CRITERIO; diferencas
    ├── views.py · urls.py                       # dois fragmentos; reexibição depois do POST
    └── templates/interface/
        ├── retificar.html                       # os dois botões; a frase sai
        ├── _retificacao_modalidade.html         # novo
        └── _retificacao_criterio.html           # novo

backend/tests/                                   # ver R-9
```

## Complexity Tracking

| Tensão | Por que é necessária | Alternativa mais simples descartada |
|---|---|---|
| `publicacoes/application/retificacoes.py` passa a consultar `resultados` (importação local) | a `D-002` recusa o corte sobre Etapa já avaliada, e só `resultados` sabe se há Resultado | na validação de conteúdo: ela não conhece o Edital nem o banco (`R-3`); só advertir: a `D-002` pede recusa |
| duas listas de campos por objeto que nasce (alteração e nascimento) | o corte nasce com três campos que depois não se trocam, e a janela nasce sem a pergunta que só tem uma resposta | uma lista só: o corte nasceria sempre recusado, e a janela, sempre *"não admite"* (`R-2`) |
