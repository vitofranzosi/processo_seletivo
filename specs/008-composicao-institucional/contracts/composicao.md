# Contrato — Composição documental institucional

**Feature**: 008 — Composição Institucional do Edital | **Data**: 2026-08-30

Três contratos. **A** é o que entra no compositor e sob que regras. **B** é o que a página
materializa. **C** é o que esta feature promete **não** mudar — e é o mais importante dos três,
porque a `008` é uma feature de apresentação sobre mecanismos já consolidados.

---

## Contrato A — Entrada do compositor

### A.1 O que o compositor recebe

| Entrada | Origem | Presença | Papel |
|---|---|---|---|
| Conteúdo publicado | snapshot canônico v3 | sempre | **única** fonte do corpo normativo |
| Hash do conteúdo | `canonical_sha256` do snapshot | sempre no publicado | declaração de integridade |
| Modo | `PUBLISHED` ou `PREVIEW` | sempre | determina o que existe no documento |
| Contexto do ato — `AutoridadeSignataria` | `Publicacao.signatory_name` / `signatory_role`, via o `signatory` que o fluxo já resolveu | ver A.2 | fechamento do ato |

**O corpo normativo é função pura do conteúdo publicado.** Nenhuma consulta ao banco, nenhuma
leitura de relógio, nenhuma variável de ambiente e nenhum estado global participam da sua composição
(FR-034, SC-013). O contexto do ato é o **único** elemento externo, e materializa apenas o bloco de
autoridade.

### A.2 Regra de presença, por modo

| Modo | Hash | `AutoridadeSignataria` | Bloco de autoridade | Bloco de verificação | Marca de prévia |
|---|---|---|---|---|---|
| `PUBLISHED` | usado | **obrigatória** | presente | presente | ausente |
| `PREVIEW` | ignorado | **proibida** | ausente | ausente | presente |

**A regra é do compositor, não do chamador.** Compor em modo publicado sem `AutoridadeSignataria` é recusado;
oferecer `AutoridadeSignataria` em modo prévia é recusado. *Se a garantia dependesse de quem chama lembrar,
ela estaria com quem não a tem — e a consequência do esquecimento seria um ato administrativo
publicado sem quem o praticou.*

### A.3 Chamadores

| Chamador | Modo | `AutoridadeSignataria` | Observação |
|---|---|---|---|
| `publicacoes/application/publish_edital.py` | `PUBLISHED` | do `signatory` já resolvido | compõe **antes** de `Publicacao.objects.create` — por isso o contexto chega por parâmetro |
| `publicacoes/application/retificacoes.py` | `PUBLISHED` | idem, da Publicação da Retificação | documento consolidado usa a **mesma** composição (FR-043) |
| `interface/views.py` (prévia) | `PREVIEW` | nenhuma | não decorre de Publicação |
| `scripts/gerar_fixture_documento.py` | `PUBLISHED` | fixa e versionada | sem ela a fixture não gera (D-009) |

---

## Contrato B — O que a página materializa

### B.1 Ordem do documento

```text
FLUXO NORMATIVO — geometria idêntica nos dois modos (FR-042)
  cabeçalho institucional      órgão · instituição · unidade   (constantes)
  ato                          EDITAL Nº <número>/<ano>        (maior corpo da página)
  Processo e título            do snapshot
  1..N seções normativas numeradas                             na ordem do conteúdo publicado
  bloco de autoridade                                          (somente PUBLISHED)
  bloco de verificação                                         (somente PUBLISHED, discreto)

REGIÃO FIXA — fora do fluxo, em toda página, não participa da paginação
  marca de prévia              (texto somente em PREVIEW; região existe nos dois modos)
  rodapé                       identificação · SHA abreviado · Página N de M
```

*A marca de prévia está **fora** do fluxo por decisão D-011: dentro dele ela empurraria o conteúdo e
faria a prévia quebrar em lugares diferentes do publicado, que é o que FR-042 proíbe. Fora dele, a
igualdade das quebras é garantida por construção, e a marca passa a aparecer em todas as páginas.*

### B.2 Vocabulário visual

