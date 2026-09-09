"""O sorteio inteiro, pela interface, contra a fonte **de produção** (021, FR-076, R-005).

**Por que este arquivo existe.** Toda a suíte da `021` observa a ocorrência por um falso: é o que
torna 4.274 testes determinísticos e independentes de rede. O preço é que o adaptador real — o que
fala com a Caixa, lê `listaDezenas` e interpreta `dataApuracao` — nunca era exercitado pelo caminho
que a presidência de fato percorre. Um defeito ali passaria pela suíte inteira e apareceria no dia
do sorteio, com a transmissão aberta.

Aqui o percurso é o da tela, do começo ao fim: identificar, congelar a relação, observar a
ocorrência **na rede**, realizar, e conferir o resultado nas três páginas públicas — relação,
verificação e manifesto. E, no fim, o que um auditor externo faria: recalcular a ordem a partir do
manifesto publicado, sem tocar no banco.

**A única coisa simulada é o calendário do certame**, e ela é simulada por necessidade lógica, não
por conveniência: a FR-016 exige que a ocorrência seja posterior ao congelamento, e toda extração
já publicada é, por construção, anterior a agora. Em produção o Edital é publicado e a relação é
congelada dias antes da extração; aqui o relógio corre nesse passado enquanto o certame é montado
e congelado, e volta a ser o de verdade no instante em que a fonte é consultada. A rede, a resposta
da fonte, a semente, a ordem e o manifesto são reais.

Roda por escolha, e não por padrão — a suíte não depende de rede:

    SORTEIO_E2E_FONTE_REAL=1 uv run pytest tests/interface/test_sorteio_com_a_fonte_de_producao.py

Apontá-lo para outra extração é trocar duas variáveis, e não editar o arquivo:
`SORTEIO_E2E_CONCURSO` e `SORTEIO_E2E_OCORRE_EM`.
"""

import os
import re
from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.domain import chave as dominio_da_chave
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, Sorteio
from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("SORTEIO_E2E_FONTE_REAL"),
        reason=(
            "E2E contra a fonte de produção: depende de rede e do serviço da Caixa. "
            "Ligue com SORTEIO_E2E_FONTE_REAL=1."
        ),
    ),
]

# Concurso já apurado e permanentemente publicado: o teste é reprodutível porque a extração é
# história, e não um alvo em movimento. As variáveis permitem apontá-lo para outro sem editar aqui.
CONCURSO = os.environ.get("SORTEIO_E2E_CONCURSO", "6098")
OCORRE_EM = os.environ.get("SORTEIO_E2E_OCORRE_EM", "2026-09-06T20:00:00-03:00")

METODO_REAL = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    # **O nome do vocabulário fechado**, e é ele que escolhe o adaptador: trocá-lo por
    # "Fonte de demonstração" faria este arquivo deixar de testar o que ele existe para testar.
    "source": "Loteria Federal",
    "occurrence": CONCURSO,
    "occurrenceAt": OCORRE_EM,
    "derivation": (
        f"concurso {CONCURSO} da Loteria Federal, extração publicada na data programada no Edital"
    ),
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números sorteados, na ordem dos prêmios, separados por espaço",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a extração seguinte da mesma fonte",
    },
}

# Cinco bilhetes de seis dígitos, separados por espaço, é o que a Loteria Federal publica. A
# asserção é sobre a **forma**, e não sobre os dígitos: o teste continua verdadeiro apontado para
# outra extração, e continua falso se o adaptador devolver qualquer outra coisa.
EXTRACAO = re.compile(r"^\d{6}(?: \d{6}){4}$")


def recuar_o_relogio(monkeypatch, instante):
    """Fixa `timezone.now()` — e, com ele, o calendário inteiro do certame.

    Recuar só o relógio do comando de congelamento não funcionaria, e a razão é boa: a relação cita
    a **versão vigente na data**, e uma versão publicada depois não existe naquele dia. O certame é
    um todo datado; ou ele acontece antes da extração, ou não acontece.
    """
    monkeypatch.setattr(timezone, "now", lambda: instante)


def _tela(client, certame):
    return client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()


def _campos_do_formulario(corpo, acao):
    """Os `hidden` que a própria página oferece naquele formulário.

    Ler os identificadores do banco seria montar um POST que a tela não oferece — e o que este
    arquivo precisa provar é justamente que ela os oferece.
    """
    formulario = re.search(
        rf'<form method="post" action="{re.escape(acao)}">(.*?)</form>', corpo, re.S
    )
    assert formulario, f"a tela não oferece o formulário de {acao}"
    return dict(
        re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)"', formulario.group(1))
    )


