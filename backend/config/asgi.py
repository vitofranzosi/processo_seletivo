import os

from django.core.asgi import get_asgi_application

# **O padrão é a produção, e não o desenvolvimento** (003, `FR-016`; RC-124). Quem carrega este
# arquivo é um servidor ASGI — o `runserver` não passa por aqui —, e servidor ASGI é implantação:
# cair em `development` na falta da variável subia o sistema com `DEBUG` ligado, a fonte de
# demonstração do sorteio e nenhuma das barreiras de `production.py` — que existem justamente para
# recusar subir mal configurado. Agora a variável esquecida é recusa na inicialização, com a
# mensagem que nomeia o que falta.
#
# O ambiente local continua em `development`, pelo `manage.py`.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
application = get_asgi_application()
