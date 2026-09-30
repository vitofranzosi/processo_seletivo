"""FR-020: o preenchimento sobrevive à expiração de sessão e à queda de conexão.

A preservação que já existia atua quando o domínio recusa, o que pressupõe a requisição ter
chegado. Nos dois casos que o requisito nomeia ela não chega, e sem armazenamento no navegador
o conteúdo se perde.

O comportamento em si é JavaScript e exige navegador — está verificado manualmente e descrito
em quickstart.md. O que dá para prender aqui é o contrato entre o template e o script — sem
estes atributos ele não tem como saber o que guardar nem sob que chave — e a metade da
restauração que é do servidor (RC-08).
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.interface import forms
from processo_seletivo.processos.models import Edital
from tests.interface.conftest import identificar

ETAPAS = [
    ("perfis", "#perfis"),
    ("cronograma", "#eventos"),
    # A etapa de cartões mais longos, que ficou sem ele até a vista do conjunto (053, FR-979).
    ("classificacao", "#classificacao-perfis"),
]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def corpo_da_etapa(client, edital, etapa):
    return client.get(reverse("interface:compor-etapa", args=[edital.id, etapa])).content.decode()


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(("etapa", "lista"), ETAPAS)
def test_formulario_declara_o_que_o_rascunho_local_precisa(
    client, seletor_ligado, edital, etapa, lista
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = corpo_da_etapa(client, edital, etapa)

    assert f'data-rascunho="{edital.id}:{etapa}:ana.elaboradora"' in corpo
    assert f'data-lista="{lista}"' in corpo
    # O fragmento vazio da linha deixou de ser declarado: era por ele que a restauração remontava
    # a tela no navegador, e perdia o que era aninhado (RC-08).
    assert "data-fragmento=" not in corpo
    assert "interface/rascunho.js" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_a_chave_do_rascunho_separa_pessoas_no_mesmo_navegador(client, seletor_ligado, edital):
    """Sem a pessoa na chave, quem usar o mesmo computador depois veria o rascunho alheio."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    da_ana = corpo_da_etapa(client, edital, "perfis")
    identificar(client, "bruno.homologador", ["elaborador"])
    do_bruno = corpo_da_etapa(client, edital, "perfis")

    chave = re.compile(r'data-rascunho="([^"]+)"')
    assert chave.search(da_ana).group(1) != chave.search(do_bruno).group(1)


@pytest.mark.django_db
@pytest.mark.integration
def test_marcador_de_nao_enviado_nasce_oculto(client, seletor_ligado, edital):
    """O HTML recém-renderizado é, por definição, o que o servidor tem."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = corpo_da_etapa(client, edital, "perfis")

    marcador = re.search(r"<span[^>]*data-nao-enviado[^>]*>", corpo)
    assert marcador, "a tela precisa distinguir o enviado do que só existe no navegador"
    assert "hidden" in marcador.group(0)


@pytest.mark.django_db
@pytest.mark.integration
def test_tela_somente_leitura_nao_guarda_rascunho(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Sem permissão de elaborar não há o que enviar, e guardar seria acumular sem propósito."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    identificar(client, "iris.auditora", ["auditor"])

    assert "data-rascunho=" not in corpo_da_etapa(client, edital, "perfis")


@pytest.mark.django_db
@pytest.mark.integration
def test_o_salvamento_devolve_o_recibo_da_etapa_gravada(client, seletor_ligado, edital):
    """A outra metade do contrato: o servidor diz **o que** recebeu, e não só que recebeu.

    Sem o recibo, o script comparava o digitado com o reexibido — que o servidor normaliza — e
    concluía que divergiam, anunciando "há preenchimento não enviado" na mesma tela em que
    imprimia "Rascunho salvo". Duas frases contraditórias sobre o mesmo ato.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(
        f"{reverse('interface:compor-etapa', args=[edital.id, 'perfis'])}?salvo=perfis"
    )
    corpo = resposta.content.decode()

    assert "Rascunho salvo — Perfis de Vaga." in corpo
    assert f'data-rascunho-salvo="{edital.id}:perfis:ana.elaboradora"' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_o_recibo_nomeia_a_etapa_gravada_e_nao_a_exibida(client, seletor_ligado, edital):
    """ "Avançar" grava uma etapa e abre a seguinte — o recibo fala da que foi gravada."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        f"{reverse('interface:compor-etapa', args=[edital.id, 'cronograma'])}?salvo=perfis"
    ).content.decode()

    assert f'data-rascunho-salvo="{edital.id}:perfis:ana.elaboradora"' in corpo
    assert f'data-rascunho="{edital.id}:cronograma:ana.elaboradora"' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_salvamento_nao_ha_recibo(client, seletor_ligado, edital):
    """Abrir a tela não é ter gravado: um recibo aqui apagaria preenchimento não enviado."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    assert "data-rascunho-salvo=" not in corpo_da_etapa(client, edital, "perfis")


