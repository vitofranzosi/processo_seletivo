"""A trilha da unidade: os atos administrativos que só se liam pelo `psql` (108).

Os atos são produzidos pelos próprios comandos — cadastrar e encerrar a autoridade, sincronizar as
unidades, criar e editar modelos, confirmar e interromper o aviso —, e não gravados à mão: a página
lê o que eles gravam, e um registro escrito pelo teste provaria só o teste. As exceções são a
exclusão do piloto, cujo comando precisa de trocas do piloto, e os eventos de vazamento, que imitam
o que outro escopo grava.

Os acessos (US3) estão em `tests/seguranca/test_trilha_da_unidade_acessos.py`, onde moram o provedor
simulado e as pessoas institucionais.
"""

import re
from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria import selectors as auditoria_selectors
from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from processo_seletivo.avisos.application.interromper import interromper
from processo_seletivo.avisos.application.modelos import (
    criar,
    editar,
    garantir_modelos_iniciais,
    mudar_situacao,
)
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.interface import trilha_da_unidade as tela
from processo_seletivo.interface.identidade import PAPEIS
from processo_seletivo.interface.views import OPERACOES
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.application import autoridades
from processo_seletivo.unidades.application.sincronizacao import sincronizar
from processo_seletivo.unidades.models import Unidade
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import CEFOR, registrar_unidade
from tests.fixtures.avisos import ASSUNTO, CORPO, PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

URL = reverse("interface:trilha-da-unidade")
GESTORA = ator_institucional("ana.gestora", "autoridade:gerir", "aviso:enviar")


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


def _auditor(client, subject="fiscal"):
    identificar(client, subject, ["auditor"])


def _lista(corpo):
    """Só a lista dos atos: o resto da página tem o filtro, que nomeia todos os assuntos."""
    if '<ol class="auditoria"' not in corpo:
        return ""
    return corpo.split('<ol class="auditoria"')[1].split("</ol>")[0]


def _itens(corpo):
    return re.findall(r"<li>(.*?)</li>", _lista(corpo), re.S)


def _cadastrar(nome="Maria Diretora", cargo="Diretora-Geral", chave=None):
    return autoridades.cadastrar(
        actor=GESTORA,
        cargo=cargo,
        nome=nome,
        ato_de_nomeacao="Portaria 12/2026",
        inicio_vigencia=date.today(),
        idempotency_key=chave or str(uuid4()),
        correlation_id="teste-108",
    )


# ---- US1: o Auditor lê os atos ------------------------------------------------------------------


def test_o_cadastro_e_o_encerramento_da_autoridade_dizem_quem_quando_e_o_que_mudou(client):
    autoridade = _cadastrar()
    autoridades.encerrar(
        actor=GESTORA,
        autoridade_id=autoridade.pk,
        fim_vigencia=date.today() + timedelta(days=30),
        idempotency_key=str(uuid4()),
        correlation_id="teste-108",
    )
    _auditor(client)

    resposta = client.get(URL)

    assert resposta.status_code == 200
    itens = _itens(resposta.content.decode())
    assert len(itens) == 2
    encerramento, cadastro = itens
    assert "Encerramento de autoridade" in encerramento
    assert "Cadastro de autoridade" in cadastro
    for item in itens:
        assert "Maria Diretora" in item and "Diretora-Geral" in item
        assert "por <strong>ana.gestora</strong>" in item
    # O fim da vigência, de antes para depois, e nenhum outro dado que não mudou.
    fim = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
    assert "<dt>Fim da vigência</dt><dd>— → " + fim + "</dd>" in encerramento
    assert "<dt>Nome</dt>" not in encerramento


