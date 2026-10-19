"""Fronteira de autenticação da interface (Decisão 4 do plano da 002).

A interface obtém identidade, escopo e permissões daqui, e não sabe como esse dado é
produzido. Quando o diretório institucional for integrado, só este módulo muda.

Enquanto isso, a identidade vem da sessão, escolhida num seletor que **existe apenas fora de
produção**. O adaptador não é fronteira de segurança: quem decide autorização continua sendo o
backend, em cada command.
"""

from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from processo_seletivo.seguranca.domain import Actor

CHAVE_SESSAO = "interface_identidade"
ESCOPO_PADRAO = "cefor"

# Papéis de responsabilidade, conforme FR-026/FR-027. Cada um reúne um conjunto fixo de
# permissões; quando o diretório for integrado, cada papel corresponderá a um grupo dele.
PAPEIS = {
    "elaborador": (
        "Elaborador",
        ["edital:elaborar", "edital:submeter", "retificacao:elaborar", "retificacao:submeter"],
    ),
    "homologador": ("Homologador", ["edital:homologar", "retificacao:homologar"]),
    "publicador": (
        "Publicador",
        [
            "edital:publicar",
            "retificacao:publicar",
            # Divulgar o resultado é ato de quem publica — e é capacidade **própria**, e não efeito
            # de `classificacao:emitir`: emitir constitui a ordem, publicar a torna pública, e são
            # atos de autoridades distintas. Quem emitiu o ato não ganha, por tê-lo emitido, o
            # poder de divulgá-lo (017, FR-025, FR-026).
            "resultado:publicar",
            # Avisar os candidatos de um ato publicado (066, `D-004`). **Capacidade própria, e não
            # efeito de `resultado:publicar`**: quem publica o resultado não é necessariamente quem
            # fala com o candidato, e quem avisa não ganha, por avisar, o poder de publicar
            # (`FR-1275`). Vai a quem publica e a quem conduz o Processo; a presidência da comissão
            # entra pelo vínculo, como em `comissao:gerir`. A grafia é conferida por
            # `tests/authorization/test_papel_do_aviso.py`.
            "aviso:enviar",
        ],
    ),
    "gestor": (
        "Gestor",
        [
            # Ler o que os candidatos enviaram é permissão própria, e não efeito colateral de
            # outra: nenhuma das existentes significa "pode ler dado pessoal de candidato", e
            # reaproveitar uma para abrir documento comprobatório seria decidir por omissão o que
            # a Constituição manda decidir explicitamente. O papel é o que já existia — quem
            # conduz a seleção é quem confere o que chegou (009, FR-072).
            "inscricao:consultar",
            "processo:criar",
            "processo:ativar",
            "processo:encerrar",
            "processo:cancelar",
            "edital:criar",
            "edital:encerrar",
            "edital:cancelar",
            # Cancelar Retificação é do Gestor pelo mesmo espelho: quem detém `edital:cancelar`
            # abandona o ato em preparação. Quem elabora não ganha, por elaborar, o poder de
            # eliminar o ato (E2E-021).
            "retificacao:cancelar",
            # Constituir a comissão é ato de quem conduz o Processo (011, FR-016). É a base
            # **sistêmica** de gestão; a outra base é a presidência, que não é papel e por isso
            # não aparece aqui — ela é verificada contra o vínculo, objeto a objeto.
            "comissao:gerir",
            # Ler o panorama institucional — o conjunto dos certames do escopo, acima do Processo
            # (040, FR-604). **Capacidade própria, e não efeito de outra**: reusar
            # `inscricao:consultar` concederia o panorama a quem pode abrir dossiê de candidato, e
            # `auditoria:consultar` o concederia a quem lê trilha — duas permissões que respondem
            # por outras perguntas. É a mesma recusa que `matricula:exportar` registrou.
            #
            # **Vai ao Gestor porque é ele quem hoje conduz os Processos do escopo.** Um papel
            # próprio de Diretoria custaria uma entrada neste mapa e é decisão institucional, não
            # técnica: está registrada como pendente na spec da 040 e não é tomada aqui.
            #
            # A permissão vai **escrita**, como todas as deste mapa: este módulo é a fronteira de
            # identidade e não deve conhecer quem a consome. A grafia é conferida por
            # `tests/authorization/test_visao_institucional.py`.
            "visao:consultar",
            # Manter as autoridades da própria unidade — cadastrar, corrigir e encerrar (060,
            # `D-005`). **Configuração administrativa da unidade, e não ato de publicação**: quem a
            # tem não publica por tê-la, e quem publica não a ganha por publicar. Permissão própria,
            # e não efeito de outra, para que destacá-la para outro papel — se o Ifes pedir gestão
            # centralizada — custe esta linha e nenhuma mudança no modelo. A grafia é conferida por
            # `tests/authorization/test_gerir_autoridades.py`.
            "autoridade:gerir",
            # O mesmo aviso aos candidatos do publicador (066, `D-004`): quem conduz o Processo é
            # quem mais fala com quem se inscreveu nele.
            "aviso:enviar",
        ],
    ),
    # Papel **próprio**, e não uma capacidade acrescentada a um existente (D-005, T-005). Cada
    # papel que já existe reúne quem tende a estar impedido: quem elabora e publica o Edital
    # também divulga o resultado atacado, e quem gere o Processo preside a comissão que avaliou.
    # Pendurar `recurso:julgar` em qualquer um deles concederia o julgamento, por construção, a
    # quem a FR-039 manda afastar — e o impedimento viraria a regra em vez da exceção.
    "julgador": ("Julgador de recursos", ["recurso:julgar"]),
    "auditor": ("Auditor", ["auditoria:consultar"]),
    # Papel **próprio**, e não uma capacidade acrescentada a um existente — a mesma forma que o
    # julgador de recursos tem, e pela mesma razão (031, `FR-455`). O arquivo de importação reúne
    # CPF, RG, filiação e endereço de toda a população numa peça só; pendurar `matricula:exportar`
    # no Gestor concederia esse acesso, por construção, a quem já tem `inscricao:consultar` — e a
    # `FR-455` diz, com todas as letras, que ler um dossiê por vez e baixar o conjunto inteiro são
    # atos distintos.
    #
    # **Nenhum papel existente ganha a permissão**, e é isso que "negar por padrão" significa aqui:
    # quem não assumir este papel não exporta, por caminho nenhum. Se a opção não aparecer no
    # Edital, é autorização — e não rota quebrada.
    #
    # **A permissão vai escrita, e não importada de `matriculas`**, como todas as outras deste
    # mapa: este módulo é a fronteira de identidade, e não deve conhecer o app que consome a
    # permissão. A grafia é conferida por `tests/authorization/test_exportacao_de_matriculas.py`.
    "exportador": ("Exportador de matrículas", ["matricula:exportar"]),
    # O piloto do assistente do Edital (071, `D-001`, `FR-1461`). Papel **próprio**, e não
    # capacidade acrescentada ao Gestor ou a outro do setor: o piloto tem participantes escolhidos,
    # e não um papel; e cada pergunta chama um serviço com custo e com efeito sobre a GPU. Nenhum
    # papel existente ganha a permissão. Os registros do piloto não têm tela, e por isso não há
    # segunda permissão. A grafia é conferida por `tests/authorization/test_papel_do_piloto.py`.
    "participante-piloto-assistente": (
        "Participante do piloto do assistente",
        ["assistente:piloto"],
    ),
}