def test_a_expiracao_do_rascunho_e_verificada_executando_o_script():
    """FR-022: o prazo e o descarte estão em tests/javascript/rascunho.test.js.

    Procurar a constante no fonte provava que ela foi escrita, não que o rascunho velho é
    descartado. O ponteiro fica aqui para que quem procurar a cobertura do requisito a encontre.
    """
    from pathlib import Path

    suite = Path(__file__).resolve().parents[1] / "javascript/rascunho.test.js"

    assert suite.exists()
    assert "mais velho que um dia é descartado" in suite.read_text(encoding="utf-8")


# RC-08 da auditoria de consolidação (AX-16 de 15/09). A restauração remontava cada linha no
# navegador a partir do fragmento **vazio** do Perfil, e o que era aninhado — Modalidade, fato,
# linha do quadro, marcos em trânsito — não tinha onde cair: voltava o Perfil, sumia o resto, e o
# autosave regravava a perda por cima do guardado. Agora quem remonta é o servidor, pelo mesmo
# caminho que já devolve o digitado depois de uma recusa (`_ler_etapa` → `_reexibir_*`).
PERFIL, MODALIDADE, FATO = "7", "7-31", "7-52"
RESTAURACAO = {
    "restaurar": "1",
    f"perfil-{PERFIL}-id": "d20e685c-6634-46fe-a30e-142d76cc753e",
    f"perfil-{PERFIL}-code": "LP99",
    f"perfil-{PERFIL}-name": "Professor de Libras",
    f"perfil-{PERFIL}-immediateVacancies": "2",
    f"perfil-{PERFIL}-reserveType": "NONE",
    f"modalidade-{MODALIDADE}-id": "f6435940-e29a-4a7d-975f-3c579e978fe9",
    f"modalidade-{MODALIDADE}-ruleId": "8c91e610-6a5d-4688-8bb4-93d13f9a214f",
    f"modalidade-{MODALIDADE}-code": "PPIQ",
    f"modalidade-{MODALIDADE}-name": "Pretos, pardos, indígenas e quilombolas",
    f"modalidade-{MODALIDADE}-percentage": "30",
    f"fato-{FATO}-id": "0b7f1c0e-4d2a-4f3e-9a51-2c6d8e9f0a1b",
    f"fato-{FATO}-code": "NASCIMENTO",
    f"fato-{FATO}-label": "Data de nascimento",
    f"fato-{FATO}-type": "DATA",
}


def restaurar(client, edital, dados=RESTAURACAO, etapa="perfis"):
    return client.post(reverse("interface:compor-etapa", args=[edital.id, etapa]), dados)


@pytest.mark.django_db
@pytest.mark.integration
def test_restaurar_devolve_as_colecoes_aninhadas(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = restaurar(client, edital)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert 'value="LP99"' in corpo
    # O que se perdia: os três segmentos depois do prefixo, que a restauração no navegador não
    # sabia onde pôr.
    assert 'value="PPIQ"' in corpo
    assert 'value="Pretos, pardos, indígenas e quilombolas"' in corpo
    assert 'value="NASCIMENTO"' in corpo
    # A tela diz que o que está nela ainda não chegou ao servidor, e é isso que impede o script de
    # tomar o restaurado pelo renderizado e apagar o guardado.
    assert "data-rascunho-restaurado" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_restaurar_nao_grava(client, seletor_ligado, edital):
    """Restaurar põe na tela, e só: quem envia continua sendo a pessoa (FR-020)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    revisao = edital.revision

    restaurar(client, edital)

    edital.refresh_from_db()
    assert edital.revision == revisao
    assert forms.perfis_do_edital(edital) == []


@pytest.mark.django_db
@pytest.mark.integration
def test_restaurar_pede_quem_pode_compor(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    identificar(client, "iris.auditora", ["auditor"])

    corpo = restaurar(client, edital).content.decode()

    assert "data-rascunho-restaurado" not in corpo
    assert 'value="PPIQ"' not in corpo


def test_a_lista_de_escolha_multipla_e_guardada_opcao_por_opcao():
    """As Etapas que o marco enumera voltam todas da restauração (053, FR-979).

    Medido no preview: o `rascunho.js` guardava cada campo pelo `value`, que numa lista de escolha
    múltipla é só a primeira opção marcada. Nenhuma etapa com rascunho tinha lista múltipla até a
    Classificação ganhar o dela, e a tela restaurada voltava com uma Etapa a menos em cada marco —
    que a gravação seguinte apagaria sem aviso.

    **Varredura do fonte, e não execução**: o shim de `tests/javascript/dom.js` não tem lista de
    escolha múltipla, e o comportamento foi verificado no navegador (quickstart.md da 053, passo 8).
    O que se prende aqui é que as duas leituras do script — a que guarda para restaurar e a que
    compara com o renderizado — tratam a lista múltipla pelas opções.
    """
    fonte = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo"
        / "interface"
        / "static"
        / "interface"
        / "rascunho.js"
    ).read_text()

    assert fonte.count('campo.type === "select-multiple"') >= 2
    assert "opcao.selected" in fonte
