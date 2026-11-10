# Entrega B — Diagnóstico de continuidade

## A resposta

**O GPS é coerente no estado, e se rompe na passagem.**

- **No estado, sim.** O Centro e o retorno de cada tela ("Próximo nesta lista") vêm da mesma
  derivação (127). Em todos os 18 retornos ao Centro, o estado novo apareceu na hora: com a data da
  espera ("até 15/11", "até 20/11"), com o papel de quem age e sem a providência que acabou de ser feita.
  Nenhuma tela mostrou um estado e o Centro outro.
- **Na passagem, não.** A experiência se rompe em quatro pontos, sempre os mesmos, em todas as jornadas:
  1. **na chegada:** a providência leva ao topo da tela, e não ao lugar do ato;
  2. **no ato irreversível:** uns têm conferência, outros praticam no clique;
  3. **no retorno:** a tela diz o que fazer em seguida, mas não leva até lá nem de volta ao Centro;
  4. **no próprio Centro, duas vezes:** ele afirma que a ordem entre as ações é livre quando não é.

Os três primeiros são de apresentação. O quarto é de derivação, e virou achado funcional
([06](06-achados-funcionais.md)).

## A continuidade, passo a passo

Os sete momentos da pergunta central, por jornada. ✓ coerente · ◐ funciona com atrito · ✗ rompe.

| Momento | A — Sorteio | B — Pontuação | D — Convocação | E — Documentos | C — Recursos |
|---|---|---|---|---|---|
| 1. O Centro mostra a providência | ✓ com "Por que esta" | ◐ avaliador: "sem ato a praticar" e "1 ação é sua" juntos | ✓ | ✓ | ✓ Julgador |
| 2. O clique leva ao ato | ✗ ato a 1.681 px, sob o método e a observação | ✓ Mesa; ◐ consolidação e ordem | ◐ gesto na dobra; contagens enganam | ✗ chamadas a 2.151 px; desfecho a 3.020 px | ◐ lista → recurso, sem o resultado atacado |
| 3. A tela diz o objetivo na língua do Centro | ✗ "universo comprometido", "Todos os inscritos do recorte de vaga" | ✓ | ◐ "Ocupadas" antes de convocar | ◐ sem Edital, Perfil nem lista | ✓ |
| 4. Prevenção e consequência antes do ato | ✗ congelar, observar e sortear num clique; a observação é o botão primário com lista por fixar | ✓ conferências exemplares | ✗ convocar e comunicar num clique; corte com aviso inline | ✓ "abra antes de conferir"; ✓ texto do desfecho conferido | ✗ admitir e julgar num clique |
| 5. O resultado se entende | ◐ a ordem sorteada não aparece | ◐ "8 consolidadas, 0 recusadas" sem o efeito | ✓ | ✓ | ◐ sucessor na tela, sem o efeito a jusante |
| 6. A próxima providência é dita **e alcançável** | ✗ aponta "Observar" com lista por fixar | ◐ dita; "Ainda neste marco" sem link | ◐ dita, longa | ◐ dita; leva ao topo da convocação | ✗ nada no Julgador |
| 7. Volta ao Centro e reconhece o estado | ◐ 2 cliques; estado ✓ | ◐ 2 cliques; estado ✓ | ◐ 2 cliques; estado ✓ | ◐ 2 cliques; estado ✓ | ✗ o Centro oferece a ordem sucessora antes da hora (F-2) |

## Onde a experiência se rompe, exatamente

### R-1. Chegada: a providência não leva ao lugar do ato (recorrente)

O Centro sabe a lista, a pessoa e o ato. A URL da providência leva só à tela, e a tela abre no topo:

| Providência no Centro | Onde o ato está na tela de destino |
|---|---|
| Fixar os participantes (C06) | primeiro "Publicar e congelar", y = 1681 |
| Fixar os participantes · PPP (`?lista=`) | o parâmetro não rola a tela; a PPP está mais abaixo ainda |
| Conferir os documentos de 3 convocações (C12) | "Chamadas praticadas", y = 2151 |
| Registrar o desfecho (retorno da conferência, C12) | desfecho da pessoa, y = 3020 |

**Ponto de quebra:** `andamento.Celula.url` aponta para a tela, sem fragmento. As telas já têm os
alvos (`#chamadas`, `#chamada-N`, `#titulo-recortes`); faltam os ids por lista nos recortes do sorteio.

### R-2. Ato irreversível: a conferência existe para uns, e não para outros (recorrente)

O GPS já tem a peça certa: "Confira antes de…", com o que será praticado e o que fica de fora.
Ela aparece em 4 dos 11 tipos de ato irreversível praticados no percurso:

| Com conferência antes | Só um aviso na tela | Nada além do rótulo do botão |
|---|---|---|
| publicar o resultado · consolidar · emitir a ordem · desfecho (texto ao candidato) | emitir o corte · convocar os titulares (sem complemento) | congelar a relação · observar a ocorrência · realizar o sorteio · admitir o recurso · julgar o recurso |

O caso mais grave é **convocar**: o ato sai para fora do GPS — a mensagem chega à pessoa — e a ajuda do
campo promete "antes de confirmar, você o verá como o candidato", o que só acontece com complemento
digitado (125, FR-3993). O segundo caso grave é o **sorteio**: congelar e observar são irreversíveis, e
a ordem entre os dois decide se a lista poderá ser sorteada.

### R-3. Retorno: o próximo é dito, mas não alcançado (recorrente)

