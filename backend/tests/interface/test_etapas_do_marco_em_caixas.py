"""As Etapas que o marco enumera: caixas com o peso, e uma frase quando só uma pode entrar (030).

**A lista de escolha múltipla era a única da interface**, e foi a que um elaborador estranhou ao ver
a prévia da 094 funcionando: a seleção aparecia em cinza, como campo desabilitado; um clique simples
desmarcava as outras Etapas, e marcar duas pedia Cmd+clique. Para duas a cinco Etapas, a caixa
mostra todas e o estado de cada uma.

**Com uma Etapa classificatória só, a pergunta não existe** (SC-139): o marco novo nasce com ela, e
o cartão a diz numa frase. Só o marco novo — o que já foi declarado não é alcançado (FR-421) —, e
só fora do sorteio, onde enumerar a Etapa, ou nenhuma, é escolha de verdade (FR-432).

**O peso vem ao lado do nome**, como o documento o escreve: é dado do Edital, e não ajuda — a
FR-428 fica como está.

O servidor não muda: caixas com o mesmo nome enviam a lista que a lista enviava, e a gravação lê por
`getlist`. O que o navegador guarda no rascunho local está em `tests/javascript/rascunho.test.js`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from tests.interface.conftest import identificar
from tests.interface.test_compor import EVENTO, PERFIL

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA_CLASSIFICATORIA = "aaaaaaaa-0000-4000-8000-00000000e021"
SEGUNDA_ETAPA = "aaaaaaaa-0000-4000-8000-00000000e023"
MARCO = "aaaaaaaa-0000-4000-8000-00000000e051"

CAIXA = re.compile(r'<input[^>]*type="checkbox"[^>]*name="marco-[^"]*-stages"[^>]*>')


def _etapas(client, edital, **segunda):
    """Regrava as duas Etapas de `com_etapas`, com a segunda como o teste pede."""
    base = {
        "etapa-0-id": ETAPA_CLASSIFICATORIA,
        "etapa-0-name": "Prova didática",
        "etapa-0-order": "1",
        "etapa-0-weight": "2",
        "etapa-0-classificatory": "on",
        "etapa-0-scheduleEventId": EVENTO,
        "etapa-1-id": SEGUNDA_ETAPA,
        "etapa-1-name": "Análise de títulos",
        "etapa-1-order": "2",
        "etapa-1-weight": "1",
        "etapa-1-classificatory": "on",
        "etapa-1-scheduleEventId": "",
    }
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {**base, **{f"etapa-1-{campo}": valor for campo, valor in segunda.items()}},
    )
    assert resposta.status_code == 302, resposta.content
    assert EtapaAvaliacao.objects.filter(edital=edital, classificatory=True).count() == 2


@pytest.fixture
def com_duas(client, com_etapas):
    _etapas(client, com_etapas)
    return com_etapas


def marco_novo(client, edital):
    """O cartão do marco acrescentado pelo botão — o caminho em que o marco nasce."""
    return client.get(
        reverse("interface:fragmento-marco", args=[PERFIL]),
        {"edital": str(edital.id), "indice": "0"},
    ).content.decode()


def recomposto(client, edital, **campos):
    """O cartão reconstruído a partir do que está digitado agora — o caminho do htmx."""
    base = {
        f"marco-{PERFIL}-0-id": MARCO,
        f"marco-{PERFIL}-0-code": "FINAL",
        f"marco-{PERFIL}-0-name": "Classificação final",
        f"marco-{PERFIL}-0-scale": "2",
        f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
        "edital": str(edital.id),
    }
    return client.get(
        reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]),
        {**base, **{f"marco-{PERFIL}-0-{campo}": valor for campo, valor in campos.items()}},
    ).content.decode()


def rotulo_da_caixa(corpo, indice):
    """O texto do `label` da caixa de índice `indice`, sem as tags."""
    rotulo = re.search(rf'<label for="marco-[^"]*-stages-{indice}">(.*?)</label>', corpo, re.S)
    assert rotulo is not None, f"caixa {indice} sem rótulo"
    return re.sub(r"<[^>]+>", "", rotulo.group(1))


# ------------------------------------------------------------- duas ou mais: caixas


def test_cada_etapa_classificatoria_e_uma_caixa_e_nao_ha_lista(client, com_duas):
    corpo = recomposto(client, com_duas, orderProduction="POR_PONTUACAO")

    assert len(CAIXA.findall(corpo)) == 2
    assert not re.search(r'<select[^>]*name="marco-[^"]*-stages"', corpo)
    assert "<legend>Etapas que entram na ordem" in corpo


def test_as_marcadas_sao_as_que_o_marco_enumera(client, com_duas):
    corpo = recomposto(client, com_duas, orderProduction="POR_PONTUACAO", stages=[SEGUNDA_ETAPA])

    marcadas = [caixa for caixa in CAIXA.findall(corpo) if " checked" in caixa]
    assert len(marcadas) == 1
    assert f'value="{SEGUNDA_ETAPA}"' in marcadas[0]


def test_o_peso_vem_ao_lado_do_nome(client, com_duas):
    corpo = recomposto(client, com_duas, orderProduction="POR_PONTUACAO")

    assert " ".join(rotulo_da_caixa(corpo, 0).split()) == "Prova didática peso 2"
    assert " ".join(rotulo_da_caixa(corpo, 1).split()) == "Análise de títulos peso 1"


def test_sem_peso_declarado_nada_se_escreve_ao_lado(client, com_etapas):
    """Quem cobra o peso é o aviso de baixo, assim que a Etapa é marcada (037, FR-551)."""
    _etapas(client, com_etapas, weight="")

    corpo = recomposto(client, com_etapas, orderProduction="POR_PONTUACAO")

    assert " ".join(rotulo_da_caixa(corpo, 1).split()) == "Análise de títulos"


def test_a_etapa_decisoria_diz_que_nao_pontua(client, com_etapas):
    """A decisória é porta, e não parcela (015, FR-074): escrever um peso afirmaria uma parcela."""
    _etapas(
        client,
        com_etapas,
        weight="",
        forma="DECISORIA",
        rotuloFavoravel="Apto",
        rotuloDesfavoravel="Inapto",
    )

    corpo = recomposto(client, com_etapas, orderProduction="POR_PONTUACAO")

    assert " ".join(rotulo_da_caixa(corpo, 1).split()) == "Análise de títulos não pontua"


def test_cada_caixa_recompoe_o_cartao_inteiro(client, com_duas):
    """`closest fieldset.marco`, e não `closest fieldset`, que seria o próprio grupo."""
    caixas = CAIXA.findall(recomposto(client, com_duas, orderProduction="POR_PONTUACAO"))

    assert caixas
    for caixa in caixas:
        assert 'hx-include="closest fieldset.marco"' in caixa
        assert 'hx-target="closest fieldset.marco"' in caixa
        assert "required" not in caixa, "num grupo, o required exigiria todas marcadas"


def test_o_marco_novo_com_duas_nao_nasce_com_nenhuma(client, com_duas):
    corpo = marco_novo(client, com_duas)

    assert len(CAIXA.findall(corpo)) == 2
    assert not [caixa for caixa in CAIXA.findall(corpo) if " checked" in caixa]


def test_a_gravacao_le_as_caixas_como_lia_a_lista(client, com_duas):
    """Duas caixas marcadas são duas Etapas no marco gravado: o envio é o mesmo da lista."""
    from tests.interface.test_compor_classificacao import marco_form

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_duas.id, "classificacao"]),
        marco_form(**{f"marco-{PERFIL}-0-stages": [ETAPA_CLASSIFICATORIA, SEGUNDA_ETAPA]}),
    )
    assert resposta.status_code == 302, resposta.content

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_duas.id, "classificacao"])
    ).content.decode()
    marcadas = [caixa for caixa in CAIXA.findall(corpo) if " checked" in caixa]
    assert len(marcadas) == 2


# ------------------------------------------------------------- uma só: a frase


def test_o_marco_novo_com_uma_etapa_nasce_com_ela_e_a_diz(client, com_etapas):
    corpo = marco_novo(client, com_etapas)

    assert not CAIXA.findall(corpo), "uma resposta possível não é escolha"
    assert f'name="marco-{PERFIL}-0-stages" value="{ETAPA_CLASSIFICATORIA}"' in corpo
    frase = re.search(r'id="marco-[^"]*-stages">(.*?)</p>', corpo, re.S)
    assert frase is not None
    texto = " ".join(re.sub(r"<[^>]+>", "", frase.group(1)).split())
    assert texto == (
        "Entra na ordem Prova didática (peso 2), a única Etapa classificatória deste Edital."
    )


def test_a_frase_viaja_no_recompor(client, com_etapas):
    """O valor oculto é o que o próximo recompor lê: a frase não some ao mudar outro campo."""
    corpo = recomposto(
        client, com_etapas, orderProduction="POR_PONTUACAO", stages=ETAPA_CLASSIFICATORIA
    )

    assert "a única Etapa classificatória deste Edital" in corpo
    assert "a pontuação combinada deste marco" in corpo


def test_sob_sorteio_a_etapa_unica_volta_a_ser_escolha(client, com_etapas):
    """FR-432: o marco de sorteio pode não enumerar Etapa, e então desmarcá-la é escolha."""
    corpo = recomposto(
        client, com_etapas, orderProduction="POR_SORTEIO", stages=ETAPA_CLASSIFICATORIA
    )

    caixas = CAIXA.findall(corpo)
    assert len(caixas) == 1
    assert " checked" in caixas[0]
    assert "a única Etapa classificatória deste Edital" not in corpo


def test_o_marco_ja_declarado_sem_etapa_nao_e_preenchido(client, com_etapas):
    """FR-421: o que o sistema responde pelo marco novo não alcança o marco já declarado."""
    corpo = recomposto(client, com_etapas, orderProduction="POR_PONTUACAO")

    caixas = CAIXA.findall(corpo)
    assert len(caixas) == 1
    assert " checked" not in caixas[0]


def test_a_ajuda_da_etapa_continua_apontando_para_o_campo(client, com_etapas):
    """O item "Etapas que entram na ordem" do como-preencher leva ao `id` do campo, nas duas."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    frase = marco_novo(client, com_etapas)
    caixas = recomposto(client, com_etapas, orderProduction="POR_PONTUACAO")

    assert f'id="marco-{PERFIL}-0-stages"' in frase
    assert f'id="marco-{PERFIL}-0-stages"' in caixas
