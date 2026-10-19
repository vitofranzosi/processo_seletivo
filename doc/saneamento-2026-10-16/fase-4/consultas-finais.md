# Minutas finais — DEC-15.04, .12 e .13

Versão para aprovação humana, 16/10/2026. **NÃO ENVIADAS.** Remetente e destinatários nominais,
protocolo institucional e prazo de resposta dependem de designação pelo responsável.

Estas minutas consolidam os recortes da [Fase 3](../fase-3/dossie-institucional.md), aproveitando
as minutas Cefor/encarregado/jurídico da Fase 1. Encaminhar um expediente por interlocutor e
reaproveitar respostas compartilhadas; não enviar as três versões históricas como pedidos duplicados.
Nenhuma interpretação jurídica conclusiva é emitida pelo agente.

## I-04 — teto de inscrições por candidato

**Destinatário proposto:** Cefor/autoridade responsável pelo certame; setor jurídico/normativo se
o Cefor remeter questão de competência ou isonomia. **Assunto:** definição formal da transição
em Retificação do teto de inscrições.

Prezadas(os), solicitamos orientação para os seis cenários abaixo, antes de ratificar a regra
administrativa de transição. O sistema é local, sem uso real aprovado por esta consulta.

**Contexto e implementação:** `maxInscricoesPorCandidato` é retificável no contrato da 026.
`tests/integration/inscricoes/test_fatos_congelados.py::test_reduzir_o_teto_por_retificacao_nao_invalida_o_ja_submetido`
expressa preservação das inscrições submetidas. A deliberação humana .04/C mantém provisoriamente
as aceitas, sem exclusão automática. Isso não decide tratamento de novos envios ou prazo.

| Cenário / pergunta formal | Alternativas administrativas a decidir | Consequências para candidatos, operadores e atos |
|---|---|---|
| 1. Pode aumentar teto durante inscrições? | Efeito desde vigência; efeito com comunicação/prazo adicional; vedação nessa fase | Novas opções para candidatos, necessidade de alcançar quem já enviou/desistiu; calendário e instruções devem corresponder ao ato |
| 2. Pode reduzir durante inscrições? | Limitar somente novos envios; adiar redução; vedar nessa fase | Preservar aceitas não resolve a oportunidade de quem ainda não enviou; operador precisa de orientação explícita |
| 3. Pode alterar após encerramento? | Correção sem novos envios; reabertura formal; vedação ou adiamento | Pode alcançar classificação/convocação; alteração de regra não reabre prazo por si |
| 4. Qual o tratamento das submetidas? | Confirmar preservação; eventual revisão individual por rito próprio, sem automatismo | Nenhuma exclusão por redução posterior; distinguir erro individual de mudança de teto |
| 5. Qual regra vale para novas após Retificação? | Versão vigente; transição com casos definidos; nenhum novo envio se período fechado | Definir referência temporal e elegibilidade sem reconstruir passado |
| 6. Quando prorrogar/reabrir por isonomia? | Obrigatório em situações definidas; discricionário motivado; desnecessário em casos delimitados | Publicidade, prazo e efeitos nos marcos seguintes precisam de decisão e autoria |

Solicitamos, por linha, alternativa, fundamento institucional, autoridade competente, vigência,
meios de comunicação e tratamento de atos dependentes. Como coordenar a designação do Evento (.05)
com alteração efetiva do período, sem confundir os dois atos?

**Recomendação submetida:** manter proteção do histórico e decidir separadamente aumento/redução,
fase, comunicação e prazo; não sugerimos transição universal por economia de implementação.
**Consulta respondida quando:** manifestação identificável e datada responde às seis linhas,
registra limites, remessas e questões sem resposta. Não basta “pode retificar”. Nova ratificação
do produto e eventual autorização administrativa do caso concreto permanecem necessárias.

## I-12 — competência e habilitação de autoridades

**Destinatário proposto:** Cefor e unidade/setor competente para nomeação, delegação e substituição.
**Assunto:** confirmação de modelo e competência para habilitar, alterar e revogar autoridades por unidade.

Prezadas(os), solicitamos confirmar o rito institucional que fundamentará a ratificação da .12.
O cadastro técnico não constitui prova autônoma de competência administrativa.

**Implementação atual:** D-003 da 060 modela habilitação explícita na unidade, sem inferir por
lotação/hierarquia. Autoridades são cadastradas com fundamento e vigência; a clarificação da 060
atribui manutenção ao Gestor da própria unidade. R1/.12/C exige confirmação institucional de quem
aprova e de quem somente opera. Nomear cargo no software não cria competência legal.

