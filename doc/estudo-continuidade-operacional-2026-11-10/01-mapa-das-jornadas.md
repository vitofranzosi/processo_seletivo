# Entrega A — Mapa das jornadas percorridas

Cada passo abaixo foi **praticado** no navegador, pelo Playwright, contra a `main` em `594d8494` (com
a 135 e a 136 já mergeadas), num banco descartável com os cenários da `134`. As capturas estão em
[`capturas/`](capturas/), com o prefixo da jornada (`a`, `b`, `c`, `d`, `e`). O caderno do percurso é
[`passeio/passeio.py`](passeio/passeio.py): cada chamada é um trecho da jornada, com a sessão da
identidade preservada entre os trechos.

**Convenção.** "Centro" é o Centro de Controle do Edital (`/gestao/editais/<id>/centro/`). "y" é a
altura, em px, em que o elemento aparece numa janela de 1440 × 900: abaixo de 900, está fora da
primeira dobra.

## Como as jornadas são de fato no GPS

O pedido descreve as jornadas em etapas genéricas. O GPS as conduz assim, e o mapa segue o que ele faz:

- **A — Sorteio.** O marco por sorteio não tem "conferir a relação" separado de "congelar": a tela
  mostra a relação projetada e o botão de congelar no mesmo bloco, por lista. A semente é **uma por
  marco**, para todas as listas. A ordem, o corte e a apuração não ficam na tela do sorteio: a ordem
  sorteada só aparece no corte, na classificação e no canal público. A publicação é de outro papel
  (Publicador), na tela de condução do marco.
- **B — Pontuação.** A avaliação é da Mesa do avaliador (`/gestao/minhas-etapas/…`), que não passa
  pelo Centro. A distribuição e a consolidação são da presidência, numa tela por Etapa. A ordem é
  emitida por lista; a publicação, pelo Publicador, por marco.
- **D — Vagas e convocação.** O corte e a apuração moram em telas próprias do marco. A convocação reúne
  vagas, gesto dos titulares, fila, aviso de pendências e chamadas praticadas numa tela só, de ~3.500 px.
- **E — Documentos.** A conferência é por convocação, numa tela de documentos. O desfecho (aceite,
  indeferimento) volta à tela da convocação. O candidato vê e reenvia pelo portal.
- **C — Recursos.** O candidato recorre pelo portal; o Julgador admite e decide numa tela por recurso;
  o efeito volta à presidência como "ordem sucessora".

## Os cenários usados

| Jornada | Cenário | Estado de partida | Papéis |
|---|---|---|---|
| A | C06 (rodadas 1, 2 e 3) | sorteio antes do congelamento | presidência, Publicador |
| B | C05, C04 | avaliação pendente; classificação por notas | avaliação, presidência, Publicador |
| D | C10, C09, C15 | convocação; resultado definitivo; vagas não preenchidas | presidência |
| E | C12, C11 | conferência documental; entrega documental | presidência, candidato |
| C | C08 | resultado preliminar e prazo recursal aberto | candidato, Julgador, presidência |

A rodada 1 do C06 foi gasta na **ordem errada** (semente antes da segunda lista), de propósito, para
observar a consequência; a 2 percorreu a ordem certa até a publicação; a 3 deu o HTML do "antes" dos
protótipos. As anteriores ficaram canceladas, como a restauração da `134` faz.

## Jornada A — Sorteio (C06)

