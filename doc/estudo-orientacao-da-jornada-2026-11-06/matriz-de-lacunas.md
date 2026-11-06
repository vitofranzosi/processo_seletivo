# Matriz de lacunas de orientação

Parte do [estudo de orientação da jornada](README.md). Cada achado tem captura em `capturas/` e
referência de código. As referências estão no [mapa da jornada](mapa-da-jornada.md) e são relativas a
`backend/processo_seletivo/`.

**Como ler.** *Gravidade* mede o risco de o operador não saber o que fazer, ou de fazer o que não devia,
num Edital publicado. Não mede esforço de correção. Tudo aqui é inspeção especializada: nenhum achado foi
medido com pessoas.

Separei três naturezas de achado:

- **Orientação**: o sistema sabe e não diz.
- **Coerência**: duas telas dizem coisas diferentes sobre o mesmo fato.
- **Funcional**: possível defeito de regra, registrado aqui só porque desorienta. Não é escopo de orientação.

---

## O que já orienta bem

Não são lacunas, e a proposta não deve desfazê-los.

| ID | Onde | O que funciona | Captura |
|---|---|---|---|
| P-01 | Detalhe do Edital em elaboração | Trilha de situação, "O próximo ato é seu", botão desabilitado com o motivo ("1 pendência impeditiva") e uma Validação que separa *Impede* de *Aviso* e diz onde corrigir ("corrija a data do Evento na etapa Cronograma") | `03` |
| P-02 | Lista (104) | "Ações disponíveis para você" para quem elabora, homologa, publica, julga ou avalia. Ela só aparece quando há trabalho e diz o ato, desde quando e para onde ir | `02`, `18` |
| P-03 | Condução do marco (049) | Uma tabela de recortes × operações com *Feito/Falta/Obsoleto*, cada célula levando à tela do ato, o aviso "Abrir esta tela **não pratica nada**" e gestos em duas fases | `09`, `10` |
| P-04 | Ocupação, sorteio | Frases que distinguem o estado do percurso de um erro: "Este recorte ainda não tem ordem emitida… emita a ordem… e volte aqui. É estado do percurso, e não erro." e "Nenhuma inscrição submetida declarou esta lista… não há o que sortear" | `14` |
| P-05 | Convocação por recorte | Vagas publicadas, efetivas, ocupadas e a ocupar; "Comunicações que ainda não saíram"; "próxima da fila"; contadores de prazo em curso, vencido e sem comunicação | `22` |
| P-06 | Confirmação de Encerrar (113) | "Continuam depois do encerramento", com convocação aguardando e resultado definitivo não publicado | `16` |
| P-07 | Transições que orientam | A apuração leva a "Abrir a convocação deste recorte". O desfecho diz se a apuração seguinte saiu no mesmo ato. O atestado manda registrar o desfecho de inércia. O sorteio realizado diz "Falta publicar a classificação" | `14`; mapa §9 |
| P-08 | Recusas | Quase todas dizem o caminho, e não só o motivo; o guia de 05/11 já tinha visto isso | guia, cap. 4 a 12 |

---

## Lacunas

