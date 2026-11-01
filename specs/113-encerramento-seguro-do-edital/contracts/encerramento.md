# Contrato: encerrar e cancelar o Edital (113)

## Serviço

`POST /api/v1/admin/editais/{id}/encerramentos` — inalterado na entrada (motivo, `If-Match`,
`Idempotency-Key`). Saídas:

| Situação | Status | Corpo |
|---|---|---|
| sem impedimento | 200 | o Edital, `status: ENCERRADO` (como hoje) |
| com impedimento | **409** | problem+json, `code: pendencias_impeditivas`, `detail`: "Antes de encerrar, resolva: " + frases separadas por "; " + "." |
| estado final ou não publicado | 409 | `invalid_state`, como hoje |
| repetição do pedido já concluído | 200 | o mesmo ato, como hoje — a repetição não reconfere |

`POST /api/v1/admin/editais/{id}/cancelamentos` — **nenhuma saída nova**: nunca responde
`pendencias_impeditivas`.

A recusa não grava `AtoAdministrativo`, `RegistroAuditoria` nem muda `revision`; o registro de recusa
de domínio (`log_domain_rejection`) continua como em toda recusa.

## Tela `interface:ato` (encerrar, cancelar)

Ordem dos blocos em `confirmar.html`:

1. erro do POST, quando houver;
2. **encerrar, com impedimento**: bloco de erro "Antes de encerrar, resolva N pendência(s)" — uma linha
   por situação: frase, e o caminho (R-006) ou "peça a …";
3. **advertências**: bloco de aviso — "Continuam depois do encerramento" (encerrar) ou "Serão atingidos
   pelo cancelamento" (cancelar);
4. **encerrar, sem impedimento nem advertência**: "Nenhuma pendência registrada no GPS impede o
   encerramento.";
5. consequências do ato;
6. formulário; sem "Confirmar" enquanto houver impedimento (`recusa_certa`).

### Frases (encerrar)

| Tipo | Frase |
|---|---|
| `PERIODO_EM_CURSO` | "O período de inscrições vai até DD/MM/AAAA às HH:MM. Encerrar antes disso não é conclusão regular: altere o período por Retificação ou cancele o Edital." |
| `PERIODO_POR_ABRIR` | "O período de inscrições ainda não começou (abre em DD/MM/AAAA às HH:MM). Para desistir do Edital, cancele-o." |
| `PRAZO_RECURSAL_EM_CURSO` | "O prazo de recurso contra «marco» vai até DD/MM/AAAA às HH:MM." |
| `RECURSO_AGUARDANDO` | "N recurso(s) aguarda(m) decisão." |
| `REAVALIACAO_PENDENTE` | "Reavaliação determinada em recurso ainda não concluída em «marco»." |
| `PROVIDENCIA_PENDENTE` | "Providência determinada em recurso ainda não cumprida em «marco»." |
| `RETIFICACAO_HOMOLOGADA` | "A Retificação de DD/MM/AAAA foi homologada e não publicada. Publique-a ou devolva-a." |
| `CONVOCACAO_AGUARDANDO` | "N convocação(ões) aguarda(m) resposta, até DD/MM. O desfecho continua podendo ser registrado." |
| `CONVOCACAO_VENCIDA` | "N convocação(ões) com prazo encerrado sem registro de desfecho." |
| `RESULTADO_NAO_DIVULGADO` | a frase da `099` (`texto_da_pendencia`) |
| `DEFINITIVO_NAO_PUBLICADO` | idem |
| `APURACAO_DESATUALIZADA` | idem |
| `RETIFICACAO_EM_CURSO` | "A Retificação de DD/MM/AAAA, em elaboração (ou em revisão), não poderá mais prosseguir." |
| `PRAZO_RECURSAL_NAO_DECLARADO` | "O Edital não declarou prazo de recurso contra «marco»: recursos continuam podendo ser interpostos depois do encerramento." |
| `PERIODO_SEM_TERMINO` | "O Edital não declarou o término das inscrições: o encerramento põe fim ao recebimento." |
| `RASCUNHOS_NAO_ENVIAVEIS` | "N inscrição(ões) em preenchimento não poderá(ão) ser enviada(s)." |

Nenhuma frase cita pessoa (FR-3540). As advertências da `099` usam a frase dela, sem o nome do Perfil
quando o Perfil for omitido pela regra de privacidade da `099`.

### Consequências de `encerrar` (substituem as atuais)

- "O Edital passa a Encerrado e deixa de receber inscrição e Retificação."
- "O que aparece acima como continuando segue possível, e consta do Relatório do Edital."
- "Publicações, documentos e histórico permanecem disponíveis na consulta pública."

## Seção "Retificações em curso"

Para Edital em `ENCERRADO` ou `CANCELADO`, no lugar do bastão: "Não pode mais prosseguir: o Edital foi
encerrado." (ou "cancelado"). Sem "Continuar a elaboração".
