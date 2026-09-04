"""Fronteira de autenticação da interface (Decisão 4 do plano da 002).

A interface obtém identidade, escopo e permissões daqui, e não sabe como esse dado é
produzido. Quando o diretório institucional for integrado, só este módulo muda.

Enquanto isso, a identidade vem da sessão, escolhida num seletor que **existe apenas fora de
produção**. O adaptador não é fronteira de segurança: quem decide autorização continua sendo o
backend, em cada command.
"""

from django.conf import settings

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
    "publicador": ("Publicador", ["edital:publicar", "retificacao:publicar"]),
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
        ],
    ),
    "auditor": ("Auditor", ["auditoria:consultar"]),
}


def permissoes_de(papeis):
    return frozenset(permissao for papel in papeis for permissao in PAPEIS.get(papel, ("", []))[1])


def ator_da_sessao(request):
    """Ator autenticado, ou None quando ninguém foi identificado ainda."""
    dados = request.session.get(CHAVE_SESSAO)
    if not dados:
        return None
    return Actor(dados["subject"], dados["escopo"], permissoes_de(dados["papeis"]))


def identificar(request, *, subject, papeis, escopo=ESCOPO_PADRAO):
    request.session[CHAVE_SESSAO] = {
        "subject": subject,
        "escopo": escopo,
        "papeis": list(papeis),
    }


def encerrar(request):
    request.session.pop(CHAVE_SESSAO, None)


def seletor_disponivel():
    return bool(getattr(settings, "INTERFACE_SELETOR_IDENTIDADE", False))


def contexto_identidade(request):
    """Disponibiliza a identidade a todos os templates, sem cada view precisar repassá-la."""
    ator = ator_da_sessao(request)
    dados = request.session.get(CHAVE_SESSAO) or {}
    return {
        "ator": ator,
        "papeis_do_ator": [PAPEIS[p][0] for p in dados.get("papeis", []) if p in PAPEIS],
        "seletor_identidade": seletor_disponivel(),
    }
