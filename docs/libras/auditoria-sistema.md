# Auditoria do sistema: de onde vem o conteúdo de um Edital

**Data:** 2026-10-11 · **Commit:** `bbc8e04c` (`main`) · **Natureza:** investigação documental para a
preparação de traduções em Libras. **Nada foi implementado nem alterado** no código, nos modelos, nas
APIs ou no gerador de PDF.

> **Não vira escopo por estar escrito aqui.** Este documento registra o que o sistema faz hoje e o que
> isso significa para uma biblioteca audiovisual em Libras. Decidir se ela será construída, e como, é
> do usuário (Constituição; `CLAUDE.md`, *Governança é do usuário*).

> **Revisão da rodada 2 (2026-10-11).** Acrescentado o §13 — contexto legal por tipo de certame, verificado
> nos textos oficiais, e a distinção entre ausência de cláusula, proibição expressa e direito previsto fora
> do edital. Atualizadas as métricas do §1 para a versão 2 do catálogo (os valores da versão 1 ficam
> indicados). Corrigidas as frases que tratavam o silêncio do edital como norma (§5, §12) e acrescentadas, no
> §6, as regras embutidas em descrições de Evento.

**Convenção.** Cada afirmação leva uma marca: **Fato** (lido no código ou observado no PDF gerado),
**Hipótese** (plausível e não verificada) ou **Lacuna** (o que não se sabe, ou o que o sistema não tem).
Os caminhos de código são relativos a `backend/processo_seletivo/`, salvo indicação.

---

## 1. A resposta curta

**Quanto do conteúdo de um Edital decorre de estruturas e regras recorrentes do próprio sistema?**

Depende do que se conta, e as duas contas dão respostas opostas.

**A forma do documento é inteiramente do sistema (Fato).** A ordem das seções, a numeração de seções,
itens e tabelas, o agrupamento dos Perfis e das subseções comuns, as tabelas, as alíneas, os
cabeçalhos dos grupos de documentos, o fecho e a verificação de integridade saem do compositor
(`publicacoes/infrastructure/pdf.py`), e o gestor não os edita. O catálogo de seções é fixo
(`editais/domain/secoes.py`, l. 77) e a topologia não se altera (`editais/domain/validation.py`,
l. 488–530).

**O texto impresso é, na maior parte, redação livre (Fato, medido).** Recompondo cada PDF do corpus
com o próprio compositor, depois de trocar cada campo de texto livre por um marcador de uma palavra
(o método está no §1.1), a origem das palavras impressas é:

| Edital (simulado) | Palavras | Redação livre | Valores estruturados (números, datas, códigos) | Texto fixo do sistema |
|---|---|---|---|---|
| 91/2026 — pós-graduação EaD, sorteio, 4 polos | 1.436 | 58% | 10% | 32% |
| 92/2026 — tutores UAB, prova de títulos, 18 Perfis | 3.711 | 64% | 9% | 27% |
| 01/2026 — professor e técnico, `seed_demo` | 654 | 33% | 11% | 55% |

Sem os rodapés de página, que são repetição pura. A redação livre se divide em duas partes, e a
diferença importa: nas **seções textuais** (preâmbulo, disposições, recursos…) estão 420 palavras do
91/2026 (29% do total) e 600 do 92/2026 (16%); o restante da redação livre está **dentro das estruturas**
— nomes e descrições de Perfis, requisitos, atribuições, nomes e instruções de documentos, descrições de
Eventos, fundamentos legais das modalidades. O 01/2026 não tem seção textual nenhuma.

**Consequência para a hipótese (Fato).** O que o sistema escreve sozinho — 27% a 55% das palavras — é o
único texto que se repete **por construção**: a mesma regra declarada produz a mesma frase, em qualquer
Edital. O resto se repete só se as pessoas o repetirem. O inventário (ver
[`viabilidade.md`](viabilidade.md)) mostra que 65% das palavras do corpus caem em unidades que
reaparecem em outro edital (72% na versão 1 do catálogo, antes dos desdobramentos da rodada 2), mas só 8%
com **texto idêntico**: a recorrência é de função e de estrutura, muito mais do que de texto. Nenhum dos
dois números mede tradução reutilizável.

**A redação do sistema não aparece literalmente nos editais reais (Fato, rodadas 3 e 4).** Nos dois editais reais
do Cefor inventariados — 28/2026 e 59/2026, escritos fora do sistema —, nenhuma frase coincide com as frases que o
sistema gera (as linhas de origem C pura dos simulados); e 12% e 31% das palavras estão em linhas idênticas às do
**outro** edital real. Isso descreve a letra, e não o sentido: a mesma regra pode estar dita de outro modo, e se uma
tradução ou uma gravação serviriam às duas redações não foi medido ([`viabilidade.md`](viabilidade.md), §2.3 e §6).
*Correção da rodada 4:* a versão anterior deste parágrafo dizia que os reais “não confirmam o texto fixo como fonte
de reuso”, o que excedia a medida.

### 1.1 Como a medição foi feita

1. Os três editais foram publicados pelo fluxo real (§10), e o conteúdo canônico de cada Publicação foi
   extraído do banco.
2. Cada campo de texto livre do conteúdo foi trocado por um marcador de uma palavra (`XQaa`, `XQab`…),
   o mesmo marcador para o mesmo texto — para que os agrupamentos da `064` e da `068`, que comparam
   textos, continuem os mesmos.
