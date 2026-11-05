"""Monta um cenário da 118 num banco próprio, para o estudo da experiência da convocação.

Uso: LETRA=C1 [CORRIGIR=1] manage.py shell < montar.py
"""

import os
from datetime import timedelta

from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
from rest_framework.test import APIClient

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures import jornada_do_convocado as J
from tests.fixtures.autoridades import garantir_o_cefor
from tests.fixtures.candidato import IdentidadeDoCandidato, registrar

letra = os.environ["LETRA"]
garantir_o_cefor()
gestor = Actor("carlos", "cefor", frozenset({"comissao:gerir"}))
headers = {
    "HTTP_AUTHORIZATION": "Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
    "HTTP_IDEMPOTENCY_KEY": f"estudo-conv-processo-{letra.lower()}-0001",
    "HTTP_X_CORRELATION_ID": "estudo-conv",
}
payload = {
    "institutionalCode": f"PS-2026-EST-{letra}",
    "title": "Processo Seletivo 2026/1 — Curso Técnico em Informática",
    "firstEdital": {"number": "72", "year": 2026, "title": "Curso Técnico em Informática"},
}
c = J.montar(letra, J.Montagem(gestor, APIClient(), headers, payload))
p = c.pessoa

if os.environ.get("CORRIGIR"):
    # A correção pela sucessão (120): mesma pessoa, motivo escrito, vencimento novo.
    from tests.fixtures.convocacao import convocar
    from tests.fixtures import documentos_da_convocacao as D
    from processo_seletivo.convocacao.models import Convocacao

    declarado = convocar(
        c.edital,
        gestor,
        p.id,
        idempotency_key="corrigir-estudo-conv",
        vencimento=timezone.now() + timedelta(days=7),
        motivo="O prazo da convocação anterior foi informado com erro; esta convocação o corrige.",
    )
    nova = Convocacao.objects.get(id=declarado["id"])
    D.comunicar(c.edital, gestor, nova, chave="comunicar-correcao-estudo")
    print("SUCESSORA", nova.id, nova.vencimento, "anterior", nova.convocacao_anterior_id)

for i in Inscricao.objects.filter(edital=c.edital):
    eh = i.id == p.id
    registrar(
        IdentidadeDoCandidato(
            i.identity_subject,
            i.nome,
            "529.982.247-25" if eh else "",
            i.email if eh else "",
        )
    )

registro = CandidateIdentity.objects.get(subject=p.identity_subject)
s = SessionStore()
s[CHAVE_SESSAO] = str(registro.pk)
s.create()
print("EDITAL", c.edital.id)
print("INSCRICAO", p.id, p.protocolo, p.nome, p.email)
print("CONVOCACAO", c.convocacao.id, c.convocacao.vencimento, c.convocacao.especie)
print("SESSIONID", s.session_key)
print("FIM")
