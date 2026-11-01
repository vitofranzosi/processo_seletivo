# Parecer técnico — A-03: imutabilidade no banco (diagnóstico dirigido)

**Data:** 01/11/2026 · **Base:** `main` em `06226ef1` · **Natureza:** diagnóstico (seções 1–9) e
implementação (seção 10). No diagnóstico nenhuma migration entrou na árvore: a medição da seção 5
usou uma migration provisória, descartada sem commit.

**Pergunta:** qual é o menor conjunto de alterações no PostgreSQL que resolve A-03 sem bloquear o
que o GPS já faz?

**Resposta curta:** três gatilhos condicionais — Inscrição enviada, documento de inscrição enviada e
Homologação — e um quarto, também condicional, na Avaliação concluída, que admite exatamente a
reabertura. Nenhuma tabela entra em `TABELAS_APPEND_ONLY`, e o total `46` não muda. Identidade e
credenciais **ficam fora**: a proposta original para elas (revogar `DELETE` de
`identidade_candidateidentity`) quebraria a retomada da `010`. O custo do PR não está no SQL — está
nas fixtures de teste que mudam inscrição já enviada pelo queryset (seção 5).

---

## 1. Matriz

| | Inscrição (`inscricoes_inscricao`) | Documento (`inscricoes_documentosubmetido`) | Avaliação (`avaliacoes_avaliacao`) | Homologação (`publicacoes_homologacao`) | Identidade / credencial (`identidade_*`) |
|---|---|---|---|---|---|
| **Estados** | `RASCUNHO`, `SUBMETIDA` | sem estado próprio; herda o da Inscrição | `RASCUNHO`, `CONCLUIDA` | vigente (`revoked_at` nulo) ou revogada | sem estado |
| **Criação** | `abrir_rascunho` (`rascunho.py`) | `anexar_documento` | na Atribuição (Distribuição) | `homologate_edital` (`publish_edital.py:551`) | primeiro acesso, reconciliação, `adicionar` |
| **Atualização legítima** | só em `RASCUNHO`: `compare_and_swap` em `rascunho.py:297`, `reconhecer_versao` (`submissao.py:148`) e a própria transição no envio (`submissao.py:424`, a partir de `RASCUNHO`) | substituição só com a Inscrição em `RASCUNHO` (`_rascunho_travado`) | `gravar` em rascunho; `concluir` (RASCUNHO→CONCLUIDA); **`reabrir`** (CONCLUIDA→RASCUNHO, `avaliacao.py:564`) | **uma vez**: preencher `revoked_at`, `revoked_by`, `revocation_reason` (`publish_edital.py:655-658`) | `gravar_nucleo` (nome sempre; CPF até a 1ª enviada, FR-008 da 010); `tornar_principal`; `retomar` move credenciais de identidade |
| **Exclusão legítima** | nenhuma | `remover_documento` e o descarte em `reconhecer_versao`, ambos em `RASCUNHO` | nenhuma | nenhuma | `remover` credencial (FR-018); `retomar` **apaga a identidade vazia** (`associacao.py:238`, FR-054/055 da 010) |
| **Gatilho de imutabilidade** | `OLD.status = 'SUBMETIDA'` | Inscrição-mãe `SUBMETIDA` | `OLD.estado = 'CONCLUIDA'` | sempre, exceto a revogação | — |
| **Campos imutáveis** | todos (FR-054, FR-064 da 009; docstring de `Inscricao.save`) | todos, inclusive a inserção de novo documento | todos, salvo o que a reabertura zera | `revisao`, `homologated_by`, `reason`, `homologated_at`; `revoked_*` depois de preenchidos | `subject` (FR-042), nunca alterado por código |
| **Exceção legítima** | nenhuma no código de produção | nenhuma | reabertura: `estado→RASCUNHO`, `concluida_em→NULL`, `concluida_por→''`, `versao→NULL`, `revision` avança; o resto igual | a revogação acima | as da linha "exclusão" e "atualização" |
| **Proteção na aplicação** | `Inscricao.save()` (recusa total se enviada); `_rascunho_travado` | `DocumentoSubmetido.save/delete`; `_rascunho_travado` | `compare_and_swap` + `_recusar_se_fundamenta_resultado`; `ConclusaoAvaliacao` append-only | nenhuma no modelo; só o comando | regras em `credenciais.py` e `associacao.py` |
| **Proteção no PostgreSQL** | `ck_inscricao_submetida_completa`, `ck_inscricao_submetida_com_cpf` (forma, não imutabilidade) | nenhuma | `ck_avaliacao_concluida_completa`, `uq_avaliacao_concluida_por_pessoa`; `ConclusaoAvaliacao` em `TABELAS_APPEND_ONLY` | nenhuma | unicidades de credencial |
| **Lacuna demonstrada** | `QuerySet.update()` e SQL alteram nome, CPF, modalidade e status da enviada | `UPDATE`/`DELETE`/`INSERT` em documento de enviada | reescrever a nota de concluída sem reabrir | reescrever autoria e motivo | ver seção 3 |
| **Correção mínima** | gatilho condicional (molde `requerimentos/0002`) | gatilho que lê a Inscrição-mãe (molde `alteracao_normativa` da `publicacoes/0007`) | gatilho condicional que admite só a reabertura | gatilho que admite só a revogação | nenhuma mudança neste PR; registrar a decisão |
| **Classe** | **A** | **A** | **A** | **A** | **B** (decisão) / **C** (o resto) |

