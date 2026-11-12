"""O movimento sem apuração é lido, e a vaga não preenchida também (155, R-001, R-002).

**Duas provas, de naturezas diferentes.** A primeira é de texto: nenhuma leitura do movimento por
`apuracao__edital` fica sem a outra metade, o recorte próprio. O defeito que ela impede não dá
erro — o movimento da lista de sorteio sem relação, que não tem apuração (R-007), sumiria da conta
da ampla, e a vaga sairia da reserva sem chegar a lugar nenhum. Uma varredura acha a leitura que
alguém escrever amanhã; um caso de comportamento só acha as que já existem.

A segunda é de comportamento, sobre a apuração de verdade: o movimento sem apuração obsoleta a
vigente e entra na seguinte; a declaração de vaga não preenchida obsoleta pela sétima causa e sai do
"a ocupar" da seguinte, com os ids congelados. Nenhum ato da `155` grava essas linhas ainda — eles
vêm nos incrementos seguintes —, e por isso elas são gravadas à mão, como `test_acrescimo.py` faz.
"""

import re
import uuid
from pathlib import Path

import pytest
from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao
from tests.integration.ocupacao.test_emissao import apurar

RAIZ = Path(__file__).resolve().parents[3] / "processo_seletivo"
# O único lugar que pode perguntar por `apuracao__edital`: o filtro que já pergunta pelos dois.
DONO_DO_FILTRO = RAIZ / "ocupacao/application/selectors.py"
POR_APURACAO = re.compile(r"apuracao__(edital|perfil_id|marco_id)\b")


def _sem_comentario(texto):
    # Duas passadas, e não uma alternância com `re.S`: ali o `#.*$` atravessaria as linhas e
    # apagaria o arquivo do primeiro comentário em diante — a varredura passaria lendo nada.
    sem_docstring = re.sub(r'""".*?"""', " ", texto, flags=re.S)
    return re.sub(r"^\s*#.*$", " ", sem_docstring, flags=re.M)


def test_nenhuma_leitura_do_movimento_por_apuracao_fica_sem_o_recorte_proprio():
    """Fora de `selectors.do_recorte`, ninguém filtra o movimento pela apuração."""
    achados = []
    for caminho in sorted(RAIZ.rglob("*.py")):
        if "migrations" in caminho.parts:
            continue
        corpo = _sem_comentario(caminho.read_text(encoding="utf-8"))
        for linha in corpo.splitlines():
            if POR_APURACAO.search(linha):
                achados.append((caminho.relative_to(RAIZ).as_posix(), linha.strip()))
    fora_do_dono = [
        achado for achado in achados if achado[0] != DONO_DO_FILTRO.relative_to(RAIZ).as_posix()
    ]

    assert fora_do_dono == [], (
        "leitura do movimento pela apuração sem o recorte próprio — use selectors.do_recorte: "
        f"{fora_do_dono}"
    )
    # E no dono, uma linha só, a do filtro que pergunta pelos dois caminhos.
    assert len(achados) == 1, achados


def test_o_filtro_pergunta_pelos_dois_caminhos():
    filtro = selectors.do_recorte(edital="e", perfil="p", marco="m")

    assert filtro.connector == "OR"
    assert len(filtro.children) == 2


# --- O comportamento, sobre a apuração de verdade -----------------------------------------------


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_ocupacao(
        gestor, api_client, manager_headers, process_payload, prefixo="ocupacao-155-leitura"
    )


def movimento_sem_apuracao(edital, *, destino=None, origem=None, quantidade=2):
    """Uma vaga que chega à ampla de uma lista sem apuração — a forma do sorteio sem relação."""
    return MovimentoDeVaga.objects.create(
        apuracao=None,
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        especie=nomes.MOVIMENTO_REVERSAO,
        origem_lista_id=origem or uuid.uuid4(),
        destino_lista_id=destino,
        quantidade=quantidade,
        causa="Lista reservada sem concorrente",
        gatilho=nomes.REVERSAO_POR_ESGOTAMENTO,
        fundamento="Item 4.3 do Edital.",
        versao=effective_version(edital_id=edital.id),
        registrado_por="teste",
        registrado_em=timezone.now(),
    )


def nao_preenchida(edital, quantidade=1, *, lista_id=None, especie=None, desfaz=None):
    return VagaNaoPreenchida.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        especie=especie or nomes.NAO_PREENCHIDA_DECLARACAO,
        desfaz=desfaz,
        quantidade=quantidade,
        fundamento="Ninguém mais pode ocupar a vaga da linha geral.",
        versao=effective_version(edital_id=edital.id),
        registrado_por="teste",
        registrado_em=timezone.now(),
    )


def causas(apuracao):
    return {c["causa"] for c in selectors.causas_de_obsolescencia(apuracao)}


def vigente(edital):
    return selectors.apuracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


