# Inventário — o que cada feature produz, e o que disso a presidência não consegue ver

Levantamento feito em **09/09/2026**, sobre a worktree `spec-014-acompanhamento-operacional` em
`7cca2f9`, como entrada para a spec de **Supervisão do Processo**.

> **Não abre spec, não cria requisito e não decide nada.** O que se registra é o fato que cada
> feature persiste, se ele interessa à presidência, e se a tela dona já o torna visível. A decisão
> sobre o que vira requisito é de governança, e a Constituição a reserva ao usuário.

## Por que existe

A primeira proposta desta feature nasceu do roadmap e não do repositório: pedia painel de
produtividade, feed de auditoria, percentual global do Processo e estados de Etapa que o domínio
não tem. Metade do que ela pedia já estava implementado, e a outra metade era invenção.

O corretivo é este inventário. Ele percorre `001`–`021` fazendo cinco perguntas, nesta ordem:

```text
QUE FATO A FEATURE PERSISTE?
        ↓
ESSE FATO INTERESSA A QUEM PRESIDE O PROCESSO?
        ↓
EXISTE AUSÊNCIA OU DIVERGÊNCIA QUE TRAVA O PRÓXIMO ATO?
        ↓
A TELA DONA JÁ TORNA ISSO VISÍVEL?
        ↓
SIM  → a supervisão no máximo referencia. Não é requisito.
NÃO  → candidato a requisito.
```

A coluna que costuma ser esquecida é a penúltima respondida com **sim**. Ela é o que justifica os
requisitos que sobrevivem — sem ela, a revisão seguinte reabre o mesmo debate do zero.

## Vereditos usados

| Marca | Significado |
|---|---|
| **JÁ MOSTRA** | A tela dona exibe o fato de forma acionável. A supervisão não repete. |
| **TRANSVERSAL** | A dona mostra, mas só uma por vez: descobrir exige abrir N telas ou subir do Edital ao Processo. |
| **AUSENTE** | Nenhuma tela mostra. Candidato real. |
| **SEM FATO** | A feature não persiste fato que sirva a esta pergunta, ou não está implementada. |
| **NÃO SUPERVISÃO** | O fato existe e importa, mas o ator não é quem preside. |

## Estado de implementação, que muda o que é observável hoje

Nem toda spec escrita produz fato gravado. Conferido pelas caixas de `tasks.md`:

| Spec | Tarefas | Consequência para a supervisão |
|---|---|---|
| `001`–`013`, `015`, `017`, `018`, `020` | completas | produzem fato observável |
| `002` | 7 pendentes | são verificação externa (leitor de tela, ASES, LDAP, CSP, design system) — nenhuma produz fato |
| `013` | 1 pendente | conferência de 375 px em `distribuicao.html` e `resultados.html` |
| `021` | **0 de 77** | **especificada e não implementada.** Sorteio não grava nada ainda |

A consequência prática: **a `021` não entra na v1 da supervisão**. Não por decisão de escopo, por
ausência de fato. Quando o sorteio existir, ele entra pela porta que a `015` já abriu — o ato de
ordenação —, e não por porta própria.

---

# Parte 1 — Feature a feature

## 001 · Backbone normativo — Processo, Edital, Ato administrativo

**Fatos.** `ProcessoSeletivo`, `Edital` e seus estados; `AtoAdministrativo`. O estado do Edital
(`EM_ELABORACAO`, `EM_REVISAO`, `HOMOLOGADO`, `PUBLICADO`, `ENCERRADO`, `CANCELADO`) é a espinha de
tudo o que vem depois.

**A tela dona.** `processo_detalhe.html` traz a trilha de situação do Processo (`:25`) e o cartão
*O que fazer agora* (`:54`), com o próximo passo em destaque e os atos disponíveis para os papéis
de quem lê. `lista.html` e `detalhe.html` cobrem o Edital.

**Veredito: JÁ MOSTRA.** E mais do que isso: `interface/acoes.py` é o precedente direto do que a
supervisão pretende ser. Seu docstring registra que três lugares respondiam "o que se pode fazer
agora" sem se falarem, e que os achados 07, 08 e 09 da auditoria tinham essa única causa. A
supervisão **não pode virar o quarto lugar**. Onde ela precisar dizer o que fazer com um Edital, a
resposta vem de `acoes.py`, e não de uma segunda derivação.

