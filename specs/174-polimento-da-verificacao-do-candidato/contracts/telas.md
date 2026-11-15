# Contrato: as telas do candidato na verificação por vídeo

A forma de cada tela, na ordem do documento (que é a do leitor de tela e a do teclado), as frases e os
ganchos que o script lê. **O que não está aqui não muda**: as rotas, os corpos JSON e os códigos de
recusa são os de `specs/166-verificacao-por-video/contracts/`.

Convenções: `{etapa}` e `{modalidade}` são os nomes publicados; `{teto}` são os minutos do teto do
roteiro; `{data}` e `{hora}` vêm no fuso do sistema. A frase entre aspas é literal; o resto descreve.
"(166)" marca frase que já existe e só muda de lugar.

## O degrau no acompanhamento (FR-7856 a FR-7859)

Ordem dentro de "Sua situação", quando o vídeo pode ser gravado:

1. selo em pílula: ícone de relógio + "Falta um passo seu";
2. **"Prazo: até {data} às {hora}."**, em linha própria (sem fim de período, não aparece);
3. "Por quê": as linhas da `171`, sem mudança;
4. "O que fazer": "Você pode gravar um vídeo curto ou fazer a entrevista ao vivo. As duas formas valem
   igual." (171), sem o prazo no meio;
5. ação principal: **"Escolher entre vídeo e entrevista ao vivo"**;
6. a consequência da ausência e "No Edital, veja a etapa {etapa}." (171).

O selo das outras situações provisórias muda do mesmo jeito (D-008); o das registradas leva o ícone de
confirmação.

## A página da gravação

Cabeçalho comum a todas as telas (FR-7852, T-009):

- "Voltar ao acompanhamento", discreto, acima;
- `h1`: `{etapa}`;
- `ol.jornada-momentos`: "Preparar", "Gravar", "Conferir e enviar", com `aria-current="step"` no atual.
  Escolha, ao vivo, preparo e menor ficam em "Preparar"; o palco em "Gravar"; revisão e envio em
  "Conferir e enviar".

### `escolha` (FR-7860, FR-7861)

1. `h2` "Falta um passo seu";
2. "Você se inscreveu em {modalidade}, e quem se inscreve nela passa também por esta etapa." (sem
   modalidade: a frase da `171` para "a sua lista");
3. "Prazo: até {data} às {hora}." (se houver fim);
4. aviso informativo, se já há vídeo: o texto de substituição (166);
5. "**As duas formas valem igual.** Escolha a que for melhor para você." (166);
6. dois `article.forma`, mesmo tamanho:
   - **"Vídeo gravado agora"** — "Você grava pelo celular ou pelo computador, de onde estiver." · "O
     vídeo tem até {teto} minutos." · "Você assiste antes de enviar e pode gravar de novo." · botão
     "Gravar um vídeo curto" (`data-ir="acolhimento"`);
   - **"Entrevista ao vivo"** — "A comissão informa o dia, a hora e como participar." · "Você conversa
     com a comissão, presencialmente ou por vídeo, como o Edital disser." · "Você não precisa fazer nada
     agora." · botão "Prefiro entrevista ao vivo" (`data-ir="ao-vivo"`).

### `ao-vivo`, `menor`, `nao-consigo` (FR-7862)

Textos de hoje (166). Ação principal: "Voltar ao acompanhamento". Em `ao-vivo`, secundária: "Voltar à
escolha".

### `acolhimento` — "Antes de gravar" (FR-7863 a FR-7865)

1. `h2` "Antes de gravar";
2. `ul.preparo`, três itens, cada um com ícone:
   - "Um lugar claro, com luz de frente para o rosto."
   - "O rosto descoberto: sem óculos escuros, boné ou filtro."
   - "O seu documento de identidade com foto, em mãos."
3. "O vídeo tem até {teto} minutos. Não há pressa em nenhum passo." (166);
4. `section` "Quem vê o seu vídeo" (`h3`), com as quatro frases de hoje (166): a comissão olha só a
   aparência; só a comissão assiste, pelo sistema; a guarda; o encaminhamento não é reprovação;
5. `fieldset.maioridade` "Qual é a sua idade?", dois `label.opcao-grande` (166);
6. `p.recusa[data-erro-maioridade][hidden]` "Escolha uma das duas respostas." — visível só depois de
   "Continuar" sem resposta;
7. principal "Continuar" (`data-continuar-acolhimento`) — abre a câmera;
8. discreta "Voltar" (`data-ir="escolha"`).

### `palco` (FR-7866 a FR-7879)

Uma seção, `data-tela="palco"`, com `data-estado` = `preparo` | `gravando`. Dentro de
`.palco` (grade de uma célula):

| Camada | Preparo | Gravando |
|---|---|---|
| `video.previa[data-previa]` | sim | sim |
| `.oval` + "Encaixe o rosto no oval. Ele não aparece no vídeo." | sim | só o oval |
| faixa de cima: `[data-passo-rotulo]` "Passo N de 4", `[data-passo-titulo]`, `[data-passo-atual]` (instrução) | não | sim |
| `[data-selo]` "Gravando" + `[data-tempo]` "0:42 de 3:00" | não | sim |
| `[data-recomecar]` "Parar e recomeçar", canto de cima | não | sim |
| "Voltar" (`data-ir="acolhimento"`), canto de cima | sim | não |
| `[data-comecar]` "Começar a gravar", faixa de baixo | sim | não |
| `[data-proximo]` "Próximo" / "Terminar a gravação", faixa de baixo | não | sim |
| "Não consigo usar a câmera" (`data-ir="nao-consigo"`), faixa de baixo | sim | sim |