## 2. O que mudou desde o diagnóstico original

O A-03 da auditoria de 31/10 acertou o diagnóstico das quatro primeiras e errou o remédio da quinta.

1. **`identidade_candidateidentity` tem exclusão legítima.** A auditoria diz que "não há caminho
   legítimo de exclusão" e propõe revogar `DELETE`. Há: `retomar` (`associacao.py:213-239`) descarta
   a identidade vazia depois de mover as credenciais, numa operação só (FR-054/055 da 010), com
   teste próprio em `test_retomada.py` e `test_retomada_concorrente.py`. Revogar `DELETE` quebraria
   a retomada em produção — exatamente a classe de A-01.
2. **`identidade_candidateemail` não é peça de ato.** O `DELETE FROM identidade_candidateemail → 12`
   da auditoria é uma operação que a própria spec manda permitir (FR-018), e a 010 diz que
   "credencial é como se entra, não o que se enviou" (FR-019, `credenciais.py:150-156`). O endereço
   que consta do ato é `Inscricao.email`, que o gatilho da Inscrição passa a cobrir.
3. **Inserção de documento** não estava no diagnóstico original: além de `UPDATE`/`DELETE`, um
   `INSERT` de documento novo numa inscrição enviada também acrescenta o que a comissão vê. O
   gatilho cobre as três operações.
4. **A Avaliação concluída não é "imutável exceto reabertura" no sentido frouxo**: a reabertura tem
   forma exata (quatro colunas zeradas, o resto igual), e o gatilho pode exigi-la campo a campo em vez
   de admitir qualquer `UPDATE` que leve a `RASCUNHO`. Sem isso, um `UPDATE ... SET estado =
   'RASCUNHO', pontuacao = 99` passaria como "reabertura".
5. **"Os testes de imutabilidade existentes ganham as novas tabelas"** não vale como foi escrito:
   `test_as_tabelas_append_only_sao_exatamente_as_que_recusam_mutacao_no_modelo` exige que todo
   modelo cujo `delete` fale em "append-only" esteja em `TABELAS_APPEND_ONLY`. Os testes novos são
   casos próprios, e nenhum `delete` de modelo deve passar a dizer "append-only".

## 3. Proposta por entidade

**Inscrição — A.** Molde exato da `requerimentos/0002`:

```sql
CREATE TRIGGER inscricao_enviada_imutavel
BEFORE UPDATE OR DELETE ON inscricoes_inscricao
FOR EACH ROW WHEN (OLD.status = 'SUBMETIDA')
EXECUTE FUNCTION reject_submitted_enrollment_mutation();
```

O envio (`OLD.status = 'RASCUNHO'`), a edição do rascunho e o `reconhecer_versao` passam. Nenhum
caminho de produção altera ou apaga inscrição enviada — conferido por `grep` em `processo_seletivo/`:
as duas escritas fora de `inscricoes/` são do `seed_demo` (`:1229`, `:1397`) e são a própria
transição a partir de `RASCUNHO`.

**Documento — A.** Gatilho `BEFORE INSERT OR UPDATE OR DELETE`, sem `WHEN`, lendo o status da
Inscrição-mãe (de `OLD` e de `NEW`, para que mover um documento de inscrição também seja coberto),
com `RETURN OLD`/`RETURN NEW` como a `alteracao_normativa` da `publicacoes/0007` já explica.

