# Encaminhamento — a passagem da vaga entre cotas antes da ampla

**Registrado em**: 11/11/2026, pela spec
[`155`](../specs/155-destinacao-da-vaga-sem-concorrente/spec.md) (decisão D-008), contra a `main` em
`d1ec1e0a`.

**Estado**: **encaminhado, sem spec.** O usuário decidiu que a passagem entre cotas tem spec própria e
pediu que o trabalho ficasse encaminhado. A `155` só declara que ela existe e recusa a destinação
direta à ampla onde o Edital a exige.

> **Não vira escopo por estar escrito aqui.** O número da spec, a faixa de identificadores e o momento
> são do usuário.

---

## O que os Editais declaram

| Edital | Cláusula | Ordem |
|---|---|---|
| 173/2025 (cadastro de reserva, Cefor) | 9.5.1 e 9.5.6 | subgrupos de PPIQ entre si (pretos e pardos, indígenas, quilombolas), depois ampla — Decreto nº 12.536/2025 |
| 140/2025 (tutoria, Cefor) | 10.5.1 | a mesma |
| 90/2026 (tutoria, Cefor) | 11.3 | a mesma |
| 33/2026 (IFFluminense) | Anexo 7, "Redirecionamento das vagas entre cotas" | oito cotas da Lei nº 12.711/2012, cada uma com a sua sequência de sete destinos |

Os três do Cefor são seleção de pessoal; o do IFFluminense, curso. Os PDFs estão em `~/Downloads`, com
os nomes de origem.

## O que existe no GPS

- A reversão tem um destino só: a linha geral do mesmo Perfil (FR-246 da `016`).
- Desde a `155`, o Perfil pode declarar *"Passa antes por outras cotas, na ordem do Edital"*. Com essa
  resposta, nenhum ato move a vaga, e a tela diz que o GPS ainda não aplica a ordem.
- O movimento de vaga tem origem, destino e quantidade; o destino pode ser uma lista (`destino_lista_id`),
  embora a reversão sempre grave a linha geral. A tabela já admitiria um destino reservado.

## O que a spec própria precisa decidir

1. **Como o Perfil declara a ordem.** Por Modalidade de origem, a sequência de Modalidades de destino
   — como o Anexo 7 do 33/2026 —, ou uma ordem única para o Perfil, como o Decreto nº 12.536/2025
   escreve. A primeira cobre a segunda; o custo é o passo Perfis.
2. **O gatilho em cada degrau.** O 173/2025 fala em *"inexistência de candidatos habilitados"* no
   subgrupo, que é esgotamento; nada no corpus declara saldo entre cotas. A condição de cada degrau é a
   da `155` (FR-6304 e FR-6305) ou uma terceira.
3. **Destino intermediário que também não tem quem ocupar.** A vaga passa adiante no mesmo ato, ou
   cada degrau é um ato.
4. **A concomitância no destino.** Quem já ocupa pela ampla e é autodeclarado do subgrupo de destino.
5. **A prévia** (`095`, `098`): mostrar os degraus, e a equivalência com o caminho oficial.
6. **O documento do Edital**: a frase de cada ordem, e a entrada no catálogo de Retificação.

## Por onde começar

Ler a `155` inteira, a `016` (FR-245 a FR-253) e este arquivo; extrair o 9.5 do 173/2025 e o Anexo 7
do 33/2026 com `pdftotext -layout`. O cenário de teste mínimo é um Perfil com três subgrupos de PPIQ e
a ampla, uma vaga em cada, e um único habilitado no segundo subgrupo.
