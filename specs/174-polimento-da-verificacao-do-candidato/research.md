# Research: O polimento das telas do candidato na verificação por vídeo

As decisões técnicas do plano. As de domínio estão na spec (`D-001` a `D-010`); as daqui são `T-`.
Cada uma diz o que se escolheu, por quê e o que se descartou. Nenhuma ficou como "precisa de
esclarecimento": as quatro perguntas da spec foram decididas pelo usuário em 15/11.

## T-001 — O palco é uma seção só, com dois estados e um elemento de vídeo

**Decisão.** As seções `camera` e `gravacao` de hoje viram `data-tela="palco"`, com
`data-estado="preparo"` ou `data-estado="gravando"` no próprio elemento. Há **um** `<video>` de prévia,
e não dois: o fluxo da câmera abre ao entrar no palco e continua o mesmo ao começar a gravar. O script
troca o estado, e a folha decide o que aparece em cada um (a lista dos passos, o medidor grande e
"Começar a gravar" no preparo; a instrução, o selo, "Próximo" e "Parar e recomeçar" gravando).

"Continuar", no "Antes de gravar", chama `abrirCamera()` direto: o toque é o gesto que o navegador
exige para pedir a câmera, e a permissão aparece sem outro clique (FR-7866). A recusa leva à tela
`permissao`, como hoje; "Tentar de novo" chama a mesma função.

**Por quê.** Dois elementos de vídeo com o mesmo fluxo dobram a decodificação no celular, e trocar de
tela entre o teste e a gravação fazia a pessoa perder o enquadramento que acabou de acertar (D-004).

**Descartado.** Manter as duas telas e abrir a câmera sozinho no teste: continua o clique em "Ir para a
gravação", que é a queixa 5.

## T-002 — A instrução sobre o vídeo, por grade, e não por posição absoluta em cascata

**Decisão.** O palco é uma grade de uma célula; a prévia, o guia, a faixa de cima (passo, título e
instrução) e a faixa de baixo (selo, tempo, "Próximo") ocupam a mesma célula (`grid-area: 1 / 1`), e
cada faixa se alinha pelo `align-self`. A faixa da instrução tem fundo escuro com opacidade de 0,78
sobre texto branco, o que dá contraste acima de 4,5:1 mesmo sobre um quadro branco puro (SC-2656: o
pior caso é calculado e o teste mede a cor computada). Ela ocupa no máximo um terço da altura, e o que
passar disso rola dentro dela — é o caso do passo 4 (A-4 da spec).

O texto vem dos atributos `data-texto` e `data-titulo` que o template já escreve a partir de
`roteiro.PASSOS`; o script só escolhe qual mostrar (D-003). O anúncio ao leitor de tela continua num
elemento `aria-live="assertive"`, agora com "Passo N de 4: título. instrução" (UX-875).

**Por quê.** A grade mantém a ordem do documento (instrução antes do botão) para o leitor de tela e
para o teclado, e não depende de coordenadas que mudam com a proporção da câmera.

**Descartado.** Desenhar a instrução num `<canvas>` sobre o vídeo: o texto deixaria de ser texto.

## T-003 — No celular, o palco ocupa a tela pela composição

**Decisão.** Abaixo de 40rem, o palco em uso recebe `position: fixed; inset: 0` e a altura
`100dvh` (com `100vh` antes, para navegador sem a unidade), cobrindo o cabeçalho do portal sem tirá-lo
do documento. A prévia ocupa a célula inteira com `object-fit: cover`, e os controles respeitam
`env(safe-area-inset-bottom)`. No computador e no tablet largo, o palco fica na coluna, em paisagem,
com `aspect-ratio: 16 / 9` e altura máxima de 70% da janela (FR-7876).

**Por quê.** O modo de tela cheia do navegador, no iPhone, só vale para o elemento de vídeo e entrega
o vídeo ao reprodutor do sistema, que esconde a instrução e os controles (D-005). A composição faz o
mesmo nos dois sistemas.

**Descartado.** Esconder o cabeçalho por classe no `body`: exigiria o script mexer fora da página, e o
`fixed` resolve sem isso.

## T-004 — A tela acesa, pelo pedido do próprio navegador

