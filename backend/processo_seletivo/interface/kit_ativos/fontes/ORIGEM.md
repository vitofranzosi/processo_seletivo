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

**Por que a Edital Sans não é copiada para cá.** É a fonte da peça Institucional desde a `111`, e a
peça mede com ela exatamente o que o Edital mede. Duas cópias do mesmo arquivo poderiam divergir em
silêncio; uma só, com o resumo conferido nos dois registros, não.

**A Poppins (Pós Lato Sensu).** Os PPTX da comunicação embutem a Poppins comprimida em MicroType
Express, que o projeto não descomprime; a original veio do repositório oficial do Google Fonts, com a
aprovação do responsável pelo produto (04/11/2026). A OFL da Poppins não reserva nome, e o
subconjunto mantém o nome da família. Sem `kern` nem `GPOS`: o compositor mede pelo avanço de cada
glifo, e o rasterizador desenha o mesmo.
