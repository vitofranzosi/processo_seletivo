# Auditoria e evolução visual dos e-mails do GPS — 13/11/2026

Pedido do usuário: inventariar todo envio de e-mail, propor um padrão visual pequeno e institucional,
melhorar a apresentação dos e-mails ativos **sem mudar regra, destinatário, gatilho nem significado**,
e entregar a prova. **Sem spec nova**, por pedido explícito ("não quero uma grande especificação de
arquitetura"): nenhum `FR-`/`SC-` foi criado, e os testes novos citam só os que já existem.

A galeria está em [`galeria-dos-emails/depois/index.html`](galeria-dos-emails/depois/index.html) — abre
direto do disco —, e o "antes" em [`galeria-dos-emails/antes/`](galeria-dos-emails/antes/).

---

## A. Inventário

**Quatro módulos enviam, e são cinco situações** — a mesma contagem que
`tests/test_situacoes_de_mensagem.py` já asseverava (FR-084 da `010`, revista pela `019`, `066` e
`134`). A varredura confirmou que nada mais envia:

- nenhuma chamada a `send_mail`, `EmailMessage` ou `EmailMultiAlternatives` fora dos quatro módulos;
- nenhum `mail_admins`, `ADMINS` ou `AdminEmailHandler` no `LOGGING`;
- nenhum `django.contrib.admin`, nenhum fluxo de redefinição de senha (o portal não tem senha), nenhuma
  biblioteca de terceiro que envie (sem `allauth`, sem fila, sem Celery);
- nenhum `smtplib`, `sendmail` ou `msmtp` em scripts e na implantação — os achados do `grep` são testes
  e documentação.

| # | Mensagem | Para | Gatilho | Implementação | Assunto (atual) | Formato antes → depois | Prioridade |
|---|---|---|---|---|---|---|---|
| 1 | Código de acesso | Quem pede para entrar | Pede código na tela de acesso | `identidade/application/mensagem.py` · `enviar_codigo` ← `portal/views.py` (3 chamadas) | Seu código de acesso — Seleções ‹rótulo› | texto → **multipart** | Alta (toda entrada) |
| 2 | Código para acrescentar e-mail | Dono do endereço informado | Acrescenta credencial na conta | idem, `finalidade=ADICIONAR_CREDENCIAL` | Confirme este e-mail — Seleções ‹rótulo› | texto → **multipart** | Média |
| 3 | Mudança no acesso à conta | E-mail principal da conta | Credencial acrescentada ou removida | idem · `avisar_mudanca_de_credencial` ← `portal/views.py` (2) | Mudança no acesso à sua conta — Seleções ‹rótulo› | texto → **multipart** | Média (segurança) |
| 4 | Confirmação de inscrição | Quem enviou a inscrição | Envio da inscrição, depois do commit | `inscricoes/application/mensagem.py` · `enviar_comprovante` ← `portal/views.py::_confirmar_por_email` | Inscrição recebida — ‹protocolo› | texto → **multipart** | Alta |
| 5 | Convocação | Convocado, quando o Edital comunica por mensagem | Comissão comunica a convocação (gesto ou lote) | `convocacao/application/comunicar.py` · modelos `convocacao/mensagem/inicial.*` | ‹Ifes› · Convocação no Edital N: envie seus documentos até dd/mm | multipart → multipart, **restilizado** | Alta |
| 6 | Correção da convocação | Convocado | Convocação sucedida e comunicada de novo | idem · `correcao.*` | ‹Ifes› · Convocação corrigida no Edital N: prazo válido até dd/mm | multipart → multipart, **restilizado** | Alta |
| 7 | Aviso complementar (066) | Pessoas da publicação | Operador confirma; `despachar_avisos` envia (timer) | `avisos/application/despacho.py`; texto da unidade, congelado | o do modelo da unidade (inicial: "Processo Seletivo Ifes — Nova publicação disponível") | texto → **multipart** | Média |
| 8 | Aviso de pendência documental (134) | Convocado com documento a revisar | Quem confere pede o aviso; o despacho envia | idem; texto de `avisos/domain/pendencia.py` | Ifes · Edital N: há documento da sua convocação para revisar | texto → **multipart** | Alta (ação) |

**Duplicações e inconsistências encontradas** (todas de apresentação, todas resolvidas):

- **Três estilos de composição**: constantes `str.format` em Python (1–4), modelos de arquivo (5–6) e
  texto congelado no banco (7–8). Os de 1–4 passaram a modelos, como os da convocação.
- **Três rodapés escritos à mão**, iguais por coincidência: "‹assinatura› — Seleções / Esta mensagem é
  automática; não responda." em quatro lugares. Agora é um bloco da moldura (1–4) e continua no texto
  congelado (7–8), que não se reescreve.
- **Quebra fixa de linha** na confirmação de inscrição ("são\nfeitas") — palavra solta no celular. A
  `066` já tinha corrigido isso nos avisos; o comprovante passou a um parágrafo por linha.
- **Só a convocação tinha HTML**, e sem estilo nenhum (atributos de apresentação puros): o prazo num
  `bgcolor`, o link como texto sublinhado padrão, nenhuma largura fluida.
- **Nenhum modelo abandonado**: `portal/acesso_email.html` e `portal/_mensagens.html` são páginas, não
  e-mails.

## B. Diagnóstico de UX

Lendo como um candidato com pouca familiaridade digital, no celular:

1. **Nada dizia "isto é do Ifes" à primeira vista.** Nos e-mails de texto, a instituição só aparecia no
   rodapé. Uma mensagem com código de seis dígitos e sem identidade visual é, para muita gente,
   indistinguível de phishing.
2. **O código de acesso se perdia no corpo.** Recuado com quatro espaços num texto proporcional, sem
   tamanho nem espaçamento — e é o único dado que a pessoa precisa copiar.
3. **O protocolo da inscrição** — "o que a página manda guardar" — vinha no meio de seis linhas de
   metadados de mesmo peso.
4. **A ação não tinha forma de ação.** Todo destino era uma URL longa por extenso; na convocação, um
   link sublinhado num parágrafo. Em nenhuma mensagem havia um alvo de toque claro.
5. **O prazo da convocação competia com o resto.** Estava num fundo azulado (`#eef3f8`) sem relação com
   a paleta do produto, sem rótulo, e logo antes de outro bloco de mesmo peso.
6. **Os rodapés de valor jurídico pareciam letra miúda.** "Este aviso não substitui a publicação" e
   "Este aviso não é a convocação e não altera o seu prazo" vinham depois de um "—", na mesma
   aparência da assinatura.
7. **Linguagem**: em geral boa — curta, sem jargão, e a regra "o HTML não diz o que o texto não diz"
   já existia na convocação. Os pontos fracos estão em *Achados*, abaixo, porque mexer neles é mexer em
   texto fixado por spec ou por decisão do usuário.

## C. O padrão visual

Implementado em `backend/processo_seletivo/shared/correio.py` e
`backend/processo_seletivo/shared/templates/correio/`, onde fica também o mapa de estilos
(`estilos.json`). Pequeno de propósito: **uma moldura, um botão,
seis estados e ~35 classes**.

**Moldura.** Faixa verde-escura de 6 px no topo; cabeçalho em texto — "Instituto Federal do Espírito
Santo" e "‹Unidade› · Seleções"; cartão branco de até 600 px, fluido no celular; rodapé com a
assinatura da unidade e "Esta mensagem é automática; não responda.".

**Sem logomarca.** Decisão, não omissão: a FR-3886 da `121` proíbe imagem e `src=` na convocação;
imagem é bloqueada por padrão no Outlook e em muitos Gmails corporativos, e viraria um retângulo
vazio no topo; e uma logo hospedada seria um endereço externo — exatamente o que o pedido recusa.

**Multiunidade.** O cabeçalho e a assinatura vêm de `unidades.application.identificacao` (109), nunca
escritos: "Cefor · Seleções" com uma unidade; só "Seleções" e a assinatura "Ifes" quando a implantação
tem várias, ou quando a mensagem é da conta e não de uma unidade. Nos avisos, a unidade sai da própria
assinatura congelada — o despacho não faz consulta a mais por mensagem.

**Tokens.** Os de `shared/static/shared/tokens.css`, copiados porque e-mail não lê folha: verde
`#15803d` (botão), verde de texto `#146c37`, verde-escuro `#0b5a2a` (faixa), âmbar `#8a5300` /
`#fdf5e5`, texto `#1c1c1c`, fraco `#555`, bordas `#d4d4d4`. Todos acima de 4,5:1 sobre o fundo em que
aparecem. Fonte do sistema (`Segoe UI`, Roboto, Helvetica, Arial); código em `Consolas`/`Courier New`.
Corpo 16 px, título 22 px.

**Seis estados**, distinguidos por uma borda esquerda de 4 px e um fundo claro no quadro de destaque —
e pelo título. A cor nunca é o único portador do sentido:

| Estado | Borda / fundo | Usado em |
|---|---|---|
| Informação | verde-escuro / cinza-esverdeado | código, mudança de credencial, aviso 066, quadro "esta substitui a anterior" |
| Ação | verde / verde-claro | (reservado ao botão) |
| Prazo | âmbar / âmbar-claro | prazo da convocação e da correção |
| Confirmação | verde-texto / verde-claro | protocolo da inscrição |
| Pendência | âmbar / âmbar-claro | aviso de pendência; "se não foi você" |
| Desfavorável | ardósia / cinza | **nenhum e-mail hoje** — reservado ao aviso de desfecho da `156`; ardósia e não vermelho, porque resultado ruim pede cuidado, não alarme |

**Ação principal.** Um botão por mensagem, no máximo, com verbo que diz o destino ("Acessar minha
convocação", "Rever minha inscrição", "Abrir minha convocação", "Entrar na área do candidato"), e o
endereço por extenso, em cinza, logo abaixo — para quem tem o link bloqueado ou usa leitor de tela.
O código de acesso **não** tem botão nem link (P-001 da `010`: nenhum link autentica).

**Preheader.** Uma frase da própria mensagem, que aparece ao lado do assunto na caixa de entrada: o
prazo na convocação, o protocolo na inscrição, a validade no código. **Nunca o código**, que apareceria
na tela bloqueada do celular.

**Compatibilidade.** Tabelas de apresentação, estilo em linha, atributos `bgcolor`/`width` para o
Outlook do Windows, tabela de 600 px entre comentários condicionais `<!--[if mso]>` (o Outlook não lê
`max-width`), `<meta name="color-scheme" content="light">`, cores sólidas que a inversão dos modos
escuros preserva, nenhuma imagem, fonte externa, script ou rastreio.

### Como o estilo chega à mensagem — a decisão de arquitetura

A guarda da política de conteúdo (`tests/interface/test_politica_de_conteudo.py`, FR-2097) recusa
`style=""` e `<style>` em **todo** `.html` do repositório; e o cliente de e-mail só respeita estilo em
linha. Em vez de abrir exceção na guarda, os modelos de mensagem escrevem `class="..."` e
`correio.estilizar()` troca cada classe pela declaração dela depois de renderizar. Classe sem regra é
`ValueError`, e um teste confere que toda classe citada em modelo de mensagem tem estilo — o par, para
o e-mail, da regra "classe no template exige regra na folha".

**A convocação não herda a moldura**, e repete a estrutura dela: o resumo gravado em cada comunicação
(FR-3889, `identificacao_do_modelo`) é o dos dois arquivos dela e do mapa de estilos, e uma moldura
herdada mudaria palavras que saíram sem mudar o resumo. **O mapa de estilos é um arquivo versionado**
(`shared/templates/correio/estilos.json`), e não um dicionário em Python, justamente para entrar no
resumo e se reconstituir pelo Git (achado 6).

**Os avisos 066/134 ganham a forma HTML na hora do envio**, a partir do texto congelado e só dele:
parágrafos, listas (`- `), o endereço final de parágrafo que leva a uma página conhecida do portal vira
botão com rótulo **da rota** (não do texto da unidade), e o rodapé do sistema vira um quadro. O texto
puro continua sendo o corpo e o registro. Se a forma HTML falhar, a mensagem sai **só com o texto**,
como antes, e a tentativa é registrada pelo resultado do envio — nunca como falha de preparação.

## D. Antes e depois

Os três representativos pedidos — convocação (5), providência (8) e confirmação (4) — mais os demais,
estão na galeria com HTML, texto puro, `.eml` e captura em 600 e 375 px. Em resumo:

- **Convocação.** Antes: HTML sem estilo, prazo em azul genérico, link sublinhado. Depois: título,
  processo como subtítulo, o que a convocação pede, **prazo em quadro âmbar rotulado**, botão "Acessar
  minha convocação" com o endereço abaixo, "como entrar", a ressalva em tom secundário, e o quadro de
  segurança com borda. **Três frases mudaram**, a pedido do usuário depois da primeira versão: "que
  enviaremos numa mensagem separada" (achado 1), e o título e o rodapé sem masculino genérico (achado
  5). O teste frase a frase da SC-1159 continua verde.
- **Pendência documental.** Antes: texto com a URL inteira no meio da frase e o rodapé com cara de
  assinatura. Depois: a lista de documentos como lista, o botão "Abrir minha convocação", o prazo, e
  "Este aviso não é a convocação e não altera o seu prazo" num quadro âmbar. Mesmo texto puro, byte a byte.
- **Confirmação de inscrição.** Antes: seis linhas de mesmo peso. Depois: protocolo e código de
  verificação em quadro de confirmação, os dados numa tabela de duas colunas, a lista de documentos,
  a ressalva "receber não é deferir", e o botão "Rever minha inscrição".

Casos-limite na galeria: título de 300 caracteres, inscrição sem documento, seis documentos com nomes
longos, convocação sem vencimento, implantação com várias unidades, pendência de um documento só.

## E. Implementação

| Arquivo | O que mudou |
|---|---|
| `shared/correio.py` (novo) | tokens, `estilizar`, `compor`, `moldura`, blocos do aviso, `html_do_aviso` |
| `shared/templates/correio/base.html`, `_botao.html`, `aviso.html` (novos) | moldura, botão, aviso em blocos |
| `identidade/templates/identidade/mensagem/{codigo,vinculo,mudanca}.{txt,html}` (novos) | o texto que era constante em Python, e o HTML |
| `identidade/application/mensagem.py` | compõe pelos modelos e envia `html_message`; destinatário, gatilho e falha silenciosa iguais |
| `inscricoes/templates/inscricoes/mensagem/comprovante.{txt,html}` (novos) | idem |
| `inscricoes/application/mensagem.py` | idem; envio continua depois do commit e fora da transação |
| `convocacao/templates/convocacao/mensagem/{inicial,correcao}.{html,txt}` | apresentação; e "que enviaremos", no lugar de "que enviamos", na frase de como entrar |
| `convocacao/application/comunicar.py` | `_renderizar` aplica `correio.estilizar` — envio e conferência pela mesma composição |
| `avisos/application/despacho.py` | `EmailMultiAlternatives` com a forma HTML; recaída no texto puro |
| `scripts/galeria_dos_emails.py` (novo) | a galeria, sem banco e sem enviar |

**Textos alterados**, todos fora de texto fixado por spec:

- código e vínculo: acrescentada "Digite-o na tela em que você o pediu." — diz **onde** a ação se faz;
- comprovante: "acesse\n‹endereço›\ne entre com este e-mail — enviamos…" virou "acesse:\n‹endereço›" e
  "Entre com este e-mail: enviamos um código de acesso a cada entrada, e não há senha."; e um parágrafo
  por linha.

**Cabeçalho `Auto-Submitted: auto-generated` em toda mensagem** (RFC 3834). Era só dos avisos; agora
o código, o vínculo, a mudança de credencial, o comprovante e a convocação também se declaram
automáticos, e a resposta de férias de quem recebe não volta para uma caixa que ninguém lê. A constante
mora em `shared/correio.py` (`CABECALHOS`), e a dos avisos passou a apontar para ela. Para levar
cabeçalho, identidade e inscrição trocaram `send_mail` por `EmailMultiAlternatives`, numa função
`entregar` por módulo — os seis testes que simulavam a queda do correio trocando `send_mail` passaram a
trocar `entregar`. Era o achado 2 da primeira versão deste relatório, corrigido a pedido do usuário.

**Não mudou**: destinatários, remetente, cópias, gatilhos, idempotência, ordem reservar–enviar–gravar
da convocação, contagem de situações da FR-084, tokens, nenhuma migration e nenhuma dependência nova.

**Testes novos**:

- `tests/unit/test_apresentacao_dos_emails.py` (81 casos, sem banco): para 13 composições, o HTML não
  diz nada que o texto e o assunto não digam, além da moldura e do rótulo do botão; nenhuma classe
  sobrando, script, imagem, `src=`, folha ou fonte; todo `href` é do portal ou o `mailto:` do canal, e
  está no texto; o código não tem link e não vai ao preheader; o nome de arquivo hostil sai escapado;
  a implantação com várias unidades não escolhe uma; os blocos do aviso; toda classe de modelo tem estilo.
- `tests/integration/avisos/test_despacho_em_html.py`: o despacho anexa a forma HTML, mantém um
  destinatário, `Auto-Submitted` e o texto congelado; sem a forma HTML, os dois avisos saem e são `ACEITA`.
- `tests/integration/test_envios_em_duas_partes.py`: código, vínculo, mudança e comprovante saem uma
  vez, ao mesmo destinatário, com texto, HTML e `Auto-Submitted`; a convocação também leva o
  cabeçalho; sem destinatário, nada sai.

## F. Cobertura

| # | Mensagem | Situação |
|---|---|---|
| 1 | Código de acesso | **Modernizado** |
| 2 | Código para acrescentar e-mail | **Modernizado** |
| 3 | Mudança no acesso à conta | **Modernizado** |
| 4 | Confirmação de inscrição | **Modernizado** |
| 5 | Convocação | **Modernizado** (apresentação; texto fixado pela `121`/`156`) |
| 6 | Correção da convocação | **Modernizado** (idem) |
| 7 | Aviso complementar 066 | **Modernizado** (forma HTML do texto congelado; o texto é da unidade) |
| 8 | Aviso de pendência 134 | **Modernizado** (idem; o texto é da 3ª decisão de 08/11) |
| — | Aviso do desfecho (`156`) | **Não existe ainda** — a spec o deixa para depois; o estado "desfavorável" está pronto para ele |
| — | E-mails de biblioteca ou de sistema | **Nenhum** |
| — | Legados | **Nenhum** modelo ou fluxo abandonado |

### O que não foi verificado

- **Clientes reais.** Nada foi enviado. A renderização foi conferida no navegador (600 e 375 px, sem
  rolagem horizontal) e estruturalmente pelos testes. Os `.eml` da galeria abrem no Apple Mail, Outlook
  e Thunderbird sem envio — **é o próximo passo antes de produção**, sobretudo o Outlook do Windows e o
  Gmail com imagens bloqueadas e modo escuro.

## Achados — registrados, não corrigidos

Fora do escopo de apresentação, ou fixados por spec/decisão; a decisão é do usuário.

1. ~~**"o código de seis dígitos que enviamos numa mensagem separada"**~~ **Corrigido em 13/11**, a
   pedido do usuário: "que enviaremos numa mensagem separada", na inicial e na correção, texto e HTML.
   O código só sai quando a pessoa o pede, e o passado mandava procurar na caixa um código que ainda
   não existe. A FR-3883 da `121` fixa só *"numa mensagem separada"*, e a spec não precisou mudar. O
   resumo do modelo (FR-3889) muda para os envios seguintes, e não para os já gravados.
   `test_o_codigo_de_entrada_e_futuro_e_nao_ja_enviado` prende a forma nova.
2. ~~**`Auto-Submitted: auto-generated` só nos avisos.**~~ **Corrigido em 13/11**, a pedido do
   usuário: toda mensagem do GPS leva o cabeçalho (seção E).
3. ~~**"quem o tiver poderá entrar na conta dele"**~~ **Corrigido em 13/11**, a pedido do usuário:
   *"quem o tiver poderá usar este endereço para entrar na própria conta"*, num parágrafo por linha.
   O teste que prendia a forma antiga prende a nova.
4. ~~**O assunto da pendência é singular com vários documentos**~~ **Corrigido em 13/11**, a pedido
   do usuário: com dois ou mais, *"há documentos da sua convocação para revisar"*, o número que o corpo
   já concordava. A FR-4613 da `134` fixava o assunto literalmente e foi revista, com a redação
   anterior preservada. Vale para os avisos gravados daqui em diante: o texto congelado dos já
   gravados não se reescreve.
5. ~~**"Você foi convocado"** em masculino genérico~~ **Corrigido em 13/11**, a pedido do usuário: o
   título diz *"Você tem uma convocação no Edital ‹NN/AAAA›"*, e o rodapé, *"porque tem uma
   convocação num processo seletivo"*. A FR-3883 da `121` citava o título literalmente e foi revista,
   com a redação anterior anotada ao lado. `test_a_mensagem_nao_presume_o_genero_de_quem_le` varre os
   treze e-mails da composição.
7. ~~**A página da convocação no portal diz "Você foi convocado!"**~~ **Corrigido em 13/11**, a
   pedido do usuário: o título da chamada aberta com providência pendente é *"Você tem uma
   convocação!"* (`portal/obrigacoes.py`, `TITULO_ABERTA`), como o e-mail. A norma foi revista onde
   ela mora — a FR-6202 e a tabela de títulos da `154`, a tabela e os acréscimos da `121`, o cenário K
   da `125` —, com a redação anterior anotada; os cenários narrados e os registros históricos das três
   specs continuam citando o título antigo, que era o vigente quando foram escritos.
8. ~~**Ainda há masculino genérico em três frases do portal**~~ **Corrigido em 13/11**, a pedido do
   usuário, junto com outras quatro frases dirigidas ao candidato que a varredura achou:

   | Onde | Antes | Agora |
   |---|---|---|
   | `portal/selecao.html` | Se for convocado, a convocação pedirá também: | A convocação, se houver, pedirá também: |
   | `portal/selecao.html` | Se concorrer em ‹X› e for convocado, a convocação pedirá também: | Para quem concorre em ‹X›, a convocação, se houver, pedirá também: |
   | `portal/requerimento.html` | Você foi convocado e pode conferir o que enviou. | Você tem uma convocação e pode conferir o que enviou. |
   | `portal/_convocacoes_da_selecao.html` | Foi convocado? … Estar convocado não é… | Tem uma convocação? … Ter uma convocação não é… |
   | `requerimentos/application/preencher.py` | …ficará disponível quando você for convocado. | …ficará disponível na sua convocação. |
   | `requerimentos/application/selectors.py` | …pede o Requerimento de Matrícula quando você for convocado. | …pede o Requerimento de Matrícula na convocação. |
   | idem | Se algo mudar e você for convocado, esta página… | Se algo mudar e houver convocação, esta página… |
   | `duvidas/domain/respostas.py` (assistente) | Se você for convocado, a convocação pedirá também: | Se houver convocação, ela pedirá também: |

   A FR-3752 da `118` citava a frase do Requerimento enviado e foi revista, com a anterior anotada.
   `tests/portal/test_sem_masculino_generico.py` varre as telas do portal e os quatro módulos cujo
   texto chega a elas.
9. **O masculino genérico que ficou** é de outra natureza, e é decisão de quem responde pelos atos:
   - **nomes e colunas de atos oficiais** publicados no portal: *"Publicação de convocados"* (`149`),
     a coluna *"Candidato"* das listas públicas (`publicacao_das_inscricoes.html`,
     `relacao_de_habilitados.html`, `resultado.html`, `comprovante.html`), *"N candidato habilitado"*
     (`_lista_do_sorteio.html`) e *"cada candidato consulta a própria situação"*;
   - **o texto do Edital** — *"quando o candidato for convocado"* (`interface/revisao.py`,
     `duvidas/domain/rotulos.py`) —, que é o ato legal (PDF) e se revê por Retificação, não por código;
   - **a gestão** — *"quem foi convocado"* —, que fala da pessoa em terceira pessoa a quem conduz o
     certame, e não a ela;
   - *"área do candidato"*, nome da área no portal.
6. ~~**O mapa de estilos não entra no resumo da FR-3889.**~~ **Corrigido em 13/11**, a pedido do
   usuário. O mapa saiu do Python para um arquivo versionado,
   `shared/templates/correio/estilos.json`, que `correio.py` lê uma vez: a mesma leitura estiliza o
   HTML e entra no resumo, como terceira fonte. O valor gravado ganhou rótulo de regra próprio,
   `‹nome›:sha256-com-estilos:‹hex›`; os gravados antes conservam `‹nome›:sha256:` e se conferem pela
   regra anterior. A FR-3889, a R-009, o data-model e o roteiro de conferência do quickstart da `121`
   foram revistos, com a redação anterior preservada. Um teste confere que o arquivo está no índice
   do Git e não é ignorado.
