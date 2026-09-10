"""A jornada de partir de um Edital anterior, pela tela (023, US1 e US3).

O canal é a interface administrativa, que é o de quem elabora. Os dois papéis aparecem separados de
propósito: quem cria o Processo é o **Gestor**, quem escolhe a origem é o **Elaborador**. Fazer os
dois passos com a mesma identidade esconderia justamente a decisão que `D-001` tomou.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from tests.fixtures.publicacao import retify
from tests.integration.editais.test_reaproveitamento import PERFIL, rascunho_rico
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("seletor_ligado")]


@pytest.fixture
def origem(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    def vincular(edital):
        edital.documentos_exigidos.filter(key="diploma").update(
            anexo=edital.anexos.order_by("order").first()
        )

    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_rico(),
        anexos=1,
        antes_de_submeter=vincular,
    )


@pytest.fixture
def destino(api_client, manager_headers, origem):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-001",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "77", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-key-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def composicao(edital, etapa="identificacao"):
    return reverse("interface:compor-etapa", args=[edital.id, etapa])


def escolher(client, destino, origem):
    pagina = client.get(reverse("interface:reaproveitar", args=[destino.id]))
    assert pagina.status_code == 200
    corpo = pagina.content.decode()
    import re

    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)
    return client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(origem.id), "chave_idempotencia": chave},
    )


# ---------------------------------------------------------------------------
# T016 — a jornada e a afordância
# ---------------------------------------------------------------------------


def test_o_cartao_aparece_no_edital_vazio(client, destino):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(composicao(destino)).content.decode()

    assert "Partir de um Edital anterior" in corpo
    assert reverse("interface:reaproveitar", args=[destino.id]) in corpo


def test_a_escolha_lista_a_origem_elegivel_e_a_copia_preenche_o_assistente(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])

    pagina = client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()
    assert f"Edital {origem.number}/{origem.year}" in pagina
    assert "Usar como base" in pagina

    resposta = escolher(client, destino, origem)

    assert resposta.status_code == 302
    assert resposta["Location"].startswith(composicao(destino))
    destino.refresh_from_db()
    assert destino.perfis.count() == 1
    assert destino.anexos.count() == 1
    # E o conteúdo chega nas etapas do assistente, que é o que a pessoa precisa ver.
    perfis = client.get(composicao(destino, "perfis")).content.decode()
    assert "Designer Educacional" in perfis
    cronograma = client.get(composicao(destino, "cronograma")).content.decode()
    assert "Período de inscrições" in cronograma


def test_o_cartao_desaparece_depois_da_copia(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    corpo = client.get(composicao(destino)).content.decode()

    assert "Partir de um Edital anterior" not in corpo


def test_a_tela_avisa_quando_ja_ha_conteudo_a_substituir(client, destino, origem):
    """Rascunho cheio não fecha mais a porta: muda o que a porta avisa (D-009).

    Fechá-la deixava um beco — errada a origem, refazer à mão ou cancelar o Edital, que queima o
    número para sempre porque a unicidade de `(escopo, número, ano)` não tem condição.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    corpo = client.get(reverse("interface:reaproveitar", args=[destino.id]))

    assert corpo.status_code == 200
    texto = corpo.content.decode()
    assert "Este Edital já tem conteúdo composto" in texto
    assert "substitui" in texto
    assert "Substituir pelo escolhido" in texto


def test_quem_nao_elabora_nao_ve_nem_alcanca(client, destino):
    """Sem `edital:elaborar` o cartão não aparece e a tela não abre (FR-003)."""
    identificar(client, "bruno.homologador", ["homologador"])

    corpo = client.get(composicao(destino)).content.decode()
    assert "Partir de um Edital anterior" not in corpo
    assert client.get(reverse("interface:reaproveitar", args=[destino.id])).status_code == 404


# ---------------------------------------------------------------------------
# T035 / T040 — o aviso e a trilha
# ---------------------------------------------------------------------------


