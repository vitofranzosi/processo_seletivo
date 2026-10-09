# Quickstart — validar a 068

Roteiro de verificação: o que rodar, contra o quê, e o que se espera. A forma do documento está no
[contrato](contracts/documento.md).

## 0. Pré-requisitos

- PostgreSQL local, `LC_ALL=en_US.UTF-8` exportado, superusuário = login da máquina.
- `cd backend && uv sync --extra dev` uma vez na worktree; `.env` com `DB_NAME=ps068`.
- **Bancos de validação novos, com dados fictícios**: `ps_068_base` (migrado, molde) e, por
  `createdb -T`, `ps_068_a_antes`, `ps_068_a_depois`, `ps_068_b_antes`, `ps_068_b_depois`,
  `ps_068_a_ret` (Retificação). Nenhum banco de desenvolvimento, de demonstração ou de produção.

## 1. Suíte

```bash
cd backend && make lint check
```

```bash
cd backend && make DB_NAME=ps068 test-pg
```

Esperado: tudo passa; os pulados são os onze deliberados do `AGENTS.md`. A fixture de contrato de um
Perfil não aparece no diff (FR-1356).

## 2. Cenários A e B pelo fluxo real, antes e depois

Os roteiros da auditoria (`doc/auditoria-edital-pdf-2026-10-08/cenarios/cenario_a.py` e
`cenario_b_corrigido.py`), copiados para o scratchpad com os caminhos trocados, pelos comandos de
aplicação reais (`create_process_with_first_edital` → `replace_draft` → `submit_edital` →
`homologate_edital` → `publish_edital`).

- **Antes:** o código da `main` `2b698592`, extraído por `git archive`, rodando de dentro da pasta
  extraída (imprimir `pdf.__file__` para provar qual código rodou), nos bancos `*_antes`.
- **Depois:** o código desta branch, nos bancos `*_depois`.

| Cenário | O que medir | Critério |
|---|---|---|
| A | páginas totais e da seção de Perfis | ≤ 7 e ≤ 3 (de 9 e 5) — SC-510 |
| B | páginas totais e da seção de Perfis | ≤ 18 e ≤ 12 (de 36 e 30) — SC-511 |
| A, B | uma ocorrência do texto dos marcos, da tabela de modalidades, de cada frase e das linhas do método | SC-512 |
| A, B | diff de texto (`pdftotext -layout`, rodapé de verificação neutralizado): toda frase normativa de antes existe depois, no Perfil, na subseção comum, na tabela ou na frase consolidada | SC-513 |
| A, B | branco no pé das páginas da seção de Perfis, antes e depois (soma, em pontos) | SC-514 |

## 3. Páginas

Por CoreGraphics — o poppler desta máquina desenha o Helvetica-Bold como Regular:

```bash
uv run --no-project --with pyobjc-framework-Quartz python doc/auditoria-edital-pdf-2026-10-08/cenarios/qrender_all.py <pdf-absoluto> <prefixo> 1.0
```

Olhar todas as páginas da seção de Perfis de A e de B, depois; e as de antes correspondentes. Conferir
que o espaço liberado não virou branco no pé das páginas. Gravar as escolhidas em `demonstracao/`.

## 4. Retificação

No banco `ps_068_a_ret`, publicar o cenário A com o código desta branch e retificar o prazo de recurso
do marco de um Perfil: o consolidado agrupa os três que continuam iguais, e o quarto imprime os
próprios marcos (US4).

## 5. Acervo

Num banco de validação, publicar com o código da `main`, trocar para o desta branch e conferir que o
documento servido tem os mesmos bytes (FR-1358).
