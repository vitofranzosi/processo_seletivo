# Quickstart — 028 · Cronograma reaproveitado não nasce publicável

Como provar que a feature funciona, de ponta a ponta, **pelo canal do ator** — que é o que o
Princípio VI da Constituição exige.

São **três** percursos, e os três são obrigatórios: o que reproduz o achado, o que prova que o
Edital legítimo continua publicável, e o que prova que o acervo não foi preso. Fechar só o primeiro
entregaria a metade da feature que recusa, e nenhuma das duas que a mantêm usável.

Este arquivo é guia de validação. Modelo e contratos estão em [data-model.md](data-model.md) e
[contracts/cronograma-vencido.md](contracts/cronograma-vencido.md).

---

## Antes de começar

### O banco desta worktree é próprio

Suítes paralelas disputam `test_processo_seletivo` e se derrubam:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_028 POSTGRES_USER="$USER" preparar
```

**A variável vai para o `make`, e não antes dele.** O `Makefile` faz `include .env` seguido de
`export`, e `include` sobrepõe variável de ambiente: `DB_NAME=ps_demo_028 make preparar` prepara o
banco que está no `.env`, sem avisar. Fora do `make` — `manage.py` chamado direto, como nos blocos
abaixo — o prefixo é a forma certa.

`preparar` são **três** passos nesta ordem: provisionar, migrar, provisionar de novo. A segunda
passada concede privilégio sobre as tabelas que as migrations acabaram de criar; se ela disser
`0 de N protegidas`, ela não rodou.

No macOS com PostgreSQL do Homebrew, `LC_ALL` não é opcional.

### Antes de investigar qualquer erro estranho

```bash
cd backend && DB_NAME=ps_demo_028 uv run python manage.py migrate --check
```

Esta feature **não acrescenta migration nenhuma**. Se `migrate --check` acusar algo, é ambiente, e
não o diff.

### O servidor

**Acrescente** uma entrada ao `.claude/launch.json` — sem reescrever o arquivo, que é versionado e
carrega as entradas de outras sessões:

```json
{
  "name": "cronograma-028",
  "runtimeExecutable": "sh",
  "runtimeArgs": ["-c", "cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_demo_028 POSTGRES_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8028"],
  "port": 8028
}
```

Sem `INTERFACE_SELETOR_IDENTIDADE=true` a `/gestao/` devolve 503. O endereço é `localhost:8028` —
`127.0.0.1` devolve `DisallowedHost`.

### A demonstração

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_028 POSTGRES_USER=$USER uv run python manage.py seed_demo
```

Documento publicado não se regenera: mudou o renderizador, re-semeie.

### O relógio importa neste quickstart

Toda conferência desta feature é contra o **instante do ato**. Os percursos abaixo dizem "ontem" e
"daqui a dez dias" em relação ao dia em que forem executados — e não a datas fixas. Anotar a data da
execução ao lado do resultado é o que torna o percurso reproduzível por outra pessoa.

---

## Percurso A — o cenário do 12/2027, reproduzido

É o achado da auditoria, refeito pela interface. Papel: quem elabora.

| # | Ação | O que tem de acontecer | Requisito |
|---|---|---|---|
| A1 | Criar um Edital novo do ano **seguinte** e, no rascunho vazio, escolher "Partir de um Edital anterior" apontando um Edital cujo cronograma já passou | a cópia acontece, e **nenhuma data é diferente** da do Edital de origem | `FR-351`, `FR-364` |
| A2 | Abrir a composição, sem gravar nada | a etapa **Cronograma** exibe-se **pendente**, e não concluída | `FR-359`, `SC-113` |
| A3 | Na mesma tela | o aviso permanente da `023` — "datas, vagas e prazos são da oferta anterior" — continua lá, e o sinal novo se soma a ele | `UX-051` |
| A4 | Abrir a etapa Cronograma | ela diz, em texto visível, quais Eventos já passaram e por que está pendente | `UX-049`, `T-004` |
| A5 | Ler as mensagens | cada uma nomeia o Evento e mostra o instante em forma legível na zona institucional — nunca ISO cru, nunca UTC, nunca JSON Pointer | `UX-047` |
| A6 | Abrir a etapa 9 · Revisão | três achados desta feature: evento no passado, ano divergente, **e** o impeditivo de inscrições encerradas. A Revisão **não** diz que nada está pendente | `SC-114`, `UX-050` |
| A7 | Tentar submeter | recusado, dizendo **quando** as inscrições se encerraram e que o Edital publicado assim não receberá inscrição alguma | `FR-346`, `UX-048` |
| A8 | Seguir o destino da pendência impeditiva | ela leva à etapa **Cronograma**, que é onde a data se corrige — e não à etapa Inscrição | `FR-349`, `T-005` |
| A9 | Conferir o rascunho antes e depois de toda a conferência | idêntico: nenhuma data alterada, deslocada ou sugerida | `FR-351`, `SC-116` |
| A10 | Corrigir as datas do período para o futuro, deixando os demais Eventos no passado | o impedimento some; as advertências ficam; a submissão passa | `FR-343`, `FR-346` |
| A11 | Corrigir **todas** as datas para o futuro | a etapa Cronograma volta a exibir-se concluída, sem gravação além da correção | `FR-360` |
| A12 | Conferir os outros oito selos ao longo de A2–A11 | nenhum mudou de critério | `FR-361` |

