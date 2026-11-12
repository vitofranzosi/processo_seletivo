# Cenários de treinamento — guia da equipe de seleção

Este guia é para quem vai **usar** o GPS de homologação para treinar e avaliar as telas. Não é
preciso saber nada de programação.

## O que são os cenários

São **Processos Seletivos fictícios**, já preparados pelo próprio GPS e parados em pontos
diferentes do certame: um com inscrições abertas, outro pronto para sortear, outro com convocados
entregando documentos, e assim por diante. Você não precisa percorrer o certame inteiro para
treinar uma etapa: abre o cenário e faz o exercício.

Tudo nos cenários é inventado: pessoas, CPFs, e-mails, notas e documentos. Os nomes levam a palavra
**Treinamento**, e os documentos dizem *"TREINAMENTO — DADO FICTÍCIO, SEM VALOR LEGAL"*. Nada do
que você fizer neles chega a um candidato de verdade.

## Como reconhecer um cenário

Na lista de Processos Seletivos, aba **Em andamento**, os cenários aparecem assim:

> **SIM-TREINAMENTO-007** — Sorteio pronto para execução (FICTÍCIO)

O número depois de `SIM-TREINAMENTO-` é o número do cenário (C07). O Edital de cada um se chama
`SIM07/2026`. Use a busca da lista com **SIM-TREINAMENTO** para ver só os cenários.

Se um cenário já foi restaurado, a versão nova termina em `-R2`, `-R3`… e a anterior fica na aba
**Cancelados**, com tudo o que foi feito nela.

## Como entrar

1. Abra o GPS e clique em **Área de gestão**.
2. Escolha **Acessar ambiente de demonstração**.
3. Escolha com quem entrar:
   - para os exercícios da **comissão** (classificar, sortear, convocar, conferir documentos),
     escolha no grupo **Comissões** a identidade `treino.presidencia` (presidência),
     `treino.avaliacao1` (avaliação) ou `treino.avaliacao2` (membro alocado à conferência dos
     documentos, no C12);
   - para os demais, escolha em **Responsabilidades da unidade** o papel pedido no exercício
     (Gestor, Elaborador, Homologador, Publicador, Julgador de recursos). Se preferir que a
     auditoria registre o seu nome, use o campo **Nome na auditoria** e marque o papel.

   - para os exercícios do **setor da formalização** (C16 e C17), escreva `treino.formalizacao`
     no campo **Nome na auditoria** e marque o papel **Formalização**. Ela não aparece na lista
     de sugestões, de propósito: é a pessoa fictícia do setor, que o cenário já traz com o papel
     concedido na unidade.

**Para chegar ao lugar do exercício**, a presidência começa em **Minhas atividades**. Em **Para fazer
agora** estão os atos que são dela em todos os Editais que preside, cada um com o Edital, o Perfil e o
link direto para a tela do ato: não é preciso abrir Edital por Edital. A seção **Em espera nos seus
Editais**, recolhida, diz o que aguarda uma data, e de onde a data vem. Quem avalia encontra ali a
avaliação pendente e as Etapas, e quem foi alocado à conferência encontra **Conferir os documentos**,
marcado **pela alocação**. Os demais papéis começam em **Processos Seletivos**: o Julgador de recursos
encontra os recursos a decidir no quadro **Ações disponíveis para você**, no alto da lista. Para ver tudo o
que está em aberto num Edital, de todos os papéis, abra o Processo e, nele, o Edital (`SIM07/2026`,
por exemplo): no alto da página, o quadro **O que fazer agora** mostra as providências e marca com
**SUA** as que cabem a você.

Cada exercício diz **quem** faz cada passo. Quando um passo é de outro papel, saia e entre de novo
com o papel indicado: o GPS separa quem elabora, quem homologa e quem publica, e é parte do
treinamento perceber essa separação.

**Exercícios no portal do candidato** (C02, C08, C11): o candidato entra com um código enviado ao
e-mail. Os candidatos dos cenários têm e-mails que não existem. Para se inscrever, use o seu próprio
e-mail (C02). Para agir como um candidato já inscrito (C08, C11):

