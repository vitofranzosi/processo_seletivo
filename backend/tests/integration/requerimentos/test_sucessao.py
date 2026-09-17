"""Corrigir o que se declarou, sem apagar o que se declarou antes (029, `US5`, `SC-135`).

**O sucessor nasce da mudança, e não do clique.** `atualizar` compara **antes** de gravar: conteúdo
idêntico ao antecessor é recusado sem que linha nenhuma exista. A redação anterior criava a cópia ao
abrir a conferência — bastava clicar e sair para o requerimento enviado sumir da tela da pessoa e do
dossiê, escondido atrás de um rascunho que ninguém pediu (`FR-406`, `FR-410`).

**A autorização é a porta, e é a regra inteira** (`R-6`). Sucessor só nasce sob chamada em aberto, e
cita a convocação que o autorizou. Se essa porta afrouxar, o requerimento deixa de ser declaração
num instante determinado e vira campo editável com histórico — que é o inverso do que a `D-007`
decidiu, e o defeito que a `FR-408` existe para impedir.

**E corrigir não apaga.** O antecessor continua íntegro e legível, porque é sob aquela declaração
que atos já praticados se fundaram: um indeferimento motivado no que a pessoa declarou em março não
pode passar a citar o que ela declarou em maio.

**Chamado direto, sem passar por tela.** O que se prende aqui é o comando — a tela só evita oferecer
o botão, e um `POST` montado à mão encontra a mesma recusa (Princípio IV).
"""

