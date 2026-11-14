# Contrato — as recusas da publicação e do envio

## Publicação e Retificação (impeditivas)

| Código | Quando | Frase |
|---|---|---|
| `video_sem_protocolo` | `videoOption` com a chave desligada | "A Etapa «X» admite o vídeo, mas o vídeo depende de protocolo institucional que ainda não existe." |
| `video_fora_da_colegiada` | `videoOption` em Etapa que não é decisória colegiada | "A Etapa «X» admite o vídeo, mas só a Etapa decisória com regra de deliberação pode admiti-lo: o vídeo só confirma, e quem confirma é a deliberação." |
| `video_sem_alcance` | `videoOption` sem alcance | "A Etapa «X» admite o vídeo, mas não declara as Modalidades que alcança." |
| `video_sem_periodo` | `videoOption` sem Evento com início e fim | "A Etapa «X» admite o vídeo, mas o período dela não tem início e fim." |
| `video_ja_recebido` | Retificação retira `videoOption` depois do primeiro vídeo | "A Etapa «X» já recebeu vídeo, e deixar de admiti-lo agora tiraria o meio de quem o usou." |

## Envio (portal)

| Código | Status | Quando |
|---|---|---|
| `indisponivel` | 409 | fora do período, com parecer concluído, Resultado, encaminhamento, ou troca depois da abertura |
| `ja_aberto` | 409 | troca depois da primeira abertura da comissão |
| `maioridade` | 422 | sem a declaração de maioridade |
| `tamanho` | 422 | tamanho acima do teto, ou o recebido diferente do declarado |
| `formato` | 422 | tipo não aceito, ou assinatura do contêiner não reconhecida |
| `duracao` | 422 | acima do teto, medida ou no contêiner |
| `marcas` | 422 | marcas fora de ordem ou fora da duração |
| `resumo` | 422 | o resumo do aparelho difere do calculado |
| `deslocamento` | 409 | parte fora do deslocamento recebido |

## Mesa e consolidação

| Código | Status | Quando |
|---|---|---|
| `video_nao_aberto` | 409 | concluir em modo vídeo sem ter aberto o vídeo |
| `parecer_obrigatorio` | 422 | "Não dá para confirmar pelo vídeo" sem motivo (a regra da `012` para o desfavorável) |
| `desfavoravel_pelo_video` | 409 | gravar Resultado desfavorável sobre inscrição em modo vídeo |
| `encaminhamento_duplicado` | 409 | encaminhar de novo |
| `nao_encaminhavel` | 409 | encaminhar inscrição que não está em modo vídeo com deliberação não favorável |
