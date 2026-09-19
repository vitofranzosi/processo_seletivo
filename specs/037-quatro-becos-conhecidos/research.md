# Phase 0 — o que foi medido, e o que a medição mudou

**Quando**: 19/09/2026. **Contra**: a worktree `spec-037-quatro-becos`, sobre a `main` `2beb2d9`.

**Método**: leitura do código e dos testes que o prendem, com a frase literal citada sempre que a
spec promete não reescrevê-la. Nenhuma afirmação abaixo foi herdada da auditoria sem conferência.

**Placar**: das cinco afirmações que a spec pediu para confirmar, **três se confirmaram**, **uma se
confirmou pela metade e produziu um requisito novo**, e **uma se mostrou parcialmente já resolvida**.

---

## R-1 — A tela do corte explica, sim. Mas o **caminho** que ela oferece é do outro caso.

**Confirmado, e com uma falha que a feature criaria.**

A recusa do domínio para este caso existe, com código próprio e frase própria
(`classificacao/application/corte.py`):

> *"Este marco não declara regra de corte: o Edital não publicou quantos progridem."*

Ela sai como `DomainError("marco_sem_regra_de_corte", …, **409**)` — e **409, não 404**. A view só
transforma 404 em `Http404`; 409 ela **mostra**. A premissa da `D-001` está de pé: a tela explica, e
a frase foi escrita para este caso, não emprestada do caso da ordem obsoleta.

**O que a medição achou além disso.** O template imprime a recusa e anexa **sempre o mesmo caminho**:

```
<p class="aviso">{{ recusa }} <a href="{{ para_a_ordenacao }}">Ir para a classificação deste recorte</a>.</p>
```

São **três** recusas passando por esse bloco, e o caminho só serve a duas:

| Recusa | O que falta | "Ir para a classificação" resolve? |
|---|---|---|
| `sem_ato_vigente` | a ordem do recorte | **sim** — é para lá que a frase manda |
| `ato_obsoleto` | reemitir a ordem | **sim** |
| `marco_sem_regra_de_corte` | a **regra de corte**, que é conteúdo do Edital | **não** |

**Hoje isso é inalcançável**, porque o link para o corte não é oferecido quando não há regra. A
`FR-538` o torna alcançável — e **a feature entregaria, no fim do caminho que ela abre, um segundo
caminho que não resolve**. É o `ACH-40` outra vez, criado pela correção do `ACH-46`.

**Consequência**: requisito novo, `FR-539a`. A frase não muda; o **caminho** passa a depender de qual
recusa é.

**Testes que hoje prendem o destino**: `tests/interface/test_destinos_do_edital.py` (**10** casos) e
`tests/interface/test_corte.py` (**13**). Nenhum deles afirma, pelo nome, que o destino some sem
regra — a conta precisa ser refeita **caso a caso** na implementação, e não pelo nome do arquivo.

---

## R-2 — A régua do vencido: um predicado, **dois** consumidores, e um homônimo

**Confirmado.** `editais/domain/calendario.py::vencido` devolve

```
(inicio is not None and inicio < agora) or (termino is not None and termino < agora)
```

Os dois consumidores que o docstring nomeia existem e são só esses dois:

| Onde | O quê |
|---|---|
| `interface/views.py:828` | o selo da etapa do Cronograma — o `PENDENTE` que nunca conclui |
| `editais/domain/validation.py:2004` | a conferência de publicação — a advertência `schedule_event_in_past` |

**Não há terceiro.** Há um **homônimo**: `interface/static/interface/rascunho.js` tem uma função
`vencido` própria, sobre validade de rascunho guardado no navegador. Nada a ver, e fica registrado
para que ninguém a "corrija" junto.

---

## R-3 — `instante_vencido` **muda junto**, e não é opcional

**Achado que a spec não previa.**

Se `vencido` deixar de responder verdadeiro para o Evento em curso e `instante_vencido` continuar
devolvendo o início dele, as duas funções do mesmo módulo passam a **discordar sobre o mesmo
Evento** — que é exatamente a divergência que a `028` criou o módulo para impedir.

