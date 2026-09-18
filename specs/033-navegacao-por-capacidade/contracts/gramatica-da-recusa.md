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

## As três origens, e o que cada uma responde

```
1. escopo institucional alheio ──► 404   (inalterado — é proteção de dados)
2. objeto inexistente          ──► 404   (inalterado — é a resposta verdadeira)
3. falta de capacidade          ─┐
4. falta de vínculo de comissão ─┴► 403 com recusa explicada   (o que muda)
```

**A ordem de avaliação é normativa.** O escopo é verificado **antes** de capacidade e vínculo.
Inverter a ordem faria a recusa de escopo virar 403 e vazar a existência de Editais de outras
unidades — e nenhum teste de status pegaria isso, porque o status estaria "certo".

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

### O motivo, nas duas formas

| O que falta | Como se escreve |
|---|---|
| capacidade de papel | nomeia a capacidade — por exemplo, a de publicar resultado — e diz que ela é concedida por papel |
| vínculo de comissão | nomeia o vínculo — a presidência **deste** Processo —, e **não** nomeia um papel, porque nenhum papel concede presidência |

**A distinção não é estilo.** Dizer "peça o papel de X" a quem precisa de **vínculo** manda a pessoa
pedir o que não resolve. É o defeito que `FR-485` fecha.

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
