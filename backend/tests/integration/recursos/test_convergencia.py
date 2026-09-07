"""Os dez achados do code review, cada um com o teste que falha sem a correção.

Este módulo não organiza por funcionalidade: organiza pelo **defeito**. Cada caso descreve o que
acontecia antes e por que aquilo era errado, porque é essa a informação que se perde primeiro — o
código corrigido não conta o que ele deixou de fazer.
"""

import re
from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.application.selectors import (
    assinatura_do_estado_da_peca,
    reavaliacoes_pendentes,
    resumo,
)
from processo_seletivo.recursos.domain.elegibilidade import CONSOLIDOU, impedimento
from processo_seletivo.recursos.domain.janela import admite_recurso, computavel
from processo_seletivo.recursos.models import DecisaoRecurso, Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.recursos_us4 import (
    JULGADORA,
    assinatura_de,
    cenario_julgavel,
    julgador,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=150, codigo="0850"
    )


def interpor_contra_a_publicacao(peca, inscricao, *, chave):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor

    publicacao = peca["publicacao"]
    return interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        publicacao=publicacao,
        fundamentacao="A minha nota da Etapa do marco está errada na divulgação.",
        assinatura_do_objeto=str(publicacao.pk),
        idempotency_key=chave,
    )


# ---------------------------------------------------------------------------
# 1 — a interposição serializa com a publicação definitiva
# ---------------------------------------------------------------------------


def test_interpor_trava_o_processo_como_publicar_e_emitir(peca):
    """**Sem este bloqueio, a definitiva e a interposição confirmam as duas** (spec §concorrência).

    A aferição lê "zero recursos pendentes" enquanto a interposição é gravada na transação vizinha,
    e nasce um resultado definitivo com recurso pendente dentro dele — o defeito do E2E17-005 outra
    vez, agora por corrida em vez de por seletor livre.

    O teste lê o SQL emitido: é a única forma de provar o bloqueio sem montar duas conexões
    concorrentes, que tornaria a suíte não determinística. O ponto travado é o `ProcessoSeletivo`,
    o mesmo que emitir, publicar e consolidar já travam — travar em outro lugar criaria uma segunda
    ordem de bloqueio, que é como nascem os *deadlocks*.
    """
    outra = peca["cenario"]["inscricoes"][1]

    with CaptureQueriesContext(connection) as consultas:
        interpor_contra_a_publicacao(peca, outra, chave="serializa")

    travas = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "FOR UPDATE" in consulta["sql"] and "processos_processoseletivo" in consulta["sql"]
    ]
    assert travas, "interpor precisa travar o Processo, como publicar já faz"


# ---------------------------------------------------------------------------
# 2 — recurso contra publicação produz correção pelo canal real
# ---------------------------------------------------------------------------


def test_recurso_contra_publicacao_corrige_o_resultado_pela_tela(client, seletor_ligado, peca):
    """**O objeto atacado e o lugar do erro são eixos distintos** (D-001).

    Um recurso contra a divulgação cujo mérito é "minha nota da Etapa 2 está errada" corrige o
    `ResultadoEtapa` daquela Etapa. Enquanto a tela derivava a Etapa do objeto atacado, este recurso
    chegava ao julgador **sem alvo**, e o formulário escondia `CORRECAO_FIXADA` e
    `REAVALIACAO_DETERMINADA` — quem recorreu da divulgação por causa da própria nota não tinha,
    pelo canal real, como obter a correção que a decisão institucional prometeu.
    """
    cenario = peca["cenario"]
    inscricao = peca["inscricao"]
    contra_a_publicacao = interpor_contra_a_publicacao(peca, inscricao, chave="publicacao-corrige")
    admitir(
        actor=julgador(),
        recurso_id=contra_a_publicacao.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(contra_a_publicacao),
        idempotency_key="admitir-publicacao-corrige",
    )

    identificar(client, JULGADORA, ["julgador"])
    tela = reverse("interface:recurso", args=[contra_a_publicacao.id])
    corpo = client.get(tela).content.decode()

    # A tela **oferece** a correção, e oferece a Etapa que o marco enumera.
    assert 'value="CORRECAO_FIXADA"' in corpo
    assert 'value="REAVALIACAO_DETERMINADA"' in corpo
    vigente = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa_do_recurso"])
    opcao = re.search(r'<option value="([^"|]+)\|([^"]+)"', corpo)
    assert opcao.group(2) == str(vigente.id), "a opção carrega a assinatura do Resultado vigente"

    resposta = client.post(
        reverse("interface:recurso-julgar", args=[contra_a_publicacao.id]),
        {
            "especie": "CORRECAO_FIXADA",
            "motivacao": "A nota divulgada não corresponde ao parecer.",
            "etapa": f"{opcao.group(1)}|{opcao.group(2)}",
            f"pontuacao-{opcao.group(1)}": "82.0000",
        },
    )

    assert resposta.status_code == 302
    sucessor = ResultadoEtapa.vigentes.get(
        inscricao=inscricao, etapa_id=cenario["etapa_do_recurso"]
    )
    assert sucessor.resultado_anterior_id == vigente.id
    assert sucessor.pontuacao == Decimal("82.0000")


