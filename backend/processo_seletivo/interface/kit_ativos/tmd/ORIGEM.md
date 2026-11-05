# Origem dos ativos da família TMD (119, T052, FR-3826, EC-20)

A referência são os arquivos de template da comunicação do Cefor, `Editais TMD/`, com três
apresentações — post, story e site —, de um exemplo cada. **Os fundos daqui não vêm deles: são
desenho do projeto.**

**Por que desenho próprio.** O fundo dos slides é uma imagem só, com uma ilustração plana de banco —
uma pessoa diante de um tablet com uma aula em vídeo, a lâmpada, as folhas — cuja licença ninguém
conferiu. A T052 pede ilustração de licença conferida ou desenho próprio, simples, feito no código. Os
três fundos são desenhados por `backend/scripts/desenhar_fundo_do_tmd.py`, em SVG rasterizado pelo
`resvg-py` do projeto, só com formas geométricas: o roxo, o lilás da colina, o turquesa dos
asteriscos e o dourado do elo, lidos do pixel do fundo dos slides, e a mesma disposição — ilustração
no alto à direita, colina embaixo, a barra da chamada com o elo, e o rodapé. A ilustração (tablet,
vídeo, lâmpada) é um desenho novo, e não um traçado da do slide.

**O que entra de fora no desenho**: a marca `cefor-horizontal-branco.png` oficial, de `kit_ativos/`
(ver o `ORIGEM.md` de lá), só reduzida, e os perfis de rede "ifescefor" e "Ifes Cefor" escritos na
Inter negrito do kit (OFL). O banner, como o slide do site, não tem rodapé.

**Família sem banco de imagens** (EC-20): a tela não pede imagem, e a peça sai com o fundo fixo do
formato. Quando a comunicação trouxer uma ilustração de licença conferida (P-1), ela entra aqui,
redesenhada no mesmo roteiro ou no lugar dele, e a versão do template sobe.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `fundo-post.png` | desenho do projeto, `scripts/desenhar_fundo_do_tmd.py`, 1080 × 1350 | do projeto; a marca é a oficial do Cefor | aguarda a comunicação (SC-1135) | `042402bbfd6a749f937157da80d56be6728e859ccae4404617231dddf007c764` |
| `fundo-story.png` | desenho do projeto, `scripts/desenhar_fundo_do_tmd.py`, 1080 × 1920 | do projeto; a marca é a oficial do Cefor | aguarda a comunicação (SC-1135) | `4a43c5a0a44e6f0a161ea3428d241d7b655410c22dbc5ba5ec1968c093d838e6` |
| `fundo-banner.png` | desenho do projeto, `scripts/desenhar_fundo_do_tmd.py`, 1500 × 850 | do projeto | aguarda a comunicação (SC-1135) | `06adfd4812793ca7779beb577ce90832ec1d478bc66f8b6f79422a2ad8d643f7` |

Os resumos dos arquivos de referência da comunicação, de onde vieram as cores e as medidas:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais TMD - Posts Intagram.pptx` | `ad73c4ced3f9de88e9a0206889b18bfb84aad62976dd8db2f42a9dba0c3a933e` |
| `Editais TMD - Story Intagram.pptx` | `555f877a763d6b2c98788e33d6231f2e54179a8221622c1efd56c23705606679` |
| `Editais TMD - Site Cefor.pptx` | `3edb3ad387d490ba0b6e330b07b49e714d8a88e6a87f64ed19b5d871252ae7aa` |
