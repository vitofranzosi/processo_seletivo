# Implementation Plan: Executabilidade antes de publicar

**Branch**: `claude/spec-032-executabilidade-antes-de-publicar` | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/032-executabilidade-antes-de-publicar/spec.md`

## Summary

A validação de publicabilidade passa a perguntar se o Edital **funciona**, e não apenas se está
preenchido. Quatro achados novos na validação de conteúdo — dois impeditivos e dois avisos —, o
método do sorteio impresso no documento publicado, e duas ações que sempre falham retiradas das
telas onde eram oferecidas.

**A abordagem técnica cabe em uma frase: nada de novo é construído.** Cada peça de que a feature
precisa já existe e foi conferida na árvore (ver [research.md](./research.md)):

| O que a feature precisa | O que já existe |
|---|---|
| distinguir publicação de retificação | `validate_for_publication(snapshot, *, ato)` e o padrão de `_forma_da_ordem_declarada` (`030`) |
| levar o achado à etapa certa | `_destino(caminho, codigo)` lendo o caminho de trás para frente |
| resolver o método que governa um marco | `marcos.metodo_que_governa` — ponto único desde a `030` |
| saber se um marco sorteia | `marcos.marco_ordena_por_sorteio` |
| o snapshot inteiro no renderizador do marco | `pdf._marcos(composicao, snapshot, perfil, …)` já o recebe |
| os rótulos dos sete campos do método | `CAMPOS_DO_METODO`, em `editais/domain/perfis.py` |
| o tom de um aviso sobre quadro de vagas | `vacancy_reserved_list_without_row`, seu irmão mais velho |
| o padrão "a razão no lugar do botão" | três telas do PR #120, registrado pela auditoria como padrão a preservar |

**Nenhuma migration, nenhum campo novo no conteúdo normativo, nenhum degrau de elevação.** Isso não
é economia de esforço: é o que a feature é. Uma migration aqui seria sinal de escopo escorregando.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2.17

**Primary Dependencies**: Django, DRF, htmx na interface administrativa; nenhuma nova

**Storage**: PostgreSQL. **Sem migration nesta feature** — a leitura nova sai do conteúdo canônico
já publicado

**Testing**: pytest contra PostgreSQL (`make test-pg`). As camadas envolvidas são
`tests/unit/editais`, `tests/integration/editais`, `tests/integration/publicacoes`,
`tests/interface` e `tests/unit/publicacoes`

**Target Platform**: servidor Linux; interface administrativa renderizada no servidor

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: a validação de conteúdo roda por ato de publicação e por abertura da Revisão.
As quatro verificações novas percorrem Perfis e marcos, que são dezenas — a maior amostra é o
28/2026, com 7 polos. O orçamento de consulta não muda: tudo sai do snapshot já carregado, sem ida
ao banco

**Constraints**: publicação é ato imutável; tabelas append-only protegidas por gatilho **e** por
privilégio ausente; conteúdo publicado não muda de valor nem de resumo criptográfico; recusa nova
não pode alcançar a gravação do rascunho nem a Retificação do acervo

**Scale/Scope**: quatro achados de validação, um bloco novo na seção do marco do documento, dois
booleanos na leitura da ocupação, duas condições de template e uma frase de composição

## Constitution Check

*GATE: passou antes da Phase 0 e foi reavaliado após a Phase 1.*

| Princípio | Como esta feature se situa |
|---|---|
| **I · Linguagem Ubíqua** | Os rótulos do método no documento saem de `CAMPOS_DO_METODO`, que já os nomeia em português. Nenhum termo novo é inventado: *corte*, *geração*, *faixa*, *recorte* e *marco* são os do domínio, e a `030` acabou de defini-los no ponto de uso |
| **II · Integridade Normativa e Imutabilidade** | `FR-460`, `FR-469` e `SC-161` são a expressão direta dele. Nenhum degrau de elevação, nenhuma reescrita de snapshot, e o Edital do acervo continua retificável |
| **III · Segurança e Negar por Padrão** | Nenhuma superfície nova de autorização. As duas telas tocadas continuam sob a mesma verificação de capacidade; retirar um botão **não** substitui a recusa do lado do servidor, que já existe |
| **IV · Regras Explícitas** | É o princípio que a feature cumpre literalmente — *"a operação DEVE validar inconsistências, classificá-las como informação, aviso ou erro impeditivo e bloquear a publicação diante de erro impeditivo"*. Tudo é verificado no domínio; a tela é conveniência, nunca a fronteira |
| **V · Qualidade e Rastreabilidade** | Todo `FR-` desta feature nasce com teste e linha na matriz de rastreabilidade. Nenhum requisito fora de `specs/` |
| **VI · Completude de Jornada** | **Este é o gate que exigiu cuidado, e está declarado na spec.** Validação é requisito de qualidade e não pode substituir capacidade. Por isso: a P2 entrega capacidade nova e observável a quem está **fora** da instituição — conferir o sorteio contra a norma publicada; a P1 entrega ao elaborador uma informação que hoje **não existe** enquanto ainda é rascunho; a P3 retira duas ações impossíveis. As três são demonstráveis pelo canal do ator, sem shell e sem banco |

**Resultado do gate**: passa, com o Princípio VI declarado como tensão tratada e não como
formalidade.

## Constitution Check — reavaliação após Phase 1

Nada mudou de direção, e três decisões de desenho apertaram o cumprimento:

- **`FR-461` ganhou uma condição** que a spec já previa como caso de borda e o desenho tornou
  central: marco cuja regra de corte declara **não governar Etapa alguma** não recebe aviso. Sem
  isso, o Edital mais simples e mais comum da amostra receberia ruído — e ruído treina a pessoa a
  ignorar a família inteira, que é o oposto do Princípio IV.
- **A leitura da ocupação ganha dois booleanos, e não um quinto estado.** A `016` registra por
  escrito que colapsar estados é o que a `UX-032` proíbe; multiplicá-los sem necessidade é o erro
  simétrico. Campo aditivo mantém todo consumidor existente lendo o que lia.
- **A resolução do método no documento é a de `marcos.metodo_que_governa`**, e não uma segunda
  leitura no renderizador. Duas resoluções divergiriam, e a divergência apareceria como documento
  publicado dizendo uma coisa e sorteio fazendo outra.

**Complexity Tracking**: sem violações a justificar. A tabela foi removida.

## Project Structure

### Documentation (this feature)

```text
specs/032-executabilidade-antes-de-publicar/
├── plan.md              # Este arquivo
├── research.md          # Phase 0 — oito perguntas, respondidas contra o código
├── data-model.md        # Phase 1 — achados, seção do documento, leitura da ocupação
├── quickstart.md        # Phase 1 — quatro cenários de verificação
├── contracts/
│   ├── achados-de-executabilidade.md
│   └── marco-no-documento.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── validation.py            # os quatro achados novos; o recorte por `ato`
│   ├── marcos.py                # leitura; nada novo — `metodo_que_governa`, `marco_ordena_por_sorteio`
│   └── perfis.py                # leitura de `CAMPOS_DO_METODO` para os rótulos do documento
├── publicacoes/infrastructure/
│   └── pdf.py                   # `_marcos`: o par `Ordem`, o bloco `Sorteio`, o corte de `Combinação`
├── ocupacao/application/
│   └── selectors.py             # `apuravel` e `faixaDisponivel` na leitura do recorte
└── interface/
    ├── templates/interface/
    │   ├── ocupacao.html        # a razão no lugar dos dois botões
    │   └── _marco.html          # a consequência real da ausência de corte, na composição
    └── views.py                 # nada — `_destino` já roteia os quatro caminhos

