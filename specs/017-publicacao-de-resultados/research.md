# Pesquisa — Publicação de Resultados

As decisões técnicas da 017. As decisões de domínio estão fechadas na spec (D-001 a D-009) e não são
reabertas aqui; o que segue é como cada uma se realiza no código que já existe.

Nenhum item ficou como NEEDS CLARIFICATION.

---

## T-001 — O agregado mora num app novo, `divulgacao`

**Decisão**: app novo, `processo_seletivo/divulgacao/`.

**Racional**: a alternativa óbvia — acrescentar `PublicacaoResultado` ao app `publicacoes` — poria
`Publicacao` e `PublicacaoResultado` no mesmo `models.py`, e é exatamente a confusão que a D-009
existe para evitar. São atos diferentes, sobre objetos diferentes, praticados por autoridades que
podem ser diferentes, com ciclos de vida independentes. O Princípio I manda que conceitos distintos
sejam distintos onde a linguagem é lida, e `models.py` é onde ela é mais lida.

A direção da dependência confirma o corte: `divulgacao` importa `classificacao` (o ato),
`publicacoes` (o catálogo de autoridades e o renderizador) e `inscricoes` (nome e protocolo, uma
vez, na composição). Nenhum deles passa a importar `divulgacao`. Um app novo que só é importado por
`interface` e `portal` não acrescenta acoplamento; acrescenta uma fronteira.

**Alternativas consideradas**:

- **Dentro de `classificacao`** — faria o app cuja autoridade é o vínculo com a comissão hospedar um
  ato cuja autoridade é capacidade institucional (D-004). O acoplamento seria de autoridade, não de
  dado, e é o pior tipo.
- **Dentro de `publicacoes`** — compartilha o renderizador, e é o único argumento a favor. Mas o
  renderizador já é importável de fora: `inscricoes` o usa desde o comprovante.

---

## T-002 — A cadeia repete a forma da 015, e as invariantes vão ao banco

**Decisão**: `publicacao_anterior` como FK para `self`, com duas constraints:

```text
uq_publicacao_raiz_por_marco     (edital, perfil_id, marco_id) WHERE publicacao_anterior IS NULL
uq_publicacao_sucessora_unica    (publicacao_anterior)         WHERE publicacao_anterior IS NOT NULL
uq_publicacao_por_ato_natureza   (ato, natureza)
```

A terceira responde a "o mesmo ato pode ser publicado duas vezes?" — **pode, uma por natureza**
(D-007, FR-039). Um preliminar que ninguém contestou vira definitivo sem que exista ato novo a
emitir; exigir um sucessor idêntico faria a 015 registrar uma sucessão que não sucedeu nada. A mesma
natureza duas vezes sobre o mesmo ato é duplicidade, e vira recusa de banco — o que dá ao cenário
das duas abas uma garantia que a idempotência sozinha não dá (T-005).

A ordem entre naturezas — preliminar não sucede definitiva — e a pertinência do predecessor ao mesmo
marco dependem de **outra linha**, e por isso são trigger, e não `CheckConstraint`: é a situação que
`resultado_etapa_coerente` já resolve desse jeito na 013.

Vigente é a publicação que ninguém sucedeu — `sucessoras__isnull=True` —, e não existe coluna.

**Racional**: é a forma que `AtoDeOrdenacao` já usa (`classificacao/models.py:44-61`), e ela não é
estilo. A política de papéis revoga `UPDATE` das tabelas append-only (`seguranca/papeis.py`), então
um booleano `vigente` seria impossível de virar em produção — o desenho não é preferido, é o único
que o banco permite. As duas constraints também são o que impede duas publicações concorrentes de
nascerem raízes do mesmo marco (FR-042).

A cadeia é **uma por marco**, com `natureza` como atributo (D-007): a definitiva sucede a
preliminar. Uma cadeia por natureza permitiria duas vigentes simultâneas para o mesmo marco.

**Alternativas consideradas**: coluna `vigente` com atualização em transação — inexecutável sob a
política de privilégios; ordem crescente tipo `publication_order` como em `Publicacao` — resolve
ordenação, não sucessão, e não diz quem sucedeu quem.

---

## T-003 — A publicação congela a projeção, não o ponteiro

