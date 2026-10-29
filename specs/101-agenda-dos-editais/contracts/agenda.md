# Contrato: a página da Agenda dos Editais

## Rota

`GET /gestao/agenda` — nome `interface:agenda`. Só `GET`; não há formulário de escrita nem endpoint
de API.

**Sem identidade na sessão**: a mesma resposta de toda tela da gestão (`pedir_identificacao`).
**Com qualquer identidade**: 200 (FR-2609). Não há recusa por capacidade, e não há 404.

## Parâmetros

| Parâmetro | Valores | Padrão | Inválido |
|---|---|---|---|
| `visao` | `mes`, `proximos` | `mes` | `mes` |
| `mes` | `AAAA-MM` | mês corrente na zona institucional | padrão |
| `dia` | `AAAA-MM-DD` (só com `visao=mes`) | nenhum | ignorado |
| `janela` | `7`, `30` (só com `visao=proximos`) | `7` | `7` |
| `edital` | UUID de Edital considerado | nenhum | ignorado — inclusive UUID de outro escopo |
| `especie` | `inscricoes`, `etapa`, `demais` | nenhuma | ignorado |

Com `dia`, o `mes` passa a ser o do dia. Todo link da página — abas, navegação de mês, células,
volta ao mês, janela de 30 dias — carrega `edital` e `especie` quando presentes (FR-2638).

## Estrutura da resposta

Na ordem do documento:

1. `<h1>Agenda dos Editais</h1>` e o parágrafo de proveniência (FR-2640), com o instante da leitura
   em `<time>` (FR-2643).
2. Abas: `<nav class="abas-da-agenda" aria-label="Visualizações">` com dois links; o da visualização
   ativa tem `aria-current="page"`.
3. Avisos de Retificação a vigorar, quando há: `<ul class="avisos-de-retificacao">`, um `<li>` por
   Edital (FR-2614).
4. Síntese: `<dl class="sintese-da-agenda">` com os quatro números da janela (FR-2634); ausente na
   consulta de um dia.
5. Filtros: `<form method="get" class="filtros-da-agenda">`, com `visao`, `mes`/`janela` em campos
   ocultos (FR-2637).
6. O conteúdo da visualização:
   - **mês**: navegação (`<nav class="navegacao-do-mes">`), `<table class="grade-do-mes">` com
     `<caption>`, sete `<th scope="col">`, células `<td>`; dia com marco tem
     `<a class="quantidade-do-dia">N marcos</a>`; célula destacada tem a classe `varios`; hoje tem
     `aria-current="date"`; nomes em `<ul class="nomes-do-dia">`. Depois, a seção *Períodos no mês*
     (`<section class="periodos-do-mes">`).
   - **dia**: `<section class="dia-consultado">` com os marcos do dia e *Períodos em curso neste
     dia*; link *Voltar a {mês}*.
   - **próximos**: `<section class="em-curso">`, depois um `<section class="dia-da-agenda">` por
     dia com marco, título `<h2>` com a data e a quantidade.
7. Legenda fixa de previsto × efetivo (FR-2641).

## O item (`_agenda_marco.html`)

`<li class="marco-da-agenda">` com: a hora ou *Abre*/*Encerra*; o nome publicado; *Edital NN/AAAA —
Processo*; o local, quando há; o intervalo, quando é marco de período; *Cancelado* (classe
`cancelado`) ou *data passada* / *em curso pelo cronograma*; e os dois links — `Edital` →
`interface:detalhe`, `Cronograma publicado` → `portal:selecao` + `#cronograma-titulo` (FR-2629).

## Estados

| Estado | Resposta |
|---|---|
| nenhum Edital publicado ou encerrado no escopo | *"Nenhum Edital da unidade tem cronograma publicado."* — sem grade, sem síntese, sem filtros |
| janela sem marco | *"Nenhum marco previsto …"*; e *"O próximo é em …"* quando há (FR-2644); no mês a grade é desenhada |
| filtro sem resultado | a mesma frase, mais o link *Limpar filtros* |

## Vocabulário proibido

O texto visível não contém *concluído*, *cumprido*, *realizado*, *pendente*, *atrasado* nem
*prazo* sem *previsto* ao lado (FR-2636, FR-2642).
