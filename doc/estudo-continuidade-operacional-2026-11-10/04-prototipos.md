# Entrega D — Protótipos navegáveis

## O que são, e o que não são

São as **telas reais**, salvas em HTML no estado em que o operador as viu, e as mesmas telas com **só a
melhoria aplicada**. Não há tela redesenhada à mão, nem componente novo da gestão:

- o **antes** sai de [`prototipo/capturar_antes.py`](prototipo/capturar_antes.py), que pratica os atos no
  banco descartável e salva a página logo depois de cada um (a mensagem de sucesso só existe nessa
  resposta). As folhas e os scripts vêm do mesmo servidor;
- o **depois** sai de [`prototipo/montar_depois.py`](prototipo/montar_depois.py): carrega cada página do
  antes no navegador, aplica uma transformação de [`prototipo/transformacoes/`](prototipo/transformacoes/)
  e salva o resultado estático. Se a tela real mudar a ponto de a transformação não achar o que muda, a
  montagem falha (`exigir`, em `comum.js`).

**Linguagem visual.** O depois usa as folhas da gestão e as classes que ela já tem: `consequencias
irreversivel`, `ajuda`, `botao`, `secundario`, `proximo-nesta-lista`, `ainda-neste-marco`. A folha do
protótipo ([`continuidade.css`](prototipo/sitio/static/prototipo/continuidade.css)) só acrescenta as peças
novas — objetivo, índice, retorno — e usa só os tokens de `shared/tokens.css`.

**O que depende da D-5 está marcado** com contorno tracejado amarelo e o rótulo "Depende da D-5". Está
ali para que a decisão se tome olhando a tela, e não para ser adotado.

Nada no protótipo grava no GPS: o que leva adiante no percurso é link entre as páginas do protótipo.

## Como rodar

```bash
python3 doc/estudo-continuidade-operacional-2026-11-10/prototipo/servidor.py 8171
```

Ou a entrada `continuidade-prototipo` do `.claude/launch.json`. Abra <http://localhost:8171/>. O
servidor responde com a **CSP de produção** (`style-src 'self'`, `script-src 'self'`): um estilo inline
que funcionasse no protótipo e sumisse na implementação seria um falso positivo.

Para refazer do zero (o banco do estudo precisa estar no ar, na 8170, com o C06 recém-restaurado):

```bash
cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/capturar_antes.py
```

```bash
cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/montar_depois.py
```

```bash
cd backend && uv run python ../doc/estudo-continuidade-operacional-2026-11-10/prototipo/validar.py
```

Os ids do banco do estudo estão em `capturar_antes.py`; um banco novo os troca por `prototipo/ids.json`.

## Os dois percursos

**Jornada A — sorteio (C06).** Comece em [`depois/centro-c06-inicial.html`](prototipo/sitio/depois/centro-c06-inicial.html):
1. "Abrir a tela" leva aos **recortes** do sorteio, e não ao topo (M-02);
2. a tela diz o que se faz ali, em três passos, com os nomes do Centro e "(no GPS: …)" (M-03); os
   recortes vêm antes da ocorrência; o método fica recolhido, inteiro; "Observar" é secundário enquanto há
   lista por fixar; sai o "Nenhum corte emitido" de antes do sorteio (M-06);
3. "Fixar os participantes desta lista" leva ao estado depois do congelamento da ampla: o "Ainda neste
   marco" é link para a PPP (M-07), a consequência da ordem está marcada D-5, e o bloco termina em
   "Voltar ao Centro de Controle do Edital" (M-01);
4. de volta ao Centro, a exceção à "ordem livre" aparece marcada D-5, e "Fixar · PPP" leva direto à PPP.

**Jornadas D e E — conferência e convocação (C12, C15).** Comece em [`depois/centro-c12.html`](prototipo/sitio/depois/centro-c12.html):
1. "Conferir os documentos" leva às **chamadas praticadas** (antes: topo da tela, seção a 2.151 px) (M-02);
2. a convocação ganha um índice das seções (M-05) e "Ocupadas **na apuração**" (M-09);
3. os documentos da Cecília mostram Edital, Perfil e lista no alto, e o retorno diz "Próximo para esta
   pessoa: registrar o desfecho", que leva à chamada dela (M-08, M-07), e volta ao Centro (M-01);
4. no C15, [`depois/convocacao-c15.html`](prototipo/sitio/depois/convocacao-c15.html): "Convocar as 2…"
   leva à **conferência** (M-04), com as duas pessoas, o texto que cada uma lerá, o prazo (ou a falta
   dele) e quem fica de fora. "Cancelar e voltar" volta.

## Escolhas conservadoras, registradas