# O que cada papel faz, em palavras de quem o exerce (075, `FR-1692`, `D-004`). A tela de entrada
# mostra isto **no lugar** dos códigos de permissão, que continuam sendo o que a autorização lê.
# Mapa à parte, e não terceiro elemento da tupla: cinco testes de autorização leem o papel como par
# (`T-004` da 075). O guardião de `FR-1701` cobra que as chaves dos dois mapas sejam as mesmas.
DESCRICOES = {
    "elaborador": "Redige Editais e Retificações e os envia para homologação.",
    "homologador": "Confere e homologa Editais e Retificações antes da publicação.",
    "publicador": "Publica Editais, Retificações e resultados, e avisa os candidatos.",
    "gestor": (
        "Conduz os Processos da unidade: abre e encerra, constitui comissões, consulta inscrições "
        "e mantém as autoridades."
    ),
    "julgador": "Julga os recursos interpostos pelos candidatos.",
    "auditor": "Consulta a trilha de auditoria dos atos praticados.",
    "exportador": "Exporta o arquivo de matrículas dos convocados.",
    "participante-piloto-assistente": "Participa do piloto do assistente do Edital.",
}

# A origem da identidade na sessão (075, `FR-1698`). Hoje só existe uma; o diretório institucional
# será a segunda, e é ela que continua valendo com o seletor desligado.
ORIGEM_DEMONSTRACAO = "demonstracao"


