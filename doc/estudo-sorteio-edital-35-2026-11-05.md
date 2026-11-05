# Estudo de caso — o sorteio do Edital 35/2026

**Data**: 05/11/2026 · **Base**: `main` em `de5df85c` · **Natureza**: investigação. Nenhum código de
produto, migration, dependência ou spec foi alterado.

Pós-graduação em Educação Especial Inclusiva, oferta **Polo Cefor** (`PEEI-CEFOR`): onze candidatos e
seis vagas. Este estudo explica o que o GPS fez no Edital, por que fez, e onde a regra publicada e a
tela se desencontram. Foi preparado depois da reunião de alinhamento de 05/11 (85 min). A transcrição
da reunião foi lida como registro das dúvidas da equipe, e não como regra.

**Fontes.** O backup do banco de 05/11 foi restaurado num PostgreSQL à parte. As simulações rodaram
numa cópia descartável desse banco, migrada para a `main`, com o correio em memória. O banco restaurado
não foi alterado e nenhum e-mail saiu.

Os caminhos de código são relativos a `backend/processo_seletivo/`. Os identificadores `FR-` citados
são de specs existentes. As decisões pendentes usam `Q`, para não colidir com a varredura de
`test_citacoes_de_requisito.py` se este estudo virar spec.

> **Governança.** Este documento registra fatos medidos e recomendações. Nada aqui vira escopo por
> estar escrito. Priorizar e decidir são do usuário.

## Candidatos, sem nome

O repositório é público, por isso os candidatos aparecem por código. **C*n*** é a pessoa que recebeu o
número *n* na relação geral do sorteio, em ordem de protocolo. O nome e o protocolo estão no GPS, na
relação congelada de 03/11. Nas listas reservadas, a mesma pessoa tem outro número, porque cada relação
numera os seus participantes. Por isso o código usa sempre o número da relação geral.

| Código | Modalidade marcada |
|---|---|
| C1, C3, C4, C5, C8, C10 | AC (só ampla) |
| C6, C9 | PcD |
| C2, C7, C11 | PPI |

Cada inscrição marcou **uma** modalidade.

## 1. Resumo

A leitura da equipe está certa, e é a regra publicada: **C6 ocupa uma das quatro vagas da ampla, e a
vaga PcD vai para C9.** O GPS conhece essa regra e chega ao mesmo resultado. Mas ele a aplica na
**ocupação**, e não no **corte**. A tela de corte da lista PcD calcula a lista isolada, por isso
propõe C6, e nada nela avisa que a vaga ainda vai mudar de mãos.

| Situação | Conclusão |
|---|---|
| Confirmado | **O sorteio está correto e é reproduzível.** Os quatro sorteios foram recalculados a partir da relação congelada e da semente da Loteria 6115. A ordem e o resumo do manifesto conferem nos quatro. |
| Confirmado | **A regra da concorrência simultânea existe no sistema.** A ocupação e a fila de convocação descontam quem já ocupa vaga pela ampla. Na cópia, o caminho completo termina com seis pessoas distintas nas seis vagas, e C9 na PcD. |
| Desencontro | **O corte reservado não sabe disso.** Emitir o corte PcD grava "C6 — progride" na lista PcD, num ato irreversível. C9 só é alcançada depois de mais três atos: apurar, pedir faixa seguinte e apurar de novo. |
| Indício de defeito | **Três comportamentos a corrigir**, todos observados na cópia. Sem corte, a convocação PcD oferece "chamar para regularizar" começando por C6. Sem ninguém a alcançar, a faixa seguinte é emitida vazia. E a vaga reservada sem candidato nunca reverte. |

> **Risco de emitir novos atos agora.** Emitir os cortes PcD e PPI não leva a vaga à pessoa errada,
> porque a convocação chama C9 e C7. O custo é deixar no histórico um ato PcD que diz o contrário do
> Edital. Na ampla já há uma segunda faixa emitida (5º a 8º, motivo "Suplente"). Ela fez quatro
> pessoas *progredirem*, e isso não se desfaz. **Sugestão:** só emitir os cortes PcD e PPI depois da
> decisão Q1, na §9.

