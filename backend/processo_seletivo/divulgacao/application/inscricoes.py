"""Publicar as inscrições — a aferição, a prévia e o comando, na ordem da divulgação (148).

```text
require_permission(actor, "resultado:publicar")           # fora da transação
  ↓
transação
  ↓
ProcessoSeletivo.objects.select_for_update()              # serializa com consolidar e julgar
  ↓
reserve(operation="inscricoes:publicar:<edital>")         # repetido → o ato que já nasceu
  ↓
aferir → impedimentos nomeados, na ordem do caminho
  ↓
confirmacao_da_previa confere?                            # 409 se não
  ↓
gravar PublicacaoDasInscricoes + InscricaoNaPublicacao (com o PDF na mesma linha)
  ↓
auditar(...)  →  finish(...)
```

**É a receita de `publicar_resultado`, e não uma variação dela.** Trava, idempotência, prévia
assinada, autoridade e unidade congeladas, bytes canônicos, documento gravado uma vez, trilha. O que
muda é a fonte: em vez de um ato de ordenação, as inscrições enviadas e os resultados vigentes da
Etapa de análise.

**A trava é a do Processo**, a mesma linha que a consolidação, o julgamento do recurso e a
publicação de resultado tomam. Sem ela, a homologação aferiria "nenhum recurso pendente" enquanto
uma interposição era gravada na transação vizinha, e nasceria homologada uma inscrição em disputa.
"""

from dataclasses import dataclass, field

