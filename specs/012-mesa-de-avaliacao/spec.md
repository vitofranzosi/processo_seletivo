# Feature Specification: Mesa de Avaliação

**Feature Branch**: `012-mesa-de-avaliacao`

**Created**: 2026-09-01

**Status**: Draft

**Input**: Redação conceitual da feature, reconciliada com o que a 011 e a 009 efetivamente
entregaram no repositório em `ae86b6e`, e revista em duas rodadas de avaliação. A reconciliação
produziu as **Decisões fechadas antes do planejamento** da seção 5, que corrigem quatro pontos
escritos contra um sistema que o repositório não tem: a pontuação máxima não existe no conteúdo
publicado; a permissão sob a qual a 009 abre documento de candidato não é a que esta feature pode
usar; o mecanismo de versão canônica recusa retificar conteúdo de versão anterior, e esta spec
recusa aceitar isso como consequência; e "atribuição" já significa outra coisa na 011.

A segunda rodada fechou as consequências semânticas que a primeira deixou abertas: o que a
quantidade declarada é normativamente, o que acontece com a Avaliação quando a Atribuição é
inativada, e o que impede que inativar Atribuição vire um modo de escolher quais avaliações contam
no resultado.

---

## 1. Visão

Permitir que a presidência **distribua as inscrições** entre os membros já alocados à Etapa, e que
cada avaliador **execute, dentro do sistema, somente as avaliações que lhe foram atribuídas** —
abrindo a documentação como instrumento de trabalho, registrando o que afirma sobre a inscrição na
forma que a Etapa publicou, e concluindo.

A feature responde à pergunta:

> **O avaliador consegue executar o trabalho dentro do sistema?**

A 012 executa o trabalho.

Ela **não produz resultado**.

---

## 2. Frase que governa

> **Quem foi alocado a uma Etapa deve receber suas inscrições, abrir o que o candidato enviou,
> registrar a avaliação e concluí-la — sem planilha paralela, sem pasta compartilhada e sem que
> ninguém precise saber quem avalia quem por combinação informal.**

Para quem preside:

> **A distribuição das inscrições é ato administrativo com autoria, e não efeito colateral de um
> algoritmo.**

---

## 3. O que a 011 entregou, e que a 012 herda como contrato

A 011 fechou com o gate que autoriza esta spec. A 012 **assume** e não reabre:

**PC-001** — **A 011 determina quem pode trabalhar em cada Etapa. A 012 determina quais inscrições
cada uma dessas pessoas deverá avaliar.** Estar alocado à Etapa não concede acesso algum aos
candidatos daquela Etapa. Se o ator chegou à Mesa de uma Etapa, sua autorização para **atuar
naquela Etapa** já foi resolvida pela 011; a 012 acrescenta a segunda pergunta, e só ela: *esta
inscrição foi atribuída a esta pessoa?*

**PC-002** — Os dois guards existem, e a 012 **compõe** com eles em vez de reescrevê-los:
`pode_atuar_na_etapa(ator, edital, etapa_id)` responde por uma Etapa e custa duas a três consultas;
`etapas_autorizadas(ator, edital)` responde a mesma regra para o conjunto, numa leitura só, e
existe justamente porque a 012 desenharia listas. Conjunto vazio significa "nenhuma", e nunca
"todas".

**PC-003** — A Etapa pertence ao **Edital**, e a comissão pertence ao **Processo** (011, D-001). A
Atribuição herda os dois caminhos e não cria um terceiro.

**PC-004** — A alocação designa a Etapa pela identidade que o **conteúdo publicado** carrega, e não
pela linha de elaboração (011, D-002). Alocação sobre Etapa ausente da Versão Consolidada vigente
não concede acesso, e a Atribuição sob ela também não.

**PC-005** — O isolamento por escopo institucional vale integralmente (011, D-004): escopo
divergente responde como recurso inexistente.

**PC-006** — A trilha de auditoria existente é a única, com a base de autorização registrada. Não
há subsistema paralelo de logs de negócio.

**PC-007** — O que a **009** entregou e a 012 consome sem recriar: entrega mediada de arquivo,
verificação de integridade **antes de sair um byte** com a cópia conferida sendo a servida,
registro de cada consulta a documento, registro da divergência de integridade como recusa, resposta
marcada como não armazenável pelo navegador, ausência de download em lote e um arquivo por
requisito, ligado ao Documento Exigido que ele atende. Boa parte da mecânica desta feature já
existe; o que não existe é a **porta** por onde o avaliador entra nela (D-005).

**PC-008** — O gate de identidade institucional confiável, herdado da 011, continua explícito. Esta
é a feature em que ele deixa de ser teórico (FR-058).

---

## 4. A cadeia, em uma figura

```text
SPEC 011
Comissão do Processo
   ↓
Membro da comissão
   ↓
Alocação na Etapa
   │
   │  "pode trabalhar aqui"
   ↓
SPEC 012
Atribuição de inscrições
   │
   │  "deve avaliar estes candidatos"
   ↓
Mesa do avaliador
   ↓
Avaliação
   ↓
SPEC 013
Consolidação / Resultado
```

A linguagem canônica, e nenhuma outra:

> **011 — aloca membro da comissão à Etapa.**
> **012 — atribui inscrições ao avaliador.**

---

## 5. Decisões fechadas antes do planejamento

*A redação conceitual desta spec foi escrita olhando a jornada. Verificada contra o repositório,
três de seus requisitos pediam algo que o sistema não tem, e um quarto reutilizaria uma porta que
não pode ser reutilizada. As decisões abaixo fecham isso em termos de resultado; o corpo da spec já
está escrito conforme elas.*

### D-001 — O incremento canônico é um, e ele carrega **duas** propriedades

> **Decisão histórica, e verdadeira no contexto em que foi tomada.** Ela descreve o primeiro
> incremento, de 4 para 5. Uma mudança de requisito posterior — a conclusão que não pressupõe nota —
> exigiu um segundo, de 5 para 6, e está em D-008. As duas convivem: o que a D-001 fixou sobre o
> primeiro incremento não é reescrito, e a história dele não é reencenada como se os cinco campos
> tivessem nascido juntos.

A redação original declarava um único incremento — quantas avaliações por inscrição — e, oito
seções adiante, exigia validar a pontuação contra "o limite que o Edital publicou". **Esse limite
não existe.** A Etapa publicada carrega hoje `id`, `name`, `order`, `weight`, `eliminatory`,
`classificatory`, `minimumScore` e `scheduleEventId`. Há nota mínima; não há nota máxima, nem no
conteúdo publicado, nem no modelo de elaboração, nem no documento materializado.

Por P-007, regra não publicada não se aplica. Restavam duas saídas: abandonar o limite, ou
publicá-lo. Abandoná-lo faria a pontuação ser validada apenas pela faixa que a persistência tolera
— um teto acidental de `decimal(7,4)`, que não é regra normativa de coisa nenhuma e que nenhum
candidato pode ler no Edital.

Publicá-lo é o caminho, e o mecanismo obriga que as duas propriedades viajem juntas. A versão
canônica do snapshot existe para identificar **uma forma**, e o próprio código registra a razão nos
incrementos anteriores: subir a versão com uma propriedade e acrescentar a outra depois produziria
snapshots da mesma versão com e sem a segunda, e a versão deixaria de identificar uma forma.

**A decisão**: o incremento é um só e acontece uma vez, subindo a versão canônica de 4 para 5, e
ele acrescenta à Etapa publicada **duas** propriedades — quantas avaliações a inscrição recebe e a
pontuação máxima. As duas são normativas pela mesma razão: afetam direito do candidato e precisam
ser legíveis no Edital.

### D-002 — O incremento não torna irretificável o que já foi publicado

O sistema recusa consolidar Retificação sobre conteúdo cuja versão canônica não é a vigente, e a
recusa é uma comparação entre o `schemaVersion` do próprio conteúdo e a constante global. A 007 e a
009 subiram a versão e aceitaram essa consequência, cada uma registrando a mesma precondição de
implantação — a feature precede o primeiro Edital de produção, e os dados de demonstração são
recriados.

**A 012 não repete essa precondição, porque a razão que a sustentava não se transfere.** O
comentário que justifica a recusa diz que a alternativa seria uma máquina que "construiria
compatibilidade para conteúdo que não existe", e isso era verdade dos incrementos anteriores: eles
acrescentaram seções ao catálogo e coleções inteiras ao conteúdo, e qualquer valor que uma
conversão inventasse para elas seria afirmação normativa que ninguém publicou — dizer que um Edital
não exige documento algum é dizer alguma coisa.

O incremento desta feature é diferente em espécie. Ele é **aditivo, e a spec já declara o que a
ausência significa**: sem a declaração, uma avaliação por inscrição (FR-009); sem o limite, limite
não declarado (FR-066). Elevar conteúdo da versão anterior não inventa nada — escreve na forma nova
exatamente o que o conteúdo já dizia por omissão.

**A decisão**: tornar irretificável, por evolução de esquema, um Edital que a instituição publicou
seria consequência de produto, e não detalhe de implantação. A Retificação deve continuar podendo
interpretar conteúdo-base da versão anterior, elevá-lo pela leitura declarada acima e produzir
Versão Consolidada na versão vigente — **sem tocar na Publicação original**, que permanece imutável
como a Constituição exige, e **sem que a elevação apareça como ato normativo de alguém**, porque ela
não é retificação: é a mesma norma escrita na forma nova, sem autoria e sem proveniência de ato.

Se o `/plan` concluir que isso não é alcançável sem violar imutabilidade, proveniência ou hash, a
decisão volta a esta spec em vez de ser aceita em silêncio.

### D-003 — "Atribuição" passa a ser entidade, e o nome fica reservado

A 011 usa "atribuição" no sentido corrente da língua — *a atribuição pela qual o ator chegou à
página*, alocação ou gestão — e batizou assim uma rota sua, que mostra a **Etapa**. A 012 promove a
palavra a entidade do domínio: *esta pessoa avalia esta inscrição*. Duas coisas com um nome só, na
mesma aplicação, é exatamente o que o princípio de linguagem ubíqua da Constituição proíbe.

**A decisão**: `Atribuição` designa, daqui em diante e sem exceção, o vínculo avaliador→inscrição.
Onde a 011 usa a palavra no sentido corrente, ela passa a precisar de outra — inclusive no
identificador interno que hoje a carrega. **Qual nome, e onde, é decisão do `/plan`**: a spec reserva
o significado do termo e não prescreve nome interno. O que ela fixa é que nada dessa correção altera
domínio, dado, autorização ou comportamento da 011.

Pela mesma razão, a entidade nova chama-se `Avaliacao` — o **ato** —, e `EtapaAvaliacao` continua
sendo a **fase**. As duas convivem porque significam coisas diferentes e o dizem.

### D-004 — A Atribuição espelha a alocação, e a revogação é computada

A Atribuição poderia apontar para a linha de alocação. Não aponta, e a razão é a mesma que a 011
registrou para não usar chave estrangeira na Etapa: **remover é inativar, e readicionar cria linha
nova**. Uma Atribuição pendurada na linha de alocação morreria a cada remoção, e a presidência que
retirasse uma pessoa da Etapa por engano não teria como desfazer o engano — as mil atribuições
dela ficariam órfãs para sempre.

**A decisão**: a Atribuição é `membro + edital + etapa_id + inscrição`, exatamente a forma da
alocação mais a inscrição, com `etapa_id` sendo a identidade da Etapa no conteúdo publicado, pela
razão que a 011 já escreveu.

E disso decorre o ponto que decide a escala: **a revogação por perda de alocação é computada, nunca
desnormalizada**. Ninguém marca duas mil linhas quando uma pessoa sai da Etapa. O acesso é a
conjunção verificada no servidor — guard da 011 **e** Atribuição ativa —, de modo que retirar a
alocação revoga tudo aquilo em um único ato, e devolvê-la restaura, que é o que torna o engano
reparável.

### D-005 — A porta do avaliador é nova; a mecânica do arquivo é a que já existe

