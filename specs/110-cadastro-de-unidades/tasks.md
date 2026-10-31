# Tasks: Cadastro de unidades administrado pela aplicação

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [migracao.md](migracao.md). Caminhos
relativos a `backend/`, salvo os que começam por `specs/`, `doc/`, `scripts/` ou nomeiam um arquivo
da raiz.

**Testes**: pedidos pela spec (FR-3336) e pelo pedido de 31/10 (§7, os quinze); cada fase escreve os
seus antes de dar a fase por concluída. Os gatilhos e privilégios só se provam contra PostgreSQL,
com casos transacionais.

**Três incrementos, três PRs** (D-019). A e B não dependem de nada e podem correr em paralelo. C é
um PR só. A revisão da decisão de produto 3 (D-002) foi confirmada pelo usuário em 31/10/2026.

**Revisão final de 31/10/2026.** As 41 tarefas da versão anterior viraram 51: saiu a que
acrescentava o rótulo do canal à trilha (veio com a integração da `108` e da `109`); entraram o papel
próprio e a opção `--papel` (T018–T021), o apelido do comando (T023, T025), a entrada de homologação
(T010–T014), um fechamento por PR (T009, T014) e a validação funcional separada da verificação
automatizada (T051). Depois da comparação das estratégias de homologação, T010–T013 passaram ao
provedor simulado, sem código assinado. As outras foram reagrupadas, sem mudar de conteúdo.

## Fase 0 — Verificação de dependência (antes de cada incremento)

- [x] T001 Conferir que #349 (`109`) e #348 (`108`) estão na `main` — **feito em 31/10/2026**: `cf048007` e `81ce6e94`
- [ ] T002 Reconferir na `main` do dia os contratos do plan (§Verificação de dependência): `Unidade.atendimento` e a validação em `processo_seletivo/unidades/application/sincronizacao.py`; `processo_seletivo/unidades/application/identificacao.py`; `linhas`, os mapas e `CAMPOS_LEGIVEIS["Unidade"]` (com o canal) em `processo_seletivo/interface/trilha_da_unidade.py`; `_autoridade`, `conceder_administracao_institucional` e as funções de retirar e substituir em `processo_seletivo/seguranca/application/acessos.py`; `_e_administracao_institucional` em `processo_seletivo/seguranca/application/suspensao.py`. Divergência → a spec volta ao `/speckit-analyze`
- [ ] T003 Medir o teto de `FR-`/`SC-` em todas as worktrees e na `main` (se outra spec tomou 3301–3343 ou 1041–1048, renumerar antes de escrever código); conferir que nenhuma branch aberta cria `processos/0005` nem papel em `PAPEIS_INSTITUCIONAIS`

## Fase 1 — Incremento A: integridade do escopo (US6) — PR próprio

**Objetivo**: o escopo de Processo e de Edital não muda no banco; as quatro áreas sem segunda unidade
ganham teste. **Teste independente**: os cenários da US6. Nenhuma decisão pendente o bloqueia.

- [ ] T004 [US6] Criar `processo_seletivo/processos/migrations/0005_escopo_imutavel.py` com os gatilhos `processo_escopo_imutavel` e `edital_escopo_imutavel`, no-op fora do PostgreSQL, reversível (D-013)
- [ ] T005 [US6] `tests/migrations/test_migrations.py`: `processos` de 4 para 5, com o parágrafo de justificativa, e os dois gatilhos em `TRIGGERS_POR_APP["processos"]`, para que a reversibilidade deles seja exercitada
- [ ] T006 [US6] `tests/integration/agenda/test_fonte.py`: o Edital da Serra criado por um ator de `serra` registrada, e não movido (FR-3335, EC-15)
- [ ] T007 [P] [US6] `tests/integration/test_escopo_imutavel.py`, transacional, com a role de runtime: `update()`, `save()` e SQL direto recusados nas duas tabelas; `save()` completo sem mudança aceito; os gatilhos da `060` continuam (FR-3333, FR-3334)
- [ ] T008 [P] [US6] `tests/authorization/test_isolamento_entre_unidades.py`: com `campus-a` registrada e um ator dela, os quatro caminhos da D-014 respondem como inexistente e não gravam; se algum vazar, corrigir neste PR e registrar em `specs/110-cadastro-de-unidades/verificacao.md` (FR-3336)
- [ ] T009 `cd backend && make lint check test-pg` com `DB_NAME` próprio; o resultado em `specs/110-cadastro-de-unidades/verificacao.md`, seção A; PR do incremento A, sem merge automático

