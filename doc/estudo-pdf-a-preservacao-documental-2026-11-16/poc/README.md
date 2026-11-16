# POC — PDF/A no GPS (16/11/2026)

Prova de conceito do [estudo](../../estudo-pdf-a-preservacao-documental-2026-11-16.md). **Nada aqui
é código do GPS**, e nada roda na suíte: são roteiros descartáveis, executados em contêiner sem
rede, sobre amostras sintéticas (nenhum dado pessoal real) e sobre PDFs que o próprio GPS gera a
partir dos cenários congelados da auditoria de 08/10.

## Ferramentas medidas

| Ferramenta | Versão | Onde |
|---|---|---|
| Ghostscript | 10.00.0 (Debian bookworm) | imagem `poc-pdfa` (`Dockerfile`) |
| qpdf / pikepdf | 11.3.0 / 9.x | idem — só para inspecionar e para simular a geração direta |
| pyHanko | 0.29 | idem — assinatura PAdES de teste, certificado autoassinado (não é ICP-Brasil) |
| veraPDF | 1.30.4 | imagem oficial `verapdf/cli` |

## Como repetir

```bash
cd doc/estudo-pdf-a-preservacao-documental-2026-11-16/poc
docker build -t poc-pdfa .
mkdir -p amostras saida
# PDFs do GPS (do backend, com o venv do projeto):
(cd ../../../backend && .venv/bin/python ../doc/estudo-pdf-a-preservacao-documental-2026-11-16/poc/gerar_amostras_do_gps.py "$OLDPWD/amostras")
cp ../../../backend/tests/contract/fixtures/comprovante_v1.pdf amostras/I2-comprovante-gps.pdf
cp ../../../backend/tests/contract/fixtures/divulgacao_v1.pdf amostras/I3-divulgacao-gps.pdf
cp ../../estudo-relatorio-de-execucao-do-edital-2026-10-24/modernizacao/relatorio-61-2026-emitido-pelo-sistema.pdf amostras/I4-relatorio-gps.pdf
# Amostras sintéticas, assinatura de teste, conversão e medidas:
./no_conteiner.sh poc-pdfa "python gerar_amostras.py /poc/amostras && python assinar.py amostras/C1b-textual-fonte-embutida.pdf amostras/C4-assinado.pdf && python converter.py && python direto.py"
```

A validação roda na imagem do veraPDF (`/opt/verapdf/verapdf --flavour 2b --format json …`), e
`resumir.py` monta a tabela de `resultados/resumo.txt`.

**Duas armadilhas já pagas.** O `no_conteiner.sh` passa os arquivos por `tar` porque o Colima não
monta `/tmp`. E o Ghostscript procura um `PDFA_def.ps` passado sem caminho **na biblioteca dele
antes da pasta corrente**: o da distribuição aponta para um `srgb.icc` relativo, falha sob
`-dSAFER`, imprime "PDF/A processing aborted" — e sai com código 0. Passe o caminho absoluto.

## Resultados

- `resultados/conversao.json` — por amostra: resumo, inspeção, tempo do Ghostscript, tamanho,
  semelhança de texto extraído, % de pixels diferentes a 72 dpi, estado da assinatura.
- `resultados/verapdf-convertidos-2b.json` — o veraPDF sobre os convertidos.
- `resultados/verapdf-geracao-direta.json` — o veraPDF sobre os PDFs do GPS com os quatro
  acréscimos da geração direta.
- `resultados/resumo.txt` — a tabela e as regras que cada original do GPS descumpre.
