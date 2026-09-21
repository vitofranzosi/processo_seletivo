"""A visão institucional pela tela: o recorte, a gramática da ausência e o que ela declara (040).

Os cenários de derivação vivem em `tests/unit/test_visao_institucional.py`, sem banco. Aqui ficam
os que só existem no canal — o recorte declarado, a concordância com a tela dona, a varredura de
dado pessoal e a declaração do que a página não mede.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.edital import identidade_do_marco, marco_minimo
from tests.fixtures.publicacao import encerrar_inscricoes, publish_original
from tests.fixtures.supervisao import (
    perfil_de,
    publicar_no_processo,
    rascunho_com_periodo,
    submeter,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 — é a guarda que produção exige."""


URL = "interface:visao-geral"
PAPEIS_DO_GESTOR = ["gestor"]


def abrir(client, consulta="", papeis=PAPEIS_DO_GESTOR, subject="carlos"):
    identificar(client, subject, list(papeis))
    resposta = client.get(reverse(URL) + consulta)
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def texto(corpo):
    """O que chega a olho: sem marcação, **sem folha de estilo**, com os espaços normalizados.

    O `<style>` sai antes de tudo, e a razão é um defeito que este repositório já registrou: a
    folha de `base.html` é prosa densa — os comentários explicam a decisão de cada regra —, e uma
    varredura que só remova tags devolve esse texto junto. Uma asserção de **ausência** passa a
    falhar por uma palavra escrita num comentário de CSS, longe da tela que ela mede.
    """
    sem_folha = re.sub(r"<(style|script)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sem_folha)).strip()


@pytest.fixture
def certame(db, api_client, manager_headers):
    """Um Processo com dois Editais publicados: um com inscrições abertas e um encerrado.

    Montado do zero, e não obtido apagando o que sobra de outro: **nada é excluído** neste sistema,
    e um teste que apagasse um Edital provaria o contrário do que a Constituição garante.
    """
    agora = timezone.now()
    aberto = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "visao-processo-0001"},
        {
            "institutionalCode": "PS-2026-040",
            "title": "Processo da visão institucional",
            "firstEdital": {"number": "40", "year": 2026, "title": "Edital aberto"},
        },
        draft=rascunho_com_periodo(
            0, inicio=agora - timedelta(days=10), fim=agora + timedelta(days=5)
        ),
    )
    encerrado = publicar_no_processo(
        api_client,
        manager_headers,
        aberto.processo,
        draft=rascunho_com_periodo(
            2, inicio=agora - timedelta(days=30), fim=agora + timedelta(days=5)
        ),
        number="41",
        year=2026,
        chave="visao-geral-segundo-edital",
    )
    # **O prazo vence por Retificação, e não publicando com a data já vencida** — a `028` recusa
    # publicar certame que ninguém pode disputar, e o atalho não existe na realidade: nenhum Edital
    # é publicado depois de as inscrições fecharem.
    encerrar_inscricoes(api_client, encerrado, agora - timedelta(days=1))
    submeter(aberto, 3, seed=0)
    return aberto, encerrado


# ---------------------------------------------------------------------------
# T-11 — o recorte padrão, declarado
# ---------------------------------------------------------------------------


def test_t11_abre_no_ano_corrente_e_declara_o_recorte(client, certame):
    corpo = abrir(client)

    assert f"Editais de {timezone.localtime().year}" in texto(corpo)


def test_t11b_o_seletor_oferece_todos_os_anos_como_escolha_explicita(client, certame):
    corpo = abrir(client)

    assert "Todos os anos" in texto(corpo)


# ---------------------------------------------------------------------------
# T-13 — o filtro move consolidado e tabela juntos
# ---------------------------------------------------------------------------


def test_t13_outro_ano_esvazia_o_recorte_sem_afirmar_nada_sobre_o_acervo(client, certame):
    corpo = abrir(client, "?ano=1999")

    visivel = texto(corpo)
    assert "Nenhum Edital no período selecionado" in visivel
    assert "Isto não é uma afirmação sobre o acervo" in visivel