*Concorrência.* A aplicação já serializa: todo caminho de escrita de documento e o envio tomam
`select_for_update` na Inscrição (`_rascunho_travado`, `rascunho.py:444`). Para que a garantia do
banco não dependa disso, a leitura no gatilho deve ser `SELECT status ... FOR SHARE`: ela conflita
com o `FOR NO KEY UPDATE` que o `UPDATE` do envio toma, de modo que uma escrita concorrente espera o
envio terminar e então relê `SUBMETIDA` e recusa. A trava da chave estrangeira (`FOR KEY SHARE`) não
basta, porque não conflita com o `UPDATE` do envio. `FOR SHARE` exige privilégio de `UPDATE` em
`inscricoes_inscricao`, que a runtime tem e continua tendo — a tabela não é append-only, e é por isso
que a lição de A-01 não se aplica aqui. Dentro dos fluxos da aplicação a linha já está travada pela
própria transação, e o `FOR SHARE` não espera nada.

**Avaliação — A.** `WHEN (OLD.estado = 'CONCLUIDA')`, e a função admite só a forma exata da
reabertura: `NEW.estado = 'RASCUNHO'`, `concluida_em IS NULL`, `concluida_por = ''`, `versao_id IS
NULL`, e `atribuicao_id`, `identity_subject`, `etapa_id`, `inscricao_id`, `forma`, `pontuacao`,
`sentido`, `parecer` iguais (`IS NOT DISTINCT FROM` nos anuláveis). `DELETE` recusado. A conclusão
anterior continua preservada em `ConclusaoAvaliacao`, que já é append-only nas duas camadas.

O que fica fora, deliberadamente: o gatilho **não** confere que exista `ConclusaoAvaliacao` para a
conclusão reaberta, nem que nenhum Resultado vigente se funde nela (`_recusar_se_fundamenta_resultado`).
As duas seriam garantias novas, além do que A-03 pede — **C**.

**Homologação — A.** Gatilho sem `WHEN`: `DELETE` recusado; `UPDATE` admitido só com
`OLD.revoked_at IS NULL` e `id`, `revisao_id`, `homologated_by`, `reason`, `homologated_at` iguais.
Revogar duas vezes ou reescrever a revogação passa a ser recusado. Sem `save`/`delete` que recusem
no modelo, para não acionar o guardião da seção 2, item 5.

**Identidade e credenciais — sem mudança neste PR.**

- `candidateemail`: nenhuma. Exclusão e troca de principal são operações previstas (FR-018, FR-019);
  credencial não integra ato administrativo. **C** qualquer proteção aqui.
- `candidateidentity`, exclusão: a regra real é "só sem inscrição" (`esta_vazia`). Um gatilho que
  recusasse `DELETE` quando houver `inscricoes_inscricao.identity_subject = OLD.subject` exprimiria
  isso sem quebrar a retomada. Mas a proteção relevante — a inscrição enviada — já fica coberta pelo
  gatilho da Inscrição, e o descarte de identidade é matéria da política de retenção (B-2, A-31/A-32).
  **B**: decidir junto com B-2.
- `candidateidentity`, CPF congelado depois da primeira enviada (FR-008 da 010): exprimível por
  gatilho que consulta `inscricoes_inscricao`, mas a spec diz que a correção passa a ser "ato
  institucional, fora desta feature" — procedimento que não existe. Um gatilho hoje obrigaria esse
  procedimento futuro a nascer como migration. **B**.
- `subject` imutável (FR-042): nenhum código o altera, e um gatilho de coluna seria trivial. Útil,
  mas não é o que A-03 aponta. **C**.

A decisão "identidade e credenciais protegidas só pela aplicação" deve ficar escrita — no comentário
de `TABELAS_APPEND_ONLY` em `seguranca/papeis.py`, que é onde a auditoria notou a ausência dela.

## 4. Riscos de bloquear operação legítima

| Risco | Avaliação |
|---|---|
| Rascunho, envio, `reconhecer_versao` | passam: `OLD.status` é `RASCUNHO` em todos |
| Substituir/remover documento antes do envio | passa |
| Documento depois do envio | recusado, como FR-054 manda |
| Concluir e reabrir avaliação | passam; reabertura com outra forma é recusada |
| Revogar homologação | passa uma vez |
| Retomada, troca de principal, remoção de credencial | intocadas |
| Migration de dados futura sobre inscrição enviada | passa a falhar, e é o ponto: terá de desligar o gatilho explicitamente, como `resultados/0004` já faz com `resultado_etapa_append_only` |
| Política de retenção (B-2) | **não fica inviabilizada**: anonimizar ou eliminar inscrição enviada depois do prazo passará a exigir uma migration que ajuste o gatilho — a decisão continua aberta, só deixa de poder ser tomada por um `UPDATE` silencioso |
| Retificação de inscrição (FR-054 diz "nesta versão") | mesma resposta: a feature que a criar ajusta o gatilho |
| `TRUNCATE` da limpeza da suíte | gatilhos de linha não disparam em `TRUNCATE` |

