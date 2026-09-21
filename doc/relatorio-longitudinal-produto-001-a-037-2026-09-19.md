# Evolução do Sistema de Processos Seletivos — da `001` à `037`

> **Este documento entrou no git dois dias depois de ter sido escrito, e parte dele está vencida.**
> Ele é o retrato de **19/09/2026**, contra a `main` em `0c96283` — antes da `037` e da `038`, que
> hoje estão mescladas. Foi escrito fora do repositório e ficou fora dele; a
> [auditoria de convergência de 20/09](auditoria-de-convergencia-pos-038-2026-09-20.md) registra, na
> seção *"O que esta auditoria NÃO fez"*, que esta fonte **não existia**. É a repetição exata do caso
> que a [varredura dos dezessete](varredura-dos-dezessete-2026-09-19.md) documentou como lição de
> método — e é por isso que ele é versionado agora, com este aviso, em vez de corrigido ou descartado.
>
> **Não edite o corpo.** O que segue abaixo é o texto original, palavra por palavra. A conferência
> contra a `main` de hoje está aqui no topo.

**Conferido em:** 21/09/2026, contra a `main` em `fa4b5b2` — `037` (`#144`) e `038` (`#149`)
mescladas, `specs/` termina em `038`.

## O que nele já está vencido

| Onde | O que dizia | O que vale hoje |
|---|---|---|
| §1, tabela de notas | dez dimensões, com a visão global em **5** | superseded pela [convergência de 20/09](auditoria-de-convergencia-pos-038-2026-09-20.md) §6-bis, que **mediu** o que aqui era projeção — e a contradiz: visão global **6**, não os 8 projetados, e *previsibilidade* **cai** de 9 para 8 por causa da `038` |
| §10, fricção 1 | a visão global não acompanha o Processo vivo | a `038` construiu o painel. A direção recomendada aqui — *"prolongar o Pulso, sem dashboard separado"* — foi a adotada, e a convergência §20 a reafirma. O que resta é `N-01`…`N-04`, achados da feature nova |
| §10, fricção 10 · §13.1 · §18 · §19 (`P2`) | a `037` em deriva de integração, com artefatos falando em 32 tabelas | **fechado.** `037` mesclada; `33 de 33` provisionadas |
| §13, quick wins 3, 4 e 5 | destino do corte · régua *"vencido"* · peso antecipado | **fechados pela `037`**, conforme a matriz da convergência §4 |
| §19, *Ordem recomendada*, item 2 | *"tomar as cinco decisões de governança"* | **tomadas** em 19/09 (`D-G1`…`D-G5`). Quatro seguem **não executadas** — é outra pendência, não esta |
| §19, `P0` | *"nenhum `P0` aberto"* | a convergência abriu dois `S3` na `038`: `N-01` (frase de ausência que afirma fato global) e `N-02` (recurso aguardando admissibilidade é invisível) |
| §17, tabela de engenharia | 93.510 linhas · 4.552 `def test_` · 37 specs · 7.398 passando | **94.414** · **4.620** · **39** pastas em `specs/` · 7478 passando e 1 instável (convergência §2) |

**A tabela de engenharia da §17 reproduz exatamente.** Medida hoje contra `0c96283` pelo mesmo
método — linhas `.py`/`.html`/`.js` sob `backend/processo_seletivo`, e `^def test_` no nível de
módulo —, ela devolve **93.510** e **4.552**, os números impressos. A série é auditável, e é o único
lugar do repositório onde a trajetória de engenharia de 28/08 a 19/09 está registrada.

## O que ele mede que ninguém mais mede — conferido no código

Sete coisas. As três primeiras são **lacunas de cobertura** que a §3 nomeia e que nem a convergência
nem a varredura tocam; as quatro seguintes são achados dele, reconferidos aqui contra a `main`.

| # | Achado | Estado em 21/09 | Como foi medido |
|---|---|---|---|
| 1 | **divergência real entre duas avaliações da mesma inscrição** | 🔴 **aberto, e mais preciso do que o texto diz** | A unicidade é **por pessoa** — `uq_avaliacao_concluida_por_pessoa` em `avaliacoes/models.py:136` —, de modo que dois membros atribuídos à mesma inscrição concluem os dois. A consolidação então devolve `NAO_CONSOLIDAVEL` com a frase, literal em `resultados/application/prontidao.py:93`: *"há {quantas} avaliações concluídas onde o Edital prevê uma, e o sistema não escolhe qual vale"*. **Não há mecanismo de resolução**: zero ocorrências de média entre avaliações, terceiro avaliador ou desempate. A única saída é a reabertura pela presidência (`FR-074`), que **descarta** uma avaliação em vez de resolver a divergência |
| 2 | **heteroidentificação como fluxo próprio** | 🔴 **aberto** | **zero** ocorrências de `heteroidentifica` em `backend/processo_seletivo/`. Aparece só em specs, como matéria fora de escopo |
| 3 | **barema estruturado e grupos em cascata** | 🔴 **aberto** | **zero** ocorrências de `barema` no código de produto. É a borda do cenário 6a, que nunca foi montado |
| 4 | **passagem de bastão fora da navegação ativa** (§3) | 🟠 **parcialmente vencido, e o resto compõe com `N-04`** | Notificação **existe** — três módulos com `send_mail`: convocação, código de acesso e inscrição. Os três escrevem **ao candidato**. Nenhuma mensagem vai a avaliador, gestor, comissão ou julgador: `send_mail` não aparece em `avaliacoes/`, `comissoes/`, `resultados/`, `recursos/` nem `classificacao/`. O trabalho interno só se descobre abrindo o painel — e a convergência mediu que **9 dos 15 sinais do gestor não têm caminho** (`N-04`) |
| 5 | **`E-3` — duas gramáticas do mesmo fato normativo** (§12, §13 quick win 7) | 🟠 **aberto, com outra forma; e a recomendação do relatório está errada** | A convergência deixou `E-3` como `[NÃO REAUDITADO a fundo]`. Reauditado aqui: **as telas internas já não mostram caminho cru**. `interface/views.py::_onde_e_campo` traduz `/schedule/id=…/endAt` para português, e o docstring nomeia a auditoria de 13/09 como causa. Mas a tradução existe **duas vezes**: `CAMPO_EM_PORTUGUES` (gestão, em `views.py`) e `COLECOES`/`OPERACOES` (portal, em `publicacoes/domain/alteracoes.py`, **um único consumidor**: `portal/leitura.py`). São duas tabelas de vocabulário paralelas, que derivam em silêncio. **O quick win 7 — *"usar o renderizador humano também na tela interna"* — não se aplica:** o próprio docstring de `alteracoes.py` explica por quê — *"a tela de homologação da gestão precisa do antes e do depois"*, e o portal recusa devolvê-los por decisão (`D-009`). O conserto é **uma tabela**, não um renderizador |
| 6 | **a Classificação concentra decisão demais** (§10, fricção 8) | 🔴 **aberto, e cresceu** | O relatório contou 28 controles em 19/09. Hoje `_marco.html` declara **42** `input`/`select`/`textarea` — revelados condicionalmente —, e o template se repete **por marco, por Perfil**. A convergência não remediu esta tela |
| 7 | **specs implementadas que seguem `Status: Draft`** (§17, alerta) | 🔴 **aberto, e é o mais fácil de medir** | **32 das 39** pastas de `specs/` carregam literalmente `**Status**: Draft` — inclusive a `038`, mesclada e em produção. Outras **três** não têm linha de `Status` nenhuma. Só a `003` e a `004` declaram conclusão; a `031`, implementada, ainda diz *"pronta para implementação"*. Nenhum outro documento do `doc/` registra isso |

