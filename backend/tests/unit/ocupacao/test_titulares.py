"""Titular inicial, e o que os desfechos da `019` fazem com o número (019, `R-001`, `SC-093`).

**O que este arquivo prende é um defeito que não dava erro.** O cálculo anterior era
`min(|faixa ∩ habilitadas|, efetivas)`, e ele conta **capacidade**, não ocupação: enquanto
sobrassem habilitados na faixa, o número saturava no alvo. Com 40 vagas, faixa de 70 e 67
habilitadas, eram necessárias **28** desistências para ele se mover — e cada uma das 27 anteriores
era uma suplente promovida em silêncio.

Sem banco: o que entra são quantidades, uma sequência e os efeitos que a apuração congelou.
"""

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes

# O recorte do 77/2026: 40 vagas, faixa de 70 (alvo mais 30 suplentes), 67 habilitadas.
VAGAS = 40
FAIXA = [f"p{n:02d}" for n in range(1, 71)]
HABILITADAS = set(FAIXA) - {"p68", "p69", "p70"}


def ocupadas(*, efeitos=(), faixa=FAIXA, habilitadas=HABILITADAS, vagas=VAGAS, empates=None):
    _, _, quantas = apuracao.apurar(
        publicadas=vagas,
        progrediram_em_ordem=faixa,
        habilitadas=habilitadas,
        efeitos_lidos=efeitos,
        empates_residuais=empates,
    )
    return quantas


def excluir(quem):
    return (nomes.EFEITO_EXCLUSAO, quem)


def incluir(quem):
    return (nomes.EFEITO_INCLUSAO, quem)


class TestOCicloQueACC093Mede:
    """`SC-093`: uma desistência dá 39, e o aceite da suplente devolve 40 (`T007`).

    É o cenário inteiro da `§1.0` da spec, medido contra a função real — e é o que o número antigo
    não conseguia dizer: ele respondia 40 nas três linhas.
    """

    def test_sem_desfecho_o_numero_e_o_alvo(self):
        assert ocupadas() == VAGAS

    def test_uma_titular_desiste_e_o_numero_cai_um(self):
        assert ocupadas(efeitos=[excluir("p01")]) == 39

    def test_a_suplente_aceita_e_o_numero_volta(self):
        assert ocupadas(efeitos=[excluir("p01"), incluir("p41")]) == VAGAS

    def test_cinco_desistem_e_ninguem_aceitou_ainda(self):
        saidas = [excluir(f"p{n:02d}") for n in range(1, 6)]
        assert ocupadas(efeitos=saidas) == 35

    def test_vinte_e_sete_desistem(self):
        """O número antigo continuava em 40 aqui. Eram necessárias 28 para ele se mover."""
        saidas = [excluir(f"p{n:02d}") for n in range(1, 28)]
        assert ocupadas(efeitos=saidas) == 13


