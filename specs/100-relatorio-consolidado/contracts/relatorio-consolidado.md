# Contrato: Relatório consolidado da unidade

## Rotas

| Método | Caminho | Nome | Porta | Resposta |
|---|---|---|---|---|
| GET | `/gestao/visao-geral/relatorio` | `interface:relatorio-consolidado` | `visao:consultar` | a escolha do conjunto: critério, atalhos e a lista dos Editais alcançados, marcados |
| GET | `/gestao/visao-geral/relatorio/conjunto` | `interface:relatorio-consolidado-ver` | `visao:consultar` | a camada executiva do conjunto e o formulário "Baixar PDF" |
| POST | `/gestao/visao-geral/relatorio/pdf` | `interface:relatorio-consolidado-pdf` | `visao:consultar` | o PDF, `attachment`, nome `relatorio-consolidado-<sigla>-emissao-<n>.pdf` |

Todas as respostas são privadas (`Cache-Control: private, no-store`). Sem identidade: pedido de
identificação. Sem a capacidade: a recusa explicada da `033`. Não há 404: as rotas não endereçam
objeto, e identificador alheio é ignorado (FR-2555).

## Parâmetros (GET e POST)

| Parâmetro | Valores | Padrão |
|---|---|---|
| `criterio` | `publicacao` · `numero` · `manual` | `publicacao` |
| `atalho` | `ano` · `s1` · `s2` (com `ano`) | `ano` |
| `ano` | inteiro | ano corrente |
| `inicio`, `fim` | `AAAA-MM-DD` (só `publicacao`, sem atalho) | — |
| `busca` | texto (só `manual`) | — |
| `escolha` | `1` quando a lista de marcados vale | ausente: todos os elegíveis |
| `edital` | UUID, repetido | — |

Valor fora do conjunto aceito cai no padrão; intervalo com `inicio` depois de `fim` é recusado com a
frase "A data inicial é posterior à final."

## Recusas da página e da emissão

| Situação | Código | Frase |
|---|---|---|
| conjunto vazio | 422 `conjunto_vazio` | "Nenhum Edital publicado entra neste conjunto. Escolha outro período ou marque Editais." |
| acima do limite | 422 `conjunto_grande_demais` | "O relatório reúne até 60 Editais por emissão, e este conjunto tem N. Reduza o período ou desmarque Editais." |
| caractere sem grafia | 422 `relatorio_sem_grafia` | a do relatório do Edital |
| concorrência | 409 `relatorio_concorrente` | "Outro registro foi gravado agora. Baixe o relatório de novo." |

## A ordem do documento

**Camada executiva**

1. Cabeçalho do órgão (a Unidade do escopo), título "Relatório consolidado da unidade", o período ou a
   escolha por extenso, a natureza gerencial.
2. Ficha: **Conjunto analisado** (critério, unidade, quantos Editais); **Data dos dados** ("dados até
   DD/MM/AAAA, HHhMM — o período escolheu os Editais; a situação de cada um é a deste instante");
   **Situação no GPS** (encerrados · publicados · cancelados); **Situação das providências**.
3. Visão geral (frases por regra).
4. Seis números, cada um com a base escrita embaixo.
5. Pontos de atenção (até três, ordem da FR-2576).

**Seções**

6. Oferta e procura — o que foi oferecido; inscrições enviadas, por mês do envio; por Edital; Perfis
   com procura menor que a oferta.
7. Execução e resultados — situação dos Editais por espécie; alterações; recursos; resultados
   publicados; vagas imediatas por situação de apuração; convocações.
8. Providências — por tipo; por Edital; registros na trilha depois do encerramento; o que este
   relatório não diz.

**Anexo técnico**

9. A1 Editais considerados (número/ano, título, primeira publicação, situação, espécie, endereço da
   página da seleção); Editais fora do conjunto e retirados.
10. A2 Critério do conjunto e data dos dados.
11. A3 Definição de cada número.
12. A4 Limitações e o que o GPS não registra.
13. A5 Emissão (número, instante, unidade).

Toda página: o conjunto, "dados até…", "Relatório gerencial — não é ato administrativo", "emissão nº
N" e "página X de Y".

## Frases fixas

- Natureza: "Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não
  substitui as publicações oficiais de cada Edital."
- Data dos dados: "O período escolheu os Editais. A situação de cada um é a de DD/MM/AAAA, HHhMM, e
  não a do fim do período."
- Série: título "Inscrições enviadas, por mês do envio"; nota "Os meses vão do primeiro ao último
  envio dos Editais do conjunto e podem passar do período que os escolheu."
- Trilha: "A trilha de auditoria tem N registros depois do encerramento" e, no anexo, "a contagem
  cobre os atos registrados na trilha de auditoria do GPS, e não todo acontecimento".
- Privacidade: "fora N Editais com menos de 5 inscrições enviadas, cujo relatório individual omite
  estes totais".
- Cancelado: "fora o Edital cancelado" / "fora os N Editais cancelados".
- Matrícula: "O GPS não registra matrículas. Este relatório mostra convocações aceitas, e não
  matrículas efetivadas."
