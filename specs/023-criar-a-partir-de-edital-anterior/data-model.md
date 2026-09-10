# Modelo de dados — Criar Edital a partir de Edital anterior

**Nenhuma entidade nova, nenhum campo novo, nenhuma migration.** Este documento não descreve modelo:
descreve **o mapa da cópia** — o que é lido do conteúdo vigente da origem, o que é escrito no destino,
o que é reiniciado e o que não é copiado. É esse mapa que os testes prendem.

## O que a operação toca

```text
ORIGEM  (somente leitura)                    DESTINO  (escrita)
─────────────────────────                    ──────────────────
VersaoConsolidada.content   ──── elevar ───▶  payload
   da versão vigente                            │
                                                ├─▶ ArtefatoAnexo   (novo, congelado_em nulo)
ArtefatoAnexo (congelado)   ──── bytes ─────▶   ├─▶ AnexoEdital     (novo)
                                                │
                                                └─▶ replace_draft ─▶ PerfilVaga + aninhados
                                                                     Cronograma + Eventos
                                                                     EtapaAvaliacao
                                                                     DocumentoExigido
                                                                     SecaoEdital

                                                    RegistroAuditoria  (a VERSÃO de origem,
                                                                        o ator, o instante)
```

Nada mais é lido, e nada mais é escrito. Em particular: a origem não recebe escrita nenhuma — nem
`revision`, nem `last_edited_by`, nem versão nova.

## Coleção por coleção

| Coleção | Copiada? | O que muda no caminho |
|---|---|---|
| `profiles[]` | sim | identidade nova; `classificationInformation` e `callInformation` **não** vêm (`FR-008`) |
| `profiles[].competitionModalities[]` | sim | identidade nova |
| `…[].normativeRule` | sim | identidade nova; `effectiveFrom` convertido de texto para instante (`T-002`) |
| `profiles[].declaredFacts[]` | sim | identidade nova |
| `profiles[].classificationMilestones[]` | sim | identidade nova; `stages[]`, `tiebreakers[].parameters` e `drawMethod.qualifyingStageId` remapeados (`T-005`) |
| `…[].tiebreakers[]` | sim | identidade nova |
| `…[].appealWindow` | sim | sem alteração — é declaração normativa sem identidade |
| `schedule[]` | sim | identidade nova; `startAt`/`endAt` convertidos; **`status` volta a `PLANEJADO`** (`FR-008a`); `isRegistrationPeriod` preservado |
| `stages[]` | sim | identidade nova; `scheduleEventId` remapeado |
| `documentRequirements[]` | sim | identidade nova; `profileId`, `modalityId` e `attachmentId` remapeados |
| `sections[]` | só as textuais | **todas** as textuais, e não só as editadas: o conteúdo publicado traz o padrão do catálogo quando não há linha (`T-006`). Identidade **recalculada** pelo destino, não remapeada |
| `attachments[]` | sim | Anexo e Artefato novos; bytes copiados; `congelado_em` nulo (`T-003`) |
| `number`, `year`, `title`, `description` | **não** | identificação é entrada da criação (`FR-007`) |
| `maxInscricoesPorCandidato` | **não** | nenhuma etapa do assistente o desenha (`FR-008`) |
| `processoCode`, `processoTitle` | **não** | são do Processo de destino, que já existe |
| `schemaVersion` | **não** | do conteúdo publicado; o rascunho não o carrega |

## O que nunca é criado no destino

Consequência de a operação escrever **apenas** nas tabelas acima — e verificada por teste, porque
consequência não conferida é suposição:

```text
Inscricao · RascunhoInscricao · DocumentoDaInscricao · Pagamento
MembroComissao · AlocacaoEtapa · Distribuicao
Avaliacao · Parecer · ResultadoEtapa · Classificacao
Recurso · DecisaoDeRecurso
Sorteio · Semente · Divulgacao · Notificacao
```

`MembroComissao` merece a nota, porque é a que mais confunde: ela é do **Processo**, não do Edital.
A feature não clona Processo, então não há o que proibir — o Edital novo simplesmente nasce dentro do
Processo que quem elabora escolheu, com a comissão que aquele Processo já tiver.

## Estados

| Objeto | Na origem | No destino |
|---|---|---|
| `Edital.status` | `PUBLICADO` ou `ENCERRADO` | permanece `EM_ELABORACAO` (`FR-020`) |
| `Edital.revision` | inalterada | um salto, o de `replace_draft` |
| `EventoCronograma.status` | qualquer | sempre `PLANEJADO` (`FR-008a`) |
| `ArtefatoAnexo.congelado_em` | não nulo (publicado, imutável) | nulo (rascunho, substituível) |

## Identidade

Três regimes, e confundi-los é o defeito que `FR-009` e `FR-010` existem para impedir:

1. **Identidade nova, mapeada** — Perfil, modalidade, regra, fato, marco, critério, Evento, Etapa,
   Documento Exigido e Anexo: as dez posições de identidade do conteúdo canônico, no mapa de `T-005`.
   **O `ArtefatoAnexo` não está entre elas**: ele recebe identidade nova na cópia binária, fora do
   payload, e o conteúdo canônico o endereça por `artifactId` dentro do Anexo — quem entra no mapa é
   o Anexo.
2. **Identidade derivada** — Seção, `uuid5(edital.id, key)`. Não entra no mapa: o destino a
   recalcula, e por construção ela já é dele.
3. **Sem identidade** — `appealWindow`, `distribution`, `callRules` e demais objetos de declaração.
   Viajam como estão.
