# Research — 073

Decisões de forma, com o que foi medido em 14/10/2026 no macOS da equipe, Python 3.13 e Django
5.2. Nenhum envio real e nenhuma inferência: os servidores de correio eram falsos e locais.

---

## R-001 — A seção mora em §10.4, e o §16 remete a ela

**Decisão.** A seção "Configurar, verificar e testar o correio e o Ollama" entra como §10.4, no fim
de "Configuração e segredos":

- o §16.3 (Teste) e o §16.5 (Trocar o servidor de correio) passam a remeter a ela;
- o §16.5 fica com o que só ele tem: o que pedir ao setor de correio e a guarda dos valores antigos;
- a linha do §25 que cita o `openssl` da §16.3 passa a citar a §10.4.

**Por quê.** O §10 é onde a TI já preenche o `app.env`, e a §10.4 continua o mesmo ato. Uma seção
de primeiro nível renumeraria do §11 ao §28, e o guia se cita por número em dezenas de lugares. O
Ollama não é correio, e por isso não cabe no §16.

**Descartado.** *Um documento novo em `doc/`*: seria a quinta fonte, contra o FR-1657. *Duplicar o
§16.5*: a FR-1650 manda incorporar.

## R-002 — A configuração carregada, por `shell -c` com lista fechada

**Decisão.** Um exemplo de `sudo ps-manage shell -v 0 -c '…'` que imprime chaves nomeadas, uma por
linha, e de cada segredo só `bool(...)`.

- A primeira linha é o `SETTINGS_MODULE`: é ela que distingue desenvolvimento de produção.
- O `-v 0` cala a linha "N objects imported automatically" do Django 5.2. Medido: com ele, a saída é
  só o que o exemplo imprime.

**Por quê.** O `diffsettings` imprime a `SECRET_KEY` e a senha do SMTP. A lista fechada não tem como
vazar o que não nomeia. Medido em 14/10: a senha plantada apareceu zero vezes.

**O que ela não prova.** O processo é o de diagnóstico, que acabou de ler o `app.env`. Os workers do
gunicorn leram o arquivo quando subiram (R-005).

## R-003 — Conexão, segurança e conta do correio, sem enviar

**Decisão.** `get_connection().open()` seguido de `close()`. O backend SMTP do Django abre o socket,
negocia o STARTTLS quando `EMAIL_USE_TLS` está ligado e autentica quando há `EMAIL_HOST_USER`. Ele
não envia nada. A falha sobe como exceção, e **a última linha da saída diz em que etapa parou**.

Medido contra servidores falsos locais, com `EMAIL_TIMEOUT=4`:

| Cenário | Última linha | Etapa |
|---|---|---|
| porta fechada | `ConnectionRefusedError: [Errno 61] Connection refused` | conexão |
| nome que não resolve | `socket.gaierror: [Errno 8] nodename nor servname provided, or not known` | conexão |
| nada responde (endereço sem rota, firewall que descarta) | `TimeoutError: timed out` | conexão |
| a conexão abre e o servidor não fala | `smtplib.SMTPServerDisconnected: Connection unexpectedly closed: timed out` | conexão aberta, sem saudação |
| o servidor não oferece STARTTLS | `smtplib.SMTPNotSupportedError: STARTTLS extension not supported by server.` | segurança |
| a conta é recusada | `smtplib.SMTPAuthenticationError: (535, b'5.7.8 …')` | conta |
| tudo aceito | a linha que o exemplo imprime | — |
| `EMAIL_HOST` vazio | `smtplib.SMTPServerDisconnected: please run connect() first` | — (a FR-1660 recusa antes) |

O número do `Errno` varia entre sistemas: é 61 no macOS e 111 no Linux. A tabela do guia cita o nome
da exceção, e não o número.

**Os dois "tempos esgotados" são sintomas diferentes, e a tabela os separa.** No `TimeoutError`, a
conexão nem abriu: rede, firewall, endereço ou porta errados, ou servidor fora do ar. No
`SMTPServerDisconnected … timed out`, ela abriu e o servidor não mandou a saudação SMTP. Uma causa
possível é ele esperar o aperto de mão TLS (SSL implícito, que o sistema não suporta). Outra é a
porta ser de outro serviço. Nenhum dos dois sintomas conclui sozinho. A tabela diz como distinguir:
o `openssl s_client` com e sem `-starttls`.

## R-004 — O Ollama em três níveis, pela configuração da aplicação

**Decisão.** Dois exemplos de `shell -c` que leem `ASSISTENTE_ENDERECO` e `ASSISTENTE_MODELO` das
settings e fazem `GET`, pela biblioteca padrão:

1. **conexão:** `/api/version`;
2. **disponibilidade do modelo:** `/api/tags`, e se o modelo configurado está na lista.

O terceiro nível, a **inferência efetiva**, é a `verificar_servico_de_inferencia`, que já existe e
confere também a quantização, o contexto e a ocupação da GPU.

**Por quê.** Pelo `ps-manage`, a consulta sai como o usuário da aplicação e com o endereço que a
aplicação vai usar. Um `curl` com o endereço digitado de novo testaria outra coisa. A versão,
sozinha, só prova que algo responde naquela porta: a seção o diz (FR-1653).

## R-005 — Confirmar que o serviço adotou o arquivo

**Decisão.** Depois do `systemctl restart`, comparar o instante em que o serviço subiu com a última
mudança do `app.env`:

- `systemctl show -p ActiveEnterTimestamp processoseletivo`;
- `stat -c %y /etc/processoseletivo/app.env`.

O primeiro tem de ser posterior. Para o correio, a prova do caminho inteiro é opcional e fica em
homologação: pedir o código de acesso no portal com uma caixa da equipe.

**Por quê.** A CLI não tem como perguntar a um worker qual configuração ele carregou. Que o serviço
subiu depois da edição é a evidência disponível. O pedido de código é a única prova de que os workers
entregam, e é envio real: por isso fica opcional e restrito a homologação.

## R-006 — A recusa só para o backend SMTP

**Decisão.** `_exigir(EMAIL_BACKEND != SMTP or EMAIL_HOST.strip(), "EMAIL_HOST", …)`, logo depois
da recusa do remetente.

**Por quê.** Só o backend SMTP do Django lê `EMAIL_HOST`. Um backend de terceiros, que o projeto não
tem, poderia não precisar dele. O usuário pediu a recusa "quando esse backend estiver selecionado".
O `AMBIENTE_MINIMO` da suíte ganha um `EMAIL_HOST` no mesmo commit (risco do plano).

## R-007 — A mensagem do serviço desconhecido

**Decisão.** No `else` da verificação:

- valor vazio: `nenhum serviço configurado (ASSISTENTE_SERVICO)`, como hoje;
- outro valor: `serviço desconhecido: 'Ollama' (ASSISTENTE_SERVICO); os aceitos são ollama e
  openrouter, e em produção só ollama`.

O `repr` mostra espaço e maiúscula, que são os erros típicos. A aplicação já diz "serviço
desconhecido" em `inferencia.conversar`; a verificação passa a dizer o mesmo.

## R-008 — O guia é testado a partir do próprio guia

**Decisão.** O teste novo extrai da §10.4:

- os blocos `app.env`, por cerca de código;
- os `shell -c`, pela expressão `shell -v 0 -c '(…)'`.

E executa os exemplos com `call_command("shell", command=…)`.

**Por quê.** Uma cópia do exemplo no teste ficaria verde enquanto o guia apodrece. O preço é o
exemplo não poder ter aspas simples dentro, que o próprio `ps-manage` também não admite.