**Decisão.** Ao entrar no palco, o script pede `navigator.wakeLock.request("screen")`; ao sair do palco
(revisão, "não consigo", voltar) solta o pedido. O navegador solta o pedido sozinho quando a página
some, e por isso, ao voltar a ficar visível com o palco aberto, o script pede de novo. Sem a interface,
ou com o pedido recusado, o palco mostra o aviso da FR-7877 antes de "Começar a gravar".

A `Permissions-Policy` da página de gravação continua `camera=(self), microphone=(self)`: ela não cita
`screen-wake-lock`, cuja lista padrão já é a própria origem. Nada muda no cabeçalho (FR-7889).

**Suporte.** Safari no iPhone desde 16.4, Chrome no Android desde 84, Firefox desde 126, Safari e Chrome
no computador. O aviso cobre o resto, e o descarte de quando a página some (a FR-7115 da `166`) continua.

**Descartado.** Tocar um vídeo mudo em laço para impedir o apagamento, truque antigo: gasta bateria e
não é garantido.

## T-005 — O avanço só pelo gesto, com o foco em "Próximo" e a proteção contra o toque duplo

**Decisão.** Ao começar, o foco vai para "Próximo" e fica lá a cada passo (o script devolve o foco
depois de trocar o texto). Espaço e Enter o acionam pelo comportamento nativo do botão, sem atalho de
teclado próprio. Uma função pura, `aceitaAvanco(agora, ultimo)`, recusa o segundo toque a menos de 500
ms do anterior (FR-7870). "Parar e recomeçar" fica no canto de cima, oposto a "Próximo", e menor.

**Por quê.** É a recomendação da Q-1 (D-001): o problema é a posição do alvo, e não o relógio. O meio
segundo é proteção contra dois toques de um gesto só, e não tempo mínimo de passo: ninguém leva menos
que isso para mostrar um documento ou virar o rosto.

**Descartado.** Atalho de tecla de letra (WCAG 2.1.4); tocar em qualquer lugar do vídeo para avançar,
que dispara com a mão que segura o documento.

## T-006 — O medidor de som grande, com a frase que diz o que ele mostra

**Decisão.** O `<meter>` continua (é o controle nativo, e o leitor de tela o lê), com largura cheia e
altura de 12 px. Uma função pura, `ouviuFala(niveis)`, diz que houve fala quando o nível passa de 20
em pelo menos 300 ms seguidos; a frase passa a "Estamos ouvindo você", anunciada uma vez. Sem faixa de
áudio, a frase diz que o microfone não foi encontrado, e "Começar a gravar" continua disponível.
Durante a gravação, o medidor fica pequeno, ao lado do selo.

**Por quê.** É nível de sinal, calculado no aparelho, e não entra no que se envia (FR-7890).

## T-007 — O nome publicado da Modalidade sai do conteúdo que a página já lê

**Decisão.** A função `_nome_da_modalidade(conteudo, perfil_id, modalidade_id)`, de
`portal/passo_da_etapa.py`, muda para `editais/domain/alcance.py` como `nome_da_modalidade`, pública e
pura. A `Situacao` da `166` ganha `modalidade: str = ""`, que `envio.contexto_do_titular` preenche com o
conteúdo vigente que ele já carrega. O título da página é `situacao.nome_da_etapa`, que já existe.

**Por quê.** O app `verificacao` não importa do `portal`; a função é de leitura do conteúdo publicado,
e o lugar dela é o domínio do Edital, ao lado de `codigo_da_modalidade`. Nenhuma consulta a mais.

**Descartado.** Uma segunda leitura do conteúdo na view do portal.

## T-008 — O selo provisório com ícone em SVG no próprio HTML

**Decisão.** `p.rotulo-da-situacao` vira pílula (`--raio-pilula`), sem tracejado. O provisório leva o
ícone de relógio e fundo âmbar claro; o registrado, o de confirmação e fundo verde claro. Os ícones
ficam num include, `portal/_icone.html`, com o traço de 1,75 da barra lateral da gestão, `aria-hidden`
e a palavra sempre ao lado (UX-155 da `063`, UX-873).

