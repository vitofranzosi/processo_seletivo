# Filme de lançamento — Sistema de Processo Seletivo · Cefor | Ifes

## Entregas

| Arquivo | O que é |
|---|---|
| `sistema-de-processo-seletivo-lancamento.mp4` | versão de distribuição — 1920×1080, 30 fps, H.264 (CRF 20) + AAC 320 kb/s, 4min38s, ~500 MB |
| `sistema-de-processo-seletivo-lancamento-master.mp4` | master — mesma montagem em H.264 CRF 14, ~2,0 GB, para reedição |
| `producao/` | as fontes da composição, para refazer um trecho |

Os MP4 ficam fora do git (`.gitignore` desta pasta).

Roteiro e decupagem da versão produzida. A grade musical é de 128 BPM: um compasso tem 1,875 s,
e todo corte, entrada de texto e efeito sonoro cai em batida.

**Sem Remotion, sem React, sem HTML animado.** Cada quadro é pintado por um compositor próprio
(skia sobre raster 1920×1080, em Python), recebe grão e vinheta em numpy e segue para o ffmpeg
(H.264). As interfaces são **capturas reais** do sistema rodando localmente sobre o banco de
demonstração (`seed_demo`), feitas em Chrome headless a 2× — nenhuma tela foi desenhada ou
inventada. A trilha é montada com Apple Loops do GarageBand (licença de uso em produções próprias),
todos em Dó menor a 128 BPM, e os efeitos sonoros são sintetizados.

Não houve geração de vídeo por IA: o ambiente não tem esse recurso. O que no prompt seria "cena
gerada" virou composição gráfica vetorial.

## Movimentos

| # | Tempo | Movimento | Música |
|---|---|---|---|
| I | 0:00–0:41 | **A complexidade invisível** — fragmentação | drone em Dó menor, tiques, riser; corte seco |
| — | 0:34–0:41 | Congelamento e silêncio: *"Mas nenhum deveria precisar começar do zero."* | pad, sub |
| II | 0:41–0:56 | **Transformação** — os fragmentos se reorganizam e viram a tela real | arpejo que abre o filtro, rufar, impacto |
| III | 0:56–2:56 | **Uma plataforma, uma jornada** — quatro trechos | groove eletrônico, uma variação por trecho |
| IV | 2:56–3:26 | **O que torna a plataforma diferente** — sete capacidades | variação mais rápida |
| V | 3:26–3:49 | **Clímax — tudo está conectado** | ápice |
| VI | 3:49–4:09 | **Encerramento** | pad e piano, fade |

## Decupagem

### I. A complexidade invisível (0:00–0:41)
- Tela escura. *"Cada processo seletivo tem suas regras."*
- As oportunidades surgem uma a uma — Bolsistas · Vagas remanescentes · Pós-graduação · Cursos FIC ·
  Outras seleções — e se multiplicam até forrar a tela.
- Entram as ferramentas avulsas, desenhadas como ícones vetoriais genéricos (não são telas de
  produto nenhum): formulário, planilha, PDF, e-mail, pasta, lista de controle, calendário. Linhas
  vermelhas as ligam umas às outras e se embaraçam, a cada batida.
- Legendas em sequência: *Um formulário se conecta a uma planilha. · A planilha depende de
  documentos. · Documentos chegam por diferentes canais. · Resultados precisam ser consolidados. ·
  Recursos precisam ser analisados. · Convocações precisam ser acompanhadas.*
- **Congela.** A imagem perde a cor, o som corta. Silêncio de um compasso.
- *"Mas nenhum deveria precisar começar do zero."*

### II. Transformação (0:41–0:56)
- Os fragmentos não somem: as linhas emaranhadas se endireitam em grade, cada ícone voa para uma
  posição de uma tela real (Visão Geral da gestão) e **vira** o bloco correspondente — o mesmo
  objeto, em continuidade, até a captura real assumir.
- Batida. A tela recua em perspectiva e surge **SISTEMA DE PROCESSO SELETIVO** · Cefor | Ifes.

### III. Uma plataforma, uma jornada (0:56–2:56)