def test_t14_o_filtro_por_situacao_do_periodo_seleciona_pelo_conteudo(client, certame):
    aberto = texto(abrir(client, "?periodo=aberto"))
    encerrado = texto(abrir(client, "?periodo=encerrado"))

    assert "Inscrições abertas" in aberto
    assert "Inscrições encerradas" in encerrado
    assert "Inscrições encerradas" not in aberto


def test_parametro_invalido_e_saneado_e_nao_derruba_a_pagina(client, certame):
    corpo = abrir(client, "?ano=banana&situacao=INEXISTENTE&periodo=xyz&ordem=nada&sentido=??")

    assert f"Editais de {timezone.localtime().year}" in texto(corpo)


# ---------------------------------------------------------------------------
# SC-208 — nenhum `0` onde há ausência, nenhuma ausência onde há zero
# ---------------------------------------------------------------------------


def test_sc208_edital_sem_conteudo_publicado_mostra_ausencia_e_nao_zero(
    client, api_client, manager_headers, certame
):
    edital, _ = certame
    api_client.post(
        f"/api/v1/admin/processos/{edital.processo_id}/editais",
        {"number": "03", "title": "Em elaboração", "year": edital.year},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "visao-geral-terceiro-edital"},
    )

    visivel = texto(abrir(client))

    assert "sem conteúdo publicado" in visivel


def test_sc208_edital_encerrado_sem_procura_mostra_zero_legitimo(client, certame):
    visivel = texto(abrir(client, "?periodo=encerrado"))

    # `0` submetidas é afirmação verdadeira, e a marca a explica.
    assert "Encerrou sem nenhuma inscrição submetida." in visivel


# ---------------------------------------------------------------------------
# FR-586 — o termo é o da tela dona
# ---------------------------------------------------------------------------


def test_fr586_a_coluna_de_rascunhos_usa_o_termo_da_tela_dona(client, certame):
    visivel = texto(abrir(client))

    assert "Em preenchimento" in visivel
    assert "Rascunhos" not in visivel


# ---------------------------------------------------------------------------
# SC-207 — a visão e a tela dona dizem o mesmo número
# ---------------------------------------------------------------------------


def test_sc207_a_visao_e_a_tela_de_inscricoes_dizem_o_mesmo_numero(client, certame):
    edital, _ = certame
    esperado = Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA).count()
    assert esperado == 3

    visivel = texto(abrir(client))
    identificar(client, "carlos", PAPEIS_DO_GESTOR)
    dona = client.get(reverse("interface:inscricoes", args=[edital.id]))

    assert dona.status_code == 200, dona.content
    # O mesmo número nas duas superfícies — é a única prova automatizada de que a visão não tem
    # uma segunda derivação da mesma contagem (`FR-582`).
    assert str(esperado) in visivel
    assert str(esperado) in texto(dona.content.decode())


# ---------------------------------------------------------------------------
# T-16 · SC-210 · FR-593 — a varredura do HTML
# ---------------------------------------------------------------------------


def test_t16_nenhum_dado_pessoal_de_candidato_no_html(client, certame):
    """E a varredura alcança o **conteúdo expandido** (041): a expansão é agregada por Perfil, e
    não pode trazer pessoa nenhuma para dentro de um `<details>` que a busca do navegador encontra.
    """
    edital, _ = certame
    inscricao = Inscricao.objects.filter(edital=edital).first()
    assert inscricao.nome and inscricao.cpf_normalizado

    corpo = abrir(client)
    # A expansão está no HTML, recolhida — e é dentro dela que a varredura precisa entrar.
    assert "perfis-do-edital" in corpo

    assert inscricao.nome not in corpo
    assert inscricao.cpf_normalizado not in corpo
    assert inscricao.email not in corpo
    assert inscricao.protocolo not in corpo


def test_fr593_nenhum_rotulo_de_contagem_diz_candidatos_ou_pessoas(client, certame):
    visivel = texto(abrir(client)).lower()

    # A página conta **inscrições**. Chamá-las de candidatos ou pessoas seria outra grandeza,
    # com outra fonte e outra confiabilidade.
    assert "candidatos" not in visivel
    assert "pessoas" not in visivel
    assert "inscrições submetidas" in visivel