from django.db import IntegrityError
from django.utils.dateparse import parse_datetime

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.domain.conjunto import recusa_por_inscricoes_em_curso
from processo_seletivo.classificacao.domain.nomes import edital_por_extenso
from processo_seletivo.divulgacao.domain import inscricoes as dominio
from processo_seletivo.divulgacao.models import (
    InscricaoNaPublicacao,
    NaturezaDasInscricoes,
    PublicacaoDasInscricoes,
)
from processo_seletivo.editais.domain.recortes import recortes_do_perfil
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.contexto_do_ato import (
    colunas_da_unidade,
    contexto_do_ato,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256
from processo_seletivo.shared.idempotency import finish, reserve
from processo_seletivo.shared.tempo import ZONA

PERMISSAO = "resultado:publicar"
OPERACAO = "INSCRICOES_PUBLICAR"
SEM_RECURSO = "SEM_RECURSO"

# A consequência dita pela recusa do período em curso — a frase segue a de `conjunto.py`.
CONSEQUENCIA = "A relação das inscrições só se publica depois que o período termina."

MENSAGENS = {
    "inscricoes_publicacao_vazia": "Nenhuma inscrição foi enviada neste Edital: não há o que "
    "publicar.",
    "inscricoes_natureza_invalida": "Escolha qual ato publicar.",
    "inscricoes_natureza_regride": "Este ato não pode vir depois do que já foi publicado: a ordem "
    "é relação de recebidas, resultado preliminar e homologação das inscrições.",
    "inscricoes_motivo_obrigatorio": "Publicar de novo o mesmo ato é uma correção: escreva o "
    "motivo, que ficará impresso no ato e na página pública.",
    "inscricoes_sem_etapa_de_analise": "O Edital não declara Etapa decisória eliminatória — a "
    "análise das inscrições. Sem ela não há resultado preliminar a publicar.",
    "inscricoes_etapa_a_escolher": "O Edital tem mais de uma Etapa decisória eliminatória: escolha "
    "qual delas é a análise das inscrições.",
    "inscricoes_etapa_invalida": "A Etapa escolhida não é decisória eliminatória neste Edital.",
    "inscricoes_etapa_divergente": "Esta cadeia já publicou a análise de outra Etapa; a publicação "
    "seguinte usa a mesma.",
    "inscricoes_analise_incompleta": "{n} inscrição(ões) ainda sem conclusão consolidada na Etapa "
    "{etapa}. Conclua e consolide a análise antes de publicar.",
    "inscricoes_prazo_obrigatorio": "Escolha no Cronograma o período de recurso contra este "
    "resultado, ou declare que o Edital não prevê recurso.",
    "inscricoes_prazo_invalido": "O Evento escolhido não está no Cronograma vigente ou já "
    "terminou: publicar com prazo vencido suprimiria o recurso.",
    "inscricoes_recurso_pendente": "Há {n} recurso(s) sem decisão contra o resultado da análise. A "
    "homologação espera o julgamento.",
    "inscricoes_reavaliacao_pendente": "Há {n} reavaliação(ões) determinada(s) em recurso e ainda "
    "não cumprida(s) na Etapa de análise.",
    "inscricoes_prazo_correndo": "O prazo de recurso contra o resultado preliminar corre até "
    "{fecha}. A homologação espera o encerramento.",
}
STATUS = {
    "inscricoes_publicacao_vazia": 409,
    "inscricoes_natureza_invalida": 422,
    "inscricoes_natureza_regride": 422,
    "inscricoes_motivo_obrigatorio": 422,
    "inscricoes_sem_etapa_de_analise": 409,
    "inscricoes_etapa_a_escolher": 422,
    "inscricoes_etapa_invalida": 422,
    "inscricoes_etapa_divergente": 422,
    "inscricoes_analise_incompleta": 409,
    "inscricoes_prazo_obrigatorio": 422,
    "inscricoes_prazo_invalido": 422,
    "inscricoes_recurso_pendente": 409,
    "inscricoes_reavaliacao_pendente": 409,
    "inscricoes_prazo_correndo": 409,
}


@dataclass
class Afericao:
    """O que a prévia mostra e o comando confere — composto por uma função só."""

    natureza: str
    conteudo: dict
    versao: object
    etapa: dict | None
    etapas: list
    eventos: list
    anterior: object
    projecao: object
    impedimentos: list = field(default_factory=list)

    @property
    def publicavel(self):
        return not self.impedimentos

    @property
    def assinatura(self):
        return assinatura_da_previa(self)


def assinatura_da_previa(afericao):
    """O resumo do mundo que a prévia mostrou: natureza, Etapa, ato anterior e cada inscrição.

    Sem o instante, pela razão de `divulgacao.application.publicar.assinatura_da_previa`: o instante
    só existe no POST. Prazo, motivo e autoridade são escolha do operador, submetidos no mesmo
    pedido, e não têm como envelhecer — são validados, não assinados.
    """
    # **A versão entra desde a revisão de 12/11** (D-011): as listas do ato saem dela, e uma
    # Retificação publicada entre a prévia e a confirmação mudaria as listas com as mesmas
    # inscrições — a comissão confirmaria uma repartição que não viu (FR-5430).
    return canonical_sha256(
        {
            "natureza": afericao.natureza,
            "versao": str(afericao.versao.pk) if afericao.versao is not None else None,
            "etapa": (afericao.etapa or {}).get("id"),
            "anterior": str(afericao.anterior.id) if afericao.anterior is not None else None,
            "itens": [
                [item.inscricao_id, item.situacao, item.resultado_id]
                for item in afericao.projecao.itens
            ],
            "pendentes": afericao.projecao.pendentes,
        }
    )


# ---------------------------------------------------------------------------
# Leituras
# ---------------------------------------------------------------------------


def cadeia(edital):
    """Os atos do Edital, do primeiro ao vigente — sem o documento, que é o campo pesado."""
    return list(
        PublicacaoDasInscricoes.objects.filter(edital=edital)
        .defer("documento", "conteudo_publico")
        .order_by("publicado_em", "id")
    )


def vigente(edital):
    """O ato que ninguém sucedeu, ou `None`."""
    return (
        PublicacaoDasInscricoes.objects.filter(edital=edital, sucessoras__isnull=True)
        .defer("documento")
        .first()
    )


def etapa_da_cadeia(atos):
    """A Etapa que a cadeia já publicou, ou `None` (FR-5409)."""
    for ato in atos:
        if ato.etapa_id is not None:
            return str(ato.etapa_id)
    return None


def _enviadas(edital):
    return list(
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .order_by("id")
        .values("id", "profile_id", "modality_id", "nome", "protocolo")
    )


def _resultados_vigentes(edital, etapa_id):
    from processo_seletivo.resultados.models import ResultadoEtapa

    return {
        str(linha["inscricao_id"]): {
            "id": linha["id"],
            "habilitada": linha["consequencia"] == ResultadoEtapa.Consequencia.HABILITADA,
        }
        for linha in ResultadoEtapa.vigentes.filter(
            inscricao__edital=edital, etapa_id=etapa_id
        ).values("id", "inscricao_id", "consequencia")
    }


def _perfis(conteudo):
    return [
        (str(perfil.get("id")), perfil.get("name") or "")
        for perfil in conteudo.get("profiles") or []
    ]


def _listas_reservadas(conteudo):
    """`{perfil_id: [(modalidade_id, nome)]}` — as reservadas de cada Perfil, pelos recortes.

    **A derivação é a dos recortes, e não uma leitura própria** (FR-5439): é ela que tira a
    Modalidade apontada como a ampla, e a mesma pergunta já é feita pela classificação, pelo sorteio
    e pela ocupação. O rótulo dos recortes é o de gestão ("Nome (CÓDIGO)"); o ato publica o nome da
    Modalidade, como a divulgação do resultado (FR-5440).
    """
    listas = {}
    for perfil in conteudo.get("profiles") or []:
        if not isinstance(perfil, dict):
            continue
        perfil_id = str(perfil.get("id"))
        nomes = {
            str(modalidade.get("id")): modalidade.get("name") or ""
            for modalidade in perfil.get("competitionModalities") or []
            if isinstance(modalidade, dict)
        }
        listas[perfil_id] = [
            (lista_id, nomes.get(lista_id) or rotulo)
            for lista_id, rotulo in recortes_do_perfil(conteudo, perfil_id=perfil_id)
            if lista_id
        ]
    return listas


def projetar_agora(edital, *, natureza, etapa_id, conteudo, sem_analise=False):
    """A projeção desta natureza agora — a conta da prévia, do ato e da divergência."""
    inscricoes = [
        {
            "id": linha["id"],
            "perfil_id": linha["profile_id"],
            "modalidade_id": linha["modality_id"],
            "nome": linha["nome"],
            "protocolo": linha["protocolo"],
        }
        for linha in _enviadas(edital)
    ]
    # `None` só onde a natureza não lê Etapa: a relação de recebidas e a homologação **sem análise**
    # (D-007). Sem Etapa resolvida em qualquer outro caso, o dicionário vazio faz toda inscrição
    # contar como pendente — e a prévia não mostra deferida que ninguém deferiu.
    if natureza == dominio.RECEBIDAS or sem_analise:
        resultados = None
    elif etapa_id is None:
        resultados = {}
    else:
        resultados = _resultados_vigentes(edital, etapa_id)
    return dominio.projetar(
        natureza=natureza,
        inscricoes=inscricoes,
        resultados=resultados,
        perfis=_perfis(conteudo),
        listas=_listas_reservadas(conteudo),
    )


def divergencia_do_vigente(edital, ato=None, *, at=None):
    """Em quantas inscrições o ato vigente difere da situação de agora — ou `None` sem ato.

    Derivada, e nunca gravada (D-006): o ato não muda, e quem o lê na gestão precisa saber se ele
    ainda descreve o certame antes de decidir por uma correção.
    """
    ato = ato if ato is not None else vigente(edital)
    if ato is None:
        return None
    conteudo = effective_version(edital_id=edital.id, at=at).content
    atuais = projetar_agora(
        edital,
        natureza=ato.natureza,
        etapa_id=str(ato.etapa_id) if ato.etapa_id else None,
        conteudo=conteudo,
        sem_analise=ato.natureza == dominio.HOMOLOGACAO and ato.etapa_id is None,
    ).itens
    publicados = [
        dominio.Item(str(inscricao_id), situacao, str(resultado_id) if resultado_id else None)
        for inscricao_id, situacao, resultado_id in ato.itens.values_list(
            "inscricao_id", "situacao", "resultado_id"
        )
    ]
    return dominio.divergencia(publicados, atuais)


def publica(publicacao_id):
    """O ato pelo endereço público — qualquer um, vigente ou sucedido; sem o documento."""
    return (
        PublicacaoDasInscricoes.objects.filter(pk=publicacao_id)
        .select_related("edital")
        .defer("documento")
        .first()
    )


def documento_publico(publicacao_id):
    """`(bytes, resumo)` do documento gravado, ou `None`."""
    linha = (
        PublicacaoDasInscricoes.objects.filter(pk=publicacao_id)
        .values_list("documento", "documento_hash")
        .first()
    )
    return (bytes(linha[0]), linha[1]) if linha else None


def situacao_publicada(inscricao):
    """O que o ato vigente diz da inscrição — `None` sem ato, ou sem a inscrição nele (FR-5434).

    Lê só o **vigente**: o candidato quer saber como está, e o histórico mora na página do ato. A
    inscrição que chegou depois do ato (Retificação que reabriu o prazo) não está nele, e a tela
    não inventa uma situação para ela.
    """
    ato = vigente(inscricao.edital)
    if ato is None:
        return None
    item = ato.itens.filter(inscricao=inscricao).values_list("situacao", flat=True).first()
    if item is None:
        return None
    return {"ato": ato, "natureza": ato.natureza, "situacao": item}


def recurso_ate_do_preliminar(atos):
    """O último preliminar da cadeia, que é o que declara o prazo vigente — ou `None`."""
    preliminares = [ato for ato in atos if ato.natureza == dominio.PRELIMINAR]
    return preliminares[-1] if preliminares else None


# ---------------------------------------------------------------------------
# A aferição
# ---------------------------------------------------------------------------


def _impedimento(codigo, **campos):
    return (codigo, MENSAGENS[codigo].format(**campos))


def aferir(*, edital, natureza, etapa_id=None, at):
    """O que se publicaria, e tudo o que impede — **todos** os impedimentos, para a prévia.

    O comando recusa pelo primeiro; a prévia mostra a lista, porque quem lê precisa do caminho
    inteiro e não de uma recusa por vez. A ordem é a do caminho: o período, o universo, a cadeia, a
    Etapa, a análise e, por último, a disputa.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    conteudo = versao.content
    atos = cadeia(edital)
    anterior = atos[-1] if atos else None
    if natureza not in NaturezaDasInscricoes.values:
        raise DomainError(
            "inscricoes_natureza_invalida",
            MENSAGENS["inscricoes_natureza_invalida"],
            STATUS["inscricoes_natureza_invalida"],
            campo="natureza",
        )

    impedimentos = []
    recusa = recusa_por_inscricoes_em_curso(conteudo, at, consequencia=CONSEQUENCIA)
    if recusa is not None:
        impedimentos.append((recusa.code, recusa.detail))
    if anterior is not None and dominio.regride(anterior.natureza, natureza):
        impedimentos.append(_impedimento("inscricoes_natureza_regride"))

    etapas = dominio.etapas_de_analise(conteudo)
    etapa, problema = None, None
    if natureza != dominio.RECEBIDAS:
        etapa, problema = _etapa_escolhida(natureza, etapas, etapa_id, etapa_da_cadeia(atos))
        if problema:
            impedimentos.append(_impedimento(problema))

    projecao = projetar_agora(
        edital,
        natureza=natureza,
        etapa_id=(etapa or {}).get("id"),
        conteudo=conteudo,
        sem_analise=natureza == dominio.HOMOLOGACAO and etapa is None and problema is None,
    )
    if not projecao.itens and not projecao.pendentes:
        impedimentos.append(_impedimento("inscricoes_publicacao_vazia"))
    if projecao.pendentes and etapa is not None:
        impedimentos.append(
            _impedimento(
                "inscricoes_analise_incompleta",
                n=projecao.pendentes,
                etapa=(etapa or {}).get("name", ""),
            )
        )
    if natureza == dominio.HOMOLOGACAO and etapa is not None:
        impedimentos.extend(_disputa_em_aberto(edital, etapa["id"], atos, at))

    return Afericao(
        natureza=natureza,
        conteudo=conteudo,
        versao=versao,
        etapa=etapa,
        etapas=etapas,
        eventos=dominio.eventos_de_recurso(conteudo, at) if natureza == dominio.PRELIMINAR else [],
        anterior=anterior,
        projecao=projecao,
        impedimentos=impedimentos,
    )


def _etapa_escolhida(natureza, etapas, etapa_id, da_cadeia):
    """A Etapa de análise desta publicação, ou o motivo de não haver uma.

    A da cadeia prevalece (FR-5409). Sem Etapa decisória no Edital, o preliminar é impossível e a
    homologação é **sem análise** (D-007) — e só nesse caso, o que torna a FR-5412 verdadeira por
    construção: havendo Etapa, ela é escolhida ou exigida, nunca dispensada.
    """
    por_id = {str(etapa.get("id")): etapa for etapa in etapas}
    if da_cadeia is not None:
        if etapa_id and str(etapa_id) != da_cadeia:
            return None, "inscricoes_etapa_divergente"
        return por_id.get(da_cadeia) or {"id": da_cadeia, "name": ""}, None
    if etapa_id:
        escolhida = por_id.get(str(etapa_id))
        return (escolhida, None) if escolhida else (None, "inscricoes_etapa_invalida")
    if len(etapas) == 1:
        return etapas[0], None
    if not etapas:
        if natureza == dominio.PRELIMINAR:
            return None, "inscricoes_sem_etapa_de_analise"
        return None, None
    return None, "inscricoes_etapa_a_escolher"


def _disputa_em_aberto(edital, etapa_id, atos, at):
    """Os três fatos que só a homologação enfrenta — os da definitiva de um marco (D-004)."""
    from processo_seletivo.recursos.application import selectors as recursos

    impedimentos = []
    pendentes = recursos.recursos_pendentes_da_etapa(edital=edital, etapa_id=etapa_id)
    if pendentes:
        impedimentos.append(_impedimento("inscricoes_recurso_pendente", n=len(pendentes)))
    reavaliacoes = recursos.reavaliacoes_pendentes(edital, etapa_id=etapa_id)
    if reavaliacoes:
        impedimentos.append(_impedimento("inscricoes_reavaliacao_pendente", n=len(reavaliacoes)))
    preliminar = recurso_ate_do_preliminar(atos)
    if preliminar is not None and preliminar.recurso_ate and at <= preliminar.recurso_ate:
        fecha = preliminar.recurso_ate.astimezone(ZONA).strftime("%d/%m/%Y às %Hh%M")
        impedimentos.append(_impedimento("inscricoes_prazo_correndo", fecha=fecha))
    return impedimentos


# ---------------------------------------------------------------------------
# O comando
# ---------------------------------------------------------------------------


def publicar_inscricoes(
    *,
    actor,
    edital_id,
    natureza,
    autoridade,
    confirmacao_da_previa,
    idempotency_key,
    correlation_id="",
    etapa_id=None,
    prazo="",
    motivo="",
):
    """Publica o ato, congelando o que publicou — ou recusa antes de gravar coisa alguma."""
    require_permission(actor, PERMISSAO)
    motivo = (motivo or "").strip()
    with command_context() as agora:
        edital = (
            Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
            .select_related("processo")
            .first()
        )
        if edital is None:
            raise _nao_encontrado()
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=edital.processo_id, institution_scope=actor.institution_scope)
            .first()
        )
        if processo is None:
            raise _nao_encontrado()

        reserva = reserve(
            actor=actor,
            operation=f"inscricoes:publicar:{edital.pk}",
            key=idempotency_key,
            payload={
                "natureza": str(natureza or ""),
                "etapa": str(etapa_id or ""),
                "prazo": str(prazo or ""),
                "motivo": motivo,
                "autoridade": str(autoridade or ""),
                "confirmacao": confirmacao_da_previa or "",
            },
        )
        if reserva.result_id:
            return PublicacaoDasInscricoes.objects.get(pk=reserva.result_id)

        afericao = aferir(edital=edital, natureza=natureza, etapa_id=etapa_id, at=agora)
        if afericao.impedimentos:
            codigo, mensagem = afericao.impedimentos[0]
            raise DomainError(codigo, mensagem, STATUS.get(codigo, 409))

        anterior = afericao.anterior
        if anterior is not None and anterior.natureza == natureza and not motivo:
            raise DomainError(
                "inscricoes_motivo_obrigatorio",
                MENSAGENS["inscricoes_motivo_obrigatorio"],
                422,
                campo="motivo",
            )
        prazo_do_ato = _prazo(afericao, prazo, agora)

        if (confirmacao_da_previa or "") != afericao.assinatura:
            raise DomainError(
                "publication_preview_stale",
                "As inscrições, os resultados ou a cadeia mudaram entre a prévia e a confirmação; "
                "confira o que será publicado antes de tentar de novo.",
                409,
                campo="confirmacao_da_previa",
            )

        contexto = contexto_do_ato(edital, autoridade, agora)
        conteudo = dominio.conteudo_publico(
            projecao=afericao.projecao,
            natureza=natureza,
            processo=afericao.conteudo.get("processoTitle", "") or "",
            edital=edital_por_extenso(afericao.conteudo, edital),
            etapa=(afericao.etapa or {}).get("name", ""),
            prazo=prazo_do_ato["publico"],
            publicado_em=agora,
            signatario=contexto.autoridade,
            unidade=contexto.unidade,
            sucede=_sucede(anterior, motivo),
        )
        documento = _documento(conteudo)
        try:
            publicacao = PublicacaoDasInscricoes.objects.create(
                edital=edital,
                natureza=natureza,
                etapa_id=(afericao.etapa or {}).get("id"),
                versao=afericao.versao,
                publicacao_anterior=anterior,
                motivo_da_sucessao=motivo if anterior is not None else "",
                admite_recurso=prazo_do_ato["admite"],
                recurso_evento_id=prazo_do_ato["evento_id"],
                recurso_ate=prazo_do_ato["ate"],
                quantidade=afericao.projecao.total,
                conteudo_publico=canonical_bytes(conteudo),
                conteudo_publico_hash=canonical_sha256(conteudo),
                documento=documento,
                documento_hash=_resumo(documento),
                publicado_por=actor.subject,
                publicado_em=agora,
                signatario_id=contexto.autoridade.pk,
                signatario_nome=contexto.autoridade.nome,
                signatario_cargo=contexto.autoridade.cargo,
                signatario_ato_de_nomeacao=contexto.autoridade.ato_de_nomeacao,
                **colunas_da_unidade(contexto.unidade),
            )
        except IntegrityError as exc:
            # A segunda barreira: duas abas com chaves diferentes passaram juntas pela aferição, e a
            # unicidade de raiz ou de sucessor recusou a segunda (FR-5406).
            raise DomainError(
                "publication_already_exists",
                "Outra publicação das inscrições acabou de ser feita; confira a cadeia.",
                409,
            ) from exc

        InscricaoNaPublicacao.objects.bulk_create(
            InscricaoNaPublicacao(
                publicacao=publicacao,
                inscricao_id=item.inscricao_id,
                situacao=item.situacao,
                resultado_id=item.resultado_id,
            )
            for item in afericao.projecao.itens
        )
        auditar(
            actor=actor,
            permissao=PERMISSAO,
            operation=OPERACAO,
            aggregate=publicacao,
            now=agora,
            correlation_id=correlation_id,
            # O ato e a cadeia, sem dado pessoal: quantas, sob qual versão, sucedendo qual
            # (FR-5431).
            reason=_narrativa(publicacao, anterior),
            idempotency_key=idempotency_key,
        )
        finish(reserva, publicacao, 201)
        return publicacao


def _prazo(afericao, escolha, agora):
    """O prazo de recurso do preliminar, validado e pronto para congelar (FR-5413, FR-5414)."""
    vazio = {"admite": None, "evento_id": None, "ate": None, "publico": None}
    if afericao.natureza != dominio.PRELIMINAR:
        return vazio
    escolha = (escolha or "").strip()
    if not escolha:
        raise DomainError(
            "inscricoes_prazo_obrigatorio",
            MENSAGENS["inscricoes_prazo_obrigatorio"],
            422,
            campo="prazo",
        )
    if escolha == SEM_RECURSO:
        return {**vazio, "admite": False, "publico": {"admite": False}}
    evento = next((item for item in afericao.eventos if item["id"] == escolha), None)
    if evento is None or evento["fim"] < agora:
        raise DomainError(
            "inscricoes_prazo_invalido", MENSAGENS["inscricoes_prazo_invalido"], 422, campo="prazo"
        )
    return {
        "admite": True,
        "evento_id": evento["id"],
        "ate": evento["fim"],
        "publico": {"admite": True, "evento": evento["nome"], "ate": evento["fim"].isoformat()},
    }


def _sucede(anterior, motivo):
    if anterior is None:
        return None
    return {
        "natureza": anterior.natureza,
        "natureza_rotulo": dominio.ROTULOS[anterior.natureza],
        "publicado_em": anterior.publicado_em.isoformat(),
        **({"motivo": motivo} if motivo else {}),
    }


def _documento(conteudo):
    from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
        render_inscricoes_pdf,
    )

    return render_inscricoes_pdf(conteudo)


def _resumo(dados):
    import hashlib

    return hashlib.sha256(dados).hexdigest()


def _narrativa(publicacao, anterior):
    partes = [
        f"{dominio.ROTULOS[publicacao.natureza]} publicada com "
        f"{publicacao.quantidade} inscrição(ões)",
        f"sob a versão normativa {publicacao.versao_id}",
    ]
    if anterior is not None:
        partes.append(f"sucedendo a publicação {anterior.id}")
    return ", ".join(partes) + "."


def _nao_encontrado():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def instante(texto):
    """O instante ISO congelado, de volta a `datetime` — para as telas que o formatam."""
    return parse_datetime(texto or "")


__all__ = [
    "Afericao",
    "OPERACAO",
    "PERMISSAO",
    "SEM_RECURSO",
    "aferir",
    "assinatura_da_previa",
    "cadeia",
    "divergencia_do_vigente",
    "documento_publico",
    "etapa_da_cadeia",
    "projetar_agora",
    "publica",
    "publicar_inscricoes",
    "recurso_ate_do_preliminar",
    "situacao_publicada",
    "vigente",
]
