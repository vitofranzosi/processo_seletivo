# Constituição do Sistema de Gestão de Processos Seletivos

Crie a Constituição v1.0.0 deste projeto utilizando o mecanismo oficial do GitHub Spec Kit.

A Constituição deve estabelecer princípios arquiteturais, de domínio, segurança, integridade normativa, rastreabilidade, qualidade e governança que serão obrigatórios em todas as futuras especificações, planos, tarefas e implementações.

Não implemente funcionalidades nesta etapa.

## 1. Contexto do sistema

O sistema será uma plataforma institucional para gestão de processos seletivos.

O domínio está organizado inicialmente em três grandes módulos:

1. Processo Seletivo e Editais;
2. Inscrições de Candidatos;
3. Avaliação, Recursos, Classificação e Resultados.

O primeiro módulo a ser especificado e implementado posteriormente será **Processo Seletivo e Editais**.

A Constituição, entretanto, deve estabelecer princípios válidos para todo o sistema.

## 2. Linguagem do domínio

Adote uma linguagem ubíqua consistente.

Conceitos jurídicos, administrativos e acadêmicos devem possuir significado único e inequívoco em especificações, código, API, banco de dados, testes, documentação e interface.

Não utilizar termos diferentes para representar o mesmo conceito de negócio sem justificativa explícita.

Distinguir obrigatoriamente, entre outros:

* Processo Seletivo;
* Edital;
* Versão de Edital;
* Retificação;
* Publicação;
* Perfil de Vaga;
* Vaga;
* Cadastro Reserva;
* Cronograma;
* Evento de Cronograma;
* Etapa de Avaliação;
* Critério de Avaliação;
* Modalidade de Cota;
* Documento Exigido;
* Inscrição;
* Candidato;
* Comissão;
* Presidente da Comissão;
* Autoridade Signatária;
* Recurso;
* Avaliação;
* Classificação;
* Resultado;
* Cancelamento.

A estrutura das telas não deve determinar artificialmente a estrutura do domínio.

## 3. Processo Seletivo e Edital são conceitos distintos

Um Processo Seletivo deve possuir no mínimo um Edital e pode possuir múltiplos Editais.

Cada Edital pertence a exatamente um Processo Seletivo.

Um mesmo Edital pode abranger múltiplos Perfis de Vaga.

Editais pertencentes ao mesmo Processo Seletivo podem possuir cronogramas independentes.

O modelo de domínio não deve tratar Processo Seletivo e Edital como sinônimos.

## 4. Integridade normativa e fonte única da verdade

Informações normativas estruturadas devem possuir uma única fonte autoritativa.

Dados como:

* vagas;
* perfis;
* cronograma;
* cotas;
* requisitos;
* documentos;
* etapas;
* critérios;
* pesos;
* pontuações;
* regras de avaliação;

não devem ser duplicados como informações independentes em diferentes partes do sistema.

Quando essas informações aparecerem no edital, relatórios, telas ou PDF, devem ser derivadas da fonte estruturada correspondente sempre que tecnicamente aplicável.

O sistema deve impedir divergências entre configuração estruturada e documento publicado.

## 5. Publicações são historicamente imutáveis

Toda publicação realizada deve ser permanentemente preservada.

Um Edital publicado não pode ser sobrescrito ou silenciosamente modificado.

A imutabilidade se aplica ao registro histórico publicado, e não ao conteúdo normativo futuro.

Uma Retificação pode alterar qualquer conteúdo do Edital, incluindo, mas não se limitando a:

* identificação;
* cronograma;
* perfis;
* vagas;
* cadastro reserva;
* requisitos;
* documentos;
* cotas;
* etapas;
* critérios;
* pesos;
* cláusulas;
* anexos.

Entretanto, uma Retificação nunca pode apagar ou reescrever a publicação anterior.

O sistema deve preservar:

* publicação original;
* cada retificação;
* cada versão consolidada;
* autoria;
* datas;
* efeitos;
* documentos gerados;
* histórico completo das alterações.

