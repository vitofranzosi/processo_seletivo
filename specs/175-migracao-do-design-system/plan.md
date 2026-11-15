# Implementation Plan: A migração do design system para toda a gestão

**Branch**: `claude/173-migracao-ds-antes-e-depois` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/175-migracao-do-design-system/spec.md`

## Summary

Os padrões que o usuário aprovou no piloto da `172` saem da classe de escopo `.piloto-ds` e vão para
as folhas comuns da gestão. O texto perde a medida `--leitura`, o indicador vira grade de partes
iguais, o campo ocupa a largura do formulário, a lista de definição põe o rótulo e o valor na mesma
linha, e o aviso, o cartão e o botão ganham o desenho do piloto. O resultado é medido pelo rastreio do
estudo nas 123 telas, na `main` e na branch, sobre a mesma cópia da referência. **Este plano é
retrospectivo**: a branch foi feita antes da spec, a pedido do usuário (ver o status da spec).

## Technical Context

**Language/Version**: CSS em arquivo estático, templates do Django; Python 3.12 para os guardiões e os
scripts de medida.

**Primary Dependencies**: nenhuma nova. O instrumento do estudo (`medicoes/`), o Playwright do grupo
`navegador` e, para comparar pixels, o Pillow, por `uv run --with pillow`, fora do projeto.

**Storage**: nenhuma mudança. O rastreio usa `ps_piloto_validacao`, a cópia migrada da referência.

**Testing**: os guardiões de `tests/interface` (folha, larguras, acessibilidade) e a suíte contra
PostgreSQL.

**Target Platform**: a gestão no navegador.

**Project Type**: monólito web (Django), só camada de interface.

**Performance Goals**: nenhuma consulta nova.

**Constraints**: CSP sem estilo nem script no template; tokens num lugar só; guardiões que leem a
folha como texto; nenhum texto gerado pela folha (D-002).

**Scale/Scope**: 3 folhas comuns, 14 folhas de grupo e de tela, 4 templates e 5 arquivos de teste.

## Constitution Check

| Princípio | Como a migração o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | nenhum texto muda (FR-7906) | passa |
| II. Imutabilidade | nenhuma regra de negócio nem migration | passa |
| III. Segurança | nenhuma permissão, rota ou escopo muda | passa |
| IV. Regras explícitas | a contradição com a FR-7702 da `172` está escrita (FR-7910, D-003) | passa |
| V. Rastreabilidade | **a implementação veio antes da spec**, a pedido do usuário; esta spec e as tarefas registram o feito, e a revisão o apontou. A exceção à ordem dos artefatos foi **aceita pelo usuário em 15/11/2026** ("Aceito a exceção"); o aceite não cobre a validação nem a aprovação | exceção aceita pelo usuário |
| VI. Completude de jornada | a capacidade é a mesma ação, em telas que usam a largura; o cenário demonstrável é a equipe fazendo as tarefas do roteiro nas duas versões, que **ainda não aconteceu** (SC-2704) | pendente da validação |

## Project Structure

### Documentation (this feature)

```text
specs/175-migracao-do-design-system/
├── spec.md
├── plan.md
├── tasks.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/static/interface/
├── gestao/componentes.css      # sem a medida do parágrafo; o indicador em grade
├── gestao/formularios.css      # o campo na largura do formulário
├── gestao/telas.css            # o cartão, o aviso, o botão, o respiro, a lista de definição
├── grupos/*.css, telas/*.css   # sem as medidas de leitura
├── grupos/piloto-ds.css        # só o que a comum não tem (FR-7908)
└── grupos/confirmacao-de-ato.css   # retirada (FR-7907)

backend/tests/interface/        # test_larguras, test_polish_da_056, test_polish_da_058,
                                # test_folha_estatica, test_confirmacao_do_encerramento, conftest

doc/auditoria-design-system-2026-11-14/migracao/   # o antes e o depois e os scripts
```

**Structure Decision**: as folhas comuns, porque os padrões são de componente (D-001).

## Complexity Tracking

| Ponto | Por que | Alternativa, e por que não |
|---|---|---|
| 110 telas mudam de uma vez | os padrões são de componente, e o usuário pediu o antes e o depois de tudo | família por família: cinco specs antes de o usuário ver o resultado |
