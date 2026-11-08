# Estudo de convergência UX — tornar óbvia a condução de um processo seletivo no GPS

**Data:** 07/11/2026 · **Base:** `main` em `da566ff2` · **Natureza:** investigação. Nenhum código de
produto, spec, migration ou ato oficial foi alterado. **Governança:** tudo aqui é recomendação; decidir
e priorizar são do usuário (§8).

**Pergunta.** Qual é o menor conjunto de mudanças que torna o GPS mais compreensível, previsível e fácil
de operar, no sorteio e na classificação?

**Hipótese recebida:** *"o GPS está orientado a operações isoladas, não à jornada"*. Ela foi testada, e
não aceita pronta (§1).

| Entrega | Onde |
|---|---|
| A. Diagnóstico na sequência real de uso | §2 |
| B. Mapa de oportunidades | §3 |
| C. Maquetes comparativas, com os dados do caso | §4 e `maquetes/` |
| D. Estratégia incremental para specs futuras | §5 |
| E. Roteiro de validação com TI e negócio | §6 |
| Decisões que ficam com o usuário | §8 |
| Telas reais novas (7) | `capturas/` |
| Sonda da derivação, planos de captura e maquetes | `roteiro/` |

**Fontes.**

- O Edital 900/2026 fictício, reproduzido do zero com `reproduzir.py` do
  [estudo de 07/11](../estudo-classificacao-demonstrativa-2026-11-07.md). As capturas desse estudo
  (citadas como **E-nn**) continuam válidas: o código mudou depois delas só na Classificação somente
  leitura e nos documentos (132).
- O [estudo do sorteio do Edital 35](../estudo-sorteio-edital-35-2026-11-05.md) e o
  [de concorrência concomitante](../estudo-concorrencia-concomitante-2026-11-07.md).
- O [estudo de orientação da jornada de 06/11](../estudo-orientacao-da-jornada-2026-11-06/README.md),
  que gerou a `126`, a `127` e a `128`, **já implementadas**.
- O código, lido e exercitado em bancos isolados (§7).

---

## 1. Resposta curta

**A hipótese estava certa em 06/11 e já não está.** Depois da `127`, o GPS tem uma camada de jornada
bem desenhada:

- "O que fazer agora", por papel;
- o "Andamento da seleção";
- o "Próximo nesta lista" depois de cada ato.

Essa camada lê as mesmas funções que decidem as telas, sem estado novo. O problema mudou de natureza.
**Hoje são três falhas de convergência, e nenhuma delas pede página, fluxo ou motor novo.**

**1. A jornada aponta o ato errado na classificação com mais de um marco. É o achado mais grave.**
Com as seis vagas ocupadas por aceite, o cartão diz à presidência "**SUA: Apurar a ocupação**" para o
marco intermediário. Numa cópia descartável, o GPS **aceitou** esse ato. Em seguida o cartão pediu
"Convocar 4 titulares" desse marco, e o comando aceitou convocar:

- Bruno, que já tinha desistido;
- Sofia, 7ª na classificação final e fora das vagas.

A derivação também:

- sugere o corte enquanto o prazo de recurso corre;
- oferece a quem publica uma definitiva que o comando recusa;
- esconde "Chamar a próxima da fila" depois de uma desistência.

São quatro defeitos de derivação, com causa localizada em `interface/andamento.py` (§2, **CV-01 a
CV-04**).

**2. A explicação existe, mas mora nas prévias, e não nas telas dos atos.** As prévias já desenham:

- o desempate critério a critério (`ordenar_com_trajetoria`);
- a união das faixas, "N candidatos poderiam participar";
- a marca "ocuparia pela ampla" (`_marcas_do_recorte.html`).

Fazem isso para **20 candidatos fictícios**. As telas da ordem, do corte, da ocupação e da convocação,
que tratam dos candidatos reais, mostram só a pontuação combinada e "Fora da faixa". A explicação que o
operador procura, para a Sofia e para a vaga PPI que foi a Kátia, já foi escrita uma vez. Falta
servi-la com os dados do processo.

**3. A configuração descreve cada decisão numa frase normativa, mas não mostra o plano que elas
formam.** Uma das frases está errada: "os 8 primeiros", quando o motor aplica 8 **em cada lista**
(`publicacoes/infrastructure/pdf.py:2012`). A dependência entre Etapas, que decide quem chega a cada
uma, não está escrita em lugar nenhum da composição.

**O menor conjunto de mudanças** tem três entregas, nesta ordem:

1. **Corrigir a derivação da jornada.** São quatro regras puras em `andamento.py`, mais a frase do
   corte fixo. É a primeira entrega: pequena e validável pela mesma sonda deste estudo.
