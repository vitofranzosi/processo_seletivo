from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.canonical import canonical_sha256


def test_state_vocabularies_are_distinct():
    assert ProcessoSeletivo.Status.ENCERRADO != ProcessoSeletivo.Status.CANCELADO
    assert Edital.Status.ENCERRADO != Edital.Status.CANCELADO
    assert ProcessoSeletivo.Status.EM_ELABORACAO == "EM_ELABORACAO"


def test_actor_denies_unknown_permission_by_default():
    actor = Actor("a", "cefor", frozenset({"processo:criar"}))
    assert actor.can("processo:criar")
    assert not actor.can("processo:cancelar")


def test_canonical_hash_is_independent_of_key_order():
    assert canonical_sha256({"b": 2, "a": 1}) == canonical_sha256({"a": 1, "b": 2})
