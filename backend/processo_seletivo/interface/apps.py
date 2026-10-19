from django.apps import AppConfig


class InterfaceConfig(AppConfig):
    name = "processo_seletivo.interface"

    def ready(self):
        """Registra a verificação das folhas estáticas (089) no `check` do Django.

        A tag mora em `shared/`, que não é app e não tem `ready`; a interface é a dona da folha
        comum e das duas bases que mais a usam. Sem este import, a verificação só existiria depois
        da primeira página renderizada — tarde demais para impedir a subida.
        """
        from processo_seletivo.shared import estaticos  # noqa: F401