3. O conteúdo marcado foi recomposto por `render_edital_pdf`, com a mesma Unidade, autoridade e data.
4. Palavras do PDF original − palavras não marcadoras do PDF marcado = redação livre. Entre as palavras
   restantes, as que têm algarismo ou são códigos declarados (Perfil, marco, modalidade) contam como
   valores estruturados; as demais, como texto fixo do sistema (rótulos, títulos, cabeçalhos e frases).

**Limite da medição (Fato).** Contar palavras mede volume, não dificuldade de tradução: uma tabela de
18 linhas tem muitas palavras e uma decisão linguística só; uma frase de recurso tem 25 palavras e
efeito jurídico.

---

## 2. De onde vem o conteúdo: o caminho até o PDF

```text
gestão (composição)                      publicação                                 leitura
──────────────────────                   ───────────────────────────                ─────────────────────
modelos do Edital  ──replace_draft──▶     submit_edital: edital_snapshot()  ──▶     DocumentoPublicado.bytes
(Perfis, Etapas,                          RevisaoEdital.content + hash              (servido como está)
 Cronograma, seções…)                     homologate_edital
                                          publish_edital: render_edital_pdf()
                                          Publicacao.canonical_content + hash
                                          VersaoConsolidada (1ª)
```

| Passo | Onde | O que acontece | Marca |
|---|---|---|---|
| Composição | `editais/application/draft.py` (`replace_draft`) e modelos em `editais/models/`, `processos/models.py` | o gestor preenche campos estruturados e textos livres | Fato |
| Instantâneo | `publicacoes/application/publish_edital.py`, `edital_snapshot` (l. 306–357) | o conteúdo vira um JSON canônico: Perfis e modalidades ordenados por `code`, decimais com quatro casas, seções na ordem do catálogo | Fato |
| Congelamento | `submit_edital` (l. 499–509) | a revisão guarda conteúdo, bytes canônicos e SHA-256 | Fato |
| Publicação | `publish_edital` (l. 710–774) | recusa se o hash mudou desde a homologação; compõe o PDF **uma vez**; grava `Publicacao`, `DocumentoPublicado` e a primeira `VersaoConsolidada` | Fato |
| Composição do PDF | `publicacoes/infrastructure/pdf.py` (3.803 linhas) | escreve o PDF à mão, página a página, a partir do JSON e do contexto do ato (Unidade, autoridade, data) | Fato |
| Leitura | `publicacoes/api/views.py`, `PublishedDocumentView` (l. 118–132) | serve os bytes gravados; nada é recomposto | Fato |

**O PDF publicado nunca é regenerado (Fato).** `render_edital_pdf` é chamado em três lugares só: na
publicação do Edital (`publish_edital.py`, l. 736), na publicação de uma Retificação
(`retificacoes.py`, l. 896) e na prévia da gestão (`interface/views.py`, l. 3502), que não se grava.
`Publicacao` e `DocumentoPublicado` recusam alteração no modelo e por gatilho (`publicacoes/models.py`,
l. 91–97 e 115–121).

---

## 3. Arquitetura relevante

| Peça | Caminho | Papel para a tradução |
|---|---|---|
| Compositor | `publicacoes/infrastructure/pdf.py` | escreve todo o texto fixo; decide ordem, numeração, consolidação e tabelas |
| Vocabulário da regra | `publicacoes/domain/vocabulario_da_regra.py` | frases de desempate (l. 21, 26) e de forma de convocação (l. 52), compartilhadas com o documento do resultado |
| Formatação humana | `publicacoes/infrastructure/humano.py` | datas (“13/10/2026, às 09h”), datas por extenso, decimais |
| Catálogo de seções | `editais/domain/secoes.py` | as 22 seções, títulos fixos; as redações-padrão retiradas na `054` (`REDACOES_PADRAO_RETIRADAS`, l. 128) |
| Campos do método do sorteio | `editais/domain/perfis.py`, `CAMPOS_DO_METODO` (l. 527) | rótulos Algoritmo, Fonte, Ocorrência, Quando, Derivação, Semente, Se faltar |
| Instantâneo | `publicacoes/application/publish_edital.py` | o conteúdo canônico, que é a fonte de todas as variáveis |
| Retificação | `publicacoes/application/retificacoes.py`, `publicacoes/domain/changes.py`, `consolidation.py` | alterações por caminho, consolidação, documento consolidado |
| Mutabilidade | `editais/domain/mutabilidade.py` (`CONTRATO`, l. 171–516) | o que pode e o que não pode ser retificado, campo a campo |
| Consulta pública | `publicacoes/api/public_urls.py`, `public_views.py` | recuperação de versões, documentos e alterações |
| Canonicalização | `shared/canonical.py` (`SCHEMA_VERSION = 17`, l. 152) | bytes canônicos e SHA-256 |

---

## 4. A estrutura do documento

### 4.1 As seções

**O catálogo tem 22 seções fixas (Fato; `editais/domain/secoes.py`, l. 77–117).** Dezessete são
textuais (redação livre) e cinco são geradas a partir de coleções:

| Ordem | Seção | Tipo |
|---|---|---|
| 1 | Apresentação (preâmbulo, sem número nem título) | textual |
| 2–5 | Disposições Preliminares · Informações Gerais sobre o Curso · Público-Alvo · Requisitos Gerais de Participação | textuais |
| 6 | **Perfis de Vaga** | gerada (`profiles`) |
| 7 | Da Inscrição | textual + frase do teto |
| 8 | **Documentos Exigidos para a Inscrição** | gerada (`documentRequirements`) |
| 9–10 | Da Verificação da Autodeclaração · Do Atendimento à Pessoa com Deficiência | textuais |
| 11 | **Etapas de Avaliação** | gerada (`stages`) |
| 12 | Critérios de Classificação | textual |
| 13 | **Cronograma** | gerada (`schedule`) |
| 14–20 | Dos Recursos · Da Convocação · Da Matrícula (+ Requerimento) · Do Acesso ao Curso · Da Homologação da Matrícula · Do Certificado · Do Prazo de Validade | textuais |
| 21 | **Anexos** | gerada (`attachments`) |
| 22 | Disposições Finais | textual |

**Seção vazia não sai (Fato; `pdf.py`, `_materializaveis`, l. 3218).** Textual sem texto e gerada sem
itens são omitidas. Exceção: Da Inscrição e Da Matrícula saem quando o sistema tem norma a acrescentar
nelas — o teto de inscrições e o Requerimento de Matrícula (`_norma_da_secao`, l. 3485; `054`, FR-984).
Por isso o 01/2026 tem uma seção “2. DA INSCRIÇÃO” com uma única frase, escrita pelo sistema.

**A numeração é posicional (Fato; `numeracao`, l. 3242).** O número de cada seção é a sua posição entre
as que saem. Consequência que pesa na tradução: **uma Retificação que esvazia ou preenche uma seção
renumera todas as seguintes** — e é o que a Retificação do 92/2026 faz (ver
[`editais/edital-92-2026/retificacoes.md`](editais/edital-92-2026/retificacoes.md)).

**Não há redação-padrão (Fato).** Até a `053` o catálogo trazia textos-padrão; a `054` os retirou
(`secoes.py`, l. 36–42), e um texto igual a um deles conta como vazio (`texto_redigido`, l. 152–155).
**O sistema, portanto, não sabe quando dois Editais trazem a mesma cláusula livre** — ela não tem
identidade além do próprio texto.

### 4.2 Itens, subitens, tabelas e anexos

| Elemento | Como sai | Fonte | Marca |
|---|---|---|---|
| Item de Perfil | `<seção>.<ordem> <código> — <nome>` | `_identificacao_do_perfil`, l. 2228 | Fato |
| Subseção comum (064, 068) | `<seção>.<n> Requisitos / Atribuições / Marcos classificatórios comuns aos Perfis X, Y e Z`, depois do último Perfil | `TITULO_DA_SUBSECAO`, l. 2306; `plano_de_consolidacao`, l. 2421 | Fato |
| Remissão do Perfil à subseção | “Requisitos: os descritos no item 5.5.” | `_perfis`, l. 2165–2181 | Fato |
| Item de Etapa | `<seção>.<ordem> <nome>` com pares Caráter, Peso, Nota mínima… | `_etapas`, l. 3005 | Fato |
| Alínea de documento | `a)`, `b)`… por grupo de destinatário | `_alinea`, l. 3066; `_documentos_exigidos`, l. 3166 | Fato |
| Tabela | “Tabela N — <legenda>”, numeração contínua no documento, cabeçalho repetido na quebra | `_Numerador`, l. 1101; `_tabela`, l. 1176 | Fato |
| Anexo | **só o rótulo**; o arquivo é artefato separado | `_anexos`, l. 3138; `editais/models/anexos.py` | Fato |
| Numeração dentro do texto livre | o que o gestor digitar (“11.1 Os recursos…”) | seção textual | Fato |

**Os anexos não estão no PDF (Fato).** O documento lista os rótulos; o conteúdo — modelos de
autodeclaração, fichas de avaliação, matriz curricular — é outro arquivo, servido por
`/api/v1/public/anexos/<id>`. **Lacuna:** este inventário não cobre o conteúdo dos anexos, que integram
o Edital e precisariam de tratamento próprio.

### 4.3 Um Perfil, ou vários

**A forma muda com a quantidade de Perfis (Fato; `_perfis`, l. 2128).** Com um Perfil, os dados saem em
pares rótulo-valor (`_perfil_unico`, l. 2194). Com dois ou mais, saem a tabela de Perfis, a matriz de
vagas por lista, as frases de reversão e de convocação uma vez, as tabelas de modalidades agrupadas por
identidade e, depois do último Perfil, as subseções comuns (068). O texto de cada regra é o mesmo, mas o
**bloco** que o contém muda — o que importa para qualquer composição audiovisual por blocos.

---

## 5. Conteúdos fixos, dinâmicos e condicionais

O texto que o sistema escreve sozinho é finito e está no código. Cada frase existe porque uma regra foi
declarada, e a variante que sai depende de um valor enumerado. Abaixo, as que o corpus mostra e as que
o código prevê sem que o corpus as tenha exercitado.