## 2. Linha do tempo (fatos do banco)

- **28/10, 10h53.** O Edital é publicado. O método do sorteio apontava o concurso `3819` da Loteria
  Federal, um número de 2004.
- **28/10, 10h56–11h09.** Chegam 11 inscrições: 6 AC, 2 PcD e 3 PPI. Às 13h01 são congeladas as
  primeiras relações, ainda com o concurso 3819.
- **29/10 e 03/11, 12h04.** Duas Retificações. A segunda troca o concurso para o `6115`, de 04/11.
- **03/11, 12h05–12h06.** As quatro relações são publicadas de novo, sucedendo as anteriores, com o
  motivo "Alteração de concurso". A relação que vale é essa.
- **04/11.** Acontece a extração 6115. A Caixa publica só a data, então o sistema registra "aconteceu
  não antes de 04/11 00h00" e exige que a relação tenha sido congelada antes desse instante. O
  congelamento de 03/11 é anterior, e o sorteio podia rodar.
- **05/11, 09h23.** O gestor consulta e registra o resultado da 6115:
  `032588 078206 078624 063078 020763`.
- **05/11, 14h36–14h38.** São feitos quatro sorteios: todos os inscritos (11), AC (6), PcD (2) e
  PPI (3).
- **05/11, 14h41–15h15.** As quatro ordens são divulgadas como resultado **preliminar**, e um aviso é
  registrado para os 11 candidatos.
- **05/11, 15h20–15h22.** A comissão emite três cortes, todos na linha geral da ampla:
  - a faixa 1º–4º;
  - uma sucessora idêntica, com o motivo "Chamada imediata";
  - uma **faixa seguinte 5º–8º, com o motivo "Suplente"**, que fez C10, C7, C3 e C8 progredirem.
- **05/11, 15h26.** A ocupação é apurada: a ampla fica com 4 de 4 ocupadas e a PcD com 0 de 1, sem
  corte. Não há corte PcD nem PPI, nem convocação.

## 3. Passo a passo

### 3.1 Antes do sorteio: quem concorre a quê

O quadro de vagas do Polo Cefor tem três linhas: **4 vagas de ampla concorrência, 1 PcD e 1 PPI**.
Todos os candidatos concorrem à ampla. Quem marcou PcD ou PPI concorre, ao mesmo tempo, à reserva da
sua modalidade.

> "O sorteio será realizado de forma que todos os candidatos (inclusive os cotistas) participem do
> sorteio da ampla concorrência e em sequência haverá o sorteio das reservas de vaga."
> — Edital 35/2026, seção "Como será a seleção?", que cita a Resolução CS nº 10/2017 do Ifes

| Lista | Quem concorre |
|---|---|
| Ampla | todos os 11 |
| Reserva PcD | C6 e C9 |
| Reserva PPI | C2, C7 e C11 |
| Só ampla | C1, C3, C4, C5, C8 e C10 |

### 3.2 Congelamento: a lista não muda mais

Em 03/11 o GPS publicou a relação de habilitados de cada lista e deu a cada pessoa um **número do
sorteio**, em ordem de protocolo. Cada relação recebe um resumo criptográfico, que muda se alguém for
incluído, retirado ou renumerado. O resumo da relação geral começa com `5df7fbde…`.

A relação precisa ser congelada **antes** de a Loteria correr, para que ninguém possa montar a lista
já sabendo o resultado. Por isso a tela recusou congelar uma lista nova em 05/11: a extração 6115 já
tinha acontecido.

### 3.3 O sorteio: uma chave por pessoa

O sorteio não usa roleta nem embaralhamento. Para cada participante, o GPS calcula o SHA-256 de cinco
dados:

- um rótulo fixo;
- o resumo da relação;
- a lista;
- a semente da Loteria;
- o número da pessoa.

A ordem do sorteio é a desses resultados, do menor para o maior. Depois do congelamento ninguém escolhe
mais nada, e qualquer pessoa pode refazer a conta.