## 6. Temporalidade e reprodutibilidade jurídica

O sistema deve permitir reconstruir integralmente o estado normativo vigente em qualquer instante relevante.

Deve ser possível determinar, para uma determinada inscrição, avaliação, recurso, classificação ou resultado:

* qual Processo Seletivo;
* qual Edital;
* qual versão;
* quais retificações;
* qual cronograma;
* quais requisitos;
* quais documentos;
* quais regras de cotas;
* quais etapas;
* quais critérios;
* quais pesos;
* quais regras de classificação;

estavam vigentes naquele momento.

Regras atuais nunca devem substituir retroativamente regras históricas.

Toda alteração normativa deve possuir temporalidade e rastreabilidade suficientes para permitir reprodução histórica.

## 7. Legislação e regras configuráveis

Regras sujeitas a legislação ou regulamentação não devem ser permanentemente hard-coded quando forem passíveis de mudança normativa.

Isso se aplica especialmente às ações afirmativas e cotas.

As cotas são definidas por Perfil de Vaga e devem atender à legislação e regulamentação vigentes aplicáveis ao processo.

Quando necessário, o sistema deve permitir representar e versionar:

* modalidade;
* fundamento normativo;
* percentual;
* regra de cálculo;
* regra de arredondamento;
* regra de distribuição;
* vigência;
* versão.

A alteração futura de uma regra legal não pode modificar retroativamente um Edital já publicado.

## 8. Perfis de Vaga

Um Edital pode possuir múltiplos Perfis de Vaga.

Cada perfil pode possuir independentemente:

* código;
* denominação/especialidade;
* vagas imediatas;
* cadastro reserva;
* requisitos;
* documentos;
* cotas;
* etapas de avaliação;
* critérios e demais regras aplicáveis.

O cadastro reserva pode ser limitado ou ilimitado.

Um candidato poderá realizar inscrições distintas para mais de um Perfil de Vaga do mesmo Edital, desde que as regras específicas do Edital não determinem restrição diferente.

## 9. Documentação contextual

Os documentos exigidos podem variar conforme:

* Edital;
* Perfil de Vaga;
* modalidade de concorrência/cota;
* etapa;
* outras condições normativas.

Modalidades de cotas podem exigir documentação complementar destinada à comprovação da condição declarada.

O sistema deve ser capaz de determinar de maneira reproduzível quais documentos eram exigidos para determinada inscrição.

## 10. Etapas e critérios de avaliação

Perfis de Vaga podem possuir etapas de avaliação distintas.

Uma etapa pode ser obrigatória para determinados perfis e inexistente para outros.

Etapas podem possuir:

* ordem;
* peso;
* nota mínima;
* nota máxima;
* caráter eliminatório;
* caráter classificatório;
* banca/responsáveis;
* critérios;
* regras de pontuação;
* regras de acumulação.

Regras de avaliação que influenciem elegibilidade, eliminação, pontuação ou classificação devem existir no domínio/backend e possuir testes automatizados.

Não permitir que regras críticas existam exclusivamente no frontend.

## 11. Reutilização segura de modelos

Cronogramas, etapas, critérios, documentos, cláusulas e outros elementos poderão possuir modelos reutilizáveis.

A reutilização deve funcionar como origem controlada para criação/configuração.

Alterar posteriormente um modelo reutilizável não pode modificar retroativamente processos ou editais que já tenham incorporado aquele modelo.

Instâncias utilizadas por um Edital devem possuir independência e versionamento suficientes para preservar sua história.

## 12. Cronograma

Cada Edital deve possuir cronograma próprio.

O cronograma deve ser estruturado em eventos.

Eventos podem possuir início, término, tipo, visibilidade, relacionamento com etapas e demais propriedades necessárias ao domínio.

Alterações do cronograma depois da publicação devem ocorrer por Retificação.

As regras devem impedir cronogramas temporal ou logicamente inconsistentes quando essas inconsistências puderem ser determinadas automaticamente.

## 13. Workflow e máquina de estados

Entidades com ciclo de vida relevante devem possuir estados e transições explícitos.

