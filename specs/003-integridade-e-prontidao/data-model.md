# Data Model: Integridade Normativa e Prontidão para Produção

**Feature**: `003-integridade-e-prontidao` | **Fase**: 1 | **Data**: 2026-08-29

Esta feature é corretiva: não cria entidade nova. O que ela muda é **um campo**, **quatro
proteções de banco** e **a política de privilégios** — e o que justifica cada mudança é uma
garantia que antes dependia de disciplina da aplicação.

## Campo novo

### `AlteracaoNormativa.expected_anchors`

| Atributo | Valor |
| --- | --- |
| Tipo | `JSONField(default=dict, blank=True)` |
| Migration | `publicacoes/0005_ancoras_de_alteracao` |
| Preenchimento retroativo | `publicacoes/0006_backfill_precondicoes`, só para Retificações em curso |
| Origem | Derivado pelo servidor a partir de `base_snapshot.content` |
| Declarável pelo cliente | **Não** |

Mapa `prefixo do caminho → identidade da entidade` para cada índice de lista que o `target_path`
atravessa. A identidade é `id:<uuid>` quando o elemento tem `id`, e `hash:<sha256>` quando não tem.

```
target_path: /profiles/1/name
expected_anchors: {"/profiles/1": "id:00000000-0000-0000-0000-000000000502"}
```

**Por que existe.** `expected_previous_hash` responde "o valor ainda é este?". A âncora responde
"ainda é esta entidade?". São perguntas diferentes e nenhuma supre a outra:

| Situação | Hash | Âncora |
| --- | --- | --- |
| Outra Retificação mudou o mesmo campo da mesma entidade | recusa | passa |
| Índice deslocou e o novo ocupante tem o mesmo valor | passa | recusa |
| `ADD` posicional deslocou | não se aplica | recusa |

Por isso a Publicação exige as duas, e recusa `REPLACE`/`REMOVE` que chegue sem hash
(`precondition_missing`).

**Posição de acréscimo.** `/profiles/-` não gera âncora: acrescentar ao fim é estável por
definição. Índice além do fim também não — não há entidade ali.

## Proteções de banco

`publicacoes/0007_imutabilidade_do_historico`. As quatro primeiras já existiam; as quatro últimas
são desta feature.

| Tabela | Trigger | Condição |
| --- | --- | --- |
| `auditoria_registroauditoria` | `auditoria_append_only` | absoluta |
| `publicacoes_publicacao` | `publicacao_append_only` | absoluta |
| `publicacoes_documentopublicado` | `documento_publicado_append_only` | absoluta |
| `publicacoes_versaoconsolidada` | `versao_consolidada_append_only` | absoluta |
| `publicacoes_retificacao` | `retificacao_final_imutavel` | `OLD.status IN ('PUBLICADA','CANCELADA')` |
| `publicacoes_alteracaonormativa` | `alteracao_normativa_final_imutavel` | estado final da Retificação pai |
| `processos_atoadministrativo` | `ato_administrativo_append_only` | absoluta |
| `publicacoes_revisaoedital` | `revisao_edital_append_only` | absoluta |

**Por que duas condicionais.** `Retificacao` transita de estado, é devolvida e reeditada;
`AlteracaoNormativa` é apagada e recriada a cada edição de rascunho. Congelá-las por completo
quebraria o fluxo. A condição olha `OLD.status`, de modo que a transição que *torna* o ato final é
admitida e qualquer alteração posterior é recusada.

**Armadilha registrada.** Numa trigger `BEFORE`, o valor devolvido é a linha que segue adiante.
`RETURN OLD` num `UPDATE` descarta a alteração em silêncio — o comando responde sucesso e nada
muda. `reject_final_change_mutation` devolve `NEW` em `UPDATE` e `OLD` em `DELETE`.

## Política de privilégios

`processo_seletivo/seguranca/papeis.py` — fonte única, aplicada por `manage.py provisionar_papeis`
e verificada pelos testes de conformidade.

| Papel | Sobre o esquema | Sobre tabelas ordinárias | Sobre append-only |
| --- | --- | --- | --- |
| migração | dono, `USAGE, CREATE` | dono | dono |
| runtime | `USAGE` | `SELECT, INSERT, UPDATE, DELETE` | `SELECT, INSERT` |

Append-only aqui são as seis da tabela acima cuja trigger é absoluta. `Retificacao` e
`AlteracaoNormativa` ficam de fora: privilégio não distingue linha de linha, e a imutabilidade
delas é condicional ao estado — só a trigger consegue expressar isso.

**Propriedade importa.** `GRANT ALL` deixa o papel de migração usar as tabelas, mas `ALTER TABLE`
exige ser dono. Sem a transferência, um esquema criado pelo superusuário faz a próxima migration
falhar no meio do deploy.

**Ordem.** Provisionar → migrar → provisionar. Todo comando que toca tabela é condicional à
existência dela, e o comando informa quantas protegeu para que a segunda passada esquecida apareça
no momento em que é esquecida.

## Limites de borda

Espelham as colunas, e são derivados delas onde possível.

| Campo | Limite | Onde é imposto |
| --- | --- | --- |
| `targetPath` | 1000 | `ChangeSerializer` |
| `expectedPreviousHash` | 64 | `ChangeSerializer` |
| `institutionalCode`, títulos, número | `_meta.get_field(...).max_length` | `interface/views.TEXTOS_DA_CRIACAO` |
| ano do Edital | 2000–9999 | `interface/views` e `CreateEditalSerializer` |
| `X-Correlation-ID` | 100, imprimível | `CorrelationIdMiddleware` |
| `Idempotency-Key` | 16–128 | `processos/api/views.idempotency_key` |

Na tela de criação o limite vem de `_meta` em vez de ser repetido: número copiado à mão se
desatualiza em silêncio na primeira migration que mudar o tamanho da coluna.

## O que não mudou

Nenhuma entidade nova, nenhum relacionamento novo, nenhuma mudança em `VersaoConsolidada`,
`Publicacao`, `Perfil`, `Evento` ou no snapshot canônico. O endereçamento normativo continua por
índice — contido, não curado. A cura é a `004`.
