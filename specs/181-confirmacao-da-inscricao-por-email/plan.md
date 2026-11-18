# Implementation Plan: A confirmação da inscrição por e-mail diz o que aconteceu, uma vez, e deixa rastro

**Branch**: `claude/gps-auto-confirmation-email-85c434` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

## Summary

A confirmação já sai (`inscricoes/application/mensagem.py`, chamada por `portal/views.py`
`_confirmar_por_email` depois de `enviar_inscricao`). Esta feature não cria remetente, fila, tabela
nem estado: **envolve o envio que existe** num módulo novo, `inscricoes/application/confirmacao.py`,
que

1. trava a inscrição (`pg_advisory_xact_lock`, a mesma técnica de `_travar_o_par`);
2. lê, na trilha de auditoria, as tentativas anteriores (`operation="CONFIRMAR_POR_EMAIL"`, agregado
   `Inscricao`) e **não envia** se alguma foi aceita (FR-8351);
3. envia pelo remetente declarado, que passa a **contar** o retorno do servidor (FR-8360);
4. grava a tentativa na trilha, num ponto de salvamento, com número e resultado — sem endereço
   (FR-8358).

A view do envio passa a chamar `confirmacao.confirmar`, e uma rota nova de `POST`,
`portal:comprovante-confirmacao`, faz o mesmo a pedido da titular (FR-8363). O comprovante lê a última
tentativa e diz o que aconteceu (FR-8362), com a palavra "Inscrição enviada" no topo (FR-8365). Sem
sessão, o comprovante leva ao acesso e volta (FR-8357), como a convocação da `121`. O modelo da
mensagem muda de texto: assunto com o Edital, "enviada", o que acontece agora, e o botão
"Ver meu comprovante", que leva ao comprovante da inscrição.

## Technical Context

**Language/Version**: Python 3.13, Django 5 (monólito existente)
**Primary Dependencies**: nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration** — a trilha (`auditoria.RegistroAuditoria`) já tem
`detalhe` em JSON e o índice `(aggregate_type, aggregate_id, occurred_at)`
**Testing**: pytest contra PostgreSQL (`make test-pg`), backend de correio `locmem` e um backend que
falha, criado no próprio teste; a concorrência por duas threads com conexões próprias
(`transaction=True`)
**Target Platform**: servidor Linux; portal no navegador, celular incluído
**Project Type**: web, renderização no servidor, sem JavaScript novo
**Performance Goals**: uma consulta a mais no comprovante (a última tentativa, por índice); o envio
continua limitado por `EMAIL_TIMEOUT`
**Constraints**: CSP sem inline (classes que já têm regra em `portal.css`); FR-084a da `010` (sem CPF,
telefone nem link que autentica); `tests/test_situacoes_de_mensagem.py` (nenhum módulo novo põe
mensagem na fila — `confirmacao.py` chama o remetente declarado); o PDF e o código de verificação do
comprovante não mudam (D-004)
**Scale/Scope**: dois módulos de `inscricoes`, duas views e uma rota do portal, dois modelos de
mensagem, um template do portal

## Constitution Check

| Princípio | Como esta feature o respeita |
|---|---|
| I. Linguagem ubíqua | "enviada" é a palavra da área do candidato para o ato; "recebida" fica reservada ao degrau da `148` na mensagem (D-004) |
| II. Imutabilidade | nada do ato muda: a inscrição enviada não ganha campo, e o documento comprovante fica como está (FR-8366); a trilha só acrescenta |
| II. Nada é excluído | sem migration; nenhuma linha sai |
| III. Proteção de dados | a mensagem continua sem CPF e telefone, e sem anexo (D-001); a trilha não guarda endereço nem erro do servidor (FR-8358); o log, o identificador da inscrição e não o endereço (FR-8361) |
| III. Negar por padrão | a nova tentativa exige sessão e titularidade, e responde como inexistente nos demais casos (FR-8364); o comprovante sem sessão redireciona sem consultar (FR-8357) |
| IV. Consistência operacional | envio depois do commit, falha que não desfaz o ato (FR-8352); trava por inscrição e leitura da trilha antes de enviar (FR-8351) |
| V. Rastreabilidade e simplicidade | nenhum estado, tabela, fila ou serviço novo (D-002); `rastreabilidade.md` cobre FR-8350 a FR-8368, SC-2920 a SC-2925, UX-1020 a UX-1022 e cada caso-limite |
| VI. Completude de jornada | falhou → a tela diz → a titular tenta de novo → a tela diz que saiu; e-mail → link → código → comprovante |

Sem violação.

## Project Structure

### Documentation (this feature)

```text
specs/181-confirmacao-da-inscricao-por-email/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # as escolhas técnicas (R1 a R6)
├── data-model.md         # a tentativa na trilha
├── contracts/portal.md   # o comprovante, a nova tentativa e a mensagem
├── quickstart.md         # o roteiro de verificação
├── tasks.md              # (speckit-tasks)
├── rastreabilidade.md    # (na implementação)
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── inscricoes/application/
│   ├── confirmacao.py                    # novo: trava, tentativas, confirmar
│   └── mensagem.py                       # o remetente passa a contar o retorno e a dizer de qual inscrição falhou
├── inscricoes/templates/inscricoes/mensagem/
│   ├── comprovante.txt                   # o assunto e o texto novos
│   └── comprovante.html                  # idem, na moldura da 121
└── portal/
    ├── views.py                          # _confirmar_por_email, comprovante (sem sessão; a tentativa), confirmar_de_novo
    ├── urls.py                           # portal:comprovante-confirmacao
    └── templates/portal/comprovante.html # o aviso da confirmação e "Inscrição enviada"

backend/tests/
├── integration/inscricoes/test_confirmacao_por_email.py   # o comando: uma vez, falha, contagem, trilha
├── integration/portal/test_confirmacao_de_inscricao.py     # a jornada pela tela e a nova tentativa (arquivo da 010, ampliado)
└── (ajustes) unit/test_apresentacao_dos_emails.py, integration/test_envios_em_duas_partes.py
```

**Structure Decision**: a orquestração mora em `inscricoes/application`, ao lado do remetente, porque é
regra da inscrição (uma confirmação por inscrição) e não do canal do portal. A view continua dona de
montar os dados a partir do que o comprovante mostra (`_dados_do_comprovante`), como já é.

## Complexity Tracking

Nenhuma violação a justificar.
