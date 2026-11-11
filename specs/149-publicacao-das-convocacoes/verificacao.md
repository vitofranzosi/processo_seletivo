# Verificação: A publicação das convocações no GPS (149)

Feita em 11/11/2026, sobre a `main` em `d3e98a89`.

## Suíte

`make test-pg` (PostgreSQL, 4 workers, com os grupos `dev` e `assistente`, sem o `navegador`):
**18 296 passando, 22 pulados e 2 falhas**, em 2108 s. As duas eram guardiões que a feature precisava
satisfazer, e foram corrigidas depois:

- `test_readme_acompanha_o_codigo.py::test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos` —
  faltava a linha da `149` na tabela de incrementos do README;
- `unit/convocacao/test_append_only.py::test_nao_existe_entidade_de_vaga` — o conjunto literal dos
  modelos do app não tinha os três novos (nenhum deles é vaga).

Os dois arquivos, mais o das citações, foram rodados de novo contra PostgreSQL: 27 passando. A suíte
inteira não foi rodada de novo depois disso — as correções só tocam o README e um teste.
Os 25 testes novos (`integration/convocacao/test_publicacao_de_convocados.py`, 16, e
`interface/test_publicacao_de_convocados.py`, 9) passam; `ruff check`, `ruff format --check`,
`manage.py check` e `makemigrations --check` estão limpos.

**Depois do merge da `main` com a `148` da publicação das inscrições (#469)** e da renumeração desta
para `149`: `make test-pg`, mesmas condições — **18 450 passando e 23 pulados, sem falha**, em 1011 s.

## Navegador real

Num banco de demonstração montado por [`demonstracao/montar.py`](demonstracao/montar.py) — o mesmo
cenário dos testes —, servido pelo `runserver` de desenvolvimento e aberto no navegador embutido do
app. As capturas estão em [`capturas/`](capturas/).

| Captura | O que mostra |
|---|---|
| `01-selecao-1280` | A seção *Convocações* na página da seleção: duas publicações lado a lado, a orientação dita uma vez |
| `02-1a-publicacao-1280` | A 1ª publicação: o aviso de correção posterior no topo e na linha, os dois grupos (ampla e PPI), a orientação na coluna ao lado |
| `03-2a-publicacao-correcao-1280` | A 2ª: a linha marcada *"Corrige a convocação divulgada na 1ª publicação"*, sem o motivo |
| `04-1a-publicacao-1920` | A mesma página em tela ampla, na moldura centralizada do portal |
| `05-1a-publicacao-375`, `06-selecao-375` | Celular: uma coluna, a orientação antes da relação |
| `07-gestao-previa-1280`, `08-gestao-confirmacao-1280` | A gestão: publicações feitas, escolha das vagas e listas, o efeito em destaque, o que será público e o formulário |
| `09-gestao-publicada-1280` | Depois da confirmação, **feita por cliques** (autoridade escolhida, declaração digitada, botão): a mensagem nomeia a 3ª publicação e leva à página e ao documento |
| `10-recorte-cartao-e-aviso-1280` | A tela do recorte: cada cartão diz *"Na página pública"*, e o aviso aos convocados da `066` já agrupa as três publicações nativas |
| `11-gestao-375` | A gestão no celular |
| `12-area-do-candidato-1280` | A convocação na área da candidata, entrada pelo código de acesso: *"Publicada em"* leva à 3ª publicação |
| `13-documento-1a-publicacao-1` | O PDF da 1ª, desenhado pelo `pdftoppm`: o mesmo número, data, prazos e resumo SHA-256 da página |

**Rolagem horizontal** (`document.documentElement.scrollWidth` contra `innerWidth`): nenhuma, a
375, 1280 e 1920 px na página da publicação; a 375 e 1280 px na seção da seleção e na gestão.

**O que o navegador mostrou e os testes não**: os cartões da seção ficavam numa coluna de 68ch e
deixavam metade da tela vazia a 1280 px — passaram a uma grade que se adapta (um por linha no
celular, dois ou três lado a lado); e a página da publicação ganhou a coluna lateral para a
orientação em tela larga. Também uma concordância (*"o prazo de cada uma"* com uma pessoa só).

## Não verificado

- O provisionamento de papéis num banco novo (`make preparar`) não foi rodado nesta worktree, para
  não mexer nos papéis do cluster com suítes de outras sessões em curso. A contagem (58) e o
  privilégio estão cobertos por `seguranca/test_homologacao_preservada.py` e
  `test_database_permissions.py`, que é parametrizado por `TABELAS_APPEND_ONLY`.
- A divulgação informativa (efeito *divulga*) não tem captura de tela: o cenário de demonstração usa
  uma forma só. Os testes `ato::test_a_mensagem_enviada…` e `ato::test_a_publicacao_externa…` a
  cobrem.
