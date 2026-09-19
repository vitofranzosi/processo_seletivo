# O "antes" do painel — medido em 19/09/2026

**Quando**: 19/09/2026, na worktree `spec-038-implementacao`, com a árvore **limpa** em `fcb448f`
— a mesma ponta de `origin/main`. **Antes de qualquer edição**, que é o que o portão 1 exige.

**Como**: `cd backend && make test-pg`. Nunca `make test`: no modo padrão 21 casos falham em vez de
pular, e a medição sairia errada sem avisar.

---

## 1. A suíte

```
7454 passed, 11 skipped in 694.63s (0:11:34)
```

**O briefing desta sessão dizia 7406 e 11.** Os pulados batem; os passados **não** — são **48 a
mais**. A árvore estava limpa e em `fcb448f`, de modo que a diferença não é do diff: é do número de
referência, medido antes de alguma das integrações que chegaram à `main` em 19/09. **O "antes" desta
feature é 7454**, e é contra ele que a contagem final se compara.

## 2. O orçamento de consulta — e a descoberta que muda a `T021`

**Os dois guardiões não têm número escrito no arquivo.** Ambos medem em tempo de execução e cobram
**invariância sob escala**, não um teto:

| Guardião | O que escala | Orçamento medido |
|---|---|---|
| `test_sinais.py::test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas` | recursos pendentes (1 → 4) | **21 consultas** |
| `test_fronteira.py::test_o_custo_da_pagina_cresce_com_o_que_mudou_e_nao_com_o_tamanho_do_processo` | inscrições (5 → 10) | **32 consultas** |

O segundo **não está no `R-7`**, que nomeia só o primeiro. Ele cobre `pulso` **e** `sinais` juntos, e
é o que a `US1` mais facilmente move, porque leva os dois a uma segunda tela.

**Consequência para a `T021`**: não há "o número novo" a escrever no lugar de um antigo — o número
nasce da execução. O que a feature precisa provar é que **nenhuma espécie nova acrescenta consulta
por recurso nem por inscrição**. Uma leitura **por recorte** passa nos dois, porque nenhum deles
escala recortes; e é por isso que o custo do `UX-065` precisa ser dito por escrito em vez de
conferido por um `assert` que não o mede. Os números acima são o "antes" com que comparar.

## 3. Os arquivos que cercam a Supervisão — são **cinco**, e **37** casos

| Arquivo | Casos |
|---|---|
| `tests/interface/test_supervisao.py` | 15 |
| `tests/integration/supervisao/test_sinais.py` | 13 |
| `tests/integration/supervisao/test_fronteira.py` | 5 |
| `tests/acceptance/test_supervisao_do_processo.py` | 1 |
| **`tests/unit/interface/test_supervisao.py`** | **3** |
| | **37** |

**O `R-7` conta quatro arquivos e 34 casos.** O quinto é o **guardião do catálogo**:

```python
assert len(supervisao.ESPECIES) == 6
assert supervisao.ESPECIES == (UX_001, UX_002, UX_003, UX_004, UX_005, UX_046)
```

As quatro espécies desta feature o tornam vermelho **por construção** — é o serviço dele, e a
própria docstring registra que ele já fez isso uma vez, quando a `027` abriu o catálogo. Emendá-lo
é parte da `US3` e vai no mesmo commit que acrescenta as espécies: teste de contrato que prende a
citação quebra sozinho se for deixado para depois.

---

## 4. As quatro premissas, reconferidas pela **condição**

**Método**: ler a condição, nunca a mensagem. Foi lendo mensagem que a spec errou duas premissas.

### 4.1 O `UX-005` é a comissão **inteira** impedida — confirmada

`interface/supervisao.py`, em `comissao_impedida`:

```python
if not any(not (membros - impedidos.get(peca.id, set())) for peca in pendentes):
    continue
```

Dispara só quando **alguma peça pendente não tem nenhum membro livre**. A mensagem começa *"Há
recurso aguardando julgamento…"*, e quem a lê conclui o contrário do que o código faz.

### 4.2 O `UX-003` mede **cobertura** — confirmada

`cobertura_insuficiente` segue em frente quando `not resumo["carentes"]`, e `carentes` é
`inscricoes − completas`: inscrição sem avaliador suficiente. Etapa coberta com cinquenta avaliações
paradas não produz sinal nenhum.

### 4.3 Seis no código, cinco no requisito — confirmada

`ESPECIES = (UX_001, UX_002, UX_003, UX_004, UX_005, UX_046)`. A `FR-024` da `022` diz
*"exclusivamente os sinais definidos em `UX-001` a `UX-005`"*. A `027` acrescentou a sexta sem
revisá-la.

### 4.4 A derivação de *ato sem divulgação* vive só em `views.py` — confirmada

`_divulgacao_do_marco`, privada, em `interface/views.py`. Devolve `nunca_divulgado` e `defasadas`, e
filtra as publicações vigentes **por recorte** — premissa que a `034` mudou. `atos_publicados`, em
`publicacoes`, responde outra pergunta: os atos **do Edital**. A varredura não encontra a derivação
em nenhum outro módulo.

**Nenhuma das quatro precisou ser retirada do escopo por não ser derivável** — a `FR-567` não foi
acionada aqui.

---

## 5. Duas medições que os artefatos não tinham, e que decidem o desenho

### 5.1 `resumo_da_etapa` **não devolve `avaliadas`**

O `R-3` escreve *"`completas − avaliadas`"*, e `avaliadas` não está no dicionário devolvido. O que
há é `sem_conclusao = inscricoes − avaliadas`. A conta existe e é a mesma —
`completas − (inscricoes − sem_conclusao)` —, apenas não é a escrita. A diferença importa porque a
forma errada não falharia: devolveria número plausível.

### 5.2 "Sem consulta nova" obriga a **fundir laços**, não a escrever geradores ao lado

Os gates de `sinais()` são por espécie (`alcancadas[UX_00x]`), e cada espécie hoje é um gerador
próprio. Escrever as espécies novas como geradores paralelos **acrescentaria consulta**, ainda que
elas leiam "o mesmo dado":

| Espécie nova | Se gerador próprio | Se fundida ao laço existente |
|---|---|---|
| `UX-063` | +1 `resumo_da_etapa` **por Etapa** | 0 — mesma chamada do `UX-003` |
| `UX-064` | +1 `recursos_do_edital` + `impedidos_por_recurso` **por Edital** | 0 — mesmo cálculo do `UX-005` |
| `UX-065` | +2 **por recorte** (`ato_vigente` e `apuracao_vigente`) | +1 por recorte — só `apuracao_vigente` |

A `T005` já manda fundir o do recurso, "num ato só". A medição mostra que **as três** têm a mesma
forma: uma leitura, dois desfechos. O `UX-065` é a única que acrescenta consulta, e acrescenta
**uma por recorte** — exatamente o que o `R-5` mediu, e só se partilhar o `ato_vigente` que o
`UX-004` já lê.

---

## 6. Ambiente

- `make preparar`: **33 de 33 tabelas append-only** — o portão 2 está aberto, e a worktree não está
  atrás da `main`. Esta feature **não tem migration**, e o total deve continuar 33 no fim.
- Banco próprio da worktree, para não disputar com suíte paralela.
