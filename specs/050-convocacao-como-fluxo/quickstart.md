# Quickstart: validar a convocação como fluxo

## Suíte

```bash
cd backend && make lint check && make DB_NAME=ps050 test-pg
```

Só os testes da feature:

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps050 uv run pytest -q tests/unit/convocacao tests/integration/convocacao tests/interface/test_convocacao_em_fluxo.py
```

## Percurso no navegador

Pré-requisito: runserver da worktree com `INTERFACE_SELETOR_IDENTIDADE=true`, e um recorte com
apuração emitida e forma de comunicação declarada — o cenário é montado por
`tests/fixtures/convocacao.py::montar_cenario_da_convocacao`, num banco próprio.

1. Abrir `/gestao/editais/<id>/marcos/<id>/convocacao`. **Esperado:** a seção *"Convocar os
   titulares"* lista as pessoas, com a espécie e a origem de cada valor, e o botão diz
   *"Convocar os N titulares"*.
2. Informar o vencimento (ou escolher o Evento) e confirmar. **Esperado:** *"N convocações praticadas;
   N comunicações enviadas, 0 falharam"*; as mensagens aparecem no terminal do servidor (backend de
   console).
3. Avançar o vencimento (cenário com vencimento curto) e abrir de novo. **Esperado:** a seção *"Não
   atendimento dos vencidos"* lista as vencidas; confirmar registra N desfechos, e a tela diz que a
   apuração seguinte foi emitida.
4. Chamar o primeiro suplente pela chamada individual. **Esperado:** sem campo de espécie; o fundamento
   por extenso; a comunicação sai no mesmo ato, sem visita à ocupação.
