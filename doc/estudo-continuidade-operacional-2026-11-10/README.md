# Auditoria de continuidade da experiência operacional do GPS (2026-11-10)

**Pergunta.** O GPS oferece uma experiência coerente ao longo da operação inteira? Ela começa quando o
operador identifica uma providência no Centro de Controle do Edital, segue pela tela real do ato, e
termina quando ele volta ao Centro e reconhece o novo estado e a próxima providência.

**Resposta curta.** **No estado, sim; na passagem, não.**
- **No estado.** Em todos os 18 retornos ao Centro, o estado novo apareceu na hora, com a data da
  espera e o papel de quem age. O Centro e o retorno das telas vêm da mesma derivação (127), e nunca se
  contradisseram.
- **Na passagem.** A experiência se rompe em quatro pontos, sempre os mesmos:
  1. **Chegada.** A providência leva ao topo da tela, e o ato está longe. No sorteio, a 1.681 px e sob o
     passo seguinte; na conferência documental, a 2.151 px; o desfecho, a 3.020 px.
  2. **Ato irreversível.** Só 4 dos 11 tipos de ato irreversível percorridos têm conferência antes.
     Convocar pratica **e envia as mensagens** num clique, embora a ajuda prometa mostrar antes o texto
     ao candidato.
  3. **Retorno.** A tela diz o próximo passo, mas não leva até ele (leva ao topo de outra tela), não
     liga o "Ainda neste marco" e não volta ao Centro. A volta custa dois cliques.
  4. **No próprio Centro, duas vezes.** Ele diz que "o GPS não escolhe a ordem" entre ações que têm
     ordem:
     - no sorteio, observar a semente antes de fixar a segunda lista a condena em silêncio, e o Centro
       segue oferecendo o sorteio dela;
     - depois de um recurso, ele oferece a ordem sucessora antes da avaliação que falta ao reabilitado.

**A intervenção de maior ganho** é completar as duas pontas que já existem, sem peça nova:
- **o bloco "Próximo nesta lista"**, um parcial usado em seis telas: link de volta ao Centro e
  "Ainda neste marco" clicável;
- **a URL da providência**: um fragmento que leva ao lugar do ato.

São poucas linhas, e melhoram as cinco jornadas de uma vez (grupos G1 e G2 do [plano](05-plano-de-evolucao.md)).
Logo depois vem a **conferência antes de convocar**: é o único ato irreversível do percurso que sai do
GPS.

## Entregas

| | Documento | Conteúdo |
|---|---|---|
| A | [Mapa das jornadas percorridas](01-mapa-das-jornadas.md) | as cinco jornadas, passo a passo, como o GPS as conduz; o inventário das telas percorridas, com as 12 colunas pedidas |
| B | [Diagnóstico de continuidade](02-diagnostico.md) | os sete momentos da jornada × cinco jornadas; os seis pontos de ruptura (R-1 a R-6); as onze coisas que funcionam e devem ser preservadas (P-1 a P-11) |
| C | [Inventário priorizado de melhorias](03-inventario-de-melhorias.md) | M-01 a M-23 nos eixos impacto × abrangência; P1 com todos os campos; o que depende da D-5, à parte |
| D | [Protótipos navegáveis](04-prototipos.md) | 9 páginas antes/depois, montadas sobre o HTML real; 50 de 50 conferências automatizadas ([validacao.txt](validacao.txt)) |
| E | [Plano de evolução incremental](05-plano-de-evolucao.md) | oito grupos mínimos, as dependências, o que se reaproveita, e duas tarefas para a validação com operadores da 136 |
| — | [Achados funcionais](06-achados-funcionais.md) | F-1 a F-5, separados do escopo, com proposta de investigação |

O caderno do walkthrough está em [`passeio/`](passeio/), e as 104 capturas, em [`capturas/`](capturas/).

## Método

- **Banco isolado e descartável.**
  - `ps_continuidade`, PostgreSQL local, com os 15 cenários da `134`, rodada 1.
  - Para o sorteio, o C06 foi restaurado duas vezes: rodadas 2 e 3.
  - Nenhum banco de homologação ou de desenvolvimento foi tocado.
- **Código.** A `main` em `594d8494`. A 135 (#440, #441) e a 136 (#442, #443) já estavam mergeadas
  quando o estudo começou, e por isso não foi preciso integrá-las numa branch descartável.
- **Atos praticados no navegador, pelo Playwright.** O percurso por jornada:
  - A: congelar, observar e sortear, na ordem errada e na certa, e publicar;
  - B: avaliar, consolidar, distribuir, emitir a ordem e publicar;
  - D: convocar e emitir o corte;
  - E: conferir, reenviar como candidato e registrar o desfecho;
  - C: recorrer como candidato, admitir e julgar.

  Antes, durante e depois de cada ato relevante, o Centro foi reaberto.
- **Atos não praticados, e por quê:**
  - o corte do C06 e o resultado definitivo: o prazo recursal corre até 15/11, e a recomendação da tela
    é esperar;
  - a ordem sucessora do C08: a prévia mostrava que ela sairia errada (F-2);
  - "Pedir a faixa seguinte" do C15 (F-5).
- **Papéis exercidos:** presidência, avaliação, Publicador, Julgador e candidato (portal, com o código
  lido no terminal do servidor).

## Decisões pendentes que este estudo toca

| Decisão | O que o estudo trouxe | O que fez |
|---|---|---|
| **D-5** — observar a extração antes de congelar todas as relações | evidência de ponta a ponta do risco (A4–A10): o Centro e o retorno da tela empurram para a semente com a PPP por fixar, o congelamento tardio é aceito em silêncio na fonte de demonstração, e o sorteio da PPP só se recusa depois | **não decidiu.** As frases que corresponderiam às opções (b) e (c) estão no protótipo marcadas "Depende da D-5"; nada foi desabilitado |
| **D-2** — onde mora o Centro | o retorno custa dois cliques porque a migalha aponta o detalhe atual | propôs o retorno no bloco do próximo passo, que vale com qualquer resposta à D-2; não tocou a migalha |
| **D-7** — textos pedagógicos | os nomes do Centro não chegam às telas | propôs que as telas leiam os nomes do mesmo módulo da 136, e não os copiem |

## Limitações

- **Nenhum teste com pessoas.** As evidências são o percurso praticado, as medições e a inspeção.
- **A Loteria Federal não foi exercitada.** A fonte dos cenários é a de demonstração. O F-1 depende
  disso: em produção, com a Caixa, o aviso da 102 deve cobrir o caso, e isso não foi verificado.
- **Os cenários de pontuação têm a PPP vazia.** A continuidade entre duas listas com gente nas duas foi
  vista só no sorteio.
- **O celular** só foi medido nos protótipos.
- **Os ids** dos scripts são os do banco do estudo. Outro banco precisa de `prototipo/ids.json`.
