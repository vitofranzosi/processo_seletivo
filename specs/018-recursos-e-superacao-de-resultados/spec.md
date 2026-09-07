# Feature Specification: Recursos e Superação de Resultados

**Feature Branch**: `claude/spec-018-recursos-6a3ffe`

**Created**: 2026-09-06

**Status**: Draft

**Input**: O candidato deve conseguir contestar um resultado que lhe diga respeito, e uma autoridade
imparcial deve conseguir decidir essa contestação de forma motivada, fazendo a decisão produzir seus
efeitos sem apagar ou reescrever os atos que historicamente aconteceram.

A 018 não calcula resultado, não ordena, não publica e não convoca. Ela recebe a contestação,
julga-a com autoridade própria e faz o deferimento produzir efeito **acrescentando** atos — nunca
alterando os que já existem.

---

## 1. O que já está fechado, e que a 018 consome

Esta feature começa depois da 017 e não redefine nenhum conceito das anteriores. O que segue não é
aspiração: é decisão tomada ou código existente, e é o chão sobre o qual a 018 é planejada.

### 1.1 A decisão C — como um recurso deferido supera um Resultado

Fechada em `doc/descoberta-018-decisao-c-superacao-de-resultado.md`, §1. Esta spec a **consome** e
não a rediscute:

- `ResultadoEtapa` é superado por **sucessor append-only** — nunca alterado, anulado, marcado nem
  apagado. Vigente é o Resultado que ninguém sucedeu, e a vigência é derivada da cadeia, como já é
  no `AtoDeOrdenacao` e na `PublicacaoResultado`;
- a decisão que **fixa diretamente** o resultado corrigido cria sucessor com origem `RECURSO`, que
  não cita Avaliação nenhuma e cita obrigatoriamente a decisão;
- decisão e Resultado sucessor nascem **na mesma transação**. Não existe estado "deferido,
  aguardando aplicação";
- a decisão que **ordena reavaliação** não cria sucessor: quem o produz é a consolidação da nova
  Avaliação, depois, e o estado intermediário é legítimo porque o resultado corrigido ainda não
  existe.

### 1.2 As sete decisões institucionais

Fechadas e aprovadas em 06/09/2026 em `doc/decisao-018-escopo-institucional-do-recurso.md`, §11. A
§2 desta spec as traduz em decisões de desenho; ela **não** reabre as alternativas descartadas.

### 1.3 O que o repositório já entrega, e que esta feature não constrói

- **A cadeia a jusante reage sozinha.** O `AtoDeOrdenacao` grava em `universo.stageResults` o
  conjunto de ids dos Resultados que o produziram; `comparar()` emite `resultados_alterados` quando
  esse conjunto muda; `estado_do_marco` marca o ato obsoleto; `aferir()` recusa a publicação
  nomeando o caminho — emitir o ato sucessor e publicar aquele. Nada disso é trabalho da 018.
- **A correção é sempre ato humano autorizado.** A cascata é de **bloqueio**, não de recálculo
  (015, D-002). Onde falta um fato, o remédio do produto é impedir o ato seguinte, e nunca produzir
  um ato por conta própria.
- **A reprodução histórica é imune por construção.** `reproduzir_ato` lê os Resultados por id do
  universo gravado; o Resultado superado permanece na tabela, imutável. A IO-5 da 015 permanece
  verdadeira sem cuidado adicional.
- **Titularidade já tem contrato.** `exigir_titularidade` compara `inscricao.identity_subject` com
  o `subject` da sessão do portal e recusa com **404**, porque dizer "existe, mas não é seu" já
  entrega que existe.
- **O `Impedimento` já existe**, ancorado em pessoa × inscrição, com motivo escrito e unicidade por
  par. É o mesmo conceito, e a 018 não cria um segundo.
- **O invólucro de comando já existe** — transação, bloqueio do contêiner, reavaliação da
  autorização **depois** do bloqueio, reserva da chave de idempotência, desfecho serializado — e é
  o que `consolidar`, `ocorrencia` e `emitir_ordem` usam.
- **A revisão otimista já tem forma**: `confirmacao_do_calculo` na 015 e a revalidação
  prévia→confirmação da 017, com recusa por estado obsoleto.
- **O marco enumera suas Etapas na norma publicada** (`marco["stages"]`), e essa enumeração é
  conteúdo normativo lido pela 015. É o fato que a §2 D-003 consome.
- **O Edital que o produto emite já promete recurso**: *"Caberá recurso contra os resultados
  divulgados, nos prazos do Cronograma"*. A 018 é o que torna essa promessa executável.

> O resultado existe, é oficial, é imutável e chegou à pessoa; falta a pessoa poder contestá-lo —
> e falta a instituição poder decidir essa contestação sem reescrever o que aconteceu.

---

## 2. Decisões fechadas antes do planejamento

### D-001 — Uma capacidade de recurso, dois objetos atacáveis

A V1 admite recurso contra **exatamente dois** objetos:

```text
PublicacaoResultado vigente de um marco classificatório      (o resultado divulgado)
ResultadoEtapa vigente do par Inscrição × Etapa              (o ato individual)
```

Existe **uma** capacidade de recurso, e o objeto atacado é um dado da peça — não um segundo
workflow. Interposição, admissibilidade, julgamento, motivação, proveniência, concorrência e
trilha são os mesmos nos dois casos; o que muda é qual identidade a peça nomeia e quais remédios
a decisão pode aplicar.

Construir dois fluxos paralelos duplicaria a máquina inteira para variar um campo, e faria a
linguagem ubíqua se partir em duas pelo canal em que a pergunta é feita — o que o Princípio I
proíbe.

**O objeto atacado e o lugar do erro são eixos distintos.** Recorrer da publicação não evita a
superação: um recurso cujo mérito é *"minha nota da Etapa 2 está errada"* ataca a publicação e
produz efeito no `ResultadoEtapa`. O mapa dos seis lugares em que o erro pode estar é o da §4 da
descoberta, e continua valendo — é ele, e não o objeto atacado, que diz qual remédio a decisão
aplica (D-009).

### D-002 — Somente o titular da Inscrição interpõe

Legitimidade é do titular, verificada pelo contrato de titularidade que já existe. A recusa é a
mesma 404 uniforme, pela mesma razão.

Não existem, na V1: terceiro interessado, procurador, representação, login delegado, impugnação por
concorrente. Cada um arrasta uma capacidade que o produto não tem — notificação num caso,
representação no outro — e nenhuma das duas é do escopo do recurso.

**A vedação é coerente com D-006**: *non reformatio in pejus* protege quem recorre do próprio
recurso, e a impugnação de terceiro é justamente o caminho legítimo pelo qual a situação de alguém
piora. Admitir a segunda sem contraditório seria adotar a piora sem defesa.

### D-003 — A visibilidade do Resultado da Etapa vem de um ato que já existe

Havendo `PublicacaoResultado` **vigente** de um marco do Perfil da Inscrição, e enumerando esse
marco a Etapa N, o titular passa a consultar, dentro da própria Inscrição, o seu `ResultadoEtapa`
**vigente** da Etapa N: consequência, motivo, pontuação quando a forma a tiver, e a informação de
superação quando o vigente for sucessor.

**Isto não transforma `ResultadoEtapa` em objeto de divulgação e não reabre a 017.** Não há ato de
publicação novo, não há lista pública de Resultados de Etapa, não há nome de terceiro, não há
parecer nem Avaliação. O que se mostra é o dado do próprio titular, autorizado por um ato
administrativo que a instituição já praticou, com autoridade, autor e instante.

A FR-056 da 017 continua verdadeira no que ela protege: é a publicação que abre a porta, e existir
`ResultadoEtapa` no banco continua não tornando nada público. O que muda é a **largura** da porta,
e quem a alarga é esta spec, pelo seu próprio texto — não retroativamente.

**Esta é a decisão que torna D-001 honesta.** Sem ela, a 018 entregaria recurso a quem chegou ao
fim e silêncio a quem foi eliminado cedo — reproduzindo, dentro da feature de recurso, a injustiça
que o E2E17-004 registrou.

**O que se mostra é sempre o vigente, e a superação precisa ser explicável a quem a recebe.**
Mostrar a nota nova sem dizer que ela mudou porque o recurso foi deferido transforma a correção em
erro aparente.

### D-004 — A janela recursal é conteúdo normativo do marco, e a ausência tem significado declarado

Esta é a única decisão da 018 com custo de esquema, e é o item a dimensionar primeiro no plano.

**O marco classificatório passa a poder declarar**, na norma publicada: se admite recurso, a duração
da janela, a unidade da contagem e o rótulo institucional que a nomeia. A janela é **ancorada na
publicação vigente do marco** — o instante que o sistema já grava e já exibe —, e não em datas
absolutas do Cronograma.

```text
declarada        →  o sistema calcula, exibe ao candidato e aplica a janela
não declarada    →  o sistema não inventa prazo; a interposição permanece possível e a
                    tempestividade é matéria de admissibilidade humana motivada
negada           →  o Edital declarou que aquele marco NÃO admite recurso; a interposição
                    por esta via é recusada, nomeando a norma
```

**Os três estados são respostas diferentes, e confundir os dois últimos inverte a norma.** A
ausência é silêncio: o Edital nada disse, e o sistema não decide por ele. A negativa é norma
publicada: o Edital disse que não cabe recurso, e norma publicada se aplica. Tratar a negativa como
silêncio transformaria *"não cabe recurso"* em *"cabe recurso para sempre"* — o oposto exato do que
foi publicado, e a favor de ninguém: nem do candidato, que receberia uma peça que a comissão não
tem como julgar, nem da instituição, que veria nascer recursos contra o que ela declarou
irrecorrível.

**A negativa não fecha a porta do candidato**, e a recusa diz isso: ele conserva as vias que a lei
lhe dá fora deste sistema, e a mensagem o encaminha à comissão do certame. O que o sistema recusa é
processar por dentro o que a norma não previu — não é o mesmo que declarar que não há remédio.

**Por que não se lê o Cronograma.** `EventoCronograma.type` é texto livre, sem validação, e o
próprio modelo registra a razão: *"inferir o período dali seria decidir uma regra de direito lendo
o que alguém digitou"*. Recusar um recurso por intempestividade é ato que restringe direito, e
fundamentá-lo em heurística de texto é indefensável na primeira contestação. Some-se o Princípio
II: o mesmo conteúdo publicado e o mesmo hash não podem responder coisas diferentes conforme a
heurística evolua.

**A unidade admitida na V1 é `DIAS_CORRIDOS`, e a escolha é sobre o que é reproduzível.** Contar
dias úteis exige calendário de dias sem expediente, que o domínio não publica; prorrogar o
vencimento que cai em dia sem expediente exige o mesmo calendário. Computar um vencimento sem eles
e depois recusar um recurso por intempestividade seria afirmar o que não se tem — o E2E17-005 de
novo, com mais passos. A unidade continua sendo **campo publicado**, porque a frase "5 dias
corridos" é normativa e aparece no documento; o vocabulário é que tem um valor só na V1. O Edital
que precise de dias úteis não declara a janela e recebe a degradação que esta mesma decisão
declara — que é honesta, e não uma perda.

**A contagem segue a regra geral do processo administrativo**: exclui-se o dia da publicação e
inclui-se o do vencimento; a janela fecha ao fim do último dia, na **zona temporal institucional**,
e não na do servidor. Abertura e fechamento são instantes exatos, exibidos ao candidato.