| Ordem | Código | Modalidade | Início da chave |
|---:|---|---|---|
| **1º** | **C2** | PPI | `13462b1924fc…` |
| **2º** | **C1** | AC | `219b56f32299…` |
| **3º** | **C6** | PcD | `46a66874f394…` |
| **4º** | **C4** | AC | `495f5524c775…` |
| 5º | C10 | AC | `5f706cc01a0c…` |
| 6º | C7 | PPI | `6acb7686696a…` |
| 7º | C3 | AC | `7e4f3b0d3d93…` |
| 8º | C8 | AC | `8bdf3734c65c…` |
| 9º | C5 | AC | `9b6b844c0eea…` |
| 10º | C11 | PPI | `cad677de1db1…` |
| 11º | C9 | PcD | `da097f2bfbc0…` |

As quatro primeiras posições, em negrito, estão dentro das 4 vagas da ampla. Duas delas são de
cotistas: C2 (PPI) e C6 (PcD).

### 3.4 As listas específicas são sorteios separados

Cada lista tem relação própria, numeração própria e chave própria. Por isso a ordem PPI não é a ordem
geral filtrada. Na geral, C2 vem antes de C7; na PPI, C2 é a 3ª. As duas posições são fatos do
sorteio e continuam publicadas.

| Lista | Ordem | Para que serve |
|---|---|---|
| Todos os inscritos | C2, C1, C6, C4, C10, C7, C3, C8, C5, C11, C9 | Define as 4 vagas da ampla. Na tela de corte, aparece como "Ampla concorrência (linha geral do quadro)". |
| PcD | C6, C9 | Define a vaga PcD. |
| PPI | C7, C11, C2 | Define a vaga PPI. |
| AC (só quem marcou AC) | C8, C10, C5, C4, C1, C3 | **Lista a mais.** Nenhuma vaga sai dela, e a ocupação nunca a lê. É por isso que C1 aparece em 2º numa lista e em 5º noutra. A spec 122 (PR #398, sem merge) impede que essa lista volte a ser criada. |

### 3.5 Distribuição: quem fica com cada vaga

> "Caso um candidato autodeclarado seja sorteado dentro do número de vagas nas duas listas (Ampla
> concorrência e PPI ou PcD), ele será classificado na lista de ampla concorrência."
>
> "Os candidatos autodeclarados negros e indígenas sorteados dentro do número de vagas oferecido para
> ampla concorrência não serão computados para efeito do preenchimento das vagas reservadas, isto é,
> não constarão na lista de classificados como autodeclarados, abrindo vaga para o próximo suplente
> autodeclarado."
> — Edital 35/2026, "Como será a seleção?" (§§ 1º e 2º do art. 1º da Resolução CS nº 10/2017). O
> segundo trecho fala de PPI; o primeiro vale também para PcD.

| Vaga | Quem | Por quê |
|---|---|---|
| Ampla 1 | C2 | 1ª na geral. É PPI, mas fica na ampla. |
| Ampla 2 | C1 | 2ª na geral. |
| Ampla 3 | C6 | 3ª na geral. É PcD, mas fica na ampla. |
| Ampla 4 | C4 | 4ª na geral. |
| PcD | C9 | 1ª da lista PcD fora da ampla. C6, a 1ª da lista, já ocupa a Ampla 3. |
| PPI | C7 | 1º da lista PPI. É o 6º na geral, portanto está fora da ampla. |

São seis vagas para seis pessoas diferentes, e os casos de C6 e C7 não são iguais:

- **C6** está dentro das vagas da ampla e das vagas PcD. A ampla prevalece, e a vaga PcD passa para a
  próxima da lista.
- **C7** está fora da ampla, porque é o 6º e a ampla vai até o 4º. Ele ocupa a vaga PPI normalmente.
- **C2** também é PPI e está dentro da ampla. Mas é a 3ª da lista PPI, e não alcançaria a vaga
  reservada de qualquer forma.

### 3.6 Corte: o que a tela propõe e o que o sistema faz depois

O corte de cada lista é calculado **sozinho**. Ele pega o alvo da linha do quadro e marca como
"progride" as primeiras posições daquela lista. Na PcD o alvo é 1, então a proposta é C6. O corte não
consulta a ampla.

