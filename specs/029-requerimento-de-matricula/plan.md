# Implementation Plan: Requerimento de Matrícula — o que a vaga exige, perguntado uma vez

**Branch**: `claude/spec-requerimento-matricula-c09145` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

> **O branch do git e o nome da feature não coincidem, e está certo assim.** O branch é o acima; a
> feature é a pasta `029-requerimento-de-matricula`. É o mesmo descompasso que a `028` teve, e pela
> mesma causa — o branch nasce do trabalho, e a pasta, do `--number`.
>
> **Como os scripts resolvem isso**, conferido em `.specify/scripts/bash/common.sh`: eles leem
> `SPECIFY_FEATURE_DIRECTORY`; na ausência dela, `.specify/feature.json`; e, faltando os dois,
> **falham** — em momento nenhum procuram pelo nome do branch. A primeira execução com a variável
> **persiste** o `feature.json`, e desde então ela é dispensável. Nesta worktree o arquivo já existe.

**Input**: Feature specification from `specs/029-requerimento-de-matricula/spec.md`

---

## Summary

O Requerimento de Matrícula deixa de ser um PDF preenchido à mão, assinado, digitalizado e anexado,
e passa a ser **dado estruturado dentro do sistema**. O Edital declara se exige requerimento e em que
momento — na inscrição ou na convocação —; o candidato encontra o que o sistema já sabe apresentado
como informação, completa o que falta, aceita a declaração de veracidade do Edital e envia; quem
conduz lê o resultado no dossiê da inscrição.

**A abordagem técnica cabe em duas frases: o arco administrativo já existe, e o que falta é uma
entidade e uma tela.** A `019` já pratica convocação, desfecho e o vocabulário de matrícula; a `009`
já pratica rascunho-que-vira-ato; a `026` já governa campo novo em conteúdo publicado. A pesquisa
mediu cinco coisas que decidiram o formato do plano:

- **"Chamada em aberto" já é um predicado do sistema**, composto de `vigentes` e `desfecho_de` em
  `convocacao/application/selectors.py`. Escrever um segundo predicado repetiria um beco que a `019`
  já pagou, e por isso o gatilho consome um seletor único ([research.md](research.md), `T-006`).
- **A imutabilidade condicional ao estado tem precedente literal** — a trigger
  `FOR EACH ROW WHEN (OLD.status IN …)` que congela a Retificação final. A `FR-396` é essa forma com
  outro estado, e a tabela **não** entra em `TABELAS_APPEND_ONLY`: o total continua `31` (`T-005`).
- **Nenhuma etapa nova no assistente.** A sexta das nove — *Inscrição* — já reúne o período e os
  Documentos Exigidos, e é onde a declaração pertence. E ela **não** passa por `replace_draft`, que
  não carrega campo de raiz (`T-003`).
- **A base de CEP existe, é MIT e traz o código IBGE** — e a própria fonte adverte que a
  confiabilidade das coordenadas é variável, o que converte a `D-008` de preferência em evidência
  (`T-008`).
- **A conferência de publicação já aceita achado condicionado ao ato**, então a `FR-407` custa um
  caso, e não um mecanismo (`T-004`).

**O custo real está em dois lugares, e os dois foram medidos.** Um campo novo no conteúdo publicado
faz **três** guardiões falharem por omissão — o contrato de mutabilidade, a forma publicada e a
oferta de retificação (`T-001`); e a jornada ponta a ponta exige que o `seed_demo` declare o
requerimento num Edital que **chegue à convocação**, ou a `US2` não é demonstrável (`T-010`).

**Uma correção de leitura, declarada.** A primeira passada da pesquisa afirmou que a varredura por
`requerimento` no backend só encontrava vocabulário proibido de outra feature. A medição desmentiu:
são 41 ocorrências, e a maioria é a fixture `ANEXO I — REQUERIMENTO` — que não é ruído, é a evidência
de que o Anexo é exatamente o que esta feature substitui (`T-010`).

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova.** A base de CEP entra
como **dado** carregado por comando, e não como pacote: a porta do domínio (`FR-389`) mantém a fonte
substituível sem que o domínio a conheça

**Storage**: PostgreSQL 16. **A `SCHEMA_VERSION` do conteúdo publicado sobe de 15 para 16**, com o degrau de elevação do acervo. **Duas tabelas novas** — `RequerimentoDeMatricula` e `ReferenciaDeCep` —,
**dois campos** em `processos.Edital`, **um gatilho** condicional ao estado, e **cinco restrições**.
`TABELAS_APPEND_ONLY` **não** muda: continua `31`

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). O gatilho da `FR-396` é
PostgreSQL puro e **não é exercido** no modo padrão da suíte — é a armadilha que o `AGENTS.md`
registra, e aqui ela tem consequência direta

**Target Platform**: servidor web; portal e interface administrativa server-side, sem SPA e sem build
de front

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**, **medidos** por `tests/integration/requerimentos/test_orcamento_de_consulta.py`:
**+1 consulta** na tela da inscrição (o cartão); **+1** no dossiê; **zero** na lista de inscrições e
**zero** no acompanhamento.

