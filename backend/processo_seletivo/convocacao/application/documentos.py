"""Os documentos da convocação: a lista da chamada, a apresentação, a conferência e a leitura (115).

Quatro portas, cada uma com um dono:

- `gravar_lista_da_chamada` é parte do ato de convocar — não tem trilha própria (FR-3572);
- `apresentar` é ato do candidato, pelo portal (FR-3577 a FR-3583);
- `conferir` é ato de quem pode conferir, pelo predicado único (FR-3585 a FR-3589, FR-3595);
- `leitura_da_chamada` e `leituras_por_chamada` respondem o que o portal e a condução mostram.

**A lista pertence à chamada** (D-009): a raiz que ninguém corrigiu. A convocação que a sucede para
corrigir vencimento ou fundamento herda a lista por construção — as linhas apontam a raiz —, e não
por cópia.

**Nada aqui produz desfecho** (D-007, FR-3593). O que a conferência decide é se os desfechos que
incluem podem ser registrados, e essa guarda mora em `desfechar.py`, sob a trava do desfecho.
"""

from dataclasses import dataclass, field

from django.db.models import Max

from processo_seletivo.convocacao.domain import documentos as dominio
from processo_seletivo.convocacao.domain import nomes, prazo
from processo_seletivo.convocacao.models import (
    ApresentacaoDeDocumento,
    ConferenciaDeDocumento,
    Convocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.editais.domain.documentos import (
    NA_CONVOCACAO,
    aplicabilidade,
    modelo_do_requisito,
)
from processo_seletivo.shared.api.problems import DomainError

#: As operações na trilha (FR-3603). A consulta à apresentação é a que a FR-3611 lê.
APRESENTAR = "CONVOCACAO_APRESENTAR"
CONFERIR = "CONVOCACAO_CONFERIR"
CONSULTAR_APRESENTACAO = "CONSULTAR_DOCUMENTO_DA_CONVOCACAO"
CONSULTAR_DOCUMENTOS = "CONSULTAR_DOCUMENTOS_DA_CONVOCACAO"


def nao_encontrado():
    return DomainError("not_found", "Recurso não encontrado.", 404)


# ---------------------------------------------------------------------------
# A chamada
# ---------------------------------------------------------------------------


def raiz_da_chamada(convocacao):
    """A convocação que não corrige outra — a dona da lista (D-009)."""
    atual = convocacao
    while atual.convocacao_anterior_id is not None:
        atual = atual.convocacao_anterior
    return atual


def raizes_das(convocacoes):
    """`{id da convocação: raiz}` para várias, sem subir a cadeia elo a elo pelo banco.

    A condução lê dezenas de linhas, e `raiz_da_chamada` por linha custaria uma consulta por elo
    corrigido. Aqui: nenhuma quando todas são raiz, e uma só quando há sucessora.
    """
    convocacoes = list(convocacoes)
    if all(c.convocacao_anterior_id is None for c in convocacoes):
        return {c.id: c for c in convocacoes}
    todas = {
        c.id: c
        for c in Convocacao.objects.filter(inscricao_id__in={c.inscricao_id for c in convocacoes})
    }
    todas.update({c.id: c for c in convocacoes})

    def subir(atual):
        while atual.convocacao_anterior_id is not None:
            atual = todas[atual.convocacao_anterior_id]
        return atual

    return {c.id: subir(c) for c in convocacoes}


def vigente_da_chamada(raiz):
    """A convocação que ninguém sucedeu, nesta chamada: é dela o vencimento e o desfecho."""
    atual = raiz
    while True:
        seguinte = Convocacao.objects.filter(convocacao_anterior=atual).first()
        if seguinte is None:
            return atual
        atual = seguinte


def em_aberto(vigente):
    """Vigente e sem desfecho — a mesma pergunta que a `029` faz (`FR-373`)."""
    from processo_seletivo.convocacao.application.selectors import desfecho_de

    return desfecho_de(vigente) is None


def prazo_decorrido(vigente, *, agora):
    """**A mesma leitura que admite o não atendimento** (019), e nenhuma outra (FR-3578, FR-3622).

    Sem envio da comunicação o prazo não corre; sem vencimento não há o que decorrer.
    """
    from processo_seletivo.convocacao.application.selectors import envio_de

    return prazo.decorrido(vencimento=vigente.vencimento, enviado_em=envio_de(vigente), agora=agora)


# ---------------------------------------------------------------------------
# A lista, gravada no ato de convocar
# ---------------------------------------------------------------------------


def gravar_lista_da_chamada(convocacao, *, versao):
    """Os itens da lista na raiz de uma chamada, e as referências que ela já nasce tendo (FR-3572).

    **Na mesma transação do ato de convocar**, e sem evento próprio: a lista é parte do ato, como a
    da inscrição é parte do envio (molde da FR-729 da `044`). A sucessora que corrige não grava
    nada.
    """
    if convocacao.convocacao_anterior_id is not None:
        return []
    inscricao = convocacao.inscricao
    vereditos = aplicabilidade(
        versao.content,
        profile_id=str(inscricao.profile_id),
        modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
        momento=NA_CONVOCACAO,
    )
    if not vereditos:
        return []
    itens = ItemDaListaDaConvocacao.objects.bulk_create(
        [
            ItemDaListaDaConvocacao(
                chamada=convocacao,
                inscricao=inscricao,
                versao=versao,
                requisito_id=veredito.requisito["id"],
                chave=veredito.requisito.get("key", ""),
                situacao=veredito.situacao,
                forma_do_recorte=veredito.recorte.forma,
                perfil_id=veredito.recorte.perfil_id,
                modalidade_id=veredito.recorte.modalidade_id,
                modalidade_codigo=veredito.recorte.modalidade_codigo or "",
                aproveita_requisito_id=veredito.requisito.get("reusesRequirementId") or None,
                gravada_em=convocacao.criado_em,
            )
            for veredito in vereditos
        ]
    )
    _aproveitar(itens, convocacao)
    return itens


def faltas_na_lista(convocacao):
    """Os documentos que a versão da chamada pede à pessoa e que a lista gravada não tem (FR-4401).

    **Recalcula pela versão da raiz, e não pela vigente**: a lista é a da chamada (D-009), e uma
    Retificação posterior não muda o que ela pede (FR-3573). Pela mesma regra de aplicabilidade
    que a gravação usa, e só os itens que a pessoa precisaria apresentar — obrigatórios e
    facultativos; o "não se aplica" não pede nada, e a semântica dele não é desta guarda.

    **Lista vazia não é falta** (FR-3574): o Edital sem documento na convocação não pede nada, e a
    convocação anterior à `115` tem versão sem documento nesse momento (FR-3575). Falta é o que a
    versão pede e não está gravado — a convocação que o gesto de titulares registrava sem lista.
    """
    raiz = raiz_da_chamada(convocacao)
    inscricao = raiz.inscricao
    pedidos = [
        veredito
        for veredito in aplicabilidade(
            raiz.versao.content,
            profile_id=str(inscricao.profile_id),
            modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
            momento=NA_CONVOCACAO,
        )
        if veredito.situacao != dominio.NAO_SE_APLICA
    ]
    if not pedidos:
        return []
    gravados = {
        str(requisito)
        for requisito in ItemDaListaDaConvocacao.objects.filter(chamada=raiz).values_list(
            "requisito_id", flat=True
        )
    }
    return [
        veredito.requisito.get("name") or veredito.requisito.get("key") or ""
        for veredito in pedidos
        if str(veredito.requisito["id"]) not in gravados
    ]


def _aproveitar(itens, raiz):
    """As referências com que os itens já nascem, nesta precedência (FR-3619, FR-3576).

    Primeiro o que a chamada anterior da mesma inscrição recebeu e não estava pendente; depois o
    documento da inscrição que o Edital declarou aproveitado. **Sem cópia de arquivo**, e com a
    conferência ficando onde estava: o item nasce *recebido*, e quem confere julga de novo
    (FR-3620).
    """
    from processo_seletivo.inscricoes.models import DocumentoSubmetido

    anterior = (
        Convocacao.objects.filter(
            inscricao_id=raiz.inscricao_id,
            convocacao_anterior__isnull=True,
            criado_em__lt=raiz.criado_em,
        )
        .exclude(pk=raiz.pk)
        .order_by("-criado_em")
        .first()
    )
    do_anterior = {}
    if anterior is not None:
        do_anterior = {
            str(item.requisito_id): item
            for item in ItemDaListaDaConvocacao.objects.filter(chamada=anterior).prefetch_related(
                "apresentacoes", "conferencias"
            )
        }
    for item in itens:
        if item.situacao == ItemDaListaDaConvocacao.Situacao.NAO_SE_APLICA:
            continue
        item_anterior = do_anterior.get(str(item.requisito_id))
        origem = _origem_aproveitavel(item_anterior)
        documento = None
        if origem is None and item.aproveita_requisito_id is not None:
            documento = DocumentoSubmetido.objects.filter(
                inscricao_id=item.inscricao_id, requirement_id=item.aproveita_requisito_id
            ).first()
            # **O arquivo da inscrição que a chamada anterior julgou pendente não volta pela porta
            # da FR-3576**: a anterior não se aproveita por estar pendente (D-013), e cair no
            # documento da inscrição traria de volta exatamente o mesmo arquivo.
            if documento is not None and documento.content_hash in _hashes_pendentes(item_anterior):
                documento = None
        if isinstance(origem, DocumentoSubmetido):
            documento, origem = origem, None
        if origem is None and documento is None:
            continue
        fonte = origem or documento
        ApresentacaoDeDocumento.objects.create(
            item=item,
            numero=1,
            documento_da_inscricao=documento,
            apresentacao_de_origem=origem,
            nome_original=fonte.nome_original,
            tamanho=fonte.tamanho,
            content_hash=fonte.content_hash,
            apresentado_por=f"convocacao:{raiz.id}",
            unidade_de_atuacao=raiz.edital.institution_scope,
            apresentado_em=raiz.criado_em,
        )


def _hashes_pendentes(item_anterior):
    """Os arquivos que a conferência vigente da chamada anterior declarou pendentes."""
    if item_anterior is None:
        return set()
    apresentacoes = sorted(item_anterior.apresentacoes.all(), key=lambda a: a.numero)
    if not apresentacoes:
        return set()
    apresentada = apresentacoes[-1]
    da_apresentada = [
        c for c in item_anterior.conferencias.all() if c.apresentacao_id == apresentada.id
    ]
    if da_apresentada and dominio.vigente(da_apresentada).resultado == nomes.PENDENTE:
        return {apresentada.content_hash}
    return set()


def _origem_aproveitavel(item_anterior):
    """O arquivo de origem do que a chamada anterior recebeu, ou `None` (FR-3619).

    Devolve o `DocumentoSubmetido` ou a apresentação **com arquivo** — nunca uma referência, para
    que a rastreabilidade não vire corrente. Não aproveita o que lá estava *pendente*: seria pedir à
    comissão que julgasse de novo o que ela já disse que não serve (D-013).
    """
    if item_anterior is None or _hashes_pendentes(item_anterior):
        return None
    apresentacoes = sorted(item_anterior.apresentacoes.all(), key=lambda a: a.numero)
    if not apresentacoes:
        return None
    apresentada = apresentacoes[-1]
    if apresentada.arquivo:
        return apresentada
    if apresentada.documento_da_inscricao_id is not None:
        return apresentada.documento_da_inscricao
    return apresentada.apresentacao_de_origem


# ---------------------------------------------------------------------------
# A leitura
# ---------------------------------------------------------------------------


@dataclass
class ItemLido:
    item: object
    requisito: dict
    estado: str
    apresentacoes: list
    conferencias: list
    modelo: dict | None = None

    @property
    def nome(self):
        return self.requisito.get("name") or self.item.chave

    @property
    def instrucao(self):
        return self.requisito.get("instructions") or ""

    @property
    def obrigatorio(self):
        return self.item.situacao == dominio.OBRIGATORIO

    @property
    def vigente(self):
        return dominio.vigente(self.apresentacoes)

    @property
    def conferencia(self):
        return dominio.vigente(self.conferencias)

    @property
    def aproveitada(self):
        """A referência vigente, dita para gente: de onde veio o arquivo, e quando chegou."""
        vigente = self.vigente
        if vigente is None or vigente.arquivo:
            return None
        if vigente.documento_da_inscricao_id is not None:
            return {"de": "inscricao", "em": vigente.documento_da_inscricao.uploaded_at}
        origem = vigente.apresentacao_de_origem
        return {"de": "chamada", "em": origem.apresentado_em, "origem": origem}

    @property
    def exigencia_mudou(self):
        """A versão da exigência mudou desde a apresentação de origem (FR-3621)."""
        aproveitada = self.aproveitada
        if not aproveitada or aproveitada["de"] != "chamada":
            return False
        return aproveitada["origem"].item.versao_id != self.item.versao_id


@dataclass
class LeituraDocumental:
    itens: list = field(default_factory=list)
    estado: str = nomes.DOCUMENTOS_SEM_EXIGENCIA

    @property
    def pedidos(self):
        return [lido for lido in self.itens if lido.item.situacao != dominio.NAO_SE_APLICA]

    @property
    def pendencias_para_incluir(self):
        return [
            lido for lido in self.pedidos if dominio.impede_incluir(lido.item.situacao, lido.estado)
        ]

    @property
    def facultativos_sem_conferencia(self):
        return [
            lido
            for lido in self.pedidos
            if dominio.adverte_sem_impedir(lido.item.situacao, lido.estado)
        ]

    def contar(self, estado):
        return sum(1 for lido in self.pedidos if lido.estado == estado)

    @property
    def contagens(self):
        return {
            "recebidos": self.contar(nomes.ITEM_RECEBIDO),
            "complementados": self.contar(nomes.ITEM_COMPLEMENTADO),
            "pendentes": self.contar(nomes.ITEM_PENDENTE),
            "conformes": self.contar(nomes.ITEM_CONFORME) + self.contar(nomes.ITEM_NAO_SE_APLICA),
            "a_apresentar": self.contar(nomes.ITEM_A_APRESENTAR),
            "obrigatorios": sum(1 for lido in self.pedidos if lido.obrigatorio),
            "total": len(self.pedidos),
        }

    def fundamento_do_indeferimento(self):
        pendentes = [
            (lido.nome, getattr(lido.conferencia, "motivo", "") or "")
            for lido in self.pendencias_para_incluir
        ]
        return dominio.fundamento_das_pendencias(pendentes)


def leituras_por_chamada(raizes, *, decididas=frozenset()):
    """A leitura de várias chamadas em consultas de número fixo — a condução não consulta por linha.

    `decididas` são os ids das raízes cuja convocação vigente tem desfecho.

    **A versão por `prefetch`, e não por junção**: as dezenas de chamadas de um recorte citam a
    mesma versão, e a junção trazia o conteúdo inteiro do Edital — o maior campo do sistema — uma
    vez por item (revisão do #369). O `prefetch` o traz uma vez por versão.
    """
    raizes = list(raizes)
    if not raizes:
        return {}
    itens = list(
        ItemDaListaDaConvocacao.objects.filter(chamada__in=raizes)
        .prefetch_related(
            "versao",
            "apresentacoes__documento_da_inscricao",
            "apresentacoes__apresentacao_de_origem__item",
            "conferencias",
        )
        .order_by("gravada_em", "id")
    )
    por_chamada = {raiz.id: [] for raiz in raizes}
    requisitos_da_versao = {}
    for item in itens:
        if item.versao_id not in requisitos_da_versao:
            requisitos_da_versao[item.versao_id] = {
                str(r.get("id")): r for r in (item.versao.content.get("documentRequirements") or [])
            }
        requisitos = requisitos_da_versao[item.versao_id]
        requisito = requisitos.get(str(item.requisito_id)) or {"id": str(item.requisito_id)}
        apresentacoes = sorted(item.apresentacoes.all(), key=lambda a: a.numero)
        conferencias = sorted(item.conferencias.all(), key=lambda c: (c.conferido_em, str(c.id)))
        # A versão julgada de cada conferência já está nas apresentações lidas: a página dos
        # documentos diz "versão N" em cada uma, e sem isto pagava uma consulta por conferência.
        por_id = {apresentacao.id: apresentacao for apresentacao in apresentacoes}
        for conferencia in conferencias:
            if conferencia.apresentacao_id in por_id:
                conferencia.apresentacao = por_id[conferencia.apresentacao_id]
        por_chamada[item.chamada_id].append(
            ItemLido(
                item=item,
                requisito=requisito,
                estado=dominio.estado_do_item(apresentacoes, conferencias),
                apresentacoes=apresentacoes,
                conferencias=conferencias,
                modelo=modelo_do_requisito(item.versao.content, requisito),
            )
        )
    leituras = {}
    for raiz in raizes:
        lidos = sorted(por_chamada[raiz.id], key=lambda lido: lido.requisito.get("order", 0))
        estado = dominio.estado_da_convocacao(
            [(lido.item, lido.estado) for lido in lidos], decidida=raiz.id in decididas
        )
        leituras[raiz.id] = LeituraDocumental(itens=lidos, estado=estado)
    return leituras


def leitura_da_chamada(convocacao, *, decidida=False):
    raiz = raiz_da_chamada(convocacao)
    decididas = {raiz.id} if decidida else frozenset()
    return leituras_por_chamada([raiz], decididas=decididas)[raiz.id]


def fonte_do_arquivo(apresentacao):
    """Quem guarda o arquivo desta apresentação: ela mesma, o documento da inscrição ou a origem.

    Um passo só, porque a referência nunca aponta outra referência (FR-3619). Os três têm `arquivo`,
    `nome_original` e `content_hash`, que é o que a entrega e a reconferência leem.
    """
    if apresentacao.arquivo:
        return apresentacao
    if apresentacao.documento_da_inscricao_id is not None:
        return apresentacao.documento_da_inscricao
    return apresentacao.apresentacao_de_origem


def item_da_chamada(item_id, *, inscricao_id=None):
    filtros = {"pk": item_id}
    if inscricao_id is not None:
        filtros["inscricao_id"] = inscricao_id
    return (
        ItemDaListaDaConvocacao.objects.select_related("chamada", "inscricao", "versao")
        .filter(**filtros)
        .first()
    )


# ---------------------------------------------------------------------------
# A apresentação, pelo portal
# ---------------------------------------------------------------------------


@dataclass
class Apresentada:
    apresentacao: object
    ja_recebido: bool = False


def apresentar(*, identidade, inscricao_id, item_id, arquivo, nome_original, correlation_id):
    """O titular apresenta um arquivo para um item da lista (FR-3577 a FR-3583).

    **Trava a inscrição, e não o que é append-only** (`tests/guardiao_de_travas.py`): é a linha que
    serializa dois envios do mesmo item, e a conferência e o desfecho travam a mesma linha.
    """
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.convocacao.application.selectors import visivel_ao_candidato
    from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato
    from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.inscricoes.storage import ArmazenamentoPrivado
    from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
    from processo_seletivo.shared.application.commands import command_context
    from processo_seletivo.shared.arquivos import aceitar, resumo

    with command_context() as agora:
        inscricao = (
            Inscricao.objects.select_for_update()
            .select_related("edital")
            .filter(pk=inscricao_id)
            .first()
        )
        if inscricao is None:
            raise nao_encontrado()
        exigir_titularidade(inscricao, identidade)
        item = item_da_chamada(item_id, inscricao_id=inscricao.id)
        if item is None or item.situacao == ItemDaListaDaConvocacao.Situacao.NAO_SE_APLICA:
            raise nao_encontrado()
        vigente = vigente_da_chamada(item.chamada)
        # **A convocação que ninguém publicou não existe para o candidato** (125, FR-3985), e a
        # recusa é a do item inexistente, antes de qualquer outra: uma recusa própria, ou a do
        # Processo encerrado, diria que a convocação existe. A tela já não oferece o envio; esta é a
        # regra no comando, para o formulário velho e para o endereço digitado.
        if not visivel_ao_candidato(vigente):
            raise nao_encontrado()
        # **O mesmo estado do Processo que a conferência e o desfecho exigem**: receber o que
        # ninguém mais pode conferir diria "a comissão vai conferir" de algo que não será.
        ensure_processo_accepts_changes(inscricao.edital.processo)
        julgado = dominio.estado_do_item(
            list(item.apresentacoes.order_by("numero")),
            list(item.conferencias.order_by("conferido_em", "id")),
        )
        if julgado in dominio.ATENDIDOS:
            # A regra é do comando, e não só da tela (Princípio IV): um formulário velho reenviado
            # desfaria em silêncio a conferência que deixou a convocação pronta para decidir.
            raise DomainError(
                nomes.DOCUMENTO_JA_CONFERIDO,
                "Este documento já foi conferido pela comissão, e não recebe outro arquivo.",
                409,
            )
        if not em_aberto(vigente):
            raise DomainError(
                nomes.CHAMADA_FECHADA,
                "Esta convocação já tem resultado registrado, e não recebe mais documentos.",
                409,
            )
        if prazo_decorrido(vigente, agora=agora):
            raise DomainError(
                nomes.PRAZO_DA_CONVOCACAO_DECORRIDO,
                frase_do_prazo_decorrido(vigente),
                409,
            )
        limite = _limite()
        aceitar(arquivo, nome_original=nome_original, limite_em_bytes=limite)
        calculado = resumo(arquivo)
        anterior = item.apresentacoes.order_by("-numero").first()
        if anterior is not None and anterior.content_hash == calculado:
            # O mesmo arquivo de novo — o duplo clique, ou a requisição repetida (FR-3581). Não é
            # versão nova: é o que já foi recebido.
            return Apresentada(anterior, ja_recebido=True)
        numero = (item.apresentacoes.aggregate(maior=Max("numero"))["maior"] or 0) + 1
        apresentacao = ApresentacaoDeDocumento(
            item=item,
            numero=numero,
            nome_original=(nome_original or "documento.pdf")[:255],
            tamanho=getattr(arquivo, "size", 0) or 0,
            content_hash=calculado,
            apresentado_por=identidade.subject,
            unidade_de_atuacao=inscricao.edital.institution_scope,
            apresentado_em=agora,
        )
        apresentacao.arquivo.save("documento.pdf", arquivo, save=False)
        caminho_novo = apresentacao.arquivo.name
        try:
            apresentacao.save()
            record_event(
                actor=ator_do_candidato(identidade, inscricao.edital),
                permission="",
                operation=APRESENTAR,
                aggregate=apresentacao,
                now=agora,
                correlation_id=correlation_id,
                # O requisito e a chamada, e **não** o nome do arquivo, que carrega dado pessoal com
                # frequência (FR-3603, como o `ANEXAR` da inscrição).
                reason=f"Apresentação {numero} do requisito {item.requisito_id} na chamada "
                f"{item.chamada_id}.",
                new_state="",
                new_revision=None,
            )
        except Exception:
            ArmazenamentoPrivado().delete(caminho_novo)
            raise
        return Apresentada(apresentacao)


def _limite():
    from django.conf import settings

    return settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES


#: **Nega a consequência automática, e não a prevê** (FR-3748 da `118`; FR-1177 da `063`).
#: *"A comissão vai decidir"* prometia uma decisão que o fim do prazo não produz, e dizia ao
#: convocado que ele não tinha mais nada a fazer; o núcleo diz quem registra o resultado e que o
#: fim do prazo, sozinho, não decide nada.
NUCLEO_DO_PRAZO_DECORRIDO = (
    "O fim do prazo não decide nada sozinho: quem registra o resultado é a comissão."
)


def frase_do_prazo_decorrido(vigente):
    """O núcleo único do prazo vencido, para documentos e requerimento (FR-3622; FR-3748 da `118`).

    **As recusas dizem só o núcleo**, e as telas o completam com o que não se envia mais e com o
    canal de atendimento. A hora é `HHhMM`, o formato único do prazo em toda tela do candidato.
    Sem vencimento o prazo não decorre (`019`), e a recaída existe só para a frase ter sujeito.
    """
    quando = vigente.vencimento
    if quando is None:
        return f"O prazo desta convocação terminou. {NUCLEO_DO_PRAZO_DECORRIDO}"
    from zoneinfo import ZoneInfo

    from django.conf import settings

    from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar

    # Pela função única do prazo (121, FR-3873): a recusa e as telas dizem a data como o cartão do
    # prazo e o e-mail a dizem, no fuso das settings.
    prazo = apresentar(quando, quando, ZoneInfo(settings.TIME_ZONE))
    return f"O prazo terminou em {prazo.data_e_hora}. {NUCLEO_DO_PRAZO_DECORRIDO}"


# ---------------------------------------------------------------------------
# A conferência, pela gestão
# ---------------------------------------------------------------------------


def conferir(
    *,
    actor,
    item_id,
    apresentacao_id,
    resultado,
    motivo="",
    motivo_da_substituicao="",
    idempotency_key,
    correlation_id,
):
    """Registra o juízo de quem confere sobre um item (FR-3585 a FR-3589, FR-3611).

    **Trava o Processo e depois a inscrição**, na ordem dos comandos da comissão: o desfecho trava o
    Processo, e a apresentação trava a inscrição — a conferência fica serializada com os dois.
    """
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.auditoria.models import RegistroAuditoria
    from processo_seletivo.comissoes.domain.autorizacao import pode_conferir_documentos
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
    from processo_seletivo.processos.models import ProcessoSeletivo
    from processo_seletivo.shared.application.commands import command_context
    from processo_seletivo.shared.idempotency import finish, reserve

    resultado = (resultado or "").strip()
    if resultado not in nomes.RESULTADOS_DA_CONFERENCIA:
        raise DomainError(
            nomes.RESULTADO_DA_CONFERENCIA_INVALIDO,
            "A conferência é conforme, pendente ou não se aplica, e nada mais.",
            422,
            campo="resultado",
        )
    motivo = (motivo or "").strip()
    motivo_da_substituicao = (motivo_da_substituicao or "").strip()
    with command_context() as agora:
        item = item_da_chamada(item_id)
        if item is None or actor is None:
            raise nao_encontrado()
        edital = item.chamada.edital
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=edital.processo_id, institution_scope=actor.institution_scope)
            .first()
        )
        if processo is None:
            raise nao_encontrado()
        base = pode_conferir_documentos(actor, edital, item.chamada.perfil_id)
        if base is None:
            raise nao_encontrado()
        ensure_processo_accepts_changes(processo)
        Inscricao.objects.select_for_update().filter(pk=item.inscricao_id).first()
        reserva = reserve(
            actor=actor,
            operation=CONFERIR,
            key=idempotency_key,
            payload={
                "item": str(item.id),
                "apresentacao": str(apresentacao_id or ""),
                "resultado": resultado,
            },
        )
        if reserva.response_status is not None:
            return ConferenciaDeDocumento.objects.get(pk=reserva.result_id)
        vigente = vigente_da_chamada(item.chamada)
        if not em_aberto(vigente):
            raise DomainError(
                nomes.CHAMADA_FECHADA,
                "Esta convocação já tem desfecho: a conferência dela está encerrada.",
                409,
            )
        apresentacoes = list(item.apresentacoes.order_by("numero"))
        atual = apresentacoes[-1] if apresentacoes else None
        # **Sem versão indicada, a julgada é a vigente**: uma pendência sem apresentação, sobre um
        # item que tem arquivo, faria o estado derivado ler "complementado" sem que nada tivesse
        # chegado depois dela.
        julgada = atual
        if apresentacao_id:
            julgada = next((a for a in apresentacoes if str(a.id) == str(apresentacao_id)), None)
            if julgada is None:
                raise nao_encontrado()
            if atual is not None and julgada.id != atual.id:
                raise DomainError(
                    nomes.VERSAO_SUPERADA,
                    "Chegou uma versão mais nova deste documento enquanto você conferia. Abra a "
                    "versão atual antes de registrar a conferência.",
                    409,
                )
        if resultado == nomes.CONFORME:
            if julgada is None:
                raise DomainError(
                    nomes.CONFORME_SEM_APRESENTACAO,
                    "Só se confere como conforme o documento que foi apresentado.",
                    422,
                )
            aberta = RegistroAuditoria.objects.filter(
                operation=CONSULTAR_APRESENTACAO,
                aggregate_id=julgada.id,
                actor_subject=actor.subject,
            ).exists()
            if not aberta:
                raise DomainError(
                    nomes.CONFORME_SEM_ABERTURA,
                    "Abra o documento antes de conferi-lo como conforme.",
                    409,
                )
        elif not motivo:
            raise DomainError(
                nomes.MOTIVO_DA_CONFERENCIA_OBRIGATORIO,
                "Diga o motivo: ele aparece para a pessoa convocada.",
                422,
                campo="motivo",
            )
        anterior = item.conferencias.order_by("-conferido_em", "-id").first()
        if (
            anterior is not None
            and julgada is not None
            and anterior.apresentacao_id == julgada.id
            and not motivo_da_substituicao
        ):
            raise DomainError(
                nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO,
                "Este documento já foi conferido. Para mudar a conferência, diga por quê.",
                422,
                campo="motivo_da_substituicao",
            )
        conferencia = ConferenciaDeDocumento.objects.create(
            item=item,
            apresentacao=julgada,
            hash_conferido=julgada.content_hash if julgada is not None else "",
            resultado=resultado,
            motivo=motivo,
            conferencia_anterior=anterior,
            motivo_da_substituicao=motivo_da_substituicao if anterior is not None else "",
            conferido_por=actor.subject,
            unidade_de_atuacao=actor.institution_scope,
            conferido_em=agora,
        )
        record_event(
            actor=actor,
            permission=base.permissao,
            operation=CONFERIR,
            aggregate=conferencia,
            now=agora,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            reason=f"Conferência {resultado} do requisito {item.requisito_id} na chamada "
            f"{item.chamada_id}.",
            new_state=resultado,
            new_revision=None,
        )
        finish(reserva, conferencia, 201)
        return conferencia
