# Fase 0 — Pesquisa e decisões: Gestão da Comissão e Alocação por Etapa

**Feature**: [spec.md](./spec.md) | **Data**: 2026-09-01

Cada decisão abaixo foi tomada contra o repositório e contra a Constituição, não contra o hábito.
Onde uma alternativa razoável foi descartada, o motivo está escrito — é o que impede que ela volte
pela porta dos fundos na implementação.

## O ponto de partida — cinco premissas que a primeira redação dava por certas

A spec foi escrita descrevendo a jornada, e cinco de suas premissas são falsas neste sistema. Elas
governam as sete decisões:

1. **A Etapa não pertence ao Processo.** `EtapaAvaliacao.edital` é chave estrangeira para `Edital`
   (`editais/models/etapas.py:23`), e `Edital.processo` tem `related_name="editais"`
   (`processos/models.py:45`): um Processo tem N Editais, e a Etapa é neta do Processo.
2. **A coleção de Etapas é apagada e recriada a cada gravação do rascunho**
   (`editais/application/draft.py:250`), preservando os identificadores recebidos.
3. **Não existe diretório institucional, nem pessoa no domínio.** A identidade é um identificador
   textual escolhido num seletor de sessão que só existe fora de produção
   (`interface/identidade.py`), e os papéis vêm de um dicionário fixo
   (`interface/identidade.py:20`). Não há nome, e-mail, lotação nem estado de conta em lugar nenhum.
4. **Não existe "responsável pelo Processo" no código** — `ProcessoSeletivo` tem `created_by` e nada
   mais — **mas existe na Constituição** (`.specify/memory/constitution.md:92-93`). Ler só o código
   levou a primeira redação desta reconciliação ao erro registrado em D-007.
5. **Não existe representação normativa da comissão.** O catálogo de seções do Edital não a contém
   (`editais/domain/secoes.py:49`).

## D-001 — Onde vive a Etapa

**Decisão**: a comissão é do Processo; a alocação é para Etapa de Edital do Processo; a coerência é
verificada percorrendo `etapa → edital → processo`.

**Por quê**: manter a comissão no Edital obrigaria a refazê-la a cada Edital novo do mesmo Processo,
e a comissão institucional não se refaz porque um segundo Edital foi aberto. Mover a Etapa para o
Processo alteraria conteúdo normativo publicável para atender necessidade operacional, o que D-005
proíbe.

**Consequência de interface**: dois Editais do mesmo Processo podem ter Etapas homônimas — a
unicidade é `(edital, order)` e não há unicidade de nome. Por isso a visão administrativa é
organizada por Edital antes de por Etapa, e `Minhas Etapas` sempre nomeia o Edital.

## D-002 — Por que a alocação não pode depender da linha da Etapa

**O fato que decide**: a linha de elaboração e a Etapa publicada não são a mesma coisa, e podem nem
existir juntas. `EtapaAvaliacao` é lida uma única vez fora da elaboração — para montar o snapshot no
momento da publicação (`publicacoes/application/publish_edital.py:41`). Depois disso, o conteúdo
vigente evolui por Retificação, que opera sobre a Versão Consolidada e **não escreve de volta** nas
tabelas de `editais`. E a Retificação sabe acrescentar item a coleção com chave: `/stages` está entre
as coleções endereçáveis por `id` (`publicacoes/domain/colecoes.py:22`) e a aplicação de uma
Alteração admite acréscimo (`publicacoes/domain/changes.py:325`).

Logo, uma Retificação pode criar Etapa que existe no Edital vigente e não tem linha em
`EtapaAvaliacao`. Essa Etapa é tão real quanto as outras — o trabalho dela precisa ser distribuído —
e nenhuma chave estrangeira para a linha de elaboração conseguiria designá-la.

**O fato correlato**, que sustenta a regra de "só alocar depois de publicado" (D-002 na spec):
`replace_draft` apaga e recria toda a coleção de Etapas do Edital a cada gravação do rascunho
(`editais/application/draft.py:250`). Alocar durante a elaboração seria alocar contra uma coleção
que o elaborador refaz a cada salvamento.

**Alternativas descartadas**:

| Alternativa | Por que não |
|---|---|
| `ForeignKey(EtapaAvaliacao, ...)` | Não consegue designar Etapa criada por Retificação, que não tem linha. E, em qualquer `on_delete`, acopla autorização operacional à tabela de elaboração. |
| Criar linha de elaboração para a Etapa que a Retificação acrescentou | A 011 passaria a escrever em `editais_etapaavaliacao`, o que D-005 e FR-083 proíbem. |
| Copiar nome e dados da Etapa para a alocação | Segunda fonte do conteúdo normativo; contraria D-005 e a exigência constitucional de fonte autoritativa única. |
| Sincronizador que reconcilia alocações a cada publicação ou Retificação | Máquina de estados inventada para um problema que a leitura derivada resolve. |

**Decisão**: a alocação designa a Etapa pela identidade que o conteúdo publicado carrega, e a spec
fixa o invariante em vez do mecanismo — alocação nunca concede acesso a Etapa ausente da Versão
Consolidada vigente, e nada que a 011 grave pode impedir a elaboração ou a Retificação de um
Edital.

**Sobre a integridade referencial**: a Constituição exige que "relacionamentos DEVEM preservar
integridade referencial" (`.specify/memory/constitution.md:50`). Ela é preservada — no command, que
verifica existência e pertinência a cada operação e a cada acesso. O precedente é explícito: a 009
adotou `Inscricao.profile_id` como `UUIDField` e documentou o motivo — amarrar à linha de elaboração
faria o vínculo depender de um registro que a Retificação altera depois (`inscricoes/models.py:9`).

**Consequência**: a alocação órfã existe e é legítima. Assim como acrescenta, a Retificação pode
remover a Etapa do conteúdo publicado, e a alocação passa a designar identidade ausente. A condição é
derivada na leitura, comparando a alocação com a Versão Consolidada vigente; não é campo. Alterar
nome, peso ou nota mínima preservando o `id` não produz órfã — o que a torna órfã é a identidade sair
do conteúdo vigente, e não o conteúdo da Etapa mudar.

## D-003 — O que existe de identidade, e o que não existe

**O fato**: `interface/identidade.py` é a fronteira inteira. O identificador vem da sessão; as
permissões, de um dicionário fixo; e o adaptador de API aceita `subject|scope|perm,perm`
(`seguranca/api/authentication.py`). Não há atributo de pessoa em nenhum lugar do domínio.

**Alternativas descartadas**:

- **Cadastrar a pessoa na 011** (nome, e-mail, lotação). Criaria o cadastro paralelo que a própria
  spec proíbe, e a 008 já havia recusado pessoas no domínio ao materializar o Edital.
- **Simular busca com os identificadores já vistos.** Produziria uma lista que parece diretório e não
  é: quem nunca acessou o sistema não apareceria, e o gestor concluiria que a pessoa não existe.

**Decisão**: o identificador informado é a chave; o rótulo de exibição é opcional e declaradamente
não-autoritativo; não há busca nem desambiguação de homônimos enquanto não houver diretório. O gate
de PC-005 é a condição de produção, e é onde essa dívida está registrada.

**Consequência para EC-013**: sem diretório, o sistema não pode afirmar que uma pessoa não existe.
Pode validar formato, gravar, comparar exatamente com a identidade autenticada e avisar que não
verifica. "Identificador inexistente" não é caso que o sistema saiba reconhecer; "identificador que
nunca autentica" é.

## D-004 — Como o escopo isola, sem virar coluna em toda tabela

**O fato**: `require_permission` responde escopo divergente com `not_found`, e não com `forbidden`
(`seguranca/application/authorization.py:8`). E a unicidade da `Inscricao` é
`(identity_subject, edital, profile_id)` (`inscricoes/models.py:74`) — sem repetir
`institution_scope`, porque o contêiner já o carrega.

**Alternativa descartada**: copiar `institution_scope` para `MembroComissao` e `AlocacaoEtapa` por
simetria com os agregados de topo. É prescrição de persistência numa spec funcional, e a `Inscricao`
mostra que o projeto não faz isso quando há contêiner.

**Decisão**: o invariante é o isolamento — toda consulta e alteração limitadas pelo escopo do
Processo, escopo divergente respondendo como recurso inexistente, vínculos independentes entre
escopos. A chave física fica com o `/plan`.

## D-005 — Onde a comissão não entra

**O fato**: o catálogo de seções do Edital vai de `apresentacao` a `disposicoes-finais` e não contém
comissão (`editais/domain/secoes.py:49`); a seção `etapas` é gerada a partir de `stages`
(`editais/domain/secoes.py:112`).

