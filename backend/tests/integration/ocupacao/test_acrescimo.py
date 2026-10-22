"""A vaga acrescida depois da publicação: o banco, a leitura da apuração e os dois atos (097).

**O que estes testes protegem não é a soma** — ela é de unidade, em `tests/unit/ocupacao` — e sim o
que torna o número contestável: que a apuração diz quais acréscimos leu, que a antiga relida devolve
o dela, que acréscimo novo a torna obsoleta, e que os atos recusam o que não podem fazer sem gravar
nada.
"""

import uuid

import pytest
from django.db import connection
from django.db.utils import DatabaseError, IntegrityError
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import AcrescimoDeVagas, ApuracaoDeOcupacao
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e nome de constraint só no PostgreSQL"
)


def gravar(edital, quantidade=1, *, lista_id=None, especie=nomes.ACRESCIMO, desfaz=None, **campos):
    """Um acréscimo gravado à mão, sem o ato: é o que a leitura da apuração tem de enxergar."""
    padrao = {
        "origem": "" if especie == nomes.DESFAZIMENTO else "Edital Multicampi nº 20/2026",
        "fundamento": "Vaga não preenchida no Edital regular",
    }
    padrao.update(campos)
    return AcrescimoDeVagas.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        especie=especie,
        quantidade=quantidade,
        desfaz=desfaz,
        versao=effective_version(edital_id=edital.id),
        registrado_por="teste",
        registrado_em=timezone.now(),
        **padrao,
    )


def causas(apuracao):
    return {c["causa"] for c in selectors.causas_de_obsolescencia(apuracao)}


@postgresql_only
class TestAsGarantiasDoBanco:
    """Só no PostgreSQL: a mensagem do SQLite não nomeia a constraint, e o gatilho não existe lá."""

    def test_o_gatilho_recusa_alteracao_e_exclusao_por_queryset(self, cenario):
        edital, _, _ = cenario
        acrescimo = gravar(edital)

        with pytest.raises(DatabaseError, match="immutable"):
            AcrescimoDeVagas.objects.filter(id=acrescimo.id).update(quantidade=2)
        with pytest.raises(DatabaseError, match="immutable"):
            AcrescimoDeVagas.objects.filter(id=acrescimo.id).delete()

    @pytest.mark.parametrize(
        ("campos", "constraint"),
        [
            ({"quantidade": 0}, "ck_acrescimo_quantidade_positiva"),
            ({"especie": "OUTRA"}, "ck_acrescimo_especie"),
            ({"origem": ""}, "ck_acrescimo_com_origem"),
            ({"fundamento": ""}, "ck_acrescimo_com_fundamento"),
        ],
    )
    def test_as_constraints_recusam_o_acrescimo_malformado(self, cenario, campos, constraint):
        edital, _, _ = cenario

        with pytest.raises(IntegrityError, match=constraint):
            gravar(edital, **campos)

    def test_o_desfazimento_sem_citacao_e_recusado(self, cenario):
        edital, _, _ = cenario

        with pytest.raises(IntegrityError, match="ck_desfazimento_cita_o_acrescimo"):
            gravar(edital, especie=nomes.DESFAZIMENTO)