Não utilizar conjuntos dispersos de flags booleanas para representar workflows complexos quando uma máquina de estados for semanticamente adequada.

Transições inválidas devem ser rejeitadas pelo domínio.

Processo Seletivo, Edital, Publicação, Inscrição, Avaliação, Recurso e demais agregados relevantes devem possuir ciclos de vida explícitos quando aplicável.

A definição detalhada dos estados será feita nas respectivas especificações.

## 14. Publicação como operação de domínio

Publicar um Edital não deve ser tratado como simples alteração de um campo booleano.

A publicação deve ser uma operação explícita de domínio precedida por validação.

Antes da publicação, o sistema deve ser capaz de identificar inconsistências e classificá-las adequadamente, por exemplo:

* informação;
* aviso;
* erro impeditivo.

Erros impeditivos devem bloquear a publicação.

A publicação deve registrar informações suficientes para comprovar o conteúdo publicado e sua autoria.

## 15. PDF estruturado

O Edital será gerado pelo sistema em PDF a partir das informações estruturadas e conteúdo editorial homologado.

O PDF publicado deve corresponder exatamente à versão homologada.

Deve ser possível demonstrar a correspondência entre:

dados estruturados → versão homologada → PDF publicado.

O documento publicado deve possuir identificação/versionamento adequado e mecanismo de integridade, como hash criptográfico, quando tecnicamente apropriado.

## 16. Autoria, homologação e autoridade signatária

O sistema deve distinguir responsabilidades institucionais.

O Presidente da Comissão do Processo Seletivo é inicialmente o principal responsável pela gestão operacional do certame.

A autoridade que formalmente assina o Edital poderá ser diferente do Presidente da Comissão, normalmente o Diretor-Geral do Campus ou o Reitor, conforme o caso.

Inicialmente não é obrigatória integração com assinatura eletrônica real do PDF.

Mesmo sem assinatura eletrônica, o sistema deve registrar:

* autoria;
* autoridade signatária;
* cargo/função;
* responsável pela operação;
* data e hora;
* versão publicada.

O modelo de autorização deve ser baseado em responsabilidades/permissões, evitando regras rígidas acopladas a um único cargo.

## 17. Cancelamento

Processos Seletivos e/ou Editais poderão ser cancelados quando permitido pelas regras aplicáveis.

Cancelamento é um ato de domínio e não uma exclusão.

Devem ser preservados, quando aplicável:

* motivo;
* responsável;
* data/hora;
* ato/documento correspondente;
* publicação anterior;
* histórico.

Nenhuma publicação histórica deve ser apagada em decorrência do cancelamento.

## 18. Auditoria obrigatória

Operações sensíveis devem possuir auditoria.

A auditoria deve registrar, quando aplicável:

* ator;
* ação;
* entidade;
* identificador;
* data/hora;
* estado anterior;
* estado posterior;
* motivo;
* versão;
* origem/contexto da operação.

Eventos de auditoria não podem ser silenciosamente alterados ou excluídos por operações comuns da aplicação.

A auditoria deve permitir investigação administrativa e reconstrução histórica.

## 19. Segurança e autorização

Aplicar segurança por padrão.

Toda operação deve assumir acesso negado até que exista autorização explícita.

Autorizações devem ser validadas no backend.

A aplicação deve proteger contra IDOR e impedir acesso a recursos apenas pela descoberta ou manipulação de identificadores.

Privilégios devem seguir o princípio do menor privilégio.

Operações críticas devem possuir autorização explícita, incluindo, quando aplicável:

* criação;
* edição;
* revisão;
* homologação;
* publicação;
* retificação;
* cancelamento;
* avaliação;
* julgamento de recurso;
* divulgação de resultado.

## 20. Proteção de dados

Dados pessoais de candidatos devem ser tratados segundo princípios de necessidade, finalidade e minimização.

Informações sensíveis e documentos comprobatórios devem possuir acesso restrito.

Logs e auditoria não devem expor conteúdo sensível desnecessariamente.

