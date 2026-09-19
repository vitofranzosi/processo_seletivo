"""O ato de instrução, e o alcance que ele abre — que nasce dele e morre com a decisão.

**Por que é um ato, e não uma permissão.** A `FR-105` da `018` proíbe que as superfícies do recurso
ampliem o acesso a documentos do candidato, e dar ao papel de julgar o que ele precisa ver seria
exatamente isso. O caminho que resta é o inverso: alguém com autoridade decide anexar **aquela**
prova **àquele** recurso, e o ato fica registrado. A regra continua de pé, e a prova chega
(036, FR-527, FR-530).

**A autorização é a base composta que a `033` já sabe exigir** — a permissão de gerir a comissão
**ou** a presidência deste Processo, cada uma suficiente sozinha. Nenhuma capacidade nova entra no
sistema por esta feature, e é a `FR-530` que o exige por escrito.

**O impedimento não é conferido aqui, e a ausência é decisão.** `impedimento` responde *"esta pessoa
pode julgar esta peça?"*, e quem instrui é tipicamente quem está impedido de julgar — a presidência
da comissão que avaliou. Exigir elegibilidade neste ato pediria à autoridade competente uma condição
que o desenho institucional lhe nega, e nenhuma instrução aconteceria. Instruir não é julgar.

**O alcance é derivado, e nunca persistido** (FR-528, FR-530). Não há tabela de "quem pode ver":
quem alcança é quem julga **aquele** recurso, enquanto ele não estiver decidido. Guardar uma lista
de pessoas seria uma permissão com outro nome — e, derivado, o par (recurso, prova) morre com a
decisão sem que ninguém precise lembrar de fechá-lo, porque não há nada aberto a fechar.

**A trilha registra espécie e escopo, nunca conteúdo** (FR-533, FR-534). É a regra que a `018` já
pratica em `test_a_trilha_registra_o_ato_e_nao_o_conteudo`, e acrescentar registros é exatamente
como ela se quebra: copiar o parecer para o motivo criaria uma segunda cópia do dado sensível, num
lugar com outro regime de acesso e outro tempo de retenção.
"""

from dataclasses import dataclass

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.domain.autorizacao import (
    BASES_DA_GESTAO_DA_COMISSAO,
    pode_gerir_comissao,
)
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.recursos.application.porta import travar
from processo_seletivo.recursos.models import AtoDeInstrucao
from processo_seletivo.seguranca.application.authorization import require_authorization_base
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish_batch, reserve

OPERACAO = "RECURSO_INSTRUIR"
# A leitura exercida sobre o que foi instruído. Nome no mesmo formato do resto do mapa de operações
# — `APP_ATO`, em maiúsculas —, e com rótulo em `interface/views.py::OPERACOES`: sem o rótulo, a
# trilha exibiria o código cru a quem pergunta quem leu o quê (FR-534).
OPERACAO_DE_ACESSO = "RECURSO_INSTRUCAO_ACESSAR"

NADA_A_INSTRUIR = (
    "Escolha o que anexar a este recurso: o parecer atacado, o documento citado, ou os dois."
)
SEM_PARECER_A_INSTRUIR = (
    "Este recurso não ataca Resultado individual, e por isso não há parecer a instruir. Recurso "
    "contra a publicação não contesta a avaliação de ninguém."
)
PARECER_INEXISTENTE = (
    "A avaliação que fundamenta o resultado atacado não registrou parecer, e não se instrui o que "
    "não existe. A obrigatoriedade do parecer depende do caráter da Etapa e da forma da avaliação."
)
NAO_ENCONTRADO = "Recurso não encontrado."
JA_DECIDIDO = (
    "Este recurso já foi decidido. Instruir agora abriria um alcance que a decisão encerrou, e o "
    "que a decisão encerra não se reabre."
)
ALCANCE_ENCERRADO = (
    "O alcance da instrução terminou com a decisão deste recurso. O registro de que ela houve "
    "permanece — nada foi apagado; o que se encerrou foi o acesso."
)


# --- O alcance, derivado ------------------------------------------------------------------------


@dataclass(frozen=True)
class Alcance:
    """O que a instrução alcança **nesta peça, agora** — os três estados da `FR-532`.

    São **três**, e não dois, e o terceiro é o que a primeira redação da spec não tinha: sem ele a
    tela diria *"nada foi instruído"* a quem viu a prova ontem, e isso é falso sobre um ato que
    aconteceu. O código que produz o primeiro estado é o mesmo que produziria o terceiro por
    omissão, e é por isso que `houve` e `aberto` são campos distintos em vez de uma ausência que a
    tela interpreta.
    """

    houve: bool
    aberto: bool
    atos: tuple = ()

    @property
    def encerrado(self):
        """Houve instrução e o alcance terminou com a decisão — o terceiro estado."""
        return self.houve and not self.aberto

    @property
    def pareceres(self):
        return tuple(ato for ato in self.atos if ato.especie == AtoDeInstrucao.Especie.PARECER)

    @property
    def documentos(self):
        return tuple(ato for ato in self.atos if ato.especie == AtoDeInstrucao.Especie.DOCUMENTO)


