# Quickstart: verificar a 154

Para quem implementa e para quem revisa. Caminhos relativos a `backend/`.

## 1. Os testes, primeiro

```bash
cd backend
uv run pytest tests/unit/portal/test_obrigacoes_da_convocacao.py tests/unit/portal/test_situacao_da_inscricao.py tests/unit/interface/test_conducao_da_convocacao.py -q
```

Os de interface e integração pedem PostgreSQL (CLAUDE.md, *As armadilhas caras*): o par
`TEST_DB_ENGINE=postgresql` **e** `DB_USER`, e um `DB_NAME` próprio da worktree.

```bash
DB_NAME=ps154 make test-pg PYTEST_ADDOPTS="tests/interface/test_portal_convocacao.py tests/interface/test_portal_documentos_da_convocacao.py tests/interface/test_portal_jornada_consolidada.py tests/portal/test_acompanhamento_pela_situacao.py tests/integration/avisos/test_aviso_de_pendencia.py tests/test_vocabulario_dos_documentos_da_convocacao.py tests/test_citacoes_de_requisito.py"
```

A suíte inteira, uma de cada vez com as outras sessões (CLAUDE.md): `make lint check test-pg`.

## 2. Os cenários, no navegador

Banco descartável com os cenários de treinamento (a `134`): o C09 é o do estudo.

```bash
cd backend
CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco ps154
```

Na entrada da `154` do `.claude/launch.json` (acrescentada, **sem** sobrescrever as outras), com
`INTERFACE_SELETOR_IDENTIDADE=true` e `DB_NAME=ps154`. O código de acesso do portal sai no terminal
do servidor.

| Passo | Onde | O que ver |
|---|---|---|
| 0 | gestão, C09: declarar documentos da convocação (um obrigatório ao menos, e um opcional), convocar uma pessoa e comunicar — o percurso das etapas A e B do estudo | — |
| 1 | portal, convocação dessa pessoa, nada enviado (C1) | *Você foi convocado!* e a advertência, uma vez |
| 2 | enviar todos os obrigatórios e o Requerimento (T) — repete `B08-tudo-enviado` | na volta: *Acompanhe sua convocação*, o cartão do prazo, a frase de conclusão, **sem** advertência |
| 3 | acompanhamento | *Nada por enquanto.* + frase de conclusão, o prazo, **sem** advertência |
| 4 | gestão, documentos da convocação: registrar pendência num obrigatório | — |
| 5 | portal: convocação | *Você foi convocado!*, *Você ainda precisa corrigir 1 documento.* e a advertência |
| 6 | enviar um arquivo novo no item pendente — repete `D04-correcao-enviada` | cartão: *Reenviado — aguardando nova conferência. Novo arquivo recebido em …, depois da correção pedida.* |
| 7 | gestão, documentos da convocação — repete `D05-gestao-ve-versao-2` | item: *Reenviado — aguardando nova conferência*; resumo: *1 reenviado — aguardando nova conferência*; passo: *Conferir de novo: 1 documento reenviado — aguardando nova conferência.* |
| 8 | gestão, condução | linha documental: *· 1 reenviado — aguardando nova conferência* |
| 9 | gestão: conferir todos os obrigatórios como conformes (Tc) | — |
| 10 | portal: convocação e acompanhamento | *Acompanhe sua convocação* e *A conferência dos documentos obrigatórios terminou. Aguarde o registro do resultado desta convocação.*; nenhum *ainda vai concluir a análise* |
| 11 | gestão: registrar o aceite (I1) | portal: *Resultado da sua convocação*, como hoje |

As capturas de antes estão em `doc/estudo-jornada-final-2026-11-11/img/` (`B08-tudo-enviado.png`,
`D04-correcao-enviada.png`, `D05-gestao-ve-versao-2.png`); as de depois vão para
`specs/154-convocacao-depois-do-envio/capturas/` (SC-2006).

## 3. A busca que fecha o achado 23

Depois da implementação, nenhum resultado fora de comentário, docstring, teste ou spec:

```bash
cd backend
grep -rn -i -E "Complementado, aguardando|a conferir de novo|reenviado, a conferir|reenviado: nova conferência|reenviado, aguardando conferência|complementado\{\{" processo_seletivo
```

## 4. O que já estava gravado

Num banco com um aviso de pendência registrado **antes** da implementação, a trilha do gesto
continua dizendo *"documento reenviado, aguardando conferência"* (SC-2005, FR-6215). Nada se
regenera — documento publicado não se regenera, e trilha também não.
