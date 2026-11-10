# Entrega C — Inventário priorizado de melhorias

**Critério.** Um ajuste de texto, hierarquia ou feedback vale mais que um redesenho. Nenhuma melhoria
muda regra de classificação, sorteio, convocação, recurso ou conferência, nem cria estado, componente
global ou camada de jornada. O que depende de decisão de domínio está separado, no fim.

**Eixos.**
- **Impacto:** alto (evita ato errado ou rompe a jornada), médio (atrito, ambiguidade, busca), baixo (texto).
- **Abrangência:** recorrente (várias jornadas ou telas), crítica pontual (um lugar, mas num ato
  irreversível), localizada (um lugar, sem ato irreversível).
- **Prioridade:** P1 primeiro, P2 em seguida, P3 quando houver folga.

## A matriz

| | Recorrente | Crítica pontual | Localizada |
|---|---|---|---|
| **Alto** | **M-01** retorno ao Centro · **M-02** providência leva ao ato · **M-07** próximo alcançável · **M-12** conferência nos atos de um clique | **M-04** conferência antes de convocar · **M-06** ato antes do método no sorteio | M-18 transição do Julgador |
| **Médio** | M-03 objetivo na voz do Centro · M-09 "Ocupadas na apuração" | M-13 a ordem sorteada na tela do sorteio · M-14 consequência na publicação | M-05 índice das seções · M-08 contexto e próximo da pessoa · M-10 "seu papel" × "1 ação é sua" · M-20 portal · M-22 desempate explicado |
| **Baixo** | M-11 concordância · M-23 parágrafos repetidos | M-15 "falta publicar" com quem | M-16 fim da Mesa · M-17 efeito da consolidação · M-19 fila sem vaga · M-21 rolagem a 375 px |

## P1 — fazer primeiro

### M-01 · Voltar ao Centro a partir do bloco do próximo passo
| | |
|---|---|
| **Evidência** | A4, A11, B12, D4, D6, E5, E10, E11 — nenhuma tela operacional liga ao Centro; a volta custa 2 cliques (migalha → detalhe → link em y=169) |
| **Tela** | as seis que incluem `_proximo_nesta_lista.html`: sorteio, ordem, corte, ocupação, convocação, documentos |
| **Problema** | depois do ato, a pessoa entende o resultado e o próximo, mas o ponto de retorno da jornada não está à mão |
| **Impacto** | alto · recorrente |
| **Causa provável** | o Centro nasceu numa rota própria (D-2 em aberto), e a migalha continua apontando o detalhe atual |
| **Melhoria** | uma linha "Voltar ao Centro de Controle do Edital" no fim do bloco, **só depois de um ato** (onde o bloco já aparece). Não mexe na migalha, que é decisão da D-2 |
| **Complexidade** | baixa — um link num parcial, com a URL do Edital que todas as seis telas já têm |
| **Risco** | baixo. Se a D-2 levar o Centro ao detalhe, o link continua certo |
| **Prioridade** | **P1** · protótipo: `sorteio-c06-apos-fixar-a-ampla`, `documentos-c12-apos-conferir` |

### M-02 · A providência leva ao lugar do ato
| | |
|---|---|
| **Evidência** | A2 (ato em y=1681), A3 (`?lista=` não rola), E2 (chamadas em y=2151), E10 (desfecho em y=3020) |
| **Tela** | Centro → sorteio, convocação; retorno de documentos → convocação |
| **Problema** | a pessoa clica numa providência específica e chega ao topo de uma tela genérica, e tem de procurar |
| **Impacto** | alto · recorrente |
| **Causa provável** | `andamento.Celula.url` aponta a tela sem fragmento; os recortes do sorteio não têm id por lista |
| **Melhoria** | fragmento na URL: `#titulo-recortes` ou `#recorte-<lista>` no sorteio, `#chamadas` na conferência, `#chamada-N` no desfecho. Os alvos já existem, exceto os ids dos recortes |
| **Complexidade** | baixa — na montagem da URL da célula e um id por `article.recorte` |
| **Risco** | baixo. O guardião de rotas e o inventário da 033 não mudam: a rota é a mesma |
| **Prioridade** | **P1** · protótipo: os três Centros e a convocação; V5 a V7 medem a chegada na dobra |

### M-04 · Conferência antes de convocar, sempre
| | |
|---|---|
| **Evidência** | D3 — "Convocar as 3" praticou e enviou 3 e-mails no clique; a ajuda dizia "antes de confirmar, você o verá como o candidato" |
| **Tela** | `convocacao.html`, gesto dos titulares e chamada individual |
| **Problema** | o ato é irreversível **e sai do GPS** (a comunicação), e a interface promete uma conferência que não acontece |
| **Impacto** | alto · crítica pontual |
| **Causa provável** | `conferencia_do_texto.exigir` só intercepta quando há complemento (125, FR-3993); a ajuda foi escrita para esse caso e lê como geral |
| **Melhoria** | a conferência da 125 vale também sem complemento, com as peças de `marco_conferir.html`: quem será convocado, o texto que cada um lê, o prazo (ou a falta dele) e quem fica de fora. **Mínimo, se a conferência sempre não for aceita:** corrigir a ajuda para não prometer |
| **Complexidade** | média — o fluxo da conferência já existe; muda a condição e o conteúdo |
| **Risco** | baixo; um clique a mais num ato de alto custo. A idempotência da 125 continua |
| **Prioridade** | **P1** · protótipo: `convocacao-c15` → `convocar-c15-conferencia` |

