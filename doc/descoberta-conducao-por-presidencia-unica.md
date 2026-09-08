# Descoberta — o Edital pequeno conduzido pela presidência

Levantamento feito em **08/09/2026**, sobre a `main` em `a6f25a4`, a partir de uma pergunta do
usuário: *existem editais menores, onde talvez a própria presidência conduza todo o processo — o
sistema suportaria esse cenário?*

> **Não cria requisito, não abre spec e não decide nada.** O que se registra é o que o código hoje
> permite, os dois pontos em que ele recusa, e a conta de identidades que essa recusa impõe. Se a
> conta é aceitável, se o arranjo mínimo é legítimo e se algo deve mudar são perguntas de
> governança, e a Constituição as reserva ao usuário.

## Por que existe

A pergunta parece de configuração e não é: ela atravessa `011`, `012`, `013`, `015`, `017` e `018`,
e a resposta só aparece somando a cadeia de autorização inteira. Somada uma vez, vale a pena ficar
escrita — porque a conclusão contraria a intuição em dois lugares, e porque a **contagem de pessoas
que um Edital pequeno exige** é decisão institucional que hoje não está dita em lugar nenhum.

---

## 1. O que já funciona, sem nada novo

**Comissão de uma pessoa só é estado previsto, e testado.** Não há mínimo de membros: constituir com
uma única presidente é caminho normal, e
[`test_presidencia.py:102`](../backend/tests/integration/comissoes/test_presidencia.py:102) exercita
exatamente a presidente que é também a única alocada — inclusive a guarda que recusa rebaixá-la
enquanto houver alocação ativa
([`comissao.py:303`](../backend/processo_seletivo/comissoes/application/comissao.py:303), FR-030).

**Presidir não impede avaliar.** `pode_atuar_na_etapa`
([`autorizacao.py:58`](../backend/processo_seletivo/comissoes/domain/autorizacao.py:58)) não consulta
função nem permissão — só vínculo ativo e alocação —, e a segunda pergunta da `012` acrescenta a
Atribuição. A presidente aloca a si mesma, distribui para si mesma e avalia. A proposta de rodízio
não a exclui do conjunto elegível.

**Uma avaliação por inscrição é o que a ausência significa**, e não um padrão de conveniência
([`previsao.py:19`](../backend/processo_seletivo/avaliacoes/domain/previsao.py:19), FR-009). O Edital
pequeno que nada declara já nasce compatível com banca de um. Declarando duas, nada trava: a
distribuição informa quantas faltam e por quê, e quem lê decide.

**Consolidar Resultado, registrar Ocorrência, impedir e emitir o ato de ordenação** passam todos por
`comando_de_comissao`, que aceita a **presidência** como base suficiente
([`__init__.py:58`](../backend/processo_seletivo/comissoes/application/__init__.py:58)) — sem exigir
o papel sistêmico de Gestor.

**Um detalhe de partida:** a comissão vazia não tem presidência para se autorizar, e por isso o
primeiro ato — constituí-la — exige `comissao:gerir`
([`autorizacao.py:39`](../backend/processo_seletivo/comissoes/domain/autorizacao.py:39)). Depois
disso a presidência se sustenta sozinha no lado da comissão.

---

## 2. Os dois lugares onde a pessoa única esbarra

### 2.1 A segregação de funções da `001` — e ela é de **domínio**, não de tela

Publicar um Edital é recusado com `403` quando a mesma identidade elaborou, homologou **e** publica:

```text
revisao.prepared_by == homologacao.homologated_by == actor.subject  →  segregation_of_duties
"Uma única pessoa não pode elaborar, homologar e publicar."
```

[`publish_edital.py:574`](../backend/processo_seletivo/publicacoes/application/publish_edital.py:574),
espelhado na Retificação em
[`retificacoes.py:615`](../backend/processo_seletivo/publicacoes/application/retificacoes.py:615)
(FR-021 da `001`). A interface antecipa a recusa em vez de descobri-la no clique
([`selectors.py:219`](../backend/processo_seletivo/publicacoes/application/selectors.py:219),
[`acoes.py:211`](../backend/processo_seletivo/interface/acoes.py:211)), mas quem recusa é o comando.

**A regra é ternária, e é isso que abre a saída:** ela alcança a coincidência dos **três** atos.
Elaborar e homologar sozinha, e outra pessoa publicar — ou elaborar e publicar, e outra homologar —
passa. Uma segunda identidade basta, e ela precisa praticar **um** ato, não todos.

### 2.2 O impedimento recursal da `018` — e aqui a segunda identidade não pode ser qualquer uma

