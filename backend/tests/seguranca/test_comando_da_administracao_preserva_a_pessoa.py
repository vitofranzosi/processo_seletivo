"""O comando da administração institucional não estraga quem já existe (revisão do #346).

Dois defeitos do comando da `106`, achados na revisão do #346 e corrigidos como correção da
dependência:

- **Apagava o nome e o e-mail** de quem já tinha entrado, quando rodado sem `--nome` e `--email`:
  localizava a pessoa por `resolver_pessoa`, que atualiza os dois com o que chega — e o que chegava
  era o vazio da linha de comando.
- **Concedia a quem estava suspenso ou desativado**, sem aviso.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.models import Vinculo
from tests.fixtures import provedor_simulado
from tests.seguranca.apoio import pessoa

pytestmark = pytest.mark.django_db


def _conceder(identificador, *extra):
    call_command(
        "conceder_administracao_institucional",
        "--provedor",
        provedor_simulado.NOME,
        "--identificador",
        identificador,
        "--motivo",
        "Portaria 100/2026",
        *extra,
    )


def test_quem_ja_entrou_continua_com_o_nome_e_o_email():
    paula = pessoa("paula", nome="Paula Prado", email="paula@ifes.edu.br")

    _conceder("paula")

    paula.refresh_from_db()
    assert (paula.first_name, paula.email) == ("Paula Prado", "paula@ifes.edu.br")
    assert Vinculo.objects.get(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).pessoa == paula


def test_quem_nunca_entrou_nasce_com_o_que_o_comando_informa():
    _conceder("nova", "--nome", "Nova Reitoria", "--email", "nova@ifes.edu.br")

    nova = Vinculo.objects.get(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).pessoa
    assert (nova.first_name, nova.email) == ("Nova Reitoria", "nova@ifes.edu.br")


def test_desativada_nao_recebe_a_administracao():
    paula = pessoa("paula", nome="Paula Prado")
    get_user_model().objects.filter(pk=paula.pk).update(is_active=False)

    with pytest.raises(CommandError, match=acessos.PESSOA_INDISPONIVEL):
        _conceder("paula")
    assert not Vinculo.objects.exists()
