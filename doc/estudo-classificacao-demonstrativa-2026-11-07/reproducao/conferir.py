"""Calcula, sem banco, o que o GPS deve produzir para o elenco — com as funções puras do próprio motor.

Serve para duas coisas: escolher as notas antes de executar (o desenho do caso), e conferir depois
que a execução real produziu exatamente isto. Usa `combinacao.combinar`, `desempate.ordenar` e
`faixa.calcular`, as mesmas que `calcular_ordem` e `calcular_corte` chamam.

    cd backend && uv run python ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/conferir.py
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[2] / "backend"))

from elenco import ELENCO, RECURSO_DA_PROVA  # noqa: E402

from processo_seletivo.classificacao.domain import faixa  # noqa: E402
from processo_seletivo.classificacao.domain.combinacao import (  # noqa: E402
    SEM_PONTUACAO,
    combinar,
)
from processo_seletivo.classificacao.domain.desempate import ordenar  # noqa: E402

CONTEUDO = json.loads((AQUI / "edital-900-publicado.json").read_text())
PERFIL = CONTEUDO["profiles"][0]
ETAPAS = {e["id"]: e for e in CONTEUDO["stages"]}
POR_NOME = {e["name"]: e["id"] for e in CONTEUDO["stages"]}
CUR, PRO, ENT = (
    POR_NOME["Análise do currículo"],
    POR_NOME["Prova escrita"],
    POR_NOME["Entrevista"],
)
M1, M2 = PERFIL["classificationMilestones"]
FATO = PERFIL["declaredFacts"][0]["id"]
VAGAS = {None: 4, "PCD": 1, "PPI": 1}


def _num(valor):
    return None if valor in (None, "AUSENTE") else Decimal(valor)


def pessoas(com_recurso):
    for cod, nome, mod, nasc, req, cur, pro, ent in ELENCO:
        if com_recurso and cod == RECURSO_DA_PROVA["codigo"]:
            pro = RECURSO_DA_PROVA["para"]
        yield {
            "cod": cod,
            "nome": nome,
            "mod": mod,
            "fatos": {FATO: nasc},
            "req": req,
            "notas": {CUR: _num(cur), PRO: _num(pro), ENT: _num(ent)},
            "ausente": {PRO: pro == "AUSENTE", ENT: ent == "AUSENTE"},
        }


def eliminado_antes(p, etapa_limite):
    """Eliminação em Etapa de ordem menor ou igual — REQ, PRO (mínima 60) e ENT (mínima 60)."""
    ordem = ETAPAS[etapa_limite]["order"]
    if p["req"] == "I":
        return "Indeferido na Análise dos requisitos"
    for eid in (PRO, ENT):
        if ETAPAS[eid]["order"] > ordem:
            continue
        if p["ausente"][eid]:
            return f"Ausente em {ETAPAS[eid]['name']}"
        nota = p["notas"][eid]
        minima = Decimal(str(ETAPAS[eid]["minimumScore"]))
        if nota is not None and nota < minima:
            return f"{ETAPAS[eid]['name']}: {nota} < {minima}"
    return None


def ordem(marco, universo, recorte):
    if recorte is not None:
        universo = [p for p in universo if p["mod"] == recorte]
    classificaveis, sem_posicao = [], []
    ultima = max(ETAPAS[e]["order"] for e in marco["stages"])
    etapa_do_marco = next(e for e in marco["stages"] if ETAPAS[e]["order"] == ultima)
    for p in universo:
        motivo = eliminado_antes(p, etapa_do_marco)
        if motivo:
            sem_posicao.append((p, motivo))
            continue
        pts = {e: p["notas"][e] for e in marco["stages"]}
        nota = combinar(marco, ETAPAS, pts)
        if nota is SEM_PONTUACAO:
            sem_posicao.append((p, "sem pontuação"))
            continue
        classificaveis.append(
            {"inscricao_id": p["cod"], "pontuacao": nota, "pontuacoes": pts, "fatos": p["fatos"], "p": p}
        )
    return ordenar(classificaveis, marco["tiebreakers"]), sem_posicao


def mostrar(titulo, marco, universo, alvo_por_recorte):
    print(f"\n=== {titulo}")
    faixas = {}
    for recorte in (None, "PCD", "PPI"):
        ordenados, sem = ordem(marco, universo, recorte)
        alvo = alvo_por_recorte(recorte)
        regra = marco["cutRule"]
        dentro, exced, _, _ = faixa.calcular(
            [(o["inscricao_id"], o["posicao"]) for o in ordenados],
            alvo=alvo,
            excedente=regra["surplusCount"],
            desfecho=regra["tieOutcome"],
        )
        faixas[recorte] = dentro
        print(f"-- lista {recorte or 'ampla (todos)'}: alvo {alvo}+{regra['surplusCount']}")
        for o in ordenados:
            p = o["p"]
            sep = o["separado_por"]
            sep = f"{sep['type']}" if sep else ""
            marca = "FAIXA" if o["inscricao_id"] in dentro else "     "
            notas = " ".join(f"{p['notas'][e]}" for e in marco["stages"])
            print(
                f"  {o['posicao']:>2} {marca} {p['cod']} {p['nome']:<18} {p['mod']:<3} "
                f"[{notas}] = {o['pontuacao']}  {sep}{' EMPATE' if o['empate_residual'] else ''}"
            )
        for p, motivo in sem:
            print(f"   - sem posição {p['cod']} {p['nome']:<18} {p['mod']:<3} {motivo}")
    return faixas


def main():
    for com_recurso in (False, True):
        rotulo = "depois do recurso" if com_recurso else "preliminar"
        todos = list(pessoas(com_recurso))
        # Universo do marco 1: quem participa do Currículo e da Prova (REQ deferido).
        universo1 = [p for p in todos if p["req"] == "D"]
        faixas = mostrar(
            f"Marco 1 — Classificação para a entrevista ({rotulo})",
            M1,
            universo1,
            lambda r: M1["cutRule"]["targetCount"],
        )
        na_entrevista = set().union(*faixas.values())
        print(f"\nChegam à Entrevista ({len(na_entrevista)}): {sorted(na_entrevista)}")
    universo2 = [p for p in pessoas(True) if p["cod"] in na_entrevista]
    mostrar("Marco 2 — Classificação final", M2, universo2, lambda r: VAGAS[r])


if __name__ == "__main__":
    main()