**Decisão**: `MembroComissao` é a única representação de comissão do sistema, e é operacional. Nada
da 011 entra no conteúdo publicado, na Versão Consolidada, no hash ou no documento; nenhuma migration
da 011 altera `editais_etapaavaliacao` nem tabelas de `publicacoes`.

Isto é a P-001 da 008 reafirmada. A tentação concreta que ela bloqueia tem nome:
`avaliadores_exigidos` na Etapa (FR-042). Acrescentar esse campo seria mudar conteúdo normativo
publicável por necessidade operacional.

**Nota de infraestrutura**: as tabelas de publicação e a trilha de auditoria são append-only também
por privilégio de banco — o papel de runtime não tem `UPDATE` nem `DELETE` sobre elas
(`seguranca/papeis.py`). Uma escrita da 011 ali falharia em produção mesmo que passasse na revisão.

## D-006 — Duas portas, e por que nomeá-las

`Minhas Etapas` derivada de alocação e visão administrativa derivada de permissão de gestão são
capacidades independentes, e nenhuma das duas cria papel ou grupo novo: a permissão de gerir comissão
é nomeada e entra no papel responsável, como as demais.

**Por que a spec precisa dizer isso**: sem a separação, "todos e somente os objetos alocados" seria
indemonstrável — a exceção administrativa engoliria a regra, e a demonstração de segurança da seção
49 perderia o sentido. Com ela, o presidente que não está alocado não vê a Etapa em `Minhas Etapas`,
e continua vendo tudo na tela de gestão.

## D-007 — A presidência, e o erro que a originou

**O erro**: a primeira versão desta reconciliação leu o código, não encontrou "responsável pelo
Processo" e concluiu que a autoridade não existia — decidindo que o presidente seria opcional. A
autoridade existe, e está onde deveria estar: a Constituição afirma que "o Presidente da Comissão é
inicialmente responsável pela gestão operacional" (`.specify/memory/constitution.md:92-93`) e lista
`Comissão` e `Presidente da Comissão` entre os conceitos que devem ser distintos
(`.specify/memory/constitution.md:45`).

**Alternativas consideradas**:

| Alternativa | Avaliação |
|---|---|
| Presidente opcional; gestor administra | **Descartada.** Não resolve a responsabilidade constitucional: muda a regra sem alterá-la. |
| Presidente obrigatório desde o primeiro membro | Descartada. Obriga o primeiro membro adicionado a ser presidente, ou exige criar a comissão em dois passos. Regra de tela virando regra de domínio. |
| Alterar a Constituição antes da spec | Legítima, mas desproporcional: nada nesta feature justifica mexer no artigo. |
| **Presidente exigido para alocar** | **Adotada.** Uma validação, nenhum lifecycle. |

**Decisão**: constituir sem presidente é estado transitório válido; alocar exige presidente ativo; e
o último presidente não pode ser removido ou rebaixado enquanto houver alocação ativa.

**O que fica de fora, deliberadamente**: mandato, posse, sucessão automática, substituto, delegação e
qualquer estado de presidência. A Constituição pede responsabilidade, não workflow.

## D-008 — A trilha de auditoria, sem inventar ciclo de vida

**O fato**: `record_event` lê `aggregate.status` e `aggregate.revision`
(`auditoria/application.py:26`). E a consulta por conjunto de agregados já existe: `trilha_do_edital`
reúne o Edital e suas Retificações numa linha do tempo só (`auditoria/selectors.py:64`).

**A tensão**: a 009 resolveu isso adotando `status` e `revision` na `Inscricao`, e documentou a
escolha — dois campos para reusar dois mecanismos (`inscricoes/models.py:3`). É precedente válido.
Mas "membro da comissão" não tem ciclo de vida próprio: tem `ativo`, e um estado inventado para
agradar a assinatura de uma função seria domínio determinado pela persistência, o que a Constituição
proíbe.

**Decisão**: a spec declara as perguntas que a trilha precisa responder e a proibição — não inventar
estado ou revisão só para satisfazer o registrador. Qual das duas adaptações é menor é medição do
`/plan`, e ambas são aceitáveis. O que não é aceitável é registro paralelo.

## D-009 — Colisão de vocabulário na URL

`editais/<uuid:edital_id>/compor/<slug:etapa>` já existe e significa **passo do compositor**, não
Etapa de Avaliação (`interface/urls.py:20`). A Constituição exige significado inequívoco do termo
entre spec, código, URL e interface. O `/plan` não deve pendurar rota de Etapa de Avaliação nesse
espaço sem desambiguar o termo.

