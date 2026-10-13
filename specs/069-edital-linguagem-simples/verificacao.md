# Verificação — 069

O que foi medido na implementação, com a data, o comando e o resultado. Os testes que mudaram de
propósito estão em *Testes atualizados*, com a razão de cada um.

## Ponto de partida (T001)

12/10/2026, `main` `a79ce463`, contra PostgreSQL, banco `ps069`:

```bash
TEST_DB_ENGINE=postgresql DB_USER=$(whoami) DB_RUNTIME_USER=$(whoami) DB_NAME=ps069 \
  uv run pytest -q tests/unit/publicacoes tests/unit/editais tests/unit/interface tests/contract \
  tests/integration/publicacoes tests/interface tests/integration/portal tests/unit/divulgacao
```

**5295 passaram, 1 pulado, em 446 s.** O pulado é o par *termo × template* de
`test_vocabulario_da_composicao.py` que a tela não usa (um dos onze deliberados do `AGENTS.md`).

## Texto de referência (T002)

O texto (`pdftotext -layout`) de `specs/068-…/demonstracao/A-publicado-068.pdf` e `B-publicado-068.pdf`
e as 91 linhas de enunciados de `doc/analise-…/equivalencia.md` foram gravados no scratchpad da sessão,
fora do repositório, para a conferência final (T061).

## Guardas antes da mudança (T003–T007)

- **Comprovante e divulgação presos por bytes** (`tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py`):
  as fixtures `comprovante_v1.pdf` e `divulgacao_v1.pdf` foram compostas pela `main` `a79ce463`, antes de
  qualquer mudança no escritor, a partir de conteúdos sintéticos versionados ao lado (`*_v1.json`) que
  passam por acentos, "í", "ª", "º", moldura, tabela de 45 linhas em três páginas e a seção do sorteio.
  Não se regeneram nesta feature (SC-522).
- **Extratores guardados** (`test_extrator_de_texto.py`): os três extratores da suíte devolvem texto
  não vazio, com frase conhecida, para o Edital publicado, a prévia, o comprovante e a divulgação.
- **Métrica como parâmetro** (`test_metrica_do_documento.py`): `Composicao(metrica=…)`, com a Helvetica
  de hoje como padrão.
- Checkpoint da fase 2: `tests/contract`, `tests/unit/publicacoes`, `tests/unit/divulgacao` —
  **432 passaram**; a fixture de contrato e os PDFs esperados da `068` não mudaram.

## Testes atualizados de propósito

A regra do plano: o teste passa a afirmar a forma nova **com a mesma força**, ou fixa a redação 1 quando
prova a história; nunca é afrouxado.

### US1 — a redação 2

