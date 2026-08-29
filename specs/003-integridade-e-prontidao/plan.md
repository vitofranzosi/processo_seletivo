# Implementation Plan: Integridade Normativa e Prontidão para Produção

**Branch**: `003-integridade-e-prontidao` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-integridade-e-prontidao/spec.md`

**Status**: Concluída — Constitution Check aprovado com uma exceção registrada e justificada.

## Summary

Corrigir os defeitos de integridade normativa e segurança encontrados na revisão sobre `b12b8f6`,
e transformar os pressupostos de implantação em precondições que falham cedo.

O trabalho tem duas naturezas distintas e o plano as separa porque elas obedecem a regras
diferentes do fluxo constitucional:

**Correção emergencial** (já aplicada, commits `41e8173`, `e3a6992`, `854f216`): os seis
bloqueadores. A Constituição admite correção emergencial justificada antes de especificação e
plano; defeito que faz o sistema publicar norma que ninguém homologou qualifica. A especificação
foi escrita junto, não depois, e cada correção tem teste de regressão que falha no código anterior.

**Trabalho planejado** (o que resta): imutabilidade no banco, limites de borda HTTP, provisionamento
de papéis, e as lacunas funcionais herdadas da 002. Nada aqui é emergencial e tudo segue a ordem
normal — plano, tarefas, análise de consistência, implementação.

A feature **não** entrega autenticação institucional nem endereçamento normativo por chave estável.
Entrega a barreira que impede implantar sem a primeira e a contenção que impede o dano da segunda.

## Technical Context

**Language/Version**: Python 3.13 — o mesmo do backend, mesmo projeto

**Primary Dependencies**: nenhuma nova. Django 5.2 LTS, DRF 3.16, psycopg 3. A verificação
anti-falsificação e o enquadramento vêm do próprio Django; a barreira de produção é um módulo de
configuração, não uma biblioteca

**Storage**: PostgreSQL 16+. Uma coluna nova (`AlteracaoNormativa.expected_anchors`), um backfill
determinístico, e triggers de imutabilidade para as tabelas normativas que ainda não os têm

**Testing**: pytest e pytest-django. A régua desta feature exige a suíte **também contra
PostgreSQL**: concorrência, permissões de papel e migrações são exatamente o que o SQLite ignora, e
é onde os riscos transacionais vivem

**Target Platform**: mesmo processo Django do backend, atrás do proxy institucional

**Project Type**: monólito modular existente; nenhuma estrutura nova

**Performance Goals**: nenhuma regressão de latência atribuível às verificações acrescentadas. A
derivação de precondição é O(alterações × profundidade do caminho) sobre conteúdo já em memória;
a paginação do histórico (FR-024) é o único item com meta própria — deixar de ordenar em memória

**Constraints**: nenhuma verificação nova pode transformar o caminho feliz em recusa; nenhuma
migração aplicada pode ser reescrita; nenhum registro normativo publicado pode ser alterado

**Scale/Scope**: o mesmo da 001 e da 002. O escopo desta feature é corretivo, não expansivo

## Constitution Check

| Princípio | Situação |
| --- | --- |
| I — Linguagem ubíqua e integridade do domínio | **Atendido com ressalva.** "Entidades DEVEM possuir identificadores estáveis" é justamente o que o endereçamento por índice não honra. A âncora de identidade é contenção; a conformidade plena depende da 004. Registrado em Complexity Tracking. |
| II — Integridade normativa, imutabilidade e temporalidade | **Reforçado.** É o objeto da feature: o conteúdo que passa a vigorar volta a ser validado, a precondição impede sobrescrita silenciosa, e FR-023 leva a imutabilidade para o banco. |
| III — Segurança, proteção de dados e auditoria | **Reforçado.** CSRF, enquadramento, correlação e chave de idempotência na auditoria, barreira de produção. A autenticação institucional continua ausente — e agora impede implantar, em vez de passar despercebida. |
| IV — Regras explícitas e consistência operacional | **Reforçado.** Invariante de finalização na criação de Edital, bloqueio do agregado pai, validação estrutural na Publicação da Retificação. |
| V — Qualidade, rastreabilidade e simplicidade | **Atendido.** Cada defeito tem teste de regressão que falha no código anterior; a suíte roda contra PostgreSQL sem ignorados. |
| Fluxo de desenvolvimento | **Exceção registrada.** Parte da implementação precedeu o plano, sob a cláusula de correção emergencial justificada. Ver Complexity Tracking. |

## Decisões técnicas

### Decisão 1 — Contenção por precondição, não troca de endereçamento

O defeito está no endereçamento por índice, e a cura é endereçar coleções por chave estável. Mas a
cura muda `data-model`, contrato público e exige migração de Retificações existentes — é feature
própria, com sua própria análise de consistência.

Entre conviver com o defeito até lá e contê-lo agora, a contenção: **verificar sempre**, com duas
peças que respondem a perguntas diferentes.

- O **hash** do conteúdo no caminho responde "o valor ainda é este?".
- A **âncora** de identidade de cada índice atravessado responde "ainda é esta entidade?".

Nenhuma supre a outra. Sem âncora, dois Perfis de denominação idêntica tornam o hash
indistinguível e o ato atinge o Perfil errado com a precondição satisfeita. Sem hash, uma
Retificação concorrente que alterou o mesmo campo da mesma entidade é sobrescrita em silêncio.

O resultado é honesto sobre o que é: a contenção impede publicar o ato errado; não permite publicar
o ato certo sem refazê-lo quando a lista mudou de forma. Concorrência sobre a mesma lista custa
reelaboração até a 004.

### Decisão 2 — A precondição é derivada pelo servidor, não exigida do cliente

Manter `expectedPreviousHash` opcional no contrato preserva os clientes existentes. Mas a ausência
da declaração não pode significar "publique sem verificar": significa "verifique contra a base que
eu declarei", e o `baseSnapshotId` é informação que o servidor já tem.

Precondição opcional para o cliente, obrigatória para o sistema. A declaração do cliente prevalece
sobre o hash derivado — quem declara sabe o que está fazendo. A âncora não é declarável: ela não
descreve conteúdo, descreve de quem o ato fala.

### Decisão 3 — A migração de dados congela a lógica que usa

Importar a função do domínio na migração faria uma alteração futura nela mudar retroativamente o
efeito de uma migração já executada em produção. Migração aplicada tem de continuar significando o
que significava no dia em que rodou.

A lógica é copiada e congelada dentro da migração. A duplicação é o preço de a história ser fixa;
um teste recusa qualquer migração que importe domínio ou aplicação, e o teste de backfill compara o
resultado congelado com o que a elaboração viva produz, para que a cópia não divirja em silêncio.

### Decisão 4 — Produção é um módulo que se recusa a subir, não uma lista de conferência

A segurança de um sistema que publica atos normativos não pode depender de alguém lembrar de
exportar uma variável. `config.settings.production` transforma cada pressuposto em precondição de
inicialização, com mensagem que nomeia a variável a corrigir.

Sobre o alcance, para que ninguém leia a barreira como mais do que é: ela recusa o que **sabe** ser
inseguro — o módulo de autenticação de desenvolvimento, os esquemas do DRF que autenticam contra
esta aplicação em vez do diretório, nomes não importáveis. Ela **não prova** que a classe declarada
fale com o diretório do Ifes; nenhuma configuração prova isso. Garante que a escolha seja explícita,
exista, e não seja um caminho conhecidamente inseguro.

### Decisão 5 — A repetição idempotente devolve o status do ato, não "criou ou não"

O contrato documenta um único código de sucesso por operação. O padrão `201 if created else 200`
respondia fora do contrato e sugeria ao cliente que nada foi criado, quando o ato existe e é dele.
O status vem do registro de idempotência, que passa a ser campo vivo.

O recurso é devolvido no estado em que se encontra, que é o que o cliente obteria relendo-o — não um
retrato da resposta original. Replay literal exigiria persistir o corpo da resposta; a diferença
importa pouco quando o `ETag` acompanha o estado atual, e está registrada como decisão.

### Decisão 6 — Imutabilidade no banco, com o papel de runtime sem `UPDATE` nem `DELETE`

`VersaoConsolidada`, `Publicacao`, `DocumentoPublicado` e a auditoria já têm trigger. Estendê-la a
`Retificacao`, `AlteracaoNormativa`, `AtoAdministrativo` e `RevisaoEdital` esbarra num detalhe: as
três primeiras **mudam legitimamente** enquanto o ato está em curso. `Retificacao` transita de
estado; `AlteracaoNormativa` é substituída a cada edição de rascunho.

A imutabilidade que interessa é a do que já foi publicado. A trigger precisa ser condicional ao
estado, não absoluta — recusar alteração quando a Retificação está `PUBLICADA` ou `CANCELADA`, e
recusar sempre em `AtoAdministrativo` e `RevisaoEdital`, que nascem imutáveis. Esta é a única
decisão desta feature que exige desenho novo, e por isso encabeça a lista de tarefas.

## Project Structure

### Documentation (this feature)

```
specs/003-integridade-e-prontidao/
├── spec.md              # o que e por quê, com a evidência de cada defeito
├── plan.md              # este documento
├── tasks.md             # a lista executável
└── checklists/
    └── requirements.md  # análise de consistência
