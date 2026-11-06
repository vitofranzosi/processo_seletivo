# Roteiro de validação das maquetes

Parte do [estudo de orientação da jornada](README.md). É uma avaliação **formativa**: diz se a proposta
resolve as tarefas críticas e onde ela falha, e não demonstra estatisticamente que é superior. Cinco
participantes bastam para achar os problemas grandes; não bastam para comparar médias.

## O que se quer saber

Se o operador **compreende o andamento e identifica a providência apropriada sem abrir sucessivamente
telas operacionais** (a exigência de produto da revisão de 06/11). Não se mede preferência.

## Participantes

- 5 pessoas: 2 ou 3 da equipe do Cefor que conduziram um Edital no GPS, e 2 ou 3 que conhecem o
  processo seletivo mas não operaram o 35, o 57 nem o 26.
- Ninguém que tenha lido este estudo ou visto as maquetes antes.

## Desenho

**Dentro de cada participante, duas condições, em ordem alternada** (3 começam pela atual, 2 pela
proposta), com Editais diferentes em cada condição, para que a segunda não se beneficie da memória da
primeira:

| Condição | Material | Como se interage |
|---|---|---|
| Atual | O GPS no banco de demonstração (`ps_jornada`), navegável | Navegação livre; conta-se cada tela aberta |
| Proposta | As maquetes v2 (`maquetes/N*.jpg`, `M3*`, `M4`) | Teste de primeiro clique: a pessoa aponta onde clicaria e diz o que espera encontrar |

**A assimetria é deliberada e tem custo**: a maquete não navega, e por isso a proposta é medida pelo
primeiro clique e pela resposta, e a atual pela navegação inteira. Para comparar navegação com
navegação seria preciso um protótipo clicável; se o resultado ficar ambíguo, ele é o próximo passo
(meio dia de trabalho com as próprias maquetes ligadas por link).

## As cinco tarefas

Pergunta lida em voz alta, sem os termos da tela. Para cada uma: o material, a resposta certa e os
erros que se espera encontrar.

| # | Tarefa | Atual | Proposta | Resposta certa | Erros a codificar |
|---|---|---|---|---|---|
| 1 | **Localizar o ponto atual.** "Neste Edital, o que já aconteceu e o que ainda está em aberto?" | Edital 35, como quem conduz | `N1` | Cefor: sorteado, cortado, apurado, resultado preliminar, convocação com 1 comunicação pendente; definitivo por publicar. Polo Vitória: nada a fazer | Dizer que o Edital "está quase encerrado"; esquecer o definitivo; dizer que o Polo Vitória está atrasado |
| 2 | **Descobrir a próxima providência.** "O que você pode fazer agora, e onde?" | Edital 35, como quem conduz; e o mesmo como quem publica | `N1` e `N2` | Quem conduz: emitir a comunicação de INS-2026-FICTC010. Quem publica: publicar o definitivo | Primeiro clique em "Inscrições recebidas" ou em "Encerrar"; não achar a ação de quem publica |
| 3 | **Interpretar situações diferentes.** "Os dois cursos deste Edital estão no mesmo ponto?" | Edital 57 | `N4` | Não. Design Educacional espera a extração 6116; Tecnologias Digitais ainda precisa congelar | Atribuir uma fase única ao Edital; achar que é preciso esperar a semente para congelar o outro |
| 4 | **Reconhecer o não aplicável.** "O Polo Vitória precisa de alguma providência?" | Edital 35, condução do marco do Polo Vitória | `N1`, `M3b` | Não: ninguém se inscreveu nele | Tomar "Falta" como pendência; tentar cortar ou apurar |
| 5 | **Continuar depois de um ato.** "Você acabou de emitir este corte. E agora?" | Captura `13b` (o banco já tem o corte do 26) | `M4` | Apurar a ocupação desta lista; a outra lista do marco ainda não tem relação | Clicar em "Emitir corte" de novo; não perceber a outra lista |

A tarefa 5 é por imagem nas duas condições: o ato não se pratica duas vezes no mesmo banco.

**[v3] Uma família que não é sorteio, em cada tarefa que admite.** As tarefas 1 e 2 se repetem no
Edital 91, por pontuação (atual: o GPS como a presidência; proposta: `G1`). Resposta certa da 2: avaliar
as 12 da Prova de Títulos e distribuir as da Prova de Desempenho Didático; a Entrevista está declarada,
mas nada depende dela (D9). Erros a codificar: clicar em "Emitir ordem"; não achar a distribuição a
partir do Edital; tratar a Entrevista como obrigação do sistema. Na tarefa 1 do 35, a resposta certa
passa a mencionar as duas Etapas declaradas que nada consome (`G2`).

## Medidas

| Medida | Como | Por tarefa |
|---|---|---|
| Acerto | Resposta igual à certa, sem ajuda | sim / parcial / não |
| Erros de interpretação | Os da coluna acima, mais os que aparecerem, codificados depois | contagem e tipo |
| Primeiro clique | Correto ou não | sim / não |
| Telas abertas (atual) | Contadas pelo moderador | número |
| Tempo | Do fim da pergunta à resposta | segundos; só descritivo |
| Confiança | "De 1 a 5, quão seguro você está?" | 1 a 5 |

## Critérios, fixados antes

**A proposta passa** se:

- tiver acerto em pelo menos 4 de 5 participantes nas tarefas 1 a 4;
- **ninguém** tomar o Polo Vitória como pendente na tarefa 4;
- o primeiro clique da tarefa 2 estiver correto em pelo menos 4 de 5;
- ninguém clicar de novo em "Emitir corte" na tarefa 5.

**Sinais de que a proposta falhou, mesmo passando:**

- as pessoas leem o nível 1 e abrem as telas operacionais mesmo assim, para confirmar;
- alguém entende "Sua" como "atribuída a você pela comissão";
- a contagem ("2 providências em aberto") é lida como prazo ou urgência.

## Roteiro da sessão (≈ 40 min)

1. Apresentação (3 min). Sem falar das maquetes nem do estudo.
2. Condição A, tarefas 1 a 5, pensando em voz alta (15 min).
3. Condição B, tarefas 1 a 5 nos outros Editais (15 min).
4. Três perguntas abertas (5 min): o que foi mais difícil de achar; o que você não entendeu; o que
   sobrou na tela.
5. Registro: uma planilha por participante, com tarefa × medida.

## O que este roteiro não cobre

- Quem opera a 375 px; quem usa leitor de tela. A acessibilidade se verifica na spec, com os guardiões
  da gestão e uma sessão com leitor de tela.
- O nível 2 aberto em Edital com muitos Perfis. O banco não tem um; a spec precisa de um cenário com
  pelo menos 6 Perfis antes de dizer que o nível 2 escala.
