"""A tela "Publicações das inscrições" pela interface, com o papel de quem a usa (148).

```text
publicador   → vê histórico, próximo ato e prévia; publica (POST → 302 → tela com o ato vigente)
auditor      → vê tudo, não publica: sem formulário, e o POST é recusado com 403
gestor       → não abre a tela (a porta é a da divulgação de resultado)
outra unidade→ 404
```

A jornada é a do ator, pelo canal dele (Princípio VI): a prévia, a assinatura que ela carrega e a
confirmação saem da página, e não de uma chamada ao comando.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoDasInscricoes
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.inscricoes_publicadas import analisar, inscrever_no, montar, publicar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, seletor_ligado):
    cenario = montar(gestor, api_client, manager_headers, seed=1500, codigo="1500")
    cenario["inscricoes"] = inscrever_no(cenario, 2, primeiro=301)
    return cenario


def url(cenario, **params):
    base = reverse("interface:publicacoes-das-inscricoes", args=[cenario["edital"].id])
    return base + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")


def campo(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def test_o_publicador_ve_a_previa_e_publica_pela_tela(client, cenario):
    identificar(client, "paula.publicadora", ["publicador"])

    resposta = client.get(url(cenario))
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "Nenhum ato sobre as inscrições foi publicado" in corpo
    # O ato sugerido é a relação de recebidas, e a prévia diz quantas e que nada foi gravado.
    assert "Relação de inscrições recebidas" in corpo
    assert "nada foi gravado" in corpo
    assert "<strong>2</strong> inscrições contempladas" in corpo
    assert cenario["inscricoes"][0].nome in corpo

    publicada = client.post(
        url(cenario),
        {
            "natureza": "RECEBIDAS",
            "chave_idempotencia": campo(corpo, "chave_idempotencia"),
            "confirmacao_da_previa": campo(corpo, "confirmacao_da_previa"),
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
        },
    )
    assert publicada.status_code == 302
    depois = client.get(url(cenario)).content.decode()
    assert "Ato publicado" in depois
    assert "<strong>Vigente</strong>" in depois
    ato = PublicacaoDasInscricoes.objects.get()
    assert reverse("portal:publicacao-das-inscricoes", args=[ato.id]) in depois
    # Depois das recebidas, a tela sugere o preliminar, porque o Edital tem análise.
    assert 'aria-current="page"><strong>Resultado preliminar da análise das inscrições' in depois


def test_a_previa_obsoleta_volta_com_409_e_nada_e_gravado(client, cenario):
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = client.get(url(cenario)).content.decode()
    inscrever_no(cenario, 1, primeiro=310)

    resposta = client.post(
        url(cenario),
        {
            "natureza": "RECEBIDAS",
            "chave_idempotencia": campo(corpo, "chave_idempotencia"),
            "confirmacao_da_previa": campo(corpo, "confirmacao_da_previa"),
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
        },
    )
    assert resposta.status_code == 409
    assert "Não foi possível publicar" in resposta.content.decode()
    assert not PublicacaoDasInscricoes.objects.exists()


def test_o_preliminar_com_analise_pendente_nomeia_o_impedimento_e_nao_oferece_o_botao(
    client, cenario, gestor
):
    analisar(cenario, gestor, [(cenario["inscricoes"][0], "FAVORAVEL")], sufixo="tela")
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(url(cenario, natureza="PRELIMINAR")).content.decode()

    assert "Este ato ainda não pode ser publicado" in corpo
    assert "1 inscrição(ões) ainda sem conclusão" in corpo
    assert 'name="confirmacao_da_previa"' not in corpo


def test_o_preliminar_oferece_o_evento_do_cronograma_e_a_declaracao_sem_recurso(
    client, cenario, gestor
):
    analisar(
        cenario,
        gestor,
        [(cenario["inscricoes"][0], "FAVORAVEL"), (cenario["inscricoes"][1], "DESFAVORAVEL")],
        sufixo="tela-prazo",
    )
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(url(cenario, natureza="PRELIMINAR")).content.decode()

    assert "Recurso contra o resultado preliminar da análise das inscrições" in corpo
    assert "O Edital não prevê recurso contra este resultado" in corpo
    assert "Etapa de análise: <strong>Análise documental</strong>" in corpo
    # A indeferida é contada e não nomeada, nem na conferência da comissão.
    assert cenario["inscricoes"][1].nome not in corpo


def test_a_divergencia_do_vigente_aparece_e_a_correcao_pede_motivo(client, cenario):
    publicar(cenario, "RECEBIDAS", chave="divergencia")
    inscrever_no(cenario, 1, primeiro=320)
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(url(cenario, natureza="RECEBIDAS")).content.decode()

    assert "O ato vigente difere da situação atual em 1 inscrição" in corpo
    assert 'name="motivo"' in corpo
    assert "Correção do ato vigente." in corpo


def test_a_auditoria_consulta_e_nao_publica(client, cenario):
    identificar(client, "auditora", ["auditor"])

    corpo = client.get(url(cenario)).content.decode()
    assert "Esta tela mostra a você o que seria publicado" in corpo
    assert 'name="confirmacao_da_previa"' not in corpo

    recusa = client.post(url(cenario), {"natureza": "RECEBIDAS"})
    assert recusa.status_code == 403
    assert not PublicacaoDasInscricoes.objects.exists()


def test_quem_nao_divulga_nao_abre_e_outra_unidade_nao_encontra(client, cenario):
    identificar(client, "carlos", ["gestor"])
    assert client.get(url(cenario)).status_code == 403

    identificar(client, "paula", ["publicador"], escopo="outra-unidade")
    assert client.get(url(cenario)).status_code == 404


def test_o_edital_oferece_o_caminho_a_quem_publica(client, cenario):
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(reverse("interface:detalhe", args=[cenario["edital"].id])).content.decode()

    assert url(cenario) in corpo
    assert "Publicações das inscrições" in corpo


def test_a_previa_mostra_a_contagem_e_os_nomes_por_lista(
    client, gestor, api_client, manager_headers, seletor_ligado
):
    """FR-5445 (revisão de 12/11, D-011): a comissão confere por lista o que vai publicar.

    O total continua por inscrição, e a tela diz por que a soma das listas passa dele.
    """
    from tests.fixtures.inscricoes_publicadas import modalidade_pcd, modalidade_ppi

    cenario = montar(gestor, api_client, manager_headers, seed=1501, codigo="1501", com_cotas=True)
    inscricoes = inscrever_no(
        cenario,
        3,
        primeiro=311,
        modalidades={1: modalidade_ppi(1501), 2: modalidade_pcd(1501)},
    )
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(url(cenario)).content.decode()

    assert "<strong>3</strong> inscrições contempladas" in corpo
    assert "consta também na ampla concorrência" in corpo
    assert "O total conta cada inscrição uma vez." in corpo
    for lista, quantas in (
        ("Ampla concorrência", 3),
        ("Pessoas com deficiência", 1),
        ("Pretos, pardos e indígenas", 1),
    ):
        assert f"<td>{lista}</td>\n      <td>{quantas}</td>" in corpo
        assert f"· {lista} ({quantas})</summary>" in corpo
    assert inscricoes[1].nome in corpo
