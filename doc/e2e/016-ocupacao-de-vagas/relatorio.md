# Percurso conduzido — SPEC 016 · Ocupação de Vagas

**Data:** 12/09/2026 · **Branch:** `claude/spec-016-ocupacao-de-vagas` · **Base:** commit `7d199c8`
**Ambiente:** banco isolado `ps_demo_016`, papéis provisionados pelo superusuário local (**26 de 26**
tabelas append-only sem `UPDATE` nem `DELETE` para o runtime — as duas novas desta feature entram
aí), `INTERFACE_SELETOR_IDENTIDADE=true`, servidor em <http://localhost:8016> (entrada
`ocupacao-016` **acrescentada** ao `.claude/launch.json`, sem reescrevê-lo).

**Escopo:** o percurso do [quickstart](../../../specs/016-ocupacao-de-vagas/quickstart.md) pela
interface administrativa contra servidor real — compor o Edital com quadro por modalidade e regra de
corte, publicar, retificar, cortar, apurar a ocupação, suceder a apuração, causar a faixa seguinte
com o déficit e ler o histórico do recorte. O Edital `28/2026` foi montado à mão pela tela: o
`seed_demo` não produz este certame.

## Sobre as evidências

**Não há PNGs em `screenshots/`, e é limitação da sessão, não esquecimento** — o mesmo registrado
pelos percursos da `014`, da `020` e da `025`. O painel de navegador desta ferramenta devolve as
capturas para a conversa e não as grava em disco. Cada achado abaixo traz, no lugar da imagem, a
**URL, o controle e o texto literal observado**.

**O que foi montado fora da tela, e por quê.** As 33 inscrições, as 33 avaliações da Prova de
títulos e a consolidação dela, mais o ato de ordenação do marco, foram criados por um script que
chama os **mesmos commands da aplicação** que a suíte usa (`adicionar_membro`, `alocar`,
`distribuir`, `concluir`, `consolidar`, `emitir_ordem`) — nada entrou direto no banco por SQL, de
modo que autoria, segregação e auditoria ficam verdadeiras. São jornadas da `009`, da `012`, da
`013` e da `015`.

**O que a 016 entrega foi percorrido pela interface, e mais que isso**: a composição inteira do
Edital (nove passos), a publicação com as três assinaturas, uma Retificação completa do ciclo
elaborar → submeter → homologar → publicar, a emissão do corte da `014`, **três avaliações da
Análise documental concluídas uma a uma na mesa**, a consolidação pela presidência e todos os atos
da ocupação.

## Quem atuou

| Identidade | Papel | O que fez pela tela |
|---|---|---|
| `carlos.gestor` | Gestor | criou e ativou o Processo; emitiu o corte, as apurações e a faixa seguinte |
| `ana.elaboradora` | Elaborador | compôs os nove passos do Edital; elaborou e submeteu a Retificação |
| `bruno.homologador` | Homologador | homologou o Edital e a Retificação |
| `diana.publicadora` | Publicador | publicou o Edital e a Retificação, com autoridade signatária |
| `joao.avaliador` | Membro da comissão | concluiu na mesa as três avaliações indeferidas |
| `maria.presidente` | Presidente | consolidou a Análise documental (28 Resultados) |
| `elisa.auditora` | Auditor | leu a trilha de auditoria do Edital |

---

## 1. Veredito

**A feature está entregue pelo canal do ator, e o percurso alcança o que o marco calculado permite
alcançar.** Ler os quatro números, distinguir "ainda não apurada" de zero, ser recusado por falta de
ordem vigente, emitir a apuração, vê-la ficar obsoleta quando o mundo muda, suceder com motivo,
causar a faixa seguinte com o déficit como causa e ler o histórico com a proveniência de cada
apuração — tudo isso acontece pela interface, sem shell e sem banco.

**O ciclo do 77/2026 fecha pela tela** (`SC-081`): ordem emitida → corte com alvo **lido da linha do
quadro** (28) → 3 documentações indeferidas na mesa → apuração `28 / 28 / 25 / 3` → *"Pedir a faixa
seguinte com este déficit"* → a tela do corte passa a dizer **"Geração vigente com 2 faixas"**.

