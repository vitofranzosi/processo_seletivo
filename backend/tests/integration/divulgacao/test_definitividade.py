""" "Definitivo" deixa de ser escolha livre de um seletor.

O E2E17-005 registrou o defeito numa frase: nada impedia publicar como **definitivo** um resultado
ainda em disputa. A natureza era um `<select>`, e o sistema acreditava.

```text
1  recurso pendente pertinente          impede a DEFINITIVA
2  reavaliação determinada não cumprida impede a DEFINITIVA
3  providência a jusante não cumprida   impede a DEFINITIVA
4  janela estruturada aberta            impede a DEFINITIVA
5  ato obsoleto                         impede AS DUAS naturezas
6  reingresso pendente                  impede AS DUAS naturezas
```

**A assimetria é dos quatro primeiros, e não dos seis** (FR-082, FR-083). Eles são fatos da
**disputa**: enquanto ela corre, publicar como preliminar é o caminho normal — é o preliminar que
abre o prazo, e bloqueá-lo travaria o certame exatamente onde ele precisa andar.

Os dois últimos não são da disputa: são do **conteúdo** do que se vai divulgar. Ato obsoleto
publica ordem revogada, e reingresso pendente publica ordem que já se sabe incompleta — e nenhuma
das duas fica menos falsa por chamar-se preliminar (D-007, FR-079).
"""

import pytest

from processo_seletivo.divulgacao.domain.publicabilidade import (
    DECLARACAO_EXIGIDA,
    DECLARACAO_RECUSADA,
    DESATUALIZADO,
    IMPEDIMENTO,
    PROVIDENCIA_PENDENTE,
    REAVALIACAO_PENDENTE,
    RECURSO_PENDENTE,
    aferir,
)
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, publicar_o_ato
from tests.fixtures.recursos_us4 import assinatura_de, cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

DECLARACAO = "O prazo recursal encerrou-se sem interposição, conforme o Edital."


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """Um recurso interposto e admitido sobre o `ResultadoEtapa` da Etapa do marco.

    O ato do marco **não** foi emitido de novo depois disso: o cenário parte de um marco publicado
    como preliminar, que é como a instituição chega à definitiva.
    """
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=124, codigo="0824"
    )


def afere(peca, natureza, *, ato=None):
    cenario = peca["cenario"]
    return aferir(
        edital=cenario["edital"],
        marco_id=cenario["marco"],
        ato=ato or cenario["ato"],
        natureza=natureza,
    )


def publicar(peca, natureza, *, chave, ato=None, declaracao=None):
    return publicar_o_ato(
        peca["cenario"],
        natureza=natureza,
        chave=chave,
        ato=ato,
        declaracao=declaracao,
    )


# ---------------------------------------------------------------------------
# T094 — os fatos, um a um
# ---------------------------------------------------------------------------


def test_recurso_pendente_impede_a_definitiva_e_nao_a_preliminar(peca):
    """O fato 1, e a assimetria que é a substância da regra (FR-082, FR-083, SC-017)."""
    definitiva = afere(peca, "DEFINITIVA")
    preliminar = afere(peca, "PRELIMINAR")

    assert definitiva.nivel == IMPEDIMENTO
    assert definitiva.codigo == RECURSO_PENDENTE
    assert "publique como resultado preliminar" in definitiva.mensagem
    assert preliminar.publicavel is True


def test_o_recurso_do_resultado_individual_tambem_e_pertinente(peca):
    """**A metade fácil de esquecer** (FR-084).

    A peça deste cenário ataca o `ResultadoEtapa`, e não a publicação do marco. Sem alcançá-la, o
    recurso individual seria a porta por onde uma definitiva nasceria com um Resultado em disputa
    dentro dela.
    """
    assert peca["recurso"].resultado_atacado_id is not None
    assert peca["recurso"].publicacao_atacada_id is None

    assert afere(peca, "DEFINITIVA").codigo == RECURSO_PENDENTE


def test_decidido_o_recurso_a_definitiva_passa(peca):
    """A prova de que o impedimento é do recurso pendente, e não do cenário."""
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-definitividade",
    )

    assert afere(peca, "DEFINITIVA").publicavel is True


