# O "antes", medido antes de qualquer edição

**Quando**: 19/09/2026, na worktree `spec-037-implementacao`, sobre a `main` `23bf70e`.

**Por que existe.** Três das quatro histórias desta feature são, essencialmente, **prosa** — e prosa
é o que muda sem que nada quebre. Sem o "antes" gravado, "quatro testes mudaram de sentido" é
afirmação sem verificação possível: a `034` previu oito e entregou doze, e só descobriu isso porque
tinha contra o que comparar.

---

## A contagem da suíte

```
$ cd backend && make test-pg
================= 7343 passed, 11 skipped in 770.64s (0:12:50) =================
```

**7343 passando, 11 pulados.** É este o número contra o qual a `T033` compara.

**E o `make preparar` fecha em `32 de 32`**, que é o que o segundo portão manda conferir:

```
Papéis provisionados. 32 de 32 tabelas append-only estão sem UPDATE nem DELETE para o runtime.
```

A 32ª veio da `036`, que já está na `main`. Esta feature **não tem migration**, e o total tem de
continuar `32` no fim — ver `32` de novo prova que nenhuma tabela nasceu aqui.

---

## Os quatro casos que mudam de sentido, citados

São os de `research.md` `R-4`. **Dois defendem o defeito por escrito** — e é por isso que a
citação, e não o nome do arquivo, é o registro.

### 1. `tests/unit/editais/test_calendario.py::test_evento_em_curso_vence_pelo_inicio`

```python
def test_evento_em_curso_vence_pelo_inicio():
    """Começou e não terminou: a advertência existe, e é só isso que este predicado diz."""
    assert vencido(em(days=-1), em(days=2), agora=AGORA) is True
```

**O nome afirma a régua errada, e a docstring a explica.** O nome fica falso com a `FR-545`, e
renomear é obrigatório: um caso chamado *"vence pelo início"* que passa a afirmar *"não vence"* é a
forma mais discreta de a suíte mentir.

### 2. `tests/unit/editais/test_calendario.py::test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro`

```python
def test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro():
    """O término ainda não passou: nomeá-lo faria a frase acusar um prazo que está correndo."""
    inicio = em(days=-1)
    assert instante_vencido(inicio, em(days=2), agora=AGORA) == inicio
```

**Este é o que prende a `FR-546a`.** A escolha do instante e o predicado moram no mesmo módulo, e
se só o predicado mudar, este caso continuará verde afirmando que o Evento em curso tem instante
vencido — as duas funções discordariam sobre o mesmo Evento, que é a divergência que a `028` criou
o módulo para impedir. A docstring está **certa sobre a intenção** e prende o comportamento errado:
o término não passou, e é por isso que o Evento não venceu — não para que outro instante seja
nomeado em lugar dele.

### 3. `tests/unit/editais/test_cronograma_vencido.py::test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro`

```python
def test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro():
    snapshot = conteudo(evento(inicio=em(days=-1), fim=em(days=2)))

    (item,) = achados(snapshot)

    assert item.path == f"/schedule/id={EVENTO}/startAt"
```

O mesmo, na conferência de publicação. O `(item,)` **exige que haja exatamente um achado** — depois
da correção não haverá nenhum, e o desempacotamento falha antes da asserção.

### 4. `tests/unit/editais/test_cronograma_vencido.py::test_periodo_em_curso_adverte_mas_nao_impede`

```python
def test_periodo_em_curso_adverte_mas_nao_impede():
    """O Edital que abre inscrições e é publicado no mesmo dia é legítimo."""
    snapshot = periodo(inicio=em(days=-1), fim=em(days=9))

    assert codigos(snapshot) == ["schedule_event_in_past"]
    assert blocking_findings(achados(snapshot)) == []
```

**O mais perigoso dos quatro.** A docstring descreve exatamente o Edital que a `US3` existe para
destravar — *"abre inscrições e é publicado no mesmo dia é legítimo"* —, e a asserção logo abaixo
prende a advertência que o impede de concluir a etapa. O nome fica falso duas vezes: ele passa a não
advertir, e "adverte mas não impede" deixa de descrever o que o caso afirma.

---

## Os vizinhos que devem permanecer

Contados por `grep -c '^def test_'` nos três arquivos que a `R-4` nomeia, e nos dois acima:

| Arquivo | Casos hoje |
|---|---|
| `tests/interface/test_destinos_do_edital.py` | **10** |
| `tests/interface/test_corte.py` | **13** |
| `tests/interface/test_selo_do_cronograma.py` | **11** |
| `tests/unit/editais/test_calendario.py` | 14 |
| `tests/unit/editais/test_cronograma_vencido.py` | 29 |

