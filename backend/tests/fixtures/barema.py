"""O cenário do barema na Mesa (146): uma Etapa pontuada com a ficha do 14/2026.

Separado de `mesa.py` e de `resultado.py` porque os dois montam a Etapa sem barema, que é o caso de
quase toda a suíte e tem de continuar sendo (FR-5231). Aqui a Etapa de leitura única ganha os cinco
critérios do quickstart §1 e os dois Documentos Exigidos que os comprovam, e a máxima da Etapa é a
soma das máximas (D-003). O resto — publicação, comissão, alocação — é o percurso normal.

A ficha é concluída pelo comando real, `avaliacao.concluir`, com o detalhamento: um cenário que
gravasse a nota por fora seria o Resultado sem parcelas que a FR-5232 diz que nunca existe.
"""

from processo_seletivo.avaliacoes.application.avaliacao import concluir, gravar
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.conftest import ator_institucional
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, rascunho_com_etapas
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import publish_original

TITULOS = 1460
DECLARACAO = 1461
CRITERIO_BASE = 1462

NOMES = (
    "Diploma de Doutorado",
    "Diploma de Mestrado",
    "Especialização",
    "Curso de formação de orientadores",
    "Exercício de docência em EaD",
)


def criterio_de(indice, seed=0):
    """O identificador do critério `indice` (0 a 4) do barema do `seed`."""
    return identificador(CRITERIO_BASE + indice, seed)


def documentos_do_barema(seed=0):
    return [
        {
            "id": identificador(TITULOS, seed),
            "key": "titulos",
            "name": "Títulos acadêmicos",
            "required": False,
            "order": 1,
        },
        {
            "id": identificador(DECLARACAO, seed),
            "key": "docencia",
            "name": "Declaração de exercício de docência",
            "required": False,
            "order": 2,
        },
    ]


def barema_do_14(seed=0, *, descricao_da_docencia="Em cursos a distância."):
    """O Anexo IV do 14/2026, como o quickstart §1 o compõe — a soma das máximas é 100."""
    titulos = identificador(TITULOS, seed)
    linhas = [
        ("20.0000", "20.0000", "diploma", titulos, ""),
        ("15.0000", "15.0000", "diploma", titulos, ""),
        ("10.0000", "5.0000", "certificado", titulos, "Lato sensu, na área da Educação."),
        ("15.0000", "15.0000", "certificado", titulos, ""),
        ("40.0000", "1.0000", "mês", identificador(DECLARACAO, seed), descricao_da_docencia),
    ]
    return [
        {
            "id": criterio_de(indice, seed),
            "name": NOMES[indice],
            "description": descricao,
            "maximumScore": maxima,
            "pointsPerUnit": pontos,
            "unitLabel": unidade,
            "documentRequirementId": documento,
        }
        for indice, (maxima, pontos, unidade, documento, descricao) in enumerate(linhas)
    ]


def com_barema(rascunho, *, etapa=0, seed=0):
    """O rascunho com o barema do 14/2026 na Etapa de posição `etapa`, e os seus documentos."""
    rascunho["documentRequirements"] = [
        *(rascunho.get("documentRequirements") or []),
        *documentos_do_barema(seed),
    ]
    alvo = rascunho["stages"][etapa]
    alvo["criteria"] = barema_do_14(seed)
    alvo["maximumScore"] = "100.0000"
    return rascunho


def montar_mesa_com_barema(gestor, api_client, manager_headers, *, seed, codigo, minima="60.0000"):
    """Edital publicado com barema na Etapa 1, de leitura única, e `joao` alocado nela."""
    rascunho = com_barema(
        rascunho_com_etapas(seed, avaliacoes=1, maxima="100.0000", minima=minima), seed=seed
    )
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
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO), ("ana", Funcao.MEMBRO)],
        prefixo=f"barema-{seed}",
    )
    etapa = identificador(ETAPA_A1, seed)
    for nome in ("joao", "ana"):
        alocar_em(gestor, processo, membros[nome], edital, etapa, chave=f"aloc-146-{seed}-{nome}")
    return {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": etapa,
        "seed": seed,
        "titulos": identificador(TITULOS, seed),
        "declaracao": identificador(DECLARACAO, seed),
    }