def test_o_recurso_inadmitido_nao_impede(gestor, api_client, manager_headers, process_payload):
    """Inadmitir é resposta: a instituição disse que não conhece do recurso, e isso resolve.

    O que impede a definitiva é a **disputa em aberto**, e não a existência de uma peça.
    """
    from processo_seletivo.recursos.application.admitir import admitir

    outra = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=125,
        codigo="0825",
        admitir_a_peca=False,
    )
    admitir(
        actor=julgador(),
        recurso_id=outra["recurso"].id,
        admitido=False,
        motivo="Interposto fora de qualquer prazo razoável.",
        assinatura_do_estado=assinatura_de(outra["recurso"]),
        idempotency_key="inadmitir-definitividade",
    )

    assert afere(outra, "DEFINITIVA").publicavel is True


def test_o_ato_obsoleto_impede_as_duas_naturezas(peca):
    """Os fatos 5 e 6 **não** têm a assimetria dos quatro primeiros (D-007, FR-079).

    A revisão do PR encontrou a spec afirmando as duas coisas: a D-007 dizia que a reinclusão
    pendente impede *a publicação daquele marco*, e a D-008 listava-a entre o que impede só a
    definitiva, fechando com "a preliminar continua livre em todos esses casos". O código sempre
    fez o certo — os dois são aferidos antes de a natureza ser consultada —, e era a prosa que
    prometia o contrário.

    Chamar de preliminar uma ordem revogada não a torna menos revogada. O rótulo diz que a
    contestação ainda corre, e não que o conteúdo pode estar errado.
    """
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="O documento juntado na inscrição não foi considerado.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao="82.0000",
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="corrigir-obsolescencia",
    )

    definitiva = afere(peca, "DEFINITIVA")
    preliminar = afere(peca, "PRELIMINAR")

    assert definitiva.nivel == IMPEDIMENTO
    assert preliminar.nivel == IMPEDIMENTO, "preliminar de ordem revogada continua sendo revogada"
    assert preliminar.codigo == DESATUALIZADO

    # E o comando recusa, que é quem grava — a aferição sozinha não protege nada.
    with pytest.raises(DomainError) as recusa:
        publicar(peca, "PRELIMINAR", chave="preliminar-com-ato-obsoleto")
    assert recusa.value.code == DESATUALIZADO


def test_reavaliacao_determinada_impede_a_definitiva(peca):
    """O fato 2: há trabalho de avaliação por fazer, e a ordem ainda vai mudar."""
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-definitividade",
    )

    resultado = afere(peca, "DEFINITIVA")

    assert resultado.codigo == REAVALIACAO_PENDENTE
    assert afere(peca, "PRELIMINAR").publicavel is True


def test_providencia_a_jusante_impede_a_definitiva(peca):
    """O fato 3: a decisão reconheceu um vício e mandou corrigi-lo — e ninguém corrigiu ainda."""
    _determinar_providencia(peca)

    resultado = afere(peca, "DEFINITIVA")

    assert resultado.codigo == PROVIDENCIA_PENDENTE
    assert "citando a decisão" in resultado.mensagem
    assert afere(peca, "PRELIMINAR").publicavel is True


# ---------------------------------------------------------------------------
# T095 e T096 — o cumprimento por citação **publicada**, e a recitação
# ---------------------------------------------------------------------------


def test_ato_que_nao_cita_deixa_a_pendencia_aberta(peca):
    """**Publicar ato diferente não cumpre** (T-015).

    Um ato sucessor emitido por razão alheia — uma Retificação que mudou um peso — encerraria a
    pendência sem que ninguém tivesse corrigido o vício reconhecido. O vínculo tem de ser causal.
    """
    _determinar_providencia(peca)
    cenario = peca["cenario"]

    cenario["ato"] = emitir(cenario, _gestor(), chave="emitir-sem-citar", motivo="Outra razão.")
    publicar(peca, "PRELIMINAR", chave="publicar-sem-citar", ato=cenario["ato"])

    assert afere(peca, "DEFINITIVA", ato=cenario["ato"]).codigo == PROVIDENCIA_PENDENTE


