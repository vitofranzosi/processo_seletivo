# Contrato: a tela `/gestao/` (`interface:lista`)

`GET` apenas. Exige identificação, como hoje. Sem escrita, sem sessão nova.

## Parâmetros

| Parâmetro | Exemplo | Efeito |
|---|---|---|
| (nenhum) | `/gestao/` | aba "Em andamento", página 1 (FR-4300) |
| `situacao` | `?situacao=cancelados` | a aba; inválida → "Em andamento" (FR-4315) |
| `busca` | `?busca=90%2F2026` | busca em todas as situações; a aba não vale (FR-4305) |
| `pagina` | `?situacao=todos&pagina=3` | a página; inválida → 1; além da última → a última |

Nenhum caso responde erro.

## Ordem de leitura (UX-272)

1. `h1` "Processos Seletivos" e o subtítulo com o **nome** da Unidade (FR-4322).
2. Avisos obrigatórios (demonstração, "Sem permissões", vínculo com comissão), como hoje.
3. A faixa "Ações disponíveis para você": título, **nota de cobertura**, itens, "Mostrar os outros";
   ou a frase vazia com as mesmas famílias (FR-4324, FR-4325).
4. "Novo Processo Seletivo", para quem cria.
5. `nav aria-label="Situação dos Processos"`: quatro links, cada um com a contagem no texto; o da aba
   aberta com `aria-current="page"`; nenhum com `aria-current` durante a busca (UX-270, FR-4309).
6. O formulário GET da busca: `label` visível "Buscar em todas as situações", campo `busca` com o texto
   buscado, botão "Buscar" (UX-271).
7. A frase do recorte ("61 Processos, mostrando 1–20") ou a da busca, com "Limpar a busca" (FR-4309,
   FR-4310, FR-4312, UX-273).
8. Os Processos: um `article.processo` cada, com o `header` da linha do Processo e uma lista `ul` de
   linhas de Edital; ou "Nenhum Edital neste Processo.".
9. `nav.paginacao`, só com mais de uma página: "Anterior", "Página N de M" (`aria-current="page"`),
   "Próxima".

## Linha do Processo (FR-4317)

Título com link para `interface:processo-detalhe`, código, selo da situação **real** (FR-4304), o selo do
vínculo, e, para quem gere, os links Comissão e Alocação por Etapa.

## Linha do Edital (FR-4318, FR-4319)

Número/ano com link para `interface:detalhe`; o título só quando difere do do Processo (some a 375 px);
o selo da situação; uma marca por Retificação em curso, com link, a situação dela e "aguarda {papel}" ou
"não pode mais prosseguir". **Nenhuma** ação, contador, ato desabilitado ou "Nenhuma ação disponível".

## Estados vazios

| Caso | Texto |
|---|---|
| unidade sem Processo | "Nenhum Processo Seletivo no seu escopo institucional." (como hoje) |
| aba vazia | "Nenhum Processo nesta situação." |
| busca sem resultado | "Nenhum Processo encontrado para “X” em nenhuma situação." + "Limpar a busca" |

## Contexto que os testes leem

`faixa` (como hoje), `processos` (os da página, cada um com `editais_da_linha`), `abas`, `recorte`,
`pagina`, `contagem`.
