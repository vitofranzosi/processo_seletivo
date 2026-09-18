# Implementation Plan: Navegação por capacidade

**Branch**: `claude/spec-033-navegacao-por-capacidade` | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/033-navegacao-por-capacidade/spec.md`

## Summary

A tela do Edital passa a derivar seus destinos **por capacidade**, e as quatro portas que recusam por
base de autorização composta passam a fazê-lo com a gramática que a camada de segurança já implementa para os
outros dois eixos.

**A abordagem técnica cabe numa frase: falta recusar a pergunta composta.** `require_permission`
recebe **uma** permissão; não há como expressar "esta **ou** aquela", que é o que quatro das seis
portas perguntam — e por isso as quatro improvisaram o mesmo `raise Http404`. Cada peça necessária foi
**medida** na árvore, por varredura de AST (ver [research.md](./research.md)):

| O que a feature precisa | O que já existe |
|---|---|
| a doutrina da recusa | **implementada** em `seguranca/application/authorization.py::require_permission` — uma capacidade nomeada → 403, escopo → 404 — e usada por 2 das 6 portas |
| a recusa como página | `interface/erros.py::RecusaDoDominioMiddleware` + `interface/recusa.html`, com título, motivo e "nada foi alterado" |
| saber **o que falta** | `comissoes/domain/autorizacao.py::pode_gerir_comissao` devolve uma `Base` que **nomeia** o que autorizou; a recusa é o espelho dela |
| o princípio da navegação | *"oferecer o que se vai recusar é pior do que não oferecer"*, em `_marcos_publicados` — e o padrão de **derivar a navegação do predicado da porta**, já aplicado numa tela por `_pode_auditar_a_etapa` |
| a frase do "peça a alguém" | praticada na tela do Edital, em `detalhe.html` |
| o instrumento de `SC-168` | `tests/authorization/`, **197 casos** em 38 arquivos |

**Nenhuma migration, nenhuma capacidade nova, nenhum campo novo.** Uma migration aqui seria sinal de
escopo escorregando para "criar papel", que a `FR-483` proíbe.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2.17

**Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL. **Sem migration** — nada do que a feature lê é novo

**Testing**: pytest contra PostgreSQL (`make test-pg`). As camadas envolvidas são
`tests/authorization` — que é onde a garantia mora — e `tests/interface`

**Target Platform**: servidor Linux; interface administrativa renderizada no servidor

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: a derivação de destinos roda por abertura da tela do Edital e consulta o que
já está carregado. O orçamento de consulta não muda: a base de autorização já é lida hoje

**Constraints**: a recusa é superfície de segurança; o conjunto de pares (ator, tela) que abre tem de
ser idêntico antes e depois; o 404 de escopo institucional é proteção de dados e não se toca; o canal
do candidato mantém o 404 uniforme

**Scale/Scope**: **seis** portas de autorização, das quais **quatro** erram — e as quatro fazem a
mesma pergunta composta, que a camada de segurança não sabe recusar. Uma delas, a da distribuição, decide escopo e vínculo na mesma condição e
precisa ser separada antes. Mais: um ponto único de recusa por base composta na camada de segurança, a
derivação de destinos, três frases de template, e o inventário dos **75** pontos que respondem "não
encontrado" — dos quais **59 funções**, **53** recebendo `request` e **32** consultando ator, escopo
ou vínculo

## Constitution Check

*GATE: passou antes da Phase 0 e foi reavaliado após a Phase 1.*

| Princípio | Como esta feature se situa |
|---|---|
| **III · Segurança, Proteção de Dados e Auditoria** | **É o princípio que governa, e o que torna a feature delicada.** Ela muda como a negativa se apresenta, e negativa é superfície de segurança. Três garantias respondem: `FR-482` mantém a verificação no servidor, `FR-483` proíbe afrouxar regra, `FR-480` preserva o 404 de escopo. `SC-168` é o critério que prende as três, e o cenário 4 do quickstart é como ele se verifica |
| **I · Linguagem Ubíqua** | Nenhum vocabulário novo. A feature **estende** a formulação que `detalhe.html` já pratica e a gramática que `_edital_para_publicar` já documenta. `FR-486` proíbe criar uma segunda maneira de dizer a mesma coisa |
| **IV · Regras Explícitas** | A autorização continua no servidor, e continua sendo a mesma. O que muda é a apresentação. Retirar link **não** é regra — `FR-482` diz isso por escrito |
| **V · Qualidade e Rastreabilidade** | Todo `FR-` nasce com teste e linha na matriz. E, aqui, com uma exigência a mais: todo teste **alterado** entra na matriz com o motivo da alteração |
| **VI · Completude de Jornada** | A capacidade entregue é de jornada e é observável: o Publicador puro passa a **conseguir divulgar o resultado** pela interface. Hoje isso só acontece por URL montada à mão ou por acúmulo de papéis — ou seja, a segregação que o produto recomenda passa a ser executável |

**Resultado do gate**: passa, com o Princípio III declarado como o eixo de risco e `SC-168` como a
contenção.

## Constitution Check — reavaliação após Phase 1

Nada mudou de direção, e três descobertas apertaram o desenho:

- **A regra que eu havia escrito no contrato estava errada, e a medição a corrigiu.** Não é a ordem
  de avaliação que protege — a porta da divulgação avalia capacidade **antes** do escopo e não vaza.
  O que protege é o **filtro por escopo na própria consulta**, que as seis portas já fazem, tornando
  objeto de outra unidade indistinguível de objeto inexistente. `FR-487` fixa isso, e `FR-488` trata
  da porta que decide escopo e vínculo no mesmo `if`.
- **O canal do candidato ficou explicitamente fora.** Lá o 404 é uniforme de propósito, para que
  ninguém descubra pela resposta se a inscrição não existe ou é de outra pessoa. Levar a recusa
  explicada para lá seria vazamento, não melhoria.
- **A feature altera testes que passam hoje**, e isso foi para o contrato em vez de aparecer no diff.
  A mudança permitida é de um tipo só: trocar o status esperado, jamais a asserção de quem entra.

**Complexity Tracking**: sem violações a justificar. A tabela foi removida.

## Project Structure

### Documentation (this feature)

```text
specs/033-navegacao-por-capacidade/
├── plan.md              # Este arquivo
├── research.md          # Phase 0 — oito perguntas, respondidas contra o código
├── data-model.md        # Phase 1 — a taxonomia da recusa e a matriz de destinos
├── quickstart.md        # Phase 1 — quatro cenários, e o quarto é o que decide
├── contracts/
│   ├── gramatica-da-recusa.md
│   └── destinos-da-tela-do-edital.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/
│   ├── views.py                     # as quatro portas erradas; a derivação de destinos
│   ├── erros.py                     # nada — o middleware já faz o que precisa
│   └── templates/interface/
│       ├── detalhe.html             # o bloco de marcos, por destino
│       ├── ordenacao.html           # o texto que instrui, e para quem ele vale
│       ├── ato_ordenacao.html       # "não tem ação disponível" passa a dizer a quem pedir
│       └── recusa.html              # nada — já traz título, motivo e "nada foi alterado"
├── comissoes/domain/autorizacao.py  # leitura; é quem sabe nomear o que falta
└── seguranca/application/authorization.py  # onde nasce o ponto único de recusa por base composta

