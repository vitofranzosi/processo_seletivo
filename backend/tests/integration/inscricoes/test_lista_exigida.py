"""A lista exigida: gravada no envio, lida depois, reconstruída quando não há (044, US2, US4).

O que se prova aqui é que a lista é **o que foi pedido**, e não o que a regra de hoje pediria. Os
leitores já liam a versão aceita, que é imutável — por isso um teste que só retifica e compara
passaria sem a feature. O teste que discrimina grava uma lista diferente do que `aplicabilidade`
calcularia, e confere que quem lê mostra a gravada (R-006).
"""

import pytest

from processo_seletivo.editais.domain import documentos
from processo_seletivo.inscricoes.application import lista_exigida as modulo
from processo_seletivo.inscricoes.application.consulta import _linhas
from processo_seletivo.inscricoes.application.lista_exigida import lista_exigida
from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import ItemDaListaExigida
from processo_seletivo.portal.views import _documentos, _requisitos_pedidos
from tests.fixtures.candidato import JOAO, MARIA, MODALIDADE_AC, PERFIL_DOCENTE, pdf
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

DECLARACOES = {"veracidade": True, "ciencia": True}


def _enviada(edital, identidade=MARIA, *, chave="envio-1"):
    inscricao = abrir_inscricao(
        identidade=identidade, edital_id=edital.id, profile_id=PERFIL_DOCENTE
    )
    inscricao = gravar_dados(
        identidade=identidade,
        inscricao=inscricao,
        dados={
            "nome": identidade.nome,
            "cpf": identidade.cpf,
            "email": identidade.email,
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito in (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL):
        anexar_documento(
            identidade=identidade, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=identidade, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key=chave
    )


def _itens(inscricao):
    return {
        str(item.requisito_id): item
        for item in ItemDaListaExigida.objects.filter(inscricao=inscricao)
    }


def test_o_envio_grava_um_item_por_documento_inclusive_o_que_nao_se_aplica(
    selecao, candidatos_registrados
):
    itens = _itens(_enviada(selecao))

    assert {chave: (item.situacao, item.forma_do_recorte) for chave, item in itens.items()} == {
        DOCUMENTO_DE_TODOS: ("OBRIGATORIO", "TODOS"),
        DOCUMENTO_DO_PERFIL: ("OBRIGATORIO", "PERFIL"),
        DOCUMENTO_DA_MODALIDADE: ("NAO_SE_APLICA", "TODOS_COM_MODALIDADE_DE_UM_PERFIL"),
    }
    assert str(itens[DOCUMENTO_DO_PERFIL].perfil_id) == PERFIL_DOCENTE


def test_a_lista_e_da_versao_e_do_instante_do_envio(selecao, candidatos_registrados):
    enviada = _enviada(selecao)

    for item in _itens(enviada).values():
        assert item.versao_id == enviada.versao_aceita_id
        assert item.gravada_em == enviada.submitted_at


def test_o_reenvio_com_a_mesma_chave_nao_grava_de_novo(selecao, candidatos_registrados):
    enviada = _enviada(selecao)
    enviar_inscricao(
        identidade=MARIA, inscricao=enviada, declaracoes=DECLARACOES, idempotency_key="envio-1"
    )

    assert ItemDaListaExigida.objects.filter(inscricao=enviada).count() == 3


def _dispensar_o_diploma(api_client, edital, suffix):
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/documentRequirements/id={DOCUMENTO_DO_PERFIL}/required",
                "operation": "REPLACE",
                "newValue": False,
            }
        ],
        suffix=suffix,
    )


def test_uma_retificacao_entre_dois_envios_deixa_cada_um_com_o_seu(
    api_client, selecao, candidatos_registrados
):
    antes = _enviada(selecao)
    _dispensar_o_diploma(api_client, selecao, "dispensa")
    depois = _enviada(selecao, JOAO, chave="envio-2")

    assert _itens(antes)[DOCUMENTO_DO_PERFIL].situacao == "OBRIGATORIO"
    assert _itens(depois)[DOCUMENTO_DO_PERFIL].situacao == "FACULTATIVO"
    assert (
        _itens(antes)[DOCUMENTO_DO_PERFIL].versao_id
        != _itens(depois)[DOCUMENTO_DO_PERFIL].versao_id
    )


def test_quem_le_mostra_a_lista_gravada_e_nao_a_regra_de_hoje(
    selecao, candidatos_registrados, monkeypatch
):
    """O teste que discrimina: a lista gravada diverge do que a regra calcularia agora."""
    original = documentos.aplicabilidade

    def gravada_diferente(conteudo, **kwargs):
        return [
            documentos.Veredito(v.requisito, documentos.FACULTATIVO, v.recorte)
            if str(v.requisito["id"]) == DOCUMENTO_DO_PERFIL
            else v
            for v in original(conteudo, **kwargs)
        ]

    monkeypatch.setattr(modulo, "aplicabilidade", gravada_diferente)
    enviada = _enviada(selecao)
    monkeypatch.setattr(modulo, "aplicabilidade", original)
    conteudo = enviada.versao_aceita.content

    lista = lista_exigida(enviada, conteudo)
    situacoes = {str(v.requisito["id"]): v.situacao for v in lista.itens}
    assert situacoes[DOCUMENTO_DO_PERFIL] == "FACULTATIVO", "a lista, e não a regra"
    assert lista.reconstruida is False

    linha = _linhas(selecao, [enviada])[0]
    assert (linha["recebidos"], linha["esperados"]) == (1, 1), "a consulta conta pela lista"

    pedidos = [str(item["id"]) for item, _obrigatorio in _requisitos_pedidos(conteudo, enviada)]
    assert pedidos == [DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL], "o portal lê a mesma lista"
    # Os ids sozinhos não discriminam: são os que a regra também daria. O que discrimina é a
    # obrigatoriedade — o conteúdo diz obrigatório, a lista diz facultativo, e o portal conta pela
    # lista, como a consulta acima.
    portal = _documentos(conteudo, enviada)
    obrigatorios = {linha["id"]: linha["obrigatorio"] for linha in portal["linhas"]}
    assert obrigatorios[DOCUMENTO_DO_PERFIL] is False, "o portal lê a situação, e não o conteúdo"
    assert portal["total"] == 1, "o portal conta os obrigatórios pela lista, como a consulta"


