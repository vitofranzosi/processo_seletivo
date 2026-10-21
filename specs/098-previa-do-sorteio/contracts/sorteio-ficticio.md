# Contrato: o sorteio fictício, puro, e a garantia de igualdade

Dois módulos novos no app do sorteio, nenhum com gerador de aleatoriedade (R-004): a varredura de
`tests/unit/sorteios/test_sem_gerador_pseudoaleatorio.py` os alcança sem emenda.

## `sorteios/domain/simulacao.py` — puro, sem Django e sem banco

```text
populacao(so_ampla, por_reservada, *, nomear) -> [CandidatoFicticio]  # nomear: o da 094, por parâmetro
relacao_ficticia(candidatos, *, perfil_id, lista_id) -> RelacaoFicticia   # numerada e resumida (R-005)
ordem_do_recorte(relacao, *, perfil_id, lista_id, semente, relation_hash=None) -> [ItemDaOrdem]
semente_da_rodada(semente, indice) -> str                                  # f"{semente}:{indice}"
```

- `ordem_do_recorte` chama `chave.ordem` e mais nada. `relation_hash=None` usa o resumo da relação
  fictícia; o teste de equivalência passa o oficial (R-009).
- `ItemDaOrdem` = `{inscricao_id, posicao, empate_residual: False, numero_publico}` — o formato que o
  corte e a rodada de ocupação da `094`/`095` leem (R-008).
- Nada aqui sabe de Modalidade além do `lista_id`, nem de vaga, corte ou ocupação.

## `sorteios/application/simulacao.py` — a rodada e o resumo

```text
simular_sorteio(marco, *, perfil_id, metodo, material, candidatos, recortes,
                apurar_recortes=None, resumos_oficiais=None) -> PreviaDoSorteio
resumir(marco, *, perfil_id, semente, candidatos, recortes,
        apurar_recortes, rodadas=1000) -> ResumoDasRodadas
```

- `material` chega pronto, da interface; daqui ele só é normalizado (`normalizacao.normalizar`).
- O corte de cada recorte é `classificacao.application.previa.corte_da_ordem` (R-008), com o alvo e os
  suplentes da regra do marco e, no alvo do quadro, a linha de cada recorte.
- A ocupação é `apurar_recortes(entradas)`, injetada pela interface como na `095`; sem ela, a prévia não
  fala de ocupação e o resumo não é calculado.
- `resumir` chama a mesma rodada para cada `semente_da_rodada(semente, i)` e soma os contadores do
  [data-model](../data-model.md); não guarda as ordens.

## A garantia de igualdade

1. **Para todo vetor normativo de ordem** — os de `backend/tests/contract/fixtures/sorteio/`, descritos
   no § 5 de `specs/021-sorteio-publico-auditavel/contracts/algoritmo-sorteio.md` —,
   `ordem_do_recorte(..., relation_hash=<o do vetor>)` devolve a ordem publicada no vetor.
2. **Para todo caso da matriz da R-009**, com os resumos oficiais injetados e o mesmo material, as
   ordens, as faixas, as quatro quantidades e as vagas cedidas da prévia são as do caminho oficial
   (`constituir_sorteio` → corte → apuração).
3. **Sentinela**: com um dígito do material trocado só na prévia, a igualdade do item 2 **quebra**.
   (Trocar a regra de normalização não serve: no formato da Loteria Federal, as duas regras dão a mesma
   semente.)
4. **Lista vazia**: a reservada sem participante não tem ordem, e a rodada a lê como corte não emitido
   — a recusa do caminho oficial, nos termos da prévia —, sem vaga cedida.
5. **Determinismo**: a mesma semente, a mesma população e os mesmos recortes dão o mesmo
   `PreviaDoSorteio` e o mesmo `ResumoDasRodadas`.
