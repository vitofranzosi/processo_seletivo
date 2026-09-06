# Feature Specification: Publicação de Resultados

**Feature Branch**: `claude/spec-017-publicacao-resultados-605ce0`

**Created**: 2026-09-06

**Status**: Draft

**Input**: Um resultado oficialmente constituído deve poder ser publicado pela autoridade
competente e consultado posteriormente exatamente como foi divulgado, sem recalcular seu conteúdo
e sem reescrever publicações históricas. Para o candidato: quando a instituição publicar um
resultado que lhe diga respeito, ele deve conseguir encontrá-lo e compreender sua situação sem
depender de planilha, PDF produzido manualmente ou consulta a outro sistema.

A 017 não calcula resultado, não classifica e não decide recurso. Ela **publica um ato já
existente**, e fecha a borda institucional do primeiro vertical: a instituição chegou a uma decisão
classificatória e a tornou oficialmente acessível às pessoas interessadas.

---

## 1. O que a 015 entregou, e que a 017 herda como contrato

Esta feature começa depois do ato de ordenação e não redefine nenhum de seus conceitos. O que
segue não é aspiração: é o que já existe no repositório, e é o chão sobre o qual a 017 é
planejada.

- **`AtoDeOrdenacao` é o ato de resultado constituído.** Ele cita `edital`, `perfil_id`,
  `marco_id`, a `VersaoConsolidada` sob a qual foi emitido, o `universo` que considerou, quem o
  emitiu e quando. Nasce imutável — `save` recusa alteração, `delete` recusa exclusão — e a tabela
  está na política de privilégios como append-only.
- **A vigência não é coluna.** Sucessão é `ato_anterior` apontando para o antecessor, com
  `uq_ato_sucessor_unico` garantindo cadeia linear; **vigente é o ato que ninguém sucedeu**. Não
  existe `vigente = bool` em lugar nenhum desta linhagem, e não pode existir: o papel de runtime
  não tem `UPDATE` nas tabelas append-only.
- **`PosicaoNaOrdem` é o snapshot do ato.** Guarda `posicao` (nula para quem foi considerado e não
  a recebeu, com `motivo` obrigatório nesse caso), `pontuacao_combinada`, `modalidade_id`,
  `consequencia`, `empate_residual` e a proveniência `desempate` — uma lista por critério com
  `criterionId`, `order`, `type`, `separated` **e `value`**, que é o valor do fato pessoal.
- **Calcular não é emitir.** `calcular_ordem` é read-only e não grava ato, posição nem auditoria;
  só `emitir_ordem` constitui o ato. **Não existe proposta persistida.**
- **Obsolescência é derivada, não gravada.** `estado_do_marco` reproduz a proposta sob a versão
  vigente e a compara com o `universo` do ato, devolvendo `obsoleto`, `recomputavel` e as
  `divergencias`. Quando o marco não existe mais na versão vigente, devolve `obsoleto=True` e
  `recomputavel=False`.
- **Revalidar entre leitura e ato já tem forma.** `emitir_ordem` exige `confirmacao_do_calculo`, a
  assinatura da proposta que o operador leu, e recusa com `409 ordering_act_already_exists` ou
  `422 stale_ordering_calculation` quando o mundo mudou embaixo da tela.
- **Idempotência já tem forma.** `shared/idempotency.reserve` + `finish`, com a repetição
  devolvendo o desfecho original em vez de reexecutar. `processos/application/commands.py` é o
  precedente de comando **autorizado por permissão** que reserva antes de executar.
- **A autoridade da 015 é de vínculo, não de papel.** `emitir_ordem` roda dentro de
  `comando_de_comissao`, que autoriza por `pode_gerir_comissao` — a presidência da comissão do
  Processo. `classificacao:emitir` não aparece no mapa de papéis, e é assim de propósito.

E o que a linhagem do Edital já entregou, e que a 017 herda como padrão:

- **"Publicação", sem qualificador, já significa outra coisa.** `publicacoes.Publicacao` é a
  publicação do **Edital**, com `canonical_content`, `content_hash`, `publication_order`,
  `published_by` e a autoridade signatária (`signatory_id`, `signatory_name`, `signatory_role`)
  persistida no ato. É append-only.
- **`publicacoes.Homologacao` existe, e é ato distinto de `Publicacao`**, com permissão própria
  (`edital:homologar` × `edital:publicar`) e segregação de funções: uma pessoa não elabora,
  homologa e publica o mesmo Edital.
- **`DocumentoPublicado`** guarda os bytes do PDF e o `document_hash`, e o renderizador
  (`publicacoes/infrastructure/pdf.py`) é próprio, sem dependência externa, com métricas base-14,
  brasão e `WinAnsiEncoding`. Ele já está separado em duas camadas: `Composicao` acumula o texto e
  `render_documento` o pagina e monta o arquivo — e essa separação existe porque **um segundo
  documento já a usa**, o comprovante de inscrição. A saída é determinística, sem data de criação
  embutida, que é o que permite publicar o resumo de um documento e esperar que ele confira.
