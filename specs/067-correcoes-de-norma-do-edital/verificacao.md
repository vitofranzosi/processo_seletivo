# Verificação — 067, correções de norma do Edital em PDF

## Ponto de partida (T001, T002)

Medido em 2026-10-09 sobre `17f361b6` (spec, plano e tarefas, sem código), contra PostgreSQL, com
`DB_NAME=ps067` e `pytest` chamado direto (a worktree não tem `.env`):

```text
tests/unit/editais tests/unit/publicacoes tests/unit/interface tests/contract
tests/integration/publicacoes tests/interface/test_compor_quadro.py
2202 passed in 120.39s
```

`test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes` (A e B) verde nesse ponto: o
renderizador da `main` reproduz byte a byte os PDFs da auditoria. O texto deles (`pdftotext
-layout`) foi gravado no scratchpad para a comparação final.

## Os testes da feature, antes do código

| Fase | Arquivo | Falha antes do código |
|---|---|---|
| 2 | `tests/unit/editais/test_predicados_da_067.py` | `ImportError: cannot import name 'declara_sorteio'` |
| US1 | `tests/unit/publicacoes/test_frase_de_recurso.py` | `ImportError: cannot import name 'prazo_do_recurso'` |
| US1 | `tests/unit/interface/test_revisao.py` (frase) | asserção — a frase antiga, sem objeto |

**Achado na implementação de US1 (`D-012`).** Com o nome do marco dentro da frase, o agrupamento da
Revisão — que junta os marcos de mesma regra de Perfis diferentes — separou cada Perfil num grupo, e
`test_marcos_iguais_em_perfis_diferentes_aparecem_uma_vez` e `test_o_marco_que_diverge_diz_em_que`
caíram. A Revisão passou a dizer "deste marco", com o nome na linha da denominação logo acima; o
documento continua nomeando.
