"""Os bancos da validação do piloto com a equipe, um por tarefa (172, US4, T038, FR-7738).

Monta, num banco de teste limpo, o estado de cada tarefa da `validacao.md` pelo mesmo catálogo da
fotografia, e grava um `pg_dump` dele em `<PILOTO_DS_BANCO>/<tarefa>.dump`.
`doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh` os restaura.

**Um banco por tarefa, e não um banco só** (research §8 da spec): as fixtures foram escritas para um
banco vazio — buscam "o único Edital" e repetem código de Processo, chaves de idempotência e
identificadores de linha —, e o banco da referência da P0 não tem os estados das tarefas (nenhum
Edital em revisão, um recurso só, nenhum acréscimo de vaga). Cada estado nasce no seu banco, como
nasce na fotografia.

Só sob demanda: sem `PILOTO_DS_BANCO`, o módulo pula. Não verifica nada além de o estado ter sido
alcançado, que é o mesmo que a fotografia confere.
"""

import os
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador")

PASTA = os.getenv("PILOTO_DS_BANCO")
if not PASTA:
    pytest.skip("os bancos da validação saem só com PILOTO_DS_BANCO", allow_module_level=True)

from django.db import connection  # noqa: E402

from tests.navegador.piloto.estados import carregar  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)
CATALOGO = carregar()

# A tarefa da validação e o estado do catálogo que ela usa. V1 e V2 dividem o banco da Lista.
TAREFAS = {"lista": "L-01", "v3": "C-09", "v4": "C-03", "v5": "O-07", "v6": "K-01"}


@pytest.mark.parametrize("tarefa", sorted(TAREFAS))
def test_monta_e_grava_o_banco_da_tarefa(tarefa, request):
    estado = CATALOGO[TAREFAS[tarefa]]
    montagem = estado.montar(request)
    resposta = montagem.cliente.get(montagem.url)
    assert resposta.status_code == 200
    if montagem.gesto is None:
        assert estado.prova in " ".join(resposta.content.decode().split()), estado.codigo
    if tarefa == "lista":
        # O V1 busca o Edital 90/2026, que é do acervo da Lista: o mesmo banco serve às duas.
        from tests.fixtures.lista_de_processos import processo

        processo("Seleção de monitores", editais=[("91", 2026, "PUBLICADO")], ha_minutos=6)
    dados = connection.settings_dict
    destino = Path(PASTA) / f"{tarefa}.dump"
    destino.parent.mkdir(parents=True, exist_ok=True)
    ambiente = {**os.environ, "PGPASSWORD": dados.get("PASSWORD") or ""}
    subprocess.run(
        [
            "pg_dump",
            "-Fc",
            "--no-owner",
            "-h",
            dados.get("HOST") or "localhost",
            "-p",
            str(dados.get("PORT") or 5432),
            "-U",
            dados["USER"],
            "-f",
            str(destino),
            dados["NAME"],
        ],
        check=True,
        env=ambiente,
    )