def test_citar_sem_publicar_tambem_deixa_a_pendencia_aberta(peca):
    """**Citar não é cumprir**: o ato citante pode ficar obsoleto antes de ser publicado."""
    decisao = _determinar_providencia(peca)
    cenario = peca["cenario"]

    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-citando",
        motivo="Cumprimento da decisão.",
        decisoes=[str(decisao.id)],
    )

    # O ato **candidato** cita, e por isso ele próprio pode ser publicado — não é circular.
    assert afere(peca, "DEFINITIVA", ato=citante).publicavel is True
    # E a pendência do **marco** continua aberta, porque citação nenhuma foi publicada ainda. É
    # ela que se pergunta sem candidato: o ato citante pode ficar obsoleto antes de ser publicado,
    # e nesse caso ninguém corrigiu coisa alguma.
    assert _pendentes_do_marco(peca) == [decisao.id]


def test_ato_citante_publicado_cumpre_a_providencia(peca):
    decisao = _determinar_providencia(peca)
    cenario = peca["cenario"]

    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-citante",
        motivo="Cumprimento da decisão.",
        decisoes=[str(decisao.id)],
    )
    publicar(peca, "PRELIMINAR", chave="publicar-citante", ato=citante)
    cenario["ato"] = citante

    seguinte = emitir(cenario, _gestor(), chave="emitir-seguinte", motivo="Ajuste posterior.")

    assert afere(peca, "DEFINITIVA", ato=seguinte).publicavel is True


def test_um_ato_cita_duas_decisoes(peca, gestor, api_client, manager_headers, process_payload):
    """Dois deferimentos sobre o mesmo marco se resolvem numa emissão só (FR-112)."""
    from processo_seletivo.classificacao.models import CitacaoDeDecisao

    primeira = _determinar_providencia(peca)
    segunda = _determinar_providencia_da_outra(peca)
    cenario = peca["cenario"]

    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-duas",
        motivo="Cumprimento das duas decisões.",
        decisoes=[str(primeira.id), str(segunda.id)],
    )
    publicar(peca, "PRELIMINAR", chave="publicar-duas", ato=citante)
    cenario["ato"] = citante

    assert CitacaoDeDecisao.objects.filter(ato=citante).count() == 2
    seguinte = emitir(cenario, _gestor(), chave="emitir-depois-das-duas", motivo="Ajuste.")
    assert afere(peca, "DEFINITIVA", ato=seguinte).publicavel is True


def test_o_sucessor_recita_a_decisao_quando_o_citante_fica_obsoleto(peca):
    """**A recitação impede o único beco possível** (FR-112).

    Um `UNIQUE(decisao)` — que uma redação anterior previa — tornaria a definitiva deste marco
    impedida para sempre no dia em que o primeiro ato citante ficasse obsoleto antes de publicar.
    """
    from processo_seletivo.classificacao.models import CitacaoDeDecisao

    decisao = _determinar_providencia(peca)
    cenario = peca["cenario"]

    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-obsoleto",
        motivo="Cumprimento.",
        decisoes=[str(decisao.id)],
    )
    cenario["ato"] = citante
    sucessor = emitir(
        cenario,
        _gestor(),
        chave="emitir-recitando",
        motivo="O anterior ficou obsoleto.",
        decisoes=[str(decisao.id)],
    )

    assert CitacaoDeDecisao.objects.filter(decisao=decisao).count() == 2
    publicar(peca, "PRELIMINAR", chave="publicar-recitado", ato=sucessor)
    cenario["ato"] = sucessor
    seguinte = emitir(cenario, _gestor(), chave="emitir-apos-recitacao", motivo="Ajuste.")
    assert afere(peca, "DEFINITIVA", ato=seguinte).publicavel is True


# ---------------------------------------------------------------------------
# T098 — a declaração expressa
# ---------------------------------------------------------------------------


def test_sem_janela_computavel_a_declaracao_e_exigida_e_gravada(peca):
    """Ela responde por quem afirma o que a máquina não pode verificar (FR-085, SC-018)."""
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-declaracao",
    )

    with pytest.raises(DomainError) as recusa:
        publicar(peca, "DEFINITIVA", chave="definitiva-sem-declaracao", declaracao="")
    assert recusa.value.code == DECLARACAO_EXIGIDA

    publicada = publicar(
        peca, "DEFINITIVA", chave="definitiva-com-declaracao", declaracao=DECLARACAO
    )

    assert publicada.prazo_encerrado_fundamento == DECLARACAO
    assert publicada.prazo_encerrado_declarado_por != ""
    assert publicada.prazo_encerrado_declarado_em is not None


