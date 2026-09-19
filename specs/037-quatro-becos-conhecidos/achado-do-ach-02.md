# O desfecho do `ACH-02`, decidido por percurso

**Quando**: 19/09/2026. **Onde**: `http://localhost:8037`, banco `ps_037_percurso`, entrada
`becos-037` do `.claude/launch.json`. **Tudo pela interface** — nenhum passo por shell, banco ou
relógio.

Este documento é o que a `SC-195` exige: **desfecho escrito, qualquer que ele seja**. A `FR-542b`
mandou percorrer **antes** de escrever qualquer condução, porque a auditoria inferiu papel ausente
da ausência de controle — e o controle existe. Escrever frase para problema que não existe é pior
do que não escrever.

---

## O percurso

**Identidade**: `ana.gestora`, papel **Gestor** — a mesma da reauditoria de 16/09/2026. O seletor
mostra, na própria tela, o que o papel concede:

> Gestor — `inscricao:consultar`, `processo:criar`, `processo:ativar`, `processo:encerrar`,
> `processo:cancelar`, `edital:criar`, `edital:encerrar`, `edital:cancelar`,
> `retificacao:cancelar`, `comissao:gerir`

**Passos**, todos pela tela: criar o Processo `PS 37/2026` com o primeiro Edital `37/2026` → abrir o
Edital → abrir a validação.

---

## O que a tela do Edital mostrou

```
Validação do conteúdo
IMPEDE  Ao menos um Perfil é obrigatório.
IMPEDE  Ao menos um Evento é obrigatório.
AVISO   Nenhum Evento do Cronograma está marcado como período de inscrições. …
```

E o cartão *"O que fazer agora"* ofereceu **duas** ações: `Visualizar Edital` e `Cancelar`. Lidos os
links da página inteira, não há caminho algum até os Perfis, e **não há `Elaborar o Edital`** —
porque o Gestor não detém `edital:elaborar`.

## O que as telas de composição mostraram

Na etapa **Revisão**, que é a que enumera tudo o que falta:

```
Somente leitura. Você não tem a permissão edital:elaborar.

O que falta para submeter
IMPEDE  Ao menos um Perfil é obrigatório.   [Ir para Perfis de Vaga]
IMPEDE  Ao menos um Evento é obrigatório.   [Ir para Cronograma]
```

E, seguindo o caminho até a etapa **Perfis de Vaga**:

```
Somente leitura. Você não tem a permissão edital:elaborar.

Perfis de Vaga
IMPEDE  Ao menos um Perfil é obrigatório.
…
0 Perfis
```

Não há controle de acrescentar Perfil. A etapa abre, e é de leitura.

---

## O desfecho: **saída (a)** — uma permissão impede, e a `T015` é executada

**Há o que fechar.** O Gestor não consegue criar o Perfil, e o que o impede é uma permissão nomeada:
`edital:elaborar`. A alternativa (b) — *"nada o impede, e o caminho até os Perfis já está na tela"* —
**não se confirmou**: o caminho está, e o que ele alcança é uma tela de leitura.

**Mas a auditoria estava certa pela metade, e a medição corrigiu as duas metades.**

| O que o `ACH-02` afirmava | O que o percurso mediu |
|---|---|
| *"não há indicação de que falta papel"* | **há**: a faixa de somente leitura nomeia `edital:elaborar` |
| *"o gestor não sabe o que falta"* | **sabe**: a pendência diz, e leva à etapa — fechado por feature anterior |
| *"o gestor não sabe a quem pedir"* | **confirmado**: nenhuma das duas telas o diz |

**O que sobra para a `FR-542`, então, é exatamente uma coisa**: *a quem pedir*. E ela é a metade
que a `R-5` já havia isolado no código.

### Duas observações que o percurso produziu e que não são escopo

**1. A faixa nomeia o codename, e não a permissão.** *"Você não tem a permissão `edital:elaborar`"*
mostra a quem lê um identificador de máquina. O produto tem uma forma de dizer isso — *"a permissão
de elaborar o Edital"* —, e a faixa não a usa. Corrigi-la é mexer numa frase que não é a desta
feature e que aparece nas nove etapas; **fica registrado como achado, e não vira escopo**
(`ACH-31`/`ACH-45` são da mesma família, e têm spec própria na `13.4`).

**2. A tela do Edital exibe a pendência sem caminho nenhum.** O `_pendencias.html` só imprime o
*"Ir para …"* quando quem o inclui pede (`com_link`), e a tela do Edital não pede. É ali que o
Gestor chega primeiro, e é dali que ele não sai. **Também não é escopo**: a `FR-542a` fala da
condução, e mudar quais telas oferecem caminho é decisão de navegação, com a garantia da `033` a
respeitar. Fica registrado.

---

## O que a `T015` entrega, em consequência

A condução nasce **onde a tela exibe o achado** (`FR-542a`, `D-002`), e não na mensagem normativa —
que descreve o defeito do conteúdo, é lida por mais de uma superfície e não conhece quem está
olhando. Ela é produzida pelo mecanismo único (`FR-543`), na forma cheia (`FR-543a`), nomeia **a
permissão** e nunca uma pessoa (`FR-543b`), e **cala para quem pode resolver** (`FR-544`).

E o que a tela já diz — o que falta, e o caminho até a etapa — **permanece intocado**.
