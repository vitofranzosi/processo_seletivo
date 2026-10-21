# Modelo de dados: Prévia do sorteio

**Nenhuma tabela, nenhuma migration, nenhuma gravação** (FR-2509). Tudo abaixo vive na resposta do
fragmento e no formulário do painel. As entidades são as da spec, campo a campo.

## Semente fictícia

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `material` | texto: cinco números de seis dígitos, separados por espaço | `secrets.randbelow(10**6)` cinco vezes, na interface (R-004) | nunca digitado (FR-2483) |
| `regra` | identificador de normalização | o método do marco; o comum do Edital; senão `DIGITOS_EM_SEQUENCIA` (D-007) | `supos_regra` = verdadeiro quando caiu no último caso |
| `semente` | texto | `normalizacao.normalizar(material, regra)` | é o `seed` de toda ordem da rodada |
| `token` | texto assinado | `signing.dumps({edital, perfil, marco, material}, salt="previa-do-sorteio")` | o servidor só aceita o que assinou para aquele marco (FR-2483, SC-931) |

**Ciclo.** Sem `token` no pedido → semente nova. Com `token` válido e `sortear` ausente → a mesma semente
(D-006). Com `sortear=1` → semente nova. Com `token` inválido ou de outro marco → recusa, sem cálculo.

## População informada

| Campo | Tipo | Regra |
|---|---|---|
| `so_ampla` | inteiro ≥ 0 | sugestão: dobro das vagas da linha geral; dez sem linha (FR-2487) |
| `por_reservada` | `{lista_id: inteiro ≥ 0}` | uma entrada por recorte reservado, na ordem da derivação (R-006); mesma sugestão pela linha da lista |
| `total` | inteiro | `so_ampla + Σ por_reservada`; ≤ 600 (FR-2491) |
| `sugerida` | booleano por lista | verdadeiro enquanto o elaborador não mudou aquele número |

**Candidato fictício**: `id` estável (`a<i>` só da ampla, `<lista>-<i>` autodeclarado), `nome` do
repertório de `cenarios_da_previa` pela posição na população, `lista_id` (`None` para só da ampla). O
`id` e o nome não mudam quando outra quantidade muda (FR-2490).

## Relação fictícia (uma por recorte)

| Campo | Regra |
|---|---|
| `lista_id` | `None` para a ampla |
| `participantes` | ampla: todos os candidatos; reservada: só os da lista; na ordem da população |
| `numero_publico` | 1 a N, nessa ordem (R-005) |
| `resumo` | SHA-256 canônico de `{"previaDoSorteio": true, perfilId, listaId, participantes: [[número, nome]]}` — forma diferente da relação oficial, de propósito |
| `draw_scope_id` | `chave.recorte(perfil_id, lista_id)` |

## Rodada

Por recorte, na ordem da derivação (a ampla primeiro):

| Campo | Origem |
|---|---|
| `ordem` | `[{inscricao_id, posicao, empate_residual: False, numero_publico}]`, de `chave.ordem` (R-002) |
| `corte` | `corte_da_ordem(regra, ordem, [], alvo, suplentes)` — a função da `094`, tornada pública (R-008) |
| `consequencias` | `previa.consequencias` |
| `posicao_na_ampla` | `{inscricao_id: posição}` da ordem da ampla, para o detalhe da reservada (FR-2494) |

E, para o Perfil:

| Campo | Origem |
|---|---|
| `ocupacao_por_recorte` | `rodada_da_previa.rodada(entradas, especie=...)`, injetada (FR-2497–FR-2499) |
| `todos_tem_posicao` | verdadeiro em todo recorte: o sorteio dá posição a todos (FR-2496) |
| `menos_inscritos_que_vagas` | por recorte, `len(ordem) <= vagas` |

## Resumo das rodadas

| Campo | Definição |
|---|---|
| `rodadas` | 1.000 (R-003) |
| `sementes` | `f"{semente}:{i}"`, i de 0 a 999 — derivadas da exibida (FR-2502, D-006) |
| por reservada: `com_sobra` | rodadas com `sem_ocupante_antes > 0`, em porcentagem |
| por reservada: `sem_ocupante` | média de `sem_ocupante_antes` |
| por reservada: `pela_ampla` | média de `len(ocupam_pela_ampla)` |
| por reservada: `cedidas` | média de `cederia`, só com reversão declarada |
| por reservada: `com_cessao` | rodadas com `cederia > 0`, em porcentagem, só com reversão declarada |
| ampla: `autodeclarados_ocupando` | média, sobre as rodadas, da soma de `ocupam_pela_ampla` das reservadas |
| `constante` | por número, verdadeiro quando todas as rodadas deram o mesmo valor — o painel diz "em todas as rodadas", e não uma porcentagem (FR-2503) |
| `nao_avaliado` | por recorte, quando a rodada não o avalia (sem linha no quadro, corte não emitido): o resumo diz por quê, e não calcula média |

**Nenhum campo do resumo vem de fórmula própria**: cada um é a soma, rodada a rodada, de um campo que
`rodada_da_previa.rodada` já devolve (FR-2504).
