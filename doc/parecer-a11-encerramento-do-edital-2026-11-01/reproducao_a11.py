"""Reprodução do A-11 (parecer de 01/11/2026). Anexo, não é teste da suíte.

Para repetir: copie para `backend/tests/integration/convocacao/` (usa o `conftest` dali), troque os
caminhos de saída dos HTML e rode com `-s` contra PostgreSQL. Os dois casos passam e imprimem o que
foi aceito e o que foi recusado antes e depois de encerrar e de cancelar.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application.comunicar import comunicar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import acoes
from processo_seletivo.interface.relatorio_do_edital import fatos_do_edital
from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recursos import admitir, interpor
from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import (
    criar,
    levar_a,
    publicar,
)
from tests.interface.test_auditoria_passagem_da_retificacao import sessao
from tests.interface.test_portal_caminho_da_convocacao import primeira_da_fila

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GESTOR_EDITAL = Actor("gabi", "cefor", frozenset({"edital:encerrar", "edital:cancelar"}))
JULGADOR = Actor("julia", "cefor", frozenset({"recurso:julgar", "recurso:admitir"}))


def montar(gestor, api_client, manager_headers, process_payload):
    edital, _, inscricoes = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="a11"
    )
    pessoa = primeira_da_fila(edital, inscricoes)
    conv = convocar(edital, gestor, pessoa.id, idempotency_key="a11-convocar-0001")
    conv_id = getattr(conv, "id", None) or conv["id"]
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=conv_id,
        idempotency_key="a11-comunicar-0001",
        correlation_id="a11",
    )
    resultado = (
        ResultadoEtapa.vigentes.filter(inscricao__edital=edital).exclude(inscricao=pessoa).first()
    )
    alvo = resultado.inscricao
    recurso = interpor(
        inscricao=alvo, versao=effective_version(edital_id=edital.id), resultado=resultado
    )
    admitir(recurso)
    rascunho = Inscricao.objects.create(
        created_at=timezone.now(),
        identity_subject="cpf:11144477735",
        edital=edital,
        profile_id=PROFILE_ID,
        nome="Candidata Rascunho",
        cpf="111.444.777-35",
        cpf_normalizado="11144477735",
        email="rascunho@exemplo.br",
    )
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    return edital, conv_id, recurso, rascunho, retificacao


def tentar(rotulo, fn):
    try:
        fn()
        print(f"  {rotulo}: ACEITO")
    except DomainError as exc:
        print(f"  {rotulo}: RECUSADO {exc.status} {exc.code} — {exc.detail}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {rotulo}: ERRO {type(exc).__name__}: {exc}")


@pytest.mark.parametrize("desfecho", ["ENCERRAR", "CANCELAR"])
def test_diagnostico(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, desfecho):
    edital, conv_id, recurso, rascunho, retificacao = montar(
        gestor, api_client, manager_headers, process_payload
    )
    print(f"\n=== {desfecho} ===")
    print("aguardando decisão (acoes):", acoes.recursos_aguardando_decisao(edital))
    fatos = fatos_do_edital(edital, agora=timezone.now())
    print("pendências 099 antes:", [(p.tipo, p.quantidade) for p in fatos.pendencias])
    print("rascunhos:", fatos.rascunhos, "período aberto:", fatos.periodo_aberto)

    cliente = sessao("gabi.gestora", ["gestor"])
    acao = "encerrar" if desfecho == "ENCERRAR" else "cancelar"
    pagina = cliente.get(reverse("interface:ato", args=[edital.id, acao]))
    print("tela GET:", pagina.status_code, "recusa_certa:", pagina.context["recusa_certa"])
    html = pagina.content.decode()
    inicio = html.find("<h1>")
    fim = html.find("</form>")
    with open(f"/tmp/a11_{acao}.html", "w") as f:
        f.write(html)
    print("pendencias na tela:", pagina.context["pendencias"])
    del inicio, fim

    edital.refresh_from_db()
    comando = close_edital if desfecho == "ENCERRAR" else cancel_edital
    tentar(
        desfecho,
        lambda: comando(
            actor=GESTOR_EDITAL,
            edital_id=edital.id,
            expected_revision=edital.revision,
            reason="Etapas concluídas",
            idempotency_key=f"a11-{acao}-000000001",
            correlation_id="a11",
        ),
    )
    edital.refresh_from_db()
    print("status:", edital.status)

    print("depois:")
    tentar(
        "julgar recurso admitido (INDEFERIDO)",
        lambda: julgar(
            actor=JULGADOR,
            recurso_id=recurso.id,
            especie="INDEFERIDO",
            motivacao="Sem razão.",
            idempotency_key="a11-julgar-0000001",
            correlation_id="a11",
        ),
    )
    tentar(
        "desfecho da convocação (ACEITE)",
        lambda: desfechar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=conv_id,
            especie=nomes_da_convocacao.ACEITE,
            fundamento="Manifestação registrada.",
            idempotency_key="a11-desfecho-00001",
            correlation_id="a11",
        ),
    )
    tentar("publicar Retificação homologada", lambda: publicar(retificacao, "a11-publicar-ret-0001"))
    retificacao.refresh_from_db()
    print("  retificação ficou:", retificacao.status)
    fatos = fatos_do_edital(edital, agora=timezone.now())
    print("pendências 099 depois:", [(p.tipo, p.quantidade) for p in fatos.pendencias])
    print("espécie:", fatos.especie)
    rascunho.refresh_from_db()
    print("rascunho ficou:", rascunho.status)
    detalhe = cliente.get(reverse("interface:detalhe", args=[edital.id]))
    with open(f"/tmp/a11_detalhe_{acao}.html", "w") as f:
        f.write(detalhe.content.decode())
    assert edital.status in (Edital.Status.ENCERRADO, Edital.Status.CANCELADO)
