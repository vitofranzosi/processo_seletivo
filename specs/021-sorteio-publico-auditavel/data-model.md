# Modelo de dados — 021 · Sorteio público auditável

Fase 1. Quatro entidades novas em `processo_seletivo/sorteios/`, mais quatro módulos existentes
alterados — `classificacao`, `divulgacao`, `editais` e `publicacoes` —, e um método que não é
entidade nenhuma: é conteúdo versionado do Edital. Toda entidade nova é **append-only**, na forma
que `AtoDeOrdenacao` e `PosicaoNaOrdem` já praticam: `save` recusa atualização, `delete` recusa exclusão, e a role de runtime não recebe
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
| `marco_id` | UUID | o marco de classificação; é ele que declara o método (D-013) |
| `lista_id` | UUID, nulo | identidade publicada da modalidade; `NULL` = ampla concorrência |
| `versao` | FK `VersaoConsolidada` PROTECT | a norma sob a qual a projeção foi feita |
| `metodo_hash` | char(64) | `canonical_sha256` do `drawMethod` do marco **nessa versão** (FR-067) |
| `criterio_de_projecao` | texto | a frase publicada de quem entrou e por quê (R-012) |
| `quantidade` | inteiro | redundância deliberada: o manifesto a publica, e ela é conferível |
| `resumo` | char(64) | `canonical_sha256` do conteúdo canônico da relação |
| `publicada_em` / `publicada_por` | datetime / char | |
| `relacao_anterior` | FK self, nula, PROTECT | sucessão |
| `motivo_da_sucessao` | texto | obrigatório quando há anterior |

**`marco_id` e `metodo_hash` são o compromisso do método.** Sem o primeiro a relação não sabe qual
marco a governa e o método não é localizável; sem o segundo, "o método vigente" seria resolvido no
instante do sorteio — isto é, **depois** da semente —, que é exatamente o que a D-014 fecha. Com os
dois, a relação publicada já **prova**, criptograficamente e antes de existir semente, sob qual
método aquele universo se comprometeu.

**Constraints**

- **A unicidade de raiz parte em duas, pela mesma cirurgia do `AtoDeOrdenacao`** (D-014, FR-070):

  ```python
  UniqueConstraint(fields=["edital", "perfil_id", "marco_id"],
                   condition=Q(relacao_anterior__isnull=True, lista_id__isnull=True),
                   name="uq_relacao_raiz_por_marco")
  UniqueConstraint(fields=["edital", "perfil_id", "marco_id", "lista_id"],
                   condition=Q(relacao_anterior__isnull=True, lista_id__isnull=False),
                   name="uq_relacao_raiz_por_marco_e_lista")
  ```

  A cadeia de sucessão continua dizendo qual é a vigente — a última sem sucessor —, e agora há
  **uma** cadeia por recorte, e não quantas se quisesse abrir. A versão anterior deste documento
  recusava a unicidade de raiz por leitura da sucessão; a leitura estava certa e a conclusão não:
  sucessão ordena uma cadeia, não impede que nasçam duas.
- `uq_relacao_sucessora_unica` em `relacao_anterior`, where not null.
- `ck_relacao_sucessao_com_motivo` — sucessora exige motivo.
- `ck_relacao_nao_vazia` — `quantidade >= 1` (FR-009).

**Conteúdo canônico da relação** (o que o `resumo` cobre):

```json
{
  "relationId": "<uuid>", "editalId": "<uuid>", "versionId": "<uuid>",
  "profileId": "<uuid>", "milestoneId": "<uuid>", "listId": "<uuid|null>",
  "methodHash": "<64 hex>",
  "criterion": "<texto publicado>",
  "participants": [{"publicNumber": 1, "name": "…", "protocol": "INS-2026-XXXX"}]
}
```

**O `registrationId` saiu, e a saída dele é requisito, não economia.** O manifesto e a FR-005
proíbem identificador interno no canal público; enquanto o resumo o cobrisse, o cidadão receberia um
`relationHash` que **não conseguiria recalcular** da relação que lê — teria de acreditar nele, que é
a palavra que esta feature existe para não pedir. O conteúdo canônico passa a ser exatamente a
projeção pública da FR-005: número, nome e protocolo, nesta ordem de chaves canônicas. Um resumo
interno, se algum dia for preciso, é outro campo e outro nome.

