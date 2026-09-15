# Pesquisa — 027 · Estrutural de vagas

Fase 0. As perguntas que o plano precisou responder antes de existir, cada uma medida no código de
14/09/2026. Onde a resposta recusou uma alternativa, a razão da recusa está escrita: é ela que
impede a decisão de ser reaberta por esquecimento.

---

## T-001 — Onde a linha geral derivada é materializada

**Decisão: num normalizador de domínio sobre a carga do Perfil, aplicado por `replace_draft`, que
persiste a linha como qualquer outra.**

A linha geral precisa ter **identidade estável**, porque é por ela que a Retificação a alcança
depois de publicada e porque dois conteúdos idênticos têm de produzir o mesmo resumo canônico
(`025`, FR-168 e FR-170). Isso elimina as duas alternativas mais baratas:

- **Derivar na emissão do snapshot** (`edital_snapshot`) faria a identidade nascer a cada emissão.
  Duas emissões do mesmo rascunho produziriam resumos canônicos diferentes — quebra direta da
  FR-168 da `025`, e o teste que a guarda reprovaria.
- **Derivar só na interface**, montando a linha no formulário, deixaria o canal de API fora: quem
  gravasse rascunho por `PUT /draft` continuaria publicando Perfil sem linha, e a FR-316 fala do
  sistema, não da tela.

Sobra uma terceira, que **funciona e foi recusada por outra razão**: identidade determinística
(`uuid5` da identidade do Perfil) derivada na emissão manteria o resumo estável. Ela foi recusada
porque a linha continuaria não existindo no rascunho — a conferência da submissão não teria o que
conferir, a Revisão não teria o que exibir e o `PROTECT` do banco não teria o que proteger. A linha
derivada é uma linha; fingi-la só na saída faria o sistema ter, de novo, dois lugares dizendo a
mesma coisa.

**Onde entra:** `editais/application/draft.py`, imediatamente antes do laço que cria
`LinhaDoQuadroDeVagas`, chamando uma função pura de `editais/domain/perfis.py`. Idempotente: se a
carga já traz a linha geral, o `id` recebido é preservado e só a quantidade é reafirmada.

---

## T-002 — O que conta como "lista reservada", e o que isso conserta de quebra

**Decisão: Modalidades declaradas no Perfil, menos a que o Perfil declara ser a da ampla
concorrência.**

O campo já existe — `PerfilVaga.modalidade_ampla_concorrencia`, publicado como
`generalCompetitionModalityId` — e `_ampla_concorrencia_declarada` já recusa dar linha própria a
ela. Casar a denominação continua recusado (`025`, R-006).

**E aqui o plano encontrou uma lacuna fechável.** A conferência de igualdade de
`_coerencia_do_quadro_de_vagas` testa a completude assim:

```python
elif tem_linha_geral and not (set(modalidades) - com_linha) and soma != total:
```

`modalidades` inclui a declarada como ampla — que, por obedecer a FR-176 da `025`, **nunca** tem
linha. Logo a diferença nunca é vazia, a igualdade nunca roda, e o Edital no formato mais comum do
acervo — uma Modalidade "Ampla concorrência" mais as reservadas — nunca tem a soma conferida. É a
lacuna que a `025` registrou como `R-006` e deixou aberta por não ter, então, como identificar a
ampla.

Com a FR-317 ela fecha: a completude passa a ser `set(modalidades) - {ampla} - com_linha == ∅`.

**Está no escopo por necessidade, e não por vizinhança.** Sem esse fechamento, um Perfil com ampla
declarada e uma reservada pode publicar linha geral e linha reservada que não somam o total, em
silêncio — que é exatamente a divergência entre os dois números que esta feature existe para
eliminar. Entregar a derivação sem fechar a completude deixaria o defeito vivo por outro caminho.

---

## T-003 — Onde a exigência da linha geral bloqueia sem prender o acervo

