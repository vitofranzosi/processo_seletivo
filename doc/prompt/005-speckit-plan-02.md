Execute a próxima etapa do projeto **Processo Seletivo — Editais** utilizando o workflow oficial do **GitHub Spec Kit**.

# Comando

```text
$speckit-plan
```

## Contexto atual

A branch ativa é:

```text
001-processo-seletivo-editais
```

A especificação está localizada em:

```text
specs/001-processo-seletivo-editais/spec.md
```

Existe um planejamento preliminar em:

```text
specs/001-processo-seletivo-editais/plan.md
```

Esse `plan.md` foi criado durante uma execução anterior de `$speckit-plan`, interrompida corretamente no **Constitution Check**.

Após o bloqueio, foi executado um novo `$speckit-clarify`, que resolveu todas as ambiguidades impeditivas.

O `plan.md` preliminar **não foi atualizado depois dessas clarificações**.

Portanto, antes de continuar o planejamento:

1. releia integralmente a `spec.md` atual;
2. releia a Constituição vigente do projeto;
3. reavalie todo o conteúdo existente em `plan.md`;
4. atualize ou substitua qualquer decisão preliminar incompatível com a especificação atual;
5. execute novamente o Constitution Check;
6. somente prossiga se não houver violação constitucional ou ambiguidade impeditiva.

---

# Estado atual validado da especificação

O último `$speckit-clarify` concluiu com:

```text
Status: CONCLUÍDO
```

Resultado:

* cenários de aceitação: `29`;
* requisitos funcionais: `39`;
* checklist: `16/16`;
* `[NEEDS CLARIFICATION]`: nenhum;
* compatibilidade constitucional: aprovada;
* contradições impeditivas: nenhuma.

Foram alterados:

```text
FR-006
FR-028
FR-029
```

Foi criado:

```text
FR-039
```

`FR-006` e `FR-034` estão agora consistentes.

---

# Decisões de domínio que obrigatoriamente devem orientar o planejamento

## 1. Estado `Encerrado` do Edital

O Edital possui explicitamente o estado:

```text
Encerrado
```

Esse estado representa a conclusão regular das etapas do Edital.

Ele é diferente de:

```text
Cancelado
```

que representa interrupção administrativa.

O planejamento técnico deve preservar essa diferença no:

* modelo de domínio;
* máquina de estados;
* persistência;
* contratos;
* validações;
* auditoria;
* casos de teste.

Não modelar `Encerrado` e `Cancelado` como equivalentes.

---

# 2. Cancelamento do Processo Seletivo

Preservar a regra definida na especificação:

> O cancelamento do Processo Seletivo fica bloqueado enquanto existir Edital que não esteja `Encerrado` nem `Cancelado`, observadas as demais regras administrativas da especificação.

O planejamento deve prever como essa invariante será garantida no domínio e testada.

---

# 3. Retificações

Uma Retificação:

* precisa ser publicada para produzir efeitos;
* pode vigorar imediatamente na Publicação;
* pode possuir início de vigência futuro;
* nunca pode possuir vigência anterior à Publicação.

A ordem normativa não pode ser determinada simplesmente pela ordem de criação ou Publicação.

---

# 4. Precedência temporal

Quando existirem múltiplas Retificações, a determinação do conteúdo vigente deve considerar:

```text
data/hora de início da vigência
```

A consolidação deve ser:

```text
temporal + cumulativa
```

Para qualquer instante `T`, deve ser possível reconstruir deterministicamente a versão normativa aplicável naquele instante.

O planejamento deve tratar explicitamente essa necessidade no modelo de dados e nos serviços de domínio.

---

# 5. Empate de vigência

Quando duas ou mais Retificações possuírem exatamente a mesma data/hora de início da vigência:

* alterações sobre conteúdos diferentes devem ser combinadas;
* havendo conflito sobre o mesmo conteúdo, prevalece a Retificação publicada por último.

O modelo técnico deve permitir aplicar essa regra deterministicamente.