class TestAApuracaoLeOAcrescimo:
    def test_acrescimo_posterior_torna_a_apuracao_obsoleta(self, cenario, gestor):
        """A sexta causa (`FR-2453`): o número que ela diz já não é o do recorte."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        assert causas(vigente) == set()

        gravar(edital, 2)

        assert causas(vigente) == {nomes.CAUSA_ACRESCIMO_POSTERIOR}

    def test_a_emissao_seguinte_le_congela_e_soma(self, cenario, gestor):
        """`FR-2452`: as efetivas sobem, e os ids lidos ficam no universo."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        acrescimo = gravar(edital, 2)

        declarado = apurar(edital, gestor, chave="097-seguinte", motivo="Vaga acrescida")

        assert declarado["publicadas"] == 3
        assert declarado["efetivas"] == 5
        assert declarado["universo"]["acrescimosLidos"] == [str(acrescimo.id)]
        nova = ApuracaoDeOcupacao.objects.get(id=declarado["id"])
        assert causas(nova) == set()

    def test_o_desfazimento_e_descontado(self, cenario, gestor):
        edital, _, _ = cenario
        acrescimo = gravar(edital, 2)
        gravar(edital, 1, especie=nomes.DESFAZIMENTO, desfaz=acrescimo, fundamento="Engano")

        declarado = apurar(edital, gestor)

        assert declarado["efetivas"] == 4
        assert len(declarado["universo"]["acrescimosLidos"]) == 2

    def test_a_apuracao_antiga_relida_continua_com_o_numero_dela(self, cenario, gestor):
        """`SC-922`: a reprodução é pelo congelado, e não pelos acréscimos de hoje."""
        edital, _, _ = cenario
        gravar(edital, 1)
        antiga = apurar(edital, gestor)
        gravar(edital, 4)
        apurar(edital, gestor, chave="097-depois", motivo="Mais vagas")

        relida = ApuracaoDeOcupacao.objects.get(id=antiga["id"])

        assert relida.efetivas == 4
        assert relida.universo["acrescimosLidos"] == antiga["universo"]["acrescimosLidos"]
        lidos = selectors.acrescimos_lidos_por(relida)
        assert [quantidade for _, quantidade in lidos] == [1]

    def test_acrescimo_de_outro_recorte_nao_alcanca_este(self, cenario, gestor):
        """**O recorte exato** (`T-002`): a vaga vale onde foi registrada, e não em toda a ampla."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

        gravar(edital, 1, lista_id=uuid.uuid4())

        assert causas(vigente) == set()

    def test_apuracao_sem_a_lista_congelada_so_e_obsoleta_com_acrescimo(self, cenario, gestor):
        """As apurações anteriores à `097` não têm `acrescimosLidos`, e não mudam de estado sem
        motivo: só a vaga acrescida no recorte as torna obsoletas."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        universo = dict(vigente.universo)
        universo.pop("acrescimosLidos", None)
        # Em memória: a apuração é append-only, e o que se simula é a linha gravada antes da `097`.
        vigente.universo = universo

        assert causas(vigente) == set()
        gravar(edital, 1)
        assert causas(vigente) == {nomes.CAUSA_ACRESCIMO_POSTERIOR}


# --- O ato (US1) -------------------------------------------------------------------------------


def previa(edital, quantidade=1, *, lista_id=None):
    from processo_seletivo.ocupacao.application.acrescimo import previa_do_acrescimo

    return previa_do_acrescimo(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        quantidade=quantidade,
    )


def acrescentar(edital, ator, quantidade=1, *, chave="097-acrescentar", leitura=None, **campos):
    from processo_seletivo.ocupacao.application.acrescimo import acrescentar_vagas

    argumentos = {
        "origem": "Edital Multicampi nº 20/2026, Campus Vitória",
        "fundamento": "Vaga não preenchida no Edital regular",
        "lista_id": None,
    }
    argumentos.update(campos)
    if leitura is None:
        leitura = previa(edital, quantidade, lista_id=argumentos["lista_id"])["assinatura"]
    return acrescentar_vagas(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        quantidade=quantidade,
        leitura_confirmada=leitura,
        idempotency_key=chave,
        correlation_id="teste-097",
        **argumentos,
    )


def nada_gravado():
    return AcrescimoDeVagas.objects.count() == 0