**Publicação sucessora e conteúdo novo.** A janela abre com a publicação vigente que divulga pela
primeira vez um determinado ato de ordenação. Publicação que apenas muda a natureza do **mesmo**
ato não abre janela nova, porque nada de novo foi divulgado para se contestar. Publicação de ato
**diferente** divulga conteúdo novo e abre janela nova — que é o resultado correto, porque contra
o conteúdo novo ninguém recorreu ainda.

**Editais anteriores ao degrau.** A ausência da declaração significa **janela não declarada**, e
não "janela de zero dias". Nenhum Edital publicado antes deste incremento pode ser punido por não
ter declarado o que não existia para ser declarado.

### D-005 — Julgar é capacidade própria, e o impedimento bloqueia

Julgar exige capacidade sistêmica própria, no mapa de papéis. Ela **não deriva** de presidir a
comissão, de integrá-la, de ter avaliado, de ter consolidado nem de ter emitido a classificação —
pela mesma arquitetura que a 017 escolheu para o caso simétrico ao separar constituir de divulgar.

Está **impedido** de decidir quem, para aquela Inscrição e aquela Etapa:

- concluiu a Avaliação que fundamentou o Resultado atacado ou o Resultado antecedente relevante;
- consolidou o Resultado atacado;
- constatou a Ocorrência que produziu o Resultado atacado;
- emitiu o ato de ordenação atacado, ou praticou a publicação atacada;
- possui `Impedimento` registrado para aquela Inscrição.

O impedimento **bloqueia**, e não apenas declara: decisão de quem está impedido é decisão viciada, e
declará-lo depois repete o padrão do E2E17-005 — um ato que afirma o que não tem.

**O impedimento recursal é o mesmo `Impedimento` da 012**, ampliado do avaliar para o julgar. A 012
o manteve fora da cadeia de autorização por custo de escala — uma verificação por linha em toda
listagem. **Julgamento é ponto único, não listagem**, e o custo que a 012 recusou não se coloca
aqui.

**A admissibilidade obedece às mesmas regras.** Inadmitir mata o recurso tão eficazmente quanto
indeferi-lo; permitir que o impedido o faça deixaria a porta aberta um passo antes.

**Quando o impedimento não deixa ninguém elegível, a saída é institucional, e não técnica**: sendo
capacidade do mapa, ela é concedida a quem está fora da comissão. Foi assim que
`resultado:publicar` resolveu o mesmo aperto.

### D-006 — *Non reformatio in pejus*, e a trava que a torna íntegra

Na V1, o recurso do próprio candidato **não pode piorar a sua situação**. Piorar significa, e
somente:

- **consequência** — `HABILITADA` virar `ELIMINADA`;
- **pontuação** — pontuação do sucessor menor que a do superado.

**A posição classificatória não entra na comparação.** O deferimento do recurso de outra pessoa pode
empurrar o recorrente para baixo na ordem, e isso não é *reformatio in pejus*: a garantia protege
quem recorre do efeito do **próprio** recurso sobre o **próprio** objeto. Dizer o contrário
congelaria a ordem inteira ao primeiro recurso.

Concluindo o julgamento por situação pior que a vigente, o recurso é **indeferido**: o Resultado
vigente permanece e nenhum sucessor pior nasce.

**A vedação alcança também a reavaliação ordenada no recurso.** Sem isso, D-006 é contornável pelo
caminho mais curto: basta ordenar reavaliação em vez de fixar a nota, e a piora entra pela porta de
trás com origem `AVALIACAO`. A nova Avaliação **pode ser registrada** — ela é o juízo do avaliador,
e apagá-lo seria mentir sobre o que ele concluiu —, mas o seu Resultado não é consolidado como
sucessor quando for pior que o superado protegido. Quem o consolidasse estaria executando, por
outro caminho, a decisão que esta vedação proíbe.

**A regra é política, e por isso vive no comando e no teste — não em constraint.** O esquema precisa
continuar admitindo o sucessor pior, porque a instituição pode adotar o agravamento com
contraditório depois, e porque a revisão de ofício produzirá exatamente esse sucessor. Revisão de
ofício é assunto futuro e **não deve ser simulada como recurso**.

### D-007 — Progressão retroativa: efeito pleno, com guarda de publicação e aviso nomeado

Recurso deferido produz **efeito pleno**. Superado o Resultado que eliminava a inscrição por outro
que a habilita, ela volta ao fluxo das Etapas seguintes pelas regras derivadas que já existem.

**Não se cria estado artificial de "reintegrado", e não se cria exceção de progressão.** Participação
e prontidão já são derivadas dos Resultados vigentes; removida a eliminação vigente, a inscrição
reaparece como pendente sozinha. Não há nada a construir para o **efeito** — o trabalho é de
**aviso**, e ele não é decoração:

1. na Mesa e no painel da Etapa, a linha reaberta é nomeada como tal — *"reabilitada por recurso
   deferido em DD/MM"* —, e não aparece como uma pendência qualquer que ninguém explica;
2. na tela do marco, a divergência de obsolescência diz a causa certa: **participante reingressou**,
   e não apenas "resultados alterados";
3. na prévia de publicação, o impedimento com o caminho a seguir.

**A guarda é de bloqueio, e não de recálculo.** Enquanto existir inscrição reabilitada por recurso e
ainda sem Resultado numa Etapa que o marco enumera, a publicação daquele marco é **impedida**, com
motivo nomeado. Impede-se que a instituição divulgue uma ordem que omite quem teve o direito
reconhecido; não se emite ato nenhum por conta própria.

**Limitar o efeito à Etapa do recurso fica registrado como possível e fora da V1**: exigiria ou uma
segunda fonte que a prontidão consultasse — o que o Princípio II proíbe —, ou um Resultado por
Ocorrência declarando não participação numa Etapa que a pessoa nunca fez, o que faria o registro
afirmar algo falso.

### D-008 — Definitividade: dois fatos verificados, um fato declarado, e o nome que vem da causa

Uma publicação não se torna `DEFINITIVA` por escolha de `<select>`. A natureza pretendida passa a
ser insumo da aferição de publicabilidade, e a publicação `DEFINITIVA` é **impedida** enquanto,
para o marco pertinente, existir:

1. **recurso pendente** — interposto e ainda sem admissibilidade, ou admitido e ainda sem
   julgamento;
2. **reavaliação determinada e ainda não cumprida**;
3. **providência a jusante determinada em deferimento e ainda não cumprida** (D-009, espécie 4);
4. **janela recursal estruturada ainda aberta**.

A `PRELIMINAR` continua livre **nesses quatro**: é ela o caminho de quem quer divulgar enquanto a
contestação corre, e é ela que abre o prazo.

**Dois outros fatos impedem as duas naturezas**, e não entram na lista acima porque a assimetria
não vale para eles:

5. **ato de ordenação obsoleto** — que a 017 já verifica;
6. **pendência reaberta por progressão retroativa** que afete o marco (D-007).

Os quatro primeiros são fatos da **disputa**: enquanto ela corre, divulgar como preliminar é o
caminho normal. Os dois últimos são do **conteúdo** do que se vai divulgar — ato obsoleto publica
ordem revogada, e reingresso pendente publica ordem que já se sabe incompleta. Nenhuma das duas
fica menos falsa por chamar-se preliminar, e chamá-la assim diria que a contestação ainda corre,
não que o conteúdo pode estar errado.

**Pertinência ao marco** alcança tanto o recurso contra a publicação daquele marco quanto o recurso
contra `ResultadoEtapa` de Etapa que o marco enumera, no mesmo Edital e Perfil. Sem isso, o recurso
individual seria o buraco por onde uma definitiva nasceria com um Resultado em disputa dentro dela.

**Quando o Edital não declara janela estruturada**, o publicador **declara expressamente**, no
próprio ato, que o prazo recursal aplicável se encerrou. A declaração tem autoria, instante e texto,
é gravada na publicação e é auditável — e é coisa diferente de uma opção de menu. Ela **não** simula
prazo calculado, e não é oferecida quando a janela é computável: ali o fato é verificado, e declarar
o que se pode verificar seria pedir à pessoa que respondesse pelo que o sistema sabe.

**Uma publicação definitiva que sucede outra definitiva continua sendo `DEFINITIVA`.** Não nasce
`DEFINITIVA_RETIFICADA`: vigência e natureza derivam da cadeia, e não de estado duplicado. O nome
vem do fato — *"Resultado definitivo, retificado em DD/MM em razão do julgamento do recurso R"* —,
texto derivado da cadeia e da causa, e não de coluna nova. Sendo mais de uma a causa, o texto as
nomeia **todas**: dois deferimentos que alcançam o mesmo marco se resolvem numa emissão só, e
nomear um deles omitiria quem recorreu e teve razão.

**Nenhuma exceção à regra da janela, e a razão é de alcançabilidade.** Uma redação anterior desta
decisão dispensava de janela nova a definitiva que corrige outra definitiva, temendo tornar o
deferimento inexecutável. A exceção não é necessária, e o cenário que a motivava se divide em dois:

- **com janela estruturada, ele não ocorre.** A `DEFINITIVA` só nasce com a janela fechada e sem
  recurso pendente; fechada a janela, a interposição é recusada. Recurso interposto antes impede a
  definitiva enquanto pendente, e deferido com correção obsoleta o ato — bloqueando aquela
  publicação. Não há caminho que produza uma definitiva e, depois dela, um deferimento sobre o
  mesmo conteúdo;
- **sem janela estruturada, não há janela para abrir.** A interposição permanece possível enquanto
  o objeto for vigente, e é por aí que o candidato prejudicado pelo conteúdo corrigido recorre — a
  definitiva retificada é objeto novo, e contra ela a interposição é nova.

Vale, portanto, a regra geral e uma só: a `DEFINITIVA` é impedida enquanto a janela ancorada na
publicação vigente estiver aberta. Se algum caminho não previsto produzir o cenário, o efeito é uma
**espera** até a janela fechar — e não um impasse: o Resultado corrigido já está em vigor, e o que
aguarda é apenas a divulgação da natureza definitiva.

### D-009 — As espécies de decisão são quatro, e a quarta não é invenção

O julgamento produz **uma** de quatro espécies, e a lista é derivada do mapa da §4 da descoberta —
os seis lugares em que o erro pode estar, e o remédio de cada um:

| espécie | quando | efeito |
|---|---|---|
| **INDEFERIDO** | o mérito não procede, ou proceder pioraria a situação (D-006) | nenhum. O vigente permanece |
| **DEFERIDO, com correção fixada** | a decisão declara ela mesma a consequência e, quando aplicável, a pontuação corrigida | Resultado sucessor com origem `RECURSO`, **na mesma transação** |
| **DEFERIDO, com reavaliação determinada** | o mérito procede e a correção exige juízo de avaliador competente | nenhum sucessor agora; a consolidação da nova Avaliação o produz depois |
| **DEFERIDO, com providência a jusante** | o erro não está em Resultado nenhum: está no cálculo, no desempate, no universo, na forma da divulgação ou na própria norma | nenhum sucessor de Resultado; a decisão nomeia a providência, que é ato de outra autoridade pela 015, pela 017 ou pela Retificação |

**A quarta espécie é necessária, e omiti-la produziria mentira.** Um recurso cujo mérito é *"o
desempate foi aplicado ao contrário"* procede sem que Resultado nenhum esteja errado. Sem a quarta
espécie, o julgador teria de indeferir um recurso procedente ou fabricar um sucessor de Resultado
para registrar um erro que não está lá. As três primeiras linhas da §4 da descoberta exigem
primitiva nova; as três últimas exigem que a decisão saiba **citar** o ato que a executa — o que é
vínculo de auditoria, e não mecanismo.

