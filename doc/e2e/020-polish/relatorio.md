# Auditoria visual de polish — SPEC 020 · Anexos do Edital

**Data:** 07/09/2026 · **Branch:** `claude/edital-anexos-spec-f9bdf2` · **Base:** commit `27d51c8`
**Ambiente:** banco `ps020_demo` limpo, `seed_demo` da 020, `INTERFACE_SELETOR_IDENTIDADE=true`,
servidor em `127.0.0.1:8022` (entrada `spec-020` do `launch.json`).

**Escopo:** experiência pelo navegador. Não repete a validação funcional — ela está coberta por
3776 testes e pelo ciclo E2E do 173/2025.

## Sobre as evidências

**Não há PNGs em `screenshots/`, e isso é uma limitação da sessão, não um esquecimento.** O painel
de navegador desta ferramenta devolve as capturas para a conversa e não as grava em disco; não
existe caminho para persistir o arquivo. Cada achado abaixo traz, no lugar da imagem, a **URL, o
seletor e o texto literal observado**, que é o que torna o achado reproduzível. Quem quiser as
imagens reproduz em dois minutos com o ambiente descrito acima.

---

## 1. Veredito

**A 020 está pronta para uma demonstração institucional pelo lado de quem consulta e de quem se
inscreve, e não está pelo lado de quem elabora e de quem homologa.** As três superfícies públicas —
a página da seleção, o download do artefato e o cartão do requisito na inscrição — estão no padrão
do resto do produto: linguagem institucional, rótulos completos, nenhum identificador técnico à
vista. O cartão do candidato, em especial, realiza literalmente a frase que a spec queria: *documento
exigido → modelo oficial → seu arquivo*, nessa ordem e nessa hierarquia.

**Existe defeito visual que diminui confiança mesmo com o domínio correto, e ele está concentrado em
duas telas.** A primeira é a lista de anexos na elaboração: três formulários empilhados por anexo,
sem cartão, sem numeração, sem separador — e com o botão **Remover** de um anexo encostado no rótulo
do anexo seguinte. Em 375 px o rótulo, que é a única coisa que identifica o anexo, aparece truncado
("ANEXO I — REQUERIMENTO DE INSC"). É a definição de P1 desta auditoria: a funcionalidade existe e a
experiência pode levar a erro operacional real. A segunda é a tela de detalhe da Retificação, onde a
substituição do artefato aparece como duas linhas de UUID e SHA-256 — e é ali que o homologador e o
publicador decidem.

O contraste que mais incomoda é interno ao próprio produto. A etapa **Inscrição**, construída pela
`009`, mostra `DOCUMENTO EXIGIDO 1 DE 3` num cartão com borda, botões `↑ Subir` / `↓ Descer` e
`Remover este documento`. A etapa **Anexos**, construída pela `020`, não tem cartão, não tem posição,
não tem reordenação e o botão diz apenas `Remover`. O padrão existe, está a uma tela de distância, e
a feature nova não o seguiu.

Nada do que encontrei é defeito funcional. O domínio se comporta como os testes afirmam: os dois
artefatos coexistem, a versão aceita governa o que a banca vê, a consulta por instante devolve o de
então, e o aviso de "Edital atualizado" da `009` dispara corretamente para quem tem rascunho aberto.

---

## 2. Superfícies auditadas