2. **Levar às telas dos atos a explicação que as prévias já produzem**, com os dados reais e sem
   cálculo novo: na ordem, no corte e na ocupação.
3. **Mostrar na Revisão o plano de execução**, lido do conteúdo, com as verificações que hoje só a
   prévia revela.

A prévia com as notas reais (P2 do usuário) é viável no código. `simular()` aceita uma `populacao`
própria. Mas ela depende de uma decisão, a G3 do estudo de 07/11, e a `132` tornou a etapa somente
leitura depois da publicação (§2.8).

**Revisão da priorização inicial.**

| Tema | Prioridade proposta pelo usuário | Prioridade recomendada | Por quê |
|---|---|---|---|
| Próxima ação contextual | P0 | **P0, como correção, e não como construção** | Ela existe. Erra em quatro lugares, e um deles leva a ato irreversível com efeito externo |
| Prévia de consequências | P0 | **P0 só nos dois pontos de risco medidos** | O corte antes do fim do prazo e a apuração ou convocação de marco intermediário. Nas demais telas, a conferência que já existe responde bem (§2.9) |
| Explicação individual, progressão e vagas | P1 | **P1, uma entrega só** | Têm a mesma causa: a explicação está só na prévia |
| Configuração visual das Etapas | P1 | **P1b** | Sem risco imediato depois de corrigida a frase. O trilho reaproveita a `jornada()` |
| Simulador contextualizado | P2 | **P2, depois da decisão G3** | — |

---

## 2. Diagnóstico na sequência real de uso

Cada achado é classificado pelo tipo que o pedido definiu: regra de negócio, modelagem,
sequenciamento, informação insuficiente, linguagem, navegação fragmentada, validação tardia,
inconsistência de estados ou defeito funcional. O caso é o Edital 900, salvo indicação, e os nomes são
fictícios. As provas de banco foram feitas em cópias descartáveis.

### 2.1 Configuração (elaborador)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| CV-10 | A Revisão diz "os 8 (oito) primeiros classificados", e o motor aplica 8 em cada lista. Doze pessoas foram à Entrevista, e o teto era 24 | E-13; `pdf.py:2012` usa a mesma frase para o alvo fixo e só o alvo do quadro diz "de cada lista" | **Linguagem**, com risco normativo: a frase vai ao PDF do Edital |
| CV-11 | A dependência entre Etapas é implícita na ordem: eliminado em qualquer Etapa anterior sai, e a imediatamente anterior precisa habilitar. Nada a escreve. As setas ↑↓ parecem arrumação visual | Diário C06; D4 do estudo de 07/11 | **Informação insuficiente** |
| CV-12 | O marco novo nasce como "Classificação final", com o código do Perfil e o corte pelo quadro. O intermediário exige desfazer 4 padrões | Diário C07 e C08 (D5) | **Modelagem** do padrão |
| CV-13 | A mínima em Etapa não eliminatória é aceita e não faz nada. O peso é um só para todos os marcos. Nenhuma das duas coisas é dita na Etapa | D9 | **Validação tardia** |
| CV-14 | "Qual é a ampla" e "reversão" só aparecem depois do 1º salvamento dos Perfis | D10 | **Sequenciamento** |
| CV-15 | O simulador alerta "empate pararia a apuração" num marco que não apura vagas | Diário C09 (D13) | **Inconsistência de estados**. É a mesma raiz da CV-01: o GPS não sabe que um marco é intermediário |

**O que funciona.** As mensagens nomeiam número e lugar ("o quadro soma 8 e o Perfil declara 6"). A
Revisão separa *Impede* de *Aviso* e diz o que fica imutável. O estudo de 07/11 contou 12 salvamentos
e 1 recusa. **O risco não está no ciclo salva-erra-corrige. Está no que passa sem erro.**

### 2.2 Publicação até as inscrições

Fora do escopo: a orientação é boa desde a `104` (P-01 e P-02 do estudo de 06/11).

### 2.3 Etapas e primeira ordem (09/12)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| CV-02 | A presidência emite a ordem do marco 1. O "Próximo nesta lista" e o cartão dizem **"SUA: Emitir o corte"**, enquanto, no mesmo cartão, a definitiva "Aguarda: o prazo recursal… se encerra em 12/12". Na cópia descartável, o corte foi aceito antes até da preliminar. Depois do recurso deferido de 13/12, ele ficou obsoleto, a Entrevista ficou impedida, e a sucessão exige motivo e fica na trilha | `capturas/01`; sonda T1 e T2; `andamento.situacao_do_corte` só olha se a ordem está *Feito* | **Sequenciamento**. É recomendação, e não impedimento: o domínio aceita, e a decisão de recusar é do usuário (R2) |
| CV-16 | A tela da ordem mostra só a pontuação combinada (91,5 · 87,25 · 70: as casas variam). Não mostra as notas por Etapa, quem cabe no corte nem o critério que separou Sofia de Rafael. A proposta do comando já traz `separado_por` em cada linha | E-18; `classificacao/application/calculo.py:161`; `ordenacao.html:171-181` | **Informação insuficiente**. A informação está calculada e não é desenhada |