1. No portal, peça o código com o e-mail do candidato. Ele segue o padrão
   `<unidade>-<cenário>r<rodada>p<número>@treinamento.exemplo.test` — o candidato 02 do C11, no
   Cefor, na primeira rodada, é `cefor-c11r1p02@treinamento.exemplo.test`. O número é o do nome
   ("Bernardo Treinamento C11-02"), e a rodada é a do Processo (`-R2` é a rodada 2).
2. Abra a caixa de entrada do ambiente, o **mailpit**, na porta 8025 do servidor de homologação. O
   código está na mensagem mais recente para aquele e-mail.
3. Digite o código no portal: você está agindo como o candidato.

## Quem faz o quê nos cenários

Num certame real, o trabalho de um Edital se reparte entre pessoas diferentes, cada uma por uma
razão diferente. Os cenários trazem cada uma dessas frentes com alguém nela, para que se possa ver
quem cobre o quê:

| Frente | Por que a pessoa está nela | Cenário | Identidade |
|---|---|---|---|
| Conduzir o certame | preside a comissão do Processo | C04 a C12, C14 a C17 | `treino.presidencia` |
| Avaliar uma Etapa | membro alocado à Etapa | C05 | `treino.avaliacao1` |
| Conferir os documentos da convocação | membro **alocado à conferência** — sem presidir | C12 | `treino.avaliacao2` |
| Receber os documentos para formalizar | **designada** para o Edital, sem integrar a comissão | C16 (designada), C17 (a designar) | `treino.formalizacao` |
| Decidir recursos | papel Julgador de recursos da unidade | C08 (um recurso admitido) | Julgador de recursos |
| Publicar resultado, elaborar, homologar | papel da unidade | C01, C04, C13 | Publicador, Elaborador, Homologador |

Quem foi alocado à conferência **só confere**: a decisão de cada convocação (o desfecho) continua
com a presidência. A pessoa designada para a formalização não vê nada da comissão: só os documentos
das pessoas aptas do Edital em que foi designada.

## O que observar em todo exercício

Anote, enquanto faz:

- Foi fácil **encontrar** onde fazer?
- As **palavras** da tela ficaram claras?
- O sistema **explicou** o que ia acontecer antes de você confirmar?
- As **mensagens de erro ou de impedimento** disseram o que fazer?
- O **resultado** foi fácil de entender?
- Ficou claro **qual é o próximo passo** e de quem ele é?

---

## C01 — Elaboração de edital

**Objetivo:** completar um Edital em elaboração e levá-lo à publicação.

**Você começa com:** o Edital `SIM01` em elaboração, com Perfil, vagas, cotas, Cronograma e Etapas
já preenchidos. Faltam os **Documentos Exigidos**.

**Quem faz:** Elaborador → Homologador → Publicador.

**Seu desafio:**

1. Como **Elaborador**, abra o Edital `SIM01` e vá à etapa de Documentos Exigidos.
2. Acrescente pelo menos um documento (por exemplo, "Documento de identificação com foto").
3. Revise o Edital inteiro e envie para homologação.
4. Como **Homologador**, confira e homologue.
5. Como **Publicador**, publique.

**Resultado esperado:** Edital publicado, com o documento oficial em PDF.

**Validade:** 7 dias depois da carga (as inscrições começam nesse dia).

## C02 — Inscrições abertas

**Objetivo:** viver a jornada de quem se inscreve e acompanhar as inscrições na gestão.

**Você começa com:** o Edital `SIM02` publicado, inscrições abertas e 3 inscrições já enviadas.

**Quem faz:** você como candidato (portal) e como Gestor.

**Seu desafio:**

1. Na página pública do Edital, leia o Perfil e as vagas.
2. Inscreva-se com o **seu** e-mail; anexe um PDF qualquer como documento de identificação.
3. Envie a inscrição e guarde o protocolo.
4. Como **Gestor**, encontre a sua inscrição entre as do Edital.

**Resultado esperado:** inscrição enviada, com protocolo e comprovante.

**Validade:** 30 dias.

## C03 — Inscrições encerradas

**Objetivo:** organizar o certame depois do fim das inscrições.

**Você começa com:** o Edital `SIM03` com 8 inscrições (2 na cota) e as inscrições encerradas por
Retificação. Ainda não há comissão.

**Quem faz:** Gestor.

**Seu desafio:**

