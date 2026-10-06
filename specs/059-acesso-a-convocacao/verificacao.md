# Verificação: 059

**Feature**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md)

## Estado de partida (T002), medido em 06/10/2026 sobre a `main` 4602b04

**Custo da lista.** Em `tests/performance/test_area_do_candidato.py`, "Minhas inscrições" custa **9**
consultas com uma e com duas inscrições em rascunho. O teto do teste é 12.

**O clique em "Acompanhar" não chegava ao acompanhamento (`D-010`, confirmado).** No banco
`ps_demo_059` semeado, entrando como a convocada da demonstração (Ana Silva, Edital 51/2026), a
lista mostrava só "✓ Inscrição enviada" e "Acompanhar" — nada da convocação. E no centro do botão:

```js
document.elementFromPoint(centro de "Acompanhar")
// → A.titulo  /selecoes/inscricoes/<id>/       (o título esticado: "Sua inscrição")
// e não       /selecoes/inscricoes/<id>/acompanhamento
```

O `::after` do título cobre o cartão inteiro e é posicionado; a ação principal não é. Com o mouse,
"Acompanhar" levava a "Sua inscrição". Teclado e leitor de tela não eram afetados — o link existe e
recebe foco. Corrigido pela mesma regra que põe "Ver convocação" acima do título (T011).

## Depois (T024, T025), medido em 06/10/2026

### A suíte

`cd backend && make lint check test-pg DB_NAME=test_ps_059`:

| Passo | Resultado |
|---|---|
| `ruff check` | All checks passed |
| `ruff format --check` | 1267 files already formatted |
| `manage.py check` | no issues |
| `makemigrations --check` | No changes detected — o aviso de conexão que o precede é do `DB_NAME` próprio, que nomeia o banco de **teste** e não existe como banco de desenvolvimento |
| `test-pg` | **9193 passando, 1 falha, 11 pulados** (862 s); a falha corrigida logo depois — ver abaixo |

A falha era `test_readme_acompanha_o_codigo.py`: a pasta da `059` não estava na tabela de
incrementos do README. Corrigida no mesmo arco, e o guardião rodado de novo, isolado — verde. O
total esperado de uma rodada inteira é, portanto, **9194 passando e 11 pulados**; a rodada inteira
depois da correção não foi repetida, porque a correção é uma linha de README e nenhum código mudou. Os **11 pulados** são os mesmos onze do `CLAUDE.md` — nenhum teste desta
feature pula.

Os testes desta feature: 5 do seletor, 23 de tela, 2 de orçamento da lista, 13 de autorização, 3 da
varredura da `019` — **46**. Os testes vizinhos que a feature podia quebrar, sem edição:
`test_portal_convocacao.py` (16), `test_orcamento_de_consulta.py` (o zero da lista e do
acompanhamento), `test_portal_requerimento_convocacao.py`, `test_area_do_candidato.py`.

### No navegador

Banco `ps_demo_059` semeado, servidor da worktree na 8059 (entrada `acesso-059`), entrando como Ana
Silva, a convocada da demonstração:

| Tela | Antes | Depois |
|---|---|---|
| Minhas inscrições | "✓ Inscrição enviada" e "Acompanhar" | mais "➜ Convocação aberta", **Ver convocação** como ação principal e "Acompanhar" como link |
| `elementFromPoint` no centro de "Acompanhar" | `A.titulo` (o título esticado) | o próprio link |
| `elementFromPoint` no centro de "Ver convocação" | — | o próprio link |
| Clique em **Ver convocação** | — | a tela da convocação, com *"Conferir o Requerimento de Matrícula enviado"* (a seed envia o dela) |
| Clique em **Voltar ao acompanhamento** | sem nada de convocação | a seção **Convocação** no topo: espécie, *"ainda não foi enviada… não começou a correr"*, o caminho ao requerimento enviado e **Ver convocação** |
| 375 px — lista, acompanhamento, convocação | — | `scrollWidth` = `clientWidth` = 375 nas três |

**O que o navegador não mostrou, e por quê.** Os estados *"Preencher Requerimento de Matrícula"* e
*convocação concluída* pedem outro ato da gestão sobre a seed (convocar quem ainda não tem
requerimento, registrar desfecho), e a seed convoca uma pessoa só, com o requerimento já enviado. Os
dois estão presos em teste de tela: `TestRequerimentoNaConvocacao` e
`TestMinhasInscricoes::test_a_concluida_vira_nota_e_a_acao_volta_a_ser_acompanhar`,
`TestAcompanhamento::test_a_concluida_continua_consultavel`.

**Trilha (`D-008`)**: provada em `test_so_a_tela_da_convocacao_registra_leitura` — a lista e o
acompanhamento não acrescentam `CONVOCACAO_LER`; a tela da convocação acrescenta uma.
