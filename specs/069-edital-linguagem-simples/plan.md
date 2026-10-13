# Implementation Plan: O Edital oficial em linguagem simples — redação, organização, tipografia e navegação (lote 1)

**Branch**: `claude/edital-linguagem-simples-79eec9` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/069-edital-linguagem-simples/spec.md`

## Summary

O documento do Edital passa a ser composto em duas **apresentações**, escolhidas pela assinatura do
catálogo que o snapshot guarda (R-001):

- **Por perguntas**, para os Editais novos: resumo, sumário, seções na ordem das perguntas do
  candidato, seções reunidas como subseções N.k e cada regra gerada na seção que trata dela.
- **Plana**, para os Editais publicados antes e os consolidados deles: a forma da `068`, com a
  numeração e as remissões intocadas.

As duas usam a **redação 2** das frases geradas ([contrato](contracts/redacao.md)), a fonte Liberation
Sans embutida e medida pelas próprias larguras, a hierarquia nova, as regras de paginação, os
marcadores, os links, o título e o idioma no arquivo.

Três coisas mantêm o corte:

- **As frases têm versão** (R-004). A `Publicacao` registra com qual o documento foi composto, e a
  página do ato de ordenação já publicado mostra a redação dele.
- **O escritor do Edital se separa** do comprovante e da divulgação (R-005), que ficam presos por
  fixtures de bytes antes da mudança.
- **A numeração é uma regra só**, consciente da apresentação, lida pelo documento e por todas as telas
  (R-003).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2.

**Primary Dependencies**: nenhuma nova no produto. O renderizador de PDF continua sendo o próprio
(`publicacoes/infrastructure/pdf.py`). A fonte é um arquivo versionado. O `fontTools` só aparece no
roteiro de desenvolvimento que gera o subconjunto, por `uv run --with fonttools`, e o guardião de
dependências (`tests/unit/test_leitura_do_documento_submetido.py`) não o proíbe.

**Storage**: uma coluna nova em `Publicacao` (`redacao_do_documento`, padrão 1) e o `AlterField` dos
rótulos de `callForm` (R-015). Documentos publicados não são regerados.

**Testing**: pytest contra PostgreSQL (`make DB_NAME=ps069 test-pg`). Os cenários da auditoria são
compostos a partir dos snapshots congelados (`tests/unit/publicacoes/cenarios_da_auditoria.py`) e pelo
fluxo real (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`), e conferidos em três motores de
renderização.

**Target Platform**: o monólito Django; o documento é lido em qualquer leitor de PDF.

**Project Type**: aplicação web (monólito).

**Performance Goals**: compor um Edital de 18 Perfis não fica perceptivelmente mais lento. O sumário
custa uma ou duas paginações a mais, sem consulta ao banco. A fonte embutida soma de 35 a 65 KB por
documento.

**Constraints**:

- bytes determinísticos, sem data e sem `/ID`;
- streams de página sem compactação (R-006);
- comprovante e divulgação byte a byte iguais (FR-1383);
- conteúdo já submetido com o mesmo hash (FR-1393);
- numeração e remissões dos Editais antigos intocadas (FR-1399).

**Scale/Scope**: Editais de até algumas dezenas de Perfis; o cenário B tem 18.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o atende | Resultado |
|---|---|---|
| **I. Linguagem ubíqua** | A redação 2 troca o vocabulário do sistema ("recorte", "marco", "Corte:", "valor declarado em") pelo do candidato, sem mudar os conceitos. "Perfil", "Cadastro de reserva", "Etapa" e "lista de concorrência" continuam os termos do domínio. Os rótulos de formulário da equipe ficam. | ✅ |
| **II. Integridade normativa e imutabilidade** | O documento continua derivado só do snapshot homologado. O conteúdo já submetido não muda, e documento publicado não se regenera. A redação histórica de ato publicado é preservada e identificável (FR-1397, R-004). A equivalência é provada por variante e por enunciado (FR-1361, FR-1396), e nenhuma regra é acrescentada, retirada ou corrigida (FR-1395). Os problemas herdados ficaram como achados. | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão, rota ou ator novo. A coluna da redação é auditável e imutável, como as da `060`. | ✅ |
| **IV. Regras explícitas** | A apresentação é escolhida por um registro explícito (R-001); o agrupamento é por identidade, com unidades declaradas (R-009); cada frase é função da regra declarada e da versão. A paginação tem parâmetros nomeados. | ✅ |
| **V. Rastreabilidade e simplicidade** | Um compositor com duas apresentações, e não dois compositores; uma numeração para todas as telas; o escritor do Edital separado do compartilhado só no que muda. Rastreabilidade FR/SC/caso-limite → teste em `rastreabilidade.md`. Emendas às specs alcançadas (`054`, `064`, `067`, `068`) anotadas junto dos requisitos. | ✅ |
| **VI. Jornada e valor demonstrável** | **A jornada pelo navegador, nos canais dos atores** ([quickstart §10](quickstart.md)): o Elaborador compõe e confere a prévia, vê o aviso de remissão na Revisão; o Edital é homologado e publicado pela interface; o candidato baixa pelo portal, conferindo o nome do arquivo; a página do ato de ordenação é aberta. Evidências em `demonstracao/jornada/`. Os roteiros de comandos (cenários A e B, três motores, Retificação de Edital antigo, acervo) **medem**, e não substituem a jornada. O teste com candidatos é validação do piloto. | ✅ |