- **A resolução de rótulos para o documento oficial já existe**, e é recente: a correção de
  E2E15-004/005/008 ensinou o renderizador a resolver `stageId` e `factId` para os nomes
  publicados, a dizer o modo de arredondamento por extenso e a nomear o critério de desempate
  inteiro. Junto veio a política do alvo irresolvível — `ETAPA_NAO_IDENTIFICADA`,
  `FATO_NAO_IDENTIFICADO` —, que diz a lacuna em vez de imprimir identificador.
- **O catálogo de autoridades** (`publicacoes/domain/autoridades.py`) oferece nome, cargo e
  identificador escolhidos por chave — ninguém digita UUID de signatário.
- **O canal público em HTML é o `portal/`**; os endereços públicos de `publicacoes/api/` são JSON.
- **A Área do Candidato já existe** em `portal/views.acompanhamento`, e hoje
  `_fatos_da_participacao` devolve **apenas o envio da inscrição**, recusando explicitamente
  inventar fato sobre a pessoa. O candidato hoje não vê resultado nenhum.

> O resultado existe, é oficial e é imutável; falta a instituição divulgá-lo — e divulgar é outro
> ato, praticado por outra autoridade, sobre um conteúdo que já está pronto.

---

## 2. Decisões fechadas antes do planejamento

### D-001 — Publicar não recalcula o conteúdo; aferir publicabilidade, sim

A contradição que esta decisão resolve é real: exigir que a publicação nunca execute a regra
classificatória e, ao mesmo tempo, que ela recuse ato obsoleto é impossível — obsolescência, na
015, **só existe por reprodução**.

A distinção é entre duas perguntas diferentes feitas ao mesmo motor:

```text
conteúdo da publicação      ←  AtoDeOrdenacao imutável + PosicaoNaOrdem
                               (nunca recalculado, nem na publicação, nem anos depois)

checagem de publicabilidade ←  reprodução do estado classificatório no instante da confirmação
                               (obrigatória, descartada em seguida, não constitui ato)
```

A reprodução responde "este ato ainda representa o estado classificatório vigente?" e **nada mais**.
Ela nunca alimenta o que é divulgado, nunca corrige o snapshot, nunca é persistida na publicação.
Publicabilidade é condição aferida no instante do ato — **não é atributo da publicação**, e não é
reavaliada quando alguém abre uma publicação histórica.

### D-002 — A V1 publica apenas `AtoDeOrdenacao`

`ResultadoEtapa` é por Inscrição × Etapa. Não existe ato coletivo consolidado da Etapa: consolidar
opera linha a linha, e não há agregado a referenciar. Publicar resultado de Etapa exigiria
**constituir** o ato coletivo que hoje não existe — que é exatamente o que esta feature não faz.

Portanto a 017 não cria abstração `Publicavel`, não generaliza sobre dois casos quando há um, e não
antecipa o segundo. Se a divulgação de resultado de Etapa for necessária, ela começa por uma
feature que **constitua** esse ato, e a publicação dele vem depois, com contrato próprio.

### D-003 — Homologação de resultado fica fora da 017

O domínio já demonstrou, na linhagem do Edital, que homologação e publicação são atos distintos,
com autoridades e permissões distintas. Não se assume que "definitiva" e "homologada" sejam
sinônimos, e não se resolve a diferença aqui: a 017 conhece **duas** naturezas, `PRELIMINAR` e
`DEFINITIVA`, e não implementa homologação de resultado.

Se a homologação do resultado se mostrar ato necessário, ela nasce com contrato próprio, autoridade
própria e trilha própria — e a publicação de um resultado homologado será, então, mais uma
publicação nesta mesma cadeia, não uma mutação da anterior.

### D-004 — A autoridade de publicar é capacidade institucional, não consequência da autoria

Comissão constitui o resultado; autoridade publicadora o divulga. São **mecanismos de autorização
diferentes**, e não apenas capacidades diferentes:

```text
015  emitir   →  vínculo    →  presidência da comissão do Processo
017  publicar →  capacidade →  `resultado:publicar`, no mapa de papéis
```

Isso reaproveita literalmente a arquitetura que o Edital já usa e evita concentrar produzir e
publicar na mesma origem de autoridade. Não se proíbe tecnicamente para sempre que uma mesma pessoa
detenha ambos os papéis: proíbe-se que a autorização para publicar **derive** de ter emitido. Ser
membro da comissão, ser presidente ou ser avaliador não concede publicar.

Consequência de desenho: o comando de publicar **não** passa por `comando_de_comissao`. Ele segue o
precedente de comando autorizado por permissão, com `require_permission` fora da transação e
`reserve` dentro dela.

### D-005 — Identificação pública é nome completo mais protocolo, e nada além

A publicação não despeja os campos da classificação. Publica-se **nome completo + protocolo**.

Não se publica CPF (nem parcial), e-mail, telefone, documentos, `identity_subject`, identificador
de inscrição, hashes internos ou qualquer campo que exista para uso interno.

Sobre desempate, duas coisas diferentes:

- **que houve empate residual**: publicável, e obrigatório — é a posição compartilhada;
- **o valor pessoal que separou ou deixou de separar**: não publicável. Data de nascimento, meses
  de experiência e demais fatos declarados ficam fora da fronteira institucional.

A proveniência completa continua existindo e continua consultável na tela administrativa por quem
tem autorização. O que muda é apenas o que atravessa a fronteira do público.

### D-006 — Quem não recebeu posição não é nomeado na publicação da V1