def test_a_sincronizacao_aparece_pela_implantacao_com_os_dados_mudados(client):
    registrar_unidade("campus-a")
    declaradas = {
        "cefor": {**{k: v for k, v in CEFOR.items() if k != "codigo"}, "local": "Serra (ES)"},
        "campus-a": {
            "sigla": "Campus-a",
            "nome": "Unidade campus-a",
            "cabecalho": ["Unidade campus-a"],
            "local": "Vitória (ES)",
            "ativa": True,
        },
        "campus-b": {
            "sigla": "CB",
            "nome": "Campus B",
            "cabecalho": ["Campus B"],
            "local": "Vila Velha (ES)",
            "ativa": True,
        },
    }
    sincronizar(declaradas, correlation_id="teste-108")
    _auditor(client)

    itens = _itens(client.get(URL).content.decode())

    assert len(itens) == 1, "o registro do campus-b é do escopo dele"
    (alteracao,) = itens
    assert "Alteração da unidade" in alteracao
    assert "por <strong>Implantação</strong>" in alteracao
    assert CEFOR["nome"] in alteracao
    assert "<dt>Local</dt><dd>Vitória (ES) → Serra (ES)</dd>" in alteracao


def test_os_modelos_aparecem_pelo_nome_e_sem_o_texto(client):
    garantir_modelos_iniciais(correlation_id="teste-108")
    modelo = criar(
        actor=GESTORA, nome="Convocação geral", assunto="Assunto secreto 108", corpo=CORPO
    )
    editar(
        actor=GESTORA,
        modelo_id=modelo.pk,
        nome="Convocação geral",
        assunto="Assunto secreto 108 (editado)",
        corpo=CORPO + "\nCorpo secreto 108",
    )
    mudar_situacao(actor=GESTORA, modelo_id=modelo.pk, ativo=False)
    _auditor(client)

    corpo = client.get(URL).content.decode()
    itens = _itens(corpo)

    assert len(itens) == 6
    assert "Inativação de modelo de aviso" in itens[0]
    assert "Edição de modelo de aviso" in itens[1]
    assert "Criação de modelo de aviso" in itens[2]
    assert all("Convocação geral" in item for item in itens[:3])
    iniciais = itens[3:]
    assert all("por <strong>Implantação</strong>" in item for item in iniciais)
    assert all("Criação de modelo de aviso" in item for item in iniciais)
    # FR-3164: nem assunto nem corpo, de modelo nenhum.
    assert "secreto" not in corpo
    assert "{nome_do_candidato}" not in corpo


@pytest.fixture
def publicado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    return cenario


def test_o_aviso_confirmado_e_interrompido_nomeia_o_edital_e_nao_o_destinatario(client, publicado):
    edital = publicado["edital"]
    declarado = avisar_resultado(edital, publicado["publicacao"].marco_id)
    interromper(
        actor=PUBLICADORA,
        aviso_id=declarado["aviso"],
        motivo="Texto com erro no nome da etapa.",
        idempotency_key="interromper-108",
        correlation_id="teste-108",
    )
    _auditor(client)

    corpo = client.get(URL).content.decode()
    itens = _itens(corpo)

    assert len(itens) == 2
    interrupcao, confirmacao = itens
    assert "Interrupção de aviso aos candidatos" in interrupcao
    assert "Texto com erro no nome da etapa." in interrupcao
    assert "Confirmação de aviso aos candidatos" in confirmacao
    for item in itens:
        assert f"Edital {edital.number}/{edital.year}, aviso de resultado" in item
        assert "por <strong>publicadora-aviso</strong>" in item
    # FR-3164: nenhum endereço de e-mail e nenhum texto do aviso.
    assert "@" not in _lista(corpo)
    assert ASSUNTO not in corpo
    # E a publicação do resultado é da trilha do Edital, e não desta.
    assert "Publicação" not in _lista(corpo)


def test_a_exclusao_do_piloto_diz_quantos_e_de_quando(client):
    record_event(
        actor=Actor("implantacao", "cefor"),
        permission="implantacao",
        operation="EXCLUIR_REGISTROS_DO_PILOTO",
        aggregate=Unidade.objects.get(codigo="cefor"),
        now=timezone.now(),
        correlation_id="",
        new_state="",
        new_revision=None,
        detalhe={"trocas_excluidas": 7, "relatorio_final_em": "2026-07-01"},
    )
    _auditor(client)

    (item,) = _itens(client.get(URL).content.decode())

    assert "Exclusão dos registros do piloto do assistente" in item
    assert "7 registros excluídos; relatório final de 01/07/2026." in item
    assert CEFOR["nome"] in item


