# Auditoria de UX — a experiência de Retificar um Edital

05/11/2026, sobre a `main` em `f092aaf8`. Diagnóstico pedido antes de qualquer spec: **nada foi
implementado**, nenhum dado institucional foi tocado, e as Retificações criadas no percurso vivem
num banco descartável (`ps_retif_ux`).

Marcas usadas: **[C]** confirmado no navegador ou no código; **[H]** hipótese sem evidência
suficiente; **[N]** hipótese testada e não reproduzida. Contagem de ações e alturas são **medidas do
roteiro automatizado** (`roteiro-de-captura.py`), não de pessoas reais.

> **Não vira escopo por estar escrito aqui.** As recomendações são insumo para decisão. As quatro
> perguntas da seção 9 são do produto, e o relatório não as responde.

---

## 1. Resumo executivo

**A hipótese de partida está metade certa.** O GPS **não** reabre o editor de elaboração para
retificar. A Retificação tem tela própria (`interface/retificacao.py`, `retificar.html`) e trabalha
por diferença: só vira Alteração Normativa o campo que a pessoa mudou, e o resto não é tocado [C].
Também já existe boa parte do que a proposta sugeria: índice "Ir para", busca "Encontrar", marca
"alterada" campo a campo, barra fixa com contagem e uma tabela "Vigente hoje × Passará a ser"
antes de criar o ato. Tudo isso foi entregue pelas specs 026, 048, 051, 056 e 103.

**O que se confirma é o modelo orientado ao documento.** A tela desenha o Edital inteiro como
formulário aberto:

- Edital de demonstração (2 Perfis, 3 Eventos): **14.852 px**, 41 cartões e 180 campos. São 16,5
  telas a 1280×900 e 34 telas a 375 px.
- Edital ampliado ao porte dos Editais 57 e 59/2026 (4 Perfis, 11 Eventos): **26.517 px**, 73
  cartões, 364 campos e 29,5 telas. O Cronograma só começa a 15.804 px.

E as ajudas de orientação falham justamente onde o operador precisa delas:

1. **A busca só lê o nome do cartão**, e não o rótulo nem o valor dos campos. «vagas»,
   «remuneração» e «prazo» (recursal) não acham o campo. «requisito» acha a Seção «Requisitos
   gerais», que está vazia, e não os Requisitos de participação do Perfil [C].
2. **A conferência apaga a memória do formulário.** Depois de «Ver o que vai mudar», a marca
   «alterada» some de todos os cartões («Nada alterado desde a conferência»), e as linhas da tabela
   não levam de volta ao campo [C].
3. **A recusa chega no último clique.** A incoerência entre as vagas do Perfil e o quadro só
   aparece em «Criar Retificação». A conferência não a mostra, e a mensagem não leva à linha do
   quadro [C].
4. **«Vigente hoje» mostra o que ainda não vigora.** Com uma Retificação publicada de vigência
   futura, a coluna exibe o término 05/12, quando o que vigora hoje é 25/11 [C].
5. **Quem homologa lê outro vocabulário.** A mesma alteração aparece como «Evento 1 — Inscrições ·
   Término» para quem elabora e como «Evento do cronograma “Inscrições pelo sistema, com isenção…”
   · REPLACE · `/schedule/id=…/endAt`» para quem homologa, e sem o contexto ao redor [C].
6. **Nada confere a consequência.** Uma prorrogação que termina as inscrições **depois** da Prova
   objetiva foi criada, submetida e chegou à homologação sem aviso. O domínio declara essa coerência
   uma "decisão normativa que ninguém tomou" (`editais/domain/validation.py:20-22`) [C].

**Recomendação.** Não construir um segundo editor nem uma entrada obrigatória "O que você precisa
retificar?". A maior parte do problema se resolve **dentro da tela atual**, com quatro mudanças
pequenas, todas reaproveitando código que já existe:

- busca por rótulo e valor;
- caminho de volta da conferência ao campo, com a marca preservada;
- achados da criação já na conferência;
- rótulo honesto da versão base.

