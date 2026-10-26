"""Extrai os números da maquete do Edital 51, pelas fontes que o estudo nomeia.

Cada valor sai com a fonte que o produziu. Roda em `manage.py shell`; escreve dados.json.
Somente leitura: nenhum command é chamado.
"""

import json
import time
from collections import Counter
from pathlib import Path

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.convocacao.models import Convocacao, DesfechoDaConvocacao
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.models import DocumentoDoResultado, PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import visao_geral
from processo_seletivo.interface.supervisao import serie_do_edital
from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.processos.models import AtoAdministrativo, Edital
from processo_seletivo.publicacoes.application.selectors import atos_publicados
from processo_seletivo.publicacoes.domain.alteracoes import alteracoes_legiveis
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.recursos.application.selectors import recursos_do_edital, resumo
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.resultados.application.prontidao import contagens, panorama_da_etapa
from processo_seletivo.resultados.models import ResultadoEtapa

inicio = time.perf_counter()
agora = timezone.now()
edital = Edital.objects.select_related("processo").get(number="51")
d = {"referencia": agora.isoformat(), "fontes": {}}


def fonte(chave, texto):
    d["fontes"][chave] = texto


with CaptureQueriesContext(connection) as consultas:
    # A. Identificação
    primeira = Publicacao.objects.filter(edital=edital).order_by("publication_order").first()
    desfecho = desfechos([edital])[edital.id]
    ato_final = AtoAdministrativo.objects.filter(aggregate_id=edital.id).order_by("occurred_at").last()
    d["identificacao"] = {
        "unidade": primeira.unidade_nome,
        "sigla": primeira.unidade_sigla,
        "cabecalho": primeira.unidade_cabecalho,
        "local": primeira.unidade_local,
        "processo": f"{edital.processo.institutional_code} — {edital.processo.title}",
        "edital": f"{edital.number}/{edital.year}",
        "titulo": edital.title,
        "situacao": str(edital.status),
        "desfecho": desfecho and {"operacao": desfecho.operacao, "em": desfecho.em.isoformat()},
        "motivo_do_ato": ato_final.reason if ato_final else None,
        "primeira_publicacao": primeira.published_at.isoformat(),
        "autoridade_do_edital": f"{primeira.signatory_name} — {primeira.signatory_role}",
    }
    fonte("identificacao", "Publicacao (1ª, campos congelados) · desfechos() · AtoAdministrativo")

    # Conteúdo vigente e original
    versoes = list(VersaoConsolidada.objects.filter(edital=edital).order_by("valid_from", "materialized_at"))
    original, vigente = versoes[0].content, versoes[-1].content
    quadro = visao_geral.vagas_do_conteudo(vigente)
    d["quadro"] = repr(quadro)
    perfis = vigente["profiles"]
    d["perfis"] = [
        {
            "id": p["id"],
            "nome": p.get("name") or p.get("code"),
            "vagas": p.get("immediateVacancies"),
            "reserva": p.get("reserveType"),
            "limite_reserva": p.get("reserveLimit"),
            "modalidades": [m.get("name") for m in p.get("modalities", [])],
            "marcos": [
                {"id": m["id"], "nome": m.get("name"), "etapas": m.get("stages") or m.get("etapas")}
                for m in p.get("classificationMilestones", [])
            ],
        }
        for p in perfis
    ]
    d["etapas"] = [
        {k: s.get(k) for k in ("id", "name", "order", "eliminatory", "classificatory", "weight", "minimumScore", "forma", "scheduleEventId")}
        for s in vigente["stages"]
    ]
    fonte("perfis_etapas", "VersaoConsolidada.content vigente (profiles, stages) · visao_geral.vagas_do_conteudo")

    # B/D. Inscrições
    cont = visao_geral.contagens_por_edital([edital])[edital.id]
    d["inscricoes"] = {
        "submetidas_por_perfil": {str(k): v for k, v in cont["submetidas"].items()},
        "rascunhos": cont["rascunhos"],
        "pessoas_distintas_cpf": Inscricao.objects.filter(edital=edital, status="SUBMETIDA")
        .values("cpf_normalizado").distinct().count(),
        "por_modalidade": dict(
            Counter(
                str(m) for m in Inscricao.objects.filter(edital=edital, status="SUBMETIDA").values_list("modality_id", flat=True)
            )
        ),
        "primeiro_envio": Inscricao.objects.filter(edital=edital, status="SUBMETIDA").order_by("submitted_at").first().submitted_at.isoformat(),
        "ultimo_envio": Inscricao.objects.filter(edital=edital, status="SUBMETIDA").order_by("submitted_at").last().submitted_at.isoformat(),
    }
    periodo = visao_geral.situacao_do_periodo(vigente, agora)
    d["periodo"] = repr(periodo)
    try:
        from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes

        serie = serie_do_edital(edital, periodo_de_inscricoes(vigente, agora), agora)
        d["serie"] = repr(serie)[:2000]
    except Exception as exc:  # a maquete registra a falha em vez de inventar a série
        d["serie"] = f"FALHA: {exc!r}"
    fonte("inscricoes", "visao_geral.contagens_por_edital · supervisao.serie_do_edital · Inscricao (cpf, modalidade)")

    # E. Etapas
    d["por_etapa"] = []
    for etapa in sorted(vigente["stages"], key=lambda s: s.get("order", 0)):
        try:
            panorama = panorama_da_etapa(edital=edital, etapa=etapa, conteudo=vigente)
            c = contagens(panorama)
            c = c if isinstance(c, dict) else c.__dict__
        except Exception as exc:
            c = {"FALHA": repr(exc)}
        vig = ResultadoEtapa.vigentes.filter(inscricao__edital=edital, etapa_id=etapa["id"]) if hasattr(ResultadoEtapa, "vigentes") else ResultadoEtapa.objects.filter(inscricao__edital=edital, etapa_id=etapa["id"], sucessor__isnull=True)
        datas = list(vig.order_by("consolidado_em").values_list("consolidado_em", flat=True))
        d["por_etapa"].append(
            {
                "etapa": etapa.get("name"),
                "contagens_prontidao": {k: v for k, v in c.items() if not callable(v)},
                "consequencias": dict(Counter(vig.values_list("consequencia", flat=True))),
                "origens": dict(Counter(vig.values_list("origem", flat=True))),
                "primeira_consolidacao": datas[0].isoformat() if datas else None,
                "ultima_consolidacao": datas[-1].isoformat() if datas else None,
            }
        )
    fonte("etapas", "prontidao.panorama_da_etapa + contagens · ResultadoEtapa.vigentes")

    # F. Resultado por marco, ocupação, convocação
    d["marcos"] = []
    for p in perfis:
        for m in p.get("classificationMilestones", []):
            pub = vigente_do_marco(edital=edital, marco_id=m["id"])
            sit = Counter()
            if pub:
                sit = Counter(SituacaoDivulgada.objects.filter(publicacao=pub).values_list("situacao", flat=True))
            try:
                recortes = recortes_do_marco(edital=edital, perfil_id=p["id"], marco_id=m["id"])
                recortes = repr(recortes)[:1500]
            except Exception as exc:
                recortes = f"FALHA: {exc!r}"
            cortes = Corte.objects.filter(ato__edital=edital, ato__marco_id=m["id"]) if hasattr(Corte, "ato") else Corte.objects.none()
            d["marcos"].append(
                {
                    "perfil": p.get("name"),
                    "marco": m.get("name"),
                    "natureza_vigente": pub and pub.natureza,
                    "publicado_em": pub and pub.publicado_em.isoformat(),
                    "publicacoes_da_cadeia": PublicacaoResultado.objects.filter(marco_id=m["id"], ato__edital=edital).count(),
                    "situacoes": dict(sit),
                    "ocupacao": recortes,
                    "itens_do_corte": dict(Counter(ItemDoCorte.objects.filter(corte__in=cortes).values_list("consequencia", flat=True))) if cortes.exists() else None,
                }
            )
    raizes = Convocacao.objects.filter(inscricao__edital=edital, convocacao_anterior__isnull=True)
    d["convocacoes"] = {
        "por_especie": dict(Counter(raizes.values_list("especie", flat=True))),
        "inscricoes_distintas": raizes.values("inscricao").distinct().count(),
        "desfechos": dict(Counter(DesfechoDaConvocacao.objects.filter(convocacao__in=raizes, desfecho_anterior__isnull=True).values_list("especie", flat=True))) if hasattr(DesfechoDaConvocacao, "desfecho_anterior") else None,
        "requerimentos_enviados": RequerimentoDeMatricula.objects.filter(inscricao__edital=edital, enviado_em__isnull=False).count(),
    }
    fonte("resultado", "divulgacao.vigente_do_marco · SituacaoDivulgada · ocupacao.recortes_do_marco · Convocacao/Desfecho")

    # G. Atos publicados, retificações, documentos
    d["atos_publicados"] = repr(atos_publicados(edital_id=edital.id))[:2500]
    d["retificacoes"] = []
    for r in Retificacao.objects.filter(edital=edital, status="PUBLICADA").select_related("base_snapshot", "publication"):
        alts = list(r.alteracoes.all()) if hasattr(r, "alteracoes") else list(r.alteracaonormativa_set.all())
        d["retificacoes"].append(
            {
                "publicada_em": r.publication.published_at.isoformat() if r.publication else None,
                "justificativa": r.justification,
                "alteracoes": [repr(a) for a in alteracoes_legiveis(r.base_snapshot.content, alts)],
                "caminhos": [a.target_path for a in alts],
            }
        )
    d["documentos"] = [
        {"tipo": "Edital/Retificação", "ordem": doc.publicacao.publication_order, "em": doc.publicacao.published_at.isoformat(), "sha256": doc.document_hash}
        for doc in DocumentoPublicado.objects.filter(publicacao__edital=edital).select_related("publicacao")
    ] + [
        {"tipo": f"Resultado {doc.publicacao.natureza}", "em": doc.publicacao.publicado_em.isoformat(), "sha256": doc.documento_hash}
        for doc in DocumentoDoResultado.objects.filter(publicacao__ato__edital=edital).select_related("publicacao")
    ]
    fonte("atos", "publicacoes.atos_publicados · Retificacao + alteracoes_legiveis · DocumentoPublicado/DocumentoDoResultado")

    # Cronograma original × vigente
    def cron(c):
        return {e["id"]: {k: e.get(k) for k in ("description", "type", "startAt", "endAt", "status")} for e in c.get("schedule", [])}

    d["cronograma"] = {"original": cron(original), "vigente": cron(vigente)}

    # H. Recursos
    pecas = list(recursos_do_edital(edital))
    d["recursos"] = {
        "total": len(pecas),
        "linhas": [repr({k: v for k, v in (resumo(p) if not isinstance(p, dict) else p).items() if k != "recurso"})[:400] for p in pecas],
    }
    fonte("recursos", "recursos.selectors.recursos_do_edital + resumo")

    # I. Fatos posteriores ao desfecho
    if desfecho and desfecho.em:
        d["posteriores"] = dict(
            Counter(
                RegistroAuditoria.objects.filter(occurred_at__gt=desfecho.em)
                .exclude(operation__in=["ENCERRAR"])
                .values_list("operation", flat=True)
            )
        )
    fonte("posteriores", "RegistroAuditoria com occurred_at > instante do AtoAdministrativo")

d["custo"] = {"consultas": len(consultas.captured_queries), "segundos": round(time.perf_counter() - inicio, 2)}
Path("dados.json").write_text(
    json.dumps(d, ensure_ascii=False, indent=1, default=str)
)
print("ok", d["custo"])
