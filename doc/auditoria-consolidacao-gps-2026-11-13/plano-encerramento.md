# Plano de encerramento

*Base: `origin/main` em `33546564`, 13/11/2026. Nenhuma ação deste plano foi executada.*

**🔒 = depende da sua autorização.** Quase tudo depende, porque mexe em commit, push, merge ou
exclusão. As exceções estão marcadas com **(livre)**: são as que só copiam arquivos para fora do
repositório.

Ordem: o P0 inteiro antes de qualquer item do P2. P1 e P2 podem correr em paralelo, desde que o P0
esteja feito.

`W` abaixo é `~/Projetos/processo_seletivo/.claude/worktrees`.

---

## P0 — Preservação: nada se perde

- [x] **P0-1 🔒 Guardar a implementação não commitada da 123** (`W/upbeat-haslett-9d4178`,
  branch `claude/123-implementacao`).
  - **Feito em 13/11, autorizado pelo usuário:** commit WIP `d3471784` com 30 arquivos (22
    modificados e 8 novos), idêntico ao backup, e push para `origin/claude/123-implementacao`.
    `git status` está limpo. Não foi rebaseado nem testado: retomar exige integrar com a `main`.
  - *Evidência:* `git status` mostra 21 arquivos modificados e 8 não rastreados, de 06/11. Entre eles
    estão `versao_base.py`, `_versao_base.html` e 5 arquivos de teste novos. O `tasks.md` local
    marca T002–T007, T012–T015 e T017.
  - *Ação:* um commit WIP na própria branch (`git -C W/upbeat-haslett-9d4178 add -A && git commit`)
    e o push dela. Sem rebase agora: a `main` mexeu nos mesmos arquivos em 5 commits (131, 144 e
    146), e integrar é trabalho de retomada, não de preservação.
  - *Justificativa:* é o único trabalho de produto em risco real.
  - *Dependências:* nenhuma.
  - *Concluído quando:* `git -C W/upbeat-haslett-9d4178 status --porcelain` sai vazio e
    `origin/claude/123-implementacao` existe.
  - **Rede de segurança em 13/11:** `diff`, arquivos novos e commit-base copiados para
    `~/Projetos/processo-seletivo-preservacao-2026-11-13/backup-123-ux-da-retificacao/`. O diff foi
    conferido como reaplicável. Isso não substitui o commit.