1. Como **Gestor**, consulte os inscritos e confira quem concorre na cota.
2. Constitua a comissão do Processo: uma presidência e pelo menos um membro.
3. Aloque os membros nas Etapas.

**Resultado esperado:** comissão pronta para distribuir as avaliações.

## C04 — Classificação por notas

**Objetivo:** emitir a ordem classificatória e conferir empates, desempate e listas.

**Você começa com:** o Edital `SIM04`, 10 inscritos (2 na cota), prova e títulos já avaliados. As
notas foram escolhidas para criar situações:

| Candidato | Prova (peso 2) | Títulos (peso 1) | O que observar |
|---|---|---|---|
| 01 e 02 | 9,0 e 8,5 | 8,0 e 9,0 | mesmo total (26); o desempate pela prova põe 01 na frente |
| 03 e 04 | 8,0 | 7,0 | tudo igual: ficam empatados na mesma posição |
| 08 | 5,0 | — | eliminado na prova (mínima 6,0) |
| 09 e 10 | 7,0 e 6,0 | 8,0 e 6,0 | concorrem na cota |

São 4 vagas: 3 na ampla concorrência e 1 na cota.

**Quem faz:** presidência da comissão (`treino.presidencia`) → Publicador.

**Seu desafio:**

1. Como `treino.presidencia`, abra a classificação do marco "Classificação final".
2. Confira a prévia: posições, empate, desempate, quem ficou de fora e por quê.
3. Emita a ordem da ampla concorrência e a da cota.
4. Como **Publicador**, divulgue o resultado preliminar.

**Resultado esperado:** ordem emitida por lista e resultado preliminar público.

## C05 — Avaliação pendente

**Objetivo:** registrar avaliações e fechar uma Etapa.

**Você começa com:** o Edital `SIM05`, 8 inscritos, a prova distribuída para `treino.avaliacao1`:
3 avaliações concluídas e 5 pendentes.

**Quem faz:** avaliação (`treino.avaliacao1`) → presidência (`treino.presidencia`).

**Seu desafio:**

1. Como `treino.avaliacao1`, abra as suas avaliações pendentes.
2. Registre as notas das 5 pendentes; dê a alguém uma nota abaixo de 6,0.
3. Como `treino.presidencia`, consolide a prova.

**Resultado esperado:** prova consolidada; quem ficou abaixo de 6,0 aparece eliminado.

## C06 — Sorteio antes do congelamento

**Objetivo:** entender a preparação do sorteio e congelar as relações de participantes.

**Você começa com:** o Edital `SIM06`, de curso técnico, com 10 inscrições para 4 vagas — 3 na
ampla concorrência e 1 na cota PPP — e as inscrições encerradas. Três inscritos declararam a cota.
Eles não anexaram comprovante: a autodeclaração é pedida na convocação, depois do sorteio.

**Quem faz:** presidência (`treino.presidencia`).

**Seu desafio:**

1. Como `treino.presidencia`, abra o Edital `SIM06/2026`; em **O que fazer agora**, siga a
   providência do sorteio até a tela **Sorteio — Sorteio público**.
2. Leia o método declarado no Edital. Em **Recortes deste marco** há duas listas: **Todos os
   inscritos** (a ampla concorrência, que inclui os cotistas) e **Pessoas pretas, pardas e
   indígenas (PPP)**.
3. Congele as duas, uma de cada vez, em **Publicar e congelar a relação**. **Congele as duas antes
   de observar a ocorrência**: uma relação congelada depois de conhecida a semente é recusada.

**Resultado esperado:** duas relações congeladas — 10 participantes na ampla concorrência e 3 na
cota —, cada uma com a sua lista pública.

## C07 — Executando um sorteio

**Objetivo:** realizar e conferir os sorteios da ampla concorrência e da cota.

**Você começa com:** o Edital `SIM07`, inscrições encerradas e as duas relações **já congeladas**:
10 participantes na ampla concorrência e 3 na cota PPP. Falta observar a ocorrência e sortear.

**Quem faz:** presidência (`treino.presidencia`).

**Seu desafio:**

1. Como `treino.presidencia`, abra o Edital `SIM07/2026`. Em **O que fazer agora** aparece
   **SUA — Observar a extração**; siga até a tela **Sorteio — Sorteio público**.
