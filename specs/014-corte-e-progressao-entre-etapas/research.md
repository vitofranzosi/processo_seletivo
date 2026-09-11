# Pesquisa — 014 · Corte e Progressão entre Etapas

Fase 0 do plano. As dez decisões da §3 da spec chegam **fechadas** — duas delas pelo usuário — e não
são reabertas aqui. O que esta pesquisa faz é dar forma a elas contra o código que já existe, e dizer
o custo onde ele existe.

Duas coisas a spec deixou para o plano: **os nomes** e **qual degrau de schema** esta feature ocupa.
Ficam na `R-001` e na `R-004`.

Três coisas esta pesquisa **encontrou**, e que ninguém tinha pedido:

- a `R-005` encontrou um **ciclo de importação latente**: `classificacao/application/calculo.py` já
  importa `resultados/application/prontidao.py`, e é exatamente a prontidão que precisa passar a ler
  o corte. O caminho existe e é estreito;
- a `R-006` encontrou que a spec diz "o marco que antecede uma Etapa" e que **nada no domínio impede
  dois marcos de anteceder a mesma** — a pergunta não tinha resposta, e agora tem;
- a `R-008` encontrou que o empate que atravessa o corte **já é legível na ordem emitida** sem campo
  novo: posição compartilhada é o que `PosicaoNaOrdem` grava, e `empate_residual` diz se ele
  sobreviveu aos critérios publicados.

**Revisão cruzada de 11/09/2026.** Uma segunda leitura dos três artefatos encontrou três
incompatibilidades de domínio que a análise anterior não pegou, e o usuário fechou as quatro decisões
que elas exigiam (`D-011` a `D-014` da spec). A `R-003`, a `R-006`, a `R-009` e a `R-010` estão
reescritas por causa disso, e o que elas diziam antes está dito onde foi corrigido — porque o erro
anterior é a razão de a redação atual ser o que é.

---

## R-001 · Os nomes

**Problema.** Chave em inglês no conteúdo publicado, vocabulário do domínio em português no código, e
permanência: a chave publicada não muda depois de publicada, porque mudá-la mudaria o endereço de
retificação de tudo o que já saiu.

**Decisão.**

| Onde | Nome |
|---|---|
| Objeto no marco publicado | `cutRule`, irmão de `appealWindow` e `drawMethod` |
| Campos publicados | `targetKind`, `targetCount`, `surplusCount`, `tieOutcome` |
| Campo no marco relacional | `MarcoClassificatorio.regra_de_corte` (`JSONField`) |
| Ato emitido | `Corte`, em `classificacao/models.py` |
| Linha do ato | `ItemDoCorte` |
| `related_name` | `ato.cortes`, `corte.itens` |
| Caminho de retificação | `/profiles/id=…/classificationMilestones/id=…/cutRule/targetCount` |

**Rationale.** *Corte* é a palavra que a operação usa e que a spec adotou; *faixa* é o intervalo, e
não vira entidade — é um par de números derivado dos itens. `cutRule` segue a forma dos dois objetos
que já moram no marco, e por isso não inventa gramática de retificação nenhuma: quem alcança
`appealWindow/durationDays` alcança `cutRule/targetCount` pelo mesmo caminho.

**Alternativas recusadas.** `progressionRule` diria mais do que a feature faz — a progressão é
consequência, e o que o Edital publica é o corte. `CorteDeProgressao` como nome do modelo repetiria
no identificador o que o módulo já diz.

---

## R-002 · A regra mora no marco, e não no Edital nem na Etapa

**Problema.** Três lugares eram plausíveis: a Etapa que recebe os progredidos, o Edital, ou o marco
que produz a ordem.

**Decisão.** No **marco**, como `appealWindow` e `drawMethod`.