class TestOAto:
    def test_no_recorte_sem_apuracao_grava_e_emite_a_primeira(self, cenario_reserva, gestor):
        """O TMD depois de divulgar a ordem (`T-004`): 0 publicadas, e ninguém apurou nada."""
        edital, _, _ = cenario_reserva

        declarado = acrescentar(edital, gestor)

        registro = AcrescimoDeVagas.objects.get()
        assert registro.especie == nomes.ACRESCIMO
        assert registro.quantidade == 1
        assert registro.registrado_por == gestor.subject
        assert registro.versao == effective_version(edital_id=edital.id)
        seguinte = declarado["apuracaoSeguinte"]
        assert declarado["apuracaoPendente"] is None
        assert (seguinte["publicadas"], seguinte["efetivas"], seguinte["ocupadas"]) == (0, 1, 1)
        assert seguinte["universo"]["acrescimosLidos"] == [str(registro.id)]

    def test_sobre_a_apuracao_vigente_emite_a_sucessora_com_o_autor_e_o_motivo(
        self, cenario_reserva, gestor
    ):
        """`FR-2454`: a seguinte sai do ato, em nome de quem o praticou."""
        edital, _, _ = cenario_reserva
        apurar(edital, gestor)

        declarado = acrescentar(edital, gestor, 2)

        nova = ApuracaoDeOcupacao.objects.get(id=declarado["apuracaoSeguinte"]["id"])
        assert nova.efetivas == 2
        assert nova.emitida_por == gestor.subject
        assert "Vaga acrescida" in nova.motivo_da_sucessao
        assert "Edital Multicampi" in nova.motivo_da_sucessao
        assert causas(nova) == set()

    def test_com_outra_causa_presente_grava_e_nao_emite(self, cenario_reserva, gestor):
        """Apuração obsoleta por outra causa é fato que alguém precisa ver (`FR-2454`)."""
        from processo_seletivo.ocupacao.models import EfeitoDeOcupacao

        edital, _, inscricoes = cenario_reserva
        apurar(edital, gestor)
        EfeitoDeOcupacao.objects.create(
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=None,
            inscricao_id=inscricoes[0].id,
            especie=nomes.EFEITO_EXCLUSAO,
            fundamento="Desfecho registrado",
            ato_de_origem_id=uuid.uuid4(),
            rotulo_da_origem="teste",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )
        apuracoes_antes = ApuracaoDeOcupacao.objects.count()

        declarado = acrescentar(edital, gestor)

        assert AcrescimoDeVagas.objects.count() == 1
        assert ApuracaoDeOcupacao.objects.count() == apuracoes_antes
        assert declarado["apuracaoSeguinte"] is None
        assert declarado["apuracaoPendente"]["codigo"] == nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA

    def test_a_mesma_chave_devolve_o_mesmo_acrescimo(self, cenario_reserva, gestor):
        """`FR-2458`: a confirmação reenviada não grava uma segunda vaga."""
        edital, _, _ = cenario_reserva
        leitura = previa(edital)["assinatura"]

        primeiro = acrescentar(edital, gestor, leitura=leitura)
        segundo = acrescentar(edital, gestor, leitura=leitura)

        assert primeiro["acrescimo"] == segundo["acrescimo"]
        assert AcrescimoDeVagas.objects.count() == 1

    def test_leitura_velha_e_recusada_sem_gravar(self, cenario_reserva, gestor):
        """`FR-2457`: confirmar sobre a prévia que outro acréscimo já mudou."""
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva
        velha = previa(edital)["assinatura"]
        acrescentar(edital, gestor, chave="097-outro")

        with pytest.raises(DomainError) as recusa:
            acrescentar(edital, gestor, leitura=velha)

        assert recusa.value.code == nomes.LEITURA_DO_RECORTE_MUDOU
        assert AcrescimoDeVagas.objects.count() == 1

    @pytest.mark.parametrize(
        ("quantidade", "campos", "codigo"),
        [
            (0, {}, nomes.QUANTIDADE_INVALIDA),
            ("dois", {}, nomes.QUANTIDADE_INVALIDA),
            (1, {"origem": "  "}, nomes.ORIGEM_OBRIGATORIA),
            (1, {"fundamento": ""}, nomes.FUNDAMENTO_OBRIGATORIO),
        ],
    )
    def test_os_campos_sao_conferidos(self, cenario_reserva, gestor, quantidade, campos, codigo):
        """`FR-2450`, `FR-2451`."""
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva

        with pytest.raises(DomainError) as recusa:
            acrescentar(edital, gestor, quantidade, leitura="qualquer", **campos)

        assert recusa.value.code == codigo
        assert nada_gravado()

    def test_perfil_sem_cadastro_de_reserva_e_recusado(self, cenario, gestor):
        """`FR-2463`: o Perfil de 3 vagas sem reserva não chama além delas sem Retificação."""
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario

        with pytest.raises(DomainError) as recusa:
            acrescentar(edital, gestor)

        assert recusa.value.code == nomes.ACRESCIMO_SEM_CADASTRO_DE_RESERVA
        assert "Retificação do Perfil" in recusa.value.detail
        assert nada_gravado()

    def test_quem_nao_gere_a_comissao_e_recusado(self, cenario_reserva, auditor):
        """`FR-2465`: a autoridade é a de quem apura, e o auditor só lê."""
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva

        with pytest.raises(DomainError):
            acrescentar(edital, auditor)

        assert nada_gravado()

    def test_a_trilha_registra_o_acrescimo_e_a_apuracao_com_o_mesmo_ator(
        self, cenario_reserva, gestor
    ):
        """`FR-2466`."""
        from processo_seletivo.auditoria.models import RegistroAuditoria

        edital, _, _ = cenario_reserva

        acrescentar(edital, gestor)

        registros = RegistroAuditoria.objects.filter(
            operation__in=["OCUPACAO_ACRESCENTAR_VAGAS", "OCUPACAO_APURAR"]
        )
        assert sorted(r.operation for r in registros) == [
            "OCUPACAO_ACRESCENTAR_VAGAS",
            "OCUPACAO_APURAR",
        ]
        assert {r.actor_subject for r in registros} == {gestor.subject}
        trilha = registros.get(operation="OCUPACAO_ACRESCENTAR_VAGAS")
        assert "Edital Multicampi" in trilha.reason
        assert "Apuração anterior: nenhuma" in trilha.reason

    def test_o_edital_publicado_nao_muda(self, cenario_reserva, gestor):
        """`FR-2450`: nem versão, nem Publicação, nem conteúdo."""
        from processo_seletivo.publicacoes.models import Publicacao, VersaoConsolidada

        edital, _, _ = cenario_reserva
        versoes, publicacoes = VersaoConsolidada.objects.count(), Publicacao.objects.count()
        conteudo = effective_version(edital_id=edital.id).content

        acrescentar(edital, gestor, 3)

        assert VersaoConsolidada.objects.count() == versoes
        assert Publicacao.objects.count() == publicacoes
        assert effective_version(edital_id=edital.id).content == conteudo