@pytest.mark.django_db(transaction=True)
class TestOMovimentoSemApuracao:
    def test_obsoleta_a_vigente_e_entra_na_seguinte(self, cenario, gestor):
        edital, _, _ = cenario
        apurar(edital, gestor)
        assert causas(vigente(edital)) == set()

        movimento = movimento_sem_apuracao(edital)

        assert causas(vigente(edital)) == {nomes.CAUSA_MOVIMENTO_POSTERIOR}
        seguinte = apurar(edital, gestor, chave="155-seguinte", motivo="Vaga destinada")
        assert seguinte["publicadas"] == 3
        assert seguinte["efetivas"] == 5
        assert seguinte["universo"]["movimentosLidos"] == [str(movimento.id)]
        assert causas(vigente(edital)) == set()

    def test_o_desfazimento_devolve_a_vaga(self, cenario, gestor):
        """O ato contrário, com o sentido invertido, é lido como movimento (R-005)."""
        edital, _, _ = cenario
        origem = uuid.uuid4()
        destinacao = movimento_sem_apuracao(edital, origem=origem)
        MovimentoDeVaga.objects.create(
            apuracao=None,
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            especie=nomes.MOVIMENTO_DESFAZIMENTO,
            origem_lista_id=None,
            destino_lista_id=origem,
            quantidade=2,
            causa="Desfazimento da destinação",
            fundamento="Destinação registrada no recorte errado.",
            versao=effective_version(edital_id=edital.id),
            desfaz=destinacao,
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

        declarado = apurar(edital, gestor)

        assert declarado["efetivas"] == 3
        assert len(declarado["universo"]["movimentosLidos"]) == 2

    def test_o_movimento_de_outro_perfil_nao_alcanca_este(self, cenario, gestor):
        edital, _, _ = cenario
        apurar(edital, gestor)

        MovimentoDeVaga.objects.create(
            apuracao=None,
            edital=edital,
            perfil_id=uuid.uuid4(),
            marco_id=MARCO,
            especie=nomes.MOVIMENTO_REVERSAO,
            origem_lista_id=uuid.uuid4(),
            destino_lista_id=None,
            quantidade=1,
            causa="Outro Perfil",
            fundamento="Item 4.3 do Edital.",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

        assert causas(vigente(edital)) == set()


@pytest.mark.django_db(transaction=True)
class TestAVagaNaoPreenchida:
    def test_obsoleta_pela_setima_causa(self, cenario, gestor):
        edital, _, _ = cenario
        apurar(edital, gestor)

        nao_preenchida(edital)

        assert causas(vigente(edital)) == {nomes.CAUSA_DECLARACAO_POSTERIOR}

    def test_a_seguinte_le_desconta_do_a_ocupar_e_congela(self, cenario, gestor):
        """FR-6326: sai do "a ocupar", e as efetivas ficam — a vaga existe."""
        edital, _, _ = cenario
        declaracao = nao_preenchida(edital, 2)
        desfeita = nao_preenchida(
            edital, 1, especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO, desfaz=declaracao
        )

        declarado = apurar(edital, gestor)

        assert declarado["efetivas"] == 3
        assert declarado["ocupadas"] == 0
        assert declarado["faltando"] == 2
        assert declarado["universo"]["naoPreenchidasLidas"] == [
            str(declaracao.id),
            str(desfeita.id),
        ]
        apuracao = ApuracaoDeOcupacao.objects.get(id=declarado["id"])
        assert apuracao.nao_preenchidas == 1
        assert causas(apuracao) == set()

    def test_sem_declaracao_a_emissao_e_a_de_sempre(self, cenario, gestor):
        """Nenhuma linha gravada, nenhum comportamento mudado: o padrão zero e a lista vazia."""
        edital, _, _ = cenario

        declarado = apurar(edital, gestor)

        assert declarado["faltando"] == 3
        assert declarado["universo"]["naoPreenchidasLidas"] == []
        assert ApuracaoDeOcupacao.objects.get(id=declarado["id"]).nao_preenchidas == 0

    def test_a_declaracao_de_outro_recorte_nao_alcanca_este(self, cenario, gestor):
        """O recorte exato: a da reserva não muda a linha geral."""
        edital, _, _ = cenario
        apurar(edital, gestor)

        nao_preenchida(edital, lista_id=uuid.uuid4())

        assert causas(vigente(edital)) == set()

    def test_a_apuracao_anterior_a_155_so_e_obsoleta_com_declaracao(self, cenario, gestor):
        edital, _, _ = cenario
        apurar(edital, gestor)
        atual = vigente(edital)
        universo = dict(atual.universo)
        universo.pop("naoPreenchidasLidas", None)
        # Em memória: a apuração é append-only, e o que se simula é a linha gravada antes da `155`.
        atual.universo = universo

        assert causas(atual) == set()
        nao_preenchida(edital)
        assert causas(atual) == {nomes.CAUSA_DECLARACAO_POSTERIOR}

    @pytest.mark.skipif(connection.vendor != "postgresql", reason="nome de constraint")
    def test_o_banco_recusa_ocupadas_e_nao_preenchidas_alem_das_efetivas(self, cenario, gestor):
        """`ck_apuracao_ocupadas_no_limite` com as duas parcelas: ninguém conta além do que há."""
        edital, _, _ = cenario
        apurar(edital, gestor)
        base = vigente(edital)
        campos = {
            campo.name: getattr(base, campo.name)
            for campo in ApuracaoDeOcupacao._meta.concrete_fields
            if campo.name not in ("id", "apuracao_anterior", "motivo_da_sucessao")
        }

        with (
            pytest.raises(IntegrityError, match="ck_apuracao_ocupadas_no_limite"),
            transaction.atomic(),
        ):
            ApuracaoDeOcupacao.objects.create(
                **{**campos, "ocupadas": 2, "nao_preenchidas": 2},
                apuracao_anterior=base,
                motivo_da_sucessao="Teste do limite",
            )
