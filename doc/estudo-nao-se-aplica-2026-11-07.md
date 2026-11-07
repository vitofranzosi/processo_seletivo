# Estudo — o "não se aplica" na conferência dos documentos da convocação — 07/11/2026

**Natureza:** só investigativo. Nada aqui muda código, FR ou decisão. O estudo recomenda, e quem
decide é o responsável pelo produto (governança é do usuário).

**Base:** `main` em `5fcbfa54` (07/11/2026). O guia que motivou o estudo usou a `ffde747b`. Entre as
duas, nada mudou nos arquivos lidos aqui.

**Banco:** `nsa_estudo`, clonado de `gps_docs_demo` (`createdb -T`) sem conexões na origem. A origem
não foi alterada. Cada cenário rodou numa transação desfeita ao final, de modo que um não contamina
o outro. O roteiro e a saída estão no apêndice.

**Marcas de evidência**, usadas em todo o texto:

| Marca | Quer dizer |
|---|---|
| **[T]** | comprovado por teste da suíte (o nome do teste vai junto) |
| **[X]** | comprovado neste estudo, no banco descartável, e **sem** teste na suíte |
| **[C]** | lido no código, sem execução |
| **[S]** | só na spec |
| **[N]** | norma ou Edital da amostra |

---

## Resumo

1. **O GPS tem dois "não se aplica", com a mesma palavra.**
   - O do **item**, automático, vem do recorte publicado (Perfil e modalidade), gravado na lista da
     chamada. Ninguém o escolhe, e o candidato nem vê o item.
   - O da **conferência** é manual: um juízo de quem confere sobre um item que a lista diz que se
     aplica.

   É só deste segundo que a dúvida trata.
2. **O manual é, no código, uma dispensa sem esse nome.** Ele afasta um obrigatório que o recorte
   publicado diz aplicável. Conta como atendido para o aceite, como o "conforme", e só exige motivo
   não vazio: `"."` passa. Quem tem só a alocação à conferência pode escolhê-lo, e no item com
   arquivo não precisa abrir o arquivo.
3. **Ninguém o revê antes do aceite, porque ninguém o vê.** A condução diz *"Pronta para decidir —
   3 de 4 conferidos"* tanto para três "conforme" quanto para três "não se aplica". O formulário do
   aceite não menciona nenhum dos dois. O setor de formalização recebe *"não se aplica"* sem motivo
   nem autor, com o mesmo rótulo do item que o recorte excluiu.
4. **Há uso legítimo, e ele é necessário.** A `044` decidiu (D2) que condição sobre o candidato
   (sexo, idade, vínculo) não ganha recorte. Os Editais da amostra publicam obrigatórios
   condicionados exatamente assim:
   - *"Certificado de Alistamento Militar, no caso de candidatos do sexo masculino"*;
   - *"quando for o caso"*.

   Quem confere aplica esse critério publicado à pessoa. É **inaplicabilidade**, e não dispensa.
5. **Não se achou fundamento para a dispensa excepcional.** Não há nenhum no repositório, nos Editais
   da amostra nem na Constituição. O que os Editais têm é a cláusula de **casos omissos**, que não
   alcança documento expressamente exigido. O 89/2026 diz o contrário: quem não apresentar o
   certificado na convocação *"será desclassificado"* (11.2). **A dispensa fica pendente de decisão
   institucional**, e este estudo não presume que ela seja permitida.
6. **Recomendação: a alternativa A, estreitada**, com sete partes:
   - definir o "não se aplica" da conferência como *inaplicabilidade pelo critério publicado*, e
     nada além disso;
   - mostrar cada um antes do aceite, com quem o registrou e por quê, e pedir ciência expressa de
     quem desfecha;
   - contá-los à parte na condução;
   - levá-los à formalização com o motivo;
   - não criar o estado "dispensado" enquanto a instituição não decidir que a dispensa existe;
   - não criar papel novo;
   - deixar ao produto a escolha de restringir ao gestor o "não se aplica" de obrigatório.

---

## 1. O comportamento comprovado

### 1.1 Onde o estado é definido

