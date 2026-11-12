"""A declaração de vaga não preenchida (155, T031, US2, FR-6323 a FR-6327, contrato).

O cenário é a V-1 da verificação, com o Perfil **sem reversão declarada** — o C09: o único cotista
PPI desiste, e a reserva fica sem quem a ocupe e sem para onde ir. Os fatos externos chegam por um
*callable* fixo, que é o que o ato recebe: a composição deles pela interface tem os seus casos em
`test_condicao_do_esgotamento.py`, sobre a publicação de verdade.
"""

import pytest
from django.db import IntegrityError

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.destinacao import (
    declarar_nao_preenchida,
    previa_da_nao_preenchida,
)
from processo_seletivo.ocupacao.domain import destinacao, nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_concomitancia import apurar
from tests.integration.ocupacao.test_condicao_do_esgotamento import (
    DEFINITIVO,
    definitivo,
    efeito,
    esgotado,
)

pytestmark = pytest.mark.django_db(transaction=True)

FUNDAMENTO = "O Edital não declara reversão, e a lista da cota não tem mais quem a ocupe."


@pytest.fixture
def silente(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return esgotado(gestor, api_client, manager_headers, process_payload, "np-155", reversao=None)


def previa(certame, *, lista_id=LISTA_PPI, fatos=DEFINITIVO):
    return previa_da_nao_preenchida(
        edital=certame["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        fatos_externos=fatos,
    )


def declarar(
    certame,
    gestor,
    *,
    lista_id=LISTA_PPI,
    chave="np-155-ato",
    fundamento=FUNDAMENTO,
    assinatura=None,
    fatos=DEFINITIVO,
):
    return declarar_nao_preenchida(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        fundamento=fundamento,
        assinatura=(
            assinatura
            if assinatura is not None
            else previa(certame, lista_id=lista_id, fatos=fatos)["assinatura"]
        ),
        fatos_externos=fatos,
        idempotency_key=chave,
        correlation_id="teste-155-np",
    )


def recusa(certame, gestor, **kwargs):
    with pytest.raises(DomainError) as erro:
        declarar(certame, gestor, **kwargs)
    return erro.value


def vigente(certame, lista_id=LISTA_PPI):
    return selectors.apuracao_vigente(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )


def sem_ninguem_na_ampla(certame, gestor, prefixo):
    """Todos da ordem da ampla saem por desfecho, e a ampla é apurada de novo: ninguém a ocupa."""
    for inscricao in certame["inscricoes"]:
        efeito(certame, inscricao, nomes.EFEITO_EXCLUSAO, lista_id=None)
    apurar(certame, gestor, chave=f"{prefixo}-ampla-vazia", motivo="Ninguém mais na ampla")


class TestNaReservaSemReversao:
    def test_registra_o_recorte_a_quantidade_o_fundamento_e_a_versao(self, silente, gestor):
        """FR-6325: ator, instante, recorte, quantidade, fundamento e a versão do Edital."""
        conferencia = previa(silente)
        assert conferencia["recusa"] is None
        assert conferencia["situacao"]["estado"] == destinacao.NAO_PREENCHIDA_DISPONIVEL
        lida = conferencia["apuracao"]

        declarado = declarar(silente, gestor)

        registro = VagaNaoPreenchida.objects.get()
        assert declarado["quantidade"] == registro.quantidade == 1
        assert registro.especie == nomes.NAO_PREENCHIDA_DECLARACAO
        assert (str(registro.lista_id), str(registro.perfil_id)) == (LISTA_PPI, PROFILE_ID)
        assert registro.fundamento == FUNDAMENTO
        assert registro.versao_id == conferencia["versao"].id
        assert registro.apuracao_id == lida.id
        assert registro.registrado_por == gestor.subject
        assert MovimentoDeVaga.objects.count() == 0, "FR-6320: nada move a vaga"

    def test_faltando_desconta_e_as_efetivas_ficam(self, silente, gestor):
        """FR-6326: a vaga deixa de contar como a ocupar, e a quantidade não muda."""
        antes = vigente(silente)

        declarado = declarar(silente, gestor)

        seguinte = declarado["apuracaoSeguinte"]
        assert seguinte is not None, declarado["apuracaoPendente"]
        depois = ApuracaoDeOcupacao.objects.get(id=seguinte["id"])
        assert (depois.publicadas, depois.efetivas) == (antes.publicadas, antes.efetivas)
        assert (depois.nao_preenchidas, depois.faltando) == (1, 0)
        assert seguinte["universo"]["naoPreenchidasLidas"] == [
            str(VagaNaoPreenchida.objects.get().id)
        ]
        leitura = selectors.ocupacao_do_recorte(
            edital=silente["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=LISTA_PPI
        )
        assert (leitura["estado"], leitura["faltando"]) == (nomes.VIGENTE, 0)

    def test_a_apuracao_lida_fica_obsoleta_pela_declaracao(self, silente, gestor):
        """A sétima causa: a apuração que não leu a declaração está para trás."""
        lida = vigente(silente)

        declarar(silente, gestor)

        causas = {c["causa"] for c in selectors.causas_de_obsolescencia(lida)}
        assert nomes.CAUSA_DECLARACAO_POSTERIOR in causas

    def test_a_trilha_registra_o_ato(self, silente, gestor):
        declarar(silente, gestor)

        registro = RegistroAuditoria.objects.get(operation="OCUPACAO_DECLARAR_NAO_PREENCHIDA")
        assert registro.correlation_id == "teste-155-np"
        assert FUNDAMENTO in registro.reason

    def test_a_repeticao_devolve_o_mesmo_desfecho(self, silente, gestor):
        assinatura = previa(silente)["assinatura"]
        primeira = declarar(silente, gestor, assinatura=assinatura)

        assert declarar(silente, gestor, assinatura=assinatura) == primeira
        assert VagaNaoPreenchida.objects.count() == 1


class TestNaLinhaGeral:
    def test_a_ampla_sem_ninguem_que_a_ocupe(self, silente, gestor):
        """D-014, FR-6324: a linha geral sem quem a ocupe admite a declaração."""
        sem_ninguem_na_ampla(silente, gestor, "np-geral")
        assert previa(silente, lista_id=None)["recusa"] is None

        declarado = declarar(silente, gestor, lista_id=None, chave="np-geral-ato")

        registro = VagaNaoPreenchida.objects.get()
        assert registro.lista_id is None
        assert declarado["quantidade"] == 1
        assert vigente(silente, None).faltando == 0

    def test_a_ampla_que_recebeu_a_vaga_revertida(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        """D-014, FR-6324: inclusive a que recebeu vaga da reserva — a vaga recebida também é
        declarável. Nesta entrega quem a leva é a apuração da reserva, pela reversão por saldo e
        pela regra de antes da `155`: a desistência deixa o saldo, e a emissão o cede."""
        certame = esgotado(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            "np-recebida",
            reversao=nomes.REVERSAO_POR_SALDO,
        )
        assert MovimentoDeVaga.objects.count() == 1, "a apuração da reserva cedeu a vaga"
        sem_ninguem_na_ampla(certame, gestor, "np-recebida")
        assert vigente(certame, None).efetivas == 2

        declarado = declarar(certame, gestor, lista_id=None, chave="np-recebida-ato")

        assert declarado["quantidade"] == 2
        assert vigente(certame, None).faltando == 0

    def test_a_ampla_com_quem_a_ocupe_recusa(self, silente, gestor):
        erro = recusa(silente, gestor, lista_id=None)
        assert erro.code == nomes.AINDA_HA_QUEM_OCUPAR


class TestRecusas:
    def test_sem_fundamento(self, silente, gestor):
        """US2.2: o comando recusa e pede o fundamento — e nada é gravado."""
        for vazio in ("", "   "):
            erro = recusa(silente, gestor, fundamento=vazio, chave=f"np-vazio-{len(vazio)}")
            assert (erro.code, erro.status) == (nomes.FUNDAMENTO_OBRIGATORIO, 422)
        assert VagaNaoPreenchida.objects.count() == 0

    @pytest.mark.parametrize("especie", nomes.ESPECIES_DE_REVERSAO)
    def test_o_edital_manda_destinar(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, especie
    ):
        """FR-6327: onde o Edital declara a reversão, a vaga da reserva não é declarada não
        preenchida — nas duas espécies, cuja reversão nesta entrega é a da apuração."""
        certame = esgotado(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            f"np-destina-{especie[:4].lower()}",
            reversao=especie,
        )
        erro = recusa(certame, gestor)
        assert erro.code == nomes.O_EDITAL_MANDA_DESTINAR
        assert "aplicada pela apuração" in erro.detail
        assert VagaNaoPreenchida.objects.count() == 0

    def test_ainda_ha_quem_ocupar(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        from tests.fixtures.ocupacao_sorteada import certame_sorteado_com_quadro
        from tests.integration.ocupacao.test_concomitancia import emitir_cortes
        from tests.integration.ocupacao.test_condicao_do_esgotamento import sem_concomitancia

        certame = certame_sorteado_com_quadro(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="np-quem",
            com_corte=True,
            quantos=8,
            geral=1,
        )
        emitir_cortes(certame, gestor)
        apurar(certame, gestor, chave="np-quem-ampla")
        sem_concomitancia(certame, certame["cotista_ppi"])
        apurar(certame, gestor, lista_id=LISTA_PPI, chave="np-quem-ppi")

        erro = recusa(certame, gestor)

        assert erro.code == nomes.AINDA_HA_QUEM_OCUPAR
        assert "1 pessoa" in erro.detail

    def test_impedida(self, silente, gestor):
        """As condições e os impedimentos da FR-6300 (FR-6323)."""
        erro = recusa(silente, gestor, fatos=definitivo(natureza_do_resultado="PRELIMINAR"))
        assert erro.code == nomes.DESTINACAO_IMPEDIDA
        assert "não é definitivo" in erro.detail

    def test_sem_saldo_depois_de_declarada(self, silente, gestor):
        assinatura = previa(silente)["assinatura"]
        declarar(silente, gestor, assinatura=assinatura)

        erro = recusa(silente, gestor, chave="np-155-ato-2", assinatura=assinatura)

        assert erro.code == nomes.SEM_SALDO_A_DESTINAR
        assert VagaNaoPreenchida.objects.count() == 1

    def test_leitura_mudada(self, silente, gestor):
        assert recusa(silente, gestor, assinatura="outra").code == nomes.LEITURA_DO_RECORTE_MUDOU


class TestOLimiteDasVagas:
    def test_a_inclusao_posterior_e_recusada_pelo_nome_e_nao_pela_constraint(self, silente, gestor):
        """R-002: `ocupadas + nao_preenchidas <= efetivas` recusado antes do banco.

        Declarada a vaga, a pessoa volta por um efeito de inclusão: a apuração seguinte contaria 1
        ocupada e 1 não preenchida sobre 1 efetiva. A emissão recusa com o código nomeado, e nada é
        rebaixado em silêncio.
        """
        declarar(silente, gestor)
        apuracoes = ApuracaoDeOcupacao.objects.count()
        efeito(silente, silente["cotista_ppi"], nomes.EFEITO_INCLUSAO)

        try:
            with pytest.raises(DomainError) as erro:
                apurar(silente, gestor, lista_id=LISTA_PPI, chave="np-limite", motivo="Retorno")
        except IntegrityError:  # pragma: no cover - é o defeito que este teste prende
            pytest.fail("a emissão chegou à constraint em vez de recusar pelo nome")

        assert erro.value.code == nomes.NAO_PREENCHIDAS_ALEM_DAS_VAGAS
        assert "Desfaça a declaração" in erro.value.detail
        assert ApuracaoDeOcupacao.objects.count() == apuracoes

    def test_a_reversao_retificada_nao_cede_a_vaga_declarada(self, silente, gestor, api_client):
        """R-002: retificado o Edital para declarar a reversão por saldo, a apuração seguinte não
        cede a vaga declarada não preenchida — cedê-la seria desfazer a declaração sem ato, e
        contá-la ainda passaria das vagas. A reversão alcança só o que sobra; aqui, nada."""
        from tests.fixtures.publicacao import retify

        declarar(silente, gestor)
        retify(
            api_client,
            silente["edital"],
            [
                {
                    "targetPath": f"/profiles/id={PROFILE_ID}/vacancyReversion",
                    "operation": "REPLACE",
                    "newValue": {"kind": nomes.REVERSAO_POR_SALDO},
                }
            ],
            suffix="np155saldo",
        )

        apurado = apurar(
            silente, gestor, lista_id=LISTA_PPI, chave="np-saldo", motivo="Reversão retificada"
        )

        assert apurado["reverteu"] == 0
        assert MovimentoDeVaga.objects.count() == 0
        assert (vigente(silente).nao_preenchidas, vigente(silente).faltando) == (1, 0)


class TestReproducao:
    def test_relida_depois_da_retificacao_diz_o_que_leu(self, silente, gestor, api_client):
        """FR-6342: a Retificação declara a reversão; a declaração continua com a versão dela."""
        from tests.fixtures.publicacao import retify

        declarar(silente, gestor)
        registro = VagaNaoPreenchida.objects.get()
        lida = registro.versao

        retify(
            api_client,
            silente["edital"],
            [
                {
                    "targetPath": f"/profiles/id={PROFILE_ID}/vacancyReversion",
                    "operation": "REPLACE",
                    "newValue": {"kind": nomes.REVERSAO_POR_ESGOTAMENTO},
                }
            ],
            suffix="np155",
        )

        relido = VagaNaoPreenchida.objects.get(pk=registro.pk)
        hoje = previa(silente)
        assert hoje["declaracao"] == nomes.REVERSAO_POR_ESGOTAMENTO, "a declaração de hoje mudou"
        assert hoje["versao"].id != lida.id
        assert (relido.quantidade, relido.versao_id, relido.fundamento) == (1, lida.id, FUNDAMENTO)
        assert relido.apuracao.universo.get("vacancyReversion") is None, "a apuração que ele leu"