| Superfície | Desktop | Mobile | Resultado |
|---|:---:|:---:|---|
| Página pública da seleção | ✅ | ✅ | Boa. Achados de affordance e de marcador de lista |
| Download do artefato | ✅ | — | Correto. Nome entregue é o físico |
| Elaboração — etapa Anexos (editável) | ⚠️ | ❌ | **P1.** Sem fronteira entre itens; rótulo truncado |
| Elaboração — etapa Anexos (somente leitura) | ⚠️ | — | Campos desabilitados no lugar de texto |
| Elaboração — Inscrição (vínculo do modelo) | ✅ | — | **Padrão da casa.** Rótulo institucional, nunca UUID |
| Retificação — composição | ✅ | — | Resumo legível; numeração dupla no título do grupo |
| Retificação — detalhe/homologação | ❌ | — | **P1.** Só UUID e SHA-256 |
| Portal — cartão do requisito com modelo | ✅ | ✅ | **Melhor superfície da feature** |
| Portal — aviso de Edital atualizado | ⚠️ | — | Dispara, mas não nomeia o Anexo |
| Mesa de avaliação | ✅ | — | Não infla a tela quando não há anexo |
| Negativos (404, tipo inválido) | ✅ | — | Mensagens boas; problema de posicionamento |

---

## 3. Achados

### POLISH020-001

**Severidade:** P1 · **Tipo:** UX · **Ator:** elaborador

**Observado:** em `/gestao/editais/<id>/compor/anexos`, cada anexo é uma sequência de três
formulários (`rotular`, `substituir`, `remover`) dentro de um `<li>` sem borda, sem fundo e sem
separador — `getComputedStyle` do item devolve `border: 0px none` e `background: transparent`. O
botão **Remover** de um anexo fica imediatamente acima do rótulo do anexo seguinte. Em 375 px o
campo do rótulo tem 287 px e trunca o texto: lê-se `ANEXO I — REQUERIMENTO DE INSC`.

**Esperado:** o padrão que a etapa Inscrição já usa — um cartão por item, com legenda de posição
(`ANEXO 1 DE 3`) e ação destrutiva nomeando o alvo (`Remover este anexo`).

**Impacto:** quem administra um Edital com oito ou doze anexos — a amostra real tem de dois a onze —
pode remover ou substituir o anexo errado. É erro operacional sobre conteúdo normativo, e o rótulo
truncado retira justamente a informação que distinguiria um do outro.

**Evidência:** `#anexos-lista > li` no Edital 99/2026, desktop e 375 px.

**Recomendação:** reaproveitar o desenho de `_documento.html` — `fieldset.linha` com `legend` de
posição, agrupamento visual e rótulo do botão de remoção nomeando o item.

---

### POLISH020-002

**Severidade:** P1 · **Tipo:** conteúdo / UX · **Ator:** homologador, publicador

**Observado:** em `/gestao/retificacoes/<id>/`, a substituição do artefato aparece como:

```
CAMINHO                                          OPERAÇÃO  ANTES              DEPOIS
/attachments/id=3d7ce4aa-.../artifactId          REPLACE   716579ef-...       5e9906c6-...
/attachments/id=3d7ce4aa-.../artifactHash        REPLACE   39ec5b92...(64)    8b476efd...(64)
```

Nenhum rótulo de anexo aparece na tela. Para comparação, a Retificação de vaga da mesma base rende
`/profiles/id=.../immediateVacancies | REPLACE | 2 | 3` — caminho igualmente cru, mas com valores
que uma pessoa confere.

**Esperado:** ao menos uma linha legível, no molde do resumo que a **composição** já produz:
`Anexo I — Autodeclaração étnico-racial · Arquivo do anexo · substituído`. UUID e resumo podem ficar,
em segundo plano, para auditoria.

**Impacto:** é a tela onde o homologador aprova e o publicador assina. Nenhum dos dois viu a tela de
composição. Hoje eles aprovam a substituição confiando apenas no texto da justificativa.

**Evidência:** `/gestao/retificacoes/dbe5ed10-2137-46a6-9253-0ac84513b10d/`, tabela "Alterações
declaradas (2)".

**Recomendação:** a tela é anterior à 020 e serve a todas as Retificações; a correção mínima é a
020 contribuir a projeção legível dos seus dois caminhos. Vale registrar em separado que a tela
inteira merece a mesma tradução.

---

### POLISH020-003

**Severidade:** P1 · **Tipo:** UX · **Ator:** elaborador

