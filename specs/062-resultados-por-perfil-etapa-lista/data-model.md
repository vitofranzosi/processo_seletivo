# Data Model: Resultados divulgados por Perfil, etapa e lista

**Nenhum modelo, nenhuma coluna, nenhuma migration.** O que muda é a estrutura de tela que a página
do Edital monta a partir de dados já lidos (`FR-1165`).

## Entrada (já existe)

| Fonte | O que traz | Onde |
|---|---|---|
| Vigentes do Edital | por vigente: a `PublicacaoResultado` (`perfil_id`, `marco_id`, `lista_id`, `natureza`, `publicado_em`), os rótulos do cabeçalho congelado (`marco`, `marco_codigo`, `lista`, e `perfil` a partir desta feature) e as `anteriores` da cadeia | `historico_publico_do_edital` |
| Prazo de recurso | `recurso_ate` acrescentado a cada vigente | `views.selecao`, como hoje |
| Conteúdo vigente | `profiles` em ordem; em cada Perfil, `name` e `competitionModalities` em ordem | `versao.content`, já carregado |
| Inscrições da pessoa | as do Edital, por Perfil, com `status` | `_inscricoes_iniciadas`, já chamada |

## Saída: a árvore

```text
ResultadosDoPerfil
  perfil_id
  nome                 # vigente; congelado se o Perfil saiu do Edital (D-009)
  etapas: [ResultadosDaEtapa]

ResultadosDaEtapa
  marco_id
  nome                 # marco gravado na vigente mais recente da etapa (D-010)
  listas: [ListaDivulgada]
  anteriores: [ItemDoHistorico]     # vazio → sem bloco (FR-1157)

ListaDivulgada
  lista_id             # None = ampla concorrência
  nome                 # nome_da_lista
  publicacao           # a vigente
  natureza_rotulo
  recurso_ate          # None quando encerrado ou sem janela

ItemDoHistorico
  lista_nome
  publicacao           # a sucedida
  natureza_rotulo
```

## Ordem

| Nível | Regra | Desempate |
|---|---|---|
| Perfil | posição em `profiles` do conteúdo vigente; ausentes por último | publicação mais recente do grupo |
| Etapa | `marco_codigo` gravado | nome do marco |
| Lista | sem lista primeiro; depois posição em `competitionModalities` do Perfil; desconhecidas por último | nome gravado |
| Histórico | a ordem das listas acima; dentro da lista, mais recente primeiro | — |

## Convite

| Quem lê | Convite |
|---|---|
| sem sessão | "Entrar para ver minha situação" → acesso, com destino na página do Edital |
| sessão, 1 inscrição enviada no Edital | "Ver minha situação" → o acompanhamento da inscrição, onde a situação divulgada aparece |
| sessão, 2 ou mais enviadas | "Ver minhas inscrições" → a lista |
| sessão, nenhuma enviada | sem convite |
| nenhum resultado divulgado | sem bloco, e portanto sem convite |
