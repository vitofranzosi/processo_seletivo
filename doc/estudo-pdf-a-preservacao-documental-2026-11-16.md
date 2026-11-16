# Estudo — PDF/A como formato de preservação no GPS (16/11/2026)

Pergunta: **como o GPS pode preservar melhor os seus documentos digitais ao longo dos anos, sem
aumentar desnecessariamente a complexidade do sistema?**

Estudo e prova de conceito, sem implementação: nenhuma linha do GPS foi alterada, nenhum banco foi
tocado. A POC está em [`estudo-pdf-a-preservacao-documental-2026-11-16/poc/`](estudo-pdf-a-preservacao-documental-2026-11-16/poc/README.md),
com os roteiros, as versões das ferramentas e os resultados brutos.

> **Desdobramento (16/11/2026).** O usuário decidiu adotar o PDF/A só em parte: a frente 1 da
> resposta curta virou a spec [`178`](../specs/178-documentos-em-pdfa/spec.md), implementada e
> mergeada no mesmo dia (#581). A frente 2 continua como recomendação, sem decisão; o pacote de
> destinação espera o B-2.

## Resposta curta

**Adotar seletivamente, em duas frentes de tamanho muito diferente.**

1. **Os documentos que o GPS gera nascem PDF/A** — e isso é barato. O escritor próprio do GPS já
   está a quatro acréscimos do PDF/A-2b: com eles, o Edital e o relatório passaram no veraPDF em
   PDF/A-2b, 2u, e até 1b (Edital) e 2a (relatório). O comprovante e a família da divulgação
   pedem um quinto, embutir a fonte que o Edital já embute. Sem dependência nova em produção.
   São esses os documentos de guarda permanente (resultados, recursos, o próprio Edital).
2. **Os documentos que o candidato envia não são convertidos durante o certame.** Ficam como
   estão — originais intactos, com o SHA-256 que o GPS já grava —, e a única coisa a reforçar é a
   conferência periódica desse resumo. A representação de preservação, se vier, é produzida **na
   destinação**, e talvez nem pelo GPS: a tabela de temporalidade manda eliminar a maior parte
   desses arquivos um ano depois da homologação, e a que fica (o assentamento de quem se
   matriculou) sai do GPS para outro sistema.

A hipótese do pedido — converter só na fase de arquivamento — se confirma, e com uma razão a mais
do que a economia: a POC mostrou que a conversão automática **produz PDF/A válido a partir de
documento ilegível, apaga assinatura e degrada o texto sem que nenhum validador acuse**. Converter
durante a operação poria esse risco sobre todo arquivo de todo candidato, para benefício de quase
nenhum.

---

## 1. Diagnóstico: os fluxos documentais que existem

Referências relativas a `backend/processo_seletivo/`.

### 1.1 O que entra

| Ponto | Onde | Guarda | Validação | Imutabilidade |
|---|---|---|---|---|
| Documento da inscrição (candidato) | `portal/views.py:2571` → `inscricoes/application/rascunho.py:467-521`; modelo `DocumentoSubmetido` (`inscricoes/models.py:328-386`) | disco privado, `inscricoes/<inscricao>/<uuid4>.pdf` (`inscricoes/storage.py:64-72`); SHA-256 em `content_hash` | `%PDF-` + extensão + limite de 10 MiB (`shared/arquivos.py:56-93`; `config/settings/base.py:478-480`); reconferido no envio (`inscricoes/application/submissao.py:480-511`) | trigger depois do envio (`inscricoes/migrations/0007_imutabilidade_da_enviada.py:56-75`); no rascunho, substituível |
| Documento da convocação (candidato) | `portal/views.py:3110` → `convocacao/application/documentos.py:619-722`; `ApresentacaoDeDocumento` (`convocacao/models.py:516-591`) | disco privado, `convocacoes/<chamada>/<uuid4>.pdf`; SHA-256 obrigatório | a mesma `aceitar`; reenvio do mesmo resumo é deduplicado | append-only (`seguranca/papeis.py:170`), cada envio é versão nova |
| Anexo do Edital (gestão) | `interface/views.py:1597-1606`, `:4611-4650` → `editais/application/anexos.py:58-73`; `ArtefatoAnexo` (`editais/models/anexos.py:24-66`) | **no banco** (`BinaryField`), SHA-256 em `document_hash` | a mesma `aceitar`, limite de 5 MiB | congelado na Publicação por trigger (`editais/migrations/0013_congelamento_do_artefato.py`) |
| Vídeo da verificação (candidato) | `portal/verificacao.py`, `verificacao/application/envio.py` | disco, SHA-256 conferido contra o do aparelho | contêiner MP4/WebM | append-only; **único caso com retenção** (`verificacao/application/retencao.py`) |

Requerimentos, recursos, matrículas, divulgação e formalização **não recebem arquivo**: o recurso
referencia o `DocumentoSubmetido`, sem cópia.

Três fatos decidem o resto do estudo:

- **Os bytes recebidos nunca são reescritos**, e o resumo é a âncora de todas as entregas: a
  comissão recebe o arquivo por `copia_verificada` (`portal/arquivos.py:110-132`), que recalcula o
  SHA-256 e recusa com 409 se divergir. Um arquivo derivado que substituísse o original quebraria
  essa cadeia.
- **O GPS não lê o conteúdo do que o candidato envia, por decisão declarada.** "OCR, conferência de
  conteúdo, antivírus, extração — está fora de escopo por decisão declarada"
  (`shared/arquivos.py:3-5`), e um teste-guarda proíbe importar pypdf, pdfminer, PyMuPDF, PIL e
  afins no backend (`tests/unit/test_leitura_do_documento_submetido.py`). Converter para PDF/A é
  interpretar o PDF inteiro. Fazê-lo dentro do GPS é rever essa decisão — governança do usuário.
- **Não há processamento assíncrono.** Nem Celery, nem fila, nem worker. O que roda fora da
  requisição são comandos de `manage.py` chamados por timers do systemd, documentados e não
  versionados (`despachar_avisos` a cada minuto; `doc/implantacao-em-producao-ubuntu.md`, §16.4).
  É esse o padrão a reaproveitar, se algum processamento em lote vier a existir.

### 1.2 O que sai

Todo PDF do GPS sai de um **escritor próprio**, sem biblioteca, em `publicacoes/infrastructure/pdf.py`
(6.122 linhas, cabeçalho `%PDF-1.4`), e é **determinístico**: sem data, sem identificador
aleatório — o mesmo conteúdo dá os mesmos bytes, e é isso que permite publicar o resumo do
documento e esperar que confira.

| Documento | Escritor | Fonte | Guardado? |
|---|---|---|---|
| Edital publicado e Retificação | `_arquivo_do_edital` (`pdf.py:5854`) | **Edital Sans embutida** (Liberation Sans 2.1.5, OFL; `publicacoes/infrastructure/fonte.py`) | sim, `DocumentoPublicado.bytes`, append-only, com SHA-256 |
| Resultado, publicação das inscrições, convocados, agenda | `render_documento` (`pdf.py:6050`) | **Helvetica base-14, não embutida** | sim, append-only, com SHA-256 |
| Comprovante de inscrição | `render_documento` via `inscricoes/infrastructure/comprovante_pdf.py` | Helvetica não embutida | não — regenerado a cada download, com bytes prometidos iguais |
| Relatórios do Edital e consolidado | `interface/diagramacao.py`, sobre `_montar_o_arquivo` | Edital Sans embutida; **único PDF marcado** (`/StructTreeRoot`) | não; o resumo vai ao evento de auditoria |
| Prévia do Edital | `render_edital_pdf` em modo prévia | Edital Sans | não |

Duas regras de spec prendem esses bytes: o FR-1383 da `069` ("o comprovante de inscrição, o
documento de divulgação de resultado e qualquer outro documento composto pelo mesmo escritor MUST
continuar byte a byte o mesmo"), com fixtures em `tests/contract/fixtures/*_v1.pdf`; e o FR-037 da
`008`, que proíbe ao GPS assinatura digital, certificado, ICP-Brasil e carimbo.

**Nada no repositório menciona PDF/A, XMP, OutputIntent ou veraPDF.**

### 1.3 Assinatura, retenção e arquivamento

- **Assinatura digital:** nada lê, valida ou preserva assinatura. Um PDF assinado pelo candidato
  é guardado byte a byte e entregue igual — o que, sem que ninguém tenha decidido isso por esse
  motivo, já é o tratamento correto.
- **Retenção:** não há política nem mecanismo para documentos (B-2 aberto,
  `doc/implantacao-em-producao-ubuntu.md`; MAT-04 e MAT-05 de
  `doc/auditoria-matricula-e-dossie-documental-2026-11-03.md`). O encerramento do Edital existe
  (estados ENCERRADO e CANCELADO, `processos/domain/finalizacao.py`), mas **não há estado de
  arquivamento**.
- **O que a auditoria do dossiê já estabeleceu** (`doc/auditoria-matricula-e-dossie-documental-2026-11-03.md:98-108`):
  pela tabela de temporalidade das IFES (Portaria AN 92/2011), as inscrições de não matriculados
  ficam até a homologação + 1 ano e são **eliminadas**; o assentamento do aluno é de 100 anos;
  recursos e resultados são de **guarda permanente**. O PDF do candidato é **cópia simples** (Dec.
  10.278/2020). O GPS não é SIGAD nem RDC-Arq: conduz e guarda durante o certame e **entrega**.

Esse último ponto é o que mais pesa na recomendação: o documento permanente é, quase sempre,
**um documento que o GPS gera**, e o documento que o candidato envia é, quase sempre, **um
documento destinado à eliminação**.

## 2. O que o PDF/A dá ao GPS, e o que ele não dá

### 2.1 O que a norma e o CONARQ dizem

A **Orientação Técnica nº 4 da CTDE/CONARQ** (out/2016) foi lida na íntegra. O que interessa aqui:

- Cenário de idade corrente e intermediária: os documentos "podem ser produzidos diretamente em
  PDF/A ou em outros formatos e convertidos para PDF/A no momento do arquivamento"; e o sistema que
  guarda documento em tabelas "poderá produzir um PDF/A para apresentar o documento ao usuário ou
  para exportá-lo" a um SIGAD. É exatamente o caso dos atos do GPS.
- Em idade permanente, ao converter, "o documento original (digital ou não digital) deve ser
  mantido".
- **Rec. 1** prefere PDF/A-1; **Rec. 2** manda PDF/A-2 quando houver assinatura PAdES; **Rec. 3**
  manda não converter PDF/A-1 para PDF/A-2 ou 3; **Rec. 5** manda verificar a licença das fontes
  embutidas; **Rec. 6** diz que PDF e PDF/A "não são formatos de preservação de imagens" — para
  digitalizados, o PDF/A é derivada de acesso, e a matriz se preserva; **Rec. 13** manda usar
  validador de conformidade.
- O anexo lembra os níveis: **b** garante a aparência; **u** acrescenta Unicode (o texto se
  extrai e se pesquisa); **a** acrescenta estrutura lógica (acessibilidade).

### 2.2 Ganho concreto

- **Nos documentos gerados:** a família de `render_documento` declara Helvetica sem embutir, e
  cada leitor desenha com a fonte que tiver — foi o defeito ED-14 da auditoria do PDF (o poppler
  desenhava o negrito como regular), corrigido só no Edital. Daqui a vinte anos, "a fonte que o
  leitor tiver" é uma incógnita; com PDF/A, o arquivo carrega a fonte, o espaço de cor e os
  metadados que o descrevem. Esses são os documentos permanentes.
- **Nos documentos recebidos:** o ganho é pequeno. O PDF do candidato abre hoje; o que a conversão
  traria — fonte embutida, script removido — é marginal diante do que ela arrisca (seção 4), e a
  maior parte desses arquivos não chega à idade permanente.

### 2.3 O que PDF/A não é

Não é OCR (um digitalizado convertido continua sem texto — amostra C2), não é acessibilidade (isso
é o nível **a**, ou PDF/UA), não é assinatura e **não prova autenticidade**: o PDF/A de um
documento é outro arquivo, com outro resumo, e a sua relação com o original só existe se for
registrada. A integridade no GPS continua sendo o SHA-256, e a autenticidade, a cadeia de custódia
que ele ancora.

## 3. As três alternativas

| | A — só o original | B — converter e substituir | C — original + derivado |
|---|---|---|---|
| Simplicidade | **máxima**: já é o que existe | média, e perigosa | a mais complexa: vínculo, falha, reprocessamento |
| Integridade | preservada; o resumo continua a âncora | **rompida**: o `content_hash` deixa de corresponder ao que o candidato enviou, e a reconferência da comissão passa a mentir ou a falhar | preservada, se o derivado for registro à parte |
| Autenticidade | preservada | **destruída** para assinados (amostra C4: a assinatura some, e o resultado é PDF/A válido) | preservada no original |
| Preservação de longo prazo | depende do formato de origem | melhor aparência, com perdas silenciosas | a melhor das duas, com custo |
| Custo operacional | nenhum novo | conversão em toda entrada | conversão + validação + dobro de guarda |
| Compatível com o GPS | sim | **não**: contraria o CONARQ, a imutabilidade (trigger e append-only) e a recusa de ler o conteúdo | só fora da requisição, e com decisão de governança |

**B está descartada.** C é a certa **quando houver representação de preservação a produzir** — e a
pergunta passa a ser *quando* e *por quem* (seção 5).

## 4. A prova de conceito

Ghostscript 10.00.0 para converter (PDF/A-2b, `-dPDFACompatibilityPolicy=1`, perfil sRGB),
veraPDF 1.30.4 para validar, pdftoppm/pdftotext para medir fidelidade, pyHanko para a assinatura
de teste. Tudo em contêiner sem rede. Amostras sintéticas — nenhum dado pessoal real — e quatro
PDFs do próprio GPS (Edital composto agora a partir do cenário A da auditoria de 08/10, comprovante
e divulgação das fixtures de contrato, relatório do Edital 61/2026 do estudo de 24/10).

### 4.1 Conversão

| Amostra | Antes (KB) | veraPDF 2b antes | Depois (KB) | ×tamanho | veraPDF 2b depois | Texto extraído igual | Pixels ≠ (72 dpi) | O que se perdeu |
|---|---:|---|---:|---:|---|---:|---:|---|
| C1 textual, Helvetica não embutida | 2 | falha | 13 | 6,6 | **passa** | 100% | 0% | a fonte foi substituída (Nimbus) e congelada |
| C1b textual, fonte embutida | 24 | falha | 17 | 0,7 | **passa** | **83%** | 0,01% | **acentos do texto extraível**: "Declaração" vira "Declara\x01\x02o" |
| C2 digitalizado (JPEG) | 248 | falha | 252 | 1,0 | **passa** | sem texto | 0% | — |
| C3 6 páginas, imagens, transparência | 1.082 | falha | 874 | 0,8 | **passa** | 100% | 0% | — |
| C4 **assinado** (PAdES de teste) | 29 | falha | 17 | 0,6 | **passa** | 83% | 0,01% | **a assinatura**: íntegra e válida antes, campo inexistente depois |
| C5 JavaScript + formulário | 4 | falha | 9 | 2,6 | **passa** | 100% | 0% | script e formulário (o que é o propósito) |
| C6 **senha de abertura** | 3 | ilegível | 5 | — | **passa** | — | — | **o documento inteiro**: saiu uma página em branco |
| C6b restrição de permissões, sem senha | 25 | falha | 16 | 0,7 | **passa** | 83% | 0,01% | a restrição foi ignorada, e os acentos |
| C7 **truncado** | 541 | ilegível | 5 | — | **passa** | — | — | **o documento inteiro**: página em branco |
| C8 alega PDF/A sem ser | 2 | **falha** | 12 | 6,2 | passa | 100% | 0% | — |
| I1 Edital do GPS | 98 | falha | 55 | 0,6 | **passa** | 99,5% | 0,70% | **os 18 links** e o `/Lang`; o texto mudou em detalhes |
| I2 comprovante do GPS | 12 | falha | 25 | 2,2 | passa | 100% | 1,05% | a Helvetica trocada pela Nimbus |
| I3 divulgação do GPS | 26 | falha | 27 | 1,0 | passa | 100% | 0,32% | idem |
| I4 relatório do GPS | 171 | falha | 50 | 0,3 | **passa** | 99,8% | 0,01% | **a marcação** (`Tagged: yes` → `no`), o `/Lang` e os links |

O que a tabela prova:

1. **Conformidade não é fidelidade, e o código de saída não é sucesso.** Para o PDF cifrado e o
   truncado, o Ghostscript **saiu com código 0** e produziu uma página em branco que o veraPDF
   declarou **conforme**. Um fluxo que confiasse em "converteu e validou" guardaria, como
   representação de preservação, uma folha vazia.
2. **A assinatura desaparece sem aviso**, e o resultado é PDF/A válido. Converter assinado é
   sempre perder a assinatura — confirmado pela literatura (a conversão reescreve objetos, e a
   atualização incremental não a salva).
3. **A degradação do texto passa no nível b.** A C1b e a C4 continuam idênticas ao olho (0,01% de
   pixels) e perderam o mapeamento Unicode dos acentos. O nível **u** pegaria: validado em 2u, o
   Edital convertido falhou justamente na regra 6.2.11.7.2 (mapa para Unicode). Quem converter
   documento de texto deve exigir 2u, e não 2b.
4. **A conversão tira dos documentos do GPS o que o GPS pôs de propósito**: os links internos do
   Edital (anotações sem a marca de impressão são descartadas), o idioma declarado e a estrutura
   lógica do relatório — o único PDF marcado do sistema sai sem marcação.
5. **"Já é PDF/A" não se lê no arquivo**: a C8 declara `pdfaid:part=2` e não é. A Rec. 3 do CONARQ
   (não reconverter PDF/A) só se aplica a PDF/A **validado**.
6. **A saída não é determinística**, nem com `SOURCE_DATE_EPOCH`: duas conversões do mesmo
   arquivo deram bytes diferentes. O resumo do derivado tem de ser **gravado**, e o
   reprocessamento é idempotente pelo registro ("existe derivado válido para este original com
   esta versão da ferramenta"), e não pela igualdade de bytes.
7. **Custo:** o Ghostscript leva 30–50 ms num documento comum e **0,42 s** num digitalizado de 20
   páginas a 300 dpi (24,6 MB, tamanho inalterado — o JPEG passa direto). O veraPDF valida em
   milissegundos, mas **a partida da JVM leva ~10,7 s**: validação só faz sentido em lote. Tamanho:
   de 0,3× a 6,6× — arquivo pequeno cresce pelo perfil ICC e pela fonte embutida (~10 KB fixos);
   digitalizado fica igual.
8. **Segurança da ferramenta:** sob `-dSAFER`, o Ghostscript só funcionou depois de autorizar
   explicitamente a leitura do perfil ICC e da definição PDF/A; com o arquivo de definição da
   própria distribuição, ele aborta o PDF/A e sai com código 0. O Ghostscript interpreta conteúdo
   não confiável e tem histórico de falhas de execução de código (CVE-2023-36664, CVE-2024-29510):
   em produção ele exigiria isolamento próprio — usuário sem privilégio, sem rede, sem acesso ao
   resto da raiz de arquivos —, que hoje não existe na VM.

### 4.2 Geração direta

Os originais do GPS descumprem, no veraPDF 2b, só estas regras:

| Regra (ISO 19005-2) | O que falta | Edital | Relatório | Comprovante e divulgação |
|---|---|:-:|:-:|:-:|
| 6.1.3-1 | `/ID` no trailer | ✗ | ✗ | ✗ |
| 6.6.2.1-1 | metadados XMP no catálogo | ✗ | ✗ | ✗ |
| 6.2.4.3-2 e -4 | espaço de cor independente (OutputIntent) para `DeviceRGB`/`DeviceGray` | ✗ | ✗ | ✗ |
| 6.3.2-1 | `/F` (imprimível) nas anotações de link | ✗ | ✗ | — |
| 6.2.11.4.1-1 | fonte embutida | — | — | ✗ |

`direto.py` acrescentou aos PDFs do GPS exatamente isso — `/ID` derivado do conteúdo, XMP com
`pdfaid`, OutputIntent sRGB e `/F 4` nos links —, sem tocar no conteúdo das páginas:

| Arquivo | Resultado no veraPDF |
|---|---|
| Edital + 4 acréscimos | **passa em PDF/A-2b, 2u e 1b** |
| Relatório + 4 acréscimos | **passa em PDF/A-2u e 2a** (a marcação que a `diagramacao` já faz basta ao nível a) |
| Comprovante + 4 acréscimos | falha só em 6.2.11.4.1 — a Helvetica não embutida |

Os links, o idioma, os marcadores e a marcação ficam — tudo o que a conversão destruiu. E o
resultado continua determinístico: `/ID` derivado dos bytes e XMP sem data mantêm a promessa de
"mesmo conteúdo, mesmos bytes".

## 5. Recomendação

**Adotar seletivamente.**

### 5.1 Documentos gerados pelo GPS: gerar em PDF/A — sim, agora

- **Nível: PDF/A-2u**, com 2b como piso. 2u porque garante o texto pesquisável, que é o que um
  Edital de vinte anos atrás precisa ter, e o Edital e o relatório já passam. PDF/A-2 e não 1,
  contra a Rec. 1 do CONARQ, pela Rec. 2: se a instituição vier a assinar o PDF publicado com
  certificado ICP-Brasil, fora do GPS, é o PDF/A-2 que aceita PAdES — e o custo de um ou de outro,
  aqui, é o mesmo. O relatório pode declarar 2a, porque já é marcado.
- **Sem dependência de execução nova.** Os quatro acréscimos são objetos que o escritor próprio
  escreve: um `/ID` derivado do resumo do conteúdo, um XMP estático por tipo de documento, um
  OutputIntent com um perfil sRGB versionado no repositório (o da POC veio com o Ghostscript;
  para versionar, escolher um perfil sRGB de licença explícita para redistribuição, e registrar a
  origem e o resumo como `fontes/ORIGEM.md` faz com a Edital Sans), e `/F 4` nas
  anotações. A família de `render_documento` passa a embutir a Edital Sans, que já está no
  repositório sob a OFL — a Rec. 5 (licença da fonte) está atendida.
- **Validação no CI, e não em produção.** Um job com a imagem do veraPDF valida um exemplar de
  cada tipo de documento a cada mudança no escritor, como o grupo `navegador` roda o Playwright.
  Produção não ganha Java.
- **Só para documentos novos.** O que já foi publicado está em tabela append-only e não muda — nem
  deve: é o ato. Edital publicado antes do corte continua o arquivo que foi.
- **Duas decisões de governança, que são do usuário e não deste estudo:**
  - o **FR-1383** da `069` prende o comprovante e a divulgação "byte a byte". Mudar o escritor
    deles é emendá-lo, com fixtures `_v2` e uma regra para o comprovante já emitido, que é
    regenerado a cada download e cujo resumo foi prometido ao candidato (manter o escritor antigo
    para inscrições anteriores ao corte, ou aceitar que o resumo mude e dizê-lo);
  - a **ordem**: o Edital e o relatório custam quatro acréscimos e nenhum byte de compromisso
    antigo; o comprovante e a divulgação custam a emenda. Os primeiros podem ir antes.

### 5.2 Documentos recebidos: manter o original — e não converter durante o certame

- **Alternativa A, reforçada no que é barato.** O GPS já grava o SHA-256 de tudo e reconfere na
  entrega à comissão. Falta a **conferência periódica de fixidez**: hoje é o roteiro manual
  `ps-conferir-documentos` (`doc/implantacao-em-producao-ubuntu.md`). Vale transformá-lo num
  comando com timer, no padrão do `despachar_avisos`, que registre divergência — é a medida de
  preservação de maior retorno e menor custo deste estudo, e não tem nada a ver com formato.
- **Não converter na entrada.** Pesa contra: a recusa declarada de ler o conteúdo; a ausência de
  fila; o risco de segurança de interpretar PDF de terceiros no servidor; o custo de guardar dados
  pessoais em dobro (o derivado é mais uma cópia a reter, eliminar e salvar em backup); e,
  sobretudo, que **a maioria desses arquivos será eliminada** um ano depois da homologação.
- **A representação de preservação pertence à destinação.** Quando o B-2 for decidido e houver
  destino para o assentamento (SIGAA, acervo, um RDC-Arq), o GPS entrega um **pacote**: os
  originais, os resumos, a relação entre eles e o ato a que pertencem. Se a normalização para PDF/A
  for exigida, é provável que o repositório arquivístico a faça (normalização na admissão é função
  típica de RDC-Arq). **Antes de projetar qualquer conversão no GPS, convém perguntar ao Arquivo
  do Ifes o que ele recebe.**

### 5.3 Se um dia o GPS converter (alternativa C), os portões mínimos

Aprendidos na POC, e não negociáveis:

1. **Nunca converte assinado** (campo `/Sig` ou `/ByteRange`), **nunca converte cifrado**, nunca
   substitui o original.
2. **Valida em 2u**, e não em 2b, para documento com texto.
3. **Confere fidelidade além da conformidade:** mesmo número de páginas; nenhuma página em branco
   onde o original tinha conteúdo; texto extraído equivalente; diferença de pixels abaixo de um
   teto, página a página.
4. Conformidade + fidelidade aprovadas → derivado registrado com resumo próprio, versão da
   ferramenta e vínculo ao resumo do original; reprovadas → registro da recusa e o original
   continua sendo o documento. Falha nunca bloqueia nada do candidato.
5. Em lote, fora da requisição, por comando com timer, com o Ghostscript isolado (`-dSAFER`,
   sem rede, usuário próprio) e o veraPDF numa única JVM por lote.

## 6. Arquitetura mínima

```
Gerados (agora)                                  Recebidos (sem mudança no fluxo)
───────────────                                  ─────────────────────────────────
composição ─► escritor próprio                   upload ─► aceitar (PDF? cabe?)
              + /ID do conteúdo                         ─► SHA-256 ─► disco privado
              + XMP pdfaid 2u                           ─► (nada mais)
              + OutputIntent sRGB versionado
              + /F 4 nos links                   timer: conferir_fixidez
              + fonte embutida em todos                 ─► recalcula SHA-256, registra divergência
          ─► bytes determinísticos
          ─► tabela append-only (como hoje)      destinação (quando o B-2 existir)
                                                        ─► pacote: originais + resumos + vínculos
CI: veraPDF valida um exemplar de cada tipo             ─► normalização, se houver, no destino
```

Nenhuma tabela nova, nenhum campo na interface do candidato, nenhuma etapa a mais. O GPS não vira
GED.

## 7. Complexidade, impactos e riscos

| Frente | Tamanho | Toca | Risco principal |
|---|---|---|---|
| PDF/A no Edital, Retificação e relatórios | pequeno | `pdf.py` (`_montar_o_arquivo`, `_arquivo_do_edital`, anotações), `diagramacao.py`, um perfil ICC versionado, job de CI | regenerar as fixtures do Edital publicado; testes que prendem bytes |
| PDF/A no comprovante e na família da divulgação | médio | `render_documento`, fixtures `_v1`, emenda do FR-1383 | o resumo já prometido do comprovante; medir de novo a composição com outra fonte (larguras mudam, linhas podem quebrar em outro lugar) |
| Conferência periódica de fixidez | pequeno | um comando, um timer documentado | ruído: arquivo de rascunho apagado legitimamente não é divergência |
| Pacote de destinação | grande, e **depende do B-2** | — | decidir antes do Arquivo do Ifes |
| Conversão dos recebidos no GPS | grande | fila ou lote, isolamento do Ghostscript, Java em produção, tabela de derivados | as perdas silenciosas da seção 4; dado pessoal em dobro; superfície de ataque |

## 8. Proposta enxuta de especificação

Há justificativa para **uma** spec, e só a dos documentos gerados. O esboço abaixo é o que este
estudo propôs; a spec que dele saiu é a [`178`](../specs/178-documentos-em-pdfa/spec.md), e onde as
duas divergem vale a spec — ela decidiu, entre outras coisas, que o comprovante das inscrições já
enviadas continua no escritor de hoje, byte a byte, e reviu o FR-1383 da `069` com a redação
anterior preservada.

> **Documentos institucionais em PDF/A.** Todo PDF composto pelo GPS e gravado como ato, a partir
> da data de corte, é arquivo PDF/A-2u conforme, verificado pelo veraPDF no CI. A conformidade não
> muda o que o documento diz nem como se apresenta: os links, o idioma, os marcadores e a marcação
> lógica permanecem; o arquivo continua determinístico; os atos publicados antes do corte não
> mudam.
>
> - Requisitos: identificação do arquivo derivada do conteúdo; metadados XMP declarando a parte e
>   o nível; perfil de cor de saída sRGB versionado; anotações imprimíveis; fonte embutida em todo
>   documento composto.
> - Fora do escopo: assinatura digital (FR-037 da `008` continua valendo), documentos recebidos,
>   conversão de qualquer arquivo existente, PDF/UA.
> - Decisões a tomar na spec: a emenda do FR-1383 e o que acontece com o comprovante de
>   inscrição enviada antes do corte; se a prévia também declara PDF/A (sugestão: não — a prévia
>   não é ato).
> - Critério de sucesso: um exemplar de cada tipo passa no veraPDF em 2u no CI; o mesmo conteúdo
>   gera os mesmos bytes; nenhuma diferença visual nos documentos do Edital e do relatório além
>   dos metadados.

A conferência periódica de fixidez é pequena demais para spec própria — cabe como tarefa de
operação. O pacote de destinação espera o B-2.

## Fontes

- CONARQ/CTDE, [Orientação Técnica nº 4 — Recomendações de uso do PDF/A para Documentos Arquivísticos](https://www.gov.br/conarq/pt-br/assuntos/camaras-tecnicas-setoriais-inativas/camara-tecnica-de-documentos-eletronicos-ctde/Orientacao_tecnica_4.pdf) (out/2016) — lida na íntegra.
- PDF Tools, [How to convert signed documents to PDF/A?](https://www.pdf-tools.com/pdf-knowledge/how-convert-signed-documents-pdfa) — por que a conversão invalida a assinatura.
- Bugzilla do Ghostscript: [692588](https://bugs.ghostscript.com/show_bug.cgi?id=692588) (rasterização de marca-d'água), [703591](https://bugs.ghostscript.com/show_bug.cgi?id=703591) (espaços inseridos em texto de OCR), [707450](https://bugs.ghostscript.com/show_bug.cgi?id=707450) (falha de conformidade de cor no veraPDF).
- veraPDF 1.30.4, imagem oficial `verapdf/cli` — perfis PDF/A-1b, 2a, 2b e 2u.
- No repositório: `doc/auditoria-matricula-e-dossie-documental-2026-11-03.md` (temporalidade,
  Dec. 10.278/2020, o GPS não é SIGAD), `doc/implantacao-em-producao-ubuntu.md` (timers, B-2,
  conferência de documentos), `specs/069-edital-linguagem-simples/spec.md` (FR-1383),
  `specs/008-composicao-institucional/spec.md` (FR-037).
