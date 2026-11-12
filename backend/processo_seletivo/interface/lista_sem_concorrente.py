"""A lista em que ninguém concorre, levada num gesto à ordem vazia e ao corte vazio (155, US5).

**Um gesto, e os dois registros de hoje** (155, D-010, FR-6328). A lista reservada sem ninguém pedia
três confirmações sem efeito — ordem, corte e publicação —, cada uma numa tela. O gesto não inventa
ato: chama `emitir_ordem` e, se o marco corta, `emitir_corte`, os mesmos comandos com as mesmas
recusas, numa transação só. A publicação sai junto da do marco (`divulgacao.publicar`, FR-6330).

**Nenhuma linha de candidato** (FR-6329). O gesto só existe onde a proposta da ordem é vazia — com
posição ou sem —, e a faixa de uma ordem vazia não alcança ninguém. As duas condições são conferidas
de novo sob a trava, antes de cada comando: uma inscrição que passasse a concorrer entre a
conferência e o clique faria o gesto gravar a ordem de alguém sem que ninguém a tivesse lido.

**Por que mora na interface** (R-006, o molde de `conducao_do_marco.py`): o gesto compõe dois
comandos da classificação e dá a eles uma conferência só; não decide nada de domínio. A trava, a
autorização e a reserva da chave são as de `comando_de_comissao`, e as chaves dos dois comandos são
derivadas da do gesto — a repetição do envio devolve o desfecho da primeira vez.

**Nenhum `Http404` nasce aqui**: o recorte que não é identidade e o marco fora do Perfil recusam
pelas funções de `views.py` que o inventário da `033` já classifica.
"""

from uuid import uuid4

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import (
    calcular_corte,
    geracao_vigente,
    regra_do_marco,
)
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.interface import identidade
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.shared.http import marcar_como_privada

EVENTO = "CLASSIFICACAO_LISTA_SEM_CONCORRENTE"
ATO = "classificacao:lista_sem_concorrente"

LISTA_COM_CONCORRENTE = "lista_com_concorrente"
LISTA_JA_REGISTRADA = "lista_ja_registrada"
LEITURA_MUDOU = "leitura_da_lista_mudou"
SO_LISTA_RESERVADA = "lista_sem_concorrente_so_na_reserva"

#: O que a conferência acrescenta à frase do ato da `135` (FR-4672, na redação que a `155` lhe
#: deu; FR-6330): a lista não pede publicação própria. A frase do ato vem do andamento, que a diz
#: na providência — uma redação só para as duas telas.
FRASE_DA_PUBLICACAO = (
    "A lista entra na publicação do resultado do marco junto das outras listas, dita como "
    "«ninguém concorreu», sem publicação própria."
)


# --- A conferência -----------------------------------------------------------------------------


def conferencia(*, edital, perfil_id, marco_id, lista_id, at=None):
    """O que o gesto registraria agora, e a recusa que daria — **sem gravar nada** (FR-6331).

    `{"recusa": (codigo, frase) | None, "ordem": bool, "corte": bool, "temCorte": bool,
    "ordemVigente", "assinatura"}`. `ordem` e `corte` dizem o que **falta** registrar: a lista que
    já tem a ordem vazia, emitida antes da `155`, recebe só o corte, e nada é emitido duas vezes.
    """
    estado = estado_do_marco(edital=edital, marco_id=marco_id, at=at, lista_id=lista_id)
    vigente = estado["vigente"]
    proposta = estado["proposta"]
    conteudo = effective_version(edital_id=edital.id, at=at).content
    tem_corte = regra_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id) is not None
    geracao = (
        geracao_vigente(edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id)
        if tem_corte
        else []
    )
    base = {
        "ordemVigente": vigente,
        "temCorte": tem_corte,
        "ordem": vigente is None,
        "corte": tem_corte and not geracao,
        "recusa": _recusa(estado, lista_id=lista_id, vigente=vigente, tem_corte=tem_corte),
    }
    if base["recusa"] is None and not base["ordem"] and not base["corte"]:
        base["recusa"] = (
            LISTA_JA_REGISTRADA,
            "Esta lista já tem a ordem vazia"
            + (" e o corte vazio" if tem_corte else "")
            + ": não há o que registrar.",
        )
    # **A assinatura cobre o que o gesto lê** (o molde da FR-495 da `034`): a proposta da ordem com
    # o vigente daquela leitura, e a geração do corte. Um autodeclarado que passe a concorrer, ou
    # uma emissão feita por outra pessoa, entre a conferência e o clique, é leitura nova.
    base["assinatura"] = canonical_sha256(
        {
            "gesto": "lista_sem_concorrente",
            "recorte": str(lista_id) if lista_id else None,
            "ordem": assinatura_da_proposta(proposta, ato_vigente=vigente) if proposta else None,
            "geracao": [str(item.id) for item in geracao],
            "temCorte": tem_corte,
        }
    )
    return base


