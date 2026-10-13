# Data model — 070, a fonte de consulta do Edital vigente

**Nenhuma tabela nova, nenhuma coluna nova, nenhuma migration** (`FR-1449`, `D-006`). Este documento
descreve:

- o que a feature **lê** e de onde;
- as estruturas que ela monta **em memória** para cada consulta;
- as regras que as ligam.

Os caminhos são relativos a `backend/processo_seletivo/`.

---

## 1. O que é lido

| Fonte | Modelo e campos | Para quê | Nunca |
|---|---|---|---|
| Edital | `processos.Edital`: `id`, `number`, `year`, `institution_scope`, `status`, `processo` | Alcance (`obter_edital`), identificação, desfecho | — |
| Versão vigente | `publicacoes.VersaoConsolidada`: `id`, `valid_from`, `materialized_at`, `content`, `content_hash`, `applied_publications`, `source_publication`, e `proveniencias` (`ProvenienciaConteudo`: `target_path`, `publicacao`) | Todo o conteúdo da resposta | `canonical_content` (bytes) |
| Versões futuras | As mesmas, com `valid_from > instante` | O aviso da `FR-1414` | — |
| Publicações aplicadas | `publicacoes.Publicacao`: `id`, `publication_order`, `published_at`, `effective_at`, e `retificacao` (`Retificacao`: `effective_at`, e `base_snapshot.applied_publications`, só para a publicação de origem da versão) | Origem, links, documento de origem incompleto (`R-005`) | `canonical_content`, colunas do signatário; o `content` da versão-base |
| Documentos | `publicacoes.DocumentoPublicado`: `id`, `publicacao_id` | O link `public-document` | `bytes` |
| Anexos | `content.attachments[]` da versão vigente | Rótulo e link `public-anexo` | os bytes de `ArtefatoAnexo` |
| Desfecho | `processos.application.selectors.desfechos([edital])` → `Desfecho(alcance, operacao, em)` | Situação de calendário (`R-006`) | motivo e autor do ato |
| Canal institucional | `settings.PORTAL_ATENDIMENTO` | Alternativa da `FR-1441` | — |

**Explicitamente fora** (`FR-1412`):

- as tabelas de elaboração do Edital (`editais.models.*`, `SecaoEdital`);
- `Retificacao` e `AlteracaoNormativa` que não estejam publicadas;
- `RevisaoEdital` e `Homologacao`;
- qualquer tabela de `inscricoes`, `divulgacao`, `resultados`, `classificacao`, `sorteios`,
  `convocacao`, `recursos`, `requerimentos` e `identidade`.

Um teste de fronteira, no padrão de `backend/tests/portal/test_fronteira_publica.py`, reprova
consulta a essas tabelas durante uma resposta.

---

## 2. Estruturas em memória

Todas são dataclasses congeladas de `duvidas/domain/` (`R-001`). A forma serializada está em
[contracts/resposta.md](contracts/resposta.md).

### 2.1 `Consulta` — a entrada

| Campo | Tipo | Regra |
|---|---|---|
| `edital_id` | UUID | — |
| `instante` | datetime com fuso | Padrão: o presente (`R-020`) |
| `pergunta` | código do catálogo, `P-01` a `P-12` | Fora do catálogo: recusa (`FR-1417`, `FR-1419`) |
| `parametros` | `perfil_id`, `modalidade_id` (ou "sem modalidade") | Só os da versão vigente. Valor que não existe nela: a pergunta é reapresentada sem resposta, com o motivo (`FR-1418`) |
| `versao_anterior` | UUID de `VersaoConsolidada`, opcional | Só do mesmo Edital; de outro, é ignorado |

### 2.2 `VersaoConsultada`

| Campo | Origem |
|---|---|
| `id` | `VersaoConsolidada.id` |
| `identificador_curto` | os 12 primeiros caracteres de `content_hash` |
| `vigente_desde` | `valid_from` |
| `publicada_em` | `published_at` da publicação original (a primeira de `applied_publications`) |
| `retificacoes` | `(publicada_em, vigente_desde)` de cada Retificação aplicada, na ordem `(effective_at, publication_order)` |

### 2.3 `Resposta`

| Campo | Regra |
|---|---|
| `consulta` | a entrada, normalizada |
| `versao` | `VersaoConsultada` — **uma só por resposta** (`FR-1411`) |
| `mudanca` | `None` ou `MudancaDeVersao(anterior, atos, sem_efeito)` (`FR-1415`): os atos aplicados agora e não antes, e os aplicados antes e não agora — a consulta a um instante anterior ao da resposta anterior |
| `tipo` | `RESPONDIDA`, `NAO_INFORMA`, `DEPENDE_DA_LEITURA`, `FONTES_DIVERGENTES` ou `DETALHE_EM_ANEXO` (`FR-1421`) |
| `avisos` | tupla de `Aviso`: `RETIFICACAO_FUTURA`, `DESFECHO`, `DETALHE_EM_ANEXO`, `REDACAO_ALCANCA_MAIS` (`R-008`) |
| `explicacao` | `Referencia` de natureza `EXPLICACAO` |
| `referencias` | tupla de `Referencia` de natureza `TEXTO` ou `DADO`, na ordem da tabela da pergunta |
| `situacao` | `None` ou `SituacaoDeCalendario` (só `P-01` e `P-02`) |

