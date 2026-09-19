# Phase 0 — Pesquisa e medição · 035 · Sorteio executável

**Método**: varredura do repositório inteiro e leitura dirigida, em 18/09/2026, contra a `main`
`d30f6d8`; mais leitura de **quatro Editais da amostra real** por extração de texto. Cada afirmação
abaixo tem o arquivo e a linha, ou o Edital e a cláusula, em que foi conferida.

> ## ⚠️ Esta pesquisa contradiz a spec em dois pontos, e os dois mudam a feature
>
> **A `spec.md` precisa ser revista antes do Phase 1.** O que ela descreve como *"três campos de
> texto livre que nada valida"* é, medido, **um** campo. E a família de Editais que ela toma como
> destinatária **não declara ocorrência de fonte externa em nenhum dos quatro que li**.
>
> Nada disso invalida a feature. Torna-a **menor, mais precisa — e faz um dos critérios de sucesso
> medir o que não interessa**.

---

## R-1 — Confirmado, e com folga: o motor existe

| Peça | Estado | Onde |
|---|---|---|
| Material bruto → semente | ✅ regras de vocabulário fechado | `sorteios/domain/normalizacao.py` |
| Ocorrência seguinte da mesma fonte | ✅ `5900` → `5901`, preservando prefixo e número de dígitos, com `LIMITE_DA_CADEIA = 5` | `sorteios/domain/substituicao.py` |
| Fonte externa, real e de demonstração | ✅ dois adaptadores, ligados por vocabulário fechado | `sorteios/infrastructure/fontes/__init__.py` |
| Chave, resumo canônico, manifesto | ✅ com vetores normativos publicados | `sorteios/domain/chave.py`, `manifesto.py` |

**O `ACH-55` não é "falta o mecanismo".** Isto a spec acertou.

---

## R-2 — A spec erra: **cinco dos seis** campos do método já são validados

A spec diz que *"nada valida na composição"*. Medido: `editais/domain/perfis.py` tem **seis**
validadores do método, e eles disparam **ao gravar o rascunho**, não só ao publicar.

| Campo | Vocabulário | Validado hoje? | Validador |
|---|---|---|---|
| `algorithm` | **fechado**, 1 elemento | ✅ | `_validar_algoritmo_publicado` |
| `source` | **fechado**, 2 nomes | ✅ | `_validar_fonte_publicada` |
| `occurrenceAt` | livre, exige fuso | ✅ | `_validar_instante_da_ocorrencia` |
| `normalization.rule` | **fechado** | ✅ | `_validar_regra_publicada` |
| `substitutionRule.rule` | **fechado** | ✅ | `_validar_substituicao_publicada` |
| **`occurrence`** | **livre, mas tem de terminar em número** | ❌ **nada** | — |

`occurrence` aparece em `perfis.py` **uma única vez**: na tabela de rótulos, como *"a ocorrência
concreta que fixará a semente"*. O domínio já a chama de **concreta**, e o formulário não diz isso.

**A assimetria é o achado.** Cinco campos do método têm guarda; o sexto — o único que impede o
sorteio de rodar quando mal declarado — não tem nenhum.

### E a escolha já existe, na tela ao lado

`interface/retificacao.py` oferece o algoritmo como **escolha entre os publicados**, construindo as
opções a partir do próprio vocabulário fechado. **A Retificação já faz o que a composição não faz.**

Isto reforça a `FR-507` e muda o argumento dela: não é "criar uma escolha", é **generalizar a que já
existe** — o mesmo tipo de argumento que a `FR-509` faz sobre a ajuda do instante da ocorrência.

---

## R-3 — Confirmado, e é o que sustenta a `FR-510`: a derivação em prosa não é lida por ninguém

Varredura do repositório inteiro — `.py`, `.html`, `.js`, `.json`, em `processo_seletivo/` e em
`tests/`. **44 ocorrências.** A repartição:

| Onde | Quantas | O que faz |
|---|---|---|
| Formulários e templates de composição | 6 | carrega o valor |
| Retificação e mutabilidade | 4 | declara o campo retificável |
| Documento publicado e tela do sorteio | 2 | **exibe**, com o rótulo *Derivação* |
| `seed_demo` e fixtures | 3 | dados de exemplo |
| Testes | 29 | dados de exemplo |

**Zero em `sorteios/domain/` e zero em `sorteios/application/`.** Nenhum caminho de execução o lê.

E a distinção já está escrita **duas vezes**, nas mesmas palavras, no `seed_demo` e nas fixtures do
sorteio: *"`occurrence` é a ocorrência concreta — o concurso —, e `derivation` é a prosa que explica
como ela foi escolhida. Se `occurrence` fosse a regra em prosa, a escolha de qual extração observar
voltaria para a mesa no dia do sorteio."*

**A `FR-510` está certa, e o projeto já a tinha descoberto** — só não a tinha transformado em
requisito.

### Um defeito de vocabulário, encontrado de passagem

O mesmo campo tem **dois rótulos**: *"Como a ocorrência decorre da data programada"* na composição, e
*"Como a ocorrência foi escolhida"* na Retificação. Princípio I. É pequeno, é de uma linha, e está
registrado aqui porque ninguém o encontraria procurando.

---

## R-4 — Onde a exceção é engolida, e por que a mensagem culpa a fonte

`sorteios/application/previa.py`, na função que resolve a próxima ocorrência a observar:

```
try:
    proxima = substituicao.proxima_a_observar(metodo, indisponiveis)
except DomainError as esgotada:
    return (None, "", [ …as ocorrências registradas como indisponíveis… ])
```

