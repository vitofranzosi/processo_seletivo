# Auditoria do Edital em PDF gerado pelo sistema

**Data:** 2026-10-08 · **Natureza:** auditoria técnica, visual e editorial — **nada foi implementado**.
Nenhum template, regra de negócio ou dado real foi alterado.

> **Não vira escopo por estar escrito aqui.** É registro e proposta de priorização. Decidir se,
> quando e em que lotes corrigir é do usuário (Constituição; [registrar a decisão, não tomá-la]).
> Desde 28/09/2026 o PDF do sistema **é o ato oficial do piloto** — por isso os defeitos abaixo são
> tratados como defeitos de norma publicada, e não como polimento.

Evidências na pasta [`auditoria-edital-pdf-2026-10-08/`](auditoria-edital-pdf-2026-10-08/):
`pdf/` (os documentos gerados), `paginas/` (páginas renderizadas citadas abaixo) e `cenarios/`
(os roteiros que reproduzem tudo).

---

## 0. Protocolo

| Item | Valor |
|---|---|
| Commit auditado | `fd18add4` (`main`, merge do PR #264 — a 064 já integrada, e a correção do "?" de 08/10) |
| Branch | `claude/auditoria-edital-pdf-d33731` |
| Banco | `ps_auditoria_pdf` (cenário A) e `ps_auditoria_pdf_b` (cenário B), criados do zero a partir de um banco migrado (`ps_auditoria_base`); nenhum banco de desenvolvimento ou de produção foi tocado |
| Caminho de geração | o **mecanismo real**: `create_process_with_first_edital` → `EditalDraftSerializer` → `replace_draft` → `atualizar_requerimento_de_matricula` / `atualizar_teto_de_inscricoes` → `submit_edital` → `homologate_edital` → `publish_edital` (e `create_retification` → `transition_retification` → `publish_retification`). Os bytes auditados são os gravados em `DocumentoPublicado` |
| Prévia | pelo mesmo caminho da view `previa_documento` (`edital_snapshot` + `render_edital_pdf(..., MODO_PREVIA)`) |
| Renderização visual | CoreGraphics do macOS (o motor do Preview/Safari), 72 dpi; e poppler (`pdftoppm`) como segundo motor |
| Texto e estrutura | `pdftotext -layout` (leitura visual), `pdftotext -raw` (ordem do fluxo de conteúdo), `pdfinfo`, `pdffonts`, inspeção dos objetos do arquivo |
| Comparação antes/depois | o **mesmo snapshot** renderizado pelo `pdf.py` de `1ec066e7` (antes da 054) e de `d7d3fe0b` (antes da 064), extraídos com `git archive`. O harness foi validado: com o código atual ele reproduz **byte a byte** o PDF publicado pelo sistema |
| Dados | fictícios, marcados "DEMONSTRAÇÃO" no título e no preâmbulo. Nenhum dado pessoal real. Os fundamentos normativos citados (Resolução CS nº 10/2017, Lei nº 15.142/2025 etc.) são os que os Editais reais da amostra citam, e foram usados só para dar forma plausível |

**Convenção deste documento.** Cada afirmação é marcada como **Fato** (observado no PDF ou no código),
**Hipótese** (plausível, não verificada) ou **Sugestão**. As páginas citadas são as do PDF do cenário
indicado (A = `pdf/A-publicado.pdf`, B = `pdf/B-publicado.pdf`).

---

## 1. Resumo executivo

O gerador produz um documento **tecnicamente íntegro e com aparência institucional correta**:
brasão e cabeçalho do órgão, anúncio do ato, seções numeradas por regra única, tabelas com grade,
legenda numerada e cabeçalho repetido na quebra de página, fecho com local e data, autoridade,
verificação de integridade, determinismo byte a byte. Nada vaza de UUID ou enum cru, e o caractere
que a fonte não imprime é recusado em vez de virar "?". A seção de **documentos exigidos agrupados por
destinatário** ("Dos candidatos concorrentes na modalidade…") é o ponto alto para o candidato.

Os problemas estão em outro lugar, e se repartem em quatro famílias:

1. **Norma que o documento afirma de forma errada, sem objeto ou contraditória** — a numeração
   digitada no texto livre colide com a calculada e as remissões apontam para o item errado (B,
   pp. 39–43); o prazo recursal gerado no marco não diz de qual resultado se recorre e convive com
   outro prazo no texto e no Cronograma (A, pp. 3 e 8); arredondamento impresso sob classificação por
   sorteio (A, p. 3); quadro de vagas zerado com frase de reversão e percentual de reserva em Perfil
   só de cadastro de reserva (B, p. 8 e seguintes).
2. **Organização guiada pela estrutura de dados, e não pela pergunta do candidato** — a regra de
   classificação, o método do sorteio, a tabela de modalidades e as frases do Perfil se repetem
   inteiras em cada Perfil. A seção de Perfis ocupa **5 de 9 páginas** em A e **38 de 44** em B. A 064
   tirou as atribuições repetidas (−134 linhas em B), mas o documento continuou com **44 páginas**.
3. **Vocabulário do sistema no ato** — "marco classificatório", "recorte", "Continuação",
   "Normalização: nenhuma", "Semente", "menor valor declarado em Data de nascimento", "(número
   inteiro)", "Perfis de vaga" num edital de curso.
4. **Acessibilidade e leitura digital quase inexistentes** — PDF sem tags, sem idioma, sem título,
   sem marcadores, sem links, fontes não embutidas; em células que quebram em várias linhas, a ordem
   de leitura intercala as colunas. No celular, o corpo do texto fica com ~6,9 px.

**Recomendação (detalhe na §12).** O PDF está **adequado com ressalvas** para um Edital simples do
piloto (poucos Perfis, texto livre sem numeração própria), desde que se corrijam antes quatro pontos
de norma (ED-01, ED-02, ED-03, ED-12) e se resolva a pendência da autoridade sem nome (ED-10). **Não
está adequado** para Editais com muitos Perfis no formato do cenário B: a extensão e a repetição
comprometem a consulta.

---

## 2. Caracterização do cenário

Investigadas as capacidades reais antes de montar os cenários (§3). Os dois cenários foram calibrados
contra Editais reais da amostra em `~/Downloads`: o **28/2026** (pós-graduação EaD, polos, cotas,
sorteio) e o **90/2026** (tutores UAB, cadastro de reserva, prova de títulos).

### Cenário A — processo seletivo realista (`pdf/A-publicado.pdf`, 9 páginas)

*Edital nº 91/2026 – Pós-graduação Lato Sensu em Informática na Educação, EaD (DEMONSTRAÇÃO).*

| Dimensão | Configuração |
|---|---|
| Perfis | 4 polos (`INF-BJN`, `INF-IUN`, `INF-SMT`, `INF-VAL`), 40 vagas cada, sem cadastro de reserva, carga horária 480 h |
| Modalidades | AC, PPI (25%) e PcD (5%), fundamento Resolução CS nº 10/2017; quadro 28/10/2 por polo; reversão `ON_EXHAUSTION` |
| Classificação | um marco por Perfil, **por sorteio**, método comum do Edital (Loteria Federal, concurso fictício); corte pelo quadro de vagas + 15 suplentes, governando a Análise documental; empate estrito; continuação admitida; recurso de 2 dias |
| Etapa | Análise documental, decisória e eliminatória ("Deferida"/"Indeferida"), ligada a um Evento |
| Cronograma | 10 eventos (inscrições → início das aulas), dois com local |
| Documentos | 5 de todos (1 facultativo), 1 por código PPI, 1 por código PcD |
| Seções textuais | 13 preenchidas (preâmbulo, disposições, informações do curso, público-alvo, requisitos, inscrição, verificação da autodeclaração, classificação, recursos, convocação, matrícula, certificado, disposições finais) |
| Normas executadas | teto de 1 inscrição; Requerimento de Matrícula no ato da inscrição, com declaração |
| Anexos | 3 (dois vinculados a documentos exigidos) |
| Autoridade | com nome, cargo e ato de nomeação (fictícios) |
| Retificação | prorrogação das inscrições + 5 vagas no polo BJN (`pdf/A-retificado.pdf`) |

### Cenário B — teste de estresse (`pdf/B-publicado.pdf`, 44 páginas)

*Edital nº 92/2026 – Cadastro de reserva de tutores UAB (DEMONSTRAÇÃO).*