def decidido(peca):
    """Se a peça já foi julgada — lido do `prefetch` que a porta faz, e não de coluna.

    `Recurso` não tem coluna de situação, e é decisão da `018`: o que aconteceu com uma peça é a
    existência dos atos que a alcançaram. Aqui isso é vantagem — o fim do alcance não depende de
    ninguém lembrar de virar uma chave.
    """
    return bool(peca.decisoes.all())


def alcance_da_instrucao(peca, *, atos=None):
    """O alcance derivado do par (aquela peça, quem a julga) — **nunca** de uma lista de pessoas.

    `atos` é a lista já lida, quando quem chama a tem: a tela da peça a lê uma vez e a passa
    adiante, para não pagar a mesma consulta duas vezes.

    **Não recebe ator, e a ausência é o ponto.** Quem chega até aqui já atravessou a porta da peça,
    que exige `recurso:julgar` e o escopo institucional. O alcance não pergunta *quem é você* —
    pergunta *qual recurso é este*, e é isso que o separa de uma permissão: instruir uma peça não
    diz nada sobre nenhuma outra, ainda que da mesma Etapa, do mesmo Edital ou do mesmo candidato
    (FR-528).
    """
    lidos = tuple(peca.instrucoes.select_related("documento").all() if atos is None else atos)
    return Alcance(houve=bool(lidos), aberto=bool(lidos) and not decidido(peca), atos=lidos)


def ato_alcancado(peca, *, documento_id):
    """O ato que autoriza **este** documento **nesta** peça, ou a recusa — `FR-528` e `FR-529`.

    Duas recusas, e elas dizem coisas diferentes de propósito:

    - **documento que esta peça não instruiu é 404**, indistinguível de documento inexistente. É a
      mesma doutrina que protege o escopo institucional: quem não foi alcançado não deve sequer
      saber que aquele anexo existe em outro recurso;
    - **peça decidida é 403 e nomeia a razão.** Aqui o ator sabe que o ato houve — a tela acabou de
      dizer —, e responder "não encontrado" faria a tela mentir sobre por que o caminho não abre. O
      que terminou foi o alcance; o registro permanece.
    """
    ato = (
        peca.instrucoes.filter(especie=AtoDeInstrucao.Especie.DOCUMENTO, documento_id=documento_id)
        .select_related("documento", "documento__inscricao")
        .first()
    )
    if ato is None:
        raise DomainError("not_found", NAO_ENCONTRADO, 404)
    if decidido(peca):
        raise DomainError("instruction_reach_closed", ALCANCE_ENCERRADO, 403)
    return ato


# --- O ato -------------------------------------------------------------------------------------


def instruir(
    *,
    actor,
    recurso_id,
    parecer=False,
    documento_ids=(),
    razao="",
    idempotency_key,
    correlation_id="",
):
    """Anexa a **este** recurso o parecer atacado e os documentos citados, e registra o ato.

    Devolve a lista de atos gravados — uma linha por item anexado. **Instruir de novo acrescenta**:
    não há unicidade por recurso, e não há nada a sobrescrever.

    Uma chamada é **um** ato da autoridade, e todas as suas linhas compartilham autor e instante. A
    trilha recebe um registro por linha, porque é a linha que nomeia o que foi alcançado — e é
    *"quem viu o quê"* que a `FR-534` precisa poder responder depois.
    """
    pedidos = [str(item) for item in documento_ids if item]
    if not parecer and not pedidos:
        raise DomainError("nothing_to_instruct", NADA_A_INSTRUIR, 422)

    with command_context() as agora:
        peca = travar(actor, recurso_id)
        base = pode_gerir_comissao(actor, peca.inscricao.edital.processo)
        # A base composta, e a recusa que nomeia o que teria bastado — a formulação única da `033`.
        require_authorization_base(base is not None, bases=BASES_DA_GESTAO_DA_COMISSAO)
        if decidido(peca):
            # **A porta fechada não se reabre pela frente.** Instruir depois de decidido gravaria um
            # ato cujo alcance nasce encerrado — nem registro útil nem acesso concedido —, e
            # sugeriria a quem praticou que alguma coisa foi aberta (FR-529).
            raise DomainError("appeal_already_decided", JA_DECIDIDO, 409)

        reserva = reserve(
            actor=actor,
            operation=f"{OPERACAO}:{peca.pk}",
            key=idempotency_key,
            payload={"parecer": bool(parecer), "documentos": sorted(pedidos), "razao": razao},
        )
        if reserva.result_payload:
            # **A repetição devolve os atos daquele ato, e não uma lista vazia.** Um ato que grava
            # mais de uma linha não tem "o objeto criado", e por isso a reserva guarda o desfecho —
            # a mesma escolha que a `012` fez para a distribuição em lote.
            return list(peca.instrucoes.filter(pk__in=reserva.result_payload))

        atos = []
        if parecer:
            _exigir_parecer_instruivel(peca)
            atos.append(
                AtoDeInstrucao.objects.create(
                    recurso=peca,
                    especie=AtoDeInstrucao.Especie.PARECER,
                    razao=(razao or "").strip(),
                    instruido_por=actor.subject,
                    instruido_em=agora,
                )
            )
        for documento in _documentos_da_peca(peca, pedidos):
            atos.append(
                AtoDeInstrucao.objects.create(
                    recurso=peca,
                    especie=AtoDeInstrucao.Especie.DOCUMENTO,
                    documento=documento,
                    razao=(razao or "").strip(),
                    instruido_por=actor.subject,
                    instruido_em=agora,
                )
            )
        for ato in atos:
            auditar(
                actor=actor,
                permissao=base.permissao,
                operation=OPERACAO,
                aggregate=ato,
                now=agora,
                correlation_id=correlation_id,
                # **Espécie e escopo, nunca conteúdo** (FR-533). O texto do parecer, o conteúdo do
                # documento e a fundamentação de quem recorreu ficam fora: eles vivem nos agregados
                # deles, sob o regime de acesso deles, e copiá-los para cá criaria uma segunda cópia
                # do dado sensível num lugar com outro tempo de retenção.
                reason=motivo_do_ato(peca, ato),
                idempotency_key=idempotency_key,
            )
        finish_batch(reserva, 201, [str(ato.pk) for ato in atos])
        return atos