def test_o_aviso_nomeia_a_origem_em_todas_as_etapas(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    for etapa in ("identificacao", "perfis", "cronograma", "conteudo", "revisao"):
        corpo = client.get(composicao(destino, etapa)).content.decode()
        assert f"iniciado a partir do Edital {origem.number}/{origem.year}" in corpo
        assert "versão da publicação nº" in corpo and "vigente desde" in corpo
        assert "atualize as informações desta oferta" in corpo


def test_a_trilha_diz_de_onde_veio_em_forma_legivel(client, destino, origem, api_client):
    """Identificador no registro, Edital e versão na tela (FR-014a).

    O aviso desaparece quando o Edital sai da elaboração; a trilha é o que sobra, e é por ela que a
    origem se verifica depois de publicado.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    identificar(client, "carla.auditora", ["auditor"])
    corpo = client.get(reverse("interface:auditoria", args=[destino.id])).content.decode()

    assert "Criação a partir de Edital anterior" in corpo
    assert f"a partir do Edital {origem.number}/{origem.year}" in corpo
    # **O ato que produziu a versão, e não só a data**: uma Retificação rematerializa uma versão por
    # fronteira temporal, e duas linhas distintas apareceriam como a mesma "versão de 09/09/2026"
    # (FR-014a, SC-005).
    assert "versão da publicação nº" in corpo
    assert "vigente desde" in corpo


def test_a_trilha_continua_legivel_depois_de_retificada_a_origem(
    client, destino, origem, api_client
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    retify(
        api_client,
        origem,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/name",
                "operation": "REPLACE",
                "newValue": "Nome retificado",
            }
        ],
    )

    identificar(client, "carla.auditora", ["auditor"])
    corpo = client.get(reverse("interface:auditoria", args=[destino.id])).content.decode()

    assert f"a partir do Edital {origem.number}/{origem.year}" in corpo


# ---------------------------------------------------------------------------
# Regressões encontradas na revisão do próprio incremento
# ---------------------------------------------------------------------------


def test_reenviar_o_formulario_termina_onde_a_primeira_requisicao_terminou(client, destino, origem):
    """O POST não pode ser barrado pela precondição que a própria operação altera.

    Era o mesmo defeito de `FR-017a`, reintroduzido uma camada acima: a view conferia o rascunho
    vazio antes de chamar o comando, e o reenvio da mesma requisição — recarregar a página de
    resultado, ou voltar e enviar de novo — respondia 404 em vez de terminar na composição.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    primeira = escolher(client, destino, origem)
    assert primeira.status_code == 302

    repetida = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(origem.id), "chave_idempotencia": _chave_da_primeira(client, destino)},
    )

    # **302 e o destino, e não "302 ou 200"**: `DomainError` é renderizado com 200, então aceitar os
    # dois faria o teste passar com a repetição recusada — que é exatamente o que ele existe para
    # impedir.
    assert repetida.status_code == 302
    assert repetida["Location"].startswith(composicao(destino))
    destino.refresh_from_db()
    assert destino.perfis.count() == 1
    assert destino.anexos.count() == 1


def test_a_repeticao_sobrevive_a_mudanca_de_situacao_do_destino(client, destino, origem):
    """A precondição que a operação altera não é só o rascunho: a situação também muda.

    Copiado o Edital, alguém o submete para revisão. O reenvio da mesma requisição — o botão de
    voltar, a recarga da página de resultado — precisa terminar onde a primeira terminou, porque a
    reserva da chave já tem resposta pronta. Conferir a situação antes do comando devolvia 404.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)
    chave = _chave_da_primeira(client, destino)
    Edital.objects.filter(pk=destino.pk).update(status=Edital.Status.EM_REVISAO)

    repetida = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(origem.id), "chave_idempotencia": chave},
    )

    assert repetida.status_code == 302
    assert repetida["Location"].startswith(composicao(destino))
    destino.refresh_from_db()
    assert destino.perfis.count() == 1


def test_a_tela_de_escolha_some_quando_o_edital_sai_da_elaboracao(client, destino):
    """A exibição continua conferindo a situação.

    O que a tela oferece precisa ser o que a tela consegue fazer.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    Edital.objects.filter(pk=destino.pk).update(status=Edital.Status.EM_REVISAO)

    assert client.get(reverse("interface:reaproveitar", args=[destino.id])).status_code == 404


def _chave_da_primeira(client, destino):
    """A mesma chave da primeira requisição, que é o que caracteriza um reenvio."""
    from processo_seletivo.auditoria.models import IdempotencyRecord

    return (
        IdempotencyRecord.objects.filter(operation=f"edital:reaproveitar:{destino.id}")
        .latest("id")
        .key
    )


