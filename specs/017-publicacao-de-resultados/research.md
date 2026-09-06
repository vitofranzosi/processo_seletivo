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
```

Vigente é a publicação que ninguém sucedeu — `sucessoras__isnull=True` —, e não existe coluna.

**Racional**: é a forma que `AtoDeOrdenacao` já usa (`classificacao/models.py:44-61`), e ela não é
estilo. A política de papéis revoga `UPDATE` das tabelas append-only (`seguranca/papeis.py`), então
um booleano `vigente` seria impossível de virar em produção — o desenho não é preferido, é o único
que o banco permite. As duas constraints também são o que impede duas publicações concorrentes de
nascerem raízes do mesmo marco (FR-040).

A cadeia é **uma por marco**, com `natureza` como atributo (D-007): a definitiva sucede a
preliminar. Uma cadeia por natureza permitiria duas vigentes simultâneas para o mesmo marco.

**Alternativas consideradas**: coluna `vigente` com atualização em transação — inexecutável sob a
política de privilégios; ordem crescente tipo `publication_order` como em `Publicacao` — resolve
ordenação, não sucessão, e não diz quem sucedeu quem.

---

## T-003 — A publicação congela a projeção, não o ponteiro

**Decisão**: `conteudo` (bytes canônicos) + `conteudo_hash` (sha256), no molde de
`Publicacao.canonical_content`/`content_hash`, gravados no ato de publicar.

**Racional**: e o racional **não** é a estabilidade dos rótulos. `VersaoConsolidada` é append-only,
e ler `ato.versao.content` na hora de renderizar já devolveria sempre os mesmos nomes.

O que precisa ser congelado é a **projeção**: quem entra na lista (FR-017), o que de cada linha
atravessa a fronteira (FR-018 a FR-020), como o empate é dito (FR-014), como a natureza é afirmada
(FR-016). São decisões desta feature, escritas em código desta feature. Compor na leitura faria
qualquer correção futura numa delas reescrever, em silêncio, tudo o que já foi divulgado — e a
I-005 diz o contrário.

Congelar também é o que dá conteúdo à SC-004: existe um resumo publicado a conferir, e ele é o mesmo
que o documento imprime (FR-061). `canonical_sha256` já faz a canonização — `sort_keys`,
`separators` sem espaço, NFC (`shared/canonical.py:86-94`) — e é a mesma função que a publicação do
Edital usa.

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
`regra_ausente`. Reimplementar a comparação aqui criaria a segunda regra de obsolescência que a
FR-068 proíbe.

A decisão de domínio é absoluta (D-001, FR-005): não existe publicar mediante confirmação
adicional. As `divergencias` da 015 continuam sendo apresentadas ao operador como **informação** —
elas explicam a recusa —, e nenhuma delas é aviso superável.

---

## T-005 — Três frentes de concorrência, todas com precedente

**Decisão**:

1. **Duplo submit** — `reserve`/`finish` de `shared/idempotency.py`, com
   `operation="resultado:publicar:<ato_id>"`. Repetição devolve o desfecho da primeira.
2. **Obsolescência entre prévia e confirmação** — a confirmação carrega
   `confirmacao_da_previa`, o `canonical_sha256` do conteúdo composto na prévia. Divergência é
   `409 publication_preview_stale`.
3. **Duas publicações concorrentes do mesmo marco** — as constraints de T-002, que recusam a
   segunda raiz no banco.

**Racional**: os três mecanismos existem e resolvem coisas diferentes, e é por isso que são três. A
idempotência cobre o mesmo pedido repetido; ela **não** cobre dois pedidos distintos, porque chaves
diferentes são pedidos diferentes — a armadilha que a 015 já registrou. A assinatura cobre a janela
entre ler e confirmar, e é literalmente o `confirmacao_do_calculo` de `emitir_ordem`
(`classificacao/application/emissao.py`) aplicado ao conteúdo em vez de à proposta. A constraint
cobre o que passa pelas duas.

`require_permission` corre **fora** da transação, e por isso `reserve` pode vir antes de executar —
é o padrão de `processos/application/commands.py`, e não o de `comando_de_comissao`, que reserva
depois porque a base dele é contextual e pode mudar sob os pés.

---

## T-006 — A autorização é capacidade, e não há trava de identidade

**Decisão**: `resultado:publicar`, acrescentada ao papel **Publicador** em
`interface/identidade.py:26`, ao lado de `edital:publicar` e `retificacao:publicar`. O comando não
passa por `comando_de_comissao`.

**Racional**: a D-004 separa os dois mecanismos de autoridade — a 015 autoriza por vínculo
(presidência da comissão), a 017 por capacidade. Passar pelo invólucro da comissão faria a
publicação exigir vínculo, que é exatamente o que a FR-025 nega.

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
mesmo de ontem?" para o código — que é a pergunta que a FR-060 responde com um hash.

**Consequência para o sequenciamento**: até a F4, publicações nascem sem documento. `DocumentoDoResultado`
é tabela própria com `OneToOne`, como `DocumentoPublicado`, e a ausência é naturalmente
representável — não há coluna anulável a limpar depois.

---

## T-008 — A página pública é do portal, e o endereço não colide

**Decisão**: `portal/urls.py` ganha `resultados/<uuid:publicacao_id>/` e
`resultados/<uuid:publicacao_id>/documento.pdf`.

**Racional**: o portal é o canal HTML público do projeto — a vitrine e o detalhe da seleção já
moram lá, e leem exclusivamente conteúdo publicado (`portal/views.py:1-11`). Os endereços de
`publicacoes/api/public_urls.py` são JSON, e entregar a FR-045 como endpoint JSON seria entregar
outra coisa.

Não há colisão com o `path("<uuid:edital_id>/", …)` que fecha o arquivo: `resultados` não casa com
`uuid`. O `.pdf` no fim do documento segue o precedente do comprovante
(`portal/urls.py`, `comprovante-pdf`) — é o que uma pessoa reconhece como arquivo para guardar.

A descobribilidade da FR-048 entra em `portal/views.selecao`: a página do Edital passa a listar as
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
autorização qualifica. E a condição na navegação é o que a FR-067 cobra: a auditoria da 015
registrou um achado inteiro — depois retratado — que existiu porque uma ação real não foi encontrada
por quem não tinha a permissão dela. Uma tela alcançável só por endereço decorado é uma capacidade
que o Princípio VI não considera entregue.

O catálogo declarativo de `interface/atos.py` já tem `exige_signatario` e `consequencias`, e a
prévia de publicação as usa; mas o catálogo é indexado por situação do **Edital**, e este ato pende
do ato de ordenação. A prévia é view própria, no molde de `praticar_ato_retificacao` — o terceiro
irmão de uma família que já tem três.

---

## T-010 — O snapshot tem duas faces, e a página pública renderiza uma

**Decisão**: o conteúdo congelado guarda `publico` — as linhas divulgadas — e `individual` — um
índice por Inscrição com a situação de cada participante considerado, inclusive quem não recebeu
posição. A página pública lê apenas `publico`; a Área do Candidato lê `individual` na chave da
própria Inscrição.

**Racional**: é a tensão entre a FR-017 (quem não recebeu posição não é nomeado publicamente) e a
FR-058 (mas é informado na sua Área). Resolvê-la lendo `PosicaoNaOrdem` no acompanhamento criaria a
segunda fonte de verdade que a FR-056 proíbe — e pior, uma fonte **viva**, que mudaria quando o ato
fosse sucedido, enquanto a publicação permanece histórica.

Com as duas faces no mesmo snapshot, a FR-056 fica literalmente verdadeira: o resumo individual e a
lista pública são duas vistas sobre os mesmos bytes, congelados no mesmo instante, com o mesmo
resumo. E a I-004 fica estrutural: antes da publicação não existe `individual` para consultar.

O `individual` é dado interno e não atravessa a fronteira pública — nenhum caminho do
`portal/views.resultado` o alcança, e o teste de contrato afirma isso sobre o HTML renderizado, e
não sobre a intenção do código.

---

## T-011 — Três registros fora do app, e o teste só enxerga o que foi registrado

**Decisão**: `"divulgacao"` entra em `APPS` e em `TRIGGERS_POR_APP` com
`("publicacao_resultado_append_only", "documento_do_resultado_append_only")`
(`tests/migrations/test_migrations.py:17-38`); as duas tabelas entram em `TABELAS_APPEND_ONLY`
(`seguranca/papeis.py:26-48`).

**Racional**: a imutabilidade tem três camadas independentes, e nenhuma depende da aplicação se
comportar — `save`/`delete` no modelo, a trigger no banco e o privilégio ausente no papel de
runtime. Esquecer o registro não quebra nada em execução: quebra a **prova**, que é o que o teste
estrutural existe para dar. As duas triggers são absolutas, sem a condicionalidade ao estado final
que `Retificacao` e `AlteracaoNormativa` exigem — publicação não tem estado em curso.

---

## T-012 — Naturezas como `TextChoices`, e o rótulo vem do domínio

**Decisão**: `PRELIMINAR` e `DEFINITIVA` como `TextChoices` no modelo; o texto institucional
("Resultado preliminar", "Resultado definitivo") é composto no `conteudo` congelado, e não derivado
do enum na renderização.

**Racional**: a FR-013 proíbe enum canônico como texto institucional, e a maneira de garantir isso
não é traduzir bem na template — é o texto já estar congelado no conteúdo publicado, como tudo o
mais. `HOMOLOGADA` não existe: a D-003 a manteve fora, e acrescentar o valor ao enum "para o
futuro" seria a spec afirmando um ato que ela não implementa.

---

## T-013 — A superfície pública não tem caminho de leitura para dado pessoal

**Decisão**: `portal/views.resultado` faz **uma** consulta — a publicação por id — e renderiza o
`publico` desserializado. Nenhuma junção com `Inscricao`, `PosicaoNaOrdem` ou `VersaoConsolidada`.

**Racional**: é a consequência de T-003, e vale registrar como propriedade de segurança e não como
otimização. Uma página que **pode** ler `Inscricao` e confia num serializer para filtrar é uma
página a uma linha de distância de vazar; uma página que não tem a consulta não tem a linha. O
Princípio III pede minimização, e minimização estrutural é mais forte que minimização por
disciplina.

O ganho de desempenho vem junto e é medível: o custo da página não varia entre 10 e 1.000 posições,
e o teste afirma derivada zero no molde de `tests/performance/test_public_queries.py`.

O preço é a composição, que é proporcional ao universo e acontece uma vez, dentro do comando: uma
consulta de posições, uma de inscrições (nome e protocolo) e a leitura do `content` da versão que o
ato cita — resolvida antes do laço, como `calcular_ordem` já faz.
