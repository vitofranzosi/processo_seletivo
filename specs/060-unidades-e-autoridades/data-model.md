# Data Model: Unidades institucionais e autoridades de publicação

Duas tabelas novas no app `unidades` (research R-001), e colunas novas em duas tabelas append-only
que já existem. Nenhuma chave estrangeira nova em `ProcessoSeletivo`, `Edital` ou auditoria
(`D-001`).

---

## Unidade — `unidades.Unidade`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, pk | gerado; existe porque `record_event` exige pk UUID |
| `codigo` | texto (100), único | igual ao valor de `institution_scope`; **imutável** (FR-1107, FR-1108) |
| `sigla` | texto (30) | obrigatório — *"Cefor"*, *"Serra"*, *"Reitoria"* |
| `nome` | texto (255) | obrigatório, por extenso — *"Centro de Referência em Formação e em Educação a Distância"* |
| `cabecalho` | lista JSON de 1 ou 2 textos | as linhas que o nome ocupa no cabeçalho dos documentos (FR-1106) |
| `local` | texto (120) | *"Vitória (ES)"* — o local do ato no fecho (FR-1113) |
| `ativa` | booleano | `false` = desativada; nunca excluída (FR-1109) |
| `registrada_em` | instante | da primeira sincronização |
| `alterada_em` | instante, nulo | da última mudança aplicada |

**Restrições no banco** (R-006): `codigo` único; gatilho recusa `DELETE`; gatilho recusa `UPDATE`
que mude `codigo`; `CHECK` de 1 a 2 linhas em `cabecalho`.

**Origem**: `unidades/unidades.json`, aplicado por `sincronizar_unidades` (R-003,
[contrato](contracts/registro-de-unidades.md)). Nenhuma tela escreve nesta tabela.

**Transições**: `ativa → desativada` e `desativada → ativa`, pelo arquivo. Desativada não recebe
Processo nem Edital novo (FR-1110); o que já existe nela continua operando, e as Autoridades dela
continuam sendo cadastradas, corrigidas e encerradas.

---

## Autoridade habilitada — `unidades.AutoridadeHabilitada`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, pk | gerado; nunca digitado nem exibido (FR-1117); é o que a Publicação congela em `signatory_id` |
| `unidade` | FK → Unidade, `PROTECT` | a unidade **por cujos atos** responde, não a lotação (FR-1118, `D-003`) |
| `cargo` | texto (255) | obrigatório |
| `nome` | texto (255) | opcional (`054`, FR-992) |
| `ato_de_nomeacao` | texto (255) | opcional; delegação, quando houver, é dita aqui |
| `inicio_vigencia` | data | obrigatório |
| `fim_vigencia` | data, nula | nula = aberta; `fim ≥ início` (FR-1120) |
| `cadastrada_por`, `cadastrada_em` | sujeito, instante | do ato de cadastrar |
| `encerrada_por`, `encerrada_em` | sujeito, instante, nulos | do ato de encerrar |
| `usada_em` | instante, nulo | primeiro ato praticado com ela (R-004); preenchido pela publicação |

Só isso: sem CPF, matrícula, contato ou foto (FR-1116; `007`, FR-044).

**Restrições no banco** (R-006):

- `CHECK (fim_vigencia IS NULL OR fim_vigencia >= inicio_vigencia)`;
- `CHECK` de completude do encerramento: `encerrada_em` e `encerrada_por` nulos juntos, e não nulos
  só com `fim_vigencia` preenchido — no molde de `ck_membro_inativacao_completa` da Comissão;
- gatilho recusa `DELETE`;
- gatilho recusa `UPDATE` de `unidade_id`, sempre (FR-1121);
- gatilho recusa, quando `OLD.usada_em IS NOT NULL`, `UPDATE` de `nome`, `cargo`,
  `ato_de_nomeacao` e `inicio_vigencia`, e `fim_vigencia` anterior ao dia do primeiro uso no fuso
  institucional (FR-1120, FR-1121, `D-004`). A regra inteira do encerramento retroativo — fim ≥ dia
  do encerramento — é do domínio (R-006).

