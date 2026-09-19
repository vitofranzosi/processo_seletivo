"""O cenário 7/1/2 da `034` — um Perfil, três recortes, e quem se autodeclarou em cada um.

**Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta.** Importar uma fixture de
outro módulo de teste a redefine no importador; importar uma função comum não tem esse problema. É a
regra que `tests/fixtures/corte.py` registra.

**Módulo novo, e não um parâmetro a mais em `tests/fixtures/ocupacao.py`.** O cenário da `016` tem
uma cota só e alvo fixo, e é ele que seis arquivos exercitam; acrescentar-lhe uma segunda Modalidade
e trocar a regra de corte por `FROM_VACANCY_TABLE` mudaria o que aqueles arquivos testam sem que
nenhum deles dissesse por quê. O cenário daqui é o da auditoria — sete na linha geral, uma para PcD,
duas para PPI —, e é o que a `SC-169` percorre.

**A autodeclaração é gravada depois da emissão da ordem da ampla**, e isso não a altera: o universo
da ampla é o Perfil inteiro, com ou sem autodeclaração (`D-001`, `FR-492`). O que a autodeclaração
muda é de quem são os recortes reservados.
"""

from processo_seletivo.classificacao.domain import faixa
from tests.fixtures.corte import MARCO, montar_cenario_do_corte, rascunho
from tests.fixtures.ocupacao import LINHA_GERAL, LINHA_PPI, MODALIDADE_PPI

LINHA_PCD = "00000000-0000-4000-8000-000000000481"
MODALIDADE_PCD = "00000000-0000-4000-8000-000000000482"

#: A Modalidade que o Perfil aponta como sendo a ampla concorrência — a grafia-armadilha. Tem nome
#: de Modalidade, não tem vagas próprias, e a quantidade dela mora na linha geral. **Não é recorte**
#: (`FR-503`), e quem a declara é `rascunho_7_1_2(com_ampla_declarada=True)`.
MODALIDADE_AMPLA_DECLARADA = "00000000-0000-4000-8000-000000000483"


def regra_do_quadro(**overrides):
    """A regra de corte que deriva o alvo **do quadro**, que é o que faz cada recorte ter o seu.

    A regra do cenário da `014` é de alvo fixo, e com ela os três recortes cortariam no mesmo
    número — o que esconderia justamente o que esta feature entrega.
    """
    base = {
        "targetKind": faixa.ALVO_DO_QUADRO,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": None,
        "continuation": "NONE",
    }
    base.update(overrides)
    return base


def rascunho_7_1_2(
    *,
    cut=None,
    geral=7,
    pcd=1,
    ppi=2,
    com_ampla_declarada=False,
    sem_reserva=False,
):
    """O rascunho do Perfil com as duas Modalidades reservadas e o quadro repartido.

    `sem_reserva` devolve o Perfil de recorte único — é a contraprova da `FR-493`, e ela precisa do
    **mesmo** Edital em tudo o mais para que a comparação de ordem signifique alguma coisa.

    `com_ampla_declarada` acrescenta a Modalidade que o Perfil aponta como sendo a ampla. Ela entra
    no quadro de Modalidades e **não** ganha linha própria: a quantidade dela é a da linha geral.
    """
    base, pontuada = rascunho(cut=cut if cut is not None else regra_do_quadro())
    perfil = base["profiles"][0]
    modalidades = []
    linhas = [{"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": geral}]
    if not sem_reserva:
        modalidades.append(
            {
                "id": MODALIDADE_PCD,
                "code": "PCD",
                "name": "Pessoas com deficiência",
                "vacancies": 0,
            }
        )
        modalidades.append(
            {
                "id": MODALIDADE_PPI,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "vacancies": 0,
            }
        )
        linhas.append({"id": LINHA_PCD, "modalityId": MODALIDADE_PCD, "immediateVacancies": pcd})
        linhas.append({"id": LINHA_PPI, "modalityId": MODALIDADE_PPI, "immediateVacancies": ppi})
    if com_ampla_declarada:
        modalidades.append(
            {
                "id": MODALIDADE_AMPLA_DECLARADA,
                "code": "AC",
                "name": "Ampla concorrência",
                "vacancies": 0,
            }
        )
        perfil["generalCompetitionModalityId"] = MODALIDADE_AMPLA_DECLARADA
    if modalidades:
        perfil["competitionModalities"] = modalidades
    perfil["vacancyTable"] = linhas
    # O total do Perfil acompanha o quadro, senão o Edital não publica: a conferência da `025` exige
    # igualdade quando o quadro é completo. A Modalidade declarada como ampla não soma — a
    # quantidade dela **é** a da linha geral, e somá-la declararia duas vezes o mesmo número.
    perfil["immediateVacancies"] = geral if sem_reserva else geral + pcd + ppi
    return base, pontuada


def montar_cenario_7_1_2(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    prefixo="recortes-034",
    pontuacoes=("95.0000", "90.0000", "85.0000", "80.0000", "75.0000"),
    autodeclarar=True,
    **quadro,
):
    """Edital publicado 7/1/2, ordem da **ampla** emitida, e as autodeclarações gravadas.

    Devolve `(edital, etapa_pontuada, inscricoes)` — a mesma forma que a `014` e a `016` usam, para
    que quem leia os três reconheça o cenário.

    A repartição das autodeclarações é a do `quickstart`: a segunda colocada em PcD, a terceira e a
    quinta em PPI, e as demais sem autodeclaração alguma. Ela é deliberadamente **entremeada** — se
    os autodeclarados fossem os últimos, uma implementação que ordenasse o recorte reservado pelo
    universo inteiro produziria a mesma lista, e o teste passaria sem provar nada.
    """

    def monta(cut=None):
        return rascunho_7_1_2(cut=cut, **quadro)

    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        pontuacoes=pontuacoes,
        draft_factory=monta,
    )
    if autodeclarar and not quadro.get("sem_reserva"):
        declarar(inscricoes[1], MODALIDADE_PCD)
        declarar(inscricoes[2], MODALIDADE_PPI)
        declarar(inscricoes[4], MODALIDADE_PPI)
    return edital, pontuada, inscricoes


def declarar(inscricao, modalidade_id):
    """A autodeclaração, gravada pelo queryset como todo campo de Inscrição submetida."""
    from processo_seletivo.inscricoes.models import Inscricao

    Inscricao.objects.filter(pk=inscricao.pk).update(modality_id=modalidade_id)
    inscricao.refresh_from_db()
    return inscricao


def emitir_recorte(edital, gestor, *, lista_id=None, chave, motivo="", decisoes=()):
    """Emite a ordem de um recorte pelo comando, com a confirmação **daquele** recorte.

    A assinatura é recomposta aqui de propósito: ela distingue os recortes (`FR-495`), e um helper
    que reaproveitasse a confirmação da ampla esconderia justamente o defeito que ela existe para
    impedir.
    """
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from tests.fixtures.edital import PROFILE_ID

    proposta = calcular_ordem(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )
    vigente = ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)
    return emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-recortes-034",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        motivo=motivo,
        decisoes=decisoes,
    )


def confirmacao_do_recorte(edital, *, lista_id=None):
    """A assinatura da leitura daquele recorte — o que o teste da confirmação cruzada compara."""
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from tests.fixtures.edital import PROFILE_ID

    proposta = calcular_ordem(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )
    return assinatura_da_proposta(
        proposta, ato_vigente=ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)
    )
