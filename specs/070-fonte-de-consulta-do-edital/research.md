# Research — 070, a fonte de consulta do Edital vigente

*Fase 0 do plano, em 12/10/2026, sobre a `main` em `a79ce463`. Cada item é uma decisão técnica
com o fato que a sustenta, lido no código desta data. Os caminhos são relativos a
`backend/processo_seletivo/`, salvo quando começam por `backend/`, `specs/`, `doc/` ou `docs/`.*

As decisões de produto estão na spec, em `D-001` a `D-009`. Aqui ficam as técnicas, numeradas
`R-001` a `R-020`.

---

## R-001 — Um pacote novo, `duvidas`, com domínio e aplicação; a tela fica em `interface`

**Decisão.** A fonte de consulta mora num pacote novo, `processo_seletivo/duvidas/`.

| Camada | Conteúdo |
|---|---|
| `domain/` | Puro: recebe o conteúdo publicado e devolve a resposta, sem banco |
| `application/` | Lê do banco a versão, as versões futuras, a proveniência, as publicações e o desfecho, e chama o domínio |

O pacote não tem `models.py` nem migration. É registrado em `INSTALLED_APPS` como os vizinhos,
com o comentário do porquê. A tela é uma view de `interface`, num módulo próprio,
`interface/duvidas.py`, como a `066` fez com `interface/avisos.py`.

**Por quê.**

- **O nome é o do produto final, e não o de uma plataforma.** `duvidas` é o que o assistente
  responde, e as Fases B e C crescem dentro dele sem mudar de casa.
- **`consulta` foi recusado.** "Consulta pública" e "consulta histórica" já nomeiam outra coisa no
  sistema: a API de `publicacoes`, da `001` e da `024`. Dois conceitos com o mesmo nome violam o
  princípio I.
- **`assistente` foi recusado.** Na gestão, "assistente" já é o assistente de composição
  (`interface/templates/interface/compor_base.html`, `class="assistente"`).
- **Domínio puro é o que a `FR-1448` pede.** A resposta sai de uma função sem requisição nem sessão,
  que a Fase B pode chamar de outro processo.

**Alternativas.**

- Dentro de `publicacoes`: misturaria a regra de publicar com a de explicar.
- Dentro de `portal`: a Fase A não é pública, e o portal é o canal do candidato.

---

## R-002 — Vocabulário: "assistente de dúvidas", sempre qualificado

**Decisão.**

- Na tela e nos textos, o produto se chama sempre **"assistente de dúvidas"**, nunca "assistente"
  sozinho.
- Os três rótulos de cartão são os da spec: "Texto do Edital", "Dado da versão vigente" e
  "Explicação".
- O componente de tela usa a classe `referencia`, e não `cartao`. O assistente de composição tem
  regras próprias para os cartões dele (a microcópia vai ao "como preencher"), e o nome igual
  convidaria a aplicar a regra errada.

**Por quê.** Princípio I. É a mesma armadilha que fez a `062` separar "lista" de "recorte".

---

## R-003 — A versão: `effective_version` uma vez, as futuras por `valid_from`

**Decisão.**

- **Leitura única.** A aplicação lê a versão vigente uma vez por resposta, com
  `publicacoes.application.selectors.effective_version(edital_id=..., at=instante)` (`:27-42`).
- **Sem versão vigente.** A recusa `no_effective_version` — Edital sem publicação, ou instante
  anterior à primeira vigência — vira o estado "sem versão vigente" da tela, e não erro (`FR-1413`).
- **Versões futuras.** São as `VersaoConsolidada` do Edital com `valid_from > instante` **e
  `materialized_at <= instante`**, por `valid_from` e depois `materialized_at`, a mais recente de
  cada fronteira. Elas são lidas na mesma ida ao banco e servem só para o aviso da `FR-1414`. O
  filtro de `materialized_at` entrou na revisão de código de 12/10: sem ele, a consulta a um
  instante passado tratava como "futura já publicada" a Retificação publicada depois do instante.
- **Nada em elaboração.** Nenhuma `Retificacao` em elaboração, revisão ou homologada é lida: a
  aplicação só conhece `VersaoConsolidada` e `Publicacao` (`FR-1412`).

**Por quê.** É a regra da página pública: `portal/views.py:406` usa um `agora` só para a leitura
inteira. E a versão vigente muda **sem ato novo** quando a fronteira passa (auditoria, §6.4):
determinar a versão pelo instante, a cada consulta, é a única forma correta.