# ---------------------------------------------------------------------------
# 3 — o impedimento alcança o par que a decisão atinge
# ---------------------------------------------------------------------------


def test_quem_consolidou_a_etapa_nao_julga_recurso_contra_a_publicacao_que_a_corrige(peca):
    """A brecha estava no ramo da publicação (FR-039).

    Olhando só para o objeto atacado, quem consolidou o Resultado da Etapa podia julgar um recurso
    contra a **publicação** e, nele, corrigir esse mesmo Resultado — julgando a correção do próprio
    ato. A elegibilidade precisa conhecer o par que o remédio alcança, e não só o objeto atacado.
    """
    cenario = peca["cenario"]
    contra_a_publicacao = interpor_contra_a_publicacao(
        peca, peca["inscricao"], chave="impedimento-publicacao"
    )
    consolidadora = ator_institucional("carlos", "recurso:julgar")

    # Sem a Etapa, o objeto atacado é só a publicação — e ela não foi publicada por Carlos.
    assert impedimento(consolidadora, contra_a_publicacao) != CONSOLIDOU
    # Com a Etapa que a decisão alcança, o impedimento aparece.
    assert (
        impedimento(consolidadora, contra_a_publicacao, etapa_id=cenario["etapa_do_recurso"])
        == CONSOLIDOU
    )

    admitir(
        actor=julgador(),
        recurso_id=contra_a_publicacao.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(contra_a_publicacao),
        idempotency_key="admitir-impedimento-publicacao",
    )

    with pytest.raises(DomainError) as recusa:
        julgar(
            actor=consolidadora,
            recurso_id=contra_a_publicacao.id,
            especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
            motivacao="Corrijo o que eu mesmo consolidei.",
            etapa_id=cenario["etapa_do_recurso"],
            pontuacao=Decimal("82.0000"),
            assinatura_do_resultado=str(peca["superado"].id),
            idempotency_key="julgar-impedido",
        )

    assert recusa.value.code == "appeal_judge_barred"
    assert not DecisaoRecurso.objects.exists()


# ---------------------------------------------------------------------------
# 4 — a assinatura do estado é obrigatória
# ---------------------------------------------------------------------------


def test_admitir_sem_assinatura_e_recusado(
    peca, gestor, api_client, manager_headers, process_payload
):
    """**Omitir o campo contornava a revisão otimista inteira** (FR-100).

    Enquanto a comparação só acontecia com a assinatura preenchida, bastava não dizer o que se leu
    para poder gravar sobre qualquer estado. A garantia que se pode omitir não é garantia.
    """
    nova = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=151,
        codigo="0851",
        admitir_a_peca=False,
    )

    with pytest.raises(DomainError) as recusa:
        admitir(
            actor=julgador(),
            recurso_id=nova["recurso"].id,
            admitido=True,
            motivo="Tempestivo.",
            assinatura_do_estado="",
            idempotency_key="sem-assinatura",
        )

    assert recusa.value.code == "stale_appeal_state"
    assert recusa.value.status == 409
    assert not nova["recurso"].juizos.exists()