- [x] **P0-2 Tirar do repositório o código-fonte do filme de apresentação** (livre).
  - **Feito em 13/11:** copiado para `~/Projetos/processo-seletivo-video/` (3,6 GB), conferido por
    `rsync -c` sem nenhuma diferença. Foram juntos os vídeos finais, as locuções e a trilha. Ficaram
    de fora só os quadros `out/frames_*` (15,5 GB), que se regeneram. A worktree está intacta.
  - *Evidência:* `W/processo-seletivo-video-519ad6/video/` não é rastreado. Tem cerca de 42 MB de
    fonte (`scenes-*.js`, `shots.js`, `tools/`, `fonts/`, `capturas/`, `README.md`) e 19 GB em
    `out/`, que já é ignorado. Não está na `main` (o #286 é o filme de *lançamento*).
  - *Ação:* copiar `video/` sem o `out/` para uma pasta permanente fora das worktrees, por exemplo
    `~/Projetos/processo-seletivo-video/`. O `out/` só se apaga com autorização sua 🔒.
  - *Concluído quando:* a cópia existe, e o `README.md` dela abre.

- [x] **P0-3 🔒 Auditoria de autonomia operacional** (`claude/operation-vs-task-execution-5e2d5c`).
  - *Evidência:* 1 commit só local, `c7232947`, com 265 linhas em
    `doc/estudo-autonomia-operacional-2026-11-13/README.md`.
  - *Ação:* empurrar a branch e abrir um PR de documentação. Se não quiser na `main`, basta empurrar.
  - *Concluído quando:* o commit existe no remoto.
  - **Empurrada em 13/11, autorizado pelo usuário:** `origin` aponta para `c7232947`, igual à branch
    local. Nenhum PR foi aberto. A decisão sobre levar para a `main` continua sua.

- [x] **P0-4 🔒 Estudo da configuração da classificação** (`claude/gps-classification-config-ux-294027`).
  - *Evidência:* 5 commits só locais, de 01/11, com 122 arquivos em
    `doc/estudo-configuracao-classificacao-2026-11-01/`. O teste A11 que vinha junto foi superado
    pela versão da `main`.
  - *Ação:* decidir entre empurrar a branch como arquivo ou descartá-la. Se for para a `main`, sem o
    arquivo de teste.
  - *Concluído quando:* a decisão está registrada e, se for "guardar", o remoto tem os commits.
  - **Empurrada em 13/11, autorizado pelo usuário:** `origin` aponta para `5dc7f420`, igual à branch
    local. Nenhum PR foi aberto. A decisão sobre levar para a `main` continua sua.

- [x] **P0-5 🔒 Estudo de revisão dos cronogramas** (`claude/estudo-visualizacao-cronogramas-1950cd`).
  - *Evidência:* 6 commits só locais, de 01/11, com 81 arquivos em
    `doc/estudo-cronogramas-revisao-2026-11-01/`. Nenhuma spec o cita, e a 101 (Agenda) foi
    mergeada antes dele.
  - *Ação:* a mesma decisão do P0-4.
  - **Empurrada em 13/11, autorizado pelo usuário:** `origin` aponta para `78603338`, igual à branch
    local. Nenhum PR foi aberto. A decisão sobre levar para a `main` continua sua.

- [x] **P0-6 🔒 Achado dos documentos da convocação sem forma no PDF** (`claude/edital-pdf-formatting-3963ad`).
  - *Evidência:* 1 commit só local, de 12/11, em
    `doc/achado-documentos-da-convocacao-sem-forma-no-pdf.md`. O PDF é o ato oficial no piloto, e
    nada na `main` trata esse trecho.
  - *Ação:* empurrar e abrir um PR de documentação, ou anexá-lo ao próximo PR de documentação.
  - *Concluído quando:* o arquivo está na `main` ou no remoto.
  - **Empurrada em 13/11, autorizado pelo usuário:** `origin` aponta para `29c361a8`, igual à branch
    local. Nenhum PR foi aberto. A decisão sobre levar para a `main` continua sua.

- [x] **P0-7 🔒 Branch `claude/achado-jornada-do-candidato-na-convocacao`** (só local; a remota foi
  apagada).
  - *Evidência:* 1 commit, superado pelo #375. O comentário de fechamento do #374 diz que ela "fica
    preservada como referência histórica".
  - *Ação:* empurrá-la de novo, ou confirmar que a referência histórica não é mais necessária.
  - **Empurrada em 13/11, autorizado pelo usuário:** `origin` aponta para `36bac857`, igual à branch
    local. Nenhum PR foi aberto. A decisão sobre levar para a `main` continua sua.

- [ ] **P0-8 Tutorial da formalização** (livre para copiar; 🔒 para decidir o destino).
  - *Evidência:* `W/127-andamento-da-selecao-ac9d30/tutorial-formalizacao.html` (763 KB), fora do
    git. O `contexto-para-outro-agente.md` de 12/11 registra que o tutorial da equipe "ainda diz que
    só a gestão de acessos designa o setor", e o #501 mudou isso.
  - *Ação:* copiar o arquivo para fora da worktree.
  - **Cópia feita em 13/11:** em `~/Projetos/processo-seletivo-preservacao-2026-11-13/tutorial-formalizacao/`,
    junto com o achado e o diff do `launch.json`. Falta só decidir o destino.
  - No mesmo lugar:
    - o `doc/achado-designacao-da-formalizacao-pela-presidencia.md` foi resolvido pelo #501 e pode
      ser descartado 🔒;
    - a entrada `secretaria-demo` acrescentada ao `.claude/launch.json` é local e pode ser
      descartada 🔒.

- [ ] **P0-9 Capturas da 160** (livre para copiar; 🔒 para commitar).
  - *Evidência:* 37 PNG e `capturar.py` em
    `W/gps-candidate-auth-ui-2db0c1/doc/estudo-minhas-atividades-2026-11-12/capturas/` (8,9 MB),
    fora do git. O `verificacao.md` da 160 cita as capturas de T002/T036 (UX-714) como "feitas pela
    sessão que pediu a implementação", que é esta.
  - *Ação:* commitá-las na `main`, ao lado do estudo que já está lá, para que a evidência da UX-714
    exista. Se preferir não versionar imagens, copie-as para fora e corrija o `verificacao.md` para
    dizer onde estão.
  - **Cópia feita em 13/11:** em `~/Projetos/processo-seletivo-preservacao-2026-11-13/capturas-160/`.
    Falta decidir se vão para a `main`.

- [ ] **P0-10 Demais arquivos fora do git** (livre para copiar; 🔒 para descartar).
  - `W/gps-final-selection-journey-d04cb1/doc/estudo-jornada-final-2026-11-12/` (16 MB):
    reavaliação e verificação de 12/11 e `contexto-para-outro-agente.md`. Ficou sem commit **por
    decisão sua**. Copie para fora antes de remover a worktree.
  - `W/edital-clickable-annexes-0c0d80/doc/estudo-remissao-a-anexo-clicavel-2026-10-19.md` (36 KB):
    o estudo de 19/10 sobre FR-027a. Copiar ou descartar.
  - `W/silly-cerf-78b884/specs/104-acoes-disponiveis/*.pdf` (3 PDFs, 6 MB) e
    `capturas/depois/19-edital-devolvida-verbo-unico.png`: relatórios da revisão da 104. Copiar ou
    descartar.
  - **Cópias feitas em 13/11:** os três itens estão em
    `~/Projetos/processo-seletivo-preservacao-2026-11-13/`, conferidos byte a byte. Falta decidir o
    que descartar.

- [x] **P0-11 🔒 Checkout principal** (`~/Projetos/processo_seletivo`, na branch
  `codex/133-guia-visual-conceitos`, 394 commits atrás).
  - *Evidência:* em `doc/gps-por-dentro/`, `README.md` e `verificar_interface.cjs` estão modificados,
    e `gerar_autocontido.py` e `gps-por-dentro-autocontido.html` (3,9 MB) não são rastreados. Tudo é
    de 09/11, depois do merge do #433.
  - *Ação:* decidir entre um PR com o gerador (o HTML gerado provavelmente não deve ser versionado)
    e o descarte. Depois, pôr o checkout na `main` atualizada (`git -C <raiz> fetch origin main:main`
    e `git switch main`).
  - *Concluído quando:* `git -C ~/Projetos/processo_seletivo status --porcelain` sai
    vazio e a branch atual é `main`.
  - **Rede de segurança em 13/11:** cópia em
    `~/Projetos/processo-seletivo-preservacao-2026-11-13/backup-gps-por-dentro/`.
  - **Feito em 13/11, autorizado pelo usuário:**
    - os quatro arquivos foram para a branch `claude/gps-por-dentro-autocontido`, criada a partir
      da `main` (commit `87883f00`, worktree `W/gps-por-dentro-autocontido`), e abriu-se o PR
      [#528](https://github.com/vitofranzosi/processo_seletivo/pull/528), só de documentação;
    - o gerador reproduz o HTML byte a byte, e o verificador passa no índice e na versão
      autocontida;
    - o checkout principal foi limpo depois de conferir os quatro arquivos idênticos aos do PR, e
      agora está na `main` em `26748113`, com `status` vazio;
    - **falta o merge do #528, que é decisão sua.** O PR diz como fazer se o HTML gerado não deve ser
      versionado.

## P1 — Consolidação obrigatória

- [x] **P1-1 🔒 Decidir o [#524](https://github.com/vitofranzosi/processo_seletivo/pull/524)**
  (vitrine paginada).
  - *Evidência:* CI verde, mescla limpo, sem spec e sem FR. O próprio PR deixa o registro para
    decisão sua. Acrescenta a entrada `vitrine-paginada` ao `.claude/launch.json` versionado.
  - *Ação:* fazer merge ou fechar.
  - *Concluído quando:* o PR não está mais `OPEN`.
  - **Mergeado pelo usuário em 13/11** (`e815aeb5` na `main`). A worktree e a sessão passam para o P2-1,
    sob o mesmo critério de segurança.

- [x] **P1-2 🔒 Acompanhar o [#525](https://github.com/vitofranzosi/processo_seletivo/pull/525)**
  (156, US2).
  - *Evidência:* a sessão [156 MVP: textos do desfecho sem jargão](#local_1b0e8e48-4586-4e59-b005-1adabad1c5a3)
    está rodando. O PR mescla limpo com a `main` e com o #524. As fatias de teste ainda estavam
    rodando. A T023 esbarra na FR-3740 da 118, e a decisão foi remetida ao PR.
  - *Ação:* decidir a T023, esperar o CI e fazer o merge. Não encerre essa sessão nem a worktree
    dela até lá.
  - **Mergeado pelo usuário em 13/11** (`26748113` na `main`). A worktree e a sessão passam para o P2-1,
    sob o mesmo critério de segurança.

- [x] **P1-3 Confirmar o CI da `main` em `33546564`** (livre).
  - *Evidência:* ainda estava em andamento ao fim da auditoria. As duas falhas anteriores
    (`76ac8ea1` e `6aa1efdd`) foram corrigidas por #523, #517 e `68a74df5`.
  - *Concluído quando:* `gh run list --branch main --limit 1` mostra `success`.
  - **Feito em 13/11:** `33546564`, `e815aeb5` e `26748113` passaram (`success`).

Não há merge de branch de funcionalidade pendente além dos dois PRs abertos. As frentes incompletas
(144 B/C, 150, 152 US2, 154 US2, 155, 156, 161) não são consolidação: são trabalho que continua, já
registrado nas próprias specs.

## P2 — Organização e limpeza (só depois do P0)

- [x] **P2-1 🔒 Remover as 72 worktrees integradas** do apêndice do inventário, e arquivar as
  sessões delas.
  - *Critério de segurança, por worktree, no momento da remoção:*
    - `git -C <wt> status --porcelain` vazio;
    - `git rev-list origin/main..HEAD` vazio.
  - *Comando:* `git worktree remove <wt>`, sem `--force`. Se ele recusar, a worktree mudou desde a
    auditoria e precisa ser olhada de novo.
  - Arquivar a sessão não remove a worktree; o inverso também não arquiva a sessão.
  - **Feito em 13/11.** Na hora da remoção, a checagem achou só **59** worktrees limpas, e não 72. Nas outras 13, o contador da auditoria tinha escondido uma modificação local no `.claude/launch.json`: uma entrada de preview de dias atrás. Os 13 diffs foram salvos em `~/Projetos/processo-seletivo-preservacao-2026-11-13/launch-json-locais/` antes da remoção, feita com `--force`. As 59 saíram sem `--force` e sem recusa. Ficaram de fora 5 worktrees com sessão ativa ou recente, sem trabalho exclusivo conhecido: `156-textos-sem-jargao-b3b945` (já em outra branch), `selective-process-discovery-ux-2cf327`, `gps-final-selection-journey-d04cb1`, `merge-order-950a2a` e `candidato-login-copy-polish-482d06` (#527, nova). 72 sessões foram arquivadas. "Visão da secretaria acadêmica" foi mantida pelo app (fixada ou em uso) e fica para você arquivar pela barra lateral.

- [x] **P2-2 🔒 Remover as worktrees esvaziadas pelo P0**: `upbeat-haslett` (depois do push),
  `operation-vs-task-execution`, `beautiful-bohr`, `relatorio-consolidado-gps`,
  `edital-pdf-formatting`, `gps-candidate-auth-ui-2db0c1`, `gps-final-selection-journey`,
  `127-andamento-da-selecao`, `edital-clickable-annexes`, `silly-cerf` e
  `processo-seletivo-video`.
  - A última leva o `out/` de 19 GB junto.
  - Mesmo critério do P2-1, depois de confirmar que a cópia do P0 existe.
  - **Feito em 13/11.** As 11 worktrees saíram depois de reconferir que as cópias batem byte a byte com a origem e que as branches empurradas estavam iguais ao remoto. A do filme levou junto os quadros `out/frames_*`. Cerca de 40 GB foram liberados.

- [x] **P2-3 🔒 Apagar as branches locais integradas.** São 38 das 42 sem worktree, e as das
  worktrees removidas. Use `git branch -d`, que recusa o que não está integrado; nunca `-D` sem
  olhar.
  - **Não apagar:** `claude/155-destinacao-completa`, a do P0-7, a `main` e as que sustentam os
    PRs #524 e #525.
  - **Feito em 13/11.** 115 branches locais apagadas com `-d`, sem nenhuma recusa. Ficaram 9: as das worktrees vivas, a `main`, a `155-destinacao-completa` e a `gps-work-centered-model-4c557f`, cujos 4 commits nunca foram empurrados (o conteúdo é idêntico ao da `main`).

- [x] **P2-4 🔒 Apagar as 21 branches remotas integradas ou superadas:**
  - `claude/117-designacao-pela-presidencia-9d4f1c`
  - `claude/134-frentes-de-trabalho-nos-cenarios`
  - `claude/134-treino-da-formalizacao-b5bbbc`
  - `claude/150-implementacao`
  - `claude/150-us5-mesmo-arquivo`
  - `claude/152-conferencias`
  - `claude/152-desfecho-que-cabe-362ce1`
  - `claude/154-implementacao`
  - `claude/154-us3-nome-do-reenviado`
  - `claude/160-implementacao`
  - `claude/160-minhas-atividades`
  - `claude/160-revisao-de-codigo`
  - `claude/convocar-e-publicar`
  - `claude/demonstracao-publicacao-convocados`
  - `claude/designar-sem-quem-ja-esta-designado`
  - `claude/gps-barema-investigation-1750ab`
  - `claude/gps-candidate-auth-ui-7eeb4b`
  - `claude/gps-ui-ux-polish-three-screens-fa56bf`
  - `claude/teste-aberto-por-voce`
  - `claude/textos-da-jornada-final`
  - `claude/intelligent-robinson-4466a5` (superada pelo #488)

  **Manter no remoto:**
  - as cinco `claude/119-*-previas`, porque os PRs #386, #387, #391, #392 e #393 linkam imagens
    pelos SHAs delas;
  - `claude/155-destinacao-completa` e a tag `155-destinacao-completa`;
  - `001-decisoes-pendentes` e `002-inserir-documentacao-sistema`, que são de Vito Franzosi.
  - **Feito em 13/11.** As 21 branches remotas foram apagadas, cada uma reconferida antes.

- [ ] **P2-5 🔒 Atualizar as linhas `**Status**` defasadas** (inventário, §4: 32 concluídas, mais a
  152 e a 154).
  - Num PR só de documentação.
  - Antes do merge, rodar `test_citacoes_de_requisito.py` e `test_readme_acompanha_o_codigo.py`.
  - Não mexer em identificadores.
  - **PR aberto em 13/11:** [#530](https://github.com/vitofranzosi/processo_seletivo/pull/530) corrige 35 linhas de status. A antiga fica como "Status anterior". Os 8 testes que leem `specs/` passaram (1546).

- [x] **P2-6 🔒 Registrar a colisão FR-4601+** entre `134-aviso-de-pendencia-documental` e
  `134-cenarios-de-treinamento`, e o FR-001 a FR-009 da `133-guia`.
  - Registro, e não renumeração: renumerar mexe em código que cita os números (`production.py:126`
    e três testes). Se e como renumerar é decisão de governança sua.
  - **Registrado no mesmo #530**, em `doc/achado-identificadores-duplicados-133-134.md`. Renumerar continua decisão sua.

- [x] **P2-7 Corrigir o `contexto-para-outro-agente.md` de 12/11** se ele for preservado (P0-10).
  - Ele diz que a 158 está "só no PR #492, sem merge", e o #492 foi mergeado.
  - **Resolvido sem editar o original:** o `LEIA-ME.md` da pasta de preservação aponta o engano.

- [ ] **P2-8 Perguntar ao Vito** sobre `001-decisoes-pendentes` (saneamento de 16/10, cerca de 109
  arquivos) e `002-inserir-documentacao-sistema` (#329 fechado, 3 patches exclusivos). Nenhuma ação
  nossa sobre elas.

## P3 — Melhorias futuras (fora do encerramento)

Registradas para não se perderem. Nenhuma é necessária para consolidar.

- Um guardião de definição única de `FR-`, `SC-`, `UX-` e `D-` entre specs. O
  `test_citacoes_de_requisito.py` aceita duplicata em silêncio.
- O teste de tarefa com uma ou duas pessoas da equipe, sugerido no contexto de 12/11 para responder
  "a operação é óbvia?". É mais barato que outra recaptura por agente.
- As validações humanas já registradas nas specs: SC-605, SC-948, SC-958, SC-990, SC-1378, SC-1805,
  SC-2281 e SC-2297, além do leitor de tela e dos celulares da 157.
- Os próximos incrementos já especificados: 144 B/C, 152 US2, 154 US2, 150 fechamento, 156, 161, o
  restante da 155 (depois da D-015) e a 158 (depois das respostas P-1 a P-8).

---

## Ordem sugerida

1. P0-2, P0-8, P0-9 e P0-10, que são cópias e não pedem autorização.
2. P0-1, P0-3 a P0-7 e P0-11, uma decisão sua por item.
3. P1-1 a P1-3.
4. P2-1 a P2-4, a limpeza, refazendo a checagem de segurança no momento.
5. P2-5 a P2-8.