**O que se compara com a versão futura.** A mesma pergunta é respondida, pelo mesmo construtor,
sobre o conteúdo de cada versão futura, e os cartões das duas respostas se comparam pelo que dizem.
Onde diferirem, sai o aviso: o valor novo, o `valid_from` e a Retificação que o fixou (`R-004`).

**Por que não cruzar com `target_path`.** Comparar o valor pega também a alteração num ancestral —
um Perfil substituído inteiro —, que o cruzamento literal de caminhos perderia.

**Emenda da revisão de código de 12/10.** A primeira implementação resolvia o valor cru em cada
caminho citado (`resolve_path`). Isso tinha três defeitos:

- dava o valor como gravado ("UNLIMITED", uma identidade de Etapa), e não nas palavras do cartão;
- deslocava os itens de lista atômica quando a Retificação acrescentava um no início;
- não via o que a Retificação **acrescenta** (um Evento, um documento), e dizia "não altera o que
  esta resposta cita".

Responder de novo sobre o conteúdo futuro resolve os três com a regra de formatação que já existe.

---

## R-004 — A origem de cada valor: a proveniência da versão, pelo ancestral mais próximo e pelo último ato

**Decisão.** A origem de um valor no caminho `P` da versão `V` é calculada assim.

1. Toma-se `V.proveniencias` (`ProvenienciaConteudo`, já pré-carregado por `effective_version`).
2. Ficam os registros cujo `target_path` é **`P` ou ancestral de `P`**.
3. Desses, vence o do ato aplicado por último, na ordem `(effective_at, publication_order)` — a mesma
   de `publicacoes/domain/consolidation.py:7`.
4. Sem nenhum registro, a origem é a **publicação original**: a primeira de `applied_publications`.
5. Valor composto — o quadro de vagas, a lista de requisitos — **cujos descendentes** foram
   alterados por atos diferentes leva **uma origem por valor**, e não uma só. O cartão diz cada uma.

**Por quê.**

- `consolidate` só acrescenta: a substituição posterior de um ancestral não apaga o registro antigo
  do descendente. Escolher pelo caminho mais longo daria a origem velha, e por isso a ordem dos atos
  decide.
- **O documento do ato de origem contém o valor.** O conteúdo de uma Retificação publicada é a base
  dela mais as alterações dela (`retificacoes.py:885-903`); o da publicação original é o conteúdo
  inteiro. Os dois cenários do
  [achado](../../doc/achado-documento-ligado-nao-contem-a-versao-vigente.md) mostram a diferença: o
  documento de R2 tem o valor de R2 e não o de R1, e o de R1 tem o de R1.

**A entidade acrescentada** (emenda da revisão de 12/10). O acréscimo ao fim de uma coleção é
gravado pelo caminho literal — `/profiles/-`, e não `/profiles/id=<novo>` —, e `consolidate` guarda
um registro por caminho: o segundo acréscimo apaga o registro do primeiro. Sem correção, o cartão de
um Perfil acrescentado por Retificação levava ao documento da publicação original, que não o
contém. A regra para esse caso: a entidade vem do **primeiro ato, na ordem de aplicação, cujo
documento a contém** (`origem.acrescimos`). O conteúdo de cada ato só é lido quando a proveniência
tem um acréscimo, na mesma consulta das publicações. As alterações normativas não são lidas: são
fronteira da consulta (`FR-1412`).

**Risco registrado.** `ProvenienciaConteudo` não é append-only: não tem gatilho e não está em
`TABELAS_APPEND_ONLY`, como a auditoria já notou. A Fase A só lê a tabela. Protegê-la é achado à
parte, e não escopo.

**Verificação.** Testes de integração nos dois cenários do achado e numa Retificação que substitui
um Perfil inteiro depois de outra que mudou um campo dele (`SC-535`).

---

## R-005 — O documento de origem incompleto: diferença de conjuntos de atos, sem hash

**Decisão.** Para a versão vigente `V`, a publicação `S = V.source_publication`:

- **contém os atos** `A(S)`:
  - a própria `S`, se é a original;
  - os de `Retificacao.base_snapshot.applied_publications` mais `S`, se é Retificação;