| Arquivo | O que mudou, e por quê |
|---|---|
| `test_documento_da_auditoria_depois_da_068.py` | O "agora" passa a ser o PDF que a `068` gravou (`specs/068-…/demonstracao/`), e não o compositor de hoje — a mesma decisão que a `068` tomou para a prova da `067`. Asserções intactas. |
| `test_equivalencia_da_consolidacao.py` | Compõe com `Composicao(redacao=REDACAO_1)`: é a prova do que a `068` fez, com as frases que ela publicava. O monkeypatch de `_frases_da_convocacao` aceita a redação. |
| `test_itens_do_documento.py` | Os bytes esperados dos cenários A e B passam a `specs/069-…/demonstracao/A-plana-069.pdf` e `B-plana-069.pdf` (os snapshots congelados têm o catálogo anterior, e saem na apresentação plana). Regenerados a cada fase que muda a composição; os da `068` ficam como evidência dela. |
| `tests/contract/fixtures/documento_publicado_v1.pdf` | Regenerada pela regra da docstring (mudança de composição deliberada), com o diff de texto revisado: só as frases da redação 2, "Cadastro de reserva", "Regras de classificação", a Etapa em frase e a paginação (4 → 3 páginas). |
| `tests/contract/test_documento_publicado.py` | Os mesmos parâmetros (alvo de cada critério, fatos, pesos, arredondamento, reversão), afirmados nas frases da redação 2. |
| `test_pdf_classificacao.py` | 46 casos: cada parâmetro que fecha a conta continua afirmado, na frase nova (C3–C14, K1–K10, T1–T8, S1–S7). O teste dos rótulos do método passou a varrer o **valor** de cada um dos sete campos, porque a redação 2 diz fonte, ocorrência e instante na abertura; a força é a mesma — um campo que suma reprova. |
| `test_consolidacao_por_perfil.py` | As frases que a `068` imprime uma vez (reversão, convocação, separação por Perfil, método comum) e o rótulo G1–G3 "Regras de classificação"; as partes do marco na subseção comum (FR-1357) conferidas pelas linhas da redação 2. |
| `test_pdf.py` | Cadastro (P2), autenticidade (F1), Etapa em frase (E2), teto (V7/V8), Cronograma com "Quando". |
| `test_pdf_documentos_exigidos.py` | D2–D4 ("Também, de quem concorre…") e D5 (instrução em minúscula). |
| `test_documento_sob_sorteio.py`, `test_frase_de_recurso.py`, `test_perfil_sem_vaga_imediata.py`, `test_fecho_e_normas_da_054.py` | As mesmas ausências e presenças, nas frases da redação 2 (C11, K5/K6, R1, V1/V2, V11/V12, V7). Em `test_perfil_sem_vaga_imediata.py`, a varredura de "cadastro de reserva" desconta o rótulo do par, que é dado, e não frase sobre a reserva. |
| `tests/unit/interface/test_revisao.py`, `tests/interface/test_correcoes_de_norma_na_revisao.py` | A Revisão mostra as frases do documento na redação 2 (FR-1364); os rótulos dos pares continuam os da equipe. |
| `tests/migrations/test_migrations.py` | `editais` sobe para 23, com a justificativa da `0023` (rótulos de `callForm`, sem SQL). |

### US6 — a redação que o ato publicado lê

| Arquivo | O que mudou, e por quê |
|---|---|
| `tests/interface/test_legibilidade_da_classificacao.py` | A página do ato de ordenação de um Edital publicado depois da `069` nomeia os critérios na redação 2; a do publicado antes continua na 1 (`test_redacao_do_ato_publicado.py` prova os dois lados). |
| `tests/migrations/test_migrations.py` | `publicacoes` sobe para 11, com a justificativa da `0011` (`redacao_do_documento`, padrão 1: o acervo é da redação 1). |

### US3 — fonte embutida e hierarquia

| Arquivo | O que mudou, e por quê |
|---|---|
| `test_pdf.py`, `test_pdf_classificacao.py` | As medidas de largura e margem do Edital passam a usar `METRICA_DO_EDITAL` (a fonte embutida), e o corpo do título de seção é `CORPO_TITULO_DE_SECAO`. O comprovante continua medido pela Helvetica. |
| `tests/contract/fixtures/documento_publicado_v1.pdf` | Regenerada de novo: a fonte embutida muda a quebra de linha e o arquivo (objetos 4–9). |

**A licença** (T030, FR-1380). Baixado com aprovação do usuário: `liberation-fonts-ttf-2.1.5.tar.gz`,
2.385.008 bytes, do release oficial. A versão 2.1.5 está sob a SIL OFL 1.1, com "Liberation" entre os
nomes reservados. Um subconjunto é versão modificada, e a OFL não deixa versão modificada usar nome
reservado: a família embutida se chama **Edital Sans**. Os resumos de origem e dos arquivos gerados
estão em `backend/processo_seletivo/publicacoes/infrastructure/fontes/ORIGEM.md`, e a licença, em
`LICENSE` ao lado.

### US2 — a apresentação por perguntas

O catálogo vigente passou a ser o da `069`. Os snapshots dos testes que afirmam a forma **plana** — a
dos Editais publicados antes e dos consolidados deles, que continua a sair — passam a nascer do
catálogo da `054`, congelado; os que afirmam a forma nova pedem o da `069`. Nenhuma asserção foi
afrouxada.

