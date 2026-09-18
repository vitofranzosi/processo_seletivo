# Research — 033 · Navegação por capacidade

Fase 0, **refeita em 18/09/2026 por medição**. A primeira versão foi escrita lendo definições de
função, e errou a superfície duas vezes seguidas — cada correção partindo da leitura seguinte da
mesma prosa. Esta parte de uma varredura por AST de `processo_seletivo/interface/views.py`.

**O método importa e fica registrado:** o que está abaixo foi contado, não estimado. Onde algo não
foi medido, está dito que não foi.

---

## R-1 · A superfície, medida

| Medida | Valor |
|---|---|
| `raise Http404` em `interface/views.py` | **75** |
| Funções distintas que os contêm | **59** |
| Dessas, que recebem `request` | **53** |
| Dessas, que consultam ator, escopo ou vínculo no corpo | **32** |
| Helpers no padrão `_x_para_y` que **autorizam** | **6** |

**As seis portas**, e não quatro:

`_edital_para_classificar` · `_edital_para_publicar` · `_etapa_para_auditar` ·
`_etapa_para_distribuir` · `_peca_para_julgar` · `_processo_para_gerir`

`_ato_para_publicar` **não** é porta: recebe `edital`, `marco_id` e `ato_id`, sem `request` e sem
ator, e busca o ato dentro de um Edital já autorizado. O 404 dela é objeto inexistente.

**E 26 funções autorizativas ficam fora dos seis helpers** — são views que consultam ator ou escopo e
levantam 404 elas mesmas. Não foram classificadas uma a uma; é o que o inventário faz.

---

## R-2 · As quatro portas erradas fazem todas a mesma pergunta

Esta é a descoberta que a leitura de prosa não dava. Classificando as seis:

| Porta | Escopo | O que ela pergunta | Recusa hoje | Veredito |
|---|---|---|---|---|
| `_edital_para_publicar` | 404 ✅ | uma capacidade nomeada | **403** ✅ | ✅ correta |
| `_peca_para_julgar` | 404 ✅ | uma capacidade nomeada, via `require_permission` | **403** ✅ | ✅ correta |
| `_edital_para_classificar` | 404 ✅ | base composta **ou** `auditoria:consultar` | **404** ❌ | ❌ |
| `_etapa_para_auditar` | 404 ✅ | base composta **ou** `auditoria:consultar` | **404** ❌ | ❌ |
| `_processo_para_gerir` | 404 ✅ | base composta | **404** ❌ | ❌ |
| `_etapa_para_distribuir` | **na mesma condição da base** ❌ | base composta | **404** ❌ | ❌ e estruturalmente travada |

**Duas já estão certas, e a diferença entre elas e as outras quatro não é cuidado — é o tipo de
pergunta.** As duas certas perguntam por **uma capacidade nomeada**, que é exatamente o que
`require_permission` sabe recusar. As quatro erradas perguntam por um **predicado composto**:

| Porta | O que ela pergunta |
|---|---|
| `_processo_para_gerir`, `_etapa_para_distribuir` | `comissao:gerir` **ou** presidência daquele Processo |
| `_edital_para_classificar`, `_etapa_para_auditar` | a base acima **ou** `auditoria:consultar` |

Nenhuma delas erra no escopo — todas filtram o Edital por `institution_scope` na própria consulta.

O achado deixa de ser *"duas portas discordam"* e passa a ser: **a camada de segurança sabe recusar
uma capacidade nomeada, e não sabe recusar uma base composta** — então toda porta que pergunta por
uma base improvisou. Elas improvisaram igual porque o buraco é o mesmo.

**E há uma peça pronta para o conserto.** `pode_gerir_comissao` devolve um objeto `Base` que
**nomeia** qual das duas autorizou. O que falta é o espelho: nomear o que faltou quando devolve
`None`.

---

## R-3 · A taxonomia já está implementada — para **um tipo de pergunta**

**Descoberta.** Não é só docstring. `seguranca/application/authorization.py::require_permission`
**implementa** a regra:

```python
if not actor.can(permission):
    raise DomainError("forbidden", "A operação não é permitida.", 403)
if institution_scope is not None and actor.institution_scope != institution_scope:
    raise DomainError("not_found", "Recurso não encontrado.", 404)
```

`_peca_para_julgar` a consome. `_edital_para_publicar` reescreve a mesma coisa à mão.

**Note a assinatura: `require_permission(actor, permission, *, institution_scope)`.** Ela recebe
**uma** permissão. Não há como expressar "esta **ou** aquela", que é o que quatro portas perguntam —
e é por isso que as quatro improvisaram, e improvisaram igual.

**O que falta, portanto, não é "o eixo do vínculo": é recusa nomeada para base composta.** Um ator
sem `comissao:gerir` e sem presidência não falhou num eixo — falhou em **duas** alternativas, e a
recusa honesta nomeia as duas.

**Decisão.** O ponto único vive ao lado de `require_permission`, na camada de segurança — e não em
`interface`. Espalhá-lo pelas portas reproduziria exatamente a divergência que esta feature existe
para fechar.