**Da ideia ao edital.** Uma folha de PDF isolada se parte em blocos que se encaixam no assistente
de composição (Edital 02/2026, reaproveitado do 01). Perfis e quadro de vagas por modalidade,
cronograma, etapas, critérios de classificação, *Partir de um Edital anterior*, revisão. As
páginas do Edital oficial em linguagem simples se abrem em leque ("Quem pode se inscrever?",
"Quantas vagas há, e onde?"). A linha do tempo do ato: Elaboração → Revisão → Homologado →
Publicado, e a Retificação com o histórico preservado.
*Da ideia ao edital. · Regras estruturadas. · Publicações rastreáveis.*

**Da oportunidade à inscrição.** Um formulário avulso se dobra e vira o portal público. Busca e
filtro, o Edital com vagas, requisitos, documentos e cronograma. Acesso por código, sem senha.
Modalidade, documentos anexados, Requerimento de Matrícula, revisão, comprovante com código de
verificação. Celular em paralelo.
*Encontre. · Inscreva-se. · Acompanhe.*

**Da comissão ao resultado.** As linhas de uma planilha de avaliação deslizam e se tornam as
linhas da Mesa da avaliadora. Documentos associados à inscrição e à etapa. Distribuição entre
avaliadores, resultados da etapa, classificação calculada pelas regras, faixa de corte e
progressão, ocupação de vagas. Um recurso interposto pelo portal chega à julgadora. O resultado
publicado. Nenhuma IA julga: quem avalia é a comissão.
*Critérios definidos. · Avaliações organizadas. · Resultados estruturados. · Decisões rastreáveis.*

**Do resultado à convocação.** Respiro: *O resultado não encerra a jornada.* Situação individual
no acompanhamento, convocação (vagas, convocadas, efetivas, a ocupar), Requerimento de Matrícula
enviado e a exportação que prepara os dados para o Registro Acadêmico — o sistema gera o arquivo;
a matrícula é efetivada fora dele.
*Da classificação à convocação.*

### IV. O que torna a plataforma diferente (2:56–3:26)
Governança (papéis e autoridades) · Rastreabilidade (trilha de auditoria) · Operação (Visão Geral
com sinais de atenção) · Transparência (resultado por perfil e lista, sorteio verificável) ·
Comunicação (avisos vinculados à publicação — *habilitação condicionada à validação institucional*)
· Flexibilidade (perfis, modalidades, etapas, sorteio) · Evolução (assistente de dúvidas —
*piloto interno, experimental, em validação*).

### V. Clímax (3:26–3:49)
Os objetos do filme reaparecem como nós de uma rede; a câmera a atravessa; eles se alinham em
**EDITAL → INSCRIÇÃO → AVALIAÇÃO → RESULTADO → RECURSO → CONVOCAÇÃO**.
*Uma plataforma. Diferentes seleções. Uma jornada integrada.*
*Menos fragmentação. · Mais organização. · Mais transparência. · Mais capacidade de gestão.*

### VI. Encerramento (3:49–4:09)
Composição mínima. **SISTEMA DE PROCESSO SELETIVO** — Cefor | Ifes.
*A complexidade faz parte da seleção. A fragmentação não precisa fazer.*

## Fidelidade
- Toda tela é captura do sistema real (commit desta branch), sobre dados de demonstração. Nomes de
  candidatos são os do `seed_demo`; os documentos anexados são PDFs marcados como fictícios.
- Nenhum número institucional aparece como real: o que se lê nas telas é a demonstração.
- Avisos complementares: mostrados como capacidade, com a ressalva de que a habilitação depende de
  validação institucional (estão desligados em produção até a validação de LGPD).
- Assistente de dúvidas: mostrado como piloto interno e experimental, com o rótulo da própria tela
  ("Protótipo interno, não visto por candidatos").
- Matrícula: o filme mostra o Requerimento e a exportação; não mostra matrícula efetivada.

## Trilha