def _recusa(estado, *, lista_id, vigente, tem_corte):
    """`(codigo, frase)` da recusa do gesto, ou `None`. Primeiro o recorte, depois a lista."""
    if lista_id is None:
        return (
            SO_LISTA_RESERVADA,
            "O gesto é da lista reservada em que ninguém concorre: a ampla concorrência vazia é um "
            "Perfil sem inscrição nenhuma, e a ordem dela se emite na classificação.",
        )
    proposta = estado["proposta"]
    if proposta is None or not estado["recomputavel"]:
        return (
            LISTA_COM_CONCORRENTE,
            "A ordem desta lista não se calcula pelas Etapas: o gesto não se aplica a ela.",
        )
    if proposta["posicoes"] or proposta["sem_posicao"]:
        return (
            LISTA_COM_CONCORRENTE,
            "Há quem concorra por esta lista: a ordem dela tem linhas, e se emite na "
            "classificação, com a conferência da ordem.",
        )
    if vigente is not None and (estado["obsoleto"] or vigente.posicoes.exists()):
        # A sucessão exige motivo, e o gesto não sucede nada: é o que `conducao_do_marco` também
        # recusa no gesto do marco da `049`.
        return (
            LISTA_JA_REGISTRADA,
            "Esta lista já tem ordem vigente, e suceder uma ordem exige motivo: a sucessão se faz "
            "na tela do recorte.",
        )
    return None


# --- O gesto -----------------------------------------------------------------------------------


def registrar_lista_sem_concorrente(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    lista_id,
    assinatura,
    idempotency_key,
    correlation_id,
):
    """Emite a ordem vazia e, se o marco corta, o corte vazio, numa transação (FR-6328, FR-6329).

    Recusa o que os dois comandos recusam, e mais `lista_com_concorrente`. A trava é a do Processo,
    tomada aqui e reencontrada pelos dois comandos, que rodam aninhados: a conferência e a emissão
    leem o mesmo mundo.
    """
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "leitura": assinatura or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        from processo_seletivo.classificacao.application.emissao import _edital_do_processo

        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil, marco = identificador(perfil_id), identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        lida = conferencia(
            edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=ctx.now
        )
        if lida["recusa"] is not None:
            codigo, frase = lida["recusa"]
            raise DomainError(codigo, frase, 409)
        if (assinatura or "") != lida["assinatura"]:
            raise DomainError(
                LEITURA_MUDOU,
                "Esta lista mudou desde que a conferência foi aberta: confira de novo antes de "
                "registrar.",
                409,
            )
        registrado = {"ordem": None, "corte": None}
        if lida["ordem"]:
            # A confirmação é a da proposta que `emitir_ordem` recalcula — a mesma função, o mesmo
            # recorte, nenhum vigente. A conferência do gesto já foi conferida acima, e é ela que a
            # pessoa leu; esta é a que o comando exige de qualquer emissão.
            proposta_da_ordem = calcular_ordem(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=ctx.now
            )
            emitir_ordem(
                actor=actor,
                processo_id=processo_id,
                edital_id=edital.id,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                idempotency_key=f"{idempotency_key}:ordem",
                correlation_id=correlation_id,
                confirmacao_do_calculo=assinatura_da_proposta(proposta_da_ordem),
            )
        ato = ato_vigente(edital=edital, marco_id=str(marco), lista_id=lista)
        registrado["ordem"] = str(ato.id)
        if lida["corte"]:
            proposta = calcular_corte(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=ctx.now
            )
            # **O corte vazio, conferido**: a ordem vazia não tem quem a faixa alcance, e um item
            # aqui seria linha de candidato que o gesto não pode gravar (FR-6329).
            if proposta["itens"]:
                raise DomainError(
                    LISTA_COM_CONCORRENTE,
                    "A faixa desta lista alcançaria alguém: o corte se emite na tela do corte.",
                    409,
                )
            emitir_corte(
                actor=actor,
                processo_id=processo_id,
                edital_id=edital.id,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                idempotency_key=f"{idempotency_key}:corte",
                correlation_id=correlation_id,
                confirmacao_do_calculo=assinatura_do_corte(proposta, geracao=[]),
            )
            registrado["corte"] = str(
                geracao_vigente(edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista)[
                    0
                ].id
            )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=EVENTO,
            aggregate=ato,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                f"Lista {lista} do marco {marco}, Perfil {perfil}, registrada sem concorrente: "
                + (
                    f"ordem vazia {registrado['ordem']} emitida por este gesto"
                    if lida["ordem"]
                    else f"ordem vazia {registrado['ordem']}, já vigente"
                )
                + (f"; corte vazio {registrado['corte']}" if registrado["corte"] else "")
                + ". Nenhuma posição nem item de candidato gravado."
            ),
            idempotency_key=idempotency_key,
        )
        declarado = {**registrado, "listaId": str(lista)}
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