def permissoes_de(papeis):
    return frozenset(permissao for papel in papeis for permissao in PAPEIS.get(papel, ("", []))[1])


def ator_da_sessao(request):
    """Ator autenticado, ou None quando ninguém foi identificado ainda.

    **A identidade da demonstração não sobrevive ao seletor desligado** (075, `FR-1698`). Antes, a
    sessão aberta pelo seletor valia para sempre: desligar a chave no mesmo banco de sessões não
    tirava ninguém de dentro. Sessão sem origem é anterior à 075, e a única origem que existia era
    a demonstração (`D-005`). Apagar, e não só ignorar, impede que ela volte a valer quando a chave
    for religada sem nova escolha.
    """
    dados = request.session.get(CHAVE_SESSAO)
    if not dados:
        return None
    if dados.get("origem", ORIGEM_DEMONSTRACAO) == ORIGEM_DEMONSTRACAO and not seletor_disponivel():
        encerrar(request)
        return None
    return Actor(dados["subject"], dados["escopo"], permissoes_de(dados["papeis"]))


def identificar(request, *, subject, papeis, escopo=ESCOPO_PADRAO, origem=ORIGEM_DEMONSTRACAO):
    request.session[CHAVE_SESSAO] = {
        "subject": subject,
        "escopo": escopo,
        "papeis": list(papeis),
        "origem": origem,
    }


def encerrar(request):
    request.session.pop(CHAVE_SESSAO, None)


def seletor_disponivel():
    return bool(getattr(settings, "INTERFACE_SELETOR_IDENTIDADE", False))


def metodos_disponiveis():
    """Por onde se entra na gestão neste ambiente (075, `FR-1691`).

    A página de acesso desenha o que esta lista disser, e só isso. Quando o diretório
    institucional chegar, ele entra aqui como outro método, e a página não precisa ser redesenhada.
    Lista vazia é produção hoje: a página diz que a entrada não está configurada.
    """
    return [ORIGEM_DEMONSTRACAO] if seletor_disponivel() else []


def destino_seguro(request, valor):
    """O destino pedido, se ele for um caminho da própria gestão — ou None (075, `FR-1696`).

    `url_has_allowed_host_and_scheme` sozinho aceitaria qualquer caminho do mesmo host, e o portal é
    o mesmo host: a pessoa sairia da gestão depois de se identificar nela (`T-001`). A identificação
    e a saída ficam de fora para não haver laço.
    """
    if not valor:
        return None
    if not url_has_allowed_host_and_scheme(
        valor, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return None
    caminho = urlsplit(valor).path
    if not caminho.startswith(reverse("interface:lista")):
        return None
    if caminho.startswith((reverse("interface:identificar"), reverse("interface:sair"))):
        return None
    return valor


def pedir_identificacao(request):
    """O redirecionamento de toda porta da gestão para quem ainda não tem identidade (075, `D-002`).

    Leva o próprio endereço como destino, e por isso a pessoa volta a ele depois de se identificar.
    **Só em GET**: um POST não se repete por redirecionamento, e reenviar o ato depois da
    identificação seria praticar algo que a pessoa não confirmou.
    """
    destino = reverse("interface:identificar")
    if request.method == "GET" and destino_seguro(request, request.get_full_path()):
        destino += "?" + urlencode({"proximo": request.get_full_path()})
    return redirect(destino)


def contexto_identidade(request):
    """Disponibiliza a identidade a todos os templates, sem cada view precisar repassá-la."""
    ator = ator_da_sessao(request)
    dados = (request.session.get(CHAVE_SESSAO) or {}) if ator else {}
    return {
        "ator": ator,
        "papeis_do_ator": [PAPEIS[p][0] for p in dados.get("papeis", []) if p in PAPEIS],
        "seletor_identidade": seletor_disponivel(),
        # O portal oferece a porta da gestão só onde há por onde entrar (075, `FR-1699`). É o único
        # dado da gestão que o portal lê, e não diz nada sobre quem está identificado.
        "metodos_de_acesso": metodos_disponiveis(),
    }