**A decisão nomeia a providência; ela não a executa.** Calcular, conferir e emitir continuam sendo
atos de quem tem a autoridade da 015 e da 017. A cascata é de bloqueio (D-007, D-008).

**O cumprimento é declarado pelo ato que o executa, e não por um ato próprio.** A pendência da
quarta espécie se fecha quando o **ato de ordenação que se publica cita a decisão** que a
determinou:

```text
cumprida, para um marco  →  o ato que se vai publicar cita a decisão
                            OU já existe, naquele marco, ato citante que foi publicado
pendente                 →  nenhuma das duas
```

**Citar é intenção; publicar é o remédio.** Um ato pode citar a decisão e nunca ser publicado — por
ficar obsoleto antes disso, por exemplo. Enquanto nenhum ato citante for publicado, a providência
continua pendente, e **qualquer sucessor do marco pode citar a decisão de novo**. É essa recitação
que impede o único beco possível deste desenho.

**O segundo ramo é o remédio já executado e divulgado.** Publicado o ato citante, um sucessor
posterior emitido por razão alheia não reabre a pendência — do contrário, toda emissão futura
exigiria recitar decisões antigas.

**A apuração é por marco.** Uma decisão cuja providência é normativa alcança todos os marcos que a
regra retificada governa, e cada um precisa do seu próprio ato citante publicado: o trabalho feito
num marco não libera a definitiva de outro.

**A citação é declarada por quem emite o ato sucessor**, entre as decisões pendentes daquele marco,
e é proveniência do próprio ato — do mesmo tipo de `motivo_da_sucessao`, que a 015 já exige. Ela não
tem autoridade, instante nem motivo próprios: quem a declara é quem emite, no ato de emitir.

**Por que não basta "publicar ato diferente".** Uma redação anterior desta decisão dava a pendência
por cumprida quando a publicação vigente divulgasse qualquer ato diferente do reconhecido viciado.
Isso quitaria a providência **por acidente**: um ato sucessor emitido por razão alheia — uma
Retificação que mudou um peso, um Resultado consolidado tarde — encerraria a pendência sem que
ninguém tivesse corrigido o vício que a decisão reconheceu. O vínculo precisa ser causal, e causal é
o que a citação declara.

**A regra não é circular, e não vira beco.** A publicação que executa o remédio **é** a que cita a
decisão, e por isso não é impedida por ela. Emitir ato sucessor citando a decisão está sempre
disponível, e a citação pode ser repetida quantas vezes for preciso enquanto nenhum ato citante for
publicado. Um mesmo ato pode citar mais de uma decisão pendente, de modo que dois deferimentos sobre
o mesmo marco se resolvem numa emissão só.

Disso decorrem três coisas que a spec **não** cria, e é deliberado:

- **nenhum ato de cumprimento com autoridade própria.** Um passo humano separado — alguém declarando,
  depois, que a providência foi cumprida — acrescentaria autoridade, tela e a possibilidade de
  travar o marco por esquecimento. A citação vive **dentro** do ato que executa, e não ao lado dele;
- **nenhuma espécie estruturada de providência.** O vocabulário só se justificaria se o cumprimento
  fosse verificado por espécie, e ele não é: é verificado pela citação. A providência é fundamentação
  escrita, como toda motivação desta feature;
- **nenhum ato de impossibilidade.** Removido o marco por Retificação, a 017 já recusa qualquer
  publicação daquele marco por razão própria e anterior — não há definitividade a desbloquear, e a
  pendência é inócua. Nos demais casos há sempre ato sucessor a emitir.

### D-010 — O Recurso é uma cadeia de atos; pendência é derivada, não coluna

O Recurso **não ganha máquina de estados persistida**. Ele é a peça interposta, e o que aconteceu
com ela é a existência dos atos que a alcançaram:

```text
peça interposta                       (o Recurso existe)
   └─ Juízo de Admissibilidade        (ato motivado: admitido | inadmitido)
        └─ Decisão de Recurso         (ato motivado: uma das quatro espécies de D-009)
```

A situação exibida deriva de quais atos existem, e não de coluna a manter coerente:

| situação exibida | é a ausência ou a presença de |
|---|---|
| aguardando admissibilidade | nenhum juízo de admissibilidade |
| inadmitido | juízo de admissibilidade negativo — terminal |
| aguardando julgamento | admitido, sem decisão |
| decidido | decisão existente |
| reavaliação determinada, não cumprida | decisão da terceira espécie, sem Resultado sucessor do par posterior a ela |
| providência determinada, não cumprida | decisão da quarta espécie que, para o marco pertinente, nenhum ato publicado cita |

É o mesmo idioma de `PENDENTE`/`CONSOLIDADO` na 013 e de vigência na 015 e na 017: **pendência
calculável não vira coluna porque facilita uma tela.** Os dois atos são imutáveis e append-only, como
todo ato administrativo desta linhagem.

### D-011 — A peça é fundamentação textual, e não há instância seguinte

**Sem anexos na V1.** Admitir prova nova em recurso é questão normativa que nenhum Edital lido
declarou, e abri-la pelo botão de anexar seria respondê-la por omissão. O mecanismo de documentos do
candidato continua existindo; quando houver norma que declare a admissibilidade de prova nova, ela
chega com o caso que a justifica.

**Sem segunda instância e sem pedido de reconsideração.** Decidido o recurso, aquele objeto não é
atacado de novo. O que nasce depois — Resultado sucessor, ato sucessor, publicação sucessora — é
**outro objeto**, e contra ele a interposição é nova, com a sua própria janela.

**No máximo um recurso por titular e objeto atacado.** A segunda interposição equivalente é
recusada nomeando o protocolo da primeira — pendente ou já decidida —, em vez de produzir duas peças
que dois julgadores decidiriam em direções opostas.

---

## 3. Contratos herdados e reuso obrigatório

Esta seção existe para que o planejamento não construa infraestrutura paralela à que o repositório
já consolidou. Cada item é obrigação, não sugestão.

| O que | De onde | O que isso proíbe |
|---|---|---|
| Superação por sucessor append-only, vigência derivada | `classificacao/models.py`, `divulgacao/models.py` | coluna de vigência, anulação, `UPDATE`, exclusão |
| Unicidade de raiz e de sucessor por constraint | as duas cadeias já existentes | unicidade como promessa de código |
| Invólucro transacional com autorização reavaliada após o bloqueio | `comissoes/application/__init__.py` | autorizar só na view; reservar antes de autorizar |
| Idempotência por reserva e desfecho preservado | `shared/idempotency.py` | chave própria, `get_or_create` como sucedâneo |
| Revalidação entre o que se leu e o que se confirma | `confirmacao_do_calculo` (015), prévia→confirmação (017) | confirmar sem reler, ou reler sem comparar |
| `Impedimento` por pessoa × inscrição | `avaliacoes/models.py` | segundo conceito de impedimento recursal |
| Titularidade e 404 uniforme | `inscricoes/domain/titularidade.py` | 403 que revela existência; identificador como credencial |
| Aferição de publicabilidade em três degraus | `divulgacao/domain/publicabilidade.py` | segunda máquina de recusa; publicar mediante confirmação adicional |
| Obsolescência derivada por diferença de universo | `classificacao/domain/universo.py` | segundo mecanismo de detecção paralelo ao que funciona |
| Degrau de elevação declarando o que a ausência significa | `publicacoes/domain/elevacao.py` | conteúdo novo sem caminho de leitura das versões anteriores |
| Zona temporal institucional | `interface/forms.py`, `interface/retificacao.py` | fuso do servidor em regra de calendário |
| Trilha de auditoria existente | `avaliacoes/application/trilha.auditar` | log paralelo, tabela de eventos própria |
| Portal Django para o candidato; interface administrativa para a comissão | `portal/`, `interface/` | endpoint JSON apresentado como canal do ator |
| Renderizador de documento existente | `publicacoes/infrastructure/pdf.py` | biblioteca nova de PDF |

---

## 4. Problema

O ciclo institucional fecha até a divulgação e para ali. A auditoria E2E-017 registrou a borda em
uma frase: *"o resultado está publicado, acessível e defensável. Ninguém é avisado, e não há por
onde recorrer."*

Três consequências, e as três são do produto:

```text
O Edital promete recurso            →  e o produto não oferece meio
"Resultado definitivo" é escolhido  →  sem que exista o fato que o legitima      (E2E17-005)
Quem foi eliminado cedo             →  não vê nem que houve resultado            (E2E17-004)
```

A 018 responde à pergunta que resta: **o candidato consegue recorrer de uma decisão que lhe afeta, a
instituição consegue julgar esse recurso com autoridade e imparcialidade, e o deferimento consegue
alterar legitimamente o estado vigente sem reescrever a história?**

---

## Clarifications

### Sessão 2026-09-06

Duas questões de governança que as sete decisões institucionais não alcançavam, e que mudavam o
texto da spec. Ambas decididas pelo usuário nesta sessão.

- Q: A janela recursal declara duração e unidade. "Dias úteis" não é reproduzível — o domínio não
  publica calendário de dias sem expediente, e a prorrogação do vencimento exige o mesmo calendário.
  Qual vocabulário a V1 admite? → A: **Somente dias corridos.** A contagem exclui o dia da
  publicação, inclui o do vencimento e fecha ao fim do último dia na zona institucional, sem
  prorrogação. O Edital que precise de dias úteis não declara a janela e recebe a degradação já
  decidida — tempestividade como juízo de admissibilidade motivado. Nada é computado sem lastro
  (D-004).
- Q: A peça recursal admite anexos? → A: **Não, na V1.** A peça é fundamentação textual. Admitir
  prova nova em recurso é questão normativa que nenhum Edital lido declarou, e abri-la pelo botão de
  anexar seria respondê-la por omissão (D-011).

### Sessão 2026-09-06 (segunda rodada, sobre a primeira leitura da spec)

Três pontos que a primeira redação deixou inconsistentes ou resolvidos por mecanismo a mais.

- Q: Como tratar a janela recursal depois de uma publicação definitiva ser corrigida por recurso
  deferido? → A: **Remover a exceção.** Ela era letra morta: com janela estruturada o cenário é
  inalcançável, porque a definitiva não nasce com recurso pendente e a interposição é recusada
  depois de fechada a janela; sem janela estruturada não há janela para abrir, e o candidato
  prejudicado pelo conteúdo corrigido recorre da nova publicação como de qualquer objeto vigente.
  Vale a regra geral, sem exceção, e o pior caso é uma espera (D-008).
- Q: Que fato encerra a pendência da quarta espécie de decisão, cujo remédio é ato de outra
  autoridade? → A: **Um fato derivado, sem registro de cumprimento com autoridade própria.** A
  primeira redação o fez derivar de "a publicação vigente divulga ato diferente", e a revisão do
  plano mostrou que isso quitaria a providência **por acidente** — um ato sucessor emitido por razão
  alheia encerraria a pendência sem que ninguém tivesse corrigido o vício. O vínculo passa a ser
  causal: o ato de ordenação **cita** a decisão, e a citação é declarada por quem emite o ato
  sucessor, como proveniência dele. A análise cruzada corrigiu a segunda metade: citar não basta —
  a providência só está cumprida quando um ato citante é **publicado**, a apuração é **por marco**, e
  a citação pode ser repetida enquanto nenhum ato citante o tiver sido (D-009, FR-089, FR-112).