**Observado:** o botão **Remover** da etapa Anexos submete direto. Não há diálogo, `onsubmit` nem
`data-confirm` — verificado no DOM. Remover apaga o artefato do rascunho, que não é recuperável.

**Esperado:** a Constituição exige que operações irreversíveis apresentem confirmação e consequências
inequívocas. A remoção de Documento Exigido, na etapa vizinha, também não confirma — mas ali o item
volta a ser digitado; aqui o arquivo precisa ser reenviado.

**Impacto:** um clique perde o arquivo, e o próximo passo é procurar o PDF de novo.

**Recomendação:** confirmação nomeando o anexo, no padrão de `confirmar.html`.

---

### POLISH020-004

**Severidade:** P2 · **Tipo:** linguagem / consistência · **Ator:** elaborador, homologador

**Observado:** na Retificação, o grupo do anexo tem a legenda
`Anexo 1 — ANEXO I — AUTODECLARAÇÃO ÉTNICO-RACIAL`. A mesma duplicação aparece no resumo do diff.

**Esperado:** o rótulo já é a identificação editorial completa. O prefixo `Anexo {order} —` repete
o que ele diz e — pior — introduz um número **posicional** que a D-006 decidiu que o sistema não
calcula. Se a ordem mudar, o prefixo muda e passa a divergir do número impresso dentro do PDF.

**Impacto:** contradiz, na tela, a decisão que a feature inteira sustenta.

**Recomendação:** usar o rótulo puro como título do grupo.

---

### POLISH020-005

**Severidade:** P2 · **Tipo:** conteúdo · **Ator:** elaborador

**Observado:** no resumo da composição, a substituição rende
`Arquivo do anexo (PDF) | arquivo anterior | arquivo novo`.

**Esperado:** o nome e o tamanho dos dois, para que a conferência sirva para conferir —
`autodeclaracao.pdf (3 KB)` → `autodeclaracao-retificada.pdf (4 KB)`.

**Impacto:** a etapa "ver o que vai mudar" é onde um arquivo trocado por engano deveria aparecer, e
é a única que não permite notá-lo.

---

### POLISH020-006

**Severidade:** P2 · **Tipo:** UX · **Ator:** elaborador

**Observado:** ao enviar um JPEG renomeado, a recusa é excelente em texto — *"Este arquivo é uma
imagem (JPEG), e não um PDF — é o que o celular produz ao fotografar um documento. Converta a imagem
em PDF e envie novamente."* — mas: aparece no topo da seção, a ~400 px do campo (erro em `top: 462`,
campo em `top: 856`); **o rótulo digitado é perdido**; e a mensagem inteira viaja na query string
(`?erro=Este%20arquivo%20...`), sobrevivendo a recarregar e a compartilhar o endereço.

**Esperado:** mensagem junto do campo, conteúdo digitado preservado, estado no servidor — que é o
que `compor_etapa` já faz com `digitados` nas outras etapas.

**Impacto:** quem escolheu o arquivo errado redigita o rótulo. É pequeno e é exatamente o tipo de
atrito que faz a tela parecer improvisada.

---

### POLISH020-007

**Severidade:** P2 · **Tipo:** UX · **Ator:** elaborador

**Observado:** a etapa Anexos não mostra a ordem editorial nem permite alterá-la. Não há campo de
ordem no formulário de acréscimo, nem `↑ Subir` / `↓ Descer` como na etapa Inscrição. O comando
`reordenar` existe na aplicação e é testado; **nenhuma tela o alcança**.

**Esperado:** ordem visível e alterável por teclado, como nas coleções vizinhas.

**Impacto:** a ordem é conteúdo publicado e determina como o documento lista os anexos. Hoje ela é
decidida pela ordem de envio e não pode ser corrigida sem Retificação — mesmo com o Edital ainda em
elaboração.

---

### POLISH020-008

**Severidade:** P2 · **Tipo:** UX · **Ator:** elaborador, homologador