class TestOAcrescimoSobreviveAoQueSucedeDepois:
    """`FR-2452`: o acréscimo é do recorte, e não do corte nem da ordem que estavam vigentes."""

    def test_o_corte_sucedido_nao_o_desfaz_nem_o_duplica(self, cenario_reserva, gestor):
        from processo_seletivo.classificacao.application.corte import geracao_vigente
        from tests.fixtures.corte import emitir as emitir_corte

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor, 2)
        vigente = selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        assert vigente.efetivas == 2

        emitir_corte(
            edital,
            gestor,
            chave="097-corte-sucessor",
            motivo="a comissão revisou o alvo",
            geracao=geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
        )

        assert causas(vigente) == {nomes.CAUSA_CORTE_OBSOLETO}, "o corte, e não o acréscimo"
        seguinte = apurar(edital, gestor, chave="097-depois-do-corte", motivo="Corte sucedido")
        assert seguinte["efetivas"] == 2, "nem desfeito, nem somado de novo"
        assert seguinte["universo"]["acrescimosLidos"] == vigente.universo["acrescimosLidos"]


class TestALinhaGeral:
    """`FR-2464`: só a ampla de Perfil cujo quadro tem só a linha geral (`T-006`)."""

    @pytest.fixture
    def com_modalidade(self, db, gestor, api_client, manager_headers, process_payload):
        from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

        edital, _, _ = montar_cenario_da_ocupacao(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="ocupacao-097-ppi",
            geral=0,
            ppi=0,
            reserva="UNLIMITED",
        )
        return edital

    def test_linha_de_modalidade_ate_com_zero_e_recusada(self, com_modalidade, gestor):
        from processo_seletivo.shared.api.problems import DomainError

        with pytest.raises(DomainError) as recusa:
            acrescentar(com_modalidade, gestor)

        assert recusa.value.code == nomes.ACRESCIMO_FORA_DA_LINHA_GERAL
        assert nada_gravado()

    def test_recorte_de_modalidade_e_recusado(self, cenario_reserva, gestor):
        from processo_seletivo.shared.api.problems import DomainError
        from tests.fixtures.ocupacao import MODALIDADE_PPI

        edital, _, _ = cenario_reserva

        with pytest.raises(DomainError) as recusa:
            acrescentar(edital, gestor, leitura="x", lista_id=MODALIDADE_PPI)

        assert recusa.value.code == nomes.ACRESCIMO_FORA_DA_LINHA_GERAL