**Achados dele que continuam válidos, mas já têm dono em outro documento** — e por isso não se
contam aqui: `E-4` (fontes sem confronto), `ACH-60` (trabalho sem recorte por Perfil/polo),
Retificação que não acrescenta Modalidade (`D-G5`), as sete recusas em 404 (`D-G2`), e a matrícula
não validada no destino. Os cinco estão medidos na
[convergência de 20/09](auditoria-de-convergencia-pos-038-2026-09-20.md) §4 e §16.

---


**Data do retrato:** 19/09/2026  
**Código entregue analisado:** `main` em `0c96283` — inclui a implementação da `036`  
**Fronteira da análise:** a `037` tem especificação mesclada, mas sua implementação ainda está em
uma worktree, sem commit final, sem rastreabilidade concluída e sem a suíte completa registrada.
Portanto, ela aparece neste relatório como **trabalho em curso**, e não como capacidade entregue.

---

## 1. Resumo executivo

### Veredito

**Sim: o sistema está indo na direção certa.** A mudança não é apenas aumento de funcionalidade.
Entre 28/08 e 19/09, o produto mudou de natureza:

- no início, era sobretudo um núcleo normativo sólido, capaz de criar, aprovar, publicar e
  preservar a história de um Edital;
- em 02/09, o percurso operacional chegava bem até a avaliação, mas ainda não constituía um ciclo
  seletivo completo;
- em 13/09, já havia um percurso do início ao fim, porém ele dependia de descoberta acidental em
  pontos centrais e deixava consequências importantes aparecerem tarde;
- em 16/09, a auditoria com seis cenários reais mostrou que a espinha funcionava para famílias
  diferentes, mas sorteio, reservas, suplência e convocação ainda não fechavam;
- de `029` a `036`, o foco mudou de acrescentar telas para **fechar a cauda, antecipar recusas,
  alinhar navegação à autorização e entregar ao ator a informação necessária no momento da
  decisão**;
- hoje, com a `036` na `main`, o sistema sustenta um percurso institucional muito mais completo:
  composição, publicação, inscrição, organização do trabalho, avaliação, consolidação,
  classificação, resultado, recurso instruído, ordem por lista, sorteio auditável, ocupação,
  convocação e início da matrícula.

O principal ganho de UX é este: **o produto passou a ensinar uma parte relevante do domínio pela
própria operação**. Processo × Edital, publicação imutável, Retificação, forma da Etapa,
consolidação, classificação, ato publicado, sucessão e auditoria já não dependem principalmente de
manual.

O principal limite também é claro: **o produto explica bem cada estação, mas ainda não mostra bem a
viagem inteira enquanto ela acontece**. A visão de Supervisão traz inscrições, cronograma e alertas
de distribuição, mas não reúne o estado operacional da cauda: avaliações, sorteios, resultados,
recursos, ocupações, convocações e matrícula. A página do Processo, por sua vez, lista os Editais e
oferece essencialmente os atos de encerrar ou cancelar. É por isso que a visão global permanece a
pior dimensão.

### Quão perto está da meta de “não precisar de manual”?

Para um servidor que **conhece processos seletivos**, mas nunca usou o produto, o sistema está
próximo de ser operável com orientação pontual, não treinamento intensivo. Para um servidor novato
também no domínio, ainda será necessário apoio institucional para regras legítimas — reservas,
recursos, impedimentos, composição de comissão e atos normativos —, mas já não é razoável exigir
que ele conheça a arquitetura interna do software para executar a maior parte do fluxo.

Minha síntese é:

- **execução local das tarefas:** forte;
- **integridade, história e auditabilidade:** muito forte;
- **encadeamento ponta a ponta:** forte e agora quase completo nas famílias percorridas;
- **visão transversal e coordenação do processo vivo:** ainda mediana;
- **generalização para casos reais:** boa, com bordas conhecidas em polos, barema, cascatas e
  práticas institucionais de sorteio;
- **prontidão para operação real:** tecnicamente próxima, mas ainda condicionada à resolução das
  lacunas estruturais, às integrações de produção e a uma rodada com usuários reais.

### Notas atuais

Estas notas não fingem ser uma nova execução integral dos seis cenários. A coluna de 16/09 é a
medição completa; a coluna atual combina os percursos documentados de `029`–`036`, a suíte, a
rastreabilidade e uma inspeção da `main` com banco novo e `seed_demo`. Onde não houve reauditoria
integral, a confiança está declarada.

| Dimensão | 16/09, medida | Atual, até `036` | Confiança | Leitura |
|---|---:|---:|---|---|
| Clareza conceitual | 7 | **9** | alta | Cinco conceitos centrais passaram a ser definidos no ponto de uso; a composição ficou progressiva. A `037` corrige mais uma contradição, mas ainda não está entregue. |
| Encontrabilidade | 7 | **8** | alta | A `033` passou a derivar ações pelo destino que o ator alcança. Ainda há link condicional, edição distribuída e recusas fora das portas. |
| Previsibilidade | 5 | **9** | alta | A `032` antecipa inexequibilidade antes da publicação e nomeia falta, entidade e local de correção. |
| Fluxo ponta a ponta | 4 | **9** | média-alta | `034` e `035` fecharam reserva/sorteio; `036` fechou a instrução do recurso, último `P0`. Falta repetir os seis percursos numa única rodada atual. |
| Organização do trabalho | 7 | **7** | alta | Comissão, alocação e mesa são fortes; distribuição ainda não conhece Perfil/polo/modalidade. |
| Experiência do candidato | 8 | **8** | média | O núcleo continua forte e a `036` acrescenta o parecer; requerimento de matrícula da `029` ainda não teve reauditoria própria. |
| Avaliação | 9 | **9** | alta | Continua sendo o artefato mais maduro do produto. |
| Resultado e publicação | 8 | **9** | alta | Cálculo, ato e divulgação são distintos; obsolescência e sucessão são visíveis; sorteio passou a produzir ordem verificável. |
| Recuperação de erros | 7 | **8** | alta | Muitos erros agora aparecem antes do ato imutável; sete recusas ainda terminam em 404 uniforme. A `037` deve melhorar, mas não entra na nota. |
| Visão global do Processo | 5 | **5** | alta | A Supervisão é útil, porém cobre sobretudo inscrições, cronograma e distribuição. O estado vivo da cauda permanece fragmentado. |

**Não se deve calcular média.** Um produto pode ter avaliação 9 e visão global 5 ao mesmo tempo.
Essa assimetria é justamente o diagnóstico atual.

### Por que “fluxo ponta a ponta” foi 7 em 13/09 e 4 em 16/09

