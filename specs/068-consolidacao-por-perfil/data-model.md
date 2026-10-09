# Data Model: O que se repete por Perfil sai uma vez no Edital em PDF

**Nenhuma entidade persistida muda.** Nenhum modelo, migration, campo do snapshot ou do conteúdo
publicado. O que existe de novo é transitório, vive dentro de uma composição e não sai dela.

## Plano de consolidação (transitório)

Calculado do snapshot grafado, só com dois ou mais Perfis (R-001).

| Parte | O que é |
|---|---|
| grupos de atribuições | os da `064`, inalterados |
| grupos de requisitos | Perfis de bloco de requisitos idêntico (R-002), dois ou mais, lista não vazia |
| grupos de marcos | Perfis de bloco de marcos idêntico (R-002), dois ou mais, com marco |
| grupos de modalidades | Perfis de tabela de modalidades idêntica, **inclusive grupos de um** (cada Perfil com modalidade tem a sua tabela) |
| subseções comuns | número `N.k` e grupo, na ordem: atribuições, requisitos, marcos (FR-1359) |
| remissão por Perfil | para cada Perfil e matéria, o número da subseção a que remete, ou nenhum |
| listas | a ordem única de R-005 |
| tabela de vagas | forma (matriz, longa ou nenhuma), colunas e linhas |
| frases | por espécie de reversão e por forma de convocação: o texto e os códigos do prefixo, ou nenhum |
| método comum | o item em que as linhas saem, ou nenhum |

**Invariantes** (cobradas por teste):

- cada Perfil tem, por matéria, exatamente uma fonte: o próprio bloco ou uma subseção comum;
- toda subseção comum é objeto de remissão de todos os Perfis que nomeia, e de nenhum outro;
- os números `N.1 … N.n` dos Perfis e os das subseções de atribuições não dependem dos grupos de
  requisitos e de marcos;
- `itens_do_documento` e `tabelas_do_documento` são funções do plano, e coincidem com o que a
  composição escreve (guardião da `065`).
