# Corpus da 070 — conteúdo publicado de três Editais simulados

Cópia de `docs/libras/editais/edital-{01,91,92}-2026/fonte/*.json`, feita em 12/10/2026 sobre a `main`
em `a79ce463` (`specs/070-fonte-de-consulta-do-edital/research.md`, `R-016`).

**Por que cópia, e não leitura de `docs/`.** O estudo de Libras é revisado por rodadas. Um teste da
fonte de consulta não pode mudar de resultado porque um documento de estudo foi revisto. Se o corpus
precisar mudar, a mudança é deliberada, nesta pasta, com os resumos abaixo atualizados.

**O que é cada arquivo.**

- `pubN-canonico.json`: os bytes canônicos do conteúdo da versão consolidada depois da publicação N.
  O resumo do arquivo é o `content_hash` que o PDF publicado imprime.
- `pubN-alteracoes.json`: as alterações da Retificação N, no formato do estudo: `path`, `op` e `novo`.
  `vigencia` nula quer dizer vigência imediata.

Os três foram publicados pelo fluxo real em 11/10/2026, num banco isolado:

- o 01/2026 pelo `seed_demo`;
- o 91/2026 e o 92/2026 pelos roteiros da auditoria do PDF (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`).

São **simulados**: marcam "DEMONSTRAÇÃO", e os dados de pessoas são fictícios. Os PDFs não entram:
a 070 não lê documento.

## SHA-256

| Arquivo | SHA-256 |
|---|---|
| `edital-01-2026/pub1-canonico.json` | `c29f09d938a8780677c8f764d5b8d954a0515647888bc9260106efa20eedacbb` |
| `edital-01-2026/pub2-alteracoes.json` | `e927ef14430501f199372066da0f2a1e6167a6b3ebdac363074ee5b8b1c60f9a` |
| `edital-01-2026/pub2-canonico.json` | `c05270a337024e047d7f6a5b2dd1bace47b4171bcd0d7bdff459844cf70a6329` |
| `edital-01-2026/pub3-alteracoes.json` | `3c57b035f7c1d276217df1c74ad1dfbeceddd1538a9fa23a0cb35122e0f3a053` |
| `edital-01-2026/pub3-canonico.json` | `f23684d2e41bfdaa9cf916ed900eacc23c43b74bbf636eff2418b631797bc008` |
| `edital-91-2026/pub1-canonico.json` | `083468eb97dfa5843555132992abdf88a6a2085bd14fb16e8a64551f1b8ee132` |
| `edital-91-2026/pub2-alteracoes.json` | `9cb7e3a3903efb43a9d25054e9912aa5f098bb7f60f9910eb4d6337b7907b587` |
| `edital-91-2026/pub2-canonico.json` | `d0186c039d8f02c4d9369be743a86926067e6001ec3fe09535d53134236c337c` |
| `edital-92-2026/pub1-canonico.json` | `34bc1a9f9a9f3de85933ca10fc2544c0bc39c19a34c94e9b1562b6fb1e68d2ca` |
| `edital-92-2026/pub2-alteracoes.json` | `e4260b3759636d150a278e2f99d84c6df618ae9e446d1ead35f01b1046017ee5` |
| `edital-92-2026/pub2-canonico.json` | `b695a0e1c0d80c634e6d038c900e8115adcf278693e6a3e954692e5521ea8495` |

`backend/tests/unit/duvidas/test_corpus.py` confere esses resumos.
