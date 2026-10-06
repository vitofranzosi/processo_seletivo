# Contrato — autoridades habilitadas e a escolha ao publicar

## A tela — `/gestao/autoridades`

**Porta**: permissão `autoridade:gerir` (do Gestor, `D-005`), por `require_authorization_base`. Sem
ela, 403 que nomeia a permissão e a quem pedir (`037`, FR-543). O acesso é pelo botão *"Autoridades
da unidade"* na Lista de Editais, visível só com a permissão.

**Escopo**: a Unidade do escopo do operador. Escopo sem Unidade registrada: a tela diz *"<código>
não é uma unidade registrada no sistema."* e não oferece cadastro.

**Leitura** (UX-149): três grupos, nesta ordem — *Vigentes*, *A partir de <data>* (futuras),
*Encerradas*. Cada linha: cargo; nome, quando houver; ato de nomeação, quando houver; o período
(*"desde 06/10/2026"*, *"de 06/10/2026 a 31/12/2026"*); e, nas já usadas, *"Já usada em ato
publicado — para corrigir, encerre e cadastre outra."*

**Ações** — POST na mesma rota, com `acao` e `chave_idempotencia`, e redirecionamento para
`?feito=<acao>`:

| `acao` | Campos | Recusas (422, com a tela de volta e o erro nomeado) |
|---|---|---|
| `cadastrar` | `cargo`*, `nome`, `ato_de_nomeacao`, `inicio_vigencia`* | cargo vazio; data inválida |
| `corrigir` | `autoridade`, `cargo`*, `nome`, `ato_de_nomeacao`, `inicio_vigencia`* | `autoridade_ja_usada` (FR-1121); início depois do fim |
| `encerrar` | `autoridade`, `fim_vigencia`* | fim antes do início; `encerramento_retroativo` — fim antes de hoje, no fuso institucional (FR-1120); já encerrada com fim passado |

**Unidade desativada** (FR-1110): as três ações continuam disponíveis, com a mesma permissão e o
mesmo escopo. A desativação só impede Processo e Edital novos.

**O fim é inclusivo**: encerrar com fim hoje mantém a autoridade nas opções de publicação hoje e a
retira a partir de amanhã. A tela diz isso ao lado do campo: *"A autoridade continua disponível até
o fim deste dia."*

`autoridade` de outra unidade ou inexistente: **404**, inventariado na `033` como *"escopo
institucional ∪ inexistente"* (FR-1122).

## Publicar — a escolha

As três telas de publicação (Edital, Retificação, Resultado) e o gesto do marco:

- oferecem `autoridades_vigentes(unidade_do_edital, hoje)`, na ordem cargo, nome;
- cada opção diz `rotulo_da_autoridade(a)`: `quem_assinou(nome, cargo)` e, se houver,
  `· <ato de nomeação>` (UX-148);
- o valor enviado é o identificador da autoridade;
- **sem nenhuma vigente**: no lugar do seletor, *"Nenhuma autoridade vigente para <sigla> hoje.
  Quem tem a permissão de gerir autoridades da unidade as cadastra."*, e o botão de confirmar
  desabilitado (FR-1127).

## Publicar — os comandos

| Comando | Recebia | Recebe |
|---|---|---|
| `publish_edital` | `signatory={authorityId, name, role, appointment}` | `autoridade_id` |
| `publish_retification` | `signatory={…}` | `autoridade_id` |
| `publicar_resultado` | `autoridade="<chave do catálogo>"` | `autoridade="<identificador>"` |

Todos chamam `autoridade_para_o_ato(autoridade_id, unidade_codigo=edital.institution_scope,
data_do_ato=now.astimezone(ZONA).date())` dentro da transação, antes de gravar a Publicação.

| Código | HTTP | Quando | Mensagem |
|---|---|---|---|
| `signatario_obrigatorio` | 422 | nenhum identificador | *"Escolha a autoridade que responde por este ato."* |
| `autoridade_indisponivel` | 422 | inexistente **ou** de outra unidade — indistinguíveis | *"A autoridade escolhida não está habilitada para esta unidade."* |
| `autoridade_fora_de_vigencia` | 422 | fora do período na data do ato | *"A autoridade escolhida não está vigente hoje (período: …)."* |

Em todos, nada é gravado. A repetição com a mesma chave de idempotência devolve o ato já praticado,
sem reverificar (comportamento de hoje).

## A API administrativa

`POST /api/v1/admin/editais/<id>/publicacoes` e `POST /api/v1/admin/retificacoes/<id>/publicacoes`:

```json
{ "signatory": { "authorityId": "<uuid>" }, "reason": "…" }
```

`name`, `role` e `appointment` deixam de ser aceitos: **400** se presentes (research R-014). O
`SignatorySnapshot` do `openapi.yaml` da `001` é emendado.

## A consulta pública

`GET /api/v1/public/publicacoes/<id>` — `signatory` continua `{authorityId, name, role, appointment}`, e a
resposta ganha:

```json
"unit": { "code": "cefor", "acronym": "Cefor", "name": "Centro de Referência em Formação e em Educação a Distância" }
```

lido das colunas congeladas da Publicação (FR-1131), nunca do registro de Unidades.
