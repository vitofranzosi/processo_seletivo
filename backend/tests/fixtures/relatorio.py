"""O cenário coerente do relatório do Edital (099, R-011): o Edital 61/2026 da maquete v2.

**Pelos commands da aplicação, com o relógio posto na data de cada ato** — o mesmo recurso do
`seed_demo --dias-atras`, só que ato a ato. As inscrições seguem o caminho do candidato (abrir,
gravar, enviar), e não a gravação direta do semeador: foi a gravação direta que deu à maquete v1
uma cronologia impossível, com inscrições depois do fim do prazo. Se a cronologia daqui estivesse
errada, o command recusaria.

A história, em horário de Brasília:

    03/08  Edital publicado; inscrições de 10/08 a 30/08
    25/08  Retificação prorroga as inscrições até 04/09
    10/08–04/09  38 inscrições enviadas; 4 rascunhos
    15–17/09  prova, com 1 ocorrência; 19–20/09 títulos
    24/09  ordens; 25/09 preliminares (5 dias de recurso)
    26–29/09  3 recursos; 02/10 julgados (1 não admitido, 2 indeferidos)
    06/10  definitivos; 08–10/10 corte, análise documental, apuração
    13/10  convocação dos dois titulares (ampla e reservada)
    20/10  Edital encerrado

O `final` escolhe o que acontece depois do encerramento, ou se ele acontece:

- `pendente` (o da maquete): a reservada no prazo até 30/10; o aceite da ampla em 21/10, depois do
  encerramento;
- `sem-pendencia`: os dois aceites antes do encerramento;
- `aberto`: para em 20/08, com o período de inscrições correndo;
- `cancelado`: o Edital cancelado em 10/09, depois das inscrições.

O instante de referência dos testes é **fixo** (`REFERENCIA`): o relógio da suíte anda, e "prazo em
curso até 30/10" deixaria de ser verdade no mês seguinte.
"""

import contextlib
import io
import random
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.utils import timezone

ZONA = ZoneInfo("America/Sao_Paulo")
NUMERO = "61"
CORRELACAO = "teste-099"


def dia(d, m, h=10, mi=0):
    return datetime(2026, m, d, h, mi, tzinfo=ZONA)


#: O instante de referência da maquete v2: depois do aceite da ampla, antes do fim do prazo da
#: reservada.
REFERENCIA = dia(24, 10, 13, 10)
#: Com o período correndo, para o final `aberto`.
REFERENCIA_ABERTA = dia(20, 8, 18)


def _id(sufixo, numero=NUMERO):
    return f"00000000-0000-0000-00{numero}-0000000000{sufixo}"


PROF, TEC = _id("b1"), _id("b2")
MARCO_PROF, MARCO_TEC = _id("a1"), _id("a2")
AC_PROF, PPP, AC_TEC = _id("e1"), _id("e2"), _id("e3")
PROVA, TITULOS, DOCUMENTAL = _id("d1"), _id("d2"), _id("d3")
EVENTO_DAS_INSCRICOES = _id("c1")


@contextlib.contextmanager
def em(instante):
    """O relógio da aplicação posto em `instante`, andando a partir dali."""
    real = timezone.now
    inicio = real()
    timezone.now = lambda: instante + (real() - inicio)
    try:
        yield
    finally:
        timezone.now = real


def cpf_valido(base9):
    digitos = [int(c) for c in f"{base9:09d}"]
    for tamanho in (9, 10):
        soma = sum(d * (tamanho + 1 - i) for i, d in enumerate(digitos))
        resto = (soma * 10) % 11
        digitos.append(0 if resto == 10 else resto)
    s = "".join(map(str, digitos))
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"