backend/tests/
├── authorization/                   # onde a garantia mora — e onde os casos mudam de status
└── interface/                       # os destinos por papel, e as frases
```

**Structure Decision**: monólito Django com a separação que o repositório já pratica. A decisão de
autorização permanece onde está — nas portas, no servidor. O que esta feature acrescenta é
**apresentação** e **derivação da navegação**, em `interface` — mais **um ponto único de recusa por
base composta** em `seguranca/application`, ao lado do que já existe para capacidade nomeada. Espalhá-lo pelas
portas reproduziria a divergência que a feature existe para fechar: foi a ausência desse ponto que
produziu quatro improvisos idênticos.

## Ordem de execução sugerida

As três histórias são separáveis. A ordem abaixo é a de risco crescente, e a **fase 0 não é
formalidade**.

0. **Registrar o "antes".** A contagem de `tests/authorization/` e o inventário dos pontos que
   respondem "não encontrado" na gestão. Sem isso, `SC-168` não é verificável e a revisão dirigida
   não tem contra o que comparar.
1. **US1 · a derivação por destino.** Só navegação, sem tocar em porta. É a história que entrega o
   `P0` e a que menos risco carrega.
2. **US3 · as frases.** Menor esforço, e independente das outras duas.
3. **US2 · a gramática da recusa.** Por último de propósito: é a que mexe em superfície de segurança
   e a que altera testes existentes. Entra com o cenário 4 do quickstart ao lado. E tem ordem interna
   própria, que a medição impôs:
   1. o **ponto único** de recusa por base composta, em `seguranca/application`;
   2. a **separação** de escopo e vínculo na porta da distribuição, que hoje os decide no mesmo `if`;
   3. só então as quatro portas passam a usar o ponto único.
   Inverter 2 e 3 responderia recusa explicada para Edital de outra unidade.

## Riscos, e o que cada um custaria

| Risco | Sinal de que aconteceu | Contenção |
|---|---|---|
| Afrouxar autorização sem perceber | um caso de `tests/authorization` passa a esperar sucesso onde esperava recusa | cenário 4 do quickstart, lido **caso a caso** e não pela contagem |
| Inverter a ordem de avaliação | recusa de escopo institucional vira 403 | está no contrato como regra normativa; o teste de escopo alheio é obrigatório |
| Levar a recusa explicada ao portal | o candidato passa a distinguir "não existe" de "é de outra pessoa" | o middleware já separa os canais por prefixo; o teste do 404 uniforme não pode mudar |
| Regredir o defeito que o código já corrigiu | quem julga recursos volta a ver "Classificação final" e a receber erro ao clicar | é caso de aceitação de US1, e não caso de borda |
| Retirar destino de quem já tinha | a presidência perde um caminho | `FR-475` e o cenário 1 do quickstart medem os dois sentidos |
| Esconder link e achar que protegeu | a URL montada à mão passa | `FR-482`, e o teste que monta a URL à mão |
| **O escopo crescer no meio do caminho** — **este risco ocorreu** | o inventário encontra recusa de autorização fora das seis portas — e **26** funções autorizativas ainda não foram classificadas | o inventário é a **primeira** tarefa, e T004 é portão: encontrou, para antes da fase 2 e leva a conversa a quem governa o backlog. **A contenção funcionou**: ver abaixo |
| O critério valer só no dia em que foi conferido | uma porta nova nasce depois com a gramática antiga, e a suíte não reclama | a varredura da fase 6, espelhando `test_vocabulario_da_composicao.py` da `030` |

## O que aconteceu com o risco de escopo

**Ele ocorreu, e a contenção funcionou.** O inventário de `T003` classificou as **75** negativas de
`interface/views.py` por varredura de AST — 23 propagações de 404 do domínio, 22 de escopo ∪
inexistente, 17 de objeto inexistente, 1 de estado, 1 de não autenticado e **11 de autorização**.

Das 11, quatro são as portas que este plano nomeia. **Sete não estavam descritas em artefato
nenhum**: `criar_edital`, `anexo_do_rascunho`, `reaproveitar`, `supervisao`, `minha_etapa` e as duas
telas da Mesa, que recusam em `avaliacoes/application/mesa.py::_autorizar`.

Nenhuma delas é descuido — cada uma justifica o 404 no próprio comentário, e três citam doutrina de
spec anterior por identificador. Três misturam escopo e vínculo na mesma resposta, que é trabalho da
natureza da `FR-488` e não tem tarefa aqui.

**A decisão de quem governa o backlog, em 2026-09-18, foi manter o escopo nas quatro portas.** Em
consequência: a `SC-165` passou a se recortar às portas desta feature — o mesmo recorte que a
`FR-476` já praticava —, o contrato e o `data-model` foram recortados junto, e a `T030` fechou sem
código, entregando o registro. As sete estão nomeadas em
[inventario-das-negativas.md](./inventario-das-negativas.md), e há um teste que quebra se alguém
desfizer a decisão de passagem.

O `analyze` rodou de novo sobre os três artefatos depois disso, e não encontrou crítica.
