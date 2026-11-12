"""A destinação da vaga reservada sem quem a ocupe: a leitura, a prévia e o ato (155, US1, R-001).

**A destinação é ato próprio, e não efeito da apuração** (155, D-001, D-005, FR-6308). A apuração
informa a ocupação; quem move a vaga é a presidência, depois de ver origem, destino, quantidade e a
frase que o Edital publicou. O ato grava o mesmo `MovimentoDeVaga` que a apuração gravava — a conta
da ocupação já o sabe ler, e o movimento antigo e o novo contam igual (FR-6316).

**A autoridade é a de quem apura, e nenhuma nova** (FR-6341): o mesmo `comando_de_comissao` da
emissão — transação, Processo travado, gestão da comissão e reserva da chave. É a trava do Processo
que faz duas confirmações simultâneas darem um registro só (FR-6314): a segunda lê, sob a trava, o
movimento da primeira e a sucessora que ela emitiu, e o saldo é zero.

**Este módulo não conhece a condução** (FR-6344, `UX-034` da `016`). O que só a divulgação, os
recursos e a condução respondem — o resultado é definitivo? corre prazo? alguém foi chamado para a
vaga e ainda não respondeu? — chega por `fatos_externos`, um *callable* que a interface compõe, como
`pessoas_chamadas` no acréscimo (155, R-004). O ato o chama **sob a trava**: calculado na tela,
seria um fato velho no instante do ato.

**Só o esgotamento** (155, R-010). Sob a reversão por saldo, o ato recusa com
`reversao_por_saldo_aguarda_decisao`, e a emissão continua movendo vaga como antes: é a parada da
parte que a decisão do usuário governa, e não regra adotada.
"""

from django.db import transaction

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.corte import admite_continuacao, regra_do_marco
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.ocupacao.application import efeitos as efeitos_de_ocupacao
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import (
    _edital_do_processo,
    conferir_limite,
    emitir_sucessora_por_efeito,
)
from processo_seletivo.ocupacao.domain import apuracao as calculo
from processo_seletivo.ocupacao.domain import destinacao as conta
from processo_seletivo.ocupacao.domain import nomes, reversao
from processo_seletivo.ocupacao.models import MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256

DESTINAR = "OCUPACAO_DESTINAR_VAGA"
DECLARAR_NAO_PREENCHIDA = "OCUPACAO_DECLARAR_NAO_PREENCHIDA"
DESFAZER_DESTINACAO = "OCUPACAO_DESFAZER_DESTINACAO"
DESFAZER_NAO_PREENCHIDA = "OCUPACAO_DESFAZER_NAO_PREENCHIDA"
DESFAZIMENTO_IMPEDIDO = "OCUPACAO_DESFAZIMENTO_IMPEDIDO"
ATO_DE_DESTINAR = "ocupacao:destinar_vaga"
ATO_DE_DECLARAR = "ocupacao:declarar_nao_preenchida"
ATO_DE_DESFAZER_DESTINACAO = "ocupacao:desfazer_destinacao"
ATO_DE_DESFAZER_NAO_PREENCHIDA = "ocupacao:desfazer_nao_preenchida"


# --- A leitura ---------------------------------------------------------------------------------


def frase_publicada(versao, declaracao):
    """A frase da reversão como a versão a publicou, na redação do documento dela (FR-6309).

    **A redação é a da Publicação que a versão cita**, e não a de hoje: um Edital publicado antes da
    `069` publicou a redação 1, e citar a 2 no fundamento do ato seria citar texto que ele não tem.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import frase_da_reversao

    if not declaracao:
        return ""
    origem = getattr(versao, "source_publication", None)
    redacao = getattr(origem, "redacao_do_documento", None)
    return (
        frase_da_reversao(declaracao, redacao=redacao) if redacao else frase_da_reversao(declaracao)
    )


def leitura_da_vaga(*, edital, perfil_id, marco_id, lista_id, fatos_externos=None, at=None):
    """A situação da vaga do recorte, com tudo o que a conferência e o ato leem (155, R-004).

    `fatos_externos(edital=, perfil_id=, marco_id=, lista_id=, etapa_governada_id=, eliminados=,
    at=)` devolve o dicionário dos fatos que só outros módulos respondem (ver
    `domain.destinacao.impedimentos`), e mais `chamados` — as inscrições chamadas para a vaga e sem
    desfecho. `None` é ninguém para perguntar: a prévia da classificação e a equivalência dela leem
    só a condição (`quantidadePelaCondicao`), que não depende deles.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    perfil = por_identidade((versao.content or {}).get("profiles"), perfil_id) or {}
    declaracao = reversao.declarada(perfil)
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    movimentos = selectors._movimentos_que_alcancam(
        edital=edital, perfil=perfil_id, marco=marco_id, lista=lista_id
    )
    declaracoes = selectors.nao_preenchidas_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    base = {
        "versao": versao,
        "declaracao": declaracao,
        "frase": frase_publicada(versao, declaracao),
        "listaId": lista_id,
        "apuracao": vigente,
        "movimentos": movimentos,
        "destinadas": _destinadas(movimentos, lista_id),
        # **As declarações de hoje, cada uma com o que ainda tem a desfazer** (155, FR-6326): a
        # tela as mostra como "não preenchida", e a conta da apuração as lê pelos ids congelados.
        "naoPreenchidas": _com_o_restante(declaracoes),
        "declaradas": calculo.saldo_das_nao_preenchidas(
            (d.especie, d.quantidade) for d in declaracoes
        ),
    }
    if vigente is None:
        # **A lista de sorteio sem relação, com a ausência comprovada** (155, D-011, FR-6332): a
        # vaga dela não precisa de apuração, e a leitura vem do quadro e dos atos da vaga. Fora
        # dela, sem apuração não há saldo afirmado: nada a destinar nem a declarar (FR-6333).
        ausencia = _ausencia(
            fatos_externos,
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            at=at,
        )
        if ausencia is not None and ausencia["comprovada"]:
            return _leitura_sem_relacao(
                base,
                ausencia,
                perfil=perfil,
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                fatos_externos=fatos_externos,
                at=at,
            )
        situacao = conta.situacao(
            declaracao=declaracao,
            lista_id=lista_id,
            saldo=None,
            destinadas=base["destinadas"],
        )
        return {
            **base,
            "ausencia": ausencia,
            "situacao": situacao,
            "quantidadePelaCondicao": 0,
            "restantes": [],
        }

    causas = selectors.causas_de_obsolescencia(vigente, at=at)
    saldo = calculo.faltando(
        efetivas=vigente.efetivas,
        ocupadas=vigente.ocupadas,
        nao_preenchidas=vigente.nao_preenchidas,
    )
    fatos = _condicao(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        versao=versao,
        efetivas=vigente.efetivas,
    )
    externos = (
        fatos_externos(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            etapa_governada_id=fatos["etapaGovernada"],
            eliminados=fatos["eliminados"],
            at=at,
        )
        if fatos_externos is not None
        else {}
    )
    # **Os inabilitados só saem da conta com o prazo e os recursos da eliminação fechados** (155,
    # D-007): enquanto o recurso pode devolvê-los à lista, a vaga não é "sem quem a ocupe", e o
    # impedimento diz até quando.
    inabilitados = (
        set()
        if externos.get("prazo_da_eliminacao_ate") or externos.get("recursos_da_eliminacao")
        else fatos["eliminados"]
    )
    restantes = conta.quem_ainda_pode_ocupar(
        posicoes=fatos["posicoes"],
        excluidos=fatos["excluidos"],
        ocupam_a_ampla_confirmados=fatos["confirmadosNaAmpla"],
        alcancaveis=fatos["alcancaveis"],
        inabilitados=inabilitados,
        ocupantes=fatos["ocupantes"],
    )
    pela_condicao = conta.quem_ainda_pode_ocupar(
        posicoes=fatos["posicoes"],
        excluidos=fatos["excluidos"],
        ocupam_a_ampla_confirmados=fatos["confirmadosNaAmpla"],
        alcancaveis=fatos["alcancaveis"],
        inabilitados=fatos["eliminados"],
        ocupantes=fatos["ocupantes"],
    )
    chamados = {conta.chave(i) for i in externos.get("chamados") or ()}
    sem_confirmacao = fatos["semConfirmacaoNaAmpla"]
    # O eliminado com recurso possível é pendente, e não livre: a vaga não é dele agora, e o caminho
    # não é chamá-lo — é esperar o prazo ou a decisão que o impedimento nomeia (US3.5).
    em_recurso = fatos["eliminados"] - inabilitados
    impedimentos = conta.impedimentos(
        {
            **externos,
            "ocupam_a_ampla_sem_confirmacao": len(sem_confirmacao),
            "apuracao_obsoleta": bool(causas),
        }
    )
    situacao = conta.situacao(
        declaracao=declaracao,
        lista_id=lista_id,
        saldo=saldo,
        restantes=restantes,
        pendentes=chamados | sem_confirmacao | em_recurso,
        impedimentos=impedimentos,
        destinadas=base["destinadas"],
    )
    return {
        **base,
        "causas": causas,
        "saldo": saldo,
        "situacao": situacao,
        "restantes": restantes,
        # **A condição sozinha, sem os impedimentos** (155, R-011): é o que a prévia da
        # classificação e a do sorteio fazem sobre a ordem fictícia, onde não há desfecho, recurso
        # nem chamada a simular; a equivalência delas com o caminho oficial lê este número.
        # A linha geral não é origem de destinação (D-014): a vaga dela é a da declaração de não
        # preenchida, e a prévia não tem o que simular ali.
        "quantidadePelaCondicao": conta.quantidade_destinavel(
            gatilho=reversao.especie_que_move(perfil),
            saldo=saldo,
            ainda_podem_ocupar=len(pela_condicao),
        )
        if lista_id is not None
        else 0,
    }


