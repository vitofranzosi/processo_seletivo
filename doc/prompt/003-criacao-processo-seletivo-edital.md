Prepare e execute a fase de planejamento da feature:

```text
001-processo-seletivo-editais
```

## 1. Preparação do Git

Antes de executar o planejamento, verifique o estado atual do repositório com:

```bash
git status
git branch --show-current
```

A execução anterior confirmou que:

* a branch atual é `main`;
* a branch `001-processo-seletivo-editais` ainda não existe;
* `.specify/feature.json` já identifica corretamente a feature ativa;
* `doc/prompt/002-fase-1.md` encontra-se não rastreado e não deve ser removido, sobrescrito ou incluído inadvertidamente em alterações.

Crie uma branch específica para a feature a partir do estado atual da `main`:

```bash
git switch -c 001-processo-seletivo-editais
```

Não descarte, altere ou sobrescreva arquivos locais existentes.

Confirme que a branch ativa passou a ser:

```text
001-processo-seletivo-editais
```

Se houver qualquer condição no estado do Git que torne insegura a criação ou troca da branch, interrompa essa etapa e apresente o diagnóstico antes de prosseguir.

## 2. Executar o planejamento

Após confirmar a branch, execute:

```text
$speckit-plan
```

Use como fontes normativas e funcionais, nesta ordem:

1. `.specify/memory/constitution.md` — Constituição v1.0.0;
2. `specs/001-processo-seletivo-editais/spec.md`;
3. seção `Clarifications` do `spec.md`;
4. `specs/001-processo-seletivo-editais/checklists/requirements.md`;
5. `.specify/feature.json`;
6. estrutura e convenções já existentes no repositório.

## 3. Decisões de domínio já consolidadas

Não reabra decisões já resolvidas pelo `$speckit-clarify`, especialmente:

* ativação e encerramento do Processo Seletivo são atos administrativos explícitos e auditáveis;
* Retificação entra em vigor na Publicação, salvo data futura expressamente declarada;
* Retificação nunca possui vigência anterior à sua Publicação;
* o elaborador não pode executar sozinho elaboração, homologação e Publicação do mesmo Edital;
* Edital original, Retificações e versões consolidadas históricas permanecem públicas;
* cancelamento do Processo Seletivo fica bloqueado enquanto existir Edital não encerrado ou não cancelado;
* um Processo Seletivo pode possuir múltiplos Editais;
* Editais podem possuir cronogramas independentes;
* um Edital pode abranger múltiplos perfis de vaga;
* Retificação pode alterar qualquer conteúdo, preservando histórico e rastreabilidade;
* cotas devem atender à legislação vigente.

Não simplifique essas regras para facilitar a implementação.

## 4. Objetivo do planejamento

Transforme a especificação funcional em um plano técnico implementável, mantendo separação clara entre:

* requisitos de negócio;
* modelo de domínio;
* persistência;
* regras de aplicação;
* autorização;
* auditoria;
* API;
* validações;
* testes.

O planejamento deve ser derivado da especificação, e não o contrário.

## 5. Modelo de domínio

Analise cuidadosamente as entidades, agregados, relacionamentos, estados, invariantes e eventos necessários.

Dê atenção especial a:

* Processo Seletivo;
* Edital;
* Retificação;
* versões do Edital;
* Perfil de Vaga;
* cronogramas;
* vagas;
* cadastro reserva;
* cotas;
* atos administrativos;
* estados e transições;
* publicação;
* homologação;
* cancelamento;
* encerramento;
* histórico;
* auditoria.

Evite modelar histórico normativo apenas sobrescrevendo registros existentes.

A solução deve permitir reconstruir qual conteúdo estava vigente em determinado momento.

## 6. Retificações e versionamento

O planejamento deve explicar como representar:

```text
Edital original
        ↓
Retificação 1
        ↓
Versão consolidada
        ↓
Retificação 2
        ↓
Nova versão consolidada
```

Devem permanecer distinguíveis:

* documento original;
* cada Retificação;
* cada versão consolidada;
* data/hora de Publicação;
* início de vigência;
* responsável pelo ato;
* conteúdo vigente em determinado instante;
* histórico público.

Não implemente isso ainda; apenas defina adequadamente a estratégia técnica.

## 7. Estados e transições

