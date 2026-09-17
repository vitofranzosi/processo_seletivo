"""A situação da base de CEP, para o deploy conferir e para o alerta disparar (029, `T-015`).

**Três perguntas, e o código de saída responde a elas.** Existe uma base válida? A última tentativa
de atualização falhou? A base vigente ficou velha demais?

**Por que um comando e não um `check` de readiness.** A `FR-390` é categórica: base ausente **não**
impede preenchimento, envio, inscrição nem matrícula. Uma verificação que derrubasse o readiness
transformaria um serviço auxiliar em porta de entrada do processo — exatamente o que a decisão de
carregar localmente existe para evitar. O deploy **confere e informa**; ele não recusa subir.

**O código de saída é a interface com o alerta.** `0` é normal, `1` é *"alguém precisa olhar"*. É o
que um `cron` e qualquer coletor entendem sem integração, e é por isso que a saída também é legível
por pessoa: quem receber o alerta às três da manhã lê a frase, não o JSON.

**A idade é medida da conclusão, e não do início.** Carga que começou e não terminou não é base
nova; é base que não existe.
"""

import json
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from processo_seletivo.requerimentos.models import CargaDeCep

# **Sessenta dias, e não trinta.** O job é mensal; alertar em trinta faria toda execução atrasada
# por um dia virar incidente. O dobro do intervalo é o que distingue *"atrasou"* de *"parou"*.
DIAS_ATE_ENVELHECER = 60


class Command(BaseCommand):
    help = "Informa a situação da base de referência de CEP, e sai com 1 quando algo pede atenção."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="saída para coletor de métrica")
        parser.add_argument(
            "--dias", type=int, default=DIAS_ATE_ENVELHECER, help="idade máxima aceitável"
        )

    def handle(self, *args, **opcoes):
        vigente = CargaDeCep.objects.filter(vigente=True).first()
        ultima = CargaDeCep.objects.order_by("-geracao").first()
        agora = timezone.now()
        situacao = {
            "vigente": vigente.geracao if vigente else None,
            "linhas": vigente.linhas if vigente else 0,
            "carregada_em": vigente.concluida_em.isoformat()
            if vigente and vigente.concluida_em
            else None,
            "origem": vigente.origem if vigente else "",
            "checksum": vigente.checksum if vigente else "",
            "dias": None,
            "alertas": [],
        }
        if vigente is None:
            # **Não é falha do sistema, e a frase diz isso.** Instalação sem a base funciona; o que
            # ela perde é o preenchimento assistido, e quem opera precisa saber que perdeu.
            situacao["alertas"].append(
                "não há base de CEP carregada: o preenchimento assistido está desligado, e o "
                "endereço é digitado à mão"
            )
        else:
            idade = agora - (vigente.concluida_em or vigente.iniciada_em)
            situacao["dias"] = idade.days
            if idade > timedelta(days=opcoes["dias"]):
                situacao["alertas"].append(
                    f"a base de CEP tem {idade.days} dias: a atualização mensal não está rodando"
                )
        if ultima is not None and ultima.falha:
            situacao["alertas"].append(
                f"a última tentativa de carga (geração {ultima.geracao}) falhou: {ultima.falha}"
            )
        self._dizer(situacao, opcoes["json"])
        # **Sem `CommandError`**: ele imprime um traceback, e isto não é erro de programa — é estado
        # do mundo que alguém precisa olhar. O código de saída basta.
        if situacao["alertas"]:
            raise SystemExit(1)

    def _dizer(self, situacao, como_json):
        if como_json:
            self.stdout.write(json.dumps(situacao, ensure_ascii=False))
            return
        if situacao["vigente"] is None:
            self.stdout.write("Base de CEP: ausente.")
        else:
            self.stdout.write(
                f"Base de CEP: geração {situacao['vigente']}, {situacao['linhas']} linhas, "
                f"carregada há {situacao['dias']} dia(s) de {situacao['origem']}."
            )
        for alerta in situacao["alertas"]:
            self.stderr.write(f"ATENÇÃO: {alerta}")
