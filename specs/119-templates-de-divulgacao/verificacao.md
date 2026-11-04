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

## Validações que dependem do ambiente de implantação

Nenhuma delas se faz na máquina de desenvolvimento, e nenhuma está feita. **Em host local a peça não
é gerada** (EC-12, regra da `111`): sem endereço público não há link na peça, e a tela diz o motivo
no lugar das prévias. Por isso a prévia com imagem, o download do PNG e do SVG e o ZIP da família
foram provados pela suíte e pela galeria, **e nunca num navegador**. A adoção registrada acima
(P-4) aprova o desenho dos templates; ela não comprova a jornada de quem os usa.

| O quê | Requisito | Tarefa | Como | Situação |
|---|---|---|---|---|
| Prévias dos três formatos e downloads PNG, SVG e ZIP pelo navegador, num Edital publicado, com o endereço público | FR-3806, FR-3829, FR-3830 | T056 | Abrir o kit de um Edital publicado da Pós Lato Sensu, escolher imagem, baixar cada formato e o ZIP, e conferir que o ZIP traz os três formatos e o manifesto | pendente |
| Jornada com uma pessoa da comunicação: post, story e banner em menos de três minutos, sem abrir o PDF e sem digitar texto | SC-1136 | T056 | Cronometrar, registrar aqui nome do papel, Edital, tempo e o que travou | pendente |
| Tela com as três prévias em menos de 2 s e ZIP em menos de 3 s, num lote de 20 | SC-1137 | T044 | 20 gerações seguidas de cada, registrando mediana e máximo | pendente |
| O PNG da mesma ficha e escolha sai idêntico em duas gerações | SC-1134 | T044 | Comparar o SHA-256 de dois downloads seguidos de cada formato | pendente |
| A liberação nomeia versão e resumo, e template divergente não é gerado | FR-3808, SC-1140 | — | Conferir `KIT_DE_DIVULGACAO_TEMPLATES` do ambiente contra a tabela acima; a recusa do divergente é coberta pela suíte | pendente |

## Desempenho (SC-1137)

Pendente no ambiente de implantação (T044). Na máquina de desenvolvimento, a galeria da Pós Lato
Sensu compõe e rasteriza os 48 pares cenário × formato pelo fluxo real.