def _ausencia(fatos_externos, *, edital, perfil_id, marco_id, lista_id, at):
    """A ausência de concorrente lida na relação definitiva pertinente, ou `None` (155, R-007).

    **Pergunta à interface, e não ao sorteio**: a ocupação não importa o sorteio, e a composição
    dos fatos externos já é quem lê o que outros módulos respondem (R-004). Quem a injeta sem a
    pergunta — a prévia da classificação, um *callable* de teste — não tem lista de sorteio sem
    relação, e recebe `None`: a ausência de registro não é lida como lista vazia (FR-6333).
    """
    if lista_id is None or fatos_externos is None:
        return None
    perguntar = getattr(fatos_externos, "ausencia_de_concorrente", None)
    if perguntar is None:
        return None
    return perguntar(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=at
    )


#: Os impedimentos que são do resultado **da lista**, e que a lista sem relação não tem: não houve
#: sorteio, nem publicação, nem prazo contra ela. A prova da ausência é a relação definitiva da
#: ampla (155, FR-6332); os demais impedimentos da FR-6306 continuam valendo.
_SO_DO_RESULTADO_DA_LISTA = frozenset({conta.RESULTADO_NAO_DEFINITIVO, conta.PRAZO_RECURSAL_ABERTO})


def _leitura_sem_relacao(
    base, ausencia, *, perfil, edital, perfil_id, marco_id, lista_id, fatos_externos, at
):
    """A vaga da lista de sorteio comprovadamente sem concorrente, **sem apuração** (155, R-007).

    As efetivas são as da conta da apuração (`apuracao.apurar`) sem ninguém na ordem: as publicadas
    no quadro, as acrescidas, e os movimentos que a alcançam — o que a destinação cedeu sai daqui,
    e é por isso que, destinada, a vaga não é oferecida de novo (FR-6314). Ninguém ocupa: não há
    quem concorra, e a relação congelada o comprova.
    """
    from processo_seletivo.classificacao.application.corte import linha_do_quadro
    from processo_seletivo.ocupacao.domain import acrescimo as conta_do_acrescimo

    versao = base["versao"]
    publicadas = selectors._quantidade(
        linha_do_quadro(versao.content, perfil_id=perfil_id, lista_id=lista_id)
    )
    if publicadas is None:
        # Sem quadro não há quantidade a afirmar (UX-032 da `016`): a ausência continua dita, e
        # nenhum ato é oferecido.
        situacao = conta.situacao(
            declaracao=base["declaracao"],
            lista_id=lista_id,
            saldo=None,
            destinadas=base["destinadas"],
        )
        return {**base, "ausencia": ausencia, "situacao": situacao, "restantes": []}
    acrescimos = selectors.acrescimos_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    recebidas, cedidas = calculo.recebidas_e_cedidas(
        (m.especie, calculo.mesma_lista(m.destino_lista_id, lista_id), m.quantidade)
        for m in base["movimentos"]
    )
    efetivas = (
        int(publicadas)
        + recebidas
        - cedidas
        + conta_do_acrescimo.saldo((a.especie, a.quantidade) for a in acrescimos)
    )
    saldo = calculo.faltando(efetivas=efetivas, ocupadas=0, nao_preenchidas=base["declaradas"])
    externos = (
        fatos_externos(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            etapa_governada_id=None,
            eliminados=(),
            at=at,
        )
        if fatos_externos is not None
        else {}
    )
    impedimentos = [
        i for i in conta.impedimentos(externos) if i.codigo not in _SO_DO_RESULTADO_DA_LISTA
    ]
    situacao = conta.situacao(
        declaracao=base["declaracao"],
        lista_id=lista_id,
        saldo=saldo,
        restantes=[],
        impedimentos=impedimentos,
        destinadas=base["destinadas"],
    )
    return {
        **base,
        "ausencia": ausencia,
        "causas": [],
        "saldo": saldo,
        "publicadas": publicadas,
        "efetivas": efetivas,
        "situacao": situacao,
        "restantes": [],
        "quantidadePelaCondicao": conta.quantidade_destinavel(
            gatilho=reversao.especie_que_move(perfil), saldo=saldo, ainda_podem_ocupar=0
        ),
    }


def _efetivas(leitura):
    """As efetivas que a conferência mostra: as da apuração, ou as da conta sem ela (R-007)."""
    if leitura["apuracao"] is not None:
        return leitura["apuracao"].efetivas
    return leitura.get("efetivas")


def _sem_relacao(leitura):
    """A leitura é a da lista de sorteio sem relação, com a ausência comprovada (R-007)."""
    ausencia = leitura.get("ausencia")
    return bool(ausencia and ausencia.get("comprovada")) and leitura["apuracao"] is None


