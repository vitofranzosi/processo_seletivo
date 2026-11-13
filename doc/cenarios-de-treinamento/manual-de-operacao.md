# Cenários de treinamento — manual de operação

*Spec [`134`](../../specs/134-cenarios-de-treinamento/spec.md), 08/11/2026.* Para quem administra
o servidor de homologação. O roteiro de cada exercício, para a equipe de seleção, está no
[guia da equipe](guia-da-equipe.md).

## O que o gerador faz, e o que ele não faz

Ele **acrescenta** ao banco até dezessete Processos fictícios, `SIM-TREINAMENTO-001` a `017`, cada um
parado numa etapa do certame e pronto para a próxima ação. Cria tudo pelos mesmos comandos que a
tela usa: publica, inscreve, avalia, classifica, convoca. Por isso cada cenário tem a trilha de
auditoria e o histórico completos.

Ele **não**:

- apaga nada, nem na carga nem na restauração (não há `flush`, `TRUNCATE`, `DELETE` ou dump);
- altera Edital, inscrição, pessoa, unidade, autoridade ou permissão que não tenha criado;
- concede papel, com uma exceção só, a da formalização (abaixo);
- roda sozinho — nem no `git pull`, nem na migration, nem ao reiniciar o servidor;
- envia e-mail: durante a carga o correio fica na memória do processo;
- roda em produção: são três barreiras, descritas abaixo.

### A exceção: a pessoa do setor da formalização (C16 e C17)

Desde a revisão de 12/11/2026 (FR-4615 e FR-6720 a FR-6729 da spec), os cenários da formalização
trazem uma pessoa fictícia do setor, para que o fim do certame se treine pela tela:

- a pessoa `treino.formalizacao`, criada se não existir, **sem senha e sem identidade
  institucional** — ela não entra pelo login institucional, e a busca de pessoas de **Acessos da
  unidade** não a encontra;
- o papel **Formalização** dela na unidade, concedido pelo mesmo comando da tela de acessos, com
  motivo e trilha, e só se ela ainda não o tiver;
- no C16, a designação dela para o Edital `SIM16`.

Ela só existe nos Editais de treinamento: nos Editais reais da unidade, a tela de designar não a
oferece e o Centro não a conta, embora o vínculo seja da unidade (FR-6730). Quem concede e designa
na trilha é `treino.acessos`, que não é pessoa nem tem vínculo: ninguém entra
com esse poder. Nenhum outro papel é concedido, e nada é revogado na carga. A pré-visualização do
C16 e do C17 diz se a pessoa e o papel serão criados ou mantidos. Uma `treino.formalizacao`
desativada ou suspensa não é reativada: o cenário falha com `pessoa_indisponivel`.

### As outras frentes de trabalho (C08 e C12)

Desde a segunda revisão de 12/11/2026, para que se veja quem cobre cada frente de um Edital, dois
cenários trazem mais do que a presidência e a avaliação. Nenhum dos dois concede papel:

- **C08**: a candidata 03 já recorreu do resultado preliminar, pelo mesmo comando do portal, e o
  recurso foi **admitido** por `treino.julgamento` — que, como `treino.acessos`, só existe em
  memória, com a capacidade do Julgador de recursos e nenhuma outra. O mérito fica para a equipe.
- **C12**: `treino.avaliacao2`, membro que não preside, está **alocado à conferência** dos
  documentos da convocação, pelo comando de quem gere a comissão.

As duas receitas subiram para a **versão 2**. Uma rodada carregada antes aparece na verificação como
gerada com a versão 1: continua válida, mas sem essas frentes; restaure o C08 e o C12 para tê-las.

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

A carga dos quinze levou 8 segundos numa máquina de desenvolvimento. Cada cenário é uma
transação: um que falha não deixa nada no banco, e os outros seguem. `FALHOU` é uma recusa do
domínio, com a frase dela — a regra funcionando. `ERRO` é defeito do gerador, e a pilha sai na saída
de erros: registre-a como achado, sem tentar contornar. Rodar de novo cria só os que
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

A restauração também **revoga**, com motivo, as designações para a formalização vigentes nos
Editais da rodada anterior, inclusive no encerrado — senão o setor continuaria vendo o Edital antigo
na lista dele. A pré-visualização diz quantas. A pessoa `treino.formalizacao` e os papéis ficam
como estão.

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

## Montar o cenário como se fosse de dias atrás

O C10 e os que seguem o mesmo caminho (C11, C12, C15, C16, C17) nascem com o resultado **preliminar**
divulgado na hora da carga, e a janela recursal dele é de 5 dias corridos. Enquanto ela corre, o GPS
recusa divulgar o definitivo, declarar vaga não preenchida e encerrar o Edital — como recusaria num
certame real. Para exercitar esses atos no dia da carga, monte o cenário atrasado:

```bash
uv run python manage.py restaurar_cenario_de_treinamento --cenario C10 --banco processo_seletivo --confirmar C10 --dias-atras 6
```

O `carregar` aceita a mesma opção. O cenário é montado pelos mesmos comandos, com as mesmas
aferições: só o instante dos atos é outro, e as telas mostram essas datas. **Use 6 ou mais**: a
janela exclui o dia da divulgação e fecha às 23h59 do quinto dia, de modo que com 5 ela ainda está
aberta.

O que saber antes:

- **Só a rodada nova é atrasada.** O cancelamento da rodada anterior é datado de agora.
- **A validade conta do instante atrasado.** O C11 montado há 6 dias vale 24, e não 30: o prazo da
  convocação dele também começou há 6 dias.
- **O atraso que venceria o cenário é recusado**, sem gravar nada: o C08 vale 5 dias, e há 6 a
  janela em que o candidato recorre já nasceria fechada. Na carga do catálogo inteiro com
  `--dias-atras 6`, ele sai como `FALHOU` e os outros são criados; carregue-o depois, sem a opção.
- **A autoridade precisa ter sido vigente naquele dia.** Se ela foi cadastrada depois, a montagem é
  recusada e diz a data; use um atraso menor ou escolha outra com `--autoridade`.
- **O que você fizer hoje é de hoje.** Um ato novo que abra prazo — outro resultado divulgado, uma
  convocação com vencimento — conta do instante real, e o que depender dele espera.

## O correio da homologação

Os candidatos fictícios têm e-mail em `treinamento.exemplo.test`, que não entrega a ninguém. O
código de acesso ao portal chega ao **mailpit** do ambiente, na porta 8025 do servidor, e é de lá
que a equipe o lê para agir como candidato (C08, C11). O mailpit não guarda nada em disco:
reiniciá-lo esvazia a caixa, e basta pedir um código novo.

Sem o mailpit, o GPS imprime a mensagem no log do app, e só quem acessa o servidor a lê:

```bash
docker logs --tail 200 processo_seletivo-app-1 2>&1 | grep -B2 -A12 "treinamento.exemplo.test"
```

## Script auxiliar

Não há. Os quatro comandos já são a interface, e um script por cima esconderia justamente a linha
`Banco ... em ...` que a pré-visualização mostra para ser lida. O script de atualização do servidor
**não** foi alterado e não deve chamar a carga.

## Se algo der errado

Os cenários só acrescentam linhas, e todas ficam identificadas pelo manifesto. Voltar ao banco de
antes é restaurar o backup do passo 2 **num banco novo** e trocar o servidor para ele — nunca por
cima do banco em uso.
