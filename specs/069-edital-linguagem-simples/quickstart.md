# Quickstart — validar a 069

O roteiro de verificação: o que rodar, contra o quê e o que se espera. A forma do documento está em
[`contracts/documento.md`](contracts/documento.md), e as frases em [`contracts/redacao.md`](contracts/redacao.md).

## 0. Pré-requisitos

- PostgreSQL local, com `LC_ALL=en_US.UTF-8` exportado e o superusuário igual ao login da máquina.
- `cd backend && uv sync --extra dev`, uma vez na worktree, e `.env` com `DB_NAME=ps069`.
- **Bancos de validação novos, com dados fictícios:**
  - `ps_069_base`: migrado, serve de molde;
  - pelo `createdb -T`, os bancos de antes e depois de A e de B, um de Retificação de Edital antigo e um
    de acervo.

  Nenhum banco de desenvolvimento, de demonstração ou de produção.
- O subconjunto da Liberation Sans já gerado e versionado (R-007).

## 1. Suíte

```bash
cd backend && make lint check
```

```bash
cd backend && make DB_NAME=ps069 test-pg
```

Esperado: tudo passa, e os pulados são os onze deliberados do `AGENTS.md`. No diff de testes:

- a fixture de contrato regenerada, com o diff revisado;
- os bytes esperados da auditoria movidos para `specs/069-…/demonstracao/`;
- as fixtures novas do comprovante e da divulgação, **iguais** às de antes da mudança (SC-522).

## 2. Comprovante e divulgação não mudam

Antes de qualquer mudança no escritor, gravar os bytes de um comprovante e de um documento de divulgação
compostos pela `main`. Depois, compor os mesmos com esta branch e comparar com `cmp`. Esperado: iguais
(FR-1383, SC-522).

## 3. Cenários A, B e a variante, antes e depois

