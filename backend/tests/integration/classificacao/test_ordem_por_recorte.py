"""A ordem de cada recorte: raiz, sucessão e confirmação próprias (034, US1).

**O que este arquivo prende é a independência das cadeias.** As três ordens de um marco nascem do
mesmo cálculo e da mesma versão normativa, e é natural tratá-las como uma coisa só — tratá-las assim
faria uma sucessão num recorte revogar em silêncio duas ordens que ninguém decidiu revogar.
Publicação é ato imutável, e revogação por efeito colateral é a maneira mais discreta de violá-lo.

Os casos estão na ordem em que as tarefas os pediram — não-atravessamento, confirmação cruzada,
universo, leitura pura, contraprova do sorteio, ordem vazia e os dois casos de borda —, e cada um
diz qual obrigação do contrato `specs/034-ordem-por-recorte/contracts/ordem-por-recorte.md` ele
responde.
"""

import pytest

from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    confirmacao_do_recorte,
    emitir_recorte,
    montar_cenario_7_1_2,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Edital 7/1/2 com a ordem da **ampla** já emitida, e os dois recortes ainda sem ordem."""
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034",
    )


def atos(edital, lista_id):
    return list(
        AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO, lista_id=lista_id).order_by(
            "emitido_em"
        )
    )


# --- T016 · Emitir num recorte não constitui ato sobre os outros (FR-494, obrigação 1) ----------


def test_a_ordem_do_recorte_reservado_nasce_com_a_lista_daquele_recorte(cenario, gestor):
    """`FR-490`: raiz própria, e a coluna que a identifica é a do recorte."""
    edital, _, _ = cenario

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-ppi")

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    assert ato is not None
    assert str(ato.lista_id) == MODALIDADE_PPI
    assert ato.ato_anterior is None, "é raiz do próprio recorte, e não sucessor do ato da ampla"


def test_emitir_no_recorte_reservado_nao_toca_a_ordem_da_ampla(cenario, gestor):
    """A obrigação 1, no caso que a auditoria descreveu: o vigente do outro recorte não se move."""
    edital, _, _ = cenario
    da_ampla_antes = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-ppi-nao-toca")
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-pcd-nao-toca")

    da_ampla_depois = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)
    assert da_ampla_depois is not None
    assert da_ampla_depois.id == da_ampla_antes.id
    assert da_ampla_depois.ato_anterior_id is None
    assert not da_ampla_depois.sucessores.exists(), "nada o sucedeu, e nada o obsoletou"


def test_suceder_num_recorte_nao_obsoleta_os_outros(cenario, gestor):
    """A obsolescência é por cadeia, e a cadeia é do recorte.

    **É o caso que mais convida ao erro.** Um filtro de vigente sem lista escolheria uma das três
    raízes pela ordem de emissão, e a sucessão de PPI apareceria como sucessão da ampla.
    """
    edital, _, _ = cenario
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-ppi-raiz")
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-pcd-raiz")

    emitir_recorte(
        edital,
        gestor,
        lista_id=MODALIDADE_PPI,
        chave="034-ppi-sucessor",
        motivo="Recurso deferido na lista de PPI.",
    )

    assert len(atos(edital, MODALIDADE_PPI)) == 2
    assert len(atos(edital, MODALIDADE_PCD)) == 1, "o outro recorte não ganhou sucessor"
    assert len(atos(edital, None)) == 1, "nem a ampla"
    assert (
        ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PCD).sucessores.count() == 0
    )


def test_cada_recorte_tem_uma_raiz_e_as_tres_convivem(cenario, gestor):
    """Três listas, três atos raiz, um marco só — a forma que a `021` já descrevia por escrito."""
    edital, _, _ = cenario

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-tres-ppi")
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-tres-pcd")

    raizes = AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO, ato_anterior__isnull=True)
    assert raizes.count() == 3
    assert {str(item.lista_id) if item.lista_id else None for item in raizes} == {
        None,
        MODALIDADE_PCD,
        MODALIDADE_PPI,
    }


# --- T017 · A confirmação do cálculo é do recorte (FR-495, obrigação 2) -------------------------


def test_confirmar_num_recorte_e_emitir_no_outro_e_recusado(cenario, gestor):
    """`FR-495`: a leitura feita em A não confirma a emissão em B.

    Sem isso, o operador emitiria a ordem certa com a conferência errada, e nada acusaria.
    """
    from processo_seletivo.classificacao.application.emissao import emitir_ordem

    edital, _, _ = cenario
    lida_em_ppi = confirmacao_do_recorte(edital, lista_id=MODALIDADE_PPI)

    with pytest.raises(DomainError) as recusa:
        emitir_ordem(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=MODALIDADE_PCD,
            idempotency_key="034-cruzada",
            correlation_id="teste-recortes-034",
            confirmacao_do_calculo=lida_em_ppi,
        )

    assert recusa.value.code == "stale_ordering_calculation"
    assert atos(edital, MODALIDADE_PCD) == [], "e nada foi gravado no recorte errado"


def test_dois_recortes_vazios_do_mesmo_marco_nao_compartilham_confirmacao(
    gestor, api_client, manager_headers, process_payload
):
    """O caso que torna a `FR-495` indispensável, e não apenas prudente.

    Dois recortes reservados **sem nenhum autodeclarado** produzem universo e ordem idênticos: sem o
    recorte na assinatura, as duas confirmações seriam byte a byte a mesma, e a leitura de um
    autorizaria a emissão do outro.
    """
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034-vazios",
        autodeclarar=False,
    )

    assert confirmacao_do_recorte(edital, lista_id=MODALIDADE_PPI) != confirmacao_do_recorte(
        edital, lista_id=MODALIDADE_PCD
    )


def test_a_mesma_chave_de_idempotencia_nao_serve_a_dois_recortes(cenario, gestor):
    """O recorte está no payload do comando: a segunda emissão é conflito, e não repetição.

    Lida como repetição, ela devolveria o desfecho da primeira — e um recorte ficaria sem ato, sem
    que nada acusasse.
    """
    edital, _, _ = cenario
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-mesma-chave")

    with pytest.raises(DomainError) as recusa:
        emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-mesma-chave")

    assert recusa.value.status == 409
    assert atos(edital, MODALIDADE_PCD) == []


# --- T018 · O universo emitido de cada recorte (D-001, FR-492) ----------------------------------


def test_a_ordem_da_ampla_emitida_contem_os_autodeclarados(cenario):
    """`D-001` gravado no ato, e não só calculado: a ampla é o universo inteiro do Perfil."""
    edital, _, inscricoes = cenario

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)
    gravadas = set(
        PosicaoNaOrdem.objects.filter(ato=ato).values_list("inscricao__protocolo", flat=True)
    )

    assert gravadas == {item.protocolo for item in inscricoes}


def test_a_ordem_do_recorte_reservado_emitida_contem_so_os_autodeclarados_dele(cenario, gestor):
    """A outra metade do `D-001`: a cota ordena quem declarou **aquela** Modalidade."""
    edital, _, inscricoes = cenario

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-universo-ppi")

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    gravadas = set(
        PosicaoNaOrdem.objects.filter(ato=ato).values_list("inscricao__protocolo", flat=True)
    )
    assert gravadas == {inscricoes[2].protocolo, inscricoes[4].protocolo}


def test_o_universo_gravado_no_ato_do_recorte_e_o_daquele_recorte(cenario, gestor):
    """A proveniência acompanha o recorte: o ato cita os Resultados que **ele** leu."""
    edital, _, inscricoes = cenario

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-universo-prov")

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    assert set(ato.universo["participants"]) == {
        str(inscricoes[2].id),
        str(inscricoes[4].id),
    }


# --- T019 · Abrir a tela não constitui ato (FR-496, obrigação 3) --------------------------------


def test_ler_os_tres_recortes_repetidamente_nao_constitui_ato(cenario):
    """Abrir três telas não pode produzir três atos, nem um."""
    from processo_seletivo.classificacao.application.selectors import estado_do_marco

    edital, _, _ = cenario
    antes = AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO).count()

    for _ in range(3):
        for recorte in (None, MODALIDADE_PCD, MODALIDADE_PPI):
            estado_do_marco(edital=edital, marco_id=MARCO, lista_id=recorte)

    assert AtoDeOrdenacao.objects.filter(edital=edital, marco_id=MARCO).count() == antes
    assert antes == 1, "a premissa: só a ordem da ampla, emitida ao montar o cenário"


def test_a_leitura_do_recorte_sem_ordem_nao_cria_ato_vazio(cenario):
    """Ler o recorte que ninguém emitiu devolve proposta e vigente nulo — e grava nada."""
    from processo_seletivo.classificacao.application.selectors import estado_do_marco

    edital, _, _ = cenario

    estado = estado_do_marco(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PCD)

    assert estado["vigente"] is None
    assert estado["proposta"] is not None
    assert atos(edital, MODALIDADE_PCD) == []


# --- T020 · O marco que sorteia continua indo pelo caminho do sorteio ---------------------------


def test_marco_que_sorteia_recusa_a_emissao_computada_em_todos_os_recortes(
    gestor, api_client, manager_headers, process_payload
):
    """Cenário de aceitação 4 da `US1`, e ele não era prendido por nada.

    A recusa de `emitir_ordem` é anterior a esta feature; o que se prende aqui é que a emissão por
    recorte **não a contornou** — nem pela ampla, nem por uma lista reservada. O dano que ela impede
    é irreversível: o ato sairia com `origem=COMPUTADO` ocupando uma raiz que o sorteio precisa, e
    `constituir_sorteio` recusaria o certame inteiro dali em diante. A tabela é append-only, e a
    sucessão de uma ordem sorteada nasce da anulação de um sorteio que, nesse caminho, nunca chegou
    a existir.
    """
    from processo_seletivo.classificacao.application.emissao import emitir_ordem
    from tests.fixtures.sorteio import LISTA_PPI, certame_com_cotas

    certame = certame_com_cotas(gestor, api_client, manager_headers, process_payload)

    for recorte, chave in ((None, "034-sorteio-ampla"), (LISTA_PPI, "034-sorteio-ppi")):
        with pytest.raises(DomainError) as recusa:
            emitir_ordem(
                actor=gestor,
                processo_id=certame["processo"].id,
                edital_id=certame["edital"].id,
                perfil_id=certame["perfil"],
                marco_id=certame["marco"],
                lista_id=recorte,
                idempotency_key=chave,
                correlation_id="teste-recortes-034",
                confirmacao_do_calculo="qualquer",
            )
        assert recusa.value.code == "ordering_milestone_is_drawn", recorte

    assert (
        AtoDeOrdenacao.objects.filter(edital=certame["edital"], marco_id=certame["marco"]).count()
        == 0
    ), "nenhuma raiz foi ocupada"


# --- T021 · A ordem vazia do recorte sem nenhum autodeclarado (FR-492a) -------------------------


def test_recorte_sem_autodeclarado_admite_ordem_vazia_emitida(
    gestor, api_client, manager_headers, process_payload
):
    """`FR-492a`: existe um ato que **declara a ausência**, e ele é publicável.

    Sem ele, "ninguém se inscreveu por esta cota" e "ainda não emitiram" são indistinguíveis na
    tela — e a diferença entre as duas é quem tem trabalho a fazer.
    """
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034-vazia",
        autodeclarar=False,
    )

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-vazia")

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PCD)
    assert ato is not None
    assert PosicaoNaOrdem.objects.filter(ato=ato).count() == 0
    assert ato.universo["participants"] == []


def test_a_ordem_vazia_nunca_e_automatica(gestor, api_client, manager_headers, process_payload):
    """Emitir continua sendo **ato de quem conduz**, e o que muda é que passa a haver o que emitir.

    Um ato que nascesse sozinho seria o sistema declarando um fato normativo por conta própria — e
    seria a Constituição violada por conveniência de tela.
    """
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034-sem-ato",
        autodeclarar=False,
    )

    assert atos(edital, MODALIDADE_PCD) == []
    assert ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PCD) is None


# --- T022 · Os dois casos de borda --------------------------------------------------------------


def test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla(cenario, gestor):
    """`FR-494a`: o recorte novo nasce sem ordem, e a ordem da ampla **continua vigente**.

    A razão é a `FR-492`, e não uma escolha nova: o universo da ampla é todo mundo, e acrescentar
    uma Modalidade não retira nem acrescenta ninguém a ele. A ordem que foi emitida continua sendo a
    daquele universo, sob a norma que o ato citou.

    *A Retificação em si é exercitada pelo percurso do `quickstart` 5.2; o que se prende aqui é a
    regra de vigência — que o ato da ampla não ganha sucessor nem obsolescência por causa de um
    recorte que passou a existir.*
    """
    edital, _, _ = cenario
    da_ampla = ato_vigente(edital=edital, marco_id=MARCO, lista_id=None)

    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="034-nova-modalidade")

    da_ampla.refresh_from_db()
    assert not da_ampla.sucessores.exists()
    assert ato_vigente(edital=edital, marco_id=MARCO, lista_id=None).id == da_ampla.id


def test_o_empate_residual_atravessa_quando_o_par_inteiro_esta_no_recorte(
    gestor, api_client, manager_headers, process_payload
):
    """O mesmo candidato pode estar empatado nas duas ordens, e o julgamento vale para as duas.

    **Vale porque é o mesmo cálculo.** O empate residual é propriedade da pontuação e dos critérios
    publicados do marco, e não do recorte: os critérios são oferecidos na mesma ordem em todos, e
    declarar um que separe o empate o separa dos dois lados.

    O cenário põe **os dois autodeclarados de PPI com a mesma pontuação**, que é o caso de que a
    spec fala — e é a única forma de o empate existir nas duas ordens.
    """
    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034-empate",
        pontuacoes=("95.0000", "90.0000", "85.0000", "80.0000", "85.0000"),
    )
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-empate-ppi")

    empatados_na_ampla = _empatados(ato_vigente(edital=edital, marco_id=MARCO, lista_id=None))
    empatados_em_ppi = _empatados(
        ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    )
    o_par = {inscricoes[2].protocolo, inscricoes[4].protocolo}

    assert o_par <= empatados_na_ampla, "a premissa: os dois empatam na ampla"
    assert o_par <= empatados_em_ppi, "e o empate atravessa inteiro para o recorte"


def test_o_empate_entre_um_cotista_e_um_nao_cotista_nao_atravessa(
    gestor, api_client, manager_headers, process_payload
):
    """E a metade que a redação da spec não diz, medida aqui: **o empate é do grupo**.

    Quando só uma das pessoas empatadas concorre pela cota, não há com quem empatar dentro do
    recorte — e a posição lá é única. Não é divergência entre a regra escrita e a regra do código:
    é a mesma regra, aplicada ao universo de cada recorte, que é o que a `FR-492` define. Registrar
    isso importa porque a leitura natural de "o julgamento vale para as duas" sugere que a pastilha
    acompanha a pessoa, e ela acompanha o **grupo**.
    """
    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-recorte-034-empate-solo",
        pontuacoes=("95.0000", "90.0000", "85.0000", "85.0000", "75.0000"),
    )
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="034-empate-solo-ppi")

    empatados_na_ampla = _empatados(ato_vigente(edital=edital, marco_id=MARCO, lista_id=None))
    empatados_em_ppi = _empatados(
        ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PPI)
    )

    assert inscricoes[2].protocolo in empatados_na_ampla, (
        "a premissa: empata com o quarto, na ampla"
    )
    assert inscricoes[3].protocolo in empatados_na_ampla
    assert empatados_em_ppi == set(), "e no recorte ele está sozinho na sua pontuação"


def _empatados(ato):
    return set(
        PosicaoNaOrdem.objects.filter(ato=ato, empate_residual=True).values_list(
            "inscricao__protocolo", flat=True
        )
    )