Fechado: **texto, fio e contorno**. Ficam fora ícone, sombra, cartão, gradiente, imagem, fundo e
paleta. O documento é preto sobre branco (FR-003, FR-008).

Níveis tipográficos, e apenas estes (FR-009): identificação institucional · título do ato · título
de seção · subseção/bloco · corpo · nota/metadado.

### B.3 Materialização por tipo de conteúdo

| Conteúdo | Forma | Requisito |
|---|---|---|
| Seção textual | parágrafos preservados, numerada | FR-010, invariante da `006.1` |
| Perfil de Vaga | bloco com moldura; identificação tabular; requisitos em lista; modalidades em tabela | FR-014 a FR-019 |
| Cronograma | tabela — ordem, evento, início, término | FR-023 a FR-026 |
| Etapa de Avaliação | subseção numerada com pares rótulo-valor alinhados | FR-013, FR-027 |
| Autoridade | nome e cargo, sem praça e sem data | FR-033, FR-036 |
| Verificação | após a autoridade, corpo de nota | FR-038 a FR-040 |

### B.4 Regras de quebra

| Regra | Requisito |
|---|---|
| Título — de seção, Perfil ou Etapa — nunca fecha página sem conteúdo abaixo | FR-022, FR-030 |
| Perfil que cabe inteiro na página seguinte não é partido | FR-020 |
| Perfil grande desce a cascata: sub-bloco → unidade interna → linha | FR-021 |
| Cabeçalho de tabela não se separa da primeira linha e se repete na continuação | FR-026 |
| As quebras do corpo normativo são idênticas entre prévia e publicado | FR-042 |

### B.5 Ausência

Nenhuma célula, rótulo ou linha é preenchida com informação inexistente (FR-019, FR-024). A ausência
é materializada como ausência, na forma que o documento já usa.

---

## Contrato C — O que **não** muda

*Este é o contrato que a feature promete e que os testes existentes guardam. Uma alteração aqui não
é evolução da `008`: é defeito.*

### C.1 Conteúdo e integridade

| Garantia | Verificada por |
|---|---|
| `SCHEMA_VERSION` permanece `3` | suíte canônica existente |
| Snapshot: mesmas chaves, mesma forma canônica, mesmo hash | suíte canônica existente |
| Representação decimal canônica intocada; formatação humana só no compositor | FR-001, `humano.py` |
| Gramática de endereçamento da Retificação intocada | suíte de `changes.py` |
| Declaração de integridade preserva o SHA-256 completo e a afirmação de derivação | FR-040 |
| Corpo normativo composto sem consulta ao banco | `test_o_snapshot_basta_para_compor_o_documento` |
| Mesma entrada produz os mesmos bytes | `test_the_same_snapshot_always_produces_the_same_bytes` |

### C.2 Documento e publicação

| Garantia | Verificada por |
|---|---|
| Documentos já publicados conservam bytes e `document_hash` | imutabilidade de `DocumentoPublicado`; nenhuma rematerialização é executada |
| Prévia não carrega nenhuma afirmação de integridade | `test_a_previa_nao_carrega_nenhuma_afirmacao_de_integridade` |
| Rodapé com identificação, SHA abreviado e `Página N de M` em toda página | invariante de não regressão |
| Nenhum identificador técnico no corpo normativo | `test_a_declaracao_de_integridade_identifica_sem_expor_uuid` |
| Acentuação do português preservada | `test_document_preserves_portuguese_accents` |

### C.3 Superfície externa

| Garantia | Situação |
|---|---|
| Endpoints administrativos e públicos | **inalterados** — mesmo caminho, mesmo método, mesmo tipo de conteúdo |
| Contrato HTTP do documento publicado | **inalterado** — o que muda é o interior do PDF |
| Migrations | **nenhuma** |
| Permissões e papéis | **inalterados** |
| Telas da interface administrativa | **inalteradas** — a prévia já chama este compositor |

*O documento publicado continua sendo `application/pdf` no mesmo endereço, com o mesmo cabeçalho de
resposta. Um consumidor da API não percebe a `008` de nenhuma outra forma que não abrindo o arquivo.*
