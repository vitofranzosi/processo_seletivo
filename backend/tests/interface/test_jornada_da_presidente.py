"""A jornada de quem preside sem papel sistêmico — o ator central da 011.

Estes testes nasceram de um percurso manual: a presidente conseguia fazer tudo, e o sistema lhe
dizia que ela não podia nada. As telas herdadas decidiam por `ator.permissions`, e a base
contextual que a 011 criou não existia para elas.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def presidente(client, seletor_ligado, comissao_de_a):
    identificar(client, "maria", [])
    return client


def test_a_lista_nao_diz_que_a_presidente_nao_tem_papel(presidente, processo_a):
    """L1: "Sua conta não possui nenhum papel de responsabilidade" era falso para ela."""
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" not in corpo
    assert "Você preside a comissão" in corpo


def test_a_lista_oferece_a_comissao_a_quem_a_integra(presidente, processo_a):
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo


def test_quem_nao_tem_vinculo_continua_recebendo_a_orientacao(client, seletor_ligado, processo_a):
    """A garantia da 002 permanece para quem de fato não tem nada."""
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" in corpo


def test_a_presidente_sem_alocacao_nao_e_mandada_pedir_acesso(presidente):
    """L2: ela já integra a comissão — mandá-la pedir para ser registrada é dizer o oposto."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" not in corpo
    assert "Comissões que você integra" in corpo


def test_minhas_etapas_leva_a_presidente_ate_a_comissao_dela(presidente, processo_a):
    """L3: o acesso existia; a rota não."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo
    assert reverse("interface:alocacoes", args=[processo_a.id]) in corpo


def test_quem_nao_tem_nada_continua_recebendo_a_orientacao_em_minhas_etapas(
    client, seletor_ligado
):
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" in corpo


def test_a_escolha_nao_oferece_quem_ja_esta_alocado(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L4: oferecer quem já está era a tela produzindo o próprio 409."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    bloco = corpo.split(f'value="{etapa_a1}"')[1].split("</form>")[0]
    assert f'value="{comissao_de_a["joao"].id}"' not in bloco
    assert f'value="{comissao_de_a["maria"].id}"' in bloco


def test_etapa_com_a_comissao_toda_alocada_diz_isso(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    for membro in comissao_de_a.values():
        alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert "Toda a comissão já está alocada nesta Etapa" in corpo


def test_as_remocoes_dizem_de_quem_e_de_onde(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L5: rótulos repetidos são indistinguíveis por leitor de tela.

    Na Alocação isso deixou de ser um botão por linha: a caixa nomeia a pessoa e o botão nomeia
    a Etapa, o que resolve a distinção e a remoção em lote de uma vez.
    """
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    alocacoes = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()
    comissao = presidente.get(
        reverse("interface:comissao", args=[processo_a.id])
    ).content.decode()

    assert f'name="alocacao_id" value="{comissao_de_a["joao"].alocacoes.get().id}"' in alocacoes
    assert 'aria-label="Remover as pessoas marcadas da Etapa Análise documental"' in alocacoes
    assert "Quem atua em Análise documental" in alocacoes
    assert 'aria-label="Remover joao da comissão"' in comissao