### 2.4 Preliminar e recurso (10–13/12)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| CV-04 | O recurso de C10 é deferido e a ordem da ampla fica obsoleta. Para quem publica, o cartão mostra "**Pendente: Publicar o resultado definitivo**" na ampla. O comando recusa: "a regra ou o universo mudaram desde a emissão". É a recusa que a `128` quis evitar para a ordem, aqui na divulgação | Sonda T3; cópia descartável; `situacao_do_resultado` só checa a ordem obsoleta quando a publicação **não** está feita | **Validação tardia** e **inconsistência de estados** |
| CV-17 | A ordem obsoleta lista as "mudanças posição a posição" **por protocolo**, sem nome, e não diz que a 8ª posição é a fronteira do corte nem que Elisa sai da faixa da ampla mas continua pela PcD | E-22b (D8) | **Informação insuficiente** |
| CV-18 | O Julgador não vê o objeto sem instrução, e a decisão diz só "o resultado foi corrigido" | E-23 | **Regra**, de propósito (instrução). Fica de fora: não se resolve regra com texto |

### 2.5 Corte e Etapa governada (14/12)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| CV-19 | O corte da ampla marca **"Fora da faixa"** para Elisa, Kátia, Iara e Luan, que **vão** à Entrevista por outra lista. Nenhuma tela diz quem vai à Etapa seguinte, nem por qual lista. A prévia diz ("14 candidatos poderiam participar"), mas para fictícios | E-24; `previa_da_classificacao._participantes` (`uniao`, `so_pela_ampla`); D2 | **Navegação fragmentada**: três telas, uma por lista, e a soma fica de cabeça |
| — | No sorteio, é o mesmo padrão: o corte PcD marca C6 "progride", sem a marca "ocupa pela ampla" que a prévia do sorteio já tem | Estudo do 35, §3.6; `_marcas_do_recorte.html` | Igual à CV-19 |

### 2.6 Classificação final, apuração e convocação (28/12–04/01)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| **CV-01** | Em 29/12 o cartão lista primeiro "**SUA: Apurar a ocupação**", Ampla, PCD e PPI, do **marco 1**, e só depois "Convocar 4 titulares" do marco final. Em 06/01, com as 6 vagas ocupadas por aceite, a única providência é a mesma apuração. **Na cópia descartável, `emitir_apuracao` no marco 1 foi aceita** (4/4/4). O cartão passou a "Convocar 4 titulares" do marco 1, e `convocar` aceitou C01, C16, C02 (que desistiu no marco final) e C07 (7ª na final, fora das vagas) | `capturas/03`, `04`; E-50; sonda T5 e final; `andamento._pontos_do_marco` dá Apuração, Resultado e Convocação a todo marco | **Modelagem** (o GPS não distingue o marco cuja Etapa governada é lida por um marco posterior) e **inconsistência de estados**. Risco de **erro administrativo com efeito externo**: a comunicação sai no ato da convocação |
| CV-20 | A ocupação diz "4 publicadas · 4 efetivas · 4 ocupadas" antes de qualquer convocação. Não diz **quem** ocupa, nem que João ocupa pela ampla e por isso a vaga PPI foi a Kátia | E-40, E-41; D7; Q8 do estudo do 35 | **Informação insuficiente**. O significado de "ocupada" é decisão pendente (G6 e Q8) |
| — | A tela da convocação é a melhor do produto: titulares, por que o suplente fica fora, o fundamento que o candidato lê e o prazo | E-41; `capturas/06` | **Manter** |

### 2.7 Desistência, reversão e nova chamada (05–06/01)

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| **CV-03** | Bruno desiste. A ampla fica com 3 de 4 ocupadas e 1 a ocupar, e a fila tem Diana. O cartão e o "Próximo nesta lista" dizem só "**Aguarda: resposta de 1 convocação**", a de Rafael, cujo documento está pendente. "Chamar a próxima da fila" some porque a derivação faz `faltando − em_aberto` = 1 − 1 = 0. Mas Rafael é **titular**, e já conta como ocupado | `capturas/06` (a tela da convocação acerta: "Diana Ferraz… próxima da fila") × `capturas/07`; sonda T6; `andamento.py`, `"em_aberto"` e `sem_chamada` em `situacoes_da_convocacao` | **Defeito funcional** da derivação: a jornada contradiz a tela do ato |
| CV-21 | A desistência da única PcD não emite a apuração seguinte. O cartão acerta ("Emitir a apuração sucessora" na PCD), mas não diz que a ampla vai ganhar a vaga revertida. São três telas para um fato só | Sonda T7; E-16 do diário; D16 | **Navegação fragmentada**. O texto de cada tela é bom |

