# Implementation Plan: A habilitação do assistente do Edital pela interface do sistema

**Branch**: `claude/170-habilitacao-do-assistente-12c936` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: a spec revista em 14/11, com as respostas do usuário às perguntas Q-1 a Q-4 e o recorte
da entrega.

## Summary

O administrador institucional habilita o piloto da gestão (uma vez por implantação) e a página
pública de cada Edital pela interface, com motivo. Fora de produção, o ato basta: não é preciso
chave de demonstração nem os requisitos da abertura. Em produção, a página pública continua fechada
pelo backend.

Toda a mudança cabe nas estruturas que já existem:

- **uma tabela append-only** no app `duvidas`;
- **uma permissão** no papel Administrador institucional;
- **uma página** na administração institucional, no molde de Unidades da `110`;
- **uma função de leitura**, chamada nos cinco pontos que hoje leem as chaves;
- a separação por **`AMBIENTE_DE_PRODUCAO`**, que o `production.py` já define;
- **um teste de navegador** que percorre o caminho inteiro.

Não há papel novo, nem app novo, nem mecanismo de configuração.

## Technical Context

**Language/Version**: Python 3.13, Django (o monólito existente).

**Primary Dependencies**: as do projeto. O grupo opcional `assistente`, que traz a `tokenizers`,
só entra na leitura da configuração (FR-7501). Playwright, do grupo `navegador`, só para o teste de
navegador.

**Storage**: PostgreSQL. Uma tabela nova, `duvidas_habilitacao_do_assistente`, com gatilho
append-only e sem privilégio de UPDATE ou DELETE para o runtime.

**Testing**: pytest contra PostgreSQL (`make test-pg`). Um teste de navegador em `tests/navegador/`.
O serviço do modelo é a porta falsa da suíte (`tests/fixtures/inferencia.py`).

**Target Platform**: o servidor Linux do guia de implantação. Os testes rodam na máquina da equipe
e no ambiente de homologação funcional da `110`.

**Project Type**: aplicação web, o monólito Django.

**Performance Goals**: a conferência da habilitação faz no máximo uma consulta por requisição, pelo
índice de frente e Edital. A página do administrador não chama o modelo.

**Constraints**:

- a CSP sem `unsafe-inline`: estilo em arquivo, e não no template;
- nada de `select_for_update` em tabela append-only, porque o runtime não tem UPDATE (a memória
  "FOR UPDATE em append-only falha como runtime");
- a credencial nunca sai do ambiente.

**Scale/Scope**: um registro pequeno, com dezenas de atos por ano. Uma página, duas
confirmações, e os cinco pontos de leitura.

## Constitution Check

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "habilitar", "piloto", "página pública", "requisitos da abertura": termos das specs `071` e `074` | ✔ |
| II. Imutabilidade | não toca ato normativo. Os atos de habilitação são append-only (gatilho e privilégio), e desabilitar é ato novo | ✔ |
| III. Segurança e auditoria | permissão explícita, conferida na aplicação, com escopo institucional; a demonstração é recusada; evento na trilha na mesma transação; a credencial não aparece; LGPD avaliada na spec | ✔ |
| IV. Regras explícitas | a regra "quem atende" é uma função só, usada pelos cinco leitores; produção é conferida no backend | ✔ |
| V. Simplicidade e rastreabilidade | uma tabela e uma permissão; nenhum papel, app ou mecanismo novo; a matriz de rastreabilidade entra com a implementação | ✔ |
| VI. Jornada demonstrável | o teste de navegador do percurso (SC-2451) e a demonstração com o serviço real (SC-2457) | ✔ |

Nenhuma violação, e não há o que registrar em *Complexity Tracking*. A reconferência depois do
desenho deu o mesmo resultado.

## Project Structure

### Documentação (esta feature)

```text
specs/170-habilitacao-do-assistente/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # as decisões técnicas, R-1 a R-10
├── data-model.md        # a tabela e a regra de quem atende
├── quickstart.md        # o percurso, a demonstração e a conferência de produção
├── contracts/tela.md    # a página, as confirmações, as recusas e o aviso ao visitante
└── checklists/requirements.md
```

### Código (o que muda)