**Rationale.** O corte é uma leitura da ordem, e a ordem é do marco. Marcos diferentes cortam
diferente no mesmo Edital — o 14/2026 tem sete Perfis, e nada obriga os sete a cortarem igual. Na
Etapa a regra ficaria longe do que ela lê e não saberia de qual ordem falar; no Edital, ela não
saberia de qual Perfil. E a `FR-184` exige que alterá-la seja Retificação: os dois objetos vizinhos
do marco já estão nessa gramática, e a `EtapaAvaliacao` é do Edital e não do Perfil — declará-la lá
obrigaria a inventar a dimensão de Perfil que a Etapa ainda não tem.

---

## R-003 · A forma publicada do `cutRule`

**Decisão.**

```json
"cutRule": {
  "targetKind": "FIXED" | "FROM_VACANCY_TABLE",
  "targetCount": 10,
  "surplusCount": 0,
  "tieOutcome": "ADMITS_SURPLUS" | "STRICT",
  "governedStage": "<uuid da Etapa>" | "NONE",
  "continuation": "ALLOWED" | "NONE"
}
```

| Campo | Regra |
|---|---|
| `targetKind` | obrigatório quando `cutRule` existe |
| `targetCount` | inteiro ≥ 0 em `FIXED`; **sempre `null`** em `FROM_VACANCY_TABLE` |
| `surplusCount` | inteiro ≥ 0, **sempre emitido**, inclusive `0` |
| `tieOutcome` | obrigatório; a ausência impede a publicação (`FR-182`) |
| `governedStage` | identidade da Etapa, ou a palavra `NONE`; a ausência impede a publicação (`FR-224`) |
| `continuation` | `ALLOWED` ou `NONE`; a ausência impede a publicação (`FR-226`) |

**`cutRule: null` significa marco que não corta**, que é o que todo Edital publicado hoje afirma.

**A forma publicada é normalizada, e isso não é estética.** A obsolescência compara o `cutRule` que o
corte congelou com o da versão vigente (`R-011`). Duas regras semanticamente idênticas gravadas com
bytes diferentes — uma omitindo `surplusCount`, outra escrevendo `0`; uma com `targetCount: null`,
outra sem a chave — fariam a comparação acusar **obsolescência falsa**, e a operação emitiria geração
nova para corrigir uma diferença que não existe. Por isso: `surplusCount` sempre presente, e
`targetCount` com uma grafia só em cada espécie.

**`governedStage` carrega a ausência como palavra, e não como `null`.** A `D-012` exige que a ausência
seja **declarada**, e `null` é indistinguível de "esqueci" em toda chave anulável do sistema. `NONE`
é afirmação; `null` seria silêncio, e silêncio é o que a decisão proíbe.

**Alternativa recusada.** Um `targetKind` implícito, deduzido de qual campo veio preenchido. Deduzir
faria `targetCount: 0` ser indistinguível de "derivado", e o zero é legítimo.

---

## R-004 · O degrau 13, e o que ele afirma

**Decisão.** `SCHEMA_VERSION` 12 → **13**, com `DEGRAUS_DE_MARCO[13] = {"cutRule": None}`.

**Rationale.** É degrau **de marco**, e a família existe: o 8 acrescentou `appealWindow` e o 10
acrescentou `drawMethod`, os dois com `None` significando *não declarado*. `None` é verdade sobre
todo Edital publicado antes: a capacidade não existia, e nenhum deles declarou regra de corte. Há
conversão sem invenção.

`None` e não `{}`: um dicionário vazio seria uma segunda grafia para a mesma ausência, e os dois
vizinhos do marco já fixaram `None` para isso.

**O degrau é um só.** A `D-009` fecha que a regra e o desfecho do empate entram na mesma elevação —
`tieOutcome` é campo de `cutRule`, e não objeto próprio, então não há o que separar.

---

## R-005 · Onde o corte emitido mora, e o ciclo de importação que ele quase cria

**Problema.** O corte é sobre o ato de ordenação, e quem precisa lê-lo é a **prontidão**, que mora em
`resultados`. Só que `classificacao/application/calculo.py:14` já importa
`resultados.application.prontidao`. Somar a direção inversa entre os dois módulos fecharia o ciclo.

