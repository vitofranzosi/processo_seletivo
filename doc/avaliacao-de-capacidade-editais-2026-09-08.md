# Avaliação de capacidade — os sete Editais contra a `main` pós-020

Releitura do repositório em `2910c06` — `main` com a `020` (Anexos do Edital) integrada — contra a
mesma amostra de sete Editais reais do Ifes/Cefor lida em
[`avaliacao-de-capacidade-editais-2026-09-07.md`](avaliacao-de-capacidade-editais-2026-09-07.md),
que mediu o estado em `368d9cd`.

**Este documento não relê os Editais.** A leitura daquele documento permanece válida como leitura,
e as perguntas P-1 a P-9 continuam sendo as de
[`achados-editais-externos.md`](achados-editais-externos.md). O que mudou foi o repositório, e é o
repositório que se remede aqui: cada lacuna é conferida de novo no código, com a linha.

## Veredito

**Uma das seis lacunas sem endereço fechou — e era uma das três de autoria. A condução
está exatamente onde estava.**

A `020` entregou L-5 inteira. O efeito não é de acabamento: antes dela, **nenhum dos seis Editais
no alvo do produto era publicável inteiro**, porque todos os seis têm anexos e o sistema não tinha
onde escrevê-los. Depois dela são três.

```
autoria — documento publicável inteiro    antes  0 de 6      agora  3 de 6
condução — tem como produzir resultado    antes  2 de 7      agora  2 de 7
```

Os três que continuam impublicáveis — 57, 28 e 173 — estão presos a **uma lacuna só**, a L-1, e é
a mesma para os três: o quadro de vagas por modalidade. A condução não se moveu um passo porque
nada do que a bloqueia foi tocado: o sorteio continua inexistente, e com ele quatro dos sete.

## O que a 020 fechou — estado verificado

L-5 dizia: *"o catálogo de Seções é declarado, fixo, com onze entradas e nenhuma delas anexo"*, e
que *"o sistema sabe exigir o documento e não sabe publicar o formulário que o candidato precisa
preencher para produzi-lo"*. As duas frases deixaram de ser verdadeiras.

| O que L-5 pedia | Onde está hoje |
|---|---|
| identidade normativa do anexo, separada dos bytes | `AnexoEdital` e `ArtefatoAnexo` (`editais/models/anexos.py:24,69`); `congelado_em` nulo é rascunho substituível, não nulo é publicado e imutável (`:56`) |
| o anexo dentro do conteúdo publicado | `attachments` na raiz do snapshot (`publicacoes/application/publish_edital.py:233,237`), com `artifactId` e `artifactHash` por item |
| o vínculo com o requisito que manda usá-lo | `DocumentoExigido.anexo` (`editais/models/documentos.py:52`) e `attachmentId` no snapshot (`publish_edital.py:280`) |
| seção "Anexos" no documento | entrada nova do catálogo, que passou de onze para doze seções — `GERADA` a partir de `attachments`, ordem 11 (`editais/domain/secoes.py:150`) —, e seção própria no PDF (`publicacoes/infrastructure/pdf.py:1630`) |
| retificar a coleção por identidade | `/attachments` declarada como coleção endereçável (`publicacoes/domain/colecoes.py:46`) — acrescentar, substituir artefato, rotular, reordenar e remover |
| degrau de versão sem tornar o acervo irretificável | `SCHEMA_VERSION = 9` (`shared/canonical.py:84`) e a conversão 8 → 9 (`publicacoes/domain/elevacao.py:69`) |
| o candidato baixar o modelo | rota pública por artefato (`publicacoes/api/public_urls.py:42`) e a lista na página da seleção (`portal/views.py:115`) |
| a banca abrir o modelo que estava valendo | mesa da inscrição (`interface/templates/interface/mesa_inscricao.html`) |
| o autor compor a coleção | etapa "Anexos" da elaboração (`interface/views.py:512,650`) |

**E o que ela recusou, de propósito.** O anexo é arquivo, e o sistema nunca lê o que há dentro: a
ficha de avaliação do 14/2026 e a do 173/2025 **passam a ser publicáveis** como conteúdo normativo
binário, e o barema que elas descrevem continua sem existir como estrutura que alguém consuma
(D-4 da `015`). A autopontuação vinculante do 173 (P-7) segue fora. Publicar a ficha e executar a
ficha são duas coisas, e só a primeira foi feita.

## Por Edital

| Edital | Autoria em 07/09 | Autoria hoje | Condução — sem mudança |
|---|---|---|---|
| **77/2026** FIC, vagas remanescentes | faltavam 3 anexos | **publicável inteiro** | bloqueada: sorteio |
| **14/2026** Orientador de TFC | faltavam 6 anexos, com as duas fichas | **publicável inteiro** | o mais próximo; para nos mesmos 4 pontos |
| **76/2026** Secretaria Escolar, CR | faltavam anexos | **publicável**, menos a coluna LOCAL (L-6) | bloqueada: sorteio; inscrição no SIGAA (P-8) |
| **57/2026** unificado, 2 cursos | quadro (L-1) + 6 anexos | **não** — resta L-1 | sorteio + heteroidentificação (L-2) + 2ª instância |
| **28/2026** Informática na Educação | quadro (L-1) + anexos | **não** — resta L-1 | sorteio |
| **173/2025** Designer Educacional | quadro (L-1) + 9 anexos | **não** — resta L-1 | vai até a lista publicada |
| **46/2026** técnicos integrados | fora do alvo do produto por decisão | | |

**O 14/2026 continua sendo a medida da distância.** Ele passou a ser publicável inteiro, e para
nos mesmos quatro pontos de 07/09, nenhum deles tocado: o corte de dez por código para a entrevista
(014), a cascata Grupo 1 → 2 → 3 na convocação (016/019), o terceiro critério de desempate (L-4) e
o barema das duas fichas (D-4).

