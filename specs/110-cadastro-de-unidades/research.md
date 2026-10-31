# Research: Cadastro de unidades administrado pela aplicação (110)

As decisões técnicas desta feature, cada uma com a alternativa descartada e o custo. A análise que as
motivou está na [revisão arquitetural de 30/10](../../doc/revisao-arquitetural-multiunidade-2026-10-30.md);
o que aqui se decide é como cumprir as oito decisões de produto do pedido de 31/10.

Caminhos sem prefixo são relativos a `backend/processo_seletivo/`. "*(109)*" e "*(108)*" marcam o que
veio dos PRs #349 e #348, integrados à `main` em 31/10/2026 (`81ce6e94` e `cf048007`).

**Revisão final de 31/10/2026**, antes da implementação, sobre a `main` com as duas integradas: a
D-002 (o papel), a D-003 (o nome do comando) e a D-017 (antes do SSO) foram revistas, e entraram a
D-018 (a entrada de homologação) e a D-019 (a ordem dos incrementos). Cada uma diz o que mudou.
Depois, o usuário aprovou a direção e pediu que a estratégia de homologação fosse comparada de novo:
a D-017 e a D-018 foram reescritas, e o código assinado saiu.

## D-001 — O banco é a fonte; o arquivo só semeia um registro vazio

**Decisão.** O registro de Unidades no banco é a única fonte que se escreve depois da instalação. O
`unidades.json` passa a ser **semente**: o comando o aplica só quando a tabela de Unidades está
vazia. Com qualquer unidade registrada, não lê o arquivo, não grava nada e diz que a semente não se
aplica.

**Por quê "só vazio", e não "só os códigos ausentes".** A revisão de 30/10 propôs inserir por código
ausente. Isso mantém o arquivo como **segundo caminho de criação**: quem acrescentasse uma entrada ao
JSON faria uma unidade nascer no deploy seguinte, com o autor `implantacao`, por fora da permissão e
do motivo que esta feature exige. O pedido de 31/10 diz "sem autoridade para alterar registros
existentes" e "não manter dois mecanismos concorrentes": "só vazio" cumpre os dois, e o primeiro
preparo de um banco novo continua idêntico ao de hoje.

**Descartado.**
- *Manter a sincronização completa ao lado da tela*: duas fontes; a tela seria desfeita no deploy.
- *Sincronização que só avisa a divergência*: devolve ao arquivo o papel de referência — alguém
  "corrigiria" o banco para ficar igual ao arquivo.
- *Apagar o arquivo*: o primeiro preparo de desenvolvimento, de teste e de homologação pediria um
  passo manual a mais, e o `seed_demo` perderia o Cefor. A semente custa um arquivo de seis linhas.

## D-002 — `unidade:administrar` no papel institucional que já existe, renomeado Administrador institucional

*Decidida pelo usuário em 31/10/2026, depois de duas versões: a primeira ampliava o papel; a
segunda criava um papel próprio, o "Administrador do registro de unidades". A segunda foi recusada
por não haver exigência institucional que pedisse a separação.* A regra que o usuário fixou vale
daqui em diante: **toda abstração, papel, tabela ou mecanismo novo precisa resolver um problema
concreto, e não uma possibilidade futura.**

**Decisão.** A permissão nova entra na lista do `administrador-institucional`, em
`PAPEIS_INSTITUCIONAIS` (`seguranca/acessos.py`), ao lado de `acesso:administrar`. O papel passa a se
chamar **"Administrador institucional"**. A chave `administrador-institucional`, os vínculos, os três
comandos de implantação, as regras da `106` e da `107` e a trilha ficam como estão. Como a
`autoridade:gerir` da `060`, a permissão é declarada em `unidades/domain/nomes.py` e escrita por
extenso no catálogo, e um teste confere que as duas grafias são a mesma.

**Dois níveis, e não três.**

| Nível | Papel | Permissões | Concedido por |
|---|---|---|---|
| institucional | Administrador institucional | `acesso:administrar`, `unidade:administrar` | só a implantação (FR-3029 da `106`) |
| unidade | Administrador de acessos da unidade | `acesso:gerir`, `acesso:consultar` | o Administrador institucional (`107`) |

O administrador de acessos da unidade continua separado: ele tem justificativa operacional — a
gestão de usuários se descentraliza quando outros campi entram. Dois papéis não são duas pessoas;
quem recebe cada um é designação institucional.

**Por que não o papel próprio.** O menor privilégio continua certo como princípio, mas a separação
só se paga quando há exigência de que as duas responsabilidades fiquem com pessoas diferentes. Não
há: são cerca de 26 unidades, cujo cadastro muda em anos, numa equipe de duas ou três pessoas. O
papel próprio custava um segundo papel no catálogo, a opção `--papel` nos três comandos, as regras de
segunda pessoa e de última administração por papel, a recusa pela tela estendida, a suspensão
estendida e a tela mostrando um papel ou o outro — tudo para uma separação que ninguém pediu. Se um
dia for pedida, separar é mover a permissão para um papel novo, sem tocar no resto desta feature.

