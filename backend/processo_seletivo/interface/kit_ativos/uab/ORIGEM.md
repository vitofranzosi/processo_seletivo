# Origem dos ativos da família UAB/bolsista (119, FR-3826, D-006, T049)

Tudo aqui vem dos arquivos de template da comunicação do Cefor, `Editais UAB/`, com três
apresentações — post, story e site —, de cinco exemplos cada. Nada foi desenhado pelo projeto.

**A imagem do banco é o fundo inteiro do slide** (P-1, resposta de 04/11/2026: "o mais próximo do
template possível"): o fundo ondulado, a foto, o rabisco, o endereço do Cefor, a linha e o rodapé com
os perfis de rede (@ifescefor, Ifes Cefor) e a marca do Ifes vêm juntos. Cada foto tem um arquivo por
formato, o recorte que a comunicação fez para ele. A redução foi feita uma vez, com o `sips` do macOS
(`sips -s format jpeg -s formatOptions 50 -z <altura> <largura>`), para caber nos 400 kB da
FR-3826; o teste `tests/unit/kit/test_familias.py` confere o tamanho e o resumo. O banner sai do
arquivo de 2500 × 1417 do site, reduzido a 1500 × 850.

**Entram dois dos cinco exemplos**: os de fundo claro com o rabisco magenta (slides 1 e 2 de cada
apresentação). O de rabisco verde (slide 3) pediria a chamada em verde, e o do slide 1 em rosa
`#ff2e63`: nenhum dos dois passa o contraste AA sobre o fundo (3,0:1), e a peça usa o magenta
`#bf247a` do slide 2 nos dois fundos. Os slides 4 e 5, de foto no alto e fundo escuro ou mostarda,
são outro desenho — texto noutra posição e noutra cor —, e entrariam como outro template.

**A licença não foi verificada.** As fotos são de banco de imagens, escolhidas pela comunicação; a
decisão de adotá-las sem verificar a licença é do responsável pelo produto (P-1), e fica registrada
aqui e na spec.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `atendente-post.jpg` | `Editais UAB - Posts Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `990840de22f388547e2d65375b1311c2b15ad41fa9698eed5f3ce389257e8489` |
| `atendente-story.jpg` | `Editais UAB - Story Intagram.pptx`, `ppt/media/image4.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `9bce5e0af6b8426d5376d9686393e310d8cf2d52b32c16ea3a232b6e4da0a42d` |
| `atendente-banner.jpg` | `Editais UAB - Site Cefor.pptx`, `ppt/media/image5.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `2ff49c9c18cdae56875bb139aa981fb506a0fed14befbf88ad311ef4ee4258b1` |
| `escritorio-post.jpg` | `Editais UAB - Posts Intagram.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `9869e8aa1e71a11d257d5feab78d08f8710ae7bc3124653799a00197e155faf0` |
| `escritorio-story.jpg` | `Editais UAB - Story Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `4401ce54f86d5fec374f260707deed1d06276839dbbd636675226dd7acf14a3a` |
| `escritorio-banner.jpg` | `Editais UAB - Site Cefor.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `707358a6e0c1496f2ab8608a2550c6758391cdba190d3860cbf6ef6478a4e7f1` |

Os resumos dos arquivos de origem:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais UAB - Posts Intagram.pptx` | `5b0a48f2e73055e34d29a6b60a7201abfdc157f1bf98d172bd21189cc10dba4a` |
| `Editais UAB - Story Intagram.pptx` | `7b10b4408d34adddb7d0b9a557beb362f25b6d741377b117758e77fb140cc2f9` |
| `Editais UAB - Site Cefor.pptx` | `c60c927533c6cf3f93e347514d105c37e1da0824dbaeff03ecf63f81b06c2054` |