# --- A porta -----------------------------------------------------------------------------------


@require_http_methods(["GET", "POST"])
def registrar(request, edital_id, marco_id):
    """A conferência do gesto (GET, ou POST sem `confirmar`), ou o gesto confirmado (FR-6331).

    **O GET abre a conferência** porque é por um link que a providência do andamento chega aqui
    (FR-4671 da `135`, revista pela `155`): a conferência não grava nada, e quem a abre lê o que o
    clique registraria antes de praticá-lo.
    """
    from processo_seletivo.interface import andamento, views

    ator, edital, _ = views._edital_para_classificar(request, edital_id, somente_gestao=True)
    if ator is None:
        return identidade.pedir_identificacao(request)
    if views._e_marco_de_sorteio(edital, marco_id):
        return redirect(reverse("interface:sorteio", args=[edital_id, marco_id]))
    dados = request.POST if request.method == "POST" else request.GET
    lista_id = views._recorte_pedido(edital, marco_id, dados.get("lista"))
    perfil_id = views._perfil_do_marco(edital, marco_id)
    if lista_id is None and request.method == "GET":
        # **A providência que junta as listas vazias de um marco** chega sem `?lista=` (o
        # agrupamento da `127`): o gesto é de uma lista, e a conferência abre na primeira que falta,
        # na ordem da derivação. Registrada ela, a ordenação diz a seguinte.
        return redirect(_primeira_pendente(edital, perfil_id, marco_id))
    destino = views._url_no_recorte(edital, marco_id, rota="interface:ordenacao", lista_id=lista_id)
    chave = dados.get("chave") or uuid4().hex
    aviso = ""
    if request.method == "POST" and request.POST.get("confirmar") == "1":
        try:
            request.session["resultado_da_ordenacao"] = {
                "listaSemConcorrente": registrar_lista_sem_concorrente(
                    actor=ator,
                    processo_id=edital.processo_id,
                    edital_id=edital.id,
                    perfil_id=perfil_id,
                    marco_id=marco_id,
                    lista_id=lista_id,
                    assinatura=request.POST.get("leitura", ""),
                    idempotency_key=chave,
                    correlation_id=getattr(request, "correlation_id", "")
                    or f"interface-lista-sem-concorrente-{edital_id}",
                )
            }
            return redirect(destino)
        except DomainError as erro:
            if erro.code != LEITURA_MUDOU:
                request.session["erro_da_ordenacao"] = erro.detail
                return redirect(destino)
            aviso = erro.detail
    lida = conferencia(edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id)
    if lida["recusa"] is not None:
        request.session["erro_da_ordenacao"] = lida["recusa"][1]
        return redirect(destino)
    estado = estado_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
    return marcar_como_privada(
        render(
            request,
            "interface/ordenacao_lista_sem_concorrente.html",
            {
                "processo": edital.processo,
                "edital": edital,
                "perfil": estado["perfil"],
                "marco": estado["marco"],
                "lista_id": lista_id,
                **views._navegacao_do_recorte(
                    edital, marco_id, rota="interface:ordenacao", atual=lista_id
                ),
                "conferencia": lida,
                "chave_idempotencia": chave,
                "aviso": aviso,
                # A frase do ato é a da providência (FR-4672): uma redação só para as duas telas.
                "frase_do_ato": andamento.ATO_DA_ORDEM_VAZIA,
                "frase_da_publicacao": FRASE_DA_PUBLICACAO,
            },
        )
    )


