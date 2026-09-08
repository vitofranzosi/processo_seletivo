"""Popula uma demonstração navegável, percorrendo o fluxo normativo real.

Não insere nada direto no banco: usa os mesmos commands da API, com atores distintos, para que
a segregação de funções e a auditoria fiquem verdadeiras. Serve para inspecionar o sistema no
ar; não é fixture de teste nem carga de produção.
"""

import contextlib
from datetime import timedelta
from decimal import Decimal

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


@contextlib.contextmanager
def _relogio_atrasado(dias):
    """Roda a demonstração inteira como se ela tivesse acontecido há `dias` dias.

    **Não é atalho de produto, e nenhuma regra é afrouxada**: o certame percorre os mesmos
    commands, com as mesmas aferições; só o instante em que ele ocorreu é outro. Sem isso, um
    prazo recursal de cinco dias declarado hoje só poderia ser demonstrado **aberto** — e o que
    a instituição precisa ver é também a recusa depois do encerramento, que nenhuma tela alcança
    sem esperar cinco dias.

    O deslocamento vale só enquanto o `seed` roda; a aplicação continua lendo o relógio real, e é
    por isso que o resultado semeado aparece, no navegador, com a janela já encerrada.
    """
    if not dias:
        yield
        return
    real = timezone.now
    deslocamento = timedelta(days=dias)

    def atrasado():
        return real() - deslocamento

    timezone.now = atrasado
    try:
        yield
    finally:
        timezone.now = real


def ator(subject, *permissoes):
    return Actor(subject, ESCOPO, frozenset(permissoes))


def _janela_do_marco(escolha):
    if escolha == "negada":
        return {"appealWindow": {"admits": False, "durationDays": None, "unit": "DIAS_CORRIDOS"}}
    if escolha == "declarada":
        return {"appealWindow": {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}}
    return {}


def perfis(numero, *, janela_recursal="declarada"):
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
            # O marco classificatório da 015: a combinação das duas Etapas pontuadas, com o
            # desempate declarado sobre os fatos que `_declarar_fatos_e_teto` cria. Ele existe aqui
            # porque sem marco não há ordem a emitir — e sem ordem emitida não há resultado a
            # divulgar, que é a demonstração que a 017 precisa deixar navegável.
            "classificationMilestones": [
                {
                    "id": f"00000000-0000-0000-00{numero}-0000000000a1",
                    "code": "FINAL",
                    "name": "Classificação final",
                    "stages": [
                        f"00000000-0000-0000-00{numero}-0000000000d1",
                        f"00000000-0000-0000-00{numero}-0000000000d2",
                    ],
                    "operation": "SOMA_PONDERADA",
                    "normalization": "NENHUMA",
                    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                    "tiebreakers": [],
                    # A janela recursal declarada (018, degrau 8). Ela existe aqui porque o prazo é
                    # **norma publicada**, e a demonstração precisa mostrar o candidato lendo os
                    # instantes exatos de abertura e encerramento — e não uma tela que fala de
                    # recurso sem dizer até quando (FR-024, FR-030).
                    #
                    # Os **três** estados, porque são três coisas diferentes (FR-020, FR-113):
                    #
                    # ```text
                    # declarada  admite recurso, por cinco dias corridos
                    # negada     `admits` falso — norma publicada dizendo que não cabe por esta via
                    # ausente    a chave não existe, como em todo Edital anterior ao degrau 8
                    # ```
                    #
                    # A ausência devolve a tempestividade ao juízo humano motivado; a negativa a
                    # recusa nomeando a norma. Semear só a primeira deixaria as outras duas
                    # indemonstráveis no navegador.
                    **_janela_do_marco(janela_recursal),
                }
            ],
            "competitionModalities": [
                {
                    "id": f"00000000-0000-0000-00{numero}-0000000000e1",
                    "code": "AC",
                    "name": "Ampla concorrência",
                },
                {
                    "id": f"00000000-0000-0000-00{numero}-0000000000e2",
                    "code": "PPP",
                    "name": "Pessoas pretas, pardas e indígenas",
                    "normativeRule": {
                        "id": f"00000000-0000-0000-00{numero}-0000000000f2",
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
            "competitionModalities": [
                {
                    "id": f"00000000-0000-0000-00{numero}-0000000000e3",
                    "code": "AC",
                    "name": "Ampla concorrência",
                }
            ],
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
            # O primeiro marco é o período de inscrições, e a demonstração precisa que ele **se
            # diga** período: sem a marca, a vitrine não teria situação a anunciar e o candidato
            # não teria prazo. Chamar-se "Inscrições" não basta, e é essa a diferença.
            "isRegistrationPeriod": indice == 1,
        }
        for indice, (tipo, descricao, inicio, fim) in enumerate(marcos, 1)
    ]


def documentos_exigidos(numero):
    """As quatro aplicabilidades numa demonstração só.

    Identificação de todos, diploma do Perfil docente, autodeclaração de quem concorre na
    modalidade reservada. É o cenário do critério emblemático da `009`: o candidato de ampla
    concorrência recebe dois pedidos, e o da modalidade, três.
    """
    return [
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d1",
            "key": "identificacao",
            "name": "Documento de identificação com foto",
            "instructions": "Frente e verso em arquivo único.",
            "required": True,
            "order": 1,
        },
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d2",
            "key": "diploma",
            "name": "Diploma de graduação",
            "instructions": "Diploma ou certidão de conclusão, com histórico.",
            "required": True,
            "order": 2,
            "profileId": f"00000000-0000-0000-00{numero}-0000000000b1",
        },
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d3",
            "key": "autodeclaracao",
            "name": "Autodeclaração étnico-racial",
            "instructions": "Conforme o modelo do Anexo do Edital.",
            "required": True,
            "order": 3,
            "modalityId": f"00000000-0000-0000-00{numero}-0000000000e2",
        },
    ]


