"""As duas corridas que o `command_context()` sozinho **não** serializa (029, T036).

**Por que duas travas, e não uma.** O envio do requerimento lê duas coisas que outra transação pode
mudar debaixo dele: a **versão vigente do Edital**, que uma Retificação publica, e a **chamada em
aberto**, que um desfecho fecha. Sem trava, o envio grava um par incoerente — a versão aceita não é
a do texto cujo resumo se guardou — ou confirma sobre uma chamada que já foi respondida. Nos dois
casos nada acusa: o requerimento fica no banco parecendo correto.

`FOR SHARE` nas duas, e não `FOR UPDATE`: candidatos não se bloqueiam entre si, e as duas conflitam
com o `FOR UPDATE` de quem muda a norma (a Retificação) ou o desfecho (`comando_de_comissao`).

**Este arquivo precisa de duas conexões**, e por isso `transaction=True` e threads de verdade: o
`django_db` comum compartilha uma transação, e as duas gravações seriam sequenciais sobre o mesmo
snapshot — a corrida não aconteceria e o teste passaria sem exercer nada.

**E precisa de PostgreSQL.** `select_for_update` é inócuo no SQLite, que serializa a escrita
inteira: lá estas corridas não existem, e o teste não provaria o invariante — ele quebraria, por um
motivo sem relação com o que ele protege.
"""

import threading