Os três primeiros são os que as tarefas mandam **acrescentar ao fim**: a `030` sobrescreveu um
arquivo de teste existente e oito regressões sumiram sem a suíte ficar vermelha.

---

## O que a `T031` já sabe que vai recontar

**A `R-4` prevê quatro, e a medição do ambiente achou mais três antes de a implementação começar.**
Fica registrado aqui, e não descoberto depois:

`tests/interface/test_destinos_do_edital.py` monta o `certame` com `rascunho_com_marco`, e **esse
marco não declara regra de corte**. Três casos afirmam a lista de destinos **por igualdade exata**:

| Caso | O que ele afirma hoje |
|---|---|
| `test_a_presidencia_sem_publicar_nao_perde_destino_nenhum` | `[ordenacao, ocupacao]` |
| `test_quem_preside_e_publica_ve_a_uniao_sem_repetir` | `[ordenacao, ocupacao, divulgacao]` |
| `test_a_auditoria_continua_lendo_o_que_lia` | `[ordenacao, ocupacao]` |

A `FR-538` acrescenta o corte a essas listas. **O que cada caso afirma não muda** — "nenhum destino
a menos" continua sendo a promessa, e ela não é desfeita por um a mais —, mas o valor esperado
cresce, e isso é alteração de teste que a `T031` tem de contar.

---

## As quatro premissas, conferidas por varredura

O "confirme, não assuma" que a `035` provou valer. Nenhuma das quatro foi herdada da `research.md`
sem conferência no código desta worktree.

### 1. A recusa do marco sem regra sai como **conflito**, e não como ausência (`R-1`) ✓

`classificacao/application/corte.py`:

```python
    regra = regra_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if regra is None:
        raise DomainError(
            "marco_sem_regra_de_corte",
            "Este marco não declara regra de corte: o Edital não publicou quantos progridem.",
            409,
        )
```

**409, e não 404** — e a view só transforma 404 em `Http404`; 409 ela mostra. A frase tem código
próprio e foi escrita para este caso, e não emprestada do caso da ordem obsoleta. A `D-001` está de
pé: nada a reescrever.

**E a falha que a `R-1` achou além disso continua lá.** `corte.html` anexa o mesmo caminho às três
recusas:

```html
<p class="aviso" role="status">{{ recusa }} <a href="{{ para_a_ordenacao }}">Ir para a classificação deste recorte</a>.</p>
```

### 2. A pendência de Perfil **já é corrigível e já leva à etapa** (`R-5`) ✓

`interface/views.py`:

```python
DESTINO_DA_PENDENCIA = {
    ...
    "profiles": ("perfis", "#perfis-titulo", True),
```

O `True` é o "corrigível", e `_pendencias.html` imprime *"Ir para Perfis"*. **"O que falta" já é
dito, com caminho** — fechado por feature anterior, e não por esta. O que falta é "a quem pedir", e
`_pendencias(edital, *, agora=None)` **não recebe o ator**: é assinatura a mudar, com chamadores a
encontrar, e é por isso que a `FR-542b` manda percorrer antes de prometer.

### 3. `frase_da_recusa` existe e é pública (`R-6`) — **e não produz a forma cheia** (`R-11`) ✓

`seguranca/application/authorization.py`:

```python
    return (
        f"Esta operação depende {_enumerar([_com_de(base.nome) for base in bases])}{sozinha}. "
        f"Peça {_enumerar([base.a_quem for base in bases])}."
    )
```

**A frase acaba aí**, sem a oração do ato que a `FR-543a` exige. E ela abre com *"Esta operação
depende de…"* porque tem um só chamador, `require_authorization_base`, que levanta 403 — situação
de fala que esta feature não tem.

**E a varredura confirma que não há rede**: `grep -rn 'frase_da_recusa' tests/` não devolve
ocorrência alguma. Ampliá-lo é mexer em código sem teste, e a `T013` cria a rede antes.

### 4. A lista de Etapas do cartão do marco **não carrega o peso** (`R-8`) ✓

`interface/views.py`:

```python
    etapas = [
        {"id": str(etapa.id), "rotulo": f"{etapa.name}"}
        for etapa in edital.etapas.filter(classificatory=True).order_by("order")
    ]
```

Identificador e rótulo, e nada mais. E a lista é consumida em **quatro** pontos do arquivo — a
composição, o marco acrescentado, o **fragmento recomposto** e o critério —, todos pelo mesmo
helper: acrescentar o campo nele cobre os quatro.
