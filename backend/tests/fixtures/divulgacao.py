"""O cenário da 017: um marco classificatório com ato **emitido e vigente**, pronto para publicar.

Fica aqui, e não dentro de um arquivo de teste, porque cinco jornadas partem do mesmo ponto — um
`AtoDeOrdenacao` sobre inscrições consolidadas — e repetir a montagem faria cada uma divergir da
outra com o tempo.

**A montagem percorre o caminho normal**, e não `INSERT` cru: publicar afere publicabilidade
reproduzindo o estado classificatório, e um ato semeado por fora não teria universo com que
comparar. É o mesmo motivo por que `tests/fixtures/publicacao.py` publica pelo canal
administrativo em vez de criar a linha.
"""

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

# Os marcos classificatórios dos cenários, derivados do `seed` como Perfil e Etapa: o
# identificador do marco é publicado e **único no escopo**, e dois Editais do mesmo teste com o
# mesmo marco fazem o rascunho ser recusado por `identifier_belongs_to_another_edital`.
MARCO_BASE = 471
MARCO_INTERMEDIARIO_BASE = 472
# Uma modalidade declarada, para que a coluna da lista tenha rótulo institucional a resolver: sem
# ela a projeção sairia com modalidade vazia, e a correspondência entre página e documento seria
# afirmada sobre um campo que ninguém preencheu (FR-064).
MODALIDADE_BASE = 473
MODALIDADE_NOME = "Ampla concorrência"


def modalidade_de(seed=0):
    return identificador(MODALIDADE_BASE, seed)


def marco_de(seed=0):
    return identificador(MARCO_BASE, seed)


def marco_intermediario_de(seed=0):
    """O segundo marco, para o cenário dos dois blocos na Área do Candidato (SC-022).

    `code` decide a ordem normativa, e é por isso que o intermediário é `A-INTERMEDIARIO` e o
    final é `Z-FINAL`: publicá-los fora de ordem é o que o teste precisa exercer.
    """
    return identificador(MARCO_INTERMEDIARIO_BASE, seed)


PUBLICADORA = "paula.publicadora"


def ator_publicador(subject=PUBLICADORA):
    return ator_institucional(subject, "resultado:publicar")


def rascunho_com_marco(seed=0, *, com_intermediario=False, criterios=None, regra_da_etapa=None):
    """O rascunho da 015: duas Etapas, a segunda enumerada por um marco classificatório."""
    rascunho = rascunho_com_etapas(seed, avaliacoes=1, maxima="100.0000", minima="60.0000")
    primeira, segunda = rascunho["stages"]
    segunda["weight"] = "1.0000"
    primeira["weight"] = "1.0000"
    # A regra da Etapa do marco, quando o teste precisa de uma: nota mínima e caráter eliminatório
    # são o que separa "habilitada" de "eliminada", e sem elas o cenário só produz habilitação —
    # o que tornaria vazio qualquer teste sobre a consequência derivada.
    if regra_da_etapa:
        segunda.update(regra_da_etapa)
    marcos = [
        {
            "id": marco_de(seed),
            "code": "Z-FINAL",
            "name": "Classificação final",
            "stages": [segunda["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": criterios or [],
        }
    ]
    if com_intermediario:
        # O marco intermediário enumera a primeira Etapa, e o Edital só publica marco sobre Etapa
        # **classificatória** — enumerar uma que ele não publicou assim é recusa de validação, e
        # com razão: um marco sobre Etapa não classificatória ordenaria por um número que o Edital
        # não declarou servir para ordenar.
        primeira["classificatory"] = True
        marcos.insert(
            0,
            {
                "id": marco_intermediario_de(seed),
                "code": "A-INTERMEDIARIO",
                "name": "Classificação da análise documental",
                "stages": [primeira["id"]],
                "operation": "SOMA_PONDERADA",
                "normalization": "NENHUMA",
                "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                "tiebreakers": [],
            },
        )
    rascunho["profiles"][0]["classificationMilestones"] = marcos
    rascunho["profiles"][0]["competitionModalities"] = [
        {"id": modalidade_de(seed), "code": "AC", "name": MODALIDADE_NOME, "vacancies": 1}
    ]
    return rascunho


def montar_marco(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    seed=0,
    codigo="0171",
    com_intermediario=False,
    criterios=None,
    fatos=None,
    regra_da_etapa=None,
):
    """Edital publicado, comissão constituída e banca alocada nas duas Etapas."""
    rascunho = rascunho_com_marco(
        seed,
        com_intermediario=com_intermediario,
        criterios=criterios,
        regra_da_etapa=regra_da_etapa,
    )
    if fatos is not None:
        rascunho["profiles"][0]["declaredFacts"] = fatos
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            **process_payload,
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {
                **process_payload["firstEdital"],
                "number": codigo,
                "title": f"Edital {codigo}",
            },
        },
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"divulgacao-{seed}",
    )
    primeira = identificador(410, seed)
    segunda = identificador(411, seed)
    for etapa in (primeira, segunda):
        alocar_em(
            gestor,
            edital.processo,
            membros["joao"],
            edital,
            etapa,
            chave=f"aloc-017-{seed}-{etapa}",
        )
    return {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": segunda,
        "primeira": primeira,
        "segunda": segunda,
        "marco": marco_de(seed),
        "marco_intermediario": marco_intermediario_de(seed),
        "perfil": identificador(401, seed),
        "modalidade": modalidade_de(seed),
    }