**Decisão**: `conteudo_publico` (bytes canônicos) + `conteudo_publico_hash` (sha256), no molde de
`Publicacao.canonical_content`/`content_hash`, gravados no ato de publicar. **Só o que é
divulgado** entra ali; a projeção individual é tabela à parte (T-010).

**Racional**: e o racional **não** é a estabilidade dos rótulos. `VersaoConsolidada` é append-only,
e ler `ato.versao.content` na hora de renderizar já devolveria sempre os mesmos nomes.

O que precisa ser congelado é a **projeção**: quem entra na lista (FR-017), o que de cada linha
atravessa a fronteira (FR-018 a FR-020), como o empate é dito (FR-014), como a natureza é afirmada
(FR-016). São decisões desta feature, escritas em código desta feature. Compor na leitura faria
qualquer correção futura numa delas reescrever, em silêncio, tudo o que já foi divulgado — e a
I-005 diz o contrário.

Congelar também é o que dá conteúdo à SC-004: existe um resumo publicado a conferir, e ele é o mesmo
que o documento imprime (FR-063). E o resumo só significa "isto foi divulgado" porque cobre
exclusivamente o divulgado — um hash sobre público mais privado provaria outra coisa, e não a que a
SC-004 enuncia. `canonical_sha256` já faz a canonização — `sort_keys`, `separators` sem espaço, NFC
(`shared/canonical.py:86-94`) — e é a mesma função que a publicação do Edital usa.

**Este não é o resumo da prévia.** `conteudo_publico_hash` contém `publicado_em`, que só existe
depois do POST; a assinatura que fecha a janela entre ler e confirmar cobre outro material, e os dois
estão separados em T-005.

**Alternativas consideradas**: compor na leitura a partir do ato e da versão — mais barato em
armazenamento, e transforma toda a imutabilidade da feature numa promessa sobre código futuro.

---

## T-004 — Publicabilidade é leitura de `estado_do_marco`, com três recusas nomeadas

**Decisão**: o comando chama `estado_do_marco(edital=…, marco_id=…)` e exige duas condições:
`vigente.id == ato.id` e `obsoleto is False`. As recusas mapeiam a FR-004 uma a uma:

| Situação lida | Código | Mensagem |
|---|---|---|
| `vigente.id != ato.id` | `publication_act_superseded` | O ato foi sucedido; publique o sucessor |
| `obsoleto and recomputavel` | `publication_act_stale` | A regra ou o universo mudaram desde a emissão |
| `obsoleto and not recomputavel` | `publication_milestone_removed` | O marco não existe na norma vigente |

**Racional**: obsolescência na 015 é derivada, não gravada
(`classificacao/application/selectors.py:52-116`), e a função já distingue os três casos —
inclusive o marco removido por Retificação, que devolve `recomputavel=False` e a divergência
`regra_ausente`. Reimplementar a comparação aqui criaria a segunda regra de obsolescência, e a FR-001 é
explícita em que a publicação não copia a regra classificatória.

A decisão de domínio é absoluta (D-001, FR-005): não existe publicar mediante confirmação
adicional. As `divergencias` da 015 continuam sendo apresentadas ao operador como **informação** —
elas explicam a recusa —, e nenhuma delas é aviso superável.

---

## T-005 — Quatro frentes de concorrência, e uma delas exige bloqueio

**Decisão**:

1. **Duplo submit** — `reserve`/`finish` de `shared/idempotency.py`, com
   `operation="resultado:publicar:<ato_id>"`. Repetição devolve o desfecho da primeira.
2. **Dois pedidos distintos sobre o mesmo ato** — `uq_publicacao_por_ato_natureza` recusa no banco.
   A idempotência **não** cobre este caso: chaves diferentes são pedidos diferentes, e é a armadilha
   que a 015 já registrou.
3. **Projeção ou cadeia mudam entre a prévia e a confirmação** — `confirmacao_da_previa`, o
   `canonical_sha256` de `{ato_id, publicacao_anterior_id, projecao}`. Divergência é
   `409 publication_preview_stale`.
4. **Ato sucessor emitido enquanto a publicação confirma** — `select_for_update` na linha do
   `ProcessoSeletivo`, tomado **antes** de aferir publicabilidade.

**Racional da assinatura (3).** Ela não pode ser o `conteudo_publico_hash`: o conteúdo publicado
contém `publicado_em`, que só existe no POST, e um resumo calculado na prévia jamais coincidiria com
ele. São dois resumos, sobre materiais diferentes, porque respondem a perguntas diferentes.

