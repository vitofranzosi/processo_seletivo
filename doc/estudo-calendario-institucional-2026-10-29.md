# Calendário Institucional de Processos Seletivos — análise e proposta de spec

**Data**: 29/10/2026 (revisão do mesmo dia) · **Base**: `main` em `0ff70f07` · **Natureza**:
investigação. Nenhum código, migration, dependência ou spec foi alterado.

**Revisão de 29/10, depois da primeira leitura do usuário:**

- **`Q1` decidida**: toda identidade da gestão. A condição é exibir só cronogramas publicados e
  vigentes, no escopo da unidade, sem visão entre unidades.
- **A visão mensal entra no MVP**, ao lado da agenda, com a mesma fonte e os mesmos filtros. A
  avaliação do impacto está na seção G.
- **Previsto × efetivo**: a distinção entre o prazo previsto no cronograma e o prazo aberto pela
  publicação de um ato virou regra explícita da especificação (C.5).

Os caminhos de código são relativos a `backend/processo_seletivo/`, e os de teste a `backend/tests/`.
Os identificadores de requisito citados (`FR-`, `D-`, `G-`) são de specs existentes. Os critérios
propostos aqui usam `CA-` e as decisões pendentes `Q`, para não colidir com a varredura de
`test_citacoes_de_requisito.py` quando esta proposta virar spec.

---

## 0. Em uma página

1. **O dado existe, estruturado e com uma régua só.** Todo Evento publicado tem:
   - identidade estável;
   - início com fuso e término anulável;
   - local;
   - marca de período de inscrições;
   - cancelamento declarado.

   A fase — planejado, em andamento, concluído — já é **derivada do relógio** numa régua única
   (`editais/domain/calendario.py:79`, `editais/domain/fase_do_evento.py:55`), que a gestão e o
   portal leem. Nada precisa ser cadastrado de novo.
2. **A fonte certa não é a tabela de cronograma.** `EventoCronograma` é a linha de **elaboração**: a
   Retificação grava na Versão Consolidada e não escreve de volta, e o Evento acrescentado por
   Retificação nem tem linha (`comissoes/domain/etapas.py:49`). O calendário tem de ler
   `VersaoConsolidada.content["schedule"]` da versão **vigente**. O carregador em lote que faz isso
   em duas consultas fixas já existe (`publicacoes/application/selectors.py:294`,
   `versoes_vigentes`), e a Visão Geral o usa.
3. **A lacuna é real e foi deixada aberta de propósito.** Hoje cada leitura temporal é de **um**
   Processo (supervisão, `022`) ou de **um** Edital (portal, `047`). A única tela entre Processos, a
   Visão Geral (`040`), mostra só o período de inscrições. A `022` declarou fora de escopo
   *"qualquer visão entre Processos"*.
4. **Metade dos filtros pedidos não tem dado.**
   - Não existe modalidade nem natureza do Processo.
   - Não existe categoria de Evento: `type` é texto livre.
   - Toda pessoa da gestão tem **uma** unidade só. A visão entre unidades é a `G-014` da `040`, que
     o usuário manteve fora nesta etapa.
5. **Duas visualizações, uma leitura.** A **agenda** responde *"o que acontece nesta semana"*. O
   **mês** responde *"como os marcos dos Editais se distribuem, e onde se acumulam"*. As duas são
   formas diferentes da mesma lista de itens, montada pela mesma função, com os mesmos filtros e as
   mesmas três consultas. O mês acrescenta uma função pura de grade, um parcial de template e
   regras de folha — **nenhuma consulta**.

**Recomendação final: implementar com ajustes, com as duas visualizações no MVP.**

- **A agenda é a visualização padrão.**
- **A grade do mês marca os marcos** — Evento pontual, abertura e encerramento de período —, com a
  contagem do dia e destaque para dia com mais de um marco.
- **Os períodos ficam fora da grade.** Eles são listados abaixo dela como intervalos, e não
  desenhados como barras nem repetidos dia a dia.
- **Só o previsto no cronograma publicado e vigente.** O prazo aberto por ato fica para a fase 1.3,
  com marca própria.

O acréscimo do mês é de cerca de **40% sobre a agenda sozinha**, e nada dele é infraestrutura.

---

## A. Diagnóstico do estado atual

### A.1 Como o cronograma é modelado, armazenado e apresentado

| Camada | Onde | O que é |
|---|---|---|
| Elaboração | `editais/models/cronograma.py:9` `Cronograma` (1:1 com `Edital`) e `:17` `EventoCronograma` | Linhas editáveis enquanto o Edital está `EM_ELABORACAO`. Lidas pela composição (`interface/views.py`, `_eventos_do_cronograma`) |
| Submissão | `publicacoes/models.py:8` `RevisaoEdital.content` | Retrato do rascunho submetido à homologação |
| Publicação | `publicacoes/models.py:46` `Publicacao`, e `publicacoes/models_retificacao.py:8` `VersaoConsolidada.content["schedule"]` | O cronograma **normativo**: lista de dicionários montada em `publicacoes/application/publish_edital.py:353` |
| Leitura vigente | `publicacoes/application/selectors.py:27` `effective_version(edital_id, at)` e `:294` `versoes_vigentes(edital_ids, at)` | A versão com maior `valid_from` já iniciado; a segunda é a forma em lote, em duas consultas |

**Forma do Evento publicado**: `id`, `type`, `description`, `startAt`, `endAt` (anulável), `order`,
`status`, `location`, `isRegistrationPeriod`.

**Apresentação atual** — toda de um Edital ou de um Processo:

- **Composição** (`interface:compor-etapa … "cronograma"`) e **Revisão** (`interface/revisao.py:789`).
  Nenhuma das duas tem âncora estável por Evento.
- **Supervisão do Processo** (`022`). `interface/supervisao.py:110` `Marco`, `:388`
  `marcos_do_edital` e `:445` `pulso` mostram os próximos marcos de cada Edital do Processo. A tela
  fica atrás de `pode_gerir_comissao` (`:267`).
- **Página do Processo**: o mesmo `pulso` (`processo_detalhe.html`).
- **Visão Geral** (`040`). `interface/visao_geral.py:803` `ler` é a única leitura entre Processos,
  e só traz o **período de inscrições**.
- **Portal**. `portal/leitura.py:36` `cronograma` e `:101` `agora_e_proximo` são renderizados em
  `portal/templates/portal/_cronograma.html`, com âncora `#cronograma-titulo` (`selecao.html:410`).
- **PDF**: `publicacoes/infrastructure/pdf.py`, `_cronograma`.
- **Relatório do Edital** (`099`). `interface/relatorio_do_edital.py:1460` `_cronograma` compara
  *previsto × após Retificações × ato registrado*.

### A.2 Entidades de evento, período, data e prazo

- **Evento pontual × período.** Não há tipo para isso: é `endAt` nulo ou não. O relatório da `099`
  já trata como período o Evento cujo término cai em **outro dia** (`_cronograma`, função interna
  `periodo`). A agenda deve usar a mesma regra.
- **Instantes, não datas.** `validate_event` (`editais/domain/cronograma.py:17`) exige offset
  explícito. O dia de um instante se lê na zona institucional `ZONA = America/Sao_Paulo`
  (`shared/tempo.py`), como exige a Constituição no Princípio II. `ano_do_evento`
  (`calendario.py:103`) documenta o defeito de 31/12 às 23:30 lido em UTC.