| O quê | Onde | Evidência |
|---|---|---|
| Os três resultados, e só eles | `convocacao/domain/nomes.py:237-240` (`RESULTADOS_DA_CONFERENCIA`); `ck_conferencia_resultado` | [C] |
| Motivo obrigatório fora do "conforme" | `ck_conferencia_motivo` (`convocacao/models.py:637-640`) e `conferir` (`application/documentos.py:709-715`) | [T] para o pendente (`test_pendente_exige_motivo_e_o_motivo_volta_ao_estado`); [X] para o "não se aplica" |
| O estado do item, derivado | `domain/documentos.py::estado_do_item`: a conferência vigente "não se aplica" vence qualquer apresentação, anterior ou posterior | [T] (`test_nao_se_aplica_sem_apresentacao_com_motivo`) e [C] para o caso com arquivo |
| Conta como atendido | `ATENDIDOS = (CONFORME, NAO_SE_APLICA)` (`domain/documentos.py:56`) | [C]; [X] para o aceite |
| A guarda do aceite | `desfechar.py::_recusar_inclusao_sem_documentos`, que lê `pendencias_para_incluir` | [T] só com "conforme" (`test_o_aceite_espera_os_obrigatorios_conferidos`); [X] com "não se aplica" |
| A palavra na condução | `LeituraDocumental.contagens`: `"conformes" = CONFORME + NAO_SE_APLICA` (`application/documentos.py:341`) | [X]. A FR-3607 pede a contagem de *conformes*; somar o "não se aplica" nela é escolha da implementação, que a spec não faz |

### 1.2 Quem pode escolhê-lo

O predicado único `pode_conferir_documentos` (`comissoes/domain/autorizacao.py:100`) admite três
bases, cada uma suficiente sozinha:

- a permissão `comissao:gerir`;
- a presidência do Processo;
- a **alocação à conferência**, com restrição opcional por Perfil.

O comando não distingue o resultado escolhido: quem confere registra qualquer um dos três. O alocado
**não** desfecha (FR-3596, D-010).

- [T] `test_o_membro_alocado_confere_e_nao_desfecha`, com um *pendente*;
- [X] `joao.conferente`, só alocado, registrou "não se aplica" nos três obrigatórios do Gael. O
  aceite dele foi recusado como inexistente (`not_found`).

### 1.3 A validação do motivo

Só *não vazio depois do `strip`* [C][X]:

- `"   "` é recusado (`motivo_da_conferencia_obrigatorio`);
- `"."` é aceito;
- `"Dispensado."`, o motivo do experimento de 07/11, também é aceito.

Não há tamanho mínimo, catálogo de fundamentos nem referência à cláusula do Edital.

### 1.4 Revisão por outro papel

**Não existe.** O "não se aplica" registrado pelo alocado tem efeito imediato na guarda do aceite
[X]. O gestor que desfecha é outro papel, mas o que ele vê não o põe diante do "não se aplica"
(§1.6). Uma conferência nova pode substituir a anterior, com motivo de substituição se for sobre a
mesma versão (FR-3586).

Há uma ressalva no **item sem arquivo**. Lá, trocar *pendente* por *não se aplica* **não** pede
motivo de substituição, porque a regra compara versões e não há versão [X]. É o mesmo efeito que
`test_a_pendencia_sem_arquivo_nao_pede_motivo_de_revisao` prova para a revisão da pendência [T].

### 1.5 O efeito no aceite

Os três obrigatórios do Gael em "não se aplica", nenhum conforme, deixam a convocação *pronta para
decidir*. O gestor registra o aceite, e o efeito é `INCLUSAO`, com a apuração seguinte emitida no
mesmo ato [X], pelo alocado (cenários 5–7) e pelo próprio gestor (5b).

O "não se aplica" pode ser registrado **depois do vencimento**, porque a conferência continua
enquanto a chamada estiver aberta (FR-3588) [C]. Assim, o obrigatório que nunca chegou, cuja falta o
Edital pune com desclassificação, vira atendido.

### 1.6 Como aparece a cada ator

