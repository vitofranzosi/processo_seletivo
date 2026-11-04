# Verificação do motor da peça (T024, D-007)

**Data**: 01/11/2026. **Objeto**: `resvg-py` 0.5.0 (PyPI, 24/08/2026), que embute o `resvg` 0.48.

**Resultado**: aprovado nos sete itens da D-007. O item 2 vale com uma ressalva: a execução no Linux é
a do CI, porque não há imagem de produção versionada nem Docker na máquina da verificação.

**Aprovado pelo usuário em 01/11 (P-4).** O `resvg-py==0.5.0` é dependência de execução, em
`dependencies` do `pyproject.toml`, travada no `uv.lock`. A alternativa da D-007, o CairoSVG, foi
posta ao lado e preterida: pede a `libcairo2` no sistema e acha a fonte pelo nome, nas fontes
instaladas, e a peça perderia a garantia de sair com a Edital Sans. A peça continua desligada em
produção pela chave `KIT_DE_DIVULGACAO_PECA` até a aprovação do template (SC-1054).

## 1. Licença

- **`resvg-py`**: MIT. O metadado do PyPI não declara licença; quem a declara é o repositório
  (`baseplate-admin/resvg-py`): `license = "MIT"` no `Cargo.toml` da versão 0.5.0, e `LICENSE` MIT.
- **Dependências Python transitivas**: nenhuma (`requires_dist` vazio).
- **Dependências Rust, ligadas estaticamente**: 75 crates do registro no `Cargo.lock` da tag
  `0.5.0`. A licença de cada uma, na versão travada, foi conferida no crates.io:

  | Licença | Crates |
  |---|---|
  | MIT, Apache-2.0 ou ambas, com ou sem Zlib/Unlicense/0BSD como alternativa | 69 |
  | BSD-3-Clause | 2 (`tiny-skia`, `tiny-skia-path`) |
  | BSD-2-Clause | 1 (`arrayref`) |
  | Zlib | 1 (`slotmap`) |
  | (MIT ou Apache-2.0) e Unicode-3.0 | 1 (`unicode-ident`) |
  | Apache-2.0 com exceção LLVM | 1 (`target-lexicon`, de compilação, fora do binário) |

  Todas são permissivas, e nenhuma é copyleft. As BSD pedem a nota de copyright na redistribuição
  do binário; o sistema não redistribui o binário, e o instala do PyPI.

## 2. Linux de implantação

- **Wheels**: o PyPI publica `cp310-abi3` para `manylinux_2_17` e `musllinux_1_2`, em `x86_64` e
  `aarch64` (além de armv7l, ppc64le, s390x e i686). A ABI estável cobre o Python 3.13 do projeto.
- **Imagem**: a de desenvolvimento (`python:3.13-slim-bookworm`, glibc 2.36) cabe no
  `manylinux_2_17`, e o instala com as demais dependências. Nenhuma biblioteca de sistema é pedida — o
  resvg não usa cairo, freetype nem fontconfig.
- **Execução**: o CI (`ubuntu-latest`) o instala com as demais dependências e roda
  `tests/unit/kit/test_svg.py`, que gera o PNG duas vezes e exige os mesmos bytes. **A imagem de
  produção não é versionada**, e a verificação nela fica para quem a monta, com o mesmo teste.

## 3. Fontes e caracteres

- O PNG sai **só** das fontes do Edital (`EditalSans-Regular.ttf` e `-Bold.ttf`), passadas por
  arquivo, com `skip_system_fonts=True`. Um glifo que faltasse não seria completado pela fonte da
  máquina.
- Uma peça com título de prova — "Curso de Pós-graduação — Informática na Educação: módulo nº 2 –
  “turma” ‘A’ ç ã õ é ê í ó ú ü º ª" — desenhou cada caractere, inclusive "º", "ª", "–", "—" e as
  aspas curvas. A captura foi conferida a olho.
