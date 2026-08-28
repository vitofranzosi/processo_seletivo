Execute exclusivamente a próxima etapa de especificação do projeto **Processo Seletivo — Editais**, utilizando o workflow oficial do **GitHub Spec Kit**.

## Comando da etapa

```text
$speckit-clarify
```

## Contexto

A execução anterior de `$speckit-plan` foi corretamente interrompida no **Constitution Check** devido a duas ambiguidades ainda existentes na especificação.

A branch ativa é:

```text
001-processo-seletivo-editais
```

A especificação está localizada em:

```text
specs/001-processo-seletivo-editais/spec.md
```

Existe também um `plan.md` preliminar já criado em:

```text
specs/001-processo-seletivo-editais/plan.md
```

O arquivo local:

```text
doc/prompt/003-criacao-processo-seletivo-edital.md
```

deve continuar sendo **preservado**, sem alteração e sem ser adicionado ao versionamento caso permaneça não rastreado.

Não implemente código funcional nesta etapa.

---

# Objetivo do novo ciclo de clarificação

Resolver **somente** as duas ambiguidades identificadas durante o Constitution Check, incorporando as decisões abaixo à especificação.

Não reabra decisões de domínio que já tenham sido esclarecidas e incorporadas anteriormente.

---

# Clarificação 1 — Estado `Encerrado` do Edital

A especificação deve estabelecer explicitamente que um **Edital pode assumir o estado `Encerrado`**.

O estado `Encerrado` representa a conclusão normal do ciclo administrativo e operacional daquele Edital.

Ele é semanticamente diferente de `Cancelado`.

Considere, portanto, pelo menos a seguinte distinção:

```text
Encerrado
    conclusão regular do Edital após o término de suas etapas.

Cancelado
    interrupção administrativa do Edital antes de sua conclusão regular.
```

O modelo de estados do Edital deve ficar consistente em toda a especificação.

Revise especialmente:

* `FR-006`;
* `FR-034`;
* User Stories relacionadas;
* cenários de aceitação;
* Edge Cases;
* regras de cancelamento do Processo Seletivo;
* quaisquer outras referências aos estados possíveis de Edital.

Deve ficar explicitamente válida a regra já estabelecida de que:

> um Processo Seletivo somente pode ser cancelado quando todos os seus Editais estiverem `Encerrados` ou `Cancelados`, conforme as demais regras administrativas da especificação.

Não transforme `Encerrado` em sinônimo de `Cancelado`.

---

# Clarificação 2 — Precedência de Retificações com vigência futura

Retificações podem:

* ser publicadas em uma determinada data/hora;
* entrar em vigor imediatamente na publicação; ou
* estabelecer expressamente uma data/hora futura para início de sua vigência.

Uma Retificação nunca pode produzir efeitos retroativos anteriores à sua publicação.

Quando existirem múltiplas Retificações publicadas com datas futuras de vigência fora da ordem de publicação, a precedência normativa deve obedecer às seguintes regras.

## Regra principal

A versão normativa aplicável em determinado instante deve ser determinada pela:

```text
data/hora de início da vigência
```

e **não simplesmente pela ordem de publicação**.

Exemplo:

```text
Retificação A
Publicada: 01/09
Vigência: 10/09

Retificação B
Publicada: 05/09
Vigência: 08/09
```

Resultado:

```text
05/09 a 07/09:
versão anterior continua vigente.

08/09 a 09/09:
entra em vigor a Retificação B.

A partir de 10/09:
entra em vigor a Retificação A, considerando também todas as alterações
normativas que já estejam vigentes e não tenham sido posteriormente
substituídas.
```

Portanto, a consolidação deve ser **temporal e cumulativa**, considerando todas as Retificações cuja vigência já tenha iniciado naquele instante.

---

# Empate de vigência

Caso duas ou mais Retificações tenham exatamente a mesma:

```text
data/hora de início da vigência
```

utilize como critério determinístico de desempate:

```text
a Retificação publicada por último prevalece em caso de conflito entre
alterações sobre o mesmo conteúdo.
```