`recurso:julgar` é papel próprio e deliberadamente **não** decorre da presidência. O comentário do
mapa de papéis diz o porquê
([`identidade.py:66`](../backend/processo_seletivo/interface/identidade.py:66)): pendurá-lo num papel
existente concederia o julgamento, por construção, a quem a FR-039 manda afastar.

Sobre isso, as cinco perguntas de
[`elegibilidade.py:42`](../backend/processo_seletivo/recursos/domain/elegibilidade.py:42) barram com
`403` quem:

```text
concluiu a Avaliação que fundamentou o Resultado alcançado
consolidou o Resultado alcançado (ou constatou a Ocorrência)
emitiu o ato de ordenação atacado
praticou a publicação atacada
tem Impedimento declarado quanto àquela inscrição
```

Valem para **admitir** e para **julgar**, na mesma porta
([`admitir.py:54`](../backend/processo_seletivo/recursos/application/admitir.py:54),
[`julgar.py:102`](../backend/processo_seletivo/recursos/application/julgar.py:102)) — de modo que
nem o juízo de admissibilidade sobrevive à pessoa única.

Na presidência-conduz-tudo, ela é impedida por três das cinco ao mesmo tempo. E isto **não é
lacuna**: a [Decisão 018 §5](decisao-018-escopo-institucional-do-recurso.md:361) descartou
explicitamente a alternativa *"julga a presidência, por vínculo"* citando este cenário — *"em
comissões pequenas, a presidência frequentemente avaliou"* — e registrou a consequência aceita ao
escolher **5B**: *"Em comissão pequena, o impedimento pode não deixar ninguém elegível — e a saída é
institucional, não técnica"*, concedendo o papel a quem está fora da comissão. Foi assim que
`resultado:publicar` resolveu o mesmo aperto na `017`.

**O que a recusa custa em prazo, e não só em pessoas:** o Edital que o produto emite promete recurso
em texto fixo ([`secoes.py:146`](../backend/processo_seletivo/editais/domain/secoes.py:146)). O nome
do julgador precisa existir **antes da divulgação**, e não quando a primeira peça chega.

---

## 3. A conta das identidades

Nenhuma das duas recusas exige uma pessoa por papel: os papéis se acumulam numa identidade, e o que
o sistema verifica é **autoria de ato**, não crachá. Somando as duas, o mínimo é **duas
identidades** — com uma divisão específica, porque nem toda divisão de dois sobrevive à §2.2.

```text
arranjo mínimo que passa nas duas recusas

#1  presidência           gestor + elaborador + publicador do Edital + presidência da comissão
                          aloca-se, avalia, consolida, emite o ato, publica o resultado
                          impedida de julgar por AVALIOU, CONSOLIDOU, EMITIU e PUBLICOU

#2  a outra assinatura    homologador do Edital + julgador
                          pratica UM ato na cadeia do Edital — o que satisfaz FR-021 —
                          e não toca avaliação, consolidação, ato nem publicação de resultado:
                          nenhuma das cinco perguntas o alcança
```

Duas armadilhas que a contagem esconde:

- **A segunda identidade não pode ser o publicador do resultado.** Se #2 divulgar o resultado, ele
  responde `PUBLICOU` e o par inteiro fica impedido — e aí o mínimo sobe para **três**. Publicar o
  Edital e publicar o resultado são capacidades distintas
  ([`identidade.py:35`](../backend/processo_seletivo/interface/identidade.py:35), `017`, FR-025), e
  aqui essa distinção deixa de ser doutrinária: ela decide a conta.
- **Emitir e divulgar o resultado na mesma pessoa não é barrado.** Não há verificação de autoria
  entre `classificacao:emitir` e `resultado:publicar` — a separação ali é de capacidade, e a `017`
  a formulou assim de propósito. É o que permite a #1 fazer os dois.

---

## 4. O que este levantamento **não** resolve

Três perguntas ficam abertas, e todas são de governança:

1. **Duas identidades é aceitável como piso institucional?** O produto hoje o exige sem nunca o
   dizer: quem for montar um Edital pequeno descobre a FR-021 no `403` da publicação, e o
   impedimento recursal quando o primeiro recurso chega. Dizer o piso antes é decisão de produto.
2. **O arranjo mínimo da §3 é legítimo, ou apenas possível?** Ele satisfaz cada regra escrita e
   concentra em #1 tudo que decide a sorte do candidato, deixando a #2 a homologação e o
   julgamento. Nenhuma regra do sistema o recusa; se a instituição o recusa é outra conversa.
3. **A recusa deve ser antecipada?** Nada hoje avisa, na constituição da comissão ou na prévia de
   publicação, que o Processo caminha para um recurso sem julgador elegível. A `018` decidiu que a
   saída é institucional; ela não decidiu se o sistema deve **avisar** que ela será necessária.

Nenhuma delas vira requisito por estar escrita aqui.
