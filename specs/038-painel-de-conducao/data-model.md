# Modelo — e de onde cada espécie lê

## Nenhuma entidade, nenhuma migration

A feature não persiste nada. O total do `make preparar` continua **`N de 33`** — a 33ª veio da
`036`. Se a saída disser 32, a worktree está atrás da `main`.

## De onde cada espécie nova lê

| Espécie | Fonte | Consulta nova? |
|---|---|---|
| avaliação distribuída e não concluída | `resumo_da_etapa` — `completas − avaliadas` | **não**; o `UX-003` já a chama |
| recurso aguardando julgamento com julgador | `recursos_do_edital(AGUARDANDO_JULGAMENTO)` + `impedidos_por_recurso` | **não**; o `UX-005` já as chama |
| recorte com ordem e sem ocupação | `ato_vigente` + `apuracao_vigente` | **sim, uma por recorte** — a Supervisão lê `ato_vigente`, mas **não lê** `apuracao_vigente` |
| ato emitido e não publicado | derivação hoje privada em `interface/views.py` | **sim** — e exige **extração**, não reescrita (`R-6`) |

## Por que o Pulso não muda

O pulso já responde por Edital, e a página do Processo passa a **lê-lo**, não a recalculá-lo. Duas
telas com o mesmo número calculado duas vezes é o defeito que a `FR-557` existe para impedir — e
foi o que esta série passou a semana removendo em outras telas.

## O que a feature não modela, de propósito

**Responsável.** Papéis vêm da sessão e não há registro que ligue identidade a papel — o próprio
`UX-005` o diz por escrito. Um campo "quem precisa agir" seria modelo para um dado que não existe.
Ver `D-003`.
