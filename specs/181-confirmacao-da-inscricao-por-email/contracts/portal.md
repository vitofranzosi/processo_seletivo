# Contrato: o portal e a mensagem

## `GET /selecoes/inscricoes/<id>/comprovante` (`portal:comprovante`) — muda

| Situação | Resposta |
|---|---|
| Sem sessão de candidato | `302` para `portal:acesso?destino=<caminho deste comprovante>`, **antes** de qualquer consulta; o mesmo para identificador real, inventado ou alheio (FR-8357) |
| Sessão de outra pessoa, ou inscrição inexistente | `404`, como antes |
| Rascunho da titular | `302` para a inscrição, como antes |
| Enviada da titular | `200`; topo "✓ Inscrição enviada" (FR-8365); o aviso da confirmação pela última tentativa (FR-8362) |

O aviso da confirmação, sempre com a classe `nao-imprime` (FR-8366):

- **sem tentativa**: nada.
- **última `ENVIADA`**: "Enviamos a confirmação para ‹e-mail da inscrição› em ‹dd/mm/aaaa› às ‹hh›h‹mm›.
  Se não a encontrar, procure na caixa de spam."
- **última `NAO_ENVIADA`**: "Não conseguimos enviar a confirmação para ‹e-mail›. Sua inscrição foi
  enviada do mesmo jeito, e este comprovante vale como prova: baixe o PDF abaixo." e o formulário
  `POST` com o botão secundário "Enviar a confirmação de novo" (UX-1022).

## `POST /selecoes/inscricoes/<id>/comprovante/confirmacao` (`portal:comprovante-confirmacao`) — novo

| Situação | Resposta |
|---|---|
| `GET` | `405` |
| Sem sessão, sessão de outra pessoa, inscrição inexistente ou rascunho | `404`, e nada sai (FR-8364) |
| Enviada da titular | `confirmacao.confirmar`; `302` para `portal:comprovante`. Se já houve tentativa aceita, nada sai e nada se registra (FR-8351) |

CSRF exigido, como todo `POST` do portal. Resposta privada (`Cache-Control: private, no-store`).

## A mensagem

- **Destinatário**: o e-mail gravado na inscrição; um só, sem cópia; `Auto-Submitted: auto-generated`.
- **Assunto**: `Sua inscrição foi enviada — Edital ‹número›/‹ano›` (FR-8353).
- **Corpo** (texto puro e HTML com o mesmo conteúdo): título "Sua inscrição foi enviada."; Processo
  Seletivo e Edital; protocolo e código de verificação em destaque; Perfil de vaga, Concorrência,
  "Enviada em"; documentos enviados; "O que acontece agora"; o link "Ver meu comprovante" para o
  endereço absoluto de `portal:comprovante`; a nota de acesso por código; a assinatura da unidade.
- **Nunca**: CPF, telefone, data de nascimento, anexo, link que autentica, "recebida", "aceita",
  "deferimento", "homologação" (FR-8354, FR-8356).

## `inscricoes.application.confirmacao`

```text
confirmar(*, inscricao, ator, montar_dados, correlation_id="") -> Tentativa | None
tentativas(inscricao) -> list[Tentativa]
ultima(inscricao) -> Tentativa | None
```

`confirmar` devolve `None` quando não tentou (inscrição não enviada, ou já confirmada); `montar_dados`
só é chamado quando há envio.
