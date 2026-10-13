# Contrato — O despacho (066)

*`manage.py despachar_avisos`, num timer do systemd a cada minuto. É o único lugar do aviso que
chama o servidor de correio, e o módulo remetente declarado na `FR-084` da `010`
(`avisos/application/despacho.py`).*

## Invocação

```
manage.py despachar_avisos [--limite N]
```

- `--limite`: teto de destinatários tentados nesta execução. O padrão é `AVISOS_LIMITE_POR_MINUTO`
  (60).
- **Saída 0** quando terminou, quando não havia o que fazer, quando outra execução tinha a trava e
  quando `AVISOS_AOS_CANDIDATOS` está desligada.
- **Saída diferente de 0** só quando a conexão ao servidor de correio não abriu. É isso que aciona o
  `OnFailure=ps-alerta@%n.service` que o runbook já usa.

## Sequência de uma execução

0. **Chave.** Com `AVISOS_AOS_CANDIDATOS` desligada, sai com 0 sem tocar em nada (`R-013`).
1. **Trava global.** `pg_try_advisory_lock(TRAVA_DO_DESPACHO)`. Sem a trava, sai com 0 e uma linha
   no registro (`R-002`).
2. **Varredura de órfãs.** Toda `TentativaDeEnvio` sem `ResultadoDaTentativa` recebe `INDETERMINADA`,
   com o detalhe "a execução anterior terminou sem registrar o resultado". Com a trava global, ela
   não pertence a ninguém vivo (`R-004`).
3. **Seleção.** Até N destinatários elegíveis ao despacho (data-model §2), **dentro da janela de
   despacho** (`R-016`), na ordem de `solicitado_em` do aviso e, dentro dele, do protocolo.
4. **Conexão.** `get_connection()` e `open()`. Se falhar, sai com código diferente de 0, sem
   registrar tentativa nenhuma. Nada saiu, e a próxima execução tenta de novo.
5. **Para cada destinatário:**
   1. Transação curta: `pg_advisory_xact_lock(aviso)`. Se o aviso tem `InterrupcaoDoAviso`, pula para
      o próximo aviso. Senão, insere `TentativaDeEnvio(numero = última + 1)` e confirma.
   2. Fora de transação: compõe a mensagem (contrato `mensagem.md`), com um destinatário só e sem `cc`
      nem `bcc`. **Prepara e valida antes da rede**: saneia o endereço e monta a mensagem. Erro aqui
      é a fase 1 de `R-004`. Só então chama `connection.send_messages([mensagem])`.
   3. Transação curta: insere `ResultadoDaTentativa` **pela fase** em que a resposta veio (`R-004`).
      Código só classifica quando é resposta lida a um comando. Queda, timeout, resposta ilegível ou
      código fora de 400–599 são indeterminados.
   4. Se o resultado foi `INDETERMINADA`, **para a execução**: a conexão está em estado
      desconhecido.
6. **Fim.** Fecha a conexão, libera a trava e registra uma linha de resumo: avisos, aceitas, falhas e
   indeterminadas. O resumo leva os números e o id dos avisos, e nunca endereço ou nome.

## Garantias, e de onde vêm

| Garantia | Mecanismo |
|---|---|
| Nunca duas execuções ao mesmo tempo | trava global (passo 1) e serviço `oneshot` do systemd |
| Nunca a mesma tentativa duas vezes | `UNIQUE (destinatario, numero)` |
| Nenhuma tentativa começa depois da interrupção | o passo 5.1 e a interrupção tomam a mesma trava por aviso |
| Reativação ou timer que volta não disparam mensagem antiga | janela de despacho (`R-016`): fora dela, o destinatário expira sem envio |
| Indeterminada nunca reenviada sozinha | a seleção (passo 3) não a inclui; só o aviso filho (`R-011`) a alcança |
| Falha temporária retentada com intervalo | seleção por `ResultadoDaTentativa.registrado_em` + intervalo (`AVISOS_INTERVALOS_DE_RETENTATIVA`, padrão `5,15` minutos) |
| Limite por minuto | N por execução, uma execução por minuto |
| Timeout | `EMAIL_TIMEOUT` (`R-006`) na conexão aberta no passo 4 |
| Nenhum envio real na suíte | `get_connection()` usa `EMAIL_BACKEND`, que a suíte substitui. Um guardião (`FR-1281`) varre o módulo e falha se ele importar `smtplib` para abrir conexão, ou passar `backend=` a `get_connection` |

## Configuração

| Variável | Padrão | Uso |
|---|---|---|
| `AVISOS_AOS_CANDIDATOS` | `false` (produção), `true` (desenvolvimento e suíte) | chave da `R-013` |
| `AVISOS_LIMITE_POR_MINUTO` | 60 | `FR-1270`; valor inicial, a validar com o setor de correio |
| `AVISOS_MAX_TENTATIVAS` | 3 | `FR-1269` |
| `AVISOS_INTERVALOS_DE_RETENTATIVA` | `5,15` | minutos antes da 2ª e da 3ª tentativa |
| `AVISOS_ALERTA_DE_PENDENTE_MIN` | 10 | `FR-1272` |
| `AVISOS_JANELA_DE_DESPACHO_HORAS` | 24 | `FR-1283`, `R-016` |
| `EMAIL_TIMEOUT` | 20 | segundos; vale para os quatro envios |

## Unidade systemd (runbook, §21)

```ini
# /etc/systemd/system/ps-avisos.service
[Unit]
Description=Processo Seletivo — despacho dos avisos aos candidatos
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-manage despachar_avisos

# /etc/systemd/system/ps-avisos.timer
[Timer]
OnCalendar=*-*-* *:*:00
AccuracySec=5s
[Install]
WantedBy=timers.target
```