def etapas(numero):
    """Três Etapas: duas pontuadas e uma decisória.

    As duas primeiras mostram que as datas vêm do Cronograma e que o vínculo é opcional. A terceira
    é a análise documental dos Editais 35 e 57 do Cefor/Ifes — eliminatória, concluída por decisão e
    **sem nota**. Ela existe aqui porque a forma decisória precisa existir em ambiente de
    demonstração, e não só em teste: quem abre o sistema para conhecer precisa ver que avaliar nem
    sempre é pontuar (D-008).
    """
    return [
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d1",
            "name": "Prova objetiva",
            "order": 1,
            "weight": Decimal("2.0000"),
            "eliminatory": True,
            "classificatory": True,
            "minimumScore": Decimal("6.0000"),
            "scheduleEventId": f"00000000-0000-0000-00{numero}-0000000000c2",
        },
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d2",
            "name": "Análise de títulos",
            "order": 2,
            "weight": Decimal("1.0000"),
            "eliminatory": False,
            "classificatory": True,
            "minimumScore": None,
            "scheduleEventId": None,
        },
        {
            "id": f"00000000-0000-0000-00{numero}-0000000000d3",
            "name": "Análise documental",
            "order": 3,
            "weight": None,
            "eliminatory": True,
            "classificatory": False,
            # Nem mínima nem máxima: nesta forma elas não se aplicam, e publicá-las seria regra
            # normativa fictícia (FR-121).
            "minimumScore": None,
            "forma": "DECISORIA",
            "rotuloFavoravel": "Deferido",
            "rotuloDesfavoravel": "Indeferido",
            "scheduleEventId": None,
        },
    ]


# Os Perfis do seed são fixos — docência em Informática e técnico de laboratório. Fazer o
# título variar sem variar o conteúdo produziria um Processo anunciando "Tutoria a distância"
# cujos Perfis são outros; quem precisa de execuções distintas usa --titulo.
AREA = "Professor Substituto e Técnico-Administrativo"


