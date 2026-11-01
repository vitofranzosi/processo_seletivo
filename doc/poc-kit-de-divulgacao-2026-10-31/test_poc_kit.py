"""O roteiro da POC: publica cada cenário pelo fluxo real, gera o kit, confere e grava em `saidas/`.

**Por que pytest, e por que fora da suíte.** Os cenários precisam de Edital publicado de verdade —
`Publicacao`, `VersaoConsolidada`, Retificação com vigência —, e o caminho mais curto e mais fiel é o
dos testes: o corpus da `070` (`tests/fixtures/corpus.py`) republicado pelos comandos reais, num
banco de teste que nasce e morre com a rodada. Nada fica em banco nenhum; o que sobra são os
arquivos em `saidas/`. O arquivo mora aqui, e não em `backend/tests/`, para não entrar no
`make test-pg` nem nas varreduras que leem `backend/`.

Rodar (de `backend/`, com o PostgreSQL local):

    TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=ps_poc_kit \\
      uv run --with resvg-py pytest -p tests.conftest -c pyproject.toml --rootdir=. \\
      ../doc/poc-kit-de-divulgacao-2026-10-31/test_poc_kit.py -s
"""

import hashlib
import sys
import time
from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.portal.views import _selecao_da_vitrine
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures import editais_do_piloto
from tests.fixtures.corpus import REFERENCIA, publicar_do_corpus, retificar_do_corpus

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from kit import coerencia, pacote, peca, textos  # noqa: E402
from kit.ficha import diferencas, ficha_do_edital  # noqa: E402

SAIDAS = PASTA / "saidas"
BASE = "https://gps.exemplo.ifes.edu.br"

pytestmark = pytest.mark.django_db(transaction=False)


def _deslocamento():
    """Dias inteiros, para que 23h59 continue 23h59: o deslocamento do corpus leva a hora junto."""
    return timedelta(days=(timezone.now() - REFERENCIA).days + 2)


def _inicio(ficha):
    return parse_datetime(ficha["inicio"])


def _conferir_com_o_portal(ficha, edital_id, agora):
    """A ficha diz o que o cartão da vitrine diz, no mesmo instante — período, situação e oferta."""
    versao = effective_version(edital_id=edital_id, at=agora)
    desfecho = desfechos([versao.edital])[versao.edital_id]
    cartao = _selecao_da_vitrine(versao, agora, desfecho)
    periodo = cartao["periodo"]
    problemas = []
    if (ficha["periodo_estado"], ficha["situacao_chave"]) != (
        periodo.estado,
        cartao["situacao_chave"],
    ):
        problemas.append("situação diverge da vitrine")
    if ficha["inicio"] != (
        periodo.inicio
        and periodo.inicio.astimezone(parse_datetime(ficha["referencia"]).tzinfo).isoformat()
    ):
        problemas.append("início diverge da vitrine")
    ofertas = [(o["nome"], o["quantidade"]) for o in ficha["ofertas"]]
    if ofertas != [(o["nome"], o["quantidade"]) for o in cartao["ofertas_todas"]]:
        problemas.append("oferta diverge da vitrine")
    return problemas


