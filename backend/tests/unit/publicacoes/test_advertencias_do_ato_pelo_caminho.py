"""A subtração dos impeditivos é pelo par (código, caminho) (issue #117; ED-13, auditoria 15/10).

`advertencias_do_ato` mostra na confirmação da Retificação o que a conferência sabe e não impede, e
tira da lista o que impediria a publicação. Pelo código, um impeditivo num Perfil apagava em
silêncio a advertência de mesmo código noutro Perfil, e nenhum teste falhava: a lista vinha menor.

Hoje nenhum código vive nas duas severidades em caminhos diferentes — o desenho os separa —, e por
isso o caso é montado aqui, sobre a validação substituída: o que se prende é a regra da subtração,
para o dia em que a premissa do desenho deixar de valer.
"""

from types import SimpleNamespace

from processo_seletivo.editais.domain.validation import Severity, ValidationFinding
from processo_seletivo.publicacoes.application import retificacoes

PERFIL_A = "/profiles/id=a/vacancyTable"
PERFIL_B = "/profiles/id=b/vacancyTable"


def _advertencias(monkeypatch, *, na_publicacao, na_retificacao):
    def validar(content, *, ato=None, topologia=None):
        return na_retificacao if ato == retificacoes.ATO_DE_RETIFICACAO else na_publicacao

    monkeypatch.setattr(retificacoes, "_changes_payload", lambda retificacao: [{}])
    monkeypatch.setattr(retificacoes, "_content_in_force", lambda edital, momento: {})
    monkeypatch.setattr(retificacoes, "apply_changes", lambda *args, **kwargs: ({}, None))
    monkeypatch.setattr(retificacoes, "topologia_publicada", lambda edital: None)
    monkeypatch.setattr(retificacoes, "validate_for_publication", validar)
    return retificacoes.advertencias_do_ato(SimpleNamespace(edital=None, effective_at=None))


def _achado(severidade, caminho):
    return ValidationFinding(severidade, "codigo_de_teste", "mensagem", caminho)


def test_impeditivo_num_perfil_nao_apaga_a_advertencia_de_outro(monkeypatch):
    advertencia_em_b = _achado(Severity.WARNING, PERFIL_B)

    advertencias = _advertencias(
        monkeypatch,
        na_publicacao=[_achado(Severity.BLOCKING_ERROR, PERFIL_A)],
        na_retificacao=[advertencia_em_b],
    )

    assert advertencias == [advertencia_em_b]


def test_no_mesmo_caminho_o_impeditivo_continua_subtraido(monkeypatch):
    """O outro lado: o par não pode deixar passar o que a subtração existe para tirar."""
    advertencias = _advertencias(
        monkeypatch,
        na_publicacao=[_achado(Severity.BLOCKING_ERROR, PERFIL_A)],
        na_retificacao=[_achado(Severity.WARNING, PERFIL_A)],
    )

    assert advertencias == []
