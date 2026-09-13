"""A quinta causa de obsolescência: efeito posterior à apuração vigente (019, `D-006`).

**Nenhuma apuração é reescrita quando alguém desiste ou aceita.** A vigente passa a aparecer
obsoleta, com a causa dita, e o número novo sai na **emissão seguinte**. É o mesmo desenho da
quarta causa — obsolescência em vez de orquestração —, e é o que impede a `019` de precisar de
`UPDATE` numa tabela append-only.

**A comparação é por id congelado, e não por instante.** Um efeito gravado na mesma transação de
uma apuração pareceria posterior a ela mesma se o critério fosse o relógio. É a disciplina que
`_movimento_posterior` já usa, e o defeito que ela evita não dá erro: dá uma apuração que nasce
obsoleta.
"""

import uuid
from types import SimpleNamespace

import pytest
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import EfeitoDeOcupacao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo

PERFIL = uuid.uuid4()
MARCO = uuid.uuid4()


def test_a_causa_tem_nome_proprio_e_nao_reusa_a_do_movimento():
    """Causas nomeadas, e nunca "divergências": a `018` já pagou esse preço.

    Efeito e movimento chegam por caminhos diferentes, e quem lê a tela precisa saber qual dos dois
    deixou o número para trás — porque a providência é outra.
    """
    assert nomes.CAUSA_EFEITO_POSTERIOR == "efeito_posterior"
    assert nomes.CAUSA_EFEITO_POSTERIOR != nomes.CAUSA_MOVIMENTO_POSTERIOR


@pytest.mark.django_db
class TestOEfeitoPosterior:
    @pytest.fixture
    def edital(self):
        agora = timezone.now()
        processo = ProcessoSeletivo.objects.create(
            institution_scope="cefor",
            institutional_code="PS-019-OBSOLESCENCIA",
            title="Processo da obsolescência",
            created_at=agora,
            created_by="teste",
            last_changed_at=agora,
        )
        return Edital.objects.create(
            processo=processo,
            institution_scope="cefor",
            number="019-obs",
            year=2026,
            title="Edital da obsolescência",
            created_at=agora,
            created_by="teste",
            last_edited_by="teste",
        )

    def efeito(self, edital, *, lista_id=None):
        return EfeitoDeOcupacao.objects.create(
            edital=edital,
            perfil_id=PERFIL,
            marco_id=MARCO,
            lista_id=lista_id,
            inscricao_id=uuid.uuid4(),
            especie=nomes.EFEITO_EXCLUSAO,
            fundamento="Desistência expressa",
            ato_de_origem_id=uuid.uuid4(),
            rotulo_da_origem="desfecho de convocação",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

    def apuracao(self, edital, *, lidos=(), lista_id=None):
        """A apuração vista pela função: o recorte e os ids que ela congelou, e nada mais."""
        return SimpleNamespace(
            edital_id=edital.id,
            perfil_id=PERFIL,
            marco_id=MARCO,
            lista_id=lista_id,
            universo={"efeitosLidos": [str(i) for i in lidos]},
        )

    def test_efeito_que_a_apuracao_nao_leu_a_torna_obsoleta(self, edital):
        novo = self.efeito(edital)

        assert selectors._efeito_posterior(self.apuracao(edital)) is True
        assert selectors._efeito_posterior(self.apuracao(edital, lidos=[novo.id])) is False

    def test_o_efeito_que_ela_leu_nao_a_torna_obsoleta(self, edital):
        """Sem isto, toda apuração nasceria obsoleta pelo efeito que ela mesma acabou de ler."""
        lido = self.efeito(edital)
        outro = self.efeito(edital)

        assert selectors._efeito_posterior(self.apuracao(edital, lidos=[lido.id])) is True
        assert (
            selectors._efeito_posterior(self.apuracao(edital, lidos=[lido.id, outro.id])) is False
        )

    def test_efeito_de_outro_recorte_nao_alcanca_este(self, edital):
        """O efeito é do recorte, e recorte é `(perfil, marco, lista)`.

        Um efeito na lista reservada não torna obsoleta a apuração da ampla: são conjuntos de
        ocupantes distintos, e confundi-los emitiria sucessora à toa — ato irreversível.
        """
        self.efeito(edital, lista_id=uuid.uuid4())

        assert selectors._efeito_posterior(self.apuracao(edital)) is False

    def test_apuracao_anterior_a_feature_nao_tem_efeitos_lidos(self, edital):
        """E qualquer efeito a torna obsoleta. Está certo: ele é mesmo posterior a ela."""
        self.efeito(edital)
        antiga = SimpleNamespace(
            edital_id=edital.id,
            perfil_id=PERFIL,
            marco_id=MARCO,
            lista_id=None,
            universo={"movimentosLidos": []},
        )

        assert selectors._efeito_posterior(antiga) is True