- **é incompleta** quando `V.applied_publications − A(S)` não é vazio. Os atos faltantes são
  nomeados no ponto para revisão (`FR-1443`).

**Por quê.** É exato e explicável: diz **quais** atos faltam. Comparar `content_hash` diria só que
há diferença.

**Verificação.** Os dois cenários do achado acusam o ponto, e um Edital com uma Retificação só não
acusa.

---

## R-006 — O desfecho no instante: `desfechos`, filtrado pela data do ato

**Decisão.**

- Usa-se `processos.application.selectors.desfechos([edital])` (`:89`), que devolve o `Desfecho`
  com `em`, o instante do ato.
- O desfecho vale para a consulta quando `em <= instante`. Com `em` nulo, vale só para o instante
  presente.
- `Desfecho.do_edital` decide se o período fecha, como na página (047).

**Por quê.** O estado do Edital é o de agora. Com instante de referência no passado (`D-009`), um
cancelamento posterior não pode aparecer como já ocorrido.

---

## R-007 — A situação de calendário: as funções de domínio da página, e não as do portal

**Decisão.** A situação vem de duas funções de domínio:

- `inscricoes.domain.periodo.periodo_de_inscricoes(conteudo, instante)`, para o período;
- `editais.domain.fase_do_evento.fase_publica_do_evento(evento, conteudo, instante)`, para a fase de
  cada Evento.

Mais o desfecho (`R-006`). As palavras da situação são deste pacote.

**Por quê.** São as funções que a página pública usa por baixo de `portal/leitura.py:36-166`.
Importar o domínio, e não o portal, mantém a direção das dependências: o canal depende do domínio,
nunca o inverso.

---

## R-008 — Vagas, listas de concorrência e documentos: as leituras que a página já faz

**Decisões.**

