"""Publicar as convocações no GPS: a prévia do Edital e o ato (149, FR-5701 a FR-5711).

```text
prévia (GET)  → lê o Edital inteiro em consultas fixas, avalia cada convocação, compõe os grupos
confirmação   → comando_de_comissao (trava do Processo, idempotência)
              → a mesma prévia, agora; assinatura confere?           (409 se não)
              → declaração do veículo, se alguém é convocado aqui    (422 se faltar)
              → autoridade da `060`                                  (a recusa dela)
              → número = maior + 1
              → ato + comunicação de cada *convoca* + vínculos + documento + trilha, no mesmo commit
```

**Um ato por Edital, e não por recorte** (D-009). O gesto das pendentes da `050` é por recorte, e a
comissão faria N publicações para a 1ª chamada de um Edital de N vagas e listas — o retrabalho que o
pedido quer eliminar. Aqui a comissão escolhe os recortes, e todos entram por padrão.

**A comunicação nasce na transação do ato** (D-003). Não há efeito externo a proteger de um
`rollback`, como há no SMTP da `050`: o ato **é** a publicação, e ela só existe depois do `commit`.
"""

import hashlib

from django.db import IntegrityError
from django.db.models import Max

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.convocacao.application.comunicar import COMUNICAR
from processo_seletivo.convocacao.application.convocar import _edital_do_processo
from processo_seletivo.convocacao.application.selectors import (
    desfecho_de,
    envio_de,
    forma_do_perfil,
    identidades_de,
    vigentes,
)
from processo_seletivo.convocacao.domain import publicacao as dominio
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    Convocacao,
    ConvocacaoPublicada,
    DocumentoDaPublicacaoDeConvocados,
    PublicacaoDeConvocados,
)
from processo_seletivo.editais.domain.recortes import recortes_do_perfil
from processo_seletivo.publicacoes.application.contexto_do_ato import (
    colunas_da_unidade,
    contexto_do_ato,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from processo_seletivo.publicacoes.models import VersaoConsolidada
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.requerimentos.domain.disponibilidade import momento_declarado
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256

ATO = "convocacao:publicar_convocados"
PUBLICAR = "CONVOCACAO_PUBLICAR_CONVOCADOS"

PREVIA_OBSOLETA = "publicacao_previa_obsoleta"
NADA_A_PUBLICAR = "nada_a_publicar"
VEICULO_NAO_DECLARADO = "veiculo_nao_declarado"

#: O nome público da ampla concorrência — o mesmo de `divulgacao.domain.conteudo.nome_da_lista`.
LISTA_AMPLA = "Ampla concorrência"


def chave_do_recorte(perfil_id, marco_id, lista_id):
    """`perfil:marco:lista` — o recorte como o formulário o envia; a ampla é `ampla`."""
    return f"{perfil_id}:{marco_id}:{lista_id or 'ampla'}"


def previa_da_publicacao(*, edital, recortes=None, at, convocacoes=None):
    """O que a publicação de agora faria, recorte a recorte — sem gravar nada (FR-5708, SC-1864).

    `recortes` é o conjunto de chaves escolhidas; `None` escolhe todos os que têm o que publicar.

    **Consultas fixas** (FR-5736): as convocações do Edital, as três coleções que a vigência, o
    desfecho e o envio leem, as versões citadas, as identidades, as reservas indeterminadas e as
    publicações anteriores — uma cada, qualquer que seja o número de recortes e de pessoas.
    """
    from processo_seletivo.convocacao.application.fluxo import _com_emissao_indeterminada

    do_gesto = None if convocacoes is None else {str(c) for c in convocacoes}
    convocacoes = list(
        Convocacao.objects.filter(edital=edital)
        .prefetch_related("sucessoras", "desfechos", "comunicacoes")
        .order_by("criado_em", "id")
    )
    por_id = {c.id: c for c in convocacoes}
    em_vigor = vigentes(convocacoes)
    if do_gesto is not None:
        # **Só as convocações do gesto** (159, FR-6815): a publicação que nasce de uma confirmação
        # de convocar diz quem aquela confirmação convocou, e não o que mais houver a publicar no
        # Edital. A cadeia inteira continua em `por_id`, para a marca de correção (FR-6817).
        em_vigor = [c for c in em_vigor if str(c.id) in do_gesto]
    versoes = VersaoConsolidada.objects.in_bulk({c.versao_id for c in em_vigor})
    identidades = identidades_de({c.inscricao_id for c in em_vigor})
    indeterminadas = _com_emissao_indeterminada(
        c.id for c in em_vigor if envio_de(c) is None and desfecho_de(c) is None
    )
    numero_de = dict(
        ConvocacaoPublicada.objects.filter(publicacao__edital=edital).values_list(
            "convocacao_id", "publicacao__numero"
        )
    )
    maior = PublicacaoDeConvocados.objects.filter(edital=edital).aggregate(n=Max("numero"))["n"]
    numero = (maior or 0) + 1

    por_recorte = {}
    for convocacao in em_vigor:
        versao = versoes[convocacao.versao_id]
        conteudo = versao.content or {}
        chave = chave_do_recorte(convocacao.perfil_id, convocacao.marco_id, convocacao.lista_id)
        if chave not in por_recorte:
            por_recorte[chave] = _recorte(chave, convocacao, conteudo)
        recorte = por_recorte[chave]
        forma = forma_do_perfil(conteudo.get("profiles"), convocacao.perfil_id)
        comunicacao = _ultima_bem_sucedida(convocacao)
        avaliada = dominio.avaliar(
            forma=forma,
            desfechada=desfecho_de(convocacao) is not None,
            enviada_em=comunicacao.enviado_em if comunicacao else None,
            indeterminada=convocacao.id in indeterminadas,
            vencimento=convocacao.vencimento,
            ja_publicada=convocacao.id in numero_de,
            agora=at,
        )
        pessoa = identidades[convocacao.inscricao_id]
        if avaliada.efeito is None:
            if avaliada.motivo:
                recorte["fora"].append(
                    {
                        "protocolo": pessoa["protocolo"],
                        "nome": pessoa["nome"],
                        "motivo": dominio.MOTIVOS_DE_FORA[avaliada.motivo],
                    }
                )
            continue
        recorte["linhas"].append(
            {
                "convocacao": convocacao,
                "comunicacao": comunicacao,
                "linha": {
                    "chave": chave,
                    "ordem": recorte["ordem"],
                    "perfil": recorte["perfil"],
                    "lista": recorte["lista"],
                    "marco": recorte["marco"],
                    "efeito": avaliada.efeito,
                    "canal": (
                        dominio.canal_da_divulgacao(
                            comunicacao.forma, comunicacao.referencia_da_publicacao
                        )
                        if avaliada.efeito == dominio.DIVULGA
                        else ""
                    ),
                    "vencimento": convocacao.vencimento,
                    "nome": pessoa["nome"] or "",
                    "protocolo": pessoa["protocolo"] or "",
                    "corrige": _corrige(convocacao, por_id, numero_de),
                },
            }
        )

    # **Na ordem em que foram convocadas, e no mesmo gesto, na ordem da fila** (FR-5714). As de um
    # gesto nascem no mesmo instante, e o desempate saía pelo identificador interno: a relação do
    # C10 listava Bernardo, Cecília e Alice, embora Alice fosse a primeira da classificação e a
    # primeira chamada. A fila é a classificação, e por isso a posição vem antes do protocolo.
    posicao = _posicoes_na_classificacao(
        [x["convocacao"] for r in por_recorte.values() for x in r["linhas"]]
    )
    for recorte in por_recorte.values():
        recorte["linhas"].sort(
            key=lambda x: (
                x["convocacao"].criado_em,
                posicao.get((x["convocacao"].ato_de_ordenacao_id, x["convocacao"].inscricao_id))
                or 10**9,
                x["linha"]["protocolo"],
            )
        )
        recorte["convoca"] = sum(1 for x in recorte["linhas"] if x["linha"]["efeito"] == "CONVOCA")
        recorte["divulga"] = len(recorte["linhas"]) - recorte["convoca"]
        recorte["escolhido"] = bool(recorte["linhas"]) and (
            recortes is None or recorte["chave"] in recortes
        )
    ordenados = sorted(por_recorte.values(), key=lambda r: r["ordem"])
    escolhidas = [x for r in ordenados if r["escolhido"] for x in r["linhas"]]
    grupos = dominio.compor_grupos([x["linha"] for x in escolhidas])
    itens = [
        (
            x["convocacao"].id,
            x["linha"]["efeito"],
            x["comunicacao"].id if x["linha"]["efeito"] == dominio.DIVULGA else None,
        )
        for x in escolhidas
    ]
    return {
        "numero": numero,
        "titulo": dominio.titulo(numero),
        "recortes": ordenados,
        "com_o_que_publicar": [r for r in ordenados if r["linhas"]],
        "fora": sum(len(r["fora"]) for r in ordenados),
        "escolhidas": escolhidas,
        "grupos": grupos,
        "natureza": dominio.natureza(grupos) if grupos else "",
        "convoca": sum(1 for _, efeito, _ in itens if efeito == dominio.CONVOCA),
        "divulga": sum(1 for _, efeito, _ in itens if efeito == dominio.DIVULGA),
        "assinatura": dominio.assinatura(edital_id=edital.id, numero=numero, itens=itens),
    }


def _posicoes_na_classificacao(convocacoes):
    """`{(ato, inscrição): posição}` das convocações, numa consulta só (FR-5736).

    A posição é a do ato de ordenação que a convocação citou, e não a da ordem vigente: é a fila
    que valia quando ela foi chamada.
    """
    from processo_seletivo.classificacao.models import PosicaoNaOrdem

    if not convocacoes:
        return {}
    return {
        (linha["ato_id"], linha["inscricao_id"]): linha["posicao"]
        for linha in PosicaoNaOrdem.objects.filter(
            ato_id__in={c.ato_de_ordenacao_id for c in convocacoes},
            inscricao_id__in={c.inscricao_id for c in convocacoes},
        ).values("ato_id", "inscricao_id", "posicao")
    }


def nomes_publicos(conteudo, *, perfil_id, marco_id, lista_id):
    """A vaga, a lista e o marco pelos nomes que a relação pública imprime (FR-5726).

    Uma função só para a publicação e para a conferência de convocar (159, FR-6802): o que se
    confere como público é, letra a letra, o que se publica.
    """
    from processo_seletivo.classificacao.domain.nomes import nomes_do_marco

    nomes = nomes_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    listas = recortes_do_perfil(conteudo, perfil_id=perfil_id)
    alvo = str(lista_id) if lista_id else None
    # **O nome da lista é o que a divulgação do resultado publica** (FR-5726, D-008): a ampla por
    # extenso, e a reserva pelo nome da Modalidade. O rótulo da gestão — "linha geral do quadro",
    # o código entre parênteses — é vocabulário de quem conduz, e não de quem consulta.
    rotulo_da_lista = ((nomes["modalidades"].get(alvo) or "") if alvo else LISTA_AMPLA) or next(
        (r for lista, r in listas if lista == alvo), ""
    )
    return {
        "perfil": nomes["perfil"].get("name") or "",
        "lista": rotulo_da_lista,
        "marco": nomes["marco"].get("name") or "",
        "posicao_da_lista": next((i for i, (lista, _) in enumerate(listas) if lista == alvo), 0),
    }


def _recorte(chave, convocacao, conteudo):
    """O recorte com os nomes da versão que a convocação citou, e a posição dele no Edital."""
    nomes = nomes_publicos(
        conteudo,
        perfil_id=convocacao.perfil_id,
        marco_id=convocacao.marco_id,
        lista_id=convocacao.lista_id,
    )
    perfis = [str(p.get("id")) for p in conteudo.get("profiles") or [] if isinstance(p, dict)]
    perfil = str(convocacao.perfil_id)
    return {
        "chave": chave,
        "perfil_id": convocacao.perfil_id,
        "marco_id": convocacao.marco_id,
        "lista_id": convocacao.lista_id,
        "perfil": nomes["perfil"],
        "lista": nomes["lista"],
        "marco": nomes["marco"],
        "ordem": (
            perfis.index(perfil) if perfil in perfis else len(perfis),
            nomes["posicao_da_lista"],
            str(convocacao.marco_id),
        ),
        "linhas": [],
        "fora": [],
    }


def _ultima_bem_sucedida(convocacao):
    """A comunicação bem-sucedida mais recente da própria convocação, ou `None`."""
    enviadas = [c for c in convocacao.comunicacoes.all() if c.enviado_em is not None]
    return max(enviadas, key=lambda c: c.enviado_em) if enviadas else None


def _corrige(convocacao, por_id, numero_de):
    """O número da publicação que divulgou uma convocação que esta corrige, ou `None` (D-006).

    A cadeia é lida em memória, da anterior imediata para a raiz: a correção da correção corrige o
    que foi publicado por último.
    """
    anterior = por_id.get(convocacao.convocacao_anterior_id)
    while anterior is not None:
        if anterior.id in numero_de:
            return numero_de[anterior.id]
        anterior = por_id.get(anterior.convocacao_anterior_id)
    return None


def publicar_convocados(
    *,
    actor,
    processo_id,
    edital_id,
    recortes,
    alcance_confirmado,
    autoridade,
    declaracao_do_veiculo,
    idempotency_key,
    correlation_id,
):
    """Pratica a publicação de convocados que a prévia mostrou (FR-5701 a FR-5711).

    `recortes` é o conjunto de chaves escolhidas, como a prévia o recebeu; `None` escolhe todos.
    """
    escolhidos = None if recortes is None else sorted(set(recortes))
    declaracao = (declaracao_do_veiculo or "").strip()
    payload = {
        "edital": str(edital_id),
        "recortes": escolhidos,
        "alcance": alcance_confirmado or "",
        "autoridade": str(autoridade or ""),
        "declaracao": declaracao,
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            # A repetição devolve o ato que o primeiro pedido praticou, e não uma leitura do mundo
            # depois dele (FR-5707): o duplo clique recebe a mesma publicação.
            return ctx.desfecho_anterior
        agora = ctx.now
        edital = _edital_do_processo(ctx.processo, edital_id)
        previa = previa_da_publicacao(
            edital=edital, recortes=None if escolhidos is None else set(escolhidos), at=agora
        )
        if (alcance_confirmado or "") != previa["assinatura"]:
            raise DomainError(
                PREVIA_OBSOLETA,
                "O que seria publicado mudou entre a prévia e a confirmação — alguém convocou, "
                "comunicou ou publicou nesse meio-tempo. Confira a prévia de novo antes de "
                "publicar.",
                409,
            )
        if not previa["escolhidas"]:
            raise DomainError(
                NADA_A_PUBLICAR,
                "Não há convocação a publicar nas vagas e listas escolhidas.",
                409,
            )
        if previa["convoca"] and not declaracao:
            raise DomainError(
                VEICULO_NAO_DECLARADO,
                "Esta publicação é o ato oficial de convocação de "
                f"{previa['convoca']} {'pessoa' if previa['convoca'] == 1 else 'pessoas'}: "
                "diga onde o Edital admite a página pública do GPS como veículo da convocação — "
                "por exemplo, «item 7.2 do Edital». Se o Edital não a admite, publique fora do GPS "
                "e registre a publicação na tela da convocação.",
                422,
                campo="declaracao_do_veiculo",
            )
        declarado = gravar_publicacao(
            ctx,
            actor=actor,
            edital=edital,
            previa=previa,
            autoridade=autoridade,
            declaracao=declaracao,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


ATO_DO_GESTO = "convocacao:publicar_do_gesto"


def publicar_na_transacao(
    ctx, *, actor, edital, convocacoes, autoridade, declaracao, correlation_id, idempotency_key
):
    """Convocar e publicar no GPS num ato só: a publicação dentro da transação do gesto (D-004).

    Toda convocação do gesto precisa sair com efeito *convoca*: uma que não saísse — vencimento já
    passado, forma que não é a publicação — ficaria convocada e invisível, aguardando uma publicação
    que a confirmação prometeu fazer. A recusa desfaz o gesto inteiro (FR-6809).
    """
    declaracao = (declaracao or "").strip()
    if not declaracao:
        raise DomainError(
            VEICULO_NAO_DECLARADO,
            "Para convocar e publicar no GPS, diga onde o Edital admite a página pública do GPS "
            "como veículo da convocação — por exemplo, «item 7.2 do Edital». Se o Edital manda "
            "publicar em outro lugar, escolha «Fora do GPS».",
            422,
            campo="declaracao_do_veiculo",
        )
    previa = previa_da_publicacao(edital=edital, at=ctx.now, convocacoes=convocacoes)
    if previa["convoca"] != len(convocacoes):
        raise DomainError(
            NADA_A_PUBLICAR,
            "Nem todas as convocações deste gesto podem ser publicadas como ato oficial agora — "
            "confira a forma de comunicar do Perfil e o vencimento. Nada foi convocado.",
            409,
        )
    return gravar_publicacao(
        ctx,
        actor=actor,
        edital=edital,
        previa=previa,
        autoridade=autoridade,
        declaracao=declaracao,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
    )


def publicar_do_gesto(
    *, actor, processo_id, edital_id, convocacoes, autoridade, idempotency_key, correlation_id
):
    """A relação informativa das convocações de um gesto já comunicadas (159, D-005, D-007).

    Depois dos envios, ou dos registros da publicação externa, numa transação própria e com a chave
    derivada do gesto: a falha aqui não desfaz convocação nem comunicação (FR-6812), e repetir a
    confirmação completa a publicação sem repetir o resto (FR-6813). Só entram as do gesto que a
    prévia avalia como *divulga* — as comunicadas com sucesso e ainda não publicadas; a que falhou
    fica fora (FR-6806). Sem nenhuma, nada é publicado, e devolve `None`.
    """
    ids = sorted(str(c) for c in convocacoes)
    # **As convocações não entram na reserva**: a chave já é derivada do gesto, e nas pendentes a
    # lista é lida no momento do pedido — a segunda tentativa do mesmo clique veria outra, e
    # receberia `idempotency_conflict` em vez do que a primeira publicou.
    payload = {"edital": str(edital_id), "autoridade": str(autoridade or "")}
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DO_GESTO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        previa = previa_da_publicacao(edital=edital, at=ctx.now, convocacoes=ids)
        if previa["convoca"]:
            # Ninguém a convocar aqui: a publicação que convoca é a do GPS, na transação do gesto.
            previa = _so_as_divulgadas(previa)
        if not previa["escolhidas"]:
            ctx.concluir_sem_resultado(200, None)
            return None
        declarado = gravar_publicacao(
            ctx,
            actor=actor,
            edital=edital,
            previa=previa,
            autoridade=autoridade,
            declaracao="",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _so_as_divulgadas(previa):
    """A prévia sem as linhas *convoca* — a publicação informativa não convoca ninguém."""
    escolhidas = [x for x in previa["escolhidas"] if x["linha"]["efeito"] == dominio.DIVULGA]
    grupos = dominio.compor_grupos([x["linha"] for x in escolhidas])
    return {
        **previa,
        "escolhidas": escolhidas,
        "grupos": grupos,
        "convoca": 0,
        "divulga": len(escolhidas),
    }


def gravar_publicacao(
    ctx, *, actor, edital, previa, autoridade, declaracao, correlation_id, idempotency_key
):
    """Grava o ato que a prévia descreve, no `comando_de_comissao` de quem chama (159, D-003).

    **Extraída de `publicar_convocados`** para que convocar e publicar sejam uma confirmação: a
    página da `149` a chama depois de conferir a prévia do Edital; o gesto de convocar, com a prévia
    das convocações dele — dentro da própria transação, quando o GPS é o veículo oficial (D-004), ou
    numa transação própria depois dos envios, quando a relação é informativa (D-005). O que se grava
    é o mesmo nos três caminhos: o ato, a comunicação de cada *convoca*, os vínculos, o documento e
    a trilha.
    """
    agora = ctx.now
    if not previa["convoca"]:
        # Sem ninguém convocado aqui, a declaração não tem objeto, e não é gravada (D-012).
        declaracao = ""
    # A autoridade habilitada na unidade do Edital e vigente hoje, conferida pela mesma regra
    # da publicação do Edital e do resultado (060, FR-1125).
    contexto = contexto_do_ato(edital, autoridade, agora)
    assinante = contexto.autoridade
    numero = previa["numero"]
    versao = effective_version(edital_id=edital.id, at=agora)
    conteudo = dominio.conteudo(
        cabecalho=_cabecalho(edital, versao, numero, agora, assinante, contexto.unidade),
        grupos=previa["grupos"],
    )
    try:
        ato = PublicacaoDeConvocados.objects.create(
            edital=edital,
            numero=numero,
            conteudo_publico=canonical_bytes(conteudo),
            conteudo_publico_hash=canonical_sha256(conteudo),
            publicado_por=actor.subject,
            publicado_em=agora,
            declaracao_do_veiculo=declaracao,
            signatario_id=assinante.pk,
            signatario_nome=assinante.nome,
            signatario_cargo=assinante.cargo,
            signatario_ato_de_nomeacao=assinante.ato_de_nomeacao,
            **colunas_da_unidade(contexto.unidade),
        )
    except IntegrityError as erro:
        # A trava do Processo serializa as publicações; a constraint é a segunda guarda.
        raise DomainError(PREVIA_OBSOLETA, "Outra publicação foi feita agora.", 409) from erro

    referencia = dominio.referencia_nativa(numero, agora)
    vinculos = []
    for escolhida in previa["escolhidas"]:
        convocacao = escolhida["convocacao"]
        if escolhida["linha"]["efeito"] == dominio.CONVOCA:
            comunicacao = ComunicacaoEmitida.objects.create(
                convocacao=convocacao,
                forma=FORMA_POR_PUBLICACAO,
                referencia_da_publicacao=referencia,
                enviado_em=agora,
                resultado="ENVIADA",
            )
            # A frase da publicação registrada da `125` (R-008 dela), com o ato que publicou: a
            # trilha de cada pessoa diz de onde o prazo dela corre (FR-5711).
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=COMUNICAR,
                aggregate=comunicacao,
                now=agora,
                correlation_id=correlation_id,
                reason=(
                    f"Publicação da convocação {convocacao.id}, inscrição "
                    f"{convocacao.inscricao_id}, pela {dominio.titulo(numero)} no GPS "
                    f"({ato.id}): {referencia}. Registro em {agora.isoformat()}."
                ),
                idempotency_key=idempotency_key,
            )
        else:
            comunicacao = escolhida["comunicacao"]
        vinculos.append(
            ConvocacaoPublicada(
                publicacao=ato,
                convocacao=convocacao,
                comunicacao=comunicacao,
                efeito=escolhida["linha"]["efeito"],
            )
        )
    ConvocacaoPublicada.objects.bulk_create(vinculos)
    _gravar_documento(ato, conteudo)
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=PUBLICAR,
        aggregate=ato,
        now=agora,
        correlation_id=correlation_id,
        reason=(
            f"{dominio.titulo(numero).capitalize()} do Edital {edital.number}/{edital.year} "
            f"publicada no GPS: {previa['convoca']} convocada(s) por ela e "
            f"{previa['divulga']} divulgada(s). "
            + (f"Veículo declarado: {declaracao}." if declaracao else "Nenhuma convocada.")
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(ato.id),
        "numero": numero,
        "titulo": dominio.titulo(numero),
        "convoca": previa["convoca"],
        "divulga": previa["divulga"],
        "publicadaEm": agora.isoformat(),
    }
    return declarado


def _cabecalho(edital, versao, numero, agora, assinante, unidade):
    """A identificação do ato, como estava no dia (FR-5713)."""
    from processo_seletivo.classificacao.domain.nomes import edital_por_extenso

    conteudo = versao.content or {}
    return {
        "unidade": {
            "cabecalho": list(unidade.cabecalho),
            "local": unidade.local,
            "sigla": unidade.sigla,
            "nome": unidade.nome,
        },
        "edital": edital_por_extenso(conteudo, edital),
        "processo": conteudo.get("processoTitle", "") or "",
        "numero": numero,
        "titulo": dominio.titulo(numero),
        "publicadoEm": agora.isoformat(),
        "signatario": {
            "nome": assinante.nome,
            "cargo": assinante.cargo,
            "atoDeNomeacao": assinante.ato_de_nomeacao,
        },
        # Para a orientação dizer que o Requerimento também está na Área do candidato (FR-5716).
        "requerimentoNaConvocacao": (
            momento_declarado(conteudo) == requerimento_nomes.NA_CONVOCACAO
        ),
    }


def _gravar_documento(ato, conteudo):
    """O documento oficial, dos mesmos bytes que a página lê, gravado uma vez (FR-5710)."""
    from processo_seletivo.convocacao.infrastructure.documento import render_convocados_pdf

    arquivo = render_convocados_pdf(conteudo)
    DocumentoDaPublicacaoDeConvocados.objects.create(
        publicacao=ato, bytes=arquivo, documento_hash=hashlib.sha256(arquivo).hexdigest()
    )


__all__ = [
    "ATO",
    "NADA_A_PUBLICAR",
    "PREVIA_OBSOLETA",
    "PUBLICAR",
    "VEICULO_NAO_DECLARADO",
    "chave_do_recorte",
    "previa_da_publicacao",
    "publicar_convocados",
]
