"""Lê o Edital 61/2026 do cenário coerente e grava `dados_v2.json` — só agregados, sem nome.

Somente leitura. Cada bloco nomeia a função que a tela dona já usa; onde não há uma, a consulta é
a mais próxima do modelo, e o bloco o diz. Mede consultas e tempo, para o RNF de desempenho.
"""

import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.models import ItemDoCorte, PosicaoNaOrdem
from processo_seletivo.convocacao.models import Convocacao, DesfechoDaConvocacao
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.models import DocumentoDoResultado, PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import visao_geral
from processo_seletivo.interface.supervisao import serie_do_edital
from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.processos.models import AtoAdministrativo, Edital
from processo_seletivo.publicacoes.domain.alteracoes import alteracoes_legiveis
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.resultados.application.prontidao import contagens, panorama_da_etapa
from processo_seletivo.resultados.models import ResultadoEtapa

inicio = time.perf_counter()
agora = timezone.now()
edital = Edital.objects.select_related("processo").get(number="61")
d = {"referencia": agora.isoformat()}


def iso(x):
    return x.isoformat() if x else None


with CaptureQueriesContext(connection) as consultas:
    primeira = Publicacao.objects.filter(edital=edital).order_by("publication_order").first()
    desfecho = desfechos([edital])[edital.id]
    d["identificacao"] = {
        "unidade": primeira.unidade_nome,
        "processo": f"{edital.processo.institutional_code} — {edital.processo.title}",
        "edital": f"{edital.number}/{edital.year}",
        "titulo": edital.title,
        "situacao": str(edital.status),
        "desfecho_em": iso(desfecho.em) if desfecho else None,
        "primeira_publicacao": iso(primeira.published_at),
    }
    versoes = list(VersaoConsolidada.objects.filter(edital=edital).order_by("valid_from", "materialized_at"))
    original, vigente = versoes[0].content, versoes[-1].content
    nomes_modalidade = {}
    d["perfis"] = []
    for p in vigente["profiles"]:
        for m in p.get("competitionModalities", []):
            nomes_modalidade[m["id"]] = m["name"]
        d["perfis"].append(
            {
                "id": p["id"],
                "nome": p["name"],
                "vagas": p["immediateVacancies"],
                "quadro": [(l["modalityId"], l["immediateVacancies"]) for l in p.get("vacancyTable") or []],
                "reserva": p["reserveType"],
                "limite": p.get("reserveLimit"),
                "local": p.get("locality"),
                "marcos": [{"id": m["id"], "nome": m["name"], "corte": m.get("cutRule")} for m in p["classificationMilestones"]],
            }
        )
    d["etapas"] = [{k: s.get(k) for k in ("id", "name", "order", "eliminatory", "classificatory", "weight", "minimumScore", "forma")} for s in vigente["stages"]]
    d["modalidades"] = nomes_modalidade

    # Inscrições — visao_geral.contagens_por_edital (fonte da 040) + recortes por modalidade.
    cont = visao_geral.contagens_por_edital([edital])[edital.id]
    sub = Inscricao.objects.filter(edital=edital, status="SUBMETIDA")
    d["inscricoes"] = {
        "por_perfil": {str(k): v for k, v in cont["submetidas"].items()},
        "rascunhos": cont["rascunhos"],
        "por_modalidade": {f"{p}|{m}": n for (p, m), n in Counter((str(a), str(b)) for a, b in sub.values_list("profile_id", "modality_id")).items()},
        "pessoas_distintas": sub.values("identity_subject").distinct().count(),
        "primeiro_envio": iso(sub.order_by("submitted_at").first().submitted_at),
        "ultimo_envio": iso(sub.order_by("submitted_at").last().submitted_at),
    }
    periodo = periodo_de_inscricoes(vigente, agora)
    serie = serie_do_edital(edital, periodo, agora)
    d["serie"] = [(p.dia.isoformat(), p.quantidade) for p in serie]

    # Etapas — prontidao.panorama_da_etapa (fonte da tela da Etapa), por Perfil.
    d["etapas_por_perfil"] = defaultdict(list)
    for etapa in sorted(vigente["stages"], key=lambda s: s["order"]):
        panorama = panorama_da_etapa(edital=edital, etapa=etapa, conteudo=vigente)
        c = contagens(panorama)
        vig = ResultadoEtapa.vigentes.filter(inscricao__edital=edital, etapa_id=etapa["id"])
        porp = defaultdict(Counter)
        for perfil, consequencia, origem in vig.values_list("inscricao__profile_id", "consequencia", "origem"):
            porp[str(perfil)][consequencia] += 1
            porp[str(perfil)][f"origem:{origem}"] += 1
        datas = sorted(vig.values_list("consolidado_em", flat=True))
        d["etapas_por_perfil"][etapa["name"]] = {
            "contagens_da_tela": dict(c),
            "por_perfil": {k: dict(v) for k, v in porp.items()},
            "consolidado_de": iso(datas[0]) if datas else None,
            "consolidado_ate": iso(datas[-1]) if datas else None,
        }

    # Resultado por recorte — divulgacao.vigente_do_marco + ocupacao.recortes_do_marco.
    d["recortes"] = []
    for p in vigente["profiles"]:
        for m in p["classificationMilestones"]:
            ocupacao = {str(r["listaId"]): r for r in recortes_do_marco(edital=edital, perfil_id=p["id"], marco_id=m["id"])}
            listas = {None} | {pub.lista_id for pub in PublicacaoResultado.objects.filter(marco_id=m["id"], ato__edital=edital)}
            for lista in sorted(listas, key=lambda x: str(x)):
                pub = vigente_do_marco(edital=edital, marco_id=m["id"], lista_id=lista)
                sit = Counter(SituacaoDivulgada.objects.filter(publicacao=pub).values_list("situacao", flat=True)) if pub else Counter()
                oc = ocupacao.get(str(lista))
                d["recortes"].append(
                    {
                        "perfil": p["name"],
                        "marco": m["name"],
                        "lista": nomes_modalidade.get(str(lista), "Ampla concorrência") if lista else "Ampla concorrência",
                        "natureza": pub.natureza if pub else None,
                        "publicado_em": iso(pub.publicado_em) if pub else None,
                        "cadeia": PublicacaoResultado.objects.filter(marco_id=m["id"], lista_id=lista, ato__edital=edital).count(),
                        "situacoes": dict(sit),
                        "ocupacao": {k: oc[k] for k in ("publicadas", "efetivas", "ocupadas", "faltando", "estado")} if oc else None,
                    }
                )
    d["corte"] = dict(Counter(ItemDoCorte.objects.filter(corte__perfil_id__isnull=False, inscricao__edital=edital).values_list("consequencia", flat=True)))

    # Convocações — raízes vigentes, desfechos, situação derivada.
    raizes = Convocacao.objects.filter(inscricao__edital=edital, convocacao_anterior__isnull=True)
    d["convocacoes"] = []
    for c in raizes:
        desf = DesfechoDaConvocacao.objects.filter(convocacao=c).order_by("registrado_em").last()
        d["convocacoes"].append(
            {
                "lista": nomes_modalidade.get(str(c.lista_id), "Ampla concorrência") if c.lista_id else "Ampla concorrência",
                "especie": c.especie,
                "em": iso(c.criado_em),
                "vencimento": iso(c.vencimento),
                "desfecho": desf.especie if desf else None,
                "desfecho_em": iso(desf.registrado_em) if desf else None,
            }
        )

    # Recursos — contagem por espécie, sem a listagem nominal (recursos_do_edital traz nome).
    rec = Recurso.objects.filter(inscricao__edital=edital)
    d["recursos"] = {
        "interpostos": rec.count(),
        "inadmitidos": JuizoDeAdmissibilidade.objects.filter(recurso__in=rec, admitido=False).count(),
        "decisoes": dict(Counter(DecisaoRecurso.objects.filter(recurso__in=rec).values_list("especie", flat=True))),
        "pendentes": rec.exclude(juizos__admitido=False).exclude(decisoes__isnull=False).count(),
        "interpostos_de": iso(rec.order_by("interposto_em").first().interposto_em) if rec else None,
        "interpostos_ate": iso(rec.order_by("interposto_em").last().interposto_em) if rec else None,
        "julgados_em": sorted({iso(x.date()) for x in DecisaoRecurso.objects.filter(recurso__in=rec).values_list("decidido_em", flat=True)}),
    }

    # Retificações e documentos.
    d["retificacoes"] = []
    for r in Retificacao.objects.filter(edital=edital, status="PUBLICADA").select_related("base_snapshot", "publication"):
        alts = list(r.alteracoes.all()) if hasattr(r, "alteracoes") else list(r.alteracaonormativa_set.all())
        d["retificacoes"].append({"em": iso(r.publication.published_at), "justificativa": r.justification, "alteracoes": alteracoes_legiveis(r.base_snapshot.content, alts)})
    d["documentos"] = [
        {"tipo": "Edital" if doc.publicacao.publication_order == 1 else f"Retificação {doc.publicacao.publication_order - 1}", "em": iso(doc.publicacao.published_at), "sha256": doc.document_hash}
        for doc in DocumentoPublicado.objects.filter(publicacao__edital=edital).select_related("publicacao").order_by("publicacao__publication_order")
    ] + [
        {"tipo": f"Resultado {doc.publicacao.natureza.lower()} — {doc.publicacao.marco_id}|{doc.publicacao.lista_id}", "em": iso(doc.publicacao.publicado_em), "sha256": doc.documento_hash}
        for doc in DocumentoDoResultado.objects.filter(publicacao__ato__edital=edital).select_related("publicacao").order_by("publicacao__publicado_em")
    ]
    d["cronograma"] = {
        "original": [{k: e.get(k) for k in ("type", "startAt", "endAt", "status")} for e in original["schedule"]],
        "vigente": [{k: e.get(k) for k in ("type", "startAt", "endAt", "status")} for e in vigente["schedule"]],
    }
    if desfecho and desfecho.em:
        d["depois_do_encerramento"] = list(
            RegistroAuditoria.objects.filter(occurred_at__gt=desfecho.em, institution_scope=edital.institution_scope)
            .values_list("operation", "occurred_at")
        )
    d["ato_de_encerramento"] = AtoAdministrativo.objects.filter(aggregate_id=edital.id).values_list("reason", flat=True).first()

d["custo"] = {"consultas": len(consultas.captured_queries), "segundos": round(time.perf_counter() - inicio, 2)}
Path("dados_v2.json").write_text(json.dumps(d, ensure_ascii=False, indent=1, default=str))
print("ok", d["custo"])
