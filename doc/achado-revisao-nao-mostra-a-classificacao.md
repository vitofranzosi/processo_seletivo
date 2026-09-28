# A Revisão não mostra a Classificação que a submissão congela

**Encontrado em**: 27/09/2026, no ensaio do [teste operacional assistido](roteiro-teste-operacional-assistido-28-2026.md)
(passo 0,5), contra a `main` em `f6efe0dd`.

**Estado**: **corrigido em 27/09/2026**, antes da spec do passo 1, por decisão do usuário. Ver
[a correção](#a-correção-2709), no fim. Até aqui, o texto é o registro como foi feito.

---

## O que se vê

O Edital do ensaio tem a estrutura do 28/2026: 7 Perfis, 3 Modalidades, 18 Eventos e 7 marcos que
ordenam por sorteio, com o método comum declarado no alto da etapa Classificação. Na Revisão, o bloco
*"O que será congelado na submissão"* lista sete grupos: Identificação, Perfis de Vaga, Cronograma,
Etapas de Avaliação, Documentos Exigidos, Anexos e Conteúdo. **Não há grupo de Classificação.** Quem
submete não lê, nessa tela:

- o **método do sorteio** — algoritmo, fonte da semente, ocorrência, instante, normalização e
  substituição;
- os **marcos** de cada Perfil — como a ordem é produzida, a regra de corte, os suplentes, a Etapa
  que o corte alimenta, a faixa seguinte e o recurso;
- os **critérios de desempate**, quando houver.

O documento sabe de tudo isso. A *"Visualizar Edital"* da mesma tela gera o PDF, e lá cada Perfil
traz *"Marcos classificatórios"* com o sorteio, o corte e o recurso. Só a conferência da tela não
traz.

## Por que o guardião não pegou

`interface/revisao.py` promete, na abertura, que *"uma coleção nova aparece na Revisão porque está no
snapshot, e não porque foi lembrada"*. O guardião é
`test_toda_colecao_do_snapshot_esta_declarada_na_conferencia`
(`tests/unit/interface/test_revisao.py`), e ele compara **só as coleções-raiz que são listas de
entidades com `id`**. Dois formatos escapam dele por construção:

| O que escapa | Onde mora no snapshot | Por que o guardião não vê |
|---|---|---|
| Método comum do sorteio | `drawMethod`, na raiz | é um dicionário, e não uma lista |
| Marcos, com corte, recurso e método próprio | `profiles[].classificationMilestones` | é coleção **aninhada** no Perfil |
| Fatos exigidos do candidato | `profiles[].declaredFacts` | idem |

E a leitura do Perfil (`_perfil`, no mesmo arquivo) também é escrita à mão: ela lê vagas, quadro,
cadastro reserva, localidade, requisitos e Modalidades, e **não** lê `callForm` (como a convocação é
comunicada), `vacancyReversion` (a reversão de vaga reservada), descrição, carga horária,
remuneração nem atribuições. A reversão e a forma de comunicar são duas das declarações que mais
pesam na operação, e as duas se corrigem depois só por Retificação.

É a mesma classe de defeito que o arquivo diz ter feito desaparecer, uma camada abaixo: a raiz
passou a ser lida do snapshot, e o interior do Perfil continuou sendo lembrado.

## Por que importa no teste

A `D-G3` e a `035` dizem que o método do sorteio é norma publicada, e que alterá-lo depois exige
Retificação. Na Revisão, que é a última tela antes de submeter, quem elabora não o vê. No 28/2026 a
Classificação é a etapa em que a estimativa do [anexo A](reavaliacao-pos-consolidacao-2026-09-27/anexo-A-composicao.md)
mais oscila (~18 a ~72 interações). Se a pessoa do teste, na Revisão, voltar à Classificação para
conferir o que escreveu, a volta custa interações que a estimativa não previu, e o motivo dela é esta
lacuna, e não a carga cognitiva da etapa. O roteiro manda anotar a volta com o motivo, para que os
dois casos não se somem.

## O que não se decidiu aqui

- **Se a conferência deve mostrar o marco inteiro ou um resumo.** Num Edital de 16 Perfis são 16
  marcos. A dobra por Perfil que o RC-10 pede para as pendências vale também para a conferência.
- **Se o guardião passa a descer nos Perfis.** A alternativa é declarar, ao lado de `COLECOES`, as
  chaves do Perfil que a leitura cobre, e comparar com as chaves do Perfil no snapshot.

Nada foi corrigido. Registro, não escopo.

---

## A correção (27/09)

**O requisito.** A `FR-042` da [`006`](../specs/006-elaboracao-completa-edital/spec.md): *"A Revisão
DEVE consolidar o que está pronto e o que está pendente"*. O bloco *"O que será congelado"* é a metade
"o que está pronto", e nasceu no `006.1` como correção da própria `006` — *"cada item aqui viola um FR
da própria 006"* —, com a promessa de completude que este achado mostrou quebrada. A `FR-326` da `027`
pede o bloco por Perfil. Nenhum requisito novo.

**O que a Revisão passou a mostrar** (`backend/processo_seletivo/interface/revisao.py`):

- **Um bloco "Classificação"**, que volta para a etapa `classificacao`, entre Etapas e Documentos. Ele
  traz o método comum do sorteio e os marcos, com ordem, combinação, arredondamento, sorteio, Etapa que
  habilita ao sorteio, recurso, corte, empate na última posição, continuação e critérios de desempate.
  **As frases são as do documento**: a Revisão importa de `publicacoes/infrastructure/pdf.py` as
  mesmas funções que o PDF usa (`_combinacao`, `_regra_de_corte`, `_janela_recursal`…). O silêncio
  aparece como silêncio: *"Recurso: nada declarado"*, *"Corte: este marco não corta"*.
- **Marcos agrupados.** Marcos que declaram a mesma coisa aparecem uma vez, com os Perfis a que se
  aplicam. A denominação derivada do Perfil não separa grupos, e sai *"Classificação final — o nome de
  cada Perfil"*. O grupo mais numeroso é a referência, e cada outro abre com *"Diverge do marco de 3
  Perfis em: Recurso e Corte."*, em destaque. A comparação é por posição do marco no Perfil: o 1º
  marco de um Perfil se compara com o 1º dos outros.
- **Os Perfis sem marco**, nomeados no mesmo bloco.
- **No Perfil**: descrição, carga horária, remuneração, atribuições, vigência e descrição da
  Modalidade, qual é a ampla concorrência, a reversão, a forma de comunicar a convocação e os fatos
  exigidos, com código e tipo. **No Evento**: o local e a marca do período de inscrições. **Na
  Identificação**: o Processo e o teto de inscrições por candidato.

**Qual das duas alternativas acima foi tomada.** O guardião passou a descer, e não a declarar chaves
do Perfil ao lado. A declaração é **campo a campo** (`LIDOS` e `NAO_MOSTRADOS`, este com a razão de
cada exclusão), na grafia `(coleção, caminho)` do contrato de mutabilidade. Dois guardiões a prendem,
em `backend/tests/unit/interface/test_revisao.py`:

- **contra o `CONTRATO`**, sem banco. A `026` já prende o contrato ao snapshot, falhando por omissão
  nos dois sentidos. Um campo novo reprova lá até ser classificado, e aqui até ter destino;
- **contra o snapshot** de um Edital máximo publicado, pela travessia da `026`, que desce em
  dicionário da raiz e em coleção aninhada. Se o contrato envelhecer, este acusa sozinho.

Um terceiro teste confere que a declaração não mente: todo valor em prosa de um campo declarado como
lido aparece, literal, na tela. Os três foram vistos falhando: com `callForm` fora de `LIDOS`, os
dois guardiões o nomeiam; com a carga horária fora da leitura, o terceiro a nomeia.

**Verificado no navegador** sobre um Edital em elaboração com cinco Perfis, sorteio comum e corte: três
Perfis agrupados num item, o quarto com *"Diverge do marco de 3 Perfis em: Recurso e Corte."*, o quinto
em *"Sem marco classificatório"*. A verificação achou dois defeitos da primeira versão, que foram
corrigidos e têm teste. O primeiro era *"Sorteio — Quando: —"* em todo marco que referencia o método
comum: o PDF devolve `"—"` para o instante vazio, e o filtro o tomava por valor. O segundo era a
concordância no singular de *"não produz ordem"*.

### O que a correção não alcança

- **A confirmação da Retificação não passa por aqui.** Ela mostra o que muda (*"Conteúdo que passará
  a vigorar"*, uma linha por alteração, pelo dicionário do [RC-111](achado-o-que-mudou-cala-campos-retificaveis.md)),
  e não o Edital inteiro. A correção não chega a ela, e não precisa chegar do mesmo jeito. A
  **prévia do alcance** da `DP-17` — "aplicar a todos" na Retificação — é trabalho da spec do passo 1.
- **A Revisão de um Edital já publicado é a mesma tela**, em leitura, e a correção vale para ela. Mas
  ela lê `edital_snapshot`, que vem das tabelas relacionais, e a Retificação não reescreve essas
  tabelas. Num Edital publicado **e retificado**, a Revisão mostra o conteúdo do dia da publicação, e
  não o vigente. É anterior a este achado, e não foi tocado.
- **O documento cala parte do que a Revisão agora mostra**: o empate na última posição, a continuação
  do corte e a Etapa que habilita ao sorteio. Ver o
  [achado do documento](achado-documento-cala-parte-do-corte.md).