def test_a_preliminar_nao_exige_nem_grava_declaracao(peca):
    """O preliminar não afirma que o prazo acabou: a declaração ali não tem objeto.

    A publicação preliminar do cenário nasceu **sem** declaração, e é ela que se lê aqui — publicar
    outra do mesmo ato e da mesma natureza é duplicidade, e o banco a recusa com razão.
    """
    publicada = peca["publicacao"]

    assert publicada.natureza == "PRELIMINAR"
    assert publicada.prazo_encerrado_fundamento == ""
    assert publicada.prazo_encerrado_declarado_em is None
    assert publicada.prazo_encerrado_declarado_por == ""


def test_com_janela_computavel_a_declaracao_e_recusada(peca, monkeypatch):
    """Declarar o que o sistema verifica seria pedir que a pessoa respondesse pela máquina (FR-086).

    A janela estruturada é do degrau 8 e ainda não existe; o que se exercita aqui é a **regra**, com
    a leitura da declaração forçada. Quando o degrau existir, a US6 percorre o caminho real.
    """
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-janela",
    )
    monkeypatch.setattr(
        "processo_seletivo.recursos.domain.janela.janela_declarada",
        lambda **_: {"dias": 5, "unidade": "DIAS_CORRIDOS"},
    )

    with pytest.raises(DomainError) as recusa:
        publicar(peca, "DEFINITIVA", chave="definitiva-com-janela", declaracao=DECLARACAO)

    assert recusa.value.code == DECLARACAO_RECUSADA


# ---------------------------------------------------------------------------
# T099 — a publicação histórica não é tocada
# ---------------------------------------------------------------------------


def test_nenhuma_publicacao_anterior_e_alterada(peca):
    """O que foi divulgado continua sendo o que foi divulgado (FR-091)."""
    anterior = peca["publicacao"]
    antes = (
        anterior.natureza,
        anterior.publicado_em,
        anterior.conteudo_publico_hash,
        bytes(anterior.conteudo_publico),
    )

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-historica",
    )
    publicar(peca, "DEFINITIVA", chave="definitiva-historica", declaracao=DECLARACAO)

    anterior.refresh_from_db()
    assert (
        anterior.natureza,
        anterior.publicado_em,
        anterior.conteudo_publico_hash,
        bytes(anterior.conteudo_publico),
    ) == antes
    assert PublicacaoResultado.objects.count() == 2


def _pendentes_do_marco(peca):
    from processo_seletivo.recursos.application.selectors import providencias_pendentes_do_marco

    cenario = peca["cenario"]
    marco = _marco_publicado(cenario)
    publicacoes = list(
        PublicacaoResultado.objects.filter(
            edital=cenario["edital"], marco_id=cenario["marco"]
        ).values_list("id", flat=True)
    )
    return [
        decisao.id
        for decisao in providencias_pendentes_do_marco(
            edital=cenario["edital"],
            marco_id=cenario["marco"],
            marco=marco,
            publicacoes_do_marco=publicacoes,
        )
    ]


def _marco_publicado(cenario):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    for perfil in conteudo_vigente(cenario["edital"]).get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(cenario["marco"]):
                return marco
    return {}


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


def _determinar_providencia(peca):
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato de ordenação corrigindo o critério de desempate.",
        idempotency_key="providencia-definitividade",
    )
    return decisao


def _determinar_providencia_da_outra(peca):
    """A segunda inscrição também recorre, e também obtém providência a jusante."""
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.resultados.models import ResultadoEtapa

    cenario = peca["cenario"]
    outra = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=outra, etapa_id=cenario["etapa_do_recurso"])
    segunda = interpor(
        identidade=IdentidadeDoCandidato(
            outra.identity_subject, outra.nome, outra.cpf_normalizado, "o@ex.br"
        ),
        inscricao=outra,
        resultado=alvo,
        fundamentacao="O critério de desempate aplicado não é o publicado.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="interpor-segunda-providencia",
    )
    admitir(
        actor=julgador(),
        recurso_id=segunda.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(segunda),
        idempotency_key="admitir-segunda-providencia",
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=segunda.id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato aplicando o critério publicado.",
        idempotency_key="providencia-segunda",
    )
    return decisao