import pytest
from django.db import connection

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.requerimentos.application import exigencia, preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import encerrar_conexoes_da_thread
from tests.fixtures.candidato import MARIA
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a corrida exige as travas do PostgreSQL"
)


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O recorte do 77/2026, com o Edital declarando o requerimento **na convocação**."""
    from tests.fixtures.corte import regra
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    def publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=declarar("AT_CALL"),
        )

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="requerimento-029-corrida",
        geral=2,
        cut=regra(surplusCount=1),
        publicar=publicar_declarando,
    )


def preparar(edital, gestor, inscricao, campos, *, chave):
    """Convoca, abre o rascunho e o preenche — tudo menos o aceite."""
    convocar(edital, gestor, inscricao, idempotency_key=chave)
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return Convocacao.objects.filter(inscricao=inscricao).latest("criado_em")


def enviar(inscricao, versao_id, declaracao):
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=versao_id,
        declaracao_exibida=declaracao,
        aceite=True,
    )


def test_retificacao_entre_a_leitura_e_o_envio_nao_produz_par_incoerente(
    cenario, gestor, campos_declarados, api_client
):
    """**(a)** O par `versão aceita` + `resumo da declaração` fecha, retifique-se ou não.

    **Sem threads, e a ausência delas é a correção de um desenho anterior.** A primeira redação
    deste teste disparava a Retificação numa thread paralela, na crença de que só uma trava
    impediria o par incoerente. Não é o caso: o resumo é calculado a partir do **mesmo objeto de
    versão** que se grava, e não de um texto recebido no `POST`. Publicada a Retificação antes ou
    depois da leitura, o que se registra é sempre a versão que a pessoa leu, com o resumo do texto
    daquela versão.

    Trocar as threads por sequência não é abrir mão da garantia; é testar a garantia que existe. A
    paralela testava a trava — e a trava do Edital foi removida justamente porque deadlockava, e
    porque não era ela que sustentava esta propriedade.

    O que continua valendo é a recusa: enviar com a versão **exibida** obsoleta é `edital_updated`,
    e a pessoa relê antes de confirmar.
    """
    from tests.fixtures.publicacao import retify

    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    preparar(edital, gestor, pessoa, campos_declarados, chave="corrida-a")
    antiga = preencher._conteudo(pessoa)
    texto_antigo = preencher.declaracao_publicada(antiga.content)

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": "/matriculationRequest/declarationText",
                "operation": "REPLACE",
                "newValue": "Declaro, sob as penas da Lei, texto retificado.",
            }
        ],
    )

    with pytest.raises(DomainError) as recusa:
        enviar(pessoa, antiga.id, texto_antigo)
    assert recusa.value.code == nomes.EDITAL_ATUALIZADO, "a versão exibida ficou para trás"

    nova = preencher._conteudo(pessoa)
    gravado = enviar(pessoa, nova.id, preencher.declaracao_publicada(nova.content))

    assert gravado.versao_aceita_id == nova.id
    assert gravado.declaracao_hash == preencher.resumo_da_declaracao(
        preencher.declaracao_publicada(nova.content)
    )
    assert gravado.declaracao_hash != preencher.resumo_da_declaracao(texto_antigo), (
        "o resumo é o do texto novo, e o cenário mudou o texto de verdade"
    )


@postgresql_only
def test_desfecho_entre_a_leitura_da_chamada_e_o_commit_nao_confirma_sobre_chamada_fechada(
    cenario, gestor, campos_declarados
):
    """**(b)** O envio não confirma sobre uma chamada que outra transação já fechou.

    Sem o `FOR SHARE` no Processo Seletivo, o envio leria a chamada em aberto, o desfecho
    comitaria, e o requerimento nasceria autorizado por uma convocação concluída — um envio válido
    pendurado num fato que já não existia.
    """
    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    chamada = preparar(edital, gestor, pessoa, campos_declarados, chave="corrida-b")
    versao = preencher._conteudo(pessoa)
    declaracao = preencher.declaracao_publicada(versao.content)
    partida = threading.Barrier(2)
    desfechos = []

    def enviar_o_requerimento():
        partida.wait(timeout=5)
        try:
            enviar(pessoa, versao.id, declaracao)
            desfechos.append(("ok", ""))
        except DomainError as recusa:
            desfechos.append(("recusa", recusa.code))
        except Exception as erro:  # noqa: BLE001
            desfechos.append(("erro", type(erro).__name__))
        finally:
            encerrar_conexoes_da_thread()

    def registrar_o_desfecho():
        partida.wait(timeout=5)
        try:
            desfechar(
                actor=gestor,
                processo_id=edital.processo_id,
                convocacao_id=chamada.id,
                especie=nomes_da_convocacao.DESISTENCIA_EXPRESSA,
                fundamento="Manifestação registrada em processo.",
                idempotency_key="corrida-b-desfecho",
                correlation_id="teste",
            )
        except Exception:  # noqa: BLE001 — perder a corrida é desfecho legítimo
            pass
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=alvo) for alvo in (enviar_o_requerimento, registrar_o_desfecho)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=20)

    assert "erro" not in [tipo for tipo, _ in desfechos], desfechos
    gravado = exigencia.vigente_de(pessoa)
    if gravado.status == nomes.ENVIADO:
        # Envio concluído **implica** que ele chegou antes do desfecho: as duas transações foram
        # serializadas pela trava, e não correram uma por cima da outra.
        assert gravado.convocacao_autorizadora_id == chamada.id
    else:
        assert desfechos == [("recusa", nomes.INDISPONIVEL)], desfechos


@postgresql_only
def test_retificacao_concorrente_de_verdade_nao_produz_par_incoerente(
    cenario, gestor, campos_declarados, api_client
):
    """**(c)** A corrida da `T027`/`T036`, com **duas conexões** — e o que ela afirma mudou.

    A `T027` previa um `FOR SHARE` no Edital para impedir a Retificação de publicar entre a leitura
    da versão e a gravação. Essa trava **não existe**: tomá-la junto com a do Processo produz
    *deadlock* contra as duas ordens de travamento incompatíveis que já convivem neste repositório,
    e o teste a reproduziu nas duas ordens antes de a decisão ser tomada.

    **O que a substituiu é um invariante, e ele é mais forte do que a trava.** O resumo sai do
    **mesmo objeto de versão** que se grava; não há caminho pelo qual `versao_aceita` aponte uma
    versão e `declaracao_hash` resuma o texto de outra. A Retificação pode publicar a qualquer
    instante — antes, durante ou depois — e o par continua fechando.

    **Por isso o que se afirma aqui é o par, e não quem venceu.** Um teste que exigisse uma ordem
    entre as duas transações estaria afirmando a trava removida; este afirma a propriedade que a
    substituiu, e falharia no dia em que alguém voltasse a resumir o texto recebido no `POST`.
    """
    from tests.fixtures.publicacao import retify

    edital, _, inscricoes = cenario
    pessoa = inscricoes[0]
    preparar(edital, gestor, pessoa, campos_declarados, chave="corrida-c")
    versao = preencher._conteudo(pessoa)
    declaracao = preencher.declaracao_publicada(versao.content)
    partida = threading.Barrier(2)
    desfechos = []

    def enviar_o_requerimento():
        partida.wait(timeout=5)
        try:
            enviar(pessoa, versao.id, declaracao)
            desfechos.append(("ok", ""))
        except DomainError as recusa:
            desfechos.append(("recusa", recusa.code))
        except Exception as erro:  # noqa: BLE001 — é justamente o que não pode acontecer
            desfechos.append(("erro", type(erro).__name__))
        finally:
            encerrar_conexoes_da_thread()

    def retificar():
        partida.wait(timeout=5)
        try:
            retify(
                api_client,
                edital,
                [
                    {
                        "targetPath": "/matriculationRequest/declarationText",
                        "operation": "REPLACE",
                        "newValue": "Declaro, sob as penas da Lei, texto retificado no meio.",
                    }
                ],
            )
        except Exception:  # noqa: BLE001 — a Retificação perder a corrida é desfecho legítimo
            pass
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=alvo) for alvo in (enviar_o_requerimento, retificar)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=30)

    assert "erro" not in [tipo for tipo, _ in desfechos], desfechos
    gravado = exigencia.vigente_de(pessoa)
    if gravado.status == nomes.ENVIADO:
        # **O par fecha**: o resumo guardado é o do texto da versão aceita, e de nenhuma outra.
        texto = preencher.declaracao_publicada(gravado.versao_aceita.content)
        assert gravado.declaracao_hash == preencher.resumo_da_declaracao(texto)
    else:
        assert desfechos == [("recusa", nomes.EDITAL_ATUALIZADO)], desfechos