```text
backend/
├── config/settings/
│   ├── base.py                   # comentários das chaves: atalho de demonstração (FR-7506)
│   ├── production.py             # recusa ASSISTENTE_PILOTO; serviço e tempo-limite sem depender da chave (FR-7505)
│   └── test.py                   # o atalho continua ligado; os casos novos o desligam (R-7)
├── processo_seletivo/
│   ├── duvidas/
│   │   ├── models.py             # HabilitacaoDoAssistente
│   │   ├── migrations/0003_habilitacao_do_assistente.py   # tabela, constraint e gatilho
│   │   ├── domain/nomes.py       # a permissão, os códigos de recusa e a lista RA-1 a RA-12
│   │   ├── application/habilitacao.py                     # ler, atende?, conferir, habilitar, desabilitar
│   │   ├── infrastructure/inferencia/__init__.py          # configuracao_do_servico(), sem rede (R-6)
│   │   └── management/commands/avaliar_assistente.py      # deixa de conferir a chave (FR-7509)
│   ├── seguranca/
│   │   ├── acessos.py            # "assistente:habilitar" no Administrador institucional (FR-7510)
│   │   └── papeis.py             # a tabela em TABELAS_APPEND_ONLY (M sobe para 66)
│   ├── interface/
│   │   ├── habilitacao_do_assistente.py                   # as views da página (molde de unidades.py)
│   │   ├── urls.py               # administracao-do-assistente/...
│   │   ├── navegacao.py          # a seção em SECOES_DE_ACESSO, ao lado de Unidades
│   │   ├── assistente.py         # _edital_do_piloto e _conversa usam a regra (FR-7515, FR-7525)
│   │   ├── painel_do_assistente.py                        # conversa_da_sessao recebe a marca da habilitação
│   │   ├── views.py              # a entrada e a linha do Edital (FR-7515, FR-7522)
│   │   ├── trilha_da_unidade.py  # as duas operações, em palavras
│   │   ├── templates/interface/habilitacao_do_assistente*.html
│   │   └── static/interface/...  # a folha da página (bloco estilo_da_pagina)
│   └── portal/
│       ├── assistente.py         # _edital_com_pagina e painel usam a regra; aviso de encerrado (FR-7520, FR-7524)
│       ├── templates/portal/selecao.html                  # o aviso (UX-813)
│       └── static/portal/portal.css
└── tests/
    ├── integration/duvidas/test_habilitacao.py            # atos, permissão, produção, conversa nova
    ├── interface/test_habilitacao_do_assistente.py        # a página: configuração, sem segredo, sem chamada
    ├── portal/test_assistente_habilitado.py               # Edital A × B, aviso, 404 em produção
    ├── navegador/test_jornada_do_assistente.py            # o percurso (SC-2451)
    ├── test_configuracao_producao.py                      # as recusas novas (SC-2453)
    └── migrations/test_migrations.py                      # duvidas: 2 → 3; o gatilho em TRIGGERS_POR_APP
```

## Ordem de implementação

Um PR só, este, em quatro commits que se testam um a um:

1. **O registro.** A tabela, a migration e o gatilho; a permissão no papel; `habilitacao.py` com os
   atos, a trava, o motivo, a recusa do ato que não muda nada, a recusa de produção para a página
   pública e o evento na trilha. Testes de integração, e os guardiões de migração e de privilégio.
2. **Os leitores.** A função "quem atende" nos cinco pontos; a marca da habilitação na chave da
   conversa; o aviso de encerrado; as recusas do `production.py`. Testes do portal, da gestão e da
   configuração de produção. As suítes da `071` e da `074` têm de passar sem mudança (SC-2455).
3. **A página.** As views, as confirmações, a seção da barra, a linha do Edital na gestão e a folha.
   Testes da página e dos guardiões de CSP, acessibilidade e vocabulário.
4. **O percurso e a documentação.** O teste de navegador; o `CLAUDE.md`/`AGENTS.md` (o `M` de 65
   para 66), o guia de implantação, o `.env.example`, as notas na `071` e na `074`, o README e a
   `rastreabilidade.md`. Depois, a demonstração com o serviço real (SC-2457), com capturas, e a
   suíte inteira com `make test-pg`.

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| A `169` (#552) também acrescenta tabela append-only, seção na barra e recusa no `production.py` | conflito de merge e o `M` contado errado | quem mergear depois reconta o `M` e refaz a ordem das seções; os dois PRs não compartilham código, porque o mecanismo comum está fora do escopo |
| A ampliação do papel chega a quem já o tem | um administrador de acessos passa a abrir o assistente sem decisão | passo 0 do quickstart: listar os vínculos vigentes do papel e pedir autorização antes do deploy, como na `110` |
| Uma habilitação de teste chega a produção num banco copiado | o painel abriria ao público | a regra lê `AMBIENTE_DE_PRODUCAO` a cada requisição (FR-7519), com teste |
| Os testes da `071` dependem de `ASSISTENTE_PILOTO = True` no `test.py` | quebrar dezenas de casos | o atalho continua ligado no `test.py`; os casos novos o desligam (R-7) |
| A porta falsa da suíte não alcança o `live_server` do teste de navegador | o percurso chegaria à rede | conferir na tarefa 4 como as jornadas da `121` e da `110` injetam dependência; sem rede por padrão, a chamada termina em "serviço não configurado", e o teste mede a ausência de chamada pela porta falsa |

## Complexity Tracking

Nada a justificar.
