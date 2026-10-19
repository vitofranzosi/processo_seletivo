# DEC-15 — registro da Rodada 3 e apresentação da Rodada 4

> Atualização de 16/10/2026: a Rodada 4 recebeu deliberação expressa. O
> [relatório consolidado](fase-2-consolidacao-dec-15.md) registra a resposta e o estado atual
> das 16 questões. A apresentação histórica abaixo permanece preservada.

Data: 16/10/2026. Histórico: [análise inicial](fase-2-deliberacao-dec-15.md),
[Rodada 1](fase-2-rodadas-1-e-2.md) e [Rodada 2](fase-2-rodadas-2-e-3.md).
Evidência: mensagem expressa “Fase 2 — DEC-15 — Deliberação da Rodada 3”, nesta conversa.
Autor: responsável pelo produto, usuário da conversa. Não se infere parecer institucional adicional.

## 1. Deliberações humanas registradas — Rodada 3

### DEC-15.05 / A — capacidade técnica ratificada com condições

Ratificada a capacidade técnica de retificar a designação do Evento que define o período de inscrições.
Condições expressas:

1. Preservar histórico de Eventos, versões e inscrições anteriores.
2. Diferenciar correção de designação de Evento de alteração efetiva do período de inscrições.
3. Não excluir ou invalidar automaticamente inscrições anteriormente submetidas.
4. Não interpretar capacidade técnica como autorização administrativa para reabrir, prorrogar ou reduzir o período.
5. Registrar efeitos da Retificação sobre calendário público e inscrições.
6. Submeter alterações administrativas do período à autoridade competente.

Efeitos administrativos concretos continuam sujeitos à aprovação institucional. O atendimento a
todas as condições não foi verificado nesta atualização documental; não se declara conformidade
implementada ou homologação por consequência da ratificação.

### DEC-15.01 / C — demonstração operacional aprovada; impeditivo não ratificado

Preparar demonstração dos três cenários:

1. Primeira publicação cujo único Evento designado para inscrições está cancelado.
2. Retificação de Edital publicado que cancela o período de inscrições.
3. Retificação que substitui Evento cancelado por outro válido.

Para **cada cenário**, apresentar: estado inicial do Edital; estado do Evento de inscrições;
operação solicitada; validações acionadas; resultado observado; impacto sobre inscrições existentes;
impacto sobre novas inscrições; consequências administrativas; recomendação técnica.

Distinguir impossibilidade de receber inscrições de eventual impossibilidade de publicar ato de
cancelamento. Não ratificar o impeditivo geral `registration_period_cancelled` nem modificar a
implementação nesta etapa. **Demonstração pendente:** não executada por este registro, sem resultado
observado preenchido por inferência. Esta execução permanece exclusivamente documental, sem banco.

### DEC-15.08 / A — regra ratificada com condições

Ratificada coerência de denominação entre Perfis somente quando o código da Modalidade é utilizado
transversalmente. Condições expressas:

1. Não impor catálogo global a Perfis independentes.
2. Exigir coerência quando código tiver significado compartilhado em documento ou regra transversal.
3. Manter rastreabilidade das validações.
4. Apresentar mensagens compreensíveis ao elaborador diante de incompatibilidade.
5. Incluir cenário na homologação operacional com elaboradores.

O alcance humano inclui **documento ou regra transversal**. A evidência técnica anterior demonstrava
validação por documento transversal; não se presume que todos os demais usos de regra transversal
já sejam reconhecidos pelo código. Essa correspondência e as demais condições ficam para verificação
autorizada posterior, sem ampliar implementação ou specs nesta fase.

### DEC-15.09 / A — apresentação técnica ratificada com condições

Ratificada apresentação fiel das condições de habilitação ao sorteio no PDF. Condições expressas:

1. Texto correspondente ao método de classificação declarado.
2. Eventual Etapa habilitante apresentada corretamente.
3. Informação correspondente ao universo efetivamente habilitado ao sorteio.
4. PDF sem criação de requisitos novos de participação.
5. Validação do conteúdo pela comissão durante homologação.
6. Nenhuma antecipação da decisão sobre alcance da DEC-15.06.

Conferência operacional e homologação com comissão permanecem pendentes. Ratificação de apresentação
não aprova novo universo, mudança da espécie de classificação ou alcance ainda não ratificado da .06.

## 2. Controle consolidado após três rodadas

