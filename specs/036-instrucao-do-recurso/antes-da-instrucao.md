# O "antes" da `036` — a medição gravada antes da primeira edição

**Quando**: 2026-09-19, na worktree `spec-036-implementacao-f8f3cb`, contra a `main` `2beb2d9` —
que já traz a `034`, a `035` e os artefatos desta feature.

**Por que este arquivo existe**: a `034` previu **oito** casos de teste alterados e entregou
**doze**. Sem o "antes" escrito, a diferença não teria contra o que ser comparada, e a recontagem
da `T028` não teria régua. Aqui ficam a contagem da suíte, o que afirma **hoje** o único caso que a
`research.md` prevê alterar, e os dois vizinhos que precisam permanecer.

---

## 1. A contagem da suíte, antes de qualquer edição

```bash
cd backend && make test-pg
```

| | Medido |
|---|---|
| passando | **7343** |
| pulados | **11** |
| falhando | **0** |
| tempo | 689,93 s (11min29) |

O briefing desta implementação dava **7343 passando e 11 pulados** como o "antes" desta `main`.
**Confere exatamente** — `7343 passed, 11 skipped`. A régua da `T028` e da `T030` é esta, e não
uma aproximação.

## 2. A preparação do banco, e o número que o portão vigia

```bash
cd backend && make preparar
```

Saída da terceira passada:

> `Papéis provisionados. 32 de 32 tabelas append-only estão sem UPDATE nem DELETE para o runtime.`

**O total já é 32, e não 31.** O `tasks.md` e o `CLAUDE.md` dizem 31 porque foram escritos contra
uma `main` anterior; `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py` tem
hoje **32** entradas. O portão da `T006` continua valendo com o mesmo sentido — o total **sobe uma**
depois da migration —, só que a leitura correta é **32 → 33**, e o que importa continua sendo o
primeiro número não vir zero.

## 3. O único caso que a `research.md` `R-6` prevê alterar

`backend/tests/interface/test_proveniencia_do_recurso.py::test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta`

O que ele afirma **hoje**, citado por inteiro:

```python
def test_quem_so_julga_alcanca_o_edital_e_le_o_que_lhe_falta(client, seletor_ligado, julgado):
    """`recurso:julgar` não concede leitura de Etapa nem de inscrição, e a tela diz isso."""
    identificar(client, JULGADORA, ["julgador"])
    corpo = client.get(reverse("interface:recurso", args=[julgado["peca"].id])).content.decode()
    edital = julgado["inscricao"].edital

    assert reverse("interface:detalhe", args=[edital.id]) in links_de(corpo)
    assert reverse("interface:inscricao-recebida", args=[julgado["inscricao"].id]) not in corpo
    assert "Julgar não as concede." in corpo
```

Três asserções, e **o que muda é uma**: a tela passa a dizer, além de *"Julgar não as concede"*,
que a prova chega por **ato de instrução** e a quem pedi-la. As outras duas permanecem exatamente
como estão — o julgador continua alcançando o Edital e continua **não** alcançando a tela de
documentos da inscrição, porque nada nesta feature amplia `recurso:julgar`.

> A peça do `julgado` está **decidida** e **sem instrução** alguma: é o terceiro estado da
> `FR-532`? Não — é o primeiro. Sem ato praticado, não há instrução a declarar, e a decisão não
> inventa uma. Esta distinção é o que a `T028` precisa conferir caso a caso.

## 4. Os dois vizinhos que permanecem — e são contraprova

| Caso | O que afirma hoje | Depois da `036` |
|---|---|---|
| `test_quem_audita_alcanca_o_resultado_e_a_avaliacao` | com `auditoria:consultar`, os links do resultado e da trilha filtrada aparecem, abrem com 200, e *"Julgar não as concede."* **não** aparece | permanece |
| `test_quem_consulta_inscricoes_alcanca_os_documentos` | com `inscricao:consultar`, o link dos documentos aparece e abre com 200 | permanece |

Se algum dos dois mudar, a feature ampliou o que não devia: são eles que respondem por `SC-187` do
lado de quem já alcançava.

## 5. O orçamento de consulta, e o número exato de hoje

`test_a_tela_do_recurso_nao_faz_uma_consulta_por_ato` prende **oito** consultas para quem só julga,
e o comentário do caso enumera as oito. A oitava — a presidência do Processo — só acontece para
quem **não** tem `comissao:gerir`, que é o caso da julgadora.

O que esta feature promete a esse orçamento: **não mexer nele**. O parecer já está carregado
(`R-3`), e a existência de instrução entra por subconsulta `EXISTS` na própria leitura da peça, que
não é consulta a mais. A leitura das linhas do ato acontece **só quando há ato**, e a peça deste
caso não tem nenhum.

---

## 6. As três premissas reconferidas contra o código (`T003`)

