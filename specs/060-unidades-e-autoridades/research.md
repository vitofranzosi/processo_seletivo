# Research: Unidades institucionais e autoridades de publicação

Levantamento feito em 06/10/2026 sobre a árvore de `eb982468`. Cada decisão diz o que foi escolhido,
por quê, e o que se descartou.

---

## R-001 — Um app novo, `unidades`

**Decisão.** `Unidade` e `AutoridadeHabilitada` moram num app próprio, `processo_seletivo/unidades/`,
com `models.py`, `domain/`, `application/` e `management/commands/`.

**Por quê.** A Unidade é lida por quatro apps — `processos` (criação), `publicacoes` (Edital e
Retificação), `divulgacao` (Resultado) e `inscricoes`/`portal` (comprovante) — e não pertence a
nenhum. `seguranca` é dono do escopo, mas não tem modelo nem migration, e a README o descreve como
autorização; pôr cadastro ali mudaria o que ele é. `processos` e `publicacoes` têm contagem de
migrations presa por dois guardiões (`test_a_022_…` e `test_a_017_…`), e acrescentar duas tabelas
de outro assunto num deles seria a 060 "tocando o que lê".

**Custo aceito.** Linha na tabela de módulos do README, entrada em `INSTALLED_APPS` com a
justificativa, e o app em `APPS` e `TRIGGERS_POR_APP` de `tests/migrations/test_migrations.py`.

**Descartado.** Pôr as duas tabelas em `publicacoes`, onde o catálogo mora hoje: a Unidade não é
assunto de publicação — a criação de Processo também a lê (FR-1110) — e a dependência
`processos → publicacoes` inverteria a direção atual.

## R-002 — A Unidade guarda o escopo como código; nada aponta para ela

**Decisão.** `Unidade.codigo` é texto único e imutável, igual ao valor de `institution_scope`. A
chave primária é UUID, porque `record_event` exige `aggregate.pk` UUID. `ProcessoSeletivo`, `Edital`,
`RegistroAuditoria` e `IdempotencyRecord` **não** ganham chave estrangeira (`D-001`).

**Por quê.** As 22 ocorrências de `escopo="outra-unidade"` nos testes e os portadores
`…|outra|…` provam que o escopo é usado como valor livre em isolamento, e é isso que deve continuar
funcionando. Uma FK obrigaria todo teste de isolamento a registrar a unidade alheia, para não ganhar
garantia nenhuma que a recusa de criação (R-011) não dê.

## R-003 — Unidades vêm de um arquivo versionado, aplicado por comando

**Decisão.** O registro de Unidades é declarado em `unidades/unidades.json`, revisado em diff, e
aplicado ao banco pelo comando `sincronizar_unidades`, que o `make preparar` roda depois de migrar
(`D-002`). O comando:

- cria a Unidade que aparece pela primeira vez;
- atualiza nome, sigla, linhas de cabeçalho, local e situação que mudaram;
- **recusa** retirar uma Unidade do arquivo (FR-1109) — desativar é `"ativa": false`;
- **recusa** um código que mude (FR-1108) — o código é a chave do arquivo;
- registra cada criação e cada mudança em `RegistroAuditoria`, com o ator `implantacao`, o escopo da
  própria Unidade e `detalhe = {"antes": …, "depois": …}`;
- é idempotente: rodado duas vezes sem mudança no arquivo, não grava nada.

**Por quê.** São ~26 unidades que mudam em anos, e as linhas do cabeçalho são decisão editorial de
documento oficial. O argumento que derrubou o catálogo de autoridades — mudança frequente — não vale.
E a trilha que a FR-1108 exige fica de pé: migration de dados não pode importar `application`
(`test_migrations_do_not_import_domain_or_application_code`), e por isso não gravaria auditoria.

**Descartado.** *Uma data migration por mudança*: sem auditoria, pelo motivo acima. *Tela de
administração*: pediria papel central, que não existe num modelo de uma unidade por operador.

**O arquivo inicial** tem uma entrada, o Cefor, com as linhas que o compositor imprime hoje
(FR-1111). As demais unidades entram quando o Ifes as fornecer.

## R-004 — `AutoridadeHabilitada`, e o primeiro uso como coluna

**Decisão.** O modelo guarda `unidade` (FK `PROTECT`), `cargo`, `nome`, `ato_de_nomeacao`,
`inicio_vigencia` e `fim_vigencia` (datas), quem cadastrou e quando, quem encerrou e quando, e
**`usada_em`**, o instante do primeiro ato praticado com ela.