| Ator | O que vê | Evidência |
|---|---|---|
| **Candidato** (portal) | Na categoria *Conferido*, *"Não se aplica: ‹motivo›."*, sem autor (FR-3584). No experimento: *"Não se aplica: Dispensado."* | [T] `test_obrigacoes_da_convocacao` (*"Concluiu no Ifes."*); [X] |
| **Conferente** (página dos documentos) | O selo *Não se aplica*, com a **mesma cor** do *Conforme* (`s-PUBLICADO`); o motivo e o autor ficam recolhidos em *Conferências registradas* | [C] `convocacao_documentos.html:33,52-61` |
| **Gestor** (condução e aceite) | *"Pronta para decidir — 3 de 4 conferidos"*. O formulário do desfecho só fala dos documentos quando há **falta**, e a conferência do texto mostra só o fundamento | [X] contagens; [C] `convocacao.html:463-466,525-527`, `views.py:9493` |
| **Auditor** | Na condução, o mesmo estado e a mesma contagem (FR-3598). Na trilha, *"Conferência NAO_SE_APLICA do requisito ‹uuid›…"*, com a base `comissao:conferir_documentos` e **sem** o motivo, por desenho (FR-3603). Não abre a página dos documentos: 403 pelo predicado (D-015, pendente) | [X] trilha; [C] página |
| **Formalização** (`117`) | A situação *não se aplica*, **igual** à do item excluído pelo recorte, sem motivo, autor nem data. O arquivo apresentado não vai | [T] `test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica`; [X] |

### 1.7 Com arquivo recebido

**Cabe**, e sem abrir o arquivo [X]. A identidade do Gael é um documento aproveitado da inscrição.
Ela foi marcada "não se aplica" com motivo `"."`, e a trilha não tem consulta de `joao.conferente`
àquela apresentação.

A conferência grava a apresentação e o hash julgados. A D-012 exige abrir antes só para o "conforme",
com a razão de que *"o documento pode nem ter sido apresentado"*. A razão não cobre o caso em que ele
foi apresentado.

### 1.8 As interações com outros mecanismos

| Mecanismo | Efeito | Evidência |
|---|---|---|
| **Nova versão do candidato** | Recusada (`documento_ja_conferido`): o "não se aplica" tranca o item como o "conforme" | [X]; [T] só para o "conforme" (`test_o_documento_ja_conferido_nao_recebe_outro_arquivo`) |
| **Aproveitamento da inscrição** | O item nasce *recebido* por referência, e pode ser marcado "não se aplica" sem abrir | [X] (Gael, identidade) |
| **Aproveitamento entre chamadas** | O "não se aplica" **não** viaja, porque a conferência não se transporta (D-013). O arquivo que havia viaja e nasce *recebido*; sem arquivo, o item nasce *a apresentar*. A chamada nova exige juízo novo | [C] `_aproveitar`, `_origem_aproveitavel`; [T] para a regra geral (`test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia`) |
| **Retificação** | Ela pode mudar a obrigatoriedade e o recorte (D-014), mas só para as chamadas seguintes. A lista gravada é append-only: um `UPDATE` direto foi recusado pelo gatilho (*"call documents are append-only"*). Na chamada aberta, o único meio de refletir uma Retificação que retirou um documento é o "não se aplica" manual, e a FR-3573 diz que a Retificação **não** vale para ela | [X] gatilho; [S] FR-3573, D-014; [T] indireto (`test_a_raiz_da_chamada_grava_um_item_por_documento_da_convocacao`) |
| **Correção da `120`** | A sucessora usa a lista, as apresentações e as conferências da chamada: o "não se aplica" continua valendo | [S] FR-3573 da `115`, `120` §Conferências da chamada; [T] `test_correcao_da_convocacao.py:567` |
| **Item excluído pelo recorte** | O candidato não envia (404), mas o comando `conferir` **aceita** conferência sobre ele, por exemplo um *pendente* no laudo do Davi. A conferência fica invisível, porque o item não está entre os pedidos | [X] — achado lateral, fora do escopo (§3, R-9) |

### 1.9 O que tem teste e o que não tem

O que a suíte prova sobre o "não se aplica" da conferência:

- o estado, sem arquivo e registrado pelo gestor;
- o texto do portal;
- a situação na formalização.

Nenhum teste cobre:

- o "não se aplica" registrado pelo alocado;
- o item com arquivo;
- o arquivo não aberto;
- o motivo trivial;
- o aceite sem nenhum conforme;
- a tranca contra versão nova;
- a soma na contagem da condução.

Tudo isso foi comprovado aqui [X], e nada disso é regra escrita em FR.

---

## 2. As quatro situações, e as regras

### 2.1 O GPS as distingue?

