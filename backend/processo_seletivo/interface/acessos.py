"""As telas de gestão de acessos: a da unidade e a institucional (107).

**Um par de views, dois níveis** (`D-002`). A unidade concede os papéis operacionais na unidade
ativa de quem opera; o institucional concede o Administrador de acessos de uma unidade escolhida. A
jornada é a mesma — buscar a pessoa, conferir, confirmar com motivo —, e duas cópias divergiriam na
primeira correção.

**As telas pedem capacidade, e não papel** (`D-001`): quem concede na unidade é proposta da `106`, e
se o usuário decidir que o Gestor concede, muda o catálogo e nenhuma linha daqui.

**Nada grava antes da confirmação, e a confirmação não confia na primeira etapa** (`D-003`). O
envio `conferir` só lê; o `confirmar` chama `conceder` ou `revogar` da `106`, que reconferem tudo
sob a trava e gravam o ato e a trilha na mesma transação. A unidade do nível da unidade nunca vem
do formulário (`FR-3109`).

**Só a sessão institucional chega aqui** (`FR-3127`). A demonstração não tem as capacidades de
acesso — o seletor desenha só os oito papéis do `PAPEIS` —, e a conferência de origem é a segunda
barreira, para o dia em que alguém as acrescentar ao mapa.
"""

from dataclasses import dataclass

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_DE_ACESSOS,
    ADMINISTRAR,
    CONSULTAR,
    ESCOPO_INSTITUCIONAL,
    GERIR,
    INTEGRANTE,
)
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.shared.api.problems import DomainError

# O que cada papel permite, em palavras de quem o recebe (`FR-3108`, `FR-3116`). Os oito do `PAPEIS`
# já têm a frase da tela de entrada (075); os dois daqui são os do catálogo de acesso.
ALCANCE_DOS_PAPEIS_DE_ACESSO = {
    INTEGRANTE: (
        "Atua na unidade só no que a comissão lhe atribuir, sem permissão sistêmica. É este "
        "vínculo que deixa a comissão alcançá-la."
    ),
    ADMINISTRADOR_DE_ACESSOS: (
        "Concede e revoga os papéis operacionais da unidade, e consulta quem atua nela. Não conduz "
        "Processo nem Edital, e não concede papel de acesso."
    ),
}


@dataclass(frozen=True)
class Nivel:
    """Um dos dois níveis de administração (`D-002`)."""

    chave: str
    titulo: str
    ler: str
    conceder: str
    base_ler: str
    base_conceder: str
    rota: str
    rota_conceder: str
    rota_revogar: str

    @property
    def institucional(self):
        return self.chave == "institucional"

    def escopo_do_ator(self, ator):
        # O nível da unidade age na unidade ativa; o institucional, só no escopo institucional — a
        # pessoa que também atua numa unidade troca para ele no seletor da barra.
        return ESCOPO_INSTITUCIONAL if self.institucional else ator.institution_scope

    def papeis(self):
        """Os papéis que este nível concede, com o nome e o alcance em palavras."""
        if self.institucional:
            chaves = [ADMINISTRADOR_DE_ACESSOS]
        else:
            chaves = [*identidade.PAPEIS, INTEGRANTE]
        catalogo = acessos.catalogo()
        return [
            {"chave": chave, "nome": catalogo[chave][0], "alcance": alcance(chave)}
            for chave in chaves
        ]


UNIDADE = Nivel(
    chave="unidade",
    titulo="Acessos da unidade",
    ler=CONSULTAR,
    conceder=GERIR,
    base_ler="consultar os acessos da unidade",
    base_conceder="conceder e revogar os acessos da unidade",
    rota="interface:acessos",
    rota_conceder="interface:acessos-conceder",
    rota_revogar="interface:acessos-revogar",
)
INSTITUCIONAL = Nivel(
    chave="institucional",
    titulo="Administração de acessos",
    ler=ADMINISTRAR,
    conceder=ADMINISTRAR,
    base_ler="administrar os acessos das unidades",
    base_conceder="administrar os acessos das unidades",
    rota="interface:administracao-de-acessos",
    rota_conceder="interface:administracao-de-acessos-conceder",
    rota_revogar="interface:administracao-de-acessos-revogar",
)
NIVEIS = {UNIDADE.chave: UNIDADE, INSTITUCIONAL.chave: INSTITUCIONAL}