Isso não representa uma regressão do produto. Em 13/09, “ponta a ponta” significava principalmente
conseguir atravessar um cenário pontuado até resultado e recurso. Em 16/09, a régua foi ampliada
para seis arquétipos reais e passou a exigir também sorteio, reservas, suplência e convocação. A
nota caiu porque a auditoria ficou mais completa e revelou que a cauda não generalizava. `034` e
`035` atacaram exatamente essa descoberta. Comparar as duas notas sem essa mudança de cobertura
produziria uma conclusão falsa.

---

## 2. Como esta análise foi construída

### Evidências usadas

1. histórico Git desde a criação do código em 28/08;
2. Constituição, `AGENTS.md`, specs, planos, tarefas, pesquisas, contratos, quickstarts e matrizes de
   rastreabilidade;
3. auditoria inicial de 02/09;
4. auditoria ponta a ponta de 13/09;
5. reauditoria de 16/09, com seis cenários e amostra de 101 PDFs reais;
6. reavaliação de 18–19/09, com os deltas de `030` a `035`;
7. implementação e percurso documentado da `036`;
8. código e estado de trabalho da `037`;
9. inspeção atual da `main`, com PostgreSQL isolado, migrations, provisionamento das proteções,
   `seed_demo` e navegação pela gestão.

### Limite metodológico

Isto é uma **análise longitudinal do produto**, não uma repetição hoje, do zero, de todas as ações
do prompt original. Os percursos completos foram realizados nas auditorias anteriores e nos
quickstarts das features. Hoje foram reconferidos o estado do repositório, a fronteira entregue, o
ambiente atual e telas-chave.

Consequências:

- achados atuais de código e UI têm evidência direta;
- deltas de `034`–`036` têm evidência de percurso e testes, mas as notas globais não foram todas
  remedidas numa única sessão;
- `029` e `031` acrescentaram superfícies relevantes de matrícula que ainda não receberam a mesma
  profundidade de auditoria de UX;
- não houve pesquisa com servidores e candidatos reais; as personas foram simuladas por análise
  especializada;
- a `037` não é contabilizada como pronta.

---

## 3. O teste ponta a ponta que sustenta o retrato

### Cenários cobertos na auditoria de 16/09

| Cenário | Cobertura | Onde parava em 16/09 | O que mudou depois |
|---|---|---|---|
| 1 — seleção simples | 1 Perfil, vagas, Etapa pontuada, resultado e recurso | resultado definitivo dependia da janela; convocação sem corte era inalcançável | `032` antecipa executabilidade; `033` conduz; `036` instrui o recurso; `034` fecha a cauda de ocupação/convocação |
| 2 — análise e classificação | comissão, alocação, distribuição, dois avaliadores, consolidação, classificação e sucessão | divergência entre avaliações não foi exercitada | mesa e consolidação continuam fortes; ausência de reexecução da divergência permanece |
| 3 — sorteio | método, população e marco por sorteio | não havia execução, semente, manifesto nem verificação pública | `035` tornou o método computável e o sorteio executável, reprodutível e publicamente verificável |
| 4 — modalidades e reservas | AC/PcD/PPP, quadro, documentos, inscrição, corte e ocupação por recorte | recortes reservados não produziam ordem utilizável nem convocação | `034` produz ordem por lista de concorrência e alimenta ocupação e convocação |
| 5 — curso/formação | duas turmas, cotas, reversão, sorteio | parava no congelamento do universo | `035` fecha a execução; permanece a questão de o conceito Perfil carregar turma/horário |
| 6a — orientador de TFC | grupos em cascata, pesos, barema e alvo por código | execução completa não foi montada; barema/cascata não têm representação própria | não houve mudança estrutural nessas bordas |
| 6b — pós-graduação em 7 polos | 21 recortes, 280 vagas, reversão por polo, 7 marcos | publicado, sem executar sorteio e sem heteroidentificação representável | sorteio fecha; organização do trabalho por polo continua ausente |

### O que segue sem cobertura suficiente

- divergência real entre duas avaliações da mesma inscrição;
- heteroidentificação como fluxo próprio;
- barema estruturado e grupos em cascata;
- operação cotidiana de matrícula e exportação por usuário do Registro Acadêmico;
- comportamento sob escala humana real: dezenas de Editais simultâneos, equipes locais e muitos
  recursos;
- notificações e passagem de bastão fora da navegação ativa;
- identidade, armazenamento e retenção em infraestrutura de produção.

---

## 4. Linha do tempo: o que o sistema era e no que se transformou

### 28–29/08 — `001` a `005`: primeiro a verdade normativa

O projeto começou pela parte mais difícil de corrigir depois: história, integridade e identidade
dos objetos. Processo, Edital, publicação, Retificação, consulta pública, encerramento, cancelamento,
endereçamento estável e snapshot nasceram antes do restante da operação.

**Efeito no produto:** desde cedo, publicação não era mero `status`; era ato imutável. O sistema
preservava autoria, instante, versão e sucessão. Isso evitou que a UX posterior fosse construída
sobre um modelo que permitisse “editar o passado”.

**Custo inicial:** o núcleo sabia preservar o processo melhor do que conduzi-lo.

### `006` a `012`: instituição, candidato e mesa de trabalho

Entraram composição institucional, oferta, inscrição, área do candidato, comissão, alocação,
distribuição e avaliação.

Na auditoria de 02/09, o sistema já apresentava bons trechos para candidato, comissão e avaliador,
mas o arco terminava na avaliação. A “mesa” já era promissora; resultado, recurso, sucessão e
convocação ainda não formavam uma jornada.

### `013` a `021`: resultado, classificação, recursos e sorteio auditável

O produto ganhou resultado, corte, classificação, ocupação, publicações, recursos, convocação,
anexos e a base de sorteio auditável.

Em 13/09 foi possível percorrer um fluxo inteiro. Porém, o resultado revelava a diferença entre
**existir** e **ser operável**:

- recursos não tinham porta natural;
- publicar resultado era encontrabilidade E2/E3;
- a Classificação concentrava dezenas de decisões;
- consequências apareciam depois de publicar;
- a Supervisão não refletia resultado e recurso vivos;
- a Retificação pública era humana, mas a tela interna ainda vazava gramática técnica.

### `022` a `028`: supervisão, reaproveitamento, descoberta e consistência da oferta

Entraram supervisão, reaproveitamento de Edital, descoberta pública, quadro de vagas, contrato de
mutabilidade, declaração única de vagas e proteção contra cronograma reaproveitado.

Esse bloco corrigiu incoerências sérias: o sistema deixou de publicar uma quantidade e operar com
outra; passou a aceitar um segundo Edital no mesmo Processo; e começou a revelar mais do estado
operacional.

### `029` a `031`: depois da convocação e uma composição que se explica

- `029`: requerimento de matrícula estruturado, reaproveitando dados conhecidos;
- `030`: composição com definições, defaults, revelação progressiva e consequências mais próximas
  da escolha;
- `031`: exportação para matrícula, preservando desconhecido como vazio em vez de inventar dado.