backend/tests/
├── unit/editais/                # as quatro regras, sobre snapshot montado à mão
├── unit/publicacoes/            # a seção do marco no documento, nas três grafias de `Método:`
├── integration/editais/         # o recorte por ato: publicação × rascunho × Retificação do acervo
├── integration/publicacoes/     # o acervo não muda de conteúdo nem de resumo
└── interface/                   # a Revisão nomeia e leva à etapa; os botões somem com a razão
```

**Structure Decision**: monólito Django com a separação em `domain` / `application` /
`infrastructure` / `interface` que o repositório já pratica. As regras vão para `domain`, porque a
interface administrativa invoca os commands diretamente e não atravessa o DRF — o Princípio IV não
admite que a fronteira seja o serializer.

## Ordem de execução sugerida

As três histórias são separáveis, e a ordem abaixo é a de risco crescente.

1. **P1 · os dois achados da Classificação** (`FR-457`, `FR-461`, `FR-458`, `FR-459`, `FR-460`).
   Sem tocar em documento nem em tela de execução. É onde a contraprova do falso positivo do corte
   precisa nascer junto com a regra.
2. **P1 · as duas telas** (`FR-462`, `FR-463`). Frase na composição, condição na ocupação.
3. **P2 · o documento** (`FR-464`–`FR-469`). É o maior dos três e o único que mexe no renderizador;
   o teste do acervo entra aqui, antes da mudança, para medir o antes.
4. **P3 · a reserva** (`FR-470`–`FR-472`). Depende de `FR-472` conhecer o mesmo predicado que
   `FR-470` usa — e ele deve ser **uma função só**, consumida pela validação e pelo selector, pelo
   mesmo motivo que a `029` deu ao criar `chamada_em_aberto`: dois predicados de "em aberto"
   divergiriam na primeira mudança.

## Riscos, e o que cada um custaria

| Risco | Sinal de que aconteceu | Contenção |
|---|---|---|
| O aviso do corte vira ruído | dispara no 69/2026 | contraprova obrigatória no cenário 3 do quickstart |
| A grafia-armadilha da ampla | aviso de reserva em Edital que nomeia a ampla | condicionar pelo recorte `NULL`, nunca pela Modalidade declarada |
| Duas resoluções do método | documento diz o comum, sorteio usa o próprio | uma função só: `marcos.metodo_que_governa` |
| A recusa alcançar o rascunho | testes de payload caem em bloco | é o que derrubou 759 testes na `030`; o recorte por `ato` é obrigatório desde a primeira tarefa |
| Um degrau de elevação acrescentado por engano | resumo de versão do acervo muda | cenário 4 do quickstart, medido antes e depois |
| A aresta nova `ocupacao` → `editais.domain` passar despercebida | um fato de emissão morando no módulo de conteúdo normativo, sem ninguém saber por quê | T032 e T034 exigem o registro por escrito: no docstring da função e no comentário do import |
