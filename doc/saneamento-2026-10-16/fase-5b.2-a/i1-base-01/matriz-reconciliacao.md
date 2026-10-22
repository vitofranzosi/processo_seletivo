# Alternativas de reconciliação — decisão pendente

Investigação FASE-5B.2-A-I1-BASE-01; executor Codex; 20/10/2026, America/Sao_Paulo (UTC−03:00).
Repositório: D:\projetos\cefor\processo_seletivo. Branch: 001-decisoes-pendentes. HEAD observado: 4ec10ba52636ef54b56dee35970333f5742548df.

I1 bloqueado; I2–I6 não autorizados; G1–G6 bloqueados individualmente. Nenhuma nova baseline aprovada.

| Alternativa | Pré-condições / evidência faltante | Benefícios | Riscos / rastreabilidade | Hashes históricos / não rastreados | I1 / gates / decisão |
|---|---|---|---|---|---|
| A — manter referência anterior | Deliberação sobre como comparar execução futura com referência antiga, sem mover HEAD nesta autorização | Mantém vínculo literal com autorização antiga | Ambiente atual não satisfaz HEAD antigo; risco de fingir correspondência | Preservar todos; nenhum reset ou restauração autorizado | I1 continua bloqueado; G1–G6 bloqueados; decisão humana |
| B — propor HEAD atual prospectivamente | Aprovação nominal humana do HEAD, inventário de 124 documentos e tratamento dos 15 não rastreados; revisão dos seis caminhos de código | Reflete ambiente efetivamente encontrado sem movimento Git | Mudanças de produto não validadas funcionalmente nesta investigação; não reescrever baseline antiga | Hashes antigos intactos; preservar bytes atuais e aceitar explicitamente não rastreados como evidências locais | Possibilita autorização específica posterior de I1; G1–G6 bloqueados; aprovação reservada ao humano |
| C — baseline documental segregada | Definir escopo, identificação, caminhos e relação com HEAD em decisão posterior | Separa referência documental de estado operacional | Pode ampliar complexidade e criar ambiguidade se HEAD omitido | Históricos e 15 não rastreados preservados; nenhum commit/branch ou alteração histórica implícita | Não executa I1; gates bloqueados; exige decisão humana |
| D — manter bloqueio | Quando faltarem confiança externa dos manifestos ou decisão sobre mudanças | Evita assumir autorização e preserva todas as alternativas | Adia I1; requer aquisição adicional de proveniência, sem operação automática | Sem mudança nos hashes e não rastreados | I1 bloqueado; G1–G6 bloqueados; deliberação humana continua necessária |

## Recomendação técnica

Submeter B à decisão humana, com referência prospectiva nominal ao HEAD atual e inventário documental segregado do uso operacional. Os merges explicam o desvio e não mudam a área documental no diff; os hashes locais conferem com A.4/A.5. Isso é fundamento documental para proposta, sem validar comportamento da classificação ou endossar controles operacionais.

Enquanto não houver aprovação, D é o estado efetivo. Se a confiança independente ou a autorização sobre a nova referência forem insuficientes, manter D e solicitar evidências adicionais delimitadas. A ausência de hash externo de A.5 e de comprovação pessoal de autoria deve ser aceita expressamente como limitação, ou suprida pelo responsável.

