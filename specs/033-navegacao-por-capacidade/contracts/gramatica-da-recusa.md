# Contrato — a gramática da recusa na gestão

A recusa é **superfície de segurança**. Este contrato fixa o que cada origem de negativa responde, e
o que esta feature promete não mexer.

## A regra que governa tudo abaixo

**Só o status e o texto mudam. Quem entra não muda.** Toda linha deste contrato descreve como uma
recusa **se apresenta**. Nenhuma delas altera o conjunto de atores que atravessa uma porta. O
critério que prende isso é `SC-168`, e ele é aritmético.

**Este contrato vale para `/gestao/`.** O canal do candidato mantém o **404 uniforme**, de propósito:
lá, distinguir "não existe" de "é de outra pessoa" seria oráculo de enumeração.

---

## As quatro origens, e o que cada uma responde

```
1. escopo institucional alheio     ──► 404   (inalterado — é proteção de dados)
2. objeto inexistente              ──► 404   (inalterado — é a resposta verdadeira)
3. falta de capacidade nomeada     ──► 403 com recusa explicada   (já é assim em 2 das 6 portas)
4. falta de base de autorização    ──► 403 com recusa explicada   (o que muda, nas 4 restantes)
```

**A quarta é composta, e é a que não tinha tratamento.** Uma base é "esta capacidade **ou** aquele
vínculo", cada um suficiente sozinho. `require_permission` recebe **uma** permissão e não sabe
expressar a alternativa — e é por isso que as quatro portas que perguntam por uma base improvisaram,
e improvisaram igual.

**O que protege não é a ordem de avaliação — é o filtro.** Uma versão anterior deste contrato
mandava avaliar escopo **antes** de capacidade e base. A medição desmentiu: a porta da divulgação
avalia **capacidade primeiro**, devolve 403 sem tocar no banco, e **não vaza** — quem não tem a
capacidade recebe 403 para tudo e nunca aprende se o objeto existe.

A invariante real é outra, e já é uniforme nas seis portas: **a consulta que busca o objeto filtra
por escopo institucional**, de modo que objeto de outra unidade e objeto inexistente caiam no mesmo
`is None` e sejam **indistinguíveis**.

**A ordem que vaza** é buscar o objeto **sem** filtrar por escopo e decidir depois. Nenhuma porta faz
isso hoje, e é isso que este contrato proíbe.

**E há uma porta travada.** A da distribuição decide escopo-ou-inexistente e falta de base na
**mesma condição**:

```python
if edital is None or pode_gerir_comissao(ator, edital.processo) is None:
    raise Http404
```

Trocar o status ali, sem separar as duas condições antes, responderia recusa explicada também para
Edital de outra unidade. **Separar vem primeiro; mudar a gramática vem depois.**

---

## A recusa explicada — a forma

```
título:    Você não tem permissão para isto
motivo:    <o que falta, nomeado>
a quem:    <quem resolve aquele caso>
garantia:  Nenhuma alteração foi feita
```

O título e a garantia já existem e não mudam. O que esta feature escreve é o **motivo** e o **a
quem**.

### O motivo, e a regra que o governa

| O que a tela aceita | Como a recusa se escreve |
|---|---|
| **uma capacidade nomeada** | nomeia a capacidade — por exemplo, a de publicar resultado |
| **mais de uma base**, cada uma suficiente | nomeia **todas** as que teriam servido **naquela chamada** — por exemplo, a permissão de gerir a comissão **e** a presidência deste Processo |
| **só o vínculo** | nomeia a presidência, e **não** inventa um papel que a conceda, porque nenhum concede |

**O conjunto de bases é de quem chama, não da porta.** A porta do marco tem dois modos: em boa parte
das chamadas a capacidade de auditoria **não** serve, e nas demais serve. Uma recusa que assuma
conjunto fixo mente em metade dos casos (`FR-489`).

**A distinção não é estilo.** Dizer "peça o papel de X" a quem precisa de outra coisa manda a pessoa
pedir o que não resolve; nomear só uma das bases manda pedir metade. É o que `FR-485` e `FR-479`
fecham, cada uma do seu lado.

### A fonte

O "o que falta" sai da **mesma leitura** que a porta já fez para decidir. Reescrever a frase a partir
de uma segunda leitura criaria duas verdades sobre a mesma recusa.

---

## O que este contrato **não** toca

| | Por quê |
|---|---|
| O 404 de escopo institucional | é proteção de dados, e `FR-480` o preserva literalmente |
| O 404 uniforme do portal do candidato | doutrina diferente, canal diferente, e a suíte de autorização a registra por escrito |
| O 404 de objeto inexistente | é verdade, não recusa |
| A verificação no servidor | `FR-482` — esconder um link nunca substitui a recusa; quem montar a URL recebe a mesma resposta |
| Quem atravessa cada porta | `FR-483` e `SC-168` |

---

## O que muda na suíte de autorização, e por quê

Esta feature **altera testes que passam hoje**, e isso precisa estar escrito num contrato, não
descoberto num diff.

`tests/authorization/` tem **197 casos**. A mudança permitida é de um tipo só:

| Permitido | Proibido |
|---|---|
| trocar `404` por `403` num caso de recusa | mudar a asserção de **quem** entra |
| renomear um caso cujo nome descreve a resposta antiga | remover um caso |
| acrescentar caso novo | afrouxar uma asserção existente |

**Um caso muda de nome de propósito:** `test_quem_nao_tem_vinculo_nenhum_recebe_inexistente`, em
`test_distribuicao.py`, afirma no próprio nome a doutrina que esta feature corrige. Renomeá-lo
mantendo intacta a asserção de que aquele ator **não entra** é o registro de que a mudança foi de
gramática.

**Um caso que passe a esperar sucesso onde esperava recusa derruba a feature, não o teste.**
