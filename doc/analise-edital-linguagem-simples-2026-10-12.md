# Edital em linguagem simples — análise exploratória

**Data:** 2026-10-12 (duas rodadas no mesmo dia) · **Natureza:** análise exploratória — **nada foi
implementado no produto**, nenhuma spec foi aberta, nenhum requisito ou regra de seleção foi alterado,
nada foi publicado.

**Depois da terceira rodada.** O usuário aprovou a estrutura e a direção tipográfica, e a spec do lote 1
foi aberta: [`specs/069-edital-linguagem-simples/`](../specs/069-edital-linguagem-simples/spec.md). Os
dois problemas herdados viraram achados próprios:
[requisito sem comprovante](achado-requisito-sem-comprovante-correspondente.md) e
[sorteio condicionado no texto](achado-sorteio-condicionado-no-texto-e-incondicional-no-sistema.md).

**Entregue pela `069`**, em 12/10/2026: os documentos compostos pelo produto a partir dos snapshots desta
amostra estão em [`specs/069-…/demonstracao/`](../specs/069-edital-linguagem-simples/demonstracao/), com a
conferência por enunciado refeita sobre o texto final (`equivalencia.md`) e as frases novas listadas para
aprovação. A amostra desta pasta continua como evidência da análise, e não é regravada.

**Terceira rodada.** O usuário aprovou a direção do lote 1 e pediu, antes da SPEC:

- tipografia que funcione em vários leitores;
- paginação que não separe informação relacionada;
- conferência de equivalência por regra, e não só por fato;
- cuidado ao classificar a frase do sorteio;
- decisões que não inflem a feature;
- o cenário B.

Tudo está no §9, refeito, e em [`equivalencia.md`](analise-edital-linguagem-simples-2026-10-12/equivalencia.md).
A amostra agora é composta por um roteiro **sem nada escrito para um cenário**, com fonte embutida, e
foi conferida em três motores de renderização.

**Segunda rodada.** Depois da primeira leitura, o usuário corrigiu cinco conclusões e deu diretrizes
(§7.1). Esta versão incorpora as correções — inclusive as que mudam o veredito: o primeiro lote passou a
incluir apresentação visual (§7.2), o HTML→PDF deixou de ser descartado (§5.3, §5.4), a acessibilidade
deixou de ser "decisão de exigir" e virou qualidade a verificar, e o endereço, o contato, os resultados
e o recurso foram procurados em fontes existentes antes de qualquer campo novo (§3.4). E traz a
**amostra** pedida: o cenário A como o gerador o publica hoje e como o lote 1 o comporia, com texto e
layout completos (§9), em [`analise-edital-linguagem-simples-2026-10-12/`](analise-edital-linguagem-simples-2026-10-12/).

> **Não vira escopo por estar escrito aqui.** As recomendações abaixo são insumo de priorização. Decidir
> se, quando e em que lotes fazer é do usuário (Constituição; [registrar a decisão, não tomá-la]).

Este relatório parte de dois trabalhos anteriores e **não os repete**: a
[auditoria do Edital em PDF de 08/10](auditoria-edital-pdf-2026-10-08.md) (achados ED-01 a ED-28 e as
frases L1–L17) e a [camada comunicativa do estudo de Libras](../docs/libras/camada-comunicativa.md)
(perguntas do candidato → enunciados normativos com fonte). Onde eles já respondem, este documento cita.

---

## 0. Protocolo

