# Prova de conceito: verificação por vídeo (entrega 0)

Uma página estática, sem servidor do GPS e sem dado real, que percorre o caminho inteiro do lado
do navegador e mede o que cada navegador produz. Nada sai do aparelho: o "envio" fatia o arquivo e
calcula o SHA-256 de cada parte e do todo, e a "trilha" vive na memória da aba. Fechar a aba apaga
tudo.

| Arquivo | O que é |
|---|---|
| `index.html` | as três visões: Candidato, Comissão e Medição |
| `poc.js` | captura, gravação guiada, revisão, envio simulado, Mesa, deliberação e medição |
| `poc.css` | tokens de `shared/tokens.css`, celular primeiro |

A página roda sob a **mesma CSP do GPS** (`shared/politica_de_conteudo.py`), declarada num `<meta>`,
com uma só exceção: `media-src 'self' blob:`. Estilo e script vêm de arquivo, como no produto.

## Como rodar

```bash
python3 -m http.server 8091 --bind 127.0.0.1 --directory doc/estudo-verificacao-da-autodeclaracao-2026-11-13/poc
```

No app, é a entrada `poc-verificacao-video` do `.claude/launch.json`. Abra
<http://localhost:8091/>. Para testar sem se gravar, marque **"Usar imagem de teste"** na tela
"Antes de gravar". É um vulto cinza animado, sem cor de pele, com som sintético.

**No celular**, a câmera exige contexto seguro:
- **Android**: Chrome com depuração USB e *port forwarding* (`chrome://inspect`). O celular abre
  `localhost:8091`, que conta como seguro.
- **iOS**: só por HTTPS. Pode ser um certificado local confiável no aparelho (por exemplo, `mkcert`)
  ou a VM de testes. Pôr a POC na VM é decisão do usuário.

## O que foi verificado (13/11/2026, Chromium 156 do painel do app, macOS, imagem de teste)

| # | Verificação | Resultado |
|---|---|---|
| V-1 | Prévia, medidor de som e oval fora da gravação | câmera 720×960 a 30 qps; microfone detectado; o oval é CSS sobre o `<video>` e o arquivo grava o `MediaStream` |
| V-2 | Gravação guiada, com 4 passos avançados pelo toque e marcas de tempo | 4 marcas gravadas; "Terminar a gravação" no último passo |
| V-3 | Formato | o Chromium 156 grava **MP4/H.264** (`avc1.42001f, mp4a.40.2`); `isTypeSupported` verdadeiro para os 6 formatos da lista |
| V-4 | Revisão sob a CSP | toca (`readyState 4`); **0 violações** |
| V-5 | **Sem `media-src blob:`** (cópia temporária da página, apagada depois) | a prévia continua (`MediaStream` não passa por `media-src`); **a revisão falha** com `MEDIA_ERR_SRC_NOT_SUPPORTED` (4) e a violação `media-src blob`. A exceção é necessária e suficiente |
| V-6 | Regravar | a tomada some (URL revogada); a trilha registra só a contagem |
| V-7 | Envio com queda simulada | interrompe na parte, retoma dela, e não do começo; resumo de cada parte e do todo |
| V-8 | Conferência de conteúdo | assinatura `ftyp` reconhecida como MP4; a duração no arquivo (4,8 s) bate com a medida |
| V-9 | Comprovante e o titular vê o próprio vídeo (R-24) | número, formato, roteiro e SHA-256; o vídeo toca no comprovante; a câmera se fecha depois do envio |
| V-10 | Mesa: abrir é ato | parecer recusado antes de abrir ("Abra o vídeo…"); 1 evento `VISUALIZAR_VIDEO_DA_VERIFICACAO` por abertura, com o resumo reconferido |
| V-11 | Saltos por passo, ±10 s e 0,5× | o passo 3 posiciona em 2,9 s (marca 0:02) |
| V-12 | Parecer: motivo obrigatório; pareceres alheios só depois do próprio | "Marque ao menos um motivo."; a deliberação só aparece após o registro |
| V-13 | Regras × cenários (R-4, R-11) | as 9 combinações dão o esperado; **nenhuma produz "não confirmada"** |
| V-14 | Menor de idade (R-22) | a opção do vídeo some e o aviso aparece |
| V-15 | Tela oculta no meio da gravação | a tomada é descartada, com "A gravação parou porque a tela saiu do navegador". Disparou **sem querer** duas vezes: a captura de tela do painel esconde a página por um instante |
| V-16 | Celular, 375×812 | página sem rolagem lateral (375 = 375); durante a gravação, "Próximo passo" termina em 663 px e "Parar e recomeçar" em 721 px, dentro da primeira tela |
| V-17 | Console | nenhum erro |

