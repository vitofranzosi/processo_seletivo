# Data Model: Polish — os resíduos dos três lotes

**Não há entidade de domínio nova nem alterada.** Nenhuma migration, nenhum modelo, nenhum campo. O
que esta feature trata são elementos de tela, já existentes:

| Elemento | Onde mora | O que muda |
|---|---|---|
| Ato do Processo (`AtoProcesso`) | `interface/atos_processo.py` | nada no objeto; o template o desenha pelo `irreversivel` que ele já declara ([D-001](research.md)) |
| Grupo das terminais | `_estilo_das_terminais.html`, incluído pelo Detalhe do Edital e pelo Processo | só o lugar das regras ([D-002](research.md)) |
| Moldura de rolagem | `div.rolavel-no-estreito`, na Lista e na Condução | rola abaixo de 60 rem ([D-003](research.md)) |
| Célula de resultado | `resultados.html` | `numero` só na nota ([D-009](research.md)) |
| Linha de Etapa no formulário | `forms.etapas_do_edital` | o texto dos três números, sem zeros ([D-005](research.md)) |
| Par rotulado da Revisão (`Rotulada`) | `interface/origens.py`, desenhado por `_linhas_da_revisao.html` | nada no objeto; a largura da coluna ([D-006](research.md)) |
| Motivo de sucessão | `ocupacao.html`, `sorteio.html` | o controle ([D-007](research.md)) |

**Estado gravado das Etapas** — a prova do R6 ([D-005](research.md)): por Etapa, `name`, `order`,
`weight`, `eliminatory`, `classificatory`, `minimum_score`, `evaluations_per_registration`,
`maximum_score`, `forma`, `rotulo_favoravel`, `rotulo_desfavoravel`, `evento_id`; e, do registro
`ALTERAR_RASCUNHO`, a operação, o motivo e os estados.