| Dimensão | Configuração |
|---|---|
| Perfis | 18: 16 tutores presenciais por polo (0 vaga imediata, cadastro limitado a 15, **atribuições idênticas**) + 2 tutores a distância (6 e 4 vagas, atribuições distintas, um com nome de 160 caracteres) |
| Modalidades | 4 por Perfil: AC, PPIQ (30%), PcD (5%), PTT (sem percentual), fundamentos longos; reversão `ON_BALANCE` |
| Classificação | marco por pontuação de uma Etapa (prova de títulos, máx. 100), corte fixo de 10 + 5 suplentes, empate admite excedente, recurso de 3 dias, **3 critérios de desempate** sobre 2 fatos declarados (data de nascimento, meses de experiência) e sobre a Etapa |
| Etapas | 2 com nomes longos (uma pontuada, uma decisória) |
| Cronograma | 18 eventos, 4 janelas de recurso, descrições de até 200 caracteres, locais |
| Documentos | 6 de todos, 2 por Perfil, 3 por código de modalidade, instruções longas |
| Seções textuais | 11, **com a numeração de subitens digitada pelo gestor** (como sai da transcrição do Word, prática da DP-20) |
| Autoridade | **só o cargo**, como o registro inicial do Cefor está hoje (060, FR-1124) |
| Anexos | 6, com rótulos longos |

---

## 3. Investigação do sistema e cobertura funcional

### 3.1 Onde o documento nasce