A 009 já abre documento de candidato com tudo o que a 012 pediria: conferência de integridade antes
do primeiro byte, a cópia conferida sendo a servida, registro da consulta e registro da
divergência. Mas ela abre sob a permissão `inscricao:consultar`, que pertence ao Gestor e vale
para **o Edital inteiro** — sem atribuição, sem alocação, sem Etapa.

Reutilizar essa permissão para o avaliador entregaria a ele o acervo completo do Edital e
contradiria FR-055 na primeira linha de código.

**A decisão**: a 012 reutiliza a **mecânica** — entrega mediada, verificação, trilha, resposta não
armazenável — e não reutiliza a **permissão**. A rota do avaliador é própria e sua autorização é a
composta da seção 16. A porta administrativa da 009 permanece exatamente como está.

### D-006 — Não existe retirada de inscrição, e a 012 não a inventa

A inscrição tem dois estados — rascunho e submetida — e a submetida é imutável **no agregado**: a
própria 009 registra que isso não é garantia de banco, porque a inscrição muda legitimamente
enquanto é rascunho e imutabilidade condicional ao estado não cabe em privilégio de tabela. Não há
desistência, cancelamento nem retirada em lugar nenhum do sistema.

**A decisão**: o caso da inscrição retirada depois de distribuída (EC-006) não é alcançável hoje, e
a 012 não cria o estado que o tornaria alcançável — seria inventar ato do candidato dentro de uma
feature de avaliador. Quando alguma feature criar a retirada, é ela que responderá pelo efeito
sobre atribuições e avaliações já registradas, e este edge case é o registro de que a pergunta está
esperando por ela.

### D-007 — A quantidade declarada é teto que a 012 aplica e piso que a 013 cobra

A primeira redação chamou o número de "meta", e isso o contradizia duas seções antes: uma
quantidade que afeta direito do candidato não pode ser um número que o sistema exibe e ignora. Mas
tratá-lo como quantidade obrigatória em toda a extensão faria a 012 bloquear a conclusão enquanto
faltasse avaliador — que é decidir o que fazer com a insuficiência, e isso é resultado.

O número tem dois lados, e eles não pertencem à mesma feature:

- **O excedente é recusado, e a recusa é da 012.** Isso pressupõe uma classificação que a 011
  adiou explicitamente ao recusar `avaliadores_exigidos` até saber se aquilo era norma, operação ou
  resultado, e que a 012 agora faz: **o número é a cardinalidade normativamente prevista de
  avaliações válidas por inscrição, e não um mínimo nem uma meta de distribuição**. Sendo exato,
  admitir a terceira seria produzir avaliação fora do que o Edital previu. Recusar é barato,
  acontece na distribuição e é integralmente verificável aqui.
- **O déficit é visível, e a consequência é da 013.** Distribuição parcial é estado legítimo
  (FR-015), e o que fazer quando a quantidade não é atingida até o prazo — esperar, decidir com o
  que há, convocar outro — é decisão sobre resultado.

Disso decorre que a 012 não cria estado "aguardando segundo avaliador", não bloqueia conclusão por
insuficiência e não impede concluir quando só há uma avaliação distribuída. Ela impede a terceira,
conta a que falta, e para por aí.

E o teto conta **o que é elegível**, não o que já aconteceu. Avaliação tornada inelegível — por
impedimento superveniente, por exemplo — deixa de ocupar uma das vagas previstas, senão o registro
histórico de uma pessoa impediria para sempre que outra a substituísse. Preservar o passado não pode
significar bloquear o presente.

### D-008 — Concluir deixa de significar pontuar, e a Etapa publica qual das duas formas exige

*Mudança de requisito, tomada em 03/09/2026 a partir da análise de três Editais reais do Cefor/Ifes
— 35/2026 e 57/2026 (sorteio e análise documental) e 14/2026 (títulos e entrevista), registrada em
`doc/decisao-012-conclusao-decisoria.md`. Não reabre nada que o §21 recusou: conclusão não-numérica
não aparece ali, e a 012 nunca decidiu que concluir exige nota — ela só nunca teve pela frente uma
Etapa que não pontuasse.*

Nos Editais 35 e 57 a Etapa central não pontua. Depois do sorteio, a comissão faz a análise
documental dos candidatos sorteados, e o que ela produz é **deferido** ou **indeferido** — nunca uma
nota. Fingir que produz — deferido igual a 1, indeferido igual a 0 — inventaria uma grandeza que o
Edital não publicou, e a 013 teria de descobrir, por convenção não escrita, que aquele `0` elimina.
É o mesmo erro de categoria que esta spec já recusa em outro lugar: heteroidentificação não é
"avaliação com nota zero".

**A decisão**: uma Avaliação concluída precisa possuir a **conclusão completa segundo a forma que a
Etapa publicou**. "Completa" deixa de significar *tem nota* e passa a significar *tem o que a forma
exige*. O invariante forte não é relaxado — o que muda é o que ele afirma.

```text
Avaliacao concluída
├── forma:     PONTUADA | DECISORIA      ← publicada pela Etapa, gravada na linha
├── pontuação                            ← exigida quando PONTUADA, ausente quando DECISORIA
├── sentido:   FAVORAVEL | DESFAVORAVEL  ← exigida quando DECISORIA, ausente quando PONTUADA
└── parecer
```

**1 · A Etapa publica a forma.** `forma = PONTUADA | DECISORIA` é conteúdo normativo, pelo mesmo
argumento de P-007 que obrigou a pontuação máxima a ser publicada (D-001): regra que decide se o
trabalho do avaliador produz nota ou deferimento afeta direito do candidato, e não pode ser
configuração de tela.

**2 · A forma decisória publica os rótulos.** O domínio guarda sempre `FAVORAVEL | DESFAVORAVEL`; o
rótulo que o avaliador lê e o documento imprime é dado publicado — `rotuloFavoravel` e
`rotuloDesfavoravel` —, pelo mesmo padrão de `ModalidadeConcorrencia`, onde código e denominação são
dados e não enumeração. Deferido/Indeferido, Apto/Inapto, Elegível/Não elegível e
Classificado/Desclassificado são o mesmo juízo com o vocabulário que cada Edital escolheu; um enum
com os quatro pares teria oito valores para dois significados e cresceria a cada Edital novo, que é
hard-code de regra sujeita a legislação. **Sem objeto genérico e sem default institucional**: a tela
de elaboração pode sugerir um par inicial editável, e prefill de tela não é default normativo.

**3 · Conteúdo anterior é lido como `PONTUADA`.** Edital em versão canônica igual ou anterior a 5
não carrega a forma, e a ausência significa a forma pontuada — não por conveniência, mas porque o
domínio anterior não admitia outra. A ausência dos rótulos, ali, é correta: não há sentido a nomear.
A leitura vale nos **dois** lugares em que o projeto a exerce, e a spec nomeia os dois: o **consumo**,
onde a ausência já é interpretada num lugar só; e a **elevação no caminho de Retificação**, que hoje
é declaradamente a conversão de um incremento, e só dele. **O `/plan` decide a forma** — cadeia
4 → 5 → 6, ou origem que passa a ser um conjunto —, mas não pode decidir que ela não acontece: a
D-002 continua valendo por inteiro, e tornar irretificável por evolução de esquema um Edital já
publicado seria consequência de produto.

**4 · São dois incrementos canônicos, e a história do primeiro não é reescrita.**

```text
012 original      v4 → v5    + evaluationsPerRegistration, + maximumScore
revisão da 012    v5 → v6    + forma, + rotuloFavoravel, + rotuloDesfavoravel
```

Dentro de cada incremento as propriedades entram juntas, pela razão que o próprio `SCHEMA_VERSION`
registra: subir a versão com uma e acrescentar a outra depois produziria snapshots da mesma versão
com e sem a segunda, e a versão deixaria de identificar uma forma. Entre incrementos não há essa
exigência — o segundo nasce de mudança de requisito posterior, e não de descuido do primeiro.

**5 · A conclusão copia a forma da versão contra a qual foi validada.** A forma aparece em dois
lugares com funções diferentes, e eles não são fontes concorrentes:

```text
Etapa publicada     → "a regra vigente determina a forma X"
Avaliação concluída → "esta avaliação foi concluída sob a forma X"
```

Na transação que conclui, a forma é lida **do conteúdo da versão consolidada** — a mesma leitura
única que FR-096 já exige para a Etapa —, a conclusão é validada contra ela e aquela mesma forma é
gravada. São duas razões, e a segunda é a que importa mais. Uma verificação do banco não referencia
outra tabela: com a forma na linha, a regra volta a ser local e continua sendo do banco. E a
conclusão é histórica: se uma Retificação mudar a natureza da Etapa depois, a conclusão antiga
precisa continuar interpretável sob a regra que a governou — que é exatamente por que ela já guarda
a versão (FR-071). Gravar a forma não é duplicação; é a mesma preservação de sentido, no padrão que
esta spec estabeleceu.

**6 e 7 · Cada forma exige o que é seu, e recusa o que é da outra.** `PONTUADA` exige pontuação e
não admite sentido; `DECISORIA` exige sentido e não admite pontuação. As duas juntas substituem o
que define "concluída" no banco, que continua sendo verificação do banco e não promessa da tela.

**8 · `DESFAVORAVEL` exige parecer.** Na forma pontuada a regra atual permanece intacta — nota
abaixo do mínimo em Etapa eliminatória (FR-034). Na forma decisória a obrigatoriedade **não** depende
do caráter da Etapa, e a assimetria é deliberada: o desfavorável é justamente o caso em que o
candidato mais precisará da fundamentação para recorrer, e é contra o parecer que o recurso
responderá. Exigir parecer também no favorável é configuração futura, e não se generaliza aqui.

**9 · Aplicabilidade dos campos normativos de pontuação, por forma.**

```text
PONTUADA    maximumScore aplicável · minimumScore aplicável conforme a Etapa
            sentido ausente · rótulos ausentes
DECISORIA   maximumScore ausente  · minimumScore ausente
            sentido aplicável · rótulos obrigatórios
```

**O peso fica fora dessa condicionalidade.** Ele descreve a composição entre Etapas — feature
posterior — e não a forma da conclusão local; condicioná-lo à forma o acoplaria a uma distinção que
não é a dele. O caráter eliminatório e o classificatório também permanecem propriedades da Etapa, e
não da forma, mas com uma consequência nova que a 013 cobra: **na forma decisória é o caráter
eliminatório que dá consequência à decisão.** Etapa decisória que não o declara não publicou o que o
sentido desfavorável produz, e a 013 recusa consolidá-la em vez de inventar o efeito — decisão
registrada na contraparte desta em `specs/013`.

**10 · Todos os campos normativos da Etapa introduzidos pela 012 são retificáveis pelo canal
institucional suportado**, inclusive a forma e os dois rótulos, e inclusive os dois que o primeiro
incremento deixou para trás. O requisito é de **capacidade**, e não de contagem: qual é a lista, e
onde ela vive, é do `/plan`; o que a spec exige é que publicar uma forma que só se corrige pela API
não seja um resultado aceitável. A metade `documentRequirements` da lacuna E2E-004 continua fora
desta feature — é trabalho de outra natureza, e de outra leva.

**O que esta decisão não é.** Não é barema: pontuação por critério, com itens e limites por item,
continua fora pela recusa do §21, que segue valendo por inteiro. A conclusão decisória não pontua
nada — ela é o que permite **não** pontuar. E existe uma terceira forma plausível que nenhum dos
três Editais exercita — conceito ordinal, A/B/C, menção de prova didática —, deliberadamente não
construída: `forma` é o ponto de extensão por onde ela entraria, e desenhá-la antes da regra que a
consome seria inventar norma.

---

## 6. Problema

A 011 organizou o trabalho e parou antes de executá-lo. Hoje, terminada a alocação, o sistema sabe
que quarenta pessoas podem atuar na Análise documental — e não sabe mais nada. A operação real
recomeça fora dele:

- quem avalia quais candidatos vira planilha;
- a documentação é baixada em lote e circula por pasta compartilhada;
- a pontuação, ou o deferimento, é anotada em papel ou em documento de texto;
- o parecer chega por e-mail;
- e a consolidação é feita à mão, sem que exista registro de quem avaliou o quê e quando.