- **Fase derivada.** `calendario.fase` (`:79`) devolve PLANEJADO, EM_ANDAMENTO ou CONCLUIDO.
  `vencido` usa `<` estrito, e o pontual vence pelo início (`037`, `FR-545`).
  `fase_do_evento.fase_do_evento` (`:55`) põe o cancelamento antes da fase e manda o período de
  inscrições para a régua do período (`inscricoes/domain/periodo.py:51`). Por essa régua, o
  período **sem término segue aberto**.
- **O único estado declarado é `CANCELADO`.** O `status` gravado no modelo (`PLANEJADO`…) é legado:
  a `045` tornou a fase derivada (`STATUS_DECLARAVEIS` em `editais/domain/cronograma.py`).
- **Período de inscrições**: a marca `isRegistrationPeriod`. Há no máximo um por cronograma, por
  constraint parcial.
- **Vínculo com Etapa.** `stages[].scheduleEventId` aponta o Evento de que a Etapa depende
  (`editais/domain/etapas.py:64`).
- **Prazos que não estão no cronograma.**
  - A **janela recursal** é contada a partir da publicação do ato, e não da data digitada no
    cronograma (`recursos/domain/janela.py`, docstring). O prazo real já é calculado em lote para a
    vitrine: `portal/leitura.py:534` `prazos_de_recurso`, sobre
    `divulgacao/application/selectors.py:133` `historico_publico_dos_editais`.
  - Os prazos de **convocação** são operacionais, por candidato, e moram na convocação.
  - Um Evento chamado "Prazo de recurso" no cronograma é, portanto, a **previsão publicada**, e
    pode divergir do prazo que o sistema computa (C.5).

### A.3 Alterações e Retificações

- O que a Retificação pode mudar em cada campo do Evento está em
  `editais/domain/mutabilidade.py:422-443`:

  | Campo | Natureza |
  |---|---|
  | `description`, `startAt`, `endAt`, `location`, `isRegistrationPeriod` | retificável |
  | `type` | **não** retificável ("muda a que o Evento serve") |
  | `id`, `order` | estruturais |
  | `status` | derivado |

  O `id` é estável entre versões, e isso importa para a fase 2.
- **A vigência da Retificação pode ser futura.** Cada Retificação publicada materializa uma nova
  `VersaoConsolidada`, com `valid_from` igual à sua vigência
  (`publicacoes/application/retificacoes.py:807-813`). A vigência **pode ser futura e nunca
  retroativa** (`:881-883`). Existe, portanto, a situação *"Retificação publicada que ainda não
  vigora"*. `effective_version(at=agora)` a ignora até `valid_from`, e o portal faz o mesmo
  (`selecoes_publicas`, `:319`).
- **A proveniência é registrada por caminho.** `ProvenienciaConteudo` (`models_retificacao.py:93`)
  registra qual Publicação fixou cada `target_path` da versão (por exemplo,
  `/schedule/id=<uuid>/endAt`). O assistente já a usa (`duvidas/domain/origem.py:38`). É o que
  permitiria marcar *"alterado pela Retificação nº X"* sem comparar conteúdos inteiros.
- **Atos de elaboração não mudam a versão vigente.** Isso vale para a Retificação em elaboração, em
  revisão ou homologada (`models_retificacao.py:37`).

### A.4 Situações do cronograma, pelos estados que existem

O cronograma não tem estado próprio: herda o do Edital (`processos/models.py:36`) e o da versão.

| O que o pedido chama de… | O que existe | Fonte das datas |
|---|---|---|
| em elaboração | `Edital.EM_ELABORACAO` | `EventoCronograma` |
| aprovado | `EM_REVISAO` (submetido) e `HOMOLOGADO` (homologado, não publicado) | `RevisaoEdital.content` |
| publicado | `PUBLICADO` com versão vigente | `VersaoConsolidada` vigente |
| encerrado | `Edital.ENCERRADO`, por ato (`processos/application/finalizacao.py`) | a última versão vigente |
| cancelado | `Edital.CANCELADO`; e, por Evento, `status = CANCELADO` | idem |
| substituído | **não é estado**: é a `VersaoConsolidada` de `valid_from` anterior | histórico (`public_history`) |

O `ProcessoSeletivo` tem situação própria (`EM_ELABORACAO`, `ATIVO`, `ENCERRADO`, `CANCELADO`) e
**nenhuma data**: *"não existe marco do Processo"* (`022`, `D-005`; repetido em `040`, `D-001`).

### A.5 Processo, Edital, Unidade e pessoas

- `Edital → ProcessoSeletivo` por chave estrangeira; os dois carregam `institution_scope` (texto).
- `Unidade` (`unidades/models.py:25`) **materializa** o escopo pelo `codigo`, e nada aponta para
  ela por chave estrangeira. Só `cefor` está cadastrada (`unidades/unidades.json`).
- O ator é `Actor(subject, institution_scope, permissions)` (`seguranca/domain.py:5`). Na gestão,
  ele vem de `interface/identidade.py:161` `ator_da_sessao`, com escopo padrão `cefor`.
- **Cada ator tem um escopo só.** A `060` lista *"operador com mais de uma unidade, e papel de
  visão institucional entre unidades"* entre o que fica fora.
- As pessoas ligam-se ao Processo pela comissão (`comissoes/models.py:31` `MembroComissao`, função
  `PRESIDENTE`/`MEMBRO`) e à Etapa pela alocação (`:76` `AlocacaoEtapa`).
  `comissoes/application/selectors.py:22` `comissoes_da_pessoa(ator)` lista os vínculos ativos.

### A.6 Papéis e permissões aproveitáveis

- **Papéis** (`interface/identidade.py:25` `PAPEIS`): elaborador, homologador, publicador, gestor,
  julgador, auditor, exportador e participante do piloto.
  - O **gestor** tem `visao:consultar`, a porta da Visão Geral e do relatório consolidado.
  - A **presidência** não é papel: é vínculo de comissão (`comissoes/domain/autorizacao.py:65`
    `pode_gerir_comissao`).
- **Escopo**: o filtro está na própria consulta (`.filter(institution_scope=ator.institution_scope)`).
  - Objeto de outro escopo responde 404.
  - Falta de capacidade responde 403 explicado (`seguranca/application/authorization.py:117,124`).
  - Listagens **não** têm 404 de escopo: *"listagem de escopo alheio não existe"*
    (`views.py:325`).
- **Visibilidade atual dos Editais na gestão.**
  - Qualquer identidade do escopo vê a lista de Processos e Editais **em todos os estados**,
    inclusive em elaboração (`views.py:258` `lista`).
  - Ela também abre o detalhe e a composição em modo leitura, sem papel nenhum.
  - O que exige papel é o anexo do rascunho (`LEITURA_DO_RASCUNHO`) e as ações.
- **No portal**, qualquer pessoa vê o cronograma vigente de toda seleção publicada, de **todas** as
  unidades (`selecoes_publicas` não filtra escopo).

**Consequência**: um calendário que mostre só o cronograma **publicado** não expõe nada que já não
seja público. A questão de autorização se reduz a *em que lugar da gestão* ele aparece, e não a *o
que ele pode revelar*. Foi a razão da `Q1`.