### M-06 · No sorteio, o ato antes do método
| | |
|---|---|
| **Evidência** | A2 — ordem da tela: método (8 campos + resumo), ocorrência com o botão primário "Observar", recortes; "Nenhum corte emitido" em amarelo antes do sorteio |
| **Tela** | `sorteio.html` |
| **Problema** | o que a pessoa veio fazer (fixar) está a 1.681 px, sob o passo seguinte (observar), que é o botão de maior peso |
| **Impacto** | alto · crítica pontual (os dois atos são irreversíveis, e a ordem entre eles decide o sorteio) |
| **Causa provável** | a tela foi montada na ordem do método, e não na da tarefa; o estado do corte por recorte (014, UX-029) aparece em qualquer fase |
| **Melhoria** | (1) recortes antes da ocorrência, e o método recolhido num `details`, inteiro; (2) "Observar" como secundário enquanto há lista por fixar — **sem desabilitar**, o que seria decidir a D-5; (3) o estado do corte só depois do sorteio |
| **Complexidade** | baixa — ordem de blocos e uma classe |
| **Risco** | baixo. O conteúdo publicado do método continua na tela (V3 confere o resumo) |
| **Prioridade** | **P1** · protótipo: `sorteio-c06-inicial`; V1 mede 1681 → 1053 px e a ordem fixar → observar |

### M-07 · O próximo passo alcançável
| | |
|---|---|
| **Evidência** | A4 e B12 ("Ainda neste marco" sem link), E5 e E10 (o próximo leva ao topo da convocação), B4 (a Mesa leva à próxima pendente) |
| **Tela** | `_proximo_nesta_lista.html` e `convocacao_documentos.html` |
| **Problema** | o próximo é dito, e a pessoa ainda tem de achá-lo |
| **Impacto** | alto · recorrente |
| **Causa provável** | o bloco renderiza `outras` como texto, e o `url` da célula é o da tela (M-02) |
| **Melhoria** | "Ainda neste marco" com link para cada item; nos documentos, "Próximo para esta pessoa" (desfecho, quando pronta) antes de "Depois, nesta lista" |
| **Complexidade** | baixa a média |
| **Risco** | baixo. A escolha **de qual** item vem primeiro continua sendo a da derivação — mudar isso no sorteio é a D-5 |
| **Prioridade** | **P1** · protótipo: os dois retornos |

### M-12 · Conferência nos outros atos irreversíveis de um clique
| | |
|---|---|
| **Evidência** | A4, A6, A11 (congelar, observar, sortear), D6 (corte), C5 (admitir, julgar) |
| **Tela** | sorteio, corte, recurso |
| **Problema** | 7 dos 11 tipos de ato irreversível do percurso não passam por conferência (ver [02](02-diagnostico.md), R-2) |
| **Impacto** | alto · recorrente |
| **Causa provável** | cada tela nasceu numa spec, e a conferência não foi padrão desde o começo |
| **Melhoria** | o padrão "Confira antes de…" das quatro telas que já o têm. No sorteio, a conferência do **congelamento** mostra a lista, os participantes e os números que ficam publicados. A conferência da **observação** fica de fora: uma confirmação antes de observar é a opção (b) da D-5, e só entra com ela |
| **Complexidade** | média por ato; alta para todos |
| **Risco** | médio: mais um passo em atos frequentes (avaliar não entra, por ser reabrível). Medir com operadores |
| **Prioridade** | **P1** para congelar e convocar (M-04); **P2** para sortear, corte, admitir e julgar; observar, **só com a D-5** |

## P2

