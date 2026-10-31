# Revisão arquitetural da operação multiunidade — 30/10/2026

**O que é.** Revisão crítica, sem implementação, de se o GPS está pronto para operar com os campi e
a Reitoria como unidades, e do que rever antes de expandir. Responde às sete questões do pedido de
30/10 e termina numa recomendação para uma spec futura.

**Base examinada.**

- a `main` em `77f35fd3` (depois do #347);
- as specs [`060`](../specs/060-unidades-e-autoridades/), [`106`](../specs/106-identidade-institucional-preparada/)
  e [`107`](../specs/107-gestao-de-acessos/);
- o PR **#349** (spec `109`, *identidade institucional preparada para mais de uma unidade*), aberto,
  em `f9236854` — o mais recente sobre identificação institucional e eliminação do Cefor fixo;
- o PR **#348** (spec `108`, *trilha da unidade*), aberto, em `c4639ab9`, onde ele muda a resposta;
- a [auditoria de 30/10](auditoria-administracao-institucional-2026-10-30.md) e o
  [estudo de identidade e acessos](estudo-identidade-e-acessos-2026-10-30.md).

> **Atualização de 31/10/2026.** A recomendação virou a spec
> [`110`](../specs/110-cadastro-de-unidades/spec.md), com as decisões de produto aprovadas pelo
> usuário. Diferenças em relação ao que está escrito abaixo, depois da revisão final da spec no
> mesmo dia: a semente se aplica **só a registro vazio**, e não a "código ausente" — inserir por
> código ausente mantinha o arquivo como segundo caminho de criação (decisão um do research da
> `110`); a permissão vai ao papel institucional existente, renomeado Administrador institucional,
> com verificação de quem já o tem antes do deploy (decisão dois); o nome anterior do comando fica como apelido (decisão três); a
> validação por pessoas antes do SSO usa um adaptador de homologação só no código de teste
> (decisões dezessete e dezoito); e a entrega é em três PRs, com a troca da fonte junto das telas
> (decisão dezenove).

Referências a código são da `main`, salvo quando marcadas *(#349)*, e os caminhos sem prefixo
são relativos a `backend/processo_seletivo/`. Nada aqui foi executado contra
banco: é leitura de código e de spec. Onde uma afirmação depende de teste, ele é citado.

---

## 1. Resumo

**A arquitetura de isolamento está certa e não precisa ser refeita.** O escopo textual
`institution_scope` funciona como chave natural estável porque três garantias o sustentam: o código
da Unidade não muda (gatilho `unidade_codigo_imutavel`), a Unidade não se exclui (gatilho
`unidade_nao_se_exclui`), e todo ponto que cria Processo, Edital ou vínculo confere que a unidade
existe e está ativa. A publicação congela nome, sigla, cabeçalho e local da unidade em colunas
próprias, de modo que o documento histórico não depende do registro atual. Trocar o texto por chave
estrangeira em todo lugar não compraria garantia proporcional ao custo — ver §5.

**O que está errado é quem escreve o registro de Unidades, e não o registro.** Desde a `106` e a
`107` o sistema tem o que a `060` dizia faltar para cadastrar unidade pela aplicação — um papel
central, com trilha por pessoa. A razão escrita para o arquivo (*"Tela de administração: pediria
papel central, que não existe"*, R-003) caducou. E o arquivo hoje tem dois defeitos concretos para
quem quer operar várias unidades:

1. **entrar um campus é commit, PR e deploy** — o critério do pedido, "sem alteração específica de
   código para cada campus", não se cumpre;
2. **o banco não pode divergir do arquivo**: a sincronização roda em toda subida do container
   (`scripts/docker/entrypoint.sh:54`, sob `set -eu`) e em todo `ps-migrar`, sobrescreve o que
   mudou e recusa unidade ausente do arquivo. Uma correção feita no banco é desfeita no deploy
   seguinte, com evento `ALTERAR_UNIDADE` atribuído à `implantacao`; uma unidade criada no banco
   **impede a subida** do container até alguém a copiar para o JSON.

**Recomendação.** O banco passa a ser a fonte oficial; o `unidades.json` vira semente de instalação,
que só insere o código que falta e nunca altera; o cadastro passa à aplicação, no nível
institucional, com permissão própria e trilha por pessoa no escopo da unidade. É a menor mudança que
cumpre o critério: nenhuma tabela nova, nenhuma migração de dado, nenhuma chave estrangeira nova —
os leitores já leem o banco, e só o caminho de escrita muda. A integridade pede um acréscimo só, no
molde da `060`: um gatilho que torne imutável o escopo de Processo e Edital, hoje alterável por um
`update()` sem que nada recuse (§5.1).

**O resto do que falta para duas unidades operarem é decisão, não arquitetura.** Com a `109`
mergeada, nenhuma regra de negócio, autorização ou numeração depende da string `cefor`. Ficam: as
perguntas P-1, P-2 e P-7 da `109` (marca e canal das superfícies sem unidade), quem audita o nível
institucional (P1 da `108`), o papel da Reitoria (unidade emissora, supervisão transversal ou as
duas), e a conexão real com o provedor do Ifes, que bloqueia a produção inteira e não só a
multiunidade.

---

## 2. Diagnóstico da arquitetura atual

### 2.1 O registro de Unidades (060)

| Peça | Onde | O que garante |
|---|---|---|
| `Unidade` — `codigo` único, `sigla`, `nome`, `cabecalho` (1–2 linhas), `local`, `ativa`; *(#349)* `atendimento` | `unidades/models.py:24-50` | o que o documento oficial diz da unidade |
| `AutoridadeHabilitada` — FK `PROTECT` para `Unidade`, vigência, `usada_em` | `unidades/models.py:53-100` | quem pode assinar os atos da unidade numa data |
| Cinco gatilhos: Unidade não se exclui, código não muda, autoridade não se exclui, unidade da autoridade não muda, autoridade usada não se reescreve | `unidades/migrations/0002_nada_se_exclui.py:39-97` | a referência textual e o `signatory_id` congelado nunca apontam para o nada |
| `unidades.json` + `sincronizar_unidades` — arquivo inteiro validado, tudo ou nada, trilha com ator `implantacao` | `unidades/application/sincronizacao.py:47-152` | o único caminho de escrita da Unidade |
| `exigir_unidade(codigo, ativa=True)` | `unidades/application/selectors.py:15-36` | Processo, Edital e vínculo só nascem em unidade registrada e ativa |
| colunas `unidade_*` e `signatory_*` na `Publicacao` e na `PublicacaoResultado` | `publicacoes/models.py:75-79`; `divulgacao/models.py:80-84` | o ato guarda a unidade do dia; renomear não reescreve o publicado (FR-1129) |

A sincronização é chamada em três lugares: `make preparar` (`backend/Makefile:105`), o
`entrypoint.sh` do compose (`scripts/docker/entrypoint.sh:54`) e o `ps-migrar` do guia de produção
(`doc/implantacao-em-producao-ubuntu.md:714`). E ela é também o único ponto que cria os três modelos
iniciais de aviso de cada unidade (`sincronizar_unidades.py:39-41` →
`avisos/application/modelos.py:206`).

### 2.2 Identidade e acessos (106, 107)

| Peça | Onde | O que garante |
|---|---|---|
| A pessoa é o `auth.User`, `username = pessoa-<uuid4>`, imutável; `IdentidadeExterna` localiza pelo par provedor × identificador | `seguranca/models.py:32-58`; `seguranca/autenticacao.py:117-160` | a pessoa não tem unidade; atua onde tem vínculo |
| `Vinculo(pessoa, escopo, papel)` e `RevogacaoDeVinculo`, append-only nas duas camadas | `seguranca/models.py:61-96`; `seguranca/papeis.py` (`TABELAS_APPEND_ONLY`) | "quem tinha o papel X na unidade Y na data D" |
| `Actor(subject, institution_scope, permissions)` recalculado por requisição da **unidade ativa** | `seguranca/domain.py`; `interface/identidade.py:379-505` | trocar de unidade não carrega permissão de uma a outra |
| Três níveis: papéis operacionais (por `acesso:gerir` na unidade) → `administrador-de-acessos` (por `acesso:administrar` no escopo `institucional`) → `administrador-institucional` (só por comando de implantação) | `seguranca/acessos.py:14-44`; `seguranca/application/acessos.py:163-178` | ninguém concede a si mesmo, e o institucional não conduz certame |
| Concessão confere unidade registrada e ativa, e recusa o escopo `institucional` para papel de unidade | `seguranca/application/acessos.py:151-160` | o texto do escopo nunca vem livre do usuário |

**O administrador institucional não tem poder sobre unidade nenhuma.** O catálogo lhe dá só
`acesso:administrar` (`seguranca/acessos.py:41-44`), e o comentário diz por quê: *um global com poder
operacional seria o superusuário que o estudo recusou*. Hoje **ninguém** tem permissão sobre o
registro de Unidades — quem escreve é o deploy.

### 2.3 O escopo nos dados

| Onde | Como se liga à unidade | Avaliação |
|---|---|---|
| `ProcessoSeletivo.institution_scope` | texto, do ator, conferido por `exigir_unidade` (`processos/application/commands.py:24,31-32`) | raiz do certame |
| `Edital.institution_scope` | texto, do ator, **depois** de ler o Processo com o mesmo escopo (`commands.py:86-88,101-105`) | coerente por construção; nenhum outro `Edital.objects.create` no código de produção |
| `Edital` → `Processo` | FK `PROTECT` | |
| `AutoridadeHabilitada.unidade` | FK `PROTECT` | a única FK para `Unidade` |
| `Vinculo.escopo` | texto; inclui o escopo `institucional`, que não é unidade | FK impossível sem unidade fictícia |
| `RegistroAuditoria.institution_scope`, `IdempotencyRecord.institution_scope` | texto, do ator (`auditoria/application.py:29`) | a trilha não pode depender do registro que audita |
| `ModeloDeAviso`, `Aviso` (`avisos/models.py:56,99`) | texto | ver §5 |
| `Publicacao.unidade_*`, `PublicacaoResultado.unidade_*` | cópia congelada no ato | correto por desenho (R-007 da `060`) |

O resto dos dados chega à unidade por FK: a maior parte das apps (avaliações, classificação,
convocação, divulgação, inscrições, matrículas, ocupação, publicações, recursos, resultados,
sorteios, editais, `duvidas.TrocaDoPiloto`) aponta para o Edital, direto ou pela Inscrição; os
membros de comissão apontam para o Processo (`comissoes/models.py:33`), e a alocação, para o membro
e para o Edital (`:80-81`). O que não chega a unidade nenhuma é global por natureza: a identidade
do candidato, a base de CEP, a ocorrência da fonte do sorteio e o artefato anexo, que só se alcança
pelo `AnexoEdital`.

### 2.4 Isolamento nas consultas

Varredura das leituras da gestão, das APIs e dos *selectors*:

- **Filtram pela unidade do ator, direto ou por FK**: os carregadores de Processo e Edital
  (`processos/application/selectors.py:18,45`; `interface/views.py:3081,5366,7094,8732`), a agenda
  (`interface/agenda.py:695-696`), a visão geral (`interface/visao_geral.py:360,422`), os
  relatórios (`interface/relatorio.py:84,265`; `interface/relatorio_consolidado.py:246,250`), os
  avisos (`interface/avisos.py:54,77`), a trilha (`auditoria/selectors.py:61`), as comissões
  (`comissoes/application/selectors.py:36,215`), os acessos (`interface/acessos.py:348`) e o
  reaproveitamento de Edital (`editais/application/reaproveitamento.py:118,284`).
- **Não filtram, mas recebem o Edital ou o Processo já carregado com filtro**: os *selectors* de
  classificação, ocupação, recursos, convocação e divulgação, e as buscas na trilha por
  `aggregate_id`. A segurança é de quem chama — é o padrão do projeto, e não um defeito.
- **Um ponto frágil, sem vazamento**: `_para_a_proxima` (`interface/views.py:6873`) lê a Inscrição
  pelo `pk` sem escopo para pôr o protocolo na mensagem. Só roda depois de `concluir` ter aceitado
  aquela inscrição naquele Edital, de modo que o id já foi conferido; mas a conferência é implícita.
- **Portal**: a vitrine reúne as unidades e diz a sigla de cada seleção (`portal/views.py:346-376`),
  como a `072` decidiu. Nenhuma mistura indevida encontrada.

**Cobertura de teste.** 56 arquivos usam um segundo escopo literal (`outra-unidade`, `campus-a`,
`serra` e outros), cobrindo avisos, comissão e mesa, classificação, publicação de resultado,
reaproveitamento, agenda, supervisão, sorteios, convocação, matrículas, relatórios, trilha,
dúvidas, autoridades e vínculos. **Sem teste de segunda unidade**: ocupação e acréscimo de vagas,
decisão e admissibilidade de recurso, requerimentos na gestão, condução do marco e do corte, e a API
`/api/v1/admin`. Nenhum desses lê por id sem passar por um Edital filtrado, de modo que a falta é de
prova, e não indício de defeito — mas é onde um teste de isolamento renderia, se a spec futura
quiser um.

---

## 3. Matriz de capacidades e lacunas

Legenda: **✓** existe e basta · **◐** existe com limitação · **✗** não existe · **D** depende de
decisão institucional, e não de código.

| # | Capacidade | Estado | Evidência | Lacuna efetiva |
|---|---|---|---|---|
| C-1 | Registrar unidade | ◐ | `sincronizacao.py:99-130` | exige commit e deploy; autor na trilha é `implantacao` |
| C-2 | Alterar nome, sigla, cabeçalho, local | ◐ | `sincronizacao.py:131-151` | idem; e o banco não pode divergir (§6) |
| C-3 | Desativar unidade sem perder o histórico | ✓ | `"ativa": false`; `selectors.py:29-35` | o certame em curso termina; nada novo nasce |
| C-4 | Código imutável, unidade nunca excluída | ✓ | `unidades/0002` | só gatilho, sem privilégio ausente — escolha documentada |
| C-5 | Autoridades por unidade, conferidas no ato | ✓ | `unidades/application/autoridades.py:29-81` | — |
| C-6 | Documento histórico independente do registro atual | ✓ | colunas `unidade_*`; `contexto_do_ato.py:89` | — |
| C-7 | Numeração de Edital por unidade | ✓ | `uq_edital_scope_number_year` (`processos/models.py:121`) | — |
| C-8 | Acesso por unidade, com administrador de acessos da unidade | ✓ | `seguranca/application/acessos.py:191-263` | — |
| C-9 | Pessoa em várias unidades, sem acúmulo de permissão | ✓ | `trocar_unidade` (`interface/identidade.py:479-505`) | — |
| C-10 | Administrar o registro de Unidades pela aplicação | ✗ | nenhuma permissão sobre `Unidade` | **a lacuna central** |
| C-11 | Marca, assinatura e canal da unidade nas telas e mensagens | ◐ *(#349)* | `unidades/application/identificacao.py` *(#349)* | sem merge; P-1, P-2, P-7 provisórias |
| C-12 | Modelos iniciais de aviso para unidade nova | ◐ | `avisos/application/modelos.py:206` | só a sincronização os cria |
| C-13 | Trilha legível por unidade | ◐ *(#348)* | `GET /gestao/trilha-da-unidade` *(#348)* | sem merge; quem audita o institucional é P1 da `108` |
| C-14 | Remetente e servidor de correio por unidade | ✗ / D | `EMAIL_*` global; descartado na `109` (D-003) | decisão: basta assinatura + canal da unidade? |
| C-15 | Entrada institucional real (SSO do Ifes) | ✗ / D | `doc/ativacao-do-sso-institucional.md` | D-1 e D-2 do estudo; bloqueia toda a produção |
| C-16 | Supervisão transversal (Reitoria lê várias unidades) | ✗ / D | `Actor` tem um escopo só, por desenho | decisão: é requisito? |
| C-17 | Edital de mais de uma unidade | ✗ / D | `Edital.institution_scope` único | decisão; provavelmente fora |
| C-18 | Demonstração com duas unidades | ◐ | `ESCOPO_PADRAO = "cefor"` (`interface/identidade.py:23`) | só a homologação; a suíte já usa `campus-a` |
| C-19 | Exportação de matrícula de outro campus | D | `ABA = "Import_ModeloCefor"` (`matriculas/domain/nomes.py:95`) | P-3 da `109`: contrato externo |

---

## 4. Cadastro: arquivo versionado × banco administrado pela aplicação

### 4.1 O que a `060` decidiu, e o que mudou desde então

A R-003 escolheu o arquivo por três razões: ~26 unidades que mudam em anos; as linhas do cabeçalho
são decisão editorial de documento oficial, que se revisa melhor em diff; e a tela pediria um papel
central que não existia. Descartou a data migration porque ela não grava trilha.

As duas primeiras continuam verdadeiras. **A terceira caducou** com a `106` e a `107`: há papel
institucional, concedido só pela implantação, com trilha por pessoa, sessão real e tela. E surgiram
dois fatos que a `060` não tinha:

- a `109` acrescentou o canal de atendimento ao registro, e o próprio research dela recusou copiar o
  canal do Cefor para o arquivo porque *"seria inventar o dado ou publicá-lo no diff"*
  (`specs/109-identidade-multiunidade/research.md`, D-003) *(#349)*. Um dado operacional de contato
  num arquivo de repositório é o primeiro sinal de que o arquivo está guardando o que não é dele;
- a sincronização passou a rodar a cada subida do container, o que torna o arquivo não só a origem,
  mas um **sobrescritor periódico** do banco.

### 4.2 Comparação

| Critério | `unidades.json` + sincronização (hoje) | Banco administrado pela aplicação |
|---|---|---|
| **Governança** | quem decide é quem aprova o PR — a equipe de desenvolvimento executa uma decisão da Reitoria; entrar um campus é deploy | quem decide é quem tem a permissão institucional; entrar um campus é ato no sistema, no dia |
| **Rastreabilidade** | trilha com `antes`/`depois`, mas o autor é `implantacao`; o autor real está no `git log`, fora do sistema (M-09 da auditoria) | trilha com a pessoa, o motivo e `antes`/`depois`, numa fonte só |
| **Segurança** | nenhum caminho de escrita em execução: a menor superfície possível. Mas quem tem acesso ao repositório altera o cabeçalho de todo documento futuro | um caminho de escrita novo, protegido por permissão no escopo institucional, CSRF e CSP como o resto; o código continua imutável por gatilho |
| **Revisão editorial do cabeçalho** | diff revisado | prévia do cabeçalho como o compositor o imprime, e confirmação; o publicado não muda de qualquer forma (C-6) |
| **Consistência** | duas fontes: o banco diverge do arquivo até o próximo deploy, e o deploy reverte o banco | uma fonte |
| **Manutenção** | validador, comando, três chamadores e o acoplamento com os modelos de aviso | o validador migra para o domínio; o comando vira semente; uma tela e três casos de uso |
| **Esforço** | zero | uma spec pequena (§8): uma permissão, três casos de uso, uma tela, a semente, testes |
| **Critério do pedido** | não cumpre — cada campus é alteração do repositório | cumpre |

**A variante intermediária**, comandos de gerenciamento que gravam no banco com a pessoa como ator
(no molde de `conceder_administracao_institucional`), resolve a fonte única e a autoria, mas mantém a
TI como executora e o acesso ao servidor como requisito. Só vale se a resposta à D-4 for "a TI
administra o registro". Ela custa quase o mesmo que a tela — o que custa é a regra, e não o
formulário.

### 4.3 Recomendação sobre a fonte oficial

**O banco é a fonte oficial.** O arquivo deixa de ser fonte e passa a ser **semente de instalação**:

- o comando passa a **só inserir** o código que ainda não existe no banco, e nunca altera nem recusa
  ausência — semear um banco novo (desenvolvimento, teste, primeira instalação) continua sendo um
  passo do `make preparar`;
- mudar a semente depois de instalada não tem efeito, e o comando diz isso na saída (`Unidades: N
  semeadas, M já registradas`), para que ninguém edite o arquivo esperando ver a mudança;
- o arquivo fica só com o Cefor. As outras unidades entram pela tela, quando o Ifes decidir — sem
  cadastro retroativo nem lista prévia de 26 entradas.

**Não recomendo** apagar o arquivo: a suíte e o `seed_demo` precisam de uma unidade sem tela, e a
fixture `autouse` já registra o Cefor sem ele. Também **não recomendo** manter a sincronização
completa ao lado da tela, nem em modo "só avisa a divergência": qualquer comparação com o arquivo
devolve a ele o papel de fonte.

---

## 5. Integridade dos relacionamentos

### 5.1 O escopo textual é seguro pelo que o cerca

`institution_scope` é texto, mas não é texto livre: em nenhum caminho de produção ele vem do pedido
do usuário. Vem do `Actor`, cuja unidade vem do vínculo, cuja concessão confere o registro. Os riscos
clássicos da referência textual, um por um:

| Risco | Situação | Por quê |
|---|---|---|
| Referência para unidade inexistente | coberto na aplicação | `exigir_unidade` na criação de Processo, Edital e vínculo |
| Unidade excluída deixando órfãos | impossível | gatilho `unidade_nao_se_exclui` |
| Código renomeado deixando órfãos | impossível | gatilho `unidade_codigo_imutavel` |
| Grafia divergente (`Cefor` × `cefor`) | coberto | o validador exige minúsculas, dígitos e hífen (`sincronizacao.py:31`); o escopo nunca é digitado |
| Edital com escopo diferente do Processo | coberto por construção | os dois recebem o escopo do ator, e o Processo é lido com ele |
| Escopo `institucional` tomado por unidade | coberto | o validador o recusa (`sincronizacao.py:55-59`) |
| Aviso, Publicação e alocação com unidade diferente da do Edital | coberto por construção | copiados do Edital no ato (`avisos/application/confirmar.py:89`; `contexto_do_ato.py:89`; `comissoes/application/alocacao.py:44-47`) |
| Inserção direta no banco com escopo qualquer | **não coberto** | nenhuma FK nem gatilho confere existência |
| **Escopo de Processo ou Edital alterado depois de criado** | **não coberto** | nenhum caminho da aplicação o altera, mas nada o impede: `tests/integration/agenda/test_fonte.py:197` o faz com um `update()` |

**O risco que vale tratar é o último.** A inserção direta exige a role de runtime e não é o que esta
revisão deve priorizar. Já o escopo mutável é o que um `QuerySet.update()` distraído desfaz — o
argumento exato que a `060` usou para pôr gatilho na unidade da autoridade (`unidades/0002`). Um
Edital que mudasse de unidade levaria consigo inscrições, resultados e trilha, e ficaria com
publicações que congelaram outra unidade no cabeçalho. A proteção proporcional é a mesma da `060`:
**um gatilho que recuse mudar `institution_scope` em `ProcessoSeletivo` e `Edital`**, sem FK. O
custo é ajustar o teste da agenda, que passaria a criar o Edital da outra unidade por um ator dela.

### 5.2 Onde FK compraria algo, e onde não

| Relação | Recomendação | Por quê |
|---|---|---|
| `AutoridadeHabilitada` → `Unidade` | manter a FK | a autoridade é da unidade e o gatilho impede trocá-la |
| `Publicacao.unidade_*` | **nunca** FK | o ato é autocontido; a FK traria o nome de hoje ao documento de ontem |
| `RegistroAuditoria`, `IdempotencyRecord` | texto | a trilha guarda escopos que não são unidade (`institucional`) e não pode falhar porque o registro falhou |
| `Vinculo.escopo` | texto | o escopo `institucional` não é unidade |
| `ProcessoSeletivo`, `Edital`, avisos | texto, como está, com o escopo de Processo e Edital imutável por gatilho | a FK por `to_field="codigo"` só acrescentaria a conferência de existência na inserção direta, ao custo de registrar a unidade alheia em todo teste de isolamento (R-002 da `060`) |
| `User` | sem unidade | a pessoa atua em várias; a unidade é do vínculo |

**Se a conferência de existência no banco for desejada mesmo assim**, a forma proporcional é uma
restrição só, em `ProcessoSeletivo`, a raiz: o Edital herda do Processo, e o resto herda do Edital.
Não recomendo fazê-la agora — o gatilho de imutabilidade cobre o caso que tem causa plausível.

### 5.3 O que muda com o cadastro pela aplicação

Duas garantias que hoje são do validador do arquivo precisam passar ao domínio: o formato do código
e a recusa do `institucional`. E a trilha precisa ser gravada **no escopo da unidade alterada**, e
não no `institucional` do ator — a sincronização já faz isso (`Actor(IMPLANTACAO, codigo)`,
`sincronizacao.py:114`), e é o que faz a trilha da `108` mostrar a mudança ao auditor da unidade.

---

## 6. Fonte única de verdade: como impedir que o arquivo sobrescreva o banco

Hoje a sobrescrita é garantida, não eventual:

1. `sincronizar` compara cada campo do arquivo com o banco e grava o do arquivo
   (`sincronizacao.py:131-151`);
2. recusa qualquer código do banco ausente do arquivo (`sincronizacao.py:105-112`) e levanta
   `CommandError`;
3. roda em toda subida do container, sob `set -eu` (`entrypoint.sh:11,54`), e em todo `ps-migrar`.

O mecanismo para impedi-lo é a mudança de semântica da §4.3, e nada além dela: **semear só insere
por código ausente**. Com isso:

- uma unidade criada pela tela não está no arquivo, e o comando não a vê como retirada;
- uma unidade alterada pela tela está no arquivo com o valor antigo, e o comando não a toca;
- um banco vazio recebe o Cefor, como hoje.

Os modelos iniciais de aviso deixam de depender do comando: o caso de uso que registra a unidade os
cria na mesma transação, e o `garantir_modelos_iniciais` continua idempotente para quem já existe.

Não é preciso marcador de origem nem versão no registro: depois da troca, o banco é a única fonte
que alguém escreve.

---

## 7. Compatibilidade com o que existe

| O que existe | Efeito da transição | Por quê |
|---|---|---|
| A linha do Cefor no banco | nenhum | os leitores (`selectors.py`, `identificacao.py`, `contexto_do_ato.py`) já leem o banco; nenhuma migração de dado |
| Códigos | nenhum | o gatilho continua; a tela não expõe o código depois de criado |
| Publicações e resultados publicados | nenhum | leem as colunas `unidade_*` congeladas |
| Autoridades e `signatory_id` congelados | nenhum | a FK e os gatilhos não mudam |
| Eventos `REGISTRAR_UNIDADE` e `ALTERAR_UNIDADE` de `implantacao` | ficam | são história; os novos terão a pessoa. O tipo de agregado e as operações podem ser os mesmos, o que mantém a `108` lendo os dois |
| `make preparar`, `entrypoint.sh`, `ps-migrar` | continuam chamando o comando | só a semântica muda; a linha de saída muda de forma — e o CLAUDE.md e o guia de produção que a ensinam a ler precisam acompanhar |
| `test_sincronizacao.py`, `test_registro.py` | reescritos | fixam o comportamento que se quer mudar |
| A fixture `autouse` que registra o Cefor | fica | é independente do arquivo |
| `garantir_modelos_iniciais` | fica, chamado também pelo registro | idempotente |
| Tabelas append-only (`M` = 46) | não muda | `Unidade` continua mutável e fora da lista, como hoje |

**Dois cuidados de transição.** (a) Se a `109` entrar antes, o campo `atendimento` já está no
arquivo e no comando; a semente deve aceitá-lo como opcional, e a tela, oferecê-lo. (b) A ordem dos
merges: esta mudança não depende da `108`, mas a `108` precisa ler os eventos novos — o que acontece
de graça se o agregado e as operações forem os mesmos.

---

## 8. O menor conjunto de melhorias

Em ordem. Os quatro primeiros são código; os outros são decisão que o código já acomoda.

1. **Merge da `109` (#349) e da `108` (#348)**, ou a decisão de não fazê-lo. São o que falta de
   identificação e de trilha; esta revisão não acha nada nelas a refazer antes.
2. **Cadastro de Unidades pela aplicação** — a spec do §9.
3. **Semente no lugar da sincronização** — parte da mesma spec, porque sem ela a tela é desfeita no
   deploy seguinte.
4. **Escopo de Processo e Edital imutável por gatilho** (§5.1) — separável, e pode ir na mesma spec
   ou sozinho; não tem pergunta ao usuário.
5. **Responder P-1, P-2 e P-7 da `109`** antes de a segunda unidade ficar ativa: a regra provisória
   (uma unidade ativa, ela; várias, só "Ifes") muda o que o candidato lê no dia em que a segunda
   entrar, por efeito de dado. Não é defeito, mas é visível.
6. **Responder P1 da `108`** (quem audita o nível institucional) antes de a tela de unidades
   existir: ela acrescenta ao nível institucional um poder que muda o cabeçalho de todo documento
   futuro de uma unidade.
7. **Decidir o papel da Reitoria** (C-16): se ela é unidade emissora, basta registrá-la; se
   supervisiona os campi, a leitura transversal é feature própria, e não ajuste do `Actor`.

Fica **fora** do conjunto mínimo, por não ser necessário ao critério: FK nova, versionamento da
Unidade, correio por unidade, Edital de várias unidades, seletor de demonstração com duas unidades.

---

## 9. Recomendações para a spec futura

**Título sugerido:** *Registro de Unidades administrado pela aplicação*.

**Sem sobreposição com:** a `060` (o modelo, os gatilhos, as autoridades e o congelamento no ato
ficam como estão), a `106`/`107` (o modelo de vínculos não muda; só o catálogo de permissões ganha
uma), a `108` (a trilha lê o que esta grava), a `109` (a identificação lê o que esta grava).

**Escopo.**

- uma permissão nova, `unidade:administrar`, conferida no escopo `institucional`;
- três casos de uso — registrar, alterar (sigla, nome, cabeçalho, local, atendimento) e
  ativar/desativar —, com motivo obrigatório, trava da linha e trilha no escopo da unidade, com
  `antes`/`depois`;
- o validador do arquivo levado ao domínio, inclusive o formato do código e a recusa do
  `institucional`;
- a criação dos modelos iniciais de aviso no registro;
- uma tela na área institucional, com prévia do cabeçalho como o compositor o imprime;
- a semente no lugar da sincronização (§4.3, §6), e os documentos que a ensinam;
- o gatilho que recusa mudar `institution_scope` de Processo e Edital (§5.1);
- regressões: tela desfeita pelo comando; unidade fora do arquivo derrubando a subida; código
  imutável; `institucional` recusado; trilha no escopo certo; quem não tem a permissão recebe a
  recusa da `033`; escopo do Edital recusado pelo banco.

**Decisões a levar ao usuário antes do `/speckit-specify`.**

| # | Pergunta | Proposta da revisão |
|---|---|---|
| U-1 | A permissão vai ao `administrador-institucional` que já existe ou a um papel novo? | ao existente, por enquanto: a equipe é de duas a três pessoas e os papéis se acumulam; separá-los depois é uma linha do catálogo |
| U-2 | A unidade edita algo de si — o canal de atendimento, por exemplo? | não, na primeira versão |
| U-3 | Quem pede o registro de um campus, e com que documento? | o motivo do ato cita o documento; o sistema não o interpreta |
| U-4 | A Reitoria é unidade emissora? | registrar como unidade quando publicar Edital próprio |
| U-5 | Reativar unidade desativada é permitido? | sim, com motivo; nada se perde ao desativar |

**O que não entra:** criar unidade por importação em lote, cadastro retroativo, excluir unidade,
trocar código, FK nova, correio por unidade, leitura transversal da Reitoria, testes de isolamento
para as áreas sem segunda unidade (§2.4) — que podem entrar se a spec quiser, mas não dependem dela.

**Custo escondido**: o gatilho acrescenta uma migration a `processos`, e o guardião da `022`, que
conta as migrations por app, cobra o parágrafo de justificativa. A semente não precisa de migration.

---

## 10. O PR mais recente de identificação institucional (#349, spec 109)

| Situação | Item | Evidência |
|---|---|---|
| **Resolvido** | marca, título e rodapé da gestão, do portal, da página de acesso e da 404 saem do registro | `_marca_da_unidade.html`, `identificacao.py` *(#349)* |
| **Resolvido** | assinatura do aviso, da convocação e do comprovante pela unidade certa (do Edital no envio; do ato no comprovante) | D-004 do research *(#349)* |
| **Resolvido** | "peça acesso a quem administra o sistema no Cefor" passa a dizer a unidade ativa | inventário, outras ocorrências *(#349)* |
| **Resolvido** | guardião contra "Cefor" em moldura e mensagem | `tests/unidades/test_identificacao_multiunidade.py` *(#349)* |
| **Resolvido** | nenhuma ocorrência de classe F — dependência funcional de `cefor` | inventário *(#349)*; confirmado nesta revisão por `git grep -i cefor` fora de comentário, teste e demonstração |
| **Parcial** | canal de atendimento por unidade: existe, opcional, mas o do Cefor continua no `PORTAL_ATENDIMENTO` | P-2 *(#349)* |
| **Parcial** | marca das superfícies sem unidade com mais de uma ativa: regra provisória "só Ifes" | P-1 *(#349)* |
| **Parcial** | área do candidato numa inscrição, resultado e sorteio com a moldura da implantação | P-7 *(#349)* |
| **Parcial** | `Import_ModeloCefor`, nome do serviço no endpoint operacional, frases sobre a amostra | P-3, P-4, P-5 *(#349)* — contrato ou texto, não defeito |
| **Lacuna** | o canal novo entra pelo **mesmo arquivo** e pelo mesmo comando, o que aprofunda a dependência que a §4 recomenda desfazer | research, *"As dependências do unidades.json que permanecem"* *(#349)* |
| **Lacuna** | o registro continua sem administração; o próprio research da `109` lista os seis pontos a rever — esta revisão os responde na §4 a §9 | idem |
| **Fora do alcance da 109, e certo que fique** | o seletor de demonstração fixo em `cefor`; os `NAMESPACE` de `uuid5`; o `type` dos problemas da API | D-008 *(#349)* |

**Nota de custo**: a `109` acrescenta uma leitura do registro a toda página com moldura (+1 consulta;
a prévia do aviso, +2). Com a tela de unidades, essa leitura passa a refletir a mudança na requisição
seguinte, sem reinício — o que já era a razão do D-001 dela para não guardar em memória.
