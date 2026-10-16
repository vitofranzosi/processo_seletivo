# Contrato — a tela do piloto

A tela da gestão em que o participante conversa com o assistente (`R-010`, `R-011`). O modelo é a
tela da `070` (`interface/duvidas.py`): formulário nativo, sem script obrigatório, na folha da gestão.

---

## 1. Rotas

| Método | Caminho | Nome | Faz |
|---|---|---|---|
| `GET` | `gestao/editais/<uuid:edital_id>/assistente/` | `interface:assistente` | Mostra a conversa corrente do Edital, lida de `TrocaDoPiloto` |
| `POST` | o mesmo | — | Grava uma pergunta (`perguntar`) e redireciona para o `GET` |
| `POST` | `…/assistente/nova/` | `interface:assistente-nova` | Troca a conversa da sessão e redireciona |

As duas condições do `FR-1460` — o alcance de `obter_edital` e a permissão `assistente:piloto` — são
verificadas nas três, antes de qualquer outra coisa. Sem uma delas, a negativa `not_found` da `070`.
Com o piloto desligado, a mesma negativa (`FR-1464`).

Edital sem publicação vigente no instante: a página diz "Só Edital publicado tem piloto", sem
formulário (`FR-1413` da `070`).

---

## 2. A página

De cima para baixo:

1. **A faixa do piloto** (`UX-210`): "Piloto interno do assistente do Edital. As respostas podem
   conter erros: confira cada uma nas fontes. Nada desta tela é visto por candidatos."
2. **Com o serviço externo** (`UX-211`): "As perguntas desta configuração saem da rede institucional.
   Faça só perguntas sobre Editais públicos, sem dado de pessoa."
3. **A orientação da sessão** (13º): "Pergunte como um candidato perguntaria, sobre este Edital. Não
   escreva nome, CPF, e-mail, telefone ou situação de ninguém. CPF, e-mail e telefone são mascarados
   no registro, mas o mascaramento não torna a conversa anônima."
4. **O Edital**: número, ano, título.
5. **A conversa**, um bloco por turno, na ordem:
   - a versão, no topo; a marca "versão anterior" quando difere da vigente (`UX-212`, `UX-216`);
   - o aviso de mudança de versão, antes de tudo, no primeiro turno depois da mudança;
   - a pergunta, mascarada;
   - o tipo, em palavras;
   - os trechos, cada um com o rótulo da natureza — "Explicação do assistente", "Dado, segundo a
     fonte", "Citação literal" (`UX-213`) — e as fontes que cita; o texto escapado, nunca marcação
     (`FR-1492`);
   - os avisos de Retificação futura e de desfecho, da aplicação (`FR-1490`);
   - as referências, em `<details>`: cada fonte citada com a natureza da `070` — "Texto do Edital",
     "Dado da versão vigente" — ou "Calculado pelo sistema no instante", o lugar, o ato de origem e os
     links (`FR-1489`);
   - o canal de atendimento (`FR-1493`);
   - quando o histórico foi reduzido: "Esta resposta considerou as perguntas a partir da nº N".
   - ou, em vez de tudo isso, o estado (§3).
6. **O formulário**: um `<textarea>` com `<label>`, o limite em caracteres dito, e o botão "Perguntar".
7. **"Começar outra conversa"**, num formulário próprio.
8. **Para conferir sem o assistente**: o link da tela da `070` para este Edital.

A resposta nova recebe o foco e fica numa região `aria-live="polite"` (`UX-215`). Script opcional só
desabilita o botão e mostra "Consultando o Edital…" durante o envio.

---

## 3. Os estados

| Estado | Texto | Oferece |
|---|---|---|
| `NAO_PASSOU_NA_CONFERENCIA` | "A resposta não foi mostrada porque não se sustentou nas fontes do Edital." | As perguntas sugeridas da `070`, o documento do Edital, o canal |
| `INCOMPLETA`, `POSSIVEL_CORTE`, `RESPOSTA_MALFORMADA`, `MODELO_DIFERENTE` | "O assistente não produziu uma resposta completa e conferível." | Os mesmos |
| `INDISPONIVEL`, `TEMPO_ESGOTADO` | "O assistente não respondeu agora." | Os mesmos |
| `LIMITE_DE_USO` | "O limite de perguntas foi atingido. Tente de novo em alguns minutos, ou comece outra conversa." | Os mesmos |
| `LIMITE_DO_SERVICO` | "O serviço do modelo recusou a pergunta por excesso de pedidos. Tente de novo em alguns minutos." — separado do `LIMITE_DE_USO` em 14/10: com o mesmo texto, a recusa do serviço parecia do piloto | Os mesmos |
| `ORCAMENTO_ESGOTADO` | "O limite de gasto do serviço desta configuração acabou." | Os mesmos |
| `EXCEDE_O_CONTEXTO` | "Este Edital não cabe na configuração atual do piloto." | Os mesmos |
| `PERGUNTA_RECUSADA` | O motivo: tamanho, ou dado pessoal com serviço externo | O formulário com a pergunta, para corrigir |
| `SEM_TOKENIZER` | "O piloto não está pronto: falta o tokenizer do modelo." | — |

O estado aparece no lugar da resposta, no bloco do turno, e o turno fica no histórico **sem** entrar
no contexto das próximas perguntas (`FR-1495`).

---

## 4. A entrada

Na página do Edital da gestão, ao lado do link da `070`, "Conversar com o assistente (piloto)", só
quando: o piloto está ligado, o Edital tem publicação, e o ator tem a permissão.