Aqui aparece uma maturidade importante: o sistema não tenta apenas produzir o resultado seletivo;
ele começa a entregar a passagem para a atividade acadêmica.

### `032` e `033`: prevenir antes do dano e navegar pelo que se pode fazer

A `032` é a virada mais clara de qualidade operacional. Como publicação é imutável, descobrir
depois que sorteio, reserva, marco ou convocação eram inexequíveis era particularmente caro. A
feature trouxe o erro para antes da publicação e passou a dizer:

- qual entidade está incompleta;
- o que falta;
- por que isso impede a execução;
- em qual etapa se corrige.

A `033` alinhou as ações oferecidas às capacidades do ator e aos destinos que ele realmente alcança.
Fechou o caminho para publicar resultado e substituiu parte dos 404 mudos por recusas que nomeiam a
base necessária.

Esse par explica a subida de previsibilidade de 5 para 9: a interface passou de “deixar errar e
recusar depois” para “mostrar a inviabilidade antes do ato”.

### `034` e `035`: a cauda deixa de ser apenas declarativa

A `034` produziu ordem própria por lista de concorrência e ligou reserva de vagas à ocupação e à
convocação. A `035` transformou a prosa do método de sorteio em dados computáveis e fechou:

**população elegível → congelamento → semente → execução → ordem → manifesto → verificação**.

Isso resolve o diagnóstico de 16/09: o sistema elaborava e publicava muito bem, mas cedia na
condução. Depois dessas duas features, a cauda deixou de ser o principal gargalo.

### `036`: o recurso passa a ser decidido com a prova

A `036`, agora na `main`, fecha o último `P0` aberto:

- o candidato eliminado lê o motivo e o parecer que fundamentou o resultado;
- quem julga recebe o parecer/documento por **ato de instrução daquele recurso**, não por ampliação
  permanente de papel;
- o alcance termina com decisão ou inadmissão;
- a trilha registra quem autorizou, quem acessou, quando e qual foi o escopo, sem copiar o conteúdo
  sensível;
- nada de outro candidato ou de outro recurso atravessa a fronteira.

É uma solução coerente com o domínio e com a proteção de dados. Em vez de “dar mais permissão ao
julgador”, o sistema modela o ato administrativo que justifica aquele acesso.

### `037`: acabamento de quatro becos, ainda em implementação

A especificação reúne quatro situações nas quais o sistema já sabe a resposta, mas não a entrega no
ponto da decisão:

1. o destino do corte some quando justamente falta a regra;
2. bloqueios dizem que não pode, mas não dizem a quem pedir;
3. um período em curso é chamado de vencido pela gestão;
4. o peso parece opcional e só vira obrigatório nove etapas depois.

O código em trabalho já aponta para as soluções corretas: destino sempre oferecido a quem o alcança,
caminho conforme a causa da recusa, formulação centralizada de autorização, régua de calendário
coerente e contradição do peso antecipada no marco.

Mas **não deve ser contabilizado ainda**. A worktree está baseada antes da implementação final da
`036`; os artefatos ainda falam em 32 tabelas protegidas, enquanto a `main` atual protege 33; as
tarefas seguem desmarcadas; e faltam rastreabilidade, quickstart final e suíte completa.

---

## 5. Antes e depois do fluxo completo

| Trecho | Antes | Hoje, até `036` | Julgamento |
|---|---|---|---|
| Concepção | núcleo de Processo/Edital correto, mas pouco percurso | criação e múltiplos Editais com relação explícita | 🟢 natural |
| Composição da oferta | configurações densas, ajuda invisível ou distante, consequência tardia | passos progressivos, conceitos apresentados, defaults e executabilidade prévia | 🟢/🟡; Classificação ainda é densa |
| Publicação | já forte e imutável | continua forte, agora com mais pré-condições verificadas antes | 🟢 padrão a preservar |
| Descoberta e inscrição | boa desde `009`/`010` | filtros, prazo, documentos contextuais, comprovante e versão aceita | 🟢 |
| Comissão | composição e alocação já boas | capacidade, alocação e distribuição coerentes | 🟢 localmente; 🟡 em múltiplos polos |
| Avaliação | mesa já promissora | fila real, regra à vista, leitura registrada, avanço e recuperação | 🟢 melhor bloco |
| Consolidação | existia, com algum vocabulário opaco | mostra regra, números e por quê | 🟢 |
| Classificação | densa, difícil de encontrar e sem cauda completa | ordem, corte, recortes e destinos mais claros | 🟢/🟡 |
| Resultado | cálculo e ato fortes, acesso ruim | caminho por capacidade, prévia, diff e sucessão | 🟢 |
| Recursos | porta e prova ausentes | portal, caixa, instrução, decisão, efeito e auditoria | 🟢 com a `036` |
| Sorteio | método declarado em prosa, não executável | método computável, execução e verificação pública | 🟢; há divergência com a prática institucional real |
| Reservas | quadro e inscrição existiam; apuração não fechava | ordem por lista, ocupação e convocação | 🟢 nas regras suportadas |
| Convocação/suplência | beco operacional | alimentadas por ordem e ocupação | 🟢 nos cenários percorridos |
| Matrícula | ausente | requerimento e exportação existem | 🟡 ainda não reauditoriado |
| Retificação | forte conceitualmente | história, diff e versão preservados | 🟢; não acrescenta Modalidade |
| Visão global | quase ausente | há pulso e alertas, mas a cauda segue fragmentada | 🟡 principal lacuna |

### Jornada atual resumida

**Processo → Edital → Perfis/vagas/modalidades → cronograma → Etapas → marcos → publicação →
inscrição → comissão/alocação/distribuição → avaliação → consolidação → ordem/corte/sorteio →
resultado preliminar → recurso instruído → resultado sucessor/final → ocupação/convocação →
matrícula → Retificação**

Hoje, essa sequência é mais do que uma lista de entidades: há caminhos reais entre quase todas as
partes. O que falta é uma superfície que conte, no presente, **onde cada Edital está nessa sequência,
qual é o próximo compromisso e quem precisa agir**.

---

## 6. O sistema ensina seus conceitos?

### Conceitos atualmente bem ensinados

| Conceito | Como a interface o ensina | Avaliação |
|---|---|---|
| Processo × Edital | Processo reúne Editais; cada Edital possui fluxo e publicação próprios | claro para novato e especialista |
| Publicação | ato consciente, autoral, datado e irreversível | excelente |
| Retificação | correção por nova versão, não edição silenciosa | excelente |
| Etapa de avaliação | forma, efeito e condições aparecem antes da escolha | muito bom |
| Avaliação × consolidação | trabalho individual separado da decisão consolidada | muito bom |
| Resultado calculado × publicado | ordem técnica não se confunde com ato de divulgação | excelente |
| Sucessão/obsolescência | versão posterior substitui a anterior sem apagar história | excelente |
| Sorteio auditável | método, população, semente, execução e manifesto têm papéis distintos | bom após `035` |
| Ordem por lista | ampla e reservas deixam de compartilhar uma ordem imprópria | bom após `034` |
| Recurso instruído | acesso nasce de ato específico e termina com o processo da peça | excelente após `036` |

### Conceitos ainda incompletamente comunicados