def _cronograma(numero=NUMERO):
    eventos = [
        ("Inscrições", "Inscrições pelo sistema.", dia(10, 8, 0), dia(30, 8, 23, 59)),
        ("Prova objetiva", "Aplicação da prova no Campus Vitória.", dia(13, 9, 8), None),
        ("Análise de títulos", "Avaliação dos títulos.", dia(16, 9, 8), dia(22, 9, 18)),
        ("Resultado preliminar", "Resultado preliminar e prazo de recurso.", dia(25, 9, 12), None),
        ("Resultado definitivo", "Resultado definitivo.", dia(6, 10, 12), None),
    ]
    return [
        {
            "id": _id(f"c{i}", numero),
            "type": tipo,
            "description": descricao,
            "startAt": inicio,
            "endAt": fim,
            "order": i,
            "isRegistrationPeriod": i == 1,
        }
        for i, (tipo, descricao, inicio, fim) in enumerate(eventos, 1)
    ]


def _perfis(numero=NUMERO):
    from processo_seletivo.processos.management.commands import seed_demo

    perfis = seed_demo.perfis(numero, janela_recursal="declarada")
    # O marco do cadastro de reserva do semeador não declara prazo recursal, e a definitiva o
    # recusaria; aqui os dois marcos declaram os mesmos cinco dias.
    perfis[1]["classificationMilestones"][0].update(seed_demo._janela_do_marco("declarada"))
    return perfis


def _etapas(numero=NUMERO):
    from processo_seletivo.processos.management.commands import seed_demo

    etapas = seed_demo.etapas(numero)
    etapas[0]["scheduleEventId"] = _id("c2", numero)
    etapas[1]["scheduleEventId"] = _id("c3", numero)
    return etapas


def _registrar(identidade):
    from processo_seletivo.identidade.application.associacao import associar_credencial
    from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity

    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=identidade.subject,
        defaults={
            "nome": identidade.nome,
            "cpf_normalizado": identidade.cpf.replace(".", "").replace("-", ""),
            "created_at": timezone.now(),
        },
    )
    if not CandidateEmail.objects.filter(email_canonico=identidade.email.lower()).exists():
        associar_credencial(registro, identidade.email.lower(), identidade.email)


def _ator(subject, *permissoes):
    from processo_seletivo.seguranca.domain import Actor

    return Actor(subject, "cefor", frozenset(permissoes))


