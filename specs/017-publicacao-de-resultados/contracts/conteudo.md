# Contrato — a forma do conteúdo congelado

O que a publicação grava, como é canonizado e o que é proibido conter.

## 1. A forma

```text
{
  "versao_do_formato": 1,
  "cabecalho": {
    "titulo": "Resultado preliminar — Professor de Matemática",
    "natureza": "PRELIMINAR",
    "natureza_rotulo": "Resultado preliminar",
    "processo": "Processo Seletivo Simplificado 3/2026",
    "edital": "Edital 14/2026",
    "perfil": "Professor de Matemática",
    "marco": "Classificação final",
    "publicado_em": "2026-10-18T17:42:00-03:00",
    "signatario_nome": "Diretora do Cefor",
    "signatario_cargo": "Diretora-Geral do Centro de Referência…",
    "ato": { "id": "…", "emitido_em": "2026-10-17T09:12:00-03:00" }
  },
  "publico": [
    { "posicao": 1, "compartilhada": false, "candidato": "Ana Silva",
      "protocolo": "INS-2026-K7M4Q2PX", "modalidade": "Ampla concorrência",
      "pontuacao": "185,00" }
  ],
  "individual": {
    "<inscricao_id>": { "situacao": "CLASSIFICADA", "posicao": 1,
                        "pontuacao": "185,00", "motivo": "" }
  }
}
```

## 2. Convenções

Herdadas do conteúdo publicado do Edital, e pelas mesmas razões:

- **texto ausente é `""`**, nunca `null` e nunca chave omitida;
- **decimal já vem formatado como texto**, na apresentação institucional (`185,00`) — o número não
  é reformatado na renderização, porque reformatar é decidir de novo;
- **todo campo é obrigatório**: a forma publicada não tem campo opcional.

`versao_do_formato` existe para que uma mudança futura de projeção seja **legível** no histórico, e
não silenciosa. Publicações antigas continuam na versão em que nasceram, e são renderizadas por ela.

## 3. Canonização

`canonical_bytes` / `canonical_sha256` de `shared/canonical.py:86-94` — `sort_keys=True`,
`separators` sem espaço, NFC, UTF-8. Os mesmos bytes vão para `conteudo`; o resumo vai para
`conteudo_hash`, aparece no documento (FR-061) e é o que a SC-004 confere.

## 4. O que `publico` não pode conter

Verificado por teste de contrato sobre os bytes gravados, e não sobre a intenção do código:

- CPF, e-mail, telefone, `identity_subject`, identificador de `Inscricao`;
- qualquer valor vindo de `PosicaoNaOrdem.desempate` — a coluna **não é lida** (FR-020);
- `motivo` de quem não recebeu posição (esse vive em `individual`);
- UUID de qualquer espécie fora de `cabecalho.ato.id`;
- enum canônico como texto de apresentação (FR-013).

## 5. `individual`

Chaveado por identificador de `Inscricao`, com `situacao` em `CLASSIFICADA` \| `SEM_POSICAO`. É a
face interna do mesmo snapshot (T-010): a Área do Candidato lê a chave da própria Inscrição, e
nenhum caminho do `portal/views.resultado` a alcança.

O teste que sustenta isso afirma sobre o **HTML renderizado** da página pública: nenhum protocolo,
nome ou motivo de quem está apenas em `individual` aparece ali.
