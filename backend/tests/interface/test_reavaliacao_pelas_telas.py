"""A reavaliação determinada se cumpre pelas telas — julgar, distribuir, avaliar e consolidar.

**Por que pelas telas, se o domínio já tem teste.** O percurso de 07/09 (E2E18-001) concluiu que a
reavaliação era inexequível: tentou reabrir a avaliação original, recebeu a recusa — correta por
regra — e não achou outro caminho. O caminho existia (`test_reavaliacao.py` o prova pelas funções
de aplicação), mas nenhum teste o percorria pelas views, e foi justamente aí que ele se perdeu. A
auditoria de consolidação de 26/09 o manteve como "implementado, mas não validado" (RC-63), e este
arquivo é a validação que ficou.

Cada passo usa a view que a pessoa usa, com o papel dela: quem julga, quem organiza a Etapa, a
avaliadora e, de novo, quem organiza. O que se afirma é o desfecho da FR-067 e da FR-068 — a
pendência nomeada, a distribuição a avaliador diverso aceita, e o Resultado sucessor citando a
decisão.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.recursos_us4 import JULGADORA, cenario_julgavel
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _avaliadora_diversa(cenario):
    """Quem concluiu a original não reavalia (FR-068); a Etapa precisa de outra pessoa alocada."""
    from processo_seletivo.comissoes.models import Funcao
    from tests.conftest import ator_institucional
    from tests.fixtures.comissao import alocar_em, constituir

    gestor = ator_institucional("carlos", "comissao:gerir")
    membros = constituir(
        gestor, cenario["processo"], [("ana", Funcao.MEMBRO)], prefixo="reav-telas"
    )
    alocar_em(
        gestor,
        cenario["processo"],
        membros["ana"],
        cenario["edital"],
        cenario["etapa"],
        chave="aloc-reav-telas",
    )
    return membros["ana"]


def _campo(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def test_a_reavaliacao_determinada_se_cumpre_pelas_telas(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=164, codigo="0864"
    )
    cenario = peca["cenario"]
    edital, etapa, inscricao = cenario["edital"], cenario["etapa"], peca["inscricao"]
    organizacao = reverse("interface:distribuicao", args=[edital.id, etapa])

    # 1. Quem julga determina a reavaliação pela tela do recurso.
    identificar(client, JULGADORA, ["julgador"])
    julgado = client.post(
        reverse("interface:recurso-julgar", args=[peca["recurso"].id]),
        {
            "especie": "REAVALIACAO_DETERMINADA",
            "motivacao": "Reavalie-se a prova didática por avaliador diverso.",
            "etapa": f"{etapa}|{peca['superado'].id}",
        },
    )
    assert julgado.status_code == 302
    decisao = DecisaoRecurso.objects.get(recurso=peca["recurso"])

    # 2. A organização da Etapa nomeia a pendência, e não a dá por consolidada (FR-067).
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(organizacao).content.decode()
    assert "reavaliação determinada por recurso, ainda não cumprida" in corpo

    # 3. A distribuição aceita avaliadora diversa, apesar de o teto da Etapa já estar ocupado.
    ana = _avaliadora_diversa(cenario)
    distribuido = client.post(
        organizacao,
        {
            "acao": "distribuir",
            "membro_id": [str(ana.id)],
            "inscricao_id": [str(inscricao.id)],
            "chave_idempotencia": "reav-telas-distribuir",
        },
    )
    assert distribuido.status_code == 302
    assert Atribuicao.objects.filter(inscricao=inscricao, etapa_id=etapa, membro=ana).exists()

    # 4. A avaliadora conclui pela Mesa.
    identificar(client, "ana", [])
    mesa = client.get(reverse("interface:mesa-inscricao", args=[edital.id, etapa, inscricao.id]))
    assert mesa.status_code == 200
    pagina = mesa.content.decode()
    concluido = client.post(
        reverse("interface:mesa-avaliacao-concluir", args=[edital.id, etapa, inscricao.id]),
        {
            "pontuacao": "88",
            "parecer": "Reavaliada a prova didática: atende.",
            "expected_revision": _campo(pagina, "expected_revision"),
            "versao_reconhecida": _campo(pagina, "versao_reconhecida"),
        },
    )
    assert concluido.status_code == 302

    # 5. Quem organiza consolida — pela seleção, com a conferência de dois passos.
    identificar(client, "carlos", ["gestor"])
    consolidar = reverse("interface:consolidar-resultados", args=[edital.id, etapa])
    conferencia = client.post(consolidar, {"inscricao_id": [str(inscricao.id)]})
    assert conferencia.status_code == 200
    previa = conferencia.content.decode()
    assert "em cumprimento de decisão" in previa
    confirmado = client.post(
        consolidar,
        {
            "confirmar": "1",
            "chave_idempotencia": _campo(previa, "chave_idempotencia"),
            "inscricoes": _campo(previa, "inscricoes"),
        },
    )
    assert confirmado.status_code == 302

    # O desfecho da FR-068: o sucessor cita a decisão e supera o Resultado atacado.
    vigente = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=etapa)
    assert vigente.resultado_anterior_id == peca["superado"].id
    assert vigente.decisao_id == decisao.id
    assert vigente.consequencia == ResultadoEtapa.Consequencia.HABILITADA
