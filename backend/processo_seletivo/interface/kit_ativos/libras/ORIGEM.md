# Origem dos ativos da família Libras (119, T048, FR-3826, D-006)

Tudo aqui vem dos arquivos de template da comunicação do Cefor, `Editais Libras/`, com três
apresentações — post, story e site —, de dois exemplos cada. Nada foi desenhado pelo projeto.

**A imagem do banco é o fundo inteiro do slide** (P-1, resposta de 04/11/2026: "o mais próximo do
template possível"): a foto recortada em círculo com o contorno preto, o ícone das mãos, os traços que
ladeiam a chamada e, no post e no story, o rodapé com os perfis de rede (@ifescefor, Ifes Cefor) e a
marca do Ifes vêm juntos. Nenhum desses fundos traz texto que a peça precise trocar: os textos dos
slides são caixas do PowerPoint, e a peça os escreve a partir da ficha. Cada foto tem um arquivo por
formato, o recorte que a comunicação fez para ele. A redução foi feita uma vez, com o `sips` do macOS
(`sips -s format jpeg -s formatOptions 50 -z <altura> <largura>`), para caber nos 400 kB da FR-3826;
o teste `tests/unit/kit/test_familias.py` confere o tamanho e o resumo. Os slides do site medem
1563 × 886 px, e o banner é reduzido a 1500 × 850 (`D-007`).

**A família não tem ativo fixo**: sem balão e sem botão, a chamada fica direto sobre o amarelo, entre
os traços do fundo.

**A licença não foi verificada.** As fotos são de banco de imagens, escolhidas pela comunicação; a
decisão de adotá-las sem verificar a licença é do responsável pelo produto (P-1), e fica registrada
aqui e na spec.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `grupo-post.jpg` | `Editais Libras - Posts Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 em 1080 × 1350 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `1c9064fa09ee18c5e59dac2ed5e40a0c449facc5d6552380b5975bcb1aa2168f` |
| `grupo-story.jpg` | `Editais Libras - Story Intagram.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 em 1080 × 1920 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `44f4bd5a0f4c5ae4b058c4cfa8789ab481526da6fd63fe47761a4d537ab69a90` |
| `grupo-banner.jpg` | `Editais Libras - Site Cefor.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 em 1500 × 850 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `d0590a7f5803ab23421c0fbb26605620ffdd79672a47cb4b2d0ff7c3593a1399` |
| `sinal-post.jpg` | `Editais Libras - Posts Intagram.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 em 1080 × 1350 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `b1de16299b13dd2248295279c7e47d807e10908911809bafb96ce561807ade8d` |
| `sinal-story.jpg` | `Editais Libras - Story Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 em 1080 × 1920 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `47a4d0935e15d0e5f0d132c16eb6eee1c51194d45a13a7c077ef09dea6a67674` |
| `sinal-banner.jpg` | `Editais Libras - Site Cefor.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 em 1500 × 850 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `59de29d4d97b3518d41074213c1aed62a24b4c035a59c9deb7a6465284ce3bb9` |

Os resumos dos arquivos de origem:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais Libras - Posts Intagram.pptx` | `cbc6cbef33e1655b335116971a4c35ead014b67c80ac12ae9aec1f897d45eb3e` |
| `Editais Libras - Story Intagram.pptx` | `c1971d24fb68e29204894387bfc7a0e42972251d41e50adf7a99029e3c6d58ba` |
| `Editais Libras - Site Cefor.pptx` | `105afd749da605b9d7484e64bd4c867baaf23c9ffb89a9eb17a3d09271e91da7` |