def pontuar(cenario, gestor, pontuacoes, *, primeiro=701, etapa=None, sufixo="a"):
    """Inscrições submetidas, distribuídas, concluídas e consolidadas na Etapa do marco.

    `pontuacoes` é a lista de notas: uma inscrição por nota, na ordem. `None` deixa a inscrição
    **sem Resultado** — é o que produz alguém considerado e sem posição, que é a linha que separa
    a projeção pública da individual (FR-017).
    """
    alvo = etapa or cenario["etapa"]
    anterior = cenario["etapa"]
    cenario["etapa"] = alvo
    inscricoes = inscrever(
        cenario["edital"], len(pontuacoes), primeiro=primeiro, perfil=cenario["perfil"]
    )
    # A modalidade é escolhida na inscrição, e o cenário a declara para todas: é o que dá à
    # projeção um rótulo institucional a resolver em vez de uma coluna vazia.
    Inscricao.objects.filter(pk__in=[item.pk for item in inscricoes]).update(
        modality_id=cenario["modalidade"]
    )
    for item in inscricoes:
        item.refresh_from_db()
    com_nota = [
        inscricao
        for inscricao, nota in zip(inscricoes, pontuacoes, strict=True)
        if nota is not None
    ]
    if com_nota:
        distribuir_para(cenario, gestor, ["joao"], com_nota, chave=f"lote-017-{sufixo}")
        for inscricao, nota in zip(inscricoes, pontuacoes, strict=True):
            if nota is not None:
                concluir_como(cenario, "joao", inscricao, pontuacao=nota)
        consolidar(
            actor=gestor,
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            etapa_id=alvo,
            inscricao_ids=[item.id for item in com_nota],
            idempotency_key=f"consolidar-017-{sufixo}",
            correlation_id="fixture",
        )
    cenario["etapa"] = anterior
    return inscricoes


def emitir(cenario, gestor, *, marco=None, chave="emitir-017", motivo="", decisoes=()):
    """Emite o ato do marco pelo command, conferindo a assinatura como a tela faz.

    `decisoes` são as providências a jusante que o ato executa (018, FR-089): a citação nasce com o
    ato, na mesma transação, e é ela — depois de publicada — que prova o cumprimento.
    """
    marco_id = marco or cenario["marco"]
    proposta = calcular_ordem(
        edital=cenario["edital"], perfil_id=cenario["perfil"], marco_id=marco_id
    )
    vigente = AtoDeOrdenacao.objects.filter(
        edital=cenario["edital"], marco_id=marco_id, sucessores__isnull=True
    ).first()
    emitir_ordem(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        perfil_id=cenario["perfil"],
        marco_id=marco_id,
        idempotency_key=chave,
        correlation_id="fixture",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        motivo=motivo or ("Correção da ordem." if vigente is not None else ""),
        decisoes=decisoes,
    )
    return AtoDeOrdenacao.objects.filter(
        edital=cenario["edital"], marco_id=marco_id, sucessores__isnull=True
    ).get()


def montar_ato_publicavel(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    seed=0,
    codigo="0171",
    pontuacoes=("90.0000", "70.0000"),
    primeiro=701,
    com_intermediario=False,
    criterios=None,
):
    """O ponto de partida de quase todo teste da feature: ato emitido e vigente.

    Devolve o cenário acrescido de `inscricoes` e `ato` — e, com `pontuacoes` contendo `None`,
    também de quem foi considerado e não recebeu posição.
    """
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        com_intermediario=com_intermediario,
        criterios=criterios,
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, list(pontuacoes), primeiro=primeiro, sufixo=str(seed)
    )
    cenario["ato"] = emitir(cenario, gestor, chave=f"emitir-017-{seed}")
    return cenario


def publicar_o_ato(
    cenario,
    ator=None,
    *,
    natureza="PRELIMINAR",
    autoridade="diretoria-cefor",
    chave="publicar-017",
    ato=None,
    declaracao=None,
):
    """Publica pelo command, recalculando a assinatura da prévia como a tela faz.

    **A declaração de encerramento do prazo acompanha a natureza definitiva** desde a 018: enquanto
    o Edital não declara janela recursal computável, publicar como definitivo exige dizer, com
    fundamento escrito, que o prazo se encerrou (FR-085). A fixture a fornece por padrão porque é o
    que o operador faz na tela — os testes que exercitam a exigência a omitem de propósito.
    """
    if declaracao is None and natureza == "DEFINITIVA":
        declaracao = "O prazo recursal encerrou-se sem interposição, conforme o Edital."
    from processo_seletivo.divulgacao.application.publicar import (
        assinatura_da_previa,
        publicar_resultado,
    )
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.conteudo import compor

    alvo = ato or cenario["ato"]
    projecao = compor(alvo)
    anterior = vigente_do_marco(edital=cenario["edital"], marco_id=alvo.marco_id)
    return publicar_resultado(
        actor=ator or ator_publicador(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        marco_id=alvo.marco_id,
        ato_id=alvo.id,
        natureza=natureza,
        autoridade=autoridade,
        confirmacao_da_previa=assinatura_da_previa(
            ato=alvo, publicacao_anterior=anterior, projecao=projecao
        ),
        idempotency_key=chave,
        correlation_id="fixture",
        declaracao_de_encerramento=declaracao or "",
    )


def entrar_como_titular(client, inscricao):
    """Deixa a sessão do portal identificada como a titular **daquela** inscrição.

    As inscrições do cenário nascem com `identity_subject` próprio, e não com o de Maria ou João:
    é o que permite exercitar a Área da pessoa certa e, no teste de isolamento, a de outra.
    """
    from django.utils import timezone

    from processo_seletivo.identidade.models import CandidateIdentity
    from processo_seletivo.portal import identidade as identidade_do_candidato

    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject,
        defaults={
            "nome": inscricao.nome,
            "cpf_normalizado": inscricao.cpf_normalizado,
            "created_at": timezone.now(),
        },
    )
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(registro.pk)
    sessao.save()
    return registro