**O que a permissão não dá.** Nenhuma outra capacidade (FR-3310): nem Processo, Edital, Publicação,
autoridades, modelos de aviso, nem acesso de unidade. O risco novo é de disponibilidade e de
integridade editorial — uma conta comprometida poderia renomear ou desativar uma unidade —, e não de
acesso a dado; os dois ficam na trilha da unidade e se desfazem pela própria tela. Continua faltando
quem leia os atos institucionais como conjunto (P-4).

**A ampliação não pode ser silenciosa.** Quem já tiver o papel ganharia o poder novo no deploy, sem
ato novo. Por isso a [migração](migracao.md) começa por uma verificação, em cada ambiente instalado:

- **sem nenhum vínculo vigente** de `administrador-institucional`, a ampliação não alcança ninguém,
  e o papel consolidado se adota como está;
- **com algum**, o deploy não se faz antes de o usuário autorizar expressamente, pessoa por pessoa,
  a ampliação — com o ato que a designa, que é o motivo de uma nova concessão, se for o caso — ou
  retirar a administração dela pela implantação.

Em 31/10/2026 nenhum banco local tinha vínculo vigente desse papel, e produção nunca foi instalada.
A VM de homologação não estava ao alcance desta verificação, e é o primeiro ambiente a conferir.

**O rótulo muda em um lugar de código** — a entrada do catálogo —, mais as mensagens e ajudas que
dizem "administração institucional de acessos": a recusa ao suspenso (`interface/views.py`), as
recusas da primeira administração (`seguranca/application/acessos.py`) e as ajudas dos três
comandos. Nenhum teste existente confere o rótulo. A trilha guarda a chave, e não o rótulo: os atos
antigos passam a ser lidos com o nome novo, que é o do mesmo papel. As specs `106`, `107` e `108`
ficam como estão — registram o nome do dia em que foram escritas.

**Descartado.**
- *Papel institucional próprio* (a segunda versão): ver acima.
- *Ampliar sem verificar quem tem o papel* (a primeira versão, sem o passo 0): ampliaria privilégio
  real em silêncio.
- *Manter o rótulo antigo*: diria menos do que o papel faz.
- *O gestor da unidade edita os campos dela*: recusado pela decisão de produto 4.

## D-003 — O comando passa a `semear_unidades`, e `sincronizar_unidades` continua como apelido

*Revista em 31/10/2026. A versão anterior apagava o nome antigo e aceitava que um `ps-migrar`
instalado de cópia antiga falhasse no deploy.*

**Decisão.** O nome canônico é `semear_unidades`, que diz o que o comando passa a fazer.
`sincronizar_unidades` **continua existindo**, como apelido: a mesma classe de comando, que escreve
uma linha no *stderr* — `sincronizar_unidades é o nome anterior de semear_unidades; atualize o
roteiro que o chamou.` — e faz exatamente o que a semente faz, com o mesmo código de saída. As duas
chamadas aceitam as mesmas opções.

**Quem passa ao nome novo, no mesmo commit:** o preparo local (`backend/Makefile`), o
`scripts/docker/entrypoint.sh`, o `seed_demo`, o `ps-migrar` e os outros cinco pontos do guia de
produção, e os dois scripts de `doc/` e `docs/` que importam ou citam a sincronização. As auditorias
datadas em `doc/` ficam como estão: registram o que era.

**Por quê.** O deploy de uma versão nova não pode falhar por um roteiro instalado ter o nome
anterior. Um `ps-migrar` de cópia antiga chama o apelido, a semente roda, a subida termina, e o aviso
fica no *log* para quem o ler. O aviso vai ao *stderr*, e não ao *stdout*: a linha
`Unidades: ...`, que o guia ensina a ler, continua a primeira da saída. E o `set -eu` do
`entrypoint.sh` e do `ps-migrar` só reage ao código de saída, que é o da semente.

**Quando o apelido sai.** Não nesta feature. Sai quando todo roteiro instalado tiver sido
reinstalado a partir do guia novo — fato da operação, que o repositório não vê. Fica registrado como
pendência técnica no guia de produção (FR-3307), com o critério: nenhum *log* de implantação com o
aviso.

**Descartado.**
- *Remover o nome antigo* (a versão anterior): falha alta no primeiro deploy de quem instalou o
  roteiro antes, depois do `migrate`. Era benigno, mas é uma falha de deploy por nome, que o pedido de
  31/10 manda evitar.
- *Manter só o nome antigo, com a semântica nova*: zero mudança nos roteiros, ao custo de um nome
  que ensina o modelo errado — que o arquivo manda no banco — a quem lê o guia.
- *Apelido para a função Python `sincronizar`*: quem a importa está no repositório e muda no mesmo
  commit; um apelido de função só esconderia o import velho.

## D-004 — A semente: trava, validação, trilha e saída

**Decisão.**
- **Trava global** (`pg_advisory_xact_lock`), como a primeira administração institucional da `106`:
  "o registro está vazio?" é pergunta sobre a tabela inteira, e duas subidas simultâneas do contêiner
  sobre um banco novo gravariam o Cefor duas vezes — a segunda falharia na unicidade e derrubaria a
  subida. Com a trava, a segunda espera e encontra o registro preenchido.
