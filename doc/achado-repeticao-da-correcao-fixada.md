# Repetir a correção fixada responde 403, e não a decisão gravada

**Data:** 2026-10-31
**Origem:** os testes do julgamento sob a role de produção, no PR #354 (A-01 e A-02 da auditoria
de prontidão de 31/10/2026).
**Natureza:** achado registrado, não corrigido. A correção é decisão de escopo, e não do PR do A-01.

## O que acontece

Uma julgadora defere um recurso com `CORRECAO_FIXADA`. O ato conclui: grava a decisão e o
Resultado sucessor. Ela repete o mesmo comando, com o mesmo conteúdo e a mesma chave de
idempotência. Em vez de receber a decisão já gravada, recebe:

```text
DomainError('appeal_judge_barred', 'Você consolidou o resultado atacado.', 403)
```

O comportamento é o mesmo como superusuário e como a role de produção: **não tem relação com
privilégio**, nem com a trava que o A-01 removeu. Nada se grava duas vezes, porque a recusa
acontece antes de qualquer escrita.

Na tela, a chave é fixa por peça (`idempotency_key=f"julgar-{peca.id}"`, em
`interface/views.py::julgar_recurso`). Por isso o duplo clique, o reenvio do formulário depois de
um *timeout* ou o "voltar e enviar de novo" mostram à julgadora, logo depois de um julgamento que
deu certo, que ela está impedida de julgar.

## Por que

`recursos/application/julgar.py::julgar` faz, nesta ordem:

```text
travar(actor, recurso_id)                         ← trava o Processo, confere o escopo
exigir_elegibilidade(actor, peca, etapa_id=...)   ← impedimento (FR-039, FR-043)
_exigir_admissao(peca)
reserve(...) → se já há resultado, devolve-o      ← idempotência (FR-097)
```

O impedimento lê o Resultado **vigente** do par (`elegibilidade._resultados_alcancados`). Depois de
uma correção fixada, o vigente é o sucessor que a própria decisão criou, e `_superar` grava
`consolidado_por=actor.subject`. Na repetição, a julgadora aparece como quem consolidou o Resultado
que a decisão alcança (`CONSOLIDOU`) e é barrada antes de a reserva ser consultada.

As outras espécies não criam sucessor, o vigente não muda, e a repetição devolve a decisão. É o que
o teste de repetição do PR #354 exercita, com a reavaliação determinada.

## Contrato violado

`specs/018-recursos-e-superacao-de-resultados/spec.md`:

- **FR-097**: repetir a mesma chave MUST devolver o desfecho original, sem criar linha nem evento.

A repetição não cria linha nem evento, mas também não devolve o desfecho: devolve uma recusa que
afirma um impedimento que não existia quando o ato foi praticado.

O impedimento continua certo **para atos novos**. Se a mesma julgadora tentar julgar outro recurso
sobre o mesmo par depois da correção, ela é quem consolidou o vigente, e a FR-039 a impede. O
defeito é só a ordem: a pergunta "já respondi a este pedido?" vem depois da pergunta "posso
praticar um ato novo?".

## Correção mínima proposta

Consultar a reserva **antes** do impedimento e **depois** da trava e do escopo. Na prática, mover o
bloco `reserve(...)` / `if reserva.result_id: return ...` para logo depois de `travar(...)`, dentro
da mesma transação:

```text
require_permission(recurso:julgar)        ← inalterado, fora da transação
travar(actor, recurso_id)                 ← inalterado: Processo travado, escopo conferido
reserve(...) → repetição devolve o gravado
exigir_elegibilidade(...)                 ← só para ato novo
_exigir_admissao(peca)
... (resto inalterado)
```

### O que se preserva

- **Autorização.** `require_permission` continua antes de tudo, e `travar` continua recusando com
  `404` fora do escopo. A repetição só alcança quem ainda tem a permissão e o escopo.
- **Segregação de funções.** A reserva é por `actor_subject`, escopo e operação, e a operação
  carrega a peça (`recurso:julgar:<id>`). Só a pessoa que praticou o ato recebe a repetição, e ela
  já passou pelo impedimento quando o praticou. Um terceiro com a mesma chave cai em reserva
  própria, vazia, e passa pelo impedimento normalmente.
- **Conteúdo diferente com a mesma chave.** Continua `409 idempotency_conflict` (FR-098), agora
  antes do impedimento. Isso não revela nada: a reserva é da própria pessoa.
- **Atomicidade.** A reserva nasce dentro de `command_context`. Se o impedimento ou a admissão
  recusarem um ato novo, a transação desfaz a reserva junto.

### O que ela deliberadamente não faz

- Não muda `impedimento`. Ignorar o sucessor criado pela própria decisão alteraria a FR-039 para
  julgamentos de **outros** recursos do mesmo par, e essa é decisão de domínio, não correção.
- Não muda a chave da tela.

### Teste que a prende

Sob `como_producao`, chamar `julgar` duas vezes com `CORRECAO_FIXADA`, mesmo conteúdo e mesma
chave: a segunda chamada devolve a mesma `DecisaoRecurso`, o mesmo sucessor, e nenhum evento novo na
trilha. Em seguida, outra julgadora (ou a mesma, com outra chave) tenta julgar outro recurso do
mesmo par e continua recebendo `403 appeal_judge_barred` (a FR-039 intacta).

**Conferido num experimento descartável** (31/10/2026, sobre `224bd47c`, não commitado): com o
bloco movido, os dois cenários acima passaram sob a role de produção, e também
`tests/integration/recursos/` e `tests/authorization/test_julgamento_de_recurso.py` inteiros (157
casos). Detalhe do retorno: a repetição devolve `(decisao, None)`, sem o sucessor, como já acontece
hoje na repetição das outras espécies. A tela só usa a decisão.

### Onde mais a ordem é a mesma

`admitir` também chama `exigir_elegibilidade` antes de `reserve`. Ali a repetição não se quebra,
porque admitir não muda o Resultado vigente nem a publicação atacada. A mesma inversão a deixaria
coerente com o julgamento, mas não é necessária para corrigir este defeito.
