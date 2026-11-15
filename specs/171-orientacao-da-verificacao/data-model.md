# Data Model: A orientação da verificação da autodeclaração

Quase tudo é derivado. O que se grava é só o que o aviso precisa.

## Derivados (não guardados)

### Passo (portal, por inscrição × Etapa restrita)

| Campo | Origem |
|---|---|
| `etapa` | o dict da Etapa no conteúdo vigente (`id`, `name`) |
| `modalidade` | o nome da Modalidade da inscrição, do Perfil no conteúdo |
| `inicio`, `fim` | `periodo_da_etapa(conteudo, etapa)`; `None` sem Evento |
| `estado` | `FALTA` · `AGUARDA_COMISSAO` · `AGUARDA_RESULTADO` (abaixo) |
| `efeito_da_ausencia` | `efeito_da_ausencia(etapa)`: `RETIRA_DA_RESERVA` ou `ELIMINA` |
| `video` | a `Situacao` da `166`, só com a chave ligada e a Etapa admitindo o vídeo; senão `None` |

**Estado**, avaliado nesta ordem, só para a Etapa restrita que alcança a inscrição, de que ela
participa e cujo Resultado não está visível:

1. há parecer concluído ou Resultado vigente → `AGUARDA_RESULTADO`;
2. `fim` existe e `agora > fim` → `AGUARDA_COMISSAO`;
3. senão → `FALTA`.

Com o vídeo, os estados `RECEBIDO` e `EM_ANALISE` da `166` dão `AGUARDA_RESULTADO`; `PODE_GRAVAR` e
`ENCAMINHADA` dão `FALTA`; `AO_VIVO` e `INDISPONIVEL` seguem a regra acima.

### Fatos da Etapa restrita (gestão, por Etapa)

`faltam_por_membro` (lista de nome × contagem, só contagem > 0, decrescente), `nao_avisadas`,
`sem_desfecho_vencido`, `fim` e, com o vídeo admitido, `a_encaminhar`. Ver T-006 e T-007.

## Gravados (migration `avisos/0004_origem_passo`)

### `Aviso` (append-only; gatilhos sem mudança)

| Campo | Mudança |
|---|---|
| `origem` | aceita `PASSO` |
| `marco_id` | passa a aceitar nulo |
| `etapa_id` | novo, UUID, nulo |
| `perfil_id` | passa a aceitar nulo |

CHECKs:

- `ck_aviso_origem_conhecida` com as quatro origens;
- `ck_aviso_ato_da_origem`: `PASSO` ⇒ `etapa_id` não nulo, `marco_id` nulo, `natureza = ''` e
  `referencia_da_publicacao = ''`; as outras três ⇒ `marco_id` e `perfil_id` não nulos e `etapa_id`
  nulo.

Um gesto grava **um** `Aviso` por Etapa (research T-004, revisto), e os `DestinatarioDoAviso` de
sempre.

### `ModeloDeAviso` (mutável, nunca excluído)

| Campo | Mudança |
|---|---|
| `chave_inicial` | novo, texto curto, vazio por padrão; `"PASSO"` no quarto modelo inicial |

## Relações com o que existe

- **Etapa restrita**: `alcance.restrita(etapa)`, da `163`.
- **Participação**: `prontidao.participa_da_etapa`, da `163`.
- **Visibilidade**: `resultados_visiveis`, da `164`.
- **Efeito da ausência**: `efeito.efeito_da_ausencia`, da `164`.
- **Situação do vídeo**: `disponibilidade.situacao`, da `166`.
