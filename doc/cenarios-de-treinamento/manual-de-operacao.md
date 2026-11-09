# Cenários de treinamento — manual de operação

*Spec [`134`](../../specs/134-cenarios-de-treinamento/spec.md), 08/11/2026.* Para quem administra
o servidor de homologação. O roteiro de cada exercício, para a equipe de seleção, está no
[guia da equipe](guia-da-equipe.md).

## O que o gerador faz, e o que ele não faz

Ele **acrescenta** ao banco até quinze Processos fictícios, `SIM-TREINAMENTO-001` a `015`, cada um
parado numa etapa do certame e pronto para a próxima ação. Cria tudo pelos mesmos comandos que a
tela usa: publica, inscreve, avalia, classifica, convoca. Por isso cada cenário tem a trilha de
auditoria e o histórico completos.

Ele **não**:

- apaga nada, nem na carga nem na restauração (não há `flush`, `TRUNCATE`, `DELETE` ou dump);
- altera Edital, inscrição, pessoa, unidade, autoridade ou permissão que não tenha criado;
- roda sozinho — nem no `git pull`, nem na migration, nem ao reiniciar o servidor;
- envia e-mail: durante a carga o correio fica na memória do processo;
- roda em produção: são três barreiras, descritas abaixo.

## As três barreiras

| Barreira | O que exige | Sem ela |
|---|---|---|
| Ambiente | `AMBIENTE_DE_PRODUCAO` falso e `DJANGO_SETTINGS_MODULE` sem `production` | todo comando recusa |
| Chave | `CENARIOS_DE_TREINAMENTO=true` no ambiente do comando | todo comando recusa; `production.py` não sobe com ela |
| Banco | `--banco <nome>` igual ao banco conectado, em toda escrita | carga e restauração recusam |

A chave só precisa estar no ambiente **do comando**, e não no do servidor web. Ligue-a na linha de
comando, e não no `.env` permanente.

**Para os cenários de sorteio (C06 e C07)**, o servidor web e o comando precisam também de
`SORTEIO_FONTE_DE_DEMONSTRACAO=true`. As configurações de desenvolvimento, que a VM de testes usa,
já a ligam. Sem ela, a pré-visualização mostra C06 e C07 como `RECUSAR`, e os outros treze seguem.

## Antes da primeira carga no banco compartilhado

1. **Atualize o GPS como sempre**, pelo script de atualização do servidor. A release traz a
   migration `treinamento/0001`, que só cria a tabela vazia do manifesto. O `provisionar_papeis`
   continua informando **53 de 53**: a tabela nova não é append-only.

2. **Faça o backup** do banco de homologação, com o usuário que tem acesso a ele:

   ```bash
   pg_dump -Fc -d processo_seletivo -f /var/backups/gps-homologacao-antes-dos-cenarios.dump
   ```

   Confira que o arquivo tem tamanho e que ele se lê:

   ```bash
   pg_restore --list /var/backups/gps-homologacao-antes-dos-cenarios.dump | head
   ```

