# Plano — PS-RET-002

Plano decorrente da autorização explícita do procedimento. Correção mínima em Django existente.

1. Diagnosticar o banco local em transação somente leitura; não identificar por suposição.
2. Reproduzir regressões em cluster PostgreSQL novo, sem volumes preexistentes.
3. Aplicar na abertura o mesmo filtro temporal de `effective_version`, preservando o retorno vazio
   para Edital sem publicação; manter a base declarada no POST.
4. Acrescentar achado impeditivo de intervalo invertido em `validate_for_publication`, usando os
   parsers de instante e caminhos de Evento existentes. Não restringir duração igual a zero.
5. Provar rollback de recusa e preservação de atos futuros, inclusive conflito legítimo e revisão
   concorrente. Rodar testes afetados e as seis classes de arquivos da auditoria anterior.
6. Rodar lint, formatação, checks/migrations e suíte PostgreSQL. Demonstrar seis cenários no Chrome.
7. Documentar diagnóstico separado e limitações; não corrigir PS-RET-003.

Política temporal existente: `publicacoes/domain/consolidation.py` ordena por `(effectiveAt,
publicationOrder)`; `_materialize_affected_versions` acrescenta novas consolidações para cada
fronteira, com histórico append-only. Não se cria precedência nova. Conflito estrutural futuro
continua recusado atomicamente, como demonstra o teste existente de consolidação inconsistente.

Conferência constitucional: linguagem portuguesa; fonte normativa estruturada; atos imutáveis;
nenhuma migration necessária; negar por padrão; mesmo controle de revisão/transação; teste real
do canal Web. Contradição anterior sobre coerência entre datas resolvida pela regra explícita
autorizada em PS-RET-002 e FR-017 da 001, sem editar o texto histórico.