| ID | Tela | Cenário | Evidência | Problema | Consequência | Grav. | Causa provável | Correção possível |
|---|---|---|---|---|---|---|---|---|
| **J-01** | Detalhe do Edital publicado | 2 a 6 | `05`: seis Editais, o mesmo cartão. `acoes.py:407-411` (`PROXIMO_RESPONSAVEL` para em HOMOLOGADO); `PREFERENCIA_DA_PRINCIPAL` põe "Inscrições recebidas" como ação principal | "O que fazer agora" não muda entre um Edital que espera a semente (57), um sorteado (26), um em avaliação (91), um em convocação (51 e 35) e um com Retificação homologada à espera (72). A frase mais forte do cartão é uma negação ("Conteúdo imutável… Peça a alguém…") | Depois da publicação, a tela que responde "o que fazer" não responde. O operador precisa saber o rito de cor, e um Edital parado é indistinguível de um em andamento | **Alta** | Comunicação de estado: o bastão da FR-028 nunca foi estendido além da publicação | Bastão derivado das pendências do Edital (o mesmo padrão "papel + ato + sou eu?"), e um bloco de andamento |
| **J-02** | Detalhe do Edital publicado | 2 a 6 | `04`: trilha "Em elaboração → … → **Publicado** (situação atual) → Encerrado". `detalhe.html:15-23` | A trilha é o ciclo do documento. Depois de publicado, todo o trabalho (sorteio, corte, convocação…) mora dentro de um só ponto, e o próximo ponto desenhado é "Encerrado", que é também o primeiro botão contornado do cartão | Sugere que o Edital está quase no fim quando a seleção nem começou. Confunde situação do documento com andamento da seleção | Média | Arquitetura de informação | Legendar a trilha como situação do documento, ou recolhê-la depois de publicado (D1) |
| **J-03** | Gestão inteira | 3 a 6 | Para dizer o que falta no 35 é preciso abrir **7 telas**: o detalhe, as conduções dos 2 marcos, a convocação de 3 recortes e a confirmação de Encerrar (`10`, `11`, `22`, `16`). Mapa §8(1): nenhuma tela junta sorteio, condução e convocação; `sorteios_do_edital` só é usada no portal | O estado da seleção está fragmentado por marco e por recorte, e cada tela mostra um pedaço | Exige memória de trabalho e conhecimento do rito para montar o quadro, e é fácil esquecer um recorte | **Alta** | Arquitetura de informação | Um bloco no detalhe que junte as derivações já existentes (ver a proposta) |
| **J-04** | Detalhe, cartão "Classificação" | 2 a 4 | `06`: 57 (uma relação congelada, a outra não, semente pendente) e 91 (nenhuma relação; seleção por avaliação) mostram o mesmo "com ordem 0 · com corte 0 · apurados 0 · publicados 0". `conducao_do_marco.py:348` (`resumo_dos_marcos`) | O resumo conta ordem, corte, apuração e publicação; não conta relação congelada, semente observada nem convocação. "Sorteio" aparece só como sufixo do link. E o cartão é o quinto bloco da página, a ~1250 px do topo | Entre o fim das inscrições e o sorteio, o período em que mais se erra (congelar cedo, semente fora de hora), o resumo diz zero para tudo | **Alta** | Comunicação de estado | Contar as etapas do sorteio e a convocação, e subir o bloco para logo depois de "O que fazer agora" |
| **J-05** | Condução do marco | 3 a 5 | `10`: no 35 Cefor, "Nenhum recorte deste marco está em falta nas operações que você pratica", com uma convocação sem comunicação. `09b`: no 57, a célula "Ordem pelo sorteio" diz *Falta* sem distinguir relação, semente e sorteio. `conducao_do_marco.py:234-251`; `marco.html` não tem coluna de convocação | A condução termina na publicação. Antes dela, "Falta" junta três atos com responsáveis e momentos diferentes | O marco parece pronto enquanto há convocação parada; quem lê "Falta a ordem" não sabe se deve congelar, esperar a Caixa ou sortear | **Alta** | Escopo da 049 (era ordem, corte, apuração e publicação) | Colunas de relação, semente e convocação, e o motivo da espera na célula (maquete `M3`) |
| **J-06** | Condução e convocação de marco sem inscrito | 4, 6 | `11`: Polo Vitória (0 inscrições) com *Falta* nas 12 células e os gestos "Cortar o marco…" e "Apurar…". `12`: a convocação diz ao mesmo tempo "Ir para a apuração de ocupação" e "Não há mais quem chamar dentro da faixa… Ir para a ocupação e pedir a faixa seguinte". O estado `NAO_SE_APLICA` já existe em `conducao_do_marco.py` | Recorte vazio aparece como pendente, e a convocação dá duas orientações que se contradizem | Falsa pendência, que o encerramento herda, e um caminho que leva a recusa (pedir faixa sem corte) | Média | Coerência + funcional (a segunda frase é da família "regularizáveis sem corte" do guia) | *Não se aplica — sem inscritos* e nenhum gesto (maquete `M3b`); a frase da faixa seguinte só quando há corte |
| **J-07** | Confirmação de Encerrar | 5, 6 | `16`. `interface/encerramento.py:59-79`; `processos/application/pendencias_do_edital.py:87` | A única lista do que ainda está em aberto **no Edital inteiro** está na tela de um ato irreversível. Além disso, ela diz "1 convocação aguardando resposta, até 10/11/2026" de uma convocação cuja comunicação não saiu e cujo prazo, pela tela da convocação, "não começou a correr" | Para saber o que falta, o caminho mais curto é fingir que vai encerrar | Média | Arquitetura de informação; coerência no rótulo | Mostrar a mesma derivação no detalhe, como leitura; distinguir "sem comunicação" de "aguardando resposta" |
| **J-08** | Telas de ato | 3 a 6 | `13a`/`13b`: depois de emitir o corte, a mesma tela com "Corte emitido." e, logo abaixo, o formulário de **outro** "Emitir corte" (sucessão), aberto. Mapa §9: ordem, congelar, observar, convocar, comunicar e conferir documento também só confirmam | A transição confirma e não diz o próximo passo da lista nem o que falta no marco. O botão de maior peso depois do sucesso é o de suceder o ato que acabou de ser praticado | Ritmo quebrado em cada ato; e risco de sucessão por engano, que é ato imutável com motivo | **Alta** | Feedback | "Próximo nesta lista" e "Ainda neste marco" no aviso de sucesso; sucessão recolhida (maquete `M4`) |
| **J-09** | "O que fazer agora", por papel | 2 a 5 | `17`: o publicador lê "Nenhum ato disponível para seus papéis" no 35, que tem o resultado definitivo por publicar, e o mesmo detalhe oferece "divulgar o resultado" mais abaixo. `18`: a presidência do 91 tem "Avaliar (12 pendentes)" na Lista e nada no cartão do Edital. Mapa §8(3): o alocado à conferência não tem caminho até a convocação; `sorteio.html:75-79, 385` diz "Falta publicar a classificação" à presidência sem dizer a quem pedir | O cartão só conhece atos do Edital e a Retificação (que a 104 incluiu pela FR-2819). Avaliação, divulgação e conferência ficam de fora | A mesma contradição que a 104 corrigiu para a Retificação, agora nos outros trabalhos | Média | Coerência | Estender a FR-2819 da 104 aos outros trabalhos do Edital, e "Peça a quem publica resultado" onde falta |
| **J-10** | Sorteio | 3, 6 | `08`: no 35 Cefor, com as 3 relações congeladas e sorteadas, o topo dos recortes diz "Não congele a relação hoje: o sorteio seria recusado… peça… que o retifique". No Polo Vitória, sem inscritos, pede Retificação da extração | O aviso vale só para uma eventual sucessão, mas aparece no topo, como se fosse a próxima ação | Leva a pedir Retificação sem necessidade e ensina a ignorar avisos | Média | Feedback sem contexto | Mostrar o aviso só onde há relação a congelar, ou dentro do formulário de sucessão |
| **J-11** | Lista | 2 a 6 | `01`: para quem conduz, a faixa diz "Nenhum ato… aguarda você agora. Classificação, divulgação de resultado e avisos… ficam no detalhe de cada Edital", e as 8 linhas publicadas são iguais ("Inscrições recebidas · Encerrar · Cancelar") | Quem conduz não tem, na entrada, sinal de qual Edital pede ação | Visita Edital por Edital | Média | Decisão da 104 (D-002), por custo de consulta | Depois do incremento 1, levar a contagem de "Em aberto" à linha, em lote (D4) |
| **J-12** | Sorteio, semente | 3, 6 | `15`: falha de acesso à Caixa mostra `**nada foi registrado**` com os asteriscos e "HTTPError: HTTP Error 500: Internal Server Error". `sorteios/application/ocorrencia.py:81`. `07`: antes da observação, a tela não diz quando a extração acontece se o Edital não declarou o instante | Erro técnico cru e marcação literal; ausência de quando voltar | O operador não sabe se errou, se a Caixa caiu ou se é cedo | Baixa | Linguagem | Texto sem marcação; "a Caixa não respondeu; tente de novo mais tarde"; mostrar o instante declarado, quando houver |
| **J-13** | Agenda, Visão Geral, Processo | 2 a 5 | `20`: "35/2026 Classificação Preliminar (Resultado do Sorteio)" em 03/11, sem dizer se aconteceu, o que é deliberado (`agenda.py:1-17`). `19`, `21`: Visão Geral e "Onde cada Edital está" cobrem só inscrições. Mapa §8(2): a Supervisão não tem sinal de sorteio nem de convocação | O previsto não se liga ao realizado em lugar nenhum | Um evento com data passada parece cumprido | Média | Arquitetura (previsto × realizado são de fontes diferentes, e a Agenda não deve afirmar execução) | No Andamento, mostrar o ato (e não o evento); a Agenda continua só previsão |
| **J-14** | Processo, "Atenção" | 4 | `21`: o 35, conduzido por sorteio, tem "Etapa… tem inscrição sem avaliador suficiente — 11 de 11" para duas Etapas | Não se sabe se é trabalho a fazer ou Etapa que a operação não usa | Ruído ou pendência esquecida, e a tela não ajuda a distinguir | Baixa | **A confirmar**: depende de como o 35 conduz essas Etapas | Registrar para a equipe; não é escopo |
| **J-15** | Detalhe em elaboração | 1 | `03`: "1 pendência impeditiva precisa ser resolvida antes" sem link; o item é o 5º de 7 da Validação, entre avisos | Pequena caça ao impeditivo | Atrito leve | Baixa | Feedback | Link "ver a pendência", e impeditivos antes dos avisos |
| **J-16** | Inscrições, detalhe | 2 | Mapa §3: a tela de inscrições não diz o que vem depois. `04`: o detalhe não diz se o período está aberto nem quando termina; só Visão Geral e Processo dizem | A pergunta "já posso congelar?" não tem resposta no Edital | Congelamento cedo (o achado da relação congelada com inscrições abertas) ou espera desnecessária | Média | Comunicação de estado | A linha "Inscrições encerradas em… / abertas até…" no Andamento |