| Item | Mérito / encaminhamento aprovado | Pendência que permanece |
|---|---|---|
| .14 | Permissão separada ratificada nos limites da R1 | Validação institucional de usuários, concessão, revogação e controles |
| .13 | Consulta aprovada; regra não ratificada | Necessidade, momento e exigência de dados com Cefor/encarregado |
| .12 | Consulta aprovada; regra não ratificada | Cefor: competência para habilitar, alterar e revogar autoridades |
| .15 | Levantamento aprovado; condição de auditoria não ratificada | Dados expostos e eventos de visualização, geração e download |
| .02 | Capacidade técnica ratificada com condições da R2 | Adequação, validação e efeitos administrativos competentes |
| .03 | Capacidade técnica ratificada com condições da R2 | Adequação, versões, auditoria e autorização administrativa |
| .06 | Esclarecimento aprovado; alcance não ratificado | Três cenários técnico-administrativos da R2 |
| .04 | Consulta aprovada; transição não ratificada | Seis situações da R2; preservar aceitas provisoriamente |
| .05 | Capacidade técnica ratificada com condições da R3 | Verificação das condições e aprovação dos efeitos administrativos |
| .01 | Demonstração aprovada; impeditivo não ratificado | Três cenários e nove dimensões por cenário |
| .08 | Regra ratificada com condições da R3 | Correspondência do alcance transversal, validações/mensagens e homologação |
| .09 | Apresentação técnica ratificada com condições da R3 | Equivalência ao universo e homologação com comissão; .06 continua própria |
| .10, .11, .07, .16 | Aguardando deliberação na R4 | Questões abaixo, sem ratificação nesta atualização |

Estas anotações não comprovam execução de consultas, análises ou homologações. As condições de cada
rodada continuam cumulativas nos respectivos registros. Nenhum item é encerrado por mero registro
de encaminhamento. **DEC-15 continua aberta**, inclusive após eventual deliberação da R4 enquanto
persistirem os esclarecimentos e decisões necessários.

## 3. Rodada 4 — quatro questões restantes

Fontes: [Constituição](../../.specify/memory/constitution.md),
[026, matriz](../../specs/026-contrato-de-mutabilidade-normativa/matriz.md),
[060](../../specs/060-unidades-e-autoridades/spec.md), ED-47 e evidências da análise inicial.
Leituras anteriores sustentam as descrições; nenhuma demonstração operacional nova é afirmada.

### DEC-15.10 — Chave do documento exigido não editável

**Atual e evidência:** `documentRequirements/key` é não retificável no contrato
`editais/domain/mutabilidade.py` e na matriz da 026. Nome e instruções são campos distintos,
retificáveis. ED-47/E2E-004 registra a escolha sem aprovação expressa localizada.
A chave liga a exigência aos arquivos enviados; não é somente o rótulo apresentado.

**Alternativas:**

- **A — recomendada:** ratificar estabilidade da chave publicada; correção de apresentação usa
  campos próprios sem alterar o sentido histórico ou dispensar exigência do Edital.
- **B:** solicitar proposta de alteração com remapeamento versionado, preservando todos os vínculos.
- **C:** esclarecer caso concreto em que corrigir nome/instruções é insuficiente antes de ratificar.

**Impactos:** identificação da exigência, documentos recebidos, leitura pelo avaliador e auditoria.
**Risco de manter:** chave equivocada não tem correção simples por Retificação e exige rito próprio.
**Risco de modificar:** desligar arquivo de sua exigência ou atribuir documento a outra obrigação.
**Fundamento técnico:** identidade estável protege a prova do que foi apresentado e exigido; eventual
remapeamento deve ser especificado separadamente. Não ratifica inclusão/remoção de exigência (DEC-07).
Classificação: produto, com esclarecimento técnico para eventual exceção.

**Pergunta:** ratifica A, solicita proposta B ou esclarecimento C?

### DEC-15.11 — Catálogo de unidades mantido pela implantação, sem tela

**Atual e evidência:** D-002 da 060 prevê unidades em registro versionado, sincronizado a partir
de `unidades.json`; não oferece tela central. ED-47/lote 09 inclui essa escolha entre as pendentes.
Autoridades mantêm cadastro próprio: ratificar catálogo de unidades não altera sua gestão.

**Alternativas:**

- **A — recomendada:** ratificar manutenção versionada sem tela, condicionada a conteúdo aprovado
  pelo Cefor e aplicação pela implantação, com responsabilidade editorial e técnica distintas.
- **B:** solicitar proposta de tela e papel central, sem presumir sua criação aprovada.
- **C:** validar primeiro a rotina de solicitação, aprovação e sincronização com os responsáveis.

