# Contrato — a forma do conteúdo divulgado

O que a publicação grava, como é canonizado, o que é proibido conter — e os **dois** resumos, que
cobrem materiais diferentes.

## 1. `conteudo_publico`

```text
{
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
  "posicoes": [
    { "posicao": 1, "compartilhada": false, "candidato": "Ana Silva",
      "protocolo": "INS-2026-K7M4Q2PX", "modalidade": "Ampla concorrência",
      "pontuacao": "185,00" }
  ]
}
```

**Este objeto é tudo o que a leitura pública carrega.** A situação individual de quem foi
considerado mora em `SituacaoDivulgada`, tabela à parte, e nenhuma consulta da página pública a
alcança (T-010, T-013).

## 2. Convenções

Herdadas do conteúdo publicado do Edital, e pelas mesmas razões:

- **texto ausente é `""`**, nunca `null` e nunca chave omitida;
- **decimal já vem formatado como texto**, na apresentação institucional (`185,00`) — o número não é
  reformatado na renderização, porque reformatar é decidir de novo;
- **todo campo é obrigatório**: a forma publicada não tem campo opcional.

**Não há campo de versão do formato.** Ele foi considerado e retirado: prometeria que publicações
antigas continuam sendo renderizadas pela regra em que nasceram, e nada nesta feature entrega isso —
há um renderizador só. Um campo que anuncia garantia que ninguém sustenta é pior que a ausência
dele, porque a próxima pessoa confia nele.

Quando uma mudança de projeção for necessária de verdade, ela virá com o mecanismo que a torna
legível — e a decisão de qual mecanismo é dessa hora, não desta.

## 3. Os dois resumos

Eles cobrem materiais diferentes porque respondem a perguntas diferentes, e confundi-los não fecha:
o instante definitivo da publicação só existe no POST, e um resumo calculado na prévia jamais
coincidiria com um conteúdo que contém `publicado_em`.

| Resumo | Material | Para quê |
|---|---|---|
| `confirmacao_da_previa` | `{ ato_id, publicacao_anterior_id, projecao }` — **sem** instante, sem natureza, sem autoridade | Detectar que o mundo mudou entre ler e confirmar (FR-031) |
| `conteudo_publico_hash` | `conteudo_publico` inteiro, já com o instante real | Provar depois que o que se lê é o que foi divulgado (FR-011, SC-004) |

`projecao` é a lista de posições com os rótulos resolvidos — o que o operador viu e **não podia
alterar**. Fica de fora tudo o que muda legitimamente entre a prévia e o POST:

- **`publicado_em`** — só existe quando o ato acontece;
- **`natureza` e `autoridade`** — são escolha do operador, submetidas no mesmo pedido. Elas não têm
  como ficar obsoletas: não existe leitura anterior delas a comparar. São **validadas** como
  entrada (pertencer ao catálogo, respeitar a ordem entre naturezas), não assinadas.

**`publicacao_anterior_id` está dentro da assinatura**, e é o que cobre o caso em que outra pessoa
publica o mesmo marco entre a prévia e a confirmação: a cadeia mudou, a posição da nova publicação
mudou, e a confirmação é recusada em vez de gravar uma sucessão de algo que já não é a ponta.

Ambos usam `canonical_bytes` / `canonical_sha256` de `shared/canonical.py:86-94` — `sort_keys=True`,
`separators` sem espaço, NFC, UTF-8.

## 4. O que `conteudo_publico` não pode conter

Verificado por teste de contrato sobre os bytes gravados, e não sobre a intenção do código:

- CPF, e-mail, telefone, `identity_subject`, identificador de `Inscricao`;
- qualquer valor vindo de `PosicaoNaOrdem.desempate` — a coluna **não é lida** (FR-020);
- nome, protocolo ou motivo de quem não recebeu posição (FR-017);
- UUID de qualquer espécie fora de `cabecalho.ato.id`;
- enum canônico como texto de apresentação (FR-013).

## 5. `SituacaoDivulgada`

Uma linha por participante considerado, congelada na mesma transação e a partir do mesmo ato
imutável — não é fonte viva, e por isso não é segunda fonte de verdade (FR-058).

| Campo | Valores |
|---|---|
| `situacao` | `CLASSIFICADA` \| `SEM_POSICAO` |
| `posicao`, `compartilhada`, `pontuacao` | Congelados como divulgados; nulos ou vazios quando `SEM_POSICAO` |
| `motivo` | O motivo da não classificação, quando houver |

A Área do Candidato lê a linha da própria Inscrição (FR-059). O teste que sustenta a fronteira
afirma sobre o **HTML renderizado** da página pública: nada de quem está apenas em
`SituacaoDivulgada` aparece ali.