- **Validação** do arquivo inteiro antes de gravar, pela regra única da D-005, só quando a semente
  se aplica. Num registro preenchido o arquivo não é lido: um arquivo sem autoridade não pode
  derrubar uma subida.
- **Trilha** como hoje: `REGISTRAR_UNIDADE`, ator `implantacao`, escopo da unidade.
- **Modelos iniciais de aviso** garantidos sempre, como hoje (`garantir_modelos_iniciais`, que já é
  idempotente e só insere).
- **Saída**, uma linha para cada caso, para que o `CLAUDE.md` possa ensinar a lê-la:
  `Unidades: 1 semeadas.` e `Unidades: registro com 3 unidades; a semente não se aplica.`, seguidas
  de `Modelos de aviso: N criados.`

## D-005 — Uma regra de validação, no domínio

**Decisão.** O que hoje é `validar` em `unidades/application/sincronizacao.py` — inclusive o canal
de atendimento da `109` — vai para `unidades/domain/registro.py`, como função pura que recebe os
campos de uma unidade e devolve os valores normalizados ou a primeira recusa, com o campo. A semente,
o cadastro e a edição a chamam. Nada é copiado.

As recusas ganham códigos próprios por campo, para a tela pôr a mensagem no lugar certo (o padrão
das autoridades da `060`): `codigo_invalido`, `codigo_reservado`, `campo_obrigatorio`,
`cabecalho_invalido`, `atendimento_invalido`. A semente as embrulha em `unidade_malformada`, que é o
que o comando já diz hoje.

**A situação (`ativa`) não é da regra única.** Ela é campo do arquivo-semente, conferido como
booleano pelo leitor da semente, e na aplicação só muda por desativar e reativar, que não passam por
formulário de campos.

**O formato do código** é o regex de hoje — minúsculas, dígitos e hífen interno —, com o limite da
coluna (100). A regra não aceita "corrigir" a caixa por conta própria (EC-1 da spec): o código é
permanente, e uma conversão silenciosa decidiria por quem cadastra.

## D-006 — Quatro casos de uso e as conferências, no `unidades`

**Decisão.** `unidades/application/registro.py` expõe `registrar`, `alterar`, `desativar` e
`reativar`, e para cada um um `conferir_*` que só lê — o padrão de duas etapas da `107`. Cada ato:

1. confere `unidade:administrar` **e** o escopo do ator igual ao institucional, as duas como recusa
   por base (`require_authorization_base`, 403), como `_ator_do_nivel` da `107` — e não por
   `require_permission(..., institution_scope=...)`, que responde 404 quando o escopo diverge;
2. exige o motivo;
3. abre `command_context`, trava a linha da unidade (`select_for_update`), reconfere tudo;
4. grava a unidade e o evento na mesma transação (FR-3332);
5. no registro, cria os três modelos iniciais **da unidade nova, com a pessoa como autora**, dentro
   da mesma transação. `garantir_modelos_iniciais` não serve como está: não recebe unidade, trava
   todas, e grava com o ator `implantacao` e o `correlation_id` da sincronização — a trilha diria que
   a implantação criou os modelos. A criação de uma unidade é extraída dela em
   `avisos/application/modelos.py`, e a função de sempre passa a chamá-la com o ator de sempre.

A unicidade do código, violada por cadastro concorrente (EC-2), é convertida em
`codigo_ja_registrado` por um bloco atômico aninhado em volta do `INSERT`, para que o erro não
envenene a transação externa.

**As leituras também são da aplicação.** `listar(ator)` e `ficha(ator, codigo)` — esta com os
eventos da unidade — conferem a mesma permissão; a tela não consulta o registro por conta própria
(FR-3309).

Não há chave de idempotência: o reenvio do cadastro esbarra na unicidade do código
(`codigo_ja_registrado`), e o reenvio de uma edição, desativação ou reativação esbarra na
conferência de versão (D-007) ou na transição já feita (FR-3328). É o que a `107` faz com a
concessão.

**Descartado.** *Pôr os casos de uso em `seguranca`*: a unidade é do `unidades`, e o `seguranca` só
precisa da constante da permissão no catálogo.

## D-007 — Concorrência: a versão conferida, sem coluna nova

**Decisão.** A conferência devolve, num campo oculto, o resumo (`sha256`) dos valores atuais da
unidade em forma canônica — os seis campos editáveis e `ativa`; não `alterada_em`, que é efeito.
Desativar e reativar levam a mesma versão: as consequências que a tela mostrou (Processos não
encerrados, mudança da moldura) foram calculadas sobre aquela versão. A confirmação trava a linha, recalcula o resumo e recusa
(`unidade_alterada`) se ele mudou: alguém editou entre a conferência e a confirmação.

