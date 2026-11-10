"""As telas do protótipo do Centro de Controle (estudo de 2026-11-09). Só leitura.

Cada tela chama **as mesmas funções** que o detalhe do Edital e o do Processo já chamam
(`views.detalhe`, `views.processo_detalhe`): a autorização, o andamento, as ações e as Retificações
em curso. O protótipo não pratica ato nenhum — todo botão leva à tela real do ato, que continua sendo
a que autoriza e a que recusa ("prever não é autorizar").
"""

from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import centro as cc
from django.http import Http404
from django.shortcuts import render
from django.urls import path, reverse

from processo_seletivo.interface import acoes, andamento, atos_retificacao, identidade, views
from processo_seletivo.interface import supervisao as supervisao_do_processo
from processo_seletivo.processos.domain.finalizacao import pending_editais
from processo_seletivo.processos.models import ProcessoSeletivo

app_name = "prototipo"

# Os cenários que o estudo usa, e o que cada um demonstra. O código é o do Processo do cenário de
# treinamento (134); a rodada pode ter sufixo -R2, -R3.
CENARIOS = (
    ("SIM-TREINAMENTO-006", "1 · Sorteio em preparação, antes do congelamento", "C06"),
    ("SIM-TREINAMENTO-004", "2 · Classificação por pontuação, ordem a emitir", "C04"),
    ("SIM-TREINAMENTO-008", "3 · Resultado preliminar e prazo de recurso aberto", "C08"),
    ("SIM-TREINAMENTO-012", "4 · Convocação e conferência documental", "C12"),
    ("SIM-TREINAMENTO-011", "4b · Entrega documental com pendência", "C11"),
    ("SIM-TREINAMENTO-007", "Extra · Sorteio pronto para execução", "C07"),
    ("SIM-TREINAMENTO-005", "Extra · Avaliação pendente", "C05"),
    ("SIM-TREINAMENTO-014", "Extra · Resultado definitivo, perto do encerramento", "C14"),
)


