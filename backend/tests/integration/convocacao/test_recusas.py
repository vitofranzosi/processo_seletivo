"""As recusas da convocação, uma por vez e com o código nomeado (019, contrato §3).

**A recusa é o produto, tanto quanto o ato.** Convocar a pessoa errada não dá erro nenhum: dá um
Edital cumprido fora da ordem que ele publicou, e quem descobre é quem foi pulado. Cada recusa
abaixo existe porque há um caminho pelo qual o certame sairia do trilho em silêncio.

**Ficam em `integration/` e não em `unit/`**, ao contrário do que o `tasks.md` escreveu: as sete
recusas são da camada de aplicação e leem apuração, corte, ordem e Resultado do banco. É onde a
`016` já pôs as dela, pela mesma razão.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.application.efeitos import registrar_efeito
from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


def fila_do(edital):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return contexto["fila"], contexto


def test_o_cenario_tem_uma_vaga_faltante_e_dois_chamaveis(cenario):
    """A premissa dos demais testes, dita em voz alta — e medida, não suposta."""
    edital, _, _ = cenario
    fila, contexto = fila_do(edital)

    assert contexto["apuracao"].efetivas == 3
    assert contexto["apuracao"].ocupadas == 2
    assert contexto["apuracao"].faltando == 1
    assert len(fila) == 2, "os dois que a faixa alcançou, nenhum deles ainda chamado"


class TestAApuracao:
    def test_recorte_sem_apuracao_recusa(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        """**Não é o mesmo que "não há vaga": é não saber**, e a recusa diz isso (`FR-266`).

        Chamar para vaga que ninguém apurou é prometer o que não se sabe existir.
        """
        from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

        edital, _, inscricoes = montar_cenario_da_ocupacao(
            gestor, api_client, manager_headers, process_payload, prefixo="sem-apuracao"
        )

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, inscricoes[0], idempotency_key="sem-apuracao-convocar")

        assert erro.value.code == nomes.APURACAO_AUSENTE

    def test_apuracao_obsoleta_recusa_e_nomeia_a_causa(self, cenario, gestor):
        """A apuração vigente já se sabe para trás: o número novo sai na emissão seguinte.

        **Convocar sobre ela chamaria a pessoa que a lista de ontem indicava.** O caminho de saída
        é emitir, e a mensagem nomeia a causa para que quem lê saiba qual.
        """
        edital, _, inscricoes = cenario
        registrar_efeito(
            edital=edital,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=None,
            inscricao_id=uuid.uuid4(),
            especie=nomes_da_ocupacao.EFEITO_EXCLUSAO,
            fundamento="Desistência expressa da titular",
            ato_de_origem_id=uuid.uuid4(),
            rotulo_da_origem="desfecho de convocação",
            registrado_por="teste",
            registrado_em=timezone.now(),
        )

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, inscricoes[0], idempotency_key="obsoleta-convocar")

        assert erro.value.code == nomes.APURACAO_OBSOLETA
        assert nomes_da_ocupacao.CAUSA_EFEITO_POSTERIOR in erro.value.detail


class TestAOrdem:
    def test_marco_sem_ordem_vigente_recusa(self, cenario, gestor):
        """**Sem ordem não há de onde tirar quem é o próximo** (`FR-265`)."""
        edital, _, inscricoes = cenario

        with pytest.raises(DomainError) as erro:
            convocar(
                edital,
                gestor,
                inscricoes[0],
                marco_id=str(uuid.uuid4()),
                idempotency_key="sem-ordem-convocar",
            )

        assert erro.value.code == nomes.ORDEM_NAO_VIGENTE

    def test_fora_da_faixa_recusa(self, cenario, gestor):
        """**Convocar fora da faixa é selecionar, e seleção é ato da `014`** (`FR-265`).

        O quarto inscrito do cenário não foi avaliado: ele não tem Resultado, não está na faixa, e
        chamá-lo contornaria o corte publicado sem que nada o registrasse como seleção.
        """
        edital, _, inscricoes = cenario

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, inscricoes[3], idempotency_key="fora-da-faixa-convocar")

        assert erro.value.code == nomes.FORA_DA_FAIXA

    def test_precedencia_na_ordem_recusa_e_diz_quantos_estao_antes(self, cenario, gestor):
        """**Pular alguém em silêncio é o defeito; pular não é** (`FR-267`).

        A mensagem diz quantos estão antes porque quem conduz o certame precisa saber o que fazer:
        convocá-los, ou registrar o desfecho que os tirou da fila.
        """
        edital, _, _ = cenario
        fila, _ = fila_do(edital)

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, fila[1], idempotency_key="precedencia-convocar")

        assert erro.value.code == nomes.PRECEDENCIA_NA_ORDEM
        assert "1 Inscrição" in erro.value.detail

    def test_a_precedencia_e_admitida_com_fundamento_registrado_no_ato(self, cenario, gestor):
        """A `FR-267` admite a exceção *"salvo fundamento registrado no ato"*.

        **Não bastaria exigir fundamento**, que já é obrigatório em toda convocação: lida assim, a
        recusa nunca dispararia. O que a torna real é quem convoca ter de declarar que sabe que
        está passando à frente — e o ato registra isso na trilha.
        """
        edital, _, _ = cenario
        fila, _ = fila_do(edital)

        declarado = convocar(
            edital,
            gestor,
            fila[1],
            justifica_precedencia=True,
            fundamento="Convocação antecipada por decisão da comissão, ata de 12/09/2026.",
            idempotency_key="precedencia-justificada",
        )

        assert declarado["inscricao"] == str(fila[1])


class TestADuplicidade:
    def test_convocacao_vigente_existente_recusa(self, cenario, gestor):
        """`FR-268`: duas convocações vigentes para a mesma pessoa no mesmo recorte, nunca."""
        edital, _, _ = cenario
        fila, _ = fila_do(edital)
        convocar(edital, gestor, fila[0], idempotency_key="primeira")

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, fila[0], idempotency_key="segunda")

        assert erro.value.code == nomes.CONVOCACAO_VIGENTE_EXISTENTE

    def test_com_motivo_a_segunda_sucede_a_primeira_sem_tocar_nela(self, cenario, gestor):
        """**Correção é sucessão** (`FR-272`), e é a mesma forma que a apuração da `016` usa.

        A anterior continua legível, e é ela que explica o que foi corrigido e por quê.
        """
        edital, _, _ = cenario
        fila, _ = fila_do(edital)
        primeira = convocar(edital, gestor, fila[0], idempotency_key="raiz")

        segunda = convocar(
            edital,
            gestor,
            fila[0],
            motivo="Vencimento informado com o ano errado.",
            idempotency_key="sucessora",
        )

        assert segunda["sucede"] == primeira["id"]
        _, contexto = fila_do(edital)
        vigentes = selectors.vigentes(contexto["convocacoes"])
        assert [str(c.id) for c in vigentes] == [segunda["id"]]
        assert len(contexto["convocacoes"]) == 2, "a anterior continua legível"


class TestODeficit:
    def test_o_titular_e_chamavel_mesmo_com_faltando_zero(self, cenario_com_suplente, gestor):
        """**A primeira convocação de todo certame acontece com `faltando` em zero.**

        Pela contagem da `016` o titular ocupa vaga desde a emissão da apuração — antes de ser
        chamado. Exigir déficit para convocá-lo recusaria a chamada de quem já tem a vaga, que é
        exatamente o ato que a US1 existe para praticar. A `FR-266` confirma: ela nomeia só duas
        recusas ligadas à apuração, e nenhuma delas é ausência de déficit.
        """
        edital, _, _ = cenario_com_suplente
        fila, contexto = fila_do(edital)

        assert contexto["apuracao"].faltando == 0
        assert convocar(edital, gestor, fila[0], idempotency_key="titular-sem-deficit")

    def test_o_suplente_sem_vaga_faltante_e_recusado(self, cenario_com_suplente, gestor):
        """`sem_deficit`: chamar quem **acrescentaria** um ocupante exige vaga que o receba."""
        edital, _, _ = cenario_com_suplente
        fila, _ = fila_do(edital)
        convocar(edital, gestor, fila[0], idempotency_key="titular-primeiro")
        fila, _ = fila_do(edital)

        with pytest.raises(DomainError) as erro:
            convocar(
                edital,
                gestor,
                fila[0],
                especie=nomes.SUPLENCIA,
                idempotency_key="suplente-sem-deficit",
            )

        assert erro.value.code == nomes.SEM_DEFICIT

    def test_esgotada_a_fila_a_recusa_nomeia_o_esgotamento(self, cenario, gestor):
        """`lista_alcancada_esgotada`, e **ela vem antes de `fora_da_faixa`** de propósito.

        Quem tenta convocar alguém de fora da faixa costuma estar fazendo isso justamente porque a
        lista esgotou. Responder *"essa pessoa não está na faixa"* o manda investigar a pessoa,
        quando o que ele precisa saber é que não há mais ninguém e que o caminho é pedir a faixa
        seguinte à `014`.
        """
        edital, _, _ = cenario
        fila, contexto = fila_do(edital)
        assert contexto["apuracao"].faltando == 1
        # Os dois da fila são titulares: nenhum deles acrescenta ocupante, e os dois passam mesmo
        # com uma vaga só faltando.
        convocar(edital, gestor, fila[0], idempotency_key="titular-um")
        convocar(
            edital, gestor, fila[1], justifica_precedencia=True, idempotency_key="titular-dois"
        )
        assert fila_do(edital)[0] == [], "a fila esvaziou"

        with pytest.raises(DomainError) as erro:
            convocar(
                edital,
                gestor,
                cenario[2][2],
                especie=nomes.SUPLENCIA,
                idempotency_key="terceiro",
            )

        assert erro.value.code == nomes.LISTA_ALCANCADA_ESGOTADA


class TestAForma:
    def test_especie_desconhecida_e_recusada(self, cenario, gestor):
        edital, _, _ = cenario
        fila, _ = fila_do(edital)

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, fila[0], especie="OUTRA", idempotency_key="especie-invalida")

        assert erro.value.code == nomes.ESPECIE_DE_CONVOCACAO_INVALIDA

    def test_fundamento_vazio_e_recusado(self, cenario, gestor):
        """O *"no interesse da Administração"* do 77/2026 entra aqui, e sem ele a chamada é linha
        de planilha — não ato administrativo."""
        edital, _, _ = cenario
        fila, _ = fila_do(edital)

        with pytest.raises(DomainError) as erro:
            convocar(edital, gestor, fila[0], fundamento="   ", idempotency_key="sem-fundamento")

        assert erro.value.code == nomes.FUNDAMENTO_OBRIGATORIO


class TestODesfechoQueNaoCabeNaChamada:
    """Nem toda espécie cabe em toda convocação — e o enum sozinho não sabe disso.

    **O registro é append-only**: a transição juridicamente impossível entraria uma vez e ficaria,
    com a contagem divergindo do que os Resultados dizem.
    """

    def desfechar(self, edital, gestor, convocacao_id, especie, chave):
        from processo_seletivo.convocacao.application.desfechar import desfechar

        return desfechar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocacao_id,
            especie=especie,
            fundamento="Registrado em processo.",
            idempotency_key=chave,
            correlation_id="teste-convocacao-019",
        )

    def test_a_chamada_para_vaga_nao_termina_em_regularizacao(self, cenario, gestor):
        """Não há indeferimento a suceder: a regularização produziria sucessor de um Resultado que
        estava habilitado."""
        edital, _, _ = cenario
        fila, _ = fila_do(edital)
        convocada = convocar(edital, gestor, fila[0], idempotency_key="inc-vaga")

        with pytest.raises(DomainError) as erro:
            self.desfechar(edital, gestor, convocada["id"], nomes.REGULARIZACAO, "inc-vaga-d")

        assert erro.value.code == nomes.DESFECHO_INCOMPATIVEL_COM_A_CHAMADA

    def test_a_chamada_para_regularizar_nao_termina_em_aceite(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        """**O defeito mais caro dos três.** `ACEITE` inclui na contagem de ocupantes — e ali a
        pessoa continuaria com o Resultado indeferido, ocupando vaga sem habilitação nenhuma."""
        from tests.fixtures.convocacao import montar_cenario_da_convocacao

        edital, _, _ = montar_cenario_da_convocacao(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="incompativel-019",
            indeferidas=(0,),
        )
        _, contexto = fila_do(edital)
        convocada = convocar(
            edital,
            gestor,
            contexto["regularizaveis"][0],
            especie=nomes.PARA_REGULARIZAR,
            idempotency_key="inc-reg",
        )

        with pytest.raises(DomainError) as erro:
            self.desfechar(edital, gestor, convocada["id"], nomes.ACEITE, "inc-reg-d")

        assert erro.value.code == nomes.DESFECHO_INCOMPATIVEL_COM_A_CHAMADA

    def test_o_nao_atendimento_antes_do_envio_e_recusado(self, cenario, gestor):
        """`FR-269a`: sem envio o prazo não corre, e não há não atendimento a registrar.

        Dar por não atendida uma chamada que nunca partiu puniria a pessoa por uma falha do sistema.
        """
        edital, _, _ = cenario
        fila, _ = fila_do(edital)
        convocada = convocar(edital, gestor, fila[0], idempotency_key="prem-conv")

        with pytest.raises(DomainError) as erro:
            self.desfechar(edital, gestor, convocada["id"], nomes.NAO_ATENDIMENTO, "prem-d")

        assert erro.value.code == nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO

    def test_o_nao_atendimento_antes_do_vencimento_e_recusado(self, cenario, gestor, settings):
        """E depois do envio, antes do vencimento, a pessoa ainda está dentro do prazo dela."""
        from datetime import timedelta

        from django.utils import timezone

        from processo_seletivo.convocacao.application.comunicar import comunicar

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        edital, _, _ = cenario
        fila, _ = fila_do(edital)
        convocada = convocar(
            edital,
            gestor,
            fila[0],
            vencimento=timezone.now() + timedelta(days=5),
            idempotency_key="venc-conv",
        )
        comunicar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocada["id"],
            idempotency_key="venc-comunicar",
            correlation_id="teste",
        )

        with pytest.raises(DomainError) as erro:
            self.desfechar(edital, gestor, convocada["id"], nomes.NAO_ATENDIMENTO, "venc-d")

        assert erro.value.code == nomes.NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO
