# Research — 166 · A verificação da autodeclaração por vídeo

Cada decisão registra a alternativa descartada. As de número `D-` são da spec; as `T-` são técnicas,
deste plano.

## D-001 — A admissão do vídeo é declaração publicada da Etapa

**Decisão**: a Etapa ganha a coluna `admite_video` e o conteúdo publicado ganha `videoOption` em cada
item de `stages` — degrau 25. O Edital anterior é lido `false`.

**Por quê**: o vídeo muda o direito do candidato (um meio a mais de ser visto), e a Constituição exige
uma fonte só para regra de avaliação. A P-0 pede, além do ato, "Edital que o cite": sem o campo, o
Edital não teria onde citá-lo.

**Descartado**: (a) uma lista de Editais em variável de ambiente — regra de avaliação fora do Edital,
divergente dele; (b) habilitar por Etapa colegiada automaticamente com a chave — o sistema decidindo
por quem elabora.

## D-002 — Só na Etapa colegiada, com alcance e período

**Decisão**: a publicação e a Retificação recusam `videoOption = true` fora da Etapa decisória e
colegiada da `165`, sem alcance declarado (`163`), ou cujo Evento não tenha início e fim; e com a chave
desligada.

**Por quê**: a R-11 é uma regra sobre deliberação — sem colegiado não há regra para aplicar ao vídeo;
sem alcance, a ampla concorrência gravaria vídeo de autodeclaração que não fez; sem fim, o período não
termina e a R-12 não tem quando valer.

## D-003 — A maioridade é declarada pelo candidato

Ver *Clarifications*. A declaração vai na linha do vídeo (`declarou_maioridade`), e não numa tabela à
parte: o único efeito dela é o vídeo existir.

## D-004 — O parecer pelo vídeo é a Avaliação da `012`, e o meio é derivado

**Decisão**: não há coluna nova na Avaliação nem na Conclusão. Uma inscrição está **em modo vídeo**
numa Etapa quando tem vídeo vigente e não tem encaminhamento. Os pareceres concluídos enquanto ela está
em modo vídeo são pareceres pelo vídeo.

**Por quê**: a invariante "em modo vídeo, todo parecer concluído é pelo vídeo" se sustenta por três
regras que já são desta spec: o vídeo só é aceito sem parecer concluído (FR-7107); concluir exige ter
aberto o vídeo (FR-7134); a troca só existe antes da primeira abertura (FR-7124). E o encaminhamento
reabre todos os pareceres, de modo que tudo o que se concluir depois é ao vivo. O instante da
conclusão, preservado na `ConclusaoAvaliacao`, reconstrói o meio de qualquer parecer antigo.

**Descartado**: (a) uma coluna `meio` na Avaliação e na Conclusão — migration em duas tabelas com
gatilho de imutabilidade e a cópia de um fato que já é derivável; (b) uma tabela própria de pareceres
do vídeo — a estrutura paralela que o pedido proíbe.

## D-005 — O encaminhamento é ato da presidência, sem contagem, e reabre pela `012`

Ver *Clarifications*. O encaminhamento grava a linha append-only e chama a reabertura da `012` em cada
Avaliação, com o motivo fixo. Se a `165` recusar uma reabertura (autor exposto), a transação inteira
desfaz, e a inscrição não fica meio encaminhada.

**Descartado**: (a) uma votação nova, sem reabrir — a Atribuição é única por membro e inscrição, e
uma segunda Avaliação para a mesma pessoa contraria a FR-074 da `012`; (b) encaminhar sem a
presidência — um ato que muda o caminho do candidato sem autoria.

## D-006 — A R-11 mora no plano da consolidação e no ato que grava

**Decisão**: o plano da `165` (`_planejar`) recusa com o motivo `encaminhar à entrevista ao vivo` a
inscrição em modo vídeo cuja deliberação não é favorável; o ato que cria o Resultado deliberado e a
correção fixada do recurso recusam, por uma função só, o Resultado desfavorável sobre inscrição em modo
vídeo.

**Por quê**: o plano é a fonte única da conferência e do ato (a `165` já o usa assim); a guarda no ato
cobre a chamada direta.

**Descartado**: gatilho no banco — ele teria de ler o vídeo e o encaminhamento de outra app, e a
garantia que a spec pede é de domínio (FR-7139).

## D-007 — Abrir é ato; a entrega em intervalos não registra

**Decisão**: "Abrir o vídeo" é um `POST` que confere o resumo do arquivo, grava a `AberturaDoVideo`
(da comissão), registra **um** evento e devolve um identificador de abertura guardado na sessão. O
`<video>` pede `.../video/<abertura>` com `Range`; cada pedido confere que a abertura é daquela sessão,
daquele vídeo e daquela pessoa, e que a autorização continua valendo, e **não** registra.

**Por quê**: o reprodutor faz dezenas de pedidos por sessão de reprodução; registrar cada um afogaria a
trilha, e não registrar nenhum deixaria a leitura sem rastro (FR-7130).

**Descartado**: registrar no primeiro pedido `bytes=0-` — o Safari pede `bytes=0-1` antes e repete a
partir do zero ao voltar; contar "aberturas" por heurística de intervalo é frágil.

## D-008 — Retenção sem valor, contada do encerramento do Edital

**Decisão**: `VERIFICACAO_POR_VIDEO_RETENCAO_DIAS`, inteiro, **sem padrão** (vazio = `None`). O comando
`eliminar_videos_da_verificacao --edital <id> --confirmar` recusa sem o prazo, recusa o Edital não
encerrado ou dentro do prazo, e elimina o arquivo de cada vídeo do Edital, gravando a
`EliminacaoDoVideo` e um evento. O encerramento é o evento `ENCERRAR` da trilha do Edital.

## D-009 — A desistência não existe nesta entrega

Ver *Clarifications*.

## T-001 — Uma app nova, `verificacao`

O vídeo, o envio, a abertura, o encaminhamento e a eliminação são de uma capacidade só, e nenhuma das
apps existentes é dona dela: a Avaliação é do avaliador, a Inscrição é do candidato, o Resultado é da
consolidação. A app nova **lê** as três e **não** é lida por elas, exceto pelos dois ganchos — a
conclusão (FR-7134) e o plano da consolidação (FR-7138) —, que a chamam por importação local.

## T-002 — Envio em partes, sem protocolo de terceiros

**Decisão**: `POST envios` (inicia, declara tamanho, formato, duração medida, marcas e a maioridade) →
`PUT envios/<id>/partes?deslocamento=N` (corpo cru, ≤ 8 MiB) → `GET envios/<id>` (deslocamento
recebido) → `POST envios/<id>/concluir` (resumo do aparelho). As partes se acrescentam a um arquivo
temporário no armazenamento privado; o `PUT` com deslocamento diferente do recebido responde 409 com o
deslocamento certo.

**Por quê**: cabe nos 12 MB do nginx e nos 120 s do gunicorn síncrono, não muda nenhum limite global e
não precisa de dependência nova. O tus faria o mesmo com um pacote a aprovar.

**Corpo cru**: o `PUT` lê `request.body`; o `DATA_UPLOAD_MAX_MEMORY_SIZE` (2,5 MB) não se aplica a
corpo que não é formulário, e a view confere o tamanho pelo `Content-Length` antes de ler.

## T-003 — Conferência do contêiner sem biblioteca

**Decisão**: MP4 pela caixa `ftyp` nos bytes 4–8 e duração pela `mvhd` (escala e duração, versões 0 e
1); WebM pela assinatura EBML `1A45DFA3` e o `DocType` `webm`, e a duração pelo elemento `Duration`
da `Info` com o `TimecodeScale`, **quando existir** — o `MediaRecorder` do Chrome grava WebM sem
`Duration`, e então vale a duração medida pelo aparelho, conferida contra o teto. A leitura percorre
só as caixas e os elementos de topo, nunca o conteúdo.

**Descartado**: `ffprobe` ou `pymediainfo` — dependência nova e, no caso do `ffprobe`, um binário que
decodifica o vídeo, o que a R-19 manda evitar.

## T-004 — A política de conteúdo da página de gravação

A view da página de gravação responde com o cabeçalho `Content-Security-Policy` já montado: a política
comum mais `media-src 'self' blob:`. O middleware não sobrescreve cabeçalho existente
(`politica_de_conteudo.py`), e a exceção fica em **uma** função, `politica_com_midia_local()`. A mesma
resposta leva `Permissions-Policy: camera=(self), microphone=(self)`. As demais respostas não mudam.

## T-005 — A Mesa e o comprovante assistem pela mesma entrega

As duas superfícies usam `verificacao/infrastructure/entrega.py`: intervalo de bytes (`Range:
bytes=a-b`, `bytes=a-`, `bytes=-n`), 206 com `Content-Range`, 416 fora do arquivo, `Accept-Ranges:
bytes`, o tipo do formato guardado, `Cache-Control: no-store` e `Content-Disposition: inline`. A tela
usa `controlsList="nodownload"` e `disablePictureInPicture` — o que não impede captura, e a spec não
promete que impede.

## T-006 — Quanto custa a conferência do resumo

A abertura relê o arquivo inteiro para conferir o resumo: 25 MB a ~500 MB/s são ~50 ms. É uma vez por
abertura, e não por pedido. Os pedidos com `Range` não conferem.

## T-007 — Fonte sintética nos testes e no navegador

A suíte gera MP4 e WebM mínimos à mão (caixas `ftyp`/`mvhd`/`mdat`; cabeçalho EBML com `Info`/
`Duration`), sem codificar imagem. A verificação no navegador usa o `canvas.captureStream` e um
oscilador de `AudioContext`, como a prova de conceito — a página oferece a fonte sintética só com
`DEBUG` ligado e a chave ligada.