Quem consulta a ampla é a **ocupação**. Ao apurar a PcD, ela vê que C6 já ocupa vaga pela ampla, não
a conta, e acusa "1 vaga, 0 ocupadas". A faixa seguinte pedida por esse déficit alcança C9, e a
apuração seguinte fecha "1 de 1".

Na cópia, o sistema atual chega a C9 em cinco passos:

1. **Emitir o corte PcD.** O ato grava C6 como "progride" e C9 fora da faixa. É irreversível.
2. **Apurar a ocupação PcD.** Como C6 já ocupa pela ampla, o resultado é 0 de 1 ocupadas.
3. **Pedir a faixa seguinte**, pelo déficit de 1. O ato grava C9 como "progride".
4. **Apurar de novo.** O resultado é 1 de 1 ocupadas, e C9 é a titular.
5. **Convocar titulares.** A prévia mostra C9.

A spec 095 já registrava esse efeito (FR-2319): quem ocupa pela ampla gasta uma posição na faixa da
reservada, e chegar ao próximo exige faixa seguinte.

### 3.7 Convocação: chamar, desistir, chamar o próximo

Convocar não é ocupar. A pessoa convocada é chamada para enviar documentos e se matricular. A vaga só
conta como ocupada quando o desfecho é aceite ou regularização.

Se a pessoa desiste, não atende ou é indeferida, o desfecho a tira da vaga. A ocupação é refeita
sozinha e a fila aponta o próximo. O que aconteceu na simulação está na §5.

## 4. Duas leituras lado a lado

| Vaga | Regra do Edital | Tela de corte (prévia de hoje) | Sistema depois da ocupação e da faixa seguinte |
|---|---|---|---|
| Ampla 1–4 | C2, C1, C6, C4 | C2, C1, C6, C4 | C2, C1, C6, C4 |
| PcD | C9 | **C6** progride; C9 fora da faixa | C9 |
| PPI | C7 | C7 | C7 |
| Pessoas distintas | 6 | 5 (C6 aparece duas vezes) | 6 |

A divergência está na camada do corte e na forma como ele é apresentado, e não no resultado final. O
sistema não convocaria C6 para a vaga PcD em nenhum momento, porque a fila PcD exclui quem ocupa pela
ampla. Mas o ato de corte PcD, depois de emitido, continua dizendo que C6 progrediu ali. O Edital diz
que essa pessoa "não constará na lista de classificados como autodeclarados".

## 5. Convocação simulada (na cópia, com o e-mail desligado)

| Cenário | O que se fez | O que o sistema respondeu |
|---|---|---|
| Rodada 1 | "Convocar titulares" nos três recortes | Ampla: C2, C1, C6 e C4. PcD: C9. PPI: C7. Ninguém foi convocado em dois recortes. |
| D. Desistência na ampla | C1 desiste | A ocupação é refeita sozinha: 3 de 4. A próxima da fila é C10, a 5ª. Ela já estava alcançada pela faixa 5º–8º; sem essa faixa, seria preciso pedi-la. |
| D. Desistência na reserva | C9 desiste | PcD fica com 0 de 1, e a fila fica vazia. A única outra pessoa PcD é C6, que ocupa a ampla. |
| E. Reserva sem candidato | Pedir a faixa seguinte PcD | **O sistema emitiu uma faixa vazia**: ela começa na 3ª posição, que não existe, e ninguém progrediu. A vaga continua 0 de 1 e não reverte para a ampla, embora o Perfil declare "reverte ao esgotar". C6 ainda conta como alguém que poderia ocupá-la. |

**Estado real do banco, sem corte PcD.** A tela de convocação PcD oferece "chamar para regularizar"
C6 e depois C9. Foi o que apareceu na reunião, aos 58 minutos. Sem corte, o sistema trata a lista
inteira como alcançada, e essa fila não desconta quem ocupa pela ampla. Do mesmo modo, a convocação
PPI oferece C7, C11 e C2.

**Cenário C, com vários cotistas dentro da ampla.** É o próprio caso real: C2 e C6 estão entre os
quatro primeiros. C2 não afeta a PPI porque é a 3ª ali. Se fosse a 1ª, a vaga PPI passaria a C7 pelo
mesmo mecanismo da PcD.