# ---------------------------------------------------------------------------
# T-17 · T-18 — legibilidade sem cor, e a declaração do que não se mede
# ---------------------------------------------------------------------------


def test_t17_as_marcas_sao_legiveis_sem_cor(client, certame):
    visivel = texto(abrir(client, "?periodo=encerrado"))

    # A mensagem está no texto, e não apenas numa classe de estilo.
    assert "Encerrou sem nenhuma inscrição submetida." in visivel


def test_t18_a_pagina_declara_o_que_nao_mede(client, certame):
    visivel = texto(abrir(client))

    assert "O que esta página não mede" in visivel
    assert "Matrícula efetivada" in visivel
    assert "Supervisão" in visivel
    assert "ano do Edital" in visivel


def test_a_linha_de_matricula_fica_fora_do_recolhido(client, certame):
    """**Uma permanente e três recolhidas**, e a repartição é de risco, não de espaço.

    A de matrícula é a única cuja ausência alguém pode confundir com zero e decidir em cima —
    *"não há matriculados"* e *"não medimos matrícula"* levam a decisões diferentes, e só a segunda
    é verdade. As outras três viram ruído depois da primeira leitura.
    """
    corpo = abrir(client)
    recolhido = re.search(r"<details class=\"demais-limites\".*?</details>", corpo, re.S).group(0)

    assert "Matrícula efetivada" not in recolhido
    assert "Matrícula efetivada" in corpo
    # E o resumo **nomeia os três**: quem nunca o abrir sabe o que há dentro.
    resumo = re.search(r"<summary>(.*?)</summary>", recolhido, re.S).group(1)
    for anunciado in ("ocupação", "indicadores", "recortes"):
        assert anunciado in resumo


def test_o_recolhido_nasce_fechado(client, certame):
    corpo = abrir(client)

    assert '<details class="demais-limites">' in corpo
    assert '<details class="demais-limites" open>' not in corpo


# ---------------------------------------------------------------------------
# SC-213 — a população da razão, dita na linha
# ---------------------------------------------------------------------------


def test_sc213_o_edital_misto_declara_a_populacao_da_razao(
    client, api_client, manager_headers, certame
):
    """A metade de interface de `SC-213`: o cálculo é do `tests/unit`, a declaração é daqui.

    O Edital tem um Perfil com 1 vaga imediata e outro **só de cadastro reserva**. A coluna
    *Submetidas* mostra a demanda do Edital inteiro; a razão usa só a do primeiro — e a linha
    **diz** qual população usou. Sem essa frase, a tela mostra dois números que não se explicam.
    """
    edital, _ = certame
    agora = timezone.now()
    draft = rascunho_com_periodo(5, fim=agora + timedelta(days=5))
    com_vaga = draft["profiles"][0]
    so_reserva = {
        **com_vaga,
        "id": perfil_de(6),
        "code": "RESERVA",
        "name": "Só cadastro reserva",
        "immediateVacancies": 0,
        "reserveType": "UNLIMITED",
        "classificationMilestones": [marco_minimo(identidade_do_marco(perfil_de(6)))],
    }
    draft["profiles"] = [com_vaga, so_reserva]
    misto = publicar_no_processo(
        api_client,
        manager_headers,
        edital.processo,
        draft=draft,
        number="04",
        year=edital.year,
        chave="visao-geral-edital-misto",
    )
    encerrar_inscricoes(api_client, misto, agora - timedelta(days=1), suffix="mis")
    submeter(misto, 2, seed=5, primeiro=10)
    submeter(misto, 7, seed=6, primeiro=50)

    visivel = texto(abrir(client, "?periodo=encerrado"))

    # A demanda total do Edital: 2 + 7.
    assert "9" in visivel
    # E a razão declara ter usado só as 2 do Perfil com vaga imediata.
    assert "sobre 2 inscrições nos Perfis com vaga imediata" in visivel


