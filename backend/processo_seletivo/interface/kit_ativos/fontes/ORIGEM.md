# Origem das fontes da peça do kit de divulgação (119, FR-3823, FR-3826, D-005)

Só fontes livres, sob a SIL Open Font License 1.1, e só subconjuntos que cobrem o repertório que a
`grafia` deixa chegar à peça (o WinAnsi imprimível). O rasterizador recebe estes arquivos e nenhum
outro: sem fonte do sistema, o PNG é o mesmo em qualquer máquina.

**O formato do registro.** Uma linha por arquivo, com o arquivo, a família tipográfica que o SVG
declara, o peso, a licença, a origem e o resumo SHA-256 do arquivo versionado. O teste
`tests/unit/kit/test_fontes_do_kit.py` lê a tabela e confere cada resumo contra o arquivo e contra
`kit_fontes.FONTES`; uma fonte registrada no código sem linha aqui, ou com outro resumo, reprova a
suíte. A fonte de uma família da comunicação entra nesta pasta, com o texto da licença ao lado e o
roteiro que gerou o subconjunto nomeado na origem.

| Arquivo | Família tipográfica | Peso | Licença | Origem | SHA-256 |
|---|---|---|---|---|---|
| `EditalSans-Regular.ttf` | Edital Sans | 400 | SIL OFL 1.1 | a fonte do Edital, lida no lugar: `publicacoes/infrastructure/fontes/` (069; origem e licença no `ORIGEM.md` de lá) | `62b13299f160417649de8979ee1b72f5c276af2db2c3e9933d5e9054b4aa71e4` |
| `EditalSans-Bold.ttf` | Edital Sans | 700 | SIL OFL 1.1 | a fonte do Edital, lida no lugar: `publicacoes/infrastructure/fontes/` (069; origem e licença no `ORIGEM.md` de lá) | `465a6122bcd959c9a9a4f392cc67ecec886d28397019e4ef9d6cff6fd832508c` |
| `Poppins-Regular.ttf` | Poppins | 400 | SIL OFL 1.1 | a Poppins de `google/fonts`, `ofl/poppins/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Poppins-OFL.txt` (original `7e65201e9b79…`) | `1a28e1d7124696a93c1e5894aff6dc0ca74c72c71777ed8fb8c747c2a657a3aa` |
| `Poppins-SemiBold.ttf` | Poppins | 600 | SIL OFL 1.1 | a Poppins de `google/fonts`, `ofl/poppins/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Poppins-OFL.txt` (original `d3bf1bdaf055…`) | `fefe0b3d545ead98fb66a28b5f23fc9b570d5eeb025c11fe3ae0252531892a7e` |
| `Poppins-Bold.ttf` | Poppins | 700 | SIL OFL 1.1 | a Poppins de `google/fonts`, `ofl/poppins/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Poppins-OFL.txt` (original `983676516167…`) | `7422528506b3264a11d167a0de0e757a322ded7c08f4fca6df4a7d43d02951f5` |
| `ArchivoBlack-Regular.ttf` | Archivo Black | 400 | SIL OFL 1.1 | a Archivo Black de `google/fonts`, `ofl/archivoblack/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `ArchivoBlack-OFL.txt` (original `dd9a89a019b4…`) | `24efaface31f64b28d2e34a09753230ef00181f1fe1188bf1e15c9522b426e8a` |
| `BarlowSemiCondensed-Medium.ttf` | Barlow Semi Condensed | 500 | SIL OFL 1.1 | a Barlow Semi Condensed de `google/fonts`, `ofl/barlowsemicondensed/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `BarlowSemiCondensed-OFL.txt` (original `4998b693a190…`) | `feeb1c5417579e1b9e5b2e5f8a0bfc6a7e9f84fac02b947a9354890285c21cac` |
| `BarlowSemiCondensed-Bold.ttf` | Barlow Semi Condensed | 700 | SIL OFL 1.1 | a Barlow Semi Condensed de `google/fonts`, `ofl/barlowsemicondensed/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `BarlowSemiCondensed-OFL.txt` (original `5bd6757e459a…`) | `6e904ce4579c543817016f540d27bb8bfbf706d7aac8d1eccaedd5721dca0cda` |
| `SpaceMono-Bold.ttf` | Space Mono | 700 | SIL OFL 1.1 | a Space Mono de `google/fonts`, `ofl/spacemono/` (commit `bbda7253`), baixada em 04/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `SpaceMono-OFL.txt` (original `405e73d41afb…`) | `81c793fc957300ca0521c18f7ebd2ca3f751c373182ceafcfc63cd171c1447d5` |
| `Unbounded-Regular.ttf` | Unbounded | 400 | SIL OFL 1.1 | a Unbounded de `google/fonts`, `ofl/unbounded/Unbounded[wght].ttf` (commit `bbda7253`, original `323b511be380…`), baixada em 04/11/2026; instância estática em `wght` 400 e subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Unbounded-OFL.txt` | `94c048a78a9b3ff3023dd970d1ca93c5c9918c32acd3c2f1948b2d41bfc3aba2` |
| `Lexend-ExtraBold.ttf` | Lexend | 800 | SIL OFL 1.1 | a Lexend de `google/fonts`, `ofl/lexend/Lexend[wght].ttf` (commit `bbda7253`, original `3add53e641fb…`), baixada em 04/11/2026; instância estática em `wght` 800 e subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Lexend-OFL.txt` | `64c5421403046c7f6f61db724c6d897a5369c303a466de5ad84f7a7d2e518268` |
| `Unbounded-Bold.ttf` | Unbounded | 700 | SIL OFL 1.1 | a Unbounded de `google/fonts`, `ofl/unbounded/Unbounded[wght].ttf` (commit `bbda7253`, original `323b511be380…`), baixada em 05/11/2026; instância estática em `wght` 700 e subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Unbounded-OFL.txt` | `28bb0d3b70521e03d5856a0f09c0a46949ddb439d0e4f5fd3947c3a1c56157e3` |
| `Inter-Light.ttf` | Inter | 300 | SIL OFL 1.1 | a Inter 4.1 da release oficial de `rsms/inter` (`https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip`, SHA-256 `9883fdd4a49d…`), `extras/ttf/Inter-Light.ttf` (original `164414f0aacb…`), baixada em 05/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Inter-OFL.txt` | `f7dd17c00ffc680f1c282ac65aefb926d25ace556cfa5378e0cbbd7c79956757` |
| `Inter-Regular.ttf` | Inter | 400 | SIL OFL 1.1 | a Inter 4.1 da release oficial de `rsms/inter` (`https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip`, SHA-256 `9883fdd4a49d…`), `extras/ttf/Inter-Regular.ttf` (original `40d692fce188…`), baixada em 05/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Inter-OFL.txt` | `dbacf55135637df6fb3cf41a991befb60e757413b515691c208cfdc993a95b31` |
| `Inter-Bold.ttf` | Inter | 700 | SIL OFL 1.1 | a Inter 4.1 da release oficial de `rsms/inter` (`https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip`, SHA-256 `9883fdd4a49d…`), `extras/ttf/Inter-Bold.ttf` (original `288316099b1e…`), baixada em 05/11/2026; subconjunto WinAnsi por `scripts/gerar_subconjunto_do_kit.py`; licença em `Inter-OFL.txt` | `42b065a835ac5c595f397be754a2ab209fce80aefc9ed2a0d6dc3ddbcbe601b4` |