# Decisões de implementação

*Fase 0 do `/plan`. As nove decisões acima reconciliaram a spec com o domínio; as nove abaixo
escolhem como ela é construída, e cada uma foi verificada contra o código que vai receber a
mudança.*

## D-010 — Onde o código vive

**Decisão**: um app novo, `comissoes`, com domínio, persistência e comandos. As telas ficam em
`interface`, onde o Processo já é administrado.

**Por quê**: `processos` guarda o ciclo de vida normativo — Processo, Edital, Ato Administrativo — e
a comissão é autorização operacional sobre esses objetos. Misturar as duas coisas faria o agregado
normativo carregar `related_name` de autorização, e a 012 herdaria essa confusão ao acrescentar
`Avaliacao`.

**Alternativa descartada**: um app novo também para o canal, como a 009 fez com `portal`. Aqui não
há ator novo nem canal novo: quem gere a comissão e quem recebe alocação são atores institucionais,
autenticados pelo mesmo mecanismo, na mesma base visual. O que a 009 separou foi um *canal*, não uma
*feature*.

## D-011 — A capacidade sistêmica e a base contextual

**Decisão**: uma permissão nomeada nova, `comissao:gerir`, acrescentada ao papel `gestor`
(`interface/identidade.py:20`). A presidência **não** entra em `PAPEIS`: é verificada contra o
vínculo, por uma função de domínio única.

```text
pode_gerir_comissao(ator, processo) =
    ator.can("comissao:gerir")                       # base sistêmica
    or membro_ativo(ator.subject, processo).e_presidente()   # base contextual
```

**Por quê**: `require_permission` responde a permissão de conjunto fixo e não sabe olhar objeto. A
autorização contextual precisa de uma segunda função — e uma só, chamada por todo comando e por toda
view, para que a regra não se duplique em oito lugares.

**Alternativa descartada**: acrescentar `comissao:presidir` a `PAPEIS`. Faria da presidência um papel
global — a pessoa presidiria todas as comissões —, que é exatamente o que P-003 e o SC-011 proíbem.

## D-012 — O resolvedor de Etapas, e a fonte única

**Decisão**: uma função só, `etapas_vigentes(edital)`, que lê `effective_version(edital_id=...)`
(`publicacoes/application/selectors.py:26`) e devolve as Etapas de `content["stages"]` indexadas por
`id`. Criação de alocação, listagem administrativa, `Minhas Etapas` e o guard de acesso chamam essa
função e mais nenhuma.

**Por quê**: é o que torna o SC-021 verdadeiro por construção — uma Etapa alocável é exatamente uma
Etapa que aparecerá para quem foi alocado, porque as duas perguntas passam pelo mesmo código. E é o
que impede o desvio natural do `/plan`: consultar `edital.etapas.all()`, que é a coleção de
elaboração e responderia diferente depois de uma Retificação (D-002).

**Consequência conhecida**: `effective_version` levanta `no_effective_version` com 404 quando o
Edital nunca foi publicado. É esse erro que sustenta FR-032 e EC-014 — não é preciso consultar
`Edital.status` para saber que não há o que alocar, embora a tela o consulte para explicar por quê.

## D-013 — Remover é inativar, e a unicidade é parcial

**Decisão**: `ativo` booleano nos dois modelos; remover grava `ativo=False`, `inativado_em` e
`inativado_por`; readicionar cria linha nova. A unicidade é `UniqueConstraint` **parcial**, com
`condition=Q(ativo=True)`.

**Por quê**: a Constituição proíbe excluir fisicamente registro cuja remoção comprometa
rastreabilidade, e a trilha de auditoria referencia o agregado pelo `id` — apagar a linha deixaria o
evento apontando para o nada. A constraint parcial é o que faz EC-001 e EC-002 serem recusados pelo
banco, e não por conferência em código sujeita a corrida.

**Verificado**: `UniqueConstraint(condition=...)` funciona em PostgreSQL e em SQLite; a suíte roda
nos dois, e só exercita as constraints parciais com `TEST_DB_ENGINE=postgresql`.

**Alternativa descartada**: máquina de estados com `status`. Membro de comissão não tem ciclo de
vida — tem presença. Inventar estados só para reusar a assinatura do registrador de auditoria é o
que D-008 proíbe.