`PosicaoNaOrdem` guarda também quem foi considerado e **não** recebeu posição, com o motivo
("eliminada por nota", "eliminada na Etapa 1"). A V1 publica **a ordem**: as posições atribuídas.

Publicar nominalmente a eliminação de uma pessoa é decisão institucional sobre dado pessoal que
nenhuma norma do Edital declarou até aqui, e o default conservador é não a tomar por conveniência
de implementação. Não ser nomeado publicamente não é o mesmo que não ser informado: o motivo
continua disponível ao próprio candidato na sua Área (FR-059) e à administração na proveniência.

Se um Edital vier a exigir a divulgação nominal dos não classificados, isso é conteúdo normativo a
declarar — e passa a ser lido da versão publicada, não decidido no renderizador.

### D-007 — A publicação é append-only, e vigência é derivada da sucessão

Mesma forma da 015, pela mesma razão e sob a mesma restrição de privilégios:

```text
Classificação C1 → Publicação P1 (preliminar)
                        ↑ publicacao_anterior
Classificação C2 → Publicação P2 (definitiva)     vigente = quem ninguém sucedeu
```

**Uma única cadeia por marco classificatório**, com a natureza como atributo da publicação e não
como eixo de cadeia. A alternativa — uma cadeia por natureza — permitiria duas publicações
simultaneamente vigentes para o mesmo marco e reintroduziria exatamente a ambiguidade que a
concorrência precisa impedir.

Não existe coluna de vigência, não existe despublicação, não existe `UPDATE`. Preliminar não vira
definitiva: nasce outra publicação, e a anterior permanece íntegra.

**Um mesmo ato pode originar mais de uma publicação — uma por natureza.** Um resultado preliminar
contra o qual ninguém recorreu, ou cujos recursos não alteraram a ordem, é publicado como definitivo
sem que exista ato novo a emitir; exigir a emissão de um sucessor idêntico só para poder publicá-lo
faria a 015 registrar uma sucessão que não sucedeu nada. O que não cabe é a mesma natureza duas
vezes sobre o mesmo ato: isso é duplicidade, e o banco a recusa (FR-039).

E a ordem entre naturezas tem sentido único: uma publicação preliminar não sucede uma definitiva.

### D-008 — Não há rascunho persistente; a prévia é derivada

A prévia é composta a partir do ato imutável, pela mesma função que compõe o conteúdo publicado.
Visualizá-la não grava linha, não reserva identidade e não constitui ato administrativo.

Persistir rascunho traria ciclo de vida (criar, editar, abandonar, expirar), tela de gestão e
cancelamento — estrutura inteira para um requisito de preparação editorial que ninguém declarou.
Ela nasce quando houver o caso que a justifique.

### D-009 — O nome do agregado é `PublicacaoResultado`

"Publicação", sem qualificador, continua significando a publicação do Edital, em todo o código e em
toda a interface. O ato desta feature é **Publicação de Resultado**, e a distinção é de linguagem
ubíqua, não de conveniência de nomenclatura: são atos diferentes, sobre objetos diferentes, por
autoridades que podem ser diferentes.

---

## 3. Contratos herdados e reuso obrigatório

Esta seção existe para que o planejamento não construa infraestrutura paralela àquela que o
repositório já consolidou. Cada item abaixo é uma obrigação, não uma sugestão.

| O que | De onde | O que isso proíbe |
|---|---|---|
| Append-only e sucessão sem coluna de vigência | `classificacao/models.py`, `seguranca/papeis.py` | `vigente = BooleanField`, `UPDATE`, exclusão |
| A nova tabela entra em `TABELAS_APPEND_ONLY` | `seguranca/papeis.py` | tabela histórica fora da política de privilégios |
| Idempotência por `reserve` + `finish` | `shared/idempotency.py` | chave de idempotência própria, `get_or_create` como sucedâneo |
| Revalidação entre prévia e confirmação | `confirmacao_do_calculo` em `classificacao/application/emissao.py` | confirmar sem reler, ou reler sem comparar |
| Catálogo de autoridades signatárias | `publicacoes/domain/autoridades.py` | cadastro novo de autoridade, UUID digitado à mão |
| `Composicao` + `render_documento` | `publicacoes/infrastructure/pdf.py` | biblioteca de PDF nova, dependência externa, renderizador próprio |
| Resolução de rótulo e política do alvo ausente | idem, pós E2E15-004/005/008 | segunda tradução de enum, UUID impresso como lacuna |
| Trilha de auditoria existente | `avaliacoes/application/trilha.auditar` | log paralelo, tabela de eventos própria |
| Portal Django para a página pública | `portal/` | endpoint JSON apresentado como página pública |
| Acompanhamento como extensão aditiva | `portal/views.acompanhamento`, `_fatos_da_participacao` | segunda fonte de verdade do resultado do candidato |
| UUID pode estar no endereço, nunca na linguagem | padrão dos endereços públicos existentes | slug inventado; e UUID como texto institucional |

---

## 4. Problema

O produto produz a classificação e não a comunica. A auditoria exploratória do ciclo completo
registrou a borda exata: o candidato nunca vê posição, o resultado não tem página, não tem
documento e não tem endereço — e o próprio PDF do Edital promete recurso sem que exista meio de
divulgar aquilo contra o que se recorreria.

