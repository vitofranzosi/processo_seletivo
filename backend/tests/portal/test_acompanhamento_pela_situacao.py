"""O acompanhamento abre pela situação, derivada só de atos (063).

Cada teste lê **o topo** — o bloco Situação → Por quê → O que fazer — ou **os cartões**, e não a
página inteira: desde a 063 a mesma lista e o mesmo marco aparecem nas duas regiões, e uma asserção
sobre a página casaria com a errada.

Os cenários de publicação gravam ato, publicação e situação divulgada diretamente, como os testes
da `047` e da `062`: o que se testa aqui é a leitura, e não a emissão. Os de convocação usam o
cenário da `019` e os atalhos da `059`, porque a convocação precisa de apuração e de fila reais
para existir.

**Toda página renderizada passa pela varredura de vocabulário** (`UX-158`, `SC-452`): é a forma de
a proibição valer em todos os estados, e não só nos que alguém lembrou de testar.
"""

import json
import re
import uuid
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.portal import situacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import inscrever, rascunho_com_etapas
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, MARCO, marco_com_metodo
from tests.interface.test_portal_caminho_da_convocacao import (
    comunicar,
    convocada,
    enviar,
    responder,
    visivel,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PPI = "Pessoas pretas, pardas e indígenas"
PCD = "Pessoas com deficiência"
MARCO_INTERMEDIARIO = "00000000-0000-4000-8000-000000000822"

# **O que a tela não pode dizer**, com o que cada palavra afirmaria (UX-158). "Classificado" sai
# como palavra inteira: "Não classificado" é rótulo do conjunto fechado, e diz o contrário.
PROIBIDAS = {
    # Em qualquer caixa: "você está classificado" engana tanto quanto o rótulo (revisão da 063).
    r"(?i)(?<!não )\bclassificad[oa]\b": "lido como aprovado (FR-1170)",
    r"\bAprovad[oa]\b": "nenhum ato aprova",
    r"[Dd]entro das vagas": "a ocupação não registra a pessoa (L-1)",
    r"[Ll]ista de espera": "vocabulário que o domínio não tem (L-5)",
    r"[Dd]ireito [àa] vaga": "convocar não entrega a vaga (FR-292c)",
    r"\b[Mm]atriculad[oa]\b": "nenhum ato confirma matrícula (L-3)",
    r"\b[Cc]ontratad[oa]\b": "nenhum ato confirma contratação (L-3)",
    r"da fila": "posição na fila não é ato (FR-1169)",
    r"perderá": "nenhuma perda automática (FR-1177)",
}
# Termos técnicos que o topo não usa sem explicar (UX-156).
TECNICOS = ("marco", "faixa", "apuração", "homologa")
# **A única exceção à varredura do requerimento, e literal** (Clarifications da 063): o rótulo do
# desfecho da convocação. Qualquer outra ocorrência de `deferid` continua reprovando.
ROTULO_DO_INDEFERIMENTO = situacao.DESFECHOS[nomes_da_convocacao.INDEFERIMENTO]


def main(resposta):
    corpo = visivel(resposta)
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def topo(pagina):
    (bloco,) = re.findall(r'<section class="situacao-da-inscricao".*?</section>', pagina, re.S)
    return bloco


def cartoes(pagina):
    return re.findall(r'<section class="cartao-de-lista".*?</section>', pagina, re.S)


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def conferir_vocabulario(pagina):
    """A varredura do HTML renderizado: o que a pessoa lê, sem comentário de template.

    **A proibição do requerimento lê o topo, e não a página** (revisão da 063). A UX-058 protege o
    Requerimento de Matrícula, cujo chamado mora no topo; "Recurso indeferido", em "Seus recursos",
    é o nome que a `018` dá à decisão de um recurso, e reprová-lo seria a varredura governando outra
    feature.
    """
    lido = texto(pagina)
    achados = [f"{p!r}: {porque}" for p, porque in PROIBIDAS.items() if re.search(p, lido)]
    assert achados == [], "; ".join(achados)
    sem_o_rotulo = texto(topo(pagina)).replace(ROTULO_DO_INDEFERIMENTO, "")
    assert not re.search(r"deferid", sem_o_rotulo, re.I), (
        "o requerimento não aparece como deferido nem indeferido (UX-058)"
    )
    do_topo = texto(topo(pagina)).lower()
    assert [t for t in TECNICOS if t in do_topo] == [], "termo técnico no topo (UX-156)"
    return pagina


def abrir(client, inscricao):
    entrar_como_titular(client, inscricao)
    pagina = main(client.get(reverse("portal:acompanhamento", args=[inscricao.id])))
    return conferir_vocabulario(pagina)


# --- O cenário de publicação ---------------------------------------------------------------------


@pytest.fixture
def certame(api_client, manager_headers, process_payload):
    """Edital publicado com um marco, cadastro reserva de até nove e convocação por publicação."""
    return _publicar_edital(api_client, manager_headers, process_payload, reserva=("LIMITED", 9))


def _publicar_edital(api_client, manager_headers, process_payload, *, reserva, dois_marcos=False):
    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    for perfil in rascunho["profiles"]:
        if str(perfil["id"]) == str(PROFILE_ID):
            perfil["reserveType"], perfil["reserveLimit"] = reserva
            if dois_marcos:
                # O banco recusa ato de marco que a versão não declara; o segundo é cópia do
                # primeiro, com identidade e nome próprios.
                (primeiro,) = perfil["classificationMilestones"]
                perfil["classificationMilestones"].append(
                    {
                        **primeiro,
                        "id": MARCO_INTERMEDIARIO,
                        "code": "SORTEIO_2",
                        "name": "Classificação intermediária",
                    }
                )
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def ato(certame, *, lista_id=None, marco_id=MARCO):
    edital, versao = certame
    return AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=marco_id,
        lista_id=lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo={
            "editalId": str(edital.id),
            "profileId": PROFILE_ID,
            "milestoneId": marco_id,
            "versionId": str(versao.id),
            "stageResults": [],
            "origem": "SORTEIO",
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def publicar(
    certame,
    *,
    lista_id=None,
    lista="",
    natureza=Natureza.DEFINITIVA,
    marco_id=MARCO,
    marco="Classificação final",
    codigo="M2",
    publicado_em=None,
):
    edital, _ = certame
    origem = ato(certame, lista_id=lista_id, marco_id=marco_id)
    rotulo = dict(Natureza.choices)[natureza]
    cabecalho = {"marco": marco, "marco_codigo": codigo, "lista": lista, "natureza_rotulo": rotulo}
    return PublicacaoResultado.objects.create(
        edital=edital,
        ato=origem,
        perfil_id=PROFILE_ID,
        marco_id=marco_id,
        lista_id=lista_id,
        natureza=natureza,
        conteudo_publico=json.dumps({"cabecalho": cabecalho, "posicoes": []}).encode(),
        conteudo_publico_hash="0" * 64,
        publicado_por="cpf:publicadora",
        # Fora da janela recursal de cinco dias, para que o recurso só apareça onde o teste o pede.
        publicado_em=publicado_em or timezone.now() - timedelta(days=10),
        signatario_id=uuid.uuid4(),
        signatario_nome="Diretora-Geral",
        signatario_cargo="Diretoria",
    )


def situar(publicacao, inscricao, posicao=None, motivo="sem nota apurada nesta lista"):
    return SituacaoDivulgada.objects.create(
        publicacao=publicacao,
        inscricao=inscricao,
        situacao=(
            SituacaoDivulgada.Situacao.CLASSIFICADA
            if posicao
            else SituacaoDivulgada.Situacao.SEM_POSICAO
        ),
        posicao=posicao,
        compartilhada=False,
        pontuacao="7,50" if posicao else "",
        motivo="" if posicao else motivo,
    )


def edson(certame, primeiro=6301):
    """O caso do Edital 72/2026: 8º na ampla, 2º na PPI, as duas definitivas."""
    (pessoa,) = inscrever(certame[0], 1, primeiro=primeiro)
    situar(publicar(certame), pessoa, posicao=8)
    situar(publicar(certame, lista_id=LISTA_PPI, lista=PPI), pessoa, posicao=2)
    return pessoa


# --- US1: a pessoa em duas listas ----------------------------------------------------------------


class TestDuasListas:
    def test_o_topo_diz_a_situacao_e_cada_lista_com_a_sua_posicao(self, client, certame):
        pagina = abrir(client, edson(certame))
        bloco = texto(topo(pagina))

        assert "Aguardando chamada" in bloco
        assert "Ampla concorrência: 8º lugar" in bloco
        assert f"{PPI}: 2º lugar" in bloco
        assert situacao.MAIS_DE_UMA_LISTA in bloco
        assert situacao.NADA_POR_ENQUANTO in bloco
        assert situacao.NOVAS_CHAMADAS in bloco

    def test_dois_cartoes_de_titulo_distinto_e_posicao_oficial(self, client, certame):
        pagina = abrir(client, edson(certame))
        titulos = [re.search(r"<h3[^>]*>(.*?)</h3>", c).group(1) for c in cartoes(pagina)]

        assert titulos == [
            "Ampla concorrência — Classificação final",
            f"{PPI} — Classificação final",
        ]
        assert len(set(titulos)) == len(titulos)
        posicoes = [re.search(r"(\d+)º lugar", c).group(1) for c in cartoes(pagina)]
        assert posicoes == ["8", "2"], "a posição de cada cartão é a oficial da lista (SC-451)"

    def test_a_situacao_vem_antes_de_qualquer_evidencia(self, client, certame):
        pagina = abrir(client, edson(certame))

        assert pagina.index('class="situacao-da-inscricao"') < pagina.index("cartao-de-lista")
        assert pagina.index("cartao-de-lista") < pagina.index("Sua participação")
        assert pagina.index("Sua participação") < pagina.index("Cronograma do processo")
        for parte in ("Sua situação", "Por quê", "O que fazer"):
            assert parte in topo(pagina), "as três partes, sempre (SC-450)"

    def test_titulos_sem_salto(self, client, certame):
        """UX-157: h1 → h2 → h3, sem pular nível."""
        niveis = [int(n) for n in re.findall(r"<h([1-6])\b", abrir(client, edson(certame)))]
        assert niveis[0] == 1
        assert all(depois <= antes + 1 for antes, depois in zip(niveis, niveis[1:], strict=False))


class TestRecursoPorLista:
    def test_com_o_prazo_aberto_cada_lista_tem_a_sua_linha(self, client, certame):
        """Revisão da 063: as duas linhas de recurso diziam só "Classificação final"."""
        (pessoa,) = inscrever(certame[0], 1, primeiro=6305)
        agora = timezone.now()
        situar(publicar(certame, publicado_em=agora), pessoa, posicao=8)
        situar(
            publicar(certame, lista_id=LISTA_PPI, lista=PPI, publicado_em=agora), pessoa, posicao=2
        )

        bloco = texto(topo(abrir(client, pessoa)))
        linhas = re.findall(r"Se você discordar de (.*?), pode recorrer", bloco)

        assert linhas == [
            "Ampla concorrência — Classificação final",
            f"{PPI} — Classificação final",
        ]


class TestAVarredura:
    """A varredura do teste também é testada: uma que não enxerga aprova tudo, calada."""

    PAGINA = (
        '<section class="situacao-da-inscricao"><p>{topo}</p></section>'
        '<ul class="meus-recursos"><li>{fora}</li></ul>'
    )

    def test_classificado_em_minuscula_reprova(self):
        with pytest.raises(AssertionError, match="FR-1170"):
            conferir_vocabulario(self.PAGINA.format(topo="Você está classificado.", fora=""))

    def test_nao_classificado_passa(self):
        conferir_vocabulario(self.PAGINA.format(topo="Não classificado", fora=""))

    def test_recurso_indeferido_fora_do_topo_passa(self):
        conferir_vocabulario(
            self.PAGINA.format(topo="Nada por enquanto.", fora="Recurso indeferido")
        )

    def test_requerimento_indeferido_no_topo_reprova(self):
        with pytest.raises(AssertionError, match="UX-058"):
            conferir_vocabulario(self.PAGINA.format(topo="Requerimento indeferido", fora=""))


# --- US2: classificação sem ocupação definida ----------------------------------------------------


class TestSemOcupacaoDefinida:
    def test_so_preliminar_aguarda_o_definitivo(self, client, certame):
        (pessoa,) = inscrever(certame[0], 1, primeiro=6311)
        situar(publicar(certame, natureza=Natureza.PRELIMINAR), pessoa, posicao=3)

        bloco = texto(topo(abrir(client, pessoa)))

        assert "Aguardando resultado definitivo" in bloco
        assert "pode mudar" in bloco
        assert situacao.NOVAS_CHAMADAS not in bloco

    def test_o_canal_e_o_que_o_perfil_declara(self, client, certame):
        """O Perfil declara convocação por publicação: nada de e-mail nem mensagem (FR-1179)."""
        bloco = texto(topo(abrir(client, edson(certame, primeiro=6312))))

        assert "por publicação no endereço eletrônico do certame" in bloco
        assert "e-mail" not in bloco
        assert "mensagem" not in bloco


# --- US3: cadastro reserva sem pertença ----------------------------------------------------------


class TestCadastroReserva:
    def test_o_edital_preve_e_a_tela_nao_diz_que_a_pessoa_esta_nele(self, client, certame):
        bloco = texto(topo(abrir(client, edson(certame, primeiro=6321))))

        assert "O Edital prevê cadastro reserva de até 9 pessoas para este Perfil." in bloco
        assert "você está no cadastro reserva" not in bloco.lower()

    def test_sem_cadastro_reserva_nao_se_menciona(
        self, client, api_client, manager_headers, process_payload
    ):
        sem_reserva = _publicar_edital(
            api_client, manager_headers, process_payload, reserva=("NONE", None)
        )
        bloco = texto(topo(abrir(client, edson(sem_reserva, primeiro=6322))))

        assert "cadastro reserva" not in bloco


# --- US6: eliminada, sem posição, ou sem resultado -----------------------------------------------


class TestOsOutrosEstados:
    def test_sem_posicao_em_todas_e_nao_classificado(self, client, certame):
        (pessoa,) = inscrever(certame[0], 1, primeiro=6331)
        situar(publicar(certame), pessoa, motivo="não alcançou a nota mínima")

        pagina = abrir(client, pessoa)

        assert "Não classificado" in topo(pagina)
        assert "não alcançou a nota mínima" in topo(pagina)
        (cartao,) = cartoes(pagina)
        assert "Sem posição nesta lista" in cartao

    def test_recem_enviada_e_inscricao_enviada(self, client, certame):
        (pessoa,) = inscrever(certame[0], 1, primeiro=6332)

        pagina = abrir(client, pessoa)
        bloco = texto(topo(pagina))

        assert "Inscrição enviada" in bloco
        assert timezone.localtime(pessoa.submitted_at).strftime("%d/%m/%Y") in bloco
        assert situacao.RESULTADO_CONFORME_O_EDITAL in bloco
        assert "Classificação por lista" not in pagina, "nada divulgado, nada aparece (FR-056)"

    def test_eliminada_em_etapa(self, client, gestor, api_client, manager_headers, process_payload):
        from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
        from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

        cenario = montar_marco(
            gestor, api_client, manager_headers, process_payload, seed=63, codigo="0763"
        )
        inscricoes = pontuar(
            cenario, gestor, ["90.0000", "70.0000", None], primeiro=6341, sufixo="63"
        )
        registrar_ocorrencia(
            actor=gestor,
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            etapa_id=cenario["etapa"],
            inscricao_ids=[inscricoes[2].id],
            motivo="não compareceu à prova didática",
            idempotency_key="ocorrencia-063",
            correlation_id="ocorrencia-063",
        )
        cenario["ato"] = emitir(cenario, gestor, chave="emitir-063")
        publicar_o_ato(cenario, chave="publicar-063")

        bloco = texto(topo(abrir(client, inscricoes[2])))

        assert "Eliminado" in bloco
        assert "não compareceu à prova didática" in bloco


# --- US4 e US5: a convocação e o desfecho --------------------------------------------------------


@pytest.fixture
def convocacao_sem_requerimento(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="portal-063"
    )


@pytest.fixture
def convocacao_com_requerimento(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
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
        prefixo="portal-063-req",
        publicar=publicar_declarando,
    )


def acompanhamento(client, pessoa):
    pagina = main(client.get(reverse("portal:acompanhamento", args=[pessoa.id])))
    return conferir_vocabulario(pagina)


class TestConvocacaoAberta:
    def test_acao_prazo_e_consequencia(self, client, convocacao_com_requerimento, gestor):
        edital, _, _ = convocacao_com_requerimento
        vencimento = timezone.localtime(timezone.now() + timedelta(days=4))
        pessoa, declarado = convocada(
            convocacao_com_requerimento, gestor, client, "063-aberta", vencimento=vencimento
        )
        comunicar(edital, gestor, declarado["id"], "063-aberta-com")

        bloco = topo(acompanhamento(client, pessoa))
        lido = texto(bloco)

        assert "Convocado" in lido
        assert situacao.PREENCHER_REQUERIMENTO in lido
        destino = reverse("portal:requerimento", args=[pessoa.id])
        assert f'href="{destino}">Preencher Requerimento de Matrícula</a>' in bloco
        assert f"Prazo desta convocação: até {vencimento.strftime('%d/%m/%Y')}" in lido
        assert situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO in lido
        assert "pela lista Ampla concorrência" in lido
        assert "1ª chamada" in lido

    def test_sem_envio_o_prazo_nao_comecou_e_nao_ha_consequencia(
        self, client, convocacao_com_requerimento, gestor
    ):
        vencimento = timezone.now() + timedelta(days=4)
        pessoa, _ = convocada(
            convocacao_com_requerimento, gestor, client, "063-sem-envio", vencimento=vencimento
        )

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert "não começou a correr" in lido
        assert situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO not in lido

    def test_envio_com_falha_nao_inicia_o_prazo(self, client, convocacao_com_requerimento, gestor):
        vencimento = timezone.now() + timedelta(days=4)
        pessoa, declarado = convocada(
            convocacao_com_requerimento, gestor, client, "063-falha", vencimento=vencimento
        )
        ComunicacaoEmitida.objects.create(
            convocacao=Convocacao.objects.get(pk=declarado["id"]),
            forma="INDIVIDUAL_MESSAGE",
            destinatario=pessoa.email,
            resultado="FALHA",
            detalhe_tecnico="servidor de correio indisponível",
        )

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert "não começou a correr" in lido
        assert situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO not in lido

    def test_sem_vencimento_nenhuma_consequencia_de_prazo(
        self, client, convocacao_sem_requerimento, gestor
    ):
        edital, _, _ = convocacao_sem_requerimento
        pessoa, declarado = convocada(convocacao_sem_requerimento, gestor, client, "063-sem-venc")
        comunicar(edital, gestor, declarado["id"], "063-sem-venc-com")

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert "Convocado" in lido
        assert "Prazo desta convocação" not in lido
        assert situacao.NAO_ATENDIMENTO_PODE_SER_REGISTRADO not in lido

    def test_requerimento_enviado(
        self, client, convocacao_com_requerimento, gestor, campos_de_exemplo
    ):
        pessoa, _ = convocada(convocacao_com_requerimento, gestor, client, "063-enviado")
        enviar(pessoa, campos_de_exemplo)

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert situacao.REQUERIMENTO_ENVIADO in lido
        assert "Conferir o Requerimento de Matrícula enviado" in lido
        assert "homologa" not in lido.lower()
        assert "efetivad" not in lido.lower()

    def test_edital_sem_requerimento_da_a_instrucao_neutra(
        self, client, convocacao_sem_requerimento, gestor
    ):
        pessoa, _ = convocada(convocacao_sem_requerimento, gestor, client, "063-neutra")

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert situacao.SIGA_AS_INSTRUCOES in lido
        assert "atrícula" not in lido
        assert "ontrata" not in lido


@pytest.fixture
def campos_de_exemplo():
    from tests.fixtures.requerimento import campos_de_exemplo

    return campos_de_exemplo()


class TestDesfecho:
    def test_aceite_e_vaga_aceita(self, client, convocacao_sem_requerimento, gestor):
        edital, _, _ = convocacao_sem_requerimento
        pessoa, declarado = convocada(convocacao_sem_requerimento, gestor, client, "063-aceite")
        responder(edital, gestor, declarado["id"], "063-aceite-desf")

        lido = texto(topo(acompanhamento(client, pessoa)))

        assert "Vaga aceita" in lido
        assert "Manifestação registrada em processo." in lido
        assert situacao.NADA_POR_ENQUANTO in lido

    def test_desistencia_nomeia_o_desfecho(self, client, convocacao_sem_requerimento, gestor):
        edital, _, _ = convocacao_sem_requerimento
        pessoa, declarado = convocada(convocacao_sem_requerimento, gestor, client, "063-desist")
        responder(
            edital,
            gestor,
            declarado["id"],
            "063-desist-desf",
            especie=nomes_da_convocacao.DESISTENCIA_EXPRESSA,
        )

        assert "Desistência registrada" in texto(topo(acompanhamento(client, pessoa)))

    def test_o_indeferimento_e_a_unica_excecao_da_varredura(
        self, client, convocacao_sem_requerimento, gestor
    ):
        """Clarifications da 063: só o rótulo exato do desfecho passa; o resto continua vigiado."""
        edital, _, _ = convocacao_sem_requerimento
        pessoa, declarado = convocada(convocacao_sem_requerimento, gestor, client, "063-indef")
        responder(
            edital,
            gestor,
            declarado["id"],
            "063-indef-desf",
            especie=nomes_da_convocacao.INDEFERIMENTO,
        )

        pagina = acompanhamento(client, pessoa)

        assert ROTULO_DO_INDEFERIMENTO in texto(topo(pagina))
        with pytest.raises(AssertionError, match="UX-058"):
            conferir_vocabulario(pagina.replace(ROTULO_DO_INDEFERIMENTO, "Requerimento indeferido"))


# --- A tela vizinha e o custo --------------------------------------------------------------------


class TestApuracaoNaoELida:
    def test_a_apuracao_vigente_nao_muda_a_situacao_de_quem_nao_foi_chamado(
        self, client, convocacao_sem_requerimento
    ):
        """FR-1169, L-1: o cenário tem apuração emitida e fila, e ninguém foi convocado ainda.

        Quem a fila poria entre os primeiros continua sem ato que diga isso, e a tela não deduz.
        """
        from tests.interface.test_portal_caminho_da_convocacao import entrar_como, primeira_da_fila

        edital, _, inscricoes = convocacao_sem_requerimento
        pessoa = primeira_da_fila(edital, inscricoes)
        entrar_como(client, pessoa)

        bloco = texto(topo(acompanhamento(client, pessoa)))

        assert "Convocado" not in bloco
        assert "vaga" not in bloco.lower()


class TestTelaDaConvocacao:
    def test_quem_nao_foi_chamado_le_a_frase_neutra(
        self, client, convocacao_sem_requerimento, gestor
    ):
        """FR-1184: a frase antiga prometia chamada "quando uma vaga vagar"."""
        from tests.interface.test_portal_caminho_da_convocacao import entrar_como

        _, _, inscricoes = convocacao_sem_requerimento
        chamada, _ = convocada(convocacao_sem_requerimento, gestor, client, "063-vizinha")
        outra = next(i for i in inscricoes if i.id != chamada.id)
        entrar_como(client, outra)

        tela = visivel(client.get(reverse("portal:convocacao", args=[outra.id])))

        assert situacao.NOVAS_CHAMADAS in tela
        assert "quando uma vaga vagar" not in tela


class TestCusto:
    def test_a_situacao_e_os_cartoes_nao_consultam_o_banco(
        self, client, api_client, manager_headers, process_payload
    ):
        """SC-454, D-007: a derivação roda sem consulta nenhuma, com seis cartões em dois marcos.

        **Não é a contagem da página inteira, e o motivo está registrado** (achado da 063):
        `objetos_recorriveis`, da `018`, avalia a janela recursal publicação a publicação, e a
        página já crescia três consultas por lista antes desta feature. Corrigir aquilo é decisão do
        usuário; o que esta feature promete é não somar nada, e é o que se mede aqui.
        """
        from unittest import mock

        certame = _publicar_edital(
            api_client, manager_headers, process_payload, reserva=("NONE", None), dois_marcos=True
        )
        (pessoa,) = inscrever(certame[0], 1, primeiro=6351)
        for marco_id, nome, codigo in (
            (MARCO, "Classificação final", "M2"),
            (MARCO_INTERMEDIARIO, "Classificação intermediária", "M1"),
        ):
            for lista_id, lista in ((None, ""), (LISTA_PPI, PPI), (LISTA_PCD, PCD)):
                publicacao = publicar(
                    certame,
                    lista_id=lista_id,
                    lista=lista,
                    marco_id=marco_id,
                    marco=nome,
                    codigo=codigo,
                )
                situar(publicacao, pessoa, posicao=2)

        medidas = []

        def medindo(funcao):
            def medida(*args, **kwargs):
                with CaptureQueriesContext(connection) as consultas:
                    devolvido = funcao(*args, **kwargs)
                medidas.append((funcao.__name__, len(consultas)))
                return devolvido

            return medida

        with (
            mock.patch.object(
                situacao, "situacao_da_inscricao", medindo(situacao.situacao_da_inscricao)
            ),
            mock.patch.object(situacao, "ordenar_cartoes", medindo(situacao.ordenar_cartoes)),
        ):
            pagina = abrir(client, pessoa)

        assert medidas == [("ordenar_cartoes", 0), ("situacao_da_inscricao", 0)]
        assert len(cartoes(pagina)) == 6
        titulos = [re.search(r"<h3[^>]*>(.*?)</h3>", c).group(1) for c in cartoes(pagina)]
        assert titulos[0] == "Ampla concorrência — Classificação intermediária", (
            "a ordem é a do marco e, dentro dele, a ampla primeiro"
        )