| Situação | O que é | Como o GPS a representa hoje |
|---|---|---|
| **Não aplicável pelo recorte** | O Edital publica a quem o documento é pedido (Perfil, modalidade), e a pessoa está fora | **Distingue bem**: item `NAO_SE_APLICA` na lista, pela aplicabilidade da `044`. Não é pedido, não aparece ao candidato (FR-3577) e não recebe envio (FR-3582) |
| **Não aplicável por critério publicado sobre a pessoa** | O Edital publica o critério (*"no caso de candidatos do sexo masculino, maiores de 18"*, *"quando for o caso"*), mas a `044` não o representa (D2) | Item **obrigatório** na lista, afastado pela conferência "não se aplica" com motivo livre |
| **Aplicável e conforme** | Apresentado e conforme ao Edital | Distingue: "conforme", com abertura exigida (D-012) |
| **Aplicável e pendente** | Apresentado e insuficiente, ou não apresentado | Distingue: "pendente" com motivo, ou "a apresentar" |
| **Dispensa excepcional** | O documento se aplica, mas é afastado por decisão | **Não distingue.** Cai no mesmo "não se aplica" da conferência, e é indistinguível da linha 2 |

**A confusão está entre a segunda e a quinta linha**, e não entre a primeira e a quinta. A
inaplicabilidade que o recorte resolve já é automática e não passa pelo conferente. O que sobra ao
conferente é afastar um obrigatório, e a palavra não diz se ele o faz por um critério publicado ou
por decisão própria.

**Os próprios testes da suíte usam o "não se aplica" para três figuras distintas:**

- *"Mora no exterior."* (`test_nao_se_aplica_sem_apresentacao_com_motivo`) é fato pessoal, e
  inaplicabilidade se o Edital o prevê;
- *"Concluiu no Ifes."* (`test_obrigacoes_da_convocacao`) é **fato já comprovado ao órgão**, que a
  Lei 14.129/2021 (art. 3º, XIII) veda exigir de novo. É dispensa *ex lege*, não inaplicabilidade;
- *"Mora com os pais"* (`test_conjunto.py`, residência) é **equivalência** de comprovante: o
  documento se aplica e foi atendido de outro modo.

### 2.2 O fundamento normativo

- **[N] Inaplicabilidade por critério publicado: há.** Os Editais 28, 35, 69 e 77/2026 trazem, na
  lista *"(Para todos os candidatos)"*, o alistamento militar *"no caso de candidatos do sexo
  masculino"*. O 146/2025 e o 140/2025 trazem o mesmo. O 69/2026 traz ainda a declaração de
  equivalência de estudos no exterior *"quando for o caso"*, e há o comprovante de votação *"quando
  for o caso"*. A Constituição prevê documento variável por *"condição normativa"* (§Domínio), e a
  D2 da `044` deixou essa condição sem forma estruturada. **Este é o uso que justifica o "não se
  aplica" manual.**
- **[N] Dispensa *ex lege*: há indício, e falta a aplicação.** A auditoria de 03/11
  (`doc/auditoria-matricula-e-dossie-documental-2026-11-03.md`, §6) registra, como **verificados**:
  - a Lei 13.726/2018, art. 3º: certidão de nascimento substituível por documento de identidade;
    título de eleitor só para votar;
  - a Lei 14.129/2021, art. 3º, XIII: vedação de exigir prova de fato já comprovado;
  - o Decreto 9.094/2017, art. 2º: obter da base oficial.

  A própria auditoria reserva a aplicação ao caso concreto à Procuradoria. Esse fundamento apoia
  retirar o documento **da lista do Edital**, não afastá-lo pessoa a pessoa na conferência.
- **[N] Dispensa excepcional por decisão da comissão: não se achou.** Os Editais 28, 35, 57, 69, 76,
  77, 89, 140 e 146 têm só a cláusula de **casos omissos**, que é situação não prevista; documento
  expressamente exigido é situação prevista. O 89/2026 é explícito no sentido contrário: o
  certificado do curso, se não apresentado na convocação, leva à desclassificação (11.1–11.2). A
  Constituição não trata de dispensa, e o Princípio IV pede que *regras que afetem documentação*
  residam no domínio.

  **Pendente de decisão institucional.** Este estudo não presume que a dispensa excepcional seja
  permitida.

### 2.3 As regras atuais e a justificativa de cada uma

