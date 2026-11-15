# Implementation Plan: O piloto do design system em três telas

**Branch**: `claude/172-piloto-do-design-system` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/172-piloto-do-design-system/spec.md`

## Summary

Aplicar a direção experimental do estudo de 14/11 (neutros da entrada, cabeçalho de página, três
composições, botão, indicador, aviso, cartão) a cinco templates (`confirmar.html`, `ocupacao.html`,
`ocupacao_acrescimo.html`, `ocupacao_nao_preenchida.html` e `lista.html`), por uma folha de grupo
nova, `grupos/piloto-ds.css`, com toda regra sob a classe `.piloto-ds`, num contêiner dentro do bloco
`conteudo`. Os tokens novos se acrescentam a `tokens.css`, e nada do resto muda. O conteúdo, as ações,
a fonte e os tamanhos ficam como estão.

O aceite tem três peças, e duas delas existem antes de qualquer estilo:

1. **A fotografia**: uma jornada de navegador nova, sob demanda, que monta pelas fixtures da suíte
   cada um dos 63 estados do catálogo (D-004), abre a tela com o papel certo nas cinco larguras e
   grava a captura e o inventário de conteúdo. Ela roda uma vez sobre a `main` (o "antes") e uma vez
   sobre a branch (o "depois").
2. **A comparação**: um script fora da suíte que compara os inventários e confere as sequências
   declaradas, nas duas ordens; mais o rastreio da referência da P0, para o "nada fora muda".
3. **A validação**: duas ou três pessoas da equipe, as mesmas seis tarefas nas duas versões, em dois
   servidores sobre cópias do banco da referência acrescido dos estados que as tarefas pedem.

O piloto termina num relatório para o usuário, que decide se a migração continua.

## Technical Context

**Language/Version**: Python 3.12, Django (o do `pyproject.toml`); HTML de template do Django; CSS em
arquivo estático, sem pré-processador.

**Primary Dependencies**: nenhuma nova. Playwright e Chromium do grupo opcional `navegador`, já
instalado no CI; o instrumento do estudo (`medicoes/metricas.js`, `medicoes/largura.js`) e os
scripts de `referencia-p0/`.

**Storage**: PostgreSQL. Nenhuma migration, modelo ou tabela; o `M` das append-only não muda. Dois
bancos de trabalho locais para a validação (`ps_piloto_antiga`, `ps_piloto_nova`), restaurados da
cópia da referência, fora do produto.

**Testing**: a suíte contra PostgreSQL (`make test-pg`), com os guardiões de folha e de acessibilidade
que já existem; a jornada de fotografia sob demanda (`PILOTO_DS_FOTOGRAFIA=<pasta>`); a comparação e
o rastreio, fora da suíte.

**Target Platform**: a gestão no navegador, de 320 a 1920 px, com zoom de 200% e 400%.

**Project Type**: monólito web (Django), só camada de interface.

**Performance Goals**: nenhuma consulta nova nas cinco telas (FR-7713). A Lista continua no orçamento
de consultas da `129`.

**Constraints**: CSP sem `unsafe-inline` (nada de `style=`, `<style>`, `<script>` nem `on*=` no
template); nenhuma regra fora do escopo; nenhum seletor existente mudado; guardiões que leem a folha
como texto (sem `}}` nem `%}` na folha); classe citada nasce com regra; os scripts que selecionam por
classe (`rascunho.js`, `remocao.js`, `visualizador.js`, `envio.js`) não alcançam as cinco telas, e a
T003 confirma.

**Scale/Scope**: 5 templates, 1 folha nova, 1 arquivo de tokens acrescido, 63 estados × 5 larguras,
6 tarefas de validação, 2 ou 3 pessoas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o piloto o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | nenhum texto muda (FR-7707, FR-7710); a marca de espécie da P0 fica | passa |
| II. Imutabilidade e temporalidade | nenhuma regra de negócio, nenhuma migration; nenhum dado normativo apagado. Os dois bancos da validação são cópias de trabalho, criados e descartados fora do produto, como o `ps_auditoria_visual` do estudo | passa |
| III. Segurança e auditoria | nenhuma permissão, rota ou escopo muda; a lista de ações por papel é idêntica antes e depois (FR-7710), e é isso que a comparação prova | passa |
| IV. Regras explícitas | as sequências que não se invertem estão escritas na spec, e a comparação as confere | passa |
| V. Rastreabilidade e simplicidade | cada FR tem tarefa (tasks.md); nenhuma biblioteca nova; a fotografia e a comparação reusam o padrão das jornadas da `118` e da `147`. A jornada nova não é teste de regra crítica: é instrumento, e por isso fica sob demanda | passa |
| VI. Completude de jornada | o cenário demonstrável é a equipe abrindo as três telas pela interface da gestão, com o papel dela, nas duas versões (US4). A montagem do banco é preparação, como o `seed_demo`, e não a demonstração. A capacidade melhorada é ler a consequência antes de confirmar e achar o gesto junto do dado | passa |
| Fluxo e critérios | "operações irreversíveis DEVEM apresentar confirmação e consequências inequívocas": é o que a D-007 mede, e não só presume | passa |

**Depois do desenho (Fase 1):** continua passando. O único ponto de atenção é o princípio VI: o
piloto não é capacidade nova, e sim a mesma ação feita de modo que se espera melhor. Por isso o
critério de conclusão inclui a validação com a equipe, e não só a suíte verde. Se a validação
mostrar que a nova versão não é melhor (SC-2606, SC-2607), o piloto termina igualmente, com o
relatório dizendo isso, e a decisão de não migrar é do usuário.

## Project Structure

### Documentation (this feature)

```text
specs/172-piloto-do-design-system/
├── spec.md
├── plan.md                         # este arquivo
├── research.md                     # Fase 0
├── data-model.md                   # Fase 1: estado, fotografia, inventário, comparação, registro
├── quickstart.md                   # Fase 1: como fotografar, comparar e subir as duas versões
├── contracts/
│   ├── escopo-da-folha.md          # o que a folha do piloto pode e não pode fazer
│   └── inventario.md               # o formato do inventário e da comparação
├── checklists/requirements.md
├── tasks.md                        # Fase 2 (/speckit-tasks)
├── validacao.md                    # na implementação: roteiro, gabarito e registro (US4)
├── levantamento-dos-guardioes.md   # na implementação (FR-7741)
└── relatorio.md                    # na implementação: o resultado de cada critério e hipótese
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── shared/static/shared/tokens.css                         # acrescido, nada alterado (D-010)
└── interface/
    ├── static/interface/grupos/piloto-ds.css               # nova (D-003)
    └── templates/interface/
        ├── confirmar.html                                  # contêiner + folha
        ├── ocupacao.html                                   # contêiner + folha + marcação de indicador
        ├── _situacao_da_vaga.html                          # só se nenhuma outra tela a incluir (FR-7706)
        ├── ocupacao_acrescimo.html                         # contêiner + folha
        ├── ocupacao_nao_preenchida.html                    # contêiner + folha
        └── lista.html                                      # contêiner + folha

