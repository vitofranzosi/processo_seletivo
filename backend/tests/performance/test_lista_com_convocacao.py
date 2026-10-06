"""O custo de "Minhas inscrições" quando a lista passa a falar de convocação (059, `SC-426`).

**A lista ganhou uma leitura, e ela precisa ser uma só.** Mostrar a convocação de cada item é o
desenho exato do defeito que `test_area_do_candidato.py` existe para pegar: uma consulta por
inscrição, invisível com três e fatal com trezentas. O seletor lê por conjunto; este arquivo prova
que a **tela** também — porque um `desfecho_de` chamado no laço sem o prefetch certo desfaria o
seletor sem que o teste dele visse.

**E o requerimento continua fora da lista.** A `029` decidiu que o estado dele se lê na tela dele, e
prende o zero em `test_orcamento_de_consulta.py`; o caso que aquele teste não cobria é o de quem
**tem** convocação, que é justamente quem esta feature faz a lista mostrar.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="portal-059-custo"
    )


def convocada(cenario, gestor):
    edital, _, inscricoes = cenario
    alvo = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]
    convocar(edital, gestor, alvo, idempotency_key="custo-1")
    return next(i for i in inscricoes if i.id == alvo)


def entrar(client, subject):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def medir(client):
    """Duas cargas, e só a segunda contada: a primeira aquece o cache do conteúdo publicado."""
    url = reverse("portal:inscricoes")
    client.get(url)
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(url)
    assert resposta.status_code == 200
    return capturadas


def test_a_lista_le_a_convocacao_numa_consulta_so(client, cenario, gestor):
    """**Uma** consulta à tabela das convocações, com `IN`, e as duas dos prefetches — e só.

    O seletor já prova que o custo dele não cresce com as inscrições nem com as convocações
    (`tests/integration/convocacao/test_vigentes_por_inscricao.py`). O que resta provar é que a
    tela não desfaz isso: um `desfecho_de` sem o prefetch, chamado no laço dos itens, seria uma
    consulta por item — e apareceria aqui como uma segunda leitura de `convocacao_`.
    """
    pessoa = convocada(cenario, gestor)
    entrar(client, pessoa.identity_subject)

    capturadas = medir(client)
    da_convocacao = [c["sql"] for c in capturadas if '"convocacao_' in c["sql"]]

    assert "Convocação aberta" in client.get(reverse("portal:inscricoes")).content.decode()
    assert len(da_convocacao) == 3, da_convocacao
    principal = [sql for sql in da_convocacao if 'FROM "convocacao_convocacao"' in sql]
    assert len(principal) == 1 and " IN (" in principal[0], principal


def test_a_lista_de_quem_foi_convocado_nao_toca_o_requerimento(client, cenario, gestor):
    """O zero da `029` vale também para quem tem convocação — e é dela que a lista agora fala."""
    pessoa = convocada(cenario, gestor)
    entrar(client, pessoa.identity_subject)

    capturadas = medir(client)

    assert [c["sql"] for c in capturadas if "requerimentos_" in c["sql"]] == []
    assert any("convocacao_" in c["sql"] for c in capturadas), (
        "a medição precisa enxergar a leitura da convocação, ou o zero acima não diz nada"
    )