| Regra | Justificativa registrada | Avaliação |
|---|---|---|
| Três resultados, motivo obrigatório no pendente e no "não se aplica" (FR-3585) | Nasce do escopo do complemento de 03/11 (§4: *"conforme, pendente com motivo ou não se aplica com motivo"*). **Nenhuma D- trata da semântica do "não se aplica"** | Sem decisão de domínio por trás |
| O aceite admite "conforme" **ou** "não se aplica" (FR-3592 e caso-limite) | O mesmo complemento propunha *"aceite só com os obrigatórios **conformes**"* (§6 do escopo). A spec ampliou sem decisão registrada | **Ampliação sem rastro de decisão** |
| Abrir antes só no "conforme" (D-012) | *"Pendente e não se aplica não exigem abertura: o documento pode nem ter sido apresentado"* | Vale para o item sem arquivo. Para o item com arquivo, a razão não se aplica |
| O alocado confere e não desfecha (D-010) | Separar conferir de desfechar; não presumir competências iguais (D-002) | Correta. Mas o "não se aplica" faz o conferir **decidir** a guarda do desfecho, que é o que a D-010 queria separar |
| A trilha sem o motivo (FR-3603) | LGPD: o motivo pode ter dado pessoal | Correta. A consequência é que o auditor não o vê em lugar nenhum enquanto a D-015 estiver pendente |

---

## 3. Os riscos

| # | Risco | Gravidade | Evidência |
|---|---|---|---|
| R-1 | **Aceite indevido**: obrigatório aplicável afastado sem fundamento, e a inclusão na ocupação, com a apuração seguinte, no mesmo ato | Alta: atinge direito de terceiro (o próximo da lista) | [X] |
| R-2 | **Decisão sem decisor**: o alocado, que por D-010 não desfecha, decide de fato a guarda do aceite; o gestor desfecha sem ver o que foi afastado | Alta | [X] |
| R-3 | **Contorno da consequência do Edital**: "não se aplica" depois do vencimento sobre o que nunca chegou (89/2026, 11.2) | Alta | [C] FR-3588 + FR-3592 |
| R-4 | **Opacidade na decisão**: *"3 de 4 conferidos"*, com o mesmo selo e a mesma cor, contra o Princípio IV (*"tornar visíveis, antes do ato irreversível, o resultado e a sua origem"*) | Média. É a leitura deste estudo, a confirmar | [X] |
| R-5 | **Rastro que não distingue**: a formalização recebe *não se aplica* sem motivo, igual ao do recorte | Média | [T][X] |
| R-6 | **Motivo trivial**: `"."` passa | Média; sozinho é cosmético | [X] |
| R-7 | **Juízo sobre arquivo não aberto**: o arquivo existe, ninguém o abriu, e ele não segue para a formalização | Baixa a média | [X] |
| R-8 | **Recorte desmentido**: o laudo do PcD, que o recorte publicado diz obrigatório, foi marcado "não se aplica" pelo alocado. A cota reservada fica sem a prova que o Edital exige, e é o mesmo risco que a `044` corrigiu na inscrição | Alta | [X] |
| R-9 | *(lateral)* Conferência aceita sobre item que o recorte excluiu, e que fica invisível | Baixa; fora do escopo, registrado como achado | [X] |

---

## 4. Os usos legítimos

1. **Critério sobre a pessoa, publicado no Edital e sem recorte (D2 da `044`).** Alistamento militar
   para quem não é do sexo masculino ou é menor; equivalência de estudos para quem estudou no Brasil;
   comprovante de votação *"quando for o caso"*. É o uso que o desenho precisa preservar. Sem ele, ou
   o compositor declara o documento facultativo, e então ele não trava o aceite de quem deveria
   apresentá-lo, ou o declara obrigatório e trava todos.
2. **Fato já comprovado ao Ifes** (*"Concluiu no Ifes"*), **se** a Procuradoria confirmar a
   aplicação da Lei 14.129, art. 3º, XIII. O certo seria o Edital dizê-lo. Enquanto não diz, é
   dispensa *ex lege*, e precisa de nome próprio ou de decisão.
3. **Retificação posterior à convocação** que retirou ou estreitou o documento. A FR-3573 diz que ela
   não vale para a chamada aberta. Usar o "não se aplica" para antecipá-la é decisão do produto, e
   **não** uso legítimo presumido.

**Não é uso legítimo:**

- afastar documento que o recorte publicado declara aplicável (R-8);
- substituir o "conforme" por comodidade;
- *"Dispensado."* sem fundamento.

---

## 5. As alternativas

**A — Manter o modelo, com salvaguardas.** O resultado continua sendo um só, com três mudanças:

- a semântica escrita passa a ser *inaplicabilidade pelo critério publicado*;
- cada "não se aplica" de obrigatório é mostrado antes do aceite, com autor e motivo, e quem desfecha
  dá ciência expressa;
- a condução os conta à parte, e a formalização recebe o motivo.

