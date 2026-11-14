# Contrato: recusas e achados

O vocabulário é o do documento: "Etapa", "Modalidade", "alcance", "inscrição". Os nomes entre
chevrons são do conteúdo.

## Gravação do rascunho (`validate_stage`, FR-6962)

| Caso | Campo | Mensagem |
|---|---|---|
| lista vazia | `modalityCodes` | A Etapa «nome» está marcada para alcançar só algumas Modalidades, mas nenhuma foi escolhida. Marque ao menos uma, ou escolha "Todas as inscrições". |
| código repetido | `modalityCodes` | O alcance da Etapa «nome» repete a Modalidade «código». |
| item que não é texto, ou vazio | `modalityCodes` | O alcance da Etapa «nome» tem um código de Modalidade inválido. |

## Aviso do rascunho (FR-6963)

`alcance_codigo_inexistente` (aviso): A Etapa «nome» alcança a Modalidade «código», que nenhum Perfil
deste Edital tem mais. Escolha outra Modalidade, ou o Edital não poderá ser publicado.

## Publicação e Retificação (`BLOCKING_ERROR`)

| Código | Requisito | Mensagem |
|---|---|---|
| `alcance_codigo_inexistente` | FR-6963 | A Etapa «nome» alcança a Modalidade «código», que nenhum Perfil deste Edital tem. |
| `alcance_em_papel_de_todos` | FR-6964 | A Etapa «nome» alcança só algumas Modalidades e não pode «papel»: o que ela decide valeria para quem ela não avalia. |
| `alcance_denominacao_divergente` | FR-6965 | A Modalidade «código», que a Etapa «nome» alcança, tem denominações diferentes nos Perfis «lista». Use a mesma denominação em todos. |

«papel», um por caso: *ser classificatória*; *ter peso*; *ser a Etapa comparada pelo critério de
desempate do marco «marco»*; *ser pontuada e medida pelo marco «marco»*; *ser a Etapa que o corte do
marco «marco» governa*; *ser a Etapa de habilitação ao sorteio do marco «marco»*.

## Retificação que estreita (FR-6980)

`stage_scope_narrowed_over_assigned`, 422:

> A Retificação tiraria do alcance da Etapa «nome» a(s) Modalidade(s) «códigos», e «N» inscrição(ões)
> dessas Modalidades já têm Atribuição ou Resultado nessa Etapa. Remova antes as Atribuições abertas,
> pela distribuição; inscrição com avaliação concluída ou Resultado não sai do alcance.

## Operação

| Onde | Código | Mensagem |
|---|---|---|
| distribuição, atribuição individual (FR-6973) | `inscricao_fora_da_etapa` (o de hoje) | motivo: *"a Modalidade da inscrição está fora do alcance da Etapa «nome»"* |
| Ocorrência, conclusão (FR-6975) | o código de hoje para não participante | o mesmo motivo |
| publicação das inscrições (FR-6987) | `inscricoes_etapa_invalida` | A Etapa «nome» alcança só algumas Modalidades e não decide o deferimento de todas as inscrições. |