def test_sem_ato_a_pagina_diz_que_nao_ha(client):
    _auditor(client)

    corpo = client.get(URL).content.decode()

    assert "Nenhum ato administrativo registrado para esta unidade." in corpo
    assert '<ol class="auditoria"' not in corpo


# ---- paginação e custo ---------------------------------------------------------------------------


def _vinte_e_um_cadastros():
    return [_cadastrar(nome=f"Autoridade {i:02d}") for i in range(21)]


def test_a_paginacao_nao_repete_nem_pula(client):
    _vinte_e_um_cadastros()
    _auditor(client)

    primeira = client.get(URL).content.decode()
    assert len(_itens(primeira)) == 20
    seguinte = re.search(r'href="(\?[^"]*cursor=[^"]+)"', primeira).group(1).replace("&amp;", "&")
    segunda = client.get(URL + seguinte).content.decode()

    nomes = re.findall(r"Autoridade \d\d", _lista(primeira) + _lista(segunda))
    # Cada nome aparece uma vez por linha (o "sobre o quê"): vinte e um nomes, nenhum repetido.
    assert sorted(set(nomes)) == [f"Autoridade {i:02d}" for i in range(21)]
    assert len(nomes) == 21
    assert "Ver atos anteriores" not in segunda


def test_atos_no_mesmo_instante_ficam_em_ordem_estavel():
    agora = timezone.now()
    unidade = Unidade.objects.get(codigo="cefor")
    for _ in range(3):
        record_event(
            actor=Actor("implantacao", "cefor"),
            permission="implantacao",
            operation="ALTERAR_UNIDADE",
            aggregate=unidade,
            now=agora,
            correlation_id="",
            new_revision=None,
            new_state="ATIVA",
        )
    ator = ator_institucional("fiscal", "auditoria:consultar")

    primeira, cursor = auditoria_selectors.trilha_da_unidade(actor=ator, limit=2)
    segunda, fim = auditoria_selectors.trilha_da_unidade(actor=ator, cursor=cursor, limit=2)

    vistos = [r.event_id for r in primeira + segunda]
    assert len(vistos) == len(set(vistos)) == 3
    assert fim is None


def _consultas_da_pagina(client):
    with CaptureQueriesContext(connection) as capturadas:
        assert client.get(URL).status_code == 200
    return len(capturadas.captured_queries)


def test_o_custo_da_pagina_nao_cresce_com_as_linhas(client, publicado):
    """`FR-3168`, `SC-1023`: uma linha de cada assunto, e depois vinte, custam o mesmo."""
    declarado = avisar_resultado(publicado["edital"], publicado["publicacao"].marco_id)
    aviso = Aviso.objects.get(pk=declarado["aviso"])
    garantir_modelos_iniciais(correlation_id="teste-108")
    _cadastrar()
    sincronizar(
        {"cefor": {**{k: v for k, v in CEFOR.items() if k != "codigo"}, "local": "Serra (ES)"}}
    )
    _auditor(client)
    _consultas_da_pagina(client)  # aquece o que a sessão faz uma vez
    poucas = _consultas_da_pagina(client)

    for _ in range(8):
        _cadastrar()
        record_event(
            actor=PUBLICADORA,
            permission="aviso:enviar",
            operation="AVISO_CONFIRMAR",
            aggregate=aviso,
            now=timezone.now(),
            correlation_id="",
            new_state="",
            new_revision=None,
        )
    assert RegistroAuditoria.objects.filter(institution_scope="cefor").count() >= 20
    muitas = _consultas_da_pagina(client)

    assert len(_itens(client.get(URL).content.decode())) == 20
    assert muitas == poucas


# ---- US2: só a unidade de quem lê ---------------------------------------------------------------


@pytest.mark.parametrize("papel", sorted(set(PAPEIS) - {"auditor"}))
def test_sem_a_permissao_a_recusa_diz_o_que_falta(client, papel):
    identificar(client, "pessoa.qualquer", [papel])

    resposta = client.get(URL)

    assert resposta.status_code == 403
    assert "consultar a trilha de auditoria da unidade" in resposta.content.decode()