| # | Passo | O que se viu | Captura |
|---|---|---|---|
| A1 | Centro, presidência | "Sua próxima ação · Fixar os participantes · no GPS: congelar a relação", com "Por que esta: destrava Obter a semente → Realizar o sorteio" | `a01` |
| A2 | Clique em "Abrir a tela" | Tela "Sorteio — Sorteio público", **no topo**. Antes do ato vêm: o método (8 campos e um resumo de 64 caracteres), a ocorrência e o botão verde **"Observar a ocorrência…" (y = 887)**. O primeiro "Publicar e congelar a relação" está em **y = 1681**. Cada lista abre com o aviso amarelo "Nenhum corte emitido neste recorte. Abrir o corte" | `a02` |
| A3 | Link da PPP no Centro (`?lista=`) | A mesma tela, no topo: o parâmetro não leva à lista | `a03` |
| A4 | Congelar a ampla | **Um clique, sem conferência.** Retorno: "Próximo nesta lista: **Observar a extração**" (link) e "Ainda neste marco: PPP — congelar a relação" (texto) | `a04`, `a04b` |
| A5 | Volta ao Centro | Três ações "suas", "**Todas já podem ser feitas … e o GPS não escolhe a ordem entre elas**", com "Obter a semente pública" listada **antes** de "Fixar os participantes · PPP" | `a05` |
| A6 | Seguir "Obter a semente" e observar | Um clique; a semente aparece. Retorno: "Próximo nesta lista: Congelar a relação" | `a06`, `a07` |
| A7 | Congelar a PPP depois da semente | **Aceito, sem aviso** | `a08` |
| A8 | Sortear a PPP | **Recusado**: a extração é anterior ao congelamento; a saída é Retificar, suceder a relação e observar de novo | `a09` |
| A9 | Sortear a ampla | Feito | `a10` |
| A10 | Centro | **Continua oferecendo "Realizar o sorteio · PPP" como ação sua** — um ato que a tela sempre recusará | `a11` |
| A11 | C06-R2, ordem certa: congelar as duas, observar, sortear as duas | Tudo aceito. O retorno do sorteio diz "Falta publicar a classificação" (sem dizer de quem) e "Próximo nesta lista: Distribuir 10 inscrições" (a Etapa de títulos, que o marco enumera). A tabela segue na **ordem da relação**: a ordem sorteada não aparece nesta tela. "Anular este sorteio" fica logo abaixo, em vermelho | `a12`–`a15` |
| A12 | Centro | Classificação **Concluída**; "Publicar o resultado" com outro papel; corte "aguarda" | `a16` |
| A13 | Centro, Publicador | "Sua próxima ação · Publicar o resultado" | `a17` |
| A14 | "Abrir a tela" | Tela de condução do marco, com um parágrafo sobre quem pode **ordenar, cortar e apurar** — que não é o ato do Publicador. Escolhe a natureza num `<select>` | `a18`, `a19` |
| A15 | Publicar | **"Confira antes de confirmar"**: recorte a recorte, "10 posições divulgadas", "3 posições divulgadas". Não diz que o preliminar **abre o prazo recursal**, nem até quando | `a20` |
| A16 | Confirmar e voltar | "2 feitos, 0 recusados"; o Centro mostra Resultado "Resultado preliminar · até 15/11" e Vagas "até 15/11" | `a21`, `a22` |
| A17 | Corte, presidência | Proposta da faixa, com "Recomendação: aguarde … até 15/11/2026" e "Emitir é irreversível". **Não praticado**: a recomendação manda esperar o prazo, e esperar é o comportamento certo | `a23` |

**A fonte pública (116 e 122).** Os cenários usam a **Fonte de demonstração**, que responde na hora.
A conferência na Caixa e a espera pela extração da Loteria Federal **não foram exercitadas**: não há
cenário com a fonte real, e o E2E contra a Caixa fica atrás de uma chave própria. O botão "Conferir na
Caixa" aparece mesmo com a fonte de demonstração; não foi clicado.

## Jornada B — Classificação por pontuação (C05, C04)

| # | Passo | O que se viu | Captura |
|---|---|---|---|
| B1 | Centro, `treino.avaliacao1` | "1 ação é sua" e, no mesmo cabeçalho, "**Seu papel aqui: Você acompanha este Edital sem ato a praticar nele**" | `b01` |
| B2 | "Abrir a tela" | A Mesa do avaliador, com 8 / 5 / 0 / 3 e a lista. Coerente | `b02` |
| B3 | Avaliar | Formulário com nota mínima e parecer; aviso de registro fora do período | `b03` |
| B4 | Concluir | Vai sozinho para a **próxima pendente**, com "Avaliação … concluída. Esta é a próxima pendente da sua Mesa" | `b04` |
| B5 | Concluir a última | "Não há mais inscrições pendentes suas nesta Etapa". Não diz o que vem depois, nem de quem | `b05` |
| B6 | Centro, presidência | "Consolidar 8 inscrições prontas" e "Distribuir 8 … Análise de títulos", paralelas | `b06` |
| B7 | Consolidar | Tela da Etapa → "Consolidar as 8 prontas" → **"Confira antes de consolidar"**, com a consequência de cada inscrição ("2 eliminadas, 6 habilitadas") | `b07`, `b08` |
| B8 | Confirmar | "8 consolidadas, 0 recusadas", entre os contadores; "Distribuir o que falta" continua abaixo, sem nada a distribuir | `b09` |
| B9 | Centro | "Distribuir 6 inscrições" na Análise de títulos: as 2 eliminadas saíram da conta | `b10` |
| B10 | Propor e confirmar a distribuição | Proposta inline ("6 atribuições … confira antes de confirmar"); o Centro passa a "Os avaliadores alocados: avaliar 6" | `b11`, `b12` |
| B11 | C04, Centro → "Classificar a lista" | Tela da lista **ampla** (a PPP é outro botão). Empate residual explicado; o desempate de 01 e 02 (26 pontos cada) **não é explicado**: Alice aparece 1ª, Bernardo 2º | `b14`, `b15` |
| B12 | Emitir a ordem | **"Confira antes de emitir"**, e depois "Próximo nesta lista: publicar o resultado, com quem publica resultado" e "Ainda neste marco: PPP — emitir a ordem" (texto, sem link). O parágrafo "Divulgá-lo não é ato seu…" aparece **duas vezes** | `b16`, `b17` |
| B13 | PPP e volta ao Centro | A tela da PPP explica a relação com a ordem da ampla. O Centro: nenhuma ação sua; "publicar" com o Publicador | `b18` |
| B14 | Publicador publica | Conferência e retorno como em A15–A16 | `b19` |