O caso está prendido por teste, com o nome dizendo o que afirma:
`test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro`.

---

## R-4 — Quatro casos de teste **mudam de sentido**, e dois deles defendem o defeito por escrito

**Medido, e é a superfície da `US3`.**

| Arquivo | Caso | O que ele afirma hoje |
|---|---|---|
| `tests/unit/editais/test_calendario.py` | `test_evento_em_curso_vence_pelo_inicio` | *"Começou e não terminou: a advertência existe"* |
| `tests/unit/editais/test_calendario.py` | `test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` | o início é o instante nomeado |
| `tests/unit/editais/test_cronograma_vencido.py` | `test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` | o mesmo, na conferência |
| `tests/unit/editais/test_cronograma_vencido.py` | `test_periodo_em_curso_adverte_mas_nao_impede` | `codigos(snapshot) == ["schedule_event_in_past"]` |

O último é o mais perigoso: o **nome** dele fica falso depois da correção — passa a não advertir — e
a docstring dele diz *"O Edital que abre inscrições e é publicado no mesmo dia é legítimo"*, que é
precisamente o Edital que hoje **não consegue concluir a etapa**. O teste descreve a intenção certa e
prende o comportamento errado.

**Renomear é obrigatório**, e não cosmético: um caso chamado *"adverte mas não impede"* que passa a
afirmar *"não adverte"* é a forma mais discreta de a suíte mentir.

**São quatro, medidos hoje.** A `034` previu oito e entregou doze; recontar na implementação é tarefa,
não zelo.

---

## R-5 — O `ACH-02` já está **meio fechado**, e a metade que sobra precisa de algo que a tela não tem

**A afirmação de partida não se confirmou inteira.**

A reavaliação restata o `ACH-02` como *"o gestor não sabe o que falta nem a quem pedir"*. Medido:

- **"o que falta" já é dito, com caminho.** `DESTINO_DA_PENDENCIA` mapeia `"profiles"` para
  `("perfis", "#perfis-titulo", **True**)` — corrigível, com âncora —, e `_pendencias.html` imprime
  *"Ir para Perfis"*. Isso foi fechado por feature anterior, não por esta.
- **"a quem pedir" não é dito** — e para dizê-lo é preciso saber as permissões de quem lê.
  `_pendencias(edital, *, agora=None)` **não recebe o ator**. Não é uma frase a mais: é assinatura a
  mudar e chamadores a encontrar.

**E há uma pergunta que o código não responde**: se o caminho existe, o gestor da auditoria travou
por **falta de papel** ou por outra razão? A auditoria inferiu o papel ausente da ausência do
controle — e o controle existe. **Isto só se decide percorrendo**, com o ator exato. A `034` e a
`033` já mostraram que 404 na gestão costuma ser autorização, e que reproduzir com o papel certo vem
antes de caçar rota.

**Consequência**: a `US2` entra em duas partes com pesos diferentes. A do `ACH-30` é uma frase. A do
`ACH-02` **começa por um percurso que decide se há o que fazer**, e a spec passa a dizer isso.

---

## R-6 — A formulação existe como **mecanismo**, e não só como padrão a copiar

**Achado que encolhe a `US2`.**

A `033` deixou `seguranca/application/authorization.py::frase_da_recusa(bases)`, e o docstring diz
por que ela é pública:

> *"existe **uma** maneira de dizer isto, e criar uma segunda para a mesma coisa é o que a feature
> existe para não fazer"*

Ela produz *"Esta operação depende da permissão de X. Peça a alguém com a permissão de X."*, com
`base_de_permissao(nome)` montando as duas posições da frase e a contração que o português exige.

**Escrever a frase à mão nas telas novas derrotaria a guarda que a `033` deixou.** A `FR-543` passa a
significar *usar o mecanismo*, e não *imitar o texto*.

---

## R-7 — A formulação **não é uniforme hoje**, e há quatro ocorrências renderizadas

