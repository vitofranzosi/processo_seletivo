"""O cenário da 148: um Edital com análise das inscrições, inscrições analisadas e um prazo de recurso.

**A montagem percorre o caminho normal** — publicação pelo canal administrativo, comissão
constituída, distribuição, conclusão na Mesa e consolidação pelos comandos —, porque o que a 148
publica é o `ResultadoEtapa` que esse caminho produz. Um resultado semeado por fora provaria que o
ato lê linhas, e não que ele lê a análise.

O Cronograma ganha um Evento de recurso com término no futuro: é o que o preliminar escolhe como
prazo. O período de inscrições não é designado (o padrão das fixtures), e por isso nada espera o
período terminar — o caso do período em curso tem teste próprio, com Evento designado.
"""

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.divulgacao.application.inscricoes import aferir, publicar_inscricoes
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

EVENTO_DE_RECURSO = 480
EVENTO_DE_RECURSO_NOME = "Recurso contra o resultado preliminar da análise das inscrições"
PUBLICADORA = "paula.publicadora"


def ator_publicador(subject=PUBLICADORA):
    return ator_institucional(subject, "resultado:publicar")


def evento_de_recurso(seed):
    return identificador(EVENTO_DE_RECURSO, seed)


def montar(
    gestor,
    api_client,
    manager_headers,
    *,
    seed,
    codigo,
    decisoria=True,
    fim_do_recurso="2099-12-31T23:59:00-03:00",
    cronograma_extra=(),
):
    """Edital publicado com a Análise documental decisória, comissão e banca alocada."""
    rascunho = rascunho_com_etapas(seed, decisoria=decisoria)
    rascunho["schedule"] = [
        *rascunho["schedule"],
        {
            "id": evento_de_recurso(seed),
            "type": "RECURSO",
            "description": EVENTO_DE_RECURSO_NOME,
            "startAt": "2026-09-10T00:00:00-03:00",
            "endAt": fim_do_recurso,
            "order": 2,
        },
        *cronograma_extra,
    ]
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        draft=rascunho,
    )
    processo = edital.processo
    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"inscricoes-{seed}",
    )
    etapa = identificador(ETAPA_A1, seed)
    alocar_em(gestor, processo, membros["joao"], edital, etapa, chave=f"aloc-148-{seed}")
    return {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": etapa,
        "perfil": identificador(401, seed),
        "seed": seed,
    }


def inscrever_no(cenario, quantas, *, primeiro):
    """Inscrições enviadas no Perfil **deste** Edital — o Perfil deriva do `seed`."""
    return inscrever(
        cenario["edital"], quantas, primeiro=primeiro, perfil=identificador(401, cenario["seed"])
    )


def analisar(cenario, gestor, decisoes, *, sufixo):
    """Distribui, conclui na forma decisória e consolida — `[(inscricao, "FAVORAVEL"|...)]`."""
    if not decisoes:
        return
    inscricoes = [inscricao for inscricao, _ in decisoes]
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave=f"lote-148-{sufixo}")
    for inscricao, sentido in decisoes:
        concluir_como(
            cenario,
            "joao",
            inscricao,
            sentido=sentido,
            parecer=(
                "Documentação conforme o Edital."
                if sentido == "FAVORAVEL"
                else "Faltou o diploma de graduação exigido no item 4.2."
            ),
        )
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=f"consolidar-148-{sufixo}",
        correlation_id="fixture",
    )


def publicar(
    cenario,
    natureza,
    *,
    chave,
    prazo="",
    motivo="",
    etapa_id=None,
    ator=None,
    autoridade=str(AUTORIDADE_DO_RESULTADO),
):
    """Publica pelo comando, com a assinatura da prévia recalculada como a tela faz."""
    from django.utils import timezone

    afericao = aferir(
        edital=cenario["edital"], natureza=natureza, etapa_id=etapa_id, at=timezone.now()
    )
    return publicar_inscricoes(
        actor=ator or ator_publicador(),
        edital_id=cenario["edital"].id,
        natureza=natureza,
        etapa_id=etapa_id,
        prazo=prazo,
        motivo=motivo,
        autoridade=autoridade,
        confirmacao_da_previa=afericao.assinatura,
        idempotency_key=chave,
        correlation_id="fixture",
    )
