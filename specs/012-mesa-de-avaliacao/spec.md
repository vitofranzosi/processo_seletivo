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
abrindo a documentação como instrumento de trabalho, registrando pontuação e parecer, e
concluindo.

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

---

## 6. Problema

A 011 organizou o trabalho e parou antes de executá-lo. Hoje, terminada a alocação, o sistema sabe
que quarenta pessoas podem atuar na Análise documental — e não sabe mais nada. A operação real
recomeça fora dele:

- quem avalia quais candidatos vira planilha;
- a documentação é baixada em lote e circula por pasta compartilhada;
- a pontuação é anotada em papel ou em documento de texto;
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

A 012 registra o que **um** avaliador afirmou sobre **uma** inscrição. Média, quórum, divergência,
desempate e resultado são da 013. Antecipá-los aqui faria a nota de uma pessoa parecer decisão da
instituição.

### P-007 — O que o Edital publicou é o que vale

A pontuação máxima, o caráter eliminatório e a nota mínima vêm do conteúdo vigente, e não de
configuração de tela. Se a regra não está publicada, ela não pode ser aplicada — e é por isso que
a pontuação máxima precisou passar a ser publicada (D-001).

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

**FR-063** — A Atribuição espelha a forma da alocação, com `etapa_id` designando a Etapa do
conteúdo publicado e não a linha de elaboração (D-004, e 011 D-002).

### 8.2 Avaliação

```text
Avaliacao
- atribuição
- pontuação
- parecer
- estado: RASCUNHO | CONCLUIDA
- versão consolidada sob a qual foi concluída
- revisão
- concluída_em / concluída_por
```

> o que esta pessoa afirmou sobre esta inscrição, e sob qual regra.

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

**FR-008** — Esse é o **único** incremento canônico da 012, ele acontece **uma vez**, e as duas
propriedades entram juntas (D-001).

**FR-064** — O incremento sobe a versão canônica do snapshot e alcança a Etapa publicada, o
esquema que verifica sua forma, o caminho de elaboração e o documento materializado. **Nenhuma
outra coleção do conteúdo publicado muda.**

**FR-009** — Edital publicado antes do incremento continua **legível**, e a ausência da declaração
significa uma avaliação por inscrição.

**FR-098** — Edital publicado antes do incremento continua **retificável**. A Publicação original
não é alterada, e a Retificação que o alcança produz Versão Consolidada na versão vigente,
interpretando a ausência pela leitura de FR-009 e FR-066 (D-002). A elevação não tem autor e não é
apresentada como alteração normativa, porque não altera norma nenhuma.

**FR-010** — Alterar qualquer uma das duas declarações num Edital publicado é Retificação, com tudo
o que ela já exige.

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

**FR-066** — A pontuação máxima publicada é o limite superior da validação de FR-033. Etapa sem a
declaração — porque foi publicada antes do incremento — não admite pontuação acima do que a
persistência comporta, e a tela diz que o Edital não declarou limite, em vez de inventar um.

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

**FR-021** — Filtro por pendente e concluída, e contagem visível.

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

Como avaliador, quero registrar pontuação e parecer, salvar sem concluir, e concluir quando
terminar.

**FR-031** — A Avaliação nasce como rascunho e é gravada sem exigir conclusão.

**FR-103** — **O rascunho valida a forma; a conclusão valida a regra.** Salvar exige que a
pontuação seja um número que o registro comporte — finito, não negativo, na escala do conteúdo
publicado. Não exige a pontuação máxima do Edital: quem está no meio do trabalho pode gravar um
valor que ainda não decidiu, e cobrar a regra normativa ali obrigaria a concluir para descobrir se
o número passa. A máxima é cobrada no ato que tem efeito (FR-033).

Valor que não é número — infinito, indefinido, expoente que a coluna não comporta — é recusado nos
dois, com mensagem: forma impossível não pode virar erro interno.

**FR-032** — Concluir é ato explícito, distinto de salvar.

**FR-033** — A pontuação é validada contra o que o Edital publicou para aquela Etapa: a pontuação
máxima, a forma decimal do conteúdo publicado e a não-negatividade. **A nota mínima não recusa
pontuação nenhuma** — nota abaixo do mínimo é registro válido, é justamente o que o avaliador
precisa poder afirmar, e a consequência dela é da 013. O que a nota mínima produz aqui é uma coisa
só: torna o parecer obrigatório (FR-034).

**FR-034** — O parecer é texto livre. Ele é o que responde recurso, e por isso não pode ser
opcional quando a Etapa for eliminatória e a nota ficar abaixo do mínimo.

**FR-035** — Avaliação concluída é imutável para o avaliador, e a imutabilidade é garantida no
agregado, como a 009 fez com a inscrição enviada — e não apenas na tela que grava.

**FR-036** — Reabrir é ato da presidência, com motivo, registrado. Recurso e erro material existem;
o que não pode existir é reabertura silenciosa.

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

**FR-049** — As telas de distribuição, de Mesa e de **conclusões preservadas** devem ser paginadas
e filtráveis. A última é o maior acervo da feature — uma linha por conclusão, e mais uma a cada
reabertura —, e é justamente a tela que se abre para responder a recurso.

**FR-050** — A trilha desta feature será volumosa por natureza — duas mil atribuições e cada
documento aberto. Ela precisa nascer filtrável por inscrição, por avaliador e por operação.

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