Um ato pode existir internamente sem estar publicado, e isso é correto. O que falta é o segundo
ato, que responde a uma pergunta diferente da primeira:

```text
Qual era o resultado?              →  AtoDeOrdenacao          (existe)
Quando e como a instituição
o tornou público?                  →  PublicacaoResultado     (não existe)
```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Publicar um resultado constituído (Priority: P1)

Como autoridade publicadora, quero selecionar um ato de ordenação emitido, conferir exatamente o
que será divulgado e confirmar a publicação, para que o resultado se torne ato público.

**Por que P1**: sem ela nada mais desta feature existe.

**Fluxo**:

```text
ato emitido → o sistema verifica que ele ainda é publicável → prévia composta do ato imutável
→ escolha da natureza e da autoridade signatária → confirmação → PublicacaoResultado
```

**Cenários de aceitação**:

1. **Dado** um ato de ordenação emitido e vigente, **quando** a autoridade publicadora abre a
   publicação, **então** vê a prévia com título, Processo/Edital, marco, natureza, ato de origem,
   autoridade signatária e o conteúdo exato a divulgar — e nada foi gravado.
2. **Dado** que a prévia está correta, **quando** a autoridade confirma, **então** nasce uma
   publicação com autor, instante, autoridade signatária e referência ao ato, imediatamente
   consultável.
3. **Dado** que a confirmação foi enviada duas vezes, **quando** a segunda chega, **então** o
   sistema devolve o desfecho da primeira e existe **uma** publicação.
4. **Dado** que o ato ficou obsoleto entre a prévia e a confirmação, **quando** a autoridade
   confirma, **então** a publicação é recusada com a razão nomeada, e nada foi publicado.
5. **Dado** um ator sem `resultado:publicar` — inclusive o presidente da comissão que emitiu o ato
   —, **quando** tenta publicar, **então** a operação é recusada.
6. **Dado** um ato emitido e um ator com a capacidade, **quando** ele abre o ato, **então** a ação
   de publicar lhe é oferecida ali mesmo; a quem não tem a capacidade, ela não aparece.

### User Story 2 — Consultar o resultado publicado (Priority: P1)

Como qualquer pessoa interessada, quero abrir o resultado publicado por um endereço estável e
entender que resultado é, de qual Edital, quando foi publicado e se é a versão vigente.

**Por que P1**: é a metade pública do ato; sem ela, publicar não publica nada.

**Cenários de aceitação**:

1. **Dado** o endereço de uma publicação, **quando** alguém o abre sem estar autenticado, **então**
   vê o resultado com posições, nomes e protocolos, rótulos institucionais e o instante da
   publicação.
2. **Dado** um empate residual, **quando** a lista é apresentada, **então** as posições
   compartilhadas aparecem como tais (1º, 2º, 3º, 3º) e nenhum desempate é inventado.
3. **Dado** que a publicação foi sucedida por outra, **quando** alguém abre a antiga, **então** a
   página diz que ela foi sucedida e oferece o caminho para a vigente — sem alterar o conteúdo
   histórico.
4. **Dado** um telefone de 375 px, **quando** a página é aberta, **então** não há rolagem
   horizontal da página.
5. **Dado** alguém que não conhece o endereço da publicação, **quando** abre a página pública do
   Edital, **então** encontra ali o resultado publicado vigente.

### User Story 3 — Encontrar o resultado na própria Inscrição (Priority: P1)

Como candidato, quero que o resultado que me diz respeito apareça dentro da minha Inscrição, para
não ter de procurar o Edital de novo nem descobrir por fora que houve publicação.

**Por que P1**: é a validação de produto da feature — o resultado finalmente chega à pessoa.

**Cenários de aceitação**:

1. **Dado** que existe classificação emitida e **nenhuma** publicação, **quando** o candidato abre
   o acompanhamento, **então** não há qualquer sinal de resultado.
2. **Dado** que a publicação existe e contempla a Inscrição, **quando** o candidato abre o
   acompanhamento, **então** vê a natureza, sua posição, sua pontuação e o caminho para o resultado
   completo.
3. **Dado** que a publicação foi sucedida, **quando** o candidato abre o acompanhamento, **então**
   é levado à publicação vigente.
4. **Dado** um candidato que foi considerado e não recebeu posição, **quando** abre o
   acompanhamento depois da publicação, **então** vê a sua situação e o motivo — sem que seu nome
   apareça na publicação.

### User Story 4 — Documento oficial (Priority: P2)

Como instituição, quero um documento imprimível do resultado publicado, para instruir processo,
arquivar e responder a quem exigir a forma documental.

**Cenários de aceitação**:

1. **Dado** uma publicação concluída, **quando** o documento é obtido, **então** ele traz
   Processo/Edital, marco, natureza, ato de origem, data e hora, autoridade signatária, o conteúdo
   da classificação e o resumo criptográfico do que foi publicado.
2. **Dado** que o Edital foi retificado depois da publicação, **quando** o documento é obtido de
   novo, **então** ele é o mesmo documento — nada é regenerado a partir do estado atual.

### User Story 5 — Histórico e sucessão (Priority: P2)

Como gestão ou auditoria, quero ver todas as publicações de um marco, com natureza, instante, autor
e situação, para saber o que foi divulgado, quando, e o que vale hoje.