Apple Loops do GarageBand, todos em Dó menor; os de groove a 128 BPM, sem esticar. Abertura:
Legend Synth Drone, Legend Dark Synth Pad, Fast Hat Beat, Basic Core Beat, Hard Grinding Bass.
Frase e encerramento: Afloat Pad, Longing Piano. Jornada: Chronograph Set Beat 01, Rocket Fuel
Beat 01, Deep Cycles Beat, Blueprint Beat 01, Tight Tech Beat, Luminosity / Lightspeed Lead / Pure
Candy / Spike Riff / Mass Appeal Synth Layers, Airy Vox Synth, Progressive Techno Synth, Rolling Emo
Synth, Melodic Silk Bass, Power Tool Bass. Clímax: Sweeper Beat, Deep Dream Synth, Four Four Beat,
Epic Anthem Synth, Thick Gritty Bass. Viradas: toppers do mesmo pacote. Risers, whooshes,
impactos, cliques de interface e o tique de relógio são sintetizados (numpy/scipy).
Sonoridade final: −16 LUFS integrados (medido: −15,7), pico verdadeiro −1,5 dBTP.

## O que conferir antes de exibir

- **A trilha foi equilibrada por medição, não por audição.** Níveis por trecho (EBU R128),
  espectrograma e grade de tempo foram conferidos; ninguém ouviu a mixagem. Vale uma escuta
  atenta — em especial a abertura (drone grave) e o clímax.
- Sem locução, por decisão: trilha, efeitos e tipografia cinética carregam o filme.
- Não houve vídeo gerado por IA (o ambiente não tem esse recurso); as passagens "geradas" do
  prompt viraram composição gráfica sobre as telas reais.

## Como refazer

Os dados vêm de um banco próprio, `ps_filme` (PostgreSQL local), preparado com `make preparar` e
`seed_demo`, e acrescido, só ali, de: Edital 02/2026 reaproveitado do 01 (composição limpa),
documentos PDF fictícios anexados às inscrições do Edital 51, a inscrição da Ana no Edital 01 feita
pelo portal e um recurso da Elisa. As capturas são de `producao/capture.py` (Playwright + Chrome
headless, escala 2); cada cena é um módulo `sc_*.py` que pinta o quadro no instante `T`;
`render.py` renderiza em paralelo com desfoque de movimento; `score.py` monta a trilha;
`mux.sh` junta e normaliza. A grade de tempo comum está em `timeline.py`.

## Revisão de 15/10 — texto não cruza imagem

Regra de layout aplicada a todas as cenas: com legenda embaixo, a imagem fica acima da faixa
(y ≤ 818); com legenda à esquerda, a imagem fica à direita da coluna (x ≥ 770). `kit.room()`
encaixa cada pose na zona. Cartão e legenda não entram nem saem ao mesmo tempo; no clímax, o
rótulo de um nó só aparece onde não há outro cartão por baixo, e a rede termina numa grade
legível antes de virar a cadeia.

`producao/overlap.py` mede isso quadro a quadro: intercepta o desenho de textos e imagens e
acusa todo texto que cubra ≥15% de imagem ou de outro texto. Na versão final, a 20 amostras
por segundo, sobram só dois casos intencionais — a frase do congelamento sobre o fundo
desfocado e escurecido (0:36–0:41) e o meio segundo em que as linhas da planilha se
transformam nas da Mesa (1:59).

## Revisão de 15/10 — telas planas e câmera no detalhe

As telas deixaram de ficar inclinadas em perspectiva enquanto são lidas: a inclinação deformava a
letra em trapézio. Agora toda tela de interface fica de frente em repouso; o giro existe só no
movimento de entrada e saída, proporcional ao deslocamento (`kit.moved`), e some quando a tela
assenta. A perspectiva continua onde não há interface para ler: o recuo do título e o voo do
clímax.

A câmera passou a ir ao detalhe: em vez da página inteira, cada tomada recorta a região que se lê
(contadores, tabela, formulário), e a letra chega a ~100% do tamanho da captura, contra ~60%
antes. Na composição do Edital, a faixa das etapas rola para manter a etapa ativa à vista. Os
destaques verdes vêm de caixas medidas no DOM real (`producao/domboxes.py` → `dom.json`), não
mais estimadas, e nunca passam da borda do recorte.

## Revisão de 15/10 — ênfase no assistente e na linguagem simples

Duas sequências entraram sem retemporizar o resto (`timeline.INSERTS`; `film.py` toca cada uma no
lugar e desloca o filme original). O filme passou a 4min43s.