**Observado:** a etapa Anexos nunca menciona a palavra "modelo" (verificado no texto renderizado).
Não há como saber, ali, que o ANEXO I é o modelo do requisito *Autodeclaração étnico-racial*. A
informação existe do outro lado — a etapa Inscrição mostra o seletor — e na tela de Revisão.

**Esperado:** cada anexo dizendo de qual requisito é modelo, ou "não é modelo de nenhum requisito",
como a tela de Revisão já faz.

**Impacto:** remover um anexo vinculado, na elaboração, desfaz o vínculo em silêncio — e a tela onde
a pessoa remove é a única que não diz que existe vínculo.

---

### POLISH020-009

**Severidade:** P2 · **Tipo:** UX · **Ator:** revisor, homologador

**Observado:** com o Edital publicado, a etapa Anexos entra em somente leitura e os rótulos
continuam dentro de `<input disabled>`. O texto extraído da página não os contém — a listagem lê-se
como um formulário travado, e não como conteúdo publicado.

**Esperado:** em somente leitura, texto.

---

### POLISH020-010

**Severidade:** P2 · **Tipo:** conteúdo · **Ator:** candidato

**Observado:** depois da Retificação que trocou o ANEXO I, a revisão da inscrição mostra o aviso da
`009` — *"O Edital foi atualizado. Houve alteração desde que você começou."* — com o botão **Ler o
Edital vigente (PDF)**. Em nenhum lugar se diz que **um Anexo mudou**, e o novo modelo não é
oferecido ali.

**Esperado:** quando a alteração alcança um anexo que serve de modelo a um requisito daquela
inscrição, nomeá-lo e oferecer o novo.

**Impacto:** é o caso em que a candidata mais perde trabalho — ela pode ter preenchido e assinado o
formulário antigo. O aviso genérico não a faz olhar para o documento que ela já preencheu. A `020`
introduziu uma espécie de alteração que o aviso da `009` não sabe nomear.

---

### POLISH020-011

**Severidade:** P2 · **Tipo:** UX / consistência · **Ator:** público

**Observado:** na página da seleção, `Ler o Edital completo (PDF)` e os links de anexo têm a **mesma
classe** (`documento secundaria`) e a mesma aparência. O primeiro abre o PDF no navegador; os anexos
respondem `Content-Disposition: attachment` e **baixam**. Os rótulos dos anexos não dizem "(PDF)".

**Esperado:** afordância distinta para comportamentos distintos, e o formato no rótulo.

---

### POLISH020-012

**Severidade:** P2 · **Tipo:** conteúdo · **Ator:** público, candidato

**Observado:** o arquivo entregue chama-se `autodeclaracao.pdf` — o nome físico que quem elaborou
enviou. Depois da Retificação, `autodeclaracao-retificada.pdf`.

**Esperado:** um nome derivado do rótulo institucional, como `ANEXO-I-autodeclaracao-etnico-racial.pdf`.

**Impacto:** a pessoa baixa doze anexos e fica com doze arquivos cujo nome depende de como o autor
salvou o dele. É a decisão da FR-014 (o nome enviado é só exibição) aplicada num lugar onde ela
produz um efeito indesejado.

---

### POLISH020-013

**Severidade:** P3 · **Tipo:** responsividade / consistência · **Ator:** todos

