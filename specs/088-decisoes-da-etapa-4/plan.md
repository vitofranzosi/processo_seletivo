# Implementation Plan: As quatro decisões de produto da etapa 4

**Branch**: `claude/decisoes-da-etapa-4-088-698fba` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Uma regra de impressão na folha comum, três rótulos de trilha e o destino de um link. Na mídia de
impressão, o cabeçalho de contexto deixa de sair da página — sai sem "Trocar identidade", sem a
altura mínima e sem a moldura da tela —, e a barra lateral continua fora (D-001, D-005). Nas três
telas dos avisos que nomeiam um aviso, o rótulo ganha a hora, com o mesmo filtro de data do título
(D-003). No Ato de classificação, a view passa a entregar o endereço da Classificação no recorte do
ato, derivado como o da conferência da emissão, e o template o usa no lugar do `{% url %}` sem
recorte (D-004). A decisão (2) do usuário é só registro (D-002). Nenhuma migration, nenhuma
permissão, nenhum endereço de rota, nenhuma classe nova.

## Technical Context

Django 5 sobre PostgreSQL. A folha comum é o `<style>` de
`interface/templates/interface/base.html`; a regra de impressão de hoje é
`.barra-lateral,.cabecalho-de-contexto{display:none}`, da `076`. As telas que a feature toca ganharam
a trilha no cabeçalho em PRs ainda abertos — 298 (`081`), 300 (`084`), 302 (`086`), 304 (`085`) —, e
a implementação começa com eles na `main`, por `git merge origin/main` (ver *Dependências* da spec).
O fuso de exibição é o `TIME_ZONE = "America/Sao_Paulo"` das settings, com `USE_TZ`; o filtro `date`
do template já converte. O recorte do ato é `AtoDeOrdenacao.lista_id` (`NULL` = ampla
concorrência), e o endereço de uma tela num recorte é o que `_navegacao_do_recorte` calcula como
`url_do_recorte` desde a `034`. Não há entidade nem contrato externo: `data-model.md` e `contracts/`
não se aplicam; as decisões e as alternativas descartadas estão na própria spec, e não há
`research.md`.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição muda. O link da trilha do Ato leva a uma tela que
  já tem porta própria, e quem não a alcança continua recusado lá; a regra de impressão não mostra
  nada que a tela não mostre.
- **Imutabilidade (II)**: nenhum ato, nenhuma tabela append-only; o Ato é só lido.
- **Linguagem ubíqua (I)**: o rótulo do aviso passa a ser o título da própria tela; "Classificação"
  continua "Classificação".
- **Rastreabilidade (V)**: requisitos e decisões em `spec.md`, matriz em `rastreabilidade.md`,
  cobrada por `tests/test_citacoes_de_requisito.py`. As FRs e os casos-limite que esta feature
  substitui são anotados nas specs de origem quando elas estiverem na `main`.
- **Simplicidade (V)**: uma regra de folha, três trechos de template e uma variável de contexto.
- **Completude de jornada (VI)**: a impressão é conferida em quatro telas por emulação de mídia de
  impressão e por impressão para PDF; o inventário inteiro é refeito nos dois estados da barra.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/base.html` | no `@media print`, a regra deixa de esconder `.cabecalho-de-contexto`; passa a esconder `.cabecalho-de-contexto>a`, e o cabeçalho sai em bloco, sem altura mínima, sem moldura e com a trilha quebrando a linha. Comentário de Django explica a troca e cita a decisão; sem `}}` numa linha (D-001, D-005) |
| `interface/views.py` (`ato_de_ordenacao`) | entrega `url_da_classificacao`, o `url_do_recorte` de `_navegacao_do_recorte(edital, marco_id, rota="interface:ordenacao", atual=ato.lista_id)`; nenhuma consulta nova além da que a função faz, e nenhuma mudança de porta (D-004, D-006) |
| `ato_ordenacao.html` | o link "Classificação" da trilha usa `url_da_classificacao` |
| `aviso.html`, `aviso_interromper.html`, `aviso_previa.html` | o rótulo do aviso na trilha leva `às {{ …|date:"H:i" }}`, como o título (D-003) |
| `tests/interface/test_decisoes_da_etapa_4.py` | testes novos (ver *Testes*) |
| `tests/interface/test_telas_dos_avisos.py` (da `086`) | as duas asserções que prendem *Aviso de DD/MM/AAAA* passam a esperar a hora — a `FR-1941` da `086` foi substituída pela `FR-2010` e pela `FR-2011` |
| `specs/076-*`, `077-*`, `081-*`, `084-*`, `086-*` (spec) | anotação de substituição junto do caso-limite, da FR ou da decisão superada, apontando para a `088` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-088/` | o inventário de antes e o de depois nos dois estados da barra, e a conferência de impressão das quatro telas |

**Por que a variável na view, e não `?lista=` no template.** A docstring de `_navegacao_do_recorte`
diz por que nenhum template monta `?lista=` à mão: é o mesmo endereço que "Cancelar e voltar" usa, e
derivá-lo de dois jeitos é o que deixa um deles divergir em silêncio (`FR-2021`).

**Por que o `@media print` não reescreve a trilha.** A trilha já é `nav.caminho-da-secao` em todas
as telas; ela herda a cor e o tamanho da tela, que são legíveis no papel. A regra só desfaz o que a
`076` fez — tirar o cabeçalho — e tira o que no papel é ação.

## Testes

Novos, em `tests/interface/test_decisoes_da_etapa_4.py`:

- a regra de impressão, lida da folha como texto: dentro do `@media print`, `.barra-lateral` e
  `.cabecalho-de-contexto>a` saem; `.cabecalho-de-contexto` não sai (`FR-2000`, `FR-2001`,
  `FR-2002`);
- nas quatro telas da `SC-780` — a inscrição da Mesa, um Ato, uma Inscrição recebida e um Recurso —,
  a trilha inteira está dentro do cabeçalho de contexto, e "Trocar identidade" é o único link fora
  da trilha nele (o que a regra esconde é exatamente esse link);
- nas três telas dos avisos, o rótulo com a hora de America/Sao_Paulo, num aviso confirmado às 22:30
  de Brasília (01:30 UTC do dia seguinte), e dois avisos do mesmo dia com rótulos diferentes
  (`FR-2010`, `FR-2011`, `SC-782`);
- no Ato de uma lista PPI, o link "Classificação" leva a `?lista=<PPI>`, e seguir o link abre a
  Classificação com a PPI como recorte atual; no Ato da ampla concorrência, o link é o de antes
  (`FR-2020`, `FR-2022`, `SC-783`).

A `FR-2005` é provada pelos testes da `077` que já fixam a trilha da lista e de Minhas Etapas, sem
mudança.

## Verificação

`make lint check test-pg DB_NAME=ps_088 POSTGRES_USER=$USER`, com `LC_ALL=pt_BR.UTF-8`; o inventário
refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` com
o de antes; a conferência de impressão do [quickstart](quickstart.md).
