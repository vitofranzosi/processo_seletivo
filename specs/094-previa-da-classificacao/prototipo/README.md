# Protótipo da 094 — prévia da classificação

**Terceira versão, de 19/10/2026.** O painel abre na **jornada do Perfil** — as Etapas com os nomes
cadastrados e os dois marcos, na ordem do Edital, cada ponto dizendo se é simulado, se só quem chega é
calculado, se não é calculado aqui ou se é indeterminado (`jornada.py`). O simulador da segunda versão
é o detalhe do marco, a um clique. As capturas estão em `capturas/v3/`, e o que a prévia simula, e o
que não, em [`../variaveis-simuladas.md`](../variaveis-simuladas.md).

**Segunda versão, de 19/10/2026.** A primeira demonstrava o algoritmo; esta começa pela consequência —
manchete, fluxo classificação → corte → Etapa seguinte, apuração das vagas como hipótese, a fronteira, os
empates lado a lado — e usa por padrão uma **população estável**, que não muda quando a regra muda, com
o quadro "O que mudou". A comparação está em [`comparacao-v1-v2.md`](comparacao-v1-v2.md), e as capturas
das duas versões em `capturas/v1/` e `capturas/v2/`.

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
| `combinacao.combinar` | a população estável e os casos-limite (`previa.populacao_estavel`, `previa.cenario`) |
| `desempate.ordenar` e `desempate.particiona_o_grupo` | a função extraída de `calcular_ordem` (`previa.preparar_universo`), esboço |
| `faixa.calcular` e `EmpateAtravessaOCorte` | a trajetória da partição (`previa.ordenar_com_trajetoria`), conferida contra `ordenar` a cada cálculo |
| `apuracao.titulares_iniciais` e `EmpateNaFronteiraDoAlvo` | as frases do painel, o "o que mudou" (`previa.estado`, `previa.comparar`) e o cartão simplificado |
| | pesos, fatos e vagas editáveis — no produto vêm de outros passos |

Se a trajetória do esboço divergir de `ordenar`, o painel diz, em vermelho, que não deve ser lido.

## Arquivos

- `servidor.py` — rotas `/`, `/previa`, `/fechar`, `/estatico/…`, `/saude`.
- `previa.py` — população estável, casos-limite, esboço da extração, trajetória, corte, fronteira das
  vagas, consequências e o estado comparável.
- `pagina.py` — os dois cartões, o painel (jornada e detalhe) e as frases.
- `jornada.py` — os pontos da jornada do Perfil, derivados da configuração, sem cálculo.
- `estatico/` — a folha e o script de foco. Nenhum estilo ou script inline.
- `capturas/v1/`, `capturas/v2/` e `capturas/v3/` — desktop e 375 px das três versões, validados em
  19/10/2026.
- `comparacao-v1-v2.md` — os três cenários de comparação e as cinco perguntas.
