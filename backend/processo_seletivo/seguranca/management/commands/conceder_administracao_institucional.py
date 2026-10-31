"""Concede a administração institucional, pela implantação (106, `FR-3029`; 110, `D-002`).

É o único ponto que cria poder institucional: nenhuma tela o concede, e o próprio administrador
institucional não concede outro. Roda com o acesso de quem implanta, grava sob o ator `implantacao`
e exige o motivo — o número do ato que designou a pessoa. A pessoa é localizada, ou criada, pelo
par provedor e identificador, como na entrada; nunca pelo e-mail.

Quem é a pessoa, e por qual ato, é decisão do usuário (proposta 2 da spec), e não deste comando.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.autenticacao import IdentidadeAutenticada, pessoa_para_implantacao
from processo_seletivo.shared.api.problems import DomainError


class Command(BaseCommand):
    help = (
        "Concede a administração institucional — acessos das unidades e registro de Unidades — "
        "a uma identidade do provedor."
    )

    def add_arguments(self, parser):
        parser.add_argument("--provedor", required=True, help="O nome do adaptador institucional.")
        parser.add_argument(
            "--identificador", required=True, help="O identificador estável no provedor."
        )
        parser.add_argument("--motivo", required=True, help="O ato que designou a pessoa.")
        parser.add_argument("--nome", default="", help="O nome, até a primeira entrada.")
        parser.add_argument("--email", default="", help="O e-mail, até a primeira entrada.")
        parser.add_argument(
            "--adicional",
            action="store_true",
            help="Concede a mais uma pessoa quando já há administração institucional vigente.",
        )

    def handle(self, *args, **opcoes):
        identidade = IdentidadeAutenticada(
            opcoes["provedor"].strip(),
            opcoes["identificador"].strip(),
            opcoes["nome"].strip(),
            opcoes["email"].strip(),
        )
        try:
            # Junto, para que a recusa não deixe para trás uma pessoa criada sem vínculo.
            with transaction.atomic():
                pessoa = pessoa_para_implantacao(identidade)
                if pessoa is None:
                    raise CommandError("provedor e identificador são obrigatórios.")
                vinculo = acessos.conceder_administracao_institucional(
                    pessoa=pessoa,
                    motivo=opcoes["motivo"],
                    adicional=opcoes["adicional"],
                    now=timezone.now(),
                )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(
            f"Administração institucional concedida a {pessoa.username} "
            f"({identidade.provedor}:{identidade.identificador}), vínculo {vinculo.pk}."
        )
