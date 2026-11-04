# Verificação: Templates de Divulgação por Família e Formato

## Templates aprovados (FR-3834, SC-1135)

A aprovação nomeia exatamente uma versão e um resumo. `tests/unit/kit/test_familias.py` confere que
cada linha desta tabela tem o resumo que o código fixa em `RESUMOS`; a liberação no ambiente
(`KIT_DE_DIVULGACAO_TEMPLATES`) nomeia a mesma versão e o mesmo resumo curto.

| Template | Versão | Resumo curto | Quem aprovou | Data |
|---|---|---|---|---|
| pos-lato-sensu/post · 1 | 1 | `bfcb25490b8e` | responsável pelo produto, por adoção (P-4) | 04/11/2026 |
| pos-lato-sensu/story · 1 | 1 | `91137d4ddd46` | responsável pelo produto, por adoção (P-4) | 04/11/2026 |
| pos-lato-sensu/banner · 1 | 1 | `1badbdf0cb93` | responsável pelo produto, por adoção (P-4) | 04/11/2026 |

**Por adoção, e não sobre a galeria.** A resposta à P-4, em 04/11/2026, foi "apenas adote o
template": a aprovação da comunicação sobre a galeria (SC-1135) foi dispensada pelo responsável
pelo produto, e a adoção dele é o registro. A galeria continua gerada por
`scripts/galeria_do_kit.py --familia pos-lato-sensu`, como prova visual de cada versão.

**A liberação em produção** continua da operação, pela configuração:

```text
KIT_DE_DIVULGACAO_TEMPLATES=pos-lato-sensu/post@1#bfcb25490b8e,pos-lato-sensu/story@1#91137d4ddd46,pos-lato-sensu/banner@1#1badbdf0cb93
```

## Desempenho (SC-1137)

Pendente no ambiente de implantação (T044). Na máquina de desenvolvimento, a galeria da Pós Lato
Sensu compõe e rasteriza os 48 pares cenário × formato pelo fluxo real.
