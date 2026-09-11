# Um teste comparava data em UTC com data na tela, e só falhava de madrugada

**Data:** 2026-09-11
**Origem:** CI do PR #102 (`025` — Quadro de Vagas por Modalidade), que reprovou num teste que
aquele branch não toca.
**Natureza:** a instância foi corrigida (`a6443f5`); a **classe** fica registrada. Protegê-la é
decisão de escopo, e não desta entrega.

## O que aconteceu

As duas execuções do CI reprovaram no mesmo caso, e em nada mais:

```
1 failed, 4680 passed, 2 skipped
FAILED tests/integration/portal/test_historico_publico.py::
       test_retificacao_com_vigencia_futura_e_ato_publicado_que_ainda_nao_vale
       assert 'vigente desde 26/09/2026' in '<!DOCTYPE html>…'
```

A mesma suíte, na mesma árvore, rodada localmente à tarde: **4681 passando, 2 pulados**.

## Por que

O teste montava a data esperada assim:

```python
daqui_a_quinze = timezone.now() + timedelta(days=15)
assert f"vigente desde {daqui_a_quinze.strftime('%d/%m/%Y')}" in pagina
```

`timezone.now()` devolve **UTC**. A página renderiza por `{{ ato.vigente_desde|date:"d/m/Y" }}`, e o
filtro `date` converte para `TIME_ZONE` — `America/Sao_Paulo`, três horas atrás. Entre **00h e 03h
UTC** os dois caem em dias diferentes, e a asserção compara datas que nunca vão bater.

O CI rodou à 01h38 UTC:

| | |
|---|---|
| esperado pelo teste (UTC) | `26/09/2026` |
| renderizado pela página (zona institucional) | `25/09/2026` |

O Brasil não tem mais horário de verão desde 2019, então o deslocamento é fixo em −3h e a janela é
sempre a mesma: **três horas por dia**, das 21h às 23h59 de Brasília.

## Por que ninguém viu

O CI dispara em `push` e `pull_request`, e não em horário marcado — de modo que a janela só é
atingida quando alguém empurra código no fim da tarde. Quem roda a suíte localmente durante o
expediente nunca vê.

O teste nasceu **ontem**, com a `024` (`265b7b9`, 10/09/2026), e esta foi a primeira noite dele.
Não é código velho apodrecendo: é uma asserção escrita hoje que já nasce com a janela dentro.

O defeito é do mesmo formato do
[achado da suíte em SQLite](achado-suite-em-sqlite.md): verde que não corresponde a verde nenhum —
só que aqui o eixo é a hora do dia, e não o banco.

## O que **não** está quebrado, e por que quase esteve

A suíte tem uma dúzia de testes que comparam data formatada com o que a tela mostra, e a maioria
usa `.astimezone()` **sem argumento** — que converte para o fuso local da *máquina*. O runner do
GitHub roda em UTC, então esses testes deveriam quebrar na mesma janela. Não quebram, e a razão é
indireta: ao carregar as settings, o Django escreve `os.environ["TZ"] = TIME_ZONE` e chama
`time.tzset()` (`django/conf/__init__.py`). O fuso do **processo** passa a ser o institucional, e
`.astimezone()` acerta por consequência.

Vale dizer o que isso significa: aqueles testes estão certos **por causa de um efeito colateral de
uma configuração**, e não porque digam o que querem dizer. `localtime()` — que
`tests/portal/test_resultado_da_etapa.py` já usava — diz.

## O que foi corrigido

Uma linha, no único lugar da suíte que ainda formatava instante cru para comparar com tela:

```python
assert f"vigente desde {localtime(daqui_a_quinze).strftime('%d/%m/%Y')}" in pagina
```

## O que continua aberto

Nada impede o próximo. Não há verificação que reprove uma asserção de data escrita em UTC, e a
janela de três horas continua sendo o único momento em que ela se revela.

## Os caminhos, sem escolher nenhum

1. **Rodar o CI com `TZ=UTC` explícito e uma execução extra dentro da janela** — por exemplo, um
   `schedule` diário às 02h UTC. Faz a classe inteira aparecer em vez de esperar por um `push`
   noturno. Custa uma execução por dia.
2. **Congelar o relógio nos testes que dependem dele**, com uma fixture que fixe `timezone.now()`
   num instante conhecido. Elimina a dependência em vez de vigiá-la, e é o que torna o caso
   reproduzível — hoje não há como escrever um teste que prove este defeito.
3. **Proibir `strftime` sobre instante não convertido**, por varredura na suíte, no formato que
   `tests/test_citacoes_de_requisito.py` já usa para citações. Barato e estreito: pega exatamente
   esta forma, e não a próxima.
4. **Deixar como está e confiar no `tzset` do Django.** É o estado de hoje, e funciona — desde que
   ninguém mude `TIME_ZONE`, rode teste fora do carregamento das settings, ou escreva a próxima
   asserção em UTC.

Enquanto não houver decisão, o que é verdade: a suíte passa, e uma asserção de data escrita em UTC
volta a reprovar o CI em qualquer `push` feito entre 21h e meia-noite.