`usada_em` é preenchida pelo comando de publicação, na mesma transação, sob a trava da linha
(R-005). A correção de nome, cargo e ato de nomeação é recusada quando ela não é nula (FR-1121,
`D-004`).

**Por quê uma coluna, e não uma consulta.** Saber se foi usada consultando `Publicacao` e
`PublicacaoResultado` faria `unidades` depender de `publicacoes` e `divulgacao`, quando a direção é
a contrária. E a coluna é o que o gatilho do banco lê (R-006).

**O nome do modelo.** `AutoridadeHabilitada`, e não `Autoridade`: o termo do domínio é *habilitada
na unidade* (`D-003`), e o teste que hoje proíbe um modelo `autoridade` é retirado junto com o
catálogo (R-012).

## R-005 — A verificação na publicação: trava, unidade, vigência

**Decisão.** Os três comandos — `publish_edital`, `publish_retification` e `publicar_resultado` —
recebem o **identificador** da autoridade e chamam um único serviço de `unidades`:

```
autoridade_para_o_ato(autoridade_id, *, unidade_codigo, data_do_ato) -> AutoridadeHabilitada
```

Ele faz `select_for_update` na linha, confere que pertence à Unidade do Edital, que
`inicio ≤ data_do_ato ≤ fim` (fim nulo é aberto), preenche `usada_em` se nula, e devolve a linha.
A data do ato é a da `054`: o `now` da transação, no fuso institucional (`shared/tempo.ZONA`).

**As recusas.** Autoridade inexistente **ou de outra unidade** → `422 autoridade_indisponivel`, com a
mesma mensagem: a de outra unidade é indistinguível de inexistente. Fora de vigência → `422
autoridade_fora_de_vigencia`, que nomeia o período. Nada é gravado em nenhum dos casos, porque a
verificação vem antes da Publicação na mesma transação.

**Concorrência.** Encerrar e corrigir travam a mesma linha. Encerramento confirmado entre a abertura
da tela e a publicação é visto pela publicação, que espera a trava e relê o fim (FR-1126). Correção
contra publicação simultânea: uma das duas espera; se a publicação vence, a correção encontra
`usada_em` preenchida e é recusada.

**Idempotência.** O payload reservado passa a conter o identificador, e não o dicionário. A repetição
com a mesma chave devolve a Publicação existente sem reverificar — o comportamento de hoje.

## R-006 — O banco recusa excluir e recusa reescrever o que já foi usado

**Decisão.** Cinco gatilhos, no padrão condicional da `requerimentos/0002` e da `editais/0013`,
numa migration de `unidades`:

- `unidade_nao_se_exclui` e `autoridade_nao_se_exclui`: `BEFORE DELETE`, recusa sempre;
- `unidade_codigo_imutavel`: `BEFORE UPDATE … WHEN (OLD.codigo <> NEW.codigo)`;
- `autoridade_unidade_imutavel`: `BEFORE UPDATE … WHEN (OLD.unidade_id IS DISTINCT FROM
  NEW.unidade_id)` — **sempre**, e não só depois do uso. A unidade de uma autoridade nunca muda
  (FR-1121); antes, só o comando a protegia, por não expor o campo;
- `autoridade_usada_imutavel`: `BEFORE UPDATE … WHEN (OLD.usada_em IS NOT NULL AND ((OLD.nome,
  OLD.cargo, OLD.ato_de_nomeacao, OLD.inicio_vigencia) IS DISTINCT FROM (NEW.…) OR
  NEW.fim_vigencia < (OLD.usada_em AT TIME ZONE 'America/Sao_Paulo')::date))`. A segunda condição
  impede, no banco, o encerramento retroativo a antes do primeiro ato praticado com ela (FR-1120).

**O que o banco não cobre do encerramento retroativo.** A regra inteira — fim ≥ dia do encerramento
— é do domínio, e é ela que a tela e o comando aplicam. O banco cobre o caso grave: um fim que faria
o registro dizer que a autoridade não estava vigente **no dia do primeiro ato** que praticou. Entre o
primeiro e o último ato, só o domínio protege: cobrir também esse intervalo pediria guardar a data do
último uso, e atualizar a linha a cada publicação. Aceito, porque o banco já recusa o pior caso e a
única porta que grava o fim é o comando. O fuso é escrito por extenso no SQL, copiado de
`shared/tempo.ZONA` e não importado (`test_migrations_do_not_import_domain_or_application_code`).