### 2.8 Simulação

| # | O que acontece | Evidência | Tipo |
|---|---|---|---|
| CV-22 | A prévia usa 20 fictícios com a mesma nota em todas as Etapas, então o peso nunca muda nada. Inverter os critérios do marco final deu "não mudou para ninguém", e com as notas reais tiraria da faixa quem se matriculou | Estudo de 07/11, §8 | **Informação insuficiente** sobre o escopo. A tela diz o que não simula, mas não diz "estes não são os seus candidatos" no lugar da resposta |
| CV-23 | Desde a `132`, a Classificação do Edital publicado é **somente leitura**: o simulador roda com os valores gravados, e não dá mais para alterar um critério e ver o efeito. O experimento do estudo de 07/11 já não se repete | `static/interface/somente-leitura.js` (132) | **Regra**, correta: o ato é imutável. Mas ela fecha a única via de "e se" depois da publicação |
| — | Viabilidade da prévia com as notas reais: `classificacao/application/previa.simular(..., populacao=)` aceita uma população própria. `calcular_ordem` já monta os inscritos com Resultados e fatos. **É o mesmo motor, sem segunda conta** | código | Depende da decisão G3 |

### 2.9 Antecipação de consequências: o que já existe

Antes de cada ato irreversível, o GPS já tem uma **conferência** boa:

- ordem: contagens, sem posição, recursos executados;
- corte: a faixa calculada;
- convocação: quem entra, o fundamento e o texto;
- conferência de documento: "Conforme" exige ter aberto a versão.

**O que falta não é a prévia de um ato. É a consequência entre atos:**

- o corte emitido agora envelhece se um recurso for deferido (CV-02);
- a apuração deste marco não é a das vagas (CV-01);
- a desistência na PcD vai mover vaga para a ampla (CV-21).

Por isso a proposta de "consequência" (maquete A) é **uma linha** na providência, e não uma tela nova.

### 2.10 A hipótese, testada

| Pergunta | Resposta medida |
|---|---|
| O GPS orienta a jornada? | **Sim**, desde a `127`, com a mesma derivação que decide as telas |
| Onde ela falha? | No **marco intermediário** (CV-01, CV-15), na **janela recursal** (CV-02), na **conta do "a ocupar"** (CV-03) e na **divulgação com ordem obsoleta** (CV-04). As quatro estão no mesmo módulo |
| As telas de ato se explicam? | Sobre o **ato**, sim. Sobre as **pessoas**, não: por que esta posição, por qual lista avança, quem ocupa (CV-16, CV-19, CV-20) |
| A causa comum? | O conhecimento existe em dois lugares que não conversam: a **prévia** explica com fictícios, o **ato** decide com reais |

---

## 3. Mapa de oportunidades

As oportunidades estão agrupadas por **causa comum**: uma spec por grupo, e não por achado.
**Abrangência**: S = sorteio, C = classificação. **Regra de corte**: o que cada proposta elimina, pelo
critério do pedido.

### Grupo 1. A jornada conhece o que a regra já sabe (correção imediata)

| Problema | Evidência | Consequência | Solução mínima | Elimina | Abrang. | Prior. |
|---|---|---|---|---|---|---|
| CV-01: apurar e convocar o marco intermediário | `capturas/03`, `04`; cópia descartável | Ato irreversível errado; convocação de quem desistiu ou ficou fora | Na derivação: o marco cuja Etapa governada é **lida por um marco posterior** tem Apuração e Convocação *Não se aplica*, com nota ("decide quem vai à Entrevista; as vagas são da Classificação final"). Se o comando também deve recusar, é decisão do usuário (R1) | Uma tentativa frustrada, e um erro administrativo | C (e S com sorteio + Etapa governada + marco seguinte) | **P0** |
| CV-02: corte com o prazo de recurso aberto | `capturas/01` | Corte obsoleto, sucessão com motivo, Entrevista bloqueada | Corte *Aguarda* enquanto houver janela aberta ou recurso pendente no marco, com a marca **recomendação** (o GPS aceita) e a consequência em uma linha (maquete A3). A aferição `publicabilidade` já sabe a janela | Uma dúvida, e uma sucessão evitável | S e C | **P0** |
| CV-03: "a ocupar" esconde a próxima da fila | `capturas/06` × `07` | Vaga parada; o operador espera um prazo que não é o dele | Contar em `em_aberto` só as chamadas que **não** ocupam: suplente sem aceite. O titular já está em "ocupadas" | Uma navegação desnecessária, e uma vaga parada | S e C | **P0** |
| CV-04: definitiva oferecida com ordem obsoleta | Sonda T3 | Recusa no comando | Em `situacao_do_resultado`, ordem obsoleta → *Depois* também com a publicação feita | Uma tentativa frustrada | S e C | **P0** |
| CV-10: "os 8 primeiros" | E-13 | Edital publicado com regra diferente da executada | No alvo fixo, "os N primeiros classificados **de cada lista de concorrência**". Muda o PDF de Editais novos, e só deles: o publicado não se regenera | Uma dúvida, e uma divergência normativa | S e C | **P0**, junto com G1 |