O **zero da listagem** é o número que importa: exibir o estado do requerimento por linha é leitura
por listagem, que este repositório já reprovou (`T-009`) — e não é meta de desempenho, é a decisão de
não colocar o dado ali.

Uma redação anterior previa **+2** na inscrição e **+2** no acompanhamento. A medição mostrou **+1**
e **zero**: a política pergunta em ordem e só busca a linha do requerimento quando o Edital declara,
e o acompanhamento simplesmente não exibe o requerimento. Acrescentá-lo lá para gastar o orçamento
previsto seria produzir leitura para satisfazer um número.

**Constraints**: nenhuma permissão nova; nenhuma escrita em identidade, inscrição ou requerimento
anterior; envio e sucessão tomam `FOR SHARE` **no Processo Seletivo**, para conflitar com o `FOR UPDATE` de
quem desfecha — e **não** no Edital, porque as duas juntas produzem *deadlock* contra as duas ordens
de travamento incompatíveis que já convivem neste repositório, e porque o par *versão aceita* +
*resumo da declaração* passou a sair do mesmo objeto de versão, de modo que não tem como divergir
(a razão inteira está no topo de `requerimentos/application/preencher.py`); nenhuma chamada a serviço externo em tempo de requisição; nenhum dado pessoal em URL, log
ou superfície pública; nenhum byte de conteúdo publicado reescrito

**Scale/Scope**: um requerimento por inscrição, algumas centenas por Edital. A base de CEP é da
ordem de **10⁶ linhas** — o `OpenCEP` declara 1.192.347 CEPs, e o `gpfconfea/banco-ceps`, que é o
dump efetivamente carregado, **não teve o seu tamanho medido** (`T-008`). Carregada por comando e
lida por chave primária. *Nem o número do OpenCEP se atribui à base escolhida, nem se afirma que ela
é a maior tabela do sistema: o que decide o desenho é a ordem de grandeza e o padrão de acesso*

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | "Requerimento de Matrícula", "declaração de veracidade" e "chamada em aberto" são termos dos Editais reais e do código existente. O único conceito novo — *momento da coleta* — é campo de duas opções, não entidade. E a `UX-058` **proíbe por varredura** o vocabulário da feature vizinha, que é a fronteira mais fácil de atravessar sem perceber | ✅ |
| **II — Integridade normativa e imutabilidade** | O campo novo entra no contrato de mutabilidade com natureza e razão (`FR-370`); o texto da declaração é retificável e o aceite guarda o resumo do que foi **exibido**, de modo que retificar não reescreve o que alguém leu (`FR-393`); requerimento enviado não muda nem é excluído, e a garantia é de gatilho (`FR-396`) | ✅ |
| **III — Segurança, proteção de dados e auditoria** | É o princípio mais exercido. Negar por padrão: titularidade em toda rota, recusa indistinguível de inexistente, sem listagem de dado pessoal (`FR-399`, `FR-400`). Minimização como **recusa escrita**: oito informações do formulário atual não são coletadas (`FR-382`), e a exceção consciente está nomeada. Base local em vez de serviço de terceiro, para não transmitir CEP de candidato identificado (`D-009`). Auditoria pelo mecanismo existente (`FR-397`) | ✅ |
| **IV — Regras explícitas e consistência** | Gatilho, autorização da sucessão e completude do envio moram no domínio e no banco, não na tela. Estados e transições explícitos, e **dois** deles persistidos — os outros três são derivados, como a vigência já é em três features | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md). A simplicidade é o eixo: **uma entidade**, dois estados, nenhum JSON, nenhum construtor de formulário, nenhuma permissão nova, nenhuma dependência | ✅ |
| **VI — Completude de jornada** | Cinco histórias priorizadas e uma jornada ponta a ponta (`C8` do quickstart). E o `T-002` é a guarda contra o defeito que a própria Constituição nomeia: há neste repositório um campo publicado **sem tela** — e esta feature não repete isso, por decisão escrita | ✅ |

### Invariantes do domínio tocados

| Invariante | Efeito |
|---|---|
| "Dados pessoais DEVEM obedecer a necessidade, finalidade e minimização" | vira lista: o que se coleta, o que se recusa, e a exceção declarada |
| "Documentos Exigidos PODEM variar por Edital, Perfil, modalidade…" | inalterado — o Anexo em papel continua sendo decisão de quem elabora (`FR-395`) |
| "Cada especificação DEVE avaliar os requisitos aplicáveis da LGPD" | §18 da spec, e a política de redação da amostra real alcança a própria documentação |
| "Entidades com ciclo de vida relevante DEVEM possuir estados e transições explícitos" | §12 da spec: dois estados persistidos, três derivados, uma transição |
| "APIs DEVEM ter contratos explícitos" | [contracts/requerimento-de-matricula.md](contracts/requerimento-de-matricula.md) |
| "Nada é excluído" | o gatilho recusa `DELETE` sobre enviado; o sucessor não apaga o antecessor |

