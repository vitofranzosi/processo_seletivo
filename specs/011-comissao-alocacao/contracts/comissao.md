# Fase 1 — Contratos: Gestão da Comissão e Alocação por Etapa

**Feature**: [spec.md](../spec.md) | **Plano**: [plan.md](../plan.md) | **Modelo**: [data-model.md](../data-model.md)

Esta feature **não** expõe API. Não há endpoint novo em `publicacoes/api` nem em `shared/api`, e
nada do que ela grava entra no conteúdo publicado — logo não há forma canônica nova, nem incremento
de `SCHEMA_VERSION`, nem coleção nova endereçável por Retificação.

O que ela expõe são **superfícies HTML no canal institucional** e um **contrato de autorização** que
a 012 herda. Os dois estão abaixo.

## 1. Rotas

Todas sob `/gestao/`, no app `interface`. Nenhuma usa `etapas/` como segmento, porque a palavra já
significa *passo do compositor* em `editais/<uuid>/compor/<slug:etapa>` (D-009, D-015).

| Rota | Método | Ator | Autorização |
|---|---|---|---|
| `processos/<uuid:processo_id>/comissao` | GET | gestor ou presidente | `pode_gerir_comissao` |
| `processos/<uuid:processo_id>/comissao` | POST | gestor ou presidente | `pode_gerir_comissao` |
| `processos/<uuid:processo_id>/alocacoes` | GET | gestor ou presidente | `pode_gerir_comissao` |
| `processos/<uuid:processo_id>/alocacoes` | POST | gestor ou presidente | `pode_gerir_comissao` |
| `minhas-etapas` | GET | qualquer identidade institucional | nenhuma; a lista é derivada das alocações |
| `minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>` | GET | alocado, gestor ou presidente | `pode_atuar_na_etapa` **ou** `pode_gerir_comissao` |

`minhas-etapas` não exige permissão porque não revela nada: para quem não tem alocação, ela é o
estado vazio da seção 26 da spec, e não uma recusa.

## 2. Corpos aceitos

Formulários HTML, sem JSON. Toda validação é de servidor; a tela apenas antecipa a recusa.

### `POST processos/<id>/comissao`

| Campo | Obrigatório | Regra |
|---|---|---|
| `acao` | sim | `incluir`, `alterar_funcao` ou `remover` |
| `identity_subject` | em `incluir` | Identificador institucional. Não é validado contra diretório: não há diretório (D-003) |
| `display_label` | não | Rótulo de leitura humana, declaradamente não verificado |
| `funcao` | em `incluir` e `alterar_funcao` | `PRESIDENTE` ou `MEMBRO` |
| `membro_id` | em `alterar_funcao` e `remover` | UUID de membro ativo **deste** Processo |
| `idempotency_key` | sim | Gerada pelo formulário; alimenta `reserve()` |

### `POST processos/<id>/alocacoes`

| Campo | Obrigatório | Regra |
|---|---|---|
| `acao` | sim | `incluir` ou `remover` |
| `membro_id` | sim | UUID de membro **ativo** deste Processo |
| `edital_id` | sim | Edital **publicado** deste Processo |
| `etapa_id` | sim | Identidade presente em `etapas_vigentes(edital)` |
| `idempotency_key` | sim | |

## 3. Respostas

O contrato de recusa é tão importante quanto o de sucesso, porque metade desta feature **é** a
recusa.

| Situação | Resposta | Regra |
|---|---|---|
| Sucesso | 302 para a mesma tela, com confirmação perceptível | `UX-006` |
| Processo de outro escopo institucional | **404** | `FR-056` |
| Processo que o ator não pode gerir | **404** | `FR-057`, D-017 |
| Etapa não alocada ao ator, em `minhas-etapas/...` | **404** | `SC-009`, `SC-010` |
| Etapa de Edital de outro Processo | **404** | `FR-054` |
| `membro_id` de outro Processo | **404** | não enumerável |
| Etapa ausente da Versão Consolidada vigente | **404** | alocação órfã não concede acesso (`FR-047`) |
| Edital sem versão publicada | 409, com a razão nomeada na tela | `FR-032`, `EC-014` |
| Comissão sem presidente ativo, ao alocar | 409, nomeando o caminho | `FR-030` |
| Remover o último presidente com alocação ativa | 409, nomeando o caminho | `FR-030` |
| Vínculo ou alocação ativa já existente | 409 idempotente: nada é criado e nada falha para o usuário | `FR-064`, `FR-065`, `EC-001`, `EC-002` |
| Pessoa que não é membro ativo, ao alocar | 422 | `FR-033`, `FR-034`, `EC-005` |

**Uma única resposta para tudo que o ator não alcança.** Distinguir 403 de 404 já revelaria a
existência do objeto, que é o que `FR-057` proíbe.

## 4. O contrato que a 012 herda

É este o produto arquitetural da feature, e a razão de ela existir separada:

```python
pode_atuar_na_etapa(ator, edital, etapa_id) -> bool
```

Verdadeiro quando, e somente quando:

1. o ator tem identidade institucional no escopo do Processo do Edital;
2. existe `MembroComissao` **ativo** dele nesse Processo;
3. existe `AlocacaoEtapa` **ativa** desse membro para `(edital, etapa_id)`;
4. `etapa_id` está em `etapas_vigentes(edital)`.

Nenhuma das quatro condições é dispensável por papel, função ou privilégio administrativo
(`FR-012`, `FR-044`, D-006).

A 012 pode assumir: **se o ator chegou à Mesa de Avaliação de uma Etapa, a autorização para atuar
nela já foi resolvida aqui.** O que a 012 acrescentar — avaliador para inscrições específicas, por
exemplo — é decisão dela, e não altera este contrato.

## 5. O que esta feature promete **não** oferecer

Verificável por inspeção das telas, e é o objeto da demonstração de fronteira (`§50` da spec):

- nenhuma lista de candidatos, inscrição ou documento em qualquer superfície da 011;
- nenhum controle de avaliar, pontuar, opinar, marcar apto/inapto ou concluir (`FR-051`);
- nenhum controle desabilitado antecipando a 012 (`FR-052`);
- nenhum campo novo na Etapa: `avaliadores_exigidos`, `quorum` e equivalentes não existem
  (`FR-042`).