| Item | Valor |
|---|---|
| Commit | `a79ce463` (`main`, depois do PR #273). O compositor `pdf.py` não muda desde `a2924597` (068) |
| PDF atual de demonstração | o snapshot do cenário A da auditoria renderizado pelo `pdf.py` **de hoje**: 6 páginas, **idêntico byte a byte** a `specs/068-consolidacao-por-perfil/demonstracao/A-publicado-068.pdf`. É, portanto, o que o sistema publica hoje para aquela configuração. Cenário B: 14 páginas |
| Amostras lidas (de `~/Downloads`) | `gerado_sistema_libras.pdf` (8 p.), `edital_gerado.pdf` (17 p.), `edital_linguagem_simples_OK.pdf` (IFSP, 23 p.), `edital-linguagem-simpes-ifpe-2026-1.pdf` (IFPE, 30 p.), `EDITAL+33-2026+-+IFFLU…pdf` (IFF, 125 p.), `prototipo-edital-linguagem-simples.html` (mockup). Todos presentes. Também `solicitacao_melhoria_geracao_edital_revisada.pdf` (08/10), que pede o que a 064 já entregou |
| Extração | `pdftotext -layout`, `pdfinfo` (inclusive `-struct`), `pdffonts`, `pypdf` (marcadores, links, `/Lang`); páginas olhadas com `pdftoppm` |
| Experimento HTML→PDF | uma composição **temporária** do cenário A em HTML/CSS, impressa pelo Chrome 155 headless (`--print-to-pdf --generate-pdf-document-outline`). Ficou no scratchpad da sessão, fora do repositório (§5.3) |
| Amostra do lote 1 | os cenários A e B (e uma variante declarada de B) compostos pelas **primitivas do `pdf.py`** (não por outro motor), por um roteiro sem nada escrito para um cenário, com o texto livre reescrito como o Elaborador o reescreveria e seis extensões pequenas e declaradas do compositor, entre elas a fonte embutida. Roteiro, PDFs e páginas em [`analise-edital-linguagem-simples-2026-10-12/`](analise-edital-linguagem-simples-2026-10-12/) (§9) |
| Base legal | textos compilados do Planalto, lidos em 12/10/2026; busca no DOU (in.gov.br) de 17/11/2025 a 12/10/2026 (§2) |
| Convenção | **Fato** (observado no código, no PDF ou na lei), **Hipótese**, **Sugestão** |

**Não avaliado.** Leitores de tela reais; teste com candidatos; WeasyPrint (exige bibliotecas de sistema
que esta máquina não tem, e instalar seria mexer no ambiente); o IFF foi lido nas seções 1–4 e 9–12, não
nas 125 páginas; o brasão não entrou no protótipo HTML; a ABNT NBR ISO 24495-1 não foi lida.

---

## 1. Veredito

**O sistema já tem dados estruturados para a maior parte do esqueleto de um edital claro** — vagas por
Perfil e lista, reserva e reversão, documentos por destinatário, cronograma com datas, método do
sorteio, prazo de recurso por marco, desempate, forma de convocação, momento do Requerimento. Faltam
alguns dados (§3.4): o **domínio** do portal, sem o qual não se imprime o endereço do certame; o **tipo**
do evento do cronograma; o **momento** de entrega de cada documento; e a **autoridade recursal**, que a
decisão 018 deliberadamente não modelou como órgão.

**O trabalho tem três frentes, e nenhuma substitui as outras** (correção da segunda rodada — a primeira
dizia "o que falta não é layout", e a evidência não sustentava a frase):

1. **Redação.** As frases que o sistema escreve (origem C da auditoria) são trabalho **de uma vez**, com
   ganho em todo Edital futuro; o texto livre do Elaborador (origem D) é trabalho **recorrente**, que só
   guia, modelos e revisão reduzem.
2. **Organização da informação.** Onde cada regra mora: hoje a de recurso está em três lugares, a de
   classificação em quatro, e o Cronograma vem na seção 11 de 17. Isso é do compositor e do catálogo.
3. **Composição gráfica.** Hierarquia, densidade, tabelas, paginação e navegação. Um edital de palavras
   simples continua difícil de percorrer se os títulos não se distinguem do texto, se uma tabela se
   parte com uma linha no pé da página ou se não há sumário. A amostra do §9 mostra o quanto disso o
   compositor atual alcança: hierarquia por corpo e fio, resumo em caixa, sumário com página, matriz de
   vagas com total, listas com recuo pendente, tabelas coesas, marcadores, links, título e idioma.

**Formato recomendado: o próprio ato oficial, em PDF, gerado pelo compositor atual, com linguagem
simples e apresentação melhorada no mesmo lote (alternativa 1).** Não produzir agora uma segunda versão
explicativa.

- **A Lei nº 15.263/2025 não pede segundo documento.** Ela manda aplicar as técnicas "na redação de
  textos dirigidos ao cidadão" (art. 5º). A exigência de "duas versões — uma original e outra em
  linguagem simples" estava no texto da Câmara e **foi retirada no Senado** (§2.1).
- **Um segundo documento duplica o trabalho editorial a cada Edital e a cada Retificação**, e a
  Constituição proíbe que vagas, cronogramas, requisitos e regras "existam como dados independentes e
  divergentes" (princípio II). As versões complementares da amostra (IFSP e IFPE) mandam o candidato ler
  os dois documentos, e a do IFSP nem traz as vagas.
- **O IFF publicou o próprio ato em linguagem simples** — assinado pelo Reitor no SUAP, com sumário,
  perguntas como títulos e um quadro de recursos por objeto.
- **O compositor atual chega longe.** As amostras do §9 foram compostas com as primitivas dele, com
  extensões pequenas, uma fonte embutida como única dependência nova e bytes determinísticos. Elas
  conservam os 27 fatos de A e os 85 de B. As 87 regras conferidas por enunciado (`equivalencia.md`)
  mantêm condição, alcance e consequência, com três correções que essa conferência obrigou a fazer.

**HTML→PDF não está descartado.** O experimento do §5.3 mostrou que ele produz recursos estruturais
favoráveis à acessibilidade — marcação, idioma, marcadores, links, fontes embutidas — e que os bytes só
variam nos campos de data de criação, normalizáveis. O sumário sem página e a legenda separada da
tabela são problemas de implementação. Não são razões para adotá-lo agora, nem provas de que a
abordagem seja inadequada: o critério para revisitá-lo está no §5.4. **Nenhum dos dois caminhos,
sozinho, torna o documento acessível**: título, idioma, marcadores e links no PDF atual também não. A
experiência de leitura assistiva continua sem validação (§8).

**Próximo passo concreto:** com A e B aprovados como alvo, escrever a spec do lote 1 — redação,
organização e apresentação do edital oficial com a estrutura existente. Ficam decididas antes dela só a
ordem e os títulos do catálogo (D2) e a fonte (D8). As demais decisões do §7.4 não bloqueiam. O teste
com candidatos entra como validação do piloto, e não como condição para preparar a proposta.

---

## 2. Base legal verificada

### 2.1 O que as normas dizem

| Norma | Dispositivo (texto verificado) | Alcance para o Ifes |
|---|---|---|
| **Lei nº 15.263, de 14/11/2025** (DOU 17/11/2025; vigência na publicação, art. 9º) | art. 1º: "órgãos e entidades da administração pública direta e indireta de todos os Poderes" de todos os entes, "em sua comunicação com a população". Art. 4º **define**: técnicas para que "as palavras, a estrutura e o leiaute da mensagem permitam ao cidadão facilmente encontrar a informação, compreendê-la e usá-la". Art. 5º **lista as técnicas**: 18 incisos exemplificativos ("tais como"), entre eles ordem direta, frases curtas, termo técnico explicado, sigla por extenso, "listas, tabelas e recursos gráficos" (IX), o mais importante primeiro (X), voz ativa (XII), acessibilidade conforme a LBI (XVII) e "testar com o público-alvo se a mensagem está compreensível" (XVIII). Art. 6º: versão na língua indígena "sempre que possível". Art. 7º: **vetado** (encarregado de linguagem simples). Art. 8º: cada Poder define "diretrizes complementares e formas de operacionalização" | o Ifes é autarquia federal: **alcançado** |
| Lei nº 13.460/2017, art. 5º, XIV | "utilização de linguagem simples e compreensível, evitando o uso de siglas, jargões e estrangeirismos" | diretriz da prestação de serviços públicos; alcança |
| Lei nº 13.146/2015 (LBI), art. 30 | nos processos seletivos "para ingresso e permanência nos cursos oferecidos pelas instituições de ensino superior e de educação profissional e tecnológica": formulário com campos de acessibilidade (II), provas acessíveis (III)… e "tradução completa do edital e de suas retificações em Libras" (VII) | editais de **ingresso em curso**; enquadrar FIC e bolsista é questão jurídica ([Libras, §13](../docs/libras/auditoria-sistema.md)) |
| LBI, art. 63 | acessibilidade obrigatória "nos sítios da internet mantidos [...] por órgãos de governo", "conforme as melhores práticas e diretrizes de acessibilidade adotadas internacionalmente" | o **portal** e os documentos que ele serve. A lei não nomeia WCAG |
| LBI, art. 3º, V | a definição de "comunicação" inclui "a linguagem simples, escrita e oral" | conceito |
| Lei nº 14.129/2021, art. 3º, VII; Decreto nº 9.094/2017, art. 1º, VII; Lei nº 12.527/2011, art. 5º | "linguagem clara e compreensível a qualquer cidadão"; "linguagem clara, que evite o uso de siglas, jargões e estrangeirismos"; informação "em linguagem de fácil compreensão" | alcançam |
| Decreto nº 12.002/2024, art. 11 | regras de clareza (sentido comum, frases curtas, ordem direta) para atos normativos da administração federal, admitida a nomenclatura técnica | **incerto**: não verifiquei se edital de seleção de estudantes é "ato normativo" no sentido do decreto |

**Histórico legislativo (relevante para a decisão de formato).** O texto da Câmara, reproduzido no
Boletim Legislativo do Senado nº 110 (jul/2025), tinha um parágrafo único no art. 5º: documentos
oficiais dirigidos à população "deverão ter versão em linguagem simples, além da versão original". Segundo
a Agência Senado (12/03/2025), o relator retirou "a exigência de elaboração de duas versões". A lei
publicada não tem esse parágrafo. *Limitação:* não li o texto das emendas; a retirada se apoia na
notícia e no texto final, que concordam.

**Regulamentação complementar: não encontrada.** A busca no DOU por "linguagem simples" e por
"Lei nº 15.263" de 17/11/2025 a 12/10/2026 não achou decreto regulamentador nem portaria do MEC ou do
Executivo que operacionalize o art. 8º. Não verifiquei guia oficial do governo federal posterior à lei
(a página do gov.br sobre o assunto não abriu). A busca textual do DOU pode falhar: é indício forte, não
prova. Normas internas do Ifes não foram pesquisadas.

**Sobre edital oficial × versão explicativa.** Nenhuma norma lida trata da relação entre os dois. As
regras de publicação de edital no DOU (Decreto nº 9.739/2019, art. 41; Lei nº 14.965/2024) são de
**concurso para cargo**, não de seleção de estudantes. O único texto que exige uma versão paralela é a
LBI, art. 30, VII — e exige **tradução completa** em Libras, não resumo.

### 2.2 Obrigação, orientação e escolha

| Categoria | O que entra |
|---|---|
| **Obrigação legal** | aplicar técnicas de linguagem simples nos textos dirigidos ao cidadão (Lei 15.263, art. 5º), com teste de compreensão entre as técnicas listadas (XVIII); linguagem simples na prestação de serviço (Lei 13.460); site acessível (LBI, art. 63); nos editais de ingresso em curso, as medidas do art. 30 da LBI |
| **Questão a confirmar com a área jurídica** | se o edital, ato normativo, é "texto dirigido ao cidadão" para o art. 5º — a lei não diz, e o mais prudente é tratá-lo como se fosse; se o Decreto 12.002/2024 alcança o edital; equivalência formal entre o ato e qualquer versão derivada; o estatuto de um "resumo" impresso dentro do ato |
| **Norma técnico-administrativa** | eMAG (Portaria SLTI nº 3/2007, compulsória para o SISP; versão e vigência atuais **não verificadas**) |
| **Orientação técnica, não lei** | WCAG, PDF/UA (ISO 14289), ABNT NBR ISO 24495-1, guia da Enap. Nenhuma conformidade é declarada aqui |
| **Escolha de produto** | ter ou não segundo documento; HTML, PDF ou ambos; motor de renderização; resumo no ato; títulos em forma de pergunta |

**Não se conclui** que a lei exija HTML, segundo edital, sumário ou qualquer formato específico.

---

## 3. Diagnóstico do código

### 3.1 O caminho do Edital

| Passo | Onde | O que importa para esta análise |
|---|---|---|
| Cadastro | `processos/application/commands.py:79` `add_edital` (`edital:criar`); `Edital` em `processos/models.py:35` | número, ano, título, descrição, teto, momento e declaração do Requerimento |
| Composição | assistente em `interface/views.py:997` (`ETAPAS_COMPOSICAO`: identificação → perfis → cronograma → etapas → classificação → inscrição → anexos → conteúdo → revisão); `replace_draft` em `editais/application/draft.py:163` (`edital:elaborar`) | o texto livre entra na etapa "conteúdo", em 16 seções textuais, cada uma uma `textarea` (`SecaoEdital`, `editais/models/secoes.py:6`) |
| Revisão (HTML) | `interface/revisao.py` `blocos()` :1036, a partir do snapshot | **já é uma representação HTML do mesmo conteúdo**, e reusa as frases do `pdf.py` (:44-61) para não divergir |
| Submissão e homologação | `publicacoes/application/publish_edital.py` `submit_edital` :477, `homologate_edital` :533 | o snapshot (`edital_snapshot` :116) é serializado (`shared/canonical.py:86`) e recebe SHA-256 |
| Publicação | `publish_edital` :681 (`edital:publicar`) | segregação Elaborador/Homologador/Publicador (:704); recusa se o snapshot divergir do homologado (:711); **o PDF sai do snapshot homologado** (:736), não das tabelas; bytes gravados em `DocumentoPublicado` |
| Retificação | `publicacoes/application/retificacoes.py`: `create_retification` :378, `publish_retification` :853 | alterações por caminho sobre a versão consolidada; o PDF consolidado é **regerado inteiro** com marca de consolidação (:896-903). Documento publicado não se regenera |
| Portal | `portal/views.py` `selecao` :395, a partir da versão vigente | mostra período, vagas por Perfil, requisitos, modalidades (só nomes), documentos anunciados, teto, sorteio, cronograma, "O que mudou" e o link "Ler o Edital completo (PDF)" (`selecao.html:58`). **Nenhuma seção textual aparece em HTML no portal** |

### 3.2 O compositor

`publicacoes/infrastructure/pdf.py` (3.803 linhas), entrada `render_edital_pdf` (:3670), escritor de
baixo nível `render_documento` (:3731), compartilhado com o comprovante de inscrição e o documento de
divulgação. Modelo intermediário: uma lista de itens em `Composicao` (:644) — texto, régua, blocos
coesos, tabelas — paginada em duas passadas (`paginar` :783) e escrita direto em operadores PDF.

| Tem | Não tem (Fato, conferido no código e no arquivo) |
|---|---|
| quebra por largura real (Helvetica base-14), justificação, negrito, listas, tabelas com grade, cabeçalho repetido na quebra, total, numeração calculada de seções e tabelas, rodapé com página e hash, brasão, fecho, autoridade, integridade, prévia com marca, **determinismo byte a byte** (há teste que prende os bytes) | `/Info` (título), `/Lang`, tags (`/StructTreeRoot`), marcadores (`/Outlines`), links (`/Annots`), sumário, fontes embutidas e `ToUnicode`, recuo pendente, controle de viúvas, `Content-Disposition` no download do publicado |

**O que já está pronto para outra apresentação.** `plano_de_consolidacao` (:2421) devolve dados puros
(`TabelaDeVagas`, `SubsecaoComum`, `GrupoDeModalidades`); as frases da regra (`_janela_recursal`,
`_regra_de_corte`, `_habilitacao_ao_sorteio`, `teto_de_inscricoes`, `requerimento_de_matricula`,
`FRASE_DA_REVERSAO`, `vocabulario_da_regra.py`) devolvem texto e já são reusadas pela Revisão;
`numeracao`, `itens_do_documento` e `tabelas_do_documento` são funções do snapshot. Já `_perfis`,
`_marcos`, `_cronograma`, `_etapas` e `_documentos_exigidos` escrevem direto na `Composicao`. Separá-las
em "dado" e "desenho" é o custo real de qualquer segunda apresentação.

**Onde mora o texto fixo.** O catálogo de 22 seções é global (`editais/domain/secoes.py:77`), sem nada
por unidade nem por família de edital. **Desde a 054 nenhuma seção textual nasce com redação padrão**
(FR-983: "o documento só publica texto que alguém escreveu para ele"). Isso pesa sobre qualquer
proposta de "textos fixos revisados" para as seções textuais (§6.1).

**Permissões** (`interface/identidade.py:20`): Elaborador (`edital:elaborar`, `edital:submeter`,
`retificacao:elaborar`), Homologador (`edital:homologar`), Publicador (`edital:publicar`), Gestor. A
revisão humana de linguagem tem lugar natural: o Homologador já confere o conteúdo antes de publicar.

### 3.3 Matriz de origem das informações

Origem: **E** estruturado · **En** enumerado · **L** texto livre · **F** texto fixo no código · **—** ausente.
"Sem inferência" = dá para apresentar com clareza usando só o dado e frases fixas revisadas.

| Informação | Origem | Onde | Consumidores hoje | Sem inferência? |
|---|---|---|---|---|
| Público e requisitos | L + lista de L por Perfil + fatos declarados (En) | seções `publico-alvo`, `requisitos-gerais`; `PerfilVaga.requirements` (`editais/models/perfis.py:20`); `FatoDeclarado` (:192) | PDF, portal (cartão do Perfil), Revisão | lista: sim, item a item. Clareza do conteúdo: **só com reescrita humana**. Nível de escolaridade, idade etc. não são campos |
| Vagas por Perfil/polo/modalidade, cadastro de reserva | E + En | `immediate_vacancies`, `locality` (texto livre — **"polo" não é conceito do modelo**), `reserve_type`/`reserve_limit`; `LinhaDoQuadroDeVagas` (:126); `RegraNormativa` (:376) | PDF (matriz da 068); portal só total e nomes das modalidades | **sim** — é matriz. Mas o rótulo "polo", "turma" ou "curso" não sai do dado (L16 da auditoria) |
| Documentos e momento da entrega | E (nome, destinatário) + L (instruções) | `DocumentoExigido` (`editais/models/documentos.py:21`), recorte por código (044) | PDF (agrupado por destinatário), portal (antes do login), upload | o quê e de quem: **sim**. **Quando: não** — todo documento é, por construção, de inscrição; os da matrícula ou da etapa documental são texto livre. Documento condicional não existe ([achado](achado-documento-condicional-no-portal.md)) |
| Inscrição | período E (`is_registration_period`), teto E, canal L, taxa —, declarações F (template do portal) | `EventoCronograma` (`editais/models/cronograma.py:28`); `max_inscricoes_por_candidato` | PDF, portal | período e teto: sim. **Canal: não** (ED-09). Taxa: nada a mostrar. As declarações aceitas no portal não estão no Edital |
| Etapas e ordem | E | `EtapaAvaliacao` (`etapas.py:23`); o sorteio vem do marco, não é Etapa | PDF; o portal **não lista as Etapas** | cada Etapa, sim; o fluxo inteiro (sorteio → análise) precisa ser montado do marco + `governedStage` + cronograma — é derivação determinística, mas ainda não existe |
| Sorteio / pontuação | En + E; fonte, ocorrência e derivação em L | `metodo_de_sorteio_comum` (`processos/models.py:112`), `MarcoClassificatorio` (`perfis.py:228`) | PDF; portal (sorteio público, verificação) | **sim**, por tabelas de frases. O barema de uma Etapa não é modelado |
| Cotas, verificação, reversão | cotas E; reversão En; verificação **L** | `ModalidadeConcorrencia`, `RegraNormativa`, `especie_de_reversao` (`perfis.py:66`); seções `verificacao-autodeclaracao`, `atendimento-pcd` | PDF; portal só nomes | quadro e reversão: sim. Heteroidentificação e comprovação PcD: **só com texto humano** |
| Desempate | En + parâmetros | `CriterioDesempate` (`perfis.py:331`); `vocabulario_da_regra.py:21` | PDF | **sim** — mas a frase atual é a L4 ("menor valor declarado em Data de nascimento") |
| Recursos | prazo E por marco; objeto = nome do marco; canal e julgador **L/—** | `janela_recursal` (`perfis.py:289`); seção `recursos`; Evento de cronograma | PDF (frase da 067), portal (recorrer) | prazo do marco: sim. **Três fontes que podem divergir** (marco, seção, Evento) — e divergem no cenário A |
| Resultado | Evento com tipo **L** | `EventoCronograma.type` é texto livre (`cronograma.py:26`) | portal (resultados publicados), PDF do resultado | datas: sim. "Preliminar"/"final" no Edital: **não tipado** |
| Convocação | forma En; suplentes e continuação E; prazo de resposta **—** no Edital | `forma_de_convocacao` (`perfis.py:83`), `regra_de_corte` | PDF, portal | forma e suplentes: sim; prazo: só texto livre |
| Matrícula | momento En, declaração L publicada como norma; documentos e prazos L | `requerimento_momento`, `requerimento_declaracao` (`processos/models.py:78`) | PDF, portal | momento e declaração: sim; o resto: não |
| Anexos | E (rótulo + arquivo) | `AnexoEdital` (`anexos.py:85`) | PDF (rótulos), portal (download) | sim, como lista |
| Contato | **—** no Edital; configuração global + L | `PORTAL_ATENDIMENTO` (`config/settings/base.py:225`); `Unidade` não tem contato | portal (duas telas) | só o canal global |
| Cronograma, unidade, autoridade | E (datas, local); tipo L; unidade e autoridade fora do snapshot, congeladas na `Publicacao` | `EventoCronograma`; `Unidade` (`unidades/models.py:25`); `contexto_do_ato.py` | PDF, portal | datas: sim. Rótulo do evento é o que a comissão escreveu |

**Leitura da matriz.** As linhas "sim" cobrem o **esqueleto** que o candidato mais consulta: quanto, onde,
quando, o quê levar, como se ordena. As linhas "não" se concentram em **onde e como agir**: canal de
inscrição, canal de recurso, onde sai o resultado, contato. É a mesma conclusão da auditoria (tarefas 5,
7 e 8 do §10 dela), e nenhum redesenho a resolve — ela pede dado (ED-09) ou texto da comissão.

### 3.4 Fontes existentes, antes de qualquer campo novo

Pedido da segunda rodada: procurar a fonte adequada antes de propor campo. Resultado, item a item:

| Informação | O que já existe | Escopo | No snapshot? | Avaliação |
|---|---|---|---|---|
| **Onde se inscrever** (o "endereço eletrônico do certame") | a inscrição **é** no portal do sistema: rota estável `/selecoes/<editalId>/` (`portal/urls.py:120`), e `editalId` está no snapshot (`publish_edital.py:308`). Os avisos da 066 e os e-mails de convocação montam o link a partir da requisição (`interface/avisos.py:63-72`) | por Edital (caminho); **por implantação (domínio)** | o caminho sim; **o domínio não** | o caminho existe. **Falta o domínio**: não há `SITE_URL` nem nada parecido nas configurações, só `ALLOWED_HOSTS`, que é lista de permissão. E há um segundo obstáculo: a rota usa o **UUID** do Edital, e "nada vaza de UUID" é invariante do documento (008). Imprimir o endereço pede uma configuração de domínio congelada na `Publicacao`, como a Unidade (060), e uma rota legível (por número e ano). A FR-027a da 020 proíbe só o endereço **de download de anexo**, mas a razão dela — o domínio que muda — pesa aqui e tem de ser respondida |
| **Contato** | `PORTAL_ATENDIMENTO` (`config/settings/base.py:225`, obrigatório em produção): e-mail, telefone ou página, já usado no portal, no rodapé dos avisos e nas convocações | por implantação | não | **a fonte existe**; para o documento, precisa ser congelada na Publicação. Contato por Edital ou por Unidade não existe — hoje o Elaborador o escreve nas disposições, e isso pode continuar |
| **Onde sai o resultado** | o sistema publica os resultados ele mesmo, e a página da seleção os lista (`portal/views.py:457`; 017, FR-050) | por Edital | o caminho sim | **a fonte basta**, com o mesmo domínio da linha 1. **Exceção:** a convocação "por publicação" é ato externo; o operador registra depois onde publicou (`convocacao/models.py:374-382`; 050). Para ela, "no endereço do certame" pode não ser o portal |
| **Canal do recurso** | o recurso contra o resultado do marco é apresentado no portal (`portal/views.py:1676`; 018 §1) | estrutural | implícito | **corrigido na terceira rodada:** o canal é estrutural no sistema, mas o Elaborador pode indicar outro (em B, um formulário eletrônico). Gerar "pelo sistema de inscrição" criaria conflito; a frase gerada não diz canal, e a divergência é candidata a aviso na Revisão (§9.5) |
| **Quem julga o recurso** | papel `julgador` (`interface/identidade.py:95`); quem decidiu fica registrado depois (`DecisaoRecurso.decidido_por`). A decisão 018 §5 escolheu de propósito não ter comissão recursal | por papel, não por Edital | não | **lacuna deliberada**: não há o que imprimir sem reabrir a 018. Se o Edital precisar nomear a instância, é texto do Elaborador |
| **Tipo do Evento** | só `is_registration_period` e o vínculo Etapa→Evento são estruturados; a heurística por "recurs" serve só a aviso (`validation.py:1611`) | — | — | **lacuna real** para um quadro de recursos derivado e para validar a ordem sorteio × inscrições |

**Consequência para o lote 1.** O período de inscrições (do Evento marcado) e o contato
(`PORTAL_ATENDIMENTO`, congelado) podem sair gerados sem campo novo; o canal do recurso, não (§9.5). O endereço
precisa de **uma** configuração nova — o domínio — e de uma rota legível. Na amostra, ele aparece com o
formato que essa fonte produziria e está marcado como exemplo.

---

## 4. Crítica das amostras e do mockup

### 4.1 Ato oficial ou versão complementar?

| Amostra | Natureza | Evidência |
|---|---|---|
| IFSP (23 p.) | **complementar** | "tem como referência o Edital IFSP nº 211 [...] e não o substitui"; "Cabe ao candidato ler tanto este documento quanto o edital original" |
| IFPE (30 p.) | **complementar**, de dois atos | "tem como referência o Edital IFPE Nº 47/2025 [...] e o Edital IFPE Nº 48/2025"; matrícula remetida a um terceiro edital |
| IFF (125 p.) | **o próprio ato** | "EDITAL 33/2026 – IFFLU, DE 19 DE AGOSTO DE 2026 – EDITAL DE ABERTURA", assinado no SUAP pelo Reitor e pelo Pró-Reitor, com código verificador |
| `gerado_sistema_libras.pdf`, `edital_gerado.pdf` | o ato, gerado pelo sistema | anteriores à 054 (22–23/09): **não representam o gerador de hoje** |
| mockup | demonstração de leitura, não ato | "PROTÓTIPO — NÃO É UM EDITAL PUBLICADO" |

O que cada um ensina, com o que é escolha de produto separada do que é técnica de linguagem simples:

- **IFF** — títulos em pergunta ("COMO SE INSCREVER?"), sumário clicável, barra de seções em toda página,
  **"Cronograma de recursos"** (Etapa · Motivo · Data do recurso · Data do resultado), anexos de passo a
  passo, PDF marcado (LibreOffice). Custos: 125 páginas (25 só de conteúdo de prova), uma página inteira
  por título de seção. **Prova que o ato oficial pode ser escrito em linguagem simples, e que linguagem
  simples não é sinônimo de curto.**
- **IFPE** — o sumário separa "informações gerais" de "para quem vai concorrer por prova / por análise de
  desempenho": é o padrão de que um Edital com muitos Perfis precisa. Exemplo numérico de renda per
  capita. "Datas importantes (seu caminho até o IFPE)". Sem tags (InDesign).
- **IFSP** — remete ao item do original em cada bloco ("item 11.5 do EDITAL IFSP N.º 211/2025"): boa
  rastreabilidade. Mas **não traz as vagas** ("veja o Anexo I do EDITAL IFSP N.º 211"), e é ilustrado,
  sem tags. Exige que o candidato leia dois documentos.

### 4.2 O PDF que o sistema gera hoje

Os dois PDFs anexados são de antes da 054; o de hoje (§0) já resolveu seções vazias, repetição por
Perfil (068), quadro zerado e arredondamento sob sorteio (067) e numeração digitada (065). **O que
persiste**, no PDF atual do cenário A:

| Achado | Classe | Referência |
|---|---|---|
| Vocabulário do sistema: "Marcos classificatórios", "Corte", "recorte", "Continuação", "Semente", "Derivação", "inscrições submetidas" | problema editorial | ED-05, L1–L13 |
| "endereço eletrônico do certame" citado quatro vezes e nunca informado | lacuna de dados | ED-09 |
| Cronograma só na seção 11 de 17; nada na abertura aponta para ele | problema editorial (catálogo) | auditoria §5.1, item 7 |
| Seção 10: "**Havendo mais inscritos que vagas**, a ordem [...] será definida por sorteio"; marco 5.6: "participam todas as inscrições" | **divergência entre o texto e o sistema**, não contradição entre as frases (terceira rodada): uma diz *quando* há sorteio, a outra *quem* participa. Mas o sistema sorteia sempre — um marco por sorteio não tem outra fonte de ordem (`classificacao/application/emissao.py:231`) —, e a condição do Elaborador nunca foi modelada (o Edital 78/2026 real a tem) | [equivalência](analise-edital-linguagem-simples-2026-10-12/equivalencia.md), achado 3 |
| Recurso: marco diz 2 dias contra o sorteio; seção 12 diz recurso contra a análise documental; Cronograma tem uma só janela, sem objeto | inconsistência normativa conhecida; a 067 só avisa | ED-02 (resto aberto) |
| Sem título, idioma, marcadores, links; fontes não embutidas | defeito técnico de acessibilidade | ED-07, ED-14 |
| "Realização: 17/11/2026, às 08h a 24/11/2026, às 17h"; "às 00h" | problema editorial | L14, ED-28 |
| "PERFIS DE VAGA" e "Cadastro reserva" num edital de curso | problema editorial (catálogo) | L16 |

**Dados inconsistentes das amostras antigas** (não são defeito do gerador; seriam do Edital):
no 78/2026, inscrições de 04/08 a 03/10 com publicação em 05/08, habilitados em 04/09 e sorteio em 09/09
— o sorteio acontece com inscrições abertas; no 149/2024, inscrições até outubro de 2026 e sorteio em
fevereiro de 2025. **Lacuna de dados que isso revela:** como o tipo do Evento é texto livre, o sistema
não sabe qual Evento é o sorteio e **não tem como** recusar essa ordem
([achado correlato](achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md)).

### 4.3 O mockup

**Como ler os achados abaixo** (correção da segunda rodada). O mockup se apresentou como demonstração
incompleta. As omissões confirmam que ele não pode ser **transposto** como edital oficial, mas não
invalidam a sua **organização visual**, e é ela que a amostra do §9 aproveita, com as regras completas
de volta. Seis estruturas dele passaram à amostra:

- títulos em pergunta, onde ajudam;
- um resumo de abertura;
- navegação por seção, que no PDF vira sumário com página e marcadores;
- o comum dito uma vez;
- um quadro único por polo;
- um destaque para o que o candidato faz.

Uma sétima, a origem citada em cada bloco, cabe na tela de Revisão, e não no ato. A recusa de mostrar
um cronograma incoerente é papel da validação.

O que **não** passou: a hierarquia de página de divulgação, com título-chamada, *tags* e cartões, que
num ato oficial impresso compete com o anúncio do ato; e o conteúdo recolhido em `<details>`, que o PDF
não tem como recolher. A pergunta que a segunda rodada mandou fazer — "as regras completas continuam
compreensíveis nessa estrutura?" — tem resposta na amostra: o §8 da proposta reúne as quatro peças da
seleção e mantém o quadro técnico do sorteio inteiro e visível. Ela passa de uma página e meia, e
continua legível.

**Achados** (classe entre parênteses):

| # | Achado | Evidência |
|---|---|---|
| M1 | **Omite uma condição de participação.** "Quem pode: Pessoas com graduação" — o 149/2024 admite quem ainda não colou grau, com declaração da data de colação anterior ao início do curso e comprovação em até 30 dias (problema editorial) | `edital_gerado.pdf`, seção 3 e documento "e)" |
| M2 | **Troca a regra das cotas por um aviso.** "Os critérios [...] precisam ser conferidos no edital completo" — some a concorrência simultânea, a regra de que o cotista sorteado na ampla não é computado na reserva, a reversão por polo, a CLVA, a instância recursal (CPVA) e a consequência de não comparecer (permanece só na ampla) (problema editorial: supressão de condição) | `edital_gerado.pdf`, seção 7 |
| M3 | **Esconde consequências da matrícula.** No 149/2024, quem não acessar o AVA em 5 dias corridos é desistente; no 78/2026, regularização em 2 dias úteis e falta na primeira semana cancelam a matrícula. O mockup diz "regras específicas [...] precisam ser conferidas na versão oficial" (problema editorial) | seção 10 de cada amostra |
| M4 | **Recurso incompleto.** Omite "não será aceito o envio de novos documentos" e que o recurso cabe "somente" contra dois atos — a restrição é proibição dos demais (problema editorial) | `edital_gerado.pdf`, seção 9 |
| M5 | **Regra de auditoria em elemento recolhido.** O método do sorteio fica em `<details>`, aberto na impressão por JavaScript (`beforeprint`). Um renderizador sem JavaScript ou outro leitor não o abre; e na tela o candidato não vê. Separar o técnico da leitura principal é bom; recolher, não (defeito visual/editorial) | script do mockup |
| M6 | **Escolhe em silêncio entre duas regras.** Repete "Se houver mais inscrições do que vagas" quando o próprio PDF diz também "Será realizado sorteio a fim de determinar a ordem" (inconsistência normativa da amostra) | `gerado_sistema_libras.pdf`, seção 7 |
| M7 | **Omite requisitos e o cadastro de reserva.** Some "Ter habilidade no uso do computador" (78/2026), "Conhecimentos intermediários de Informática" (149/2024), o cadastro de reserva "ilimitado" e a análise de até 30/15 suplentes por código de vaga (problema editorial) | quadros de Perfis |
| M8 | **Quadro de polos sem percentual, fundamento e reversão**, e eles não aparecem em outro lugar da página (problema editorial) | seção 02 do exemplo de pós |
| M9 | **Marca desenhada para o mockup** (grade 3×3 verde-limão) e paleta própria, que lembram o IF sem ser os ativos oficiais; o título "Aprenda Libras no Cefor" é chamada de página de divulgação, não título de ato (defeito visual / identidade) | CSS `.mark` |
| M10 | **"Selecionado" ambíguo.** "O que acontece se eu for selecionado?" junta classificação no sorteio, deferimento documental e matrícula, que são três situações (problema editorial) | seção 08 do exemplo de Libras |
| M11 | Cronogramas bloqueados com "A revisar" (dado inconsistente da amostra) — correto como demonstração; no produto, a recusa é da validação, não da página | seção 06 |

**Evidências contra a proposta inicial** (a página HTML como **produto**, não como hipótese visual):
1. Seis dos onze achados (M1–M4, M7, M8) são **supressão de regra**, e nenhum deles é de layout. Parte
   da clareza da página vinha de estar incompleta. A amostra do §9 é o teste do inverso: a estrutura,
   com as regras todas.
2. As frases que o mockup "explica" ou já existem no sistema (o 78/2026 de hoje sairia com "Participam
   do sorteio todas as inscrições enviadas" se L9 fosse adotada) ou dependem de texto livre que só a
   comissão pode reescrever.
3. O mockup é um segundo texto: a cada Retificação alguém teria de reescrevê-lo.
4. O portal **já é** uma visão HTML derivada do mesmo conteúdo, e já mostra vagas, cronograma e
   documentos. O que falta nele é derivável (§6.2), não redigível.

---

## 5. Alternativas

### 5.1 Comparação

| Critério | 1. Melhorar o PDF oficial no gerador atual | 2. Compor em HTML/CSS e gerar o PDF oficial | 3. Ato oficial + versão explicativa complementar | 4. HTML e PDF integrais do mesmo ato |
|---|---|---|---|---|
| Ganho ao candidato | alto: frases, ordem, hierarquia, tabelas, sumário e navegação (amostra do §9); nulo no celular | o de 1, com mais liberdade de composição gráfica, + marcação e fontes embutidas; celular igual (A4) | alto no primeiro contato; obriga a ler dois documentos | o de 1 + leitura no celular |
| Esforço da comissão | o mesmo de hoje + revisão única das frases | o mesmo de 1 | **dobra por Edital e por Retificação** se a versão for redigida; zero se for derivada (e então é a alternativa 4 reduzida) | o mesmo de 1 |
| Fidelidade | frases fixas testadas; texto livre igual | igual a 1 | risco alto se redigida (amostras M1–M4); se derivada, igual a 1 | igual a 1, se as duas saírem do mesmo snapshot |
| Cobertura | integral (é o ato) | integral | parcial por natureza ("não substitui") | integral |
| Duplicidade editorial | nenhuma | nenhuma | **sim**, salvo se derivada | nenhuma no texto; duas formas a manter |
| Retificação | já regenera o consolidado inteiro | idem | segunda peça a sincronizar a mão | duas renderizações do mesmo consolidado |
| Recursos estruturais de acessibilidade | marcadores, título, idioma, links: baratos (feitos na amostra). **Marcação (tags) e fonte embutida: caras** à mão (§5.4) | marcação, idioma, marcadores, links e fontes **sem custo de implementação** (medido, §5.3) | depende do formato | HTML no portal; PDF como em 1 ou 2 |
| Homologação | intacta: o PDF sai do snapshot homologado | intacta, se o HTML também sair só do snapshot | **novo objeto a homologar**, sem lugar no fluxo atual | intacta, mas o hash prende o conteúdo, não as duas formas |
| Custo de migração | baixo a médio, sem dependência nova | **alto**: reescrever ~2.000 linhas de composição em templates, refazer a calibração da 054, trocar a forma dos testes que prendem bytes (§5.4), nova dependência de sistema (Chromium ou Pango) no servidor | médio (fluxo, modelo, tela) | médio a alto (o desacoplamento "dado × desenho" do §3.2) |
| Custo recorrente | nenhum novo | operar o renderizador (processo externo, versão do navegador) | redação por Edital | duas formas a verificar |
| Reuso do gerador atual | total | dados e frases, sim; paginação, não | parcial | frases e `plano_de_consolidacao`, sim |

### 5.2 Por que 1, e em que ordem

A alternativa 1 entrega, sem dependência nova, a maior parte do ganho que está ao alcance do sistema:
**as frases são do sistema**, e é nelas que está o jargão; **a ordem e o agrupamento são do
compositor**, que a 068 já mostrou saber mudar com equivalência demonstrada; a **composição gráfica**
— corpo dos títulos, fios, caixas, recuo pendente, sumário com página, tabelas coesas — cabe nas
primitivas de hoje com extensões pequenas (§9); e **marcadores, título, idioma, links e nome do
arquivo** são acréscimos ao escritor à mão (ED-07, parte P). O que ela não entrega — marcação para
tecnologia assistiva, fonte embutida e leitura no celular — é qualidade técnica a verificar, com
critério próprio (§5.4), e não é condição para o lote 1.

A alternativa 3 só faz sentido **derivada**, e derivada ela é a alternativa 4 reduzida, que já existe
em germe no portal. A alternativa 4 completa (o ato inteiro em HTML) depende do desacoplamento do
§3.2 e só se paga se o teste com candidatos mostrar que o celular é o obstáculo.

### 5.3 O experimento HTML→PDF (medido)

Montei o cenário A em HTML/CSS, já reorganizado (resumo, sumário, vagas em matriz, recursos por
objeto), e imprimi com o Chrome 155 headless.

| Verificação | PDF atual (`pdf.py`) | PDF do Chrome |
|---|---|---|
| Páginas | 6 | 5 (sem brasão e sem a descrição; não é comparação de extensão) |
| Tamanho | 45 KB | 231 KB (fontes embutidas) |
| `Tagged` / `/Lang` | não / ausente | **sim / pt-BR** |
| Estrutura | — | `H2`, `H3`, `P`, `L`/`LI`/`Lbl`, `Table`/`TR`/`TH` (com `/Scope`)/`TD` (com `/Headers`), `Caption`, `Link`; rodapé fora da árvore (artefato). Ruído: 211 `NonStruct`; a lista de definição do resumo virou `NonStruct` |
| Marcadores | ausentes | gerados dos títulos, com hierarquia |
| Links | ausentes | 9 internos (sumário) + `mailto:` |
| Fontes | base-14 não embutidas | Arial embutida em subconjunto, com `ToUnicode` |
| Determinismo | **byte a byte** | duas execuções seguidas diferem em **2 bytes**: os segundos de `/CreationDate` e `/ModDate`. Com esses campos fixados ou retirados, o resultado é determinístico (correção da segunda rodada: a primeira dizia "não determinístico") |
| Defeitos observados | — | a legenda "Tabela 1" ficou no pé da página 1 e a tabela na 2; o sumário saiu **sem número de página** (`target-counter` não é suportado pelo Chrome) |

**Fato.** O motor produziu **recursos estruturais favoráveis à acessibilidade**: marcação, idioma,
marcadores, links e fontes embutidas. **Não se afirma** que o documento seja acessível: nenhum leitor de
tela foi usado, a árvore traz 211 nós `NonStruct` de ruído, e a ordem de leitura com tecnologia
assistiva não foi verificada. **Fato.** Ele não muda uma palavra: a clareza do protótipo vem da
reorganização e da reescrita, que a amostra do §9 reproduziu no `pdf.py`. **Fato.** O sumário sem
página e a legenda separada da tabela são **problemas de implementação**. O sumário se resolve com uma
segunda passada, como a amostra fez no `pdf.py`, ou com um motor que suporte `target-counter`. A legenda
se resolve com uma regra de quebra ou com a legenda dentro do bloco da tabela. Nenhum dos dois indica
que a abordagem seja inadequada. **Hipótese:** o WeasyPrint suportaria o sumário numerado nativamente,
mas traz Pango ao servidor; não foi testado.

**Como preservar o que importa, se um dia for HTML→PDF:** o HTML só pode sair do snapshot homologado
(nunca da tela); paginação com `@page` e caixas de margem (funcionaram); títulos com `break-after: avoid`
e legenda presa à tabela (falhou no teste — exige regra); `thead` repetido; sumário numerado exige motor
que suporte `target-counter` ou uma segunda passada; marcadores dos `h2`/`h3`; anexos continuam
arquivos à parte; a verificação de integridade continua sendo o hash do conteúdo, e o teste que hoje
prende bytes passa a prender texto extraído e estrutura. **Imprimir uma página não gera PDF acessível
por si**: as tags vieram limpas aqui porque o HTML foi escrito com `th scope`, `caption`, listas e
títulos — o mesmo cuidado que o template definitivo teria de ter, e testar.

### 5.4 A decisão do motor, separada — e o que a igualdade de bytes protege

**O que os testes de bytes protegem.** Há dois tipos de teste, e a própria suíte os distingue:

- **Ausência de mudança não intencional.** `tests/contract/test_documento_publicado.py` compara byte a
  byte com uma fixture. A docstring o classifica como *"forma da apresentação"*: a fixture *"é
  regenerada a cada entrega que muda a composição de propósito"*. É técnica de regressão, e
  `test_documento_da_auditoria_depois_da_068.py` faz o mesmo papel com texto extraído.
- **Determinismo como invariante.** A 008 e a SC-370 da 054 o listam entre os invariantes do documento.
  A razão de produto está escrita **para o comprovante de inscrição** (009, FR-063a): ali a página
  publica o SHA-256 do arquivo, e *"sem determinismo o resumo publicado deixaria de conferir na segunda
  emissão"*.

**Para o Edital, a necessidade de integridade é outra.** Os bytes publicados são gravados uma vez em
`DocumentoPublicado` e servidos dali; o `document_hash` confere sempre, porque o arquivo não é
regerado. A cadeia que a Constituição exige — dados → versão homologada → PDF — é provada pelo hash do
**conteúdo** e pela renderização a partir do snapshot homologado. O determinismo dá uma prova
adicional e forte: qualquer um re-renderiza o snapshot e obtém os mesmos bytes. Foi assim que a
auditoria validou o seu harness.

**Conclusão.** O determinismo é um invariante escolhido, e barato de manter — o Chrome o atinge
fixando dois campos. **Não é** uma restrição arquitetural que exclua outro motor. Trocar de motor
exigiria:

- manter o determinismo, normalizando os metadados;
- ou substituir a prova por comparação de texto e estrutura, e registrar essa troca como decisão.

A fixture de bytes, em qualquer motor, continua sendo detector de mudança e se regenera de propósito.

**Quando revisitar o motor.** Pelo ganho visual e estrutural medido, e não por "exigir ou não" PDF/UA:
a acessibilidade é qualidade a verificar (§8). Três custos a comparar quando a marcação virar
prioridade:

- **(a)** marcar o PDF escrito à mão: emitir conteúdo marcado (`BDC/EMC`), a árvore de estrutura, a
  `ParentTree` e os artefatos, e embutir uma fonte TrueType com `ToUnicode`;
- **(b)** HTML→PDF como no §5.3;
- **(c)** servir o ato também em HTML no portal.

**Sugestão:** fazer o lote 1 no compositor atual. Depois, repetir o experimento do §5.3 com o mesmo
alvo visual da amostra do §9, já aprovado. A comparação fica justa — mesmo conteúdo, mesmo desenho — e
mede o que cada motor custa para chegar lá.

---

## 6. Viabilidade editorial e automação

### 6.1 Quem escreve o quê

| Camada | Exemplos | Como produzir | Revisão |
|---|---|---|---|
| **Derivável com frases fixas revisadas** | quadro de vagas, reversão, teto, Requerimento, regra do sorteio, corte, suplentes, continuação, desempate, prazo do recurso do marco, forma de convocação, cronograma, documentos por destinatário, "o que mudou" (ED-06) | tabela de frases por valor enumerado, como já é; reescrever L1–L17 | **uma vez**, pela área responsável e, onde houver efeito jurídico, pela procuradoria; teste por variante |
| **Exige redação humana** | público-alvo e requisitos em prosa, inscrição (canal, passo a passo), verificação da autodeclaração, atendimento PcD, matrícula, certificado, disposições | o Elaborador, com guia de redação; **modelos opcionais por unidade**, como os de aviso da 066 — o que exige decidir como fica a FR-983 | por Edital, na homologação |
| **Assistência opcional de LLM** | sugerir reescrita de um parágrafo livre, apontar frase longa, voz passiva, sigla sem extenso, termo do sistema | só na elaboração, como sugestão que o Elaborador aceita ou não; **nunca na renderização** | o mesmo da redação humana |

**Nenhum JSON ou Markdown intermediário é necessário.** O snapshot canônico já é o intermediário, com
hash, versão e homologação. A camada comunicativa do estudo de Libras (intenções, enunciados com
modalidade e fonte) serve como **ferramenta de análise e de teste** — para montar as perguntas do teste
com candidatos e a matriz de cobertura —, não como artefato a gerar por Edital.

### 6.2 Exemplos de transformação

Todos sobre o PDF de hoje (cenário A) ou sobre as amostras. "Preservado" lista as condições que a
versão nova mantém.

**1. Instrução de inscrição** — origem: seção 6 (L), Cronograma nº 1 (E), teto (E/F), seção 14 (En).

> **Antes:** "A inscrição será feita exclusivamente pela internet, no endereço eletrônico do certame, no
> período previsto no Cronograma. [...] Cada candidato poderá ter apenas 1 inscrição enviada neste Edital."
> (o Requerimento, que também vai na inscrição, só aparece na seção 14)
>
> **Depois:** "Inscreva-se somente pela internet, em **[endereço — dado ausente]**, de 13/10/2026, às 9h,
> a 30/10/2026, às 23h59. Escolha o polo e a lista de concorrência. Anexe os documentos do item 7 e envie
> o Requerimento de Matrícula, que faz parte da inscrição (item 14). Cada candidato pode enviar apenas 1
> (uma) inscrição neste Edital."

Preservado: canal exclusivo, período, escolha de polo e lista, teto contado sobre a inscrição **enviada**, Requerimento no ato da inscrição. **Lacuna:** o endereço; e o fuso do "23h59", que o Edital
não declara (a amostra real diz "horário de Brasília"). Derivável: período, teto e Requerimento; o resto
é texto da comissão.

**2. Regra condicional** — origem: `edital_gerado.pdf` (149/2024), seção 3 e documento "e)" (L).

> **Antes:** "O candidato que ainda não colou grau poderá enviar, no ato da inscrição, declaração emitida
> por instituição reconhecida pelo MEC constando a data em que irá colar grau, que deverá anteceder a data
> do início do curso; nessa condição, deverá enviar o documento de comprovação do término da graduação no
> prazo máximo de 30 (trinta) dias após o início do curso."
>
> **Mockup:** "Quem pode: Pessoas com graduação." (M1)
>
> **Depois:** "**Ainda não colou grau?** Você pode se inscrever com uma declaração da sua instituição,
> reconhecida pelo MEC, que informe a data da colação. Essa data precisa ser anterior ao início do curso.
> Depois, você terá até 30 (trinta) dias, contados do início do curso, para enviar o comprovante de
> conclusão."

Preservado: quem pode usar a exceção, documento, emissor, condição de data, prazo e termo inicial.
**Lacuna:** o Edital não diz o que acontece se o comprovante não chegar em 30 dias — a versão nova não
inventa. Só redação humana produz este texto.

**3. Quadro multicampi** — origem: Tabelas 1–3 e frase de reversão (E/En, 068).

> **Antes:** Tabela 1 (Perfil, localidade, vagas, cadastro, carga horária), Tabela 2 (vagas por lista),
> Tabela 3 (modalidades, percentual, fundamento), e "Havendo ausência de candidatos aprovados na reserva
> de vagas, o quantitativo será destinado à respectiva ampla concorrência."
>
> **Depois:** uma tabela Polo × Ampla concorrência × PPI × PcD × Total, com linha de total (112, 40, 8,
> 160), seguida de: "A reserva segue a Resolução CS nº 10/2017 do Ifes: 25% para pretos, pardos e
> indígenas e 5% para pessoas com deficiência. Quem concorre a uma vaga reservada concorre também às
> vagas de ampla concorrência do mesmo polo. Se faltarem candidatos aprovados para as vagas reservadas,
> elas passam para a ampla concorrência do mesmo polo. Não há cadastro de reserva."

Preservado: números por Perfil e lista, percentual e fundamento, reversão `ON_EXHAUSTION` (cuja frase
fala da ampla concorrência "respectiva", isto é, do mesmo Perfil), ausência de cadastro. **Derivável por
inteiro — com uma exceção:** a palavra "polo". O modelo conhece Perfil e `locality` (texto livre), não
sabe que aqui Perfil é polo. A frase "do mesmo polo" exige um rótulo do Perfil por Edital ou por família
(decisão L16); sem ele, a frase gerada diz "do mesmo Perfil". A frase da concorrência simultânea está
hoje no texto livre da seção 6, e não no dado.

**4. Recurso** — origem: marco (E), seção 12 (L), Cronograma nº 4 e nº 7 (E, tipo L).

> **Antes:** em 5.6, "Recurso: Caberá recurso contra o resultado de 'Classificação por sorteio
> eletrônico', no prazo de 2 (dois) dias corridos, contados da divulgação desse resultado."; na seção 12,
> "Caberá recurso contra o resultado preliminar da análise documental, no prazo previsto no Cronograma,
> exclusivamente pelo sistema de inscrição. Não serão aceitos recursos enviados por e-mail ou fora do
> prazo."; no Cronograma, "Prazo para interposição de recurso", 26/11 a 27/11.
>
> **Depois:**
>
> | Contra o quê | Prazo | Como |
> |---|---|---|
> | Resultado da "Classificação por sorteio eletrônico" | 2 (dois) dias corridos, contados da divulgação desse resultado (Cronograma, nº 4) | **o Edital não informa** |
> | Resultado preliminar da análise documental | de 26/11/2026, às 0h, a 27/11/2026, às 23h59 (Cronograma, nº 7) | exclusivamente pelo sistema de inscrição |
>
> "Não serão aceitos recursos enviados por e-mail ou fora do prazo."

Preservado: dois objetos, dois prazos, termo inicial, canal exclusivo, vedações. **Não inferido:** a
data final dos "2 dias corridos" (a hora final não está declarada — o estudo de Libras levantou a mesma
dúvida), o canal do recurso contra o sorteio, e se a vedação da seção 12 vale para os dois recursos.
**Derivável:** só a primeira linha. A segunda vem do texto livre e do Evento, cujo tipo não é estruturado
— o sistema não sabe que o Evento 7 é "recurso contra a análise documental". O quadro do IFF é o modelo
a seguir, mas aqui ele só pode ser **orientação de redação**, até que o Evento tenha tipo.

**5. Sorteio** — origem: marco 5.6 e método comum (E/En/L), seção 10 (L).

> **Antes:** "SORTEIO — Classificação por sorteio eletrônico / Ordem: por sorteio / Sorteio / Método:
> comum a este Edital / Algoritmo: IFES-SORTEIO-SHA256-v1 / [...] / Semente: Os cinco números sorteados [...]
> / Habilitação: participam todas as inscrições submetidas / [...] / Corte: Progridem para Análise
> documental os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais 15 (quinze)
> suplentes. / Continuação: Poderá haver chamada, nesta ordem, além dos que este corte publicar."
>
> **Depois:** "Participam do sorteio todas as inscrições enviadas. Cada polo tem a sua própria
> classificação e o seu próprio resultado. Passam para a análise dos documentos os primeiros sorteados de
> cada lista de concorrência, em número igual ao das vagas dessa lista, mais 15 (quinze) suplentes. Depois,
> poderão ser chamados outros candidatos, seguindo a mesma ordem." Seguido de um quadro **sempre
> impresso** "Dados para conferir o sorteio": concurso 6010 da Loteria Federal, de 14/11/2026, às 19h;
> algoritmo; como se escolhe o concurso; "Número usado no sorteio (semente)"; o que acontece se o
> concurso não ocorrer.

Preservado: universo do sorteio, separação por Perfil (`MARCOS_SEPARADAMENTE`), corte por lista,
suplentes, continuação e todos os dados de auditoria (FR-465 da 032) — fora do texto corrido, mas não
escondidos (contra M5). Derivável por inteiro: são as L1, L3, L8 e L9 da auditoria. **Divergência que a
versão nova não resolve:** a seção 10 condiciona o sorteio a haver mais inscritos que vagas; o sistema
sorteia sempre. Com menos inscritos, todos passam do mesmo jeito, mas a norma escrita promete algo que o
sistema não faz. Cabe à comissão decidir se retira a condição ou se o produto passa a modelá-la.

### 6.3 Conteúdo comum uma vez — e quando não agrupar

A 064 e a 068 já agrupam **pela identidade do texto impresso** e declaram o alcance ("aplicam-se a cada
um desses Perfis separadamente"). É o critério certo, e deve ser o único:

- agrupar só o que é **igual no dado e na frase**, nunca o que é parecido. Duas regras de recurso com
  textos parecidos e objetos diferentes ficam separadas (o erro que a rodada 1 do estudo de Libras
  cometeu e corrigiu);
- dizer sempre a quem se aplica e se a aplicação é **separada por Perfil**;
- partilha parcial vira: comum + o que é próprio de cada um, nunca "comum com exceções" em prosa;
- o resumo de abertura, se adotado, só **repete** dado do snapshot com remissão ao item, e declara que não
  substitui as seções (auditoria §6.3).

### 6.4 Origem, integridade e sincronização

| Verificação | Automática | Humana |
|---|---|---|
| Cada frase gerada corresponde à regra | teste por valor enumerado (o padrão de `test_frase_de_recurso.py`) | revisão única do texto de cada frase |
| Nada do snapshot deixou de sair | teste de cobertura sobre `itens_do_documento`/`tabelas_do_documento`: todo valor estruturado aparece no documento | — |
| A reorganização não mudou norma | equivalência por enunciado entre o documento antigo e o novo, como a 068 fez (`specs/068-…/demonstracao/equivalencia-A.md`) | leitura do quadro de equivalência |
| O documento corresponde ao homologado | já existe: snapshot homologado → PDF; hash do conteúdo | — |
| A paráfrase do texto livre é fiel | **nenhuma** — um hash prova que o texto não mudou, não que a paráfrase diz o mesmo | Homologador, por Edital |
| Retificação sincronizada | já existe: o consolidado é regerado inteiro do conteúdo consolidado | — com um só documento, não há o que sincronizar |

Mudar as frases **não muda o hash** dos Editais (as frases são de renderização, não de conteúdo), e não
altera nenhum documento publicado (documento publicado não se regenera). O efeito alcança só o que for publicado depois — argumento
para fazer o lote 1 cedo no piloto.

---

## 7. Menor entrega útil, dependências e decisões

### 7.1 Diretrizes recebidas na segunda rodada

O usuário não aprovou os sete pontos da primeira versão em bloco e deu, em lugar deles, estas
diretrizes, que orientam tudo abaixo:

- priorizar o edital oficial em linguagem simples, no gerador atual;
- títulos em pergunta onde ajudam o candidato, e títulos diretos onde funcionam melhor;
- preservar todas as condições e consequências relevantes;
- reutilizar fontes e configurações existentes antes de criar campo;
- incluir melhoria visual no primeiro lote;
- tratar acessibilidade como qualidade a verificar, e não como decisão de "exigir ou não";
- fazer o teste com candidatos como validação do piloto, sem convertê-lo em impedimento para preparar a
  proposta.

### 7.2 Lote 1 — o que a amostra do §9 mostra

Tudo no compositor atual, e só para Editais publicados depois (documento
publicado não se regenera). Cada item diz de onde vem: **G** frase gerada, **O** organização (o
compositor ou o catálogo), **V** composição gráfica, **N** navegação e arquivo, **R** redação do
Elaborador (guia, não código).

| # | Item | Tipo | Na amostra |
|---|---|---|---|
| 1 | Reescrever as frases geradas (ED-05; L1–L9, L11–L13, L15, L17 da auditoria) — corte, continuação, habilitação, sorteio, desempate, teto, reversão, período "de… a…" | G | §8.1, §8.2, §4, §6 |
| 2 | Cada regra gerada na seção que trata dela: o recurso do marco em "Como recorrer?"; a convocação em "Como será a convocação?"; os requisitos comuns em "Quem pode se inscrever?"; o período de inscrições em "Como se inscrever?"; o Requerimento lembrado em "Documentos" (ED-18) | O | §3, §6, §7, §9, §10 |
| 3 | "Como será a seleção?" reunindo sorteio, dados de conferência, Etapa e verificação, que hoje estão em quatro seções | O (catálogo) | §8 |
| 4 | Cronograma logo depois das vagas | O (catálogo) | §5 |
| 5 | Títulos: pergunta onde ajuda ("Quem pode se inscrever?", "Como recorrer?"), direto onde funciona ("Cronograma", "Anexos", "Disposições finais") | O (catálogo) | todos |
| 6 | Resumo de abertura **derivado** — só dado estruturado, cada linha com o item, e a declaração de que não substitui as seções | O, V | p. 1 |
| 7 | Matriz única de vagas com total; atributos iguais em todos os Perfis ditos uma vez; tabela de reserva sem a linha de travessões | V (068 estendida) | §4 |
| 8 | Hierarquia: título de seção em corpo maior com fio; subseção distinta do texto; caixa de fundo claro para o resumo, a conferência do sorteio e a declaração; recuo pendente nas listas (ED-16) | V | todas |
| 9 | Paginação por regra (§9.4): bloco curto coeso, tabela até 60% da página inteira, frase presa à tabela, item de lista atômico, fecho com a última seção, anúncio preso ao que anuncia | V | A e B |
| 9a | **Tipografia:** fonte TrueType embutida em subconjunto, com as larguras medidas nela; correção da largura de "í", "ì", "î", "ï", "ª" e "º" (§9.3). É a única dependência nova do lote: um arquivo de fonte | V | A e B |
| 9b | Perfis de mesmo nome numa tabela própria; faixa de códigos contígua; partilha parcial com unidades que não se separam (§9.5, achado 3) | O, V | B e variante |
| 10 | Sigla preservada no anúncio (ED-24); descrição administrativa fora do ato (ED-25); "Autenticidade" no lugar de "deriva integralmente" (L17) | V, G | p. 1, p. 6 |
| 11 | Sumário com número de página, marcadores em dois níveis, links do sumário, do e-mail e do endereço, título e idioma do documento (ED-07 parte P, ED-08) | N | arquivo |
| 12 | Nome do arquivo no download (ED-22) | N | — (é da view, não do PDF) |
| 13 | Guia de redação para as seções textuais, com os exemplos do §6.2 e da amostra (`REDACAO` no roteiro) | R | texto livre |

**O que o lote 1 não faz:** marcar o PDF para tecnologia assistiva (a acessibilidade estrutural acompanha
o lote, com a limitação explícita de que o arquivo continua `Tagged: no`); mudar a hora para um dígito
(L14). O "às 09h" com dois dígitos é decisão registrada em `humano.instante`, pela paridade com o
portal; a L14 da auditoria a contrariava sem saber disso.

### 7.3 Lote 2 — dado e editorial

- **Domínio do portal congelado na Publicação e rota legível do Edital** (§3.4), para que o endereço
  saia gerado. Até lá, ele continua texto do Elaborador.
- **Contato** (`PORTAL_ATENDIMENTO`) congelado na Publicação, se a unidade quiser o contato gerado.
- **Tipo do Evento do cronograma**: destrava o quadro de recursos derivado, no modelo do IFF, e a
  validação da ordem sorteio × inscrições.
- **"O que mudou" no consolidado** (ED-06).
- **Portal**: mostrar o que já é estruturado e hoje só está no PDF — vagas por lista, Etapas, prazos de
  recurso.
- Modelos opcionais de texto por unidade, se a decisão sobre a FR-983 permitir (§7.4).

### 7.4 Decisões que restam

| # | Decisão | Situação depois das diretrizes |
|---|---|---|
| — | Linguagem simples no próprio ato | **decidido** pelas diretrizes |
| D2 | Reordenar o catálogo e mudar títulos (itens 3–5 do lote 1) | as diretrizes autorizam perguntas "onde ajudam". **Falta aprovar a ordem e os títulos concretos**, que a amostra propõe. Muda a forma de todo documento futuro (`secoes.py:72`) |
| D3 | Endereço do certame | diretriz da terceira rodada: **confiável e vinculado à publicação** — o domínio congelado na `Publicacao`, como a Unidade. A **rota legível** é tratamento próprio, fora do lote 1, se exigir mudança ampla. Até lá, o endereço é texto do Elaborador (§9.7) |
| D4 | Modelos de texto por unidade × FR-983 da 054 | aberta; não bloqueia o lote 1 |
| D6 | Resumo derivado dentro do ato | a amostra o inclui; **confirmar com a área jurídica** o estatuto de um resumo dentro do ato |
| D7 | Rótulo do Perfil por Edital ("polo", "turma", "curso") | **resolvido sem campo novo** (diretriz: aproveitar os nomes existentes): código do Perfil, "Localidade" e títulos genéricos (§9.7). Rótulo por Edital só se o teste mostrar necessidade |
| D8 | Fonte do documento | **nova:** qual fonte (Liberation Sans 2.x, OFL, métricas da Helvetica) e onde mora o arquivo (repositório ou imagem). Não muda nenhuma palavra; muda os bytes de todo documento futuro |
| — | Exigir PDF/UA | **retirada**: acessibilidade é qualidade a verificar (§8) |

### 7.5 O que fica para depois

A troca de motor, revisitada com o alvo visual aprovado (§5.4); o ato integral em HTML no portal; LLM na
elaboração, depois do guia, para que a sugestão tenha critério; documento condicional e momento de
entrega como dado; Libras.

### 7.6 Dependências reais

Nenhuma biblioteca nova no produto: o subconjunto da fonte se gera uma vez, e o escritor só embute os
bytes. (A amostra usou o `fontTools` para gerá-lo, e isso pode ficar fora do produto.) Decisões: D2 e D8
antes de fixar a composição; a área jurídica para o resumo
(D6) e para as frases com efeito normativo (recurso, cotas, matrícula). A Retificação não é dependência:
o consolidado é regerado do conteúdo, e o resumo e o período de inscrições, por serem gerados,
acompanham a prorrogação sozinhos.

---

## 8. Validação

1. **Cobertura das regras** (automática): para cada frase reescrita, o teste da variante; para o
   documento, o teste de cobertura do §6.4; para a reorganização, o quadro de equivalência por enunciado,
   nos cenários A e B da auditoria e num Edital real do piloto.
2. **Teste com candidatos** (Lei 15.263, art. 5º, XVIII) — **validação do piloto, não condição para
   preparar a proposta**: 5 a 8 pessoas do público de cada família
   (curso FIC, pós EaD, bolsista), com as tarefas do §10 da auditoria — há vaga no polo X? posso me
   inscrever sem ter colado grau? até quando recorro do sorteio? onde sai o resultado? —, **antes**
   (`atual-A.pdf`) e **depois** (`proposta-A.pdf`, ou o primeiro Edital real do lote 1). Medir acerto e
   tempo, e anotar onde a pessoa procurou. As perguntas de verificação das narrativas do estudo de
   Libras servem de banco inicial.
3. **Revisão da comissão**: as frases fixas uma vez, com a procuradoria onde houver efeito jurídico; o
   texto livre por Edital, na homologação, com o guia como lista de conferência.
4. **Inspeção do documento renderizado**: dois motores de leitura (CoreGraphics e poppler, porque o
   negrito não embutido diverge entre eles), `pdftotext -raw` para a ordem de leitura, `pdfinfo` para
   título, idioma e marcadores, página a página nos cenários A e B — o protocolo da auditoria de 08/10.
5. **Acessibilidade como qualidade verificada**, e não declarada: ler o documento com leitor de tela
   real (NVDA no Windows, VoiceOver no macOS) nas tarefas do item 2, e registrar onde a leitura se perde.
   Sem marcação, o PDF é lido na ordem do fluxo; com título, idioma e marcadores ele melhora a
   navegação, mas **não** passa a ser acessível por isso. O resultado dessa leitura é o insumo para a
   decisão do §5.4.

---

## 9. Amostra: os cenários A e B hoje e no lote 1

Arquivos em [`analise-edital-linguagem-simples-2026-10-12/`](analise-edital-linguagem-simples-2026-10-12/):

| Arquivo | O que é |
|---|---|
| `atual-A.pdf`, `atual-B.pdf` | o que o sistema publica **hoje** — idênticos aos PDFs da 068 (A byte a byte; B é o da 068, com a autoridade só pelo cargo) |
| `proposta-A.pdf`, `proposta-B.pdf` | os mesmos Editais compostos como o lote 1 os comporia, com Liberation Sans embutida |
| `proposta-B-variante-de-teste.pdf` | B com corte e prazo de recurso próprios nos dois Perfis a distância — **variante declarada**, só para testar regras diferentes por Perfil; o hash impresso não corresponde ao conteúdo |
| `*-paginas.png` | as páginas de cada documento, lado a lado (CoreGraphics) |
| `tres-motores.png` | o mesmo trecho, hoje e na proposta, em CoreGraphics, poppler e PDFium |
| [`equivalencia.md`](analise-edital-linguagem-simples-2026-10-12/equivalencia.md) | a conferência por enunciado — condição, exceção, alcance, consequência |
| `proposta.py` | o roteiro que compõe as propostas a partir dos snapshots da auditoria |

### 9.1 Como foi feita, e o que isso garante

**As mesmas primitivas do `pdf.py`** — `Composicao`, `_tabela`, `_quebrar`, `_instante`, brasão, órgão,
fecho, autoridade —, de modo que o que aparece nas propostas o compositor de hoje sabe paginar. Seis
extensões pequenas, declaradas no roteiro:

- **E1** caixa com fundo claro;
- **E2** item de lista com recuo pendente;
- **E3** sumário com número de página, por duas passadas;
- **E4** título, idioma, marcadores e links;
- **E5** fonte TrueType embutida, em subconjunto WinAnsi;
- **E6** larguras medidas na própria fonte embutida.

**O roteiro não tem nada escrito para um cenário.** Ele compõe A e B pelo mesmo código:

- agrupa por identidade do dado;
- decide entre um quadro único de vagas e quadros separados pelo próprio dado (todo Perfil tem vaga
  imediata?);
- põe Perfis de mesmo nome numa tabela própria;
- compõe a faixa de códigos ("TP-01 a TP-16") só quando eles são contíguos;
- gera as frases da classificação pelo tipo da regra;
- separa o que é comum do que é próprio de cada grupo de Perfis.

O que é de cada cenário é só a **redação do Elaborador** (`REDACAO_A`, `REDACAO_B`): o texto livre
reescrito seguindo o guia, sem a numeração digitada.

**Limite.** Dois cenários e uma variante. Não foram compostos:

- dois marcos no mesmo Perfil;
- sorteio com método próprio por Perfil;
- Retificação, com a marca de consolidação e o "o que mudou".

O roteiro demonstra o resultado e a viabilidade da regra. Generalizá-la no compositor é o trabalho da
spec.

### 9.2 Medidas

| | A hoje | A proposta | B hoje | B proposta |
|---|---|---|---|---|
| Páginas | 6 | 7 | 14 | 10 |
| Fonte | Helvetica não embutida | Liberation Sans embutida (subconjunto) | Helvetica não embutida | Liberation Sans embutida |
| Tamanho | 32 KB | 98 KB | 67 KB | 103 KB |
| Sumário / marcadores / links | não / 0 / 0 | sim / 18 / 21 | não / 0 / 0 | sim / 14 / 14 |
| Título e idioma do arquivo | não | sim | não | sim |
| Bytes determinísticos | sim | sim | sim | sim |
| Fatos do documento de hoje presentes na proposta (automático) | — | **27 de 27** | — | **85 de 85** |
| Regras conferidas por enunciado | — | 43 | — | 44 |

**Páginas não são meta** (diretriz da terceira rodada). A tem uma página a mais porque os blocos
relacionados passaram a não se separar. B tem quatro a menos porque as tabelas de Perfis deixaram de
repetir o que é igual. Nos 85 fatos de B, a extração do PDF de hoje acusou 9 ausências aparentes: são os
nomes dos polos partidos pela intercalação das colunas da tabela. É o defeito de ordem de leitura do
ED-07, que acontece no documento de hoje e não na proposta.

### 9.3 Tipografia

**O defeito que você viu tem causa medida.** O PDF de hoje declara Helvetica e Helvetica-Bold sem
embuti-las, e cada leitor as substitui à sua maneira. No poppler (Linux, LibreOffice e muitos leitores)
o negrito é desenhado como regular com as larguras do negrito: o título "1. DISPOSIÇÕES PRELIMINARES"
perde o peso e o espaçamento fica irregular (`tres-motores.png`). Na proposta, com a fonte embutida, as
três renderizações — CoreGraphics, poppler e PDFium — são iguais.

**Segundo defeito, achado nesta rodada.** A tabela de larguras do `pdf.py` mede "í", "ì", "î" e "ï"
como "i" (222 milésimos de em), mas o glifo tem 278 na Helvetica e na Liberation. Em negrito, "ª" e "º"
também estão subestimados. Uma linha justificada com esses caracteres passa da margem por uma fração
de ponto por ocorrência. A proposta mede na fonte embutida (E6).

**A fonte.** A Liberation Sans tem as mesmas métricas da Arial e da Helvetica nos caracteres que o
compositor conhece, e por isso a quebra de linha não muda. A amostra usou a versão 1.07.4, que estava
nesta máquina, sob a licença Liberation (GPL com exceção para fontes). Para o produto, a versão 2.x é
OFL 1.1. **Decisão:** qual fonte e qual licença; se o arquivo entra no repositório, cerca de 400 KB por
estilo, ou se é dependência da imagem. Embutida em subconjunto, ela custa de 35 a 65 KB por documento.

**Hierarquia** — corpo e peso, como hoje, com acréscimos:

- título de seção em 12,5 pt com fio abaixo;
- subseção em 11 pt;
- rótulos de grupo em negrito;
- caixas de fundo claro para o resumo, a conferência do sorteio e a declaração;
- listas com recuo pendente.

A cor ficou de fora de propósito: a identidade do Ifes não foi verificada, e nenhuma informação pode
depender de cor.

### 9.4 Paginação: as regras que a amostra usa

Cada uma é geral, e nasceu de um defeito visto nas páginas:

| Regra | Defeito que a motivou |
|---|---|
| Seção ou bloco até 45% da altura útil é **coeso**: não começa no pé de uma página para continuar na outra | regras da inscrição longe das instruções; matrícula partida (segunda rodada) |
| Tabela até 60% da altura útil não se parte; acima disso, quebra entre linhas e repete o cabeçalho | uma linha só (TP-16) na página seguinte |
| A tabela e a frase que a explica são um bloco | reserva e reversão separadas do quadro |
| Item de lista nunca se parte | a continuação de um critério de desempate sozinha no topo da página |
| A última seção e o fecho são um bloco | página só com local, data e autoridade |
| O anúncio fica preso ao que anuncia ("Ao enviá-lo, o candidato declara:" + a caixa) | declaração separada da frase |

**Custo.** Ficam brancos no pé de algumas páginas (A, p. 4 e 6; B, p. 3). É a troca entre não separar
e não deixar branco. A spec deve fixar os limites (45%, 60%) depois de ver mais Editais, e não antes.

### 9.5 Equivalência: o que a conferência por regra encontrou

Detalhe enunciado por enunciado em [`equivalencia.md`](analise-edital-linguagem-simples-2026-10-12/equivalencia.md).
Os achados que a contagem de fatos não pegaria:

1. **Uma condição acrescentada, e corrigida.** A primeira redação da continuação dizia "Se ainda
   sobrarem vagas, poderão ser chamados outros candidatos". A norma publicada não tem essa condição. O
   sistema só chama para vaga não preenchida, mas isso é regra de convocação, e não texto do marco.
2. **Uma frase explicativa que só vale sem cadastro de reserva.** "Os suplentes são chamados, na ordem,
   para as vagas deste Edital que não forem preenchidas" torna compreensível, em A, "não há cadastro de
   reserva" ao lado de "mais 15 suplentes": suplente não é reserva, completa as vagas deste Edital. Em B
   seria errada — lá o cadastro é de até 15, e o corte leva 10 + 5, relação que é a pendência DP-05 — e
   não sai.
3. **Uma dependência entre frases.** Na variante, a partilha parcial pôs "Se houver empate [...] esse
   número" na parte comum e o número na parte de cada grupo. Corrigido: corte, empate, suplentes e
   continuação são uma unidade, e quando uma difere, a unidade inteira fica em cada grupo.
4. **O sorteio** (§4.2): divergência entre o texto do Elaborador e o comportamento do sistema, não
   contradição entre as frases.
5. **Canal de recurso:** a frase gerada não diz canal. Em B, o Elaborador indica um formulário
   eletrônico, e gerar "pelo sistema de inscrição" criaria conflito. Isso corrige o §3.4, que dava o canal
   como derivável.

### 9.6 Regras diferentes por Perfil (variante de teste)

Na variante, os Perfis a distância têm corte de 3 e recurso de 5 dias; os presenciais, 10 e 3. A seção
"Como será a seleção?" traz:

- uma vez, "Para todos os Perfis", o que é igual: nota final, arredondamento e os três critérios de
  desempate;
- depois, para cada grupo, a unidade do corte.

"Como recorrer?" traz uma frase por grupo, com o alcance na frente ("Para os Perfis TD-ADM e TD-INFO-EDU
— contra o resultado…"). Os demais Perfis, requisitos, atribuições e documentos de B já variam entre
Perfis no cenário original, e saem agrupados pela identidade.

### 9.7 O que continua à vista, e não se resolve na amostra

- **O endereço do certame** aparece só onde o Elaborador o escreve, como exemplo. A diretriz da
  terceira rodada separa duas coisas. O endereço precisa ser confiável e vinculado à publicação: o
  domínio congelado na `Publicacao`, como a Unidade. Já uma rota legível, se exigir mudança ampla, tem
  tratamento próprio, fora do lote 1.
- **"Polo", "turma", "curso"** — resolvido sem campo novo. A proposta usa os nomes que já existem: o
  **código** do Perfil, impresso em toda tabela; o rótulo **Localidade**, que é o do campo; e títulos
  genéricos ("Quantas vagas há, e onde?"). A frase de reversão diz "do mesmo código". Um rótulo por
  Edital só se o teste com candidatos mostrar que "código" não basta.
- **Perfis de B sem vaga imediata e com cadastro** não são convocáveis dentro do sistema (DP-05). O
  documento diz o que o dado diz — "os demais formam cadastro de reserva" — e não explica como.
- **Acessibilidade estrutural.** As propostas têm título, idioma, marcadores, links e fonte embutida,
  mas **continuam sem marcação** (`Tagged: no`). A leitura com tecnologia assistiva não foi validada.

## Anexo — como reproduzir

- **PDF atual:** de `backend/`, `uv run python ../doc/auditoria-edital-pdf-2026-10-08/cenarios/render_old.py
  "$PWD" ../doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json <saída>.pdf` renderiza o
  snapshot com o `pdf.py` do checkout; o resultado de hoje é idêntico a
  `specs/068-consolidacao-por-perfil/demonstracao/A-publicado-068.pdf`.
- **Experimento HTML→PDF:** uma página HTML escrita à mão a partir do texto desse PDF (não gerada pelo
  sistema), impressa com `Google Chrome --headless --no-pdf-header-footer
  --generate-pdf-document-outline --print-to-pdf=<saída>.pdf file://<página>.html`; estrutura lida com
  `pdfinfo -struct`, fontes com `pdffonts`, marcadores e links com `pypdf`. Os arquivos ficaram fora do
  repositório, de propósito: são amostra, não proposta de template.
- **Amostra do lote 1:** de `backend/`, `uv run --with fonttools python
  ../doc/analise-edital-linguagem-simples-2026-10-12/proposta.py A|B <saída>.pdf --fontes <pasta>`, com
  `LiberationSans-Regular.ttf` e `LiberationSans-Bold.ttf` na pasta (não estão no repositório). Sem
  `--fontes`, o documento sai com Helvetica não embutida; `--variante-marcos` gera a variante de teste
  de B. As páginas foram renderizadas com o `qrender_all.py` da auditoria (CoreGraphics, via
  `pyobjc-framework-Quartz`), com `pdftoppm` (poppler) e com `pypdfium2` (PDFium).
- **Leis:** textos compilados do Planalto, nas URLs da §2.1, lidos em 12/10/2026.

[registrar a decisão, não tomá-la]: ../CLAUDE.md