### `ParticipanteHabilitado`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `relacao` | FK `RelacaoDeHabilitados` CASCADE | |
| `inscricao` | FK `Inscricao` PROTECT | a inscrição não desaparece sob a relação que a cita |
| `numero_publico` | inteiro ≥ 1 | atribuído na projeção, por protocolo crescente (R-011) |

**Constraints**: `uq_participante_por_relacao` em `(relacao, inscricao)`;
`uq_numero_por_relacao` em `(relacao, numero_publico)`.

### `OcorrenciaDaFonte`

O material observado. Não é o ato, e observar não decide nada.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `fonte` / `referencia` | char / char | |
| `material_bruto` | texto | como veio da fonte, sem interpretação |
| `observada_em` / `observada_por` | datetime / char | |
| `indisponivel` | booleano | registra a hipótese que aciona a substituição |
| `evidencia` | texto | o que se observou, quando `indisponivel` (FR-015, R-006) |

**Constraint**: `uq_ocorrencia_por_fonte` em `(fonte, referencia)` — observar duas vezes devolve a
mesma linha, e é o que torna a observação idempotente.

**`semente_normalizada` saiu daqui** (D-016, FR-019). A linha é única por `(fonte, referência)` e a
normalização é regra do **método**: guardar a semente derivada aqui congelaria a regra do primeiro
método que observasse aquela ocorrência e a imporia, calada, a todo método posterior que a citasse.
A ocorrência guarda o que a fonte publicou; a derivação mora no `Sorteio`.

**Toda observação fica registrada, inclusive a que não virou sorteio.** É o controle que torna
visível o descarte de ocorrência (R-006).

### `Sorteio`

A proveniência do ato: o que amarra relação, método e ocorrência à ordem produzida.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | identidade pública, é o que a verificação endereça |
| `edital` | FK PROTECT | |
| `perfil_id` / `lista_id` | UUID / UUID nulo | recorte |
| `relacao` | FK `RelacaoDeHabilitados` PROTECT | e é ela que carrega recorte, versão e método |
| `ocorrencia` | FK `OcorrenciaDaFonte` PROTECT | |
| `metodo_hash` | char(64) | copiado de `relacao.metodo_hash`, e conferido contra ele |
| `semente_normalizada` | char | o material bruto sob a regra do método (D-016) |
| `ato` | OneToOne `AtoDeOrdenacao` PROTECT | a ordem |
| `manifesto_hash` | char(64) | resumo do manifesto derivado (R-007) |
| `executado_em` / `executado_por` | datetime / char | |
| `sorteio_anterior` | FK self, nulo, PROTECT | anulação |
| `motivo_da_anulacao` | texto | obrigatório quando há anterior |

**O comando de constituição não recebe método** (FR-067). Ele lê `relacao.versao.content`, localiza
o `drawMethod` do `relacao.marco_id`, confere que o resumo daquele objeto bate com
`relacao.metodo_hash` — e recusa se não bater, porque isso significaria que a relação cita um método
que a versão citada não contém — e só então normaliza o material bruto e calcula. É o que faz a
FR-039 valer: a reprodução lê a mesma versão congelada, e nunca a vigente.

**Constraints**

- `uq_sorteio_raiz` em `(relacao, ocorrencia)` where `sorteio_anterior IS NULL` — **a tupla da D-009
  e da FR-031**. `perfil_id` e `lista_id` ficam **fora** dela porque a relação já os carrega: incluí-los
  não restringiria nada e sugeriria que um sorteio pudesse ter recorte diferente do da sua própria
  relação. **O método saiu pela mesma razão, e é a razão que mudou**: desde a D-014 ele não é escolha
  do sorteio, e sim citação da relação — dada a relação, o método está determinado, e mantê-lo na
  chave sugeriria uma liberdade que o modelo deixou de ter;
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

**`universo` num ato constituído por sorteio.** É `JSONField` com `default=dict`, e é o campo que
`comparar()` consome para decidir obsolescência. Um ato de sorteio grava ali a proveniência que o
originou — `{"origem": "SORTEIO", "sorteioId": …, "relacaoId": …, "relationHash": …, "quantidade": N}`
—, e **nunca** um resumo de Etapas, que não existiu. Deixá-lo `{}` faria o ato passar pela leitura
sem denunciar nada e quebrar na comparação; enchê-lo com forma de ato computado seria mentir sobre a
origem. É esta chave `origem` que a FR-069 usa para despachar.

### `classificacao.PosicaoNaOrdem` — o que cada campo recebe num ato de sorteio

Nenhuma alteração de esquema, e ainda assim é preciso dizer: `consequencia` é `CharField` **sem
default**, e sem valor definido a primeira gravação de posição falha no banco.