O custo não é só operacional. Sem registro do ato, um recurso não tem contra o que ser respondido,
e a instituição não consegue demonstrar que a avaliação seguiu o que o Edital publicou.

---

## 7. Princípios

### P-001 — Autorização é composta, e a primeira metade não se refaz

> pode atuar na Etapa (011) **e** esta inscrição foi atribuída a esta pessoa (012).

Nenhuma das duas basta sozinha. A 012 não reimplementa a primeira nem a contorna.

### P-002 — Distribuir é ato administrativo

Quem distribui tem nome, e o ato fica registrado. Um algoritmo pode **propor**; quem responde pela
distribuição é uma pessoa. Isso não é preferência de produto: ato com efeito administrativo exige
autoria demonstrável.

### P-003 — Manual primeiro, e não por conservadorismo

A distribuição automática precisa de parâmetros que o domínio ainda não tem: quantas avaliações por
candidato, qual carga é tolerável, quais impedimentos existem. Construí-la antes obrigaria a chutar
os três. A distribuição manual não precisa de nada além do que a 011 entregou — e produz, em uso
real, exatamente os números que faltam.

### P-004 — A escala é a de mil candidatos, e ela decide o desenho

Mil inscritos com dupla avaliação são duas mil atribuições. Nenhuma tela desta feature pode custar
um clique por atribuição, e nenhuma consulta pode custar por linha.

### P-005 — Documento é instrumento de trabalho, não acervo

O avaliador abre o que precisa para avaliar, sob a atribuição que o autoriza, e cada abertura fica
registrada. Não existe download em lote, não existe navegação livre pelo acervo, e não existe
acesso a inscrição que não lhe foi atribuída.

### P-006 — Avaliar não é decidir

A 012 registra o que **um** avaliador afirmou sobre **uma** inscrição — uma pontuação ou um
sentido, conforme a forma que a Etapa publicou. Média, quórum, divergência, desempate e resultado
são da 013. Antecipá-los aqui faria a afirmação de uma pessoa parecer decisão da instituição.

É por isso que o campo da forma decisória chama-se `sentido`, e não `decisão` (D-008). Duas análises
documentais podem afirmar sentidos opostos, e resolver isso continua sendo da 013, exatamente como
média, quórum e divergência já eram. A 012 não ganhou poder de decidir; ganhou uma segunda forma de
afirmar.

### P-007 — O que o Edital publicou é o que vale

A forma da conclusão, os rótulos com que ela é lida, a pontuação máxima, o caráter eliminatório e a
nota mínima vêm do conteúdo vigente, e não de configuração de tela. Se a regra não está publicada,
ela não pode ser aplicada — e é por isso que a pontuação máxima precisou passar a ser publicada
(D-001), e a forma e os rótulos também (D-008).

---

## 8. Conceitos de domínio

### 8.1 Atribuição

```text
AtribuicaoAvaliacao
- membro da comissão
- edital + identidade da Etapa no conteúdo publicado
- inscrição
- ativo
- criado_em / criado_por
- inativado_em / inativado_por
```

> esta pessoa avalia esta inscrição, nesta Etapa.

**FR-001** — A Atribuição só produz efeito sob alocação ativa. Perder a alocação torna a Atribuição
inoperante, exatamente como a 011 fez com a Etapa — e sem tocar em uma única linha de Atribuição
(D-004).

**FR-002** — A inscrição atribuída deve pertencer ao Edital da Etapa, e a verificação percorre
`inscrição → edital → processo`, como a 011 faz para a alocação.

**FR-003** — Não permitir duas Atribuições ativas equivalentes: mesma pessoa, mesma inscrição,
mesma Etapa. A restrição é parcial sobre o ativo, para que redistribuir a mesma inscrição à mesma
pessoa depois de removê-la crie linha nova e preserve o histórico — o padrão que a 011 já adotou.

**FR-004** — Remover a Atribuição é inativá-la. Isso revoga o acesso e **não** apaga a Avaliação já
registrada.

**FR-109** — **Toda tela desta feature é alcançável por link**, a partir de onde o ator entra.

A 012 ficou pronta, testada e **inalcançável**: nenhuma tela do sistema tinha link para a
distribuição de uma Etapa — nem a lista de Processos, nem o Processo, nem o Edital, nem a Alocação
por Etapa, nem Minhas Etapas —, e impedimentos, trilha e conclusões preservadas pendem dela. A
lacuna atravessou a implementação inteira porque toda verificação chegava por `reverse()` e todo
roteiro montava a URL: quem verifica nunca clica para chegar.

O elo é a **Etapa**, que é onde a 011 e a 012 se encontram: a matriz de alocação lista as Etapas do
Edital, e cada uma leva à sua distribuição. É o princípio VI cobrado no lugar onde ele é fácil de
perder — a jornada demonstrável pelo canal do ator inclui **chegar** à tela.

Do mesmo defeito: quem tem `comissao:gerir` e não integra a comissão não recebia link nenhum para
ela. A permissão existia, o caminho não — e quem constitui a comissão é justamente quem ainda não a
integra.

**FR-112** — **Ler o documento e registrar a avaliação acontecem na mesma tela.** O documento
abria por cima da página, e ler e avaliar eram duas telas que se revezavam — com o formulário
preenchido correndo o risco de se perder no caminho. Em tela larga, o documento fica ao lado do
formulário.

Três coisas não mudam, e é o que separa isto de uma conveniência:

- **a abertura continua sendo um ato.** Nada é carregado sozinho ao entrar na inscrição: quem abre
  um documento clica nele, e é esse clique que a trilha registra, com o mesmo significado de antes
  (FR-027, FR-053). Embutir o arquivo automaticamente faria “abriu o documento” virar “abriu a
  inscrição” — o mesmo evento dizendo outra coisa;
- **a conferência de integridade e a entrega mediada são as mesmas** (FR-029), porque o painel
  carrega exatamente a resposta que o link carregava;
- **abaixo de tela larga nada disso vale**: não há onde pôr duas colunas, e o documento continua
  abrindo em aba própria — que é o que a tela fazia antes. Sem JavaScript, idem.

O documento é emoldurável **pela própria origem**, e por nenhuma outra: sem isso o
`X-Frame-Options: DENY` do resto do sistema bloquearia a nossa própria moldura. A proteção contra
clickjacking continua valendo contra quem ela protege.

E o painel recebe a largura da **página**, e não a de um limite herdado: com o limite antigo o PDF
ficava com 550 px enquanto sobravam 412 px de tela, e uma página A4 renderizava a 69% do tamanho.
A separação entre a largura do texto e a da estrutura está em `shared/_tokens.css.html` — é ela que
faz esta feature caber na tela.

**FR-111** — **O seletor de identidade oferece quem tem trabalho de comissão.** Presidir e avaliar
não são papéis — vêm do vínculo, objeto a objeto —, e nenhuma caixa daquela tela os concede. Quem
digitava o próprio nome, ou aceitava o exemplo que vinha preenchido, entrava sem vínculo nenhum e
via uma página vazia: o campo em branco era uma parede antes de qualquer percurso.

A lista diz **o que cada identidade alcança** — preside este Processo, integra aquele, tem tantas
Etapas alocadas, tantas avaliações pendentes — e não apenas que ela existe. Some junto com o
seletor, quando o diretório institucional for integrado (FR-058).

**FR-113** — **O foco começa onde o trabalho começa, e o trabalho começa na leitura.** A tela da
inscrição abria com o cursor no campo de pontuação: a ordem da página dizia uma coisa — candidato,
documentos, avaliação — e o cursor dizia outra, convidando a pontuar antes de qualquer documento
ter sido aberto.

O foco para no primeiro documento por abrir. Ele vai para a nota quando não há o que ler antes:
quando esta pessoa já abriu algum documento desta inscrição, quando não há documento nenhum, ou
quando há aviso a ler — que tem prioridade sobre tudo.

**Sugerida, e não imposta**, como o período previsto de FR-095: nada impede pontuar antes de abrir,
porque documento ausente é caso legítimo e ninguém precisa abrir arquivo para registrar que não
havia o que conferir.

E a tela diz, numa linha, **se houve leitura** — nas duas direções. Só a frase negativa deixaria
o caso oposto em silêncio, e silêncio é indistinguível de defeito: quem chega e encontra o cursor
na nota não saberia se o sistema pulou a leitura ou se foi ela mesma que já leu.

O que ela afirma é **o fato, e não o minuto**. Para quem avalia dezenas de inscrições por dia,
"já vi este?" é sim ou não; a hora exata não muda decisão nenhuma e disputa espaço com o que muda.
Ela é dado de auditoria, e o lugar dela é a **trilha**, de onde o fato vem (FR-027) — na tela fica
ao alcance de quem a procure, fora do caminho de quem não a procura.

**FR-114** — **Cada documento diz se esta pessoa já o abriu.** FR-113 responde "houve leitura?"
para a inscrição inteira. Com dez requisitos exigidos, essa resposta não basta: "onde eu parei"
volta a ser pergunta que só a memória responde, e quem retoma o trabalho relê o que já leu ou pula
o que não leu.

Cada linha da lista mostra **que esta pessoa já abriu aquele documento**, e a lista mostra quantos
dos entregues já foram abertos — a contagem só aparece quando há mais de um, porque com um só ela
não informa nada que a linha não diga. O instante segue a regra de FR-113: fica ao alcance, não
impresso na linha, onde competiria em largura com o nome do documento.

**Aberto, e não avaliado.** A Avaliação é uma só por inscrição — nota e parecer sobre o conjunto —
e não existe veredito por documento: marcar "avaliado" em cada linha inventaria um julgamento que
o domínio não tem, e transformaria a leitura numa lista de conferência cujo preenchimento pareceria
ter efeito sobre o resultado.

A marca é **de quem abriu**, e não do documento: ela vem da trilha, filtrada pela Atribuição e pelo
ator (FR-027). Abertura de outra pessoa — outro avaliador, ou a consulta administrativa da 009 —
não aparece como trabalho feito, porque apareceria como trabalho de quem não o fez.

**FR-115** — **O cartão da Etapa responde as duas perguntas de quem tem várias.** "115 pendentes
de 255" responde o que se age; não responde o que se compara — qual destas Etapas nem começou, e
qual está no fim. Ao lado de "200 pendentes de 200", descobrir isso custava duas divisões a quem
lê, e é a pergunta que se faz olhando a lista inteira.

O cartão traz a contagem pendente, o percentual concluído e a barra que diz o mesmo de relance.

**O percentual arredonda, e arredondar mente nas duas pontas**: uma avaliação de 255 vira "0%" e dá
por não começada a Etapa que já andou; 254 de 255 vira "100%" e dá por encerrada a que ainda deve
uma. Os extremos ficam reservados aos extremos.

E os **quatro estados são quatro**, e não três parecidos: concluída ganha a palavra, porque
"0 pendentes" é a mesma notícia dita ao contrário; e alocada sem distribuição diz isso, em vez de
omitir a linha e ficar idêntica ao cartão de quem não sabe informar.

**FR-110** — **O caminho não pode custar mais que o trabalho.** Numa Mesa de 230 inscrições, cada
clique de navegação é cobrado 230 vezes. Três deles não decidiam nada:

- **o documento abre em aba própria.** Servido `inline` na mesma aba, o PDF substituía a página — e
  quem havia digitado a nota perdia o formulário. Eram dois cliques, abrir e voltar, e um risco;
- **o foco começa no campo de pontuação**, que é onde o trabalho começa. Salvo quando há aviso a
  ler: aí o foco é dele;
- **concluir leva à próxima pendente.** Quem conclui está, quase sempre, seguindo — e a Mesa fica a
  um clique. O aviso nomeia **qual** inscrição foi concluída, porque a tela que aparece é a de
  outra, e uma confirmação sem nome se referiria ao candidato errado.

Salvar rascunho não avança: quem salva sem concluir está no meio do trabalho.

**FR-108** — **Quem perde trabalho é avisado.** A revogação é imediata, e era silenciosa: a
atribuição sumia da Mesa e a contagem mudava, sem nada dizer o que houve. A trilha registra o ato
com autor e motivo e responde 404 para quem avalia — corretamente, porque avaliar não é auditar —,
de modo que a pessoa cujo trabalho foi retirado era a única sem canal para saber disso.

