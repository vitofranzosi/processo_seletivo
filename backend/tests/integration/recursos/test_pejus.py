"""*Non reformatio in pejus* — e a linha que separa piora de deslocamento.

```text
piora    a consequência deixa de habilitar, ou a pontuação cai
não é    a posição na ordem cai porque OUTRA pessoa foi corrigida
```

**A distinção é a substância da garantia**, e confundi-la a inverteria. A posição é relativa: ela
muda quando o resultado alheio muda, e a instituição não pode deixar de corrigir o erro de A porque
isso desloca B. Tratar queda de posição como piora tornaria a vedação uma trava contra o próprio
deferimento — e, no limite, congelaria a ordem no primeiro recurso deferido (FR-070, FR-074).
"""

from decimal import Decimal

import pytest

from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """Quem recorre foi **habilitada** com 70: há o que piorar, e é o que se veda."""
    return cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=112,
        codigo="0812",
        pontuacoes=("70.0000", "90.0000"),
    )


def corrigir(peca, pontuacao, **extra):
    from processo_seletivo.recursos.application.julgar import julgar

    argumentos = {
        "actor": julgador(),
        "recurso_id": peca["recurso"].id,
        "especie": DecisaoRecurso.Especie.CORRECAO_FIXADA,
        "motivacao": "Revisão da pontuação atribuída.",
        "etapa_id": peca["cenario"]["etapa"],
        "pontuacao": pontuacao,
        "assinatura_do_resultado": str(peca["superado"].id),
        "idempotency_key": f"pejus-{pontuacao}",
    }
    return julgar(**{**argumentos, **extra})


def test_a_correcao_que_baixaria_a_pontuacao_e_recusada(peca):
    """E **nenhum** sucessor nasce — nem a decisão fica gravada sem ele (FR-070, SC-008)."""
    with pytest.raises(DomainError) as recusa:
        corrigir(peca, Decimal("65.0000"))

    assert recusa.value.code == "appeal_worsens_situation"
    assert recusa.value.status == 422
    assert not DecisaoRecurso.objects.exists()
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_a_correcao_que_eliminaria_e_recusada(peca):
    """Perder a habilitação é piora **qualquer que seja** a pontuação (FR-071).

    Fixar 40 numa Etapa de mínima 60 derrubaria quem já estava habilitada — e é o caso em que a
    vedação mais importa, porque o recurso teria custado à pessoa a própria continuidade.
    """
    with pytest.raises(DomainError) as recusa:
        corrigir(peca, Decimal("40.0000"))

    assert recusa.value.code == "appeal_worsens_situation"
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_a_correcao_que_melhora_passa(peca):
    """A prova de que a vedação não é uma trava contra o deferimento."""
    _decisao, sucessor = corrigir(peca, Decimal("85.0000"))

    assert sucessor is not None
    assert sucessor.pontuacao == Decimal("85.0000")
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.HABILITADA


def test_a_correcao_que_mantem_a_pontuacao_passa(peca):
    """Igual não é pior — e a comparação é decimal, e nunca de ponto flutuante.

    O empate exato é justamente onde o arredondamento binário decidiria errado, e é por isso que a
    igualdade tem teste próprio em vez de ficar implícita no "maior ou igual".
    """
    _decisao, sucessor = corrigir(peca, peca["superado"].pontuacao)

    assert sucessor.pontuacao == peca["superado"].pontuacao


def test_a_queda_de_posicao_por_ato_alheio_nao_e_piora(
    gestor, api_client, manager_headers, process_payload
):
    """**A posição é relativa, e a vedação não é sobre ela** (FR-072, FR-074).

    Quem recorre está em segundo com 70. A instituição corrige a terceira colocada para 95, e a
    recorrente cai para terceiro **sem que nada seu tenha mudado**. Essa queda não é piora, e
    tratá-la como tal impediria a instituição de corrigir o erro de outra pessoa — que é o
    resultado exatamente oposto ao que a garantia protege.
    """
    from processo_seletivo.classificacao.application.calculo import calcular_ordem

    cenario = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=113,
        codigo="0813",
        pontuacoes=("70.0000", "90.0000", "65.0000"),
        publicar=True,
    )
    terceira = cenario["cenario"]["inscricoes"][2]
    protegido = ResultadoEtapa.vigentes.get(
        inscricao=terceira, etapa_id=cenario["cenario"]["etapa"]
    )
    recorrente = cenario["inscricao"]

    def posicao_de(inscricao):
        ordem = calcular_ordem(
            edital=cenario["cenario"]["edital"],
            perfil_id=cenario["cenario"]["perfil"],
            marco_id=cenario["cenario"]["marco"],
        )
        return next(
            item["posicao"]
            for item in ordem["posicoes"]
            if str(item["inscricao_id"]) == str(inscricao.id)
        )

    antes = posicao_de(recorrente)

    _elevar_por_recurso(cenario, terceira, protegido, Decimal("95.0000"))

    depois = posicao_de(recorrente)
    recorrente_vigente = ResultadoEtapa.vigentes.get(
        inscricao=recorrente, etapa_id=cenario["cenario"]["etapa"]
    )
    assert depois > antes, "a queda de posição precisa ter mesmo acontecido"
    assert recorrente_vigente.pontuacao == Decimal("70.0000")
    assert recorrente_vigente.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert recorrente_vigente.resultado_anterior_id is None, "nada seu foi alterado"


