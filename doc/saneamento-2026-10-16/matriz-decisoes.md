# Controle de decisões — proposta de 16/10/2026

Fonte: [decisões da auditoria](../auditoria-de-consolidacao-2026-10-15/decisoes-pendentes.md),
[rastreabilidade](../auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md) e
[decisões históricas](../decisoes-pendentes-da-consolidacao.md).
Responsáveis são propostos por função e ainda precisam de designação nominal.

**Todas as decisões novas desta tabela estão aguardando decisão humana.** Registros históricos
abaixo são evidências documentais de escolhas anteriores, sem ratificar a recomendação atual.
Nenhum responsável proposto foi consultado ou recebeu mensagem nesta fase.

## Mérito, alternativas e evidência anterior

| Identificador | Descrição / alternativas | Recomendação técnica submetida | Evidência de decisão anterior |
|---|---|---|---|
| DEC-01 | Piloto e janela: A janela e edital; B sem data; C piloto-sombra | A com C intermediário; dados reais exigem avaliação própria | Auditoria registra premissa local confirmada em 14/10 e adiamento do pedido à TI em 28/09 (RC-124); nenhuma janela aprovada localizada |
| DEC-02 | Identidade da gestão: LDAP direto, proxy ou SSO | Consultar TI e especificar solução suportada | Sessão `0b03a4b5`, 28/08: preferência do usuário por LDAP; não é confirmação técnica da TI |
| DEC-03 | LGPD: consulta única ou por spec | Pacote único de sete questões; não antecipar retenção ou base legal | Decisão de 01/09 condiciona dados reais à política de retenção, conforme auditoria; parecer do encarregado não localizado |
| DEC-04 | Assinatura: eletrônica externa, identificação/publicação no sistema ou papel digitalizado | Cefor definir rito e autoridades; preservar artefatos históricos | DP-20, 28/09: PDF do sistema é oficial; forma e nome da autoridade ficaram com Cefor |
| DEC-05 | Correio: infraestrutura; produto com mensagem neutra ou aviso transitório uniforme de falha | Checklist ao correio; propor aviso uniforme sem revelar cadastro | Mensagem neutra é comportamento documentado; aprovação da alternativa nova não localizada; 073 integrada |
| DEC-06 | Documento vigente: A explicitar atos cobertos; B restringir bases; C PDF por versão; D compor na vigência | A em spec curta, sem reescrever ato; B/C/D aguardam decisão própria | PDF oficial já decidido; escolha A não ratificada no material conferido |
| DEC-07 | Documento exigido retificado: A só novas inscrições; B todos com complementação; C só antes da primeira inscrição | Auditoria recomenda A; submeter efeitos temporais ao setor competente, sem conclusão jurídica | Demanda priorizada em 03/09; 044 congela lista por inscrição; regra de transição não aprovada |
| DEC-08 | Reabilitação: A ampliar consulta; B corte consultar estado da ordem; C apenas orientar tela | B, após aprovação do comportamento esperado | Caso de 07/10 registrado em `achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md`; alternativa ainda pendente |
| DEC-09 | Famílias normativas: A selecionar por piloto; B procedimento externo; C todas agora | A; sem piloto definido, avaliar B explicitamente | Barema externo decidido em 04/09; DP-10 e alcance da Etapa por Perfil continuam abertos |
| DEC-10 | Acessibilidade: PDF marcado, HTML equivalente ou atendimento | HTML equivalente sujeito a decisão sobre publicação e autenticação do ato | Oficialidade do PDF decidida; artefato adicional não ratificado |
| DEC-11 | Nome social: antes do piloto ou depois com procedimento manual | Consulta jurídica sem adiar automaticamente o tema | Spec própria decidida em 16/09, conforme CA-19; prazo não definido |
| DEC-12 | Requerimento: manter bloqueio, não bloquear ou desaconselhar coleta na inscrição | Auditoria propõe desaconselhar; reavaliar bloqueio com encarregado | FR-372 da 029 atribuída ao agente, sem aprovação expressa, na rastreabilidade histórica linha 36 |
| DEC-13 | Manual: retomar arquitetura, integrar Visão do Sistema ou adiar até piloto | Adiar com preparação da integração, somente se aprovado | Arquitetura de 08/09 aprovada; mudar calendário ou produção exige decisão nova |
| DEC-14 | Homologação conjunta em uma semana ou por spec | Pauta conjunta com dados sintéticos e evidências por jornada | Dispensa do teste operacional como porta das 049–051 em 28/09 não aprova nova porta; validações humanas seguem pendentes |
| DEC-15 | Ratificar, rever ou pedir evidência para cada escolha do agente | Deliberar separadamente a [pauta](pauta-dec-15.md); manter comportamento até mudança autorizada | ED-47 e CA-07 identificam falta de aprovação; merge não comprova ratificação expressa |
| DEC-16 | Governança: deliberar cada uma das cinco subdecisões abaixo | Não aprovar pacote indivisível; encerrar o pai somente após registrar todas | Documento de decisões pendentes mantém questões abertas; prática ou Draft não prova deliberação |
| DEC-16.1 | DP-12: manter, regularizar ou retirar campo Status | Auditoria propõe retirar e usar README conferido por teste | 63 de 74 specs como Draft é contagem histórica de 15/10; nenhuma abolição aprovada localizada |
| DEC-16.2 | DP-08 item 1: retomar ou encerrar 039 como registro sem implementação | Encerrar explicitamente como registro, sem excluir pasta/evidências | 039 não implementada na auditoria; encerramento ainda proposto |
| DEC-16.3 | DP-09: manter recurso sem prova nova ou rever | Manter status quo, sujeito a confirmação competente | Comportamento existente não equivale à ratificação nova solicitada |
| DEC-16.4 | DP-11: acesso da comissão global, por Perfil ou polo | Decidir com comissão durante homologação | Questão mantida aberta; nenhuma restrição nova aprovada |
| DEC-16.5 | DP-15: um documento público por marco ou outro arranjo | Formalizar opção A praticada, se confirmada | Prática de um documento por marco; formalização pendente |

