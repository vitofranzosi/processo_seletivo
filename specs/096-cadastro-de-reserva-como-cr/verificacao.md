# Verificação: Cadastro de reserva sem vaga imediata impresso como CR

**Feature**: [spec.md](spec.md) · **Tasks**: [tasks.md](tasks.md)

## Ponto de partida (T001, T002)

Em 21/10/2026, sobre `b0fc3b03` (a `main` em `717fc057` mais os artefatos da spec), contra
PostgreSQL com `DB_NAME=ps096` e 4 workers:

- `tests/unit/editais tests/unit/publicacoes tests/contract tests/integration/publicacoes
  tests/integration/portal`: **2896 passados**, nenhuma falha, em 78 s.

As premissas do `SC-901`, contadas nos snapshots:

| Snapshot | Perfis | Perfis `CR` |
|---|---|---|
| cenário A (`doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json`) | 4 | 0 |
| cenário B (`…/B-conteudo-publicado.json`) | 18 | 16 (TP-01 a TP-16, quadro todo em 0) |
| fixture de contrato (`backend/tests/contract/fixtures/snapshot_publicado.json`) | 1 (3 vagas, `LIMITED`) | 0 |

## Correção de desenho durante a implementação

A `D-007` dizia que a nota iria `junto`, para não começar a página seguinte sozinha. O `junto` prende
uma linha à **seguinte**, e o paginador recusa de propósito prender a última linha de um quadro
(`prender_a_ultima_linha`). A nota segue a tabela como a frase de reversão segue o quadro. A decisão,
o contrato, o plano e as tarefas foram corrigidos antes do código.

## A prévia passou a paginar diferente do publicado (D-012, 21/10)

Depois da US1, `tests/contract/test_documento_publicado.py` reprovou no `consolidado-B`: a prévia
tinha 15 páginas e o publicado 16. A seção 15, "Disposições finais", terminava a uma linha do pé da
página 15; a nota "CR: cadastro de reserva." empurrou o documento uma linha, e a seção e o fecho
deixaram de caber juntos. No publicado, o bloco da `069` (`com_o_fecho`) os levou à página 16; na
prévia, sem fecho, a seção ficou. O sumário dizia "15" num e "16" no outro.

O usuário escolheu, entre três opções, que a prévia reservasse o espaço efetivamente necessário para
o fecho, com escopo limitado à paginação do corpo normativo (D-012). Medição depois da correção, com
e sem a reserva:

| Composição do B | Autoridade | Sem reserva | Com reserva |
|---|---|---|---|
| plana | só o cargo | igual | igual |
| plana | nome, cargo e ato (a do A) | **diverge** | igual |
| plana | a do contrato | **diverge** | igual |
| por perguntas | as três | igual | igual |
| variante | as três | igual | igual |

O caso que diverge sem a reserva é o que `test_sem_a_reserva_o_cenario_b_volta_a_divergir` prende.