| Onde | Como |
|---|---|
| `detalhe.html:60` | "Peça a alguém com a permissão de publicar **que conclua o ato**." |
| `ato_ordenacao.html:51` | "Peça a alguém com a permissão de publicar resultado **que …**" |
| `ordenacao.html:112` | "peça a alguém com a permissão de publicar resultado **que a conclua**." |
| `ordenacao.html:62` | "peça a alguém com a permissão de publicar resultado." — **sem a oração final** |

A forma cheia é *"peça a alguém com a permissão de **X** que **Y**"*, e uma das quatro larga o `Y`.
As frases novas seguem a **cheia**.

---

## R-8 — O cartão do marco **não tem os pesos**, mas tem o mecanismo que a `FR-551` precisa

**Medido, e a `FR-551a` continua satisfeita.**

O cartão itera `etapas_classificatorias` com `etapa.id` e `etapa.rotulo` — **sem o peso**. Nomear as
Etapas enumeradas sem peso exige **um campo a mais no que já é montado**, e não um controle novo nem
uma segunda consulta.

E o momento existe: a seleção dispara `fragmento-marco-recomposto`, que **reconstrói o cartão a cada
mudança**. *"No momento em que enumera"* é literalmente esse ciclo — não há tela a inventar.

O cartão **já fala do peso**, e a frase nova não pode contradizê-la:

> *"Só Etapas classificatórias. O peso de cada uma é o que ela já publica; aqui se escolhe quais
> entram."*

As duas frases que cobram o peso hoje, e com as quais a nova precisa concordar:

| Onde | Frase |
|---|---|
| `editais/domain/validation.py:718` | *"O marco enumera uma Etapa sem peso declarado. Quem enumera declara o peso."* |
| `classificacao/domain/combinacao.py:58` | *"Etapa enumerada pelo marco sem peso declarado: quem enumera declara o peso."* |

---

## R-9 — O portal e a gestão **não compartilham a régua**

**Achado que corrige o alcance da `FR-549`.**

O *"Acontecendo agora"* do portal nasce de `portal/leitura.py::_situacao_do_evento`, que é derivação
**própria** e não importa `calendario.vencido`. As duas superfícies não discordam por engano de
cálculo compartilhado: elas discordam porque **são duas leituras independentes do mesmo dado**.

**Consequência**: a `FR-549` promete **concordância de desfecho**, e não unificação de código.
Unificar as duas é mudança maior, com o portal no caminho, e **não cabe aqui** — fica registrado.

---

## Testes de template nas telas tocadas, e a armadilha da prosa

`test_destinos_do_edital.py` (10), `test_corte.py` (13) e `test_selo_do_cronograma.py` (11). Além
deles, `tests/test_gramatica_das_portas.py` varre a gramática das recusas, e `tests/interface/
test_fluxo.py` afirma sobre a tela do Edital.

**A varredura deste repositório lê o comentário do template.** Prosa nova dentro de `{% comment %}`
já quebrou asserção de substring sem nada funcional mudar — e três das quatro histórias desta feature
são, essencialmente, prosa.

---

## O que a Phase 0 mudou na spec

| Mudança | Por quê |
|---|---|
| **`FR-539a` novo** | a `FR-538` tornaria alcançável um caminho que não resolve o caso que ela abre (`R-1`) |
| **`FR-542` reescrita** | "o que falta" já é dito com caminho; o que falta é "a quem pedir", e a tela não tem o ator (`R-5`) |
| **`FR-542b` novo** | o percurso decide se o `ACH-02` ainda tem o que fechar, e vem **antes** de prometer (`R-5`) |
| **`FR-546a` novo** | a escolha do instante discordaria da régua; as duas mudam no mesmo ato (`R-3`) |
| **`FR-543` precisada** | usar `frase_da_recusa`, e não imitar o texto (`R-6`) |
| **`FR-549` precisada** | concordância de desfecho, não unificação de código (`R-9`) |