**Por quê.** É a perda de atualização que a Constituição manda tratar (princípio IV). Uma coluna de
revisão faria o mesmo com uma migration em `unidades` e o guardião das migrations, para uma tabela
que muda em anos. O resumo forjado não abre nada: quem o forja já tem a permissão, e só conseguiria
sobrescrever uma edição alheia — o que o ato, com motivo e trilha, mostraria.

**Descartado.** *Último que grava vence*: perde a edição da primeira pessoa sem aviso.

## D-008 — Eventos que a trilha da `108` já lê

**Decisão.** Os atos gravam com os nomes que o registro já usa, para que a trilha da unidade
*(108)* os leia sem mudança:

| Ato | `operation` | `previous_state` → `new_state` | `detalhe` |
|---|---|---|---|
| cadastrar | `REGISTRAR_UNIDADE` | — → `ATIVA` | `{"depois": {...}}` |
| editar | `ALTERAR_UNIDADE` | `ATIVA` → `ATIVA` (ou `DESATIVADA` → `DESATIVADA`) | `{"antes": {...}, "depois": {...}}` |
| desativar | `ALTERAR_UNIDADE` | `ATIVA` → `DESATIVADA` | idem, com `ativa` mudando |
| reativar | `ALTERAR_UNIDADE` | `DESATIVADA` → `ATIVA` | idem |

`aggregate` é a Unidade, `permission` é `unidade:administrar`, `reason` é o motivo, `actor_subject` é
o identificador interno da pessoa. **O escopo do evento é o código da unidade**, e não o
institucional do ator: `record_event` toma o escopo do ator, e por isso o caso de uso grava com um
`Actor` de mesmo `subject` e permissões no escopo da unidade — exatamente o que a sincronização já
faz com `Actor(IMPLANTACAO, codigo)`. É o que põe o ato diante do auditor da unidade.

**Descartado.** *Operações novas* (`DESATIVAR_UNIDADE`, `REATIVAR_UNIDADE`): mais legíveis na trilha
crua, mas a `108` traduz por um mapa de operações, e cada nome novo seria mudança nela, que está em
revisão. A situação já diz o que aconteceu.

## D-009 — A ficha reaproveita a leitura e a tradução da `108`

**Decisão.** A ficha lê os eventos da unidade por uma consulta só — agregado `Unidade` e o `id`
dela, do mais recente para o mais antigo — e os traduz pela função `linhas` de
`interface/trilha_da_unidade.py` *(108)*, que já põe em palavras o ato, a situação, o autor (pelo
nome, ou "Implantação") e o antes→depois. Não há paginação: a unidade muda em anos.

**Duas costuras com a `108`.** O autor pelo nome não sai de `linhas`: sai da tag `nome_de_pessoa`
no template, que a ficha usa do mesmo jeito. E o mapa `CAMPOS_LEGIVEIS["Unidade"]` precisava do
canal de atendimento, que a `109` criou depois da `108`: a integração das duas o acrescentou
(`25460040`, "Trilha da unidade mostra o canal de atendimento da 109"). Aqui não há mais o que
acrescentar; o teste da trilha dos atos (T035) confere uma edição só do canal.

**A trilha da `108` não abre no escopo institucional** (a revisão de código dela, `c76dca30`, tirou o
item da barra nesse escopo, e a página já recusava). A ficha é, portanto, o único lugar em que o
Administrador institucional lê o histórico de uma unidade — e é por isso que ela tem a leitura própria.

**Por quê não o *selector* da `108`.** Ele toma a unidade do ator, e o ator aqui é institucional. A
consulta própria é uma linha; o que não se duplica é a tradução, que é onde mora a regra.

**Descartado.** *Esperar a P-4 e mostrar o histórico só na trilha*: o Administrador institucional
não tem `auditoria:consultar` em unidade nenhuma, e a FR-3315 pede o histórico na ficha.

## D-010 — A prévia é texto, pelas linhas que o compositor usa

**Decisão.** A prévia mostra, em HTML, as linhas de `linhas_do_orgao` de
`publicacoes/infrastructure/pdf.py` — as duas da instituição seguidas das da unidade —, o local no
fecho ("Vitória (ES), 31 de outubro de 2026") e a marca da moldura pela identificação da `109`
("Serra/Ifes") e a sigla como o anúncio do ato a imprime (`anuncio_em_caixa_alta`, a mesma função
do compositor). Cada linha do cabeçalho é medida pela métrica do compositor contra a largura que o
cabeçalho tem; a que não couber gera um **aviso** na conferência — no documento ela quebraria em
duas, e a prévia em HTML não mostra isso por si. Aviso, e não recusa: quebrar é feio, não é errado.
A função recebe um objeto com `cabecalho`; a tela passa os valores conferidos, e não
a unidade gravada. O módulo do compositor é importado dentro da função da view, para não pesar no
carregamento das outras telas.

**Por quê.** É a função que decide as linhas do documento oficial: a prévia não pode ter regra
própria. E o que se quer conferir é a quebra das linhas e a grafia, que o texto mostra.

**Descartado.** *Gerar um PDF de amostra*: o cabeçalho é a única parte que muda, o painel do
navegador não exibe PDF embutido, e um documento com cara de oficial gerado fora de um ato é o que a
Constituição não quer circulando.