2. Confira o método (a fonte é a **Fonte de demonstração**) e as duas relações congeladas. Repare
   que os três cotistas aparecem nas duas, com um número diferente em cada uma.
3. Clique em **Observar a ocorrência … na fonte** — no Cefor, a primeira rodada do C07 usa o
   concurso 807001106; cada rodada e cada unidade têm o seu. A ocorrência é **uma só** para as duas
   listas.
4. Clique em **Realizar o sorteio** na ampla concorrência e, depois, no da cota PPP.
5. Leia o quadro **Sorteio realizado** de cada lista: a semente é a mesma, e os manifestos são
   diferentes. Abra **Verificar no canal público**.

**Resultado esperado:** dois sorteios realizados — a ordem dos 10 participantes da ampla e a dos 3
da cota —, com manifesto e página de verificação cada um. A comprovação da cota fica para a
convocação, como no certame real.

> **A fonte de demonstração e a Caixa.** Aqui a observação vale na hora, e por isso dá para congelar
> e sortear no mesmo dia. Com a Loteria Federal, que publica só a data da extração, a relação
> precisa ser congelada **num dia anterior** ao da extração.

> **Uma providência a mais.** O quadro "O que fazer agora" também lista *Distribuir 10 inscrições
> … — Análise de títulos*: é a Etapa que o marco de sorteio deste modelo enumera. O sorteio não
> depende dela, e o exercício pode ignorá-la. Anote se a presença dela confundiu você.

> **Por que não é preciso esperar a Loteria:** em treinamento, o sorteio usa a **Fonte de
> demonstração**, que responde na hora. O nome dela aparece no Edital e no comprovante do sorteio.
> Num certame real, a fonte é a Loteria Federal, e o sorteio só acontece depois da extração.

## C08 — Resultado preliminar e recursos

**Objetivo:** recorrer de um resultado e julgar o recurso.

**Você começa com:** o Edital `SIM08`, resultado preliminar divulgado e o prazo de recurso de 5
dias aberto. O candidato 08 foi eliminado na prova. E **já há um recurso**: a candidata 03, empatada
com o 04, pediu a revisão da nota de títulos, e o recurso dela já foi **admitido** — está à espera
da decisão.

**Quem faz:** Julgador de recursos; candidato (portal) → Julgador de recursos → presidência.

**Seu desafio:**

1. Como **Julgador de recursos**, veja no alto da lista de Processos, em **Ações disponíveis para
   você**, *Recursos do Edital SIM08/2026 — Decidir recursos (1)*. Abra e decida o recurso da 03.
2. Como candidato 08 (código no mailpit), recorra do resultado com uma fundamentação.
3. Como **Julgador de recursos**, aprecie a admissibilidade do recurso do 08 e decida-o.
4. Como `treino.presidencia`, cumpra a decisão, se algum recurso for deferido.

**Resultado esperado:** recursos julgados; se deferido algum, nova ordem.

**Repare:** enquanto houver recurso sem decisão, o resultado definitivo **espera por ele**, e não só
pelo fim do prazo. Abra o Edital como `treino.presidencia` antes e depois de decidir o recurso da 03
e compare o que o quadro **O que fazer agora** diz sobre o definitivo.

**Validade:** 5 dias (a janela de recurso).

## C09 — Resultado definitivo

**Objetivo:** examinar um resultado definitivo e preparar a convocação.

**Você começa com:** o Edital `SIM09`, 6 inscritos e resultado **definitivo** divulgado. O marco
deste Edital não admite recurso, e por isso o definitivo veio direto.

**Quem faz:** presidência (`treino.presidencia`).

**Seu desafio:**

1. Leia o resultado definitivo como o público lê.
2. Como `treino.presidencia`, conclua a Etapa "Análise documental" (habilitar ou não cada um).
3. Na tela do corte, clique em "Conferir antes de emitir", leia a faixa na conferência — quem
   progride, quem fica fora e por quê — e só então emita o corte. Depois, apure a ocupação das vagas.

**Resultado esperado:** apuração emitida, pronta para convocar.

## C10 — Convocação

**Objetivo:** convocar candidatos para as vagas.