def _elevar_por_recurso(cenario, inscricao, protegido, pontuacao):
    """A terceira colocada recorre e é corrigida para cima — pelo caminho real."""
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.recursos.application.julgar import julgar

    peca = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "t@ex.br"
        ),
        inscricao=inscricao,
        resultado=protegido,
        fundamentacao="A soma dos critérios está errada.",
        assinatura_do_objeto=str(protegido.pk),
        idempotency_key="interpor-terceira",
    )
    admitir(
        actor=julgador(),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado="",
        idempotency_key="admitir-terceira",
    )
    return julgar(
        actor=julgador(),
        recurso_id=peca.id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="Erro material na soma.",
        etapa_id=cenario["cenario"]["etapa"],
        pontuacao=pontuacao,
        assinatura_do_resultado=str(protegido.pk),
        idempotency_key="julgar-terceira",
    )


# ---------------------------------------------------------------------------
# T077 — a porta dos fundos: a reavaliação ordenada
# ---------------------------------------------------------------------------


def test_a_reavaliacao_pior_e_registrada_e_nao_vira_sucessor(
    gestor, api_client, manager_headers, process_payload
):
    """**A vedação alcança o caminho da reavaliação** (FR-073, SC-008).

    Sem isto, a *non reformatio* seria contornável por um caminho legítimo: bastaria deferir
    determinando reavaliação, e a nota pior entraria como Resultado sucessor sem que ninguém
    tivesse decidido piorar a situação de quem recorreu.

    **A nova Avaliação fica registrada.** Ela é o juízo do avaliador, e apagá-la seria mentir sobre
    o que ele concluiu — o que não acontece é a consolidação dela como sucessor. A recusa nomeia a
    vedação, para que quem opera não a confunda com um erro de sistema.
    """
    from processo_seletivo.avaliacoes.models import Avaliacao
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.mesa import concluir_como, distribuir_para

    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=118,
        codigo="0818",
        pontuacoes=("70.0000", "90.0000"),
    )
    cenario = peca["cenario"]
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        etapa_id=cenario["etapa"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-pejus",
    )

    outra = _outro_avaliador(cenario)
    distribuir_para(cenario, _gestor(), [outra], [peca["inscricao"]], chave="lote-pejus")
    concluir_como(cenario, outra, peca["inscricao"], pontuacao="61.0000")

    declarado = consolidar(
        actor=_gestor(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[peca["inscricao"].id],
        idempotency_key="consolidar-pejus",
        correlation_id="pejus",
    )

    assert declarado["feitas"] == 0
    assert declarado["recusadas"] == 1
    assert "não pode agravar" in " ".join(item["motivo"] for item in declarado["motivos"])
    # A avaliação **existe**: o que não existe é o sucessor pior.
    assert Avaliacao.objects.filter(
        inscricao_id=peca["inscricao"].id, concluida_por=outra, pontuacao=Decimal("61.0000")
    ).exists()
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()
    vigente = ResultadoEtapa.vigentes.get(inscricao=peca["inscricao"], etapa_id=cenario["etapa"])
    assert vigente.pk == peca["superado"].pk
    assert vigente.pontuacao == Decimal("70.0000")


def _gestor():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")


def _outro_avaliador(cenario):
    from processo_seletivo.comissoes.models import Funcao
    from tests.fixtures.comissao import alocar_em, constituir

    membros = constituir(
        _gestor(), cenario["processo"], [("ana", Funcao.MEMBRO)], prefixo="pejus-us5"
    )
    cenario["membros"]["ana"] = membros["ana"]
    alocar_em(
        _gestor(),
        cenario["processo"],
        membros["ana"],
        cenario["edital"],
        cenario["etapa"],
        chave="aloc-pejus-us5",
    )
    return "ana"
