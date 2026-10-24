"""Completa o ciclo do Edital 51 da demonstração pelos commands da aplicação.

Roda dentro de `manage.py shell` num banco semeado com `seed_demo --dias-atras 20`.
Recurso julgado (no passado, dentro da janela), resultado definitivo, encerramento do Edital,
e um desfecho de convocação registrado DEPOIS do encerramento — para a maquete mostrar R-16.
"""

import contextlib
from datetime import timedelta

from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.divulgacao.application.publicar import assinatura_da_previa, publicar_resultado
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from processo_seletivo.processos.application.finalizacao import close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.recursos.application.interpor import interpor
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.application.selectors import assinatura_do_estado_da_peca
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.models import AutoridadeHabilitada

ESCOPO = "cefor"


def ator(subject, *permissoes):
    return Actor(subject, ESCOPO, frozenset(permissoes))


@contextlib.contextmanager
def relogio(dias):
    real = timezone.now
    timezone.now = lambda: real() - timedelta(days=dias)
    try:
        yield
    finally:
        timezone.now = real


edital = Edital.objects.get(number="51")
preliminar = PublicacaoResultado.objects.get(ato__edital=edital, natureza="PRELIMINAR")
daniel = Inscricao.objects.get(edital=edital, nome="Daniel Rocha")

with relogio(19):
    recurso = interpor(
        identidade=IdentidadeDoCandidato(
            daniel.identity_subject, daniel.nome, daniel.cpf_normalizado, "daniel@exemplo.test"
        ),
        inscricao=daniel,
        publicacao=preliminar,
        fundamentacao="Fiz a segunda prova e não recebi nota.",
        assinatura_do_objeto=str(preliminar.pk),
        idempotency_key="maquete-recurso",
    )
    julgadora = ator("helena.julgadora", "recurso:julgar")
    admitir(
        actor=julgadora,
        recurso_id=recurso.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_do_estado_da_peca(recurso),
        idempotency_key="maquete-admitir",
    )
    recurso.refresh_from_db()
    julgar(
        actor=julgadora,
        recurso_id=recurso.id,
        especie="INDEFERIDO",
        motivacao="Não há registro de comparecimento à segunda Etapa.",
        idempotency_key="maquete-julgar",
    )
print("recurso julgado")

ato = AtoDeOrdenacao.objects.get(edital=edital, sucessores__isnull=True)
autoridade = AutoridadeHabilitada.objects.filter(cargo__startswith="Diretora-Geral").first()
with relogio(10):
    publicar_resultado(
        actor=ator("paula.publicadora", "resultado:publicar"),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=preliminar.marco_id,
        ato_id=ato.id,
        natureza="DEFINITIVA",
        autoridade=str(autoridade.pk),
        confirmacao_da_previa=assinatura_da_previa(
            ato=ato, publicacao_anterior=preliminar, projecao=compor(ato)
        ),
        idempotency_key="maquete-definitiva",
        correlation_id="maquete",
    )
print("definitiva publicada")

with relogio(3):
    edital.refresh_from_db()
    close_edital(
        actor=ator("gustavo.gestor", "edital:encerrar"),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Resultado definitivo divulgado e vaga ocupada.",
        idempotency_key="maquete-encerrar",
        correlation_id="maquete",
    )
print("edital encerrado")

convocacao = Convocacao.objects.get(inscricao__edital=edital, convocacao_anterior__isnull=True)
desfechar(
    actor=ator("paulo.presidente"),
    processo_id=edital.processo_id,
    convocacao_id=convocacao.id,
    especie="ACEITE",
    fundamento="Requerimento de matrícula enviado e conferido.",
    idempotency_key="maquete-desfecho",
    correlation_id="maquete",
)
print("desfecho depois do encerramento")