### A.7 Frontend reaproveitável

- **Templates Django renderizados no servidor**, sem framework JS. O htmx fica restrito à
  composição e à Retificação, e as telas de leitura usam formulário GET (`visao_geral.html:25`).
- **CSP sem `unsafe-inline`** (`shared/politica_de_conteudo.py`). O estilo vai para
  `interface/static/interface/telas/<tela>.css`, carregado por `{% block estilo_da_pagina %}` e
  registrado em `QUEM_CARREGA` (`tests/interface/test_folha_estatica.py`).
- **Classes prontas:**
  - tabelas: `table`, `.rolavel-no-estreito`, `.tabela-estreita`;
  - situação do Edital: `.situacao .s-<STATUS>` (`gestao/componentes.css:21-35`);
  - números de síntese: `.resumo`;
  - estado vazio: `.vazio`, `.nenhuma`;
  - texto só para leitor de tela: `.oculto`;
  - filtros: `.filtros-da-visao`, que mora em `telas/visao-geral.css` e teria de ser promovida ou
    repetida;
  - lista de marcos: `ul.marcos`;
  - paginação: `nav.paginacao`.
- **Armadilha**: `.marca` (o "em andamento" da supervisão) só tem desenho dentro da Visão Geral.
- **Navegação**: `interface/navegacao.py:62` `SECOES`, com predicado por capacidade e ícone SVG
  próprio em `base.html`. `tests/interface/test_shell_da_gestao.py` percorre `SECOES`, e o item
  novo é testado de graça (item visível ⇔ 200, ícones únicos).
- **Guardiões que a tela nova enfrenta:**
  - `test_politica_de_conteudo.py`;
  - `test_acessibilidade.py`: classe exige regra, controle nativo e contraste. Os pares de
    contraste são uma **lista literal** (`PARES`, `:79`), e cor nova de destaque exige par novo;
  - `test_larguras.py`;
  - `test_gramatica_das_portas.py`, se houver `raise Http404`;
  - as varreduras de vocabulário, se a tela usar os termos delas.

### A.8 Calendário, agenda ou endpoint semelhante

**Não há.** A busca por agenda, calendário, timeline e ics não encontrou nenhuma tela ou rota. Os
parentes mais próximos, todos reaproveitáveis:

| Peça | Reaproveitamento |
|---|---|
| `fase_do_evento.eventos_do_conteudo`, `instantes_do_evento`, `esta_cancelado`, `fase_do_evento`, `descricao_do_evento` | integral: é a régua |
| `fase_do_evento.marcos_pendentes` (`:87`) | modelo da derivação; a agenda precisa da variante *por janela* |
| `versoes_vigentes` | integral: carga em lote |
| `visao_geral.ler` (`:803`) | padrão de montagem: filtros relacionais → lote de versões → derivação em memória, com número fixo de consultas (`SC-209`) |
| `supervisao.Marco`, `lido_em` | forma do item e declaração do instante da leitura |
| `portal/leitura.prazos_de_recurso` | o prazo recursal **efetivo**, já em lote — candidato da fase 1.3 |
| `calendar.Calendar` da biblioteca padrão | as semanas do mês, sem dependência |
| API pública `versao-vigente` | já entrega o `schedule` de um Edital; não lista vários |

### A.9 Limitações encontradas

1. **Não há categoria de Evento.** `type` é texto livre e não retificável. O relatório da `099` já
   infere "resultado" por substring (`_natureza_do_evento`), e essa inferência não deve se espalhar.
2. **Não há modalidade nem natureza do Processo.** O próprio modelo recusa criá-la (comentário de
   `requerimento_momento`, `029`, `D-002`).
3. **Não há visão entre unidades** (`040`, `G-014`/`G-010`; `060`, fora de escopo). Mantida fora
   pelo usuário.
4. **Faltam âncoras por Evento.**
   - O `<li>` do portal não tem `id`.
   - A composição e a Revisão numeram por posição.
   - A página do Edital na gestão (`interface:detalhe`) **não tem seção de cronograma**.
   - O destino possível hoje é `portal:selecao` + `#cronograma-titulo`.
5. **O cronograma é previsão publicada, não execução.** O ato registrado (publicação de resultado,
   janela recursal) mora em outros modelos.
6. **O conteúdo vigente é carregado inteiro.** `versoes_vigentes` materializa o `content` todo —
   Perfis, quadros, documentos — para que se leia só o `schedule`. Não foi medido para a agenda. A
   Visão Geral já paga o mesmo custo.

---

## Avaliação crítica

**1. Resolve uma necessidade que o sistema não atende?** Sim, e uma só: a leitura temporal **entre
Processos**.

- A supervisão responde por Processo e o portal por Edital.
- A `022` deixou de fora *"qualquer visão entre Processos"*, e a `040` só olha o período de
  inscrições.
- A numeração da amostra (Edital 89/2026, `doc/achado-edital-89-2026-bolsista-no-catalogo.md`)
  indica dezenas de Editais por ano no Cefor.

A necessidade foi confirmada pelo usuário em 29/10 — inclusive a de enxergar o **mês** —, mas
ainda não foi observada com quem gere (`CA-14`).

**2. Há dados suficientes sem modificações significativas?** Para as duas visualizações, sim, sem
nenhuma mudança de modelo. Para os filtros de modalidade, categoria e unidade, **não**, e criá-los
seria a classificação manual que o pedido proíbe.

**3. Há problema com cronogramas retificados, condicionais ou não publicados?**

- **Retificados**: nenhum, desde que a leitura seja da versão vigente. Ler `EventoCronograma` seria
  o erro clássico (`D-012` do plano da `011`, citado em `comissoes/domain/etapas.py:49`).
  - O caso fino é a **Retificação publicada com vigência futura**. Até `valid_from`, as duas
    visualizações mostram a data antiga, que **é** a vigente, como faz o portal.
  - No mês isso pesa mais que na agenda, porque a grade olha semanas à frente. Por isso o aviso de
    *"Retificação publicada vigora a partir de …"* subiu da fase 1.1 para o MVP (C.1).
- **Condicionais**: o sistema não os modela. *"A partir de"*, *"a definir"* e *"após o resultado"*
  vivem no texto de `description`. O início é obrigatório, e a tela mostra a data que o Edital
  publicou, como o portal.
- **Não publicados**: misturá-los é o risco mais grave da proposta. O MVP os exclui por construção:
  sem versão vigente não há Evento.

**4. A quantidade de eventos compromete a legibilidade?** Com nomes em toda célula, sim.

- Trinta Editais simultâneos × 4 a 18 Eventos dão 120 a 540 Eventos por semestre, e de 20 a 90
  marcos por mês.
- Os inícios de período se concentram nas mesmas semanas.

Daí as três regras da grade (C.1):

- a célula diz a **contagem**;
- a célula mostra no máximo **dois** nomes, e só em tela larga;
- o **período não ocupa os dias intermediários**.

Com elas, o dia mais carregado mostra *"7 marcos"*, dois nomes e *"mais 5"*, e o detalhe fica com
a agenda do dia.

**5. A grade mensal basta, ou a agenda entrega mais?** Nenhuma das duas basta sozinha.