## Fase 2 — Incremento B: entrada de homologação (US7) — PR próprio

**Objetivo**: uma pessoa chega às telas da gestão pela entrada institucional, numa instância
controlada, antes do SSO; produção recusa o adaptador. **Teste independente**: os cenários da US7.
Só código de teste e documentação.

- [ ] T010 [US7] Criar `tests/homologacao/__init__.py` e `tests/homologacao/provedor.py` com `ProvedorDeHomologacao(ProvedorSimulado)`, `nome = "homologacao"`: herda `concluir` e `apenas_para_testes`; `iniciar` responde a página do provedor, no molde de `tests/navegador/provedor.py`, com as pessoas cuja `IdentidadeExterna` é do provedor `homologacao`, o nome e os papéis vigentes; escolher uma chama `provedor_simulado.emitir` e volta ao retorno com o `state` e o bilhete. Sem criptografia própria (D-018, FR-3342, FR-3343)
- [ ] T011 [US7] Uma linha na docstring de `tests/fixtures/provedor_simulado.py` dizendo que a subclasse de homologação existe e que as duas recusas de produção valem para ela — o ponto que a revisão de quem mexer no simulado precisa ver
- [ ] T012 [P] [US7] `tests/homologacao/test_entrada_de_homologacao.py`: com as settings de produção, o provedor é recusado no *boot* pelo pacote e pela declaração de teste, e `provedor_configurado` devolve nada em execução (FR-3342); a página lista só pessoas do provedor `homologacao`, e não as do provedor simulado nem as de demonstração; escolher uma entra no escopo dos vínculos dela; o bilhete não serve duas vezes; retorno sem o `state` da ida recusado, como hoje (FR-3343)
- [ ] T013 [P] [US7] `specs/110-cadastro-de-unidades/quickstart.md`, roteiro G, e `doc/implantacao-em-producao-ubuntu.md`, §10.3: o ambiente de homologação funcional com a tabela da D-018 — separado da VM de homologação, que não muda; settings de desenvolvimento; seletor desligado; banco sintético; segredos próprios; perímetro (só `localhost` até a P-6; depois, rede fechada e autenticação básica num *proxy* que não termina TLS)
- [ ] T014 `cd backend && make lint check test-pg`; resultado em `verificacao.md`, seção B; PR do incremento B, sem merge automático

## Fase 3 — Incremento C: fonte oficial e administração (US1–US5) — um PR só

**Objetivo**: o registro passa a ser escrito pela aplicação, e a troca da fonte chega com o mecanismo
que a substitui. **Teste independente**: a jornada (SC-1041) e a validação funcional (SC-1048).
Começa depois de o usuário confirmar a revisão da decisão de produto 3 (D-002); se ele mantiver a
original, T018–T021 se reduzem a pôr a permissão na lista do `administrador-institucional`.

### C.1 — A regra única e o papel

