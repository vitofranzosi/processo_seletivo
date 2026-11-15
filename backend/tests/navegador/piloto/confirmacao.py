"""Os estados da confirmação de ato do Edital (172, D-004, C-01 a C-13).

Os sete atos que `confirmar.html` serve, montados pelos mesmos caminhos dos testes de tela: o
rascunho composto pela interface (`compor_rascunho`, da `test_fluxo`) quando o estado depende do
que o Edital declara, e a API quando só importa chegar à situação (`_ate_homologado`, da `060`).

**C-12 se desdobrou em dois** (C-12 e C-13). A D-004 da spec juntava num código a recusa do
envio e a tela de quem não tem a permissão, e são duas páginas: uma fotografia é de uma página. O
catálogo tem, por isso, 64 estados, e não 63.

**O cronograma tem data no futuro onde a falta de pendência importa** (C-01): as fixtures da suíte
trazem a inscrição em setembro e outubro de 2026, e desde que essas datas passaram toda confirmação
de submeter e de publicar mostra também a atenção "já passou". O C-02, que quer a atenção, usa a
data das fixtures.
"""

from django.test import Client
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_fluxo import EVENTOS, MARCOS, PERFIS, praticar
from tests.navegador.piloto.estados import Montagem, estado

EVENTOS_FUTUROS = {**EVENTOS, "evento-0-startAt": "2027-10-01T09:00"}


def _ato(edital, acao):
    return reverse("interface:ato", args=[edital.id, acao])


def _sessao(request, subject, papeis):
    request.getfixturevalue("seletor_ligado")
    cliente = Client()
    identificar(cliente, subject, papeis)
    return cliente


def _api(request):
    return (
        request.getfixturevalue("api_client"),
        request.getfixturevalue("manager_headers"),
        request.getfixturevalue("process_payload"),
    )


def _em_elaboracao(request, *, eventos=EVENTOS, marcos=MARCOS):
    """O Edital do `process_payload`, composto pela tela por quem elabora."""
    api_client, manager_headers, process_payload = _api(request)
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    ana = _sessao(request, "ana.elaboradora", ["elaborador"])
    if marcos is None:
        compor_rascunho(ana, edital, PERFIS, eventos)
    else:
        compor_rascunho(ana, edital, PERFIS, eventos, marcos=marcos)
    return edital, ana


def _submetido(request):
    edital, ana = _em_elaboracao(request)
    resposta, _ = praticar(ana, Edital.objects.get(), "submeter")
    assert resposta.status_code == 302, resposta.content
    return Edital.objects.get()


def _homologado(request):
    from tests.interface.test_escolha_da_autoridade import _ate_homologado

    return _ate_homologado(*_api(request))


def _publicado(request):
    from tests.fixtures.publicacao import publish_original

    return publish_original(*_api(request))


@estado(
    "C-01",
    tela="confirmacao",
    papel="quem elabora",
    prova="aguardando quem homologa",
    acao_principal="Confirmar: Submeter para revisão",
)
def submeter_sem_pendencia(request):
    edital, ana = _em_elaboracao(request, eventos=EVENTOS_FUTUROS)
    return Montagem(_ato(edital, "submeter"), ana)


@estado("C-02", tela="confirmacao", papel="quem elabora", prova="Impedimento:")
def submeter_com_impedimento_e_atencao(request):
    # Sem o marco, o Perfil não classifica ninguém e a submissão é recusada (FR-457 da 032); a
    # inscrição de outubro de 2026, que já passou, dá a atenção.
    edital, ana = _em_elaboracao(request, marcos=None)
    return Montagem(_ato(edital, "submeter"), ana)


@estado(
    "C-03",
    tela="confirmacao",
    papel="quem elaborou e homologa",
    prova="Depois de homologar, você não poderá publicar esta revisão",
    acao_principal="Confirmar: Homologar",
)
def homologar_por_quem_elaborou(request):
    # Quem submeteu é quem abre a homologação: a mesma pessoa, agora com o papel de homologar.
    edital = _submetido(request)
    return Montagem(_ato(edital, "homologar"), _sessao(request, "ana.elaboradora", ["homologador"]))


@estado(
    "C-04",
    tela="confirmacao",
    papel="quem homologa",
    prova="Motivo da revogação",
    acao_principal="Confirmar: Revogar homologação",
)
def revogar_homologacao(request):
    edital = _homologado(request)
    return Montagem(_ato(edital, "revogar-homologacao"), _sessao(request, "bruno", ["homologador"]))