- O que a fonte não tem é recusado **antes** do rasterizador, nomeando o caractere (FR-3430): a
  peça usa a `grafia` do Edital, e o teste `test_caractere_sem_grafia_recusa_nomeando` o prova.

## 4. Segurança

- Nenhum recurso externo é resolvido: o SVG não tem `href` fora de `data:` (a marca vai em
  `data:image/png`), e a chamada não passa `resources_dir`. O teste
  `test_nenhum_recurso_fora_de_data` confere o arquivo.
- A entrada é sempre o SVG que o compositor gerou, com cada valor escapado como nó de texto
  (`test_valor_entra_escapado_como_no_de_texto`). Nenhum SVG de quem pede chega ao rasterizador.

## 5. Reprodutibilidade

- **Mac** (arm64, macOS 26.6, Python 3.13.14): 20 gerações seguidas da mesma ficha, um resumo só
  (`59df9d60…`).
- **Linux**: o mesmo, pelo teste do item 2, no CI. A igualdade entre o PNG do Mac e o do Linux não
  é exigida (D-007): o que a FR-3438 exige é a mesma peça no ambiente de implantação, e o SVG,
  esse sim, é idêntico em qualquer um.

## 6. Lote pequeno

20 gerações seguidas (composição + rasterização), no Mac acima, com a peça de quatro polos e o selo
de prorrogação:

```text
67, 58, 57, 58, 58, 58, 57, 57, 58, 58, 57, 58, 57, 57, 58, 57, 57, 57, 57, 57 ms
mediana 57 ms, máximo 67 ms (a primeira, que carrega as fontes)
```

A prévia na tela é um PNG por abertura, e a exportação, um por clique: dezenas de milissegundos não
pedem fila nem cache.

## 7. Versão fixada

`resvg-py==0.5.0` em `dependencies` do `backend/pyproject.toml`, travada no `backend/uv.lock`. Igual,
e não intervalo: outra versão do resvg pode mudar o antisserrilhado, e o PNG deixaria de ser o mesmo
entre duas implantações.

## 8. A tela com prévia e o ZIP, num lote de 20 (T032, SC-1057)

**Data**: 04/11/2026, com o incremento C. **Onde**: o Mac do item 5, `runserver` em desenvolvimento
(`DEBUG` ligado, um processo), PostgreSQL local, banco com o corpus da `070` publicado por
`scripts/publicar_corpus_do_piloto.py`. **Não é o ambiente de implantação**: a imagem de produção
continua sem versão (item 2), e a SC-1057 só se fecha quando a medição se repetir lá, com o mesmo
roteiro.

**Roteiro**: 20 rodadas seguidas, como Comunicação, no 91/2026 com a Retificação nº 1 (quatro polos),
pelo host público `kit.127.0.0.1.nip.io` — em `localhost` não há peça (FR-3447). Cada rodada abre a
tela, pede a prévia com a impressão lida dela e exporta o ZIP com o mesmo formulário, por `curl`,
medindo o `time_total` de cada resposta.

| Resposta | Mediana | Máximo | Status |
|---|---|---|---|
| Tela do kit | 20 ms | 32 ms (a primeira) | 200 nas 20 |
| Prévia PNG | 83 ms | 110 ms | 200 nas 20 |
| ZIP completo (sete arquivos, 328 KB) | 91 ms | 104 ms | 200 nas 20 |

A tela com a prévia, somadas, fica abaixo de 150 ms em toda rodada, e o ZIP, abaixo de 110 ms — uma
ordem de grandeza abaixo dos 2 s.

**Determinismo no lote**: os 20 ZIPs têm resumos diferentes, como a FR-3438 prevê — o manifesto, a
ficha e as notas dizem o instante da geração. Dentro deles, a peça é uma só: o PNG, o SVG e o texto
alternativo têm o mesmo resumo nos 20. Duas montagens no **mesmo** instante de referência dão o
mesmo ZIP, byte a byte (`tests/integration/kit/test_pacote.py`, e a galeria confere de novo em cada
cenário).