- [ ] T015 [US5] Criar `processo_seletivo/unidades/domain/registro.py` com a validação de uma unidade (código, reservado, campos, cabeçalho, canal), movida de `sincronizacao.validar` sem cópia, e os códigos de recusa por campo (D-005); `tests/seguranca/test_vinculos.py`, que importa `sincronizacao.validar`, passa a importar a regra nova
- [ ] T016 [US5] Acrescentar a `processo_seletivo/unidades/domain/nomes.py` os códigos `codigo_invalido`, `codigo_reservado`, `codigo_ja_registrado`, `campo_obrigatorio`, `cabecalho_invalido`, `atendimento_invalido`, `nada_mudou`, `unidade_alterada`, `unidade_ja_desativada`, `unidade_ja_ativa`, `motivo_obrigatorio`, e a permissão `ADMINISTRAR = "unidade:administrar"`
- [ ] T017 [P] [US5] Testes da regra em `tests/unidades/test_regra_da_unidade.py`: cada recusa, aparar espaços (EC-4), caixa e espaço no código recusados sem conversão (EC-1), `institucional` recusado
- [ ] T018 [US1] `processo_seletivo/seguranca/acessos.py`: o papel `ADMINISTRADOR_DE_UNIDADES = "administrador-de-unidades"` em `PAPEIS_INSTITUCIONAIS`, "Administrador do registro de unidades", com `"unidade:administrar"` por extenso e nada mais; o `administrador-institucional` sem mudança; comentário com a comparação da D-002
- [ ] T019 [US1] `processo_seletivo/seguranca/application/acessos.py`: `_autoridade` recusa pela tela todo papel de `PAPEIS_INSTITUCIONAIS` com `PAPEL_SO_POR_IMPLANTACAO` (FR-3339); `conceder_administracao_institucional`, a retirada e a substituição recebem `papel`, com padrão `ADMINISTRADOR_INSTITUCIONAL`, conferem que ele é institucional, e aplicam `adicional` e a regra da última administração por papel, sob a mesma trava global; `processo_seletivo/seguranca/application/suspensao.py`: `_e_administracao_institucional`, com o mesmo nome, passa a perguntar por vínculo vigente no escopo institucional com qualquer papel (FR-3340)
- [ ] T020 [US1] `processo_seletivo/seguranca/management/commands/conceder_administracao_institucional.py`, `retirar_administracao_institucional.py` e `substituir_administracao_institucional.py`: `--papel`, com as escolhas de `PAPEIS_INSTITUCIONAIS` e o padrão de hoje; a mensagem de saída nomeia o papel (FR-3310)
- [ ] T021 [P] [US1] `tests/seguranca/test_papel_do_registro.py`: conceder, retirar e substituir com `--papel administrador-de-unidades`, com motivo e trilha; segunda pessoa sem `--adicional` recusada, por papel; retirar a última sem a marca recusada; os comandos sem `--papel` fazem o mesmo de antes; o Administrador institucional de acessos não concede o papel pela aplicação (EC-18); só a implantação suspende quem tem o papel do registro; o papel não tem outra permissão (FR-3308); os testes de implantação e de suspensão da `107` passam sem mudança (SC-1047)

### C.2 — A semente

- [ ] T022 [US5] Renomear `processo_seletivo/unidades/application/sincronizacao.py` para `semente.py`: aplicar só com a tabela vazia, sob `pg_advisory_xact_lock`; validar pela regra única só quando se aplica; trilha `REGISTRAR_UNIDADE` de `implantacao`; `exportar()` (D-001, D-004, D-016)
- [ ] T023 [US5] Substituir `processo_seletivo/unidades/management/commands/sincronizar_unidades.py` por `semear_unidades.py`, com as linhas de saída do contrato, `--arquivo` e `--exportar`, mantendo a chamada a `garantir_modelos_iniciais` (FR-3305); recriar `sincronizar_unidades.py` como apelido — subclasse que escreve o aviso do nome anterior no *stderr* e faz o mesmo (D-003, FR-3306)
- [ ] T024 [US5] Trocar as chamadas pelo nome novo: `Makefile` (alvo `unidades` e comentário), `scripts/docker/entrypoint.sh`, `processo_seletivo/processos/management/commands/seed_demo.py`, as seis menções de `doc/implantacao-em-producao-ubuntu.md` (linhas 670, 714, 1249, 2533, 2802 e 3020 na `main` de 31/10, entre elas o roteiro `ps-migrar`), `doc/auditoria-edital-pdf-2026-10-08/cenarios/comum.py` (importa `sincronizar`) e `docs/libras/ferramentas/exportar_corpus.py`
- [ ] T025 [P] [US5] Em `tests/conftest.py`, um marcador (`sem_unidade_da_suite`) que dispensa a fixture `autouse` do Cefor, para os casos de registro vazio; o registro se esvazia por `TRUNCATE`, que não dispara o gatilho de linha `unidade_nao_se_exclui`, em caso transacional. Depois, substituir `tests/unidades/test_sincronizacao.py` por `tests/unidades/test_semente.py`: registro vazio semeia; registro preenchido não grava nem lê o arquivo; unidade fora do arquivo permanece; valores diferentes no arquivo não se aplicam; arquivo malformado só falha com registro vazio (EC-11); duas sementes simultâneas em banco vazio gravam uma vez; modelos iniciais idempotentes; `--exportar` não grava e reproduz o registro, inclui `ativa`, omite `atendimento` vazio e é aceito pela regra da semente (D-016); `sincronizar_unidades` roda a semente, com a mesma saída no *stdout*, o aviso no *stderr* e o mesmo código de saída (EC-17); `test_os_roteiros_chamam_a_semente` lê o `Makefile`, o `entrypoint.sh` e o guia de produção e exige o nome novo neles; o arquivo continua só com o Cefor
- [ ] T026 [P] [US5] `test_a_inicializacao_nao_altera_o_registro` em `tests/unidades/test_semente.py`: com `cefor` editado e `serra` criada direto no banco, rodar `semear_unidades` e o apelido por `call_command` e conferir registro e trilha idênticos; e conferir, lendo o `entrypoint.sh`, que a semente é o único passo dele que toca dado de unidade. **Não** rodar `provisionar_papeis` nem `migrate` dentro do caso: os papéis são do cluster, e os workers colidiriam (pedido §7, itens 3 e 4)

