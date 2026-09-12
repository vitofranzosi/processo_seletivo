"""As três ordens do marco são divulgadas, e suceder uma não arrasta as outras (021, FR-068).

**A tarefa existia e o agregado a recusava.** A `021` fez o ato admitir três raízes por marco e a
publicação continuava única por `(Edital, Perfil, marco)`: o certame com cotas sorteava e não
divulgava. Este arquivo exercita o caminho inteiro — pelo comando de publicação, e não pelo ORM —,
que é o que prova que a dimensão atravessou de fato.
"""

from unittest.mock import patch

import pytest

from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
    publicar_resultado,
)
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import Sorteio
from tests.fixtures.divulgacao import ator_publicador
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, METODO, certame_com_cotas, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def sorteadas(gestor, api_client, manager_headers, process_payload):
    """As três listas sorteadas: relações congeladas primeiro, semente depois, atos por fim."""
    certame = certame_com_cotas(gestor, api_client, manager_headers, process_payload)
    relacoes = {
        lista: publicar_relacao(
            actor=presidente(),
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=certame["perfil"],
            marco_id=certame["marco"],
            lista_id=lista,
            idempotency_key=f"pub-relacao-{indice}",
            correlation_id="teste-021",
        )["relacao"]
        for indice, lista in enumerate((None, LISTA_PPI, LISTA_PCD))
    }
    ocorrencia_id = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="pub-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]
    sorteios = {
        lista: Sorteio.objects.get(
            pk=constituir_sorteio(
                actor=presidente(),
                processo_id=certame["processo"].id,
                edital_id=certame["edital"].id,
                relacao_id=relacao_id,
                ocorrencia_id=ocorrencia_id,
                idempotency_key=f"pub-sorteio-{indice}",
                correlation_id="teste-021",
            )["sorteio"]
        )
        for indice, (lista, relacao_id) in enumerate(relacoes.items())
    }
    return certame, sorteios


def _publicar(certame, sorteio, *, chave, natureza="PRELIMINAR"):
    projecao = compor(sorteio.ato)
    anterior = vigente_do_marco(
        edital=certame["edital"], marco_id=sorteio.marco_id, lista_id=sorteio.lista_id
    )
    return publicar_resultado(
        actor=ator_publicador(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        marco_id=sorteio.marco_id,
        ato_id=sorteio.ato_id,
        natureza=natureza,
        autoridade="diretoria-cefor",
        confirmacao_da_previa=assinatura_da_previa(
            ato=sorteio.ato, publicacao_anterior=anterior, projecao=projecao
        ),
        idempotency_key=chave,
        correlation_id="teste-021",
        # **Sem declaração expressa**: o marco declara prazo computável, e onde há prazo o sistema
        # verifica. Pedir a declaração ali seria pedir à pessoa que respondesse pelo que a máquina
        # sabe — e o comando a recusa, corretamente (018, FR-085).
        declaracao_de_encerramento="",
    )


def test_as_tres_ordens_sao_publicadas_cada_uma_citando_o_seu_ato(sorteadas):
    certame, sorteios = sorteadas

    publicadas = {
        lista: _publicar(certame, sorteio, chave=f"publicar-{indice}")
        for indice, (lista, sorteio) in enumerate(sorteios.items())
    }

    assert len({p.id for p in publicadas.values()}) == 3
    for lista, publicacao in publicadas.items():
        assert publicacao.ato_id == sorteios[lista].ato_id
        assert (str(publicacao.lista_id) if publicacao.lista_id else None) == lista


def test_cada_lista_tem_a_sua_vigente(sorteadas):
    certame, sorteios = sorteadas
    for indice, sorteio in enumerate(sorteios.values()):
        _publicar(certame, sorteio, chave=f"vigente-{indice}")

    for sorteio in sorteios.values():
        vigente = vigente_do_marco(
            edital=certame["edital"], marco_id=sorteio.marco_id, lista_id=sorteio.lista_id
        )
        assert vigente is not None
        assert vigente.ato_id == sorteio.ato_id


def test_o_documento_publicado_identifica_a_lista(sorteadas):
    """FR-045: a ordem publicada diz de qual lista ela é."""
    certame, sorteios = sorteadas

    publicacao = _publicar(certame, sorteios[LISTA_PPI], chave="documento-ppi")

    import json

    conteudo = json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))
    assert conteudo["cabecalho"]["lista"] == "Pretos, pardos e indígenas"