A Mesa mostra o que saiu dela, quando e por qual ato. Não é registro novo: é o registro que já
existe, mostrado a quem ele afeta.

**FR-063** — A Atribuição espelha a forma da alocação, com `etapa_id` designando a Etapa do
conteúdo publicado e não a linha de elaboração (D-004, e 011 D-002).

### 8.2 Avaliação

```text
Avaliacao
- atribuição
- forma:     PONTUADA | DECISORIA      ← publicada pela Etapa, gravada na conclusão
- pontuação                            ← exigida quando PONTUADA, ausente quando DECISORIA
- sentido:   FAVORAVEL | DESFAVORAVEL  ← exigido quando DECISORIA, ausente quando PONTUADA
- parecer
- estado: RASCUNHO | CONCLUIDA
- versão consolidada sob a qual foi concluída
- revisão
- concluída_em / concluída_por
```

> o que esta pessoa afirmou sobre esta inscrição, e sob qual regra.

**FR-116** — **Uma Avaliação concluída possui a conclusão completa segundo a forma que a Etapa
publicou** (D-008). Completa significa *tem o que a forma exige*, e não *tem nota*:

```text
forma = PONTUADA   → pontuação presente  e sentido ausente
forma = DECISORIA  → sentido   presente  e pontuação ausente
```

A verificação é **do banco**, e continua sendo ela o que define "concluída" ali — como já era antes
desta revisão. Relaxar o campo e confiar a regra à aplicação seria trocar o invariante forte pela
promessa da tela, que é precisamente o que esta spec recusou ao escrevê-lo.

**FR-117** — A Avaliação **grava a forma sob a qual foi concluída**, e a forma gravada é a que a
versão consolidada lida em FR-096 publicava para aquela Etapa. Não é segunda fonte concorrente com a
Etapa: a Etapa diz qual regra vige, e a conclusão diz sob qual regra foi feita. É a mesma preservação
de sentido de FR-071, pelo mesmo motivo — e é o que mantém a verificação local, já que uma verificação
do banco não referencia outra tabela.

**FR-118** — Na forma decisória, o que o avaliador registra é `FAVORAVEL` ou `DESFAVORAVEL`, e o que
ele **lê na tela** são os rótulos que a Etapa publicou. O domínio nunca guarda o rótulo no lugar do
sentido, e a tela nunca mostra o sentido no lugar do rótulo. Etapa que não publicou rótulos não é
decisória, e a recusa é da elaboração e da Retificação, não da Mesa.

**FR-005** — Uma Avaliação pertence a exatamente uma Atribuição, e há **no máximo uma** Avaliação
por Atribuição. A restrição é do banco, e não da tela que grava.

**FR-006** — A autoria da Avaliação é histórica: ela sobrevive à saída da pessoa da comissão, e por
isso o autor é registrado como identificador estável, e não como referência a um vínculo que pode
ser inativado.

**FR-071** — A Avaliação registra a **Versão Consolidada** sob a qual foi concluída. Sem isso, a
Constituição fica sem resposta: ela exige que, para cada Avaliação, seja possível determinar
Processo, Edital, versão, retificações, cronograma, requisitos, etapas, critérios, pesos e regras
**então vigentes**, e que regra atual não substitua regra histórica. O precedente é a inscrição,
que já guarda a versão que o candidato aceitou.

**FR-072** — A Avaliação **não copia** a pontuação máxima, a nota mínima nem o caráter da Etapa. A
versão registrada os reproduz, e duplicá-los criaria a segunda fonte divergente que o princípio da
fonte autoritativa única proíbe.

**A forma é a única exceção, e ela é exceção por uma razão que os outros três não têm** (FR-117): a
verificação que define "concluída" precisa ser verificável na própria linha, e nenhum dos outros três
participa dessa verificação. Copiar a nota mínima não tornaria nenhuma regra local; copiar a forma
torna. Onde a cópia não compra invariante, ela continua proibida.

**FR-073** — Se a versão vigente mudar entre a última gravação e a conclusão, o avaliador é avisado
**antes** de concluir e reconhece a mudança explicitamente. **O reconhecimento é obrigatório**:
concluir sem declarar contra qual versão se escreveu é recusado, senão omitir o campo do envio
desligaria este requisito pelo cliente. Retificação que muda a pontuação máxima
no meio do trabalho não pode ser descoberta depois, no parecer de outra pessoa. O precedente é o
aviso de Retificação que a inscrição já dá ao candidato, e a razão é a mesma.

**FR-096** — O aviso sozinho não basta, e é aqui que ele se fecha: **a versão contra a qual a
conclusão é validada e a versão gravada na Avaliação são a mesma**, lida uma vez dentro da transação
que conclui — e a Etapa é extraída **do conteúdo dessa versão**, e não de uma segunda consulta.

Ler a versão para avisar e outra para gravar produziria uma Avaliação que afirma obedecer a uma
regra contra a qual nunca foi verificada, o que é pior do que não registrar versão alguma. E
resolver a Etapa por fora reabre a mesma janela por outro caminho: uma Retificação consolidada
entre as duas leituras faria a pontuação ser validada pela Etapa nova e a versão antiga ficar
gravada.

**FR-074** — Existe **no máximo uma Avaliação concluída** por pessoa, inscrição e Etapa, qualquer
que seja o número de Atribuições — ou de vínculos de comissão — que tenham existido ali. Reatribuir
a inscrição a quem já concluiu a avaliação dela naquela Etapa é recusado, e a recusa nomeia o único
caminho de volta: a reabertura da presidência (FR-036).

**"Pessoa" aqui é a identidade institucional estável, e nunca o vínculo de comissão.** Vínculo é
linha que a remoção inativa e a readmissão recria; ancorar a garantia nele permitiria que remover e
readicionar alguém liberasse uma segunda conclusão sua sobre a mesma inscrição — que é precisamente
o contorno que este requisito existe para fechar.

**FR-075** — São **três** coisas distintas, e confundi-las foi um erro que esta spec já cometeu
duas vezes. A segunda foi de vocabulário: "invalidar" chegou a significar, no mesmo documento,
*apagar ou alterar o registro* e *tirar do conjunto que a 013 consome*. **Passa a ter um sentido
só, e ele é o segundo:**

| termo | significa, aqui e em todo lugar |
|---|---|
| **preservar** | o registro não é apagado, não é alterado, e continua consultável |
| **tornar inelegível**, ou **invalidar** | o registro deixa de integrar o conjunto de avaliações válidas, por ato nomeado, com autor e motivo |

As duas coisas acontecem **juntas** no caso desta seção: uma Avaliação sob Atribuição inativa é
preservada **e** inelegível. Invalidar nunca significa mexer no registro, e preservar nunca
significa continuar valendo.

Dito isso, as três colunas:

| | Avaliação sob Atribuição inativa |
|---|---|
| **visibilidade operacional** | não — não aparece na Mesa do avaliador, não conta e não é retomada |
| **preservação histórica** | **sim** — permanece íntegra e consultável |
| **elegibilidade para a 013** | não — não integra o conjunto de avaliações válidas |

Um rascunho abandonado sob Atribuição removida nunca é retomado por uma Atribuição nova: a nova
nasce vazia.

**FR-091** — A preservação histórica é **consultável**, e não apenas existente no banco. Presidência
e auditoria conseguem reconstruir o ocorrido: o que a pessoa havia registrado, quando, sob qual
versão, e por qual ato aquilo deixou de valer. Uma avaliação concluída e depois invalidada é
exatamente o tipo de coisa que um recurso pergunta, e "está gravada em algum lugar" não é resposta.

A concessão é a **cada um dos dois**, e não à interseção: quem preside sem papel de auditoria
consulta, e quem audita sem gerir o Processo também. Exigir as duas coisas ao mesmo tempo reduziria
a consulta ao usuário híbrido, que é justamente quem não responde a recurso.

A consulta **não é a trilha**, e não pode ser: a trilha guarda que o ato aconteceu e nunca a
pontuação nem o parecer (FR-054). O conteúdo do que foi concluído vive no registro do domínio, e é
de lá que ele é lido.

**FR-104** — **Concluir e remover atribuição serializam pela mesma Atribuição.** As duas disputam
a linha, e sem trava comum a remoção lê "pendente", inativa, e a conclusão grava depois — o que
produz avaliação concluída **e** inelegível pela via comum: o efeito sem o ato que FR-092 impede,
por concorrência em vez de por decisão. Quem chega depois encontra a Atribuição já inativa e é
recusado; quem chega antes conclui, e a remoção passa a ver a conclusão.

**FR-092** — Depois de concluída a Avaliação, a inativação da Atribuição que a tornaria inelegível
**não é operação comum de redistribuição**: exige ato nomeado, com motivo obrigatório e auditoria —
impedimento, ou anulação declarada como tal. A operação corriqueira de retirar e redistribuir
alcança apenas Atribuição sem Avaliação concluída.

A razão não é formalismo. Sem essa restrição, a sequência abaixo seria possível e indistinguível de
trabalho normal:

```text
dois avaliadores concluem
        ↓
a presidência não gosta de uma das notas
        ↓
remove aquela Atribuição
        ↓
a avaliação deixa de ser elegível
        ↓
distribui a inscrição a um terceiro
```

Isto é escolher qual avaliação conta no resultado, com a aparência de organizar o trabalho.
**Nenhum caminho da 012 pode produzir esse efeito sem que ele tenha nome, autor e motivo.**

**FR-093** — A organização do trabalho mostra as avaliações tornadas inelegíveis daquela Etapa, com
o ato que as invalidou, quem o praticou e o motivo declarado. Invalidação visível é o que impede a
seleção silenciosa; invalidação apenas registrada não é.

### 8.3 Impedimento

```text
Impedimento
- membro da comissão
- inscrição
- motivo
- criado_em / criado_por
```

> esta pessoa não avalia esta inscrição, e o motivo está escrito.

---

## 9. Quantas avaliações cada inscrição recebe

A 011 recusou-se a fixar isto e mandou a 012 classificar. **A classificação é: é regra normativa.**

O número de avaliações que uma inscrição recebe afeta direito do candidato — decide se uma nota
isolada o elimina ou se há segunda leitura. Regra que afeta direito não pode ser configuração
operacional invisível.

**FR-007** — A Etapa passa a declarar, como conteúdo normativo publicado, quantas avaliações cada
inscrição recebe e qual é a pontuação máxima daquela Etapa.

**FR-119** — A Etapa passa a declarar, também como conteúdo normativo publicado, **a forma da
conclusão** que ela exige — `PONTUADA` ou `DECISORIA` — e, na forma decisória, os dois rótulos com que
o Edital nomeia o sentido favorável e o desfavorável (D-008). A classificação é a mesma de FR-007,
pelo mesmo argumento: decidir se o trabalho do avaliador produz nota ou deferimento afeta direito do
candidato tanto quanto decidir quantas pessoas o avaliam.

**FR-008** — A 012 produz **dois** incrementos canônicos, em momentos distintos e por razões
distintas: o primeiro subiu a versão de 4 para 5 e levou juntas as duas propriedades de FR-007
(D-001); o segundo sobe de 5 para 6 e leva juntas as três de FR-119 (D-008). **Dentro de cada
incremento as propriedades entram juntas**, pela razão que o `SCHEMA_VERSION` registra; entre
incrementos não há essa exigência, porque o segundo nasce de mudança de requisito posterior e não de
omissão do primeiro.

**FR-064** — Cada incremento sobe a versão canônica do snapshot e alcança a Etapa publicada, o
esquema que verifica sua forma, o caminho de elaboração e o documento materializado. **Nenhuma
outra coleção do conteúdo publicado muda**, nos dois.

**FR-009** — Edital publicado antes do primeiro incremento continua **legível**, e a ausência da
declaração significa uma avaliação por inscrição.