Opcionalmente, o "não se aplica" de obrigatório fica restrito à base de gestão.

**B — Separar a inaplicabilidade da dispensa excepcional.** Um quarto resultado, *dispensado*, com
fundamento obrigatório e só para a base de gestão. O "não se aplica" fica restrito ao critério
publicado.

**C — Não permitir afastar obrigatório aplicável.** O "não se aplica" da conferência sai dos
obrigatórios, ou deixa de contar para o aceite. A FR-3592 volta ao *"só conformes"* do complemento.

| Critério | A | B | C |
|---|---|---|---|
| Segurança jurídica | Média a alta: o ato fica nomeado, visível e assinado por quem desfecha | **Baixa enquanto a dispensa não tiver fundamento**: o sistema institucionaliza um ato que a instituição não autorizou | Alta para o certame-padrão, e **frágil** para o critério sobre a pessoa |
| Risco de aceite indevido | Cai: o gestor vê e assina cada afastamento | Cai para a inaplicabilidade e **sobe** na dispensa, que ganha um botão | Mínimo, mas desloca o risco para o facultativo que deveria ser obrigatório |
| Clareza | Boa, se a palavra e a tela disserem *"pelo critério do Edital"* | A melhor no papel, e confusa na prática (*dispensado* × *não se aplica* × *isento*, que é nome de documento militar) | Boa |
| Rastreabilidade | Boa: autor, motivo e ciência no desfecho | Boa | Boa |
| Compatibilidade com as specs | Mantém a FR-3585 e a FR-3592. Revê a FR-3607, a FR-3672 e o caso-limite, e acrescenta uma regra ao desfecho | Revê a FR-3585, a FR-3590, a FR-3592 e a FR-3672, além da `118` | Revê a FR-3585 e a FR-3592, e contraria a D2 da `044` |
| Dados já gravados | Nenhuma migração: a regra nova é de leitura e de comando | Migração de constraint numa tabela append-only. O "não se aplica" antigo não se reclassifica e fica ambíguo para sempre | A guarda teria de decidir o que o "não se aplica" antigo vale |
| Esforço | Pequeno a médio | Médio a grande (`domain`, portal, formalização, templates) | Pequeno no código, e grande no Edital (representar a condição sobre a pessoa) |
| Complexidade | +1 bloco na confirmação e +1 contagem | +1 resultado, +1 regra de permissão e +1 texto em cada superfície | −1 resultado, e reabre a D2 |
| Overengineering | Baixo | **Alto**: modela um ato sem fundamento achado | Baixo no código; o custo vai para o Edital |

**Os papéis existentes bastam.** O alocado confere. `comissao:gerir` e a presidência desfecham, e são
a base natural para afastar obrigatório, se o produto quiser restringir. Nenhuma hierarquia nova se
justifica: a salvaguarda que falta é de **visibilidade no ato de desfechar**, e não de papel.

---

## 6. A recomendação

**A, estreitada.** Em ordem de valor:

1. **Nomear a regra.** O "não se aplica" da conferência sobre obrigatório quer dizer: *o critério que
   o Edital publica para este documento não alcança esta pessoa*. Não é dispensa, equivalência nem
   correção de recorte. O texto de ajuda e o rótulo da conferência dizem isso.
2. **Mostrar antes do aceite e pedir ciência.** A confirmação do aceite e da regularização lista cada
   obrigatório atendido por "não se aplica", com:
   - o nome do documento;
   - quem registrou;
   - o motivo.

   Quem desfecha confirma ter visto. É o Princípio IV aplicado ao único ato irreversível do
   percurso. **É a salvaguarda que resolve R-1, R-2 e R-4 sem papel novo.**
3. **Contar à parte.** A condução diz *"2 conformes, 1 não se aplica"*, e não *"3 conferidos"*. O
   selo do "não se aplica" deixa de ter a cor do "conforme".
4. **Levar o motivo à formalização.** Na `117`, a situação separa:
   - o *não se aplica pelo recorte*;
   - o *não se aplica pela conferência*, com motivo, autor e data.

   O setor que recebe a pessoa precisa saber por que um obrigatório não veio.
5. **Recusar o "não se aplica" contra o recorte de modalidade.** O item obrigatório **por recorte de
   modalidade** (o laudo do PcD, a autodeclaração do PPI) não admite "não se aplica" na conferência.
   A modalidade é o que a pessoa declarou, e afastar a prova dela é desfazer a cota pela porta dos
   fundos (R-8). O critério sobre a pessoa, que é o legítimo, mora nos itens que o recorte não
   condiciona à modalidade: os de todos e os de Perfil.