Ficam **de fora** da assinatura a natureza e a autoridade: elas são escolha do operador, submetidas
no mesmo pedido, e não têm como ficar obsoletas — não existe leitura anterior delas a comparar. São
**validadas** como entrada, não assinadas. Fica **dentro** o `publicacao_anterior_id`, e é ele que
cobre o caso de outra pessoa publicar o mesmo marco no intervalo: a cadeia mudou, e gravar uma
sucessão a partir de uma ponta que já não é a ponta é exatamente o que a assinatura existe para
impedir.

**Racional do bloqueio (4).** É a frente que revalidação nenhuma resolve. `emitir_ordem` roda dentro
de `comando_de_comissao`, que faz `select_for_update` na linha do `ProcessoSeletivo` e a segura pela
transação inteira (`comissoes/application/__init__.py:48-63`). Sem tomar a **mesma** linha, os dois
comandos correm em paralelo:

```text
publicar:  afere → ato é vigente ✓ .................... grava a publicação de C1
emitir:    ................. grava C2, sucessor de C1
```

A aferição estava correta no instante em que ocorreu; o problema é o que aconteceu depois dela, e
transação isolada não impede a outra transação de existir. Tomar a linha antes de aferir serializa
os dois, e o perdedor encontra o mundo já mudado — a publicação recusa por ato sucedido, ou a
emissão sucede um ato já divulgado, que é legítimo.

O bloqueio é o mesmo objeto e a mesma granularidade que a 011 escolheu, e pela mesma razão: não há
linha única a bloquear quando o invariante lê vários agregados do Processo. O comando **não** passa
por `comando_de_comissao` — isso imporia autoridade de vínculo (T-006) —, mas toma o mesmo bloqueio
explicitamente.

`require_permission` corre **fora** da transação, e por isso `reserve` pode vir antes de executar —
é o padrão de `processos/application/commands.py`, e não o de `comando_de_comissao`, que reserva
depois porque a base dele é contextual e pode mudar sob os pés.

## T-006 — A autorização é capacidade, e não há trava de identidade

**Decisão**: `resultado:publicar`, acrescentada ao papel **Publicador** em
`interface/identidade.py:26`, ao lado de `edital:publicar` e `retificacao:publicar`. O comando não
passa por `comando_de_comissao`.

**Racional**: a D-004 separa os dois mecanismos de autoridade — a 015 autoriza por vínculo
(presidência da comissão), a 017 por capacidade. Passar pelo invólucro da comissão faria a
publicação exigir vínculo, que é exatamente o que a FR-026 nega.

**E não se replica a trava de identidade da publicação do Edital.** Lá,
`segregation_of_duties` recusa quem elaborou e homologou o mesmo Edital
(`publicacoes/application/publish_edital.py:493`), e faz sentido: os três atos são capacidades da
mesma cadeia, e concentrá-las é acúmulo de papéis. Aqui os dois atos vêm de sistemas de autorização
diferentes, e uma pessoa que presida a comissão **e** detenha `resultado:publicar` é uma
configuração institucional — decisão de quem provisiona papéis, não defeito a impedir no comando.
Impedir seria a 017 legislando sobre composição de responsabilidades, que não é dela.

---

## T-007 — O documento entra pela costura que já sustenta dois

**Decisão**: `divulgacao/infrastructure/documento.py`, no molde de
`inscricoes/infrastructure/comprovante_pdf.py:54-71` — monta uma `Composicao`, escreve as seções e
chama `render_documento(composicao, identificacao=…)`. A lista usa `_tabela`, com alinhamento à
direita para posição e pontuação.

**Racional**: a separação entre acumular texto e virar arquivo existe **porque** um segundo
documento apareceu, e está dita no docstring de `render_documento`
(`publicacoes/infrastructure/pdf.py:1899-1908`). O terceiro documento é o teste dessa extração. A
saída é determinística — sem data de criação embutida, sem identificador aleatório —, e é isso que
permite publicar o resumo do documento e esperar que ele confira.

Os bytes são gerados **dentro do comando de publicar** e persistidos, como `DocumentoPublicado`
faz. Gerar sob demanda economizaria armazenamento e devolveria a pergunta "o documento de hoje é o
mesmo de ontem?" para o código — que é a pergunta que a FR-062 responde com um hash.

