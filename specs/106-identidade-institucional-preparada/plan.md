# Implementation Plan: Identidade institucional preparada

**Branch**: `claude/eloquent-wing-4d768b` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/106-identidade-institucional-preparada/spec.md`, com
D-001 a D-012 no [research.md](research.md).

## Summary

O Django Auth passa a guardar a pessoa institucional (D-001), com um identificador interno
`pessoa-<uuid4>` que o banco não deixa mudar (D-002). Três tabelas append-only no app `seguranca`
— identidade externa, vínculo e revogação — guardam a associação com o provedor e quem pode o quê
em cada unidade (D-003). `ator_da_sessao` ganha uma segunda origem, a institucional, que recalcula o
`Actor` a cada requisição a partir dos vínculos vigentes da unidade ativa (D-006); a origem de
demonstração não é tocada. Um adaptador de contrato fixo entrega a identidade autenticada (D-007),
e nos testes ele é um provedor simulado sem rede. A concessão e a revogação são funções da camada de
aplicação, com as regras do estudo e trilha (D-005); o primeiro administrador institucional nasce
por comando. `production.py` recusa provedor de teste e *backend* de senha, e o seletor passa a se
recusar também em execução sob a marca de produção (D-009).

**Onde está o risco**: em mexer em `interface/identidade.py`, de que 260 arquivos de teste
dependem. A mudança ali é aditiva: um ramo novo para a origem institucional, e uma conferência a
mais em `seletor_disponivel()` que só morde com a marca de produção.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django (`django.contrib.auth`, já
instalado); nenhuma nova.

**Storage**: PostgreSQL. Uma migration nova, `seguranca/0001_initial`: três tabelas append-only
(o `M` do `provisionar` passa de 41 a 44) e dois gatilhos sobre a `auth_user`.

**Testing**: pytest contra PostgreSQL. Testes novos em `backend/tests/seguranca/`, com o provedor
simulado em `backend/tests/fixtures/provedor_simulado.py`; recusas de produção em
`tests/test_configuracao_producao.py`.

**Target Platform**: `/gestao/` (entrada, retorno, troca de unidade) e a camada de aplicação de
`seguranca`.

**Performance Goals**: a resolução do `Actor` institucional em no máximo duas consultas por
requisição (SC-1005); zero consultas a mais no modo demonstração (SC-1006).

**Constraints**: o seletor não muda (FR-3001); nenhuma rota nova levanta 404 (D-012); nenhum
template novo; CSP sem inline; `ruff check` e `ruff format --check`; citações FR-/SC-/D- conferidas.

**Scale/Scope**: dois módulos novos em `seguranca` (`acessos.py`, `autenticacao.py`), um de
aplicação (`seguranca/application/acessos.py`), `models.py` e a migration; um comando; ramos novos
em `interface/identidade.py`, três views; `base.py` e `production.py`.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | Pessoa, vínculo, revogação, unidade ativa: os nomes do estudo, em português. |
| II. Imutabilidade; nada se exclui | Vínculo, revogação e identidade externa append-only nas duas camadas; a pessoa não se exclui e o identificador não muda; nenhuma tabela existente alterada (FR-3030). |
| III. Negar por padrão, menor privilégio, auditoria | Sem vínculo, sem `Actor`; a concessão exige capacidade e escopo, recusa autoconcessão e vai à trilha com motivo; o administrador institucional não tem poder operacional; nenhum identificador do cliente é aceito. LGPD: nome e e-mail do servidor são o mínimo para exibir e contatar, e entram na política de retenção (B-2). |
| IV. Regras explícitas | Cada recusa é `DomainError` com código próprio, e o 403/404 segue a doutrina da `033`. |
| V. Rastreabilidade e simplicidade | Spec, plano, tarefas, matriz; nenhuma tela e nenhum framework novo; o Django Auth no lugar de código de sessão próprio. |
| VI. Jornada demonstrável | A jornada de homologação é preservada e provada pela suíte; a institucional se demonstra pelos testes de tela com o provedor simulado, e só ali, porque o SSO real está fora. |

**Resultado**: passa. Pós-desenho: passa — nada do data-model contraria os princípios.

## Project Structure

```text
specs/106-identidade-institucional-preparada/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md
├── contracts/adaptador-e-configuracao.md
├── checklists/requirements.md
├── tasks.md · rastreabilidade.md · verificacao.md

backend/processo_seletivo/seguranca/
├── acessos.py                      # novo: catálogo de acesso, escopo institucional (D-004, D-011)
├── autenticacao.py                 # novo: IdentidadeAutenticada, backend, provedor configurado (D-007, D-008)
├── models.py                       # novo: IdentidadeExterna, Vinculo, RevogacaoDeVinculo
├── migrations/0001_initial.py      # novo: tabelas e gatilhos
├── application/acessos.py          # novo: conceder, revogar, vigentes, ator institucional, sessão
├── management/commands/conceder_administracao_institucional.py   # novo (FR-3029)
├── papeis.py                       # +3 em TABELAS_APPEND_ONLY

backend/processo_seletivo/interface/
├── identidade.py                   # origem institucional; seletor recusado sob produção
├── views.py                        # entrar, retorno, unidade ativa; sair encerra a institucional
├── urls.py
├── templates/interface/identificar.html   # botão institucional só com provedor

backend/processo_seletivo/unidades/application/sincronizacao.py   # recusa o código reservado
backend/config/settings/base.py · production.py

backend/tests/
├── fixtures/provedor_simulado.py
├── seguranca/                      # os doze testes do pedido e o resto
├── migrations/test_migrations.py   # seguranca nas listas de apps e gatilhos

doc/
├── diagnostico-autenticacao-da-gestao-2026-10-30.md · decisao-identidade-e-autorizacao-da-gestao.md
├── homologacao-com-o-seletor-de-demonstracao.md · ativacao-do-sso-institucional.md
```

## Ordem

1. Modelos, migration e `TABELAS_APPEND_ONLY` (incremento B).
2. Catálogo e regras de concessão e revogação (B).
3. *Backend*, resolução do `Actor`, sessão institucional (B).
4. Provedor simulado e rotas (C).
5. Recusas de produção e o seletor sob a marca de produção (D).
6. Comando de implantação (D).
7. Documentos e verificação.