backend/tests/
├── interface/test_folha_estatica.py                        # o mapa de quem carrega cada folha ganha uma linha
├── fixtures/                                               # as fixtures locais que o catálogo precisa sobem para cá, sem mudar
└── navegador/
    ├── piloto/__init__.py
    ├── piloto/estados.py                                   # o catálogo: montagem, papel e trecho por código
    └── test_fotografia_do_piloto.py                        # a jornada, sob demanda

doc/auditoria-design-system-2026-11-14/piloto/
├── README.md                                               # o que está aqui e como reproduzir
├── antes/ e depois/                                        # inventários (JSON) e uma captura reduzida por estado
├── comparacao/                                             # o relatório da comparação, por estado
└── scripts/
    ├── comparar.py
    ├── sequencias.toml
    └── montar_banco_da_validacao.sh

.claude/launch.json                                         # duas entradas acrescentadas: piloto-antiga, piloto-nova
```

**Structure Decision**: só a camada de interface do monólito. O que é do produto fica em `backend/`;
o que é instrumento do piloto e resultado de medida fica em `doc/`, ao lado da referência da P0 com
que se compara; o que é registro de decisão e de validação fica na pasta desta spec.

### A marcação que muda nos templates

O piloto pode mudar **marcação**, e não **texto**: acrescentar o contêiner, envolver blocos em
elementos de agrupamento, trocar uma classe por uma do escopo, mover um bloco dentro das sequências.
Toda mudança de marcação preserva o texto, o `role`, o `aria-*`, o `id`, o `for`, o `name`, o `value`
e o `action`. Mover um bloco para outro item da estrutura muda a associação, e a comparação o acusa
(FR-7709). As classes existentes que os testes de tela procuram (`resumo`, `consequencias`, `aviso`,
`erro`, `nota`, `sucessao`, `confirmar`, `salvar`, `acoes`, `processo`, `linha-do-edital`, e as da
`129`) ficam no elemento em que estão; o piloto acrescenta classes, e não remove.

### A ordem do trabalho

1. **Preparação, sem tocar o produto**: o catálogo, a jornada, a comparação, as sequências. A
   jornada roda sobre a `main` e grava o "antes". É a fase que mais custa, e é ela que torna o piloto
   comparável.
2. **A fundação**: os tokens acrescidos, a folha vazia carregada pelos cinco templates, o contêiner.
   A comparação tem de dar zero diferença de conteúdo já aqui; a medida da P0 tem de continuar.
3. **As telas**, uma por vez, na ordem confirmação, conferências, Ocupação, Lista: cada uma termina
   com a jornada do estado dela, a comparação sem diferença de conteúdo e a acessibilidade conferida.
4. **O rastreio** sobre o `ps_p0_referencia` (SC-2602).
5. **A validação** com a equipe, nas duas versões.
6. **O relatório** e o levantamento dos guardiões.

## Complexity Tracking

| Ponto | Por que é necessário | Alternativa mais simples, e por que não basta |
|---|---|---|
| Uma jornada de 63 estados × 5 larguras | o aceite é por estado, e a Ocupação tem 18 estados de página que só as fixtures montam | fotografar o `ps_p0_referencia`: tem um estado só da Ocupação |
| Inventário de conteúdo próprio, além do instrumento do estudo | o aceite compara conjunto, associação e ordem; o instrumento mede forma, não conteúdo | comparar texto de `main` como sequência: reprova a mudança de posição, que é o que o piloto testa |
| Dois bancos e dois servidores para a validação | as mesmas tarefas nas duas versões, ao mesmo tempo, com registros diferentes no mesmo estado | trocar de branch entre sessões: a equipe não compara, e o servidor serve a worktree, e não a branch |