Um detalhe que a supervisão herda: em `Acao`, motivo vazio significa disponível, e motivo
preenchido mostra o controle desabilitado com a razão ao lado — *nem oferecido, nem escondido*.
É o padrão de exibição de impedimento que já existe no produto.

## 002 · Interface administrativa

**Fatos.** Nenhum. Entrega o canal.

**Veredito: SEM FATO.** Duas heranças, porém, valem para a supervisão: toda tela é anotada com
`aria-label` e `role="status"`, e a conferência de 375 px é tarefa recorrente. Um gráfico mudo, ou
que force rolagem horizontal do corpo da página, contraria as duas.

## 003 · Integridade e prontidão

**Fatos.** `validate_for_publication` produz achados sobre o snapshot do Edital, com severidade e
caminho por chave. Não são persistidos: são calculados na leitura.

**A tela dona.** `_pendencias.html`, incluída no assistente e no detalhe do Edital. Cada achado
aponta para a etapa do assistente que o resolve, e diz explicitamente quando **não** há onde
resolver — em vez de oferecer um caminho que não termina em lugar nenhum.

**Veredito: JÁ MOSTRA.** É também o modelo de redação que a supervisão deve copiar para os seus
sinais: mensagem, destino, e a razão quando destino não existe.

**Um achado colhido aqui, e ele é o sinal S01.** `_coerencia_das_etapas`
(`editais/domain/validation.py:747`) confere que o `scheduleEventId` de uma Etapa **existe** no
cronograma — referência pendurada é impeditiva. Mas o campo é declarado `admite_nulo=True`
(`:178`): **Etapa sem Evento vinculado publica normalmente**, e nada avisa. É comportamento
deliberado, não defeito. A consequência é que a Etapa fica sem qualquer referência temporal, e não
existe hoje nenhuma tela que diga isso.

## 004 · Endereçamento normativo estável · 005 · Integridade do snapshot

**Fatos.** Chaves estáveis e verificação de integridade na publicação.

**Veredito: SEM FATO** para supervisão. São qualidade da capacidade, não capacidade observável — a
própria Constituição separa as duas coisas no Princípio VI.

## 006 · Elaboração completa · 007 · Edital institucional · 008 · Composição institucional

**Fatos.** Conteúdo do Edital, forma canônica, documento publicado.

**A tela dona.** O assistente `compor_*`, a prévia e o PDF.

**Veredito: JÁ MOSTRA** — e o que interessaria à supervisão daqui (o Edital está pronto para
submeter?) é exatamente o que a `003` já responde no mesmo lugar onde se corrige.

## 009 · Inscrição e documentos

**Fatos, e são os mais ricos do sistema para esta feature.**

| Fato | Onde | Observação |
|---|---|---|
| `Inscricao.status` | `RASCUNHO` \| `SUBMETIDA` | **não existe `CANCELADA`** |
| `Inscricao.submitted_at` | `inscricoes/models.py:62` | garantido não-nulo quando submetida |
| `Inscricao.created_at` | `:67` | nascimento do rascunho |
| `profile_id`, `modality_id` | `:33` | recorte por Perfil e por modalidade |
| `ValorDeFato`, `DocumentoSubmetido` | mesmo módulo | conteúdo da inscrição |

A garantia do `submitted_at` não é convenção da aplicação: a `CheckConstraint`
`ck_inscricao_submetida_completa` (`:84`) torna o estado `SUBMETIDA` inalcançável sem instante,
versão aceita, aceite de declarações e protocolo. **Uma série temporal de submissões não tem como
sair silenciosamente errada**, e isso é raro o bastante para ser dito na spec.

Não existe `updated_at`. A última atividade num rascunho **é** derivável, mas de outro lugar: as
edições gravam evento de auditoria (`inscricoes/application/rascunho.py:125`, `:206`, `:226`,
`:416`, `:447`) e `RegistroAuditoria.occurred_at` existe. Usar a trilha como fonte de indicador
operacional é decisão de fronteira que merece ser tomada de propósito — fica registrado que é
possível, para a próxima revisão não redescobrir que era impossível.

**A tela dona.** `inscricoes.html`: total do Edital no título, quantas **por Perfil como filtro
clicável**, por modalidade com contagem no `select`, e os rascunhos numa seção própria. A contagem
aparece antes de abrir, no rótulo da própria ação — `acoes.py:94` produz
`Inscrições recebidas (N)`, e o comentário ao lado explica: obrigar a abrir para descobrir é o
atrito que a `007` passou uma feature inteira tirando.

