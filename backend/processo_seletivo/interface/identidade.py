"""Fronteira de autenticação da interface (Decisão 4 do plano da 002).

A interface obtém identidade, escopo e permissões daqui, e não sabe como esse dado é
produzido. Quando o diretório institucional for integrado, só este módulo muda.

Enquanto isso, a identidade vem da sessão, escolhida num seletor que **existe apenas fora de
produção**. O adaptador não é fronteira de segurança: quem decide autorização continua sendo o
backend, em cada command.
"""

from dataclasses import dataclass, field
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from django.utils.http import url_has_allowed_host_and_scheme

from processo_seletivo.seguranca.domain import Actor

CHAVE_SESSAO = "interface_identidade"
ESCOPO_PADRAO = "cefor"

# Papéis de responsabilidade, conforme FR-026/FR-027. Cada um reúne um conjunto fixo de
# permissões. **Não correspondem a grupos do diretório**, como este comentário dizia até a 109: a
# 106 decidiu que o diretório institucional só autentica, e que quem tem cada papel, em cada
# unidade, é vínculo pessoa × unidade × papel mantido no GPS (`seguranca/acessos.py`), concedido e
# revogado pela interface da 107. Este dicionário é o catálogo, e é também o que o seletor de
# demonstração oferece.
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
    # O kit de divulgação do Edital (111, `D-012`, `FR-3403`). Papel **próprio e restrito**: quem
    # divulga não pratica ato, e a capacidade não abre ato nenhum nem leitura além do kit. Nenhum
    # papel existente a ganha. **Não se atribui a ninguém antes da spec da P-2** (`112`): hoje
    # qualquer pessoa da unidade lê rascunho e Retificação em curso pelo detalhe do Edital, e quem é
    # só da comunicação saberia de um ato antes de publicado. A grafia é conferida por
    # `tests/authorization/test_papel_da_comunicacao.py`.
    "comunicacao": ("Comunicação", ["material:gerar"]),
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
    "comunicacao": "Gera os textos e a peça de divulgação dos Editais publicados.",
}

# A origem da identidade na sessão (075, `FR-1698`). A institucional é a segunda (106): é ela que
# continua valendo com o seletor desligado, e a única que produção admite.
ORIGEM_DEMONSTRACAO = "demonstracao"
ORIGEM_INSTITUCIONAL = "institucional"

# O estado de uso único da ida ao provedor (106, `FR-3023`), em chave própria: ele existe antes de
# haver identidade, e não pode sobreviver nela.
CHAVE_ESTADO_INSTITUCIONAL = "interface_estado_institucional"

# Onde a resolução institucional guarda o resultado na própria requisição (106, `D-006`). A página
# lê o ator dezenas de vezes; sem isto, cada leitura seriam duas consultas (`SC-1005`).
_ATOR_DA_REQUISICAO = "_ator_institucional"


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
    if dados.get("origem") == ORIGEM_INSTITUCIONAL:
        return _resolucao_institucional(request, dados).ator
    if dados.get("origem", ORIGEM_DEMONSTRACAO) == ORIGEM_DEMONSTRACAO and not seletor_disponivel():
        encerrar(request)
        return None
    return Actor(dados["subject"], dados["escopo"], permissoes_de(dados["papeis"]))