- Q: A quarta espécie precisa de espécie estruturada de providência e de ato terminal de
  impossibilidade? → A: **Nenhum dos dois.** O cumprimento não é verificado por espécie, e a
  impossibilidade não produz beco — marco removido já impede qualquer publicação daquele marco pela
  recusa que a 017 tem. A providência é fundamentação escrita (D-009).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ver o próprio Resultado da Etapa (Priority: P1)

Como candidato, quero consultar, dentro da minha Inscrição, o Resultado que a instituição registrou
para mim em cada Etapa cujo marco já foi divulgado, para saber o que aconteceu comigo e de que ato
eu poderia recorrer.

**Por que P1**: não se recorre do que não se vê. Esta história é pré-requisito de jornada do recurso
individual e fecha o E2E17-004 pela raiz.

**Independent Test**: publicar o marco de um Perfil que enumera a Etapa 1; abrir o acompanhamento de
uma candidata eliminada naquela Etapa — fora do universo do ato — e conferir que ela vê a
consequência e o motivo escritos do seu Resultado, sem ver Resultado de terceiro.

**Cenários de aceitação**:

1. **Dado** que nenhuma publicação de marco do Perfil existe, **quando** o candidato abre o
   acompanhamento, **então** não vê Resultado de Etapa nenhum.
2. **Dado** que existe publicação vigente de um marco que enumera a Etapa 1, **quando** a candidata
   eliminada nessa Etapa abre o acompanhamento, **então** vê a consequência e o motivo do seu
   Resultado vigente da Etapa 1 — inclusive estando fora do universo do ato.
3. **Dado** um marco que enumera duas Etapas, **quando** o candidato abre o acompanhamento,
   **então** vê o seu Resultado vigente de cada uma delas, e nada de Etapa que nenhum marco
   publicado enumere.
4. **Dado** que o Resultado vigente é sucessor de outro, **quando** o candidato o consulta,
   **então** lê que ele corrigiu o anterior, por qual decisão e quando — e não uma nota trocada sem
   explicação.
5. **Dado** qualquer estado, **quando** o candidato consulta, **então** não alcança Resultado,
   parecer, Avaliação ou nome de outro candidato por caminho nenhum.

---

### User Story 2 — Interpor recurso, receber protocolo e acompanhar (Priority: P1)

Como candidato, quero contestar o resultado divulgado ou o meu Resultado de Etapa, informando a
fundamentação, e receber um protocolo que prove que interpus, para acompanhar a situação e ler a
decisão quando ela existir.

**Por que P1**: é a metade do candidato na capacidade central da feature. Sem ela, nada do resto tem
o que julgar.

**Independent Test**: a partir do resultado divulgado e do Resultado de Etapa visíveis, interpor
recurso com fundamentação, conferir o protocolo, reabrir o acompanhamento e ver a situação; repetir
a confirmação e verificar que existe um só recurso.

**Cenários de aceitação**:

1. **Dado** um resultado divulgado vigente que contempla a Inscrição, **quando** o titular abre a
   sua Inscrição, **então** a ação de recorrer lhe é oferecida ali mesmo, com o objeto atacado
   nomeado em linguagem institucional.
2. **Dado** o formulário aberto, **quando** o titular envia sem fundamentação, **então** a
   interposição é recusada: recurso sem fundamento não é peça.
3. **Dado** fundamentação informada, **quando** o titular confirma, **então** nasce o recurso com
   protocolo legível, instante, objeto atacado, identidade do ato que era vigente naquele instante e
   a versão normativa então vigente — e ele passa a ser consultável pelo titular.
4. **Dado** que a confirmação foi enviada duas vezes, **quando** a segunda chega, **então** o
   sistema devolve o desfecho da primeira e existe **um** recurso.
5. **Dado** um recurso do mesmo titular contra o mesmo objeto — pendente ou já decidido —,
   **quando** ele interpõe de novo, **então** a segunda peça é recusada nomeando o protocolo da
   primeira.
6. **Dado** que outra pessoa manipula o identificador da Inscrição ou do recurso, **quando** tenta
   interpor ou consultar, **então** recebe a mesma resposta de recurso não encontrado.
7. **Dado** um recurso decidido, **quando** o titular abre o acompanhamento, **então** lê a espécie
   da decisão, a motivação escrita, o autor e o instante, e — havendo correção — o que mudou.

---

### User Story 3 — Admitir ou inadmitir, e julgar com imparcialidade (Priority: P1)

Como autoridade com capacidade de julgar recurso, quero ver os recursos recebidos, decidir a
admissibilidade e julgar o mérito com motivação escrita, sem que quem produziu o ato atacado possa
decidir sobre ele.

**Por que P1**: é a metade institucional da capacidade central, e é onde a imparcialidade deixa de
ser promessa.

**Independent Test**: conceder a capacidade a duas pessoas, uma delas a que consolidou o Resultado
atacado; verificar que a segunda é recusada na admissibilidade e no julgamento, e que a primeira
conclui os dois atos com motivo gravado.

**Cenários de aceitação**:

1. **Dado** um ator sem a capacidade de julgar — inclusive o presidente da comissão e o avaliador
   da Etapa —, **quando** tenta abrir a lista de recursos ou decidir, **então** a operação é
   recusada e a ação não lhe é oferecida.
2. **Dado** um ator com a capacidade que concluiu a Avaliação fonte, consolidou o Resultado, emitiu
   o ato ou praticou a publicação atacada, **quando** tenta admitir ou julgar, **então** a operação
   é recusada e a recusa nomeia o impedimento.
3. **Dado** um ator com a capacidade e `Impedimento` registrado para aquela Inscrição, **quando**
   tenta decidir, **então** a operação é recusada pela mesma porta.
4. **Dado** um julgador elegível, **quando** ele admite ou inadmite o recurso, **então** o ato é
   gravado com autor, instante e motivo, e passa a ser consultável pelo titular.
5. **Dado** um recurso não admitido, **quando** alguém tenta julgá-lo no mérito, **então** a
   operação é recusada: receber a peça não é admiti-la.
6. **Dado** dois julgadores decidindo o mesmo recurso ao mesmo tempo, **quando** o segundo confirma,
   **então** existe uma decisão só e ele recebe recusa por estado obsoleto, com o que já foi
   decidido.
7. **Dado** um recurso julgado, **quando** alguém tenta decidi-lo de novo, **então** a operação é
   recusada: decisão de recurso é ato imutável.

---

### User Story 4 — Deferir fixando a correção (Priority: P1)

Como julgador, quero deferir o recurso declarando eu mesmo a consequência e, quando aplicável, a
pontuação corrigida, para que a correção produza efeito imediato sem que o Resultado anterior seja
alterado.

**Por que P1**: é o efeito que dá sentido ao recurso, e é o consumo integral da decisão C.

**Independent Test**: deferir com correção sobre um Resultado que eliminava a inscrição; conferir
que o Resultado anterior permanece íntegro, que o sucessor é o vigente, que o ato de ordenação
ficou obsoleto e que a publicação daquele ato passou a ser recusada com o caminho nomeado.

**Cenários de aceitação**:

1. **Dado** um recurso admitido contra Resultado de Etapa pontuada, **quando** o julgador defere
   fixando pontuação superior, **então** nascem, na mesma transação, a decisão imutável e o
   Resultado sucessor que a cita, com origem em recurso e sem citar Avaliação nenhuma.
2. **Dado** o deferimento concluído, **quando** o histórico do par é consultado, **então** os dois
   Resultados aparecem em ordem, com motivo, autor, instante e a decisão que autorizou a superação.
3. **Dado** o Resultado sucessor, **quando** o marco é aberto na interface administrativa,
   **então** o ato vigente aparece obsoleto, com a causa nomeada, e a publicação daquele ato é
   recusada indicando emitir o sucessor.
4. **Dado** um ato de ordenação emitido antes do deferimento, **quando** ele é reproduzido a partir
   da sua proveniência, **então** produz exatamente a ordem que constituiu, com as entradas de
   então.
5. **Dado** que a correção proposta declararia consequência ou pontuação pior que a vigente,
   **quando** o julgador confirma, **então** nenhum sucessor nasce e o desfecho é indeferimento
   (D-006).
6. **Dado** que o Resultado vigente do par mudou entre a leitura e a confirmação, **quando** o
   julgador confirma, **então** a operação é recusada por estado obsoleto e nada é gravado.
7. **Dado** um recurso contra Resultado por Ocorrência, **quando** o julgador defere declarando
   desfecho sem grandeza, **então** o sucessor registra a consequência e o motivo, sem forma, sem
   pontuação e sem sentido.

---

### User Story 5 — Deferir determinando reavaliação (Priority: P2)

Como julgador, quero deferir determinando que a Etapa seja reavaliada por avaliador competente,
quando a correção exige juízo que não é meu, para que a decisão fique registrada sem antecipar um
resultado que ainda não existe.

**Por que P2**: é a segunda espécie de efeito, e é o que impede a decisão de fabricar avaliação.

**Independent Test**: deferir determinando reavaliação; conferir que nenhum Resultado sucessor
nasceu, que a Etapa apresenta a pendência nomeada, que a nova Avaliação é distribuível e que a
consolidação dela produz o sucessor citando a decisão.

**Cenários de aceitação**:

1. **Dado** um recurso admitido, **quando** o julgador defere determinando reavaliação, **então** a
   decisão é gravada com a determinação escrita e **nenhum** Resultado sucessor nasce.
2. **Dado** a reavaliação determinada, **quando** a presidência abre a organização da Etapa,
   **então** a inscrição aparece com a pendência nomeada — reavaliação determinada, não cumprida —
   e não como já consolidada.
3. **Dado** que quem concluiu a Avaliação original tenta concluir a reavaliação, **então** ele não
   consegue: a segunda conclusão da mesma pessoa sobre o mesmo par não existe.
4. **Dado** a nova Avaliação concluída e elegível, **quando** ela é consolidada, **então** nasce o
   Resultado sucessor citando a decisão que determinou a reavaliação, e o anterior permanece
   íntegro.
5. **Dado** que a nova Avaliação produziria consequência ou pontuação pior que o Resultado
   superado protegido, **quando** a consolidação é tentada, **então** ela é recusada nomeando a
   vedação, a Avaliação permanece registrada e nenhum sucessor pior nasce.
6. **Dado** a reavaliação determinada e não cumprida, **quando** alguém tenta publicar o marco como
   definitivo, **então** a operação é recusada com a pendência nomeada.

---

### User Story 6 — Declarar, exibir e aplicar a janela recursal (Priority: P2)

Como quem elabora o Edital, quero declarar que um marco admite recurso e por quanto tempo, para que
o candidato veja o prazo e o sistema o aplique — e, não declarando, para que ninguém invente prazo
nenhum.

**Por que P2**: é o que transforma tempestividade em regra reproduzível, e é o único item da 018 com
custo de conteúdo publicado.

**Independent Test**: declarar a janela num marco, publicar o Edital, publicar o resultado e
conferir que o candidato vê a abertura e o fechamento exatos; interpor dentro e depois do prazo;
repetir tudo num Edital publicado antes do incremento.

**Cenários de aceitação**:

1. **Dado** o assistente de elaboração, **quando** o marco é composto, **então** é possível declarar
   que ele admite recurso, por quantos dias e em que unidade — e a declaração aparece no documento
   publicado e é endereçável por Retificação.