**Veredito por pergunta:**

| Pergunta | Veredito |
|---|---|
| Quantas se inscreveram neste Edital? | **JÁ MOSTRA** |
| Quantas por Perfil, por modalidade? | **JÁ MOSTRA** |
| Quantas no **Processo**, somando Editais? | **AUSENTE** — `processo_detalhe.html:42` lista Editais sem número nenhum |
| Quantas nas últimas 24 h? Como evoluiu? | **AUSENTE** — `submitted_at` existe e ninguém o lê como série |
| Falta quanto para encerrar? | **AUSENTE** — o dado existe na `001`, o volume na `009`, e ninguém junta os dois |
| Quantos rascunhos, perto do fecho? | **TRANSVERSAL** — o número existe por Edital; o confronto com o prazo, não |
| Quantas canceladas? | **SEM FATO** — o estado não existe no domínio |

**Um conflito de vocabulário a resolver antes de escrever a spec.** A tela existente diz
**"Em preenchimento — 312"** (`inscricoes.html:93`). Dizer "312 rascunhos" na supervisão cria dois
termos para o mesmo conceito, o que o Princípio I proíbe sem justificativa documentada. As saídas
íntegras são duas: adotar o termo existente, ou decidir a mudança e aplicá-la **nas duas telas**.
Escolher só para a tela nova não é uma delas.

## 010 · Área do candidato

**Fatos.** `DesafioDeAcesso`, credenciais, reconciliação por CPF.

**Veredito: NÃO SUPERVISÃO.** O ator é o candidato. Nada aqui pede ato da presidência.

## 011 · Comissão e alocação por Etapa

**Fatos.** `MembroComissao` (vínculo, função, presidência) e `AlocacaoEtapa`. A comissão é do
**Processo**; a alocação é por Etapa, e a Etapa é do Edital. É a única feature que já vive na
camada em que a supervisão vai viver.

**A tela dona.** `alocacoes.html:31` traz o resumo: Etapas com equipe, Etapas sem ninguém, membros
sem nenhuma Etapa, Editais não publicados. A matriz membro × Etapa está logo abaixo, com totais por
linha e por coluna.

**Veredito: JÁ MOSTRA**, e a cobertura é boa. Etapa sem equipe — que seria um candidato óbvio a
sinal — já está lá, com o número no cartão e a Etapa na matriz.

**Carga por membro: descartado, e não por duplicação.** A operação inicial é de duas ou três
pessoas acumulando papéis, e a presidência avalia — `pode_atuar_na_etapa` não consulta função. Uma
tabela de produtividade individual nesse arranjo mede a presidência contra si mesma. O gargalo
declarado da operação pequena é outro, e aparece na `018`.

## 012 · Mesa de avaliação

**Fatos.** `Atribuicao` (com `ativo` e `criado_em`), `Avaliacao` (`RASCUNHO` \| `CONCLUIDA`),
`ConclusaoAvaliacao`, `Impedimento`. O esperado por inscrição vem de
`EtapaAvaliacao.evaluations_per_registration`, e o que a ausência significa vive num leitor só,
`avaliacoes/domain/previsao.py`.

Logo, as quatro grandezas do trabalho já existem, sem inventar nada:

```text
esperado    = inscrições submetidas × avaliações previstas na Etapa
distribuído = Atribuicao ativa
iniciado    = Avaliacao em RASCUNHO
concluído   = Avaliacao CONCLUIDA
```

**A tela dona.** `distribuicao.html:40` — e aqui está a decisão de projeto que a supervisão precisa
respeitar, escrita no próprio template (`:42`):

> Os números **são o filtro** […] ler o número num cartão para depois procurá-lo num `select` é
> pedir duas vezes a mesma coisa.

Os quatro cartões são links que recortam a lista: todas, sem nenhum avaliador, sem avaliador
suficiente, com avaliação pendente.

**Veredito: JÁ MOSTRA, por Etapa. TRANSVERSAL, no Processo.** Saber se *alguma* Etapa está com
cobertura insuficiente exige abrir a distribuição de cada uma. Esta é a justificativa do sinal S03,
e ela é diferente da dos demais — não é invisibilidade, é custo de varredura. Convém que a spec o
diga, senão a primeira revisão marca o sinal como duplicação e o corta.

