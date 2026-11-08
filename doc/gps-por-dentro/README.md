# GPS por Dentro

Abra [index.html](index.html) diretamente no navegador. Um único HTML contém estilos, interações,
dados, fontes conceituais e três capturas reais de referência. Não precisa de servidor, conexão,
conta ou instalação; pode copiar só o HTML para outro computador.

- Dez cenas interativas com os mesmos oito candidatos.
- Mapa e laboratório de 17 conceitos, com cenário alternativo de sorteio e empate no corte.
- Busca local e sete desafios com feedback, retorno e reinício.
- Nenhum dado real nem operação no GPS. Resultados fixos gerados pelas funções oficiais.

| Entrega | Arquivo |
|---|---|
| Inventário, fontes e divergências | [inventario.md](inventario.md) |
| Aplicativo | [index.html](index.html) |
| Roteiro pedagógico, regras e elenco | [roteiro-pedagogico.md](roteiro-pedagogico.md) |
| Evidências e limites de validação | [validacao.md](validacao.md), [capturas](capturas/) |
| Avaliação crítica e prioridades propostas | [avaliacao-critica.md](avaliacao-critica.md) |

## Manutenção e conferência

A execução do HTML não depende de Python ou Node. Eles são usados somente na manutenção:

```bash
backend/.venv/bin/python doc/gps-por-dentro/conferir_cenarios.py --conferir
node doc/gps-por-dentro/verificar_interface.cjs
```

`conferir_cenarios.py` importa funções puras do GPS, sem conectar a banco. Sem `--conferir`, regenera
`cenarios.json` e atualiza os estados embutidos no HTML; revise as hipóteses antes de aceitar mudanças.
`embutir_capturas.py` reembute as três referências do repositório, preservando legendas de origem.
`verificar_interface.cjs` verifica as composições sem navegador; a QA real está documentada à parte.

As fontes de manutenção ficam separadas para permitir conferência; não são dependências do HTML.
Os documentos de investigação são complementares e os links para eles pedem a pasta completa.
Plano e rastreabilidade da entrega: [spec 133](../../specs/133-guia-visual-conceitos/spec.md).