def ficha(seed=0, *valores, justificativas=None):
    """O detalhamento na ordem do barema: `ficha(0, 1, 0, 3, 0, 52)` é o quickstart §2.

    `None` deixa o critério em branco. As quantidades vão como texto, como o formulário as envia.
    """
    justificativas = justificativas or {}
    return [
        {
            "criterionId": criterio_de(indice, seed),
            "quantidade": None if valor is None else str(valor),
            "justificativa": justificativas.get(indice, ""),
        }
        for indice, valor in enumerate(valores)
    ]


def concluir_com_ficha(cenario, subject, inscricao, criterios, *, parecer="Conferido.", revisao=1):
    versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    avaliacao, _ = concluir(
        ator=ator_institucional(subject),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao=None,
        criterios=criterios,
        parecer=parecer,
        expected_revision=revisao,
        versao_reconhecida=versao.id,
        correlation_id="teste",
    )
    return avaliacao


def gravar_ficha(cenario, subject, inscricao, criterios, *, parecer="", revisao=1):
    avaliacao, _ = gravar(
        ator=ator_institucional(subject),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao=None,
        criterios=criterios,
        parecer=parecer,
        expected_revision=revisao,
        correlation_id="teste",
    )
    return avaliacao


def montar_marco_com_barema(
    gestor, api_client, manager_headers, process_payload, *, seed, codigo, regra_da_etapa=None
):
    """O marco da 017 com o barema na Etapa que ele enumera, e `ana` alocada para a reavaliação.

    É o caminho inteiro de `montar_marco` — publicar, constituir, alocar —, com a ficha do 14/2026
    na segunda Etapa. A reavaliação determinada por recurso se cumpre com **outro** avaliador
    (018, FR-067), e por isso a banca ganha uma segunda pessoa.
    """
    from tests.fixtures.divulgacao import montar_marco

    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        regra_da_etapa=regra_da_etapa,
        ajustar=lambda rascunho: com_barema(rascunho, etapa=1, seed=seed),
    )
    ana = constituir(
        gestor, cenario["processo"], [("ana", Funcao.MEMBRO)], prefixo=f"barema-ana-{seed}"
    )["ana"]
    alocar_em(
        gestor, cenario["processo"], ana, cenario["edital"], cenario["etapa"], chave=f"ana-{seed}"
    )
    cenario["membros"]["ana"] = ana
    cenario["titulos"] = identificador(TITULOS, seed)
    cenario["declaracao"] = identificador(DECLARACAO, seed)
    cenario["seed"] = seed
    return cenario


def pontuar_com_ficha(cenario, gestor, fichas, *, primeiro, sufixo, avaliador="joao"):
    """Inscreve uma inscrição por ficha, distribui, conclui pela ficha e consolida a Etapa do marco.

    `fichas` são detalhamentos completos, como `ficha(seed, 1, 0, 3, 0, 52)` os monta.
    """
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.comissao import inscrever
    from tests.fixtures.mesa import distribuir_para

    inscricoes = inscrever(
        cenario["edital"],
        len(fichas),
        primeiro=primeiro,
        perfil=cenario["perfil"],
        documentos=[cenario["titulos"], cenario["declaracao"]],
        modalidades=cenario["modalidade"],
    )
    distribuir_para(cenario, gestor, [avaliador], inscricoes, chave=f"lote-146-{sufixo}")
    for inscricao, criterios in zip(inscricoes, fichas, strict=True):
        concluir_com_ficha(cenario, avaliador, inscricao, criterios)
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=f"consolidar-146-{sufixo}",
        correlation_id="fixture",
    )
    return inscricoes