2. **Dado** um marco com janela declarada, **quando** o resultado é publicado, **então** o candidato
   vê, na página e na sua Inscrição, o instante de abertura e o de encerramento, na zona temporal
   institucional.
3. **Dado** a janela aberta, **quando** o titular interpõe, **então** o recurso nasce registrando
   que estava dentro do prazo computável.
4. **Dado** a janela encerrada, **quando** o titular tenta interpor, **então** a operação é recusada
   nomeando a norma, a abertura e o encerramento — e a ação não é oferecida na tela.
5. **Dado** um Edital que não declara janela, **quando** o titular abre o resultado, **então** não
   há prazo exibido nem inventado, a interposição permanece possível e a peça registra que não havia
   janela computável.
6. **Dado** uma publicação sucessora que divulga ato de ordenação diferente, **quando** ela entra em
   vigor, **então** uma janela nova abre a partir dela; publicação que só muda a natureza do mesmo
   ato não abre janela nova.
7. **Dado** um Edital publicado antes deste incremento, **quando** ele é lido, retificado ou
   consultado, **então** a ausência da declaração significa janela não declarada, e nada nele é
   recusado por isso.

---

### User Story 7 — Publicar como definitivo com lastro (Priority: P2)

Como autoridade publicadora, quero que o sistema me impeça de chamar de definitivo um resultado que
ainda está em disputa, e me exija declarar expressamente o encerramento do prazo quando ele não for
computável, para que a natureza do ato deixe de ser uma afirmação sem lastro.

**Por que P2**: fecha o E2E17-005, que é o achado que a 018 foi apontada para resolver.

**Independent Test**: tentar publicar como definitivo com recurso pendente, com reavaliação
pendente, com janela aberta e com pendência reaberta; resolver cada um e conferir que a publicação
passa a ser permitida.

**Cenários de aceitação**:

1. **Dado** um recurso pendente pertinente ao marco, **quando** a autoridade tenta publicar como
   definitivo, **então** a operação é recusada nomeando a pendência; publicar como preliminar
   continua possível.
2. **Dado** uma reavaliação determinada e não cumprida, ou uma providência a jusante não cumprida,
   **quando** a autoridade tenta publicar como definitivo, **então** a operação é recusada com o
   motivo nomeado.
3. **Dado** uma janela recursal estruturada ainda aberta, **quando** a autoridade tenta publicar
   como definitivo, **então** a operação é recusada informando o instante em que a janela fecha.
4. **Dado** que o Edital não declara janela estruturada, **quando** a autoridade publica como
   definitivo, **então** o sistema exige a declaração expressa de encerramento do prazo, e a grava
   com autor, instante e texto.
5. **Dado** que todas as pendências foram resolvidas, **quando** a autoridade publica como
   definitivo, **então** a publicação nasce normalmente.
6. **Dado** um Edital sem janela estruturada e um recurso deferido depois de uma publicação
   definitiva, **quando** o ato sucessor é publicado, **então** a publicação sucessora é definitiva,
   exige nova declaração expressa de encerramento do prazo e é apresentada pela causa — resultado
   definitivo, retificado em tal data em razão do julgamento do recurso.
7. **Dado** um deferimento com providência a jusante, **quando** a autoridade tenta publicar como
   definitivo um ato que **não cita** a decisão, **então** a operação é recusada nomeando a decisão e
   o caminho; emitido o ato sucessor que a cita, a mesma publicação passa — e um ato sucessor
   emitido por razão alheia não cumpre a providência.
8. **Dado** a publicação vigente, **quando** alguém a abre, **então** ela diz que é a vigente — e
   não apenas a anterior diz que foi sucedida.

---

### User Story 8 — A reabilitação aparece na operação (Priority: P3)

Como presidência da comissão, quero que uma inscrição reabilitada por recurso apareça nomeada como
tal nas Etapas seguintes, para saber por que uma Etapa que eu considerava encerrada voltou a ter
pendência.

**Por que P3**: o efeito acontece sozinho; o que falta é ele ser descoberto por aviso, e não por
acaso.

**Independent Test**: deferir recurso que reabilita uma inscrição eliminada na Etapa 1, com a Etapa
2 já consolidada para todos os demais; abrir a Etapa 2 e a tela do marco.

**Cenários de aceitação**:

1. **Dado** o deferimento que habilita a inscrição na Etapa 1, **quando** a presidência abre a Etapa
   2, **então** a inscrição aparece como pendente e nomeada — reabilitada por recurso deferido em
   tal data —, e pode ser distribuída, avaliada e consolidada normalmente.
2. **Dado** a mesma situação, **quando** a tela do marco é aberta, **então** a divergência de
   obsolescência nomeia a causa como participante reingressado, e não apenas como resultados
   alterados.
3. **Dado** a inscrição reaberta e ainda sem Resultado numa Etapa que o marco enumera, **quando**
   alguém tenta publicar aquele marco, **então** a operação é recusada nomeando a pendência
   reaberta e o caminho.
4. **Dado** o Resultado da Etapa 2 finalmente consolidado, **quando** a publicação é tentada de
   novo, **então** a pendência reaberta deixou de existir e o impedimento correspondente não
   aparece.

---

### Edge Cases

- **O objeto atacado é superado entre a leitura e a confirmação da interposição.** A confirmação
  carrega a identidade do que foi lido; divergência recusa a peça, informa que o objeto mudou e
  oferece o objeto vigente — em vez de nascer um recurso contra um ato que já não vale.
- **O objeto atacado é superado depois da interposição e antes do julgamento.** O recurso continua
  existindo e é julgado: ele registra o que era vigente quando foi interposto. A decisão que fixa
  correção opera sobre o **vigente do par no instante do julgamento**, e a recusa por estado
  obsoleto protege o julgador de decidir sobre o que já mudou.
- **Duas interposições equivalentes do mesmo titular**, concorrentes: uma peça nasce, a outra é
  recusada nomeando o protocolo da primeira.
- **Dois julgadores decidindo o mesmo recurso**: uma decisão nasce; a segunda recebe recusa por
  estado obsoleto, com o que já foi decidido.
- **Dois deferimentos com correção sobre o mesmo Resultado vigente**: um sucessor nasce; o outro é
  recusado pela unicidade de sucessor, no banco, e não por leitura prévia.
- **Reavaliação concluída e consolidada enquanto outro recurso do mesmo par é decidido**: a
  unicidade de sucessor resolve, e o perdedor recebe recusa explícita.
- **Publicação definitiva concorrendo com interposição.** As duas serializam no mesmo contêiner. Se
  a publicação vence, ela era legítima no seu instante e permanece; o recurso interposto depois é
  recebido normalmente, e o remédio de um eventual deferimento é a publicação sucessora definitiva
  de D-008. Se a interposição vence, a publicação definitiva é recusada com a pendência nomeada.
- **Confirmação enviada de uma página obsoleta**, em qualquer dos atos: recusa por estado obsoleto,
  com o que mudou, e nada é gravado.
- **Recurso contra Resultado de Etapa que nenhum marco publicado enumera**: a ação não existe,
  porque o Resultado não é visível ao titular — o fato autorizador de D-003 não ocorreu.
- **Marco removido por Retificação depois da interposição**: o recurso continua existindo e
  consultável, e continua podendo ser julgado quanto ao Resultado individual. A providência a
  jusante que dependa do marco removido é dita impossível **na motivação**, e não simulada — e ela
  não bloqueia nada, porque a 017 já recusa qualquer publicação daquele marco por razão própria e
  anterior. Restabelecido o marco por Retificação, um ato novo é emitido e a pendência se fecha pelo
  fato derivado da FR-089.
- **Providência determinada e nunca praticada**: o marco permanece sem publicação definitiva, e isso
  é o comportamento correto — é a mesma cascata de bloqueio que a recusa por ato obsoleto já produz.
  Não é beco: emitir ato sucessor e publicá-lo está sempre disponível, e a recusa nomeia esse
  caminho.
- **Janela declarada, publicação atrasada**: a janela abre no instante em que a publicação existe,
  e não antes. Publicação atrasada não produz prazo vencido antes de existir.
- **Retificação que altera a duração da janela depois de publicado o resultado**: vale a norma
  vigente citada pela publicação que ancora a janela; a Retificação alcança o conteúdo futuro, e
  não recalcula prazo já em curso.
- **Deferimento que habilita quem já estava habilitado, ou que fixa a mesma pontuação**: não é
  piora, e não é correção — o desfecho é indeferimento por ausência de efeito, com motivo escrito.
- **Recurso contra publicação cujo mérito é a nota**: procede; ataca a publicação e produz efeito no
  `ResultadoEtapa`. Objeto atacado e lugar do erro são eixos distintos.
- **Inadmissão**: é ato motivado, consultável pelo titular, e não desaparecimento silencioso da
  peça.
- **A Etapa reaberta pela reavaliação não tem avaliador elegível** — todos impedidos ou alocados:
  a operação recusa nomeando a falta, e a saída é institucional (alocar outro membro), não técnica.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Objeto, legitimidade e interposição

- **FR-001**: O sistema MUST admitir recurso contra a `PublicacaoResultado` vigente de um marco
  classificatório e contra o `ResultadoEtapa` vigente do par Inscrição × Etapa, e contra nenhum
  outro objeto na V1.
- **FR-002**: A capacidade MUST ser **uma**: interposição, admissibilidade, julgamento, motivação,
  proveniência, concorrência e trilha são os mesmos para os dois objetos, e o sistema MUST NOT
  construir dois fluxos paralelos.
- **FR-003**: Cada recurso MUST nomear exatamente um objeto atacado, pela identidade dele.
- **FR-004**: Somente o titular da Inscrição MUST poder interpor, e a titularidade MUST ser
  verificada pelo contrato existente, com a mesma resposta uniforme de recurso não encontrado para
  quem não é titular.
- **FR-005**: O sistema MUST NOT implementar terceiro interessado, procurador, representação, login
  delegado ou impugnação por concorrente.
- **FR-006**: A interposição MUST exigir fundamentação escrita, e MUST recusar a peça sem ela.
- **FR-007**: A interposição MUST NOT aceitar anexos na V1 (D-011).
- **FR-008**: O recurso MUST receber protocolo próprio, legível e opaco, no mesmo padrão de
  legibilidade já adotado pelo protocolo da Inscrição, e o protocolo MUST NOT conferir autorização.
- **FR-009**: A confirmação da interposição MUST carregar a identificação do objeto que foi lido, e
  divergência entre o lido e o vigente MUST recusar a peça informando o objeto vigente.
- **FR-010**: Repetir a confirmação com a mesma chave MUST devolver o desfecho da primeira e MUST
  NOT criar segunda peça.
- **FR-011**: MUST existir no máximo um recurso por titular e objeto atacado; a segunda
  interposição MUST ser recusada nomeando o protocolo da primeira, esteja o primeiro pendente ou já
  decidido (FR-012).
- **FR-012**: Decidido o recurso, o mesmo objeto MUST NOT ser atacado de novo; objeto sucessor é
  objeto novo, com interposição e janela próprias (D-011).
- **FR-013**: A ação de recorrer MUST ser oferecida ao titular a partir do objeto que ele já
  consulta — o resultado divulgado e o Resultado da Etapa —, e MUST NOT aparecer quando a
  interposição não é possível.

#### Visibilidade do Resultado individual da Etapa