| Frase (forma) | Condição | Variantes no código | No corpus? | Fonte |
|---|---|---|---|---|
| “Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será destinado à respectiva ampla concorrência.” | reversão `ON_EXHAUSTION` | ou `ON_BALANCE` (“Na hipótese do não preenchimento total…”); prefixo “No Perfil X,” / “Nos Perfis…” quando só parte dos Perfis a declara | as duas espécies; o prefixo, não | `FRASE_DA_REVERSAO`, l. 2320; `_frases_consolidadas`, l. 2761 |
| “A convocação dos classificados será feita por publicação no endereço eletrônico do certame.” | `callForm = PUBLICATION` | ou `INDIVIDUAL_MESSAGE`; prefixo de alcance | as duas | `vocabulario_da_regra.py`, l. 52 |
| “Os marcos abaixo se aplicam a cada um desses Perfis separadamente…” | subseção comum de marcos | — | sim | `MARCOS_SEPARADAMENTE`, l. 2316 |
| “Ordem: por sorteio” / “pela pontuação combinada das Etapas” | `orderProduction` | ausente: a linha não sai | as duas | `FORMA_DA_ORDEM`, l. 1588 |
| “Combinação: soma ponderada das Etapas X (peso 2) e Y (peso 1)” | marco por pontuação | “média ponderada”; “(não pontua)” para Etapa decisória | só soma ponderada | `_combinacao`, l. 1321 |
| “Normalização: nenhuma” | idem | “pela soma dos pesos” | só “nenhuma” | l. 1277 |
| “Arredondamento: 2 casas decimais, meio para cima” | idem; nunca sob sorteio (067) | “meio para par”, “truncamento”, “sem casas decimais”, “1 casa decimal” | só a primeira | `_arredondamento`, l. 1337 |
| Bloco “Sorteio” (Método, Algoritmo, Fonte…) | marco por sorteio | “Método: próprio deste marco” e “— diverge do comum deste Edital”; remissão “o comum a este Edital, descrito no item N.” | só o comum | `_metodo_do_marco`, l. 1658; `_origem_do_metodo`, l. 1621 |
| “Habilitação: participam todas as inscrições submetidas” | sorteio sem Etapa de habilitação | “participam apenas as inscrições habilitadas na Etapa X” | só a primeira | l. 1579–1583 |
| “Recurso: Caberá recurso contra o resultado de “<marco>”, no prazo de N (extenso) dias corridos, contados da divulgação desse resultado.” | `appealWindow.admits` | **negativa expressa**: “Não caberá recurso contra o resultado de …”; sem nome, “Caberá recurso no prazo de …”; **sem declaração, nada** — ausência de cláusula, que não é proibição (§13.3) | a primeira e a ausência | `_janela_recursal`, l. 1411 |
| “Corte: Progridem para <Etapa> os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais N suplentes.” | `targetKind = FROM_VACANCY_TABLE` | alvo fixo (“os N (extenso) primeiros”); singular (“Progride… o 1 (um) primeiro”); sem Etapa; sem suplentes | derivado e fixo, com e sem Etapa | `_regra_de_corte`, l. 1455 |
| “Empate no corte: …” | `tieOutcome`, fora de sorteio | `ADMITS_SURPLUS` / `STRICT` | as duas | `EMPATE_NO_CORTE`, l. 1521 |
| “Continuação: …” | `continuation` | `ALLOWED` / `NONE` | as duas | `CONTINUACAO_DO_CORTE`, l. 1528 |
| “1º menor valor declarado em <dado>; sem o valor, fica por último neste critério” | critérios de desempate | três tipos × duas regras de ausência | três tipos, as duas ausências | `vocabulario_da_regra.py`, l. 21–26 |
| “Cada candidato poderá ter apenas 1 inscrição enviada neste Edital.” | teto declarado | “no máximo N inscrições enviadas”; sem teto, nada | só teto 1 | `teto_de_inscricoes`, l. 3426 |
| “O Requerimento de Matrícula será enviado no ato da inscrição.” + “Ao enviá-lo, o candidato declarará:” | Requerimento declarado | “quando o candidato for convocado” | só “no ato da inscrição” | `requerimento_de_matricula`, l. 3460 |
| “De todos os candidatos:” / “Dos candidatos ao perfil X:” / “Dos candidatos concorrentes na modalidade Y:” | destinatário do documento | “Dos candidatos ao perfil X concorrentes na modalidade Y:” | as três primeiras | `_titulo_do_grupo`, l. 3109 |
| “(facultativo)” | documento não obrigatório | — | sim | l. 3202 |
| “Versão consolidada. Publicado em …; retificado em …[, com vigência a partir de …].” | documento de Retificação | com e sem vigência futura; várias datas | as duas | `marca_de_consolidacao`, l. 1039 |
| Fecho, autoridade, verificação de integridade, rodapé | sempre | autoridade sem nome (só cargo) | as duas formas da autoridade | l. 3508–3593, 3721 |

**O texto fixo também é dinâmico em outro sentido: ele muda com a versão do compositor (Fato).** O
`pdf.py` teve 49 commits desde 28/08/2026. A `067` reescreveu a frase de recurso para nomear o
resultado; a `068` criou a frase dos marcos por Perfil e as subseções comuns. Uma frase “EXATA” é
exata **dentro de uma versão do compositor**: um vídeo gravado para a frase de antes da `067` não serve à
de depois. O catálogo registra, por isso, o commit e o hash de cada ocorrência.

---

## 6. O modelo interno não é o documento

**Há no conteúdo publicado informação que o PDF não imprime (Fato).** `classificationInformation` e
`callInformation` do Perfil, a `description` da modalidade, a `version` e a vigência da regra
normativa, o `status` dos Eventos, a ordem das linhas do quadro, os identificadores, o código dos dados
declarados. Quem traduzisse a partir do JSON traduziria coisa que o candidato não lê no ato.

