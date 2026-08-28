No projeto `processo_seletivo`, na branch ativa `001-processo-seletivo-editais`, execute a próxima etapa oficial do GitHub Spec Kit:

`$speckit-tasks`

## Objetivo

Gerar o `tasks.md` completo para a feature `001-processo-seletivo-editais`, utilizando exclusivamente como fonte de verdade os artefatos já aprovados da especificação e do planejamento.

Considere obrigatoriamente:

* `constitution.md`;
* `spec.md`;
* `plan.md`;
* `research.md`;
* `data-model.md`;
* `contracts/openapi.yaml`;
* `quickstart.md`.

Não implemente código funcional nesta etapa.

## Estado atual

O `$speckit-plan` foi concluído com sucesso.

O Constitution Check resultou em `PASS` antes e depois do desenho, com:

* 39 requisitos funcionais rastreados;
* 29 cenários de aceitação;
* nenhum `NEEDS CLARIFICATION`;
* nenhum gate constitucional bloqueado;
* nenhuma exceção constitucional.

A arquitetura definida é:

* monólito modular;
* Python;
* Django;
* PostgreSQL 18;
* persistência relacional para dados editáveis;
* migrations para gerenciamento da evolução do banco de dados.

## Regras que o `tasks.md` deve preservar

A decomposição das tarefas não pode simplificar, reinterpretar ou contradizer as decisões já aprovadas.

### Domínio

Preservar explicitamente as fronteiras dos agregados e conceitos definidos:

* `ProcessoSeletivo`;
* `Edital`;
* `Retificacao`;
* fluxo normativo imutável de `Publicacao`;
* `VersaoConsolidada`;
* `RegistroAuditoria` append-only.

Preservar a distinção:

* `Encerrado` = conclusão regular do Edital;
* `Cancelado` = interrupção administrativa.

Não tratar esses estados como equivalentes.

### Publicação, vigência e Retificações

As tarefas devem contemplar a implementação e os testes da reconstrução normativa temporal.

Cada Publicação deverá preservar, conforme o planejamento:

* ato original ou Retificação;
* alterações normativas estruturadas;
* snapshot consolidado;
* PDF publicado;
* hashes;
* autoria;
* Autoridade Signatária;
* instante de Publicação;
* início de vigência.

Para reconstruir o conteúdo aplicável no instante `T`, preservar rigorosamente a regra definida:

1. partir do Edital original;
2. selecionar atos publicados cuja vigência já tenha iniciado em `T`;
3. ordenar por início de vigência;
4. em igualdade de vigência, utilizar a ordem real e transacional de Publicação;
5. acumular alterações independentes;
6. quando houver conflito sobre o mesmo conteúdo, prevalecer a última Publicação.

A ordenação normativa não pode depender de:

* ID;
* posição física;
* timestamp de criação.

Também deve permanecer proibida vigência anterior à Publicação.

### Segurança e segregação de funções

Criar tarefas explícitas para implementar e testar:

* negação de acesso por padrão;
* autorização considerando recurso, estado e contexto institucional;
* segregação de funções;
* restrição para que o elaborador não consiga sozinho concluir elaboração, homologação e Publicação;
* identificação dos participantes reais dos atos;
* proteção das operações administrativas;
* proteção contra alteração indevida de conteúdo normativo já publicado.

Não reduzir essas regras a simples validações de perfil/role.

### Auditoria

Criar tarefas específicas para:

* `RegistroAuditoria` append-only;
* gravação da auditoria na mesma transação do ato de negócio;
* autoria e contexto do ato;
* impossibilidade de credenciais comuns alterarem ou excluírem registros de auditoria;
* correlação com logs técnicos sem duplicação desnecessária de conteúdo sensível.

Incluir testes para essas invariantes.

### Concorrência e idempotência

O `tasks.md` deve decompor explicitamente:

* optimistic locking dos agregados mutáveis;
* suporte a `If-Match`;
* locks curtos nas operações normativas críticas;
* `Idempotency-Key` nos comandos irreversíveis definidos pelo contrato;
* ordem monotônica de Publicação por Edital;
* constraints contra dupla Publicação;
* comportamento seguro em retry;
* consolidação temporal idempotente;
* verificação por hash.

Incluir testes concorrentes quando previstos pelo planejamento.

## Contrato HTTP

Utilizar `contracts/openapi.yaml` como contrato da API.

O contrato atualmente possui 11 `operationId` únicos, contemplando:

* criação de Processo Seletivo com primeiro Edital;
* criação de Editais adicionais;
* edição estruturada;
* ativação;
* submissão;
* homologação;
* Publicação;
* Retificação;
* encerramento;
* cancelamento;
* consultas públicas vigentes e históricas;
* documentos publicados;
* auditoria administrativa.

As tarefas de controller/API devem ser derivadas do contrato, e não o contrário.

Não modificar silenciosamente o OpenAPI para acomodar decisões de implementação.

Caso seja encontrada inconsistência real entre contrato, especificação e plano, interrompa a decomposição dessa parte e reporte-a em vez de inventar uma regra.

## Estratégia de decomposição

Organize o `tasks.md` segundo o formato oficial do Spec Kit.

As tarefas devem possuir:

* IDs;
* descrição objetiva;
* caminhos de arquivos quando aplicável;
* dependências implícitas ou explícitas suficientes para determinar a ordem;
* marcação `[P]` somente quando puderem ser executadas realmente em paralelo;
* associação à User Story quando exigida pelo formato oficial.

