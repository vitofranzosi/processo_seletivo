# Rodada 4: a visão reconsolidada (12/11/2026)

**A crítica.** O usuário trouxe uma avaliação das rodadas 1 a 3. Ela diz que o estudo começou com a
pergunta "como o GPS coordena o trabalho da comissão" e terminou com outra: "como reunir para uma
pessoa os links do que ela já pode executar". Pede três coisas:
- que a visão original fique explícita;
- que a distribuição de responsabilidades não vire possibilidade vaga;
- que "Minhas atividades" seja tratada como a primeira de três entregas.

**Veredito.** A crítica procede no essencial, e o estudo a adota, com três correções de fato e uma
condição para a terceira entrega.

## 1. Onde a crítica tem razão

**O estudo trocou a pergunta sem dizer.** A rodada 1 respondeu bem "o que eu posso executar agora".
Depois passou a tratar essa resposta como **a** solução. A pergunta do pedido era outra: um
presidente organiza e acompanha o trabalho da comissão, e cada integrante sabe o que fazer para o
Edital avançar. A primeira entrega cobre só a segunda metade dessa frase.

**A recusa da "designação informativa" foi absoluta demais.** A D-3 dizia "(c) não". O argumento
estava certo: uma linha em "Para fazer" que a pessoa não pode praticar é frustração. Mas ele recusava
uma coisa diferente da que o pedido descreve. Responsabilidade e autorização são eixos distintos, e o
estudo os juntou:
- "João responde pelo acompanhamento do sorteio" não precisa aparecer como ato executável;
- pode aparecer como trabalho **a acompanhar**, e na visão da presidência como **quem responde**.

O trabalho de uma comissão real não se esgota nos atos do GPS. Há a sessão pública do sorteio, a
conferência fora do sistema e o contato com o convocado. Dizer quem responde por cada frente tem
valor mesmo quando o ato formal é da presidência.

## 2. Onde a crítica precisa de correção

1. **A frase citada não está no estudo.** "A proposta não resolve, sozinha, a coordenação completa da
   seleção", e a menção a "sobrecarga", não aparecem em nenhum arquivo deste diretório. O diagnóstico
   da crítica não depende delas, mas o registro deve ser fiel.
2. **"Distribuir responsabilidades: não" e "acompanhar equipe: não" exageram.**
   - A rodada 1 já tinha "Quem faz o quê", no Centro, como primeiro item depois do MVP (D-5, e o
     wireframe 3). É a segunda entrega da crítica.
   - A distribuição que o GPS executa (alocação à Etapa, alocação à conferência, designação para a
     formalização) já existe, e a primeira entrega a lê.

   A divergência real é estreita: a responsabilidade **sem** autorização, que é a terceira entrega.
3. **"Do início ao encerramento" precisa respeitar uma recusa deliberada.** O encerramento nunca é
   providência: a fase Conclusão não diz "pode encerrar" (`interface/centro.py:543-552`). A revisão da
   página de processos de 06/11 mostrou que um sinal de "pronto para encerrar" é inseguro com cadastro
   de reserva. Cobrir o encerramento é **dizer o que ainda está em aberto antes da decisão**, e não
   transformá-la em tarefa.
   - A publicação das convocações (149) é diferente: é lacuna de cobertura, e já estava na D-5.

## 3. A visão de produto, explícita

> **Gestão operacional orientada do processo seletivo.** O GPS identifica, a partir das regras e do
> estado de cada Edital, o trabalho necessário para que ele avance. Cada integrante da comissão
> encontra o que é seu, sabe o que fazer e onde clicar. O presidente organiza quem responde por cada
> frente e acompanha o que está feito, em aberto, parado ou sem responsável, sem planilha paralela.

**Critério de sucesso final:** um presidente organiza e acompanha o trabalho da comissão, e cada
integrante encontra suas responsabilidades e sabe exatamente o que fazer para o Edital avançar.

**Fora da visão**, porque é o que o pedido recusa:
- tarefa cadastrada à mão;
- status marcado à mão sobre ato do GPS;
- prazo inventado;
- motor de workflow.

## 4. As três entregas

| # | Entrega | Pergunta | O que lê ou grava | Estado |
|---|---|---|---|---|
| 1 | **Minhas atividades**: execução pessoal | "o que eu faço agora?" | lê a derivação da 127 e as alocações. Nada novo gravado | pronta para spec (rodadas 2 e 3) |
| 2 | **Organização do trabalho**: visão da comissão | "quem responde por cada frente deste Edital, e o que está sem ninguém?" | lê as bases existentes: presidência, alocações, designação, papéis da unidade. Nada novo gravado | wireframe 3; pede cenários com alocação à conferência e recurso (V-8) |
| 3 | **Coordenação**: responsabilidade e acompanhamento | "quem acompanha cada frente, entre Editais, e onde há atraso ou acúmulo?" | **grava** a responsabilidade por frente, sem conceder base. O acompanhamento continua derivado | visão de produto; condicionada à evidência (§6) |