def _resolucao_institucional(request, dados):
    """O ator institucional, os papéis dele, a pessoa e os escopos, recalculados (106, `D-006`).

    **Nada de papel na sessão.** O que a sessão guarda é a unidade ativa; os papéis vêm dos vínculos
    vigentes ali, e por isso a revogação vale na requisição seguinte (`FR-3017`). Sem vínculo
    vigente na unidade ativa não há ator — e a presidência de uma comissão, que se confere pelo
    `subject` do ator, não alcança quem perdeu o acesso à unidade (`FR-3018`).

    **Sem provedor neste ambiente, a sessão se encerra** (`FR-3028`), pela razão da demonstração sem
    o seletor: a origem que deixou de ser admitida não volta a valer quando a configuração voltar.

    **Os vínculos da pessoa se leem uma vez, todos** (107, `D-006`): deles saem os papéis da unidade
    ativa e os escopos do seletor da barra, e a resolução continua em duas consultas. **Os prazos
    vêm antes** (107, `D-009`): a sessão vencida não lê vínculo nenhum.
    """
    guardado = getattr(request, _ATOR_DA_REQUISICAO, None)
    if guardado is not None:
        return guardado
    from django.contrib.auth import get_user

    from processo_seletivo.seguranca.application import acessos
    from processo_seletivo.seguranca.autenticacao import caminho_do_provedor

    resultado = Resolucao()
    if not caminho_do_provedor():
        encerrar(request)
    else:
        pessoa = get_user(request)
        if not pessoa.is_authenticated:
            encerrar(request)
        elif motivo := _prazo_vencido(request):
            _encerrar_por_prazo(request, dados, pessoa, motivo)
        else:
            _renovar_atividade(request)
            unidade = dados.get("unidade")
            vigentes = acessos.vigentes_da_pessoa(pessoa.pk)
            if not unidade and vigentes:
                # Entrou sem acesso e o recebeu depois: a unidade ativa ainda não existia, e passa a
                # ser a inicial da regra da 106 (`FR-3019`), sem precisar sair e entrar (107,
                # `D-007`). Quem **tinha** unidade e perdeu o acesso nela não troca sozinho — a
                # tela sem acesso oferece a troca, que vai à trilha.
                unidade = acessos.unidade_inicial_de(vigentes)
                request.session[CHAVE_SESSAO] = {**dados, "unidade": unidade}
            papeis = sorted({papel for escopo, papel in vigentes if escopo == unidade})
            escopos = sorted({escopo for escopo, _ in vigentes})
            ator = None
            if unidade and papeis:
                ator = Actor(pessoa.username, unidade, acessos.permissoes_dos_papeis(papeis))
            resultado = Resolucao(ator, papeis, pessoa, escopos)
    setattr(request, _ATOR_DA_REQUISICAO, resultado)
    return resultado


@dataclass(frozen=True)
class Resolucao:
    """O que a sessão institucional resolve numa requisição (106, `D-006`; 107, `D-006`).

    `pessoa` sem `ator` é quem entrou e não tem acesso vigente na unidade ativa: a tela sem acesso
    é dela (107, `D-007`).
    """

    ator: Actor | None = None
    papeis: list = field(default_factory=list)
    pessoa: object = None
    escopos: list = field(default_factory=list)


# Os prazos da sessão institucional (107, `D-009`): 8 horas e 30 minutos, decididos pelo usuário em
# 30/10/2026 (spec da 107, P4). Valem fora de produção sem declaração; produção não sobe sem os dois
# declarados (`D-010`).
DURACAO_MAXIMA_PADRAO = 8 * 60
INATIVIDADE_PADRAO = 30

# Os dois instantes do prazo, em chave própria (107, `D-009`): a identidade da sessão continua com a
# forma que a 106 fixou, e o prazo sai com ela, porque o término institucional apaga a sessão
# inteira.
CHAVE_PRAZO = "interface_prazo_institucional"

# A marca do motivo do término, na sessão nova, para a página de acesso dizê-lo (107, `FR-3125`).
CHAVE_SESSAO_ENCERRADA = "interface_sessao_encerrada"
DURACAO_MAXIMA = "duracao_maxima"
INATIVIDADE = "inatividade"

# O cabeçalho com que a interface declara uma requisição que ela fez sozinha (107, `FR-3123`). Ele
# só **tira** atividade: quem o forjasse encurtaria a própria sessão, e nada mais. Hoje nenhuma
# requisição da gestão o envia — não há sondagem periódica —, e ele existe para a primeira que vier.
CABECALHO_AUTOMATICA = "Requisicao-Automatica"


def _limites():
    duracao = getattr(settings, "GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS", DURACAO_MAXIMA_PADRAO)
    inatividade = getattr(settings, "GESTAO_SESSAO_INATIVIDADE_MINUTOS", INATIVIDADE_PADRAO)
    return int(duracao) * 60, int(inatividade) * 60


def _agora():
    from processo_seletivo.seguranca import relogio

    return relogio.agora().timestamp()


def _prazo_vencido(request):
    """O motivo do término, se a sessão passou de um dos limites — ou vazio (107, `D-009`).

    **No instante igual ao limite, já venceu**: a sessão vale enquanto o tempo passado é menor que
    ele. Sessão sem os instantes é anterior à 107, e não há como saber há quanto tempo está aberta:
    vence, pela regra de negar por padrão.
    """
    prazo = request.session.get(CHAVE_PRAZO) or {}
    entrada, atividade = prazo.get("entrada_em"), prazo.get("atividade_em")
    if entrada is None or atividade is None:
        return DURACAO_MAXIMA
    duracao, inatividade = _limites()
    agora = _agora()
    if agora - entrada >= duracao:
        return DURACAO_MAXIMA
    if agora - atividade >= inatividade:
        return INATIVIDADE
    return ""