def gerar(nome, edital_id, agora, *, descricao, anterior=None):
    """O pipeline inteiro: ficha → textos → peça → PNG → pacote, com as conferências."""
    pasta = SAIDAS / nome
    pasta.mkdir(parents=True, exist_ok=True)
    ficha = ficha_do_edital(edital_id, agora=agora, base_url=BASE).como_dict()
    relatorio = {"cenario": nome, "descricao": descricao, "modo": ficha["modo"], "problemas": []}
    relatorio["problemas"] += [
        f"portal: {p}" for p in _conferir_com_o_portal(ficha, edital_id, agora)
    ]

    kit = textos.compor(ficha)
    notas = textos.notas_para_quem_divulga(ficha)
    if anterior is not None:
        mudou = diferencas(anterior, ficha)
        relatorio["desatualizacao"] = [
            {"campo": campo, "de": de, "para": para} for campo, de, para in mudou
        ]
        if mudou:
            notas.insert(
                0,
                f"Material anterior (ref. {anterior['impressao'][:8]}) desatualizado. Mudou: "
                + "; ".join(f"{campo} ({de} → {para})" for campo, de, para in mudou),
            )
        else:
            notas.insert(
                0,
                f"Houve publicação depois do material anterior (ref. {anterior['impressao'][:8]}), "
                "mas ela não muda nada do que o material diz: ele continua valendo.",
            )
    arquivos = {
        "ficha.json": pacote.json_bonito(ficha),
        "kit.md": textos.em_markdown(ficha, kit, notas),
        "kit.txt": textos.em_texto(ficha, kit, notas),
        "textos.json": pacote.json_bonito({"notas": notas, **kit}),
    }
    svg = png = None
    omissoes = []
    try:
        svg, alternativo, omissoes = peca.compor(ficha)
        segunda, _, _ = peca.compor(ficha)
        relatorio["svg_deterministico"] = svg == segunda
        inicio = time.perf_counter()
        png = pacote.rasterizar(svg)
        relatorio["ms_rasterizacao"] = round((time.perf_counter() - inicio) * 1000, 1)
        relatorio["png_deterministico"] = pacote.rasterizar(svg) == png
        relatorio["problemas"] += coerencia.peca_contida_na_ficha(svg, ficha)
        relatorio["problemas"] += coerencia.peca_contida_nos_textos(svg, ficha, kit)
        arquivos["peca-feed-1080x1350.svg"] = svg
        arquivos["peca-feed-1080x1350.png"] = png
        arquivos["texto-alternativo.txt"] = alternativo + "\n"
    except peca.PecaNaoCabe as recusa:
        relatorio["peca_recusada"] = str(recusa)
    relatorio["omissoes"] = omissoes
    relatorio["problemas"] += coerencia.vocabulario(ficha, kit, svg)
    gerado_em = timezone.now().astimezone(ZONA).isoformat()
    arquivos["manifesto.json"] = pacote.json_bonito(
        pacote.manifesto(ficha, gerado_em=gerado_em, svg=svg, png=png, omissoes=omissoes)
    )
    for arquivo, conteudo in arquivos.items():
        destino = pasta / arquivo
        destino.write_bytes(conteudo if isinstance(conteudo, bytes) else conteudo.encode())
    zip_ = pacote.empacotar(
        {k: v for k, v in arquivos.items() if k != "manifesto.json"}
        | {"manifesto.json": arquivos["manifesto.json"]}
    )
    (pasta / f"kit-{ficha['numero']}-{ficha['ano']}.zip").write_bytes(zip_)
    relatorio["zip_sha256"] = hashlib.sha256(zip_).hexdigest()[:16]
    relatorio["impressao"] = ficha["impressao"][:8]
    (pasta / "conferencia.json").write_text(pacote.json_bonito(relatorio))
    print(
        f"\n[{nome}] modo={ficha['modo']} problemas={relatorio['problemas']} "
        f"omissoes={omissoes} recusa={relatorio.get('peca_recusada')}"
    )
    assert relatorio["problemas"] == [], relatorio["problemas"]
    return ficha


def _so_um_perfil(conteudo):
    conteudo["profiles"] = conteudo["profiles"][:1]
    _podar_referencias(conteudo)


def _sem_localidade(conteudo):
    # Uma opção com localidade e outra sem: a ausência some da frase, e não vira "não informado".
    conteudo["profiles"] = conteudo["profiles"][:2]
    conteudo["profiles"][1]["locality"] = ""
    _podar_referencias(conteudo)


def _sem_periodo(conteudo):
    for evento in conteudo["schedule"]:
        evento["isRegistrationPeriod"] = False


def _podar_referencias(conteudo):
    """Documentos e sorteio que citam Perfil retirado: o rascunho recusaria a referência órfã."""
    restantes = {perfil["id"] for perfil in conteudo["profiles"]}
    for documento in conteudo.get("documentRequirements") or []:
        alcance = documento.get("profileIds")
        if alcance:
            documento["profileIds"] = [p for p in alcance if p in restantes]


# Um caso por Edital: cada um com a sua transação, que o rollback desfaz — o corpus reusa número e
# identidades, e dois Editais 91/2026 no mesmo banco colidem.


