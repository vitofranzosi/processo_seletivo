"""Lista os cenários de treinamento e a situação de cada um (134, FR-4616)."""

from django.utils import timezone

from processo_seletivo.treinamento import servico
from processo_seletivo.treinamento.management.commands._base import ComandoDeTreinamento, linha
from processo_seletivo.treinamento.models import CenarioDeTreinamento


class Command(ComandoDeTreinamento):
    help = "Lista os cenários do catálogo, a rodada em uso de cada um e as rodadas substituídas."

    def executar(self, *, unidade, cenario, **_):
        for item in servico.escolher(cenario):
            atual = servico.situacao(item, unidade)
            detalhes = [item.nome]
            if atual.manifesto is not None:
                processo = atual.manifesto.processo
                detalhes += [
                    f"rodada {atual.manifesto.rodada}",
                    processo.institutional_code,
                    f"criado em {timezone.localtime(atual.manifesto.criado_em):%d/%m/%Y %H:%M}",
                ]
            detalhes += atual.avisos
            linha(self.stdout, item.codigo, atual.estado, detalhes)
            for antiga in CenarioDeTreinamento.objects.filter(
                unidade=unidade,
                codigo=item.codigo,
                situacao=CenarioDeTreinamento.Situacao.SUBSTITUIDO,
            ).order_by("rodada"):
                self.stdout.write(
                    f"         rodada {antiga.rodada} substituída — "
                    f"{antiga.processo.institutional_code} ({antiga.processo.status})"
                )