- **FR-014**: Havendo `PublicacaoResultado` vigente de um marco do Perfil da Inscrição que enumere a
  Etapa N, o titular MUST poder consultar o seu `ResultadoEtapa` vigente da Etapa N: consequência,
  motivo e pontuação quando a forma a tiver.
- **FR-015**: A visibilidade MUST alcançar o titular que **não** está no universo do ato, e MUST NOT
  depender de existir situação divulgada para ele.
- **FR-016**: O que se mostra MUST ser sempre o Resultado **vigente**; quando ele for sucessor, a
  consulta MUST dizer que houve correção, por qual decisão e quando.
- **FR-017**: O sistema MUST NOT publicar `ResultadoEtapa` como lista pública, MUST NOT nomear
  terceiros, e MUST NOT expor Avaliação, parecer ou proveniência interna ao candidato.
- **FR-018**: Etapa que nenhum marco publicado enumere MUST NOT ter Resultado exibido ao candidato.
- **FR-019**: A 018 MUST NOT criar ato de divulgação de `ResultadoEtapa` nem abstração genérica de
  publicável.

#### Janela recursal

- **FR-020**: O marco classificatório MUST poder declarar, no conteúdo normativo publicado, que
  admite recurso, a duração da janela e a unidade da contagem.
- **FR-021**: A unidade admitida na V1 MUST ser dias corridos; declaração em outra unidade MUST ser
  recusada na publicação, nomeando a razão (D-004).
- **FR-022**: A janela MUST ser ancorada no instante da `PublicacaoResultado` vigente do marco, e
  MUST NOT ser inferida do Cronograma, de `EventoCronograma.type`, de texto livre ou de heurística.
- **FR-023**: A contagem MUST excluir o dia da publicação e incluir o do vencimento, e a janela MUST
  fechar ao fim do último dia na zona temporal institucional.
- **FR-024**: Abertura e encerramento MUST ser instantes exatos, exibidos ao candidato e registrados
  na peça interposta.
- **FR-025**: Publicação sucessora que divulga ato de ordenação diferente MUST abrir janela nova;
  publicação que apenas muda a natureza do mesmo ato MUST NOT abrir janela nova.
- **FR-026**: Havendo janela declarada e encerrada, a interposição MUST ser recusada, nomeando a
  norma, a abertura e o encerramento.
- **FR-027**: Quando mais de um marco publicado enumerar a Etapa do Resultado atacado, a
  interposição MUST ser possível enquanto qualquer uma das janelas correspondentes estiver aberta.
- **FR-028**: Não havendo janela declarada, o sistema MUST NOT exibir, calcular ou aplicar prazo
  algum, e a interposição MUST permanecer possível enquanto o objeto atacado for vigente.
- **FR-029**: O sistema MUST elevar a versão do conteúdo canônico ao introduzir a janela, e MUST
  declarar que a ausência da declaração, em conteúdo anterior, significa **janela não declarada**.
- **FR-113**: Declarando o marco que **não** admite recurso, a interposição contra a publicação
  daquele marco, e contra o `ResultadoEtapa` de Etapa que somente marcos assim enumerem, MUST ser
  recusada nomeando a norma, e a ação MUST NOT ser oferecida na tela. A negativa declarada MUST NOT
  ser tratada como ausência de declaração — que é o caso da FR-028 —, e quando outro marco publicado
  enumerar a mesma Etapa e admitir recurso, a FR-027 MUST prevalecer. A recusa MUST distinguir-se,
  por código próprio, da recusa por janela encerrada da FR-026: a primeira diz que o recurso não é
  previsto, e a segunda, que o prazo dele passou (D-004).
- **FR-030**: A declaração da janela MUST ser escrita pelo assistente de elaboração, MUST aparecer
  no documento publicado e MUST ser endereçável pelo catálogo de Retificação por identidade estável.

#### Admissibilidade

- **FR-031**: Receber a peça e admitir a peça MUST ser atos distintos: a existência do recurso MUST
  NOT significar que ele foi admitido.
- **FR-032**: O juízo de admissibilidade MUST ser ato motivado, com autor e instante, e MUST ser
  consultável pelo titular.
- **FR-033**: Havendo janela estruturada, a intempestividade MUST ser impedida na interposição
  (FR-026), e MUST NOT ser matéria de admissibilidade.
- **FR-034**: Não havendo janela estruturada, a tempestividade MUST ser juízo humano motivado no
  ato de admissibilidade.
- **FR-035**: O sistema MUST NOT criar causas automáticas de inadmissibilidade. As recusas que o
  sistema pratica sozinho — falta de titularidade, objeto inexistente ou superado, janela declarada
  encerrada e recurso duplicado — incidem todas na **interposição**, antes de a peça existir; o que
  chega ao juízo de admissibilidade é matéria humana e motivada.
- **FR-036**: Recurso não admitido MUST NOT ser julgado no mérito.

#### Autoridade para julgar, e impedimento

- **FR-037**: Admitir e julgar MUST exigir capacidade institucional própria de julgamento de
  recurso, reconciliada com o mapa de papéis existente.
- **FR-038**: A autorização MUST NOT derivar de presidir a comissão, de integrá-la, de ter avaliado,
  de ter consolidado, de ter constatado ocorrência, de ter emitido o ato classificatório nem de ter
  publicado.
- **FR-039**: MUST ser impedido de admitir e de julgar quem, para aquela Inscrição e aquela Etapa,
  concluiu a Avaliação fonte relevante, consolidou o Resultado atacado, constatou a Ocorrência que o
  produziu, emitiu o ato de ordenação atacado ou praticou a publicação atacada.
- **FR-040**: MUST ser impedido quem possui `Impedimento` registrado para aquela Inscrição, e o
  sistema MUST usar o `Impedimento` existente, sem criar segundo conceito.
- **FR-041**: O impedimento MUST **bloquear** o ato, e MUST NOT apenas declará-lo depois.
- **FR-042**: A recusa por impedimento MUST nomear a razão ao ator impedido, sem expor dado pessoal
  de candidato a quem não pode vê-lo.
- **FR-043**: A autorização e o impedimento MUST ser reavaliados dentro do ato protegido, depois do
  bloqueio e antes de gravar.

#### Decisão: espécies, motivação e imutabilidade

- **FR-044**: A decisão MUST ser de uma de quatro espécies: indeferimento; deferimento com correção
  fixada; deferimento com reavaliação determinada; deferimento com providência a jusante (D-009).
- **FR-045**: Toda decisão MUST ter motivação escrita, autor, instante e a versão normativa sob a
  qual foi tomada.
- **FR-046**: A decisão MUST ser imutável: não é editada, não é excluída e não é revista pela V1.
- **FR-047**: MUST existir no máximo uma decisão por recurso, e tentativas concorrentes MUST
  produzir uma só, com a segunda recusada por estado obsoleto.
- **FR-048**: A decisão MUST ser consultável pelo titular, em linguagem institucional, sem
  identificador técnico e sem enum canônico.
- **FR-049**: A decisão da quarta espécie MUST nomear a providência, e MUST NOT executá-la: emitir
  ato sucessor, publicar sucessora e retificar continuam sendo atos de outras autoridades.
- **FR-050**: O sistema MUST NOT criar espécie, estado ou taxonomia além das necessárias, e MUST NOT
  simular revisão de ofício como recurso.

#### Efeito sobre o Resultado — superação append-only

- **FR-051**: O `ResultadoEtapa` MUST ser superado por sucessor append-only; o sistema MUST NOT
  alterar, anular, marcar nem excluir Resultado algum.
- **FR-052**: Para cada par Inscrição × Etapa MUST existir no máximo um Resultado **vigente**, e a
  garantia MUST ser de banco — unicidade da raiz e unicidade do sucessor —, e não de leitura da
  aplicação.
- **FR-053**: A cadeia MUST ser linear e do mesmo par: todo sucessor cita exatamente um superado, do
  mesmo Edital, Inscrição e Etapa; nenhum Resultado sucede a si mesmo nem fecha ciclo.
- **FR-054**: Todo Resultado sucessor MUST citar a decisão que o autorizou, e a citação MUST ser
  obrigatória qualquer que seja a sua origem.
- **FR-055**: Consolidação **ordinária** e constatação de ocorrência MUST criar apenas raízes, e
  MUST recusar o par que já possui Resultado vigente. A **única** exceção é a consolidação praticada
  em cumprimento de decisão que determinou reavaliação, definida na FR-068.
- **FR-056**: Deferimento com correção fixada MUST criar a decisão e **exatamente um** Resultado
  sucessor na mesma transação; qualquer invariante que falhe MUST derrubar a transação inteira, de
  modo que não exista decisão sem efeito nem efeito sem decisão.
- **FR-057**: O Resultado sucessor por correção fixada MUST declarar origem em recurso e MUST NOT
  citar Avaliação alguma; o sistema MUST NOT sintetizar Avaliação para satisfazer esquema.
- **FR-058**: O Resultado sucessor MUST ser coerente com a decisão que o fundamenta: mesma
  Inscrição, mesmo Edital, mesma Etapa, decisão deferida, consequência declarada pela decisão e
  versão normativa da própria decisão.
- **FR-059**: A conclusão fixada pela decisão MUST obedecer à forma que a Etapa publica — pontuação
  na forma pontuada, sentido na decisória —, e a consequência MUST ser derivada da regra publicada
  vigente para a Etapa, e não digitada livremente. Desfecho **sem grandeza** MUST ser admitido
  somente quando a decisão o declarar, caso em que o sucessor não tem forma, pontuação nem sentido.
- **FR-060**: O instante do sucessor MUST ser posterior ao do superado.
- **FR-061**: Toda leitura de efeito — progressão, participação, prontidão, consolidação,
  classificação, divulgação e Área do Candidato — MUST considerar somente o Resultado vigente do
  par. Ler o superado MUST ser privilégio de duas superfícies e de nenhuma outra: a consulta
  histórica e a reprodução de ato já emitido.
- **FR-062**: A reprodução de ato já emitido MUST continuar lendo os Resultados pela proveniência
  gravada, e MUST NOT ganhar filtro de vigência.
- **FR-063**: Superado e superador MUST ser igualmente imutáveis; nenhuma migration MUST desligar o
  regime append-only para gravar superação.
- **FR-064**: O histórico do par MUST ser consultável, com os dois Resultados em ordem, motivo,
  autor, instante e a decisão que autorizou.

#### Reavaliação determinada

- **FR-065**: Deferimento com reavaliação determinada MUST NOT criar Resultado sucessor.
- **FR-066**: A pendência de reavaliação MUST ser derivada — decisão dessa espécie sem Resultado
  sucessor do par posterior a ela —, e MUST NOT ser coluna de workflow.
- **FR-067**: A organização da Etapa MUST apresentar a inscrição com reavaliação determinada como
  pendência nomeada, e não como já consolidada, e MUST permitir distribuir, avaliar e consolidar.
- **FR-068**: A consolidação praticada **em cumprimento de decisão que determinou reavaliação** MUST
  criar o Resultado **sucessor**, citando obrigatoriamente essa decisão, e MUST ser o único caminho
  pelo qual nasce sucessor com origem em avaliação. É a exceção declarada da FR-055, e ela existe
  **somente** onde existe, para aquele par, decisão dessa espécie ainda não cumprida: fora dela,
  consolidar continua recusando o par que já possui Resultado vigente.
- **FR-069**: A decisão MUST NOT antecipar a correção, e o sistema MUST NOT tratar a determinação
  como se o resultado corrigido já existisse.