class TestAPrevia:
    """`FR-2456`: o que o ato faria, sem gravar nada."""

    def test_diz_as_vagas_depois_e_quem_a_ordem_alcanca(self, cenario_reserva, gestor):
        edital, _, inscricoes = cenario_reserva

        lida = previa(edital, 1)

        assert lida["publicadas"] == 0
        assert lida["acrescidasLiquidas"] == 0
        assert lida["efetivasDepois"] == 1
        assert [p["id"] for p in lida["alcancados"]] == [str(inscricoes[0].id)]
        assert lida["alcancados"][0]["nome"] == inscricoes[0].nome
        assert lida["alcancados"][0]["posicao"] == 1
        assert lida["faltamPessoas"] == 0
        assert lida["emissao"] is None
        assert nada_gravado()

    def test_com_mais_vagas_do_que_a_faixa_diz_quantas_ficam_sem_pessoa(
        self, cenario_reserva, gestor
    ):
        """O caso-limite da spec: a faixa de dois e 3 vagas."""
        edital, _, _ = cenario_reserva

        lida = previa(edital, 3)

        assert len(lida["alcancados"]) == 2
        assert lida["faltamPessoas"] == 1

    def test_mostra_os_acrescimos_anteriores_com_a_origem(self, cenario_reserva, gestor):
        """Para que a duplicata se veja antes de confirmar (caso-limite da spec)."""
        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)

        lida = previa(edital, 1)

        assert [a["registro"].origem for a in lida["acrescimos"]] == [
            "Edital Multicampi nº 20/2026, Campus Vitória"
        ]
        assert lida["acrescidasLiquidas"] == 1
        assert lida["efetivasDepois"] == 2


# --- O desfazimento (US3) ----------------------------------------------------------------------


def ninguem_chamado(**_):
    return 0


def um_chamado(**_):
    return 1


def desfazer(edital, ator, acrescimo, quantidade=1, *, chamadas=ninguem_chamado, **campos):
    from processo_seletivo.ocupacao.application.acrescimo import (
        desfazer_acrescimo,
        previa_do_desfazimento,
    )

    argumentos = {"motivo": "Matrícula efetivada no Edital regular", "chave": "097-desfazer"}
    argumentos.update(campos)
    leitura = argumentos.pop("leitura", None)
    if leitura is None:
        leitura = previa_do_desfazimento(
            edital=edital,
            acrescimo_id=acrescimo.id,
            quantidade=quantidade,
            pessoas_chamadas=chamadas,
        )["assinatura"]
    return desfazer_acrescimo(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        acrescimo_id=acrescimo.id,
        quantidade=quantidade,
        motivo=argumentos["motivo"],
        pessoas_chamadas=chamadas,
        leitura_confirmada=leitura,
        idempotency_key=argumentos["chave"],
        correlation_id="teste-097",
    )


