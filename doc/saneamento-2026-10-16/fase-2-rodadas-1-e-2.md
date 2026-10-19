# DEC-15 — registro da Rodada 1 e deliberação da Rodada 2

> Atualização de 16/10/2026: a apresentação histórica abaixo foi preservada. A Rodada 2 recebeu
> deliberação expressa, registrada no [controle seguinte](fase-2-rodadas-2-e-3.md), junto da
> apresentação da Rodada 3. As indicações de espera abaixo descrevem o momento da apresentação.

Data: 16/10/2026. Complementa o [relatório inicial](fase-2-deliberacao-dec-15.md).
Fonte da deliberação: mensagem expressa do responsável pelo produto nesta conversa,
“Fase 2 — DEC-15 — Deliberação da Rodada 1”, com instruções de registro por identificador.
Não foi inferida aprovação pelo silêncio, pela implementação ou por recomendação anterior.

## 1. Registro da deliberação humana — Rodada 1

| Item / opção | Estado da deliberação | Alcance expressamente aprovado | Pendências e condição de encerramento |
|---|---|---|---|
| DEC-15.13 / C | Encaminhamento aprovado; regra não ratificada | Consultar Cefor e encarregado sobre necessidade de cada categoria, momento da coleta e exigências normativas do edital; manter implementação provisoriamente, sem ratificação para certame real | Manifestação institucional e nova decisão do produto; consulta não enviada nesta execução |
| DEC-15.12 / C | Encaminhamento aprovado; regra não ratificada | Consultar Cefor sobre habilitação por unidade e competência para habilitar, alterar e revogar; distinguir competência administrativa de permissão técnica | Manifestação do Cefor antes da ratificação; consulta não enviada nesta execução |
| DEC-15.14 / A | **Ratificada exclusivamente quanto ao modelo de permissão separada** | Exportação em lote exige permissão separada; não concedê-la automaticamente a outros papéis | Usuários autorizados, concessão, revogação e controles de acesso dependem de validação institucional; isso não ratifica papel organizacional específico, integração de identidade, importação no RA ou homologação |
| DEC-15.15 / C | Encaminhamento de análise aprovado; condição atual não ratificada | Levantar dados pessoais, sensíveis e indiretamente identificáveis nas prévias; distinguir visualização, geração e download e avaliar auditoria de cada operação | Levantamento e nova deliberação sobre política de auditoria; análise detalhada não executada neste registro |

Autor da deliberação: responsável pelo produto, usuário desta conversa; sem atribuição nominal
institucional adicional. Data do registro: 16/10/2026. Evidência: texto explícito da mensagem acima.
Não há parecer institucional anexado nem homologação demonstrada por essa decisão.

A opção A apresentada anteriormente para .14 mencionava papel separado. O usuário delimitou a
ratificação à **separação da permissão**; esse limite expresso prevalece sobre a formulação da
alternativa. A escolha do papel nominal `exportador` e quem o recebe não são presumidas aprovadas.

Nenhuma permissão foi concedida ou removida. Não se autoriza uso real da regra .13 por manter a
implementação local. Não houve envio de consultas, alteração de specs ou autorização da Fase 3.
As pendências institucionais permanecem abertas, mesmo onde existe ratificação parcial do modelo.

## 2. Rodada 2 — critérios comuns

Próximos quatro itens, na ordem proposta: **DEC-15.02, .03, .06 e .04**.
Todos aguardam resposta humana. Recomendações abaixo não são ratificações.

Conforme a [Constituição](../../.specify/memory/constitution.md), retificar conteúdo futuro não
autoriza reescrever publicação, inscrição ou ato histórico. Obsolescência de ordem não significa
exclusão ou substituição automática: a 015 mantém o ato vigente até emissão explícita de sucessor.
Recursos, cortes e convocações dependentes precisam de análise própria quando houver efeitos.

### DEC-15.02 — Retificabilidade da operação de combinação das pontuações

**Atual:** `classificationMilestones/operation` é retificável. A 015 especifica que mudança relevante
da regra torna o ato calculado anterior obsoleto; novo ato exige emissão explícita, autorizada e
auditável. Trocar como as pontuações são combinadas pode mudar posições, mesmo sem mudar as notas.