### C.3 — Os casos de uso

- [ ] T027 [US1] `processo_seletivo/avisos/application/modelos.py`: extrair de `garantir_modelos_iniciais` a criação dos três modelos de **uma** unidade, com o ator e o `correlation_id` recebidos; `garantir_modelos_iniciais` passa a chamá-la com o ator `implantacao`, como hoje (D-006)
- [ ] T028 [US1] Criar `processo_seletivo/unidades/application/registro.py` com `conferir_registro` e `registrar`: permissão no escopo institucional, regra única, motivo, unicidade convertida em `codigo_ja_registrado` por um bloco atômico aninhado (EC-2); modelos iniciais da unidade nova pela função da T027, com o ator da pessoa no escopo da unidade, na mesma transação; evento no escopo da unidade; e as leituras `listar` e `ficha`, que também exigem a permissão (D-006, D-008, FR-3309)
- [ ] T029 [US2] Em `registro.py`, `conferir_alteracao` e `alterar`: código da rota, chave `codigo` ignorada (EC-9), `nada_mudou` (FR-3322), resumo de versão — os seis campos editáveis e `ativa` — e `unidade_alterada` sob trava (D-007), `alterada_em`, evento com antes e depois
- [ ] T030 [US3] Em `registro.py`, `desativar`, `reativar` e `consequencias`: transições e recusas, com a mesma versão conferida da edição; Processos não encerrados; se a identificação das telas sem unidade muda (FR-3326–FR-3330)
- [ ] T031 [P] [US1] `tests/unidades/test_administrar_unidades.py`: registrar uma unidade; modelos iniciais uma vez, com a pessoa como autora na trilha; evento no escopo da unidade com pessoa, permissão, motivo e `depois`; falha no evento desfaz o ato (FR-3332); dois cadastros do mesmo código gravam um (EC-2); a Reitoria é unidade sem leitura dos campi (EC-13); unidade nova sem autoridade nem acesso herdado; disponível na requisição seguinte para conceder o Administrador de acessos, criar Processo e cadastrar autoridade (FR-3320)
- [ ] T032 [P] [US2] Em `tests/unidades/test_administrar_unidades.py`: alterar grava antes e depois; código enviado ignorado; nada mudou recusado sem evento; duas alterações concorrentes, a segunda recusada; canal apagado volta ao institucional (EC-12)
- [ ] T033 [P] [US3] Em `tests/unidades/test_administrar_unidades.py`: desativada não recebe Processo nem vínculo e conduz o existente; desativar a única ativa é permitido (EC-5); autoridade de desativada continua editável (EC-14); reativada volta a receber; transições repetidas recusadas
- [ ] T034 [P] [US1] `tests/authorization/test_administrar_unidades.py`: a matriz — os oito papéis do `PAPEIS`, o Integrante e o Administrador de acessos da unidade, o **Administrador institucional de acessos sem o papel do registro**, o administrador do registro com escopo de unidade (EC-8), a demonstração — recebem a recusa em cada caso de uso; a permissão não abre Processo, Edital nem acesso, e o administrador do registro não concede acesso (FR-3310); a grafia da permissão no catálogo e em `nomes.py` é a mesma; nenhum outro papel a tem (FR-3308–FR-3311)
- [ ] T035 [P] [US1] `test_a_trilha_da_unidade_le_os_atos`, inclusive uma edição só do canal de atendimento, em `tests/unidades/test_administrar_unidades.py`: os quatro atos aparecem na trilha da unidade da `108`, com rótulo, situação, autor pelo nome e antes→depois — conferência, porque o rótulo do canal já está na `main` (D-009)