def test_inscricao_sem_lista_gravada_e_reconstruida_e_diz_que_foi(
    selecao, candidatos_registrados, monkeypatch
):
    """A inscrição enviada antes da `044` não tem lista, e não ganha uma (FR-726, D-004)."""
    monkeypatch.setattr(
        "processo_seletivo.inscricoes.application.submissao.gravar_lista_exigida",
        lambda *args, **kwargs: None,
    )
    enviada = _enviada(selecao)

    lista = lista_exigida(enviada, enviada.versao_aceita.content)

    assert ItemDaListaExigida.objects.filter(inscricao=enviada).count() == 0
    assert lista.reconstruida is True
    assert {str(v.requisito["id"]): v.situacao for v in lista.itens} == {
        DOCUMENTO_DE_TODOS: "OBRIGATORIO",
        DOCUMENTO_DO_PERFIL: "OBRIGATORIO",
        DOCUMENTO_DA_MODALIDADE: "NAO_SE_APLICA",
    }


def test_o_envio_tem_um_evento_so_e_a_auditoria_nao_repete_a_lista(selecao, candidatos_registrados):
    """A gravação da lista é parte do ato de envio, e não tem evento próprio (FR-729)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    enviada = _enviada(selecao)
    eventos = RegistroAuditoria.objects.filter(aggregate_id=str(enviada.pk))

    assert eventos.filter(operation="SUBMETER").count() == 1
    for evento in eventos:
        texto = f"{evento.reason} {evento.previous_state} {evento.new_state}"
        assert "NAO_SE_APLICA" not in texto and "OBRIGATORIO" not in texto


def test_a_divergencia_da_161_aparece_na_lista_reconstruida(selecao, candidatos_registrados):
    """O 903 original: "Todos os Perfis" + a PcD do C1, e a inscrição PcD do C2 (FR-727, SC-265)."""
    from processo_seletivo.inscricoes.models import Inscricao

    c1 = {
        "id": "c1",
        "code": "C1",
        "competitionModalities": [
            {"id": "c1-pcd", "code": "PcD", "name": "Pessoas com Deficiência"}
        ],
    }
    c2 = {
        "id": "c2",
        "code": "C2",
        "competitionModalities": [
            {"id": "c2-pcd", "code": "PcD", "name": "Pessoas com Deficiência"}
        ],
    }
    laudo = {
        "id": "laudo",
        "key": "laudo",
        "name": "Laudo médico (PcD)",
        "order": 1,
        "modalityId": "c1-pcd",
    }
    conteudo = {"profiles": [c1, c2], "documentRequirements": [laudo]}
    antiga = Inscricao(profile_id="00000000-0000-0000-0000-0000000000c2", modality_id=None)
    antiga.profile_id, antiga.modality_id = "c2", "c2-pcd"

    lista = lista_exigida(antiga, conteudo, itens=[])

    (veredito,) = lista.itens
    assert lista.reconstruida is True
    assert veredito.divergente_do_publicado is True
    assert documentos.razao_legivel(veredito, conteudo) == (
        "Não se aplica: pedido de quem concorre ao Perfil C1 em Pessoas com Deficiência — o "
        "Edital publicado o exigia de todo candidato em Pessoas com Deficiência. O portal não o "
        "pediu a esta inscrição."
    )


def test_a_divergencia_gravada_aparece_sem_aviso_de_reconstrucao():
    """O 903 continua recebendo inscrições depois da 044: a lista é gravada sobre a versão ambígua,
    e a divergência vai junto (FR-727, segunda frase)."""
    from processo_seletivo.inscricoes.models import Inscricao

    c1 = {
        "id": "c1",
        "code": "C1",
        "competitionModalities": [
            {"id": "c1-pcd", "code": "PcD", "name": "Pessoas com Deficiência"}
        ],
    }
    laudo = {"id": "laudo", "key": "laudo", "name": "Laudo médico (PcD)", "order": 1}
    conteudo = {"profiles": [c1], "documentRequirements": [laudo]}
    inscricao = Inscricao(profile_id="00000000-0000-0000-0000-0000000000c2")
    linha = ItemDaListaExigida(
        requisito_id="00000000-0000-0000-0000-0000000000aa",
        chave="laudo",
        situacao="NAO_SE_APLICA",
        forma_do_recorte="TODOS_COM_MODALIDADE_DE_UM_PERFIL",
        modalidade_id="00000000-0000-0000-0000-0000000000bb",
        divergente_do_publicado=True,
    )
    conteudo["profiles"][0]["competitionModalities"][0]["id"] = str(linha.modalidade_id)
    laudo["id"] = str(linha.requisito_id)

    lista = lista_exigida(inscricao, conteudo, itens=[linha])

    (veredito,) = lista.itens
    assert lista.reconstruida is False
    assert veredito.divergente_do_publicado is True
    assert "o Edital publicado o exigia de todo candidato em Pessoas com Deficiência" in (
        documentos.razao_legivel(veredito, conteudo)
    )