def alcance(papel):
    return identidade.DESCRICOES.get(papel) or ALCANCE_DOS_PAPEIS_DE_ACESSO.get(papel, "")


def _ator_do_nivel(request, nivel, permissao, base):
    """O ator que pode exercer `permissao` no nível, ou a recusa que diz o que falta.

    A capacidade se lê do ator, que só tem as permissões do escopo ativo; no institucional, o escopo
    ativo precisa ser o institucional. A recusa nomeia a base (`FR-481` da `033`), e a sessão de
    demonstração é recusada depois, pela origem (`FR-3127`).
    """
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None
    require_authorization_base(
        ator.can(permissao) and ator.institution_scope == nivel.escopo_do_ator(ator),
        bases=[base_de_permissao(base)],
    )
    if identidade.resolucao_institucional(request).pessoa is None:
        raise DomainError(
            "so_entrada_institucional",
            "A gestão de acessos é da entrada institucional; a demonstração não a alcança.",
            403,
        )
    return ator


def _unidades():
    from processo_seletivo.unidades.models import Unidade

    return {unidade.codigo: unidade for unidade in Unidade.objects.order_by("codigo")}


def _nome_da_unidade(codigo, unidades=None):
    unidades = unidades if unidades is not None else _unidades()
    return identidade.rotulo_do_escopo(codigo, unidades)


@require_http_methods(["GET"])
def lista(request, nivel):
    """Quem atua no escopo do nível, e o histórico das concessões e revogações (`FR-3106`)."""
    nivel = NIVEIS[nivel]
    ator = _ator_do_nivel(request, nivel, nivel.ler, nivel.base_ler)
    if ator is None:
        return identidade.pedir_identificacao(request)
    unidades = _unidades()
    pode_conceder = ator.can(nivel.conceder)
    if nivel.institucional:
        grupos = [
            {
                "unidade": unidade,
                "vinculos": [_linha(nivel, v, ator, pode_conceder) for v in vinculos],
            }
            for unidade, vinculos in acessos.administradores_por_unidade(ator)
        ]
        eventos = acessos.historico(
            ator,
            permissao=nivel.ler,
            no_escopo=ESCOPO_INSTITUCIONAL,
            escopos=list(unidades),
            papeis=[ADMINISTRADOR_DE_ACESSOS],
        )
    else:
        grupos = [
            {
                "unidade": unidades.get(ator.institution_scope),
                "vinculos": [
                    _linha(nivel, v, ator, pode_conceder)
                    for v in acessos.vinculos_vigentes_da_unidade(ator)
                ],
            }
        ]
        eventos = acessos.historico(
            ator,
            permissao=nivel.ler,
            no_escopo=ator.institution_scope,
            escopos=[ator.institution_scope],
        )
    autores = acessos.nomes_dos_autores(
        [v["vinculo"].concedido_por for g in grupos for v in g["vinculos"]]
        + [evento[2] for evento in eventos]
    )
    for grupo in grupos:
        for linha in grupo["vinculos"]:
            linha["concedido_por"] = autores.get(linha["vinculo"].concedido_por, "")
    catalogo = acessos.catalogo()
    return render(
        request,
        "interface/acessos.html",
        {
            "nivel": nivel,
            "codigo": ator.institution_scope,
            "nome_da_unidade": _nome_da_unidade(ator.institution_scope, unidades),
            "grupos": grupos,
            "historico": [
                {
                    "tipo": tipo,
                    "quando": quando,
                    "por": autores.get(por, por),
                    "motivo": motivo,
                    "pessoa": acessos.nome_legivel(vinculo.pessoa),
                    "papel": catalogo.get(vinculo.papel, (vinculo.papel,))[0],
                    "unidade": _nome_da_unidade(vinculo.escopo, unidades),
                }
                for tipo, quando, por, motivo, vinculo in eventos
            ],
            "pode_conceder": pode_conceder,
            "feito": request.GET.get("feito", ""),
        },
    )


def _linha(nivel, vinculo, ator, pode_conceder):
    """Um vínculo vigente na tela, e se o ator pode revogá-lo daqui (`FR-3111`).

    O botão só aparece onde a regra da `106` aceitaria: papel que o nível concede, e vínculo que não
    é do próprio ator. O administrador da unidade lê os administradores dela, e não os revoga — é o
    nível acima. O servidor recusa os demais de qualquer modo.
    """
    catalogo = acessos.catalogo()
    revogavel = (
        pode_conceder
        and vinculo.pessoa.username != ator.subject
        and vinculo.papel in {papel["chave"] for papel in nivel.papeis()}
    )
    return {
        "vinculo": vinculo,
        "pessoa": acessos.nome_legivel(vinculo.pessoa),
        "email": vinculo.pessoa.email,
        "papel": catalogo.get(vinculo.papel, (vinculo.papel,))[0],
        "revogavel": revogavel,
    }


