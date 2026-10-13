# Contrato — Telas da gestão (066)

*Rotas sob o `interface:` existente. Todas são POST-redirect-GET, nenhuma usa htmx. Todas exigem
sessão de gestão e filtram pelo escopo do ator: objeto de outra unidade responde como inexistente
(`FR-1276`). Com `AVISOS_AOS_CANDIDATOS` desligada (`R-013`, `FR-1282`):

- "Avisar candidatos" aparece **sem ação**, com "O envio de avisos está desabilitado nesta
  instalação";
- a prévia de aviso e de reenvio abre só com essa explicação, sem formulário;
- o POST de confirmação recusa com `aviso_envio_desabilitado`;
- histórico, interrupção e modelos continuam como sempre.*

## Rotas

| Rota | Nome | GET | POST | Porta (`D-004`) |
|---|---|---|---|---|
| `editais/<e>/marcos/<m>/avisos/novo?natureza=` | `aviso-do-resultado` | prévia: publicações não avisadas, universo, contagens, mensagem para uma pessoa real | confirma | `aviso:enviar` ou base de comissão |
| `editais/<e>/marcos/<m>/convocacao/avisos/novo?lista=&comunicacao=<id>` | `aviso-da-chamada` | prévia: o universo da referência daquela comunicação, elegíveis e não elegíveis com motivo | confirma | base de comissão |
| `avisos/<id>` | `aviso` | histórico: texto enviado, ato citado, contagens por estado, destinatários paginados, alerta de despacho parado | — | quem pode enviar pela origem, ou `auditoria:consultar` |
| `avisos/<id>/interromper` | `aviso-interromper` | confirmação: quantas já foram aceitas e não voltam (`UX-177`) | interrompe, com motivo | a mesma porta do envio |
| `avisos/<id>/reenviar?estado=` | `aviso-reenviar` | prévia do aviso filho, com os destinatários do estado (falha definitiva e expirada sem envio; ou indeterminada e interrompido antes do envio, com justificativa e texto editável) | confirma o reenvio (`R-011`) | a mesma porta do envio |
| `editais/<e>/avisos` | `avisos-do-edital` | lista dos avisos do Edital | — | como `aviso` |
| `modelos-de-aviso` | `modelos-de-aviso` | lista dos modelos da unidade, ativos e inativos | — | `aviso:enviar` |
| `modelos-de-aviso/novo` | `modelo-de-aviso-novo` | formulário | cria | `aviso:enviar` |
| `modelos-de-aviso/<id>` | `modelo-de-aviso` | formulário | salva | `aviso:enviar` |
| `modelos-de-aviso/<id>/situacao` | `modelo-de-aviso-situacao` | — | inativa ou reativa | `aviso:enviar` |

**Pontos de entrada nas telas que já existem**:

- `publicacoes_do_marco.html`: "Avisar candidatos" e a linha de estado (`UX-174`, `UX-175`), uma por
  natureza com publicação vigente não avisada.
- `convocacao.html`: o cartão da chamada por publicação, só quando o Perfil declara `PUBLICATION`
  (`FR-1245`).

## Campos da confirmação

`chave` (idempotência, gerada no GET, como em `convocacao.html`), `assinatura` (`R-010`), `modelo`
(opcional), `assunto`, `corpo`, `justificativa` (exigida em reenvio de publicação já avisada ou de
indeterminadas), `salvar_como_modelo` e `nome_do_modelo` (opcionais).

## Recusas (código → quando)

| Código | Quando | Status |
|---|---|---|
| `aviso_sem_ato` | nenhuma publicação vigente da natureza, ou comunicação que não é por publicação | 404 |
| `aviso_sem_publicacao_nova` | todas as publicações vigentes da natureza já avisadas, sem justificativa | 409 |
| `aviso_justificativa_obrigatoria` | reenvio justificado sem texto | 422 |
| `aviso_sem_elegivel` | nenhum destinatário elegível com endereço (`FR-1252`) | 409 |
| `aviso_previa_defasada` | a assinatura não confere (`FR-1259`) | 409 |
| `aviso_variavel_desconhecida` | chave fora da lista fechada (`FR-1256`) | 422 |
| `aviso_variavel_sem_valor` | variável que não existe para a origem, como `{etapa}` na chamada | 422 |
| `aviso_chamada_por_mensagem_individual` | Perfil `INDIVIDUAL_MESSAGE` (`FR-1245`) | 409 |
| `aviso_processo_em_estado_final` | `ensure_processo_accepts_changes` (`FR-1244`) | 409 |
| `aviso_concluido` | interromper um aviso concluído | 409 |
| `aviso_falhas_ja_reenviadas` | segundo reenvio de falhas do mesmo aviso, na prévia ou na confirmação (`FR-1264`) | 409 |
| `aviso_envio_desabilitado` | confirmar aviso ou reenvio com a chave desligada (`FR-1282`) | 409 |
| `idempotency_conflict` | mesma chave com outro conteúdo, como hoje | 409 |

As recusas voltam à mesma tela com o motivo, como `recusa.html`. Cada `Http404` novo entra no
inventário de negativas da `033`.

## Vocabulário obrigatório

- Os resultados são "aceita pelo servidor de correio", "falha", "sem endereço", "resultado
  indeterminado", "não elegível para o aviso", "pendente", "em envio" e "expirado sem envio".
- **Nunca** "entregue", "recebida" ou "lida" (`UX-172`).
- O objeto se chama "aviso", e nunca "comunicação" (`UX-171`).
- O botão diz "Enviar a N pessoas" (`UX-173`).