**Por quê só gatilho, e não privilégio.** As duas tabelas aceitam `UPDATE` — encerrar é `UPDATE` —,
e `TABELAS_APPEND_ONLY` revoga `UPDATE` e `DELETE` juntos. Criar uma segunda lista, "sem `DELETE`",
em `seguranca/papeis.py` daria a segunda camada, ao custo de mudar o provisionamento e o formato
`N de M` que o CLAUDE.md ensina a ler. Não há precedente no projeto de tabela mutável sem exclusão
protegida no banco; o mais próximo, `MembroComissao`, nem gatilho tem. Um gatilho é proporcional a
duas tabelas de cadastro; a lista fica registrada como alternativa se o Ifes pedir.

**Custo.** Os cinco nomes entram em `TRIGGERS_POR_APP["unidades"]`. As tabelas **não** entram em
`TABELAS_APPEND_ONLY`, e o `M` do provisionamento continua 34.

## R-007 — O que a Publicação congela

**Decisão.**

- **`Publicacao`** (Edital e Retificação) ganha `unidade_codigo`, `unidade_sigla`, `unidade_nome`,
  `unidade_cabecalho` (lista JSON de uma ou duas linhas) e `unidade_local`. Os quatro
  `signatory_*` continuam como estão, agora preenchidos a partir da `AutoridadeHabilitada`.
- **`PublicacaoResultado`** ganha as mesmas cinco colunas de unidade e `signatario_ato_de_nomeacao`.
- **`conteudo_publico` do Resultado** ganha, no `cabecalho`, `signatario_ato_de_nomeacao` e
  `unidade` (`{"sigla", "nome", "cabecalho"}`). É o precedente da `017`: o documento e a página do
  Resultado leem estes bytes, e é daí que vem a correspondência entre os dois (`conteudo.py`,
  `conteudo_divulgado`).

**Migration.** `ADD COLUMN` com padrão constante numa tabela append-only não reescreve linha nem
dispara gatilho de `UPDATE` (é a R-007 da `054`). Sem dado em produção, o padrão vazio só existe em
banco de demonstração antigo, que se re-semeia. `publicacoes` sobe de 9 para 10 e `divulgacao` de 3
para 4 nos guardiões, cada um com o parágrafo de justificativa.

**Descartado.** Uma FK da Publicação para a Unidade no lugar das colunas: a Publicação deixaria de
ser autocontida, e o nome do dia se perderia na primeira renomeação (FR-1129).

## R-008 — O compositor recebe a unidade como contexto do ato

**Decisão.** `ORGAO` e `LOCAL` deixam de existir em `pdf.py`. Fica a constante das linhas comuns,
`INSTITUICAO = ("Ministério da Educação", "Instituto Federal do Espírito Santo")`, e o compositor
recebe:

```
render_edital_pdf(snapshot, hash, *, unidade: UnidadeDoAto, modo=…, autoridade=…, data_do_ato=…, consolidacao=…)
UnidadeDoAto(cabecalho: tuple[str, ...], local: str)
```

`unidade` é **obrigatório nos dois modos**, porque a prévia também imprime o cabeçalho; o fecho com o
local continua só no publicado (`008`, FR-035). Sem padrão: um valor padrão seria o Cefor de novo,
escondido num argumento.

- **Edital e Retificação**: o comando monta `UnidadeDoAto` da Unidade do Edital, congela os mesmos
  valores na Publicação (R-007) e os passa ao compositor.
- **Prévia** (`views.previa_documento`): lê a Unidade registrada no momento.
- **Resultado**: `render_resultado_pdf(conteudo)` lê `conteudo["cabecalho"]["unidade"]`.
- **Comprovante**: `_dados_do_comprovante` lê as colunas `unidade_*` de
  `versao.source_publication` — a Publicação que originou a versão aceita pelo candidato
  (FR-1115), e não a mais recente. O mesmo
  valor substitui o `institution_scope.upper()` de `portal/views.py:144` e o texto fixo de
  `portal/comprovante.html`.

**A fixture de bytes.** `tests/contract/test_documento_publicado.py` passa a chamar o compositor com
a Unidade do Cefor, versionada em `tests/contract/fixtures/unidade_publicada.json`.
`documento_publicado_v1.pdf` **não** é refeito, e é essa a prova da FR-1114: se a composição a partir
da Unidade divergir em um byte do que as constantes produziam, o teste reprova.

## R-009 — A tela das autoridades