**Você começa com:** o Edital `SIM10`, 6 candidatos habilitados, faixa de corte e apuração
emitidas, ninguém convocado.

**Quem faz:** presidência (`treino.presidencia`).

**Seu desafio:**

1. Abra a convocação do marco "Classificação final".
2. Em "Chamar uma pessoa da fila", escolha a primeira pessoa, informe o prazo e clique em "Conferir
   antes de convocar". Leia a conferência — a espécie, o fundamento, o e-mail e o prazo — e só então
   confirme. Nada é gravado nem enviado antes da confirmação.
3. Confira, na tela da convocação, que a comunicação saiu no mesmo ato da confirmação.
4. Confira a lista de documentos pedida a ela. A autodeclaração étnico-racial é só da cota: para
   quem concorre na ampla, ela não aparece na lista.

**Resultado esperado:** convocação praticada e comunicada.

## C11 — Entrega documental

**Objetivo:** viver a entrega dos documentos da convocação.

**Você começa com:** o Edital `SIM11`, 3 convocados:

| Convocado | Situação |
|---|---|
| 01 | não entregou nada |
| 02 | entregou o diploma, que voltou como **pendente** ("arquivo ilegível") |
| 03 | entregou tudo; aguarda conferência |

**Quem faz:** candidato (portal) → presidência (`treino.presidencia`).

**Seu desafio:**

1. Como `treino.presidencia`, abra a convocação do Edital `SIM11/2026` e, em cada convocado,
   **Documentos**. O 02 mostra o diploma **Pendente** e a residência **A apresentar**.
2. Como candidato 02 (código no mailpit), leia a pendência e envie o diploma de novo.
3. Como `treino.presidencia`, confira os documentos do 03.

**Resultado esperado:** itens entregues e conferidos.

**Validade:** 30 dias (o prazo da convocação).

## C12 — Conferência documental

**Objetivo:** conferir documentos, um a um, e decidir cada convocação.

**Você começa com:** o Edital `SIM12`, 3 convocados com diploma e comprovante de residência
entregues e **nada conferido**. A autodeclaração não aparece: ninguém deste cenário é da cota.
Além da presidência, `treino.avaliacao2` — membro da comissão que **não preside** — está alocado à
conferência dos documentos deste Edital.

**Quem faz:** membro alocado à conferência (`treino.avaliacao2`) → presidência (`treino.presidencia`).

**Seu desafio:**

1. Entre como `treino.avaliacao2` (grupo **Comissões**). Em **Minhas atividades**, *Para fazer
   agora* diz **Conferir os documentos de 3 convocações**, Edital SIM12/2026, **pela alocação**.
   Siga o link.
2. Abra os documentos do primeiro convocado e **abra cada arquivo** — o GPS só aceita "conforme"
   de quem abriu o documento.
3. Marque um item como **conforme** e outro como **pendente**, com o motivo. O desfecho da
   convocação não é seu: quem é alocado só confere, e o GPS recusa o desfecho a quem não preside.
4. Entre como `treino.presidencia` e faça o mesmo nos outros convocados; registre o desfecho de
   quem tiver tudo conforme.

**Resultado esperado:** conferências registradas — umas pela alocação, outras pela presidência — e
desfecho das convocações.

**Validade:** 30 dias.

## C13 — Retificação

**Objetivo:** retificar um Edital publicado.

**Você começa com:** o Edital `SIM13` publicado, inscrições abertas e 2 inscrições enviadas.

**Quem faz:** Elaborador → Homologador → Publicador.

**Seu desafio:**

1. Como **Elaborador**, crie uma Retificação: por exemplo, prorrogue as inscrições ou acrescente
   uma vaga.
2. Envie para homologação; como **Homologador**, homologue; como **Publicador**, publique.
3. Veja o que mudou na página pública e o que os inscritos passam a ver.

**Resultado esperado:** Retificação publicada e nova versão do Edital.

**Validade:** 30 dias.

## C14 — Encerramento

**Objetivo:** ler as pendências finais e encerrar.

**Você começa com:** o Edital `SIM14` com resultado definitivo divulgado e a convocação não
iniciada.

**Quem faz:** Gestor.

**Seu desafio:**

