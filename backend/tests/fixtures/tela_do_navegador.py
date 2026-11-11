"""A tela de cada pessoa nas jornadas de navegador: sessão, console vigiado e capturas (115, 146).

Saiu de `navegador/test_jornada_dos_documentos_da_convocacao.py` quando a jornada do barema passou
a precisar dela: a função compartilhada mora em `tests/fixtures`, e cada módulo declara a fixture
dele — a regra que a 081 fixou para as telas da presidência (FR-1823).
"""

import os
import re
from pathlib import Path

CELULAR = {"width": 375, "height": 812}
DESKTOP = {"width": 1280, "height": 900}


class Tela:
    """Um navegador por pessoa, com o console vigiado e as capturas do caso."""

    def __init__(self, navegador, servidor, caso):
        self._navegador = navegador
        self.servidor = servidor
        self._capturas = os.getenv("NAVEGADOR_CAPTURAS")
        self._caso = re.sub(r"\W+", "-", caso)
        self._passo = 0
        self._contextos = []
        self.violacoes = []

    def _nova(self, viewport):
        contexto = self._navegador.new_context(viewport=viewport)
        self._contextos.append(contexto)
        pagina = contexto.new_page()
        pagina.set_default_timeout(10_000)
        pagina.on(
            "console",
            lambda mensagem: (
                self.violacoes.append(mensagem.text)
                if "Content Security Policy" in mensagem.text
                else None
            ),
        )
        return pagina

    def gestao(self, subject, papeis=(), viewport=DESKTOP):
        """A sessão da gestão pelo seletor de identidade, como `identificar` dos testes de tela.

        O seletor é a entrada de demonstração que o ambiente local oferece, e a sessão que ele abre
        é a mesma que o navegador leva — o cookie é só o transporte.
        """
        from django.test import Client
        from django.urls import reverse

        cliente = Client()
        resposta = cliente.post(
            reverse("interface:identificar"), {"subject": subject, "papeis": list(papeis)}
        )
        assert resposta.status_code == 302, resposta.content
        pagina = self._nova(viewport)
        pagina.context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": cliente.cookies["sessionid"].value,
                    "url": self.servidor.url,
                }
            ]
        )
        return pagina

    def candidato(self, inscricao, viewport=CELULAR):
        from django.contrib.sessions.backends.db import SessionStore
        from django.utils import timezone

        from processo_seletivo.identidade.models import CandidateIdentity
        from processo_seletivo.portal.identidade import CHAVE_SESSAO

        registro, _ = CandidateIdentity.objects.get_or_create(
            subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
        )
        sessao = SessionStore()
        sessao[CHAVE_SESSAO] = str(registro.pk)
        sessao.save()
        pagina = self._nova(viewport)
        pagina.context.add_cookies(
            [{"name": "sessionid", "value": sessao.session_key, "url": self.servidor.url}]
        )
        return pagina

    def capturar(self, pagina, rotulo):
        if not self._capturas:
            return
        self._passo += 1
        destino = Path(self._capturas) / f"{self._caso}-{self._passo:02d}-{rotulo}.png"
        destino.parent.mkdir(parents=True, exist_ok=True)
        pagina.screenshot(path=str(destino), full_page=True)

    def fechar(self):
        for contexto in self._contextos:
            contexto.close()
