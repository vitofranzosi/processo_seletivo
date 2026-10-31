"""Substitui a administração institucional de uma pessoa por outra, numa operação (107, `FR-3148`).

A revogação da anterior e a concessão à nova são da mesma transação, e vão à trilha com o mesmo
motivo e a mesma correlação: não há instante com o anterior ainda ativo, nem com uma administração
a mais. A pessoa nova é localizada pelo par do provedor, e criada só se nunca entrou.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.autenticacao import IdentidadeAutenticada, pessoa_para_implantacao
from processo_seletivo.seguranca.management.commands._pessoa_do_provedor import (
    argumentos_da_pessoa,
    pessoa_do_provedor,
)
from processo_seletivo.shared.api.problems import DomainError


class Command(BaseCommand):
    help = "Substitui a administração institucional de uma pessoa por outra."

    def add_arguments(self, parser):
        argumentos_da_pessoa(parser, "de-")
        argumentos_da_pessoa(parser, "para-")
        parser.add_argument("--motivo", required=True, help="O ato que determina a substituição.")
        parser.add_argument("--para-nome", default="", help="O nome, até a primeira entrada.")
        parser.add_argument("--para-email", default="", help="O e-mail, até a primeira entrada.")

    def handle(self, *args, **opcoes):
        de = pessoa_do_provedor(opcoes["de_provedor"], opcoes["de_identificador"])
        identidade = IdentidadeAutenticada(
            opcoes["para_provedor"].strip(),
            opcoes["para_identificador"].strip(),
            opcoes["para_nome"].strip(),
            opcoes["para_email"].strip(),
        )
        try:
            # Junto, para que a recusa não deixe para trás uma pessoa criada sem vínculo.
            with transaction.atomic():
                # Quem já entrou fica como está; o vazio de `--para-nome` não apaga o nome dela, e a
                # linha dela não é escrita antes da trava global (revisão do #346).
                para = pessoa_para_implantacao(identidade)
                if para is None:
                    raise CommandError("provedor e identificador da pessoa nova são obrigatórios.")
                acessos.substituir_administracao_institucional(
                    de=de, para=para, motivo=opcoes["motivo"], now=timezone.now()
                )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(
            f"Administração institucional passada de {de.username} a {para.username}."
        )
