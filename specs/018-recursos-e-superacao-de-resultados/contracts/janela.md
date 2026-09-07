# Contrato — a janela recursal e a definitividade

**Feature**: 018 · **Spec**: [spec.md](../spec.md) · **Pesquisa**: T-007, T-008, T-010

Duas coisas que parecem uma. A janela é **conteúdo normativo**; a definitividade é **aferição de
ato**. Elas se encontram num ponto só — a janela aberta é um dos fatos que impedem a definitiva —, e
a decisão institucional já verificou que não compartilham primitiva.

---

## 1. O conteúdo publicado — degrau 8

Dentro de cada marco classificatório, em `/profiles/*/classificationMilestones/*`:

```json
"appealWindow": {
  "admits": true,
  "durationDays": 5,
  "unit": "DIAS_CORRIDOS"
}
```

| chave | valores | significado |
|---|---|---|
| `admits` | booleano | se aquele marco admite recurso — e `false` é **norma**, não silêncio (FR-113) |
| `durationDays` | inteiro positivo | a duração da janela |
| `unit` | `DIAS_CORRIDOS` | a unidade; único valor admissível na V1 |

**`null` ou ausente significa janela não declarada** — e não janela de zero dias. É o significado que
o degrau declara para todo Edital publicado antes dele (FR-029).

**Três estados, e os três respondem coisas diferentes** (FR-113, D-004):

```text
ausente ou null   →  o Edital nada declarou: nenhum prazo é exibido, calculado ou aplicado
admits: false     →  o Edital declarou que aquele marco NÃO admite recurso: a interposição
                     por esta via é recusada com `appeal_not_provided`
admits: true      →  admite, e `durationDays` diz por quanto tempo
```

Confundir os dois primeiros transforma *"não cabe recurso"* em *"cabe recurso para sempre"*. A
distinção vale por marco: enumerando dois marcos a mesma Etapa e admitindo apenas um deles, a
interposição contra o `ResultadoEtapa` permanece possível pela janela daquele — prazo que restringe
direito interpreta-se a favor de quem recorre (FR-027).

```text
SCHEMA_VERSION      7 → 8
DEGRAUS_DE_MARCO    {8: {"appealWindow": None}}
elevar_marco(...)   simétrico a elevar_etapa e elevar_perfil
```

**Recusas na publicação**

| quando | mensagem |
|---|---|
| `unit` diferente de `DIAS_CORRIDOS` | nomeia que a contagem em dias úteis exige calendário de dias sem expediente que o Edital não publica, e aponta a alternativa: não declarar a janela |
| `admits` verdadeiro sem `durationDays` | a janela declarada sem duração não é computável |
| `durationDays` não positivo | prazo de zero dias não é prazo |

**Retificação**: `/profiles/*/classificationMilestones` já é coleção com identidade em
`publicacoes/domain/colecoes.py`, e `appealWindow` é campo de um item já endereçável. **Verificar na
implementação** se `changes.py` resolve objeto aninhado como alvo; recusando, ele entra em
`COLECOES_ATOMICAS` pelo mesmo argumento que a enumeração de Etapas do marco já entrou — valor
normativo substituído inteiro (T-007).

**Elaboração**: o assistente do marco ganha os três campos, e o documento publicado passa a imprimir
a frase normativa — *"Caberá recurso no prazo de 5 (cinco) dias corridos, contados da divulgação do
resultado"*. A unidade é campo publicado justamente porque essa frase é normativa.

---

## 2. A contagem — função pura

```text
âncora  = a PublicacaoResultado vigente do marco que divulgou PELA PRIMEIRA VEZ o ato que publica
abre    = âncora.publicado_em
fecha   = fim do N-ésimo dia, contado do dia seguinte ao da publicação,
          na zona temporal institucional
```

Exclui-se o dia do começo e inclui-se o do vencimento — a regra geral do processo administrativo.
**Sem prorrogação**: prorrogar o vencimento que cai em dia sem expediente exige o calendário que o
domínio não publica, e é a mesma razão pela qual a unidade é dias corridos (D-004).

**A zona é a institucional**, e não a do servidor. Ela hoje está declarada duas vezes, as duas em
`interface/` — a contagem é domínio, e domínio não importa de `interface`. A zona sobe para módulo
compartilhado antes de a janela existir (T-008).

