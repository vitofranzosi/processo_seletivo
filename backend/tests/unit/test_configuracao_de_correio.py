"""O limite da conexão com o servidor de correio existe, e chega a quem conecta (066, `R-006`).

**Sem ele, um servidor que aceita a conexão e não responde prende o worker** até os 120 s do
gunicorn — e o código de acesso é o único fator de autenticação do candidato (gap I-4 do runbook).
O backend SMTP do Django aplica o setting à conexão, e por isso um teste basta para os quatro
envios.
"""

from django.conf import settings
from django.core.mail import get_connection


def test_o_timeout_existe_e_e_inteiro():
    assert isinstance(settings.EMAIL_TIMEOUT, int)
    assert settings.EMAIL_TIMEOUT > 0


def test_o_backend_smtp_recebe_o_timeout(settings):
    settings.EMAIL_TIMEOUT = 7

    conexao = get_connection("django.core.mail.backends.smtp.EmailBackend")

    assert conexao.timeout == 7