def test_a_confirmacao_de_atribuicao_nao_usa_estilo_de_alerta(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L8: a frase que confirma a atribuição parecia um problema a resolver."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])

    corpo = client.get(
        reverse("interface:atribuicao", args=[edital_a.id, etapa_a1])
    ).content.decode()

    trecho = corpo.split("Você está alocado nesta Etapa")[0][-120:]
    assert 'class="sucesso"' in trecho


def test_alocar_a_comissao_inteira_numa_submissao(
    presidente, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """O item que corta 160 envios a 4: uma submissão, várias pessoas."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    resposta = presidente.post(
        reverse("interface:alocacoes", args=[processo_a.id]),
        {
            "acao": "incluir",
            "edital_id": str(edital_a.id),
            "etapa_id": etapa_a1,
            "membro_id": [str(m.id) for m in comissao_de_a.values()],
            "chave_idempotencia": "interface-lote-0001",
        },
        follow=True,
    )

    assert resposta.status_code == 200
    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 2


def test_a_alocacao_abre_com_o_resumo(presidente, processo_a, comissao_de_a):
    """Sem ele, a resposta que a tela existe para dar tem de ser contada nos cartões."""
    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert "Etapas com equipe" in corpo or "Etapa com equipe" in corpo
    assert "sem ninguém" in corpo
    assert "sem atribuição" in corpo


def test_a_comissao_pode_ser_filtrada_por_nome(presidente, processo_a, comissao_de_a):
    corpo = presidente.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?q=joao"
    ).content.decode()

    assert "joao" in corpo
    assert "maria" not in corpo.split("Membros da comissão")[1].split("Adicionar membro")[0]


def test_a_comissao_pode_mostrar_so_quem_esta_sem_etapa(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """A pergunta que o presidente faz de verdade numa banca grande."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?sem_etapa=1"
    ).content.decode()

    lista = corpo.split("Membros da comissão")[1].split("Adicionar membro")[0]
    assert "maria" in lista
    assert "joao" not in lista


def test_a_trilha_filtra_por_pessoa_e_por_operacao(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """19 páginas de vinte não respondem “quem perdeu acesso a esta Etapa”."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "auditora", ["auditor"])
    url = reverse("interface:auditoria-comissao", args=[processo_a.id])

    def atos(corpo):
        # Só a lista: o seletor de filtro contém todos os rótulos, e procurá-los na página
        # inteira testaria o formulário em vez do filtro.
        return corpo.split('aria-label="Atos registrados"')[1]

    por_operacao = atos(client.get(url + "?operacao=ALOCACAO_INCLUIR").content.decode())
    por_pessoa = atos(client.get(url + "?pessoa=maria").content.decode())

    assert "Alocação em Etapa" in por_operacao
    assert "Inclusão na comissão" not in por_operacao
    assert "maria" in por_pessoa
    assert "joao" not in por_pessoa


def test_constituir_a_comissao_pela_lista_colada(presidente, processo_a):
    """Oitenta passos para uma banca de quarenta: dois envios por pessoa era o custo real."""
    from processo_seletivo.comissoes.models import MembroComissao

    url = reverse("interface:comissao", args=[processo_a.id])
    conferencia = presidente.post(
        url,
        {
            "acao": "incluir_lote",
            "lista": "ana.costa, Ana Costa\njoao.souza\nbia.lima, Bia Lima",
            "funcao": "MEMBRO",
        },
    )

    assert conferencia.status_code == 200
    corpo = conferencia.content.decode()
    assert "ana.costa" in corpo and "joao.souza" in corpo and "bia.lima" in corpo
    assert "3 pessoas" in corpo
    # Nada foi gravado ainda: a conferência confere a lista inteira antes.
    assert MembroComissao.objects.filter(identity_subject="ana.costa").count() == 0

    presidente.post(
        url,
        {
            "acao": "incluir_lote",
            "confirmado": "1",
            "lista": "ana.costa, Ana Costa\njoao.souza\nbia.lima, Bia Lima",
            "funcao": "MEMBRO",
            "chave_idempotencia": "interface-lote-membros-0001",
        },
    )

    assert MembroComissao.objects.filter(processo=processo_a, ativo=True).count() == 5


def test_a_conferencia_marca_quem_ja_integra_a_comissao(presidente, processo_a, comissao_de_a):
    corpo = presidente.post(
        reverse("interface:comissao", args=[processo_a.id]),
        {"acao": "incluir_lote", "lista": "joao\nana.nova", "funcao": "MEMBRO"},
    ).content.decode()

    assert "já integra a comissão" in corpo
    assert "será incluída" in corpo


def test_remover_varias_alocacoes_numa_submissao_pela_tela(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    alocacoes = [
        alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)
        for membro in comissao_de_a.values()
    ]

    presidente.post(
        reverse("interface:alocacoes", args=[processo_a.id]),
        {
            "acao": "remover",
            "alocacao_id": [str(a.id) for a in alocacoes],
            "chave_idempotencia": "interface-remocao-lote-0001",
        },
        follow=True,
    )

    assert AlocacaoEtapa.objects.filter(ativo=True).count() == 0


def test_alocar_toda_a_comissao_disponivel_num_botao(
    presidente, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """O caso mais comum numa etapa documental é a banca inteira entrar."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    presidente.post(
        reverse("interface:alocacoes", args=[processo_a.id]),
        {
            "acao": "incluir_todos",
            "edital_id": str(edital_a.id),
            "etapa_id": etapa_a1,
            "disponivel": [str(m.id) for m in comissao_de_a.values()],
            "chave_idempotencia": "interface-todos-0001",
        },
        follow=True,
    )

    assert AlocacaoEtapa.objects.filter(ativo=True, etapa_id=etapa_a1).count() == 2


def test_a_comissao_e_ordenada_pelo_que_se_le(presidente, gestor, processo_a):
    """Mostrar "Maria Silva" e ordenar por "maria.presidente" embaralha uma lista de quarenta."""
    from processo_seletivo.comissoes.application.comissao import adicionar_varios
    from processo_seletivo.comissoes.application.selectors import membros

    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[
            ("zeca", "Ana Primeira"),
            ("ana", "Zulmira Última"),
            ("bea", "Bruno Meio"),
            # Acentuada no meio: por codepoint ela cairia depois de Zulmira.
            ("iri", "Íris Melo"),
        ],
        funcao="MEMBRO",
        idempotency_key="ordem-de-leitura-0001",
        correlation_id="c",
    )

    lidos = [m.display_label for m in membros(processo_a) if m.display_label]

    assert lidos == ["Ana Primeira", "Bruno Meio", "Íris Melo", "Zulmira Última"]


