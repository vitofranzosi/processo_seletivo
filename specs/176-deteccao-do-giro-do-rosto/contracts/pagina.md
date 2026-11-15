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
| rotas, corpos e respostas do envio | os da `166` | **os mesmos** (FR-8030) |

## Os ganchos do script

| Gancho | Em | Quem escreve | O que significa |
|---|---|---|---|
| `data-deteccao` | `[data-verificacao]` | `deteccao.js` | `carregando`, `pronta`, `simulada`, `indisponivel`, `recusada` (a pessoa escolheu o toque) ou `desligada` (orçamento) |
| `[data-aviso-deteccao]` | o topo de `.preparo-do-palco` | o template, `hidden` | a frase da FR-8004 e o botão `[data-so-tocando]` |
| `data-rosto` | `.oval` | `deteccao.js` | `fora` ou `dentro`; o traço muda nos dois |
| `[data-guia-do-oval]` | `.guia-do-oval` | `gravacao.js` | o texto muda com o `data-rosto` |
| `[data-confirmacao]` | dentro de `.instrucao-do-passo`, `hidden` | `gravacao.js` | "Perfil esquerdo visto", "Perfil direito visto" ou "Para o outro lado" |
| `[data-ajuda-deteccao]` | depois da lista do roteiro, `hidden` | o template | a frase de como os perfis avançam |

## As frases

| Onde | Frase |
|---|---|
| aviso, antes de começar | "A tela acompanha o giro do seu rosto para passar sozinha aos passos seguintes. Isso acontece só neste aparelho: nada dessa leitura é enviado nem guardado." |
| botão do aviso | "Prefiro avançar só tocando" |
| depois da escolha | "Combinado: você avança tocando em «Próximo»." |
| ajuda do roteiro | "O vídeo tem até {teto} minutos. Nos dois perfis, a tela passa sozinha quando vê o giro. Você também pode tocar em «Próximo», no seu tempo." — no lugar da ajuda da `174`, que volta quando a detecção não está |
| guia do oval, fora | "Encaixe o rosto no oval. Ele não aparece no vídeo." (o de hoje) |
| guia do oval, dentro | "Rosto no oval. Ele não aparece no vídeo." |
| confirmação | "Perfil esquerdo visto" · "Perfil direito visto" |
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
- `Orcamento` com `registrar(ms)` → `true` enquanto cabe;
- `podeCarregar(ambiente)` → booleano (sem `WebAssembly`, com `saveData`, ou recusada → `false`);
- `Vigia(opcoes)`: `iniciar(video, palco)`, `observar(lado | "oval" | null)`, `parar()`, e os retornos
  `aoRosto(dentro)`, `aoGiro(estado)`; com `simulada: () => giro`, não carrega o motor.