| Visualização | Responde bem | Responde mal |
|---|---|---|
| Agenda | *o que acontece nesta semana*, *qual Edital originou*, *onde está o cronograma oficial* | a forma do mês, e onde os marcos se acumulam ao longo dele |
| Mês | a distribuição no mês e os dias de acúmulo | o conteúdo do dia |

Por isso as duas visualizações, com a célula do mês levando à agenda daquele dia.

**6. O que adiar para evitar overengineering?**

- Visão semanal em colunas: a agenda de 7 dias **é** a semana.
- Barras de período atravessando a grade.
- Filtros de unidade, modalidade e categoria.
- Rascunhos, alerta e notificação.
- `.ics` e assinatura.
- Qualquer cache, tarefa agendada ou tabela de projeção.

**7. Há risco de ler data prevista como obrigação já atribuída?** Sim, e a grade o aumenta: um dia
destacado parece um dia "cheio de trabalho". Mitigação:

- o título e a legenda dizem *datas previstas nos cronogramas publicados*;
- nenhum item nomeia pessoa ou diz *pendente* ou *atrasado*;
- o concluído é dito *concluído*, e não *cumprido*;
- o destaque mede **concentração de marcos publicados**, não carga de ninguém;
- o prazo aberto por ato tem marca própria quando vier (C.5).

**8. Qual o menor MVP capaz de demonstrar valor?** A página com as duas visualizações (seção C). A
agenda sozinha seria menor, mas não demonstra o que o usuário declarou ser o objetivo — a visão
consolidada do mês. O custo dessa diferença está na seção G.

**Alternativas comparadas**

| Forma | Responde bem | Custo | Veredito |
|---|---|---|---|
| **Agenda cronológica por dia** | semana, origem, link oficial; concentração pela contagem no cabeçalho do dia | baixo | **MVP, padrão** |
| **Mês com contagem e destaque**, períodos listados à parte | distribuição no mês; dias de acúmulo | baixo a médio: tabela semântica, grade em função pura, folha | **MVP, segunda visualização** |
| Mês com barras de período | duração visual dos intervalos | alto: período atravessando semanas, sobreposição, leitor de tela, 375 px | não fazer |
| Visão semanal em colunas | a semana | médio; a 375 px vira lista de qualquer jeito | não fazer |
| Painel de próximos eventos (números + 5 itens) | *"há algo urgente?"* | mínimo | entra como síntese das duas visualizações |
| Ampliar a Visão Geral | período de inscrições, já entregue | baixo, mas mistura duas perguntas | não: a `040` (`D-002`) separa leitura institucional de condução |

---

## B. Veredito de produto

**Valor potencial.** A agenda tira o gestor da navegação Processo a Processo para responder *"o que
acontece nesta semana?"*. O mês mostra a forma do período e os dias em que marcos de Editais
diferentes se acumulam — dois resultados e uma prova no mesmo dia — antes que aconteça. O valor é
de coordenação, não de controle. O sistema já derivava tudo isso; faltava a leitura transversal.

**Usuários beneficiados**

- **Toda identidade da gestão** da unidade (`Q1`, decidida), o que inclui:
  - quem coordena a unidade (hoje, o papel gestor);
  - a presidência e os membros de comissão, que conduzem os Processos;
  - os elaboradores, que ao datar um Edital novo veem o acúmulo existente. É um uso indireto: a
    página não mostra rascunho.

**Riscos**

| Risco | Mitigação |
|---|---|
| Ler a página como cronograma oficial | título, legenda e proveniência; link "cronograma publicado" em cada item; nenhum dado que o Edital não publicou |
| Ler a data prevista como tarefa atribuída | sem responsável, sem "pendente", sem "atrasado"; destaque descrito como concentração de marcos |
| Confundir prazo previsto com prazo aberto por ato | C.5: vocabulário, marca e contagem separados; o efetivo só entra na 1.3 |
| Retificação com vigência futura | aviso no MVP, nas duas visualizações |
| Célula lotada no mês | contagem + até dois nomes em tela larga; o resto na agenda do dia |
| Pressão por filtros sem dado | recusados por escrito na spec, com a razão |

**Oportunidades**

- Uma régua única de *Eventos numa janela*, posta no domínio, serve depois ao `.ics` e ao portal.
- Um feed por Edital, com o mesmo dado público, sem autorização nova.

**Recomendação.** Implementar **com ajustes**, com as duas visualizações. Só o publicado vigente,
no escopo do ator, com os filtros que o dado sustenta. Os ajustes que permanecem em relação à
pergunta original:

- não há visão entre unidades;
- não há filtros de modalidade nem de categoria;
- não há barras de período na grade;
- o prazo efetivo não entra no MVP.

---

## C. Especificação funcional (MVP)

### C.1 Comportamentos

**Lugar e nome.**

- Seção **Agenda** na barra da gestão, grupo *Trabalho*, depois de *Visão Geral*, na rota
  `/gestao/agenda`.
- Título **Agenda dos Editais**.
- Duas abas, que são **links** (e não um componente de abas): **Próximos dias** · **Mês**. Elas
  levam a mesma query string, de modo que trocar de visualização preserva os filtros.
- Subtítulo fixo: *"Datas previstas nos cronogramas publicados e vigentes. O cronograma oficial é o
  do Edital e de suas Retificações."*
- O instante da leitura é declarado (*"lido em 29/10/2026 às 14:02"*), como na supervisão.

**O que entra** — o mesmo conjunto nas duas visualizações. Cada Evento da versão vigente de cada
Edital do escopo, desde que:

1. a situação do Edital seja `PUBLICADO` ou `ENCERRADO`. `CANCELADO` fica fora, pela regra da
   vitrine;
2. o Evento toque a janela da visualização: os dias pedidos, na agenda; o mês, no mês;
3. se o Edital está `ENCERRADO`, o Evento já tenha sido concluído. É a regra de
   `EDITAL_PAROU_POR_ATO` (`supervisao.py:549`): não se anuncia o que a instituição encerrou.

**Marco × período** — a mesma classificação nas duas visualizações.

- **Marco pontual**: Evento sem término, ou com término no mesmo dia na `ZONA`. Lança **um** item,
  no seu dia, com a hora (*"14h"*, *"8h–12h"*).
- **Período**: Evento com término em outro dia. Lança **dois** marcos do mesmo Evento: **Abre**, no
  dia de início, e **Encerra**, no dia de término. Os dois têm a mesma descrição, o mesmo destino e
  o intervalo escrito, e nunca ocupam os dias intermediários. É a resposta ao exemplo do pedido:
  inscrições de 3 a 15 de novembro são **um** intervalo, com dois limites marcados, e não treze
  eventos.
- **Período de inscrições sem término**: segue *aberto* pela régua do período. Lança só *Abre*, e
  nunca ganha encerramento inventado.
- **Cancelado**:
  - aparece na agenda com o texto **Cancelado** e a data publicada, como no portal (`FR-766`; `Q2`);
  - não entra na grade nem em número nenhum.

**Visualização "Próximos dias"** (padrão)

- **Janela padrão**: hoje + 6 dias. Atalho *Próximos 30 dias*.
- **Bloco "Em curso"**, no alto. Cada período aberto aparece uma vez, com o intervalo e *"encerra em
  N dias"* ou *"sem término declarado"*.