---

## Percurso B — o Edital legítimo continua publicável

O caso que separa esta feature de um bloqueio que tornaria impublicável o Edital mais comum do fim do
ano.

| # | Ação | O que tem de acontecer | Requisito |
|---|---|---|---|
| B1 | Compor um Edital do ano **seguinte** cujos Eventos correm todos no ano seguinte, com o período de inscrições no futuro | advertência de ano divergente, e **nenhum** impedimento | `FR-344`, `D-006` |
| B2 | Publicar | publica | `FR-344` |
| B3 | Compor um Edital cujo período de inscrições **já começou** e ainda não terminou | advertência pelo início no passado, e **nenhum** impedimento | `FR-343`, `FR-347` |
| B4 | Compor um Edital cujo Evento marcado como período **não declara término** | nenhum impedimento: sem término declarado não há encerramento | `FR-347` |
| B5 | Compor um Edital que não marca Evento algum como período | a advertência que já existia, e **nenhum achado novo** | `FR-350` |
| B6 | Compor um Edital com Evento em 31/12 às 23:30 do horário de Vitória, no mesmo ano do Edital | **nenhuma** advertência de ano: o ano lido é o da zona institucional, e não o de UTC | `FR-342`, `SC-118`, `T-006` |
| B7 | Compor um Edital **do zero**, sem reaproveitamento, com um Evento no passado | os mesmos achados aparecem: a regra é de todo Edital | `FR-363` |
| B8 | Compor um Edital com janela de inscrição de **uma hora**, no futuro | nada é dito sobre duração | `FR-352`, `D-005` |
| B9 | Submeter um Edital com o período aberto e publicar **depois** que ele fechar | a publicação é recusada, ainda que a submissão tenha passado | `FR-357`, `FR-358` |

> **B9 é o percurso que exige espera real.** A forma barata de executá-lo é declarar o término a
> poucos minutos à frente, submeter e homologar dentro da janela, e confirmar a publicação depois
> dela. Não há relógio a congelar na interface, e é assim que o caso acontece na vida.

---

## Percurso C — o acervo não foi preso

O insumo é a demonstração semeada: Editais publicados cujo cronograma já venceu.

| # | Ação | O que tem de acontecer | Requisito |
|---|---|---|---|
| C1 | Abrir a Retificação de um Edital publicado cujo cronograma inteiro já passou | **zero** achados desta feature na conferência do ato | `FR-354`, `SC-115` |
| C2 | Retificar **só uma frase** desse Edital e publicar a Retificação | passa. Cronograma vencido não prende Retificação nenhuma | `FR-354` |
| C3 | Retificar antecipando o encerramento das inscrições para um instante já passado | **não** é recusada: encerrar prazo é ato de quem assina | `FR-355` |
| C4 | Conferir os achados que já existiam sobre o período — marca ausente, marca ambígua | inalterados | `FR-350` |
| C5 | Conferir o resumo canônico de todo conteúdo publicado antes da feature | idêntico | `FR-365` |

---

