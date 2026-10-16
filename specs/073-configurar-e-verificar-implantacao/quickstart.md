# Quickstart — validar a 073

| Roteiro | Precisa de | Prova |
|---|---|---|
| A — A suíte | PostgreSQL local | as duas correções e a §10.4 contra o código (SC-621, SC-622, SC-624) |
| B — O correio em homologação | VM de homologação, conta do setor de correio, caixa da equipe | US1, SC-620, SC-623 |
| C — O Ollama | acesso de rede à L4 | US2, SC-623 |

---

## A — A suíte

```bash
cd backend && make lint check test-pg DB_NAME=test_073
```

**Esperado:** verde. Os servidores de correio e o Ollama do teste do guia são falsos, locais e de
vida curta: nenhum envio, nenhuma inferência.

## B — O correio, em homologação

Uma pessoa da TI que não participou do desenvolvimento segue **só** a §10.4 do guia, do passo 1 ao
8, com a conta que o setor de correio forneceu. Quem conduz anota três coisas: o tempo, cada vez em
que ela precisou de outro documento e cada linha da tabela que ela usou.

**Esperado:** a mensagem chega na caixa da equipe, e não no spam, em até 30 minutos, com zero
consultas a código ou a `specs/` (SC-620).

Para o SC-623, provoque um sintoma de cada vez e confira se a tabela leva à causa: a porta errada, o
nome errado e a senha errada.

## C — O Ollama

**Bloqueado até haver acesso à L4**, como o roteiro D da `071`. Antes, confira na máquina que vai
rodar o roteiro:

- o grupo de dependências `assistente` instalado (`uv pip show tokenizers` no ambiente da release);
- o `tokenizer.json` no caminho de `ASSISTENTE_TOKENIZER`, legível pelo usuário da aplicação.

Depois, siga os passos 5, 6 e 9 da §10.4, com o bloco do assistente preenchido.

**Esperado:**

- a versão no passo 5;
- o modelo "instalado" no passo 6;
- "Divergências: nenhuma" no passo 9.

Com o nome do modelo trocado de propósito, o passo 6 diz "NÃO instalado", sem inferência.
