"""Reproduz o certame demonstrativo do Edital 900/2026, fase a fase, pelos comandos da aplicação.

**Pelos mesmos comandos que as telas chamam**, e cada um com o relógio da aplicação posto no dia do
ato (`tests/fixtures/relatorio.em`): a inscrição só existe dentro do período, a distribuição só
depois dele, o recurso só na janela. Se a cronologia daqui estivesse errada, o comando recusaria.

As notas e os personagens vêm de `elenco.py`. O que o GPS produz em cada fase pode ser conferido
contra `conferir.py`, que faz a mesma conta com as funções puras do motor e sem banco.

Uso, a partir de `backend/`, num banco próprio e já migrado (ver `roteiro-de-reproducao.md`):

    export DB_NAME=ps_estudo_classif DB_USER=$USER DB_RUNTIME_USER=$USER \
           DJANGO_SETTINGS_MODULE=config.settings.development \
           ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos-estudo-classif AVISOS_AOS_CANDIDATOS=false
    uv run python ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/reproduzir.py f0
    ... f1 f2 ... f9

Fases (cada uma pressupõe as anteriores):

    f0  Processo, rascunho, autoridade e publicação do Edital         09/11/2026
    f1  18 inscrições, com Diploma e Currículo anexados               16–27/11
    f2  comissão; Análise dos requisitos (17 Deferidos, 1 Indeferido)  30/11–02/12
    f3  Análise do currículo; Prova escrita (com uma ausência)        02–08/12
    f4  ordens do marco 1 nos três recortes; publicação preliminar    09/12
    f5  recurso de C10, correção fixada, ordem sucessora,
        publicação definitiva e cortes do marco 1                     10–14/12
    f6  Entrevista (com uma ausência) e ordens do marco 2;
        publicação preliminar                                        15–21/12
    f7  recurso de C07 (indeferido); publicação definitiva            22–28/12
    f8  cortes do marco 2 e apuração das vagas                        28–29/12
    f9  convocação com documentos, desfechos e nova convocação       04–08/01/2027

O estudo fez f0 pela interface, à mão, e as demais por este script — exceto onde o guia diz que o
gesto foi praticado na tela; a reprodução não depende disso.
"""

import io
import json
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django  # noqa: E402

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.utils import timezone  # noqa: E402

from elenco import ELENCO, MOTIVOS, RECURSO_DA_PROVA  # noqa: E402
from tests.fixtures.relatorio import cpf_valido, em  # noqa: E402

ZONA = ZoneInfo("America/Sao_Paulo")
CORRELACAO = "estudo-classificacao"
CHAVE = "estudo900"
CONTEUDO = json.loads((AQUI / "edital-900-publicado.json").read_text())
PERFIL = CONTEUDO["profiles"][0]
PERFIL_ID = PERFIL["id"]
ETAPA = {e["name"]: e["id"] for e in CONTEUDO["stages"]}
REQ, CUR, PRO, ENT = (
    ETAPA["Análise dos requisitos"],
    ETAPA["Análise do currículo"],
    ETAPA["Prova escrita"],
    ETAPA["Entrevista"],
)
MOD = {m["code"]: m["id"] for m in PERFIL["competitionModalities"]}
M1, M2 = (m["id"] for m in PERFIL["classificationMilestones"])
DOC = {d["key"]: d["id"] for d in CONTEUDO["documentRequirements"]}
FATO = PERFIL["declaredFacts"][0]["id"]
#: As três listas de cada marco: a ampla (lista nula, o universo inteiro) e as duas reservadas.
LISTAS = (None, MOD["PCD"], MOD["PPI"])


def dia(d, m, h=10, mi=0, a=2026):
    return datetime(a, m, d, h, mi, tzinfo=ZONA)


def ator(subject, *permissoes):
    from processo_seletivo.seguranca.domain import Actor

    return Actor(subject, "cefor", frozenset(permissoes))


GESTOR = ator("demo.gestor", "comissao:gerir", "processo:ativar")
PRESIDENCIA = ator("demo.presidente")
AVALIADORA, AVALIADOR = ator("demo.avaliadora"), ator("demo.avaliador")
JULGADOR = ator("demo.julgador", "recurso:julgar")
PUBLICADOR = ator("demo.publicador", "resultado:publicar")


def edital():
    from processo_seletivo.processos.models import Edital

    return Edital.objects.get(number="900", year=2026)


