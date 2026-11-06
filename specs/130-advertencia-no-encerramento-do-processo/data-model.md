# Data Model: a advertência no "Encerrar Processo"

**Nada persistido.** Sem migration, tabela, coluna, permissão ou estado (SC-1325). As estruturas abaixo
são valores derivados no instante da leitura (R-4) e descartados depois da resposta.

## Lidos, sem mudança

| Fonte | O que se lê | Onde já é lido |
|---|---|---|
| `Edital` do Processo | estado (só ENCERRADO e CANCELADO), número, ano, título | `pending_editais` |
| `Publicacao` | existência, para excluir o Edital nunca publicado | relatório da `099` |
| `pendencias_do_edital.situacoes(edital, ato="encerrar", com_advertencias=True)` | as situações da `113`, filtradas por `TIPOS_NO_PROCESSO` | confirmação do Edital |
| `relatorio_do_edital.fatos_do_edital(edital, agora=)` | as providências nos tipos do `DA_099`, somadas como na confirmação do Edital | confirmação do Edital e relatório |

## Derivados (valores imutáveis, em `interface/encerramento.py`)

### `Item` (existente, um campo novo)

| Campo | Tipo | Nota |
|---|---|---|
| `mensagem` | texto | a frase da `113` ou da `099`, com ponto final |
| `url`, `rotulo` | texto | o caminho, só a quem a tela de destino aceita (FR-4355) |
| `a_quem_pedir` | texto | a quem não tem o caminho |
| `tipo` | texto, padrão `""` | **novo**: o tipo da situação ou da providência. Serve à UX-276 e aos testes. A confirmação do Edital não o lê, e por isso o padrão vazio não muda nada lá |

### `GrupoDoEdital`

| Campo | Tipo | Nota |
|---|---|---|
| `edital` | `Edital` | para número/ano, título, situação e o link ao detalhe |
| `itens` | tupla de `Item` | na ordem da confirmação do Edital: situações da `113`, depois providências da `099`; nunca vazia (FR-4358) |

### `AdvertenciaDoProcesso`

| Campo | Tipo | Nota |
|---|---|---|
| `grupos` | tupla de `GrupoDoEdital` | só Editais finais publicados com algo em aberto, por ano, número e id (R-3) |
| `convocado_no_prazo` | booleano | algum item é `CONVOCACAO_AGUARDANDO` (UX-276) |
| `resumo` | texto (64 hex) | `sha256` do JSON canônico `[[id do Edital, [mensagens]], …]` (R-5); a lista vazia também tem resumo |
| `vazia` | propriedade | `not grupos`, que decide a frase da UX-277 |

## As constantes de tipo (R-2)

- `TIPOS_NO_PROCESSO`: `PRAZO_RECURSAL_EM_CURSO`, `PRAZO_RECURSAL_NAO_DECLARADO`, `RECURSO_AGUARDANDO`,
  `REAVALIACAO_PENDENTE`, `PROVIDENCIA_PENDENTE`.
- `TIPOS_FORA_DO_PROCESSO`: `PERIODO_EM_CURSO`, `PERIODO_POR_ABRIR`, `PERIODO_SEM_TERMINO`,
  `RETIFICACAO_HOMOLOGADA`, `RETIFICACAO_EM_CURSO`, `RASCUNHOS_NAO_ENVIAVEIS` (D-002; o último só existe no
  cancelar).
- `DA_099` (existente): as três de convocação, `RESULTADO_NAO_DIVULGADO`, `DEFINITIVO_NAO_PUBLICADO` e
  `APURACAO_DESATUALIZADA`.

**Invariante, prendida pelo guardião unitário**: toda constante de tipo de `pendencias_do_edital` está
em exatamente um dos três conjuntos.

## O ciclo da tela (não é estado persistido)

```text
GET ──► mostra a lista L e o resumo r(L)
POST com r ──► relê L′
   ├─ r(L′) ≠ r, ou r ausente ──► 409: mostra L′, r(L′), UX-279, motivo de volta  (volta ao POST)
   └─ r(L′) = r ──► comando de hoje
         ├─ aceito ──► 302 ao detalhe
         └─ recusado (422 motivo, 409 revisão, …) ──► relê pendentes, impedimento e, se ainda
            confirmável, L″ e r(L″) (FR-4360)
```

A advertência só é lida quando a tela oferece o Confirmar (FR-4357). Nos outros casos a seta do POST vai
direto ao comando, como hoje.
