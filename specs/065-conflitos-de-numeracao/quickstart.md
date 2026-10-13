# Quickstart — validar a 065

Roteiro para provar a feature de ponta a ponta. Os artefatos de partida estão em
`doc/auditoria-edital-pdf-2026-10-08/`: `cenarios/` (roteiros que publicam pelo fluxo real),
`snapshots/` (conteúdo publicado congelado de A e de B) e `pdf/` (os documentos da auditoria). O plano
de validação completo, com o porquê de cada passo, está em
[insumos-para-o-plano.md](insumos-para-o-plano.md) §3.

## Pré-requisitos

```bash
cd backend && uv sync --extra dev
```

```bash
LC_ALL=C /opt/homebrew/opt/postgresql@16/bin/pg_isready -h localhost
```

Um banco migrado de base, só para a validação (nunca o de desenvolvimento):

```bash
LC_ALL=C createdb -h localhost ps_065_base && DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_065_base DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate -v0
```

Os roteiros de `cenarios/` gravam a saída num caminho de scratchpad absoluto: ajuste `SAIDA` em
`comum.py` e o `sys.path.insert` dos cenários antes de rodar. Cada cenário roda num banco novo,
copiado da base.

## 1. Cenário B sem correção — a submissão é recusada

Rodar `cenario_b.py` num banco copiado de `ps_065_base`. **Esperado:** a submissão levanta
`blocking_findings` com os 5 conflitos (Da Inscrição, Da Verificação da Autodeclaração, Dos Recursos,
Da Convocação, Disposições Finais), cada um com os parágrafos, os números e os trechos; e o aviso da
remissão ambígua "item 8.1" (`SC-462`, `SC-463`, `SC-469`).

## 2. Cenário B corrigido — publica, e o documento fecha

Copiar `cenario_b.py` e reescrever as seções só pelo que as mensagens dizem: 3.x→4.x, 4.x→6.x,
8.x→11.x, "item 8.1"→"item 11.1", 11.x→12.x, 14.x→15.x. Publicar. **Esperado:**

- nenhum achado desta feature na submissão;
- `pdftotext -layout` do documento: todo parágrafo numerado começa pelo número da sua seção, e "11.1"
  aparece uma vez como subitem (`SC-465`);
- 44 páginas;
- diferença de texto contra `pdf/B-publicado.pdf` só nos números corrigidos;
- páginas 39 a 44 conferidas visualmente (`qrender_all.py`, CoreGraphics; e `pdftoppm`).

## 3. Cenário A — nada a acusar

Rodar `cenario_a.py` e `cenario_a2.py`. **Esperado:** nenhum achado desta feature, publicação e
Retificação concluídas (`SC-464`).

## 4. Os bytes não mudam

```bash
uv run python ../doc/auditoria-edital-pdf-2026-10-08/cenarios/render_old.py "$PWD" ../doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json /tmp/A-novo.pdf
```

**Esperado:** `cmp /tmp/A-novo.pdf ../doc/auditoria-edital-pdf-2026-10-08/pdf/A-publicado.pdf` sem
diferença; o mesmo para B (`SC-466`, `FR-1219`). E a fixture de bytes do contrato do documento
publicado passa sem ser refeita.

## 5. Retificação que desloca a numeração — publica, com aviso

Sobre o B corrigido e publicado, uma Retificação que esvazia "Do Atendimento à Pessoa com
Deficiência". **Esperado:** a confirmação da Retificação mostra os conflitos que ela cria como avisos
(`typed_numbering_conflict_in_retification`), e a Retificação é publicada (`SC-470`, `D-002`).

## 6. Pelo canal de quem elabora (Princípio VI)

Num Edital em elaboração, aberto no navegador (`/gestao/`, com `INTERFACE_SELETOR_IDENTIDADE=true`):

1. na etapa Conteúdo, escrever em "Da Inscrição" um parágrafo que comece por "3.1" e salvar;
2. ver o achado no topo da etapa e na Revisão, com a seção, o número impresso, o parágrafo e o
   trecho;
3. seguir o link e chegar à legenda da seção, que mostra o mesmo número (`UX-160`);
4. tentar submeter e ver a recusa com a mesma mensagem;
5. corrigir para "4.1", salvar, e ver o achado sumir.

## 7. Suíte

```bash
cd backend && make lint check test-pg DB_NAME=test_ps_065
```