## Percurso D — a demonstração contém o caso

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_028 POSTGRES_USER=$USER uv run python manage.py seed_demo
```

| # | O que conferir | Requisito |
|---|---|---|
| D1 | Existe um **quarto** Edital, criado por reaproveitamento, em elaboração | `FR-366`, `FR-367` |
| D2 | A etapa Cronograma dele exibe-se pendente | `FR-359`, `SC-119` |
| D3 | A Revisão dele exibe os três achados | `SC-114` |
| D4 | A publicação dele é recusada, e ele permanece em elaboração | `FR-346`, `FR-367` |
| D5 | Os três Editais anteriores continuam publicados e percorríveis — inscrição aberta, resultado divulgado, sorteio | `FR-367` |
| D6 | O segundo Edital continua com as inscrições encerradas, e o ato que as encerrou é uma **Retificação** publicada | `FR-355`, `T-008` |

---

## Verificação

```bash
cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_028 POSTGRES_USER="$USER" lint check test-pg
```

`test-pg`, e não `test`: sem o par de variáveis a suíte cai para SQLite, onde dezenas de casos falham
por motivo que nada tem com o diff. `lint` são **dois** passos — `ruff check` e `ruff format --check`
—, e rodar só o primeiro declara verde local e quebra no CI.

**O que esta feature muda na conta esperada da suíte**, medido em [research.md](research.md):

- **A advertência nova não quebra asserção nenhuma** (`T-007`). Toda leitura de achados na suíte
  filtra por `blocking_findings` ou por prefixo de código. Se alguma quebrar, é asserção que não
  filtrava — e ler qual é o ponto.
- **O impedimento derruba seis lugares** (`T-008`), e é esperado: são os fixtures que publicam Edital
  com a inscrição já encerrada. Eles passam a publicar abertos e a fechar por Retificação. Cada queda
  é lida e decidida; nenhuma é silenciada.

E antes de empurrar, mesmo que só documentação tenha mudado:

```bash
cd backend && uv run pytest tests/test_citacoes_de_requisito.py
```

---

## Registro da execução

**15/09/2026**, banco `ps_demo_028`, servidor em `localhost:8028`, identidade `ana.elaboradora`
com o papel Elaborador. O alvo foi o **quarto Edital da demonstração** — `01/2027`, reaproveitado
do `51/2026` —, que é o cenário do `12/2027` reconstruído pelo `seed_demo`.

| # | O que foi observado | Resultado |
|---|---|---|
| A2 | Etapa 3 · Cronograma, lida a partir da etapa 1 | **PENDENTE** ✔ |
| A3 | Aviso da `023` no topo de todas as etapas | presente, e o sinal novo se soma a ele ✔ |
| A4 | Etapa Cronograma diz quais Eventos venceram | três avisos, um por Evento ✔ |
| A5 | Forma dos instantes | `06/08/2026 às 20:32` — zona institucional, sem ISO, sem UTC, sem JSON Pointer ✔ |
| A6 | Etapa 9 · Revisão | "O que falta para submeter", **não** "Nada pendente"; três avisos de passado, três de ano e o IMPEDE ✔ |
| A8 | Destino de cada pendência | "Ir para Cronograma" em todas ✔ |
| A12 | Os outros oito selos | inalterados ✔ |
| D1–D4 | O quarto Edital existe, em elaboração, pendente, com os três achados | ✔ |

### O que **não** foi percorrido à mão, e por quê

- **A1, A7, A9–A11 e o Percurso B inteiro** são verificados por teste automatizado contra as mesmas
  views e os mesmos serviços — a lista está em [rastreabilidade.md](rastreabilidade.md). Repeti-los
  na tela mediria a mesma coisa duas vezes.
- **B9** — publicar depois de o prazo fechar — deixou de exigir espera real: o teste
  `test_o_prazo_que_vence_entre_a_homologacao_e_a_publicacao_impede_publicar` injeta o instante do
  ato em vez de dormir sete segundos. O roteiro acima permanece como está para quem quiser vê-lo
  acontecer na tela.
- **O Percurso C** (o acervo) é integralmente automatizado em
  `tests/integration/publicacoes/test_cronograma_vencido_no_ato.py`.

> **O que a execução à mão encontrou e o teste não encontraria.** Um cronograma de três Eventos
> reaproveitado produz **sete** achados — três de passado, três de ano e o impeditivo. É a `FR-345`
> funcionando como escrita, uma advertência por Evento e por espécie; num Edital real de quinze
> Eventos seriam trinta linhas. Agrupar por espécie seria mudança de decisão, e não correção.