class _Cenario:
    """Os passos, na ordem da história; cada um com o relógio na data do ato."""

    def __init__(self, escala, numero=NUMERO, publicado_em=None, tecnicos=None, maximo=None):
        self.escala = escala
        # O número entra nos identificadores do conteúdo, nas chaves e no código do Processo, e
        # com ele o mesmo cenário monta vários Editais coerentes na mesma unidade (100, R-012). As
        # mesmas pessoas se inscrevem em todos — o caso real que o consolidado não conta como gente.
        self.numero = numero
        self.chave = "099" if numero == NUMERO else f"099-{numero}"
        self.codigo = "PS-CEFOR-2026-2" if numero == NUMERO else f"PS-CEFOR-2026-{numero}"
        self.publicado_em = publicado_em
        #: Quantas inscrições no Técnico, e quantas no total — para o Perfil e o Edital pequenos.
        self.tecnicos = tecnicos
        self.maximo = maximo
        self.PROF, self.TEC = _id("b1", numero), _id("b2", numero)
        self.MARCO_PROF, self.MARCO_TEC = _id("a1", numero), _id("a2", numero)
        self.AC_PROF, self.PPP, self.AC_TEC = (
            _id("e1", numero),
            _id("e2", numero),
            _id("e3", numero),
        )
        self.PROVA, self.TITULOS, self.DOCUMENTAL = (
            _id("d1", numero),
            _id("d2", numero),
            _id("d3", numero),
        )
        self.EVENTO_DAS_INSCRICOES = _id("c1", numero)
        self.rng = random.Random(61)
        self.inscricoes = {}
        self.pessoas = []
        self.convocacoes = {}

    # -- composição e publicação ---------------------------------------------------------------

    def publicar(self):
        from processo_seletivo.editais.application.draft import replace_draft
        from processo_seletivo.processos.application.commands import (
            create_process_with_first_edital,
        )
        from processo_seletivo.processos.management.commands import seed_demo
        from processo_seletivo.processos.models import Edital

        with em(self.publicado_em or dia(3, 8, 9)):
            self.comando = seed_demo.Command(stdout=io.StringIO())
            self.comando.janela_recursal = "declarada"
            self.comando._unidade_e_autoridades()
            elaborador = _ator(
                "ana.elaboradora", "processo:criar", "edital:elaborar", "edital:submeter"
            )
            self.processo, _ = create_process_with_first_edital(
                actor=elaborador,
                data={
                    "institutionalCode": self.codigo,
                    "title": "Processo Seletivo Simplificado 2026/2",
                    "firstEdital": {
                        "number": self.numero,
                        "year": 2026,
                        "title": f"Edital {self.numero}/2026 — Professor de Informática e Técnico",
                        "description": "Seleção simplificada.",
                    },
                },
                idempotency_key=f"{self.chave}-processo",
                correlation_id=CORRELACAO,
            )
            self.edital = Edital.objects.get(processo=self.processo)
            replace_draft(
                actor=elaborador,
                edital_id=self.edital.id,
                expected_revision=self.edital.revision,
                profiles=_perfis(self.numero),
                schedule=_cronograma(self.numero),
                stages=_etapas(self.numero),
                document_requirements=[],
                correlation_id=CORRELACAO,
            )
            self.edital.refresh_from_db()
            self.comando._publicar(
                elaborador,
                _ator("bruno.homologador", "edital:homologar"),
                _ator("carla.publicadora", "edital:publicar"),
                self.edital,
            )

    def prorrogar(self):
        from processo_seletivo.processos.management.commands import seed_demo
        from processo_seletivo.publicacoes.application.retificacoes import (
            create_retification,
            publish_retification,
            transition_retification,
        )
        from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

        elaborador = _ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
        with em(dia(25, 8, 11)):
            base = VersaoConsolidada.objects.filter(edital=self.edital).latest("materialized_at")
            retificacao, _ = create_retification(
                actor=elaborador,
                edital_id=self.edital.id,
                data={
                    "baseSnapshotId": base.id,
                    "justification": "Prorrogação do período de inscrições.",
                    "changes": [
                        {
                            "targetPath": f"/schedule/id={self.EVENTO_DAS_INSCRICOES}/endAt",
                            "operation": "REPLACE",
                            "newValue": dia(4, 9, 23, 59).isoformat(),
                        }
                    ],
                },
                idempotency_key=f"{self.chave}-ret",
                correlation_id=CORRELACAO,
            )
            for acao, quem in (
                ("submeter", elaborador),
                ("homologar", _ator("bruno.homologador", "retificacao:homologar")),
            ):
                retificacao, _ = transition_retification(
                    actor=quem,
                    retificacao_id=retificacao.id,
                    expected_revision=retificacao.revision,
                    action=acao,
                    reason="Conferido.",
                    idempotency_key=f"{self.chave}-ret-{acao}",
                    correlation_id=CORRELACAO,
                )
            publish_retification(
                actor=_ator("carla.publicadora", "retificacao:publicar"),
                retificacao_id=retificacao.id,
                expected_revision=retificacao.revision,
                autoridade_id=self.comando.autoridades[seed_demo.CARGO_DO_EDITAL],
                idempotency_key=f"{self.chave}-ret-publicar",
                correlation_id=CORRELACAO,
            )

    # -- inscrições -----------------------------------------------------------------------------

    def inscrever(self, *, ate=None):
        from processo_seletivo.inscricoes.application.rascunho import (
            abrir_inscricao,
            gravar_dados,
        )
        from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
        from processo_seletivo.portal.identidade import IdentidadeDoCandidato

        e = self.escala
        for i in range(1, 36 * e + 1):
            self.pessoas.append(
                IdentidadeDoCandidato(
                    f"cand:099-{i:04d}",
                    f"Pessoa Candidata {i:02d}",
                    cpf_valido(100000000 + i * 7919),
                    f"pessoa{i:02d}@exemplo.test",
                )
            )
        p = self.pessoas
        pedidos = [(x, self.PROF, self.AC_PROF) for x in p[: 20 * e]]
        pedidos += [(x, self.PROF, self.PPP) for x in p[20 * e : 26 * e]]
        pedidos += [(x, self.TEC, self.AC_TEC) for x in p[26 * e : 36 * e]]
        # Duas pessoas se inscrevem nos dois Perfis: 38 inscrições de 36 cadastros.
        pedidos += [(p[0], self.TEC, self.AC_TEC), (p[1], self.TEC, self.AC_TEC)]
        self.rng.shuffle(pedidos)
        # Os cortes vêm depois do sorteio da ordem, para que o resto da história — datas, notas,
        # desempates — seja o do cenário inteiro, e só o que se cortou deixe de existir.
        if self.tecnicos is not None:
            manter = {id(x) for x in [x for x in pedidos if x[1] == self.TEC][: self.tecnicos]}
            pedidos = [x for x in pedidos if x[1] != self.TEC or id(x) in manter]
        if self.maximo is not None:
            pedidos = pedidos[: self.maximo]
        dias = [10, 10, 11, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 24, 25, 26]
        dias += [27, 28, 28, 29, 29, 30, 30, 30]
        datas = [dia(d, 8, self.rng.randint(8, 22), self.rng.randint(0, 59)) for d in dias]
        datas += [
            dia(d, 9, self.rng.randint(8, 22), self.rng.randint(0, 59))
            for d in (1, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4)
        ]
        datas = sorted(datas * e)[: len(pedidos)]

        prorrogado = False
        for (pessoa, perfil, modalidade), quando in zip(pedidos, datas, strict=True):
            if ate is not None and quando > ate:
                break
            if not prorrogado and quando > dia(25, 8, 12):
                self.prorrogar()
                prorrogado = True
            with em(quando):
                _registrar(pessoa)
                rascunho = abrir_inscricao(
                    identidade=pessoa, edital_id=self.edital.id, profile_id=perfil
                )
                rascunho = gravar_dados(
                    identidade=pessoa,
                    inscricao=rascunho,
                    dados={
                        "nome": pessoa.nome,
                        "cpf": pessoa.cpf,
                        "email": pessoa.email,
                        "modality_id": modalidade,
                    },
                )
                self.inscricoes[(pessoa.subject, perfil)] = enviar_inscricao(
                    identidade=pessoa,
                    inscricao=rascunho,
                    declaracoes={"veracidade": True, "ciencia": True},
                    idempotency_key=f"{self.chave}-envio-{pessoa.subject}-{perfil[-2:]}",
                )
        # O Edital encolhido não chega à prorrogação: rascunhos de setembro cairiam fora do prazo.
        if ate is not None or self.maximo is not None:
            return
        # Quatro rascunhos que nunca foram enviados.
        quando = (dia(14, 8), dia(23, 8), dia(2, 9), dia(4, 9, 21))
        for indice, instante in zip(range(36 * e + 1, 36 * e + 5), quando, strict=True):
            pessoa = IdentidadeDoCandidato(
                f"cand:099-{indice:04d}",
                f"Pessoa Candidata {indice:02d}",
                cpf_valido(100000000 + indice * 7919),
                f"pessoa{indice:02d}@exemplo.test",
            )
            with em(instante):
                _registrar(pessoa)
                abrir_inscricao(
                    identidade=pessoa,
                    edital_id=self.edital.id,
                    profile_id=self.PROF if indice % 2 else self.TEC,
                )

    # -- avaliação ------------------------------------------------------------------------------

    def comissao(self):
        from processo_seletivo.comissoes.application.alocacao import alocar
        from processo_seletivo.comissoes.application.comissao import adicionar_membro
        from processo_seletivo.comissoes.domain.funcoes import Funcao

        self.gestor = _ator("gustavo.gestor", "comissao:gerir")
        self.membros = {}
        with em(dia(7, 9)):
            for k, (subject, funcao) in enumerate(
                [
                    ("paulo.presidente", Funcao.PRESIDENTE),
                    ("joana.avaliadora", Funcao.MEMBRO),
                    ("otavio.avaliador", Funcao.MEMBRO),
                ]
            ):
                self.membros[subject], _ = adicionar_membro(
                    actor=self.gestor,
                    processo_id=self.processo.id,
                    identity_subject=subject,
                    funcao=funcao,
                    idempotency_key=f"{self.chave}-membro-{k}",
                    correlation_id=CORRELACAO,
                )
            for etapa in (self.PROVA, self.TITULOS, self.DOCUMENTAL):
                for nome in ("joana.avaliadora", "otavio.avaliador"):
                    alocar(
                        actor=self.gestor,
                        processo_id=self.processo.id,
                        membro_id=self.membros[nome].id,
                        edital_id=self.edital.id,
                        etapa_id=etapa,
                        idempotency_key=f"{self.chave}-aloc-{etapa[-2:]}-{nome[:4]}",
                        correlation_id=CORRELACAO,
                    )
        self.presidencia = _ator("paulo.presidente")

    def _avaliar(self, etapa, alvo, notas, instante, chave):
        from processo_seletivo.avaliacoes.application.avaliacao import concluir
        from processo_seletivo.avaliacoes.application.distribuicao import distribuir
        from processo_seletivo.publicacoes.application.selectors import effective_version
        from processo_seletivo.resultados.application.consolidacao import consolidar

        versao = effective_version(edital_id=self.edital.id)
        with em(instante):
            distribuir(
                actor=self.gestor,
                processo_id=self.processo.id,
                edital_id=self.edital.id,
                etapa_id=etapa,
                membro_ids=[self.membros["joana.avaliadora"].id],
                inscricao_ids=[i.id for i in alvo],
                idempotency_key=f"{self.chave}-lote-{chave}",
                correlation_id=CORRELACAO,
            )
        for k, inscricao in enumerate(alvo):
            with em(instante + timedelta(hours=2 + k // 6)):
                concluir(
                    ator=_ator("joana.avaliadora"),
                    edital=self.edital,
                    etapa_id=etapa,
                    inscricao_id=inscricao.id,
                    pontuacao=notas[inscricao.id] if notas else None,
                    parecer="Avaliação concluída.",
                    expected_revision=1,
                    versao_reconhecida=versao.id,
                    correlation_id=CORRELACAO,
                    **({} if notas else {"sentido": "FAVORAVEL"}),
                )
        with em(instante + timedelta(days=1, hours=8)):
            consolidar(
                actor=self.presidencia,
                processo_id=self.processo.id,
                edital_id=self.edital.id,
                etapa_id=etapa,
                inscricao_ids=[i.id for i in alvo],
                idempotency_key=f"{self.chave}-consolidar-{chave}",
                correlation_id=CORRELACAO,
            )

    def avaliar(self):
        from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

        todas = list(self.inscricoes.values())
        self.ausente = next(
            i
            for i in todas
            if str(i.profile_id) == self.PROF and str(i.modality_id) == self.AC_PROF
        )
        if self.escala == 1:
            self.nota_prova = {
                i.id: Decimal(str(round(self.rng.uniform(3.5, 9.8), 1))) for i in todas
            }
            self.nota_titulos = {
                i.id: Decimal(str(round(self.rng.uniform(1.0, 10.0), 1))) for i in todas
            }
        else:
            # Com volume, notas sorteadas empatam na fronteira das vagas e a apuração recusa — com
            # razão, porque o marco não declara desempate. Para medir a leitura, notas distintas.
            grade = [Decimal("3.50") + Decimal(k) * Decimal("0.01") for k in range(len(todas))]
            self.rng.shuffle(grade)
            self.nota_prova = {i.id: nota for i, nota in zip(todas, grade, strict=True)}
            self.nota_titulos = {i.id: Decimal("5.0") for i in todas}
        with em(dia(15, 9, 9)):
            registrar_ocorrencia(
                actor=self.presidencia,
                processo_id=self.processo.id,
                edital_id=self.edital.id,
                etapa_id=self.PROVA,
                inscricao_ids=[self.ausente.id],
                motivo="Ausência na prova objetiva, conforme lista de presença.",
                idempotency_key=f"{self.chave}-ocorrencia",
                correlation_id=CORRELACAO,
            )
        self.presentes = [i for i in todas if i.id != self.ausente.id]
        self._avaliar(self.PROVA, self.presentes, self.nota_prova, dia(16, 9, 9), "prova")
        self.habilitadas = [i for i in self.presentes if self.nota_prova[i.id] >= Decimal("6")]
        self._avaliar(self.TITULOS, self.habilitadas, self.nota_titulos, dia(19, 9, 9), "titulos")

    # -- resultados -----------------------------------------------------------------------------

    def ordenar(self):
        from processo_seletivo.classificacao.application.calculo import calcular_ordem
        from processo_seletivo.classificacao.application.emissao import (
            assinatura_da_proposta,
            emitir_ordem,
        )
        from processo_seletivo.classificacao.application.selectors import ato_vigente

        self.atos = {}
        with em(dia(24, 9, 15)):
            for perfil, marco, lista in (
                (self.PROF, self.MARCO_PROF, None),
                (self.PROF, self.MARCO_PROF, self.PPP),
                (self.TEC, self.MARCO_TEC, None),
            ):
                # Perfil sem inscrição não tem ordem a emitir — e a comissão real não a emitiria.
                if not any(str(i.profile_id) == perfil for i in self.inscricoes.values()):
                    continue
                proposta = calcular_ordem(
                    edital=self.edital, perfil_id=perfil, marco_id=marco, lista_id=lista
                )
                emitir_ordem(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=perfil,
                    marco_id=marco,
                    lista_id=lista,
                    idempotency_key=f"{self.chave}-ordem-{marco[-2:]}-{lista}",
                    correlation_id=CORRELACAO,
                    confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
                )
                self.atos[(marco, lista)] = ato_vigente(
                    edital=self.edital, marco_id=marco, lista_id=lista
                )

    def publicar_resultados(self, natureza, instante, anteriores):
        from processo_seletivo.divulgacao.application.publicar import (
            assinatura_da_previa,
            publicar_resultado,
        )
        from processo_seletivo.divulgacao.domain.conteudo import compor
        from processo_seletivo.processos.management.commands import seed_demo

        publicadas = {}
        with em(instante):
            for (marco, lista), ato in self.atos.items():
                publicadas[(marco, lista)] = publicar_resultado(
                    actor=_ator("paula.publicadora", "resultado:publicar"),
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    marco_id=marco,
                    ato_id=ato.id,
                    natureza=natureza,
                    autoridade=self.comando.autoridades[seed_demo.CARGO_DO_RESULTADO],
                    confirmacao_da_previa=assinatura_da_previa(
                        ato=ato,
                        publicacao_anterior=anteriores.get((marco, lista)),
                        projecao=compor(ato),
                    ),
                    idempotency_key=f"{self.chave}-pub-{natureza}-{marco[-2:]}-{lista}",
                    correlation_id=CORRELACAO,
                )
        return publicadas

    def recorrer(self):
        from processo_seletivo.recursos.application.admitir import admitir
        from processo_seletivo.recursos.application.interpor import interpor
        from processo_seletivo.recursos.application.julgar import julgar
        from processo_seletivo.recursos.application.selectors import assinatura_do_estado_da_peca

        julgadora = _ator("helena.julgadora", "recurso:julgar")
        recorrentes = [
            (
                next(
                    i
                    for i in self.presentes
                    if str(i.profile_id) == self.PROF and self.nota_prova[i.id] < 6
                ),
                (self.MARCO_PROF, None),
                dia(26, 9, 14),
                False,
            ),
            (
                next(
                    i
                    for i in self.habilitadas
                    if str(i.profile_id) == self.PROF and str(i.modality_id) == self.PPP
                ),
                (self.MARCO_PROF, self.PPP),
                dia(27, 9, 16),
                True,
            ),
            (
                next((i for i in self.habilitadas if str(i.profile_id) == self.TEC), None),
                (self.MARCO_TEC, None),
                dia(29, 9, 10),
                True,
            ),
        ]
        # O Técnico encolhido pode não ter habilitada a quem atribuir o terceiro recurso.
        recorrentes = [r for r in recorrentes if r[0] is not None]
        for k, (inscricao, chave, quando, admitido) in enumerate(recorrentes):
            publicacao = self.preliminares[chave]
            titular = next(p for p in self.pessoas if p.subject == inscricao.identity_subject)
            with em(quando):
                peca = interpor(
                    identidade=titular,
                    inscricao=inscricao,
                    publicacao=publicacao,
                    fundamentacao="Solicito revisão da minha pontuação.",
                    assinatura_do_objeto=str(publicacao.pk),
                    idempotency_key=f"{self.chave}-rec-{k}",
                )
            with em(dia(2, 10, 10 + k)):
                admitir(
                    actor=julgadora,
                    recurso_id=peca.id,
                    admitido=admitido,
                    motivo="Tempestivo."
                    if admitido
                    else "O recurso não indica o ponto contestado.",
                    assinatura_do_estado=assinatura_do_estado_da_peca(peca),
                    idempotency_key=f"{self.chave}-adm-{k}",
                )
                if admitido:
                    peca.refresh_from_db()
                    julgar(
                        actor=julgadora,
                        recurso_id=peca.id,
                        especie="INDEFERIDO",
                        motivacao="A pontuação confere com a planilha da banca.",
                        idempotency_key=f"{self.chave}-julgar-{k}",
                    )

    def apurar(self):
        from processo_seletivo.classificacao.application.corte import calcular_corte
        from processo_seletivo.classificacao.application.emissao_do_corte import (
            assinatura_da_proposta as assinatura_do_corte,
        )
        from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
        from processo_seletivo.classificacao.models import ItemDoCorte
        from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

        with em(dia(8, 10, 10)):
            for lista in (None, self.PPP):
                emitir_corte(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=self.PROF,
                    marco_id=self.MARCO_PROF,
                    lista_id=lista,
                    idempotency_key=f"{self.chave}-corte-{lista}",
                    correlation_id=CORRELACAO,
                    confirmacao_do_calculo=assinatura_do_corte(
                        calcular_corte(
                            edital=self.edital,
                            perfil_id=self.PROF,
                            marco_id=self.MARCO_PROF,
                            lista_id=lista,
                        )
                    ),
                )
        # Quem progrediu em qualquer das duas listas passa pela análise documental, uma vez só.
        self.progrediram = list(
            {
                item.inscricao_id: item.inscricao
                for item in ItemDoCorte.objects.filter(
                    consequencia="PROGREDIU", inscricao__edital=self.edital
                ).select_related("inscricao")
            }.values()
        )
        self._avaliar(self.DOCUMENTAL, self.progrediram, None, dia(8, 10, 14), "documental")
        with em(dia(10, 10, 9)):
            for lista in (None, self.PPP):
                emitir_apuracao(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=self.PROF,
                    marco_id=self.MARCO_PROF,
                    lista_id=lista,
                    idempotency_key=f"{self.chave}-apurar-{lista}",
                    correlation_id=CORRELACAO,
                    motivo="",
                )

    def convocar(self):
        from processo_seletivo.convocacao.application.convocar import convocar

        with em(dia(13, 10, 10)):
            for lista, vencimento in ((None, dia(23, 10, 23, 59)), (self.PPP, dia(30, 10, 23, 59))):
                ato = self.atos[(self.MARCO_PROF, lista)]
                ja = {c["inscricao"] for c in self.convocacoes.values()}
                primeira = min(
                    (
                        p
                        for p in ato.posicoes.all()
                        if p.posicao
                        and p.inscricao in self.progrediram
                        and str(p.inscricao_id) not in ja
                    ),
                    key=lambda p: p.posicao,
                ).inscricao
                self.convocacoes[lista] = convocar(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=self.PROF,
                    marco_id=self.MARCO_PROF,
                    lista_id=lista,
                    inscricao_id=primeira.id,
                    vencimento=vencimento,
                    fundamento="No interesse da Administração, conforme o item 8.2 do Edital.",
                    idempotency_key=f"{self.chave}-convocar-{lista}",
                    correlation_id=CORRELACAO,
                )

    def aceitar(self, lista, instante):
        from processo_seletivo.convocacao.application.desfechar import desfechar

        with em(instante):
            desfechar(
                actor=self.presidencia,
                processo_id=self.processo.id,
                convocacao_id=self.convocacoes[lista]["id"],
                especie="ACEITE",
                fundamento="Aceite manifestado por mensagem.",
                idempotency_key=f"{self.chave}-aceite-{lista}",
                correlation_id=CORRELACAO,
            )

    def encerrar(self):
        from processo_seletivo.processos.application.finalizacao import close_edital

        with em(dia(20, 10, 17)):
            self.edital.refresh_from_db()
            close_edital(
                actor=_ator("gustavo.gestor", "edital:encerrar"),
                edital_id=self.edital.id,
                expected_revision=self.edital.revision,
                reason="Resultados definitivos divulgados e titulares convocados.",
                idempotency_key=f"{self.chave}-encerrar",
                correlation_id=CORRELACAO,
            )

    def cancelar(self):
        from processo_seletivo.processos.application.finalizacao import cancel_edital

        with em(dia(10, 9, 15)):
            self.edital.refresh_from_db()
            cancel_edital(
                actor=_ator("gustavo.gestor", "edital:cancelar"),
                edital_id=self.edital.id,
                expected_revision=self.edital.revision,
                reason="Cancelado por decisão da direção.",
                idempotency_key=f"{self.chave}-cancelar",
                correlation_id=CORRELACAO,
            )


def montar_cenario(
    *,
    escala=1,
    final="pendente",
    numero=NUMERO,
    publicado_em=None,
    tecnicos=None,
    maximo=None,
):
    """Monta o Edital `numero`/2026 e devolve o cenário, com `edital` e `processo` atualizados.

    `publicado_em` muda só o instante da publicação; o resto da história fica nas datas de sempre.
    `tecnicos` e `maximo` encolhem o Perfil do Técnico e o Edital inteiro, para os casos de grupo
    pequeno — `maximo` só serve aos finais `aberto` e `cancelado`, que não passam pela comissão.
    """
    if final not in {"pendente", "sem-pendencia", "aberto", "cancelado"}:
        raise ValueError(final)
    cenario = _Cenario(escala, numero, publicado_em, tecnicos, maximo)
    cenario.publicar()
    if final == "aberto":
        cenario.inscrever(ate=REFERENCIA_ABERTA)
        cenario.edital.refresh_from_db()
        return cenario
    cenario.inscrever()
    if final == "cancelado":
        cenario.cancelar()
        cenario.edital.refresh_from_db()
        return cenario
    cenario.comissao()
    cenario.avaliar()
    cenario.ordenar()
    cenario.preliminares = cenario.publicar_resultados("PRELIMINAR", dia(25, 9, 12), {})
    cenario.recorrer()
    cenario.definitivas = cenario.publicar_resultados(
        "DEFINITIVA", dia(6, 10, 12), cenario.preliminares
    )
    cenario.apurar()
    cenario.convocar()
    if final == "sem-pendencia":
        cenario.aceitar(None, dia(16, 10, 11))
        cenario.aceitar(cenario.PPP, dia(17, 10, 11))
        cenario.encerrar()
    else:
        cenario.encerrar()
        cenario.aceitar(None, dia(21, 10, 11))
    cenario.edital.refresh_from_db()
    return cenario