O bloco "Próximo nesta lista" (127, FR-4090; `_proximo_nesta_lista.html`) está em seis telas: sorteio,
ordem, corte, ocupação, convocação e documentos. É a melhor peça de continuidade do sistema, e é onde
o ganho de uma mudança se multiplica. Hoje ele:
- **não volta ao Centro**, e nenhuma outra peça das telas operacionais volta;
- **não liga o "Ainda neste marco"**, que é texto puro;
- **leva ao topo** da tela do próximo ato, quando ele é em outra tela, e não ao item. Compare com a Mesa
  do avaliador, que leva à **próxima pendente**;
- **escolhe o primeiro item em aberto desta lista**, e por isso, no sorteio, aponta "Observar a
  extração" quando a outra lista ainda não foi fixada (A4). Esse é o ponto que toca a D-5.

### R-4. O Centro diz "o GPS não escolhe a ordem" quando ela importa (crítica pontual, duas vezes)

- **A:** depois de fixar a ampla, "Obter a semente" e "Fixar · PPP" aparecem como paralelas. Feita a
  semente primeiro, a PPP é congelada **sem aviso**, o sorteio dela é recusado, e a saída é uma
  Retificação. Depois disso, o Centro **continua oferecendo** "Realizar o sorteio · PPP" (F-1).
- **C:** depois do deferimento que reabilita, "Distribuir 1 inscrição" e "emitir a ordem sucessora"
  aparecem como paralelas. A ordem emitida antes da avaliação deixaria o reabilitado sem posição (F-2).

O texto do Centro é fiel à derivação: o defeito está nela, e não na página da 136.

### R-5. Vocabulário: o Centro e a tela falam línguas diferentes (recorrente, média)

| Centro (136) | Tela operacional |
|---|---|
| Fixar os participantes · no GPS: congelar a relação | "Publicar e congelar a relação"; "Universo ainda não comprometido" |
| Obter a semente pública · no GPS: observar a extração | "Observar a ocorrência 806003106 na fonte" |
| Ampla concorrência | "Todos os inscritos do recorte de vaga (sem lista de concorrência)" e "Ampla concorrência (linha geral do quadro)" |
| Definir até onde se chama | "Corte e progressão" |
| Distribuir as vagas entre as listas | "Ocupação de vagas"; "3 Ocupadas" antes de qualquer convocação |

A ponte "no GPS: …" do Centro resolve a ida. Falta a volta: a tela não ecoa o nome que trouxe a pessoa.

### R-6. Transições entre papéis (média)

- **Avaliador → presidência:** a Mesa termina em "Não há mais inscrições pendentes"; a consolidação é
  da presidência, e nada o diz. O Centro da presidência mostra bem o que chegou.
- **Presidência → Julgador → presidência:** o Julgador recebe "Decidir recursos" como próxima ação sem
  saber que a instrução é da presidência; depois de decidir, nada diz que a ordem será sucedida. O
  Centro da presidência mostra o efeito, mas na ordem errada (R-4).
- **Comissão → candidato (pendência):** o "pendente" não avisa a pessoa. O gesto "Avisar as pessoas com
  documento pendente" existe na convocação, mas o retorno da conferência não o aponta. O candidato que
  entra vê tudo com clareza; o que não entra, não sabe. (A QI-7 da 115 já tratou do aviso automático, e
  ele espera decisão institucional — ver o [achado de 05/11](../achado-comunicacao-ao-convocado-2026-11-05.md).)

## O que já funciona, e deve ser preservado

| # | O quê | Onde | Por que preservar |
|---|---|---|---|
| P-1 | **O estado do Centro sempre bate com o da tela** | todas as jornadas | é a base de tudo; qualquer melhoria tem de continuar lendo a mesma derivação |
| P-2 | **As conferências "Confira antes de…"** | publicar, consolidar, ordem, desfecho | o modelo certo: recorte a recorte, consequência por inscrição, texto como o candidato verá. É o que se replica, não o que se redesenha |
| P-3 | **A Mesa do avaliador** | B | próxima pendente automática, retorno à Mesa, mensagem de fim. É o padrão de "próximo item" que falta nas outras telas |
| P-4 | **O bloco "Próximo nesta lista"** | 6 telas | a peça de continuidade; o problema é o que ele não faz, e não o que faz |
| P-5 | **"Por que esta" e "Esperam por ela"** no Centro | A, B | explicou a dependência do sorteio melhor que a tela do sorteio |
| P-6 | **Recomendações com data, que não bloqueiam** | corte ("aguarde até 15/11 … emitir agora continua possível") | consequência dita, decisão com a pessoa |
| P-7 | **Recusas que dizem a saída** | sorteio recusado (os 3 passos), "abra antes de conferir", aceite antes de conformar | o operador nunca ficou num beco sem explicação |
| P-8 | **"Abrir esta tela não pratica nada"** | condução, convocação | tira o medo de clicar para ver |
| P-9 | **Quem pode, quando não é você** | "peça a alguém com a permissão…" | a separação de papéis é ensinada no lugar |
| P-10 | **O portal da convocação** | E, candidato | andamento, motivo da pendência, prazo e "próxima tarefa" |
| P-11 | **Nenhuma violação de CSP** | todas as telas percorridas | — |

## O que não está aqui

- **A Loteria Federal.** A conferência na Caixa e a espera pela extração real não foram exercitadas.
- **Duas listas com gente nas duas.** Nos cenários com pontuação, a PPP não tem concorrente; a
  continuidade entre duas listas com ordem e convocação próprias foi vista só no sorteio.
- **O celular.** As jornadas foram feitas a 1.440 px. A 375 px só se mediram os protótipos; ali, a tela
  real do sorteio depois de congelar **já tem rolagem horizontal** (antes e depois do protótipo).
- **A instrução do recurso pela presidência**, e se o Centro dela a anuncia: não verificado.
