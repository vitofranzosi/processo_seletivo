# Contrato da gestão: conferir a identidade

## Detalhe da inscrição — `GET interface:inscricao-recebida` (rota existente)

- Para a inscrição **enviada**, a tela ganha um bloco "Conferir identidade" sob os dados da pessoa:
  uma frase ("Para conferir CPF e data de nascimento na Receita, em caso de dúvida. Fica registrado
  quem conferiu e por quê."), o campo **Motivo** (texto, obrigatório, até 300 caracteres, com a dica
  "não escreva CPF nem data aqui") e o botão **Conferir identidade**.
- Rascunho não mostra o bloco: rascunho não é ato, e a gestão não o consulta por este caminho.
- O CPF continua mascarado nesta tela.

## Conferência — `POST interface:conferir-identidade` → `gestao/inscricoes/<uuid>/conferir-identidade`

**Entrada**: `motivo`, `csrfmiddlewaretoken`.

**Autorização**: a mesma do detalhe — `inscricao:consultar` e o Edital da inscrição no escopo do ator
(FR-8317). Sem sessão, pede identificação como as demais.

**Respostas**:

| Situação | Resposta |
|---|---|
| ator sem a permissão `inscricao:consultar` | 403, a recusa explicada do detalhe |
| inscrição fora do escopo ou inexistente | 404, como o detalhe (linha nova no inventário de negativas da `033`) |
| inscrição em rascunho | 404 (não há o que conferir) |
| `GET` | 405 |
| motivo vazio ou só espaços | 422, a página do detalhe com a recusa "Escreva o motivo da conferência." e nada revelado (FR-8315) |
| válido | 200, página privada (`no-store`) com nome, CPF completo formatado, data `dd/mm/aaaa` ou "Não informada nesta inscrição" (enviada antes da `180`), o motivo e o instante; um link de volta ao detalhe |

**Efeito**: um evento na trilha, `CONFERIR_IDENTIDADE`, com ator, inscrição, instante e
`reason="Conferência de identidade da inscrição <protocolo>: <motivo>"`. Sem CPF, sem data (FR-8316).
Um POST repetido grava outro evento: cada revelação é uma conferência.

**Onde se lê depois**: na trilha de auditoria do Edital (`interface:auditoria`), como "Conferência de
identidade de inscrição", com o motivo (SC-2906). Só a conferência entra ali: os demais registros
auditados sob a inscrição continuam fora daquela tela (R8 da pesquisa).

> **Corrigido na implementação da história 3.** A primeira redação desta tabela dizia 404 para o ator
> sem permissão, "como o detalhe". O detalhe responde **403** a quem não tem `inscricao:consultar`
> (`tests/authorization/test_consulta_administrativa.py`), e 404 só ao que não existe e à outra
> unidade — a gramática da `033`. A conferência segue o detalhe, que é o que a FR-8317 pede. O
> protocolo entrou na frase da trilha pela R8.

**Não há GET** para a página da conferência: atualizar a página reenvia o POST, e o navegador
avisa; voltar ao detalhe é pelo link.