def test_91_futuro_aberto_e_prorrogado(api_client):
    """Um curso em quatro polos, título longo; depois, prorrogação e cinco vagas a mais num polo."""
    deslocamento = _deslocamento()
    edital, _ = publicar_do_corpus(
        api_client, "91", ate=1, deslocamento=deslocamento, chave="poc-91"
    )
    # O instante de cada geração é tomado **depois** da publicação: a versão nasce com `valid_from`
    # no instante do ato, e antes dele não há conteúdo vigente.
    futuro = gerar(
        "91-inscricoes-futuras",
        edital.id,
        timezone.now(),
        descricao="91/2026 publicado; inscrições ainda não começaram.",
    )
    assert futuro["periodo_estado"] == "futuro"
    no_periodo = _inicio(futuro) + timedelta(days=1)
    aberto = gerar(
        "91-inscricoes-em-andamento",
        edital.id,
        no_periodo,
        descricao="91/2026 no segundo dia do período.",
    )
    assert aberto["periodo_estado"] == "aberto"
    retificar_do_corpus(api_client, edital, "91", 2, deslocamento, chave="poc-91")
    prorrogado = gerar(
        "91-prorrogado-por-retificacao",
        edital.id,
        no_periodo,
        anterior=aberto,
        descricao="91/2026 depois da Retificação nº 1: prazo prorrogado e 45 vagas num polo.",
    )
    assert prorrogado["prorrogado"] and prorrogado["impressao"] != aberto["impressao"]


def test_01_retificacao_a_vigorar(api_client):
    """Dois Perfis, um só de cadastro reserva; prorrogação publicada com vigência futura."""
    edital, _ = publicar_do_corpus(api_client, "01", deslocamento=_deslocamento(), chave="poc-01")
    em_aberto = parse_datetime(
        ficha_do_edital(edital.id, agora=timezone.now(), base_url=BASE).inicio
    ) + timedelta(hours=1)
    a_vigorar = gerar(
        "01-retificacao-a-vigorar",
        edital.id,
        em_aberto,
        descricao="01/2026 com a prorrogação publicada, mas ainda não vigente.",
    )
    assert a_vigorar["retificacao_a_vigorar"]
    depois = parse_datetime(a_vigorar["retificacao_a_vigorar"]) + timedelta(hours=1)
    gerar(
        "01-depois-da-vigencia",
        edital.id,
        depois,
        anterior=a_vigorar,
        descricao="01/2026 depois de a prorrogação passar a valer.",
    )


def test_92_muitos_perfis(api_client):
    """Dezoito Perfis e título muito longo; Retificação que não toca o material."""
    deslocamento = _deslocamento()
    edital, _ = publicar_do_corpus(
        api_client, "92", ate=1, deslocamento=deslocamento, chave="poc-92"
    )
    no_periodo = parse_datetime(
        ficha_do_edital(edital.id, agora=timezone.now(), base_url=BASE).inicio
    ) + timedelta(days=1)
    antes = gerar(
        "92-muitos-perfis",
        edital.id,
        no_periodo,
        descricao="92/2026: 18 opções, só cadastro reserva em 16 delas.",
    )
    retificar_do_corpus(api_client, edital, "92", 2, deslocamento, chave="poc-92")
    gerar(
        "92-retificacao-que-nao-muda-o-material",
        edital.id,
        no_periodo,
        anterior=antes,
        descricao="92/2026 depois de Retificação que só muda uma seção textual.",
    )


@pytest.mark.parametrize(
    ("nome", "mudar", "descricao"),
    [
        ("um-perfil", _so_um_perfil, "91/2026 reduzido a um Perfil."),
        ("localidade-ausente", _sem_localidade, "91/2026 com dois Perfis, um sem localidade."),
        ("sem-periodo-designado", _sem_periodo, "91/2026 sem período de inscrições designado."),
    ],
)
def test_variacoes_do_91(api_client, nome, mudar, descricao):
    """O que o corpus não tem, pelo `mudar` de `publicar_do_corpus`."""
    edital, _ = publicar_do_corpus(
        api_client, "91", deslocamento=_deslocamento(), chave=f"poc-{nome}", mudar=mudar
    )
    agora = timezone.now()
    inicio = ficha_do_edital(edital.id, agora=agora, base_url=BASE).inicio
    gerar(
        nome,
        edital.id,
        parse_datetime(inicio) + timedelta(days=1) if inicio else agora,
        descricao=descricao,
    )


def test_cancelado_dentro_do_periodo(api_client):
    """O desfecho vence o período: não há material."""
    edital = editais_do_piloto.cancelado(api_client)
    ficha = gerar(
        "cancelado",
        edital.id,
        timezone.now(),
        descricao="Edital cancelado pelo ato de domínio, dentro do período.",
    )
    assert ficha["modo"] == "indisponivel"