**Reabertura por conteúdo novo** (FR-025):

| publicação sucessora | abre janela nova? | por quê |
|---|---|---|
| divulga **ato diferente** | sim | conteúdo novo; contra ele ninguém recorreu ainda |
| divulga o **mesmo ato**, mudando só a natureza | não | nada de novo foi divulgado para se contestar |

A comparação é de **identidade do ato** — não de hash do conteúdo, que mudaria por causa do rótulo da
natureza no cabeçalho.

**Vários marcos enumerando a mesma Etapa** (FR-027): a interposição contra o `ResultadoEtapa` é
possível enquanto **qualquer** uma das janelas correspondentes estiver aberta. Prazo que restringe
direito interpreta-se a favor de quem recorre.

**Publicação atrasada não produz prazo vencido antes de existir**: a janela abre no instante em que a
publicação existe, e não na data que alguém digitou no Cronograma. É a razão pela qual a âncora é o
ato, e não uma data absoluta.

---

## 3. A aferição de definitividade

`aferir()` passa a receber a **natureza pretendida**. Hoje ela não a conhece — o comando decide a
natureza depois —, e sem ela a verificação não distingue o que impede a definitiva do que não impede
nada (T-010).

**Os seis fatos, e o que cada um responde**

| # | fato | como se apura | impede |
|---|---|---|---|
| 1 | recurso pendente pertinente | existe recurso do marco sem decisão | `DEFINITIVA` |
| 2 | reavaliação determinada não cumprida | decisão dessa espécie sem sucessor do par posterior a ela | `DEFINITIVA` |
| 3 | providência a jusante não cumprida | nem o ato candidato cita a decisão, nem há ato citante já publicado **naquele marco** | `DEFINITIVA` |
| 4 | janela estruturada aberta | função pura sobre a publicação vigente e a norma | `DEFINITIVA` |
| 5 | ato obsoleto | `estado_do_marco`, que a 017 já verifica | **as duas** naturezas |
| 6 | pendência reaberta por progressão retroativa | inscrição com sucessor habilitante e sem Resultado numa Etapa do marco | **as duas** naturezas |

**A assimetria é dos quatro primeiros, e não dos seis.** Eles são fatos da disputa, e enquanto ela
corre o preliminar é o caminho normal. Os dois últimos são do conteúdo: ato obsoleto divulga ordem
revogada e reingresso pendente divulga ordem que já se sabe incompleta — e nenhuma delas fica menos
falsa por chamar-se preliminar (D-007, FR-079, FR-083). Por isso os dois são aferidos **antes** de a
natureza pretendida ser consultada.

**Pertinência ao marco** (FR-084) alcança dois conjuntos, e é a segunda metade que fecha o buraco:

```text
recurso contra a PublicacaoResultado daquele marco
recurso contra ResultadoEtapa de Etapa que o marco enumera, no mesmo Edital e Perfil
```

Sem a segunda, o recurso individual seria a porta por onde uma definitiva nasceria com um Resultado
em disputa dentro dela.

**Códigos de recusa**, no molde dos três que `publicabilidade.py` já tem — cada um com o caminho
nomeado, porque recusa que não diz o que fazer devolve a pessoa à tela anterior sem nada:

| código | HTTP | caminho que a mensagem nomeia |
|---|---|---|
| `publication_appeal_pending` | 422 | aguardar o julgamento, ou publicar como preliminar |
| `publication_reassessment_pending` | 422 | concluir a reavaliação determinada e consolidar |
| `publication_remedy_pending` | 422 | emitir o ato sucessor **citando a decisão** e publicar aquele |
| `publication_window_open` | 422 | o instante em que a janela fecha |
| `publication_reentry_pending` | 422 | consolidar o Resultado de quem reingressou |

Todos são **impedimento**, e não aviso: a 017 já decidiu que não existe publicar ato impedido
mediante confirmação adicional.

### 3.1 O cumprimento da providência, por citação publicada

```text
cumprida_para(decisao, ato_candidato) =
      o ato_candidato cita a decisão
   OU existe, no MESMO marco, ato citante que já foi publicado
```

A citação nasce com o `AtoDeOrdenacao`: é gravada por `emitir_ordem`, na mesma transação, por quem já
tem autoridade para emitir — a tela de emissão passa a oferecer as decisões pendentes daquele marco.
Ela é **proveniência do ato**, do mesmo tipo de `motivo_da_sucessao`: não tem autoridade, instante
nem motivo próprios, e não é passo humano separado que se possa esquecer.