**Invariante.** Todo valor citado na `explicacao` está em alguma `referencia` da mesma resposta.
Conferido por teste em toda a varredura do `SC-531`.

### 2.4 `Referencia` — o cartão

| Campo | Regra |
|---|---|
| `natureza` | `TEXTO`, `DADO` ou `EXPLICACAO` — exatamente uma (`FR-1432`) |
| `localizacao` | para o leitor: `Seção "Dos Recursos"`, `Perfil INF-BJN — Especialização…`, `Evento "Inscrições"`, `Documento "Laudo médico"`, `Modalidade PcD`. **Nunca** número impresso (`FR-1431`) |
| `caminho` | o caminho da `004` no conteúdo, para rastreio. Não aparece ao leitor |
| `rotulo` | o nome do campo na linguagem do domínio (só em `DADO`) |
| `conteudo` | `TEXTO`: a cadeia literal, sem tratamento (`R-010`). `DADO`: o valor publicado e a forma legível. `EXPLICACAO`: o texto deste pacote |
| `origens` | tupla de `Origem`; vazia só em `EXPLICACAO` |
| `futuro` | tupla de `ValorFuturo(valor, vigente_desde, origem)` (`FR-1414`) |
| `links` | o trecho da página pública, quando existe (`FR-1438`) |

### 2.5 `Origem`

| Campo | Regra |
|---|---|
| `publicacao_id` | o ato que fixou o valor (`R-004`) |
| `ato` | `ORIGINAL` ou `RETIFICACAO` |
| `publicado_em`, `vigente_desde` | datas do ato |
| `documento` | o caminho `public-document` do ato. **Nunca** a publicação de origem da versão, salvo quando ela é a origem do valor (`D-004`) |

### 2.6 `SituacaoDeCalendario`

| Campo | Regra |
|---|---|
| `instante` | o instante consultado, exibido sempre (`FR-1429`) |
| `periodo` | `Periodo` de `inscricoes.domain.periodo` (`R-007`) |
| `eventos` | `(evento, fase)` por `fase_publica_do_evento` |
| `desfecho` | `Desfecho` com `em <= instante`, ou `None` (`R-006`) |

### 2.7 `Canal`

| Campo | Regra |
|---|---|
| `origem` | `EDITAL` ou `INSTITUCIONAL` (`FR-1439`, `FR-1441`) |
| `contatos` | os canais distintos, normalizados (`R-011`) |
| `paragrafos` | `Referencia` de natureza `TEXTO` (só quando a origem é `EDITAL`) |
| `exclusividade` | verdadeiro quando algum parágrafo tem termo de exclusividade (`FR-1442`) |

### 2.8 `PontoParaRevisao`

| Campo | Regra |
|---|---|
| `tipo` | `CANAIS_DIVERGENTES`, `EXCLUSIVIDADE_DO_CANAL`, `ANEXO_CITADO_INEXISTENTE`, `RETIFICACAO_FUTURA` ou `DOCUMENTO_DE_ORIGEM_INCOMPLETO` (`FR-1443`) |
| `descricao` | o que o setor precisa revisar, em palavras |
| `fontes` | as `Referencia` que mostram a condição |
| `atos_faltantes` | só em `DOCUMENTO_DE_ORIGEM_INCOMPLETO` (`R-005`) |

Derivados na leitura; nunca gravados nem marcados como resolvidos (`FR-1444`).

---

## 3. Regras que ligam as estruturas

1. **Uma versão por resposta.** A aplicação lê a versão uma vez e passa o conteúdo ao domínio. O
   domínio não tem acesso a outra versão, exceto as futuras, que entram só como `ValorFuturo`.
2. **Uma origem por valor.** A regra é a do `R-004`. Um valor composto alterado por atos diferentes
   carrega várias.
3. **Literal é literal.** A `Referencia` de natureza `TEXTO` nunca é produzida por formatação ou por
   frase do pacote. O teste do `SC-534` compara cada uma com o conteúdo.
4. **A explicação só usa o que está nos cartões.** Valor que não está numa referência da mesma
   resposta não entra no texto.
5. **Determinismo.** A mesma `Consulta` sobre o mesmo banco produz a mesma `Resposta`. A ordem segue
   a do conteúdo publicado e da tabela da pergunta, nunca a do banco (`FR-1446`).
