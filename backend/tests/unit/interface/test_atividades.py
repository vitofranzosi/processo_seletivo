"""As funções puras de "Minhas atividades" (160, T003): filtrar, agrupar entre Editais e ordenar.

**Sem banco**: as providências são montadas à mão, como a derivação as emitiria. O que se prende
aqui é que a página não decide "sua" — só filtra pela base e pelas famílias que cobre —, que o ato
com número nunca se junta, e que a data da derivação não ordena a lista.
"""

import uuid
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import atividades as at
from processo_seletivo.interface import conceitos as c
from processo_seletivo.interface.providencias import Providencia

BRT = ZoneInfo("America/Sao_Paulo")


def edital(numero, ano=2026):
    return SimpleNamespace(id=uuid.uuid4(), number=str(numero), year=ano)


def prov(ato, *, natureza=a.ORDEM, situacao=a.PENDENTE, responsavel=a.CONDUZ, sua=True, **extra):
    return Providencia(
        natureza=natureza,
        chave=(natureza, ato),
        onde="Cefor",
        ato=ato,
        situacao=situacao,
        responsavel=responsavel,
        sua=sua,
        url="/gestao/x" if sua else "",
        lugar="Cefor",
        **extra,
    )


def linha(item, ed, *, base=at.PRESIDENCIA, indice=0):
    return at.Linha(item, ed, base, c.NOMES[c.CLASSIFICACAO], indice)


# --- o filtro da base (R-003) ---------------------------------------------------------------


def test_a_presidencia_fica_com_a_conducao_e_a_conferencia_e_nada_mais():
    itens = [
        prov("Emitir a ordem"),
        prov("Conferir os documentos de 1 convocação", natureza=a.CONFERIR, responsavel=a.CONFERE),
        prov("Publicar o resultado preliminar", natureza=a.RESULTADO, responsavel=a.PUBLICA),
        prov("Decidir 2 recursos", natureza=a.RECURSO, responsavel=a.JULGA),
        prov("Definir os documentos", natureza=a.FORMALIZACAO, responsavel=a.CONDUZ),
        prov("Avaliar 3 inscrições", natureza=a.AVALIAR, responsavel=a.AVALIA),
        prov("Emitir o corte", sua=False),
    ]
    atos = [item.ato for item in at.da_presidencia(itens)]
    assert atos == ["Emitir a ordem", "Conferir os documentos de 1 convocação"]


def test_a_conferencia_por_alocacao_fica_so_com_o_perfil_alocado():
    perfil_a, perfil_b = str(uuid.uuid4()), str(uuid.uuid4())
    itens = [
        prov("Conferir A", natureza=a.CONFERIR, responsavel=a.CONFERE, perfil_id=perfil_a),
        prov("Conferir B", natureza=a.CONFERIR, responsavel=a.CONFERE, perfil_id=perfil_b),
        # Ao Gestor a derivação diz "sua" a condução inteira; a alocação não a alcança.
        prov("Emitir a ordem", perfil_id=perfil_a),
    ]
    assert [i.ato for i in at.da_conferencia(itens, {perfil_a})] == ["Conferir A"]
    assert [i.ato for i in at.da_conferencia(itens, None)] == ["Conferir A", "Conferir B"]


def test_a_espera_entra_qualquer_que_seja_o_papel_seguinte_menos_a_formalizacao():
    itens = [
        prov(
            "Publicar o resultado definitivo",
            natureza=a.RESULTADO,
            situacao=a.AGUARDA,
            responsavel=a.PUBLICA,
            sua=False,
            razao="O prazo de recurso aberto pela publicação corre até 17/11/2026",
        ),
        prov("Congelar a relação", situacao=a.IMPEDIDO, sua=False, quem_resolve=a.RETIFICA),
        prov("Exportar", natureza=a.FORMALIZACAO, situacao=a.AGUARDA, sua=False),
        prov("Emitir a ordem"),
    ]
    atos = [item.ato for item in at.esperas(itens)]
    assert atos == ["Publicar o resultado definitivo", "Congelar a relação"]


# --- o agrupamento entre Editais (R-006) ----------------------------------------------------


def test_o_mesmo_ato_sem_numero_junta_entre_editais():
    um, dois, tres = edital(1), edital(2), edital(3)
    vazia = prov(a.ATO_DA_ORDEM_VAZIA, lista_vazia=True)
    grupos = at.agrupar_entre_editais(
        [linha(vazia, um), linha(prov("Emitir o corte"), dois), linha(vazia, tres)]
    )
    assert [(g.ato, g.quantos_editais) for g in grupos] == [
        (a.ATO_DA_ORDEM_VAZIA, 2),
        ("Emitir o corte", 1),
    ]
    assert [e.number for e in grupos[0].editais] == ["1", "3"]


def test_o_ato_com_numero_nunca_junta_nem_com_o_mesmo_numero():
    um, dois = edital(1), edital(2)
    convocar = prov("Convocar 3 titulares", natureza=a.CONVOCACAO)
    grupos = at.agrupar_entre_editais([linha(convocar, um), linha(convocar, dois)])
    assert [g.quantos_editais for g in grupos] == [1, 1]


def test_a_lista_vazia_nao_junta_com_a_lista_com_inscritos():
    um, dois = edital(1), edital(2)
    grupos = at.agrupar_entre_editais(
        [linha(prov("Emitir a ordem"), um), linha(prov("Emitir a ordem", lista_vazia=True), dois)]
    )
    assert len(grupos) == 2


