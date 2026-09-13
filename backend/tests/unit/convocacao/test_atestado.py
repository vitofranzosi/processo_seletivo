"""O atestado de fato externo: quem concluiu, e o que a ausência dele impede (019, `US5`).

**"O prazo venceu" não é uma pessoa responsável.** O cancelamento de matrícula por inércia decide a
vaga de alguém, e a `D-003` fechou que nenhum desfecho nasce do relógio: alguém competente tem de
concluir que o fato aconteceu, e ficar escrito como tendo concluído.

**A exigência é de forma, e não só de código** (`T078`). A constraint do banco recusa inércia sem
atestado para quem chegue por fora da aplicação — e num registro append-only o inválido entra uma
vez e fica.
"""

import pytest

from processo_seletivo.convocacao.domain import nomes, prazo
from processo_seletivo.convocacao.models import AtestadoDeFatoExterno, DesfechoDaConvocacao


class TestAInerciaExigeAtestadoPorForma:
    """`T078`, `FR-277`: fato externo sem atestante não entra — nem por SQL direto."""

    def test_a_constraint_amarra_a_inercia_ao_atestado(self):
        formas = {c.name: str(c.condition) for c in DesfechoDaConvocacao._meta.constraints}

        assert "ck_desfecho_inercia_exige_atestado" in formas
        condicao = formas["ck_desfecho_inercia_exige_atestado"]
        assert nomes.INERCIA in condicao
        assert "atestado__isnull" in condicao

    def test_os_outros_seis_desfechos_nao_exigem_atestado(self):
        """A exigência é da inércia, e só dela.

        Estendê-la ao não atendimento colapsaria os dois desfechos que a `D-011` mandou manter
        distintos — e o não atendimento se mede contra o vencimento informado, que o sistema tem.
        """
        condicao = next(
            str(c.condition)
            for c in DesfechoDaConvocacao._meta.constraints
            if c.name == "ck_desfecho_inercia_exige_atestado"
        )

        for especie in nomes.ESPECIES_DE_DESFECHO:
            if especie != nomes.INERCIA:
                assert especie not in condicao

    def test_o_atestado_exige_atestante_e_conclusao(self):
        """**Sem atestante não há atestado** (`D-004`), e o banco o diz por forma."""
        formas = {c.name: str(c.condition) for c in AtestadoDeFatoExterno._meta.constraints}

        assert "ck_atestado_com_atestante" in formas
        assert "ck_atestado_com_conclusao" in formas
        assert "ck_atestado_especie" in formas

    def test_o_atestado_e_append_only(self):
        """Reescrevê-lo mudaria, sem rastro, quem concluiu o quê sobre a vaga de alguém."""
        import uuid

        atestado = AtestadoDeFatoExterno(id=uuid.uuid4())
        atestado._state.adding = False

        with pytest.raises(TypeError, match="append-only"):
            atestado.save()


class TestODecursoNaoCancelaNada:
    """`T079`, `FR-274`, `D-003`: nenhum relógio tem competência para tirar vaga de ninguém.

    **É a decisão que separa esta feature de um `cron`.** O sistema mostra que o vencimento passou;
    o que acontece a partir disso é ato de quem conduz o certame, com fundamento e autoria.
    """

    def test_o_vencimento_decorrido_e_estado_de_leitura(self):
        from datetime import UTC, datetime, timedelta

        envio = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)

        estado = prazo.estado(
            tem_desfecho=False,
            enviado_em=envio,
            vencimento=envio + timedelta(days=1),
            agora=envio + timedelta(days=5),
        )

        assert estado == nomes.CONVOCADO_VENCIMENTO_DECORRIDO
        assert estado not in nomes.ESPECIES_DE_DESFECHO

    def test_nenhuma_funcao_do_dominio_produz_desfecho_a_partir_do_relogio(self):
        """**A ausência é a regra**, e este teste a prende no lugar mais cedo que existe.

        Quem acrescentar um `cancelar_por_decurso` não é barrado ao escrevê-lo — é barrado quando
        alguém perder a vaga por um relógio, que é o modo de falha mais tardio possível.
        """
        from processo_seletivo.convocacao.application import desfechar as modulo

        exportado = set(getattr(modulo, "__all__", ()))

        assert exportado == {"desfechar"}
        for proibido in ("cancelar_por_decurso", "expirar", "vencer", "decorrer"):
            assert not hasattr(modulo, proibido)

    def test_a_inercia_nao_se_mede_pelo_vencimento_da_convocacao(self):
        """`D-011`: são dois desfechos, e o que os separa é o fato que cada um olha.

        O não atendimento olha o vencimento informado na convocação — que o sistema tem. A inércia
        olha um fato posterior à matrícula, que aconteceu fora daqui e que alguém atestou.
        """
        assert nomes.INERCIA != nomes.NAO_ATENDIMENTO
        assert nomes.INERCIA in nomes.ESPECIES_DE_DESFECHO
        assert nomes.NAO_ATENDIMENTO in nomes.ESPECIES_DE_DESFECHO