**Decisão: `validate_for_publication` passa a receber qual ato está sendo conferido, e a exigência
da linha geral só é impeditiva na conferência de rascunho.**

O risco é concreto e teria passado despercebido: `publicacoes/application/retificacoes.py` afere o
conteúdo que a Retificação produziria com
`blocking_findings(validate_for_publication(content))`. Uma exigência impeditiva de linha geral
escrita sem recorte **bloquearia toda Retificação de todo Edital do acervo** — inclusive a que
corrige uma data e nada tem com vagas. Seria coagir pelo caminho errado, e a FR-323 já proíbe por
escrito.

O parâmetro é honesto porque a distinção é do domínio, e não de implementação: publicar Edital novo
sem linha geral é criar hoje o defeito que a feature remove; retificar Edital publicado antes dela é
o único caminho que o acervo tem.

- Chamadas de rascunho — `interface/views._pendencias` e `publicacoes/application/publish_edital` —
  conferem o ato de publicação.
- `retificacoes.py` confere o ato de Retificação, e ali a ausência de linha geral **não** é
  impeditiva. As advertências da feature continuam sendo produzidas (T-006).

Alternativa recusada: severidade única para os dois atos. Ou prenderia o acervo, ou não impediria o
Edital novo — e as duas metades são requisito.

---

## T-004 — As duas advertências, e por que são duas

**Decisão: `_coerencia_do_quadro_de_vagas` ganha a advertência de lista reservada sem linha
(FR-324), e `_ampla_concorrencia_declarada` ganha a de Modalidade declarada sem ampla apontada
(FR-325).**

São duas porque os atos que as resolvem são diferentes: uma se resolve escrevendo uma quantidade, a
outra escolhendo num campo que já existe. Uma advertência só, somando os dois casos, mandaria metade
das pessoas ao lugar errado.

A segunda também cumpre, enfim, a promessa que a `025` deixou escrita na FR-176 — *"o que o sistema
pode fazer é dizer, na composição, que o número da ampla concorrência mora na linha geral"* — e que
até aqui não tinha canal.

As duas são `Severity.WARNING`, que `interface/views._pendencias` já traduz para `informacao`/aviso
e encaminha por `_destino` à etapa que as resolve. Nenhum mecanismo novo.

---

## T-005 — Por onde o acervo é dito a quem pode retificá-lo

**Decisão: uma sexta espécie de sinal na supervisão do Processo.**

`interface/supervisao.py` já monta sinais por Edital publicado, com `Destino` (rótulo e URL),
`Medida` (numerador e denominador) e supressão por alcance do ator — e a `022` já decidiu que sinal
que o ator não alcança nem chega a ser montado. A leitura que a FR-331 pede é exatamente essa forma:
por Edital publicado, com quantos recortes ficam sem quantidade, e com destino para o ato.

Alternativas recusadas:

- **Tela nova de "acervo inerte"**: uma sexta espécie custa uma função de detecção e uma entrada no
  catálogo; uma tela custa rota, porta, template e teste de autorização, para dizer menos.
- **Comando de gestão que lista**: não é canal do ator. O Princípio VI recusa demonstrar por chamada
  manual o que o canal do ator não oferece.

A leitura é **por Processo**, como toda a supervisão. Uma varredura global do acervo inteiro não tem
onde morar hoje, e inventá-la seria escopo que ninguém pediu.

---

## T-006 — A conferência da Retificação e as advertências que ela hoje descarta

**Decisão: a tela de confirmação da Retificação passa a exibir os achados não impeditivos do
conteúdo que o ato produziria.**

`retificacoes.py` calcula `validate_for_publication(content)` e fica só com
`blocking_findings(...)`; o resto é descartado. A FR-336 pede que a conferência da Retificação diga
o mesmo que a submissão diz — e a informação já é calculada, só não é mostrada.

É também o que sustenta o caso da borda: retificar um Edital publicado acrescentando a primeira
Modalidade deixa o quadro parcial, que é legítimo, e a advertência é o que impede que fique
silencioso.

