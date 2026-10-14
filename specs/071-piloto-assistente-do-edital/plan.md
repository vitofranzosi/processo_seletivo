# Implementation Plan: O piloto interno do assistente conversacional do Edital (Fase B)

**Branch**: `claude/piloto-assistente-do-edital` (pasta `071-piloto-assistente-do-edital`), empilhada
sobre a `070` em `5e7cdd6c` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/071-piloto-assistente-do-edital/spec.md`, com as decisões
13º a 16º do usuário (*Clarifications*).

## Summary

A menor implementação que permite **conversar com o modelo, conferir as fontes e avaliar os
resultados** (16º). Ela tem cinco peças, e nenhuma delas é nova em espécie no repositório:

1. **As fontes** são a união das respostas da `070` para todas as perguntas e todos os Perfis,
   deduplicada, com a obrigatoriedade dos documentos como fonte calculada por Perfil e lista
   (`R-002`). Nenhuma leitura nova de Edital, nenhum PDF.
2. **A chamada** passa por uma porta com dois adaptadores pela biblioteca padrão, um para o Ollama e
   um para o OpenRouter, sem troca, sem retentativa, com o contexto fixo e os parâmetros sempre
   explícitos (`R-008`).
3. **A conferência** é uma função pura: fonte que existe, citação idêntica, número e data presentes
   na fonte citada, tipo coerente (`R-005`). Antes dela, a contagem de tokens pelo tokenizer do
   modelo, que recusa o excesso e acusa o corte (`R-006`, `R-007`).
4. **A conversa** é uma tabela, `TrocaDoPiloto`, que é ao mesmo tempo o histórico e o registro, sem
   identidade, com mascaramento simples (`R-011`, `R-015`). A tela é a da gestão, com uma permissão a
   mais nos papéis fixos (`R-010`).
5. **A avaliação** é um comando que roda a matriz pela mesma função da tela e escreve o relatório em
   arquivos, com a revisão humana numa planilha (`R-016`). A verificação de conexão e as medições
   ficam prontas para a L4 (`R-017`, `R-018`).

**O que não há:** fila, cache, serviço novo, painel de conversas, plataforma de provedores,
anonimização, busca vetorial, streaming, falso de demonstração, rota pública.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2, templates no servidor e CSS à mão na folha da gestão.

**Primary Dependencies**: **uma nova, opcional**: `tokenizers`, no grupo
`[project.optional-dependencies] assistente`, instalado só na máquina da equipe (`R-006`). Nenhuma
nas dependências de execução. O HTTP é `urllib.request`, como na fonte do sorteio. Reaproveita da
`070`:

| Da `070` | Para quê |
|---|---|
| `duvidas.application.consultar.contexto` | A versão, as futuras, os atos, o desfecho, o canal institucional |
| `duvidas.domain.respostas.responder` e `catalogo` | As fontes, por união das respostas (`R-002`), e o gabarito das doze perguntas |
| `duvidas.domain.canal` | O encaminhamento e os padrões de e-mail e telefone |
| `duvidas.domain.cobertura` | O guardião da cobertura das fontes |
| `duvidas.domain.estruturas` | Os tipos, as naturezas, `MudancaDeVersao` |
| `editais.domain.documentos.aplicabilidade` | A fonte calculada dos documentos por Perfil e lista |

E do repositório: `interface.identidade.PAPEIS`, `seguranca.application.authorization.require_permission`,
`processos.application.selectors.obter_edital`, as travas consultivas do padrão de
`avisos/application/despacho.py`, o `JsonFormatter`.

**Storage**: PostgreSQL. **Uma tabela nova**, `duvidas_trocadopiloto`, não append-only
([data-model.md](data-model.md) §3). A sessão do Django guarda só o identificador da conversa.

**Testing**: pytest, sem rede nenhuma (`R-019`). Unitários sem banco para fontes, mensagens,
conferência, orçamento, adaptadores e máscara; poucos casos transacionais contra PostgreSQL para a
versão entre turnos, o teto, o orçamento e a exclusão; interface para o acesso, os estados e a
acessibilidade; guardiões da credencial, da produção e da chamada única. As rodadas com serviço
real, a verificação e as medições ficam **fora da suíte**.

**Target Platform**: a máquina da equipe, com as configurações de desenvolvimento e o seletor de
identidade (`D-012` da spec). Na produção, nada muda além do `_exigir` que recusa o serviço externo.

**Project Type**: monólito web Django; uma tela de gestão, três comandos de gestão e um script.

**Performance Goals**: a montagem das fontes do 92/2026 em menos de 1 s, medida (`R-002`); o
tempo-limite da chamada em 90 s, abaixo dos 120 s do servidor (`R-013`). As metas de latência do
modelo são da DP-3, e só se medem na L4.

**Constraints**:

- Nenhuma chamada a serviço real na suíte.
- Nenhuma retentativa; no máximo uma chamada por pergunta.
- Nenhuma fonte cortada; o excesso é estado.
- Nenhuma credencial fora do ambiente do processo.
- Nenhum texto em log; nenhuma identidade no registro.
- 375 px sem rolagem horizontal.

**Scale/Scope**:

- No `duvidas`: cinco módulos de domínio e aplicação, a porta e dois adaptadores, a contagem, um
  modelo e uma migration, três comandos, a matriz em JSON.
- Uma view, um template, um link na página do Edital, um papel e uma permissão.
- Um script de medição.
- Perto de 70 casos unitários, 8 de integração e 10 de interface.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o respeita | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Assistente do Edital", "piloto", "troca", "fonte", "conferência", nomes próprios e qualificados; os tipos e as naturezas reaproveitam os códigos da `070`, e só o rótulo de `RESPONDIDA` muda no piloto, por decisão registrada (`D-011` da spec) | ✓ |
| II. Fonte única, imutabilidade, temporalidade | A única fonte é a leitura da `070` sobre a versão consolidada vigente no instante de cada pergunta. Nada de cópia, índice ou banco editorial (`R-002`). Retificação futura dita pela aplicação, nunca aplicada antes. O histórico de outra versão não volta (`FR-1495`). A tabela nova não guarda conteúdo normativo além do que foi citado, como evidência da resposta | ✓ |
| III. Negar por padrão, auditoria, LGPD | Alcance de `obter_edital` **e** permissão explícita, verificados no servidor a cada requisição; fora deles, a negativa inventariada (`R-010`). Credencial só no ambiente. Log sem texto. Registro sem identidade, com mascaramento declarado como não anonimização, exclusão em 90 dias (`R-015`, `R-021`). A seção de LGPD da spec avalia o tratamento. A validação institucional segue como dependência da Fase C | ✓ |
| IV. Regras explícitas, derivação explícita | O que o modelo produz aparece como produzido, separado das fontes; cada trecho diz a natureza; a referência mostrada é a da aplicação, e não a paráfrase do modelo (`FR-1489`). A tela diz que as respostas podem conter erros. Concorrência: teto global por trava consultiva; versão relida a cada pergunta; nenhuma transação longa durante a chamada | ✓ |
| V. Simplicidade e rastreabilidade | Uma dependência opcional, justificada abaixo; uma tabela; nenhuma fila, cache, serviço ou vetor. Fila e Redis examinados e descartados (`D-008` da spec). Cada troca leva a impressão das fontes e a versão das instruções; cada rodada, o commit | ✓, com a dependência justificada |
| VI. Jornada demonstrável | A pessoa do setor, numa sessão acompanhada, pela gestão, sem banco nem shell, pergunta, continua e confere as fontes ([quickstart.md](quickstart.md) C; `SC-559`). A conclusão exige isso no serviço local | ✓ |

**Re-check depois do desenho:** ✓.

- O data-model acrescenta uma tabela, sem identidade, e nenhuma coluna em tabela existente.
- Os contratos não expõem nada fora da versão consultada; a única saída para fora da rede é a do
  serviço externo, recusada na produção e recusada para pergunta com padrão pessoal.
- O desenho não acrescenta processo nem serviço à implantação.
- A escrita em artefatos de outras specs é a de sempre para tela nova: uma linha no inventário da
  `033`, uma entrada em `MODULOS_DE_VIEW` (`R-020`). Nenhum código da `070` muda de comportamento.

## Project Structure

### Documentation (this feature)

```text
specs/071-piloto-assistente-do-edital/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── saida-do-modelo.md
│   ├── servico-de-inferencia.md
│   ├── tela.md
│   └── comandos.md
├── checklists/requirements.md
├── avaliacao/                 # os relatórios datados das rodadas e das medições, quando houver
└── tasks.md                   # $speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml                         # o grupo opcional `assistente`
├── config/settings/
│   ├── base.py                            # as variáveis ASSISTENTE_* (R-009)
│   ├── production.py                      # o _exigir do serviço local
│   └── test.py                            # piloto ligado, serviço vazio
├── processo_seletivo/duvidas/
│   ├── domain/
│   │   ├── estruturas_do_piloto.py        # data-model §2 e §4
│   │   ├── fontes.py                      # R-002
│   │   ├── mensagens.py                   # R-003, R-004, R-007
│   │   ├── conferencia.py                 # R-005
│   │   └── mascara.py                     # R-015
│   ├── application/
│   │   └── perguntar.py                   # R-011, R-012
│   ├── infrastructure/
│   │   ├── tokens.py                      # R-006
│   │   └── inferencia/
│   │       ├── __init__.py                # a porta, a Devolucao, as falhas, a parte comum
│   │       ├── ollama.py
│   │       └── openrouter.py
│   ├── models.py                          # TrocaDoPiloto
│   ├── migrations/0001_initial.py
│   ├── avaliacao/matriz.json              # CA-01–32, as doze, CB-01–16
│   └── management/commands/
│       ├── avaliar_assistente.py          # R-016
│       ├── verificar_servico_de_inferencia.py   # R-017
│       └── excluir_registros_do_piloto.py # R-021
├── processo_seletivo/interface/
│   ├── assistente.py                      # a view
│   ├── templates/interface/assistente.html
│   ├── identidade.py                      # o papel e a permissão
│   └── urls.py
├── scripts/carga_do_assistente.py         # R-018
├── scripts/publicar_corpus_do_piloto.py   # o corpus no banco da equipe, para a avaliação
└── tests/
    ├── fixtures/inferencia.py             # a porta falsa e o contador falso
    ├── unit/duvidas/test_fontes.py, test_mensagens.py, test_conferencia.py, test_orcamento.py,
    │   test_tokens.py, test_mascara.py, test_adaptador_openrouter.py, test_adaptador_ollama.py,
    │   test_verificar_servico.py, test_log_do_piloto.py
    ├── integration/duvidas/test_perguntar.py, test_continuacao.py, test_teto_e_orcamento.py,
    │   test_avaliar_assistente.py, test_exclusao.py
    ├── interface/test_assistente.py
    └── test_credencial_do_assistente.py
