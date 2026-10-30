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
