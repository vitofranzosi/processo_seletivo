# Implementation Plan: A confirmação de "Encerrar Processo" adverte as providências em aberto dos Editais

**Branch**: `claude/silly-engelbart-07c8f4`, sobre a `main` em `5cf5f179` (PR #421) | **Date**: 2026-11-06 |
**Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta, com o esclarecimento de 06/11 (opção B, renovação da confirmação).

## Summary

Uma composição nova, sobre o que a `113` e a `099` já derivam, lida numa tela só:

- **A composição** (R-1, R-2, R-3): `interface/encerramento.do_processo(processo, ator, *, agora)` percorre
  os Editais finais publicados do Processo, na ordem da recusa. Para cada um, reúne os itens que a
  confirmação do Edital produziria: `pendencias_do_edital.situacoes` filtrada por `TIPOS_NO_PROCESSO`
  e redigida por `_item`, mais `_providencias_da_099`. Devolve os grupos, a marca "há convocação
  aguardando" (UX-276) e o resumo da lista (R-5).
- **A leitura** (R-4): a view a faz dentro de `leitura_consistente()`, e fecha o bloco antes de chamar o
  comando.
- **A renovação** (R-5, R-6): no POST do encerrar, quando a tela ainda ofereceria o Confirmar, a view
  relê a advertência e compara o resumo enviado. Se for diferente ou faltar, devolve 409 com a lista
  atual, a frase da UX-279 e o motivo preenchido, sem chamar o comando. Se for igual, segue o fluxo de
  hoje.
- **A tela** (R-8): o bloco em `processo_confirmar.html`, com as classes que a folha já tem.
- **O que não muda**: `close_process`, `pendencias_do_edital`, `relatorio_do_edital`, a confirmação do
  Edital, o "Cancelar Processo", o detalhe e a lista de Processos (FR-4362, FR-4364).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova (`hashlib` e `json` da biblioteca padrão para o
resumo)

**Storage**: PostgreSQL. **Sem migration**, tabela, coluna ou permissão (SC-1325). O resumo vive só no
formulário (R-5)

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio). Os cenários saem de
`tests/fixtures/relatorio.montar_cenario` (finais `pendente`, `sem-pendencia` e `cancelado`). O
orçamento de consultas fica em `tests/performance/`

**Target Platform**: a gestão, em navegador, renderizada no servidor

**Project Type**: aplicação web

**Performance Goals**: a lista de Processos e o detalhe do Processo **sem consulta nova** (a
composição só roda na confirmação). Na confirmação, o número de consultas é constante por Edital final
e não cresce com inscrições, convocações ou recursos. O orçamento é medido e fixado no teste de
desempenho, como o da `113` (23 por Edital publicado com o período correndo). O POST que encerra paga
uma releitura (R-6)

**Constraints**:
- CSP sem `inline`, e só classes que já têm regra na folha (R-8);
- a linha do botão de confirmar é lida literalmente por `test_paineis_e_telas_de_apoio.py`;
- a releitura fecha a transação `REPEATABLE READ` antes do comando (R-4);
- as frases novas (UX-275 a UX-277, UX-279) passam pela varredura de vocabulário;
- o "a quem pedir" mantém a forma canônica da `033`, porque vem de `_item`, sem mudança.

**Scale/Scope**:
- `encerramento.py` ganha uma função, duas constantes e um campo `tipo` no `Item`;
- muda uma view (`praticar_ato_processo`) e um template (`processo_confirmar.html`);
- três arquivos de teste novos e um helper ajustado (R-7).

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | "Edital", "convocação", "Requerimento de Matrícula", "recurso", "marco" e "providência" são os termos do domínio e do relatório; o título não reaproveita o da `113` porque lá o sentido é outro (D-001) | ✅ |
| II — imutabilidade e temporalidade | nada é gravado; a leitura é de um instante só, em `REPEATABLE READ` (R-4), com a versão vigente que a `113` e a `099` já leem | ✅ |
| III — negar por padrão; dados pessoais | nenhuma permissão nova; a advertência só é lida para quem pode encerrar (FR-4357); o caminho só a quem a tela aceita (FR-4355, por `_item`); só contagens, nome do marco e datas, sem dado pessoal (FR-4356, SC-1323); o resumo é um hash de frases sem dado pessoal | ✅ |
| IV — regra explícita; concorrência; consequência visível antes do ato | a regra é a da `113` e da `099`, sem segunda definição (FR-4351, R-2); a concorrência é tratada pela renovação, e o limite que sobra está escrito (FR-4367, D-005); o efeito sobre o convocado fica visível antes do ato irreversível (UX-276) | ✅ |
| V — simplicidade e rastreabilidade | uma composição e uma releitura, sem estado; o guardião exaustivo dos tipos (R-2); o teste ajustado nomeado em `verificacao.md` (R-7) | ✅ |
| VI — jornada demonstrável | o quickstart monta o Processo com a convocação no prazo e percorre abrir, mudar e confirmar | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho (data-model, contrato,
quickstart): sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/130-advertencia-no-encerramento-do-processo/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/confirmacao-do-processo.md
└── checklists/requirements.md
```

`tasks.md`, `rastreabilidade.md`, `verificacao.md` e as capturas vêm nas fases seguintes.

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/encerramento.py                              # do_processo, TIPOS_NO/FORA_DO_PROCESSO, Item.tipo
├── interface/views.py                                     # praticar_ato_processo: leitura, renovação, reexibição
└── interface/templates/interface/processo_confirmar.html  # o bloco, a mensagem da renovação, o motivo de volta

backend/tests/
├── unit/interface/test_advertencia_do_processo.py                       # guardião dos tipos; resumo
├── interface/test_advertencia_do_encerramento_do_processo.py            # histórias 1 a 5, paridade, privacidade
├── performance/test_confirmacao_do_encerramento_do_processo.py          # orçamento por Edital
└── interface/test_processo.py                                           # helper ato() envia o resumo (R-7)
```

**Structure Decision**: a composição fica na interface, ao lado da do Edital, porque só redige; a regra
continua em `processos/application/pendencias_do_edital.py` e no relatório, intocados.

## Riscos

- **Frase da `113` mudada depois**: muda nas duas telas, e o teste de paridade acompanha, porque compara
  as funções e não um texto fixo.
- **Tipo novo em `pendencias_do_edital`**: o guardião exaustivo reprova até alguém decidir se ele entra
  no Processo (R-2).
- **Releitura no POST**: custa a mesma leitura do GET, uma vez por envio. Numa tela rara, com poucos
  Editais, é aceitável (D-007).
- **A `129`** (PR #420) não toca a confirmação do Processo. Os dois PRs só se encontram no README.

## Complexity Tracking

Nada a justificar.