**Achado.** O ciclo é entre **módulos**, não entre apps, e o caminho estreito existe:
`classificacao/models.py` importa `inscricoes`, `processos` e `publicacoes` — e **não** importa
`resultados`. Logo `prontidao.py` pode importar `classificacao.models` sem fechar nada.

**Decisão.** O `Corte` e o `ItemDoCorte` moram em `classificacao/models.py`, ao lado do
`AtoDeOrdenacao`, e a prontidão importa **apenas esse módulo**.

**A regra que precisa virar comentário no código, porque ela quebra em silêncio:**
`resultados/application/prontidao.py` MUST importar `classificacao.models`, e MUST NOT importar
`classificacao.application.*`. O primeiro `from processo_seletivo.classificacao.application import …`
escrito ali fecha o ciclo, e o erro aparece longe da causa — na primeira importação de qualquer um
dos dois, num arquivo sorteado.

**Alternativa recusada.** App próprio `cortes`. Ele não desfaz o ciclo (precisaria importar
`classificacao` de qualquer forma), acrescenta uma fronteira sem regra própria para defender, e
afasta o ato do `AtoDeOrdenacao`, que é o objeto que ele cita em toda leitura.

**Precedente que confirma o desenho.** `avaliacoes/application/distribuicao.py:209` e `:394` já
importam a prontidão **dentro da função**, e não no topo, por essa mesma razão. Onde o import de topo
não couber, é esse o recurso, e ele já está no repositório.

---

## R-006 · Qual Etapa o corte governa — declarada, e não inferida

**Problema.** A primeira redação derivava a Etapa governada: *"a que sucede a última Etapa que o marco
enumera"*. A revisão cruzada mostrou que a derivação não se sustenta, e a razão é mais forte do que a
colisão que esta questão originalmente tratava.

**O que a derivação não sabia.** `editais/domain/perfis.py:216` exige que **todo** marco enumere ao
menos uma Etapa — *"sem Etapa não há pontuação a combinar, e a ordem não sai"*. Num marco que ordena
por **sorteio**, porém, a ordem nasce da semente: a Etapa enumerada não entra em conta nenhuma, e
está ali para satisfazer a validação. O marco `SORTEIO` do `seed_demo.py:408` enumera *Análise de
títulos*, e a Etapa que um corte dali alimentaria é a *Análise documental*, que vem depois. A
derivação acerta por acidente, e erraria no dia em que alguém trocasse a Etapa enumerada por outra
igualmente irrelevante para aquele marco.

**Decisão (`D-012`).** A regra **declara** `governedStage`, por identidade estável, ou declara `NONE`.
Nada é inferido. A publicação recusa a ausência (`FR-224`) e a Etapa inexistente na versão
(`FR-225`).

**E a guarda contra Etapa errada é de circularidade, não de ordem.** A primeira redação desta
decisão dizia que a Etapa governada precisa "suceder a ordem do marco" — e isso era a derivação
entrando de novo pela janela que a `D-012` fechou. Pior: tornava o **77/2026 impublicável**. Naquele
Edital não existe Etapa avaliada antes do sorteio; a única é a análise documental, que é a que o
marco **tem de enumerar** — o domínio exige ao menos uma — e é a que o corte governa.

O que a norma de fato proíbe é o **laço**, e só ele existe em marco computado:

| Marco | Etapa governada entre as que ele enumera | Por quê |
|---|---|---|
| computado a partir de Etapas | **impede a publicação** (`FR-229`) | o universo da ordem passaria a depender do corte que ela mesma produz |
| constituído por sorteio | **legítimo, e é o caso normal** | a ordem vem da relação de habilitados, não de Etapa nenhuma — `_estado_do_marco_que_sorteia` devolve `proposta: None` |

**A colisão que esta questão tratava desaparece junto.** Dois marcos com regra de corte governando a
mesma Etapa continua sendo achado impeditivo de publicação, nomeando os dois marcos — e agora a
comparação é entre duas declarações, e não entre duas deduções.

