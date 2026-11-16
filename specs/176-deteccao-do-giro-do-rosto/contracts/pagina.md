# Contrato: a página da gravação com a detecção

O que a `176` acrescenta à página da `174` ([contracts/telas.md da 174](../../174-polimento-da-verificacao-do-candidato/contracts/telas.md)).
Com a chave desligada, **nada** deste contrato aparece no HTML (SC-2751).

## O servidor

| O quê | Com a chave desligada | Com a chave ligada |
|---|---|---|
| `script-src` da gravação | `'self'` | `'self' 'wasm-unsafe-eval'` |
| demais diretivas, `Permissions-Policy` | as de hoje | as de hoje |
| `<script>` da página | `gravacao.js` | `deteccao.js` e `gravacao.js`, nesta ordem, ambos com `defer` |
| atributos de `[data-verificacao]` | os de hoje | mais `data-deteccao-motor`, `-carregador`, `-binario`, `-modelo` (endereços com `?v=`) |
| `data-giro` em `[data-passo]` | ausente | `esquerda` no perfil esquerdo, `direita` no perfil direito |
| `data-documento` em `[data-passo]` (emenda) | ausente | só no passo `documento` |
| rotas, corpos e respostas do envio | os da `166` | **os mesmos** (FR-8030) |

## O sinal do gesto (emenda de 15/11), com ou sem a chave

| O quê | Onde |
|---|---|
| `data-gesto` em `[data-passo]` | `documento`, `esquerda`, `direita`; ausente no passo de frente |
| `.gesto-do-passo` (`aria-hidden`) | sobre a prévia, só gravando; `.gesto-esquerda`, `.gesto-direita`, `.gesto-documento` |
| `data-gesto` e `data-confirmado` no palco | escritos por `gravacao.js`; a folha mostra o sinal do passo e o esconde quando visto |
| frases | "Sua esquerda", "Sua direita", "Mostre o documento ao lado do rosto" |

## Os ganchos do script

| Gancho | Em | Quem escreve | O que significa |
|---|---|---|---|
| `data-deteccao` | `[data-verificacao]` | `deteccao.js` | `carregando`, `pronta`, `simulada`, `indisponivel`, `recusada` (a pessoa escolheu o toque) ou `desligada` (orçamento) |
| `[data-aviso-deteccao]` | o topo de `.preparo-do-palco` | o template, `hidden` | a frase da FR-8004 e o botão `[data-so-tocando]` |
| `data-rosto` | `.oval` | `deteccao.js` | `fora` ou `dentro`; o traço muda nos dois |
| `[data-guia-do-oval]` | `.guia-do-oval` | `gravacao.js` | o texto muda com o `data-rosto` |
| `[data-confirmacao]` | dentro de `.instrucao-do-passo`, `hidden` | `gravacao.js` | "Documento visto" (emenda), "Perfil esquerdo visto", "Perfil direito visto" ou "Para o outro lado" |
| `[data-ajuda-deteccao]` | depois da lista do roteiro, `hidden` | o template | a frase de como os perfis avançam |

## As frases

| Onde | Frase |
|---|---|
| aviso, antes de começar | "A tela percebe quando você mostra o documento e quando vira o rosto, para passar sozinha aos passos seguintes. Ela não lê o documento. Isso acontece só neste aparelho: nada dessa leitura é enviado nem guardado." (revista pela emenda; antes, só o giro) |
| botão do aviso | "Prefiro avançar só tocando" |
| depois da escolha | "Combinado: você avança tocando em «Próximo»." |
| ajuda do roteiro | "O vídeo tem até {teto} minutos. No documento e nos dois perfis, a tela passa sozinha. Você também pode tocar em «Próximo», no seu tempo." (revista pela emenda) — no lugar da ajuda da `174`, que volta quando a detecção não está |
| guia do oval, fora | "Encaixe o rosto no oval. Ele não aparece no vídeo." (o de hoje) |
| guia do oval, dentro | "Rosto no oval. Ele não aparece no vídeo." |
| confirmação | "Documento visto" (emenda; aparece quando o documento entra, e o passo passa quando ele sai) · "Perfil esquerdo visto" · "Perfil direito visto" |
| lado oposto | "Para o outro lado" |
| passo de frente | "Estamos ouvindo você." (no selo, a mesma leitura da `174`) |
| anúncio, ao avançar pelo giro | "Perfil esquerdo visto. Passo 3 de 4: Perfil direito. {instrução}" |