O corte de disciplina permanece: **o número, sim; a segunda tabela com aquelas 17 linhas, não.**

## 013 · Consolidação e Resultado da Etapa

**Fatos.** `ResultadoEtapa`, com `Consequencia` (`HABILITADA` \| `ELIMINADA`), `Origem`
(`AVALIACAO`, `OCORRENCIA`, `RECURSO`) e `versao`.

**A tela dona.** `resultados.html`, alcançada da distribuição (`distribuicao.html:146`).

**Veredito: JÁ MOSTRA.**

**E aqui morre um requisito da proposta original.** Não existe ato de encerrar Etapa.
`EtapaAvaliacao` não tem ciclo de vida — nenhum campo de estado, nenhum comando `encerrar`. Logo
*"todo o trabalho está concluído mas a Etapa não foi formalmente encerrada"* não é pendência: é
afirmação sobre um estado que o domínio não tem. Se um dia houver necessidade normativa de abrir e
fechar Etapa — proibir avaliação antes da abertura, por exemplo —, isso é feature de domínio, e não
tela.

## Cronograma — atravessa 001, 006 e 012

Fica em seção própria porque é o eixo que nenhuma feature dona possui inteiro.

**Fatos.** `Cronograma` é `OneToOneField(Edital)`. `EventoCronograma` tem `start_at`, `end_at`
anulável, `order`, `status` (`PLANEJADO`, `EM_ANDAMENTO`, `CONCLUIDO`, `CANCELADO`, default
`PLANEJADO`) e `is_registration_period`. A marca do período de inscrições está no próprio Evento,
com unicidade garantida por constraint parcial — e o comentário diz por quê: `type` é texto livre,
e inferir dali uma regra de direito seria decidi-la lendo o que alguém digitou.

`EtapaAvaliacao.evento` é `SET_NULL`, anulável: a Etapa referencia o Evento e **as datas não são
copiadas**.

**Veredito: AUSENTE, em três frentes.**

1. **Ninguém confronta prazo com execução.** É a lacuna estrutural: metade do dado está no Edital,
   metade na `009` ou na `012`, e nenhuma tela tem as duas.
2. **Etapa sem Evento não é dita em lugar nenhum** (sinal S01, achado da `003` acima).
3. **`status` é declarado à mão.** Derivar atraso dele produziria muro de alarme falso no dia em
   que ninguém o mantiver. A leitura íntegra exibe os dois — *"declarado PLANEJADO · prazo
   encerrado em 08/09/2026"* — e faz da divergência o sinal, sem a tela decidir qual é o
   verdadeiro. É o mesmo padrão que a `015` já usa para o ato obsoleto.

**A armadilha do nível.** Cronograma, marcos e período de inscrições são **do Edital**. Um Processo
com três Editais tem três períodos de inscrição e três listas de marcos. "Próximo marco" e "encerra
em 2 dias" só são afirmações sobre o Processo quando ele tem um Edital — o caso comum, e não o
único. O desdobramento por Edital não é enfeite: é a forma correta de tudo o que tem data. O total
de inscritos do Processo é a soma; **o prazo do Processo não existe**.

## 015 · Ordenação e classificação

**Fatos.** `AtoDeOrdenacao`, `PosicaoNaOrdem`, `CitacaoDeDecisao`. Entrada nova torna o ato vigente
**obsoleto e não inválido**; alguém autorizado emite o próximo.

**A tela dona.** `ordenacao.html:22` já exibe o bloco *O ato vigente está obsoleto*, com a
divergência e a marca de não recomputável. O cálculo está em
`classificacao/application/selectors.py:170`.

**Veredito: JÁ MOSTRA, por marco. TRANSVERSAL, no Processo.** O caminho é
`detalhe.html:135` → marco → ordenação: só se descobre a obsolescência abrindo o marco. O sinal S04
custa quase nada porque o cálculo já existe; a supervisão apenas o traz para fora.

## 017 · Publicação de resultados

**Fatos.** `PublicacaoResultado`, `SituacaoDivulgada`, `DocumentoDoResultado`, com sucessão entre
publicações e conteúdo público congelado.

**A tela dona.** `publicacoes_do_marco.html`, oferecida pelas ações do ato de ordenação
(`acoes.py:170`). O docstring de `do_ato_de_ordenacao` registra a razão: *sem isso a tela de
publicar existiria e ninguém a encontraria*.