class TestNadaMudaOndeNaoHaDesfecho:
    """A contagem nova preserva o que os testes da `016` já prendem (`T008`).

    **Não é coincidência, é aritmética**: sem efeito, `len(titulares)` é
    `min(|elegíveis|, efetivas)` — exatamente o `min(cabem, efetivas)` que esta função
    substituiu. A janela recorta o mesmo número que a interseção contava.
    """

    def test_faixa_inteira_habilitada_ocupa_o_alvo(self):
        assert ocupadas(faixa=FAIXA, habilitadas=set(FAIXA)) == VAGAS

    def test_menos_habilitados_que_vagas_ocupa_o_que_ha(self):
        poucos = FAIXA[:10]
        assert ocupadas(faixa=FAIXA, habilitadas=set(poucos)) == 10

    def test_ninguem_habilitado_ocupa_zero(self):
        assert ocupadas(habilitadas=set()) == 0

    def test_eliminado_no_topo_abre_vaga_em_vez_de_promover_o_proximo(self):
        """**Três eliminados dentro do alvo deixam três vagas faltando** — e não três promovidos.

        A janela de titulares é recortada sobre a sequência que progrediu, **antes** de perguntar
        por habilitação. Quem é titular e foi eliminado não ocupa a vaga dele: ela aparece em
        `faltando`, e alguém precisa **chamar** o próximo para ocupá-la, com ato registrado.

        *Filtrar as habilitadas antes de recortar a janela é a promoção silenciosa vestida de
        conveniência: os três seguintes entram na contagem sem que ninguém os tenha convocado, e o
        certame anda sem que nenhum ato o tenha feito andar. Foi o defeito da primeira
        implementação desta feature, e é o mesmo que a `§1.0` mediu do outro lado.*
        """
        habilitadas = set(FAIXA) - {"p01", "p02", "p03"}

        assert ocupadas(habilitadas=habilitadas) == VAGAS - 3

    def test_eliminado_fora_do_alvo_nao_muda_nada(self):
        """A simetria da anterior: quem foi eliminado na suplência não ocupava vaga nenhuma."""
        habilitadas = set(FAIXA) - {"p50", "p51", "p52"}

        assert ocupadas(habilitadas=habilitadas) == VAGAS


class TestExclusaoDeQuemNaoEraTitular:
    """A suplente só entra na contagem depois de aceitar (`FR-278d`, `T009`)."""

    def test_excluir_suplente_nao_desconta_nada(self):
        """`p41` está na faixa e habilitou, mas não ocupava vaga: sair não abre vaga nenhuma."""
        assert ocupadas(efeitos=[excluir("p41")]) == VAGAS

    def test_excluir_quem_nem_estava_na_faixa_nao_desconta_nada(self):
        assert ocupadas(efeitos=[excluir("estranho")]) == VAGAS

    def test_duas_exclusoes_da_mesma_pessoa_nao_produzem_menos_dois(self):
        """O modo de errar aqui é subtrair contagem em vez de operar conjunto (`R-001`)."""
        assert ocupadas(efeitos=[excluir("p01"), excluir("p01")]) == 39

    def test_duas_inclusoes_da_mesma_pessoa_nao_produzem_mais_dois(self):
        assert ocupadas(efeitos=[excluir("p01"), incluir("p41"), incluir("p41")]) == VAGAS

    def test_a_inclusao_nao_ultrapassa_o_teto(self):
        """`ocupadas <= efetivas` é constraint da `016`: o ato seria recusado no banco."""
        assert ocupadas(efeitos=[incluir("p41"), incluir("p42")]) == VAGAS

    def test_a_exclusao_depois_da_inclusao_vence(self):
        """A suplente aceitou e teve a matrícula cancelada por inércia depois (`D-011`, `US5`).

        É o caso em que a álgebra de conjuntos da `R-001`, lida ao pé da letra, erraria: a união
        com os incluídos venceria a exclusão qualquer que fosse a ordem dos atos, e a pessoa
        continuaria contada como ocupante de uma vaga que ela deixou.
        """
        efeitos = [excluir("p01"), incluir("p41"), excluir("p41")]
        assert ocupadas(efeitos=efeitos) == 39


