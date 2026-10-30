"""O contrato do adaptador institucional e o *backend* que o Django chama (106, `D-007`, `D-008`).

**Quem autentica é o provedor; o GPS só recebe o resultado.** O adaptador apontado por
`GESTAO_PROVEDOR_INSTITUCIONAL` entrega uma `IdentidadeAutenticada` de uma autenticação concluída,
ou nada. Nada do pedido do cliente — cabeçalho, parâmetro, corpo — vira identidade por outro
caminho: é o que separa este modo do `RemoteUserMiddleware`, que confia num cabeçalho e que
produção recusa.

**O *backend* não aceita senha.** É o único declarado em `AUTHENTICATION_BACKENDS`, e por isso um
`authenticate(username=..., password=...)` não encontra quem o atenda, e um `createsuperuser` não
abre porta nenhuma.
"""

import uuid
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.module_loading import import_string

from processo_seletivo.seguranca.models import IdentidadeExterna

# O que distingue o identificador interno de qualquer identidade de demonstração escrita à mão, e de
# um identificador qualquer num relatório da trilha (`D-002`).
PREFIXO_DO_IDENTIFICADOR = "pessoa-"


@dataclass(frozen=True)
class IdentidadeAutenticada:
    """O que o provedor afirma, depois de autenticar. Nenhum campo vem do cliente (`FR-3022`)."""

    provedor: str
    identificador: str
    nome: str = ""
    email: str = ""


def _em_producao():
    return bool(getattr(settings, "AMBIENTE_DE_PRODUCAO", False))


def caminho_do_provedor():
    caminho = (getattr(settings, "GESTAO_PROVEDOR_INSTITUCIONAL", "") or "").strip()
    # A mesma recusa de `production.py`, em execução: o código de teste não autentica ninguém sob a
    # marca de produção, mesmo que a configuração mude depois do *boot* (`FR-3026`).
    if _em_producao() and caminho.startswith("tests."):
        return ""
    return caminho


def provedor_configurado():
    """O adaptador deste ambiente, ou None.

    Lido a cada chamada, e não guardado no módulo: a suíte o liga e desliga por `settings`, e um
    adaptador guardado sobreviveria ao caso que o configurou.
    """
    caminho = caminho_do_provedor()
    if not caminho:
        return None
    classe = import_string(caminho)
    if _em_producao() and getattr(classe, "apenas_para_testes", False):
        return None
    return classe()


def novo_identificador():
    return f"{PREFIXO_DO_IDENTIFICADOR}{uuid.uuid4()}"


def _atualizar(pessoa, identidade):
    nome, email = identidade.nome[:150], identidade.email[:254]
    if (pessoa.first_name, pessoa.email) != (nome, email):
        # `update`, e não `save`: o `save` reescreveria o `username` com o mesmo valor, e o gatilho
        # só olha para a troca — mas a escrita mínima é a que não depende disso.
        get_user_model().objects.filter(pk=pessoa.pk).update(first_name=nome, email=email)
        pessoa.first_name, pessoa.email = nome, email
    return pessoa


def resolver_pessoa(identidade, *, now=None):
    """A pessoa desta identidade externa, criada no primeiro acesso (`FR-3005`, `FR-3006`).

    Devolve `(pessoa, identidade_externa)`. **Localiza só pelo par provedor e identificador**: nunca
    pelo e-mail, nem pelo texto de um `subject` — e por isso nenhuma identidade de demonstração se
    converte em institucional (`FR-3002`).
    """
    if not identidade.provedor or not identidade.identificador:
        return None, None
    now = now or timezone.now()
    try:
        externa = IdentidadeExterna.objects.select_related("pessoa").get(
            provedor=identidade.provedor, identificador=identidade.identificador
        )
    except IdentidadeExterna.DoesNotExist:
        try:
            with transaction.atomic():
                pessoa = get_user_model()(
                    username=novo_identificador(),
                    first_name=identidade.nome[:150],
                    email=identidade.email[:254],
                )
                pessoa.set_unusable_password()
                pessoa.save()
                externa = IdentidadeExterna.objects.create(
                    pessoa=pessoa,
                    provedor=identidade.provedor,
                    identificador=identidade.identificador,
                    associada_em=now,
                )
            return pessoa, externa
        except IntegrityError:
            # Dois primeiros acessos ao mesmo tempo: o outro criou. A pessoa criada aqui saiu com o
            # rollback do bloco, e a que vale é a dele.
            externa = IdentidadeExterna.objects.select_related("pessoa").get(
                provedor=identidade.provedor, identificador=identidade.identificador
            )
    return _atualizar(externa.pessoa, identidade), externa


class BackendInstitucional(BaseBackend):
    """Autentica uma `IdentidadeAutenticada`, e nada mais (`D-008`)."""

    def authenticate(self, request, identidade_institucional=None, **credenciais):
        if identidade_institucional is None:
            return None
        pessoa, externa = resolver_pessoa(identidade_institucional)
        if pessoa is None or not pessoa.is_active:
            return None
        # A identidade externa usada vai à trilha da entrada (`D-010`), e o `login()` do Django só
        # carrega o usuário: pendurá-la nele evita reler o que acabou de ser lido.
        pessoa.identidade_externa_usada = externa
        return pessoa

    def get_user(self, user_id):
        # `is_active` falso devolve anônimo, e o Django encerra a sessão aberta na requisição
        # seguinte (`FR-3021`).
        return get_user_model().objects.filter(pk=user_id, is_active=True).first()