**Veredito: JÁ MOSTRA** — com a ressalva de que a cadeia é longa: Edital → marco → ordenação →
consultar ato → resultados divulgados. Quatro saltos. Não é invisível; é fundo.

Um sinal candidato foi considerado e **descartado por ora**: *ato emitido e não divulgado*. Ele é
computável, mas nem todo ato emitido deve ser publicado de imediato, e transformar em alerta uma
espera legítima é o modo de falha que o catálogo fechado existe para evitar. Fica registrado como
candidato para uma revisão futura, com a semântica a definir.

## 018 · Recursos e superação de resultados

**Fatos.** `Recurso` (protocolo, janela gravada, objeto atacado), `JuizoDeAdmissibilidade`,
`DecisaoRecurso`. O impedimento do julgador não é conceito novo: são cinco perguntas sobre autoria
de atos já gravados, em `recursos/domain/elegibilidade.py`.

**A tela dona.** `recursos.html` — tabela filtrável por situação, **sem contagem** e, de propósito,
**sem impedimento por linha**. O comentário no topo cita `T-006`: perguntar quem está impedido de
julgar cada peça custaria cinco leituras por linha, o custo que a `012` já recusou uma vez.

**Veredito: AUSENTE, e é o achado mais forte do inventário.**

A pergunta que a operação pequena faz não é *"quantos recursos pendentes"*. É:

> Existe alguém que **possa** julgar estes recursos?

Com duas ou três pessoas acumulando papéis, a resposta pode ser não — e nenhuma tela a formula.
As duas perguntas são distintas e devem continuar sendo:

```text
018:  esta pessoa pode julgar esta peça?          → cinco perguntas, no ato
022:  existe ao menos uma pessoa elegível?        → álgebra de conjuntos sobre autorias
```

A segunda **não** deve ser respondida iterando `recurso × membro` com o guardião individual. Deve
sair dos conjuntos de membros e de autorias já persistidas, preservando a decisão da `018` — e o
requisito precisa citar `T-006` e `FR-031`, senão se lê como reversão silenciosa.

**Um achado colateral que não é sinal, e sim defeito.** A rota `interface:recursos` **não é
alcançada por nenhuma tela**. Não há `reverse` para ela em `acoes.py` nem em `views.py`, e os
únicos `{% url %}` que a citam são o próprio formulário de filtro e a trilha de navegação da peça —
à qual só se chega vindo da listagem. Quem preside só encontra a tela digitando a URL.

Pelo Princípio VI, *uma capacidade que o domínio sustenta mas que nenhuma interface alcança não
deve ser considerada entregue*. A correção cabe em poucas linhas de `acoes.py`, no mesmo padrão de
`Inscrições recebidas (N)`. **Se ela deve entrar no escopo da supervisão ou virar registro próprio
é decisão de governança**, e não deste inventário — mas ela não deve ficar esperando a spec.

## 020 · Anexos do Edital

**Fatos.** Anexos com arquivo, ordem e vínculo à versão.

**Veredito: JÁ MOSTRA.** O que faltasse aqui é pendência de publicação, e a `003` já a exibe onde
se resolve.

## 021 · Sorteio público auditável

**Veredito: SEM FATO.** Especificada, `0` de `77` tarefas. Não grava nada. Quando gravar, entra
pela porta da `015` — o sorteio constitui uma ordem, e ordem já tem tela, ato e obsolescência.

---

# Parte 2 — O que sobrevive

## Pulso — permanente, não precisa ser anomalia

Um único bloco, e é o que justifica a feature para quem a usa todo dia.

| Informação | Fonte | Por que não está em nenhuma tela |
|---|---|---|
| Submetidas no **Processo** | soma de `Inscricao.status=SUBMETIDA` | a contagem existente é por Edital |
| Por Edital | mesma consulta | o Processo não desdobra |
| Últimas 24 h | `submitted_at` | ninguém lê o campo como série |
| Série diária | `submitted_at` | idem |
| Rascunhos | `Inscricao.status=RASCUNHO` | existe por Edital, não por Processo |
| Prazo do período de inscrições | `EventoCronograma.is_registration_period` | **por Edital**, sempre nomeado |
| Próximos marcos | `EventoCronograma` | **por Edital**, sempre nomeado |