---

## T-007 — O bloco do quadro que ainda não existe quando a primeira Modalidade chega

**Decisão: o fragmento que acrescenta Modalidade passa a entregar a seção do quadro inteira quando
ela ainda não está desenhada, e só a linha quando já está.**

Hoje `_modalidade_com_linha.html` manda a Modalidade para o destino do botão e a linha
correspondente **fora de banda**, para `#quadro-{{ indice }}`. O mecanismo está certo e continua; o
que muda é que, no Perfil sem lista reservada, `#quadro-{{ indice }}` não existe — o alvo fora de
banda não acha nada e a linha se perde sem erro.

O envelope fora de banda passa a endereçar um ponto que existe sempre no cartão do Perfil, e entrega
a seção com a linha geral preenchida quando ela é a primeira. O comentário que já está no template
sobre o invólucro descartado continua valendo e ganha o segundo caso.

---

## T-008 — O que esta feature quebra na suíte, e por quê isso é esperado

**Medida: toda composição de Perfil que hoje publica sem quadro passa a publicar linha geral.**

Fixtures, testes de aceitação e testes de conteúdo publicado que afirmam `vacancyTable: []` ou que
comparam resumo canônico de Edital composto sem quadro mudam de valor. Não é regressão: é o efeito
declarado da FR-318, e a `026` pagou exatamente esta conta ao ligar o contrato ao ato — *"onze
testes caíram, cada um uma decisão anterior que a matriz contradizia"*.

O que **não** pode mudar é o conteúdo já publicado: nenhuma migration toca em `PublishedVersion`, e
a SC-110 é verificada por teste que relê os resumos canônicos do acervo semeado antes e depois.

---

## T-009 — A FR-334 precisa de código?

**Não. Precisa de teste.**

`ocupacao/application/emissao.py` lê `effective_version(edital_id=..., at=ctx.now)` e congela os
efeitos no ato; a ordem vigente é escolhida por `ato_vigente`. Uma Retificação que acrescente linha
hoje não alcança ato praticado ontem, por construção. O que falta é o teste que fixa isso como
promessa desta feature, para que uma mudança futura em `effective_version` não a desfaça em
silêncio.

Mesma natureza da FR-309 da `026`, e mesma forma de guarda.

---

## T-010 — Os números da demonstração

**Decisão: o quadro entra em `seed_demo` por Perfil, e a repartição é declarada onde ela ensina
alguma coisa.**

| Perfil | Hoje | Passa a |
|---|---|---|
| `DOC-INFO` (2 vagas, Modalidades AC e PPP) | nenhuma linha | declara AC como a ampla; linha geral 1, linha PPP 1 |
| `TEC-LAB` (0 vagas, Modalidade AC só) | nenhuma linha | declara AC como a ampla; linha geral 0, derivada |
| `TEC-EAD` (40 vagas, Modalidades AC e PPP) | nenhuma linha | declara AC como a ampla; linha geral 30, linha PPP 10 |

Os três casos da feature ficam demonstrados no mesmo seed: repartição declarada, derivação pura, e o
Perfil de sorteio — que é o que a Ocupação e a Convocação percorrem — com quantidade a apurar nos
dois recortes.

**O `seed_demo` não deixa de ser o que era.** Ele continua sem produzir o certame do manual, e isso
continua registrado onde já estava.

---

## T-011 — Degrau de schema: não há

O quadro é conteúdo publicado desde o degrau 12, e `generalCompetitionModalityId` desde o 13. Esta
feature **não acrescenta campo nenhum** ao conteúdo publicado: ela muda quem escreve um valor que a
forma já admite, e o que o sistema diz sobre ele.

Consequência direta: **nenhuma migration, nenhum degrau, nenhuma conversão de conteúdo publicado** —
e é o que torna a D-006 barata de cumprir. O acervo fica exatamente como está até que alguém o
retifique.
