# Implementation Plan: Destinação da vaga reservada sem ocupante

**Branch**: `claude/155-plano-e-tarefas`, sobre a branch do #482 em `d1f6bbf4` | **Date**: 2026-11-11 |
**Spec**: [spec.md](spec.md)

## Summary

A reversão de cota deixa de ser efeito da emissão da apuração e passa a ser ato próprio, com
"Confira antes", fundamento e registro. Ela grava o mesmo movimento de vaga que a ocupação já sabe
ler (R-001). Ao lado dela:
- a declaração de vaga não preenchida, numa tabela nova (R-002);
- a terceira resposta da reversão, a passagem entre cotas, que não move nada (R-003);
- o gesto único da lista vazia e a publicação conjunta (R-006);
- a lista de sorteio sem relação, com ausência comprovada (R-007);
- o desfazimento (R-005);
- a destinação na página pública e no relatório (R-009).

Uma derivação só alimenta a ocupação, o Centro e a convocação (R-008).

**A D-015 está em aberto, e o plano a isola.** A condição da reversão por saldo é o incremento F,
bloqueado. Até ela fechar, a emissão continua a mover vaga **só** sob a declaração por saldo, como
hoje (R-010). O resto não depende dela.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL. Duas migrations:
- `ocupacao/0005`: colunas no movimento e na apuração, e a tabela `VagaNaoPreenchida`;
- `editais`: os *choices* da declaração.

Uma tabela append-only nova: o `provisionar_papeis` passa a `N de 59`.
**Testing**: pytest contra PostgreSQL (`make test-pg`, 4 workers, `worksteal`). Os casos com trava,
gatilho e privilégio são transacionais. A jornada vai no navegador do painel (quickstart).
**Target Platform**: a gestão (`/gestao/`) e o portal público (`/selecoes/`), sob a CSP da `091`/`092`
**Project Type**: monólito web; só `backend/`
**Performance Goals**: o detalhe do Edital mantém custo fixo por Edital (FR-4686 da `135`); os fatos
externos da situação são lidos uma vez por marco (R-008)
**Constraints**:
- sem estilo nem script no template;
- a ocupação não importa a convocação: fatos externos chegam por *callable* injetado (R-004);
- nenhuma prévia grava;
- a varredura de vocabulário da ocupação vale para os arquivos novos.
**Scale/Scope**: dezenas de recortes por Edital; uma ou duas destinações por Perfil

## Constitution Check

*Antes da pesquisa e depois do desenho: passa.*

- **I. Linguagem ubíqua.** Os nomes vêm da spec e do domínio: *destinação*, *vaga não preenchida*,
  *passagem entre cotas*, *lista sem concorrente*. O código os escreve em português.
- **II. Imutabilidade.** Nada se atualiza nem se apaga:
  - os movimentos antigos ficam e contam (FR-6316);
  - o desfazimento é outro registro (R-005);
  - a tabela nova é append-only, por gatilho e por privilégio;
  - as colunas novas são acrescentadas, sem tocar linha antiga.
- **III. Auditoria.** Todo ato tem evento de trilha com correlação. O desfazimento impedido também,
  porque a recusa é confirmada e não desfeita (R-005).
- **IV. Regras explícitas.** A condição de cada gatilho e os impedimentos são funções puras do
  domínio, lidas igualmente pela tela e pelo comando (R-004, R-008). Toda escrita tem conferência com
  assinatura. Nenhuma regra do saldo é escrita antes da D-015.
- **V. Rastreabilidade.** `rastreabilidade.md` com cada FR, SC e UX, escrita na implementação. As
  revisões das specs afetadas já estão no #482.
- **VI. Jornada.** C09 de ponta a ponta, mais um Edital por esgotamento e um com a passagem entre
  cotas (quickstart).

## Os incrementos

Cada incremento é testável sozinho, e a ordem é a das dependências.

| Inc. | O quê | Requisitos | Depende de |
|---|---|---|---|
| **A** | A terceira resposta da reversão (passagem entre cotas): declaração, validação, coluna, frase, Retificação, revisão, dúvidas, prévias, contrato | FR-6317, FR-6318, FR-6319, UX-603 | — |
| **B** | A leitura da situação e o ato de destinação por esgotamento: domínio, comando, prévia e conferência, desacoplamento por esgotamento, Centro, convocação, prévias e equivalências | FR-6300 a FR-6304, FR-6306 a FR-6316, FR-6343, FR-6344, UX-600 a UX-602 | A (a recusa da passagem) |
| **C** | A vaga não preenchida, o Edital silente e a linha geral, e os desfazimentos | FR-6320 a FR-6327, FR-6334 a FR-6336 | B (a situação e os impedimentos) |
| **D** | A lista vazia: o gesto, a publicação conjunta e o sorteio sem relação | FR-6328 a FR-6333 | B (a destinação sem apuração de origem) |
| **E** | A página pública, o relatório e o fundamento na chamada | FR-6337 a FR-6340 | B, C |
| **F** | **Bloqueado pela D-015**: a condição do saldo, o fim do movimento na emissão, S-1 a S-4 | FR-6305, SC-2104 (parte de S) | a decisão do usuário |