**Consequência para o sequenciamento**: até a F4, publicações nascem sem documento. `DocumentoDoResultado`
é tabela própria com `OneToOne`, como `DocumentoPublicado`, e a ausência é naturalmente
representável — não há coluna anulável a limpar depois.

---

## T-008 — A página pública é do portal, e o endereço não colide

**Decisão**: `portal/urls.py` ganha `resultados/<uuid:publicacao_id>/` e
`resultados/<uuid:publicacao_id>/documento.pdf`.

**Racional**: o portal é o canal HTML público do projeto — a vitrine e o detalhe da seleção já
moram lá, e leem exclusivamente conteúdo publicado (`portal/views.py:1-11`). Os endereços de
`publicacoes/api/public_urls.py` são JSON, e entregar a FR-047 como endpoint JSON seria entregar
outra coisa.

Não há colisão com o `path("<uuid:edital_id>/", …)` que fecha o arquivo: `resultados` não casa com
`uuid`. O `.pdf` no fim do documento segue o precedente do comprovante
(`portal/urls.py`, `comprovante-pdf`) — é o que uma pessoa reconhece como arquivo para guardar.

A descobribilidade da FR-050 entra em `portal/views.selecao`: a página do Edital passa a listar as
publicações vigentes dos marcos daquele Edital. É a página que alguém já abre para conhecer a
seleção, e é onde ela procura o resultado.

---

## T-009 — A ação administrativa pende do ato, no lugar onde a interface já oferece o que fazer

**Decisão**: três rotas em `interface/urls.py`, penduradas no ato de ordenação, no molde exato das
rotas da 015 (`interface/urls.py:172-187`):

```text
editais/<edital_id>/marcos/<marco_id>/atos/<ato_id>/publicar       GET   prévia
editais/<edital_id>/marcos/<marco_id>/atos/<ato_id>/publicar       POST  confirmação
editais/<edital_id>/marcos/<marco_id>/publicacoes                  GET   histórico
```

E a oferta da ação na tela do ato (`views.ato_de_ordenacao`), condicionada a
`ator.can("resultado:publicar")`, no padrão de `_navegacao` (`interface/acoes.py:65-78`).

**Racional**: a rota pende do ato porque é dali que ela é alcançada e porque é o ato que a
autorização qualifica. E a condição na navegação é o que a FR-069 cobra: a auditoria da 015
registrou um achado inteiro — depois retratado — que existiu porque uma ação real não foi encontrada
por quem não tinha a permissão dela. Uma tela alcançável só por endereço decorado é uma capacidade
que o Princípio VI não considera entregue.

O catálogo declarativo de `interface/atos.py` já tem `exige_signatario` e `consequencias`, e a
prévia de publicação as usa; mas o catálogo é indexado por situação do **Edital**, e este ato pende
do ato de ordenação. A prévia é view própria, no molde de `praticar_ato_retificacao` — o terceiro
irmão de uma família que já tem três.

---

## T-010 — A projeção individual é tabela à parte, e não uma chave do conteúdo

**Decisão**: `conteudo_publico` guarda exclusivamente o que é divulgado. A situação de cada
participante considerado — inclusive de quem não recebeu posição — vai para `SituacaoDivulgada`,
tabela append-only com uma linha por Inscrição, apontando para a publicação.

**Racional**: a tensão a resolver é entre a FR-017 (quem não recebeu posição não é nomeado
publicamente) e a FR-059 (mas é informado na sua Área). A primeira tentativa foi guardar as duas
faces no mesmo registro, e ela **não fecha por duas razões**:

- **a fronteira deixaria de ser estrutural.** A view pública leria o registro inteiro, com o
  individual dentro, e a proteção passaria a ser o template não renderizar o que a view já tem em
  mãos. Isso é exatamente a "minimização por disciplina" que T-013 diz ser mais fraca — não dá para
  reivindicar minimização estrutural e carregar o dado assim mesmo;
- **o resumo provaria outra coisa.** `conteudo_publico_hash` é apresentado pela SC-004 como o resumo
  do conteúdo divulgado. Um hash sobre público mais privado não é isso, e o documento oficial
  imprimiria um número que não corresponde ao que ele contém.