**Há no PDF norma que o modelo não estrutura (Fato, observado no corpus).**

- **Numeração e remissões digitadas** no texto livre (“11.1 …”, “da prevista no item 11.1”) — o sistema
  detecta conflitos (`validation.py`, l. 3637–3791), mas o número continua sendo texto.
- **Regras dentro da descrição de um Evento**, que o sistema guarda como texto: “Inscrições pelo
  sistema, com isenção de taxa até o 5º dia.” (01/2026, Evento 1; não há modelo de taxa de inscrição);
  “Resultado final e abertura do prazo recursal.” (01/2026, Evento 3); a convocação “enviada por e-mail com
  48 horas de antecedência” (92/2026, Evento 10). Na rodada 2 cada uma ganhou unidade própria (LIB-0152,
  LIB-0153, LIB-0147).
- **“Código de inscrição”** (92/2026, seção 9) designando o Perfil num vocabulário próprio.
- **Regras repetidas em texto livre** que o sistema já publica estruturadas: classificação por sorteio e
  corte (91/2026, seção 10), concorrência a um só código (92/2026, seção 9, frente ao teto).

**O PDF não carrega estrutura acessível (Fato; auditoria do PDF de 08/10/2026, §4.5 e §7).** Sem tags,
sem idioma, sem título, sem marcadores; nas tabelas com células quebradas, a ordem de leitura intercala
as colunas. O efeito aparece no próprio texto extraído para este inventário — no Cronograma, “2
Divulgação da relação de 10/11/2026, às 17h — — inscrições que participarão do sorteio”. Para uma
composição automática, o PDF é fonte pior que o conteúdo canônico; para a fidelidade ao ato, é a única
fonte que vale.

**Hipótese.** A fonte certa para uma futura composição é o **par** conteúdo canônico + versão do
compositor: o primeiro dá as variáveis, a segunda determina o texto que elas produzem. O PDF gravado é a
prova do que foi publicado.

---

## 7. Versões, publicações e Retificações

**Uma Retificação é um conjunto de alterações por caminho (Fato; `publicacoes/domain/changes.py`).**
Operações `ADD`, `REPLACE` e `REMOVE` (l. 48) sobre caminhos como
`/profiles/id=<uuid>/immediateVacancies`, cada uma com o hash do conteúdo anterior. O que pode ser
retificado é decidido campo a campo em `editais/domain/mutabilidade.py`; número, ano, códigos, títulos
de seção e o momento do Requerimento não podem.

**O documento de uma Retificação é o Edital inteiro, consolidado (Fato; `retificacoes.py`,
l. 884–903).** Não há documento que liste só o que mudou: `DocumentoPublicado` é um por Publicação
(`publicacoes/models.py`, l. 102–104). O consolidado é composto do **conteúdo-base da Retificação mais
as alterações dela**, e não do conteúdo em vigor — uma Retificação elaborada sobre a versão original e
publicada depois de outra sai sem as mudanças da outra, e a marca de consolidação diz isso
(`_consolidacao`, l. 826–836).

**A vigência pode ser futura (Fato; `retificacoes.py`, l. 874–876).** Publicada hoje, com efeito em
quinze dias: durante esses quinze dias há dois documentos publicados e o vigente é o anterior. O
01/2026 do corpus tem exatamente esse caso (ver
[`editais/edital-01-2026/retificacoes.md`](editais/edital-01-2026/retificacoes.md)).

**Nem toda versão vigente tem documento (Fato; `interface/views.py`, l. 3515–3522).** A versão
consolidada que se rematerializa numa fronteira de vigência não tem PDF próprio.

**O que o candidato vê sobre o que mudou (Fato).** A página pública mostra a justificativa e, por
alteração, a operação, a entidade e o campo — sem valor anterior nem novo
(`portal/templates/portal/_documentos_do_edital.html`, l. 32–44; `publicacoes/domain/alteracoes.py`,
l. 7–11). Quem quer o texto exato abre o documento consolidado.

**A Retificação avisa, e não impede, conflito de numeração (Fato; `validation.py`, l. 3638–3643).**
No Edital original, número digitado que colide com o calculado impede a publicação; na Retificação, é
aviso (`typed_numbering_conflict_in_retification`). O 92/2026 do corpus foi retificado com quatro
avisos desses e publicado.

---

## 8. Recuperar o conteúdo exato de uma versão publicada

**É possível, e é a base de qualquer vínculo entre vídeo e ato (Fato).**

| O quê | Como | Fonte |
|---|---|---|
| Bytes do PDF de cada Publicação | `GET /api/v1/public/publicacoes/<id>/documento` (com `ETag` = hash do documento) | `publicacoes/api/views.py`, l. 118–132 |
| Conteúdo canônico de cada Publicação | `GET /api/v1/public/publicacoes/<id>` (`content`, `contentHash`, `documentHash`) | `public_serializers.py`, l. 47–78 |
| Versão vigente num instante | `GET /api/v1/public/editais/<id>/versao-vigente?em=<ISO com fuso>` | `selectors.py`, `effective_version`, l. 27–42 |
| Histórico do Edital | `GET /api/v1/public/editais/<id>/historico` | `selectors.py`, l. 146–183 |
| Alterações de uma Retificação | `GET /api/v1/public/retificacoes/<id>` (sem valor anterior) | `public_serializers.py`, l. 81–92 |
| Uma versão consolidada | `GET /api/v1/public/versoes/<id>` | `public_views.py`, l. 137–144 |