# ---------------------------------------------------------------------------
# Os cinco defeitos da primeira entrega, cada um com o seu caso
# ---------------------------------------------------------------------------


def test_a_coluna_do_periodo_nao_se_chama_inscricoes(client, certame):
    """Havia duas colunas: **Inscrições**, que mostrava o período, e **Submetidas**, que mostrava
    inscrições. O rótulo dizia de uma o que valia da outra."""
    visivel = texto(abrir(client))

    assert "Período de inscrições" in visivel
    assert "Submetidas" in visivel


def test_o_filtro_do_periodo_nao_se_chama_inscricoes(client, certame):
    corpo = abrir(client)

    assert 'for="f-periodo">Situação do período<' in corpo


def test_o_denominador_nao_afirma_um_demais_que_nao_existe(client, certame):
    """A frase afirmava um "demais" que não existia, quando eram 3 de 3.

    Numa página cuja tese é que todo número traz o denominador dito, a frase que se contradiz é o
    pior defeito possível — e ela passou por toda a suíte da primeira entrega.
    """
    visivel = texto(abrir(client))

    assert "os demais não têm conteúdo publicado" not in visivel
    assert "em todos os 2 Editais" in visivel


def test_a_ressalva_aparece_quando_ha_ressalva(client, api_client, manager_headers, certame):
    """E o recíproco: havendo Edital sem conteúdo, a frase o conta — e o conta certo."""
    edital, _ = certame
    api_client.post(
        f"/api/v1/admin/processos/{edital.processo_id}/editais",
        {"number": "43", "title": "Em elaboração", "year": edital.year},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "visao-geral-sem-conteudo-0001"},
    )

    visivel = texto(abrir(client))

    assert "em 2 de 3 Editais — 1 ainda sem conteúdo publicado" in visivel


def test_nenhuma_flexao_de_planilha_na_tela(client, certame):
    """`Edital(is)` e `Perfil(is)` são forma de planilha. O Django flexiona, e o repositório usa."""
    visivel = texto(abrir(client))

    assert "(is)" not in visivel
    assert "(ões)" not in visivel


# ===========================================================================
# 041 — a expansão dos Perfis
# ===========================================================================


def test_t013_a_expansao_existe_nasce_recolhida_e_traz_as_colunas(client, certame):
    corpo = abrir(client)

    assert '<details class="perfis-do-edital">' in corpo
    # **Recolhida**: `open` não aparece no elemento (`FR-606`).
    assert '<details class="perfis-do-edital" open>' not in corpo
    visivel = texto(corpo)
    # **"Cadastro de reserva" saiu de coluna na `042`** e passou à identidade do Perfil: é atributo
    # caracterizador, não métrica de comparação vertical.
    for coluna in ("Vagas imediatas", "Submetidas", "Inscr./vaga"):
        assert coluna in visivel


def test_t013b_a_linha_principal_continua_com_as_sete_colunas(client, certame):
    """`FR-617` — se alguém a substituísse por linhas de Perfil, o teste de estrutura passaria."""
    corpo = abrir(client)
    cabecalho = re.search(r"<thead>(.*?)</thead>", corpo, re.S).group(1)

    # O cabeçalho numérico ganhou classe na correção de alinhamento: contar a abertura exata da
    # tag prende a marcação, e não a estrutura, que é o que este teste quer medir.
    assert len(re.findall(r'<th scope="col"[^>]*>', cabecalho)) == 8
    assert "Processo / Edital" in cabecalho and "Período de inscrições" in cabecalho