## O desenho, por módulo

### `ocupacao/domain/`

- `nomes.py`:
  - `PASSAGEM_ENTRE_COTAS` e `DECLARACOES_DE_REVERSAO` (R-003);
  - as espécies novas de movimento e de não preenchida;
  - os códigos de recusa do contrato;
  - a causa `declaracao_posterior`.
- `reversao.py`:
  - `declarada` devolve as três respostas;
  - `especie_que_move` devolve só as duas que movem;
  - `quantidade_a_reverter` não muda.
- `destinacao.py` (novo), com funções puras:
  - `ainda_podem_ocupar`;
  - `impedimentos`;
  - `situacao` — os estados do data-model —;
  - `quantidade_destinavel`, que é o saldo líquido dos movimentos antigos.
- `apuracao.py`: `faltando` desconta as não preenchidas, e o cálculo lê o movimento de desfazimento
  como movimento.

### `ocupacao/application/`

- `destinacao.py` (novo):
  - `previa_da_destinacao`, `destinar_vaga` e `desfazer_destinacao`;
  - `previa_da_nao_preenchida`, `declarar_nao_preenchida` e `desfazer_nao_preenchida`.

  O molde é o de `acrescimo.py`: prévia assinada, `comando_de_comissao`, `auditar`, sucessora no
  *savepoint*, `concluir_sem_resultado`.
- `emissao.py::_apurar`: o ramo que cede vaga só age sob a declaração por saldo (R-010); por
  esgotamento, não grava movimento.
- `selectors.py`:
  - `_movimentos_que_alcancam` lê também o recorte próprio do movimento;
  - `causas_de_obsolescencia` ganha a sétima causa;
  - `ocupacao_do_recorte` ganha `naoPreenchidas` e `situacaoDaVaga`;
  - `destinacoes_publicas` é novo.
- `movimento.py`: `gravar_reversao` grava as colunas novas; `reverter_cota`, só de teste, passa a
  chamar o comando.

### `interface/`

- `destinacao_da_vaga.py` (novo): compõe os fatos externos — divulgação, recursos e convocação — uma
  vez por marco, e a situação de R-008.
- **Telas e rotas**: `views.py`, `urls.py` e as rotas do contrato. Os templates novos:
  - `ocupacao_destinacao.html`, a conferência;
  - `_situacao_da_vaga.html`.

  A view nova entra em `MODULOS_DE_VIEW` se tiver módulo próprio, e cada `Http404` novo ganha linha
  no inventário da `033`.
- `ocupacao.html`: a situação e os botões.
- `andamento.py`: o ramo `IMPEDIDO` de `situacoes_da_convocacao` lê a situação.
- `conducao_da_convocacao.py::_vaga_sem_chamada`: cita a situação quando a fila está vazia. O #489
  (152) também mexe neste arquivo, em `convocacao.html` e em `views.py`, e o PR da implementação diz
  isso.
- **A terceira resposta** (incremento A): `_perfil.html`, `compor_perfis.html`, `forms.py`,
  `retificacao.py`, `aplicacao_na_retificacao.py`, `revisao.py`, `aplicacao.py`,
  `previa_da_classificacao.py` e `previa_do_sorteio.py`.
- **O gesto da lista vazia**: uma view e o template de conferência, sobre `emitir_ordem` e
  `emitir_corte` (R-006).
- `relatorio_do_edital.py` e o template: a seção nova.

### Outros apps

- `divulgacao/application/publicar.py`: a publicação conjunta (R-006).
- `editais/domain/validation.py`, `editais/models/perfis.py` e migration: a terceira resposta.
- `publicacoes/infrastructure/pdf.py`: as frases dela.
- `duvidas/domain/rotulos.py`: o rótulo dela.
- `portal/views.py::selecao` e `portal/_destinacao_das_vagas.html`: a seção pública.
- `seguranca/papeis.py`: a tabela nova.
- `treinamento/`: um cenário com reversão por esgotamento, se o C09 não bastar à jornada. Ele sobe a
  `versao` do cenário.
- `specs/001-.../contracts/openapi.yaml`: o `enum`.
- `CLAUDE.md`: a contagem do `provisionar_papeis`.

## Riscos

- **As equivalências das prévias** (R-011) leem o "cedido" pelo movimento que a emissão cria. Por
  esgotamento, o lado oficial passa a ser a conta da destinação. O teste muda de forma, e não de
  garantia.
- **A coluna `apuracao` do movimento fica nula** só na lista de sorteio sem relação. Toda leitura por
  `apuracao__edital` passa a ler o recorte próprio também, e um teste prende que nenhuma leitura ficou
  para trás.
- **Conflito com o #489** nos arquivos da convocação: rebase antes da validação final, preservando os
  requisitos dos dois.

## Complexity Tracking

| Item | Por quê | Alternativa mais simples recusada |
|---|---|---|
| Tabela nova (`VagaNaoPreenchida`) | a vaga não preenchida existe e não muda as efetivas (D-003) | acréscimo negativo: diria que a vaga deixou de existir |
| Colunas de recorte no movimento | a lista de sorteio sem relação não tem apuração de origem (D-011) | apuração artificial, recusada pelo usuário |
