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
import logging
import math
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from processo_seletivo.identidade.domain import codigo as codigo_de_acesso
from processo_seletivo.identidade.models import (
    TETO_DE_TENTATIVAS,
    VALIDADE_EM_MINUTOS,
    DesafioDeAcesso,
)

logger = logging.getLogger("processo_seletivo.identidade")

# A janela e os tetos são constantes da aplicação, e não configuração de usuário (FR-030).
JANELA = timedelta(hours=1)
ESPERA_ENTRE_ENVIOS = timedelta(seconds=60)
LIMITE_POR_ENDERECO = 5
# Mais folgado que o do endereço, e deliberadamente: uma família, um laboratório de escola ou um
# telecentro compartilham origem, e um teto apertado ali recusaria gente legítima em bloco. Não
# existe teto **global** por razão parecida, e mais forte: converteria abuso distribuído em
# indisponibilidade para todos os candidatos, no dia em que ela mais custa.
#
# **Trinta continua, e o que mudou foi a resposta a quem passa dele** (FR-031c). Um polo com
# quarenta pessoas na mesma hora recusa dez — e o defeito era que essas dez liam "pode pedir outro
# código agora", com o bloqueio valendo ainda por até uma hora. Subir o número só mudaria o tamanho
# da sala que esbarra nele; dizer o que aconteceu, por quanto tempo, e que outra conexão resolve é o
# que tira o candidato do beco. O número é constante pela FR-030, e torná-lo ajustável é decisão
# registrada, não tomada aqui.
LIMITE_POR_ORIGEM = 30

# Por que o pedido não gerou código. Nenhum dos três depende de existir identidade: os contadores
# são por endereço, por finalidade e por origem (FR-021), e dizê-los não revela quem existe.
EM_ESPERA = "espera_de_reenvio"
TETO_DO_ENDERECO = "limite_por_endereco"
TETO_DA_ORIGEM = "limite_por_origem"


@dataclass(frozen=True)
class Bloqueio:
    """O que impede outro envio agora, e em quantos segundos deixa de impedir.

    Os segundos saem do registro que vai sair da janela, e não de uma constante: o teto da origem
    era anunciado como "sessenta segundos" enquanto valia por até uma hora (FR-031c).
    """

    motivo: str
    segundos: int

    @property
    def e_teto(self) -> bool:
        return self.motivo != EM_ESPERA


@dataclass(frozen=True)
class Recibo:
    """O que a tela pode dizer — e que é igual para todo mundo.

    `proxima_tentativa_em` existe para a UX-006: reenviar precisa informar quando a próxima
    tentativa é possível. O valor não depende de existir identidade, porque o contador não depende.
    `bloqueio` é `None` quando o código foi gerado.
    """

    proxima_tentativa_em: int
    bloqueio: Bloqueio | None = None


def _resumir_origem(origem: str) -> str:
    """Resumo, e nunca o endereço de rede em claro.

    A contagem por origem não precisa saber de onde veio; precisa distinguir uma origem da outra.
    Guardar o resumo é o que atende à minimização sem perder a contagem (Princípio III).
    """
    if not origem:
        return ""
    return hashlib.sha256(origem.encode()).hexdigest()


def _espera_restante(email_canonico: str, finalidade: str, agora) -> int:
    """A espera é por endereço **e finalidade**, e o teto por hora é por endereço.

    São duas proteções com alvos distintos. A espera de um minuto existe para não transformar um
    clique repetido em enxurrada de mensagens iguais; o teto por hora existe para conter quem varre.
    Prender a espera só ao endereço confundia as duas: quem acabava de entrar e clicava em vincular
    a participação anterior era mandado para a tela do código sem código nenhum, porque o pedido
    anterior — de outra finalidade, feito segundos antes — ainda ocupava a janela.

    Alternar finalidades não é atalho para quem ataca: a única alcançável sem sessão é `ENTRAR`.
    """
    ultimo = (
        DesafioDeAcesso.objects.filter(email_canonico=email_canonico, finalidade=finalidade)
        .order_by("-criado_em")
        .values_list("criado_em", flat=True)
        .first()
    )
    if not ultimo:
        return 0
    restante = (ultimo + ESPERA_ENTRE_ENVIOS - agora).total_seconds()
    return max(0, int(restante))