#### *Non reformatio in pejus*

- **FR-070**: O recurso do próprio candidato MUST NOT piorar a sua situação: MUST NOT nascer
  sucessor cuja consequência regrida de habilitada para eliminada, nem cuja pontuação seja inferior
  à do superado.
- **FR-071**: A posição classificatória MUST NOT compor a comparação de piora.
- **FR-072**: Concluindo o julgamento por situação pior, o desfecho MUST ser indeferimento, o
  Resultado vigente MUST permanecer e nenhum sucessor MUST nascer.
- **FR-073**: A vedação MUST alcançar o sucessor produzido pela reavaliação determinada em recurso:
  a nova Avaliação MUST poder ser registrada, e o seu Resultado MUST NOT ser consolidado como
  sucessor quando for pior que o superado protegido.
- **FR-074**: A vedação MUST ser regra de comando e de teste, e MUST NOT ser constraint de esquema.

#### Progressão retroativa

- **FR-075**: Superado o Resultado que eliminava a inscrição por outro que a habilita, ela MUST
  voltar ao fluxo das Etapas seguintes pelas regras derivadas existentes.
- **FR-076**: O sistema MUST NOT criar estado de reintegração, sinalizador de progressão nem exceção
  às regras de participação.
- **FR-077**: A Mesa e o painel da Etapa MUST nomear a linha reaberta como reabilitada por recurso
  deferido, com a data.
- **FR-078**: A divergência de obsolescência na tela do marco MUST nomear a causa como participante
  reingressado quando for esse o caso.
- **FR-079**: Enquanto existir inscrição reabilitada por recurso e ainda sem Resultado numa Etapa
  que o marco enumera, a publicação daquele marco MUST ser impedida, com motivo nomeado e caminho
  indicado.
- **FR-080**: A cascata MUST ser de bloqueio: nenhum ato de ordenação e nenhuma publicação MUST ser
  recalculado, alterado ou emitido automaticamente em consequência do deferimento.

#### Definitividade da publicação

- **FR-081**: A natureza pretendida MUST ser insumo da aferição de publicabilidade.
- **FR-082**: A publicação `DEFINITIVA` MUST ser impedida enquanto, para o marco pertinente,
  existir recurso pendente, reavaliação determinada não cumprida, providência a jusante não cumprida
  no sentido da FR-089 ou janela estruturada aberta.
- **FR-083**: A publicação `PRELIMINAR` MUST permanecer possível nos quatro casos da FR-082. Ato de
  ordenação obsoleto e pendência reaberta por progressão retroativa MUST impedir **as duas**
  naturezas: o primeiro divulgaria ordem revogada e o segundo, ordem que já se sabe incompleta, e
  nenhum dos dois deixa de ser falso por ser rotulado como preliminar (D-007, FR-079).
- **FR-084**: A pertinência ao marco MUST alcançar o recurso contra a publicação daquele marco e o
  recurso contra `ResultadoEtapa` de Etapa que o marco enumera, no mesmo Edital e Perfil.
- **FR-085**: Não havendo janela estruturada, a publicação `DEFINITIVA` MUST exigir declaração
  expressa do publicador de que o prazo recursal aplicável se encerrou, com autoria, instante e
  texto, gravada na publicação.
- **FR-086**: A declaração MUST NOT ser oferecida quando a janela for computável, e MUST NOT simular
  prazo calculado.
- **FR-087**: O sistema MUST NOT criar natureza nova para a definitiva que corrige outra definitiva.
- **FR-088**: A publicação definitiva que sucede outra definitiva MUST ser apresentada pela causa,
  em texto derivado da cadeia e das **decisões** que a motivaram, na página e no documento. Citando
  o ato mais de uma decisão (FR-112), todas MUST ser nomeadas, em ordem estável, e a causa MUST ser
  congelada no conteúdo publicado — derivá-la na leitura faria decisão posterior reescrever a frase
  de ato já praticado (FR-091).
- **FR-089**: A providência a jusante MUST ser considerada cumprida, **para um marco**, quando o ato
  de ordenação que se vai publicar citar a decisão que a determinou, **ou** quando já existir,
  naquele marco, ato citante que tenha sido publicado. Publicar como `DEFINITIVA` sem que uma das
  duas condições valha MUST ser impedido.
- **FR-112**: A citação MUST nascer com o `AtoDeOrdenacao`, declarada por quem o emite entre as
  decisões pendentes do marco, e MUST ser conferida como pertinente ao Perfil e ao Marco daquele ato
  — não apenas ao Edital. Um mesmo ato MUST poder citar mais de uma decisão, e uma mesma decisão
  MUST poder ser citada por mais de um ato: enquanto nenhum ato citante for publicado, um sucessor
  MUST poder recitá-la, e uma decisão pertinente a mais de um marco MUST ser citada em cada um. O
  sistema MUST NOT criar ato de cumprimento com autoridade própria, espécie estruturada de
  providência nem ato de impossibilidade de cumprimento (D-009).
- **FR-090**: A publicação vigente MUST dizer que é a vigente, e não apenas a anterior dizer que foi
  sucedida.
- **FR-091**: A 018 MUST NOT alterar retroativamente publicação histórica nem regenerar documento já
  produzido.

#### Proveniência, auditoria e trilha

- **FR-092**: Para qualquer recurso MUST ser possível responder, pela administração e pela
  auditoria: quem interpôs, qual Inscrição, qual objeto foi atacado, qual era o ato vigente naquele
  instante, sob qual versão normativa, quando foi interposto, se estava dentro da janela computável
  quando existia, quem admitiu ou inadmitiu e por quê, quem decidiu e por quê, qual efeito produziu,
  qual ato anterior foi superado e qual ato sucessor nasceu.
- **FR-093**: O candidato MUST NOT precisar ver a trilha técnica; ele MUST ver o objeto atacado, a
  sua fundamentação, a admissibilidade, a decisão e o efeito, em linguagem institucional.
- **FR-094**: Interposição, admissibilidade, decisão e superação MUST gerar auditoria na trilha
  existente, com ator, ação, entidade, identificador, instante, versão normativa, motivo e
  correlação, sem copiar fundamentação, parecer ou pontuação para a trilha.
- **FR-095**: O sistema MUST NOT criar log paralelo nem tabela de eventos própria da feature.

#### Concorrência e idempotência

- **FR-096**: Todo ato desta feature MUST usar o invólucro transacional existente, com autorização
  reavaliada depois do bloqueio e reserva de chave de idempotência.
- **FR-097**: Repetir a mesma chave MUST devolver o desfecho original, sem criar linha nem evento.
- **FR-098**: Mesma chave com conteúdo diferente MUST produzir conflito.
- **FR-099**: A corrida entre dois sucessores do mesmo Resultado MUST ser resolvida por constraint
  no banco, e não por leitura prévia.
- **FR-100**: A confirmação de qualquer ato MUST carregar a identificação do estado que foi lido, e
  divergência MUST recusar por estado obsoleto sem gravar nada.
- **FR-101**: O sistema MUST NOT introduzir mecanismo novo de concorrência onde revisão otimista,
  idempotência, append-only e recusa por estado obsoleto já resolvem.

#### Proteção de dados

- **FR-102**: A fundamentação do recurso e a motivação da decisão MUST ser acessíveis ao titular, à
  autoridade julgadora e à auditoria autorizada, e a mais ninguém.
- **FR-103**: Nenhum dado de outro candidato MUST atravessar as superfícies do recurso, nem na
  interposição, nem no acompanhamento, nem na decisão.
- **FR-104**: Identificador de Inscrição, de Resultado, de publicação ou de recurso MUST NOT
  conceder acesso; escopo ou vínculo divergente MUST receber a resposta uniforme de recurso não
  encontrado.
- **FR-105**: Respostas com Resultado individual, fundamentação ou decisão MUST NOT ser armazenáveis
  pelo navegador e MUST NOT ampliar o acesso a documentos do candidato.

#### Jornada, limites e não regressão

- **FR-106**: A jornada MUST ser executável de ponta a ponta pelo canal do ator — o portal para o
  candidato, a interface administrativa para a comissão e a autoridade —, sem banco, shell ou
  chamada manual.
- **FR-107**: A 018 MUST NOT alterar conteúdo, autoria ou estado de Avaliação, Atribuição,
  Impedimento, `AtoDeOrdenacao`, `PosicaoNaOrdem` ou `PublicacaoResultado` existentes.
- **FR-108**: A 018 MUST NOT recalcular nem emitir classificação automaticamente.
- **FR-109**: A 018 MUST NOT disparar notificação de espécie alguma.
- **FR-110**: Nenhum comportamento existente de consolidação, ocorrência, classificação, publicação
  ou Área do Candidato MUST mudar por causa desta feature, salvo os acréscimos que os requisitos
  acima declaram; a demonstração é por identidade de teste, com as asserções alteradas enumeradas
  uma a uma na entrega.
- **FR-111**: A recusa de reabertura de Avaliação que fundamenta Resultado MUST permanecer, e a sua
  mensagem MUST deixar de prometer uma anulação que não existe, passando a nomear o ato que existe.

### Key Entities

- **Recurso** — a peça interposta pelo titular contra um objeto vigente. Registra protocolo, quem
  interpôs, a Inscrição, o objeto atacado e a identidade do ato que era vigente naquele instante, a
  versão normativa então vigente, o instante, a fundamentação e se havia janela computável e se ela
  estava aberta. Append-only.
- **Juízo de Admissibilidade** — o ato que admite ou inadmite a peça, com autor, instante e motivo.
  Append-only.
- **Decisão de Recurso** — o ato que julga o mérito, com a espécie, a motivação, o autor, o
  instante e a versão normativa. Quando fixa a correção, declara a consequência e, quando aplicável,
  a conclusão corrigida; quando determina reavaliação ou providência, declara o que determinou.
  Append-only, e fonte jurídica citada pelo Resultado sucessor.
- **Superação de Resultado** — não é entidade: é a cadeia do próprio `ResultadoEtapa`, em que o
  sucessor cita o superado, o motivo da superação e a decisão que a autorizou. Vigente é quem
  ninguém sucedeu.
- **Janela Recursal** — derivada do conteúdo normativo do marco e do instante da publicação vigente
  que a ancora. Não é linha, não é estado e não é coluna.
- **Declaração de Encerramento do Prazo** — o fato declarado pelo publicador, com autoria, instante
  e texto, gravado na publicação, quando o Edital não declara janela estruturada.

---

## 5. Invariantes observáveis

- **IR-001** — Para cada par Inscrição × Etapa existe no máximo um Resultado vigente, e vigente é o
  que ninguém sucedeu. A garantia é do banco.
- **IR-002** — Nenhum registro histórico é alterado, anulado ou excluído: superado e superador são
  igualmente imutáveis.
- **IR-003** — Nenhum Resultado sucessor nasce senão da execução de uma decisão de recurso deferido,
  e todo sucessor cita a decisão que o autorizou. São dois caminhos, e só dois: o próprio ato de
  deferimento que fixa a correção, e a consolidação praticada em cumprimento de decisão que
  determinou reavaliação. Consolidação ordinária e ocorrência criam apenas raízes.
- **IR-004** — Deferir e superar são o mesmo ato quando a decisão já declara o resultado corrigido:
  não existe decisão sem efeito, nem efeito sem decisão.
- **IR-005** — Nenhum recurso é julgado por quem produziu o ato atacado ou está impedido para
  aquela Inscrição.