**Cenários de aceitação**:

1. **Dado** um marco com publicação preliminar sucedida por definitiva, **quando** a lista é
   aberta, **então** as duas aparecem, com a vigente identificada e a anterior marcada como
   sucedida.
2. **Dado** que a informação de vigência é apresentada, **quando** alguém a lê sem distinguir
   cores, **então** a situação continua legível.

### Edge Cases

- Ato cujo marco foi **removido** por Retificação: não é publicável (não é reproduzível, logo não é
  aferível como vigente), e a recusa diz isso.
- Ato **sucedido** por outro: não é publicável; o caminho é publicar o sucessor.
- Ato **divergente** da regra ou do universo vigentes: não é publicável; o caminho é emitir ato
  sucessor na 015 e publicar aquele.
- Duas abas publicando o mesmo ato: uma publicação, e a segunda recebe o desfecho da primeira.
- **Ato sucessor emitido enquanto a publicação confirma**: os dois atos disputam o mesmo marco, e
  revalidar dentro da transação não basta sem serialização — a publicação não pode terminar
  divulgando um ato que deixou de ser vigente entre a aferição e a gravação.
- Duas publicações produzidas concorrentemente para o mesmo marco: a cadeia recusa a segunda raiz.
- Publicação sem nenhuma posição atribuída (todos eliminados): publicável, com a lista vazia dita
  explicitamente em vez de página em branco.
- Candidato cuja Inscrição não está no universo do ato: nada aparece no acompanhamento dele.
- Candidato contemplado por publicações de **dois marcos** — a intermediária e a final: as duas
  aparecem na sua Área, nomeadas pelo marco. Esconder a intermediária seria o sistema decidindo qual
  ato administrativo importa.
- Publicação preliminar cujo Edital não declara prazo de recurso: não se inventa prazo nem botão.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Objeto da publicação e publicabilidade

- **FR-001** — A publicação referencia um `AtoDeOrdenacao` existente pela sua identidade; ela não
  copia a regra classificatória nem constitui resultado.
- **FR-002** — Somente ato emitido é publicável. A proposta calculada não possui identidade
  persistida e é, por construção, inalcançável pela ação de publicar.
- **FR-003** — A publicabilidade é aferida no instante da confirmação, reproduzindo o estado
  classificatório vigente naquele instante.
- **FR-004** — São impublicáveis: ato que já foi sucedido; ato cujo universo ou cuja regra divergem
  do estado vigente; ato cujo marco não existe mais na versão vigente.
- **FR-005** — A verificação classifica o que encontrou como informação, aviso ou impedimento, e
  apresenta os três ao operador. Qualquer das formas de obsolescência é impedimento — não há
  publicação de ato obsoleto mediante confirmação adicional.
- **FR-006** — A recusa nomeia qual forma de obsolescência ocorreu e indica o caminho: emitir o ato
  sucessor na 015 e publicar aquele.
- **FR-007** — Aferir publicabilidade não constitui ato, não grava e não altera o ato de origem.
- **FR-008** — Um ato obsoleto permanece consultável administrativamente; o que ele perde é a
  possibilidade de originar publicação nova.

#### Conteúdo publicado

- **FR-009** — O conteúdo divulgado deriva exclusivamente do snapshot do ato e da versão normativa
  que o ato cita.
- **FR-010** — Abrir uma publicação, no dia seguinte ou anos depois, nunca executa a regra
  classificatória nem recalcula posições.
- **FR-011** — A publicação persiste o conteúdo divulgado em forma canônica, com resumo
  criptográfico, de modo que se possa afirmar depois que o que se lê é o que foi divulgado.
- **FR-012** — Nomes de Etapas, marcos, perfis, modalidades e critérios são resolvidos para os
  rótulos da versão que o ato cita.
- **FR-013** — Enum canônico e identificador técnico não aparecem como texto institucional. O
  rótulo que o snapshot não resolve é dito como ausente — nunca como identificador —, seguindo a
  política que o documento do Edital já adota.
- **FR-014** — Empate residual é representado como posição compartilhada; nenhum desempate é
  inventado para produzir posições exclusivas.
- **FR-015** — O conteúdo mínimo de cada linha é: posição, identificação pública, perfil,
  modalidade quando aplicável, pontuação combinada quando publicável, e a marcação de empate quando
  houver.
- **FR-016** — A natureza aparece como afirmação institucional em texto — "Resultado preliminar",
  "Resultado definitivo" —, na página e no documento, e não apenas como atributo de dados.
- **FR-017** — Quem foi considerado e não recebeu posição não é nomeado na publicação (D-006).

#### Proteção de dados

Esta feature atravessa a fronteira entre dado administrativo e informação pública, e é onde a
avaliação de LGPD do vertical se concentra. A finalidade é dar publicidade ao ato classificatório;
a necessidade se mede contra essa finalidade, e a minimização é o default — publica-se o que a
finalidade exige, e o resto não sai porque estava à mão na mesma consulta.

- **FR-018** — A identificação pública do candidato é nome completo mais protocolo.
- **FR-019** — Não são publicados: CPF, e-mail, telefone, documentos, `identity_subject`,
  identificador de inscrição, hashes internos, nem qualquer campo cuja finalidade seja interna.