Depois disso vêm o vocabulário único entre elaboração, homologação e portal, e o contexto na
homologação. Os cartões recolhidos e a entrada por assunto só entram se uma medição depois do MVP
mostrar que o tamanho ainda pesa.

---

## 2. O fluxo atual

```
Detalhe do Edital ──«Retificar»──► Retificar (tela única, Edital inteiro aberto)
                                    │  Ir para · Encontrar · Só o que eu alterei
                                    │  edita campos / Remover do Edital / Acrescentar …
                                    ├─«Ver o que vai mudar» (POST, recarrega no topo)
                                    │     tabela Onde · Campo · Vigente hoje · Passará a ser
                                    └─«Criar Retificação» (exige Justificativa, no fim da página)
                                          │  aqui roda a conferência do conteúdo (impeditivos)
                                          ▼
                     Detalhe da Retificação — EM_ELABORACAO
                        «Editar a Retificação» (mesma tela, sobre o proposto) · «Submeter»
                                          ▼ confirmar (sem a tabela do que se submete)
                     EM_REVISAO ── Homologador: «Homologar» | «Devolver para elaboração» (motivo)
                                          ▼ confirmar (tabela Onde · Antes · Depois, avisos)
                     HOMOLOGADA ── Publicador: «Publicar» (signatário; tabela; irreversível)
                                          ▼
                     PUBLICADA — o PDF oficial é o Edital consolidado, com a frase
                                 "Versão consolidada… retificado em …"
```

O que se confirmou em cada passo [C]:

| Passo | Tela | O que se confirmou |
|---|---|---|
| Entrar | `detalhe.html` → `retificar` | «Retificar» no cartão "O que fazer agora". Com Retificação em curso, um cartão a lista com o próximo ato (103). |
| Primeira tela | `retificar.html` | Aviso de Retificação em curso, «Como funciona», índice, busca e então os cartões. O 1º campo editável fica abaixo da dobra a 375 px (cap. M1). |
| Localizar | âncoras do índice e filtro JS (`retificacao.js`) | Índice só por seção, no topo e sem acompanhar a rolagem; filtro só pelo nome do cartão. |
| Editar | `_retificacao_linha.html` | Borda verde e a palavra «alterada» na legenda; contagem na barra fixa. |
| Conferir | mesmo template, POST sem `confirmar` | Tabela antes/depois no topo; a página volta rolada para o topo; as marcas zeram. |
| Criar | POST `confirmar=1` | Justificativa obrigatória; impeditivos só aqui. |
| Submeter | `retificacao_confirmar.html` | Passagem de bastão, sem a lista do que se submete. |
| Homologar | idem | Lista de alterações (104), avisos anteriores recolhidos e fundamento obrigatório. |
| Publicar | idem | Signatário, lista e consequências irreversíveis. Não há prévia do documento que será publicado (nada em `urls.py` nem nos templates). |