A arquitetura futura deve considerar requisitos aplicáveis da LGPD.

## 21. Consistência transacional e concorrência

Operações que alterem estado normativo ou produzam efeitos administrativos devem ser transacionalmente consistentes.

Concorrência deve ser tratada explicitamente onde alterações simultâneas possam provocar:

* perda de atualização;
* publicação de versão incorreta;
* duplicidade;
* classificação inconsistente;
* julgamento conflitante;
* alteração de dados obsoletos.

Utilizar mecanismos adequados de controle de concorrência e versionamento.

## 22. Identificadores e integridade referencial

Entidades de domínio devem possuir identificadores estáveis.

Identificadores públicos não devem transmitir autorização.

Relacionamentos devem preservar integridade referencial.

Exclusão física de registros normativos, históricos, publicados ou auditáveis deve ser evitada quando comprometer rastreabilidade.

## 23. Data, hora e temporalidade

Decisões de data e hora devem ser explícitas.

Persistência de instantes deve preservar informação temporal adequada e evitar dependência implícita do fuso horário do servidor.

Regras de negócio dependentes de calendário devem utilizar a zona temporal institucional definida pelo domínio quando necessário.

Operações relacionadas devem utilizar referência temporal consistente dentro da mesma transação.

## 24. Contratos explícitos

APIs devem utilizar contratos explícitos.

Entidades de persistência não devem constituir diretamente contratos públicos da API.

Entradas e saídas devem possuir DTOs/commands/responses apropriados.

Validações de entrada não substituem invariantes de domínio.

Contratos devem documentar erros relevantes e permanecer consistentes com a especificação.

## 25. Evolução do banco de dados

Toda alteração estrutural persistente deve ocorrer por migrations versionadas.

Migrations aplicadas não devem ser reescritas.

Correções posteriores devem ser feitas por novas migrations.

Integridade, constraints e índices relevantes devem ser utilizados também no banco de dados quando representarem invariantes persistentes.

## 26. Qualidade e testes obrigatórios

Regras de negócio críticas devem possuir testes automatizados.

O projeto deve adotar estratégia em camadas, incluindo conforme aplicável:

* testes unitários de domínio;
* testes de serviços;
* testes de persistência;
* testes de integração;
* testes de autorização;
* testes de API;
* testes end-to-end para fluxos críticos.

Devem existir testes específicos para regras que afetem:

* publicação;
* retificação;
* temporalidade;
* cotas;
* documentos;
* elegibilidade;
* avaliação;
* pontuação;
* recursos;
* classificação;
* autorização;
* concorrência.

Correção de defeitos relevantes deve incluir teste de regressão sempre que tecnicamente possível.

## 27. Rastreabilidade requisito → implementação → teste

Requisitos críticos devem ser rastreáveis entre:

especificação → plano → tarefas → implementação → testes.

Nenhuma implementação deve deliberadamente contradizer a especificação vigente.

Quando implementação e especificação divergirem, a inconsistência deve ser resolvida explicitamente, evitando transformar comportamento acidental do código em regra de negócio sem decisão documentada.

## 28. Backend como autoridade das regras críticas

O frontend pode realizar validações para melhorar a experiência do usuário, mas não constitui fronteira de segurança nem autoridade final de regras de negócio.

Regras que afetem direitos ou resultados devem ser verificadas pelo backend.

Isso inclui especialmente:

* elegibilidade;
* documentação obrigatória;
* cotas;
* publicação;
* transições de estado;
* pontuação;
* eliminação;
* classificação;
* recursos;
* autorização.

## 29. Observabilidade e diagnóstico

Falhas relevantes devem ser diagnosticáveis sem exposição indevida de informações sensíveis.

Logs devem possuir contexto suficiente para investigação.

Erros devem ser tratados de forma consistente e não devem revelar stack traces, credenciais, tokens ou detalhes internos sensíveis ao cliente.

Operações críticas devem possuir correlação adequada entre logs e auditoria quando necessário.

## 30. Experiência do usuário e acessibilidade