| Arquivo | O que mudou, e por quê |
|---|---|
| `tests/unit/publicacoes/test_pdf.py` | `secoes()` compõe pelo catálogo da `054` por padrão (`catalogo_=` para o da `069`). "Seleção" saía da descrição do Edital, que não vai mais ao ato (FR-1378): a acentuação é conferida em "Computação". O brasão é procurado pelo operador com o nome (`/Im1 Do`), porque "Do" também aparece no sumário. A contagem de títulos numerados ignora as linhas do sumário. |
| `tests/unit/editais/test_secoes.py` | `ORDEM_ESPERADA` é o catálogo da `069`; o da `054` ganha `ORDEM_ESPERADA_DA_054` e um caso que o prende congelado. A posição relativa da classificação: as Etapas saem logo depois dela, como subseções. |
| `tests/unit/editais/test_catalogo_da_054.py` | A ordem das quinze seções do 28/2026 é conferida no catálogo da `054` (a decisão daquela spec); as chaves, nos dois. Os títulos numerados ignoram o sumário. |
| `tests/unit/editais/test_conflito_de_numeracao.py`, `test_remissoes.py` | Pelo catálogo da `054`: provam a regra da `065` na apresentação plana. A regra pelo prefixo apresentado tem arquivo próprio (`test_numeracao_apresentada_nas_conferencias.py`). |
| `tests/unit/editais/test_avisos_do_documento_oficial.py` | A Inscrição é a 8ª do catálogo da `069`, e o título dela é «Como se inscrever?»; «Disposições finais» em caixa de frase. |
| `tests/unit/publicacoes/test_itens_do_documento.py` | O guardião compõe pela apresentação do snapshot e ganhou cinco casos por perguntas (A e B levados ao catálogo novo, um Perfil, Etapas, seções reunidas). A unidade do teste de bytes tem a sigla "Cefor", que o anúncio preserva (FR-1377). |
| `tests/unit/publicacoes/test_consolidacao_por_perfil.py` | O rodapé "Página N de M", que o extrator dá numa linha própria, sai das linhas do corpo. |
| `tests/unit/publicacoes/test_atribuicoes_consolidadas.py` | Com o equilíbrio (FR-1392), a subseção comum que começaria com a página quase vazia divide-se: inteira, ou partida na página seguinte com ao menos dois itens de cada lado e o título junto do primeiro. |
| `tests/contract/fixtures/documento_publicado_v1.pdf` | Regenerada duas vezes, com o diff de texto revisado: sem a descrição, com o sumário, e a paginação do fecho junto da última seção. |
| `specs/069-…/demonstracao/*-plana-069.pdf` | Regenerados: a descrição sai, as siglas ficam, o sumário entra. |
| `tests/interface/test_conteudo_da_054.py` | A legenda leva o rótulo do número ("1.1 Público-alvo"), e a pergunta que reúne a seção vem antes dela. A Matrícula sem texto tem o número da seção que a declaração faz sair. |
| `tests/interface/test_fluxo.py` | "Como será a seleção?" com as Etapas em N.k; "Como recorrer?"; "Cronograma" em caixa de frase. |
| `tests/interface/test_caractere_sem_grafia.py` | Nenhum "?" de substituição; os títulos em pergunta têm o seu, no fim. |
| `tests/integration/publicacoes/test_numeracao_na_publicacao.py` | A Inscrição sai como 5 (o Cronograma veio para antes dela); os subitens coerentes são 5.1 e 5.2. |
| `tests/integration/publicacoes/test_documento_da_retificacao_que_acrescenta.py` | O recurso em "Como recorrer?", com o alcance pelo código (R6); a matriz de vagas se chama "Vagas por Perfil e lista de concorrência". |
| `tests/integration/publicacoes/test_retificacoes.py` | O reagrupamento da `064` e da `068`, dito na forma nova: "Atribuições" com rótulos de grupo, e o recurso em "Como recorrer?". O documento original continua byte a byte. |
| `tests/integration/publicacoes/test_sorteio_no_documento.py` | Os dados do sorteio na subseção "Dados para conferir o sorteio". |
| `tests/acceptance/test_us4_publicacao.py` | O número de vagas do conteúdo homologado continua chegando ao documento, agora na tabela "Vagas por Perfil e lista de concorrência", e não no rótulo "Vagas imediatas". |
| `tests/unit/publicacoes/test_numeracao_apresentada.py` | A chave principal sem texto tem o número da seção que sai pela norma (como a plana faz com a seção de norma, UX-132 da `054`). |

