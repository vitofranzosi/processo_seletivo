"""A emissão da apuração: as recusas, a sucessão e o que o ato congela (016).

O que estes testes protegem não é a aritmética — ela é de unidade — e sim as recusas que impedem
apurar o que não se deve, e a sucessão que preserva o que já foi apurado.
"""

import pytest

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def apurar(edital, gestor, *, chave="ocupacao-016-apurar", motivo="", lista_id=None):
    return emitir_apuracao(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-ocupacao-016",
        motivo=motivo,
    )


def test_a_apuracao_grava_as_tres_quantidades_e_congela_o_universo(cenario, gestor):
    """O ato nasce com publicadas, efetivas e ocupadas — e `faltando` é derivado."""
    edital, _, _ = cenario

    declarado = apurar(edital, gestor)

    assert declarado["publicadas"] == 3
    # Sem movimento nenhum, efetivas igualam publicadas.
    assert declarado["efetivas"] == 3
    # Ninguém habilitou na Entrevista ainda: a faixa progrediu, a Etapa governada não concluiu.
    assert declarado["ocupadas"] == 0
    assert declarado["faltando"] == 3
    universo = declarado["universo"]
    assert universo["immediateVacancies"] == 3
    assert universo["orderId"]
    assert universo["cutId"]
    # **Os ids congelados, e não "os movimentos de hoje"** (`FR-244`).
    assert universo["movimentosLidos"] == []


def test_a_apuracao_e_idempotente(cenario, gestor):
    """A mesma chave devolve o mesmo desfecho, e não emite um segundo ato."""
    edital, _, _ = cenario

    primeiro = apurar(edital, gestor)
    segundo = apurar(edital, gestor)

    assert primeiro["id"] == segundo["id"]
    assert ApuracaoDeOcupacao.objects.count() == 1


def test_a_sucessao_sem_motivo_e_recusada(cenario, gestor):
    """Sucessão exige motivo, como a do corte e a do Resultado já exigem."""
    edital, _, _ = cenario
    apurar(edital, gestor)

    with pytest.raises(DomainError) as erro:
        apurar(edital, gestor, chave="ocupacao-016-apurar-2")

    assert erro.value.code == "motivo_da_sucessao_obrigatorio"


def test_a_sucessao_com_motivo_preserva_a_anterior(cenario, gestor):
    """**A anterior continua legível**: correção é sucessão, nunca reescrita (`FR-262`)."""
    edital, _, _ = cenario
    primeira = apurar(edital, gestor)

    segunda = apurar(edital, gestor, chave="ocupacao-016-apurar-2", motivo="Reanálise documental")

    assert primeira["id"] != segunda["id"]
    anterior = ApuracaoDeOcupacao.objects.get(id=primeira["id"])
    nova = ApuracaoDeOcupacao.objects.get(id=segunda["id"])
    assert nova.apuracao_anterior_id == anterior.id
    assert nova.motivo_da_sucessao == "Reanálise documental"
    # A vigente é a que ninguém sucedeu — derivada, e não coluna.
    vigente = selectors.apuracao_vigente(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert vigente.id == nova.id


def test_duas_sucessoras_da_mesma_anterior_sao_recusadas(cenario, gestor):
    """**A constraint que faltava no primeiro desenho** (`uq_apuracao_sucessora_unica`).

    Sem ela o recorte ficaria com **duas** vigentes, e vigência é derivada justamente de "ninguém me
    sucedeu". O ataque aqui é direto ao banco, porque a aplicação já impede pelo caminho normal: é a
    mesma razão pela qual a constraint existe além da regra de aplicação.
    """
    from django.db.utils import IntegrityError
    from django.utils import timezone

    edital, _, _ = cenario
    primeira_id = apurar(edital, gestor)["id"]
    apurar(edital, gestor, chave="ocupacao-016-apurar-2", motivo="Primeira sucessão")
    primeira = ApuracaoDeOcupacao.objects.get(id=primeira_id)

    with pytest.raises(IntegrityError, match="uq_apuracao_sucessora_unica"):
        ApuracaoDeOcupacao(
            edital=edital,
            perfil_id=primeira.perfil_id,
            marco_id=primeira.marco_id,
            lista_id=primeira.lista_id,
            ato=primeira.ato,
            corte=primeira.corte,
            versao=primeira.versao,
            apuracao_anterior=primeira,
            motivo_da_sucessao="Segunda sucessora da mesma anterior",
            publicadas=3,
            efetivas=3,
            ocupadas=0,
            emitida_por="teste",
            emitida_em=timezone.now(),
        ).save()


def test_o_gatilho_recusa_alteracao_por_queryset(cenario, gestor):
    """A terceira camada: `QuerySet.update()` não passa pelo `save()` do modelo (`FR-260`)."""
    from django.db.utils import InternalError, ProgrammingError

    edital, _, _ = cenario
    apurar(edital, gestor)

    with pytest.raises((InternalError, ProgrammingError), match="immutable"):
        ApuracaoDeOcupacao.objects.all().update(ocupadas=99)


def test_apurar_sem_quadro_publicado_e_recusado(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """**Ausência de quadro não é zero** (`FR-242`, `UX-032`).

    O cenário aqui é o da `014` sem quadro nenhum — que é o que todo Edital publicado antes do
    degrau 12 afirma. A recusa nomeia a causa em vez de a tela dizer "0 vagas".
    """
    from tests.fixtures.corte import emitir as emitir_corte_do_cenario
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="ocupacao-016-sem-quadro"
    )
    emitir_corte_do_cenario(edital, gestor, chave="ocupacao-016-sem-quadro-corte")

    with pytest.raises(DomainError) as erro:
        apurar(edital, gestor, chave="ocupacao-016-sem-quadro-apurar")

    assert erro.value.code == "sem_quadro_publicado"