## A interface de `deteccao.js`

`window.DeteccaoDoGiro` (e `module.exports`, para o teste):

- constantes `LIMIAR_DO_GIRO` (0,3), `INSTANTE_MANTIDO` (400), `CONFIRMACAO` (900), `INTERVALO` (150),
  `TETO_DA_LEITURA` (120), `LEITURAS_LENTAS` (5);
- `giroDosPontos(pontos)` → número, positivo à esquerda da pessoa, ou `null`;
- `caixaDosPontos(pontos)` → `{x, y, largura, altura}` normalizados;
- `rostoNoOval(caixa, quadro, palco, oval, espelhada)` → booleano;
- `avaliarGiro(leituras, lado, opcoes)` → `"esperando" | "outro-lado" | "visto"`;
- `avaliarDocumento(leituras, anterior, opcoes)` → `"esperando" | "sozinha" | "na-mao" | "visto"`, sobre
  leituras `{ms, rostos}` (emenda); o vigia avisa `aoGiro("na-mao")` e `aoGiro("visto")`;
- `Orcamento` com `registrar(ms)` → `true` enquanto cabe;
- `podeCarregar(ambiente)` → booleano (sem `WebAssembly`, com `saveData`, ou recusada → `false`);
- `Vigia(opcoes)`, um por página: `carregar()`, `observar(lado | "oval" | "documento" | null)`, `pausar()` (fora do
  palco: para de ler e esquece as leituras, e guarda o motor), `parar()` (solta tudo: a escolha de
  tocar, o orçamento, a falha de leitura e a saída da página), e os retornos `aoEstado`, `aoRosto` e
  `aoGiro`; `emGravacao()` impede o aquecimento com a tomada em curso; com `simulada`, não carrega
  o motor.

## A fala e o microfone (emenda de 15/11), com ou sem a chave

| O quê | Onde | O que significa |
|---|---|---|
| `[data-fala-do-passo]` (`.fala-do-passo`) | o primeiro filho de `.faixa-de-baixo`, só gravando | a frase do passo de frente, escrita por `gravacao.js` com `partesDaFrase`: o que está entre «aspas» em `<strong>`, nada acrescentado |
| `data-passo-da-fala` | no palco | escrito por `gravacao.js` no último passo; a folha esconde a frase do alto e mostra a de baixo |
| `.ultimo-passo` | no "Antes de gravar", depois do teto | "No último passo, você diz o seu nome e a frase da sua autodeclaração. Se preferir, mostre a frase escrita num papel, ou diga em Libras." |
| `.medidor-do-som` (`aria-hidden`) | no lugar do `<meter>`, no preparo | `.barra-do-som` com `[data-volume]` e a marca `[data-marca-do-volume]`, "volume bom" |
| `.microfone-do-selo` (`aria-hidden`) | na linha do selo, gravando | o ícone `microfone` e uma `.barra-do-som` com `[data-volume]` |

`window.GravacaoDoVideo` ganha `picoDasAmostras`, `nivelDoPico` (a régua da `174`), `fracaoDoMedidor`
(decibéis, de −48 a −6), `suavizarMedidor`, `MARCA_DO_VOLUME_BOM`, `LIMIAR_DA_FALA`, `partesDaFrase` e
`rostosDaImagemDeTeste`. A largura do volume é `transform: scaleX(…)`, e a posição da marca, `left`,
ambos pelo CSSOM.