### Grupo 2. A explicação da prévia, servida com os dados do processo

| Problema | Evidência | Consequência | Solução mínima | Elimina | Abrang. | Prior. |
|---|---|---|---|---|---|---|
| CV-16: a posição não se explica | E-18; `calculo.py:161` | O operador refaz a conta fora do sistema para responder ao candidato | Na ordem: colunas com a nota de cada Etapa enumerada e o peso; "Por que nesta posição" a partir de `separado_por` e `trajetoria`, que **são da mesma partição** que decidiu o ato (`ordenar_com_trajetoria`). Nenhum cálculo novo | Uma comparação manual | C (S: a ordem sorteada não tem o que explicar) | P1 |
| CV-19: quem vai à Etapa seguinte | E-24 | Três telas e a união de cabeça; "Fora da faixa" para quem vai | No corte que governa Etapa: o quadro "Quem vai à Entrevista", com a união das faixas vigentes, e a coluna "chega por: ampla / PcD / PPI / não alcançado". É a frase de `_participantes`, com os cortes emitidos (maquete B) | Uma navegação desnecessária e uma comparação manual | C; S quando o sorteio governa Etapa | P1 |
| CV-20 e o corte reservado do sorteio | E-40; estudo do 35, §3.6 | "Quem ocupa as vagas?" não tem resposta numa tela | Na ocupação e no corte reservado: a marca "ocupa pela ampla" de `_marcas_do_recorte.html` e a lista de ocupantes por lista. É o mesmo fragmento da prévia | Uma comparação manual (o Q1 da reunião do 35) | **S e C** | P1 |
| CV-17: mudanças por protocolo | E-22b | Não se vê o efeito do recurso na progressão | Nome e fronteira do corte na tabela de mudanças | Uma comparação manual | S e C | P2 |

### Grupo 3. A configuração mostra o plano

| Problema | Evidência | Consequência | Solução mínima | Elimina | Abrang. | Prior. |
|---|---|---|---|---|---|---|
| CV-11, CV-15: dependências e o marco intermediário | Diário C06 e C09 | Ordem das Etapas decidida sem saber que é regra | Na Revisão e na etapa Classificação, o **trilho** "Como o Edital será executado", lido do conteúdo pela `jornada()` da `094`, com o conector do que cada Etapa faz com quem passa e o que cada corte decide (maquete C). Nenhum campo novo | Uma dúvida | S e C | P1b |
| CV-10: verificação antecipada | — | O corte por lista só aparece na prévia | No trilho, uma linha "Confira" quando o alvo é fixo e há reservadas: o teto é N × listas | Uma dúvida | S e C | P1b |
| CV-12, CV-13, CV-14 | Diário | Atrito na configuração | O 2º marco não herda o padrão "final"; aviso de mínima sem efeito; seletores antes do 1º salvamento | Tentativas | S e C | P2 |

### Grupo 4. A prévia sabe de quem fala

| Problema | Evidência | Consequência | Solução mínima | Elimina | Abrang. | Prior. |
|---|---|---|---|---|---|---|
| CV-22: escopo da prévia | Estudo de 07/11, §8 | "Não mudou para ninguém" lido como verdade sobre o caso | **Imediato:** a resposta diz "nos 20 candidatos fictícios"; população com notas diferentes por Etapa | Uma dúvida | C | P1 (texto) |
| CV-22, CV-23: prévia com as notas consolidadas | `previa.simular(populacao=)` | Não há "e se" com os candidatos reais | Só leitura, só depois de haver Resultados, a mesma `simular` com a população lida por `calcular_ordem`. Depende da G3 e de como o "e se" convive com a somente leitura da `132` | Uma comparação manual (o `conferir.py` do estudo) | C | P2 |

