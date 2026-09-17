"""O degrau 16 acrescenta o Requerimento de Matrícula ao acervo antigo (029, `FR-368`).

**Por que este arquivo existe.** A feature acrescentou um campo à forma canônica publicada, e toda
mudança de forma exige subir a `SCHEMA_VERSION` **e** escrever o degrau que eleva o que já está
publicado. Sem o degrau, conteúdo de antes e de depois conviveriam sob o mesmo número, e
`VERSOES_ELEVAVEIS` passaria a mentir sobre o que sabe elevar — defeito que só apareceria meses
depois, numa consulta histórica.

**O valor elevado é `null`, e a chave existe.** `null` diz que aquele Edital **não exige**
requerimento, o que é verdade sobre todos os publicados antes deste degrau: a capacidade não
existia. Elevar **sem** a chave deixaria o acervo antigo com uma forma que o emissor de hoje não
produz — e a grafia da ausência no conteúdo publicado é a chave presente com valor nulo, como
`vacancyReversion` e `callForm`.

Este achado faltou nas três primeiras passadas da pesquisa desta feature, e é o que o `T-014`
registra: as tarefas saíram dos módulos que a feature toca, e o repositório também cobra os módulos
que observam toda feature.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import elevar
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = pytest.mark.contract

CHAVE = "matriculationRequest"


def conteudo(versao, **extra):
    return {"schemaVersion": versao, "title": "Edital do acervo", **extra}


class TestODegrauAcrescentaAChave:
    def test_conteudo_anterior_ganha_a_chave_com_null(self):
        elevado = elevar(conteudo(15))

        assert CHAVE in elevado, "a chave precisa existir: ausência não é a grafia deste contrato"
        assert elevado[CHAVE] is None
        assert elevado["schemaVersion"] == SCHEMA_VERSION

    def test_o_acervo_mais_antigo_tambem_chega_elevado(self):
        """Do degrau de origem até hoje, e não só do 15: a elevação é cumulativa."""
        elevado = elevar(conteudo(4))

        assert elevado[CHAVE] is None
        assert elevado["schemaVersion"] == SCHEMA_VERSION


class TestOQueODegrauNaoFaz:
    def test_conteudo_que_ja_declara_preserva_o_que_declarou(self):
        declarado = {"moment": "AT_ENROLLMENT", "declarationText": "Declaro, sob as penas da Lei…"}

        elevado = elevar(conteudo(SCHEMA_VERSION, matriculationRequest=declarado))

        assert elevado[CHAVE] == declarado

    def test_conteudo_na_versao_corrente_com_null_permanece_null(self):
        elevado = elevar(conteudo(SCHEMA_VERSION, matriculationRequest=None))

        assert elevado[CHAVE] is None

    def test_a_elevacao_e_idempotente(self):
        """Elevar o já elevado não muda nada — e é o que permite ler o acervo sem reescrevê-lo."""
        uma_vez = elevar(conteudo(15))

        assert elevar(uma_vez) == uma_vez

    def test_versao_desconhecida_atravessa_intacta(self):
        """A recusa mora em `_assert_versao_canonica`: carimbar aqui afirmaria forma inexistente."""
        estranho = conteudo(SCHEMA_VERSION + 99)

        assert elevar(estranho) == estranho