| Campo | Valor num ato constituído por sorteio | Porquê |
|---|---|---|
| `posicao` | 1..N, sem lacuna | todos os participantes recebem posição (FR-025) |
| `motivo` | `""` | `ck_posicao_ou_motivo` exige motivo vazio quando há posição |
| `consequencia` | `HABILITADA` | é o que o motor já grava para quem recebe posição (`calculo.py:158`) |
| `pontuacao_combinada` | `NULL` | não há grandeza a afirmar — sorteio não pontua |
| `modalidade_id` | a modalidade da inscrição, como hoje | é coluna da posição, e continua sendo |
| `empate_residual` | `False` | a ordem é total: o desempate por número público não deixa empate |
| `desempate` | `[]`, ou o registro da colisão quando ela ocorre | proveniência do que separou duas chaves idênticas (D-005) |

**Uma ressalva de vocabulário, registrada e não resolvida aqui.** `HABILITADA` é o termo que a `015`
usa para "considerada e posicionada", e é o que o motor grava. Ele **não** afirma habilitação no
sentido do Edital — quem habilita é a análise documental, que nesta feature vem depois e é de outra
capacidade (FR-064). Reusar o valor mantém uma grafia só para o mesmo estado do motor; renomeá-lo
seria mexer na `015` por causa da `021`.

### `divulgacao.PublicacaoResultado`

A D-015, e a parte da dimensão da lista que a D-006 não tinha atravessado.

| Alteração | Forma |
|---|---|
| `lista_id` | `UUID`, nulo — identidade publicada da modalidade; `NULL` = ampla concorrência |

**A constraint vira duas parciais, pela cirurgia idêntica à do `AtoDeOrdenacao`:**

```python
UniqueConstraint(fields=["edital", "perfil_id", "marco_id"],
                 condition=Q(publicacao_anterior__isnull=True, lista_id__isnull=True),
                 name="uq_publicacao_raiz_por_marco")
UniqueConstraint(fields=["edital", "perfil_id", "marco_id", "lista_id"],
                 condition=Q(publicacao_anterior__isnull=True, lista_id__isnull=False),
                 name="uq_publicacao_raiz_por_marco_e_lista")
```

A primeira mantém o nome e a garantia de hoje para a publicação sem lista — toda publicação
existente tem `lista_id NULL` e continua sob exatamente a constraint que já a governava.

`uq_publicacao_por_ato_natureza`, em `(ato, natureza)`, **não muda e não precisa mudar**: três listas
são três atos distintos, e a duplicidade que ela recusa continua sendo a mesma.

### `classificacao` e `divulgacao` — a leitura, e não só a escrita

A FR-069, e o que o `plan.md` não tinha visto quando escreveu que `divulgacao` não mudava.

| Ponto | O que faz hoje | O que passa a fazer |
|---|---|---|
| `classificacao/application/selectors.py::ato_vigente` | filtra `(edital, marco_id)` e devolve o primeiro sem sucessor | recebe `lista_id` e filtra por ele; com três raízes no marco, "o primeiro" é sorteio de dado |
| `classificacao/application/selectors.py::estado_do_marco` | chama `calcular_ordem` e compara o resultado com `vigente.universo` | despacha por `vigente.universo["origem"]`: para `SORTEIO`, a obsolescência é a da **relação** — houve sucessora? —, e não a de um cálculo por Etapas |
| `divulgacao/domain/publicabilidade.py::aferir` | afere contra o estado recomputado do marco | consome o estado já despachado; nenhuma regra nova, e o caminho do ato computado sai bit a bit igual |

**O ato computado é a regressão que importa.** Toda alteração acima é aditiva por dispatch, e a
prova de que não houve dano é um teste que roda o caminho de hoje — marco sem lista, ato computado —
e afirma o mesmo desfecho de antes.

### `editais.EventoCronograma`

| Alteração | Forma |
|---|---|
| `location` | `char(255)`, `blank=True`, `default=""` — onde o evento acontece (D-008) |

Sem default institucional, sem validação de URL, um campo só. A sugestão vive na tela.

### Conteúdo canônico — dois degraus, e a ordem entre eles não é arbitrária

**Degrau 10 — `drawMethod` no marco de classificação** (D-013, FR-013, FR-014).

```python
DEGRAUS_DE_MARCO = {
    8: {"appealWindow": None},
    10: {"drawMethod": None},          # `None` = método não declarado
}
```

