# Implementation Plan: Prevenção de erro nos atos irreversíveis da convocação

**Branch**: `claude/152-plano-e-tarefas`, sobre a `main` em `be830e65` | **Date**: 2026-11-11 |
**Spec**: [spec.md](spec.md)

## Summary

São três frentes, e cada uma reaproveita um desenho que já existe:

1. **O indeferimento** passa a ler o que a *pessoa* deixou de cumprir, e não a lista do que impede
   o aceite. A leitura documental ganha a lista dos motivos do atalho e o fato de ter havido
   apresentação nesta chamada. O comando de desfecho ganha uma guarda nova, a ciência do prazo em
   curso, no molde da ciência das inaplicabilidades da `131`.
2. **A chamada individual, a chamada para regularizar e o corte** ganham o segundo passo que o lote
   (`140`) e a ordem já têm. É o mesmo POST, em duas etapas. As recusas saem de uma verificação só,
   que o comando chama sob a trava e a conferência chama fora dela.
3. **O seletor do desfecho e o gesto do atestado** passam a ser filtrados por predicados puros de
   domínio. São os mesmos predicados que as guardas do comando usam, e eles devolvem o código e a
   frase da recusa.

Nenhuma migration, tabela, coluna nem permissão nova. A ciência do indeferimento fica na trilha do
desfecho, como a da `131` (R-001).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**
**Testing**: pytest contra PostgreSQL (`make test-pg`), cliente de teste do Django; os casos de
convocação e corte são transacionais onde a trava importa
**Target Platform**: a gestão (`/gestao/`), sob a CSP da `091`/`092`
**Project Type**: monólito web; só `backend/`
**Performance Goals**: a tela da convocação mantém o número de consultas por recorte. Cada predicado
do seletor lê o que a linha já carrega (R-006)
**Constraints**: sem script nem estilo no template; nenhuma prévia grava nada (FR-5815, FR-5830); o
seletor não é fronteira (FR-5838)
**Scale/Scope**: dezenas de chamadas por recorte; uma pessoa por chamada individual; faixas do
corte de dezenas de posições

## Constitution Check

*Antes da pesquisa e depois do desenho: passa.*

- **I. Linguagem ubíqua.** Os nomes novos são do domínio: *motivos do atalho*, *ciência do prazo*,
  *desfechos cabíveis*, *conferência da chamada*. Os rótulos das espécies não mudam (D-010).
- **II. Imutabilidade.** Nenhum ato muda de forma. O desfecho, a convocação e o corte continuam
  append-only, e a ciência entra na trilha, que também é (R-001).
- **III. Auditoria.** O indeferimento com ciência fica legível na trilha, com o vencimento que foi
  mostrado (FR-5806). As conferências não registram evento, porque não praticam ato (FR-5815,
  FR-5830).
- **IV. Regras no domínio.** A ciência é conferida pelo comando (D-003). O filtro do seletor e as
  guardas do comando leem os mesmos predicados (FR-5838). As conferências mostram o resultado, a
  origem e o alcance antes do ato: a pessoa, a espécie, a precedência e a faixa.
- **V. Rastreabilidade.** Cada FR, SC e UX e cada caso-limite ganha linha em `rastreabilidade.md`,
  escrita na implementação.
- **VI. Jornada.** Os cenários C09 e C11 da `134` são a verificação de ponta a ponta (quickstart).

## O desenho

### 1. Leitura documental — `convocacao/application/documentos.py` e `convocacao/domain/documentos.py`

- `ItemLido.apresentado_pela_pessoa`: há, na chamada, apresentação com arquivo, enviada pelo
  candidato. A aproveitada da inscrição não conta (D-011, R-003).
- `LeituraDocumental.houve_apresentacao`: algum item apresentado pela pessoa.
- `LeituraDocumental.motivos_do_atalho(*, prazo_decorrido)` lista os itens pendentes (estado
  `PENDENTE`). Com `prazo_decorrido` e `houve_apresentacao`, inclui também os obrigatórios em
  `A_APRESENTAR` (FR-5800).
- `LeituraDocumental.aguardando_conferencia`: itens em `RECEBIDO` ou `COMPLEMENTADO` (FR-5802).
- `fundamento_do_atalho(*, prazo_decorrido)` cita o pendente com o motivo e o não apresentado com
  "não apresentado no prazo". É composto por uma função nova do domínio, irmã de
  `fundamento_das_pendencias` (FR-5801).
- `fundamento_do_indeferimento` e `pendencias_para_incluir` continuam como estão: o aceite e a
  nota da `131` dependem deles.

### 2. A ciência do prazo — `convocacao/application/desfechar.py`