def _renovar_atividade(request):
    """A última atividade passa a ser agora — se a requisição é da gestão, e da pessoa (`FR-3123`).

    O portal está na mesma sessão do navegador, e não é atividade na gestão; a requisição declarada
    automática também não.
    """
    if not request.path.startswith(reverse("interface:lista")):
        return
    if request.headers.get(CABECALHO_AUTOMATICA):
        return
    request.session[CHAVE_PRAZO] = {**request.session[CHAVE_PRAZO], "atividade_em": _agora()}


def _encerrar_por_prazo(request, dados, pessoa, motivo):
    """O término por prazo: a saída na trilha com o motivo, e a marca para a página de acesso."""
    from django.utils import timezone

    from processo_seletivo.seguranca.models import IdentidadeExterna

    externa = IdentidadeExterna.objects.filter(pk=dados.get("identidade_externa")).first()
    if externa is not None:
        _registrar_sessao(
            "SAIDA",
            pessoa.username,
            dados.get("unidade"),
            externa,
            timezone.now(),
            getattr(request, "correlation_id", ""),
            motivo=motivo,
        )
    encerrar(request)
    request.session[CHAVE_SESSAO_ENCERRADA] = motivo


def resolucao_institucional(request):
    """A resolução da sessão institucional desta requisição, ou a vazia na demonstração."""
    dados = request.session.get(CHAVE_SESSAO) or {}
    if dados.get("origem") != ORIGEM_INSTITUCIONAL:
        return Resolucao()
    return _resolucao_institucional(request, dados)


def nome_do_ator(request, ator):
    """Como a pessoa identificada aparece na barra (107, `FR-3103`, `D-008`).

    Na demonstração, o identificador escolhido no seletor, como sempre — sem consulta. No
    institucional, o nome, ou o e-mail, e nunca `pessoa-<uuid>`.
    """
    resolucao = resolucao_institucional(request)
    if resolucao.pessoa is None:
        return ator.subject if ator else ""
    from processo_seletivo.seguranca.application.acessos import nome_legivel

    return nome_legivel(resolucao.pessoa)


def rotulo_do_escopo(escopo, unidades=None):
    """O nome do escopo no seletor: a unidade pelo nome, o institucional pelo que ele é."""
    from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL

    if escopo == ESCOPO_INSTITUCIONAL:
        return "Administração institucional"
    unidade = (unidades or {}).get(escopo)
    return unidade.nome if unidade is not None else escopo


def escopos_da_pessoa(request):
    """Os escopos com acesso vigente, pelo nome, para o seletor e a tela sem acesso (`FR-3104`)."""
    resolucao = resolucao_institucional(request)
    if not resolucao.escopos:
        return []
    from processo_seletivo.unidades.models import Unidade

    unidades = {u.codigo: u for u in Unidade.objects.filter(codigo__in=resolucao.escopos)}
    ativo = (request.session.get(CHAVE_SESSAO) or {}).get("unidade")
    return [
        {"codigo": escopo, "rotulo": rotulo_do_escopo(escopo, unidades), "ativo": escopo == ativo}
        for escopo in resolucao.escopos
    ]


def identificar(request, *, subject, papeis, escopo=ESCOPO_PADRAO, origem=ORIGEM_DEMONSTRACAO):
    request.session[CHAVE_SESSAO] = {
        "subject": subject,
        "escopo": escopo,
        "papeis": list(papeis),
        "origem": origem,
    }


def encerrar(request):
    dados = request.session.pop(CHAVE_SESSAO, None)
    if hasattr(request, _ATOR_DA_REQUISICAO):
        delattr(request, _ATOR_DA_REQUISICAO)
    if dados and dados.get("origem") == ORIGEM_INSTITUCIONAL:
        # A sessão inteira, e não só a chave: o `login()` do Django gravou as dele, e sobrariam
        # apontando para a pessoa (`FR-3020`). A da demonstração continua só tirando a chave, como
        # sempre tirou.
        from django.contrib.auth import logout

        logout(request)


def seletor_disponivel():
    """Se o seletor de demonstração existe neste ambiente.

    **Nunca sob a marca de produção** (106, `FR-3003`). `production.py` já recusa subir com a
    chave ligada; esta conferência fecha o caso de a chave mudar depois do *boot* — um
    `override_settings`, uma configuração de terceiros —, e nenhum caminho cai para a demonstração.
    """
    if getattr(settings, "AMBIENTE_DE_PRODUCAO", False):
        return False
    return bool(getattr(settings, "INTERFACE_SELETOR_IDENTIDADE", False))


