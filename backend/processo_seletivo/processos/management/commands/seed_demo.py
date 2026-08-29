"""Popula uma demonstração navegável, percorrendo o fluxo normativo real.

Não insere nada direto no banco: usa os mesmos commands da API, com atores distintos, para que
a segregação de funções e a auditoria fiquem verdadeiras. Serve para inspecionar o sistema no
ar; não é fixture de teste nem carga de produção.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.publish_edital import (
    homologate_edital,
    publish_edital,
    submit_edital,
)
from processo_seletivo.publicacoes.application.retificacoes import (
    create_retification,
    publish_retification,
    transition_retification,
)
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor

ESCOPO = "cefor"
SIGNATARIO = {
    "authorityId": "00000000-0000-0000-0000-0000000000a1",
    "name": "Reitora do IFES",
    "role": "Reitora",
}


def ator(subject, *permissoes):
    return Actor(subject, ESCOPO, frozenset(permissoes))


def perfis(numero):
    return [
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000b1",
            "code": "DOC-INFO",
            "name": "Professor de Informática",
            "description": "Docência em Informática no ensino técnico e superior.",
            "requirements": ["Mestrado em Computação ou área afim"],
            "immediateVacancies": 2,
            "reserveType": "LIMITED",
            "reserveLimit": 6,
            "locality": "Campus Serra",
            "competitionModalities": [
                {"code": "AC", "name": "Ampla concorrência"},
                {
                    "code": "PPP",
                    "name": "Pessoas pretas, pardas e indígenas",
                    "normativeRule": {
                        "foundation": "Lei 12.990/2014",
                        "version": "2014-06-09",
                        "percentage": "20.0000",
                        "rounding": {"modo": "PARA_CIMA"},
                    },
                },
            ],
        },
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000b2",
            "code": "TEC-LAB",
            "name": "Técnico de Laboratório",
            "description": "Apoio técnico aos laboratórios de informática.",
            "requirements": ["Curso técnico em Informática"],
            "immediateVacancies": 0,
            "reserveType": "UNLIMITED",
            "locality": "Campus Vitória",
            "competitionModalities": [{"code": "AC", "name": "Ampla concorrência"}],
        },
    ]


def cronograma(agora, numero):
    # `type` é texto livre e a tela o exibe como foi escrito: "INSCRICAO" aparecia cru no
    # Cronograma e no PDF. Aqui vale escrever como um Edital de verdade escreveria.
    marcos = [
        ("Inscrições", "Inscrições pelo sistema, com isenção de taxa até o 5º dia.", 0, 20),
        ("Prova objetiva", "Aplicação da prova no Campus Vitória, em turno único.", 35, None),
        ("Resultado final", "Resultado final e abertura do prazo recursal.", 60, None),
    ]
    return [
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000c{indice}",
            "type": tipo,
            "description": descricao,
            # A camada de aplicação recebe datetime; a conversão de ISO é do serializer.
            "startAt": agora + timedelta(days=inicio),
            "endAt": None if fim is None else agora + timedelta(days=fim),
            "order": indice,
        }
        for indice, (tipo, descricao, inicio, fim) in enumerate(marcos, 1)
    ]



# Os Perfis do seed são fixos — docência em Informática e técnico de laboratório. Fazer o
# título variar sem variar o conteúdo produziria um Processo anunciando "Tutoria a distância"
# cujos Perfis são outros; quem precisa de execuções distintas usa --titulo.
AREA = "Professor Substituto e Técnico-Administrativo"


def _titulo_do_processo(ano, titulo_informado):
    return titulo_informado or f"Processo Seletivo Simplificado {ano}"


class Command(BaseCommand):
    help = "Cria um Processo Seletivo demonstrativo, publicado e retificado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--codigo", default="PS-DEMO-2026", help="identificação institucional do Processo"
        )
        parser.add_argument(
            "--numero",
            default="01",
            help="número do Edital; precisa ser único no escopo para o mesmo ano",
        )
        parser.add_argument(
            "--titulo",
            default=None,
            help="título do Processo (padrão: Processo Seletivo Simplificado <ano>)",
        )
        parser.add_argument(
            "--ano", type=int, default=None, help="ano do Edital (padrão: o ano corrente)"
        )

    def handle(self, *args, **opcoes):
        codigo = opcoes["codigo"]
        existente = ProcessoSeletivo.objects.filter(
            institution_scope=ESCOPO, institutional_code=codigo
        )
        if existente.exists():
            # Não há `--recriar`, e é decisão e não esquecimento: apagar a demonstração exigiria
            # excluir Publicações, que a Constituição proíbe e que as triggers de imutabilidade
            # recusam. A saída é criar outra demonstração com outro código.
            raise CommandError(
                f"Já existe Processo com o código {codigo}. Use --codigo para outro identificador."
            )

        numero = opcoes["numero"]
        agora = timezone.now()
        ano = opcoes["ano"] or agora.year
        titulo = _titulo_do_processo(ano, opcoes["titulo"])
        elaborador = ator("ana.elaboradora", "processo:criar", "edital:elaborar", "edital:submeter")
        homologador = ator("bruno.homologador", "edital:homologar")
        publicador = ator("carla.publicadora", "edital:publicar")

        with transaction.atomic():
            processo, _ = self._criar(elaborador, codigo, numero, ano, titulo)
            edital = Edital.objects.get(processo=processo)
            self._elaborar(elaborador, edital, agora, numero)
            self._publicar(elaborador, homologador, publicador, edital)

        self._retificar(edital, agora)
        self._resumo(processo, edital)

    def _criar(self, elaborador, codigo, numero, ano, titulo):
        self.stdout.write("Criando Processo e primeiro Edital…")
        from processo_seletivo.processos.application.commands import (
            create_process_with_first_edital,
        )

        return create_process_with_first_edital(
            actor=elaborador,
            data={
                "institutionalCode": codigo,
                "title": titulo,
                "firstEdital": {
                    "number": numero,
                    "year": ano,
                    "title": f"Edital {numero}/{ano} — {AREA}",
                    "description": "Seleção simplificada para professor substituto e técnico.",
                },
            },
            idempotency_key=f"seed-demo-{codigo}-{numero}-01",
            correlation_id="seed-demo",
        )

    def _elaborar(self, elaborador, edital, agora, numero):
        from processo_seletivo.editais.application.draft import replace_draft

        self.stdout.write("Elaborando Perfis e Cronograma…")
        replace_draft(
            actor=elaborador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            profiles=perfis(numero),
            schedule=cronograma(agora, numero),
            correlation_id="seed-demo",
        )
        edital.refresh_from_db()

    def _publicar(self, elaborador, homologador, publicador, edital):
        self.stdout.write("Submetendo, homologando e publicando…")
        edital, _, _ = submit_edital(
            actor=elaborador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            idempotency_key=f"seed-demo-sub-{edital.id.hex[:12]}",
            correlation_id="seed-demo",
        )
        edital, _ = homologate_edital(
            actor=homologador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            reason="Conteúdo conferido pela comissão.",
            idempotency_key=f"seed-demo-hom-{edital.id.hex[:12]}",
            correlation_id="seed-demo",
        )
        publish_edital(
            actor=publicador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            signatory=SIGNATARIO,
            reason="Publicação do edital original.",
            idempotency_key=f"seed-demo-pub-{edital.id.hex[:12]}",
            correlation_id="seed-demo",
        )

    def _retificar(self, edital, agora):
        """Uma vigente e outra com vigência futura, para a consulta temporal ter o que mostrar."""
        elaborador = ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
        homologador = ator("bruno.homologador", "retificacao:homologar")
        publicador = ator("carla.publicadora", "retificacao:publicar")

        for sufixo, mudancas, vigencia, motivo in (
            (
                "a",
                [
                    {
                        "targetPath": "/profiles/0/immediateVacancies",
                        "operation": "REPLACE",
                        "newValue": 3,
                    }
                ],
                None,
                "Ampliação de uma vaga imediata no perfil de docência.",
            ),
            (
                "b",
                [
                    {
                        "targetPath": "/schedule/0/endAt",
                        "operation": "REPLACE",
                        "newValue": (agora + timedelta(days=30)).isoformat(),
                    }
                ],
                agora + timedelta(days=15),
                "Prorrogação das inscrições, vigente a partir de 15 dias.",
            ),
        ):
            self.stdout.write(f"Publicando Retificação {sufixo}…")
            base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
            dados = {
                "baseSnapshotId": base.id,
                "justification": motivo,
                "changes": mudancas,
            }
            if vigencia is not None:
                dados["effectiveAt"] = vigencia
            correlacao = f"seed-demo-{sufixo}"
            retificacao, _ = create_retification(
                actor=elaborador,
                edital_id=edital.id,
                data=dados,
                idempotency_key=f"seed-demo-{sufixo}-elaborar",
                correlation_id=correlacao,
            )
            for acao, ator_da_vez in (
                ("submeter", elaborador),
                ("homologar", homologador),
            ):
                retificacao, _ = transition_retification(
                    actor=ator_da_vez,
                    retificacao_id=retificacao.id,
                    expected_revision=retificacao.revision,
                    action=acao,
                    reason="Conferido.",
                    idempotency_key=f"seed-demo-{sufixo}-{acao}",
                    correlation_id=correlacao,
                )
            publish_retification(
                actor=publicador,
                retificacao_id=retificacao.id,
                expected_revision=retificacao.revision,
                signatory=SIGNATARIO,
                idempotency_key=f"seed-demo-{sufixo}-publicar",
                correlation_id=correlacao,
            )

    def _resumo(self, processo, edital):
        publicada = Retificacao.objects.filter(
            edital=edital, status=Retificacao.Status.PUBLICADA
        ).first()
        versoes = VersaoConsolidada.objects.filter(edital=edital).count()
        self.stdout.write(self.style.SUCCESS("\nDemonstração criada.\n"))
        self.stdout.write(f"  Processo  {processo.institutional_code}  {processo.id}")
        self.stdout.write(f"  Edital    {edital.number}/{edital.year}  {edital.id}")
        self.stdout.write(f"  Versões consolidadas: {versoes}\n")
        self.stdout.write("Abra no navegador (consulta pública, sem autenticação):")
        for rotulo, caminho in (
            ("versão vigente", f"/api/v1/public/editais/{edital.id}/versao-vigente"),
            ("histórico", f"/api/v1/public/editais/{edital.id}/historico"),
            ("retificação", f"/api/v1/public/retificacoes/{publicada.id}" if publicada else ""),
            ("saúde", "/health"),
        ):
            if caminho:
                self.stdout.write(f"  {rotulo:16} http://127.0.0.1:8000{caminho}")
