<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0 -> 1.1.1
- Motivo do MINOR (1.1.0): princípio novo acrescentado; nenhum princípio existente foi removido ou
  redefinido, e nenhuma garantia anterior foi enfraquecida.
- Motivo do PATCH (1.1.1): "interface do produto" era leitura estreita demais. O produto tem mais
  de um canal — a interface administrativa serve quem elabora, a API pública serve quem consulta —
  e a redação anterior tornaria indemonstrável, por definição, qualquer jornada cujo ator não use
  navegador. A exigência passa a ser o canal destinado ao ator daquela jornada, sem perder o dente:
  continua vedado demonstrar por chamada manual o que o canal do ator não oferece.
- Origem: revisão de produto de 2026-08-30 sobre as telas da `002`, verificada contra o
  repositório. As specs `003`, `004` e `005` nasceram, cada uma, do limite registrado pela
  anterior — a função objetivo que a Constituição declarava era completa em integridade e omissa
  em jornada, e o processo a otimizou corretamente. O princípio VI fecha essa omissão.
- Added sections:
  - VI. Completude de Jornada e Valor Demonstrável
- Modified principles: nenhum
- Modified sections:
  - Fluxo de Desenvolvimento e Critérios de Qualidade — a lista de conclusão de funcionalidade
    passa a exigir o cenário demonstrável do princípio VI.
- Removed sections: nenhuma
- Impacto nos artefatos vigentes: `001` a `005` permanecem conformes; o princípio VI não é
  retroativo e não reabre feature concluída. A `006` já nasce sob ele — suas entregas são
  demonstráveis no navegador e seu `SC-009` é o cenário de ponta a ponta exigido.
- Plano de adequação: nenhum necessário. A exigência incide sobre especificações abertas a partir
  desta data.
- Templates dependentes: não modificados; leem a Constituição em tempo de execução.
- Aprovação institucional: 1.1.1 aprovada em 2026-08-30, conforme exigido pela Governance.
- Follow-up TODOs: nenhum
-->
# Constituição do Sistema de Gestão de Processos Seletivos

## Core Principles

### I. Linguagem Ubíqua e Integridade do Domínio

O projeto DEVE adotar linguagem ubíqua única e consistente. Conceitos jurídicos,
administrativos e acadêmicos DEVEM possuir significado inequívoco e equivalente em
especificações, código, APIs, banco de dados, testes, documentação e interfaces. Termos
diferentes NÃO DEVEM representar o mesmo conceito sem justificativa documentada. A estrutura
das telas NÃO DEVE determinar artificialmente a estrutura do domínio.

Processo Seletivo, Edital, Versão de Edital, Retificação, Publicação, Perfil de Vaga, Vaga,
Cadastro Reserva, Cronograma, Evento de Cronograma, Etapa de Avaliação, Critério de Avaliação,
Modalidade de Cota, Documento Exigido, Inscrição, Candidato, Comissão, Presidente da Comissão,
Autoridade Signatária, Recurso, Avaliação, Classificação, Resultado e Cancelamento DEVEM ser
conceitos distintos quando seus significados ou ciclos de vida forem distintos.

Entidades DEVEM possuir identificadores estáveis; identificadores públicos NÃO DEVEM conferir
autorização. Relacionamentos DEVEM preservar integridade referencial. Invariantes persistentes
DEVEM usar constraints e índices quando aplicável. Registros normativos, publicados, históricos
ou auditáveis NÃO DEVEM ser fisicamente excluídos quando isso comprometer rastreabilidade.

Racional: linguagem e invariantes estáveis impedem que detalhes de interface ou persistência
alterem o significado jurídico e administrativo do sistema.

### II. Integridade Normativa, Imutabilidade e Temporalidade

Cada informação normativa estruturada DEVE possuir uma única fonte autoritativa. Vagas, perfis,
cronogramas, cotas, requisitos, documentos, etapas, critérios, pesos, pontuações e regras de
avaliação NÃO DEVEM existir como dados independentes e divergentes. Editais, relatórios, telas e
PDFs DEVEM derivá-los da fonte estruturada quando tecnicamente aplicável. Divergência entre a
configuração homologada e o documento DEVE impedir a publicação.

Toda Publicação DEVE ser histórica e imutável. Um Edital publicado NÃO PODE ser sobrescrito,
apagado ou silenciosamente modificado. Uma Retificação PODE alterar qualquer conteúdo normativo
futuro, mas NÃO PODE apagar ou reescrever Publicação anterior. O sistema DEVE preservar a
publicação original, cada retificação e versão consolidada, autoria, datas, efeitos, documentos
gerados e histórico completo.