### Fora do mapa, de propósito

- **Concomitância entre listas** (Q6, Q7 e Q8 do 35; estudo de 07/11): é regra, com decisões abertas.
  A CV-20 só **mostra** o que a ocupação já decide.
- **Barema e peso por marco** (G4): é capacidade nova, e não convergência.
- **O Julgador sem o objeto** (CV-18): é regra deliberada.
- **Barra de fases**: o estudo de 06/11 mostrou que ela mentiria, e a evidência daqui confirma. No 900,
  o marco 1 e o marco 2 estão em momentos diferentes.

---

## 4. Maquetes comparativas

Cada maquete troca **um bloco** da tela real do Edital 900, no banco da fase, pelo trecho proposto
(`roteiro/maquetes.py`). A moldura tracejada marca o que muda. O resto da página é o GPS de hoje. Os
dados são os do caso.

### Maquete A: "O que fazer agora", corrigido, em três momentos

| Momento | Hoje | Proposto | O que muda |
|---|---|---|---|
| 10/12, preliminar publicada, prazo até 12/12 | `capturas/01-t2-o-que-fazer-agora.jpg`: "SUA: Emitir o corte" ao lado de "Aguarda… prazo recursal" | `maquetes/A3.jpg` | **Onde está** em uma linha. O corte vira *Aguarda o prazo*, com a marca **recomendação** e a consequência "Se fizer agora". A definitiva, **impedida até 12/12** |
| 29/12, vagas apuradas | `capturas/03-t5-o-que-fazer-agora.jpg`: 1º item "Apurar a ocupação" do marco 1 | `maquetes/A1.jpg` | Só as convocações do marco final, com nomes e "Ao confirmar". A PPI diz por que vai a Kátia. O marco 1, *Não se aplica*, com o motivo |
| 05/01, Bruno desistiu | `capturas/07-t6-o-que-fazer-agora.jpg`: só "Aguarda resposta" | `maquetes/A2.jpg` | "Chamar a próxima da fila — Diana Ferraz", a mesma conclusão da tela da convocação (`capturas/06`) |

**Abrangência:** sorteio e classificação. As linhas "Onde está" e "Ao confirmar" são **texto derivado
do que a célula já sabe**:

- a nota da célula;
- o `ate` da aferição;
- os nomes da prévia dos titulares, que o andamento já chama (`fluxo.previa_dos_titulares`).

Não há estado novo. O "Onde está" sai do resumo por Perfil que a `127` já calcula
(`resumo_do_perfil`). **A maquete não propõe um passo único**: continua um conjunto, e diferencia
*Pendente*, *Aguarda* e *Impedido*, como o contrato da `127`.

### Maquete B: a explicação consolidada da classificação, da progressão e das vagas

| Hoje | Proposto |
|---|---|
| E-24: corte da ampla, "Fora da faixa" para Elisa, Kátia, Iara e Luan | `maquetes/B.jpg`: "Quem vai à Entrevista", 12 = 8 pela ampla + 2 só pela PcD + 2 só pela PPI, mais os não alcançados e os eliminados antes. Por linha: as notas por Etapa com peso, a combinada, **por que nesta posição** (Sofia × Rafael pela Prova; Caio × Diana pelo nascimento; Gustavo subiu pelo recurso) e **por qual lista chega** |

**Abrangência:**

- **Classificação**, na ordem e no corte.
- **Sorteio**, no corte reservado e na ocupação, com a marca "ocupa pela ampla". É o mesmo fragmento.

**Fonte única:**

- `separado_por` e a `trajetoria` saem da partição que emitiu o ato;
- a união sai dos cortes vigentes;
- as notas saem dos Resultados que a ordem leu.

**Decisão do usuário:** o que disso pode ir ao **candidato** (G5). A data de nascimento é dado
pessoal. A maquete é da gestão.

### Maquete C: a Revisão como plano de execução

| Hoje | Proposto |
|---|---|
| E-13: frases normativas, uma por decisão; a do corte errada | `maquetes/C.jpg`: o trilho Etapa → marco → Etapa → marco. Cada ponto traz o conector do que faz com quem passa e o que o corte decide ("não apura vagas" no intermediário). Um "Confira" com o teto 24 × os 14 da prévia, e o peso único |

**Abrangência:** sorteio e classificação. No sorteio, o trilho mostra relação, semente e sorteio, e a
Etapa de habilitação antes ou depois; a `jornada()` já trata isso (D-011 da `127`). **Não é segunda
configuração**: é a leitura, na ordem do motor, do que já está gravado.

---

