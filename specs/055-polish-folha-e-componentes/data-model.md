# Data model — 055 · Polish da folha e dos componentes

**Não há entidade de domínio nova nem alterada.** Nenhum modelo, migration, formulário ou view muda
(**FR-1019**). O que esta feature desenha são **componentes da folha**, e o "modelo" deles é a
geometria que cada um promete. O contrato de cada um, com a medida que o prende, está em
[contracts/folha.md](contracts/folha.md).

| Componente | Marcação | Onde vive | O que muda |
|---|---|---|---|
| Bloco de números | `ul.resumo > li > strong + rótulo` | folha da gestão | nada na regra; passa a ser usado pela Ocupação e pelo Corte (**FR-1000** a **FR-1003**) |
| Célula de tabela | `th`, `td` | folha da gestão | preenchimento padrão `.5rem .75rem` (**FR-1004**) |
| Coluna numérica | `table.tabela td.numero` | folha da gestão | nada na regra; a ordem do marco passa a usá-la (**FR-1005**) |
| Botão | `.botao`, `.secundario`, `.perigoso`, `.desabilitado` | folha da gestão | caixa única de 40 px (**FR-1006**) |
| Ação de linha | `.acao` | folha da gestão | 40 px dentro de barra; 25 px fora (**FR-1007**) |
| Título | `h1`, `h2`, `h3` | folha da gestão | escala global (**FR-1010**, **FR-1011**) |
| Controle | `input` de uma linha, `select` | as duas folhas | uma altura por folha (**FR-1012**) |
| Barra de filtro | `.filtro`, `.filtros` | folha da gestão | alinhada pelo topo (**FR-1013**, **FR-1014**) |
| Corpo da seleção | `.corpo-da-selecao` | folha do portal | sem a área do sorteio quando não há sorteio (**FR-1015**) |
| Grade de campos | `.grade-de-campos` | folha do portal | colunas reservadas; controle largo até 40 rem (**FR-1016**) |

## Estados que a folha distingue

- **Barra** × **fora de barra**, para `.acao`: dentro de `.navegacao-etapa`, `.salvar` ou `.filtros`,
  a ação tem a caixa do botão; fora, continua pequena.
- **Com sorteio** × **sem sorteio**, para `.corpo-da-selecao`: decidido pela presença do filho
  `.sorteio-da-selecao`, que o template só renderiza quando há sorteio.