def test_julgar_correcao_sem_assinatura_do_resultado_e_recusado(peca):
    with pytest.raises(DomainError) as recusa:
        julgar(
            actor=julgador(),
            recurso_id=peca["recurso"].id,
            especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
            motivacao="Revisão da pontuação.",
            etapa_id=peca["cenario"]["etapa_do_recurso"],
            pontuacao=Decimal("82.0000"),
            assinatura_do_resultado="",
            idempotency_key="julgar-sem-assinatura",
        )

    assert recusa.value.code == "stale_stage_result"
    assert not DecisaoRecurso.objects.exists()


# ---------------------------------------------------------------------------
# 5 — a decisão cita a norma vigente no julgamento
# ---------------------------------------------------------------------------


def test_a_decisao_cita_a_versao_vigente_no_julgamento_e_nao_a_da_interposicao(peca, api_client):
    """Havendo Retificação entre a interposição e o julgamento, a decisão é tomada sob a norma
    **de agora** (FR-045, FR-059).

    Gravar a versão da peça faria a decisão afirmar ter sido tomada sob regra revogada — e a
    consequência sairia de uma nota mínima que já não vale. A versão que a peça cita continua
    registrada nela: é a regra sob a qual se **recorreu**, e responde outra pergunta.
    """
    from processo_seletivo.publicacoes.application.selectors import selecao_publica
    from tests.fixtures.publicacao import retify

    versao_da_peca = peca["recurso"].versao_id
    retify(
        api_client,
        peca["cenario"]["edital"],
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado no meio"}],
        suffix="convergencia",
    )
    agora = selecao_publica(edital_id=peca["cenario"]["edital"].id).id
    assert agora != versao_da_peca, "a Retificação precisa ter mesmo produzido outra versão"

    decisao, _sucessor = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="Revisão da pontuação.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="julgar-apos-retificacao",
    )

    assert decisao.versao_id == agora
    peca["recurso"].refresh_from_db()
    assert peca["recurso"].versao_id == versao_da_peca, "a peça guarda a norma da interposição"


# ---------------------------------------------------------------------------
# 6 — duas reavaliações pendentes da mesma inscrição não colidem
# ---------------------------------------------------------------------------


def test_duas_reavaliacoes_da_mesma_inscricao_em_etapas_distintas_convivem(
    gestor, api_client, manager_headers, process_payload
):
    """**Chaveando por inscrição, a segunda sobrescrevia a primeira** — em silêncio.

    A pendência desaparecida liberaria indevidamente a publicação definitiva do marco que enumera a
    Etapa perdida. É o tipo de perda que não produz erro nenhum: o dicionário fica menor, e ninguém
    percebe (FR-066, FR-082).
    """
    cenario = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=152,
        codigo="0852",
        na_primeira_etapa=True,
        # **Habilitada na Etapa 1**, de propósito: quem foi eliminada ali não participa da Etapa 2,
        # e o cenário precisa da mesma pessoa com pendência nas duas.
        pontuacoes=("70.0000", "90.0000"),
    )
    inscricao = cenario["inscricao"]
    primeira = cenario["cenario"]["primeira"]

    _determinar_reavaliacao(cenario["recurso"], primeira, cenario["superado"], "reav-primeira")
    segunda_peca, segundo_alvo = _segunda_peca_em_outra_etapa(cenario)
    _determinar_reavaliacao(
        segunda_peca, cenario["cenario"]["segunda"], segundo_alvo, "reav-segunda"
    )

    pendentes = reavaliacoes_pendentes(cenario["cenario"]["edital"])

    assert len(pendentes) == 2, "as duas pendências precisam sobreviver à mesma inscrição"
    assert {etapa for _identidade, etapa in pendentes} == {
        _uuid(primeira),
        _uuid(cenario["cenario"]["segunda"]),
    }
    assert {identidade for identidade, _etapa in pendentes} == {inscricao.id}


# ---------------------------------------------------------------------------
# 7 — `admits: false` não é ausência
# ---------------------------------------------------------------------------