def test_a_lista_atravessa_a_conferencia_sem_perder_as_linhas(presidente, processo_a):
    """O caminho real passa a lista por um campo oculto — e atributo HTML não é textarea.

    O teste anterior reenviava a lista que ele mesmo montou. Este pega a que a tela devolveu,
    que é a única forma de saber se a conferência preserva o que a pessoa colou.
    """
    import re

    from processo_seletivo.comissoes.models import MembroComissao

    url = reverse("interface:comissao", args=[processo_a.id])
    lista = "ana.costa, Ana Costa\njoao.souza\nbia.lima, Bia Lima"
    corpo = presidente.post(
        url, {"acao": "incluir_lote", "lista": lista, "funcao": "MEMBRO"}
    ).content.decode()

    campo = re.search(r'name="lista" value="(.*?)"', corpo, re.S)
    assert campo, "a conferência precisa devolver a lista para o envio final"
    devolvida = campo.group(1).replace("&#x0A;", "\n").replace("&amp;", "&")

    presidente.post(
        url,
        {
            "acao": "incluir_lote",
            "confirmado": "1",
            "lista": devolvida,
            "funcao": "MEMBRO",
            "chave_idempotencia": "interface-roundtrip-0001",
        },
    )

    incluidos = set(
        MembroComissao.objects.filter(processo=processo_a, ativo=True).values_list(
            "identity_subject", flat=True
        )
    )
    assert {"ana.costa", "joao.souza", "bia.lima"} <= incluidos


def test_os_controles_de_cada_membro_ficam_sob_demanda(presidente, processo_a, comissao_de_a):
    """A leitura corrente é quem está aqui e onde atua; o resto abre quando se pede.

    O que **não** pode ficar escondido é a informação — nome, identificador, função e Etapas
    continuam na leitura direta.
    """
    corpo = presidente.get(
        reverse("interface:comissao", args=[processo_a.id])
    ).content.decode()

    assert "<summary>Gerir joao</summary>" in corpo
    assert "<summary>Gerir maria</summary>" in corpo
    # A informação continua fora do disclosure.
    for membro in comissao_de_a.values():
        antes_do_details = corpo.split(f"Gerir {membro.identity_subject}")[0]
        assert membro.identity_subject in antes_do_details


def test_o_disclosure_nao_esconde_a_acao_do_teclado(presidente, processo_a, comissao_de_a):
    """`details` é nativo: abre por teclado e o formulário continua submetível."""
    from processo_seletivo.comissoes.models import Funcao

    presidente.post(
        reverse("interface:comissao", args=[processo_a.id]),
        {
            "acao": "alterar_funcao",
            "membro_id": str(comissao_de_a["joao"].id),
            "funcao": "PRESIDENTE",
            "chave_idempotencia": "interface-details-0001",
        },
    )

    comissao_de_a["joao"].refresh_from_db()
    assert comissao_de_a["joao"].funcao == Funcao.PRESIDENTE