| Alternativa a avaliar | Consequências |
|---|---|
| Habilitação explícita por unidade | Registro de pessoa em várias unidades; competência e vigência precisam de comprovação própria |
| Aprovação/concessão central com operação delimitada por unidade | Mais controle central, dependência de atendimento e responsabilidades claras |
| Modelo hierárquico com atos e exceções formalizados | Exige desenho institucional para evitar competência indevida por herança; não é capacidade aprovada |

**Perguntas para resposta formal:**

1. Quem autoriza habilitação, alteração e revogação, por unidade/tipo de ato? Quem somente cadastra?
2. Quais nomeação/delegação/substituição, documentos, vigências e limites devem ser conferidos?
3. Gestor pode acumular aprovação e operação? Há segregação ou dupla conferência exigida?
4. Como tratar Reitoria em múltiplas unidades sem pressupor competência universal pelo cargo?
5. Qual rito para erro descoberto após uso em publicação, preservando ato e histórico sem correção silenciosa?
6. Como comunicar cessação de competência, revogar acessos e auditar as duas ações distintamente?

**Impactos:** candidato e cidadão precisam reconhecer autoria válida; publicador precisa de opções
corretas; cadastro incorreto pode alcançar atos oficiais. Mudança automática de hierarquia pode
ampliar competência sem fundamento. Rito excessivamente central pode paralisar publicação legítima.
**Recomendação submetida:** conservar concessão explícita e provar fundamento/escopo; não inferir
competência por diretório ou lotação. Modelo definitivo e responsáveis são decisão institucional.
**Resposta suficiente:** quadro ação → autoridade aprovadora → operador → fundamento → evidência →
escopo/vigência, com autor/data e pendências. Essa resposta pode instruir DEC-04, mas não decide
automaticamente assinatura, conceder usuários ou ratificar .12 sem nova deliberação.

## I-13 — necessidade e momento da coleta do Requerimento

**Destinatários propostos:** Cefor e encarregado de dados, com jurídico/normativo se necessário.
**Assunto:** posicionamento conjunto por categoria de dado, momento e bloqueio da inscrição.

Prezadas(os), solicitamos análise conjunta antes de autorizar uso real da regra FR-372 da 029.
Se o Edital declara Requerimento na inscrição, a implementação atual exige-o enviado para submeter
a inscrição. A decisão .13/C preserva provisoriamente esse comportamento, sem ratificar seu uso
em certame real. A base da exigência e a necessidade de cada campo precisam ser confirmadas.

| Alternativa administrativa | Consequências |
|---|---|
| Requerimento completo na inscrição como condição | Antecipação de coleta inclusive de quem não será convocado; barreira ao envio; precisa de fundamento por categoria |
| Coleta na convocação/matrícula | Minimiza antecipação, mas pode atrasar análise ou contrariar exigência concreta do Edital |
| Dados mínimos na inscrição, complemento depois | Exige regra por categoria/momento e consequência da ausência; capacidade parcial não é presumida existente |
| Procedimento externo formal | Pode ser transitório, mas exige autoria, acesso, retenção e vínculo ao certame; não presumir jornada completa |

**Perguntas para resposta formal:**

1. Por categoria (identidade/contato, filiação, civil/eleitoral, nascimento/nacionalidade, endereço,
   cor/raça, necessidades específicas, renda), qual finalidade, necessidade, fundamento, momento,
   obrigatoriedade, acesso e retenção? Reaproveitar manifestação da DEC-03, sem duplicar consulta.
2. O que é necessário para concorrer e o que somente para matrícula? Isso muda por sorteio,
   avaliação, seleção discente ou modalidade? Identificar norma do edital, sem usar apenas “ele pede”.
3. Quando ausência deve impedir inscrição, permitir complemento ou produzir outra consequência?
4. Que orientação deve ser exibida ao candidato e qual procedimento de correção/complemento?
5. Como preservar o que cada versão exigiu sem retroagir critérios nem reescrever inscrição enviada?

**Impactos:** acesso do candidato e dados de quem não chega à matrícula; carga de conferência;
exigências do ato e riscos de omissão ou excesso de coleta. Exemplos anexáveis somente sintéticos.
**Recomendação submetida:** decidir por necessidade/categoria/momento, antes de escolher bloqueio
global. Não retirar exigência normativa válida nem ampliar coleta por conveniência técnica.
**Resposta suficiente:** manifestação conjunta ou respostas articuladas, identificáveis e datadas,
com quadro por categoria e cenário, conflitos remetidos ao setor competente e condições de uso
real. Nova deliberação .13/DEC-12 é necessária; não habilitar produção ou avisos por essa minuta.

## Registro de retorno e despacho — campos ainda não preenchidos

Versão da minuta; remetente autorizado; destinatário nominal/competência; processo/protocolo;
data do envio; resposta sanitizada; autor/fundamento; itens respondidos/parciais; autoridade que
decidirá pendências; data de nova deliberação. Nenhum desses campos é inventado nesta fase.