- **Dias**: cada dia é um `<h2>` (*"qui, 12/11 · 4 marcos"*) e uma lista. Acima de 8 itens, a lista
  se agrupa por Edital.
- **Item**, nesta ordem:
  1. hora, ou *Abre*/*Encerra*;
  2. descrição publicada (`descricao_do_evento`);
  3. *Edital NN/AAAA — título do Processo*, com o selo de situação só quando o Edital não está
     `PUBLICADO`;
  4. local, quando declarado (`FR-127`);
  5. dois links: **Edital** → `interface:detalhe`, e **Cronograma publicado** → `portal:selecao` +
     `#cronograma-titulo`.
- **Dia selecionado**: `?dia=AAAA-MM-DD` mostra só aquele dia e, à parte, *"períodos em curso neste
  dia"*. É o destino da célula do mês.

**Visualização "Mês"**

- **Janela**: o mês civil na `ZONA`, por `?mes=AAAA-MM`. O padrão é o mês corrente.
- **Navegação**: *‹ outubro* · **novembro de 2026** · *dezembro ›* · *Hoje*.
- **Grade**: `<table>` com `<caption>` *"Novembro de 2026 — marcos dos cronogramas publicados"*.
  - Sete colunas, de **domingo a sábado**, cada uma com `<th scope="col">` e `<abbr>` (*dom* para
    domingo), conforme a convenção dos calendários brasileiros.
  - Os dias fora do mês ficam vazios, sem marcos. Os marcos do mês vizinho são do mês vizinho:
    mostrá-los contaria o mesmo marco em duas páginas.
- **Célula**:
  - o número do dia;
  - quando há marco, um link para a agenda daquele dia, com o texto *"N marco(s)"*;
  - em tela larga (≥ 60rem), até **dois** marcos nomeados (*"12/2026 · Encerra Inscrições"*,
    reticências quando longo) e *"mais N"*;
  - abaixo de 60rem, só o número do dia e a contagem. Sete colunas cabem em 375 px a ~49 px cada,
    com o alvo de toque mínimo.
  - **Hoje**: `aria-current="date"` e contorno.
- **Destaque de concentração**: dia com **dois ou mais marcos**.
  - É *"múltiplos eventos"*, nas palavras do pedido, e não um limiar inventado.
  - A contagem fica em negrito e a célula ganha fundo e borda.
  - A cor nunca é o único sinal, porque a contagem está escrita.
  - O par de cor entra em `PARES` do teste de contraste.
- **Períodos do mês**, logo abaixo da grade: todo período que toca o mês, uma linha cada.
  - Cada linha traz descrição, Edital, intervalo (*"03/11 a 15/11"*) e situação (*em curso*, *por
    vir*, *concluído*).
  - A ordem é pelo início.
  - Na grade, o período aparece só pelos seus dois marcos. A lista é onde ele é dito como intervalo.
- **Legenda** curta, abaixo da grade: *"Cada marco é uma data prevista no cronograma publicado:
  um Evento pontual, ou a abertura ou o encerramento de um período."*

**Síntese** — uma linha de números, calculada sobre a janela da visualização ativa, sem consulta a
mais.

| Número | Próximos dias | Mês |
|---|---|---|
| Marcos | nos próximos 7 dias | no mês |
| Editais envolvidos | nesses marcos | nesses marcos |
| Encerramentos de período | nos próximos 7 dias | no mês |
| Concentração | dia mais carregado (data e quantidade) | dias com mais de um marco, e o mais carregado |

Cancelados não contam.

**Aviso de Retificação a vigorar** — nas duas visualizações. Quando um Edital da janela tem
Retificação publicada com `valid_from` posterior a agora, o aviso diz *"Edital 12/2026: Retificação
publicada vigora a partir de 05/11 — as datas abaixo são as vigentes hoje."* e aponta o histórico
público do Edital. Uma consulta a mais (D.3).

**Filtros** (GET), **os mesmos nas duas visualizações**. Eles operam sobre o que a página já
carregou, sem consulta a mais, como a vitrine faz desde a `024` (`D-003`):

| Filtro | Fonte | Situação |
|---|---|---|
| Janela | dias (agenda) ou mês (grade) | MVP; é o que distingue as visualizações |
| Edital | Editais carregados | MVP; lista os que têm marco na janela |
| Espécie estrutural do Evento: *período de inscrições* · *ligado a Etapa* · *demais* | `isRegistrationPeriod`, `stages[].scheduleEventId` | MVP |
| Processo | Processo dos Editais carregados | não no MVP: o Edital já nomeia o Processo |
| Situação do Edital | `Edital.status` | não: só `PUBLICADO`/`ENCERRADO` chegam, e o selo já os distingue |
| Unidade | `institution_scope` | **recusado nesta etapa** (`Q1`, `G-014`) |
| Modalidade de seleção | inexistente | **recusado**: não há taxonomia, e criá-la é classificação manual |
| Categoria do Evento por `type` | texto livre | **recusado**: inferir de texto livre decide regra lendo o que alguém digitou (comentário de `is_registration_period`) |

### C.2 Regras de visibilidade

1. **Só conteúdo publicado e vigente.** Nunca `EventoCronograma`, `RevisaoEdital`, alteração de
   Retificação não publicada ou versão de `valid_from` futuro. A versão futura só é **anunciada**
   pelo aviso, e nunca **aplicada**.
2. **Só o escopo do ator**, pelo filtro na consulta. Outro escopo não existe para a página: não há
   404, ele só não é listado.
3. **Acesso: toda identidade da gestão** (`Q1`, decidida em 29/10).
   - O predicado é `_toda_identidade`, o mesmo da lista de Processos.
   - A decisão é condicionada às regras 1 e 2 e às permissões existentes, e não cria papel nem
     capacidade.
   - A justificativa registrada: a página só mostra o que o portal já publica, e a lista de
     Processos já mostra esses Editais a qualquer identidade do escopo.
4. **Sem visão entre unidades nesta etapa** (`Q1`; `G-014`/`G-010`).

### C.3 Interações e estados da interface

- **Hierarquia**:
  1. título e proveniência;
  2. abas;
  3. aviso de Retificação, quando houver;
  4. síntese;
  5. filtros, recolhíveis a 375 px;
  6. o conteúdo da visualização.
- **Da grade ao dia**: a célula leva à agenda do dia (`?visao=dias&dia=…`), com os filtros
  preservados. *"Voltar ao mês"* leva de volta, com o mesmo `mes`.
- **Do item à origem**: os dois links do item. O estado da página vive inteiro na query string, e
  não há armazenamento no navegador.
- **Tipo do Evento** por **texto** (*Abre*, *Encerra*, *Inscrições*, *Etapa: Prova objetiva*). O
  ícone é opcional, e a cor nunca é o único sinal.
- **Fase**:
  - em andamento → *"Acontecendo agora"* com `aria-current`, como no portal;
  - futuro → só a data;
  - concluído → *"concluído"*, em texto secundário;
  - cancelado → *"Cancelado"*.
  - Nunca *atrasado*, *pendente* ou *cumprido*.
- **Estados**:
  - *Nenhum Edital publicado no escopo* → *"Nenhum Edital da unidade tem cronograma publicado."*,
    nas duas visualizações; a grade não é desenhada.
  - *Janela sem marco* → na agenda, *"Nenhum marco entre 29/10 e 04/11."*. No mês, a grade
    desenhada vazia e a mesma frase. Nas duas, quando houver, vem também *"O próximo é em 18/11:
    Resultado final — Edital 12/2026."*, tirado da mesma lista, sem consulta.
  - *Filtro sem resultado* → o mesmo texto, com *"limpar filtros"*.
  - *Sem permissão* não ocorre: o acesso é de toda identidade. Sem identidade, vale o
    `pedir_identificacao` de toda a gestão.
  - *Carregando*: não há, porque a página é renderizada no servidor.
- **Responsividade e acessibilidade (WCAG 2.1 AA, eMAG)**:
  - lista semântica na agenda e `<table>` com `caption`/`th scope` no mês;
  - `<time datetime>` em todo instante;
  - contraste pelos pares de `PARES`;
  - alvo de toque ≥ 44 px;
  - sem rolagem horizontal a 375 px;
  - foco visível; controles nativos num `<form method="get">`;
  - abas como links com `aria-current="page"` na ativa.

### C.4 Critérios de aceitação verificáveis

| # | Critério |
|---|---|
| CA-01 | Um Edital `EM_ELABORACAO`, `EM_REVISAO` ou `HOMOLOGADO` com Eventos na janela não contribui com item, célula nem número, em nenhuma das visualizações |
| CA-02 | Uma Retificação publicada e vigente que muda `startAt` faz as duas visualizações mostrarem a data nova, e não a da linha `EventoCronograma` |
| CA-03 | Um Evento acrescentado por Retificação, sem linha relacional, aparece |
| CA-04 | Uma Retificação publicada com `valid_from` futuro não altera as datas antes daquele instante, e altera depois. Antes, o aviso de Retificação a vigorar aparece |
| CA-05 | Um período 03/11–15/11 lança *Abre* em 03/11 e *Encerra* em 15/11, nas duas visualizações. Nenhuma célula ou dia entre os dois o contém, e ele aparece **uma** vez em *Períodos do mês* e em *Em curso* |
| CA-06 | Um Evento às 23:30 de 31/12 na `ZONA` cai em 31/12, e não em 01/01, inclusive na grade de dezembro × janeiro |
| CA-07 | Um Evento cancelado aparece na agenda como *Cancelado* e não entra na grade nem em nenhum número |
| CA-08 | O Edital de outro `institution_scope` nunca aparece, nem por parâmetro de filtro com o seu id |
| CA-09 | O número de consultas é o mesmo com 1 e com 30 Editais publicados, e o mesmo nas duas visualizações (padrão `test_consultas_da_vitrine.py`) |
| CA-10 | Um Edital `CANCELADO` não aparece; um `ENCERRADO` só mostra Eventos concluídos |
| CA-11 | A grade de qualquer mês tem 4 a 6 semanas, começa no domingo, e a soma das contagens das células é igual ao número *Marcos no mês* da síntese (fevereiro de 2026, com 4 semanas exatas; agosto de 2026, com 6) |
| CA-12 | Um dia com 2 ou mais marcos tem o destaque; um dia com 1 não tem |
| CA-13 | A página passa nos guardiões de CSP, acessibilidade (incluindo o par de contraste do destaque), larguras e folha estática; não rola na horizontal a 375 px; o item da barra ⇔ 200 para todo papel (`test_shell_da_gestao.py`) |
| CA-14 | Validação humana: pelo menos uma pessoa que gere Processos responde às cinco perguntas da seção 6 do pedido usando só a página, em sessão observada, antes de a fase 1.1 começar |
| CA-15 | Nenhum texto da página chama de *prazo* um Evento do cronograma sem a qualificação *previsto*, e nenhum número soma previsto com efetivo (C.5) |

### C.5 Prazo previsto × prazo aberto por ato

O sistema tem duas coisas diferentes que a linguagem comum chama de prazo, e a página não pode
confundi-las.

| | **Previsto no cronograma** | **Aberto por ato** |
|---|---|---|
| O que é | a data que o Edital publicou para um Evento | a janela que começa quando um ato é publicado — hoje, a recursal |
| Fonte | `VersaoConsolidada.content["schedule"]` | a publicação do resultado + `appealWindow` do marco (`recursos/domain/janela.py`), por `portal/leitura.prazos_de_recurso` |
| Muda por | Retificação | publicação, ou republicação de ato diferente |
| Pode divergir do outro? | sim: o "Prazo de recurso" do cronograma é previsão; se o resultado sai atrasado, a janela real começa depois | — |
| No MVP | **sim**, e é tudo o que a página mostra | **não** |

**Regras para o MVP:**

- Todo item é qualificado como *previsto*.
  - O nome da página é *Agenda dos Editais*, e não *Prazos*.
  - A legenda diz *"data prevista no cronograma publicado"*.
  - O encerramento de período é *Encerra*, e nunca *Prazo final*.
- A legenda da página traz, fixa: *"Prazos contados a partir da publicação de um ato — como o de
  recurso — podem diferir das datas previstas. O prazo em curso está na publicação do ato."*

**Quando o efetivo entrar (fase 1.3):**

- **Lançamento próprio**, com rótulo *"Prazo de recurso aberto pela publicação de 10/11 — até
  20/11"* e marca visual distinta do previsto.
- **Contagem própria** na síntese (*"N prazos abertos por ato"*), nunca somada aos marcos.
- **Na grade, nunca na mesma contagem da célula**: um segundo indicador, ou só na agenda do dia.
  Isso se decide na própria 1.3.
- **Custo**: três consultas fixas a mais (`historico_publico_dos_editais`, duas; `conteudos_citados`,
  uma), todas já usadas pela vitrine.
- **Limitação a registrar**: `prazos_de_recurso` só devolve a janela **enquanto ela corre** (corte
  por `agora`). Meses passados não mostrariam janelas encerradas sem uma variante da função.
  Convocação fica fora: o prazo dela é por candidato, e não do certame.

---

## D. Proposta técnica

### D.1 O que se reaproveita, sem alteração

- **Fonte e régua**: `versoes_vigentes`, a régua de `fase_do_evento`, `calendario` e `periodo`, e
  `ZONA`.
- **Montagem**: o padrão `visao_geral.ler`.
- **Escopo**: o filtro de `institution_scope` na consulta.
- **Barra e acesso**: `navegacao.SECOES` e `_toda_identidade`.
- **Visual**: as classes de A.7.
- **Destinos dos links**: `interface:detalhe` e `portal:selecao`.
- **Grade do mês**: `calendar.Calendar(firstweekday=6)`, da biblioteca padrão, para as semanas.

### D.2 O que se acrescenta

| Peça | Onde | Natureza |
|---|---|---|
| `marcos_na_janela(conteudos, inicio, fim, agora)` → itens (Evento, Edital, lançamento *pontual/abre/encerra*, fase) e períodos que tocam a janela | `interface/agenda.py` no MVP. Desce para `editais/domain/` quando o `.ics` for o segundo leitor, como a `028` e a `047` fizeram | pura, sem banco |
| `semanas_do_mes(ano, mes, itens)` → semanas × dias, com contagem, até dois itens e marca de concentração | `interface/agenda.py` | pura, sem banco |
| `ler(ator, parametros, *, agora)` → `Leitura(visao, janela, itens, periodos, sintese, filtros, avisos)` | `interface/agenda.py` | consultas + derivação. Docstring *"Este módulo só lê"* |
| View `agenda` | `interface/views.py` | GET; `ator_da_sessao`; sem `Http404` (listagem) |
| Rota `path("agenda", …, name="agenda")` com `?visao=dias|mes` | `interface/urls.py` | uma rota, duas visualizações |
| `Secao("Agenda", "interface:agenda", TRABALHO, _toda_identidade, "i-calendario")` | `interface/navegacao.py`, mais o símbolo SVG em `base.html` | — |
| Template `interface/agenda.html` com os parciais `_agenda_dias.html` e `_agenda_mes.html` | — | blocos `titulo`, `estilo_da_pagina`, `caminho_do_contexto`, `conteudo` |
| Folha `interface/telas/agenda.css` | registrada em `QUEM_CARREGA`; par novo em `PARES` | promove `.filtros-da-visao` à folha comum, ou a repete |

**Não há endpoint de API, migration, modelo novo, dependência, cache, fila nem tarefa agendada.**

### D.3 Consulta e autorização

```text
1. Edital.objects.filter(institution_scope=ator.institution_scope,
                         status__in={PUBLICADO, ENCERRADO})
          .select_related("processo")                                   1 consulta
2. versoes_vigentes(edital_ids=…, at=agora)                             2 consultas
3. VersaoConsolidada.objects.filter(edital_id__in=…, valid_from__gt=agora)
          .values_list("edital_id", "valid_from")                       1 consulta  (aviso)
4. derivação em memória: marcos_na_janela(…), e semanas_do_mes(…) no mês   0
```

- **Quatro consultas, fixas, iguais nas duas visualizações.** O mês e os dias diferem só na janela
  aplicada **em memória**.
- **O intervalo não desce ao SQL**, porque os Eventos estão dentro do JSON. Filtrar no banco exigiria
  operadores de JSONB do PostgreSQL, o que quebraria o modo SQLite da suíte (CLAUDE.md, *As
  armadilhas caras*). A economia seria pequena: dezenas de Editais × até ~18 Eventos.
- **O corte relacional é pela situação do Edital, e não pelo ano.** Um período pode atravessar o
  ano, e o Edital de 2025 com resultado em 2026 tem de aparecer.
- **O que revisaria a decisão**, como a vitrine registrou na `024` (`D-003`), é uma de duas coisas:
  - o escopo passar de algumas centenas de Editais publicados não encerrados;
  - a medição de A.9 (item 6) mostrar o `content` inteiro pesando.

  A saída, nesse caso, é uma variante de `versoes_vigentes` que materialize só `content__schedule`
  (transformação de chave do `JSONField`, portátil) — e não uma tabela de projeção.
- **Autorização.** O predicado da barra e o da view são a mesma função (`FR-482`). O escopo vem da
  consulta. O filtro *Edital* só escolhe entre o que a consulta já trouxe, e um id estranho na
  query string simplesmente não casa.

### D.4 Cronogramas e Retificações

- A página lê **sempre** `versoes_vigentes(at=agora)`. Ela nunca compõe versões nem lê
  `AlteracaoNormativa`.
- **Atualização**: não há o que sincronizar. A versão é imutável e append-only, e uma Retificação
  nova materializa outra versão, que a próxima requisição lê. A de vigência futura passa a valer
  sozinha em `valid_from`, e até lá é só anunciada (consulta 3).
- **Fase 1.1**: a marca *"alterado pela Retificação nº X"*. Uma consulta a `ProvenienciaConteudo`,
  filtrada pelas versões vigentes e por `target_path` iniciado em `/schedule/`. O número de
  consultas continua fixo.

### D.5 Impacto nas estruturas existentes

- **Nenhum** em modelo, migration, permissão ou papel.
- Toca `navegacao.SECOES` (uma entrada), `base.html` (um símbolo SVG) e `urls.py` (uma rota).
- Talvez toque `gestao/*.css`, se `.filtros-da-visao` for promovida.
- Toca a lista `PARES` do teste de contraste.

### D.6 Estratégia de testes

| Nível | O que | Base |
|---|---|---|
| Unidade, sem banco | `marcos_na_janela`: pontual, período, mesmo dia, sem término, cancelado, período de inscrições sem término, fronteira 31/12 23:30, Edital parado por ato (CA-05, 06, 07, 10) | conteúdos sintéticos, como os testes de `supervisao` |
| Unidade, sem banco | `semanas_do_mes`: domingo primeiro, 4 e 6 semanas, fevereiro, dias fora do mês vazios, soma das células = síntese, destaque ≥ 2, corte em dois nomes (CA-11, 12) | idem |
| Integração | publicar → retificar data → as duas visualizações mostram a nova (CA-02); Evento acrescentado (CA-03); vigência futura antes e depois, com aviso (CA-04); rascunho com Eventos na janela ausente (CA-01) | `tests/fixtures/selecao.py` (`publicar_selecao`), helpers de Retificação; `transaction=True` só onde o gatilho importa |
| Autorização | outro escopo (CA-08); barra ⇔ 200 (CA-13) | `test_shell_da_gestao.py` cobre o segundo sem caso novo |
| Orçamento | 1 × 30 Editais, nas duas visualizações (CA-09) | `tests/portal/test_consultas_da_vitrine.py` |
| Interface | CSP, acessibilidade, contraste do destaque, larguras, folha estática, 375 px (CA-13) | guardiões existentes |
| Vocabulário | *previsto* em todo prazo do cronograma; nenhuma soma de previsto com efetivo (CA-15) | teste de substring nos templates, no estilo das varreduras existentes |
| Rastreabilidade | citações da spec nova | `test_citacoes_de_requisito.py` |

Tudo verificado com `make lint check test-pg`, como manda o CLAUDE.md.

---

## E. Plano incremental

| Fase | Conteúdo | Condição para começar |
|---|---|---|
| **1 — MVP** | Página com **Próximos dias** e **Mês** (C.1–C.5): mesma leitura, mesmos filtros, síntese por janela, aviso de Retificação a vigorar | `Q1` — decidida |
| **1.1** | Marca *"alterado pela Retificação nº X"* (D.4). `id="evento-<uuid>"` no `<li>` do `_cronograma.html` do portal, para o link cair no Evento e não só na seção, sem mudar a substring `class="marco …"` de que os testes da `010` dependem | `CA-14` cumprido |
| **1.2** | Filtro *"só Processos em que atuo"* por `comissoes_da_pessoa` (uma consulta) | uso real pedir |
| **1.3** | **Prazo aberto por ato** (recursal), com marca e contagem próprias (C.5) | a divergência previsto × efetivo aparecer na validação |
| **2 — calendários externos** | ver abaixo | MVP em uso |
| — | Visão entre unidades | `G-014`/`G-010`; fora nesta etapa por decisão do usuário |

### Fase 2 — calendários externos (avaliação, não implementar)

**Exportação estática × assinatura.**

- A **exportação** é um arquivo baixado uma vez, um retrato do instante. Ela não acompanha
  Retificação.
- A **assinatura** é uma URL que o cliente relê periodicamente, e acompanha. O intervalo de
  releitura é do cliente: o Google Agenda leva de horas a mais de um dia, e o sistema não o
  controla. Por isso a assinatura **nunca** substitui o cronograma oficial, e o texto do evento
  exportado tem de dizê-lo.

**O que simplifica tudo: o cronograma publicado é público.** Uma assinatura **por Edital** pode
morar no portal, em `/selecoes/<edital_id>/cronograma.ics`:

- sem autenticação, sem token e sem expiração;
- sem questão de privacidade, porque entrega exatamente o que `portal:selecao` já mostra a qualquer
  pessoa;
- um feed da unidade, com todas as seleções públicas, segue a mesma lógica;
- não há OAuth nem integração com Google ou Microsoft: o padrão é RFC 5545, e qualquer cliente
  assina por URL.

**Identidade e Retificação.**

- `UID`: o id do Evento — **estrutural**, que nunca muda entre versões e é único por geração —, mais
  um sufixo de domínio institucional.
- `SEQUENCE`: o `publication_order` da Publicação que originou a versão vigente, monotônico por
  Edital.
- `DTSTAMP`: o `materialized_at` da versão.
- **Período**: **um** `VEVENT`, com `DTSTART`/`DTEND`. Os marcos *Abre*/*Encerra* são forma de
  tela, e não dois eventos.