**Por que a Edital Sans não é copiada para cá.** É a fonte da peça Institucional desde a `111`, e a
peça mede com ela exatamente o que o Edital mede. Duas cópias do mesmo arquivo poderiam divergir em
silêncio; uma só, com o resumo conferido nos dois registros, não.

**A Poppins (Pós Lato Sensu).** Os PPTX da comunicação embutem a Poppins comprimida em MicroType
Express, que o projeto não descomprime; a original veio do repositório oficial do Google Fonts, com a
aprovação do responsável pelo produto (04/11/2026). A OFL da Poppins não reserva nome, e o
subconjunto mantém o nome da família. Sem `kern` nem `GPOS`: o compositor mede pelo avanço de cada
glifo, e o rasterizador desenha o mesmo.

**As fontes da FIC.** Os PPTX da comunicação (`Editais FIC/`) embutem Archivo Black, Barlow Semi
Condensed (regular, médio e negrito) e Space Mono, também em MicroType Express; as originais vieram
do mesmo commit do `google/fonts` que a Poppins. Nenhuma das três licenças reserva nome, e os
subconjuntos mantêm o nome das famílias. Entram só os pesos que a peça desenha: a Archivo Black no
título, a Barlow Semi Condensed média no corpo e a negrita no destaque, e a Space Mono negrita no
número do Edital e na faixa da prorrogação (o papel `rotulo`). A Space Mono não mapeia o hífen condicional (U+00AD), que o WinAnsi tem: o
roteiro o aponta para o glifo do hífen (U+002D), e é a única alteração do desenho de origem.

**A Unbounded e a Lexend (Aperfeiçoamento).** Os arquivos da comunicação pedem a Unbounded no peso
regular, na lista dos cursos, e a Lexend ExtraBold, no cabeçalho. O Google Fonts só as publica
variáveis; o roteiro fixa o eixo `wght` antes do subconjunto (`gerar_subconjunto_do_kit.py <origem>
<destino> <peso>`), e o arquivo versionado é estático, com um avanço por glifo. A OFL da Unbounded
não reserva nome; a da Lexend reserva "RevReading Lexend", e não "Lexend", que o subconjunto
mantém.

**A Unbounded não desenha o micro (U+00B5)**, em nenhum peso da origem. O projeto não desenha glifo:
a lacuna fica declarada em `kit_fontes.FONTES` (`sem_grafia`), o teste confere que ela é a única, e
a peça cujo texto a pedir numa caixa em Unbounded é recusada nomeando o caractere e a fonte
(FR-3823, EC-13).

**A Inter, no lugar da Helvetica Neue (Libras, Internos e TMD).** Os arquivos da comunicação pedem a
Helvetica Neue, que é proprietária: não se versiona nem se embute no SVG exportado. A P-2 foi
respondida em 04/11/2026 ("escolha a mais próxima possível") e, em 05/11/2026, o responsável pelo
produto decidiu pela substituta livre; a escolhida é a **Inter** (`rsms/inter`), uma grotesca
neo-humanista de desenho próximo, com os mesmos pesos que os templates usam — leve (TMD), regular e
negrito (Libras e Internos), sem itálico. Veio da release oficial 4.1, fixada pela versão e pelo
resumo do ZIP, e não do Google Fonts, que publica outra compilação. A OFL da Inter não reserva nome,
e os subconjuntos mantêm "Inter". As três cobrem o WinAnsi inteiro — «º», «ª», «–», «—», as aspas
curvas e todos os acentos —, sem lacuna declarada. A leve entra já com a Libras, que não a usa, para
que Internos e TMD não precisem tocar nesta pasta.

**O negrito da Unbounded (Libras).** As informações do slide de Libras — número e prazo — estão em
Unbounded negrito; a instância é a do mesmo arquivo variável da regular, em `wght` 700, e herda a
mesma lacuna do micro (U+00B5).