**Sem violações. A tabela de Complexity Tracking fica vazia.**

---

## Project Structure

### Documentation (this feature)

```text
specs/029-requerimento-de-matricula/
├── plan.md              # Este arquivo
├── spec.md              # A especificação, com as clarificações de 16/09/2026
├── research.md          # Fase 0 — T-001 a T-013
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1 — C1 a C8
├── contracts/
│   └── requerimento-de-matricula.md
└── tasks.md             # Fase 2 — do $speckit-tasks, não deste comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── requerimentos/                    # módulo novo
│   ├── domain/
│   │   ├── nomes.py                  # estados, faixas de renda, cor/raça, códigos de recusa
│   │   ├── disponibilidade.py        # exigível? disponível? enviado? — a política que o domínio impõe
│   │   └── endereco.py               # a porta: referencia_de_cep(cep) -> … | None
│   ├── application/
│   │   ├── preencher.py              # abrir rascunho, gravar, enviar, suceder
│   │   └── selectors.py              # o estado do requerimento para a tela
│   ├── infrastructure/
│   │   └── referencia_local.py       # a implementação da porta, sobre ReferenciaDeCep
│   ├── management/commands/
│   │   └── carregar_ceps.py
│   ├── models.py
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_imutabilidade_do_enviado.py     # o gatilho condicional
├── processos/migrations/             # os dois campos do Edital
├── publicacoes/application/publish_edital.py    # emissão de matriculationRequest
├── publicacoes/domain/elevacao.py               # o degrau v15 → v16
├── shared/canonical.py                          # SCHEMA_VERSION 15 → 16
├── editais/domain/
│   ├── mutabilidade.py               # as duas classificações
│   └── validation.py                 # o achado impeditivo da FR-407
├── convocacao/application/selectors.py          # o seletor de chamada em aberto
├── inscricoes/application/submissao.py          # consulta a política antes de submeter
├── interface/                        # etapa Inscrição: declaração; dossiê: leitura
└── portal/                           # a tela do candidato

backend/tests/
├── unit/requerimentos/               # domínio, estados, faixas
├── integration/requerimentos/        # gatilho, restrições, sucessão
├── interface/                        # composição da declaração, dossiê
├── contract/                         # forma publicada, mutabilidade
├── acceptance/                       # C8 do quickstart
└── test_vocabulario_do_requerimento.py
```

**Structure Decision**: módulo novo `requerimentos/`, com a divisão domínio / aplicação /
infraestrutura que todo módulo deste repositório pratica. O requerimento **não** entra em
`inscricoes/` — é outro ato, com outro ciclo de vida e outra imutabilidade (`D-001`), e a `Inscricao`
é congelada justamente onde o requerimento precisa mudar.

---

## Ordem sugerida

*É a leitura do plano; a sequência executável é a do `tasks.md`.*

1. **A declaração do Edital** — dois campos, emissão no snapshot, as duas classificações de
   mutabilidade, o achado impeditivo, a oferta de retificação do texto, e a tela na etapa Inscrição.
   É o passo que destrava tudo, e é o que o `T-002` proíbe entregar sem interface.
2. **A entidade** — modelo, restrições, gatilho, privilégio, e a guarda de aplicação.
3. **O gatilho de disponibilidade** — o seletor único de chamada em aberto, a **política de domínio**
   que `abrir_rascunho`, `gravar`, `enviar` e a submissão da inscrição consultam, e os cinco estados.
   A política mora no domínio, e não na tela, porque o Princípio IV diz que validação de frontend
   **não é fronteira de segurança**.
4. **A tela do candidato** — pré-preenchimento por cópia, aceite, envio, conferência.
5. **O endereço** — a porta, a tabela de referência, o comando de carga, e a degradação.
6. **A sucessão** — autorizada por chamada em aberto, com a versão anterior legível.
7. **A leitura na gestão** — o bloco no dossiê.
8. **A demonstração** — a declaração no Edital do `seed_demo` que chega à convocação.

Os passos 1 a 4 fecham a `US1` e a `US3`. A `US2` precisa do 3; a `US5`, do 6.

---

## Riscos do plano

| Risco | Mitigação |
|---|---|
| O gatilho não é exercido no modo padrão da suíte | o teste roda no molde de `test_efeito_append_only`, com role de runtime real, e só contra PostgreSQL |
| Um campo novo no conteúdo publicado quebra três guardiões | é o comportamento desejado deles; o passo 1 os atualiza junto, não depois |
| A base de CEP é grande e o dump escolhido não foi medido | carga por comando, leitura por chave primária, ausência sem consequência (`FR-390`), e medição do dump como primeiro passo da tarefa que o carrega |
| "Chamada em aberto" reescrita no módulo novo | seletor único, e teste que prende a fonte |
| O Edital da demonstração não chegar à convocação | a escolha é tarefa explícita do passo 8, não efeito colateral |

---

## Complexity Tracking

*Sem violações da Constituição. Tabela vazia, de propósito.*