def _numero_do_segundo_edital(numero):
    """Dois dígitos, derivados do primeiro e sempre diferentes dele.

    Devolve `None` quando o número informado não é numérico: o segundo Edital é conveniência da
    demonstração, e inventar um identificador a partir de texto arbitrário produziria UUID
    inválido — melhor não criá-lo e dizê-lo do que falhar no meio.
    """
    if not numero.isdigit():
        return None
    return f"{(int(numero) + 50) % 100:02d}"


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
        parser.add_argument(
            "--janela-recursal",
            choices=["declarada", "negada", "ausente"],
            default="declarada",
            help=(
                "o que o marco declara sobre recurso: prazo de cinco dias, negativa expressa, "
                "ou nada — como nos Editais anteriores ao degrau 8"
            ),
        )
        parser.add_argument(
            "--dias-atras",
            type=int,
            default=0,
            help=(
                "roda a demonstração como se ela tivesse ocorrido há N dias; serve para "
                "exibir um prazo recursal já encerrado"
            ),
        )

    def handle(self, *args, **opcoes):
        with _relogio_atrasado(opcoes["dias_atras"]):
            self._semear(**opcoes)

    def _semear(self, **opcoes):
        self.janela_recursal = opcoes["janela_recursal"]
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
            self._anexar_formularios(edital, numero)
            self._declarar_fatos_e_teto(edital, numero)
            self._publicar(elaborador, homologador, publicador, edital)

        # O segundo Edital e a divulgação dele. Fora da transação do primeiro, e depois de ele
        # estar publicado: cada Edital é um ato completo, e falhar aqui não desfaz aquele.
        #
        # **O número do segundo deriva do primeiro e tem de caber em dois dígitos**: ele entra nos
        # identificadores publicados como `00000000-0000-0000-00<numero>-…`, e três dígitos ali não
        # formam UUID. O deslocamento de 50 em aritmética modular nunca devolve o próprio número, e
        # é o que garante que os dois Editais não disputem identificador de Perfil, Etapa ou marco.
        segundo = _numero_do_segundo_edital(numero)
        publicacao = None
        if segundo is None:
            self.stdout.write(
                "Número do Edital não é numérico: o segundo Edital, com resultado divulgado, "
                "não foi criado. Use --numero com dois dígitos para tê-lo."
            )
        else:
            concluido = self._edital_encerrado(
                elaborador, homologador, publicador, processo, segundo, ano, agora
            )
            publicacao = self._divulgar_resultado(concluido, segundo, agora)

        self._retificar(edital, agora)
        self._resumo(processo, edital, publicacao)

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

        self.stdout.write("Elaborando Perfis, Cronograma, Etapas e contrato de inscrição…")
        replace_draft(
            actor=elaborador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            profiles=perfis(numero, janela_recursal=self.janela_recursal),
            schedule=cronograma(agora, numero),
            stages=etapas(numero),
            document_requirements=documentos_exigidos(numero),
            correlation_id="seed-demo",
        )
        edital.refresh_from_db()

    def _anexar_formularios(self, edital, numero):
        """Os Anexos que o Edital publica, e o vínculo do requisito que os cita (020).

        **Pelos modelos, e não pelo rascunho**, pela mesma razão dos fatos: a coleção fica fora do
        `replace_draft`, e é comando próprio que a mantém. Precisa rodar **depois** de `_elaborar`,
        que apaga e recria os Documentos Exigidos — e o vínculo mora num deles.

        Dois anexos porque a demonstração precisa do caso com modelo e do sem: a autodeclaração
        cita o Anexo I; a identificação e o diploma não fornecem forma própria, que é o caso mais
        comum de todos.
        """
        import hashlib

        from django.utils import timezone

        from processo_seletivo.editais.models.anexos import AnexoEdital, ArtefatoAnexo
        from processo_seletivo.editais.models.documentos import DocumentoExigido

        self.stdout.write("Publicando os Anexos que o Edital fornece…")
        for ordem, (rotulo, marca) in enumerate(
            [
                ("ANEXO I — AUTODECLARAÇÃO ÉTNICO-RACIAL", b"autodeclaracao"),
                ("ANEXO II — DECLARAÇÃO DE ANUÊNCIA DA CHEFIA IMEDIATA", b"anuencia"),
            ],
            start=1,
        ):
            conteudo = b"%PDF-1.4\n% " + marca + b" (demonstracao)\n%%EOF\n"
            artefato = ArtefatoAnexo.objects.create(
                bytes=conteudo,
                tamanho=len(conteudo),
                document_hash=hashlib.sha256(conteudo).hexdigest(),
                nome_original=f"{marca.decode()}.pdf",
                enviado_por="ana.elaboradora",
                enviado_em=timezone.now(),
            )
            anexo = AnexoEdital.objects.create(
                edital=edital, rotulo=rotulo, order=ordem, artefato=artefato
            )
            if ordem == 1:
                DocumentoExigido.objects.filter(edital=edital, key="autodeclaracao").update(
                    anexo=anexo
                )

    def _declarar_fatos_e_teto(self, edital, numero):
        """Os fatos que o desempate consome, e o teto do certame (D-2, D-3).

        **Pelo modelo, e não pelo rascunho**, porque a elaboração de fatos ainda não existe no
        caminho de produto — `replace_draft` não os conhece. Duas consequências que valem estar
        escritas: isto precisa rodar **depois** de `_elaborar`, que apaga e recria os Perfis; e este
        método sai daqui no dia em que a `US2` entregar o serializer e a persistência, quando os
        fatos passarão a viajar no próprio rascunho, como as Modalidades já viajam.
        """
        from processo_seletivo.editais.models.perfis import FatoDeclarado, PerfilVaga

        self.stdout.write("Declarando os fatos exigidos do candidato e o teto de inscrições…")
        perfil = PerfilVaga.objects.filter(edital=edital).order_by("code").first()
        if perfil is not None:
            FatoDeclarado.objects.bulk_create(
                [
                    FatoDeclarado(
                        id=f"00000000-0000-0000-00{numero}-0000000000f1",
                        perfil=perfil,
                        code="NASCIMENTO",
                        label="Data de nascimento",
                        tipo=FatoDeclarado.Tipo.DATA,
                    ),
                    FatoDeclarado(
                        id=f"00000000-0000-0000-00{numero}-0000000000f2",
                        perfil=perfil,
                        code="EXPERIENCIA",
                        label="Meses de experiência na área",
                        tipo=FatoDeclarado.Tipo.INTEIRO,
                    ),
                ]
            )
        # Uma inscrição por candidato, que é o que os Editais 14 (7.8) e 57 exigem.
        Edital.objects.filter(pk=edital.pk).update(max_inscricoes_por_candidato=1)
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

    def _edital_encerrado(self, elaborador, homologador, publicador, processo, numero, ano, agora):
        """Um **segundo** Edital, com o período de inscrições já vencido (T072).

        **Por que dois, e não um.** Distribuir exige o conjunto fechado: enquanto o prazo corre,
        distribuir deixaria sem avaliador quem se inscrever depois, e o domínio recusa — com razão.
        O primeiro Edital da demonstração existe justamente para mostrar o período **aberto**, com a
        contagem de dias na vitrine e a inscrição funcionando; forçar ali um resultado divulgado
        exigiria ou fechar o prazo, tirando a jornada do candidato da demonstração, ou contornar a
        regra por dentro, semeando linhas que a aplicação nunca teria aceitado.

        Dois Editais no mesmo Processo é o que um Processo Seletivo real tem, e resolve os dois
        estados sem que nenhum deles seja mentira: um em curso, outro concluído e divulgado.
        """
        from processo_seletivo.editais.application.draft import replace_draft
        from processo_seletivo.processos.application.commands import add_edital

        self.stdout.write("Criando o segundo Edital, já com as inscrições encerradas…")
        # Criar Edital é do Gestor, e elaborar é de quem elabora: são pessoas diferentes, como no
        # resto deste arquivo. Reusar o elaborador aqui daria a ele uma capacidade que o mapa de
        # papéis não lhe concede — e a demonstração passaria a mentir sobre a segregação.
        edital, _ = add_edital(
            actor=ator("gustavo.gestor", "edital:criar"),
            processo_id=processo.id,
            data={
                "number": numero,
                # **O ano é o informado, e não o do relógio.** Os dois Editais são do mesmo
                # Processo: um `--ano` que valesse só para o primeiro produziria uma demonstração
                # com dois anos diferentes dentro do mesmo certame.
                "year": ano,
                "title": f"Edital {numero}/{ano} — seleção concluída",
                "description": "Seleção com inscrições encerradas e resultado divulgado.",
            },
            idempotency_key=f"seed-demo-edital2-{processo.id.hex[:12]}",
            correlation_id="seed-demo",
        )
        # O Cronograma inteiro deslocado para trás: o período de inscrições vai de 60 a 40 dias
        # atrás, e é isso que torna o conjunto fechado.
        replace_draft(
            actor=elaborador,
            edital_id=edital.id,
            expected_revision=edital.revision,
            profiles=perfis(numero, janela_recursal=self.janela_recursal),
            schedule=cronograma(agora - timedelta(days=60), numero),
            stages=etapas(numero),
            document_requirements=documentos_exigidos(numero),
            correlation_id="seed-demo",
        )
        edital.refresh_from_db()
        self._publicar(elaborador, homologador, publicador, edital)
        edital.refresh_from_db()
        return edital

    def _divulgar_resultado(self, edital, numero, agora):
        """A cadeia da 011 à 017, para que a demonstração chegue ao que o candidato lê (T072).

        **Pelos mesmos commands da aplicação**, como o resto deste arquivo: constituir a comissão,
        alocar, inscrever, avaliar, consolidar, emitir a ordem e divulgá-la. Semear a publicação
        por `INSERT` produziria uma linha que a aplicação nunca teria aceitado — sem trilha, sem
        idempotência e sem a aferição de publicabilidade —, e a demonstração passaria a mostrar um
        estado que o sistema não sabe alcançar.

        A autoridade que divulga é **outra pessoa**, com capacidade própria: `resultado:publicar`
        não decorre de `classificacao:emitir`, e a demonstração precisa tornar isso visível
        (FR-025, FR-026).
        """
        from processo_seletivo.avaliacoes.application.avaliacao import concluir
        from processo_seletivo.avaliacoes.application.distribuicao import distribuir
        from processo_seletivo.classificacao.application.calculo import calcular_ordem
        from processo_seletivo.classificacao.application.emissao import (
            assinatura_da_proposta,
            emitir_ordem,
        )
        from processo_seletivo.classificacao.models import AtoDeOrdenacao
        from processo_seletivo.comissoes.application.alocacao import alocar
        from processo_seletivo.comissoes.application.comissao import adicionar_membro
        from processo_seletivo.comissoes.domain.funcoes import Funcao
        from processo_seletivo.divulgacao.application.publicar import (
            assinatura_da_previa,
            publicar_resultado,
        )
        from processo_seletivo.divulgacao.domain.conteudo import compor
        from processo_seletivo.inscricoes.models import Inscricao
        from processo_seletivo.resultados.application.consolidacao import consolidar

        self.stdout.write("Constituindo a comissão e alocando a banca…")
        gestor = ator("gustavo.gestor", "comissao:gerir")
        # **Consolidar e emitir são atos da presidência**, e não da gestão que constituiu a
        # comissão. Os dois caminhos autorizam — `comando_de_comissao` aceita presidência **ou**
        # `comissao:gerir` —, e quem os pratica na demonstração precisa ser quem os pratica no
        # certame: sem isso, o impedimento da 018 fica indemonstrável, porque quem consolidou o
        # Resultado não é ninguém que o seletor de identidade ofereça (018, FR-039).
        presidencia = ator("paulo.presidente")
        perfil_id = f"00000000-0000-0000-00{numero}-0000000000b1"
        marco_id = f"00000000-0000-0000-00{numero}-0000000000a1"
        primeira = f"00000000-0000-0000-00{numero}-0000000000d1"
        segunda = f"00000000-0000-0000-00{numero}-0000000000d2"
        chave = edital.id.hex[:8]

        membros = {}
        for indice, (subject, funcao) in enumerate(
            [
                ("paulo.presidente", Funcao.PRESIDENTE),
                ("joana.avaliadora", Funcao.MEMBRO),
                # **Um segundo avaliador, e não um enfeite**: a reavaliação determinada por
                # recurso exige avaliador diverso do que concluiu a original — a unicidade de
                # conclusão por pessoa impede a segunda —, e sem ele o passo 9 do roteiro esbarra
                # numa garantia estrutural em vez de ser percorrido (018, FR-068).
                ("otavio.avaliador", Funcao.MEMBRO),
            ]
        ):
            membro, _ = adicionar_membro(
                actor=gestor,
                processo_id=edital.processo_id,
                identity_subject=subject,
                funcao=funcao,
                idempotency_key=f"seed-demo-membro-{chave}-{indice}",
                correlation_id="seed-demo",
            )
            membros[subject] = membro
        for etapa in (primeira, segunda):
            # Os **dois** avaliadores alocados nas duas Etapas: quem conclui a original é a Joana,
            # e o Otávio fica disponível para a reavaliação que um deferimento pode determinar.
            # Alocar só na hora seria um passo a mais no roteiro, e um passo que a presidência já
            # teria dado ao montar a banca.
            for nome in ("joana.avaliadora", "otavio.avaliador"):
                alocar(
                    actor=gestor,
                    processo_id=edital.processo_id,
                    membro_id=membros[nome].id,
                    edital_id=edital.id,
                    etapa_id=etapa,
                    idempotency_key=f"seed-demo-aloc-{chave}-{etapa[-4:]}-{nome[:6]}",
                    correlation_id="seed-demo",
                )

        self.stdout.write("Recebendo inscrições e avaliando…")
        versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
        candidatas = [
            ("Ana Silva", "8.5000", "9.0000"),
            ("Bruno Costa", "7.0000", "8.0000"),
            # Empate residual com a segunda: o marco não declara critério de desempate, e por isso
            # as duas permanecem empatadas — a demonstração precisa mostrar a posição compartilhada.
            ("Clara Dias", "7.0000", "8.0000"),
            # Habilitado na primeira Etapa e **sem nota na segunda**: considerado pelo ato e sem
            # posição. É ele quem torna a fronteira visível — não aparece na lista pública e vê a
            # própria situação dentro da inscrição.
            #
            # Sem Resultado em Etapa alguma ele não estaria aqui: quem não passou pela Etapa
            # eliminatória anterior não é participante da seguinte, e o ato nem o consideraria.
            ("Daniel Rocha", "7.5000", None),
            # **Eliminada na Etapa 1**, abaixo da mínima de 6,0: é ela quem o roteiro da 018 segue.
            # Fora do universo do ato, ela não aparece na lista pública — e, desde a 018, lê o
            # próprio Resultado com o motivo escrito e tem por onde recorrer (FR-014, FR-015).
            ("Elisa Moraes", "4.0000", None),
        ]
        inscricoes = []
        for indice, (nome, _, _) in enumerate(candidatas, 1):
            inscricao = Inscricao.objects.create(
                created_at=agora,
                identity_subject=f"cand:seed-{chave}-{indice:02d}",
                edital=edital,
                profile_id=perfil_id,
                nome=nome,
                cpf="111.444.777-35",
                cpf_normalizado="11144477735",
                email=f"{nome.split()[0].lower()}@exemplo.test",
                modality_id=f"00000000-0000-0000-00{numero}-0000000000e1",
            )
            Inscricao.objects.filter(pk=inscricao.pk).update(
                status=Inscricao.Status.SUBMETIDA,
                protocolo=f"INS-{edital.year}-{chave.upper()}{indice:02d}",
                submitted_at=agora,
                versao_aceita=versao,
                declaracoes_aceitas_em=agora,
            )
            inscricao.refresh_from_db()
            self._dar_acesso(inscricao)
            inscricoes.append(inscricao)

        avaliadora = ator("joana.avaliadora")
        notas_por_inscricao = {
            inscricao.id: notas
            for inscricao, (_, *notas) in zip(inscricoes, candidatas, strict=True)
        }
        for etapa, posicao in ((primeira, 0), (segunda, 1)):
            # Só quem tem nota **nesta** Etapa entra no lote dela: distribuir alguém para depois
            # não concluir deixaria uma avaliação pendente, que é outro estado e não o que se quer
            # demonstrar aqui.
            desta_etapa = [
                inscricao
                for inscricao in inscricoes
                if notas_por_inscricao[inscricao.id][posicao] is not None
            ]
            distribuir(
                actor=gestor,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                etapa_id=etapa,
                membro_ids=[membros["joana.avaliadora"].id],
                inscricao_ids=[item.id for item in desta_etapa],
                idempotency_key=f"seed-demo-lote-{chave}-{etapa[-4:]}",
                correlation_id="seed-demo",
            )
            for inscricao in desta_etapa:
                concluir(
                    ator=avaliadora,
                    edital=edital,
                    etapa_id=etapa,
                    inscricao_id=inscricao.id,
                    pontuacao=notas_por_inscricao[inscricao.id][posicao],
                    parecer="Avaliação concluída.",
                    expected_revision=1,
                    versao_reconhecida=versao.id,
                    correlation_id="seed-demo",
                )
            consolidar(
                actor=presidencia,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                etapa_id=etapa,
                inscricao_ids=[item.id for item in desta_etapa],
                idempotency_key=f"seed-demo-consolidar-{chave}-{etapa[-4:]}",
                correlation_id="seed-demo",
            )

        self.stdout.write("Emitindo a ordem classificatória…")
        proposta = calcular_ordem(edital=edital, perfil_id=perfil_id, marco_id=marco_id)
        emitir_ordem(
            actor=presidencia,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=perfil_id,
            marco_id=marco_id,
            idempotency_key=f"seed-demo-ordem-{chave}",
            correlation_id="seed-demo",
            confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
        )
        ato = AtoDeOrdenacao.objects.get(edital=edital, marco_id=marco_id, sucessores__isnull=True)

        self.stdout.write("Divulgando o resultado…")
        publicadora = ator("paula.publicadora", "resultado:publicar")
        publicacao = publicar_resultado(
            actor=publicadora,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            marco_id=marco_id,
            ato_id=ato.id,
            natureza="PRELIMINAR",
            autoridade="diretoria-cefor",
            confirmacao_da_previa=assinatura_da_previa(
                ato=ato, publicacao_anterior=None, projecao=compor(ato)
            ),
            idempotency_key=f"seed-demo-divulgar-{chave}",
            correlation_id="seed-demo",
        )
        return publicacao

    def _dar_acesso(self, inscricao):
        """A identidade e a credencial de quem já se inscreveu — para que ela consiga entrar.

        **Não é atalho de demonstração**: são exatamente as linhas que o produto cria quando o
        candidato prova o controle do e-mail, e a premissa deste seed é que essas pessoas já se
        inscreveram — logo, já entraram alguma vez. Sem elas, o `identity_subject` das inscrições
        seria um valor que nenhum login produz, e a demonstração ficaria com uma tela de
        acompanhamento inalcançável: quem entrasse com o e-mail da Elisa criaria uma identidade
        nova e vazia, e a inscrição dela responderia 404 — corretamente, e para ninguém.

        A credencial nasce **verificada**, pela mesma razão: ela representa uma prova que já
        aconteceu. A alternativa seria semear o desafio de acesso pendente, que é estado de
        transição e não estado de mundo.
        """
        from processo_seletivo.identidade.domain.enderecos import canonizar
        from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity

        agora = timezone.now()
        identidade, _ = CandidateIdentity.objects.get_or_create(
            subject=inscricao.identity_subject,
            defaults={
                "nome": inscricao.nome,
                "cpf_normalizado": inscricao.cpf_normalizado,
                "created_at": agora,
            },
        )
        CandidateEmail.objects.get_or_create(
            email_canonico=canonizar(inscricao.email),
            defaults={
                "identidade": identidade,
                "email_como_informado": inscricao.email,
                "principal": True,
                "verified_at": agora,
                "created_at": agora,
            },
        )

    def _retificar(self, edital, agora):
        """Uma vigente e outra com vigência futura, para a consulta temporal ter o que mostrar."""
        elaborador = ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
        homologador = ator("bruno.homologador", "retificacao:homologar")
        publicador = ator("carla.publicadora", "retificacao:publicar")

        # As alterações nascem do conteúdo vigente, porque o caminho nomeia a entidade: o
        # identificador do Perfil e o do Evento só existem depois de o Edital ter sido publicado.
        def vagas_do_primeiro_perfil(conteudo):
            perfil = conteudo["profiles"][0]["id"]
            return [
                {
                    "targetPath": f"/profiles/id={perfil}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 3,
                }
            ]

        def termino_do_primeiro_evento(conteudo):
            evento = conteudo["schedule"][0]["id"]
            return [
                {
                    "targetPath": f"/schedule/id={evento}/endAt",
                    "operation": "REPLACE",
                    "newValue": (agora + timedelta(days=30)).isoformat(),
                }
            ]

        for sufixo, montar_mudancas, vigencia, motivo in (
            (
                "a",
                vagas_do_primeiro_perfil,
                None,
                "Ampliação de uma vaga imediata no perfil de docência.",
            ),
            (
                "b",
                termino_do_primeiro_evento,
                agora + timedelta(days=15),
                "Prorrogação das inscrições, vigente a partir de 15 dias.",
            ),
        ):
            self.stdout.write(f"Publicando Retificação {sufixo}…")
            base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
            dados = {
                "baseSnapshotId": base.id,
                "justification": motivo,
                "changes": montar_mudancas(base.content),
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

    def _resumo(self, processo, edital, publicacao=None):
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
            (
                "resultado",
                f"/selecoes/resultados/{publicacao.id}/" if publicacao else "",
            ),
            (
                "documento",
                f"/selecoes/resultados/{publicacao.id}/documento.pdf" if publicacao else "",
            ),
            ("saúde", "/health"),
        ):
            if caminho:
                self.stdout.write(f"  {rotulo:16} http://127.0.0.1:8000{caminho}")