def _condicao(*, edital, perfil_id, marco_id, lista_id, versao, efetivas):
    """Os fatos da ocupação que a condição da FR-6304 lê, consultados uma vez por recorte."""
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    posicoes = [(p.inscricao_id, p.posicao) for p in ato.posicoes.all()] if ato else []
    membros = {conta.chave(i) for i, _ in posicoes}
    progrediram, corte, empates = selectors.progrediram_em_ordem(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    habilitadas = selectors.habilitadas_pelo_corte(
        edital=edital, corte=corte, progrediram=progrediram
    )
    efeitos = efeitos_de_ocupacao.efeitos_lidos_por(
        efeitos_de_ocupacao.efeitos_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
        )
    )
    da_ampla = efeitos_de_ocupacao.efeitos_lidos_por(
        efeitos_de_ocupacao.efeitos_do_recorte(
            edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
        )
    )
    try:
        # **Na linha geral, ninguém "ocupa a ampla" à parte** (155, D-014): a concorrência
        # concomitante é pergunta da reserva, e na ampla quem a ocupa é o titular dela mesma — a
        # conta de `ocupantes`, abaixo. É o que a emissão faz (`emissao._apurar`).
        ocupantes_da_ampla = (
            {
                conta.chave(i)
                for i in selectors.ocupantes_da_ampla(
                    edital=edital, perfil_id=perfil_id, marco_id=marco_id, versao=versao
                )
            }
            if lista_id is not None
            else set()
        )
    except calculo.EmpateNaFronteiraDoAlvo:
        # A ampla não apura com o empate não julgado, e a reserva também não: a vigente dela está
        # obsoleta, e a causa impede o ato. Ninguém conta como ocupante da ampla, e a conta segue.
        ocupantes_da_ampla = set()
    confirmados = conta.incluidos_por_efeito(da_ampla) & membros if lista_id is not None else set()
    # **Os ocupantes da reserva, pela conta da apuração** (`apuracao.titulares_iniciais` e
    # `ocupantes`), sobre as efetivas que a vigente gravou: a pergunta é se há alguém para a vaga
    # que **sobra**, e quem já ocupa outra não responde por ela.
    try:
        titulares = calculo.titulares_iniciais(
            progrediram_em_ordem=progrediram,
            efetivas=efetivas,
            ocupantes_da_ampla=ocupantes_da_ampla,
            empates_residuais=empates,
            habilitadas=habilitadas,
        )
    except calculo.EmpateNaFronteiraDoAlvo:
        # A apuração vigente não seria emitida hoje: ela está obsoleta, e a causa impede o ato.
        titulares = []
    ocupantes = calculo.ocupantes(
        titulares=titulares, habilitadas=habilitadas, efeitos_lidos=efeitos
    )
    regra = regra_do_marco(versao.content, perfil_id=perfil_id, marco_id=marco_id)
    # **Alcançável é quem a faixa alcançou, ou a ordem inteira** quando o Edital admite continuação
    # (FR-6304) — e mais quem entrou por efeito: a pessoa chamada além da faixa foi alcançada.
    alcancaveis = (
        None
        if admite_continuacao(regra)
        else {conta.chave(i) for i in progrediram} | conta.incluidos_por_efeito(efeitos)
    )
    etapa = corte.etapa_governada_id if corte is not None else None
    # **`vigentes`, e não `objects`** — a varredura `test_vigencia_do_resultado.py` o cobra: o
    # Resultado superado por recurso deferido não elimina mais ninguém.
    eliminados = (
        {
            conta.chave(r.inscricao_id)
            for r in ResultadoEtapa.vigentes.filter(
                edital=edital,
                etapa_id=etapa,
                inscricao_id__in=[i for i, _ in posicoes],
                consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
            )
        }
        if etapa is not None and posicoes
        else set()
    )
    return {
        "posicoes": posicoes,
        "excluidos": conta.excluidos_por_efeito(efeitos),
        "confirmadosNaAmpla": confirmados,
        "semConfirmacaoNaAmpla": (ocupantes_da_ampla & membros) - confirmados,
        "alcancaveis": alcancaveis,
        "eliminados": eliminados,
        "ocupantes": ocupantes,
        "etapaGovernada": etapa,
    }


def _destinadas(movimentos, lista_id):
    """O saldo do que a reserva cedeu à ampla — pelo movimento antigo ou pelo ato (FR-6316)."""
    if lista_id is None:
        return 0
    total = 0
    for movimento in movimentos:
        if calculo.mesma_lista(movimento.origem_lista_id, lista_id):
            total += movimento.quantidade
        elif calculo.mesma_lista(movimento.destino_lista_id, lista_id):
            total -= movimento.quantidade
    return max(total, 0)


# --- A prévia ----------------------------------------------------------------------------------


def previa_da_destinacao(*, edital, perfil_id, marco_id, lista_id, fatos_externos, at=None):
    """O que o ato faria agora, e a recusa que daria — **sem gravar nada** (FR-6309, UX-601)."""
    leitura = leitura_da_vaga(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=fatos_externos,
        at=at,
    )
    situacao = leitura["situacao"]
    ampla = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None
    )
    quantidade = situacao["quantidade"] if situacao["estado"] == conta.DESTINACAO_DISPONIVEL else 0
    return {
        **leitura,
        "quantidade": quantidade,
        "recusa": _recusa(leitura),
        "ampla": ampla,
        "efetivasAntes": _efetivas(leitura),
        "amplaDepois": (ampla.efetivas + quantidade) if ampla is not None else None,
        "origemDepois": (
            leitura["apuracao"].efetivas - quantidade
            if leitura["apuracao"] is not None
            else (leitura["efetivas"] - quantidade if _sem_relacao(leitura) else None)
        ),
        # **A assinatura cobre o que o ato lê** (FR-6342): a apuração, os movimentos, a versão e a
        # declaração. Qualquer um que mude entre a conferência e o clique é leitura nova, e o ato
        # recusa com `leitura_do_recorte_mudou` em vez de confirmar o que a pessoa não viu.
        "assinatura": canonical_sha256(
            {
                "gesto": "destinacao",
                "apuracao": str(leitura["apuracao"].id) if leitura["apuracao"] else None,
                # A relação que comprova a ausência (R-007): sucedida, a prova é outra.
                "relacao": (leitura.get("ausencia") or {}).get("relacao"),
                "movimentos": [str(m.id) for m in leitura["movimentos"]],
                "versao": str(leitura["versao"].id),
                "declaracao": leitura["declaracao"],
                "quantidade": quantidade,
            }
        ),
    }


