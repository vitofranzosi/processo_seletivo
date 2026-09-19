# Quickstart — validação da `036` · Instrução do recurso

Cinco cenários. **Os quatro primeiros são pelos canais reais** — o portal para o candidato, a
interface administrativa para a comissão e a autoridade. É o que o Princípio VI cobra, e é o que
pegou, nas três features anteriores, defeitos que teste nenhum pegou.

## Preparação

```bash
cd backend && uv sync --extra dev && make preparar
```

Confira que a saída termina em `N de M` com **N diferente de zero**. O `runserver` precisa de
`INTERFACE_SELETOR_IDENTIDADE=true` e de `PORTAL_IDENTIDADE_DEMO=true` — sem eles, a gestão devolve
503 e o portal não deixa ninguém se identificar.

**O cenário**: um Edital com Etapa **eliminatória** e nota mínima declarada; uma inscrição avaliada
com nota **abaixo** da mínima, com o parecer escrito; o resultado divulgado; e o prazo recursal
**aberto**.

> **O código de acesso do portal sai no terminal do servidor.** Na execução nativa o backend de
> e-mail é o de console: a mensagem é impressa onde o `runserver` está rodando, e não há outro lugar
> de onde lê-la.

---

## Cenário 1 — o candidato lê a razão (`SC-182`)

1. Entre no portal como o titular da inscrição eliminada.
2. Abra o acompanhamento.

**Esperado**: a tela mostra **as duas frases**. O motivo — *"pontuação inferior à nota mínima…"* — e,
ao lado dele, **o parecer que o avaliador escreveu**. Identificado como a fundamentação daquele
resultado, e não como um segundo motivo.

3. Confira que **nada de terceiro** aparece: nenhum nome, nenhuma nota alheia, nenhum parecer de
   outra pessoa.

### Contraprovas

| | Esperado |
|---|---|
| resultado **favorável** | nada muda |
| Etapa **não eliminatória**, sem parecer escrito | a tela **diz que não há parecer** — não fica em silêncio |
| entrar como **outro candidato** | não alcança nada daquela inscrição |

---

## Cenário 2 — o prazo fecha, e a tela diz (`FR-524`)

**Como encerrar o prazo sem mexer no relógio.** A composição **recusa Evento com data passada** — a
etapa fica pendente —, de modo que compor um Edital já vencido não é caminho. O que funciona é
declarar a **janela recursal do marco curta**, de minutos, e esperar ela passar de verdade.

> **Se não houver caminho pela interface, registre e siga.** A `034` esbarrou no equivalente — a
> Retificação não acrescenta Modalidade — e registrou *"inexequível pela interface"* com a metade que
> deu para percorrer. Fazer o mesmo aqui é a resposta certa; **contornar por banco ou por relógio não
> é**, e o protocolo do projeto proíbe.

1. Faça o prazo recursal se encerrar, pelo caminho acima.
2. **Confira que não há recurso pendente** daquela inscrição — é a segunda condição da `FR-522`, e
   com um recurso em julgamento o parecer **continua aparecendo**, corretamente.
3. Abra o acompanhamento como o titular.

**Esperado**: o parecer **não** aparece, **e a tela diz por quê**.

### A contraprova da segunda condição, e ela é a que o `analyze` acrescentou

4. No mesmo Edital, com **outra** inscrição eliminada: interponha o recurso **antes** de o prazo
   fechar, e deixe-o **sem decisão**.
5. Depois de o prazo fechar, abra o acompanhamento como esse titular.

**Esperado**: o parecer **continua aparecendo**. Quem recorreu decide se insiste, escreve réplica ou
aceita a decisão — e fazer isso sem poder reler o texto que está contestando é o defeito desta
feature acontecendo um passo adiante.

**Este é o cenário que separa a feature de um defeito.** Sumir em silêncio faria a pessoa pensar que
perdeu algo, ou que o sistema falhou. Se a frase não estiver lá, a `FR-524` não foi cumprida — ainda
que o parecer tenha sumido corretamente.

---

## Cenário 3 — quem julga, antes e depois da instrução (`SC-183`)

1. Interponha o recurso pelo portal, como o titular.
2. Entre na gestão como alguém que tem **apenas** a capacidade de julgar recursos — sem presidir,
   sem auditoria, sem consultar inscrições. Abra a peça.

**Esperado**: a tela diz **o que falta e a quem pedir**. E **não oferece** caminho que ele não
alcança — essa é a garantia da `033`, e ela precisa continuar de pé.

3. Entre como a autoridade competente e **pratique a instrução**.

**Esperado**: o ato acontece, com autor e instante.

4. Volte como quem **só julga** e abra a peça.

**Esperado**: ele lê **o parecer atacado** e alcança **o documento citado**. E nada além daquele
recurso.

5. **A contraprova que mais importa**: com o mesmo julgador, abra **outro** recurso da mesma Etapa.

**Esperado**: ele **não** alcança nada por causa da instrução anterior. Se alcançar, o que se
construiu foi uma permissão, e não um ato.

---

## Cenário 4 — o alcance morre com a decisão (`SC-185`)

1. Com a instrução praticada, **decida** o recurso.
2. Volte à peça como quem julgou.

**Esperado**: a tela diz **que houve instrução e que o alcance se encerrou** — e não *"nada foi
instruído"*, que seria falso sobre um ato que aconteceu. O **registro** permanece; o **acesso**
terminou.

**As duas metades são o ponto.** Nada se apaga; a porta fecha. E a tela precisa saber dizer **os três
estados**, não dois.

---

## Cenário 5 — a auditoria responde quem viu o quê (`SC-184`)

Este precisa da auditoria, e é o único que não é percurso de tela comum.

1. Consulte a trilha do recurso instruído.

**Esperado**: aparecem **dois** tipos de registro — o **ato** de instrução (quem, quando, qual
recurso, o que foi anexado **por espécie**) e o **acesso exercido** por quem julgou.

2. **Contraprova, e ela é obrigatória**: o texto do parecer, o conteúdo do documento e a fundamentação
   de quem recorreu **não** aparecem em registro nenhum.

Copiar conteúdo sensível para a trilha criaria uma segunda cópia, num lugar com outro regime de
acesso e outro tempo de retenção. É a regra que a `018` já pratica, e esta feature não pode quebrá-la
ao acrescentar registros.

---

## Verificação

```bash
cd backend && make lint check test-pg
```

`test-pg` e **nunca** `test`. `lint` são **dois** passos. **Não edite arquivos do projeto enquanto a
suíte roda.**

**Esta feature tem migration** — é entidade nova —, e por isso `makemigrations --check` **não** é a
prova de "nada mudou". O que ele prova aqui é que a migration escrita cobre o modelo. A promessa que
vale a conferência por leitura do diff é outra: **nenhuma capacidade nova, nenhum papel novo, nenhum
parecer alterado**.

### O caso alterado, e por que ele é um só

`research.md` `R-6` nomeia o único caso que muda de sentido: o que afirma hoje que quem só julga lê o
que lhe falta. Os dois vizinhos — quem audita, quem consulta inscrições — **permanecem**, e são a
contraprova de que a feature não ampliou nada por engano.

**Reconte contra a implementação.** A `034` previu oito e entregou doze, porque um código vivia num
dicionário que quatro casos liam.