def test_admits_falso_e_norma_e_nao_silencio():
    """```text
    None    o Edital não declarou nada sobre recurso naquele marco
    False   o Edital declarou que aquele marco NÃO admite recurso
    True    admite, e a duração diz por quanto tempo
    ```

    Confundir `False` com `None` transforma "não cabe recurso" em "cabe para sempre" — o oposto
    exato do que a norma disse (FR-020).
    """
    assert admite_recurso(None) is None
    assert admite_recurso({}) is None
    assert admite_recurso({"admits": False}) is False
    assert admite_recurso({"admits": True, "durationDays": 5}) is True
    # E as três continuam sem janela **computável**, que é outra pergunta.
    assert computavel({"admits": False}) is None


def test_marco_que_nao_admite_recurso_recusa_a_interposicao(
    gestor, api_client, manager_headers, process_payload
):
    """E a ação **não é oferecida** na tela, porque a recusa não é o caminho normal (FR-013)."""
    from processo_seletivo.recursos.application.interpor import objetos_recorriveis
    from tests.integration.recursos.test_janela import _declarar_janela, montar

    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=153,
        codigo="0853",
        janela={"admits": False, "durationDays": None, "unit": "DIAS_CORRIDOS"},
    )
    inscricao = cenario["inscricoes"][0]
    _declarar_janela(cenario, cenario["marco"], {"admits": False, "unit": "DIAS_CORRIDOS"})

    assert objetos_recorriveis(inscricao) == []

    from tests.integration.recursos.test_janela import interpor_como_titular

    with pytest.raises(DomainError) as recusa:
        interpor_como_titular(cenario, inscricao, chave="nao-admite")

    # **Código próprio**: "o recurso não é previsto" e "o prazo dele passou" são orientações
    # opostas para quem as recebe, e um código só as tornaria indistinguíveis (FR-113).
    assert recusa.value.code == "appeal_not_provided"
    assert recusa.value.code != "appeal_window_closed"
    assert "não admite recurso" in recusa.value.detail
    assert not Recurso.objects.exists()


# ---------------------------------------------------------------------------
# 8 — a reserva representa o pedido inteiro
# ---------------------------------------------------------------------------


def test_a_mesma_chave_contra_outro_objeto_e_conflito(peca):
    """**Sem o objeto na reserva, a repetição devolvia a peça errada** (FR-098).

    Quem recorreu de duas coisas com a mesma chave receberia o protocolo de uma só, e sairia
    achando que recorreu das duas.
    """
    cenario = peca["cenario"]
    outra = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=outra, etapa_id=cenario["etapa_do_recurso"])

    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor

    identidade = IdentidadeDoCandidato(
        outra.identity_subject, outra.nome, outra.cpf_normalizado, "o@ex.br"
    )
    interpor(
        identidade=identidade,
        inscricao=outra,
        resultado=alvo,
        fundamentacao="A mesma razão.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="chave-compartilhada",
    )

    with pytest.raises(DomainError) as recusa:
        interpor(
            identidade=identidade,
            inscricao=outra,
            publicacao=peca["publicacao"],
            fundamentacao="A mesma razão.",
            assinatura_do_objeto=str(peca["publicacao"].pk),
            idempotency_key="chave-compartilhada",
        )

    assert recusa.value.code == "idempotency_conflict"
    assert Recurso.objects.filter(inscricao=outra).count() == 1


def test_a_mesma_chave_com_outra_declaracao_e_conflito(peca):
    """A declaração de encerramento faz parte do pedido de publicação (FR-098)."""
    from tests.fixtures.divulgacao import publicar_o_ato

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-declaracao-chave",
    )
    publicar_o_ato(
        peca["cenario"],
        natureza="DEFINITIVA",
        chave="mesma-chave-declaracao",
        declaracao="O prazo encerrou-se sem interposição.",
    )

    with pytest.raises(DomainError) as recusa:
        publicar_o_ato(
            peca["cenario"],
            natureza="DEFINITIVA",
            chave="mesma-chave-declaracao",
            declaracao="Outro fundamento inteiramente diferente.",
        )

    assert recusa.value.code == "idempotency_conflict"


# ---------------------------------------------------------------------------
# 9 — a trilha nasce com motivo
# ---------------------------------------------------------------------------