def test_o_percurso_inteiro_da_presidencia_contra_a_fonte_real(
    gestor, api_client, manager_headers, process_payload, seletor_ligado, client, monkeypatch
):
    ocorre_em = parse_datetime(OCORRE_EM)
    assert ocorre_em is not None and ocorre_em <= datetime.now(ocorre_em.tzinfo), (
        f"{OCORRE_EM} ainda não aconteceu: a fonte não teria o que publicar."
    )

    # 1. O certame acontece **antes** da extração: Edital publicado, comissão constituída,
    #    inscrições submetidas e universo congelado, tudo nos dias que antecedem o sorteio.
    congelamento = ocorre_em - timedelta(days=5)
    recuar_o_relogio(monkeypatch, congelamento)
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=METODO_REAL
    )
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "maria", [])

    resposta = client.post(
        reverse("interface:publicar-relacao-do-sorteio", args=[edital.id, marco]),
        _campos_do_formulario(
            _tela(client, certame),
            reverse("interface:publicar-relacao-do-sorteio", args=[edital.id, marco]),
        ),
    )
    assert resposta.status_code == 302
    monkeypatch.undo()

    # 2. Observar a ocorrência. **Aqui há rede**, e o formulário não diz qual extração buscar: a
    # referência vem do método publicado, e a tela apenas a nomeia.
    corpo = _tela(client, certame)
    assert f"Observar a ocorrência {CONCURSO} na fonte" in corpo
    resposta = client.post(
        reverse("interface:observar-ocorrencia-do-sorteio", args=[edital.id, marco])
    )
    assert resposta.status_code == 302

    ocorrencia = OcorrenciaDaFonte.objects.get(referencia=CONCURSO)
    assert not ocorrencia.indisponivel, ocorrencia.evidencia
    assert ocorrencia.fonte == "Loteria Federal"
    assert EXTRACAO.match(ocorrencia.material_bruto), ocorrencia.material_bruto

    # **O limite inferior é o início do dia publicado, e não um horário inventado.** A fonte manda
    # `dataApuracao` sem hora; carimbar 20:00 sobre ela afrouxaria a precedência da FR-016 com um
    # dado que ninguém publicou.
    quando = timezone.localtime(ocorrencia.ocorrida_nao_antes_de, ZONA)
    assert (quando.hour, quando.minute, quando.second) == (0, 0, 0), quando
    assert quando.date() == ocorre_em.date()
    assert quando > congelamento

    # 3. Realizar. Um botão, e ele constitui.
    corpo = _tela(client, certame)
    acao = reverse("interface:realizar-sorteio", args=[edital.id, marco])
    resposta = client.post(acao, _campos_do_formulario(corpo, acao))
    assert resposta.status_code == 302

    sorteio = Sorteio.objects.get()
    # A normalização publicada é `DIGITOS_EM_SEQUENCIA`: os grupos de dígitos do material bruto, na
    # ordem em que a fonte os publica, separados por espaço — e nada mais do que veio da fonte.
    assert sorteio.semente_normalizada == " ".join(re.findall(r"\d+", ocorrencia.material_bruto))

    # 4. As três páginas públicas, que é onde o certame de fato aparece.
    manifesto = client.get(reverse("portal:manifesto-do-sorteio", args=[sorteio.id])).json()
    assert manifesto["seed"]["source"] == "Loteria Federal"
    assert manifesto["seed"]["occurrence"] == CONCURSO
    assert manifesto["seed"]["rawMaterial"] == ocorrencia.material_bruto
    assert manifesto["method"]["methodHash"] == canonical_sha256(METODO_REAL)

    verificacao = client.get(
        reverse("portal:verificar-sorteio", args=[sorteio.id])
    ).content.decode()
    assert manifesto["manifestHash"] in verificacao

    relacao_publica = client.get(
        reverse("portal:relacao-de-habilitados", args=[manifesto["relation"]["relationId"]])
    ).content.decode()
    assert manifesto["relation"]["relationHash"] in relacao_publica

    # 5. E o que um auditor de fora faria: recalcular a ordem **a partir do manifesto**, sem tocar
    # no banco. É esta asserção que prova que o publicado basta para conferir o sorteio.
    assert manifesto["manifestHash"] == canonical_sha256(
        {k: v for k, v in manifesto.items() if k != "manifestHash"}
    )
    recorte = dominio_da_chave.recorte(
        perfil_id=manifesto["scope"]["profileId"], lista_id=manifesto["scope"]["listId"]
    )
    conferidas = dominio_da_chave.chaves(
        relation_hash=manifesto["relation"]["relationHash"],
        draw_scope_id=recorte,
        seed=manifesto["seed"]["normalized"],
        public_numbers=[p["publicNumber"] for p in manifesto["participants"]],
    )
    esperada = dominio_da_chave.ordenar(conferidas)
    publicada = [
        p["publicNumber"] for p in sorted(manifesto["participants"], key=lambda p: p["position"])
    ]
    assert esperada == publicada
    assert conferidas == {p["publicNumber"]: p["key"] for p in manifesto["participants"]}