*"Confirme, não assuma"* — a `035` provou que vale. As três estão na `research.md`; abaixo está
onde cada uma foi conferida **nesta worktree**, hoje.

### 6.1 O parecer **já está carregado** na porta da peça (`R-3`) — confirmado

`backend/processo_seletivo/interface/views.py`, em `_peca_para_julgar`:

```python
.select_related(
    "inscricao",
    "inscricao__edital",
    "inscricao__edital__processo",
    "versao",
    "resultado_atacado",
    "resultado_atacado__avaliacao",
    ...
)
```

`resultado_atacado__avaliacao` está lá, e `Avaliacao.parecer` é campo de texto da linha
(`backend/processo_seletivo/avaliacoes/models.py`). **O que falta à tela de quem só julga não é
consulta: é autorização.** A mesma função também já traz `inscricao__edital__processo`, com o
comentário dizendo por quê — *"a tela pergunta pela presidência dele para decidir quais caminhos
oferecer"*. A tela **já sabe** quem preside.

`backend/processo_seletivo/recursos/application/porta.py::travar` carrega a mesma tripla, o que
significa que o **ato** de instrução também encontra o parecer sem consulta nova.

### 6.2 A auditoria **já registra leitura** — confirmado, e há **dois** precedentes

A `research.md` `R-2` nomeia um. A varredura encontrou **dois**, e o segundo é mais antigo:

| Precedente | Onde | Forma |
|---|---|---|
| a prévia da exportação de matrículas (`031`) | `interface/views.py`, operação `MATRICULA_PREVER` | `new_revision=None`, `new_state=edital.status`, razão descrevendo **população e quantidade** |
| a consulta a documento do candidato (`009`) | `interface/views.py::_registrar_consulta`, operação `CONSULTAR_DOCUMENTO` | agregado é a Inscrição, razão descrevendo **qual requisito** foi aberto |

O segundo é o mais próximo do que esta feature faz, e diz por escrito a regra que ela precisa
respeitar: *"Registra a leitura, e não o conteúdo — nem o nome do arquivo, que é do candidato."*

**Consequência**: a `FR-534` não é mecanismo novo, e não há uma segunda forma a inventar. As duas já
existentes concordam entre si: **escopo, nunca conteúdo**.

### 6.3 O acompanhamento **já exibe o motivo** (`R-4`) — confirmado

`backend/processo_seletivo/portal/templates/portal/acompanhamento.html`:

```html
{% if etapa.motivo %}<p class="meta">{{ etapa.motivo }}</p>{% endif %}
```

com o comentário imediatamente acima: *"O motivo é escrito para ser lido — 'pontuação inferior à
nota mínima da Etapa (45,0000 < 60,0000)' —, e é obrigatório por constraint desde a 013."*

E a frase do `R-5` está onde a `research.md` disse, na linha 60 do mesmo arquivo: *"Nada aqui é de
terceiro: nenhum nome, nenhuma nota alheia, nenhum parecer, nenhuma avaliação."* O sujeito dela é
**de terceiro** — e é isso que ela proíbe.

---

## 7. O que a varredura encontrou **além** da `research.md`

Duas medições que a `research.md` não tem, e a segunda muda como a `FR-523` se implementa.

### 7.1 O total append-only já era 32

Está na seção 2. É correção de número, não de doutrina.

### 7.2 Avaliação que fundamenta Resultado **não pode ser reaberta** — a `013` fechou essa porta

`backend/processo_seletivo/avaliacoes/application/avaliacao.py::_recusar_se_fundamenta_resultado`
recusa a reabertura quando existe `ResultadoEtapa` apontando para aquela Avaliação, e a mensagem
manda ao caminho que existe: *"Corrigir um Resultado consolidado é ato de outra natureza: o
julgamento de recurso o supera por um Resultado sucessor."*

As duas únicas escritas em `Avaliacao.parecer` — a gravação do rascunho e a conclusão — recusam
quando a avaliação está `CONCLUIDA`, e voltar a `RASCUNHO` exige `reabrir`. Logo: **o parecer de
uma avaliação que fundamenta um Resultado é imutável pelo canal real.**

**O que isso faz com a `FR-523`**: o caso de borda *"avaliação reaberta depois do resultado"* é,
hoje, inalcançável pela interface — não porque a `036` o resolveu, mas porque a `013` já o havia
fechado. A `FR-523` continua implementada, e lendo a `ConclusaoAvaliacao` preservada, porque é ela a
fonte historicamente correta: *vale o que o ato citou*. O que fica registrado é que a condição que a
dispara não é reproduzível por percurso, e por isso ela é prendida por teste e **não** por cenário
de quickstart.

**Não é escopo desta feature mudar isso**, e a governança do projeto é clara: achado vira registro.