**E o marco terminal continua existindo**, declarado: `governedStage: "NONE"`, corte legítimo e sem
efeito de participação.

*O que **não** é caso de marco terminal é o corte de suplentes.* A redação anterior dizia que sim, e
errava: no 77, no 57 e no 28 os suplentes são a parte excedente da mesma faixa, no mesmo marco que
alimenta a análise documental (`D-011`).

---

## R-007 · Como a condição entra na progressão sem custar consulta por linha

**Problema.** A `FR-213` proíbe verificação por linha, e os orçamentos de consulta da `011`, da `012`
e da `015` são verificados por teste. A condição do corte não pode corroê-los.

**Decisão.** A mesma cirurgia que a progressão já usa: um `Exists` correlacionado somado dentro de
`restringir_a_participantes`, e uma pergunta de existência em `participa_da_etapa`.

```
consulta.filter(Exists(ItemDoCorte.objects.filter(
    inscricao_id=OuterRef(…), corte__in=<faixas da geração vigente que governa esta Etapa>,
    consequencia=ItemDoCorte.Consequencia.PROGREDIU)))
```

O conjunto das faixas vigentes é resolvido **uma vez por listagem**, junto do `_anteriores_e_gate`,
que já lê o conteúdo publicado uma vez e devolve o que a junção precisa. O custo somado é: uma
leitura a mais da regra no conteúdo que já estava em memória, e uma consulta para as faixas da
geração vigente — constante, não proporcional à população.

**E a regra governante vem da declaração**, nunca da ordem das Etapas: a prontidão procura a regra
publicada cujo `governedStage` é esta Etapa (`R-006`).

**A condição é dormente quando não há corte vigente** (`FR-214`), e é esse gate que garante a não
regressão: Edital sem regra e Edital com regra e sem corte emitido não ganham filtro nenhum.

**Cuidado nomeado.** `restringir_a_participantes` é chamada por `calculo.py` para montar o universo
de uma ordem. A condição do corte **deve** valer ali também: a ordem do marco seguinte não pode
conter quem o corte anterior deixou de fora. Não há circularidade — o corte anterior é ato emitido,
não cálculo em curso.

**E o laço que poderia existir é fechado na publicação, não aqui** (`FR-229`): em marco computado, a
Etapa governada não pode estar entre as que alimentam a própria ordem. Em marco de sorteio a
restrição não se aplica, porque `calculo.py` não participa: a ordem vem da relação de habilitados.

---

## R-008 · O empate que atravessa o corte já é legível na ordem

**Achado.** Não é preciso campo novo. `PosicaoNaOrdem.posicao` **compartilha** o número entre
empatados e consome as seguintes, e `empate_residual` diz se o empate sobreviveu a todos os critérios
publicados. Logo:

- **atravessa o corte** quando a posição da última colocação dentro da faixa se repete em alguma
  linha fora dela;
- e só importa quando `empate_residual` é verdadeiro — empate desfeito por critério publicado não
  chega à comparação, porque as posições já saíram distintas.

**Decisão.** O cálculo detecta a travessia comparando as posições na fronteira da faixa, sem tocar na
ordem. Sob `STRICT`, recusa com `DomainError` nomeando as posições; sob `ADMITS_SURPLUS`, estende a
faixa até a última linha daquela posição e grava quantos entraram além do alvo.

**O alvo conta pessoas, e não números de posição.** `desempate.py:18-20` já registra a convenção e
já a explica **por causa desta feature**: a posição é o número de participantes à frente mais um, e
as posições consumidas por um grupo empatado são puladas — `1, 1, 3`. Logo "os dez primeiros" pode
terminar na posição **nove** com dez pessoas dentro, e contar por número de posição entregaria nove.
A `primeira_posicao` e a `ultima_posicao` gravadas no ato são **leitura**, não critério.

**A fronteira é a da faixa emitida**, alvo mais excedente — e não a do alvo. É o que o caso de borda
da spec fixa, e é o que o 57 e o 28 exigem: o empate relevante é o que atravessa a última posição
**analisada**, e ninguém analisa o suplente 21 porque o 20 empatou.