def test_suceder_a_publicacao_de_uma_lista_nao_toca_as_outras(sorteadas):
    """A definitiva da PPI espera o prazo **da PPI**, e sucede só a preliminar dela.

    O marco declara janela recursal, então a definitiva só é publicável depois de ela fechar — e é
    isso que o `freeze_time` reproduz. Antes da correção do eixo, a janela consultada era a da ampla
    concorrência: sem publicação lá, ela não existia, e a definitiva da PPI saía na hora.
    """
    from datetime import timedelta

    from django.utils import timezone

    certame, sorteios = sorteadas
    publicadas = {
        lista: _publicar(certame, sorteio, chave=f"sucede-{indice}")
        for indice, (lista, sorteio) in enumerate(sorteios.items())
    }

    depois_do_prazo = timezone.now() + timedelta(days=6)
    with patch("django.utils.timezone.now", return_value=depois_do_prazo):
        definitiva = _publicar(
            certame, sorteios[LISTA_PPI], chave="sucede-ppi-definitiva", natureza="DEFINITIVA"
        )

    assert definitiva.publicacao_anterior_id == publicadas[LISTA_PPI].id
    for lista in (None, LISTA_PCD):
        assert not PublicacaoResultado.objects.filter(
            publicacao_anterior=publicadas[lista]
        ).exists()


def test_o_prazo_recursal_da_definitiva_e_o_da_propria_lista(sorteadas):
    """**O eixo perdia-se no último degrau** (021, D-015, FR-068).

    `_impedimento_da_definitiva` não encaminhava `lista_id`, e `_janela_aberta` procurava a
    publicação da **ampla concorrência**. Havendo só uma preliminar de PPI, a consulta devolvia
    `None`, a janela não existia, e a definitiva da PPI era liberada na hora — antes de qualquer
    prazo recursal correr.
    """
    from processo_seletivo.divulgacao.domain.publicabilidade import IMPEDIMENTO, aferir

    certame, sorteios = sorteadas
    ppi = sorteios[LISTA_PPI]
    _publicar(certame, ppi, chave="prazo-ppi-preliminar")

    afericao = aferir(
        edital=certame["edital"],
        marco_id=ppi.marco_id,
        ato=ppi.ato,
        natureza="DEFINITIVA",
        lista_id=ppi.lista_id,
    )

    assert afericao.nivel == IMPEDIMENTO, (
        "a definitiva da PPI foi liberada sem o prazo recursal da própria PPI correr"
    )


def test_a_janela_de_uma_lista_nao_e_lida_da_outra(sorteadas):
    """Sem a ampla publicada, a definitiva da PPI continua impedida pela janela dela mesma."""
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.publicabilidade import _janela_aberta

    certame, sorteios = sorteadas
    ppi = sorteios[LISTA_PPI]
    _publicar(certame, ppi, chave="janela-ppi")

    marco = {"appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}}
    da_ppi = _janela_aberta(
        edital=certame["edital"],
        marco_id=ppi.marco_id,
        marco=marco,
        at=None,
        lista_id=ppi.lista_id,
    )
    da_ampla = _janela_aberta(
        edital=certame["edital"], marco_id=ppi.marco_id, marco=marco, at=None, lista_id=None
    )

    assert da_ppi is not None, "a PPI tem publicação, logo tem janela correndo"
    assert da_ampla is None, "a ampla não tem publicação, e a janela dela não existe"
    assert vigente_do_marco(edital=certame["edital"], marco_id=ppi.marco_id) is None