**Quem acha a Retificação** [C]: o homologador a vê na tela inicial ("Ações disponíveis para você →
Analisar a Retificação", cap. F2), na lista de Editais e no detalhe do Edital. O achado AUD-RET-01
de 29/10 está resolvido, e nada aqui o reabre.

---

## 3. Inventário de problemas

Gravidade: **A** pode produzir ato errado ou retrabalho; **M** atrasa ou confunde sem risco
normativo direto; **B** é polimento. Esforço: **P** até um dia, **M** alguns dias, **G** uma spec
inteira.

| # | Problema | Evidência | Grav. | Esforço |
|---|---|---|---|---|
| RU-01 | **A busca não lê rótulo nem valor.** `aplicar()` compara só `data-nome`, o nome do cartão (`retificacao.js:185`). «vagas» → 0; «remunera» → 0; «prazo» → só «Seção Prazo de validade»; «requisito» → «Seção Requisitos gerais», que está vazia. Além disso, `data-nome` diverge da legenda: «Linha do quadro» contra «LINHA DO QUADRO DE VAGAS». | cap. B1, C1; `medidas.json` | A | P |
| RU-02 | **A conferência zera a marca de alterado.** Depois do POST, o digitado vira o valor de comparação: 0 cartões marcados, «Só o que eu alterei» não acha nada, e a página volta ao topo (rolagem 0). As linhas de «O que vai mudar» não têm link, embora cada cartão já tenha `id="cartao-<ref>"` e os gestos da 051 já linkem («Ir ao cartão de origem»). | cap. D2, D3; console | A (retificação múltipla) | P |
| RU-03 | **Impeditivo só no clique final.** Vagas do Perfil 3→4 sem mexer no quadro: a conferência mostra uma linha e nenhum aviso; «Criar» recusa com "O quadro de vagas do Perfil 'DOC-INFO' soma 3…", sem link para a linha. Para chegar à linha é preciso saber que ela se chama "Linha do quadro", e a busca por «vagas» não a acha (RU-01). | cap. B3, B5 | M | M |
| RU-04 | **«Vigente hoje» mostra a última versão publicada, que pode não vigorar.** A Retificação nº 3 do demo vigora em 20/11; hoje (05/11) o término vigente é 25/11 21:38, e a tela mostra 05/12 21:38 em «Vigente hoje» e em «Antes» na homologação. A causa é o nome: `_versao_vigente` devolve a de maior `valid_from` (`views.py:4377`). Compor sobre a última é coerente com as precondições; o rótulo é que afirma o que não é. O cartão "Documentos publicados" do Edital também não diz que a nº 3 ainda não vigora. | cap. A3, F5, G1 | A | P (rótulo) |
| RU-05 | **Coerência temporal não conferida.** Inscrições prorrogadas até 12/12 23:59 com a Prova objetiva em 10/12 21:38: Retificação criada, submetida e levada à homologação, sem aviso em ponto nenhum. A ausência é declarada no domínio como decisão pendente (`validation.py:20-22`). | cap. F5; banco | A | depende de **D1** |
| RU-06 | **Três vocabulários para a mesma alteração.** O resumo da elaboração (`retificacao.py`), a lista da gestão (`views._alteracoes_legiveis`, `views.py:4969`) e o portal (`publicacoes/domain/alteracoes.py`) traduzem por códigos distintos. Na gestão, o Evento é nomeado pela descrição; a coluna «Operação» diz `REPLACE`; o caminho JSON fica sempre à vista. A divergência dos rótulos já está registrada em `alteracoes.py:28-32`. | cap. F4, F5 × A3 | M | M |
| RU-07 | **Homologação sem contexto.** A lista diz o campo e os dois valores, e nada do entorno: os outros Eventos do Cronograma, o quadro do Perfil cujas vagas mudaram. Quem homologa precisa redescobrir o Edital para julgar a consequência, que é o caso do RU-05. | cap. F5 | M | M |
| RU-08 | **Tamanho e densidade.** A tela inteira é formulário aberto. Cada Marco ocupa ~950 px com 22 campos, 10 deles do sorteio. A seção Perfis custa ~3.600 px por Perfil. Medidas na seção 5. | cap. 03, E1 | M | M a G |
| RU-09 | **O índice não acompanha a rolagem e não desce ao Perfil.** Ele fica no alto da página; a seção «Perfis de Vaga» tem 14.459 px no Edital ampliado, e não há salto direto ao 3º Perfil. | código (`telas.css:729`, sem `sticky`) | M | P |
| RU-09b | **Conferir pelo topo, editar pelo meio.** «Ver o que vai mudar» devolve a página no topo; a Justificativa, exigida para criar, fica no fim (14.769 px no demo; 26.047 px no ampliado). A barra fixa ajuda a enviar, e não a voltar ao ponto em que se estava. | `medidas.json` | B | P |
| RU-10 | **Submeter sem ver o que se submete.** A confirmação de «Submeter» traz bastão e consequências, mas não a lista que a de homologar já traz (104). | cap. F0 | B | P |
| RU-11 | **Sem prévia do documento oficial.** O PDF é o Edital consolidado e nasce na publicação (`retificacoes.py:1037`). Nenhuma das telas antes de publicar mostra o que vai sair. | código | M | M |
| RU-12 | **Conflito entre Retificações em curso só na publicação.** Duas em curso são permitidas, e o choque de conteúdo só aparece ao publicar, com a ordem de "refazer". A tela não reaponta a base; a API faz isso por `baseSnapshotId`. | código (relatório da arquitetura) | M | M; pendência da 103 |

### O que funciona e deve ser preservado [C]

- **Tela própria, por diferença.** O operador não reescreve o Edital: só o tocado vira Alteração, e o
  campo que volta ao valor anterior deixa de ser alteração.
- **«O que vai mudar» antes do ato**, com antes e depois em português, e «formnovalidate» para
  conferir sem precisar justificar.
- **A marca «alterada» como palavra**, além da cor (WCAG 1.4.1), e a contagem com `aria-live=polite`.
- **O filtro esconde, não remove.** O campo escondido continua sendo enviado.
- **«O que não se corrige por Retificação nesta seção»**: a razão normativa da ausência, uma vez por
  bloco.
- **«Acrescentar» dentro da seção** do que se acrescenta.
- **Bastão, segregação desabilitada com motivo, motivo da devolução e «Quem atuou»** (103 e 104).
- **Modo somente leitura** para quem não tem `retificacao:elaborar`.
- **Sem rolagem lateral a 375 px** (largura medida = 375).

---

## 4. Capturas comentadas

Todas estão em `capturas/`, a 1280×900 salvo indicação. O Edital é o 01/2026 do `seed_demo`.

| Captura | O que mostra |
|---|---|
| `02-retificar-primeira-dobra.jpg` | A primeira dobra: aviso, «Como funciona», índice e busca. O primeiro campo começa na borda da tela. |
| `03-regua-demo-1280.jpg` | **Régua**: a página inteira reduzida a 160 px de largura, 14.852 px de altura real. |
| `E1-regua-extenso-1280.jpg` | Régua do Edital ampliado: 26.517 px. |
| `A1-cronograma-pelo-indice.jpg` | Depois de «Cronograma» no índice: chega-se ao lugar, mas o índice fica para trás. |
| `A2-campo-alterado-com-selo.jpg` | O cartão do Evento com a marca «alterada»: o que funciona bem. |
| `A3-conferencia-o-que-vai-mudar.jpg` | «Vigente hoje 05/12/2026 21:38». Hoje vigora 25/11 (RU-04). |
| `B0-retificar-com-retificacao-em-curso.jpg` | A Retificação em curso anunciada antes de compor outra (103). |
| `B1-encontrar-vagas.jpg` | «vagas» → «Nenhuma linha corresponde» (RU-01). |
| `B5-recusa-so-no-criar.jpg` | O impeditivo do quadro, só depois de «Criar Retificação» (RU-03). |
| `C1-encontrar-requisito.jpg` | «requisito» → a Seção «Requisitos gerais», vazia; o requisito do Perfil fica de fora. |
| `D1-so-o-que-eu-alterei.jpg` | **Antes** de conferir, «Só o que eu alterei» reduz a página a 3 cartões (3.850 px): a ajuda funciona até o primeiro envio. |
| `D2-conferencia-multipla.jpg` | Três alterações em três seções: tabela correta, mas sem caminho de volta. |
| `D3-barra-depois-da-conferencia.jpg` | «Nada alterado desde a conferência» (RU-02). |
| `F0-confirmar-submeter.jpg` | Submeter sem a lista do que se submete (RU-10). |
| `F2-inicio-do-homologador.jpg` | O homologador encontra a Retificação na tela inicial. |
| `F4-detalhe-visto-pelo-homologador.jpg`, `F5-confirmar-homologar.jpg` | `REPLACE`, caminho JSON e o Evento nomeado pela descrição (RU-06); nenhum contexto (RU-07). |
| `G1-detalhe-do-edital-documentos.jpg` | Retificações nº 2 e nº 3; nada indica que a nº 3 só vigora em 20/11. |
| `M1-retificar-375.jpg` | A 375 px, a primeira dobra é só aviso. |

---

## 5. Os cenários

| Cenário | Objetivo | Caminho no roteiro (ações) | O que dificultou | Risco | Grav. |
|---|---|---|---|---|---|
| **A — Cronograma** | Prorrogar o término das inscrições | Cronograma no índice → Término → Ver o que vai mudar → Justificativa → Criar (**5**) | Pouco, neste Edital: 3 Eventos, nomeados pelo tipo. No ampliado, o Cronograma começa a 15.804 px. | «Vigente hoje» falso (RU-04); inscrição terminando depois da prova sem aviso (RU-05) | A |
| **B — Vagas** | Mais uma vaga num Perfil | Busca «vagas» (falha) → Perfis no índice → rolar até o Perfil → Vagas → Ver (sem aviso) → achar a linha do quadro → Ver (**6**, mais a recusa em B5) | Busca cega a campo; o quadro mora em outro cartão, recuado sob o Perfil; o impeditivo só no fim | Baixo: o servidor recusa | M |
| **C — Requisitos** | Acrescentar requisito a um Perfil; ver um Documento exigido | Busca «requisito» (acha a Seção errada) → busca pelo nome do Perfil → editar → busca «Diploma» → Ver (**5**) | Só se acha pelo nome do Perfil; o termo do assunto leva a uma Seção vazia | Médio: alterar a Seção do texto achando que é o requisito | M |
| **D — Múltipla** | Três campos em três seções | 3 edições → «Só o que eu alterei» → Ver (**5**) | Antes de conferir, o filtro funciona (cap. D1). **Depois de conferir, a marca some**, e a tabela não leva de volta. | Médio: esquecer ou desfazer uma alteração ao corrigir outra | A |
| **E — Edital extenso** | Navegar no porte real | Render do conteúdo do demo com 4 Perfis e 11 Eventos (`renderizar-edital-extenso.py`) | 26.517 px a 1280 e 51.109 px a 375 (63 telas); seção Perfis com 14.459 px | Proporcional ao tamanho | M |
| **F — Homologação** | Decidir homologar ou devolver | Tela inicial → Analisar a Retificação → Homologar (**1** depois de achar) | Outro vocabulário; `REPLACE`; sem contexto. Neste caso, a inscrição depois da prova passou sem nada que a mostrasse. | A decisão sai sobre uma linha isolada | A |
| **G — Sucessivas** | Retificar um Edital já retificado duas vezes | Detalhe do Edital → Retificar | A base é a última versão publicada (correto), chamada de "vigente" (incorreto); o detalhe do Edital não distingue "vigora" de "vigorará" | Ler como em vigor o que ainda não está | A |

**Dimensões, Edital de demonstração** (01/2026, 2 Perfis, 3 Eventos, 3 Etapas, 3 Documentos,
2 Anexos, 17 Seções):

| Seção | Altura a 1280 px |
|---|---|
| Identificação | 396 |
| Perfis de Vaga (12 cartões) | 5.397 |
| Cronograma | 991 |
| Etapas | 1.173 |
| Documentos | 1.296 |
| Anexos | 540 |
| Seções do texto (17) | 4.143 |
| **Página** | **14.852** (27.420 a 375 px) |

**Edital ampliado** (4 Perfis com 2 Modalidades cada, 11 Eventos): Perfis 14.459, Cronograma
3.288, página **26.517** (51.109 a 375 px). É conservador: o 57/2026 tem quadros com três
modalidades (AC, PcD, PPI).

**Retificações reais** como indício de frequência: dos onze Editais institucionais com
"retificado" no nome, na amostra em `~/Downloads`, o único que marca o que mudou é o 59/2026, e
marca «ANEXO I – CRONOGRAMA (RETIFICADO)». Os demais saem consolidados e sem marca, como o próprio
GPS publicou o 72/2026 ("Versão consolidada. Publicado em 27 de outubro…; retificado em 29 de
outubro…"). É indício, não estatística: não há base para dizer qual assunto se retifica mais.

---

## 6. Arquitetura: restrições e o que se reaproveita

Resumo da leitura do código (detalhes e linhas no histórico desta auditoria):

- **Estados** (`publicacoes/models_retificacao.py:37-42`): `EM_ELABORACAO`, `EM_REVISAO`,
  `HOMOLOGADA`, `PUBLICADA`, `CANCELADA`. "Devolvida" é `EM_ELABORACAO` com `return_reason`.
- **Permissões**: `retificacao:elaborar`, `:submeter`, `:homologar` (que também devolve),
  `:publicar` e `:cancelar`. A única segregação imposta é a da publicação: quem submeteu **e**
  homologou não publica (`retificacoes.py:1008`).
- **O que se guarda**: `AlteracaoNormativa` com caminho JSON Pointer por identidade (`id=<uuid>`),
  operação, valor novo e **hash** do anterior. **O valor anterior não é guardado**: o "antes" se
  recalcula da `base_snapshot` a cada leitura. Por isso o "antes" é sempre o da base, e não o do
  dia, o que é o fundo do RU-04.
- **O documento oficial** é o Edital consolidado, sem "onde se lê, leia-se" (`pdf.py:1185-1203`).
  A Justificativa não entra nele [H, por busca textual].
- **Conferência do conteúdo**: `editais/domain/validation.py` já calcula os achados (impeditivos e
  advertências) sobre o conteúdo que a Retificação produziria, e a criação os usa. A tela de
  composição não os chama na conferência (RU-03).
- **Contrato de mutabilidade** (`editais/domain/mutabilidade.py`): retificável, não retificável (com
  razão), derivado ou estrutural. A tela já lê o contrato para dizer o que não se corrige.

**Reaproveitável sem arquitetura nova:**

| Peça | Serve a |
|---|---|
| `id="cartao-<ref>"` em cada cartão, e o padrão «Ir ao cartão de origem» da 051 | RU-02: link de cada linha do resumo ao cartão |
| `resumo` do servidor, que já sabe quais referências mudaram | RU-02: marcar os cartões alterados depois da conferência |
| Rótulos de campo já no HTML (`<label>`) e valores nos controles | RU-01: busca por rótulo e valor, só em `retificacao.js` |
| Achados que a criação calcula (`validation.py`) | RU-03: mostrar na conferência, com o caminho de cada achado ligado ao cartão |
| `base.valid_from` e `effective_version(at=agora)` | RU-04: dizer qual versão é a base e se ela já vigora |
| Um só tradutor de caminho (o de `alteracoes.py` cobre o contrato inteiro desde 27/09) | RU-06 |
| `aplicar(base, alteracoes)`, já usado na edição (`views.py:4727`) | RU-07: desenhar a coleção afetada, proposta |

**O que não é necessário:** novo modelo de versionamento, histórico campo a campo, segundo editor.
Nada nos achados pede isso.

---

## 7. As alternativas

| Alternativa | O que resolve | Limite | Custo | Veredito |
|---|---|---|---|---|
| **A — Melhorar o editor existente** (busca por campo, índice fixo com Perfis, marcas persistentes, links do resumo) | RU-01, 02, 09 e parte do 08 | Não reduz o tamanho; reduz o custo de atravessá-lo | P a M | **Fazer, como MVP** |
| **B — Entrada orientada à tarefa** ("o que você precisa retificar?" antes do Edital) | Orientação para quem chega sem saber onde está o dado | Mais um passo para todos; ruim para a múltipla (D); duplica o índice e a busca, que já existem | M | **Não agora.** A busca da A faz o papel dela sem passo obrigatório. |
| **C — Retificação contextual** (recorte do Edital em torno do alvo; cartões recolhidos) | RU-08 | Recolher esconde o que não se vê; exige marca de "tem alteração aqui" e de "tem achado aqui" para não esconder trabalho | M | **Depois do MVP, se medido.** Começar pelo grupo do sorteio no Marco: 10 dos 22 campos do cartão. |
| **D — Revisão consolidada** (mesma lista para elaborador, homologador e publicador, com contexto) | RU-06, 07, 10 e parte do 05 | Exige unificar os tradutores | M | **Fazer, como segunda etapa** |
| **E — Híbrida** | Tudo, aos poucos | — | — | É a recomendação: A + D, e C se a medição pedir |

---

## 8. A experiência proposta

Maquete: `maquetes/mvp-retificacao.html`, renderizada em `maquetes/mvp-retificacao.jpg`. Ela usa
os dados do demo e destaca em tracejado o que é novo.

| Etapa | Objetivo | Muda | Reaproveita | Editor completo |
|---|---|---|---|---|
| **Iniciar** | Saber se já há Retificação em curso e começar | Nada | Cartão da 103 | — |
| **Localizar** | Achar o campo pelo nome do assunto | Busca lê rótulo, valor e nome do cartão, e lista os campos encontrados com «Ir ao campo». Índice fixo ao lado, com um nível por Perfil e a contagem do que já foi alterado. | `retificacao.js`, `nav.indice`, âncoras | A tela continua sendo o Edital inteiro: nada se esconde |
| **Editar** | Mudar sem perder o lugar | Nada além da marca, que já existe | `_retificacao_linha.html` | — |
| **Conferir** | Ver o efeito e os problemas antes do ato | Cada linha do resumo com «Ir ao campo»; marca «alterada» preservada depois do POST; achados impeditivos e advertências da criação já aqui, cada um com link; a base nomeada como "última versão publicada", dizendo quando ela vigora | `resumo`, `validation.py`, `effective_version` | — |
| **Encaminhar** | Saber o que se entrega | A confirmação de Submeter com a mesma lista | `_alteracoes_legiveis` | — |
| **Homologar** | Julgar a consequência | O mesmo vocabulário da elaboração; operação e caminho em "Detalhe técnico"; a coleção afetada desenhada com a alteração (o Cronograma inteiro, o quadro do Perfil) | `aplicar()`, um tradutor | — |
| **Publicar** | Assinar sabendo o que sai | Prévia do documento consolidado, se for decidida | `render_edital_pdf` | — |

**Prevenção de erro.** O impeditivo deixa de chegar no último clique (RU-03). A advertência
temporal (RU-05) só entra com a decisão D1. A marca persistente impede "esquecer o que já mexi"
(RU-02).

---

## 9. Plano incremental

**MVP: uma spec pequena, só interface, sem migration.**

| | Mudança | Critério de aceitação preliminar |
|---|---|---|
| M1 | Busca por rótulo, valor e nome (RU-01) | «vagas» encontra o campo do Perfil e as linhas do quadro; «remuneração» encontra o campo; «prazo» encontra o prazo recursal do Marco; o filtro continua escondendo sem remover do envio. |
| M2 | Caminho de volta e marca persistente (RU-02) | Depois de «Ver o que vai mudar», todo cartão com alteração no ato traz «alterada»; «Só o que eu alterei» os acha; cada linha do resumo leva ao cartão. |
| M3 | Base nomeada com honestidade (RU-04) | Com Retificação publicada de vigência futura, a coluna não se chama "Vigente hoje" e a tela diz quando a base passa a vigorar; o mesmo vale para "Antes" na homologação e na publicação. |
| M4 | Achados na conferência (RU-03) | O impeditivo do quadro aparece em «Ver o que vai mudar», com link à linha, antes de «Criar». |

**Depois do MVP:**

| | Mudança |
|---|---|
| P1 | Vocabulário único entre elaboração, gestão e portal; `REPLACE` e caminho em "Detalhe técnico" (RU-06) |
| P2 | Índice fixo com nível por Perfil (RU-09); Submeter com a lista (RU-10) |
| P3 | Contexto na homologação: a coleção afetada, proposta (RU-07) |
| P4 | Medir de novo a régua e o cenário E; só então avaliar cartões recolhidos (RU-08) |

**Não fazer agora:**

- segundo editor;
- passo obrigatório de assunto;
- histórico campo a campo;
- "onde se lê, leia-se" no PDF, que é decisão normativa;
- mudar o que conta como base da composição (compor sobre a última publicada está certo, e o defeito
  é o nome).

**Decisões que são do produto, e que o relatório não toma:**

- **D1.** Inscrição que termina depois de um Evento posterior, ou término antes do início: advertir
  na Retificação? impedir? Hoje nada é conferido, por decisão declarada. Sem resposta, RU-05 fica
  como está.
- **D2.** Ao retificar sobre uma versão de vigência futura, o "antes" que se mostra é o da base ou
  o de hoje? (M3 resolve o rótulo; D2 decide se a tela mostra os dois.)
- **D3.** Prévia do documento consolidado antes de publicar (RU-11): sim ou não?
- **D4.** Reapontar a base pela tela quando outra Retificação publica no intervalo (RU-12):
  pendência já registrada na 103.

---

## 10. Recomendação para SDD

- **Uma spec para o MVP (M1–M4).** É interface sobre peças existentes, testável por cliente HTTP
  (M2, M3, M4) e por navegador (M1 e a marca de M2, no grupo `navegador`, como as jornadas da 107).
  Os cenários A–D deste relatório servem de critério de aceitação.
- **Uma segunda spec para P1 + P3** (vocabulário único e contexto), porque mexe em três tradutores
  e no portal.
- **D1 antes de qualquer spec que toque coerência de cronograma.** A FR que nascer dela é norma,
  não interface.

### As perguntas do pedido, respondidas

- **Por que o operador se perde?** Porque a tela é o Edital inteiro, aberto, e as ajudas leem a
  estrutura (seção, nome do cartão) em vez do vocabulário do operador (o campo, o valor). E as ajudas
  perdem o estado na conferência.
- **Extensão, navegação, arquitetura da informação ou combinação?** Combinação. A extensão multiplica;
  a navegação (busca por nome, índice no topo) e a arquitetura da informação (quadro em cartão
  separado do Perfil, Marco com 22 campos abertos) fazem a extensão pesar.
- **Exige conhecer a estrutura interna?** Sim, em dois pontos medidos: saber que as vagas por lista
  moram em "Linha do quadro" (RU-01, RU-03) e que o prazo recursal mora no "Marco".
- **Dá para reduzir a localização sem tocar regra de negócio?** Sim: M1, M2 e M3 são só interface.
- **Como tornar as alterações perceptíveis?** Manter a marca depois da conferência e ligar o resumo
  ao campo (M2). A marca durante a edição já existe e funciona.
- **Como facilitar a conferência do homologador?** Um vocabulário só e a coleção afetada desenhada
  (P1, P3).
- **Dá para resolver a maior parte reaproveitando o editor atual?** Sim.
- **Menor mudança de alto impacto?** M1: busca por rótulo e valor. É só JavaScript, numa tela que
  já tem filtro.
- **O que não vale agora?** Segundo editor, passo obrigatório de assunto, versionamento campo a
  campo e cartões recolhidos antes de medir.

---

## Reprodução

```bash
createdb -h localhost ps_retif_ux
cd backend && make preparar DB_NAME=ps_retif_ux DB_HOST=localhost DB_PORT=5432 \
  POSTGRES_USER=$USER POSTGRES_PASSWORD= DB_MIGRATION_USER=processo_seletivo_owner \
  DB_MIGRATION_PASSWORD=change-me DB_RUNTIME_USER=processo_seletivo_runtime \
  DB_RUNTIME_PASSWORD=change-me DJANGO_SETTINGS_MODULE=config.settings.development
```

```bash
cd backend && DB_NAME=ps_retif_ux DB_HOST=localhost DB_ROLE=runtime \
  DB_RUNTIME_USER=processo_seletivo_runtime DB_RUNTIME_PASSWORD=change-me \
  DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py seed_demo
```

Depois, o `runserver 8135` com as mesmas variáveis e `INTERFACE_SELETOR_IDENTIDADE=true`, e:

```bash
cd backend && UX_BASE=http://localhost:8135 UX_SAIDA=/tmp/ux-retificacao uv run python \
  ../doc/auditoria-ux-retificacao-2026-11-05/roteiro-de-captura.py
```

O Edital ampliado do cenário E sai de `renderizar-edital-extenso.py`, por `manage.py shell` com
`DJANGO_ALLOWED_HOSTS=localhost,testserver`. Ele **só lê**: substitui `conteudo_base` em memória e
grava o HTML. As datas do demo são relativas ao dia do `seed_demo`; as citadas aqui são as de 05/11.