## 6. O que confundiu na reunião, e a explicação

| Momento | O que se viu ou se disse | O que de fato acontece |
|---:|---|---|
| 17–21 min | Uma candidata é 2ª "na ampla" e 5ª "na ampla concorrência". | São dois sorteios diferentes: um com todos os 11 e outro só com os 6 que marcaram AC. A lista dos 6 não é usada para nada (spec 122). |
| 32 min | "A cotista PcD da ampla não deveria estar no sorteio PcD." | Ela tem de estar. A relação é congelada antes da Loteria, quando ninguém sabe quem cai na ampla, e o desconto é feito depois. O Edital manda as duas listas e a dupla concorrência. |
| 44–47 min | O corte PcD mostra C6 progredindo. | O corte é calculado só sobre a lista PcD. A ocupação corrige depois, sem que a tela avise. |
| 45 e 65 min | "O 1º da PPI já foi contemplado na ampla; a vaga PPI é da 2ª." | Não é. C7 é o 6º, e a ampla vai até o 4º. A cotista PPI dentro da ampla é C2, que é a 3ª na PPI. C7 fica com a vaga PPI. A própria reunião corrigiu isso aos 66 min. |
| 49–52 min | Faixa seguinte com motivo "Suplente": do 5º ao 8º apareceram como "progride". | Faixa seguinte quer dizer **mais uma chamada**: quem ela alcança progride. Suplente, no corte, é outra coisa: a sobra que a regra publicada manda analisar junto, e aqui a regra publicou 0. O efeito prático foi que C10, C7, C3 e C8 entraram na fila da ampla. |
| 58 min | Convocação PcD: "vai chamar a cotista da ampla", "próxima na ordem", "chamar para regularizar". | Sem corte PcD, a convocação lista a ordem inteira como "regularizáveis". É indício de defeito. |
| 59 min | "Apuração vigente não alterada, a nova sucede a anterior." | Atos não se editam. Cada apuração ou corte novo é mais um registro, que substitui o vigente, e o anterior continua legível para auditoria. |
| 01h07 | Datas: congelado em 03/11, Loteria em 04/11, sorteio em 05/11. | Está correto. A regra exige congelar antes do dia da extração, porque a Caixa só publica a data. |

## 7. Matriz de comparação

Legenda: **Fato** está comprovado no banco ou no código. **Hipótese** é plausível, mas falta teste.
**Pendente** espera decisão da equipe.

| Questão | Regra publicada | Sistema observado | Divergência | Evidência |
|---|---|---|---|---|
| O que é sorteado | A ampla com todos, depois cada reserva | Um sorteio por lista: todos (11), PcD (2), PPI (3), e um de AC (6) | **Fato.** O sorteio AC não está no Edital e nada o consome | 4 linhas em `sorteios_sorteio`; spec 034 D-004; spec 122 |
| Reprodutibilidade | "Semente utilizada" para auditoria | SHA-256 por participante; manifesto público | **Nenhuma.** Os 4 sorteios foram reproduzidos | `sorteios/domain/chave.py`; §10 |
| Momento do congelamento | Lista publicada dois dias antes do sorteio | Relação congelada antes do dia da extração | **Nenhuma.** 03/11 é anterior a 04/11 | `sorteios/application/sorteio.py:219` |
| Cotista dentro da ampla | Fica na ampla, não é computado na reserva e abre vaga ao próximo | Aplicado na ocupação e na fila de convocação; o corte não aplica | **Fato.** O ato de corte PcD registra C6 como "progride" | FR-252 a FR-254 (016); `ocupacao/application/selectors.py:571`; simulação |
| Cotista fora da ampla | Concorre à reserva | C7 progride na PPI e é titular | **Nenhuma** | Simulação |
| Lista publicada da reserva | Quem está nas vagas da ampla "não constará na lista de classificados como autodeclarados" | Lista PcD publicada com C6 em 1º, como "classificada" | **Pendente.** A lista divulgada é a ordem do sorteio, e não a classificação | `divulgacao_situacaodivulgada` |
| Desistência em vaga reservada | A vaga vai ao próximo autodeclarado | O desfecho retira a pessoa, a ocupação é refeita e a faixa seguinte sai pelo déficit | **Nenhuma**, quando há próximo | Simulação, cenário D |
| Reserva sem candidato | O Edital não diz; o Perfil declara "reverte ao esgotar" | Nunca esgota enquanto houver cotista ocupando pela ampla | **Pendente** (DP-2 da spec 095) | `ocupacao/domain/reversao.py`; cenário E |
| Faixa seguinte sem ninguém | — | É emitida vazia, e é irreversível | **Hipótese:** defeito provável | Cenário E |
| Regularizar sem corte | Só quem foi alcançado pode ser chamado | Sem corte, oferece a ordem inteira, começando por C6 | **Hipótese:** defeito provável | `convocacao/domain/fila.py:92`; leitura do estado real |
| Suplentes | "Até 15 suplentes por código de vaga" para chamada imediata | Regra de corte publicada com 0 suplentes | **Pendente.** A configuração difere do texto | `cutRule.surplusCount = 0` na versão de 03/11 |
| Mesma pessoa em dois recortes | Uma vaga por pessoa | Não há trava entre recortes; a proteção vem da exclusão na fila | **Hipótese:** risco. C7 é titular PPI e está na fila da ampla (6º) | `convocacao/models.py:163` |
| Nome do resultado | — | A página diz "Classificação final", e a linha diz "Resultado preliminar" | **Fato:** é questão de linguagem. Um é o nome dado ao marco, o outro a natureza da publicação | Marco `PEEI-CEFOR`; natureza PRELIMINAR |