**"Previsto, em andamento, concluído, bloqueado" já existe por Edital.** São as situações da 127:
*Depois*, *Pendente*, *Feito*, *Impedido* e *Aguarda*. A terceira entrega as projeta por
responsável e entre Editais. Não cria status próprio.

## 5. O que a primeira entrega precisa preservar desde já

Estas escolhas não custam nada agora, e evitam que a primeira entrega feche a porta da terceira.

1. **A responsabilidade, quando existir, se prende a Edital × frente, e nunca à providência
   derivada.** Providências nascem e somem com o estado; uma responsabilidade presa a elas ficaria
   órfã na primeira Retificação. A taxonomia de frentes já existe: as macrofases do Centro
   (`centro.fase_da_providencia`, `conceitos.py`), de Publicação a Conclusão. A primeira entrega
   **agrupa e rotula por essa mesma taxonomia**, e não inventa outra.
2. **"Para fazer" é só executável.** A página nasce com seções nomeadas pelo tipo de relação, e não
   por natureza. Para as primeiras entregas: "Para fazer agora", "Em espera" e "Suas Etapas de
   avaliação". Para a terceira: "Para acompanhar". Nenhuma linha não executável entra em "Para
   fazer".
3. **Toda linha diz por que é sua.** A marca de base ("Presidência", "Alocação", "Designação") já foi
   adotada na rodada 2. A terceira entrega acrescenta "Responsável pela frente", sem mudar a
   gramática.
4. **A designação nova, se vier, é registro próprio, com trilha e revogação, e não reusa as tabelas
   de alocação.** Toda alocação existente concede base. Uma responsabilidade gravada nelas daria
   acesso por acidente.

## 6. A condição da terceira entrega

A terceira entrega **grava** algo, e por isso precisa de evidência de que a comissão real coordena
trabalho que o GPS não vê:
- a equipe inicial tem 2–3 pessoas acumulando papéis;
- nos cenários, toda condução é da mesma presidência.

Sem essa evidência, ela vira o Trello que o pedido recusa. A prova proposta:
- acompanhar **um Edital real** do início ao fim;
- listar o que a comissão coordenou;
- separar o que é ato do GPS do que é trabalho fora dele.

Se a lista de fora for curta, a segunda entrega basta. Se for longa, a terceira tem o seu
fundamento, e a lista vira o catálogo de frentes.

## 6a. Dois ajustes aceitos depois da rodada 4

O usuário trouxe dois ajustes, e o estudo os adota. Eles substituem o que conflitar no §3, no §4 e no
§6.

**O GPS só acompanha o que observa.**
- Um ato praticado no GPS aparece como feito, porque a derivação o lê.
- Uma preparação feita fora dele **nunca** aparece como concluída por inferência. Na frente, o GPS
  mostra a situação dos atos dele e o nome de quem responde. Sobre o trabalho externo, não diz nada.
- Três palavras precisam ser separadas:
  - **"Sem responsável"** é observável.
  - **"Parado há N dias"** é observável quando a derivação tiver `desde`. Ela não tem depois da
    publicação, e isso é a lacuna da D-5.
  - **"Atrasado"** exige um prazo definido. Pela D-4 não existe prazo da comissão, e por isso a
    palavra não entra.

  Onde o §3 diz "parado", entende-se "parado há N dias, quando observável". Em nenhuma entrega há
  "atrasado".

**A terceira entrega precisa de necessidade real, e não de volume.**
- Uma única responsabilidade importante e hoje mal representada basta para justificá-la. A régua do
  §6, "lista longa de trabalho externo", estava errada.
- A evidência se colhe **durante a operação**, sem esperar o encerramento de um Edital inteiro. Vale
  a primeira vez que a presidência precisar dizer "quem cuida disso" e o GPS não tiver onde.

**Consequência.** Seguem as entregas 1 e 2. A terceira fica registrada como direção, e se valida com
a comissão real. Um cadastro genérico de responsabilidades, construído agora, seria antecipação.

## 7. Decisões revistas

| # | Antes | Agora |
|---|---|---|
| D-3 | (a) agora; (b) depois; **(c) não** | (a) agora. **(c) passa a ser a terceira entrega**: responsabilidade por Edital × frente, sem base, em "Para acompanhar" e na visão da presidência, nunca em "Para fazer", condicionada ao §6. (b), a delegação com base, continua sendo spec de domínio própria, se a operação pedir |
| D-5 | "Quem faz o quê" e as coberturas, depois do MVP | as três entregas do §4. As coberturas (Publicador na unidade, atos que hoje são só acesso) entram na primeira ou na segunda, conforme o custo |
| **D-9** (nova) | — | **Aceitar a visão do §3 como norte das três entregas**, com o critério de sucesso final |