## D-014 — A adaptação mínima do registrador

**Decisão**: `record_event` ganha `new_state` e `new_revision` com **sentinela `_UNSET`**, e não
`None` como padrão. Ausente o argumento, o valor continua vindo de `aggregate.status` e
`aggregate.revision` (`auditoria/application.py:26`); presente, é usado como veio — inclusive
`None`. Nenhum campo novo em tabela nenhuma, nenhuma mudança em quem já chama.

`None` como padrão não serve: ele é valor legítimo — `new_revision` é coluna anulável — e usá-lo
também como marcador de "leia do agregado" faria o registrador tentar `aggregate.revision` num
`MembroComissao`, que não tem o atributo. O defeito só apareceria no dia em que alguém quisesse
gravar revisão nula de propósito, e apareceria como `AttributeError` em produção.

**Por quê**: é a menor adaptação que atende D-008. A alternativa — dar `status` e `revision` a
`MembroComissao` — foi o que a 009 fez na `Inscricao`, e lá havia dois estados reais; aqui não há.

**O que a trilha registra**: no campo `permission`, a **base efetivamente usada** — `comissao:gerir`
quando a autorização veio da permissão sistêmica, `comissao:presidir` quando veio do vínculo
(FR-016). Só a primeira existe em `PAPEIS`; a segunda é rótulo de trilha, e acrescentá-la a um papel
seria desfazer D-011.

**O que a trilha responde** (FR-074): o Processo sai de `MembroComissao.processo_id`; a pessoa
afetada, do `subject` do membro, gravado em `reason` de forma legível; a Etapa afetada, do
`etapa_id` da alocação. A consulta "o que mudou na comissão deste Processo" reúne os agregados da
comissão pelo mesmo caminho de `trilha_do_edital` (`auditoria/selectors.py:64`), que já consulta por
conjunto de identificadores.

## D-015 — Rotas, e o vocabulário que já estava ocupado

**Decisão**:

```text
/gestao/processos/<uuid:processo_id>/comissao            # composição
/gestao/processos/<uuid:processo_id>/alocacoes           # organização por Edital e Etapa
/gestao/minhas-etapas                                    # área pessoal
/gestao/minhas-etapas/<uuid:edital_id>/<uuid:etapa_id>   # a atribuição
```

**Por quê**: `editais/<uuid>/compor/<slug:etapa>` já significa *passo do compositor*
(`interface/urls.py:20`), e D-009 registrou a colisão. Nenhuma rota nova usa `etapas/` como segmento
solto: a administrativa fala de `alocacoes`, a pessoal de `minhas-etapas`.

**Consequência**: a URL de uma atribuição carrega Edital e Etapa, e nenhum identificador de pessoa —
o checklist exige identificador sensível fora da URL, e o ator já vem da sessão.

## D-016 — Concorrência

**Decisão, em três partes**:

1. **Todo comando mutável bloqueia o Processo** com `select_for_update`, logo ao abrir o
   `command_context()` (`shared/application/commands.py:8`), **reavalia a base de autorização
   dentro da transação** — depois do bloqueio, nunca antes — e só então chama
   `ensure_processo_accepts_changes` (`processos/domain/finalizacao.py:70`), como todo comando
   mutável do projeto já faz.
2. As constraints parciais de D-013 respondem por duplicidade, e `reserve()`
   (`shared/idempotency.py:6`) por reenvio do mesmo formulário — nos **cinco** comandos, e não só
   na inclusão de membro.
3. **Remover membro inativa as alocações dele na mesma transação**, e não em duas operações, com
   **um evento de auditoria por alocação inativada**.

**A ordem entre autorização e idempotência é deliberada, e inverte a de `processos/commands.py`.**
Lá, `reserve()` é a primeira coisa dentro da transação, e a repetição devolve o resultado memorizado
sem reexecutar nada — o que é seguro porque `require_permission` já correu antes, fora dela. Aqui a
base pode ser contextual e só é confiável depois do bloqueio: reservar primeiro faria a repetição
devolver o resultado a quem perdeu a presidência nesse meio-tempo. Por isso a ordem é bloquear,
autorizar, conferir o estado do Processo e **depois** reservar.