**Decisão.** Uma tela de topo, `/gestao/autoridades`, guardada pela permissão `autoridade:gerir`
com `require_authorization_base` — a recusa nomeia a permissão e a quem pedir, no padrão da `037`. O
acesso é pelo botão na Lista de Editais, sob `{% if pode_gerir_autoridades %}`, como a Visão
institucional da `040`. Uma view GET/POST que despacha por `acao` — `cadastrar`, `corrigir`,
`encerrar` —, como a da Comissão (`views.comissao`), com `chave_idempotencia` em cada formulário e
redirecionamento para `?feito=<acao>`.

**A permissão.** Constante `GERIR = "autoridade:gerir"` em `unidades/domain/nomes.py`, escrita por
extenso no papel `gestor` de `interface/identidade.py`, com o comentário do porquê, e conferida por um
teste no molde de `tests/authorization/test_visao_institucional.py`: está no Gestor e em nenhum outro
papel (`D-005`).

**Escopo.** A lista filtra pela Unidade do escopo do operador. Corrigir ou encerrar uma autoridade de
outra unidade responde 404, e a função entra no inventário de negativas da `033`, na classe
*"escopo institucional ∪ inexistente"*.

**Trilha.** Três operações novas — `CADASTRAR_AUTORIDADE`, `CORRIGIR_AUTORIDADE` e
`ENCERRAR_AUTORIDADE` — com rótulo em `OPERACOES` (`test_trilha_legivel.py`), e o mesmo para
`REGISTRAR_UNIDADE` e `ALTERAR_UNIDADE` do comando de sincronização. Sem estado nem revisão, os
eventos levam `new_state=""` e `new_revision=None`, como os da Comissão, e os valores anterior e
posterior em `detalhe`.

**Escopo sem Unidade registrada.** A tela diz que a unidade não está registrada e não oferece
cadastro.

## R-010 — A escolha nas telas de publicação

**Decisão.** As quatro telas que hoje iteram `autoridades.CATALOGO` — `confirmar.html`,
`retificacao_confirmar.html`, `previa_de_publicacao.html` e `marco.html` — e a conferência
`marco_conferir.html` passam a receber `autoridades_vigentes(unidade_codigo, data)`, um selector de
`unidades`. O valor de cada opção é o identificador (UUID). A FR-1117 proíbe digitá-lo e exibi-lo, e
o atributo `value` de uma opção não é nenhum dos dois. A Revisão do marco (`marco_conferir.html`)
mostra a autoridade relendo-a pelo identificador.

**O texto da opção** sai de uma função só, `rotulo_da_autoridade(autoridade)`: `quem_assinou(nome,
cargo)`, e o ato de nomeação depois de um ponto médio quando houver (UX-148). `quem_assinou` muda de
`publicacoes/domain/autoridades.py` para `unidades/domain/`, e o resto do arquivo é apagado.

**Sem autoridade vigente** (FR-1127): o seletor dá lugar à frase *"Nenhuma autoridade vigente para
<Unidade> hoje. Quem tem a permissão de gerir autoridades da unidade as cadastra."*, no formato que
`test_gramatica_das_portas.py` aceita, e o botão de confirmar fica desabilitado. A recusa continua
sendo do domínio (R-005).

## R-011 — Criar Processo ou Edital exige Unidade ativa

**Decisão.** `create_process_with_first_edital` e `add_edital` (`processos/application/commands.py`)
chamam `unidades.application.selectors.unidade_ativa(actor.institution_scope)` antes de criar, e
recusam com `422 unidade_nao_registrada` quando ela não existe ou está desativada (FR-1110). Os atos
seguintes sobre o que já existe não consultam a situação.

**Medido antes de decidir** (memória *regra impeditiva quebra a suíte em bloco*): 67 arquivos de
teste criam Processo pela API, todos com escopo `cefor` menos um; 11 criam pelo ORM, que não passa
pela regra. O risco é a Unidade `cefor` sumir no meio da suíte (R-012), e não a regra.

## R-012 — A suíte: uma fixture que registra o Cefor e as autoridades de teste

**O problema.** 2.599 casos transacionais truncam todas as tabelas ao terminar. Qualquer dado que
uma migration crie some depois do primeiro deles, e a suíte passaria a falhar conforme a ordem.

**Decisão.** Uma fixture `autouse` em `tests/conftest.py`, ativa só quando o caso tem banco
(marcador `django_db` ou as fixtures `db`/`transactional_db`), garante com `get_or_create`:

- a Unidade `cefor`, com os valores do `unidades.json`;
- `AUTORIDADE_DA_SUITE`, com o identificador que `tests/fixtures/publicacao.SIGNATORY` já usa
  (`…000000000601`), nome `Diretora` e cargo `Diretora-Geral` — os valores que os testes de Edital
  já conferem;