def test_t014_o_details_esta_dentro_de_um_td_e_nao_solto_na_tr(client, certame):
    """**Estrutura, e é o único caso que a cobre** (`R-001`, `R-007`).

    `<details>` não é filho válido de `<tr>` nem de `<tbody>`: os filhos de `<tr>` são `<td>` e
    `<th>`. Solto na linha, cada navegador o reparenteia à sua maneira — e **nenhum outro teste
    deste repositório olha estrutura de tabela**: a suíte inteira passaria.
    """
    corpo = abrir(client)

    # Todo `<details>` da expansão é precedido por uma abertura de `<td>` e nunca por `<tr>`.
    for antes in re.findall(r"(<t[dr][^>]*>)\s*(?=<details class=\"perfis-do-edital\")", corpo):
        assert antes.startswith("<td"), antes
    assert re.search(r'<tr class="expansao-do-edital">\s*<td colspan="8">', corpo)
    # E nunca o contrário.
    assert not re.search(r"<tr[^>]*>\s*<details", corpo)


def test_t018_o_controle_e_o_summary_e_a_linha_continua_sendo_link(client, certame):
    """`FR-620` — a `FR-600` da `040` manda a linha levar ao Edital; as duas não disputam clique."""
    edital, _ = certame
    corpo = abrir(client)

    assert reverse("interface:detalhe", args=[edital.id]) in corpo
    assert "<summary>" in corpo
    # A linha não carrega gatilho de expansão nenhum.
    assert "onclick" not in corpo
    assert not re.search(r"<tr[^>]*\bdata-toggle", corpo)


def test_t015_os_perfis_trazem_codigo_e_localidade_como_publicados(client, certame):
    visivel = texto(abrir(client))

    # O `seed_demo` publica Perfis com código; a localidade some quando não declarada.
    assert "Perfi" in visivel
    assert "não informada" not in visivel


def test_t020_a_diferenca_sem_perfil_vigente_nao_vira_linha_da_tabela(client, certame):
    """`FR-613a` — quando houver, é texto; e nunca *Outros*, *Removidos* ou *Sem Perfil*.

    **A asserção é sobre a tabela de Perfis, e não sobre a página**: a proibição é de inventar uma
    *linha* que faça as vezes de Perfil. A primeira versão varria o documento inteiro e passou a
    falhar quando o resumo do bloco de limitações escreveu *"Outros três limites"* — palavra certa,
    lugar nenhum a ver.
    """
    corpo = abrir(client)
    tabelas = re.findall(r"<table class=\"tabela-de-perfis\".*?</table>", corpo, re.S)
    assert tabelas, "a expansão tem tabela de Perfis"

    for tabela in tabelas:
        visivel = texto(tabela)
        for inventado in ("Outros", "Removidos", "Sem Perfil"):
            assert inventado not in visivel


def test_t023_com_um_perfil_so_a_marca_do_edital_e_a_do_perfil(client, certame):
    """`R-004` — os Editais do `certame` têm **um** Perfil, e aí *"1 de 1"* seria aritmética
    falando com quem quer português. A mensagem do Edital é a do próprio Perfil.
    """
    visivel = texto(abrir(client, "?periodo=encerrado"))

    assert "Encerrou sem nenhuma inscrição submetida." in visivel
    assert "de 1 Perfil" not in visivel


def test_t023b_com_varios_perfis_a_marca_nomeia_quantos_de_quantos(
    client, api_client, manager_headers, certame
):
    """A `US2` na tela, no Edital misto: cada espécie com o **seu** denominador.

    Dois Perfis vigentes, um só deles com vaga imediata e sem nenhuma inscrição — *sem procura*
    conta sobre os **dois**, *demanda abaixo* sobre o **um** que publica vaga.
    """
    edital, _ = certame
    agora = timezone.now()
    draft = rascunho_com_periodo(8, fim=agora + timedelta(days=5))
    com_vaga = draft["profiles"][0]
    so_reserva = {
        **com_vaga,
        "id": perfil_de(9),
        "code": "RESERVA",
        "name": "Só cadastro reserva",
        "immediateVacancies": 0,
        "reserveType": "UNLIMITED",
        "classificationMilestones": [marco_minimo(identidade_do_marco(perfil_de(9)))],
    }
    draft["profiles"] = [com_vaga, so_reserva]
    varios = publicar_no_processo(
        api_client,
        manager_headers,
        edital.processo,
        draft=draft,
        number="45",
        year=edital.year,
        chave="visao-geral-varios-perfis",
    )
    encerrar_inscricoes(api_client, varios, agora - timedelta(days=1), suffix="var")

    visivel = texto(abrir(client, "?periodo=encerrado"))

    assert "2 de 2 Perfis sem nenhuma inscrição" in visivel
    assert "1 de 1 Perfil com vaga imediata abaixo da oferta" in visivel