| Conceito | Leitura provável pela UI | Significado real | Classificação |
|---|---|---|---|
| Perfil | “vaga/perfil de vaga” | também carrega curso, turma, polo, turno ou código, conforme a família | D2; o modelo cabe, mas o nome não acompanha todas as famílias |
| Marco classificatório | uma configuração dentro da Classificação | o ponto que reúne regras, ordem, corte, resultado e janela recursal | D2/D3; ainda denso |
| Peso opcional | pode ficar vazio | fica vazio apenas enquanto nenhum marco enumerar a Etapa | D2; alvo da `037` |
| Corte | algo disponível só quando já há regra | uma superfície que também deve explicar por que ainda não há faixa | D4; alvo da `037` |
| Estado global do Processo | soma dos cards e alertas | situação operacional corrente de vários Editais e atores | D3/D4; permanece fragmentado |
| Retificação completa | mecanismo geral de corrigir publicação | não alcança toda alteração legítima, como acrescentar Modalidade | D3; promessa ampla demais para o alcance real |
| Método de sorteio | ocorrência externa pública e previamente definida | prática real observada gera número depois e o chama de semente | conflito de governança, não simples UX |

### Novato versus especialista

- **Novato:** tende a travar em Perfil, marco, recorte, peso condicional e em saber “o que vem
  depois” no Processo vivo.
- **Especialista:** entende a regra de negócio, mas estranha onde ela foi representada — sobretudo
  curso/turma/polo como Perfil, duas fontes para prazos e distribuição sem recorte local.
- **Ambos:** sofrem com visão global, recusas silenciosas, caminhos condicionais e contradições que
  aparecem tarde.

---

## 7. Personas: como o produto se apresenta hoje

### Operador novato

Consegue começar, distinguir Processo de Edital, seguir a composição e perceber publicação como ato.
A `030` e a `032` reduziram muito a dependência de treinamento. Ainda pode não saber:

- por que turma ou polo é um Perfil;
- como o marco governa etapas, corte, resultado e recurso;
- qual é a situação global depois que vários Editais entram em execução;
- a quem pedir quando encontra uma recusa fora das portas já tratadas.

### Operador experiente do domínio

Reconhece quase todos os conceitos e encontra boa correspondência com o modelo mental institucional.
As maiores fricções são justamente onde o produto comprime famílias diferentes numa abstração única
ou exige coerência entre fontes separadas.

### Presidência/coordenador da comissão

Comissão, alocação e distribuição são fortes. O sistema mostra dependências e propõe distribuição
antes de gravar. O limite aparece na escala: não há organização do trabalho por Perfil, polo ou
modalidade para comissões locais. A presidência enxerga tarefas de uma Etapa, mas não necessariamente
a geografia organizacional do certame.

### Avaliador

É a persona mais bem atendida. “Minhas Etapas” e a mesa formam uma fila de trabalho, com regra,
documentos, estado, pendência e continuidade. O produto se comporta como mesa de trabalho, não como
cadastro administrativo.

### Candidato

Descoberta, inscrição, documentação contextual, comprovante, versão aceita, acompanhamento e recurso
são fortes. A `036` fecha uma lacuna de justiça procedimental: quem foi eliminado pode ler o parecer
que fundamentou a decisão, dentro das condições temporais definidas. Matrícula precisa de nova
auditoria para confirmar a mesma qualidade.

### Julgador de recurso

Antes, tinha a caixa, mas não a prova. Agora recebe exatamente o que foi instruído naquele recurso,
sem ganhar acesso genérico à inscrição ou a terceiros. É uma melhora funcional, conceitual e de
proteção de dados.

### Registro Acadêmico

Ganhou requerimento estruturado e exportação. Ainda não há evidência equivalente à da mesa do
avaliador de que o trabalho cotidiano, a importação externa e o tratamento de campos ausentes
funcionem naturalmente para esse ator.

---

## 8. Mapa atual de encontrabilidade

| Intenção | Onde se procuraria | Onde está | Esforço atual |
|---|---|---|---:|
| criar outro Edital no mesmo Processo | página do Processo | página do Processo | E0 |
| cadastrar vagas e reservas | composição da oferta/Perfis | Perfis e modalidades | E0/E1 |
| definir quem avalia | comissão ou Etapa | comissão → alocação/distribuição | E0/E1 |
| encontrar trabalho atribuído | área pessoal | Minhas Etapas → mesa | E0 |
| publicar resultado | marco/classificação | destino oferecido conforme capacidade | E0/E1 após `033` |
| saber por que não pode publicar | revisão/publicação | validação do conteúdo com destino | E0/E1 após `032` |
| corrigir Edital publicado | tela do Edital | Retificação, se a capacidade estiver disponível | E1; aviso ainda pouco condutor na `main` |
| abrir corte sem regra declarada | marco | o link ainda é condicional na `main` | E3/E4; alvo da `037` |
| alterar período de inscrição | cronograma ou inscrição | informação distribuída | E2 |
| saber o estado completo do Processo | página do Processo/Supervisão | várias telas e contadores | E2/E3 |
| organizar comissão por polo | comissão/alocação | não existe recorte por Perfil/polo | E4 |
| acrescentar modalidade após publicação | Retificação | não suportado | E4 |

---

## 9. Pontos de imprevisibilidade que ainda importam

1. **Cronograma × janela recursal.** Duas fontes podem declarar datas incompatíveis e nenhuma
   validação transversal as confronta.
2. **Perfil como conceito polimórfico.** A escolha inicial repercute depois em vaga, inscrição,
   classificação e organização do trabalho, mas a interface não explicita que Perfil pode significar
   turma, polo ou código.
3. **Peso da Etapa.** Na `main`, o campo parece opcional e a obrigação nasce quando o marco enumera
   a Etapa; a `037` pretende antecipar a consequência.
4. **Retificação.** A interface ensina corretamente que corrige o publicado, mas o operador só
   descobre depois que certas entidades, como Modalidade, não podem ser acrescentadas.
5. **Sorteio e prática institucional.** O sistema exige ocorrência externa; a amostra real do Cefor
   não a declara. A consequência é descoberta na implantação, não na composição.
6. **Distribuição em processos grandes.** Alocar por Etapa parece suficiente no início; em sete
   polos, descobre-se tarde que cada comissão local não recebe somente o seu recorte.

---

## 10. Top 10 fricções atuais

### 1. A visão global não acompanha o Processo vivo

**Evidência:** na `main` atual, a Supervisão mostra 12 inscrições, marcos e alertas de avaliadores;
não resume avaliações concluídas, sorteios, resultados publicados, recursos, ocupações,
convocações ou matrícula. A página do Processo lista três Editais e oferece Encerrar/Cancelar.

**Causa:** cada feature criou uma boa superfície local; não existe um modelo de estado operacional
compartilhado para a condução.

**Afetados:** gestor, presidência e operador.  
**Severidade:** S3 sistêmica.  
**Direção:** prolongar o “O que fazer agora” e o Pulso, por Edital e por compromisso, sem criar um
dashboard analítico separado.

### 2. Fontes normativas podem se contradizer silenciosamente

