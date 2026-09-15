"""O acervo publicado sem quadro continua retificável, e ganha linha por ato (027, FR-323, FR-332).

**A armadilha que este arquivo existe para travar.** `retificacoes.py` afere o conteúdo que o ato
produziria com `blocking_findings(validate_for_publication(content))`. A exigência da linha geral,
escrita sem o recorte do ato, bloquearia **toda** Retificação de **todo** Edital do acervo —
inclusive as que corrigem uma data e nada têm com vagas. O defeito não apareceria em nenhum teste
de composição: só apareceria no dia em que alguém tentasse corrigir um Edital antigo.

Por isso o par é obrigatório: a recusa da T009 e este teste entram no mesmo passo.

O acervo é simulado como ele realmente é — Publicação em versão canônica anterior ao degrau que
criou o quadro —, e não por `UPDATE`: publicação é append-only por trigger desde a `002`.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.domain.elevacao import elevar
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.legado import publicar_na_versao_anterior
from tests.fixtures.publicacao import retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    """Edital publicado antes de o quadro de vagas existir — a condição de 100% do acervo."""
    return publicar_na_versao_anterior(api_client, manager_headers, process_payload)


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def conteudo_vigente(edital):
    """Elevado, que é como todo leitor o enxerga.

    O que está **gravado** é o conteúdo da versão canônica em que foi publicado, e ele não é
    reescrito nunca; a elevação acontece na leitura. Um Edital do acervo tem `vacancyTable` ausente
    no que está gravado e **vazio** no que se lê — e vazio é a grafia da ausência (025, D-005).
    """
    return elevar(vigente(edital).content)


def test_o_acervo_nasce_sem_linha_de_quadro(do_acervo):
    """A premissa dos demais: sem isto, eles provariam outra coisa."""
    perfil = conteudo_vigente(do_acervo)["profiles"][0]
    assert perfil["vacancyTable"] == []
    assert perfil["immediateVacancies"] >= 1


def test_retificar_a_descricao_de_edital_sem_quadro_passa(api_client, do_acervo):
    """A armadilha 2, e a razão de a FR-323 recortar a exigência pelo ato.

    Esta Retificação não tem nada com vagas. Se a ausência de linha geral fosse impeditiva aqui, o
    acervo inteiro ficaria preso — e coagir a declarar o quadro seria o mecanismo errado: quem diz
    quem precisa do ato é a FR-331, e quem aponta o ato é a FR-332.
    """
    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Descrição corrigida"}],
    )

    assert vigente(do_acervo).content["description"] == "Descrição corrigida"


def test_o_acervo_ganha_a_linha_geral_por_retificacao(api_client, do_acervo):
    """O caminho que a `025` abriu e a `026` obrigou a existir na tela (FR-332, SC-109)."""
    perfil = conteudo_vigente(do_acervo)["profiles"][0]
    total = perfil["immediateVacancies"]

    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009a1",
                    "modalityId": None,
                    "immediateVacancies": total,
                },
            }
        ],
    )

    linhas = conteudo_vigente(do_acervo)["profiles"][0]["vacancyTable"]
    assert [(linha["modalityId"], linha["immediateVacancies"]) for linha in linhas] == [
        (None, total)
    ]


def test_nenhum_conteudo_publicado_anterior_e_reescrito(api_client, do_acervo):
    """FR-333 e SC-110: o acervo só muda por ato, e o que ficou para trás continua legível."""
    original = vigente(do_acervo)
    antes = original.content

    retify(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Outra"}],
    )

    original.refresh_from_db()
    assert original.content == antes, "a versão anterior foi reescrita — publicação é ato imutável"
    assert vigente(do_acervo).id != original.id


def test_a_retificacao_do_acervo_aponta_o_ato_que_declara_a_quantidade(do_acervo):
    """FR-332 e FR-335: a advertência chega onde quem pode agir já está.

    A tela de Retificação é exatamente o lugar onde a linha se acrescenta, e é nela que a
    advertência aparece — em vez de o operador descobrir na Ocupação, meses depois, que o Edital
    publica um número que não governa nada.

    **Advertência, e nunca recusa.** Prender a Retificação de um Edital antigo até que alguém lhe
    dê quadro bloquearia até a correção de uma data.
    """
    from processo_seletivo.editais.domain.validation import (
        ATO_DE_PUBLICACAO,
        ATO_DE_RETIFICACAO,
        Severity,
        validate_for_publication,
    )

    conteudo = conteudo_vigente(do_acervo)
    achados = [
        item
        for item in validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO)
        if item.code == "vacancy_table_absent_in_archive"
    ]
    assert achados, "o acervo sem quadro precisa ser dito a quem pode retificá-lo"
    assert achados[0].severity == Severity.WARNING
    assert "não publica quadro de vagas" in achados[0].message
    assert "é o ato que declara a quantidade" in achados[0].message

    # E no ato de publicação a mesma ausência é impedimento, e não conselho: ali ela significaria
    # criar hoje o Edital inerte que a feature existe para deixar de produzir.
    impeditivos = [
        item.code
        for item in validate_for_publication(conteudo, ato=ATO_DE_PUBLICACAO)
        if item.code.startswith("vacancy_")
    ]
    assert "vacancy_general_row_missing" in impeditivos
    assert "vacancy_table_absent_in_archive" not in impeditivos, (
        "publicar não é a hora de aconselhar: ali a ausência é impedimento"
    )


def test_alterar_so_o_total_de_um_perfil_com_linha_geral_e_recusado_dizendo_os_dois(
    api_client, do_acervo
):
    """FR-335: num Perfil sem lista reservada, o total e a linha são o mesmo número.

    Este é o caminho pelo qual a divergência renasceria depois de a feature a ter eliminado: o
    Edital ganha a linha por Retificação e, na Retificação seguinte, alguém move só o total.
    """
    from tests.fixtures.publicacao import create_retification

    perfil = conteudo_vigente(do_acervo)["profiles"][0]
    total = perfil["immediateVacancies"]
    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009b1",
                    "modalityId": None,
                    "immediateVacancies": total,
                },
            }
        ],
        suffix="b",
    )

    recusa = create_retification(
        api_client,
        do_acervo,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/profiles/id={perfil['id']}/immediateVacancies",
                "newValue": total + 7,
            }
        ],
        suffix="c",
        esperar=422,
    )

    detalhe = recusa["detail"]
    assert str(total + 7) in detalhe and str(total) in detalhe, "a recusa diz os dois números"
    assert "mesmo número" in detalhe and "mesmo ato" in detalhe


def test_a_advertencia_do_acervo_alcanca_o_perfil_de_zero_vaga(
    api_client, manager_headers, process_payload
):
    """A outra metade da FR-331 no mesmo caso: a advertência da Retificação também não descarta o
    zero. Ausência de quadro é ausência, tenha o Perfil 40 vagas ou nenhuma."""
    from processo_seletivo.editais.domain.validation import (
        ATO_DE_RETIFICACAO,
        validate_for_publication,
    )
    from tests.fixtures.edital import complete_draft
    from tests.fixtures.legado import publicar_na_versao_anterior

    rascunho = complete_draft()
    rascunho["profiles"][0]["immediateVacancies"] = 0
    edital = publicar_na_versao_anterior(
        api_client, manager_headers, process_payload, draft=rascunho, versao=11
    )

    achados = [
        item
        for item in validate_for_publication(conteudo_vigente(edital), ato=ATO_DE_RETIFICACAO)
        if item.code == "vacancy_table_absent_in_archive"
    ]
    assert achados, "zero declarado não é o mesmo que quadro ausente"
    assert "publica 0 vaga(s) imediata(s)" in achados[0].message


def test_a_confirmacao_mostra_a_advertencia_do_conteudo_que_vai_vigorar(
    client, api_client, do_acervo, seletor_ligado
):
    """FR-336 pelo canal do ator, e sobre a base certa.

    **Duas coisas de uma vez.** A primeira é que a advertência chega à tela: a conferência do ato
    calculava os achados e ficava só com os impeditivos, de modo que o mesmo conteúdo dizia coisas
    diferentes conforme chegasse por submissão ou por Retificação.

    A segunda é de onde ela é calculada. Aplicar as mudanças sobre o conteúdo-base isolado ignora as
    Retificações concorrentes: a publicação consolida todas as vigentes na fronteira, e uma
    Retificação de outra pessoa pode fazer a advertência aparecer ou sumir. Aqui a linha é declarada
    por um ato **já publicado**, e o ato em elaboração — que não a toca — não pode continuar
    anunciando que ela falta.
    """
    from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
    from tests.fixtures.publicacao import create_retification
    from tests.interface.conftest import identificar

    perfil = conteudo_vigente(do_acervo)["profiles"][0]

    # Um ato em elaboração que **não** toca no quadro: corrige a descrição.
    em_elaboracao = create_retification(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Corrigida"}],
        suffix="d",
    )
    antes = {item.code for item in advertencias_do_ato(em_elaboracao)}
    assert "vacancy_table_absent_in_archive" in antes, "o acervo sem quadro é dito a quem retifica"

    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:retificacao-ato", args=[em_elaboracao.id, "submeter"])
    ).content.decode()
    assert "não publica quadro de vagas" in corpo, "e chega à tela de confirmação"

    # Outra pessoa declara a linha, e publica. O ato em elaboração continua o mesmo.
    retify(
        api_client,
        do_acervo,
        [
            {
                "operation": "ADD",
                "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/-",
                "newValue": {
                    "id": "00000000-0000-0000-0000-0000000009e1",
                    "modalityId": None,
                    "immediateVacancies": perfil["immediateVacancies"],
                },
            }
        ],
        suffix="e",
    )

    depois = {item.code for item in advertencias_do_ato(em_elaboracao)}
    assert "vacancy_table_absent_in_archive" not in depois, (
        "a advertência fala do conteúdo que vai vigorar, e ele já não tem essa ausência"
    )
