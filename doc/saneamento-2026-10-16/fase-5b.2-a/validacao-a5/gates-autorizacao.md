# Gates independentes de autorização

O plano A.5 não aprova nenhum gate. A atividade documental autorizada e concluída é distinta de G1, que exige resolução formal da integridade.

| Gate | Pré-condições e responsável proposto, sem identidade presumida | Evidência exigida / critério de aceite | Estado atual | Recusa/interrupção |
|---|---|---|---|---|
| G1 — Integridade documental | Responsável do produto escolhe estratégia; responsável técnico prepara I1; revisor confirma procedência | Deliberação formal, comparação dos 11 caminhos, cadeia antiga/atual/sucessora e preservação; referência bruta aprovada | PENDENTE; diagnóstico pronto, resolução não aprovada | Causa/diferença nova ou referência sem aprovação; não recalcular para liberar |
| G2 — Controles técnicos | Revisão aprovada, I2–I5; responsável técnico e revisor de segurança | Guardas estáticas, testes puros e, em autorização própria, evidência de processo sintético Windows sem órfãos; controles de tempo/saída/custódia completos | PENDENTE; mecanismos ausentes/parciais | Falha de negativa, processo fora do job, captura ilimitada, guarda ignorada |
| G3 — Preparação operacional | Técnico, executor/supervisor e custodiante designados; sem presumir nomes | Binários e runtime confiáveis, caminho/hash, endpoint exato já ativo/local sem autoativação, janela, destino/ACL/retenção, timeout e interrupção confirmados | PENDENTE; campos humanos e host não confirmados | Qualquer pendência; não testar engine para descobrir endpoint |
| G4 — Autorização expressa | Autoridade humana aprovadora identificada; G1–G3 aceitos com hashes finais | Deliberação específica de uma tentativa, comando/argumentos, binários, endpoint, janela, limite temporal e gravação exclusiva do recibo; sem retry | PENDENTE; nenhuma autorização operacional concedida | Autorização genérica, expirada, reutilizada ou de revisão diferente |
| G5 — Execução supervisionada | Executor e supervisor; G4 válido e todas as pré-condições reconferidas | Uma consulta autorizada, registros sanitizados, tempo/resultado, contenção e término; sem operações adicionais | NÃO EXECUTADO — BLOQUEADO | Pedido humano, timeout, saída fora do contrato, hash/endpoint alterado; cancelar só cliente autorizado |
| G6 — Validação posterior | Técnico/revisor/custodiante; tentativa encerrada | Término/descendentes comprovados, hashes preexistentes preservados, recibos íntegros, revisão dos efeitos e aceite formal | PENDENTE; depende de G5 | Órfão suspeito, evidência ausente, efeito inesperado; operação não encerrada formalmente |

G1–G4 são cumulativos para uma eventual consulta. Nenhum aceite parcial libera G5. G6 não pode ser aprovado antecipadamente. Estado do host, ausência de efeitos indiretos e comportamento da engine não são provados por este plano.

## Autorizações que permanecem separadas

- Preparar I1 não autoriza modificar manifestos históricos ou controles atuais.
- Preparar código exclusivo e testar stubs não autoriza iniciar processos sintéticos; estes exigem escopo próprio.
- Confirmar pessoas, binário e janela não autoriza Docker.
- Autorizar inspecionar não autoriza conferir, Compose, pull/build, criação, parada de serviços, SQL, aplicação, demonstrações ou descarte.
- Gravar recibo deve estar explicitamente incluído, com destino/custódia; não autoriza outras gravações.

## Pontos de decisão humana

Escolha da alternativa; aprovação dos caminhos e incrementos; atribuição de executor/supervisor/revisor/custodiante; aceitação dos limites propostos de 30 s + 5 s, saída e retenção; confirmação do endpoint e confiança dos binários; revisão final do comando e autorização nominal. Tudo permanece pendente até resposta expressa com evidência correspondente.