---

## R-009 · O alvo derivado, a identidade que o ato registra, e o quadro parcial

**Decisão.** Em `FROM_VACANCY_TABLE`, o alvo apurado é `LinhaDoQuadroDeVagas.vagas_imediatas` da
linha do recorte — a linha da Modalidade quando o ato tem `lista_id`, e a **linha geral** quando ele
é nulo. O ato registra a quantidade **e** o `id` da linha lida.

**Rationale.** A quantidade sozinha não basta para a obsolescência da `FR-215`: retificado o quadro,
é preciso saber **qual** linha foi lida para dizer se aquele corte ficou para trás. É o mesmo motivo
pelo qual o ato de ordenação guarda `versionId` e não só a regra.

**`lista_id` nulo lê a linha geral** porque as duas grafias já foram decididas: o recorte sem lista é
a ampla concorrência, e a linha de `modalidade` nula é onde a quantidade dela mora. A leitura vem do
**conteúdo publicado** da versão citada pelo ato, e não do relacional em elaboração.

**O quadro parcial era o buraco, e a `D-014` o fecha.** A `025` admite quadro parcial de propósito, e
a Regra de Corte é do **marco**, que pode ordenar três listas. A primeira redação dizia apenas "o
recorte sem linha impede a publicação" — sem dizer **quais** recortes precisam de linha —, e com isso
um Edital com quadro parcial publicava uma regra derivada que seria inexequível na lista sem linha,
descoberta no dia da emissão.

Agora a publicação exige linha para **todo recorte que o marco ordena**: a linha geral e cada
Modalidade que terá lista própria. Faltando uma, o Edital é recusado nomeando o recorte (`FR-183`).

**Linha zerada não é linha ausente.** Zero vagas naquele recorte é declaração legítima, publica, e o
corte dali não faz ninguém progredir. A ausência é que impede.

**Achado da implementação, e ele restringe a `D-014`.** Exigir linha para **toda** Modalidade
declarada — a leitura óbvia daquela decisão — torna impublicável o Edital no **formato normal**. A
`025` documenta por quê na sua `R-006`: o Edital normal declara **também** uma Modalidade chamada
"Ampla concorrência", e a `FR-176` daquela feature **proíbe** dar linha reservada a ela, porque a
quantidade dela mora na linha geral. Essa Modalidade nunca terá linha, por norma — e exigi-la
recusaria o 57/2026 e o 28/2026, que são justamente os dois Editais que usam alvo derivado.

Identificá-la mecanicamente exigiria casar o nome, e a `025` recusou isso por escrito: seria decidir
no plano uma questão que aquela spec declarou aberta, e erraria em Edital que chame a Modalidade de
outra coisa.

**A saída não é enfraquecer a conferência, e a revisão de aceitação recusou a tentativa.** A
primeira implementação exigiu só a linha geral e deixou o recorte por Modalidade para a emissão — o
que permitiria publicar regra derivada inexequível numa das listas, com o defeito aparecendo no dia
do corte. A `D-014` está mantida inteira.

**O que destrava a conferência é o Edital dizer qual Modalidade é a ampla concorrência** (`FR-231`).
Uma identidade declarada no Perfil, alcançável por Retificação, que corresponde à linha geral e não
recebe linha própria. Ela não contraria a `R-006` da `025`: aquela pesquisa recusou **adivinhar**
casando o nome, e isto é o oposto — o sistema lê o que foi declarado. As demais Modalidades continuam
exigindo linha, e o Edital que declara a sua ampla concorrência publica sem exceção nenhuma.

---

## R-010 · Geração, e não faixa: os dois eixos e o buraco que o primeiro desenho tinha

**Problema.** O corte tem **duas** relações com outro corte, e confundi-las é o defeito mais provável
desta feature: *sucessão* substitui, *continuação* acrescenta.