Prefira tarefas pequenas o suficiente para que cada uma tenha um resultado verificável.

Não crie tarefas genéricas como:

* "implementar backend";
* "implementar segurança";
* "criar testes";
* "implementar models".

Decomponha-as em unidades concretas e verificáveis.

## Organização desejada

Respeitando o formato produzido pelo `$speckit-tasks`, procure estruturar a execução aproximadamente em:

1. Setup;
2. infraestrutura/fundação compartilhada;
3. persistência e migrations fundamentais;
4. domínio compartilhado;
5. segurança, autorização e auditoria fundamentais;
6. User Stories em ordem de prioridade;
7. Publicação e versionamento normativo;
8. Retificações e consolidação temporal;
9. consultas públicas vigentes e históricas;
10. concorrência, idempotência e integridade;
11. testes de integração/contrato;
12. validações do `quickstart.md`;
13. polish e validação final.

Entretanto, siga a organização oficial do Spec Kit caso ela determine estrutura diferente.

## Testes

As tarefas de testes devem ser derivadas principalmente:

* dos 29 cenários de aceitação;
* dos 39 requisitos funcionais;
* dos invariantes constitucionais;
* do OpenAPI;
* dos 15 grupos de validação definidos no `quickstart.md`.

Garanta cobertura explícita para, no mínimo:

* fluxo completo de criação até Publicação;
* Retificação com vigência imediata;
* Retificação com vigência futura;
* vigências fora da ordem cronológica de Publicação;
* empate de vigência sem conflito;
* empate de vigência com conflito;
* reconstrução histórica em diferentes instantes;
* preservação das versões históricas;
* encerramento regular;
* cancelamento;
* tentativa inválida de cancelamento;
* segregação de funções;
* autorização contextual;
* auditoria;
* optimistic locking;
* `If-Match`;
* idempotência;
* retries;
* dupla tentativa de Publicação;
* concorrência em operações normativas;
* consistência dos hashes;
* consulta pública do conteúdo vigente;
* consulta pública histórica.

Não agrupe cenários críticos de forma que a rastreabilidade seja perdida.

## Rastreabilidade

Antes de finalizar, valide que:

* todos os 39 requisitos funcionais possuem cobertura por uma ou mais tarefas;
* todos os 29 cenários de aceitação possuem caminho de implementação/teste;
* os 15 grupos do `quickstart.md` estão contemplados;
* todos os `operationId` do OpenAPI possuem tarefas correspondentes;
* todas as entidades/agregados do `data-model.md` possuem implementação planejada;
* todas as decisões arquiteturais relevantes do `research.md` estão refletidas;
* nenhuma tarefa viola a Constituição.

Se possível dentro do fluxo oficial do `$speckit-tasks`, mantenha a rastreabilidade entre:

`Requisito → User Story → tarefa de implementação → tarefa de teste`

## Riscos não impeditivos

Não transforme automaticamente estes riscos em decisões arquiteturais inventadas:

* homologação institucional da plataforma;
* definição de RPO/RTO;
* provedor institucional de identidade;
* política definitiva de armazenamento/retenção de PDFs;
* escolha definitiva do gerador de PDF;
* confirmação dos volumes estimados.

Quando necessário, crie apenas abstrações ou tarefas preparatórias compatíveis com o planejamento atual.

Não escolha arbitrariamente fornecedores ou tecnologias ainda não decididos.

## Restrições desta execução

Nesta etapa:

* não implementar código funcional;
* não criar migrations;
* não criar models;
* não criar controllers;
* não criar services;
* não criar repositories;
* não implementar frontend;
* não alterar decisões de domínio aprovadas;
* não reabrir clarificações já resolvidas sem evidência objetiva de inconsistência;
* não executar `$speckit-implement`.

O objetivo desta execução é produzir e validar exclusivamente o plano de tarefas de implementação.

## Validação final

Após gerar `tasks.md`:

1. execute as verificações previstas pelo `$speckit-tasks`;
2. revise dependências e oportunidades reais de paralelismo;
3. verifique se nenhuma tarefa depende de artefato criado apenas posteriormente;
4. confirme a cobertura dos requisitos, cenários, contrato e quickstart;
5. confirme novamente a conformidade com `constitution.md`;
6. procure placeholders, `TODO`, `NEEDS CLARIFICATION` ou decisões não resolvidas;
7. não avance para implementação.

## Relatório esperado

Ao concluir, apresente:

1. **Status final** — `CONCLUÍDO`, `CONCLUÍDO COM RESSALVAS` ou `BLOQUEADO`;
2. caminho do `tasks.md`;
3. quantidade total de tarefas;
4. quantidade de tarefas `[P]`;
5. distribuição das tarefas por fase/User Story;
6. dependências principais;
7. oportunidades de paralelismo;
8. cobertura dos 39 requisitos funcionais;
9. cobertura dos 29 cenários de aceitação;
10. cobertura dos 15 grupos do quickstart;
11. cobertura dos 11 `operationId`;
12. resultado do Constitution Check;
13. inconsistências ou lacunas encontradas;
14. riscos ainda pendentes;
15. confirmação explícita de que nenhum código funcional foi implementado.

Ao final, informe se a feature está apta para avançar posteriormente para `$speckit-implement`.

Não execute `$speckit-implement` nesta etapa.