**O Edital em linguagem simples (1:20–1:35).** No ponto em que o Edital oficial aparece, a câmera
desce pelo próprio PDF publicado do Edital 01/2026: o "Resumo deste Edital", o sumário em perguntas
("Quem pode se inscrever?", "Quantas vagas há, e onde?", "Como recorrer?") e, rolando, a seção de
vagas da página 2. Legendas: *Resumo em cinco linhas. · Um sumário que responde. · Escrito para ser
entendido.* É funcionalidade implementada (`069`), sem ressalva.

**O assistente do Edital (2:11–2:30), selo "Em breve".** Telas reais do painel da `074` (assistente
na página do Edital), capturadas na página pública do Edital 01/2026 com o código da worktree da
`074` — trabalho ainda não commitado, rodado sem alterar nenhum arquivo dela — sobre uma cópia do
banco do filme (`ps_filme_074`). O percurso é o das perguntas sugeridas: "Que documentos preciso
enviar?" → a opção → a resposta pronta, montada dos dados do Edital, com a ressalva de que a
conferência é da seleção → "Consultar fontes", com o trecho literal do Edital. Legendas: *Pergunte ao
Edital. · Respostas do texto oficial. · Com a fonte citada. · Não substitui o Edital.* O item
"Evolução" dos diferenciais passou a usar o mesmo painel real, com o mesmo selo.

**A pergunta livre ao modelo não aparece no filme.** Foram três perguntas livres sobre este Edital
de demonstração (OpenRouter, `qwen/qwen3.8-27b`): duas voltaram "Não foi possível confirmar uma
resposta nas fontes deste Edital" ("Posso me inscrever nas duas vagas ao mesmo tempo?", "Quantas
vagas há para Professor de Informática, e onde?" — a primeira tem resposta no texto da página: "Cada
candidato pode enviar apenas 1 (uma) inscrição"), e uma respondeu com fonte, mas afirmou "às 20h57"
e, na frase seguinte, que o Edital não informa o horário ("Onde e quando será a prova?"). O 20h57
vem do `seed_demo`, que grava os eventos do Cronograma com hora — o próprio PDF diz "18/11/2026, às
20h57". Mostrar uma resposta livre sugeriria um desempenho que o teste não confirmou. Fica como
registro para a `074`/`071`, não como escopo deste filme.

O selo do painel ("Ambiente local de desenvolvimento") aparece nas telas, como é.

## Revisão de 15/10 — a segunda metade para o público geral do Cefor

A partir da avaliação, o filme virou inventário: 13 telas em ~60 s, vocabulário de quem opera
("faixa de corte", "ocupação", "admissibilidade", "tempestividade") e sete diferenciais em lista.
As três seções foram refeitas em linguagem simples, uma ideia por tela (`timeline.PLAYLIST`):

- **Da comissão ao resultado (2:30–2:50).** *A comissão avalia.* (a Mesa e os documentos) · *O sistema
  classifica.* (o resultado público) · *Quem discorda, pode recorrer.* (o formulário do candidato).
- **Convocação (2:50–3:04).** *Aprovado? A convocação chega.* (o celular) · *Matrícula com os dados
  prontos.*
- **O que muda na prática (3:04–3:19).** *Tudo fica registrado. · Tudo é público. · Tudo num só lugar.*

Saíram do filme — continuam no sistema e cabem num vídeo técnico para quem opera: distribuição e
carga, consolidação, corte, ocupação, rito do recurso, fila de suplentes, formato de exportação,
governança, flexibilidade e avisos. As legendas da primeira metade também perderam o jargão
("Regras organizadas.", "Publicado, fica registrado.", "Basta o e-mail: um código chega na hora.").
O filme passou de 4min43s a 4min02s.

## Revisão de 15/10 — o Edital gerado, a publicação, a pergunta livre e a planilha

Cinco pontos levantados pelo responsável pelo produto, todos com telas reais:

- **O Edital é gerado do que se preenche (1:16–1:31).** O formulário da composição do Edital 02/2026
  em cima, o PDF que o sistema gerou embaixo; cada linha preenchida "escreve" a linha correspondente
  do documento (Perfis → Tabela 1; Cronograma → Tabela 5). *Você preenche. · O sistema escreve o
  Edital. · Edital pronto.* A sequência de linguagem simples passou a usar o mesmo Edital 02.
