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


def _id(sufixo):
    return f"00000000-0000-0000-00{NUMERO}-0000000000{sufixo}"


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


def _cronograma():
    eventos = [
        ("Inscrições", "Inscrições pelo sistema.", dia(10, 8, 0), dia(30, 8, 23, 59)),
        ("Prova objetiva", "Aplicação da prova no Campus Vitória.", dia(13, 9, 8), None),
        ("Análise de títulos", "Avaliação dos títulos.", dia(16, 9, 8), dia(22, 9, 18)),
        ("Resultado preliminar", "Resultado preliminar e prazo de recurso.", dia(25, 9, 12), None),
        ("Resultado definitivo", "Resultado definitivo.", dia(6, 10, 12), None),
    ]
    return [
        {
            "id": _id(f"c{i}"),
            "type": tipo,
            "description": descricao,
            "startAt": inicio,
            "endAt": fim,
            "order": i,
            "isRegistrationPeriod": i == 1,
        }
        for i, (tipo, descricao, inicio, fim) in enumerate(eventos, 1)
    ]


def _perfis():
    from processo_seletivo.processos.management.commands import seed_demo

    perfis = seed_demo.perfis(NUMERO, janela_recursal="declarada")
    # O marco do cadastro de reserva do semeador não declara prazo recursal, e a definitiva o
    # recusaria; aqui os dois marcos declaram os mesmos cinco dias.
    perfis[1]["classificationMilestones"][0].update(seed_demo._janela_do_marco("declarada"))
    return perfis