Evite depender implicitamente de:

* ID;
* ordem física no banco;
* ordem de retorno da consulta;
* timestamp de criação não relacionado à Publicação.

---

# 6. Histórico normativo

Devem permanecer preservados:

* Edital original;
* todas as Retificações publicadas;
* versões consolidadas históricas;
* snapshots normativos imutáveis;
* histórico necessário para auditoria.

O sistema deve conseguir responder:

```text
Qual era o conteúdo normativo vigente no instante T?
```

sem reconstruções ambíguas.

---

# 7. Atos administrativos

Ativação e encerramento do Processo Seletivo são atos administrativos:

* explícitos;
* auditáveis;
* sujeitos às invariantes definidas na especificação.

Não inferir esses atos apenas pela passagem do tempo ou pelo estado dos Editais.

---

# 8. Segregação de funções

Preservar a regra já definida de que o elaborador não pode concluir sozinho todo o fluxo de:

```text
elaboração → homologação → Publicação
```

O planejamento deve considerar autorização contextual e segregação de funções.

Não tratar autorização apenas como uma lista simples de roles.

---

# 9. Auditoria

A arquitetura preliminar anteriormente registrada propôs:

```text
auditoria append-only
```

Reavalie essa decisão contra a Constituição e a especificação atual.

Caso continue adequada, detalhe no planejamento:

* eventos auditáveis;
* ator;
* instante;
* operação;
* entidade/agregado afetado;
* estado anterior quando necessário;
* estado resultante;
* contexto administrativo;
* correlação da operação quando aplicável.

A auditoria não deve permitir alteração destrutiva do histórico administrativo.

---

# 10. Concorrência

O planejamento deve tratar explicitamente operações concorrentes relevantes, principalmente:

* alteração de Processo;
* alteração de Edital;
* homologação;
* Publicação;
* Retificação;
* início de vigência;
* encerramento;
* cancelamento.

Defina estratégia consistente para impedir:

* lost update;
* dupla Publicação;
* transições inválidas;
* consolidações normativas inconsistentes.

Avalie optimistic locking e demais mecanismos necessários sem introduzir complexidade desnecessária.

---

# Arquitetura

A execução anterior registrou preliminarmente:

```text
monólito modular
snapshots normativos imutáveis
Retificações com versões consolidadas
autorização contextual
auditoria append-only
controle explícito de concorrência
```

Essas decisões ainda eram preliminares.

Agora:

1. reavalie cada uma contra a `spec.md` atual;
2. mantenha somente as que continuarem justificadas;
3. documente as decisões arquiteturais;
4. registre alternativas relevantes descartadas e seus motivos.

Evite:

* microserviços sem necessidade;
* event sourcing completo se não houver justificativa;
* CQRS artificial;
* abstrações prematuras;
* infraestrutura incompatível com o escopo atual.

Prefira a solução mais simples que preserve corretamente as invariantes do domínio.

---

# Modelagem

O `data-model.md` deve derivar da especificação e não de conveniências do framework.

Avalie explicitamente conceitos como:

* Processo Seletivo;
* Edital;
* perfil de vaga;
* cronograma;
* versão do Edital;
* Retificação;
* Publicação;
* versão consolidada;
* atos administrativos;
* histórico/auditoria.

Não crie entidades apenas porque foram mencionadas nesta instrução.

Determine corretamente:

* agregados;
* entidades;
* value objects;
* relacionamentos;
* cardinalidades;
* estados;
* invariantes;
* timestamps relevantes;
* fronteiras transacionais.

Diferencie claramente quando necessário:

```text
criação
Publicação
início da vigência
encerramento
cancelamento
```

---

# Research

Crie/atualize:

```text
research.md
```

Registre as decisões técnicas que realmente exigirem pesquisa ou justificativa.

Para cada decisão relevante, utilize estrutura equivalente a:

```text
Decision
Rationale
Alternatives considered
```

Não transforme `research.md` em repetição da especificação.

---

# Contratos

Crie:

