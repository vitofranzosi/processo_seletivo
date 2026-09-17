# Quickstart — como se verifica que esta feature funcionou

Três cenários, um por história. Todos pela interface administrativa, sem shell, sem banco — é o que o
princípio VI cobra.

## Pré-requisitos

```bash
cd backend && make lint check test-pg
```

`test-pg`, nunca `test`: sem o par `TEST_DB_ENGINE=postgresql` **e** `POSTGRES_USER` a suíte cai para
SQLite e 33 testes falham por motivo que não é o diff.

Para subir a interface, o seletor de identidade precisa estar ligado — sem
`INTERFACE_SELETOR_IDENTIDADE=true` o `/gestao/` devolve 503.

---

## Cenário 1 — o marco do Edital canônico (P1, SC-138, SC-139)

**Monte**: um Edital com um Perfil, três vagas, uma Etapa de análise curricular marcada como
classificatória, **sem Modalidade de Concorrência**.

**Percorra** o assistente até a etapa de Classificação e acrescente um marco.

**Conte** os controles apresentados, **sem abrir o disclosure de ajuda**.

| O que observar | Esperado |
|---|---|
| Primeira pergunta | **como a ordem é produzida** — antes de qualquer campo sobre o marco |
| Controles apresentados | **menos de 10** (hoje: 28) |
| Combinação e normalização | **ausentes**, com a declaração de que a pontuação combinada é a da Etapa única |
| Casas decimais e arredondamento | já preenchidos com `2` e `meio para cima`, editáveis |
| Código e denominação | já derivados do Perfil, editáveis |
| Campos do método de sorteio | ausentes, porque a ordem não nasce de sorteio |

**Método de contagem de SC-138**: conta-se cada controle que recebe foco por teclado na composição de
**um** marco — `input`, `select`, `textarea`, `radio` e `checkbox` visíveis. Campo oculto do
contrato do rascunho **não conta**: ele não é pergunta. Ajuda em `<details>` fechado não conta.

**Depois, volte ao Perfil e declare uma Modalidade.** As perguntas sobre ampla concorrência e
reversão, que estavam ocultas, aparecem — e nada do que já foi declarado se perdeu.

---

## Cenário 2 — o conceito onde a decisão acontece (P2, SC-141)

**Percorra** as telas de Classificação, Distribuição, Corte e Ocupação.

| Tela | O que precisa estar visível, no primeiro uso |
|---|---|
| Distribuição | o que a consolidação **produz**, antes de a ação ser acionada |
| Classificação | por que a Etapa pertence ao Edital e a ordem pertence ao Perfil |
| Corte | **recorte**, **geração** e **faixa**, definidos |
| Ocupação | os mesmos três termos, definidos |

**E o que não pode acontecer**: nenhuma ajuda visível dentro dos cartões de composição (FR-428). A
decisão do projeto permanece; o equivalente para tecnologia assistiva continua de pé. Microcópia
nova vai para o `como-preencher` da etapa, nunca para o cartão.

**O bloco de ajuda da etapa** não aparece enquanto não existir item a que ele se refira (FR-426), e
cada item dele leva ao campo que explica (FR-427).

---

## Cenário 3 — o método declarado uma vez (P3, SC-140)

**Monte**: um Edital com **sete Perfis**, todos com marco que ordena por sorteio.

**Conte** quantas vezes a regra do sorteio precisa ser declarada.

| O que observar | Esperado |
|---|---|
| Declarações do método | **uma** (hoje: sete) |
| Cada marco de sorteio | referencia o método comum, sem redigitá-lo |
| Um marco que precise divergir | declara método próprio, e a divergência fica **explícita** no conteúdo normativo |

**A fronteira que não pode vazar** (contrato do rascunho): componha um marco de sorteio, declare o
método, troque a forma da ordem para pontuação, e publique. O método **não** pode aparecer no
conteúdo publicado — e **precisa** reaparecer na tela se a forma voltar a ser sorteio.

---

## Cenário 3-bis — o sorteio que não precisa de Etapa (FR-432)

O percurso mais curto desta feature, e o único que **remove** uma recusa em vez de remover uma
pergunta.

**Monte**: um Edital cujo sorteio precede a análise documental — o caso real do ACH-48.

**Acrescente** um marco e responda que a ordem nasce de **sorteio**. Deixe a habilitação em
*nenhuma* e **não enumere Etapa alguma**.

| O que observar | Esperado |
|---|---|
| Publicar o Edital | **aceito** — hoje a validação recusa, exigindo uma Etapa que o Edital não tem |
| A ajuda da tela | deixa de se contradizer: ela já mandava deixar em nenhuma |

**A contraprova, no mesmo percurso**: troque a forma da ordem para **pontuação**, sem enumerar
Etapa, e publique. Agora **tem que recusar**. A exigência não foi removida — foi condicionada.

**Por que só agora dá**: a validação exigia Etapa de todo marco porque não conseguia distinguir
quem sorteia de quem pontua. A forma da ordem cria a distinção, e é dela que a regra depende.

---

## Cenário 4 — o que não pode ter mudado (SC-142)

**Semeie** o banco e publique um Edital **antes** de aplicar a feature; guarde o conteúdo canônico.
Aplique a feature e releia.

O conteúdo publicado é **idêntico**, byte a byte. Sem `orderProduction`, sem `drawMethod` no nível do
Edital, com o método literal em cada marco. Nenhuma chave nova em snapshot publicado.

**Retifique** esse Edital. Os valores já declarados prevalecem sobre qualquer padrão novo (FR-421):
a Retificação não vê `2` e `meio para cima` chegarem por conta própria.

**Lembre**: documento publicado não se regenera. Mudou o renderizador? Re-semeie para ver.
