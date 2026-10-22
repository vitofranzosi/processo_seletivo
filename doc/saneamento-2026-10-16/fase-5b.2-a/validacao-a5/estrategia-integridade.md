# Estratégia de integridade para deliberação

As alternativas abaixo são propostas. Nenhuma está aprovada ou implementada.

| Dimensão | 1 — Preservação com nova baseline | 2 — Restauração histórica | 3 — Dupla representação controlada |
|---|---|---|---|
| Descrição | Preservar todos os bytes atuais; aprovar nova referência de hashes brutos, ligada às anteriores | Reproduzir bytes CRLF esperados, preferencialmente em cópia nova identificada | Preservar bytes físicos e registrar hash físico + hash canônico LF separadamente |
| Segurança | Forte identidade binária se revisão e aprovação precederem confiança; proibir simples recalcular-e-aceitar | Hash antigo volta a coincidir, mas controles ausentes permanecem; equivalência não aprova executor | Boa capacidade explicativa; validação deve exigir hash físico da revisão aprovada, sem OR entre hashes |
| Rastreabilidade | Tabela antigo/atual/sucessor, autoria, justificativa e aprovação; históricos intactos | Registrar transformação, origem e destino; não sobrescrever evidência histórica | Registrar algoritmo, encoding, EOL e ambos os digests; separar comparação textual de autorização |
| Compatibilidade atual | Operador atual exige manifesto antigo; nova revisão com referências aprovadas é necessária | Pode satisfazer comparador bruto em scripts, mas contradiz eol=lf e sofre nova normalização | Comparador atual não entende digest canônico; nova revisão necessária se houver integração |
| Alteração não intencional | Risco de legitimar bytes desconhecidos; mitigar revisão de diferenças e gate humano | Risco elevado de mudanças por transcodificação/encoding, normalização posterior e conflito com Linux | Risco de esconder alterações usando digest textual; recusar encoding inválido e EOL misto |
| Históricos | Nenhuma alteração; novos registros sucessores | Alteração no lugar compromete custódia; exigir cópias novas em vez de reescrita | Nenhuma alteração se relatórios adicionais forem novos |
| Código necessário | Nova revisão exclusiva do executor/contratos e manifesto; código funcional intocado | Transformação de bytes requer autorização específica; não corrige lacunas do executor | Nova política/validador se usado operacionalmente; comparação só documental dispensa código operacional |
| Reversão | Suspender nova revisão e voltar ao estado bloqueado, sem apagar nada | Suspender cópia; qualquer restauração no lugar exige nova autorização e evidência | Suspender política canônica; preservar registros e exigir hash físico |
| Evidência exigida | Diff revisado, hashes brutos fonte/sucessor, aprovação nominal, testes de recusa e rechecagem Git | Byte a byte reconstruído, hashes antes/depois, EOL/encoding, teste de checkout autorizado e análise de compatibilidade | Vetores de teste de normalização, versões do algoritmo, hashes físicos/canônicos e decisão sobre autoridade |
| Autorização | Escolha humana da alternativa e autorização de novos artefatos antes de implementação | Aprovação específica de caminhos e transformação; nenhuma alteração automática | Aprovação explícita de política, sem aceitar normalização como bypass da guarda |

**Recomendação: alternativa 1**, mantendo os históricos e estabelecendo nova revisão operacional em caminho novo. A alternativa 3 pode ser evidência secundária; a identidade autorizada continuará sendo o hash dos bytes exatos. A alternativa 2 tem custo de manutenção e conflito com LF já estabelecido.

## Política proposta de hashes e EOL

Para artefatos novos aprovados: UTF-8 sem BOM e LF; hash bruto SHA-256 de read_bytes, sem read_text ou transcodificação no caminho de confiança. Registrar tamanho, EOL, caminho relativo e revisão. Rejeitar CR isolado, EOL misto, caminho fora do conjunto, atalho/junção ou divergência; não normalizar na validação. Para arquivos históricos: preservar bytes encontrados e registrar divergência com sua referência original.

SHA-256 bruto é o identificador autoritativo da revisão aprovada. Hash canônico, se aprovado, é explicativo e nunca alternativa de sucesso. O manifesto deve ter conjunto exato de entradas e digest atestado fora dele; não pode aprovar a si próprio. Alterações de manifesto exigem nova revisão e aprovação, nunca preenchimento silencioso de hashes atuais.

Recalcular após eventual incorporação Git futura, em ambiente de revisão autorizado: a política LF já existe e não será modificada. Se bytes divergirem após checkout, bloquear. Não iniciar incorporação/checkout nesta fase.

Riscos residuais: arquivo de aprovação local não equivale a assinatura; hash não comprova procedência; há janela entre conferir e executar. Impedir edição concorrente por ACL/permissões e revisar caminho/identidade/bytes imediatamente antes do lançamento; se essa garantia não puder ser sustentada, negar execução. Atualizar a baseline somente após todos os incrementos aprovados, mantendo sua cadeia de origem.