Três pontos técnicos ficaram de fora da matriz por falta de teste:

- a apuração reservada não guarda quem ocupava a ampla quando foi emitida, e por isso não fica
  obsoleta se a ampla mudar;
- um titular da ampla que foi eliminado continua sendo descontado da reserva;
- um aceite numa reserva pode continuar contando ali, mesmo que a pessoa depois ocupe pela ampla.

## 8. Glossário operacional

- **Inscrição.** O pedido do candidato, com uma modalidade marcada (AC, PcD ou PPI).
- **Habilitação.** Neste Edital, toda inscrição enviada entra no sorteio. A análise de documentos vem
  depois, para quem é alcançado.
- **Relação congelada.** A lista publicada de quem participa de um sorteio, com o número de cada
  pessoa. Tem um resumo criptográfico e não muda mais.
- **Número do sorteio.** A posição da pessoa na relação, em ordem de protocolo. É o que entra na
  conta, junto com a semente.
- **Ordem sorteada.** A sequência que o sorteio produz numa lista. Todos recebem uma posição. O
  sorteio não decide quem fica com vaga.
- **Classificação geral.** A ordem da lista com todos os inscritos. É a lista da ampla concorrência.
- **Classificação por modalidade.** A ordem de uma lista reservada, sorteada à parte. O termo é
  ambíguo: o Edital chama de "lista de classificados" o resultado já sem quem ficou na ampla, e o GPS
  publica a ordem inteira.
- **Alocação de vagas.** Não é um ato próprio no GPS. Ela aparece na **ocupação**: quantas vagas há,
  quantas estão ocupadas e por quem.
- **Corte.** Ato que marca até onde uma lista avança para a etapa seguinte. É calculado lista por
  lista, e é irreversível.
- **Progressão.** Estar dentro da faixa de um corte. Não é o mesmo que ocupar vaga: C6 pode progredir
  na PcD e não ocupar a vaga PcD.
- **Faixa seguinte.** Mais um trecho da mesma lista, a partir de onde o corte anterior parou. Quem ela
  alcança passa a progredir. Serve para chegar a quem vem depois quando faltam ocupantes.
- **Suplente.** Tem duas acepções. No corte, são as posições a mais que a regra publicada manda
  incluir além do alvo (aqui, 0). No Edital, é qualquer pessoa da ordem que espera vaga. A palavra é
  ambígua e confundiu a reunião.
- **Ocupação.** A apuração de quantas vagas de uma linha do quadro estão ocupadas. É aqui que o
  cotista dentro da ampla deixa de contar na reserva.
