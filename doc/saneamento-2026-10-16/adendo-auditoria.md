# Adendo de 16/10/2026 à auditoria de 15/10

Este documento complementa, sem substituir ou corrigir retroativamente, o
[relatório original](../auditoria-de-consolidacao-2026-10-15.md) baseado em `main` @ `db428b30`.
Sua matriz e seus totais são fotografias históricas, não contagens atuais reexecutadas.

## Método e alcance

Leitura do histórico, status, refs e arquivos do checkout em
`D:\projetos\cefor\processo_seletivo`, sem fetch ou mutação de refs. A branch atual é
`001-decisoes-pendentes`, HEAD `6fc3a85a9ce58a973dc0e29bc38085dfd055f171`.
Antes desta entrega o checkout estava limpo, inclusive de arquivos não rastreados.
Há uma worktree registrada neste clone; as worktrees históricas da auditoria não estão nele.

O relatório de análise anterior consultou os PRs #283 e #287 no GitHub; esta execução reconferiu
as integrações no histórico local. Nenhuma suíte funcional foi reexecutada para homologar o produto.
A Constituição permanece em 1.2.0, emendada em 28/09/2026, sem alteração nesta fase.

## Mudanças de estado sustentadas por evidência

| Item | Implementação | Integração | Teste automatizado | Homologação / encerramento |
|---|---|---|---|---|
| GO-26 / 073 | Artefatos presentes | PR #283 integrado por `19c7afbc`, em 15/10 às 16h43, horário de Brasília; atualização anterior `6203580d` | PR registra 11294 passando e 12 pulados; não reexecutado aqui | Integração concluída; validações com TI e L4 continuam pendentes (GO-27) |
| GO-46 / 074 | Commit `f9ce2b08`, spec, plano, tarefas, rastreabilidade, código e testes presentes | PR #287 integrado por `6f8f8b50`, em 16/10 às 7h31, horário de Brasília | PR registra 11351 passando e 11 pulados; não reexecutado aqui | Risco histórico de código exclusivamente não commitado superado; T013 continua aberta, sem homologação integral |
| Lote direto | `59fa8380`: ED-07, ED-18, ED-13, PV-03, PV-04 e PV-05a | PR #285, merge `c3dba2e8`, alcançável pelo HEAD | Evidência de integração não equivale a nova execução de testes | Não declarar os itens homologados nesta fase |
| GO-47 / filme | Roteiro e scripts versionados pelo trabalho do PR #286 | Histórico presente no checkout | Não aplicável à integridade dos vídeos ausentes | Arquivos binários e backup não comprovados |

Fontes externas da análise anterior: [PR #283](https://github.com/vitofranzosi/processo_seletivo/pull/283)
e [PR #287](https://github.com/vitofranzosi/processo_seletivo/pull/287).
Fonte da pendência da 074: [tasks.md](../../specs/074-assistente-na-pagina-do-edital-local/tasks.md).
A integração não estende a 074 à produção: seu escopo continua exclusivamente local.

O estado histórico `CONFLICTING/DIRTY` do #283 foi superado pela integração. Não há conflito de
merge pendente desse PR a resolver agora. Não se infere conflito atual a partir de `mergeable=false`
em PR encerrado, nem se atribui um arquivo conflitante sem evidência. As diferenças da branch
local `main` são outro assunto, detalhado no [diagnóstico](diagnostico-git.md).

## Pendências abertas

| Item | Estado atual | Evidência que falta |
|---|---|---|
| GO-09 | Pendente de comprovação pelo titular | Revogação da chave exposta e análise sanitizada de consumo posterior |
| GO-47 | Localização física e cópia dos binários não confirmadas | Manifestos da origem/destino, hashes iguais, reprodução e responsável |
| Bancos `ps_filme` / `ps_video` | Existência atual não consultada | Inventário na máquina de origem, backup e restauração autorizados |
| CA-23 | Texto ambíguo ainda presente | Aprovação da redação; futura alteração rastreável e regressão |
| DEC-01 a DEC-16 | Aguardam deliberações específicas | Registro expresso por item; decisões históricas não aprovam recomendações novas |
| GO-27 e T013 da 074 | Validação operacional pendente | Ambiente, participantes e autorizações específicas; nenhuma chamada real feita |
| Divergência `main` local | Trabalho exclusivo a preservar | Revisão dos cinco arquivos antes de qualquer integração |

Na pasta local `filme-de-lancamento/` foram medidos 46 arquivos, somando **481638 bytes**, de fontes
e roteiro. `video/` não existe neste checkout. Não foram encontrados `.mp4`, `.mov` ou `.webm`
na varredura local. Os tamanhos históricos de 2,1 GB e 19 GB não foram medidos de novo e não devem
ser tratados como presença atual. Ausência neste clone não comprova exclusão na máquina de origem.

## Governança preservada

Nada foi marcado como decisão ratificada com base em merge, teste verde ou relato do agente.
O status quo permanece até decisão competente. Piloto-sombra com dados reais não está dispensado
de avaliação de proteção de dados. A recomendação sobre efeitos de retificação é proposta de
produto sujeita ao setor competente, sem conclusão jurídica nesta entrega.