def test_as_esperas_juntam_pela_razao_inteira_com_a_data():
    um, dois, tres = edital(1), edital(2), edital(3)

    def espera(data):
        return prov(
            "Publicar o resultado definitivo",
            natureza=a.RESULTADO,
            situacao=a.AGUARDA,
            responsavel=a.PUBLICA,
            sua=False,
            razao=f"O prazo de recurso aberto pela publicação corre até {data}",
        )

    grupos = at.agrupar_entre_editais(
        [
            linha(espera("17/11/2026"), um),
            linha(espera("17/11/2026"), dois),
            linha(espera("20/11/2026"), tres),
        ],
        espera=True,
    )
    assert [g.quantos_editais for g in grupos] == [2, 1]


# --- a ordem (R-007) ------------------------------------------------------------------------


def test_o_obsoleto_vem_primeiro_depois_o_edital_mais_antigo_e_a_data_nao_ordena():
    antigo, novo = edital(5, 2025), edital(1, 2026)
    cedo = datetime(2026, 11, 13, tzinfo=BRT)
    linhas = [
        linha(prov("Convocar 2 titulares", natureza=a.CONVOCACAO, ate=cedo), novo, indice=0),
        linha(prov("Emitir o corte"), antigo, indice=1),
        linha(prov("Emitir a ordem"), antigo, indice=0),
        linha(prov("Emitir a ordem sucessora", situacao=a.OBSOLETO), novo, indice=3),
    ]
    atos = [item.providencia.ato for item in at.ordenar(linhas)]
    assert atos == [
        "Emitir a ordem sucessora",
        "Emitir a ordem",
        "Emitir o corte",
        "Convocar 2 titulares",
    ]


# --- a avaliação pela carga (R-005) ----------------------------------------------------------


def test_a_avaliacao_sai_da_carga_com_a_frase_do_andamento_e_o_numero_da_mesa():
    ed = edital(7)
    etapa = uuid.uuid4()
    atribuicoes = [
        {"edital": ed, "etapa_id": etapa, "nome": "Prova objetiva"},
        {"edital": ed, "etapa_id": uuid.uuid4(), "nome": "Entrevista"},
    ]
    carga = {(ed.id, str(etapa)): {"pendentes": 5, "concluidas": 0, "total": 5}}
    linhas = at.linhas_de_avaliacao(atribuicoes, carga)
    assert len(linhas) == 1
    item = linhas[0].providencia
    assert item.ato == a.ato_de_avaliar(5) == "Avaliar 5 inscrições"
    assert item.url == f"/gestao/minhas-etapas/{ed.id}/{etapa}"
    assert linhas[0].base == at.ALOCACAO
    assert linhas[0].fase == c.NOMES[c.AVALIACAO]


# --- a marca só quando distingue (FR-6885) e o filtro por Edital (FR-6886) ------------------------


def test_com_uma_base_so_a_marca_vai_para_o_titulo():
    um = edital(1)
    so_presidencia = at.Atividades(para_fazer=at.agrupar_entre_editais([linha(prov("Emitir"), um)]))
    assert so_presidencia.base_unica == at.PRESIDENCIA
    assert so_presidencia.base_no_titulo == "pela presidência"

    misturada = at.Atividades(
        para_fazer=at.agrupar_entre_editais(
            [linha(prov("Emitir"), um), linha(prov("Conferir"), um, base=at.ALOCACAO)]
        )
    )
    assert misturada.base_unica == ""
    assert misturada.base_no_titulo == ""


def atividades_em_dois_editais():
    um, dois = edital(1), edital(2)
    vazia = prov(a.ATO_DA_ORDEM_VAZIA, lista_vazia=True)
    espera = prov("Publicar", situacao=a.AGUARDA, sua=False, razao="até 17/11/2026")
    return (
        at.Atividades(
            para_fazer=at.agrupar_entre_editais(
                [linha(vazia, um), linha(vazia, dois), linha(prov("Emitir o corte"), dois)]
            ),
            em_espera=at.agrupar_entre_editais([linha(espera, um, base=at.SEM_BASE)], espera=True),
        ),
        um,
        dois,
    )


def test_o_filtro_mostra_so_o_edital_escolhido_e_o_grupo_so_com_ele():
    atividades, um, dois = atividades_em_dois_editais()
    filtrada, opcoes, escolhido = at.filtrar(atividades, str(dois.id))

    assert escolhido == str(dois.id)
    assert [(o.edital.number, o.atos) for o in opcoes] == [("1", 1), ("2", 2)]
    assert [(g.ato, g.quantos_editais) for g in filtrada.para_fazer] == [
        (a.ATO_DA_ORDEM_VAZIA, 1),
        ("Emitir o corte", 1),
    ]
    assert filtrada.em_espera == []


def test_valor_invalido_ou_de_edital_alheio_mostra_tudo():
    atividades, _, _ = atividades_em_dois_editais()
    for valor in ("", None, "nao-e-uuid", str(uuid.uuid4())):
        filtrada, opcoes, escolhido = at.filtrar(atividades, valor)
        assert filtrada is atividades
        assert escolhido == ""
        assert len(opcoes) == 2


def test_o_edital_mais_antigo_vem_primeiro_em_ordem_natural():
    """Revisão do #511: em ordem de texto, o 10/2026 vinha antes do 9/2026."""
    nove, dez, sim5, sim12 = edital("9"), edital("10"), edital("SIM05"), edital("SIM12")
    linhas = [linha(prov(f"Ato {e.number}"), e) for e in (sim12, dez, sim5, nove)]
    assert [li.edital.number for li in at.ordenar(linhas)] == ["9", "10", "SIM05", "SIM12"]
