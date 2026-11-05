# Origem dos ativos da família Aperfeiçoamento (119, T050, FR-3826, D-006)

Tudo aqui vem dos arquivos de template da comunicação do Cefor, `Pós-graduação Aperfeiçoamento/`,
com três apresentações — post, story e site —, de cinco exemplos cada. Nada foi desenhado pelo
projeto.

**A imagem do banco é o fundo inteiro do slide** (P-1, resposta de 04/11/2026: "o mais próximo do
template possível"): a foto presa pelo clipe sobre o papel rasgado, o selo "PROCESSO SELETIVO", a fila
de pílulas, o botão com o contorno e o rodapé com os perfis de rede (@ifescefor, Ifes Cefor) e a marca
do Ifes vêm juntos. Cada foto tem um arquivo por formato, o recorte que a comunicação fez para ele. A
redução foi feita uma vez, com o `sips` do macOS (`sips -s format jpeg -s formatOptions 50 -z <altura>
<largura>`), para caber nos 400 kB da FR-3826; o teste `tests/unit/kit/test_familias.py` confere o
tamanho e o resumo. Os slides do site medem 1563 × 886 px, e o banner é reduzido a 1500 × 850
(`D-007`).

**O ativo da chamada é composição, e não recorte.** O botão verde e o contorno ao lado são do fundo; o
texto "SE INTERESSOU?" é uma caixa do slide, desenhada pelo PowerPoint. Os renders são as páginas do
PDF que o PowerPoint exportou de cada apresentação, rasterizadas no tamanho do formato
(`pdftoppm -png -scale-to-x <largura> -scale-to-y <altura>`). No post, o botão está numa altura em
cada foto (de 1108 a 1128 px), e o ativo o cobre por inteiro em qualquer uma: o miolo é o botão vazio
da foto de referência, com o texto do render colado no retângulo interno do botão, e a borda esmaece
sobre o azul liso. Coordenadas e esmaecimento estão em `scripts/compor_chamada_do_aperfeicoamento.py`.

**A licença não foi verificada.** As fotos são de banco de imagens, escolhidas pela comunicação; a
decisão de adotá-las sem verificar a licença é do responsável pelo produto (P-1), e fica registrada
aqui e na spec.

| Arquivo | Origem | Licença | Aprovação | SHA-256 |
|---|---|---|---|---|
| `blazer-post.jpg` | `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `ed8042b04ea467840f101a71676d34ddf0e7db766ec36e74dc6358daba103bf9` |
| `blazer-story.jpg` | `Pós Aperfeiçoamento - Story Intagram.pptx`, `ppt/media/image4.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `25476589859c4c7aa01692f6dfd2d434712f32c0ec975003a733d7e24d878031` |
| `blazer-banner.jpg` | `Editais de  Aperfeiçoamento   - Site Cefor.pptx`, `ppt/media/image5.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `25fc6f4f8acfb68fd910b5f4449390f51eb53c0f2b09d371d0edd0268d5c91bd` |
| `cachos-post.jpg` | `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `5a51cb36f1fa30c1eca1a238c0fc782440afce46af2a1ba31e78aee679ae7407` |
| `cachos-story.jpg` | `Pós Aperfeiçoamento - Story Intagram.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `3860a8a03db8541cab93fcbfaa4f68e36d96f8c0e269c772f89bd52e7d81d669` |
| `cachos-banner.jpg` | `Editais de  Aperfeiçoamento   - Site Cefor.pptx`, `ppt/media/image2.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `15d4fecb8b9a990d809c37936038bc7a1f162db9f23e16e06df21f82dcc33ba5` |
| `camisa-post.jpg` | `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `115f4870000598b86e19eee3b21f9872bf50592a02567747d33bd3a0e621b26f` |
| `camisa-story.jpg` | `Pós Aperfeiçoamento - Story Intagram.pptx`, `ppt/media/image5.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `b758c65bf2b634ca892f3a13dba0c61f156947f881624d8d721e196bdbce6067` |
| `camisa-banner.jpg` | `Editais de  Aperfeiçoamento   - Site Cefor.pptx`, `ppt/media/image4.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `2351d93728edd2b03374354cff5f61588eebc7026412d3f49286edc1d82d3b1b` |
| `fone-preto-post.jpg` | `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`, `ppt/media/image4.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `9d3376037aa8dce6693cc3743d8744707f96342cc0a0eea6124585ea3021a344` |
| `fone-preto-story.jpg` | `Pós Aperfeiçoamento - Story Intagram.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `c3697054dbf37a51bcc27714d7c85312fddd1830053045dbbba9516a041bc756` |
| `fone-preto-banner.jpg` | `Editais de  Aperfeiçoamento   - Site Cefor.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `bd8f8349239b7cd5c13fc1bc8391bd6047d1ff4c5d571279dda39394831ae383` |
| `fone-branco-post.jpg` | `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`, `ppt/media/image5.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `f2223e371a498bd96b974835399dfe8d01ee1f89ade0154dc775f5996b1bd1dc` |
| `fone-branco-story.jpg` | `Pós Aperfeiçoamento - Story Intagram.pptx`, `ppt/media/image1.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `0afc4ce741cb989aeab0ac67ed64481f09014e55dcc7ea2bff374c80b2475c30` |
| `fone-branco-banner.jpg` | `Editais de  Aperfeiçoamento   - Site Cefor.pptx`, `ppt/media/image3.png`; JPEG qualidade 50 no tamanho do formato | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `878080036bf04b246df59e533a46fc9a2956913d77b302b36bce02541c9127a3` |
| `chamada-post.png` | composição de `Editais Pós Aperfeiçoamento - Posts Intagram.pptx`: o botão vazio do fundo e o texto do botão de o render do slide 3, cujo fundo é `cachos-post.jpg`, por `scripts/compor_chamada_do_aperfeicoamento.py` | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `16409a2ed440ae97edf811a675d7eed6fc53b66ca9efc92a61e828e990ae59ee` |
| `chamada-story.png` | composição de `Pós Aperfeiçoamento - Story Intagram.pptx`: o botão vazio do fundo e o texto do botão de o render do slide 1, cujo fundo é `fone-branco-story.jpg`, por `scripts/compor_chamada_do_aperfeicoamento.py` | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `419f12c611b3d316e7262da3643b87b7739f66e688e1374265bdb26ae14b7b20` |
| `chamada-banner.png` | composição de `Editais de  Aperfeiçoamento   - Site Cefor.pptx`: o botão vazio do fundo e o texto do botão de o render do slide 1, cujo fundo é `fone-branco-banner.jpg`, por `scripts/compor_chamada_do_aperfeicoamento.py` | não verificada (P-1) | responsável pelo produto, 04/11/2026 | `e52d8188848db4a6821c8db7d452903d2999a7c9433a05f6a6106bee6ed8f2a4` |

Os resumos dos arquivos de origem:

| Arquivo da comunicação | SHA-256 |
|---|---|
| `Editais Pós Aperfeiçoamento - Posts Intagram.pptx` | `2aadcab4ff555d42a1e80095390eadd695f4961f594333a20ac6c0910098c809` |
| `Pós Aperfeiçoamento - Story Intagram.pptx` | `77ed1dc965361c59b1f819ddf75869b4c9cdafe7fb76db57d917274b1ae99a57` |
| `Editais de  Aperfeiçoamento   - Site Cefor.pptx` | `84899aef8d5702ebeaf7374283c004c235ffe38df5878f74ed3cc572d484e92a` |
| PDF do post exportado pelo PowerPoint | `27efcfe6573e27b0febac64fd5d4fba57ce86949c0512e0b624fd2c237a1adb2` |
| PDF do story exportado pelo PowerPoint | `efe35d1e6e3907df9be79519dc8d6ec1ff116f475ea99fac8bc4225fd10f8339` |
| PDF do site exportado pelo PowerPoint | `4635da5220d6e34782f6a06b62b95b58280e406de79275ba442e2ec2a2975ddf` |