**Impactos:** alterações de nome/cabeçalho dependem de revisão e implantação; não mudam documentos
históricos já publicados. **Risco de manter:** dependência técnica e demora em correção editorial.
**Risco de modificar:** ampliar acesso sem papel central definido e reduzir revisão do conteúdo oficial.
**Fundamento técnico:** catálogo pouco mutável pode ser revisado por diff; isso não confere à equipe
técnica competência editorial nem substitui aceite da rotina pelo setor. Classificação: produto,
Cefor e validação operacional antes de uso.

**Pergunta:** ratifica modelo condicionado A, solicita proposta B ou validação prévia C?

### DEC-15.07 — Identificador da regra normativa como estrutural

**Atual e evidência:** `normativeRule/id` é estrutural em `mutabilidade.py`; fundamento, versão e
vigência possuem tratamento próprio. A ED-47 fala em seis reclassificações, mas a linha já aparece
como identidade na adição da matriz em `0c3f0135`; a emenda `1d721b93` enumera cinco restaurações
sem esse ID. Não foi demonstrada sexta reclassificação naquela mesma revisão.

**Alternativas:**

- **A:** ratificar estabilidade do identificador como decisão de mérito, sem confirmar atribuição
  histórica imprecisa ou restringir automaticamente outros campos da regra.
- **B:** solicitar proposta de troca versionada de identidade com integridade demonstrada.
- **C — recomendada:** esclarecer origem histórica e caso de correção pretendido antes da ratificação.

**Impactos:** proveniência do fundamento da modalidade, distinção entre corrigir conteúdo e trocar
identidade. **Risco de manter:** falta de rito claro para eventual vínculo errado.
**Risco de modificar:** romper referências ou aparentar continuidade normativa onde há outra regra.
**Fundamento técnico:** preservar identidade enquanto se esclarece a atribuição e o caso real;
não pedir ratificação de fato histórico não demonstrado. Classificação: esclarecimento técnico,
depois produto; manifestação normativa se houver mudança de fundamento administrativo.

**Pergunta:** confirma esclarecimento C, ratifica somente estabilidade A ou solicita proposta B?

### DEC-15.16 — Ajuda após dez minutos de dificuldade em homologação

**Atual e evidência:** é proposta de método, não regra funcional implementada. O
[roteiro assistido](../roteiro-teste-operacional-assistido-28-2026.md), §2.1, propõe oferecer seguir
ou parar após dez minutos sem avanço; se persistir dificuldade, ajuda mínima registrada como
intervenção e exclusão daquela etapa da comparação de tempo. O próprio roteiro pede decisão prévia.
GO-31 registra ausência de aprovação, sem comprovar que a metodologia já foi aplicada.

**Alternativas:**

- **A:** aprovar o protocolo proposto, registrando toda intervenção e distinguindo conclusão
  assistida de conclusão autônoma, sem alterar métricas depois do resultado.
- **B:** adotar proposta de encerrar a tarefa sem ajuda ao atingir o limite, com protocolo prévio.
- **C — recomendada:** pactuar protocolo com observadores e representantes dos usuários na DEC-14
  antes das sessões, incluindo limite, ajuda, desistência e tratamento da comparação.

**Impactos:** interpretação do sucesso da jornada, tempos e comparabilidade entre participantes.
**Risco de manter como regra informal:** observadores ajudarem de modos diferentes e esconderem
dificuldade real. **Risco de modificar depois de medir:** invalidar comparação ou favorecer conclusão
artificial. Excluir etapa da comparação não autoriza omitir dificuldade do relatório.
**Fundamento técnico:** decidir critérios antes da observação, preservando dado de intervenção e
consentimento para prosseguir. Classificação: produto e validação operacional; depende da DEC-14.

**Pergunta:** confirma pactuação prévia C, aprova protocolo A ou prefere proposta B?

## 4. Limites e continuidade

Atualização exclusivamente do controle documental: este arquivo e aviso no registro anterior.
Nenhuma mudança em código, banco, permissões, specs funcionais ou Constituição; sem commits,
pushes, merges, migrations ou envio externo. Demonstração da .01 não executada nesta etapa.
Links locais e espaços finais conferidos; isso não é teste ou homologação do produto.

Aguardar deliberação do usuário sobre R4 **antes de encerrar a DEC-15**. A resposta poderá ratificar
mérito, aprovar esclarecimento/proposta ou adiar expressamente, com seus limites. Nenhuma opção
autoriza implementação automaticamente ou apaga pendências das rodadas anteriores.

**FASE 2 — RODADA 3 REGISTRADA; RODADA 4 AGUARDANDO DELIBERAÇÃO HUMANA; DEC-15 ABERTA.**