**Achados de composição corrigidos no caminho.** O recurso de um grupo saía "Para o Perfil P1 — Perfil A —
contra…", dois travessões numa frase: o R6 do contrato diz só os códigos. O resumo dizia "1 vaga em
P1" quando o Perfil não tinha localidade: sem localidade em todos, o resumo diz os códigos.

**A prévia e o publicado.** A prévia não tem o fecho (FR-014 da `008`), e o publicado leva a última
seção junto dele (contrato do documento §7). Só ela pode mudar de página entre os dois; tudo antes
quebra igual, e o teste prende isso.

### US5 — a paginação

**As regras** (R-011), todas só no Edital — o comprovante e a divulgação paginam como antes, byte a
byte (`Composicao(equilibrio=False)` por padrão):

- **a última seção vai com o fecho** (`com_o_fecho`): as duas num bloco coeso; se não couberem juntas
  numa página, a última linha da seção pede companhia e a quebra a leva. Era o defeito de A na `068` e
  na amostra: a página 7 só com a data, a autoridade e a autenticidade;
- **equilíbrio** (`FRACAO_EM_BRANCO = 0.5`, `LINHAS_PARA_DIVIDIR = 4`): o bloco coeso que saltaria
  deixando mais da metade da área útil em branco divide-se, se tiver ao menos quatro linhas e não for
  destacado (moldura partida é pior que o branco);
- o resto já era do paginador: o `junto` dos títulos, subseções, rótulos e legendas; a linha de tabela
  coesa; o cabeçalho repetido só quando há linha para encabeçar; o parágrafo maior que a página se
  partindo.

**A calibração** (T054). Os limites de 45% e 60% da R-011 não foram precisos: com o equilíbrio e o
fecho, as páginas de A, B e da variante passam pelos seis critérios do teste de forma
(`test_paginacao_do_edital.py`). As páginas foram olhadas em CoreGraphics (PDFKit): A em 7 páginas —
o resumo e o preâmbulo na primeira, o sumário abrindo a segunda, a última seção com o fecho na
sétima; B em 10. A primeira página de A tem cerca de 37% em branco, porque o sumário é coeso e não
cabe nela — dentro do limite, e sumário partido seria pior.

**A prévia e o publicado.** A prévia não tem o fecho; a última seção pode cair em outra página no
publicado. Tudo antes dela quebra igual (`test_a_previa_e_o_publicado_tem_as_mesmas_paginas`).

### US4 — a navegação no arquivo