- **FR-020** — Os valores dos fatos pessoais usados no desempate não atravessam a fronteira
  pública, ainda que o critério que os usa esteja declarado no Edital.
- **FR-021** — A proveniência completa do ato, incluindo o desempate, permanece disponível na
  interface administrativa a quem possui autorização.
- **FR-022** — Da publicação é possível navegar até o ato de origem quando o usuário tem
  autorização; o público não precisa desse caminho para que a proveniência exista.
- **FR-023** — Nenhum dado atravessa a fronteira pública por conveniência de implementação: o
  conjunto publicável é declarado, e não é o resultado de serializar o que a consulta trouxe.
- **FR-024** — Publicar o protocolo o torna público, e ele não confere autorização — nem hoje, nem
  quando alguém quiser oferecer consulta por protocolo. Identificador publicado não vira
  credencial.

#### Autoridade e constituição do ato

- **FR-025** — Publicar exige capacidade institucional própria (`resultado:publicar`), reconciliada
  com o mapa de papéis existente.
- **FR-026** — A autorização não deriva de ter emitido o ato, de presidir a comissão, de integrá-la
  nem de avaliar.
- **FR-027** — A publicação registra quem publicou.
- **FR-028** — A publicação registra o instante em que foi praticada.
- **FR-029** — A publicação registra a autoridade signatária — nome, cargo e identificador —
  escolhida no catálogo existente, persistida no ato e imune a alterações posteriores do catálogo.
- **FR-030** — Repetir a confirmação com a mesma chave devolve o desfecho da primeira e não cria
  publicação equivalente.
- **FR-031** — A confirmação carrega a identificação do que foi lido na prévia; divergência entre
  o lido e o vigente recusa o ato em vez de publicá-lo.
- **FR-032** — A publicação concluída é imediatamente consultável nos canais entregues pela
  feature.

#### Prévia

- **FR-033** — A prévia usa a mesma composição do conteúdo que será publicado.
- **FR-034** — A prévia explicita título, Processo/Edital, marco, natureza, ato de origem,
  autoridade signatária e o conteúdo a divulgar.
- **FR-035** — Visualizar a prévia não constitui ato administrativo, não grava linha e não reserva
  identidade.
- **FR-036** — Não existe rascunho persistente de publicação.

#### Natureza, sucessão e imutabilidade

- **FR-037** — A publicação declara sua natureza: `PRELIMINAR` ou `DEFINITIVA`.
- **FR-038** — Uma publicação preliminar não se converte em definitiva; a definitiva é outra
  publicação.
- **FR-039** — Um mesmo ato de ordenação pode originar publicações de naturezas distintas, e no
  máximo uma por natureza: publicar como definitivo o resultado que já foi divulgado como
  preliminar não exige emitir ato novo, e republicar a mesma natureza sobre o mesmo ato é
  duplicidade.
- **FR-040** — A publicação concluída é imutável: não é editada, não é excluída e não é
  despublicada.
- **FR-041** — Correção posterior ocorre por sucessão: novo ato de resultado, nova publicação.
- **FR-042** — A vigência é derivada da cadeia de sucessão, sem coluna de estado; existe no máximo
  uma publicação vigente por marco classificatório.
- **FR-043** — Uma publicação sucedida permanece existindo, íntegra e acessível.
- **FR-044** — Quem abre uma publicação sucedida é informado disso e recebe o caminho para a
  vigente.
- **FR-045** — Retificação posterior do Edital não altera publicação concluída e não regenera seu
  documento.
- **FR-046** — `PublicacaoResultado` **não possui máquina de estados**, porque não possui ciclo de
  vida: nasce completa e não muda. A única transição observável do conjunto é a sucessão, e ela é
  outra linha — não uma transição desta.

#### Página pública

- **FR-047** — A publicação possui endereço estável, que não depende de sessão administrativa e não
  exige autenticação.
- **FR-048** — Publicação histórica continua acessível pelo mesmo endereço depois de sucedida.
- **FR-049** — A página responde: que resultado é, de qual Edital, quando foi publicado, se é a
  vigente e se existe publicação posterior.
- **FR-050** — A publicação vigente é alcançável a partir da página pública do Edital: quem não
  conhece o endereço chega a ela pelo caminho que já usa para conhecer a seleção.
- **FR-051** — A página funciona em 375 px sem rolagem horizontal da página; listas extensas usam
  apresentação responsiva adequada.
- **FR-052** — A situação vigente/sucedida não é comunicada apenas por cor.
- **FR-053** — Os fluxos administrativos e públicos críticos funcionam por teclado.
- **FR-054** — Listas e tabelas possuem estrutura semântica adequada.
- **FR-055** — A página não oferece ação de recurso. Se a versão citada declarar prazo recursal, a
  informação normativa existente pode ser apresentada, sem mecanismo transacional.

#### Área do Candidato

- **FR-056** — Nada relativo a resultado aparece na Área do Candidato antes da publicação. Existir
  `ResultadoEtapa` ou `AtoDeOrdenacao` no banco não torna a informação pública.
- **FR-057** — Havendo publicação cujo ato contemple a Inscrição, ela aparece dentro da própria
  Inscrição, no acompanhamento. Havendo mais de uma — o Edital pode ter vários marcos
  classificatórios, e cada um é ato pleno —, **todas** aparecem, cada uma identificada pelo seu
  marco. O sistema não escolhe por conta própria qual resultado interessa à pessoa.
