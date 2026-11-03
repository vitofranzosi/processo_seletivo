# Publicação segura de retificações — PS-RET-002

Correção autorizada em 28/10/2026. Origem: RET-001 e RET-002 da auditoria
`docs/auditorias/PS-RET-E2E-001/`. Sem alteração retrospectiva de especificações.

- **FR-2609**: A composição de nova Retificação deve partir da versão vigente no instante da
  abertura, sem confundir uma consolidação futura com conteúdo vigente. O formulário conserva a
  identidade da base entre conferência e confirmação, inclusive diante de publicação concorrente.
- **FR-2610**: Publicação imediata válida deve ser possível na presença de ato futuro. Preservam-se
  publicações, versões anteriores e a composição temporal cumulativa já definida pela 001: vigência
  e ordem de publicação determinam a aplicação. Novas consolidações nas fronteiras futuras não
  modificam os atos publicados. Conflitos que inviabilizem essa composição continuam impeditivos.
- **FR-2611**: A conferência central de publicação deve recusar Evento cujo término seja anterior
  ao início, comparando instantes com deslocamento temporal. Igualdade é admitida e término ausente
  continua permitido quando a forma do Evento o permitir. Aplica-se à publicação original e às
  consolidações de Retificações, em todas as fronteiras afetadas. Concretiza FR-017 da 001.
- **FR-2612**: Recusa deve informar o Evento e o campo, sem confirmar publicação, versão ou mudança
  de estado parcial. Autorização, escopo, autoria, concorrência e trilha existentes permanecem.

Fora do escopo: navegação de retificações pendentes, edição Web de devolvidas, alteração de dados
reais, migrations de dados, mudança de permissões e cancelamento/substituição automática de atos.

Aceite: regressões PostgreSQL, fluxo real em Chrome com portal/API/SQL e evidências PS-RET-002.