6. **Não criar o *dispensado*.** Enquanto a instituição não disser que a dispensa existe, por quem e
   com que fundamento, o GPS não oferece botão para ela. O caminho para o caso excepcional continua
   o que existe:
   - a correção por sucessão, com prazo novo (FR-3618);
   - o indeferimento;
   - a Retificação, que vale para as chamadas seguintes.

**Fica para o produto decidir** (§8):

- se o "não se aplica" de obrigatório passa a exigir a base de gestão;
- se o item com arquivo exige abertura também para o "não se aplica";
- o que fazer com o motivo trivial.

O estudo **não** recomenda o mínimo de caracteres: ele produz *"Não se aplica ao caso."* em vez de
*"."*, sem ganho real. A salvaguarda é quem desfecha ver e assinar.

---

## 7. O que mudaria (se a recomendação for aceita)

**FRs e decisões da `115`:**

- **FR-3585**: acrescentar a semântica do "não se aplica" e a vedação no obrigatório por recorte de
  modalidade (item 5). Se o produto restringir, acrescentar também a base de gestão.
- **FR-3592**: o aceite e a regularização com "não se aplica" de obrigatório mostram a lista e pedem
  ciência. Revisar o caso-limite *"Obrigatório marcado 'não se aplica'"*.
- **FR-3607**: a contagem separa *conformes* de *não se aplica*. Hoje a implementação os soma, e a
  FR não manda.
- **FR-3608**: o selo e a ajuda da conferência.
- **D-012**: se o produto decidir, estender a abertura ao "não se aplica" sobre item com arquivo.
- Uma **decisão nova** registra a semântica (inaplicabilidade × dispensa) e a pendência
  institucional da dispensa.

**Outras specs:**

- **FR-3672 da `117`**: separar as duas origens do *não se aplica* e levar o motivo ao manifesto.
  O registro da exportação (FR-3700) hoje guarda identificadores, situações e hashes, e nenhum
  texto livre de conferência. O motivo pode conter dado pessoal, e levá-lo exige rever a FR-3700.
- **`118`**, FR-3722 e FR-3746: a frase do portal pode continuar *"Não se aplica: ‹motivo›."*. Se a
  semântica mudar, rever o caso-limite *"Obrigatório não se aplica por conferência"*.
- **`044`, D2**: não muda. O estudo apoia-se nela.

**Testes que faltam hoje, e que a spec futura deve pedir:**

- o "não se aplica" registrado pelo alocado;
- o aceite com todos os obrigatórios em "não se aplica", que a confirmação mostra;
- a recusa do "não se aplica" no obrigatório por recorte de modalidade;
- a tranca contra versão nova depois do "não se aplica" (hoje provada só para o "conforme");
- a contagem separada na condução;
- a formalização distinguindo as duas origens, com o motivo;
- a troca de pendente por "não se aplica" no item sem arquivo, que hoje dispensa o motivo de
  substituição. Decidir e prender.

**Dados:** o sistema não está em produção (D-013). Os bancos de demonstração têm "não se aplica"
gravados (07/11). Nenhuma das mudanças recomendadas reescreve conferência. As linhas append-only
continuam como estão, e a regra nova é de leitura e de comando.

---

## 8. As decisões do responsável pelo produto

1. **A dispensa excepcional existe?** Se existir: por quem, com que fundamento normativo e em que
   ato. **Depende da Procuradoria.** Sem resposta, o GPS não a oferece.
2. **O "não se aplica" de obrigatório exige a base de gestão**, ou o alocado continua podendo, com a
   ciência no aceite como salvaguarda? Recomendação: manter o alocado com a ciência. Restringir é
   aceitável e barato.
3. **O fato já comprovado ao Ifes** (Lei 14.129, art. 3º, XIII) é tratado:
   - no Edital, retirando o documento da lista de quem já o comprovou;
   - ou na conferência, e então com nome próprio?
4. **O "não se aplica" sobre item com arquivo** exige abrir o arquivo?
5. **A Retificação que retira documento** depois da convocação pode ser antecipada na chamada
   aberta pelo "não se aplica"? A FR-3573 diz hoje que não vale para ela.
6. **O motivo vai à formalização?** Ele pode ter dado pessoal, e o registro da exportação
   (FR-3700 da `117`) hoje não guarda texto livre.