**Reavaliação depois do desenho (Phase 1)**: sem violação. Duas mudanças persistentes, as duas
consequência direta da spec e do clarify:

- a coluna `redacao_do_documento` (FR-1397);
- os títulos e a ordem do catálogo, que já eram copiados para o snapshot desde a `054`.

A premissa da spec foi corrigida para dizer isso.

## Componentes afetados

| Componente | O que muda |
|---|---|
| `backend/processo_seletivo/editais/domain/secoes.py` | Ordem e títulos do *Catálogo apresentado*; `APRESENTACAO` (grupos, membros, lugares do gerado); assinatura e registro de apresentações (R-001, R-002); mapa congelado dos títulos anteriores para os destinos (R-013) |
| `backend/processo_seletivo/publicacoes/domain/vocabulario_da_regra.py` | Redação versionada (1 e 2) das frases do desempate e da convocação; funções com o parâmetro de redação (R-004) |
| `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` | As duas apresentações; resumo; sumário em duas passadas; frases na redação 2; partilha parcial com unidades; tabelas de Perfis por nome; métrica como parâmetro de `Composicao`; caixa de fundo; recuo pendente; regras de paginação; perfil de arquivo do Edital (fonte, `/Info`, `/Lang`, marcadores, links); `numeracao`, `numeracao_impressa`, `itens_do_documento` e `tabelas_do_documento` conscientes da apresentação |
| `backend/processo_seletivo/publicacoes/infrastructure/fonte.py` (novo) e o subconjunto versionado | Leitura do subconjunto e das larguras; objetos `/TrueType` |
| `backend/processo_seletivo/publicacoes/models.py` + `migrations/0011` | `Publicacao.redacao_do_documento` |
| `backend/processo_seletivo/publicacoes/application/publish_edital.py`, `retificacoes.py` | Gravam a redação na `Publicacao` |
| `backend/processo_seletivo/publicacoes/api/views.py` | `Content-Disposition` com o nome do arquivo (R-012) |
| `backend/processo_seletivo/classificacao/application/selectors.py` | `nomear_criterios` lê a redação da Publicação da versão do ato; a proposta usa a vigente (R-004) |
| `backend/processo_seletivo/interface/revisao.py`, `aplicacao.py`, `forms.py`, `retificacao.py`, `views.py` | Redação 2; numeração apresentada; o código novo do aviso de remissão em `CODIGOS_DO_TEXTO_DA_SECAO` e nas âncoras; rótulos de `callForm` |
| `backend/processo_seletivo/interface/static/interface/conteudo.js`, `templates/interface/compor_conteudo.html` | O número vem do servidor; o título de grupo aparece na etapa Conteúdo |
| `backend/processo_seletivo/editais/domain/validation.py`, `numeracao_digitada.py` | `_DESCRICAO_DO_ITEM` com a natureza nova; conflito pelo prefixo apresentado; `_remissao_a_secao_pelo_titulo` (R-013) |
| `backend/processo_seletivo/editais/models/perfis.py` + migration | Rótulos de `callForm` (`AlterField`) |
| `backend/processo_seletivo/portal/situacao.py`, `portal/views.py` | Redação 2 do canal de convocação e do teto (vigente) |
| Templates com cópia da frase (`compor_perfis.html`, `_perfil.html`, `convocacao.html`) | Rótulo de `callForm` da redação 2 |
| `doc/` ou `backend/scripts/` | O roteiro que gera o subconjunto da fonte, com o SHA-256 da origem |

**Preservados, e conferidos por teste**:

- `render_documento` e a métrica Helvetica do comprovante e da divulgação;
- o snapshot (salvo o título e a ordem dos Editais novos);
- `edital_snapshot`;
- a topologia da Retificação;
- `DocumentoPublicado`;
- os documentos publicados.

## Ordem de construção

A ordem dos lotes da implementação, cada um verde antes do seguinte:

1. **Guardas antes da mudança:**
   - fixtures de bytes do comprovante e da divulgação;
   - teste que falha se o extrator de texto devolver vazio;
   - testes da apresentação plana sobre os snapshots congelados.