## D-011 — As telas, num módulo próprio da `interface`

**Decisão.** `interface/unidades.py`, no molde de `interface/acessos.py`: o ator do nível
institucional com a permissão, a recusa da sessão de demonstração, a conferência que não grava e a
confirmação que chama o caso de uso. Rotas sob `/gestao/administracao-de-unidades`:

| Rota | Métodos | O quê |
|---|---|---|
| `` | GET | lista |
| `cadastrar` | GET, POST | formulário; `acao=conferir` mostra a conferência; `acao=confirmar` grava |
| `<codigo>` | GET | ficha |
| `<codigo>/editar` | GET, POST | idem cadastrar |
| `<codigo>/desativar`, `<codigo>/reativar` | GET, POST | consequências e motivo; `acao=confirmar` grava |

Código não registrado responde 404, e a linha entra no inventário das negativas da `033` no mesmo
commit, classificada como objeto inexistente. A barra ganha "Unidades" em `SECOES_DE_ACESSO`,
logo depois de "Administração de acessos", só para quem tem a permissão — e por isso a demonstração
nunca a vê.

Estilo em `interface/static/interface/telas/unidades.css`, pela CSP; nenhum script.

## D-012 — LGPD

| Dado | Natureza | Exposição | Decisão |
|---|---|---|---|
| sigla, nome, cabeçalho, local | institucional e público — sai em todo documento oficial | nenhuma nova | — |
| canal de atendimento | contato institucional, que o candidato lê | a mesma da `109` | a ajuda do campo diz que é o canal da unidade, e não o contato pessoal de um servidor |
| quem praticou o ato | identificador interno da pessoa na trilha; o nome na ficha | só a quem tem `unidade:administrar`, que já vê nomes e e-mails na administração de acessos | — |
| motivo | texto livre do servidor | idem | a ajuda pede para não escrever dado pessoal de candidato |

Nenhum dado de candidato é lido, gravado ou mostrado. A retenção é a da trilha, que não se exclui.

## D-013 — O escopo de Processo e de Edital, imutável por gatilho

**Decisão.** Uma migration em `processos` cria dois gatilhos `BEFORE UPDATE ... WHEN
(OLD.institution_scope IS DISTINCT FROM NEW.institution_scope)`, um em `processos_processoseletivo`
e outro em `processos_edital`, que recusam a mudança — o molde exato de `unidade_codigo_imutavel`
(`unidades/0002`). Fora do PostgreSQL a migration é no-op, como lá.

- **Privilégios**: nenhum muda. As duas tabelas mudam legitimamente em outras colunas, e não entram
  em `TABELAS_APPEND_ONLY`; o `M` do provisionamento continua 46.
- **ORM**: um `save()` completo regrava o mesmo escopo, e `IS DISTINCT FROM` é falso — não recusa.
  Só a mudança de valor recusa, venha do `QuerySet.update()`, do `save()` ou de SQL direto.
- **Código de produção**: nenhum caminho muda o escopo (varredura de 31/10: nenhum `update` nem
  atribuição de `institution_scope` fora da criação).
- **Testes**: um só o muda, `tests/integration/agenda/test_fonte.py:197`, para simular um Edital
  da Serra. Ele passa a criar o Edital por um ator da outra unidade, registrada antes (FR-3335).
- **Guardião das migrations**: `processos` sobe de 4 para 5 em `tests/migrations/test_migrations.py`,
  com o parágrafo de justificativa.

**Descartado.** *FK para `Unidade.codigo`*: compraria a conferência de existência na inserção
direta, que não é o risco com causa plausível, ao custo de registrar a unidade alheia em todo teste
de isolamento (decisão dois da `060`). *Gatilho também em avisos e auditoria*: o aviso copia o
escopo do Edital no ato e não o muda depois; a trilha já é append-only nas duas camadas.

## D-014 — Os testes de isolamento: um caminho de maior risco por área

**Decisão.** Uma unidade `campus-a` registrada e um ator dela; para cada área, o caminho que recebe
identificador do objeto e grava:

| Área | Caminho | Por quê este |
|---|---|---|
| Ocupação | `editais/<id>/marcos/<id>/ocupacao/acrescentar-vagas` e `desfazer-acrescimo` sobre Edital alheio | grava em tabela append-only |
| Recursos | `recursos/<id>/admitir` e `recursos/<id>/julgar` sobre recurso alheio | é ato contestável |
| Requerimentos | a consulta administrativa da inscrição alheia (`inscricoes/<id>/`), que mostra o requerimento de matrícula, e o documento dela (`inscricoes/<id>/documentos/<id>`) | tem dado pessoal; a exportação de matrículas já tem teste de segunda unidade |
| API administrativa | `GET` e um `POST` de mudança de estado em Processo e Edital alheios sob `/api/v1/admin/` | não passa pela interface |

Em cada um: a resposta é a de objeto inexistente, e o número de eventos da trilha e de linhas da
tabela tocada não muda. **Se algum revelar vazamento**, a correção entra nesta feature — é o que a
FR-3336 pede — e o achado é registrado no `verificacao.md`.