---

## R-4 · A regra que eu tinha escrito no contrato estava mal formulada

A primeira versão do contrato dizia que **escopo é avaliado antes de capacidade e vínculo**, e que
inverter vazaria a existência de Editais de outras unidades. Ela chegou até o `data-model.md`, que foi
o último artefato a ser corrigido.

**A medição desmente.** `_edital_para_publicar` avalia **capacidade primeiro** — 403 antes de
qualquer consulta ao banco — e **não vaza**: quem não tem a capacidade recebe 403 para tudo, e nunca
aprende se o Edital existe. `require_permission` faz o mesmo.

**O que protege não é a ordem. É o filtro.** Todas as seis portas buscam o Edital com
`institution_scope=ator.institution_scope` na própria consulta, de modo que objeto fora de escopo é
**indistinguível** de objeto inexistente — os dois caem no mesmo `is None`. Essa é a invariante real,
e ela já é uniforme.

**A ordem que vaza** é outra: buscar o objeto **sem** filtrar por escopo e decidir depois. Nenhuma
porta faz isso hoje, e é isso que o contrato tem de proibir.

---

## R-5 · `_etapa_para_distribuir` está travada, e é a porta do `ACH-35`

**Duas descobertas em uma.**

A primeira: a evidência `[UI]` do `ACH-35` é a tela de **distribuição**, e `views.py:4241` mostra que
ela passa por `_etapa_para_distribuir` — **não** por `_edital_para_classificar`, que é onde a versão
anterior destes artefatos mandava mexer. Reescrever a porta errada deixaria o achado aberto e os
testes alterados vermelhos.

A segunda: aquela porta não admite a correção direta.

```python
if edital is None or pode_gerir_comissao(ator, edital.processo) is None:
    raise Http404
```

Escopo-ou-inexistente e falta de vínculo compartilham **um `if`**. Trocar o 404 por 403 ali
responderia 403 também para Edital de outra unidade, que é vazamento. **A separação das duas
condições é trabalho próprio, e vem antes da mudança de gramática.**

---

## R-6 · O padrão de derivar navegação também já existe, aplicado uma vez

`_pode_auditar_a_etapa` tem no docstring exatamente o que a `FR-473` pede, generalizado:

> *"Separada de `_etapa_para_auditar` porque a tela do recurso precisa **oferecer ou não** o caminho
> antes de alguém batê-lo: link para porta fechada responde 404, e **404 não explica nada a quem o
> recebe**."*

É o predicado extraído da porta para que a **tela** possa consultá-lo antes de oferecer o caminho.
Uma tela faz isso. A tela do Edital não.

**Decisão.** `_marcos_publicados` passa a derivar por destino consultando o predicado de cada um —
o mesmo desenho, aplicado onde ele faltava. E `FR-476` ganha um antecedente real no código, em vez de
ser princípio sem precedente.

---

## R-7 · A recusa explicada já é página, e alcança toda a gestão

`interface/erros.py::RecusaDoDominioMiddleware` intercepta `DomainError` e a renderiza com o status
que o domínio declarou, escolhendo o template pelo prefixo: `/gestao/` → `interface/recusa.html`,
`/selecoes/` → `portal/recusa.html`. O título de 403 já é *"Você não tem permissão para isto"*, e o
template fecha com *"Nenhuma alteração foi feita"*.

**Nada a construir.** O que a feature escreve é o `detail` — hoje *"A operação não é permitida."*,
correto e mudo.

---

## R-8 · O canal do candidato não entra

`tests/authorization/test_publicacao_de_resultado.py` registra, em
`test_uma_candidata_nao_alcanca_a_situacao_de_outra`: *"A recusa é **404 uniforme**: quem tenta não
descobre pela resposta se a inscrição não existe ou se existe e é de outra pessoa."*

Doutrinas diferentes de propósito, e as duas certas. No canal institucional o ator já sabe que o
Edital existe; no canal do candidato, distinguir seria oráculo de enumeração.

---

## R-9 · A feature altera testes que passam hoje

`tests/authorization/` tem **197 casos** em 38 arquivos, e afirma as duas doutrinas.
`test_distribuicao.py` prende `404` para vínculo — inclusive num caso cujo **nome** é
`test_quem_nao_tem_vinculo_nenhum_recebe_inexistente`.

**A contenção é `SC-168`**, e é aritmética: pode mudar **o status da recusa**, nunca **quem passa**.
Um caso que passe a esperar sucesso onde esperava recusa derruba a feature, não o teste.

---

## R-10 · O que ainda não foi medido, e é tarefa

As **26 funções autorizativas fora dos seis helpers** não foram classificadas. Algumas quase
certamente respondem por objeto inexistente; outras podem ser recusa por base de autorização, e aí são superfície
desta feature.

**Isto não é estimado aqui de novo.** Três tentativas de adivinhar essa repartição já erraram — por
ler definições de função, por varrer faixas de linha e por confundir busca de objeto com porta. O
inventário conta; a parada de escopo decide o que fazer com o que ele encontrar.