- **Pontual sem término**: só `DTSTART`.
- **Fuso**: instantes em UTC (`Z`), para dispensar `VTIMEZONE`.
- **Cancelamento**: o Evento ou o Edital cancelado sai com `STATUS:CANCELLED` e o mesmo `UID`,
  **e continua no feed**. Sumir com o evento deixa cópia órfã em alguns clientes.
- `URL`: `portal:selecao`.
- **Só o previsto.** O prazo aberto por ato não entra no feed, ou entra como evento separado,
  rotulado como tal (C.5).

**Exportação filtrada da gestão** (`/gestao/agenda.ics?<filtros>`):

- usa a mesma projeção e a mesma autorização da página;
- é só estática, um download com a sessão.

**Assinatura de dado da gestão não é recomendada.**

- Ela não funciona com sessão, porque o cliente de calendário não leva cookie.
- Exigiria um token por pessoa, guardado com hash, revogável, com expiração, com escopo fixo na
  emissão e com auditoria. Isso é modelo e migration novos, contra a restrição deste estudo.
- Enquanto a página mostrar só dado público, o feed do portal atende.

**Rascunhos num `.ics`: nunca.**

**Implementação sem dependência.**

- O formato é texto: dobra de linha em 75 octetos, escape de `\`, `;`, `,` e quebra de linha, e
  CRLF.
- Basta uma função de ~60 linhas, com testes de forma.
- A régua `marcos_na_janela`, já no domínio a essa altura, alimenta a página e o arquivo.

### Dependências e riscos do plano

- **`Q1` está decidida**, e o MVP não tem bloqueio de decisão. `Q2` e `Q3` têm recomendação
  aplicada na spec, e podem ser revistas sem retrabalho.
- **`CA-14` bloqueia as fases seguintes**, e não o MVP.
- **O risco técnico é baixo.** A régua é antiga e testada, o carregador em lote é usado pela Visão
  Geral, e o padrão de tela existe. O único custo não medido é o do `content` inteiro (A.9, item 6),
  medido na própria implementação, como a `100` fez em `R-006`.
- **O risco de escopo** é a pressão por categoria, modalidade, unidade e barras de período. A spec
  registra a recusa de cada uma, com a razão, como a `040` fez em `G-014`.

---

## G. Impacto incremental de incluir o mês no MVP

**O que o mês acrescenta à agenda sozinha:**

| Dimensão | Acréscimo |
|---|---|
| Consultas | **nenhuma**: mesma `ler`, janela aplicada em memória |
| Modelo, migration, dependência, permissão | **nenhum** |
| Domínio | `semanas_do_mes`, função pura de ~40 linhas sobre `calendar.Calendar` |
| Interface | um parcial de template (~60 linhas); ~80 linhas de folha (grade, célula, destaque, hoje, faixa estreita); um par de contraste; as abas |
| Leitura | `ler` aceita `visao` e `mes`; a síntese passa a ser calculada **por janela** |
| Testes | ~8 casos unitários de grade (CA-11, 12); render das duas visualizações nos testes de integração existentes; CA-09 em dobro; guardiões automáticos |
| Esforço | **~40% sobre a agenda sozinha**, estimado pela contagem de peças: das sete peças de D.2, o mês acrescenta uma e alarga outras três |

**O que o mês exige de decisão de desenho**, já tomada nesta revisão:

- domingo primeiro;
- dias de fora vazios;
- até dois nomes, só em tela larga;
- destaque a partir de dois marcos;
- períodos listados, e não desenhados.

**O que o mês acrescenta de risco:**

- **Legibilidade da célula**: resolvida pela contagem e pelo corte em dois nomes, e verificável
  com um mês de carga realista na validação (`CA-14`).
- **Leitura da grade como carga de trabalho**: resolvida por legenda e vocabulário (C.5,
  Avaliação 7).
- **Acessibilidade de tabela**: os guardiões cobrem o mecânico; o restante é `caption`, `th scope`,
  `aria-current="date"` e nenhuma informação só por cor.

**O que o mês não faz, de propósito:** barras de período, arrastar, criar compromisso, visão
semanal em colunas e prazo efetivo.

## F. Decisão recomendada

**Implementar com ajustes, com a agenda e o mês no MVP.**

**Por que o mês entra agora**

- O objetivo declarado é a visão consolidada do mês, e a agenda sozinha não a dá.
- O acréscimo não toca banco, modelo nem autorização.
- A grade é derivação pura sobre a mesma lista de itens, e por isso não tem como discordar da
  agenda.

**Por que não *como proposta original***

- Três dos seis filtros não têm dado.
- A visão entre unidades ficou fora por decisão do usuário.
- A grade não desenha períodos como barras: eles são intervalos listados, com abertura e
  encerramento marcados.
- O prazo aberto por ato é outra fonte, e entra depois, separado.

**Os ajustes, em uma linha cada:**

1. Duas visualizações, uma leitura e os mesmos filtros; a agenda é a padrão.
2. Só o vigente publicado, com aviso da Retificação a vigorar.
3. Escopo do ator, e acesso de toda identidade da gestão.
4. Filtros de janela, Edital e espécie estrutural.
5. Síntese por janela, com a concentração.
6. Só o previsto, sempre qualificado como tal.
7. `.ics` e visão entre unidades depois, cada um com a sua condição.

### Decisões

- **`Q1` — decidida em 29/10.** Toda identidade da gestão, condicionada a cronogramas publicados e
  vigentes, ao escopo da unidade e às permissões existentes, sem visão entre unidades.
- **`Q2`** — O Evento cancelado na janela: mostrar com *Cancelado* na agenda e fora da grade
  (aplicado na spec; é o que o portal faz), ou omitir (o que a supervisão faz).
- **`Q3`** — O nome na barra: *Agenda* (aplicado na spec) ou *Calendário*. Com a grade no MVP, os
  dois descrevem a página. *Agenda* foi mantido porque a visualização padrão é a lista.
- **`Q4`** — A visão entre unidades (`G-014`) continua fora nesta etapa, por `Q1`. Quando voltar, é
  feature própria, com o papel decidido em `G-010`.