def institucional_disponivel():
    from processo_seletivo.seguranca.autenticacao import caminho_do_provedor

    return bool(caminho_do_provedor())


def metodos_disponiveis():
    """Por onde se entra na gestão neste ambiente (075, `FR-1691`).

    A página de acesso desenha o que esta lista disser, e só isso. A institucional entra quando há
    provedor configurado (106, `FR-3025`), e a página não foi redesenhada. Lista vazia é produção
    sem provedor: a página diz que a entrada não está configurada.
    """
    metodos = [ORIGEM_DEMONSTRACAO] if seletor_disponivel() else []
    if institucional_disponivel():
        metodos.append(ORIGEM_INSTITUCIONAL)
    return metodos


def entrar_institucional(request, identidade, *, correlation_id=""):
    """A pessoa que o provedor autenticou, com a sessão aberta — ou None (106, `FR-3020`).

    O `login()` do Django troca o identificador da sessão e descarta a sessão de outra pessoa que
    estivesse nela. A unidade ativa é a primeira em que a pessoa atua (`FR-3019`).
    """
    from django.contrib.auth import authenticate, login
    from django.utils import timezone

    from processo_seletivo.seguranca.application import acessos

    pessoa = authenticate(request, identidade_institucional=identidade)
    if pessoa is None:
        return None
    externa = pessoa.identidade_externa_usada
    login(request, pessoa)
    unidade = acessos.unidade_inicial(pessoa.pk)
    request.session[CHAVE_SESSAO] = {
        "origem": ORIGEM_INSTITUCIONAL,
        "unidade": unidade,
        "identidade_externa": str(externa.pk),
    }
    # Os dois instantes do prazo nascem juntos, na entrada (107, `D-009`); a troca de unidade não
    # os toca, e a duração máxima conta daqui.
    instante = _agora()
    request.session[CHAVE_PRAZO] = {"entrada_em": instante, "atividade_em": instante}
    if hasattr(request, _ATOR_DA_REQUISICAO):
        delattr(request, _ATOR_DA_REQUISICAO)
    _registrar_sessao("ENTRADA", pessoa.username, unidade, externa, timezone.now(), correlation_id)
    return pessoa


def trocar_unidade(request, escopo, *, correlation_id=""):
    """Passa a atuar em outro escopo em que a pessoa tem vínculo vigente (106, `FR-3019`).

    Não carrega nada de um escopo para o outro: o ator do novo é recalculado dos vínculos dele.
    """
    from django.contrib.auth import get_user
    from django.utils import timezone

    from processo_seletivo.seguranca.application import acessos
    from processo_seletivo.seguranca.models import IdentidadeExterna
    from processo_seletivo.shared.api.problems import DomainError

    dados = request.session.get(CHAVE_SESSAO) or {}
    pessoa = get_user(request) if dados.get("origem") == ORIGEM_INSTITUCIONAL else None
    if pessoa is None or not pessoa.is_authenticated:
        raise DomainError(
            "sem_sessao_institucional", "A troca de unidade é da entrada institucional.", 403
        )
    if escopo not in acessos.escopos_vigentes(pessoa.pk):
        raise DomainError(
            "sem_vinculo_no_escopo", "Você não tem acesso vigente nesta unidade.", 403
        )
    request.session[CHAVE_SESSAO] = {
        **(request.session.get(CHAVE_SESSAO) or dados),
        "unidade": escopo,
    }
    if hasattr(request, _ATOR_DA_REQUISICAO):
        delattr(request, _ATOR_DA_REQUISICAO)
    externa = IdentidadeExterna.objects.get(pk=dados["identidade_externa"])
    _registrar_sessao(
        "TROCA_DE_UNIDADE", pessoa.username, escopo, externa, timezone.now(), correlation_id
    )


def sair(request, *, correlation_id=""):
    """Encerra a identidade da sessão; a institucional, com a saída na trilha (106, `FR-3020`)."""
    dados = request.session.get(CHAVE_SESSAO) or {}
    if dados.get("origem") == ORIGEM_INSTITUCIONAL:
        from django.contrib.auth import get_user
        from django.utils import timezone

        from processo_seletivo.seguranca.models import IdentidadeExterna

        pessoa = get_user(request)
        externa = IdentidadeExterna.objects.filter(pk=dados.get("identidade_externa")).first()
        if pessoa.is_authenticated and externa is not None:
            _registrar_sessao(
                "SAIDA",
                pessoa.username,
                dados.get("unidade"),
                externa,
                timezone.now(),
                correlation_id,
            )
    encerrar(request)