**Evidência:** janela recursal do marco e Evento do Cronograma podem declarar datas diferentes;
período de inscrição também aparece em mais de uma superfície.

**Causa:** cada agregado valida a própria forma, mas ninguém valida coerência cruzada.

**Afetados:** elaborador, publicador, candidato e julgador.  
**Severidade:** S3.  
**Direção:** validação cruzada antes de homologar/publicar, apontando ambas as fontes e um destino de
correção.

### 3. A organização do trabalho não conhece Perfil/polo/modalidade

**Evidência:** no cenário de sete polos, alocação e distribuição operam por Etapa; não há como
separar naturalmente o trabalho das comissões locais.

**Causa:** autorização e trabalho foram modelados no eixo Processo/Edital/Etapa, enquanto a operação
real também usa recortes da oferta.

**Afetados:** presidência, comissão local e avaliadores.  
**Severidade:** S3.  
**Direção:** introduzir escopo opcional de trabalho por Perfil/lista, sem duplicar comissão nem
transformar Perfil em permissão global.

### 4. A prática real de sorteio diverge do modelo exigido

**Evidência:** 10 de 10 Editais reais da amostra não declaram ocorrência externa pública; o produto
exige uma fonte/ocorrência que permita derivar e reproduzir a semente.

**Causa:** conflito entre governança institucional e exigência de auditabilidade, não falha de
microcopy.

**Afetados:** elaborador, comissão, auditoria e candidato.  
**Severidade:** S3 potencialmente S4 se a instituição operar fora do modelo.  
**Direção:** decisão institucional explícita: adotar ocorrência externa nos próximos Editais ou
alterar o modelo de produto com uma alternativa igualmente verificável.

### 5. A Retificação não alcança Modalidade

**Evidência:** um Perfil de cotas publicado sem ampla concorrência não recebe não-cotista, e a
interface não oferece correção por Retificação.

**Causa:** o alcance de alteração normativa não cobre criação dessa entidade.

**Afetados:** elaborador, candidato e gestão de vagas.  
**Severidade:** S3.  
**Direção:** permitir acréscimo normativo de Modalidade com diff, vigência e revalidação das
consequências; não liberar edição direta.

### 6. Sete recusas fora das portas continuam em 404 uniforme

**Evidência:** a `033` corrigiu as portas e inventariou sete recusas que não passam pelo mecanismo
central.

**Causa:** mistura entre ocultação de objeto por escopo e negativa de uma capacidade conhecida.

**Afetados:** operadores e administradores.  
**Severidade:** S2.  
**Direção:** decisão semântica por classe: 403 condutor quando o objeto é visível e falta capacidade;
404 quando revelar a existência do vínculo/conteúdo seria indevido.

### 7. Duas gramáticas descrevem o mesmo fato normativo

**Evidência:** a Retificação pública usa diff humano; telas internas do ato ainda podem exibir
caminhos, UUIDs e operações como `REPLACE`.

**Causa:** renderizador humano foi aplicado ao documento público, não convertido em serviço comum.

**Afetados:** operadores, homologador e auditor.  
**Severidade:** S2.  
**Direção:** uma representação semântica única, consumida pelas superfícies interna e pública.

### 8. A Classificação ainda concentra muita decisão

**Evidência:** a auditoria contou 28 controles; progressive disclosure reduziu parte do ruído, mas
marco, combinação, normalização, sorteio, corte, arredondamento e recurso continuam próximos.

**Causa:** o marco agrega muitas consequências legítimas; a interface ainda as apresenta mais como
formulário do que como sequência de decisões.

**Afetados:** elaborador novato e experiente.  
**Severidade:** S2.  
**Direção:** agrupar pela pergunta de negócio e revelar somente blocos acionados pela forma escolhida,
com resumo de consequência no cartão.

### 9. Matrícula e exportação ainda não receberam auditoria equivalente

**Evidência:** `029` e `031` têm requisitos e testes, mas a própria reavaliação marca a experiência
como não reauditorada e mantém decisão aberta sobre o importador acadêmico.

**Causa:** a entrega avançou mais rápido do que a validação longitudinal dessa nova persona.

**Afetados:** candidato e Registro Acadêmico.  
**Severidade:** risco S2, ainda não defeito confirmado.  
**Direção:** percurso real curto com arquivo importado pelo sistema de destino e tratamento de campos
vazios.

### 10. A `037` já sofre deriva de integração antes de terminar

**Evidência:** a worktree está baseada antes da implementação final da `036`; as tarefas da `037`
esperam 32 tabelas append-only, enquanto a `main` atual provisiona 33. Há mudanças ainda não
commitadas e rastreabilidade pendente.

**Causa:** alta velocidade e features paralelas em worktrees.

**Afetados:** equipe de desenvolvimento e, indiretamente, confiabilidade da entrega.  
**Severidade:** S2 de processo de engenharia.  
**Direção:** integrar a `main`, repetir o “antes”, atualizar os contadores, concluir quickstarts e só
então creditar a feature.

---

## 11. Complexidade que pode ser eliminada ou adiada

- esconder configuração de sorteio quando o marco não sorteia;
- esconder corte quando não se aplica, sem esconder o destino que explica a ausência;
- derivar ampla concorrência quando não há lista reservada, como a `027` já faz;
- não pedir ao Registro Acadêmico dados que o sistema não conhece; exportar vazio, como a `031`;
- inferir o destino de correção pela própria recusa, como a `037` propõe;
- usar uma única derivação para saber se o ator pode Retificar, em vez de repetir a pergunta em
  template e autorização;
- mostrar no Processo somente compromissos acionáveis e exceções, deixando detalhes no Edital;
- evitar tornar o par marco×Etapa um novo modelo sem caso real que exija pesos distintos. Hoje, o
  custo de migração e de preservação normativa supera o benefício conhecido.

---

## 12. Problemas estruturais

### E-3 — duas representações normativas

Não se resolve com texto auxiliar. É preciso que o fato alterado tenha uma representação semântica
única, renderizada conforme o público.

### E-4 — fontes que não se confrontam

Não se resolve escolhendo uma das telas por convenção. Enquanto cronograma, inscrição e marco
continuarem fontes legítimas, a publicação precisa confrontá-las.

### E-6 — a visão global some com o Processo vivo

Não se resolve com “mais um dashboard”. A solução deve continuar a linguagem atual de estado e
próximo passo, agregando compromissos da cauda ao Processo e à Supervisão.

### Escopo de trabalho por recorte

Não é mera filtragem de tabela. Envolve quem pode ver, receber, concluir e supervisionar trabalho
de um Perfil/polo/modalidade. Precisa manter negar-por-padrão e não expor inscrição de outro recorte.

---

## 13. Quick wins seguros

1. concluir a `037` depois de atualizar sua base e sua contagem de proteção;
2. no aviso de conteúdo imutável, dizer a ação e a capacidade necessárias somente quando o ator não
   recebe o caminho;
3. sempre oferecer o destino do corte a quem pode classificá-lo e deixar a própria tela explicar o
   estado vazio;
