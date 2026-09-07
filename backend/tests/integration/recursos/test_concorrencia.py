"""As corridas — resolvidas por constraint, idempotência e revisão otimista.

Nenhuma delas ganha mecanismo novo.

Três corridas reais, e nenhuma delas ganha um mecanismo próprio:

```text
dois deferimentos sobre o mesmo Resultado  →  uq_resultado_sucessor_unico, no banco
dois julgadores no mesmo recurso           →  uq_decisao_por_recurso, no banco
o Resultado mudou entre ler e confirmar    →  assinatura do que foi lido, 409
```

**Ler o vigente antes de gravar é conforto de mensagem de erro, e não garantia** — é a mesma frase
que a 015 escreveu sobre `uq_ato_sucessor_unico`, e vale igual aqui: entre a leitura e a gravação
cabe a outra transação inteira. Quem responde é o índice único.

Exige PostgreSQL: `select_for_update` e as *constraints* parciais não existem em SQLite, e um teste
de concorrência que passasse lá provaria o contrário do que afirma.
"""

from decimal import Decimal

import pytest
from django.db import connection

from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos_us4 import assinatura_de, cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=114, codigo="0814"
    )


def corrigir(peca, **extra):
    argumentos = {
        "actor": julgador(),
        "recurso_id": peca["recurso"].id,
        "especie": DecisaoRecurso.Especie.CORRECAO_FIXADA,
        "motivacao": "Revisão da pontuação atribuída.",
        "etapa_id": peca["cenario"]["etapa"],
        "pontuacao": Decimal("82.0000"),
        "assinatura_do_resultado": str(peca["superado"].id),
        "idempotency_key": "concorrencia-us4",
    }
    return julgar(**{**argumentos, **extra})


def test_o_banco_recusa_o_segundo_sucessor_do_mesmo_resultado(peca):
    """A corrida que a leitura prévia não pega: o segundo `INSERT` esbarra no banco.

    A gravação direta simula o que duas transações simultâneas fariam — cada uma tendo lido que
    não havia sucessor. Sem a garantia, existiriam dois vigentes para o mesmo par, e "qual é o
    vigente" deixaria de ter resposta (FR-099).

    **Duas camadas respondem, e a de cima responde primeiro**: `check_stage_result_source` recusa
    com a frase que diz o que aconteceu, e `uq_resultado_sucessor_unico` fica atrás dela, para o
    caso de a trigger ser desativada. A asserção prende a mensagem da trigger porque é ela que de
    fato chega — afirmar o índice aqui seria afirmar o que o teste não exercita.
    """
    from django.db.utils import ProgrammingError

    from tests.fixtures.recursos import superar

    decisao, primeiro = corrigir(peca)

    with pytest.raises(ProgrammingError, match="already has a successor"):
        superar(peca["superado"], decisao, pontuacao=Decimal("83.0000"))

    assert primeiro is not None
    assert ResultadoEtapa.objects.filter(resultado_anterior=peca["superado"]).count() == 1


def test_dois_julgadores_no_mesmo_recurso_produzem_uma_decisao(peca):
    """`uq_decisao_por_recurso` — e o segundo recebe `409`, e não erro de banco."""
    corrigir(peca)

    with pytest.raises(DomainError) as recusa:
        corrigir(
            peca,
            actor=julgador("outra.julgadora"),
            especie=DecisaoRecurso.Especie.INDEFERIDO,
            etapa_id=None,
            pontuacao=None,
            assinatura_do_resultado="",
            idempotency_key="concorrencia-us4-b",
        )

    assert recusa.value.code == "appeal_already_judged"
    assert DecisaoRecurso.objects.count() == 1


def test_o_resultado_alterado_entre_a_leitura_e_a_confirmacao_recusa(peca):
    """A revisão otimista: a decisão não corrige o Resultado errado (FR-100).

    O Resultado do par é superado **por outro recurso da mesma pessoa** — o que ela interpôs contra
    a publicação do marco — enquanto esta tela está aberta. A confirmação carrega a assinatura do
    que foi lido, e a divergência recusa em vez de decidir sobre história.
    """
    lido = str(peca["superado"].id)
    _superar_por_outro_recurso(peca)

    with pytest.raises(DomainError) as recusa:
        corrigir(peca, assinatura_do_resultado=lido)

    assert recusa.value.code == "stale_stage_result"
    assert recusa.value.status == 409
    assert DecisaoRecurso.objects.filter(recurso=peca["recurso"]).count() == 0


def test_o_julgamento_trava_o_processo(peca):
    """A serialização com emitir, publicar e consolidar — o mesmo ponto de bloqueio da 015 e da 017.

    Travar em outro lugar criaria uma segunda ordem de bloqueio, que é como nascem os *deadlocks*
    entre comandos que hoje convivem. O teste lê o SQL emitido: é a única forma de provar o
    bloqueio sem montar duas conexões concorrentes, que tornaria a suíte não determinística.
    """
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as consultas:
        corrigir(peca)

    travas = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "FOR UPDATE" in consulta["sql"] and "processos_processoseletivo" in consulta["sql"]
    ]
    assert travas, "o julgamento precisa travar o Processo, como emitir e publicar já fazem"


def _superar_por_outro_recurso(peca):
    """A mesma pessoa recorreu de dois objetos, e o outro recurso foi julgado primeiro.

    Não é cenário rebuscado: contestar a publicação do marco **e** o próprio resultado da Etapa é o
    que faz quem discorda das duas coisas, e a unicidade é por objeto, não por pessoa. É o caminho
    real pelo qual o Resultado do par muda entre a leitura desta tela e a confirmação dela.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from tests.fixtures.recursos import decidir, superar

    inscricao = peca["inscricao"]
    outro = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        publicacao=peca["publicacao"],
        fundamentacao="A divulgação omitiu a minha posição.",
        assinatura_do_objeto=str(peca["publicacao"].pk),
        idempotency_key="interpor-outro-conc",
    )
    admitir(
        actor=julgador(),
        recurso_id=outro.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(outro),
        idempotency_key="admitir-outro-conc",
    )
    outro.refresh_from_db()
    decisao = decidir(
        outro,
        protegido=peca["superado"],
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        forma="PONTUADA",
        pontuacao=Decimal("75.0000"),
        versao=peca["versao"],
    )
    return superar(peca["superado"], decisao, pontuacao=Decimal("75.0000"))