**Duas causas distintas caem no mesmo `except`:**

| Causa | O que aconteceu | O que a tela diz hoje |
|---|---|---|
| A cadeia de substituição **esgotou** | a fonte esteve indisponível 5 vezes | *"a ocorrência declarada e todas as substitutas estão indisponíveis"* ✅ correto |
| A regra **não soube derivar** | a referência não termina em número | **a mesma frase** ❌ e ela é falsa |

A própria `substituicao.py` levanta a segunda com uma mensagem **correta e específica** — *"a regra
da ocorrência seguinte não se aplica a X: ela deriva do número da ocorrência"* —, e o `except` a
descarta. **A frase certa existe e é jogada fora a uma linha de distância de onde seria exibida.**

---

## R-5 — O contraexemplo, palavra por palavra

O campo do instante da ocorrência, no mesmo bloco do formulário, ensina assim:

> *"Com fuso, como `2026-11-20T20:00:00-03:00`. É este instante que separa 'a fonte ainda não
> publicou' de 'a fonte não publicará': antes dele, a ausência não descarta a ocorrência."*

**Forma, exemplo e consequência.** É a formulação que a `FR-509` manda seguir, e ela está a três
linhas do campo que não ensina nada.

---

## R-6 — A suíte: três fixtures quebram, e elas são a prova do defeito

Varredura de toda declaração de `occurrence` no repositório: **16**, das quais **13 terminam em
número** e **3 não**.

As três estão no mesmo arquivo — `tests/unit/publicacoes/test_pdf_classificacao.py` — e têm a mesma
forma: `'concurso 6100 da Loteria Federal'`.

**Elas não são um problema da feature. São a evidência dela.** Alguém do próprio projeto, escrevendo
uma fixture, escreveu a referência do jeito que uma pessoa escreve — com o número no meio e a fonte
repetida no fim — e o motor não a derivaria. O número está lá; ele só não está onde a regra o
procura.

E a memória do projeto diz que regra impeditiva costuma quebrar a suíte em bloco, com **uma** causa
nas fixtures. Aqui são três linhas, um arquivo, uma forma.

> **Consequência para a ajuda da `FR-508`:** ela precisa dizer **só a referência**, e que a fonte já
> está declarada no campo acima. A forma natural de escrever duplica a fonte, e é justamente a que
> não roda.

---

## R-7 — ⚠️ Os Editais reais da amostra **não declaram ocorrência de fonte externa**

Li quatro dos que sorteiam — **57/2026, 58/2026, 69/2026 e 78/2026** — por extração de texto. Os
quatro trazem **a mesma cláusula**, palavra por palavra:

> *"Este programa sorteia aleatoriamente a ordem dos números através de algoritmos e cálculos
> matemáticos. Para fins de auditoria, observar o campo 'Semente utilizada: xxxxxxxxxxxxx',
> localizado ao fim da página do sorteio."*

**Nenhum menciona Loteria Federal, concurso, extração externa ou ocorrência.** O modelo real é: *o
software gera a semente e a publica depois*.

### O que isso significa, e o que não significa

**Não significa que o modelo do sistema esteja errado.** Ele é deliberadamente **mais forte**: semente
derivada de fonte pública externa, declarada antes, verificável por terceiro. A `021` escolheu isso
por escrito, e é o que permite a verificação pública que os Editais reais prometem e não entregam —
uma semente publicada depois não prova nada a quem não estava lá.

**Significa três coisas para esta feature:**

1. **O `SC-180` mede o que não interessa.** Varrer os doze Editais para contar quantos seriam
   impedidos devolveria **zero** — não porque estejam bem declarados, mas porque não declaram nada
   desta família. O critério precisa mudar de pergunta.
2. **A ajuda da `FR-508` tem um destinatário a mais do que a spec previu**: quem compõe partindo de
   um Edital real não tem, no texto de origem, o que escrever no campo da ocorrência. A tela precisa
   dizer o que ele é **e de onde ele sai**, não só a forma dele.
3. **Há uma pergunta de governança que esta feature não deve responder**: o sistema exige uma
   declaração que os Editais correntes do Cefor não fazem. Ou os Editais passam a declará-la — e é
   ganho de auditabilidade, que é o argumento da `021` —, ou existe uma família de sorteio que o
   modelo atual não representa. **Registro, e não decido.**

---

## Resumo, e o que ele pede

| | Medição | Consequência |
|---|---|---|
| R-1 | o motor existe | a spec acertou |
| **R-2** | **cinco dos seis campos já são validados; só a ocorrência não é** | **a spec descreve três buracos onde há um** |
| **R-2b** | **a Retificação já oferece o algoritmo como escolha** | a `FR-507` vira *generalizar*, não *criar* |
| R-3 | zero caminhos de execução leem a derivação em prosa | a `FR-510` confirmada, com folga |
| R-4 | duas causas num `except` só, e a frase certa é descartada | a `FR-517` tem endereço exato |
| R-5 | o contraexemplo está a três linhas | a `FR-509` tem modelo literal |
| R-6 | 3 fixtures quebram, num arquivo, com a forma que uma pessoa escreve | é a evidência, não o problema |
| **R-7** | **quatro Editais reais não declaram ocorrência externa alguma** | **o `SC-180` precisa mudar de pergunta** |

**O Phase 1 não deve começar antes de a `spec.md` ser revista nos pontos R-2 e R-7.** Escrever
`data-model`, contratos e `quickstart` sobre uma premissa medida como falsa é construir três
artefatos que depois teriam de ser refeitos — e é o que a `034` mostrou custar quatro passadas de
`analyze`.
