"""O formulário deixa de oferecer o que a escolha ao lado torna proibido ou inútil.

Duas telas do assistente pediam ao elaborador que carregasse a regra de cabeça.

Na **Etapa de Avaliação**, o domínio é categórico (012, FR-033, FR-121): a forma pontuada *proíbe*
os rótulos do resultado, e a decisória *proíbe* as notas. O formulário mostrava os quatro campos,
sempre, habilitados, com `placeholder="Deferido"` convidando a preencher — e a submissão recusava
depois. A recusa estava certa; o convite é que não devia existir.

No **marco classificatório**, `_janela_recursal` descarta o prazo de quem não admite recurso. O
formulário mostrava "Prazo, em dias" habilitado ao lado das três opções, inclusive sob "Não declarar
nada sobre recurso". Quem digitasse 5 ali salvava, não recebia erro nenhum, e o prazo não existia.

No **Perfil de Vaga**, `validate_profile` recusa limite na reserva inexistente e na ilimitada, e o
exige na limitada. `ler_perfis` já descartava o que não fosse limitado — faltava a metade da tela,
que oferecia "Limite da reserva" nas três e se explicava numa frase: "Só para reserva limitada."

Um recusava tarde; o outro não recusava nunca; o terceiro descartava sem dizer. O que estes
testes prendem é a divisão do trabalho:
**a folha esconde, o servidor descarta.** Esconder sozinho não bastaria, porque campo escondido
continua sendo enviado e porque envio forjado não passa por tela nenhuma.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import PERFIL, etapa, etapas_form, eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def bloco(corpo, classe):
    """O conteúdo do `div` que carrega esta classe, até o `</div>` que o fecha.

    Serve porque a pergunta destes testes não é "o campo existe na página" — ele sempre existiu —,
    e sim **dentro de qual opção** ele está. Nenhum destes blocos aninha outro `div`.
    """
    marca = f'class="campos dependentes {classe}"'
    inicio = corpo.index(marca)
    return corpo[inicio : corpo.index("</div>", inicio)]


@pytest.fixture
def elaborando(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    return edital


def marco_de(client, edital):
    """O fragmento do marco, que é onde `_marco.html` de fato se renderiza.

    A página da classificação só o inclui para marcos que já existem; o assistente os cria pelo
    botão "Acrescentar marco", que busca este endereço. Pedi-lo aqui é percorrer o mesmo caminho.
    """
    return client.get(
        reverse("interface:fragmento-marco", args=[PERFIL]),
        {"edital": str(edital.id), "indice": "0"},
    ).content.decode()


# ------------------------------------------------ o servidor descarta o que a forma proíbe


def test_a_etapa_pontuada_nao_grava_o_rotulo_que_a_forma_proibe(client, elaborando):
    """Quem digitou "Deferido" e depois marcou "Com pontuação" continua enviando o rótulo."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(
            **{
                "etapa-0-forma": "PONTUADA",
                "etapa-0-rotuloFavoravel": "Deferido",
                "etapa-0-rotuloDesfavoravel": "Indeferido",
            }
        ),
    )

    gravada = EtapaAvaliacao.objects.order_by("order").first()
    assert gravada.forma == "PONTUADA"
    assert (gravada.rotulo_favoravel, gravada.rotulo_desfavoravel) == ("", ""), (
        "a Etapa pontuada gravou um rótulo que a validação recusa na submissão"
    )