def _liberacao_do_teto(filtro: Q, limite: int, agora) -> int:
    """Segundos até a janela de uma hora deixar de estar cheia; zero se ela não está.

    A janela desliza: o teto se abre quando sai dela o pedido que a mantém cheia — o
    `excedente`-ésimo mais antigo, que é o mais antigo de todos quando a contagem está exatamente
    no teto. Lido assim, e não como "uma hora a partir de agora", o tempo anunciado é o efetivo: a
    sala cujos pedidos se espalharam pela hora espera minutos, e não a hora inteira. Pedidos
    simultâneos podem passar o teto em alguns (ver `test_limite_concorrente`), e o índice cobre
    isso — com dois a mais, são três os que precisam sair.
    """
    momentos = list(
        DesafioDeAcesso.objects.filter(filtro, criado_em__gte=agora - JANELA)
        .order_by("criado_em")
        .values_list("criado_em", flat=True)
    )
    excedente = len(momentos) - limite
    if excedente < 0:
        return 0
    # Arredondado para cima e nunca zero: no instante exato da liberação o pedido ainda conta
    # (`criado_em__gte`), e anunciar "agora" ali seria anunciar uma recusa.
    return max(1, math.ceil((momentos[excedente] + JANELA - agora).total_seconds()))


def _bloqueio(email_canonico: str, finalidade: str, origem_hash: str, agora) -> Bloqueio | None:
    """O impedimento que vale — o mais longo, quando há mais de um.

    O mais longo, porque é o que a pessoa vai de fato esperar: anunciar a espera de um minuto com o
    teto do endereço valendo por quarenta é a mesma mentira que este achado corrige. No empate, o
    teto do endereço vem antes do da origem, porque trocar de rede não o resolve.
    """
    vigentes = [
        bloqueio
        for bloqueio in (
            Bloqueio(
                TETO_DO_ENDERECO,
                _liberacao_do_teto(Q(email_canonico=email_canonico), LIMITE_POR_ENDERECO, agora),
            ),
            Bloqueio(
                TETO_DA_ORIGEM,
                _liberacao_do_teto(Q(origem_hash=origem_hash), LIMITE_POR_ORIGEM, agora)
                if origem_hash
                else 0,
            ),
            Bloqueio(EM_ESPERA, _espera_restante(email_canonico, finalidade, agora)),
        )
        if bloqueio.segundos > 0
    ]
    return max(vigentes, key=lambda bloqueio: bloqueio.segundos) if vigentes else None


def bloqueio_atual(*, email_canonico: str, finalidade: str, origem: str = "") -> Bloqueio | None:
    """O que impede outro envio agora, e não quando a página foi montada.

    A tela guardava o valor devolvido pelo recibo e o repetia a cada renderização, então ele
    envelhecia: depois de dois minutos parados na página, ela ainda anunciava sessenta segundos de
    espera. Recalcular na leitura é o que permite ao botão dizer a verdade e ao contador chegar a
    zero (UX-006). Até a FR-031c lia-se só a espera — e a tela de quem esbarrava num teto dizia
    "pode pedir outro código agora".
    """
    return _bloqueio(email_canonico, finalidade, _resumir_origem(origem), timezone.now())


def _registrar_recusa(bloqueio: Bloqueio, finalidade: str, origem_hash: str) -> None:
    """Uma linha estruturada por pedido recusado, para que a recusa deixe rastro.

    Sem ela, a sala inteira de um polo recusada no último dia era indistinguível de correio caído.
    O `code` separa os três motivos entre si e da falha de envio, que `mensagem.py` registra com o
    seu. Não leva endereço nem código; da origem leva o começo do mesmo resumo que a tabela já
    guarda — o bastante para contar quantas redes bateram no teto, ou conferir a de um polo
    conhecido, e nada que a tabela não tenha. A espera não é alarme, e por isso é só informação.
    """
    logger.log(
        logging.INFO if bloqueio.motivo == EM_ESPERA else logging.WARNING,
        "codigo_de_acesso_nao_enviado",
        extra={
            "code": bloqueio.motivo,
            "operation": f"identidade.solicitar_codigo.{finalidade.lower()}",
            "origin": origem_hash[:12],
            "retryAfter": bloqueio.segundos,
        },
    )