**Por que a cascata gera um evento por alocação**: a trilha responde por agregado, e `FR-074` exige
saber qual Etapa foi afetada. Um único evento de remoção de membro não nomeia N Etapas de forma
consultável — quem investiga "quem perdeu acesso à Etapa X, e quando" não encontraria a resposta.
São N+1 eventos, com a mesma operação `ALOCACAO_REMOVER` que a remoção avulsa usa, e o `reason`
dizendo que a causa foi a saída do membro.

**Por que reavaliar a autorização depois do bloqueio**: a base contextual é um dado mutável desta
mesma feature. Entre a verificação na view e a gravação, outro gestor pode ter rebaixado o
presidente — e ele executaria a alteração com uma autorização que já não existe. Verificar antes do
bloqueio é verificar um estado que a transação seguinte pode desmentir. A permissão sistêmica não
tem esse problema; a presidência tem, e a regra vale para as duas porque uma função só responde
pelas duas (D-011).

**Por que a inativação em cascata**: alocação ativa sob membro inativo é relação contraditória —
`FR-025` e `EC-003` exigem que os acessos derivados do vínculo sejam revogados de forma consistente,
e uma alocação órfã de membro atrapalharia a própria regra do último presidente, que lê "há alocação
ativa nesta comissão". Fazer isso fora da transação deixa uma janela em que o acesso sobrevive à
remoção.

**Por que o bloqueio no Processo, e não nas linhas**: o invariante de presidência lê membros e
alocações antes de decidir, e não há linha única a bloquear. O Processo é o contêiner de tudo que
a feature escreve, e é a menor granularidade que fecha a leitura inteira. A escala da feature é de
ata: dezenas de membros, alterações esporádicas — nenhuma contenção real.

**Não usado**: `compare_and_swap`. Ele existe para agregado com `revision`, e D-013 decidiu não dar
revisão a estes modelos.

## D-017 — Como a recusa se apresenta

**Decisão**: `Http404` nas views, `DomainError("not_found", ..., 404)` nos comandos — os dois
padrões que o `interface` e o `application` já usam (`interface/views.py:1456`,
`seguranca/application/authorization.py:8`). Escopo divergente, Processo alheio, Etapa não alocada e
Etapa de outro Processo produzem **a mesma** resposta.

**Por quê**: FR-057 pede que a existência não seja enumerável, e responder 403 em um caso e 404 em
outro já é enumerar.

## D-018 — A trilha da comissão precisa de tela

**O fato**: a trilha de auditoria só é navegável por Edital hoje — `trilha_do_edital`
(`auditoria/selectors.py:64`), servida por `editais/<uuid>/auditoria`
(`interface/urls.py:29`). Os eventos desta feature têm por agregado `MembroComissao` e
`AlocacaoEtapa`, que não aparecem em tela nenhuma.

**Por que isso é bloqueio, e não detalhe**: o princípio VI da Constituição diz que capacidade que
nenhuma interface alcança não está entregue, e `SC-013` exige demonstrar que as alterações ficam
registradas. Sem superfície, a auditoria da 011 seria verificável só por consulta ao banco — que é
exatamente o que o princípio recusa.

**Decisão**: um seletor `trilha_da_comissao(processo)`, que reúne os identificadores dos membros do
Processo e de suas alocações e chama o `consultar` existente por conjunto de agregados — o mesmo
caminho de `trilha_do_edital`, sem consulta nova. E uma rota,
`/gestao/processos/<uuid:processo_id>/auditoria`, sob `auditoria:consultar`, reusando o template
`interface/auditoria.html` e acrescentando as cinco operações novas ao dicionário `OPERACOES` que
ele já usa para traduzir nomes de operação.

**Alternativa descartada**: demonstrar pela API de auditoria. Ela existe, mas o canal do auditor
neste produto é a interface — é onde a trilha do Edital já mora, e ter a do Processo em outro canal
faria a mesma pessoa trocar de ferramenta no meio da mesma investigação.

## O que esta pesquisa não decidiu

- A forma dos fragmentos htmx das telas — quais trechos recarregam e quais recarregam a página.
- O texto exato de cada recusa. As três de governança precisam nomear o caminho, e isso é redação
  de produto, decidida com a tela na frente.
- Se a remoção de alocação órfã é ação por linha ou em lote; depende de quantas aparecem juntas na
  prática, e uma por linha é o começo seguro.
- Os rótulos das cinco operações novas na tela de auditoria.

Nenhuma dessas escolhas pode violar os invariantes de D-002, D-004, D-005, D-007 e D-016.