## D-015 — A jornada pelo navegador

**Decisão.** Um caso em `tests/navegador/`, no molde da `107`. A preparação concede, pela
implantação, o Administrador institucional a uma pessoa. Ela entra pelo provedor simulado, cadastra
`serra`, confere a prévia, confirma, concede o Administrador de acessos de `serra` a outra pessoa,
que entra e concede o Gestor a uma terceira, que cria um Processo. Entre a preparação e as
verificações, nenhuma ação fora do navegador (SC-1041).

É a prova automatizada do princípio VI. A validação por pessoas é outra coisa, e usa a entrada de
homologação (D-017, D-018).

## D-016 — Exportar o registro, só para reverter

**Decisão.** `semear_unidades --exportar` imprime o registro atual no formato do arquivo-semente, e
não grava nada. O formato é o que a **release de destino** aceita: todos os campos obrigatórios,
inclusive `ativa`, e `atendimento` só quando preenchido — a validação da `109` recusa o canal
declarado vazio. Um teste confere que a saída passa pela regra da semente.

**Por quê.** A reversão desta feature para a versão anterior volta a ligar a sincronização, que
recusaria subir com unidade fora do arquivo e reverteria toda edição feita pela tela. O procedimento
de reversão ([migracao.md](migracao.md)) começa por exportar o registro e pô-lo no arquivo da versão
a que se volta. Sem o comando, isso seria uma consulta escrita à mão no meio de um incidente.

**Não** é sincronização reversa: ninguém o roda em deploy, e nada lê a saída dele.

## D-017 — Antes do SSO: o teste automatizado prova as regras; a validação funcional é outro ambiente

*Revista duas vezes em 31/10/2026. A primeira versão aceitava que, até o SSO, a tela só existisse na
suíte; a segunda propunha um código assinado emitido pelo operador. Esta é a terceira, depois da
comparação pedida pelo usuário antes do PR B.*

**O fato.** As telas exigem a entrada institucional (FR-3312), que só existe com um adaptador em
`GESTAO_PROVEDOR_INSTITUCIONAL`. A VM de homologação do guia roda `config.settings.production`
(§10.3 do guia): sem SSO, **a gestão inteira** responde 503 lá — criar Processo, publicar, conceder
acesso. É o B-1 do guia (§17.3), e não uma limitação desta feature.

**A VM de homologação não muda.** O valor dela é ensaiar a receita de produção — as mesmas settings,
as mesmas barreiras, o mesmo `ps-migrar` —, e o 503 sem SSO é uma dessas barreiras, provada lá.
Ligar nela qualquer mecanismo de teste exigiria afrouxar uma recusa de `production.py`, e uma
recusa condicional é o caminho pelo qual o mecanismo chega a produção. A validação funcional
acontece **noutro ambiente**, descrito na D-018.

**Duas coisas diferentes.**

| | Teste automatizado | Validação funcional |
|---|---|---|
| Pergunta | as regras valem? | a tela serve a quem vai usá-la? |
| Quem faz | a suíte, no CI e em `make test-pg` | pessoas da equipe, seguindo um roteiro |
| Onde | banco de teste, provedor simulado da `106`, navegador da `107` | o ambiente de homologação funcional (D-018) |
| Prova | recusas, trilha, concorrência, semente, gatilhos, a jornada de ponta a ponta (D-015, SC-1041) | linguagem, prévia contra o documento, consequências ditas antes de desativar, percurso sem ajuda |
| Como se registra | resultado da suíte, no PR | **critério de aceite humano** (SC-1048), com data e quem validou, no `verificacao.md` — nunca como teste |
| Quando | a cada commit | antes de a feature ser dada por aceita, e de novo antes da segunda unidade ativa em produção |

**As duas estratégias comparadas** para levar pessoas às telas antes do SSO:

| Critério | Seletor de demonstração, só em homologação | Provedor institucional de testes, pelo contrato da `106` |
|---|---|---|
| Alcança as telas desta feature? | **não**, sem mudar regra: a sessão de demonstração é recusada antes de ler (FR-3312, e a FR-3127 da `107` para os acessos). Alcançar exigiria um nono papel no seletor (contraria a FR-3001 da `106`) ou aceitar a demonstração nas telas institucionais | sim: é a entrada institucional |
| Exercita o que produção vai rodar? | não: o `Actor` vem do papel declarado, sem vínculo, sem pessoa, sem troca de escopo, sem os prazos da sessão; a trilha grava `demo-…`, e o histórico da ficha não mostraria nomes | sim: pessoa e identidade externa, vínculos concedidos pela implantação, `Actor` recalculado a cada pedido, escopo institucional, prazos, autor pelo nome |
| Na VM de homologação | exige tirar a recusa do seletor de `production.py` ou uma settings nova | também não roda lá (`production.py` recusa adaptador de `tests.`) — e não deve: ver acima |
| Mudança de código | no seletor, ou na regra das telas institucionais | uma subclasse de 20 linhas do provedor simulado, em `tests/` |
| Criptografia própria | nenhuma | nenhuma: o bilhete é o do provedor simulado (aleatório, de uso único, consumido no retorno) |
| Risco de chegar a produção | o seletor tem uma recusa; afrouxá-la para a VM é o risco | duas recusas que já existem e já têm teste (pacote `tests.`, declaração de teste), no *boot* e em execução |