4. corrigir a régua “vencido”: com término, vence pelo término; sem término, pelo início;
5. antecipar no cartão do marco a Etapa enumerada sem peso;
6. decidir e corrigir as sete recusas usando a distinção 403/404, sem transformar tudo numa só
   resposta;
7. usar o renderizador humano já existente também na tela interna da Retificação.

---

## 14. Melhorias estruturais recomendadas

### 14.1 Painel de condução dentro do fluxo existente

**Problema raiz:** o Processo perde a capacidade de orientar depois que os Editais são publicados.

**Mudança:** expandir a página do Processo e/ou Supervisão para mostrar, por Edital:

- fase operacional atual;
- próximo marco ou prazo;
- trabalho pendente por tipo e responsável funcional;
- atos aguardando emissão/publicação;
- recursos em prazo ou pendentes;
- situação de sorteio, ocupação, convocação e matrícula;
- exceções que exigem ação.

**Risco:** criar um painel redundante e inconsistente.  
**Mitigação:** cada indicador deve derivar do mesmo comando/consulta que governa a tela de destino e
levar diretamente a ela.  
**Impacto esperado:** mover a visão global de 5 sem enfraquecer as ótimas superfícies locais.

### 14.2 Validação cruzada de conteúdo antes de publicar

**Problema raiz:** cada fonte pode ser internamente válida e externamente contraditória.

**Mudança:** uma família de verificações que confronte prazos e relações equivalentes, com evidência
dos dois valores e caminho de correção.

**Risco:** falso positivo por tentar inferir equivalência sem declaração.  
**Mitigação:** validar somente relações semânticas já declaradas pelo modelo; não casar eventos por
texto livre.

### 14.3 Escopo organizacional opcional por Perfil

**Problema raiz:** processos multi-polo precisam dividir trabalho dentro da mesma Etapa.

**Mudança:** permitir que alocação/distribuição sejam limitadas a Perfis ou listas explicitamente
declarados.

**Risco:** explosão de autorização e vazamento horizontal.  
**Mitigação:** escopo derivado, negar por padrão, testes de contraprova entre recortes e visão global
para a presidência.

---

## 15. O que não fazer

- não criar uma spec para cada frase ou cada 404 sem antes decidir a semântica comum;
- não resolver visão global com um dashboard separado que replique contadores;
- não colocar tooltip em “Perfil” e manter a abstração sem contexto de turma/polo;
- não ampliar permanentemente a permissão do julgador; a `036` acertou ao usar ato de instrução;
- não permitir edição direta de Edital publicado para corrigir a Retificação;
- não obrigar cronograma a ter um Evento textual de recurso só para comparar datas;
- não aceitar uma semente inventada depois do sorteio apenas porque é a prática atual;
- não mover peso para marco×Etapa sem um Edital real que precise de pesos diferentes;
- não chamar a `037` de pronta antes de integrar `036`, atualizar o “antes” e percorrer o quickstart;
- não usar crescimento de código ou quantidade de testes como substituto de evidência de uso.

---

## 16. Padrões que devem ser preservados

1. **Publicação como ato imutável**, com Retificação e história explícita.
2. **Prévia antes do irreversível**, mostrando consequência, autoria e estado.
3. **Mesa do avaliador**, com fila, regra à vista, próximo item e recuperação.
4. **Consolidação com “por quê”**, números e regra, não apenas resultado.
5. **Navegação por capacidade**, sem oferecer destinos que o ator não abre.
6. **Recusa no comando, não só no botão**; esconder não é autorizar.
7. **Ato de instrução do recurso**, com alcance estreito, temporal e auditado.
8. **Diff humano e sucessão**, preservando passado e tornando vigência compreensível.
9. **Desconhecido permanece vazio**, em vez de dado inventado na exportação.
10. **Quickstart pela interface**, porque foi ele que encontrou defeitos que testes isolados não
    encontrariam.

---

## 17. Evolução de engenharia e confiabilidade

O crescimento foi extraordinariamente rápido:

| Marco | Data | Código de produto aproximado | Funções de teste `def test_` | Specs numeradas |
|---|---|---:|---:|---:|
| depois da `002` | 29/08 | 9.034 linhas | 323 | 2 |
| auditoria inicial, depois da `012` | 02/09 | 34.345 | 1.891 | 12 |
| auditoria de 13/09 | 13/09 | 77.470 | 3.804 | 26 |
| reauditoria de 16/09 | 16/09 | 82.105 | 4.097 | 29 |
| depois da `033` | 18/09 | 91.454 | 4.397 | 34 |
| depois da `035` | 19/09 | 92.157 | 4.496 | 36 |
| `main` atual, depois da `036` | 19/09 | 93.510 | 4.552 | 37 |

As contagens de teste acima são funções no código, não casos parametrizados executados. A evidência
de execução registrada após a `036` é **7.398 passando e 11 pulados**, em PostgreSQL. O banco atual
protege **33 de 33** tabelas append-only. Há cerca de 602 arquivos de teste e 80 migrations.

### O que esses números significam

Positivamente:

- o projeto não deixou segurança e integridade para depois;
- requisitos têm rastreabilidade até testes e quickstarts;
- regressões em autorização, imutabilidade e escopo têm contraprovas;
- as auditorias efetivamente mudam a fila de produto.

Como alerta:

- 37 incrementos em pouco mais de três semanas criam risco de integração e de fadiga de governança;
- várias specs permanecem com `Status: Draft` mesmo depois de implementadas;
- artefatos podem ficar numericamente defasados entre worktrees;
- a precisão documental é excelente, mas seu custo pode ultrapassar o tamanho da mudança;
- o próximo ganho não virá de escrever mais especificação local antes de tomar as decisões de
  governança e atacar as três raízes estruturais.

---

## 18. Situação exata da `037`

### O que já está decidido na spec

- corte deve ser encontrável mesmo sem regra;
- o destino oferecido depende da causa da recusa;
- quem não pode corrigir deve saber qual capacidade procurar;
- Evento com término vence pelo término; Evento pontual vence pelo início;
- peso continua pertencendo à Etapa, mas sua condição deve ser dita e cobrada no marco que a usa.

### O que o código em trabalho já mostra

- alterações na régua de calendário;
- condução de recusas para Classificação ou Retificação;
- frase centralizada de autorização;
- aviso de conteúdo imutável condicionado à capacidade;
- rótulo e alerta antecipado do peso;
- testes novos e ampliados.

### O que falta para contar como produto

1. integrar a `main` com a `036`;
2. repetir a medição inicial com 33/33 proteções;
3. resolver qualquer conflito sem perder as garantias de acesso da `036`;
4. concluir os cinco cenários do quickstart;
5. escrever rastreabilidade final;
6. rodar lint, checks e suíte PostgreSQL completa;
7. só então atualizar as notas.

Minha avaliação é que a direção da `037` é correta e o escopo é pequeno. O risco não é conceitual;
é creditar cedo demais uma implementação ainda não integrada.

---

## 19. Backlog priorizado

