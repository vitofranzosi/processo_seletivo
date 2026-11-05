# Contrato: a correção da convocação

Dois contratos: o da tela (o POST que o formulário envia e o que volta) e o do comando (o argumento
novo de `convocar`). Os códigos de recusa, os status e onde cada um aparece estão em
[data-model.md](../data-model.md#as-recusas).

## A tela

### `POST /gestao/editais/<edital>/marcos/<marco>/convocacao/convocar` (`interface:convocar`)

A rota é a da chamada individual da `050`. O ramo da correção é escolhido pela presença de `corrige`.

**Pedido** (`application/x-www-form-urlencoded`, com CSRF):

| Campo | Obrigatório | Observação |
|---|---|---|
| `lista` | — | o recorte; vazio é a ampla concorrência |
| `chave` | sim | `‹chave da tela›-corrigir-‹convocação›` |
| `inscricao` | sim | a do cartão |
| `corrige` | sim, para corrigir | o id da convocação vigente do cartão |
| `previa` | sim, para corrigir | a assinatura da prévia |
| `motivo` | sim | texto livre |
| `vencimento` | um dos dois | `datetime-local`, fuso da instituição |
| `evento` | um dos dois | id do Evento do Cronograma publicado |
| `complemento` | — | texto livre |

**Respostas:**

| Situação | Status | Efeito |
|---|---|---|
| corrigida | 302 → a condução do recorte | `acao_da_convocacao = "correcao"`, `resultado_da_convocacao` com os dois vencimentos, o efeito e a comunicação |
| repetição do mesmo formulário | 302 → a condução | o resultado do primeiro envio; nada novo |
| recusa do domínio ou do formulário | 302 → a condução | `recusa_da_correcao`; nada gravado |
| sem base de convocar | 403 | recusa explicada; nada gravado, nada na sessão |
| Edital de outra unidade, ou inexistente; nomeada de outro recorte | 404 | nada gravado, nada na sessão |
| sem identificação | o pedido de identificação de hoje | — |

### `GET /gestao/editais/<edital>/marcos/<marco>/convocacao` (`interface:convocacao`)

Sem mudança de rota nem de parâmetro. Para quem pode emitir, cada cartão em aberto e com vencimento
ganha a ação; a tela consome `recusa_da_correcao` e o resultado `"correcao"`.

## O comando

### `convocar(..., correcao=None)`

`correcao` é `None` (o comando de hoje, sem mudança) ou:

```text
{ "convocacao_id": <id da convocação corrigida>, "assinatura": <assinatura da prévia> }
```

**Ordem, dentro da trava do Processo:**

1. repetição da chave → o resultado anterior;
2. ordem vigente, apuração ausente, apuração superada;
3. com `correcao`: a nomeada existe no recorte e é da inscrição (senão `nao_encontrado`); é a vigente
   em aberto (senão `convocacao_corrigida_com_desfecho` ou `convocacao_corrigida_sucedida`); tem
   vencimento (senão `correcao_sem_vencimento`); o motivo não é vazio (senão
   `motivo_da_correcao_obrigatorio`);
4. a espécie da sucessora;
5. com `correcao`: a assinatura confere (senão `previa_da_correcao_superada`);
6. as guardas de ordem, regularização e déficit, como hoje;
7. a gravação e a trilha.

**Payload da reserva:** o de hoje, acrescido de `corrige` e `previa` quando há `correcao`.

**Trilha:** a razão de hoje, acrescida de *"Sucede a convocação ‹id›, de vencimento ‹instante›."*
quando há anterior — com ou sem `correcao`, porque a sucessão pelo serviço também a merece.

### `convocar_e_comunicar(..., correcao=None)`

Repassa `correcao` a `convocar`. Com `correcao` e sem vencimento resolvido, recusa com
`vencimento_da_correcao_obrigatorio` antes do comando, ao lado da recusa de vencimento passado que
já está ali.

## O que não muda

- a API da `019` e os gestos em lote da `050`: `correcao` não existe neles;
- a fila e a fila dos regularizáveis;
- o portal.