- `/Info` com `/Title` (o anúncio em caixa mista, "Edital nº 91/2026 — …") e `/Author` ("Ifes —
  Cefor"), sem data; catálogo com `/Lang (pt-BR)`, `/ViewerPreferences << /DisplayDocTitle true >>`,
  `/PageMode /UseOutlines` e `/Outlines`;
- marcadores das seções e subseções, em dois níveis, pela lista de itens que numera o documento;
- links do sumário para cada seção e `/URI` para os e-mails e endereços `http(s)` que o texto
  imprime — nenhum endereço acrescentado;
- numeração de objetos fixa, sem `/ID`: os mesmos bytes em duas composições;
- download com `Content-Disposition: inline; filename="edital-«n»-«ano».pdf"`, e
  `…-retificado-«AAAA-MM-DD».pdf` com a data no fuso institucional.

Conferido fora da suíte: `pdfinfo` (poppler) lê título, autor e `Tagged: no` sem erro; um roteiro em
PDFKit lista os 21 marcadores de A com as páginas certas, os 14 links do sumário e o `mailto:`.

### Cenários pelo fluxo real (T063)

12/10/2026, esta branch, bancos novos a partir de `ps_069_base` (preparado por `make preparar`: 40 de
40 tabelas protegidas, a Unidade e os três modelos de aviso), pelos roteiros da auditoria
(`create_process_with_first_edital` → `replace_draft` → `submit_edital` → `homologate_edital` →
`publish_edital`). O "antes" é a `main` como a `068` a deixou: os PDFs de `specs/068-…/demonstracao/`.

| Cenário | Banco | Resultado | Páginas `068` → `069` |
|---|---|---|---|
| A | `ps_069_a` | publicado; na submissão, os dois avisos de remissão pelo título ("seção Perfis de Vaga", em Requisitos gerais e na seleção) e os avisos de sempre (Evento de 2027, prazos de recurso) | 6 → 7 |
| B, texto original | `ps_069_b_original` | **recusado**: cinco conflitos de numeração comprovados (Requisitos gerais 2.1, Inscrição 5, Verificação 7.4, Convocação 9, Disposições finais 12) — o achado 1 | — |
| B, numeração corrigida (`demonstracao/cenarios/cenario_b_069.py`) | `ps_069_b` | publicado | 14 → 10 |

**O documento do fluxo real é o da demonstração.** O texto de `A-fluxo-real-069.pdf` é o de
`A-publicado-069.pdf` salvo a data do ato (12 e não 8 de outubro) e o hash; o de B, salvo a numeração
que o roteiro corrigiu. Medidas sobre eles: fatos (SC-516) 100% em A e B; termos internos (SC-518)
zero; sumário e marcadores contra as páginas (SC-520) 100%; paginação (SC-521) sem defeito; B com o
nome comum por grupo e os atributos iguais uma vez (SC-524) — as mesmas asserções de
`test_documento_da_auditoria_depois_da_069.py`, `test_arquivo_do_edital.py` e
`test_paginacao_do_edital.py`, que rodam sobre a composição dos mesmos snapshots.

### Edital publicado antes, pelo fluxo real (T065, quickstart §5, §7 e §8)

12/10/2026, banco `ps_069_main`: migrado e populado com o código da `main` (`a79ce463`, extraído por
`git archive` e rodado pelo `manage.py` de dentro), e depois migrado com esta branch (`editais/0023`,
`publicacoes/0011`). Com a `main`: o cenário A publicado, e um segundo Edital (o mesmo, com outro
número) só homologado. Com esta branch:

| Passo | Resultado |
|---|---|
| §7, acervo | o documento guardado é byte a byte o que a `main` gravou, e é servido assim; `redacao_do_documento` = 1; o download sai como `edital-91-2026.pdf` |
| §5, Retificação do prazo de inscrições | o consolidado sai na **apresentação plana**, com a redação 2 (`redacao_do_documento` = 2): os mesmos 17 títulos em caixa alta, a mesma numeração e os mesmos itens do original (`itens_do_documento` iguais); "Regras de classificação: as descritas no item 5.6" no lugar de "Marcos classificatórios", com o mesmo número e o mesmo destino (D-007); a fonte embutida, o sumário e o título; sem resumo e sem seção reunida. Download `edital-91-2026-retificado-2026-10-12.pdf` |
| §5, tela de Retificação | os grupos das seções com os números do PDF original ("1 — Disposições Preliminares", "6 — Da Inscrição") |
| §8, Edital homologado antes | a publicação é recusada com `homologated_revision_changed`, e nada é publicado |

Os dois PDFs estão em `demonstracao/` (`A-publicado-pela-main.pdf`, `A-main-retificado-pela-069.pdf`).
O §6 — a página de um ato de ordenação publicado antes — é provado por
`test_redacao_do_ato_publicado.py` e mostrado pela jornada (T066).

### Jornada pelo navegador (T066)

Em `demonstracao/jornada/README.md`, com as capturas e o PDF baixado do portal: o Elaborador compõe
(a numeração apresentada e o aviso de remissão na etapa Conteúdo), confere a prévia e a Revisão; três
pessoas submetem, homologam e publicam pela interface; o candidato chega ao Edital pelo portal, com o
nome `edital-36-2027.pdf`, título, marcadores e links; a presidência abre a página do ato de ordenação
publicado pela `main` (redação 1, "maior pontuação na Etapa Prova objetiva") e a proposta do mesmo marco
na redação vigente ("… na Etapa “Prova objetiva”"). O README diz as duas diferenças do roteiro — o ato
de redação 1 semeado pelo comando da `main`, e não pela tela, e o critério acrescentado na cópia da
`main` — e a correção que a jornada provocou na etapa Conteúdo.

### Três motores (T064, SC-519)

12/10/2026, `A-publicado-069.pdf` e `B-variante-069.pdf`, páginas guardadas em `demonstracao/motores/`:

| Motor | Como | O que se viu |
|---|---|---|
| CoreGraphics | PDFKit, roteiro em Swift, escala 1,2 | títulos com fio, subseções, rótulos e o negrito do resumo e dos pares; fundo 0,95 com contorno; o recuo pendente dos itens; texto justificado sem passar da margem |
| poppler | `pdftoppm -r 100`; `pdffonts` | **o negrito agora sai negrito** — o ED-14, que era o poppler trocando o Helvetica-Bold não embutido pelo regular; as duas fontes listadas como `TrueType`, `emb yes`, `sub yes` |
| PDFium | o visualizador do Chromium, no navegador embutido | o `/Title` na aba ("Edital nº 91/2026 — …", pelo `DisplayDocTitle`), o painel de marcadores oferecido, e a página igual às outras duas |

A medição da margem é a do teste `test_nenhuma_linha_passa_da_margem_pela_metrica_da_fonte_embutida`
(A, B e o parágrafo de "í", "ª" e "º"), pela métrica da fonte que o arquivo embute. Na variante, a
partilha parcial sai como o contrato pede: "Para todos os Perfis:" com a ordem, a nota, o
arredondamento e o desempate, e depois cada grupo com a unidade do corte inteira.

### Acessibilidade — a limitação declarada (T070, FR-1388)

**Medido:** título do documento na janela do leitor, idioma `pt-BR`, marcadores navegáveis, links do
sumário e dos endereços, fonte embutida (o texto extraído é o desenhado, com acentos, em qualquer
leitor), hierarquia visual sem depender de cor.

**Não medido, e não prometido:** o PDF continua **sem marcação** (`Tagged: no`, sem
`/StructTreeRoot`), e por isso a ordem de leitura, os cabeçalhos e as tabelas não existem para um
leitor de tela como estrutura; nenhum teste com leitor de tela foi feito. Esta entrega não declara
conformidade com PDF/UA nem com as diretrizes de acessibilidade. Está também em *O que esta feature
não cobre* da spec.

## Checkpoint das US1, US6 e US3 (T018, T025, T034)

12/10/2026, a suíte inteira contra PostgreSQL (`DB_NAME=ps069`), antes das mudanças da US2:

**10583 passaram, 11 pulados, 1 falha, em 1268 s.** A falha é
`tests/test_readme_acompanha_o_codigo.py::test_toda_pasta_de_specs_aparece_na_tabela_de_incrementos`:
a pasta `specs/069-…` ainda não está na tabela de incrementos do README, que é tarefa da fase final
(T068). Os onze pulados são os deliberados do `AGENTS.md`.

## Verificação final (T071)

12/10/2026, a worktree com todas as fases, contra PostgreSQL (`DB_NAME=ps069`):

- `make lint` — `ruff check` e `ruff format --check` verdes (1414 arquivos);
- `make check` — sem migration pendente;
- `make DB_NAME=ps069 test-pg` — **10780 passaram, 11 pulados, em 1183 s**. Os onze pulados são os
  deliberados do `AGENTS.md` (não mudaram, e por isso o `AGENTS.md` não muda). `test_citacoes_de_requisito.py`
  (com a matriz de rastreabilidade) e `test_sem_dado_pessoal_da_amostra.py` verdes.

A rodada anterior, uma hora antes, deu 10777 passando e 1 falha — `test_us4_publicacao.py`, que procurava o
rótulo "Vagas imediatas" da tabela de antes; atualizado (ver *US2*).

## Achados do caminho que não viraram escopo (T072)

Registro, e não decisão: cada um fica para o responsável pelo produto. Os dois da análise —
o comprovante de residência só do TP-01 e a condição do sorteio no texto — já estão em `doc/`.

1. **A numeração digitada do original colide com as subseções apresentadas.** Um Edital transcrito
   do Word com "2.1 Ser brasileiro…" dentro de "Requisitos gerais", que agora sai como a subseção
   2.1, tem dois itens 2.1. A conferência da `065`, pelo prefixo apresentado, recusa a publicação até a
   numeração ser corrigida — o comportamento certo, mas que vai aparecer em todo Edital transcrito com
   numeração. Na seção que imprime subseções ("Como se inscrever?" com o atendimento em 5.1), o texto
   principal não tem número livre que não colida a partir de 5.1: na prática, o Elaborador retira os
   números. Vale decidir se o assistente deve oferecer isso, ou se a orientação basta.
2. **A forma de convocação gerada não diz onde se publica** (V4, achado 1 da conferência por
   enunciado). O "onde" fica com o texto do Elaborador; o endereço do certame gerado é outra feature.
3. **Atribuições e requisitos escritos com "•" não ganham recuo pendente.** São texto livre (FR-1395) e
   saem como parágrafos: a segunda linha de um item começa na margem, e não sob a primeira palavra. O
   recuo pendente desta entrega é o das listas que o sistema compõe (ED-16). Reconhecer o marcador no
   texto livre seria interpretação do texto, e ficou de fora.
4. **A inicial do valor muda de caixa dentro da frase comum.** "remuneração: bolsa mensal…" — o dado
   é "Bolsa mensal…". É apresentação, e não muda a regra; fica registrado porque o texto do dado não
   sai literal ali.
5. **O sumário é coeso.** Quando não cabe na primeira página, vai inteiro para a segunda, e a primeira
   fica com cerca de um terço em branco (A). Partir o sumário seria pior para quem o usa; o equilíbrio
   não o divide, de propósito.
6. **A prévia e o publicado podem diferir na página da última seção**, porque só o publicado tem o
   fecho e a última seção vai com ele. Tudo antes quebra igual.

## Revisão de código (12/10/2026)

Quatro revisões, uma por camada (compositor, apresentação e publicação, domínio dos Editais,
interface). Cada achado foi conferido no código, ou reproduzido, antes de virar correção; o que não
se confirmou ficou de fora. Cada correção tem teste que reprova sem ela.

**Corrigidos**

| Achado | Onde | Correção |
|---|---|---|
| O Edital de um Perfil perdia, no corpo, o nome, a descrição, a carga horária, a remuneração e o cadastro do Perfil — a matriz não traz nome, e a frase P1 e a tabela de características só existiam com dois Perfis | `pdf.frase_dos_atributos_comuns` | a frase sai como "Perfil P1: …" |
| A descrição igual sob nomes diferentes não saía em lugar nenhum | `apresentacao._caracteristicas` | vai para a tabela |
| As frases da ordem eram partilhadas uma a uma, e a normalização ("Depois, o resultado é dividido…") saía depois do arredondamento, sob outro rótulo de grupo | `apresentacao._unidades_do_perfil` | a ordem do marco é uma unidade só |
| A frase do uso no desempate valia para o grupo inteiro dos dados declarados, inclusive o Perfil cujo marco não os usa | `apresentacao._dados_declarados` | grupos pelo que se imprime, com a frase |
| O resumo dizia "sorteio, seguido de Análise documental", e a Etapa habilita ao sorteio, antes dele | `apresentacao._selecao_em_poucas_palavras` | "com", que não afirma ordem; os três PDFs de demonstração regravados, e só essa linha mudou |
| A última célula da tabela, ou a última linha do destaque, ia sozinha para a página do fecho, fora da grade | `pdf.prender_a_ultima_linha` | o `junto` não vale dentro de quadro ou moldura; ali o fecho volta a poder abrir a página |
| O pedaço de um endereço partido pelo refluxo virava link para outro lugar | `pdf._anotacoes` | só vira link o endereço escrito inteiro no texto |
| Endereço com acento ia em UTF-16 na `/URI`, que os leitores não abrem | `pdf._uri` | `%XX` do UTF-8 |
| "Cefor-Ifes" subia para "CEFOR-IFES" no anúncio | `pdf.anuncio_em_caixa_alta` | o hífen separa como a barra |
| O sumário se dividia pelo equilíbrio, contra o achado 5 acima | `pdf.sumario` | bloco `INTEIRO` |
| "Para todos os Perfis:" com Perfil sem marco; os dados do sorteio sem rótulo quando só parte dos Perfis sorteia | `apresentacao._regras_dos_marcos`, `_dados_do_sorteio` | o rótulo diz os Perfis |
| O nome do arquivo ia cru em `filename="…"`: aspas quebravam o cabeçalho, e caractere fora do ASCII fazia o navegador ignorá-lo | `publicacoes/api/views.py` | `content_disposition_header` (RFC 6266) e o nome sem caractere proibido |
| O aviso de remissão pelo título mudava de texto conforme o `PYTHONHASHSEED`: "Etapas de Avaliação" e "Etapas de avaliação" empatavam, e o destino sugerido sumia num processo e aparecia no outro | `numeracao_digitada.remissoes_por_titulo`, `validation._remissao_a_secao_pelo_titulo` | ordem estável, a grafia da `054` primeiro e o destino pela caixa ignorada |
| "cada item da inscrição" e "o item do certificado" avisavam como remissão | `remissoes_por_titulo` | depois de "seção"/"item", a inicial do título vale como escrita |
| A lista das subseções na mensagem de conflito saía como texto: "8.1, 8.10, 8.2" | `validation` | pela ordem dos números |
| Na etapa Conteúdo, digitar ou esvaziar uma seção deixava as outras com o número salvo, que o documento já não imprimiria; o mesmo depois de envio recusado | `conteudo.js` | os números ficam provisórios até salvar |
| O membro sozinho na seção ("Público-alvo" sem Requisitos) aparecia como "3. Público-alvo", título que o documento não imprime | `forms.py`, `revisao.py` | "sai como o texto de 3. Quem pode se inscrever?" |
| A principal com só o lembrete do Requerimento era dada como "sai" mesmo sem texto | `forms._principais_que_saem_sem_texto` | o lembrete não conta, como no plano |
| A Revisão dizia "nenhuma Etapa enumerada" do marco com Etapas e sem operação | `revisao._leitura_do_marco` | "operação não declarada, sobre …" |
| O parágrafo de ajuda da etapa Conteúdo dizia que só sai a seção com texto e que a numeração não salta | `compor_conteudo.html` | texto próprio na apresentação por perguntas |

A frase "Perfil P1: …" e o "com" do resumo são redação nova, e entram na aprovação das frases
(`demonstracao/equivalencia.md`) com as demais.

**Registrados, e não corrigidos**

1. A divisão pelo equilíbrio não garante duas linhas de cada lado: onde ela cai é o espaço que
   decide, e uma linha só no alto da página seguinte é possível. É a troca contra a meia página em
   branco; o comentário de `_divisivel` passou a dizer isso.
2. `inicial_minuscula` não distingue sigla de uma maiúscula ("Ifes …" vira "ifes …"). Distinguir pede
   uma lista de siglas, e o caso é raro no rótulo de dado declarado.
3. A linha de título copiada do Word ("8. DA INSCRIÇÃO") avisa duas vezes: título transcrito (`065`)
   e remissão pelo título.
4. O título da pergunta acima do primeiro membro, na etapa Conteúdo, também é o do último salvamento.
5. Marcador de subseção que o leitor não ache tira a subseção do sumário do arquivo, mas os filhos
   dela iriam para a seção anterior. Não acontece em A nem em B.
6. `_arquivo_do_edital` sem `navegacao` não tem chamador; o escritor do comprovante continua o
   próprio, por causa dos bytes.

Depois das correções: `make DB_NAME=ps069 lint check test-pg` — lint e check limpos, 10793 passaram e
11 pulados (os mesmos onze), em 1332 s. Os testes de JavaScript: 137 passaram.
