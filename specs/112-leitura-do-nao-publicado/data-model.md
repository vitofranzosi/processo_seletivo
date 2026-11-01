# Data Model: Leitura do conteúdo não publicado na gestão

**Nenhuma tabela, coluna, migration ou gatilho.** A feature acrescenta uma permissão ao catálogo e uma
regra de leitura; nada se grava.

## Permissão `rascunho:ler`

- Mora no `PAPEIS` de `interface/identidade.py`, escrita por extenso (`D-001`).
- Papéis: `elaborador`, `homologador`, `publicador`, `gestor` (FR-3502).
- Não entra em `PAPEIS_DE_ACESSO` nem em `PAPEIS_INSTITUCIONAIS` (`seguranca/acessos.py`).
- `DESCRICOES` não muda (FR-3522). `len(PAPEIS)` não muda.
- Os vínculos existentes passam a carregá-la na requisição seguinte, porque as permissões saem do
  papel, e não do vínculo: **não há migração de dado**.

## `Alcance`

Enumeração de três valores, ordenada: `NENHUM < EXISTENCIA < CONTEUDO`.

## A regra (`D-002`)

Entrada: o ator da requisição (escopo, permissões, sujeito) e o ato, já filtrado pelo escopo.

### Edital

| Condição, avaliada nesta ordem | Alcance |
|---|---|
| Edital tem ao menos uma Publicação | `CONTEUDO` |
| ator tem `rascunho:ler` | `CONTEUDO` |
| ator tem `auditoria:consultar` | `EXISTENCIA` |
| ator tem vínculo de comissão vigente no Processo do Edital (P-3) | `EXISTENCIA` |
| nenhuma das anteriores | `NENHUM` |

### Retificação

| Condição | Alcance |
|---|---|
| Retificação publicada | `CONTEUDO` |
| ator tem `rascunho:ler` | `CONTEUDO` |
| nenhuma das anteriores (P-4) | `NENHUM` |

A trilha de auditoria não pergunta à regra da Retificação (`D-005`).

### Processo

| Condição | Alcance |
|---|---|
| ao menos um Edital do Processo com alcance ≥ `EXISTENCIA` | `EXISTENCIA` |
| ator tem vínculo de comissão no Processo | `EXISTENCIA` |
| nenhuma das anteriores | `NENHUM` |

O Processo não tem "conteúdo" próprio: as telas dele listam Editais, cada um filtrado pela regra do
Edital.

## Transições

Nenhuma. O alcance muda quando o ato é publicado — a Publicação é append-only, e por isso o alcance
de um ato publicado nunca volta a cair.
