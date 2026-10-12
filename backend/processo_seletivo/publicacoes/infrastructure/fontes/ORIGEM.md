# Origem da fonte embutida no Edital

O documento do Edital embute a **Edital Sans**, Regular e Bold (069, D-002, FR-1380). Ela é um
subconjunto WinAnsi da **Liberation Sans 2.1.5**, gerado por `backend/scripts/gerar_subconjunto_da_fonte.py`.

## De onde veio

| | |
|---|---|
| Projeto | `liberationfonts/liberation-fonts`, release 2.1.5 (30/09/2021) |
| Arquivo baixado | `liberation-fonts-ttf-2.1.5.tar.gz`, 2.385.008 bytes |
| Endereço | <https://github.com/liberationfonts/liberation-fonts/files/7261482/liberation-fonts-ttf-2.1.5.tar.gz> |
| SHA-256 do pacote | `7191c669bf38899f73a2094ed00f7b800553364f90e2637010a69c0e268f25d0` |
| SHA-256 de `LiberationSans-Regular.ttf` | `76d04c18ea243f426b7de1f3ad208e927008f961dc5945e5aad352d0dfde8ee8` |
| SHA-256 de `LiberationSans-Bold.ttf` | `788abee4c806d660e8aee46689dd8540cd4bb98da03dcc9d171ce3efd99a9173` |
| Baixado em | 12/10/2026, com aprovação do responsável pelo produto |

## O que foi gerado

| Arquivo | SHA-256 | Bytes |
|---|---|---|
| `EditalSans-Regular.ttf` | `62b13299f160417649de8979ee1b72f5c276af2db2c3e9933d5e9054b4aa71e4` | 41132 |
| `EditalSans-Bold.ttf` | `465a6122bcd959c9a9a4f392cc67ecec886d28397019e4ef9d6cff6fd832508c` | 39608 |
| `EditalSans-Regular.ttf.zlib` | `0e5bb7cb264840f34216a022b72c4f6dc90423803eebe5a002b19ae5f6c0a469` | 25951 |
| `EditalSans-Bold.ttf.zlib` | `0c64e1441ce1315d27d47ebe11c717e00b5d7a3ab0740dc472328148cb4afd5b` | 25332 |

Os `.zlib` são o mesmo TTF comprimido uma vez, pelo roteiro: o PDF embute esse fluxo, e comprimir na
hora de compor faria os bytes do Edital dependerem da `zlib` da máquina.

O teste `tests/unit/publicacoes/test_fonte_embutida.py` confere estes resumos.

## A licença, verificada no arquivo distribuído

O `LICENSE` do pacote baixado diz: *"This Font Software is licensed under the SIL Open Font License,
Version 1.1."* O texto está aqui, em `LICENSE`, como a OFL exige que acompanhe a fonte.

**Os nomes reservados.** A mesma licença reserva os nomes "Liberation" (Red Hat) e "Arimo", "Tinos"
e "Cousine" (Google). O subconjunto é uma *versão modificada* no sentido da OFL — tem só os glifos do
WinAnsi —, e versão modificada não pode usar nome reservado. Por isso ele se chama **Edital Sans**
nos nomes da família, do estilo, completo e PostScript; o aviso de direitos autorais (nameID 0), a
marca (nameID 7) e a licença (nameID 13 e 14) de origem continuam no arquivo.

## Por que esta fonte

As métricas da Liberation Sans são as da Helvetica e da Arial nos caracteres que o compositor
conhece: a quebra de linha não muda de natureza (FR-1380). As únicas divergências estão onde a
tabela da Helvetica do `pdf.py` estava errada — "í", "ì", "î", "ï" e, no negrito, "ª" e "º"
(FR-1381). Embutida, ela acaba com a substituição do negrito no poppler (ED-14).

## Para regenerar

Só quando a fonte de origem mudar, e com o diff dos documentos revisado — os bytes de todo Edital
composto depois mudam. A partir de `backend/`, com o pacote extraído numa pasta:

```bash
uv run --no-project --with fonttools python scripts/gerar_subconjunto_da_fonte.py <pasta>
```