**Decisão.** O provedor institucional de testes (D-018), num ambiente de homologação funcional
isolado, separado da VM de homologação. O seletor continua como está, servindo à homologação do
resto da gestão (FR-3338).

**O que esta escolha não esconde.** Dentro do ambiente, quem passa pelo perímetro escolhe, na página
do provedor, como qual pessoa cadastrada entrar — é uma declaração, como no seletor, restrita às
pessoas que a implantação cadastrou. **A barreira é o perímetro**, e não a página: o ambiente só é
alcançável por quem valida, e só tem dado sintético (D-018). É por isso que a exposição dele é decisão
de governança (P-6), e não detalhe técnico.

**Descartado.**
- *Seletor de demonstração em homologação*: ver a tabela.
- *Código assinado emitido pelo operador* (a segunda versão): autenticação criptográfica própria,
  um passo do operador a cada entrada, e nenhum ganho dentro de um perímetro que já restringe quem
  chega.
- *Código por e-mail, reaproveitando o desafio do portal*: o desafio é do domínio do candidato
  (`identidade`), com finalidades fechadas no modelo; usá-lo na gestão acoplaria os dois domínios e
  pediria migration — escopo novo para proteger um ambiente de dado sintético.
- *Provedor OIDC de desenvolvimento num contêiner (Keycloak ou semelhante)*: é metade da integração
  do SSO, fora do escopo, com um serviço novo para operar.
- *Mudar a VM de homologação para settings de desenvolvimento*: perde o ensaio da receita de
  produção, que é a razão de ela existir.
- *Validar assistindo à jornada do navegador*: é demonstração — quem assiste não opera.

## D-018 — O provedor de homologação e o ambiente de homologação funcional

*Revista em 31/10/2026: substitui o código assinado da versão anterior pelo provedor simulado da
`106`, e descreve o ambiente.*

**O provedor.** `tests/homologacao/provedor.py` define `ProvedorDeHomologacao`, **subclasse** de
`tests.fixtures.provedor_simulado.ProvedorSimulado`:

- herda `concluir` — o bilhete aleatório, de uso único, retirado do provedor no retorno — e
  `apenas_para_testes = True`;
- muda só `iniciar`: em vez de mandar a `provedor.invalid`, responde a página do provedor — a mesma
  forma da página de `tests/navegador/provedor.py` —, com uma linha por pessoa cuja identidade
  externa é do provedor `homologacao`, com o nome e os papéis vigentes. Escolher uma emite o bilhete
  (`provedor_simulado.emitir`) e volta ao retorno da gestão com o `state` da ida;
- o nome do provedor é `homologacao`: as pessoas dele nunca se confundem com as do provedor real.

Nada mais muda: o estado de uso único ligado à sessão continua conferido pela gestão (FR-3023 da
`106`); a página de entrada oferece a entrada institucional porque há adaptador (FR-3025); o
*backend*, a sessão, os vínculos, o seletor ficam como estão. **Quem existe na página é quem a
implantação cadastrou**: o operador concede os papéis pelos comandos de sempre, com
`--provedor homologacao`, e cada concessão vai à trilha com o motivo.

**Por que não chega a produção.** Duas recusas que já existem, com teste, valem para a subclasse
sem uma linha nova: o pacote `tests.` e a declaração de teste, recusados por `production.py` no
*boot* e por `provedor_configurado` em execução (FR-3026 da `106`). Os testes desta feature
conferem as duas para o adaptador novo.

**Limite conhecido.** Os bilhetes ficam na memória do processo, como no provedor simulado. Serve ao
`runserver` da imagem de desenvolvimento, que é um processo só; num servidor de vários processos a
volta cairia noutro e não acharia o bilhete. É o ambiente da validação, e não outro.

**O ambiente de homologação funcional** — a configuração a documentar no guia (§10.3), ao lado da
VM de homologação, e não no lugar dela:

