"""Evidências sintéticas da Fase 3; sem conexão de banco, rede ou persistência de domínio.

Executar da raiz: backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-3/reproduzir-em-memoria.py
Usa fixtures puras dos testes existentes. A saída não comprova publicação por API ou interface.
"""

import copy
import json
import os
from pathlib import Path
import runpy
import sys

raiz = Path(__file__).resolve().parents[3]
backend = raiz / "backend"
sys.path.insert(0, str(backend))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"

from django.db.backends.base.base import BaseDatabaseWrapper


def impedir_conexao(*args, **kwargs):
    raise RuntimeError("Esta demonstração não autoriza conexão de banco")


BaseDatabaseWrapper.ensure_connection = impedir_conexao

import django

django.setup()

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    validate_for_publication,
)
from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.elevacao import elevar

periodos = runpy.run_path(str(backend / "tests/unit/editais/test_publicacao_com_periodo_cancelado.py"))
metodos = runpy.run_path(str(backend / "tests/contract/test_elevacao_degrau_10.py"))
resultados = {"escopo": "Somente memória; conexões de banco proibidas", "periodos": [], "normativa": []}

for nome, ato, substituir in (
    ("primeira_publicacao_cancelada", ATO_DE_PUBLICACAO, False),
    ("retificacao_cancelamento", ATO_DE_RETIFICACAO, False),
    ("retificacao_substituicao", ATO_DE_RETIFICACAO, True),
):
    conteudo = periodos["_snapshot"]("CANCELADO")
    if substituir:
        conteudo["schedule"][0]["isRegistrationPeriod"] = False
        conteudo["schedule"][1].update(status="PLANEJADO", isRegistrationPeriod=True)
    achados = validate_for_publication(conteudo, ato=ato, agora=periodos["AGORA"])
    relevantes = [item for item in achados if item.code == "registration_period_cancelled"]
    resultados["periodos"].append({
        "cenario": nome,
        "ato": ato,
        "impeditivo_cancelado": [str(item.severity) for item in relevantes],
        "outros_codigos": sorted({item.code for item in achados if item not in relevantes}),
    })

conteudo = elevar(metodos["conteudo_na_versao"](9))
perfil = conteudo["profiles"][0]
modalidade = "55555555-5555-5555-5555-555555555555"
perfil["competitionModalities"] = [{
    "id": modalidade,
    "code": "SINTETICA",
    "name": "Modalidade sintética",
    "normativeRule": {
        "id": "66666666-6666-6666-6666-666666666666",
        "foundation": "Fundamento sintético A",
        "version": "sintetica-1",
        "effectiveFrom": "2026-01-01",
    },
}]
base = f"/profiles/id={metodos['PERFIL']}/competitionModalities/id={modalidade}/normativeRule"
for campo, valor in (
    ("foundation", "Fundamento sintético corrigido"),
    ("version", "sintetica-2"),
    ("effectiveFrom", "2026-02-01"),
    ("id", "77777777-7777-7777-7777-777777777777"),
):
    entrada = copy.deepcopy(conteudo)
    try:
        saida, _ = apply_changes(entrada, [{
            "targetPath": f"{base}/{campo}", "operation": "REPLACE", "newValue": valor,
        }], publication_id="44444444-4444-4444-4444-444444444444")
        regra = saida["profiles"][0]["competitionModalities"][0]["normativeRule"]
        resultados["normativa"].append({"campo": campo, "resultado": "aceito_em_memoria", "valor": regra[campo]})
    except ValueError as erro:
        resultados["normativa"].append({"campo": campo, "resultado": "recusado_em_memoria", "tipo": type(erro).__name__, "mensagem": str(erro)})

texto = json.dumps(resultados, ensure_ascii=False, indent=2)
if "--salvar" in sys.argv:
    # Só escreve evidência documental nova; não sobrescreve resultado anterior.
    with Path(__file__).with_name("resultado-em-memoria.json").open("x", encoding="utf-8") as destino:
        destino.write(texto + "\n")
sys.stdout.reconfigure(encoding="utf-8")
print(texto)