```text
contracts/
```

Os contratos devem refletir os casos de uso e requisitos funcionais.

Não invente endpoints apenas para produzir CRUD de todas as entidades.

Priorize contratos orientados aos comportamentos definidos pela especificação, incluindo quando aplicável:

* criação;
* alteração;
* transições administrativas;
* homologação;
* Publicação;
* Retificação;
* encerramento;
* cancelamento;
* consulta da versão vigente;
* consulta do histórico normativo.

Considere:

* códigos HTTP;
* validação;
* concorrência;
* idempotência quando necessária;
* optimistic locking;
* erros de domínio;
* autorização;
* paginação quando pertinente.

---

# Quickstart

Crie/atualize:

```text
quickstart.md
```

O quickstart deve permitir validar posteriormente a implementação dos principais fluxos definidos na especificação.

Inclua cenários representativos, especialmente:

1. criação de Processo;
2. criação de Edital;
3. fluxo de elaboração;
4. homologação;
5. Publicação;
6. Retificação com vigência imediata;
7. Retificação com vigência futura;
8. duas Retificações publicadas fora da ordem de vigência;
9. empate de vigência sem conflito;
10. empate de vigência com conflito;
11. reconstrução histórica;
12. encerramento regular do Edital;
13. tentativa inválida de cancelamento do Processo;
14. segregação de funções;
15. concorrência relevante.

Não implemente testes nesta fase; apenas planeje sua validação.

---

# Constitution Check

Execute novamente o Constitution Check com base na versão atual da especificação.

Valide especialmente:

* rastreabilidade requisito → planejamento;
* integridade histórica;
* auditabilidade;
* segregação de funções;
* segurança/autorização;
* concorrência;
* invariantes de domínio;
* ausência de decisões técnicas incompatíveis com a Constituição.

Se surgir nova violação real ou ambiguidade que não possa ser resolvida sem decisão de negócio:

```text
PARE.
```

Não invente regra de domínio.

Informe:

```text
Status: BLOQUEADO
```

e descreva precisamente o impedimento.

---

# Artefatos esperados

Se o Constitution Check for aprovado, conclua os artefatos previstos pelo `$speckit-plan`, incluindo conforme o workflow:

```text
plan.md
research.md
data-model.md
contracts/
quickstart.md
```

Atualize também os demais artefatos auxiliares exigidos pelo Spec Kit, caso o workflow oficial determine.

---

# Restrições

Nesta execução:

```text
NÃO executar $speckit-tasks.
NÃO implementar código funcional.
NÃO criar classes Java de produção.
NÃO criar migrations de implementação.
NÃO implementar controllers.
NÃO implementar services.
NÃO implementar repositories.
NÃO implementar frontend.
```

Esta etapa termina no planejamento técnico.

---

# Arquivos locais

Preserve arquivos não rastreados existentes que não façam parte do workflow.

Em especial, preserve:

```text
doc/prompt/003-criacao-processo-seletivo-edital.md
```

Não remova, sobrescreva ou adicione esse arquivo ao versionamento sem necessidade explícita.

---

# Relatório final

Ao concluir, apresente:

```text
Status: CONCLUÍDO
```

ou:

```text
Status: BLOQUEADO
```

Informe:

1. resultado do Constitution Check;
2. arquitetura final escolhida;
3. decisões técnicas principais;
4. agregados e fronteiras identificados;
5. estratégia para versionamento normativo;
6. estratégia para Retificações e precedência temporal;
7. estratégia de auditoria;
8. estratégia de autorização e segregação de funções;
9. estratégia de concorrência;
10. contratos planejados;
11. cenários principais do quickstart;
12. artefatos criados/modificados;
13. pendências ou riscos identificados;
14. confirmação de que nenhum código funcional foi implementado.

Se o planejamento for concluído sem impedimentos, encerre explicitamente com:

```text
O planejamento está apto para avançar para $speckit-tasks.
```

Não execute `$speckit-tasks` nesta mesma atividade.
