# Modelo — 057 · Polish das telas de operação

**Não há entidade de domínio nova nem alterada**, nenhuma migration e nenhuma view nova. O que esta
feature trata são elementos da tela; o contrato visual de cada um está em
[contracts/telas.md](contracts/telas.md).

## Elementos

| Elemento | Onde | O que muda |
|---|---|---|
| Grupo de ações do Edital | `detalhe.html`, `acoes.py` | repartido em principal, secundárias e terminais; em linha |
| Coluna de ações da Lista | `lista.html`, `views.lista` | frequentes primeiro, terminais no fim e separadas; zerada esmaecida |
| Gestos do marco | `marco.html` | o primeiro preenchido, os demais secundários, lado a lado |
| Glossário | oito telas de marco e matrículas | dentro de `details.como-preencher`, fechado |
| Sinal de Atenção | `_sinal.html`, folha | lista com divisor e faixa âmbar |
| Evento de auditoria | `auditoria.html`, folha | divisor no lugar do cartão |
| Requisito apresentado | `inscricao_detalhe.html` | linha de `ul.documentos` |
| Ficha curta | `distribuicao.html`, `minha_etapa.html` | largura do conteúdo |
| Matriz de Alocação | `alocacoes.html`, folha | linha de grupo por Edital; `thead` fixo; controles numa faixa |
| Envio de documento | portal, `_documentos.html` | uma linha de controles |

## A repartição das ações

`hierarquia(conjunto)` devolve `(principal, secundarias, terminais)`. Invariantes:

- `[principal] + secundarias + terminais`, sem a principal quando ela é `None`, tem **os mesmos
  elementos** de `conjunto`, sem repetir nem perder nenhum (FR-1064);
- `terminais` são as ações de chave `encerrar` e `cancelar`, na ordem de `conjunto`;
- `principal` é a primeira, na ordem de preferência — `elaborar`; `submeter`, `homologar`,
  `publicar`; `inscricoes` —, que estiver em `conjunto`; se ela estiver indisponível, `principal` é
  ela mesma, desabilitada, e nenhuma outra é promovida (FR-1045);
- `secundarias` preservam a ordem relativa de `conjunto`.

`Acao.quantidade` é `None`, salvo nas duas ações que contam ("Inscrições recebidas" e "Recursos
aguardando decisão"); não entra no destino nem no rótulo.