As frases do passo mudam em `portal/situacao.py`: `VER_COMO_FUNCIONA` dá lugar a
`ESCOLHER_VIDEO_OU_AO_VIVO = "Escolher entre vídeo e entrevista ao vivo"`, e o prazo deixa o meio da
frase principal e vai para o campo `prazo` da `Acao`, que o template já mostra em linha própria — com
um rótulo próprio do passo ("Prazo:"), e não o da convocação (FR-7857).

**Por quê.** A política de conteúdo tem `img-src 'self'`, e um SVG em `data:` na folha seria recusado.
O SVG escrito no HTML não é carga de imagem, e herda a cor do texto.

**Descartado.** Glifo de texto (◐, ✓), que o estudo de design system manda sair aos poucos.

## T-009 — A composição centrada, por envoltório, sem mexer na `main` do portal

**Decisão.** As três páginas da verificação envolvem o bloco `conteudo` em `<div class="jornada">`,
com `max-width: var(--coluna); margin-inline: auto`. O cabeçalho "onde estou" (`.jornada-momentos`) é
uma lista ordenada de três itens com o atual marcado por `aria-current="step"` e por peso, e não só
por cor. As medidas `--leitura` do bloco da `166` saem.

**Por quê.** A `main` do portal serve outras telas, que são da `P2.3` do estudo. O envoltório dá a
composição da jornada só onde esta spec alcança.

**Dependência.** `--coluna` e os demais tokens chegam com o #564 (D-007). A implementação desta spec
começa depois do merge dele; se o usuário preferir não esperar, o incremento A acrescenta os mesmos
tokens com os mesmos valores, e o merge do #564 resolve o conflito pela versão dele.

## T-010 — A escolha em cartões com um botão cada

**Decisão.** Cada forma é um `<article class="forma">` com título (`h3`), três linhas de descrição e um
botão de largura cheia — "Gravar um vídeo curto" e "Prefiro entrevista ao vivo", os rótulos de hoje.
Os dois botões têm o **mesmo** desenho (secundário forte), porque a FR-7108 da `166` pede o mesmo peso.
Lado a lado a partir de 40rem; empilhados abaixo, o vídeo primeiro, como hoje.

**Descartado.** O cartão inteiro como botão: um botão não pode conter título nem parágrafo, e o nome
acessível ficaria com três frases.

## T-011 — As opções da idade e a recusa que só aparece depois do gesto

**Decisão.** Cada rádio fica num `label.opcao-grande`, com borda e alvo de 48 px, e o selecionado se
destaca por `:has(:checked)` com borda mais grossa e marca (Safari desde 15.4; sem suporte, o rádio
nativo continua mostrando a escolha). A recusa ganha a regra que faltava:
`.verificacao [hidden]{display:none !important}`, delimitada às páginas da verificação (FR-7854,
A-2). Ao "Continuar" sem resposta, a recusa aparece e o foco vai para o `fieldset`, que a cita por
`aria-describedby`.

**Descartado.** A regra global `[hidden]{display:none !important}` no portal: corrigiria o A-2 em todas
as telas, mas muda telas fora do escopo sem conferência. Fica no registro.

## T-012 — O comprovante, a duração por extenso e a impressão

**Decisão.** Um filtro `duracao_por_extenso`, em `portal/templatetags/`, transforma segundos em
"1 min 12 s" (e "45 s" abaixo de um minuto), com arredondamento para o segundo. O template abre pela
confirmação (`.confirmacao-do-envio`, ícone e data), segue com "E agora?", "Assistir", "Gravar outro
vídeo" e "Dados para conferência" (`dl` em linha, texto de 0,875rem). Na impressão, o reprodutor, o
botão de assistir e o "voltar" somem, e a página cabe numa folha (FR-7884). A revisão calcula os
megabytes no script por `megabytes(bytes)`, pura, com uma casa.

## T-013 — O celular deitado e o movimento reduzido

**Decisão.** `@media (orientation: landscape) and (max-height: 30rem)`: a faixa de baixo passa a coluna à
direita da prévia, e uma linha "Fica melhor com o celular em pé" aparece no preparo, sem impedir
(FR-7878). `@media (prefers-reduced-motion: reduce)` desliga toda transição do palco (FR-7879); nenhuma
animação pisca.

