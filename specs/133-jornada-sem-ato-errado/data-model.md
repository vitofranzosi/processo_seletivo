# Data Model: A jornada não aponta o ato errado

**Nada persiste.** Sem migration, tabela, coluna nem estado (SC-1428). Os três conceitos abaixo são
derivados, no instante da leitura, do conteúdo vigente e dos atos que já existem.

## Marco intermediário (qualidade derivada do marco)

| Campo lido | De onde | Retificável? |
|---|---|---|
| `cutRule.governedStage` do marco | conteúdo vigente do Edital, Perfil | não (`mutabilidade.py:391`) |
| `stages` de cada outro marco do mesmo Perfil | conteúdo vigente | não (`mutabilidade.py:326`) |

**Regra (FR-4530, D-001).** O marco `M` do Perfil `P` é intermediário quando:

- `governedStage(M)` não é vazio;
- existe outro marco `N` de `P`, com `N ≠ M`, tal que `governedStage(M) ∈ stages(N)`.

**Saída da função pura:** o marco `N`, ou `None`. Se houver mais de um, vale o primeiro na ordem do
Perfil, que é só para a frase.

**Invariante.** Para um Edital publicado, a resposta é a mesma em todo instante, porque os campos
lidos não se retificam.

**O que ela governa:**

| Operação no recorte de `M` | Com `M` intermediário |
|---|---|
| Apurar a ocupação (inicial, sucessora, por efeito) | recusada |
| Acrescentar vaga | recusada |
| Causar faixa por déficit | recusada |
| Convocar (individual, lote, correção) | recusada |
| Desfecho, conferência de documento, comunicação, atestado de convocação existente | permitidos |
| Emitir ordem, corte, faixa seguinte pedida no corte, publicar resultado | inalterados |

## Espera recomendada do corte (apresentação de uma célula)

Entradas: `appealWindow.admits` do marco; se o resultado da lista já foi divulgado (célula da
publicação *feita* ou *obsoleta*); e a aferição da definitiva (`publicabilidade.aferir`):
`{nivel, codigo, mensagem, ate}`.

| Situação | Espera |
|---|---|
| marco sem recurso declarado | nenhuma |
| resultado não divulgado | sim, sem data, com a razão "o prazo começa com a divulgação" |
| divulgado, aferição em `JANELA_ABERTA`, `RECURSO_PENDENTE`, `REAVALIACAO_PENDENTE` ou `PROVIDENCIA_PENDENTE` | sim, com a data e a frase da aferição |
| demais | nenhuma |

A célula do corte em espera sai assim: `AGUARDA`, com `recomendacao=True`, `responsavel=""`, `ato="Emitir o
corte"` e `ate`. **A célula não é estado**, e o comando de corte não a lê.

## Vagas a ocupar sem chamada (conta da derivação)

```text
sem_chamada = max(faltando − #{convocações sem desfecho cuja espécie ≠ VAGA_INICIAL}, 0)
```

`faltando` vem da apuração vigente, lida pela `leitura_do_recorte`. A espécie vem da convocação
(`VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR`).

## Celula (apresentação, `interface/andamento.py`)

Campo novo: `recomendacao: bool = False`. Ele só muda a marca que o template desenha e a ordem de
preferência de `da_lista`, onde o que se pratica vem antes do que espera.