**O 77/2026 publica validade de seis meses** e o `Edital` continua sem prazo de validade
(`processos/models.py:35`, P-3). Isso não o torna impublicável — a validade cabe em seção textual,
como cabia em 07/09 —, mas o que fica publicado é prosa que nada consome, e é assim que o 14 e o
173 publicam os seus dois anos.

## As cinco lacunas de 07/09 que continuam abertas

Conferidas de novo hoje, uma por uma.

| Lacuna | Estado verificado em `2910c06` |
|---|---|
| **L-1** quadro de vagas por modalidade | `ModalidadeConcorrencia` (`editais/models/perfis.py:56`) segue com `code`, `name` e `description`; `RegraNormativa.percentage` (`:209`) segue sendo um decimal só, e `PerfilVaga.immediate_vacancies` (`:21`) segue guardando o total do Perfil, não a repartição. É o único bloqueio de autoria de 57, 28 e 173 |
| **L-2** aplicabilidade da Etapa | `EtapaAvaliacao` (`editais/models/etapas.py:11`) continua sendo do Edital e alcançando todos os Perfis; a docstring segue dizendo que mover a coleção custa uma migration "quando houver um Edital real que precise disso". A heteroidentificação de 57, 28, 173 e 46 é esse Edital |
| **L-3** parcela nomeada de Etapa no desempate | `CriterioDesempate.MAIOR_PONTUACAO_NA_ETAPA` (`editais/models/perfis.py:176`) endereça a Etapa inteira, e `Avaliacao.pontuacao` (`avaliacoes/models.py:109`) continua sendo um número só |
| **L-4** fato que não é número nem data | `FatoDeclarado.Tipo` (`editais/models/perfis.py:89`) ainda tem `DATA` e `INTEIRO`, e a docstring ainda diz que *"o terceiro entra quando aparecer o Edital que o exija"*. Ele apareceu — 14/2026, 9.2(c) — e continua sem grafia |
| **L-6** local do evento | `EventoCronograma` (`editais/models/cronograma.py:17`) tem tipo, descrição, datas, ordem e status. Local, não. É o que o 76 publica em coluna própria |

E as de 07/09 que têm endereço em feature futura, todas no mesmo lugar em que estavam: **sorteio**
(inexistente, e é o bloqueio de maior alcance — 4 dos 7); **corte e progressão** (014);
**convocação e suplência** (019); **ocupação de vagas e concorrência entre modalidades** (016) — o
snapshot continua carregando `percentage`, `distribution` e `callRules`
(`publish_edital.py:112-122`) sem que nada além das telas de composição os leia;
**heteroidentificação**; **impugnação por quem não é candidato** (`Recurso.inscricao` segue
obrigatório, `recursos/models.py:46`); e **segunda instância recursal**.

`specs/` vai de `018` direto para `020`: 014, 016 e 019 continuam sendo números citados, sem spec.

## O que a 020 acrescentou às pressões já registradas

A pressão sobre o limite de arquivo **ganhou um segundo caso**. A `020` repetiu para os bytes que
a instituição publica a decisão que a `009` tomou para os do candidato — *"um Edital não negocia
tamanho de arquivo"* —, e agora são dois limites de aplicação: 10 MB para o arquivo do candidato e
5 MB para o anexo (`config/settings/base.py:139` e `:147`). O conflito com a amostra continua sendo
o do primeiro — três Editais publicam 7 MB, dois publicam 10 MB, e dois publicam ainda um limite de
50 páginas que não tem grafia nenhuma no sistema. O que mudou é que a decisão contestada passou a
valer em dois lugares em vez de um.

As outras duas pressões de 07/09 seguem intactas e sem novidade: a terceira dimensão do
`DocumentoExigido` — condição sobre a pessoa, do tipo "reservista, no caso de candidatos do sexo
masculino maiores de 18 anos" — e o custo de autoria da modalidade que é do Perfil.

## O resíduo da própria 020

Um, registrado no dia seguinte à integração e conferido aqui:
[`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md). A página pública lista os
anexos e não diz a quem cada um serve — o que é modelo de requisito, o que está à disposição e o
que talvez tenha ficado sem vínculo por esquecimento se parecem na tela. **Não é defeito**: as
quatro combinações são legítimas e a `020` entregou o que FR-039 pede. Fica anotado porque a
decisão de dizer algo ali é de conteúdo publicado, e portanto tem preço de degrau.

## Onde as lacunas incidem, agora

| Lacuna | Linhagem | Estado |
|---|---|---|
| L-5 anexos | autoria do Edital; toca `DocumentoExigido` | **fechada pela `020`** |
| L-1 quadro de vagas por modalidade | autoria do Edital (006/008), **antes** da 016 | aberta — bloqueia 3 dos 6 |
| L-2 aplicabilidade da Etapa | autoria do Edital; precondição da heteroidentificação | aberta |
| L-3 parcela de Etapa no desempate | mesma estrutura do barema (D-4 da `015`) | aberta |
| L-4 fato sem grandeza | `FatoDeclarado` e `CriterioDesempate`, ambos da `015` | aberta |
| L-6 local do evento | Cronograma | aberta |

O achado principal de 07/09 era que **três das seis lacunas novas eram de autoria, e nenhuma delas
dependia da 014, 016 ou 019 para existir**. A `020` provou a leitura: fechou uma das três sem
tocar em nada da fila de execução, e o efeito foi metade dos Editais no alvo passarem a ser
publicáveis. Restam duas — L-1 e L-2 —, e a primeira é a que decide se 57, 28 e 173 podem sequer
existir como documento.
