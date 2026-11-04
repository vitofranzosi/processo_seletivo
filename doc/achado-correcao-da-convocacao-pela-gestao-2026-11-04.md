# Achado — a correção da convocação por sucessão não se alcança pela gestão

Verificado em 04/11/2026 sobre a `main` em `fb0e1ddc`, durante a spec `118` (jornada consolidada do
convocado). Partiu da suspeita registrada na §7 da revisão de UX do PR
vitofranzosi/processo_seletivo#375 (`doc/revisao-ux-jornada-do-convocado-2026-11-04/README.md`,
ainda não mergeado). Nenhum código foi alterado.

> **Não vira escopo por estar escrito aqui.** Priorizar e decidir são do usuário. A recomendação é
> tratá-lo como **prioritário**, porque a `115` faz dele o único caminho para dar mais prazo.

## Resumo

**O domínio corrige; a tela não.** O comando de convocar, com motivo, sobre uma convocação vigente e
sem desfecho, cria a sucessora com vencimento novo. A view da gestão lê o motivo do POST. Mas:

1. nenhum formulário da gestão tem o campo `motivo`;
2. o seletor de pessoa nunca lista quem tem convocação em aberto;
3. o cartão da chamada em aberto só oferece *"Registrar desfecho"* e o atestado.

Pela interface, a comissão **não consegue** corrigir uma convocação, nem dar mais prazo. A FR-3618 da
`115` aponta para um mecanismo *"que já existe"*, e ele só existe no serviço.

## Evidência

Caminhos relativos a `backend/processo_seletivo/`.

### O domínio aceita a correção

- `convocacao/application/convocar.py`, linhas 143–151: com chamada em aberto e motivo vazio, o
  comando recusa com `CONVOCACAO_VIGENTE_EXISTENTE` (409): *"Para corrigi-la, declare o motivo da
  sucessão…"*.
- O mesmo arquivo, linhas 196–215: com motivo, grava `convocacao_anterior` e `motivo_da_sucessao` e
  reaproveita o número da chamada.
- O vencimento novo vem do POST (`vencimento` ou `evento`), e não é calculado
  (`convocacao/application/fluxo.py`, `resolver_vencimento`).
- Testado só no serviço: `tests/integration/convocacao/test_recusas.py`,
  `test_com_motivo_a_segunda_sucede_a_primeira_sem_tocar_nela`.

### A view lê o motivo

- `interface/views.py`, `convocar_view`, linhas 8822–8834: `inscricao`, `especie`, `vencimento`,
  `evento`, `complemento`, `motivo` e `justifica_precedencia` vêm do POST. O `motivo` é a linha 8830.

### Nenhum formulário o envia

Os dois formulários que postam para `interface:convocar` estão em
`interface/templates/interface/convocacao.html`:

| Formulário | Campos | `motivo`? |
|---|---|---|
| *"Chamar uma pessoa da fila"* (~linha 263) | `lista`, `chave`, `inscricao`, `evento`/`vencimento` (de `_vencimento_da_convocacao.html`), `complemento`, `justifica_precedencia` | **não** |
| *"Chamar para regularizar"* (~linha 328) | `lista`, `chave`, `especie`, `inscricao`, `evento`/`vencimento`, `complemento` | **não** |

*"Convocar titulares"* posta para outra rota, cujo comando recusa sucessão. Os dois formulários
dizem *"corrigi-lo é sucedê-lo com motivo"* (linhas 268 e 334, e o aviso da linha 45), sem oferecer
como.

### A fila exclui quem estaria sendo corrigido

- `convocacao/domain/fila.py`, linhas 72–74: a ordem de chamada tira da fila quem foi servido, quem
  tem **chamada em aberto** e quem encerrou.
- `convocacao/application/selectors.py`: a fila de regularizáveis também exclui quem tem chamada em
  aberto.
- O `select` de *"Chamar uma pessoa da fila"* é essa fila. Quem precisa de correção nunca aparece
  nele.

### Nenhum teste de tela

`tests/interface/test_convocacao*.py` e `tests/navegador/` não têm POST de convocar com `motivo`. O
`motivo` de `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` é o da conferência de
documento.

## Reprodução

1. Num recorte com apuração e ordem vigentes, abrir
   `/gestao/editais/<edital>/marcos/<marco>/convocacao` como presidência da comissão.
2. Em *"Chamar uma pessoa da fila"*, convocar a primeira pessoa, com vencimento.
3. De volta à tela, ela aparece como cartão em *"Prazo em curso"* (ou *"Sem comunicação enviada"*).
4. Abrir de novo *"Chamar uma pessoa da fila"*: ela não está no `select`, e não há campo de motivo.
5. No cartão dela, há só *"Registrar desfecho"* e o fundamento. Não há *"Corrigir"* nem *"Dar mais
   prazo"*.

**Resultado esperado pelos requisitos:** corrigir a convocação com motivo e vencimento novo, pela
tela. **Resultado observado:** impossível pela tela; só por serviço (shell ou teste).

## Requisitos afetados

| Requisito | O que diz | Situação |
|---|---|---|
| **FR-3618 da `115`** | Dar mais prazo MUST ser feito pela correção da convocação por sucessão, com motivo e vencimento novo, "que já existe" | o mecanismo existe no domínio; a comissão não o alcança |
| **FR-3622 da `115`** | A correção com vencimento novo reabre documentos e Requerimento juntos | o cenário 4 da User Story 4 da `115` não se monta pela gestão |
| **FR-272 da `019`** | Correção é sucessão com motivo | regra de domínio; cumprida no serviço |
| **FR-870 da `050`** | A convocação individual continua para a exceção — inclusive a **sucessão** — e MUST mostrar as derivações antes da confirmação | **descumprido**: não há caminho de tela para a sucessão |
| **FR-886 da `050`** | Nenhum gesto altera registro; corrigir continua sendo suceder | cumprido no serviço |

## O que corrigir exigiria (para decisão)

- Uma ação por cartão de chamada em aberto e sem desfecho — *"Corrigir esta convocação"* —, com
  **motivo obrigatório** e vencimento novo, que mostre as derivações antes da confirmação (FR-870 da
  `050`) e diga que a comunicação sai de novo, quando o Perfil convoca por mensagem individual.
- A autorização é a de convocar, que já existe; nenhum papel novo.
- Testes de interface e de navegador do percurso: corrigir, ver o prazo novo no portal e
  complementar a pendência.
- **Um cuidado:** `convocar_view` não confere a inscrição contra a fila (só `_identidade_ou_404`). A
  ação nova deve continuar dependendo da guarda do comando, e não da tela. *Hipótese não testada*: um
  POST montado à mão com uma inscrição em aberto, `motivo` e `vencimento` já criaria a sucessora.

É mudança de tela da gestão, fora da `118` (que não muda a gestão), e merece spec curta ou emenda à
`050`. A mensagem da sucessora (*"A sua convocação foi corrigida: o novo prazo é…"*) é outra decisão,
sobre a FR-290 da `019`, e tem parente em `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`.
