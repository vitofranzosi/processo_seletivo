# Quickstart: verificar a feature 144 à mão

O roteiro da jornada inteira (SC-1590), para quem implementa conferir no navegador e capturar. O
teste `navegador/test_jornada_do_cronograma.py` automatiza o mesmo caminho.

## Preparar

1. Worktree com banco próprio (`DB_NAME` único), migrado nos três passos do `make preparar`.
2. `INTERFACE_SELETOR_IDENTIDADE=true` no ambiente do `runserver` — sem ele `/gestao/` devolve 503.
3. Entrar como quem elabora, com um Edital em elaboração e uma Etapa cadastrada.

## Roteiro

1. Abrir a etapa **Cronograma**. Acrescentar três Eventos: Inscrições (03/11 a 10/11), Avaliação
   curricular (12/11 a 14/11), Resultado (20/11). A prévia mostra "3 eventos · 3 no PDF", com as
   colunas Evento · Início · Término · PDF.
2. No cartão da Avaliação curricular, acionar o olho. O cartão diz "Oculto do PDF"; a prévia,
   "3 eventos · 2 no PDF · 1 oculto", e a linha diz "Oculto".
3. Mudar o início do Resultado para 01/11. A sequência fica fora da cronologia, e **nada se move**.
4. Acionar **Ordenar por data de início ↑**. O Resultado vai para o topo do formulário e da prévia; o
   anúncio diz quantos Eventos mudaram de posição; o foco continua no botão — e não salta para o
   primeiro campo de um cartão. Mover um cartão pela seta também deixa o foco na seta.
5. Gravar. Voltar à etapa: ordem e visibilidade são as de antes.
6. Na etapa **Etapas**, vincular a Etapa à Avaliação curricular: ela está na lista, oculta ou não.
7. **Ver o Edital** (prévia do PDF): a tabela do Cronograma tem duas linhas, numeradas 1 e 2; a Etapa
   diz "Será feita de 12/11/2026 … a 14/11/2026 …".
8. Ocultar os três e gravar: a prévia da etapa diz que a seção não será impressa; a Revisão também; o
   PDF não tem seção Cronograma, e a numeração das seções fecha.
9. Repetir 1 a 4 a 375 px: sem rolagem horizontal; a prévia empilha as datas sob o nome.
10. Console do navegador: nenhuma violação de CSP.

## Capturas para `verificacao.md`

A etapa antes e depois de ordenar (1440 px), a prévia com um oculto (375 px), a tabela do PDF com
dois Eventos, a Revisão com o Evento oculto.
