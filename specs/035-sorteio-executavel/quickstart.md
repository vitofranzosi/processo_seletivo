# Quickstart — validação da `035` · Sorteio executável

Cinco cenários. **Os quatro primeiros são pela interface administrativa, sem shell e sem banco** — é
o que o Princípio VI cobra, e é o que pegou, na `032` e na `033`, defeitos que teste nenhum pegou.

## Preparação

```bash
cd backend && uv sync --extra dev && make preparar
```

Confira que a saída termina em `N de M` com **N diferente de zero**. O `runserver` precisa de
`INTERFACE_SELETOR_IDENTIDADE=true`, ou `/gestao/` devolve 503.

**O Edital do cenário**: um Perfil, um marco que **ordena por sorteio**, e o método declarado por
inteiro. A fonte é a **de demonstração** — ela devolve material para qualquer referência, e é o que
permite rodar o sorteio sem rede.

---

## Cenário 1 — a composição ensina, em vez de recusar (`FR-507`, `FR-508`, `FR-509`)

1. Abra a etapa de Classificação e componha o método do marco de sorteio.

**Esperado**: o **algoritmo** e a **fonte** são **escolhidos** entre os que o sistema executa — não
há o que digitar errado. É o que a tela de Retificação já fazia com o algoritmo.

2. Chegue ao campo da **ocorrência**.

**Esperado**: a tela diz **a forma, um exemplo e a consequência** — que a substituição deriva do
número da ocorrência —, e diz que ali vai **só a referência**, porque a fonte já está declarada
acima. A formulação segue a do campo do instante, três linhas abaixo.

3. Confira o campo *"como a ocorrência decorre da data programada"*.

**Esperado**: **continua texto livre**. É a frase que diz a norma em português, e é assim que um
Edital se escreve. Se ele tiver virado código, a `FR-510` foi violada — e é o requisito mais fácil
de perder de vista, porque ele manda **não fazer** o que a auditoria parecia pedir.

---

## Cenário 2 — a sexta guarda recusa, e diz o quê (`FR-512`, `FR-513`)

1. Escreva a ocorrência como uma pessoa escreve: **`concurso 6100 da Loteria Federal`**. Grave.

**Esperado**: recusado, **no mesmo momento** em que um algoritmo fora do vocabulário já é recusado
hoje. A frase nomeia o campo, a forma e **por quê**.

2. Faça o mesmo no **método comum do Edital**, no alto da etapa.

**Esperado**: a mesma recusa. A conferência não distingue o método próprio do comum.

3. Corrija para **`6100`** e grave.

**Esperado**: aceito.

### Contraprova — o marco que não sorteia

Num marco **computado**, ou num Edital sem método algum, gravar **não** dispara nada desta família.

---

## Cenário 3 — o sorteio roda, de ponta a ponta (`SC-176`)

Este é o critério que decide se a feature entra. É o cenário 3 da reauditoria, que parou aqui.

1. Publique o Edital, receba inscrições, congele o universo.
2. **Observe a ocorrência**, pelo caminho que a tela oferece.
3. Execute o sorteio.

**Esperado**: a tela **oferece** observar a ocorrência — hoje ela não oferece —, a semente é fixada,
a ordem sorteada é constituída, o manifesto sai com o método publicado, e a **verificação pública**
confere.

**Nenhum passo pode exigir shell, banco ou endereço digitado.** E o percurso tem de ser possível
**sem saber de antemão** que a ocorrência precisa terminar em número — quem compõe aprende isso na
tela, no cenário 1.

---

## Cenário 4 — a recusa do acervo para de culpar a fonte (`FR-516`, `FR-517`, `FR-518`)

Para este é preciso um Edital **já publicado** com a ocorrência em prosa — o caso de quem publicou
antes da guarda existir.

1. Abra a tela do sorteio dele.

**Esperado**: a frase nomeia **a declaração** como causa, diz **qual campo** e **o que ele precisa
conter**, e só então que corrigir exige Retificação. Onde antes se lia que a ocorrência e todas as
substitutas estavam indisponíveis — o que era falso, e culpava quem não errou.

2. **Contraprova**: num Edital com ocorrência derivável, torne a fonte indisponível o bastante para
   esgotar a cadeia.

**Esperado**: a frase **de hoje**, inalterada. A causa é outra, e para ela a frase está certa.

---

## Cenário 5 — o acervo não se mexeu (`FR-519`, `SC-179`)

Este precisa do banco, e é o único que precisa.

**A metade "antes" não se faz aqui**: ela é gravada antes da primeira edição de código. Chegando a
este ponto com a implementação pronta, não existe mais "antes" que se possa exportar.

1. O retrato do acervo **já está gravado**: por publicação, o resumo do conteúdo canônico, o do
   documento e o censo dos degraus de elevação. **E os sorteios já realizados**: semente, ordem e
   manifesto.
2. Exporte agora e compare.

**Esperado**: idênticos. **Nenhum sorteio já realizado muda de resultado** — é a garantia mais dura
desta feature, porque ordem sorteada publicada é ato, e um resultado que muda depois de publicado
não se corrige, se Retifica.

---

## Verificação

```bash
cd backend && make lint check test-pg
```

`test-pg` e **nunca** `test`. `lint` são **dois** passos. **Não edite arquivos do projeto enquanto a
suíte roda.**

### As três fixtures que quebram, e por que não se conserta a regra

`research.md` `R-6` nomeia as três, todas num arquivo, todas na forma `concurso 6100 da Loteria
Federal`. **Corrija as fixtures, e não a regra.** Afrouxar a derivação para procurar o número em
qualquer posição criaria ambiguidade onde há mais de um: `concurso 6100 de 2026` derivaria para 2027.
