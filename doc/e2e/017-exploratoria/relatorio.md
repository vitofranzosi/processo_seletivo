# Auditoria exploratória E2E — até Publicação de Resultados (017)

## 1. Resumo executivo

**O ciclo institucional fecha.** Foi possível, só pelo navegador e alternando identidades reais, constituir um Processo, publicar um Edital normativo, receber oito inscrições, compor comissão, distribuir, avaliar nas duas formas, consolidar duas Etapas, emitir a classificação e — o que a 017 acrescenta — **divulgá-la oficialmente, entregá-la ao público sem autenticação, ao candidato dentro da própria inscrição, e preservá-la intacta depois de uma publicação posterior a suceder**.

Os dez invariantes centrais da 017 foram **todos comprovados** (§5). Os dois mais difíceis passaram com folga: a confirmação **revalida** e recusa uma prévia que envelheceu entre abrir e confirmar; e o conteúdo publicado vem do ato imutável, não de recomputação — provado empiricamente, não só por leitura de código: depois que uma Retificação dobrou o peso de uma Etapa, a publicação P1 continua exibindo `95,00`, enquanto a regra vigente hoje produziria `190,00`.

Distinguindo as quatro camadas que o roteiro pede:

- **Operação interna** — fecha. Do Edital ao ato de ordenação, sem manipulação de dado por fora.
- **Divulgação pública** — fecha. Endereço estável, anônimo, com documento oficial e SHA-256 do conteúdo divulgado.
- **Acesso do candidato** — fecha para quem está no universo do ato. **Não fecha para quem ficou fora dele**: a candidata eliminada na Etapa 1 não vê absolutamente nada sobre o resultado — nem que houve um (E2E17-004).
- **Comunicação ativa** — não existe, e está fora do escopo declarado da 017. Publicação passiva existe; ninguém é notificado.
- **Recurso** — não existe. O PDF normativo continua prometendo recurso sem que haja meio (limite do produto, não defeito da 017).

O achado mais grave **não é da 017**: seguindo o assistente na ordem natural, o Edital é publicado **sem período de inscrições**, porque qualquer gravação posterior ao passo *Inscrição* apaga silenciosamente a marca. O Edital anuncia o período no PDF e o sistema não recebe inscrição nenhuma. Causa confirmada no código, e foi o único bloqueio que exigiu contorno para esta auditoria prosseguir.

> **Corrigido depois desta auditoria.** Os achados 001, 002, 003 e 006 foram fechados no hardening
> pós-017 (§13). Os que permanecem abertos — 004, 005 e 007 — são decisão de governança ou
> capacidade nova, e ficam para a priorização do produto. O corpo dos achados preserva o que foi
> observado; o estado de cada um vem ao fim da respectiva seção.

---

## 2. Ambiente e base

