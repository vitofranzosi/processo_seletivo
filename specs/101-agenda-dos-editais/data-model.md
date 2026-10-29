# Data Model: Agenda dos Editais

**Nenhuma entidade persistida é criada ou alterada.** Tudo abaixo é forma derivada, imutável
(`dataclass(frozen=True)`), montada a cada leitura a partir de `Edital`, `ProcessoSeletivo` e
`VersaoConsolidada`, e descartada depois da resposta.

## Fontes lidas

| Fonte | O que se lê |
|---|---|
| `Edital` | `id`, `number`, `year`, `status`, `institution_scope`, `processo` |
| `ProcessoSeletivo` | `title` |
| `VersaoConsolidada` vigente (`versoes_vigentes`) | `content["schedule"]` (`id`, `type`, `description`, `startAt`, `endAt`, `status`, `location`, `isRegistrationPeriod`) e `content["stages"][].scheduleEventId` |
| `VersaoConsolidada` futura | `edital_id`, `min(valid_from)` com `valid_from > agora` |

## Formas derivadas

### `EditalDaAgenda`

O Edital como a agenda o nomeia: `id`, `numero` (`"12/2026"`), `processo` (título), `status`.

### `Marco`

Um ponto da agenda (D-002).

| Campo | Regra |
|---|---|
| `dia` | `date` do instante na `ZONA` (FR-2616) |
| `instante` | o `datetime` do ponto (início, ou término no encerramento) |
| `hora` | `"14h"`, `"14h30"`, ou `"8h–12h"` no pontual com término no mesmo dia; vazio à meia-noite exata sem término |
| `tipo` | `pontual` · `abertura` · `encerramento` (FR-2618, FR-2619) |
| `evento_id` | identidade do Evento publicado (estável entre versões) |
| `nome` | `description`, ou `type` quando vazia (FR-2622) |
| `local` | `location` aparado; vazio é não declarado |
| `intervalo` | `"03/11 a 15/11"` nos marcos de período; `"desde 03/11"` no aberto sem término |
| `especie` | `inscricoes` · `etapa` · `demais` (research R-007) |
| `fase` | `por_vir` · `em_curso` · `passada` (research R-006) |
| `cancelado` | `status == "CANCELADO"` (FR-2621) |
| `edital` | `EditalDaAgenda` |

**Invariantes**: um Evento pontual produz um marco; um período, dois (ou um, sem término); nenhum
marco em dia intermediário. Marco cancelado não conta.

### `Periodo`

Um intervalo, dito uma vez (D-002): `evento_id`, `nome`, `edital`, `inicio`, `fim` (anulável),
`dia_inicio`, `dia_fim` (anulável), `intervalo`, `especie`, `fase` (a do Evento, pela régua com o
período de inscrições — FR-2617), `restante` (dias até o encerramento previsto, quando em curso e
com término). **Período cancelado não entra** nas listas de períodos nem no bloco *em curso*: ele
não está correndo; os marcos dele continuam ditos *Cancelado* nas listas de marcos.

### `Janela`

`inicio` e `fim` (`date`, inclusivos), e o rótulo (*"novembro de 2026"*, *"29/10 a 04/11"*,
*"12/11/2026"*). Três formas: o mês (`mes`), os próximos 7 ou 30 dias a partir de hoje (`proximos`)
e o dia (`dia`).

### `DiaDaGrade`

Uma célula: `data` (anulável — célula de fora do mês), `quantidade` (marcos não cancelados),
`nomeados` (até dois marcos não cancelados), `mais` (`quantidade − len(nomeados)`), `destaque`
(`quantidade >= 2`, D-010), `hoje`.

Semanas: lista de sete `DiaDaGrade`, de domingo a sábado, de 4 a 6 linhas.

### `Sintese`

Sobre os marcos **exibidos** da janela (depois dos filtros), sem os cancelados (FR-2634):
`marcos`, `editais` (distintos), `encerramentos` (marcos de tipo `encerramento`), `dias_com_varios`
(dias com 2 ou mais marcos), `dia_mais_carregado` (`(data, quantidade)`, ou nada quando nenhum dia
tem mais de um). Invariante: no mês, `Σ DiaDaGrade.quantidade == Sintese.marcos` (FR-2635).

### `AvisoDeRetificacao`

`edital` e `vigora_em` (`datetime`), para todo Edital considerado com versão de `valid_from` futuro
(FR-2614).

### `Filtros`

`edital` (UUID ou nada), `especie` (`inscricoes` · `etapa` · `demais` ou nada), e as opções:
os Editais considerados com algum Evento, ordenados por ano e número.

### `Leitura`

O que a página recebe: `visao`, `janela`, `filtros`, `marcos` (da janela, ordenados por instante,
Edital e nome), `por_dia` (`[(data, [Marco])]`), `periodos` (que tocam a janela), `em_curso`
(períodos em curso no instante da leitura), `periodos_no_dia` (no dia consultado), `semanas`
(no mês), `sintese`, `avisos`, `proximo` (o primeiro marco não cancelado depois da janela, quando
a janela está vazia), `tem_editais` (algum Edital considerado), `lido_em`, e os endereços de
navegação (mês anterior, seguinte, corrente; abas; limpar filtros).

## Estados

Nenhum estado novo. A fase é derivada a cada leitura (régua da `045`/`047`); a situação do Edital é a
do modelo; a vigência é a das versões.