## Achados

- **A-1 · A exceção de CSP é uma linha, e só na página de gravação.** `media-src 'self' blob:`. A
  reprodução pela comissão, servida do próprio GPS, cabe no `'self'`. A exceção não precisa ir à
  política global.
- **A-2 · MP4 primeiro unifica o formato.** O Chromium atual já grava MP4/H.264, como o Safari.
  Com o MP4 no topo da lista, Chrome e Safari produzem o mesmo contêiner, que toca em qualquer
  navegador da comissão, e o WebM fica só para quem não grava MP4. Falta medir o Firefox.
- **A-3 · A interrupção por tela oculta é estrita, e precisa de medida em celular.** Ela descarta a
  tomada ao menor sumiço da página. É o que a R-13 pede ("tomada contínua"), mas falta saber o que,
  nos celulares, dispara `visibilitychange`: cortina de notificações, chamada recebida, bloqueio
  de tela. Se disparar demais, o candidato regrava sem entender por quê. A mensagem existe; a
  frequência é pergunta da matriz.
- **A-4 · O Wake Lock foi recusado no painel** (`NotAllowedError`, página sem foco). Num celular, a
  tela pode apagar no meio de um minuto de gravação. A mitigação já está no desenho: cada toque em
  "Próximo" reinicia o temporizador de tela. A matriz confirma.
- **A-5 · A taxa medida não vale para câmera real.** A imagem de teste é quase estática e saiu a
  57–65 kbit/s. O tamanho por minuto (o número que decide as partes de 8 MiB) só sai de uma câmera
  real, com gente se mexendo.
- **A-6 · Resumo e câmera pedem o mesmo contexto seguro.** O `crypto.subtle` e o `getUserMedia` só
  existem em HTTPS ou `localhost`. No GPS isso já é dado em produção; no desenvolvimento local,
  `localhost` basta.

## Matriz de navegadores

A primeira linha é a deste ambiente. As outras dependem de aparelho e de **uma pessoa gravando a si
mesma** (nunca um candidato), e o JSON da aba "Medição" preenche a linha. Ele não contém imagem.

| Navegador | Fonte | Formato gravado | MB/min | Duração no arquivo | Revisão toca | Tela oculta descarta? | Wake Lock | Leitor de tela |
|---|---|---|---|---|---|---|---|---|
| Chromium 156, macOS (painel do app) | sintética | MP4 avc1/mp4a | não representativo (A-5) | finita | sim | sim (V-15) | recusado (A-4) | não medido |
| Chrome, macOS/Windows | câmera | | | | | | | |
| Firefox, computador | câmera | | | | | | | |
| Chrome, Android | câmera | | | | | | | TalkBack: |
| Safari, iOS | câmera | | | | | | | VoiceOver: |

E, para a comissão: o vídeo gravado em cada linha **toca** no Chrome, no Firefox e no Safari do
computador?

**Critério de saída da entrega 0**: as quatro linhas com câmera preenchidas. O que não for viável
vira restrição escrita da entrega 5. Exemplo: "no iOS, só a partir da versão X".
