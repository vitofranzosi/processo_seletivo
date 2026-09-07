"""Superado o Resultado, a cadeia a jusante reage — **e não se conserta sozinha**.

É a metade menos óbvia da feature, e a mais importante para a instituição: o deferimento não
reescreve o ato de ordenação nem a publicação. Ele torna o ato **obsoleto**, com a causa nomeada, e
a publicação daquele ato passa a ser recusada com o caminho — que é emitir um ato novo.

```text
deferimento  →  o universo do ato passa a citar Resultado que não é mais o vigente
             →  o ato fica obsoleto, e a divergência diz por quê
             →  publicar aquele ato é recusado, nomeando o caminho
             →  e NADA é emitido ou publicado automaticamente
```

**O automático seria pior do que a recusa.** Emitir ato novo sem que ninguém decida seria a 018
praticando ato da 015, e republicar sem que ninguém assine seria praticar ato da 017 — as duas
autoridades que a D-005 mantém separadas (FR-080, FR-108, SC-010).

Este módulo também é a prova viva de por que o filtro de vigência existe: sem ele, o universo do
ato continuaria citando o Resultado superado, `comparar()` não veria mudança nenhuma, o ato nunca
ficaria obsoleto, e toda a cadeia ficaria cega ao recurso — **em silêncio**.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.classificacao.domain.universo import SUPERACAO
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.divulgacao.domain.publicabilidade import DESATUALIZADO, IMPEDIMENTO, aferir
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """Quem recorre foi **eliminada** com 55 numa Etapa de mínima 60 — ela está fora do universo.

    A eliminação é o que torna o cenário interessante: deferir a reabilita, e reabilitá-la muda o
    conjunto de participantes do marco — que é a divergência mais consequente das três.
    """
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=115, codigo="0815"
    )


def deferir(peca):
    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=peca["cenario"]["etapa"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-jusante",
    )


def estado(peca):
    return estado_do_marco(edital=peca["cenario"]["edital"], marco_id=peca["cenario"]["marco"])


def test_antes_do_deferimento_o_ato_nao_esta_obsoleto(peca):
    """A prova de que a obsolescência abaixo é **do deferimento**, e não do cenário."""
    assert estado(peca)["obsoleto"] is False


def test_o_deferimento_torna_o_ato_obsoleto_com_a_causa_nomeada(peca):
    """Sem a causa, a tela diria "algo mudou" e quem lê sairia procurando o quê (FR-078).

    Aqui a causa é a superação: quem recorreu já participava do marco, e o que mudou foi **qual**
    Resultado o universo cita. A reintegração de quem estava fora é a outra causa, e tem nome
    próprio porque é outra coisa — ela é exercitada pela US8.
    """
    deferir(peca)

    situacao = estado(peca)

    assert situacao["obsoleto"] is True
    causas = {item.get("causa", "") for item in situacao["divergencias"]}
    assert SUPERACAO in causas
    assert any(SUPERACAO in item["descricao"] for item in situacao["divergencias"])


def test_publicar_o_ato_obsoleto_passa_a_ser_recusado_com_o_caminho(peca):
    """A recusa nomeia o caminho: emitir ato novo. "Não é possível" sem caminho é um beco."""
    deferir(peca)
    ato = AtoDeOrdenacao.objects.get(pk=peca["cenario"]["ato"].id)

    afericao = aferir(edital=peca["cenario"]["edital"], marco_id=peca["cenario"]["marco"], ato=ato)

    assert afericao.nivel == IMPEDIMENTO
    assert afericao.codigo == DESATUALIZADO
    assert afericao.mensagem


def test_o_comando_de_publicacao_recusa_o_ato_obsoleto(peca):
    """A aferição não basta: quem grava é o comando, e é ele que precisa recusar."""
    from tests.fixtures.divulgacao import publicar_o_ato

    deferir(peca)

    with pytest.raises(DomainError) as recusa:
        publicar_o_ato(peca["cenario"], chave="publicar-depois-do-deferimento")

    assert recusa.value.status in (409, 422)


def test_nenhum_ato_nem_publicacao_nasce_automaticamente(peca):
    """**A 018 não pratica ato da 015 nem da 017** (FR-108, SC-010).

    Emitir ato novo sem que ninguém decida, ou republicar sem que ninguém assine, seria a feature
    tomando para si autoridades que a D-005 mantém separadas. O deferimento produz o sucessor do
    Resultado e para aí; o resto é decisão de quem tem o poder do ato.
    """
    antes = (AtoDeOrdenacao.objects.count(), PublicacaoResultado.objects.count())

    deferir(peca)

    assert (AtoDeOrdenacao.objects.count(), PublicacaoResultado.objects.count()) == antes


def test_a_publicacao_ja_feita_nao_e_alterada(peca):
    """O que foi divulgado continua sendo o que foi divulgado (FR-091).

    Reescrever a publicação anterior apagaria o que a instituição de fato afirmou naquele dia — e é
    justamente contra isso que a sucessão existe.
    """
    publicada = peca["publicacao"]
    antes = (publicada.publicado_em, publicada.publicado_por, publicada.conteudo_publico_hash)

    deferir(peca)

    publicada.refresh_from_db()
    assert (
        publicada.publicado_em,
        publicada.publicado_por,
        publicada.conteudo_publico_hash,
    ) == antes


def test_emitir_ato_novo_e_o_caminho_e_ele_incorpora_o_sucessor(peca):
    """O caminho que a recusa nomeia precisa **funcionar** — senão é um beco com placa.

    Emitido o ato novo, o universo passa a citar o Resultado sucessor, quem foi reabilitada volta a
    ter posição, e o marco deixa de estar obsoleto.
    """
    from tests.fixtures.divulgacao import emitir

    _decisao, sucessor = deferir(peca)

    emitir(peca["cenario"], _gestor_do_cenario(peca), chave="emitir-depois-do-deferimento")

    situacao = estado(peca)
    assert situacao["obsoleto"] is False
    citados = {
        str(item.get("id")) for item in situacao["vigente"].universo.get("stageResults") or []
    }
    assert str(sucessor.id) in citados
    assert str(peca["superado"].id) not in citados


def _gestor_do_cenario(peca):
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")