| Escolha | Alternativa descartada | Por quê |
|---|---|---|
| O retorno ao Centro só no bloco que segue um ato | um item "Centro de Controle" na migalha de todas as telas | a migalha é a D-2; o bloco já existe e já é o momento de "entender o resultado e voltar" |
| "Observar" vira secundário, mas continua clicável | desabilitar até fixar todas as listas | desabilitar é a opção (a) da D-5 |
| A frase "uma lista fixada depois da semente não sorteia" marcada D-5 | adotá-la como texto | é a opção (c) da D-5 |
| O método do sorteio recolhido num `details` | resumi-lo | é conteúdo publicado do Edital: continua inteiro, a um clique (V3 confere o resumo) |
| "Ocupadas na apuração" | "Alcançadas" ou outro termo | não troca a palavra do domínio; só diz de onde o número vem |
| A conferência da convocação com as peças de `marco_conferir.html` | uma conferência nova | o padrão já existe e é o que funciona (P-2) |

## A validação

### Automatizada

[`prototipo/validar.py`](prototipo/validar.py) sobe o servidor com a CSP de produção, percorre o antes e o
depois no Chromium e grava [`validacao.txt`](validacao.txt). **50 de 50 conferências passaram.**

| Código | O que confere | Resultado |
|---|---|---|
| V0 | nas 9 páginas, a 1440 e a 375 px: nenhuma violação de CSP nova, nenhuma rolagem horizontal nova, nenhum estilo ou script inline novo | 27 de 27 |
| V1 | no sorteio, "fixar" vem antes de "observar"; o primeiro "fixar" sobe | antes 1.681 px, abaixo de "observar" (887); depois **1.053 px**, acima de "observar" (1.720) |
| V2 | sem "Nenhum corte emitido" antes do sorteio | ok |
| V3 | o resumo do método publicado continua na tela, no `details` | ok |
| V4 | o "Ainda neste marco" é link para a lista que falta; o retorno ao Centro está na dobra | y = 655 |
| V5 | as providências do Centro chegam ao alvo, dentro da dobra | sorteio → recortes; Centro → PPP; Centro → chamadas (antes, 2.151 px) |
| V6 | o percurso de ida e volta: Centro → tela → ato → retorno → Centro no estado novo | A e E |
| V7 | o índice da convocação leva a cada seção; os documentos dizem o contexto e o próximo da pessoa; o desfecho chega na dobra | ok |
| V8 | convocar leva à conferência; ela mostra 2 pessoas, o texto, o prazo e quem fica de fora; cancelar volta; a ajuda não promete mais o que não há | ok |
| V9 | os números das vagas não mudam, só o rótulo | 3 · 3 · 2 · 1 · 0 · 0 |
| V10 | toda frase sobre a ordem semente × fixar está marcada D-5 | 1 de 1 |
| V11 | no teclado, o Tab chega a "fixar" antes de "observar" | posições 15 e 17 |

**O que a validação achou na tela real.** A 375 px, o sorteio depois do congelamento **já tem rolagem
horizontal** no antes (o resumo de 64 caracteres). O depois não piorou nem corrigiu: virou o M-21.

### Por inspeção

Conferido no painel de navegação e nas capturas `prototipo-*`:
- **Defeito encontrado e corrigido no protótipo:** a primeira montagem da conferência da convocação
  listava 5 pessoas — o seletor pegava também a fila. Corrigido para ler a lista da própria seção dos
  titulares, e o V8 passou a exigir exatamente 2.
- A nota "(derivado do Edital e dos atos deste recorte)" saía dentro do texto do candidato; é ajuda da
  tela, e saiu.
- "Fixar" continua abaixo da dobra a 1440 × 900 quando se abre a tela **pelo topo** (1.053 px): a lista
  de 10 participantes vem antes do botão, como na tela real. Pela providência do Centro, que chega aos
  recortes (M-02), ele aparece na primeira tela. As duas melhorias funcionam juntas.

### O que não se validou

- **Com pessoas.** Nenhum operador usou o protótipo. A tabela "o que se mede" do plano de produção da
  136 serve aqui também.
- **Os estados que o protótipo não tem:** a conferência antes de congelar (M-12) e a ordem sorteada na
  tela do sorteio (M-13) estão no inventário, sem protótipo.
- **Leitor de tela.** Só a ordem do Tab foi medida.

## As capturas

| Antes | Depois |
|---|---|
| `prototipo-antes-sorteio-c06-inicial-dobra.png` | `prototipo-depois-sorteio-c06-inicial-dobra.png` |
| `prototipo-antes-sorteio-c06-apos-fixar-a-ampla-dobra.png` | `prototipo-depois-sorteio-c06-apos-fixar-a-ampla-dobra.png` |
| `prototipo-antes-documentos-c12-apos-conferir-dobra.png` | `prototipo-depois-documentos-c12-apos-conferir-dobra.png` |
| `prototipo-antes-convocar-c15-conferencia-dobra.png` (a tela da convocação) | `prototipo-depois-convocar-c15-conferencia-dobra.png` |

E as demais, uma por página, a 1440 px, e três a 375 px.