1. Como **Gestor**, abra o encerramento do Edital.
2. Leia as advertências: o que o GPS diz que ficou por fazer.
3. Decida: encerre o Edital, e depois o Processo.

**Resultado esperado:** Edital e Processo encerrados, com o histórico na trilha.

## C15 — Vagas não preenchidas

**Objetivo:** ver o que acontece quando há menos habilitados que vagas.

**Você começa com:** o Edital `SIM15`, 3 inscritos para 4 vagas; 1 deles inabilitado na análise
documental; ninguém na cota. Corte e apuração já emitidos.

**Quem faz:** presidência (`treino.presidencia`).

**Seu desafio:**

1. Abra a ocupação das vagas e leia o que ela diz sobre as vagas que sobram e sobre a cota vazia.
2. Convoque as duas pessoas habilitadas.
3. Tente convocar a terceira e leia a mensagem.

**Resultado esperado:** duas convocações; vagas restantes apontadas como não preenchidas.

## C16 — Exportação à formalização

**Objetivo:** como o setor que formaliza, receber os documentos das pessoas aptas.

**Você começa com:** o Edital `SIM16`, 3 convocados que **aceitaram a vaga** e estão aptos para
formalização. A presidência já definiu o que vai ao setor (o documento de identificação), e a
pessoa fictícia do setor, `treino.formalizacao`, já tem o papel Formalização **e** está designada
para este Edital.

**Quem faz:** o setor (`treino.formalizacao`, com o papel **Formalização** — veja *Como entrar*).

**Seu desafio:**

1. Antes, entre como **Gestor** e abra o Edital `SIM16`, aba **Conclusão**: o quadro da passagem ao
   setor diz *"Quem recebe: 1 pessoa designada"* e quantas pessoas faltam disponibilizar.
2. Saia e entre como `treino.formalizacao`. Abra **Formalização** e, nela, o Edital `SIM16`.
3. **Verifique** o que vai receber, leia a lista e **baixe** o pacote.
4. Volte ao Edital como Gestor e veja o quadro: as pessoas aparecem como disponibilizadas.

**Resultado esperado:** pacote baixado e registrado; o Centro conta as 3 pessoas como
disponibilizadas.

**Atenção:** o pacote traz só o documento de identificação. Para o aceite nascer pronto, este
Edital não pede documento na convocação — os da convocação exigiriam que alguém abrisse cada
arquivo para conferi-lo, e isso é você quem faz, não o gerador (C12).

## C17 — Designação para a formalização

**Objetivo:** designar quem do setor vai receber os documentos do Edital.

**Você começa com:** o Edital `SIM17`, no mesmo ponto do C16 — 3 pessoas aptas e a definição
gravada —, mas `treino.formalizacao` tem só o papel, **sem designação**.

**Quem faz:** a presidência (`treino.presidencia`); depois, o setor (`treino.formalizacao`). Quem
administra os acessos da unidade também designa, pela tela de acessos.

**Seu desafio:**

1. Entre como `treino.formalizacao` (papel **Formalização**) e abra **Formalização**: a tela diz que
   você ainda não foi designado.
2. Como **Gestor**, abra o Edital `SIM17`, aba **Conclusão**: o GPS diz que ninguém está designado
   e a quem pedir.
3. Entre como a presidência (`treino.presidencia`, no grupo **Comissões**). No Edital `SIM17`, aba
   **Conclusão**, siga **Designar quem recebe os documentos**; em **Quem acessa os documentos**,
   escolha *Formalização Treinamento*, deixe os Perfis sem marcar (todos), escreva o motivo e clique
   em **Designar para o Edital SIM17**.
4. Entre de novo como o setor: o Edital `SIM17` aparece. Verifique e exporte, como no C16.

**Resultado esperado:** designação registrada; o Centro deixa de dizer que ninguém recebe, e o
pacote é exportado.

**Atenção:** a pessoa `treino.formalizacao` só aparece para designar nos Editais de treinamento —
nos Editais reais da unidade ela não é oferecida nem contada.

---

## Quando o cenário já foi usado

Os cenários **guardam** o que você fez. Se outra pessoa for repetir o exercício, peça ao
administrador para **restaurar** aquele cenário: ele ganha uma versão nova (`-R2`) no estado
inicial, e a sua fica na aba Cancelados, para consulta.
