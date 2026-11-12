# Data Model: Destinação da vaga reservada sem ocupante

**Feature**: [spec.md](spec.md) · **Pesquisa**: [research.md](research.md)

Duas migrations: `ocupacao/0005` e uma de `editais` (a coluna da declaração). Uma tabela nova, que é
append-only, e colunas novas em duas tabelas que já são. Nada é atualizado nem apagado: as linhas
antigas ficam como estão, e as colunas novas são nulas ou têm padrão.

> **Nesta entrega (12/11/2026, entrega mínima).** Entram a tabela `VagaNaoPreenchida` e a coluna
> `ApuracaoDeOcupacao.nao_preenchidas`, numa migration só, `ocupacao/0005_vaga_nao_preenchida.py`,
> reescrita antes de ser aplicada fora dos bancos de desenvolvimento e de teste. **As colunas novas
> de `MovimentoDeVaga` e a `editais/0028` (a terceira resposta da reversão) ficaram na branch
> preservada** `claude/155-destinacao-completa`, com a destinação e a passagem entre cotas: as
> seções delas abaixo estão marcadas *(próxima entrega)*. Nesta entrega a `apuracao` da
> `VagaNaoPreenchida` é obrigatória — o sorteio sem relação, único caso em que faltaria, é da
> próxima.

## `ocupacao.MovimentoDeVaga` (existente, ganha colunas) *(próxima entrega)*

| Campo | Hoje | Depois | Regra |
|---|---|---|---|
| `apuracao` | FK obrigatória, "a apuração que causou" | FK **nula**, "a apuração lida pelo ato" | `ck_movimento_com_recorte`: apuração ou recorte |
| `especie` | `REVERSAO_DE_COTA` (só *choices*) | + `DESFAZIMENTO_DA_REVERSAO` | `ck_movimento_especie` |
| `edital`, `perfil_id`, `marco_id` | — | nulos nas antigas; preenchidos nos novos | lidos por `_movimentos_que_alcancam` junto com `apuracao__…` |
| `gatilho` | — | `ON_EXHAUSTION` \| `ON_BALANCE` \| vazio (antigos) | — |
| `fundamento` | — | a frase publicada da reversão e a versão | não vazio nos novos |
| `versao` | — | FK da versão do Edital lida | — |
| `desfaz` | — | autorreferência | `ck_desfazimento_cita_o_movimento`: espécie de desfazimento ⇔ `desfaz` preenchido |
| `origem_lista_id`, `destino_lista_id`, `quantidade`, `causa`, `registrado_por`, `registrado_em` | — | iguais | `ck_movimento_quantidade_positiva`, `ck_movimento_recortes_distintos` continuam |

Leitura: o movimento de desfazimento move a mesma quantidade no sentido contrário, e a apuração o lê
como qualquer movimento (`recebidas`, `cedidas`).

## `ocupacao.VagaNaoPreenchida` (nova, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `edital`, `perfil_id`, `marco_id`, `lista_id` | recorte; `lista_id` nulo é a linha geral (D-014) | |
| `apuracao` | FK: a apuração lida | nesta entrega, obrigatória; nula só no sorteio sem relação, na próxima entrega |
| `especie` | `DECLARACAO` \| `DESFAZIMENTO` | `ck_nao_preenchida_especie` |
| `desfaz` | autorreferência | `ck_nao_preenchida_desfazimento_cita` |
| `quantidade` | inteiro > 0 | `ck_nao_preenchida_quantidade_positiva` |
| `fundamento` | texto não vazio | `ck_nao_preenchida_com_fundamento` |
| `versao` | FK da versão do Edital | |
| `registrado_por`, `registrado_em` | | |

Gatilho `reject_occupancy_mutation()` (o da `0001`), entrada em `TABELAS_APPEND_ONLY` com
justificativa, privilégio revogado pelo `provisionar_papeis`.

## `ocupacao.ApuracaoDeOcupacao` (existente, ganha coluna)

| Campo | Depois | Regra |
|---|---|---|
| `nao_preenchidas` | inteiro, padrão 0 | `ck_apuracao_ocupadas_no_limite` passa a `ocupadas + nao_preenchidas ≤ efetivas` |
| `universo.naoPreenchidasLidas` | ids lidos | reproduzir é reler estes (FR-6342) |
| `faltando` (propriedade) | `efetivas − ocupadas − nao_preenchidas` | |

Causa de obsolescência nova: `declaracao_posterior`.

## `editais.PerfilVaga.especie_de_reversao` (existente) *(próxima entrega)*

*Choices* passam a `ON_EXHAUSTION`, `ON_BALANCE` e `THROUGH_OTHER_QUOTAS`. O conteúdo publicado
(`vacancyReversion.kind`) aceita os três. Não há degrau canônico novo (R-003).

## Trilha (eventos novos, sem tabela)

| Evento | Quando |
|---|---|
| `OCUPACAO_DESTINAR_VAGA` | destinação à ampla *(próxima entrega)* |
| `OCUPACAO_DESFAZER_DESTINACAO` | desfazimento da destinação *(próxima entrega)* |
| `OCUPACAO_DECLARAR_NAO_PREENCHIDA` | declaração de vaga não preenchida |
| `OCUPACAO_DESFAZER_NAO_PREENCHIDA` | desfazimento da declaração |
| `OCUPACAO_DESFAZIMENTO_IMPEDIDO` | desfazimento recusado por chamada dependente (FR-6335) |
| `CLASSIFICACAO_LISTA_SEM_CONCORRENTE` | o gesto da lista vazia (ordem e corte emitidos nele) *(próxima entrega)* |

## Estados da vaga sem quem a ocupe (derivados, não gravados)

**Nesta entrega** os estados são `sem_vaga_a_destinar`, `impedida`, `nao_preenchida_disponivel` e
`reversao_pela_apuracao` — a reserva cuja reversão o Edital declara e que a apuração ainda não cedeu,
pela regra de antes da `155`: nenhum ato é oferecido, e a tela diz a regra e o próximo passo.
`destinacao_disponivel`, `passagem_entre_cotas` e `aguarda_d015` são da próxima entrega, e o desenho
abaixo, o da implementação completa, fica como estava.

```text
sem_vaga_a_destinar ─┬─> impedida (resultado provisório | recurso | chamada em curso | ampla sem aceite | apuração obsoleta)
                     ├─> destinacao_disponivel        (reversão declarada, condição cumprida)
                     ├─> nao_preenchida_disponivel    (sem reversão declarada, ou linha geral sem quem ocupe)
                     ├─> passagem_entre_cotas         (terceira resposta: nada se oferece)
                     └─> aguarda_d015                 (por saldo, até o incremento F)
destinacao_disponivel ──ato──> destinada ──ato contrário, sem chamada dependente──> sem_vaga_a_destinar
nao_preenchida_disponivel ──ato──> nao_preenchida ──ato contrário, sem chamada dependente──> ...
```