@require_http_methods(["GET", "POST"])
def conceder(request, nivel):
    """Buscar, conferir e confirmar uma concessão (`FR-3108` a `FR-3119`)."""
    nivel = NIVEIS[nivel]
    ator = _ator_do_nivel(request, nivel, nivel.conceder, nivel.base_conceder)
    if ator is None:
        return identidade.pedir_identificacao(request)
    acao = request.POST.get("acao", "") if request.method == "POST" else ""
    if acao in ("conferir", "confirmar"):
        return _concessao(request, nivel, ator, acao)
    termo = request.POST.get("termo", "") if acao == "buscar" else ""
    pessoas, ha_mais = acessos.buscar_pessoas(
        ator, termo, permissao=nivel.conceder, escopo=nivel.escopo_do_ator(ator)
    )
    unidades = _unidades()
    return render(
        request,
        "interface/acessos_conceder.html",
        {
            "nivel": nivel,
            "nome_da_unidade": _nome_da_unidade(ator.institution_scope, unidades),
            "termo": termo.strip(),
            "buscou": acao == "buscar",
            "curto": acao == "buscar" and len(termo.strip()) < acessos.PISO_DA_BUSCA,
            "piso": acessos.PISO_DA_BUSCA,
            "teto": acessos.TETO_DA_BUSCA,
            "pessoas": [
                {"identificador": p.username, "nome": acessos.nome_legivel(p), "email": p.email}
                for p in pessoas
            ],
            "ha_mais": ha_mais,
            "papeis": nivel.papeis(),
            "unidades": [u for u in unidades.values() if u.ativa] if nivel.institucional else [],
        },
    )


def _concessao(request, nivel, ator, acao):
    """A confirmação da concessão (`conferir`) e a gravação (`confirmar`)."""
    pessoa = acessos.pessoa_institucional(request.POST.get("pessoa", ""))
    papel = request.POST.get("papel", "")
    if papel not in {p["chave"] for p in nivel.papeis()}:
        raise DomainError(
            acessos.PAPEL_INEXISTENTE, "Escolha um dos papéis que esta tela concede.", 422
        )
    # A unidade do nível da unidade é a ativa, e nunca o formulário (`FR-3109`); a do institucional
    # é a escolhida, e a concessão a confere contra as unidades registradas e ativas.
    escopo = request.POST.get("unidade", "") if nivel.institucional else ator.institution_scope
    contexto = _contexto_da_confirmacao(nivel, "conceder", pessoa, escopo, papel)
    erro, status, codigo = "", 200, ""
    try:
        if acao == "confirmar":
            acessos.conceder(
                ator,
                pessoa=pessoa,
                escopo=escopo,
                papel=papel,
                motivo=request.POST.get("motivo", ""),
                now=timezone.now(),
                correlation_id=getattr(request, "correlation_id", ""),
            )
            return redirect(f"{reverse(nivel.rota)}?feito=concedido")
        acessos.conferir_concessao(ator, pessoa=pessoa, escopo=escopo, papel=papel)
    except DomainError as recusa:
        erro, status, codigo = recusa.detail, recusa.status, recusa.code
    contexto.update(
        {
            "erro": erro,
            "motivo": request.POST.get("motivo", ""),
            # Só o motivo faltou: a confirmação continua confirmável, com a frase do que falta.
            "confirmavel": not erro or codigo == acessos.MOTIVO_OBRIGATORIO,
        }
    )
    return render(request, "interface/acessos_confirmar.html", contexto, status=status)