7. **O achado lateral R-9** (conferência aceita sobre item excluído pelo recorte) vira registro em
   `doc/` ou entra na spec futura?

---

## 9. O escopo mínimo de uma spec futura

**Dentro:**

- a semântica escrita do "não se aplica" da conferência e a vedação no obrigatório por recorte de
  modalidade;
- a confirmação do aceite e da regularização: a lista dos "não se aplica" de obrigatório, com autor
  e motivo, e a ciência expressa gravada no desfecho ou na trilha dele;
- a contagem separada na condução e o selo próprio na página dos documentos;
- a formalização distinguindo as duas origens, com o motivo, se a decisão 6 permitir;
- os testes listados no §7;
- conforme as decisões 2 e 4, a base de gestão e a abertura.

**Fora:**

- o estado *dispensado* (decisão 1);
- a condição estruturada sobre o candidato (reabriria a D2 da `044`);
- o catálogo de fundamentos;
- o papel novo;
- a correção da convocação em lote (Frente A);
- o aviso de pendência;
- o Registro Acadêmico;
- o visualizador;
- a fila global;
- a OCR.

---

## Apêndice — os cenários

O banco é `nsa_estudo`, clonado de `gps_docs_demo` no Edital `22d2c6db…`.

As duas chamadas usadas estavam abertas:

- **Gael**, PcD, suplência. Três obrigatórios (identidade aproveitada da inscrição e recebida;
  escolaridade a apresentar; laudo a apresentar) e um facultativo.
- **Davi**, ampla concorrência. O laudo é `NAO_SE_APLICA` pelo recorte.

Os atores foram montados como o seletor os monta:

- `joao.conferente`, sem papel nenhum, só alocado;
- `demo.gestor`, com o papel `gestor`, que dá `comissao:gerir`.

Cada cenário rodou dentro de `transaction.atomic()` desfeita ao final.

| # | Cenário | Resultado |
|---|---|---|
| 1 | Obrigatório conforme | Sem abrir: recusado, `conforme_sem_abertura`. Depois de abrir: aceito, e o item fica *conforme* |
| 2 | Obrigatório sem arquivo | "Conforme": recusado, `conforme_sem_apresentacao`. Aceite: recusado, `documentos_nao_conferidos`, com os três nomes |
| 3 | Obrigatório pendente | Sem motivo: recusado. Com motivo: *pendente*. Trocar para "não se aplica" sem motivo de substituição: **aceito** |
| 4 | Com arquivo, "não se aplica" | Motivo `"   "`: recusado. Motivo `"."`: **aceito**, sem o arquivo ter sido aberto; a conferência grava a apresentação e o hash. Nova versão do candidato: recusada, `documento_ja_conferido` |
| 5 | Três obrigatórios "não se aplica" (alocado, *"Dispensado."*) | A convocação fica *pronta para decidir*. A condução diria *"3 de 4 conferidos"*. O portal mostra *"Não se aplica: Dispensado."* na categoria *Conferido* |
| 6 | Aceite pelo alocado | Recusado, `not_found` |
| 7 | Aceite pelo gestor, depois do 5 | **Aceito**: efeito `INCLUSAO` e apuração seguinte emitida. A formalização mostra três `NAO_SE_APLICA` sem motivo |
| 5b | O mesmo, todo pelo gestor (motivo `"x"`) | Aceito |
| 8 | Laudo PcD | Davi, laudo excluído pelo recorte: o envio é recusado, `not_found`, e um *pendente* conferido sobre ele é **aceito** e fica invisível (R-9). Gael, laudo obrigatório pelo recorte: o "não se aplica" do alocado é **aceito** (R-8) |
| 9 | Retificação | Não executada pela tela. A lista é append-only: `UPDATE` direto recusado pelo gatilho `reject_call_document_mutation`. A Retificação vale só para as chamadas seguintes (FR-3573, D-014) |
| 10 | Aproveitado | Seis apresentações aproveitadas da inscrição, uma por chamada. O cenário 4 já usa uma delas: aproveitada, marcada "não se aplica" sem abrir |

O roteiro (`cenarios.py`) e a saída ficaram no rascunho da sessão, fora do repositório. Para repetir:

```bash
createdb -T gps_docs_demo nsa_estudo
```

Depois, rode o roteiro pelo `manage.py shell`, com `DB_NAME=nsa_estudo` e as variáveis da entrada
`formalizacao-117` do `.claude/launch.json`.
