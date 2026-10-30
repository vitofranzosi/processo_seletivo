# Verificação: Ações disponíveis

Medido em 30/10/2026, na branch `claude/acoes-disponiveis-104` (sobre a `103`, PR #339, e a `main`
em `0061f28e`).

## Suíte completa (SC-988)

`cd backend && make lint check test-pg`, PostgreSQL local, grupo `assistente` instalado, 4 workers
(`--dist worksteal`), commit `dfeaa0f1`:

| Passo | Resultado |
|---|---|
| `ruff check .` / `ruff format --check .` | limpos |
| `manage.py check` | no issues |
| `makemigrations --check --dry-run` | No changes detected (FR-2829) |
| `pytest` | **13538 passed, 12 skipped**, 0 falhas, 540s |

**A primeira rodada (commit `e958b11f`) teve 1 falha, e ela era real**:
`test_correcoes_de_norma_na_publicacao.py::test_a_tela_da_retificacao_mostra_o_aviso_e_diz_que_ele_nao_impede`.
A confirmação recolhia o aviso de prazos de recurso — que já valia no Edital vigente — como nota, e
a FR-1309 da `067` exige que ele apareça como aviso na Retificação. A correção mantém a severidade
dentro do bloco recolhido (D-008); o teste não foi alterado. A rodada seguinte é a da tabela.

Os 12 pulados são os 12 deliberados do `CLAUDE.md`. Em relação à `103` (13483 passados em
`e8da7fc5`), a diferença de passados são os testes novos da `103` e desta feature.

## Testes desta feature

| Arquivo | Casos | Resultado |
|---|---|---|
| `tests/interface/test_acoes_disponiveis.py` (cenários A, B, C, D, E, F, G, I, recursos, avaliação, Edital em revisão) | 18 | passam |
| `tests/unit/interface/test_trabalho_do_ator.py` | 12 | passam |
| `tests/performance/test_trabalho_em_escala.py` | 3 | passam |
| testes da `103` ajustados ao texto novo (`test_jornada_da_retificacao.py`, jornada A) | 1 | passa; as asserções passaram a ler o ato na faixa e a situação na marca |

## Escala (SC-984, SC-985)

Editais publicados direto no banco (`publicar_direto`), ator com homologador, publicador, gestor e
julgador:

| Editais | Derivação (`trabalho.do_ator`) | Lista inteira, antes (`df2b1dcc`, a `103`) | Lista inteira, depois |
|---|---|---|---|
| 0 | 1 | 3 | 4 |
| 3 | 3 | 11 | 8 |
| 30 | 3 | 65 | 8 |
| 300 | 3 | 605 | 8 |

A Lista pagava duas consultas por Edital publicado (inscrições e recursos); agora as contagens são
lidas para a página inteira. Quem tem `matricula:exportar` continua pagando a leitura do conteúdo
por Edital (`_pede_requerimento_de_matricula`), fora do escopo e registrado no plano.

## No navegador (cenário H, SC-981, SC-989)

Servidor sobre o banco do diagnóstico (`ps_ux_103`): Retificação em revisão (26/2026), homologada
(01/2026), devolvida (51/2026), Edital 76/2027 em elaboração com pendência. As capturas estão em
[`capturas/`](capturas/) — `antes/` vem do diagnóstico, `depois/` desta branch.

| Papel | Antes | Depois |
|---|---|---|
| Homologador | "Nenhuma ação disponível" ao lado de "Retificação em revisão · Homologar"; detalhe do Edital negando ato | faixa com "Analisar a Retificação", desde 30/10; coluna com o botão; marca só com a situação; detalhe com "Uma Retificação deste Edital aguarda você" |
| Elaboradora | devolvida igual a rascunho; "Submeter para revisão" habilitado na Lista | faixa com "Corrigir a Retificação devolvida" e o motivo, e "Continuar a elaboração"; "Conferir e submeter" na coluna |
| Publicadora | "Nenhuma ação" ao lado de "Retificação homologada · Publicar Retificação" | faixa com "Publicar a Retificação" |
| Gestor | — | "Nenhuma ação disponível para você agora.", discreto; inventário igual |
| Confirmação de homologar | sem a tabela; dois avisos do Edital inteiro em destaque | "O que esta Retificação altera (1)"; os dois avisos em "Avisos que já valiam no Edital vigente (2)" |

**375 px**: a faixa ocupa de 417 a 702 px, dentro da primeira tela de 812; `scrollWidth` igual a
375. **Teclado**: o primeiro elemento focável do conteúdo é o título do item da faixa; os itens são
links nativos e o "Mostrar os outros" é um `summary` nativo. **Contraste**: o verde do ato dá
5,02:1 sobre branco, o cinza da situação 7,46:1. **Cor**: a faixa se distingue pelo título, pelo
número e pelos verbos, e o filete verde é reforço. **Leitor de tela**: não usado; a estrutura é
`section` com `h2`, `ul` e `li`.

