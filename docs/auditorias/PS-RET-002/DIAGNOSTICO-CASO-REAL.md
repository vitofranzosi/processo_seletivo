# Diagnóstico individual — PS-RET-002

## Resultado

**CASO_REAL_NAO_IDENTIFICADO.** Não se afirma que o incidente real foi corrigido ou que tinha a
mesma causa dos cenários sintéticos.

## Ambiente investigado por leitura

- Aplicação local já existente: container `processo_seletivo-app-1`.
- Configuração declarada: `config.settings.development`.
- Conexão informada pela aplicação: host `db`, porta `5432`, database `processo_seletivo`,
  usuário técnico `processo_seletivo_runtime`.
- Instância Docker local correspondente: `processo_seletivo-db-1`.
- Todas as consultas foram executadas com `SET TRANSACTION READ ONLY`, seguidas de rollback e
  fechamento da conexão. Não se abriu uma sessão Web nem se praticou ato nesse ambiente.

## Consultas e resultados observados

```sql
SELECT r.id, r.edital_id, e.number, e.year, r.status, r.base_snapshot_id,
       r.effective_at, r.created_at, r.submitted_at, r.homologated_at,
       r.publication_id, a.target_path, a.new_value
FROM publicacoes_retificacao r
JOIN processos_edital e ON e.id = r.edital_id
JOIN publicacoes_alteracaonormativa a ON a.retificacao_id = r.id
WHERE a.target_path LIKE '/schedule/%'
ORDER BY r.created_at;
```

Resultado: **zero candidatos**. Consulta adicional de contagens: **1 Edital, 0 Retificações,
0 Alterações Normativas**. Portanto não havia, nesse banco acessível, uma retificação que permitisse
reconstruir submissão, homologação, publicação, vigência ou responsáveis do incidente relatado.

Nenhum identificador de Edital/Retificação do incidente foi fornecido. Não se presumiu que o único
Edital local fosse o referido pelo usuário. Não foram consultados outros bancos por tentativa nem
usadas as retificações da auditoria anterior como se fossem dados reais.

## Evidências confirmadas, hipóteses e indisponibilidades

Confirmado: ausência de retificações na conexão local investigada. Confirmadas separadamente em
testes sintéticos: seleção de base futura incompatível e admissão de intervalo invertido antes
da correção; as duas correções têm evidências próprias.

Não comprovados para o incidente: rascunho abandonado, homologação pendente, falta de permissão,
vigência futura, conflito temporal, falha de transação, cache ou ausência de mensagem. São hipóteses,
não diagnóstico individual.

Para fechar o incidente real: obter URL/UUID do Edital e da Retificação e identificar a conexão
correspondente; consultar por leitura estado, base, publicação, vigência e eventos da trilha. Não é
necessário modificar o registro para diagnosticá-lo.