def solicitar(*, email_canonico: str, finalidade: str, origem: str = "") -> tuple[Recibo, str]:
    """Cria o desafio e devolve o recibo — mais o código, para quem vai enviá-lo.

    Devolver o código em vez de enviá-lo daqui mantém este módulo sem saber o que é uma mensagem, e
    permite ao teste ler o que a pessoa receberia. Quem envia é `mensagem.py`.

    Quando um limite está esgotado, nenhum código é gerado, e o recibo diz qual limite e por quanto
    tempo (FR-031c). Ele dizia "o mesmo que o caminho feliz", com a espera de sessenta segundos — e
    esconder o teto não protegia nada, porque nenhum contador depende de existir identidade: só
    mandava a pessoa clicar de novo num botão que continuaria recusando por uma hora.
    """
    agora = timezone.now()
    origem_hash = _resumir_origem(origem)
    bloqueio = _bloqueio(email_canonico, finalidade, origem_hash, agora)
    if bloqueio is not None:
        _registrar_recusa(bloqueio, finalidade, origem_hash)
        return Recibo(proxima_tentativa_em=bloqueio.segundos, bloqueio=bloqueio), ""

    codigo = codigo_de_acesso.gerar()
    with transaction.atomic():
        # Um novo código invalida os anteriores ainda utilizáveis **daquele endereço e daquela
        # finalidade** (FR-026 lida junto com a FR-028). Antes o escopo era só o endereço, e ficava
        # assimétrico com a espera de reenvio, que já era por finalidade: pedir um código para
        # adicionar credencial derrubaria, calado, o código de acesso pedido noutra aba — e a
        # pessoa leria "código inválido" sem ter feito nada errado. Como finalidade nenhuma valida
        # a de outra, restringir o escopo não afrouxa nada.
        #
        # Só os não consumidos: o consumido pode estar portando uma reconciliação pendente, e
        # derrubá-lo faria a pessoa perder o convite ao pedir outro código por engano.
        DesafioDeAcesso.objects.filter(
            email_canonico=email_canonico,
            finalidade=finalidade,
            consumido_em__isnull=True,
            expira_em__gt=agora,
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

    # **A tentativa é reservada antes de o código ser conferido**, e a reserva é que impõe o teto.
    #
    # A primeira versão incrementava depois, filtrando só pelo `pk` — e por isso não impunha nada:
    # dez requisições simultâneas liam `tentativas_codigo = 0`, todas erravam, e todas
    # incrementavam. O contador terminava em dez, e as dez tinham sido avaliadas. O teto existia no
    # texto e não no banco.
    #
    # Reservar primeiro inverte isso: quem não consegue a reserva não chega a conferir código
    # nenhum. O `UPDATE` condicional é o ponto de serialização, e ele vale para acerto e erro —
    # tentativa é tentativa (FR-029).
    reservada = DesafioDeAcesso.objects.filter(
        pk=desafio.pk,
        consumido_em__isnull=True,
        expira_em__gt=agora,
        tentativas_codigo__lt=TETO_DE_TENTATIVAS,
    ).update(tentativas_codigo=F("tentativas_codigo") + 1)
    if reservada != 1:
        return None

    if not codigo_de_acesso.confere(codigo_de_acesso.normalizar(codigo), desafio.codigo_hash):
        return None

    # O consumo inteiro numa instrução: só vale se afetar exatamente uma linha. É o que impede duas
    # requisições simultâneas aproveitarem o mesmo código (FR-025). O teto entra aqui de novo, e
    # não por desconfiança da reserva: é o invariante escrito onde ele é lido — nenhuma linha sai
    # daqui consumida tendo passado do quinto ensaio.
    consumidos = DesafioDeAcesso.objects.filter(
        pk=desafio.pk,
        consumido_em__isnull=True,
        expira_em__gt=agora,
        tentativas_codigo__lte=TETO_DE_TENTATIVAS,
    ).update(consumido_em=agora)
    if consumidos != 1:
        return None
    desafio.refresh_from_db()
    return desafio


SEM_DESAFIO = "sem_desafio"
ESGOTADO = "esgotado"
EXPIRADO = "expirado"
CODIGO_ERRADO = "codigo_errado"


@dataclass(frozen=True)
class Estado:
    """Por que a última tentativa não valeu — e quantas ainda restam."""

    motivo: str
    tentativas_restantes: int


def estado_atual(*, email_canonico: str, finalidade: str) -> Estado:
    """Classifica o desafio pendente depois de uma tentativa recusada.

    **Isto não afrouxa a FR-031.** O que aquela regra proíbe é distinguir *código errado de
    endereço inexistente* — e nada aqui distingue: `solicitar` cria desafio para qualquer endereço
    de forma aceitável, exista identidade ou não, então os quatro motivos e a contagem restante são
    exatamente os mesmos nos dois casos. O que se lê é o estado do desafio que **esta própria
    sessão** pediu, e que ela já conhece por ter contado os próprios erros.

    O que a mensagem única custava era concreto: esgotadas as cinco tentativas, quem finalmente
    achava o código certo na caixa de entrada e o digitava corretamente lia "código inválido" —
    a mesma frase de quando ele estava errado. A pessoa concluía que o sistema estava quebrado, e
    parava. Uma recusa que mente sobre a causa não protege ninguém; só perde candidato.

    Lido **depois** de `validar`, de propósito: a tentativa recusada já foi contabilizada, e é o
    saldo posterior a ela que a tela precisa anunciar.
    """
    agora = timezone.now()
    desafio = (
        DesafioDeAcesso.objects.filter(email_canonico=email_canonico, finalidade=finalidade)
        .order_by("-criado_em")
        .first()
    )
    if desafio is None or desafio.consumido_em is not None:
        return Estado(motivo=SEM_DESAFIO, tentativas_restantes=0)
    if desafio.tentativas_codigo >= TETO_DE_TENTATIVAS:
        return Estado(motivo=ESGOTADO, tentativas_restantes=0)
    if desafio.expira_em <= agora:
        return Estado(motivo=EXPIRADO, tentativas_restantes=0)
    return Estado(
        motivo=CODIGO_ERRADO,
        tentativas_restantes=TETO_DE_TENTATIVAS - desafio.tentativas_codigo,
    )


def limpar_terminais(*, ate=None) -> int:
    """Desafio terminal não é dado permanente de domínio (FR-033).

    Consumido, expirado ou morto por tentativas: nada disso precisa sobreviver à investigação, que
    lê a trilha de auditoria, não esta tabela.

    **O filtro nomeia o estado, e não a idade.** Apagar tudo o que fosse mais velho que uma hora
    coincidia com o resultado certo apenas porque validade e reconciliação pendente cabem em dez
    minutos — e `VALIDADE_EM_MINUTOS` é constante editável. Crescido qualquer um dos dois prazos, a
    rotina passaria a apagar desafio vivo e a derrubar reconciliação de quem está no meio do fluxo.
    """
    agora = timezone.now()
    limite = ate or agora - JANELA
    terminais = (
        Q(consumido_em__isnull=False)
        | Q(expira_em__lte=agora)
        | Q(tentativas_codigo__gte=TETO_DE_TENTATIVAS)
    )
    # A reconciliação pendente sobrevive mesmo em desafio consumido: é ela que carrega o convite.
    pendente = Q(reconciliacao_ate__isnull=False, reconciliacao_ate__gt=agora)
    return (
        DesafioDeAcesso.objects.filter(terminais)
        .filter(criado_em__lt=limite)
        .exclude(pendente)
        .delete()[0]
    )
