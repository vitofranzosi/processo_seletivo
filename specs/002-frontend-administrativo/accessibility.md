# Verificação de acessibilidade — SC-003 e SC-009

Executada em 29/08/2026 sobre a interface em `/gestao/`, com dados do `seed_demo`.

A spec exige eMAG 3.1 **e** WCAG 2.1 AA, valendo a norma mais restritiva em cada ponto.

## Como foi verificado

- **axe-core 4.13.0**, regras `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, em 11 telas, no
  navegador, com viewport de 1280×900.
- **Travessia por teclado** com teclas reais, registrando a sequência de foco.
- **Cálculo de contraste** sobre os pares de cor que as telas produzem, incluindo estados que
  o verificador não alcança (`:hover`).

As 11 telas: lista, identificação, detalhe do Processo, detalhe do Edital, trilha de
auditoria, retificação, as quatro etapas do assistente, confirmação de ato do Edital e
confirmação de ato do Processo — esta última no estado recusado, que tem paleta própria.

## Resultado

**Zero violações** ao fim, contra quatro encontradas e corrigidas.

### 1. Contraste insuficiente em três combinações (WCAG 1.4.3, AA)

`--verde:#15803d` servia a dois papéis com exigências opostas: preencher, onde precisa
contrastar com texto branco, e escrever, onde precisa contrastar com fundos claros. Como
preenchimento passava (5,01:1 com o branco); como texto sobre fundos tingidos, não:

| Onde | Sobre | Antes | Depois |
|---|---|---|---|
| "ETAPA ATUAL" no assistente | `--verde-claro` | 4,45:1 | 5,62:1 |
| Link do Edital pendente na recusa | `--vermelho-fundo` | 4,28:1 | 5,41:1 |
| `.acao` no `:hover` | `--verde-claro` | 4,45:1 | 5,62:1 |

O terceiro não foi encontrado pelo axe: verificador automatizado não avalia estados de
interação. Apareceu no cálculo dos pares.

Corrigido separando os papéis em dois tokens: `--verde` preenche, `--verde-texto:#146c37`
escreve. O novo passa em todas as superfícies da paleta, com folga de 5,3:1 a 6,3:1.

Removido `--cinza:#6c757d`, declarado e nunca usado: daria 4,04:1 sobre `--cinza-fundo`, e
um token que reprova esperando por quem o use é armadilha.

### 2. O link de salto movia a rolagem, não o foco (WCAG 2.4.1, A)

"Pular para o conteúdo" existia e era o primeiro elemento focalizável, mas `<main>` não podia
receber foco. Ativar o link rolava a página e deixava o foco no `BODY`; a tabulação seguinte
voltava ao cabeçalho — exatamente o que o link existe para pular.

O axe aprova esse caso: ele confere que o link e o alvo existem, não o que acontece ao ativar.

Corrigido com `tabindex="-1"` no `<main>`. Verificado: ativar o link leva o foco a
`MAIN#conteudo`, e a tabulação seguinte cai dentro do conteúdo.

### 3. Foco perdido ao remover uma linha (WCAG 2.4.3, A)

O botão "Remover" sai do documento junto com a linha que remove. O foco ia para o `BODY` — de
volta ao topo, com o formulário inteiro para retravessar.

Corrigido: o foco vai para a linha remanescente, ou para "Acrescentar" quando não sobra
nenhuma.

### 4. Linha nova ficava atrás do ponto de foco (WCAG 2.4.3, A)

O HTMX insere a linha **antes** do botão que a criou. Quem acrescentava um Perfil e tabulava
para frente ia para "Salvar rascunho", pulando o que acabara de criar.

Corrigido: o foco vai para o primeiro campo da linha inserida.

## O que passou sem ressalva

Ordem de tabulação coerente com a ordem visual, sem armadilha e sem `tabindex` positivo;
indicador de foco visível (contorno de 3px); um `<h1>` por tela; `lang="pt-BR"`; todos os
campos com rótulo associado; todos os controles em elementos nativos — nenhum `<div>` com
`onclick`, nenhuma âncora sem `href`.

## Limite desta verificação

**A ativação por teclado não foi verificada em execução.** As teclas sintéticas da ferramenta
usada movem o foco, mas não acionam controles: `Enter` sobre um `<a href>` nativo não navegou,
o que não acontece em navegador real. Confirmado por controle, e por isso não afirmado.

O que sustenta a ativação é a marcação ser nativa, e isso está verificado e preso em teste:
`Enter` e `Espaço` acionam `<button>` e `<a href>` por conta do navegador.

**Leitor de tela não foi executado.** NVDA ou VoiceOver com uma pessoa usuária real
continua pendente, e nenhuma verificação automatizada substitui isso — nem o axe, que cobre
por volta de um terço dos critérios da norma.

## O que ficou preso no repositório

`tests/interface/test_acessibilidade.py`:

- contraste de 17 pares de cor, incluindo os de `:hover`, contra o mínimo de 4,5:1;
- o alvo do link de salto precisa poder receber foco;
- todo controle interativo em elemento nativo, sem âncora sem `href` e sem `tabindex` positivo.

Os três foram verificados revertendo cada correção; todos falham sem ela.

O reposicionamento do foco depois das trocas do HTMX é comportamento de navegador e não está
coberto por teste automatizado — foi verificado manualmente, e os quatro casos (acrescentar,
acrescentar o segundo, remover uma, remover todas) estão descritos acima.