### C.4 — As telas e a jornada

- [ ] T036 [US4] Criar `processo_seletivo/interface/unidades.py`: ator do nível institucional com a permissão e depois a recusa da demonstração, na ordem de `interface/acessos.py::_ator_do_nivel`, as duas antes de ler o registro; lista, ficha, cadastrar, editar, desativar e reativar em duas etapas (D-011, contrato das telas)
- [ ] T037 [US4] Prévia em `interface/unidades.py` por `linhas_do_orgao` de `processo_seletivo/publicacoes/infrastructure/pdf.py`, com importação dentro da função, o local do fecho, a sigla no anúncio do ato por `anuncio_em_caixa_alta`, a marca da `109`, e o aviso quando uma linha do cabeçalho não cabe numa linha do documento, pela métrica do compositor (D-010)
- [ ] T038 [US4] Histórico da ficha: a leitura `ficha` da T028, traduzida por `linhas` de `processo_seletivo/interface/trilha_da_unidade.py`, com o autor pela tag `nome_de_pessoa`, como no template da `108`; nada a acrescentar a `CAMPOS_LEGIVEIS` (D-009)
- [ ] T039 [P] [US4] Templates `processo_seletivo/interface/templates/interface/unidades.html`, `unidades_ficha.html`, `unidades_formulario.html`, `unidades_conferencia.html`, `unidades_situacao.html`; folha `processo_seletivo/interface/static/interface/telas/unidades.css`; ajuda do canal e do motivo (D-012)
- [ ] T040 [US4] `processo_seletivo/interface/urls.py` (seis rotas), `processo_seletivo/interface/navegacao.py` ("Unidades" em `SECOES_DE_ACESSO` com `pode_administrar_unidades`), o ícone no sprite de `base.html` se a barra exigir ícone distinto
- [ ] T041 [US4] Acrescentar `processo_seletivo/interface/unidades.py` a `MODULOS_DE_VIEW` em `tests/test_gramatica_das_portas.py`, e a linha do 404 da ficha em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, como objeto inexistente
- [ ] T042 [P] [US4] `tests/interface/test_telas_de_unidades.py`: lista com ativas e desativadas; ficha com histórico da implantação e da pessoa; 404 de código inexistente; conferência sem gravar; prévia com as linhas do compositor; antes e depois na edição; aviso de código permanente; aviso da moldura nas três situações da FR-3330; sigla no anúncio e aviso de linha longa na prévia; consequências da desativação; recusas no campo com os valores digitados; envio forjado sem permissão recusado (SC-1043); código no corpo da edição ignorado (EC-9); nenhuma tela oferece exclusão (FR-3329); demonstração recusada e sem o item na barra; os dois papéis institucionais separados e juntos — itens da barra e recusas (EC-16, FR-3341); nenhum `style=`/`<style>`/`<script>`. Acrescentar os cinco templates às listas literais das varreduras de vocabulário e de acessibilidade — tela fora da lista escapa da regra sem aviso
- [ ] T043 [P] [US1] `tests/navegador/test_jornada_de_unidades.py`: a preparação concede os dois papéis institucionais à mesma pessoa pela implantação; dela à criação de Processo em `serra`, sem ação fora do navegador (D-015, SC-1041)
- [ ] T044 [P] `tests/unidades/test_compatibilidade_do_registro.py`: o Cefor continua sem ação; editar a unidade não muda o documento nem o conteúdo de Publicação e de resultado anteriores, byte a byte (SC-1045); `seed_demo` continua (FR-3337, FR-3338)

