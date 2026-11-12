# Contrato: telas e comandos da 156

O que muda na superfície. As frases são as da spec; aqui ficam a rota, o comando, as recusas e o que
cada tela recebe.

## Portal do candidato

| Rota | Método | Nome | O que faz |
|---|---|---|---|
| `inscricoes/<id>/convocacao` | GET | `portal:convocacao` (existente) | duas camadas (FR-6400), frase simples (FR-6406, FR-6442), próximo passo (FR-6410 a FR-6414), contato ou nada (FR-6415, FR-6416), *"Chamada"* no lugar de *"Espécie"* (R-005), *"Desistir desta convocação"* ou o pedido pendente (FR-6418, FR-6421) |
| `inscricoes/<id>` | GET | acompanhamento (existente) | o porquê do desfecho em duas camadas, o próximo passo e o contato |
| `inscricoes/<id>/convocacao/desistencia` | GET | `portal:desistir` (nova) | a página de confirmação da FR-6419; sem desfecho, sem pedido pendente, com a chamada visível |
| `inscricoes/<id>/convocacao/desistencia` | POST | `portal:desistir` | `pedir_desistencia`; volta para `portal:convocacao#pedido-de-desistencia` |
| `inscricoes/<id>/convocacao/desistencia/cancelar` | POST | `portal:cancelar-desistencia` (nova) | `cancelar_pedido_de_desistencia`, depois da confirmação na mesma página |

Todas exigem a identidade autenticada e a titularidade; a inexistente, a de outra pessoa e a chamada
invisível respondem pela recusa de inexistente (`DomainError` 404), como as demais rotas da convocação.

## Comandos

### `convocacao.application.desistencia.pedir_desistencia`

```text
pedir_desistencia(*, identidade, inscricao_id, ciencia: bool, idempotency_key, correlation_id) -> Pedido
```

| Ordem | Verificação | Recusa |
|---|---|---|
| 1 | trava: Processo `FOR SHARE`, Inscrição `FOR UPDATE`; reserva da chave de idempotência (R-008) | repetição devolve o resultado da primeira |
| 2 | titularidade; chamada vigente visível ao candidato | `not_found` 404 |
| 3 | Processo fora de estado final | a de sempre (`ensure_processo_accepts_changes`) |
| 4 | chamada sem desfecho | `convocacao_com_desfecho` 409 |
| 5 | pedido pendente da mesma chamada | **devolve o existente** (idempotência pelo estado) |
| 6 | `ciencia` marcada | `ciencia_obrigatoria` 422 |

Grava o pedido e a trilha (`CONVOCACAO_PEDIDO_DE_DESISTENCIA`, sem endereço).

### `convocacao.application.desistencia.cancelar_pedido_de_desistencia`

```text
cancelar_pedido_de_desistencia(*, identidade, inscricao_id, idempotency_key, correlation_id) -> Cancelamento
```

Mesma trava e mesmas verificações 1 a 4; sem pedido pendente, `sem_pedido_pendente` 409. Grava o
cancelamento e a trilha (`CONVOCACAO_CANCELAMENTO_DO_PEDIDO`).

### `convocacao.application.desfechar.desfechar` *(acréscimos)*

```text
desfechar(..., ciencia_do_pedido: bool | None = None, avisar: bool = False, endereco_do_portal="")
```

- `avisar` com `envio_do_desfecho_habilitado()` falso → `aviso_envio_desabilitado` 409, **antes** de
  qualquer gravação (FR-6438).
- Com pedido pendente na chamada e espécie diferente da desistência expressa, sem `ciencia_do_pedido`
  → `pedido_de_desistencia_pendente` 409 (FR-6425).
- `avisar` verdadeiro e habilitado → `avisos.application.desfechos.gravar(...)` na mesma transação; sem
  endereço, não grava, e o declarado diz `aviso: "sem_endereco"` (FR-6436).
- O declarado ganha `aviso: "solicitado" | "sem_endereco" | None`.

### `convocacao.application.fluxo.registrar_nao_atendimento_dos_vencidos` *(acréscimo)*

`avisar: bool = False`, com a mesma recusa da chave; o alcance deixa de fora as chamadas com pedido
pendente (`fora["pedidoDeDesistencia"]`, FR-6426). A assinatura do alcance inclui a partição, de modo
que um pedido feito entre a prévia e a confirmação muda o alcance e recusa com `ALCANCE_MUDOU`.

## Gestão

| Tela | Mudança |
|---|---|
| condução da convocação (`interface:convocacao`) | cartão: passo `PEDIDO_DE_DESISTENCIA` antes dos demais (FR-6443), a linha *"Pedido de desistência pelo portal em ‹data e hora›"*, o atalho *"Registrar a desistência pedida"* (FR-6424); no formulário do desfecho, o aviso e a marca de ciência do pedido (FR-6425); a opção *"Avisar a pessoa por e-mail"* desmarcada, ou desabilitada sem endereço, com a ajuda da UX-623 (FR-6430, FR-6436); o estado do aviso no cartão (FR-6445); a mensagem de retorno *"Desfecho registrado. Aviso solicitado."* |
| vencidos (`#vencidos`) | *"Ficam de fora…"* com *"N com pedido de desistência pendente"*; a opção *"Avisar as pessoas por e-mail"* |
| conferência do texto (`_conferir_o_texto.html`) | a prévia nas duas camadas (FR-6404; FR-3993 da `125`, revista) |
| "O que fazer agora" (Centro e Edital) | a providência *"Registrar a desistência pedida pelo portal"* (FR-6427) |
| confirmar encerramento do Edital e do Processo | a linha dos pedidos pendentes (FR-6444) |
| avisos do Edital e detalhe do aviso | o rótulo da origem nova, *"Aviso do resultado da convocação"* |

## Mensagens

| Mensagem | Mudança |
|---|---|
| convocação e correção (`convocacao/mensagem/*`) | prazo sem *"contado do envio desta mensagem"* (FR-6428); *"Em caso de dúvida, fale com ‹canal›."* só com canal (FR-6416) |
| aviso do desfecho (`avisos/domain/desfecho.py`, nova) | FR-6433 a FR-6435: o assunto, o corpo neutro, a instrução de acesso por código, o contato quando houver, o rodapé fixo |

## Recusas novas

| Código | Status | Onde |
|---|---|---|
| `convocacao_com_desfecho` | 409 | pedido e cancelamento |
| `sem_pedido_pendente` | 409 | cancelamento |
| `ciencia_obrigatoria` | 422 | pedido sem a marca |
| `pedido_de_desistencia_pendente` | 409 | desfecho de outra espécie sem a ciência |
| `aviso_envio_desabilitado` (existente) | 409 | desfecho ou lote com `avisar` e a habilitação desligada |