| Peça | Arquivo | Papel |
|---|---|---|
| Compositor e paginador | `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (3.003 linhas) | composição, refluxo por largura real, cascata de quebra, tabelas, escrita do PDF à mão (PDF 1.4, Helvetica base-14 não embutida, WinAnsi) |
| Formatação humana | `publicacoes/infrastructure/humano.py` | datas, instantes, decimais |
| Brasão | `publicacoes/infrastructure/brasao.py` + `brasao.png` | única imagem do documento |
| Vocabulário da regra | `publicacoes/domain/vocabulario_da_regra.py` | frases de desempate, ausência e forma de convocação |
| Grafia | `publicacoes/domain/grafia.py` | normaliza e recusa caracteres fora do WinAnsi |
| Catálogo de seções | `editais/domain/secoes.py` | 22 seções fixas, textuais ou geradas, sem redação padrão desde a 054 |
| Snapshot | `publicacoes/application/publish_edital.py::edital_snapshot` | o conteúdo canônico que o compositor lê; **ordena Perfis, Modalidades, fatos e marcos por `code`** |
| Contexto do ato | `publicacoes/application/contexto_do_ato.py` | unidade, autoridade, data — fora do snapshot e do hash |
| Entrega | `publicacoes/api/views.py::PublishedDocumentView` | serve os bytes gravados, sem `Content-Disposition` |

### 3.2 A origem de cada informação impressa

A distinção pedida é a que decide quem corrige (§9, coluna "origem").

| Origem | O que é |
|---|---|
| **A. Gerada automaticamente** | brasão, cabeçalho do órgão (da Unidade), anúncio do ato (`number`/`year`), numeração de seções, subseções e tabelas, total de vagas, rodapé com hash e paginação, verificação de integridade, fecho (local da Unidade + data do ato), marca de consolidação, marca de prévia |
| **B. Configurada pelo gestor (campo estruturado)** | Perfis (código, nome, localidade, vagas, cadastro, carga horária, remuneração), quadro de vagas, modalidades e regra normativa, Etapas (caráter, peso, nota mínima/máxima, rótulos), Cronograma, documentos exigidos e destinatário, anexos (rótulo), teto, momento do Requerimento |
| **C. Derivada de regra de negócio (frase escrita pelo sistema)** | frases do marco (ordem, combinação, normalização, arredondamento, método do sorteio, habilitação, recurso, corte, empate, continuação, critérios de desempate), reversão, forma de convocação, teto ("Cada candidato poderá ter…"), Requerimento ("O Requerimento de Matrícula será enviado…"), cabeçalhos de destinatário dos documentos, remissão às atribuições comuns (064) |
| **D. Redação livre do gestor** | título e descrição do Edital, título do Processo, as 18 seções textuais (preâmbulo inclusive), descrição/atribuições/requisitos do Perfil, descrição e local dos Eventos, nome e instruções dos documentos, declaração do Requerimento |
| **E. De outras entidades** | Unidade (cabeçalho, local) e Autoridade habilitada (nome, cargo, ato de nomeação), ambas congeladas na Publicação (060) |

**Fato.** Do volume impresso nos dois cenários, a parte **C** é a que concentra os problemas de
linguagem (§5) e a parte **A/C por Perfil** a que concentra a repetição (§6). A parte **D** só gera
achado quando a interface ou a validação permite produzir documento errado sem aviso (ED-01, ED-09).

### 3.3 Cobertura

**Exercitado:** publicação original, prévia, Retificação consolidada; Perfis com e sem cotas, com e
sem vagas imediatas, com cadastro limitado e sem cadastro; quadro de vagas e reversão (as duas
espécies); duas formas de convocação; marco por sorteio (método comum) e por pontuação; corte pelo
quadro e fixo; as duas políticas de empate; continuação admitida; recurso admitido; três critérios de
desempate (fato DATA, fato INTEIRO, Etapa); fatos declarados; Etapa decisória e pontuada (com
pontuação máxima e avaliações por inscrição); Cronograma com e sem local, longo, com eventos de um
instante e de período; documentos de todos, por Perfil e por código de modalidade (044), facultativo,
com anexo vinculado; atribuições idênticas agrupadas (064); remuneração e carga horária; teto;
Requerimento no ato da inscrição; autoridade com e sem nome; anexos; títulos, nomes e descrições
longos; `●` colado do Word (normalização da grafia).

**Não exercitado** (limitação desta auditoria): método de sorteio próprio do marco e a frase
"diverge do comum"; Etapa de habilitação ao sorteio; recurso negado (`admits: false`); `MEDIA_PONDERADA`
e normalização pela soma dos pesos; dois marcos no mesmo Perfil; nota mínima; Requerimento na
convocação (`AT_CALL`); Retificação com vigência futura; Retificação que acrescenta; Unidade de
campus (não Cefor); caractere sem grafia na prévia (`[U+2265]`); Edital sem nenhuma seção textual.
Também **não** foram avaliados o portal e a interface administrativa (fora do foco pedido), nem
leitores de tela reais (só a ordem do fluxo de conteúdo, que é o que eles leem num PDF sem tags).

**Duas recusas da validação apareceram na montagem**, e as duas estão certas: duas avaliações por
inscrição sem regra de combinação (B) e — esta vira achado — **arredondamento obrigatório mesmo no
marco por sorteio** (A; ver ED-03).

---

## 4. Avaliação do PDF — visual, editorial e técnica

### 4.1 Identidade institucional

**Fato.** Brasão centralizado, "Ministério da Educação / Instituto Federal do Espírito Santo" e as
linhas da Unidade (A e B, p. 1); anúncio do ato em negrito e caixa alta; fecho alinhado à direita com
local e data; bloco da autoridade centralizado; verificação de integridade em corpo de nota abaixo de
um fio (A p. 9, B p. 44). É a anatomia dos Editais do Cefor.

Pontos fracos:
- **Autoridade sem nome** quando o registro só tem o cargo (B p. 44): o ato oficial termina com
  "Autoridade responsável pelo ato / Diretora-Geral do Centro…". É o estado atual do registro do
  Cefor (060, FR-1124; `doc/pendencias-da-060.md`) e a forma de assinatura segue em aberto com o Cefor.
- **Caixa alta altera siglas** no anúncio: "EaD" → "EAD", "Cefor/Ifes" → "CEFOR/IFES" (A e B, p. 1).
  O manual de marca do Ifes grafa "Ifes".
- **Descrição do Edital impressa entre o título e o preâmbulo** (A e B, p. 1): é resumo
  administrativo, repete o preâmbulo e não tem equivalente nos Editais da amostra.

### 4.2 Hierarquia visual e tipografia

**Fato.** Quatro níveis, todos por **peso e recuo**, nenhum por corpo: seção (11 pt negrito),
subseção do Perfil/Etapa (10,5 pt negrito), rótulos internos (10,5 pt negrito, recuo 18/32/46),
texto (10,5 pt), tabela (9,5 pt), nota (7,5 pt). A decisão é deliberada e calibrada contra os Editais
62, 73 e 146 do Cefor (`pdf.py:296-308`). Entrelinha 1,45. Justificação com última linha livre.

Consequências observadas:
- **Dentro do Perfil a hierarquia vira escada de recuos** — título do Perfil, "Requisitos",
  "Tabela N", "Marcos classificatórios — X", "FINAL — …", "Sorteio", "Método:", rótulos de par —
  cinco níveis só por recuo e negrito (A p. 3; B p. 7). Fica difícil saber em que nível se está.
- **A hierarquia depende inteiramente do negrito, e o negrito não está embutido.** No poppler deste
  Mac o Helvetica-Bold foi substituído por Helvetica Regular com as larguras do negrito: títulos sem
  peso e texto espaçado (`paginas/A-02-poppler-sem-negrito-2.png`). No CoreGraphics saiu correto
  (`paginas/A-02.png`). **Fato** num renderizador; **risco** nos demais — depende do visualizador.
- **Rótulos inconsistentes:** "Atribuições:" em negrito, "Remuneração:" regular, na mesma subseção
  (B p. 7).

### 4.3 Composição e paginação

**Fato — o que funciona.** Margens de 56 pt (~2 cm), coerentes com impressão. Nenhum título órfão no
pé de página nos dois cenários. Cabeçalho de tabela repetido na continuação (Tabela 1 em B pp. 2→3;
Cronograma em B pp. 41→42→43). Legendas que trazem o código do Perfil ("Tabela 8 — Quadro de vagas —
INF-VAL"), o que mantém o contexto quando a tabela cai na página seguinte (A p. 6). Autoridade e
integridade num bloco só. A prévia pagina igual ao publicado (A: 9 e 9 páginas) e carrega a marca em
todas as páginas.

**Fato — defeitos.**
- **Frases de reversão e de convocação na margem zero**, dentro da subseção do Perfil cujo resto está
  recuado, e coladas à grade da tabela acima (A p. 2, "Havendo ausência de candidatos…"; repete em
  todos os Perfis). Causa: `_reversao_declarada` e `_forma_de_convocacao_declarada` escrevem com
  `recuo=0` e `antes=4.0` (`pdf.py:1885`, `pdf.py:1913`).
- **Listas sem recuo pendente**: a segunda linha de um requisito ou de uma alínea começa sob o
  marcador, e não sob o texto (A p. 2, Requisitos; A p. 7, alínea c; B p. 7).
- **Linhas viúvas**: última linha de parágrafo sozinha no topo da página — "matrícula, a qualquer
  tempo." (A p. 9), "Ifes." (B p. 44).
- **Brancos grandes** no pé de várias páginas de B, porque cada bloco coeso do Perfil (quadro,
  modalidades, marco) salta inteiro para a página seguinte (B pp. 3, 5, 7…). É o motivo de a 064 não
  ter reduzido páginas (§7).

### 4.4 Tabelas

- **Tabela de Perfis** (A p. 2; B pp. 2–3): legível, total em negrito. Em B, a coluna "Perfil" fica
  estreita e um nome ocupa **8 linhas**, enquanto "Cadastro reserva" e "Carga horária" sobram.
  Alinhamentos misturados: "Cadastro reserva" à esquerda, "Carga horária" centralizada.
- **Quadro de vagas** (A p. 2): duas colunas esticadas na largura total, número a ~10 cm do rótulo;
  sem linha de total do Perfil (a tabela de Perfis tem).
- **Modalidades** (A p. 2): ordem **diferente** da do quadro de vagas do mesmo Perfil — quadro: AC,
  PPI, PcD (ordem declarada); modalidades: AC, PcD, PPI. Causa: o snapshot ordena modalidades por
  `code` com a collation do banco, e o quadro pela ordem declarada (`publish_edital.py:122` e
  `:263-268`). Linha "AC — Ampla concorrência | — | —" sem informação.
- **Cronograma** (A p. 8; B pp. 41–43): a coluna "Evento" recebe a mesma largura que "Onde", e um
  evento ocupa até **9 linhas** (B p. 42, nº 10). O algoritmo de largura reparte por igual entre as
  colunas longas (`_larguras_das_colunas`, `pdf.py:1127`).

### 4.5 Técnica do arquivo

| Verificação | Resultado (Fato) |
|---|---|
| Versão / tamanho | PDF 1.4; A4; 45 KB (A), 176 KB (B) |
| Fontes | Helvetica e Helvetica-Bold, Type 1 base-14, **não embutidas**, WinAnsi, **sem ToUnicode** |
| Extração de texto | correta, acentos preservados (`pdftotext`) |
| `/Info` (título, autor, assunto) | **ausente** |
| `/Lang` | **ausente** |
| Tags (`/StructTreeRoot`, `/MarkInfo`) | **ausentes** — "Tagged: no" |
| Marcadores (`/Outlines`) | **ausentes** |
| Links (`/Annots`, `/URI`) | **ausentes**; o e-mail do texto não é clicável |
| Nome do arquivo ao baixar | `PublishedDocumentView` não envia `Content-Disposition` |
| Determinismo | confirmado: duas execuções do cenário A produziram o mesmo tamanho; o harness reproduz os bytes publicados |

---

## 5. Experiência do candidato

### 5.1 As doze perguntas (cenário A, com notas de B)

| # | Pergunta | Resposta | Onde |
|---|---|---|---|
| 1 | Identifica rapidamente o objetivo? | **Sim.** Anúncio do ato e preâmbulo na p. 1 | A p. 1 |
| 2 | Entende quais cursos têm vagas? | **Sim**, pela Tabela 1, com total. Mas o curso aparece como "Perfil de vaga" com "Cadastro reserva" e "Carga horária" — vocabulário de seleção de pessoal num edital de curso | A p. 2 |
| 3 | Localiza os requisitos? | **Parcialmente.** A seção 4 remete aos Perfis; os requisitos repetem em cada Perfil | A pp. 1–6 |
| 4 | Entende as modalidades? | **Parcialmente.** Precisa cruzar duas tabelas por Perfil (vagas numa, percentual e fundamento noutra, em ordens diferentes) e a seção 6; ninguém diz o que é "lista de concorrência" | A p. 2, p. 7 |
| 5 | Sabe como se inscrever? | **Não pelo que o sistema escreve.** As frases geradas falam em "endereço eletrônico do certame", que o documento nunca informa; depende de o gestor escrever o endereço (ED-09) | A pp. 2, 6, 8 |
| 6 | Entende os documentos? | **Sim — o melhor ponto do documento.** Mas o Requerimento de Matrícula, enviado no ato da inscrição, está na seção 14, e não na lista de documentos | A p. 7, p. 8 |
| 7 | Identifica os prazos? | **Sim, no Cronograma**, que só aparece na p. 8 de 9 (seção 11). Nada na abertura aponta para ele | A p. 8 |
| 8 | Entende a avaliação e classificação? | **Com dificuldade.** A regra está dentro de cada Perfil, em vocabulário técnico (Semente, Derivação, recorte, Continuação) e com "Arredondamento" sob um sorteio. Em B, o desempate diz "menor valor declarado em Data de nascimento" | A p. 3; B p. 7 |
| 9 | Sabe onde consultar resultados? | **Não.** Há datas de divulgação no Cronograma, mas não onde | A p. 8 |
| 10 | Entende como recorrer? | **Não com segurança.** O marco diz "2 dias, contados da divulgação do resultado"; a seção 12 diz que só cabe recurso contra a análise documental; o Cronograma dá 26–27/11 | A pp. 3, 8 |
| 11 | Identifica as condições de matrícula? | **Sim**, seção 14, com a declaração transcrita | A pp. 8–9 |
| 12 | Sabe onde obter informações? | **Sim, porque o gestor escreveu o e-mail** nas disposições preliminares (não é clicável) | A p. 1 |

### 5.2 Linguagem: textos que o sistema escreve

Só entram aqui frases da origem **C** (escritas por `pdf.py` ou `vocabulario_da_regra.py`) — o gestor
não tem como mudá-las. As sugestões preservam o efeito normativo; onde a equivalência depende de uma
regra do código, a fonte está indicada.

| # | Texto atual | Problema | Texto sugerido | Justificativa |
|---|---|---|---|---|
| L1 | "Corte: Progridem para Análise documental os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais 15 (quinze) suplentes." | "recorte" é termo interno; "Corte" como rótulo assusta | "Passam à Análise documental os primeiros classificados desta ordem, em número igual ao das vagas da respectiva lista de concorrência, mais 15 (quinze) suplentes." | `faixa.py:18-20`: o alvo "do quadro" é a linha do quadro de vagas do recorte, isto é, da lista. "Lista de concorrência" já é o termo da Tabela "Quadro de vagas" |
| L2 | "Empate no corte: Havendo empate na última posição, essa quantidade não é excedida." | voz passiva e rótulo técnico | "Se houver empate na última posição, não serão admitidos candidatos além desse número." | mesmo efeito de `STRICT` |
| L3 | "Continuação: Poderá haver chamada, nesta ordem, além dos que este corte publicar." | "Continuação" e "corte publicar" | "Chamadas posteriores: poderão ser chamados outros candidatos, seguindo esta mesma ordem, além dos indicados acima." | mesmo efeito de `ALLOWED` |
| L4 | "1º menor valor declarado em Data de nascimento; sem o valor, fica por último neste critério" | o candidato precisa deduzir que "menor data" = "mais velho" | "1º maior idade (data de nascimento mais antiga, informada na inscrição); quem não a informar fica em último lugar neste critério" | mesma ordenação. A frase vem do mesmo `vocabulario_da_regra`, então a mudança vale para o documento e para o ato de ordenação ao mesmo tempo. Pede um rótulo por par tipo × fato DATA |
| L5 | "2º maior valor declarado em Meses de experiência…; sem o valor, fica por último neste critério" | "valor declarado em" | "2º maior número de meses de experiência em tutoria na educação a distância, informado na inscrição; quem não o informar fica em último lugar neste critério" | idem |
| L6 | "Combinação: soma ponderada da Etapa Prova de títulos … (peso 1)" + "Normalização: nenhuma" | com uma Etapa só, "soma ponderada" e "peso 1" não dizem nada; "Normalização: nenhuma" é parâmetro de cálculo, não norma para o candidato | "Nota final: a pontuação obtida na Etapa Prova de títulos." (manter a forma ponderada só com duas ou mais Etapas; omitir a normalização quando for "nenhuma") | mesma conta; menos ruído |
| L7 | "Arredondamento: 2 casas decimais, meio para cima" | "meio para cima" é jargão; sob sorteio, não há nota | "A nota final será arredondada para duas casas decimais, arredondando-se para cima a partir da metade." — e **nada** sob marco por sorteio (ED-03) | idem |
| L8 | Bloco "Sorteio / Método: comum a este Edital / Algoritmo: IFES-SORTEIO-SHA256-v1 / … / Semente: … / Derivação: … / Se faltar: …" | lista técnica sem frase de abertura; repetida por Perfil | Frase de abertura: "A ordem será definida por sorteio eletrônico, a partir do resultado do Concurso 6010 da Loteria Federal, de 14/11/2026, às 19h. Os dados que permitem a qualquer pessoa conferir o sorteio são:" — seguida da lista, **uma vez no Edital** (ED-04). Rótulos: "Semente" → "Número usado no sorteio"; "Se faltar" → "Se o concurso não ocorrer" | mantém a auditabilidade (FR-465) e dá o sentido antes do detalhe |
| L9 | "Habilitação: participam todas as inscrições submetidas" | "submetidas" | "Participam do sorteio todas as inscrições enviadas." | o sistema chama de "enviada" a inscrição submetida (o teto já usa "enviada") |
| L10 | "Recurso: Caberá recurso no prazo de 2 (dois) dias corridos, contados da divulgação do resultado." | não diz **de qual resultado** (ED-02) | "Caberá recurso contra o resultado da Classificação por sorteio eletrônico no prazo de 2 (dois) dias corridos, contados da sua divulgação." | o recurso do sistema é contra a publicação do resultado **do marco** (`doc/decisao-018-escopo-institucional-do-recurso.md` §1) |
| L11 | "A convocação dos classificados será feita por publicação no endereço eletrônico do certame." | o endereço nunca é dado | Manter a frase, e garantir que o endereço esteja no documento (ED-09) | — |
| L12 | Tabela de Perfis: "Cadastro reserva: limitado em 15" / "não há" | "limitado em" | "até 15 classificados" / "Não há" | mesmo dado |
| L13 | "Dados exigidos na inscrição • Data de nascimento (data) • Meses de experiência… (número inteiro)" | o tipo de dado é detalhe técnico | "Na inscrição, o candidato informará: • a data de nascimento; • o número de meses de experiência em tutoria na educação a distância." | o anúncio continua antes da inscrição (E2E15-005) |
| L14 | "Realização: 17/11/2026, às 08h a 24/11/2026, às 17h" | falta "de"; zero à esquerda | "Realização: de 17/11/2026, às 8h, a 24/11/2026, às 17h" | redação oficial (hora sem zero à esquerda); "às 00h" já é o RC-22, adiado pela 054 |
| L15 | "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital." | construção pesada | "Cada candidato poderá enviar apenas 1 (uma) inscrição neste Edital." | conserva o FR-064 (conta só a enviada) e o número por extenso dos demais prazos |
| L16 | Título da seção gerada "PERFIS DE VAGA" e coluna "Perfil" num edital de curso | conceito interno; num curso o candidato procura "vagas", "curso", "polo" | Avaliar um título neutro ("DAS VAGAS") ou um título por família de Edital | é decisão de catálogo (054, D-001), e mudar o catálogo depois da primeira publicação real deixa o acervo com duas formas de documento (`secoes.py:72-75`). **Decisão do usuário** |
| L17 | "Verificação de integridade — este documento deriva integralmente da versão homologada identificada abaixo." | "deriva integralmente" | "Autenticidade: este documento corresponde integralmente à versão homologada do Edital identificada abaixo." | refinamento |

### 5.3 Outros problemas de leitura (Fato)

- **Informação dispersa.** A regra de recurso aparece em três lugares (marco no Perfil, seção textual,
  Cronograma), a de classificação em três (marco, seção "Critérios de Classificação", Etapas), o
  Requerimento fora da lista de documentos.
- **Remissão distante.** "Atribuições: as descritas no item 3.19" (B p. 7) manda o candidato à p. 39.
- **Repetição** sem ganho (§6.2).

---

## 6. Arquitetura da informação

### 6.1 Ordem das seções

**Fato.** A ordem é a do catálogo da 054, tirada dos quinze Editais da amostra, **com a oferta antes da
inscrição** — e é boa. O problema não é a ordem das seções, e sim o que cabe dentro de "Perfis de
Vaga": toda a matéria por Perfil (vagas, cotas, regra de classificação, recurso, corte, sorteio,
convocação) mora ali, longe das seções "Etapas", "Critérios de Classificação", "Cronograma" e "Dos
Recursos", que falam da mesma coisa. O candidato que lê "10. CRITÉRIOS DE CLASSIFICAÇÃO" (A p. 7) não
encontra a regra; ela está na p. 3.

### 6.2 Repetição medida

| Bloco repetido por Perfil | A (4 Perfis) | B (18 Perfis) |
|---|---|---|
| Regra do marco (ordem, combinação, arredondamento, recurso, corte, empate, continuação, desempate) | 4× idêntica | 18× idêntica |
| Método do sorteio (9 linhas) | 4× idêntico | — |
| Tabela de modalidades | 4× idêntica | 18× idêntica |
| Frase de reversão + frase de convocação | 4× | 18× |
| Requisitos | 4× idênticos | 16× idênticos |
| Atribuições | — | **1×** (064 agrupou 16) |
| **Páginas da seção de Perfis** | **5 de 9** | **38 de 44** |

### 6.3 Elementos de navegação — avaliados pelo ganho, não pela aparência

| Elemento | Recomendação | Ganho concreto |
|---|---|---|
| **Marcadores do PDF** (outline: seções e subseções) | **Sim, já** | barra lateral em todo visualizador; custo baixo num PDF escrito à mão; não acrescenta texto ao ato |
| **Consolidar o que se repete** (uma "regra comum aos Perfis X, Y…", como a 064 fez com as atribuições; uma tabela única Perfil × lista de concorrência com vagas, percentual e fundamento, como o "Quadro 2" do Edital 28/2026) | **Sim, curto prazo** | é o que transforma 38 páginas em poucas; responde "quantas vagas PPI no polo X" numa tabela |
| **Sumário** impresso | **Só acima de um limite** (ex.: 12 páginas) | em A (9 páginas) não paga o espaço; em B (44) paga |
| **Links internos** nas remissões ("item 3.19") e no sumário | Opcional, junto com os marcadores | útil em tela; nulo impresso |
| **Quadro-resumo para o candidato** (onde se inscrever, prazo, onde sai o resultado) | **Opcional, com cautela** | ajuda o primeiro contato, mas é **orientação (C)** dentro de um ato: só se for derivado dos mesmos dados (Cronograma, forma de convocação), declarado como não substitutivo e nunca com redação própria que possa contradizer a norma |
| **Destaque de prazos** | Não como enfeite; a tabela do Cronograma já é a fonte | — |
| **Referências cruzadas automáticas** para seções geradas ("conforme o Cronograma, seção 11") | Sim, onde o sistema escreve "no período previsto no Cronograma" | o número é calculado; não envelhece |

Na classificação pedida: **A. normativa** — seções, Perfis, regras, Cronograma, documentos;
**B. operacional** — onde e como se inscrever, nome de arquivo, e-mail, canal de transmissão;
**C. orientação** — quadro-resumo, sumário, marcadores. Nenhum elemento C deve repetir uma regra
com outras palavras.

---

## 7. Acessibilidade e leitura digital

O enquadramento: a Lei nº 13.146/2015 (LBI, art. 63) e o eMAG pedem acessibilidade nos meios
digitais da administração pública; no PDF, o padrão de referência é o PDF/UA (ISO 14289). **Esta
auditoria não verificou conformidade e não a declara.** O que se afirma abaixo é o que foi medido.

| Aspecto | Situação | Natureza |
|---|---|---|
| Seleção e extração de texto | funcionam, com acentos | Fato (positivo) |
| Contraste | preto sobre branco; cabeçalho de tabela cinza 0,85 com texto preto (~15:1) | Fato (positivo) |
| Uso de cor | nenhuma informação depende de cor | Fato (positivo) |
| Estrutura semântica | **sem tags**: títulos, listas e tabelas não existem para tecnologia assistiva | Fato |
| Ordem de leitura | segue o fluxo de conteúdo; **em células com várias linhas, as colunas se intercalam** ("Divulgação da relação de / 10/11/2026, às 17h / — / — / inscrições que participarão / do sorteio") — `pdftotext -raw`, A p. 8 | Fato |
| Rodapé e cabeçalho | lidos como conteúdo em toda página (sem marcação de artefato) | Fato |
| Idioma (`/Lang`) | ausente — o leitor de tela pode ler o português com voz de outro idioma | Fato (efeito: risco) |
| Título (`/Info /Title`) | ausente — a aba e a janela mostram o nome do arquivo ou a URL | Fato |
| Marcadores | ausentes | Fato |
| Links | ausentes; e-mail não clicável | Fato |
| Fontes | não embutidas; sem `ToUnicode` (a extração funciona hoje porque o WinAnsi é padrão) | Fato; o efeito visual comprovado num renderizador (§4.2) |
| Conformidade PDF/UA | **não atende** os requisitos estruturais, que exigem PDF marcado, idioma e título. Isto se afirma pela ausência comprovada desses elementos, sem validador | Fato |
| Leitores de tela reais | não testados | Limitação |

**Leitura no celular (Fato).** O PDF é A4 fixo e, sem tags, não reflui. Na largura de um telefone
(~390 px), ajustado à largura, o corpo de 10,5 pt vira **~6,9 px**, a tabela ~6,2 px e o rodapé ~4,9 px
(`paginas/A-08-largura-de-celular.png`). Ler exige ampliar e arrastar na horizontal. Ampliar não
perde qualidade (é vetor). **Não é defeito de "responsividade"**, que não existe para PDF; a mitigação
real é outra: tags (que habilitam o refluxo em leitores como o Liquid Mode do Acrobat) ou uma versão
HTML do mesmo conteúdo, no portal.

---

## 8. Consistência funcional e documental

**Fato — fidelidade.** Tudo o que foi configurado aparece, com os valores certos: vagas e total (160;
165 depois da Retificação), quadro que fecha com o total (28+10+2; 33+10+2), percentuais, fundamentos,
Etapas, Cronograma (com o término prorrogado no consolidado), documentos por destinatário, teto,
declaração do Requerimento, anexos, autoridade. Nada foi impresso sem respaldo na configuração.

**Divergências e ambiguidades (Fato).**

| # | O quê | Evidência |
|---|---|---|
| C1 | **Prazo recursal sem objeto e em conflito** com o texto e o Cronograma | A: marco "2 dias, contados da divulgação do resultado" (o do sorteio sai em 16/11, logo até 18/11) × seção 12 "recurso contra o resultado preliminar da análise documental" × Cronograma "26/11 a 27/11". B: um prazo único de 3 dias × quatro janelas no Cronograma, uma delas de 2 dias |
| C2 | **Arredondamento imposto e impresso sob sorteio** | A p. 3; a submissão recusa o marco por sorteio sem `rounding.scale` ("O arredondamento do marco deve declarar `scale` como inteiro") |
| C3 | **"Empate no corte" sob sorteio**, onde não há empate possível | A p. 3 |
| C4 | **Perfil só de cadastro de reserva**: quadro de vagas inteiro com zeros, frase de reversão sobre "vagas reservadas" que não existem, percentual de 30% ao lado de 0 vaga | B pp. 8 e seguintes (RC-58, conhecido). A submissão avisa que a convocação desses Perfis "será feita fora" do sistema, e o documento não diz como a reserva se aplica ao cadastro |
| C5 | **Ordem diferente** das modalidades entre o quadro de vagas e a tabela de modalidades do mesmo Perfil | A p. 2 |
| C6 | **Ordem dos Perfis e dos fatos por código**, e não pela declarada: os Perfis TD-\* antes dos TP-\* em B; "Meses de experiência" antes de "Data de nascimento", enquanto o 1º critério de desempate é a data | B pp. 2, 7. **Hipótese:** como a ordenação usa a collation do banco, a mesma configuração pode sair em outra ordem num banco com outra collation (o documento publicado fica congelado; a variação seria entre ambientes) |
| C7 | **Retificação silenciosa**: o consolidado diz "retificado em 8 de outubro de 2026", mas não diz o que mudou; prazo e vagas mudaram sem marca, e a justificativa não sai | `pdf/A-retificado.pdf` × `pdf/A-publicado.pdf` (diff: só a marca, 40→45, 160→165, 28→33, 30/10→04/11 e o hash) |
| C8 | **Requerimento enviado na inscrição fora da lista de documentos** da inscrição | A p. 7 × p. 8 |
| C9 | **Remissões quebradas pela numeração digitada** (D, sem aviso do sistema) | B p. 43: "11. DOS RECURSOS / … prevista no item 8.1", e o 8.1 do documento é a Etapa "Prova de títulos" (B p. 41) |
| C10 | **"Endereço eletrônico do certame"** citado pelo sistema e nunca definido | A pp. 2–6 (frase de convocação), 1 e 6 (texto do gestor) |

**O que depende de interpretação externa.** Onde e como se inscrever, onde sair o resultado, como
recorrer (formulário? sistema?) — tudo depende de o gestor escrever. O documento não tem um campo que
garanta o endereço; o FR-027a da 020 proíbe deliberadamente endereço na lista de anexos, por boas
razões (domínio que muda, identidade da publicação), e nenhuma regra cobre o endereço de inscrição.

---

## 9. Evolução recente — impacto das últimas features

Comparação com o **mesmo snapshot**, renderizado pelo código antigo e pelo atual (validado byte a
byte). Onde não houve comparação, a conclusão é baseada em código e spec, e isso está dito.

| Feature | Objetivo | Antes | Agora | Evidência | Benefício para o candidato | Regressão / oportunidade |
|---|---|---|---|---|---|---|
| **Correção do "?"** (`a9163516`, `bb0d32f9`, 08/10) | o ato não troca caractere por "?" em silêncio | B antes da 064 (código anterior à correção): os `●` colados do Word saíam **"?"** em todas as atribuições | `•`; e o que não tem grafia é recusado na publicação | `pdf/B-renderizado-antes-da-064.pdf` × `pdf/B-publicado.pdf` | **Alto e perceptível**: um "?" no ato oficial é defeito visível e normativo | nenhuma regressão observada |
| **064 — atribuições consolidadas** (`5cb7ef01`) | imprimir uma vez as atribuições idênticas | 16 cópias das atribuições em B | uma subseção "3.19 Atribuições comuns aos Perfis TP-01 … TP-16" e remissão em cada Perfil | −134 linhas não vazias; **44 páginas antes e depois** | **Médio**: menos texto repetido. Mas a remissão manda o leitor da p. 7 à p. 39, e o espaço liberado virou branco, porque os blocos coesos seguintes saltam de página | a mesma técnica não alcança o que mais se repete (marco, modalidades, frases) — oportunidade direta, ED-04 |
| **060 — unidades e autoridades** (`0f1f313c`) | cabeçalho e local da Unidade; autoridades no banco | constantes do Cefor | do registro, congelados na Publicação | código e spec (FR-1112..1114; para o Cefor o documento é idêntico byte a byte, SC-430). **Não houve comparação com Unidade de campus** | **Técnico** para o Cefor; **real** para campus | o registro inicial só com cargo produz ato sem nome (ED-10) |
| **054 — Edital como ato oficial** (`54f5f1f1`, `a0cecab6`) | catálogo das quatro famílias, fecho, consolidação, matrícula, total | com o snapshot de A, o renderizador anterior imprimia **4 títulos de seção vazios** (Atendimento à PcD, Acesso ao Curso, Homologação da Matrícula, Prazo de Validade), sem total de vagas, sem local e data, sem a declaração do Requerimento e sem o ato de nomeação | tudo isso corrigido, e a numeração coincide com a da tela | `pdf/A-renderizado-antes-da-054.pdf` × `pdf/A-publicado.pdf` | **Alto e perceptível**: o documento passou a ter forma de ato | a marca de consolidação não diz o que mudou (ED-06); o catálogo fixo ainda chama de "Perfis de Vaga" a oferta de curso (L16) |
| **044 — documentos por código** (`fe9780bd`) | um grupo por modalidade transversal | (sem comparação) | "Dos candidatos concorrentes na modalidade …" | A p. 7, B p. 40 | **Alto** — o melhor trecho para o candidato | — |
| **032 — método do sorteio no documento** (`14a765bd`) | a ordem por sorteio publica o método | (sem comparação) | bloco "Sorteio" completo no marco | A p. 3 | auditabilidade **real**; clareza **baixa** (jargão, repetido por Perfil) | ED-04, L8 |
| **025 / 016 / 019** — quadro, reversão, forma de convocação | publicar as quantidades por lista e as regras sobre elas | (sem comparação) | Tabela "Quadro de vagas" + frases | A p. 2 | **Alto** (o quadro); as frases saem mal posicionadas | ED-12, ED-15, C5 |
| **055** (polish) | — | — | proíbe tocar o PDF (FR-1019) | spec | nenhum, por desenho | — |

**Respostas pedidas.**

- *As últimas implementações tornaram o edital mais completo, mais claro e mais profissional?* **Mais
  completo e mais profissional, sim** — 054 e a correção do "?" são ganhos inequívocos e visíveis.
  **Mais claro, pouco**: nenhuma feature recente atacou a linguagem das frases geradas nem a
  organização por Perfil.
- *Impacto perceptível para o candidato:* correção do "?", 054 (fecho, total, declaração da matrícula,
  fim das seções vazias), 044, 064 (parcial).
- *Impacto apenas técnico:* 060 para o Cefor (documento idêntico byte a byte), a ordenação canônica
  do snapshot.
- *Alguma implementação aumentou a complexidade sem necessidade?* As features 014/015/018/032
  acrescentaram ao marco, por boas razões de reconstituição da ordem, um bloco de 10 a 25 linhas
  **por Perfil**. O ganho de completude é real, mas a forma de imprimir é que gerou a maior parte das
  páginas. A remissão da 064 para o fim da seção também tem custo de navegação.

---

## 10. Teste de compreensão (avaliação heurística simulada, cenário A)

Não é teste com usuários. Cada tarefa foi resolvida **só com o PDF**; a resposta ausente fica registrada
como ausência.

| Tarefa | Onde | Localização | Clareza | Precisa de outras partes? | Ambiguidade | Oportunidade |
|---|---|---|---|---|---|---|
| 1. Há vaga para o polo de Iúna? | Tabela 1, p. 2 | fácil | boa (40 vagas) | para saber quantas por cota, Tabela 4, p. 3 | "Perfil de vaga" | tabela única Perfil × lista |
| 2. Requisitos | seção 4 → 5.2, p. 3 | média | boa | sim (seção 3, público-alvo) | — | requisitos comuns uma vez |
| 3. Documentos | seção 7, p. 7 | fácil | **muito boa** | sim: o Requerimento está na seção 14 | — | citar o Requerimento na lista |
| 4. Modalidade aplicável | Tabelas 4–5, p. 3–4; seção 6 e 8 | média | regular | sim, 3 lugares | quem é elegível a PPI/PcD não está definido (conteúdo do gestor) | fundir as duas tabelas |
| 5. Prazo de inscrição | Cronograma, p. 8 | média (fim do documento) | boa | não | "às 23h59" de qual fuso — o documento não diz (a amostra diz "horário de Brasília") | referência ao Cronograma nas seções que o citam |
| 6. Como será classificado | marco, p. 3; seções 9 e 10 | difícil | **baixa** | sim, 3 lugares | "Arredondamento" sob sorteio; "recorte"; "Semente" | frase de abertura (L8), consolidar (ED-04) |
| 7. Quando e onde sai o resultado | Cronograma, p. 8 | quando: média; **onde: ausente** | — | — | "endereço eletrônico do certame" | ED-09 |
| 8. Como recorrer | marco p. 3, seção 12 p. 8, Cronograma p. 8 | difícil | **baixa** | sim, 3 lugares | **dois prazos e dois objetos** | ED-02 |
| 9. Condições de matrícula | seção 14, pp. 8–9 | fácil | boa | Cronograma (homologação) | — | — |

No cenário B as tarefas 1, 2, 6 e 8 pioram em grau: a regra está 18 vezes no documento, e o
desempate exige decifrar "menor valor declarado em Data de nascimento".

---

## 11. Problemas identificados — tabela consolidada e priorizada

Origem da solução: **A** template do PDF · **B** motor de geração · **C** modelagem · **D** interface
de configuração · **E** validação de regra de negócio · **F** conteúdo do gestor. Complexidade: P
(pequena), M (média), G (grande).

| ID | Prio | Problema | Evidência | Pág. | Causa provável | Impacto para o candidato | Solução recomendada | Cplx. | Origem | Componente |
|---|---|---|---|---|---|---|---|---|---|---|
| ED-01 | **P0** | Numeração digitada no texto livre colide com a calculada; remissões apontam para o item errado | "4. DA INSCRIÇÃO" seguido de "3.1…"; "11. DOS RECURSOS … item 8.1" (o 8.1 é a Etapa) | B 39–44 | catálogo com numeração calculada e texto transcrito do Word com numeração própria; nenhum aviso | remissão normativa errada no ato oficial; candidato e comissão citam itens diferentes | **Imediato:** achado na Revisão (e na submissão) quando um parágrafo de seção textual começa por número que não seja o da seção calculada. **Depois (spec):** numerar os parágrafos das textuais pelo sistema ("N.k") e retirar a numeração digitada | P / M | E, D (+F) | `editais/domain/validation.py`; `interface` (Conteúdo); `pdf.py::_secoes` |
| ED-02 | **P0** | Prazo recursal gerado sem objeto, convivendo com outro prazo no texto e no Cronograma | marco × seção 12 × Cronograma | A 3, 8; B 4 e 41–43 | o recurso é por marco; o Cronograma e o texto são livres; nada os relaciona | o candidato não sabe de quê, nem até quando, pode recorrer | nomear o resultado na frase (L10); avisar na Revisão quando houver Evento de recurso no Cronograma sem marco correspondente, ou o contrário | P | A, E | `pdf.py::_janela_recursal`; validação |
| ED-03 | **P1** | Arredondamento (exigido pela validação) e "Empate no corte" impressos sob marco por sorteio | "Ordem: por sorteio / Arredondamento: 2 casas decimais" | A 3–6 | validação de `rounding` não distingue a forma da ordem; o compositor imprime o que houver | afirma uma conta que não existe | não exigir nem imprimir arredondamento quando `orderProduction = POR_SORTEIO`; omitir o empate no corte sob sorteio | P | E, A | `editais/domain/validation.py`; `pdf.py::_marcos` |
| ED-12 | **P1** | Perfil só de cadastro de reserva com quadro zerado, reversão e percentual de reserva | 16 quadros de zeros; "Na hipótese do não preenchimento total das vagas reservadas…" | B 8–38 | o compositor imprime o quadro e a reversão sem olhar se há vaga | lê-se que há reserva de vagas onde não há vaga; não se sabe como a reserva se aplica ao cadastro | sem vaga imediata, não imprimir o quadro nem a reversão; registrar como decisão a regra de reserva no cadastro (RC-58) | P | A (+C) | `pdf.py::_quadro_de_vagas_do_perfil`, `_reversao_declarada` |
| ED-10 | **P1** | Ato com autoridade só pelo cargo | "Autoridade responsável pelo ato / Diretora-Geral…" | B 44 | registro inicial sem nome (060, FR-1124); assinatura em aberto com o Cefor | ato oficial sem quem o pratica nominalmente | decisão de governança: exigir nome antes da primeira publicação real, ou registrar que o cargo basta | P | F, E | registro de autoridades; `pendencias-da-060` |
| ED-04 | **P1** | Repetição integral, por Perfil, de marco, método, modalidades e frases | §6.2 | A 2–6; B 2–39 | composição por entidade; a 064 só tratou as atribuições | documento 4× mais longo que o necessário; a regra se perde | estender a técnica da 064: "Regra de classificação comum aos Perfis …" (identidade de texto impresso); tabela única Perfil × lista com vagas, percentual e fundamento; método do sorteio comum impresso uma vez | M | A, B | `pdf.py::_perfis`, `_marcos`, `_modalidades`, `_quadro_de_vagas_do_perfil` |
| ED-05 | **P1** | Vocabulário interno nas frases do sistema | L1–L17 | todas | frases escritas a partir dos campos | regras normativas não compreendidas | reescrever as frases (§5.2), no `vocabulario_da_regra` e no `pdf.py` | M | A | `pdf.py`; `vocabulario_da_regra.py` |
| ED-06 | **P1** | Consolidado não diz o que mudou nem por quê | diff A × A-retificado | A-ret. 1 | 054 (FR-995) só marcou a data | quem já leu o original precisa reler tudo | quadro "Alterações desta versão" gerado das mudanças (caminho → rótulo humano, valor anterior e novo, justificativa), ou marca "(retificado em …)" no item | M | A, B | `retificacoes.py`; `pdf.py` |
| ED-07 | **P1** | PDF sem tags, idioma, título, marcadores e links; ordem de leitura intercala células | §7 | todas | PDF escrito à mão sem estrutura | inacessível a leitor de tela; navegação ruim | **Imediato (P):** `/Info` (Title, Subject, Author), `/Lang (pt-BR)`, `/ViewerPreferences /DisplayDocTitle`, `/Outlines` das seções, `Content-Disposition` com nome. **Decisão (G):** PDF marcado (tags) no motor próprio, troca de motor, ou versão HTML acessível do mesmo snapshot no portal | P / G | B | `pdf.py::render_documento`; `PublishedDocumentView` |
| ED-08 | **P1** | Documento longo sem navegação | 44 páginas; remissão p. 7 → p. 39 | B | sem outline e sem sumário | consulta lenta | marcadores (ED-07); sumário acima de um limite de páginas; links nas remissões | P / M | B | `pdf.py` |
| ED-09 | **P1** | "Endereço eletrônico do certame" citado e nunca informado | frase de convocação; texto do gestor | A 2–8 | nenhum campo garante o endereço; FR-027a proíbe endereço nos anexos | o candidato não sabe onde se inscrever nem onde sai o resultado | achado na Revisão quando nenhuma seção textual contém endereço; ou o endereço do portal da Unidade como contexto do ato. **Decisão do usuário**, porque esbarra na razão do FR-027a | P | E, D | validação; Unidade |
| ED-11 | P2 | Ordem divergente das modalidades entre duas tabelas do mesmo Perfil | PPI, PcD × PcD, PPI | A 2 | snapshot ordena por `code` (collation) e o quadro pela ordem declarada | releitura e erro de cruzamento | resolvido pela tabela única de ED-04; senão, ordenar as modalidades pela ordem do quadro | P | A | `pdf.py::_modalidades` |
| ED-13 | P2 | Leitura no celular | corpo ~6,9 px | todas | A4 fixo, sem tags | leitura difícil no celular | não mudar o layout do PDF; mitigar por ED-07 (tags ou HTML) e por um resumo no portal | — | B | — |
| ED-14 | P2 | Fontes não embutidas; hierarquia depende do negrito | poppler sem negrito | A 2 | base-14 sem arquivo de fonte | aparência varia com o visualizador; inviabiliza PDF/A e PDF/UA | embutir uma fonte de métricas compatíveis (ex.: Liberation Sans / Arimo) com `ToUnicode` | M | B | `pdf.py` |
| ED-15 | P2 | Frases de reversão e de convocação na margem zero, coladas à tabela | "Havendo ausência…" | A 2–6 | `recuo=0`, `antes=4.0` | parece regra geral, e não do Perfil | recuo do Perfil e espaço de bloco | P | A | `pdf.py:1885`, `:1913` |
| ED-16 | P2 | Listas sem recuo pendente | requisitos, alíneas | A 2, 7; B 7 | `escrever` com recuo único | listas longas difíceis de varrer | recuo pendente nas linhas de continuação | P | B | `Composicao.escrever` |
| ED-17 | P2 | Coluna "Evento" estreita no Cronograma | evento em 9 linhas | B 42 | partilha igual entre colunas longas | tabela alta e difícil de ler | dar peso à coluna de descrição | P | B | `_larguras_das_colunas` |
| ED-18 | P2 | Requerimento enviado na inscrição fora da lista de documentos | — | A 7–8 | norma executada em seção textual própria | candidato pode esquecer o Requerimento | linha na seção de documentos remetendo à seção da Matrícula | P | A | `pdf.py::_documentos_exigidos` |
| ED-19 | P2 | Ordem dos Perfis e dos fatos por código, não pela declarada | TD antes de TP; fatos fora da ordem do desempate | B 2, 7 | ordenação canônica do snapshot | ordem que o gestor não escolheu | `ordem` declarada para Perfis (como o quadro já tem) | M | C | `edital_snapshot` |
| ED-20 | P2 | Seções textuais não aceitam tabela | matriz curricular em prosa (linha de base de 22/09, p. 1–2); o 28/2026 a publica como "Quadro 1" | base | adiado pela 054 | quadros da amostra (matriz, barema) viram prosa ou anexo | decisão de spec já registrada pela 054 | G | C, D | — |
| ED-21 | P2 | Etapa sem descrição | "9.1 Análise documental / Caráter / Resultado / Realização" | A 7 | o modelo não tem campo para o que a Etapa avalia | o candidato não sabe o que acontece na Etapa sem o texto livre | campo de descrição da Etapa, ou remissão à seção textual | M | C | `StageSerializer` |
| ED-22 | P2 | Arquivo baixado sem nome e sem título | sem `Content-Disposition` | — | `PublishedDocumentView` | "documento.pdf" em todo download | nome "Edital-91-2026.pdf" (ou com a Retificação) | P | B | `publicacoes/api/views.py:131` |
| ED-23 | P3 | Linhas viúvas | "matrícula, a qualquer tempo."; "Ifes." | A 9; B 44 | quebra entre linhas sem regra de viúva | estético | exigir duas linhas no topo de página para o fim de parágrafo | P | B | `Composicao.paginar` |
| ED-24 | P3 | Caixa alta altera siglas no anúncio | "EAD", "CEFOR/IFES" | A 1; B 1 | `.upper()` sobre o título | desvio da grafia institucional | preservar siglas declaradas, ou anúncio em caixa mista | P | A | `pdf.py::_cabecalho` |
| ED-25 | P3 | Descrição do Edital entre o título e o preâmbulo | — | A 1; B 1 | `snapshot["description"]` impressa | duplica o preâmbulo | não imprimir a descrição no ato (fica para o portal) | P | A | `pdf.py::_cabecalho` |
| ED-26 | P3 | Rótulo "Remuneração" sem negrito | — | B 7 | escrita direta em vez de `_pares` | inconsistência | usar `_pares` | P | A | `pdf.py::_perfis` |
| ED-27 | P3 | Hash no rodapé de toda página sem dizer onde verificar | "Verificação cf7070f3…" | todas | FR-027a (sem endereço nos bytes) | pouco útil ao candidato | manter; avaliar "Código de verificação" + indicação genérica de onde conferir | P | A | `pdf.py::render_edital_pdf` |
| ED-28 | P3 | Hora com zero à esquerda; "às 00h"; falta "de" em períodos | L14 | A 7–8 | `humano.instante` | estético / redação | L14; o "00h" é o RC-22 já adiado | P | A | `humano.py`; `pdf.py::_etapas` |

---

## 12. Propostas de melhoria e plano de evolução

### 12.1 Correções imediatas — antes do primeiro Edital real

1. **ED-01 (aviso):** achado impeditivo, ou ao menos de alerta, para parágrafo de seção textual iniciado
   por número que não seja o da seção calculada. É barato e evita a remissão errada no ato.
2. **ED-02:** nomear na frase o resultado recorrível; avisar quando Cronograma e marcos divergirem
   sobre recurso.
3. **ED-03:** nada de arredondamento nem de empate no corte sob sorteio (validação e compositor juntos;
   corrigir só um lado deixa o defeito vivo).
4. **ED-12:** sem vaga imediata, sem quadro e sem frase de reversão.
5. **ED-10:** decidir com o Cefor se o ato pode sair sem nome.
6. **ED-07 (parte P) e ED-22:** título, idioma, marcadores e nome do arquivo. Não muda uma palavra do
   ato e melhora a navegação e a acessibilidade básicas.

Todas mudam o documento **só dos Editais publicados depois** — documento publicado não se regenera
(FR-091) —, o que é argumento para fazê-las antes do piloto.

> **Tratados depois desta auditoria.** ED-01 pela `065` (PR #266). ED-02, ED-03 e ED-12 pela `067`
> (`specs/067-correcoes-de-norma-do-edital/`), em 09/10/2026, com as decisões do responsável pelo
> produto: a frase de recurso nomeia o resultado pelo nome do marco entre aspas; um aviso de
> conferência, nunca impeditivo, põe os prazos dos marcos ao lado dos Eventos de recurso do
> Cronograma; sob sorteio declarado, nem arredondamento (exigido ou impresso) nem empate no corte; e
> o Perfil sem vaga imediata não imprime quadro nem reversão, **sem** regra nova para a reserva no
> cadastro. **Continua aberto:** a regra de reserva no cadastro (RC-58), e a correspondência entre o
> prazo do marco e o período do Cronograma, que o aviso mostra e só a conferência humana resolve.
> Os PDFs desta pasta continuam os da auditoria; os de depois estão em `specs/067-…/demonstracao/`.

### 12.2 Curto prazo

- **ED-04 + ED-11:** consolidar o que se repete (regra comum, tabela única Perfil × lista, método
  uma vez). É a melhoria de maior ganho para o candidato e reaproveita a lógica de identidade da 064.
- **ED-05:** reescrever as frases geradas (§5.2).
- **ED-06:** quadro de alterações no consolidado.
- **ED-09:** endereço do certame garantido no documento (com decisão).
- **ED-15, ED-16, ED-17, ED-18:** ajustes de composição, todos pequenos.

### 12.3 Opcionais

- ED-14 (fontes embutidas), ED-19 (ordem declarada dos Perfis), ED-21 (descrição da Etapa),
  sumário acima de um limite de páginas, links internos, quadro-resumo derivado dos dados (§6.3),
  ED-23 a ED-28.

### 12.4 Não justificam implementação agora

- **Layout específico para celular** dentro do PDF: o problema se resolve fora dele (tags ou HTML).
- **Elementos decorativos**, cores, ícones, caixas de destaque: nenhum achado os pede.
- **Reformulação completa do motor**: os defeitos achados são localizados e cabem no compositor
  atual. A única razão forte para trocar de motor seria decidir por PDF marcado (PDF/UA), e essa é uma
  **decisão a tomar à parte** — comparando o custo de marcar o PDF escrito à mão, o de trocar de motor
  e o de publicar uma versão HTML acessível do mesmo snapshot.
- **Tabelas nas seções textuais** (ED-20): já adiadas pela 054, com custo alto.

---

## 13. Avaliação final (heurística, 0 a 10)

| Critério | Nota | Justificativa |
|---|---|---|
| Identidade institucional | **7** | anatomia completa de ato do Cefor (brasão, órgão, ato, fecho, autoridade, integridade); perde por autoridade sem nome no registro real, siglas em caixa alta e "Autoridade responsável pelo ato" no lugar da assinatura |
| Qualidade visual | **7** | sóbrio, consistente, tabelas com grade e cabeçalho repetido, sem estouro de margem; perde por frases fora do recuo, listas sem recuo pendente, coluna estreita no Cronograma, brancos e viúvas |
| Hierarquia de informação | **6** | seção/subseção claras; dentro do Perfil, cinco níveis só por recuo; depende de negrito não embutido |
| Clareza da linguagem | **4** | o texto do gestor é o que ele escreve; as frases do sistema concentram jargão e regras sem objeto (L1–L17) |
| Organização | **4** | ordem de seções boa; regras espalhadas em três lugares; repetição por Perfil (5/9 e 38/44 páginas) |
| Facilidade de navegação | **3** | sem marcadores, sumário ou links; remissão a 32 páginas de distância |
| Legibilidade | **6** | ótima no papel (10,5 pt, entrelinha 1,45, justificação cuidadosa); ruim no celular (~6,9 px) |
| Acessibilidade | **2** | texto extraível e bom contraste; nenhuma estrutura, idioma, título ou marcador; ordem de leitura intercalada nas tabelas |
| Consistência funcional | **7** | fiel à configuração em todos os números; perde por recurso sem objeto, arredondamento sob sorteio, ordens divergentes e retificação silenciosa |
| Experiência do candidato | **4** | acha vagas, documentos e matrícula; não acha onde se inscrever e onde sai o resultado, e não entende com segurança como será classificado nem como recorrer |

---

## 14. Recomendação

**O PDF atual está adequado para publicação como edital oficial do Ifes?** Com ressalvas, e depende
do Edital:

- **Edital simples** (poucos Perfis, um marco, texto livre sem numeração digitada, endereço do certame
  escrito pelo gestor): **sim, depois das correções imediatas ED-01, ED-02, ED-03 e ED-12** e da
  decisão sobre ED-10.
- **Edital com muitos Perfis** (forma do cenário B, que é a dos editais de tutoria e dos unificados):
  **não**, até ED-04 e ED-05. A informação está correta, mas espalhada por 44 páginas e repetida 18
  vezes.

**Correções obrigatórias:** ED-01 (remissão errada é norma errada), ED-02 (prazo de um direito sem
objeto), ED-03 (regra sem objeto), ED-12 (afirma reserva de vaga onde não há vaga), ED-10 (decisão).

**Melhorias que realmente agregam valor ao candidato:** consolidação da repetição (ED-04), linguagem
das frases geradas (ED-05), alterações visíveis na Retificação (ED-06), endereço do certame (ED-09),
marcadores e metadados (ED-07, parte P).

**Refinamentos estéticos:** ED-15, ED-16, ED-17, ED-23, ED-24, ED-25, ED-26, ED-28.

---

## Anexo — como reproduzir

Os roteiros estão em [`auditoria-edital-pdf-2026-10-08/cenarios/`](auditoria-edital-pdf-2026-10-08/cenarios/).
Os caminhos absolutos do scratchpad dentro deles precisam ser ajustados.

1. Banco migrado de base: `createdb ps_auditoria_base` e `manage.py migrate` com
   `DB_NAME=ps_auditoria_base DB_USER=<superusuário> DB_RUNTIME_USER=<superusuário>`.
2. Para cada cenário, um banco novo a partir da base (`createdb -T ps_auditoria_base …`) e
   `manage.py shell -c "exec(open('cenario_a.py').read())"` (`cenario_a2.py` acrescenta a
   Retificação; `cenario_b.py` é o estresse).
3. Renderização: `qrender_all.py <pdf> <prefixo> <escala>` (CoreGraphics, via
   `uv run --with pyobjc-framework-Quartz`) e `pdftoppm` como segundo motor.
4. Antes/depois: `git archive <commit> backend/processo_seletivo backend/config | tar -x` e
   `render_old.py <raiz-extraída> <snapshot.json> <saída.pdf>`.

[registrar a decisão, não tomá-la]: ../CLAUDE.md