- **Publicar põe no ar (1:46–2:04).** O Edital 02 foi submetido, homologado e publicado de verdade
  no banco do filme, por três pessoas (ana.elaboradora, bruno.homologador, carla.publicadora). A cena
  mostra "Quem atuou", o "Confirmar: Publicar" — com a própria frase da tela: "A Publicação passa a
  constar da consulta pública, acessível a qualquer pessoa" — e /gestao ao lado de /selecoes: a
  página pública passa de "1 seleção" a "2 seleções com inscrições abertas", com o Edital 02 no topo.
- **Assistente: sugerida × livre (2:34–3:01).** Zoom no "Assistente de IA"; "1 · Pergunta sugerida"
  com "Resposta pronta, montada a partir dos dados do Edital"; "2 · Pergunta livre": a pergunta
  digitada, "Consultando as informações deste Edital…" e a resposta da IA com a citação. A pergunta
  foi feita de verdade ao modelo: "Preciso ter mestrado para a vaga de professor?" → "Sim, para a
  vaga de Professor de Informática (Perfil DOC-INFO) o Edital exige mestrado em Computação ou área
  afim", citando o requisito do Perfil — confere com o Edital. Das três perguntas livres desta rodada,
  uma voltou "não foi possível confirmar" ("Até quando tenho isenção da taxa de inscrição?").
- **A planilha da matrícula (3:28–3:38).** A planilha real, baixada da exportação do Edital 51/2026
  (aba `Import_ModeloCefor`, 34 colunas), se preenche a partir do Requerimento e segue para o
  Registro Acadêmico, que a importa. A planilha não mostra o CPF; a tela do Requerimento, no
  celular, mostra o CPF fictício da demonstração (111.444.777-35, o mesmo de todos os candidatos do
  `seed_demo`).
- **3:15 (agora 3:49).** A Visão Geral em recorte legível: indicadores e a lista de Editais.

O filme passou a 4min37s. O banco `ps_filme` agora tem o Edital 02/2026 publicado.

## Revisão de 15/10 — Edital em linguagem simples, e publicado é aberto a todos

As duas cenas da revisão anterior foram refeitas: a do formulário ao lado do PDF (linhas cobertas,
ligações) ficou amadora, e os rótulos /gestao e /selecoes não diziam nada ao público. O objetivo
macro passou a guiar a sequência inteira:

- **O sistema escreve o Edital, em linguagem simples (1:16–1:29).** A composição recua e a página do
  Edital se compõe ao lado, de cima para baixo. Depois, a página assume o centro e, à esquerda: *Lei
  nº 15.263/2025 · Política Nacional de Linguagem Simples — Em linguagem simples. Frases diretas.
  Voz ativa. Sem jargão.* A câmera entra no documento (resumo, sumário em perguntas, tabelas).
- **Revisado, publicado, aberto a todos (1:44–1:59).** "Quem atuou" (quem elaborou, revisou e
  publicou); o clique em "Confirmar: Publicar"; a página pública do Edital entra, o PDF gerado
  encaixa no botão "Ler o Edital completo (PDF)", e a cena termina no clique em "Ver vagas e
  inscrever-se" — que abre o capítulo da inscrição.

A lei é citada pelo número e pelo nome, como no repositório (docs da `069` e a pesquisa de 07/10,
com o link da Câmara). O filme passou a 4min31s.

## Revisão de 15/10 — continuidade

Diagnóstico de continuidade sobre o render (imagem vista quadro a quadro nas fronteiras; áudio
medido, não ouvido) e quatro correções, sem mexer na estrutura:

- **1:58,9 (publicação → inscrição).** A cena terminava clicando em "Ver vagas e inscrever-se" do
  Edital 02 e o corte levava a outro percurso (procurar e se inscrever no Edital 01); o cartão e a
  legenda sumiam a meio da saída. Agora a cena termina no destaque "Inscrições abertas", o cartão
  sai para cima e a legenda acaba antes do corte.