@estado(
    "C-05",
    tela="confirmacao",
    papel="quem homologa",
    prova="aguardando quem elabora",
    acao_principal="Confirmar: Devolver para elaboração",
)
def devolver(request):
    edital = _submetido(request)
    return Montagem(
        _ato(edital, "devolver"), _sessao(request, "bruno.homologador", ["homologador"])
    )


@estado(
    "C-06",
    tela="confirmacao",
    papel="quem publica",
    prova="Quem responde institucionalmente por este Edital",
    acao_principal="Confirmar: Publicar",
)
def publicar(request):
    edital = _homologado(request)
    return Montagem(_ato(edital, "publicar"), _sessao(request, "carla", ["publicador"]))


@estado(
    "C-07",
    tela="confirmacao",
    papel="quem elaborou, homologou e publica",
    prova="Segregação de funções.",
)
def publicar_impedido_por_segregacao(request):
    api_client, manager_headers, process_payload = _api(request)
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    joao = _sessao(request, "joao.sozinho", ["elaborador", "homologador", "publicador"])
    compor_rascunho(joao, edital, PERFIS, EVENTOS, marcos=MARCOS)
    praticar(joao, Edital.objects.get(), "submeter")
    praticar(joao, Edital.objects.get(), "homologar", motivo="OK")
    return Montagem(_ato(edital, "publicar"), joao)


@estado("C-08", tela="confirmacao", papel="quem publica", prova="Nenhuma autoridade vigente para")
def publicar_sem_autoridade(request):
    from datetime import timedelta

    from django.utils import timezone

    from processo_seletivo.unidades.models import AutoridadeHabilitada

    edital = _homologado(request)
    AutoridadeHabilitada.objects.filter(unidade__codigo="cefor").update(
        fim_vigencia=timezone.localdate() - timedelta(days=1),
        encerrada_em=timezone.now(),
        encerrada_por="piloto",
    )
    return Montagem(_ato(edital, "publicar"), _sessao(request, "carla", ["publicador"]))


@estado("C-09", tela="confirmacao", papel="quem encerra", prova="Antes de encerrar, resolva")
def encerrar_com_impedimento_e_atencao(request):
    from processo_seletivo.publicacoes.models_retificacao import Retificacao
    from tests.fixtures.recursos_us4 import cenario_julgavel
    from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
    from tests.unit.processos.test_pendencias_do_edital import criar

    api_client, manager_headers, process_payload = _api(request)
    peca = cenario_julgavel(
        request.getfixturevalue("gestor"),
        api_client,
        manager_headers,
        process_payload,
        seed=161,
        codigo="1161",
    )
    edital = peca["cenario"]["edital"]
    # O recurso que aguarda julgamento impede; a Retificação em revisão continua depois, e é a
    # atenção (113).
    levar_a(criar(api_client, edital), Retificacao.Status.EM_REVISAO)
    return Montagem(_ato(edital, "encerrar"), _sessao(request, "gabi.gestora", ["gestor"]))


@estado(
    "C-10",
    tela="confirmacao",
    papel="quem encerra",
    prova="Nenhuma pendência registrada no GPS impede o encerramento.",
    acao_principal="Confirmar: Encerrar",
)
def encerrar_sem_impedimento(request):
    edital = _publicado(request)
    return Montagem(_ato(edital, "encerrar"), _sessao(request, "gabi.gestora", ["gestor"]))


@estado(
    "C-11",
    tela="confirmacao",
    papel="quem cancela",
    prova="Confirmar: Cancelar",
    acao_principal="Confirmar: Cancelar",
)
def cancelar(request):
    edital = _publicado(request)
    return Montagem(_ato(edital, "cancelar"), _sessao(request, "gustavo.gestor", ["gestor"]))


@estado("C-12", tela="confirmacao", papel="quem homologa", prova="Não foi possível concluir:")
def recusa_do_envio(request):
    edital = _submetido(request)

    def motivo_em_branco(pagina):
        # Espaços passam pelo `required` do navegador e são recusados pelo servidor, que reexibe a
        # tela com a recusa e o foco nela.
        pagina.fill("#motivo", "   ")
        pagina.get_by_role("button", name="Confirmar: Homologar").click()

    return Montagem(
        _ato(edital, "homologar"),
        _sessao(request, "bruno.homologador", ["homologador"]),
        gesto=motivo_em_branco,
    )


@estado(
    "C-13",
    tela="confirmacao",
    papel="quem não tem a permissão",
    prova="Você não pode praticar este ato.",
)
def sem_permissao(request):
    edital = _publicado(request)
    return Montagem(_ato(edital, "encerrar"), _sessao(request, "julia.julgadora", ["julgador"]))