@require_http_methods(["POST"])
def revogar(request, nivel, vinculo_id):
    """Conferir e confirmar a revogação de um vínculo do nível (`FR-3110`, `FR-3116`)."""
    nivel = NIVEIS[nivel]
    ator = _ator_do_nivel(request, nivel, nivel.conceder, nivel.base_conceder)
    if ator is None:
        return identidade.pedir_identificacao(request)
    # O vínculo se procura **no escopo do nível**, na própria consulta (`FR-487` da `033`): o de
    # outra unidade, ou o de outro papel no institucional, é indistinguível de inexistente.
    from processo_seletivo.seguranca.models import Vinculo

    encontrados = Vinculo.objects.select_related("pessoa").filter(pk=vinculo_id)
    if nivel.institucional:
        encontrados = encontrados.filter(papel=ADMINISTRADOR_DE_ACESSOS)
    else:
        encontrados = encontrados.filter(escopo=ator.institution_scope)
    vinculo = encontrados.first()
    if vinculo is None:
        raise Http404
    acao = request.POST.get("acao", "")
    contexto = _contexto_da_confirmacao(
        nivel, "revogar", vinculo.pessoa, vinculo.escopo, vinculo.papel, vinculo=vinculo
    )
    erro, status, codigo = "", 200, ""
    try:
        if acao == "confirmar":
            acessos.revogar(
                ator,
                vinculo=vinculo,
                motivo=request.POST.get("motivo", ""),
                now=timezone.now(),
                correlation_id=getattr(request, "correlation_id", ""),
            )
            return redirect(f"{reverse(nivel.rota)}?feito=revogado")
        acessos.conferir_revogacao(ator, vinculo=vinculo)
    except DomainError as recusa:
        erro, status, codigo = recusa.detail, recusa.status, recusa.code
    contexto.update(
        {
            "erro": erro,
            "motivo": request.POST.get("motivo", ""),
            "confirmavel": not erro or codigo == acessos.MOTIVO_OBRIGATORIO,
        }
    )
    return render(request, "interface/acessos_confirmar.html", contexto, status=status)


def _contexto_da_confirmacao(nivel, ato, pessoa, escopo, papel, *, vinculo=None):
    """Pessoa, unidade, papel, alcance e consequência — o que a confirmação mostra (`FR-3116`)."""
    catalogo = acessos.catalogo()
    nome = acessos.nome_legivel(pessoa)
    unidade = _nome_da_unidade(escopo)
    nome_do_papel = catalogo.get(papel, (papel,))[0]
    if ato == "conceder":
        consequencias = [
            f"{nome} passa a ter o papel {nome_do_papel} em {unidade} na próxima ação que fizer "
            "na gestão, mesmo com a sessão já aberta.",
            "A concessão vai à trilha com o seu nome, a data e o motivo, e não se apaga: para "
            "tirar o acesso depois, revoga-se.",
        ]
    else:
        consequencias = [
            f"{nome} perde o papel {nome_do_papel} em {unidade} na próxima ação que fizer na "
            "gestão, mesmo com a sessão aberta.",
            "A presidência ou a participação em comissão não devolvem o acesso: sem papel vigente "
            "na unidade, a pessoa não age nela por caminho nenhum.",
            "A revogação fica registrada ao lado da concessão, que não se apaga. Para devolver o "
            "acesso, concede-se de novo.",
        ]
    return {
        "nivel": nivel,
        "ato": ato,
        "pessoa": {"identificador": pessoa.username, "nome": nome, "email": pessoa.email},
        "escopo": escopo,
        "unidade": unidade,
        "papel": {"chave": papel, "nome": nome_do_papel, "alcance": alcance(papel)},
        "consequencias": consequencias,
        "vinculo": vinculo,
        "acao_do_formulario": (
            reverse(nivel.rota_revogar, args=[vinculo.pk])
            if vinculo is not None
            else reverse(nivel.rota_conceder)
        ),
    }


@require_http_methods(["GET"])
def sem_acesso(request):
    """Quem entrou pelo provedor e não tem acesso vigente na unidade ativa (`FR-3101`, `FR-3102`).

    Mostra a própria pessoa, os escopos em que ainda atua — cada um com a troca — e a saída. Nada
    mais: nem papéis, nem quem concedeu.
    """
    if identidade.ator_da_sessao(request) is not None:
        return redirect(reverse("interface:lista"))
    resolucao = identidade.resolucao_institucional(request)
    if resolucao.pessoa is None:
        return redirect(reverse("interface:identificar"))
    return render(
        request,
        "interface/sem_acesso.html",
        {
            "pessoa": {
                "nome": acessos.nome_legivel(resolucao.pessoa),
                "email": resolucao.pessoa.email,
            },
            "escopos": identidade.escopos_da_pessoa(request),
        },
    )