def _registrar_sessao(operacao, subject, escopo, externa, now, correlation_id, *, motivo=""):
    """Entrada, troca e saída na trilha (106, `D-010`).

    O agregado é a identidade externa usada, porque a trilha exige UUID e o `User` tem chave
    inteira; e ela diz, além de quem, por qual provedor a pessoa entrou. O escopo nunca é vazio:
    quem não tem unidade fica no institucional, que uma consulta alcança.
    """
    from processo_seletivo.auditoria.application import record_event
    from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL

    record_event(
        actor=Actor(subject, escopo or ESCOPO_INSTITUCIONAL),
        permission="sessao:institucional",
        operation=operacao,
        aggregate=externa,
        now=now,
        correlation_id=correlation_id,
        new_state="",
        new_revision=None,
        # O término por prazo diz qual dos dois venceu (107, `FR-3125`); a saída pelo botão, não.
        detalhe={"provedor": externa.provedor, **({"motivo": motivo} if motivo else {})},
    )


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
    # Quem entrou pelo provedor e não tem acesso vigente na unidade ativa não é quem não entrou: a
    # página de acesso o mandaria entrar de novo, e ele voltaria ao mesmo lugar (107, `D-007`).
    if resolucao_institucional(request).pessoa is not None:
        return redirect(reverse("interface:sem-acesso"))
    destino = reverse("interface:identificar")
    if request.method == "GET" and destino_seguro(request, request.get_full_path()):
        destino += "?" + urlencode({"proximo": request.get_full_path()})
    return redirect(destino)


def identificacao_da_gestao(ator):
    from processo_seletivo.unidades.application import identificacao

    if ator is None:
        return identificacao.da_implantacao()
    return identificacao.da_unidade(ator.institution_scope)


def _identificacao_publica():
    from processo_seletivo.unidades.application import identificacao

    return identificacao.da_implantacao()


def contexto_identidade(request):
    """Disponibiliza a identidade a todos os templates, sem cada view precisar repassá-la."""
    ator = ator_da_sessao(request)
    dados = (request.session.get(CHAVE_SESSAO) or {}) if ator else {}
    if dados.get("origem") == ORIGEM_INSTITUCIONAL:
        from processo_seletivo.seguranca.application.acessos import catalogo

        todos = catalogo()
        nomes = [todos[p][0] for p in _resolucao_institucional(request, dados).papeis if p in todos]
    else:
        nomes = [PAPEIS[p][0] for p in dados.get("papeis", []) if p in PAPEIS]
    return {
        "ator": ator,
        "papeis_do_ator": nomes,
        # O nome no lugar do identificador interno (107, `FR-3103`). Preguiçoso pela razão da barra:
        # o fragmento que o htmx troca não o lê, e a demonstração não consulta nada para dá-lo.
        "nome_do_ator": SimpleLazyObject(lambda: nome_do_ator(request, ator)),
        # Os escopos do seletor de unidade da barra, só no institucional (107, `FR-3104`).
        "escopos_do_ator": SimpleLazyObject(lambda: escopos_da_pessoa(request)),
        "seletor_identidade": seletor_disponivel(),
        # **Duas identificações, e nunca uma pela outra** (109). A da gestão é a unidade em que o
        # ator atua — o escopo que a requisição já autorizou, sem consulta a mais além da leitura da
        # sigla. A pública é a da implantação, e não lê sessão nenhuma: o portal, a página de acesso
        # e a 404 não podem dizer a unidade de quem por acaso está na gestão no mesmo navegador
        # (FR-3206). A página de um ato a substitui pela unidade dele (FR-3207). Preguiçosas pela
        # razão do nome: o fragmento que o htmx troca não desenha moldura.
        "identificacao_da_gestao": SimpleLazyObject(lambda: identificacao_da_gestao(ator)),
        "identificacao_publica": SimpleLazyObject(_identificacao_publica),
        # O portal oferece a porta da gestão só onde há por onde entrar (075, `FR-1699`). É o único
        # dado da gestão que o portal lê, e não diz nada sobre quem está identificado.
        "metodos_de_acesso": metodos_disponiveis(),
    }