**O buraco que a revisão cruzada encontrou.** O primeiro desenho punha a sucessão sobre a **faixa**:
`corte_anterior` apontando de um corte para outro, com um sucessor por corte. Ele funciona para uma
cadeia de uma faixa só, e quebra na hora em que a `US4` existe. Depois de `raiz → continuação`, as
duas estão vigentes; um sucessor aponta para **uma** delas, e a outra continua vigente autorizando
participantes de uma ordem que já foi substituída. E a unicidade da raiz impedia a saída óbvia —
começar uma cadeia independente.

**Decisão: a sucessão é de geração.** Toda faixa aponta a sua raiz; a sucessão liga **raiz a raiz**, e
alcança a geração inteira.

| Campo | Significado | Unicidade |
|---|---|---|
| `raiz` | a faixa inicial da minha geração; nulo **na própria raiz** | — |
| `faixa_anterior` | continuação — começo onde aquela parou | uma continuação por faixa |
| `corte_anterior` | sucessão — **minha geração substitui aquela**, e só existe em raiz | uma sucessora por geração |

**Vigente é a geração cuja raiz ninguém sucedeu**, e vigente é toda faixa dela. É a mesma definição do
ato de ordenação, e pela mesma razão: vigência não é coluna, senão o append-only teria de ser
desfeito para atualizá-la.

**A unicidade de raiz continua expressável.** `corte_anterior IS NULL AND faixa_anterior IS NULL`
identifica apenas a **primeira** geração do recorte, e é sobre ela que a constraint parcial age — nas
duas metades que o `AtoDeOrdenacao` já demonstrou, porque `NULL` não colide com `NULL` no PostgreSQL
e uma só deixaria passar duas raízes de ampla concorrência. A geração sucessora nasce com
`corte_anterior` preenchido e por isso não disputa a constraint. É, de novo, exatamente o desenho do
`AtoDeOrdenacao`.

**O que isso obriga a testar**, e que o desenho anterior não tinha como: `emitir → continuar → a ordem
muda → suceder`, provando que **nenhuma** das duas faixas da geração anterior continua efetiva
(`FR-227`, `SC-072`).

---

## R-011 · A obsolescência: o que comparar, e o que já existe

**Decisão.** `estado_do_marco` (`classificacao/application/selectors.py:281`) ganha o estado do corte
ao lado do estado da ordem, e as quatro causas da `FR-215` saem de quatro comparações:

| Causa | Comparação |
|---|---|
| ordem sucedida | o ato citado pelo corte não é mais o `ato_vigente` do recorte |
| regra alterada | o `cutRule` da versão vigente difere do que o corte congelou |
| quadro alterado | em alvo derivado, a linha citada mudou de quantidade na versão vigente |
| participante reingressou **no ato de ordenação** | `_reingressos` (`selectors.py:488`), que a `018` já escreveu |

**As três primeiras não custam consulta nova**: o ato vigente e a versão já são lidos para o estado
da ordem. A quarta é a mesma que a tela do marco já faz.

**A mensagem diz a causa, e não "divergências"** (`FR-216`) — a `018` já pagou esse preço uma vez,
quando a divergência genérica escondia o reingresso.

**A medida é o ato de ordenação, e não "o universo do corte"** (`FR-218`, `FR-230`). Todo
participante considerado está no universo do corte; medir ali faria **qualquer** reingresso
obsoletá-lo, inclusive o de quem já está dentro da faixa — e, somado ao bloqueio abaixo, pararia a
Etapa para exigir uma geração sucessora idêntica à anterior. No 77, em que o recurso é julgado na
própria Etapa que o corte governa, esse seria o caso normal. `_reingressos` já responde sobre o ato,
que é exatamente a pergunta certa.

**E a obsolescência passou a ter consequência operacional** (`D-013`, `FR-228`): enquanto ela durar e
a geração sucessora não for emitida, distribuir e concluir avaliação na Etapa governada ficam
bloqueados. O ponto de verificação é o mesmo em que a condição do corte entra — a prontidão —, e por
isso o bloqueio não custa consulta nova: quem já resolve os cortes vigentes do marco uma vez por
listagem resolve, na mesma leitura, se eles estão obsoletos.

