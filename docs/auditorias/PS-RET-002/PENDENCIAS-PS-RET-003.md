# Pendências para PS-RET-003

Nenhuma das funcionalidades abaixo foi implementada em PS-RET-002.

1. **Navegação de retificações pendentes:** listar e abrir Retificações em elaboração, revisão e
   homologadas a partir do Edital, respeitando escopo e permissões. Hoje o detalhe do Edital lista
   documentos de atos já publicados; a continuação de uma pendência exige conservar o UUID/URL.
2. **Edição Web de devolvidas:** disponibilizar formulário do mesmo rascunho em elaboração após
   devolução. O domínio/API já permitem editar com `retificacao:elaborar` e `If-Match`; o navegador
   não oferece essa operação. Reutilizar autorização e revisão existentes.

Dependências comprovadas: conservar a base explícita durante conferência/edição; exibir conflitos
de revisão/temporalidade; reutilizar a validação central de intervalo. Não é necessário alterar
privilégios institucionais ou permitir reescrita de atos publicados.

Diagnóstico do incidente real continua dependendo da identificação do ambiente e UUID correto,
mas isso não é uma nova funcionalidade de PS-RET-003.
