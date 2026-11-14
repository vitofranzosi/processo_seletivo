# Contrato — as rotas da verificação por vídeo

Todas respondem **como inexistentes** (a recusa `not_found` do domínio, 404) quando quem pede não é o
titular (portal) ou não tem a Atribuição alocada (gestão), e quando a Etapa não admite o vídeo
(FR-7110, FR-7129). **A chave desligada fecha só as rotas do portal** (FR-7100): a Mesa e o
encaminhamento continuam servindo os vídeos já recebidos, porque o parecer sobre eles é ato do
certame (achado I1 do `/speckit-analyze`).

## Portal — `selecoes/inscricoes/<inscricao>/verificacao/<etapa>/`

| Método e rota | O que faz | Respostas |
|---|---|---|
| `GET ` | a página: escolha, acolhimento, maioridade, câmera, gravação, revisão, envio | 200 HTML com a CSP da página (T-004) e `Permissions-Policy` |
| `POST envios` | inicia; JSON `{tamanho, formato, duracao, marcas, roteiro, maioridade}` | 201 `{envio, deslocamento: 0, parte}`; 409 `{codigo}` quando o vídeo não está disponível; 422 `{codigo, campo}` |
| `GET envios/<envio>` | o deslocamento recebido | 200 `{deslocamento, tamanho}` |
| `PUT envios/<envio>/partes?deslocamento=N` | acrescenta o corpo cru, ≤ 8 MiB | 200 `{deslocamento}`; 409 `{codigo: "deslocamento", deslocamento}`; 413 parte grande demais |
| `POST envios/<envio>/concluir` | JSON `{sha256}`; confere e grava o vídeo | 201 `{video, comprovante}`; 422 `{codigo}` (`tamanho`, `formato`, `duracao`, `resumo`) |
| `GET comprovante` | o comprovante do vídeo vigente | 200 HTML |
| `POST video/abrir` | abertura do titular (um evento) | 303 para `comprovante?abertura=<id>` |
| `GET video/<abertura>` | a entrega com `Range` | 200/206/416; 404 abertura alheia |

As rotas JSON exigem o cabeçalho `X-CSRFToken`, como as demais do portal.

## Gestão — `gestao/minhas-etapas/<edital>/<etapa>/inscricoes/<inscricao>/video/`

| Método e rota | O que faz | Respostas |
|---|---|---|
| `POST abrir` | confere o resumo, grava a `AberturaDoVideo` e um evento | 303 para a Mesa com `?abertura=<id>`; 409 resumo divergente (evento de integridade) |
| `GET <abertura>` | a entrega com `Range` | 200/206/416 |

## Gestão — o encaminhamento

| Método e rota | O que faz | Respostas |
|---|---|---|
| `GET  gestao/editais/<edital>/distribuicao/<etapa>/encaminhar` | a lista das inscrições que o vídeo não confirmou, e o alcance | 200 HTML |
| `POST gestao/editais/<edital>/distribuicao/<etapa>/encaminhar` | encaminha as marcadas, uma transação por inscrição | 303 para a conferência, com o resumo |

Exige a capacidade de consolidar (`resultado:consolidar`) no escopo do Edital.

## Eventos de trilha

| Operação | Agregado | Quando |
|---|---|---|
| `VIDEO_DA_VERIFICACAO_RECEBIDO` | o vídeo | concluir o envio (com `substitui`, quando troca) |
| `VISUALIZAR_VIDEO_DA_VERIFICACAO` | o vídeo | cada abertura (comissão ou titular, no `detalhe`) |
| `VIDEO_DA_VERIFICACAO_INTEGRIDADE` | o vídeo | resumo divergente na abertura |
| `ENCAMINHAR_A_ENTREVISTA_AO_VIVO` | o encaminhamento | o ato da presidência |
| `ELIMINAR_VIDEO_DA_VERIFICACAO` | o vídeo | cada eliminação |

Nenhum evento leva o conteúdo do vídeo nem o resumo do aparelho; o `detalhe` traz tamanho, duração,
formato e o resumo do servidor.

## Comando

```text
manage.py eliminar_videos_da_verificacao --edital <uuid> [--confirmar]
```

Sem `VERIFICACAO_POR_VIDEO_RETENCAO_DIAS`: `CommandError` "o prazo de retenção do vídeo ainda não foi
decidido (P-10)". Sem `--confirmar`: lista o que eliminaria, sem eliminar.
