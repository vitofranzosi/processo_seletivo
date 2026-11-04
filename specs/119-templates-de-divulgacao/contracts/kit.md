# Contrato: o que muda nas rotas do kit

As rotas da `111` continuam, com os mesmos nomes, métodos, cabeçalhos e ordem de recusa (porta,
capacidade, estado, impressão). Muda o que elas aceitam.

## `GET /gestao/editais/<id>/kit-de-divulgacao/`

Aceita na consulta, todos opcionais: `familia`, `variante`, `imagem`, `manchete`. Sem eles, a
pré-escolha da última exportação (FR-3806).

Responde a tela com:

- o formulário de escolha (`GET` para a própria tela; funciona sem script);
- para cada formato da família: a prévia, o texto alternativo e os botões de exportação; ou o motivo
  da indisponibilidade ("em aprovação pela comunicação", recusa da composição);
- as faixas da `111`, mais "o título oficial não coube em: …" e "o contato não coube em: …".

Escolha fora da lista: a tela abre com a pré-escolha e diz que a escolha não está disponível; nada é
gerado.

## `GET /gestao/editais/<id>/kit-de-divulgacao/previa.png`

Acrescenta à consulta: `familia`, `variante`, `imagem`, `formato_da_peca` (D-012). Escolha fora da
lista, template não liberado ou em versão divergente (FR-3835), ou composição recusada: 404,
como hoje. Impressão divergente: 409.

## `POST /gestao/editais/<id>/kit-de-divulgacao/exportar/<formato>`

`<formato>` continua sendo o tipo de arquivo. Para `png` e `svg`, o corpo leva `familia`,
`variante`, `imagem`, `formato_da_peca`, `manchete` e `impressao`.

| Situação | Resposta | Registra |
|---|---|---|
| Escolha fora da lista (EC-9) | 400 com "a escolha não está disponível; abra o kit de novo" | não |
| Template não liberado, ou versão divergente da liberada (EC-7, EC-23) | 409 com o motivo | não |
| Composição recusada | 409 com o motivo da recusa | não |
| Impressão divergente | 409 `kit_desatualizado` | não |
| Sucesso | anexo com o tipo e a CSP da `111` | sim, com o `detalhe` do data-model |

`zip`: para família da comunicação, leva a peça de cada formato liberado e na versão liberada, com os
nomes `peca-<formato>.{png,svg}` e `peca-<formato>-alternativo.txt`; o manifesto e o evento trazem uma
entrada por formato da família, incluído ou não (FR-3828, FR-3829; forma no data-model). Para a
Institucional, o ZIP é o da `111`, sem mudança.

## Configuração de liberação

`KIT_DE_DIVULGACAO_TEMPLATES`: lista separada por vírgula de `familia/formato@versao`, por exemplo
`pos-lato-sensu/post@1,pos-lato-sensu/story@1`. Entrada sem `@versao`, de família ou formato
desconhecido, é recusada na subida das settings, como as outras chaves do kit. Template cuja versão no
código não é a nomeada fica indisponível (FR-3808, FR-3835). Vazia por padrão; em produção, só a
operação a preenche, depois do registro da aprovação (FR-3834). `KIT_DE_DIVULGACAO_PECA` continua
regendo a Institucional.

**Inventário de negativas da `033`.** O guardião `backend/tests/test_gramatica_das_portas.py`
varre `kit_de_divulgacao.py`. Os `Http404` novos da **prévia** — escolha fora da lista, template não
liberado ou em versão divergente, composição recusada — ganham linha no inventário
(`specs/033-navegacao-por-capacidade/inventario-das-negativas.md`) — ou cabem na linha da `previa`
que a `111` já registrou, se continuarem no mesmo `raise` —, classificados como "objeto
inexistente", a classificação daquela linha. Linha do inventário que mudar de número no arquivo é
atualizada no mesmo PR. O **400** da exportação com escolha fora da lista não é
`Http404`: sai por `DomainError`, como as recusas 409 da `111`, e não entra no inventário.