- Predicado puro `exige_ciencia_do_prazo(*, especie, enviado_em, vencimento, agora,
  pendencias_para_incluir)`, em `convocacao/domain/desfechos_cabiveis.py`. Ele é verdadeiro quando:
  - a espécie é `INDEFERIMENTO`;
  - há obrigatório não atendido;
  - o prazo não decorreu pela regra de `prazo.decorrido`, o que inclui a convocação sem vencimento e
    a ainda não enviada (R-002).
- Guarda `_recusar_indeferimento_sem_ciencia(convocacao, *, especie, ciencia_do_prazo, agora)`,
  logo depois de `_recusar_inercia_sem_ocupacao`. O código novo é `CIENCIA_DO_PRAZO_EM_CURSO`.
  Lê a leitura documental e o envio pela mesma trava que a inclusão já usa (FR-5805).
- `desfechar(..., ciencia_do_prazo=False)`. A trilha recebe, no `reason`, a frase "Com ciência do
  prazo em curso, vencendo em …" (ou "sem vencimento informado") e, no `detalhe`, `{"cienciaDoPrazo":
  {"vencimento": ..., "pendentes": [...]}}`. Esse é o FR-5806 (R-001).

### 3. Os desfechos cabíveis — `convocacao/domain/desfechos_cabiveis.py` (novo)

- `cabiveis(*, especie_da_chamada, enviado_em, vencimento, agora, tem_atestado, ocupando,
  pendencias_para_incluir, canal)` devolve `(cabem, ainda_nao)`. `cabem` lista as espécies na ordem de
  `ESPECIES_DE_DESFECHO`; `ainda_nao` lista `(especie, codigo, frase, a_partir_de)`. Começa por
  `DESFECHOS_POR_ESPECIE` (FR-5837), e cada guarda vira um predicado que devolve código e frase.
- As guardas do comando passam a chamar esses predicados, e as frases continuam as mesmas. O
  inventário de recusas não muda de texto (FR-5838, R-005).
- `admite_inercia(especie_da_chamada)` vale para o gesto do atestado (FR-5840).

### 4. A conferência da chamada — `convocacao/application/fluxo.py` e `convocar.py`

- `verificar_chamada(*, edital, perfil_id, marco_id, lista_id, inscricao_id, especie,
  justifica_precedencia, vencimento, evento_id, agora)` é a sequência de recusas de `convocar`, na
  ordem de hoje: marco, espécie, ordem vigente, apuração, convocação vigente, ordem ou
  regularização com a precedência, déficit, espécie derivada, vencimento. Devolve a espécie, a
  posição, os anteriores (`fila.precedencia`) e o vencimento com a origem. `convocar` a chama sob a
  trava, para as duas espécies de chamada. A correção (`120`) continua no ramo dela (R-004).
- `conferencia_da_chamada(...)` faz a mesma verificação fora da trava, mais
  `ensure_processo_accepts_changes`. Compõe:
  - o fundamento (`fundamentos_por_especie` + complemento);
  - a mensagem, por `previa_das_mensagens` com uma inscrição, ou a frase da publicação;
  - o prazo (`_prazo_da_conferencia`);
  - quem fica para trás;
  - na regularização, o Resultado indeferido, lido como `_suceder_o_resultado` o lê.
  
  Devolve `{"recusa"}` quando a confirmação seria recusada.
- `gesto_ja_concluido(*, actor, chave, operation=GESTO_TITULARES)` ganha o parâmetro, para valer
  também para `convocacao:convocar`.

### 5. O corte — `classificacao/application/emissao_do_corte.py`

- A emissão já confere a assinatura do cálculo (`_conferir`). Só a tela muda.
- `previa_da_continuacao(*, edital, perfil_id, marco_id, lista_id, quantidade, motivo, agora)` é a
  sequência de recusas de `continuar_corte` sem a trava. Devolve a proposta e a assinatura.
  `continuar_corte` passa a chamá-la e aceita `confirmacao_do_calculo` opcional: quando vem, é
  conferida pela mesma `assinatura_da_proposta`. A `causar_faixa_seguinte` da ocupação não a passa,
  e continua como está (R-007).

### 6. A tela — `interface/views.py`, `interface/conducao_da_convocacao.py` e templates

- **`convocar_view`**: fora do ramo da correção, deixa de usar `conferencia_do_texto.exigir` e segue
  as cinco etapas de `convocar_titulares_view`: autorização, chave concluída, composição, página e
  comando. A página é `convocacao_conferir.html`, com um modo de uma pessoa (R-008).
- **`emitir_corte_view`** e **`continuar_corte_view`**: sem `confirmar=1`, respondem
  `corte_confirmar.html` com a assinatura recomposta e `calculo_mudou`, como `emitir_ordenacao`.
  Com `confirmar=1`, chamam o comando.
- **`desfechar_view`**:
  - leva `ciencia_do_prazo` ao comando;
  - na recusa, guarda `recusa_do_desfecho` (convocação, espécie, fundamento, atestado) na sessão,
    que a tela consome para reabrir o formulário preenchido (FR-5805);
  - `_texto_do_desfecho` passa à conferência do texto a frase do prazo (FR-5807).
- **`_documentos_por_linha`** e **`anotar`**:
  - cada linha ganha `motivos_do_atalho`, `fundamento_do_atalho`, `aguardando_conferencia`,
    `exige_ciencia_do_prazo`, `desfechos` (`cabem`, `ainda_nao`) e `admite_atestado`;
  - o passo `VENCIDA` ganha a frase da FR-5809 quando há exigência e nada foi apresentado (UX-535).
- **`convocacao.html`**:
  - atalho condicionado a `motivos_do_atalho`;
  - aviso e marca da ciência nos dois formulários (UX-532);
  - seletor por `desfechos.cabem` e nota "Ainda não cabem nesta chamada" (UX-533);
  - atestado por `admite_atestado`;
  - botões "Conferir antes de convocar" (UX-530) e "Conferir antes de emitir" (UX-531).
- **Folhas**: só classes que já existem, mais as regras novas na folha da tela (`telas/corte.css`,
  `telas/convocacao-conferir.css`). Toda classe citada no template precisa de regra na folha
  (`test_acessibilidade`), e a folha não pode ter `}}` nem `%}` (`test_estaticos`).

### 7. Testes

Os testes ficam todos em `tests/interface/` e `tests/integration/`:

- `test_indeferimento_pelas_pendencias.py` (novo): FR-5800 a FR-5809, SC-1900, SC-1901 e SC-1910,
  por atalho e desfecho geral.
- `test_conferencia_da_chamada.py` (novo): FR-5810 a FR-5823, SC-1902, SC-1903, SC-1907 e SC-1909,
  com e sem complemento, regularização e precedência.
- `test_conferencia_do_corte.py` (novo): FR-5825 a FR-5833 e SC-1904, nas três operações.
- `tests/unit/convocacao/test_desfechos_cabiveis.py` (novo, de domínio, sem banco): a tabela dos
  predicados e as frases iguais às das recusas.
- `test_desfecho_cabivel.py` (novo, de interface): SC-1905, e o oráculo da SC-1906 — *oferecido ⇔
  aceito pelo comando* — sobre combinações montadas no banco.
- Ajustes nos helpers que postam a chamada individual, o corte e o desfecho: `test_convocacao_em_fluxo`,
  `test_conferencia_do_texto`, `test_faixa_seguinte`, `test_emissao_do_corte` e
  `test_publicacao_de_convocados`. O inventário de recusas da `033` ganha o código novo.

## Project Structure

### Documentation (this feature)

```text
specs/152-prevencao-nos-atos-irreversiveis/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # decisões técnicas (R-001 a R-010)
├── data-model.md        # o que muda nas leituras e no comando; nenhuma tabela
├── quickstart.md        # verificação pelos cenários C09 e C11
├── contracts/
│   └── telas.md         # formulários, etapas e códigos de recusa
├── checklists/requirements.md
├── tasks.md             # /speckit-tasks
└── rastreabilidade.md   # na implementação
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/domain/desfechos_cabiveis.py      # novo: cabiveis, exige_ciencia_do_prazo, admite_inercia
├── convocacao/domain/documentos.py              # fundamento_do_atalho
├── convocacao/domain/nomes.py                   # CIENCIA_DO_PRAZO_EM_CURSO
├── convocacao/application/documentos.py         # motivos do atalho, apresentação nesta chamada
├── convocacao/application/desfechar.py          # guarda da ciência; guardas pelos predicados
├── convocacao/application/convocar.py           # chama verificar_chamada
├── convocacao/application/fluxo.py              # verificar_chamada, conferencia_da_chamada
├── classificacao/application/emissao_do_corte.py  # previa_da_continuacao, confirmação opcional
└── interface/
    ├── views.py                                 # convocar_view, emitir/continuar_corte_view, desfechar_view
    ├── conducao_da_convocacao.py                # frase do passo vencido sem apresentação
    ├── templates/interface/convocacao.html
    ├── templates/interface/convocacao_conferir.html  # modo de uma pessoa
    ├── templates/interface/corte.html
    ├── templates/interface/corte_confirmar.html      # novo
    └── static/interface/telas/{corte,convocacao-conferir,convocacao}.css

backend/tests/
├── interface/test_indeferimento_pelas_pendencias.py
├── interface/test_conferencia_da_chamada.py
├── interface/test_conferencia_do_corte.py
└── unit/convocacao/test_desfechos_cabiveis.py
```

**Structure Decision**: o monólito de hoje, sem módulo novo além do arquivo de domínio dos desfechos
cabíveis.

## Complexity Tracking

Nenhuma violação da Constituição a justificar.
