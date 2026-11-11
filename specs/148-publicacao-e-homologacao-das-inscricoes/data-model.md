# Data Model: Publicação e homologação das inscrições

Duas tabelas novas no app `divulgacao`, ambas append-only (ORM, gatilho e privilégio ausente).
Nenhuma coluna nova em tabela existente.

## `divulgacao_publicacaodasinscricoes`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `edital` | FK `processos.Edital`, PROTECT | |
| `natureza` | `RECEBIDAS` · `PRELIMINAR` · `HOMOLOGACAO` | ordem de sentido único |
| `etapa_id` | UUID, nulo | identidade publicada da Etapa decisória; obrigatória no `PRELIMINAR`, nula em `RECEBIDAS` |
| `versao` | FK `publicacoes.VersaoConsolidada`, PROTECT | a versão citada |
| `publicacao_anterior` | FK self, nulo, PROTECT | a cadeia |
| `motivo_da_sucessao` | texto | obrigatório quando a natureza repete a anterior (aplicação) |
| `admite_recurso` | booleano, nulo | só no `PRELIMINAR`: `True` com Evento, `False` quando não prevê |
| `recurso_evento_id` | UUID, nulo | o Evento escolhido |
| `recurso_ate` | instante, nulo | término do Evento, congelado |
| `conteudo_publico` | bytes | canônicos |
| `conteudo_publico_hash` | char(64) | SHA-256 |
| `documento` / `documento_hash` | bytes / char(64) | o PDF, gravado uma vez |
| `quantidade` | inteiro ≥ 1 | inscrições do universo |
| `publicado_por` / `publicado_em` | texto / instante | |
| `signatario_*`, `unidade_*` | colunas congeladas | as mesmas de `PublicacaoResultado` |

Constraints: uma raiz por Edital; no máximo um sucessor por publicação; `PRELIMINAR` ⇒ `etapa_id`;
`RECEBIDAS` ⇒ sem `etapa_id`; `recurso_ate` ⇒ `PRELIMINAR` e `admite_recurso`; `quantidade ≥ 1`.
Gatilho de coerência: o sucessor é do mesmo Edital.

## `divulgacao_inscricaonapublicacao`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `publicacao` | FK, PROTECT | |
| `inscricao` | FK `inscricoes.Inscricao`, PROTECT | |
| `situacao` | `RECEBIDA` · `DEFERIDA` · `INDEFERIDA` | publicada, nunca pública quando indeferida |
| `resultado` | FK `resultados.ResultadoEtapa`, nulo, PROTECT | a origem da situação |

Constraints: única por `(publicacao, inscricao)`; `RECEBIDA` ⇔ sem resultado é permitido; a
`DEFERIDA` da homologação sem análise não tem resultado.

## Leituras derivadas (nunca gravadas)

- **vigente da cadeia**: a publicação sem sucessora do Edital.
- **divergência**: itens do vigente × projeção de agora (inscrição nova, situação mudada,
  resultado sucedido).
- **situação do candidato**: a linha da inscrição no vigente, mais o `ResultadoEtapa` visível.