# ---------------------------------------------------------------------------
# US3 — Somente com atenção
# ---------------------------------------------------------------------------


def test_t027_o_filtro_reduz_a_tabela_e_o_consolidado_acompanha(client, certame):
    """`FR-621`, `SC-221` — como os demais filtros da `040`, os dois se movem juntos."""
    sem_filtro = texto(abrir(client, "?ano=2026"))
    com_filtro = texto(abrir(client, "?ano=2026&atencao=1"))

    # O Edital com inscrições abertas não tem marca e sai; os encerrados sem procura ficam.
    assert "Edital 40/2026" in sem_filtro
    assert "Edital 40/2026" not in com_filtro
    assert "Edital 41/2026" in com_filtro
    # E o consolidado acompanha: o número cai junto com a tabela, e flexiona.
    assert "2 Editais" in sem_filtro
    assert "1 Edital" in com_filtro and "1 Editais" not in com_filtro


def test_t028_filtro_sem_nenhum_marcado_declara_recorte_vazio(client, certame):
    """E não afirma nada sobre o acervo — a mesma frase que a `040` fixou."""
    visivel = texto(abrir(client, "?ano=2027&atencao=1"))

    assert "Nenhum Edital no período selecionado" in visivel
    assert "Isto não é uma afirmação sobre o acervo" in visivel


def test_o_controle_do_filtro_tem_rotulo_associado(client, certame):
    corpo = abrir(client)

    assert 'for="f-atencao"' in corpo
    assert 'name="atencao"' in corpo and 'id="f-atencao"' in corpo


# ===========================================================================
# 042 — a hierarquia do detalhe
# ===========================================================================