- **Vagas** saem de `profiles[].vacancyTable`. A linha com `modalityId` nulo é a ampla concorrência
  (`FR-1427`). Uma modalidade declarada sem linha no quadro **não** aparece no quadro — é a grafia
  que existe para que documento possa apontá-la (memória do projeto, "ampla concorrência tem duas
  grafias"; `025`).
- **As opções de lista de concorrência da `P-05`** são as mesmas de `portal/views.py:248-283`
  (`_documentos_anunciados`):
  - "sem modalidade", que é o que vale para todos no Perfil;
  - cada modalidade declarada.
- **Documentos.** Saem de `editais.domain.documentos.aplicabilidade(conteudo, profile_id=...,
  modality_id=...)` (`:222`), a regra única que a inscrição usa.
- **O veredito `divergente`.** Ele marca documento que o publicado nomeia por grupo e que o leitor
  pode entender como exigido também ali — o resíduo da `044`. Quando vem marcado, a resposta passa a
  "Depende da leitura do Edital", com o documento e a explicação de que a redação publicada alcança
  mais do que a regra aplicada.

**Por quê.** Três leituras da mesma regra, e nenhuma interpretação nova — o argumento do próprio
comentário de `_documentos_anunciados`.

---

## R-009 — A explicação é escrita aqui; nada do compositor do documento é importado

**Decisões.**

- **Os textos da explicação são deste pacote.** Ficam em `duvidas/domain/explicacao.py`, em
  linguagem simples, com só os valores dos cartões (`FR-1425`, `D-003`).
- **A formatação é a do sistema.** Datas e decimais saem de `publicacoes.infrastructure.humano`
  (`instante`, `decimal`, `data_por_extenso`), que a página pública já usa. É formatação, e não
  frase normativa.
- **Guardião de importação.** Um teste varre por AST os módulos de `duvidas/` e reprova a importação
  de:
  - `publicacoes.infrastructure.pdf`;
  - `publicacoes.domain.vocabulario_da_regra`;
  - `sorteios.domain.prosa`.

  Sem ele, a `FR-1434` dependeria de disciplina.

**Por quê.** As frases do compositor não estão no conteúdo publicado e mudam com o código (`067`,
`068`, e a `069` reescrevendo). Importá-las faria a explicação mudar com o PDF futuro, e citá-las
como texto seria afirmar sobre documentos antigos o que eles não dizem.

**Alternativa recusada.** Reaproveitar `vocabulario_da_regra` para o desempate. É a mesma frase do
documento do resultado, e é justamente a que a `069` reescreve.

---

## R-010 — Texto literal: o valor resolvido, sem tratamento

**Decisão.**

- O cartão "Texto do Edital" carrega a cadeia resolvida no conteúdo publicado, por caminho, **sem**
  `strip`, sem normalização e sem corte. A tela preserva as quebras de linha.
- O parágrafo de seção é a linha de `sections[].content` separada por `\n`, que é como o conteúdo
  publicado guarda parágrafos (medido no corpus).
- O cartão de seção textual leva a seção inteira (`FR-1420`). O parágrafo só é unidade no canal de
  atendimento, onde a spec pede o parágrafo literal (`FR-1439`).

**Verificação (`SC-534`).** Para todo cartão de texto de toda resposta da varredura, o texto é
idêntico a `resolve_path(conteudo, caminho)`, ou à linha dele.

---

## R-011 — O canal de atendimento: termos, contatos e exclusividade em listas fechadas

**Decisão.** O canal sai das seções textuais da versão vigente, parágrafo a parágrafo.

1. **Parágrafo de dúvida.** É o que contém, depois de `shared.texto.dobrar()`, uma destas raízes:
   `duvida`, `esclarec`, `atendimento`, `contato`, `informacoes sobre este edital`.
2. **Contato** é qualquer um destes:
   - e-mail, pelo padrão `local@dominio.tld`;
   - endereço eletrônico, que começa por `http://`, `https://` ou `www.`;
   - telefone brasileiro: DDD entre parênteses ou não, 8 ou 9 dígitos, hífen opcional.
3. **Canal distinto** é o contato normalizado: e-mail em minúsculas; endereço sem barra final;
   telefone só com dígitos.
4. **Exclusividade** é o parágrafo de dúvida com contato e com uma destas palavras: `exclusivamente`,
   `somente`, `unicamente`, `apenas`.

**Conferido no corpus.**

| Edital | Resultado |
|---|---|
| 91/2026 | Um canal (o e-mail da seção "Disposições Preliminares", 2º parágrafo), **com** exclusividade |
| 92/2026 | Um canal (item 15.3 das "Disposições Finais"), **sem** exclusividade. O 11.1 dos recursos não tem contato nem termo de dúvida e fica de fora |
| 01/2026 | Nenhuma seção; vale o canal da implantação |

**Os erros possíveis são visíveis.** Falso positivo gera ponto para revisão a mais; falso negativo
põe o canal institucional no lugar do do Edital. Os dois aparecem na validação interna, que é o
propósito da Fase A.

**Alternativa recusada.** Ler "informações" sozinho: alcançaria "Informações Gerais sobre o Curso".

---

## R-012 — Anexos: pelo vínculo do documento e pela citação do rótulo

**Decisão.** O cartão de anexo sai por dois caminhos.

1. **Pelo vínculo.** `documentRequirements[].attachmentId` aponta um anexo publicado: sai o cartão
   dele, com rótulo e link `public-anexo`.
2. **Pela citação.** Nos textos que a resposta mostra — seções pertinentes, nome de Etapa,
   instruções de documento, descrição de Evento —, a expressão
   `\banexo\s+([ivxlcdm]+|\d+)\b`, sem diferenciar maiúsculas, é comparada ao começo do rótulo dos
   anexos publicados (`ANEXO <identificador>`).
   - Havendo anexo correspondente, sai o cartão com o aviso de que o sistema não lê o conteúdo.
   - Não havendo, sai um ponto para revisão.

**Conferido no corpus.** O 92/2026 cita "Anexo IV" no nome da Etapa de títulos e na instrução de
"Documentos passíveis de pontuação", e o anexo existe. O 91/2026 cita "Anexo I" na instrução da
autodeclaração. Os dois casos se resolvem pelo segundo caminho.

---

## R-013 — O tipo da resposta: uma tabela de decisão por pergunta

*Emenda de 12/10/2026 (`D-011`).* Acima da tabela abaixo, vale: "Respondida" exige cobertura do
enunciado. O texto que é o núcleo da resposta e remete a anexo leva a "Depende da leitura".

**Decisão.** O tipo é calculado por regras fixas, no contrato
[resposta.md](contracts/resposta.md#tipos-por-pergunta). A regra geral:

| Fontes que tratam do assunto | Tipo |
|---|---|
| Só dado estruturado | "Respondida pelos dados" |
| Dado estruturado **e** texto, ou texto só | "Depende da leitura do Edital" |
| Nenhuma | "O Edital não informa" |
| Duas fontes comparáveis que divergem — na Fase A, só canais | "Fontes divergentes" |

**O caso que define a regra.** Na `P-08` do 91/2026 há a janela declarada no marco, a seção "Dos
Recursos" e o Evento de recurso: o tipo é "Depende da leitura". No `TEC-LAB` do 01/2026 não há
nenhuma das três: "O Edital não informa". O marco que declara `admits: false` dá "Respondida pelos
dados", com a negativa como dado (`FR-1422`).

**A seção pertinente sozinha não muda o tipo quando o dado responde.** Na `P-01`, a seção
`inscricao` acompanha a resposta como texto, mas o período é dado. O critério é se o **assunto
perguntado** está no texto. Para cada pergunta, a tabela do contrato nomeia quais seções tratam do
assunto (mudam o tipo) e quais só acompanham.

**A lista literal que a pergunta pede é dado, mesmo sendo texto.** Os requisitos do Perfil, na
`P-04`, são uma coleção estruturada de itens de texto. Listá-los, inteiros e na ordem, é responder
pelos dados: a estrutura determina **quais** são, e o sistema não interpreta nenhum. Só leva a
"Depende da leitura" o texto **sobre** o assunto que está fora dessa lista — a seção
`requisitos-gerais` na `P-04`; as seções `convocacao` e `matricula` na `P-10` —, porque aí a resposta
depende de ler prosa que a estrutura não delimita.

O critério, em uma linha: a pergunta pede uma coleção que o conteúdo declara? A coleção é dado.
A pergunta só se responde lendo prosa? É leitura.

---

## R-014 — Eventos de recurso: pela palavra, para mostrar, e não para decidir

**Decisão.** Na `P-08`, os Eventos mostrados são os que têm a raiz `recurs` em `type` ou em
`description`, depois de `dobrar()`. Eles aparecem como texto e dado: data e descrição literais.
Nenhum é ligado a marco.

**Por quê.** Não existe vínculo entre Evento e marco (RC-76, fora da `047`). Mostrar pela palavra é
seleção do que exibir. Concluir o prazo pelo Evento seria interpretar.

**Descoberta na implementação (12/10/2026).** No 01/2026, o `TEC-LAB` não declara recurso, e o
Edital não tem seção de recursos. Mas o Evento 3 diz "Resultado final e abertura do prazo recursal".
Pela regra acima, ele é fonte sobre recurso, e a resposta é "Depende da leitura do Edital". A spec
esperava "O Edital não informa", pela matriz da auditoria (`CA-10`), que não tinha visto o Evento. A
spec foi emendada (US3, cenário 1a). A regra não mudou: mudou o exemplo, que estava errado.

---

## R-015 — O guardião de cobertura: tabela de caminhos, conferida contra o conteúdo e presa à versão do esquema

**Decisão.** `duvidas/domain/cobertura.py` declara a tabela `COBERTURA`. Cada linha liga um padrão
de caminho do conteúdo publicado (`/profiles/*/vacancyTable/*/immediateVacancies`) a uma de duas
coisas:

- as perguntas que o mostram;
- `EXCLUIDO` com o motivo — por exemplo `classificationInformation`, opaco, que o documento não
  imprime.

O teste tem três partes:

1. **Conteúdo.** Percorre o conteúdo dos três Editais do corpus e de uma fixture que preenche todo
   campo opcional, generaliza índices e chaves para `*`, e exige que todo caminho folha esteja na
   tabela.
2. **Esquemas declarados.** Exige que todo campo de `PERFIL_PUBLICADO`, `EVENTO_PUBLICADO`,
   `DOCUMENTO_EXIGIDO_PUBLICADO`, `ETAPA_PUBLICADA`, `SECAO_PUBLICADA`, `ANEXO_PUBLICADO` e
   `LINHA_DO_QUADRO_PUBLICADA` (`editais/domain/validation.py:95-290`) esteja na tabela.
3. **Versão do esquema.** Exige que `shared.canonical.SCHEMA_VERSION` seja a versão registrada na
   tabela, que hoje é 17.

**Por quê das três.** As coleções sem esquema declarado — modalidades e marcos — só aparecem pelo
conteúdo. E um campo novo que nenhuma fixture preencha só aparece pela mudança da versão do esquema,
que toda feature que muda o conteúdo publicado é obrigada a fazer (`shared/canonical.py:7-151`). É o
"campo novo faz a conferência falhar" do `SC-533`.

---

## R-016 — O corpus nos testes: o conteúdo copiado para o domínio, e o fluxo real para a integração

**Decisão.** Duas camadas.

1. **Domínio, sem banco.** Os conteúdos publicados e as alterações do corpus são copiados de
   `docs/libras/editais/edital-{01,91,92}-2026/fonte/` para
   `backend/tests/fixtures/corpus_070/`. Junto vai um `LEIA-ME.md` com a origem, o commit e o
   SHA-256 de cada arquivo.

   As versões consolidadas v2 e v3 já estão nos `pubN-canonico.json`. Os casos `CA-*` de conteúdo
   rodam como testes unitários sobre eles, com instantes absolutos de outubro e novembro de 2026,
   que o domínio aceita porque não consulta relógio.

   **Copiar, e não ler de `docs/`.** O estudo de Libras é revisado por rodadas, e o teste não pode
   mudar porque um documento de estudo mudou.
2. **Integração, pelo fluxo real.** Um ajudante de teste, `publicar_do_corpus(nome, deslocamento)`,
   publica pelos comandos de aplicação:
   - `replace_draft`, com o conteúdo publicado como rascunho. A forma é a mesma: perfis, cronograma,
     etapas, seções, documentos e método do sorteio (`editais/application/draft.py:163-175`);
   - teto e Requerimento, pelos comandos deles;
   - anexos, por `criar_anexo`, com bytes de teste;
   - depois as Retificações, de `pubN-alteracoes.json`.

   Todas as datas são deslocadas para o futuro do relógio de teste, porque a `028` recusa publicar
   período vencido. As integrações cobrem o que só existe no banco: versão no instante, fronteira,
   proveniência, desfecho, os cenários do achado e o orçamento de consultas.

**A confirmar na primeira tarefa** (um ensaio, e não suposição): se o conteúdo publicado passa
inteiro pelo `replace_draft` e pelas validações de publicação. A `065` recusa conflito de numeração
no Edital original, e o 92/2026 publicado foi o "B corrigido".

**Resultado do ensaio (12/10/2026, T004): passou.** Os três Editais voltam pelo fluxo real com o
conteúdo vigente igual ao do corpus (`backend/tests/integration/duvidas/test_corpus_pelo_fluxo_real.py`).
A diferença é só o que o fluxo não reproduz por construção: datas deslocadas, identificadores do
Processo e do Edital, a identidade das seções e o artefato de cada anexo.

Dois ajustes, ambos no ajudante e não no produto:

- o rascunho recusa `null` em `normativeRule`, e o conteúdo publicado o escreve. Ausente e nulo
  dizem o mesmo, e as chaves nulas são omitidas nos Perfis;
- a identidade da seção é `uuid5(edital:key)`. O caminho das Retificações que alteram seção é
  remapeado pela chave.

O plano B não foi necessário.

**Plano B, se o ensaio falhar.** Editais de teste mínimos que reproduzem só o fato de cada caso de
integração. A `FR-1450`, emendada depois da análise de 12/10, prevê exatamente as duas camadas:
- o conteúdo, sem banco, sobre o corpus;
- o banco, pelo fluxo real, com o corpus quando ele passa pelo fluxo, ou com Editais mínimos quando
  não passa.

**Custo.** Os casos de integração são transacionais (caros, ver `CLAUDE.md`). São poucos, perto de
dez, e o resto é unitário.

---

## R-017 — O isolamento futuro: uma função de aplicação sem requisição, e uma resposta serializável

**Decisão.** O contrato é
`duvidas.application.consultar.consultar(*, edital_id, instante, pergunta, parametros, versao_anterior=None) -> Consulta`.

- Ela recebe só valores e não toca `request`, sessão nem settings de tela.
- Devolve dataclasses congeladas, com `como_dict()` determinístico, descrito em
  [resposta.md](contracts/resposta.md).
- Na Fase A, nenhuma chave de configuração, nenhum cache e nenhuma rota além da tela.

**Por quê.** É o que a `FR-1448` pede e o 7º do usuário limita. A Fase B poderá chamar a mesma
função num conjunto de workers isolado, sem refatorar. Uma API ou um comando de gestão agora seriam
infraestrutura antecipada.

---

## R-018 — A tela: GET com parâmetros, alcance de `obter_edital`, e os guardiões que ela aciona

**Decisões.**

- **Rota:** `gestao/editais/<uuid:edital_id>/duvidas/`, nome `interface:duvidas`, só `GET`. O
  formulário é `GET` porque a consulta não muda nada: é endereçável e o botão "voltar" funciona.
- **Alcance:** `processos.application.selectors.obter_edital(actor=..., edital_id=...)` (`:42`), o
  mesmo da página do Edital (`interface/views.py:3541-3549`), sem capacidade nova (`D-010`). Fora do
  escopo, `Http404`, que é classificado como **escopo institucional** no inventário.
- **Entrada:** um link na página do Edital, no bloco dos documentos publicados, só quando o Edital
  tem publicação.
- **Guardiões que a tela aciona**, a atualizar no mesmo commit:

  | Guardião | O que muda |
  |---|---|
  | `backend/tests/test_gramatica_das_portas.py` | `MODULOS_DE_VIEW` ganha `interface/duvidas.py` |
  | `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` | Uma linha "acrescentada pela `070`", na prática de toda feature que cria porta. Não altera decisão da `033` |
  | `backend/tests/interface/test_acessibilidade.py` | Varre `interface/templates/interface/*.html` sozinho; classe nova precisa de regra em `base.html` |
  | `backend/tests/interface/test_estaticos.py` | CSS sem `}}` na mesma linha |
  | `backend/tests/test_vocabulario_da_composicao.py` | Lista literal; o template entra se usar algum termo da lista, a conferir na implementação |

---

## R-019 — Desempenho: orçamento de consultas fixo, tempo medido

**Decisões.**

- **Consultas ao banco: no máximo oito por resposta, e o número não cresce com Retificações, Perfis
  ou documentos.** São estas:
  1. o Edital;
  2. a versão vigente;
  3. a proveniência dela, pré-carregada por `effective_version`;
  4. as versões futuras;
  5. a proveniência delas, só quando há futuras;
  6. as publicações aplicadas, com a Retificação e a versão-base de cada uma, na mesma consulta — e,
     só quando uma Retificação acrescentou a uma coleção, o conteúdo de cada ato, ainda na mesma
     (`R-004`);
  7. a versão anterior informada, só quando há;
  8. o ato do desfecho, só quando há desfecho.

  Os documentos e anexos **não** são consultados: o link de cada um sai do identificador que já está
  na publicação e no conteúdo. Um teste de orçamento conta as consultas.

  *Corrigido na implementação (12/10/2026).* A primeira versão desta decisão dizia "no máximo seis" e
  listava uma consulta aos documentos que não é necessária. Medido: cinco consultas sem versão futura
  e seis com ela, mais as duas condicionais.
- **Tempo.** O `SC-537` é medido sobre o 92/2026 publicado pelo ajudante do `R-016`, e o número vai
  para a verificação da feature, como a `066` fez.

**Por quê.** Teste de tempo falha por motivo errado em CI (`backend/scripts/carga_publica.py`, na
docstring). O orçamento de consultas é o que impede a regressão real: ler por listagem (memória do
projeto, "orçamento de consulta reprova leitura por listagem").

**Atenção aos bytes.** Os documentos e anexos guardam os bytes no banco. A consulta não os carrega:
usa `.only()` ou `.values()` com identificador e data.

---

## R-020 — O instante de referência: parâmetro `em`, na zona institucional

**Decisão.**

- O parâmetro `em` tem a forma `AAAA-MM-DDTHH:MM` e é interpretado na zona institucional
  (`shared.tempo.ZONA`).
- Sem `em`, vale o instante da requisição. Com `em` inválido, a tela diz que o instante não foi
  entendido e consulta no presente.
- A tela sempre mostra o instante usado.
- A versão anterior vai no parâmetro `versao`: o identificador da `VersaoConsolidada` em que a
  resposta mostrada se baseou. O formulário o carrega escondido.
- O "identificador curto" exibido é o começo do `content_hash`, com 12 caracteres.

**Por quê.** `D-009`. E o identificador interno na URL da gestão segue o resto da gestão, que já
endereça por UUID. A regra de não expor UUID vale para o documento (`007`), e não para a tela
interna.
