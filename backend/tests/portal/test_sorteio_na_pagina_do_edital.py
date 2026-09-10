"""O sorteio anunciado **antes** de acontecer, na página que qualquer pessoa abre (021, FR-011).

**A promessa da feature era invisível onde precisava ser vista.** A relação de habilitados é
publicada dias antes, é imutável e é o compromisso do universo — e página nenhuma do portal a
apontava: ela só respondia no endereço da própria identidade. Quem se inscreveu não descobria que
participava de um sorteio, com que número, nem que a lista já estava fechada.

A garantia que a `021` existe para produzir — *o universo foi comprometido antes de a semente
existir* — era observável só **depois** do fato, pela divulgação do resultado, e apenas por quem já
tivesse o endereço. Provar depois e não contar antes é a diferença entre um sistema que prova e um
que convence.
"""

import pytest
from django.urls import reverse

from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _congelar(certame, *, chave="portal-sorteio-relacao"):
    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key=chave,
        correlation_id="teste-portal",
    )
    return RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])


def _sortear(certame, relacao):
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="portal-sorteio-ocorrencia",
        correlation_id="teste-portal",
    )
    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=str(relacao.id),
        ocorrencia_id=ocorrencia["ocorrencia"],
        idempotency_key="portal-sorteio-ato",
        correlation_id="teste-portal",
    )
    return Sorteio.objects.get(pk=declarado["sorteio"])


def _pagina(client, certame):
    resposta = client.get(reverse("portal:selecao", args=[certame["edital"].id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_sem_relacao_publicada_a_pagina_nao_inventa_bloco_de_sorteio(client, certame):
    """A mesma regra do Cronograma: bloco vazio afirmaria uma omissão que não existe (FR-128)."""
    assert "Sorteio público" not in _pagina(client, certame)


def test_publicada_a_relacao_a_pagina_diz_que_o_sorteio_esta_por_vir(client, certame):
    relacao = _congelar(certame)

    corpo = _pagina(client, certame)

    assert "Sorteio público" in corpo
    assert "Aguardando o sorteio" in corpo
    # **A frase que o cidadão precisa ler**, e que só o sistema pode afirmar: a lista fechou antes.
    assert "antes de existirem os números" in corpo
    assert f"{relacao.quantidade} candidatos habilitados" in corpo
    assert reverse("portal:relacao-de-habilitados", args=[relacao.id]) in corpo


def test_a_tabela_de_participantes_nao_vem_para_esta_pagina(client, certame):
    """O endereço estável da relação é onde ela vive — e é o que manifesto e ofício citam.

    Reproduzir 327 nomes no meio da página do Edital seria duplicar o artefato e poluir a leitura
    de quem veio decidir se participa.
    """
    relacao = _congelar(certame)
    corpo = _pagina(client, certame)

    for participante in relacao.participantes.select_related("inscricao"):
        assert participante.inscricao.nome not in corpo


def test_realizado_o_sorteio_a_pagina_muda_de_frase_e_abre_a_verificacao(client, certame):
    relacao = _congelar(certame)
    sorteio = _sortear(certame, relacao)

    corpo = _pagina(client, certame)

    assert "Sorteio realizado" in corpo
    assert "Aguardando o sorteio" not in corpo
    assert reverse("portal:verificar-sorteio", args=[sorteio.id]) in corpo
    # A relação continua alcançável depois: é dela que o resumo se recalcula (R-015).
    assert reverse("portal:relacao-de-habilitados", args=[relacao.id]) in corpo


def test_a_relacao_sucedida_nao_e_anunciada_como_atual(client, certame):
    """Só o vigente aparece: a sucedida continua no endereço dela, dizendo que foi sucedida."""
    primeira = _congelar(certame)
    segunda = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="portal-relacao-nova",
        correlation_id="teste-portal",
        motivo="Resultado de origem sucedido.",
    )

    corpo = _pagina(client, certame)

    assert reverse("portal:relacao-de-habilitados", args=[segunda["relacao"]]) in corpo
    assert reverse("portal:relacao-de-habilitados", args=[primeira.id]) not in corpo


def test_o_bloco_custa_duas_consultas_e_nao_uma_por_recorte(client, certame):
    """Derivada zero, que é a regra que a `024` fixou para esta página.

    Duas consultas — as relações vigentes do Edital e os sorteios vigentes dele —, casadas em
    memória pelo recorte. Um certame com três listas, ou com sete polos, custa exatamente o mesmo:
    o que cresce é o tamanho do resultado, e não o número de idas ao banco.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    _congelar(certame)
    endereco = reverse("portal:selecao", args=[certame["edital"].id])

    with CaptureQueriesContext(connection) as consultas:
        client.get(endereco)

    do_sorteio = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "sorteios_relacaodehabilitados" in consulta["sql"]
        or "sorteios_sorteio" in consulta["sql"]
    ]

    assert len(do_sorteio) == 2, do_sorteio