## T-014 — O que acontece com os testes de hoje

- `tests/portal/test_verificacao_por_video.py` lê textos que continuam ("As duas formas valem igual.",
  "Gravar um vídeo curto", "Prefiro entrevista ao vivo", "Tenho menos de 18 anos", "Não consigo usar a
  câmera", "isso não é reprovação", "Gravar outro vídeo", "nodownload") e o cabeçalho de política de
  conteúdo; deve passar sem mudança, e ganha os casos novos.
- `tests/unit/portal/test_situacao_do_passo.py` e `tests/portal/test_vocabulario_do_passo.py` leem as
  frases do degrau; mudam com o rótulo da ação e a linha do prazo.
- `tests/javascript/gravacao.test.js` testa as funções puras de hoje, que não mudam (FR-7887), e ganha as
  novas.
- Os testes de envio e de contrato da `166` (`tests/integration/verificacao/`, `tests/unit/
  verificacao/`) NÃO DEVEM mudar: são a prova da FR-7887.
- Os guardiões de folha (`test_folha_estatica.py`, a acessibilidade que exige regra para toda classe,
  `test_larguras.py`) leem a folha e os templates como texto: cada classe nova precisa de regra, e
  nenhum `}}` nem `%}` pode aparecer na folha.

## T-015 — A prova no navegador, com a câmera simulada do Chromium

**Decisão.** Uma jornada nova, `tests/navegador/test_jornada_do_video.py`, sobe o `live_server` em
`localhost` (contexto seguro, que a câmera exige) e abre o Chromium com
`--use-fake-device-for-media-stream` e `--use-fake-ui-for-media-stream`: a câmera e o microfone
simulados respondem sem diálogo. Ela percorre, a 375×667 e a 1280×800, do acompanhamento ao comprovante
e mede:

- a diferença das margens da coluna (SC-2650);
- a altura do palco contra a janela e a visibilidade da instrução, de "Próximo" e de "Não consigo usar a
  câmera" a cada passo (SC-2651);
- os cliques entre "Continuar" e "Começar a gravar" (SC-2652);
- todo elemento com `hidden` no carregamento de cada tela, por `getComputedStyle(...).display`
  (SC-2653);
- o corpo do pedido de início do envio: a versão do roteiro, as quatro marcas em ordem, o formato
  (SC-2654);
- a cor computada da faixa da instrução (SC-2656).

A fixture `navegador` de hoje lança o Chromium sem argumentos; a jornada nova tem a sua, com os dois
argumentos, e fecha as conexões ao sair, como a outra (a armadilha do `DROP DATABASE` no `CLAUDE.md`).

**Descartado.** A imagem de teste do desenvolvimento (`fonte_sintetica`) na jornada: ela não passa pelo
pedido de permissão, que é justamente o que a FR-7866 muda.

## T-016 — Os aparelhos reais pedem contexto seguro

**Achado do plano.** O navegador só abre a câmera em contexto seguro: HTTPS ou `localhost` **no próprio
aparelho**. Um celular que abre `http://<ip-da-máquina>:8174` não consegue pedir a câmera, e o portal
recusa o host fora de `ALLOWED_HOSTS`. O quickstart descreve dois caminhos que não mandam nada para fora
da rede local:

- **Android**: cabo USB, depuração ligada e `adb reverse tcp:8174 tcp:8174`; o Chrome do celular abre
  `http://localhost:8174`, que é contexto seguro.
- **iPhone**: um certificado local (`mkcert`), com a autoridade instalada e confiada no iPhone, e um
  proxy TLS na frente do `runserver` (por exemplo, o `caddy reverse-proxy`), com o nome do host em
  `ALLOWED_HOSTS` e em `CSRF_TRUSTED_ORIGINS` só nesse ambiente.

Um túnel público (serviços de túnel por domínio externo) é mais simples, mas faz o vídeo de teste e a
sessão passarem por terceiro; fica como última opção, só com dados de demonstração e com o aval do
usuário. Pelo cabo, o envio não passa pela rede do celular; o envio por rede móvel de verdade (A-5 da
spec) só acontece com o túnel ou num ambiente de homologação com HTTPS, e por isso fica registrado, e
não prometido.