def _recusa(leitura):
    """`(codigo, frase)` da recusa que o ato daria, na ordem do contrato, ou `None` (FR-6312)."""
    situacao = leitura["situacao"]
    declaracao = leitura["declaracao"]
    if declaracao is None:
        return (
            nomes.SEM_REVERSAO_DECLARADA,
            "Este Edital não declara o que acontece com a vaga reservada não preenchida: sem a "
            "declaração, nenhum ato a move para a ampla concorrência.",
        )
    if declaracao == nomes.PASSAGEM_ENTRE_COTAS:
        return (
            nomes.RECUSA_PASSAGEM_ENTRE_COTAS,
            "Este Edital manda a vaga passar antes por outras cotas, e o GPS ainda não aplica essa "
            "ordem: a vaga não vai direto à ampla concorrência.",
        )
    if declaracao == nomes.REVERSAO_POR_SALDO:
        # **Sem frase sobre decisões** na tela: a recusa diz o que o ato não faz aqui, e a tela não
        # chega a oferecê-lo.
        return (
            nomes.REVERSAO_POR_SALDO_AGUARDA_DECISAO,
            "A destinação por ato próprio não se aplica à reversão pelo saldo não preenchido.",
        )
    if leitura["apuracao"] is None and leitura.get("saldo") is None:
        return (nomes.SEM_SALDO_A_DESTINAR, _sem_apuracao(leitura, "destinar"))
    if situacao["estado"] == conta.IMPEDIDA and situacao["impedimentos"]:
        primeiro = situacao["impedimentos"][0]
        return (nomes.DESTINACAO_IMPEDIDA, _frase_do_impedimento(primeiro))
    if not leitura["saldo"]:
        return (
            nomes.SEM_SALDO_A_DESTINAR,
            "Esta lista não tem vaga a ocupar"
            + (": a vaga já foi destinada à ampla concorrência." if leitura["destinadas"] else "."),
        )
    if situacao["aindaPodemOcupar"]:
        quantas = situacao["aindaPodemOcupar"]
        return (
            nomes.AINDA_HA_QUEM_OCUPAR,
            f"Ainda há {quantas} pessoa{'s' if quantas != 1 else ''} na ordem desta lista que "
            f"{'podem' if quantas != 1 else 'pode'} ocupar a vaga: a lista não está esgotada.",
        )
    if situacao["estado"] != conta.DESTINACAO_DISPONIVEL:
        return (
            nomes.DESTINACAO_IMPEDIDA,
            "A vaga desta lista não está disponível para destinação.",
        )
    return None


def _sem_apuracao(leitura, gesto):
    """Por que a lista sem apuração não tem vaga afirmada — e, no sorteio, o que falta (FR-6333)."""
    ausencia = leitura.get("ausencia") or {}
    if ausencia.get("frase"):
        return ausencia["frase"]
    return f"Esta lista ainda não tem apuração: não há vaga a ocupar afirmada para {gesto}."


def _frase_do_impedimento(impedimento):
    from processo_seletivo.shared.tempo import ZONA

    frase = impedimento.frase[:1].upper() + impedimento.frase[1:]
    if impedimento.ate is not None:
        frase += f", até {impedimento.ate.astimezone(ZONA).strftime('%d/%m/%Y às %Hh%M')}"
    return frase + "."


# --- O ato -------------------------------------------------------------------------------------