class TestODesfazimento:
    def test_com_o_titular_so_na_conta_e_aceito_e_ele_sai_da_conta(self, cenario_reserva, gestor):
        """Acceptance 3 da US3, e a trava que o plano corrigiu (`FR-2462`, `T-005`)."""
        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)
        acrescimo = AcrescimoDeVagas.objects.get()

        declarado = desfazer(edital, gestor, acrescimo)

        seguinte = declarado["apuracaoSeguinte"]
        assert (seguinte["efetivas"], seguinte["ocupadas"]) == (0, 0)
        assert len(seguinte["universo"]["acrescimosLidos"]) == 2, "`FR-2461`: os dois congelados"
        desfeito = AcrescimoDeVagas.objects.get(especie=nomes.DESFAZIMENTO)
        assert desfeito.desfaz == acrescimo
        assert desfeito.fundamento == "Matrícula efetivada no Edital regular"
        assert AcrescimoDeVagas.objects.filter(especie=nomes.ACRESCIMO).count() == 1

    def test_quem_foi_chamado_trava_o_desfazimento(self, cenario_reserva, gestor):
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)
        acrescimo = AcrescimoDeVagas.objects.get()

        with pytest.raises(DomainError) as recusa:
            desfazer(edital, gestor, acrescimo, chamadas=um_chamado)

        assert recusa.value.code == nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
        assert "Registre antes o desfecho" in recusa.value.detail
        assert AcrescimoDeVagas.objects.count() == 1

    def test_a_pergunta_e_feita_dentro_do_ato_depois_da_trava(self, cenario_reserva, gestor):
        """Calculada na tela, a trava seria um número velho no instante do ato (`T-005`)."""
        from django.db import connection as conexao

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)
        acrescimo = AcrescimoDeVagas.objects.get()
        dentro = []

        def espia(**_):
            dentro.append(conexao.in_atomic_block)
            return 0

        from processo_seletivo.shared.api.problems import DomainError

        # A leitura vazia faz o ato recusar depois de perguntar — e é a pergunta que se espia.
        with pytest.raises(DomainError):
            desfazer(edital, gestor, acrescimo, chamadas=espia, leitura="")

        assert dentro == [True]

    def test_nao_passa_do_que_resta_do_acrescimo(self, cenario_reserva, gestor):
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor, 2)
        acrescimo = AcrescimoDeVagas.objects.get()
        desfazer(edital, gestor, acrescimo, 1)

        with pytest.raises(DomainError) as recusa:
            desfazer(edital, gestor, acrescimo, 2, chave="097-desfazer-2")

        assert recusa.value.code == nomes.DESFAZIMENTO_ALEM_DO_ACRESCIMO
        assert "só 1 vaga(s)" in recusa.value.detail

    @pytest.mark.parametrize(
        ("quantidade", "motivo", "codigo"),
        [(0, "Engano", nomes.QUANTIDADE_INVALIDA), (1, "  ", nomes.MOTIVO_OBRIGATORIO)],
    )
    def test_os_campos_sao_conferidos(self, cenario_reserva, gestor, quantidade, motivo, codigo):
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)
        acrescimo = AcrescimoDeVagas.objects.get()

        with pytest.raises(DomainError) as recusa:
            desfazer(edital, gestor, acrescimo, quantidade, motivo=motivo, leitura="x")

        assert recusa.value.code == codigo
        assert AcrescimoDeVagas.objects.count() == 1

    def test_acrescimo_de_outro_edital_nao_existe_aqui(self, cenario_reserva, gestor):
        from processo_seletivo.shared.api.problems import DomainError

        edital, _, _ = cenario_reserva
        estranho = AcrescimoDeVagas(id=uuid.uuid4())

        with pytest.raises(DomainError) as recusa:
            desfazer(edital, gestor, estranho, leitura="x")

        assert recusa.value.code == nomes.ACRESCIMO_INEXISTENTE
        assert recusa.value.status == 404

    def test_a_trilha_registra_o_desfazimento(self, cenario_reserva, gestor):
        from processo_seletivo.auditoria.models import RegistroAuditoria

        edital, _, _ = cenario_reserva
        acrescentar(edital, gestor)
        desfazer(edital, gestor, AcrescimoDeVagas.objects.get())

        trilha = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZER_ACRESCIMO")
        assert trilha.actor_subject == gestor.subject
        assert "Matrícula efetivada" in trilha.reason
