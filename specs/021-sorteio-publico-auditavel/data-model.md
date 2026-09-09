# Modelo de dados — 021 · Sorteio público auditável

Fase 1. Entidades novas em `processo_seletivo/sorteios/`, mais duas alterações em módulos
existentes. Toda entidade nova é **append-only**, na forma que `AtoDeOrdenacao` e `PosicaoNaOrdem`
já praticam: `save` recusa atualização, `delete` recusa exclusão, e a role de runtime não recebe
`UPDATE` nem `DELETE`.

## Decisão de plano — publicar é congelar

A spec fala em publicar e em congelar a relação. **São o mesmo ato, e o plano os funde num
instante só.** Uma relação publicada e ainda editável seria exatamente a janela que a feature existe
para fechar: universo conhecido, compromisso ausente. Não há estado "publicada, não congelada".

---

## Entidades novas

### `RelacaoDeHabilitados`

O universo comprometido de um recorte. Publicada, é imutável; corrigida, é sucedida.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | identidade estável, pública |
| `edital` | FK `Edital` PROTECT | |
| `perfil_id` | UUID | identidade **publicada**, não FK — a mesma razão de `AtoDeOrdenacao` |
| `lista_id` | UUID, nulo | identidade publicada da modalidade; `NULL` = ampla concorrência |
| `versao` | FK `VersaoConsolidada` PROTECT | a norma sob a qual a projeção foi feita |
| `criterio_de_projecao` | texto | a frase publicada de quem entrou e por quê (R-012) |
| `quantidade` | inteiro | redundância deliberada: o manifesto a publica, e ela é conferível |
| `resumo` | char(64) | `canonical_sha256` do conteúdo canônico da relação |
| `publicada_em` / `publicada_por` | datetime / char | |
| `relacao_anterior` | FK self, nula, PROTECT | sucessão |
| `motivo_da_sucessao` | texto | obrigatório quando há anterior |

**Constraints**

- `uq_relacao_sucessora_unica` em `relacao_anterior`, where not null. **Não há unicidade por
  recorte:** a relação pode ser sucedida quantas vezes o certame precisar, e é a cadeia de sucessão
  que diz qual é a vigente — a última sem sucessor.
- `ck_relacao_sucessao_com_motivo` — sucessora exige motivo.
- `ck_relacao_nao_vazia` — `quantidade >= 1` (FR-009).

**Conteúdo canônico da relação** (o que o `resumo` cobre):

```json
{
  "relationId": "<uuid>", "editalId": "<uuid>", "versionId": "<uuid>",
  "profileId": "<uuid>", "listId": "<uuid|null>",
  "criterion": "<texto publicado>",
  "participants": [{"publicNumber": 1, "registrationId": "<uuid>", "protocol": "INS-2026-XXXX"}]
}
```

### `ParticipanteHabilitado`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `relacao` | FK `RelacaoDeHabilitados` CASCADE | |
| `inscricao` | FK `Inscricao` PROTECT | a inscrição não desaparece sob a relação que a cita |
| `numero_publico` | inteiro ≥ 1 | atribuído na projeção, por protocolo crescente (R-011) |

**Constraints**: `uq_participante_por_relacao` em `(relacao, inscricao)`;
`uq_numero_por_relacao` em `(relacao, numero_publico)`.

### `MetodoDeSorteio`

O que o certame declara **antes** do congelamento, e que passa a ser conteúdo normativo (FR-013,
FR-014).

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `edital` | FK `Edital` PROTECT | |
| `perfil_id` / `lista_id` | UUID / UUID nulo | o recorte a que se aplica |
| `algoritmo` | char | `IFES-SORTEIO-SHA256-v1` |
| `fonte` | char | identidade da fonte pública externa |
| `referencia_da_ocorrencia` | char | a ocorrência que fixará a semente |
| `derivacao` | texto | como a ocorrência decorre da data programada |
| `normalizacao` | texto | como o material bruto vira semente |
| `regra_de_substituicao` | texto | hipóteses e a ocorrência que substitui, sem escolha humana |
| `declarado_em` / `declarado_por` | datetime / char | |
| `resumo` | char(64) | resumo canônico do método declarado |

Imutável desde a declaração. Trocar o método é declarar outro, e é ato da classe da Retificação —
**nunca** implantação de software.

### `OcorrenciaDaFonte`

O material observado. Não é o ato, e observar não decide nada.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `fonte` / `referencia` | char / char | |
| `material_bruto` | texto | como veio da fonte, sem interpretação |
| `semente_normalizada` | char | resultado da regra publicada |
| `observada_em` / `observada_por` | datetime / char | |
| `indisponivel` | booleano | registra a hipótese que aciona a substituição |
| `evidencia` | texto | o que se observou, quando `indisponivel` (FR-015, R-006) |

**Constraint**: `uq_ocorrencia_por_fonte` em `(fonte, referencia)` — observar duas vezes devolve a
mesma linha, e é o que torna a observação idempotente.

**Toda observação fica registrada, inclusive a que não virou sorteio.** É o controle que torna
visível o descarte de ocorrência (R-006).

### `Sorteio`

