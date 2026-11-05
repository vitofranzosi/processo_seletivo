"""As duas peças puras da correção pela tela (120): a espécie da sucessora e a assinatura da prévia.

**A tela e o comando chegam à mesma espécie, ou a assinatura nunca casa** (`R-004`). E a assinatura
muda com cada um dos cinco componentes que fixam o fundamento e a comunicação (`FR-3857`, `R-003`)
— e só com eles: o complemento viaja no próprio formulário, e não entra nela.
"""

import inspect
import uuid
from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.domain import alcance, nomes
from processo_seletivo.convocacao.domain.especie import especie_da_sucessora
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)

A, B, C = (uuid.UUID(int=n) for n in (1, 2, 3))


def _anterior(especie):
    return SimpleNamespace(especie=especie)


class TestAEspecieDaSucessora:
    def test_quem_passou_a_ocupar_e_chamado_para_vaga_inicial(self):
        """O suplente que a contagem nova pôs entre os ocupantes: a sucessora diz o que vale."""
        especie = especie_da_sucessora(
            A,
            ocupando={A},
            alcancados=[A, B],
            regularizaveis=[],
            anterior=_anterior(nomes.SUPLENCIA),
        )

        assert especie == nomes.VAGA_INICIAL

    def test_quem_esta_na_faixa_sem_ocupar_e_chamado_para_vaga_que_vagou(self):
        especie = especie_da_sucessora(
            B,
            ocupando={A},
            alcancados=[A, B],
            regularizaveis=[],
            anterior=_anterior(nomes.SUPLENCIA),
        )

        assert especie == nomes.SUPLENCIA

    def test_sem_posicao_a_especie_e_a_da_convocacao_corrigida(self):
        """**Corrigir não muda a posição.** Quem tem chamada em aberto para regularizar saiu da fila
        dos regularizáveis por ter sido chamado, e a espécie da raiz é a dela."""
        especie = especie_da_sucessora(
            C,
            ocupando=set(),
            alcancados=[],
            regularizaveis=[],
            anterior=_anterior(nomes.PARA_REGULARIZAR),
        )

        assert especie == nomes.PARA_REGULARIZAR


BASE = {
    "convocacao_id": A,
    "apuracao_id": B,
    "versao_id": C,
    "forma": FORMA_POR_MENSAGEM_INDIVIDUAL,
    "especie": nomes.SUPLENCIA,
}


class TestAAssinaturaDaCorrecao:
    @pytest.mark.parametrize(
        ("campo", "outro"),
        [
            ("convocacao_id", uuid.UUID(int=9)),
            ("apuracao_id", uuid.UUID(int=9)),
            ("versao_id", uuid.UUID(int=9)),
            ("forma", FORMA_POR_PUBLICACAO),
            ("especie", nomes.VAGA_INICIAL),
        ],
    )
    def test_a_assinatura_muda_com_cada_componente(self, campo, outro):
        assert alcance.assinatura_da_correcao(**{**BASE, campo: outro}) != (
            alcance.assinatura_da_correcao(**BASE)
        )

    def test_a_assinatura_nao_depende_do_complemento(self):
        """O complemento não é argumento: ele viaja no formulário e entra no fundamento gravado, de
        modo que o texto gravado continua o mostrado sem que a assinatura o leve. Se alguém o
        acrescentasse, a tela — que assina antes de a pessoa digitar — nunca casaria."""
        parametros = inspect.signature(alcance.assinatura_da_correcao).parameters

        assert set(parametros) == set(BASE)

    def test_o_identificador_vale_como_texto_ou_como_uuid(self):
        """O formulário devolve texto; o comando lê `UUID`. Os dois dão a mesma assinatura."""
        como_texto = {chave: str(valor) for chave, valor in BASE.items()}

        assert alcance.assinatura_da_correcao(**como_texto) == alcance.assinatura_da_correcao(
            **BASE
        )

    def test_nao_e_a_assinatura_dos_vencidos(self):
        """Um gesto não serve de prova de outro: a assinatura dos vencidos tem o seu gesto."""
        dos_vencidos = alcance.assinatura(
            gesto="correcao",
            apuracao_id=B,
            versao_id=C,
            forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
            identidades=[A],
        )

        assert dos_vencidos != alcance.assinatura_da_correcao(**BASE)
