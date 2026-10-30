# Contrato das telas: Ações disponíveis

Nenhuma rota nova. Nenhuma rota de API nova.

## `GET /gestao/` — Lista

Ordem dos blocos: título, subtítulo, aviso de demonstração (quando ligado), **faixa ou linha de
ausência**, "Novo Processo Seletivo", contadores, inventário.

**Faixa** (`section` com `aria-labelledby="acoes-disponiveis-titulo"`, classe
`acoes-disponiveis`), só com ao menos um objeto:

- título "Ações disponíveis para você" e o total ("2 procedimentos");
- `ul.itens-de-trabalho` com até cinco `li`, cada um: link com o título, a situação, o detalhe,
  "desde dd/mm/aaaa" quando houver, e o ato;
- `details` "Mostrar as outras N" com o restante;
- nota de cobertura: "Inclui atos de Edital e de Retificação, recursos e avaliações. Classificação,
  divulgação de resultado e avisos continuam no detalhe de cada Edital."

**Sem objeto**: `p.sem-acoes` "Nenhuma ação disponível para você agora." — sem número.

**Coluna "O que posso fazer"**: as ações do Edital (com "Conferir e submeter"/"Conferir e publicar" no
lugar dos atos que dependem da validação; "Publicar" desabilitado com motivo quando a segregação o
recusa) e, por Retificação em curso com ato da pessoa, um link com o rótulo do ato.
"Nenhuma ação disponível para seus papéis" só quando as duas listas estão vazias.

**Marca da Retificação**: "Retificação em revisão", "Retificação devolvida", "Retificação reenviada"
etc.; quando o ato não é da pessoa, "· aguarda <papel>".

## `GET /gestao/editais/<id>/` — detalhe

"O que fazer agora", sem ato do Edital para a pessoa:

- com Retificação em curso cujo ato é dela: "Uma Retificação deste Edital aguarda você: <ato>" e o
  link;
- com Retificação em curso sem ato dela: "A Retificação de <data> (<situação>) aguarda <papel>.";
- sem Retificação em curso: "Nenhum ato disponível para seus papéis nesta situação." (inalterado).

## `GET /gestao/retificacoes/<id>/atos/homologar` e `/devolver`

- tabela "O que esta Retificação altera" (Onde, Antes, Depois);
- advertências novas primeiro; as que já valiam em `details` "Avisos que já valiam no Edital vigente
  (N)".

## `GET /gestao/minhas-etapas`

Sem alocação: "Você não possui Etapas atribuídas no momento. Esta área é da avaliação nas
comissões; atos de Edital e de Retificação aparecem em Processos Seletivos", com o link. O começo da
frase é o de antes, que três testes de autorização usam para provar a ausência de alocação.