**Comparar a regra exige a forma normalizada da `R-003`.** Sem `surplusCount` sempre emitido e sem
uma grafia só para `targetCount`, duas regras idênticas com bytes diferentes acusariam obsolescência
que não existe — e cada falso positivo custaria uma geração sucessora emitida à toa, que é ato
irreversível.

---

## R-012 · As telas e as rotas

**Decisão.** O corte pende do marco, como a ordem e o sorteio:

```
GET  editais/<edital_id>/marcos/<marco_id>/corte            # calcula e mostra; não grava
POST editais/<edital_id>/marcos/<marco_id>/corte/emitir
POST editais/<edital_id>/marcos/<marco_id>/corte/continuar  # a faixa seguinte, com motivo
GET  editais/<edital_id>/marcos/<marco_id>/cortes/<corte_id>
```

A declaração da regra entra na **seção do marco** do cartão do Perfil, junto da janela recursal e do
método de sorteio — não é tela nova. Vale a travessia do rascunho que a `025` nomeou: ler, persistir e
reexibir, com a recusa ancorando no controle certo.

A linha *fora do corte* aparece nas superfícies da Etapa seguinte pelo estado que a prontidão já
devolve — mais um valor na partição, e não uma coluna nova na listagem.

---

## R-013 · O contrato de API

**Decisão.** `cutRule` entra no `MarcoInput` e no `MarcoPublicado` do `openapi.yaml` da `001`, nos
dois lugares — rascunho e publicado —, como `appealWindow` e `drawMethod` já estão. O ato emitido
ganha contrato próprio em [contracts/corte.md](contracts/corte.md).

---

## R-014 · O que a publicação precisa impedir

**Decisão.** Três achados novos na aferição de publicabilidade, e nenhum mecanismo novo:

| Achado | Quando | Classe |
|---|---|---|
| `cut_rule_sem_desfecho_de_empate` | `cutRule` declarado sem `tieOutcome` | impeditivo |
| `cut_rule_sem_linha_de_quadro` | `FROM_VACANCY_TABLE` e o recorte sem linha | impeditivo |
| `cut_rule_em_dois_marcos_da_mesma_etapa` | dois marcos **declarando** governar a mesma Etapa | impeditivo |
| `cut_rule_sem_etapa_governada` | nem Etapa declarada, nem `NONE` | impeditivo |
| `cut_rule_com_etapa_inexistente` | a Etapa declarada não existe na versão | impeditivo |
| `cut_rule_com_etapa_circular` | marco **computado** cuja Etapa governada alimenta a própria ordem | impeditivo |
| `cut_rule_sem_politica_de_continuacao` | `continuation` não declarada | impeditivo |

E um impedimento na publicação de **resultado** (`FR-219`), ao lado do que já existe para ato de
ordenação obsoleto: corte obsoleto impede publicar o que dele depende.

---

## R-015 · Autoridade, idempotência e auditoria

**Decisão.** `emitir_corte` e `continuar_corte` percorrem o mesmo `comando_de_comissao` que
`emitir_ordem` percorre: idempotência por chave, desfecho anterior devolvido na repetição, auditoria
por `auditar` e a permissão `classificacao:emitir`.

**Sem permissão nova.** A `D-010` da spec fecha que a autoridade é a mesma cadeia que emite a ordem,
e criar `corte:emitir` inventaria uma capacidade que nenhum Edital distingue.

**A corrida da `FR-201`** é resolvida pela constraint parcial de raiz, e não por trava de aplicação:
a segunda emissão simultânea viola a unicidade e é devolvida como conflito.

---

## R-016 · O excedente entra junto, e a continuação é declarada

**Problema.** A primeira redação dizia as duas coisas ao mesmo tempo: a `FR-180` mandava a faixa somar
o excedente, e a `FR-204` dava à continuação o teto `alvo + excedente` — que a faixa inicial já teria
consumido. Implementada ao pé da letra, a primeira emissão do 77 progredia setenta pessoas e a `US4`
não tinha o que fazer.