def _etapas():
    from processo_seletivo.processos.management.commands import seed_demo

    etapas = seed_demo.etapas(NUMERO)
    etapas[0]["scheduleEventId"] = _id("c2")
    etapas[1]["scheduleEventId"] = _id("c3")
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

    def __init__(self, escala):
        self.escala = escala
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

        with em(dia(3, 8, 9)):
            self.comando = seed_demo.Command(stdout=io.StringIO())
            self.comando.janela_recursal = "declarada"
            self.comando._unidade_e_autoridades()
            elaborador = _ator(
                "ana.elaboradora", "processo:criar", "edital:elaborar", "edital:submeter"
            )
            self.processo, _ = create_process_with_first_edital(
                actor=elaborador,
                data={
                    "institutionalCode": "PS-CEFOR-2026-2",
                    "title": "Processo Seletivo Simplificado 2026/2",
                    "firstEdital": {
                        "number": NUMERO,
                        "year": 2026,
                        "title": "Edital 61/2026 — Professor de Informática e Técnico",
                        "description": "Seleção simplificada.",
                    },
                },
                idempotency_key="099-processo",
                correlation_id=CORRELACAO,
            )
            self.edital = Edital.objects.get(processo=self.processo)
            replace_draft(
                actor=elaborador,
                edital_id=self.edital.id,
                expected_revision=self.edital.revision,
                profiles=_perfis(),
                schedule=_cronograma(),
                stages=_etapas(),
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
                            "targetPath": f"/schedule/id={EVENTO_DAS_INSCRICOES}/endAt",
                            "operation": "REPLACE",
                            "newValue": dia(4, 9, 23, 59).isoformat(),
                        }
                    ],
                },
                idempotency_key="099-ret",
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
                    idempotency_key=f"099-ret-{acao}",
                    correlation_id=CORRELACAO,
                )
            publish_retification(
                actor=_ator("carla.publicadora", "retificacao:publicar"),
                retificacao_id=retificacao.id,
                expected_revision=retificacao.revision,
                autoridade_id=self.comando.autoridades[seed_demo.CARGO_DO_EDITAL],
                idempotency_key="099-ret-publicar",
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
        pedidos = [(x, PROF, AC_PROF) for x in p[: 20 * e]]
        pedidos += [(x, PROF, PPP) for x in p[20 * e : 26 * e]]
        pedidos += [(x, TEC, AC_TEC) for x in p[26 * e : 36 * e]]
        # Duas pessoas se inscrevem nos dois Perfis: 38 inscrições de 36 cadastros.
        pedidos += [(p[0], TEC, AC_TEC), (p[1], TEC, AC_TEC)]
        self.rng.shuffle(pedidos)
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
                    idempotency_key=f"099-envio-{pessoa.subject}-{perfil[-2:]}",
                )
        if ate is not None:
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
                    profile_id=PROF if indice % 2 else TEC,
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
                    idempotency_key=f"099-membro-{k}",
                    correlation_id=CORRELACAO,
                )
            for etapa in (PROVA, TITULOS, DOCUMENTAL):
                for nome in ("joana.avaliadora", "otavio.avaliador"):
                    alocar(
                        actor=self.gestor,
                        processo_id=self.processo.id,
                        membro_id=self.membros[nome].id,
                        edital_id=self.edital.id,
                        etapa_id=etapa,
                        idempotency_key=f"099-aloc-{etapa[-2:]}-{nome[:4]}",
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
                idempotency_key=f"099-lote-{chave}",
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
                idempotency_key=f"099-consolidar-{chave}",
                correlation_id=CORRELACAO,
            )

    def avaliar(self):
        from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia

        todas = list(self.inscricoes.values())
        self.ausente = next(
            i for i in todas if str(i.profile_id) == PROF and str(i.modality_id) == AC_PROF
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
                etapa_id=PROVA,
                inscricao_ids=[self.ausente.id],
                motivo="Ausência na prova objetiva, conforme lista de presença.",
                idempotency_key="099-ocorrencia",
                correlation_id=CORRELACAO,
            )
        self.presentes = [i for i in todas if i.id != self.ausente.id]
        self._avaliar(PROVA, self.presentes, self.nota_prova, dia(16, 9, 9), "prova")
        self.habilitadas = [i for i in self.presentes if self.nota_prova[i.id] >= Decimal("6")]
        self._avaliar(TITULOS, self.habilitadas, self.nota_titulos, dia(19, 9, 9), "titulos")

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
                (PROF, MARCO_PROF, None),
                (PROF, MARCO_PROF, PPP),
                (TEC, MARCO_TEC, None),
            ):
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
                    idempotency_key=f"099-ordem-{marco[-2:]}-{lista}",
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
                    idempotency_key=f"099-pub-{natureza}-{marco[-2:]}-{lista}",
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
                    if str(i.profile_id) == PROF and self.nota_prova[i.id] < 6
                ),
                (MARCO_PROF, None),
                dia(26, 9, 14),
                False,
            ),
            (
                next(
                    i
                    for i in self.habilitadas
                    if str(i.profile_id) == PROF and str(i.modality_id) == PPP
                ),
                (MARCO_PROF, PPP),
                dia(27, 9, 16),
                True,
            ),
            (
                next(i for i in self.habilitadas if str(i.profile_id) == TEC),
                (MARCO_TEC, None),
                dia(29, 9, 10),
                True,
            ),
        ]
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
                    idempotency_key=f"099-rec-{k}",
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
                    idempotency_key=f"099-adm-{k}",
                )
                if admitido:
                    peca.refresh_from_db()
                    julgar(
                        actor=julgadora,
                        recurso_id=peca.id,
                        especie="INDEFERIDO",
                        motivacao="A pontuação confere com a planilha da banca.",
                        idempotency_key=f"099-julgar-{k}",
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
            for lista in (None, PPP):
                emitir_corte(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=PROF,
                    marco_id=MARCO_PROF,
                    lista_id=lista,
                    idempotency_key=f"099-corte-{lista}",
                    correlation_id=CORRELACAO,
                    confirmacao_do_calculo=assinatura_do_corte(
                        calcular_corte(
                            edital=self.edital, perfil_id=PROF, marco_id=MARCO_PROF, lista_id=lista
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
        self._avaliar(DOCUMENTAL, self.progrediram, None, dia(8, 10, 14), "documental")
        with em(dia(10, 10, 9)):
            for lista in (None, PPP):
                emitir_apuracao(
                    actor=self.presidencia,
                    processo_id=self.processo.id,
                    edital_id=self.edital.id,
                    perfil_id=PROF,
                    marco_id=MARCO_PROF,
                    lista_id=lista,
                    idempotency_key=f"099-apurar-{lista}",
                    correlation_id=CORRELACAO,
                    motivo="",
                )

    def convocar(self):
        from processo_seletivo.convocacao.application.convocar import convocar

        with em(dia(13, 10, 10)):
            for lista, vencimento in ((None, dia(23, 10, 23, 59)), (PPP, dia(30, 10, 23, 59))):
                ato = self.atos[(MARCO_PROF, lista)]
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
                    perfil_id=PROF,
                    marco_id=MARCO_PROF,
                    lista_id=lista,
                    inscricao_id=primeira.id,
                    vencimento=vencimento,
                    fundamento="No interesse da Administração, conforme o item 8.2 do Edital.",
                    idempotency_key=f"099-convocar-{lista}",
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
                idempotency_key=f"099-aceite-{lista}",
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
                idempotency_key="099-encerrar",
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
                idempotency_key="099-cancelar",
                correlation_id=CORRELACAO,
            )


def montar_cenario(*, escala=1, final="pendente"):
    """Monta o Edital 61/2026 e devolve o cenário, com `edital` e `processo` atualizados."""
    if final not in {"pendente", "sem-pendencia", "aberto", "cancelado"}:
        raise ValueError(final)
    cenario = _Cenario(escala)
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
        cenario.aceitar(PPP, dia(17, 10, 11))
        cenario.encerrar()
    else:
        cenario.encerrar()
        cenario.aceitar(None, dia(21, 10, 11))
    cenario.edital.refresh_from_db()
    return cenario
