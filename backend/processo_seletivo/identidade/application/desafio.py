"""Solicitar e validar o código que prova o controle de um endereço.

Três coisas decidem o desenho aqui, e todas as três estão na spec por um motivo verificável.

**A resposta é sempre a mesma** (FR-020, FR-021). Exista ou não identidade associada ao endereço, o
visitante vê o mesmo texto, o mesmo estado e a mesma janela de espera. Isso só se sustenta porque os
limites são por **endereço** e por **origem**, e nunca por identidade: um contador que só avança
para quem existe é canal lateral que anula a equivalência inteira.

**O consumo é atômico** (FR-025). Uma atualização condicional que só vale se afetar exatamente uma
linha — o mesmo idioma de `shared/concurrency.compare_and_swap`. Ler, verificar e gravar depois
deixaria duas abas consumirem o mesmo código.

**Os contadores vivem no banco** (FR-032). `CACHES` não está configurado; o padrão do Django é
cache local por processo, e um limite guardado ali seria contornável com mais de um worker — a
spec estaria prometendo proteção que a implantação não tem.
"""

import hashlib
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from processo_seletivo.identidade.domain import codigo as codigo_de_acesso
from processo_seletivo.identidade.models import (
    TETO_DE_TENTATIVAS,
    VALIDADE_EM_MINUTOS,
    DesafioDeAcesso,
)

# A janela e os tetos são constantes da aplicação, e não configuração de usuário (FR-030).
JANELA = timedelta(hours=1)
ESPERA_ENTRE_ENVIOS = timedelta(seconds=60)
LIMITE_POR_ENDERECO = 5
# Mais folgado que o do endereço, e deliberadamente: uma família, um laboratório de escola ou um
# telecentro compartilham origem, e um teto apertado ali recusaria gente legítima em bloco. Não
# existe teto **global** por razão parecida, e mais forte: converteria abuso distribuído em
# indisponibilidade para todos os candidatos, no dia em que ela mais custa.
LIMITE_POR_ORIGEM = 30


@dataclass(frozen=True)
class Recibo:
    """O que a tela pode dizer — e que é igual para todo mundo.

    `proxima_tentativa_em` existe para a UX-006: reenviar precisa informar quando a próxima
    tentativa é possível. O valor não depende de existir identidade, porque o contador não depende.
    """

    proxima_tentativa_em: int


def _resumir_origem(origem: str) -> str:
    """Resumo, e nunca o endereço de rede em claro.

    A contagem por origem não precisa saber de onde veio; precisa distinguir uma origem da outra.
    Guardar o resumo é o que atende à minimização sem perder a contagem (Princípio III).
    """
    if not origem:
        return ""
    return hashlib.sha256(origem.encode()).hexdigest()


def _espera_restante(email_canonico: str, agora) -> int:
    ultimo = (
        DesafioDeAcesso.objects.filter(email_canonico=email_canonico)
        .order_by("-criado_em")
        .values_list("criado_em", flat=True)
        .first()
    )
    if not ultimo:
        return 0
    restante = (ultimo + ESPERA_ENTRE_ENVIOS - agora).total_seconds()
    return max(0, int(restante))


def _excedeu_limites(email_canonico: str, origem_hash: str, agora) -> bool:
    desde = agora - JANELA
    por_endereco = DesafioDeAcesso.objects.filter(
        email_canonico=email_canonico, criado_em__gte=desde
    ).count()
    if por_endereco >= LIMITE_POR_ENDERECO:
        return True
    if not origem_hash:
        return False
    por_origem = DesafioDeAcesso.objects.filter(
        origem_hash=origem_hash, criado_em__gte=desde
    ).count()
    return por_origem >= LIMITE_POR_ORIGEM


def solicitar(*, email_canonico: str, finalidade: str, origem: str = "") -> tuple[Recibo, str]:
    """Cria o desafio e devolve o recibo — mais o código, para quem vai enviá-lo.

    Devolver o código em vez de enviá-lo daqui mantém este módulo sem saber o que é uma mensagem, e
    permite ao teste ler o que a pessoa receberia. Quem envia é `mensagem.py`.

    Quando o limite está esgotado, **o recibo continua o mesmo** e nenhum código é gerado: quem
    olha de fora não distingue os dois casos.
    """
    agora = timezone.now()
    origem_hash = _resumir_origem(origem)
    espera = _espera_restante(email_canonico, agora)
    if espera > 0 or _excedeu_limites(email_canonico, origem_hash, agora):
        return Recibo(proxima_tentativa_em=espera or int(ESPERA_ENTRE_ENVIOS.total_seconds())), ""

    codigo = codigo_de_acesso.gerar()
    with transaction.atomic():
        # Um novo código invalida os anteriores ainda utilizáveis daquele endereço (FR-026). Vale
        # apenas para os que ainda não foram consumidos: o consumido pode estar portando uma
        # reconciliação pendente, e derrubá-lo faria a pessoa perder o convite ao pedir outro
        # código por engano.
        DesafioDeAcesso.objects.filter(
            email_canonico=email_canonico, consumido_em__isnull=True, expira_em__gt=agora
        ).update(expira_em=agora)
        DesafioDeAcesso.objects.create(
            email_canonico=email_canonico,
            finalidade=finalidade,
            codigo_hash=codigo_de_acesso.resumir(codigo),
            origem_hash=origem_hash,
            expira_em=agora + timedelta(minutes=VALIDADE_EM_MINUTOS),
            criado_em=agora,
        )
    return Recibo(proxima_tentativa_em=int(ESPERA_ENTRE_ENVIOS.total_seconds())), codigo


def validar(*, email_canonico: str, finalidade: str, codigo: str) -> DesafioDeAcesso | None:
    """Devolve o desafio consumido, ou `None` — e `None` não diz qual dos quatro motivos foi.

    Código errado, expirado, já usado e acima do teto respondem igual (FR-031). Distingui-los
    diria a quem está tentando o que ainda vale a pena tentar.
    """
    agora = timezone.now()
    desafio = (
        DesafioDeAcesso.objects.filter(
            email_canonico=email_canonico,
            finalidade=finalidade,
            consumido_em__isnull=True,
            expira_em__gt=agora,
            tentativas_codigo__lt=TETO_DE_TENTATIVAS,
        )
        .order_by("-criado_em")
        .first()
    )
    if desafio is None:
        return None

    if not codigo_de_acesso.confere(codigo_de_acesso.normalizar(codigo), desafio.codigo_hash):
        # Incremento condicional: duas abas não dividem o mesmo orçamento de tentativas por engano.
        DesafioDeAcesso.objects.filter(pk=desafio.pk).update(
            tentativas_codigo=F("tentativas_codigo") + 1
        )
        return None

    # O consumo inteiro numa instrução: só vale se afetar exatamente uma linha. É o que impede duas
    # requisições simultâneas aproveitarem o mesmo código (FR-025).
    consumidos = DesafioDeAcesso.objects.filter(
        pk=desafio.pk, consumido_em__isnull=True, expira_em__gt=agora
    ).update(consumido_em=agora)
    if consumidos != 1:
        return None
    desafio.refresh_from_db()
    return desafio


def limpar_terminais(*, ate=None) -> int:
    """Desafio terminal não é dado permanente de domínio (FR-033).

    Consumido, expirado ou morto por tentativas: nada disso precisa sobreviver à investigação, que
    lê a trilha de auditoria, não esta tabela.
    """
    limite = ate or timezone.now() - JANELA
    return DesafioDeAcesso.objects.filter(criado_em__lt=limite).delete()[0]