def test_enviar_sem_escolher_origem_recusa_em_vez_de_estourar(client, destino, origem):
    """`UUIDField` levanta `ValidationError`, que **não** é `ValueError`.

    Sem a exceção na lista, o formulário enviado sem escolha devolvia 500 — e 500 não é recusa: é
    defeito exibido a quem só deixou de marcar uma opção.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": "", "chave_idempotencia": "sem-escolha-0001"},
    )

    assert resposta.status_code == 200
    assert "Recurso não encontrado" in resposta.content.decode()
    destino.refresh_from_db()
    assert destino.perfis.count() == 0


# ---------------------------------------------------------------------------
# A escolha, pela tela: localizar, paginar, e escolher sem armadilha
# ---------------------------------------------------------------------------


def _publicar_muitas(quantas, ano=2026):
    """Editais publicados em massa, para exercitar a lista longa.

    Direto no modelo: o que se exercita aqui é a paginação e a busca, e levar vinte Editais até a
    Publicação pelo fluxo inteiro custaria minutos para provar o que a lista já mostra. Eles não têm
    versão consolidada — e é de propósito: a lista precisa aguentar isso sem cair.
    """
    from processo_seletivo.processos.models import ProcessoSeletivo

    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code="PS-MASSA",
        title="Processo com muitos Editais",
        created_at=timezone.now(),
        created_by="gestor-a",
        last_changed_at=timezone.now(),
    )
    return Edital.objects.bulk_create(
        [
            Edital(
                processo=processo,
                institution_scope="cefor",
                number=f"{numero:03d}",
                year=ano,
                title=f"Edital de massa {numero}",
                status=Edital.Status.PUBLICADO,
                created_at=timezone.now(),
                created_by="gestor-a",
                last_edited_by="gestor-a",
            )
            for numero in range(100, 100 + quantas)
        ]
    )


def test_a_busca_encontra_e_o_filtro_fica_no_campo(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    _publicar_muitas(3)

    corpo = client.get(
        reverse("interface:reaproveitar", args=[destino.id]), {"busca": "massa 101"}
    ).content.decode()

    assert "Edital de massa 101" in corpo
    assert "Edital de massa 102" not in corpo
    assert origem.title not in corpo
    assert 'value="massa 101"' in corpo
    assert "Limpar" in corpo


def test_a_busca_sem_resultado_diz_o_que_procurou(client, destino):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:reaproveitar", args=[destino.id]), {"busca": "não existe"}
    ).content.decode()

    assert "Nenhum Edital do seu escopo corresponde a" in corpo
    assert "não existe" in corpo
    assert "Usar como base" not in corpo


def test_a_lista_e_paginada_e_a_busca_atravessa_as_paginas(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    _publicar_muitas(25)

    primeira = client.get(
        reverse("interface:reaproveitar", args=[destino.id]), {"busca": "massa"}
    ).content.decode()
    assert primeira.count('name="origem"') == 20
    assert "Página 1 de 2" in primeira
    assert "busca=massa" in primeira, "a pergunta que trouxe a pessoa até aqui viaja com a página"

    segunda = client.get(
        reverse("interface:reaproveitar", args=[destino.id]), {"busca": "massa", "pagina": 2}
    ).content.decode()
    assert segunda.count('name="origem"') == 5


def test_nenhuma_origem_vem_pre_escolhida(client, destino, origem):
    """Vinha a primeira. Com a lista paginada, isso vira armadilha: quem avança de página
    encontraria outra origem já marcada, e copiaria o que não pretendia."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()

    radios = re.findall(r"<input[^>]*type=\"radio\"[^>]*>", corpo)
    assert radios, "a lista precisa oferecer alguma origem para o cenário significar algo"
    assert all("checked" not in radio for radio in radios)
    assert all("required" in radio for radio in radios)