def identidade(codigo):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato

    numero = int(codigo[1:])
    nome = next(p[1] for p in ELENCO if p[0] == codigo)
    return IdentidadeDoCandidato(
        f"cand:demo-900-{numero:02d}",
        nome,
        cpf_valido(900000000 + numero * 7919),
        f"{codigo.lower()}@exemplo.test",
    )


def inscricao(codigo):
    from processo_seletivo.inscricoes.models import Inscricao

    return Inscricao.objects.get(
        edital=edital(), identity_subject=identidade(codigo).subject, status="SUBMETIDA"
    )


def pdf(nome, corpo):
    return SimpleUploadedFile(nome, b"%PDF-1.4\n" + corpo.encode(), content_type="application/pdf")


def pessoa(codigo):
    return next(p for p in ELENCO if p[0] == codigo)


def membro(subject):
    from processo_seletivo.comissoes.models import MembroComissao

    return MembroComissao.objects.get(processo=edital().processo, identity_subject=subject)


# ------------------------------------------------------------------------------------------- f0


def f0():
    """O Edital como o estudo o compôs à mão na interface — para reproduzir sem a interface."""
    from processo_seletivo.editais.application.draft import replace_draft
    from processo_seletivo.processos.application.commands import (
        create_process_with_first_edital,
    )
    from processo_seletivo.processos.management.commands import seed_demo
    from processo_seletivo.processos.models import Edital
    from processo_seletivo.unidades.models import AutoridadeHabilitada

    with em(dia(9, 11, 9)):
        elaborador = ator(
            "demo.elaborador", "processo:criar", "edital:elaborar", "edital:submeter"
        )
        processo, _ = create_process_with_first_edital(
            actor=elaborador,
            data={
                "institutionalCode": "PS-DEMO-CLASSIF-2027",
                "title": "Processo Seletivo Demonstrativo — Especialização em Docência (DEMO)",
                "firstEdital": {
                    "number": "900",
                    "year": 2026,
                    "title": "Seleção de estudantes — Especialização em Docência para a "
                    "Educação Profissional (turma demonstrativa)",
                    "description": "Edital fictício, para estudo de caso da classificação por "
                    "etapas. Nenhum dado é real.",
                },
            },
            idempotency_key=f"{CHAVE}-processo",
            correlation_id=CORRELACAO,
        )
        ed = Edital.objects.get(processo=processo)
        replace_draft(
            actor=elaborador,
            edital_id=ed.id,
            expected_revision=ed.revision,
            profiles=CONTEUDO["profiles"],
            schedule=[
                {
                    **evento,
                    "startAt": datetime.fromisoformat(evento["startAt"]),
                    "endAt": datetime.fromisoformat(evento["endAt"]) if evento.get("endAt") else None,
                }
                for evento in CONTEUDO["schedule"]
            ],
            stages=[
                {
                    **etapa,
                    **{
                        campo: Decimal(etapa[campo])
                        for campo in ("weight", "minimumScore", "maximumScore")
                        if etapa.get(campo) is not None
                    },
                }
                for etapa in CONTEUDO["stages"]
            ],
            document_requirements=CONTEUDO["documentRequirements"],
            correlation_id=CORRELACAO,
        )
        ed.refresh_from_db()
        from processo_seletivo.editais.application.teto import atualizar_teto_de_inscricoes

        atualizar_teto_de_inscricoes(
            actor=elaborador, edital_id=ed.id, expected_revision=ed.revision, teto=1
        )
        ed.refresh_from_db()
        comando = seed_demo.Command(stdout=io.StringIO())
        comando._unidade_e_autoridades()
        comando._publicar(
            elaborador,
            ator("demo.homologador", "edital:homologar"),
            ator("demo.publicador", "edital:publicar"),
            ed,
        )
    print("f0: Edital publicado;", AutoridadeHabilitada.objects.count(), "autoridades")


# ------------------------------------------------------------------------------------------- f1


