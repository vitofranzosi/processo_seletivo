# Implementation Plan: Conferência antes de convocar os titulares

**Branch**: `claude/140-conferencia-ao-convocar-d54ffb` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

## Summary

O POST do gesto dos titulares (`interface:convocar-titulares`) passa a ter duas etapas no mesmo
endereço. Sem `etapa=confirmar` e o resumo do texto, ele responde a página da conferência, renderizada
na própria resposta, sem gravar nada. Com eles, recompõe a conferência e só chama o comando de hoje
(`fluxo.convocar_titulares`) se o resumo conferir. As recusas que o comando faz pela leitura saem de
uma função só, chamada pelos dois.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**
**Testing**: pytest contra PostgreSQL (`make test-pg`), cliente de teste do Django
**Target Platform**: a gestão (`/gestao/`), sob a CSP da `091`/`092`
**Constraints**: sem script nem estilo no template; a prévia não grava nada (FR-4807)

## Constitution Check

- **Publicação e ato imutáveis**: o ato continua o da `050`; a conferência não o altera.
- **Nada é excluído**: nada é gravado nem apagado pela conferência.
- **Negar por padrão**: a conferência passa pela mesma porta (`_edital_para_classificar` com
  `somente_gestao`), e o comando confere a base de novo sob a trava.
- **Rastreabilidade**: cada FR, SC, UX e caso-limite tem linha em `rastreabilidade.md`.

## O desenho

### 1. Domínio — `convocacao/application/fluxo.py`

- `verificar_titulares(*, edital, perfil_id, marco_id, lista_id, alcance_confirmado, vencimento,
  evento_id, agora)` — a sequência de recusas de hoje, na mesma ordem: marco intermediário, prévia,
  impedimento, alcance (`_conferir`), nenhum titular, `resolver_vencimento`,
  `_recusar_vencimento_passado`. Devolve `(previa, instante, origem)` ou levanta `DomainError`.
  `convocar_titulares` passa a chamá-la dentro do `comando_de_comissao` (D-004).
- `conferencia_dos_titulares(...)` — a mesma verificação fora da trava, mais o Processo que não
  aceita mudança, e o conteúdo da conferência: pessoas, fundamento composto, mensagens (pela
  `comunicar.previa_das_mensagens`), prazo, quem fica de fora, rótulos do botão. Devolve
  `{"recusa": {...}}` quando a confirmação seria recusada.
- `gesto_ja_concluido(*, actor, chave)` — leitura do `IdempotencyRecord` da operação
  `convocacao:convocar_titulares` com `response_status` preenchido (D-005).

### 2. A mensagem — `convocacao/application/comunicar.py`

- `_renderizar(dados)` extraída de `enviar_mensagem_de_convocacao`: carrega o modelo, compõe o
  contexto e devolve assunto, corpo e HTML. O envio a usa; nada muda no que sai.
- `previa_das_mensagens(*, edital, versao, inscricoes, vencimento, agora)` — a variante de cada pessoa
  por `aplicabilidade` da versão vigente (o que `gravar_lista_da_chamada` gravaria) e pelo momento do
  Requerimento; o modelo inicial (titulares não têm chamada anterior); a unidade do Edital; o link
  como indicação. Agrupa pessoas com a mesma mensagem (D-003).

### 3. A tela — `interface/views.py` e templates

- `convocar_titulares_view` deixa de usar `conferencia_do_texto.exigir` e passa a:
  1. autorizar como hoje;
  2. se `etapa=confirmar` e a chave já foi concluída → comando (repetição);
  3. compor a conferência; recusa → página com a razão e a volta;
  4. sem `etapa=confirmar` ou com resumo diferente → página da conferência (com o aviso de texto
     mudado no segundo caso);
  5. resumo igual → comando, como hoje, e redirecionamento à tela.
- `interface/convocacao_conferir.html` (nova): as peças de `marco_conferir.html` —
  `consequencias irreversivel`, `ajuda`, `confirmar`, "Cancelar e voltar".
- Estilo: só classes já existentes na folha comum, mais uma regra para o texto da mensagem
  (`white-space: pre-line`) na folha da tela, pelo bloco `estilo_da_pagina`.
- `convocacao.html`: o botão "Conferir e convocar as N" e a ajuda corrigida (FR-4816).

### 4. Testes

- `tests/interface/test_conferencia_ao_convocar.py` (novo): prévia sem efeito (sem convocação, sem
  mensagem, sem trilha, sem chave reservada, sem sessão), confirmação, duplo POST, alcance mudado,
  texto mudado, recusas antes do botão, autorização, publicação, quem fica de fora, mensagem igual à
  enviada.
- `tests/interface/test_convocacao_em_fluxo.py` e `test_conferencia_do_texto.py`: o helper
  `postar_titulares` passa pela conferência; os casos da `125` sobre titulares passam a falar da
  conferência nova.

## Project Structure

```text
specs/140-conferencia-ao-convocar/
├── spec.md
├── plan.md
├── tasks.md
├── rastreabilidade.md
└── checklists/requirements.md

backend/processo_seletivo/
├── convocacao/application/fluxo.py        # verificar_titulares, conferencia_dos_titulares
├── convocacao/application/comunicar.py    # _renderizar, previa_das_mensagens
└── interface/
    ├── views.py                            # convocar_titulares_view
    ├── templates/interface/convocacao_conferir.html
    ├── templates/interface/convocacao.html
    └── static/interface/telas/convocacao_conferir.css
```

## Complexity Tracking

Nenhuma violação da Constituição a justificar.