Defina explicitamente os estados necessários e as transições permitidas para Processo Seletivo, Edital e demais elementos que realmente necessitem de ciclo de vida.

Evite representar regras importantes apenas por combinações arbitrárias de campos booleanos.

As transições devem respeitar as invariantes estabelecidas pela especificação e pela Constituição.

## 8. Segurança e autorização

Planeje autorização baseada em operações de domínio, não apenas em proteção genérica de endpoints.

Considere especialmente:

* elaboração;
* submissão;
* homologação;
* publicação;
* retificação;
* cancelamento;
* encerramento;
* consulta administrativa;
* consulta pública.

A regra de segregação de funções deve ser verificável pelo domínio/aplicação e auditável.

Não acople a regra diretamente a cargos específicos se a especificação estiver baseada em permissões.

## 9. Auditoria

Planeje rastreabilidade suficiente para atos administrativos relevantes.

Sempre que aplicável, devem poder ser identificados:

* ator;
* operação;
* entidade afetada;
* instante;
* estado anterior;
* estado posterior;
* motivo/justificativa quando exigido;
* correlação com Publicação, Retificação ou outro ato administrativo.

## 10. Persistência e concorrência

Analise:

* integridade referencial;
* constraints;
* unicidade;
* índices;
* optimistic locking onde necessário;
* concorrência em homologação, publicação, retificação, cancelamento e encerramento;
* consistência transacional;
* preservação do histórico.

Não escolha soluções excessivamente complexas sem justificativa.

## 11. API

Planeje os contratos necessários sem permitir que entidades de persistência se tornem diretamente o contrato público da API.

Considere separação adequada entre:

* commands/requests;
* responses;
* filtros;
* paginação;
* operações de workflow;
* consultas públicas;
* consultas administrativas.

Operações de domínio relevantes não devem ser artificialmente representadas como simples CRUD quando possuírem semântica própria.

## 12. Testes

Defina estratégia de testes cobrindo, no mínimo:

* regras de domínio;
* transições válidas;
* transições inválidas;
* autorização;
* segregação de funções;
* publicação;
* vigência de Retificações;
* versionamento histórico;
* cancelamento;
* encerramento;
* concorrência relevante;
* persistência;
* API;
* cenários de aceitação definidos no `spec.md`.

Relacione o planejamento dos testes aos cenários de aceitação sempre que possível.

## 13. Integrações e decisões técnicas

Os itens que o `$speckit-clarify` classificou como:

* integrações externas;
* escala, disponibilidade e recuperação;
* decisões tecnológicas;

foram deliberadamente deixados para planejamento.

Resolva somente aquilo que for necessário para produzir um plano implementável.

Quando houver escolha arquitetural relevante:

1. identifique o problema;
2. apresente alternativas razoáveis;
3. registre a decisão;
4. registre a justificativa;
5. registre trade-offs.

Não introduza infraestrutura ou padrões sem necessidade demonstrável.

## 14. Constitution Check

Execute e documente explicitamente o Constitution Check exigido pelo Spec Kit.

Qualquer conflito com a Constituição v1.0.0 deve interromper o planejamento ou ser resolvido antes de considerá-lo concluído.

## 15. Restrições desta etapa

Nesta execução:

* não implementar código funcional;
* não executar `$speckit-tasks`;
* não criar controllers, services, repositories ou entities de produção;
* não criar migrations de implementação;
* não alterar requisitos de negócio sem justificativa;
* não remover decisões consolidadas;
* não avançar automaticamente para implementação.

Crie apenas os artefatos previstos pela fase `$speckit-plan`.

## 16. Relatório final

Ao concluir, informe:

* status;
* feature;
* branch ativa;
* artefatos criados/alterados;
* arquitetura proposta;
* agregados e entidades identificados;
* estratégia de versionamento de Editais e Retificações;
* estados e principais transições;
* estratégia de autorização;
* estratégia de auditoria;
* estratégia de persistência e concorrência;
* contratos/API planejados;
* estratégia de testes;
* decisões técnicas relevantes;
* resultado do Constitution Check;
* pendências ou riscos;
* confirmação de que nenhum código funcional foi implementado.

Se o planejamento estiver completo e validado, indique como próximo passo:

```text
$speckit-tasks
```

Não execute `$speckit-tasks` nesta etapa.