A faixa tem dois parciais: `_acoes_disponiveis.html` (a seção) e `_item_de_trabalho.html` (um item,
usado pelos cinco primeiros e pelo "Mostrar os outros"). O segundo não estava na estrutura do plano;
a convergência o registrou aqui (T023).

## Validação com pessoas (SC-990)

**Não executada.** O roteiro está em [quickstart.md](quickstart.md). Nenhum resultado foi simulado.

## Convergência

Rodada depois da implementação: dois achados, um `partial` (o Edital em revisão sem teste próprio,
T022) e um `unrequested` (o parcial do item, T023), os dois resolvidos. Os itens de
`checklists/operacao.md` são de quem revisa e seguem sem marca.

## Revisão de prontidão (30/10/2026, depois da avaliação independente)

### Achados

| Achado da avaliação | Situação | O que foi feito |
|---|---|---|
| O ato parece clicável e não é | **confirmado** (só o título era link) | o item inteiro é um link só; nome acessível "ato: objeto"; contexto como descrição (D-011) |
| "Ações disponíveis" sem dizer o que cobre, sobretudo vazia | **confirmado** | o estado vazio nomeia o que a faixa cobre e o que fica no detalhe (D-012) |
| "Publicar o Edital" antes da conferência | **confirmado** | "Conferir e publicar o Edital", o verbo da coluna (D-004) |
| Limite de cinco não validado com muitos itens | **confirmado como lacuna de evidência** | medido com 1, 5, 25 e 100; o limite ficou; a densidade do item mudou (D-014) |
| "Corrigir" × "submeter" na devolvida | **confirmado** | a passagem de bastão da devolvida diz "corrigir … e submetê-la de novo" (D-013) |
| Contagens injetadas em `do_edital` | **descartado** | três chamadores: a Lista (passa as contagens), o detalhe e `proximo_passo` (um Edital só cada) |
| Teste da 103 adaptado | **confirmado em parte** | para quem publica, a asserção tinha perdido a situação na marca; restaurada |
| Validação com pessoas | **pendente** | roteiro pronto em `quickstart.md`; não executado |

### A faixa com muitos objetos

Banco do estudo (`ps_ux_103`) com Editais em elaboração sintéticos para a elaboradora; ambiente de
demonstração, com a faixa amarela de aviso (~200 px) acima da faixa, que em produção não existe.

| Objetos | Largura | Faixa fechada | Faixa aberta | Início do inventário | Tela |
|---|---|---|---|---|---|
| 1 | 375 | 257 px | — | 876 px | 812 |
| 5, antes da densidade | 1280 | 540 px | — | 955 px | 860 |
| 5 | 1280 | 406 px | — | 821 px | 860 |
| 5, antes da densidade | 375 | 771 px | — | 1389 px | 812 |
| 5 | 375 | 592 px | — | 1211 px | 812 |
| 25 | 1280 | 432 px | 1611 px | 848 px | 860 |
| 100 | 1280 | 432 px | 6036 px | 848 px | 860 |
| 100 | 375 | 618 px | 8577 px | 1237 px | 812 |

- **Consultas** da Lista inteira para a elaboradora: 6 com 1, 5, 25 e 100 objetos
  (`test_a_faixa_com_1_5_25_e_100_objetos_mostra_cinco_e_nao_cresce_em_consultas`).
- **Peso**: com 100 objetos, a faixa tem 52 KB dos 148 KB da página (o resto é o inventário de 102
  Editais); o servidor respondeu em 29 ms e o DOM ficou pronto em 8 ms, em localhost.
- **Teclado**: com "Mostrar os outros" fechado, a faixa tem 6 paradas (5 itens e o `summary`),
  qualquer que seja o total; os itens escondidos não recebem foco.
- **Leitura**: o limite de cinco segura a faixa fechada em altura constante; aberta, com 100, ela é
  longa — é o caso em que uma apresentação própria faria sentido, e ele não é plausível para a equipe
  de duas ou três pessoas do Cefor hoje. Registrado, não implementado.

### Suíte depois da revisão

`make lint check test-pg`, commit `3b178107`: lint, `check` e `makemigrations --check` limpos;
**13541 passed, 12 skipped**, 0 falhas, 592s. Os 3 casos a mais em relação a `dfeaa0f1` são os
testes de afordância, do verbo da devolvida e da faixa com 1, 5, 25 e 100 objetos.

### Depois do merge do #339

Este PR aponta para a branch da `103`. Depois que o #339 entrar na `main`: reapontar o #340 para a
`main`, sincronizar com ela, e rodar de novo `make lint check test-pg` sobre o resultado, conferindo
`test_auditoria_passagem_da_retificacao.py`, `test_jornada_da_retificacao.py` e
`test_acoes_disponiveis.py`, que atravessam as duas specs.
