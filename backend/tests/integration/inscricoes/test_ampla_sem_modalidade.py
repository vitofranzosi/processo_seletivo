"""A ampla concorrência sem Modalidade: o Perfil que só declara cotas recebe quem não é cotista.

É o A-1 da `048` e o RC-128 da auditoria, decididos pela DP-14 com a opção A em 27/09. A composição
diz a quem compõe que a ampla *"é só a linha geral do quadro"*, e a inscrição só oferecia as
Modalidades declaradas: com uma cota, todo inscrito era assumido cotista; com duas, quem não era
cotista não tinha o que escolher.

O que este arquivo prova é o que a `009` já escrevia e o código não cumpria: a ausência de reserva
apresentada como ampla sem entidade gravada (FR-039), e só os documentos daquela combinação
(FR-040, SC-005, SC-006). E prova as três fronteiras que a correção **não** atravessa: a ampla
declarada continua sendo a usada, o Perfil com tudo em cota continua sem ampla, e o POST forjado
continua recusado.

As inscrições de fixture da ocupação e do sorteio já nasciam no recorte nulo de Perfil com cota
(`tests/fixtures/ocupacao.py`, `certame_com_cotas`) — gravadas direto no banco, e por isso nunca
passaram pela porta que as recusava. O último caso daqui fecha essa distância: a inscrição que o
comando produz tem a forma que a projeção do sorteio já lê.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
    requisitos_da_inscricao,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao, ItemDaListaExigida
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.domain.projecao import elegiveis
from tests.fixtures.candidato import (
    JOAO,
    MARIA,
    MODALIDADE_AC,
    MODALIDADE_PPP,
    PERFIL_DOCENTE,
    identificar,
    pdf,
)
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    publicar_selecao,
    rascunho_aberto_com_documentos,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MODALIDADE_PCD = identificador(470, 0)
DECLARACOES = {"veracidade": True, "ciencia": True}


def _so_cotas(*, pcd=False, linha_geral=1):
    """O Perfil docente sem a ampla declarada: a PPP, e a PcD se pedida, e a linha geral dada.

    O total do Perfil é 2, e o quadro fecha nele em todas as formas: a linha geral leva o que
    `linha_geral` disser, e a PPP o resto.
    """
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    docente = rascunho["profiles"][0]
    docente["competitionModalities"] = [
        modalidade for modalidade in docente["competitionModalities"] if modalidade["code"] != "AC"
    ]
    docente["generalCompetitionModalityId"] = None
    docente["vacancyTable"] = [
        {"id": identificador(408, 0), "modalityId": None, "immediateVacancies": linha_geral},
        {
            "id": identificador(409, 0),
            "modalityId": MODALIDADE_PPP,
            "immediateVacancies": 2 - linha_geral,
        },
    ]
    if pcd:
        docente["competitionModalities"].append(
            {"id": MODALIDADE_PCD, "code": "PCD", "name": "Pessoas com deficiência"}
        )
        docente["vacancyTable"].append(
            {"id": identificador(471, 0), "modalityId": MODALIDADE_PCD, "immediateVacancies": 0}
        )
    return rascunho


@pytest.fixture
def publicar(
    raiz_de_arquivos, candidatos_registrados, api_client, manager_headers, process_payload
):
    def publicar(rascunho):
        return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)

    return publicar


def _gravar(identidade, inscricao, modalidade):
    return gravar_dados(
        identidade=identidade,
        inscricao=inscricao,
        dados={
            "nome": identidade.nome,
            "cpf": identidade.cpf,
            "email": identidade.email,
            "modality_id": modalidade,
        },
    )


def _anexar(identidade, inscricao, *requisitos):
    for requisito in requisitos:
        anexar_documento(
            identidade=identidade, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(identidade, inscricao, chave):
    return enviar_inscricao(
        identidade=identidade, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key=chave
    )


def _requisitos(edital, inscricao):
    conteudo = selectors.selecao_publica(edital_id=edital.id).content
    return {str(requisito["id"]) for requisito in requisitos_da_inscricao(conteudo, inscricao)}


def test_uma_cota_com_vaga_na_linha_geral_nao_assume_a_cota(publicar):
    """A-1: o rascunho nasce na ampla, e só o que a ampla exige é pedido (FR-039, FR-040)."""
    edital = publicar(_so_cotas())

    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert rascunho.modality_id is None, "nada é assumido: há duas opções, e a ampla é o nulo"
    assert _requisitos(edital, rascunho) == {DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL}, "SC-006"


def test_o_nao_cotista_envia_pela_ampla_sem_modalidade(publicar):
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    rascunho = _anexar(JOAO, _gravar(JOAO, rascunho, ""), DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL)
    enviada = _enviar(JOAO, rascunho, "envio-ampla-nula")

    assert enviada.status == Inscricao.Status.SUBMETIDA
    assert enviada.modality_id is None
    situacoes = dict(
        ItemDaListaExigida.objects.filter(inscricao=enviada).values_list("requisito_id", "situacao")
    )
    assert {str(requisito): situacao for requisito, situacao in situacoes.items()} == {
        DOCUMENTO_DE_TODOS: ItemDaListaExigida.Situacao.OBRIGATORIO,
        DOCUMENTO_DO_PERFIL: ItemDaListaExigida.Situacao.OBRIGATORIO,
        DOCUMENTO_DA_MODALIDADE: ItemDaListaExigida.Situacao.NAO_SE_APLICA,
    }, "a lista congelada é a da ampla (044)"


def test_o_cotista_troca_pela_cota_e_recebe_o_documento_dela(publicar):
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    escolhida = _gravar(MARIA, rascunho, MODALIDADE_PPP)

    assert str(escolhida.modality_id) == MODALIDADE_PPP
    assert DOCUMENTO_DA_MODALIDADE in _requisitos(edital, escolhida)


def test_duas_cotas_com_vaga_na_linha_geral_o_nao_cotista_tem_o_que_escolher(publicar):
    """A `D-G5` com vaga na linha geral: antes, `modality_required` para quem não é cotista."""
    edital = publicar(_so_cotas(pcd=True))
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert _gravar(JOAO, rascunho, "").modality_id is None


def test_o_post_forjado_com_modalidade_de_fora_do_perfil_e_recusado(publicar):
    """A Modalidade AC existe no Edital da fixture de origem, e não neste Perfil."""
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    with pytest.raises(DomainError) as recusa:
        _gravar(JOAO, rascunho, MODALIDADE_AC)

    assert recusa.value.code == "modality_not_available"


def test_a_ampla_declarada_continua_sendo_a_usada(publicar):
    """FR-039, 2ª frase: havendo a declarada, nenhuma outra nasce — e o vazio não é resposta."""
    edital = publicar(rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)))
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    with pytest.raises(DomainError) as recusa:
        _gravar(JOAO, rascunho, "")

    assert recusa.value.code == "modality_required"


def test_tudo_em_cota_continua_sem_ampla(publicar):
    """A contraprova da DP-14: sem vaga na linha geral, a cota única continua assumida."""
    edital = publicar(_so_cotas(linha_geral=0))

    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert str(rascunho.modality_id) == MODALIDADE_PPP
    assert str(_gravar(JOAO, rascunho, "").modality_id) == MODALIDADE_PPP


def test_a_modalidade_unica_avanca_com_o_documento_da_cota_ja_enviado(client, publicar):
    """A-14.1: a tela sem o campo não anuncia descarte, e avançar leva à revisão (FR-031, FR-041).

    O vazio do formulário era comparado como se fosse a ampla, e a confirmação oferecia descartar
    o documento da cota que a gravação, assumindo a cota, mantinha: confirmar dava
    `discard_not_confirmed`, e a pessoa não saía da tela.
    """
    edital = publicar(_so_cotas(linha_geral=0))
    rascunho = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    _anexar(MARIA, rascunho, DOCUMENTO_DA_MODALIDADE)
    identificar(client, MARIA)
    endereco = reverse("portal:inscricao", args=[rascunho.id])

    resposta = client.post(endereco, {"telefone": ""})

    assert resposta.status_code == 302, "nenhuma confirmação de descarte no caminho"
    assert resposta["Location"] == reverse("portal:revisao", args=[rascunho.id])
    rascunho.refresh_from_db()
    assert str(rascunho.modality_id) == MODALIDADE_PPP
    assert rascunho.documentos.filter(requirement_id=DOCUMENTO_DA_MODALIDADE).exists()


def test_a_inscricao_na_ampla_tem_a_forma_que_o_sorteio_ja_le(publicar):
    """O recorte nulo alcança os dois; o da cota, só quem a declarou (`projecao.elegiveis`)."""
    edital = publicar(_so_cotas())
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    joao = _enviar(
        JOAO,
        _anexar(JOAO, _gravar(JOAO, joao, ""), DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL),
        "sorteio-joao",
    )
    maria = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    maria = _enviar(
        MARIA,
        _anexar(
            MARIA,
            _gravar(MARIA, maria, MODALIDADE_PPP),
            DOCUMENTO_DE_TODOS,
            DOCUMENTO_DO_PERFIL,
            DOCUMENTO_DA_MODALIDADE,
        ),
        "sorteio-maria",
    )
    submetidas = list(Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA))

    assert {i.id for i in elegiveis(submetidas, lista_id=None)} == {joao.id, maria.id}
    assert {i.id for i in elegiveis(submetidas, lista_id=MODALIDADE_PPP)} == {maria.id}


# ---------------------------------------------------------------------------
# O que o candidato vê (FR-038)
# ---------------------------------------------------------------------------


def test_a_tela_oferece_a_ampla_marcada_ao_lado_da_cota(client, publicar):
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()

    assert '<option value="" selected>Ampla concorrência</option>' in corpo
    assert f'<option value="{MODALIDADE_PPP}" >' in corpo
    assert "Selecione a modalidade" not in corpo, "o vazio é a ampla, e não um convite"
    assert 'name="modalidade" required' not in corpo


def test_a_tela_com_a_ampla_declarada_continua_pedindo_a_escolha(client, publicar):
    edital = publicar(rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)))
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()

    assert "Selecione a modalidade" in corpo
    assert corpo.count("Ampla concorrência</option>") == 1, "a declarada, e nenhuma ao lado"


def test_voltar_da_cota_para_a_ampla_pela_tela(client, publicar):
    """O vazio guardado na hora é a ampla, e a escolha sobrevive a sair e voltar."""
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, MARIA)
    endereco = reverse("portal:inscricao", args=[rascunho.id])
    client.post(endereco, {"modalidade": MODALIDADE_PPP, "telefone": "", "acao": "guardar"})

    client.post(endereco, {"modalidade": "", "telefone": "", "acao": "guardar"})

    rascunho.refresh_from_db()
    assert rascunho.modality_id is None
    assert '<option value="" selected>' in client.get(endereco).content.decode()


def test_a_revisao_nomeia_a_ampla(client, publicar):
    """FR-063: a concorrência aparece na revisão, e o nulo tem nome onde foi escolha."""
    edital = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:revisao", args=[rascunho.id])).content.decode()

    assert "<dt>Concorrência</dt><dd>Ampla concorrência</dd>" in corpo


@pytest.mark.parametrize(
    "rascunho",
    [
        pytest.param(
            lambda: rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
            id="ampla-declarada-e-cota",
        ),
        pytest.param(lambda: _so_cotas(pcd=True, linha_geral=0), id="duas-cotas-sem-linha-geral"),
    ],
)
def test_a_revisao_nao_nomeia_a_ampla_onde_o_nulo_e_escolha_por_fazer(client, publicar, rascunho):
    """Duas opções e nenhuma delas a ampla sem Modalidade: o nulo ainda não é escolha.

    Contar opções confundia os dois casos com o de cima, e a revisão afirmava *"Ampla
    concorrência"* a quem não tinha escolhido nada — e o requerimento repetiria a afirmação.
    """
    edital = publicar(rascunho())
    inscricao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    assert inscricao.modality_id is None, "a contraprova: nada foi escolhido nem assumido"
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()

    assert "<dt>Concorrência</dt>" not in corpo


def test_o_asterisco_so_acompanha_a_escolha_obrigatoria(client, publicar):
    """Com a ampla sem Modalidade já marcada, o campo não é `required`, e o rótulo não o finge."""
    rotulo = '<label for="modalidade">Modalidade <span class="obrigatorio"'
    identificar(client, JOAO)
    so_cotas = publicar(_so_cotas())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=so_cotas.id, profile_id=PERFIL_DOCENTE)

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()

    assert '<label for="modalidade">Modalidade</label>' in corpo
    assert rotulo not in corpo


def test_o_asterisco_continua_onde_o_vazio_e_recusa(client, publicar):
    edital = publicar(rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)))
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:inscricao", args=[rascunho.id])).content.decode()

    assert '<label for="modalidade">Modalidade <span class="obrigatorio"' in corpo


def test_a_pagina_da_selecao_anuncia_a_ampla(client, publicar):
    edital = publicar(_so_cotas())

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Concorrência: Ampla concorrência; Pessoas pretas, pardas e indígenas" in corpo


# ---------------------------------------------------------------------------
# O que a gestão vê (FR-067, FR-068) — A-14.3 da DP-14
# ---------------------------------------------------------------------------


@pytest.fixture
def gestao(client, settings):
    from tests.interface.conftest import identificar as identificar_na_gestao

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar_na_gestao(client, "bruno.gestor", ["gestor"])
    return client


def _joao_na_ampla_e_maria_na_cota(edital):
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    joao = _enviar(
        JOAO,
        _anexar(JOAO, _gravar(JOAO, joao, ""), DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL),
        "gestao-joao",
    )
    maria = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    maria = _enviar(
        MARIA,
        _anexar(
            MARIA,
            _gravar(MARIA, maria, MODALIDADE_PPP),
            DOCUMENTO_DE_TODOS,
            DOCUMENTO_DO_PERFIL,
            DOCUMENTO_DA_MODALIDADE,
        ),
        "gestao-maria",
    )
    return joao, maria


def test_a_lista_da_gestao_nomeia_conta_e_filtra_a_ampla(gestao, publicar):
    """A coluna, a contagem e o filtro alcançam o nulo onde ele é a ampla (FR-067)."""
    edital = publicar(_so_cotas())
    joao, maria = _joao_na_ampla_e_maria_na_cota(edital)
    tela = reverse("interface:inscricoes", args=[edital.id])

    corpo = gestao.get(tela).content.decode()
    filtrada = gestao.get(f"{tela}?modalidade=ampla:{PERFIL_DOCENTE}").content.decode()

    assert "<td>Ampla concorrência</td>" in corpo, "a coluna não fica em branco"
    assert f'<option value="ampla:{PERFIL_DOCENTE}" >' in corpo
    assert "Ampla concorrência (1)</option>" in corpo, "o nulo entra na contagem"
    assert joao.protocolo in filtrada and maria.protocolo not in filtrada


def test_o_detalhe_da_gestao_nomeia_a_ampla(gestao, publicar):
    """FR-068: a concorrência aparece no detalhe, como no comprovante do candidato."""
    edital = publicar(_so_cotas())
    joao, _ = _joao_na_ampla_e_maria_na_cota(edital)

    corpo = gestao.get(reverse("interface:inscricao-recebida", args=[joao.id])).content.decode()

    assert "<dt>Concorrência</dt><dd>Ampla concorrência</dd>" in corpo


def test_a_gestao_nao_nomeia_o_nulo_onde_ele_e_escolha_por_fazer(gestao, publicar):
    """A contraprova: com a ampla declarada, o nulo do rascunho não é opção nem tem nome."""
    edital = publicar(rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)))
    abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    corpo = gestao.get(reverse("interface:inscricoes", args=[edital.id])).content.decode()

    assert 'value="ampla:' not in corpo
    assert "<td>—</td>" in corpo, "o rascunho sem escolha continua em branco"


def test_a_mesa_nomeia_a_ampla(publicar):
    """FR-068 na Mesa: o avaliador lê Perfil e concorrência, e não um traço sem explicação."""
    from processo_seletivo.avaliacoes.application.mesa import _perfil_e_modalidade

    edital = publicar(_so_cotas())
    joao, maria = _joao_na_ampla_e_maria_na_cota(edital)
    conteudo = joao.versao_aceita.content

    assert _perfil_e_modalidade(conteudo, joao)[1] == "Ampla concorrência"
    assert _perfil_e_modalidade(conteudo, maria)[1] == "Pessoas pretas, pardas e indígenas"


def _sem_modalidade():
    """O Perfil docente sem Modalidade nenhuma: só a linha geral, e nenhum documento de cota."""
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    docente = rascunho["profiles"][0]
    docente["competitionModalities"] = []
    docente["generalCompetitionModalityId"] = None
    docente["vacancyTable"] = [
        {"id": identificador(408, 0), "modalityId": None, "immediateVacancies": 2}
    ]
    rascunho["documentRequirements"] = [
        documento
        for documento in rascunho["documentRequirements"]
        if documento["id"] != DOCUMENTO_DA_MODALIDADE
    ]
    return rascunho


def test_a_gestao_nomeia_a_ampla_no_perfil_sem_modalidade(gestao, client, publicar):
    """O caso original do A-14.3: o Perfil sem Modalidade já mostrava a concorrência em branco.

    Ao candidato, nada muda: nada lhe foi perguntado, e a revisão continua sem a linha (FR-038).
    """
    edital = publicar(_sem_modalidade())
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    joao = _enviar(
        JOAO,
        _anexar(JOAO, _gravar(JOAO, joao, ""), DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL),
        "sem-modalidade-joao",
    )
    tela = reverse("interface:inscricoes", args=[edital.id])

    corpo = gestao.get(tela).content.decode()
    filtrada = gestao.get(f"{tela}?modalidade=ampla:{PERFIL_DOCENTE}").content.decode()
    detalhe = gestao.get(reverse("interface:inscricao-recebida", args=[joao.id])).content.decode()

    assert "<td>Ampla concorrência</td>" in corpo
    assert "Ampla concorrência (1)</option>" in corpo
    assert joao.protocolo in filtrada
    assert "<dt>Concorrência</dt><dd>Ampla concorrência</dd>" in detalhe


def test_a_revisao_do_perfil_sem_modalidade_continua_sem_a_linha(client, publicar):
    """A contraprova do lado do candidato: FR-038, e não a regra da gestão."""
    edital = publicar(_sem_modalidade())
    rascunho = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    identificar(client, JOAO)

    corpo = client.get(reverse("portal:revisao", args=[rascunho.id])).content.decode()

    assert "<dt>Concorrência</dt>" not in corpo


def test_o_filtro_forjado_nao_chama_de_ampla_a_escolha_por_fazer(gestao, publicar):
    """Duas cotas sem vaga na linha geral: o nulo é escolha por fazer, e `ampla:` não o recorta.

    O filtro confere a mesma regra que gera a opção. O que não passa não filtra, como o
    identificador que não é UUID — e a lista continua com as duas.
    """
    edital = publicar(_so_cotas(pcd=True, linha_geral=0))
    joao = abrir_inscricao(identidade=JOAO, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    maria = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    _gravar(MARIA, maria, MODALIDADE_PPP)
    tela = reverse("interface:inscricoes", args=[edital.id])

    corpo = gestao.get(tela).content.decode()
    forjada = gestao.get(f"{tela}?modalidade=ampla:{PERFIL_DOCENTE}").content.decode()

    assert joao.modality_id is None, "a premissa: o rascunho sem escolha"
    assert 'value="ampla:' not in corpo, "a opção não é oferecida"
    assert forjada.count("Em preenchimento</td>") == 2, "e o endereço forjado não a inventa"