```

### Source Code (repository root)

```
backend/
├── config/settings/
│   ├── base.py                        # CSRF e enquadramento na cadeia de middleware
│   └── production.py                  # barreira de inicialização
├── processo_seletivo/
│   ├── publicacoes/
│   │   ├── domain/conflicts.py        # precondição de conteúdo e âncora de identidade
│   │   ├── application/retificacoes.py # verificação, validação estrutural, idempotência
│   │   └── migrations/
│   │       ├── 0005_ancoras_de_alteracao.py
│   │       ├── 0006_backfill_precondicoes.py   # lógica congelada
│   │       └── 0007_*                          # imutabilidade condicional (FR-023)
│   ├── processos/application/commands.py       # invariante e bloqueio na criação de Edital
│   └── shared/idempotency.py                   # reserva e encerramento compartilhados
└── scripts/                                    # provisionamento de papéis (FR-019)
```

## Fases

| Fase | Conteúdo | Situação |
| --- | --- | --- |
| 0 | Reprodução executável de cada defeito | Concluída — evidência em `spec.md` |
| 1 | Correção emergencial dos seis bloqueadores | Concluída — `41e8173`, `e3a6992`, `854f216` |
| 2 | Plano e tarefas | Este documento e `tasks.md` |
| 3 | Análise de consistência | `checklists/requirements.md` |
| 4 | Imutabilidade no banco (FR-023) | Concluída — migration `0007` |
| 5 | Limites de borda e instantes (FR-020, FR-021) | Concluída |
| 6 | Provisionamento de papéis (FR-019) | Concluída — `manage.py provisionar_papeis` |
| 7 | Lacunas funcionais da 002 (FR-025 a FR-028) | Concluída |
| 8 | Desempenho e higiene (FR-022, FR-024) | Concluída |

A ordem das fases 4 a 8 é por risco decrescente, não por esforço. Imutabilidade primeiro porque é a
única garantia da feature que hoje depende de disciplina da aplicação em vez do banco.

## Riscos

| Risco | Mitigação |
| --- | --- |
| A trigger de imutabilidade condicional bloquear transição legítima de Retificação em curso | Condicionar ao estado final, não à tabela; teste que percorre o ciclo inteiro antes de publicar |
| O backfill não alcançar linhas criadas entre a migração e o deploy | A Publicação recusa `REPLACE`/`REMOVE` sem hash, independentemente da migração |
| A verificação de precondição gerar recusa em cenário legítimo de vigência fora de ordem | Já coberto: a base declarada precisa ser a vigente no início da própria vigência, com teste dedicado |
| Limitar campos na borda HTTP quebrar cliente existente | Os limites espelham as colunas que já existem; hoje o excesso vira erro 500, que não é contrato |
| A suíte contra PostgreSQL não rodar na CI | A CI já valida contra PostgreSQL 18; a régua da feature é ela sem ignorados |

## Complexity Tracking

| Desvio | Por quê | Alternativa descartada |
| --- | --- | --- |
| Implementação precedeu plano e tarefas | Cláusula de correção emergencial justificada. Um dos defeitos publicava, sem erro nem aviso, alteração normativa que nenhuma autoridade homologou; manter isso em produção durante um ciclo completo de artefatos é o risco maior | Escrever plano e tarefas antes de corrigir. Descartada porque o defeito estava em produção |
| Identificador estável exigido pelo princípio I permanece não atendido | A troca de endereçamento muda modelo, contrato e exige migração de dados; é feature própria (`004-enderecamento-normativo-estavel`) | Trocar o endereçamento nesta feature. Descartada por acumular duas mudanças de natureza distinta num ciclo, uma delas corretiva e urgente |
| Lógica duplicada entre a migração `0006` e o domínio | Migração aplicada não pode mudar de efeito porque o domínio evoluiu | Importar do domínio. Descartada: é exatamente o acoplamento que quebra a reprodutibilidade histórica |
