# Data Model: Cadastro de reserva sem vaga imediata impresso como CR

**Feature**: [spec.md](spec.md) · **Research**: [research.md](research.md)

**Nada muda no modelo.** Nenhum modelo, campo, migration, versão de esquema ou chave do conteúdo
canônico. O Perfil de Vaga e o snapshot publicado continuam como estão (`FR-2400`).

## O que se lê

Do Perfil no conteúdo canônico, três chaves que já existem:

| Chave | Tipo | Uso aqui |
|---|---|---|
| `immediateVacancies` | inteiro ≥ 0 | `0` é condição para `CR` |
| `vacancyTable[].immediateVacancies` | inteiro ≥ 0, por lista | nenhuma linha positiva é condição para `CR` |
| `reserveType` | `NONE` · `LIMITED` · `UNLIMITED` | `LIMITED` ou `UNLIMITED` é condição para `CR` |

`reserveLimit` não entra na decisão: ele vai para a coluna do cadastro, como hoje.

## O predicado (D-005)

`cadastro_sem_vaga_imediata(perfil)`, em `editais/domain/quadro.py`:

| `immediateVacancies` | linhas do quadro | `reserveType` | Resultado | Célula |
|---|---|---|---|---|
| `0` | nenhuma declarada | `LIMITED` / `UNLIMITED` | verdadeiro | `CR` |
| `0` | todas em `0` | `LIMITED` / `UNLIMITED` | verdadeiro | `CR` |
| `0` | alguma positiva | qualquer | falso (incoerente) | `0` |
| `0` | qualquer | `NONE`, ausente ou desconhecido | falso | `0` |
| `> 0` | qualquer | qualquer | falso | o número |
| `False`, `True`, texto, ausente | qualquer | qualquer | falso | como hoje |

O último caso existe porque o snapshot é JSON e `bool` é `int` em Python. `sem_vaga_imediata`, da
`067`, já recusa `bool` pelo mesmo motivo.

## Os textos (D-006, D-007)

| Constante | Valor | Onde mora |
|---|---|---|
| `SIGLA_DO_CADASTRO` | `CR` | `publicacoes/infrastructure/pdf.py` |
| `NOTA_DO_CADASTRO` | `CR: cadastro de reserva.` | `publicacoes/infrastructure/pdf.py` |

Os dois valores são iguais nas duas redações. A coluna da redação 1 diz "Cadastro reserva", e a nota
diz "cadastro de reserva", com a preposição: é a grafia do domínio, e a nota é frase nova, sem texto
publicado de antes a preservar.
