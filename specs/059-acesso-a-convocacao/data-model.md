# Data Model: O caminho do candidato até a convocação e o Requerimento de Matrícula

**Feature**: [spec.md](spec.md) · **Data**: 2026-10-06

**Nenhuma tabela, coluna, migration ou gatilho novo.** Esta feature lê o que a `019` e a `029` já
gravam. O que segue descreve as **leituras derivadas** que as telas consomem — nenhuma delas é
persistida.

## Convocação vigente da inscrição

| Atributo | Origem | Regra |
|---|---|---|
| convocação | `Convocacao` com `inscricao` = a da linha | A mais recente por `criado_em` entre as que ninguém sucedeu (`D-001`) |
| desfecho | `desfecho_de(convocacao)` | O vigente da cadeia de desfechos, ou nenhum |
| enviada em | `envio_de(convocacao)` | O envio bem-sucedido mais recente, ou nenhum |
| estado de prazo | `estado_de(convocacao, agora)` | `CONVOCADO_PRAZO_NAO_INICIADO`, `CONVOCADO_PRAZO_EM_CURSO`, `CONVOCADO_VENCIMENTO_DECORRIDO` — ou desfecho registrado |
| aberta | derivado | sem desfecho vigente |
| concluída | derivado | com desfecho vigente |

**Transições.** Nenhuma nesta feature. A convocação nasce, é comunicada, sucedida e desfechada pelos
atos da `019` e da `050`; a leitura acompanha o que eles gravaram.

**Escopo da leitura.** Só inscrições da identidade autenticada, e só as **enviadas** — rascunho não é
convocado (Assumptions da spec).

## Estado de leitura do requerimento

Lido de `requerimentos.application.preencher.apurar(inscricao, conteudo)` →
`Disponibilidade.estado_de_leitura` (`FR-405` da `029`). Os cinco valores e o que cada um mostra
estão na `D-007`. **Consultado só onde há convocação vigente** (`D-006`).

## O que cada tela recebe

| Tela | Recebe | Consulta o requerimento? |
|---|---|---|
| Minhas inscrições | por item: `convocacao_aberta` (bool) e `convocacao_concluida` (rótulo do desfecho, ou vazio) | **Não** (`D-002`) |
| Acompanhar | `convocacao` (o bloco acima, ou nada) e `requerimento` (estado de leitura, ou nada) | Só com convocação vigente |
| Convocação | o que já recebe, mais `requerimento` | Só com convocação vigente |