- **Convocação.** Chamar uma pessoa para enviar documentos e se matricular. Ainda não é ocupar a vaga:
  a pessoa ocupa quando aceita ou regulariza.
- **Cadastro de reserva.** Não se aplica a este Edital, porque o Polo Cefor publica 6 vagas. Em
  Editais de cadastro de reserva, a ordem toda é a fila.
- **Geração vigente.** O corte em vigor numa lista: o corte inicial e as faixas seguintes dele. Um
  corte sucessor substitui a geração inteira, e a anterior fica no histórico.

## 9. Encaminhamentos

Nenhum foi implementado. A ordem segue o risco diante de atos irreversíveis.

### Decisões de domínio pendentes

- **P1 — Q1.** O corte de uma lista reservada deve pular quem já ocupa pela ampla? Ou o caminho de
  quatro atos fica, e a tela passa a explicá-lo?
- **P1 — Q2.** A lista PcD ou PPI divulgada deve marcar ou omitir quem ficou na ampla? O Edital diz
  que essas pessoas "não constarão".
- **P2 — Q3.** Os "15 suplentes por código de vaga" do Edital devem virar suplentes na regra de corte?
- **P2 — Q4.** A vaga reservada sem candidato disponível deve reverter para a ampla quando a única
  pessoa restante ocupa pela ampla?
- **P2 — Q5.** O que fazer com a faixa 5º–8º já emitida na ampla deste Edital?

### Correção (há evidência; falta confirmar por teste)

- **P1.** Sem corte, a convocação reservada oferece "chamar para regularizar" a ordem inteira,
  inclusive quem ocupa pela ampla.
- **P1.** A faixa seguinte é emitida vazia quando não há mais ninguém na lista.
- **P2.** Os três pontos técnicos do fim da §7: a apuração reservada não guarda a ampla, o eliminado
  continua descontado e o aceite pode ser contado duas vezes.

### Interface e linguagem

- **P1.** No corte reservado, marcar quem já ocupa pela ampla ("3ª na geral, ocupa a ampla") e avisar
  que a vaga irá ao próximo depois da apuração.
- **P1.** Criar uma visão única de "quem ocupa as 6 vagas", com a posição no sorteio, a modalidade
  marcada e a vaga pela qual a pessoa entra.
- **P2.** Separar "faixa seguinte" de "suplente" nas telas. O diálogo pede um "motivo", e o operador
  escreveu "Suplente" achando que marcava suplência.