def test_so_a_leitura_e_aceita_e_ela_nao_grava_nada(client):
    _cadastrar()
    _auditor(client)
    antes = (RegistroAuditoria.objects.count(), IdempotencyRecord.objects.count())

    assert client.post(URL).status_code == 405
    for parametros in ("", "?assunto=autoridades", "?assunto=xyz"):
        assert client.get(URL + parametros).status_code == 200

    assert (RegistroAuditoria.objects.count(), IdempotencyRecord.objects.count()) == antes


def _gravar_em(escopo, operacao, tipo, *, detalhe=None):
    """Um evento como outro escopo o grava: o tipo é o nome da classe, como em `record_event`."""
    agregado = type(tipo, (), {"pk": uuid4()})()
    return record_event(
        actor=Actor("outra.pessoa", escopo),
        permission="x",
        operation=operacao,
        aggregate=agregado,
        now=timezone.now(),
        correlation_id="",
        new_state="",
        new_revision=None,
        detalhe=detalhe,
    )


def test_nada_de_outra_unidade_de_escopo_vazio_ou_da_trilha_do_certame_aparece(client):
    registrar_unidade("campus-a")
    _gravar_em("campus-a", "CADASTRAR_AUTORIDADE", "AutoridadeHabilitada")
    _gravar_em("campus-a", "ACESSO_CONCEDER", "Vinculo", detalhe={"escopo": "campus-a"})
    _gravar_em("institucional", "ACESSO_CONCEDER", "Vinculo", detalhe={"escopo": "campus-a"})
    # A credencial do candidato, com escopo vazio (010), e a publicação, que é da trilha do Edital.
    _gravar_em("", "TROCAR_CREDENCIAL", "Credencial")
    _gravar_em("cefor", "PUBLICAR", "Edital")
    _gravar_em("cefor", "COMISSAO_INCLUIR_MEMBRO", "MembroComissao")
    _auditor(client)

    for parametros in (
        "",
        "?unidade=campus-a",
        "?escopo=campus-a",
        "?assunto=acessos&unidade=campus-a",
    ):
        corpo = client.get(URL + parametros).content.decode()
        assert _itens(corpo) == [], parametros


def test_o_escopo_vem_do_ator_e_nao_do_pedido():
    """`FR-3154`: o seletor não tem parâmetro de unidade; quem está no institucional não lê nada."""
    _gravar_em("institucional", "PESSOA_SUSPENDER", "SuspensaoDePessoa")
    _gravar_em("institucional", "ACESSO_CONCEDER", "Vinculo", detalhe={"escopo": "institucional"})
    institucional = ator_institucional("adm", "auditoria:consultar", escopo="institucional")

    assert auditoria_selectors.trilha_da_unidade(actor=institucional) == ([], None)


def test_no_escopo_institucional_a_pagina_recusa(client):
    identificar(client, "fiscal", ["auditor"], escopo="institucional")

    assert client.get(URL).status_code == 403


def test_o_cursor_adulterado_e_recusado(client):
    _auditor(client)

    assert client.get(URL + "?cursor=nao-e-cursor").status_code == 400


# ---- US4: o filtro ------------------------------------------------------------------------------


def test_cada_assunto_mostra_so_os_seus_atos_e_o_filtro_continua_na_paginacao(client):
    garantir_modelos_iniciais(correlation_id="teste-108")
    _vinte_e_um_cadastros()
    _auditor(client)

    so_modelos = client.get(URL + "?assunto=modelos").content.decode()
    assert len(_itens(so_modelos)) == 3
    assert "Cadastro de autoridade" not in _lista(so_modelos)
    assert '<option value="modelos" selected>' in so_modelos
    assert "Limpar" in so_modelos

    autoridades_ = client.get(URL + "?assunto=autoridades").content.decode()
    seguinte = re.search(r'href="(\?[^"]*cursor=[^"]+)"', autoridades_).group(1)
    assert "assunto=autoridades" in seguinte
    segunda = client.get(URL + seguinte.replace("&amp;", "&")).content.decode()
    assert len(_itens(segunda)) == 1
    assert "Criação de modelo de aviso" not in _lista(segunda)

    # Sem filtro, os vinte e um cadastros vêm antes dos três modelos, e a segunda página os mostra.
    todos = client.get(URL).content.decode()
    assert len(_itens(todos)) == 20
    seguinte = re.search(r'href="(\?[^"]*cursor=[^"]+)"', todos).group(1).replace("&amp;", "&")
    resto = client.get(URL + seguinte).content.decode()
    assert "Cadastro de autoridade" in _lista(resto)
    assert _lista(resto).count("Criação de modelo de aviso") == 3