import pytest

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.requerimentos.application import exigencia, preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O recorte do 77/2026, com o Edital declarando o requerimento **na convocação**."""
    from tests.fixtures.corte import regra
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="requerimento-029-sucessao",
        geral=2,
        cut=regra(surplusCount=1),
        publicar=publicar_declarando,
    )


def praticar(edital, gestor, inscricao, **kwargs):
    declarado = convocar(edital, gestor, inscricao, **kwargs)
    return Convocacao.objects.get(pk=declarado["id"])


def responder(edital, gestor, convocacao, especie, chave):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        especie=especie,
        fundamento="Manifestação registrada em processo.",
        idempotency_key=chave,
        correlation_id="teste-requerimento-029",
    )


def enviar(inscricao):
    versao = preencher._conteudo(inscricao)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=versao.id,
        declaracao_exibida=preencher.declaracao_publicada(versao.content),
        aceite=True,
    )


def declarar_e_enviar(inscricao, campos):
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return enviar(inscricao)


@pytest.fixture
def enviado(cenario, gestor, campos_declarados):
    """Primeira chamada, requerimento enviado — o estado de onde toda correção parte."""
    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    chamada = praticar(edital, gestor, pessoa, idempotency_key="suc-primeira")
    return {
        "edital": edital,
        "pessoa": pessoa,
        "chamada": chamada,
        "requerimento": declarar_e_enviar(pessoa, campos_declarados),
    }


def com_mudanca(campos, **ajustes):
    return {**campos, **ajustes}


class TestConferirNaoCriaLinha:
    """O achado que reabriu esta história: **conferir não é corrigir**.

    Abrir a conferência e sair não pode deixar rastro. Enquanto deixava, o requerimento enviado
    desaparecia da tela da pessoa e do dossiê de quem conduz — porque vigente é a folha da cadeia —,
    e a recusa de *"nada mudou"* só chegava no envio, com a linha já criada.
    """

    def test_a_autorizacao_nao_grava_nada(self, enviado):
        antes = RequerimentoDeMatricula.objects.count()

        anterior, chamada = preencher.autorizacao_para_atualizar(enviado["pessoa"])

        assert RequerimentoDeMatricula.objects.count() == antes
        assert anterior.id == enviado["requerimento"].id
        assert chamada.id == enviado["chamada"].id

    def test_o_enviado_continua_vigente_depois_de_conferir(self, enviado):
        """`FR-406`: o que a pessoa mandou não some da vista dela por ela ter ido conferir."""
        preencher.autorizacao_para_atualizar(enviado["pessoa"])

        vigente = exigencia.vigente_de(enviado["pessoa"])
        assert vigente.id == enviado["requerimento"].id
        assert vigente.status == nomes.ENVIADO

    def test_atualizar_sem_mudar_nada_nao_cria_sucessor(self, enviado, campos_declarados):
        """`FR-410`, e a recusa vem **antes** da gravação — é isso que a torna regra."""
        antes = RequerimentoDeMatricula.objects.count()

        with pytest.raises(DomainError) as recusa:
            preencher.atualizar(inscricao=enviado["pessoa"], dados=campos_declarados)

        assert recusa.value.code == nomes.SUCESSOR_NAO_AUTORIZADO
        assert "Nada mudou" in recusa.value.detail
        assert RequerimentoDeMatricula.objects.count() == antes, "nenhuma linha foi criada"
        assert exigencia.vigente_de(enviado["pessoa"]).status == nomes.ENVIADO


class TestComChamadaEmAberto:
    def test_o_sucessor_nasce_com_a_mudanca_e_o_resto_copiado(self, enviado, campos_declarados):
        """`FR-409`: o que mudou entra, e o que não mudou vem do antecessor — sem redigitar."""
        sucessor = preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(campos_declarados, bairro="Praia do Canto"),
        )

        assert sucessor.id != enviado["requerimento"].id
        assert sucessor.requerimento_anterior_id == enviado["requerimento"].id
        assert sucessor.status == nomes.RASCUNHO
        assert sucessor.bairro == "Praia do Canto"
        assert sucessor.nome_da_mae == campos_declarados["nome_da_mae"], "o resto veio copiado"
        assert sucessor.rg == campos_declarados["rg"]

    def test_o_sucessor_cita_a_convocacao_que_o_autorizou(self, enviado, campos_declarados):
        """`FR-408`: sem a citação, a sucessão seria edição com outro nome."""
        sucessor = preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(campos_declarados, telefone_celular="(27) 98888-1111"),
        )

        assert sucessor.convocacao_autorizadora_id == enviado["chamada"].id

    def test_o_anterior_permanece_intacto_e_legivel(self, enviado, campos_declarados):
        """`SC-135`: corrigir não apaga — e a asserção é sobre a **linha**, não sobre um campo.

        Comparar `nome_da_mae` deixaria passar uma escrita em qualquer dos outros vinte.
        """
        antes = RequerimentoDeMatricula.objects.filter(pk=enviado["requerimento"].pk).values().get()

        preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(campos_declarados, nome_da_mae="Outro Nome Completamente"),
        )
        enviar(enviado["pessoa"])

        depois = (
            RequerimentoDeMatricula.objects.filter(pk=enviado["requerimento"].pk).values().get()
        )
        assert depois == antes
        assert RequerimentoDeMatricula.objects.filter(pk=enviado["requerimento"].pk).exists()

    def test_o_vigente_passa_a_ser_o_sucessor(self, enviado, campos_declarados):
        """Vigência é derivada: vigente é quem ninguém sucedeu."""
        preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(campos_declarados, telefone_celular="(27) 98888-1111"),
        )
        sucessor = enviar(enviado["pessoa"])

        assert exigencia.vigente_de(enviado["pessoa"]).id == sucessor.id
        assert sucessor.telefone_celular == "(27) 98888-1111"

    def test_conferir_duas_vezes_nao_duplica(self, enviado):
        """Atualizar a página não pode custar uma duplicata que a restrição recusaria."""
        preencher.autorizacao_para_atualizar(enviado["pessoa"])
        preencher.autorizacao_para_atualizar(enviado["pessoa"])

        assert RequerimentoDeMatricula.objects.filter(inscricao=enviado["pessoa"]).count() == 1


class TestSemChamadaEmAberto:
    def test_a_chamada_desfechada_nao_autoriza_sucessor(self, enviado, gestor):
        """`FR-408`: a vez passou, e corrigir agora precisaria de uma chamada que não existe."""
        responder(
            enviado["edital"],
            gestor,
            enviado["chamada"],
            nomes_da_convocacao.ACEITE,
            "suc-aceite",
        )

        with pytest.raises(DomainError) as recusa:
            preencher.autorizacao_para_atualizar(enviado["pessoa"])

        assert recusa.value.code == nomes.SUCESSOR_NAO_AUTORIZADO

    def test_a_recusa_e_distinta_de_ainda_indisponivel(self, cenario, gestor):
        """Duas ausências, dois códigos: *"ainda não chegou a sua vez"* ≠ *"a sua vez passou"*."""
        _, _, inscricoes = cenario

        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=inscricoes[1])

        assert recusa.value.code == nomes.INDISPONIVEL


class TestASegundaCorrecao:
    def test_um_sucessor_por_requerimento_e_a_cadeia_nao_se_ramifica(
        self, enviado, campos_declarados
    ):
        """`uq_requerimento_sucessor_unico`: a correção de uma correção sucede o **sucessor**.

        Duas linhas apontando o mesmo antecessor seriam duas correções paralelas do mesmo fato, e
        não haveria como dizer qual vale. A restrição é de banco, e não confiada a promessa de
        código.
        """
        from django.db import IntegrityError, transaction

        primeiro = preencher.atualizar(
            inscricao=enviado["pessoa"], dados=com_mudanca(campos_declarados, bairro="Outro")
        )

        with pytest.raises(IntegrityError), transaction.atomic():
            RequerimentoDeMatricula.objects.create(
                inscricao=enviado["pessoa"],
                status=nomes.RASCUNHO,
                disponibilizado_em=primeiro.disponibilizado_em,
                created_at=primeiro.created_at,
                requerimento_anterior=enviado["requerimento"],
                convocacao_autorizadora=enviado["chamada"],
                **{campo: getattr(primeiro, campo) for campo in preencher.CAMPOS_DECLARADOS},
            )


class TestSucessorQueNaoCorrigeNada:
    def test_editar_o_sucessor_de_volta_ao_original_e_recusado_no_envio(
        self, enviado, campos_declarados
    ):
        """A **segunda** camada: a comparação de `atualizar` impede a linha nascer sem mudança, e
        esta impede que ela seja editada de volta ao que o antecessor dizia.

        Um `POST` montado à mão faria isso; a tela nunca oferece.
        """
        preencher.atualizar(
            inscricao=enviado["pessoa"], dados=com_mudanca(campos_declarados, bairro="Outro")
        )
        preencher.gravar(
            inscricao=enviado["pessoa"], dados=campos_declarados, expected_revision=None
        )

        with pytest.raises(DomainError) as recusa:
            enviar(enviado["pessoa"])

        assert recusa.value.code == nomes.SUCESSOR_NAO_AUTORIZADO
        assert "Nada mudou" in recusa.value.detail

    def test_uma_letra_diferente_ja_e_correcao(self, enviado, campos_declarados):
        """A comparação é exata, e não por semelhança: quem decide o que é correção é a pessoa."""
        preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(
                campos_declarados, nome_da_mae=campos_declarados["nome_da_mae"] + "a"
            ),
        )

        assert enviar(enviado["pessoa"]).status == nomes.ENVIADO


class TestATrilhaDaSucessao:
    def test_o_envio_do_sucessor_grava_a_operacao_de_sucessao(self, enviado, campos_declarados):
        """`FR-397`: a trilha distingue o envio original da correção, e nomeia o que ele sucede."""
        from processo_seletivo.auditoria.models import RegistroAuditoria

        preencher.atualizar(
            inscricao=enviado["pessoa"],
            dados=com_mudanca(campos_declarados, bairro="Outro Bairro"),
        )
        sucessor = enviar(enviado["pessoa"])

        registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_SUCESSAO)
        assert str(registro.aggregate_id) == str(sucessor.id)
        assert str(enviado["requerimento"].id) in registro.reason
        assert str(enviado["chamada"].id) in registro.reason


class TestOSuplenteCorrigeIgual:
    def test_quem_foi_chamado_por_suplencia_corrige_pelo_mesmo_caminho(
        self, cenario, gestor, campos_declarados
    ):
        """**Nenhuma exceção foi escrita para a suplência**, nem no gatilho nem na sucessão."""
        edital, _, inscricoes = cenario
        titular, segundo, suplente = inscricoes[0], inscricoes[1], inscricoes[2]
        chamada = praticar(edital, gestor, titular, idempotency_key="suc-tit")
        praticar(edital, gestor, segundo, idempotency_key="suc-tit-2")
        declarar_e_enviar(titular, campos_declarados)
        responder(edital, gestor, chamada, nomes_da_convocacao.DESISTENCIA_EXPRESSA, "suc-desistiu")
        apurar(edital, gestor, chave="suc-reapurar", motivo="A desistência abriu a vaga.")
        praticar(
            edital,
            gestor,
            suplente,
            especie=nomes_da_convocacao.SUPLENCIA,
            idempotency_key="suc-suplente",
        )
        declarar_e_enviar(suplente, campos_declarados)

        sucessor = preencher.atualizar(
            inscricao=suplente, dados=com_mudanca(campos_declarados, bairro="Praia da Costa")
        )

        assert sucessor.requerimento_anterior_id is not None
        assert sucessor.convocacao_autorizadora_id is not None


class TestQuemDeclarouNaInscricao:
    """`FR-410` e `R-2`: **o cenário que a correção existe para atender**.

    Quem declara no ato da inscrição preenche o endereço em março e é convocado em setembro. É
    justamente aí que o dado envelhece — e a atualização na convocação é a mitigação que o `R-2`
    nomeia, sem regra nova, pelo caminho que a correção já usa.

    **E era exatamente esse o cenário que não funcionava.** `apurar` só consultava a chamada em
    aberto quando o momento declarado era *na convocação*; no outro ramo a chamada vinha sempre
    `None`, e *conferir e atualizar* nunca aparecia para quem mais precisava dele. Os testes de
    sucessão usavam só `AT_CALL`, e por isso o buraco não aparecia.
    """

    @pytest.fixture
    def declarou_na_inscricao(
        self,
        db,
        gestor,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
        campos_declarados,
    ):
        """Edital que coleta **na inscrição**, com a pessoa já convocada depois."""
        from tests.fixtures.corte import regra
        from tests.fixtures.publicacao import publish_original
        from tests.fixtures.requerimento import declarar

        def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
            return publish_original(
                api_client,
                manager_headers,
                process_payload,
                draft=draft,
                antes_de_submeter=declarar("AT_ENROLLMENT"),
            )

        edital, _, inscricoes = montar_cenario_da_convocacao(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="requerimento-029-na-inscricao",
            geral=2,
            cut=regra(surplusCount=1),
            publicar=publicar_declarando,
        )
        pessoa = inscricoes[0]
        declarar_e_enviar(pessoa, campos_declarados)
        chamada = praticar(edital, gestor, pessoa, idempotency_key="na-inscricao-chamada")
        return {"edital": edital, "pessoa": pessoa, "chamada": chamada}

    def test_a_politica_enxerga_a_chamada_mesmo_no_momento_na_inscricao(
        self, declarou_na_inscricao
    ):
        """A chamada é consultada em **dois** casos: abrir na convocação, e corrigir o enviado."""
        apurado = preencher.apurar(declarou_na_inscricao["pessoa"])

        assert apurado.enviado is True
        assert apurado.chamada is not None, (
            "quem declarou na inscrição e foi convocado precisa poder corrigir"
        )
        assert apurado.chamada.id == declarou_na_inscricao["chamada"].id

    def test_a_correcao_funciona_pelo_mesmo_caminho(self, declarou_na_inscricao, campos_declarados):
        sucessor = preencher.atualizar(
            inscricao=declarou_na_inscricao["pessoa"],
            dados=com_mudanca(campos_declarados, logradouro="Rua Nova, mudei de casa"),
        )

        assert sucessor.requerimento_anterior_id is not None
        assert sucessor.convocacao_autorizadora_id == declarou_na_inscricao["chamada"].id
        assert sucessor.logradouro == "Rua Nova, mudei de casa"

    def test_sem_convocacao_nao_ha_o_que_corrigir(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """A porta continua fechada para quem **não** foi chamado: corrigir exige autorização."""
        from tests.fixtures.requerimento import pronta_para_enviar

        pessoa = pronta_para_enviar(selecao_na_inscricao)
        declarar_e_enviar(pessoa, campos_declarados)

        with pytest.raises(DomainError) as recusa:
            preencher.autorizacao_para_atualizar(pessoa)

        assert recusa.value.code == nomes.SUCESSOR_NAO_AUTORIZADO
