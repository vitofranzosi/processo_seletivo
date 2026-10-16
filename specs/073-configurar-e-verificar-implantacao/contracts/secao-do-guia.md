# Contrato — a §10.4 do guia de implantação e as duas mensagens

O que a seção promete a quem a segue. `tests/test_guia_configurar_verificar.py` prende as partes
marcadas com **(testado)**.

## Os passos, nesta ordem (FR-1650)

| # | Passo | Comando | Contata serviço externo? | Efeito |
|---|---|---|---|---|
| 1 | Preencher | `sudo -e /etc/processoseletivo/app.env` | não | — |
| 2 | Pré-voo | `sudo ps-manage check --deploy` | não | — |
| 3 | Ler a configuração | `sudo ps-manage shell -v 0 -c '…'` | não | — |
| 4 | Correio: conexão, segurança, conta | `sudo ps-manage shell -v 0 -c '…get_connection()…'` | sim | **nada enviado** |
| 5 | Ollama: conexão | `sudo ps-manage shell -v 0 -c '…/api/version…'` | sim | nada inferido |
| 6 | Ollama: modelo disponível | `sudo ps-manage shell -v 0 -c '…/api/tags…'` | sim | nada inferido |
| 7 | Reiniciar e confirmar | `systemctl restart` e os dois instantes (R-005) | não | o serviço adota o arquivo |
| 8 | Envio de teste | `sudo ps-manage sendtestemail <CAIXA_DA_EQUIPE>` | sim | **uma mensagem** |
| 9 | Inferência efetiva | `sudo ps-manage verificar_servico_de_inferencia` | sim | **uma inferência** |

## Os blocos de exemplo (FR-1651)

- **Dois blocos `app.env`:** o do correio e o do assistente. **(testado)** Toda variável deles é lida
  por `config/settings/base.py` ou `production.py`.
- **Valores a substituir** entre `<…>`. **(testado)** A senha aparece só como `<SMTP_SENHA>`.
- **O bloco do assistente** diz:
  - só `ollama` em produção;
  - tempo-limite de no máximo 110 s;
  - o endereço na raiz, sem `/api`;
  - nenhuma variável numérica vazia.

## Os exemplos de `shell -c` (FR-1652, FR-1653)

- Sem aspas simples dentro, para caber no `ps-manage`.
- **Leitura (passo 3).** **(testado)** Executada com senha do SMTP, credencial do assistente e
  chave da aplicação plantadas, nenhum dos três valores aparece na saída. A primeira linha é o
  módulo de settings.
- **Correio (passo 4).** **(testado)** Contra servidores falsos locais, a última linha é a da tabela
  para cada cenário, e o servidor que aceita não recebe `MAIL FROM`.
- **Ollama (passos 5 e 6).** **(testado)** Contra um Ollama falso local, o passo 5 imprime a versão,
  e o 6 diz se o modelo configurado está ou não na lista. Nenhum dos dois chama `/api/chat`.

## A tabela (FR-1654, FR-1655)

Colunas: **o que aparece** → **causas possíveis** → **como distinguir e agir**. As linhas mínimas:

| O que aparece | Causas possíveis |
|---|---|
| `ConnectionRefusedError` | porta errada; serviço fora do ar; firewall que rejeita |
| `socket.gaierror` | nome do servidor errado; DNS da VM |
| `TimeoutError: timed out` | rede ou firewall que descarta; endereço ou porta errados; servidor fora do ar |
| `SMTPServerDisconnected: Connection unexpectedly closed: timed out` | o servidor espera TLS desde o início (SSL implícito); a porta é de outro serviço |
| `SMTPNotSupportedError: STARTTLS extension not supported` | porta sem STARTTLS; servidor que só aceita SSL implícito em outra porta |
| `SMTPAuthenticationError` | usuário ou senha errados; conta sem permissão de envio pelo servidor |
| Ollama: `URLError` / recusa | endereço ou porta; serviço parado; firewall |
| Ollama: `HTTP Error 404` | endereço com `/api` no fim |
| Ollama: modelo "NÃO instalado" | nome diferente do que `ollama list` mostra; modelo não baixado |
| Verificação: quantização ou contexto divergentes | o servidor serve outra versão do modelo; o valor configurado está errado |

**Nenhuma linha conclui por uma causa só. (testado)** A palavra "465" não aparece como causa.

## As duas mensagens

- **FR-1660 (testado):** com `DJANGO_EMAIL_BACKEND` igual ao backend SMTP e `EMAIL_HOST` vazio ou
  só com espaços, `ImproperlyConfigured("EMAIL_HOST: …")`. A mensagem diz o que preencher. Com
  outro backend, a regra não se aplica.
- **FR-1661 (testado):** a verificação do serviço de inferência, com `ASSISTENTE_SERVICO` fora do
  vocabulário, imprime `serviço desconhecido: '<valor>' (ASSISTENTE_SERVICO)` e os aceitos, e sai
  com 1. Vazio, imprime `nenhum serviço configurado (ASSISTENTE_SERVICO)`.