## Responsabilidade, dependências, aceite e prova de encerramento

Estado **DH** = aguardando decisão humana. Prioridade refere-se ao encaminhamento; não é nova
classificação dos 172 itens históricos. Após deliberação, registrar também impacto em specs,
plano, tarefas, testes e documentação antes de autorizar implementação.

| Identificador | Responsável proposto | Dependências | Estado / prioridade | Critério de aceite e impacto nas specs | Evidência necessária para encerramento da decisão |
|---|---|---|---|---|---|
| DEC-01 | Produto e Cefor | Edital candidato e agenda | DH / alta | Definir piloto, janela, limites e responsáveis ou adiamento explícito; orientar alvo dos incrementos | Registro assinado/confirmado pelo responsável, com data e edital ou motivo do adiamento |
| DEC-02 | TI; produto leva consulta | DEC-01 para implantação; desenho de papéis | DH / alta | Provedor, atributos, concessão e revogação definidos; 002 e futura spec de integração | Resposta da TI e aceite do produto; matriz de papéis; sem credenciais |
| DEC-03 | Encarregado e responsáveis institucionais | Inventário; DEC-12 | DH / alta | Sete questões respondidas, retenção por categoria e responsável; 060, 066, 070/071, 072 | Parecer/encaminhamento institucional identificável e condições de uso registradas |
| DEC-04 | Cefor e autoridade competente | Autoridades e atos de nomeação; DEC-03 | DH / alta | Rito, competência e fecho definidos; 054/060 e publicação | Resposta formal do Cefor, autoridades e atos aplicáveis, limites da assinatura |
| DEC-05 | Correio/TI; produto para mensagem | Infraestrutura; consulta; homologação | DH / alta | Serviço, segurança, falha uniforme e monitoramento definidos; 010/066/073 | Resposta do correio e decisão expressa de produto; teste operacional fica em controle separado |
| DEC-06 | Produto com setor de seleção | Cenários de vigência futura e bases anteriores | DH / alta | Página distinguir atos originais, retificações e cobertura sem reescrever PDF; nova spec | Escolha expressa, exemplos aprovados e limites sobre B/C/D registrados |
| DEC-07 | Produto e setor competente/jurídico | Consulta jurídica; lista da 044 | DH / média | Regra para inscrições anteriores/posteriores, complemento e prazos; 004/026/044 | Decisão temporal expressa e parecer pertinente; não aceitar apenas preferência técnica |
| DEC-08 | Produto e comissão | Caso reproduzido; contrato de estado do marco | DH / alta | Definir efeito da reabilitação no corte; 014/061 e incremento próprio, sem reutilizar faixa da 063 | Cenário aprovado com resultado esperado e alternativa escolhida |
| DEC-09 | Cefor e produto | DEC-01 | DH / média | Definir cobertura por família e procedimentos externos; avaliação, cotas e classificação | Matriz família × piloto aprovada; exclusões explícitas |
| DEC-10 | Produto, setor responsável e acessibilidade | Validação de equivalência e autenticidade | DH / média | Definir artefatos oficiais e equivalência acessível; 054/069 e nova spec | Decisão de publicação e critérios de equivalência/aprovação humana |
| DEC-11 | Cefor/jurídico e produto | Consulta jurídica | DH / média, reavaliável | Escopo e momento definidos para identidade, listas e documentos; spec própria | Resposta jurídica e decisão de prioridade com condições do piloto |
| DEC-12 | Produto, Cefor e encarregado | DEC-03 e DEC-15 | DH / média | Necessidade, momento e bloqueio da coleta definidos; 029 | Decisão expressa sobre FR-372 e fundamento institucional de tratamento |
| DEC-13 | Produto e documentação | DEC-01/14 | DH / média | Manter ou substituir plano aprovado sem apagar arquitetura histórica | Aprovação de formato, calendário e relação manual/Visão do Sistema |
| DEC-14 | Produto, comissão e representantes dos usuários | Agenda, ambiente sintético, roteiros | DH / alta | Nomear pessoas, sessões e critérios; jornadas e 069–073 | Agenda e plano de aceite aprovados; execução/homologação encerram somente depois com evidências próprias |
| DEC-15 | Produto; setor competente nos efeitos normativos | ED-47, CA-07 e pauta individual | DH / alta | Cada linha decidida ou explicitamente adiada; 026/044/054/060/029 e correlatas | Registro por linha com alternativa, autor, data, fundamento e destino de eventual mudança |
| DEC-16 | Produto | DEC-16.1 a DEC-16.5 | DH / média | Registrar as cinco deliberações; sem alteração constitucional | Cinco registros filhos e síntese sem aprovar subitem silenciosamente |
| DEC-16.1 | Produto e manutenção documental | Inventário de status e teste do README | DH / média | Definir fonte do estado e transição; templates/README/specs | Decisão sobre campo, escopo de atualização e preservação histórica |
| DEC-16.2 | Produto | Conferência da 039 | DH / média | Encerrar como registro ou retomar por plano explícito; sem exclusão | Decisão e anotação de destino da 039 autorizada |
| DEC-16.3 | Produto e setor recursal | Procedimento institucional | DH / média | Confirmar ou rever recurso sem prova nova; specs de recursos | Decisão expressa e regra institucional de referência, se aplicável |
| DEC-16.4 | Produto e comissão | DEC-14, escopos e segregação | DH / média | Definir alcance por responsabilidade; specs de comissão/autorização | Ata ou aceite da comissão e produto com cenários de permissão |
| DEC-16.5 | Produto e setor de publicação | Procedimento de divulgação | DH / média | Confirmar um documento por marco ou definir alternativa; specs de divulgação | Decisão com exemplos e tratamento de sucessões de atos |

## Registro de deliberação a preencher pelo responsável

Para cada identificador: alternativa escolhida; justificativa; autor e competência; data; link da
evidência sanitizada; condições; impacto autorizado; itens que permanecem pendentes. **Sem
deliberações preenchidas nesta fase.** A autorização de preparar estes documentos não é aprovação
do mérito das alternativas.