**Evidências:** [015](../../specs/015-ordenacao-e-classificacao/spec.md), regras sobre operação,
obsolescência e emissão; [matriz da 026](../../specs/026-contrato-de-mutabilidade-normativa/matriz.md),
linha `operation` e emenda da revisão #114; contrato em
`backend/processo_seletivo/editais/domain/mutabilidade.py`. Commit `1d721b93` registra restauração
de capacidade anterior. Nenhum desses fatos substitui ratificação expressa do produto.

**Alternativas:**

- **A — recomendada:** ratificar a capacidade técnica de retificar a operação, preservando atos e
  explicitando obsolescência; não aprovar aplicação irrestrita a qualquer fase ou certame.
- **B:** solicitar proposta de restrições por fase/ato, sem adotá-las antes de decisão competente.
- **C:** solicitar demonstração operacional e esclarecimento dos efeitos antes de ratificar.

**Impactos:** classificação, cortes e possíveis efeitos posteriores em recursos e convocação;
operador precisa reconhecer a diferença entre regra nova e ato ainda vigente.
**Risco de manter:** entender a retificação como autorização para substituir automaticamente
resultado ou ignorar atos dependentes. **Risco de restringir/modificar:** retirar caminho para
corrigir regra publicada e criar contradição com a capacidade anterior, sem rito substituto.
**Fundamento da recomendação:** correção normativa rastreável com preservação histórica é preferível
a congelar erro; condições de aplicação administrativa não devem ser deduzidas do mecanismo técnico.
Revisão de efeitos concretos exige setor competente e validação com usuários; nenhuma é declarada feita.

**Pergunta:** ratifica somente a capacidade técnica delimitada em A, solicita restrições em B ou
prefere demonstração prévia em C?

### DEC-15.03 — Retificabilidade da normalização das pontuações

**Atual:** `classificationMilestones/normalization` é retificável. É normalização de **pontuações**,
não a transformação de números de fonte externa do sorteio. Integra a regra de cálculo e sua revisão
pode afetar a comparação entre candidatos.

**Evidências:** 015, regra de operação com normalização declarada; matriz da 026, linha
`normalization`, e emenda `1d721b93`; comentário do contrato associa sua retificabilidade à operação
e ao tratamento explícito de obsolescência. Leitura documental, sem novo ensaio nesta rodada.

**Alternativas:**

- **A — recomendada:** ratificar a capacidade técnica, com versionamento, preservação dos atos e
  análise dos dependentes; sem aprovação irrestrita para qualquer fase do certame.
- **B:** solicitar proposta de restrições temporais ou por atos já emitidos.
- **C:** pedir demonstração conjunta de operação e normalização antes da ratificação.

**Impactos:** pontuações comparáveis, ordem e cortes, podendo alcançar análise de recursos e atos
posteriores. Dependência direta da deliberação .02 para consistência da política.
**Risco de manter:** efeito quantitativo não ficar claro ao operador e ser tratado como mero ajuste
de apresentação. **Risco de modificar:** manter erro de cálculo sem possibilidade de correção ou
retirar capacidade sem definir substituição. Não é seguro presumir que toda normalização é inócua.
**Fundamento da recomendação:** manter caminho explícito de correção com versões e autoria, sujeito
à análise administrativa do caso; eventual restrição exige regra aprovada, não improvisação técnica.

**Pergunta:** ratifica A, solicita B ou prefere demonstração C? Pode decidir diferentemente de .02;
nesse caso, a compatibilidade das duas decisões precisará de esclarecimento antes de implementação.

### DEC-15.06 — Declarar método de sorteio onde ele estava ausente

**Atual:** o contrato permite que `classificationMilestones/drawMethod` ausente passe a existir
por Retificação, exigindo método completo e conteúdo válido para publicação.