class TestOEmpateQueAtravessaAFronteiraDoAlvo:
    """A apuração recusa determinar titulares em vez de escolher (019, `R-002`, `T006`).

    A `014` trata o empate na última posição **da faixa**; esta é outra fronteira, e para ela a
    norma publicada não diz nada. Incluir todos faria `ocupadas > efetivas`; escolher por ordem de
    chegada inventaria desempate.
    """

    def test_empate_metade_dentro_metade_fora_recusa(self):
        with pytest.raises(apuracao.EmpateNaFronteiraDoAlvo) as erro:
            ocupadas(empates={"p40": 40, "p41": 40})
        assert erro.value.posicao == 40
        assert erro.value.quantas == 2

    def test_o_codigo_da_recusa_e_o_do_contrato(self):
        assert apuracao.EmpateNaFronteiraDoAlvo.codigo == nomes.EMPATE_NA_FRONTEIRA_DO_ALVO
        assert nomes.EMPATE_NA_FRONTEIRA_DO_ALVO == "empate_na_fronteira_do_alvo"

    def test_empate_inteiramente_dentro_do_alvo_nao_recusa(self):
        """Os dois ocupam vaga. Não há o que julgar para saber quem é titular."""
        assert ocupadas(empates={"p10": 10, "p11": 10}) == VAGAS

    def test_empate_inteiramente_fora_do_alvo_nao_recusa(self):
        """É empate entre suplentes, e a `014` já decide a fronteira da faixa."""
        assert ocupadas(empates={"p50": 50, "p51": 50}) == VAGAS

    def test_empate_entre_eliminados_nao_recusa(self):
        """**A recusa só alcança o empate que muda o número.**

        Entre duas pessoas eliminadas na Etapa governada, tanto faz qual delas é a titular: nenhuma
        ocupa vaga, e a contagem é a mesma nos dois cenários. Parar a apuração ali pediria um
        desempate que não decide coisa alguma — e o caminho de saída, julgar na `015`, seria
        trabalho pedido sem razão.
        """
        habilitadas = set(FAIXA) - {"p40", "p41"}

        assert ocupadas(habilitadas=habilitadas, empates={"p40": 40, "p41": 40}) == VAGAS - 1

    def test_empate_com_uma_habilitada_atravessando_recusa(self):
        """Basta **uma** habilitada no grupo para a escolha passar a decidir a contagem."""
        habilitadas = set(FAIXA) - {"p40"}

        with pytest.raises(apuracao.EmpateNaFronteiraDoAlvo):
            ocupadas(habilitadas=habilitadas, empates={"p40": 40, "p41": 40})

    def test_a_mensagem_nomeia_a_posicao_e_o_tamanho(self):
        """Quem lê precisa saber onde a ordem parou de separar, e quantos desempates julgar."""
        with pytest.raises(apuracao.EmpateNaFronteiraDoAlvo) as erro:
            ocupadas(empates={"p39": 39, "p40": 39, "p41": 39})
        assert "39" in str(erro.value)
        assert "3 participantes" in str(erro.value)


class TestNinguemAparecComoOcupanteSemAtoQueOSustente:
    """`SC-094`: fora dos titulares iniciais, só entra quem tem inclusão registrada.

    **É a garantia que impede a contagem de inventar ocupante.** Os titulares iniciais saem da ordem
    e da habilitação — fatos que a `015` e a `013` produziram. Qualquer pessoa além deles só aparece
    ocupando se um desfecho de aceite ou de regularização a tiver **incluído**, e a inclusão é ato
    registrado, com fundamento e proveniência.
    """

    def test_quem_nao_e_titular_so_ocupa_com_inclusao_registrada(self):
        suplente = "p41"

        sem_ato = apuracao.ocupantes(titulares=FAIXA[:VAGAS], efeitos_lidos=())
        com_ato = apuracao.ocupantes(titulares=FAIXA[:VAGAS], efeitos_lidos=[incluir(suplente)])

        assert suplente not in sem_ato
        assert suplente in com_ato

    def test_o_conjunto_de_ocupantes_sai_dos_titulares_mais_os_incluidos_e_de_mais_nada(self):
        """Não há caminho que acrescente alguém sem passar por `efeitos_lidos`.

        O modo de errar aqui seria a contagem derivar ocupante de outro fato — de estar na faixa, de
        ter sido convocado, de ter uma matrícula em algum lugar. Nenhum deles é ato registrado na
        porta, e nenhum deles entra.
        """
        titulares = FAIXA[:VAGAS]
        efeitos = [incluir("p41"), excluir("p01")]

        ocupantes = apuracao.ocupantes(titulares=titulares, efeitos_lidos=efeitos)

        esperado = {t for t in titulares if t != "p01"} | {"p41"}
        assert ocupantes == esperado