**Seis defeitos foram encontrados, e os seis foram corrigidos nesta sessão, com teste que os
prende.** Dois deles eram afirmações falsas na tela; um deixava uma apuração vencida parecendo
vigente; um deixava uma ação irreversível sem confirmação alguma.

**Dois cenários do guia não são percorríveis como estavam escritos**, e o guia foi corrigido: um
prescrevia um passo que a interface não oferece, e dois dependem de um marco de sorteio que o guia
não mencionava. Nenhum dos dois é defeito de código.

---

## 2. Os seis achados corrigidos

### `E2E16-001` — a tela dizia "deficit", "sera" e "nao", sem acento

**Onde:** `/gestao/editais/<id>/marcos/<marco>/ocupacao`, abaixo dos quatro números.
**Observado:** *"O deficit apurado de 28 vaga(s) sera a causa do ato, e a faixa anterior nao e
revogada"* — e o botão *"Pedir a faixa seguinte com este deficit"*.

**Causa.** A convenção deste repositório escreve comentário de template **sem acento**; a convenção
vazou para o texto visível, onde não vale. E o teste que cobria aquela ação afirmava
`"O deficit apurado de 3 vaga(s)"`: ele **prendia** a grafia errada em vez de acusá-la.

**Corrigido** em `ocupacao.html`, com a asserção do teste reescrita para a frase acentuada inteira e
uma varredura nova em `tests/test_vocabulario_da_ocupacao.py` que lê **só os nós de texto** dos
templates da feature — sem comentário, sem tag e sem atributo, porque `class="acoes"` é
identificador. A varredura tem teste próprio de não-vacuidade.

### `E2E16-002` — corte emitido depois da apuração não a obsoletava

**Onde:** a mesma tela, depois de emitir o corte.
**Observado:** a apuração continuava **vigente** dizendo `Ocupadas 0 · A ocupar 28`, e ainda
oferecia *"Pedir a faixa seguinte"* — quando a faixa recém-criada alcançava 28 pessoas.

**Causa.** `causas_de_obsolescencia` só comparava o corte **quando a apuração citava um**
(`if apuracao.corte_id is not None`). Apurar antes de existir corte é legítimo — o marco pode ainda
não ter cortado —, e o corte que **aparece** muda o número tanto quanto o corte que é sucedido.

**Corrigido** em `selectors.py`: a comparação passou a valer nos dois sentidos, com o caso do marco
que **não corta** preservado (ali não há geração vigente nem corte citado, e os dois lados
concordam). Regressão em `test_obsolescencia.py`, que apura antes do corte, afirma ausência de causa
e então emite o corte.

### `E2E16-003` — a causa exibida afirmava algo falso

**Observado:** corrigido o `E2E16-002`, a tela passou a dizer *"o corte que a alimentou não é mais o
vigente"* sobre uma apuração que **não citava corte algum**.

**Corrigido:** a frase passou a ser *"o corte deste recorte não é o que ela leu"*, verdadeira nos
dois sentidos, nos dois templates.

### `E2E16-004` — causar a faixa seguinte não confirmava nada

**Onde:** o botão *"Pedir a faixa seguinte com este déficit"*.
**Observado:** depois do clique, a tela exibia *"Apuração emitida. O ato é imutável…"* — **frase
falsa**, porque apuração nenhuma foi emitida ali. A única pista de que a faixa existia era ir à tela
do corte e ler "2 faixas".

**Por que importa.** É ação que não se desfaz, e quem a pratica fica sem saber se funcionou — o
convite a clicar de novo.

**Causa.** As duas ações compartilhavam um aviso de sucesso com texto fixo.

**Corrigido:** a view registra **qual** ato aconteceu e a tela diz *"Faixa seguinte emitida com o
déficit apurado como causa. A faixa anterior não foi revogada, e quem já progrediu continua nela."*
Regressão em `test_ocupacao.py` que afirma as duas frases e a **ausência** da outra em cada caso.

### `E2E16-005` — o histórico afirmava que o marco não corta

**Onde:** `/gestao/editais/<id>/marcos/<marco>/ocupacao/historico`, campo **Corte**.
**Observado:** *"nenhum — o marco não corta"* na Apuração 1 de 2 — num marco cuja regra publicada
declara alvo derivado do quadro. Ela apenas foi emitida antes do corte existir.

**Corrigido:** *"nenhum corte alimentou esta apuração"*, que vale nas duas situações que produzem o
mesmo `NULL`.

