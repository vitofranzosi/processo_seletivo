# Envio dos documentos da convocação: lista de uma coluna e rodapé de envio — 12/11/2026

Polish visual sobre o botão de envio único (`doc/polish-envio-unico-2026-11-12/`), no mesmo PR
(#509). Nenhuma regra, view, projeção, endpoint ou comportamento de envio mudou: são o CSS da tela,
três parciais e a visibilidade do rodapé no `varios.js`.

## O problema

Os documentos ficavam em duas colunas de cartões de alturas diferentes, igualadas com espaço vazio, e
o resumo com o botão de envio numa caixa cinza de meia largura, à esquerda, embaixo — um quinto
cartão, desligado do conjunto. Muitos contêineres para uma operação simples.

## O que mudou

- **Uma coluna no bloco em que se envia**, em qualquer largura, com até 56rem: a ordem de
  preenchimento é de cima para baixo, e cada cartão tem a altura do que diz.
- **O envio é o rodapé da lista**: divisor, a mesma largura dos cartões, contagem e frase à esquerda
  e o botão à direita; no celular, empilhados, com o botão na largura toda. A caixa cinza saiu.
- **Cartões na altura do conteúdo** também em *O que você já apresentou*, que fica com duas colunas
  quando o envio não mora nele, mas na mesma largura do bloco de cima — as bordas se alinham.
- **Tudo enviado, só substituição**: o rodapé aparece só depois de escolher um arquivo, e a frase do
  topo fala de substituição, e não de "cada documento".
- **Um documento só**: a orientação do rodapé vazio fica no singular.

## O que ficou

- **"O que falta" continua "O que falta"**, e não "Documentos necessários". O título é da FR-3735 da
  `118`, e o bloco mostra só o que falta: o recebido desce para *O que você já apresentou*.
  "Documentos necessários" diria que a lista é a de todos os documentos, e ela deixa de ser depois do
  primeiro envio. Se o título deve mudar, é uma revisão da `118`, para decisão do usuário.
- **"Falta enviar."** é o texto da FR-3746 da `118` para o pendente, e continua; com arquivo
  escolhido, ele já sai de vista (polish anterior).
- **"Remover a escolha"**, e não "Remover seleção": é o texto da UX-503 da `150`.

## Capturas

`‹estado›-‹largura›-‹antes|depois›.jpg`. "Antes" é o PR #509 antes deste polish. Todos os estados
foram capturados a 390, 768, 1280 e 1440 px; ficam no repositório os de 390 e 1280, e o estado 3
também a 768 e 1440.

| Estado | Arquivo |
|---|---|
| 1. Nenhum arquivo selecionado | `01-nenhum` |
| 2. Um selecionado | `02-um` |
| 3. Dois de quatro | `03-dois-de-quatro` |
| 4. Todos selecionados | `04-todos` |
| 5. Envio parcial concluído | `05-envio-parcial` |
| 6 e 7. Todos recebidos, aguardando conferência | `06-todos-recebidos-aguardando` |
| 8. Correção solicitada, sem e com escolha | `08-correcao`, `08b-correcao-escolhida` |
| 9. Um documento só | `09-um-documento` |
| 10. Seis documentos, descrições longas | `10-muitos-documentos` |

Nenhuma rolagem horizontal em nenhuma largura (o roteiro de captura conferia `scrollWidth`).