**FR-120** — Edital publicado antes do **segundo** incremento continua legível pela mesma regra, e a
ausência da forma significa `PONTUADA` — não por conveniência, mas porque o domínio anterior não
admitia outra forma (D-008). A ausência dos rótulos, nesse conteúdo, é correta: na forma pontuada não
há sentido a nomear. A leitura é **uma só**, e vale tanto no consumo quanto na elevação que a
Retificação faz; escrever a mesma interpretação em dois lugares independentes é como ela passa a
divergir.

**FR-098** — Edital publicado antes de qualquer um dos dois incrementos continua **retificável**. A
Publicação original não é alterada, e a Retificação que o alcança produz Versão Consolidada na versão
vigente, interpretando a ausência pela leitura de FR-009, FR-066 e FR-120 (D-002, D-008). A elevação
não tem autor e não é apresentada como alteração normativa, porque não altera norma nenhuma. **A
D-002 alcança o segundo incremento por inteiro**: se o mecanismo atual não comportar duas origens sem
violar imutabilidade, proveniência ou hash, a decisão volta a esta spec em vez de virar precondição
de implantação.

**FR-010** — Alterar qualquer uma dessas declarações num Edital publicado é Retificação, com tudo
o que ela já exige. Alterar a **forma** é Retificação como as demais, e a conclusão já gravada
continua interpretável sob a forma que a governou (FR-117).

**FR-089** — A quantidade declarada é a **cardinalidade normativamente prevista** de avaliações
válidas por inscrição naquela Etapa. Não é mínimo, não é meta operacional e não é sugestão. É a
classificação que a 011 adiou (D-007).

**FR-065** — Dela decorre um **teto**: a atribuição excedente é recusada, e a recusa nomeia o número
que o Edital publicou.

**FR-090** — O teto conta o que é **elegível** — Atribuições ativas e Avaliações que ainda valem —,
e nunca o registro histórico. Avaliação tornada inelegível libera a vaga que ocupava, de modo que
uma substituta possa ser distribuída (D-007).

**FR-076** — A mesma quantidade é **piso apenas para efeito de contagem**: o déficit alimenta
FR-014, é estado legítimo (FR-015) e não bloqueia distribuir, avaliar, concluir nem produz efeito
algum sobre a Avaliação. A consequência da insuficiência é da 013.

**FR-066** — A pontuação máxima publicada é o limite superior da validação de FR-033, **na forma
pontuada**. Etapa sem a declaração — porque foi publicada antes do primeiro incremento — não admite
pontuação acima do que a persistência comporta, e a tela diz que o Edital não declarou limite, em vez
de inventar um.

**FR-121** — Na forma decisória, pontuação máxima e nota mínima **não se aplicam**, e a Etapa não as
publica. Não é omissão tolerada: publicar `maximumScore = 100` numa Etapa que não pontua seria
exatamente a regra normativa fictícia que P-007 existe para impedir. O peso permanece propriedade da
Etapa nas duas formas, porque descreve a composição entre Etapas e não a conclusão local (D-008).

---

## 10. US1 — Distribuir as inscrições

**Prioridade: P1**

Como presidente, quero distribuir as inscrições entre quem está alocado à Etapa, para que cada
avaliador saiba exatamente o que lhe cabe.

**FR-011** — Só recebe Atribuição quem tem alocação ativa naquela Etapa. A recusa é a mesma forma
que a 011 usa para quem não é membro ativo.

**FR-012** — Só é atribuível inscrição **submetida** do Edital daquela Etapa.

**FR-013** — A distribuição é **em lote**: uma submissão atribui muitas inscrições a um avaliador,
ou às várias pessoas selecionadas. Um clique por atribuição é inviável na escala real. O precedente
é a alocação em lote da 011, e a regra que ela fixou vale aqui: quem já tem a atribuição não faz o
lote falhar, porque recusar o conjunto por causa de uma linha seria punir o caminho normal.

**FR-101** — A combinação do lote é **uniforme**: cada inscrição selecionada vai para cada avaliador
selecionado. O lote **não reparte** — nada nele divide o conjunto entre as pessoas, sorteia ou olha
carga. Repartir é escolher quem avalia quem, e isso é decisão com autoria: quem quer dividir cem
inscrições entre dois avaliadores faz duas submissões de cinquenta, e as duas são atos dela
(FR-017, FR-019, P-002).

**FR-102** — Quando o conjunto **não cabe** — restam menos vagas do que pessoas selecionadas para
aquela inscrição —, a inscrição inteira é recusada, e a recusa diz quantas vagas restam e quantas
pessoas foram selecionadas. Conceder as vagas na ordem em que os avaliadores vierem faria a
ordenação do banco decidir quem avalia quem: ninguém teria tomado a decisão, e ela pareceria
distribuição. A escolha volta para quem responde por ela.

**FR-014** — A tela mostra, antes do detalhe: inscrições sem avaliador suficiente, quantas cada
pessoa recebeu, quantas faltam para cumprir o declarado na Etapa.

**FR-015** — Distribuição parcial é estado válido e visível. Ninguém distribui mil inscrições de
uma sentada.

**FR-016** — Cada atribuição gera evento de auditoria próprio, com quem atribuiu, a quem, qual
inscrição e quando — pela mesma razão que a alocação em lote da 011 gera um evento por alocação: a
trilha responde por agregado.

**FR-067** — Quem distribui é quem pode gerir a comissão daquele Processo, pelas duas bases que a
011 já reconhece — permissão sistêmica ou presidência do Processo —, e a trilha registra qual
delas autorizou o ato.

---

## 11. Distribuição automática

**FR-017** — A V1 **não** distribui automaticamente.

**FR-018** — Quando existir, a distribuição automática será **proposta**: o sistema sugere, a
presidência confirma, e o ato registrado é o da confirmação. Nunca um ato do sistema.

**FR-019** — Não implementar carga máxima, balanceamento por perfil, sorteio nem substituição
automática antes de existir uso real que informe os parâmetros.

**FR-107** — **A proposta de FR-018 passa a existir, e nos termos que ele fixou.** O uso real que
FR-019 exigia apareceu no percurso de um Processo de 600 inscritos com dupla avaliação: distribuir
custava 24 telas e cerca de 700 marcações, e o equilíbrio da carga era aritmética de quem
distribui — o que não é organização do trabalho, é digitação.

O que existe é isto, e nada além:

- a presidência escolhe **entre quem** distribuir e pede a proposta;
- o sistema devolve o plano **inteiro**, sem gravar nada: quantas atribuições no total, quantas
  para cada pessoa — antes e depois —, e o que fica de fora e por quê;
- a presidência confirma, e **o ato registrado é o da confirmação**, com quem confirmou;
- cada Atribuição continua gerando o seu evento (FR-016), como no lote manual.

**A regra é por menor carga projetada, com desempate estável pelo identificador institucional.**
Não há sorteio, não há carga máxima e não há perfil: o parâmetro é o que a Etapa já declara e a
carga que a banca já tem. Sorteio, em particular, tornaria a proposta irreprodutível — e proposta
que não se reproduz não pode ser conferida sob trava antes de gravar.

**A proposta confirmada é conferida contra a proposta executada**, pela mesma razão de FR-106: entre
ver e confirmar, uma conclusão nova ou um impedimento mudam **quem** recebe o quê sem mudar quantos
são. Divergiu, o ato não acontece e a proposta é refeita. E sem proposta confirmada não há ato: um
envio que não traga a confirmação é recusado, senão a garantia seria desligável por quem monta o
formulário.

**O caminho manual não é substituído.** Quem quer escolher inscrição por inscrição continua
escolhendo, na mesma tela, com a mesma forma uniforme de FR-013.

---

## 12. US2 — A Mesa

**Prioridade: P1**

Como avaliador, quero abrir minha lista de trabalho e saber o que falta.

Página conceitual:

> # Análise documental — Edital 07/2027
>
> 48 atribuições · **31 pendentes** · 17 concluídas
>
> [ Pendentes ] [ Concluídas ] [ Todas ]
>
> Inscrição 0234 — Professor de Informática — **Avaliar**
> Inscrição 0235 — Professor de Informática — **Avaliar**

**FR-020** — A Mesa mostra todas e somente as inscrições atribuídas àquela pessoa, naquela Etapa.

**FR-021** — Filtro por pendente, **em rascunho** e concluída, e contagem visível.

O rascunho é estado próprio na lista, e não conforto: sem distingui-lo, uma avaliação começada
aparece igual às que ninguém abriu. Numa Mesa de centenas, retomar o trabalho vira memória, e uma
avaliação em andamento pode ficar esquecida sem que nada indique.

**FR-022** — A lista é paginada. Quarenta e oito é comum; quinhentas não pode quebrar a tela.

**FR-023** — Alocação abre a porta da Etapa; a Atribuição abre a inscrição. As duas coisas que
isso significa são diferentes e não se confundem:

- quem está alocado **alcança a Mesa** daquela Etapa, e ela vem **vazia** — porque a Etapa é dele
  por alocação, e responder como inexistente negaria o que a 011 concedeu;
- quem está alocado e não tem Atribuição **não alcança inscrição alguma**, e a tentativa responde
  como recurso inexistente (FR-044).

O estado vazio explica que ainda não há inscrições distribuídas para essa pessoa, e não sugere
falta de permissão.

**FR-024** — A consulta da Mesa não pode custar uma verificação de autorização por linha. A forma
em lote que a 011 entregou é `etapas_autorizadas`, e é ela que a Mesa usa — uma vez, e nunca por
inscrição.

---

## 13. US3 — Abrir a inscrição como instrumento de trabalho

**Prioridade: P1**

Como avaliador, quero ver o que o candidato enviou, sob o requisito que cada documento atende.

**FR-025** — O avaliador abre os documentos da inscrição atribuída a ele, cada um sob o Documento
Exigido que ele atende — a ligação que a 009 já grava, e não uma pasta com o nome da pessoa.

**FR-026** — A entrega do arquivo é mediada, como já é para a equipe: nada é alcançável por
conhecer o endereço.

**FR-027** — Cada abertura de documento é registrada na trilha, com ator, inscrição, requisito e
instante.

**FR-028** — Não existe download em lote, exportação do acervo nem navegação por inscrição alheia.

**FR-029** — A verificação de integridade que já existe continua valendo, na forma em que existe: a
conferência acontece **antes** do primeiro byte, a cópia conferida é a servida, e divergência é
recusa registrada, não aviso silencioso.

**FR-030** — A tela mostra os dados de identificação necessários ao trabalho e nada além, aplicando
o mascaramento que a consulta administrativa já usa.

**FR-068** — A rota do avaliador é própria, e sua autorização é a composta da seção 16. Ela não
reutiliza a permissão da consulta administrativa da 009, que vale para o Edital inteiro e
contradiria FR-055 (D-005).

---

## 14. US4 — Registrar a avaliação

**Prioridade: P1**

Como avaliador, quero registrar o que afirmo sobre a inscrição — pontuação ou sentido, conforme a
forma que a Etapa publicou — e o parecer, salvar sem concluir, e concluir quando terminar.

**FR-031** — A Avaliação nasce como rascunho e é gravada sem exigir conclusão.

**FR-122** — **A Mesa apresenta um instrumento, e não os dois.** Qual deles é decidido pela forma
que a versão vigente publica para aquela Etapa, e nunca por preferência de quem monta a tela. Uma
Etapa decisória não oferece campo de nota que ninguém deveria preencher, e uma Etapa pontuada não
oferece par de rótulos que ninguém publicou. O envio que trouxer o campo da outra forma é recusado no
domínio, e não apenas escondido pela tela — esconder é decisão de apresentação, e a regra é normativa.

**FR-103** — **O rascunho valida a forma; a conclusão valida a regra.** Salvar exige que a
pontuação seja um número que o registro comporte — finito, não negativo, na escala do conteúdo
publicado. Não exige a pontuação máxima do Edital: quem está no meio do trabalho pode gravar um
valor que ainda não decidiu, e cobrar a regra normativa ali obrigaria a concluir para descobrir se
o número passa. A máxima é cobrada no ato que tem efeito (FR-033).

Valor que não é número — infinito, indefinido, expoente que a coluna não comporta — é recusado nos
dois, com mensagem: forma impossível não pode virar erro interno.