## Jornada D — Vagas, ocupação e convocação (C10, C09, C15)

| # | Passo | O que se viu | Captura |
|---|---|---|---|
| D1 | C10, Centro | "Convocar 3 titulares" ao lado de "Classificar a lista · PPP" e de "Publicar o resultado definitivo — aguarda até 15/11" | `d01` |
| D2 | "Convocar 3 titulares" | A convocação, no topo. Vagas: "3 Publicadas · 3 Efetivas · **3 Ocupadas · 0 A ocupar** · 0 Convocadas" — antes de qualquer chamada | `d02` |
| D3 | "Convocar as 3", com prazo e sem complemento | **Pratica e envia as 3 comunicações no clique.** A ajuda do campo dizia "antes de confirmar, você o verá como o candidato": a conferência só existe com complemento digitado | `d03` |
| D4 | Retorno e Centro | "Próximo nesta lista: publicar o resultado definitivo (aguarda: …)" com a frase inteira da espera. O Centro mostra "Resposta de 3 convocações · até 20/11". A tela segue oferecendo "Chamar uma pessoa da fila" com três suplentes "para vaga que vagou", sem vaga que tenha vagado | `d04` |
| D5 | C09, Centro | "**SUA VAGAS** · Definir até onde se chama" | `d05` |
| D6 | Emitir o corte | Aviso de irreversibilidade **na própria tela**, sem conferência; retorno "6 progridem" e "Próximo: Distribuir 6 inscrições" (Análise documental) | `d06`, `d07` |
| D7 | C15, Centro | "Convocar 2 titulares". Nada diz que **uma vaga ficará sem gente** | `d08` |
| D8 | Ocupação | "3 publicadas · 2 ocupadas · 1 a ocupar", e "Pedir a faixa seguinte com este déficit" com ninguém além da faixa; o parágrafo da "vaga acrescida", que não se aplica, aparece duas vezes | `d09` |
| D9 | Convocação | "Quem pode ser chamado para regularizar": a inabilitada | `d10` |

## Jornada E — Entrega e conferência documental (C12, C11)

| # | Passo | O que se viu | Captura |
|---|---|---|---|
| E1 | C12, Centro | "Conferir os documentos de 3 convocações" | `e01` |
| E2 | Clique | A convocação, **no topo**. "Chamadas praticadas" está em **y = 2151**; o primeiro "Documentos da convocação", em y = 2187 | `e02` |
| E3 | Documentos da 1ª | Cabeçalho com a pessoa e o vencimento, **sem Edital, Perfil nem lista** (só na migalha). Bom: "Aceite e regularização ainda não podem ser registrados: falta conferir…" | `e03` |
| E4 | "Conforme" sem abrir | Recusado depois do clique: "Abra o documento antes de conferi-lo como conforme" | `e04` |
| E5 | Abrir, conforme e pendente com motivo | "Conferência registrada." e "Próximo nesta lista: **Conferir os documentos de 2 convocações**" → leva ao topo da convocação, e não à próxima pessoa | `e05` |
| E6 | Centro | "1 **aguardam** documentos" | `e06` |
| E7 | Candidato C11-02, portal | A lista diz "Convocação aberta", sem "1 a corrigir". A convocação diz bem: "A corrigir: 1 · A enviar: 1", com o motivo e o prazo | `e07`, `e08` |
| E8 | Reenviar | "Recebemos … aguarda a conferência da comissão. Próxima tarefa: Comprovante de residência" | `e09` |
| E9 | Centro do C11 | "Conferir os documentos de 2 convocações" | `e10` |
| E10 | C12, segunda pessoa, tudo conforme | "Pronta para decidir" e "Próximo nesta lista: Registrar o desfecho de 1 convocação pronta" → **topo da convocação**; o desfecho dela está em **y = 3020** | `e11`, `e12` |
| E11 | Desfecho (aceite) | **Conferência do texto** ("veja o texto como o candidato o verá"), e depois "Desfecho registrado. A apuração seguinte … foi emitida no mesmo ato: 0 a ocupar" | `e13`, `e14` |
| E12 | Centro | "Resposta de 2 convocações" | `e15` |
| E13 | Pendência ao candidato | O "pendente" **não avisa** ninguém: `despachar_avisos` encontrou 0 avisos. O gesto "Avisar as pessoas com documento pendente" existe, na tela da convocação, entre a fila e as chamadas; o retorno da conferência não o menciona | — |