**FR-088** — A validação da pontuação e a versão gravada em FR-071 são lidas **dentro da transação
que grava**, e não da tela que foi montada minutos antes. É o que impede que uma Retificação
consolidada no intervalo produza uma Avaliação validada contra regra que já não vigia.

---

## 19. Auditoria

**FR-051** — Reutilizar a trilha existente, com a base de autorização, como a 011 fez.

**FR-052** — São atos auditáveis: atribuir, remover atribuição, abrir documento, gravar avaliação,
concluir, reabrir, registrar impedimento.

**FR-053** — O registro identifica ator, inscrição, Etapa, operação e instante.

**FR-054** — A trilha não guarda o conteúdo do parecer nem a pontuação: ela guarda que o ato
aconteceu. O conteúdo vive na Avaliação, que é o registro do domínio.

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
versão vigente.** O incremento do FR-007 obrigou a 012 a tocar o mecanismo de Retificação em mais de
um ponto — a leitura do conteúdo-base, a reaplicação dos atos, a projeção que o autor compõe e a
comparação da precondição —, e o alcance da última é toda Retificação, e não apenas as de base
anterior. FR-061 protege o conteúdo, a versão, o hash e o documento; este protege o **comportamento**.

Precondição, detecção de conflito, consolidação, verificação de efeito prático e materialização
produzem, para Edital inteiramente na versão vigente, o mesmo resultado que produziam antes desta
feature. É invariante demonstrável, e não intenção: sem ele, a feature que promete não quebrar o que
já existe não tem como provar que não quebrou.

---

## 23. Success Criteria

**SC-001** — Presidente distribui inscrições em lote entre quem está alocado à Etapa.
**SC-002** — Avaliador vê todas e somente as inscrições atribuídas a ele.
**SC-003** — Alocado sem atribuição alcança a Mesa e a encontra vazia, e não abre inscrição
alguma.
**SC-004** — Atribuído abre os documentos daquela inscrição, e de nenhuma outra.
**SC-005** — Toda abertura de documento fica registrada.
**SC-006** — Avaliação é gravada como rascunho e concluída em ato distinto.
**SC-007** — Pontuação fora do que o Edital publicou é recusada.
**SC-008** — Avaliação concluída não é alterada pelo avaliador.
**SC-009** — Reabertura é ato da presidência, com motivo registrado.
**SC-010** — Remover a alocação da Etapa revoga o acesso às inscrições dela, sem escrever em
nenhuma Atribuição.
**SC-011** — Remover a atribuição preserva a Avaliação já registrada.
**SC-012** — Impedimento bloqueia atribuição e nomeia o motivo.
**SC-013** — A 012 não produz resultado, média nem situação de aprovado.
**SC-014** — Distribuir mil inscrições não exige mil interações.
**SC-015** — A Mesa com quinhentas atribuições responde sem verificação por linha.
**SC-016** — A Etapa publicada declara quantas avaliações e qual a pontuação máxima, e o documento
materializado as mostra a quem lê o Edital.
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
| **S1** | O incremento canônico: quantas avaliações e pontuação máxima, publicadas e no documento |
| **S2** | Distribuição manual em lote, com a organização do trabalho e a trilha |
| **S3** | A Mesa: lista do avaliador, filtro e contagem |
| **S4** | A inscrição aberta: documentos mediados e auditados, sob a autorização composta |
| **S5** | A avaliação: rascunho, pontuação, parecer, conclusão |
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
> Um incremento canônico, e só um — carregando as duas propriedades juntas, pela razão que o
> próprio `SCHEMA_VERSION` registra nos incrementos anteriores.
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
> Confronte o incremento canônico com D-002 antes de escrever migration: a Publicação original é
> imutável e continua sendo o que foi publicado, e a Retificação sobre conteúdo da versão anterior
> precisa continuar possível. Se o mecanismo atual não comportar isso sem violar imutabilidade,
> proveniência ou hash, a decisão volta à spec — não vira precondição de implantação.
>
> Quando houver conflito entre generalizar um motor de avaliação e implementar o estritamente
> necessário a esta Etapa e a este Edital, prefira o estreito.

---

## 27. Gate para a SPEC 013

A 012 libera a 013 quando estiver demonstrado que:

1. existe Atribuição inequívoca de inscrição a avaliador;
2. existe Avaliação com autoria, pontuação, parecer e instante de conclusão;
3. cada Avaliação aponta para a Versão Consolidada sob a qual foi concluída, de modo que a regra
   vigente à época é reproduzível sem depender da regra atual;
4. está definido, sem ambiguidade, **qual** Avaliação a 013 deve considerar: a que está sob
   Atribuição ativa, e há no máximo uma concluída por pessoa, inscrição e Etapa;
5. o conjunto de avaliações elegíveis é inequívoco, e tirar uma dele é ato nomeado, com autor e
   motivo — nunca efeito colateral de reorganizar o trabalho;
6. a autorização composta funciona e é demonstrável pela recusa;
7. a quantidade de avaliações por inscrição é conhecida e publicada, o excedente é recusado e o
   déficit é visível e contável;
8. avaliações concluídas são imutáveis, reabertura é ato registrado e o que havia sido concluído
   antes dela continua reproduzível;
9. nada disso produziu resultado.

A partir daí a 013 pode assumir como contrato:

> **as avaliações de uma inscrição existem, têm autoria e são confiáveis; o que falta é
> transformá-las em consequência.**
