# Data Model — 166 · A verificação da autodeclaração por vídeo

As decisões que justificam cada forma estão em [research.md](research.md).

## EtapaAvaliacao (elaboração) — coluna nova

| Campo | Tipo | Regra |
|---|---|---|
| `admite_video` | booleano, padrão `False` | a publicação recusa `True` fora da Etapa colegiada com alcance e período, e com a chave desligada (D-002) |

Migration `editais/0032_admite_video`. Não é append-only.

## Conteúdo publicado — degrau 25

Em cada item de `stages`: `videoOption`, `true` ou `false`. A elevação de toda versão anterior
escreve `false` (`DEGRAUS[25]`). Contrato de mutabilidade: `("stages", "videoOption")` retificável,
com a recusa de retirar depois do primeiro vídeo (FR-7105).

## App `verificacao`

### EnvioDoVideo — transitório, mutável

`verificacao_envio_do_video`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `inscricao` | FK `Inscricao`, `PROTECT` | — |
| `edital` | FK `Edital`, `PROTECT` | o da inscrição |
| `etapa_id` | UUID | a identidade publicada |
| `tamanho` | inteiro | declarado no início; ≤ teto do vídeo |
| `recebido` | inteiro | deslocamento já gravado; `0 ≤ recebido ≤ tamanho` |
| `formato` | texto | `video/mp4` ou `video/webm` (o tipo base, sem codecs) |
| `duracao_medida` | decimal (segundos) | a do aparelho; ≤ teto |
| `marcas` | JSON | lista de `{passo, instante}` em segundos, crescente |
| `roteiro` | texto | a versão do roteiro exibida |
| `declarou_maioridade` | booleano | sempre `True` (FR-7109) |
| `iniciado_em` | instante | — |
| `arquivo` | texto | caminho temporário no armazenamento privado |

Um envio aberto por inscrição e Etapa (`UniqueConstraint`): iniciar outro substitui e apaga o
temporário do anterior (FR-7125). É apagado ao concluir. **Não é ato do certame**: é a fila de um
upload, e a linha some com ele.

### VideoDaVerificacao — append-only

`verificacao_video`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | o número do comprovante |
| `inscricao`, `edital`, `etapa_id` | como no envio | — |
| `arquivo` | texto | caminho final, `verificacao/<inscricao>/<id>.<ext>` |
| `sha256` | texto, 64 hex | — |
| `tamanho` | inteiro | — |
| `duracao` | decimal | a do contêiner quando ele a declara; senão a medida |
| `formato` | texto | `video/mp4` ou `video/webm` |
| `roteiro` | texto | — |
| `marcas` | JSON | — |
| `declarou_maioridade` | booleano | `True` |
| `substitui` | FK self, nulo, `PROTECT`, **único** | o vídeo que este trocou (FR-7124) |
| `recebido_em` | instante | — |

**Vigente** = o que nenhum outro substitui. `UniqueConstraint` em `substitui` garante que dois envios
concorrentes não trocam o mesmo vídeo; a conclusão trava a inscrição (`select_for_update`) para que o
primeiro vídeo também seja único (FR-7152). Gatilho `verificacao_video_append_only`.

### AberturaDoVideo — append-only

`verificacao_abertura_do_video`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | o identificador de abertura guardado na sessão |
| `video` | FK `VideoDaVerificacao`, `PROTECT` | — |
| `pessoa` | texto (`subject`) | — |
| `papel` | `COMISSAO` ou `TITULAR` | só `COMISSAO` encerra a troca (FR-7124) |
| `aberta_em` | instante | — |

Gatilho `verificacao_abertura_append_only`. A troca trava o vídeo vigente e confere que não há
abertura `COMISSAO`; a abertura da comissão trava o mesmo vídeo — serializadas (FR-7152).

### EncaminhamentoAoVivo — append-only

`verificacao_encaminhamento`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `inscricao`, `edital`, `etapa_id` | — | **único** (`edital`, `etapa_id`, `inscricao`) (FR-7143) |
| `video` | FK `VideoDaVerificacao`, `PROTECT` | o vigente no ato |
| `pareceres` | JSON | as identidades das Avaliações reabertas |
| `registrado_em` | instante | — |
| `registrado_por` | texto | — |

Gatilho `verificacao_encaminhamento_append_only`.

### EliminacaoDoVideo — append-only

`verificacao_eliminacao_do_video`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `video` | FK `VideoDaVerificacao`, `PROTECT`, **único** | — |
| `eliminado_em` | instante | — |
| `prazo_em_dias` | inteiro | o aplicado |
| `encerramento_em` | instante | o marco da contagem |

Gatilho `verificacao_eliminacao_append_only`.

`TABELAS_APPEND_ONLY`: `M` 61 → **65**.

## Estados do meio (derivados, sem coluna)

```text
INDISPONIVEL ── (chave, admissão, alcance, maioridade, titularidade)
PODE_GRAVAR ──(conclusão do envio)──► RECEBIDO ──(abertura da comissão)──► EM_ANALISE
     │                                   │  └──(troca)──► RECEBIDO
     │ (fim do período, ou parecer       │
     │  concluído sem vídeo)             └──(encaminhamento)──► ENCAMINHADA (ao vivo)
     ▼
  AO_VIVO (padrão; nada se grava)
EM_ANALISE ──(deliberação favorável)──► Resultado da 165
EM_ANALISE ──(deliberação não favorável)──► ENCAMINHAR (na conferência) ──► ENCAMINHADA
```

**Em modo vídeo** = `RECEBIDO` ou `EM_ANALISE`. Nenhuma transição do meio leva a "não confirmada".