**Vigência** (FR-1119): vigente na data `d` ⇔ `inicio_vigencia ≤ d` e (`fim_vigencia` nula ou
`d ≤ fim_vigencia`). `d` é a data do ato no fuso institucional. O fim é inclusivo: encerrada com fim
hoje, a autoridade é oferecida hoje e deixa de ser amanhã (FR-1120).

**Situações, derivadas da data de hoje** (UX-149): *futura* (`início > hoje`), *vigente*,
*encerrada* (`fim < hoje`). Não há coluna de situação: ela é função da vigência, e uma coluna
divergiria dela à meia-noite.

**Operações**:

| Operação | Permissão | Pré-condição | Efeito | Auditoria |
|---|---|---|---|---|
| cadastrar | `autoridade:gerir`, escopo = unidade | Unidade **registrada** do escopo, ativa ou desativada (FR-1110) | cria a linha | `CADASTRAR_AUTORIDADE` |
| corrigir | idem | `usada_em` nula; Unidade registrada do escopo | altera nome, cargo, ato de nomeação ou início | `CORRIGIR_AUTORIDADE`, antes e depois |
| encerrar | idem | `fim_vigencia` nula ou ≥ hoje; novo fim ≥ início **e ≥ hoje** (FR-1120) | grava fim, quem e quando | `ENCERRAR_AUTORIDADE` |
| usar (publicar) | a do ato de publicar | vigente na data do ato, da Unidade do Edital | `usada_em` se nula | a do ato de publicar |

Todas travam a linha (`select_for_update`) — R-005.

---

## Publicação — `publicacoes.Publicacao` (append-only, já existe)

Colunas **novas**, preenchidas no ato e nunca mais alteradas (FR-1128, R-007):

| Campo | Tipo | Origem |
|---|---|---|
| `unidade_codigo` | texto (100) | `Unidade.codigo` |
| `unidade_sigla` | texto (30) | `Unidade.sigla` |
| `unidade_nome` | texto (255) | `Unidade.nome` |
| `unidade_cabecalho` | lista JSON | `Unidade.cabecalho` |
| `unidade_local` | texto (120) | `Unidade.local` |

Colunas **existentes**, agora lidas da `AutoridadeHabilitada` em vez do dicionário recebido:
`signatory_id` ← `id`, `signatory_name` ← `nome`, `signatory_role` ← `cargo`,
`signatory_appointment` ← `ato_de_nomeacao`.

Migration: `publicacoes/0010`, `ADD COLUMN` com padrão constante (vazio / `[]`).

---

## Publicação de Resultado — `divulgacao.PublicacaoResultado` (append-only, já existe)

Colunas **novas**: as mesmas cinco `unidade_*`, e `signatario_ato_de_nomeacao` (texto 255).
Migration: `divulgacao/0004`.

`conteudo_publico.cabecalho` ganha duas chaves, entram no resumo canônico, e são o que o documento e
a página do Resultado leem:

```json
{
  "signatario_ato_de_nomeacao": "Portaria nº …",
  "unidade": {"sigla": "Cefor", "nome": "Centro de Referência …", "cabecalho": ["…", "…"]}
}
```

---

## O que lê o quê

```text
unidades.json ──sincronizar_unidades──▶ Unidade ◀──FK── AutoridadeHabilitada
                                          ▲                     ▲
              (codigo = institution_scope)│                     │ select_for_update
                                          │                     │
   Processo/Edital ──criação confere────── ┘     publish_edital / publish_retification / publicar_resultado
                                                                │
                                                                ▼ congela
                                         Publicacao.unidade_* + signatory_*   PublicacaoResultado.unidade_* + signatario_*
                                                                │                         │
                                         render_edital_pdf(unidade=…)        conteudo_publico → render_resultado_pdf
                                                                │
                              VersaoConsolidada.source_publication ──▶ comprovante (FR-1115)
```