## 5. Medição: o que o PR terá de mudar nos testes

Para medir em vez de estimar, os quatro gatilhos da seção 3 foram instalados por uma migration
provisória e a suíte rodou inteira contra PostgreSQL (4 workers, `worksteal`, 595 s, banco
`ps_a03_medicao`). Depois a migration foi apagada, sem commit.

**Resultado: 128 falhas e 737 erros (865 casos), contra 13 369 passando.** Uma falha é o guardião
de contagem de migrations por app, esperado. Todo o resto vem do **gatilho da Inscrição**, e de
**onze pontos de teste**, nenhum de código de produção. Os gatilhos do documento, da Avaliação e da
Homologação **não derrubaram nenhum caso** — e os fluxos que eles poderiam bloquear (substituir
antes do envio, concluir, reabrir, homologar, revogar) estão todos exercitados pela suíte.

| Origem (o `update` sobre inscrição já enviada) | Casos nos tracebacks | O que faz |
|---|---|---|
| `tests/fixtures/divulgacao.py:254` | 396 | declara a modalidade depois de `inscrever` |
| `tests/fixtures/recortes.py:155` (`declarar`) | 77 | autodeclaração depois do envio |
| `tests/fixtures/ocupacao_sorteada.py:177` | 14 | idem |
| `tests/fixtures/sorteio.py:182` | 14 | idem |
| `tests/performance/test_ordenacao.py:180` | 2 | idem, em escala |
| `test_progressao_com_corte.py:271`, `matriculas/test_recusas.py:148` | 1 + 1 | idem |
| `portal/test_hora_do_envio.py:48` | 1 | retroage `submitted_at` |
| `avaliacoes/test_distribuicao.py:140`, `inscricoes/test_lista_exigida_imutavel.py:70` | 1 + 1 | devolvem a enviada a `RASCUNHO` para simular estado proibido |
| `inscricoes/test_fatos_congelados.py:104` | 1 | edita o nome da enviada para provar que o fato não muda |

(Os tracebacks impressos cobrem 510 dos 865 casos; o resto é o mesmo erro de *setup* repetido nas
fixtures acima, que o xdist não reimprime.)