**O hash impresso é do conteúdo, não do arquivo (Fato; `pdf.py`, l. 3568–3593).** Os dois existem: o
“SHA-256 do conteúdo” do rodapé e da verificação, e o `document_hash` do arquivo, que não é impresso.

**Recompor um PDF antigo com o código de hoje não reproduz o antigo (Fato e Hipótese).** O compositor
é determinístico para a mesma entrada (`pdf.py`, l. 5–6; `tests/unit/publicacoes/test_pdf.py`), mas a
entrada inclui a versão do código, que muda (§5). Os bytes gravados são a fonte de verdade.

**Para a biblioteca de Libras (Hipótese).** Cada tradução precisaria guardar, no mínimo: o identificador
da Publicação, o hash do conteúdo, o hash do documento e a linha de cobertura de origem. Com isso, uma
tradução fica ligada a um ato, e não a “um texto parecido”.

---

## 9. Outros conteúdos vinculados ao Edital

O PDF do Edital não é o único texto que o candidato recebe sobre o certame (Fato; levantamento nos
módulos `divulgacao`, `avisos`, `convocacao`, `portal`, `inscricoes`, `requerimentos`):

| Conteúdo | Onde | Gravado? |
|---|---|---|
| Documento do Resultado (PDF) | `divulgacao/infrastructure/documento.py`, gravado em `divulgacao/application/publicar.py` | sim, na publicação |
| Avisos aos candidatos (três modelos iniciais, rodapé fixo) | `avisos/domain/modelos_iniciais.py`, `avisos/domain/mensagem.py` | — (e-mail) |
| Mensagem e página de convocação, fundamento da convocação | `convocacao/application/comunicar.py`, `convocacao/domain/fundamento.py`, `portal/templates/portal/convocacao.html` | — |
| Páginas públicas do Edital, do resultado e do sorteio | `portal/templates/portal/` | não |
| Comprovante de inscrição (PDF) | `inscricoes/infrastructure/comprovante_pdf.py` | não, sob demanda |
| Declarações no envio da inscrição e do Requerimento | `portal/templates/portal/revisao.html`, `requerimento.html` | hash do texto aceito |
| Textos de situação do candidato | `portal/situacao.py` | não |

Estes conteúdos **ficam fora** do inventário desta rodada, que é do Edital. Muitos deles são texto fixo
do sistema — e, portanto, o melhor terreno para unidades exatas —, mas precisariam de levantamento
próprio.

**Não existe hoje nenhum recurso de Libras no sistema (Fato).** Nenhuma ocorrência de VLibras, “língua
de sinais”, vídeo ou legenda nos templates; “Libras” só aparece como nome de curso nos Editais reais da
amostra (59/2026 e 78/2026) e em dados de teste. A acessibilidade trabalhada até aqui é a de leitor de
tela, teclado, contraste e celular (`specs/002-frontend-administrativo/`; auditoria do PDF, §7).

**A declaração do Requerimento tem vínculo de integridade com o português (Fato;
`requerimentos/models.py`, l. 170–173).** O portal guarda o hash do texto exibido no aceite. Um vídeo em
Libras da declaração não substitui esse texto, e a relação entre os dois é decisão institucional.

---

## 10. Os exemplos que o repositório tem

| Exemplo | Onde | Estado | Usado aqui? |
|---|---|---|---|
| Cenários A e B da auditoria do PDF (08/10) | `doc/auditoria-edital-pdf-2026-10-08/` (`pdf/`, `snapshots/`, `cenarios/`) | PDFs do código de 08/10, anteriores à `065`–`068`; o roteiro B original é recusado desde a `065` | roteiros A e B corrigido, reexecutados hoje |
| A e B pela `068` | `specs/068-consolidacao-por-perfil/demonstracao/` | composição atual, a partir dos instantâneos de 08/10 | conferência |
| Jornada da `067` (Edital 67/2026) | `specs/067-correcoes-de-norma-do-edital/demonstracao/jornada/` | anterior à `068`; sem seções textuais | não |
| B corrigido da `065` | `specs/065-conflitos-de-numeracao/demonstracao/` | anterior à `067`–`068` | não |
| Estado inicial (`008`) | `specs/008-composicao-institucional/referencias/` | obsoleto | não |
| `seed_demo` | `processos/management/commands/seed_demo.py` | gera quatro Editais pelo fluxo real | Edital 01/2026 |

**Todos são simulados (Fato).** Não há Edital real no repositório. Os cenários A e B foram calibrados
contra Editais reais do Cefor (28/2026 e 90/2026), que estão fora do repositório, e marcam
“DEMONSTRAÇÃO” no título e no preâmbulo. O corpus desta rodada foi gerado hoje, pelo código do commit
`bbc8e04c`, num banco isolado (`ps_libras_corpus`); nenhum banco de desenvolvimento ou de produção foi
tocado. Os PDFs e o conteúdo canônico estão em `editais/<edital>/fonte/` de cada pacote.

---

## 11. Oportunidades de reutilização que a arquitetura oferece

1. **As frases do sistema são unidades naturais (Fato).** Cada uma é uma constante do código, escolhida
   por um valor enumerado e com variáveis conhecidas. O catálogo pode apontar para a constante (“LIB-0093
   é `EMPATE_NO_CORTE['ADMITS_SURPLUS']`”), e saber exatamente quando ela sai.