**Na forma decisória a assimetria é a mesma, com outro conteúdo**: o rascunho aceita sentido ainda
não escolhido, porque quem está no meio do trabalho ainda não decidiu; a conclusão o exige. Sentido
que não é `FAVORAVEL` nem `DESFAVORAVEL` é recusado nos dois.

**FR-032** — Concluir é ato explícito, distinto de salvar.

**FR-033** — **Na forma pontuada**, a pontuação é validada contra o que o Edital publicou para
aquela Etapa: a pontuação máxima, a forma decimal do conteúdo publicado e a não-negatividade. **A nota mínima não recusa
pontuação nenhuma** — nota abaixo do mínimo é registro válido, é justamente o que o avaliador
precisa poder afirmar, e a consequência dela é da 013. O que a nota mínima produz aqui é uma coisa
só: torna o parecer obrigatório (FR-034).

**FR-034** — O parecer é texto livre. Ele é o que responde recurso, e por isso não pode ser
opcional quando a Etapa for eliminatória e a nota ficar abaixo do mínimo.

**FR-123** — **Na forma decisória, o sentido `DESFAVORAVEL` exige parecer, e a exigência não depende
do caráter da Etapa.** A assimetria com FR-034 é deliberada e não é descuido: o desfavorável é o caso
em que o candidato mais precisará da fundamentação para recorrer, e é contra o parecer que o recurso
responderá. Exigir parecer também no favorável é configuração futura — pode haver Edital que o peça,
e generalizar agora seria aplicar regra que nenhum dos três publicou.

**FR-035** — Avaliação concluída é imutável para o avaliador, e a imutabilidade é garantida no
agregado, como a 009 fez com a inscrição enviada — e não apenas na tela que grava.

**FR-036** — Reabrir é ato da presidência, com motivo, registrado. Recurso e erro material existem;
o que não pode existir é reabertura silenciosa.

A reabertura mora **onde se lê o que foi concluído** — a página das conclusões preservadas —, e não
na tela de distribuição. Ali ela ocupava uma linha e um formulário por avaliação concluída, sem
paginar: numa Etapa de 600 inscritos com dupla avaliação são 1.200 formulários acima da área de
trabalho, na tela que a presidência mais recarrega. E decidir sobre uma conclusão exige ver a
conclusão: pontuação, parecer, versão que governou e instante.

**FR-094** — Reabrir **não destrói o que havia sido concluído**. Depois de uma reabertura, e de
quantas vierem, continua sendo possível responder o que aquela pessoa havia efetivamente concluído
antes de cada uma, sob qual versão e em que instante. É a mesma exigência de reprodutibilidade que
FR-071 atende para a versão normativa; a forma concreta — revisão, histórico do agregado, registro
da conclusão anterior — é do `/plan`.

**FR-037** — Concluir uma Avaliação **não** produz resultado, nem torna a inscrição apta ou
inapta. Isso é da 013.

**FR-038** — Cada gravação e cada conclusão são auditáveis.

**FR-077** — O período previsto da Etapa é **informado, e não aplicado**: avaliar antes ou depois
dele não é recusado pelo sistema. Três razões, e nenhuma é conveniência. A Etapa pode não
referenciar Evento algum, e uma proibição que valesse para algumas Etapas conforme um vínculo
opcional seria invariante nascida de acidente. O Edital publica **datas previstas**, e não a
proibição de trabalhar fora delas — transformar uma na outra é escrever regra normativa que ninguém
publicou, exatamente o que o domínio já recusa fazer ao conferir a forma do conteúdo. E o efeito de
avaliar fora do prazo é administrativo, não técnico.

**FR-078** — Em contrapartida, o instante real de cada gravação e de cada conclusão é registrado, e
a Mesa mostra o período previsto da Etapa. A divergência fica demonstrável, que é o que a
instituição precisa — e não um bloqueio que a impediria de concluir um trabalho atrasado por um dia.

**FR-095** — Concluir fora do período informado produz **aviso perceptível antes da conclusão**, e
não depois. Não informar seria o extremo oposto do bloqueio: o sistema conhecendo a divergência e
escondendo-a de quem responde por ela. O aviso não impede concluir, e o instante gravado é o real.

---

## 15. US5 — Impedimento

**Prioridade: P2**

Como presidente, quero registrar que uma pessoa não pode avaliar determinada inscrição.

**FR-039** — A presidência pode registrar impedimento entre avaliador e inscrição, com motivo.

**FR-099** — O impedimento acompanha a **pessoa**, pela identidade institucional estável, e não o
vínculo de comissão. Quem é impedido de avaliar uma inscrição não deixa de ser por ter saído da
comissão e voltado: se o impedimento morresse com o vínculo, remover e readicionar seria o caminho
para contorná-lo, e ele nomeia justamente as razões que não mudam por reorganização administrativa.

É a mesma identidade de FR-074, e pelo mesmo motivo. A Atribuição continua ancorada no vínculo
(D-004): ela é trabalho distribuído sob uma composição de comissão, e não um fato sobre a pessoa.

**FR-040** — Impedimento bloqueia a **atribuição nova**, e a recusa nomeia o motivo registrado.

**FR-041** — A confirmação do impedimento **declara o alcance antes do ato**: quantas Atribuições
ativas serão inativadas e quantas delas têm avaliação concluída. Retirar trabalho de alguém não
pode ser efeito colateral silencioso de registrar um motivo, e a declaração é da tela — um número
que só existe no comando não é aviso.

Registrado sobre uma Atribuição **ativa**, o impedimento a inativa no mesmo ato, que é da
presidência, tem motivo e é auditado. Disso decorre, por FR-004, tudo o mais: o acesso é revogado
imediatamente, a Avaliação já registrada não é apagada, e o rascunho que houvesse deixa de ser lido
por qualquer um (FR-075). O ato declara, antes de ser confirmado, quantas Atribuições ativas ele
inativará — retirar trabalho de alguém não pode ser efeito colateral silencioso de registrar um
motivo.

**FR-079** — A Avaliação **concluída** antes do impedimento é **preservada e tornada inelegível**,
nos dois sentidos exatos de FR-075: ela não é apagada nem alterada, continua consultável com o ato,
o autor e o motivo ao lado (FR-091, FR-093), e deixa de integrar o conjunto que a 013 consome — o
que libera a vaga que ocupava (FR-090).

O que a 012 **não** faz é pronunciar-se sobre o mérito dela: não afirma que a nota estava errada,
não a corrige, não a recalcula e não a substitui por outra. Ela apenas registra que quem a produziu
estava impedido, e que por isso aquela avaliação não pode ser uma das previstas. Julgar o conteúdo é
da 013 — tirar do conjunto quem não podia estar nele é desta.

**FR-080** — A autorização continua tendo **duas** condições, e o impedimento não vira uma terceira.
Ele age removendo a Atribuição, não somando uma verificação por linha — que é o que FR-048 proíbe.
Um impedimento sem Atribuição ativa correspondente não tem o que revogar, e um com ela já a
revogou.

**FR-042** — A 012 não infere impedimento por CPF, sobrenome ou coincidência de dado. Declarar é
ato de quem sabe.

---

## 16. Autorização, em uma frase

```text
Pode abrir esta inscrição nesta Etapa?
        ↓
pode_atuar_na_etapa (011)
        ↓
Atribuição ativa desta pessoa para esta inscrição
        ↓
sim
```

São **duas** condições, e não três: o impedimento não entra na cadeia porque age antes dela,
inativando a Atribuição no ato em que é registrado (FR-041, FR-080). Somá-lo aqui seria acrescentar
uma verificação por linha a toda listagem da feature, que é o que FR-048 proíbe.

**FR-043** — As duas condições são verificadas no servidor, em toda rota, sobre o objeto pedido.

**FR-044** — Recusa responde como recurso inexistente, pela convenção já vigente.

**FR-045** — Alterar identificador de inscrição na URL não alcança inscrição não atribuída.

**FR-046** — Perder a alocação à Etapa revoga o acesso a todas as inscrições daquela Etapa, mesmo
com Atribuição ativa — e a revogação é a conjunção sendo avaliada, não um campo sendo atualizado
(D-004).

---

## 17. Escala

**FR-047** — Nenhuma tela pode exigir um envio por atribuição.

**FR-048** — Nenhuma listagem pode verificar autorização por linha.

**FR-049** — As telas de distribuição, de Mesa, de **conclusões preservadas** e de **avaliações
inelegíveis** devem ser paginadas e filtráveis, e o filtro da distribuição responde por **cobertura
e por progresso**: “quais ainda não têm avaliador” e “quais ainda não têm avaliação concluída” são
perguntas diferentes, e a segunda — a da véspera do resultado — não se respondia. A de conclusões é o maior acervo da feature — uma
linha por conclusão, e mais uma a cada reabertura —, e é justamente a que se abre para responder a
recurso. A de inelegíveis é curta no uso corrente, e deixar de paginá-la por isso seria apostar no
uso: trocar a banca de uma Etapa a torna longa de uma vez.

**FR-050** — A trilha desta feature será volumosa por natureza — duas mil atribuições e cada
documento aberto. Ela precisa nascer filtrável por inscrição, por avaliador e por operação.

Cada linha diz também **a que inscrição o ato se refere**, pelo protocolo, e a quem: a pergunta que
traz alguém à trilha é quase sempre sobre uma inscrição, e "conclusão de avaliação, por joao" sem
dizer de qual não responde a ela.

E onde se **digita** uma inscrição — o filtro da trilha, o das conclusões, o formulário do
impedimento — o **protocolo** vale, porque é o que toda tela mostra e o que o candidato tem em mãos.
Exigir o identificador interno no único campo que se digita obrigava a procurá-lo em outro lugar, e
um erro de digitação virava erro de servidor.

E o **impedimento é da pessoa e da inscrição, e não da Etapa**: na trilha de uma Etapa ele entra
quando a pessoa está ou esteve alocada nela, que é onde ele decide alguma coisa. Sem esse critério
ele apareceria em toda Etapa do Edital, inclusive naquelas em que ela nunca trabalhou.

**FR-069** — Nenhum ato de alocação, remoção de alocação ou remoção de membro pode disparar
escrita proporcional ao número de atribuições da pessoa.

---

## 18. Concorrência, repetição e idempotência

A Constituição exige que a especificação trate os riscos de concorrência com controles
proporcionais — perda de atualização, duplicidade, julgamento conflitante e uso de dado obsoleto.
Nesta feature os quatro são concretos: duas mil atribuições distribuídas em lotes reenviáveis, e
avaliações gravadas por dezenas de pessoas ao mesmo tempo enquanto a presidência reabre e
redistribui. Nenhum controle novo é necessário — os três que o projeto já usa cobrem tudo, e a
spec diz qual resultado cada um deve produzir.

**FR-081** — Toda gravação e toda conclusão de Avaliação carregam a revisão esperada, e revisão
obsoleta é recusada pela resposta que o projeto já usa. Duas abas do mesmo avaliador não se
sobrescrevem em silêncio — **inclusive na primeira gravação**, que é quando a Avaliação nasce: duas
primeiras gravações simultâneas produzem uma gravação e uma recusa por revisão, e nunca um erro
interno por colisão de chave.

**FR-082** — Conclusão sobre Avaliação que a presidência reabriu no intervalo é recusada pela mesma
regra, e a tela diz que a avaliação foi reaberta. O avaliador nunca conclui sobre um estado que
deixou de existir enquanto ele escrevia.

**FR-083** — Reabrir Avaliação que não está concluída é transição inválida, e é recusada.

**FR-105** — A chave de idempotência cobre **o conteúdo inteiro do ato**, e o motivo faz parte
dele. Num ato cujo motivo é a sua própria justificativa — impedir, reabrir, anular —, tratar
motivos diferentes como repetição registraria um ato que ninguém pediu.

**FR-106** — **O alcance confirmado é conferido contra o alcance executado.** A declaração de
FR-041 é de um passo, e o ato é de outro; entre os dois a realidade continua andando — o avaliador
conclui a avaliação que estava pendente, uma atribuição nova aparece. Sem conferência, quem confirma
"nenhuma concluída" torna uma conclusão inelegível sem ter sido avisado: o efeito que FR-092 impede,
obtido por corrida em vez de por decisão.