**O padrão é um só:** as fixtures enviam primeiro e declaram a modalidade depois, pelo queryset — o
docstring de `recortes.declarar` diz isso com todas as letras ("gravada pelo queryset como todo
campo de Inscrição submetida"). A correção recomendada é **passar a modalidade para dentro de
`inscrever`** (`tests/fixtures/comissao.py:169`), cujo `update` já é a transição
`RASCUNHO→SUBMETIDA` e pode levar `modality_id` junto — um parâmetro `modalidades` (uma para todas,
ou por índice). Isso resolve os sete primeiros pontos, que são 99% dos casos, sem desligar gatilho.
Os quatro restantes simulam de propósito um estado que o banco passa a proibir: esses desligam o
gatilho no próprio caso, como `recursos/test_admitir.py:243` já faz, ou — no de `fatos_congelados`
— passam a afirmar a recusa.

## 6. Testes do PR

Um arquivo por entidade, ao lado dos existentes (`tests/integration/inscricoes/`, `avaliacoes/`,
`publicacoes/`), marcados como os da `029` para pular fora do PostgreSQL:

- **Recusas**, cada uma por `QuerySet.update()`, `QuerySet.delete()` e SQL cru, sob `como_producao`
  (`tests/fixtures/papel_de_producao.py`) — inscrição enviada (nome, CPF, modalidade, status de volta
  a `RASCUNHO`, exclusão); documento de enviada (alterar, apagar, inserir); avaliação concluída
  (nota, parecer, reabertura com nota alterada, exclusão); homologação (autoria, motivo, segunda
  revogação, exclusão).
- **Fluxos preservados**, pelos comandos e sob `como_producao`: editar rascunho, anexar, substituir,
  remover, `reconhecer_versao`, enviar; concluir, reabrir pela presidência e conferir a
  `ConclusaoAvaliacao`; homologar e revogar. Os fluxos de credencial já têm testes e não mudam.
- **Concorrência**: duas conexões; a primeira faz o `UPDATE` do envio sem confirmar, a segunda tenta
  inserir documento e fica esperando; a primeira confirma, a segunda é recusada. O molde está em
  `test_lista_exigida_concorrencia.py`.
- **Reversibilidade**: o guardião `test_every_migration_declares_a_reverse_path` já cobra; acrescentar
  um caso que desaplica e reaplica a migration e confere os gatilhos em `pg_trigger`.
- **Guardiões que mudam por construção**: a contagem de migrations por app (`inscricoes` ganha uma).
  `TABELAS_APPEND_ONLY`, o `46` do provisionamento e o CLAUDE.md **não** mudam.

## 7. Complexidade e implantação

- **Uma migration** (em `inscricoes`, dependendo de `avaliacoes/0003` e `publicacoes/0011`), ~120
  linhas de SQL no padrão existente, sem percorrer linha nenhuma: instala gatilhos e não toca dados.
- **Implantação**: `CREATE TRIGGER` toma `SHARE ROW EXCLUSIVE` nas quatro tabelas por instantes; sem
  reescrita de tabela. Reversão por `migrate inscricoes 0006`.
- **Risco principal**: um fluxo legítimo que nenhum teste exercita e que muta inscrição enviada. A
  varredura não encontrou nenhum em `processo_seletivo/`, e a execução da seção 5 confirma: todas
  as falhas vieram de testes.
- **Estimativa**: um dia. O SQL e os testes novos são meio dia; o parâmetro em `inscrever` e os
  quatro casos avulsos, a outra metade, com uma rodada completa da suíte para fechar.

## 8. Decisões realmente pendentes

1. **Identidade e credenciais ficam só com proteção de aplicação?** Recomendação: sim, registrado em
   `papeis.py`; revisitar com B-2.
2. **O CPF congelado da identidade (FR-008 da 010) vai para o banco?** Depende de existir o "ato
   institucional" de correção. Recomendação: não agora.
3. Não é decisão de produto, mas de forma: as fixtures passam a gravar a modalidade na transição
   (recomendado), em vez de desligar o gatilho em ~500 casos.

## 9. O PR pequeno

**Cabe num PR só:** os quatro gatilhos (Inscrição, documento, Avaliação, Homologação), os testes da
seção 6, o ajuste das fixtures e uma linha em `papeis.py` registrando por que `identidade_*` fica
fora. **Exige decisão antes:** os dois itens **B** da identidade. **Fica fora:** os itens **C**.

---

## 10. Implementação (01/11/2026)

A direção da seção 9 foi aprovada e implementada no mesmo dia, num PR só.

**Migrations — uma por app, cada gatilho junto da tabela que protege:**

| Migration | Gatilho | Admite |
|---|---|---|
| `inscricoes/0007_imutabilidade_da_enviada` | `inscricao_enviada_imutavel` (`WHEN OLD.status = 'SUBMETIDA'`) | rascunho, `reconhecer_versao`, o envio |
| idem | `documento_da_enviada_imutavel` (`INSERT`/`UPDATE`/`DELETE`, lê a mãe com `FOR SHARE`, em `OLD` e `NEW`) | anexar, substituir e remover no rascunho |
| `avaliacoes/0004_imutabilidade_da_concluida` | `avaliacao_concluida_imutavel` (`WHEN OLD.estado = 'CONCLUIDA'`) | a forma exata da reabertura: quatro colunas zeradas, revisão maior, o resto igual |
| `publicacoes/0012_imutabilidade_da_homologacao` | `homologacao_imutavel` | preencher a revogação uma vez, com a homologação vigente e o resto igual |

`TABELAS_APPEND_ONLY` e o total `46` não mudaram. O comentário que a precede em `seguranca/papeis.py`
passou a dizer por que as quatro tabelas ficam de fora, e por que `identidade_*` não tem camada de
banco nenhuma — decisão, e não esquecimento, à espera de B-2 e da correção institucional de CPF.

**Limite da garantia da Avaliação, dito na migration e num teste.** O gatilho garante a *forma* da
transição, e não *quem* a pratica: um `UPDATE` cru que reproduza exatamente a reabertura passa
(`test_o_limite_o_banco_nao_autentica_quem_reabre`). Autorização da presidência, motivo, ato e
trilha continuam sendo da aplicação; nenhum mecanismo de autorização foi criado no banco.

**Fixtures.** Os sete pontos que declaravam a Modalidade depois do envio passaram a gravá-la **na
transição**: `inscrever(…, modalidades=…)` (uma para todas, ou `{posição: Modalidade}`), repassada
por `montar_cenario_do_corte`, `montar_cenario_7_1_2`, `montar_cenario_da_ocupacao`,
`montar_cenario_da_convocacao` e `montar_cenario_da_exportacao`. O helper `recortes.declarar`, que
gravava pelo queryset sobre a enviada, saiu. Dos quatro casos avulsos:

- `avaliacoes/test_distribuicao.py` e `inscricoes/test_lista_exigida_imutavel.py` passaram a criar
  um rascunho de verdade, em vez de devolver a enviada a `RASCUNHO`;
- `inscricoes/test_fatos_congelados.py` edita o perfil pela identidade (`gravar_nucleo`), que é por
  onde a pessoa o edita;
- `portal/test_hora_do_envio.py` e `classificacao/test_ordem_sem_reserva_nao_muda.py` usam o único
  desvio, `sem_imutabilidade_da_enviada()` (`tests/fixtures/comissao.py`), cada um com a razão
  escrita no caso: o primeiro precisa de um envio às 23h58 de um dia fixo; o segundo compara a ordem
  sobre as **mesmas** linhas antes e depois da autodeclaração. O desvio desliga os dois gatilhos só
  pelo bloco e os religa no `finally`; um caso próprio prova que a recusa volta depois dele.

**Um 12º ponto, que a medição não viu.** A seção 5 leu 510 dos 865 tracebacks e atribuiu o resto às
mesmas fixtures. A primeira rodada completa depois do ajuste achou mais um:
`avisos/test_aviso_do_resultado.py::test_sem_endereco_fica_registrado_e_fora_do_envio` apagava o
e-mail de uma enviada para exercitar o aviso sem endereço. Ele também passou ao desvio, com a razão
escrita — o cenário nasce de `inscrever`, que sempre grava endereço.

**Testes permanentes** (todos sob `como_producao`, por `QuerySet.update()`, `bulk_create` e SQL cru):
`inscricoes/test_enviada_imutavel.py`, `avaliacoes/test_concluida_imutavel.py`,
`publicacoes/test_homologacao_imutavel.py`, e `test_as_migrations_do_a03_se_desfazem_e_se_refazem`
em `tests/migrations/test_migrations.py`, que também passou a listar os quatro gatilhos.

**A corrida, nas duas ordens.** Envio primeiro: a escrita por fora espera o `FOR SHARE`, relê
`SUBMETIDA` e é recusada. Escrita primeiro: o envio espera, lê o documento que ela gravou e passa.
Nenhuma das duas fica presa. **Contraprova**: com o `FOR SHARE` retirado da função, os dois casos
falham — na primeira ordem o documento **entra** na inscrição recém-enviada, que é exatamente a
janela que a trava fecha.

**Um detalhe que a matriz não previa.** `Inscricao.objects.filter(…).delete()` sobre a enviada já
parava antes do banco, no `PROTECT` de `ItemDaListaExigida.inscricao`; a exclusão é exercitada por
SQL cru, onde só o gatilho a recusa.

**Revisão final (01/11/2026).** Duas condições conferidas a pedido da revisão do PR, e as duas
endurecidas:

- *Revisão na reabertura.* `compare_and_swap` (`shared/concurrency.py`) grava sempre
  `revision = revision + 1`, e é por ele que `reabrir` escreve. O gatilho passou de
  `NEW.revision > OLD.revision` para `NEW.revision = OLD.revision + 1`; uma reabertura que não
  avança ou que salta a revisão é recusada (`test_reabertura_com_outra_revisao_e_recusada`).
- *Motivo da revogação.* O contrato exige (`MotivoRequest`, `required: [reason]`, `minLength: 1`,
  em `specs/001…/contracts/openapi.yaml`) e a tela também (`exige_motivo=True`), mas o comando
  `revoke_homologation` não conferia — ao contrário do vizinho `devolver_edital`, que recusa com
  `reason_required`. O comando passou a recusar do mesmo jeito, e o gatilho a exigir
  `btrim(revocation_reason) <> ''`. Nenhuma regra nova: as três camadas passaram a dizer o que o
  contrato já dizia.