**O que os Editais dizem.** A 6.10 do 77, a 8.13 do 57 e a 8.12 do 28 mandam analisar os documentos
dos suplentes **para chamada imediata, em caso de desistência**. Analisar depois é o que *imediata*
existe para evitar: o suplente precisa estar com documentação deferida **antes** de a desistência
acontecer. Logo os suplentes entram na mesma emissão do alvo.

**E a continuação é outra cláusula.** A 6.3 descreve o que vem depois: *"haverá a análise da
documentação do próximo candidato classificado, respeitando-se a ordem do sorteio, até que se preencha
o número total de vagas"*. Ela vai **além** da faixa publicada.

**Decisão (`D-011`).** Faixa da primeira emissão = `alvo + excedente`. A continuação existe onde a
regra publicada declarar `continuation: ALLOWED`, e a ausência de declaração impede a publicação.

**Sem teto numérico para a continuação admitida**, porque o Edital não publica nenhum: "até que se
preencha" é uma condição cuja apuração é da `016`. O que a limita é o motivo declarado, a autorização,
a auditoria e o fim da ordem. Inventar um teto aqui seria publicar norma que ninguém escreveu — e foi
exatamente o que a `FR-204` fazia.

**No 14/2026 a resposta é `NONE`**, e ela é normativa: a 6.1 diz que quem não foi convocado para a
entrevista não será classificado no resultado final. Continuar ali contrariaria o Edital.

**O empate na fronteira não muda de lugar**: ele incide sobre a última posição da **faixa emitida** —
que agora é, sem ambiguidade, alvo mais excedente (`R-008`).

---

## R-017 · O que a obsolescência faz com o trabalho em curso

**Problema.** A `FR-217` proíbe a obsolescência de alterar o corte vigente, e a `FR-208` faz a
participação ler as faixas vigentes. As duas juntas deixavam uma pergunta sem resposta: durante a
obsolescência, o corte antigo continua governando? O gate cai? O trabalho para?

**O caso que obriga a decidir é o reingresso.** Deferido o recurso que devolve alguém ao universo, o
corte fica obsoleto **por causa dessa pessoa** — e continuar trabalhando sob a faixa antiga é
exatamente excluí-la. O sistema sabe disso: foi ele que marcou a causa.

**Decisão (`D-013`).** O corte obsoleto continua definindo quem está dentro, e **trabalho novo fica
bloqueado** na Etapa governada — distribuir e concluir avaliação —, com motivo nomeado, até a geração
sucessora. O já registrado é preservado, e a leitura continua.

**Onde o bloqueio mora.** No mesmo ponto da prontidão em que a condição do corte entra, como um
impedimento da Etapa — a mesma forma que a `013` já usa para *regra insuficiente*, que a presidência
vê na prontidão antes de tentar consolidar. Não nasce estado novo de inscrição: o impedimento é da
Etapa, e a partição de estados continua fechando.

**As duas alternativas recusadas.** Seguir sem bloquear deixa a operação construir, sobre uma faixa
que o sistema já sabe estar para trás, trabalho que a sucessão invalida. Derrubar o gate readmite sem
ato quem a norma cortou — e amplia o universo em silêncio, que é o oposto de negar por padrão.

---

## Questões que não precisaram de pesquisa

- **O cálculo não reordena.** Ele lê `PosicaoNaOrdem` na ordem em que ela foi emitida; não há
  desempate a executar, e por isso nada de `desempate.py` é tocado.
- **A auditoria e a trilha append-only** são as mesmas de sempre: `save()` que recusa alteração,
  `delete()` que levanta, e privilégio ausente no papel de runtime.
- **O documento publicado** ganha a regra de corte na seção do marco, pelo mesmo caminho por onde a
  janela recursal já sai.
- **A fixture de bytes do documento** é regenerada de propósito, como em toda feature que acrescenta
  conteúdo ao PDF.