### Por tipo de problema (a classificação do pedido)

| Tipo | Achados |
|---|---|
| Visibilidade da situação | J-01, J-04, J-16 |
| Orientação da próxima ação | J-01, J-08, J-09 |
| Dependências ocultas | J-05, J-12, J-16 |
| Fragmentação de contexto | **J-03**, J-07 |
| Inconsistência terminológica / de mensagem | J-06, J-07, J-09, J-10 |
| Excesso de informação | J-10 (aviso irrelevante); o "Conteúdo imutável" de cinco linhas em J-01 |
| Falta de feedback | **J-08**, J-12 |
| Falta de visão global | **J-03**, J-11 |
| Previsto × realizado | J-02, J-13 |

### O que **não** é lacuna

- **Não ter um *stepper* de seis momentos.** Os seis momentos do material pedagógico não são estado
  do sistema. No 35, o marco do Cefor está no "momento 5" e o do Polo Vitória não tem momento
  nenhum. Uma barra única ou mentiria, ou mostraria a fase do recorte mais atrasado, que no 35 seria
  "antes do sorteio" para sempre.
- **A Agenda não afirmar execução.** É uma decisão da 101, e é correta: o cronograma é previsão. A
  lacuna é que o realizado não tem lugar próprio (J-13), e não que a Agenda devesse tê-lo.
- **O conteúdo de cada tela de operação.** Sorteio, corte, ocupação e convocação explicam bem o seu
  próprio recorte (P-03 a P-05). O que falta é o que vem antes e depois delas.
