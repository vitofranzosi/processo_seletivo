# Phase 0 — o que foi medido

**Quando**: 19/09/2026, contra a `main` `6f322e4`. **Método**: leitura da **condição**, não da mensagem
— foi lendo mensagem que a spec errou duas premissas antes de ser escrita.

**Placar**: as quatro medições da spec se confirmam. Das quatro espécies novas, **duas saem sem
consulta**, **uma custa uma leitura por recorte** e **uma custa extração** — e cada custo está medido
onde a espécie é descrita.

---

## R-1 — As duas premissas que eu errei: confirmadas como a spec as corrigiu

**`UX-005` não cobre recurso pendente.** A condição é

```
if not any(not (membros - impedidos.get(peca.id, set())) for peca in pendentes): continue
```

— ela só dispara quando **alguma peça pendente tem todos os membros impedidos**. Recurso pendente
com julgador disponível **não produz sinal**.

**`UX-003` não cobre trabalho parado.** Ele mede cobertura — *quantos avaliadores por Etapa*. Uma
Etapa com cobertura completa e cinquenta avaliações paradas não sinaliza.

---

## R-2 — O catálogo: seis no código, cinco no requisito

`ESPECIES = (UX_001, UX_002, UX_003, UX_004, UX_005, UX_046)`.

A `FR-024` da `022`: *"O sistema MUST apresentar exclusivamente os sinais definidos em `UX-001` a
`UX-005`, e MUST NOT apresentar sinal fora desse catálogo"*.

**Confirmado**: a `027` acrescentou a sexta sem revisá-la. A `FR-565` a substitui.

---

## R-3 — Espécie nova ➊, trabalho de avaliação pendente: **de graça**

`avaliacoes/application/selectors.py::resumo_da_etapa` já devolve, numa **agregação só** — não um
laço sobre inscrições —, `inscricoes`, `completas` (atribuídas ≥ previstas) e `avaliadas`
(concluídas ≥ previstas).

*Distribuído e não concluído* é `completas − avaliadas`. **E o `UX-003` já chama essa função**: o
sinal novo é uma segunda leitura do mesmo retorno, **sem consulta nova**.

---

## R-4 — Espécie nova ➋, recurso com julgador disponível: **é a negação do `UX-005`**

Confirmado estruturalmente. Os dois partem de `recursos_do_edital(edital,
situacao=AGUARDANDO_JULGAMENTO)` e de `impedidos_por_recurso(pendentes)`, ambos já chamados pelo
`UX-005`.

**Os dois MUST nascer do mesmo cálculo**, ou divergem: peça com todos impedidos vira `UX-005`, peça
com alguém livre vira a espécie nova, e **nenhuma peça cai nos dois**. Calculados em lugares
separados, uma mudança na regra de impedimento moveria um e não o outro.

---

## R-5 — Espécie nova ➌, recorte com ordem e sem ocupação: **derivável, e custa uma leitura por recorte**

O predicado é `ato_vigente is not None and apuracao_vigente is None`, e as duas funções são públicas.

**Mas só uma delas já é lida pela Supervisão.** `interface/supervisao.py` importa `ato_vigente` e o
chama para o `UX-004`; de `ocupacao` ela **não importa nada** — `apuracao_vigente` não aparece no
módulo. *A primeira leitura desta seção dizia "de graça" porque conferiu a função errada.*

**Custo medido**: uma leitura por recorte, que é a forma que a `034` adotou para não exigir visita
por lista — e que **o orçamento de consulta precisa acomodar**, com o número remedido e a razão
escrita ao lado (`R-7`).

---

## R-6 — Espécie nova ➍, ato emitido e não publicado: **esta custa, e o custo é conhecido**

**O estado é derivável, mas a derivação não é pública.** `publicacoes/application/selectors.py::
atos_publicados` responde outra pergunta — os atos **do Edital** (abertura e Retificações) —, e não
a divulgação de um ato de ordenação.

A derivação que responde — *nunca divulgado*, *divulgações defasadas* — existe **apenas dentro de
`interface/views.py`**, num ajudante privado. A varredura não a encontra em nenhum outro módulo.

**Consequência, e ela decide o desenho:** a `FR-557` exige que o indicador derive da **mesma
leitura** que governa a tela de destino. Cumpri-la aqui significa **extrair** aquela derivação para
onde os dois a alcancem. Reescrevê-la no sinal seria a segunda verdade que a `FR-557` proíbe.

**E há uma dependência**: `interface/views.py` é um dos três arquivos que a `037` está alterando.
A extração **espera a `037` entrar**. Ver *O que o plano propõe*.

---

## R-7 — O orçamento de consulta já é guardado, e o guarda tem nome

`tests/integration/supervisao/test_sinais.py::test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas`
fixa um orçamento com `django_assert_num_queries`.

**É a guarda que esta feature mais facilmente quebra**, porque leva o mesmo cálculo a uma segunda
tela e acrescenta quatro espécies. Superfície de teste do catálogo e dos sinais, medida:

| Arquivo | Casos |
|---|---|
| `tests/interface/test_supervisao.py` | 15 |
| `tests/integration/supervisao/test_sinais.py` | 13 |
| `tests/integration/supervisao/test_fronteira.py` | 5 |
| `tests/acceptance/test_supervisao_do_processo.py` | 1 |

**34 casos** cercam a Supervisão. Recontar na implementação: a `034` previu oito alterados e
entregou doze.

---

## O que o plano propõe, em consequência

| Espécie | Custo | Quando |
|---|---|---|
| avaliação pendente | segunda leitura de retorno existente | agora |
| recurso com julgador | mesmo cálculo do `UX-005`, partido em dois desfechos | agora |
| recorte sem ocupação | dois seletores públicos que já existem | agora |
| **ato não publicado** | **extrair derivação de `interface/views.py`** | **depois da `037`** |

**Nenhuma das quatro inventa estado** — a `FR-567` está satisfeita. A quarta não é menos derivável:
ela é derivável **no lugar errado**, e arrumá-la é a única parte desta feature que mexe em código
que a `037` está tocando.