**Evidências:** matriz da 026 e `1d721b93`; contrato de objeto ausente em `mutabilidade.py`; teste
`backend/tests/contract/test_elevacao_degrau_10.py` documenta conteúdo anterior ao degrau 10 com
`drawMethod` nulo e declaração posterior por Retificação. Essa compatibilidade não prova autorização
institucional para converter qualquer classificação calculada em sorteio depois de atos praticados.

**Alternativas:**

- **A:** ratificar alcance geral da capacidade atual, ainda sujeito a limites institucionais não definidos.
- **B:** propor ratificação limitada à compatibilidade histórica, condicionada a verificar se o
  sistema distingue esse caso; não registrar tal limitação como já implementada.
- **C — recomendada:** esclarecer separadamente compatibilidade histórica, declaração nova e
  mudança da espécie de classificação; obter enquadramento do Cefor/normativo quando necessário.

**Impactos:** método de classificação, universo habilitado, publicação da relação, rito do sorteio
e atos posteriores. Comissão precisa compreender quando se altera método e quando se declara dado
ausente por versão técnica antiga.
**Risco de manter:** usar justificativa de compatibilidade para mudança administrativa de alcance
maior que o pretendido. **Risco de restringir/modificar:** bloquear conteúdo histórico válido ou
criar uma exceção impossível de distinguir com os dados atuais.
**Fundamento da recomendação:** a evidência comprova um caso histórico, não todos os usos da permissão.
Primeiro delimitar cenários e competência decisória; ratificar depois o alcance demonstrável.

**Pergunta:** confirma C, prefere propor limitação B ou pretende ratificar A com condições explícitas?

### DEC-15.04 — Retificar teto de inscrições por candidato

**Atual:** `maxInscricoesPorCandidato` é retificável. Há teste de integração afirmando que reduzir
o teto não invalida inscrição já submetida. Isso não encerra a decisão administrativa sobre
oportunidades de novas inscrições ao longo do prazo.

**Evidências:** matriz da 026 e `1d721b93`; contrato de raiz em `mutabilidade.py`;
`backend/tests/integration/inscricoes/test_fatos_congelados.py`, caso
`test_reduzir_o_teto_por_retificacao_nao_invalida_o_ja_submetido`. Testes lidos, não executados nesta fase.

**Alternativas:**

- **A:** ratificar retificabilidade com preservação das anteriores, sem ainda definir todas as
  condições administrativas de aumento e redução.
- **B:** solicitar proposta de limites por fase, separando aumento, redução e eventuais comunicações.
- **C — recomendada:** consultar a regra institucional de transição antes de ratificar o alcance;
  manter implementação provisoriamente, sem presumir aprovação para aplicação real.

**Impactos:** admissão de novos envios, quantidade de opções por pessoa, tratamento de quem se
inscreveu antes/depois e eventual necessidade de reabrir prazo ou comunicar mudanças, se assim decidido.
Não é proposta de executar essas medidas automaticamente.
**Risco de manter:** confundir preservação do passado com solução de todo tratamento das inscrições
futuras. **Risco de modificar:** invalidar indevidamente inscrições aceitas ou impedir ajuste legítimo;
regras condicionais novas também exigem especificação e testes próprios.
**Fundamento da recomendação:** separar integridade histórica, já exigida pela Constituição, da
decisão normativa sobre quem pode fazer novos envios e sob quais condições.

**Pergunta:** confirma consulta C, solicita proposta B ou ratifica a capacidade A com limites expressos?

## 3. Estado e próximos passos permitidos

R1 registrada; R2 apresentada e **aguardando deliberação humana**. R3 não iniciada.
Uma escolha de consulta/esclarecimento aprova encaminhamento, não a regra analisada. Uma ratificação
de capacidade técnica não autoriza implementação, alteração de especificação, concessão de acesso,
uso em certame real ou decisão normativa sobre efeitos em atos existentes.

Os levantamentos e consultas aprovados na R1 permanecem identificados como trabalho pendente; este
registro não afirma que foram realizados. Nenhuma mensagem foi enviada a terceiros.

**FASE 2 — RODADA 1 REGISTRADA; RODADA 2 AGUARDANDO DELIBERAÇÃO HUMANA.**