2. **Redação versionada** (vocabulário e frases do compositor), com um teste por variante do contrato.
   Depois, a coluna na `Publicacao` e a página do ato de ordenação lendo a redação do ato.
3. **Fonte e métrica:** o subconjunto (com aprovação do download da origem), `fonte.py`, a métrica como
   parâmetro e o perfil de arquivo do Edital.
4. **Catálogo e apresentação:** títulos e ordem, `APRESENTACAO`, numeração apresentada e todas as telas
   lendo-a.
5. **Composição por perguntas:** resumo, sumário, vagas, seleção, recurso, convocação, matrícula, e a
   partilha parcial com unidades.
6. **Paginação**, com os parâmetros da R-011 calibrados em A, B e na variante.
7. **Navegação e arquivo:** marcadores, links e nome do download.
8. **Aviso de remissão textual** (FR-1400).
9. **Demonstração:** cenários pelo fluxo real, três motores e conferência por enunciado refeita.

## Testes existentes expostos à mudança

Pelo levantamento de 12/10 (R-014):

- **cerca de 120 a 160 asserções sobre frases** em 18 arquivos de PDF;
- **cerca de 20** na Revisão, no portal e na página do ato;
- **40 a 60 sobre títulos e numeração** (`test_secoes.py`, `test_catalogo_da_054.py`,
  `test_conflito_de_numeracao.py`, `test_remissoes.py`, `test_numeracao_na_publicacao.py` e outros);
- **as fixtures de bytes:** a de contrato e as dos cenários da auditoria.

**A regra para cada falha**:

- Se o teste afirma uma frase, ele passa a afirmar a frase da redação 2 **com a mesma força**, ou fixa
  a redação 1 quando prova a história.
- Se afirma uma forma, passa a afirmar a forma nova na apresentação por perguntas, e a antiga na plana.
- **Nunca** se afrouxa uma asserção, e cada caso fica em `verificacao.md`.

Os auxiliares que a forma nova quebra sem defeito de produto estão listados na R-014.

## Project Structure

### Documentation (this feature)

```text
specs/069-edital-linguagem-simples/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-016
├── data-model.md         # a coluna da redação, o catálogo, as estruturas transitórias
├── contracts/
│   ├── documento.md      # a forma do documento nas duas apresentações
│   └── redacao.md        # a redação 2, variante por variante
├── quickstart.md         # validação: suíte, cenários, motores, Retificação, ato, acervo
├── checklists/requirements.md
├── tasks.md              # /speckit-tasks
├── rastreabilidade.md    # na implementação
├── verificacao.md        # na implementação
└── demonstracao/         # PDFs, páginas e conferência por enunciado, antes e depois
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   ├── editais/domain/{secoes.py, validation.py, numeracao_digitada.py}
│   ├── editais/models/perfis.py (+ migration de AlterField)
│   ├── publicacoes/domain/vocabulario_da_regra.py
│   ├── publicacoes/infrastructure/{pdf.py, fonte.py (novo), fontes/ (subconjunto + OFL)}
│   ├── publicacoes/{models.py, migrations/0011_*, application/*, api/views.py}
│   ├── classificacao/application/selectors.py
│   ├── interface/{revisao.py, aplicacao.py, forms.py, retificacao.py, views.py, static/…/conteudo.js, templates/…}
│   └── portal/{situacao.py, views.py}
└── tests/
    ├── contract/ (fixture regenerada; fixtures novas do comprovante e da divulgação)
    ├── unit/publicacoes/ (redação por variante; apresentação; paginação; arquivo; depois_da_069)
    ├── unit/editais/ (catálogo; numeração apresentada; aviso de remissão)
    ├── integration/publicacoes/ (Retificação de Edital antigo; acervo; ato de ordenação)
    └── interface/, portal/ (telas com a redação e a numeração)
```

**Structure Decision**: o monólito existente. O único módulo novo é `fonte.py`, com a pasta do
subconjunto.

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples rejeitada porque |
|---|---|---|
| Duas apresentações no compositor | O clarify exige que os Editais antigos mantenham estrutura, numeração e remissões (apresentação plana), e que os novos tenham a apresentação por perguntas | Uma só apresentação quebraria remissões do acervo (opção C do clarify) ou negaria a apresentação por perguntas aos Editais novos |
| Redação versionada e a coluna na `Publicacao` | O FR-1397: a página do ato de ordenação reconstrói a frase na exibição, e o ato publicado tem de mostrar a sua redação | Data de corte (frágil) ou não versionar (contrariaria o clarify) |
| Escritor do Edital separado do compartilhado | O comprovante se regenera a cada download e promete o SHA-256 do arquivo | Mudar a fonte de todos mudaria o SHA-256 de todo comprovante já emitido |