- **FR-058** — O resumo individual deriva da publicação e aponta para ela; não há segunda fonte de
  verdade específica do candidato.
- **FR-059** — O candidato que foi considerado e não recebeu posição vê a sua própria situação e o
  motivo na sua Área — e só depois que a publicação existe. Não ser nomeado publicamente (FR-017)
  não é o mesmo que não ser informado.
- **FR-060** — O resumo é aditivo aos fatos existentes do acompanhamento e não afirma nada que
  ninguém tenha declarado.
- **FR-061** — Quando a publicação que contempla a Inscrição foi sucedida, o candidato é levado à
  vigente.

#### Documento oficial

- **FR-062** — O documento é derivado do conteúdo persistido da publicação, e não do estado atual
  do Processo.
- **FR-063** — O documento identifica Processo/Edital, marco, natureza, ato de origem, data e hora,
  autoridade signatária, o conteúdo da classificação e o resumo criptográfico.
- **FR-064** — O documento e a página derivam dos mesmos bytes: os rótulos institucionais são os
  mesmos, e cada linha da lista confere — posição, identificação pública, modalidade e pontuação.
- **FR-065** — O documento é produzido pelo renderizador existente e segue os padrões de
  acessibilidade já adotados pelo projeto onde tecnicamente aplicável.

#### Auditoria e histórico administrativo

- **FR-066** — Publicação e sucessão geram auditoria na trilha existente, com ator, ação, entidade
  e identificador, data e hora, versão normativa citada pelo ato, motivo quando houver e
  correlação.
- **FR-067** — Não se cria log paralelo nem tabela de eventos própria da feature.
- **FR-068** — A consulta administrativa lista as publicações de um marco com natureza, instante,
  autor, autoridade signatária e situação.
- **FR-069** — A ação de publicar é alcançável a partir do ato de ordenação, no mesmo lugar em que
  a interface já oferece ao ator o que fazer agora, e condicionada à capacidade.

#### Limites e não regressão

- **FR-070** — A feature não altera `AtoDeOrdenacao`, `PosicaoNaOrdem`, `ResultadoEtapa` nem o
  conteúdo normativo do Edital.
- **FR-071** — A feature não introduz `UPDATE` em tabela histórica; a tabela nova entra na política
  de privilégios como append-only.
- **FR-072** — Publicar não dispara notificação de espécie alguma.

### Key Entities

- **`PublicacaoResultado`** — o ato institucional de divulgação. Cita o Processo/Edital, o
  `AtoDeOrdenacao` publicado, o marco, a natureza, o instante, quem publicou, a autoridade
  signatária, o conteúdo canônico divulgado com seu resumo criptográfico, e a publicação anterior
  quando sucede outra. Append-only.
- **Situação divulgada** — a situação de uma pessoa naquela divulgação: uma linha por participante
  considerado pelo ato, inclusive quem não recebeu posição. É o que responde à FR-059 sem nomear
  ninguém publicamente, e é congelada na mesma transação e a partir do mesmo ato que a lista
  pública — por isso não é segunda fonte de verdade. Não atravessa a fronteira pública.
  Append-only.
- **Documento da publicação** — a representação imprimível dos mesmos bytes de conteúdo, com seu
  próprio resumo. Append-only.

---

## 5. Invariantes observáveis

- **I-001** — Publicação não cria resultado: toda publicação deriva de ato previamente constituído.
- **I-002** — Publicação não recalcula: o conteúdo oficial deriva do ato de origem, e reproduzir
  para aferir publicabilidade nunca alimenta o que é divulgado.
- **I-003** — Publicação concluída é imutável; correção ocorre por sucessão.
- **I-004** — Ato interno não publicado não é público, em especial na Área do Candidato.
- **I-005** — Histórico permanece reproduzível: abrir publicação antiga mostra o que foi divulgado
  naquele momento.
- **I-006** — Vigência é diferente de existência: uma publicação sucedida continua existindo.
- **I-007** — Somente dados publicáveis atravessam a fronteira institucional.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** — Um ator com `resultado:publicar` publica um ato de ordenação emitido, do início ao
  fim, pelo navegador.
- **SC-002** — A ação de publicar existe apenas a partir do ato emitido; a tela de cálculo não a
  oferece, e não há identidade de proposta a que apontá-la.
- **SC-003** — Toda publicação concluída possui autor, instante e autoridade signatária.
- **SC-004** — O conteúdo de uma publicação permanece idêntico ao divulgado, verificável pelo seu
  resumo criptográfico.
- **SC-005** — Publicar de novo o mesmo marco não sobrescreve a publicação anterior.
- **SC-006** — Abrir uma publicação sucedida informa que ela foi sucedida e leva à vigente.
- **SC-007** — Nenhum UUID ou enum canônico aparece como informação institucional na página, no
  documento ou na Área do Candidato.
- **SC-008** — Antes da publicação, o candidato não alcança resultado algum por nenhum caminho da
  sua Área.
- **SC-009** — Depois da publicação, o candidato chega ao resultado pela própria Inscrição.
- **SC-010** — O documento oficial reproduz o conteúdo publicado, inclusive depois de Retificação
  posterior do Edital.