| item | valor |
|---|---|
| commit | `c2e80c3` (merge do PR #42 — implementação da 017) |
| branch | `main` |
| banco | PostgreSQL local, `ps017_audit`, criado vazio e migrado |
| servidor | `runserver` :8177, `INTERFACE_SELETOR_IDENTIDADE=true` |
| ferramentas | Playwright (Chromium), mailpit (:1025/:8025), `psql` para as provas de banco |
| screenshots | **53** em `screenshots/` |
| candidatos | 8 |
| publicações | 2 (P1 preliminar, P2 definitiva sucedendo P1) |
| atos de ordenação | 2 (C1, C2) |
| retificações | 4 (encerrar inscrições, peso da Etapa, remoção do marco, + a de composição) |

**Atores, sem superusuário:** `elena.elaboradora` (elaborador), `wagner.homologador`, `paula.publicadora` (publicador — única com `resultado:publicar`), `gustavo.gestor`, `paulo.presidente` (presidência por vínculo, sem papel sistêmico), `alice.avaliadora` e `otavio.avaliador`, `aurora.auditora`, e oito candidatos distintos com acesso sem senha por código de e-mail.

**Preparação fora do produto** (nada do domínio): banco vazio + migrações; a variável do seletor de identidade (a autenticação institucional não existe ainda); mailpit para capturar os códigos de acesso; quatro PDFs fictícios de 209 bytes para os anexos.

**Não foi possível criar pela interface:** um segundo Edital dentro de um Processo existente — a tela do Processo não oferece a ação, embora a listagem fale em "Editais (N)". Para o contorno do bloqueio foi preciso criar um Processo novo.

---

## 3. Escopo executado

| Fase | Executada | Resultado | Evidência |
|---|---|---|---|
| Processo + Edital + Perfil + modalidades + fatos | sim | ok | `01`, `02` |
| Cronograma, 2 Etapas (decisória + pontuada) | sim | ok | `02` |
| Marco classificatório + 3 critérios de desempate | sim | ok, **numa só passagem** | `03` |
| Documentos exigidos, submissão, homologação, publicação | sim | ok | `04`, `05` |
| PDF normativo | sim | alvos e fatos nomeados | — |
| 8 inscrições com anexos, fatos e protocolo | sim | ok | `06`–`09` |
| Comissão, alocação, distribuição por rodízio | sim | ok | `10`–`12` |
| Mesa decisória e pontuada, parecer obrigatório | sim | ok | `13`, `14` |
| Consolidação das 2 Etapas | sim | ok | `15`–`17` |
| Classificação: ordem, desempate, empate residual | sim | ok | `18`, `19` |
| **§7 ato interno ≠ público** | sim | **provado** | `20`–`22` |
| **§8 segregação da autoridade** | sim | **provado** | `23`, `24` |
| **§9–§11 prévia, dados públicos, legibilidade** | sim | sem vazamento | `24` |
| **§12 publicação** | sim | ok | `26` |
| **§14 página pública (desktop + 375px)** | sim | ok | `27`, `28` |
| **§15–§16 Área do Candidato, 4 situações** | sim | 3 ok, 1 lacuna | `29`–`32` |
| **§17–§18 PDF e consistência HTML×PDF** | sim | idênticos | — |
| **§19 idempotência (duas abas)** | sim | uma só publicação | `25` |
| **§20 revalidação prévia→confirmação** | sim | **recusada** | `33`, `34` |
| **§21 ato obsoleto** | sim (regra alterada) | recusado | `35`, `36` |
| **§22 marco removido** | sim | recusado | `49`, `50` |
| **§23 sucessão completa** | sim | **exemplar** | `37`–`42` |
| **§24 append-only** | sim | trigger recusa até o dono | — |
| **§25 histórico / §42 recurso** | sim | rastreável ponta a ponta | `43`, `44` |
| **§27 IDOR** | sim | 404 uniforme | `45` |
| **§33 responsividade** | sim | sem rolagem horizontal | `46`–`48` |
| **§34 acessibilidade exploratória** | sim | boa base | — |
| §21 obsolescência por **universo** alterado | **não** | não exercida (só por regra) | — |

---

## 4. Jornada observada

Edital 12/2026 composto e publicado → 8 candidatos inscritos com protocolo → comissão de três (presidência + dois avaliadores) → distribuição por rodízio nas duas Etapas → Etapa 1 decisória (7 Deferidas, 1 Indeferida com parecer) → consolidação → Etapa 2 pontuada (6 habilitadas, 1 eliminada por nota) → consolidação → classificação calculada e emitida (C1) → **publicação P1 (preliminar)** → página pública anônima + PDF oficial + Área do Candidato → Retificação altera o peso → C1 fica obsoleto → C2 emitido → **publicação P2 (definitiva)**, que sucede P1 → P1 permanece, intacta, dizendo que foi sucedida.

Ordem publicada em P1: **1º Ana 95,00 · 2º Bruno 88,00 · 3º Carla 82,00 · 4º Diego 82,00 · 5º e 5º Elisa e Fábio 75,00 (posição compartilhada)**. Gustavo, eliminado por nota, considerado sem posição — não nomeado publicamente, mas vê a própria situação. Helena, eliminada na Etapa 1, fora do universo do ato.

O desempate entre Carla e Diego (ambos 82,00) foi decidido pelo 2º critério, meses de experiência — 40 contra 20 —, e a prova disso está na proveniência administrativa, **sem que o número apareça na publicação**.

**O fluxo termina** na consulta: o resultado está publicado, acessível e defensável. Ninguém é avisado, e não há por onde recorrer.

---

## 5. Invariantes da 017

| Invariante | Resultado | Evidência |
|---|---|---|
| publicação não cria classificação | ✅ | a publicação só oferece natureza e autoridade; posição, pontuação e desempate não trafegam no formulário (`24`) |
| conteúdo vem do ato emitido | ✅ | **prova empírica**: após a Retificação dobrar o peso, P1 continua `95,00` enquanto a regra vigente produz `190,00` (`40`); no código, `publicar_resultado` compõe de `compor(ato)`, que lê `ato.versao.content` e as `PosicaoNaOrdem` daquele ato |
| obsolescência é revalidada na confirmação | ✅ | prévia válida mantida aberta, ato envelhecido noutro contexto, confirmação **recusada** com mensagem acionável (`33`, `34`) |
| publicação é append-only | ✅ | `UPDATE` direto no banco recusado: `ERROR: result publications are append-only`; triggers de UPDATE/DELETE nas três tabelas; **não existe coluna de vigência mutável** — a sucessão aponta para trás, e a linha histórica nunca é tocada |
| histórico permanece acessível | ✅ | P1 e P2 respondem 200 e inalteradas mesmo **depois de o marco ser removido da norma** (`50`) |
| candidato não vê antes de publicar | ✅ | nenhum vazamento de posição/pontuação antes de P1; rotas de gestão redirigem ao seletor; POST → 403 (`21`, `22`) |
| candidato vê depois | ✅ | classificada, empatada e eliminado veem a própria situação e chegam à publicação (`29`–`31`) |
| dados privados não vazam | ✅ | prévia, página pública e PDF: zero CPF, e-mail, nascimento, meses, UUID, hash ou enum |
| duplo submit é idempotente | ✅ | duas abas com a mesma prévia: a segunda recusada (`publication_preview_stale`), uma única publicação no banco (`25`) |
| sucessão é observável | ✅ | P1 diz "foi sucedido… não é mais o que vale" com link para a vigente; histórico mostra Vigente/Sucedida; candidata migra sozinha para P2 (`40`, `39`, `42`) |

**10 de 10 comprovados.**

---

## 6. Achados

### E2E17-001 — O Edital é publicado sem período de inscrições, e ninguém percebe

**Severidade:** P1 (seria P0 num certame real) · **Tipo:** domínio / funcional · **Features:** 006–009, transversal · **Ator:** Elaborador

**Observado.** Compondo o Edital na ordem natural do assistente, marquei o Evento "Período de inscrições" no passo *Inscrição* e o passo salvou sem erro. Ao publicar, **nenhum evento ficou marcado**: `is_registration_period = False` em todos os cinco. A página pública não oferece inscrição, e o PDF normativo continua anunciando "2 Período de inscrições 06/09/2026, às 9h — 08/09/2026, às 23h59".

**Esperado.** A marca sobrevive até a publicação, ou o sistema impede publicar um Edital cujo cronograma anuncia inscrições que ele não receberá.

**Impacto.** O certame nasce morto: o Edital é oficial, promete prazo de inscrição e o sistema não aceita nenhuma. O aviso da Revisão ("Nenhum Evento está marcado como período de inscrições") aparece, mas é não impeditivo **e falso do ponto de vista de quem marcou** — quem configurou corretamente tende a descartá-lo.

**Reprodução.** Assistente → *Inscrição*: escolher o Evento e salvar → *Conteúdo*: salvar (é o passo seguinte, e é obrigatório atravessá-lo para chegar à Revisão) → publicar. A marca some.

**Evidência.** `E2E17-001-edital-publicado-sem-inscricao.png`; `is_registration_period=False` em todos os eventos.

**Causa confirmada no código.** `forms.eventos_persistidos()` serializa o Evento **sem** a chave `isRegistrationPeriod`; `views._gravar_etapa()` usa esse serializador como base do `schedule` em **todos** os passos e só reintroduz a chave no passo `inscricao`; `draft.py:308` faz `event.get("isRegistrationPeriod", False)`. Logo, qualquer gravação posterior ao passo *Inscrição* zera a marca — e a ordem do assistente coloca *Conteúdo* logo depois.

**Recomendação.** `eventos_persistidos()` deve emitir `isRegistrationPeriod`, como já emite `order`. Um teste que grave dois passos em sequência e afirme a sobrevivência da marca fecha a classe inteira do defeito.

**Bloqueio e contorno.** Este foi o único bloqueio da auditoria. **Nenhuma linha de código foi alterada.** O contorno foi operacional: compus um segundo Edital (12/2026) gravando *Conteúdo* **antes** de *Inscrição*, deixando o passo de inscrição por último. A Revisão passou a dizer "Nada pendente" — o que confirma o diagnóstico. O Edital 11/2026, publicado sem período, ficou preservado como evidência.

**Estado: corrigido** (hardening pós-017, `60f98f7`). O diagnóstico estava certo e era metade do
defeito. `eventos_persistidos()` passou a emitir `status` e `isRegistrationPeriod`.

A auditoria do código encontrou o mesmo defeito por um **segundo caminho**, que a reprodução do
relatório não alcança: a etapa **dona** da coleção reenvia o que o formulário leu, e o formulário
conhece só os campos que desenha. Voltar ao Cronograma para corrigir uma data desdesignava o
período, porque aquela tela não oferece a marca. Fechar só o primeiro caminho deixaria a marca
morrendo por meia jornada.

**Auditoria dos serializadores irmãos.** Comparados campo a campo o modelo, o contrato de entrada
(`editais/api/serializers.py`, `editais/domain/validation.py`) e a reconstrução em
`draft.py::replace_draft`:

| serializador | omissões reais |
|---|---|
| `eventos_persistidos()` | `status`, `isRegistrationPeriod` — o achado |
| `perfis_persistidos()` | `classificationInformation`, `callInformation` |
| `etapas_persistidas()` | nenhuma — os treze campos que o command reconstrói |
| `secoes_persistidas()` | nenhuma — `key` e `content`, e a identidade é derivada |
| `documentos_persistidos()` | nenhuma — os oito campos |

Os dois do Perfil são conteúdo normativo que o contrato declara, que `draft.py` reconstrói e que o
conteúdo publicado carrega — e que **nenhuma tela do assistente desenha**. Quem os escrevesse pela
API os perderia na primeira gravação do assistente, sem tela onde reparar a perda.

**Regressão coberta** em `tests/interface/test_round_trip_do_rascunho.py`: a jornada real, e a
comparação do Cronograma inteiro contra o contrato — não só da marca —, de modo que campo novo
esquecido no reenvio derrube o teste.

---

### E2E17-002 — Removido o marco, a tela de classificação devolve 404 técnico — e é para lá que a mensagem manda ir

**Severidade:** P2 · **Tipo:** UX / consistência · **Features:** 015–017 · **Ator:** Publicador

**Observado.** Depois de uma Retificação remover o marco, a prévia recusa a divulgação corretamente e orienta: *"Emita o ato sucessor na tela de classificação do marco e publique o ato vigente"*, com o link "Ir para a classificação do marco". Esse link leva a `/gestao/editais/<id>/marcos/<id>`, que responde **404 com a página de depuração do Django** (lista de URLconf).

**Esperado.** Ou a orientação reconhece que o marco não existe mais e não manda a lugar nenhum, ou a tela responde institucionalmente explicando que o marco foi removido.

**Impacto.** O operador é instruído a fazer algo impossível e cai numa página técnica. Some-se a isso que a orientação é logicamente inconsistente: não há ato sucessor a emitir quando o marco deixou de existir — a própria 015 trata marco removido como não recomputável.

**Evidência.** `49-marco-removido-publicacao-impedida.png`, `51-achado-404-tecnico-apos-remocao-do-marco.png`.

**Causa.** Hipótese: `_edital_para_classificar` / a resolução do marco levantam `Http404` sem template institucional, e a mensagem de impedimento é a mesma do caso "ato sucedido", que tem sucessor possível.

**Recomendação.** Mensagem específica para marco removido, sem CTA de sucessão, e página 404 institucional na gestão.

**Estado: corrigido** (hardening pós-017, `17ab044`). A hipótese sobre a causa do 404 estava
errada, e a causa real é mais ampla do que o achado.

`estado_do_marco` **trata** o marco removido: com ato vigente ele devolve `recomputavel=False` e a
tela da 015 responde 200, dizendo que o marco não existe na norma. O 404 era de **autorização**: a
tela da classificação é da presidência e da auditoria, e `paula.publicadora` não tem nenhuma das
duas. O botão levava a uma porta fechada — e levava **em qualquer das três recusas**, não só nesta.

Três correções, portanto:

1. **A mensagem.** `admite_sucessor` separa, no domínio, a recusa que tem remédio da que não tem.
   Removido o marco, a recusa diz que não há ato sucessor a emitir e para; restabelecê-lo é
   decisão normativa, por Retificação, e não operação que a tela ofereça. Ato sucedido e ato
   desatualizado continuam nomeando o caminho, porque nesses o marco segue na norma.
2. **O caminho.** O CTA passa a depender de alcançar a tela para a qual aponta — o mesmo predicado
   que a guarda. Vale para a prévia e para a tela de resultados divulgados, onde ele estava
   condicionado a `pode_publicar`, exatamente a capacidade que **não** abre aquela porta; e para a
   trilha de navegação daquela tela, que leva ao mesmo lugar.
3. **O 404.** Um `404.html` institucional em `shared/templates/`, para os dois canais. Ele não diz
   por quê: no sistema, 404 é também a resposta a "existe e você não alcança", e distinguir os dois
   casos revelaria o recurso a quem não deve sabê-lo.

**A mesma classe, com outro destino** (`4032e8a`). Na mesma prévia, a trilha "Ato de
classificação" e o botão "Cancelar" apontavam para a tela do ato de ordenação, atrás da mesma
porta e com o mesmo 404 para o publicador. Não era objeto do achado; foi fechado depois, por
decisão do produto, com a regra desta seção:

- a **trilha** deixa de ligar e continua nomeando o degrau — nomear de onde a prévia vem não é
  abrir o que veio antes dela;
- **Cancelar** leva ao histórico de divulgações do marco, que é a tela da própria publicação e que
  a capacidade de publicar já abre. Desistir precisa chegar a algum lugar, e devolver quem só
  publica ao ato trocaria a desistência por um 404.

Quem consulta o ato continua recebendo os dois caminhos de antes, e **nenhuma permissão se
alargou**: o que muda é o destino oferecido, não quem entra em cada tela.

---

### E2E17-003 — A proveniência do ato mostra enum e data em inglês onde a instituição responde recurso

**Severidade:** P2 · **Tipo:** conteúdo / legibilidade · **Features:** 015 (regressão não corrigida) · **Ator:** Presidência, Auditoria

**Observado.** Na página do ato — a que sustenta a resposta a um recurso — lê-se `Emitido por paulo.presidente em Sept. 6, 2026, 2:59 p.m.` e, no desempate, `MAIOR_PONTUACAO_NA_ETAPA — valor 82.0000`, `Critério que separou: MAIOR_VALOR_DE_FATO — valor 40`. Na tela de ordenação, a coluna MODALIDADE exibe `d05f435f-fdc4-404f-9a43-3b1d04582e14`.

**Esperado.** Datas localizadas e critérios com o rótulo publicado ("maior valor declarado em Meses de experiência em laboratório"), como **a própria 017 já faz** na prévia, na página pública e no PDF.

**Impacto.** A trilha administrativa — precisamente o artefato que responde a controle externo — é a menos legível do produto, enquanto a superfície pública é exemplar. O contraste mostra que a solução já existe no repositório.

**Evidência.** `44-proveniencia-do-ato.png`, `18-ordem-calculada-antes-de-emitir.png`.

**Causa confirmada.** Não há `LANGUAGE_CODE` em `backend/config/settings/` (há `TIME_ZONE = "America/Sao_Paulo"`), então o Django formata em `en-us`. A resolução de rótulo existe em `divulgacao/domain/conteudo.py::compor()`, que resolve modalidade pela versão que o ato citou, e não foi aplicada às telas da 015.

**Recomendação.** `LANGUAGE_CODE = "pt-br"` e reuso do resolvedor da 017 nas telas de ordenação e ato. É o achado E2E15-006/009 da auditoria anterior, ainda aberto.

**Estado: corrigido** — quase todo antes deste hardening. O PR #43 (`abd701a`, `120b19c`) entrou
**depois** desta auditoria, que rodou em `c2e80c3`, e fez exatamente o que a recomendação pede:
`LANGUAGE_CODE = "pt-br"`, datas no formato da instituição, a modalidade nomeada na coluna
MODALIDADE, e o critério de desempate pela frase publicada com o alvo normativo — "maior pontuação
na Etapa Prova didática" —, mantendo enum e `criterionId` ao lado, como detalhe técnico, porque
ali o identificador é âncora de auditoria.

O resolvedor foi **extraído**, e não `compor()` reaproveitado: `classificacao/domain/nomes.py` e
`publicacoes/domain/vocabulario_da_regra.py`. A resolução é sempre pela versão que o ato cita — a
fronteira pública/individual da 017 continua só em `compor()`.

Sobrou uma instância da mesma classe, corrigida agora (`432112c`): a tabela de resultados
antecedentes lia `consolidatedAt` como o snapshot o grava —
`2026-09-06T18:43:10.761405+00:00`, UTC e notação de máquina — na mesma tela em que as outras
datas já saíam `06/09/2026 15:43`. O filtro `date` do Django não a alcançava, porque diante de
texto ele devolve vazio.

Uma varredura das duas telas por enum e UUID confirma que o que resta é deliberado: a tela da
ordenação não tem nenhum dos dois, e a do ato mantém os identificadores da proveniência ao lado
dos nomes.

---

### E2E17-004 — Quem foi eliminado antes do marco não recebe notícia nenhuma do resultado

**Severidade:** P2 · **Tipo:** funcional / UX · **Features:** 013–017 · **Ator:** Candidato

**Observado.** Helena foi Indeferida na Etapa 1 e ficou fora do universo do ato. Publicado o resultado, o acompanhamento dela mostra apenas "✓ Inscrição enviada" e o cronograma. **Não há bloco "Resultado divulgado", nem link para a publicação, nem menção ao Indeferimento da Etapa 1.** Ela não tem como saber, dentro do produto, que o processo avançou nem por que saiu.

Compare com Gustavo, eliminado na Etapa 2 (dentro do universo), que vê: *"Você não foi classificado neste marco — pontuação inferior à nota mínima da Etapa (45,0000 < 60,0000)"* e chega à publicação.

**Esperado.** A distinção entre "eliminado antes" e "eliminado no marco" pode ser normativa, mas o silêncio absoluto não é informação. No mínimo, que o resultado da Etapa em que ela foi eliminada apareça na participação dela.

**Impacto.** O candidato eliminado cedo é exatamente quem mais precisa de resposta institucional — e é o único que precisa procurar a instituição por fora. Reabre o controle paralelo que o produto veio fechar.

**Evidência.** `32-candidata-fora-do-universo.png` contra `31-candidato-eliminado.png`.

**Causa (hipótese).** A Área do Candidato lê `SituacaoDivulgada`, que só existe para participantes do universo do ato. O resultado por Etapa (013) nunca foi objeto de divulgação — só a classificação do marco é.

**Recomendação.** Decisão de produto: divulgar resultado de Etapa é escopo próprio (não é defeito da 017). Enquanto não existir, a Área do Candidato poderia ao menos dizer que houve divulgação no marco e que a inscrição não participou dele.

---

### E2E17-005 — "Resultado definitivo" é escolha livre de um seletor, sem ato que a legitime

**Severidade:** P2 · **Tipo:** governança / domínio · **Features:** 017 · **Ator:** Publicador

**Observado.** Na prévia, `Natureza do resultado` é um `<select>` com "Resultado preliminar" e "Resultado definitivo". Publiquei P2 como **definitiva** imediatamente após P1 preliminar, sem prazo de recurso decorrido, sem homologação e sem qualquer outro ato — bastou escolher a opção. O sistema só impede o caminho inverso (definitiva → preliminar).

**Esperado.** Chamar um resultado de definitivo deveria decorrer de um fato institucional — prazo de recurso encerrado sem impugnação, ou recursos julgados. Hoje é uma afirmação sem lastro.

**Impacto.** O produto emite um ato que afirma definitividade sem ter o marco que a produz. É um risco jurídico do tipo que a 015 evitou com cuidado ao separar calcular de emitir.

**Evidência.** `38-previa-p2-sucessao.png`, `41-p2-vigente.png`.

**Causa confirmada.** `publicar_resultado` valida apenas que `natureza ∈ Natureza.values` e a não regressão preliminar↛definitiva. Nenhuma outra condição.

**Recomendação.** Registrar como **lacuna de governança**, não corrigir às cegas: a decisão de o que autoriza "definitivo" é do usuário. A 018 (recursos) é a candidata natural a fornecer o marco.

---

### E2E17-006 — A recusa por inscrições abertas mostra o horário em UTC

**Severidade:** P3 · **Tipo:** conteúdo / consistência · **Features:** 011–012 · **Ator:** Presidência

**Observado.** Com o término das inscrições gravado para 14:56 (local), a recusa da distribuição diz: *"As inscrições ficam abertas até 06/09/2026 às 17:56"* — três horas à frente, o valor UTC. A página pública, no mesmo instante, exibia o horário local corretamente.

**Impacto.** A presidência conclui que precisa esperar mais três horas do que precisa. Erro de operação, não de dado.

**Evidência.** saída da recusa; distribuição concluída às 14:57, provando que o término real era 14:56.

**Recomendação.** Localizar o instante na mensagem, como as demais telas fazem.

**Estado: corrigido** (hardening pós-017, `99e9f6d`). `timezone.localtime` antes da formatação, que
é o compromisso que `publicacoes/infrastructure/humano.py` já declarava por escrito. O teste usa um
instante cujo horário em UTC cai no **dia seguinte** — 23h59 de 6 de setembro em São Paulo é 02h59
de 7 de setembro em UTC —, de modo que a regressão não passe por diferença de três horas.

---

### E2E17-007 — Não há como criar um segundo Edital num Processo existente

**Severidade:** P3 · **Tipo:** funcional · **Features:** 001–007 · **Ator:** Gestor

**Observado.** A tela do Processo lista "Editais (1)" e oferece apenas Comissão, Alocação, Encerrar e Cancelar. Não há ação para acrescentar um Edital, embora o modelo e a listagem pressuponham vários.

**Impacto.** Uma segunda chamada exige criar outro Processo, o que separa artificialmente coisas que a instituição entende como o mesmo certame. Foi o que a auditoria teve de fazer para contornar o E2E17-001.

**Evidência.** ações da tela do Processo.

---

## 7. Severidade

| Sev. | Qtde | Achados | corrigidos | abertos |
|---|---|---|---|---|
| P0 | 0 | — | — | — |
| P1 | 1 | 001 | 001 | — |
| P2 | 4 | 002, 003, 004, 005 | 002, 003 | 004, 005 |
| P3 | 2 | 006, 007 | 006 | 007 |

Nenhum P0: não houve publicação incorreta, vazamento, ato histórico modificável, publicação por ator indevido, divergência entre conteúdo público e ato, nem acesso do candidato a resultado não publicado.

---

## 8. Regressões desde a auditoria E2E-015

| Achado anterior | Estado hoje | Como verifiquei |
|---|---|---|
| **E2E15-001** — critério de desempate nasce sem alvos | ✅ **corrigido, sem regressão** | marco e três critérios compostos numa só passagem; o select já nasce com Etapas e fatos (`03`) |
| **E2E15-004/005/008** — PDF sem alvos nem fatos | ✅ **corrigido** | PDF traz "3º menor valor declarado em Data de nascimento; sem o valor, o critério não se aplica" e a seção "Dados exigidos na inscrição" |
| **E2E15-006** — UUID nas telas da 015 | ⚠️ **parcial na auditoria** · ✅ **fechado depois** | protocolo resolvido; MODALIDADE ainda UUID (E2E17-003) — corrigido pelo PR #43, que entrou depois desta auditoria |
| **E2E15-009** — datas em inglês | ❌ **aberto na auditoria** · ✅ **fechado depois** | "Sept. 6, 2026, 2:59 p.m." (E2E17-003) — `LANGUAGE_CODE = "pt-br"` no PR #43 |
| **E2E-017** — guarda de conjunto fechado na distribuição | ✅ **sem regressão** | distribuição recusada enquanto as inscrições estavam abertas |
| **D-003** — eliminada em Etapa anterior some da Mesa seguinte | ✅ **sem regressão** | após consolidar a Etapa 1, a Mesa da Etapa 2 caiu de 4 para 3 inscrições |
| Autorização, isolamento entre candidatos | ✅ **sem regressão** | 404 uniforme (`45`) |
| Responsividade | ✅ **sem regressão** | 375px sem rolagem horizontal em cinco telas |

**Nenhuma regressão real.** As duas linhas abertas eram achados anteriores ainda não corrigidos, não retrocessos — e as duas foram fechadas pelo PR #43, que entrou depois desta auditoria (§13).

---

## 9. Limite atual do produto

Não são defeitos da 017 e não foram abertos como achados:

- **Recurso** — não existe (018). O PDF normativo promete recurso; o produto não oferece meio.
- **Comunicação ativa** — publicação passiva existe; ninguém é notificado por e-mail.
- **Corte por alvo e progressão (014)** — inexistente.
- **Convocação/nomeação** — inexistente.
- **Divulgação de resultado por Etapa** — só o marco classificatório é divulgado.
- **Prova de reprodutibilidade** — `reproduzir_ato` existe no domínio e não tem rota de interface.

---

## 10. Oportunidades de produto

**Alto impacto / baixo esforço**

1. ~~**Reusar o resolvedor da 017 nas telas da 015**~~ — **feito** (PR #43). O resolvedor foi extraído para `classificacao/domain/nomes.py` e `publicacoes/domain/vocabulario_da_regra.py` em vez de `compor()` ser reaproveitado, que era o desenho certo: `compor()` também define a fronteira pública/individual da 017, e reusá-lo inteiro traria a fronteira junto.
2. **Avisar a quem ficou fora do universo** que houve divulgação (E2E17-004), mesmo sem divulgar resultado por Etapa.
3. **Marcar explicitamente a publicação vigente** — P1 diz que foi sucedida, mas P2 não diz que é a atual; um selo positivo ajuda quem chega pelo link.

**Alto impacto / alto esforço**

4. **Recursos (018)** — é o que legitima "definitivo" (E2E17-005) e o que o Edital já promete.
5. **Divulgação de resultado por Etapa** — fecharia o silêncio para quem sai cedo.
6. **Comunicação ativa** — e-mail ao candidato quando uma publicação que o menciona entra no ar.

---

## 11. Teste institucional — "por que Carla apareceu em 3º?"

Sem alterar nada, um operador autorizado percorre:

| pergunta | onde | o que encontra |
|---|---|---|
| o que foi publicado | página pública de P1 | `3º · Carla Nunes · INS-2026-9HZ9XD68 · Candidatos negros (pretos e pardos) e indígenas · 82,00` |
| quando, por quem, sob que assinatura | mesma página + histórico | 06/09/2026 15:01, `paula.publicadora`, Diretora do Cefor |
| qual ato originou | PDF e trilha | "ATO DE ORIGEM emitido em 06/09/2026, às 14h59" |
| qual regra valia | proveniência do ato | versão normativa citada pelo ato |
| que resultados a sustentam | proveniência | participantes considerados e resultados antecedentes |
| o que separou do 4º | proveniência | **"Critério que separou: MAIOR_VALOR_DE_FATO — valor 40"** (contra 20 de Diego) |
| o público recebeu esse dado? | página pública e PDF | **não** — nem meses, nem nascimento |

O invariante do §10 está provado: **o resultado do desempate é publicável sem expor o fato pessoal que o produziu.**

---

## 12. Evidências

`screenshots/` — 53 imagens na ordem da jornada, de `00-gestao-vazia.png` a `51-achado-404-tecnico-apos-remocao-do-marco.png`, incluindo os negativos (`22`, `23`, `34`, `35`, `45`, `49`) e o achado bloqueante (`E2E17-001-edital-publicado-sem-inscricao.png`).

---

## 13. Hardening pós-017

Sessão de correção conduzida sobre `b8f85fe` — a `main` de então, que já continha o PR #43 — com o
commit desta auditoria integrado. Não abriu a SPEC 018 e não tomou decisão de domínio sobre
recursos.

### O que foi corrigido

| achado | commit | natureza |
|---|---|---|
| E2E17-001 | `60f98f7` | round-trip do rascunho, nos dois caminhos, + auditoria dos cinco serializadores |
| E2E17-002 | `17ab044`, `720038d`, `4032e8a` | recusa sem caminho impossível, todo caminho condicionado à porta, `404.html` institucional |
| E2E17-006 | `99e9f6d` | horário local na recusa por inscrições abertas |
| E2E17-003 | PR #43 + `432112c` | já corrigido antes; sobrou o instante da proveniência |

Cada correção tem teste de regressão que falha sem ela. A suíte inteira passa em SQLite e em
PostgreSQL.

### O que ficou fora, por escopo

E2E17-004 (visibilidade do `ResultadoEtapa` ao candidato), E2E17-005 (autorização de resultado
definitivo) e E2E17-007 (segundo Edital no mesmo Processo) permanecem abertos como registrados.
Os dois primeiros são decisão de governança, não defeito a corrigir às cegas — é o que o próprio
E2E17-005 já dizia.

### O que a sessão observou

- Na prévia de publicação, a trilha "Ato de classificação" e o botão "Cancelar" levavam à tela do
  ato, atrás da mesma porta que o CTA corrigido: o publicador recebia 404 nos dois. Mesma classe do
  E2E17-002, destino diferente, não coberto pelo achado — **fechado depois** (`4032e8a`), e a
  prévia deixou de oferecer qualquer caminho que quem lê não alcance.
- `perfis_persistidos()` perdia `classificationInformation` e `callInformation`, conteúdo normativo
  que **nenhuma tela do assistente escreve**. Corrigido o round-trip; que não haja onde escrevê-los
  pela interface **continua aberto**, e é decisão de produto — não defeito a corrigir às cegas.

---

## 14. Perguntas pendentes para a 018

Registradas, não decididas. A governança é do usuário.

**A. Qual fato institucional torna uma publicação definitiva?**

Hoje é escolha livre de um `<select>`: `publicar_resultado` valida que a natureza está entre as
declaradas e que não há regressão de definitiva para preliminar, e nada mais (E2E17-005). Um ato
que afirma definitividade sem ter o marco que a produz é risco jurídico do tipo que a 015 evitou ao
separar calcular de emitir.

**B. Qual fato institucional autoriza mostrar ao candidato seu Resultado individual da Etapa?**

Hoje a Área do Candidato lê `SituacaoDivulgada`, que só existe para quem estava no universo do ato.
Quem foi eliminado numa Etapa anterior não vê nada — nem que houve resultado (E2E17-004).

**A e B são relacionadas, e podem compartilhar uma primitiva — mas isso é hipótese a investigar, e
não premissa.** As duas perguntam "que fato institucional autoriza o quê", e é razoável que a
resposta tenha a mesma forma. Não se segue que tenham o **mesmo marco temporal**: a definitividade
de uma publicação e a visibilidade de um resultado individual podem depender de fatos distintos, e
declará-las a mesma decisão antes de investigar fecharia a pergunta em vez de respondê-la. A 018
deve verificar se compartilham a primitiva, e não assumir.

**C. Um recurso deferido pode alterar um `ResultadoEtapa` consolidado? Se pode, por qual
mecanismo — anulação, superação, ou outro?**

É bloqueante para a especificação, e não uma consequência a decidir depois. O sistema inteiro é
append-only sobre atos: a 015 sucede atos de ordenação, a 017 sucede publicações, e o
`ResultadoEtapa` consolidado é imutável. Um recurso deferido que mude a pontuação de uma Etapa não
tem, hoje, por onde produzir efeito — e a forma que esse efeito tomar decide o desenho da 018
inteira, porque a cadeia `ResultadoEtapa → ato de ordenação → publicação` teria de reagir a ele.

Sem resposta a C, a 018 não tem o que especificar.
