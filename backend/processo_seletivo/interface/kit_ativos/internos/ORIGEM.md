# Origem dos ativos da família Internos (119, T051, FR-3826, D-006)

Tudo aqui vem dos arquivos de template da comunicação do Cefor, `Editais Internos/`, com três
apresentações — post, story e site —, de quatro slides cada: uma arte para servidores e outra para
alunos, cada uma com o slide de orientação e um exemplo. Nada foi desenhado pelo projeto.

**A imagem do banco é o fundo inteiro do slide** (P-1, resposta de 04/11/2026: "o mais próximo do
template possível"): as três fotos recortadas em losango com o contorno verde, o losango verde-claro,
as listras e as faixas de verde mais claro e, no post e no story, o rodapé com os perfis de rede
(@ifescefor, Ifes Cefor) e a marca do Ifes vêm juntos. Nenhum desses fundos traz texto que a peça
precise trocar: os textos dos slides são caixas do PowerPoint, e a peça os escreve a partir da
ficha. As duas artes diferem só nas fotos, e cada uma é uma imagem do banco; o público (servidores
ou estudantes) é a variante, escolhida à parte. Cada arte tem um arquivo por formato, o recorte que a
comunicação fez para ele. A redução foi feita uma vez, com o `sips` do macOS
(`sips -s format jpeg -s formatOptions 50 -z <altura> <largura>`), para caber nos 400 kB da FR-3826;
o teste `tests/unit/kit/test_familias.py` confere o tamanho e o resumo. Os slides do site medem
1563 × 886 px, e o banner é reduzido a 1500 × 850 (`D-007`).

**A família não tem ativo fixo**: sem balão e sem botão, todo texto fica direto sobre o verde escuro.

**A licença não foi verificada.** As fotos são de banco de imagens, escolhidas pela comunicação; a
decisão de adotá-las sem verificar a licença é do responsável pelo produto (P-1), e fica registrada
aqui e na spec. A liberação em produção espera a conferência.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `servidores-post.jpg` | `Editais Internos - Posts Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 em 1080 × 1350 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `ce0cb4aa10fef8ec87e3d38ab0437ac6452fd682409217a3823550221bd61dd6` |
| `servidores-story.jpg` | `Editais Internos - Story Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 em 1080 × 1920 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `183aeabb05eb97e996eb139aa5565d808c3449923250b9b1b1a256d7b39eed19` |
| `servidores-banner.jpg` | `Editais Internos - Site Cefor.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 em 1500 × 850 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `115cf684b64149c03cc8a38f106a0cb86b107767d5bd3ead7a731fe2246f6778` |
| `estudantes-post.jpg` | `Editais Internos - Posts Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 em 1080 × 1350 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `ea892c6e6a410b625abfdac6ca644d8a5151d6bbabc5c8f5c0a8d1945e8d8774` |
| `estudantes-story.jpg` | `Editais Internos - Story Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 em 1080 × 1920 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `6c5358323a9ba61a9c862e6c36f9e090aece711c7d3560eb3f050fbfc29e657b` |
| `estudantes-banner.jpg` | `Editais Internos - Site Cefor.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 em 1500 × 850 | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `d779e646dfc1ba21f46c675072bf2c8d88daaa113e387f352b30c6623a42bb31` |

Os resumos dos arquivos de origem:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais Internos - Posts Intagram.pptx` | `f25bd96bc67a662cf0c47d6a5c2f348d3de0a92c5a4e7766ff009f5325e89a08` |
| `Editais Internos - Story Intagram.pptx` | `bed4568f8ff4eb0fbb6eea5943e2cf11b531125ec2d4951f83d96d69dfcfa5fd` |
| `Editais Internos - Site Cefor.pptx` | `b6a61cee7ea120990db4c74f2510623232448117db4b7956ae9981c2f6d1ec57` |