**Citar não é cumprir.** Um ato pode citar a decisão e nunca ser publicado — por ficar obsoleto antes
disso. Enquanto isso não acontecer, a providência continua pendente e **qualquer sucessor do marco
pode recitá-la**. É essa recitação que impede o único beco possível: `UNIQUE(decisao)`, que uma
redação anterior previa, tornaria a definitiva do marco impedida para sempre no dia em que o primeiro
ato citante ficasse obsoleto.

**A apuração é por marco.** Uma decisão cuja providência é normativa alcança todos os marcos que a
regra retificada governa. Cada um precisa do seu ato citante publicado; o trabalho feito num marco
não libera a definitiva de outro.

**Um mesmo ato cita quantas decisões cumprir**, de modo que dois deferimentos sobre o mesmo marco se
resolvem numa emissão só.

**Não é circular**: a publicação que executa o remédio é a que cita a decisão, e por isso não é
impedida por ela.

**A pertinência é conferida no banco** — espécie, Edital, Perfil e Marco —, e não apenas no comando:
uma gravação direta que ligasse a decisão a um ato de outro marco liberaria indevidamente uma
definitiva. Ver [data-model.md](../data-model.md) §10.1.

**Por que não basta "publicar ato diferente"** — que era a redação original: um ato sucessor emitido
por razão alheia, como uma Retificação que mudou um peso, encerraria a pendência sem que ninguém
tivesse corrigido o vício reconhecido. O vínculo tem de ser causal (T-015).

---

## 4. A declaração expressa

Exigida **somente** quando a natureza pretendida é `DEFINITIVA` e não há janela computável para o
marco (FR-085).

| campo | |
|---|---|
| autor | `identity_subject` de quem publica |
| instante | o da publicação |
| fundamento | texto, obrigatório |

Gravada na publicação, no nascimento, e auditável. **Recusada quando há janela computável**
(FR-086): declarar o que o sistema verifica seria pedir à pessoa que respondesse pelo que a máquina
sabe — e reintroduziria, com mais passos, a afirmação sem lastro que o E2E17-005 registrou.

---

## 5. A definitiva que corrige outra definitiva

**Não nasce natureza nova.** `DEFINITIVA_RETIFICADA` seria terceiro valor no enum, três pares a
decidir na regra de não regressão, mais um valor em `uq_publicacao_por_ato_natureza` e toda leitura
de natureza mudando. Vigência e natureza derivam da cadeia, e não de estado duplicado (FR-087).

**O nome vem do fato**, derivado da cadeia e das decisões que a motivaram:

> *"Resultado definitivo, retificado em 12/09/2026 em razão do julgamento do recurso REC-2026-K7M4Q2PX."*

E, sendo mais de uma, todas — *"em razão do julgamento dos recursos A e B"*. A causa é derivada por
dois caminhos, porque há dois modos de um recurso corrigir um ato:

```text
citação   a providência a jusante nomeia a decisão no próprio ato (FR-089)
cadeia    a correção fixada e a reavaliação determinada não citam nada: superam o Resultado, e o
          ato sucessor passa a enumerar o sucessor no lugar do superado
```

Ela é **congelada** no conteúdo publicado, em ordem `(decidido_em, protocolo)`: a página e o
documento leem os mesmos bytes, e ordem instável faria o mesmo ato produzir resumo canônico
diferente a cada publicação. A leitura aceita a forma singular que antecedeu esta — conteúdo
publicado não se reescreve (FR-091).

Na página e no documento (FR-088, FR-112). E a publicação vigente passa a **dizer que é a vigente** — hoje
só a anterior diz que foi sucedida, que é a oportunidade nº 3 do relatório da E2E-017 (FR-090).

**Nenhuma exceção à regra da janela.** A redação anterior da spec dispensava essa publicação de
janela nova; a exceção era inalcançável e saiu. Com janela estruturada o cenário não ocorre — a
definitiva não nasce com recurso pendente, e a interposição é recusada depois de fechada a janela;
sem janela estruturada não há janela para abrir, e o candidato prejudicado pelo conteúdo corrigido
recorre da nova publicação como de qualquer objeto vigente (D-008).
