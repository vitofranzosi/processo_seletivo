# Rastreabilidade — 165 · As regras de deliberação dos pareceres

**Frase que governa**: *a deliberação diz quando o desfecho é desfavorável, pela regra que o Edital
escolheu, sobre pareceres dados às cegas; a `164` diz o que ele produz.*

Cada linha aponta onde o requisito entrou e o teste que o prende. As abreviações dos arquivos de
teste são:

- **UD** — `tests/unit/resultados/test_deliberacao.py`
- **UR** — `tests/unit/resultados/test_regra.py`
- **UP** — `tests/unit/editais/test_deliberacao_na_publicacao.py`
- **TC** — `tests/interface/test_composicao_da_deliberacao.py`
- **TF** — `tests/interface/test_conferencia_da_deliberacao.py`
- **IC** — `tests/integration/resultados/test_consolidacao_deliberada.py`
- **IG** — `tests/integration/resultados/test_gatilhos_da_deliberacao.py`
- **IA** — `tests/integration/avaliacoes/test_parecer_as_cegas.py`
- **IF** — `tests/integration/publicacoes/test_retificacao_da_deliberacao.py`
- **IR** — `tests/integration/recursos/test_recurso_da_deliberacao.py`
- **G** — os guardiões que o campo novo atravessou: `tests/migrations/test_migrations.py`,
  `tests/interface/test_campos_vem_do_contrato.py`, `tests/unit/avaliacoes/test_elevacao.py`,
  `tests/integration/publicacoes/test_elevacao_de_versao.py`, `tests/unit/editais/test_etapas.py`,
  `tests/unit/editais/test_marco_classificatorio.py`, `tests/integration/test_database_permissions.py`.

---

## Requisitos funcionais

| Requisito | Onde entrou | Teste |
|---|---|---|
| FR-7050 | `editais/models/etapas.py`, `resultados/domain/deliberacao.py` | UD, TC |
| FR-7051 | `editais/domain/validation.py` (`deliberacao_sem_regra`), `retificacoes.py` (`_recusar_colegiada_sem_regra`) | UP, IF |
| FR-7052 | `validation.py` (`maioria_com_numero_par`) | UP |
| FR-7053 | `validation.py` (`regra_sem_colegiado`), `deliberacao.publicar`, `forms._regra_de_deliberacao` | UP, TC |
| FR-7054 | `shared/canonical.py`, `publicacoes/domain/elevacao.py` (degrau 24), `regra.impedimento_da_regra` | UR, TC, G |
| FR-7055 | `editais/domain/mutabilidade.py`, `interface/retificacao.py` | G |
| FR-7056 | `avaliacoes/application/cegas.py`, views de conclusões e impedimentos | IA |
| FR-7057 | `mesa_inscricao.html` (nada muda no seletor da Mesa) | IA |
| FR-7058 | `cegas.pendentes` (a reaberta volta a ser pendente) | IA |
| FR-7059 | a Mesa continua com os dados da inscrição | IA |
| FR-7060 | `consolidacao._auditar_consolidacao` | IC |
| FR-7061 | `deliberacao.deliberar` | UD, IC |
| FR-7062 | `prontidao._estado_colegiado`, `distribuicao.html` | IC, TF |
| FR-7063 | `prontidao._estado_colegiado` (cada parecer pela compatibilidade de hoje) | IC |
| FR-7064 | `regra.consequencia` com a `Deliberacao` | UR, IC |
| FR-7065 | `resultados/models.py`, `resultados/0008` (gatilhos), `selectors.reproduzir_deliberacao` | IC, IG |
| FR-7066 | `deliberacao.motivo` | UD, IC |
| FR-7067 | `consolidacao._planejar`, `consolidacao_confirmar.html` | IC, TF |
| FR-7068 | o ramo de uma avaliação, intocado | a suíte da `013` |
| FR-7069 | `recursos/domain/elegibilidade.py` (`DELIBEROU`, `PENDENTE`), `supervisao.py` | IR |
| FR-7070 | `julgar.py` (a correção fixada de sempre) | IR |
| FR-7071 | `julgar._recusar_reavaliacao_colegiada`, `recurso.html` | IR |
| FR-7072 | `julgar._recusar_se_piora`, intocado | IR, a suíte da `018` |
| FR-7073 | `retificacoes.py` (`_recusar_deliberacao_mudada_apos_resultado`, `_recusar_reducao_abaixo_das_conclusoes`) | IF |
| FR-7074 | o bloqueio do Processo, que a consolidação também toma | IF |
| FR-7075 | `pdf.py`, `apresentacao.py`, `revisao.py`, `deliberacao.frase_da_regra` | UD, TC |
| FR-7076 | o motivo do Resultado, que diz regra e contagem | IC |
| FR-7077 | `recursos/application/selectors.py` (`pareceres_do_titular`, `textos_da_deliberacao`), `acompanhamento.html` | IR |
| FR-7078 | a parte pública não lê o motivo nem os pareceres (nada muda) | a suíte da `017` |
| FR-7079 | `prontidao.aguardando_pareceres`, `distribuicao.html` | IC, TF |
| FR-7080 | a prévia da classificação, intocada | a suíte da `094` |
| FR-7081 | `views._parecer_atacado`, `textos_da_deliberacao` | IR |
| FR-7082 | `avaliacoes/models.py` (`ExposicaoAoParecer`), `cegas.registrar_exposicao`, `distribuicao._expostos` | IA, IG |
| FR-7083 | `avaliacao._recusar_se_o_autor_foi_exposto` | IA |

## Requisitos de experiência

| Requisito | Onde entrou | Teste |
|---|---|---|
| UX-750 | `_etapa.html`, `telas.css` (`so-colegiada`) | TC |
| UX-751 | `mesa_inscricao.html` | IA |
| UX-752 | `deliberacao.linha_da_conferencia`, `consolidacao_confirmar.html` | UD, TF |
| UX-753 | `deliberacao.motivo` ("a comissão deliberou") | UD |
| UX-754 | `mesa_inscricao.html` | IA |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-2350 | TC (`test_o_acervo_sem_regra_nao_ganha_frase`), G (a elevação) |
| SC-2351 | UD (`test_a_tabela_verdade_inteira`), IC (a reprodução) |
| SC-2352 | IA |
| SC-2353 | a suíte da `013`, que roda inalterada |
| SC-2354 | IF |
| SC-2355 | UP |
| SC-2356 | *humano*, pendente |