def test_a_etapa_decisoria_nao_grava_a_nota_que_a_forma_proibe(client, elaborando):
    """O caminho inverso, que nem frase de ajuda tinha: a decisória proíbe as duas notas."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(
            **{
                "etapa-0-forma": "DECISORIA",
                "etapa-0-rotuloFavoravel": "Deferido",
                "etapa-0-rotuloDesfavoravel": "Indeferido",
                "etapa-0-minimumScore": "7",
                "etapa-0-maximumScore": "10",
            }
        ),
    )

    gravada = EtapaAvaliacao.objects.order_by("order").first()
    assert gravada.forma == "DECISORIA"
    assert (gravada.minimum_score, gravada.maximum_score) == (None, None)
    # E o que a forma escolhida **pede** continua chegando inteiro.
    assert (gravada.rotulo_favoravel, gravada.rotulo_desfavoravel) == ("Deferido", "Indeferido")


def test_forma_desconhecida_continua_alcancavel_pela_validacao(client, elaborando):
    """A leitura não normaliza `forma`: trocá-la por PONTUADA esconderia o envio forjado."""
    client.post(etapa(elaborando, "etapas"), etapas_form(**{"etapa-0-forma": "SORTEIO"}))

    assert EtapaAvaliacao.objects.order_by("order").first().forma == "SORTEIO"


# ------------------------------------------------ a tela aninha o campo dentro da opção


def test_cada_forma_carrega_na_tela_os_campos_que_so_ela_admite(client, elaborando):
    client.post(etapa(elaborando, "etapas"), etapas_form())

    corpo = client.get(etapa(elaborando, "etapas")).content.decode()

    pontuada = bloco(corpo, "so-pontuada")
    assert 'name="etapa-0-minimumScore"' in pontuada
    assert 'name="etapa-0-maximumScore"' in pontuada
    assert "rotulo" not in pontuada

    decisoria = bloco(corpo, "so-decisoria")
    assert 'name="etapa-0-rotuloFavoravel"' in decisoria
    assert 'name="etapa-0-rotuloDesfavoravel"' in decisoria
    assert "Score" not in decisoria

    # E os dois blocos ficam **dentro** do grupo que os governa, e não como irmãos dele na fileira.
    grupo = corpo.index('<fieldset class="opcoes">')
    assert grupo < corpo.index('class="campos dependentes so-pontuada"')
    assert grupo < corpo.index('class="campos dependentes so-decisoria"')


def test_o_prazo_do_recurso_mora_dentro_da_opcao_que_o_pede(client, com_etapas):
    corpo = marco_de(client, com_etapas)

    admite = bloco(corpo, "so-admite")
    assert "appealDurationDays" in admite
    assert "appealUnit" in admite
    # A opção que o pede vem antes dele, e a que dispensa vem depois: é isso que faz a dependência
    # ser lida sem frase de ajuda nenhuma.
    assert corpo.index('value="admite"') < corpo.index('class="campos dependentes so-admite"')
    assert corpo.index('class="campos dependentes so-admite"') < corpo.index(
        'value="nao_declarada"'
    )


def test_as_opcoes_nao_usam_mais_a_classe_da_marca_de_filtrar(client, com_etapas):
    """`campo escolha` punha as três numa fileira, com a bolinha acima do próprio texto."""
    assert 'class="campo escolha"' not in marco_de(client, com_etapas)


def test_o_limite_mora_dentro_da_reserva_que_o_admite(client, elaborando):
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    limitada = bloco(corpo, "so-limitada")
    assert 'name="perfil-0-reserveLimit"' in limitada
    # E entre a opção que o pede e a que não o admite, na ordem em que se lê.
    assert corpo.index('value="LIMITED"') < corpo.index('class="campos dependentes so-limitada"')
    assert corpo.index('class="campos dependentes so-limitada"') < corpo.index('value="UNLIMITED"')


def test_a_reserva_deixou_de_ser_um_select_sem_onde_aninhar(client, elaborando):
    """`select` não tem lugar para o campo que a escolha pede; as três viraram opções."""
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    assert 'name="perfil-0-reserveType"' in corpo
    assert '<select id="perfil-0-reserveType"' not in corpo
    for valor in ("NONE", "LIMITED", "UNLIMITED"):
        assert f'id="perfil-0-reserveType-{valor}"' in corpo
        assert f'for="perfil-0-reserveType-{valor}"' in corpo


def test_a_reserva_nasce_com_uma_opcao_marcada(client, elaborando):
    """Sem marcada, a folha não teria o que esconder — e o limite apareceria fora da reserva."""
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    opcoes = re.findall(r'<input type="radio"[^>]*name="perfil-0-reserveType"[^>]*>', corpo, re.S)
    assert len(opcoes) == 3
    marcadas = [re.search(r'value="(\w+)"', tag).group(1) for tag in opcoes if "checked" in tag]
    assert marcadas == ["NONE"]


def test_a_ajuda_do_limite_deixou_de_pedir_desculpa_pela_propria_posicao(client, elaborando):
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    assert "Só para reserva limitada" not in corpo


# ------------------------------------------------ a folha esconde o que a escolha torna inaplicável


@pytest.fixture
def folha(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


@pytest.mark.parametrize(
    ("marcada", "escondido"),
    [
        ('input[name$="-forma"][value="DECISORIA"]:checked', ".so-pontuada"),
        ('input[name$="-forma"][value="PONTUADA"]:checked', ".so-decisoria"),
        ('input[name$="-appealDeclaration"]:checked:not([value="admite"])', ".so-admite"),
        ('input[name$="-reserveType"]:checked:not([value="LIMITED"])', ".so-limitada"),
    ],
)
def test_a_folha_esconde_o_que_a_escolha_marcada_torna_inaplicavel(folha, marcada, escondido):
    assert f":has({marcada}) {escondido}" in folha


def test_a_folha_nunca_esconde_por_padrao(folha):
    """Sem `:has`, tudo aparece como antes — e o servidor continua descartando o certo.

    Uma regra `\\.so-admite{display:none}` solta inverteria isso: o campo sumiria para sempre em
    navegador sem suporte, e a opção que o pede não teria como trazê-lo de volta.
    """
    for classe in ("so-pontuada", "so-decisoria", "so-admite", "so-limitada"):
        # `\n` na classe de caracteres, e não só `^`: sem ela a guarda passava por cima de uma
        # regra escrita em linha própria — que é exatamente como alguém a escreveria.
        assert not re.search(rf"(?:^|[\n,;\}}])\s*\.{classe}\s*\{{", folha), classe


def test_a_bolinha_nao_herda_a_largura_do_campo(folha):
    """`.campo input{width:100%}` fazia o marcador virar uma faixa, centralizado longe do texto."""
    assert re.search(
        r"\.opcoes \.opcao input\[type=radio\]\{[^}]*width:auto",
        folha,
    )


# ------------------------------------------------ o seletor vazio diz o que fazer


def test_sem_etapa_classificatoria_o_seletor_diz_o_que_fazer(client, elaborando):
    """Nenhuma Etapa foi marcada como classificatória: era uma caixa vazia e obrigatória."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-classificatory": "", "etapa-1-classificatory": ""}),
    )

    corpo = marco_de(client, elaborando)

    assert "Classificatória" in corpo
    assert "Etapas de\n        Avaliação" in corpo or "Etapas de Avaliação" in corpo
    # E não sobra um controle obrigatório que ninguém consegue preencher.
    assert not re.search(r'name="marco-[^"]*-stages"[^>]*required', corpo)


def test_com_etapa_classificatoria_o_seletor_volta_a_ser_seletor(client, com_etapas):
    corpo = marco_de(client, com_etapas)

    assert re.search(r'name="marco-[^"]*-stages"[^>]*multiple', corpo)
    assert "Prova didática" in corpo


def test_o_arredondamento_nao_se_oferece_como_travessao(client, com_etapas):
    """Um travessão não é instrução, e o campo é obrigatório."""
    corpo = marco_de(client, com_etapas)

    assert '<option value="">Escolha o arredondamento</option>' in corpo
    assert '<option value="">—</option>' not in corpo
