"""Elimina os arquivos de vídeo de um Edital encerrado, pelo prazo de retenção (166, FR-7146 a FR-7149).

**Sem o prazo, recusa** (P-10): `VERIFICACAO_POR_VIDEO_RETENCAO_DIAS` não tem valor padrão. Com ele,
o comando exige o Edital e, para eliminar, `--confirmar`; sem a confirmação, só lista. O ator é
`implantacao`, como na exclusão dos registros do piloto: quem roda o comando é quem tem o acesso à
máquina, e não um papel conferido.
"""

from django.core.management.base import BaseCommand, CommandError

from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.verificacao.application import retencao


class Command(BaseCommand):
    help = "Elimina os arquivos de vídeo da verificação de um Edital, pelo prazo de retenção."

    def add_arguments(self, parser):
        parser.add_argument("--edital", required=True, help="a identidade do Edital")
        parser.add_argument(
            "--confirmar", action="store_true", help="elimina; sem ela, só lista"
        )

    def handle(self, *args, **opcoes):
        edital = Edital.objects.filter(pk=opcoes["edital"]).first()
        if edital is None:
            raise CommandError("Edital não encontrado.")
        try:
            prazo, _encerrado_em, videos = retencao.elegiveis(edital)
            if not opcoes["confirmar"]:
                self.stdout.write(
                    f"{len(videos)} arquivos de vídeo seriam eliminados (prazo de {prazo} dias). "
                    "Rode de novo com --confirmar para eliminar."
                )
                return
            eliminados = retencao.eliminar(
                edital=edital, actor=Actor(nomes.IMPLANTACAO, edital.institution_scope)
            )
        except DomainError as erro:
            raise CommandError(erro.detail) from None
        self.stdout.write(f"{eliminados} arquivos de vídeo eliminados")
