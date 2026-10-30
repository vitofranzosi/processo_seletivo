# Implementation Plan: Gestão de acessos pela interface

**Branch**: `claude/107-gestao-de-acessos`, sobre `claude/eloquent-wing-4d768b` em `8af15129` |
**Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: a spec, com D-001 a D-014 no [research.md](research.md). **Aprovação**: o pedido de
30/10/2026 autoriza a execução até a entrega do incremento 1, sem merge e sem produção; as
decisões institucionais pendentes ficam fora do que se implementa.

## Summary

Seis telas e uma mudança na resolução do ator, todas no modo institucional da `106`. A tela sem
acesso e o nome na barra (D-007, D-008); o seletor de unidade na barra (D-006); "Acessos da unidade"
e "Administração de acessos", as duas sobre um mesmo par de views parametrizado por nível (D-002),
com busca de pessoas (D-005), confirmação que reconfere (D-003) e o histórico lido das tabelas; o
prazo da sessão, com relógio injetável (D-009, D-010). Nenhuma tabela nova. As regras de concessão
são as da `106`, com uma recusa a mais: pessoa inativa (D-011). A prova pelo navegador é Playwright
contra o `live_server`, com a página do provedor servida pelo próprio teste (D-012, D-013).

**Onde está o risco**: em `interface/identidade.py` e no `base.html`, de que toda a suíte depende. A
mudança é do ramo institucional; a demonstração continua lendo o que lia, e o `nome_do_ator` dela é
o mesmo `subject` que a barra já mostrava.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; Playwright no grupo opcional
`navegador`, só para teste.

**Storage**: PostgreSQL. **Nenhuma migration** (`FR-3134`): o `M` do `provisionar_papeis` continua
**44**.

**Testing**: pytest contra PostgreSQL. Casos de cliente em `tests/seguranca/` (telas, busca,
prazos, concorrência, privilégios); jornada pelo navegador em `tests/navegador/`; recusas de produção
em `tests/test_configuracao_producao.py`.

**Target Platform**: `/gestao/` — `sem-acesso`, `acessos`, `acessos/conceder`,
`acessos/vinculos/<id>/revogar`, e as mesmas três sob `administracao-de-acessos`.

**Performance Goals**: a resolução do ator institucional continua em no máximo duas consultas
(`SC-1005` da `106`); a demonstração não faz consulta a mais (`SC-1016`).

**Constraints**: CSP sem `unsafe-inline` — estilo em arquivo; nenhum script novo é necessário.
Toda classe nova no template precisa de regra na folha.

## Constitution Check

| Princípio | Como se cumpre |
|---|---|
| Negar por padrão | toda tela confere capacidade **e** sessão institucional no servidor (`FR-3127`); o link ausente não é a defesa (`FR-3128`) |
| Nada se exclui; publicação imutável | nenhuma tabela, nenhuma migration; revogar é acrescentar a revogação da `106` |
| Auditoria | concessão e revogação pelas funções da `106`, na mesma transação da trilha; o término por prazo vai à trilha |
| Operações relevantes com confirmação e consequência | a confirmação de `FR-3116` |
| Cenário demonstrável | a jornada pelo navegador (`FR-3131`) e o roteiro do [quickstart](quickstart.md) |
| Governança do usuário | P1 a P4 ficam perguntas; o mecanismo de prazo não decide os valores em produção |

Sem violação. Complexidade a justificar: uma dependência de teste nova (D-012).

## Project Structure

```text
backend/
├── config/settings/{base,production}.py      # prazos da sessão (D-009, D-010)
├── processo_seletivo/
│   ├── interface/
│   │   ├── acessos.py                        # views das telas de acesso (D-002)
│   │   ├── identidade.py                     # resolução, prazos, sem acesso, nome (D-006–D-009)
│   │   ├── navegacao.py                      # dois itens novos na barra
│   │   ├── urls.py
│   │   ├── static/interface/telas/acessos.css
│   │   └── templates/interface/
│   │       ├── base.html                     # nome, seletor de unidade
│   │       ├── identificar.html              # nome, motivo do término
│   │       ├── sem_acesso.html
│   │       ├── acessos.html                  # quem atua, histórico
│   │       ├── acessos_conceder.html         # busca e escolha
│   │       └── acessos_confirmar.html        # a confirmação dos dois atos
│   └── seguranca/
│       ├── application/acessos.py            # busca, histórico, pessoa inativa (D-005, D-011)
│       └── relogio.py
└── tests/
    ├── fixtures/provedor_simulado.py         # endereço de autorização variável (D-013)
    ├── navegador/                            # Playwright (D-012)
    └── seguranca/test_{telas_de_acesso,sessao_com_prazo,concorrencia_das_telas}.py
specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # D-014
```

## Fases

1. **Núcleo** — busca, histórico, administradores por unidade e a recusa de pessoa inativa na
   camada de aplicação; relógio; resolução lendo todos os vínculos de uma vez.
2. **Sessão** — prazos, término com trilha e motivo, configuração e recusa de produção.
3. **Telas** — sem acesso, barra, as duas telas de acesso, folha, navegação, inventário.
4. **Navegador** — o provedor de teste, a jornada das cinco histórias, o comando para assistir.
5. **Documentação e verificação** — roteiros, verificação, rastreabilidade, `make lint check
   test-pg`, CI.

## Ordem de integração

1. PR #345 (`106`) na `main`.
2. Este PR, rebaseado ou com a base trocada para a `main` depois do passo 1.

Esta branch não muda o que o #345 entrega, salvo a recusa de pessoa inativa (D-011) e o
`redirect_uri` do provedor simulado (D-013), que é código de teste.