O estado normativo vigente em qualquer instante relevante DEVE ser reproduzível. Para cada
Inscrição, Avaliação, Recurso, Classificação ou Resultado, DEVE ser possível determinar Processo
Seletivo, Edital, versão, retificações, cronograma, requisitos, documentos, cotas, etapas,
critérios, pesos e regras então vigentes. Regras atuais NÃO PODEM substituir regras históricas.
Toda alteração DEVE registrar vigência, versão, autoria e efeitos.

Instantes DEVEM ser persistidos explicitamente, sem dependência do fuso do servidor. Regras de
calendário DEVEM usar a zona temporal institucional definida pelo domínio; operações relacionadas
DEVEM compartilhar referência temporal consistente na mesma transação.

Racional: atos com efeitos administrativos e jurídicos exigem origem, integridade e vigência
demonstráveis.

### III. Segurança, Proteção de Dados e Auditoria

O sistema DEVE negar acesso por padrão. Permissões DEVEM ser explícitas, validadas no backend e
limitadas pelo menor privilégio. Controles DEVEM impedir IDOR e acesso obtido somente pela
manipulação de identificadores. Criação, edição, revisão, homologação, publicação, retificação,
cancelamento, avaliação, julgamento de recurso e divulgação de resultado DEVEM exigir autorização
específica quando aplicáveis.

O modelo de autorização DEVE representar responsabilidades e permissões, sem acoplamento rígido
a um cargo. O Presidente da Comissão é inicialmente responsável pela gestão operacional, mas a
Autoridade Signatária PODE ser outra pessoa, como Diretor-Geral ou Reitor. Mesmo sem assinatura
eletrônica, atos normativos DEVEM registrar autoria, Autoridade Signatária, cargo ou função,
responsável pela operação, data, hora e versão.

Dados pessoais DEVEM obedecer a necessidade, finalidade e minimização. Dados sensíveis e
documentos comprobatórios DEVEM ter acesso restrito. Logs e auditoria NÃO DEVEM expor conteúdo
sensível desnecessário. Cada especificação DEVE avaliar os requisitos aplicáveis da LGPD.

Operações sensíveis DEVEM gerar auditoria com ator, ação, entidade, identificador, data e hora,
estado anterior e posterior, motivo, versão e contexto, quando aplicável. Eventos de auditoria NÃO
PODEM ser silenciosamente alterados ou excluídos pela aplicação e DEVEM permitir investigação e
reconstrução histórica.

Racional: proteção por padrão, segregação de responsabilidades e evidências invioláveis preservam
direitos, dados pessoais e responsabilização institucional.

### IV. Regras Explícitas e Consistência Operacional

Regras que afetem direitos, elegibilidade, documentação, cotas, publicação, estados, pontuação,
eliminação, classificação, recursos ou autorização DEVEM residir e ser verificadas no
domínio/backend. Validações no frontend PODEM melhorar a experiência, mas NÃO são fronteira de
segurança nem autoridade final. Validação de entrada NÃO substitui invariantes de domínio.

Entidades com ciclo de vida relevante DEVEM possuir estados e transições explícitos. Flags
booleanas dispersas NÃO DEVEM representar workflows complexos quando uma máquina de estados for
adequada. Transições inválidas DEVEM ser rejeitadas. Estados detalhados de Processo Seletivo,
Edital, Publicação, Inscrição, Avaliação, Recurso e outros agregados DEVEM ser definidos nas
respectivas especificações.

Publicar um Edital DEVE ser operação explícita de domínio, nunca simples alteração booleana. A
operação DEVE validar inconsistências, classificá-las como informação, aviso ou erro impeditivo e
bloquear a publicação diante de erro impeditivo. A Publicação DEVE provar conteúdo, autoria e
momento da operação.

Operações que alterem estado normativo ou produzam efeitos administrativos DEVEM ser
transacionalmente consistentes. Especificações e planos DEVEM tratar riscos de concorrência como
perda de atualização, versão publicada incorreta, duplicidade, classificação inconsistente,
julgamento conflitante ou uso de dados obsoletos, com controles proporcionais ao risco.

Racional: decisões críticas precisam ser uniformes, atômicas e resistentes a requisições inválidas
ou concorrentes.

### V. Qualidade, Rastreabilidade e Simplicidade

Requisitos críticos DEVEM ser rastreáveis entre especificação, plano, tarefas, implementação e
testes. Implementação NÃO PODE contradizer deliberadamente a especificação vigente. Divergências
DEVEM ser resolvidas explicitamente; comportamento acidental NÃO PODE virar regra sem decisão
documentada.