A proveniência do ato: o que amarra relação, método e ocorrência à ordem produzida.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | identidade pública, é o que a verificação endereça |
| `edital` | FK PROTECT | |
| `perfil_id` / `lista_id` | UUID / UUID nulo | recorte |
| `relacao` | FK `RelacaoDeHabilitados` PROTECT | |
| `metodo` | FK `MetodoDeSorteio` PROTECT | |
| `ocorrencia` | FK `OcorrenciaDaFonte` PROTECT | |
| `ato` | OneToOne `AtoDeOrdenacao` PROTECT | a ordem |
| `manifesto_hash` | char(64) | resumo do manifesto derivado (R-007) |
| `executado_em` / `executado_por` | datetime / char | |
| `sorteio_anterior` | FK self, nulo, PROTECT | anulação |
| `motivo_da_anulacao` | texto | obrigatório quando há anterior |

**Constraints**

- `uq_sorteio_raiz` em `(relacao, ocorrencia, metodo, perfil_id, lista_id)` where
  `sorteio_anterior IS NULL` — **a tupla inteira da D-009**;
- `uq_sorteio_sucessor_unico` em `sorteio_anterior` where not null;
- `ck_sorteio_sucessao_com_motivo`.

---

## Alterações em módulos existentes

### `classificacao.AtoDeOrdenacao`

| Alteração | Forma |
|---|---|
| `origem` | `char(20)`, choices `COMPUTADO` \| `SORTEIO`, **default `COMPUTADO`** |
| `lista_id` | `UUID`, nulo — identidade publicada da modalidade; `NULL` = ampla concorrência |

`origem` tem default e não é anulável, pela razão que `EtapaAvaliacao.forma` já registrou: `NULL` e
`"COMPUTADO"` descreveriam o mesmo ato com bytes diferentes, e todo ato existente **é** computado.

**A constraint vira duas parciais** (R-001):

```python
UniqueConstraint(fields=["edital", "perfil_id", "marco_id"],
                 condition=Q(ato_anterior__isnull=True, lista_id__isnull=True),
                 name="uq_ato_raiz_por_marco")
UniqueConstraint(fields=["edital", "perfil_id", "marco_id", "lista_id"],
                 condition=Q(ato_anterior__isnull=True, lista_id__isnull=False),
                 name="uq_ato_raiz_por_marco_e_lista")
```

A primeira mantém, **palavra por palavra**, a garantia de hoje para o ato sem lista.

### `editais.EventoCronograma`

| Alteração | Forma |
|---|---|
| `location` | `char(255)`, `blank=True`, `default=""` — onde o evento acontece (D-008) |

Sem default institucional, sem validação de URL, um campo só. A sugestão vive na tela.

### Conteúdo canônico — degrau 10

`schedule[].location` passa a existir. `SCHEMA_VERSION` 9 → 10, com degrau em
`publicacoes/domain/elevacao.py`: `DEGRAUS_DE_EVENTO = {10: {"location": ""}}`. A ausência significa
"não declarado", e isso é verdadeiro sobre todo Edital publicado antes do degrau.

`/schedule/id=…/location` é endereçável pela gramática que já existe — nada a acrescentar em
`colecoes.py` nem em `changes.py`.

---

## Transições

```text
RelacaoDeHabilitados     publicada ──(fato de origem sucedido)──▶ sucedida por relação nova
                         nunca editada, nunca excluída

OcorrenciaDaFonte        observada ──▶ consumida por um Sorteio
                                   └──▶ registrada e não consumida (fica visível)

Sorteio                  constituído ──(nulidade, com motivo)──▶ sucedido por sorteio novo
                         o anterior permanece íntegro e legível

AtoDeOrdenacao           inalterado: append-only, com sucessão por motivo
```

## Regras de validação, por requisito

| Regra | Onde vive | Requisito |
|---|---|---|
| relação é projeção, sem edição de linha | comando de publicação; nenhuma rota aceita participante | FR-002 |
| numeração por protocolo crescente, 1..N | domínio da projeção | FR-003, R-011 |
| relação vazia recusada | `ck_relacao_nao_vazia` + comando | FR-009 |
| relação imutável | append-only + trigger + privilégio de runtime | FR-007 |
| ocorrência posterior ao congelamento | comando de constituição | FR-016 |
| semente nunca digitada | não existe campo de entrada em rota alguma | FR-017 |
| relação alterada invalida a ocorrência | comando compara `relacao.resumo` | FR-020 |
| um ato raiz por tupla | `uq_sorteio_raiz` + `uq_ato_raiz_por_marco_e_lista` | FR-031 |
| concorrência produz um ato | idempotência por chave + transação | FR-032 |
| ordem cobre todos | comando compara `quantidade` com posições gravadas | FR-025 |
| anulação exige motivo | `ck_sorteio_sucessao_com_motivo` | FR-053 |
| manifesto sem dado pessoal indevido | serializador do manifesto, com teste | FR-044 |

## O que este modelo deliberadamente não tem

Vaga ocupada, suplência, remanejamento, lista de convocação e a interação entre listas do 57/28.
Nada aqui responde "quem entrou" — só "em que ordem ficaram" (FR-064).