def f1():
    """Dezoito inscrições, cada uma com Diploma e Currículo, espalhadas pelo período."""
    from processo_seletivo.identidade.application.associacao import associar_credencial
    from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
    from processo_seletivo.inscricoes.application.rascunho import (
        abrir_inscricao,
        anexar_documento,
        gravar_dados,
    )
    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao

    ed = edital()
    for k, (cod, nome, mod, nasc, *_) in enumerate(ELENCO):
        quem = identidade(cod)
        with em(dia(16 + k // 2, 11, 9 + k % 9, 7 * k % 60)):
            registro, _ = CandidateIdentity.objects.get_or_create(
                subject=quem.subject,
                defaults={
                    "nome": quem.nome,
                    "cpf_normalizado": quem.cpf.replace(".", "").replace("-", ""),
                    "created_at": timezone.now(),
                },
            )
            if not CandidateEmail.objects.filter(email_canonico=quem.email).exists():
                associar_credencial(registro, quem.email, quem.email)
            rascunho = abrir_inscricao(identidade=quem, edital_id=ed.id, profile_id=PERFIL_ID)
            rascunho = gravar_dados(
                identidade=quem,
                inscricao=rascunho,
                dados={
                    "nome": quem.nome,
                    "cpf": quem.cpf,
                    "email": quem.email,
                    "modality_id": MOD[mod],
                },
            )
            for chave, nome_doc in (("DIPLOMA", "diploma"), ("CURRICULO", "curriculo")):
                anexar_documento(
                    identidade=quem,
                    inscricao=rascunho,
                    requirement_id=DOC[chave],
                    arquivo=pdf(f"{nome_doc}-{cod}.pdf", f"{nome_doc} ficticio de {cod}"),
                )
            enviar_inscricao(
                identidade=quem,
                inscricao=rascunho,
                declaracoes={"veracidade": True, "ciencia": True},
                fatos={FATO: nasc.isoformat()},
                idempotency_key=f"{CHAVE}-envio-{cod}",
            )
    print("f1:", len(ELENCO), "inscrições enviadas")


# ------------------------------------------------------------------------------------------- f2


def _avaliar(etapa, alvo, instante, chave, *, nota=None, sentido=None, quem=AVALIADORA):
    """Distribuir à avaliadora, concluir cada inscrição e consolidar — o ciclo de uma Etapa."""
    from processo_seletivo.avaliacoes.application.avaliacao import concluir
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.resultados.application.consolidacao import consolidar

    ed = edital()
    inscricoes = [inscricao(c) for c in alvo]
    with em(instante):
        versao = effective_version(edital_id=ed.id)
        distribuir(
            actor=GESTOR,
            processo_id=ed.processo_id,
            edital_id=ed.id,
            etapa_id=etapa,
            membro_ids=[membro(quem.subject).id],
            inscricao_ids=[i.id for i in inscricoes],
            idempotency_key=f"{CHAVE}-lote-{chave}",
            correlation_id=CORRELACAO,
        )
    for k, (cod, ins) in enumerate(zip(alvo, inscricoes, strict=True)):
        extra = {}
        pontuacao = None
        if sentido:
            extra["sentido"] = sentido(cod)
            parecer = (
                MOTIVOS.get(cod, "Requisito comprovado pelo diploma anexado.")
                if extra["sentido"] == "DESFAVORAVEL"
                else "Requisito comprovado pelo diploma anexado."
            )
        else:
            pontuacao = Decimal(str(nota(cod)))
            parecer = f"Pontuação atribuída conforme o barema da Etapa ({pontuacao})."
        with em(instante + timedelta(hours=2, minutes=10 * k)):
            concluir(
                ator=quem,
                edital=ed,
                etapa_id=etapa,
                inscricao_id=ins.id,
                pontuacao=pontuacao,
                parecer=parecer,
                expected_revision=1,
                versao_reconhecida=versao.id,
                correlation_id=CORRELACAO,
                **extra,
            )
    with em(instante + timedelta(days=1, hours=6)):
        consolidar(
            actor=PRESIDENCIA,
            processo_id=ed.processo_id,
            edital_id=ed.id,
            etapa_id=etapa,
            inscricao_ids=[i.id for i in inscricoes],
            idempotency_key=f"{CHAVE}-consolidar-{chave}",
            correlation_id=CORRELACAO,
        )


def f2():
    """Comissão de três, alocada nas quatro Etapas; a Análise dos requisitos de todos."""
    from processo_seletivo.comissoes.application.alocacao import alocar
    from processo_seletivo.comissoes.application.comissao import adicionar_membro
    from processo_seletivo.comissoes.domain.funcoes import Funcao

    ed = edital()
    with em(dia(28, 11, 9)):
        for k, (subject, funcao) in enumerate(
            [
                ("demo.presidente", Funcao.PRESIDENTE),
                ("demo.avaliadora", Funcao.MEMBRO),
                ("demo.avaliador", Funcao.MEMBRO),
            ]
        ):
            adicionar_membro(
                actor=GESTOR,
                processo_id=ed.processo_id,
                identity_subject=subject,
                funcao=funcao,
                idempotency_key=f"{CHAVE}-membro-{k}",
                correlation_id=CORRELACAO,
            )
        for etapa in (REQ, CUR, PRO, ENT):
            for nome in ("demo.avaliadora", "demo.avaliador"):
                alocar(
                    actor=GESTOR,
                    processo_id=ed.processo_id,
                    membro_id=membro(nome).id,
                    edital_id=ed.id,
                    etapa_id=etapa,
                    idempotency_key=f"{CHAVE}-aloc-{etapa[:8]}-{nome}",
                    correlation_id=CORRELACAO,
                )
    todos = [p[0] for p in ELENCO]
    _avaliar(
        REQ,
        todos,
        dia(30, 11, 9),
        "req",
        sentido=lambda c: "FAVORAVEL" if pessoa(c)[4] == "D" else "DESFAVORAVEL",
    )
    print("f2: requisitos consolidados")


# ------------------------------------------------------------------------------------------- f3


def f3():
    """Currículo de quem foi deferido; a Prova de quem compareceu."""
    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

    deferidos = [p[0] for p in ELENCO if p[4] == "D"]
    _avaliar(CUR, deferidos, dia(2, 12, 9), "cur", nota=lambda c: pessoa(c)[5], quem=AVALIADOR)
    ed = edital()
    ausentes = [p[0] for p in ELENCO if p[6] == "AUSENTE"]
    with em(dia(5, 12, 13)):
        for cod in ausentes:
            registrar_ocorrencia(
                actor=PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                etapa_id=PRO,
                inscricao_ids=[inscricao(cod).id],
                motivo=MOTIVOS[cod],
                idempotency_key=f"{CHAVE}-ocorrencia-pro-{cod}",
                correlation_id=CORRELACAO,
            )
    presentes = [c for c in deferidos if c not in ausentes]
    _avaliar(PRO, presentes, dia(6, 12, 9), "pro", nota=lambda c: pessoa(c)[6])
    print("f3: currículo e prova consolidados")


# ------------------------------------------------------------------------------------------- f4


def _emitir(marco, lista, chave, motivo="", decisoes=()):
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.selectors import ato_vigente

    ed = edital()
    vigente = ato_vigente(edital=ed, marco_id=marco, lista_id=lista)
    if vigente is not None and not motivo:
        # Já emitida (no estudo, a da ampla do marco 1 foi emitida pela tela): emitir de novo sem
        # motivo seria sucessão sem motivo, que o comando recusa.
        return vigente
    proposta = calcular_ordem(edital=ed, perfil_id=PERFIL_ID, marco_id=marco, lista_id=lista)
    emitir_ordem(
        actor=PRESIDENCIA,
        processo_id=ed.processo_id,
        edital_id=ed.id,
        perfil_id=PERFIL_ID,
        marco_id=marco,
        lista_id=lista,
        motivo=motivo,
        decisoes=decisoes,
        idempotency_key=f"{CHAVE}-ordem-{chave}-{lista}",
        correlation_id=CORRELACAO,
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
    )
    return ato_vigente(edital=ed, marco_id=marco, lista_id=lista)


def _publicar(marco, lista, natureza, chave, declaracao=""):
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.divulgacao.application.publicar import (
        assinatura_da_previa,
        publicar_resultado,
    )
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.conteudo import compor
    from processo_seletivo.unidades.models import AutoridadeHabilitada

    ed = edital()
    ato = ato_vigente(edital=ed, marco_id=marco, lista_id=lista)
    anterior = vigente_do_marco(edital=ed, marco_id=marco, lista_id=lista)
    if anterior is not None and anterior.ato_id == ato.id and anterior.natureza == natureza:
        # Já divulgada (no estudo, algumas o foram pela tela).
        return anterior
    return publicar_resultado(
        actor=PUBLICADOR,
        processo_id=ed.processo_id,
        edital_id=ed.id,
        marco_id=marco,
        ato_id=ato.id,
        natureza=natureza,
        autoridade=AutoridadeHabilitada.objects.order_by("inicio_vigencia").first().id,
        confirmacao_da_previa=assinatura_da_previa(
            ato=ato, publicacao_anterior=anterior, projecao=compor(ato)
        ),
        declaracao_de_encerramento=declaracao,
        idempotency_key=f"{CHAVE}-pub-{chave}-{natureza}-{lista}",
        correlation_id=CORRELACAO,
    )


def f4():
    """As três ordens do marco 1, emitidas e divulgadas como preliminares."""
    f4a()
    f4b()


def f4a():
    with em(dia(9, 12, 9)):
        for lista in LISTAS:
            _emitir(M1, lista, "m1")


def f4b():
    with em(dia(9, 12, 12)):
        for lista in LISTAS:
            _publicar(M1, lista, "PRELIMINAR", "m1")
    print("f4: marco 1 emitido e divulgado (preliminar)")


# ------------------------------------------------------------------------------------------- f5


def _recorrer(codigo, publicacao, quando, fundamentacao, chave):
    from processo_seletivo.recursos.application.interpor import interpor

    with em(quando):
        return interpor(
            identidade=identidade(codigo),
            inscricao=inscricao(codigo),
            publicacao=publicacao,
            fundamentacao=fundamentacao,
            assinatura_do_objeto=str(publicacao.pk),
            idempotency_key=f"{CHAVE}-rec-{chave}",
        )


def _publicacao(marco, lista, natureza):
    from processo_seletivo.divulgacao.models import PublicacaoResultado

    return (
        PublicacaoResultado.objects.filter(
            edital=edital(), marco_id=marco, natureza=natureza, ato__lista_id=lista
        )
        .order_by("-publicado_em")
        .first()
    )


def f5():
    """O recurso de C10 contra a soma da Prova: admitido, correção fixada, ordem sucessora."""
    f5a()
    f5j()
    f5s()


def f5a():
    """C10 interpõe o recurso contra a classificação preliminar, dentro da janela."""
    _recorrer(
        RECURSO_DA_PROVA["codigo"],
        _publicacao(M1, None, "PRELIMINAR"),
        dia(10, 12, 15),
        "Na prova escrita, as questões 3 e 4 somam 76 pontos no espelho de correção, e não 68.",
        "c10",
    )


def f5j():
    """O julgador admite e fixa a correção (no estudo, feito pela tela do recurso)."""
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.application.selectors import assinatura_do_estado_da_peca
    from processo_seletivo.resultados.models import ResultadoEtapa

    from processo_seletivo.recursos.models import DecisaoRecurso, Recurso

    cod = RECURSO_DA_PROVA["codigo"]
    peca = Recurso.objects.get(inscricao=inscricao(cod))
    if DecisaoRecurso.objects.filter(recurso=peca).exists():
        return
    with em(dia(13, 12, 10)):
        admitir(
            actor=JULGADOR,
            recurso_id=peca.id,
            admitido=True,
            motivo="Tempestivo, e indica o ponto contestado.",
            assinatura_do_estado=assinatura_do_estado_da_peca(peca),
            idempotency_key=f"{CHAVE}-adm-c10",
        )
        superado = ResultadoEtapa.vigentes.get(inscricao=inscricao(cod), etapa_id=PRO)
        decisao, _ = julgar(
            actor=JULGADOR,
            recurso_id=peca.id,
            especie="CORRECAO_FIXADA",
            motivacao="Erro material de soma: o espelho de correção registra 76 pontos.",
            etapa_id=PRO,
            pontuacao=Decimal(str(RECURSO_DA_PROVA["para"])),
            assinatura_do_resultado=str(superado.id),
            idempotency_key=f"{CHAVE}-julgar-c10",
        )


def f5s():
    """A ordem sucessora da ampla, a única que o recurso tornou obsoleta (no estudo, pela tela).

    C10 concorre só na ampla: as ordens de PCD e PPI não mudam, e o sistema não as dá por obsoletas.
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.recursos.models import DecisaoRecurso

    decisao = DecisaoRecurso.objects.get(recurso__inscricao=inscricao(RECURSO_DA_PROVA["codigo"]))
    if ato_vigente(edital=edital(), marco_id=M1, lista_id=None).emitido_em > decisao.decidido_em:
        return
    with em(dia(13, 12, 14)):
        _emitir(
            M1,
            None,
            "m1-sucessora",
            motivo="Correção fixada no recurso REC de C10: Prova escrita de 68 para 76.",
        )
    print("f5s: ordem sucessora da ampla emitida")


def f5b():
    """A definitiva do marco 1, e os cortes que dizem quem vai à Entrevista."""
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )

    ed = edital()
    with em(dia(14, 12, 12)):
        for lista in LISTAS:
            _publicar(M1, lista, "DEFINITIVA", "m1")
    with em(dia(14, 12, 15)):
        for lista in LISTAS:
            emitir_corte(
                actor=PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                perfil_id=PERFIL_ID,
                marco_id=M1,
                lista_id=lista,
                idempotency_key=f"{CHAVE}-corte-m1-{lista}",
                correlation_id=CORRELACAO,
                confirmacao_do_calculo=assinatura_da_proposta(
                    calcular_corte(edital=ed, perfil_id=PERFIL_ID, marco_id=M1, lista_id=lista)
                ),
            )
    print("f5b: definitiva e cortes do marco 1")


# ------------------------------------------------------------------------------------------- f6


def na_entrevista():
    """Quem progrediu em qualquer corte do marco 1 — uma vez só, como a Etapa governada o lê."""
    from processo_seletivo.classificacao.models import ItemDoCorte

    ids = set(
        ItemDoCorte.objects.filter(
            consequencia="PROGREDIU", corte__marco_id=M1, inscricao__edital=edital()
        ).values_list("inscricao_id", flat=True)
    )
    return [p[0] for p in ELENCO if inscricao(p[0]).id in ids]


def f6():
    """A Entrevista de quem progrediu (com uma ausência) e as três ordens do marco 2."""
    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

    ed = edital()
    chamados = na_entrevista()
    ausentes = [c for c in chamados if pessoa(c)[7] == "AUSENTE"]
    with em(dia(17, 12, 19)):
        for cod in ausentes:
            registrar_ocorrencia(
                actor=PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                etapa_id=ENT,
                inscricao_ids=[inscricao(cod).id],
                motivo=MOTIVOS[cod],
                idempotency_key=f"{CHAVE}-ocorrencia-ent-{cod}",
                correlation_id=CORRELACAO,
            )
    presentes = [c for c in chamados if c not in ausentes]
    _avaliar(ENT, presentes, dia(18, 12, 9), "ent", nota=lambda c: pessoa(c)[7], quem=AVALIADOR)
    with em(dia(21, 12, 9)):
        for lista in LISTAS:
            _emitir(M2, lista, "m2")
    with em(dia(21, 12, 12)):
        for lista in LISTAS:
            _publicar(M2, lista, "PRELIMINAR", "m2")
    print("f6: entrevista consolidada; marco 2 emitido e divulgado (preliminar)")


# ------------------------------------------------------------------------------------------- f7


def f7():
    """C07, que perdeu a 6ª posição no desempate pela Entrevista, recorre; o recurso é indeferido."""
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.application.selectors import assinatura_do_estado_da_peca

    peca = _recorrer(
        "C07",
        _publicacao(M2, None, "PRELIMINAR"),
        dia(22, 12, 11),
        "Empatei com o 6º colocado e fiquei fora dos suplentes. Peço a revisão da nota da "
        "Entrevista, que decidiu o desempate.",
        "c07",
    )
    with em(dia(26, 12, 10)):
        admitir(
            actor=JULGADOR,
            recurso_id=peca.id,
            admitido=True,
            motivo="Tempestivo.",
            assinatura_do_estado=assinatura_do_estado_da_peca(peca),
            idempotency_key=f"{CHAVE}-adm-c07",
        )
        julgar(
            actor=JULGADOR,
            recurso_id=peca.id,
            especie="INDEFERIDO",
            motivacao="A nota da Entrevista confere com a ficha da banca, e o desempate seguiu o "
            "critério publicado (maior nota na Entrevista).",
            idempotency_key=f"{CHAVE}-julgar-c07",
        )
    with em(dia(28, 12, 12)):
        for lista in LISTAS:
            _publicar(M2, lista, "DEFINITIVA", "m2")
    print("f7: recurso indeferido; marco 2 definitivo")


# ------------------------------------------------------------------------------------------- f8


def f8():
    """Os cortes do marco 2 e a apuração das vagas: a ampla primeiro, depois cada reservada."""
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

    ed = edital()
    with em(dia(28, 12, 15)):
        for lista in LISTAS:
            emitir_corte(
                actor=PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                perfil_id=PERFIL_ID,
                marco_id=M2,
                lista_id=lista,
                idempotency_key=f"{CHAVE}-corte-m2-{lista}",
                correlation_id=CORRELACAO,
                confirmacao_do_calculo=assinatura_da_proposta(
                    calcular_corte(edital=ed, perfil_id=PERFIL_ID, marco_id=M2, lista_id=lista)
                ),
            )
    with em(dia(29, 12, 9)):
        for lista in LISTAS:
            emitir_apuracao(
                actor=PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                perfil_id=PERFIL_ID,
                marco_id=M2,
                lista_id=lista,
                idempotency_key=f"{CHAVE}-apurar-{lista}",
                correlation_id=CORRELACAO,
                motivo="",
            )
    print("f8: cortes e apuração do marco 2")


# ------------------------------------------------------------------------------------------- f9


class _Titular:
    """A identidade do candidato como o portal a tem: o `subject` da inscrição."""

    def __init__(self, codigo):
        self.subject = identidade(codigo).subject


def _convocacao(codigo):
    from processo_seletivo.convocacao.models import Convocacao

    return Convocacao.objects.filter(inscricao=inscricao(codigo)).order_by("-criado_em").first()


def _apresentar(codigo, chave, quando, corpo=None):
    from processo_seletivo.convocacao.application import documentos as servico

    convocacao = _convocacao(codigo)
    item = servico.raiz_da_chamada(convocacao).itens_da_lista.get(requisito_id=DOC[chave])
    arquivo = pdf(f"{chave.lower()}-{codigo}.pdf", corpo or f"{chave} ficticio de {codigo}")
    with em(quando):
        return servico.apresentar(
            identidade=_Titular(codigo),
            inscricao_id=inscricao(codigo).id,
            item_id=item.id,
            arquivo=arquivo,
            nome_original=arquivo.name,
            correlation_id=CORRELACAO,
        )


#: Quem apresenta o quê na primeira convocação. Bruno (C02) e Elisa (C13) desistem sem apresentar.
APRESENTACOES = {
    "C01": ["IDENTIDADE"],
    "C16": ["IDENTIDADE"],
    "C06": ["IDENTIDADE"],
    "C17": ["IDENTIDADE"],
}


def f9a():
    """Os convocados apresentam os documentos pelo portal (aqui, pelo serviço do portal)."""
    for k, (cod, chaves) in enumerate(APRESENTACOES.items()):
        for chave in chaves:
            _apresentar(cod, chave, dia(5, 1, 10 + k, a=2027))
    print("f9a: documentos apresentados")


def f9b():
    """Rafael reapresenta a identidade ilegível; Diana e Caio, convocados depois, apresentam a sua."""
    for k, cod in enumerate(("C06", "C09", "C08")):
        corpo = "identidade legivel, frente e verso, de C06" if cod == "C06" else None
        _apresentar(cod, "IDENTIDADE", dia(6, 1, 8 + k, a=2027), corpo=corpo)
    print("f9b: documentos reapresentados e apresentados")


FUNDAMENTO = (
    "Convocação no Edital nº 900/2026, na ordem de classificação vigente. Complemento: envie pelo "
    "Portal de Seleções os documentos pedidos nesta convocação até o prazo."
)
VENCIMENTO = dia(8, 1, 23, 59, a=2027)


def _convocar(codigo, lista, chave):
    from processo_seletivo.convocacao.application.comunicar import comunicar
    from processo_seletivo.convocacao.application.convocar import convocar

    ed = edital()
    declarado = convocar(
        actor=PRESIDENCIA,
        processo_id=ed.processo_id,
        edital_id=ed.id,
        perfil_id=PERFIL_ID,
        marco_id=M2,
        lista_id=lista,
        inscricao_id=inscricao(codigo).id,
        fundamento=FUNDAMENTO,
        vencimento=VENCIMENTO,
        idempotency_key=f"{CHAVE}-convocar-{chave}",
        correlation_id=CORRELACAO,
    )
    comunicar(
        actor=PRESIDENCIA,
        processo_id=ed.processo_id,
        convocacao_id=declarado["id"],
        idempotency_key=f"{CHAVE}-comunicar-{chave}",
        correlation_id=CORRELACAO,
    )


def _conferir(codigo, resultado, chave, motivo=""):
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.convocacao.application import documentos as servico

    item = servico.raiz_da_chamada(_convocacao(codigo)).itens_da_lista.get(
        requisito_id=DOC["IDENTIDADE"]
    )
    vigente = item.apresentacoes.order_by("-numero").first()
    if resultado == "CONFORME":
        # Quem confere abre a versão antes de dizê-la conforme (115, FR-3611): é o registro de
        # consulta que a tela grava ao clicar em "Abrir".
        record_event(
            actor=PRESIDENCIA,
            permission="",
            operation=servico.CONSULTAR_APRESENTACAO,
            aggregate=vigente,
            now=timezone.now(),
            correlation_id=CORRELACAO,
            new_state="",
            new_revision=None,
        )
    servico.conferir(
        actor=PRESIDENCIA,
        item_id=item.id,
        apresentacao_id=vigente.id,
        resultado=resultado,
        motivo=motivo,
        idempotency_key=f"{CHAVE}-conferir-{chave}",
        correlation_id=CORRELACAO,
    )


def _desfechar(codigo, especie, fundamento, chave):
    from processo_seletivo.convocacao.application.desfechar import desfechar

    desfechar(
        actor=PRESIDENCIA,
        processo_id=edital().processo_id,
        convocacao_id=_convocacao(codigo).id,
        especie=especie,
        fundamento=fundamento,
        idempotency_key=f"{CHAVE}-desfecho-{chave}",
        correlation_id=CORRELACAO,
    )


def _apurar(lista, motivo, chave):
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

    ed = edital()
    emitir_apuracao(
        actor=PRESIDENCIA,
        processo_id=ed.processo_id,
        edital_id=ed.id,
        perfil_id=PERFIL_ID,
        marco_id=M2,
        lista_id=lista,
        idempotency_key=f"{CHAVE}-apurar-{chave}",
        correlation_id=CORRELACAO,
        motivo=motivo,
    )


ACEITE = "Aceite manifestado no portal; documentos conferidos."
DESISTENCIA = "Desistência comunicada por e-mail em 05/01/2027."


def f9c():
    """Os titulares das três listas, convocados com a lista de documentos (no estudo, pela tela)."""
    with em(dia(4, 1, 9, a=2027)):
        for cod in ("C01", "C16", "C02", "C06"):
            _convocar(cod, None, cod)
        _convocar("C13", MOD["PCD"], "C13")
        _convocar("C17", MOD["PPI"], "C17")
    print("f9c: titulares convocados")


def f9d():
    """Conferências e desfechos de 05/01; a reversão da vaga PcD; a chamada de Diana e de Caio."""
    with em(dia(5, 1, 14, a=2027)):
        _conferir("C01", "CONFORME", "c01")
        _conferir("C16", "CONFORME", "c16")
        _conferir(
            "C06",
            "PENDENTE",
            "c06-v1",
            "A imagem do documento está ilegível. Envie de novo, com frente e verso legíveis.",
        )
        _desfechar("C01", "ACEITE", ACEITE, "c01")
        _desfechar("C16", "ACEITE", ACEITE, "c16")
        _desfechar("C02", "DESISTENCIA_EXPRESSA", DESISTENCIA, "c02")
        _desfechar("C13", "DESISTENCIA_EXPRESSA", DESISTENCIA, "c13")
        # A desistência na PcD não emite a apuração seguinte: ela moveria a vaga para a ampla pela
        # reversão declarada, e o movimento é ato próprio, praticado na tela da ocupação.
        _apurar(
            MOD["PCD"],
            "Desistência expressa de Elisa Viana (PcD): a lista PcD não tem outra pessoa habilitada.",
            "pcd-2",
        )
        _apurar(None, "Desistência de Bruno Taveira e reversão da vaga PcD não preenchida.", "ac-3")
        _convocar("C09", None, "C09")
        _convocar("C08", None, "C08")
    print("f9d: desfechos, reversão e nova convocação")


def f9e():
    """Conferências de 06/01 e os aceites que fecham as seis vagas."""
    with em(dia(6, 1, 10, a=2027)):
        for cod in ("C06", "C09", "C08", "C17"):
            _conferir(cod, "CONFORME", f"{cod.lower()}-final")
        for cod in ("C06", "C09", "C08", "C17"):
            _desfechar(cod, "ACEITE", ACEITE, cod.lower())
    print("f9e: aceites")


def f9():
    f9c()
    f9a()
    f9d()
    f9b()
    f9e()


TODAS = ("f0", "f1", "f2", "f3", "f4", "f5", "f5b", "f6", "f7", "f8", "f9")


FASES = {f.__name__: f for f in (f0, f1, f2, f3, f4, f4a, f4b, f5, f5a, f5j, f5s, f5b, f6, f7, f8, f9a, f9b, f9c, f9d, f9e, f9)}

if __name__ == "__main__":
    for nome in TODAS if sys.argv[1:] == ["tudo"] else sys.argv[1:]:
        FASES[nome]()
