# Data Model: A publicação das convocações no GPS (149)

Três tabelas novas no app `convocacao`, na migration `0007_publicacao_de_convocados`. Nenhuma tabela
existente muda de forma (FR-5733, D-002).

## `PublicacaoDeConvocados` — o ato

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | identidade do ato, e do endereço público (FR-5718) |
| `edital` | FK `Edital`, `PROTECT` | |
| `numero` | inteiro positivo | sequencial por Edital, atribuído sob a trava do Processo (D-009) |
| `conteudo_publico` | bytes | `canonical_bytes` do conteúdo composto na confirmação (D-005) |
| `conteudo_publico_hash` | 64 | `canonical_sha256` do mesmo conteúdo |
| `publicado_por` | 255 | o sujeito do ator |
| `publicado_em` | instante | o `now` do comando; igual ao `enviado_em` de cada comunicação gravada (D-003) |
| `declaracao_do_veiculo` | texto | obrigatória com efeito *convoca*; vazia sem ele (D-012) |
| `signatario_id`, `signatario_nome`, `signatario_cargo`, `signatario_ato_de_nomeacao` | | congelados (FR-5709) |
| `unidade_codigo`, `unidade_sigla`, `unidade_nome`, `unidade_cabecalho`, `unidade_local` | | `colunas_da_unidade` |

Constraints: `uq_publicacao_de_convocados_numero` (`edital`, `numero`);
`ck_publicacao_de_convocados_numero_positivo`.

## `ConvocacaoPublicada` — o vínculo

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `publicacao` | FK `PublicacaoDeConvocados`, `PROTECT` | |
| `convocacao` | FK `Convocacao`, `PROTECT` | **única**: `uq_convocacao_publicada_uma_vez` (FR-5707) |
| `comunicacao` | FK `ComunicacaoEmitida`, `PROTECT` | única; no *convoca*, a gravada pelo ato; no *divulga*, a anterior |
| `efeito` | `CONVOCA` ou `DIVULGA` | `ck_convocacao_publicada_efeito` |

Gatilho de coerência `check_published_call_coherence`: a convocação, a comunicação e a publicação são
do mesmo Edital, e a comunicação é da convocação; no `CONVOCA`, a comunicação é `PUBLICATION`,
`ENVIADA` e com `enviado_em` igual a `publicado_em`. É o que o `CHECK` não alcança, porque atravessa
tabelas.

## `DocumentoDaPublicacaoDeConvocados` — o PDF

| Campo | Tipo | Regra |
|---|---|---|
| `publicacao` | 1:1 `PROTECT` | |
| `bytes` | bytes | gerados uma vez, dos mesmos bytes do conteúdo (FR-5710) |
| `content_type` | 100 | `application/pdf` |
| `documento_hash` | 64 | sha256 dos bytes; `ETag` |

## As três camadas append-only

1. `save` só de linha nova e `delete` recusado (`_AppendOnly`).
2. Gatilho `reject_published_call_mutation` em `UPDATE` e `DELETE` nas três.
3. As três em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`): o papel de runtime não recebe `UPDATE`
   nem `DELETE`. O `M` do provisionamento passa de 53 para 56.

## O conteúdo público (`conteudo_publico`)

```json
{
  "versao": 1,
  "cabecalho": {
    "unidade": {"cabecalho": ["…"], "local": "…", "sigla": "…", "nome": "…"},
    "edital": "Edital 12/2026",
    "processo": "…",
    "numero": 1,
    "publicadoEm": "2026-11-11T17:32:00+00:00",
    "signatario": {"nome": "…", "cargo": "…", "atoDeNomeacao": "…"},
    "requerimentoNaConvocacao": false
  },
  "grupos": [
    {
      "perfil": "Tutor a distância",
      "lista": "Ampla concorrência",
      "marco": "",
      "efeito": "CONVOCA",
      "canal": "",
      "vencimento": "2026-11-18T02:59:00+00:00",
      "vencimentoUnico": true,
      "pessoas": [
        {"nome": "…", "protocolo": "INS-2026-0001", "vencimento": "…", "corrige": null}
      ]
    }
  ]
}
```

- `efeito` é por grupo **e** reflete o de cada pessoa do grupo: dentro de um recorte, todas as
  pessoas de uma publicação têm o mesmo efeito, porque o recorte cita uma forma e a prévia separa
  quem é *convoca* de quem é *divulga* em grupos distintos.
- `canal` só no `DIVULGA`: *"por mensagem individual"*, ou a referência externa registrada
  (*"publicada em ‹referência›"*), uma por grupo quando todas coincidem; senão, na linha.
- `corrige` é o número da publicação anterior que divulgou a convocação que esta sucede, ou `null`.
- Nenhum identificador interno (de inscrição, convocação ou pessoa) entra no conteúdo: a página
  pública não tem caminho para eles (D-008).