3. **Ensaie num banco descartável**, restaurado desse backup. É obrigatório antes da primeira carga
   no banco compartilhado:

   ```bash
   createdb gps_ensaio_cenarios
   pg_restore -d gps_ensaio_cenarios /var/backups/gps-homologacao-antes-dos-cenarios.dump
   ```

   Rode os passos de [carga](#a-carga) com `DB_NAME=gps_ensaio_cenarios` e
   `--banco gps_ensaio_cenarios`. Abra o servidor contra esse banco, confira dois ou três cenários
   pelo navegador e apague o banco de ensaio:

   ```bash
   dropdb gps_ensaio_cenarios
   ```

4. **A autoridade que assina.** Os atos fictícios precisam de uma autoridade vigente da unidade. O
   gerador escolhe sozinho só uma autoridade **já usada** por alguma publicação: o primeiro uso de
   uma autoridade torna o cadastro dela imutável, e o gerador não faz isso por conta própria. Se
   nenhuma foi usada, ele recusa e lista as vigentes; escolha uma, sabendo do efeito, com
   `--autoridade <identificador>`.

## Como chamar o comando

Com o mesmo `manage.py` e as mesmas variáveis do banco que o script de atualização usa. Na
instalação nativa de desenvolvimento:

```bash
cd backend
set -a; . ./.env; set +a
export CENARIOS_DE_TREINAMENTO=true
uv run python manage.py listar_cenarios_de_treinamento
```

Numa instalação com o `ps-manage` do guia de implantação, a chave vai antes do comando. **Não use
o `ps-manage` se o `app.env` dele carrega `config.settings.production`**: o gerador recusa, e é
o esperado.

## A carga

Primeiro a pré-visualização, que não grava nada:

```bash
uv run python manage.py carregar_cenarios_de_treinamento --dry-run
```

Ela mostra o banco, o servidor, a configuração e a chave, e uma linha por cenário: `CRIAR`,
`MANTER` (já existe) ou `RECUSAR` (com o motivo). Conferido o banco, a carga de verdade:

```bash
uv run python manage.py carregar_cenarios_de_treinamento --banco processo_seletivo
```

Para só alguns cenários, repita `--cenario`:

```bash
uv run python manage.py carregar_cenarios_de_treinamento --banco processo_seletivo --cenario C04 --cenario C07 --cenario C11
```

A carga dos quinze levou 8 segundos numa máquina de desenvolvimento. Cada cenário é uma transação: um que falha (`FALHOU`,
com a frase do domínio) não deixa nada no banco, e os outros seguem. Rodar de novo cria só os que
faltam: os prontos aparecem como `MANTER`, e nada neles é tocado, nem o que a equipe já fez.

## Listar e verificar

```bash
uv run python manage.py listar_cenarios_de_treinamento
uv run python manage.py verificar_cenarios_de_treinamento
```

| Situação | Quer dizer | O que fazer |
|---|---|---|
| `AUSENTE` | ainda não foi criado | carregar |
| `INTACTO` | no estado inicial | nada |
| `EXERCITADO` | a equipe já agiu nele; a verificação lista o que mudou | restaurar, se outra pessoa for refazer o exercício |
| `CONFLITO` | existe um Processo com o código reservado que o gerador não criou | examinar o Processo; o gerador não o toca |
| `INCONSISTENTE` | o Processo do manifesto não se comprova do gerador | examinar; a restauração fica bloqueada |

A verificação também avisa quando **o prazo do estado inicial venceu** — por exemplo, as inscrições
abertas do C02 encerram 30 dias depois da carga. Restaure para ter datas novas.

## A restauração

Restaurar devolve **um** cenário ao estado inicial. Como nada se exclui, ela **cria a rodada
seguinte** — `SIM-TREINAMENTO-007-R2`, Edital `SIM07R2` — e **cancela** a rodada anterior pelos
comandos de cancelamento do GPS, com o motivo escrito. A rodada anterior sai da aba "Em andamento" e
fica em "Cancelados", com todo o histórico do exercício.

Primeiro veja o que vai acontecer:

```bash
uv run python manage.py restaurar_cenario_de_treinamento --cenario C07 --dry-run
```

Depois, confirmando com o código:

```bash
uv run python manage.py restaurar_cenario_de_treinamento --cenario C07 --banco processo_seletivo --confirmar C07
```

A restauração é recusada quando a propriedade do Processo não se comprova pelo manifesto e pela
trilha, quando o cenário não tem rodada em uso, ou quando a rodada nova encontraria conflito. Nesses
casos nada é alterado.

## Mantendo os cenários válidos com o tempo

As datas de cada cenário contam do dia da carga. Os que têm prazo correndo valem por um tempo:

| Cenário | Vale por | Por quê |
|---|---|---|
| C01 | 7 dias | as inscrições começam 7 dias depois da carga |
| C02, C13 | 30 dias | período de inscrições aberto |
| C08 | 5 dias | janela recursal do resultado preliminar |
| C11, C12 | 30 dias | prazo da convocação |

Os demais não dependem do calendário. Antes de uma sessão de treinamento, rode a verificação e
restaure o que ela apontar.

## Script auxiliar

Não há. Os quatro comandos já são a interface, e um script por cima esconderia justamente a linha
`Banco ... em ...` que a pré-visualização mostra para ser lida. O script de atualização do servidor
**não** foi alterado e não deve chamar a carga.

## Se algo der errado

Os cenários só acrescentam linhas, e todas ficam identificadas pelo manifesto. Voltar ao banco de
antes é restaurar o backup do passo 2 **num banco novo** e trocar o servidor para ele — nunca por
cima do banco em uso.