- **IR-006** — Nenhum recurso do próprio candidato produz situação pior que a vigente, por caminho
  algum — nem pela correção fixada, nem pela reavaliação ordenada.
- **IR-007** — A superação obsoleta a jusante e não corrige a jusante: a cascata é de bloqueio, e a
  correção é sempre ato humano autorizado.
- **IR-008** — A mesma proveniência reproduz a mesma ordem: ato emitido antes do deferimento
  continua reproduzindo a ordem que constituiu.
- **IR-009** — Nenhum prazo é inventado: onde a norma não declarou janela, o sistema não calcula,
  não exibe e não aplica prazo nenhum.
- **IR-010** — Nenhuma publicação afirma definitividade sem que os fatos que a sustentam estejam
  verificados ou expressamente declarados sob responsabilidade nominal.
- **IR-011** — Toda recusa e toda inadmissão são atos motivados e consultáveis por quem sofreu o
  efeito.
- **IR-012** — Pendência é derivada dos atos que existem, e não estado persistido.

---

## 6. Out of Scope

**Legitimidade ampliada** — terceiro interessado, procurador, representação, login delegado,
contraditório de terceiro e impugnação por concorrente. Cada um exige capacidade que o produto não
tem (D-002).

**Comunicação ativa** — e-mail, SMS, push. Ninguém é notificado da decisão; ela é consultável.

**Comissão recursal própria** — a autoridade é capacidade do mapa, e não órgão novo (D-005).

**Revisão de ofício** — é ato próprio, com motivação própria, e não deve ser simulada como recurso.

**Segunda instância, pedido de reconsideração e efeito suspensivo** (D-011).

**Anexos à peça recursal** (D-011).

**Documento imprimível do recurso e da decisão** — o registro é consultável no canal do titular,
com protocolo e instante; produzir a forma documental é acréscimo que nenhum requisito desta
feature exige.

**Recurso contra Edital, Retificação, convocação, heteroidentificação ou qualquer ato que ainda não
exista no produto.**

**Ocupação de vagas, convocação, aceite, posse e matrícula** — são da 019.

**Publicação coletiva de `ResultadoEtapa` e qualquer abstração genérica de publicável** — a 017 as
excluiu por decisão, e a D-003 desta spec não as reabre.

**Homologação de julgamento por autoridade distinta** — nenhum Edital lido a impõe; se surgir,
nasce com contrato próprio.

**Calendário de dias sem expediente e contagem em dias úteis** (D-004).

**Registro de cumprimento de providência, espécie estruturada de providência e ato de
impossibilidade de cumprimento** — o cumprimento é fato derivado, e declará-lo por ato acrescentaria
vocabulário, entidade, autoridade e tela para verificar o que uma comparação já responde (D-009).

**Publicação preliminar sucedendo uma definitiva** — a ordem entre naturezas tem sentido único na
017, e o caso que a exigiria não é alcançável (D-008).

**Alteração destrutiva de ato histórico**, em qualquer forma.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** — Publicado o marco, 100% dos candidatos do Perfil consultam o próprio Resultado
  vigente de cada Etapa que o marco enumera, inclusive os que foram eliminados antes do marco e
  estão fora do universo do ato.
- **SC-002** — Um candidato interpõe recurso, do início ao fim, pelo portal, e obtém protocolo,
  instante e o objeto atacado nomeado.
- **SC-003** — Reenviar a mesma interposição produz um único recurso e zero eventos adicionais.
- **SC-004** — Duas interposições equivalentes do mesmo titular produzem uma peça; a segunda é
  recusada nomeando o protocolo da primeira.
- **SC-005** — 100% das tentativas de admitir ou julgar praticadas por quem avaliou, consolidou,
  constatou, emitiu ou publicou o ato atacado são recusadas, e 100% das praticadas por quem tem
  `Impedimento` na Inscrição também.
- **SC-006** — Um ator sem a capacidade de julgar não alcança recurso algum, inclusive sendo
  presidente da comissão.
- **SC-007** — Deferido com correção fixada, existe exatamente um Resultado sucessor, o anterior
  permanece consultável e inalterado, e a decisão e o sucessor nasceram na mesma transação.
- **SC-008** — Nenhum caminho produz Resultado sucessor pior que o superado: nem o deferimento com
  correção, nem a consolidação da reavaliação determinada.
- **SC-009** — Deferido com reavaliação determinada, zero Resultados sucessores existem até que a
  nova Avaliação seja consolidada, e a Etapa apresenta a pendência nomeada.
- **SC-010** — Superado um Resultado, o ato de ordenação que o citava aparece obsoleto, a publicação
  daquele ato é recusada com o caminho nomeado, e nenhum ato ou publicação é alterado ou emitido
  automaticamente.
- **SC-011** — Um ato de ordenação emitido antes do deferimento reproduz, a partir da sua
  proveniência, exatamente a ordem que constituiu.
- **SC-012** — Reabilitada por recurso, a inscrição aparece como pendente e nomeada em 100% das
  Etapas seguintes que ainda não têm Resultado dela, e é distribuível, avaliável e consolidável.
- **SC-013** — Enquanto houver pendência reaberta que afete o marco, 100% das tentativas de publicar
  aquele marco são recusadas com a causa nomeada.
- **SC-014** — Com janela declarada, o candidato vê a abertura e o encerramento exatos, interpõe
  dentro do prazo e é recusado depois dele, com a norma citada.
- **SC-015** — Sem janela declarada, zero prazos são exibidos ou aplicados, e a tempestividade
  aparece como juízo motivado no ato de admissibilidade.
- **SC-016** — Editais publicados antes do incremento continuam legíveis, retificáveis e publicáveis
  sem nenhuma recusa causada pela ausência da declaração de janela.
- **SC-017** — 100% das tentativas de publicar como definitivo com recurso pendente, reavaliação
  pendente, providência pendente ou janela aberta são recusadas, e a publicação preliminar permanece
  possível nesses quatro. Com ato obsoleto ou pendência reaberta, 100% das tentativas são recusadas
  **nas duas naturezas**. Publicado um ato que **cita** a decisão, a pendência da providência deixa
  de existir sem que ninguém pratique ato de cumprimento; publicado um ato que não a cita, ela
  permanece.
- **SC-018** — Sem janela estruturada, nenhuma publicação definitiva existe sem declaração expressa
  de encerramento do prazo, com autor, instante e texto consultáveis.
- **SC-019** — A publicação definitiva que corrige outra definitiva é apresentada pela causa, na
  página e no documento, sem natureza nova no vocabulário.
- **SC-020** — Para qualquer recurso, a administração reconstrói em uma única jornada a lista
  completa da FR-092, sem banco e sem shell.
- **SC-021** — Nenhum identificador técnico e nenhum enum canônico aparece como texto institucional
  nas superfícies do candidato.
- **SC-022** — Nenhum dado de outro candidato é alcançável por qualquer superfície desta feature, e
  a manipulação de identificador devolve a mesma resposta uniforme.
- **SC-023** — Nenhuma tentativa de alterar Resultado, decisão ou admissibilidade tem efeito: 100%
  são recusadas nas três camadas.
- **SC-024** — A jornada demonstrável é executada pelos canais dos atores: o candidato vê o próprio
  Resultado, recorre e lê a decisão pelo portal; a autoridade admite e julga pela interface
  administrativa; a presidência vê a reabilitação na Etapa; o publicador é impedido e depois
  autorizado a publicar como definitivo.

---

## Assumptions

- A capacidade de julgamento de recurso será acrescentada ao mapa de papéis existente; a qual papel
  ela pertence é configuração institucional, e não mudança de contrato. Em comissão pequena, o
  impedimento pode não deixar ninguém elegível, e a saída é conceder a capacidade a quem está fora
  da comissão — como `resultado:publicar` já resolveu o mesmo aperto.
- A janela recursal é a única evolução de conteúdo publicado desta feature. É o item a dimensionar
  primeiro, e o único que, se a 018 precisar ser fatiada, pode ser adiado sem desmontar as demais:
  sem ele, a tempestividade continua sendo juízo de admissibilidade, que é a degradação que a
  própria D-004 declara.
- A reavaliação determinada é executada por avaliador diferente do que concluiu a Avaliação
  original. Isso já é consequência estrutural — a mesma pessoa não conclui duas vezes o mesmo par —
  e não precisa de regra nova; a spec apenas registra que é o comportamento correto.
- Recurso cujo mérito é a nota ataca a publicação e produz efeito no `ResultadoEtapa`: objeto
  atacado e lugar do erro são eixos distintos, e o mapa dos remédios é o da §4 da descoberta.
- A zona temporal institucional é a mesma que a elaboração e a Retificação já usam; a 018 não
  introduz zona nova.
- O produto não notifica ninguém. O candidato descobre a decisão consultando a sua Inscrição, e é
  por isso que a decisão precisa ser legível ali.

---

## 7. Ordem de implementação sugerida

| Slice | Entrega observável |
|---|---|
| **S0** | Superação de `ResultadoEtapa`: cadeia append-only, unicidade de raiz e de sucessor, origem por recurso, coerência com a decisão, e o filtro de vigência em toda leitura de efeito |
| **S1** | O candidato vê o próprio Resultado da Etapa quando o marco do seu Perfil foi divulgado |
| **S2** | Interposição, protocolo, acompanhamento e a recusa por objeto superado |
| **S3** | Capacidade de julgar, impedimento que bloqueia, admissibilidade motivada |
| **S4** | Decisão nas quatro espécies, com deferimento por correção fixada superando na mesma transação, sob *non reformatio* |
| **S5** | Reavaliação determinada: pendência nomeada, consolidação que produz o sucessor, vedação de piora |
| **S6** | Progressão retroativa visível e guarda de publicação por pendência reaberta |
| **S7** | Definitividade: fatos verificados, declaração expressa, e a definitiva retificada nomeada pela causa |
| **S8** | Janela recursal como conteúdo publicado: degrau de elevação, elaboração, documento, Retificação, exibição e aplicação |

O **S0** é o único slice sem capacidade observável própria, e existe para desbloquear tudo o mais:
sem a cadeia de sucessão e sem o filtro de vigência, deferir não teria onde produzir efeito, e o
efeito produzido seria lido errado. O seu teste de regressão mais importante é o dicionário de
pontuações do cálculo classificatório: sem filtro de vigência e sem ordenação determinística, dois
Resultados do mesmo par colapsam em silêncio e produzem ordem errada sem erro.

O **S8** vem por último de propósito. É o mais caro, é o único que toca conteúdo publicado, e o
produto funciona sem ele pela degradação que D-004 declara — a tempestividade como juízo de
admissibilidade motivado. Antecipá-lo atrasaria o ciclo que a feature existe para fechar.

## 8. Gate de conclusão

```text
resultado divulgado
  → o candidato vê o próprio Resultado da Etapa
  → interpõe recurso e recebe protocolo
  → a autoridade elegível admite e julga com motivo
  → o deferimento supera o Resultado, sem alterar nada
  → o ato classificatório fica obsoleto e a publicação é bloqueada
  → alguém autorizado emite o sucessor e publica a sucessora
  → o candidato lê a decisão e vê o efeito
  → o histórico anterior continua íntegro, consultável e reproduzível
```

Ao final da 018 o produto responde, pela primeira vez e de ponta a ponta: **o candidato contestou
uma decisão que lhe afetava, a instituição a julgou com autoridade e imparcialidade, a correção
produziu efeito legítimo — e nada do que aconteceu antes foi apagado ou reescrito.**