### C.5 — Documentação e verificação

- [ ] T045 [P] `AGENTS.md`: o parágrafo do `make preparar` passa a falar da semente e da linha nova, e do apelido
- [ ] T046 [P] `README.md`: o passo de preparo; a linha da `110` na tabela de incrementos passa a "Implementada"
- [ ] T047 [P] `doc/implantacao-em-producao-ubuntu.md`: a leitura da saída da semente; o apelido e o critério para retirá-lo; conceder, retirar e substituir o papel do registro com `--papel`; que a tela só existe com a entrada institucional; a jornada de cadastrar unidade passa à tela; a reversão aponta [migracao.md](migracao.md); `doc/ativacao-do-sso-institucional.md`: o passo do `ps-migrar` e a designação do papel do registro (FR-3307)
- [ ] T048 [P] `doc/revisao-arquitetural-multiunidade-2026-10-30.md`: a nota de 31/10 no topo passa a dizer que a `110` foi implementada, e onde está a verificação
- [ ] T049 `specs/110-cadastro-de-unidades/rastreabilidade.md`: a coluna de teste de cada linha com o nome real do caso
- [ ] T050 `cd backend && make lint check test-pg` com `DB_NAME` próprio; `make test-navegador`; roteiros A a F do [quickstart](quickstart.md); resultados e os 15 itens do pedido em `specs/110-cadastro-de-unidades/verificacao.md`, seção C; PR do incremento C, sem merge automático
- [ ] T051 **Validação funcional — critério de aceite humano, não teste** (SC-1048): no ambiente de homologação funcional, uma pessoa da equipe que não escreveu a feature segue o roteiro G; o registro vai a `specs/110-cadastro-de-unidades/verificacao.md`, numa seção própria, separada dos resultados da suíte, com a data, quem validou, o que foi feito e o que estranhou. Sem ele a feature não é dada por aceita; ele não bloqueia o merge do PR C, que é decisão do usuário

## Dependências

```text
T002–T003 ─┬─▶ Fase 1 (A) ──────────────┐
           ├─▶ Fase 2 (B) ──┐            │
           │                ▼            ▼
           └─▶ confirmação da decisão 3 ─▶ Fase 3 (C: C.1 ▶ C.2 ▶ C.3 ▶ C.4 ▶ C.5)
```

- A e B não dependem um do outro, nem de decisão pendente; podem ir a PR já.
- C não depende de A para funcionar, mas o roteiro F do quickstart (duas unidades) fica mais forte
  com o gatilho no banco; o natural é C depois de A.
- C depende de B só para a validação funcional (T051, SC-1048): a implementação pode começar antes.
- Dentro de C, a suíte fica verde ao fim de cada passo; o PR sai só depois de C.5.

## Paralelismo

- Fase 1: T007 e T008 em paralelo, depois de T004–T006.
- Fase 2: T012 e T013 em paralelo, depois de T010 e T011.
- C.1: T017 e T021 em paralelo, depois de T015, T016 e T018–T020.
- C.2: T025 e T026 em paralelo, depois de T022–T024.
- C.3: T031 a T035 em paralelo, depois de T027–T030.
- C.4: T039, T042, T043 e T044 em paralelo, depois de T036–T038.
- C.5: T045 a T048 em paralelo.

## Estratégia

**Primeiro valor**: o incremento A — o defeito de integridade que a revisão de 30/10 achou, sem
decisão pendente. **O critério do pedido** — unidade nova sem commit, PR nem deploy — chega com C,
que é indivisível na `main` para não abrir janela sem mecanismo de cadastro (D-019).
