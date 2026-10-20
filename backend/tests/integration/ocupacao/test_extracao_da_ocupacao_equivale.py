"""A linha de base das duas decisões que a `095` tira do caminho oficial (095, T003, D-005).

`selectors.ocupantes_da_ampla` e `movimento.ha_quem_ocupar` decidem sobre o que leem do banco, e a
prévia da classificação precisa das mesmas decisões sobre candidatos fictícios. A `095` as extrai
para o domínio; **este arquivo foi escrito antes da extração e passou contra o código de então**, e
é o que prova que ela não mudou nada.

**Ele prende também o que a `095` registrou como pendente, de propósito.** Dois comportamentos de
hoje não são confirmados pela norma — quem ocupa pela ampla não passa pelo filtro de habilitação
(R-002 da `095`), e "há quem ocupar" conta quem já ocupa pela ampla (DP-2 da `095`). Corrigi-los é
decisão do usuário; se um deles mudar de passagem numa refatoração, é aqui que reprova.

O empate residual na fronteira da ampla não aparece: o sorteio não produz empate, e a recusa é
coberta sobre a função pura em `tests/unit/ocupacao/test_ocupantes_pela_ampla.py`.
"""

import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.ocupacao.application import movimento, selectors
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO

pytestmark = pytest.mark.django_db(transaction=True)


def emitir_cortes(certame, gestor, prefixo):
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )

    for indice, lista in enumerate((None, LISTA_PPI)):
        proposta = calcular_corte(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
        )
        emitir_corte(
            actor=gestor,
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"{prefixo}-corte-{indice}",
            correlation_id="teste-extracao-095",
            confirmacao_do_calculo=assinatura_da_proposta(proposta),
        )


def habilitar(certame, inscricoes):
    versao = effective_version(edital_id=certame["edital"].id)
    for inscricao in inscricoes:
        ResultadoEtapa.objects.create(
            inscricao=inscricao,
            edital=certame["edital"],
            versao=versao,
            etapa_id=certame["etapa_governada"],
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="Documentação deferida",
            consolidado_em=timezone.now(),
            consolidado_por="teste",
        )


def ordem_da_ampla(certame):
    """A ordem emitida da ampla, lida das posições — e não pela função que se está prendendo."""
    posicoes = PosicaoNaOrdem.objects.filter(ato=certame["atos"][None], posicao__isnull=False)
    return [str(p.inscricao_id) for p in posicoes.order_by("posicao")]


def ocupantes(certame):
    return selectors.ocupantes_da_ampla(
        edital=certame["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        versao=effective_version(edital_id=certame["edital"].id),
    )


def chaves(conjunto):
    return {str(i) for i in conjunto}


@pytest.fixture
def quatro_vagas(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Quatro inscritos, quatro vagas na ampla e alvo quatro: a cotista PPI está entre as vagas."""
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ext-095-a",
        com_corte=True,
        quantos=4,
        geral=4,
    )


@pytest.fixture
def com_suplentes(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Seis inscritos, duas vagas na ampla e dois suplentes: a faixa da ampla é de quatro."""
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ext-095-b",
        com_corte=True,
        quantos=6,
        geral=2,
        excedente=2,
    )


class TestOcupantesDaAmpla:
    def test_sao_os_titulares_mesmo_sem_ninguem_habilitado(self, quatro_vagas, gestor):
        """**R-002 da `095`, preso como está**: os titulares da ampla, sem filtro de habilitação.

        A apuração da ampla não conta como ocupante quem não habilitou; esta função conta. É o
        comportamento que a extração preserva, e não o que ela endossa.
        """
        emitir_cortes(quatro_vagas, gestor, "ext-095-a")

        assert chaves(ocupantes(quatro_vagas)) == set(ordem_da_ampla(quatro_vagas))

    def test_habilitar_alguem_nao_muda_o_conjunto(self, quatro_vagas, gestor):
        emitir_cortes(quatro_vagas, gestor, "ext-095-a")
        habilitar(quatro_vagas, [quatro_vagas["cotista_ppi"]])

        assert chaves(ocupantes(quatro_vagas)) == set(ordem_da_ampla(quatro_vagas))
        assert str(quatro_vagas["cotista_ppi"].id) in chaves(ocupantes(quatro_vagas))

    def test_o_suplente_da_ampla_nao_ocupa(self, com_suplentes, gestor):
        """Faixa de quatro, vagas duas: só as duas primeiras posições ocupam pela ampla."""
        emitir_cortes(com_suplentes, gestor, "ext-095-b")
        ordem = ordem_da_ampla(com_suplentes)

        assert chaves(ocupantes(com_suplentes)) == set(ordem[:2])

    def test_sem_corte_emitido_a_ordem_inteira_e_a_sequencia(self, com_suplentes):
        """Sem corte, quem progrediu é a ordem com posição, e os titulares, as duas primeiras."""
        ordem = ordem_da_ampla(com_suplentes)

        assert chaves(ocupantes(com_suplentes)) == set(ordem[:2])

    def test_numero_de_consultas(self, com_suplentes, gestor):
        emitir_cortes(com_suplentes, gestor, "ext-095-b")
        versao = effective_version(edital_id=com_suplentes["edital"].id)

        with CaptureQueriesContext(connection) as consultas:
            selectors.ocupantes_da_ampla(
                edital=com_suplentes["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, versao=versao
            )

        assert len(consultas) == 8


class TestHaQuemOcupar:
    def test_conta_quem_ja_ocupa_pela_ampla(self, quatro_vagas, gestor):
        """**DP-2 da `095`, preso como está.** A única autodeclarada PPI ocupa pela ampla, e a PPI
        ainda "tem quem ocupar" com zero vagas ocupadas: a posição dela conta."""
        emitir_cortes(quatro_vagas, gestor, "ext-095-a")
        assert str(quatro_vagas["cotista_ppi"].id) in chaves(ocupantes(quatro_vagas))

        assert movimento.ha_quem_ocupar(
            edital=quatro_vagas["edital"], marco_id=MARCO, lista_id=LISTA_PPI, ja_ocupadas=0
        )

    def test_com_tantas_ocupadas_quantas_posicoes_nao_ha(self, quatro_vagas):
        assert not movimento.ha_quem_ocupar(
            edital=quatro_vagas["edital"], marco_id=MARCO, lista_id=LISTA_PPI, ja_ocupadas=1
        )

    def test_a_ampla_conta_todas_as_posicoes(self, quatro_vagas):
        edital = quatro_vagas["edital"]

        assert movimento.ha_quem_ocupar(edital=edital, marco_id=MARCO, lista_id=None, ja_ocupadas=3)
        assert not movimento.ha_quem_ocupar(
            edital=edital, marco_id=MARCO, lista_id=None, ja_ocupadas=4
        )

    def test_recorte_sem_ordem_nao_tem_quem_ocupar(self, quatro_vagas):
        assert not movimento.ha_quem_ocupar(
            edital=quatro_vagas["edital"],
            marco_id=MARCO,
            lista_id=str(uuid.uuid4()),
            ja_ocupadas=0,
        )

    def test_numero_de_consultas(self, quatro_vagas):
        with CaptureQueriesContext(connection) as consultas:
            movimento.ha_quem_ocupar(
                edital=quatro_vagas["edital"], marco_id=MARCO, lista_id=LISTA_PPI, ja_ocupadas=0
            )

        assert len(consultas) == 2
