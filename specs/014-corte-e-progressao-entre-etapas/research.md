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
  "surplusCount": 20,
  "tieOutcome": "ADMITS_SURPLUS" | "STRICT"
}
```

- `targetKind` diz qual das duas formas da `FR-179` vale; `targetCount` só é lido em `FIXED`, e é
  **recusado** em `FROM_VACANCY_TABLE` — declarar os dois faria o conteúdo publicado afirmar duas
  fontes para a mesma quantidade, que é o que o Princípio II proíbe.
- `surplusCount` é o excedente da `FR-180`, absoluto, e `0` significa sem suplentes. Aqui zero **é**
  um valor: o Edital que não declara suplentes tem faixa igual ao alvo.
- `tieOutcome` não tem valor padrão em lugar nenhum. A `FR-182` o exige declarado, e a ausência é
  achado impeditivo de publicação.
- `cutRule: null` significa **marco que não corta**, que é o que todo Edital publicado hoje afirma.

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

## R-006 · Qual Etapa o corte governa — e a pergunta que não tinha resposta

**Problema.** A spec diz "o marco que antecede uma Etapa". O marco enumera Etapas em `etapas`, e
**nada impede dois marcos do mesmo Perfil de enumerarem conjuntos cuja última Etapa é a mesma**. Se
os dois declararem regra de corte, a Etapa seguinte tem dois cortes com alvos diferentes, e o sistema
não teria como escolher.

**Decisão, em duas partes.**

1. **A Etapa governada é a que sucede a última Etapa que o marco enumera**, na ordem publicada das
   Etapas. `calculo.py:189` já tem o `_ultima_etapa` que responde a primeira metade, e a segunda é o
   `etapa_anterior`/`etapas_anteriores` de `resultados/domain/progressao.py`, lido ao contrário.
2. **Dois marcos com regra de corte governando a mesma Etapa é achado impeditivo de publicação**, com
   mensagem que nomeia os dois marcos. Não se escolhe um; recusa-se o Edital que os publica.

**Rationale.** A alternativa — unir as faixas dos dois — aplicaria a soma de dois alvos que ninguém
publicou. A outra — o marco de maior ordem vence — inventaria precedência normativa. Recusar é a
resposta que este repositório já dá quando duas declarações dizem coisas incompatíveis.

**E o marco que não antecede Etapa alguma pode ter corte.** É o corte de suplentes do 77, do 57 e do
28: ele existe para a análise documental e para a chamada, e simplesmente não tem efeito de
participação. A emissão é legítima; o gate não incide.

---

## R-007 · Como a condição entra na progressão sem custar consulta por linha

**Problema.** A `FR-213` proíbe verificação por linha, e os orçamentos de consulta da `011`, da `012`
e da `015` são verificados por teste. A condição do corte não pode corroê-los.

**Decisão.** A mesma cirurgia que a progressão já usa: um `Exists` correlacionado somado dentro de
`restringir_a_participantes`, e uma pergunta de existência em `participa_da_etapa`.

```
consulta.filter(Exists(ItemDoCorte.objects.filter(
    inscricao_id=OuterRef(…), corte__in=<cortes vigentes do marco governante>,
    consequencia=ItemDoCorte.Consequencia.PROGREDIU)))