| Prioridade | Achado | Tipo | Severidade | Esforço | Impacto | Recomendação |
|---|---|---|---:|---:|---:|---|
| P0 | Nenhum `P0` aberto na `main` após a `036` | — | — | — | — | preservar esse marco; não fabricar um novo P0 |
| P1 | visão global do Processo vivo (`E-6`/`ACH-25`) | arquitetura da informação/estado | S3 | M | muito alto | próximo incremento estrutural |
| P1 | fontes normativas sem confronto (`E-4`) | validação transversal | S3 | M | alto | validar antes da publicação |
| P1 | trabalho sem escopo por Perfil/polo (`ACH-60`) | organização/autorização | S3 | M/G | alto | desenhar com caso de 7 polos |
| P1 | prática de sorteio × ocorrência externa | governança | S3/S4 | decisão | muito alto | decisão institucional antes de código |
| P1 | Retificação não acrescenta Modalidade | modelo normativo | S3 | M | alto | especificar após decisão explícita |
| P1 | sete recusas fora das portas | autorização/feedback | S2 | P/M | alto | decidir 403 × 404 por classe |
| P2 | duas gramáticas do mesmo fato (`E-3`) | representação | S2 | M | médio | reutilizar renderizador semântico |
| P2 | classificação ainda densa | progressão | S2 | M | médio | agrupar por intenção e consequência |
| P2 | matrícula/exportação sem reauditoria | pesquisa/integração | risco S2 | P | alto | percurso com Registro Acadêmico |
| P2 | `037` incompleta | integração | S2 | P | médio | integrar, percorrer e verificar |
| P3 | polish de rótulos e resumos locais | linguagem | S1 | P | baixo/médio | fazer junto de mudanças maiores |

### Ordem recomendada

1. terminar e integrar a `037`, sem abrir outra feature em paralelo;
2. tomar as cinco decisões de governança já registradas;
3. construir o painel de condução dentro da página do Processo/Supervisão;
4. resolver as sete recusas conforme a decisão semântica;
5. implementar validação cruzada;
6. tratar organização do trabalho por Perfil com o cenário real de sete polos;
7. reauditar matrícula/exportação e, depois, repetir os seis cenários completos.

---

## 20. Respostas às cinco perguntas obrigatórias

### 1. Quais partes uma pessoa consegue compreender apenas usando o sistema?

Ela consegue compreender, com boa autonomia:

- a diferença entre Processo e Edital;
- como compor a maior parte da oferta;
- que publicação é um ato imutável;
- que correção ocorre por Retificação;
- como se inscrever, anexar documentos, enviar e acompanhar;
- como constituir comissão, alocar e distribuir trabalho;
- como avaliar e consolidar;
- como uma ordem vira resultado e publicação;
- como interpor, instruir e decidir recurso;
- como sorteio e listas de concorrência alimentam ocupação e convocação;
- como consultar história, autoria e versões.

### 2. Em quais partes ainda precisa conhecer como o sistema foi pensado?

- ao interpretar Perfil como turma, polo, turno ou código;
- ao entender o alcance agregado do marco classificatório;
- ao descobrir que peso “opcional” se torna obrigatório por uso;
- ao localizar corte quando não existe regra;
- ao juntar mentalmente o estado completo espalhado por Edital, Supervisão, mesa, marco, recurso e
  ocupação;
- ao distinguir negativa de capacidade de objeto ocultado pelo 404;
- ao saber quais mudanças a Retificação não suporta.

### 3. Em quais partes a dificuldade pertence legitimamente ao domínio?

- fundamentos e percentuais de reservas;
- regras de reversão, corte, empate e suplência;
- impedimentos e segregação de funções;
- admissibilidade e mérito de recursos;
- composição da comissão e competência de cada papel;
- definição normativa do método de sorteio;
- diferença entre resultado preliminar e definitivo.

O produto deve apresentar consequência e estado, mas não substituir formação jurídica e
administrativa nessas matérias.

### 4. Quais mudanças fariam o sistema ensinar seu modelo mental durante o uso?

- mostrar o Processo como sequência de compromissos vivos, não só coleção de Editais;
- confrontar fontes equivalentes e explicar a contradição antes da publicação;
- contextualizar Perfil pelo tipo de oferta real;
- transformar o marco em uma sequência de perguntas de negócio com resumo das consequências;
- usar a mesma gramática humana para todo fato normativo;
- conduzir recusas à ação ou à capacidade correta;
- mostrar o escopo organizacional do trabalho quando houver polos/listas.

### 5. Onde um novo servidor provavelmente travaria amanhã?

Ele provavelmente conseguiria criar, compor e publicar o Edital. Travaria depois, ao tentar
responder “qual é a situação completa agora?” e “quem precisa agir em seguida?”. Num caso simples,
chegaria mais longe. Num caso multi-polo ou com regra especial, poderia travar ao mapear a oferta
para Perfis e ao dividir o trabalho. Se o Edital publicado precisasse ganhar uma Modalidade, não
encontraria solução. Se a instituição mantivesse o sorteio como hoje aparece nos Editais reais,
encontraria um conflito entre prática e produto.

---

## 21. As cinco mudanças que mais aproximam o produto de “não precisar de manual”

1. **Manter o guia ligado depois da publicação:** fase atual, próximo compromisso, responsável e
   exceção por Edital na página do Processo/Supervisão.
2. **Confrontar fontes antes do ato:** datas e regras equivalentes não podem divergir em silêncio.
3. **Fazer a organização acompanhar a oferta:** permitir recorte de trabalho por Perfil/polo/lista
   quando o Edital exigir.
4. **Completar a gramática de recuperação:** caminho correto, capacidade necessária e 403/404
   semanticamente consistentes.
5. **Alinhar produto e norma real:** decidir ocorrência externa do sorteio e alcance da Retificação
   antes de acrescentar novas features.

---

## Conclusão

O produto não está apenas “ficando maior”. Ele está ficando **mais operacional, mais previsível e
mais defensável**. As features recentes atacaram exatamente os pontos que separavam uma coleção de
capacidades de um processo seletivo conduzível: executabilidade, navegação autorizada, ordem por
recorte, sorteio, convocação e prova no recurso.

A direção, portanto, é boa. O risco agora é continuar tratando becos locais porque eles produzem
specs fáceis de delimitar, enquanto a principal lacuna — compreender o Processo vivo como um todo —
permanece com nota 5. O próximo salto de qualidade não é outra função isolada. É conectar, na
experiência de condução, tudo o que o sistema já sabe calcular.

---

## 22. Fontes principais no repositório

- [Auditoria exploratória inicial — 02/09](auditoria-exploratoria-e2e-2026-09-02.md)
- [Auditoria ponta a ponta — 13/09](auditoria-exploratoria-ux-2026-09-13.md)
- [Reauditoria com seis cenários — 16/09](auditoria-exploratoria-ux-2026-09-16.md)
- [Reavaliação das features recentes — 18–19/09](reavaliacao-ux-2026-09-18.md)
- [Avaliação da amostra real de Editais — 12/09](avaliacao-de-capacidade-editais-2026-09-12.md)
- [Rastreabilidade da `036`](../specs/036-instrucao-do-recurso/rastreabilidade.md)
- [Especificação da `037`](../specs/037-quatro-becos-conhecidos/spec.md)
- [Tarefas da `037`](../specs/037-quatro-becos-conhecidos/tasks.md)