A conferência é **sob a mesma trava** que o ato usa, contra o conjunto que ele realmente alcançará,
e compara a identidade do conjunto — não o seu tamanho: uma atribuição removida e outra criada
mantêm a contagem e mudam o alcance. Divergiu, o ato não acontece e a confirmação é refeita sobre o
que existe agora.

E o ato **sem alcance declarado não acontece**: um envio que não traga a declaração volta ao passo
da confirmação. Aceitá-lo deixaria a garantia desligável por quem monta o formulário, que é a mesma
falha um nível acima.

**FR-084** — **Os quatro atos da presidência são idempotentes por chave** — distribuir em lote,
remover Atribuição, registrar impedimento e reabrir. Repetir qualquer um deles — por timeout, duplo
clique ou reenvio — devolve o desfecho original, sem criar registro novo e **sem gravar evento de
auditoria novo**. Chave repetida com conteúdo diferente é conflito, e responde como tal.

A gravação e a conclusão da Avaliação ficam de fora, e não por esquecimento: são linha própria do
avaliador, protegidas pela revisão esperada (FR-081), e ali reenvio com revisão obsoleta é recusa —
não repetição a ser absorvida.

**FR-097** — O resultado do lote é **declarado, e não inferido**: quantas foram atribuídas, quantas
recusadas e o motivo de cada recusa, nomeando a linha. Sucesso parcial que não se anuncia vira
surpresa administrativa, e quem distribuiu precisa saber o que ficou de fora sem conferir mil
linhas.

**FR-085** — O lote é uma transação, e a recusa tem dois tamanhos, porque as causas têm dois
tamanhos:

- **regra sobre uma linha** — impedimento registrado, teto do FR-065 atingido, atribuição que já
  existia — não derruba o lote: a linha é nomeada no resultado e o restante é distribuído. Recusar
  quinhentas por causa de uma seria punir o caminho normal, que é o que a 011 já decidiu para a
  alocação em lote;
- **erro sobre o pedido** — Etapa inexistente, avaliador sem alocação ativa, inscrição de outro
  Edital, inscrição não submetida — desfaz o lote inteiro e nomeia a causa. Aqui o pedido está
  errado, e distribuir a parte válida dele seria adivinhar a intenção.

**FR-086** — **Os mesmos quatro atos** seguem o invólucro de comando da 011, e pela mesma razão:
bloquear o contêiner, **reavaliar a autorização depois do bloqueio** e reservar a idempotência
depois de autorizar. Quem perdeu a presidência entre a tela e a gravação não conclui o ato, e a
repetição não responde a quem já não pode. Isso vale tanto para distribuir quanto para remover,
impedir e reabrir — os três últimos alteram quem tem acesso a quê, e nenhum pode ser concluído sob
autorização que deixou de existir durante a transação.

**FR-087** — Duas conclusões simultâneas da mesma Avaliação: uma vence e a outra é recusada por
revisão obsoleta. Duas conclusões de avaliadores diferentes sobre a mesma inscrição não competem —
são Avaliações distintas, de Atribuições distintas, e nenhuma interfere na outra (EC-007).

**FR-088** — A validação da conclusão e a versão gravada em FR-071 são lidas **dentro da transação
que grava**, e não da tela que foi montada minutos antes. É o que impede que uma Retificação
consolidada no intervalo produza uma Avaliação validada contra regra que já não vigia.

**A forma entra nessa mesma leitura, e não numa segunda.** Forma, pontuação máxima e nota mínima
saem do conteúdo da versão lida uma vez (FR-096), e a forma gravada em FR-117 é aquela — não a que a
tela exibia. Uma Retificação que mudasse a forma entre a montagem e o envio faria o avaliador
concluir no instrumento antigo; a conclusão é recusada com a mesma frase de FR-073, e não gravada
sob a forma nova.

---

## 19. Auditoria

**FR-051** — Reutilizar a trilha existente, com a base de autorização, como a 011 fez.

**FR-052** — São atos auditáveis: atribuir, remover atribuição, abrir documento, gravar avaliação,
concluir, reabrir, registrar impedimento.

**FR-053** — O registro identifica ator, inscrição, Etapa, operação e instante.

**FR-054** — A trilha não guarda o conteúdo do parecer, nem a pontuação, **nem o sentido**: ela
guarda que o ato aconteceu. O sentido entra nessa lista pelo mesmo motivo que os outros dois — é o
conteúdo do juízo, e não o registro de que houve juízo. Sem isso, a trilha da forma decisória passaria
a guardar o deferimento, que é exatamente o que este requisito mantém fora dela. O conteúdo vive na
Avaliação, que é o registro do domínio.

**FR-070** — Como a trilha existente é adaptada a agregados sem estado e sem revisão é decisão do
`/plan`, e a 011 já resolveu o caso passando estado e revisão explicitamente. O que a spec proíbe é
o inverso: não acrescentar estado ou ciclo de vida a Atribuição, Avaliação ou Impedimento apenas
para satisfazer a forma do registrador.

---

## 20. Proteção de dados

A 012 é a primeira feature em que membro de comissão lê dado pessoal de candidato em volume.

**FR-055** — Acesso a documento e a dado pessoal exige Atribuição, e não apenas papel.

**FR-056** — Respostas com dado pessoal não são armazenáveis pelo navegador, pela mesma marcação
que a 009 já aplica.

**FR-057** — A retenção e o descarte do acervo continuam sendo gate de implantação, e a 012 os
torna mais urgentes — não os resolve.

**FR-058** — O gate de identidade institucional confiável, herdado da 011, é condição para abrir
dado real de candidato a membro de comissão. Esta é a feature em que ele deixa de ser teórico.

---

## 21. Out of Scope

### Da 013
Consolidação, média, quórum atingido, divergência entre avaliadores, desempate, classificação,
resultado preliminar e final, publicação de resultado.

### Recurso
Interposição, resposta da banca, reconsideração. A 012 apenas garante que o parecer exista para
que o recurso tenha contra o que ser respondido.

### Barema estruturado
Pontuação por critério, com itens e limites por item. Hoje o barema vive no texto publicado do
Edital e o avaliador registra o total. Estruturá-lo é conteúdo normativo novo, com tela própria de
elaboração, e merece spec própria — não um puxadinho desta.

### Avaliação cega
Anonimização do candidato para o avaliador. Muda o que a Mesa mostra e depende de política por
Edital; declarar aqui sem essa política produziria meia anonimização, que é pior que nenhuma.

### Distribuição automática
Ver §11.

### Retirada de inscrição
Ver D-006. A 012 não cria estado de desistência, cancelamento ou retirada.

### Comunicação
Aviso de nova atribuição, lembrete, cobrança de avaliação pendente.

---

## 22. Invariantes de não regressão

**FR-059** — Nada da 012 altera comissão, alocação ou o guard da 011. A correção de nome de D-003
é a única exceção admitida, e ela não altera domínio, dado, autorização nem comportamento.

**FR-060** — Nada da 012 altera inscrição, documento submetido ou comprovante.

**FR-061** — Fora o incremento do FR-007, nenhuma operação da 012 toca conteúdo publicado, versão,
hash ou documento materializado.

**FR-062** — A identidade do candidato continua sem conceder qualquer autorização institucional, e
vice-versa.

**FR-100** — **A Retificação continua se comportando exatamente como antes para conteúdo já na
versão vigente.** O "antes" é reancorado a cada incremento: para o primeiro ele significa *antes da
012*, e para o segundo, *antes da revisão de D-008* — o que a invariante protege é o comportamento
que vigia imediatamente antes da mudança, e não um estado congelado de agosto. O incremento do FR-007
obrigou a 012 a tocar o mecanismo de Retificação em mais de
um ponto — a leitura do conteúdo-base, a reaplicação dos atos, a projeção que o autor compõe e a
comparação da precondição —, e o alcance da última é toda Retificação, e não apenas as de base
anterior. FR-061 protege o conteúdo, a versão, o hash e o documento; este protege o **comportamento**.

Precondição, detecção de conflito, consolidação, verificação de efeito prático e materialização
produzem, para Edital inteiramente na versão vigente, o mesmo resultado que produziam antes desta
feature. É invariante demonstrável, e não intenção: sem ele, a feature que promete não quebrar o que
já existe não tem como provar que não quebrou.

**FR-124** — **O comportamento da forma pontuada é invariante de não regressão, e não apenas
preservado.** Toda Etapa hoje publicada é pontuada e toda Avaliação hoje concluída tem nota; nenhuma
delas pode mudar de comportamento por causa desta revisão. Gravar, validar, concluir, reabrir,
invalidar e auditar produzem, na forma pontuada, exatamente o que produziam antes de D-008.

**A demonstração é comportamental, e o critério precisa dizer isso com precisão.** "A suíte passa sem
alteração de asserção" seria um critério impossível, e afirmá-lo faria a spec cobrar o que ela mesma
torna falso: o incremento sobe a versão canônica, e todo teste que fixa o literal da versão **tem de
mudar**. O que a invariante exige é isto:

1. nenhuma asserção sobre **comportamento da forma pontuada** muda — pontuação validada, conclusão,
   reabertura, invalidação, autorização, concorrência e trilha;
2. as asserções que mudam são **apenas** as que fixam o literal da versão canônica ou a forma do
   conteúdo publicado, e são **enumeradas** na entrega, uma a uma, com o motivo;
3. a comparação é por **identidade de teste**, e não por contagem: todo teste que existia antes
   continua existindo e continua passando. A contagem total cresce, porque a revisão acrescenta
   testes, e exigir que ela não cresça seria exigir que a revisão não fosse testada.

---

## 23. Success Criteria

**SC-001** — Presidente distribui inscrições em lote entre quem está alocado à Etapa.
**SC-002** — Avaliador vê todas e somente as inscrições atribuídas a ele.
**SC-003** — Alocado sem atribuição alcança a Mesa e a encontra vazia, e não abre inscrição
alguma.
**SC-004** — Atribuído abre os documentos daquela inscrição, e de nenhuma outra.
**SC-005** — Toda abertura de documento fica registrada.
**SC-006** — Avaliação é gravada como rascunho e concluída em ato distinto, nas duas formas.
**SC-007** — Pontuação fora do que o Edital publicou é recusada, na Etapa que pontua.
**SC-008** — Avaliação concluída não é alterada pelo avaliador.
**SC-009** — Reabertura é ato da presidência, com motivo registrado.
**SC-010** — Remover a alocação da Etapa revoga o acesso às inscrições dela, sem escrever em
nenhuma Atribuição.
**SC-011** — Remover a atribuição preserva a Avaliação já registrada.
**SC-012** — Impedimento bloqueia atribuição e nomeia o motivo.
**SC-013** — A 012 não produz resultado, média nem situação de aprovado.
**SC-014** — Distribuir mil inscrições não exige mil interações.
**SC-015** — A Mesa com quinhentas atribuições responde sem verificação por linha.
**SC-016** — A Etapa publicada declara quantas avaliações, qual a pontuação máxima e qual a forma da
conclusão — com os dois rótulos, quando decisória —, e o documento materializado as mostra a quem lê
o Edital.
**SC-017** — A permissão da consulta administrativa da 009 não abre a Mesa, e a autorização da Mesa
não abre a consulta administrativa.
**SC-018** — A Avaliação diz sob qual Versão Consolidada foi concluída, e a regra vigente à época é
reproduzível a partir dela.
**SC-019** — Atribuição além do número que a Etapa publicou é recusada, e a recusa nomeia o número.
**SC-020** — Impedimento sobre atribuição ativa revoga o acesso no mesmo ato, e a avaliação já
concluída permanece.
**SC-021** — Repetir o mesmo lote de distribuição não cria atribuição nem evento de auditoria novo.
**SC-022** — Conclusão sobre avaliação reaberta no intervalo é recusada, e o avaliador é informado.
**SC-023** — Nota abaixo do mínimo é gravada e concluída, com parecer obrigatório.
**SC-032** — Sentido desfavorável é gravado e concluído, com parecer obrigatório, independentemente do caráter da Etapa.
**SC-024** — Retificação consolidada entre a última gravação e a conclusão é anunciada ao avaliador
antes de ele concluir, e a versão contra a qual ele é validado é a que fica gravada.
**SC-025** — Remover atribuição pela via comum não invalida Avaliação concluída: a operação é
recusada e nomeia o ato que teria esse efeito.
**SC-026** — Avaliação invalidada permanece consultável pela presidência e pela auditoria, com o ato,
o autor e o motivo que a invalidaram.
**SC-027** — Avaliação invalidada libera a vaga que ocupava, e uma substituta pode ser distribuída.
**SC-028** — Depois de uma reabertura, continua sendo possível responder o que havia sido concluído
antes dela.
**SC-029** — Edital publicado antes do incremento continua retificável, e a Publicação original não
é alterada.
**SC-030** — O lote declara quantas atribuiu, quantas recusou e o motivo de cada recusa.
**SC-031** — Conclusão fora do período informado avisa antes, registra o instante real e não
bloqueia.
**SC-033** — Etapa decisória conclui sem pontuação, e a conclusão com pontuação é recusada — pelo
domínio e pelo banco.
**SC-034** — Etapa pontuada conclui sem sentido, e a conclusão com sentido é recusada — pelo domínio
e pelo banco.
**SC-035** — A Mesa apresenta o instrumento da forma publicada, e o envio do campo da outra forma é
recusado no canal HTTP real.
**SC-036** — A conclusão diz sob qual forma foi concluída, e a Retificação que muda a forma da Etapa
depois não altera o que ela afirma.
**SC-037** — Edital publicado na versão canônica 5 continua legível e retificável depois do salto
para 6, e a ausência da forma é lida como pontuada.
**SC-038** — A forma e os dois rótulos são alcançáveis pela Retificação no canal institucional
suportado, junto com os demais campos normativos da Etapa.
**SC-039** — Nenhum comportamento da forma pontuada muda: todo teste que existia antes da revisão
continua existindo e passando, e as únicas asserções alteradas são as que fixam o literal da versão
canônica, enumeradas uma a uma.