- **P2.** Fechar a spec 122 (PR #398), para que a lista AC excedente não seja criada de novo.

### Documentação

- **P3.** Uma página para a equipe com a sequência sorteio → corte → ocupação → convocação, usando
  este caso como exemplo.
- **P3.** O glossário acima, com as duas acepções de "suplente".

## 10. Como reproduzir

| Item | Valor |
|---|---|
| Edital | `c6ea917b-e8da-42d9-a32c-38afcd8da1f3` |
| Perfil / marco | `3843d905-fe5b-4d4e-993c-68621502c63e` / `e5c32a65-e641-4416-8cb8-f729542fe21a` |
| Versão vigente | `9c2fc5a2-1058-4973-9523-28013f8a866f` (03/11, 12h04) |
| Relação geral | `cb7a6605-aa20-4388-addd-0827ad53e415`, resumo `5df7fbde655446d0f3504f386bf532e76dcea3e2e224fe7c28a6a6619aee5bed` |
| Método | `IFES-SORTEIO-SHA256-v1`, resumo `74b027017eb0499495c896ff12610867b4c4946a42d033b33a6aaec06c65b8b8` |
| Semente | Loteria Federal 6115: `032588 078206 078624 063078 020763` |
| Sorteio geral | `2607f667-1065-4d90-8b0b-91e895fc5fde`, manifesto `580e905fad35863878497fda872c7fe0ecdd55a2d52d9febd08ff6dd3b503210` |

A chave de cada participante é o SHA-256 do JSON canônico
`{"domain":"processo-seletivo/sorteio/v1","drawScopeId":<perfil>[:<lista>],"publicNumber":n,"relationHash":<resumo>,"seed":<semente>}`.
A ordem é a das chaves, em ordem crescente, e o desempate é pelo número. No GPS,
`sorteios.application.verificacao.verificar(sorteio)` refaz os cinco degraus da página pública de
verificação.

### O ambiente do estudo

O dump é `pg_dump -Fc` do PostgreSQL 18, e o `pg_restore` 16 recusa a versão do arquivo. O estudo usou
um container `postgres:18` com três bancos:

1. o restaurado, que não foi tocado;
2. um clone migrado para as simulações;
3. um clone migrado para ler o estado real.

Antes de restaurar, crie as roles `processo_seletivo_owner`, `processo_seletivo_runtime` e
`processo_seletivo_publicador`, e restaure com `--no-acl`. O dump estava quatro migrations atrás da
`main`, por isso só os clones foram migrados. Os scripts rodam por `manage.py shell`, com
`DB_NAME` apontando para o clone e com
`DJANGO_EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend` na simulação de convocação.

### Script de reprodução (só leitura)

```python
# Reproduz os quatro sorteios a partir só do que foi publicado: resumo da relação
# congelada, recorte, semente e números públicos. Não grava nada.
from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.publicacoes.models import VersaoConsolidada
from processo_seletivo.sorteios.domain import chave as ch
from processo_seletivo.sorteios.domain import manifesto as mf
from processo_seletivo.sorteios.domain.metodo import metodo_declarado
from processo_seletivo.sorteios.domain.normalizacao import normalizar
from processo_seletivo.sorteios.models import Sorteio

EDITAL = "c6ea917b-e8da-42d9-a32c-38afcd8da1f3"

for s in Sorteio.objects.filter(edital_id=EDITAL).select_related("relacao", "ocorrencia").order_by("executado_em"):
    r = s.relacao
    parts = {p.numero_publico: p.inscricao_id for p in r.participantes.all()}
    semente = normalizar(material_bruto=s.ocorrencia.material_bruto, regra="DIGITOS_EM_SEQUENCIA")
    escopo = ch.recorte(perfil_id=r.perfil_id, lista_id=r.lista_id)
    chaves = ch.chaves(relation_hash=r.resumo, draw_scope_id=escopo, seed=semente, public_numbers=list(parts))
    ordem = ch.ordenar(chaves)
    gravada = [p.inscricao_id for p in PosicaoNaOrdem.objects.filter(ato_id=s.ato_id).order_by("posicao")]
    conteudo = VersaoConsolidada.objects.get(id=r.versao_id).content
    metodo = metodo_declarado(conteudo, perfil_id=r.perfil_id, marco_id=r.marco_id)
    m = mf.derivar(sorteio=s, relacao=r, metodo=metodo, chaves=chaves, ordem=ordem)
    print(r.lista_id or "GERAL",
          "| semente:", semente == s.semente_normalizada,
          "| ordem:", [parts[n] for n in ordem] == gravada,
          "| manifesto:", mf.resumo_do_manifesto(m) == s.manifesto_hash)
```

No estudo, as três comparações deram `True` nos quatro sorteios.

### A simulação de ocupação e convocação

A simulação rodou só no clone, com a comissão como ator (`comissao:gerir`), em duas sequências:

1. **Ocupação.**
   - PcD: `emitir_corte`, com a confirmação de `assinatura_da_proposta(calcular_corte(...), geracao=geracao_vigente(...))`; `emitir_apuracao`; `causar_faixa_seguinte`; `emitir_apuracao`.
   - PPI: `emitir_corte`; `emitir_apuracao`.
2. **Convocação.**
   - `fluxo.previa_dos_titulares` e `fluxo.convocar_titulares` nos três recortes, com `alcance_confirmado` igual à assinatura da prévia;
   - `desfechar` com `DESISTENCIA_EXPRESSA` para C1 na ampla e para C9 na PcD;
   - `causar_faixa_seguinte` na PcD.

O estado real foi lido com `convocacao.application.selectors.leitura_do_recorte` e
`fluxo.previa_dos_titulares`, recorte a recorte, no clone de leitura.
