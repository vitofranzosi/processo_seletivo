# Matriz de pendências — auditoria de consolidação de 15/10/2026

**Base:** `main` @ `db428b30` (merge do #282). **Entregável B** da [auditoria de consolidação](../auditoria-de-consolidacao-2026-10-15.md).

Cada item foi conferido contra o código, as specs e o histórico da `main` — e não só contra a fonte que o registrou. Os itens vêm de cinco consolidações por área, alimentadas por 185 sessões anteriores do agente (28/08 a 15/10), 74 specs, 44 achados e 14 auditorias em `doc/`, 282 PRs e uma issue, e pela varredura do código; a suíte contra PostgreSQL e um percurso pelo navegador (15/10) completam a verificação. O método e as limitações estão no relatório.

## Como ler

- **Estados** — os nove da auditoria: IMPLEMENTADO E VALIDADO · IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE · PARCIALMENTE IMPLEMENTADO · ESPECIFICADO E NÃO IMPLEMENTADO · IDENTIFICADO E NÃO ESPECIFICADO · BLOQUEADO · ADIADO FORMALMENTE · DESCARTADO OU SUBSTITUÍDO · NÃO CONFIRMADO. "Validado" exige uso real ou validação humana registrada; teste verde sozinho, quando a spec pedia pessoa, é "sem validação suficiente".
- **Prioridades** — P0 crítico · P1 alto · P2 médio · P3 evolutivo. O sistema **não está implantado** (só existe na máquina do responsável; não há candidatos reais). Por isso nenhum item é P0 de operação hoje; os P0 são **P0 para a implantação** — impedem a entrada em produção, e só passam a bloquear quando ela for decidida.
- **Itens fundidos.** A mesma pendência apareceu em mais de uma área. Fica um item canônico, com os demais IDs citados e o que cada perspectiva acrescenta; o ID fundido aparece na tabela de equivalências e não conta nos totais. A prioridade do canônico é a mais alta do grupo.
- **Origem** cita sessões pelo id de 8 caracteres e data, `L<lote>-NN` (pendência recuperada daquele lote de sessões), `RC-`/`DP-` (consolidação de 26/09 e suas decisões), `aPDF-ED-` (auditoria do PDF de 08/10), PRs (#) e specs (`NNN`, tarefa `Tnnn`). `ps/` = `backend/processo_seletivo/`, `t/` = `backend/tests/`.

## Totais

**172 itens** depois de fundir 45 registros repetidos entre áreas (217 antes da fusão).

| Estado | Itens |
|---|---|
| IMPLEMENTADO E VALIDADO | 0 |
| IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | 20 |
| PARCIALMENTE IMPLEMENTADO | 25 |
| ESPECIFICADO E NÃO IMPLEMENTADO | 8 |
| IDENTIFICADO E NÃO ESPECIFICADO | 84 |
| BLOQUEADO | 10 |
| ADIADO FORMALMENTE | 20 |
| DESCARTADO OU SUBSTITUÍDO | 1 |
| NÃO CONFIRMADO | 4 |

| Prioridade | Itens | dos quais "para a implantação" |
|---|---|---|
| P0 | 6 | 6 |
| P1 | 30 | 8 |
| P2 | 77 | 1 |
| P3 | 59 | 0 |

| Área | Itens canônicos |
|---|---|
| ED — Edital, elaboração e documento oficial | 43 |
| CA — Portal público, candidato e comunicação | 30 |
| AV — Condução do certame: avaliação, resultado, recursos, convocação | 37 |
| GO — Gestão institucional, implantação, qualidade e documentação | 39 |
| AS — Assistente de dúvidas, integrações e evolução | 18 |
| PV — Achados do percurso pelo navegador (15/10) | 5 |

## Índice — por prioridade

| ID | Item | Estado | Prior. | Decisão humana? | Fundidos |
|---|---|---|---|---|---|
| [ED-03](#ed-03) | Aprovação das frases novas da 069 antes do primeiro Edital real (SC-517) e confirmações pendentes | implementado sem validação suficiente | P0 (impl.) | sim |  |
| [ED-04](#ed-04) | Autoridade signatária: nome, ato de nomeação e forma de assinatura do ato | bloqueado | P0 (impl.) | sim | GO-11, GO-12 |
| [GO-01](#go-01) | Autenticação institucional da gestão (LDAP escolhido, nunca implementado) | especificado e não implementado | P0 (impl.) | sim | AV-01, ED-05 |
| [GO-19](#go-19) | Política de retenção e descarte (B-2) inexistente | bloqueado | P0 (impl.) | sim | AV-02, CA-03 |
| [GO-22](#go-22) | Pedido de produção à TI e definição de quem hospeda e empacota (RC-124) | adiado formalmente | P0 (impl.) | sim |  |
| [GO-25](#go-25) | Correio: único fator de acesso do candidato, porta 465 sem suporte, falha silenciosa no código de acesso | bloqueado | P0 (impl.) | sim | AS-23, CA-16 |
| [ED-06](#ed-06) | O documento oficial vigente depois de uma Retificação | identificado e não especificado | P1 (impl.) | sim | AS-05, CA-08 |
| [ED-07](#ed-07) | A Revisão de um Edital publicado e retificado mostra a norma do dia da publicação | identificado e não especificado | P1 | não |  |
| [ED-08](#ed-08) | A Retificação não acrescenta nem remove Documento Exigido | parcialmente implementado | P1 | sim |  |
| [ED-09](#ed-09) | Alcance da Etapa e Etapas por Perfil | identificado e não especificado | P1 | sim | AV-13 |
| [ED-10](#ed-10) | Famílias normativas fora do alvo (DP-10): barema, heteroidentificação, cascata de grupos, submodalidades | identificado e não especificado | P1 | sim | AV-05, AV-35 |
| [ED-11](#ed-11) | O documento oficial não é acessível a leitor de tela, e o texto só existe no PDF | identificado e não especificado | P1 | sim |  |
| [CA-01](#ca-01) | Percurso conduzido com cinco pessoas da jornada pública (SC-605) | implementado sem validação suficiente | P1 | sim |  |
| [CA-02](#ca-02) | Texto de finalidade de nome e CPF em "Seus dados" (FR-1627) | implementado sem validação suficiente | P1 | sim |  |
| [CA-04](#ca-04) | Aviso de privacidade, termo de uso e ajuda ao candidato | identificado e não especificado | P1 | sim |  |
| [CA-05](#ca-05) | Avisos aos candidatos em produção: LGPD pendente e chave sem trava | bloqueado | P1 | sim |  |
| [CA-06](#ca-06) | Modalidade de cota ao lado do nome na publicação nominal, e indexação | identificado e não especificado | P1 (impl.) | sim | AV-06 |
| [CA-07](#ca-07) | Requerimento de Matrícula: dados sensíveis, momento da coleta e base legal | implementado sem validação suficiente | P1 | sim |  |
| [CA-14](#ca-14) | Acessibilidade do portal nunca validada com pessoa nem com avaliador oficial | implementado sem validação suficiente | P1 | sim |  |
| [CA-15](#ca-15) | A jornada completa do candidato nunca foi percorrida por pessoa de fora | implementado sem validação suficiente | P1 | sim |  |
| [CA-17](#ca-17) | Atendimento ao candidato sem procedimento: correção de CPF, perda de acesso, canal por unidade | especificado e não implementado | P1 | sim | AS-27 |
| [CA-19](#ca-19) | Nome social e identidade de gênero | adiado formalmente | P1 (impl.) | sim |  |
| [CA-23](#ca-23) | O texto do reenvio da convocação sugere prazo novo | identificado e não especificado | P1 | sim | AV-24 |
| [AV-03](#av-03) | Equipe de 2–3 pessoas: julgador elegível e reavaliação por recurso | identificado e não especificado | P1 | sim | GO-07 |
| [AV-04](#av-04) | Reabilitado por recurso antes do marco não alcança o corte | identificado e não especificado | P1 | sim |  |
| [AV-07](#av-07) | Sorteio público nunca exercido de ponta a ponta com a comissão | implementado sem validação suficiente | P1 | sim |  |
| [AV-09](#av-09) | Exportação para o Registro Acadêmico e Requerimento de Matrícula: validação externa | bloqueado | P1 (impl.) | sim | AS-26 |
| [GO-03](#go-03) | Sessão: gestão não rotaciona no login, "Sair" sem `flush`, validade padrão de 2 semanas, sem limpeza | identificado e não especificado | P1 (impl.) | sim | CA-28 |
| [GO-05](#go-05) | Concessão e revisão de papéis: ninguém definido como "quem administra o sistema" | identificado e não especificado | P1 (impl.) | sim |  |
| [GO-09](#go-09) | Credencial do OpenRouter exposta em captura de tela: apagar a antiga não confirmado | não confirmado | P1 | sim | AS-11 |
| [GO-20](#go-20) | LGPD institucional: RIPD, encarregado e validações pendentes em cinco specs | bloqueado | P1 | sim |  |
| [GO-23](#go-23) | Artefatos de implantação ausentes do repositório | identificado e não especificado | P1 (impl.) | sim |  |
| [GO-24](#go-24) | Guia de implantação nunca ensaiado em VM; backup, restauração e monitoramento só como receita | implementado sem validação suficiente | P1 (impl.) | não |  |
| [GO-31](#go-31) | Teste operacional assistido (DP-18) nunca realizado; usabilidade da gestão nunca medida com servidores | especificado e não implementado | P1 | sim | AV-08, ED-01 |
| [GO-46](#go-46) | Spec 074 (assistente na página do Edital, só local) existe só numa worktree, sem commit | implementado sem validação suficiente | P1 | sim | AS-12 |
| [AS-24](#as-24) | Loteria Federal (Caixa): integração real, sem verificação contínua nem acordo | implementado sem validação suficiente | P1 | sim | AV-27, GO-33 |
| [ED-02](#ed-02) | Transcrição com conferência na homologação (E10 = B) sem roteiro nem registro | parcialmente implementado | P2 | sim |  |
| [ED-12](#ed-12) | Guarda do "objeto inteiro" na Retificação não cobre campos estruturais e derivados | identificado e não especificado | P2 | sim |  |
| [ED-13](#ed-13) | `advertencias_do_ato` subtrai impeditivos por código, e não pelo par (código, caminho) | identificado e não especificado | P2 | não |  |
| [ED-41](#ed-41) | Retificar a reversão de vagas não torna a apuração obsoleta | identificado e não especificado | P2 | sim | AV-20 |
| [ED-15](#ed-15) | Requisito × comprovante, e requisito satisfeito por uma entre várias vias | identificado e não especificado | P2 | sim |  |
| [ED-28](#ed-28) | Famílias de Edital (curso, FIC, bolsista, tutor) no catálogo e no Perfil | adiado formalmente | P2 | sim |  |
| [ED-29](#ed-29) | Cadastro de reserva: família fora do piloto (DP-05) com resíduos visíveis | adiado formalmente | P2 | sim |  |
| [ED-30](#ed-30) | Ampla concorrência: bordas que continuam abertas | parcialmente implementado | P2 | sim |  |
| [ED-31](#ed-31) | O que é comum aos Perfis mora em cada Perfil (modelo Oferta / E2) | parcialmente implementado | P2 | sim |  |
| [ED-32](#ed-32) | Comunicados: atos complementares que não são Retificação | identificado e não especificado | P2 | sim |  |
| [ED-14](#ed-14) | Validação cruzada entre fontes normativas (E-4) | parcialmente implementado | P2 | sim |  |
| [ED-16](#ed-16) | Duas gramáticas: o vocabulário normativo das telas não vem do mesmo renderizador | parcialmente implementado | P2 | sim |  |
| [ED-17](#ed-17) | Mensagens que se contradizem na composição e na Retificação | identificado e não especificado | P2 | sim |  |
| [ED-18](#ed-18) | Gravar a etapa Perfis apaga a descrição da Modalidade | identificado e não especificado | P2 | não |  |
| [ED-19](#ed-19) | Identidade do Edital: número imutável desde a criação, número queimado, ordenação textual | identificado e não especificado | P2 | sim | GO-16 |
| [ED-20](#ed-20) | A Revisão e o assistente: aviso que soterra o impeditivo e textos de fase errada | parcialmente implementado | P2 | sim |  |
| [ED-22](#ed-22) | Cronograma: Evento sem tipo controlado, sem vínculo com o marco, e cancelado impresso como vigente | parcialmente implementado | P2 | sim |  |
| [ED-23](#ed-23) | Evento só com data sai "às 00h" | adiado formalmente | P2 | sim |  |
| [ED-24](#ed-24) | Seções textuais sem tabela, subitem numerado ou negrito | adiado formalmente | P2 | sim |  |
| [ED-25](#ed-25) | Parágrafos e numeração digitada no texto colado | parcialmente implementado | P2 | sim |  |
| [ED-26](#ed-26) | Resíduos de composição do documento oficial (PDF) | parcialmente implementado | P2 | sim |  |
| [ED-27](#ed-27) | Lote 2 da linguagem simples e endereço do certame | identificado e não especificado | P2 | sim |  |
| [ED-33](#ed-33) | Cancelamento do Edital não gera Publicação | adiado formalmente | P2 | não | GO-15 |
| [ED-34](#ed-34) | Reaproveitamento de Edital anterior: resíduos | parcialmente implementado | P2 | sim |  |
| [ED-40](#ed-40) | 403 × 404 em criar Edital e reaproveitar (D-G2) | adiado formalmente | P2 | não | GO-06 |
| [CA-09](#ca-09) | O conteúdo textual do Edital não aparece no portal | identificado e não especificado | P2 | sim |  |
| [CA-10](#ca-10) | Quantidade de vagas por modalidade (lista) na página pública | adiado formalmente | P2 | sim | ED-42 |
| [CA-11](#ca-11) | Legibilidade da publicação pública do resultado | identificado e não especificado | P2 | sim |  |
| [CA-18](#ca-18) | Identidade do candidato por autodeclaração de CPF, sem verificação externa | adiado formalmente | P2 | sim |  |
| [CA-20](#ca-20) | Encerramento da participação pelo próprio candidato | identificado e não especificado | P2 | sim |  |
| [CA-21](#ca-21) | Comunicação ativa que ainda não existe | identificado e não especificado | P2 | sim |  |
| [CA-22](#ca-22) | Avisos complementares (066): validação com pessoa e resíduos do despacho | implementado sem validação suficiente | P2 | sim |  |
| [CA-25](#ca-25) | Comprovante e divulgação imprimem "?" em nome fora do cp1252 | identificado e não especificado | P2 | sim | AV-19 |
| [CA-32](#ca-32) | Modalidade nascida por Retificação gravada em silêncio no envio (RC-134) | não confirmado | P2 | não |  |
| [AV-10](#av-10) | Barema estruturado e autopontuação vinculante | adiado formalmente | P2 | sim |  |
| [AV-11](#av-11) | O ciclo depende de planilhas: sem exportação de inscritos/resultados, sem importação de notas | identificado e não especificado | P2 | sim |  |
| [AV-12](#av-12) | Comissão, alocação e distribuição sem Perfil, polo ou modalidade | identificado e não especificado | P2 | sim |  |
| [AV-14](#av-14) | Reavaliação determinada por recurso: telas não orientam o cumprimento | parcialmente implementado | P2 | não |  |
| [AV-15](#av-15) | Corrigir Resultado sem recurso (revisão de ofício / anulação) | identificado e não especificado | P2 | sim |  |
| [AV-16](#av-16) | DP-09: recurso sem prova nova (peça sem anexos) | identificado e não especificado | P2 | sim |  |
| [AV-17](#av-17) | Prazo de recurso: três fontes sem vínculo (marco × Cronograma × seção) | adiado formalmente | P2 | não | CA-31 |
| [AV-18](#av-18) | Prévia e documento da divulgação: prazo recursal, versão da janela e lista | identificado e não especificado | P2 | não |  |
| [AV-21](#av-21) | Recorte sem corte nenhum: ninguém é chamável | identificado e não especificado | P2 | sim |  |
| [AV-22](#av-22) | Cadastro de reserva não é convocável pelo sistema | adiado formalmente | P2 | sim |  |
| [AV-23](#av-23) | Nenhum ato registra matrícula efetivada ou contratação | identificado e não especificado | P2 | sim |  |
| [AV-25](#av-25) | Sorteio dá recorte próprio à Modalidade declarada como ampla (derivação divergente) | identificado e não especificado | P2 | sim |  |
| [AV-26](#av-26) | Sorteio condicionado no texto, incondicional no sistema | identificado e não especificado | P2 | sim |  |
| [AV-28](#av-28) | Trilha do Edital não reúne todos os atos da condução | parcialmente implementado | P2 | não |  |
| [AV-29](#av-29) | Ninguém é avisado: avaliador, comissão, julgador; sinais ausentes de sorteio e requerimento | identificado e não especificado | P2 | não |  |
| [AV-30](#av-30) | Encerramento do certame sem conferência do que ficou pendente; validade e prorrogação | identificado e não especificado | P2 | sim |  |
| [AV-31](#av-31) | Telas da condução nunca auditadas em UX | implementado sem validação suficiente | P2 | não |  |
| [GO-02](#go-02) | API admin e `/metrics` sem autenticação institucional; permissão `observabilidade:consultar` sem dono | identificado e não especificado | P2 | sim |  |
| [GO-04](#go-04) | Content-Security-Policy ausente e endurecimento residual do guia | especificado e não implementado | P2 | não |  |
| [GO-17](#go-17) | Lacunas da trilha de auditoria | parcialmente implementado | P2 | sim | CA-27 |
| [GO-18](#go-18) | Imutabilidade em duas camadas de três (tabelas residuais) | identificado e não especificado | P2 | sim | AV-47, CA-26, ED-39 |
| [GO-21](#go-21) | Avaliação de LGPD por spec não é sistemática | identificado e não especificado | P2 | sim |  |
| [GO-26](#go-26) | PR #283 (implementação da 073) aberto, "CONFLICTING" no GitHub, sem revisão | implementado sem validação suficiente | P2 | sim |  |
| [GO-27](#go-27) | Validação operacional da 073: roteiros B (TI em homologação) e C (Ollama na L4) | bloqueado | P2 | sim |  |
| [GO-29](#go-29) | Base de CEP: job mensal e alerta só como receita; runbook contradiz o Makefile | especificado e não implementado | P2 (impl.) | não | AS-25, AV-32 |
| [GO-30](#go-30) | SLO de carga e escala nunca medidos | especificado e não implementado | P2 | não |  |
| [GO-32](#go-32) | Repositório sem proteção de branch e sem revisão; CI sem varredura de segurança nem agendamento | identificado e não especificado | P2 | sim |  |
| [GO-36](#go-36) | Casos-limite das specs fora da matriz de requisitos | identificado e não especificado | P2 | sim |  |
| [GO-38](#go-38) | Campo `Status` das specs (DP-12) e validações humanas sem registro central | identificado e não especificado | P2 | sim |  |
| [GO-41](#go-41) | Specs e documentos de consolidação atrás das decisões já tomadas | identificado e não especificado | P2 | não |  |
| [GO-42](#go-42) | Contradições na documentação de operação e de desenvolvimento | identificado e não especificado | P2 | sim | AS-21, CA-36 |
| [GO-43](#go-43) | Manual planejado e não produzido desde 08/09 | especificado e não implementado | P2 | sim |  |
| [GO-44](#go-44) | Visão do Sistema: atrás da `main`, atualização em curso não commitada, sem ligação nem guarda | parcialmente implementado | P2 | sim |  |
| [GO-45](#go-45) | Documentos de operação institucional ausentes | identificado e não especificado | P2 | sim |  |
| [GO-47](#go-47) | Vídeos de lançamento e institucional fora do controle de versão | implementado sem validação suficiente | P2 | sim | AS-28, AS-29 |
| [AS-01](#as-01) | Revisão institucional da Fase A com o setor de seleção (T046) | implementado sem validação suficiente | P2 | sim |  |
| [AS-02](#as-02) | Detecção do canal de dúvidas erra nos Editais reais | parcialmente implementado | P2 | sim |  |
| [AS-06](#as-06) | Vocabulário das respostas: 070 × 069 e termos que os Editais não usam | identificado e não especificado | P2 | sim |  |
| [AS-07](#as-07) | Acesso à L4 / Ollama do Cefor (T058–T060) e dados da infraestrutura | bloqueado | P2 | sim |  |
| [AS-08](#as-08) | Critérios de aceite do piloto (DP-3) e conclusão | bloqueado | P2 | sim |  |
| [AS-09](#as-09) | Sessão acompanhada com o setor no piloto (T065, SC-559) | especificado e não implementado | P2 | sim |  |
| [AS-10](#as-10) | Qualidade e fundamentação das respostas (instruções v4, CB-17/CB-18, paráfrase, injeção) | implementado sem validação suficiente | P2 | sim |  |
| [PV-01](#pv-01) | Data de nascimento pedida duas vezes na mesma inscrição | identificado e não especificado | P2 | sim |  |
| [ED-35](#ed-35) | Validade/prorrogação do Edital e Editais derivados (vagas remanescentes) | identificado e não especificado | P3 | não |  |
| [ED-36](#ed-36) | Taxa de inscrição e isenção não modeladas | identificado e não especificado | P3 | não |  |
| [ED-37](#ed-37) | Objetos normativos publicados sem forma ou sem leitor | adiado formalmente | P3 | não |  |
| [ED-38](#ed-38) | Anexo publicado não diz a que serve | identificado e não especificado | P3 | sim |  |
| [ED-21](#ed-21) | Microinterações da composição e rascunho local | parcialmente implementado | P3 | não |  |
| [ED-44](#ed-44) | Tradução/interpretação de Editais em Libras (maturidade: estudo documental) | identificado e não especificado | P3 | sim |  |
| [ED-43](#ed-43) | Multiunidade: marca fixa e demais unidades | bloqueado | P3 | sim | GO-10 |
| [ED-45](#ed-45) | Contrato da API do Edital desatualizado | identificado e não especificado | P3 | não |  |
| [ED-46](#ed-46) | Encerrar formalmente a 039 (catálogo de Modalidades) | descartado ou substituído | P3 | sim | GO-39 |
| [ED-47](#ed-47) | Decisões tomadas pelo agente na área do Edital, sem aprovação explícita | implementado sem validação suficiente | P3 | sim |  |
| [CA-12](#ca-12) | Resíduos visuais da 072 e a marca da unidade no portal e nos e-mails | identificado e não especificado | P3 | não |  |
| [CA-13](#ca-13) | Lotes 2 e 3 da auditoria UX: identidade visual e o que ela adiou | adiado formalmente | P3 | sim |  |
| [CA-24](#ca-24) | Pequenas inconsistências do portal e do e-mail de confirmação | identificado e não especificado | P3 | não |  |
| [CA-29](#ca-29) | A vitrine carrega todo o conteúdo publicado, sem paginação nem índice | adiado formalmente | P3 | não |  |
| [CA-30](#ca-30) | Anexos públicos sem destinatário, sem tamanho, e figuras públicas que faltam | identificado e não especificado | P3 | sim |  |
| [CA-33](#ca-33) | Acompanhamento: custo por publicação e resíduos da revisão da 063 | identificado e não especificado | P3 | não |  |
| [CA-34](#ca-34) | Lacunas de domínio que o acompanhamento declara como ausência (063 L-4 a L-7) | identificado e não especificado | P3 | sim |  |
| [CA-35](#ca-35) | Reaproveitamento de documentos entre inscrições | adiado formalmente | P3 | não |  |
| [CA-37](#ca-37) | Entrega de documento fora do sistema: presencial, por procurador, por menor | parcialmente implementado | P3 | sim |  |
| [CA-38](#ca-38) | Condição sobre a pessoa (sexo, idade, vínculo de servidor) só informativa | adiado formalmente | P3 | sim |  |
| [AV-33](#av-33) | Página pública do resultado: o que a pesquisa recomendou | identificado e não especificado | P3 | sim |  |
| [AV-34](#av-34) | Duas avaliações por inscrição: regra de combinação | adiado formalmente | P3 | não |  |
| [AV-36](#av-36) | Reversão hierárquica e reversão dentro do polo | identificado e não especificado | P3 | não |  |
| [AV-37](#av-37) | Expressividade do desempate | identificado e não especificado | P3 | não |  |
| [AV-38](#av-38) | Segunda instância recursal | identificado e não especificado | P3 | não |  |
| [AV-39](#av-39) | Backlog do rito do sorteio | identificado e não especificado | P3 | sim |  |
| [AV-40](#av-40) | Mesa e telas da comissão: identificar a inscrição | parcialmente implementado | P3 | não |  |
| [AV-41](#av-41) | Visualização de anexos na Mesa: zoom e rotação | implementado sem validação suficiente | P3 | não |  |
| [AV-42](#av-42) | Distribuição só depois do período de inscrições | identificado e não especificado | P3 | não |  |
| [AV-43](#av-43) | "Remover da comissão" desativa alocações em cascata | parcialmente implementado | P3 | não |  |
| [AV-44](#av-44) | Convocação "por publicação": onde se publica | identificado e não especificado | P3 | sim |  |
| [AV-45](#av-45) | DP-15: documento público por marco | identificado e não especificado | P3 | sim |  |
| [AV-46](#av-46) | Filtro de concorrência das Inscrições ignora o Perfil ativo | identificado e não especificado | P3 | não |  |
| [AV-48](#av-48) | Artefatos da 019 atrás da implementação | parcialmente implementado | P3 | não |  |
| [AV-49](#av-49) | Escala da condução sem teto medido | identificado e não especificado | P3 | não |  |
| [AV-50](#av-50) | Duas ordens de travamento (risco de deadlock) | não confirmado | P3 | não |  |
| [GO-08](#go-08) | Comissão: remoção em cascata num clique e cadastro manual de membros | parcialmente implementado | P3 | não |  |
| [GO-13](#go-13) | Condução e Supervisão: resíduos que "esperam o piloto" | parcialmente implementado | P3 | sim |  |
| [GO-14](#go-14) | Visão institucional (040/041): decisões de evolução registradas e não tomadas | identificado e não especificado | P3 | sim |  |
| [GO-28](#go-28) | A release do guia não instala o grupo `assistente` (`tokenizers`) | identificado e não especificado | P3 | sim | AS-19 |
| [GO-34](#go-34) | `make test` (modo SQLite) continua vermelho | identificado e não especificado | P3 | sim |  |
| [GO-35](#go-35) | Instabilidades e armadilhas conhecidas da suíte | identificado e não especificado | P3 | sim |  |
| [GO-37](#go-37) | Limitações do guardião de citações | identificado e não especificado | P3 | não |  |
| [GO-40](#go-40) | Decisões de produto da consolidação de 26/09 sem registro (DP-09, DP-10, DP-11, DP-15) | identificado e não especificado | P3 | sim |  |
| [GO-48](#go-48) | Higiene do ambiente local (worktrees, branches, bancos, `launch.json`) | identificado e não especificado | P3 | sim |  |
| [AS-03](#as-03) | Cláusula "esclarecimentos exclusivamente por e-mail" × existência do assistente | identificado e não especificado | P3 | sim |  |
| [AS-04](#as-04) | Estatuto da resposta e limites de responsabilidade (DA-01 / DEP-08) | identificado e não especificado | P3 | sim |  |
| [AS-13](#as-13) | Protótipo da Fase C (#280): interno, sem link, com estados simulados | implementado sem validação suficiente | P3 | não |  |
| [AS-14](#as-14) | Acessibilidade e celular real do painel do assistente | implementado sem validação suficiente | P3 | não |  |
| [AS-15](#as-15) | Spec da Fase C (abertura do assistente ao candidato) não escrita | identificado e não especificado | P3 | sim |  |
| [AS-16](#as-16) | Limites por visitante, isolamento da inferência e infraestrutura para uso público | parcialmente implementado | P3 | sim |  |
| [AS-17](#as-17) | Configuração por seleção/Edital e chaves do assistente | identificado e não especificado | P3 | sim |  |
| [AS-18](#as-18) | LGPD e retenção dos registros do assistente | parcialmente implementado | P3 | sim |  |
| [AS-20](#as-20) | Achados menores da 070: guardião de cobertura e itens baixos do analyze | não confirmado | P3 | não |  |
| [AS-22](#as-22) | Assistente de acompanhamento da candidatura (área autenticada) | adiado formalmente | P3 | sim |  |
| [PV-02](#pv-02) | O comprovante fala com o candidato em linguagem técnica | identificado e não especificado | P3 | não |  |
| [PV-03](#pv-03) | A página pública "Verificar o sorteio" transborda a 375 px | identificado e não especificado | P3 | não |  |
| [PV-04](#pv-04) | O detalhe do Edital na gestão transborda a 375 px | identificado e não especificado | P3 | não |  |
| [PV-05](#pv-05) | Rótulos vazios e retificações homônimas no portal | identificado e não especificado | P3 | não |  |

## Equivalências — registros fundidos

| Registro | Fundido em | O que a perspectiva dele acrescenta |
|---|---|---|
| AS-05 — "Ler o Edital completo (PDF)" pode não conter uma Retificação em vigor | [ED-06](#ed-06) | escolher a opção (a A é só leitura e não muda publicação) e especificar. |
| AS-11 — Chave do OpenRouter exposta em captura de tela: revogação não confirmada | [GO-09](#go-09) | confirmar no painel do OpenRouter que a chave antiga foi apagada. |
| AS-12 — 074 (assistente na página pública, só local) sem commit nem PR | [GO-46](#go-46) | commit/PR; atualizar com a `main` (há #281/#282 desde a base); suíte completa; T013 pelo usuário; cuidado com o `launch.json` versionado (memória: não sobrescrever a entrada do usuário). |
| AS-19 — Release de produção não instala a biblioteca do tokenizer | [GO-28](#go-28) | escolher A/B/C; responder se o piloto roda numa máquina do guia e quem mantém o `tokenizer.json`. |
| AS-21 — Documentação do assistente desatualizada e branches residuais | [GO-42](#go-42) | atualizar os trechos; apagar as branches, a critério do usuário. |
| AS-23 — Correio (SMTP): integração real, sem validação operacional | [GO-25](#go-25) | resposta do setor de correio (587/STARTTLS ou 465); roteiro B; merge do #283. |
| AS-25 — Base de CEP: carga local, atualização mensal só como receita | [GO-29](#go-29) | ensaio da receita numa VM; revisão do runbook; amostra de CEP no seed (opcional, "se valer a pena"). |
| AS-26 — Registro Acadêmico: exportação pronta, nunca importada no destino | [AV-09](#av-09) | a conversa com o Registro Acadêmico e uma importação real. |
| AS-27 — Canal de atendimento com três fontes (Edital, implantação, unidade) | [CA-17](#ca-17) | decisão do produto; perguntas à equipe ("alguém espera respostas aos e-mails do sistema?", "quando entra a segunda unidade?"). |
| AS-28 — Filme de lançamento (worktree `ifes-launch-film-cabb9f`) | [GO-47](#go-47) | **a trilha nunca foi ouvida** (níveis só por medição); destino dos arquivos (2,1 GB não cabe em commit comum). |
| AS-29 — Vídeo institucional (worktree `processo-seletivo-video-519ad6`) | [GO-47](#go-47) | locução sintética é guia (trocar por locutor); marca oficial Ifes/Cefor na cena 23 depende de arquivo autorizado; destino dos 19 GB. |
| AV-01 — Identidade real de quem conduz (comissão, avaliador, julgador) | [GO-01](#go-01) | provedor de identidade institucional (LDAP/SSO) não escolhido nem integrado; comissão sem busca no diretório. |
| AV-02 — Retenção e descarte do acervo de avaliação e dos documentos do candidato | [GO-19](#go-19) | prazo de guarda, base legal e procedimento de descarte com o encarregado de dados. |
| AV-05 — Heteroidentificação e convocação para comparecer a Etapa | [ED-10](#ed-10) | ato de convocação para Etapa, alcance da heteroidentificação, agenda individual, exposição da autodeclaração. |
| AV-06 — Exposição da modalidade de cota ao lado do nome na lista pública | [CA-06](#ca-06) | validação com o encarregado de dados; eventual `noindex` e prazo de exposição. |
| AV-08 — Ciclo de condução sem validação com as pessoas que vão operá-lo | [GO-31](#go-31) | percurso conduzido com o setor; banco de demonstração com documentos e cotas. |
| AV-13 — Alcance da Etapa por Perfil/modalidade | [ED-09](#ed-09) | Etapa aplicável a subconjunto; encerramento da 039 (DP-08 item 1). |
| AV-19 — Nome de candidato fora do cp1252 vira "?" no documento do resultado e no comprovante | [CA-25](#ca-25) | fonte com repertório amplo ou recusa/aviso na publicação do resultado. |
| AV-20 — Reversão de vagas retificada não torna a apuração obsoleta (RC-129) | [ED-41](#ed-41) | sexta causa ou decisão de que reversão retificada não alcança apurações emitidas. |
| AV-24 — Redação do reenvio da convocação sugere prazo novo | [CA-23](#ca-23) | redação que diga o vencimento absoluto; aviso de envio tardio. |
| AV-27 — E2E contra a fonte real da Caixa não roda em lugar nenhum | [AS-24](#as-24) | gatilho periódico ou passo obrigatório antes de cada sorteio. |
| AV-32 — Base de CEP sem job mensal nem alerta | [GO-29](#go-29) | timer versionado e alerta. |
| AV-35 — Cascata de grupos, submodalidades e ordem de convocação | [ED-10](#ed-10) | modelo de grupos e ordem de convocação. |
| AV-47 — Append-only com duas camadas em PosicaoNaOrdem e GeracaoDeArquivo | [GO-18](#go-18) | terceira camada. |
| CA-03 — Retenção e descarte dos dados do candidato | [GO-19](#go-19) | prazo e responsável não definidos; sem expurgo de rascunho abandonado, desafio, sessão (o `clearsessions` é só receita do guia) e documento. A promessa do comprovante não tem regra por trás. Aviso de privacidade ausente (CA-04). |
| CA-08 — "Ler o Edital completo (PDF)" liga a documento sem a Retificação em vigor | [ED-06](#ed-06) | o rótulo promete "completo" e o documento não é. O histórico de Retificações aparece na mesma lista, mas não junto do link. |
| CA-16 — O acesso do candidato depende só do e-mail, e a falha de envio é silenciosa | [GO-25](#go-25) | sem métrica ou alerta de falha de envio do código, sem verificação periódica do correio fora da 073 e sem caminho alternativo de acesso. |
| CA-26 — Imutabilidade da inscrição enviada só no modelo, sem gatilho no banco | [GO-18](#go-18) | falta a segunda camada (gatilho que recusa `UPDATE` e `DELETE` quando o status anterior é `SUBMETIDA`). |
| CA-27 — Atos do candidato fora da trilha de auditoria | [GO-17](#go-17) | não há como responder "quem entrou nesta conta e quando" nem "o titular baixou o documento". |
| CA-28 — Sessão do candidato longa e "Sair" incompleto | [GO-03](#go-03) | em computador compartilhado (laboratório, lan house), a conta fica aberta por duas semanas para quem não clicar em "Sair". Mesmo clicando, o destino guardado sobrevive. |
| CA-31 — Recurso pelo candidato: prazo da tela × Cronograma, e o custo do parecer temporário | [AV-17](#av-17) | (a) a contradição continua visível ao candidato quando o Edital diverge. (b) é revisável. |
| CA-36 — Documentação desatualizada sobre o portal e os avisos | [GO-42](#go-42) | documentação diverge do código. |
| ED-01 — A elaboração nunca foi validada por quem elabora | [GO-31](#go-31) | nenhum documento de resultado de teste com pessoa do setor; `specs/002/tasks.md` T059 aberta; `specs/044/tasks.md:234` T065 aberta; DP-18 sem decisão de quem/quando. |
| ED-05 — A segregação elaborar × homologar × publicar só é real com identidade institucional | [GO-01](#go-01) | provedor de identidade institucional inexistente (zero ocorrências de LDAP/OIDC/SAML no código); piso de identidades não decidido. |
| ED-39 — `ProvenienciaConteudo` não é append-only | [GO-18](#go-18) | gatilho + privilégio ausente (as duas camadas da Constituição); migration nova. |
| ED-42 — Quadro de vagas por modalidade fora da página pública | [CA-10](#ca-10) | decisão de quando. |
| GO-06 — D-G2: três recusas devem passar de 404 para 403 (decidido, adiado para a produção) | [ED-40](#ed-40) | implementação + emenda do inventário; a DP-07 não tem o bloco "O que foi decidido". |
| GO-07 — Arranjo mínimo de 2–3 pessoas: tabela nunca percorrida e três perguntas de governança abertas | [AV-03](#av-03) | percurso das duas configurações; decisão sobre aviso antecipado de julgador inelegível. |
| GO-10 — Multiunidade: implementada no modelo, mas só uma unidade exercitável | [ED-43](#ed-43) | marca por unidade, atendimento por unidade, cadastro das demais unidades, escopo vindo da autenticação (GO-01). |
| GO-11 — Autoridades do Cefor não cadastradas, e o go-live do guia não manda cadastrar | [ED-04](#ed-04) | passo no go-live (`doc/implantacao-em-producao-ubuntu.md:2775-2849`) e percurso com dado real da unidade. |
| GO-12 — Assinatura do ato e nome de quem assina (DP-20 itens 4–5, ED-10) | [ED-04](#ed-04) | resposta do Cefor sobre forma de assinatura e uso de nome próprio. |
| GO-15 — Cancelamento do Edital não gera Publicação (RC-120) | [ED-33](#ed-33) | ato público de cancelamento. |
| GO-16 — Cancelar Edital "queima" o número/ano | [ED-19](#ed-19) | decidir se número de Edital cancelado pode ser reusado (prática administrativa do Cefor). |
| GO-33 — E2E contra a fonte real do sorteio (Caixa) não roda em lugar nenhum | [AS-24](#as-24) | gatilho (agendado ou rotina antes de cada sorteio). |
| GO-39 — A 039 (catálogo de Modalidades) nunca implementada nem encerrada (DP-08) | [ED-46](#ed-46) | encerramento formal. |

## ED — Edital, elaboração e documento oficial

<a id="ed-02"></a>
#### ED-02 — Transcrição com conferência na homologação (E10 = B) sem roteiro nem registro
- Descrição: em 28/09 o usuário decidiu que o setor continua redigindo no Word e transcreve no sistema;
  quem homologa confere a prévia contra o original (lista do item 3 da DP-20). Nada disso está no código
  (por decisão), mas também não há roteiro operacional para o homologador, nem registro de que a
  conferência aconteceu. O estudo de 21/09 mediu 0 de 7 atos normativos transcritos de memória (RC-25).
  O estudo de Libras registra a questão vizinha "qual redação vale, a do sistema ou a da casa".
- Origem (demanda/decisão): L07-51 (183ba11d, 21/09, "O Cefor vai redigir no sistema ou transcrever?");
  DP-20 E10; RC-25; L07-53 (citações legais sem conferência); `docs/libras/viabilidade.md` §11.
- Decisão aplicável: E10 = B, 28/09 (`doc/decisoes-pendentes-da-consolidacao.md:1393`); avisos na
  Revisão = sim (anexo citado sem rótulo; seção com redação padrão), implementados no #220; a 054 retirou a
  redação padrão.
- Spec / PRs / commits: DP-20 (#213), #220, 054 (#233).
- Implementação: avisos na Revisão (`ps/interface/revisao.py`); nenhuma lista de conferência na tela de
  homologação.
- Testes: `t/unit/publicacoes/test_fecho_e_normas_da_054.py` (avisos/fecho); nenhum da conferência.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: manual do homologador ausente (`inventario-documental.md` §4); sem registro (nem opcional) da
  conferência; a opção C (conferência assistida) não foi escolhida.
- Impacto: homologador; candidato (norma omitida no ato oficial).
- Prioridade: P2 — o risco é de processo e a decisão já existe; falta torná-lo executável.
- Dependências: ED-01 (o teste é o lugar barato de conferir), ED-03.
- Próxima ação recomendada: escrever a lista de conferência do homologador (item 3 da DP-20) como página do
  manual ou ajuda da tela de homologação; medir no teste do ED-01.
- Precisa de decisão humana? sim — se a conferência deve ficar registrada no ato (texto de declaração na
  homologação, oferecido como opção na DP-20).
- Confiança: alta — decisão literal e ausência de código conferidas.

<a id="ed-03"></a>
#### ED-03 — Aprovação das frases novas da 069 antes do primeiro Edital real (SC-517) e confirmações pendentes
- Descrição: a 069 reescreveu o próprio ato em linguagem simples. A spec exige que **toda frase nova**
  (marcadas "+" em `demonstracao/equivalencia.md`, ex.: resumo A3, K7/A21 dos suplentes) seja aprovada pelo
  responsável pelo produto antes da publicação do 1º Edital real; não há registro de aprovação. Também
  pendentes: confirmação jurídica do resumo dentro do ato (D-005, não bloqueia) e teste com candidatos (Lei
  15.263, art. 5º, XVIII) com o 1º Edital real.
- Origem (demanda/decisão): L09-88 (46626552, 12/10); S-069-01/02; c.11 SC-517, D6; github §1.3 (#275).
- Decisão aplicável: direção da 069 aprovada pelo usuário em 12/10 (escrever o próprio ato em linguagem
  simples); D-003 (Editais antigos retificados mantêm forma); a aprovação de cada frase não foi registrada.
- Spec / PRs / commits: 069 (#275, `01368bb5`), tasks 72/72.
- Implementação: `ps/publicacoes/infrastructure/pdf.py` (redação 2), `ps/editais/domain/secoes.py:126+`
  (`CATALOGO_DA_069`).
- Testes: `t/unit/publicacoes/test_redacao_das_frases.py`, `test_apresentacao_por_perguntas.py`,
  `test_documento_da_auditoria_depois_da_069.py`.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: `specs/069-edital-linguagem-simples/spec.md:695` (SC-517) e `rastreabilidade.md:89` sem
  registro de aprovação; D-005 sem resposta da área jurídica.
- Impacto: candidato (o texto normativo que ele lê); instituição (o ato oficial).
- Prioridade: P0 para a implantação — a própria spec faz da aprovação condição para publicar o 1º Edital
  real, e o custo é uma leitura humana.
- Dependências: ED-02; ED-27 (lote 2).
- Próxima ação recomendada: o usuário percorre `equivalencia.md`, aprova ou corrige cada "+" e registra a
  data na rastreabilidade; encaminhar D-005 à área jurídica.
- Precisa de decisão humana? sim — aprovar as frases (produto); estatuto do resumo (jurídico).
- Confiança: alta — critério e ausência de registro conferidos no repositório.

<a id="ed-04"></a>
#### ED-04 — Autoridade signatária: nome, ato de nomeação e forma de assinatura do ato
- Descrição: a 060 tornou a Autoridade cadastrável pela tela (cargo obrigatório; nome e ato de nomeação
  opcionais) e a 054 pôs local, data e ato de nomeação no fecho. Sem autoridade cadastrada **não se
  publica** (o catálogo em código saiu). Seguem com o Cefor: o nome de quem assina, a conferência do cargo
  ("Diretora-Geral" × "Diretora" no 28/2026), a portaria, e **qual arquivo é o oficial e onde ele é
  assinado** (DP-20 itens 4 e 5; aPDF-ED-10). Base legal LGPD dos dados de autoridade com o encarregado
  (060).
- Origem (demanda/decisão): L01-56/57 (71daf8d4, 30/08); L08-21 (2bc3c441/a083f5e1, 28–29/09); L09-26,
  L09-27, L09-28 (a1ccd396, 06/10); L09-63 (ED-10); RC-23; DP-20; S-060-02/03/05; github §1.1 (#233,
  #239).
- Decisão aplicável: 28/09 "o PDF vai ser o documento oficial"; 06/10 "assinatura dentro do sistema não
  faz sentido"; FR-1122 (060): Gestor da unidade cadastra autoridades; itens 4 e 5 da DP-20 explicitamente
  fora ("com o Cefor").
- Spec / PRs / commits: 054 (#233), 060 (#254).
- Implementação: `ps/unidades/models.py:59-83` (`cargo`, `nome`, `ato_de_nomeacao`); tela
  `/gestao/autoridades` (`ps/interface/urls.py:23`).
- Testes: `t/unidades/` e testes da 060 (cadastro, vigência, gatilhos N1/N2).
- Estado: BLOQUEADO
- Lacuna: nenhuma autoridade real cadastrada; resposta do Cefor sobre assinatura e nome; validação LGPD
  sem registro (`doc/pendencias-da-060.md:30-50`).
- Impacto: instituição/gestor (validade do ato); candidato (ato sem identificação de quem assina).
- Prioridade: P0 para a implantação — sem o cadastro nenhum Edital publica, e sem a resposta sobre
  assinatura o PDF "oficial" não tem forma de validade definida.
- Dependências: ED-05 (identidade de quem publica); B-1 (outra área).
- Próxima ação recomendada: levar ao Cefor as perguntas da DP-20 (itens 4 e 5) e da 060 numa só
  reunião; cadastrar as autoridades na preparação da implantação; registrar a base legal com o encarregado.
- Precisa de decisão humana? sim — institucional (Cefor: assinatura e nome; encarregado: LGPD).
- Confiança: alta — campos opcionais e recusa sem autoridade conferidos; pendência registrada em quatro
  documentos.
- **Fundidos neste item:** GO-11, GO-12.
  - *GO-11 (GO), Autoridades do Cefor não cadastradas, e o go-live do guia não manda cadastrar* — lacuna: passo no go-live (`doc/implantacao-em-producao-ubuntu.md:2775-2849`) e percurso com dado real da unidade. Próxima ação: acrescentar o passo ao go-live do guia; obter do Cefor a lista de cargos. - Precisa de decisão humana? sim — quais cargos o Cefor declara.
  - *GO-12 (GO), Assinatura do ato e nome de quem assina (DP-20 itens 4–5, ED-10)* — lacuna: resposta do Cefor sobre forma de assinatura e uso de nome próprio. Próxima ação: pergunta formal ao Cefor (um parágrafo, com as opções), registrar a resposta na DP-20. - Precisa de decisão humana? sim — institucional (Cefor).

<a id="ed-06"></a>
#### ED-06 — O documento oficial vigente depois de uma Retificação
- Descrição: (a) o link "Edital completo (PDF)" da página da seleção aponta o documento da
  `source_publication` da versão vigente, que pode **não conter uma Retificação em vigor** (reproduzido em
  dois casos, LAC-07); (b) uma Retificação com vigência futura troca a versão vigente sem publicação nova,
  e cada consumidor precisa reler a versão; (c) a versão gerada por Retificação não lista a publicação
  original entre os atos aplicados (a 070 contorna); (d) o consolidado marca "retificado em", mas não diz o
  que mudou (aPDF-ED-06; núcleo "retificação e histórico" da pesquisa de 07/10).
- Origem (demanda/decisão): achado #10 (`doc/achado-documento-ligado-nao-contem-a-versao-vigente.md`,
  12/10); L10-05, L10-67, L10-68 (84c96e5f); DA-12; L09-44 (288c08d9); aPDF-ED-06; c.7 núcleo 3.
- Decisão aplicável: nenhuma registrada (quatro opções no achado); 070/071 o tratam como dependência da
  Fase C.
- Spec / PRs / commits: 054 (consolidado datado, FR-995); 070 (#274); 069 lote 2 (ED-06, sem spec).
- Implementação: `ps/portal/views.py:151` (`publicacao_id: versao.source_publication_id`);
  `ps/portal/templates/portal/selecao.html:64`; `ps/publicacoes/infrastructure/pdf.py:1180-1193` (marca
  de retificado, sem lista de alterações).
- Testes: `t/integration/portal/test_documento_oficial.py` confere o link, não o conteúdo.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: nenhuma spec corrige (a), (b) ou (d).
- Impacto: candidato (lê norma desatualizada no documento que o portal chama de "completo").
- Prioridade: P1 — o PDF é o ato oficial e a página leva o candidato a uma versão que não vigora.
- Dependências: ED-16; ED-27.
- Próxima ação recomendada: o usuário escolhe entre as opções A–D do achado; especificar junto com o
  aPDF-ED-06 ("o que mudou" no consolidado), que pertencem ao mesmo núcleo.
- Precisa de decisão humana? sim — qual documento a página oferece quando há Retificação de vigência
  futura.
- Confiança: alta — código conferido; reprodução registrada no achado.
- **Fundidos neste item:** AS-05, CA-08.
  - *AS-05 (AS), "Ler o Edital completo (PDF)" pode não conter uma Retificação em vigor* — lacuna: escolher a opção (a A é só leitura e não muda publicação) e especificar. Próxima ação: decidir entre A–D; a A (dizer quais atos o documento contém e listar os demais em vigor) é a de menor custo. - Precisa de decisão humana? sim — escolha da opção.
  - *CA-08 (CA), "Ler o Edital completo (PDF)" liga a documento sem a Retificação em vigor* — lacuna: o rótulo promete "completo" e o documento não é. O histórico de Retificações aparece na mesma lista, mas não junto do link. Próxima ação: decidir entre as opções do achado. A contenção mínima é trocar o rótulo e pôr junto dele "alterado por N Retificações — veja abaixo". - Precisa de decisão humana? sim — qual das quatro opções.

<a id="ed-07"></a>
#### ED-07 — A Revisão de um Edital publicado e retificado mostra a norma do dia da publicação
- Descrição: a tela de Revisão de um Edital já publicado é a mesma da composição e lê o relacional
  (`edital_snapshot`), que a Retificação não reescreve. Quem a abre depois de uma Retificação vê os valores
  antigos, sem aviso.
- Origem (demanda/decisão): RC-152 (AUD 29/09); L08-23 (2bc3c441); resíduo do achado #37; memória
  "Retificação não reescreve o relacional".
- Decisão aplicável: nenhuma registrada (estava na lista "11 correções antes do piloto", sem execução).
- Spec / PRs / commits: nenhum.
- Implementação: `ps/interface/views.py:1557` (`snapshot_da_revisao = edital_snapshot(edital)`).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a tela não lê `effective_version` nem avisa que há Retificação vigente.
- Impacto: equipe de seleção, presidência, homologador (conferem regra errada).
- Prioridade: P1 — a equipe decide sobre a norma que lê, e a tela mostra uma norma revogada.
- Dependências: ED-06.
- Próxima ação recomendada: correção direta — em Edital publicado, a Revisão lê a versão vigente (ou
  avisa e liga ao consolidado); confirmar no navegador antes.
- Precisa de decisão humana? não.
- Confiança: alta — código conferido; não reproduzido no navegador nesta rodada.

<a id="ed-08"></a>
#### ED-08 — A Retificação não acrescenta nem remove Documento Exigido
- Descrição: E2E-004 (03/09) foi dado pelo usuário como P0 antes do primeiro certame real. A metade
  "Etapa" caiu no #28 e a edição dos documentos existentes no #32; acrescentar e remover documento
  dependem de decisão normativa sobre quem já se inscreveu. A tela da Retificação acrescenta só Perfil,
  Evento e Anexo (mais Modalidade, linha do quadro, critério, corte, janela, reversão pela 048). Também:
  Documento para Modalidade nova e Modalidade de Perfil acrescentado no mesmo ato só entram na Retificação
  seguinte; Edital publicado com documento repetido por Perfil não se reduz por Retificação (D-009 da 044).
- Origem (demanda/decisão): L03-37 (533156c5, 03/09); L08-41 (b53bd3c2, 26/09); S-044-03; RC-104
  ("DESCARTADA/contradita" na AUD).
- Decisão aplicável: 03/09 "E2E-004 é P0 antes da primeira seleção real" e, no mesmo dia, "implementa só
  a edição dos existentes" (acrescentar/remover aguardam decisão normativa).
- Spec / PRs / commits: #28, #32, 044, 048 (#197).
- Implementação: `ps/interface/retificacao.py:1630` (`SECOES_QUE_ACRESCENTAM = {"perfis", "cronograma",
  "anexos"}`).
- Testes: `t/integration/editais/test_mutabilidade_dos_requisitos.py`; `t/unit/interface/test_retificacao_estrutural.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: regra normativa para inscrições já enviadas quando a lista exigida muda (a 044 grava a lista
  exigida na inscrição, o que dá a base); tela e gramática.
- Impacto: equipe de seleção (erro de documento no Edital publicado sem conserto); candidato.
- Prioridade: P1 — documento exigido errado é dos erros mais comuns em Edital e hoje não tem conserto
  pela tela.
- Dependências: ED-15.
- Próxima ação recomendada: o usuário decide o efeito sobre inscrições enviadas (vale para quem se
  inscreve depois? reabre envio?); depois spec curta.
- Precisa de decisão humana? sim — efeito normativo sobre quem já se inscreveu.
- Confiança: alta — conjunto de seções que acrescentam conferido.

<a id="ed-12"></a>
#### ED-12 — Guarda do "objeto inteiro" na Retificação não cobre campos estruturais e derivados
- Descrição: desde o #217 (RC-130) a substituição de um objeto inteiro pela API não troca campo não
  retificável; mas `code` de Perfil e de marco, `order` e `status` do Evento (estrutural/derivado) ainda
  podem ser trocados por essa porta. Relacionado e não confirmado: a linha acrescentada por Retificação em
  Perfil e Evento gera `uuid4` a cada montagem (só o Anexo ficou idempotente; L04-16).
- Origem (demanda/decisão): achado #27 (28/09); RC-139; A-6 da 048; L08-29 (fcb99e17); L04-16 (ac086e7a,
  07/09); github §1.3 (#217, #197).
- Decisão aplicável: nenhuma; AUD §13 item 25 aberto.
- Spec / PRs / commits: 048, #217.
- Implementação: `ps/publicacoes/domain/colecoes.py:337-359` (filtra só `Natureza.NAO_RETIFICAVEL`);
  `ps/interface/retificacao.py:1960,2013` (`uuid4()` em Perfil/Evento novos).
- Testes: `t/unit/publicacoes/test_colecoes.py` (só o não retificável).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: estender a guarda às naturezas estrutural e derivada; nenhum teste da porta aberta.
- Impacto: integridade do ato (só pela API admin, que nenhuma tela usa).
- Prioridade: P2 — só alcançável pela API, que em produção não tem autenticação institucional.
- Dependências: B-1.
- Próxima ação recomendada: decidir estender a guarda (recomendação natural: sim) e escrever o teste que
  hoje falta.
- Precisa de decisão humana? sim — estender a guarda (AUD §13 item 25).
- Confiança: alta para a guarda (código conferido); baixa para o `uuid4` (efeito não reproduzido).

<a id="ed-13"></a>
#### ED-13 — `advertencias_do_ato` subtrai impeditivos por código, e não pelo par (código, caminho)
- Descrição: na confirmação da Retificação, um código impeditivo num Perfil apaga em silêncio a
  advertência de mesmo código em outro Perfil. Issue #117 aberta desde 15/09 (único item pendente no
  GitHub além do #283).
- Origem (demanda/decisão): L05-68 (ae3ad7c8, 15/09); L07-72 (9b6bb684, 21/09); L08-13; RC-125; issue #117.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 027 (FR-336); issue #117 (OPEN, conferido por `gh`).
- Implementação: `ps/publicacoes/application/retificacoes.py:749-755` (`if item.code not in impeditivos`).
- Testes: nenhum do caso multi-Perfil.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: comparar pelo par; teste com dois Perfis.
- Impacto: equipe de seleção (perde aviso na tela em que assina o ato).
- Prioridade: P2 — perde só advertência, mas na tela de assinatura.
- Dependências: nenhuma.
- Próxima ação recomendada: correção direta com teste; fechar a #117.
- Precisa de decisão humana? não.
- Confiança: alta — código conferido.

<a id="ed-41"></a>
#### ED-41 — Retificar a reversão de vagas não torna a apuração obsoleta
- Descrição: nenhuma causa de obsolescência compara a reversão (`vacancyReversion`); a apuração emitida
  sob a declaração anterior continua vigente depois de uma Retificação que a muda. Fronteira com ocupação.
- Origem (demanda/decisão): A-2 da 048 (b53bd3c2, 26/09); L08-39; RC-129; AUD §13 item 19.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 048, 016.
- Implementação: `ps/ocupacao/application/selectors.py:67-` (`causas_de_obsolescencia` sem reversão).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão e causa nova.
- Impacto: comissão (apuração errada sem aviso); candidato.
- Prioridade: P2 — caso raro (Retificação de reversão depois de apuração), mas silencioso.
- Dependências: área de ocupação/classificação.
- Próxima ação recomendada: decidir; se sim, acrescentar a causa.
- Precisa de decisão humana? sim — a reversão retificada obsoleta a apuração?
- Confiança: média — pela auditoria de 15/10 e pela AUD; não relido o selector.
- **Fundidos neste item:** AV-20.
  - *AV-20 (AV), Reversão de vagas retificada não torna a apuração obsoleta (RC-129)* — lacuna: sexta causa ou decisão de que reversão retificada não alcança apurações emitidas. Próxima ação: decidir RC-129. - Precisa de decisão humana? sim — RC-129.

<a id="ed-09"></a>
#### ED-09 — Alcance da Etapa e Etapas por Perfil
- Descrição: a Etapa pertence ao Edital e vale para todos os Perfis; a Constituição admite Etapas
  distintas por Perfil. Consequência registrada: o candidato é distribuído, avaliado e pode ser eliminado
  numa Etapa que o marco dele nunca conta (heteroidentificação só para PPI, ficha de avaliação por curso).
  Saiu da 039 pela cláusula de escape e não voltou.
- Origem (demanda/decisão): L02-03 (8f779c78, 30/08); L04-02 (L-2, 8af9d708, 07/09); L05-06; L06-37
  (3bd46d67, 20/09); AX-4; DP-08 item 3; S-006-01; S-014-02.
- Decisão aplicável: 30/08 "Etapas por Edital" (clarify da 006, resposta não transcrita); 20/09 o usuário
  respondeu "Mantém junto, como está" e a reescrita da 039 o tirou; DP-08 item 3 e DP-10 abertos (a
  "leitura estrita da Constituição sobre Etapas por Perfil é do usuário").
- Spec / PRs / commits: 006, 039 (registro, #175).
- Implementação: `ps/editais/models/etapas.py:11-24` (FK só para Edital; docstring: "preço que se paga
  quando houver um Edital real que precise disso").
- Testes: nenhum do alcance.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: modelo, composição, distribuição e consolidação conscientes de alcance.
- Impacto: candidato (avaliado em Etapa que não é dele); comissão.
- Prioridade: P1 — o 28/2026, Edital do piloto, tem heteroidentificação; sem alcance ela fica fora do
  sistema ou se aplica a todos.
- Dependências: ED-10; DP-10.
- Próxima ação recomendada: decidir DP-08 item 3 junto da DP-10 com o 28/2026 na mão.
- Precisa de decisão humana? sim — DP-08 item 3 / leitura da Constituição.
- Confiança: alta — modelo conferido.
- **Fundidos neste item:** AV-13.
  - *AV-13 (AV), Alcance da Etapa por Perfil/modalidade* — lacuna: Etapa aplicável a subconjunto; encerramento da 039 (DP-08 item 1). Próxima ação: decidir DP-08 (encerrar a 039 e o destino do alcance). - Precisa de decisão humana? sim — DP-08 itens 1 e 3.

<a id="ed-10"></a>
#### ED-10 — Famílias normativas fora do alvo (DP-10): barema, heteroidentificação, cascata de grupos, submodalidades
- Descrição: o Edital não tem onde declarar barema (critérios com pontuação/teto, autopontuação
  vinculante), heteroidentificação como fluxo, grupos em cascata (ordem de chamada, não quantidade — os
  avisos empurram para repartir vagas falsamente) nem submodalidades de PPIQ (pretos/pardos, indígenas,
  quilombolas), que o 140/2025 e o 89/2026 tratam separadamente em convocação, reversão e documentos.
  Custo registrado: a apuração paralela em planilha continua no Edital 14 (barema).
- Origem (demanda/decisão): L03-57 (eeca206a, 03/09); L04-79; L05-81; L05-88 (a6849fe4, 15/09); L06-14,
  L06-15, L06-16 (3bd46d67, 16/09); L07-70; L08-04 (6fefec8a/a083f5e1); RC-55, RC-59, RC-64, RC-65; DP-10;
  T-5 de `specs-001-037.md`; registro de 09/10 (convocação para Etapa, heteroidentificação).
- Decisão aplicável: D-4 (barema fora do primeiro vertical, 04/09); 03/09 "o alvo são os editais menores";
  19/09 "generalizar, não particularizar"; DP-10 aberta; DP-11 (comissão por Perfil) aberta.
- Spec / PRs / commits: nenhuma (fora de escopo em 012–021, 030, 044).
- Implementação: inexistente (`grep autopontua` vazio; Modalidade só por código).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão de alvo e specs por família.
- Impacto: equipe de seleção (planilha paralela), comissão, candidato cotista.
- Prioridade: P1 — define se Editais com títulos e cotas detalhadas saem do papel; o objetivo de eliminar
  planilhas não se cumpre sem barema.
- Dependências: ED-09; DP-11 (outra área).
- Próxima ação recomendada: decidir a DP-10 família a família, com Editais reais do piloto previsto.
- Precisa de decisão humana? sim — DP-10.
- Confiança: alta — repetido por oito fontes, código conferido.
- **Fundidos neste item:** AV-05, AV-35.
  - *AV-05 (AV), Heteroidentificação e convocação para comparecer a Etapa* — lacuna: ato de convocação para Etapa, alcance da heteroidentificação, agenda individual, exposição da autodeclaração. Próxima ação: responder as 5 perguntas do registro de 09/10 e decidir DP-10 para heteroidentificação. - Precisa de decisão humana? sim — DP-10 e as 5 perguntas do registro.
  - *AV-35 (AV), Cascata de grupos, submodalidades e ordem de convocação* — lacuna: modelo de grupos e ordem de convocação. Próxima ação: decidir DP-10. - Precisa de decisão humana? sim — DP-10.

<a id="ed-15"></a>
#### ED-15 — Requisito × comprovante, e requisito satisfeito por uma entre várias vias
- Descrição: requisito do Perfil é lista de texto; Documento Exigido aponta um Perfil (ou um código de
  Modalidade, desde a 044). Nada liga requisito a comprovante: no 140/2025, residência vale para 16 Perfis e
  o comprovante é exigido só do TP-01. Requisito "por uma entre várias vias" (P-13) e requisito declarado e
  nunca verificado (P-9) também não têm forma; as fontes textuais já se contradizem (AX-2).
- Origem (demanda/decisão): achado #35 (12/10); L09-91 (46626552); AX-2 (L05-80, 15/09); P-9, P-13
  (L05-38); RC-26 (resto, "fica com a E2").
- Decisão aplicável: 069/070 reproduzem o dado como declarado, de propósito; três perguntas do achado sem
  resposta.
- Spec / PRs / commits: 044 (#173).
- Implementação: `ps/editais/models/perfis.py:20` (`requirements` JSON de texto);
  `ps/editais/models/documentos.py:32,63`.
- Testes: nenhum do vínculo.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: modelo do vínculo (ou aviso na Revisão).
- Impacto: candidato (exigência desigual entre Perfis); comissão (análise documental).
- Prioridade: P2 — erro de autoria que a validação poderia apontar, sem bloquear operação.
- Dependências: ED-14; ED-31 (E2).
- Próxima ação recomendada: responder as três perguntas do achado; a saída barata é aviso de conferência
  na Revisão.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="ed-28"></a>
#### ED-28 — Famílias de Edital (curso, FIC, bolsista, tutor) no catálogo e no Perfil
- Descrição: o catálogo tem 22 seções (054) e serve às quatro famílias da amostra pela "Informações
  gerais" (069), mas não tem Mobilidade entre perfis, Curso de formação, Pagamento da bolsa nem "Das
  Vagas"; o Perfil fala a língua de emprego (carga horária, remuneração, atribuições) e não tem turma,
  horário nem polo como campos; filtrar seções por tipo de Edital ficou fora. O estudo do Q4 (curso, cargo e
  bolsa), decidido em 12/10, não existe.
- Origem (demanda/decisão): L05-39 (ffc0d6a5, 12/09); L05-70 (natureza do Edital); L05-72; L05-82 (AX-3);
  L06-11 (ACH-52); L07-52; L08-71/L08-72 (a083f5e1, 29/09); achado #13 (89/2026); C-09; Q4.
- Decisão aplicável: 29/09 "não, deixa como está" (seções de bolsista); 29/09 catálogo de 22 entradas
  (054); 12/10 Q4 "estudo separado, sem campo novo"; 19/09 "genérico o suficiente para alunos e bolsistas".
- Spec / PRs / commits: 054 (#233), 069 (#275), 072 (Q4).
- Implementação: `ps/editais/domain/secoes.py:82-121` (catálogo 054) e `:126+` (069).
- Testes: `t/unit/publicacoes/test_apresentacao_por_perguntas.py`.
- Estado: ADIADO FORMALMENTE
- Lacuna: o estudo Q4; o primeiro Edital real de bolsista dirá se as seções faltam (mudar o catálogo
  depois da 1ª publicação real pede versão de catálogo).
- Impacto: elaborador de Edital de bolsista/FIC; candidato.
- Prioridade: P2 — há caminho (seções genéricas) e decisão registrada; o risco é o custo de mudar o
  catálogo depois da primeira publicação.
- Dependências: ED-31.
- Próxima ação recomendada: fazer o estudo Q4 antes do primeiro Edital real de bolsista.
- Precisa de decisão humana? sim — escopo do estudo Q4.
- Confiança: alta.

<a id="ed-29"></a>
#### ED-29 — Cadastro de reserva: família fora do piloto (DP-05) com resíduos visíveis
- Descrição: Edital/Perfil só de cadastro de reserva publica sem quadro e sem reversão (067), mas: a regra
  de reserva no cadastro (como os percentuais se aplicam, RC-58/aPDF-ED-12) não foi decidida; o Perfil só
  de reserva ainda imprime o corte "os 10 primeiros" e é obrigado a declarar corte (o 89/2026 inventou 50);
  `reserveLimit` aceita 0 (portal promete "até 0"); o tipo de reserva não é retificável; a repartição do
  cadastro por Modalidade (76/2026) e a reserva conjunta (CAPES 25%) não têm forma; convocar do cadastro é
  feito fora do sistema.
- Origem (demanda/decisão): L04-105 (c9ff00d8, 10/09); L08-47 (3f708cd8, 27/09); L08-71; L08-86; L09-33
  (b2bc7d37, 06/10); L09-34; L09-67, L09-68 (4d4cd6b0); RC-58; RC-135; DP-05; P-2.
- Decisão aplicável: DP-05 = B (fora do piloto, 27/09); D-011 da 025 = A (quadro reparte só vaga
  imediata, 10/09); 09/10 D-003 da 067 "omitir quadro e reversão"; spec própria só "quando houver Edital
  concreto".
- Spec / PRs / commits: 025, 067 (#268), aviso `reserve_only_convocation_external`.
- Implementação: `ps/editais/domain/validation.py:107` (`reserveLimit` mínimo 0), `:3338` (aviso).
- Testes: `t/unit/publicacoes/test_perfil_sem_vaga_imediata.py`.
- Estado: ADIADO FORMALMENTE
- Lacuna: RC-58 sem bloco de decisão (a DP-05 consta "decidida" e as specs a chamam de pendência).
- Impacto: equipe (Editais de tutor/bolsista, comuns no Cefor); candidato.
- Prioridade: P2 — fora do piloto por decisão, mas a frase de corte impressa é norma errada no ato.
- Dependências: ED-10; ED-26 (aPDF-ED-15).
- Próxima ação recomendada: escrever o bloco de decisão do RC-58 na DP-05; pelo menos parar de imprimir
  corte em Perfil só de reserva.
- Precisa de decisão humana? sim — RC-58.
- Confiança: alta.

<a id="ed-30"></a>
#### ED-30 — Ampla concorrência: bordas que continuam abertas
- Descrição: a DP-14 resolveu o caso central (a inscrição oferece a ampla). Restam: Retificação que zera a
  linha geral ou dá a primeira Modalidade a Perfil sem vaga na linha geral, com rascunhos abertos (RC-134,
  `[VALIDAR]`); Perfil só de reserva com uma cota e sem ampla — todo inscrito assumido cotista (RC-135,
  "letra da DP-14"); envio conferindo documentos contra inscrição sem Modalidade (A-14.4, lido e não
  reproduzido); quadro sugerido pelo percentual preenche a ampla com o total e a Revisão bloqueia o
  "excesso" (L08-83, não reconferido).
- Origem (demanda/decisão): L08-42, L08-43, L08-44 (05b71845/60805961, 27/09); L08-83 (458e4f59, 30/09);
  RC-134, RC-135; AUD §13 item 24.
- Decisão aplicável: 27/09 DP-14 = A; "ampla marcada", "letra da DP-14", rascunhos "nada" (respostas
  literais); RC-135 fora do piloto (DP-05).
- Spec / PRs / commits: #202, #205; 051 FR-932.
- Implementação: `ps/inscricoes/application/rascunho.py` (`oferece_a_ampla_sem_modalidade`).
- Testes: testes do #202.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: validar RC-134 por teste; confirmar L08-83 no navegador.
- Impacto: candidato não cotista; elaborador.
- Prioridade: P2 — bordas, com o caso central resolvido.
- Dependências: ED-17 (RC-132); ED-29.
- Próxima ação recomendada: escrever o teste do RC-134 e reproduzir o L08-83 antes de decidir.
- Precisa de decisão humana? sim — RC-134 após validação.
- Confiança: média — dois dos quatro pontos não reproduzidos.

<a id="ed-31"></a>
#### ED-31 — O que é comum aos Perfis mora em cada Perfil (modelo Oferta / E2)
- Descrição: atribuições, carga, remuneração, requisitos e marcos se repetem por código/polo (16 cópias no
  140/2025). A 064 e a 068 consolidam o **PDF** (texto idêntico sai uma vez) e a 051 materializa "aplicar a
  todos", mas o dado segue repetido: a Retificação de `duties` vira 16 alterações sem conferência de
  igualdade, e código ≠ polo (código = formação × polo) segue sem forma (AX-5/6/7; P-5).
- Origem (demanda/decisão): L05-69, L05-78 (ae3ad7c8/0ef1dcf8, 15–16/09); L05-83; L06-11; L07-58 (E2);
  achado #3 (PARCIAL); RC-13; P-5; L03-60 (polo/campus); #115.
- Decisão aplicável: 16/09 posições do usuário sobre o modelo Oferta ("não permitir sobrescrita de
  atribuições", combinar Função e polo, identificadores estáveis) — **decisão não escrita em `doc/`**; E2
  aberta (AUD §13 item 9).
- Spec / PRs / commits: 043, 051, 064 (#264), 068 (#270).
- Implementação: `ps/publicacoes/infrastructure/pdf.py` (consolidação); `ps/interface/retificacao.py:65-66`
  (aplica `CAMPOS_PERFIL` a cada Perfil).
- Testes: `t/unit/publicacoes/test_atribuicoes_consolidadas.py`, `test_consolidacao_por_perfil.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: o dado; a decisão de modelagem.
- Impacto: elaborador (Retificação em 16 cartões); candidato (divergência entre cópias).
- Prioridade: P2 — o documento já foi resolvido; o custo restante é de Retificação e de risco de
  divergência.
- Dependências: ED-14; ED-28.
- Próxima ação recomendada: escrever em `doc/` as posições de 16/09 como registro de decisão (ou
  descartá-las) antes de qualquer spec.
- Precisa de decisão humana? sim — E2 / modelo Oferta.
- Confiança: alta.

<a id="ed-32"></a>
#### ED-32 — Comunicados: atos complementares que não são Retificação
- Descrição: os Editais reais publicam "Comunicados" que alteram ou esclarecem o certame sem ser
  Retificação (o 28/2026 e o 59/2026 têm Retificação **e** Comunicado). O sistema não tem a figura; os avisos
  da 066 são e-mails, não ato publicado.
- Origem (demanda/decisão): L04-08 (8af9d708, 07/09); S-020-02; github #54; `docs/libras/README.md`
  (pacotes 28 e 59).
- Decisão aplicável: nenhuma ("registradas mas sem dono").
- Spec / PRs / commits: 020 (fora de escopo).
- Implementação: inexistente.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão se Comunicado é Retificação, aviso ou ato próprio.
- Impacto: equipe de seleção (publica fora do sistema); candidato.
- Prioridade: P2 — prática corrente do Cefor que o sistema não representa; há contorno (publicar fora).
- Dependências: ED-06.
- Próxima ação recomendada: levantar com o setor o que os Comunicados reais contêm e decidir o
  enquadramento.
- Precisa de decisão humana? sim.
- Confiança: média — a existência nos Editais reais vem do estudo de Libras e de 07/09.

<a id="ed-35"></a>
#### ED-35 — Validade/prorrogação do Edital e Editais derivados (vagas remanescentes)
- Descrição: a validade do processo e a prorrogação (77, 14, 173) são prosa que nada consome (há a seção
  "Do Prazo de Validade"); um Edital que preenche vagas de outro (76 → 52; remanescentes) não tem relação
  no modelo, e a 023 recusou derivação normativa (P-6).
- Origem (demanda/decisão): L03-59, L03-64 (eeca206a, 03/09); L04-46, L04-82; L05-07; P-3, P-6; S-016-02,
  S-019-02, S-023-03.
- Decisão aplicável: 023 D (P-6 fora, 09/09); P-3 fora da 019.
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente (`processos/models.py` sem validade).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: modelo e decisão.
- Impacto: equipe (convocação de suplente após validade; reabertura para remanescentes).
- Prioridade: P3 — evolutivo; o reuso (023) cobre parte da criação.
- Dependências: ED-29.
- Próxima ação recomendada: nenhuma até haver Edital real que precise.
- Precisa de decisão humana? não (agora).
- Confiança: alta.

<a id="ed-36"></a>
#### ED-36 — Taxa de inscrição e isenção não modeladas
- Descrição: o sistema não modela taxa nem isenção (Edital 46; 024 fora de escopo); o estudo de Libras
  pede unidade própria para isso.
- Origem (demanda/decisão): L03-65/ideias (eeca206a, 03/09, "futuramente, quem sabe"); S-024-01; L09-81
  (9526cf31, 11/10).
- Decisão aplicável: 03/09 "futuramente, quem sabe".
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: tudo.
- Impacto: equipe (certames com taxa ficariam fora).
- Prioridade: P3 — os certames do Cefor na amostra (pós EaD, FIC, tutoria) são gratuitos.
- Dependências: nenhuma.
- Próxima ação recomendada: nenhuma até haver certame com taxa no alvo.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="ed-37"></a>
#### ED-37 — Objetos normativos publicados sem forma ou sem leitor
- Descrição: `classificationInformation` e `callInformation` são JSON livre publicado, sem tela, forma
  nem consumidor (tratados como opacos pela Revisão e pelo assistente); `reserveLimit`, `calculation`,
  `distribution` e `callRules` são publicados sem consumidor.
- Origem (demanda/decisão): L03-11 (4ef39231, 06/09); L05-03; L05-63; achado #28; L08-86 (2bc3c441, 27/09);
  S-026-01; RC-108 (tela "contradita").
- Decisão aplicável: 27/09 "cada campo se decide na spec que o consumiria, sem apagar do esquema"; 026
  natureza N; 13/09 "não derive automaticamente uma nova prioridade desse achado".
- Spec / PRs / commits: 026 (#114), 051 (passou a pedir `rounding`).
- Implementação: `ps/editais/models/perfis.py:36-37`; `ps/editais/domain/mutabilidade.py:155`.
- Testes: —
- Estado: ADIADO FORMALMENTE
- Lacuna: decisão por campo quando houver consumidor.
- Impacto: baixo (dados opacos no ato).
- Prioridade: P3 — decisão registrada de esperar o consumidor.
- Dependências: ED-29 (`reserveLimit`).
- Próxima ação recomendada: nenhuma.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="ed-38"></a>
#### ED-38 — Anexo publicado não diz a que serve
- Descrição: a lista pública mostra o rótulo e "(PDF, baixar)"; o anexo que nenhum requisito aponta não
  diz finalidade (exigiria campo novo, conteúdo normativo). Vizinho: numeração romana dos anexos digitada à
  mão (AX-12).
- Origem (demanda/decisão): achado #2 (08/09); L04-22 (ac086e7a); L06-40 (AX-12); RC-26 (resto); #59.
- Decisão aplicável: 08/09 "registra o achado"; DP-20 o classifica "não defeito"; rótulo é texto único
  (clarify 020).
- Spec / PRs / commits: 020, 024.
- Implementação: `ps/portal/templates/portal/_documentos_do_edital.html`; `ps/interface/revisao.py:496`
  (só informa).
- Testes: —
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão de produto.
- Impacto: candidato (não sabe qual anexo preencher).
- Prioridade: P3 — o texto do Edital costuma dizer; decisão registrada de não tratar como defeito.
- Dependências: nenhuma.
- Próxima ação recomendada: nenhuma até o teste com candidatos (ED-03) indicar.
- Precisa de decisão humana? sim — se vira campo.
- Confiança: alta.

<a id="ed-14"></a>
#### ED-14 — Validação cruzada entre fontes normativas (E-4)
- Descrição: a validação confere se cada parte está preenchida e se o Edital executa, mas não compara
  fontes entre si: a mesma lei com 3% × 30% em Perfis diferentes; critério de desempate invertido entre
  Perfis ("menor" × "maior", AX-1 — muda quem passa, e o `type` do critério não se corrige pela tela);
  prazo de recurso da tela × Cronograma (RC-76); terceiro critério igual à nota já empatada (92/2026);
  período de inscrições em dois lugares. A 051 ("aplicar a todos") reduz a chance de divergência, e a 067
  pôs aviso de conferência recurso × Cronograma.
- Origem (demanda/decisão): L05-79, L05-86 (a6849fe4, 15/09); L06-27, L06-39 (3bd46d67, 19/09); L09-82
  (9526cf31, 11/10); RC-31; RC-76; ACH-41; T-5; ideia de 03/09 (contradições do próprio Edital, 57/2026).
- Decisão aplicável: RC-76 "depois do piloto" (28/09, com Evento de recurso designado); 09/10 D-002 da 067
  "aviso de conferência".
- Spec / PRs / commits: 051 (#226), 067 (#268).
- Implementação: avisos da 067 (`ps/editais/domain/validation.py`); nenhuma comparação entre Perfis.
- Testes: `t/unit/publicacoes/test_frase_de_recurso.py` (aviso de conferência).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: conferência entre Perfis (mesma Modalidade/lei, critérios); Evento × marco (ver ED-22).
- Impacto: candidato (regra divergente no ato oficial); comissão.
- Prioridade: P2 — o risco é jurídico e existe, mas a 051 o reduziu e a parte de recurso foi adiada por
  decisão.
- Dependências: ED-22; ED-31; achado #39 (sorteio condicionado, área de sorteio).
- Próxima ação recomendada: aviso (não impeditivo) na Revisão para a mesma Modalidade com percentual
  diferente e para critério com sentido oposto entre Perfis.
- Precisa de decisão humana? sim — severidade (aviso ou impedimento).
- Confiança: média — RC-31 "não reconferido em 15/10"; código da 051/067 não relido aqui.

<a id="ed-16"></a>
#### ED-16 — Duas gramáticas: o vocabulário normativo das telas não vem do mesmo renderizador
- Descrição: gestão e portal têm tabelas de tradução de caminho paralelas que derivam em silêncio (RC-40);
  as telas de ato e a Retificação mostram o caminho normativo com UUID sob cada alteração (de propósito,
  "para quem audita"); os rótulos legados do "O que mudou" divergem dos da tela da Retificação; frases de
  corte/desempate/recurso não ficam gravadas e são recompostas pelo código atual a cada exibição (podem
  divergir do PDF publicado); UUID e "cand:…" nas telas de ato (RC-69).
- Origem (demanda/decisão): E-3 (L06-26, 3bd46d67, 19/09); L07-60, L07-71 (183ba11d/6c13e32b, 21–22/09);
  L05-66; L08-50 (f57fc34f, 27/09); L10-07 (84c96e5f, 12/10); RC-35, RC-40, RC-69; T-5.
- Decisão aplicável: 06/09 (017) "UUID pode existir na URL, mas não como linguagem apresentada ao
  usuário"; RC-40 "unificar ao tocar essas telas".
- Spec / PRs / commits: 030, 032–037 (citado e não feito), #201.
- Implementação: `ps/interface/templates/interface/retificacao_detalhe.html:68-70`,
  `retificacao_confirmar.html:57` (`<code>{{ item.caminho }}</code>`).
- Testes: `t/unit/publicacoes/test_alteracoes_legiveis.py` (guarda a existência da linha, não o rótulo).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: renderizador único e guardião de rótulo.
- Impacto: equipe (lê vocabulário de máquina na tela em que assina); candidato (rótulos diferentes).
- Prioridade: P2 — consistência; nada errado no ato publicado.
- Dependências: ED-06.
- Próxima ação recomendada: decidir se o caminho com UUID sai da tela de assinatura (fica no detalhe para
  auditor); unificar ao tocar as telas.
- Precisa de decisão humana? sim — o caminho fica visível na tela de assinatura?
- Confiança: média — templates conferidos; RC-40 não reconferido.

<a id="ed-17"></a>
#### ED-17 — Mensagens que se contradizem na composição e na Retificação
- Descrição: três contradições vivas: (1) quem escolhe "Nenhuma — a ampla concorrência é só a linha
  geral" (a grafia certa) recebe `general_competition_modality_undeclared` ("não declara qual delas é a
  da ampla"), contra a Revisão e o próprio seletor (RC-132); (2) sob sorteio, as dicas de vazio de
  desempate, combinação e normalização na Retificação dizem "a publicação será impedida", e a validação não
  exige esses campos; (3) o placeholder "Uma linha em branco separa parágrafos" contradiz o compositor, que
  separa a qualquer quebra (ACH-02).
- Origem (demanda/decisão): achado #13; L08-45 (ff4cbf21, 27/09); L09-66 (4d4cd6b0, 09/10); L09-59
  (cab5c781/b82fa294, 08/10); RC-132; d.3 de `doc-achados-e-auditorias.md`.
- Decisão aplicável: 27/09 RC-132 "Deixar registrado" (calar exige revisar a FR-325 da 027); ACH-02:
  "registrar separadamente" (08/10), sem arquivo próprio em `doc/`.
- Spec / PRs / commits: 027 (FR-325), 067, 064/065.
- Implementação: `ps/editais/domain/validation.py:1206-1223` × `ps/interface/templates/interface/_perfil.html:210`;
  `_perfil.html:83` × `ps/publicacoes/infrastructure/pdf.py:530-542`.
- Testes: `t/interface/test_advertencias_do_quadro.py` (prende o aviso).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: emendar FR-325 ou o texto; corrigir as dicas; trocar o placeholder.
- Impacto: elaborador (aprende a ignorar avisos).
- Prioridade: P2 — corroem a confiança nos avisos, que são a principal proteção da elaboração.
- Dependências: ED-30.
- Próxima ação recomendada: correções diretas em (2) e (3); para (1), o usuário decide a emenda da FR-325.
- Precisa de decisão humana? sim — só para (1).
- Confiança: alta — os três conferidos no código.

<a id="ed-18"></a>
#### ED-18 — Gravar a etapa Perfis apaga a descrição da Modalidade
- Descrição: `forms._modalidades` lê `…-description`, e `_modalidade.html` não desenha o campo; ao gravar,
  a descrição vira "" e substitui a existente (vinda da API, do seed ou de um Edital reaproveitado).
- Origem (demanda/decisão): RC-158 (AUD 29/09); L08-25 (2bc3c441); c.4 lateral da análise de 29/09.
- Decisão aplicável: estava nas "11 correções antes do piloto" (29/09), sem execução.
- Spec / PRs / commits: nenhum.
- Implementação: `ps/interface/forms.py:116` (`"description": _texto(dados, f"{base}-description")`);
  `_modalidade.html` sem o campo (grep vazio).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: preservar o valor ou desenhar o campo; teste de perda.
- Impacto: elaborador (perda silenciosa de texto).
- Prioridade: P2 — perda silenciosa, mas só de descrição que a tela nunca permitiu escrever.
- Dependências: ED-34 (reuso traz a descrição).
- Próxima ação recomendada: correção direta com teste de ida e volta.
- Precisa de decisão humana? não.
- Confiança: média — confirmado por leitura do código, não reproduzido.

<a id="ed-19"></a>
#### ED-19 — Identidade do Edital: número imutável desde a criação, número queimado, ordenação textual
- Descrição: número e ano aparecem só como texto na etapa Identificação (não há como corrigi-los antes de
  publicar); um número com caractere sem grafia é recusado na publicação e não se corrige pela tela;
  cancelar o Edital "queima" o número para sempre (constraint única sem condição); a lista ordena `number`
  como texto ("9/2026" acima de "10/2026").
- Origem (demanda/decisão): L04-87, L04-89 (211d74e8, 09–10/09); L09-57 (b82fa294, 08/10); github #265.
- Decisão aplicável: nenhuma (o número é não retificável **depois** de publicado — 026, conferido).
- Spec / PRs / commits: nenhum.
- Implementação: `ps/interface/templates/interface/compor_identificacao.html:45`;
  `ps/processos/models.py:47,118-122`; `ps/processos/application/selectors.py:30`;
  `ps/interface/views.py:4891`.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: edição do número em elaboração; constraint condicional ao estado; ordenação numérica.
- Impacto: elaborador/gestor (erro de digitação na criação só se resolve cancelando e queimando o número).
- Prioridade: P2 — sem produção ainda; no piloto, um erro de criação vira número perdido.
- Dependências: ED-33.
- Próxima ação recomendada: decidir se número/ano são editáveis até a submissão e se o cancelamento libera
  o número; corrigir a ordenação.
- Precisa de decisão humana? sim — liberar número de Edital cancelado.
- Confiança: alta — conferido.
- **Fundidos neste item:** GO-16.
  - *GO-16 (GO), Cancelar Edital "queima" o número/ano* — lacuna: decidir se número de Edital cancelado pode ser reusado (prática administrativa do Cefor). Próxima ação: perguntar ao setor se a numeração de Edital cancelado é reaproveitada; se não, registrar como comportamento correto. - Precisa de decisão humana? sim.

<a id="ed-20"></a>
#### ED-20 — A Revisão e o assistente: aviso que soterra o impeditivo e textos de fase errada
- Descrição: a Revisão mostra o IMPEDE sob dezenas de avisos repetidos por Perfil (25 no reuso; 54 no
  140/2025; 3 eventos geram 7 achados na 028) (RC-10); "Ir para" aponta o título da etapa e não o marco
  (RC-159); avisos antigos levam ao topo da etapa (só os da 065 levam à seção); em Edital publicado o
  assistente diz "O que falta para submeter" (RC-122); o selo CONCLUÍDA significa "tem linha" mesmo com
  IMPEDE apontando a etapa (RC-16; a 028 corrigiu só o Cronograma); a Revisão da 044 diz "em todos os
  Perfis" sem "n de N" (RC-156).
- Origem (demanda/decisão): L05-58, L05-91; L07-56 (183ba11d); L08-12 (0ebd3f4c); L08-54; L08-77; L09-65
  (fba18c90); RC-10, RC-16, RC-122, RC-156, RC-159; github #120, #230.
- Decisão aplicável: RC-156 é proposta da DP-17 sem escopo; #163 colapsou só as famílias de data.
- Spec / PRs / commits: 028, 051, 053, 056, 065.
- Implementação: `ps/interface/templates/interface/compor_revisao.html:21` ("O que falta para submeter",
  sem condição de publicado).
- Testes: `t/interface/test_selo_do_cronograma.py` (só Cronograma).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: agrupar avisos por espécie, âncora no marco, texto de fase, critério dos selos.
- Impacto: elaborador e homologador (perdem o impeditivo no meio do ruído).
- Prioridade: P2 — a Revisão é a última barreira antes do ato; o ruído é medido.
- Dependências: ED-01 (o teste dirá o que pesa).
- Próxima ação recomendada: corrigir RC-122 e RC-159 diretamente; decidir o agrupamento depois do teste
  do ED-01.
- Precisa de decisão humana? sim — agrupar avisos por espécie muda decisão (FR-344a e afins).
- Confiança: média — RC-122 conferido; demais pela auditoria (RC-10/16/159 "não reconferidos").

<a id="ed-21"></a>
#### ED-21 — Microinterações da composição e rascunho local
- Descrição: `<select multiple>` de Etapas no marco zera a seleção com clique simples (RC-11); recusa logo
  após salvar aparece junto da faixa "Rascunho salvo" (RC-147); o `MutationObserver` do rascunho local vê só
  filhos diretos (remover Modalidade não regrava até a próxima tecla, RC-153); a restauração do rascunho
  acima do limite de 13 mil campos recebe a recusa; Cronograma como tabela editável e seletor de Modalidade
  dos Documentos agrupado por Perfil (análise de 29/09, sem spec); a cópia do "Duplicar Perfil" aparece
  depois da origem e salta de posição ao salvar; marcar "Admite recurso" apagou o critério de desempate
  preenchido (L07-68, não investigado).
- Origem (demanda/decisão): L07-68 (3445162b, 25/09); L08-53 (2676363b); L08-68; L08-75, L08-76
  (d8beef33, 29/09); RC-11, RC-147, RC-153; c.4.
- Decisão aplicável: L08-75 "Você decide" sem resposta.
- Spec / PRs / commits: 052, 053, #216, #232.
- Implementação: `ps/interface/templates/interface/_marco.html:113` (`multiple`, conferido).
- Testes: `t/interface/test_limite_de_campos_da_composicao.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: correções pontuais; reprodução do L07-68.
- Impacto: elaborador.
- Prioridade: P3 — atrito, sem efeito no ato.
- Dependências: ED-01.
- Próxima ação recomendada: reproduzir L07-68 (único que pode perder dado); o resto espera o teste.
- Precisa de decisão humana? não.
- Confiança: média — só RC-11 reconferido.

<a id="ed-22"></a>
#### ED-22 — Cronograma: Evento sem tipo controlado, sem vínculo com o marco, e cancelado impresso como vigente
- Descrição: `EventoCronograma.type` é texto livre; nada liga o Evento de recurso ao marco (a 067 compara
  por conter "recurso" e deixa a conferência ao humano); coerência de sequência entre Eventos, duração e
  deslocamento de datas em bloco ficaram fora da 028; a regra do ano (FR-344) ancora no ano do Edital, e o
  certame que atravessa o ano gera aviso falso; **o PDF imprime Evento `CANCELADO` como qualquer outro**
  (o portal passou a filtrar na 047). O cancelamento de Evento só é declarável pela API.
- Origem (demanda/decisão): L02-09 (8f779c78, 31/08); L06-35/L07-40 (N-05/06); L07-57 item 13; L08-33
  (49d875fd/af8e65b6, 26/09); L09-94; aPDF-ED-02; RC-76; RC-80 (resíduo C); S-028-01/04; S-067-04; 069 lote 2.
- Decisão aplicável: DP-01 (status derivado, só `CANCELADO` declarado — 045); RC-76 "depois do piloto";
  FR-344 (decisão do estudo de 21/09 em aberto, AUD §13 item 9).
- Spec / PRs / commits: 021 (local), 028, 045, 047, 067.
- Implementação: `ps/editais/models/cronograma.py:26`; `ps/editais/domain/cronograma.py:15-16`;
  `ps/publicacoes/infrastructure/pdf.py:3883-3935` (sem filtro nem marca de status);
  `ps/editais/domain/validation.py:2566` (FR-344).
- Testes: `t/integration/editais/test_cronograma.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: vocabulário/vínculo Evento × marco; marca de cancelado no PDF.
- Impacto: candidato (prazo de recurso conferido à mão; Evento cancelado no ato); comissão.
- Prioridade: P2 — o vínculo foi adiado por decisão; o Evento cancelado no PDF é defeito, mas só alcançável
  pela API.
- Dependências: ED-14; ED-23.
- Próxima ação recomendada: corrigir o PDF para marcar (ou omitir) Evento cancelado; deixar o vínculo para
  depois do piloto, como decidido.
- Precisa de decisão humana? sim — omitir ou marcar o cancelado no ato.
- Confiança: alta — modelo e renderizador conferidos.

<a id="ed-23"></a>
#### ED-23 — Evento só com data sai "às 00h"
- Descrição: num Evento sem hora o documento imprime "às 00h" (9 de 11 e 11 de 13 nos Editais do estudo).
- Origem (demanda/decisão): RC-22; aPDF-ED-28; L08-71 (89/2026); roteiro P5.
- Decisão aplicável: 28/09 "a hora continua obrigatória; rever junto com a spec do documento (DP-20)"; a
  054 adiou de novo (`specs/054…/spec.md:485`); a 069 não tratou.
- Spec / PRs / commits: #49 (formato `09h39`/`00h`, 07/09).
- Implementação: formatação em `ps/shared` (`humano.instante`).
- Testes: `t/unit/publicacoes/test_humano.py`.
- Estado: ADIADO FORMALMENTE
- Lacuna: decidir se a data sem hora é forma legítima.
- Impacto: candidato (prazo à meia-noite que o Edital não quis dizer).
- Prioridade: P2 — afirma no ato oficial um horário que o Edital real não tem.
- Dependências: ED-22.
- Próxima ação recomendada: decidir na próxima mexida no documento; é pequeno.
- Precisa de decisão humana? sim — Evento só com data é admitido?
- Confiança: alta.

<a id="ed-24"></a>
#### ED-24 — Seções textuais sem tabela, subitem numerado ou negrito
- Descrição: o texto livre é parágrafo corrido; o Quadro 1 do 28/2026 (Edital do piloto) não cabe; o
  subitem transcrito carrega o número do original.
- Origem (demanda/decisão): RC-141; aPDF-ED-20; L08-25; L09-06 (7f415158, 30/09); L01-54 (itens numerados
  como estrutura).
- Decisão aplicável: aPDF-ED-20 "adiado pela 054"; numeração automática (solução estrutural do aPDF-ED-01)
  "para evolução posterior" (065).
- Spec / PRs / commits: 054, 065, 069.
- Implementação: `ps/publicacoes/infrastructure/pdf.py:530-542` (`_paragrafos`).
- Testes: —
- Estado: ADIADO FORMALMENTE
- Lacuna: forma de tabela/subitem no texto.
- Impacto: elaborador (tabela vira prosa ou anexo); candidato.
- Prioridade: P2 — o piloto previsto tem tabela em seção textual; há contorno (anexo), por isso não P1.
- Dependências: ED-25; ED-11.
- Próxima ação recomendada: no teste do ED-01, observar como o setor contorna o Quadro 1 e decidir.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="ed-25"></a>
#### ED-25 — Parágrafos e numeração digitada no texto colado
- Descrição: a 065 detecta conflito entre numeração digitada e a calculada (impeditivo no Edital, aviso na
  Retificação), mas: o parágrafo que é só um número ("11.2.") é lido como subitem (1 falso positivo em 517;
  excluí-lo pede emenda da FR-1199); o texto transcrito com a numeração do Word é recusado e o assistente não
  oferece retirar os números; quebras rígidas de texto colado viram parágrafos (ACH-02); o título do original
  colado no texto ("11. DA CONVOCAÇÃO") é tratado como suspeita.
- Origem (demanda/decisão): L08-69 (a083f5e1, 29/09); L09-64, L09-90 (fba18c90/46626552); L09-59 (ACH-02);
  S-065-01/02; S-069-04; github #264, #266.
- Decisão aplicável: 08–09/10 Q1/Q2 da 065 (impeditivo no Edital, aviso na Retificação); itens 3 e 4 da
  revisão "ficam".
- Spec / PRs / commits: 064, 065 (#266), 069.
- Implementação: `ps/editais/domain/numeracao_digitada.py`.
- Testes: `t/unit/editais/test_numeracao_digitada.py`, `t/interface/test_numeracao_na_revisao.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: os quatro resíduos acima.
- Impacto: elaborador que transcreve do Word (o caminho decidido em E10 = B).
- Prioridade: P2 — com transcrição como regra (ED-02), a recusa por numeração do Word é atrito certo.
- Dependências: ED-02; ED-24.
- Próxima ação recomendada: decidir se o assistente oferece "retirar a numeração digitada"; emendar a
  FR-1199 para o parágrafo só-número.
- Precisa de decisão humana? sim — as duas acima.
- Confiança: média — pela auditoria de 15/10 e verificações das specs.

<a id="ed-26"></a>
#### ED-26 — Resíduos de composição do documento oficial (PDF)
- Descrição: achados da auditoria do PDF e das verificações 064/067/068/069 ainda abertos: frases de
  reversão/convocação na margem zero (aPDF-ED-15, parcial); coluna "Evento" estreita (aPDF-ED-17); ordem
  declarada dos Perfis (aPDF-ED-19; Perfil acrescentado vai para o fim); Etapa sem descrição (aPDF-ED-21);
  linhas viúvas (aPDF-ED-23); negrito de "Remuneração" (aPDF-ED-26); código de verificação (aPDF-ED-27);
  "Tabela N" digitada pode mudar de destino com a tabela única (068); larguras da tabela de vagas e a linha
  "AC — Ampla concorrência | — | —" (068); o Perfil inteiro não salta para a página seguinte (FR-020 da
  008, D-005 da 064); seis pontos "registrados e não corrigidos" da 069; brasão de ~103 DPI pixeliza
  (L01-59, não reconferido).
- Origem (demanda/decisão): L01-43, L01-59 (2026-08-30); L09-61, L09-63, L09-68 (08–09/10); S-068-01;
  S-069-05; c.8; github #264, #268, #270.
- Decisão aplicável: 08/10 sequência de correções da auditoria do PDF (aprovada pelo usuário); os demais
  "aguardam a sua priorização".
- Spec / PRs / commits: 064–069.
- Implementação: `ps/publicacoes/infrastructure/pdf.py`.
- Testes: `t/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py`, `test_paginacao_do_edital.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: os itens listados.
- Impacto: candidato (leitura); instituição (aparência do ato).
- Prioridade: P2 — a maioria é acabamento (P3), mas a remissão "Tabela N" que muda de destino é erro
  normativo no ato oficial.
- Dependências: ED-11; ED-29 (aPDF-ED-15).
- Próxima ação recomendada: tratar a remissão "Tabela N" primeiro (aviso ou numeração estável); o resto
  num lote de acabamento depois do teste do ED-01.
- Precisa de decisão humana? sim — prioridade do lote.
- Confiança: média — pela auditoria de 15/10; não reconferido item a item.

<a id="ed-11"></a>
#### ED-11 — O documento oficial não é acessível a leitor de tela, e o texto só existe no PDF
- Descrição: o PDF do Edital sai sem marcação (`Tagged: no`, sem `/StructTreeRoot`); a leitura com leitor
  de tela real não foi feita; o portal não mostra as seções de texto (recursos, convocação, disposições
  existem só no PDF e na API JSON); a leitura no celular depende disso (aPDF-ED-13). A 069 fez o
  "ED-07 básico" (metadados, navegação, fonte embutida) e deixou a decisão grande — PDF marcado, troca de
  motor (HTML→PDF) ou ato em HTML acessível — "à parte".
- Origem (demanda/decisão): aPDF-ED-07(G), ED-13; L09-93 (46626552, 12/10); L10-08 (84c96e5f); S-069-03;
  github #275; ideia "gerador HTML→PDF" (12/10).
- Decisão aplicável: 12/10 "HTML→PDF fica como alternativa futura"; aPDF-ED-07(G) aguarda decisão.
- Spec / PRs / commits: 069 (#275, FR-1388).
- Implementação: `ps/publicacoes/infrastructure/pdf.py:5137` ("sem `/StructTreeRoot` — o arquivo
  continua sem marcação").
- Testes: `t/unit/publicacoes/test_arquivo_do_edital.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão de abordagem; percurso com leitor real.
- Impacto: candidato com deficiência visual (acesso à norma do próprio certame).
- Prioridade: P1 — o PDF é o único canal completo da norma e não é acessível; direito de acesso (LBI).
- Dependências: ED-06; ED-44.
- Próxima ação recomendada: decidir entre PDF marcado e ato em HTML acessível publicado junto; fazer a
  leitura com leitor real na versão atual como linha de base.
- Precisa de decisão humana? sim — abordagem (aPDF-ED-07 G).
- Confiança: alta — conferido no compositor.

<a id="ed-27"></a>
#### ED-27 — Lote 2 da linguagem simples e endereço do certame
- Descrição: o lote 1 (069) foi entregue; o lote 2 não tem spec: endereço eletrônico do certame gerado
  (aPDF-ED-09 / D3, domínio congelado na Publicação); contato congelado; tipo do Evento do cronograma;
  "o que mudou" (aPDF-ED-06, ver ED-06); portal com o que é estruturado. Sem o endereço, a convocação "por
  publicação" deixou de dizer onde publica. D4 (modelos de texto por unidade × FR-983 da 054) aberta.
- Origem (demanda/decisão): c.11 lote 2, D3, D4; L09-89 (46626552, 12/10); L09-94; L10-12, L10-14
  (vocabulário 069 × 070).
- Decisão aplicável: 12/10 direção da 069 com lotes; D3 e D4 sem decisão.
- Spec / PRs / commits: 069 (§7.5 "depois").
- Implementação: inexistente para o lote 2.
- Testes: —
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: spec do lote 2.
- Impacto: candidato (onde acompanhar a convocação; texto do Edital).
- Prioridade: P2 — a convocação por publicação sem endereço é lacuna real; o resto é melhoria.
- Dependências: ED-03; ED-06; ED-22.
- Próxima ação recomendada: decidir D3 (endereço congelado na Publicação) — destrava a frase da
  convocação — e D4.
- Precisa de decisão humana? sim — D3 e D4; alinhamento de vocabulário 069 × 070.
- Confiança: média.

<a id="ed-44"></a>
#### ED-44 — Tradução/interpretação de Editais em Libras (maturidade: estudo documental)
- Descrição: `docs/libras/` é estudo de viabilidade em 4 rodadas (até 11/10): catálogo de unidades,
  narrativas por situação, comparação focalizada (19, 46, 28 e 59/2026), protocolo para profissionais.
  **Nenhuma tradução foi produzida nem avaliada; nada foi implementado; nenhuma unidade tem vídeo ou
  validação.** Conclusão do próprio estudo: há base para um experimento com profissionais de Libras e
  participantes surdos, e **não** há base para desenvolver uma biblioteca audiovisual integrada.
  Pendências com responsáveis: divergências nos Editais reais (vagas 420 × 280 no 28/2026; início do 59;
  prazos de recurso × Cronograma; ano "2025"), versão traduzida pelos vídeos, alcance da obrigação por tipo
  de certame (jurídico), tradução das Retificações (LBI art. 30, VII), autorização de uso dos vídeos.
- Origem (demanda/decisão): L09-79, L09-80, L09-83 (9526cf31, 11/10); github #273;
  `docs/libras/viabilidade.md` §9–11; `historico/alteracoes-rodada-4.md` §"Pendências e responsáveis".
- Decisão aplicável: 11/10 "não utilizar avatar; não declarar traduções como concluídas; estudo só
  documental"; "não estimar economia por repetição textual"; download de documentos públicos autorizado.
- Spec / PRs / commits: #273 (só documentação).
- Implementação: inexistente (por decisão).
- Testes: ferramentas do estudo (`docs/libras/ferramentas/`).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: Fase 1 do protocolo com dois profissionais; respostas das áreas.
- Impacto: candidato surdo.
- Prioridade: P3 — exploratório por decisão; a obrigação legal por tipo de certame ainda não foi
  enquadrada pelo jurídico.
- Dependências: ED-11; ED-06 (tradução das Retificações); jurídico.
- Próxima ação recomendada: Fase 1 do protocolo e resposta da área às pendências; nenhuma spec antes.
- Precisa de decisão humana? sim — institucional (jurídico, Cefor, profissionais).
- Confiança: alta — estado declarado no README do estudo.

<a id="ed-33"></a>
#### ED-33 — Cancelamento do Edital não gera Publicação
- Descrição: o cancelamento grava ato administrativo e auditoria, mas nenhum documento público; o portal
  mostra o estado (RC-116 resolvido).
- Origem (demanda/decisão): RC-120; S-047-02; github #191.
- Decisão aplicável: 28/09 "agora não" (registro pré-piloto:42).
- Spec / PRs / commits: 047.
- Implementação: `ps/processos` (ato de cancelamento).
- Testes: testes da 047.
- Estado: ADIADO FORMALMENTE
- Lacuna: ato publicado de cancelamento.
- Impacto: candidato inscrito; transparência.
- Prioridade: P2 — a Constituição pede preservar Publicações no cancelamento; adiado por decisão.
- Dependências: ED-19.
- Próxima ação recomendada: rever quando o primeiro cancelamento real for plausível.
- Precisa de decisão humana? não (já decidido adiar).
- Confiança: alta.
- **Fundidos neste item:** GO-15.
  - *GO-15 (GO), Cancelamento do Edital não gera Publicação (RC-120)* — lacuna: ato público de cancelamento. Próxima ação: rever na primeira necessidade real de cancelar. - Precisa de decisão humana? não (já decidido "agora não").

<a id="ed-34"></a>
#### ED-34 — Reaproveitamento de Edital anterior: resíduos
- Descrição: a 023 copia integralmente; restam: o reuso copia ~10.900 caracteres de prosa de outro
  certame e a cláusula de sorteio antiga, sem pedir revisão (RC-43; a D-G3 exige fonte externa
  prospectivamente); a classe "campo novo de referência que a fixture não declara escapa do remapeamento" já
  se repetiu duas vezes (`generalCompetitionModalityId`, `governedStage`; RC-42); o teto de inscrições por
  candidato não é copiado; seleção parcial, "estado REAPROVEITADA" e importação de PDF ficaram fora.
- Origem (demanda/decisão): L04-85, L04-86 (211d74e8, 09/09); L07-55, L07-58 (183ba11d); L08-10 (05c42556);
  achados #1 e #14; RC-42, RC-43; B-10; registro pré-piloto (teto).
- Decisão aplicável: 09/09 "Criar a partir de edital anterior", sem "importar"; V1 sem REAPROVEITADA;
  importar PDF é outra feature; 30/08 nada de templates.
- Spec / PRs / commits: 023, #169, 028.
- Implementação: `ps/editais/domain/reaproveitamento.py:143-181`; sem `max_inscricoes` (grep vazio).
- Testes: `t/unit/editais/test_reaproveitamento.py`, `t/integration/editais/test_reaproveitamento.py`,
  `t/interface/test_reaproveitar.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: varredura "campos do conteúdo × campos da fixture"; aviso de prosa herdada; copiar o teto (ou
  decidir não copiar).
- Impacto: elaborador (prosa de outro certame no ato); integridade.
- Prioridade: P2 — o reuso é o caminho normal a partir do 2º Edital de cada família.
- Dependências: ED-18; ED-02.
- Próxima ação recomendada: escrever a varredura que fecha a classe; decidir sobre o teto.
- Precisa de decisão humana? sim — copiar o teto; "reuso com estado de revisão" (B-10).
- Confiança: alta — teto e remapeamento conferidos.

<a id="ed-40"></a>
#### ED-40 — 403 × 404 em criar Edital e reaproveitar (D-G2)
- Descrição: quem vê o objeto e não tem a capacidade recebe 404 em `criar_edital` e `reaproveitar`
  (também `supervisao`); a D-G2 mandou 403 nesses três.
- Origem (demanda/decisão): L06-19 (3bd46d67); L07-26, L07-43; DP-07; RC-94.
- Decisão aplicável: ~19/09 D-G2; 28/09 "vai junto com a preparação para produção".
- Spec / PRs / commits: 033 (inventário de negativas).
- Implementação: `ps/interface/views.py:415, 1813` (`Http404`).
- Testes: inventário de negativas da 033.
- Estado: ADIADO FORMALMENTE
- Lacuna: execução.
- Impacto: equipe (404 mudo parece rota quebrada).
- Prioridade: P2 — decidido para a preparação de produção.
- Dependências: B-1.
- Próxima ação recomendada: executar junto do B-1.
- Precisa de decisão humana? não.
- Confiança: alta.
- **Fundidos neste item:** GO-06.
  - *GO-06 (GO), D-G2: três recusas devem passar de 404 para 403 (decidido, adiado para a produção)* — lacuna: implementação + emenda do inventário; a DP-07 não tem o bloco "O que foi decidido". Próxima ação: incluir no incremento de preparação para produção; escrever o bloco de decisão na DP-07. - Precisa de decisão humana? não (já decidido).

<a id="ed-43"></a>
#### ED-43 — Multiunidade: marca fixa e demais unidades
- Descrição: "Cefor/Ifes" fixo em títulos, topo, 404, e-mails, rodapé dos avisos e tipo de problema da API;
  `PORTAL_ATENDIMENTO` único por instalação; só o Cefor está em `unidades.json`; o seletor fixa `cefor`.
- Origem (demanda/decisão): L09-29 (a1ccd396, 06/10); L10-50; S-060-01/04; c.6; P-9.
- Decisão aplicável: 06/10 o usuário quis a multiunidade **já** ("TENHO RECEIO DE DEIXAR ISSO PARA
  DEPOIS"); Q2 (identidade visual) adiada (12/10).
- Spec / PRs / commits: 060 (#254), 072.
- Implementação: `ps/unidades/unidades.json:1-9`; `ps/avisos/domain/mensagem.py:31`;
  `ps/interface/identidade.py:16`.
- Testes: testes da 060.
- Estado: BLOQUEADO
- Lacuna: dados das demais unidades (Ifes); decisão de marca.
- Impacto: outras unidades do Ifes.
- Prioridade: P3 — o piloto é do Cefor.
- Dependências: ED-04.
- Próxima ação recomendada: nenhuma até o Ifes fornecer unidades.
- Precisa de decisão humana? sim — marca e atendimento por unidade.
- Confiança: alta.
- **Fundidos neste item:** GO-10.
  - *GO-10 (GO), Multiunidade: implementada no modelo, mas só uma unidade exercitável* — lacuna: marca por unidade, atendimento por unidade, cadastro das demais unidades, escopo vindo da autenticação (GO-01). Próxima ação: nada antes do gatilho; responder à pergunta da 073 ("quando entra a segunda unidade?"). - Precisa de decisão humana? sim — quando entra a segunda unidade; forma do atendimento por unidade.

<a id="ed-45"></a>
#### ED-45 — Contrato da API do Edital desatualizado
- Descrição: `precondition_missing` e `no_effective_change` são emitidos e não constam do `openapi.yaml`;
  a decisão do Vito sobre `kind`/`provenance` no contrato nunca veio; a guarda
  `homologated_revision_changed` não é alcançável pela API (passo do quickstart não observável).
- Origem (demanda/decisão): L01-04, L01-08, L01-46 (0b03a4b5/75d0dcc9, 28–29/08); github #3.
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 001, 003.
- Implementação: `specs/001-processo-seletivo-editais/contracts/openapi.yaml` (zero ocorrências dos dois
  códigos, conferido).
- Testes: teste paramétrico do `openapi.yaml` (não cobre os códigos).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: documentar os códigos.
- Impacto: integrador da API (nenhum hoje).
- Prioridade: P3 — a API admin não tem consumidor nem autenticação de produção.
- Dependências: B-1.
- Próxima ação recomendada: acrescentar os códigos ao contrato quando a API ganhar consumidor.
- Precisa de decisão humana? não.
- Confiança: alta para os códigos; baixa para o resto.

<a id="ed-46"></a>
#### ED-46 — Encerrar formalmente a 039 (catálogo de Modalidades)
- Descrição: a 039 está na `main` como `Draft`, com nota que devolve o destino "a quem governa o
  backlog". O centro dela (Modalidade com fundamento e percentual no Edital) foi recusado pela decisão de
  25/09 e pela Constituição; a D-G5 foi entregue pela 048; o alcance da Etapa saiu dela (ED-09).
- Origem (demanda/decisão): L06-36; L08-31; DP-08 item 1; RC-102; X-03; S-039-01.
- Decisão aplicável: 25/09 `doc/decisao-recorte-documental.md` (mover a Modalidade para o Edital "está fora
  de questão"); 26/09 "Mesclar com nota".
- Spec / PRs / commits: 039 (#175), 044, 048.
- Implementação: inexistente (por decisão).
- Testes: —
- Estado: DESCARTADO OU SUBSTITUÍDO
- Lacuna: registro formal do encerramento.
- Impacto: quem lê o backlog (spec Draft parece pendente).
- Prioridade: P3 — governança documental.
- Dependências: ED-09; DP-12 (Status das specs, outra área).
- Próxima ação recomendada: o usuário fecha a DP-08 item 1 e a spec recebe status de encerrada.
- Precisa de decisão humana? sim — DP-08 item 1.
- Confiança: alta.
- **Fundidos neste item:** GO-39.
  - *GO-39 (GO), A 039 (catálogo de Modalidades) nunca implementada nem encerrada (DP-08)* — lacuna: encerramento formal. Próxima ação: marcar a 039 como descartada/substituída (pela 048 e pela Constituição), com nota no README. - Precisa de decisão humana? sim — DP-08 item 1.

<a id="ed-47"></a>
#### ED-47 — Decisões tomadas pelo agente na área do Edital, sem aprovação explícita
- Descrição: escolhas do agente que entraram na `main` sem pergunta: a recusa `registration_period_cancelled`
  como impeditivo (o usuário decidira só fechar o período; L08-58); seis reclassificações da matriz da 026
  como "correção de erro" (`operation`, `normalization`, `maxInscricoes`, `isRegistrationPeriod`, nascimento
  do `drawMethod`, `normativeRule/id`; L05-67); a leitura estreita da D-001 da 044 ("mesmo código, mesma
  denominação" só para códigos de recorte transversal; L08-01, perguntado duas vezes); a linha "Habilitação"
  do sorteio no PDF sem FR (L08-51); `key` do documento exigido não editável (E2E-004); a página da 060 com
  D-002/D-003 (unidades sem tela; autoridade como habilitação na unidade).
- Origem (demanda/decisão): L05-67 (ae3ad7c8, 13/09); L08-01 (6fefec8a, 25/09); L08-51 (233e8b36, 28/09);
  L08-58 (628c5ea1, 28/09); lote 03 §4 (E2E-004); lote 09 §4 (060).
- Decisão aplicável: nenhuma explícita (merge implica aceitação tácita).
- Spec / PRs / commits: 026, 044, 054, 060, #221.
- Implementação: vigente na `main`.
- Testes: os de cada spec.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: confirmação do usuário.
- Impacto: governança (o usuário decide escopo e regra).
- Prioridade: P3 — o comportamento é defensável; o risco é decisão de regra sem dono.
- Dependências: —
- Próxima ação recomendada: apresentar a lista ao usuário para confirmar ou reverter cada uma.
- Precisa de decisão humana? sim — confirmar ou reverter.
- Confiança: média — relato dos agentes nos digestos.

---


## CA — Portal público, candidato e comunicação

<a id="ca-01"></a>
#### CA-01 — Percurso conduzido com cinco pessoas da jornada pública (SC-605)
- Descrição: a 072 reorganizou a vitrine, a página da seleção, o acesso e o cartão de resultado para quem entra pelo celular. O critério de sucesso (4 de 5 pessoas concluem cada tarefa sem ajuda) nunca foi medido. O roteiro está pronto.
- Origem (demanda/decisão): auditoria UX de 12/10 (`doc/auditoria-ux-conversao-2026-10-12.md`); sessão 34ab2a4e (12–13/10), L09-84; PR #277; S-072-01; c.13 (SC-605).
- Decisão aplicável: Q1 (12/10): não instrumentar e validar por percurso conduzido. Em 13/10 o usuário mandou manter SC-605 pendente, sem declarar a feature concluída (spec 072 :63-73; lote 09, decisões 139–141).
- Spec / PRs / commits: 072; #276 (auditoria), #277 (implementação, `c3414ad1`, `d955e009`, `4d3a778c`, `2b02b6e3`).
- Implementação: `portal/templates/portal/vitrine.html`, `_consulta.html`, `selecao.html`, `_resumo_da_oferta.html`, `_cartao_da_selecao.html`; `portal/views.py`, `portal/leitura.py`.
- Testes: `tests/integration/portal/test_detalhe_selecao.py`, `tests/interface/test_acessibilidade_do_portal.py` e os da 072 (percurso técnico).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: `specs/072-jornada-publica-do-portal/validacao-humana.md:3` está "PENDENTES" (13/10). O quickstart da 072 depende do banco `ps_ux_conversao` e da entrada `ux-conversao` (porta 8077), que não estão versionados. Um terceiro não reproduz o percurso.
- Impacto: candidato (conversão e compreensão), equipe de seleção (atendimento).
- Prioridade: P1 — é a única validação do redesenho do portal, e a spec pede pessoa real.
- Dependências: CA-02 (a tarefa 3 passa por "Seus dados"), CA-14.
- Próxima ação recomendada: conduzir as cinco sessões pelo roteiro de `validacao-humana.md` e registrar em `verificacao.md`. Antes disso, versionar ou documentar como montar o banco e a entrada de preview.
- Precisa de decisão humana? sim — quem conduz, quando, e se o limite 4/5 fica (só pode mudar antes das sessões).
- Confiança: alta — o arquivo de validação e o PR dizem o mesmo.

<a id="ca-02"></a>
#### CA-02 — Texto de finalidade de nome e CPF em "Seus dados" (FR-1627)
- Descrição: a coleta de nome e CPF tem um texto de finalidade proposto e não validado por quem responde pela proteção de dados. O texto atual diz que o CPF identifica a pessoa "nos resultados". Mas o resultado público não traz CPF (`divulgacao/domain/conteudo.py:6`). A própria `validacao-humana.md` §2 pergunta, no item 3, se isso é preciso.
- Origem (demanda/decisão): auditoria UX C-13 (12/10); L09-84; PR #277; S-072-02; c.13; X-08 em specs-038-073.
- Decisão aplicável: 13/10, "mantenha pendente a validação humana do texto de finalidade" (lote 09, decisão 141). A assumption da 072 diz "sem ela, a feature não se publica", e a feature foi mergeada.
- Spec / PRs / commits: 072 FR-1627; #277.
- Implementação: `portal/templates/portal/meus_dados.html:10-16`.
- Testes: os da 072 conferem a presença do texto, não o conteúdo jurídico.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: falta a manifestação do encarregado. O texto também não traz base legal, controlador, canal do encarregado nem link para política de privacidade, que não existe (CA-04). E "nos resultados" é impreciso quanto ao CPF.
- Impacto: candidato (direito à informação, LGPD art. 9º); gestor (conformidade).
- Prioridade: P1 — é precondição de implantação de um dado pessoal coletado de todos.
- Dependências: CA-04, CA-03.
- Próxima ação recomendada: levar as quatro perguntas da `validacao-humana.md` §2 ao encarregado e corrigir já o "nos resultados", que é factual.
- Precisa de decisão humana? sim — institucional (encarregado de dados do Ifes).
- Confiança: alta.

<a id="ca-04"></a>
#### CA-04 — Aviso de privacidade, termo de uso e ajuda ao candidato
- Descrição: o portal não tem aviso de privacidade, termo de uso, FAQ nem página de ajuda. O manual do candidato (C-12) é o piloto de 08/09, vencido pelas 059, 062, 063, 066 e 072. A única informação ao titular é a frase de "Seus dados" (CA-02).
- Origem (demanda/decisão): `inventario-documental.md:75,114,216-217`; L01-47 (LGPD nas specs); PR #251 (manual com H.18 aberto).
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: nenhuma spec.
- Implementação: inexistente (só `portal/templates/portal/_ajuda_da_acao.html` e `_atendimento.html`).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: falta conteúdo institucional (aviso de privacidade com base legal, controlador, encarregado, retenção), ajuda mínima (como entrar, o que fazer sem código, o que é cada situação) e o capítulo C-12 do manual reescrito.
- Impacto: candidato; equipe de seleção (atendimento).
- Prioridade: P1 — o aviso de privacidade é precondição de implantação, e a ajuda reduz o atendimento de uma equipe de 2–3 pessoas.
- Dependências: CA-02, CA-03, CA-17.
- Próxima ação recomendada: pedir o texto do aviso de privacidade ao encarregado, junto com CA-02. Ajuda e manual depois do SC-605 (CA-01), que mostra onde as pessoas travam.
- Precisa de decisão humana? sim — institucional (texto legal) e de produto (escopo da ajuda).
- Confiança: alta.

<a id="ca-05"></a>
#### CA-05 — Avisos aos candidatos em produção: LGPD pendente e chave sem trava
- Descrição: a chave `AVISOS_AOS_CANDIDATOS` só deve ser ligada em produção depois da validação de LGPD (base legal e retenção da lista de destinatários) e do limite de envio da conta. Em produção ela herda `false` e não tem recusa de inicialização: basta uma variável de ambiente para ligar, e nada no código cobra a validação. O `SORTEIO_FONTE_DE_DEMONSTRACAO`, por exemplo, tem recusa.
- Origem (demanda/decisão): H.5 da auditoria de notificações (09/10); L09-71, L10-53; PRs #269, #272; S-066-01, S-066-06; X-08.
- Decisão aplicável: 09/10 (713f5a59), plano aprovado com "chave desligada em produção" (lote 09, decisão 136). Nenhuma decisão sobre trava de inicialização.
- Spec / PRs / commits: 066 (spec:88, :251, :747-753; plan:28, :172); #267, #269.
- Implementação: `config/settings/base.py:203` (padrão `false`), `development.py:11` e `test.py:15` (`True`); ausente em `config/settings/production.py`.
- Testes: os da 066 cobrem a chave desligada recusando confirmação (FR-1282). Nenhum teste de inicialização em produção.
- Estado: BLOQUEADO (validação LGPD institucional); a trava é IDENTIFICADA E NÃO ESPECIFICADA.
- Lacuna: falta a manifestação do encarregado e o limite real da conta (S-066-03). Falta também uma salvaguarda técnica contra ligar sem a validação.
- Impacto: candidato (tratamento de dado sem base validada); gestor.
- Prioridade: P1 — não impede operar, mas ligar sem validação expõe dado pessoal. Avisos são opcionais na jornada.
- Dependências: CA-03; correio (073, PR #283, outra área).
- Próxima ação recomendada: incluir a base legal dos avisos no mesmo pacote do CA-02 para o encarregado. Decidir se `production.py` passa a exigir uma declaração explícita (por exemplo, `AVISOS_LGPD_VALIDADA`) para aceitar a chave ligada.
- Precisa de decisão humana? sim — institucional (LGPD) e de produto (trava ou só documentação).
- Confiança: alta — conferido no código.

<a id="ca-06"></a>
#### CA-06 — Modalidade de cota ao lado do nome na publicação nominal, e indexação
- Descrição: o resultado público traz posição, nome, protocolo, modalidade e pontuação. Expor a modalidade de cota (PcD, PPI) junto do nome é dado sensível, e o cruzamento com o protocolo identifica a pessoa. Não há decisão sobre o prazo de exposição pública. A página e o PDF do resultado não têm `noindex`.
- Origem (demanda/decisão): L09-43 (07/10, 288c08d9); `doc/pesquisa-divulgacao-de-resultados-2026-10-07.md` ("O que as fontes não resolvem", núcleo 2); PR #261 ("noindex não decide LGPD"); c.7 (governança); registro de convocação para Etapas de 09/10, pergunta 4.
- Decisão aplicável: 07/10 — "a governança das cotas bloqueia só campos públicos" (lote 09, decisão 125). A decisão de mérito segue com o usuário: "continua como decisão de governança sua".
- Spec / PRs / commits: 017 (D-001: nome + protocolo, sem CPF); #261, #262.
- Implementação: `divulgacao/domain/conteudo.py:6`; `divulgacao/infrastructure/documento.py:161-170`; `portal/templates/portal/resultado.html`. `grep noindex` vazio.
- Testes: `tests/portal/test_resultado_publico.py` (sem CPF).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: falta a decisão sobre exibir a modalidade, o prazo de exposição e a indexação por buscadores.
- Impacto: candidato cotista (exposição de dado sensível).
- Prioridade: P1 — compromete direito do titular quando houver resultado real, e a decisão precisa vir antes da primeira divulgação.
- Dependências: CA-03; CA-11 (outra parte do mesmo núcleo da pesquisa).
- Próxima ação recomendada: levar ao encarregado junto com CA-02 e CA-05. O `noindex` é barato e independe da decisão de mérito.
- Precisa de decisão humana? sim — governança e LGPD.
- Confiança: alta.
- **Fundidos neste item:** AV-06.
  - *AV-06 (AV), Exposição da modalidade de cota ao lado do nome na lista pública* — lacuna: validação com o encarregado de dados; eventual `noindex` e prazo de exposição. Próxima ação: levar ao encarregado junto com AV-02. - Precisa de decisão humana? sim — governança/LGPD.

<a id="ca-07"></a>
#### CA-07 — Requerimento de Matrícula: dados sensíveis, momento da coleta e base legal
- Descrição: o Requerimento (029) coleta cor/raça, necessidade específica e faixa de renda familiar. Quando o Edital o declara "na inscrição", a FR-372 exige o Requerimento enviado para submeter a inscrição: o sistema coleta esses dados de **todos** os inscritos, inclusive num certame por sorteio em que a maioria nunca será chamada. A FR-372 foi decidida pelo agente sem pergunta ao usuário. O agente ofereceu a alternativa e não houve resposta. A base legal ficou como hipótese para o encarregado. O e-mail é sempre o da conta (decisão de 16/09). O Requerimento não teve auditoria de UX.
- Origem (demanda/decisão): L05-44, L05-47 (12/09, de544cbf); L07-03, L07-05, L07-13 (16/09, 8f427c86); L06-25 (Requerimento sem auditoria de UX); S-029-01, S-029-03, S-029-04.
- Decisão aplicável: 12/09 (lote 05, decisão 72) — "base legal fica como hipótese para o encarregado/DPO". 16/09 (lote 07, decisões 85–88) — renda em faixa do total; o Edital decide se retira o Anexo em papel; e-mail da conta. FR-372 sem decisão do usuário.
- Spec / PRs / commits: 029 (spec §18 :793-806; FR-372 :520-521; FR-382 minimização); #123, #124; 059 (#251) para o acesso pela convocação.
- Implementação: `requerimentos/models.py:98` (`cor_raca`), `:145` (`renda_familiar_faixa`); `portal/requerimento.py`; `portal/templates/portal/requerimento.html`; `portal/static/portal/requerimento.js`.
- Testes: os da 029 e da 059 (`tests/interface/test_portal_caminho_da_convocacao.py`).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: falta a base legal validada, a ratificação da FR-372 pelo usuário (ou a troca para "na inscrição não bloqueia o envio") e um percurso de UX do Requerimento. R-3 (retirada do Anexo em papel) depende do primeiro Edital real.
- Impacto: candidato (dado sensível coletado de quem não será chamado); equipe de seleção e Registro Acadêmico.
- Prioridade: P1 — envolve dado sensível de todos os inscritos e é precondição de implantação.
- Dependências: CA-02, CA-03; 031 (exportação, outra área).
- Próxima ação recomendada: perguntar ao usuário se mantém a FR-372 e, em Edital por sorteio, se o momento "na inscrição" deve ser desaconselhado na composição. Levar a base legal ao encarregado.
- Precisa de decisão humana? sim — produto (FR-372) e institucional (base legal).
- Confiança: média — o bloqueio está na spec; não reproduzi o percurso.

<a id="ca-09"></a>
#### CA-09 — O conteúdo textual do Edital não aparece no portal
- Descrição: a página da seleção mostra período, oferta, resultados, vagas, sorteio, cronograma e documentos. As seções de texto (Dos Recursos, Da Convocação, Da Matrícula, Disposições) só existem no PDF e na API JSON. A API pública de histórico também não tem link no portal.
- Origem (demanda/decisão): L10-08 (12/10); S-047-03; ED-07(G) da auditoria do PDF (PDF marcado ou HTML acessível — decisão aberta); L09-63, L09-93 (PDF `Tagged: no`).
- Decisão aplicável: 12/10, DA-03 — "sem leitura integral do Edital em HTML" no assistente (lote 10, decisão 143). Vale para o assistente, não necessariamente para o portal. ED-07(G) segue aberta.
- Spec / PRs / commits: 024; 069 (S-069-03, fora de escopo: HTML).
- Implementação: `portal/templates/portal/selecao.html` (seções :101, :184, :368, :406, :426; nenhuma de texto).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: o candidato que usa leitor de tela depende de um PDF sem marcação para ler as regras de recurso e convocação.
- Impacto: candidato, sobretudo com deficiência visual.
- Prioridade: P2 — o PDF existe e é o documento oficial; a lacuna é de acesso e legibilidade.
- Dependências: ED-07(G) (área edital/PDF); CA-08; CA-14.
- Próxima ação recomendada: decidir ED-07(G). Se a escolha for HTML, servir o mesmo conteúdo canônico na página da seleção, com aviso de que o PDF é o oficial.
- Precisa de decisão humana? sim — PDF marcado ou HTML acessível.
- Confiança: alta.

<a id="ca-10"></a>
#### CA-10 — Quantidade de vagas por modalidade (lista) na página pública
- Descrição: a página da seleção lista as concorrências só pelo nome ("Concorrência: …"), sem a quantidade do quadro. O cotista não vê quantas vagas há na lista dele. Na página da publicação do resultado, falta decidir se as vagas por lista vêm da versão citada ou da vigente.
- Origem (demanda/decisão): RC-47 (PENDENTE; o título foi resolvido no #215); ACH-53; L04-109, L05-13, L05-59 (bloqueio desfeito pela 027); PR #102; PR #262; pesquisa de 07/10 ("vagas por lista", AGUARDA DECISÃO); Q8 da auditoria UX.
- Decisão aplicável: Q8 (12/10), "Quantidade por modalidade — fora deste incremento" (072 spec:72). A auditoria de 26/09 havia posto o RC-47 em "Antes do piloto".
- Spec / PRs / commits: 025 (quadro), 027; #215; 072 (fora de escopo).
- Implementação: `portal/templates/portal/selecao.html:260`; `portal/views.py` (`_perfil` passa só os nomes).
- Testes: `tests/integration/portal/test_detalhe_selecao.py::test_o_titulo_da_pagina_e_o_do_edital_e_nao_o_do_processo` (só a metade do título).
- Estado: ADIADO FORMALMENTE
- Lacuna: o dado está no conteúdo publicado e não é exibido.
- Impacto: candidato cotista.
- Prioridade: P2 — a informação está no PDF, e o usuário adiou em 12/10. Volta a P1 se o SC-605 (CA-01) mostrar a pergunta.
- Dependências: CA-01; decisão do #262 (versão citada × vigente).
- Próxima ação recomendada: reabrir na próxima rodada do portal, junto com a decisão do #262.
- Precisa de decisão humana? sim — quando reabrir a Q8, e qual versão a publicação lê.
- Confiança: alta.
- **Fundidos neste item:** ED-42.
  - *ED-42 (ED), Quadro de vagas por modalidade fora da página pública* — lacuna: decisão de quando. Próxima ação: retomar com a decisão de qual versão (citada/vigente) a página lê. - Precisa de decisão humana? sim.

<a id="ca-11"></a>
#### CA-11 — Legibilidade da publicação pública do resultado
- Descrição: a pesquisa de 07/10 deixou abertos os núcleos 2 e 3. No núcleo 2: `<caption>` com as vagas; corte dito em texto; desempate explicado; coluna de modalidade na ampla; nota de sucessão. No núcleo 3: retificação e histórico do resultado com "o que mudou". Da avaliação crítica de 07/10: números em formatos diferentes e pesos não explicados. Não se conferiu se o candidato vê o próprio número no sorteio (P2 do rito, 10/09).
- Origem (demanda/decisão): `doc/pesquisa-divulgacao-de-resultados-2026-10-07.md` (c.7, núcleos 2 e 3 ABERTOS); L09-46 (parcial); L04-102; ED-06 (área PDF).
- Decisão aplicável: 07/10 — "spec do acompanhamento primeiro, depois spec da publicação" (lote 09, decisão 125). A primeira virou a 063; a segunda não foi aberta.
- Spec / PRs / commits: 062 (#260), 063 (#263), #262 (a publicação diz a lista).
- Implementação: `portal/templates/portal/resultado.html` (sem `caption`; o empate residual é dito em :147-148).
- Testes: `tests/portal/test_resultado_publico.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: falta a spec da publicação que a decisão de 07/10 previu.
- Impacto: candidato (entender por que está onde está; decidir se recorre).
- Prioridade: P2 — usabilidade de um ato oficial. Não impede a operação.
- Dependências: CA-06 (`noindex` e coluna de modalidade), CA-10.
- Próxima ação recomendada: abrir a "spec da publicação" prevista em 07/10, com CA-06 como pré-decisão.
- Precisa de decisão humana? sim — prioridade e escopo da spec.
- Confiança: média — o estado vem da tabela c.7 e foi conferido por `grep` (sem `caption`, sem `noindex`); não reli a pesquisa inteira.

<a id="ca-12"></a>
#### CA-12 — Resíduos visuais da 072 e a marca da unidade no portal e nos e-mails
- Descrição: (a) no celular, o resumo da oferta empurra as vagas e o primeiro "Inscrever-se" cerca de 200 px para baixo. (b) A página da seleção diz "Unidade: CEFOR" e o cartão diz "Cefor". (c) A marca "Cefor/Ifes — Seleções" está fixa em todos os e-mails (código, confirmação, convocação, avisos). (d) Sem script, os filtros recolhidos ficam fechados também na tela larga (relato da sessão, não reconferido em tela).
- Origem (demanda/decisão): L09-85, L09-29 (06 e 12/10); PR #277; S-072-04; `doc/pendencias-da-060.md:11-26` (S-060-01); L01-68 (CTA fora da dobra, resolvido em parte pela 072).
- Decisão aplicável: 072 registrou (a) como custo esperado, "se o percurso mostrar… é dado para rever" (`verificacao.md:120-126`). A marca ficou como pendência da 060.
- Spec / PRs / commits: 060, 072.
- Implementação: `portal/views.py:146` (`institution_scope.upper()`); `portal/templates/portal/selecao.html:34`; `inscricoes/application/mensagem.py:63`; `identidade/application/mensagem.py:35-39`; `convocacao/application/comunicar.py:56`; `avisos/domain/mensagem.py:31`; `portal/templates/portal/_consulta.html:47`.
- Testes: os da 072.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a marca é constante, não dado da unidade. O item (a) espera a evidência do SC-605.
- Impacto: candidato (primeira tela no celular); gestor (só com a segunda unidade).
- Prioridade: P3 — cosmético enquanto houver uma unidade. (a) sobe se o CA-01 mostrar rolagem em vez de atalho.
- Dependências: CA-01; 060 (marca por unidade).
- Próxima ação recomendada: unificar "Unidade: CEFOR" com a sigla do cartão numa varredura pequena. Tirar a marca dos e-mails para dado da unidade quando entrar a segunda unidade.
- Precisa de decisão humana? não, para a sigla; sim, para o momento da marca por unidade.
- Confiança: alta para (a)–(c); baixa para (d).

<a id="ca-13"></a>
#### CA-13 — Lotes 2 e 3 da auditoria UX: identidade visual e o que ela adiou
- Descrição: ficaram fora da 072 o rodapé institucional, o favicon, a prévia de compartilhamento, a identidade visual, o C-07 (grupos sem hierarquia), o C-09 (rótulos de trabalho num Perfil de curso) e o estudo de curso, cargo e bolsa (Q4), que não existe. No lote 3: a alternativa B editorial, o endereço legível (a rota usa UUID, inclusive os anexos públicos `/api/v1/public/anexos/<uuid>`), a página de Processo e o aviso de novas seleções.
- Origem (demanda/decisão): c.13 (C-07, C-09, C-15, C-16, lote 3); L09-86; L04-19 (POLISH020-015); L09-94; PR #277.
- Decisão aplicável: 12/10 — Q2 adiar identidade visual; Q4 estudar separadamente, sem campo novo; o lote 3 está sem decisão (072 spec:63-73, :532-545).
- Spec / PRs / commits: 072 (fora de escopo declarado).
- Implementação: inexistente (`grep favicon|og:` vazio nos templates).
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE
- Lacuna: o estudo do Q4 nunca foi aberto, e o adiamento da identidade visual depende do manual de marca.
- Impacto: candidato (confiança, compartilhamento), comunicação institucional.
- Prioridade: P3 — evolutivo, adiado por decisão.
- Dependências: manual de marca do Ifes; CA-12.
- Próxima ação recomendada: nenhuma até a próxima priorização do portal. Registrar o estudo do Q4 como pendência nominal para que não suma.
- Precisa de decisão humana? sim — quando reabrir.
- Confiança: alta.

<a id="ca-14"></a>
#### CA-14 — Acessibilidade do portal nunca validada com pessoa nem com avaliador oficial
- Descrição: a jornada do candidato nunca foi percorrida com leitor de tela real (NVDA ou VoiceOver), nem avaliada no ASES (eMAG 3.1), nem percorrida de ponta a ponta só pelo teclado. Também não foi testada em celular real com teclado virtual. As medições a 375 px são por `iframe` e testes. O contraste do contorno de campo (C-17) ficou fora da 072 por ser token compartilhado com a gestão. O comprovante e o resultado em PDF não têm marcação (o ED-07 é da área PDF).
- Origem (demanda/decisão): decisão de 28/08 "eMAG 3.1 e WCAG 2.1 AA ao mesmo tempo" (lote 01, decisão 1); L01-24, L01-38, L02-27, L03-45 (ressalva de método), L05-09, L10-26; S-009-03 ("jornada inteira por teclado e leitor de tela" não verificada; `specs/009-*/auditoria-ux.md:677`); S-003-01; c.13 C-17; PRs #4, #19, #275.
- Decisão aplicável: 28/08 (acima).
- Spec / PRs / commits: 002 T053, T054 (gestão, mesma pendência); 009; 072 (FR-1640 e outros de anúncio).
- Implementação: marcação ARIA nos templates do portal; `tests/interface/test_acessibilidade_do_portal.py`.
- Testes: `tests/interface/test_acessibilidade_do_portal.py` e os de 375 px (`test_portal_convocacao.py`, `test_detalhe_selecao.py`, `test_resultado_publico.py`).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: nenhum anúncio de `role="status"` ou `role="alert"` foi ouvido. Não há relatório ASES. O C-17 está aberto.
- Impacto: candidato com deficiência (direito de acesso; órgão federal sujeito ao eMAG).
- Prioridade: P1 — compromete o direito de acesso de um público que as cotas PcD alcançam por definição.
- Dependências: CA-09 (conteúdo só em PDF); ED-07 (área PDF).
- Próxima ação recomendada: uma sessão com pessoa usuária de leitor de tela nas quatro tarefas do SC-605 mais o envio de documento, e uma rodada do ASES nas telas do portal. Tratar o C-17 numa varredura de token.
- Precisa de decisão humana? sim — quem conduz, e se o C-17 entra antes da implantação.
- Confiança: alta.

<a id="ca-15"></a>
#### CA-15 — A jornada completa do candidato nunca foi percorrida por pessoa de fora
- Descrição: o SC-605 cobre encontrar, preparar, começar e acompanhar. Envio de documentos, revisão, comprovante, recurso, convocação e Requerimento nunca foram feitos por alguém de fora do projeto. Não verificados: upload em rede lenta, Retificação com rascunho aberto, encerramento com rascunho aberto. A série de polish não cobriu o portal logado depois do envio nem Recursos com dados. Os estados "Preencher Requerimento" e "convocação concluída" foram vistos só por teste. A meta de 5 minutos de inscrição (SC-UX-001) virou indicadores estruturais.
- Origem (demanda/decisão): L01-63; S-009-03; L09-09 (30/09); L09-25 (06/10); L06-25; DP-18 (teste operacional assistido, nunca realizado; PRs #199, #208).
- Decisão aplicável: 30/08 — "Não podemos perder candidatos por conta do sistema de inscrição confuso ou moroso" (lote 01, decisão 9). DP-18 está aberta: quem faz e quando.
- Spec / PRs / commits: 009, 010, 018, 036, 059, 063; DP-18.
- Implementação: `portal/` inteiro.
- Testes: testes de aceitação e integração por feature (`tests/acceptance/portal/`, `tests/integration/portal/`, `tests/portal/`).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: não há registro de uso real da metade da jornada que concentra os atos do candidato.
- Impacto: candidato; equipe de seleção (atendimento no primeiro certame).
- Prioridade: P1 — é a validação que falta antes do primeiro certame real.
- Dependências: CA-01, CA-14, DP-18 (área gestão).
- Próxima ação recomendada: estender o roteiro do SC-605 com as tarefas 5 a 8 (enviar documentos, guardar o comprovante, recorrer, atender convocação) e executá-lo junto com o teste operacional da DP-18.
- Precisa de decisão humana? sim — DP-18 (quem e quando).
- Confiança: alta.

<a id="ca-17"></a>
#### CA-17 — Atendimento ao candidato sem procedimento: correção de CPF, perda de acesso, canal por unidade
- Descrição: (a) com inscrição enviada, o CPF só se corrige "pelo atendimento", e não há tela nem procedimento escrito para isso. (b) Quem perde todas as credenciais tem só "o procedimento institucional existente" (FR-090), e ele não está escrito. Hoje essa pessoa ganharia uma identidade nova e vazia. (c) `PORTAL_ATENDIMENTO` é um só por instalação. Fica a pergunta à equipe: alguém espera resposta aos e-mails do sistema?
- Origem (demanda/decisão): L02-18 (01/09); S-010-02; `inventario-documental.md:221`; L10-50, L10-51 (14/10); S-060-01.
- Decisão aplicável: 010 FR-090 — recuperação fora da V1, sem perguntas pessoais, apontando o balcão. 30/08 — "OTP + CPF não pode, sozinho, dar acesso a uma identidade já existente" (lote 01, decisão 19). (c) "a escolha é do produto" (14/10), sem decisão.
- Spec / PRs / commits: 010 (FR-090 :639-643); 072 (`_atendimento.html`).
- Implementação: `portal/templates/portal/meus_dados.html:33-40` (CPF travado, "fale com o atendimento"); `portal/templates/portal/_atendimento.html`; `config/settings/base.py:286`, `production.py:192-199`.
- Testes: os da 010 (recusa de recuperação fraca).
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO (o procedimento que a FR-090 pressupõe)
- Lacuna: não há roteiro de atendimento (correção de CPF com conferência documental, vínculo de identidade nova a inscrições antigas). Falta também uma ferramenta de gestão para isso, ou a decisão de que é manual pelo banco.
- Impacto: candidato; equipe de seleção; administrador.
- Prioridade: P1 — sem isso, a equipe de 2–3 pessoas não tem como resolver o caso mais comum de suporte.
- Dependências: CA-04, CA-16; autenticação institucional da gestão (outra área).
- Próxima ação recomendada: escrever o procedimento de atendimento (documento operacional) e decidir se a correção de CPF e o vínculo pedem tela na gestão.
- Precisa de decisão humana? sim — produto (tela ou procedimento manual) e institucional (quem atende).
- Confiança: alta.
- **Fundidos neste item:** AS-27.
  - *AS-27 (AS), Canal de atendimento com três fontes (Edital, implantação, unidade)* — lacuna: decisão do produto; perguntas à equipe ("alguém espera respostas aos e-mails do sistema?", "quando entra a segunda unidade?"). Próxima ação: fazer as duas perguntas da f55c52a5 à equipe de seleção. - Precisa de decisão humana? sim — produto.

<a id="ca-18"></a>
#### CA-18 — Identidade do candidato por autodeclaração de CPF, sem verificação externa
- Descrição: o CPF é autodeclarado na primeira inscrição. Duas identidades com o mesmo CPF são detectadas e não bloqueadas. Não há provedor governamental (gov.br). Qualquer pessoa com um e-mail pode se inscrever com o CPF de outra.
- Origem (demanda/decisão): L01-70 (L12 da 009); L01-78, L01-79; T-4b em specs-001-037; S-009-02.
- Decisão aplicável: 01/09 — "CPF duplicado é detectado e não bloqueia; reconciliação vira convite" (lote 02, decisão 28). 010 deixa o provedor governamental fora do escopo (spec:810). A identificação por declaração antiga foi removida (FR-048).
- Spec / PRs / commits: 009, 010.
- Implementação: `identidade/` (`CandidateIdentity`, reconciliação em `identidade/application/associacao.py`); `production.py:104-109` recusa a variável vestigial.
- Testes: `tests/acceptance/portal/test_reencontrar_participacao.py`.
- Estado: ADIADO FORMALMENTE
- Lacuna: não há verificação de titularidade do CPF; a conferência fica para a análise documental.
- Impacto: candidato (inscrição em seu nome por terceiro); comissão.
- Prioridade: P2 — o risco é mitigado pela conferência documental e pelo protocolo; gov.br depende de credenciamento.
- Dependências: credenciamento gov.br (institucional).
- Próxima ação recomendada: nenhuma antes do piloto. Registrar como condição de produção a revisitar se houver fraude.
- Precisa de decisão humana? sim — se e quando integrar o gov.br.
- Confiança: alta.

<a id="ca-19"></a>
#### CA-19 — Nome social e identidade de gênero
- Descrição: não há nome social em nenhuma parte do sistema: identidade, comprovante, listas públicas, resultado, convocação. O Edital de demonstração da auditoria do PDF pede "Requerimento de uso do nome social" como documento facultativo, um contorno.
- Origem (demanda/decisão): L07-01, L07-02 (16/09, 8f427c86); `doc/descoberta-029-requerimento-de-matricula.md:302`; `doc/achados-editais-externos.md:355`.
- Decisão aplicável: 16/09 — "Não nesta feature, e vira spec própria. Fica registrado como lacuna conhecida" (lote 07, decisão 87).
- Spec / PRs / commits: nenhuma spec própria aberta (`grep "nome social"` só acha 029 e 071 research).
- Implementação: inexistente.
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE
- Lacuna: a spec prometida em 16/09 não foi aberta.
- Impacto: candidato trans ou não binário (nome civil exposto em listas públicas e na convocação).
- Prioridade: P1 — compromete direito. Para órgão federal, o uso do nome social é obrigação regulamentar (Decreto 8.727/2016); vira P0 para a implantação se o jurídico confirmar que alcança o certame.
- Dependências: CA-06 (listas públicas); CA-07 (Requerimento).
- Próxima ação recomendada: abrir a spec própria decidida em 16/09, com o alcance já nomeado (identidade, comprovante, listas, resultado, convocação).
- Precisa de decisão humana? sim — quando abrir, e confirmação jurídica da obrigação.
- Confiança: alta quanto à ausência; média quanto à leitura jurídica, que não verifiquei com fonte.

<a id="ca-20"></a>
#### CA-20 — Encerramento da participação pelo próprio candidato
- Descrição: o candidato não pode descartar um rascunho, desistir de uma inscrição enviada, corrigir ou substituir documento ou fato declarado depois do envio, nem responder à convocação pelo portal (aceitar ou desistir). A desistência expressa existe só como desfecho registrado pela comissão. O portal mostra apenas "Situação registrada".
- Origem (demanda/decisão): S-009-06 (cancelamento, retificação e substituição fora da 009); L03-69 (válvula para corrigir fato declarado, "feature própria a decidir"); `convocacao/models.py:248` (DESISTENCIA_EXPRESSA).
- Decisão aplicável: 009 fora de escopo (spec:787). 019 D-010 — os atos da convocação não são recorríveis (lote 05, decisão 74).
- Spec / PRs / commits: 009, 019, 059.
- Implementação: inexistente no portal (`portal/urls.py` sem rota de descarte ou desistência; `portal/templates/portal/convocacao.html:53-54` só exibe).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: falta decidir o que o candidato pode encerrar sozinho e com que efeito: rascunho; inscrição enviada (não excluir, registrar desistência); convocação.
- Impacto: candidato; equipe de seleção (registra desistências recebidas por e-mail ou balcão).
- Prioridade: P2 — tem contorno manual; pesa no volume de atendimento.
- Dependências: CA-17; princípio "nada é excluído" da Constituição (desistência como ato, nunca exclusão).
- Próxima ação recomendada: levantar no primeiro certame real quantas desistências chegam por fora antes de especificar.
- Precisa de decisão humana? sim — escopo.
- Confiança: alta.

<a id="ca-21"></a>
#### CA-21 — Comunicação ativa que ainda não existe
- Descrição: hoje o sistema envia código e aviso de credencial, confirmação de inscrição, convocação (quando o Edital a comunica por mensagem) e avisos complementares manuais de resultado e de chamada (066). Não envia: aviso de Retificação do Edital a quem tem inscrição ou rascunho; decisão de recurso; confirmação do envio do Requerimento; aviso por Etapa ou convocação para Etapa (heteroidentificação, entrevista); "só quem mudou"; agendamento; descadastro e bounce; envio de teste ao operador.
- Origem (demanda/decisão): L01-82, L03-44 (comunicação ativa); L07-12; L10-49; c.9 ("G, posterior", ABERTO); S-066-04; registro de convocação para Etapas de 09/10 (c.10, cinco perguntas, AGUARDA DECISÃO).
- Decisão aplicável: 09/10 — agendamento fora do MVP; sem exclusão manual individual de destinatários (lote 09, decisões 133–134). Toda situação nova exige revisar a FR-084, que já foi revisada três vezes (010, 019, 066).
- Spec / PRs / commits: 010 FR-084; 066; `tests/test_situacoes_de_mensagem.py` (conta as quatro situações).
- Implementação: só as quatro situações em `tests/test_situacoes_de_mensagem.py:31-36`.
- Testes: `tests/test_situacoes_de_mensagem.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a lacuna mais sensível é a Retificação: o rascunho aberto passa a ver a versão nova sem aviso por e-mail, e o inscrito com inscrição enviada não é avisado.
- Impacto: candidato.
- Prioridade: P2 — os avisos manuais da 066 cobrem resultado e chamada; o resto se informa pelo portal.
- Dependências: CA-05 (LGPD dos avisos); registro de 09/10 (convocação para Etapa, área AV).
- Próxima ação recomendada: priorizar o aviso de Retificação como próxima revisão da FR-084.
- Precisa de decisão humana? sim — quais situações e em que ordem.
- Confiança: alta.

<a id="ca-22"></a>
#### CA-22 — Avisos complementares (066): validação com pessoa e resíduos do despacho
- Descrição: (a) o SC-485 (operadora nova envia em ≤ 3 min) foi medido por percurso automatizado, em ~68 s; a medida com pessoa ficou para o teste da Lei 15.263. (b) Uma recusa 5xx do remetente (`MAIL FROM`) é classificada por destinatário e marca o lote inteiro como falha definitiva, sem parar a execução. A revisão recomendou parar. (c) A chamada é identificada pelo texto livre da referência: duas chamadas com a mesma referência viram uma. (d) O despacho relê os destinatários das últimas 24 h a cada minuto. (e) O limite de 60/min é inicial e depende da conta do setor. (f) A porta 465 (SSL implícito) não é suportada.
- Origem (demanda/decisão): L09-71 a L09-75 (09/10, 713f5a59); L10-47; PR #269 (pontos 2 e 4 "registrados para decisão"); S-066-02, S-066-03; `specs/066-avisos-complementares/verificacao.md:21-22`.
- Decisão aplicável: 09/10 — corrigir só os achados 1 e 3 da revisão; os demais ficaram registrados (lote 09, decisão 137).
- Spec / PRs / commits: 066; #267, #269, #272.
- Implementação: `avisos/application/despacho.py`; `avisos/domain/mensagem.py:20-31` (o aviso diz que não substitui a publicação oficial); `config/settings/base.py:206-219`.
- Testes: os da 066.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: (b) e (c) aguardam decisão. (e) e (f) dependem do setor de correio. (a) depende de pessoa.
- Impacto: equipe de seleção (operadora); candidato (aviso que não chega ou que chega em duplicidade).
- Prioridade: P2 — os avisos estão desligados em produção (CA-05).
- Dependências: CA-05; 073 (correio, PR #283).
- Próxima ação recomendada: decidir (b) e (c) antes de ligar a chave. Perguntar ao setor de correio o limite da conta e a porta.
- Precisa de decisão humana? sim — (b), (c), e informações do setor.
- Confiança: média — (b) a (d) vêm do PR e da sessão; não reli o despacho linha a linha.

<a id="ca-23"></a>
#### CA-23 — O texto do reenvio da convocação sugere prazo novo
- Descrição: a regra está certa: reenviar não reinicia o prazo, como prova `test_reenvio_nao_reinicia_prazo.py`. Mas o e-mail diz "contado do envio desta mensagem", e as telas do portal dizem "contado do envio da comunicação". O cartão "enviada em" mostra só o último envio. O candidato que recebe o reenvio pode supor um prazo novo e perder a vaga. Que o envio tardio encurte a janela não foi verificado.
- Origem (demanda/decisão): `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md` (achado #33, ABERTO); PR #267; c.9 (margem).
- Decisão aplicável: "fica para decisão do usuário" (achado); PR #267, "os dois resíduos de redação ficam registrados… para decisão posterior".
- Spec / PRs / commits: 019 (UX-038), 050, 059; #267.
- Implementação: `convocacao/application/comunicar.py:60`; `convocacao/application/selectors.py:119-127`; `portal/templates/portal/convocacao.html:42`; `portal/templates/portal/_convocacao_da_inscricao.html:22-23`.
- Testes: guardiões que prendem o texto: `tests/unit/convocacao/test_mensagem.py:82`, `tests/test_vocabulario_da_convocacao.py:136`, `tests/interface/test_portal_caminho_da_convocacao.py:356`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a redação e o "enviada em" precisam de decisão. Corrigir exige emendar a UX-038 da 019 e os guardiões.
- Impacto: candidato convocado (pode perder o prazo por ler errado).
- Prioridade: P1 — afeta diretamente o direito à vaga; a correção é de texto.
- Dependências: lado da gestão da convocação (área AV), que mostra o mesmo texto.
- Próxima ação recomendada: trocar para "contado do primeiro envio, em DD/MM às HH:MM" e mostrar o primeiro envio, emendando a UX-038 e os guardiões no mesmo commit.
- Precisa de decisão humana? sim — redação.
- Confiança: alta — o texto foi conferido no código.
- **Fundidos neste item:** AV-24.
  - *AV-24 (AV), Redação do reenvio da convocação sugere prazo novo* — lacuna: redação que diga o vencimento absoluto; aviso de envio tardio. Próxima ação: aprovar nova redação e emendar UX-038 e guardiões no mesmo commit. - Precisa de decisão humana? sim — texto.

<a id="ca-24"></a>
#### CA-24 — Pequenas inconsistências do portal e do e-mail de confirmação
- Descrição: (a) o mesmo desfecho aparece como "Vaga aceita" no acompanhamento e como "Situação registrada: Aceite" na convocação. A sessão de 10/10 contou três grafias. (b) O e-mail de confirmação imprime "Concorrência:" vazio quando o Perfil não tem Modalidade (RC-50). (c) `?baixar=0` também baixa (`bool("0")`). (d) Pela tela, o e-mail principal não tem "Remover", e o servidor permite removê-lo (a mais antiga das restantes assume). (e) O código do Processo aparece no cartão e não é buscável, contra a regra "o que se vê é o que se busca". (f) POST em inscrição enviada responde 200; um item sem número/ano mostra "Edital" sozinho (não reconferidos). (g) A FR-128 da 024 descreve um estado inalcançável (Edital publicado sem Evento).
- Origem (demanda/decisão): L09-55 (10/10); RC-50 (PENDENTE, polimento C); L02-22, L02-23 (01/09); L04-93 (U2 da 024), L04-94.
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 010, 024, 059, 063.
- Implementação: `portal/situacao.py:62`; `portal/templates/portal/convocacao.html:54`; `inscricoes/application/mensagem.py:50`; `portal/views.py:2222`; `portal/templates/portal/conta.html:15-28`; `portal/leitura.py:365-380`.
- Testes: nenhum que cubra esses casos.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: microcópia e bordas.
- Impacto: candidato (pequenas confusões).
- Prioridade: P3 — polimento.
- Dependências: nenhuma.
- Próxima ação recomendada: uma varredura de polimento do portal, com teste por item.
- Precisa de decisão humana? não (só a grafia canônica do Aceite).
- Confiança: alta para (a)–(e); baixa para (f).

<a id="ca-25"></a>
#### CA-25 — Comprovante e divulgação imprimem "?" em nome fora do cp1252
- Descrição: o Edital passou a recusar caractere sem grafia (#265, modo `estrito`). O comprovante de inscrição e o documento de divulgação do resultado continuam trocando por "?", em silêncio, o caractere de nome de candidato fora do WinAnsi (por exemplo, nomes indígenas ou estrangeiros com "ẽ" ou "ễ"). Limites declarados: o HMAC do comprovante usa a `SECRET_KEY`, e rotacioná-la invalida os códigos emitidos; com muitos anexos, o comprovante passa de uma página.
- Origem (demanda/decisão): L09-56 (08/10, b82fa294); PR #265; achado #11 (resíduo aberto); L09-95; L01-72, L01-73.
- Decisão aplicável: pendente — "recusar no cadastro, transliterar ou embutir uma fonte". O comprovante de mais de uma página foi aceito como limite em 30/08.
- Spec / PRs / commits: 009 FR-063; #265; 069 (fonte embutida só no Edital).
- Implementação: `publicacoes/infrastructure/pdf.py:443-461` (comentário em :450-451); `inscricoes/infrastructure/comprovante_pdf.py:28`; `divulgacao/infrastructure/documento.py:18`; `inscricoes/domain/autenticidade.py:15-17`.
- Testes: `tests/unit/publicacoes/test_grafia.py`, `test_pdf_grafia.py` (cobrem o Edital).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: o nome do candidato num documento oficial pode sair errado. A rotação da `SECRET_KEY` não tem procedimento.
- Impacto: candidato com nome fora do WinAnsi (provável entre indígenas, público das cotas); operação (rotação de chave).
- Prioridade: P2 — raro, mas atinge documento oficial e público protegido.
- Dependências: área PDF (fonte embutida da 069).
- Próxima ação recomendada: estender a fonte embutida da 069 ao comprovante e à divulgação, a opção que não recusa ninguém. Documentar no guia que a rotação da `SECRET_KEY` invalida os comprovantes.
- Precisa de decisão humana? sim — qual das três opções.
- Confiança: alta.
- **Fundidos neste item:** AV-19.
  - *AV-19 (AV), Nome de candidato fora do cp1252 vira "?" no documento do resultado e no comprovante* — lacuna: fonte com repertório amplo ou recusa/aviso na publicação do resultado. Próxima ação: verificar se a fonte embutida da 069 já cobre; senão, estender `grafia` ao resultado. - Precisa de decisão humana? não.

<a id="ca-29"></a>
#### CA-29 — A vitrine carrega todo o conteúdo publicado, sem paginação nem índice
- Descrição: a vitrine lê todas as versões vigentes e filtra e ordena em Python. Não há paginação. A busca percorre o texto do cartão de cada seleção a cada requisição.
- Origem (demanda/decisão): L03-67 (03/09); S-024-02; D-003 da 024 (índice adiado).
- Decisão aplicável: D-003 da 024 adiou o índice. Q3 (12/10) mantém a organização das encerradas.
- Spec / PRs / commits: 024, 072.
- Implementação: `portal/views.py` (vitrine, ~:290-320); `portal/leitura.py:365-380`.
- Testes: orçamento de consultas da 072.
- Estado: ADIADO FORMALMENTE
- Lacuna: o custo cresce com o número de Editais publicados, inclusive os encerrados.
- Impacto: candidato (tempo de resposta), operação.
- Prioridade: P3 — com uma unidade e dezenas de Editais por ano, não pesa.
- Dependências: SLO de carga nunca medido (área implantação).
- Próxima ação recomendada: medir com `scripts/carga_publica.py` antes de abrir a segunda unidade.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="ca-30"></a>
#### CA-30 — Anexos públicos sem destinatário, sem tamanho, e figuras públicas que faltam
- Descrição: (a) a lista "Edital e documentos" mostra só o rótulo e "(PDF, baixar)". Não diz a que serve cada Anexo (o ANEXO II não é modelo de requisito nenhum) nem o tamanho do arquivo. (b) A relação de inscritos só é publicada para sorteio, embora o 73/2026 mostre que é artefato universal. Comunicados (atos complementares) não têm figura no sistema.
- Origem (demanda/decisão): achado #2 (`doc/achado-anexo-sem-destinatario.md`, ABERTO); L01-74; L04-09, L04-22; PRs #54, #59; S-020-02, S-021-02; RC-26/DP-20 ("não defeito").
- Decisão aplicável: DP-20 classifica o anexo sem destinatário como "não defeito". Nenhuma decisão sobre relação de inscritos e comunicados.
- Spec / PRs / commits: 020, 021, 024.
- Implementação: `portal/templates/portal/_documentos_do_edital.html`.
- Testes: os da 020 e da 024.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: pergunta de produto sem decisão.
- Impacto: candidato.
- Prioridade: P3 — pouco frequente e com contorno no texto do Edital.
- Dependências: área edital (campo de finalidade do Anexo é conteúdo normativo).
- Próxima ação recomendada: nenhuma antes do piloto.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="ca-32"></a>
#### CA-32 — Modalidade nascida por Retificação gravada em silêncio no envio (RC-134)
- Descrição: quando uma Retificação faz um Perfil passar a ter uma Modalidade única, o envio a grava sem perguntar, e os documentos são conferidos contra a inscrição ainda sem ela (A-14.4 da DP-14). Isso foi lido no código e não reproduzido.
- Origem (demanda/decisão): RC-134 (B `[VALIDAR]`, "espera o piloto"); L08-44 (27/09, 60805961); PRs #202, #205.
- Decisão aplicável: DP-14 opção A (27/09). A-14.4 ficou registrado.
- Spec / PRs / commits: DP-14; #202, #205.
- Implementação: `inscricoes/application/submissao.py` (`_modalidade_escolhida`).
- Testes: nenhum que reproduza.
- Estado: NÃO CONFIRMADO
- Lacuna: falta reproduzir.
- Impacto: candidato (documento de cota não pedido, ou pedido a mais).
- Prioridade: P2 — se confirmado, a lista exigida fica errada numa inscrição enviada, que não se corrige.
- Dependências: nenhuma.
- Próxima ação recomendada: escrever o teste que reproduz (Perfil com zero Modalidades, Retificação que acrescenta uma, rascunho aberto antes, envio depois).
- Precisa de decisão humana? não.
- Confiança: baixa — nunca reproduzido.

<a id="ca-33"></a>
#### CA-33 — Acompanhamento: custo por publicação e resíduos da revisão da 063
- Descrição: (a) o acompanhamento cresce cerca de três consultas por publicação (`objetos_recorriveis` da 018): de 23 para 38 com seis publicações. (b) Pontos 5–8 da revisão da 063 não aplicados: prazo de recurso dito duas vezes; filtro de comentários copiado em cinco testes; `situacao.py` importa função interna de `leitura.py` (`_chave_da_lista`) e repete "Ampla concorrência"; data no fuso do servidor. Hoje `TIME_ZONE` é `America/Sao_Paulo`, e o risco só existe se mudar.
- Origem (demanda/decisão): L09-51, L09-53 (07–08/10, 7f78321f); PR #263.
- Decisão aplicável: 08/10 — "corrija os quatro e rode os testes"; 5–8 ficaram registrados (lote 09, decisão 130).
- Spec / PRs / commits: 063; #263.
- Implementação: `portal/situacao.py:33`, `:302`, `:478-485`.
- Testes: os da 063.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: dívida técnica pequena; (a) cresce com certames longos.
- Impacto: candidato (tempo de resposta); manutenção.
- Prioridade: P3.
- Dependências: nenhuma.
- Próxima ação recomendada: incluir na próxima varredura técnica do portal.
- Precisa de decisão humana? não.
- Confiança: média — (a) e o import foram conferidos; o resto vem do PR.

<a id="ca-34"></a>
#### CA-34 — Lacunas de domínio que o acompanhamento declara como ausência (063 L-4 a L-7)
- Descrição: o Edital não estrutura a ação nem a consequência da convocação (`call_information` é opaco). Não há vocabulário de "lista de espera" nem pertença individual ao cadastro de reserva. Não há tipo de certame. A origem do vencimento não fica na convocação. A tela não afirma o que o domínio não sabe.
- Origem (demanda/decisão): S-063-01, S-063-02; `specs/063-acompanhamento-pela-situacao/spec.md:108-131`.
- Decisão aplicável: 07/10 — L-1 "Aguardando chamada"; L-2 o corte não aparece; L-3 "Vaga aceita" (respostas-as-perguntas, 2026-10-07). L-4 a L-7 ficaram como registro para decisão.
- Spec / PRs / commits: 063.
- Implementação: `portal/situacao.py`.
- Testes: os da 063.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: L-4 a L-7 sem decisão.
- Impacto: candidato (sabe que foi chamado, não sabe o que fazer além do Requerimento).
- Prioridade: P3 — a tela é honesta, e a lacuna é de riqueza de informação.
- Dependências: área edital (estruturar `callInformation`, S-026-01); Q4 (tipo de certame, CA-13).
- Próxima ação recomendada: nenhuma até haver Edital real que precise.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="ca-35"></a>
#### CA-35 — Reaproveitamento de documentos entre inscrições
- Descrição: enviar de novo RG, diploma e histórico em cada inscrição. Duas descobertas técnicas: referenciar o arquivo de outra inscrição apagaria o arquivo dela, e uma categoria documental nunca alcançaria Editais já publicados. O caso de maior retorno é o reaproveitamento no mesmo Edital, entre Perfis (por exemplo, tutor em vários polos).
- Origem (demanda/decisão): sessão 59745df3 (07/10), L09-50.
- Decisão aplicável: 07/10 — usuário: "to achando que não compensa, né?"; agente: "agora não compensa"; gatilho: o piloto mostrar inscrições em vários Perfis do mesmo Edital. A oferta de registrar em `doc/` ficou sem resposta.
- Spec / PRs / commits: nenhum.
- Implementação: inexistente.
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE (decisão do usuário em sessão; sem registro no repositório)
- Lacuna: a decisão e o gatilho não estão escritos em lugar versionado.
- Impacto: candidato (retrabalho).
- Prioridade: P3 — evolutivo, condicionado a evidência do piloto.
- Dependências: dados do piloto.
- Próxima ação recomendada: registrar a decisão e o gatilho num documento de `doc/`.
- Precisa de decisão humana? não (já decidido).
- Confiança: alta.

<a id="ca-37"></a>
#### CA-37 — Entrega de documento fora do sistema: presencial, por procurador, por menor
- Descrição: alguns Editais (69/2026) recebem documentos presencialmente, inclusive por procurador. Existe o atestado de fato externo (019 D-004). Não há representação (procurador, responsável legal de menor) nem documento "conferido presencialmente".
- Origem (demanda/decisão): L05-37 (P-12); `doc/achados-editais-externos.md` (P-12 PARCIAL).
- Decisão aplicável: 019 §7 deixou fora a entrega presencial.
- Spec / PRs / commits: 019.
- Implementação: parcial (`convocacao/models.py`, `AtestadoDeFatoExterno`).
- Testes: os da 019.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: representação e conferência presencial.
- Impacto: candidato menor de idade ou representado; comissão.
- Prioridade: P3 — os Editais do piloto não dependem disso.
- Dependências: área edital (requisito por via, P-13).
- Próxima ação recomendada: nenhuma até um Edital do piloto exigir.
- Precisa de decisão humana? sim, quando o caso surgir.
- Confiança: média.

<a id="ca-38"></a>
#### CA-38 — Condição sobre a pessoa (sexo, idade, vínculo de servidor) só informativa
- Descrição: requisitos como sexo e idade (serviço militar) ou vínculo de servidor continuam só informativos. Não há autodeclaração sim/não no `declaredFacts`, e o documento não se condiciona a eles.
- Origem (demanda/decisão): L07-62 (25/09, 183ba11d); achado #9 (resíduo); decisão D1–D5 do recorte documental (25/09).
- Decisão aplicável: 25/09 — "condição do candidato fora" (lote 07, decisão 96; lote 08, decisão 97); "A autodeclaração fica para uma spec própria, com avaliação de LGPD."
- Spec / PRs / commits: 044 (spec:26-28).
- Implementação: inexistente.
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE
- Lacuna: spec própria não aberta.
- Impacto: candidato (envia documento que não se aplica a ele, ou não sabe que se aplica).
- Prioridade: P3.
- Dependências: área edital.
- Próxima ação recomendada: nenhuma até haver demanda de Edital do piloto.
- Precisa de decisão humana? sim, para abrir.
- Confiança: alta.

---


## AV — Condução do certame: avaliação, resultado, recursos, convocação

<a id="av-03"></a>
#### AV-03 — Equipe de 2–3 pessoas: julgador elegível e reavaliação por recurso
- Descrição: o julgador não pode ter avaliado, consolidado, emitido o ato nem publicado o que é atacado (5 impedimentos). Com 2 pessoas não há reavaliação por recurso (exige avaliador diverso) nem substituto de avaliador impedido; comissão pequena pode ficar sem julgador elegível. As perguntas de governança do "Edital pequeno" (piso de duas identidades, legitimidade do arranjo mínimo, aviso antecipado do julgador) seguem sem resposta.
- Origem: S-018-03 (018 spec:1354-1357); PR #74 (08/09, "três perguntas de governança"); memória "equipe inicial de 2–3" (08/09); manual `doc/manual/00-arquitetura-do-manual.md:184,229-231`.
- Decisão aplicável: 08/09 — equipe de 2–3 pessoas acumulando papéis (usuário). Impedimento do julgador aprovado em 06/09 (b863c7e1, "Aceito as sete recomendadas").
- Spec / PRs / commits: 018 (FR-039, FR-042); 036.
- Implementação: `ps/recursos/domain/elegibilidade.py:1-80` (impedimento); manual §A.3 com duas configurações.
- Testes: testes de elegibilidade do julgador (018).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: nenhuma regra/orientação institucional para o arranjo mínimo; nenhum aviso antecipado de que o arranjo escolhido deixará recurso sem julgador.
- Impacto: candidato (recurso que ninguém pode julgar); equipe de seleção.
- Prioridade: P1 — afeta direito de recurso no primeiro certame real com a equipe prevista.
- Dependências: AV-01; AV-14.
- Próxima ação recomendada: decidir com o setor quem julga e registrar; avaliar aviso na comissão quando o arranjo não deixa julgador elegível.
- Precisa de decisão humana? sim — composição mínima e quem julga (institucional).
- Confiança: alta.
- **Fundidos neste item:** GO-07.
  - *GO-07 (GO), Arranjo mínimo de 2–3 pessoas: tabela nunca percorrida e três perguntas de governança abertas* — lacuna: percurso das duas configurações; decisão sobre aviso antecipado de julgador inelegível. Próxima ação: incluir as duas configurações no teste operacional assistido; levar as três perguntas ao usuário. - Precisa de decisão humana? sim — as três perguntas de `descoberta-conducao-por-presidencia-unica.md:147-158`.

<a id="av-04"></a>
#### AV-04 — Reabilitado por recurso antes do marco não alcança o corte
- Descrição: quem foi eliminado numa Etapa anterior à última do marco e reabilitado por recurso não torna o corte obsoleto; a Etapa governada segue recebendo trabalho sob a faixa antiga. FR-218 da 014 × decisão 008 da 014 se contradizem; o código segue a FR-218.
- Origem: achado #32 (`doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md`, 06/10, validado 07/10); L09-39 (de1d85f6/7ab5d2eb/f5a8f73b); PR #257, #259, #272.
- Decisão aplicável: 07/10 de1d85f6 — "reabilitado antes do marco vira achado separado"; 07/10 7ab5d2eb — "abra o PR só com o registro". Escolha entre as três saídas pendente.
- Spec / PRs / commits: 061 D-002 (fora); `a768dc95`, `be153d8e`.
- Implementação: `ps/classificacao/application/corte.py` (`_reingressou` filtra `inscricao_id__in=participantes`).
- Testes: `backend/tests/integration/classificacao/test_corte_reabilitado_antes_do_marco.py` (prende o comportamento atual).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: escolher entre alargar a pergunta, delegar a `estado_do_marco` ou manter e dizer; o doc manda abrir faixa FR-1166 já tomada pela 063.
- Impacto: candidato (recurso deferido sem efeito na progressão); equipe de seleção.
- Prioridade: P1 — compromete o efeito de um recurso ganho, ainda que em caso de borda.
- Dependências: nenhuma.
- Próxima ação recomendada: decidir a saída e abrir spec curta (faixa FR atual, não FR-1166).
- Precisa de decisão humana? sim — qual das três saídas.
- Confiança: alta.

<a id="av-07"></a>
#### AV-07 — Sorteio público nunca exercido de ponta a ponta com a comissão
- Descrição: nenhum sorteio real foi feito; a reprodução por pessoa externa (SC-001 da 021) nunca ocorreu; o rito mudado (congelar relação antes, anular custa Retificação, `drawMethod` do elaborador) não foi validado com a comissão; o cenário sorteio + cotas (034+035) nunca foi percorrido; `seed_demo` semeia uma só lista; a 037 percorreu só metade do marco por sorteio.
- Origem: S-021-01; L04-99 (2acf27b6, 10/09: "valem checar com a comissão"); L06-24; L04-56; L07-35; L03-51; L08-24 ("piloto é por sorteio").
- Decisão aplicável: 07/09 8af9d708 — manter o rito com transmissão no YouTube usando o sistema; 10/09 c1e1e429 — "preservar a maneira como a equipe já trabalha"; D-G3 (19/09) — fonte pública externa declarada.
- Spec / PRs / commits: 021, 034, 035, 037; PR #82, #83, #97.
- Implementação: `ps/sorteios/` (relação, ocorrência da Loteria Federal, manifesto); verificador `ps/portal/static/portal/sorteio-cli.js`.
- Testes: suíte da 021/035; E2E real atrás de `SORTEIO_E2E_FONTE_REAL`.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: ensaio com a comissão (sorteio com cotas, transmissão, publicação), reprodução externa, demonstração com três listas.
- Impacto: equipe de seleção; candidato (confiança no sorteio).
- Prioridade: P1 — o piloto é por sorteio e o rito nunca foi exercido por quem vai operá-lo.
- Dependências: AV-28; AV-26; AV-08.
- Próxima ação recomendada: ensaio assistido com a comissão num banco de demonstração com cotas, incluindo reprodução pelo verificador.
- Precisa de decisão humana? sim — quem participa e quando.
- Confiança: alta.

<a id="av-09"></a>
#### AV-09 — Exportação para o Registro Acadêmico e Requerimento de Matrícula: validação externa
- Descrição: a 031 gera `.xlsx` de 34 colunas, mas nunca foi importada no RA; as perguntas Q-1 (célula vazia), Q-2/Q-7 (`CLASSIF_CURSO_FINAL`), Q-3 (protocolo opaco), R-1 (ausência de "Indígena" em COR), R-1c (renda per capita) e a coluna 16 seguem sem resposta. Duas decisões do agente sem aprovação explícita (papel `exportador`; prévia auditada só quando nomeia pessoas). Do Requerimento (029): Q-1, Q-4, Q-5, Q-9, R-3 (retirada do Anexo depende do 1º Edital), R-4/R-7.
- Origem: L07-14 (8f427c86/55ee1319); L07-17; S-031-01..06; S-029-01, S-029-03, S-029-04; RC-95; PR #125, #127, #130, #155.
- Decisão aplicável: 16/09 8f427c86 — dados externos saem vazios; título eleitoral coletado no requerimento; nacionalidade lista fechada (D-001, D-007, D-008). 18/09 55ee1319 — população só resultado definitivo, vigente, situação elegível.
- Spec / PRs / commits: 031 (49/53; T001–T003, T038 abertas); 029.
- Implementação: `ps/matriculas/` (`domain/colunas.py`, `application/exportar.py:299`); `ps/interface/views.py:5088-5140`.
- Testes: testes da 031 (geração); nenhum de importação no destino.
- Estado: BLOQUEADO
- Lacuna: conversa com o RA (T001–T003) e importação real (SC-143).
- Impacto: equipe de seleção e RA (redigitação se o arquivo não importar); candidato (matrícula atrasada).
- Prioridade: P1 — sem a validação o fim do ciclo volta a ser manual; é P0 para a implantação de Editais discentes.
- Dependências: Registro Acadêmico; AV-24.
- Próxima ação recomendada: agendar a conversa com o RA com a lista de perguntas da 031 (spec:479-503) e registrar respostas.
- Precisa de decisão humana? sim — externa (RA) e confirmação das duas decisões do agente.
- Confiança: alta.
- **Fundidos neste item:** AS-26.
  - *AS-26 (AS), Registro Acadêmico: exportação pronta, nunca importada no destino* — lacuna: a conversa com o Registro Acadêmico e uma importação real. Próxima ação: levar T001–T002 numa conversa única com o Registro Acadêmico, com um arquivo gerado do `seed_demo` corrigido para `PPI`. - Precisa de decisão humana? sim — aprovar o papel `exportador`; quem conversa com o Registro Acadêmico.

<a id="av-10"></a>
#### AV-10 — Barema estruturado e autopontuação vinculante
- Descrição: a Etapa tem uma nota total; não há critérios com teto por item nem autopontuação ("Expectativa de pontuação", vinculante no 173/2025). Barema só como anexo PDF; o avaliador lança a soma calculada fora; barema por curso (K=2) colapsa numa Etapa.
- Origem: L02-38, L03-57, L04-12, L04-79, L05-81 (AX-4), L06-14 (ACH-56), L07-70; RC-64; P-7; S-012-01; T-5; DP-10; PR #34, #122.
- Decisão aplicável: 04/09 eeca206a — "Apuração externa por ora (Recomendado)" (D-4 da 015); 03/09 — "Eu não reabriria a 012 para colocar barema estruturado"; DP-10 aberta.
- Spec / PRs / commits: fora de escopo em 012, 013, 014, 015, 020, 030.
- Implementação: inexistente (`grep barema|autopontua` em `ps/` só em texto de seções/validação).
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE
- Lacuna: modelo de barema, cálculo e conferência; a apuração paralela continua nos Editais de títulos.
- Impacto: avaliador (soma à mão, sem conferência); candidato (nota sem decomposição para recurso).
- Prioridade: P2 — não bloqueia o piloto por sorteio, mas mantém planilha em todo Edital de títulos.
- Dependências: DP-10; AV-11; AV-13.
- Próxima ação recomendada: decidir DP-10 quando houver Edital de títulos escolhido para operação.
- Precisa de decisão humana? sim — DP-10.
- Confiança: alta.

<a id="av-11"></a>
#### AV-11 — O ciclo depende de planilhas: sem exportação de inscritos/resultados, sem importação de notas
- Descrição: não existe exportação CSV/planilha de inscritos, resultados, classificação ou trilha; não existe importação de notas (prova objetiva ou banca externa) nem de resultados. Notas produzidas fora entram uma a uma na Mesa.
- Origem: `codigo-e-configuracao.md` §8; 040 spec:895-902 (PDF/Excel/CSV como melhoria futura; "o repositório não tem infraestrutura genérica de exportação"); S-021-02 (prova objetiva e importação de notas fora); L03-57.
- Decisão aplicável: nenhuma específica; 040 registrou exportação como melhoria futura.
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente (CSV só em `ps/duvidas/management/commands/avaliar_assistente.py`).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: exportação tabular para conferência e arquivo; importação de notas com trilha.
- Impacto: equipe de seleção (redigitação, conferência paralela); avaliador.
- Prioridade: P2 — o piloto por sorteio não precisa de notas; em Edital de prova/títulos vira P1.
- Dependências: AV-10.
- Próxima ação recomendada: levantar com o setor que planilhas usa hoje no pós-inscrição e decidir se exportação/importação entra.
- Precisa de decisão humana? sim — se e quando entra.
- Confiança: alta.

<a id="av-12"></a>
#### AV-12 — Comissão, alocação e distribuição sem Perfil, polo ou modalidade
- Descrição: alocação Etapa × avaliador e distribuição não conhecem Perfil/polo; comissão única por Processo; 7 polos = 21 colunas; a presidência distribui centenas de inscrições sem saber de qual polo cada uma é.
- Origem: L06-16 (ACH-60, P1); RC-61; DP-11; G9; S-030-02; `doc/manual/00-arquitetura-do-manual.md:1960`.
- Decisão aplicável: nenhuma — DP-11 aberta (nem a parte "A agora": coluna e filtro de Perfil).
- Spec / PRs / commits: 011, 012; 030 fora de escopo.
- Implementação: inexistente — `distribuicao.html`, `alocacoes.html`, `conclusoes.html`, `impedimentos.html` com 0 ocorrências de "Perfil" (15/10).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: coluna/filtro de Perfil na distribuição; escopo de comissão local.
- Impacto: equipe de seleção; avaliador.
- Prioridade: P2 — trabalho manual relevante em Editais multipolo; irrelevante com um Perfil.
- Dependências: DP-11; AV-13.
- Próxima ação recomendada: decidir DP-11; a parte "A agora" (coluna e filtro) é pequena e independe da decisão de escopo.
- Precisa de decisão humana? sim — DP-11.
- Confiança: alta.

<a id="av-14"></a>
#### AV-14 — Reavaliação determinada por recurso: telas não orientam o cumprimento
- Descrição: o caminho existe (consolidação cumpre a decisão), mas o recurso decidido mostra "Sucessor — Nenhum — este recurso não produziu resultado sucessor" sem apontar a distribuição; seis lacunas de orientação; a reavaliação fica fora do "Consolidar as N prontas" e segue uma a uma.
- Origem: L03-34/L04-35 (E2E18-001, resolvido no núcleo); RC-155; RC-63 (c.2, "seis itens"); L08-48 (974d1ea8, 27/09); L08-25.
- Decisão aplicável: 28/09 — RC-62 bloquear conclusão "salvo a reavaliação da 018"; 08/09 manual "Não utilize" (superada, ver Decisões superadas).
- Spec / PRs / commits: 018 FR-068; PR #218 ("não se reproduz").
- Implementação: `ps/resultados/application/consolidacao.py:126-143` (porta da reavaliação); `ps/interface/templates/interface/recurso.html:314-318` (mensagem sem orientação).
- Testes: testes da 018 (cumprimento).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: orientação na peça e na distribuição; inclusão (ou recusa explícita) no lote.
- Impacto: equipe de seleção; candidato (cumprimento atrasado).
- Prioridade: P2 — o caminho existe mas só quem o conhece o encontra.
- Dependências: AV-03.
- Próxima ação recomendada: correção direta de microcópia na peça ("aguarda reavaliação — distribuir na Etapa X") e decisão sobre o lote.
- Precisa de decisão humana? não (a do lote é menor).
- Confiança: média — RC-155/RC-63 não reconferidos item a item.

<a id="av-15"></a>
#### AV-15 — Corrigir Resultado sem recurso (revisão de ofício / anulação)
- Descrição: Resultado fundado em avaliação depois reconhecida como defeituosa não tem remédio interno sem recurso do candidato; superação só por recurso.
- Origem: L02-57 (9b1a378e, 02/09); S-013-03; S-018-01 (revisão de ofício fora, 018 spec:1250).
- Decisão aplicável: 03/09 eeca206a — "recurso não cria classificação oficial automaticamente"; nenhuma sobre revisão de ofício.
- Spec / PRs / commits: 013 (fora), 018 (fora).
- Implementação: inexistente.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: ato de revisão de ofício com motivação e trilha.
- Impacto: equipe de seleção (erro conhecido sem correção); candidato.
- Prioridade: P2 — a autotutela é dever da Administração e hoje exige contorno.
- Dependências: nenhuma.
- Próxima ação recomendada: decidir se entra e com que limites (antes/depois da definitiva).
- Precisa de decisão humana? sim — escopo jurídico.
- Confiança: média.

<a id="av-16"></a>
#### AV-16 — DP-09: recurso sem prova nova (peça sem anexos)
- Descrição: a peça recursal não admite anexos (D-011 da 018). A DP-09 pergunta se isso continua; recomendação "manter" é o status quo sem decisão registrada.
- Origem: DP-09; AUD §13 item 10; RC-89 (descartado: "o recorrente não tem campo de anexo" contraditado pela decisão).
- Decisão aplicável: 06/09 711f5b8c — "A peça recursal admite anexos? Não, na V1 (Recomendada)". Reconfirmação pendente (DP-09).
- Spec / PRs / commits: 018 D-011.
- Implementação: comportamento atual (sem anexo) em `ps/recursos/`.
- Testes: testes da 018.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão de manter ou abrir anexos na peça.
- Impacto: candidato.
- Prioridade: P2 — limita a defesa do candidato em recurso documental.
- Dependências: AV-02 (guarda de mais documentos).
- Próxima ação recomendada: responder DP-09.
- Precisa de decisão humana? sim — DP-09.
- Confiança: alta.

<a id="av-17"></a>
#### AV-17 — Prazo de recurso: três fontes sem vínculo (marco × Cronograma × seção)
- Descrição: a janela recursal mora no marco, o Evento de recurso no Cronograma (tipo em texto livre) e a seção "Dos Recursos" em prosa; podem divergir (visto no 91/2026). A 067 pôs um aviso de conferência que "mostra, não prova".
- Origem: RC-76; L08-28; L10-09 (84c96e5f, 12/10); S-036-03 (ACH-41); E-4; ED-02; PR #215, #268.
- Decisão aplicável: 28/09 — RC-76 "depois do piloto, com o Evento de recurso designado; no piloto, o operador confere à mão".
- Spec / PRs / commits: 067 (aviso); `recursos/domain/janela.py`.
- Implementação: parcial (aviso de conferência na Revisão).
- Testes: testes da 067.
- Estado: ADIADO FORMALMENTE
- Lacuna: vínculo estrutural Evento ↔ marco.
- Impacto: candidato (prazo contraditório); equipe de seleção.
- Prioridade: P2 — conferência manual aceita para o piloto.
- Dependências: área de composição do Edital.
- Próxima ação recomendada: reabrir depois do piloto, como decidido.
- Precisa de decisão humana? não (já decidida).
- Confiança: alta.
- **Fundidos neste item:** CA-31.
  - *CA-31 (CA), Recurso pelo candidato: prazo da tela × Cronograma, e o custo do parecer temporário* — lacuna: (a) a contradição continua visível ao candidato quando o Edital diverge. (b) é revisável. Próxima ação: revisitar depois do piloto, como decidido. - Precisa de decisão humana? não agora (já decidido); sim, se o piloto mostrar o caso.

<a id="av-18"></a>
#### AV-18 — Prévia e documento da divulgação: prazo recursal, versão da janela e lista
- Descrição: o documento oficial do resultado e a prévia não trazem a data-limite do recurso; a prévia não diz qual versão do Edital fundamenta a janela (RC-121); o histórico e a prévia na gestão não dizem a lista (recorte) da publicação.
- Origem: L08-37 (af8e65b6, sobra C do RC-48); c.1 (achado do registro pré-piloto, 28/09); PR #220; L09-48 (f5a8f73b, 10/10).
- Decisão aplicável: 28/09 — RC-121 "versão citada, salvo se concede"; 07/10 — publicação diz a lista no portal (#262).
- Spec / PRs / commits: 017, 047, 062.
- Implementação: ausente em `ps/divulgacao/infrastructure/documento.py` (só cita recurso que causou sucessão, :118-131) e em `previa_de_publicacao.html` (sem prazo nem lista).
- Testes: nenhum para estas ausências.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: frase de prazo no PDF e na prévia; nome da lista na gestão.
- Impacto: candidato (o ato oficial não diz até quando recorrer); equipe de seleção (confere sem saber a lista).
- Prioridade: P2 — o PDF é o documento oficial e omite o prazo que a página pública já mostra.
- Dependências: AV-17.
- Próxima ação recomendada: correção direta no compositor do resultado e na prévia, reusando `janela_do_ato`.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-21"></a>
#### AV-21 — Recorte sem corte nenhum: ninguém é chamável
- Descrição: um recorte de marco sem regra de corte lê vazio na convocação; o #194 e a 046 não decidiram esse caso.
- Origem: S-046-02 (046 spec:572, A-2); L08-15 (2bc3c441/6663da85, 26/09).
- Decisão aplicável: 26/09 0ebd3f4c — "Invariante do Perfil": Perfil sem nenhum marco com corte é impedido. O caso de recorte isolado ficou aberto.
- Spec / PRs / commits: 046; PR #194.
- Implementação: comportamento atual (vazio).
- Testes: nenhum dedicado.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: regra para recorte sem corte.
- Impacto: equipe de seleção (convocação impossível pelo sistema); candidato.
- Prioridade: P2 — beco de condução descoberto só depois da publicação.
- Dependências: nenhuma.
- Próxima ação recomendada: decidir se recorte sem corte impede publicar ou convoca a lista inteira.
- Precisa de decisão humana? sim.
- Confiança: média.

<a id="av-22"></a>
#### AV-22 — Cadastro de reserva não é convocável pelo sistema
- Descrição: Edital só de cadastro de reserva publica sem vaga e não convoca (convocar exige vaga faltante); Perfil só de reserva ainda imprime "os 10 primeiros"; como os percentuais se aplicam no cadastro (ED-12) é pergunta nova; validade, prorrogação e ordem entre modalidades dependem de Edital real.
- Origem: DP-05; RC-58; RC-135; ED-12 (067 spec:508-510); L08-47 (3f708cd8); L09-34 (b2bc7d37); L09-67; L09-33; L08-71 (89/2026); achado #13; P-2.
- Decisão aplicável: 27/09 3f708cd8 — "opção B no piloto atual", spec de reserva só com Edital concreto; 09/10 4d4cd6b0 — Perfil sem vaga imediata omite quadro e reversão, RC-58 aberto.
- Spec / PRs / commits: 067 (D-003); `3f6e344e` (`reserve_only_convocation_external`).
- Implementação: só aviso na publicação (`ps/editais/domain/validation.py`, `reserve_only_convocation_external`).
- Testes: testes da 067.
- Estado: ADIADO FORMALMENTE
- Lacuna: convocar do cadastro; regra de reserva no cadastro (RC-58).
- Impacto: equipe de seleção (Editais de bolsista/mediador conduzidos fora); candidato.
- Prioridade: P2 — fora do piloto por decisão; Editais de reserva (ex.: 89/2026) já existem na amostra.
- Dependências: Edital real de reserva escolhido para operação.
- Próxima ação recomendada: manter adiado; reabrir quando um Edital de reserva for escolhido.
- Precisa de decisão humana? sim — RC-58 (regra) quando reaberto.
- Confiança: alta.

<a id="av-23"></a>
#### AV-23 — Nenhum ato registra matrícula efetivada ou contratação
- Descrição: o desfecho mais avançado é o Aceite ("Vaga aceita"); não há ato de matrícula/contratação nem desfechos tipados (matrícula, bolsa, contratação). A visão institucional não tem fonte canônica de matrícula; a ocupação não registra quem ocupa.
- Origem: L09-54 (7f78321f, 07/10); S-063-01 (L-1, L-3); S-040-02 (G-001); L05-71 (desfechos tipados, UX-035); L08-82.
- Decisão aplicável: 07/10 7f78321f — situação nomeia o Aceite como "Vaga aceita"; L-1..L-3 decididas como ausência na tela, com decisão futura registrada.
- Spec / PRs / commits: 019, 063, 040.
- Implementação: inexistente (`ps/convocacao/models.py:243-252`, sete espécies de desfecho, nenhuma de matrícula).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: ato de matrícula efetivada (ou importação do RA) que feche a ocupação e o certame.
- Impacto: gestor (funil sem fim); equipe de seleção (controle paralelo de quem matriculou).
- Prioridade: P2 — o ciclo termina fora do sistema.
- Dependências: AV-09; AV-31.
- Próxima ação recomendada: decidir se a matrícula é ato do sistema ou fato importado do RA.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="av-25"></a>
#### AV-25 — Sorteio dá recorte próprio à Modalidade declarada como ampla (derivação divergente)
- Descrição: o sorteio deriva recortes por conta própria (não usa `editais/domain/recortes.py`): oferece recorte à AC declarada (sem vagas) além do "todos os inscritos", e não mostra quantidade por recorte. É a "segunda grafia" da ampla no domínio do sorteio.
- Origem: RC-73; S-034-02 (034 D-004); L06-22, L07-28 (535c60fd); S-025-02; L05-04; PR #96, #102.
- Decisão aplicável: ~18/09 3bd46d67 — "o sorteio permanece registrado como divergência" (escopo estreito da 034); retirá-la exige decidir como atos históricos continuam alcançáveis.
- Spec / PRs / commits: 034 D-004; 021 D-006.
- Implementação: `ps/sorteios/application/previa.py:24-60` (lista própria de recortes).
- Testes: nenhum que una as derivações.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: unificar a derivação de recortes do sorteio com a da classificação.
- Impacto: equipe de seleção (bloco vazio que confunde onde publicar); candidato.
- Prioridade: P2 — atinge o piloto por sorteio em Edital com cotas.
- Dependências: AV-07.
- Próxima ação recomendada: spec curta que leve o sorteio a `recortes.py`, com a regra para atos já emitidos.
- Precisa de decisão humana? sim — tratamento dos atos históricos.
- Confiança: alta.

<a id="av-26"></a>
#### AV-26 — Sorteio condicionado no texto, incondicional no sistema
- Descrição: Editais reais (78/2026) condicionam o sorteio a haver mais inscritos que vagas; o sistema sorteia sempre e nada avisa na Revisão.
- Origem: achado #39 (12/10); L09-92 (46626552).
- Decisão aplicável: nenhuma — "Registro, não escopo", 3 perguntas.
- Spec / PRs / commits: 069 (mantém o texto literal), 070 CA-12.
- Implementação: `ps/sorteios/application/relacao.py` recusa só relação vazia.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: condição declarável ou aviso na publicação.
- Impacto: candidato (sorteio que a norma dispensava); equipe de seleção.
- Prioridade: P2 — divergência entre norma e execução no ato oficial.
- Dependências: AV-07.
- Próxima ação recomendada: responder as 3 perguntas do achado.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="av-28"></a>
#### AV-28 — Trilha do Edital não reúne todos os atos da condução
- Descrição: a trilha do Edital passou a reunir apuração, convocação, desfecho, comunicação, atestado e instrução de recurso, mas não ordenação, corte, consolidação de Resultado, sorteio, publicação de resultado, admissibilidade e julgamento.
- Origem: L05-32 (73960a45); PR #108 ("promete 'todo ato praticado'"), #120 ("é feature, e nasce de spec").
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 019 FR-296; 036.
- Implementação: `ps/auditoria/selectors.py:86-159` (`_atos_da_conducao`).
- Testes: testes da 019/036 sobre a trilha.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: incluir os demais agregados da condução.
- Impacto: auditor; gestor (responder questionamento exige o banco).
- Prioridade: P2 — prestação de contas do certame incompleta na tela.
- Dependências: nenhuma.
- Próxima ação recomendada: estender `_atos_da_conducao` com o mesmo padrão.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-29"></a>
#### AV-29 — Ninguém é avisado: avaliador, comissão, julgador; sinais ausentes de sorteio e requerimento
- Descrição: nenhuma notificação a avaliador, comissão, gestor ou julgador; o painel não sinaliza sorteio vencido nem requerimentos de matrícula pendentes; o painel 038 ficou sem sorteio e matrícula.
- Origem: RC-67; RC-85; L06-32 (3bd46d67).
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 038, 045.
- Implementação: inexistente — `send_mail` só em identidade, inscrição, convocação e avisos; `ps/interface/supervisao.py` sem sinal de requerimento.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: sinais no painel; avisos internos.
- Impacto: avaliador, julgador, equipe de seleção (prazos internos perdidos).
- Prioridade: P2 — com equipe pequena o painel compensa parte; e-mail depende de AV-01.
- Dependências: AV-01.
- Próxima ação recomendada: acrescentar os dois sinais ao catálogo da 045; notificação só depois da identidade real.
- Precisa de decisão humana? não.
- Confiança: média — RC-67/RC-85 "não reconferidos" na auditoria; conferido só a ausência de envio.

<a id="av-30"></a>
#### AV-30 — Encerramento do certame sem conferência do que ficou pendente; validade e prorrogação
- Descrição: encerrar o Edital exige só estar publicado; não confere recurso pendente, convocação em prazo, requerimento ou definitividade. A condução continua possível depois, até o Processo encerrar. Validade do certame, prorrogação e suplente para turma futura (P-3) não existem; a cauda do processo não é derivável (038 FR-567).
- Origem: P-3 (L04-46, S-016-02, S-019-02); S-038-03; RC-118 (resolvido para o Processo); `ps/processos/domain/finalizacao.py:75-80`.
- Decisão aplicável: 28/09 — encerrar o Processo exige Editais em estado final (RC-118). Nada sobre o Edital.
- Spec / PRs / commits: 001 FR-006; 019 (P-3 fora).
- Implementação: `ps/processos/domain/finalizacao.py:75-80`; `ps/interface/supervisao.py:552-572`.
- Testes: testes da 001/RC-118.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: conferência de encerramento; validade/prorrogação.
- Impacto: gestor; candidato (suplente sem regra de validade).
- Prioridade: P2 — encerramento é ato normativo sem conferência.
- Dependências: AV-23; AV-22.
- Próxima ação recomendada: decidir o que encerrar o Edital deve conferir.
- Precisa de decisão humana? sim.
- Confiança: média — inferido do código; não há registro de demanda explícita do usuário.

<a id="av-31"></a>
#### AV-31 — Telas da condução nunca auditadas em UX
- Descrição: a série de polish não cobriu Recursos com dados, Sorteio, avaliação em rascunho; o Requerimento (029) e a exportação (031) nunca tiveram auditoria de UX; E2E18-003/004 (legibilidade da peça) seguem abertos.
- Origem: c.5 §5 (encerramento do polish, 01/10); L09-09 (67654248); L06-25; L03-35.
- Decisão aplicável: 01/10 — "rodada futura começa por aí".
- Spec / PRs / commits: 055–058 (não alcançaram).
- Implementação: existente.
- Testes: suítes funcionais.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: auditoria de UX dessas telas.
- Impacto: julgador, equipe de seleção, exportador.
- Prioridade: P2 — telas usadas em momentos de prazo curto.
- Dependências: AV-08.
- Próxima ação recomendada: rodada de polish começando por Recursos e Sorteio.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-33"></a>
#### AV-33 — Página pública do resultado: o que a pesquisa recomendou
- Descrição: sem `<caption>` com vagas, sem corte em texto, sem desempate explicado, sem `noindex`, sem nota de sucessão, sem vagas por lista (Q8).
- Origem: c.7 (núcleo 2 da pesquisa de 07/10); L09-42 (288c08d9); PR #262; 072 Q8.
- Decisão aplicável: 12/10 — Q8 "fora do incremento" (072 spec:72); 07/10 — ordem: spec do acompanhamento primeiro, depois a da publicação.
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente (`grep noindex` vazio; `ps/portal/templates/portal/resultado.html`).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: spec da publicação pública (prevista depois da 063).
- Impacto: candidato.
- Prioridade: P3 — evolutivo; o essencial (posição, lista, prazo) já está.
- Dependências: AV-06.
- Próxima ação recomendada: abrir a spec da publicação quando o usuário priorizar.
- Precisa de decisão humana? sim — prioridade e Q8.
- Confiança: alta.

<a id="av-34"></a>
#### AV-34 — Duas avaliações por inscrição: regra de combinação
- Descrição: a 046 fechou o beco (Etapa com mais de uma avaliação e Resultado exigido não publica), mas média, quórum e divergência não existem; segunda leitura segue inconsolidável.
- Origem: achado #12; L02-58, L03-58 (eeca206a); L07-69 (6c13e32b); RC-29; DP-06; S-013-02.
- Decisão aplicável: 26/09 0ebd3f4c — "Impede só se exigido" (046 D-001); DP-06 — a regra de combinação espera um Edital real.
- Spec / PRs / commits: 046 (#188, `064228c7`).
- Implementação: `ps/editais/domain/validation.py:2060-2116` (`stage_result_unreachable`).
- Testes: `unit/editais/test_etapa_sem_resultado.py`.
- Estado: ADIADO FORMALMENTE
- Lacuna: regra de combinação declarada no Edital (incremento "013.1").
- Impacto: avaliador; equipe de seleção (Editais de dupla leitura fora).
- Prioridade: P3 — decidido esperar Edital real.
- Dependências: Edital real com segunda leitura.
- Próxima ação recomendada: medir quantos Editais da amostra usam dupla leitura.
- Precisa de decisão humana? não (já decidida).
- Confiança: alta.

<a id="av-36"></a>
#### AV-36 — Reversão hierárquica e reversão dentro do polo
- Descrição: a reversão é cota → ampla, com duas espécies de gatilho; não há cadeia de destinos (reversão hierárquica) nem reversão dentro do polo do 173/2025 (P-5, polo = Perfil responde parte).
- Origem: L05-15 (8a1c834a); P-5 e forma (a) de `achados-editais-externos.md`; AX-15; L03-54.
- Decisão aplicável: 12/09 73960a45 — "Duas espécies declaradas" de gatilho.
- Spec / PRs / commits: 016, 034.
- Implementação: `ps/ocupacao/domain/reversao.py:1-25`.
- Testes: testes da 016/034.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: lista de destinos de reversão.
- Impacto: candidato cotista em Editais com reversão encadeada.
- Prioridade: P3 — sem Edital do alvo que exija.
- Dependências: DP-10.
- Próxima ação recomendada: manter registrado.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="av-37"></a>
#### AV-37 — Expressividade do desempate
- Descrição: desempate não alcança parcela de Etapa (L-3); `FatoDeclarado` sem booleano ("fez o curso", L-4); desempate por sorteio executado no sistema não existe.
- Origem: L04-03, L04-04 (8af9d708); S-015-02; L08-82.
- Decisão aplicável: 04/09 eeca206a — "Fatos declarados pelo Edital (Recomendado)".
- Spec / PRs / commits: 015 (fora).
- Implementação: `FatoDeclarado` só `DATA` e `INTEIRO`.
- Testes: —
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: tipos de fato e critérios adicionais.
- Impacto: equipe de seleção (desempates resolvidos fora).
- Prioridade: P3 — evolutivo.
- Dependências: nenhuma.
- Próxima ação recomendada: medir na amostra quantos Editais usam esses critérios.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="av-38"></a>
#### AV-38 — Segunda instância recursal
- Descrição: o 57/2026 prevê 2ª instância; a 018 não tem reconsideração nem órgão recursal distinto.
- Origem: L04-78 (df245428); S-018-01; L05-07 (D-011 da 018 como pressão).
- Decisão aplicável: RC-90 ("órgão recursal distinto") descartado em 26/09 por contradizer decisão da 018.
- Spec / PRs / commits: 018 (fora).
- Implementação: inexistente.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: segundo grau de julgamento.
- Impacto: candidato em Editais com 2ª instância.
- Prioridade: P3 — um Edital da amostra; equipe de 2–3 pessoas torna a 2ª instância difícil de compor.
- Dependências: AV-03.
- Próxima ação recomendada: manter registrado.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-39"></a>
#### AV-39 — Backlog do rito do sorteio
- Descrição: cadeia de substituição quase inerte (HTTP 500 da Caixa vira falha de acesso; criar ato de "declarar indisponibilidade"?); risco residual de a comissão não emitir após ver a ocorrência; página "Como este sorteio foi feito"; candidato ciente do próprio número; E-09 (filtro por fonte); E-14/E-15 (data/hora e endereço da transmissão como fato de domínio); reuso copia cláusula de sorteio antiga.
- Origem: L04-101, L04-102, L04-103 (c1e1e429, 10/09); L04-48 (fbd9a85a); L07-55 (183ba11d); RC-43; S-035-02.
- Decisão aplicável: 10/09 c1e1e429 — corrigir os oito P0 e o E-10 (feito, #97); P1/P2 abertos.
- Spec / PRs / commits: 021, 035; `doc/descoberta-rito-do-sorteio-2026-09-10.md`.
- Implementação: parcial (bloco "Sorteio público" E-12).
- Testes: —
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: itens P1/P2 do rito.
- Impacto: candidato; equipe de seleção.
- Prioridade: P3 — melhoram a confiança, não bloqueiam o rito.
- Dependências: AV-07 (o ensaio deve priorizar estes itens).
- Próxima ação recomendada: revisar a lista depois do ensaio com a comissão.
- Precisa de decisão humana? sim — manter a substituição ou criar o ato explícito.
- Confiança: média.

<a id="av-40"></a>
#### AV-40 — Mesa e telas da comissão: identificar a inscrição
- Descrição: a lista da Mesa mostra só protocolo e situação (sem nome, Perfil ou completude); Impedimentos exige digitar protocolo ou identificador (sem seletor); a nota não tem `max` no campo (só ajuda e recusa no servidor na conclusão); identificador cru em telas de ato (RC-69).
- Origem: L03-38 (E2E-008), L03-39 (E2E-009) (533156c5/eeca206a, 03/09); RC-56; RC-69; L03-02 (ddf731ac).
- Decisão aplicável: 01/09 ea8c1d68 — nome visível e CPF mascarado ao avaliador (FR-030).
- Spec / PRs / commits: 012.
- Implementação: `ps/interface/templates/interface/minha_etapa.html:86-92` (Inscrição, Situação; filtros já existem em :66-73); `impedimentos.html:72-75` (campo texto); `mesa_inscricao.html:289` (sem `max`).
- Testes: testes da 012.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: nome na lista da Mesa; seletor de inscrição; `max` no campo.
- Impacto: avaliador; presidente.
- Prioridade: P3 — conveniência.
- Dependências: nenhuma.
- Próxima ação recomendada: correções diretas.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-41"></a>
#### AV-41 — Visualização de anexos na Mesa: zoom e rotação
- Descrição: estado real em 15/10 — documento e formulário lado a lado em tela ≥64rem (FR-112); ampliar e girar ficam com o visualizador de PDF do navegador; desde 07/10 o painel oferece "Abrir em aba própria" (no Firefox o menu "Girar" some na moldura estreita), e o documento instruído do recurso também abre em aba própria. Visualizador próprio (PDF.js) foi descartado. Faltam: medir em que largura o menu » do Firefox volta a caber, conferir os atalhos de girar no Chrome/Edge/Safari e validar com avaliador real.
- Origem: L09-49 (4fe49f9d, 07/10); L02-44 (ea8c1d68); lote 09 §4 (PDF.js descartado).
- Decisão aplicável: 07/10 4fe49f9d — "pode implementar como fix(012)" / "corrige também a tela do recurso" / "deixa os outros links como estão".
- Spec / PRs / commits: 012 FR-112..114; PR #258 (`5f5f4c9a`, `02d84f8f`).
- Implementação: `ps/interface/static/interface/mesa.js:87-102`; `ps/interface/templates/interface/recurso.html:122-131`.
- Testes: `backend/tests/javascript/mesa.test.js`; `backend/tests/integration/avaliacoes/test_documento.py`.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: medições por navegador e uso real (fotos tiradas de lado).
- Impacto: avaliador.
- Prioridade: P3 — contorno existe (aba própria).
- Dependências: AV-08.
- Próxima ação recomendada: incluir no ensaio da Mesa com avaliador real.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-42"></a>
#### AV-42 — Distribuição só depois do período de inscrições
- Descrição: distribuir é recusado enquanto o período está aberto (invariante E2E-017); distribuição incremental é "capacidade nova"; a corrida entre submissão no encerramento e distribuição foi registrada e não implementada.
- Origem: L03-41 (eeca206a, 03/09: "Registro, não implemento"); `ps/avaliacoes/domain/conjunto.py:9-12`.
- Decisão aplicável: 03/09 eeca206a — "sim, implementa o invariante da E2E-017".
- Spec / PRs / commits: PR #32.
- Implementação: `ps/avaliacoes/domain/conjunto.py`.
- Testes: `backend/tests/unit/avaliacoes/test_conjunto.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: distribuição incremental; prova da corrida.
- Impacto: avaliador (análise só começa depois do fim das inscrições).
- Prioridade: P3 — limitação declarada.
- Dependências: nenhuma.
- Próxima ação recomendada: manter; reavaliar se o setor pedir análise durante as inscrições.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="av-43"></a>
#### AV-43 — "Remover da comissão" desativa alocações em cascata
- Descrição: remover membro em um clique desativa em cascata as alocações; o último ato em cascata segue sem conferência.
- Origem: RC-66 (PARCIAL); S-011-03.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 011.
- Implementação: `comissao.html` + `comissao_confirmar.html`.
- Testes: testes da 011.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: conferência do efeito em cascata.
- Impacto: presidente.
- Prioridade: P3 — reversível por nova alocação.
- Dependências: nenhuma.
- Próxima ação recomendada: confirmar no navegador se a confirmação já lista as alocações afetadas.
- Precisa de decisão humana? não.
- Confiança: baixa — não reconferido desde 29/09.

<a id="av-44"></a>
#### AV-44 — Convocação "por publicação": onde se publica
- Descrição: na forma PUBLICACAO a referência é declaração humana; o sistema não publica no site do certame; desde a 069 o documento deixou de dizer "no endereço eletrônico do certame".
- Origem: L05-52 (4eee84f5); L09-89 (46626552, 12/10); PR #111, #222, #275.
- Decisão aplicável: 28/09 — local da publicação registrado "num segundo gesto"; endereço do certame (D3 da linguagem simples) aberto.
- Spec / PRs / commits: 019, 050, 069.
- Implementação: referência declarada.
- Testes: testes da 050.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: endereço do certame congelado na Publicação (lote 2).
- Impacto: candidato.
- Prioridade: P3 — o texto livre do Edital pode suprir.
- Dependências: ED-09/D3 (área do Edital).
- Próxima ação recomendada: tratar junto com o endereço do certame.
- Precisa de decisão humana? sim — D3.
- Confiança: média.

<a id="av-45"></a>
#### AV-45 — DP-15: documento público por marco
- Descrição: com vários recortes, cada lista é uma publicação; não há documento único por marco. A 049 e a 050 seguiram a opção A sem decisão registrada.
- Origem: DP-15; G4/P3 da reavaliação de 27/09; S-049-01.
- Decisão aplicável: nenhuma registrada (na prática A).
- Spec / PRs / commits: 049, 050.
- Implementação: publicação por recorte.
- Testes: —
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão.
- Impacto: equipe de seleção; candidato (lê várias listas).
- Prioridade: P3 — funciona como está.
- Dependências: nenhuma.
- Próxima ação recomendada: registrar a decisão A se for a vigente.
- Precisa de decisão humana? sim — DP-15.
- Confiança: alta.

<a id="av-46"></a>
#### AV-46 — Filtro de concorrência das Inscrições ignora o Perfil ativo
- Descrição: com um Perfil escolhido, o seletor oferece Modalidades de outros Perfis e a lista fica vazia.
- Origem: achado #19 (resíduo); S-044-04; PR #172.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 044.
- Implementação: `ps/inscricoes/application/consulta.py:230-235`.
- Testes: nenhum do resíduo.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: filtrar por Perfil ativo.
- Impacto: equipe de seleção.
- Prioridade: P3 — conveniência.
- Dependências: nenhuma.
- Próxima ação recomendada: correção direta.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-48"></a>
#### AV-48 — Artefatos da 019 atrás da implementação
- Descrição: a FR-273 ainda diz "no máximo um desfecho", e o código implementa desfecho que sucede desfecho; `chamada` e `desfecho_anterior` não estão no `data-model.md`. O contrato já tem `sem_deficit`.
- Origem: L05-50 (485d14d4, PR #111).
- Decisão aplicável: nenhuma registrada (reinterpretação só no corpo do PR).
- Spec / PRs / commits: 019 spec:606; PR #111.
- Implementação: `ps/convocacao/models.py:132,148,288-315`.
- Testes: testes da 019.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: emenda da FR-273 e do data-model.
- Impacto: equipe técnica (rastreabilidade).
- Prioridade: P3 — documentação.
- Dependências: nenhuma.
- Próxima ação recomendada: emendar a spec da 019 num PR de documentação.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="av-49"></a>
#### AV-49 — Escala da condução sem teto medido
- Descrição: consolidação de 10.000 inscrições em 4,33 s sem teto declarado; a relação de habilitados ao sorteio ficou fora da medição; medição em laptop.
- Origem: L05-42 (ffc0d6a5, 12/09).
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: 016.
- Implementação: —
- Testes: `backend/tests/performance/`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: medir a relação do sorteio; teto da consolidação.
- Impacto: operação.
- Prioridade: P3 — volumes do piloto são menores.
- Dependências: nenhuma.
- Próxima ação recomendada: medir junto do SLO de carga da implantação.
- Precisa de decisão humana? não.
- Confiança: média.

<a id="av-50"></a>
#### AV-50 — Duas ordens de travamento (risco de deadlock)
- Descrição: `comando_de_comissao` trava o Processo e depois outros agregados; `replace_draft` trava Edital e Processo num só `select_for_update().select_related("processo")`.
- Origem: L07-10 (8f427c86, 16/09).
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: —
- Implementação: `ps/comissoes/application/__init__.py:75-93`; `ps/editais/application/draft.py:242-248`.
- Testes: nenhum.
- Estado: NÃO CONFIRMADO
- Lacuna: prova de que os dois caminhos disputam as mesmas linhas (um age sobre Edital publicado, o outro sobre Edital em elaboração).
- Impacto: operação.
- Prioridade: P3 — probabilidade baixa pela leitura do código.
- Dependências: nenhuma.
- Próxima ação recomendada: confirmar por leitura ou teste de concorrência antes de mexer.
- Precisa de decisão humana? não.
- Confiança: baixa.


## GO — Gestão institucional, implantação, qualidade e documentação

<a id="go-01"></a>
#### GO-01 — Autenticação institucional da gestão (LDAP escolhido, nunca implementado)
- Descrição: a gestão (`/gestao/`) só tem o seletor de identidade, em que qualquer pessoa digita um `subject` e marca papéis; produção recusa subir com ele e, sem ele, `identificar` responde 503. Não existe primeiro usuário administrativo nem mapeamento grupo do diretório → papel. Sem isso ninguém cria, publica ou conduz Edital fora da máquina do desenvolvedor.
- Origem (demanda/decisão): sessão 0b03a4b5 (28/08) — pergunta estruturada respondida "LDAP"; L01-12, L01-13, L02-28 (31/08–02/09), L03-30 (06/09), L04-36 (08/09), L05-08 (11/09), L08-85 (26/09), L09-01 (30/09), L10-52 (14/10); 002 T056 (S-002-04), 011 FR-023 (S-011-01), 012 FR-057/058 (S-012-02), T-4a; RC-92; B-1 do guia; REA G1/P5; PR #4, #17, #21, #236, #282; c.14 B-1.
- Decisão aplicável: 28/08 (0b03a4b5, `respostas-as-perguntas.md:5`): login institucional = **LDAP**; mesma sessão: adiar autenticação e priorizar o visual ("toda parte de autenticação e autorização pode ser feito depois?"); 31/08 (e790da97): "integração institucional de autenticação é gate de produção da jornada da comissão"; 28/09 (2bc3c441): pedido à TI adiado (ver GO-22).
- Spec / PRs / commits: 002 (FR-001/001a, T056 aberta), 011 FR-018–023, 012 FR-058; nenhuma spec própria de autenticação.
- Implementação: inexistente — nenhuma ocorrência de LDAP/SAML/OIDC/Keycloak em `ps/`, `config/` ou `pyproject.toml` (grep 15/10); `ps/interface/views.py:626-629` (503 + `sem_autenticacao.html`); `ps/interface/identidade.py:1-9` ("Quando o diretório institucional for integrado, só este módulo muda"; "não é fronteira de segurança"); `config/settings/production.py:90-94` (recusa o seletor).
- Testes: nenhum de autenticação real; os de produção só conferem a recusa do seletor (`tests/test_configuracao_producao.py`).
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: adaptador que produza o `Actor` a partir do diretório, papéis por grupo, rotação de sessão no login (GO-03), primeiro administrador, processo de concessão (GO-05).
- Impacto: gestor, elaborador, homologador, publicador, presidência, avaliador, julgador, auditor, exportador — todos; operação (nenhum Edital real sem isso).
- Prioridade: **P0 para a implantação** — sem ela a gestão é 503 em qualquer ambiente que não seja de desenvolvimento; hoje não bloqueia o desenvolvimento local.
- Dependências: GO-22 (pedido à TI, quem hospeda), GO-03, GO-05, GO-02; precondição da página "Configuração e diagnóstico" (073 D-001).
- Próxima ação recomendada: quando houver data de piloto real, abrir spec própria de autenticação a partir de resposta da TI do Ifes (LDAP direto, LDAP via proxy/SSO, ou outro provedor), com mapeamento de grupos → `PAPEIS` e rotação de sessão.
- Precisa de decisão humana? sim — confirmar com a TI se continua sendo LDAP (a resposta de 28/08 foi do usuário, não da TI) e quando abrir o trabalho.
- Confiança: alta — ausência verificada por grep, decisão literal em `respostas-as-perguntas.md`.
- **Fundidos neste item:** AV-01, ED-05.
  - *AV-01 (AV), Identidade real de quem conduz (comissão, avaliador, julgador)* — lacuna: provedor de identidade institucional (LDAP/SSO) não escolhido nem integrado; comissão sem busca no diretório. Próxima ação: obter do Ifes/TI o provedor; especificar a troca de `interface/identidade.py` (o módulo já isola o ponto). - Precisa de decisão humana? sim — qual provedor institucional e como papéis viram grupos.
  - *ED-05 (ED), A segregação elaborar × homologar × publicar só é real com identidade institucional* — lacuna: provedor de identidade institucional inexistente (zero ocorrências de LDAP/OIDC/SAML no código); piso de identidades não decidido. Próxima ação: tratar junto do B-1; ao especificá-lo, incluir o mapeamento papel↔grupo e a resposta às três perguntas do piso de identidades. - Precisa de decisão humana? sim — institucional (provedor, grupos) e de governança (piso de pessoas).

<a id="go-02"></a>
#### GO-02 — API admin e `/metrics` sem autenticação institucional; permissão `observabilidade:consultar` sem dono
- Descrição: a única autenticação da API admin (`/api/v1/admin/`, 21 rotas) é o adaptador de desenvolvimento `Bearer subject|escopo|perm,...`, sem assinatura (forjável). Produção exige `API_AUTHENTICATION_CLASSES` institucional que não existe; o guia usa `RemoteUserAuthentication`, que fecha tudo (403). `/metrics` exige `observabilidade:consultar`, que nenhum papel concede, e autentica por bearer.
- Origem (demanda/decisão): L01-12 (28/08); I-1 do guia; PR #236; `codigo-e-configuracao.md` §2.3, §7.
- Decisão aplicável: nenhuma registrada (a de LDAP, GO-01, é da gestão web).
- Spec / PRs / commits: 001/003 (contrato da API); PR #236 (guia).
- Implementação: `ps/seguranca/api/authentication.py:7-23`; `config/settings/production.py:218-247`; `ps/shared/observability.py:21`; `ps/shared/api/operacional.py:128-133`.
- Testes: `tests/integration/test_observabilidade.py` (com o token de desenvolvimento).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: classe institucional para a API; dono da permissão de métricas (papel de operação ou acesso só por rede); métricas em memória por worker (M-7).
- Impacto: operação (monitoramento sem `/metrics`); nenhum ator de negócio hoje — nenhuma tela consome a API admin.
- Prioridade: P2 — em produção a API e o `/metrics` ficam fechados (falha segura), e o monitoramento usa `/readiness`.
- Dependências: GO-01, GO-24.
- Próxima ação recomendada: decidir junto com GO-01 se a API admin precisa existir em produção; se não, documentar que fica fechada; dar dono a `observabilidade:consultar` ou retirá-la.
- Precisa de decisão humana? sim — a API admin entra em produção?
- Confiança: alta.

<a id="go-03"></a>
#### GO-03 — Sessão: gestão não rotaciona no login, "Sair" sem `flush`, validade padrão de 2 semanas, sem limpeza
- Descrição: `identificar` da gestão só grava a chave na sessão, sem `cycle_key()`; os dois "Sair" (gestão e portal) removem só a chave, sem `flush()`; não há `SESSION_COOKIE_AGE` (padrão Django: 2 semanas); nada agendado limpa sessões nem desafios de acesso (`limpar_terminais` só é chamada por teste). O portal rotaciona no login (`cycle_key`).
- Origem (demanda/decisão): I-5 e B-1 do guia; PR #236; `codigo-e-configuracao.md` §2.3.
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: nenhuma spec; recomendação do guia (§26 I-5).
- Implementação: `ps/interface/identidade.py:141-149` (identificar/encerrar); `ps/interface/views.py:671-674` (sair); `ps/portal/identidade.py:110` (`cycle_key` no portal), `:123-124` (encerrar sem flush); `config/settings/` sem `SESSION_COOKIE_AGE` (grep); `ps/identidade/application/desafio.py:268` (`limpar_terminais`, só `tests/integration/identidade/test_limpeza.py` a chama).
- Testes: `tests/integration/identidade/test_limpeza.py` (só a função).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: rotação na gestão (vai junto com GO-01), `flush()` no logout dos dois canais, validade explícita, comando/timer de limpeza versionado.
- Impacto: candidato (sessão de 2 semanas em máquina compartilhada, logout incompleto); equipe de seleção; operação (crescimento de tabelas).
- Prioridade: **P1 para a implantação** — o portal recebe candidatos assim que implantado; a correção é pequena.
- Dependências: GO-01 (rotação da gestão), GO-19 (prazo de guarda dos desafios), GO-23 (timer).
- Próxima ação recomendada: incremento pequeno: `flush()` nos dois logouts, `SESSION_COOKIE_AGE` explícito, comando de limpeza (sessões + desafios) chamado por timer versionado.
- Precisa de decisão humana? sim — qual validade de sessão para candidato e para a gestão.
- Confiança: alta — conferido no código.
- **Fundidos neste item:** CA-28.
  - *CA-28 (CA), Sessão do candidato longa e "Sair" incompleto* — lacuna: em computador compartilhado (laboratório, lan house), a conta fica aberta por duas semanas para quem não clicar em "Sair". Mesmo clicando, o destino guardado sobrevive. Próxima ação: definir a idade da sessão do portal (por exemplo, algumas horas, renovada por uso) e usar `flush()` em "Sair". - Precisa de decisão humana? não (só o valor).

<a id="go-04"></a>
#### GO-04 — Content-Security-Policy ausente e endurecimento residual do guia
- Descrição: não há CSP (pedida desde a 002, T058). Pendências de endurecimento listadas no guia e reconferidas: sem `500.html` institucional (M-2), uploads gravados 0644 (M-3, sem `FILE_UPLOAD_PERMISSIONS`), arquivo órfão possível (M-4), nome de anexo em cabeçalho por f-string (M-5), sem antivírus (M-6), sem tags de release (M-9), sem ferramenta de anonimização para homologação (M-10), HMAC do comprovante usa a `SECRET_KEY` (rotacionar invalida comprovantes, I-9), sem limite genérico de requisições, cache ou fila para abertura pública (L10-10).
- Origem (demanda/decisão): 002 T058 (S-002-06), L01-25 (28/08), L04-64 (09/09), T-4d; guia §26 M-1..M-10, I-6, I-9; L10-10 (12/10, auditoria do assistente).
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 002 T058 (aberta); PR #236.
- Implementação: inexistente para CSP (grep `CSP`/`Content-Security` vazio em `config/`); `ps/inscricoes/domain/autenticidade.py:61` (HMAC com `SECRET_KEY`); nenhum `500.html` no repositório; `git tag` vazio.
- Testes: nenhum.
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: CSP em modo *Report-Only* e depois aplicada (há `<style>` inline e htmx); chave própria para o HMAC; demais M-n.
- Impacto: candidato (superfície de XSS sem segunda barreira); operação.
- Prioridade: P2 — nenhuma é bloqueadora isolada; CSP e chave própria do HMAC são as de maior valor.
- Dependências: GO-23 (tags/release), GO-30 (rate limit na abertura).
- Próxima ação recomendada: um incremento de endurecimento antes da implantação, começando por CSP Report-Only e chave própria do HMAC (esta exige decidir a migração dos comprovantes já emitidos — hoje nenhum real).
- Precisa de decisão humana? não para CSP; sim para trocar a chave do HMAC.
- Confiança: alta.

<a id="go-05"></a>
#### GO-05 — Concessão e revisão de papéis: ninguém definido como "quem administra o sistema"
- Descrição: as telas de recusa mandam "pedir acesso a quem administra o sistema no Cefor", mas essa figura não existe no modelo nem em documento. Não há guia de administração de acessos (quem concede, revoga, revisa por Processo). A faixa de somente leitura ainda mostra o codinome técnico da permissão (`edital:elaborar`, `retificacao:elaborar`), e há recusas que não dizem a quem pedir (RC-123).
- Origem (demanda/decisão): `doc/pendencias-da-060.md:21` (c.6 "acesso"); inventário documental §4 ("Guia de administração de acessos — AUSENTE"); guia §25 (`:2495`, contas nominais); L07-33 (19/09); RC-123; L08-16.
- Decisão aplicável: 19/09 (62669a3a, `respostas-as-perguntas.md:252-253`): a frase de `recusa.html` igualada à de `lista.html` ("Igualar à irmã") — a frase foi mantida, o destinatário continua indefinido.
- Spec / PRs / commits: 033 (navegação por capacidade); 060 pendências.
- Implementação: `ps/interface/templates/interface/compor_base.html:101-103` e `retificar.html:56-57` (codinome em `<code>`); `recusa.html`/`lista.html` ("quem administra o sistema no Cefor").
- Testes: nenhum que cubra a frase do destinatário.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: papel/pessoa institucional responsável pela concessão; procedimento escrito; rótulo humano da permissão na faixa.
- Impacto: equipe de seleção (não sabe a quem pedir); gestor; operação.
- Prioridade: **P1 para a implantação** — sem dono da concessão, a autenticação real (GO-01) não opera.
- Dependências: GO-01.
- Próxima ação recomendada: decidir quem concede papéis no Cefor e registrar o procedimento junto com a spec de GO-01; trocar o codinome por rótulo humano (correção pequena, independente).
- Precisa de decisão humana? sim — quem administra os acessos.
- Confiança: alta.

<a id="go-08"></a>
#### GO-08 — Comissão: remoção em cascata num clique e cadastro manual de membros
- Descrição: "Remover da comissão" desativa em cascata as alocações do membro sem conferência do último ato (RC-66, parcial). Membros entram por texto colado (`subject, Nome`); a 011 prevê substituir FR-018–022 por busca no diretório quando ele existir.
- Origem (demanda/decisão): RC-66; S-011-01, S-011-03; L02-41 (renome "Alocação por Etapa" pedindo conferência, sem resposta).
- Decisão aplicável: 01/09 (dddb9cca): gestão da comissão por `comissao:gerir` ou vínculo de presidente (implementado).
- Spec / PRs / commits: 011, 012.
- Implementação: `ps/comissoes/domain/autorizacao.py:22-23,65-81`; `ps/interface/templates/interface/comissao.html:173` (texto colado).
- Testes: `tests/` de comissão (vínculos) existentes; nenhum do resíduo do RC-66.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: conferência antes da cascata; busca no diretório (depende de GO-01).
- Impacto: presidência da comissão; avaliador.
- Prioridade: P3 — "espera o piloto" (AUD), sem dado real.
- Dependências: GO-01.
- Próxima ação recomendada: medir no piloto; tratar a busca no diretório na spec de GO-01.
- Precisa de decisão humana? não.
- Confiança: média — resíduo do RC-66 não reconferido em navegador.

<a id="go-09"></a>
#### GO-09 — Credencial do OpenRouter exposta em captura de tela: apagar a antiga não confirmado
- Descrição: em 14/10 a chave do OpenRouter apareceu inteira numa captura de tela colada na conversa. Uma chave nova foi instalada (arquivo fora do repositório, só o usuário lê); o agente pediu que a antiga fosse apagada no painel. Não há confirmação registrada.
- Origem (demanda/decisão): L10-36 (14/10, sessão 7bf91059, digesto linhas 542-589).
- Decisão aplicável: DP-4 da 071 — a única barreira de gasto é o limite da própria chave.
- Spec / PRs / commits: 071 (credencial em `ASSISTENTE_CREDENCIAL`).
- Implementação: n/a (ação no painel do provedor).
- Testes: n/a.
- Estado: NÃO CONFIRMADO
- Lacuna: confirmação de que a chave antiga foi revogada.
- Impacto: operação (custo indevido até o limite da chave).
- Prioridade: P1 — risco de segurança com correção de um minuto.
- Dependências: nenhuma.
- Próxima ação recomendada: o usuário confere no painel do OpenRouter que a chave antiga está revogada.
- Precisa de decisão humana? sim — ação do usuário.
- Confiança: média — a pendência é explícita no digesto; a revogação pode ter sido feita sem registro.
- **Fundidos neste item:** AS-11.
  - *AS-11 (AS), Chave do OpenRouter exposta em captura de tela: revogação não confirmada* — lacuna: confirmar no painel do OpenRouter que a chave antiga foi apagada. Próxima ação: o usuário confere em OpenRouter → Keys e apaga a antiga, se ainda existir. - Precisa de decisão humana? não — é ação do usuário.

<a id="go-13"></a>
#### GO-13 — Condução e Supervisão: resíduos que "esperam o piloto"
- Descrição: depois da 038 e da 045 (RC-78…83 resolvidos), sobram: avisos de composição do Edital não sobem à Atenção (RC-34/N-08, fronteira não decidida); visão global dentro do Processo continua lista plana (RC-77, parcial); exportação vazia sem mensagem e três formas de prazo (RC-84); sorteio vencido e requerimentos pendentes sem sinal (RC-85); recusas que não dizem a quem pedir (RC-123); estado da cauda não derivável (038 FR-567).
- Origem (demanda/decisão): L06-32, L06-33, L07-36, L07-40, L07-42 (16–20/09); L08-34 (26/09); RC-34, RC-77, RC-84, RC-85, RC-123; S-038-03; AUD §"Espera o piloto" (`doc/auditoria-de-consolidacao-2026-09-26.md:432`).
- Decisão aplicável: 09/09 (0c26b370) — supervisão em duas regiões, catálogo fechado; ~19/09 — teto/"parar de escrever spec à frente"; AUD: "não ampliar o painel antes de limpar o ruído".
- Spec / PRs / commits: 022, 038, 045 (#187).
- Implementação: `ps/interface/supervisao.py:495-506` (catálogo), `:1391-1398` (lista plana).
- Testes: testes da 022/038/045.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: os seis resíduos acima; decisão de fronteira do RC-34.
- Impacto: gestor, presidência.
- Prioridade: P3 — dependem de uso real para serem medidos.
- Dependências: GO-31 (teste operacional).
- Próxima ação recomendada: remedir no teste operacional/piloto; só então priorizar.
- Precisa de decisão humana? sim — a fronteira do RC-34 (avisos de composição na Atenção).
- Confiança: média — vários resíduos "não reconferidos em 15/10" na fonte.

<a id="go-14"></a>
#### GO-14 — Visão institucional (040/041): decisões de evolução registradas e não tomadas
- Descrição: a 040 lista na §23 decisões do usuário não tomadas: eixo temporal (ano do Edital × data de publicação, G-005), "pessoas distintas" (G-003), termo "Em preenchimento" (G-011), polo como eixo (G-004, também na 041), série × filtro (G-013), "classificação final" (G-012), visão cross-scope (G-014). A T005 da 040 não foi executada (duplicação pré-existente em `selecoes_publicas`). A G-010 (papel Diretoria) **foi** decidida (ver "Decisões superadas"), mas a spec ainda a lista como pendente.
- Origem (demanda/decisão): L07-45, L07-46, L07-47, L07-48 (21/09); S-040-01..05, S-041-01/02; AUD §13 item 12.
- Decisão aplicável: 21/09 (0b4d88f5): "capacidade própria, inicialmente no gestor, sem inventar o papel diretoria".
- Spec / PRs / commits: `specs/040-*/spec.md:846-888`; 041; 042.
- Implementação: `visao:consultar` no Gestor (`ps/interface/identidade.py:59-75`); `/gestao/visao-geral`.
- Testes: `tests/authorization/test_visao_institucional.py` e testes da 040–042.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: as decisões; exportação de indicadores é "melhoria futura" (não pendência).
- Impacto: gestor/direção.
- Prioridade: P3 — evolutivo; G-004 exige Edital real de múltiplos polos.
- Dependências: Edital real multipolo; GO-10 (G-014).
- Próxima ação recomendada: anotar na §23 da 040 que a G-010 foi decidida em 21/09; deixar as demais para quando houver dados reais.
- Precisa de decisão humana? sim — G-003, G-004, G-005, G-011, G-012, G-013, G-014.
- Confiança: alta.

<a id="go-17"></a>
#### GO-17 — Lacunas da trilha de auditoria
- Descrição: não entram em `RegistroAuditoria`: a entrada do candidato por código; o download do próprio documento pelo candidato; a exportação de matrículas (fica só em `GeracaoDeArquivo`); o acesso direto ao banco enquanto B-1 não fecha. Eventos de credencial do candidato são gravados com `institution_scope=""` (decisão D-012 declarada no código) e não aparecem na consulta. A trilha do Edital reúne Retificações, ocupação, convocação e instrução de recurso, mas não ordenação/corte, consolidação, sorteio, publicação de resultado nem julgamento.
- Origem (demanda/decisão): I-7 do guia; PR #236; PR #108/#120 (12–16/09: a tela "promete todo ato praticado sobre este Edital"); L01-71 (30/08, `CONSULTAR_DOCUMENTO` além do FR-077); L04-61, L04-90 (UUID cru no motivo).
- Decisão aplicável: D-012 (credenciais sem escopo, declarada em `ps/identidade/application/credenciais.py:184-190`); #120: "é feature, e nasce de spec".
- Spec / PRs / commits: 001/003 (trilha), 011 D-018 (recusa de log paralelo), 019 FR-296, 036.
- Implementação: `ps/auditoria/selectors.py:86-140` (`trilha_do_edital` + `_atos_da_conducao`); `ps/portal/arquivos.py` (sem registro); `ps/matriculas/models.py:27-48`; `ps/identidade/application/desafio.py` (sem registro).
- Testes: testes da trilha (011, 019, 036).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: os eventos acima; trilha única do Edital.
- Impacto: auditor; gestor (responder questionamento); candidato (prova de acesso a dado próprio).
- Prioridade: P2 — a trilha principal existe e é append-only; as lacunas pesam em incidente/LGPD.
- Dependências: GO-20 (o que a LGPD exige registrar).
- Próxima ação recomendada: spec curta "trilha completa do certame" listando os atos que faltam na trilha do Edital e decidindo os eventos do candidato.
- Precisa de decisão humana? sim — se login/download do candidato devem ser auditados.
- Confiança: alta.
- **Fundidos neste item:** CA-27.
  - *CA-27 (CA), Atos do candidato fora da trilha de auditoria* — lacuna: não há como responder "quem entrou nesta conta e quando" nem "o titular baixou o documento". Próxima ação: registrar o login (sucesso e falha agregada) e o download do titular na trilha existente, com escopo vazio como as credenciais. - Precisa de decisão humana? não.

<a id="go-18"></a>
#### GO-18 — Imutabilidade em duas camadas de três (tabelas residuais)
- Descrição: `PosicaoNaOrdem` (só gatilho `posicao_coerente` BEFORE INSERT, sem gatilho append-only), `RevisaoEdital` e `GeracaoDeArquivo` (sem recusa no modelo) têm duas das três camadas; Unidade/Autoridade "nada se exclui" só por gatilho, sem a camada de privilégio ausente.
- Origem (demanda/decisão): PR #171, #183 (26/09); achado 42 (`doc/achado-valor-de-fato-sem-gatilho.md`); L02-04 (31/08); L09-32 (06/10).
- Decisão aplicável: nenhuma do usuário; "ficam só registradas" (#183).
- Spec / PRs / commits: 003, 015, 060.
- Implementação: `ps/classificacao/migrations/0001_initial.py:50-62`; `ps/publicacoes/models.py:8`; `ps/matriculas/models.py:27`; `ps/unidades/migrations/0002_nada_se_exclui.py:34-50`; as três primeiras estão em `ps/seguranca/papeis.py:43,86,109`.
- Testes: `tests/integration/test_imutabilidade_do_historico.py`, `tests/integration/test_database_permissions.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: terceira camada em cada uma.
- Impacto: auditor (garantia mais fraca do que a declarada).
- Prioridade: P3 — as duas camadas restantes já impedem alteração pela aplicação.
- Dependências: nenhuma.
- Próxima ação recomendada: decidir se a regra "três camadas" vale para todas; se sim, uma migration por tabela.
- Precisa de decisão humana? sim.
- Confiança: alta.
- **Fundidos neste item:** AV-47, CA-26, ED-39.
  - *AV-47 (AV), Append-only com duas camadas em PosicaoNaOrdem e GeracaoDeArquivo* — lacuna: terceira camada. Próxima ação: manter registrado. - Precisa de decisão humana? não.
  - *CA-26 (CA), Imutabilidade da inscrição enviada só no modelo, sem gatilho no banco* — lacuna: falta a segunda camada (gatilho que recusa `UPDATE` e `DELETE` quando o status anterior é `SUBMETIDA`). Próxima ação: decidir se entra um gatilho condicional, no padrão do `ValorDeFato` (`inscricoes/migrations/0006`). - Precisa de decisão humana? sim — se a Constituição exige as duas camadas para a peça enviada.
  - *ED-39 (ED), `ProvenienciaConteudo` não é append-only* — lacuna: gatilho + privilégio ausente (as duas camadas da Constituição); migration nova. Próxima ação: registrar como achado em `doc/` e decidir se entra no próximo incremento de integridade (é migration pequena, mas muda o `N de M` do provisionamento).
- **Prioridade elevada a P2** pela perspectiva de ED-39.

<a id="go-19"></a>
#### GO-19 — Política de retenção e descarte (B-2) inexistente
- Descrição: não há política institucional nem rotina de expurgo: rascunhos abandonados, documentos de quem nunca enviou, desafios com e-mail digitado, sessões e inscrições crescem sem prazo (inclusive nos backups). A única exclusão é `excluir_registros_do_piloto` (90 dias, manual). Rascunhos com dado pessoal ficam visíveis à gestão (ocultá-los depende da retenção).
- Origem (demanda/decisão): L01-66, L01-69 (30/08), L02-17 (01/09), L08-85 (26/09), L09-02 (30/09); 009 FR-076/L11, 012 FR-057, 013 Assumptions (T-4c, S-009-01, S-012-02); RC-93; B-2 do guia; PR #17, #21, #236; README "Antes de receber dado pessoal real".
- Decisão aplicável: 01/09 (c7194461): "A área candidata não entra em produção com dados reais enquanto a política institucional de retenção/descarte aplicável não estiver definida." 12/10 (7bf91059): registros do piloto excluídos 90 dias após o relatório final, sem chamar de anonimização.
- Spec / PRs / commits: 009, 010 PC-004, 012 FR-057; 071 D-012/D-013.
- Implementação: inexistente (grep `expurg`/`anonimiz` só em comentários); `ps/duvidas/management/commands/excluir_registros_do_piloto.py:1-6` (única exclusão); `ps/identidade/application/desafio.py:56-64` (e-mail canônico de qualquer endereço digitado).
- Testes: nenhum de expurgo.
- Estado: BLOQUEADO
- Lacuna: política institucional (prazos, responsável, base legal) e, depois, rotinas no código; alinhamento com a retenção dos backups.
- Impacto: candidato (direitos LGPD); instituição; operação.
- Prioridade: **P0 para a implantação** — decisão do próprio usuário condiciona dado real a ela; hoje não há dado real.
- Dependências: GO-20 (encarregado), GO-22 (TI), GO-24 (backup).
- Próxima ação recomendada: levar ao encarregado/Cefor uma proposta de tabela de prazos por categoria de dado; depois, spec de expurgo.
- Precisa de decisão humana? sim — institucional.
- Confiança: alta.
- **Fundidos neste item:** AV-02, CA-03.
  - *AV-02 (AV), Retenção e descarte do acervo de avaliação e dos documentos do candidato* — lacuna: prazo de guarda, base legal e procedimento de descarte com o encarregado de dados. Próxima ação: levar ao encarregado a lista do acervo da condução (documentos, avaliações, pareceres, instrução de recurso, exportação) e pedir prazos. - Precisa de decisão humana? sim — política institucional de retenção.
  - *CA-03 (CA), Retenção e descarte dos dados do candidato* — lacuna: prazo e responsável não definidos; sem expurgo de rascunho abandonado, desafio, sessão (o `clearsessions` é só receita do guia) e documento. A promessa do comprovante não tem regra por trás. Aviso de privacidade ausente (CA-04). Próxima ação: obter do Cefor e do encarregado o prazo por tipo de dado. Depois disso, spec curta de expurgo (rascunhos, desafios, sessões, documentos de inscrições encerradas) e ajuste da frase do comprovante. - Precisa de decisão humana? sim — institucional (prazo, responsável, base legal).

<a id="go-20"></a>
#### GO-20 — LGPD institucional: RIPD, encarregado e validações pendentes em cinco specs
- Descrição: não há RIPD nem registro das operações de tratamento; nenhuma validação com o encarregado está registrada. Pendentes: base legal de nome/cargo de autoridade (060); base legal e retenção da lista de destinatários dos avisos (066, H.5 — `AVISOS_AOS_CANDIDATOS` desligada em produção, mas **sem guarda de boot**: ligá-la por variável dispensa a validação); registros e estatuto do assistente (070/071, DA-09/DEP-07); texto de finalidade de nome e CPF (072, FR-1627); exposição da modalidade de cota ao lado do nome na lista pública (pesquisa de 07/10, #261). Não há aviso de privacidade nem termo de uso no portal.
- Origem (demanda/decisão): X-08; S-060-03, S-066-01, S-066-06, S-070-04, S-072-01; L09-27, L09-43 (06–07/10); c.6, c.7, c.9 H.5, c.12, c.13 C-13; PR #269, #272, #277, #261; inventário documental §4.
- Decisão aplicável: 09/10 (713f5a59): chave dos avisos desligada em produção até a LGPD; 06/10: "dados de autoridade seguem sujeitos à LGPD" (C1 da 060).
- Spec / PRs / commits: 060, 066, 070, 071, 072.
- Implementação: `config/settings/base.py:203` (avisos `false`); `config/settings/production.py` sem guarda de `AVISOS_AOS_CANDIDATOS` (grep vazio); `ps/portal/templates/portal/meus_dados.html:15` (finalidade); nenhum aviso de privacidade em `ps/portal/templates` (grep).
- Testes: nenhum de conformidade LGPD.
- Estado: BLOQUEADO
- Lacuna: consulta ao encarregado, RIPD, aviso de privacidade, decisão sobre exposição da modalidade; guarda de boot da chave dos avisos.
- Impacto: candidato; instituição.
- Prioridade: P1 — precondição para ligar avisos e para dado real (sobe a P0 junto com GO-19 na implantação).
- Dependências: GO-19; GO-12 (autoridade).
- Próxima ação recomendada: um único pacote para o encarregado (as cinco perguntas + rascunho de aviso de privacidade); em paralelo, guarda de boot para `AVISOS_AOS_CANDIDATOS` em produção.
- Precisa de decisão humana? sim — institucional (encarregado) e do usuário (exposição da modalidade).
- Confiança: alta.

<a id="go-21"></a>
#### GO-21 — Avaliação de LGPD por spec não é sistemática
- Descrição: a Constituição exige que "cada especificação DEVE avaliar os requisitos aplicáveis da LGPD"; 47 das 74 pastas de `specs/` não mencionam LGPD, e o template de spec não tem seção para isso. A decisão sobre onde registrar a avaliação (seção na spec × interpretação na Constituição) ficou aberta.
- Origem (demanda/decisão): L01-47 (29/08), L02-59 (02/09, C6 da 013).
- Decisão aplicável: 02/09 (9b1a378e): "aplique C1 a C5" — C6 (LGPD) ficou fora, sem decisão.
- Spec / PRs / commits: `.specify/memory/constitution.md:167-169`; `.specify/templates/spec-template.md` (sem seção).
- Implementação: n/a.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: seção obrigatória no template ou nota interpretativa na Constituição.
- Impacto: instituição (conformidade não demonstrável por spec).
- Prioridade: P2 — governança; não bloqueia uso.
- Dependências: GO-20.
- Próxima ação recomendada: decidir a forma (C6) e acrescentar a seção ao template.
- Precisa de decisão humana? sim — governança.
- Confiança: alta (contagem por grep de "lgpd" nos `.md` de cada pasta).

<a id="go-22"></a>
#### GO-22 — Pedido de produção à TI e definição de quem hospeda e empacota (RC-124)
- Descrição: não existe decisão sobre quem serve o sistema em produção nem pedido formal à TI (papéis do banco, provedor de identidade, correio, backup, retenção). O agente alertou que o pedido deve começar semanas antes do piloto real.
- Origem (demanda/decisão): L08-17, L08-18 (26–27/09); RC-124; AUD §13 item 17; REA G1/P5.
- Decisão aplicável: 28/09 (2bc3c441): "sinceramente, não vejo relevância nisso neste momento. são aspectos para implantação em produção."
- Spec / PRs / commits: guia `doc/implantacao-em-producao-ubuntu.md` (#236), 073.
- Implementação: n/a (institucional).
- Testes: n/a.
- Estado: ADIADO FORMALMENTE
- Lacuna: pedido escrito e resposta da TI.
- Impacto: operação; todos os atores (nada roda fora da máquina do usuário).
- Prioridade: **P0 para a implantação** — tem prazo de antecedência e destrava GO-01, GO-19, GO-23–GO-25.
- Dependências: data de piloto real.
- Próxima ação recomendada: quando houver data de piloto, gerar o documento para a TI a partir do guia (§26 e cheat sheet).
- Precisa de decisão humana? sim — quando disparar.
- Confiança: alta.

<a id="go-23"></a>
#### GO-23 — Artefatos de implantação ausentes do repositório
- Descrição: sem servidor WSGI nas dependências (gunicorn instalado fora do lock, sem hash, I-2); sem `STATIC_ROOT` (`collectstatic` falha, I-3); nenhum unit/timer systemd versionado (avisos a cada minuto, limpeza, CEP mensal, backup só como receita); `Dockerfile`/`compose` declaradamente de desenvolvimento (`runserver`); sem `500.html`; sem tags de release.
- Origem (demanda/decisão): L09-03 (30/09); I-2, I-3, M-2, M-9 do guia; RC-124; PR #236; L08-17.
- Decisão aplicável: nenhuma registrada (ver GO-22).
- Spec / PRs / commits: guia (#236); 066 (despacho por timer); 029 (CEP).
- Implementação: `backend/pyproject.toml:9-18` (sem gunicorn; `uv.lock` sem gunicorn); `config/settings/base.py:164` (só `STATIC_URL`); `git ls-files` sem `.service`/`.timer`; `backend/Dockerfile:8-10,59`.
- Testes: job `compose` do CI só sobe o ambiente de desenvolvimento.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: extra `prod` no `pyproject.toml` travado no lock; `STATIC_ROOT` + `collectstatic`; units/timers versionados.
- Impacto: operação.
- Prioridade: **P1 para a implantação** — o guia tem paliativos, mas sem verificação de hash nem reprodutibilidade.
- Dependências: GO-22.
- Próxima ação recomendada: incremento "empacotamento de produção" (extra `prod`, `STATIC_ROOT`, units versionadas) assim que GO-22 definir o alvo.
- Precisa de decisão humana? sim — o alvo de hospedagem (GO-22).
- Confiança: alta.

<a id="go-24"></a>
#### GO-24 — Guia de implantação nunca ensaiado em VM; backup, restauração e monitoramento só como receita
- Descrição: o guia (2849 linhas) foi ensaiado em 29/09 sem VM: `pg_dump`/restauração locais ok; nginx, TLS, firewall, systemd, restic e o passo `sincronizar_unidades` do `ps-migrar` nunca rodaram numa VM. Monitoramento (`ps-verificar`, alertas) e runbook de incidentes são receita.
- Origem (demanda/decisão): L09-04 (30/09); PR #236; inventário documental §1.3; guia §18–24.
- Decisão aplicável: 30/09 (6a1abfb7): "Concluir o tutorial de implantação e abrir PR".
- Spec / PRs / commits: PR #236; #271 (Unidades no guia); #281; #283 (§10.4, aberto).
- Implementação: `doc/implantacao-em-producao-ubuntu.md` (§18 backup, §19 restore, §21 monitoramento, §24 incidentes).
- Testes: 21 testes do #283 executam exemplos do guia (só na branch).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: um ensaio completo numa VM Ubuntu descartável, incluindo restauração com restic.
- Impacto: operação (primeira implantação sem ensaio).
- Prioridade: **P1 para a implantação**.
- Dependências: GO-22, GO-23.
- Próxima ação recomendada: ensaio em VM descartável seguindo só o guia, registrando desvios.
- Precisa de decisão humana? não (só disponibilidade de VM).
- Confiança: alta.

<a id="go-25"></a>
#### GO-25 — Correio: único fator de acesso do candidato, porta 465 sem suporte, falha silenciosa no código de acesso
- Descrição: o candidato entra só por código no e-mail (RC-93, I-10): SMTP fora do ar = candidato sem acesso. Falha de SMTP no envio do código vira só log, e o candidato vê a mensagem neutra. SSL implícito (465) não tem suporte (`EMAIL_USE_SSL` ausente); depende da resposta do setor de correio sobre STARTTLS na 587. E-mails de código, comprovante e convocação são síncronos na requisição.
- Origem (demanda/decisão): RC-93; I-4, I-10 do guia; P-5 da auditoria de configurações (14/10); PR #236, #281; `codigo-e-configuracao.md` §4.3.
- Decisão aplicável: 14/10 (f55c52a5): "Não trate a porta 465 isoladamente como erro"; 01/09: e-mail → código de uso único → sessão (V1 do candidato).
- Spec / PRs / commits: 010; 066 (`EMAIL_TIMEOUT`); 073 (diagnóstico, PR #283).
- Implementação: `ps/identidade/application/mensagem.py:107,136` (exceção engolida com log); `config/settings/base.py:186-197` (sem `EMAIL_USE_SSL`; `EMAIL_TIMEOUT` 20).
- Testes: testes de envio com backend locmem; nenhum de SMTP indisponível no código de acesso.
- Estado: BLOQUEADO
- Lacuna: resposta do setor de correio; SMTP institucional redundante e monitorado; decidir se a falha de envio deve aparecer ao candidato.
- Impacto: candidato (perde o prazo de inscrição se o correio cair no último dia).
- Prioridade: **P1 para a implantação**.
- Dependências: GO-22, GO-26.
- Próxima ação recomendada: enviar ao setor de correio a pergunta do checklist §25; decidir a mensagem ao candidato quando o envio falha.
- Precisa de decisão humana? sim — institucional (correio) e de produto (mensagem de falha).
- Confiança: alta.
- **Fundidos neste item:** AS-23, CA-16.
  - *AS-23 (AS), Correio (SMTP): integração real, sem validação operacional* — lacuna: resposta do setor de correio (587/STARTTLS ou 465); roteiro B; merge do #283. Próxima ação: perguntar ao setor de correio (checklist §25 do guia) e, com a resposta, rodar o roteiro B em homologação. - Precisa de decisão humana? sim — merge do #283 (do usuário) e quem da TI faz o roteiro B.
  - *CA-16 (CA), O acesso do candidato depende só do e-mail, e a falha de envio é silenciosa* — lacuna: sem métrica ou alerta de falha de envio do código, sem verificação periódica do correio fora da 073 e sem caminho alternativo de acesso. Próxima ação: incluir na verificação da 073, ou num timer, um alerta para falhas consecutivas de `send_mail` do código, sem quebrar a equivalência de resposta. - Precisa de decisão humana? não, para o alerta; sim, se quiser canal alternativo de acesso.
- **Prioridade elevada a P0** pela perspectiva de AS-23.

<a id="go-26"></a>
#### GO-26 — PR #283 (implementação da 073) aberto, "CONFLICTING" no GitHub, sem revisão
- Descrição: a 073 (§10.4 do guia, recusa de SMTP com `EMAIL_HOST` vazio, "serviço desconhecido" no verificador, 21 testes) está só na branch `claude/073-configurar-e-verificar`. O GitHub marca `CONFLICTING`/`DIRTY`; `git merge-tree` local contra `origin/main` (`db428b30`) sai limpo. CI verde é de antes dos merges do #281/#282. Na `main`, a 073 é só `spec.md` ("Sem plano nem tarefas"), e o README diz "especificada".
- Origem (demanda/decisão): L10-43 (14/10); X-04, S-073-01; c.14 P-4, P-6, P-11, P-12; `github.md` §4.
- Decisão aplicável: 14/10 (f55c52a5): "Aprovo o recorte da 073"; ordem de merge #281→#282→#283; estado "implementada, com validação operacional pendente".
- Spec / PRs / commits: PR #283 (`20ec4daf`, 7 commits à frente).
- Implementação: só na branch (conferido: `gh pr view 283` → OPEN, CONFLICTING, reviewDecision vazio).
- Testes: 21 testes novos na branch; suíte da branch 11294/12.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: atualizar a branch com a `main`, CI verde sobre o commit atualizado, merge (do usuário).
- Impacto: operação (o guia da `main` não tem o procedimento de correio/Ollama).
- Prioridade: P2 — não há implantação; o risco é a branch envelhecer.
- Dependências: GO-27.
- Próxima ação recomendada: sincronizar com a `main`, conferir o CI e levar ao usuário para merge.
- Precisa de decisão humana? sim — o merge é do usuário.
- Confiança: alta.

<a id="go-27"></a>
#### GO-27 — Validação operacional da 073: roteiros B (TI em homologação) e C (Ollama na L4)
- Descrição: SC-620/SC-623 pedem que uma pessoa da TI que não participou siga só a §10.4 em homologação (≤30 min, e-mail fora do spam); a US2 pede verificar o Ollama real na L4 (versão, modelo, inferência, `tokenizers`/`tokenizer.json`). Nenhum ambiente de homologação existe e não há acesso de rede à L4.
- Origem (demanda/decisão): L10-44, L10-45 (14/10); S-073-02, S-073-03; PR #283 `verificacao.md:52-56`.
- Decisão aplicável: 14/10 (f55c52a5) — roteiros B e C definidos; "Não execute envios reais nem inferências pagas sem autorização específica".
- Spec / PRs / commits: 073 (PR #283).
- Implementação: procedimento escrito (só na branch).
- Testes: n/a (validação humana).
- Estado: BLOQUEADO
- Lacuna: homologação e acesso à L4.
- Impacto: operação.
- Prioridade: P2 — só tem sentido junto da implantação.
- Dependências: GO-22, GO-24, GO-26; acesso à L4 (mesmo bloqueio da 071 T058–T060).
- Próxima ação recomendada: agendar junto do ensaio em VM (GO-24).
- Precisa de decisão humana? sim — quem da TI e quando.
- Confiança: alta.

<a id="go-28"></a>
#### GO-28 — A release do guia não instala o grupo `assistente` (`tokenizers`)
- Descrição: o `ps-construir` roda `uv sync` sem `--extra assistente`; numa máquina construída pelo guia, ligar o piloto faz toda pergunta terminar em `SEM_TOKENIZER`. Três opções registradas (A sempre com o grupo; B por variável; C só o aviso), e duas perguntas: em que máquina roda o piloto, quem mantém o `tokenizer.json`.
- Origem (demanda/decisão): L10-46 (14/10); S-071-11, S-073-04; `doc/achado-release-sem-o-grupo-do-assistente.md` (só na branch do #283).
- Decisão aplicável: nenhuma ("não vira escopo por estar escrito aqui").
- Spec / PRs / commits: 071, 073.
- Implementação: guia §8.3 (`ps-construir` sem o grupo); `backend/pyproject.toml:34-36` (grupo opcional).
- Testes: `tests/unit/duvidas/test_tokens.py:31` pula sem a biblioteca.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: escolha A/B/C.
- Impacto: equipe do piloto do assistente.
- Prioridade: P3 — sem efeito hoje (piloto roda na máquina da equipe; produção com `ASSISTENTE_PILOTO=false`).
- Dependências: GO-26.
- Próxima ação recomendada: decidir junto com o merge do #283.
- Precisa de decisão humana? sim — A, B ou C.
- Confiança: alta.
- **Fundidos neste item:** AS-19.
  - *AS-19 (AS), Release de produção não instala a biblioteca do tokenizer* — lacuna: escolher A/B/C; responder se o piloto roda numa máquina do guia e quem mantém o `tokenizer.json`. Próxima ação: decidir ao mergear o #283; a opção A é uma linha no guia. - Precisa de decisão humana? sim — A/B/C.

<a id="go-29"></a>
#### GO-29 — Base de CEP: job mensal e alerta só como receita; runbook contradiz o Makefile
- Descrição: o usuário decidiu que a base de CEP só é "pronta para produção" com job mensal agendado e alerta de falha/desatualização; existem os comandos (`carregar_ceps --se-mudou`, `situacao_dos_ceps`), mas o agendamento (`ps-ceps`) e o canal de alerta existem só no guia. O runbook manda "recarregar ignorando o resumo igual" com `make ceps`, mas o alvo sempre passa `--se-mudou`. O `seed_demo` não carrega CEP (demonstração só do caminho degradado).
- Origem (demanda/decisão): L07-08, L07-09 (16/09); PR #123; inventário documental §1.3 e (i).
- Decisão aplicável: 16/09 (8f427c86): "carga inicial no provisionamento e atualização por job agendado. Nem recarregar em todo deploy, nem depender de execução manual." e "deve existir o job mensal e o alerta de falha/desatualização."
- Spec / PRs / commits: 029 (#123); `doc/runbook-base-de-cep.md`.
- Implementação: `ps/requerimentos/management/commands/carregar_ceps.py:56`, `situacao_dos_ceps.py:33`; `backend/Makefile:93` (`--se-mudou` sempre); guia `:2172-2190`.
- Testes: testes dos comandos (029).
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: timer versionado (GO-23), canal de alerta, correção do runbook.
- Impacto: candidato (endereço sem preenchimento automático); operação.
- Prioridade: P2 — degradação graciosa existe.
- Dependências: GO-23, GO-24.
- Próxima ação recomendada: corrigir o runbook já; o timer entra no empacotamento de produção.
- Precisa de decisão humana? não.
- Confiança: alta.
- **Fundidos neste item:** AS-25, AV-32.
  - *AS-25 (AS), Base de CEP: carga local, atualização mensal só como receita* — lacuna: ensaio da receita numa VM; revisão do runbook; amostra de CEP no seed (opcional, "se valer a pena"). Próxima ação: incluir o `ps-ceps` no roteiro B de homologação. - Precisa de decisão humana? não.
  - *AV-32 (AV), Base de CEP sem job mensal nem alerta* — lacuna: timer versionado e alerta. Próxima ação: versionar o timer junto com os demais da implantação. - Precisa de decisão humana? não.

<a id="go-30"></a>
#### GO-30 — SLO de carga e escala nunca medidos
- Descrição: o SLO público (p95 ≤ 2 s a 500 consultas/s) nunca foi medido em ambiente implantado; o harness `scripts/carga_publica.py` existe. Escala da instituição (2719 vagas, RC-96) e consolidação de 10 000 (4,33 s, laptop) sem teto; workers síncronos de até 120 s; sem limite genérico de requisições, cache ou fila para abertura pública.
- Origem (demanda/decisão): L01-09 (28/08), L05-42 (12/09), L10-10 (12/10); I-8 do guia; RC-96; PR #3, #236.
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 001 (SLO); 071 D-008 (teto global do assistente).
- Implementação: `backend/scripts/carga_publica.py`, `carga_do_assistente.py`.
- Testes: `tests/performance/` (orçamentos de consulta, não carga).
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: medição em homologação; dimensionamento de workers.
- Impacto: candidato (último dia de inscrições); operação.
- Prioridade: P2 — sobe a P1 antes da primeira abertura pública.
- Dependências: GO-24.
- Próxima ação recomendada: rodar o harness no ensaio em VM.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="go-31"></a>
#### GO-31 — Teste operacional assistido (DP-18) nunca realizado; usabilidade da gestão nunca medida com servidores
- Descrição: o roteiro do teste operacional (o 28/2026 composto por uma pessoa do setor) foi escrito e ensaiado pelo agente em 27/09; quem faz e quando nunca foi decidido; não existe documento de resultado. A regra "quando a pessoa travar" (ajuda mínima após 10 min) foi proposta sem decisão. O roteiro envelheceu (não conta com 060, 066, 069; diz "34 de 34" tabelas, hoje 40). Na mesma linha, os SC-001/002/008 da 002 (15 min, 90 % na primeira tentativa) nunca foram medidos com servidores do Cefor (T059).
- Origem (demanda/decisão): DP-18; L08-19, L08-20 (27/09); L01-26 (28/08); S-002-07; `specs/051-*/spec.md:551`; AUD l.369 (dá o passo 0,5 como feito "em ensaio" — contradição); PR #199, #208.
- Decisão aplicável: nenhuma sobre quem/quando ("Quem: a decidir", DP:1110).
- Spec / PRs / commits: `doc/roteiro-teste-operacional-assistido-28-2026.md`; 002 T059.
- Implementação: roteiro pronto; banco `ps_teste_operacional_28` deixado.
- Testes: n/a (validação humana).
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: execução com pessoa do setor; atualização do roteiro.
- Impacto: equipe de seleção (nenhuma evidência de que consegue montar um Edital real sozinha).
- Prioridade: P1 — é a única validação da jornada principal com o ator real, e várias decisões (GO-07, GO-13) esperam por ela.
- Dependências: nenhuma técnica (roda no ambiente local).
- Próxima ação recomendada: decidir quem e quando; atualizar o roteiro para a `main` atual antes.
- Precisa de decisão humana? sim — DP-18.
- Confiança: alta.
- **Fundidos neste item:** AV-08, ED-01.
  - *AV-08 (AV), Ciclo de condução sem validação com as pessoas que vão operá-lo* — lacuna: percurso conduzido com o setor; banco de demonstração com documentos e cotas. Próxima ação: roteiro de ensaio da condução (análogo ao roteiro do 28/2026), com seed que anexe documentos. - Precisa de decisão humana? sim — quem conduz o ensaio e quando.
  - *ED-01 (ED), A elaboração nunca foi validada por quem elabora* — lacuna: nenhum documento de resultado de teste com pessoa do setor; `specs/002/tasks.md` T059 aberta; `specs/044/tasks.md:234` T065 aberta; DP-18 sem decisão de quem/quando. Próxima ação: decidir DP-18 (pessoa e data); rodar o roteiro do 28/2026 com datas futuras e registrar resultado; aproveitar para medir T059 e recompor o 140/2025 (T065). - Precisa de decisão humana? sim — quem conduz, quem participa e quando (DP-18); regra de ajuda quando a pessoa trava (L08-20).

<a id="go-32"></a>
#### GO-32 — Repositório sem proteção de branch e sem revisão; CI sem varredura de segurança nem agendamento
- Descrição: `main` sem proteção (`gh api .../branches/main/protection` → 404; rulesets `[]`); nenhum comentário de revisão nem review formal em 282 PRs; o pedido de revisão a `@vitofranzosi` no #2 nunca teve resposta; `gh pr merge --auto` mescla sem esperar CI (incidente #83 citado várias vezes); `/code-review ultra` da 017 era portão e nunca foi informado. O CI (`backend.yml`) roda só em `push` na `main` e `pull_request`, sem `schedule`, sem auditoria de dependências nem SAST. Política de merge (merge commit × squash) nunca fixada.
- Origem (demanda/decisão): L01-76, L01-77 (30/08), L03-01, L03-18, L03-28 (02–06/09), L04-24 (08/09), L08-81 (30/09); `github.md` §2, §8; memória "Merge de PR é do usuário".
- Decisão aplicável: 29/08 (75d0dcc9): "Use Create a merge commit. Não use squash nem rebase." (para #3–#7); merge é sempre do usuário.
- Spec / PRs / commits: `.github/workflows/backend.yml:10-24`.
- Implementação: n/a (configuração do GitHub).
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: checks `test` e `compose` obrigatórios; job agendado (E2E da Caixa, GO-33; data UTC, GO-35); auditoria de dependências.
- Impacto: operação/qualidade (regressão pode chegar à `main` sem CI).
- Prioridade: P2 — o mantenedor é quase único; tornar os checks obrigatórios custa minutos.
- Dependências: GO-33.
- Próxima ação recomendada: ativar checks obrigatórios na `main`; acrescentar `schedule` semanal e `pip-audit`/equivalente.
- Precisa de decisão humana? sim — configuração do repositório é do usuário/dono (`vitofranzosi`).
- Confiança: média — o 404 da API de proteção pode ser falta de permissão do token; rulesets vazio reforça.

<a id="go-34"></a>
#### GO-34 — `make test` (modo SQLite) continua vermelho
- Descrição: sem `TEST_DB_ENGINE=postgresql`, a suíte cai para SQLite e falha (35 falhas, ~8087 passando, 253 pulados, 1 erro em 28/09; total não reprodutível). O alvo `test` continua no Makefile; três caminhos (pular corretamente, remover o modo, documentar) sem escolha. Mitigado só por documentação.
- Origem (demanda/decisão): achado 40; L04-53 (09/09), L02-12, L02-25, L06-44, L05-27; RC-103; L08-55.
- Decisão aplicável: 06/09 (c63d1b5a): "marque as 7 como PostgreSQL-only" (pontual); 28/09: investigar a subida de pulados (feito).
- Spec / PRs / commits: `doc/achado-suite-em-sqlite.md` (números vencidos); AGENTS.md.
- Implementação: `backend/Makefile:33-34` (`test`) e `:43-46` (`test-pg`).
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: escolha de um dos três caminhos.
- Impacto: desenvolvedor novo (comando óbvio dá vermelho).
- Prioridade: P3.
- Dependências: nenhuma.
- Próxima ação recomendada: decidir remover o modo SQLite (ou fazer `test` apontar para `test-pg`).
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="go-35"></a>
#### GO-35 — Instabilidades e armadilhas conhecidas da suíte
- Descrição: (a) RC-160: um erro único de `no_effective_version` em `test_documento.py` (hipótese: relógio recuando; três saídas, nenhuma escolhida); (b) classe de teste com data em UTC sem guarda (achado 41; 7 `.astimezone()` sem argumento); (c) `tests/performance/test_ocupacao.py` (milissegundos) falhou 1 vez em 11 095 (L10-40); (d) `test_database_permissions.py` erra em bloco com outra suíte no mesmo cluster (papéis `ps_*_conformance` globais; `DB_NAME` próprio não isola); (e) o `include .env` + `export` do Makefile vaza o `.env` para `make test-pg` (dois testes corrigidos, causa de pé); (f) worktree sem `backend/.env` quebra `make check`.
- Origem (demanda/decisão): RC-160, AUD §13 item 28; achado 41, achado 43; L04-110, L08-73 (29/09), L10-40, L10-41 (13/10), L02-34, L08-49, L04-69, L05-05.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: `doc/achado-teste-com-data-em-utc.md`, `doc/achado-versao-vigente-intermitente-no-test-documento.md`.
- Implementação: `ps/publicacoes/application/selectors.py:28-42` (sem tolerância); `backend/Makefile:9-14`.
- Testes: os próprios.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão por item; nenhuma recorrência registrada de (a) depois de 29/09; a rodada de 15/10 passou limpa (11297/11).
- Impacto: desenvolvimento (falso vermelho, tempo perdido).
- Prioridade: P3.
- Dependências: GO-32 (job noturno revelaria (b)).
- Próxima ação recomendada: registrar recorrências; tratar (b) com varredura simples de `strftime`/`astimezone()` sem fuso.
- Precisa de decisão humana? sim — RC-160 (três saídas).
- Confiança: média — intermitências, por natureza, sem reprodução.

<a id="go-36"></a>
#### GO-36 — Casos-limite das specs fora da matriz de requisitos
- Descrição: as seções *Edge Cases* (~300 itens em 001–037) quase nunca citam FR/SC; só 14 specs de 038–073 levam casos-limite à `rastreabilidade.md`; nenhum teste cobra a correspondência. A 038 já teve dois casos-limite escritos e não cumpridos (`32cd6d9b`).
- Origem (demanda/decisão): T-3; X-06; memória "Casos-limite são requisitos".
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: `specs/*/spec.md` (Edge Cases); `tests/test_citacoes_de_requisito.py` (não lê casos-limite).
- Implementação: n/a.
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: regra de rastreio (casos com consequência viram FR, como 040/055–058/066 já fazem).
- Impacto: qualidade (comportamento prometido sem verificação).
- Prioridade: P2.
- Dependências: GO-38.
- Próxima ação recomendada: adotar a regra das specs 040/066 no template ("casos-limite com consequência também estão nos FR").
- Precisa de decisão humana? sim — governança.
- Confiança: alta.

<a id="go-37"></a>
#### GO-37 — Limitações do guardião de citações
- Descrição: `tests/test_citacoes_de_requisito.py` verifica que o ID existe, mas não detecta o mesmo FR/SC/UX definido em duas specs (L07-18), não verifica que um requisito substituído foi anotado como revogado (L07-19) e conta qualquer identificador em negrito como definição (L06-30; UX-062 da 037 passou só reservado).
- Origem (demanda/decisão): L06-30 (~19/09), L07-18, L07-19 (16–21/09); L08-55.
- Decisão aplicável: nenhuma.
- Spec / PRs / commits: memória "Faixa de FR- passou a ser global", "Decisão de spec é título".
- Implementação: `backend/tests/test_citacoes_de_requisito.py`.
- Testes: o próprio.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: três verificações.
- Impacto: governança de specs.
- Prioridade: P3.
- Dependências: nenhuma.
- Próxima ação recomendada: acrescentar a verificação de definição duplicada (a mais barata e a que já custou retrabalho).
- Precisa de decisão humana? não.
- Confiança: média — comportamento descrito pelas sessões, não reexecutado.

<a id="go-38"></a>
#### GO-38 — Campo `Status` das specs (DP-12) e validações humanas sem registro central
- Descrição: 63 das 74 `spec.md` dizem `Draft`, inclusive specs mergeadas (060, 062, 063, 066, 069–072); a 064 diz "aguardando o merge da 063"; a 038 tem 0/22 tarefas marcadas, embora implementada; o template continua criando `Draft`. Consequência: não há lugar único que diga quais specs estão implementadas com validação humana pendente (070 T046; 071 T058–T060/T065; 072 SC-605/FR-1627; 069 SC-517; 073 SC-620; 044 T065; 002 T053–T059; 031 SC-143).
- Origem (demanda/decisão): DP-12; RC-103; T-1, X-01, X-02, X-07; L06-31 (~19/09), L08-31, L08-55; d.1 item 7.
- Decisão aplicável: nenhuma (DP:539-559 sem bloco de decisão). A metade "README conferido por teste" foi feita (`tests/test_readme_acompanha_o_codigo.py`, `325b57d4`).
- Spec / PRs / commits: `.specify/templates/spec-template.md:7`; README (tabela 001–073).
- Implementação: n/a.
- Testes: `tests/test_readme_acompanha_o_codigo.py`.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decidir abolir o campo ou mantê-lo atualizado; registro das validações humanas pendentes.
- Impacto: quem governa o backlog; avaliador externo do projeto.
- Prioridade: P2 — induz a erro de estado em toda leitura das specs.
- Dependências: GO-41.
- Próxima ação recomendada: decidir a DP-12; se abolido, acrescentar ao README uma coluna "validação pendente".
- Precisa de decisão humana? sim — DP-12.
- Confiança: alta (contagem por grep em 15/10).

<a id="go-40"></a>
#### GO-40 — Decisões de produto da consolidação de 26/09 sem registro (DP-09, DP-10, DP-11, DP-15)
- Descrição: quatro DPs abertas sem bloco de decisão: DP-09 (D-011, sem prova nova no recurso — status quo), DP-10 (famílias de Edital no alvo: barema, heteroidentificação, cascata, submodalidades — RC-55/59/64/65), DP-11 (comissão local por Perfil/polo — RC-61), DP-15 (documento público por marco — a 049 seguiu a opção A sem registro). O conteúdo pertence a outras áreas; aqui fica a pendência de governança.
- Origem (demanda/decisão): DP-09/10/11/15; AUD §13 itens 10, 11, 13; L08-31 (26/09); `doc/manual/00-arquitetura-do-manual.md:1956-1960`.
- Decisão aplicável: nenhuma registrada; ~19/09: "generalizar, não particularizar" (princípio de produto).
- Spec / PRs / commits: `doc/decisoes-pendentes-da-consolidacao.md:460-535, 987-999`; 049 `spec.md:425,437`.
- Implementação: n/a.
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: registro da decisão (ou de que vale o status quo).
- Impacto: conforme o tema (julgador, avaliador, presidência, candidato).
- Prioridade: P3 — o status quo funciona para o piloto; formalizar evita rediscussão.
- Dependências: GO-31 (o teste operacional informa DP-11/DP-15).
- Próxima ação recomendada: registrar "vale o status quo" na DP-09 e DP-15; deixar DP-10/DP-11 para depois do piloto.
- Precisa de decisão humana? sim.
- Confiança: alta.

<a id="go-41"></a>
#### GO-41 — Specs e documentos de consolidação atrás das decisões já tomadas
- Descrição: `decisoes-pendentes-da-consolidacao.md` e `auditoria-de-consolidacao-2026-09-26.md` param em 29/09 (nenhum PR do #233 ao #282 reconciliado: a 054 ainda "em curso"; a 039 "nunca mesclada"; DP-21 com banner × introdução contraditórios; cabeçalho omite DP-19/DP-20; DP-07 sem bloco; 33 × 34 tabelas, hoje 40). Emendas decididas e não escritas: SC-273 da 045 (RC-127, `doc/decisao-sc273-estreitada.md`); G-010 da 040 decidida e listada como pendente. Sync Impact Report da Constituição 1.2.0 diz DP-16 "em aberto" e TF-1 "não entregue". Achados com estado vencido sem nota: 12, 22 (e docstrings), 25, 29, 30 (rodapé), 20 e 40 (números), 42. §9 da auditoria do assistente e §10 da auditoria de UX (Q1–Q9 já decididas).
- Origem (demanda/decisão): `doc-achados-e-auditorias.md` (b) "Contradições", d.1–d.6; L08-38 (26/09), L08-55 (28/09).
- Decisão aplicável: 28/09 — SC-273 estreitada (decidida, não escrita).
- Spec / PRs / commits: `specs/045-*/spec.md:378`; `.specify/memory/constitution.md:42,56-58`.
- Implementação: n/a.
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: notas de atualização datadas; emenda da SC-273.
- Impacto: quem decide (risco de decidir de novo o que já foi decidido).
- Prioridade: P2.
- Dependências: GO-38.
- Próxima ação recomendada: um PR só de documentação com notas datadas nos documentos de 26–29/09 e nos achados vencidos, mais a emenda da SC-273 (cuidando do guardião de citações).
- Precisa de decisão humana? não (decisões já tomadas); sim para o merge.
- Confiança: alta.

<a id="go-42"></a>
#### GO-42 — Contradições na documentação de operação e de desenvolvimento
- Descrição: (1) `PORTAL_IDENTIDADE_DEMO` é vestigial — nenhum fluxo a lê, `provedor_de_demonstracao()` não tem chamador, mas `AGENTS.md:137` e `backend/.env.example:52` dizem que o portal precisa dela; (2) `AGENTS.md:115` "hoje são 90" migrations — são 94; (3) "o par `TEST_DB_ENGINE` + `DB_USER`" (`AGENTS.md:110`, `README.md:289-294`) × `Makefile:41-46` e `base.py:345-346` (`DB_RUNTIME_USER` tem precedência); (4) números da suíte no AGENTS (11263/12, 14/10) × 11297/11 medidos em 15/10; (5) guia de implantação: "três fluxos" × tabela de quatro (`:1554`), "os únicos jobs são manutenção e backup" × `ps-avisos` (`:99-101`), go-live sem `ps-avisos` (`:2842`), lista de comandos do B-2 sem os três da `duvidas` (`:2529`), referência `views.py:606-610` (hoje `:626-629`), outras linhas envelhecidas (#281); (6) runbook de CEP × `Makefile:93` (GO-29); (7) roteiro DP-18 "34 de 34" (hoje 40); (8) quickstart da 066 manda desligar avisos pela variável, mas `development.py:11` força `True`; (9) `.env.example:39-41` × uso de `POSTGRES_*` na execução nativa; (10) LEIA-ME das ferramentas do manual aponta porta 8033 e entrada inexistente; (11) docstring de `ps/divulgacao/application/publicar.py:317-318` ("degrau 8 não existe") × uso de `janela_do_ato`.
- Origem (demanda/decisão): `codigo-e-configuracao.md` "Divergências"; `inventario-documental.md` §5 (a)–(r); L04-57, L07-50, L09-12 (01/10), L09-77; PR #281.
- Decisão aplicável: nenhuma específica; convenção "AGENTS.md é a fonte dos números".
- Spec / PRs / commits: AGENTS.md, README.md, `.env.example`, guia, runbook, quickstart 066.
- Implementação: `ps/portal/identidade.py:127-134` (código morto); `config/settings/production.py:104-109` (única leitura da chave).
- Testes: `tests/test_readme_acompanha_o_codigo.py` (só a tabela de incrementos).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: correções pontuais; remover a chave vestigial (ou documentá-la como armadilha).
- Impacto: desenvolvedor/agente novo, operação (seguir instrução errada).
- Prioridade: P2 — o AGENTS.md é lido por todo agente; instruções erradas custam sessões.
- Dependências: nenhuma.
- Próxima ação recomendada: um PR de documentação com as onze correções; decidir se remove `PORTAL_IDENTIDADE_DEMO` e `provedor_de_demonstracao`.
- Precisa de decisão humana? sim — remover a chave vestigial (mexe em `production.py`).
- Confiança: alta.
- **Fundidos neste item:** AS-21, CA-36.
  - *AS-21 (AS), Documentação do assistente desatualizada e branches residuais* — lacuna: atualizar os trechos; apagar as branches, a critério do usuário. Próxima ação: um PR só de documentação (rodar a suíte por causa de `test_citacoes_de_requisito.py`). - Precisa de decisão humana? sim — apagar as branches.
  - *CA-36 (CA), Documentação desatualizada sobre o portal e os avisos* — lacuna: documentação diverge do código. Próxima ação: corrigir (a) e (b) num PR de documentação. (c) entra na próxima sessão do manual. - Precisa de decisão humana? não.

<a id="go-43"></a>
#### GO-43 — Manual planejado e não produzido desde 08/09
- Descrição: existe a arquitetura (Revisão 5, 06/10, sobre `4602b04`, cobre 019–058) e o piloto editorial S-00 (08/09: 3 páginas e 1 espécime, 12 capturas, todos vencidos). Da S-00R só a metade documental foi feita; itens 2–5 a fazer; S-01 a S-19 não iniciadas; zero das 89 capturas definitivas. Não há capítulo para 060 (autoridades), 066 (avisos e modelos), 069, 070/071, 072; o manual conta 7 papéis (são 8) e ignora `autoridade:gerir` e `aviso:enviar`; diz que nenhum candidato é notificado e que o portal não leva à convocação (ambos superados). Não há registro de aprovação do piloto S-00 (gate da S-01), nem decisão sobre publicação (hospedagem, PDF, impresso) nem sobre a relação com a Visão do Sistema. O login da gestão não é documentável enquanto GO-01 não existir.
- Origem (demanda/decisão): L04-40, L04-41, L04-43, L04-44, L04-45 (08/09), L04-36; L09-19, L09-20 (06/10); PR #250, #251; `inventario-documental.md` §2, §3, §5 (a)–(h).
- Decisão aplicável: 08/09 (268367ba): piloto editorial antes do acervo, gate S-00 → S-01; separar operacional × referência; manter personagens; equipe 2–3; arquitetura aprovada "com quatro ajustes de direção"; 06/10 (6ef6d5ee): PR só com a R5, "manual e S-00R ficam para a próxima sessão".
- Spec / PRs / commits: `doc/manual/00-arquitetura-do-manual.md`, `01-inventario-de-capturas-revisado.md`, `doc/manual/piloto/` (`f46687af`).
- Implementação: só o piloto.
- Testes: nenhum.
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: reconciliação 059–073, aprovação do S-00, produção S-01..S-19, decisão de formato/publicação.
- Impacto: equipe de seleção, avaliador, julgador, candidato (sem material de uso).
- Prioridade: P2 — a Visão do Sistema cobre parte; antes da implantação sobe a P1 (capacitação).
- Dependências: GO-01 (C-02/login), GO-44 (redundância), GO-07 (C-04).
- Próxima ação recomendada: decidir a relação manual × Visão do Sistema antes de produzir; depois, S-00R e R6 (059–073).
- Precisa de decisão humana? sim — aprovação do S-00 e relação com a Visão do Sistema.
- Confiança: alta.

<a id="go-44"></a>
#### GO-44 — Visão do Sistema: atrás da `main`, atualização em curso não commitada, sem ligação nem guarda
- Descrição: `docs/visao-sistema/index.html` (≈1 MB) na `main` descreve até a 068 (`cf7e7f68`, 10/10): zero menções a 069–073 e ao papel do piloto. Nesta worktree há uma atualização **não commitada** (+178/−40, "specs 069–072 acrescentadas em 15/10", aviso "O sistema não está em produção"). Não é linkada no README nem no AGENTS.md (explica o envelhecimento silencioso); itens marcados "[a validar]"; nenhum teste a lê; redundante em parte com o manual planejado (tutorial, papéis, FAQ nos dois).
- Origem (demanda/decisão): L08-78, L08-80 (30/09), L09-77, L09-78 (10/10); `inventario-documental.md` §1.4; `git status` desta worktree (15/10).
- Decisão aplicável: 30/09 (7f415158): conferir no código, marcar "[a validar]" o não reproduzido, PR sem merge; 10/10 (f5a8f73b): revisar até a 068 e mergear se o CI passar.
- Spec / PRs / commits: #235, #239, #272.
- Implementação: `docs/visao-sistema/index.html` (+ `CHANGELOG-2026-09.md`, `CHANGELOG-2026-10.md`).
- Testes: nenhum.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: commit/PR da atualização em curso; link no README/AGENTS; destino dos "[a validar]".
- Impacto: servidores e gestão que a usam como material de uso.
- Prioridade: P2.
- Dependências: GO-43.
- Próxima ação recomendada: concluir e propor PR da atualização desta worktree; acrescentar o link no README.
- Precisa de decisão humana? sim — merge, e a relação com o manual.
- Confiança: alta.

<a id="go-45"></a>
#### GO-45 — Documentos de operação institucional ausentes
- Descrição: além do aviso de privacidade (GO-20), da política de retenção (GO-19) e do guia de acessos (GO-05), não existem: procedimento do atendimento (o canal `PORTAL_ATENDIMENTO`; o manual afirma que o CPF passa a ser corrigido "só pelo atendimento" e não há tela nem procedimento); plano de incidente com dado pessoal (papéis, prazos, comunicação à ANPD e aos titulares — o guia tem um parágrafo, `:2440-2448`); contingência do certame (correio fora do ar no último dia, erro em Edital publicado, julgador impedido — previstos como X-01..X-13 do manual); plano de capacitação.
- Origem (demanda/decisão): `inventario-documental.md` §4; L10-51 (14/10: "alguém espera respostas a e-mails do sistema?").
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: `doc/manual/00-arquitetura-do-manual.md:419` (CPF pelo atendimento).
- Implementação: inexistente.
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: os quatro documentos.
- Impacto: equipe de seleção; candidato (atendimento); instituição (incidente).
- Prioridade: P2 — sobe a P1 antes da primeira abertura real.
- Dependências: GO-19, GO-20, GO-25, GO-43.
- Próxima ação recomendada: começar pelo procedimento do atendimento e pela contingência do último dia de inscrições.
- Precisa de decisão humana? sim — quem atende e com que poderes.
- Confiança: alta.

<a id="go-46"></a>
#### GO-46 — Spec 074 (assistente na página do Edital, só local) existe só numa worktree, sem commit
- Descrição: a 074 — spec, plano, tarefas (13/14), quickstart, rastreabilidade, código (`portal/assistente.py`, `interface/painel_do_assistente.py`) e testes — está na worktree `assistente-pagina-edital-local-d6f44f`, branch sobre `bc6dd96b`, com 15 arquivos modificados (inclui `specs/071-*/spec.md`, settings, README, AGENTS) e 5 caminhos não rastreados. Nenhum commit, nenhuma branch remota. A emenda do FR-1462 da 071 ("nenhuma rota pública") também só existe lá. A branch está atrás da `main` (sem #281/#282).
- Origem (demanda/decisão): X-05, S-074-01/02, S-071-10; lote 10 (e76c2efd, 14/10); `git -C .claude/worktrees/assistente-pagina-edital-local-d6f44f status` (15/10).
- Decisão aplicável: 14/10 (e76c2efd): "o sistema existe apenas no meu computador"; assistente na página real, sem condicionar a B-1/073/L4; "Corrija os oito achados da revisão" (feito).
- Spec / PRs / commits: nenhum.
- Implementação: só na worktree (chave `ASSISTENTE_NA_PAGINA_DO_EDITAL`, recusada em produção).
- Testes: `backend/tests/portal/test_assistente_na_pagina.py` (não rastreado); suíte completa não repetida depois do review (L10-62: 4901 afetados passaram).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: commit e PR; T013 (pergunta livre com modelo real, custo OpenRouter); suíte completa.
- Impacto: equipe do piloto; o próprio trabalho (perda total se a worktree for removida com `--force`).
- Prioridade: P1 — risco de perda irreversível de trabalho concluído, com custo baixo para afastar.
- Dependências: nenhuma.
- Próxima ação recomendada: commitar na branch da worktree e empurrar (sem merge), sincronizar com a `main`, rodar a suíte completa; o merge é do usuário.
- Precisa de decisão humana? sim — autorizar o commit/push e decidir o merge.
- Confiança: alta.
- **Fundidos neste item:** AS-12.
  - *AS-12 (AS), 074 (assistente na página pública, só local) sem commit nem PR* — lacuna: commit/PR; atualizar com a `main` (há #281/#282 desde a base); suíte completa; T013 pelo usuário; cuidado com o `launch.json` versionado (memória: não sobrescrever a entrada do usuário). Próxima ação: responder à pergunta pendente; se sim, atualizar com a `main`, rodar `make lint check test-pg` com `DB_NAME` próprio, commitar sem a mudança do `launch.json` (ou só acrescentando a entrada) e abrir PR. - Precisa de decisão humana? sim — autorizar commit/PR e fazer a T013.

<a id="go-47"></a>
#### GO-47 — Vídeos de lançamento e institucional fora do controle de versão
- Descrição: duas produções paralelas, sem commit e sem cópia fora das worktrees: `filme-de-lancamento/` (2,1 GB, worktree `ifes-launch-film-cabb9f`, trilha nunca ouvida, `ROTEIRO.md` não rastreado) e `video/` (19 GB, worktree `processo-seletivo-video-519ad6`, locução sintética só como guia, marca oficial Ifes/Cefor na cena 23 pendente). Os bancos `ps_filme`/`ps_video` têm atos irreversíveis de filmagem.
- Origem (demanda/decisão): L10-64, L10-65, L10-66 (14/10); memórias "Filme de lançamento", "Filme de apresentação"; `git status` das duas worktrees (15/10: um único `??` cada).
- Decisão aplicável: 14/10 (c2cdae9c, 3f0ce9aa): "NAO USE REMOTION"; filme de 3–5 min e vídeo institucional de 4–6 min; assistente apresentado como piloto interno.
- Spec / PRs / commits: nenhum.
- Implementação: só nas worktrees.
- Testes: n/a.
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: decidir onde guardar (git não é lugar para 21 GB; fontes e roteiros cabem); revisão humana (trilha, locução, marca).
- Impacto: comunicação institucional; o trabalho investido.
- Prioridade: P2 — perda irreversível possível; não afeta o produto.
- Dependências: nenhuma.
- Próxima ação recomendada: copiar as duas pastas para armazenamento fora das worktrees; versionar só roteiros e scripts de geração, se o usuário quiser.
- Precisa de decisão humana? sim — onde guardar e se versiona as fontes.
- Confiança: alta.
- **Fundidos neste item:** AS-28, AS-29.
  - *AS-28 (AS), Filme de lançamento (worktree `ifes-launch-film-cabb9f`)* — lacuna: **a trilha nunca foi ouvida** (níveis só por medição); destino dos arquivos (2,1 GB não cabe em commit comum). Próxima ação: ouvir antes de exibir; decidir onde guardar. - Precisa de decisão humana? sim — qual das duas produções segue e onde ficam os arquivos.
  - *AS-29 (AS), Vídeo institucional (worktree `processo-seletivo-video-519ad6`)* — lacuna: locução sintética é guia (trocar por locutor); marca oficial Ifes/Cefor na cena 23 depende de arquivo autorizado; destino dos 19 GB. Próxima ação: responder à pergunta do commit (provavelmente só fontes, sem `out/`). - Precisa de decisão humana? sim — commit, locutor, marca.

<a id="go-48"></a>
#### GO-48 — Higiene do ambiente local (worktrees, branches, bancos, `launch.json`)
- Descrição: 11 worktrees ativas, várias residuais (`audit-edital-assistant-a8f915`, `auditoria-processo-seletivo-ux-ef5de7` em detached HEAD, `stoic-tharp-c938a1`, `youthful-noether-c08b1f`, `sistema-selecao-f933f9` com `launch.json` modificado — L10-42); duas branches remotas residuais já mergeadas (`claude/piloto-ajustes-do-ensaio`, `claude/piloto-assistente-do-edital`); dezenas de bancos locais órfãos (lista em L09-18); banco de desenvolvimento `processo_seletivo` atrás das migrations e entrada do `launch.json` apontando para banco antigo (L09-97); entrada `auditoria-1015` acrescentada ao `launch.json` desta worktree (não commitada).
- Origem (demanda/decisão): L02-26, L03-27, L04-55, L04-92, L04-107, L05-24, L06-43, L07-75, L09-18, L09-87, L09-97, L10-42; `github.md` §6; `git worktree list` (15/10).
- Decisão aplicável: 10/09 (9e4870fe) e 11/09 (67bf3671): limpezas pontuais autorizadas; memória "Apagar a própria worktree", "Arquivar sessão não remove a worktree".
- Spec / PRs / commits: n/a.
- Implementação: n/a.
- Testes: n/a.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: faxina autorizada.
- Impacto: desenvolvimento (disco, confusão de porta/banco — memória "Servidor local roda de worktree").
- Prioridade: P3 — mas **não** remover `assistente-pagina-edital-local-d6f44f`, `ifes-launch-film-cabb9f` nem `processo-seletivo-video-519ad6` antes de GO-46/GO-47.
- Dependências: GO-46, GO-47, GO-26 (a worktree `auditoria-configuracoes-sistema-cc4664` está na branch do #283).
- Próxima ação recomendada: listar e pedir autorização item a item; atualizar o banco de desenvolvimento com `make preparar`.
- Precisa de decisão humana? sim — autorização de cada remoção.
- Confiança: alta.

---


## AS — Assistente de dúvidas, integrações e evolução

<a id="as-01"></a>
#### AS-01 — Revisão institucional da Fase A com o setor de seleção (T046)
- Descrição: a 070 foi mergeada com a revisão do setor em aberto: tabela pergunta × seções (D-007), listas de termos do canal (R-011), formas da explicação, campos não mostrados, e se a P-08 deve mostrar também a seção de inscrição (57/2026 declara "não cabendo recurso" no capítulo de inscrições). O SC-538 ("uma pessoa do setor") foi demonstrado pelo agente com a identidade `gabriel.gestor`.
- Origem (demanda/decisão): sessão 84c96e5f (12/10) — L10-01, L10-13, L10-15; PR #274; spec 070 T046, verificacao §3 e §7; S-070-01, S-070-02; doc-achados c.12 (T046 "AGUARDA AÇÃO HUMANA").
- Decisão aplicável: usuário, 12/10 (84c96e5f): *"Não marque a revisão institucional como concluída sem essa manifestação."*; antes, *"Vou fazer a revisão antes do merge"* — o merge ocorreu em 13/10 com a T046 aberta.
- Spec / PRs / commits: 070; #274 (`fb3d93d5`, `049353a6`).
- Implementação: `duvidas/domain/` (catalogo, respostas, explicacao, rotulos, canal); tela `interface/urls.py:44-50`.
- Testes: `tests/unit/duvidas/*`, `tests/integration/duvidas/*` (suíte verde; nenhuma validação humana).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: nenhuma manifestação do setor; SC-538 só pelo agente; P-08 × seção de inscrição sem decisão; conferência documental do agente (verificacao §7) aguarda o setor.
- Impacto: candidato (quando aberto) e equipe de seleção, que responde pelas respostas.
- Prioridade: P2 — o sistema não está implantado e o assistente não é necessário para operar uma seleção; **é P0 para a abertura pública do assistente** (portão listado na 071).
- Dependências: AS-02, AS-03, AS-06; decisão DP-6 da 071.
- Próxima ação recomendada: uma sessão curta com uma pessoa do setor sobre a §7 da verificacao da 070 (é material pronto), registrando a resposta na própria verificacao; pode ser a mesma sessão da T065 (AS-09).
- Precisa de decisão humana? sim — manifestação do setor sobre D-007, R-011 e linguagem; o usuário decide quem e quando.
- Confiança: alta — `specs/070-fonte-de-consulta-do-edital/tasks.md:454` está `[ ]` e a verificacao §3 diz "pendente, do usuário".

<a id="as-02"></a>
#### AS-02 — Detecção do canal de dúvidas erra nos Editais reais
- Descrição: rodada sobre 15 Editais reais, a detecção (`canal.py`) toma o e-mail errado nos FIC 58, 59, 77 e 78 (cláusula "Informações a respeito das inscrições… exclusivamente por e-mail" não reconhecida); dá "Fontes divergentes" em 9 dos 14 Editais com canal (heteroidentificação, Napne, secretaria, Receita etc.; "e-mail ou whatsapp" do mesmo parágrafo contado como dois canais; "atendimento especial" lido como canal); formatos de telefone não reconhecidos.
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-02, L10-03; 070 verificacao §7.1 (cinco emendas propostas); 071 DP-6; doc-achados c.12 (LAC-06).
- Decisão aplicável: DA-02, 12/10 (84c96e5f): *"Priorize o canal informado no edital. O canal configurado por implantação será alternativa"*; as emendas ao R-011 dependem do setor (DP-6: "decidir na T046").
- Spec / PRs / commits: 070 (R-011), 071 (DP-6); `049353a6` corrigiu só o encaminhamento sem canal.
- Implementação: `duvidas/domain/canal.py:23` (`TERMOS_DE_DUVIDA` ainda inclui `"atendimento"`; sem "informações a respeito"), `:25`; arquivo inalterado desde `049353a6`.
- Testes: `tests/unit/duvidas/test_canal.py` (cobre o corpus sintético, não os Editais reais).
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: as emendas 1–4 da verificacao §7.1 não foram aplicadas; o comportamento errado está no código da `main`.
- Impacto: candidato — receberia um canal oficial errado ou um "Fontes divergentes" sem motivo (hoje só na gestão, no piloto e na demonstração local).
- Prioridade: P2 — sem exposição a candidato hoje; **P0 para a abertura pública** (indicar canal errado compromete o direito de pedir esclarecimento no prazo).
- Dependências: AS-01 (T046), AS-03.
- Próxima ação recomendada: levar as quatro emendas da §7.1 ao setor na T046; aprovadas, é correção pequena em `canal.py` com os 15 Editais como casos de teste (só texto, sem dado pessoal).
- Precisa de decisão humana? sim — o setor aprova as emendas ao R-011.
- Confiança: alta — conferido no código; a medição sobre os Editais é da verificacao §7.1 e não foi refeita.

<a id="as-03"></a>
#### AS-03 — Cláusula "esclarecimentos exclusivamente por e-mail" × existência do assistente
- Descrição: 12 dos 15 Editais reais dizem que dúvidas são esclarecidas "exclusivamente" por um canal. Um assistente público na página do Edital contradiz o próprio ato, ou precisa se apresentar de modo que não seja "esclarecimento".
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-04; DA-01/DA-02 da auditoria do assistente; 070 verificacao §7.1 item 5; 071 spec ("a cláusula de exclusividade resolvida nos Editais a abrir"); doc-achados c.12 (DA-02 PARCIAL).
- Decisão aplicável: usuário, 12/10 (84c96e5f): *"deve constar como questão a resolver antes da abertura pública do assistente nos editais afetados"* — sem bloquear a preparação interna.
- Spec / PRs / commits: 070 FR-1442 (ponto para revisão por Edital); nenhuma spec resolve.
- Implementação: `canal.py` detecta e marca a exclusividade (`:59-83`); nada decide o que fazer com ela.
- Testes: `test_canal.py` (detecção).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: falta a decisão por Edital (mudar a cláusula nos Editais futuros, ou o assistente se declarar "explicação" e não "esclarecimento", ou não abrir nesses Editais).
- Impacto: equipe de seleção e instituição (coerência do ato oficial); candidato.
- Prioridade: P3 hoje — **P0 para a abertura pública**.
- Dependências: AS-04 (estatuto da resposta), AS-15 (spec da Fase C).
- Próxima ação recomendada: incluir na spec da Fase C como decisão de entrada; para os Editais novos, o setor pode ajustar a redação da cláusula.
- Precisa de decisão humana? sim — institucional (setor + área jurídica).
- Confiança: alta — dado da verificacao §7.1, decisão literal do usuário.

<a id="as-04"></a>
#### AS-04 — Estatuto da resposta e limites de responsabilidade (DA-01 / DEP-08)
- Descrição: o assistente explica; o ato é o PDF. Falta decidir o texto permanente de natureza não oficial ("não substitui o Edital nem o atendimento oficial"), quem o aprova (área jurídica) e como as três situações de falha aparecem ao candidato.
- Origem (demanda/decisão): auditoria do assistente §8 (DA-01, DEP-08); 071 ("o texto de natureza não oficial aprovado" no portão da Fase C); 074 "Pendências para a implantação" (texto definitivo); doc-achados c.12 (DA-01 "AGUARDA DECISÃO").
- Decisão aplicável: nenhuma registrada (a 070 só usa um texto provisório que acompanha as respostas).
- Spec / PRs / commits: nenhuma.
- Implementação: textos provisórios em `duvidas/domain/mensagens.py` e no template do protótipo.
- Testes: nenhum sobre o texto definitivo.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão institucional e texto aprovado.
- Impacto: instituição (responsabilidade), candidato.
- Prioridade: P3 hoje — **P0 para a abertura pública**.
- Dependências: AS-03; AS-15.
- Próxima ação recomendada: redigir uma proposta curta de aviso e de política de uso e levá-la à área jurídica junto com AS-03.
- Precisa de decisão humana? sim — jurídica/institucional.
- Confiança: alta.

<a id="as-06"></a>
#### AS-06 — Vocabulário das respostas: 070 × 069 e termos que os Editais não usam
- Descrição: a 069 reescreveu as regras em linguagem simples e a 070 ficou no vocabulário anterior (o caso mais sério: "menor valor declarado de Data de nascimento", que a 069 trocou por ambíguo); seis termos da tela não aparecem em nenhum dos 15 Editais ("vagas imediatas", "lista de concorrência", "soma ponderada", "decisória", "pontuada", "mensagem individual"); as explicações foram escritas para cartões ("está no cartão") e leem mal no painel e no histórico que vai ao modelo.
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-12, L10-14; 7bf91059 (14/10) — L10-29; 070 verificacao §7.3 e §8; auditoria do assistente §9 (Fase C, 14/10).
- Decisão aplicável: 070 verificacao §8: *"Decisão do usuário, e não ajuste silencioso"*, junto com a T046; nenhuma tomada. A 070 não pode importar as frases do compositor (FR-1434, decisão 003).
- Spec / PRs / commits: 070, 069; #280 recompôs parte das sugestões no protótipo.
- Implementação: `duvidas/domain/rotulos.py`, `duvidas/domain/explicacao.py` (inalterados desde `049353a6`).
- Testes: `tests/integration/duvidas/test_edital_no_catalogo_da_069.py` (títulos de seção da 069).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decidir a língua das respostas (a dos Editais do Cefor ou a do documento composto) e reescrever rótulos/explicações para o painel.
- Impacto: candidato (compreensão).
- Prioridade: P2 — consistência e linguagem, sem exposição hoje.
- Dependências: AS-01; AS-15 (a redação para o painel "fica para a spec da Fase C").
- Próxima ação recomendada: decidir junto com a T046; aplicar só em `rotulos.py`/`explicacao.py`. Mudar texto que vai ao modelo sobe `VERSAO_DAS_INSTRUCOES` e invalida notas anteriores (FR-1515) — fazer antes da rodada na L4 custa menos.
- Precisa de decisão humana? sim — vocabulário.
- Confiança: alta.

<a id="as-07"></a>
#### AS-07 — Acesso à L4 / Ollama do Cefor (T058–T060) e dados da infraestrutura
- Descrição: verificação de conexão, rodada completa da matriz e medições de GPU/latência só podem rodar no Ollama da L4. Faltam: endereço do Ollama institucional, nome exato do modelo, quantização, se a versão aceita `truncate`/`shift`, leituras de GPU por quem opera, a calibração de tokens na L4 (no OpenRouter ela dependeu do provedor: ~250 fixos num, 9/mensagem no Parasail), e a escolha do modo de raciocínio (DP-5; estimativa de ~15 tokens/s com raciocínio ligado "pode virar minutos").
- Origem (demanda/decisão): 7bf91059 (12–14/10) — L10-21, L10-33, L10-35, L10-38; 84c96e5f — L10-17, L10-18; 071 T058–T060, DP-5, R-017; f55c52a5 — L10-45 (roteiro C da 073); PR #278, #283; doc-achados c.12 (DEP-05, DA-08).
- Decisão aplicável: usuário, 12/10: Ollama da L4 como destino, sem transferência automática local→externo; 13/10 DP-7 (b): só o modelo bloqueia em execução; 14/10: *"Minha preferência… é um procedimento curto de configuração, sem criar uma tela nova"* (app no Mac pode consultar o Ollama do Cefor).
- Spec / PRs / commits: 071 (`tasks.md:456-466`); 073 quickstart C (no PR #283, aberto).
- Implementação: código pronto — `duvidas/management/commands/verificar_servico_de_inferencia.py`, `avaliar_assistente.py`, `backend/scripts/carga_do_assistente.py`; `duvidas/infrastructure/inferencia/ollama.py`.
- Testes: `tests/unit/duvidas/test_verificar_servico.py`, `test_adaptador_ollama.py` (com `urlopen` falso; nenhuma chamada real à L4).
- Estado: BLOQUEADO
- Lacuna: acesso de rede e dados da infraestrutura; nenhuma medição real; `specs/071-…/avaliacao/` não existe.
- Impacto: equipe (piloto não conclui); candidato (sem medição de latência, a Fase C não abre).
- Prioridade: P2 — bloqueia o fechamento do piloto, não a operação de seleções; **P0 para a abertura pública**.
- Dependências: TI do Cefor; destrava AS-08, AS-09 (a sessão que conta), AS-19.
- Próxima ação recomendada: pedir à TI, por escrito, os itens da lista "a confirmar com a infraestrutura" (R-017) e o acesso de rede; então rodar o quickstart D da 071.
- Precisa de decisão humana? sim — DP-5 (raciocínio ligado/desligado ou ambos); o resto é ação externa.
- Confiança: alta.

<a id="as-08"></a>
#### AS-08 — Critérios de aceite do piloto (DP-3) e conclusão
- Descrição: limiares de qualidade e orçamento de latência p95 não estão aprovados; dos seis critérios de conclusão do piloto, só o 1 (suíte) está cumprido; o FR-1512 foi cumprido por amostra (um Perfil por Edital), e não por todos os parâmetros.
- Origem (demanda/decisão): 7bf91059 — L10-23, L10-34; 071 verificacao §5; 071 spec "Critérios de conclusão do piloto" e DP-3; auditoria DA-08.
- Decisão aplicável: usuário, 13/10 (7bf91059): *"cabe medir primeiro para definir o orçamento de latência, mas aprovar os critérios antes"* de declarar resultado aceito.
- Spec / PRs / commits: 071.
- Implementação: relatório/rodada em `avaliar_assistente.py`; critérios inexistentes.
- Testes: SC-545 a SC-550 na suíte; SC-551 a SC-558 sem medição.
- Estado: BLOQUEADO
- Lacuna: proposta de limiares a partir da medição na L4 e aprovação do usuário; revisão humana do `revisao.csv`.
- Impacto: equipe; decide se o modelo serve.
- Prioridade: P2 — **P0 para a abertura pública** (o 071 diz: "Concluído não é aprovado para a Fase C").
- Dependências: AS-07.
- Próxima ação recomendada: depois da primeira medição na L4, o agente propõe limiares a partir dos números e da §7.2 da auditoria; o usuário aprova antes do relatório final.
- Precisa de decisão humana? sim — aprovar os critérios (DP-3).
- Confiança: alta.

<a id="as-09"></a>
#### AS-09 — Sessão acompanhada com o setor no piloto (T065, SC-559)
- Descrição: nenhuma pessoa do setor usou o piloto; a T065 pede uma sessão acompanhada, na máquina da equipe, com um serviço real (OpenRouter com limite na chave, como ensaio, ou a L4, "que é a sessão que conta").
- Origem (demanda/decisão): 7bf91059 — L10-22; 071 `tasks.md:501`, verificacao §5 critério 5; PR #278/#280; github §1.2; doc-achados c.12 ("AGUARDA AÇÃO HUMANA").
- Decisão aplicável: DP-1, 12/10 (7bf91059): *"sessões acompanhadas na máquina da equipe."*
- Spec / PRs / commits: 071.
- Implementação: o piloto está pronto (`interface/assistente.py`).
- Testes: nenhum percurso humano.
- Estado: ESPECIFICADO E NÃO IMPLEMENTADO
- Lacuna: a sessão.
- Impacto: equipe de seleção (a avaliação precisa do julgamento dela).
- Prioridade: P2 — validação do piloto.
- Dependências: AS-01 (pode ser na mesma sessão); AS-07 para a sessão "que conta".
- Próxima ação recomendada: fazer já uma sessão-ensaio pelo OpenRouter (registro sem texto de participante, orientação sobre dado pessoal no início) e repeti-la na L4 quando houver acesso.
- Precisa de decisão humana? sim — quem do setor e quando.
- Confiança: alta.

<a id="as-10"></a>
#### AS-10 — Qualidade e fundamentação das respostas (instruções v4, CB-17/CB-18, paráfrase, injeção)
- Descrição: as instruções foram de v1 a v4 em 14/10 e congeladas na v4 (`duvidas/domain/mensagens.py:23`). A v4 corrigiu a ampliação "pretos e pardos" → PPI numa resposta só; o caso que a separa (`CB-18`, candidato indígena) e duas execuções da continuação "Preciso enviar todos?" ficaram **sem evidência** (429 do Parasail, cota compartilhada); a resposta ainda repete a lista comum; respostas mínimas (45 vagas sem a divisão AC/PPI/PcD que o CA-01 espera). Limites conhecidos da conferência: ela não prova paráfrase fiel nem condição omitida (R-005), e uma instrução escondida no texto do Edital chega ao modelo como fonte — se obedecida, a conferência não barra.
- Origem (demanda/decisão): 7bf91059 (13–14/10) — L10-24, L10-25, L10-30, L10-31, L10-32, L10-37; 071 verificacao §8; PR #280; doc-achados c.12 ("instruções v2 a v4 sem conclusão").
- Decisão aplicável: usuário, 14/10 (7bf91059): *"Mantenha a versão 4. Não crie outra versão de prompt…"*; *"Não estenda uma exigência de um subgrupo ao grupo inteiro."*; se a ampliação persistir, parar versões e comparar modelos (registrado na verificacao §8). Injeção: aceito como limite, julgado na revisão humana (CA-25).
- Spec / PRs / commits: 071 (FR-1515, R-005), #280; casos `CB-17`/`CB-18` na matriz.
- Implementação: `duvidas/domain/mensagens.py`, `duvidas/domain/conferencia.py`.
- Testes: `tests/unit/duvidas/test_conferencia.py`, `test_versoes_das_instrucoes.py`; `tests/integration/duvidas/test_limites_da_resposta.py:49-63` (o limite da instrução escondida).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: evidência dos casos pendentes; rodada da matriz com repetições (uma chamada por caso não mede taxa); revisão humana.
- Impacto: candidato (resposta errada ou incompleta sobre documentos e reservas de vaga).
- Prioridade: P2 — **P0 para a abertura pública** (respostas sobre reserva de vagas tocam direitos).
- Dependências: AS-07, AS-08.
- Próxima ação recomendada: na L4 (ou noutro provedor do OpenRouter sem cota compartilhada, se o usuário autorizar o gasto), rodar CB-17, CB-18 e a continuação com repetições, sem mudar a v4.
- Precisa de decisão humana? sim — autorizar chamadas pagas e, se a ampliação voltar, a comparação de modelos.
- Confiança: alta — verificacao §8 e código.

<a id="as-13"></a>
#### AS-13 — Protótipo da Fase C (#280): interno, sem link, com estados simulados
- Descrição: painel lateral no desktop (não modal), tela cheia no celular, aberto por botão "Dúvidas sobre este Edital", três sugestões + "Mais dúvidas" respondidas pela 070 sem modelo; mergeado como piloto interno. A rota não tem link em nenhum template (só se chega digitando a URL), por desenho.
- Origem (demanda/decisão): 7bf91059 (14/10) — decisões "UI Fase C", "protótipo", "refinamento"; codigo-e-configuracao §7 (único inalcançável por navegação); doc-achados c.12 (Fase C ABERTO).
- Decisão aplicável: usuário, 14/10: *"Integrar à `main` não significa liberar o assistente aos candidatos."*; *"Não criaria agora um classificador…"*.
- Spec / PRs / commits: #280; sem spec própria (a Fase C não foi especificada).
- Implementação: `interface/prototipo_do_assistente.py`, `interface/templates/interface/prototipo_do_assistente.html`, rotas `interface/urls.py:62-80`.
- Testes: `tests/interface/test_prototipo_do_assistente.py` (11 casos).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: nenhum percurso com candidato real ou com o setor; sem link (a equipe precisa saber a URL); comportamento real só no 074 local.
- Impacto: equipe (avaliação da experiência).
- Prioridade: P3 — evolutivo.
- Dependências: AS-12 (o 074 é o uso real do painel), AS-14, AS-15.
- Próxima ação recomendada: nenhuma de código; usar o 074 para os percursos.
- Precisa de decisão humana? não.
- Confiança: alta.

<a id="as-14"></a>
#### AS-14 — Acessibilidade e celular real do painel do assistente
- Descrição: o teclado virtual em celular real não foi validado (Simulador iOS indisponível; localhost não abre no aparelho); não há percurso com leitor de tela; a varredura de acessibilidade do portal não inclui o painel, e os testes do protótipo não afirmam `aria-live`, foco ou 375 px (o template tem atributos `aria-`). A auditoria §6.3 especifica formulário nativo, região `aria-live`, foco na resposta nova, `<details>` e `flex-wrap`.
- Origem (demanda/decisão): 7bf91059 (14/10) — L10-26; auditoria do assistente §6.3 e §9 (Fase C, "teclado virtual em aparelho real… não validado"); doc-achados c.12.
- Decisão aplicável: usuário, 14/10: *"Mantenha a validação do teclado em aparelho real como pendência explícita"*.
- Spec / PRs / commits: #280; 074 (local).
- Implementação: template do protótipo e `<worktree 074>/interface/painel_do_assistente.py`.
- Testes: nenhum específico de acessibilidade do painel (grep em `test_prototipo_do_assistente.py` e `test_acessibilidade*.py`).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: validação em aparelho real e com leitor de tela; teste automatizado das regras da §6.3.
- Impacto: candidato com deficiência ou só com celular.
- Prioridade: P3 hoje — **P0 para a abertura pública** (acessibilidade é requisito de serviço público).
- Dependências: AS-12 (expor a página local na rede da máquina para o aparelho), AS-15.
- Próxima ação recomendada: na spec da Fase C, transformar a §6.3 em FR com teste; validar com aparelho real pela rede local.
- Precisa de decisão humana? não.
- Confiança: média — a ausência de teste foi verificada por grep; o template não foi auditado por inteiro.

<a id="as-15"></a>
#### AS-15 — Spec da Fase C (abertura do assistente ao candidato) não escrita
- Descrição: não há spec da interface pública e operação. Seus requisitos estão espalhados: portão da 071 (DP-3 cumprida, T046 e canal emendado, exclusividade por Edital, achado do documento ligado, LGPD, texto de natureza não oficial), pendências da 074 (limites por visitante, proteção contra uso automatizado, texto definitivo, revisão de fontes por Edital, autenticação institucional e o lugar da página na implantação), DA-10 (liberação por Edital), DEP-06 (isolamento) e a redação das explicações para o painel.
- Origem (demanda/decisão): 7bf91059 (14/10) — L10-27, L10-28; auditoria do assistente §9 (Fase C); 071 spec "Fases posteriores"; 074 "Pendências para a implantação"; doc-achados c.12 ("Fase C… nenhuma spec na `main`").
- Decisão aplicável: usuário, 12/10: fases A → B → C, cada uma posterior; 14/10 (e76c2efd): a 074 abre só local e não revoga o FR-1462 para implantação.
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente (o 074 é demonstração local).
- Testes: nenhum.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a spec; a maior parte dos insumos depende de AS-01..AS-10.
- Impacto: candidato (é a única forma de o assistente chegar a ele).
- Prioridade: P3 — evolutivo; sem implantação e com portões ainda bloqueados, especificar agora seria prematuro.
- Dependências: AS-01–AS-05, AS-07–AS-10, AS-14, AS-16–AS-18; B-1 (área GO).
- Próxima ação recomendada: nenhuma até o piloto concluir; manter a lista de portões num único lugar (a 071 já a tem).
- Precisa de decisão humana? sim — quando abrir a Fase C.
- Confiança: alta.

<a id="as-16"></a>
#### AS-16 — Limites por visitante, isolamento da inferência e infraestrutura para uso público
- Descrição: o teto de conversas da 074 (`ASSISTENTE_CONVERSAS_POR_SESSAO`, D-004) é por sessão e se contorna apagando o cookie; não há limite por visitante que não dependa do cookie, além do limite de gasto da chave; faltam fila, cache, CSP e limite de requisições genérico; os workers são síncronos de 120 s e a inferência divide os processos com o portal (o 071 tem só um teto global de simultâneas; o pool separado ficou "para a Fase C, se a medição pedir").
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-10; e76c2efd (14/10) — L10-59; auditoria DEP-06 (PARCIAL); 074 D-004 e FR-1685.
- Decisão aplicável: 074 D-004 (14/10): teto por sessão agora, limite por visitante como pendência da implantação.
- Spec / PRs / commits: 071 D-008 (teto global); 074 D-004 (local).
- Implementação: `ASSISTENTE_TETO_SIMULTANEO`, `ASSISTENTE_TURNOS_POR_CONVERSA`, `ASSISTENTE_PERGUNTA_MAXIMA` (`config/settings/base.py:234-269`); teto por sessão só na worktree 074.
- Testes: `tests/integration/duvidas/test_teto_e_orcamento.py`; 074 `test_assistente_na_pagina.py:204`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: limite por visitante, proteção contra automação, isolamento medido (o `carga_do_assistente.py --carga-publica` existe e nunca rodou contra a L4).
- Impacto: operação (o portal pode ficar lento sob carga de inferência); custo.
- Prioridade: P3 hoje (só local) — **P0 para a abertura pública**.
- Dependências: AS-07 (medição), AS-15.
- Próxima ação recomendada: medir com `carga_do_assistente.py --carga-publica` na L4 antes de decidir pool separado.
- Precisa de decisão humana? sim — forma do limite por visitante.
- Confiança: alta.

<a id="as-17"></a>
#### AS-17 — Configuração por seleção/Edital e chaves do assistente
- Descrição: as chaves são globais: `ASSISTENTE_PILOTO` (gestão), `ASSISTENTE_NA_PAGINA_DO_EDITAL` (página pública, só local, sem commit). Não há como habilitar o assistente num Edital e não noutro; a auditoria recomendou (DA-10, opção b) "chave global + lista de Editais habilitados", para começar por um certame com equipe de plantão. Também não há configuração por Edital do canal (vem do texto) nem dos textos.
- Origem (demanda/decisão): auditoria do assistente §8 DA-10 e §9 C5; doc-achados c.12 (DA-10 ABERTO); codigo-e-configuracao §3; specs-038-073 §2.
- Decisão aplicável: nenhuma registrada sobre DA-10.
- Spec / PRs / commits: nenhuma.
- Implementação: `config/settings/base.py:225` (`ASSISTENTE_PILOTO`); `production.py:204-215`.
- Testes: `tests/test_configuracao_producao.py` (recusas de produção).
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: decisão DA-10 e, se (b), o modelo da lista.
- Impacto: equipe de seleção (liberação gradual), candidato.
- Prioridade: P3 — evolutivo, entra na Fase C.
- Dependências: AS-15; AS-03 (a exclusividade é por Edital e pode decidir quais Editais abrem).
- Próxima ação recomendada: decidir DA-10 na spec da Fase C.
- Precisa de decisão humana? sim — DA-10.
- Confiança: alta.

<a id="as-18"></a>
#### AS-18 — LGPD e retenção dos registros do assistente
- Descrição: o registro guarda pergunta e resposta sem identidade, com mascaramento de CPF, e-mail e telefone (que a spec diz não ser anonimização), e se exclui 90 dias depois do relatório final, por `excluir_registros_do_piloto`. O relatório final não existe (depende da L4), então o prazo nunca começa a correr: as trocas dos ensaios ficam nos bancos locais (`ps_071_corpus` etc.) sem data de exclusão. Falta a validação institucional (DA-09/DEP-07) e a avaliação de LGPD do texto livre de candidatos reais e da retenção para a abertura pública. Não há tela para os registros (`TrocaDoPiloto` só via `avaliar_assistente`).
- Origem (demanda/decisão): 7bf91059 (12/10) — DP-2; 071 spec "Proteção de dados"; 074 pendências; specs-038-073 X-08 (LGPD em quatro frentes); doc-achados c.12 (DA-09 "AGUARDA DECISÃO"); auditoria de configurações (avisos e LGPD, mesmo encarregado).
- Decisão aplicável: DP-2, 12/10 (7bf91059): registrar sem identidade, mascarar, excluir em 90 dias após o relatório final; *"O mascaramento não deve ser apresentado como anonimização garantida."*
- Spec / PRs / commits: 071 (FR-1503, FR-1508, FR-1509, D-012, D-013).
- Implementação: `duvidas/domain/mascara.py`; `duvidas/management/commands/excluir_registros_do_piloto.py`.
- Testes: `tests/unit/duvidas/test_mascara.py`, `tests/integration/duvidas/test_exclusao.py`, `test_log_do_piloto.py`.
- Estado: PARCIALMENTE IMPLEMENTADO
- Lacuna: manifestação do encarregado/DPO; um prazo para registros de ensaio enquanto não há relatório final.
- Impacto: candidato (dado pessoal digitado por descuido); instituição.
- Prioridade: P3 hoje (só perguntas sintéticas da equipe) — **P0 para a abertura pública**.
- Dependências: AS-08 (relatório final); validação de LGPD comum à 066/072 (outra área).
- Próxima ação recomendada: levar ao encarregado junto com a LGPD dos avisos (066) e da 072; decidir se os registros dos ensaios se apagam já.
- Precisa de decisão humana? sim — institucional (LGPD) e do usuário (apagar os ensaios).
- Confiança: média — a falta de prazo para os ensaios é inferência do desenho (exclusão ancorada no relatório final), não foi medida nos bancos locais.

<a id="as-20"></a>
#### AS-20 — Achados menores da 070: guardião de cobertura e itens baixos do analyze
- Descrição: o guardião de cobertura (SC-533) classifica campos, e não confere quais seções cada pergunta deixa de fora — não acusou as seções omitidas (Disposições Finais etc.); a 071 contornou mandando toda seção ao modelo (R-002), mas as respostas determinísticas da 070 seguem como estão. Cinco achados baixos do analyze (G3, G4, G5, U2, O1) foram oferecidos como tarefas sem resposta; G4 e U2 aparecem tratados depois.
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-11, L10-16; 071 verificacao §6 (primeiro achado); `specs/070-…/checklists/requirements.md:95`.
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 070, 071 (R-002).
- Implementação: `duvidas/domain/cobertura.py` (tabela por campo, `VERSAO_DO_ESQUEMA = 17`).
- Testes: `tests/unit/duvidas/test_cobertura.py`.
- Estado: NÃO CONFIRMADO
- Lacuna: conferir G3, G5 e O1 um a um; decidir se a 070 precisa mostrar as seções que nenhuma das 12 perguntas cobre.
- Impacto: equipe (manutenção); baixo para o candidato.
- Prioridade: P3 — sem efeito observável hoje.
- Dependências: AS-01.
- Próxima ação recomendada: conferir os cinco itens contra o código numa passada curta, e fechar ou registrar.
- Precisa de decisão humana? não.
- Confiança: baixa — o conteúdo de G3/G5/O1 não foi relido nesta consolidação.

<a id="as-22"></a>
#### AS-22 — Assistente de acompanhamento da candidatura (área autenticada)
- Descrição: assistente que leria resultados, convocações e prazos da própria inscrição do candidato. Registrado como evolução posterior, fora das fases A–C, porque lê dado pessoal.
- Origem (demanda/decisão): 84c96e5f (12/10) — L10-20; 071 spec "Fases posteriores"; auditoria §9; doc-achados c.12 ("AGUARDA DECISÃO").
- Decisão aplicável: usuário, 12/10 (84c96e5f): *"Registre no roadmap, como evolução posterior e fora do escopo dessas fases, o assistente de acompanhamento da candidatura"*.
- Spec / PRs / commits: nenhuma.
- Implementação: inexistente.
- Testes: nenhum.
- Estado: ADIADO FORMALMENTE
- Lacuna: —
- Impacto: candidato (futuro).
- Prioridade: P3 — evolutivo; pelo princípio VI não é prioridade por estar registrado.
- Dependências: Fase C em operação; decisão própria sobre dado pessoal.
- Próxima ação recomendada: nenhuma.
- Precisa de decisão humana? sim — se e quando.
- Confiança: alta.

<a id="as-24"></a>
#### AS-24 — Loteria Federal (Caixa): integração real, sem verificação contínua nem acordo
- Descrição: o sorteio busca o resultado em `servicebus2.caixa.gov.br/portaldeloterias/api/federal/{referencia}`, uma API aberta sem contrato, termos, versionamento ou SLA. O E2E contra a fonte real (`SORTEIO_E2E_FONTE_REAL`) não roda em CI nem em rotina; a última execução é de 10/09. A cadeia de substituição ficou quase inerte (HTTP 500 é "falha de acesso", e não indisponibilidade declarada), e a escolha institucional da fonte não foi registrada.
- Origem (demanda/decisão): fbd9a85a (08/09) — L04-47; df245428 (09/09) — L04-81; 2acf27b6 (10/09) — L04-100; c1e1e429 (10/09) — L04-101; 2bc3c441 (29/09) — L08-24; RC-74; `doc/achado-fonte-real-do-sorteio-sem-gatilho.md`; S-021-01.
- Decisão aplicável: nenhuma registrada sobre a fonte ("a escolha institucional é sua", 08/09) nem sobre a regularidade (CI agendado × rotina manual, 29/09).
- Spec / PRs / commits: 021/022; PR #83 (E2E real).
- Implementação: `sorteios/infrastructure/fontes/loteria_federal.py:22,45`; `SORTEIO_FONTE_TIMEOUT_SEGUNDOS`/`_TENTATIVAS` (`base.py:144-145`); `.github/workflows/` sem `schedule`.
- Testes: `tests/interface/test_sorteio_com_a_fonte_de_producao.py:48-53` (pulado sem a chave).
- Estado: IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE
- Lacuna: verificação periódica; decisão sobre a substituição; registro institucional da fonte.
- Impacto: equipe de seleção e candidatos — se a API mudar, o sorteio falha no dia do ato; o piloto é por sorteio.
- Prioridade: P1 — o ato é público e marcado; uma mudança silenciosa na API só aparece na hora.
- Dependências: área de sorteio (dona do domínio); DP-17 (automação explícita) não se aplica a um teste agendado.
- Próxima ação recomendada: rodar o E2E à mão antes de cada sorteio real, e decidir se vira workflow agendado.
- Precisa de decisão humana? sim — regularidade do E2E e a escolha institucional da fonte.
- Confiança: alta.
- **Fundidos neste item:** AV-27, GO-33.
  - *AV-27 (AV), E2E contra a fonte real da Caixa não roda em lugar nenhum* — lacuna: gatilho periódico ou passo obrigatório antes de cada sorteio. Próxima ação: decidir entre workflow agendado e passo de checklist pré-sorteio. - Precisa de decisão humana? sim.
  - *GO-33 (GO), E2E contra a fonte real do sorteio (Caixa) não roda em lugar nenhum* — lacuna: gatilho (agendado ou rotina antes de cada sorteio). Próxima ação: decidir entre `schedule` semanal no CI ou passo obrigatório no runbook do sorteio. - Precisa de decisão humana? sim.


## PV — Achados do percurso pelo navegador (15/10)

<a id="pv-01"></a>
#### PV-01 — Data de nascimento pedida duas vezes na mesma inscrição
- Descrição: no Edital 01/2026 do `seed_demo`, que pede o Requerimento de Matrícula na inscrição e declara o fato "Data de nascimento" entre os dados exigidos pelo Edital, a candidata informa a data no Requerimento e, minutos depois, a revisão pede de novo "Data de nascimento *" em "Dados exigidos pelo Edital". São duas fontes do mesmo dado, sem conferência entre elas.
- Origem (demanda/decisão): percurso de 15/10 (esta auditoria).
- Decisão aplicável: nenhuma registrada.
- Spec / PRs / commits: 029 (Requerimento), 044 (fatos e lista exigida).
- Implementação: revisão `ps/portal/templates/portal/` (formulário com `fato-<id>`); Requerimento `ps/requerimentos/`.
- Testes: nenhum que confronte as duas fontes.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: o fato declarado no Edital não reaproveita o dado do Requerimento nem acusa divergência; o elaborador não é avisado da sobreposição na composição.
- Impacto: candidato (redigitação, risco de valores diferentes); comissão (qual das duas vale).
- Prioridade: P2 — atrito e risco de divergência, sem perda de direito.
- Dependências: CA-07 (momento da coleta do Requerimento).
- Próxima ação recomendada: decidir se o fato preenche a partir do Requerimento quando os dois existirem, ou se a composição avisa da sobreposição.
- Precisa de decisão humana? sim — qual das duas fontes manda.
- Confiança: média — observado num Edital de demonstração; depende de o Edital real declarar o mesmo fato.

<a id="pv-02"></a>
#### PV-02 — O comprovante fala com o candidato em linguagem técnica
- Descrição: a tela do comprovante e o PDF mostram resumos SHA-256 de cada documento e do próprio arquivo, e instruem "shasum -a 256 arquivo.pdf" e "certutil -hashfile … SHA256". O e-mail de confirmação é claro; o comprovante não.
- Origem (demanda/decisão): percurso de 15/10.
- Decisão aplicável: nenhuma registrada; a verificação de integridade é requisito da 009/010 (prova do que foi entregue).
- Spec / PRs / commits: 009, 010.
- Implementação: `ps/portal/templates/portal/comprovante.html`, `ps/inscricoes/domain/autenticidade.py`.
- Testes: os do comprovante (conteúdo), nenhum de compreensão.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: a informação técnica não está recolhida nem explicada para quem não é da área; a linguagem simples da 069 não alcançou o portal.
- Impacto: candidato (confusão, chamadas ao atendimento).
- Prioridade: P3 — o comprovante cumpre a função; é legibilidade.
- Dependências: CA-01 (percurso com cinco pessoas), CA-04 (ajuda).
- Próxima ação recomendada: recolher os resumos sob "Para conferir a integridade (comissão)" e manter o texto principal só com protocolo, código e lista do que foi recebido.
- Precisa de decisão humana? não.
- Confiança: alta — lido na tela e no e-mail.

<a id="pv-03"></a>
#### PV-03 — A página pública "Verificar o sorteio" transborda a 375 px
- Descrição: a linha de comando do verificador (`node sorteio-cli.js --resumo …`) num `<code>` sem quebra leva a página a 673 px de largura num celular de 375 px.
- Origem (demanda/decisão): percurso de 15/10 — medição por `scrollWidth` em dez telas; as demais públicas ficaram em 375.
- Decisão aplicável: a 055/058 fixaram 375 px como largura de conferência.
- Spec / PRs / commits: 021, 035.
- Implementação: `ps/portal/templates/portal/verificacao_de_sorteio.html`.
- Testes: os de largura (`t/interface/test_larguras.py` e os de 375 px) não incluem esta tela.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: quebra (`overflow-wrap:anywhere`) ou rolagem própria do bloco de código; a tela no guardião de larguras.
- Impacto: candidato ou cidadão que confere o sorteio pelo celular.
- Prioridade: P3 — página de conferência técnica, de uso raro.
- Dependências: nenhuma.
- Próxima ação recomendada: correção direta de CSS e inclusão no teste de larguras.
- Precisa de decisão humana? não.
- Confiança: alta — medido.

<a id="pv-04"></a>
#### PV-04 — O detalhe do Edital na gestão transborda a 375 px
- Descrição: o link "Ver as respostas do assistente de dúvidas (validação interna)", acrescentado pela 070, não quebra e leva a página a 440 px.
- Origem (demanda/decisão): percurso de 15/10.
- Decisão aplicável: a mesma régua de 375 px.
- Spec / PRs / commits: 070 (#274).
- Implementação: `ps/interface/templates/interface/detalhe.html`.
- Testes: o detalhe do Edital não está no guardião de larguras com este link.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: o rótulo longo sem quebra.
- Impacto: equipe de seleção ao celular.
- Prioridade: P3 — a gestão é usada em mesa; resíduo de polish.
- Dependências: nenhuma.
- Próxima ação recomendada: correção direta (quebra ou rótulo menor).
- Precisa de decisão humana? não.
- Confiança: alta — medido.

<a id="pv-05"></a>
#### PV-05 — Rótulos vazios e retificações homônimas no portal
- Descrição: (a) no Requerimento preenchido antes do envio da inscrição, a linha "Protocolo · da sua inscrição" aparece sem valor; (b) a lista "Edital e documentos" da página da seleção mostra duas entradas "Retificação 15/10/2026", uma "vigente desde 30/10/2026", enquanto o aviso acima diz que o conteúdo é o vigente desde 15/10 — o candidato só distingue as duas pelo "O que mudou (1)/(2)".
- Origem (demanda/decisão): percurso de 15/10.
- Decisão aplicável: (b) toca a decisão pendente do ED-06 (qual documento a página oferece quando há Retificação de vigência futura).
- Spec / PRs / commits: 029 (a); 047, 048, 072 (b).
- Implementação: `ps/portal/templates/portal/requerimento.html` (a); `ps/portal/templates/portal/selecao.html` (b).
- Testes: nenhum que cubra o Requerimento sem protocolo nem a lista com duas Retificações do mesmo dia.
- Estado: IDENTIFICADO E NÃO ESPECIFICADO
- Lacuna: omitir a linha sem valor; numerar ou nomear as Retificações e dizer "ainda não vigente" na de vigência futura.
- Impacto: candidato.
- Prioridade: P3 — (b) sobe junto com o ED-06 se a decisão de lá mudar a lista.
- Dependências: ED-06.
- Próxima ação recomendada: (a) correção direta; (b) resolver com o ED-06.
- Precisa de decisão humana? não para (a); (b) segue o ED-06.
- Confiança: alta — lido na tela.


## Anexo — conferidos e resolvidos depois (não entram)

Pendências que as fontes ainda davam como abertas e que a verificação contra a `main` encontrou resolvidas. Ficam aqui para provar que foram conferidas.

### ED

- L01-01 / L01-33 proveniência por posição e Retificação no Perfil errado → endereçamento por `id=` (004, #6).
- L01-03 500 ao publicar Retificação sem efeito → `no_effective_change` (#1→#3).
- L01-15 Modalidades em textarea → editor próprio com Regra Normativa (`ps/interface/forms.py:100-125`).
- L01-20 Título/descrição não editáveis → editáveis (`compor_identificacao.html:54-64`; S-002-08).
- L01-29 regra do ADD → ADD só por `/-` (004).
- L01-31 `expectedPreviousHash` nunca verificado → verificado (#2→#3).
- L01-41 Perfil publicado mutilado → validação do snapshot resultante (005, #7).
- L01-45 `endAt` > `startAt` → recusado na elaboração (`ps/editais/domain/cronograma.py:25-30`).
- L01-53 referências visuais fora do repo → versionadas (008).
- L01-55 / L04-05 Edital sem anexos → 020 (#58).
- L01-56 / L01-57 catálogo de autoridades em código; unidade constante → 060 (#254), cadastro pela tela.
- L01-58 / AX-8 / RC-20 capa "EDITAL 140/2025" × rodapé 149/2026 → corrigido (#220/#221).
- L01-64 Editais v3 irretificáveis → superado pela elevação canônica (012 FR-098) e sem dado real.
- L02-01 / L02-05 `number`/`year` retificáveis → não retificáveis (`ps/editais/domain/mutabilidade.py:177-185`).
- L02-06 / L02-07 PDF com cara de relatório → 008 (#16) e 054 (#233).
- L02-10 comparar com Edital oficial → auditoria do PDF de 08/10 e estudo de 21/09.
- L03-23 / L07-07 / AX-9 / RC-12 teto sem campo → `compor_inscricao.html` (#224), portal (#225), teto 0 (#227).
- L03-26 / L05-31 / L07-29 / L06-21 / L07-30 / RC-37 / RC-38 Retificação não acrescentava janela, corte,
  reversão, Modalidade nem critério → 048 (#197) e DP-14 (#202).
- L03-36 E2E18-005 janela declarada no assistente apagada → #51.
- L04-01 quadro de vagas por modalidade → 025 (#99, #101, #102).
- L04-06 local do evento no Cronograma → 021 US6.
- L04-18 Revisão sem Documentos Exigidos → #55; RC-149 Revisão sem Classificação → `7abde347` (#210).
- L04-42 / L05-51 / E2E17-007 segundo Edital no Processo sem tela → "Novo Edital" (`processo_detalhe.html:168-170`, #119).
- L04-83 / Q-2 quadro estruturado → 025 D-1.
- L04-88 recusar publicar com inscrições encerradas → 028 (#118), IMPEDE mantido pela decisão de 25/09.
- L04-106 / L05-12 / L05-25 / R-006 soma sem a ampla declarada → 027 FR-317 (#116).
- L05-17 / RC-07(TF-1) copiar Perfil → 043 (#170) e 051 (#226, #231).
- L05-58 (Cronograma) CONCLUÍDA falso no Cronograma → 028 (só esta etapa; resto em ED-20).
- L05-84 / L05-85 AX-8 e AX-9 → ver RC-20 e RC-12 acima.
- L05-87 / AX-14/17 / RC-28 / RC-51 documento por modalidade alcançava um Perfil só → #161 e 044 (#173).
- L05-89 / AX-16 / G-006 / L07-67 / RC-08 rascunho local perdia coleções → #216.
- L06-18 / D-G1 FR-461 → substituída pelo invariante "Perfil sem marco com corte é impedido" (046, #188).
- L06-35 / L07-40 (`schedule.status` nunca derivado) / RC-80 → DP-01, 045 (#187).
- L07-59 / L08-05 / RC-39 / RC-111 "O que mudou" calava campos → #185, #201 (guardião por par retificável).
- L07-66 / L08-09 `governedStage` não remapeado no reuso → #169 (rascunhos antigos só em bancos de dev).
- L08-63 / RC-143 SC-001 da 008 → emendada pela 054.
- RC-21 remissão a "ANEXO X" sem anexo → aviso na Revisão (#220).
- RC-24 / AX-3 (parte) 12 seções fixas → catálogo de 22 entradas (054, #233).
- RC-140 redação padrão que afirma norma → retirada (054).
- RC-144 / Q-10 declaração do Requerimento fora do PDF → publicada (054; `pdf.py:4549`).
- RC-145 consolidado igual ao original → datado (054, FR-995).
- RC-15 / §12 item 5 casas decimais e arredondamento sob sorteio → 067 (aPDF-ED-03, #268).
- RC-119 período `CANCELADO` → impede publicar (#221) — confirmar severidade em ED-47.
- RC-118 / L01-05 FR-034 encerrar Processo → exige Editais finais (#220).
- E2E-021 cancelar Retificação → #32; devolução da Retificação → #2/#24.
- E2E-004 (metade) editar documentos existentes por Retificação → #32 (resto em ED-08).
- ACH-01 "?" no PDF do Edital → #265 (comprovante/divulgação são de outra área).
- aPDF-ED-01 conflito de numeração → 065 (#266) (resíduos em ED-25).
- aPDF-ED-02/03/12 → 067 (#268); aPDF-ED-04/11 → 068 (#270); aPDF-ED-05/07(P)/08/14/16/18/22/24/25 → 069 (#275).
- Achado #3 cabeçalho repetido por polo → `c0403a91` (#115); documento consolidado por 064/068 (dado em ED-31).
- Achado #16 Evento acrescentado sem `location` → #179.
- 89/2026 "Total 0" em Edital só de reserva → #233.
- DP-13 "aplicar a todos" / DP-19 campos definitivos → 051.
- DP-21 limite de mil campos → 13.000 + guardião (#232).

### CA

- L03-12 / E2E17-004 (eliminado antes do marco sem notícia) — 018 US1, PR #50.
- L08-82, L09-23 / H.18 (candidato não chega à convocação nem ao Requerimento) — 059, PR #251; `portal/templates/portal/inscricoes.html:45`, `_convocacao_da_inscricao.html:25`, `_chamado_do_requerimento.html:18`.
- L09-45, S-062-01, PRs #255 e #260 (acompanhamento não dizia a lista) — 063, PR #263; `portal/templates/portal/acompanhamento.html:66-68` (um cartão por lista e por marco).
- L09-46, parte "página do Edital ignora o candidato conectado" — `_convite_da_situacao` em `portal/views.py:662-678` (062).
- AX-9, RC-12, L05-85, L08-66, L08-67 (teto de inscrições não publicado, sem tela, aceito 0) — PRs #224, #225, #227; o portal diz o teto na seleção e na revisão.
- RC-49 / E2E15-007 (rascunho não avisava prazo encerrado) — PR #215; `portal/templates/portal/_rascunho_fechado.html`.
- RC-46, L05-53 (reconciliação do portal não chegava ao CPF) — não se reproduz com inscrição criada pelo portal (validação de 28/09, PR #218); resíduo C só para dado da 009, inexistente no piloto.
- L01-67 (cópia do comprovante por e-mail) — recibo com protocolo, código de verificação e link (`inscricoes/application/mensagem.py`, 010, decisão de 01/09).
- L01-82, L03-44 (nenhuma comunicação ativa) — código, confirmação, convocação (019) e avisos (066) existem; o resto está em CA-21.
- S-009-07, L01-68 (CTA abaixo da dobra) — 072 FR-1615 a FR-1617; o resíduo de ~200 px está em CA-12.
- C-01 a C-05, C-08, C-10 a C-12, C-14, C-18, C-19 da auditoria UX — 072 (spec:293-402), PR #277.
- L06-05 / A7 (`?destino=` poderia inscrever em nome de quem só se identificou) — `inscrever` é POST, e o destino só traz a pessoa de volta à vaga (`portal/views.py:979-1003`, 062/072).
- L04-60, S-022-03 (vocabulário "Em preenchimento") — mesmo termo em `inscricoes.html` e `supervisao.html`.
- L01-84 (CPF completo na auditoria, inscrição em Edital cancelado, oráculo etc.) — commits `ebb2e37`, `7a95983`, `6624e79`.
- L04-102, parte "Como este sorteio foi feito" — `portal/templates/portal/selecao.html:396`.
- L08-33 e PR #181, parte do portal (Evento cancelado) — régua unificada pela 047, PR #193.
- L06-50 / ACH-42, ACH-43 (o candidato não lia o parecer) — 036, PR #142; `tests/portal/test_parecer_do_titular.py`.
- RC-51 / achado #9 (documento condicional: portal × PDF) — PRs #161 e #173 (044).
- RC-144 (declaração do Requerimento não publicada) — 054, PR #233.
- RC-128 (cota assumida sem pergunta) — PR #202 (DP-14).
- L04-20, L04-37 (histórico público só na API) — 024, PR #91 (lista de atos com histórico na página).
- L01-52 (raiz da aplicação) — PR #18 (raiz → vitrine).
- L02-24 (eventos de credencial invisíveis) — decisão deliberada D-012 da 010 (`identidade/application/credenciais.py:180-188`); o que resta de trilha está em CA-27.
- FR-048 da 010 (identificação por declaração em produção) — tela removida; `production.py:104-109` recusa subir com a variável.

### AV

- E2E15-003 / RC-62 (avaliação concluída depois de Resultado oficial) — `ps/avaliacoes/application/avaliacao.py:366` recusa com 409 `inscricao_ja_tem_resultado` (PR #220, decisão de 28/09 "bloquear salvo reavaliação").
- E2E18-001 / H.2 / L04-35 (reavaliação determinada sem cumprimento) — PR #218 "não se reproduz"; porta em `ps/resultados/application/consolidacao.py:137-143`; manual `00-arquitetura-do-manual.md:47` "tem caminho". A orientação restante está em AV-14.
- L03-06 prazo recursal não estruturado — 018 (janela por marco); E2E18-005 janela apagada — PR #51.
- L03-07 `calculo.py` colapsando Resultados — manager `vigentes` no Foundational da 018.
- E2E17-005 "Resultado definitivo" por dropdown — definitividade com seis fatos (018).
- L04-59 tela de recursos inalcançável — PR #113 (S-022-02).
- N-02 / L06-34 / L07-38 recurso aguardando admissibilidade sem sinal — RC-79 D+I, DP-02 pela 045 (`supervisao.py`, `sinais_do_recurso`).
- ACH-43/42 julgador sem a prova e titular sem parecer — 036 (#142, `0c96283`).
- L06-39 / L05-79 (AX-1) critério de desempate invertido sem correção — 048 D-004/FR-792 permite remover e acrescentar critério; `type` segue não retificável de propósito (`ps/editais/domain/mutabilidade.py:403`).
- L04-68 ordenação sem `lista_id` — PR #85 / 034; L04-80 e L07-24 ordem por lista em marco computado — 034 (#138).
- ACH-49/50/47, ACH-55/51 (sorteio inexecutável, fonte em texto) — 032, 034, 035.
- L04-98 faixa de sucesso do sorteio — PR #97 (`sorteio.html:52-77`).
- L04-10 semente do operador — 021 D-003 (fonte externa).
- L04-49, L04-65 achados da análise e da branch `spec-021-blockers` — `2bf8220a`.
- Relação do sorteio congelada com inscrições abertas — `629fa797` (`sorteios/application/relacao.py:18,77`).
- L03-58 / L07-69 beco das duas avaliações — 046 (`validation.py:2116`); a regra de combinação ficou em AV-34.
- RC-112 Ocorrência trava a Etapa seguinte — PR #220 (`resultados/application/prontidao.py`); RC-113 — PR #194.
- L07-63 / RC-53 Mesa recalcula lista exigida, sem "não se aplica" — 044 (`6e2aa5ae`, lista gravada no envio).
- L07-64 / RC-54 filtro de concorrência repetido — PR #172 (o resíduo está em AV-46).
- L05-01 / L04-73 fronteira 016 × 019 — D-002 da 014 (resposta de 11/09).
- L05-29 definição de ocupada — 019 D-011; L05-36 P-11 reclassificação/regularização/inércia — 019.
- L09-38 corte obsoleto para sempre após recurso — 061 (`a768dc95`).
- L09-23 / H.18 candidato não chega à convocação — 059 (PR #251).
- L07-78 seed sem Convocacao — T062 da 029.
- RC-137 porta da convocação pela ocupação — PR #221 (`ocupacao.html:134`); convocação sem normalizar `?lista=` — `6da74277`.
- RC-48 prazo recursal na página pública do resultado — 047 (#193).
- L03-16 documento de resultado em UTC — corrigido para publicações futuras (sem produção afetada).
- L03-04 três julgamentos da D-1 (Ocorrência) — aceitos pelo merge do #35.
- L03-47 recusa de reabrir nomeia o Resultado — mensagem citada no E2E18-001.
- L02-43 nota antes de abrir documento — FR-113: foco começa na leitura, ordem sugerida (`mesa_inscricao.html:279-287`).
- L02-45 UUID da versão em Conclusões — hoje "vigente desde dd/mm/aaaa" (`conclusoes.html:64`).
- E2E-008 (parte) contadores da Mesa como filtros — `minha_etapa.html:66-73` (o nome continua em AV-40).
- "Distribuição sem nome do candidato" (P2 da auditoria de 13/09) — coluna "Participante" (`distribuicao.html:368`).
- L08-59 / RC-146 números da ocupação espremidos — 055 (`41d22bb5`).
- L05-95 `convocacao.html` sem acentos — só nos comentários do template; o texto visível está acentuado.
- 013 T063 (375 px) — coberta por `tests/interface/test_polish_da_058.py`; só a marcação em `tasks.md` ficou aberta.
- E2E-019 avaliadora vê processo alheio — RC-97 DESCARTADA (obsoleta) na auditoria de 26/09.
- E2E-017 distribuir com período aberto — invariante (PR #32, `conjunto.py`); a corrida restante está em AV-42.
- D-G3 / R-7 fonte externa do sorteio — decidido (19/09) e exigido pela 035; a consulta "à base de produção" (PR #188) não tem objeto enquanto não houver produção.

### GO

- **`--dry-run` expunha senha (A3 do parecer de 29/08, L01-37)** — `ps/seguranca/management/commands/provisionar_papeis.py:26-32` mascara `PASSWORD '…'` (`SEGREDO_EM_SQL`).
- **`institutionalCode` com 101 caracteres → 500 (A4, L01-37)** — `ps/processos/api/serializers.py:14` (`max_length=100`).
- **CSRF não fiscalizado (L01-34)** — resolvido pela 003 (mesma sessão, 29/08).
- **`EMAIL_TIMEOUT` ausente (I-4 em parte)** — `config/settings/base.py:197` (066); só `EMAIL_USE_SSL` segue (GO-25).
- **Encerrar Processo sem Editais finais (FR-034, RC-118, L01-05) e período `CANCELADO` recebendo (RC-119)** — #220/#221, `registration_period_cancelled`; `processo_detalhe.html:252-255`.
- **Sem tela para segundo Edital no Processo (H.17, E2E17-007, L04-42, L05-51)** — `criar_edital` (`ps/interface/views.py:415`), PR #119.
- **"Abrir a Supervisão" oferecido a todos com 404 (N-03, L06-54, L07-39)** — PR #152.
- **Atenção afirma "nenhuma condição" e sinais sem "a quem pedir" (N-01/N-04, RC-78, RC-81, L06-33)** — 045 (#187).
- **`schedule.status` derivado que nada deriva (RC-80, L06-35)** — 045 (#187).
- **Publicador sem caminho, 404 mudo (ACH-40/35, L06-51)** — 033.
- **Visão Geral sem caminho de volta (L09-35)** — PR #252.
- **`make lint` só com `ruff check` (L01-22, L02-11, L03-03)** — `backend/Makefile` alvo `lint` com os dois passos (015 T123, #23).
- **CI duas vezes por commit / run superada não cancelada (L06-55)** — PR #154 (`concurrency.cancel-in-progress`).
- **Validação em PostgreSQL 16 contra 18 da spec (L01-10)** — CI usa `postgres:18` (`.github/workflows/backend.yml:36,93`).
- **`wsgi`/`asgi` apontando para `development` (CD-5)** — #204.
- **`ValorDeFato` append-only por uma camada só (RC-101, L08-07)** — #183, `ps/inscricoes/migrations/0006_valor_de_fato_append_only.py`.
- **Fixtures com datas fixas derrubando a `main` (L08-84) e a data de 20/11 em `test_limite_de_campos_da_composicao.py` (L09-05)** — #238; grep de `2026-11` no arquivo vazio em 15/10.
- **Teste que confira a tabela do README contra `specs/` (L05-43)** — `backend/tests/test_readme_acompanha_o_codigo.py` (`325b57d4`).
- **Guia sem `sincronizar_unidades`; README com módulos duplicados (L09-77)** — PR #271/#272.
- **Roteiros de troca do assistente e do correio (L10-54, P-1..P-3, P-7, P-8)** — PR #281.
- **"Unidade: CEFOR" em caixa alta na vitrine** — 072 (`ps/portal/views.py:364-406`, FR-1605).
- **`DJANGO_DEBUG` não lido no `.env.example` (M-8)** — removido em 14/10.
- **Limite de corpo do proxy não declarado (achado 15, L08-68)** — o guia fixa `client_max_body_size 3m` (`doc/implantacao-em-producao-ubuntu.md:1413`); configuração versionada é parte de GO-23.
- **Pulso visível a presidente sem `inscricao:consultar` (L04-63)** — comportamento especificado: FR-004a da 022 (`specs/022-*/spec.md:436`) manda não suprimir o Pulso; supressão é por sinal (`views.py:4959-4962`).
- **Suspeita de que a segregação impediria equipe de duas pessoas** — `publish_edital.py:705-710` só recusa quando a mesma pessoa elaborou **e** homologou; a tabela do manual §A.3 fecha com duas.
- **Contagens do CLAUDE.md/AGENTS.md vencidas em 09/09–20/09 (L05-18, L06-56, L07-79)** — PR #153 e atualizações seguintes; a deriva atual (11263 × 11297, 90 × 94) está em GO-42.

### AS

- Especificar a 071 (L10-19) — sessão 7bf91059; PR #278 mergeado em 14/10.
- Roteiros de troca OpenRouter↔Ollama e do correio (L10-54; P-1, P-2, P-3, P-7, P-8) — `doc/troca-do-servico-do-assistente.md` e §16.5 do guia, PR #281 mergeado.
- DA-11, DA-03, DA-04, DA-05, DA-06, DA-07 da auditoria — resolvidos pela 070/071 (doc-achados c.12).
- Encaminhamento sem canal e itens de redação 2–6 da validação da 070 — `049353a6`.
- P-07 e respostas cujo essencial está em anexo → "Depende da leitura" — 070 D-011 (#274).
- Texto do 429 confundido com o limite do piloto — `LIMITE_DO_SERVICO` com texto próprio (#279).
- Acréscimo de tokens fixo por chamada — `ASSISTENTE_TOKENS_POR_CHAMADA` (#279).
- Roteamento do OpenRouter para provedor que recusava — `ASSISTENTE_PROVEDOR` fixa o provedor e o log registra qual (#279).
- Fontes do piloto sem as seções que nenhuma pergunta mostra — 071 R-002 manda toda seção inteira (verificacao §6); o resíduo da 070 está em AS-20.
- OpenRouter em produção — `production.py:205` só aceita `ollama`.
- `EMAIL_TIMEOUT` ausente (#236) — existe em `config/settings/base.py:197`.
- Contrato da 029 citando Q-3 (L07-80) — trocado por D-001 na 55ee1319.
- Destaque da vaga em link de campanha (Q5) — `.perfil:target` em `portal/templates/portal/base.html:315` (072).
- "Agendador do job mensal da CEP e canal do alerta não existem" (L07-08) — passou a existir como receita no guia (`ps-ceps.timer`, `OnFailure=ps-alerta`); o resto está em AS-25.
- Sete dos oito achados do code review da 074 — corrigidos na worktree (o 8º aceito); o conjunto segue em AS-12.
- "Arquivo de resultado de rodada gravado dentro do ambiente virtual" (L10-39) — deslize de sessão; nada da rodada está versionado (`specs/071-…/avaliacao/` não existe).
- Flaky `test_ocupacao.py` e `test_database_permissions.py` (L10-40, L10-41) — não são desta área (testes/CI).
- Versão de Retificação que não lista a publicação original (L10-68) — contornado na 070 (lê a original sempre); a causa é da área de Edital/publicação.

