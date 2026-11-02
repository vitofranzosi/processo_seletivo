# Verificação do motor da peça (T024, D-007)

**Data**: 01/11/2026. **Objeto**: `resvg-py` 0.5.0 (PyPI, 24/08/2026), que embute o `resvg` 0.48.

**Resultado**: aprovado nos sete itens da D-007. O item 2 vale com uma ressalva: a execução no Linux é
a do CI, porque não há imagem de produção versionada nem Docker na máquina da verificação.

**A decisão de adotá-lo é do usuário (P-4).** Até lá, a dependência fica num grupo opcional,
`peca`, no `pyproject.toml`, com a versão exata travada no `uv.lock`. A produção não instala o grupo,
e a chave `KIT_DE_DIVULGACAO_PECA` fica desligada lá. Para aprovar, a linha desce para
`dependencies`; para reprovar, a alternativa da D-007 é o CairoSVG.

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
  `manylinux_2_17`, e passa a instalar o grupo `peca`. Nenhuma biblioteca de sistema é pedida — o
  resvg não usa cairo, freetype nem fontconfig.
- **Execução**: o CI (`ubuntu-latest`) passa a instalar o grupo `peca` e roda
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

`resvg-py==0.5.0` no grupo `peca` do `backend/pyproject.toml`, travada no `backend/uv.lock`. Igual,
e não intervalo: outra versão do resvg pode mudar o antisserrilhado, e o PNG deixaria de ser o mesmo
entre duas implantações.