Os roteiros da auditoria (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`), pelo fluxo real
(`create_process_with_first_edital` → `replace_draft` → `submit_edital` → `homologate_edital` →
`publish_edital`):

- **Antes:** o código da `main`, nos bancos de antes.
- **Depois:** o desta branch, nos bancos de depois.

| O que medir | Critério |
|---|---|
| Fatos do documento de antes presentes no de depois (extração de texto) | 100% — SC-516 |
| Conferência por enunciado, refeita sobre o texto final (`demonstracao/equivalencia.md`) | nenhuma regra acrescentada, retirada ou mudada; frases novas listadas para aprovação — SC-517 |
| Termos internos da FR-1366 | zero — SC-518 |
| Sumário e marcadores contra as páginas | 100% — SC-520 |
| Defeitos de paginação (contrato, §7) | zero — SC-521 |
| B: nome comum por grupo e atributos iguais | uma vez — SC-524 |
| Mesmo snapshot composto duas vezes | `cmp` igual — SC-523 |

## 4. Três motores de renderização

Renderizar a mesma página — título de seção e parágrafo justificado — em CoreGraphics, poppler e PDFium:

```bash
uv run --no-project --with pyobjc-framework-Quartz python doc/auditoria-edital-pdf-2026-10-08/cenarios/qrender_all.py <pdf> <prefixo> 1.0
```

```bash
pdftoppm -r 72 -png <pdf> <prefixo>
```

```bash
uv run --no-project --with pypdfium2 --with pillow python -c "import pypdfium2 as p, sys; d=p.PdfDocument(sys.argv[1]); d[0].render(scale=1).to_pil().save(sys.argv[2])" <pdf> <png>
```

Esperado: títulos em negrito e as mesmas quebras nos três; nenhuma linha justificada além da margem —
SC-519. Gravar a comparação em `demonstracao/`.

## 5. Retificação de Edital publicado antes

1. No banco de Retificação, publicar o cenário A com o código da `main`.
2. Trocar para esta branch e retificar o prazo de inscrições.
3. Conferir o consolidado:
   - ordem, títulos, numeração e divisão das seções iguais às do original;
   - redação 2, fonte embutida, sumário e marcadores;
   - sem resumo nem reunião de seções;
   - a tela de Retificação mostra os números do PDF original (FR-1394, FR-1399).

## 6. Ato de ordenação já publicado

No mesmo banco, depois de publicar com a `main`, emitir um ato de ordenação com critério de desempate
por data. Trocar para esta branch e abrir a página do ato. Esperado:

- a frase do desempate é a da redação 1 ("menor valor declarado em Data de nascimento…") — FR-1397;
- um ato emitido sobre a versão do consolidado novo mostra a redação 2.

## 7. Acervo

Publicar com a `main`, trocar para esta branch e servir o documento. Esperado:

- os mesmos bytes (FR-1394);
- o download com nome `edital-«n»-«ano».pdf` (FR-1387).

## 8. Edital homologado antes da implantação

Homologar com a `main`, trocar para esta branch e publicar. Esperado: a recusa
`homologated_revision_changed`. O Edital volta à elaboração e é submetido e homologado de novo, já com a
redação nova (premissa da spec).

## 9. Aviso de remissão textual

Num rascunho do cenário A com "conforme o método publicado na seção Perfis de Vaga", abrir a Revisão.
Esperado: um aviso não impeditivo, com o trecho, a seção repartida e os destinos possíveis, e o texto
intocado (FR-1400).

## 10. Jornada pelo navegador — a demonstração do Princípio VI

Pelo painel do navegador, no runserver local da worktree com `INTERFACE_SELETOR_IDENTIDADE=true` e
`PORTAL_IDENTIDADE_DEMO=true`, num banco de validação novo. Cada passo é feito **pelo canal do ator**,
sem shell nem manipulação de banco. Os roteiros das seções anteriores medem; esta seção demonstra.

| Passo | Ator e canal | O que se confere | Evidência |
|---|---|---|---|
| 1 | Elaborador, assistente de composição | compor um Edital com o texto livre "conforme o método publicado na seção Perfis de Vaga" | captura da etapa Conteúdo com o título de grupo e a numeração apresentada |
| 2 | Elaborador, prévia | a prévia na apresentação por perguntas e na redação 2: resumo, sumário com páginas, fonte embutida | o PDF da prévia e uma captura |
| 3 | Elaborador, Revisão | o aviso de remissão textual, não impeditivo, com o trecho, "repartida" e os destinos possíveis; as frases da Revisão iguais às do documento | captura |
| 4 | Homologador e Publicador, interface | homologar e publicar (pessoas diferentes) | captura da publicação |
| 5 | Candidato, portal | baixar o Edital por "Ler o Edital completo (PDF)" e conferir o nome `edital-«n»-«ano».pdf`; abrir no leitor e conferir título, marcadores e links | captura e o arquivo baixado |
| 6 | Presidência, página do ato | abrir a página de um ato de ordenação já publicado com a redação 1, e a de um ato da redação 2. O ato de redação 1 é preparado **pela interface**, com o runserver rodando o código da `main` sobre o mesmo banco de validação, antes de trocar para esta branch | capturas das duas |

**Os dois servidores rodam um de cada vez, nunca juntos.** Cookie de `localhost` não é separado por
porta: com os dois no ar, o `sessionid` de um sobrescreve o do outro, e a sessão da gestão cai no meio do
percurso com um 302 para `/gestao/identificar`, que parece defeito e não é. A ordem é:

1. criar o banco de validação, migrado com o código da `main`;
2. subir o runserver da `main`, publicar um Edital e emitir por ele o ato de ordenação de redação 1, pela
   interface; **parar o servidor**;
3. migrar o mesmo banco com o código desta branch (a `publicacoes/0011`);
4. conferir com `lsof -nP -iTCP -sTCP:LISTEN` que nenhum outro runserver está em `localhost` — nem de
   outra worktree — e subir o desta branch;
5. fazer os passos 1 a 6.

Se for preciso manter os dois no ar, o segundo sobe com um módulo de settings no scratchpad que importa o
de desenvolvimento e define `SESSION_COOKIE_NAME` e `CSRF_COOKIE_NAME` próprios, passado por
`PYTHONPATH` e `DJANGO_SETTINGS_MODULE` na linha de comando. Nenhum dos dois caminhos edita o
`.claude/launch.json`, que é versionado.

Tudo em `specs/069-edital-linguagem-simples/demonstracao/jornada/`, com um `README.md` que diz o passo,
o ator, o canal e o que se viu. O `README.md` registra também a porta de cada servidor e a ordem em que
rodaram.