- **1:15,7.** "Regras organizadas." era cortada no meio da saída; agora termina 0,35 compasso antes.
- **1:43,9.** A página do Edital saía num corte seco; agora sobe nos últimos 0,55 s.
- **2:28,9 (inscrição → assistente), áudio.** A trilha caía a −34/−43 dB por ~0,4 s no corte. O pad
  do assistente entra 0,5 s antes, o groove da inscrição faz cauda de um compasso e o baixo do
  assistente entra no corte. No MP4 final o mínimo ali é −25,5 dB, na faixa das demais junções.
  Falta confirmar ouvindo.

Ficaram de fora: o "Convocado" já visível no Acompanhe (2:21–2:28), que antecipa a convocação
(refinamento opcional), e o respiro de áudio em 2:55, que pode ser intencional.

## Revisão de 15/10 — a avaliação com o documento aberto

"A comissão avalia." (2:59–3:07) mostrava a lista de documentos com botões "Abrir" e nada aberto.
Agora é uma tomada contínua sobre a tela real da avaliação da Ana, com o diploma aberto no
visualizador da própria Mesa: a câmera vai do documento à lista ("1 de 2 abertos por você",
"aberto") e à nota 8,5 com o parecer. A legenda fica na coluna da esquerda, e três passos acendem
junto com a câmera: *O documento, aberto ao lado. · Cada consulta, registrada. · A nota, com o
parecer.* A cena ganhou um compasso (o filme passou a 4min33s), para o resultado e o recurso não
ficarem apertados.

O diploma é fictício (`producao/diploma.py`: "Universidade de Exemplo — modelo para demonstração,
sem valor legal", marca d'água "DOCUMENTO FICTÍCIO"). Ele substituiu, só no banco `ps_filme`, o
arquivo do diploma da inscrição da Ana no Edital 51, com o hash atualizado (`troca_diploma.py`) —
a tela confere o arquivo pelo hash. A tabela de documentos enviados não é append-only.

Do exemplo de referência ficaram de fora a moldura de navegador (nenhuma outra tela do filme a usa)
e as palavras grandes sobre a tela (voltariam a sobrepor texto e interface).

**Assistente (2:28–2:33).** A câmera aproxima do botão "Dúvidas sobre este Edital" antes do clique,
recua para mostrar o painel deslizando sobre a página e então aproxima do cabeçalho, agora com a
linha inteira de perguntas sugeridas (antes cortava "Que documentos preciso enviar?" e "Quantas
vagas há?").

**Matrícula (3:24–3:38).** O Requerimento de Matrícula é opcional por Edital (na inscrição, na
convocação ou nenhum) e serve às seleções de estudantes; o exemplo é um Edital de professor. A
legenda passou a dizer a condição: rótulo "Seleção de estudantes" e "Quando o Edital pede o
Requerimento de Matrícula, o sistema gera a planilha no modelo do sistema acadêmico."

**Sorteio (3:12–3:17).** Entre "O sistema classifica." e o recurso, a outra forma de classificar:
*Ou por sorteio.* — com três garantias em linguagem simples, cada uma acendendo o item "confere"
correspondente da página pública "Verificar este sorteio" (Edital 26/2026): *Lista fechada antes do
sorteio.* (a relação publicada) · *Números de sorteio público, de fora.* (a semente) · *Qualquer
pessoa refaz e confere.* (a ordem publicada). As três vêm da spec `021` (universo congelado antes da
semente; semente de ocorrência futura de fonte pública externa — a Loteria Federal é o adaptador de
referência —; ordem reproduzível por qualquer pessoa). A frase não nomeia a Loteria Federal porque a
tela da demonstração mostra "Fonte de demonstração". Três compassos; o filme passou a 4min38s.

**Ordem: recurso antes do sorteio.** Com o recurso logo depois do sorteio, parecia que se recorria do
sorteio — cuja confiança vem de conferir, não de contestar —, e o recurso mostrado é contra uma prova
avaliada por pessoas. A sequência passou a ser: *A comissão avalia. → O sistema classifica. → Quem
discorda, pode recorrer.* e só então *Outra forma de classificar — Por sorteio.* (as três garantias),
seguido da convocação. O filme não afirma que o sorteio não tem recurso: no sistema, o prazo de
recurso é da publicação do resultado (`018`), não do método de classificação.