| Item | Configuração | Por quê |
|---|---|---|
| Onde | um *host* próprio, ou a máquina de quem conduz; **nunca** a VM de homologação | a VM ensaia produção (D-017) |
| Como sobe | o `compose.yaml` do repositório (imagem de desenvolvimento, `runserver`, coletor de e-mail) | é a imagem que já existe para isso; um processo só |
| Settings | `config.settings.development`, sem mudança | o adaptador é recusado em qualquer outra |
| Identidade | `INTERFACE_SELETOR_IDENTIDADE=false`; `GESTAO_PROVEDOR_INSTITUCIONAL=tests.homologacao.provedor.ProvedorDeHomologacao` | toda sessão vem da entrada institucional |
| Banco | próprio, novo, só com dado sintético; `make preparar`, depois `seed_demo` se a validação pedir certames | nunca cópia de produção (§10.3 do guia) |
| Segredos | `DJANGO_SECRET_KEY` gerada para ele, diferente da de produção e da VM | §10.3 do guia |
| Perímetro | só em `localhost`, até a P-6. Se o usuário aprovar a rede: rede fechada (VPN ou *firewall* restrito aos endereços de quem valida) **e** um *proxy* com autenticação básica, uma credencial por pessoa | a barreira é o perímetro (D-017) |
| *Proxy* | sem terminar TLS diante do `runserver` — o transporte cifrado é o da VPN —, preservando o `Host`; `DJANGO_ALLOWED_HOSTS` com o nome usado | as settings de desenvolvimento não confiam no `X-Forwarded-Proto`: um *proxy* HTTPS faria a conferência de origem do CSRF recusar todo POST |
| `DEBUG` | ligado, como nas settings de desenvolvimento | aceito dentro do perímetro: o ambiente só tem dado sintético, e o rastro do erro ajuda a relatar defeito |
| Vida | sobe para a sessão de validação; o banco se descarta depois | nada a manter entre sessões |

**Descartado.** *Código assinado com validade* (versão anterior): ver a D-017. *Página que pede o
identificador por texto livre*: criaria pessoa por digitação; a lista mostra só quem a implantação
cadastrou. *Pôr o adaptador em `processo_seletivo/`*: perderia a recusa pelo pacote.

## D-019 — Três incrementos, e a troca da fonte junto com o mecanismo que a substitui

**Decisão.** Três PRs, nesta ordem de dependência:

| Incremento | O que leva | Depende de | Muda comportamento? |
|---|---|---|---|
| **A — Integridade do escopo** | os gatilhos de escopo imutável (D-013), o ajuste do teste da agenda e os testes de isolamento (D-014) | nada | só recusa o que nenhum caminho da aplicação faz |
| **B — Entrada de homologação** | o provedor de homologação (D-018), os testes das recusas de produção, o roteiro G e o ambiente no guia | nada | não: só código de teste e documentação |
| **C — Fonte oficial e administração** | a regra única, a permissão no papel institucional, a semente com o apelido, os casos de uso, as telas, a jornada, a documentação | B, para a validação funcional | **sim**: a fonte passa ao banco, e o mecanismo novo chega no mesmo PR |

A e B se fazem em qualquer ordem, e em paralelo. **C é um PR só**: dentro dele o trabalho segue
passos com a suíte verde em cada um, mas a troca da sincronização pela semente não entra na `main`
sem as telas e o papel.

**Por quê.** A versão anterior entregava a semente primeiro. Depois daquele PR, o arquivo deixaria
de criar unidade num banco existente, e a tela ainda não existiria: num ambiente que usa unidade —
desenvolvimento, compose —, não haveria como cadastrar uma. Juntar a troca e o mecanismo fecha essa
janela.

**E nenhum ambiente fica sem mecanismo de cadastro que possa usar.**

| Ambiente | Antes da `110` | Depois de C |
|---|---|---|
| desenvolvimento e compose | o arquivo, num commit | a tela, pela entrada de homologação (B); ou banco novo com `semear_unidades --arquivo` |
| instância controlada de validação | — | a tela, pela entrada de homologação |
| VM de homologação e produção, antes do SSO | o arquivo, num deploy — mas a gestão responde 503, e nenhuma unidade nova pode ser usada: não há como criar Processo nem conceder acesso nela | a tela, que também responde 503 até o SSO. Nada que se pudesse fazer com uma unidade nova deixa de ser possível |
| produção, depois do SSO | o arquivo, num deploy | a tela |

O único efeito de uma unidade nova em produção antes do SSO seria a moldura pública da `109` mudar
de "Cefor/Ifes" para "Ifes" — efeito sem uso, que a P-1 ainda nem decidiu. **Se uma unidade
precisar existir em produção antes da `110`**, ela entra pelo arquivo, na release anterior (regra 2
da [migração](migracao.md)).

**A pode ir já.** É o defeito de integridade que a revisão de 30/10 achou, e não depende de decisão
pendente nenhuma. Se algum teste de isolamento revelar vazamento, a correção entra em A.

**Descartado.**
- *A semente primeiro* (a versão anterior): abre a janela descrita acima.
- *Um PR só para tudo*: o gatilho e o isolamento esperariam a revisão das telas, sem depender delas.
- *A entrada de homologação dentro de C*: ela serve à `107` e ao resto da gestão, e não muda
  produto; num PR próprio, a revisão dela é a das recusas de produção, sem as telas no meio.

## Perguntas ao usuário

A decisão de produto 3 voltou ao papel existente, por decisão do usuário em 31/10/2026 (D-002).
Continuam com o usuário, e nenhuma bloqueia a implementação:

- **A ampliação do papel onde já houver Administrador institucional** (P-5 da spec): bloqueia o
  deploy do incremento C naquele ambiente, e não o código.
- **A exposição do ambiente de homologação funcional além de `localhost`** (P-6 da spec).
