# Pesquisa — 082

As decisões de governança estão na spec (D-001 e D-002). Aqui ficam as questões de desenho e de teste,
e os achados.

## R-001 — A trilha da conferência

**Decisão**: `consolidacao_confirmar.html` sobrescreve o bloco `caminho_do_contexto` com a mesma
`nav aria-label="Trilha de navegação" class="caminho-da-secao"`, o produto pelo parcial
`_produto_na_trilha.html` e os níveis da Distribuição, e tira a `nav.trilha` do `main`:

| | Trilha |
|---|---|
| Antes, no conteúdo | Processos Seletivos › Prova objetiva › Conferir |
| Agora, no cabeçalho | GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por Etapa › Prova objetiva › Conferir |

**Por quê**: é a linha da conferência da retirada na tabela do R-001 da `080`, com outro ato. A tela
mora sob `/gestao/editais/`, e a seção dela, pelo endereço, já é Processos Seletivos: a barra e o
começo da trilha concordam sem declaração nenhuma da view.

**Medido em 17/10/2026**, varrendo os templates com `nav.trilha` no conteúdo e link para a
Distribuição: sobraram a conferência da consolidação e a Auditoria do Edital (que é tela do Edital, a
decisão 002 da `080`). Esta é a última das que se abrem da Distribuição.

**Alternativas**:
- *Extrair a trilha da Distribuição num parcial*, usado pela Distribuição e pelas sete telas — é a
  extração que a `081` discutiu e preferiu não fazer, com um guardião da grafia no lugar; fazê-la aqui
  tocaria oito templates para mudar um.
- *Manter os níveis que a tela tinha* — levaria ao cabeçalho a trilha que pulava o Processo e a
  Alocação, o que a decisão 001 da `080` descartou para as filhas.

## R-002 — Um cenário de teste próprio, com inscrições prontas

**Decisão**: o módulo novo monta o cenário com `montar_etapa_de_leitura_unica` e `semear_prontas`
(`tests/fixtures/resultado.py`), com seed e código próprios (8200), em vez de importar o `cenario` do
módulo da `012`, que os testes da `080` usam.

**Por quê**: o `cenario` da `012` não tem inscrição pronta, e a conferência dele não mostra o botão
que consolida — que é justamente o que a `FR-1844` exige que fique igual. E o PR 298 (`081`) tira a
importação desse `cenario` dos módulos de teste e põe um guardião contra ela: um módulo novo que o
importasse reprovaria assim que os dois PRs estivessem na `main`.

## R-003 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_prontidao_na_tela.py::test_a_conferencia_declara_o_que_fica_de_fora` | continua igual — o título e o que fica de fora |
| `test_consolidar_todas_as_prontas.py` | continua igual — o conjunto declarado e a confirmação |
| `test_telas_da_presidencia.py::test_nenhuma_acao_da_distribuicao_sai_do_lugar` | continua igual — a Distribuição não muda |
| `test_telas_de_quem_elabora.py::test_o_produto_da_trilha_tem_uma_fonte_so` | continua igual — a tela inclui o parcial |
| `test_acessibilidade.py`, `test_larguras.py`, `test_estaticos.py` | continuam iguais — `caminho-da-secao` já tem regra na folha, e a `.trilha` continua usada por outras telas |
| o guardião da abertura da trilha que o PR 298 traz | rodado à parte sobre esta worktree: 18 templates sobrescrevem a trilha, e nenhum fica fora da abertura |

## Achados registrados, fora do escopo

- **O banco de demonstração não tem inscrição pronta.** No `ps_inventario_081`, nenhuma das
  Distribuições oferece "Consolidar as N prontas", e a conferência das selecionadas só tem o que fica
  de fora — as do Edital 51/2026 já têm Resultado. O percurso no navegador cobre o caso "nada a
  consolidar"; a tabela do alcance e o botão que consolida são provados pelos testes.