Regras críticas DEVEM possuir testes automatizados no nível adequado, incluindo, conforme
aplicável, testes de domínio, serviços, persistência, integração, autorização, API e end-to-end.
Publicação, retificação, temporalidade, cotas, documentos, elegibilidade, avaliação, pontuação,
recursos, classificação, autorização e concorrência DEVEM ter cobertura específica. Correções
relevantes DEVEM incluir teste de regressão quando tecnicamente possível.

A arquitetura DEVE preferir a solução mais simples que preserve os requisitos. Microsserviços,
mensageria, event sourcing, CQRS ou complexidade equivalente EXIGEM necessidade demonstrável na
especificação ou plano. Simplicidade NÃO PODE eliminar histórico, auditoria, segurança,
versionamento, integridade normativa, testes ou consistência transacional.

Falhas relevantes DEVEM ser diagnosticáveis sem exposição indevida. Logs DEVEM conter contexto e
correlação suficientes e relacionar-se à auditoria quando necessário. Respostas ao cliente NÃO
DEVEM revelar stack traces, credenciais, tokens ou detalhes internos sensíveis.

Racional: qualidade rastreável reduz regressões; simplicidade justificada preserva a evolução sem
sacrificar garantias essenciais.

### VI. Completude de Jornada e Valor Demonstrável

Toda funcionalidade DEVE ampliar uma capacidade observável na jornada de um usuário real.
Infraestrutura, validação, auditoria, integridade, versionamento e mecanismos internos são
requisitos de qualidade da capacidade entregue e NÃO PODEM substituí-la. Uma capacidade que o
domínio sustenta mas que nenhuma interface alcança NÃO DEVE ser considerada entregue.

Uma especificação somente DEVE ser considerada concluída quando existir cenário demonstrável de
ponta a ponta no qual o usuário realiza ação nova ou completa de maneira significativamente melhor
uma ação existente. O cenário DEVE ser executável pelo canal destinado ao ator daquela jornada — a
interface administrativa para quem elabora, a API pública para quem consulta — sem manipulação de
banco, sem shell e sem recurso a canal alheio ao ator. Demonstrar por chamada manual aquilo que o
canal do ator não oferece NÃO satisfaz esta exigência.

Trabalho exclusivamente técnico PODE existir quando necessário para desbloquear jornada já
identificada, mas DEVE declarar explicitamente qual capacidade de produto desbloqueia e NÃO DEVE
gerar autonomamente a prioridade da especificação seguinte.

O backlog subsequente DEVE derivar prioritariamente das jornadas e objetivos do produto, e NÃO DEVE
derivar automaticamente dos itens `Out of Scope`, dívidas ou casos de borda da funcionalidade
imediatamente anterior. Limites registrados são insumo de priorização, nunca a priorização em si.

Racional: rigor sem jornada produz regras impecavelmente testadas sobre um fluxo principal
inexistente; a prioridade é do produto, e a integridade é como ele se sustenta — não o que ele
entrega.

## Restrições e Invariantes do Domínio

- Um Processo Seletivo DEVE possuir ao menos um Edital e PODE possuir vários. Cada Edital DEVE
  pertencer a exatamente um Processo Seletivo. Esses conceitos NÃO PODEM ser sinônimos.
- Um Edital PODE abranger múltiplos Perfis de Vaga. Editais do mesmo Processo Seletivo PODEM ter
  cronogramas independentes. Cada Perfil PODE definir código, denominação ou especialidade, vagas,
  Cadastro Reserva limitado ou ilimitado, requisitos, documentos, cotas, etapas e critérios.
- Um Candidato PODE realizar Inscrições distintas para mais de um Perfil do mesmo Edital, salvo
  restrição expressa do Edital.
- Regras sujeitas a legislação NÃO DEVEM ser permanentemente hard-coded quando passíveis de
  mudança. Cotas DEVEM ser definidas por Perfil e, quando necessário, versionar modalidade,
  fundamento, percentual, cálculo, arredondamento, distribuição e vigência. Mudança futura NÃO
  PODE alterar Edital publicado.
- Documentos Exigidos PODEM variar por Edital, Perfil, modalidade, etapa e condição normativa. O
  sistema DEVE reproduzir os documentos exigidos para cada Inscrição. Cotas PODEM exigir
  documentação comprobatória adicional.
