# Origem dos ativos da peça do kit de divulgação (111, FR-3432, D-010)

As marcas são as **oficiais**, baixadas da página de download de marcas do Ifes em 01/11/2026, e
reduzidas sem outra alteração. Nada aqui foi desenhado pelo projeto: o defeito M9 da análise de
12/10 foi uma marca inventada.

| Arquivo | Origem | Resumo do original (SHA-256) |
|---|---|---|
| `cefor-horizontal-branco.png` | `cefor/png/cefor-horizontal-branco.png` de [marca-ifes-cefor.zip][cefor] | `a4a95474ee9daacae72a981f4c985ad510bccef25cb753964093f4cd135aa61f` |
| `ifes-horizontal-branco.png` | `_ifes/png/ifes-horizontal-branco.png` de [marca-ifes.zip][ifes] | `123ddf0251a5087b0af035287947bb71506b9bfb6bfe4db416226a86fdff7253` |

Os pacotes baixados tinham os resumos `e80434d4…c6d267` (Cefor) e `3834b6e8…121a12` (Ifes). Os
resumos dos arquivos versionados estão em `kit_peca.py` (`MARCAS`), e o teste os confere.

**A redução.** O original tem 2835 × 1135 px e ~60–100 kB. A peça o desenha com 250 px de largura,
e o arquivo vai embutido em cada SVG exportado. Ele foi reduzido para 720 px de largura com o `sips`
do macOS (`sips -Z 720`), uma vez, e o resultado é o que está aqui. É o único tratamento: sem
recorte, sem mudança de cor, sem redesenho.

## O manual

[Manual de Aplicação da Marca Instituto Federal][manual], 3ª edição, 2015 (Portaria Setec/MEC nº 31,
de 15/09/2015). O que a peça segue dele:

- **Aplicação sobre fundos** (p. 19): sobre fundo escuro, a versão branca. A faixa da peça é o verde
  escuro dos tokens do GPS, e a marca é a `branco` do pacote, sem base branca.
- **Reserva de integridade** (p. 12): um módulo do símbolo livre em volta. A 250 px de largura, o
  módulo tem ~11 px, e a faixa deixa mais que isso em todos os lados.
- **Redução máxima** (p. 13): o símbolo nunca menor que 30 px. A 250 px de largura, o símbolo tem
  ~45 px de altura.
- **Usos incorretos** (p. 17): a marca não é rotacionada, distorcida, recolorida nem combinada com
  texto. A assinatura textual "SIGLA/Ifes" só aparece com a marca do Ifes, e do outro lado da faixa.
- **A marca da unidade** (FR-3432): o Cefor tem marca própria no pacote, e a peça a usa. Unidade sem
  marca versionada aqui recebe a do Ifes, com a sigla escrita. As marcas dos campi estão na mesma
  página, e entram quando a primeira unidade além do Cefor for divulgar.

## O que continua pendente

- **A aprovação do template com a marca, pela comunicação (SC-1054).** Até lá, a chave
  `KIT_DE_DIVULGACAO_PECA` fica desligada em produção (D-010).
- **A licença de uso.** A página de download não declara termos; a marca é de uso institucional do
  próprio Ifes, que é quem gera a peça. A comunicação confirma na aprovação.

[cefor]: https://www.ifes.edu.br/images/stories/files/Institucional/assessoria_comunicacao_social/marcas/marca-ifes-cefor.zip
[ifes]: https://www.ifes.edu.br/images/stories/files/Institucional/assessoria_comunicacao_social/marcas/marca-ifes.zip
[manual]: https://www.ifes.edu.br/images/stories/-publicacoes/comunicacao/manual-aplicacao-marca-IF-2015.pdf