Se as Retificações alterarem conteúdos diferentes, ambas devem compor normalmente a versão consolidada.

A especificação deve deixar claro que o sistema não pode produzir uma situação em que seja impossível determinar objetivamente qual conteúdo normativo está vigente.

---

# Publicação versus vigência

Preserve a regra já esclarecida:

```text
Uma Retificação somente pode produzir efeitos após sua Publicação.

Sua vigência será:

1. a própria data/hora da Publicação, quando não houver data futura expressa; ou
2. a data/hora futura expressamente definida.

Nunca poderá existir vigência anterior à Publicação.
```

---

# Versionamento e histórico normativo

As clarificações devem permanecer compatíveis com os princípios já estabelecidos de:

* histórico público de Editais;
* preservação do Edital original;
* preservação de todas as Retificações publicadas;
* versões consolidadas históricas;
* snapshots normativos imutáveis;
* auditabilidade;
* reconstrução do conteúdo vigente em qualquer instante histórico relevante.

Uma nova Retificação não deve destruir ou sobrescrever fisicamente:

* o Edital original;
* Retificações anteriores;
* versões consolidadas históricas.

---

# Consistência da especificação

Após incorporar as clarificações, revise a especificação inteira procurando contradições.

Atualize, quando necessário:

* seção `Clarifications`;
* User Stories;
* Acceptance Scenarios;
* Edge Cases;
* Functional Requirements;
* estados e transições;
* regras de Retificação;
* regras de cancelamento;
* Glossário ou conceitos de domínio, se existentes.

Não altere requisitos que não sejam impactados pelas duas decisões acima.

---

# Identificação dos requisitos

Se for necessário alterar requisitos existentes, preserve os identificadores atuais sempre que possível.

Por exemplo:

```text
FR-006
FR-034
```

Se surgir algum requisito novo indispensável, utilize o próximo identificador disponível, sem renumerar desnecessariamente requisitos já existentes.

---

# Validação esperada

Ao concluir `$speckit-clarify`, valide explicitamente que:

1. `Encerrado` aparece como estado válido do Edital em todos os pontos necessários;
2. `Encerrado` e `Cancelado` possuem semânticas distintas;
3. `FR-006` e `FR-034` não entram mais em conflito;
4. é possível determinar a versão normativa vigente para qualquer instante;
5. Retificações com vigência futura fora da ordem de publicação possuem precedência determinística;
6. empate de vigência possui regra determinística;
7. nenhuma Retificação possui efeitos anteriores à sua Publicação;
8. versões consolidadas históricas continuam preservadas;
9. não restam ambiguidades impeditivas para retomar `$speckit-plan`;
10. nenhuma funcionalidade foi implementada.

---

# Restrições desta execução

Nesta etapa:

```text
NÃO executar $speckit-plan.
NÃO executar $speckit-tasks.
NÃO implementar código.
NÃO criar migrations.
NÃO criar entidades Java.
NÃO criar controllers.
NÃO criar services.
NÃO criar repositories.
NÃO criar DTOs.
NÃO criar endpoints.
```

O objetivo é exclusivamente finalizar as duas clarificações pendentes da especificação.

---

# Resultado esperado

Ao final, apresente um relatório contendo:

```text
Status: CONCLUÍDO
```

ou, caso exista impedimento real:

```text
Status: BLOQUEADO
```

Informe:

1. as clarificações incorporadas;
2. os requisitos alterados;
3. User Stories ou cenários alterados;
4. Edge Cases alterados;
5. eventual requisito novo criado;
6. confirmação de que `FR-006` e `FR-034` estão consistentes;
7. regra final de precedência temporal das Retificações;
8. regra de desempate para mesma vigência;
9. quantidade final de cenários de aceitação;
10. quantidade final de requisitos funcionais;
11. resultado da verificação de consistência;
12. arquivos modificados;
13. confirmação de que nenhum código funcional foi implementado.

Se todas as ambiguidades forem resolvidas, encerre explicitamente informando:

```text
A especificação está apta para retomar $speckit-plan.
```

Não execute `$speckit-plan` nesta mesma atividade.
