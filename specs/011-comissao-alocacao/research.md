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

**O fato**: `replace_draft` executa `EtapaAvaliacao.objects.filter(edital=edital).delete()` seguido
de `bulk_create` (`editais/application/draft.py:250`). A identidade é preservada — os `id` vêm do
payload e o snapshot os publica como estão (`publicacoes/application/publish_edital.py:41`) —, mas a
linha não.

**Alternativas descartadas**:

| Alternativa | Por que não |
|---|---|
| `ForeignKey(EtapaAvaliacao, on_delete=CASCADE)` | Gravar o rascunho apagaria alocações em silêncio. |
| `ForeignKey(..., on_delete=PROTECT)` | Gravar o rascunho passaria a falhar: regressão da 006, proibida pela seção 45 da spec. |
| Copiar nome e dados da Etapa para a alocação | Segunda fonte do conteúdo normativo; contraria D-005 e a exigência constitucional de fonte autoritativa única. |
| Sincronizador que reconcilia alocações após cada gravação | Máquina de estados inventada para um problema que a leitura derivada resolve. |

**Decisão**: a alocação designa a Etapa pela identidade estável, e a spec fixa o invariante em vez do
mecanismo — gravar o rascunho nunca apaga alocação nem falha por causa dela, e alocação nunca concede
acesso a Etapa ausente da versão vigente.

**Sobre a integridade referencial**: a Constituição exige que "relacionamentos DEVEM preservar
integridade referencial" (`.specify/memory/constitution.md:50`). Ela é preservada — no command, que
verifica existência e pertinência a cada operação e a cada acesso. O precedente é explícito: a 009
adotou `Inscricao.profile_id` como `UUIDField` e documentou o motivo — amarrar à linha de elaboração
faria o vínculo depender de um registro que a Retificação altera depois (`inscricoes/models.py:9`).

**Consequência**: a alocação órfã existe e é legítima. A Retificação endereça `/stages` por `id`
(`publicacoes/domain/colecoes.py:22`), portanto pode remover a Etapa do conteúdo publicado. A
condição é derivada na leitura, comparando a alocação com a versão vigente; não é campo.

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
`avaliadores_exigidos` na Etapa (FR-043). Acrescentar esse campo seria mudar conteúdo normativo
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

## O que esta pesquisa não decidiu

- A forma física de `MembroComissao` e `AlocacaoEtapa` — colunas, chaves, constraints.
- Como o registrador de auditoria é adaptado (D-008).
- Se a inativação é campo booleano, data ou linha histórica; a spec exige apenas que a auditoria
  sobreviva à remoção.
- Onde `Minhas Etapas` mora na navegação.

Todas são decisões do `/plan`, e nenhuma delas pode violar os invariantes de D-002, D-004, D-005 e
D-007.