def test_o_grupo_de_escolha_e_anunciado_a_quem_ouve_a_tela(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()

    assert "<fieldset>" in corpo
    assert 'class="oculto">Edital de origem</legend>' in corpo


def test_a_lista_diz_o_que_cada_origem_traz(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()

    assert "1 perfil" in corpo
    assert "2 eventos" in corpo
    assert "1 anexo" in corpo
    assert "Publicado em" in corpo


# ---------------------------------------------------------------------------
# Trocar a origem: a lista antes de perder, e a troca de verdade (D-009)
# ---------------------------------------------------------------------------


@pytest.fixture
def segunda_origem(api_client, manager_headers, origem):
    """Uma origem diferente da primeira, para a troca ter para onde ir."""
    from tests.fixtures.edital import complete_draft
    from tests.fixtures.publicacao import publish_original

    return publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "segunda-origem-0001"},
        {
            "institutionalCode": "PS-2026-002",
            "title": "Outro Processo",
            "firstEdital": {"number": "99", "year": 2026, "title": "Edital da outra origem"},
        },
        draft=complete_draft(seed=7),
    )


def test_escolher_com_rascunho_cheio_pede_confirmacao_e_enumera_o_que_se_perde(
    client, destino, origem, segunda_origem
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    pedido = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(segunda_origem.id), "chave_idempotencia": "troca-0001"},
    )

    assert pedido.status_code == 200
    corpo = pedido.content.decode()
    assert "Isto substitui o que já está composto" in corpo
    assert "Serão descartados" in corpo
    assert "1 Perfil de Vaga" in corpo
    assert "2 Eventos do Cronograma" in corpo
    assert "1 Anexo" in corpo
    # E nada foi trocado ainda.
    destino.refresh_from_db()
    assert destino.perfis.get().name == "Designer Educacional"


def test_confirmada_a_troca_o_conteudo_e_o_da_nova_origem(client, destino, origem, segunda_origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)
    anexos_da_primeira = list(destino.anexos.values_list("artefato_id", flat=True))

    trocada = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {
            "origem": str(segunda_origem.id),
            "chave_idempotencia": "troca-0002",
            "confirmar_troca": "1",
        },
    )

    assert trocada.status_code == 302
    destino.refresh_from_db()
    assert destino.perfis.get().name == "Perfil"
    assert destino.perfis.get().name != "Designer Educacional"
    # Os Anexos da primeira origem saíram, e os arquivos deles junto: `uq_anexo_edital_order`
    # recomeça em 1 a cada cópia, e artefato de rascunho que ninguém publicou não fica para trás.
    from processo_seletivo.editais.models.anexos import ArtefatoAnexo

    assert destino.anexos.count() == 0
    assert not ArtefatoAnexo.objects.filter(id__in=anexos_da_primeira).exists()


def test_o_aviso_passa_a_nomear_a_nova_origem(client, destino, origem, segunda_origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {
            "origem": str(segunda_origem.id),
            "chave_idempotencia": "troca-0003",
            "confirmar_troca": "1",
        },
    )

    corpo = client.get(composicao(destino)).content.decode()
    assert f"a partir do Edital {segunda_origem.number}/{segunda_origem.year}" in corpo
    assert f"a partir do Edital {origem.number}/{origem.year}" not in corpo


def test_a_troca_nao_engole_a_repeticao_conhecida(client, destino, origem):
    """A confirmação é a recusa apresentada, e não uma segunda verificação.

    Perguntar antes de chamar o comando faria o reenvio da mesma requisição cair na pergunta em vez
    de terminar onde a primeira terminou — e quem sabe se é repetição é a reserva, no comando.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    repetida = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(origem.id), "chave_idempotencia": _chave_da_primeira(client, destino)},
    )

    assert repetida.status_code == 302
    assert "Isto substitui" not in repetida.content.decode()


def test_a_troca_aparece_no_aviso_de_todas_as_etapas(client, destino, origem):
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)

    corpo = client.get(composicao(destino, "cronograma")).content.decode()

    assert "Partir de outro" in corpo
    assert reverse("interface:reaproveitar", args=[destino.id]) in corpo


def test_a_lista_leva_ao_edital_publicado_para_ler_antes_de_escolher(client, destino, origem):
    """Ler antes de escolher, sem construir uma segunda prévia do que já está publicado."""
    from django.urls import reverse as url

    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(reverse("interface:reaproveitar", args=[destino.id])).content.decode()

    assert url("portal:selecao", args=[origem.id]) in corpo
    assert "Ver o Edital" in corpo