2. **O conteúdo canônico tem todas as variáveis (Fato).** Datas, números, nomes de Etapas e de Perfis
   estão no JSON publicado, com tipo. Uma composição futura não precisaria extrair valores do PDF.
3. **A consolidação da `068` já reduz repetição (Fato).** Requisitos, atribuições e marcos idênticos
   saem uma vez; o 92/2026 caiu de 36 para 14 páginas. Menos repetição no documento é menos trecho a
   gravar — mas também mais remissões por número de item.
4. **O hash do conteúdo amarra tradução a ato (Fato).** Ver §8.
5. **As remissões do sistema são geradas (Fato).** “Os descritos no item 5.5” é calculado; o sistema
   sabe o destino. As remissões digitadas no texto livre, não.

## 12. Limitações e riscos

| Risco | Por que pesa para Libras | Marca |
|---|---|---|
| Texto livre sem identidade | a cláusula repetida entre Editais só se reconhece por comparação de texto | Fato |
| Frase do sistema muda com o código | vídeo gravado para uma versão do compositor pode não servir à seguinte | Fato |
| Numeração posicional e digitada | vídeo que sinalize “item 11.1” fica errado quando a numeração muda | Fato |
| Tabelas | leitura espacial; a ordem de leitura do PDF já intercala colunas | Fato |
| Códigos de Perfil e marco (INF-BJN, TP-01, FINAL) | identificadores de sistema sem leitura natural em Libras | Fato |
| Vocabulário do sistema (“recorte”, “marco classificatório”, “Continuação”, “Semente”) | a auditoria de 08/10, §5, propõe reescritas; a tradução herdaria o jargão | Fato |
| Valores por extenso entre parênteses (“2 (dois)”) | redação jurídica de duplicação; não é informação nova | Fato |
| Ausência de cláusula | marco sem recurso não imprime nada; isso não é proibição, e um roteiro-padrão que dissesse que cabe, ou que não cabe, recurso afirmaria o que o ato não diz (§13.3) | Fato |
| Anexos fora do PDF | o Edital tem partes que este inventário não cobre | Lacuna |
| Conteúdos fora do PDF (§9) | resultado, convocação e avisos também são comunicação oficial | Lacuna |
| Corpus só simulado | a recorrência de texto livre entre Editais reais não se mede com ele | Lacuna (ver [`viabilidade.md`](viabilidade.md), §3) |
| Contexto legal diferente por certame | a obrigação de tradução completa em Libras existe por norma explícita só para ingresso em curso (§13) | Fato |

---

## 13. Contexto legal por tipo de certame

**Verificado em 2026-10-11** nos textos compilados do Planalto: Lei nº 13.146/2015 (LBI), Decreto nº
5.626/2005, Decreto nº 9.508/2018 (com a redação do Decreto nº 12.533/2025), Lei nº 8.745/1993 e Lei nº
9.784/1999. Esta seção registra o que os textos dizem e onde se aplicam à primeira leitura. **Enquadrar cada
certame é decisão jurídica da instituição**, não desta análise.

### 13.1 O que cada norma diz

| Norma | Dispositivo | O que estabelece | Alcance |
|---|---|---|---|
| LBI | art. 30, caput | medidas obrigatórias “nos processos seletivos para ingresso e permanência nos cursos oferecidos pelas instituições de ensino superior e de educação profissional e tecnológica, públicas e privadas” | ingresso e permanência em cursos |
| LBI | art. 30, I a VI | atendimento preferencial; formulário de inscrição com campos para o candidato com deficiência informar os recursos de acessibilidade e de tecnologia assistiva; provas em formatos acessíveis; recursos de acessibilidade previamente solicitados; dilação de tempo; critérios de avaliação que considerem a singularidade linguística | idem |
| LBI | art. 30, VII | “tradução completa do edital e de suas retificações em Libras” | idem |
| LBI | art. 34, § 3º | vedada discriminação “nas etapas de recrutamento, seleção, contratação, admissão…” | trabalho |
| Decreto 5.626/2005 | art. 14 | instituições federais de ensino devem garantir às pessoas surdas acesso à comunicação, à informação e à educação nos processos seletivos | ensino |
| Decreto 5.626/2005 | art. 21, § 1º, I | o tradutor e intérprete de Libras atua nos processos seletivos para cursos na instituição | ensino |
| Decreto 5.626/2005 | art. 26 (red. Decreto 9.656/2018) | a administração federal deve garantir atendimento às pessoas surdas por meio da Libras e da tradução e interpretação | administração federal |
| Decreto 9.508/2018 | art. 1º; art. 4º, caput e §§ 1º e 3º; Anexo | direito de concorrer em concurso e em seleção da Lei nº 8.745/1993; adequação de critérios em todas as fases; tratamento diferenciado requerido na inscrição, em prazo do edital; fases com interpretação por terceiros registradas em áudio e vídeo; ao candidato com deficiência auditiva, prova gravada em vídeo por intérprete de Libras | concurso e contratação temporária federal |
| Lei 8.745/1993 | art. 2º, IV; art. 3º | admissão de professor substituto como necessidade temporária; recrutamento por processo seletivo simplificado | contratação temporária |
| Lei 9.784/1999 | arts. 56, 58, 59 e 69 | “Das decisões administrativas cabe recurso”; legitimidade dos interessados; prazo de dez dias, salvo disposição legal específica, contado da ciência ou divulgação oficial; os processos administrativos específicos regem-se por lei própria, com esta lei subsidiária | processo administrativo federal |

