"""Maria e João existem como identidades persistidas neste diretório (010).

A abertura de rascunho passou a exigir que a linha da identidade exista — sem isso uma inscrição
poderia nascer órfã de uma identidade descartada. Os testes da jornada, da titularidade e da
interface pressupõem as duas do mesmo jeito que a realidade pressupõe.

*Autouse* aqui, e não na raiz: registrá-las em todo teste de banco poluiria os que **contam**
identidades, e contagem poluída é teste que passa a medir a `fixture` em vez do sistema.
"""

import pytest


@pytest.fixture(autouse=True)
def _candidatos_registrados(request):
    if "django_db_setup" not in request.fixturenames:
        return
    from tests.fixtures.candidato import JOAO, MARIA, registrar

    for identidade in (MARIA, JOAO):
        registrar(identidade)