def destinar_vaga(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    lista_id,
    assinatura,
    fatos_externos,
    idempotency_key,
    correlation_id,
):
    """Grava a destinação e emite a sucessora da apuração de origem, num *savepoint* (FR-6310)."""
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
        operation=ATO_DE_DESTINAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil, marco = identificador(perfil_id), identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        # **Os fatos externos são reavaliados aqui, sob a trava** (155, R-004): a chamada aberta ou
        # o recurso interposto entre a conferência e o clique impedem o ato que a tela ofereceu.
        previa = previa_da_destinacao(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            fatos_externos=fatos_externos,
            at=ctx.now,
        )
        if previa["recusa"] is not None:
            codigo, frase = previa["recusa"]
            raise DomainError(codigo, frase, 409)
        if (assinatura or "") != previa["assinatura"]:
            raise DomainError(
                nomes.LEITURA_DO_RECORTE_MUDOU,
                "As vagas desta lista mudaram desde que a conferência foi aberta: confira de novo "
                "antes de confirmar.",
                409,
            )
        quantidade = previa["quantidade"]
        versao = previa["versao"]
        movimento = MovimentoDeVaga.objects.create(
            # A apuração **lida** pelo ato, e não a que o causou (155, R-001): reproduzir o ato é
            # reler esta, com a versão e a frase que ele citou (FR-6342).
            apuracao=previa["apuracao"],
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            especie=nomes.MOVIMENTO_REVERSAO,
            origem_lista_id=lista,
            destino_lista_id=None,
            quantidade=quantidade,
            causa=(
                f"Destinação à ampla concorrência por ato próprio: {quantidade} de "
                f"{_publicadas(previa)}."
            ),
            gatilho=previa["declaracao"],
            fundamento=_fundamento(previa),
            versao=versao,
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        seguinte = (
            _SEM_APURACAO_A_SUCEDER
            if _sem_relacao(previa)
            else _emitir_seguinte(
                ctx,
                actor,
                edital=edital,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                motivo=f"Destinação de {quantidade} vaga(s) à ampla concorrência.",
                correlation_id=correlation_id,
            )
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=DESTINAR,
            aggregate=movimento,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=_razao(movimento, previa, seguinte),
            idempotency_key=idempotency_key,
        )
        declarado = {
            "movimento": str(movimento.id),
            "quantidade": quantidade,
            "gatilho": movimento.gatilho,
            **seguinte,
        }
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _fundamento(previa):
    """A frase publicada e a versão que a disse — o que a FR-6310 manda registrar."""
    from processo_seletivo.shared.tempo import ZONA

    versao = previa["versao"]
    return (
        f"{previa['frase']} (versão do Edital vigente desde "
        f"{versao.valid_from.astimezone(ZONA).strftime('%d/%m/%Y %H:%M')})"
    )


def _emitir_seguinte(
    ctx,
    actor,
    *,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    motivo,
    correlation_id,
    causa_do_ato=nomes.CAUSA_MOVIMENTO_POSTERIOR,
):
    """A sucessora da apuração do recorte, ou o que a impede — o molde do acréscimo (`T-004`).

    **Só quando o ato é a única causa** (`causa_do_ato`: o movimento, ou a declaração de não
    preenchida): o ato só é aceito sobre apuração vigente sem obsolescência, e a causa nova é a
    dele. Num *savepoint*: a recusa da emissão não desfaz o ato, que aconteceu, e o recorte aparece
    obsoleto pela causa dita.
    """
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    causas = {c["causa"] for c in selectors.causas_de_obsolescencia(vigente, at=ctx.now)}
    if vigente is not None and causas - {causa_do_ato}:
        return _pendente(
            nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA,
            "A apuração desta lista já estava obsoleta por outra causa: emita a seguinte na "
            "ocupação, onde a causa é dita.",
        )
    try:
        with transaction.atomic():
            declarado = emitir_sucessora_por_efeito(
                actor=actor,
                permissao=ctx.base.permissao,
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=lista_id,
                motivo=motivo,
                now=ctx.now,
                correlation_id=correlation_id,
            )
    except DomainError as recusa:
        return _pendente(recusa.code, recusa.detail)
    if declarado is None:
        # Por esgotamento a emissão não move vaga desde a `155` (FR-6315): este ramo é guarda.
        return _pendente(nomes.OUTRA_CAUSA_DE_OBSOLESCENCIA, "A apuração seguinte moveria vaga.")
    return {"apuracaoSeguinte": declarado, "apuracaoPendente": None}


def _pendente(codigo, detalhe):
    return {"apuracaoSeguinte": None, "apuracaoPendente": {"codigo": codigo, "detalhe": detalhe}}


#: A lista de sorteio sem relação não tem apuração a suceder (R-007): o ato é a única leitura da
#: vaga dela, e a apuração da ampla, que recebe, fica obsoleta pelo movimento, como sempre.
_SEM_APURACAO_A_SUCEDER = _pendente(
    "sem_apuracao_de_origem",
    "esta lista não tem apuração — ninguém concorreu, como a relação da ampla concorrência "
    "comprova —, e não há apuração dela a suceder.",
)


def _publicadas(previa):
    """As vagas publicadas da lista lida: da apuração, ou do quadro na lista sem relação."""
    if previa["apuracao"] is not None:
        return previa["apuracao"].publicadas
    return previa.get("publicadas")


def _lida(previa):
    """O que a trilha diz que o ato leu: a apuração, ou a relação que comprovou a ausência."""
    if previa["apuracao"] is not None:
        return f"Apuração lida: {previa['apuracao'].id}"
    return (
        "Sem apuração: ausência de concorrente comprovada pela relação da ampla concorrência "
        f"{(previa.get('ausencia') or {}).get('relacao')}"
    )


def _razao(movimento, previa, seguinte):
    """O que a trilha guarda para reconstruir o ato sem abrir o banco (FR-6310, FR-6341)."""
    emitida = seguinte["apuracaoSeguinte"]
    return (
        f"Destinação de {movimento.quantidade} vaga(s) da lista {movimento.origem_lista_id} à "
        f"ampla concorrência, no marco {movimento.marco_id}, Perfil {movimento.perfil_id}, por "
        f"esgotamento. Fundamento: {movimento.fundamento}. "
        f"{_lida(previa)}; "
        + (
            f"sucessora: {emitida['id']}."
            if emitida
            else f"sucessora pendente: {seguinte['apuracaoPendente']['codigo']}."
        )
    )


def _com_o_restante(declaracoes):
    """Cada declaração de não preenchida com o que ainda tem a desfazer, numa passada (FR-6334).

    A forma de `selectors.com_o_restante` do acréscimo, com as espécies desta tabela: os
    desfazimentos citam a declaração pela FK, e a lista é a do recorte.
    """
    desfeitas = {}
    for registro in declaracoes:
        if registro.especie == nomes.NAO_PREENCHIDA_DESFAZIMENTO:
            desfeitas[registro.desfaz_id] = desfeitas.get(registro.desfaz_id, 0) + (
                registro.quantidade
            )
    return [
        {
            "registro": registro,
            "restante": max(registro.quantidade - desfeitas.get(registro.id, 0), 0)
            if registro.especie == nomes.NAO_PREENCHIDA_DECLARACAO
            else 0,
        }
        for registro in declaracoes
    ]


# --- A vaga não preenchida (155, US2, R-002) ----------------------------------------------------


def previa_da_nao_preenchida(*, edital, perfil_id, marco_id, lista_id, fatos_externos, at=None):
    """O que a declaração faria agora, e a recusa que daria — **sem gravar nada** (FR-6323).

    **A mesma leitura da destinação** (155, D-004): a condição, os impedimentos e o saldo são os
    da FR-6300, e o que muda é para onde a vaga vai — para lugar nenhum. A declaração não mexe nas
    efetivas (D-003): tira a vaga do "a ocupar", e a quantidade publicada continua a mesma.
    """
    leitura = leitura_da_vaga(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=fatos_externos,
        at=at,
    )
    situacao = leitura["situacao"]
    quantidade = (
        situacao["quantidade"] if situacao["estado"] == conta.NAO_PREENCHIDA_DISPONIVEL else 0
    )
    saldo = leitura.get("saldo")
    return {
        **leitura,
        "quantidade": quantidade,
        "recusa": _recusa_da_nao_preenchida(leitura),
        "efetivasAntes": _efetivas(leitura),
        "faltandoDepois": (saldo - quantidade) if saldo is not None else None,
        # **A assinatura cobre o que o ato lê** (FR-6342), como a da destinação, mais as
        # declarações do recorte: uma declaração feita por outra pessoa entre a conferência e o
        # clique é leitura nova.
        "assinatura": canonical_sha256(
            {
                "gesto": "nao_preenchida",
                "apuracao": str(leitura["apuracao"].id) if leitura["apuracao"] else None,
                "relacao": (leitura.get("ausencia") or {}).get("relacao"),
                "movimentos": [str(m.id) for m in leitura["movimentos"]],
                "naoPreenchidas": [str(d["registro"].id) for d in leitura["naoPreenchidas"]],
                "versao": str(leitura["versao"].id),
                "declaracao": leitura["declaracao"],
                "quantidade": quantidade,
            }
        ),
    }


def _recusa_da_nao_preenchida(leitura):
    """`(codigo, frase)` da recusa que a declaração daria, na ordem do contrato, ou `None`.

    **O que o Edital manda vem antes de tudo** (FR-6327): onde ele declara a reversão, a vaga que
    ninguém mais pode ocupar é destinada, e não declarada não preenchida; onde manda a passagem
    entre cotas, nenhum ato a leva a lugar nenhum. Só depois a condição e os impedimentos, que são
    os da destinação (FR-6323).
    """
    situacao = leitura["situacao"]
    declaracao = leitura["declaracao"]
    reservada = leitura["listaId"] is not None
    if declaracao == nomes.PASSAGEM_ENTRE_COTAS:
        return (
            nomes.RECUSA_PASSAGEM_ENTRE_COTAS,
            "Este Edital manda a vaga passar antes por outras cotas, e o GPS ainda não aplica essa "
            "ordem: a vaga não é declarada não preenchida.",
        )
    if declaracao == nomes.REVERSAO_POR_SALDO:
        # A mesma frase da destinação (155, R-010): o saldo fica como estava, sem ato novo.
        return (
            nomes.REVERSAO_POR_SALDO_AGUARDA_DECISAO,
            "A destinação por ato próprio não se aplica à reversão pelo saldo não preenchido.",
        )
    if reservada and declaracao == nomes.REVERSAO_POR_ESGOTAMENTO:
        return (
            nomes.O_EDITAL_MANDA_DESTINAR,
            "Este Edital declara para onde vai a vaga desta lista que ninguém mais pode ocupar"
            + (f": «{leitura['frase']}»" if leitura["frase"] else "")
            + ". O caminho é a destinação à ampla concorrência, e não a declaração de vaga não "
            "preenchida.",
        )
    if leitura["apuracao"] is None and leitura.get("saldo") is None:
        return (nomes.SEM_SALDO_A_DESTINAR, _sem_apuracao(leitura, "declarar não preenchida"))
    if situacao["estado"] == conta.IMPEDIDA and situacao["impedimentos"]:
        return (nomes.DESTINACAO_IMPEDIDA, _frase_do_impedimento(situacao["impedimentos"][0]))
    if not leitura["saldo"]:
        return (
            nomes.SEM_SALDO_A_DESTINAR,
            "Esta lista não tem vaga a ocupar"
            + (": a vaga já foi declarada não preenchida." if leitura["declaradas"] else "."),
        )
    if situacao["aindaPodemOcupar"]:
        quantas = situacao["aindaPodemOcupar"]
        return (
            nomes.AINDA_HA_QUEM_OCUPAR,
            f"Ainda há {quantas} pessoa{'s' if quantas != 1 else ''} na ordem desta lista que "
            f"{'podem' if quantas != 1 else 'pode'} ocupar a vaga: ela não é declarada não "
            "preenchida enquanto houver.",
        )
    if situacao["estado"] != conta.NAO_PREENCHIDA_DISPONIVEL:
        return (
            nomes.DESTINACAO_IMPEDIDA,
            "A vaga desta lista não está disponível para a declaração de não preenchida.",
        )
    return None


def declarar_nao_preenchida(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    lista_id,
    fundamento,
    assinatura,
    fatos_externos,
    idempotency_key,
    correlation_id,
):
    """Grava a declaração de vaga não preenchida e a sucessora do recorte (FR-6323, FR-6325).

    **Nunca por padrão nem por efeito de outro ato** (FR-6323): só aqui, com o fundamento escrito
    por quem declara. O fundamento não move a vaga para lugar nenhum (FR-6320, D-006) — ele diz por
    que a vaga fica sem ocupante, e o que o Edital manda continua sendo lido na declaração dele.
    """
    texto = (fundamento or "").strip()
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "fundamento": texto,
        "leitura": assinatura or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_DECLARAR,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        if not texto:
            raise DomainError(
                nomes.FUNDAMENTO_OBRIGATORIO,
                "Diga por que a vaga fica sem ocupante: a declaração exige fundamento escrito.",
                422,
                campo="fundamento",
            )
        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil, marco = identificador(perfil_id), identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        previa = previa_da_nao_preenchida(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            fatos_externos=fatos_externos,
            at=ctx.now,
        )
        if previa["recusa"] is not None:
            codigo, frase = previa["recusa"]
            raise DomainError(codigo, frase, 409)
        if (assinatura or "") != previa["assinatura"]:
            raise DomainError(
                nomes.LEITURA_DO_RECORTE_MUDOU,
                "As vagas desta lista mudaram desde que a conferência foi aberta: confira de novo "
                "antes de confirmar.",
                409,
            )
        quantidade = previa["quantidade"]
        apuracao = previa["apuracao"]
        sem_relacao = _sem_relacao(previa)
        conferir_limite(
            efetivas=previa["efetivas"] if sem_relacao else apuracao.efetivas,
            ocupadas=0 if sem_relacao else apuracao.ocupadas,
            nao_preenchidas=(previa["declaradas"] if sem_relacao else apuracao.nao_preenchidas)
            + quantidade,
        )
        registro = VagaNaoPreenchida.objects.create(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            # A apuração **lida** (FR-6342): reproduzir a declaração é reler esta, com a versão
            # que ela leu.
            apuracao=apuracao,
            especie=nomes.NAO_PREENCHIDA_DECLARACAO,
            quantidade=quantidade,
            fundamento=texto,
            versao=previa["versao"],
            registrado_por=str(getattr(actor, "subject", actor)),
            registrado_em=ctx.now,
        )
        seguinte = (
            _SEM_APURACAO_A_SUCEDER
            if sem_relacao
            else _emitir_seguinte(
                ctx,
                actor,
                edital=edital,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                motivo=f"Declaração de {quantidade} vaga(s) não preenchida(s). Fundamento: {texto}",
                correlation_id=correlation_id,
                causa_do_ato=nomes.CAUSA_DECLARACAO_POSTERIOR,
            )
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=DECLARAR_NAO_PREENCHIDA,
            aggregate=registro,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                f"Declaração de {quantidade} vaga(s) não preenchida(s) na lista "
                f"{lista or 'ampla concorrência'}, no marco {marco}, Perfil {perfil}. "
                f"Fundamento: {texto}. {_lida(previa)}; " + _sucessora_na_razao(seguinte)
            ),
            idempotency_key=idempotency_key,
        )
        declarado = {"naoPreenchida": str(registro.id), "quantidade": quantidade, **seguinte}
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def _sucessora_na_razao(seguinte):
    emitida = seguinte["apuracaoSeguinte"]
    return (
        f"sucessora: {emitida['id']}."
        if emitida
        else f"sucessora pendente: {seguinte['apuracaoPendente']['codigo']}."
    )