# --- A publicação conjunta, na prévia (155, FR-6330, R-006) ------------------------------------


def acompanhantes_da_previa(*, edital, marco_id, ato):
    """`{"candidatas", "itens"}`: as listas sem concorrente que saem junto desta publicação.

    `candidatas` é o que a assinatura da prévia cobre (`publicar.assinatura_da_previa`); `itens` é o
    que a tela diz de cada uma — o nome da lista e, quando a natureza decide, em qual ela vai. A
    natureza é escolhida no mesmo formulário, e por isso a frase diz as duas, sem adivinhar.
    """
    from processo_seletivo.divulgacao.application.publicar import (
        incluidas_na_publicacao,
        listas_sem_concorrente_do_marco,
    )
    from processo_seletivo.divulgacao.models import Natureza
    from processo_seletivo.interface.destinacao_da_vaga import rotulo_do_recorte

    candidatas = listas_sem_concorrente_do_marco(edital=edital, marco_id=marco_id, ato=ato)
    if not candidatas:
        return {"candidatas": [], "itens": []}
    conteudo = effective_version(edital_id=edital.id).content
    por_natureza = {}
    for natureza in Natureza.values:
        incluidas, de_fora = incluidas_na_publicacao(
            edital=edital, marco_id=marco_id, candidatas=candidatas, natureza=natureza
        )
        por_natureza[natureza] = (
            {str(i["ato"].id) for i in incluidas},
            {str(i["ato"].id): i["motivo"] for i in de_fora},
        )
    itens = []
    for item in candidatas:
        chave = str(item["ato"].id)
        vai = [n for n in Natureza.values if chave in por_natureza[n][0]]
        motivos = [
            por_natureza[n][1][chave] for n in Natureza.values if chave in por_natureza[n][1]
        ]
        if len(vai) == len(Natureza.values):
            frase = "ninguém concorreu — sai junto desta publicação"
        elif vai:
            frase = (
                "ninguém concorreu — sai junto desta publicação se ela for o resultado "
                + {Natureza.PRELIMINAR: "preliminar", Natureza.DEFINITIVA: "definitivo"}[vai[0]]
            )
        else:
            frase = "ninguém concorreu — fica de fora desta publicação"
        if motivos and len(vai) < len(Natureza.values):
            frase += f": {motivos[0]}"
        itens.append(
            {
                "rotulo": rotulo_do_recorte(conteudo, item["ato"].perfil_id, item["lista_id"]),
                "frase": frase,
            }
        )
    return {"candidatas": candidatas, "itens": itens}


def _primeira_pendente(edital, perfil_id, marco_id):
    """A conferência da primeira lista vazia ainda sem a ordem, ou a ordenação do marco."""
    from processo_seletivo.classificacao.application.calculo import listas_sem_concorrente
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil

    conteudo = effective_version(edital_id=edital.id).content
    vazias = {
        str(lista)
        for lista in listas_sem_concorrente(
            edital=edital, conteudo=conteudo, perfil_id=perfil_id, marco_id=marco_id
        )
    }
    for lista, _ in recortes_do_perfil(conteudo, perfil_id=perfil_id):
        if (
            lista
            and str(lista) in vazias
            and not ato_vigente(edital=edital, marco_id=str(marco_id), lista_id=lista)
        ):
            rota = reverse("interface:registrar-lista-sem-concorrente", args=[edital.id, marco_id])
            return f"{rota}?lista={lista}"
    return reverse("interface:ordenacao", args=[edital.id, marco_id])


__all__ = [
    "ATO",
    "acompanhantes_da_previa",
    "EVENTO",
    "LISTA_COM_CONCORRENTE",
    "conferencia",
    "registrar",
    "registrar_lista_sem_concorrente",
]
