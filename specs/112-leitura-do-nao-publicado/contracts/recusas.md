# Contrato: as recusas

A regra (`D-002`) devolve um de três alcances; a porta (`D-003`) traduz cada um, nesta ordem, antes
de qualquer conferência de estado (FR-3515, EC-4).

| Alcance do ator sobre o ato | A rota pede existência | A rota pede conteúdo |
|---|---|---|
| `NENHUM` | **404** — página "não encontrado" da gestão, idêntica à do inexistente e à de outra unidade (FR-3517, FR-3520) | **404**, idem |
| `EXISTENCIA` | a tela, reduzida onde a spec manda (FR-3509) | **403**, recusa explicada pelo ponto único (FR-3518) |
| `CONTEUDO` | a tela inteira | a tela inteira |

## A recusa explicada

Produzida por `require_authorization_base(False, bases=[base_de_permissao("ler o Edital antes da
publicação")])`. A frase segue a formulação canônica da FR-486 da `033`, que
`tests/test_gramatica_das_portas.py::test_toda_tela_que_manda_pedir_usa_a_formulacao_canonica`
confere. Na Retificação, o nome da base é "ler a Retificação antes da publicação".

Ela **não** repete número, título nem situação do ato: quem a recebe já os conhece pela tela de
onde veio, e a página de recusa é a mesma para todos os atos.

## O 404 e o inventário da `033`

Cada função nova ou alterada que levanta `Http404` por alcance `NENHUM` ganha linha em
`specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, classe **recusa de autorização —
existência de ato não publicado**, com a justificativa da `D-004`. A linha de `anexo_do_rascunho`
muda de "conjunto de três capacidades" para "regra da `112`".

## Respostas htmx

Os fragmentos (classe C) respondem 404 sem corpo a `NENHUM`, como hoje respondem a Edital
inexistente; a `EXISTENCIA` respondem 200 com `HX-Retarget` para a área de recusa, como as demais
recusas de fragmento (a lição "htmx não troca 4xx" do repositório).