## 5. Estratégia incremental para specs futuras

**Entrega 1. "A jornada não aponta o ato errado"** (P0, a primeira e a menor)

- **Escopo:** CV-01 a CV-04 na derivação (`interface/andamento.py`, funções puras `situacao_*`,
  `situacoes_da_convocacao` e `_pontos_do_marco`), mais a frase da CV-10 em `pdf.py`.
- **Sem migration, estado ou permissão novos.** A recusa no comando para a CV-01 só entra se o usuário
  decidir assim (R1).
- **Como se valida:** os testes puros da `127` já provam as situações por família. A família **P3**
  (vários marcos no Perfil) é justamente a que o banco de demonstração não tinha. Esta entrega a
  ganha com o caso 900. A aceitação é a sonda deste estudo, `roteiro/sonda.py`, nos quatro instantes:

| Instante | Esperado |
|---|---|
| 10/12 09:00 | Nenhuma providência *Pendente* de corte; o corte *Aguarda* até 12/12 |
| 13/12 11:00 | Ampla: resultado *Depois* (ordem obsoleta) |
| 29/12 16:00 | Só "Convocar titulares" do marco final; marco 1, *Não se aplica* |
| 05/01 14:10 | Ampla: "Chamar a próxima da fila" |

- **Risco:** baixo. É a mesma camada, já isolada para "não derrubar a página".

**Entrega 2. "O ato se explica com as pessoas"** (P1)

- Grupo 2: ordem (notas, por que), corte (quem vai à Etapa seguinte e por qual lista), ocupação e
  corte reservado ("ocupa pela ampla", ocupantes).
- Reaproveita `ordenar_com_trajetoria`, `_participantes` e `_marcas_do_recorte.html`. A regra é **uma
  fonte**: um teste de equivalência entre a explicação desenhada e o ato, como o da prévia com o motor.
- **Depende de** G5, só para o portal; a gestão pode vir antes.

**Entrega 3. "A configuração mostra o plano"** (P1b)

- Grupo 3: o trilho na Revisão e na etapa Classificação, e o "Confira" do corte por lista. Os
  ajustes CV-12 a CV-14 vão juntos se couberem.
- **Depende de** G1: se surgir a espécie "fixo no total", o "Confira" muda de texto.

**Entrega 4. "A prévia com os seus candidatos"** (P2)

- Grupo 4: primeiro o texto do escopo, que é imediato e pode ir na entrega 2. Depois, a população
  real em só leitura, se G3 for "sim".

**Por que esta ordem.**

1. A entrega 1 tira o único risco medido de erro administrativo, e é a menor.
2. A 2 responde à pergunta mais frequente: por que esta pessoa, por que esta vaga.
3. A 3 previne, mas atua uma vez por Edital.
4. A 4 espera decisão.

Nenhuma cria página nova: todas trocam ou acrescentam um bloco numa tela que existe.

---

## 6. Roteiro de validação com TI e negócio

**Participantes:** 2 ou 3 de negócio (presidência de comissão, quem publica) e 2 de TI (quem dará
suporte). A equipe inicial tem 2 a 3 pessoas, e os papéis se acumulam.

**Material:** os bancos de fase do 900 (§7) com o servidor no instante de cada tarefa; as telas atuais
e as maquetes. Metade das pessoas começa pelo atual, a outra metade pela proposta.

**Medidas fixadas antes:**

- acerto da próxima ação;
- quantas telas abriu;
- tentativas e erros, com recusas do sistema;
- se precisou de ajuda;
- confiança declarada de 1 a 5 antes do ato irreversível.

| # | Tarefa (instante) | Pergunta ao participante | Acerto esperado | O que mede |
|---|---|---|---|---|
| T1 | 10/12, preliminar publicada | "O que você faz agora no Edital 900?" | Esperar o prazo (ou emitir o corte **sabendo** o risco) | Identificar a próxima ação; segurança antes do ato |
| T2 | 14/12, cortes emitidos | "Quem faz a Entrevista, e por quê a Kátia vai?" | 12; Kátia pela PPI | Compreensão de dependências; telas abertas |
| T3 | 28/12, ordem final | "A Sofia pergunta por que ficou em 7º. Responda" | Empate em 75,67 com Caio, que tem a Entrevista maior (80 × 74) | Explicar sem ajuda; comparação manual |
| T4 | 29/12, apuração feita | "O que falta para as 6 vagas?" | Convocar os titulares do marco **final**; **não** apurar o marco 1 | Erro administrativo (CV-01) |
| T5 | 05/01, Bruno desistiu | "E agora?" | Chamar Diana para a vaga que vagou | Próxima ação; contradição entre telas (CV-03) |
| T6 | Composição (Revisão) | "Quantas pessoas, no máximo, podem ir à Entrevista?" | 24 (8 por lista) | Antecipação de consequência na configuração |
| T7 | Prévia | "Se a Prova fosse o 1º critério do marco final, mudaria quem se matricula?" | Sim (Sofia × Caio), e a prévia de hoje não responde | Escopo da simulação |

