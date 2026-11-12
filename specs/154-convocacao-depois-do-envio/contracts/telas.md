# Contrato das telas: 154

O que cada superfície **diz**, por cenário, depois da implementação. Tudo o que não está aqui fica
como está. As frases são literais; ‹data› é `dd/mm/aaaa`, ‹hora› é `HH:MM` (as funções `data` e
`data_e_hora` de `portal/obrigacoes.py`).

## Portal — a convocação (`portal:convocacao`)

A ordem dos elementos é a da FR-3859 da `121`, sem mudança. Só mudam o título, o resumo e a
presença da advertência.

| Elemento | Com providência pendente | Sem providência, fora de Tc | Tc |
|---|---|---|---|
| `<h1 id="titulo-da-chamada">` | *Você foi convocado!* | *Acompanhe sua convocação* | *Acompanhe sua convocação* |
| `.etapa-da-chamada` | como hoje | como hoje | como hoje |
| `.cartao-do-prazo` | como hoje | como hoje (FR-6208) | como hoje (FR-6208) |
| `.resumo-da-chamada` | *Você ainda precisa ‹tarefas›.* | *Você não tem mais documentos para enviar agora. A comissão ainda vai concluir a análise.* | *A conferência dos documentos obrigatórios terminou. Aguarde o registro do resultado desta convocação.* |
| linha do opcional | — | *Se quiser, você ainda pode enviar ‹o documento opcional›‹ até o prazo›.* quando houver | idem |
| `.acao-da-chamada` | *Ver o que preciso fazer* | — | — |
| `.consequencia` | *Se você não atender no prazo, a comissão poderá registrar o não atendimento desta convocação.* — só com o prazo correndo | **ausente** | **ausente** |
| `.ressalva` | como hoje | como hoje (FR-6210) | como hoje (FR-6210) |
| confirmação do envio, sem tarefa restante | — | frase de conclusão | frase da conferência terminada |

### O cartão do item reenviado (`_cartao_do_documento_da_convocacao.html`)

| Momento | Texto | Selo |
|---|---|---|
| aberta | *Reenviado — aguardando nova conferência. Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida.* | *Aguardando conferência* (como hoje) |
| encerrada pelo prazo | idem | idem |
| encerrada pelo Processo | *Reenviado em ‹data›; não foi conferido antes do encerramento do Processo.* | *Não conferido* (como hoje) |
| decidida | *Reenviado em ‹data›; não foi conferido antes do resultado.* | idem |

Facultativo reenviado: o mesmo texto, com o selo *Opcional* além do da categoria.

### Sem documento pedido (ramo `{% else %}` de `convocacao.html`)

Só muda o `<h1>`: *Acompanhe sua convocação* quando o Requerimento é o único pedido da chamada e já
foi enviado (D-006). O bloco *O que fazer*, a linha do Requerimento enviado e os dados do ato ficam.
A página continua **sem** `.consequencia` em todos os casos, como hoje: a advertência dessa chamada
mora só no acompanhamento (D-007).

## Portal — o acompanhamento (`portal:acompanhamento`), seção da convocação

| Elemento | Com providência pendente | Sem providência, fora de Tc | Tc |
|---|---|---|---|
| `.acao-principal` | *Você ainda precisa ‹tarefas›.* | *Nada por enquanto.* + frase de conclusão | *Nada por enquanto.* + frase da conferência terminada |
| `.prazo-da-convocacao` | como hoje | como hoje (FR-6208) | como hoje (FR-6208) |
| `.consequencia` | como hoje | **ausente** | **ausente** |

Sem documento, com o Requerimento da chamada enviado: *Seu Requerimento de Matrícula foi enviado.*,
o link de conferir, o prazo, e **sem** `.consequencia`. Nada pedido pelo portal: como hoje.

## Gestão — documentos da convocação (`interface:documentos_da_convocacao`)

| Elemento | Hoje | Depois |
|---|---|---|
| rótulo do item `COMPLEMENTADO` | *Complementado, aguardando conferência* | *Reenviado — aguardando nova conferência* |
| resumo *Documentos pedidos nesta convocação* | **N** *Reenviado(s), a conferir de novo* | **1** *reenviado — aguardando nova conferência* · **2** *reenviados — aguardando nova conferência* |
| *Situação desta convocação*, passo | *Conferir de novo: o candidato reenviou 1 documento que estava pendente.* | *Conferir de novo: 1 documento reenviado — aguardando nova conferência.* (plural: *2 documentos reenviados — …*) |
| linha do aviso, frase do reenvio | *O candidato reenviou o documento pendente em ‹data›; a nova conferência está por fazer.* | *O candidato reenviou o documento pendente em ‹data›.* (R-009) |
| `<summary>` do bloco de conferência | *Conferir a versão N* | igual |

## Gestão — condução da convocação (`interface:convocacao`)

| Elemento | Hoje | Depois |
|---|---|---|
| linha documental do cartão | `· N complementado(s)` | `· 1 reenviado — aguardando nova conferência` / `· N reenviados — …` |
| passo da chamada no cartão | como na página de documentos | idem |
| prévia e resultado do aviso de pendência, *Ficam de fora* | *documento reenviado, aguardando conferência, N* | *documento reenviado — aguardando nova conferência, N* |

## O que não muda, e o teste prende

- a mensagem da convocação e a da correção (`convocacao/templates/convocacao/mensagem/*`);
- a trilha, os avisos e os documentos já gravados (SC-2005): o texto antigo continua lá;
- a tela com desfecho: *Resultado da sua convocação*, o rótulo do desfecho e a frase do aceite
  (FR-6206);
- os títulos do vencido, do encerrado pelo Processo e do decidido;
- o andamento (*A corrigir*, *A enviar*, *Aguardando conferência*, *Conferidos*).