def test_todo_evento_da_018_nasce_com_motivo(peca):
    """Sem motivo, a trilha responde "houve um evento" e obriga quem audita a abrir o agregado.

    A FR-094 pede narrativa auditável; o que ela **não** admite é a narrativa carregar o conteúdo do
    juízo — e por isso o motivo diz o ato, e não a razão escrita nem a grandeza (FR-095).
    """
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="Revisão da pontuação atribuída.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="julgar-trilha",
    )

    eventos = list(
        RegistroAuditoria.objects.filter(operation__startswith="recurso:")
        | RegistroAuditoria.objects.filter(operation="resultado:superar")
    )

    assert eventos
    for evento in eventos:
        assert evento.reason, f"{evento.operation} nasceu sem motivo"
        assert peca["recurso"].protocolo in evento.reason
        assert "82.0000" not in evento.reason
        assert peca["recurso"].fundamentacao not in evento.reason


# ---------------------------------------------------------------------------
# 10 — o contrato do candidato
# ---------------------------------------------------------------------------


def test_o_objeto_e_nomeado_pelo_marco_ou_pela_etapa(peca):
    """ "O resultado divulgado" não identifica nada para quem tem dois marcos publicados."""
    contra_o_resultado = resumo(peca["recurso"])
    cenario = peca["cenario"]
    contra_a_publicacao = resumo(
        interpor_contra_a_publicacao(peca, cenario["inscricoes"][1], chave="nome-do-objeto")
    )

    assert contra_o_resultado["objeto"] == "o meu resultado da Prova didática"
    assert contra_a_publicacao["objeto"] == "o resultado divulgado da Classificação final"


def test_o_candidato_le_quem_decidiu(client, peca):
    """Uma decisão sem autor não é ato administrativo: é um texto que apareceu."""
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="julgar-quem-decidiu",
    )

    entrar_como_titular(client, peca["inscricao"])
    corpo = client.get(reverse("portal:recurso", args=[peca["recurso"].id])).content.decode()

    assert f"decidido por {JULGADORA}" in corpo


# ---------------------------------------------------------------------------


def _uuid(valor):
    from processo_seletivo.comissoes.application.comissao import identificador

    return identificador(valor)


def _determinar_reavaliacao(recurso, etapa_id, protegido, chave):
    return julgar(
        actor=julgador(),
        recurso_id=recurso.id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se por avaliador diverso.",
        etapa_id=etapa_id,
        assinatura_do_resultado=str(protegido.id),
        idempotency_key=chave,
    )


def _segunda_peca_em_outra_etapa(cenario):
    """A mesma pessoa recorre também do Resultado da segunda Etapa.

    Não é rebuscado: quem discorda de duas Etapas recorre das duas, e a unicidade é por objeto.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor
    from tests.fixtures.mesa import concluir_como, distribuir_para

    interior = cenario["cenario"]
    inscricao = cenario["inscricao"]
    contexto = {**interior, "etapa": interior["segunda"]}
    distribuir_para(contexto, _gestor(), ["joao"], [inscricao], chave="lote-convergencia")
    concluir_como(contexto, "joao", inscricao, pontuacao="70.0000")
    _consolidar(interior, interior["segunda"], [inscricao], chave="consolidar-convergencia")
    # **A Etapa 2 precisa estar divulgada** para que o Resultado dela seja recorrível: o fato que
    # autoriza a leitura é o mesmo que autoriza a interposição (D-003).
    from tests.fixtures.divulgacao import emitir, publicar_o_ato

    final = emitir(interior, _gestor(), marco=interior["marco"], chave="emitir-convergencia")
    publicar_o_ato(interior, chave="publicar-convergencia", ato=final)

    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=interior["segunda"])
    peca = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="A nota da segunda Etapa também está errada.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="interpor-segunda-etapa",
    )
    admitir(
        actor=julgador(),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_do_estado_da_peca(peca),
        idempotency_key="admitir-segunda-etapa",
    )
    return peca, alvo


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


def _consolidar(cenario, etapa_id, inscricoes, *, chave):
    from processo_seletivo.resultados.application.consolidacao import consolidar

    return consolidar(
        actor=_gestor(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa_id,
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=chave,
        correlation_id="convergencia",
    )