def test_filtro_sem_atos_e_filtro_desconhecido(client):
    garantir_modelos_iniciais(correlation_id="teste-108")
    _auditor(client)

    vazio = client.get(URL + "?assunto=avisos").content.decode()
    assert "Nenhum ato corresponde ao filtro." in vazio

    desconhecido = client.get(URL + "?assunto=xyz").content.decode()
    assert len(_itens(desconhecido)) == 3
    assert "selected" not in desconhecido.split('<select id="assunto"')[1].split("</select>")[0]


# ---- guardiões ----------------------------------------------------------------------------------

#: As operações que os assuntos da página gravam hoje, lidas no código (data-model da 108). Literal
#: **e** conferida contra o código-fonte: uma operação nova sem rótulo apareceria crua na tela.
OPERACOES_DA_UNIDADE = (
    "REGISTRAR_UNIDADE",
    "ALTERAR_UNIDADE",
    "EXCLUIR_REGISTROS_DO_PILOTO",
    "CADASTRAR_AUTORIDADE",
    "CORRIGIR_AUTORIDADE",
    "ENCERRAR_AUTORIDADE",
    "AVISO_MODELO",
    "AVISO_CONFIRMAR",
    "AVISO_INTERROMPER",
    "ACESSO_CONCEDER",
    "ACESSO_REVOGAR",
)


def test_toda_operacao_dos_assuntos_tem_rotulo_e_toda_situacao_tem_traducao():
    """`FR-3165`."""
    for operacao in OPERACOES_DA_UNIDADE:
        rotulo = tela._rotulo_da_operacao(
            SimpleNamespace(operation=operacao, previous_state="", new_state="")
        )
        assert rotulo != operacao and not re.fullmatch(r"[A-Z_]+", rotulo), operacao
    assert set(tela.ASSUNTOS) == set(auditoria_selectors.ASSUNTOS_DA_UNIDADE)
    from processo_seletivo.avisos.application.modelos import _estado
    from processo_seletivo.unidades.application.sincronizacao import _situacao
    from processo_seletivo.unidades.domain.vigencia import ENCERRADA, FUTURA, VIGENTE

    gravadas = {
        _situacao(True),
        _situacao(False),
        _estado(SimpleNamespace(ativo=True)),
        _estado(SimpleNamespace(ativo=False)),
        *(s.upper() for s in (FUTURA, VIGENTE, ENCERRADA)),
        "vigente",
        "revogado",
    }
    assert gravadas <= set(tela.SITUACOES)


VERBOS = {"REGISTRAR", "ALTERAR", "CADASTRAR", "CORRIGIR", "ENCERRAR", "ACESSO"}


def test_a_lista_literal_e_a_do_codigo():
    """As operações gravadas sobre os cinco tipos, varridas no código: nenhuma fica sem rótulo."""
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2] / "processo_seletivo"
    fontes = {
        "unidades/application/sincronizacao.py": ("REGISTRAR_UNIDADE", "ALTERAR_UNIDADE"),
        "unidades/application/autoridades.py": (
            "CADASTRAR_AUTORIDADE",
            "CORRIGIR_AUTORIDADE",
            "ENCERRAR_AUTORIDADE",
        ),
        "seguranca/application/acessos.py": ("ACESSO_CONCEDER", "ACESSO_REVOGAR"),
    }
    for arquivo, esperadas in fontes.items():
        gravadas = set(re.findall(r'"([A-Z]+_[A-Z_]+)"', (raiz / arquivo).read_text()))
        operacoes = {
            g
            for g in gravadas
            if g.split("_")[0]
            in {"REGISTRAR", "ALTERAR", "CADASTRAR", "CORRIGIR", "ENCERRAR", "ACESSO"}
        }
        assert operacoes == set(esperadas), arquivo
    assert all(operacao in OPERACOES for operacao in OPERACOES_DA_UNIDADE)