# --- Os desfazimentos (155, US6, R-005) ---------------------------------------------------------


def previa_do_desfazimento_da_destinacao(*, edital, movimento_id, chamadas_dependentes, at=None):
    """O que o desfazimento da destinação faria agora, e a recusa que daria (FR-6334, FR-6335).

    `chamadas_dependentes(edital=, perfil_id=, marco_id=, lista_id=, movimento_id=,
    nao_preenchida_id=, at=)` devolve `[{"id", "rotulo", "ocupa"}]`: as chamadas no recorte de
    destino cuja apuração leu este movimento, e que ainda respondem pela vaga. É a pergunta que só
    a condução responde, e chega como argumento (R-005) — esta feature não a conhece.
    """
    movimento = _destinacao_do_edital(edital, movimento_id)
    perfil_id, marco_id = movimento.perfil_id, movimento.marco_id
    dependentes = list(
        chamadas_dependentes(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=movimento.destino_lista_id,
            movimento_id=movimento.id,
            nao_preenchida_id=None,
            at=at,
        )
        or []
    )
    origem = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=movimento.origem_lista_id
    )
    destino = selectors.apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=movimento.destino_lista_id
    )
    desfeito = movimento.desfazimentos.exists()
    declarada = _declaracao_que_leu(edital, movimento)
    recusa = None
    if desfeito:
        recusa = (nomes.ATO_JA_DESFEITO, "Esta destinação já foi desfeita.")
    elif declarada:
        recusa = (
            nomes.DESTINACAO_COM_DECLARACAO_DEPENDENTE,
            "A vaga destinada foi declarada não preenchida na ampla concorrência depois de "
            "recebida: desfaça antes essa declaração, com motivo, e então a destinação.",
        )
    elif dependentes:
        recusa = (nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE, _frase_dos_dependentes(dependentes))
    return {
        "movimento": movimento,
        "versao": effective_version(edital_id=edital.id, at=at),
        "origem": origem,
        "destino": destino,
        "dependentes": dependentes,
        "recusa": recusa,
        "assinatura": canonical_sha256(
            {
                "gesto": "desfazer_destinacao",
                "movimento": str(movimento.id),
                "desfeito": desfeito,
                "origem": str(origem.id) if origem else None,
                "destino": str(destino.id) if destino else None,
                "dependentes": [str(d.get("id")) for d in dependentes],
            }
        ),
    }