## Jornada C — Resultados e recursos (C08)

| # | Passo | O que se viu | Captura |
|---|---|---|---|
| C1 | Candidato 08, portal | "Eliminado … **O que fazer: Nada por enquanto.** Se você discordar…, pode recorrer até 15/11". O cronograma ainda mostra "Resultado final … 30/12/2026" | `c01` |
| C2 | Recorrer e interpor | Formulário curto; protocolo, situação e prazo na tela seguinte | `c02`, `c03` |
| C3 | Centro, Julgador | "Sua próxima ação · Decidir recursos (1)"; o definitivo "aguarda: há recurso pendente" | `c04` |
| C4 | "Abrir a tela" → recurso | O Julgador **não vê o resultado atacado** ("julgar não concede"); a instrução é da presidência, e o Centro não a anuncia como pré-requisito | `c05`, `c06` |
| C5 | Admitir e julgar (deferir, nota 6) | **Dois atos de um clique**, sem conferência. A tela mostra o sucessor "HABILITADA · 6"; não diz o que acontece depois, nem de quem | `c07`, `c08` |
| C6 | Centro, presidência | "Distribuir 1 inscrição" (títulos do reabilitado) e "emitir a ordem sucessora", **paralelas, "o GPS não escolhe a ordem"** | `c09` |
| C7 | Abrir a ordem sucessora | A prévia mostra o reabilitado "**Sem posição — sem pontuação nas Etapas enumeradas: Análise de títulos**". Emitir agora produziria uma ordem a suceder de novo. **Não praticado** | `c10` |
| C8 | Candidato depois | "Sua situação: Inscrição enviada"; Prova objetiva "Habilitada · 6", com a nota do recurso | `c11` |

## O retorno ao Centro

- **Nenhuma tela operacional liga ao Centro.** A migalha é "GPS › Processos › Processo › Edital ›
  Tela", e o "Edital" leva ao detalhe atual, onde o link "Abrir o Centro de Controle do Edital (em
  validação)" está em y = 169 (`x01`). São **dois cliques**, e é coerente com a D-2 em aberto: o Centro
  ainda mora numa rota própria.
- **A Mesa do avaliador** ("Minhas Etapas › Minha Mesa") não passa pelo Edital nem pelo Centro.
- **Em todos os 18 retornos ao Centro, o estado novo apareceu** — com a data da espera quando havia.

## Inventário das telas percorridas

Severidade: **crítica** (pode levar a ato irreversível errado), **alta** (rompe a jornada ou exige
procurar), **média** (atrito ou ambiguidade), **baixa** (texto). Só as telas percorridas.