### `E2E16-006` — `vacancyReversion` era emitida e a forma publicada não a conferia

Encontrado pela `T060`, e não pelo percurso, mas registrado aqui porque é do mesmo grau de
gravidade: a publicação emitia o campo, o degrau 14 o elevava, e `PERFIL_PUBLICADO` não o
transcrevia — o Perfil acrescentado por Retificação nascia **sem** ele. É o defeito que o `T110` da
`014` fechou para `generalCompetitionModalityId`, repetido um degrau depois. Detalhe e correção no
[tasks](../../../specs/016-ocupacao-de-vagas/tasks.md), tarefa `T060`.

---

## 3. Os dois defeitos do guia, e o que foi corrigido nele

### `G16-001` — a Retificação não pode **introduzir** a declaração de reversão

O Cenário 3 mandava *"Retifique o Perfil declarando reversão com espécie ON_BALANCE"*. Publicado sem
`vacancyReversion`, o objeto é nulo e o catálogo da Retificação **não oferece o campo** — verificado
na tela: o grupo do Perfil traz oito campos, e nenhum é o gatilho da reversão.

O comportamento é deliberado e tem teste (`test_o_campo_nao_aparece_onde_o_objeto_nao_existe`), e é
o mesmo do `cutRule` da `014`: o catálogo endereça campos de objeto existente. **O defeito era do
guia**, e ele foi corrigido — publicar já com a declaração, e usar a Retificação para trocar a
**espécie**, que é o caminho que o campo oferece.

**Fica registrado, e é decisão do usuário:** um Edital publicado **sem** a cláusula de reversão não
pode vir a declará-la por Retificação. Normativamente, Retificação que acrescenta cláusula ausente é
caso real.

### `G16-002` — os Cenários 3 e 5 exigem marco de sorteio, e o guia não dizia

Num marco ordenado por **cálculo** existe **um** ato de ordenação, o da linha geral: só o sorteio
publica relação de habilitados **por lista**. Verificado na tela: os recortes `PCD` e `PPI` aparecem
com a quantidade publicada e a ação de apurar, e a emissão é recusada com *"Este recorte não tem
ordem vigente: não há ocupação a apurar"*.

Consequência: **reversão** e **concorrência concomitante** não são alcançáveis num certame calculado
— e o guia levava a pessoa até ali sem avisar. O pré-requisito foi escrito no guia, junto do aviso
de que o sorteio congela a semente a partir de fonte pública externa.

**O que cobre esses dois mecanismos, então:** `tests/integration/ocupacao/test_reversao.py` e
`test_concomitancia.py`, sobre o certame de sorteio com cotas de `tests/fixtures/ocupacao_sorteada.py`,
mais `test_a_tela_nomeia_a_reversao_e_explica_a_divergencia` para o texto da tela. A
[rastreabilidade](../../../specs/016-ocupacao-de-vagas/rastreabilidade.md) diz quais critérios
dependem deste percurso e quais não.

---

## 4. Uma observação registrada, sem correção

### `O16-001` — a trilha de auditoria do Edital não lista os atos da ocupação

`/gestao/editais/<id>/auditoria` promete *"Todo ato praticado sobre este Edital e suas
Retificações"* e mostra 17 registros: criação, rascunhos, submissão, homologação, publicação e o
ciclo da Retificação. **Nenhum** ato de ordenação, corte, consolidação ou ocupação aparece — não é
regressão da `016`, é o escopo que aquela tela sempre teve.

O registro existe e é verificável: `OCUPACAO_APURAR`, com ator, recorte, ordem citada e as
quantidades na razão (`tests/integration/ocupacao/test_auditoria.py`). Quem o exibe é o **histórico
do recorte** (`T058`). Ampliar a tela de auditoria é decisão do usuário, e não escopo desta feature.

### `O16-002` — a tela oferece linha de quadro para a Modalidade declarada como ampla

No passo Perfis, o quadro desenha uma linha *"Ampla concorrência (AC)"* ao lado da linha geral
*"Ampla concorrência"*, com o mesmo texto de ajuda — e preenchê-la torna o Edital impublicável.

