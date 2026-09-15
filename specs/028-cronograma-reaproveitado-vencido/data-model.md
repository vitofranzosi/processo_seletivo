# Modelo — 028 · Cronograma reaproveitado não nasce publicável

Fase 1. **Nenhuma entidade nasce, nenhuma muda de forma, nenhuma tabela é tocada.** Este documento
existe para dizer onde cada regra passa a morar e o que ela lê.

---

## 1 · O que não muda

| Entidade | Situação |
|---|---|
| `EventoCronograma` | mesma tabela, mesmas colunas, mesmas três constraints. `start_at`, `end_at` e `is_registration_period` continuam como estão |
| `Cronograma` | inalterado |
| `Edital.year` | inalterado, e continua **não retificável** pelo contrato da `026`. Passa a ser lido como referência de uma advertência |
| Conteúdo publicado (`schedule`, `year`) | mesma forma, mesmo degrau, mesmos bytes. `EVENTO_PUBLICADO` não ganha nem perde campo (`FR-353`) |
| Contrato de mutabilidade (`026`) | inalterado. `startAt` e `endAt` continuam retificáveis; `year`, não |
| `ValidationFinding` e as três severidades | inalterados. Esta feature acrescenta **casos**, e não mecanismo |
| `periodo_de_inscricoes` / `Periodo` | inalterados. Ganham um segundo consumidor, e nenhuma linha nova |

**Nenhuma migration.** Se o plano produzir uma, alguma decisão foi violada.

---

## 2 · O conceito que esta feature acrescenta: *vencido*

Não é campo nem tabela — é um predicado, e vive numa função.

```
vencido(inicio, termino, *, agora) = (inicio is not None and inicio < agora)
                                  or (termino is not None and termino < agora)
```

Três consequências, e as três são requisito:

1. **O `<` é estrito.** Instante igual ao do ato não venceu (`FR-347`). É a mesma régua que
   `periodo_de_inscricoes` já aplica com `agora > fim`, e escrevê-la diferente aqui faria o selo e o
   impedimento discordarem sobre o mesmo segundo.
2. **`termino` ausente não vence** por si (`FR-347`); quem responde é o início. Um Evento sem término
   declarado é Evento que o Edital não fechou, e inventar-lhe um fim seria o sistema criando prazo —
   a mesma recusa que `periodo_de_inscricoes` já registra por escrito.
3. **Instante malformado não chega aqui.** Quem acusa texto que não é instante é a conferência de
   forma (`INSTANTE`, `EVENTO_PUBLICADO`), e empilhar duas acusações sobre a mesma causa esconde a
   que resolve. É o mesmo recuo que `_perfis_bem_formados` pratica um nível acima.

### O ano, que é leitura e não predicado

```
ano_do_evento(instante) = instante.astimezone(ZONA_INSTITUCIONAL).year
```

**O ano é o do início, e nunca o do término** (`T-006`). Um Evento que começa em dezembro e termina
em janeiro é a definição de período que atravessa o ano; conferir os dois acusaria todo Edital de fim
de ano, que é o caso que a `D-006` decidiu não incomodar.

---

## 3 · As duas formas do mesmo instante, e por que o predicado ignora as duas

O predicado recebe `datetime`, e não texto nem coluna. É o que permite que os dois lados o chamem:

| Quem chama | O que tem | O que faz antes |
|---|---|---|
| `editais/domain/validation.py` | `startAt`/`endAt` como texto ISO do snapshot | converte, e recua em silêncio se não converter |
| `interface/views.py` (`_progresso`) | `start_at`/`end_at` como `datetime` do ORM | nada |

Uma regra, um lugar, duas entradas. A alternativa — filtrar no banco de um lado e conferir em Python
do outro — poria a `FR-359` em duas grafias que ninguém compara, que é a divergência que esta feature
existe para não produzir ([research.md](research.md), `T-003`).

---

## 4 · Os três achados

| Código | Severidade | Caminho | Condição | Ato |
|---|---|---|---|---|
| `schedule_event_in_past` | advertência | `/schedule/id=<uuid>/endAt`, ou `/startAt` quando não há término | `vencido(inicio, termino, agora=agora)` | só publicação |
| `schedule_event_year_mismatch` | advertência | `/schedule/id=<uuid>/startAt` | `ano_do_evento(inicio) != snapshot["year"]` | só publicação |
| `registration_period_closed` | **erro impeditivo** | `/schedule/id=<uuid>/endAt` | `periodo_de_inscricoes(snapshot, agora).estado == ENCERRADO` | só publicação |