def _ator(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, identidade.pedir_identificacao(request)
    return ator, None


def indice(request):
    ator, desvio = _ator(request)
    if desvio:
        return desvio
    linhas = []
    for codigo, descricao, cenario in CENARIOS:
        processo = (
            ProcessoSeletivo.objects.filter(
                institutional_code__startswith=codigo, institution_scope=ator.institution_scope
            )
            .exclude(status="CANCELADO")
            .order_by("-institutional_code")
            .first()
        )
        edital = processo.editais.order_by("year", "number").first() if processo else None
        linhas.append(
            {
                "descricao": descricao,
                "cenario": cenario,
                "processo": processo,
                "edital": edital,
            }
        )
    return render(
        request, "prototipo/indice.html", {"linhas": linhas, "ator": ator, "sem_trilha": True}
    )


def _contexto_do_centro(edital, ator, *, fase=None):
    em_curso = atos_retificacao.em_curso(edital, ator)
    dados = andamento.do_edital(edital, ator, em_curso=em_curso)
    if dados is None:
        return None
    marcos = views._marcos_publicados(edital, ator)
    for perfil in dados.perfis:
        perfil.destinos = [
            item for item in marcos if str(item["perfil"].get("id")) == str(perfil.perfil.get("id"))
        ]
    documentos = views._documentos_publicados(edital)
    centro = cc.compor(
        edital,
        dados,
        documentos=documentos,
        em_curso=em_curso,
        alcance=andamento.Alcance.de(ator, edital),
    )
    pendencias = views._pendencias(edital)
    participantes = views.participantes_do_edital(edital)
    segregacao = views.impede_por_segregacao(participantes, ator)
    conjunto = acoes.do_edital(edital, ator, pendencias=pendencias, segregacao=segregacao)
    return {
        "edital": edital,
        "centro": centro,
        "fase": _fase_escolhida(centro, fase),
        "andamento": dados,
        "linha_das_inscricoes": andamento.linha_das_inscricoes(dados.inscricoes),
        "documentos": documentos,
        "retificacoes_em_curso": em_curso,
        "participantes": participantes,
        "pendencias": pendencias,
        "grupo": acoes.hierarquia(conjunto),
        "pode_ver_avisos": views._pode_ver_avisos(ator, edital),
        "url_atual": reverse("interface:detalhe", args=[edital.id]),
    }


def _fase_escolhida(centro, pedida):
    """A fase aberta no detalhe: a pedida; senão, a da ação em destaque; senão, a primeira com ato
    **seu** (a frente paralela por último); senão, a primeira com algo em aberto; senão, a primeira em
    curso; senão, a última concluída. Regra de apresentação, fixa."""
    por_chave = {f.chave: f for f in centro.fases}
    if pedida in por_chave:
        return por_chave[pedida]
    if centro.destaque is not None:
        return por_chave[centro.destaque.item.fase_chave]
    # A frente paralela (a Etapa que o sorteio não lê) fica para depois da principal.
    for paralela_por_ultimo in (False, True):
        for fase in centro.fases:
            if bool(fase.paralela) != paralela_por_ultimo:
                continue
            if any(i.p.grupo == "sua" for i in fase.providencias):
                return fase
    for fase in centro.fases:
        if fase.providencias:
            return fase
    if centro.em_curso:
        return centro.em_curso[0]
    concluidas = [f for f in centro.fases if f.situacao == cc.CONCLUIDA]
    return concluidas[-1] if concluidas else centro.fases[0]


def centro_do_edital(request, edital_id):
    ator, desvio = _ator(request)
    if desvio:
        return desvio
    edital = views.obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404
    contexto = _contexto_do_centro(edital, ator, fase=request.GET.get("fase"))
    if contexto is None:
        return render(
            request, "prototipo/antes_da_publicacao.html", {"edital": edital, "ator": ator}
        )
    contexto["ator"] = ator
    return render(request, "prototipo/centro.html", contexto)


def processo(request, processo_id):
    ator, desvio = _ator(request)
    if desvio:
        return desvio
    processo = views._processo_do_ator(ator, processo_id)
    editais = []
    for edital in processo.editais.order_by("year", "number"):
        em_curso = atos_retificacao.em_curso(edital, ator)
        dados = andamento.do_edital(edital, ator, em_curso=em_curso)
        centro = (
            cc.compor(
                edital,
                dados,
                documentos=views._documentos_publicados(edital),
                em_curso=em_curso,
                alcance=andamento.Alcance.de(ator, edital),
            )
            if dados
            else None
        )
        editais.append({"edital": edital, "centro": centro})
    alcancadas = supervisao_do_processo.alcance(ator, processo)
    return render(
        request,
        "prototipo/processo.html",
        {
            "processo": processo,
            "editais": editais,
            "suas": sum(len(e["centro"].providencias["suas"]) for e in editais if e["centro"]),
            "pendentes": pending_editais(processo),
            "atos": list(views.atos_processo.disponiveis(processo, ator)),
            "pode_gerir_comissao": views.pode_gerir_comissao(ator, processo) is not None,
            "pode_auditar": ator.can("auditoria:consultar"),
            "atencao_visivel": any(alcancadas.values()),
            "sinais": (
                supervisao_do_processo.sinais(processo, ator, alcancadas=alcancadas)
                if any(alcancadas.values())
                else ()
            ),
            "ator": ator,
        },
    )


# ---------------------------------------------------------------------------------------------
# Cenário 5 — seleção concluída. **Fixture**, e dito na tela: nenhum cenário do banco termina
# assim (o C14 para antes da convocação), e a "ilustração" não se mistura com estado real.
# ---------------------------------------------------------------------------------------------


def _fixture_concluida():
    from processo_seletivo.inscricoes.domain import periodo

    a = andamento
    zona = ZoneInfo("America/Sao_Paulo")
    listas = [
        ("ampla", "Ampla concorrência (linha geral do quadro)"),
        ("ppp", "Pessoas pretas, pardas e indígenas (PPP)"),
    ]

    def ponto(tipo, titulo, grupo, notas, **extra):
        p = a.Ponto(tipo, titulo, grupo)
        for (chave, _), nota in zip(listas, notas, strict=True):
            p.celulas[a._chave(chave)] = a.Celula(a.FEITO, natureza=tipo, nota=nota, **extra)
        return p

    marco = "Marco · por pontuação · Classificação final"
    pontos = [
        ponto(a.ETAPA, "Prova objetiva", a.GRUPO_DAS_ETAPAS, ["6 de 6 consolidadas"] * 2),
        ponto(a.ETAPA, "Análise de títulos", a.GRUPO_DAS_ETAPAS, ["6 de 6 consolidadas"] * 2),
        ponto(a.ORDEM, "Ordem", marco, ["emitida", "emitida (2 pessoas)"]),
        ponto(a.CORTE, "Corte", marco, ["faixa até a 4ª posição", "faixa até a 1ª posição"]),
        ponto(a.ETAPA, "Análise documental", a.GRUPO_DA_GOVERNADA, ["4 de 4 consolidadas"] * 2),
        ponto(a.APURACAO, "Apuração", marco, ["3 vagas ocupadas", "1 vaga ocupada"]),
        ponto(a.RESULTADO, "Resultado", marco, ["definitivo publicado"] * 2),
        ponto(
            a.CONVOCACAO,
            "Convocação",
            marco,
            ["3 convocações com desfecho", "1 convocação com desfecho"],
            contagem=0,
        ),
    ]
    perfil = a.PerfilNoAndamento(
        perfil={"name": "Professor de Informática", "id": "fixture"},
        forma="por pontuação",
        listas=listas,
        pontos=pontos,
        inscritos=8,
        resumo="2 listas · Etapas 3 de 3 · ordem 2 de 2 · corte 2 de 2 · apuração 2 de 2 · "
        "resultado definitivo publicado em 2 de 2 listas",
    )
    dados = a.Andamento(
        perfis=[perfil],
        providencias=[],
        atencoes=[],
        inscricoes={
            "estado": periodo.ENCERRADO,
            "fim": datetime(2026, 10, 20, 23, 59, tzinfo=zona),
            "cancelado": False,
            "enviadas": 8,
        },
        ve_a_matriz=True,
    )
    edital = SimpleNamespace(
        id=None,
        processo_id=None,
        number="FIX05",
        year=2026,
        title="Seleção concluída (ilustração)",
        status="ENCERRADO",
        processo=SimpleNamespace(institutional_code="FIXTURE-CONCLUIDA", status="ENCERRADO"),
    )
    documentos = [
        {"ordem": 1, "ato": "Publicação original", "retificacao_id": None, "url": "#"},
        {"ordem": 2, "ato": "Retificação", "retificacao_id": "x", "url": "#"},
    ]
    return edital, dados, documentos


def concluida(request):
    ator, desvio = _ator(request)
    if desvio:
        return desvio
    edital, dados, documentos = _fixture_concluida()
    centro = cc.compor(edital, dados, documentos=documentos, em_curso=[], alcance=None)
    centro.alcance = "Ilustração: nenhum ato é seu, porque o Processo está encerrado."
    return render(
        request,
        "prototipo/centro.html",
        {
            "edital": edital,
            "centro": centro,
            "fase": _fase_escolhida(centro, request.GET.get("fase")),
            "andamento": dados,
            "linha_das_inscricoes": andamento.linha_das_inscricoes(dados.inscricoes),
            "documentos": documentos,
            "retificacoes_em_curso": [],
            "participantes": None,
            "pendencias": [],
            "grupo": None,
            "fixture": True,
            "ator": ator,
        },
    )


urlpatterns = [
    path("", indice, name="indice"),
    path("editais/<uuid:edital_id>/", centro_do_edital, name="centro"),
    path("processos/<uuid:processo_id>/", processo, name="processo"),
    path("concluida/", concluida, name="concluida"),
]