def test_t008_um_tbody_por_edital_e_o_caso_vazio_no_seu_grupo(client, certame):
    """`R-002` — o separador passa a ser do **grupo**, e é isso que permite régua e recuo."""
    corpo = abrir(client)
    # Duas subtrações antes de contar. A folha, **porque a prosa dela escreve `<tbody>`** ao
    # explicar a regra do grupo — e uma varredura que a leia mede o comentário, não a tela. E as
    # tabelas filhas, que têm `<tbody>` próprio: válido, e grupo delas, não desta.
    sem_folha = re.sub(r"<(style|script)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    externa = re.sub(r'<table class="tabela-de-perfis">.*?</table>', " ", sem_folha, flags=re.S)
    grupos = re.findall(r"<tbody>", externa)
    linhas_de_edital = re.findall(r'<tr>\s*<th scope="row">\s*<a href="/gestao/editais/', externa)

    assert len(grupos) == len(linhas_de_edital) >= 2
    # O `<details>` continua dentro do `<td>`, e o grupo não o mudou de lugar.
    assert re.search(r'<tr class="expansao-do-edital">\s*<td colspan="8">', corpo)
    assert not re.search(r"<tr[^>]*>\s*<details", corpo)

    vazio = abrir(client, "?ano=1999")
    assert re.search(r'<tbody>\s*<tr><td colspan="8" class="vazio">', vazio)


def test_t009_a_tabela_filha_tem_uma_coluna_de_identidade_e_cinco_de_dado(client, certame):
    """`FR-627`, `SC-224` — seis na tela, e **nenhuma** de cadastro de reserva."""
    corpo = abrir(client)
    interna = re.search(r'<table class="tabela-de-perfis">.*?</thead>', corpo, re.S).group(0)
    colunas = re.findall(r'<th scope="col"[^>]*>([^<]*)</th>', interna)

    assert colunas == [
        "Perfil",
        "Vagas imediatas",
        "Submetidas",
        "Em preenchimento",
        "Inscr./vaga",
        "Atenção",
    ]
    assert "Cadastro de reserva" not in interna


def test_t009b_as_tres_especies_de_reserva_se_distinguem_na_identidade(
    client, api_client, manager_headers, certame
):
    """`FR-626`, `SC-224` — o que era coluna virou atributo, e nenhuma das três se perdeu."""
    edital, _ = certame
    agora = timezone.now()
    draft = rascunho_com_periodo(7, fim=agora + timedelta(days=5))
    sem = draft["profiles"][0]
    limitada = {
        **sem,
        "id": perfil_de(8),
        "code": "LIM",
        "name": "Reserva limitada",
        "reserveType": "LIMITED",
        "reserveLimit": 12,
        "classificationMilestones": [marco_minimo(identidade_do_marco(perfil_de(8)))],
    }
    ilimitada = {
        **sem,
        "id": perfil_de(9),
        "code": "ILI",
        "name": "Reserva ilimitada",
        "reserveType": "UNLIMITED",
        "classificationMilestones": [marco_minimo(identidade_do_marco(perfil_de(9)))],
    }
    draft["profiles"] = [sem, limitada, ilimitada]
    com_reserva = publicar_no_processo(
        api_client,
        manager_headers,
        edital.processo,
        draft=draft,
        number="07",
        year=edital.year,
        chave="visao-geral-tres-reservas",
    )
    encerrar_inscricoes(api_client, com_reserva, agora - timedelta(days=1), suffix="res")

    corpo = abrir(client, "?periodo=encerrado")
    nos_perfis = texto(
        "".join(re.findall(r'<table class="tabela-de-perfis">.*?</table>', corpo, re.S))
    )

    assert "CR limitado a 12" in nos_perfis
    assert "CR ilimitado" in nos_perfis
    # E quem **não** tem reserva não escreve nada: ausência de atributo não é dado.
    assert "não há" not in nos_perfis
    assert nos_perfis.count("CR ") == 2


def test_t010_a_mesma_frase_nao_aparece_nas_duas_granularidades(client, certame):
    """`FR-628`, `SC-225` — o Edital resume com denominador; o Perfil rotula."""
    corpo = abrir(client, "?periodo=encerrado")
    tabelas = re.findall(r'<table class="tabela-de-perfis">.*?</table>', corpo, re.S)
    nos_perfis = texto("".join(tabelas))
    frase = "Encerrou sem nenhuma inscrição submetida."

    assert "Sem procura" in nos_perfis
    assert frase not in nos_perfis
    # E a frase longa continua existindo — no Edital de um Perfil só, que é o resumo dele.
    assert frase in texto(corpo)


def test_t011_o_controle_tem_dois_rotulos_e_a_legenda_e_invisivel(client, certame):
    """`FR-622`, `FR-625`, `FR-629`, `SC-226`."""
    corpo = abrir(client)

    assert '<span class="ao-abrir">Mostrar</span><span class="ao-fechar">Ocultar</span>' in corpo
    assert "Perfis de vaga" in texto(corpo) or "Perfil de vaga" in texto(corpo)
    # A legenda fica no documento e não é desenhada.
    assert '<caption class="oculto">' in corpo
    # **Zero** JavaScript novo: a página não carrega script algum além do que a `040` já não tinha.
    assert "<script" not in corpo


def test_t012_os_rotulos_de_ordenacao_nao_embutem_direcao(client, certame):
    """`FR-630`, `SC-227` — e as **chaves** continuam as mesmas (`R-007`)."""
    corpo = abrir(client)

    for embutida in ("Mais recentes", "Maior primeiro", "Menor primeiro"):
        assert embutida not in corpo
    for rotulo in ("Data do Edital", "Decrescente", "Crescente"):
        assert rotulo in corpo
    assert 'name="ordem"' in corpo and 'value="recentes"' in corpo
    assert 'name="sentido"' in corpo and 'value="desc"' in corpo


def test_fr632_a_tabela_filha_declara_a_grade_e_nao_a_negocia(client, certame):
    """A grade precisa estar **no documento**, uma `<col>` por coluna, ou a folha não a alcança."""
    corpo = abrir(client)
    interna = re.search(r'<table class="tabela-de-perfis">.*?</thead>', corpo, re.S).group(0)
    colunas = re.findall(r'<col class="(c-[\w-]+)">', interna)
    cabecalhos = re.findall(r'<th scope="col"[^>]*>', interna)

    assert colunas == [
        "c-perfil",
        "c-vagas",
        "c-submetidas",
        "c-preenchimento",
        "c-razao",
        "c-atencao",
    ]
    # Uma `<col>` a menos e a última coluna volta a se dimensionar sozinha, sem nada acusar.
    assert len(colunas) == len(cabecalhos)


def test_fr633_a_marca_do_perfil_continua_sendo_texto(client, certame):
    """Rebaixar não é apagar: o que cai é o tamanho, e a `FR-602` da `040` segue de pé."""
    corpo = abrir(client, "?periodo=encerrado")
    nos_perfis = texto(
        "".join(re.findall(r'<table class="tabela-de-perfis">.*?</table>', corpo, re.S))
    )

    assert "Sem procura" in nos_perfis


def test_o_cabecalho_numerico_se_declara_nas_duas_tabelas(client, certame):
    """A classe é o que a folha alcança; sem ela o rótulo volta à esquerda sem nada acusar."""
    corpo = abrir(client)
    interna = re.search(r'<table class="tabela-de-perfis">.*?</thead>', corpo, re.S).group(0)
    externa = corpo[: corpo.index('<table class="tabela-de-perfis">')]

    for coluna in ("Vagas imediatas", "Submetidas", "Em preenchimento", "Inscr./vaga"):
        assert f'<th scope="col" class="numero">{coluna}</th>' in interna, coluna
    for coluna in ("Vagas", "Submetidas", "Em preenchimento", "Inscr./vaga"):
        assert f'<th scope="col" class="numero">{coluna}</th>' in externa, coluna
    # Atenção e Perfil são texto, e continuam à esquerda.
    assert '<th scope="col">Atenção</th>' in interna
    assert '<th scope="col">Perfil</th>' in interna


def test_a_marca_de_parcial_nao_repete_o_motivo_ao_lado_do_numero(client, certame):
    """Gramática da `040` emendada pela `042`.

    Por extenso, a frase ocupava **73 px** numa célula de 108 — metade da altura da linha — em
    prosa alinhada à direita, para ressalvar um número. E repetia o que a coluna *Período* da mesma
    linha acabara de dizer: existe **um** motivo de parcialidade nesta tela, atribuído exatamente
    quando o período está aberto, que é exatamente quando aquela coluna escreve *"Inscrições
    abertas"*. O motivo continua na linha; o que saiu foi a repetição colada ao número.
    """
    corpo = abrir(client, "?periodo=aberto")
    tabela = re.search(r'<table class="tabela-da-visao">.*?</table>', corpo, re.S).group(0)

    assert '<span class="parcial">parcial</span>' in tabela
    # O motivo não é repetido ao lado do número...
    assert "as inscrições ainda estão abertas" not in texto(tabela)
    # ...e continua legível na linha, dito pela coluna que é dona dele.
    assert "Inscrições abertas" in texto(tabela)


def test_fr595_a_razao_tambem_declara_que_e_parcial(client, certame):
    """A derivação marcava, e o template descartava — a tela dizia `3,0` como número fechado.

    É o tipo de defeito que nenhum teste de modelo pega: `linha.razao.parcial` era `True` o tempo
    todo, e a asserção sobre ele passava. O que faltava era alguém olhar a **tela**.
    """
    corpo = abrir(client, "?periodo=aberto")
    linha = re.search(r'<tbody>\s*<tr>\s*<th scope="row">.*?</tr>', corpo, re.S).group(0)
    celulas = re.findall(r'<td class="numero">(.*?)</td>', linha, re.S)

    # Submetidas e Inscr./vaga são as duas parciais enquanto o período corre.
    parciais = [c for c in celulas if 'class="parcial"' in c]
    assert len(parciais) == 2, celulas
