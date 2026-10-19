# Protótipo da 094 — prévia da classificação

**Não é a implementação.** É o protótipo navegável que a spec pede para avaliação, e fica fora de
`backend/processo_seletivo` de propósito (D-010): assim não entra nas varreduras, nos inventários e nos
guardiões do produto.

## Rodar

Entrada `previa-094` do `.claude/launch.json`, ou, de dentro de `backend/`:

```bash
uv run python ../specs/094-previa-da-classificacao/prototipo/servidor.py 8094
```

<http://localhost:8094/>. Sem banco, sem Django: o servidor é da biblioteca padrão e responde com a
mesma política de conteúdo da gestão.

## O que é real e o que é demonstrativo

| Real — o motor do produto, importado e chamado | Demonstrativo — marcado na tela |
|---|---|
| `combinacao.combinar` | os cenários e os candidatos fictícios (`previa.cenario`) |
| `desempate.ordenar` e `desempate.particiona_o_grupo` | a função extraída de `calcular_ordem` (`previa.preparar_universo`), esboço |
| `faixa.calcular` e `EmpateAtravessaOCorte` | a trajetória da partição (`previa.ordenar_com_trajetoria`), conferida contra `ordenar` a cada cálculo |
| `apuracao.titulares_iniciais` e `EmpateNaFronteiraDoAlvo` | as frases do painel e o cartão simplificado |
| | pesos, fatos e vagas editáveis — no produto vêm de outros passos |

Se a trajetória do esboço divergir de `ordenar`, o painel diz, em vermelho, que não deve ser lido.

## Arquivos

- `servidor.py` — rotas `/`, `/previa`, `/fechar`, `/estatico/…`, `/saude`.
- `previa.py` — cenários, esboço da extração, trajetória, corte e fronteira das vagas.
- `pagina.py` — o cartão, o painel e as frases.
- `estatico/` — a folha e o script de foco. Nenhum estilo ou script inline.
- `capturas/` — desktop e 375 px, validados em 19/10/2026.
