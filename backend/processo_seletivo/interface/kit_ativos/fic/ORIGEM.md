# Origem dos ativos da família FIC (119, FR-3826, D-006, T047)

Tudo aqui vem dos arquivos de template da comunicação do Cefor, `Editais FIC/`, com três
apresentações — post, story e site —, de dez slides cada (oito de exemplo e dois "NÃO EDITE", com as
orientações). Nada foi desenhado pelo projeto.

**A imagem do banco é o fundo inteiro do slide** (P-1, resposta de 04/11/2026: "o mais próximo do
template possível"): o amarelo, o megafone, a ilustração e, no post e no story, o rodapé com os
perfis de rede (@ifescefor, Ifes Cefor) e a marca do Ifes vêm juntos. São quatro ilustrações, cada
uma com um arquivo por formato, o recorte que a comunicação fez para ele.

**Dois tratamentos, e só eles.** Feitos uma vez, com o Pillow, antes da redução:

1. **O contato desenhado saiu.** O post e o story trazem "Dúvidas? selecaoextensao.cefor@ifes.edu.br
   (27) 3198-0925 (seg. a sex. 8h às 16h)" no fundo. A área foi pintada com o amarelo liso do fundo
   (`#fbc502`): o contato da peça é o atendimento que a unidade registrou (FR-3810, FR-3820), e o
   desenhado afirmaria um canal que a ficha pode não ter, ou ter outro.
2. **A bolha branca saiu do fundo e voltou como ativo.** Ela muda de lugar de uma ilustração para a
   outra, e o número do Edital que fica dentro dela não pode mudar com a escolha da imagem
   (FR-3827). A bolha de cada fundo foi pintada com o amarelo, e `bolha.png` é o recorte de uma
   delas, posicionado no mesmo lugar em todas as peças de um formato.

A redução para o tamanho do formato (1080 × 1350, 1080 × 1920 e 1500 × 850) foi a última etapa, em
JPEG de qualidade 60: o amarelo liso comprime bem, e cada arquivo fica abaixo de 60 kB, longe dos
400 kB da FR-3826. O teste `tests/unit/kit/test_familias.py` confere o tamanho e o resumo.

**A licença não foi verificada.** As ilustrações 3D são de banco de imagens, escolhidas pela
comunicação; a decisão de adotá-las sem verificar a licença é do responsável pelo produto (P-1), e
fica registrada aqui e na spec.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `mesa-post.jpg` | `Editais FIC - Posts Intagram.pptx`, `ppt/media/image3.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `8e163b0d6393287ee42e43dcb165700986802994d3c9d8994e1538e42e8f2f1d` |
| `mesa-story.jpg` | `Editais FIC - Story Intagram.pptx`, `ppt/media/image2.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `b22e7aac752aa7a4b7408c021bd1760d8b09f852798b62b4de38eaf9207837e5` |
| `mesa-banner.jpg` | `Editais FIC - Site Cefor.pptx`, `ppt/media/image2.png`; bolha branca pintada com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `808489aaf2d1655a7fa70859452cdbf0146566501cc759f2a8c11657aa0745c7` |
| `prancheta-post.jpg` | `Editais FIC - Posts Intagram.pptx`, `ppt/media/image2.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `61646aca6ec1214ea58ddfe18f7c0b270d432581cfc3e2252a8b8da6b326cb0e` |
| `prancheta-story.jpg` | `Editais FIC - Story Intagram.pptx`, `ppt/media/image4.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `df976cc978490ed9f0187aa91b40f18006161baef59407b89ad942078f8da20a` |
| `prancheta-banner.jpg` | `Editais FIC - Site Cefor.pptx`, `ppt/media/image6.png`; bolha branca pintada com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `64f8f7b5e876271f51be2244c3787f93a412ab2a3d685560be2a1f31a3be1e4c` |
| `poltrona-post.jpg` | `Editais FIC - Posts Intagram.pptx`, `ppt/media/image5.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `2c3589750558ebd5a99bc8bafd0e58ee2c08e4b392d81c44320621359feb97a2` |
| `poltrona-story.jpg` | `Editais FIC - Story Intagram.pptx`, `ppt/media/image6.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `809d77f5cf7385f4a2459f15c5db115a3b9aae83bafa0644b80707f1b8bca568` |
| `poltrona-banner.jpg` | `Editais FIC - Site Cefor.pptx`, `ppt/media/image4.png`; bolha branca pintada com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `668a30004670dcffe27b4924f9e691c0cee95bad52c88d960f835a5c7cd1aec8` |
| `foguete-post.jpg` | `Editais FIC - Posts Intagram.pptx`, `ppt/media/image6.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `465f4e2b1c19ff704d23dbb36cbc77a19472a26bc8c365908974354abc4a1224` |
| `foguete-story.jpg` | `Editais FIC - Story Intagram.pptx`, `ppt/media/image5.png`; bolha branca e contato desenhado pintados com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `9323ab8db97c5d14e9dda3a028acb24dcd6936e5e612b3bf1ccc0925108075ab` |
| `foguete-banner.jpg` | `Editais FIC - Site Cefor.pptx`, `ppt/media/image3.png`; bolha branca pintada com o amarelo do fundo; JPEG qualidade 60 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `021aae9adfe93d17de7b70cd396113b707e6424215437960f1575a65f47e3bb0` |
| `balao.png` | `ppt/media/image1.png` dos três arquivos (o mesmo nos três), sem alteração | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `c20ef72a711ef5a591325e4e653179b6bab9afc36565dd3a9a5f892af8777c2c` |
| `bolha.png` | recorte da bolha de `Editais FIC - Posts Intagram.pptx`, `ppt/media/image2.png`, com a transparência calculada do amarelo para o branco | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `f731add4a099d480c1adb5fd111797a8eacaac27ac7b3ff940a851b31a0f574f` |
| `megafone.png` | `Editais FIC - Site Cefor.pptx`, `ppt/media/image5.png`, sem alteração | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `c6ce2da2331b878f4f0b3dae06fa2435c75b8538e6580d1a1675b52d1f72311d` |

Os resumos dos arquivos de origem:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais FIC - Posts Intagram.pptx` | `0a77ed321fc4ef59972d6b858b5f8ca1a0c5275268941740fd0b3edde31094b0` |
| `Editais FIC - Story Intagram.pptx` | `886dc631151d3df47ac264ce38ca946d2120ad9c3f4195b4e0ec34d43b5cdf9f` |
| `Editais FIC - Site Cefor.pptx` | `447f59d79f56ec9e34099f541e78f65c0f3de08f1423e713055565aeb1629b47` |