- **SC-011** — Reabrir uma publicação histórica não executa a regra classificatória.
- **SC-012** — A publicação de ato obsoleto é recusada nas três formas: sucedido, divergente e com
  marco removido.
- **SC-013** — Confirmação repetida produz uma única publicação.
- **SC-014** — Ator sem a capacidade não publica, inclusive quando é quem emitiu o ato.
- **SC-015** — Nenhum dado pessoal não publicável aparece na publicação, incluindo os valores de
  fato usados no desempate.
- **SC-016** — A página pública não apresenta rolagem horizontal a 375 px.
- **SC-017** — Publicação e sucessão aparecem na trilha de auditoria existente, com ator, entidade,
  instante e a versão normativa que o ato citava.
- **SC-018** — Quem não conhece o endereço chega à publicação vigente a partir da página pública do
  Edital.
- **SC-019** — A página e o documento dizem em texto se o resultado é preliminar ou definitivo.
- **SC-020** — O candidato considerado e não classificado é informado da sua própria situação na sua
  Área, sem ser nomeado na publicação.
- **SC-021** — O mesmo ato publicado de novo na mesma natureza é recusado; publicado primeiro como
  `PRELIMINAR` e depois como `DEFINITIVA`, produz a segunda publicação, que sucede a primeira. A
  ordem inversa não existe: `PRELIMINAR` não sucede `DEFINITIVA`.
- **SC-022** — Publicados dois marcos que contemplam a mesma Inscrição, a Área do Candidato mostra
  os dois, cada um identificado pelo seu marco.
- **SC-023** — Um ato recusado por obsolescência continua consultável na interface administrativa,
  com a sua proveniência completa — inclusive os critérios de desempate e o que cada um comparou.

---

## 6. Out of Scope

**Seleção** — novas regras classificatórias, corte, progressão, ocupação de vagas, modalidades,
cotas, remanejamento.

**Contestação** — recurso, anexos, julgamento, decisão, efeito suspensivo, superação do resultado.
A publicação cria o marco público contra o qual um recurso futuro poderá ser interposto; a 018 o
implementa.

**Convocação** — chamadas, aceite, prazo de ciência, posse e matrícula. A 017 fornece o marco
público que a 019 poderá referenciar.

**Homologação de resultado** (D-003).

**Publicação de `ResultadoEtapa`** e qualquer abstração genérica de publicável (D-002).

**Comunicação ativa** — e-mail, SMS, push, WhatsApp.

**Integrações externas** — Diário Oficial, portal institucional externo, redes sociais, assinatura
ICP-Brasil.

**CMS** — editor genérico de páginas ou documentos.

**O documento normativo do Edital** — os achados E2E15-004, E2E15-005 e E2E15-008 foram
**resolvidos** no PR #39, antes desta spec: o Edital publicado já basta para refazer a ordem. A 017
herda o vocabulário que aquela correção produziu e não volta a mexer no documento do Edital; se
uma lacuna nova aparecer ali, ela é da linhagem do Edital, não desta feature.

---

## Assumptions

- O marco classificatório e o perfil já possuem identidade estável no conteúdo publicado, e o ato
  de ordenação os cita — a 017 não introduz identidade nova.
- A capacidade `resultado:publicar` será acrescentada ao papel Publicador existente; se a
  instituição preferir papel distinto, isso é configuração do mapa, não mudança de contrato.
- O protocolo da Inscrição (`INS-2026-K7M4Q2PX`) é único, legível — alfabeto sem `0`/`O` e
  `1`/`I`/`L`, porque ele é ditado ao telefone — e opaco, sem sequência. É adequado à divulgação
  pública, e nenhum caminho atual o aceita como credencial de acesso. FR-024 mantém isso verdadeiro
  depois de publicá-lo.
- Os endereços públicos existentes usam identificador técnico no caminho, e a 017 segue o mesmo
  padrão: o endereço não é linguagem apresentada.

---

## 7. Ordem de implementação sugerida

| Slice | Entrega |
|---|---|
| **S0** | `PublicacaoResultado` append-only, cadeia de sucessão, política de privilégios, vínculo ao ato da 015 |

O **S0** é o único slice sem comportamento observável, e existe para desbloquear o S1: sem o
agregado append-only e sua cadeia, publicar não teria onde nascer. Ele não gera prioridade própria.
| **S1** | Publicabilidade + prévia + autorização + confirmação idempotente |
| **S2** | Página pública estável |
| **S3** | Área do Candidato |
| **S4** | Documento oficial |
| **S5** | Histórico administrativo, sucessão observável e concorrência |

O documento vem **depois** do portal: ele é institucionalmente importante, mas a maior validação de
produto desta feature é o resultado chegar ao candidato.

## 8. Gate de conclusão

```text
classificação emitida
  → autoridade publicadora vê a prévia
  → publica
  → página pública nasce
  → candidato vê a publicação na própria Inscrição
  → documento oficial existe
  → publicação anterior permanece histórica quando sucedida
```

Ao final da 017 o produto responde, pela primeira vez e de ponta a ponta: **a instituição chegou a
uma decisão classificatória e tornou essa decisão oficialmente acessível às pessoas interessadas.**