`DEGRAUS_DE_MARCO` e `elevar_marco` **já existem** — o degrau 8 os criou para a janela recursal da
`018`. O `drawMethod` é a segunda entrada da mesma estrutura, no mesmo nível da árvore, e `None`
afirma o que é verdade sobre todo Edital publicado antes: não declarou método, porque a capacidade
não existia. É a mesma leitura que o degrau 8 fez de `appealWindow`, e a mesma que a `020` fez de
`attachments`.

Forma do objeto, quando declarado:

```json
{
  "algorithm": "IFES-SORTEIO-SHA256-v1",
  "source": "…", "occurrence": "…", "derivation": "…",
  "normalization": "…", "substitutionRule": "…"
}
```

**Sem `id`, e sem entrada em `colecoes.py`**: não é coleção, é objeto único do marco — como
`appealWindow`. `/profiles/id=…/classificationMilestones/id=…/drawMethod/normalization` já resolve,
porque em objeto o segmento é nome de chave literal, e é isso que faz a FR-014 valer sem gramática
nova. **Sem campo de recorte**, porque a identidade do marco *é* o recorte (D-013).

**Degrau 11 — `schedule[].location`** (D-008).

`DEGRAUS_DE_EVENTO = {11: {"location": ""}}`, `SCHEMA_VERSION` 9 → 11 ao fim da feature. A ausência
significa "não declarado", e isso é verdadeiro sobre todo Edital publicado antes do degrau.
`/schedule/id=…/location` é endereçável pela gramática que já existe.

**Por que o método é o degrau menor.** O método é P1 e o local é P3, e a US6 é declaradamente
independente das demais e pode atrasar. Numerando o método antes, qualquer estado intermediário
entregável do branch para na `SCHEMA_VERSION` 10 com a árvore de degraus contígua. O contrário
deixaria um 11 publicado com o 10 por escrever.

---

## Transições

```text
drawMethod               declarado no conteúdo do Edital ──(Retificação)──▶ outro conteúdo, outra versão
                         não é linha de tabela, e não tem ciclo de vida próprio

RelacaoDeHabilitados     publicada ──(fato de origem sucedido)──▶ sucedida por relação nova
                         uma raiz por recorte; nunca editada, nunca excluída

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
| uma relação vigente por recorte | `uq_relacao_raiz_por_marco` + `…_e_lista` | FR-070 |
| relação com sucessora não é sorteada | comando de constituição | FR-071 |
| a relação cita o método antes da semente | `metodo_hash` gravado na publicação, conferido na constituição | FR-067 |
| marco sem método não congela relação | comando de publicação | FR-066 |
| semente derivada é do sorteio, não da ocorrência | `Sorteio.semente_normalizada` | FR-019, D-016 |
| três listas publicam três resultados | `uq_publicacao_raiz_por_marco_e_lista` | FR-068 |
| ato de sorteio não é aferido por recomputação | dispatch por `universo["origem"]` | FR-069 |
| semente nunca digitada | não existe campo de entrada em rota alguma | FR-017 |
| relação alterada invalida a ocorrência | comando compara `relacao.resumo` | FR-020 |
| um ato raiz por tupla | `uq_sorteio_raiz` + `uq_ato_raiz_por_marco_e_lista` | FR-031 |
| concorrência produz um ato | idempotência por chave + transação | FR-032 |
| ordem cobre todos | comando compara `quantidade` com posições gravadas | FR-025 |
| anulação exige motivo | `ck_sorteio_sucessao_com_motivo` | FR-053 |
| manifesto sem dado pessoal indevido | serializador do manifesto, com teste | FR-044 |
| nenhum valor pós-congelamento entra na chave | `domain/chave.py` recebe só os cinco campos do contrato, e o teste ataca a tentativa | FR-024 |
| resultado publicado exibe sorteio, algoritmo, semente e resumos | renderizador do documento de resultado | FR-046 |

## O que este modelo deliberadamente não tem

Vaga ocupada, suplência, remanejamento, lista de convocação e a interação entre listas do 57/28.
Nada aqui responde "quem entrou" — só "em que ordem ficaram" (FR-064).

**E não tem mais uma tabela `MetodoDeSorteio`.** Ela existia para carregar o que a FR-014 chamava de
conteúdo normativo, e não carregava: sem versão consolidada, sem signatário, fora do snapshot e fora
do alcance da Retificação. O método virou conteúdo do Edital (D-013), e as entidades
novas passaram de cinco a **quatro**: relação, participante, ocorrência e sorteio.