```

**Structure Decision**: tudo no pacote `duvidas`, que é o produto (`R-001`); a tela em `interface/`,
como a da `070`.

## A ordem mínima

A spec tem sete histórias; a ordem abaixo entrega primeiro o que permite conversar e conferir, e
deixa para o fim o que depende da L4. Cada degrau é demonstrável sozinho.

| Degrau | O que fica pronto | Histórias | Depende de |
|---|---|---|---|
| 1 | Fontes completas, mensagens, contagem, orçamento, conferência — tudo puro e testado, sem rede | US5, parte da US1 e da US3 | — |
| 2 | A porta, o adaptador do OpenRouter, o `perguntar`, a tabela, a tela, o papel | US1, US2, US4 | 1; chave do OpenRouter para o uso real |
| 3 | O comando de avaliação e a matriz | US6 | 2 |
| 4 | O adaptador do Ollama e a verificação de conexão | US4, US7 | 2; para o uso real, a L4 |
| 5 | O script de medição e o relatório | US7 | 4 e a L4 |
| 6 | A exclusão | — | 2 |

**O mínimo para conversar, conferir e avaliar** são os degraus 1 a 3, com o OpenRouter. O adaptador do
Ollama do degrau 4 se escreve e se testa com `urlopen` substituído antes do acesso; o que só a L4
prova fica em tarefas bloqueadas.

## Riscos e o que se mede antes de afirmar

| Risco | Como aparece | O que se faz |
|---|---|---|
| A união das respostas é lenta no 92/2026 | Mais de 1 s na montagem | Medir; memorizar por versão e minuto só se passar (`R-002`) |
| Cartão da `070` que muda com o parâmetro | O guardião de colisão falha | Tratar como a obrigatoriedade: fonte calculada, ou excluir o cartão com motivo (`R-002`) |
| A conferência recusa respostas certas | Recusa indevida alta no `resumo.md` | Ajustar a normalização, como alteração do `R-005` |
| O acréscimo por mensagem está errado | Tokens informados acima ou abaixo do medido | A verificação mede; a margem de 5% protege (`R-006`, `R-007`) |
| O Ollama instalado não aceita `truncate`/`shift` | A verificação diz "não aceitos" | A conferência da contagem é a proteção; registrado no relatório |
| O OpenRouter devolve o `model` com variação de grafia | `MODELO_DIFERENTE` em toda resposta | Conferir na primeira rodada; se a grafia for estável e documentada, a comparação passa a aceitá-la, como alteração do contrato |
| O Edital real não cabe no contexto medido na L4 | `EXCEDE_O_CONTEXTO` | É a evidência que o `FR-1478` pede para abrir a seleção de fontes — alteração da spec |

## Complexity Tracking

| Acréscimo | Por que é necessário | Alternativa mais simples, e por que não serve |
|---|---|---|
| `tokenizers`, dependência opcional | A spec exige contar com o tokenizer do modelo, antes de enviar, para que nada seja cortado em silêncio (`FR-1479`) | Bytes como teto: seguro e quatro vezes pessimista, recusaria Editais que cabem. BPE em Python puro: pede o pacote `regex`. Contar pelo serviço: o Ollama só conta processando o prompt na GPU (`R-006`) |
| Uma tabela | O histórico precisa morar no servidor (`FR-1494`) e o registro precisa existir (14º); uma tabela serve aos dois | Sessão para o histórico e arquivo para o registro: duas cópias dos mesmos turnos (`R-011`) |
| Três comandos e um script | Avaliar, verificar e medir sem tela (16º), e excluir por prazo (14º) | Um comando com subcomandos: o mesmo código com mais opções num lugar só, e a exclusão misturada com a avaliação |