| # | Evidência | Tela | Problema | Imp. · abr. | Causa provável | Melhoria | Compl. | Risco |
|---|---|---|---|---|---|---|---|---|
| M-03 | A2, R-5 | sorteio (e corte, ocupação) | a tela não ecoa o nome que o Centro usou | médio · recorrente | telas anteriores à 136 | uma linha "O que se faz aqui" e os passos, com "(no GPS: …)", lendo os nomes do módulo de conceitos da 136 | baixa | baixo; os textos da 136 são provisórios (D-7) |
| M-08 | E3, E10 | documentos da convocação | sem Edital, Perfil e lista; "pronta para decidir" sem o desfecho por perto; "pendente" sem o "Avisar" | médio · localizada | a tela é por pessoa e herdou o cabeçalho da pessoa | contexto no alto; "Próximo para esta pessoa" leva a `#chamada-N`; depois de um pendente, link para `#avisar-pendencias` | baixa | baixo |
| M-09 | D2, D9 | convocação, ocupação | "3 Ocupadas · 0 Convocadas" lê como vagas já preenchidas | médio · recorrente | o número é da apuração, o rótulo não diz | "Ocupadas na apuração" / "A ocupar na apuração"; os números não mudam (V9) | baixa | baixo |
| M-10 | B1 | Centro | "Seu papel: sem ato a praticar" ao lado de "1 ação é sua" | médio · localizada | a frase do papel lê o papel institucional; a ação vem da alocação (104) | a frase considera `e_sua` (a mesma regra que conta "1 sua") | baixa | baixo |
| M-13 | A11, A17 | sorteio | a ordem sorteada só aparece no corte e no canal público | médio · crítica pontual | a tabela é a da relação | depois do sorteio, a tabela mostra a ordem sorteada (ou o link para ela, no lugar do quadro) | média | baixo |
| M-14 | A14, A15 | condução e conferência da publicação | o Publicador lê sobre quem ordena e corta; a conferência não diz que o preliminar abre o prazo recursal, nem até quando | médio · crítica pontual | a mensagem `conducao_para_emitir` aparece para quem não emite; a conferência é genérica de marco | mostrar a frase só a quem tem alguma ação do eixo; na conferência do preliminar, "abre o prazo de recurso até …" quando a janela é computável | baixa | baixo |
| M-18 | C3–C5 | Centro do Julgador; recurso | o Julgador não sabe que a instrução é da presidência; depois de decidir, nada diz o efeito | alto · localizada | — | no recurso, "o que acontece depois": "a presidência emitirá a ordem sucessora"; no Centro, a instrução como pré-requisito quando faltar (a verificar) | média | baixo |
| M-22 | B11 | ordem | 01 e 02 com 26 pontos: o critério que os separou não é dito | médio · localizada | a tela explica só o empate residual | uma coluna ou nota "desempatado por: maior pontuação na Prova objetiva", se o ato registra o critério aplicado | média | baixo; **a verificar** se o dado existe no ato |

## P3

| # | Evidência | Tela | Melhoria |
|---|---|---|---|
| M-05 | E2 | convocação (3.500 px) | índice curto das seções, com os ids que a tela já tem — protótipo em `convocacao-c12` |
| M-11 | D5, E6 | Centro | "SUA VAGAS" → rótulo da fase sem o possessivo, ou concordância; "1 aguardam" → "1 aguarda" |
| M-15 | A11 | sorteio | "Falta publicar a classificação, com quem publica resultado" — o bloco do próximo já diz isso; a frase de sucesso não |
| M-16 | B5 | fim da Mesa | "A consolidação é da presidência; nada mais é seu nesta Etapa" |
| M-17 | B8 | consolidação | o efeito ("2 eliminadas, 6 habilitadas") no retorno, e recolher "Distribuir o que falta" quando não falta nada |
| M-19 | D4 | convocação | com todas as vagas cobertas e nenhuma vaga vaga, "Chamar uma pessoa da fila" recolhido, com a razão — **validar com operadores**: a chamada individual também serve a exceções |
| M-20 | E7, C1, C8 | portal | a lista diz "1 documento a corrigir" / "pode recorrer até …"; o acompanhamento não diz "Nada por enquanto" ao lado de "pode recorrer" |
| M-21 | V0 | sorteio depois de congelar, 375 px | rolagem horizontal já na tela real (o resumo de 64 caracteres sem quebra) |
| M-23 | B12, D8 | ordem, ocupação | parágrafos repetidos: "Divulgá-lo não é ato seu…" e o da vaga acrescida |

## Depende de decisão de domínio — não priorizado

| # | O quê | Decisão | Evidência |
|---|---|---|---|
| D5-a | dizer, no lugar (retorno do congelamento, ocorrência, Centro), que uma lista fixada depois da semente não sorteia | **D-5**, opção (c) "só alertar" | A4–A10. Protótipo marcado com contorno tracejado, para a decisão se tomar olhando a tela |
| D5-b | o retorno do congelamento apontar a lista que falta **antes** da semente | **D-5** | A4 |
| D5-c | uma conferência antes de observar a ocorrência | **D-5**, opção (b) | A6 |
| — | a derivação parar de oferecer "Realizar o sorteio" na lista que nunca sorteará | achado **F-1** | A10 |
| — | a ordem sucessora esperar a avaliação do reabilitado | achado **F-2** | C6, C7 |

A frase da D5-a não é regra nova: a recusa do sorteio já a diz depois do fato (A8), e o guia da `134`
a diz ao treinando ("Congele as duas antes de observar a ocorrência"). Dizê-la antes do fato é a opção
(c) da D-5, e por isso fica com o usuário.