**Sobre o visual da série.** A curva acumulada é monotônica: sempre sobe, e as duas concentrações
esperadas — abertura e fechamento — aparecem apenas como mudança de inclinação, que um traço de
doze blocos não comunica. **A série diária mostra as duas pontas diretamente.** O acumulado
permanece como número dito ("1.284 submetidas"), não como desenho. Qualquer gráfico precisa de
equivalente textual e não pode forçar rolagem horizontal do corpo da página.

**Sem percentual.** Inscrição não tem denominador: não há conjunto finito de inscrições esperadas,
e vaga não serve — 40 vagas e 1.284 candidatos não são 3.210 %. A regra geral que daí decorre:
percentual só onde o domínio determina um conjunto finito de unidades esperadas. Avaliação tem;
inscrição não.

## Atenção — catálogo fechado

Cinco sinais. Sinal novo exige revisão da spec.

| # | Sinal | Fato de origem | Por que a dona não basta |
|---|---|---|---|
| S01 | Etapa sem Evento de cronograma | `EtapaAvaliacao.evento` nulo | a validação de publicação **permite** e nada avisa |
| S02 | `status` declarado × posição temporal | `EventoCronograma` | ninguém confronta os dois |
| S03 | Cobertura de avaliação insuficiente | `Atribuicao` × previsão | a dona mostra bem, uma Etapa por vez |
| S04 | Ato de ordenação vigente obsoleto | `selectors.py:170` | só visível abrindo o marco |
| S05 | Recurso sem julgador elegível | `elegibilidade.py` | **nenhuma tela formula a pergunta** |

## Identificadores — um detalhe que o CI cobra

`backend/tests/test_citacoes_de_requisito.py:34` reconhece `FR-`, `SC-`, `UX-`, `SC-UX-` e `D-`, e
falha quando um deles é citado sem definição. **`S01` não é nenhum desses**: citado num template e
definido em lugar nenhum, passa em silêncio — exatamente o defeito que aquele teste nasceu para
pegar, escapando por falta do prefixo.

Como o catálogo é contrato de exibição, `UX-` serve e é verificado — a `011` já usa `UX-007` para
estado vazio. A lista ser fechada vira decisão `D-NNN`, também verificada. Assim *"sinal novo exige
revisão da spec"* deixa de ser promessa e passa a quebrar o build.

## Restrição de desenho que o inventário confirma

Nenhum item das duas listas exige coluna, tabela ou projeção nova. Tudo sai de fato já persistido.

> A supervisão não introduz estado persistente próprio para representar andamento, progresso, sinal
> ou situação derivada. A necessidade de persistir estado novo durante a implementação é indício de
> violação de fronteira e provoca revisão da spec.

Isso não impede cache técnico futuro respaldado por medição; impede que cache vire verdade de
domínio. Vale lembrar que a vitrine atual (`portal/views.py`) materializa as seleções vigentes e
ordena em memória, sem paginação — foi feita para dezenas, e a operação real é dessa ordem.

## Autorização

A base é a presidência do Processo, a mesma que governa `processo_detalhe.html:16`. A recusa é o
**404 uniforme** da convenção `D-017`, não 403. E cada sinal só se exibe a quem alcança a tela dona:
sinalizar "3 recursos sem julgador" a quem não pode abrir recursos é vazamento por agregação.

---

# Parte 3 — Achados que não são requisito

Registrados aqui porque foram encontrados durante o levantamento, e a Constituição é explícita:
achado no meio de uma feature vira registro, não escopo da seguinte.

| Achado | Onde | Natureza |
|---|---|---|
| `interface:recursos` não é alcançável por nenhuma tela | `acoes.py`, templates | defeito de jornada, Princípio VI |
| "Em preenchimento" × "rascunho" | `inscricoes.html:93` | vocabulário, Princípio I |
| `Inscricao` não tem `updated_at`; atividade só pela trilha | `inscricoes/models.py` | limite conhecido |
| Ato emitido e não divulgado | `017` | candidato a sinal, semântica a definir |
| Cadeia de quatro saltos até os resultados divulgados | `detalhe` → marco → ato → publicações | profundidade de navegação |

## O que este inventário não decidiu

Duas perguntas continuam de governança:

1. **Etapa passa a ter ciclo de vida?** Recomendação registrada: não por causa de uma tela. Se
   houver necessidade normativa — proibir avaliação fora da janela —, é feature de domínio própria.
2. **`EventoCronograma.status` deixa de ser declarado?** Recomendação registrada: não agora.
   Exibir declarado e temporal lado a lado resolve a leitura sem alterar o contrato do cronograma.