---

## 24. Edge cases

**EC-001** — Inscrição sem avaliador suficiente na véspera do prazo: visível na organização.

**EC-002** — Avaliador removido da comissão com avaliações concluídas: a autoria permanece.

**EC-003** — Avaliador removido da Etapa com atribuições pendentes: acesso revogado, atribuições
visíveis como órfãs para redistribuição, e devolver a alocação restaura o acesso às mesmas
atribuições (D-004).

**EC-004** — Retificação que remove a Etapa com avaliações registradas: as Atribuições daquela
Etapa deixam de conceder acesso pela mesma regra que já vale para a alocação órfã, e as Avaliações
permanecem como registro do que foi afirmado.

**EC-005** — Retificação que altera a pontuação máxima depois de avaliações concluídas: a Avaliação
concluída aponta para a Versão Consolidada sob a qual foi concluída (FR-071), de modo que a regra
da época é reproduzível; a 012 não a reescreve, não a revalida e não a invalida.

**EC-021** — Retificação que altera a **forma** da Etapa depois de avaliações concluídas: é de outra
espécie que a EC-005, porque não muda um limite e sim o que uma conclusão significa. A resposta da
012 é a mesma, e por isso ela funciona: a conclusão guarda a forma sob a qual foi feita (FR-117) e
continua interpretável, e a 012 não a reescreve nem a invalida. **A consequência é da 013**, que
recusa fundamentar Resultado em conclusão cuja forma divergiu da vigente — pelo mesmo mecanismo com
que já trata nota mínima e pontuação máxima divergentes.

**EC-022** — Retificação que muda a forma entre a montagem da Mesa e o envio da conclusão: recusada
por FR-073 e FR-088, com a mesma frase do aviso de mudança de versão. O avaliador não conclui no
instrumento antigo, e nada é gravado sob a forma nova sem que ele a reconheça.

**EC-006** — Candidato que retira a inscrição depois de distribuída: não alcançável hoje (D-006).

**EC-007** — Dois avaliadores concluem a mesma inscrição ao mesmo tempo: nenhum interfere no outro,
porque são duas Avaliações de duas Atribuições.

**EC-008** — Documento cuja verificação de integridade falha no momento da avaliação: recusa
registrada, como já é na consulta administrativa.

**EC-009** — Etapa que declara duas avaliações e só tem um alocado: a organização mostra a
diferença; nada bloqueia (D-007).

**EC-010** — Reabertura de avaliação já usada pela 013 — precisa ser impossível ou explicitamente
tratada quando a 013 existir. A 012 registra a pendência e não constrói o mecanismo.

**EC-011** — Inscrição atribuída cuja Etapa não está na Versão Consolidada vigente: não concede
acesso, pela mesma regra da alocação órfã.

**EC-012** — Impedimento registrado sobre pessoa que já concluiu a avaliação: a conclusão
permanece, e o impedimento fica visível junto dela (FR-079).

**EC-013** — Avaliador **removido da comissão** e readicionado: o vínculo novo é outro, e as
Atribuições do vínculo antigo não revivem — elas precisam ser redistribuídas. É a assimetria que
D-004 produz de propósito: perder a **alocação** é reversível e devolvê-la restaura o acesso;
perder o **vínculo de comissão** não é, porque readicionar alguém é constituir a comissão de novo.
A autoria do que ele concluiu permanece (EC-002).

**EC-014** — Retificação consolidada entre a última gravação e a conclusão: o avaliador é avisado
antes de concluir, e o que ele conclui é validado contra a versão que passará a constar da
Avaliação (FR-073).

**EC-015** — Lote de distribuição reenviado por timeout: devolve o desfecho original, sem
atribuição nem evento novo (FR-084).

**EC-016** — Duas abas do mesmo avaliador gravando a mesma Avaliação: a segunda é recusada por
revisão obsoleta, e nada é sobrescrito em silêncio (FR-081).

**EC-017** — Avaliação em rascunho cuja Atribuição foi removida e depois recriada: a Atribuição nova
nasce vazia, e o rascunho antigo não é retomado por ninguém (FR-075).

**EC-018** — Presidência tenta retirar, pela via comum de redistribuição, a Atribuição de quem já
concluiu: recusado, e a recusa nomeia os atos que teriam esse efeito e o que cada um exige (FR-092).

**EC-019** — Retificação sobre Edital publicado antes do incremento: a Publicação original permanece
intocada, o conteúdo-base é interpretado pela leitura de FR-009 e FR-066, e a Versão Consolidada
nasce na versão vigente (FR-098).

**EC-020** — Inscrição cuja única avaliação foi invalidada às vésperas do prazo: a vaga é liberada e
a inscrição volta a aparecer como carente de avaliador (EC-001, FR-090).

---

## 25. Ordem de implementação sugerida

| Slice | Entrega observável |
|---|---|
| **S1** | O primeiro incremento canônico: quantas avaliações e pontuação máxima, publicadas e no documento |
| **S2** | Distribuição manual em lote, com a organização do trabalho e a trilha |
| **S3** | A Mesa: lista do avaliador, filtro e contagem |
| **S4** | A inscrição aberta: documentos mediados e auditados, sob a autorização composta |
| **S5** | A avaliação: rascunho, pontuação, parecer, conclusão |
| **S7** | O segundo incremento e a forma decisória: forma e rótulos publicados, conclusão por forma, dois instrumentos na Mesa |
| **S6** | Impedimento, reabertura, órfãs, escala e acessibilidade |

A primeira vertical significativa: **presidente distribui → avaliador abre a Mesa → abre a
inscrição → registra e conclui → quem não recebeu aquela inscrição não a alcança.**

---

## 26. Diretriz para o `/speckit-plan`

> A reconciliação com o repositório já foi feita e está na seção 5. O `/plan` parte dela e não a
> refaz; o que ele decide é forma, não decisão.
>
> Componha com `pode_atuar_na_etapa`; não o reescreva. Use `etapas_autorizadas` em toda listagem —
> uma vez, nunca por linha. Um teste deve exigir que as duas formas nunca divirjam, como o da 011.
>
> A Atribuição é derivada da alocação, e não paralela a ela. A revogação é computada, e nenhum ato
> da 011 pode disparar escrita proporcional ao número de atribuições.
>
> **Dois** incrementos canônicos, em momentos distintos, e as propriedades de cada um entrando
> juntas — pela razão que o próprio `SCHEMA_VERSION` registra nos incrementos anteriores. O segundo é
> de D-008, e a leitura da ausência que ele exige vive num lugar só, tanto no consumo quanto na
> elevação da Retificação.
>
> A forma da conclusão é lida da versão consolidada dentro da transação que conclui, e gravada na
> linha. É a única cópia que a Avaliação faz, e ela existe porque a verificação do banco precisa ser
> local — não porque duplicar seja conveniente.
>
> Reutilize a mecânica de arquivo da 009 inteira: `copia_verificada`, entrega mediada, registro da
> consulta, registro da divergência, resposta não armazenável. Não reutilize a permissão dela.
>
> Nenhuma tela pode custar um envio por atribuição, e nenhuma listagem pode custar uma verificação
> de autorização por linha. A escala é de mil candidatos, e ela não é hipótese.
>
> Não implemente média, quórum, divergência, desempate nem resultado.
>
> Não implemente distribuição automática.
>
> Reutilize os três controles de concorrência que já existem — revisão comparada na gravação,
> reserva de idempotência por chave e bloqueio do contêiner com reavaliação da autorização depois
> dele. Nenhum deles precisa ser inventado, e a seção 18 diz que resultado cada um deve produzir.
>
> A Avaliação aponta para a Versão Consolidada; ela não copia limite nenhum, e a versão validada é
> a versão gravada.
>
> Confronte **cada** incremento canônico com D-002 antes de escrever migration: a Publicação original é
> imutável e continua sendo o que foi publicado, e a Retificação sobre conteúdo da versão anterior
> precisa continuar possível. Se o mecanismo atual não comportar isso sem violar imutabilidade,
> proveniência ou hash, a decisão volta à spec — não vira precondição de implantação.
>
> Quando houver conflito entre generalizar um motor de avaliação e implementar o estritamente
> necessário a esta Etapa e a este Edital, prefira o estreito.

---

## 27. Gate para a SPEC 013

> **Registro histórico, e não portão.** A 013 foi especificada e implementada sob a redação anterior
> deste gate, e passou por ele. A revisão de D-008 o reescreve para que ele continue dizendo a
> verdade sobre o contrato — não para liberar nada. A contraparte de D-008 na `specs/013` é o que
> mantém as duas features coerentes daqui em diante.

A 012 libera a 013 quando estiver demonstrado que:

1. existe Atribuição inequívoca de inscrição a avaliador;
2. existe Avaliação com autoria, parecer, instante de conclusão e **conclusão válida segundo a
   forma que a Etapa publicou** — pontuação na forma pontuada, sentido na forma decisória, e a forma
   gravada na própria conclusão;
3. cada Avaliação aponta para a Versão Consolidada sob a qual foi concluída, de modo que a regra
   vigente à época é reproduzível sem depender da regra atual;
4. está definido, sem ambiguidade, **qual** Avaliação a 013 deve considerar: a que está sob
   Atribuição ativa, e há no máximo uma concluída por pessoa, inscrição e Etapa;
5. o conjunto de avaliações elegíveis é inequívoco, e tirar uma dele é ato nomeado, com autor e
   motivo — nunca efeito colateral de reorganizar o trabalho;
6. a autorização composta funciona e é demonstrável pela recusa;
7. a quantidade de avaliações por inscrição é conhecida e publicada, o excedente é recusado e o
   déficit é visível e contável; e a forma da conclusão é conhecida e publicada, legível tanto da
   Etapa vigente quanto da conclusão histórica, sem depender de a regra atual ainda ser a mesma;
8. avaliações concluídas são imutáveis, reabertura é ato registrado e o que havia sido concluído
   antes dela continua reproduzível;
9. nada disso produziu resultado.

A partir daí a 013 pode assumir como contrato:

> **as avaliações de uma inscrição existem, têm autoria e são confiáveis; o que falta é
> transformá-las em consequência.**
