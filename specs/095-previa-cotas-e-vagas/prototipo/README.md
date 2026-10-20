# Protótipo da 095 — reprodução no motor oficial

**De cálculo, e não de tela** (D-008). O protótipo navegável é o da `094`, no PR #316; esta spec é um
PR só com a fatia 2, e estender aquele aqui exigiria copiá-lo ou depender de um PR aberto. A extensão
visual é a T030, depois do merge do #316.

## Rodar

De dentro de `backend/`:

```bash
uv run python ../specs/095-previa-cotas-e-vagas/prototipo/reproducao.py
```

Sem banco, sem Django. Imprime, em Markdown, uma tabela por cenário: por recorte, o universo, a faixa,
quantas posições da faixa são de quem ocupa pela ampla, quantos ficaram além, as quatro quantidades e a
quantidade que a reversão cederia. As tabelas da R-001 saem daqui.

## O que é real e o que é esboço

| Real — o motor do produto, importado e chamado | Esboço — marcado no código |
|---|---|
| `universo_classificavel.preparar` com recorte | `ocupantes_pela_ampla`, que reproduz `selectors.ocupantes_da_ampla` sem banco |
| `desempate.ordenar`, `faixa.calcular` | `ha_quem_ocupar`, que reproduz `movimento.ha_quem_ocupar` sem banco |
| `apuracao.apurar`, `titulares_iniciais`, `ocupantes` | as vagas por recorte num dicionário, no lugar de `linha_do_quadro` sobre o snapshot |
| `reversao.quantidade_a_reverter` | as populações |

Os dois esboços são as funções que a T004 e a T005 extraem (D-005); até lá, divergência entre eles e o
original é defeito deste roteiro, e não do produto.