**Um achado por Evento e por espécie** (`FR-345`). Um Evento que esteja no passado **e** tenha ano
divergente produz dois achados, cada um uma vez, cada um nomeando o instante de que fala. Um Evento
cujo início **e** término já passaram produz **um** `schedule_event_in_past`, e ele nomeia o
**término** — o instante mais tardio, o que diz que o Evento inteiro acabou (`FR-343a`). O início só
é nomeado quando não há término declarado, e o caminho do achado acompanha o instante que a mensagem
nomeia, para que a âncora leve ao campo de que a frase fala.

**O impeditivo pode coexistir com a advertência sobre o mesmo Evento**, e deve: o período encerrado é
também um evento no passado, e as duas coisas se resolvem no mesmo campo mas dizem coisas diferentes
— uma é *"esta data já passou"*, a outra é *"este Edital não receberá inscrição alguma"*.

### O que nenhum deles faz

Nenhum lê o relógio por conta própria (`FR-341`), nenhum escreve, sugere ou desloca data
(`FR-351`), nenhum confere duração (`FR-352`), e nenhum existe num ato de Retificação (`FR-354`).

---

## 5 · O ato, e o corte que ele faz

A condição por ato é a mesma forma que a `027` já pratica em `_linha_geral_exigida` e
`_acervo_sem_quadro`:

```python
if ato != ATO_DE_PUBLICACAO:
    return []
```

**No ato de Retificação, os três não existem.** Não por brandura: no acervo, evento vencido é a
condição normal de todo Edital publicado, e o cronograma inteiro de um Edital de 2026 já passou.
Produzir advertência ali faria toda Retificação carregar uma advertência por Evento — e o que se
repete a cada ato deixa de ser lido. Recusar prenderia o acervo.

> **O padrão de `ato` é publicação, e ele erra pelo lado que recusa.** Quem esquecer o parâmetro
> produz os achados, e não os esconde. É a razão que a `027` deixou escrita na própria função, e
> vale igual aqui.

---

## 6 · O selo do Cronograma

| Antes | Depois |
|---|---|
| `CONCLUIDA` se `edital.cronograma.eventos.exists()` | `CONCLUIDA` se há Evento **e** nenhum deles está vencido |

Três coisas que o selo **não** passa a fazer:

1. **Não considera o ano.** Divergência de ano é advertência e nada mais (`FR-359` fala de passado, e
   só); apagar o selo por ela daria a um Edital legítimo de dezembro a aparência de incompleto.
2. **Não impede nada.** Pendente orienta quem retoma; quem fecha porta é o impeditivo (`FR-362`).
3. **Não muda os outros oito selos** (`FR-361`). Cada etapa tem uma noção própria de "válida", e
   decidi-las em bloco é o que produz regra que ninguém revisou.

E volta a `CONCLUIDA` sozinho quando as datas são corrigidas, porque é derivado e não persistido
(`FR-360`) — que é a mesma razão de ele estar certo já na primeira abertura depois do
reaproveitamento, sem gravação nenhuma.

---

## 7 · O instante de referência

| Quem | De onde vem |
|---|---|
| `submit_edital`, `publish_edital` | o `now` de `command_context()`, o mesmo que a publicação registra |
| `interface/views.py` | o instante da requisição, resolvido uma vez |
| chamada sem `agora` | `datetime.now(ZONA_INSTITUCIONAL)`, resolvido **uma vez** no topo de `validate_for_publication` |

A terceira linha é o padrão, e ela erra pelo lado que acusa. As duas primeiras são o que a
Constituição pede: *"operações relacionadas DEVEM compartilhar referência temporal consistente na
mesma transação"*.

---

## 8 · O que a demonstração passa a conter

| Edital | Antes | Depois |
|---|---|---|
| 1º — inscrições abertas | publicado | **inalterado** |
| 2º — inscrições encerradas | publicado já com o período vencido | publicado com o período **aberto**, e fechado por **Retificação** (`T-008`) |
| 3º — que ordena por sorteio | publicado | **inalterado** |
| 4º — reaproveitado do 2º | não existe | **em elaboração**, com cronograma vencido, ano divergente e período encerrado (`FR-366`, `FR-367`) |

A mudança no segundo não é conserto de fixture: é o Edital passando a contar a verdade. Nenhum Edital
do mundo é publicado depois de as inscrições fecharem — ele é publicado antes, e o prazo vence com o
tempo.