def motivo_do_ato(peca, ato):
    """A frase da trilha: qual peça, qual espécie — e **qual requisito**, quando é documento.

    O requisito basta para saber o que foi alcançado, e é a mesma escolha que a `009` fez ao
    registrar consulta a documento: *"registra a leitura, e não o conteúdo — nem o nome do arquivo,
    que é do candidato"*.
    """
    if ato.especie == AtoDeInstrucao.Especie.PARECER:
        return f"Recurso {peca.protocolo} instruído com o parecer atacado."
    return (
        f"Recurso {peca.protocolo} instruído com o documento do requisito "
        f"{ato.documento.requirement_id}."
    )


def motivo_do_acesso(peca, ato):
    """A frase da trilha do **acesso exercido** (FR-534), na forma que o produto já pratica.

    Saber que a prova foi anexada não responde quem a viu, e é por isso que há dois registros e não
    um. A forma segue os dois precedentes que o repositório já tem — a prévia da exportação da `031`
    e a consulta a documento da `009` —: revisão nula, porque nada mudou de estado, e uma razão que
    descreve o **escopo** do que foi visto.
    """
    if ato.especie == AtoDeInstrucao.Especie.PARECER:
        return f"Acesso ao parecer instruído no recurso {peca.protocolo}."
    return (
        f"Acesso ao documento do requisito {ato.documento.requirement_id}, instruído no recurso "
        f"{peca.protocolo}."
    )


def _exigir_parecer_instruivel(peca):
    """Não se instrui o que não existe, e as duas ausências são diferentes (casos de borda da spec).

    **Recurso contra a publicação não ataca resultado individual nenhum**, e ali não há parecer a
    instruir. **Resultado desfavorável sem parecer também existe** — a obrigatoriedade depende do
    caráter da Etapa e da forma da avaliação. Recusar as duas com a mesma frase mandaria quem
    recebeu a recusa procurar a causa errada.
    """
    resultado = peca.resultado_atacado
    if resultado is None:
        raise DomainError("no_opinion_to_instruct", SEM_PARECER_A_INSTRUIR, 422)
    avaliacao = resultado.avaliacao
    if avaliacao is None or not (avaliacao.parecer or "").strip():
        raise DomainError("no_opinion_to_instruct", PARECER_INEXISTENTE, 422)


def _documentos_da_peca(peca, pedidos):
    """Os documentos pedidos, **conferidos contra a Inscrição da peça** — e na ordem do pedido.

    A conferência é aqui e é também trigger: instruir um recurso com o documento de **outra** pessoa
    seria, num só passo, o vazamento que a `FR-535` proíbe e a ampliação que a `FR-105` da `018`
    proíbe. A resposta é a uniforme de recurso não encontrado, e não uma que confirme que aquele
    documento existe em algum lugar (FR-536).
    """
    encontrados = {
        str(documento.pk): documento
        for documento in DocumentoSubmetido.objects.filter(
            pk__in=pedidos, inscricao_id=peca.inscricao_id
        )
    }
    if len(encontrados) != len(set(pedidos)):
        raise DomainError("not_found", NAO_ENCONTRADO, 404)
    return [encontrados[item] for item in pedidos]