- Perfis PODEM possuir Etapas distintas. Cada Etapa PODE definir ordem, peso, notas mínima e
  máxima, caráter eliminatório ou classificatório, banca, critérios, pontuação e acumulação. Essas
  regras DEVEM existir no domínio/backend e ser testadas.
- Modelos reutilizáveis DEVEM ser apenas origem controlada. Alterá-los NÃO PODE modificar
  retroativamente instâncias incorporadas por Edital; estas DEVEM preservar independência e versão.
- Cada Edital DEVE ter Cronograma próprio e estruturado em Eventos. Eventos PODEM registrar início,
  término, tipo, visibilidade e vínculo com etapas. Inconsistências determináveis DEVEM ser
  rejeitadas. Alterações após Publicação DEVEM ocorrer por Retificação.
- O PDF DEVE derivar dos dados estruturados e conteúdo homologado e corresponder exatamente à
  versão homologada. A cadeia "dados estruturados -> versão homologada -> PDF publicado" DEVE ser
  demonstrável. O documento DEVE ter identificação, versão e, quando apropriado, hash
  criptográfico.
- Cancelamento DEVE ser ato de domínio, nunca exclusão, preservando motivo, responsável, data e
  hora, ato correspondente, Publicações e histórico quando aplicável.
- APIs DEVEM ter contratos explícitos. Entidades de persistência NÃO DEVEM ser contratos públicos.
  Entradas e saídas DEVEM usar DTOs, commands e responses; erros relevantes DEVEM ser documentados.
- Mudanças persistentes DEVEM usar migrations versionadas. Migrations aplicadas NÃO PODEM ser
  reescritas; correções DEVEM usar novas migrations.

## Fluxo de Desenvolvimento e Critérios de Qualidade

O projeto DEVE usar GitHub Spec Kit e desenvolvimento orientado por especificações. Incrementos
DEVEM seguir: Constituição; Especificação; Clarificação quando necessária; Planejamento; Tarefas;
Análise de consistência; Implementação; e Convergência. Implementação substancial NÃO DEVE começar
antes de especificação clara e plano aprovado, salvo correção emergencial justificada.

Especificações DEVEM concentrar-se no que e por quê. Linguagem, framework, banco, infraestrutura e
bibliotecas DEVEM ser decididos no plano técnico, salvo restrição institucional permanente.
Escolhas tecnológicas desnecessárias NÃO DEVEM entrar na especificação funcional.

Revisões DEVEM verificar conformidade constitucional. Exceções e complexidade adicional DEVEM ser
justificadas. Antes da implementação, a análise de consistência DEVE identificar contradições e
lacunas entre os artefatos vigentes.

Interfaces DEVEM priorizar clareza, consistência, prevenção de erro, feedback, acessibilidade,
teclado, legibilidade e mensagens compreensíveis. Wizard de Edital DEVE organizar a experiência e
NÃO PODE limitar o domínio. Operações irreversíveis ou juridicamente relevantes DEVEM apresentar
confirmação e consequências inequívocas.

Uma funcionalidade somente PODE ser concluída quando, conforme aplicável: requisitos e invariantes
forem atendidos; autorização validada; migrations aplicáveis; testes aprovados; documentação e
contratos atualizados; auditoria implementada; inexistirem regressões críticas conhecidas; existir o
cenário demonstrável exigido pelo princípio VI; e todos os artefatos estiverem consistentes.
Compilar ou atender apenas ao cenário principal NÃO basta, e suíte aprovada sem cenário demonstrável
também NÃO basta.

## Governance

Esta Constituição é a autoridade de engenharia e domínio do projeto. Especificações, planos,
tarefas e implementações DEVEM obedecê-la. Em conflito, ela prevalece até alteração formal.

Toda alteração constitucional DEVE ser explícita e justificada; identificar impactos nos artefatos
e implementações existentes; incluir plano de adequação ou justificar sua dispensa; atualizar a
versão semântica, a data e o Sync Impact Report; e receber revisão de consistência e aprovação
institucional antes da adoção.

O versionamento DEVE usar MAJOR para remoção ou redefinição incompatível de princípios, MINOR para
novo princípio ou expansão material e PATCH para esclarecimento sem mudança semântica. A data de
ratificação original DEVE permanecer; a última alteração DEVE refletir a emenda mais recente.

Planos e revisões de implementação DEVEM conter verificação constitucional. Violação sem
justificativa aprovada DEVE bloquear o incremento. A conformidade DEVE ser reavaliada em cada
análise de consistência e antes da conclusão de funcionalidade.

**Version**: 1.1.1 | **Ratified**: 2026-08-27 | **Last Amended**: 2026-08-30
