"""A página do Processo (147), por situação e por papel.

O que cada papel vê e o que não vê, sobre os cenários da suíte: o Processo em elaboração (a fixture
`edital`), o ativo com dois Editais e condições de atenção (`processo_a`, `edital_c`), e os finais,
levados até lá pelos mesmos comandos que a tela usa.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.application.commands import add_edital
from processo_seletivo.processos.application.finalizacao import cancel_edital, cancel_process
from processo_seletivo.processos.models import Edital
from tests.conftest import ator_institucional
from tests.fixtures.supervisao import SEGUNDO_SEED, submeter
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

GESTAO = ator_institucional(
    "gestao.da.suite", "edital:criar", "edital:cancelar", "processo:cancelar", "processo:ativar"
)


def abrir(client, processo, subject="marcia.gestora", papeis=("gestor",)):
    identificar(client, subject, list(papeis))
    resposta = client.get(reverse("interface:processo-detalhe", args=[processo.id]))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def regiao(corpo, ancora):
    """A `<section>` que o título `ancora` nomeia, até o fechamento dela."""
    abertura = re.search(rf'<section[^>]*aria-labelledby="{ancora}"[^>]*>', corpo)
    assert abertura, f"sem a região {ancora}"
    return corpo[abertura.start() : corpo.index("</section>", abertura.end())]


def texto(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def topo(corpo):
    inicio = corpo.index('<header class="cc-cabecalho')
    return corpo[inicio : corpo.index("</header>", inicio)]


def novo_edital(processo, numero):
    edital, _ = add_edital(
        actor=GESTAO,
        processo_id=processo.id,
        data={"number": numero, "year": 2026, "title": f"Edital acrescido {numero}"},
        idempotency_key=f"pagina-147-edital-{numero}-0000",
        correlation_id="pagina-147",
    )
    return edital


def cancelar(edital):
    edital.refresh_from_db()
    cancel_edital(
        actor=GESTAO,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Cancelado na suíte.",
        idempotency_key=f"pagina-147-cancelar-{edital.id}",
        correlation_id="pagina-147",
    )


# ---- o topo (FR-5300 a FR-5302, FR-5321) -------------------------------------------------------


def test_o_topo_diz_quem_e_como_esta_e_onde_esta_o_conjunto(client, seletor_ligado, edital):
    corpo = abrir(client, edital.processo)
    cabecalho = topo(corpo)

    assert cabecalho.count("<h1>") == 1 and corpo.count("<h1>") == 1
    assert edital.processo.institutional_code in cabecalho
    assert "Onde estamos" in texto(cabecalho)
    assert "1 Edital: 1 em elaboração." in texto(cabecalho)
    # O ciclo em uma linha, a atual anunciada (FR-5302); a faixa de etapas em cartão saiu.
    assert '<li class="e-atual" aria-current="step">' in cabecalho
    assert "(situação atual)" in cabecalho
    assert 'class="etapas"' not in corpo


def test_o_pulso_agregado_e_estado_do_topo(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    submeter(edital_c, 3, seed=SEGUNDO_SEED)
    cabecalho = texto(topo(abrir(client, processo_a, "maria", [])))

    assert "Inscrições no Processo" in cabecalho
    assert "3 recebidas" in cabecalho
    assert "Leitura de" in cabecalho
    assert "Inscrições abertas em 1 Edital." in cabecalho


def test_quem_gere_ve_o_grupo_da_comissao_e_quem_audita_ve_a_auditoria(
    client, seletor_ligado, edital
):
    processo = edital.processo
    cabecalho = topo(abrir(client, processo))
    for rota in ("interface:supervisao", "interface:comissao", "interface:alocacoes"):
        assert reverse(rota, args=[processo.id]) in cabecalho, rota
    assert 'aria-label="Comissão e supervisão"' in cabecalho

    cabecalho = topo(abrir(client, processo, "leitora", ["auditor"]))
    assert reverse("interface:auditoria-comissao", args=[processo.id]) in cabecalho
    assert reverse("interface:comissao", args=[processo.id]) not in cabecalho

    assert "processo-acessos" not in abrir(client, processo, "pedro", ["publicador"])


# ---- o que fazer agora (FR-5303 a FR-5305) -----------------------------------------------------


def test_quem_elabora_tem_o_botao_e_o_edital_dele_nao_se_repete(client, seletor_ligado, edital):
    segundo = novo_edital(edital.processo, "02")
    cartao = regiao(
        abrir(client, edital.processo, "ana.elaboradora", ["elaborador"]), "acoes-processo"
    )

    compor = reverse("interface:compor", args=[edital.id])
    assert f'href="{compor}">Elaborar o Edital {edital.number}/{edital.year}' in cartao
    assert cartao.count(compor) == 1, "o Edital do botão repetido na faixa"
    assert reverse("interface:compor", args=[segundo.id]) in cartao
    assert "Continuar a elaboração" in cartao
    # A cobertura da faixa, a mesma da Lista (129).
    assert "não entram aqui" in texto(cartao)


def test_aguardando_quem_elabora_so_para_quem_gere(client, seletor_ligado, edital):
    """FR-5304, D-005: o gestor sabe que o certame espera outra pessoa; quem só julga ou divulga não
    recebe a frase no lugar do trabalho dele."""
    assert "Aguardando quem elabora" in abrir(client, edital.processo)
    for subject, papeis in (("ana.julgadora", ["julgador"]), ("pedro", ["publicador"])):
        cartao = texto(regiao(abrir(client, edital.processo, subject, papeis), "acoes-processo"))
        assert "Aguardando quem elabora" not in cartao, subject
        assert "Nenhuma ação sua no nível do Processo." in cartao, subject


def test_os_atos_nao_estao_em_o_que_fazer_agora(client, seletor_ligado, edital):
    corpo = abrir(client, edital.processo)
    cartao = regiao(corpo, "acoes-processo")
    assert "/atos/" not in cartao
    assert "irreversível" not in cartao
    administracao = regiao(corpo, "administracao-titulo")
    assert reverse("interface:processo-ato", args=[edital.processo.id, "ativar"]) in administracao


# ---- precisa de atenção (FR-5317, FR-5318) -----------------------------------------------------


def test_a_atencao_vem_agrupada_por_edital_com_o_total(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    submeter(edital_c, 2, seed=SEGUNDO_SEED)
    atencao = regiao(abrir(client, processo_a, "maria", []), "atencao-titulo")

    total = int(re.search(r"\((\d+) em (\d+) Edit", texto(atencao)).group(1))
    assert total == atencao.count('<li class="sinal"')
    assert f"Edital {edital_c.number}/{edital_c.year} · " in texto(atencao)


def test_quem_nao_alcanca_especie_alguma_nao_recebe_a_regiao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    corpo = abrir(client, processo_a, "estranho", [])
    assert 'aria-labelledby="atencao-titulo"' not in corpo
    # Sem a atenção, os marcos sobem para o lado do trabalho.
    assert 'class="cc-grade sem-atencao"' in corpo


# ---- os Editais (FR-5310 a FR-5316) ------------------------------------------------------------


def test_a_linha_do_edital_diz_os_fatos_dele(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    submeter(edital_c, 2, seed=SEGUNDO_SEED)
    editais = regiao(abrir(client, processo_a, "maria", []), "editais-titulo")

    linha = editais.split(f"{edital_c.number}/{edital_c.year}: </span>")[1].split("</li>")[0]
    assert "Inscrições abertas" in texto(linha)
    assert "2 recebidas" in texto(linha)
    assert "Próximo:" in texto(linha)
    assert "<table" not in editais


def test_em_preparo_a_linha_tem_uma_altura_so(client, seletor_ligado, edital):
    editais = regiao(abrir(client, edital.processo), "editais-titulo")
    assert 'class="edital-no-processo em-preparo"' in editais
    assert "inscricoes-no-processo" not in editais


def test_encerrados_e_cancelados_recolhidos_no_processo_em_curso_e_abertos_no_final(
    client, seletor_ligado, edital
):
    processo = edital.processo
    cancelar(novo_edital(processo, "02"))

    editais = regiao(abrir(client, processo), "editais-titulo")
    assert '<details class="grupo-de-editais">' in editais
    assert "Encerrados e cancelados" in editais

    cancelar(edital)
    processo.refresh_from_db()
    cancel_process(
        actor=GESTAO,
        processo_id=processo.id,
        expected_revision=processo.revision,
        reason="Cancelado na suíte.",
        idempotency_key="pagina-147-processo-cancelado",
        correlation_id="pagina-147",
    )
    corpo = abrir(client, processo)
    assert '<details class="grupo-de-editais">' not in regiao(corpo, "editais-titulo")
    # Um grupo só: o título do grupo não vem.
    assert "titulo-do-grupo" not in regiao(corpo, "editais-titulo")
    assert "Processo cancelado." in texto(topo(corpo))
    assert '<li class="e-fora">' in topo(corpo)
    # Final, sem ato: nem administração, nem "Novo Edital".
    assert 'id="administracao-titulo"' not in corpo
    assert reverse("interface:edital-criar", args=[processo.id]) not in corpo
    assert Edital.objects.filter(processo=processo, status="CANCELADO").count() == 2


def test_novo_edital_junto_do_titulo_so_para_quem_cria(client, seletor_ligado, edital):
    criar = reverse("interface:edital-criar", args=[edital.processo.id])
    assert criar in regiao(abrir(client, edital.processo), "editais-titulo")
    assert criar not in abrir(client, edital.processo, "bruno.homologador", ["homologador"])


# ---- a série (FR-5320) -------------------------------------------------------------------------


def test_a_serie_so_dos_editais_com_periodo_em_curso(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    submeter(edital_c, 2, seed=SEGUNDO_SEED)
    serie = regiao(abrir(client, processo_a, "maria", []), "serie-titulo")

    assert f"Edital {edital_c.number}/{edital_c.year}" in texto(serie)
    assert f"Edital {edital_a.number}/{edital_a.year}" not in texto(serie)


def test_sem_periodo_em_curso_a_serie_nao_vem(client, seletor_ligado, edital):
    assert 'id="serie-titulo"' not in abrir(client, edital.processo)


# ---- a administração (FR-5306 a FR-5308) -------------------------------------------------------


def test_impedidos_sao_desabilitados_e_nomeiam_o_edital(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    administracao = regiao(abrir(client, processo_a), "administracao-titulo")

    assert '<details class="cc-terminais">' in administracao
    assert "impedidos enquanto houver Edital em andamento" in administracao
    assert "2 Editais precisam ser encerrados ou cancelados antes" in texto(administracao)
    for edital in (edital_a, edital_c):
        assert reverse("interface:detalhe", args=[edital.id]) in administracao
    assert '<span class="botao desabilitado" role="link" aria-disabled="true"' in administracao
    assert "/atos/encerrar" not in administracao and "/atos/cancelar" not in administracao


def test_ato_registrado_continua_no_topo(client, seletor_ligado, edital):
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[edital.processo.id]) + "?ato=ativar"
    ).content.decode()
    assert '<p class="sucesso" role="status">Ato registrado.</p>' in topo(corpo)
