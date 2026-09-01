import pytest
from django.db import connections
from rest_framework.test import APIClient


def encerrar_conexoes_da_thread():
    """Fecha as conexões desta thread, inclusive a subjacente do SQLite em memória.

    `connections.close_all()` não basta: para banco em memória o backend do SQLite trata
    `close()` como no-op, porque fechar destruiria o banco. Como o Django monta o banco de teste
    com `cache=shared` quando há threads, ele sobrevive enquanto qualquer conexão continuar
    aberta — e a da thread principal continua. Sem isto cada thread deixa uma `sqlite3.Connection`
    para o coletor de lixo, e o ResourceWarning aparece atribuído ao teste seguinte, que não tem
    relação nenhuma com ele.
    """
    for conexao in connections.all(initialized_only=True):
        subjacente = conexao.connection
        em_memoria = getattr(conexao, "is_in_memory_db", lambda: False)()
        conexao.close()
        if em_memoria and subjacente is not None:
            subjacente.close()
            conexao.connection = None


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager_headers():
    return {
        "HTTP_AUTHORIZATION": "Bearer gestor-a|cefor|processo:criar,processo:ativar,edital:criar",
        "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0001",
        "HTTP_X_CORRELATION_ID": "test-correlation-id",
    }


@pytest.fixture
def process_payload():
    return {
        "institutionalCode": "PS-2026-001",
        "title": "Processo Seletivo 2026",
        "firstEdital": {"number": "01", "year": 2026, "title": "Primeiro Edital"},
    }


# ---------------------------------------------------------------------------
# A jornada do candidato (009). Ficam aqui, e não num conftest de diretório, porque integração e
# autorização exercitam as mesmas precondições — e fixture só é vista do conftest da raiz ou do
# próprio diretório.
# ---------------------------------------------------------------------------


@pytest.fixture
def raiz_de_arquivos(settings, tmp_path):
    """Cada teste com a sua raiz de arquivos.

    O armazenamento resolve a configuração a cada operação justamente para isto: sem resolver por
    propriedade, `override_settings` não teria efeito e os testes escreveriam todos no mesmo lugar.
    """
    settings.ARQUIVOS_CANDIDATOS_RAIZ = str(tmp_path)
    return tmp_path


@pytest.fixture
def selecao(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada, período aberto, três documentos exigidos com alcances distintos."""
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )


@pytest.fixture
def candidatos_registrados():
    """Maria e João existem como identidades persistidas, e não como declarações (010).

    Não é *autouse*, e a razão é dupla. A abertura de rascunho passou a exigir que a linha da
    identidade exista — sem isso uma inscrição poderia nascer órfã de uma identidade descartada —,
    então os testes da jornada precisam delas. Mas registrá-las em **todo** teste de banco poluiria
    os que contam identidades, e contagem poluída é teste que passa a medir a *fixture*.
    """
    from tests.fixtures.candidato import JOAO, MARIA, registrar

    return [registrar(identidade) for identidade in (MARIA, JOAO)]


@pytest.fixture
def inscricao_de_maria(selecao, candidatos_registrados):
    from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
    from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

    return abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)


@pytest.fixture
def desafio_consumido():
    """Um desafio já validado, portando a decisão pendente da reconciliação (010).

    Fica aqui, e não num conftest de diretório, pelo mesmo motivo das *fixtures* da `009`:
    integração e autorização exercitam as mesmas precondições.
    """
    from processo_seletivo.identidade.application import desafio as servico
    from processo_seletivo.identidade.models import DesafioDeAcesso

    endereco = "maria@exemplo.test"
    _, codigo = servico.solicitar(
        email_canonico=endereco, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    return servico.validar(
        email_canonico=endereco, finalidade=DesafioDeAcesso.Finalidade.ENTRAR, codigo=codigo
    )


# ---------------------------------------------------------------------------
# A organização do trabalho (011). Ficam aqui pela mesma razão das fixtures da 009: integração,
# autorização, interface e aceitação exercitam as mesmas precondições, e fixture só é vista do
# conftest da raiz ou do próprio diretório.
# ---------------------------------------------------------------------------


def ator_institucional(subject, *permissoes, escopo="cefor"):
    from processo_seletivo.seguranca.domain import Actor

    return Actor(subject, escopo, frozenset(permissoes))


@pytest.fixture
def gestor():
    return ator_institucional("carlos", "comissao:gerir")


@pytest.fixture
def auditor():
    return ator_institucional("auditora", "auditoria:consultar")


@pytest.fixture
def sem_nada():
    return ator_institucional("estranho")


@pytest.fixture
def edital_a(db, api_client, manager_headers, process_payload):
    """Processo A publicado, com duas Etapas — A1 e A2."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(api_client, manager_headers, process_payload)


@pytest.fixture
def processo_a(edital_a):
    return edital_a.processo


@pytest.fixture
def edital_b(db, api_client, manager_headers):
    """Processo B, para que "Etapa de outro Processo" seja demonstrável."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0002"},
        {
            "institutionalCode": "PS-2026-002",
            "title": "Outro Processo",
            "firstEdital": {"number": "02", "year": 2026, "title": "Segundo Edital"},
        },
        seed=1,
    )


@pytest.fixture
def etapa_a1():
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A1, 0)


@pytest.fixture
def etapa_a2():
    from tests.fixtures.comissao import ETAPA_A2
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A2, 0)


@pytest.fixture
def etapa_b1():
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    return identificador(ETAPA_A1, 1)


@pytest.fixture
def comissao_de_a(gestor, processo_a):
    """Maria presidente, João membro — a composição dos cenários da spec."""
    from tests.fixtures.comissao import constituir

    return constituir(gestor, processo_a, [("maria", "PRESIDENTE"), ("joao", "MEMBRO")])


@pytest.fixture
def seletor_ligado(settings):
    """O seletor de identidade institucional, que só existe fora de produção.

    Estava no conftest da interface; subiu para cá quando os testes de autorização da 011
    passaram a exercitar as mesmas telas — a autorização por objeto só é demonstrável pelo canal
    do ator, e o canal exige identidade.
    """
    settings.INTERFACE_SELETOR_IDENTIDADE = True