| Jornada | Operação | Tela ou rota | Objetivo | Entrada | Pré-requisitos | Interações | Feedback | Retorno | Problemas | Sev. | Oportunidade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| todas | Orientar | Centro `/editais/<id>/centro/` | saber o estado e a próxima providência | detalhe do Edital (link em y=169) | Edital publicado | ler; seguir providência | — | ponto de retorno | providência leva ao topo da tela; "o GPS não escolhe a ordem" é falso em A e C; contradição "seu papel" × "1 ação é sua" (avaliador); "SUA VAGAS", "1 aguardam" | alta | âncora no destino (M-02); M-10, M-11; F-1, F-2 |
| A | Congelar (fixar) | `…/marcos/<m>/sorteio` | fixar quem participa, por lista | Centro "Abrir a tela" | inscrições encerradas | "Publicar e congelar a relação" | verde + "Próximo nesta lista" | migalha → detalhe | ato a 1.681 px, sob o método e a observação; um clique, sem conferência; "Nenhum corte emitido" antes do sorteio; "universo comprometido"; "Ainda neste marco" sem link | crítica | M-06, M-03, M-07, M-12; D-5 |
| A | Observar a semente | idem | registrar a extração | Centro ou retorno | uma relação congelada | "Observar a ocorrência…" (botão primário) | números da ocorrência | idem | oferecida (e primária) com lista por fixar; o retorno do 1º congelamento aponta para ela | crítica | M-06; D-5; F-1 |
| A | Sortear | idem | produzir a ordem | idem | relação congelada e semente | "Realizar o sorteio" | semente e manifesto | idem | um clique; a ordem sorteada não aparece; "Falta publicar a classificação" sem dizer de quem; "Anular" logo abaixo | alta | M-13, M-15, M-12 |
| A, B | Publicar o resultado | `…/marcos/<m>/conducao` → `/publicar` | divulgar a ordem | Centro (Publicador) | ordem emitida | natureza, autoridade, conferir, confirmar | "2 feitos, 0 recusados" | — | parágrafo de permissões alheio ao Publicador; a conferência não diz que abre o prazo recursal | média | M-14 |
| A, D | Emitir o corte | `…/marcos/<m>/corte` | fixar até onde se chama | Centro | ordem; recomendação de prazo | "Emitir corte" | "6 progridem" + próximo | — | um clique (aviso inline) | média | M-12 |
| B | Avaliar | `/minhas-etapas/<e>/<etapa>/inscricoes/<i>` | registrar nota e parecer | Centro ou Minhas Etapas | alocação | nota, parecer, concluir | próxima pendente | Mesa | fim da Mesa não diz o que vem | baixa | M-16 |
| B | Consolidar | `/editais/<id>/distribuicao/<etapa>` → `/consolidar` | transformar avaliações em Resultado | Centro | avaliações concluídas | consolidar, conferir, confirmar | "8 consolidadas, 0 recusadas" | migalha → Alocação | feedback sem efeito nem próximo | baixa | M-17 |
| B | Distribuir | idem | atribuir a avaliadores | Centro | alocação | escolher pessoas, propor, confirmar | proposta inline | — | — | — | preservar |
| B | Emitir a ordem | `…/marcos/<m>` (`?lista=`) | classificar a lista | Centro | Etapas consolidadas | emitir, conferir | ordem + próximo | — | desempate que separou 01/02 não explicado; parágrafo duplicado; "Ainda neste marco" sem link | média | M-07; parágrafo único |
| D | Convocar titulares | `…/marcos/<m>/convocacao` | chamar quem a apuração indica | Centro | apuração | prazo, complemento, convocar | "3 convocações … 3 comunicações enviadas" | — | **pratica e comunica no clique**; ajuda promete conferência; "3 Ocupadas, 0 Convocadas"; fila de suplentes oferecida sem vaga vaga | crítica | M-04, M-09, M-19 |
| D | Ocupação | `…/marcos/<m>/ocupacao` | ver vagas e déficit | Centro (telas do marco) | apuração | ler; pedir faixa | — | — | "faixa seguinte" sem ninguém além; parágrafo da vaga acrescida repetido | média | F-5; texto |
| E | Conferir documentos | `…/convocacao/<c>/documentos` | conferir cada item | convocação (y=2187) | documento aberto | abrir, conforme/pendente, motivo | "Conferência registrada" + próximo | "Voltar à convocação" | sem Edital/Perfil/lista no alto; o próximo leva ao topo da convocação; pendente não aponta o "Avisar" | alta | M-02, M-08, M-07 |
| E | Desfecho | `…/convocacao` (`#chamada-N`) | aceitar ou indeferir | convocação (y=3020) | itens conformes | espécie, fundamento, conferir o texto | "Desfecho registrado… 0 a ocupar" | — | longe do lugar da conferência | média | M-08 |
| E | Reenviar (candidato) | `/selecoes/inscricoes/<i>/convocacao` | corrigir o pendente | e-mail / lista | pendência | arquivo, enviar | "Recebemos… Próxima tarefa" | acompanhamento | a lista não diz "1 a corrigir" | média | M-20 |
| C | Recorrer (candidato) | `/selecoes/inscricoes/<i>/recorrer` | contestar o resultado | acompanhamento | prazo aberto | objeto, razão | protocolo | acompanhamento | "Nada por enquanto" ao lado de "pode recorrer" | baixa | M-20 |
| C | Admitir e julgar | `/gestao/recursos/<r>` | decidir | Centro → lista de recursos | — | motivo; espécie, nota, motivação | sucessor na tela | link do Edital | atos de um clique; o Julgador não vê o resultado sem instrução; nada diz o efeito a jusante | alta | M-12, M-18 |
| C | Ordem sucessora | `…/marcos/<m>` | reordenar após o recurso | Centro | Etapas do reabilitado | — | prévia "sem posição" | — | oferecida em paralelo com a avaliação que lhe falta | crítica | F-2 |
