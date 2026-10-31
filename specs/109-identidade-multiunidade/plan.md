# Implementation Plan: Identidade institucional preparada para mais de uma unidade

**Branch**: `claude/109-identidade-multiunidade` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

## Summary

Um resolvedor só (`unidades/application/identificacao.py`, D-001) diz a identificação de uma
unidade, a da implantação e o canal de atendimento com recaída no global. As molduras da gestão, do
portal, do acesso e da 404, as frases "a quem pedir acesso" e as cinco mensagens ao candidato passam
a perguntá-lo, cada uma pelo contexto que a spec nomeia. O registro ganha um campo opcional, o canal
da unidade, pelo mesmo `unidades.json` e pelo mesmo comando. O PDF, o seletor de demonstração, os
papéis e as regras não mudam.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (o do repositório)
**Primary Dependencies**: nenhuma nova
**Storage**: PostgreSQL; uma coluna nova em `unidades_unidade` (`atendimento`, texto, padrão vazio)
**Testing**: pytest contra PostgreSQL (`make test-pg`), com o Cefor da fixture `autouse` e o
`campus-a` de `registrar_unidade`
**Target Platform**: o monólito de sempre
**Performance Goals**: no máximo uma leitura do registro por página que desenha moldura, pela chave
**Constraints**: CSP sem inline; nenhuma tabela append-only nova (o `M` do provisionamento fica 46);
o Cefor idêntico ao de antes
**Scale/Scope**: ~26 unidades possíveis; hoje uma

## Constitution Check

| Princípio | Como se cumpre |
|---|---|
| Publicação imutável | o PDF e o comprovante leem as colunas `unidade_*` do ato; o aviso confirmado guarda o texto (FR-3216) |
| Nada se exclui | a migration só acrescenta a coluna; o gatilho de exclusão da `060` continua |
| Negar por padrão | nenhuma permissão nova; a moldura da gestão lê o escopo do ator já autorizado; a 404 não diz a unidade do objeto (FR-3208) |
| Auditoria | o canal entra na trilha da sincronização, como os demais campos |
| Concorrência | a sincronização já grava sob `select_for_update` de todas as unidades, numa transação; a identificação só lê, e o aviso congela o texto na transação da confirmação — a mudança do registro no meio dela vale para o aviso seguinte, nunca pela metade |
| LGPD | nenhum dado pessoal novo (spec, §Proteção de dados) |
| Jornada demonstrável | o [quickstart](quickstart.md), pelo canal de cada ator |
| Governança do usuário | as sete perguntas ficam no `research.md` com a resposta provisória que preserva o Cefor |

Sem violação. Nada a justificar em complexidade.

## Project Structure

### Documentation (this feature)

```text
specs/109-identidade-multiunidade/
├── inventario.md   # os pontos fixos, classificados (item 1 e item 8 do pedido)
├── spec.md
├── research.md     # D-001 a D-008, as dependências do JSON, P-1 a P-6
├── plan.md
├── tasks.md
├── quickstart.md   # o cenário demonstrável
├── verificacao.md  # antes × depois, e o que cada execução cobriu
└── checklists/requirements.md
```

### Source Code

```text
backend/processo_seletivo/
├── unidades/
│   ├── application/identificacao.py   # novo: o resolvedor
│   ├── application/sincronizacao.py   # o canal opcional
│   ├── models.py                      # Unidade.atendimento
│   └── migrations/0003_atendimento.py
├── interface/
│   ├── identidade.py                  # contexto: identificação da gestão e pública; comentário do PAPEIS
│   ├── erros.py                       # a frase do limite de envio
│   ├── avisos.py                      # rodapé visível no editor
│   └── templates/interface/{base,base_de_acesso,lista,minhas_etapas,recusa}.html
├── portal/
│   ├── views.py                       # página da seleção, convocação, comprovante por e-mail
│   └── templates/portal/base.html
├── shared/templates/404.html
├── avisos/{domain/mensagem.py,application/previa.py}
├── convocacao/application/comunicar.py
├── inscricoes/application/mensagem.py
├── identidade/application/mensagem.py
└── duvidas/application/consultar.py
backend/tests/unidades/test_identificacao_multiunidade.py   # os oito cenários
doc/pendencias-da-auditoria-institucional-2026-10-30.md     # item 7 do pedido
```

## Fases

1. **Resolvedor e registro** — `identificacao.py`, a coluna, a sincronização. Testes de unidade do
   resolvedor e da sincronização.
2. **Molduras** — gestão, portal, acesso, 404, frases de acesso. A página pública da seleção com a
   unidade do ato.
3. **Mensagens e atendimento** — aviso, convocação, comprovante, código de acesso, credencial,
   dúvidas, tela da convocação.
4. **Os oito cenários** e a comparação com a `main` (SC-1031).
5. **Documentação** — comentário do `PAPEIS`, documento das pendências, README, verificação.

## Ordem de integração

A sessão da `108` mexe em `interface/templates/interface/base.html`. A mudança desta feature ali são
três trechos de texto; o conflito, se houver, é de linha e se resolve à mão. Confere-se a `main`
antes do PR.
