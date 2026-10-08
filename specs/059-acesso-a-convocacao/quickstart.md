# Quickstart: verificar o caminho até a convocação e o requerimento

**Feature**: [spec.md](spec.md) · **Contrato**: [contracts/telas.md](contracts/telas.md)

## 1. A suíte

```bash
cd backend && make lint check test-pg DB_NAME=test_ps_059
```

Worktree nova: `uv sync --extra dev` uma vez antes. `test-pg` e não `test` (ver `CLAUDE.md`).

Os testes desta feature, isolados:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=test_ps_059 uv run pytest -q tests/interface/test_portal_caminho_da_convocacao.py tests/authorization/test_convocacao_alheia.py tests/performance/test_area_do_candidato.py tests/integration/requerimentos/test_orcamento_de_consulta.py tests/test_vocabulario_da_convocacao.py tests/interface/test_portal_convocacao.py
```

## 2. No navegador

Banco próprio, semeado; o `seed_demo` convoca a primeira colocada do Edital que pede o requerimento
**na convocação**, e envia o requerimento dela.

1. Semear `ps_demo_059` e subir o servidor da worktree na porta 8059 com
   `INTERFACE_SELETOR_IDENTIDADE=true` e `PORTAL_IDENTIDADE_DEMO=true` (entrada `acesso-059` do
   `.claude/launch.json`, acrescentada — nunca sobrescrita).
2. Entrar no portal como a convocada. Em **Minhas inscrições**, o item dela diz *"Convocação
   aberta"* e oferece **Ver convocação**; "Acompanhar" continua no item.
3. **Ver convocação** → a tela da convocação, com *"Conferir o Requerimento de Matrícula enviado"*.
4. **Acompanhar** → a seção *"Convocação"* no topo, com a situação e "Ver convocação".
5. Pela gestão (tela de Convocação do recorte), convocar a segunda colocada. Entrar como ela: a
   convocação e o acompanhamento oferecem **Preencher Requerimento de Matrícula**.
6. Registrar o desfecho da primeira. Na lista dela, o item volta a **Acompanhar** e ganha a linha
   *"Convocação: Aceite"* (ou a espécie registrada); a seção do acompanhamento continua lá.
7. A 375 px (`resize_window` mobile), as quatro telas sem rolagem horizontal; e o clique do mouse
   em **Ver convocação** e em **Acompanhar** chega a cada destino, e não ao título do cartão
   (`D-010`).

## 3. O que conferir na trilha

Abrir a lista e o acompanhamento **não** acrescenta linha `CONVOCACAO_LER`; abrir a tela da
convocação acrescenta uma (`D-008`).
