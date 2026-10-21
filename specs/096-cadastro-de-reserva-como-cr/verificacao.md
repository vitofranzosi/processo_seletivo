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

## O cenário B pelo fluxo real (T033, T034)

21/10/2026, banco novo `ps_096_b` (`createdb` e `migrate` com o superusuário, `sincronizar_unidades`),
pelo roteiro da `069` (`specs/069-…/demonstracao/cenarios/cenario_b_069.py`), que corrige a numeração
do B para o catálogo novo. O roteiro corrigido da auditoria (`cenario_b_corrigido.py`) é anterior ao
catálogo da `069`, e a submissão o recusa por cinco conflitos de numeração, como a `069` registrou.
Caminhos do scratchpad ajustados numa cópia; a `previa` do `comum.py` passou a chamar o compositor
como a tela chama desde a `096`, com as autoridades previstas.

| O que se mediu | Resultado |
|---|---|
| Submissão | publicada; 16 avisos "oferta só cadastro de reserva" e o aviso de prazos de recurso, nenhum impeditivo |
| Tabela 2 — Tutor presencial — Perfis TP-01 a TP-16 | **16** `CR`, **0** células `0`, a nota **uma** vez, logo abaixo |
| Resumo ("São 10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU.") | igual ao de antes |
| Prévia e publicado | **10** páginas cada; corpo normativo **igual** página a página; a prévia diz "Fecho do ato: local, data, autoridade e verificação, na publicação." |
| Contra `demonstracao/B-publicado-096.pdf` | 11 trechos diferentes, todos da numeração que o roteiro corrige e da data do ato |

Páginas por CoreGraphics (`qrender_all.py` com `uv run --no-project --with pyobjc-framework-Quartz`),
gravadas em `demonstracao/`: `B-fluxo-real-p04-tabela-do-grupo.png` (a tabela do grupo com `CR` e a
nota) e `B-fluxo-real-p10-previa-e-publicado.png` (a última página dos dois modos, lado a lado). Os PDFs
do fluxo real estão em `demonstracao/B-fluxo-real-096.pdf` e `B-fluxo-real-previa-096.pdf`.

## Portal e gestão pelo navegador (T035)

Pela entrada `cadastro-reserva-096` do `.claude/launch.json` (porta 8097, banco `ps_096_b`; a 8096 já
é da `interface-095`).

- **Portal, `/selecoes/<id>/`, a 1280 px:** 18 blocos de Perfil; **nenhum** com "0 vaga", **nenhum**
  `CR` na página; o tutor a distância com "4 vagas imediatas com cadastro reserva", o presencial com
  "Cadastro reserva — até 15 classificados, para convocação futura". Console sem erro.
  `demonstracao/portal-1280-tutor-presencial.jpg`.
- **Portal a 375 px:** sem estouro (`scrollWidth` 375 = `clientWidth` 375).
  `demonstracao/portal-375-tutor-presencial.jpg`.
- **Gestão, tela de Retificação do mesmo Edital:** os campos "Vagas imediatas" dos dezesseis tutores
  presenciais com `0`, e nenhum `CR` na página (`FR-2417`).
- **A prévia da gestão** é a do `comum.previa`, pelo mesmo caminho da tela; a ligação da tela com as
  autoridades vigentes está presa por `tests/unidades/test_previa_mede_o_fecho.py`.
