from django.apps import AppConfig


class RequerimentosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "processo_seletivo.requerimentos"
    verbose_name = "Requerimento de Matrícula"

    def ready(self):
        """Liga a porta do endereço à base local — **o único lugar que conhece as duas pontas**.

        É aqui, e não no domínio, porque a `FR-389` proíbe o domínio de nomear fornecedor. Trocar a
        base local por outra implementação é trocar esta linha, e nada mais; enquanto a injeção
        vivesse dentro de `domain/endereco.py`, a troca alcançaria o domínio e a porta seria porta
        só no nome.

        O import mora dentro do método porque `infrastructure` alcança o modelo, e importar modelo
        no topo de `apps.py` roda antes de o registro de apps estar pronto.
        """
        from processo_seletivo.requerimentos.domain import endereco
        from processo_seletivo.requerimentos.infrastructure import referencia_local

        endereco.registrar_fornecedor(referencia_local.buscar)
