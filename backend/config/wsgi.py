import os

from django.core.wsgi import get_wsgi_application

# **O padrão é a produção, e não o desenvolvimento** (003, `FR-016`; RC-124). Fora do `runserver`,
# quem carrega este arquivo é um servidor WSGI, e servidor WSGI é implantação: cair em `development`
# na falta da variável subia o sistema com `DEBUG` ligado, a fonte de demonstração do sorteio e
# nenhuma das barreiras de `production.py` — que existem justamente para recusar subir mal
# configurado. Agora a variável esquecida é recusa na inicialização, com a mensagem que nomeia o
# que falta.
#
# O `runserver` continua em `development`: ele carrega este módulo pelo `WSGI_APPLICATION` com a
# variável já definida pelo `manage.py`, e o `setdefault` abaixo não a sobrescreve.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
application = get_wsgi_application()
