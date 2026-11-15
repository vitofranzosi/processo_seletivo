# Relatório do piloto do design system

*15/11/2026, na branch `claude/172-piloto-implementacao`, a partir da `main` em `499491be`. FR-7740 e
SC-2609. **A validação com a equipe (US4) ainda não aconteceu**: o roteiro, os bancos e as duas
versões estão prontos, e as sessões são do usuário. Este relatório responde ao que se mede sem a
equipe, e diz o que fica esperando por ela. A decisão sobre a migração é do usuário.*

> **Segunda versão (15/11, D-012 da spec).** A primeira prendia a prosa em 80 caracteres e centrava a
> confirmação numa coluna estreita. O usuário a viu e a achou pior que a `main` ("o texto não está
> utilizando o espaço disponível"), e escolheu que o texto ocupe a largura do conteúdo. Este
> relatório é o da segunda versão; o que a primeira mediu está no fim, em *A primeira versão*.
>
> **Ajustes da segunda leitura (15/11).** O usuário pediu, como padrão a generalizar, três coisas, que
> a segunda versão já traz: os **indicadores dividem a linha em partes iguais**, em vez de caixas do
> tamanho do texto; os **campos de texto ocupam a largura do formulário** (a `main` os limita a
> 68ch); e o **rótulo e o valor ficam na mesma linha**, com dois-pontos, em toda lista de definição.

## Resposta curta

**Com o mesmo conteúdo e o mesmo comportamento, a composição nova aproveita a largura, deixa as
páginas mais baixas e aproxima a ação, sem esconder nada.**

- **O conteúdo ficou idêntico.** Nos 64 estados, nas cinco larguras e nas duas ordens: nenhum bloco
  de texto a mais ou a menos, nenhuma quantidade, associação ou ação diferente e nenhuma sequência
  declarada invertida. A ordem não mudou nem fora das sequências.
- **O texto ocupa a largura do conteúdo**, inclusive onde a `main` o limitava a 68ch (o subtítulo, a
  ajuda, as notas, a faixa da Lista e as caixas da confirmação).
- **As páginas ficaram mais baixas.** A 1440 px, somando os estados de cada tela: confirmação −6,9%,
  conferências −11,5%, Ocupação −3,5%, retornos da Ocupação −3,6%, Lista −3,0%. No banco da referência,
  com 20 Processos por página, a Lista cai de 2929 para 2709 px.
- **A ação principal ficou mais perto em seis dos sete estados** que a têm abaixo da dobra a
  1280 × 800 (de 11 a 158 px mais acima), e 10 px mais longe na O-13; nenhum chegou acima da dobra.
- **Nada fora do piloto mudou**: a `main` e a branch, rastreadas sobre o mesmo banco, só diferem nas telas do piloto.
- **A acessibilidade conferida passou** em todos os 15 estados conferidos.

## Os critérios

| Critério | Resultado | Evidência |
|---|---|---|
| SC-2600, conteúdo e ações preservados | **cumprido**: 0 diferença em 320 fotografias | `doc/auditoria-design-system-2026-11-14/piloto/comparacao/resumo.md` |
| SC-2601, sequências | **cumprido**: 28 sequências, nenhuma invertida, nas duas ordens | idem |
| SC-2602, nada fora muda | **cumprido**: só as telas do piloto diferem, fora uma diferença de dado | *O rastreio*, abaixo |
| SC-2603 (revisto pela D-012), a prosa na largura do conteúdo | **cumprido**: nenhuma medida de leitura no escopo; a linha mais longa é registrada, sem valor de aprovação | idem |
| SC-2604, ação acima da dobra | **não cumprido em 7 estados** (C-01, C-06, K-01, K-04, K-06, O-13, O-15), embora mais perto em seis | idem, e a tabela abaixo |
| SC-2605, acessibilidade | **cumprido** nos 15 estados conferidos | *A acessibilidade*, abaixo |
| SC-2606 e SC-2607, validação | **pendente**: as sessões com a equipe | `validacao.md` |
| SC-2608, suíte e lint | ver *Verificação* | — |
| SC-2609, hipóteses | respondidas abaixo, até onde o piloto informa sem a equipe | — |

### A ação e a dobra (SC-2604)

O topo da ação principal a 1280 × 800, em px. Ela está acima da dobra quando termina antes de 800.

| Estado | Antes | Depois | Diferença |
|---|---:|---:|---:|
| C-01 Submeter (cinco atenções) | 936 | 848 | −88 |
| C-06 Publicar | 1060 | 968 | −92 |
| K-01 Conferir o acréscimo | 878 | 783 | −95 |
| K-04 Conferir o desfazimento | 983 | 886 | −97 |
| K-06 Conferir a declaração | 969 | 811 | −158 |
| O-13 Ocupação com vagas acrescidas | 812 | 822 | +10 |
| O-15 Ocupação, a vaga sem quem a ocupe | 1203 | 1192 | −11 |

**Por que ainda não cabem, e o que o piloto não fez.** O que vem antes do botão é texto decidido em
spec (as cinco atenções da C-01, a lista de quem a ordem alcança da K-01), e a O-15 tem a ação no
terceiro recorte. Três saídas foram consideradas e recusadas:

- **A barra de ações fixa ao pé da janela** poria o botão à vista, mas antes das consequências na
  ordem visual, e inverteria a C-S4 ("a consequência antes da confirmação"). Numa tela de ato
  irreversível, é a inversão que a spec existe para impedir.
- **Anunciar a ação acima da dobra** (a alternativa que a FR-7731 admite) exigiria um bloco de texto
  novo, que a FR-7707 proíbe. **As duas FRs se contradizem** quando a ação está abaixo: é achado da
  spec, abaixo.
- **Pôr os recortes da Ocupação lado a lado** encurtaria a O-15, e seria outra forma de aproveitar a
  largura. O usuário escolheu, entre as opções, o texto na largura toda, e não as colunas; fica como
  hipótese.

### A acessibilidade (SC-2605)

Conferida por uma sonda no navegador, nos mesmos estados do catálogo: C-03, C-09, C-11, C-12, O-06,
O-12, O-13, R-02, R-06, K-01, K-05, K-09, L-01, L-05 e L-10.

| Conferência | Resultado |
|---|---|
| Ordem de tabulação igual à visual | nenhuma inversão nos 15 |
| Foco visível em todo controle | sim, em todos |
| Foco coberto por outro elemento | nenhum (a barra de ações não é fixa) |
| 320 px; zoom de 200%; zoom de 400% | nenhuma rolagem horizontal nos 15 |
| A recusa recebe o foco | sim, nos cinco estados com recusa (C-12, R-02, R-06, K-05, K-09) |
| Todo campo com rótulo associado | sim |
| Leitor de tela | **não conferido**: não houve quem o conferisse |

**Uma ressalva, de antes do piloto:** a recusa cita o campo no texto, mas o campo não aponta para ela
(`aria-describedby` aponta só para a ajuda). A FR-7727 pede os dois. O piloto não muda atributo de
template, e o achado fica registrado abaixo.

## O rastreio (SC-2602)

**O critério não se mede contra o `telas.csv` da referência.** O `ps_p0_referencia` ficou para trás
das migrations que entraram na `main` depois da P0 (a `167`, a `168` e a `170`), e o rastreio dele
com o código de hoje dá 500 em toda tela que lê a agenda e as novidades. Migrá-lo mudaria a
referência, e a referência fica intocada.

O que se mediu no lugar dele, e que isola o piloto melhor: **a `main` de hoje e a branch do piloto,
rastreadas sobre a mesma cópia migrada da referência** (`ps_piloto_validacao`), pelas entradas
`piloto-antiga` e `piloto-nova`. As duas diferem só pelo código do piloto.

**Resultado, na segunda versão: nada fora do piloto mudou.** No `telas.csv`, diferem:

- **as telas do piloto**: a Lista nas duas formas (`/gestao/` e `/gestao/?situacao`), os seis atos
  da confirmação que o rastreio alcança e a Ocupação. As conferências não aparecem porque só nascem
  de um POST;
- **a página Novidades, só na altura**, por dado: a primeira passada registrou a visita de
  `paulo.presidente`, e a seguinte leu "Nada novo desde a sua última visita" no lugar de "Esta é a
  sua primeira visita". As folhas carregadas são as mesmas;
- **um padrão a mais na versão nova**, a segunda página da trilha de uma Distribuição
  (`…/trilha?cursor`), por dado: as passadas do rastreio registram entradas na trilha, e a terceira
  passada encontrou registros para uma página nova.

**A amostra de vinte capturas de fora do piloto** (sorteada com semente 172 entre os 110 padrões de
fora, na primeira versão): 17 idênticas byte a byte, e três com diferença de pixel — o formulário de
aviso novo, a escolha de identidade da demonstração e a Agenda —, com as mesmas folhas, a mesma
altura e as mesmas métricas. A segunda versão só mudou a folha do piloto e retirou um token que só
ela usava.

**As telas do piloto no banco da referência** (a 1440 px; a metade direita é o diagnóstico da
FR-7734, a fração da altura em que há conteúdo à direita do meio da página):

| Tela | Altura, antes → depois | Metade direita a 1440 | Metade direita a 1920 |
|---|---|---|---|
| Lista (`/gestao/`) | 2929 → 2709 px | 32% → 35% | 25% → 31% |
| Lista, outra aba | 986 → 938 px | 25% → 24% | 9% → 20% |
| Encerrar | 1023 → 905 px | 22% → 22% | 0% → 2% |
| Publicar | 969 → 900 px | 19% → 21% | 0% → 3% |
| Submeter | 1237 → 1061 px | 24% → 17% | 0% → 12% |
| Cancelar | 933 → 900 px | 25% → 25% | 0% → 6% |
| Ocupação | 1050 → 979 px | 18% → 23% | 2% → 13% |

O portal autenticado não foi rastreado: o passo dele pede o código de acesso de cada candidato,
digitado à mão. As folhas do piloto não chegam ao portal, e os tokens acrescidos não são usados por
nenhuma regra dele.

## As hipóteses que o piloto devolve (o quadro do roadmap)

| Hipótese | O que o piloto informa |
|---|---|
| Redução tipográfica | **nada**, de propósito: os tamanhos são os de hoje, e o experimento opcional não foi feito |
| Recolher e deslocar explicações | **nada ainda**: é a pergunta "o que você leu e o que pulou" da validação |
| Um botão cheio por tela | **cabe por bloco, e não por tela**: a confirmação e as conferências têm um; a Lista tem dois ("Novo Processo Seletivo" e "Buscar"); a Ocupação tem um por recorte que tem gesto, e a O-04 chega a dois (um "Apurar" em cada recorte com ordem). A regra que cabe é "um botão cheio por bloco de gesto" |
| Um aviso por tom | **não cabe** sem mudar conteúdo: a C-01 tem cinco atenções e a C-09 três itens de atenção numa caixa; juntá-las seria recolher ou reescrever, o que o piloto não faz |
| Quatro pontos de quebra | **sem evidência**: nenhuma das três telas precisou de `@media` próprio |
| Trilho no celular | **o trilho não coube na Ocupação**: o que poderia ir para o lado ("Termos desta tela", "Abrir esta tela não apura nada") precisa vir antes do primeiro recorte nas duas ordens (O-S1, O-S3), e ao lado ele ficaria depois na ordem visual. A Ocupação ficou na composição cheia |
| Guardiões novos | o levantamento está em `levantamento-dos-guardioes.md`: cor só por token nasceria verde; caixa nova acusaria a própria folha do piloto duas vezes |

E uma que o quadro não tinha, e que o usuário decidiu:

| Hipótese | O que o piloto informa |
|---|---|
| A medida de leitura | **a linha curta não é ganho para o usuário** se custa altura e deixa a direita vazia (D-012). A primeira versão, com 80 caracteres, deixou páginas até 21% mais altas; a segunda, com o texto na largura, as deixou mais baixas. A medida da `main` (68ch) também sai das telas do piloto |

## Desvios do plano, registrados

- **64 estados, e não 63**: a C-12 virou C-12 e C-13.
- **O-06 e O-14** mostram menos do que a D-004 descrevia (ver `doc/…/piloto/README.md`).
- **A ampla concorrência e o passo seguinte saem da comparação** nos estados montados sobre o sorteio
  da `155`, porque a fixture os muda de uma montagem a outra.
- **"Novo Processo Seletivo" não subiu para o cabeçalho da Lista**: a ordem de leitura da `129`, que
  um teste prende, o quer depois da faixa.
- **A barra de ações não é fixa** (acima).
- **Um banco por tarefa na validação, e a mesma cópia para as duas versões** (FR-7737 pedia registros
  diferentes na segunda versão): as fixtures supõem banco vazio, e a mitigação é a ordem alternada.
- **A T-S1 não se confere**: a trilha é da moldura, fora do `main` que o inventário lê.
- **A medida de leitura e a composição centrada saíram** (D-012): a FR-7704, a FR-7730, a SC-2603 e
  a UX-850 foram revistas na spec.

## Achados, para o usuário decidir

1. **A FR-7731 e a FR-7707 se contradizem** quando a ação fica abaixo da dobra: a primeira admite
   anunciá-la acima, e a segunda proíbe bloco de texto novo.
2. **A medida `--leitura` (68ch) continua valendo em toda tela fora do piloto**, e a preferência do
   usuário (D-012) vai contra ela. Se a migração seguir, ela sai junto; se não seguir, fica.
3. **Três regras comuns valem só para o filho direto de `main`**: a medida do parágrafo e o respiro
   antes da seção, em `componentes.css`, e a medida da confirmação, em `confirmacao-de-ato.css`.
   Qualquer contêiner nas telas que as usam as desfaz em silêncio. No piloto isso deixou de importar
   para as medidas, que saíram, mas o respiro foi reposto sob o escopo.
4. **A recusa não é apontada pelo campo** (`aria-describedby`), nas telas do piloto e, provavelmente,
   nas outras: a FR-7727 o pede.
5. **O componente "cartão" não existe como classe aplicável**: o piloto desenhou caixa por regra
   própria duas vezes (o recorte da Ocupação e a consulta da Lista).
6. **O banco da referência ficou para trás das migrations**, e o critério "nada fora muda" deixou de
   poder ser medido contra ele sem migrá-lo.

## Verificação

`cd backend && make lint check test-pg`, em 15/11, sobre esta branch: `lint` e `check` verdes, e a
suíte em **21 380 passando e 15 pulados, sem falha** (712 s, 4 workers, com o grupo `navegador` e sem
o `assistente`). Os 15 são os 13 que a P0 mediu nessa configuração mais os dois módulos sob demanda
do piloto, que pulam sem a variável (a fotografia e os bancos da validação). Nenhum guardião foi
afrouxado; quatro aprenderam o que o piloto acrescenta, sem mudar o que exigem:

- o mapa de quem carrega cada folha ganhou a do piloto, com as cinco telas;
- a ordem das folhas da Lista ganhou a do piloto, depois da da tela;
- os três ajudantes de "o conteúdo começa pelo título" aprenderam que o contêiner `.piloto-ds` é
  moldura, como já admitiam o `<header>`, só por esse nome;
- a lista de pares de contraste ganhou os oito pares dos tokens novos, todos acima de 4,5:1.

E um guardião acusou duas vezes o que o piloto fazia de errado, e o piloto mudou: os tokens têm um
lugar só, e `acesso.css` deixou de redeclarar os que subiram para `tokens.css`; e a primeira versão
redefinia `--leitura` na folha (a segunda já não tem medida nenhuma).

**A segunda versão** (o texto na largura) passou de novo por `tests/interface` e `tests/performance`
(6106 passando), pela fotografia e comparação dos 64 estados (zero diferença de conteúdo, ação e
sequência) e pela sonda de acessibilidade (os 15 estados limpos).. A suíte inteira, de novo:
`make lint check test-pg` verde, **21 380 passando e 15 pulados, sem falha** (721 s, 4 workers).

## A primeira versão (80 caracteres e coluna centrada)

Medida em 15/11 e recusada pelo usuário no mesmo dia. Conteúdo idêntico nos 64 estados, como a
segunda. A maior linha caiu de 193 para 78 caracteres, mas as páginas das conferências e da Ocupação
ficaram mais altas, e a ação principal desceu em seis dos sete estados abaixo da dobra: de 57 a
278 px (a O-15, de 1203 para 1481). O usuário, sobre a Lista: "o piloto está pior. O main tem
margem pra melhoria — o texto não está utilizando o espaço disponível".