def desfazer_destinacao(
    *,
    actor,
    processo_id,
    edital_id,
    movimento_id,
    motivo,
    assinatura,
    chamadas_dependentes,
    idempotency_key,
    correlation_id,
):
    """O ato contrário à destinação, citando-a, ou a recusa registrada (FR-6334 a FR-6336).

    **Com chamada dependente, a recusa fica na trilha** (FR-6335, R-005): o pedido, a recusa e as
    chamadas nomeadas. Por isso ela não é levantada dentro da transação — levantar desfaria o
    registro —, e sim depois dela, com o desfecho guardado na chave: a repetição recusa de novo, e
    não grava outro evento.
    """
    texto = (motivo or "").strip()
    payload = {
        "edital": str(edital_id),
        "movimento": str(movimento_id),
        "motivo": texto,
        "leitura": assinatura or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_DESFAZER_DESTINACAO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            recusado = (ctx.desfecho_anterior or {}).get("recusa")
            if not recusado:
                return ctx.desfecho_anterior
        else:
            _exigir_motivo(texto)
            edital = _edital_do_processo(ctx.processo, edital_id)
            previa = previa_do_desfazimento_da_destinacao(
                edital=edital,
                movimento_id=movimento_id,
                chamadas_dependentes=chamadas_dependentes,
                at=ctx.now,
            )
            recusado = _registrar_se_impedido(
                ctx, actor, previa, previa["movimento"], payload, correlation_id
            )
            if recusado is None:
                return _desfazer_destinacao(
                    ctx, actor, edital, previa, texto, assinatura, idempotency_key, correlation_id
                )
    raise DomainError(recusado["codigo"], recusado["detalhe"], 409)


def _desfazer_destinacao(
    ctx, actor, edital, previa, texto, assinatura, idempotency_key, correlation_id
):
    _conferir_assinatura(previa, assinatura)
    original = previa["movimento"]
    registro = MovimentoDeVaga.objects.create(
        # A apuração lida é a do recorte que devolve a vaga — o destino da destinação —, e é nela
        # que a vaga destinada estava (FR-6342).
        apuracao=previa["destino"],
        edital=edital,
        perfil_id=original.perfil_id,
        marco_id=original.marco_id,
        especie=nomes.MOVIMENTO_DESFAZIMENTO,
        # **Origem e destino invertidos, a mesma quantidade** (R-005): a apuração lê este como lê
        # qualquer movimento, e a soma das efetivas do Perfil volta à de antes (SC-2106).
        origem_lista_id=original.destino_lista_id,
        destino_lista_id=original.origem_lista_id,
        quantidade=original.quantidade,
        causa=f"Desfazimento da destinação de {original.registrado_em:%d/%m/%Y}: "
        f"{original.quantidade} vaga(s) devolvida(s).",
        gatilho=original.gatilho,
        fundamento=texto,
        versao=previa["versao"],
        desfaz=original,
        registrado_por=str(getattr(actor, "subject", actor)),
        registrado_em=ctx.now,
    )
    # A sucessora é a da reserva, que recebe a vaga de volta. A ampla fica obsoleta pelo
    # movimento, e a seguinte dela é de quem conduz, como na destinação (FR-6313).
    seguinte = _emitir_seguinte(
        ctx,
        actor,
        edital=edital,
        perfil_id=original.perfil_id,
        marco_id=original.marco_id,
        lista_id=original.origem_lista_id,
        motivo=f"Destinação desfeita: {original.quantidade} vaga(s) de volta. Motivo: {texto}",
        correlation_id=correlation_id,
    )
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=DESFAZER_DESTINACAO,
        aggregate=registro,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=(
            f"Desfazimento da destinação {original.id}: {original.quantidade} vaga(s) da ampla "
            f"concorrência de volta à lista {original.origem_lista_id}. Motivo: {texto}. "
            + _sucessora_na_razao(seguinte)
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "movimento": str(registro.id),
        "desfaz": str(original.id),
        "quantidade": registro.quantidade,
        **seguinte,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def previa_do_desfazimento_da_nao_preenchida(
    *, edital, declaracao_id, chamadas_dependentes, at=None
):
    """O que o desfazimento da declaração faria agora, e a recusa que daria (FR-6334, FR-6335).

    A chamada dependente é a do **mesmo** recorte cuja apuração leu a declaração (R-005): ela foi
    feita sobre a conta que a declaração mudou.
    """
    declaracao = _declaracao_do_edital(edital, declaracao_id)
    restante = next(
        (
            item["restante"]
            for item in _com_o_restante(
                selectors.nao_preenchidas_do_recorte(
                    edital=edital,
                    perfil_id=declaracao.perfil_id,
                    marco_id=declaracao.marco_id,
                    lista_id=declaracao.lista_id,
                )
            )
            if item["registro"].id == declaracao.id
        ),
        0,
    )
    dependentes = list(
        chamadas_dependentes(
            edital=edital,
            perfil_id=declaracao.perfil_id,
            marco_id=declaracao.marco_id,
            lista_id=declaracao.lista_id,
            movimento_id=None,
            nao_preenchida_id=declaracao.id,
            at=at,
        )
        or []
    )
    vigente = selectors.apuracao_vigente(
        edital=edital,
        perfil_id=declaracao.perfil_id,
        marco_id=declaracao.marco_id,
        lista_id=declaracao.lista_id,
    )
    recusa = None
    if not restante:
        recusa = (nomes.ATO_JA_DESFEITO, "Esta declaração de vaga não preenchida já foi desfeita.")
    elif dependentes:
        recusa = (nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE, _frase_dos_dependentes(dependentes))
    return {
        "declaracao": declaracao,
        "restante": restante,
        "versao": effective_version(edital_id=edital.id, at=at),
        "apuracao": vigente,
        "dependentes": dependentes,
        "recusa": recusa,
        "assinatura": canonical_sha256(
            {
                "gesto": "desfazer_nao_preenchida",
                "declaracao": str(declaracao.id),
                "restante": restante,
                "apuracao": str(vigente.id) if vigente else None,
                "dependentes": [str(d.get("id")) for d in dependentes],
            }
        ),
    }


def desfazer_nao_preenchida(
    *,
    actor,
    processo_id,
    edital_id,
    declaracao_id,
    motivo,
    assinatura,
    chamadas_dependentes,
    idempotency_key,
    correlation_id,
):
    """O ato contrário à declaração de não preenchida, ou a recusa registrada (FR-6334, FR-6335)."""
    texto = (motivo or "").strip()
    payload = {
        "edital": str(edital_id),
        "declaracao": str(declaracao_id),
        "motivo": texto,
        "leitura": assinatura or "",
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO_DE_DESFAZER_NAO_PREENCHIDA,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            recusado = (ctx.desfecho_anterior or {}).get("recusa")
            if not recusado:
                return ctx.desfecho_anterior
        else:
            _exigir_motivo(texto)
            edital = _edital_do_processo(ctx.processo, edital_id)
            previa = previa_do_desfazimento_da_nao_preenchida(
                edital=edital,
                declaracao_id=declaracao_id,
                chamadas_dependentes=chamadas_dependentes,
                at=ctx.now,
            )
            recusado = _registrar_se_impedido(
                ctx, actor, previa, previa["declaracao"], payload, correlation_id
            )
            if recusado is None:
                _conferir_assinatura(previa, assinatura)
                original = previa["declaracao"]
                quantidade = previa["restante"]
                registro = VagaNaoPreenchida.objects.create(
                    edital=edital,
                    perfil_id=original.perfil_id,
                    marco_id=original.marco_id,
                    lista_id=original.lista_id,
                    apuracao=previa["apuracao"],
                    especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO,
                    desfaz=original,
                    quantidade=quantidade,
                    fundamento=texto,
                    versao=previa["versao"],
                    registrado_por=str(getattr(actor, "subject", actor)),
                    registrado_em=ctx.now,
                )
                seguinte = _emitir_seguinte(
                    ctx,
                    actor,
                    edital=edital,
                    perfil_id=original.perfil_id,
                    marco_id=original.marco_id,
                    lista_id=original.lista_id,
                    motivo=(
                        f"Declaração de vaga não preenchida desfeita: {quantidade} vaga(s) de "
                        f"volta a ocupar. Motivo: {texto}"
                    ),
                    correlation_id=correlation_id,
                    causa_do_ato=nomes.CAUSA_DECLARACAO_POSTERIOR,
                )
                auditar(
                    actor=actor,
                    permissao=ctx.base.permissao,
                    operation=DESFAZER_NAO_PREENCHIDA,
                    aggregate=registro,
                    now=ctx.now,
                    correlation_id=correlation_id,
                    reason=(
                        f"Desfazimento da declaração de vaga não preenchida {original.id}: "
                        f"{quantidade} vaga(s) de volta a ocupar. Motivo: {texto}. "
                        + _sucessora_na_razao(seguinte)
                    ),
                    idempotency_key=idempotency_key,
                )
                declarado = {
                    "naoPreenchida": str(registro.id),
                    "desfaz": str(original.id),
                    "quantidade": quantidade,
                    **seguinte,
                }
                ctx.concluir_sem_resultado(201, declarado)
                return declarado
    raise DomainError(recusado["codigo"], recusado["detalhe"], 409)


def _registrar_se_impedido(ctx, actor, previa, aggregate, payload, correlation_id):
    """A recusa da prévia; com chamada dependente, registrada na trilha antes (FR-6335).

    As outras recusas — já desfeito, declaração dependente — levantam aqui, como qualquer recusa:
    não há pedido a registrar sobre o que não existe mais. A da chamada dependente é a que a spec
    manda deixar na trilha, com as chamadas nomeadas, e a transação a confirma.
    """
    if previa["recusa"] is None:
        return None
    codigo, frase = previa["recusa"]
    if codigo != nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE:
        raise DomainError(codigo, frase, 409)
    chamadas = [
        {"id": str(d.get("id")), "rotulo": d.get("rotulo") or "", "ocupa": bool(d.get("ocupa"))}
        for d in previa["dependentes"]
    ]
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=DESFAZIMENTO_IMPEDIDO,
        aggregate=aggregate,
        now=ctx.now,
        correlation_id=correlation_id,
        reason=(
            f"Pedido de desfazimento de {aggregate.__class__.__name__} {aggregate.id}, recusado: "
            + "; ".join(c["rotulo"] or c["id"] for c in chamadas)
            + f". Motivo do pedido: {payload['motivo']}"
        ),
        detalhe={"chamadas": chamadas, "pedido": payload},
    )
    recusado = {"codigo": codigo, "detalhe": frase, "chamadas": chamadas}
    ctx.concluir_sem_resultado(409, {"recusa": recusado})
    return recusado


def _frase_dos_dependentes(dependentes):
    """A recusa que nomeia cada pessoa chamada para esta vaga e o que a chamada precisa antes."""
    itens = "; ".join(
        (d.get("rotulo") or "sem identificação")
        + (", que ocupa a vaga" if d.get("ocupa") else ", ainda sem desfecho")
        for d in dependentes
    )
    return (
        f"Há {_pessoas(len(dependentes))} chamada{'s' if len(dependentes) != 1 else ''} para "
        f"esta vaga: {itens}. Cada chamada precisa do seu desfecho antes, e só depois de um "
        "desfecho que libere a vaga o ato pode ser desfeito."
    )


def _pessoas(quantas):
    return f"{quantas} pessoa" if quantas == 1 else f"{quantas} pessoas"


def _exigir_motivo(texto):
    if not texto:
        raise DomainError(
            nomes.MOTIVO_OBRIGATORIO,
            "Diga por que o ato está sendo desfeito.",
            422,
            campo="motivo",
        )


def _conferir_assinatura(previa, assinatura):
    if (assinatura or "") != previa["assinatura"]:
        raise DomainError(
            nomes.LEITURA_DO_RECORTE_MUDOU,
            "As vagas desta lista mudaram desde que a conferência foi aberta: confira de novo "
            "antes de confirmar.",
            409,
        )


def _destinacao_do_edital(edital, movimento_id):
    """A destinação **por ato próprio** deste Edital, ou a recusa (R-005).

    **Só o ato da `155`**, reconhecido pelo recorte próprio: o movimento que a apuração gravava
    antes dela conta como destinação feita (FR-6316), mas desfazê-lo sob a reversão por saldo
    seria devolvido à ampla pela emissão seguinte, que ainda move vaga ali (R-010).
    """
    try:
        identidade = identificador(movimento_id) if movimento_id else None
    except DomainError:
        identidade = None
    registro = (
        MovimentoDeVaga.objects.filter(
            edital=edital, id=identidade, especie=nomes.MOVIMENTO_REVERSAO
        ).first()
        if identidade
        else None
    )
    if registro is None:
        raise DomainError(nomes.ATO_INEXISTENTE, "Não há esta destinação neste Edital.", 404)
    return registro


def _declaracao_do_edital(edital, declaracao_id):
    try:
        identidade = identificador(declaracao_id) if declaracao_id else None
    except DomainError:
        identidade = None
    registro = (
        VagaNaoPreenchida.objects.filter(
            edital=edital, id=identidade, especie=nomes.NAO_PREENCHIDA_DECLARACAO
        ).first()
        if identidade
        else None
    )
    if registro is None:
        raise DomainError(
            nomes.ATO_INEXISTENTE,
            "Não há esta declaração de vaga não preenchida neste Edital.",
            404,
        )
    return registro


def _declaracao_que_leu(edital, movimento):
    """Se a ampla declarou não preenchida, ainda de pé, uma vaga que contava com este movimento.

    Desfazer a destinação tiraria das efetivas da ampla a vaga que a declaração tirou do "a
    ocupar", e a apuração seguinte passaria das vagas (`conferir_limite`).
    """
    declaracoes = selectors.nao_preenchidas_do_recorte(
        edital=edital,
        perfil_id=movimento.perfil_id,
        marco_id=movimento.marco_id,
        lista_id=movimento.destino_lista_id,
    )
    alvo = str(movimento.id)
    return any(
        item["restante"]
        and item["registro"].apuracao is not None
        and alvo
        in {str(i) for i in (item["registro"].apuracao.universo or {}).get("movimentosLidos") or []}
        for item in _com_o_restante(declaracoes)
    )


__all__ = [
    "DECLARAR_NAO_PREENCHIDA",
    "DESFAZER_DESTINACAO",
    "DESFAZER_NAO_PREENCHIDA",
    "DESFAZIMENTO_IMPEDIDO",
    "DESTINAR",
    "declarar_nao_preenchida",
    "desfazer_destinacao",
    "desfazer_nao_preenchida",
    "destinar_vaga",
    "frase_publicada",
    "leitura_da_vaga",
    "previa_da_destinacao",
    "previa_da_nao_preenchida",
    "previa_do_desfazimento_da_destinacao",
    "previa_do_desfazimento_da_nao_preenchida",
]