**Não encontrei**, no Decreto nº 9.508/2018 nem nas demais normas acima, dispositivo que exija a tradução
do **edital** em Libras fora do art. 30, VII, da LBI. A busca foi nos textos citados, não em toda a legislação.

### 13.2 Os editais do corpus

| Edital | Tipo de certame | Normas que parecem alcançá-lo | Tradução completa do edital e das retificações exigida por norma explícita? |
|---|---|---|---|
| 91/2026 | ingresso em curso de pós-graduação lato sensu do Ifes | LBI, art. 30 (todos os incisos); Decreto 5.626/2005, arts. 14 e 21 | **Sim** — LBI, art. 30, VII |
| 92/2026 | seleção de bolsistas de tutoria (UAB/CAPES), cadastro de reserva | não é ingresso em curso; à primeira leitura, tampouco contratação da Lei nº 8.745/1993. Normas gerais: Decreto 5.626/2005, art. 26; LBI, art. 34, § 3º, se a bolsa for tratada como trabalho | **Não encontrada** — questão jurídica |
| 01/2026 | seleção de professor substituto e técnico (`seed_demo`) | para o professor substituto, Lei nº 8.745/1993 e Decreto nº 9.508/2018; LBI, art. 34, § 3º | **Não encontrada**; o Decreto 9.508 trata das provas e fases, não do edital |
| 28/2026 *(real, rodada 3)* | ingresso em curso de pós-graduação lato sensu do Ifes, EaD | LBI, art. 30 (todos os incisos); Decreto 5.626/2005, arts. 14 e 21 | **Sim** — LBI, art. 30, VII. O Cefor publicou a tradução do edital (vídeo de 05/05/2026); a das retificações não aparece |
| 59/2026 *(real, rodada 3)* | ingresso em curso de formação inicial e continuada (FIC) do Ifes, presencial | à primeira leitura, LBI, art. 30 — curso “oferecido” por instituição de educação profissional e tecnológica; Decreto 5.626/2005, art. 14 | **Sim, à primeira leitura** — se o FIC estiver no alcance do art. 30, o que é questão jurídica |

O 01/2026 é demonstração: o enquadramento é ilustrativo, e o Perfil técnico não corresponde necessariamente
a uma hipótese da Lei nº 8.745/1993.

**Consequência para a hipótese.** Onde a tradução completa é obrigatória (o tipo do 91/2026), o reuso não
substitui a tradução integral: ele só pode servir à preparação e à produção **dentro** dela. Onde não há
norma explícita, o escopo da tradução é decisão institucional, e a comparação entre editais de tipos
diferentes não autoriza equivalência automática — a mesma frase pode ter outro peso jurídico.

### 13.3 Ausência de cláusula, proibição expressa e direito fora do edital

| Situação | O que é | Exemplos no corpus | O que a tradução não pode fazer |
|---|---|---|---|
| **Ausência de cláusula** | o edital nada diz | marco TEC-LAB sem recurso (E01-022); recurso contra o indeferimento da autodeclaração (91/2026); canal do recurso contra o sorteio (91/2026); acessibilidade na inscrição (91/2026 e 01/2026). Nos reais: verificação da pessoa com deficiência sem data, forma nem consequência (E28-096); intérprete na entrevista por videoconferência (28/2026) | preencher a lacuna, ou dizer que “não cabe” |
| **Proibição expressa** | o edital diz que não | indeferimento por excesso de páginas “sem possibilidade de interposição de recurso” (E92-154); recurso por e-mail ou fora do prazo (E91-085); por Correios ou outra forma (E92-209); a negativa “Não caberá recurso contra o resultado de …” (variante prevista no compositor, não observada). Nos reais: recurso “somente” contra dois atos (E28-114) ou um (E59-059), o que **proíbe** os demais por restrição; inscrição indeferida por dados ou arquivo “sem possibilidade de recursos” (E28-051, E59-039); Requerimento incorreto “não cabendo recurso” (E59-033) | omitir ou atenuar a proibição |
| **Direito previsto fora do edital** | vale independentemente da cláusula | recurso administrativo (Lei 9.784/1999, arts. 56 e 59, aplicação subsidiária, art. 69 — a confirmar para cada certame); medidas do art. 30 da LBI para o 91/2026; tratamento diferenciado do Decreto 9.508/2018 para o 01/2026, se aplicável | concluir, da ausência ou da retirada de uma cláusula, que o direito não existe |

**O compositor já distingue as duas primeiras (Fato).** `_janela_recursal` (pdf.py, l. 1411) não imprime
nada quando o marco nada declara — “marco que nada declara conserva as vias que a lei dá fora deste
sistema”, diz o comentário — e imprime “Não caberá recurso…” só quando a negativa é declarada. A retirada da
seção de atendimento à pessoa com deficiência do 92/2026 (v2) é ausência criada por Retificação: tira a
cláusula do edital, e não o direito que a lei eventualmente preveja.

**Informar direitos previstos fora do edital é decisão institucional.** A tradução traduz o ato; um material
complementar que explique direitos legais seria outro conteúdo, com outra responsabilidade.
