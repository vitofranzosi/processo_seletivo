# Quickstart — 166 · A verificação da autodeclaração por vídeo

Só em desenvolvimento. **Nenhum vídeo real**: a página oferece a fonte sintética (o `canvas` animado
e o oscilador da prova de conceito) quando `DEBUG` e a chave estão ligados.

## 1. Ambiente

```bash
cd backend
export VERIFICACAO_POR_VIDEO=true
export INTERFACE_SELETOR_IDENTIDADE=true
make preparar
```

A entrada `verificacao-por-video-166` do `.claude/launch.json` sobe o `runserver` com as duas chaves.

## 2. O Edital de desenvolvimento

Num shell, com o helper dos testes (`tests/fixtures/verificacao.py`, `cenario_de_video`): um Edital
publicado com a Etapa "Verificação da autodeclaração" decisória, três avaliações, regra
**unanimidade para o favorável**, alcance `L2`, `videoOption = true`, período aberto hoje; Maria
inscrita em `L2`; três membros alocados com a Atribuição dela.

## 3. O candidato

1. Entrar no portal como Maria (`m@ex.br`; o código sai no terminal do servidor).
2. Acompanhamento → "Verificação da autodeclaração" → "Gravar um vídeo curto".
3. Declarar "Tenho 18 anos ou mais"; marcar "Usar imagem de teste".
4. Gravar os quatro passos, assistir, gravar de novo, enviar.
5. **Esperado**: o comprovante com número, data, duração, formato e resumo; o console sem violação
   de CSP; a 375 px, sem rolagem lateral.

Para a queda no envio: no console, `window.__verificacao.simularQueda(2)` interrompe na segunda parte;
"Tentar de novo" retoma da segunda.

## 4. A comissão

1. `/gestao/` como Ana → Minhas atividades → a Etapa → Maria → "Abrir o vídeo".
2. Saltar ao passo 3, recuar 10 s, 0,5×; "Confirmo".
3. **Esperado**: na trilha da avaliação, um `VISUALIZAR_VIDEO_DA_VERIFICACAO`.
4. Bruno: concluir sem abrir → "Abra o vídeo antes de dar o parecer."; abrir, "Não dá para confirmar
   pelo vídeo" com motivo. Carla: "Confirmo".
5. Presidência → Distribuição → Consolidar: Maria em "Encaminhar à entrevista ao vivo", sem contagem.
   Encaminhar → as três Avaliações voltam à Mesa.

## 5. A retenção

```bash
uv run python manage.py eliminar_videos_da_verificacao --edital <uuid>
```

**Esperado**: recusa "o prazo de retenção do vídeo ainda não foi decidido (P-10)".

## 6. A suíte

```bash
cd backend && DB_NAME=ps_166 make lint check test-pg
```
