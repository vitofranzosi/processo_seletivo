# Auditoria de consolidação das frentes do GPS — 13/11/2026

*Base: `origin/main` em `33546564` (merge do #522, 13/11 13:38). A auditoria começou em `99f298de`; o
#522 entrou durante ela, e o inventário já o conta como mergeado. Tudo foi só leitura: nenhum
commit, push, merge, exclusão ou alteração de banco.*

*Este é o diagnóstico como foi entregue. As ações executadas depois, com a autorização do usuário,
estão marcadas no [plano de encerramento](plano-encerramento.md), item a item. Entre elas, a
preservação do P0, a limpeza do P2 e a correção da contagem das worktrees limpas: eram 59, e não
72.*

- [inventario.md](inventario.md) — rastreabilidade de cada frente, branch, worktree e spec.
- [plano-encerramento.md](plano-encerramento.md) — checklist P0–P3, com o que depende da sua
  autorização.

## Resposta curta

**Pergunta:** posso encerrar as sessões antigas, limpar as branches e seguir a partir da `main` sem
risco conhecido de perder trabalho relevante?

**Ainda não, mas falta pouco.** **72 das 87 worktrees** e **38 das 42 branches locais sem
worktree** estão integradas e não têm nada exclusivo. Podem sair sem perda.

O risco de perda está concentrado em **onze lugares**, listados no P0 do plano:

- **uma implementação não commitada**: a spec 123, com 29 arquivos;
- **cinco branches só locais, nunca empurradas**: dois estudos de 01/11, a auditoria de autonomia
  operacional (13/11) e dois achados (04/11 e 12/11);
- **seis conjuntos de arquivos fora do git em worktrees**: o código-fonte do filme de apresentação,
  o tutorial da formalização, as capturas da 160, a reavaliação da jornada final de 12/11, um
  estudo de 19/10 e os relatórios da 104;
- **o checkout principal**, com alterações no guia "GPS por Dentro".

Há ainda **duas classes de branch que parecem descartáveis e não são**:

- as cinco `claude/119-*-previas`, de onde os PRs #386, #387, #391, #392 e #393 tiram as imagens;
- a `claude/155-destinacao-completa`, que as specs da 155 citam como o lugar da entrega completa.

Resolvidos esses pontos, a limpeza é segura.

## O que foi examinado

| Objeto | Quantidade | Observação |
|---|---|---|
| Worktrees | 87 | 86, mais o checkout principal. 8 em HEAD destacado. |
| Branches locais | 121 | 79 em worktree e 42 sem. |
| Branches remotas | 31 | Sem contar a `main`. 2 são de outro autor (Vito Franzosi). |
| PRs | 524 | 515 mergeados, 7 fechados sem merge, 2 abertos: [#524](https://github.com/vitofranzosi/processo_seletivo/pull/524) e [#525](https://github.com/vitofranzosi/processo_seletivo/pull/525). |
| Pastas de spec | 162 | Os números 133 e 134 aparecem duas vezes cada; 137 e 151 foram reservados e não usados. |
| Sessões do app neste projeto | 77 não arquivadas | 1 rodando: [156 MVP: textos do desfecho](#local_1b0e8e48-4586-4e59-b005-1adabad1c5a3). |
| Stash | 0 entradas | |

**Equivalência além do hash.** O critério de "fora da `main`" foi `git cherry`, que compara
patches, somado à conferência do conteúdo. Dois casos mostram por quê:

- a branch do estudo "Minhas atividades" tem 4 commits fora da `main`, mas a pasta que ela cria é
  idêntica byte a byte à que já está lá;
- a `155-destinacao-completa` é **ancestral** da `main`, mas o código dela foi retirado da árvore
  depois. "Está no histórico" não quer dizer "está no produto".

## Frentes por situação

Contagem por frente funcional (spec ou trabalho sem spec), detalhada no inventário:

| Situação | Quantas | Quais |
|---|---|---|
| CONCLUÍDA | 42 | 013, 034, 036, 038, 064, 074, 088, 090, 094 (fatia 1), 095, 099, 110, 111, 117, 119, 120, 122, 127, 128, 129, 131, as duas 133, as duas 134, 135, 136, 138–143, 145–149, 153, 157, 159 e 160. Ver a nota abaixo. |
| PENDENTE DE MERGE | 2 | #524 (vitrine paginada, sem spec) e #525 (156, US2 — sessão rodando). |
| INCOMPLETA | 8 | 123 (só local), 144 (B e C), 150 (fechamento), 152 (US2), 154 (US2), 155 (entrega mínima), 156 (só a spec na `main`) e 161 (só a spec). |
| BLOQUEADA | 5 | 158 (P-1 a P-8), 155 incremento F (D-015), 112 (pendências de produto), 039 (encerramento formal, DP-08) e 031 (Registro Acadêmico). |
| SUBSTITUÍDA | 6 | PRs #374 (→ #375), #487 (→ #488) e #490 (→ #492); o teste A11 da branch de classificação; o estudo "Minhas atividades" da branch; o achado da designação pela presidência (→ #501). |
| INDETERMINADA | 4 | Os estudos de cronogramas (01/11), da configuração da classificação (01/11), da remissão a anexo (19/10) e o achado do PDF dos documentos da convocação (12/11). Têm valor documental; falta você dizer se ainda servem. |

**Nota sobre "concluída".** Das 42 concluídas, **32 ainda declaram no `spec.md` que não foram
implementadas**: "Draft", "só documental", "PR aberto" ou "Em implementação". O mesmo vale para
duas incompletas, a 152 e a 154. O README da raiz está certo para todas, e nenhuma tem falha
funcional. É documentação defasada, e não pendência de produto. A lista está no inventário, §4.

## Riscos reais

1. **Perda da implementação da 123** (UX da Retificação, worktree `upbeat-haslett-9d4178`).
   - São 21 arquivos modificados e 8 novos, de 06/11, com T002–T007 e T012–T017 marcadas.
   - Nada disso está commitado. Remover a worktree apaga tudo.
   - A `main` andou 492 commits desde então, e 5 deles tocam os mesmos arquivos (`retificacoes.py`,
     `retificacao.py`, `retificar.html`) — vêm da 131, da 144 e da 146. Retomar exige integrar.
2. **Perda do código-fonte do filme de apresentação** (`processo-seletivo-video-519ad6/video/`).
   - É fora do git: roteiro, cenas, capturas, `tools` e fontes, cerca de 42 MB.
   - O `video/out/`, de 19 GB, é saída renderizada.
   - O filme de lançamento (#286) é outro, e esse está na `main`.
3. **Commits só locais.** Cinco branches não existem no remoto: dois estudos de 01/11, a auditoria
   de autonomia operacional (13/11), o achado do PDF (12/11) e o achado de 04/11 que o #374 pediu
   para preservar. Apagar a branch apaga o trabalho.
4. **Evidência de validação fora do repositório.**
   - As capturas antes/depois da 160 (T002/T036 e UX-714) são as 37 imagens não rastreadas em
     `gps-candidate-auth-ui-2db0c1`.
   - O `verificacao.md` da 160 afirma que elas existem, mas não diz onde.
5. **Faixa de requisito definida duas vezes.**
   - `134-aviso-de-pendencia-documental` e `134-cenarios-de-treinamento` definem, ambas, a partir de
     **FR-4601**: 23 e 20 identificadores, que se sobrepõem.
   - `test_citacoes_de_requisito.py` une as definições num `set` e não acusa nada. Uma citação
     "FR-4601" no código é ambígua.
   - A `133-guia-visual-conceitos` reusa FR-001 a FR-009 da 001.
   - Não impede a consolidação, mas a rastreabilidade, que é verificada por teste, está furada nesse
     ponto.

## Integridade da `main`

- **CI.** Das 12 últimas execuções na `main`, 10 passaram e 2 falharam:
  - `76ac8ea1`: `test_minha_etapa` casava "CPF" dentro do token CSRF. Corrigido no #523, e as
    execuções seguintes passaram.
  - `6aa1efdd`: teste de navegador da jornada dos documentos, intermitente. Corrigido no #517
    (`e5b30ac6`) e no `68a74df5`.
  - A execução sobre `33546564` estava em andamento ao fim desta auditoria.
  - A suíte não foi rodada localmente, para não disputar o cluster com a sessão em curso.
- **Migrations.** São 118 em 23 apps, e cada app tem uma folha só no grafo. Não há bifurcação.
- **PRs abertos.** Os dois mesclam sem conflito com a `main` (`git merge-tree`) e entre si.
  - [#524](https://github.com/vitofranzosi/processo_seletivo/pull/524): CI verde.
  - [#525](https://github.com/vitofranzosi/processo_seletivo/pull/525): fatias de teste ainda
    rodando.
  - Nenhum PR aberto tem mudança que já esteja na `main`.
- **Resíduos de experiência na `main`.** Nenhum encontrado.
  - Os scripts de estudo estão em `doc/`, como manda a convenção.
  - As entradas do `.claude/launch.json` são versionadas de propósito.
- **Documentação que pode induzir erro.**
  - Os 34 `**Status**` defasados (inventário, §4).
  - O `contexto-para-outro-agente.md` da reavaliação de 12/11 diz que a 158 está "só no PR #492,
    sem merge", mas o #492 foi mergeado.
  - A Visão do Sistema (`docs/visao-sistema/`) está em dia até a 161; só falta o `--dias-atras` do
    #522.
- **Regressões.** Nenhuma regressão funcional foi encontrada nos fluxos críticos. As duas falhas de
  CI eram defeitos de teste, e não de produto. Não houve recaptura pela interface nesta auditoria.

## Veredito

A `main` está consistente: CI verde, sem migration divergente, sem PR obsoleto aberto e sem
regressão conhecida. **As frentes de produto podem ser consideradas encerradas**, exceto:

- as **8 incompletas** e as **5 bloqueadas**, que já estão registradas nas próprias specs;
- os **2 PRs abertos**.

**A limpeza de worktrees e branches ainda não é segura.** Antes, faça os 11 itens de P0.

---

### 1. Pode encerrar agora

- **As 72 worktrees** do apêndice do inventário: integradas, limpas e sem commit exclusivo. As
  sessões delas têm o PR mergeado ou nenhum trabalho próprio.
- **38 das 42 branches locais sem worktree.** Todas, menos `achado-jornada-do-candidato-na-convocacao`,
  `intelligent-robinson-4466a5`, `155-destinacao-completa` e `main`.
- **20 branches remotas** já contidas na `main` (lista no plano, P2).
- **Os PRs fechados sem merge** já estão encerrados e têm sucessor mergeado: #374, #487 e #490.
- **As specs concluídas**: só falta acertar a linha de status (P2), o que não impede encerrar a
  sessão.

### 2. Resolver antes de encerrar

1. Preservar a implementação da 123 (P0-1).
2. Copiar para fora da worktree o código-fonte do filme de apresentação (P0-2).
3. Empurrar ou mergear as cinco branches só locais (P0-3 a P0-7).
4. Decidir o destino dos arquivos não rastreados (P0-8 a P0-11): o tutorial da formalização, as
   capturas da 160, a reavaliação de 12/11, o estudo de 19/10, os PDFs da 104 e as alterações do
   checkout principal no "GPS por Dentro".
5. Decidir o #524 e o #525 (P1).

### 3. Manter aberta

- **A sessão da 156 que está rodando**, com o #525, e a sessão do #524.
- **As specs incompletas**, como trabalho registrado e não como pendência de limpeza: 144 B/C,
  150 fechamento, 152 US2, 154 US2, 155 restante, 156, 161 e 123.
- **As bloqueadas por decisão sua**: 158 (P-1 a P-8), 155 F (D-015), 112 e 039 (DP-08). A 031 está
  bloqueada pelo Registro Acadêmico.
- **As branches que servem de referência**, e por isso não se apagam:
  - as cinco `claude/119-*-previas`, que hospedam imagens de PRs mergeados;
  - a `claude/155-destinacao-completa`, com a tag de mesmo nome, citada pelas specs.
- **As branches `001-decisoes-pendentes` e `002-inserir-documentacao-sistema`.** São de outro
  autor (Vito Franzosi, PR #329 fechado). Têm trabalho exclusivo, e a decisão sobre elas não é
  desta auditoria.