**Não é defeito**: verificado de propósito, a Revisão recusa com a frase exata *"A Modalidade
declarada como ampla concorrência tem linha própria no quadro de vagas, e a quantidade dela já está
na linha geral"*, e oferece o link para corrigir. A validação está no lugar certo. O que se ganharia
dizendo-o já no ponto de entrada é conveniência, e é da `025`/`014`.

---

## 5. O percurso, passo a passo

| # | Passo | Quem | Resultado observado |
|---|---|---|---|
| 1 | Criar e ativar o Processo | `carlos.gestor` | `PS-016-OCUPACAO` ativo, Edital `28/2026` em elaboração |
| 2 | Compor os nove passos | `ana.elaboradora` | Perfil de 40 vagas, três Modalidades, quadro `28 / — / 2 / 10`, `AC` declarada como ampla, marco com alvo derivado do quadro |
| 3 | **Contraprova:** preencher a linha da `AC` | `ana.elaboradora` | Revisão **IMPEDE**, com a frase da `O16-002` e link para corrigir |
| 4 | Submeter, homologar, publicar | três identidades | Publicado, com autoridade signatária registrada |
| 5 | **Abrir a ocupação antes de qualquer ato** | `carlos.gestor` | três recortes, cada um *"Ocupação ainda não apurada"* + `Publicadas` + ação de emitir. **`UX-032a` e `SC-078` literais** |
| 6 | **Contraprova:** apurar sem ordem vigente | `carlos.gestor` | *"Não foi possível apurar: Este recorte não tem ordem vigente"*, e nada mudou |
| 7 | Retificar o encerramento das inscrições | três identidades | Retificação publicada, uma alteração declarada |
| 8 | Emitir a apuração da ampla (ainda sem corte) | `carlos.gestor` | `28 / 28 / 0 / 28`, histórico e sucessão oferecidos |
| 9 | Emitir o corte | `carlos.gestor` | alvo **28**, *"lido da linha do quadro de vagas deste recorte"*; 28 progridem, 5 fora |
| 10 | Reabrir a ocupação | `carlos.gestor` | **`E2E16-002`**: a apuração aparecia vigente. Corrigido → **obsoleta, com a causa nomeada**, e a ação da faixa deixa de ser oferecida |
| 11 | Indeferir três documentações na mesa | `joao.avaliador` | 28 de 28 concluídas, três com parecer próprio |
| 12 | Consolidar a Análise documental | `maria.presidente` | 28 Resultados, 25 Habilitada e 3 Eliminada, com quem avaliou e quem consolidou |
| 13 | **Contraprova:** suceder sem motivo | `carlos.gestor` | o campo é obrigatório na tela, e o pedido não é enviado |
| 14 | Suceder com motivo | `carlos.gestor` | **`28 / 28 / 25 / 3`** — os quatro números do Cenário 4 |
| 15 | Pedir a faixa seguinte com o déficit | `carlos.gestor` | **`E2E16-004`**: nenhuma confirmação. Corrigido. A tela do corte passa a dizer **"Geração vigente com 2 faixas"** |
| 16 | Ler o histórico do recorte | `carlos.gestor` | duas apurações, a primeira **sucedida** com `28/28/0/28`, a vigente com `28/28/25/3`, cada uma citando versão, linha do quadro, ordem e corte. **`E2E16-005`** aqui |
| 17 | Ler a trilha de auditoria | `elisa.auditora` | 17 registros do ciclo do Edital; **`O16-001`** |

---

## 6. O que este percurso não alcançou

- **Reversão de cota e concorrência concomitante** — exigem marco de sorteio (`G16-002`). Cobertas
  por teste automatizado sobre certame de sorteio com cotas.
- **A contraprova do 57/2026** (`SC-080`, nenhuma vaga atravessa Perfil por nenhum caminho da
  interface) — exigiria dois Perfis com quadro e ordem própria, e o caminho de aplicação está
  provado em `test_nenhuma_vaga_atravessa_perfil_em_certame_de_sorteio`.
- **O teto de abertura** (`SC-082`) — medido por `tests/performance/test_ocupacao.py`, e não por
  percurso.
- **A contraprova de imutabilidade pelo shell** — `UPDATE` direto recusado por gatilho **e** por
  privilégio ausente. É sobre o banco, não sobre a jornada, e o guia já a marca assim; as duas
  camadas são verificadas por `tests/unit/ocupacao/test_apuracao_append_only.py` e pelo `26 de 26`
  do provisionamento.