Interfaces devem priorizar:

* clareza;
* consistência;
* prevenção de erro;
* feedback explícito;
* acessibilidade;
* navegação por teclado;
* legibilidade;
* mensagens compreensíveis.

O wizard de configuração do Edital é uma organização de experiência do usuário e não deve impor artificialmente limites ao modelo de domínio.

Operações irreversíveis ou juridicamente relevantes devem apresentar confirmação e consequências de maneira inequívoca.

## 31. Simplicidade arquitetural

Preferir a solução arquitetural mais simples que preserve corretamente os requisitos do domínio.

Não introduzir microsserviços, mensageria, event sourcing, CQRS ou outras complexidades arquiteturais apenas por antecipação.

Complexidade adicional deve possuir necessidade demonstrável na especificação ou no plano.

Ao mesmo tempo, simplicidade não pode ser usada como justificativa para eliminar:

* histórico;
* auditoria;
* segurança;
* versionamento;
* integridade normativa;
* testes;
* consistência transacional.

## 32. Separação entre especificação e tecnologia

A Constituição estabelece princípios permanentes.

As especificações devem concentrar-se prioritariamente no que o sistema deve fazer e por quê.

Decisões como linguagem, framework, banco de dados, infraestrutura e bibliotecas devem ser tratadas no planejamento técnico quando não constituírem restrição institucional permanente.

Não introduzir escolhas tecnológicas desnecessárias na especificação funcional.

## 33. Spec-Driven Development obrigatório

O projeto deve utilizar o fluxo do GitHub Spec Kit como processo de desenvolvimento orientado por especificações.

O fluxo esperado para novos incrementos é:

1. Constituição;
2. Especificação;
3. Clarificação quando necessária;
4. Planejamento;
5. Tarefas;
6. Análise de consistência;
7. Implementação;
8. Convergência entre implementação e especificação.

Não iniciar implementação substancial de uma funcionalidade antes que exista especificação suficientemente clara e plano aprovado, salvo correções emergenciais devidamente justificadas.

## 34. Critério de conclusão

Uma funcionalidade não é considerada concluída apenas porque compila ou funciona no cenário principal.

Quando aplicável, a conclusão exige:

* requisitos atendidos;
* invariantes preservadas;
* autorização validada;
* migrations aplicáveis;
* testes aprovados;
* documentação/contratos atualizados;
* auditoria implementada;
* ausência de regressões conhecidas críticas;
* consistência entre especificação, plano, tarefas e implementação.

## Governança

Esta Constituição é a autoridade de engenharia e domínio para decisões estruturantes do projeto.

Especificações, planos e implementações devem respeitá-la.

Em caso de conflito entre uma decisão de implementação e esta Constituição, a Constituição prevalece até que seja formalmente alterada.

Alterações da Constituição devem:

1. ser explícitas;
2. apresentar justificativa;
3. identificar impacto sobre especificações e implementações existentes;
4. atualizar sua versão segundo versionamento semântico;
5. registrar data da alteração.

Utilizar:

* **MAJOR** para remoção ou redefinição incompatível de princípios;
* **MINOR** para novos princípios ou expansão material da governança;
* **PATCH** para esclarecimentos sem alteração semântica relevante.

Esta é a primeira Constituição do projeto.

Definir:

* versão inicial: `1.0.0`;
* data de ratificação: data atual;
* última alteração: data atual.

Após gerar a Constituição, valide que:

* não existam placeholders inexplicados;
* os princípios sejam declarativos e verificáveis;
* termos normativos utilizem MUST/SHOULD ou equivalentes inequívocos;
* não existam contradições entre princípios;
* a Constituição não tenha implementado funcionalidades;
* requisitos específicos que pertençam às futuras especificações não tenham sido indevidamente transformados em decisões técnicas.

Grave exclusivamente o artefato de Constituição previsto pelo Spec Kit em:

`.specify/memory/constitution.md`

Ao final, apresente o Sync Impact Report e o resumo exigido pelo workflow oficial do `/speckit.constitution`.