**Isto não cria segunda fonte de verdade** (FR-058). As duas projeções nascem na **mesma
transação**, a partir do **mesmo ato imutável**, e a linha individual aponta para a publicação que a
originou. O que a FR-058 proíbe é uma fonte **viva** — ler `PosicaoNaOrdem` no acompanhamento, que
mudaria quando o ato fosse sucedido enquanto a publicação permanece histórica. `SituacaoDivulgada` é
congelada como a lista, e sucedida junto com ela.

**Alternativas consideradas**: as duas faces no mesmo `BinaryField` — descartada acima; ler
`PosicaoNaOrdem` no acompanhamento — a segunda fonte viva que a FR-058 nomeia; não informar o não
classificado — contraria a FR-059, e a D-006 é explícita em que não ser nomeado publicamente não é
o mesmo que não ser informado.

## T-011 — Quatro registros fora do app, e o teste só enxerga o que foi registrado

**Decisão**: `"divulgacao"` entra em `APPS` e em `TRIGGERS_POR_APP` com as quatro triggers —
`publicacao_resultado_append_only`, `situacao_divulgada_append_only`,
`documento_do_resultado_append_only` e `publicacao_resultado_coerente`
(`tests/migrations/test_migrations.py:17-38`); as **três** tabelas entram em `TABELAS_APPEND_ONLY`
(`seguranca/papeis.py:26-48`).

**Racional**: a imutabilidade tem três camadas independentes, e nenhuma depende da aplicação se
comportar — `save`/`delete` no modelo, a trigger no banco e o privilégio ausente no papel de
runtime. Esquecer o registro não quebra nada em execução: quebra a **prova**, que é o que o teste
estrutural existe para dar.

As três de imutabilidade são absolutas, sem a condicionalidade ao estado final que `Retificacao` e
`AlteracaoNormativa` exigem — publicação não tem estado em curso. A quarta é de coerência, no molde
de `resultado_etapa_coerente`: no `INSERT`, confere que o predecessor pertence ao mesmo marco e que
a natureza não regride.

## T-012 — Naturezas como `TextChoices`, e o rótulo vem do domínio

**Decisão**: `PRELIMINAR` e `DEFINITIVA` como `TextChoices` no modelo; o texto institucional
("Resultado preliminar", "Resultado definitivo") é composto no `conteudo` congelado, e não derivado
do enum na renderização.

**Racional**: a FR-013 proíbe enum canônico como texto institucional, e a maneira de garantir isso
não é traduzir bem na template — é o texto já estar congelado no conteúdo publicado, como tudo o
mais. `HOMOLOGADA` não existe: a D-003 a manteve fora, e acrescentar o valor ao enum "para o
futuro" seria a spec afirmando um ato que ela não implementa.

---

## T-013 — A superfície pública não tem consulta que alcance dado pessoal

**Decisão**: `portal/views.resultado` consulta a publicação e a sua cadeia, e desserializa
`conteudo_publico`. Nenhuma consulta alcança `Inscricao`, `PosicaoNaOrdem`, `VersaoConsolidada` ou
`SituacaoDivulgada`.

**Racional**: é a consequência de T-003 e T-010, e vale registrar como propriedade de segurança
antes de qualquer coisa. Uma página que **pode** ler dado pessoal e confia num serializer para
filtrar é uma página a uma linha de distância de vazar; uma página que não tem a consulta não tem a
linha. O Princípio III pede minimização, e minimização estrutural é mais forte que minimização por
disciplina — e é justamente por isso que o individual não podia viajar dentro do mesmo registro.

**O que se afirma sobre custo, e o que não se afirma.** O número de consultas é constante: a
publicação, e a cadeia para saber se ela ainda é a vigente — uma publicação histórica precisa
percorrê-la, e é honesto contar isso. O **custo** não é constante: desserializar o conteúdo, montar
o HTML e transmiti-lo crescem com o número de posições, como em qualquer lista. O teste de
desempenho afirma derivada zero em **consultas** entre 10 e 1.000 posições, no molde de
`tests/performance/test_public_queries.py`, e não promete tempo invariável — o que seria falso.

O preço fica na composição, proporcional ao universo e paga **uma vez**, dentro do comando: uma
consulta de posições, uma de inscrições (nome e protocolo) e a leitura do `content` da versão que o
ato cita — resolvida antes do laço, como `calcular_ordem` já faz.