```

O conjunto `<cortes vigentes>` é resolvido **uma vez por listagem**, junto do `_anteriores_e_gate`,
que já lê o conteúdo publicado uma vez e devolve o que a junção precisa. O custo somado é: uma
leitura a mais do marco governante no conteúdo que já estava em memória, e uma consulta para os
cortes vigentes daquele marco — constante, não proporcional à população.

**A condição é dormente quando não há corte vigente** (`FR-214`), e é esse gate que garante a não
regressão: Edital sem regra e Edital com regra e sem corte emitido não ganham filtro nenhum.

**Cuidado nomeado.** `restringir_a_participantes` é chamada por `calculo.py` para montar o universo
de uma ordem. A condição do corte **deve** valer ali também: a ordem do marco seguinte não pode
conter quem o corte anterior deixou de fora. Não há circularidade — o corte anterior é ato emitido,
não cálculo em curso.

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

**A fronteira é a da faixa emitida**, alvo mais excedente — e não a do alvo. É o que o caso de borda
da spec fixa, e é o que o 57 e o 28 exigem: o empate relevante é o que atravessa a última posição
**analisada**, e ninguém analisa o suplente 21 porque o 20 empatou.

---

## R-009 · O alvo derivado, e a identidade que o ato registra

**Decisão.** Em `FROM_VACANCY_TABLE`, o alvo apurado é `LinhaDoQuadroDeVagas.vagas_imediatas` da
linha do recorte — a linha da Modalidade quando o ato tem `lista_id`, e a **linha geral** quando ele
é nulo. O ato registra a quantidade **e** o `id` da linha lida.

**Rationale.** A quantidade sozinha não basta para a obsolescência da `FR-215`: retificado o quadro,
é preciso saber **qual** linha foi lida para dizer se aquele corte ficou para trás. É o mesmo motivo
pelo qual o ato de ordenação guarda `versionId` e não só a regra.

**`lista_id` nulo lê a linha geral** porque as duas grafias já foram decididas: o recorte sem lista é
a ampla concorrência, e a linha de `modalidade` nula é onde a quantidade dela mora. A leitura vem do
**conteúdo publicado** da versão citada pelo ato, e não do relacional em elaboração.

**Linha ausente não é zero** — mas isso é recusado na publicação (`FR-183`), e não na emissão: um
Edital publicado com alvo derivado sempre tem a linha, porque sem ela não teria publicado.

---

## R-010 · A faixa seguinte: uma cadeia, dois eixos

**Problema.** O corte tem **duas** relações com outro corte, e confundi-las é o defeito mais provável
desta feature: *sucessão* substitui, *continuação* acrescenta.

**Decisão.** Dois campos distintos, e duas constraints parciais:

| Campo | Significado | Unicidade |
|---|---|---|
| `corte_anterior` | sucessão — este corte substitui aquele | um sucessor por corte |
| `faixa_anterior` | continuação — este corte começa onde aquele parou | uma continuação por faixa |

A raiz é o corte com os dois nulos, e ela é única por `(edital, perfil_id, marco_id, lista_id)` — nas
duas constraints parciais que o `AtoDeOrdenacao` já demonstrou, porque `NULL` não colide com `NULL`
no PostgreSQL e uma constraint só deixaria passar duas raízes de ampla concorrência.

**Vigente é o corte que ninguém sucedeu** — a mesma definição do ato de ordenação, e pela mesma
razão: vigência não é coluna, senão o append-only teria de ser desfeito para atualizá-la. Uma
continuação **não** sucede a anterior, e por isso as duas ficam vigentes ao mesmo tempo, que é o que
a `FR-202` manda.

---

## R-011 · A obsolescência: o que comparar, e o que já existe

**Decisão.** `estado_do_marco` (`classificacao/application/selectors.py:281`) ganha o estado do corte
ao lado do estado da ordem, e as quatro causas da `FR-215` saem de quatro comparações:

| Causa | Comparação |
|---|---|
| ordem sucedida | o ato citado pelo corte não é mais o `ato_vigente` do recorte |
| regra alterada | o `cutRule` da versão vigente difere do que o corte congelou |
| quadro alterado | em alvo derivado, a linha citada mudou de quantidade na versão vigente |
| participante reingressou | `_reingressos` (`selectors.py:488`), que a `018` já escreveu |

**As três primeiras não custam consulta nova**: o ato vigente e a versão já são lidos para o estado
da ordem. A quarta é a mesma que a tela do marco já faz.

**A mensagem diz a causa, e não "divergências"** (`FR-216`) — a `018` já pagou esse preço uma vez,
quando a divergência genérica escondia o reingresso.

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
| `cut_rule_em_dois_marcos_da_mesma_etapa` | dois marcos governando a mesma Etapa | impeditivo |

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

## Questões que não precisaram de pesquisa

- **O cálculo não reordena.** Ele lê `PosicaoNaOrdem` na ordem em que ela foi emitida; não há
  desempate a executar, e por isso nada de `desempate.py` é tocado.
- **A auditoria e a trilha append-only** são as mesmas de sempre: `save()` que recusa alteração,
  `delete()` que levanta, e privilégio ausente no papel de runtime.
- **O documento publicado** ganha a regra de corte na seção do marco, pelo mesmo caminho por onde a
  janela recursal já sai.
- **A fixture de bytes do documento** é regenerada de propósito, como em toda feature que acrescenta
  conteúdo ao PDF.
