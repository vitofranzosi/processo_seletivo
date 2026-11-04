# Encaminhamento — o Requerimento continua preenchível com o Processo encerrado

Registrado em 04/11/2026, a pedido do usuário, no encerramento da spec `118`. **Alta prioridade,
frente separada.** Nada aqui muda regra durante a `118` (FR-3756 da `118`). Leitura estática sobre a
`main` em `fb0e1ddc`; nenhum cenário foi executado.

> **Decidir é do usuário.** Este documento investiga, separa os casos e propõe uma correção curta,
> com testes e a decisão necessária.

## O que acontece hoje

Com o **Processo Seletivo** encerrado ou cancelado (`PROCESSO_FINAL`,
`processos/domain/finalizacao.py`) e uma convocação vigente **sem desfecho**:

| Ato | Hoje | Onde |
|---|---|---|
| Apresentar documento da convocação | **recusado** | `convocacao/application/documentos.py`, `apresentar` → `ensure_processo_accepts_changes` |
| Conferir documento | **recusado** | o mesmo arquivo, a conferência → `ensure_processo_accepts_changes` |
| Registrar desfecho | **recusado** | `convocacao/application/desfechar.py` → `comando_de_comissao` (`comissoes/application/__init__.py`) → `ensure_processo_accepts_changes` |
| Abrir rascunho, preencher e enviar o Requerimento *na convocação* | **aceito**, enquanto o prazo da chamada não decorrer | `requerimentos/domain/disponibilidade.py`, `apurar`: disponível = chamada em aberto; fecha só pelo prazo (FR-374) e pelo desfecho (FR-411) |
| *Conferir e atualizar* o Requerimento enviado (sucessor) | **aceito**, nas mesmas condições | `requerimentos/application/preencher.py`, `autorizacao_para_atualizar` |

Nenhum comando do app `requerimentos` consulta o estado do Processo. Há teste de que o Processo em
estado final não recebe documento (`tests/integration/convocacao/test_documentos_da_convocacao.py`,
`test_processo_em_estado_final_nao_recebe_documento`), e nenhum para o Requerimento.

**O efeito.** A pessoa preenche e envia um Requerimento que nenhum ato pode mais considerar: a
comissão não desfecha, e a convocação fica sem resultado para sempre. É escrita sem destino, contra a
FR-035 da `001` (*"Encerramento e cancelamento DEVEM impedir novas transições incompatíveis, mantendo
disponíveis as consultas históricas autorizadas"*).

## Os casos que não se confundem

1. **Requerimento *na convocação*, ainda não enviado (rascunho ou nenhum), Processo em estado
   final.** É o caso do defeito: abrir, preencher e enviar deveriam ser recusados.
2. **Requerimento enviado, Processo em estado final.** A **leitura** MUST continuar: é consulta
   histórica (FR-035 da `001`; FR-406 da `029`). Só o sucessor (*conferir e atualizar*) é escrita.
3. **Requerimento *na inscrição*.** É exigido para enviar a inscrição (FR-372 da `029`), e o
   encerramento das inscrições já o fecha pelo período. Depois de enviado, vale o caso 2. O sucessor
   depende de chamada em aberto (FR-408), e cai na mesma pergunta do caso 1.
4. **Edital encerrado (`113`), com o Processo ainda ativo.** **Não é este caso.** A FR-3616 da `115`
   manda a apresentação e a conferência seguirem a chamada em aberto, e o teste
   `test_edital_encerrado_com_convocacao_em_aberto_continua_recebendo_e_conferindo` o prende. O
   Requerimento deve continuar seguindo a chamada aqui também: o encerramento do Edital admite
   convocação em aberto (FR-3534 da `113`, advertência que não impede).

## Impacto nas specs

| Spec | Regra | Impacto |
|---|---|---|
| `001` | FR-035 | É a regra que o Requerimento descumpre; não muda |
| `029` | FR-373 (disponível com convocação vigente sem desfecho), FR-374 (prazo), FR-408 (sucessor), FR-411 (desfecho) | **Acréscimo**: o Processo em estado final também encerra o preenchimento, o envio e o sucessor, sem fechar a leitura nem apagar o rascunho — o molde da FR-374 revista pela `115` |
| `113` | FR-3534 | Nenhum: trata do Edital, e a convocação em aberto continua só advertência |
| `115` | FR-3582, FR-3616, FR-3622 | Nenhum para os documentos. A FR-3622 (um só prazo para tudo o que a chamada autoriza a escrever) ganha coerência: documentos e Requerimento passam a fechar juntos também pelo Processo |
| `118` | FR-3725, FR-3741 | A linha 5 da FR-3725 deixa de alcançar o Processo em estado final, e a FR-3741 deixa de precisar do bloco *"O que ainda pode ser feito"*. Se a correção vier antes da implementação da `118`, ajustar as duas; se vier depois, revisar com teste |

## Proposta de correção (curta)

1. **Domínio.** `apurar` recebe, injetado como a chamada e o prazo, se o Processo está em estado
   final. Com ele, a `Disponibilidade` marca a escrita fechada, no molde de `prazo_decorrido` — **sem
   sexto estado de leitura** (a FR-405 fixa cinco). `abrir_rascunho`, `gravar`, `enviar` e
   `autorizacao_para_atualizar` recusam com a mesma recusa de `ensure_processo_accepts_changes`.
2. **Leitura.** Enviado e rascunho continuam legíveis; nada é apagado nem convertido.
3. **Telas.** A página do Requerimento diz *"O envio pelo portal está encerrado"*, com a frase do
   Processo da FR-3741 da `118`, e *"Voltar à convocação"*. O chamado ao Requerimento some, como some
   com o prazo decorrido.
4. **Nada mais.** Sem desfecho automático, sem prazo novo, sem mensagem.

## Testes

- Processo encerrado e cancelado, Requerimento *na convocação*: abrir rascunho, gravar, enviar e
  atualizar recusados, sem linha gravada; a leitura do enviado e do rascunho, preservada.
- Edital encerrado com Processo ativo: o Requerimento continua seguindo a chamada (o par do teste da
  `115`).
- Requerimento *na inscrição* enviado, Processo encerrado: leitura preservada; sucessor recusado.
- A recusa é a mesma de `ensure_processo_accepts_changes`, para documentos e Requerimento.
- O teste de custo do Requerimento (`tests/integration/requerimentos/test_orcamento_de_consulta.py`)
  não cresce: o estado do Processo vem da inscrição que a view já lê.

## A decisão necessária

**O Requerimento *na convocação* deve fechar com o Processo em estado final, como os documentos e o
desfecho?** A recomendação é **sim**, pela FR-035 da `001`: a escrita não tem destino. A alternativa
— mantê-lo aberto — pede justificar para que serve um Requerimento que nenhum ato considerará.

Decidido o sim, a correção é uma revisão curta da `029` (acréscimo à FR-374 ou à FR-411), com a
implementação acima. É independente da `118`, que não muda regra.