**Observado:** os anexos são itens de `<ul>` com marcador visível ao lado de elementos que já
parecem botão ou caixa — na página pública, na elaboração e no estado vazio ("• Este Edital ainda
não publica anexo nenhum", centralizado dentro de uma caixa, com um marcador flutuando à esquerda).
Em 375 px o marcador fica visualmente solto.

**Recomendação:** `list-style: none` nessas listas, como as demais listas do produto.

---

### POLISH020-014

**Severidade:** P3 · **Tipo:** consistência · **Ator:** elaborador

**Observado:** a gestão usa o controle nativo (`Escolher arquivo | Nenhum arquivo escolhido`), sem
estilo. O portal do candidato, na mesma base, estiliza o seu: `Escolher arquivo PDF` num botão verde
com contorno, seguido de `Somente PDF, até 10 MB.`

**Esperado:** o mesmo tratamento — o padrão já existe e é da própria casa.

---

### POLISH020-015

**Severidade:** P3 · **Tipo:** linguagem · **Ator:** público

**Observado:** o endereço do anexo é `/api/v1/public/anexos/<uuid>`, visível na barra de status ao
passar o mouse e no histórico de downloads.

**Observação:** é a mesma forma que o PDF do Edital já usa (`/api/v1/public/publicacoes/<id>/documento`),
então não é regressão. Fica registrado porque "`/api/v1/`" numa página institucional é vocabulário de
sistema.

---

### POLISH020-016

**Severidade:** P3 · **Tipo:** oportunidade · **Ator:** público

**Observado:** **não existe página HTML da publicação histórica.** O conteúdo de então está em
`/api/v1/public/editais/<id>/versao-vigente?em=<instante>` e em `/api/v1/public/publicacoes/<id>`,
como JSON. A página pública da seleção mostra sempre a versão vigente e **não indica** que houve
Retificação nem qual versão está sendo lida.

**Sobre a classificação:** a 020 não prometeu essa superfície — FR-040 e FR-041 falam da *consulta*,
e ela funciona. A ausência é anterior à feature e vale para todo o conteúdo do Edital, não só para os
anexos. Registro como oportunidade, e não como defeito da 020, conforme o critério da própria
auditoria.

**Impacto se não for feita:** o passo emblemático da feature — os dois artefatos coexistindo — é
verdadeiro no domínio e **invisível para uma pessoa no navegador**. Quem quiser ver o anexo de então
precisa montar uma URL de API com um instante ISO-8601.

---

### POLISH020-017

**Severidade:** P1 · **Tipo:** autorização / UX · **Ator:** julgador de recursos, avaliador

**Encontrado depois do fechamento da auditoria**, ao reproduzir a navegação como `ana — Julgador de
recursos`: a página do Edital em `/gestao/editais/<id>/` oferece o marco **Classificação final**, e
clicar nele devolve **404 — Recurso não encontrado** em `/gestao/editais/<id>/marcos/<id>`.

**Observado:** o 404 é a autorização funcionando: a consulta de marcos publicados exige gerir a
comissão ou `auditoria:consultar`, e o julgador não tem nenhum dos dois. O defeito não é a recusa —
é a lista ter oferecido o link. A tela monta os marcos sem consultar quem está olhando.

**Esperado:** oferecer apenas o que o ator pode abrir. Recusa depois de convidar é pior que ausência:
quem clica não conclui que não tem permissão, conclui que o sistema está quebrado.

**Impacto:** é a primeira leitura que um julgador faz da própria tela de trabalho, e ela parece
defeituosa. O mesmo caminho vale para qualquer papel sem alcance sobre a comissão.

**Evidência:** `/gestao/editais/814abbfe-.../`, identidade `ana — Julgador de recursos`, link
"Classificação final".

---

## 4. Métricas

- Superfícies auditadas: **11** · Desktop e 375 px nas cinco principais
- Achados: **17** — P1: **4** · P2: **9** · P3: **4**
  (16 na auditoria; POLISH020-017 veio depois, da navegação como julgador de recursos)
- Defeitos funcionais encontrados: **0**
- Falsos alarmes meus, verificados e descartados: **2** (aviso de versão que eu dei por ausente e
  existe; "sumiço" da lista em mobile que era captura no meio da rolagem)

---

## 5. Top questions

1. **O elaborador entende o que está anexando?** Sim. O texto de ajuda é a melhor peça de
   linguagem da feature: diz o que é o anexo, quem o preenche, que é PDF e que o sistema não numera.
2. **O candidato encontra o modelo sem procurar fora da inscrição?** Sim, e com folga. O modelo está
   dentro do cartão do requisito, acima do campo de envio, com o rótulo por extenso.
3. **Retificar um anexo parece substituir a mesma peça?** Na composição, sim — o grupo é o anexo e o
   campo é o arquivo. No detalhe da Retificação, não: ali são dois UUIDs trocados.
4. **A versão histórica deixa evidente que é histórica?** Não — não há página histórica, e a página
   vigente não se identifica como versão nenhuma (POLISH020-016).
5. **O público baixa o artefato correto da versão consultada?** Sim. Verificado: os dois artefatos
   respondem 200, com bytes e `ETag` distintos, e o vigente é o novo.
6. **A UI esconde UUID/hash/termos técnicos?** Nas superfícies públicas e do candidato, sim,
   completamente. No detalhe da Retificação, não (POLISH020-002).
7. **Desktop e mobile estão apresentáveis?** O público e o candidato, sim. A elaboração de anexos
   não, em 375 px.
8. **Algo ainda parece "sistema de desenvolvedor"?** Duas coisas: a lista de anexos da elaboração e
   a tabela de alterações da Retificação.

---

## 6. O que está muito bom, e deve ser preservado

- **O cartão do requisito com modelo, no portal.** `Autodeclaração étnico-racial` → `Conforme o
  modelo do Anexo do Edital.` → `Baixar o modelo: ANEXO I — …` → `Escolher arquivo PDF`. A ordem é a
  da tarefa e cada peça se explica.
- **O texto de ajuda da etapa Anexos.** Ensina o conceito e a convenção do rótulo num parágrafo.
- **A mensagem de recusa de arquivo não-PDF.** Diz o que aconteceu, por que costuma acontecer e o
  que fazer.
- **O seletor de modelo no Documento Exigido**, com "Não fornece modelo" como primeira opção e a
  ajuda apontando a etapa onde os anexos são cadastrados. Nunca mostra UUID.
- **A faixa "Somente leitura"** no Edital publicado, dizendo que alterações passam por Retificação.
- **A Mesa não inflou.** Sem anexos, a coluna simplesmente não aparece e a grade continua alinhada.
- **O estado vazio afirma em vez de lamentar**: "É legítimo: nem todo Edital fornece formulário
  próprio."

---

## 7. Recomendação

**Corrigir polish curto e reauditar.**

Não há defeito funcional e não há motivo para segurar o mérito da feature. Mas três achados P1 estão
em telas que uma demonstração institucional percorre — a lista de anexos da elaboração e o detalhe da
Retificação —, e dois deles podem levar a erro operacional sobre conteúdo normativo.

A correção é curta e quase toda reaproveitamento: **POLISH020-001** e **003** são o desenho de
`_documento.html` aplicado à lista de anexos; **POLISH020-002** é uma projeção legível dos dois
caminhos que a 020 introduziu; **004**, **005** e **013** são de uma linha cada. Isso já deixaria a
feature apresentável ponta a ponta.

**POLISH020-007** (ordem editorial sem tela) e **POLISH020-010** (o aviso que não nomeia o Anexo)
são decisões de produto, não de acabamento, e merecem entrar como escopo declarado — não como
correção silenciosa no meio de um polish.

---

## 8. Estado das correções

Registrado em 08/09/2026, depois da instrução "corrija tudo o que foi identificado no relatório".
Essa instrução também **autoriza expressamente** POLISH020-007 e POLISH020-010, que a §7 recomendava
não corrigir em silêncio: eles entram declarados, e não escondidos no meio do acabamento.

| Achado | Estado | O que mudou |
|---|---|---|
| 001 | ✅ corrigido | `compor_anexos.html`: `fieldset.linha` com `legend` `ANEXO 1 DE 3`, agrupamento visual e `Remover este anexo` |
| 002 | ✅ corrigido | `retificacao_detalhe.html` + `_anexo_legivel`: a linha diz o rótulo do anexo e a operação; UUID e resumo ficam em segundo plano |
| 003 | ✅ corrigido | `data-confirmar` nomeando o anexo, servido pelo `remocao.js` que a casa já usa |
| 004 | ✅ corrigido | o título do grupo passa a ser o rótulo puro; o prefixo posicional saiu |
| 005 | ✅ corrigido | `_descricao_do_artefato`: `nome_original · tamanho` nos dois lados da conferência |
| 006 | ✅ corrigido | a recusa passa pela sessão (`anexos_recusa`), preserva o rótulo digitado e sai da query string |
| 007 | ✅ corrigido | comando `mover` e os botões `↑ Subir` / `↓ Descer`, no padrão da etapa Inscrição |
| 008 | ✅ corrigido | cada anexo diz "Modelo de: …" ou "Não é modelo de nenhum documento exigido." |
| 009 | ✅ corrigido | em somente leitura o rótulo é texto (`<strong>`), e não `input disabled` |
| 010 | ✅ corrigido | `_modelos_alterados` compara os artefatos entre a versão reconhecida e a vigente e nomeia o modelo que mudou |
| 011 | ✅ corrigido | `(PDF, baixar)` no rótulo e `download` explícito, distinguindo do Edital que abre |
| 012 | ✅ corrigido | `_nome_do_arquivo` deriva do rótulo institucional, dobrado para ASCII |
| 013 | ✅ corrigido | `list-style: none` nas listas de anexo, pública e da elaboração |
| 014 | ✅ corrigido | `input[type=file].arquivo` estilizado no padrão do portal |
| 015 | ⬜ mantido | `/api/v1/public/anexos/<uuid>` é a mesma forma que o PDF do Edital já usa. Trocar só o endereço do anexo criaria a inconsistência que o achado aponta; a mudança é de rota pública, para todos os artefatos, e não cabe num polish |
| 016 | ⬜ não feito | a página HTML da publicação histórica é **superfície pública nova**, não acabamento. O próprio achado a classifica como oportunidade e diz que a ausência é anterior à 020. Construí-la aqui seria escopo entrando pela porta dos fundos |
| 017 | ✅ corrigido | `_marcos_publicados` recebe o ator e devolve lista vazia a quem não pode abrir o marco — a tela deixa de oferecer o que a autorização vai recusar |

**Cobertura de teste.** Cada correção tem teste que falha sem ela — verificado reintroduzindo o
defeito, e não apenas observando o verde. Os principais: `test_cada_anexo_e_um_item_com_posicao_e_acao_nomeada`,
`test_subir_e_descer_mudam_a_ordem_e_nao_tocam_no_rotulo`,
`test_a_recusa_preserva_o_rotulo_digitado_e_nao_vai_para_o_endereco`,
`test_em_somente_leitura_o_rotulo_e_texto_e_nao_campo_travado`,
`test_o_detalhe_da_retificacao_diz_o_anexo_e_nao_o_hash`,
`test_a_conferencia_diz_qual_arquivo_sai_e_qual_entra`,
`test_o_aviso_de_edital_atualizado_nomeia_o_modelo_que_mudou`,
`test_sem_troca_de_modelo_o_aviso_nao_inventa_alteracao` e
`test_a_classificacao_so_e_oferecida_a_quem_pode_abri_la`.

**Suíte:** 3788 passaram, 1 pulada. `ruff` limpo.

**Reauditoria pelo navegador:** a etapa Anexos e a página pública da seleção foram reabertas em
`127.0.0.1:8022` depois das correções. A etapa mostra `ANEXO 1 DE 3` … `ANEXO 3 DE 3`, cada um com
rótulo, arquivo, a linha de modelo e as ações nomeadas; a página pública lista
`ANEXO I — AUTODECLARAÇÃO ÉTNICO-RACIAL (PDF, baixar)`.