*Revisão da implementação (15/11, CI do #568)*: "Começar a gravar" e "Não consigo usar a câmera"
estavam no pé do painel do preparo, e no computador a altura dele, que muda com a fonte do sistema,
os empurrava para fora da tela. O gesto principal passou à faixa de baixo do vídeo, o mesmo lugar de
"Próximo"; o painel ficou só com a informação.

Fora da grade, no preparo (abaixo da prévia no computador; numa folha sobre a parte de baixo no
celular):

1. "O que você vai fazer": `ol.passos-do-roteiro` com os quatro **títulos** (o texto completo aparece
   passo a passo);
2. "Você se vê como num espelho. O vídeo enviado fica na posição normal, e o documento pode ser lido.";
3. `meter[data-nivel]` largo + `[data-estado-do-som]`: "Fale alguma coisa para testar o microfone." →
   "Estamos ouvindo você." / "Não encontramos o microfone. Você pode mostrar a frase escrita num papel.";
4. `[data-aviso-tela-acesa][hidden]`: "Mantenha a tela acesa: se ela apagar, a gravação para e você
   grava de novo.";
5. `[data-aviso-gravacao][hidden]`: o aviso do descarte (166).

Os dois avisos vêm no topo do painel, antes da lista. "Começar a gravar" cita a lista e o teto por
`aria-describedby`, porque vem antes deles na ordem do documento.

O anúncio ao leitor de tela, a cada passo: "Passo {N} de 4: {título}. {instrução}" (UX-875).

### `permissao`

Como hoje (166), com "Tentar de novo" como principal.

### `revisao` (FR-7880)

1. `h2` "Assista antes de enviar" (166);
2. `video.revisao[data-revisao]` no tamanho do palco;
3. `[data-dados-da-tomada]`: "Duração: 1 min 12 s. O envio vai usar cerca de 9,4 MB da sua internet.";
4. as três perguntas de autoconferência (166);
5. "**Só o vídeo que você enviar chega à comissão.** …" (166);
6. principal "Enviar este vídeo"; secundária "Gravar de novo".

### `envio` (FR-7881)

`progress` largo, `[data-estado-do-envio]` "Enviando… 45%", "Não feche esta página enquanto o envio não
terminar."; o resto como hoje (166).

## O comprovante (FR-7882 a FR-7885)

1. "Voltar ao acompanhamento"; `h1` `{etapa}`;
2. `.confirmacao-do-envio`: ícone de confirmação, `h2` **"Seu vídeo foi enviado"**, "Recebido em
   {data} às {hora}.";
3. se eliminado: a frase da eliminação (166), logo abaixo;
4. `h2` "E agora?", com o texto de hoje (166);
5. `h2` "Assistir ao vídeo que você enviou" (166), se não eliminado;
6. "Gravar outro vídeo", se a troca é permitida (166);
7. `h2` "Dados para conferência", `dl` em texto menor: "Número do envio", "Duração" (`1 min 12 s`),
   "Formato", "Código de conferência do arquivo (SHA-256)".

Na impressão: sem o reprodutor, sem os botões, numa folha.

## A situação sem gravação (FR-7886)

Mesma moldura da página da gravação; `h2` "Situação" e o texto do estado (166) como centro; "Ver o
comprovante" como principal quando há vídeo.

## Ganchos do script

Mantidos: `data-verificacao`, `data-envios`, `data-comprovante`, `data-roteiro`, `data-teto`,
`data-limite`, `data-parte`, `data-tela`, `data-ir`, `data-maioridade`, `data-erro-maioridade`,
`data-continuar-acolhimento`, `data-previa`, `data-nivel`, `data-sintetica`, `data-passos`,
`data-passo`, `data-texto`, `data-titulo`, `data-passo-atual`, `data-comecar`, `data-proximo`,
`data-recomecar`, `data-selo`, `data-tempo`, `data-aviso-gravacao`, `data-revisao`,
`data-dados-da-tomada`, `data-enviar`, `data-regravar`, `data-progresso`, `data-estado-do-envio`,
`data-erro-do-envio`, `data-tentar-de-novo`, `data-sugestao-ao-vivo`, `data-motivo-permissao`,
`data-como-liberar`, `data-abrir-camera` (só em `permissao`).

Saem: `data-previa-gravacao`, `data-ir-gravar`, `data-checagem-camera`, `data-passo-proximo`.

Novos: `data-estado` (no palco), `data-passo-rotulo`, `data-passo-titulo`, `data-estado-do-som`,
`data-aviso-tela-acesa`.

## Funções puras novas de `GravacaoDoVideo`

| Função | Entrada → saída | Teste |
|---|---|---|
| `rotuloDoPasso(indice, total)` | `(1, 4)` → `"Passo 2 de 4"` | `gravacao.test.js` |
| `aceitaAvanco(agora, ultimo)` | ms → `true` se `agora - ultimo >= 500` | idem |
| `megabytes(bytes)` | `9_856_000` → `"9,4"` | idem |
| `ouviuFala(niveis)` | amostras `{nivel, ms}` → `true` com nível ≥ 20 por ≥ 300 ms seguidos | idem |
| `duracaoPorExtenso(segundos)` | `72.3` → `"1 min 12 s"`; `45` → `"45 s"` | idem; o filtro do servidor tem o mesmo teste em Python |