- `AUTORIDADE_DO_RESULTADO`, com o cargo que o `diretoria-cefor` do catálogo tem hoje e sem nome — o
  que os testes de Resultado já conferem.

Os identificadores vivem em `tests/fixtures/autoridades.py`. **A mudança se concentra nos helpers.**
`SIGNATORY` vira `{"authorityId": …}`; o padrão `autoridade="diretoria-cefor"` de
`tests/fixtures/divulgacao.publicar_o_ato` vira o identificador de `AUTORIDADE_DO_RESULTADO`. Assim
os 130 arquivos que publicam por `publish_original` e os 35 que publicam resultado não mudam. Mudam à
mão:

- ~20 passagens explícitas de `"diretoria-cefor"`/`"reitoria"` (lista no relatório de 06/10);
- os ~10 dicionários de signatário escritos por extenso;
- as duas chaves negativas (`"prefeitura-de-outro-lugar"`, `"prefeitura-alheia"`), que viram UUID
  aleatório;
- as ~33 chamadas diretas a `render_edital_pdf`/`render_resultado_pdf`, que passam a dar a Unidade
  — por uma constante `UNIDADE_DA_SUITE` em `tests/fixtures/autoridades.py`;
- `tests/interface/test_autoridades.py`, que prende o catálogo e proíbe o modelo: é **substituído**
  pelos testes da 060, e não emendado;
- `test_fecho_e_normas_da_054.py`, que confere o catálogo vazio de nomes: as asserções sobre o
  catálogo saem, as sobre o fecho ficam.

**Descartado.** Criar a Unidade e as autoridades numa data migration e ligar `serialized_rollback`:
custaria serializar o banco em cada caso transacional, e a suíte já leva de 12 a 18 minutos.

## R-013 — `seed_demo` e o registro inicial de autoridades

**Decisão.** `seed_demo` chama `sincronizar_unidades` e cadastra pelo comando de aplicação, com um
Gestor, as autoridades de que precisa. O `SIGNATARIO` livre (`…0000000000a1`, *Reitora do IFES*) e o
`autoridade="diretoria-cefor"` passam a usar os identificadores devolvidos.

**As três autoridades do catálogo** (FR-1124) — Reitora, Pró-Reitor de Ensino e Diretora-Geral do
Cefor, só com cargo — são cadastradas na implantação pelo Gestor do Cefor, pela tela. Elas **não**
entram no `unidades.json`: o arquivo declara unidades, e autoridade é dado operacional (`D-005`). O
quickstart traz o roteiro. Os identificadores fictícios `1111…`, `2222…` e `3333…` desaparecem com o
catálogo (FR-1117).

## R-014 — Contratos de API

**Decisão.** `SignatorySerializer` (`publicacoes/api/serializers.py`) passa a aceitar
**somente** `authorityId`, e recusa as chaves `name`, `role` e `appointment` com `400`. Aceitá-las e
ignorá-las seria um contrato que mente: quem as envia acredita que valem. O `openapi.yaml` da `001`
(`SignatorySnapshot`) é emendado; `SignatarioRegistrado`, a saída, ganha `unit`. A consulta pública
(`PublicacaoDetalheSerializer`) acrescenta `unit: {code, acronym, name}` (FR-1131).

## R-015 — Emendas a specs anteriores

No padrão da R-017 da `054`, cada requisito alcançado recebe uma nota no próprio texto:

- `007`, FR-039 — *revogada pela `060` (FR-1124)*;
- `054`, FR-989 — *local emendado pela `060` (FR-1113)*;
- `054`, decisão 005 — *o catálogo deixa de existir; nome e ato de nomeação passam ao registro de
  autoridades (`060`, FR-1116)*;
- `017`, FR-029 — *o ato de nomeação passa a ser registrado (`060`, FR-1128)*.

## R-016 — O que fica registrado como pendência

Na seção *Fora de escopo* da spec, e no `doc/` quando a 060 fechar: a marca *"Cefor/Ifes"* (títulos,
topo das telas, `404.html`, assuntos de e-mail, `shared/api/operacional.py`, os tipos de problema
`processo-seletivo.cefor/errors`), as frases *"a quem administra o sistema no Cefor"*, a vitrine do
portal sem a unidade de cada seleção, e o seletor de identidade que só oferece o escopo padrão
(`views.identificar`, `ESCOPO_PADRAO`) — este último limita a demonstração a uma unidade, e não o
produto.
