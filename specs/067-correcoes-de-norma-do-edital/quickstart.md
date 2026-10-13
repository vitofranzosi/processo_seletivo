# Quickstart — validar a 067

Roteiro de verificação: o que rodar, contra o quê, e o que se espera. O detalhe das frases e das
regras está nos [contratos](contracts/).

## 0. Pré-requisitos

- PostgreSQL local, `LC_ALL=en_US.UTF-8` exportado, superusuário = login da máquina.
- `cd backend && uv sync --extra dev` uma vez na worktree.
- **Um banco por finalidade, todos novos e com dados fictícios**: `ps_067_base` (migrado, molde),
  `ps_067_a_antes`, `ps_067_a_depois`, `ps_067_b_antes`, `ps_067_b_depois` (cópias do molde com
  `createdb -T`). Nenhum banco de desenvolvimento, de demonstração ou de produção é tocado.
- Para a suíte, `DB_NAME=ps067` (o banco de teste será `test_ps067`).

## 1. Suíte

```bash
cd backend && make lint check
```

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER="$(whoami)" DB_RUNTIME_USER="$(whoami)" DB_NAME=ps067 uv run pytest -q
```

Esperado: tudo passa; os pulados são os onze deliberados do `AGENTS.md`. A fixture de contrato
(`tests/contract/fixtures/documento_publicado_v1.pdf`) **não** aparece no diff (`SC-505`).

## 2. Os cenários da auditoria, antes e depois, pelo fluxo real

Os roteiros são os da auditoria (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`), executados pelos
comandos de aplicação reais (`create_process_with_first_edital` → `replace_draft` → `submit_edital`
→ `homologate_edital` → `publish_edital`). Os caminhos absolutos do scratchpad dentro deles são
trocados por variáveis, sem mudar uma linha do conteúdo dos cenários.

- **Antes:** o código da `main` (`99d32e16`), extraído com `git archive` para uma pasta à parte,
  publicando nos bancos `*_antes`.
- **Depois:** o código desta branch, publicando nos bancos `*_depois`.

Esperado no **depois**:

| Cenário | O que conferir | Critério |
|---|---|---|
| A | submissão sem achado impeditivo; um aviso `appeal_schedule_review` | `SC-503`, `SC-504` |
| A | 4 frases "Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”…"; nenhuma linha "Arredondamento" nem "Empate no corte" | `SC-500` |
| B | um aviso `appeal_schedule_review` com 1 regra de marco e 4 Eventos de recurso | `SC-504` |
| B | 2 tabelas "Quadro de vagas" e 2 frases de reversão (TD-ADM, TD-INFO-EDU); 16 Perfis TP sem quadro e sem reversão, com a tabela de Modalidades | `SC-501` |
| A, B | `pdftotext -layout` do depois contra o PDF da auditoria: só as linhas pretendidas e as consequências na numeração das tabelas e na paginação | `SC-502` |

E um caso a mais, em banco próprio: o cenário A com o marco **sem** arredondamento (a recusa que a
auditoria registrou em §3.3) publica.

## 3. Páginas

Renderizar por CoreGraphics — o poppler desta máquina desenha o Helvetica-Bold como Regular:

```bash
uv run --no-project --with pyobjc-framework-Quartz python doc/auditoria-edital-pdf-2026-10-08/cenarios/qrender_all.py <pdf> <prefixo> 1.0
```

Olhar, antes e depois: A p. 3 (marco por sorteio) e B pp. 4, 7 e 8 (Perfil com vaga; primeiro Perfil
sem vaga). Gravar as escolhidas em `demonstracao/`.

## 4. Interface

Com o rascunho do cenário A num banco de validação e o runserver com
`INTERFACE_SELETOR_IDENTIDADE=true`:

- a Revisão mostra o aviso "Prazos de recurso a conferir", com link para a etapa Cronograma;
- a Revisão do marco por sorteio não lista "Arredondamento" nem "Empate no corte";
- a tela do marco por sorteio não mostra "Casas decimais" nem "Arredondamento"; ao trocar para
  ordem por pontuação, os dois voltam preenchidos com 2 e "Meio para cima";
- no rascunho do B, a Revisão do Perfil TP-01 diz que a reversão não sai no documento.

## 5. Acervo

Num banco de validação, publicar o cenário A com o código da `main`, trocar para o desta branch e
conferir que o documento servido tem os mesmos bytes; retificá-lo (a Retificação de
`cenario_a2.py`) e conferir que o consolidado sai pelas regras novas (`SC-506`, `FR-1326`).