**Sucesso:**

- T4 e T5 com acerto em todos os participantes na proposta. Hoje, a expectativa medida pelo código é
  de erro sempre que a pessoa seguir o cartão.
- T2 e T3 sem abrir mais de uma tela.
- Confiança média ≥ 4 antes dos atos de T1 e T4.

Uma falha na proposta volta para a maquete antes da spec.

---

## 7. Como reproduzir

A partir de `backend/`, com o PostgreSQL local (`LC_ALL` exportado), cada banco com `DB_NAME` próprio:

| Banco | Estado | Instante para o servidor |
|---|---|---|
| `ps_conv_ux` | certame inteiro (`reproduzir.py tudo`) | 2027-01-06T12:00 |
| `ps_conv_t1` | f0–f3, f4a, e **um corte emitido antes da preliminar** (experimento), depois f4b, f5a e f5j | 2026-12-13T11:00 |
| `ps_conv_t2` | f0–f4 | 2026-12-10T09:00 |
| `ps_conv_t3` | + f5a, f5j (recurso deferido) | 2026-12-13T11:00 |
| `ps_conv_t4` | + f5s, f5b (cortes do marco 1) | 2026-12-14T16:00 |
| `ps_conv_t5` | + f6, f7, f8 (apuração do marco 2) | 2026-12-29T16:00 |
| `ps_conv_t6` | + f9c, f9a, conferências e desfechos de C01, C16 e C02 | 2027-01-05T14:10 |
| `ps_conv_t7` | + desistência de C13 | 2027-01-05T14:20 |
| `ps_conv_descartavel`, `ps_conv_t1b`, `ps_conv_t3b` | **cópias onde se praticou o ato errado** (CV-01, CV-04) | — |

- **A derivação, sem navegador:** `uv run python ../doc/estudo-convergencia-ux-2026-11-07/roteiro/sonda.py andamento <instante>`.
  Ela imprime o nível 1, a matriz e o "Próximo nesta lista" de cada lista e marco.
- **As capturas:** `servidor.py` do estudo de 07/11, com `RELOGIO`, e `capturar.py` com os planos de
  `roteiro/plano-t*.json`.
- **As maquetes:** `roteiro/maquetes.py`, com o Playwright do checkout principal.

**Limitações.**

- Nenhum teste com pessoas: o §6 é o próximo passo.
- O sorteio não foi percorrido de novo no navegador. Os achados de sorteio vêm do estudo do 35 e do
  código (as marcas da prévia).
- A família "sorteio com Etapa governada e marco posterior" (CV-01 no sorteio) foi deduzida de
  `_pontos_do_marco`, e não reproduzida.
- As maquetes não foram conferidas a 375 px nem com leitor de tela, e usam estilo injetado
  (`bypass_csp`). A implementação iria para a folha da tela.

---

## 8. Decisões que ficam com o usuário

- **R1.** O **comando** deve recusar apurar e convocar num marco cuja Etapa governada é lida por um
  marco posterior? Ou basta a derivação dizer *Não se aplica*? A cópia descartável mostra que hoje se
  convoca quem desistiu e quem ficou fora das vagas. **Recomendação:** recusar no comando. É o padrão
  da `128`: a porta de gravação, com a tela prevendo a recusa. Também é a única forma de cobrir o
  operador que chega pela URL, e não pelo cartão.
- **R2.** O corte com janela recursal aberta é **recomendação** ("aguarde") ou **impedimento**? Hoje o
  domínio aceita. **Recomendação:** recomendação, com a consequência visível (maquete A3). Impedir
  muda o rito de quem corta antes por prazo apertado de Etapa.
- **R3.** A explicação da posição (Grupo 2) é só da gestão, ou vai ao candidato? É a G5 do estudo de
  07/11, sobre o que é publicável e se a data de nascimento pode aparecer.
- **R4.** Abrir a Entrega 1 como spec agora, antes do teste do §6? **Recomendação:** sim. São defeitos
  medidos, e não hipóteses de UX. O teste vale para as Entregas 2 e 3.
- As decisões já abertas que esta proposta toca, sem decidir: **G1** (corte fixo por lista), **G3**
  (prévia com notas reais), **G6** e **Q8** (o que é "ocupada"), e a §9 do estudo de concomitância.
